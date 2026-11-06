# Task 24 - Hardware audit and empirical vs theoretical discrepancy

> **Important:** the numbers in `benchmarks/results.csv` and `plots/scaling_comparison.*` that ship with this repo were produced in an **online sandbox with ONE vCPU**, with 1-16 OpenMP threads **oversubscribed** on it. They validate that the pipeline runs end-to-end; they are **not a weak-scaling result**. Re-run Task 22/23 on your own multicore machine and re-generate the plots before submitting.

## Sandbox hardware (where the shipped data came from)
| Item | Value |
|---|---|
| CPU | Intel Xeon (family 6, model 207, Sapphire Rapids class), 2.10 GHz, AVX-512/AMX flags |
| Cores / threads | 1 vCPU, 1 thread/core, 1 socket (KVM guest) |
| L1d / L1i | 48 KiB / 32 KiB |
| L2 / L3 | 2 MiB / 260 MiB reported by the guest (shared host L3; not dedicated) |
| Memory channels / NUMA | not visible under virtualization; single NUMA node |

## What the shipped run shows
Threads 1,2,4,8,16 oversubscribed on 1 vCPU, 5 reps each, 30M iterations per thread. Weak-scaling time T(P) grows ~P (0.035 s -> 0.35 s), since total work grew P-fold on a single core; the extra "speedup" (S about 1.6 at P=16) comes only from the fixed serial section being a shrinking share of T, and the fitted alpha = 0.949 is an artifact. On one core the scaled speedup is bounded by about 1 + (serial time)/(parallel time per thread-unit), so it saturates near 1.6 here instead of growing with P.

## Template for your machine (fill in)
Collect with: `lscpu`, `lscpu -C`, `numactl -H`, `lstopo`, `dmidecode -t memory` (root), `cat /sys/devices/system/cpu/cpu0/cache/index*/size`.
- CPU model, base/boost frequency, cores x SMT, sockets
- Cache: L1d/L1i, L2 per core, L3 shared (size, slices)
- Memory: channels x DIMM speed -> peak GB/s
- NUMA nodes and core-to-node map

## Expected deviations from the Gustafson curve
1. **Memory bandwidth saturation.** The benchmark is compute-bound (sin/ division), so it scales until FP units/ports saturate, but a memory-streaming variant saturates at the socket's channel count (a few cores).
2. **SMT/hyper-threads.** Threads beyond physical cores share execution units: S(P) flattens, expect about 1.2-1.3x gain, not 2x.
3. **Turbo/thermal throttling.** Single-thread runs boost to max frequency; all-core runs run 10-30% slower, so T(P) increases with P and measured S falls below the model even with alpha ~ 0. Fit alpha only on physical cores and note the frequency (check `turbostat`).
4. **NUMA boundaries.** Crossing sockets (OMP threads across nodes, first-touch not respected) adds remote-memory latency; use `OMP_PROC_BIND=close OMP_PLACES=cores` and first-touch initialization. A visible kink in S at the socket boundary is the signature.
5. **OS noise / frequency scaling / other tenants** inflate the standard deviation; use 5+ runs, quiet machine, performance governor.
6. **Thread startup/barrier cost** grows ~log P (Task 12) and shows up as alpha_eff increasing with P.

Compare the fitted alpha_observed with the instrumented serial fraction (time of the serial section / T_P): a large gap points to the effects above and not to the algorithm.
