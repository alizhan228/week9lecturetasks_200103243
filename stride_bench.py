import os
import statistics
import time

import numpy as np
from numba import njit

STRIDES = [1, 2, 4, 8, 16, 32, 64, 128]
WARMUP, RUNS = 5, 5


@njit(fastmath=True, cache=True)
def strided_sum(data, s):
    total = 0.0
    for i in range(0, data.shape[0], s):
        total += data[i]
    return total


def main():
    data = np.ones(16_777_216, dtype=np.float64)  # ~134 MB, > L3
    n = data.shape[0]
    strided_sum(data[:1024], 1)  # JIT compile outside timing

    os.makedirs("results", exist_ok=True)
    rows = []
    for s in STRIDES:
        touched = (n + s - 1) // s
        times = []
        for it in range(WARMUP + RUNS):
            t0 = time.perf_counter_ns()
            total = strided_sum(data, s)
            t1 = time.perf_counter_ns()
            assert total == touched  # data is all ones
            if it >= WARMUP:
                times.append(t1 - t0)
        med = statistics.median(times)
        rows.append((s, touched, med, med / touched))
        print(f"stride {s:4d}: {med / touched:7.3f} ns/element")

    with open("results/stride_results.tsv", "w") as f:
        f.write("stride\telements_touched\tmedian_time_ns\tlatency_per_element_ns\n")
        for s, touched, med, lat in rows:
            f.write(f"{s}\t{touched}\t{med:.0f}\t{lat:.4f}\n")


if __name__ == "__main__":
    main()