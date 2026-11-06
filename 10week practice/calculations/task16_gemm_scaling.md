# Task 16 - GEMM dimension growth under constant runtime

Flops W(N) = 2N^3, per-processor work W/P. Constant runtime means N^3/P = N1^3, hence **N(P) = N1 * P^(1/3)**.
Memory (3 matrices) = 3N^2 words total = 3 N1^2 P^(2/3), per-processor memory = 3 N1^2 P^(-1/3), so it **shrinks** with P.
Note: ignoring communication. Real 2D-distributed GEMM adds O(N^2/sqrt(P)) per-processor communication, so true weak scaling needs N to grow a bit faster / efficiency decays slowly (isoefficiency Theta(P^1.5) in work for Cannon-style).

| P | N/N1 = P^(1/3) | N | memory per proc relative to P=1 |
|---|---|---|---|
| 1 | 1.000 | N1*1.000 | 1.000 |
| 8 | 2.000 | N1*2.000 | 0.500 |
| 27 | 3.000 | N1*3.000 | 0.333 |
| 64 | 4.000 | N1*4.000 | 0.250 |
| 125 | 5.000 | N1*5.000 | 0.200 |
| 512 | 8.000 | N1*8.000 | 0.125 |
| 1000 | 10.000 | N1*10.000 | 0.100 |
| 4096 | 16.000 | N1*16.000 | 0.063 |

Example N1 = 4096: P=8 -> 8192; P=64 -> 16384; P=512 -> 32768; P=4096 -> 65536.
Total *memory* scales as P^(2/3) while total *work* scales as P: GEMM is compute-rich, so memory is not the binding constraint (contrast with Sun-Ni, Task 11).
