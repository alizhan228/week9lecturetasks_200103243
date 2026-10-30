"""Milestone 3: strong/weak scaling of a 5-point Jacobi stencil + roofline.

Run:  python3 src/scaling_study.py --student-id <ID> --peak-bw-gbs <GB/s>
Optional: --cpus 0,2,4,...  --max-p 8  --iters 100  --repeats 3
          --peak-gflops <GFLOP/s>  --flops-per-cycle 16
Needs results/host_profile.json (Milestone 0).
"""
import argparse
import json
import math
import multiprocessing as mp
import os
import statistics
import sys
import time
from multiprocessing import shared_memory

import numpy as np
from numba import njit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from salt import get_student_params

FLOPS_PER_POINT = 4  # 3 adds + 1 multiply: 0.25 * (N + S + W + E)


@njit(cache=True)
def sweep(src, dst, N, r0, r1):
    for i in range(r0, r1):
        for j in range(1, N - 1):
            dst[i, j] = 0.25 * (src[i - 1, j] + src[i + 1, j] + src[i, j - 1] + src[i, j + 1])


def worker(shm_name, N, iters, r0, r1, start_barrier, sweep_barrier, cpu):
    if cpu is not None and hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {cpu})
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = np.ndarray((2, N, N), dtype=np.float64, buffer=shm.buf)
    a, b = buf[0], buf[1]
    tiny = np.zeros((4, 4))
    sweep(tiny, tiny.copy(), 4, 1, 3)  # make sure compiled code is loaded before timing
    start_barrier.wait()
    for it in range(iters):
        if it % 2 == 0:
            sweep(a, b, N, r0, r1)
        else:
            sweep(b, a, N, r0, r1)
        sweep_barrier.wait()  # neighbours' rows must be finished before the next sweep
    del a, b, buf
    shm.close()


def make_init(N, seed):
    return np.random.default_rng(seed).random((N, N))


def serial_reference(init, iters):
    N = init.shape[0]
    a, b = init.copy(), init.copy()
    for it in range(iters):
        if it % 2 == 0:
            sweep(a, b, N, 1, N - 1)
        else:
            sweep(b, a, N, 1, N - 1)
    return a if iters % 2 == 0 else b


def run_once(ctx, init, P, iters, cpus):
    N = init.shape[0]
    shm = shared_memory.SharedMemory(create=True, size=2 * N * N * 8)
    view = np.ndarray((2, N, N), dtype=np.float64, buffer=shm.buf)
    view[0] = init
    view[1] = init
    rows = N - 2
    base, extra = divmod(rows, P)
    start_barrier = ctx.Barrier(P + 1)
    sweep_barrier = ctx.Barrier(P)
    procs, r = [], 1
    for p in range(P):
        n = base + (1 if p < extra else 0)
        cpu = cpus[p % len(cpus)] if cpus else None
        procs.append(ctx.Process(target=worker, args=(shm.name, N, iters, r, r + n,
                                                      start_barrier, sweep_barrier, cpu)))
        r += n
    for pr in procs:
        pr.start()
    start_barrier.wait()
    t0 = time.perf_counter()
    for pr in procs:
        pr.join()
    elapsed = time.perf_counter() - t0
    final = view[0 if iters % 2 == 0 else 1].copy()
    del view
    shm.close()
    shm.unlink()
    return elapsed, final


