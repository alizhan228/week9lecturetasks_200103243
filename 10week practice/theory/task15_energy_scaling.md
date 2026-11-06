# Task 15 - Energy under Gustafson scaling

Model (per core): P_idle = static power whenever the core is powered on; P_active = *additional* dynamic power while the core computes. Wall-clock time T = T_s + T_p (serial then parallel; during T_s only one core computes). Work (in core-seconds): W_P = T_s + P T_p.

**P-core energy:** E_P = P P_idle T + P_active (T_s + P T_p) = P P_idle T + P_active W_P.
**1-core energy for the same wall-clock T:** it does only W_1 = T of work: E_1 = (P_idle + P_active) T.

**Energy per unit of work**
- P cores: E_P / W_P = P_idle * (P T / W_P) + P_active = **P_idle / S(P) + P_active**, where S = W_P / T = scaled speedup.
- 1 core: E_1/W_1 = P_idle + P_active.

So at equal wall-clock time, the cluster delivers S times more work at total energy E_P = P P_idle T + P_active S T, i.e., **total energy grows ~P** (power proportionality: you pay for P nodes) but **energy per unit work drops** when the static power is a big share, since idle/static power is amortized over S useful cores. The saving is largest for high efficiency; the serial section wastes (P-1) P_idle T_s of static energy (a pure overhead; dynamic energy is not wasted if idle cores clock-gate).

**Example.** P_idle = 100 W, P_active = 150 W, alpha = 0.04, P = 1024: S = 983.08. P-core: 100/983.08 + 150 = 150.10 W per work unit; 1-core: 250. Ratio 0.600 (40% less energy per unit work). If P_idle = 0 (perfect proportionality), energy per work is identical (150), and parallelism only buys time, not energy.
**Caveat:** if comm overhead (Task 12) lowers S, the amortization drops. Interconnect/cooling power (PUE) are not modelled.
