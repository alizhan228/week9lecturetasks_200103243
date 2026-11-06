# Task 10 - Memory ceiling for a 3D grid

Model: M(P) = c*P with per-node cap 32 GiB. Grid cell state = 2 arrays (double-buffered) x 8 B = 16 B/cell (assumption; state yours).
Aggregate capacity M_max(P) = 32 GiB * P; N^3 * 16 <= 32 GiB * P  =>  **N_max = (32 GiB * P / 16 B)^(1/3)**.

Per node: 32 GiB/16 B = 2.147e+09 cells -> n = 1290^3.

| Nodes | Aggregate memory | Max cells | N_max (global, N x N x N) | Sub-block |
|---|---|---|---|---|
| 64 | 2048 GiB | 1.374e+11 | 5161 | 1290 (per node) |
| 512 | 16384 GiB | 1.100e+12 | 10321 | 1290 (per node) |

Observations
- Under pure weak scaling W(P) = P*W(1), N = N1 * P^(1/3): 8x more nodes (64->512) gives only 2x larger N (~2x).
- Memory is exactly proportional to P, so weak scaling is always memory-feasible *per node* for this solver; it fails only if the algorithm needs replicated global data (M per node growing with P).
- With 1 array of doubles (8 B/cell): N_max is 2^(1/3)=1.26x larger; with 5 arrays it's 0.74x of the 2-array figures. Adjust by the factor (arrays)^(-1/3).
