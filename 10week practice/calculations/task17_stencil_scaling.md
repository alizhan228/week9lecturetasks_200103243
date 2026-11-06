# Task 17 - 7-point 3D stencil

Weak scaling: each of P ranks keeps an n^3 sub-block, so global N = n P^(1/3), total volume = P n^3 (proportional to P).
Per-rank compute: ~8 flops * n^3 (7 loads, 6 add/1 mul-ish). Per-rank halo: 6 faces * n^2 words (interior rank).
**Comm/compute ratio = 6 n^2 / (c n^3) = 6/(c n)**, which is **independent of P**. Surface-to-volume stays constant, so the parallel overhead is constant and alpha does not grow.
Efficiency per Gustafson: E = 1 - alpha(P-1)/P tends to a constant.

Contrast:
- Strong scaling (fixed N): n = N/P^(1/3), so ratio = 6 P^(1/3)/(cN), which **degrades** as P^(1/3).
- Isoefficiency: weak scaling already satisfies it; W = Theta(P).
Caveats: (1) latency term: each halo message has startup alpha_net, constant per step, so per-step time constant (good). (2) Global reductions (e.g., residual norm, dt) cost O(log P): the real source of degradation. (3) Ranks on the machine boundary have fewer faces, so interior-rank count matters; on 3D torus topologies neighbour exchange is O(1) hops.
Table (n=128 per rank, c=8): ratio = 6/(8*128) = 0.00586 per cell-update; same for P=1..16384; global N = 128*P^(1/3): P=8 -> 256, P=64 -> 512, P=512 -> 1024, P=4096 -> 2048.
