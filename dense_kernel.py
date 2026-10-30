
import argparse
import hashlib
import json
import os
import statistics
import time

import numpy as np
from numba import njit

from salt import get_student_params


@njit(cache=True)
def matmul_ijk(A, B, C, M):
    for i in range(M):
        for j in range(M):
            acc = 0.0
            for k in range(M):
                acc += A[i * M + k] * B[k * M + j]  # B strides by M
            C[i * M + j] = acc


@njit(cache=True)
def matmul_ikj(A, B, C, M):
    for i in range(M):
        for j in range(M):
            C[i * M + j] = 0.0
        for k in range(M):
            a = A[i * M + k]  # hoisted
            for j in range(M):
                C[i * M + j] += a * B[k * M + j]  # stride-1


def timed(fn, A, B, M, runs=3):
    times = []
    for _ in range(runs):
        C = np.zeros(M * M)
        t0 = time.perf_counter_ns()
        fn(A, B, C, M)
        times.append(time.perf_counter_ns() - t0)
    return statistics.median(times), C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-id", required=True)
    args = ap.parse_args()

    p = get_student_params(args.student_id)
    N, M = p["N"], p["N"] // 2
    rng = np.random.default_rng(p["seed"])
    A = rng.random(M * M)  # flat 1D buffers
    B = rng.random(M * M)

    # JIT warm-up on a tiny problem so compile time isn't measured
    w = np.zeros(16)
    matmul_ijk(A[:16], B[:16], w, 4)
    matmul_ikj(A[:16], B[:16], w, 4)

    t_naive, C1 = timed(matmul_ijk, A, B, M)
    t_swap, C2 = timed(matmul_ikj, A, B, M)
    max_diff = float(np.max(np.abs(C1 - C2)))
    digest = hashlib.sha256(np.round(C2, 6).tobytes()).hexdigest()

    result = {
        "N": N,
        "M": M,
        "runs": 3,
        "t_naive_ijk_ns": t_naive,
        "t_interchanged_ikj_ns": t_swap,
        "speedup": t_naive / t_swap,
        "max_abs_diff": max_diff,
        "within_1e-12": max_diff <= 1e-12,
        "digest_ikj_rounded_6dp": digest,
    }
    os.makedirs("results", exist_ok=True)
    with open("results/loop_interchange.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()