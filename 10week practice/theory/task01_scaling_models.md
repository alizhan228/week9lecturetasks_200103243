# Task 01 - Amdahl (strong scaling, fixed-size) vs Gustafson (weak scaling, fixed-time)

## Amdahl (1967)
- **Assumption:** the problem size N is constant; a fraction s of its single-processor time is inherently serial.
- Parallel time: T(P) = T(1)[s + (1-s)/P]. Speedup S = 1/(s + (1-s)/P) -> **1/s** as P -> infinity.
- As P -> infinity, **N stays fixed**, so each processor receives a vanishing slice N/P and the serial part dominates.
- Question answered: *"How much faster can I solve this same problem?"* -> **fixed-size** scaling.

## Gustafson (1988)
- **Assumption:** users scale the problem to the machine so that **wall-clock time stays (roughly) constant**. Serial work (setup, I/O) is roughly independent of N, the parallel work grows.
- Parallel time normalized: s + p = 1. Equivalent serial time: s + pP. S(P) = s + pP = P - alpha(P-1), unbounded and linear in P with slope 1-alpha.
- As P -> infinity, **N grows (the parallel work grows ~ linearly in P)** while the serial time s stays constant.
- Question answered: *"How much more problem can I solve in the same time?"* -> **fixed-time** scaling.

## Why the names
| | Amdahl | Gustafson |
|---|---|---|
| Held constant | problem size W | execution time T_P |
| Varies | time (decreases) | problem size (increases) |
| Serial fraction measured on | uniprocessor, fixed size | the P-processor run, scaled size |
| Limit S(P->inf) | 1/s | infinite (linear, slope 1-alpha) |
| Limit E(P->inf) | 0 | 1-alpha |

## Philosophical / physical divergence
Amdahl treats the workload as a physical given (a particular program, a particular input), so the machine is the variable and parallelism is a way to **reduce latency**. Gustafson treats the *time budget* as the given (a weather forecast must finish before tomorrow, a design cycle overnight), so the workload is the variable and parallelism is a way to **buy resolution/accuracy/throughput**. Physically, many scientific codes have serial portions (reading input, setup) that do not grow with grid size, while the computation grows with grid points; so the serial *fraction* shrinks as the problem grows. Both laws are the same arithmetic identity (see Task 03) applied to different questions; neither is wrong, but each is only valid when its constant is the real-world constraint.
