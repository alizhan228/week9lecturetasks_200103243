"""Milestone 2: false sharing, remediation, Karp-Flatt.

Run:  python3 src/false_sharing.py                 (Numba backend, recommended)
      python3 src/false_sharing.py --backend python (pure-Python ctypes workers, as in the spec)
      python3 src/false_sharing.py --cpus 0,2,4,6,8,10,12,14   (pin to distinct physical cores)
"""
import argparse
import ctypes
import multiprocessing as mp
import os
import statistics
import time
from multiprocessing import shared_memory

import numpy as np

K_DEFAULT = 5_000_000
P_LIST = [1, 2, 4, 8]
SLOTS = 64  # 8 workers x 8 int64 (= 64 bytes) so padded slots fit


# ---------------- Numba kernels (backend "numba") ----------------
try:
    from numba import njit

    @njit(cache=True)
    def nb_increment(arr, idx0, K, zero):
        # `i * zero` is always 0 at runtime, but the compiler cannot know that,
        # so it cannot hoist the store out of the loop into a register. This keeps
        # the memory write (and the cache-line ping-pong) in the loop.
        for i in range(K):
            arr[idx0 + i * zero] += 1

    @njit(cache=True)
    def nb_private(arr, idx, K, zero):
        c = 0
        for i in range(K):
            c += 1 + i * zero
        arr[idx] = c  # single write at the end

    HAVE_NUMBA = True
except ImportError:
    HAVE_NUMBA = False


# ---------------- Pure-Python workers (backend "python") ----------------
def worker_unpadded(counter_array, worker_id, iterations):
    for _ in range(iterations):
        counter_array[worker_id] += 1


def worker_padded(counter_array, worker_id, iterations):
    idx = worker_id * 8  # 8 x int64 = 64 bytes: own cache line
    for _ in range(iterations):
        counter_array[idx] += 1


def worker_privatized(counter_array, worker_id, iterations):
    local = 0
    for _ in range(iterations):
        local += 1
    counter_array[worker_id * 8] = local


PY_WORKERS = {"unpadded": worker_unpadded, "padded": worker_padded,
              "privatized": worker_privatized}


def entry(backend, variant, handle, wid, K, barrier, cpu):
    if cpu is not None and hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {cpu})
    if backend == "numba":
        shm = shared_memory.SharedMemory(name=handle)
        arr = np.ndarray((SLOTS,), dtype=np.int64, buffer=shm.buf)
        scratch = np.zeros(SLOTS, dtype=np.int64)
        nb_increment(scratch, 0, 1, 0)  # make sure compiled code is loaded
        nb_private(scratch, 0, 1, 0)
        barrier.wait()
        if variant == "unpadded":
            nb_increment(arr, wid, K, 0)
        elif variant == "padded":
            nb_increment(arr, wid * 8, K, 0)
        else:
            nb_private(arr, wid * 8, K, 0)
        del arr
        shm.close()
    else:
        barrier.wait()
        PY_WORKERS[variant](handle, wid, K)


def run_once(ctx, backend, variant, P, K, cpus, arr_handle, view):
    for i in range(SLOTS):
        view[i] = 0
    barrier = ctx.Barrier(P + 1)
    procs = []
    for p in range(P):
        cpu = cpus[p % len(cpus)] if cpus else None
        procs.append(ctx.Process(target=entry,
                                 args=(backend, variant, arr_handle, p, K, barrier, cpu)))
    for pr in procs:
        pr.start()
    barrier.wait()
    t0 = time.perf_counter()
    for pr in procs:
        pr.join()
    elapsed = time.perf_counter() - t0
    total = int(sum(int(view[i]) for i in range(SLOTS)))
    return elapsed, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["numba", "python"], default="numba")
    ap.add_argument("--k", type=int, default=K_DEFAULT)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--cpus", type=str, default="",
                    help="comma-separated CPU ids to pin workers to (distinct physical cores)")
    args = ap.parse_args()
    if args.backend == "numba" and not HAVE_NUMBA:
        raise SystemExit("numba not installed: pip install numba, or use --backend python")

    cpus = [int(c) for c in args.cpus.split(",") if c] or None
    if cpus is None and hasattr(os, "sched_getaffinity"):
        cpus = sorted(os.sched_getaffinity(0))
        print("WARNING: no --cpus given; workers pinned to logical CPUs in order. "
              "On SMT machines neighbours may share a physical core, hiding false sharing.")
    print(f"logical CPUs: {os.cpu_count()}  (P=8 oversubscribes if you have fewer cores)")

    ctx = mp.get_context()
    if args.backend == "numba":
        shm = shared_memory.SharedMemory(create=True, size=SLOTS * 8)
        view = np.ndarray((SLOTS,), dtype=np.int64, buffer=shm.buf)
        handle = shm.name
    else:
        view = ctx.Array(ctypes.c_int64, SLOTS, lock=False)  # lock=False: no lock contention
        handle = view

    results = {}  # (variant, P) -> (median_s, total_ok)
    try:
        for variant in ["unpadded", "padded", "privatized"]:
            for P in P_LIST:
                times, ok = [], True
                for _ in range(args.repeats):
                    t, total = run_once(ctx, args.backend, variant, P, args.k, cpus, handle, view)
                    times.append(t)
                    ok &= (total == P * args.k)
                results[(variant, P)] = (statistics.median(times), ok)
                print(f"{variant:10s} P={P}  T={results[(variant, P)][0]:.4f}s  "
                      f"count_ok={ok}")
    finally:
        if args.backend == "numba":
            del view
            shm.close()
            shm.unlink()

    os.makedirs("results", exist_ok=True)
    with open("results/false_sharing_karp_flatt.tsv", "w") as f:
        f.write("variant\tP\tK\tmedian_time_s\tspeedup\tefficiency_pct\tkarp_flatt_e\tcount_ok\n")
        for variant in ["unpadded", "padded", "privatized"]:
            t1 = results[(variant, 1)][0]
            for P in P_LIST:
                t, ok = results[(variant, P)]
                s = t1 / t
                e = ((P * t / t1) - 1) / (P - 1) if P > 1 else float("nan")
                eff = s / P * 100
                e_txt = "" if P == 1 else f"{e:.5f}"
                f.write(f"{variant}\t{P}\t{args.k}\t{t:.6f}\t{s:.4f}\t{eff:.2f}\t{e_txt}\t{ok}\n")
    print("wrote results/false_sharing_karp_flatt.tsv")


if __name__ == "__main__":
    main()