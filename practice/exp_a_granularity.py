import sys, time, json
from multiprocessing import Pool


def collatz_steps(n):
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers, total_items=10_000, chunk_size=1):
    numbers = range(1, total_items + 1)
    t0 = time.perf_counter()
    with Pool(processes=workers) as pool:
        # chunk_size=1 -> one IPC task envelope per number (micro-tasks)
        results = pool.map(collatz_steps, numbers, chunksize=chunk_size)
    return time.perf_counter() - t0, sum(results)


def karp_flatt(t1, tp, p):
    return ((p * tp / t1) - 1.0) / (p - 1.0)


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    cores = [1, 2, 4, 8]
    out = {}
    for label, chunk in [("A_micro_k1", 1), ("A_coarse_k10000", 10_000)]:
        times, checks = {}, set()
        for p in cores:
            t, chk = run_granularity(p, total, chunk)
            times[p] = t
            checks.add(chk)
        assert len(checks) == 1, "result checksum differs between runs!"
        t1 = times[1]
        print(f"\n--- {label} (chunksize={chunk}, items={total:,}) ---")
        print(f"P= 1 | Time={t1:7.3f}s | Speedup= 1.00x | Eff=100.0%")
        for p in cores[1:]:
            sp = t1 / times[p]
            print(f"P={p:2d} | Time={times[p]:7.3f}s | Speedup={sp:5.2f}x | "
                  f"Eff={sp / p * 100:5.1f}% | Karp-Flatt e={karp_flatt(t1, times[p], p):6.3f}")
        out[label] = {str(p): times[p] for p in cores}
    json.dump(out, open("results_a.json", "w"), indent=2)