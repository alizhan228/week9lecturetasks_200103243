# Task 11 - Gustafson vs Sun-Ni memory-bounded speedup

Let G(P) = factor by which the **workload** grows when memory grows P-fold (set by the algorithm's work-vs-memory relation).

- Amdahl (fixed size): G(P) = 1 -> S = 1/(s + (1-s)/P)
- Gustafson (fixed time): G(P) = P -> S = s + (1-s)P
- **Sun-Ni (memory bound): S*(P) = (s + (1-s)G(P)) / (s + (1-s)G(P)/P)**

Derivation: scaled serial time = s + (1-s)G(P); parallel time = s + (1-s)G(P)/P (the parallel work is split over P).
Check: G=1 gives Amdahl; G=P gives (s+(1-s)P)/(s+(1-s)) = Gustafson.

**Where G(P) comes from.** If the memory-bound problem uses N^d words and takes N^c operations, work-vs-memory is W ~ M^(c/d). Dense matmul c=3, d=2: **G(P) = P^(3/2)**. 3D stencil (steps ~ N): work ~ N^4 vs memory N^3: G ~ P^(4/3). Streaming/linear algorithms: G = P.

**When Gustafson is wrong.**
- **Underestimates** the achievable *scaled work throughput* when G(P) > P (compute grows faster than memory, e.g., matmul): S*(P) -> (1-s)G(P)/(s+(1-s)G/P)... numerically with s=0.05, P=64, G=P^1.5=512: S* = (0.05+0.95*512)/(0.05+0.95*8) = 486.5/7.65 = **63.6**, vs Gustafson 0.05+0.95*64 = 60.85 (4.5% under). The runtime however is **not** constant (it grows by G/P = 8x), which violates Gustafson's own fixed-time premise.
- **Overestimates** when G(P) < P: workloads whose useful work grows slower than memory (e.g. memory-bound algorithms where extra memory is spent on replicated or ghost data), or when memory fills and the problem cannot be scaled to keep P busy. Then S* < P - alpha(P-1). Example s=0.05, G=sqrt(P), P=64 -> G=8: S* = (0.05+0.95*8)/(0.05+0.95*8/64) = 7.65/0.16875 = **45.3** vs 60.85.
- Also overestimates when communication overhead grows with P (Task 12), not captured by either model.

**Takeaway.** Use Gustafson when time (not memory) is the binding resource and work scales ~linearly; use Sun-Ni when memory is the constraint.