def p_list(max_p):
    ps, p = [], 1
    while p <= max_p:
        ps.append(p)
        p *= 2
    if ps[-1] != max_p:
        ps.append(max_p)
    return ps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-id", required=True)
    ap.add_argument("--iters", type=int, default=100)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--max-p", type=int, default=None)
    ap.add_argument("--cpus", type=str, default="")
    ap.add_argument("--peak-bw-gbs", type=float, default=None,
                    help="theoretical DRAM bandwidth, GB/s (channels x MT/s x 8 B)")
    ap.add_argument("--peak-gflops", type=float, default=None)
    ap.add_argument("--flops-per-cycle", type=float, default=16.0,
                    help="double-precision FLOPs/cycle/core (16 = AVX2+FMA, 32 = AVX-512 x2 FMA)")
    args = ap.parse_args()

    params = get_student_params(args.student_id)
    N, seed, iters = params["N"], params["seed"], args.iters
    with open("results/host_profile.json") as f:
        host = json.load(f)
    phys = host["topology"]["physical_cores"] or os.cpu_count()
    max_p = args.max_p or phys
    cpus = [int(c) for c in args.cpus.split(",") if c] or None
    Ps = p_list(max_p)
    print(f"N={N} iters={iters} P list={Ps}")

    sweep(np.zeros((4, 4)), np.zeros((4, 4)), 4, 1, 3)  # JIT compile in parent
    ctx = mp.get_context()
    refs = {}

    def measure(Nx, P):
        if Nx not in refs:
            refs[Nx] = serial_reference(make_init(Nx, seed), iters)
        init = make_init(Nx, seed)
        times, ok = [], True
        for _ in range(args.repeats):
            t, final = run_once(ctx, init, P, iters, cpus)
            times.append(t)
            ok &= bool(np.array_equal(final, refs[Nx]))
        return statistics.median(times), ok

    rows = []
    # ---- strong scaling (fixed N) ----
    strong = {}
    for P in Ps:
        strong[P] = measure(N, P)
        print(f"strong P={P}  T={strong[P][0]:.4f}s  checksum_ok={strong[P][1]}")
    T1 = strong[1][0]
    s_points = {}
    for P in Ps:
        t, ok = strong[P]
        S = T1 / t
        E = S / P * 100
        s_pt = ((1 / S) - (1 / P)) / (1 - 1 / P) if P > 1 else None
        s_points[P] = s_pt
        rows.append(dict(study="strong", P=P, N=N, T=t, speedup=S, eff=E, s_pt=s_pt,
                         spec_formula=None, scaled=None, weak_eff=None, alpha=None, ok=ok))

    # Least-squares Amdahl fit over P>=2:  y=1/S, x=1/P,  y-x = s(1-x)
    num = den = 0.0
    for P in Ps:
        if P == 1:
            continue
        x, y = 1 / P, strong[P][0] / T1  # y = 1/S_P
        num += (y - x) * (1 - x)
        den += (1 - x) ** 2
    s_fit = num / den if den else float("nan")
    s_used = max(s_fit, 0.0)
    s_max = (1 / s_used) if s_used > 0 else None

    # ---- weak scaling (N_P = ceil(N sqrt(P))) ----
    weak = {}
    for P in Ps:
        NP = math.ceil(N * math.sqrt(P))
        weak[P] = (NP,) + measure(NP, P)
        print(f"weak   P={P}  N_P={NP}  T={weak[P][1]:.4f}s  checksum_ok={weak[P][2]}")
    T1w = weak[1][1]
    work1 = float(weak[1][0]) ** 2 * iters
    alphas = []
    for P in Ps:
        NP, t, ok = weak[P]
        workP = float(NP) ** 2 * iters
        spec_formula = (P * work1 * T1w) / (workP * t)      # formula exactly as written in the handout
        scaled = (workP * T1w) / (work1 * t)               # throughput ratio = Gustafson scaled speedup
        weff = T1w / t * 100
        alpha = (P - scaled) / (P - 1) if P > 1 else None  # S = P - alpha (P-1)
        if alpha is not None:
            alphas.append(alpha)
        rows.append(dict(study="weak", P=P, N=NP, T=t, speedup=None, eff=None, s_pt=None,
                         spec_formula=spec_formula, scaled=scaled, weak_eff=weff,
                         alpha=alpha, ok=ok))

    def fmt(v, d=5):
        return "" if v is None else f"{v:.{d}f}"

    os.makedirs("results", exist_ok=True)
    with open("results/scaling_metrics.tsv", "w") as f:
        f.write("study\tP\tN\titers\tmedian_time_s\tspeedup\tefficiency_pct\tamdahl_s_point\t"
                "spec_scaled_formula\tscaled_speedup\tweak_efficiency_pct\tgustafson_alpha\tchecksum_ok\n")
        for r in rows:
            f.write(f"{r['study']}\t{r['P']}\t{r['N']}\t{iters}\t{r['T']:.6f}\t{fmt(r['speedup'],4)}\t"
                    f"{fmt(r['eff'],2)}\t{fmt(r['s_pt'])}\t{fmt(r['spec_formula'],4)}\t"
                    f"{fmt(r['scaled'],4)}\t{fmt(r['weak_eff'],2)}\t{fmt(r['alpha'])}\t{r['ok']}\n")

    with open("results/amdahl_fit.json", "w") as f:
        json.dump({"serial_fraction_s_fit": s_fit, "serial_fraction_used": s_used,
                   "S_max": s_max,
                   "per_P_serial_fraction": {str(k): v for k, v in s_points.items() if v is not None},
                   "gustafson_alpha_mean": statistics.mean(alphas) if alphas else None,
                   "note": "negative s_fit means superlinear speedup (cache effects); S_max null = unbounded"},
                  f, indent=2)

    # ---- roofline ----
    c = host["caches"]
    ghz = None
    fq = (host.get("cpu") or {}).get("frequency")
    if fq:
        ghz = (fq.get("max_mhz") or fq.get("current_mhz") or 0) / 1000 or None
    peak_gflops = args.peak_gflops or (phys * ghz * args.flops_per_cycle if ghz else None)
    peak_bw = args.peak_bw_gbs
    ai_ideal = FLOPS_PER_POINT / 16          # 8 B read + 8 B write per point (neighbour reuse in cache)
    ai_wa = FLOPS_PER_POINT / 24             # + write-allocate read of dst line
    ai_noreuse = FLOPS_PER_POINT / 48        # 5 reads + 1 write, no cache reuse
    interior = (N - 2) ** 2 * iters
    gf1 = FLOPS_PER_POINT * interior / T1 / 1e9
    gfp = FLOPS_PER_POINT * interior / strong[Ps[-1]][0] / 1e9
    ws = 2 * N * N * 8
    ridge = (peak_gflops / peak_bw) if (peak_gflops and peak_bw) else None
    if ridge is not None:
        regime = "memory-bandwidth bound" if ai_ideal < ridge else "compute bound"
        basis = "AI (best case) compared with ridge point = peak_gflops / peak_bw"
    else:
        regime = "memory-bandwidth bound (provisional)"
        basis = ("peak bandwidth and/or peak GFLOP/s not supplied; classification assumes ridge point "
                 "> 1 FLOP/byte, typical of x86 CPUs. Re-run with --peak-bw-gbs to confirm")
    roof = {
        "kernel": "5-point Jacobi stencil, float64",
        "flops_per_point": FLOPS_PER_POINT,
        "arithmetic_intensity_flop_per_byte": {"ideal_16B_per_point": ai_ideal,
                                               "with_write_allocate_24B": ai_wa,
                                               "no_cache_reuse_48B": ai_noreuse},
        "working_set_bytes": ws,
        "l2_bytes": c.get("l2_bytes"), "l3_bytes": c.get("l3_bytes"),
        "working_set_fits_in_L3": (ws <= c["l3_bytes"]) if c.get("l3_bytes") else None,
        "peak_gflops": peak_gflops, "peak_bw_gbs": peak_bw,
        "ridge_point_flop_per_byte": ridge,
        "attainable_gflops_at_ideal_AI": (min(peak_gflops, ai_ideal * peak_bw)
                                          if peak_gflops and peak_bw else None),
        "achieved_gflops_P1": gf1, f"achieved_gflops_P{Ps[-1]}": gfp,
        "regime": regime, "regime_basis": basis,
    }
    with open("results/roofline_summary.json", "w") as f:
        json.dump(roof, f, indent=2)
    print(json.dumps(roof, indent=2))
    print(f"Amdahl s_fit={s_fit:.5f}  S_max={s_max}")


if __name__ == "__main__":
    main()