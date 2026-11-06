#!/usr/bin/env python3
"""Regenerates the numeric tables in calculations/*.md (tasks 06-10,16-18)."""
import math, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
G = lambda P, a: P - a * (P - 1)
A = lambda P, s: 1 / (s + (1 - s) / P)
def w(name, text): open(name, "w").write(text)

# ---- Task 06
a = 0.04; rows = ""
for P in [16, 64, 256, 1024, 4096, 16384]:
    S = G(P, a); rows += f"| {P} | {P}-0.04({P}-1) = {S:.2f} | {S/P:.5f} | {100*S/P:.3f}% | {P-S:.2f} |\n"
w("task06_parametric_table.md", f"""# Task 06 - Parametric speedup, alpha = 0.04

Formulas: S(P) = P - alpha(P-1); E(P) = S/P = 1 - alpha(P-1)/P.

| P | S(P) | E(P) | E % | Lost cores P-S |
|---|------|------|-----|------|
{rows}
## Evaluation
- Efficiency does **not** degrade meaningfully as P grows exponentially: it falls from 0.9625 (P=16) and
  saturates at 1 - alpha = 0.96. Only the first doublings matter, because (P-1)/P -> 1 quickly.
- Absolute lost capacity P - S = alpha(P-1) grows linearly (0.6 core at P=16, ~655 cores at P=16384), but that is a constant 4% of the machine.
- Contrast: Amdahl with s=0.04 caps at 25x regardless of P.
- Caveat: constant alpha is an assumption; real alpha(P) usually grows (see Task 12).
""")

# ---- Task 07
P, Smin = 8192, 7500
am = (P - Smin) / (P - 1)
w("task07_tolerable_serial.md", f"""# Task 07 - Maximum tolerable serial fraction

S(P) = P - alpha(P-1) >= S_min
=> alpha(P-1) <= P - S_min
=> **alpha_max = (P - S_min)/(P - 1)** (P>1, so the inequality direction is preserved)

Numbers: P = {P}, S_min = {Smin}:
alpha_max = ({P} - {Smin}) / ({P} - 1) = 692 / 8191 = **{am:.6f}** (about {100*am:.3f}%)

Check: S = 8192 - 0.084483*8191 = {G(P, am):.4f}. OK. Equivalent efficiency requirement E >= {Smin/P:.4f}.
Interpretation: up to ~8.45% of the *parallel-run* wall time may be serial. Any alpha above 0.084483 fails the 7,500 requirement.
""")

# ---- Task 08
s = 0.08; P = 128
sa, sg = A(P, s), G(P, s)
w("task08_cross_divergence.md", f"""# Task 08 - Amdahl vs Gustafson, s = alpha = 0.08, P = 128

Amdahl: S = 1/(s + (1-s)/P) = 1/(0.08 + 0.92/128) = 1/(0.08 + {0.92/128:.6f}) = 1/{s+0.92/P:.6f} = **{sa:.3f}**
Gustafson: S = P - alpha(P-1) = 128 - 0.08*127 = 128 - 10.16 = **{sg:.2f}**

Discrepancy
- Gustafson over Amdahl: ({sg:.2f}-{sa:.3f})/{sa:.3f} = **{100*(sg-sa)/sa:.1f}%** (ratio {sg/sa:.2f}x)
- Amdahl below Gustafson: ({sg:.2f}-{sa:.3f})/{sg:.2f} = **{100*(sg-sa)/sg:.1f}%**
- Efficiency: Amdahl {sa/P:.4f} vs Gustafson {sg/P:.4f}.

Why they diverge: the two models hold different things constant. Amdahl fixes problem size, so the parallel part
shrinks as 1/P and the serial part dominates (limit 1/s = 12.5). Gustafson fixes runtime, so the parallel work grows
with P and the serial part becomes a fixed, shrinking *share* of the total work (limit E -> 1-alpha). As P grows, Amdahl
saturates at 12.5 while Gustafson grows linearly with slope 1-alpha = 0.92; the gap grows without bound.
(Note: the same numeric 0.08 means different things: serial share of 1-core time vs. of P-core time, so the comparison is a model contrast, not a like-for-like prediction of one program.)
""")

# ---- Task 09
al = 0.02 + 0.06
t = "".join(f"| {P} | {al:.2f} | {G(P,al):.2f} | {G(P,al)/P:.4f} |\n" for P in (512, 2048))
w("task09_multicomponent.md", f"""# Task 09 - Three-phase simulation

| Phase | Share of parallel time | Treated as |
|---|---|---|
| A: disk I/O + parameter broadcast | 2% | serial |
| B: boundary message-passing sync | 6% | serial (per the sheet's framing) |
| C: core flux computation | 92% | parallel |

alpha = 0.02 + 0.06 = **0.08**; p = 0.92.

| P | alpha | S(P)=P-0.08(P-1) | E |
|---|---|---|---|
{t}
Worked: P=512: 512 - 0.08*511 = 512 - 40.88 = 471.12. P=2048: 2048 - 0.08*2047 = 2048 - 163.76 = 1884.24.

Alternative: S = s + pP = 0.08 + 0.92P gives the same (0.08+471.04=471.12; 0.08+1884.16=1884.24).

Critique: phase B (halo exchange) is not truly serial; it is parallel but non-scaling communication. If it's
treated as a fraction that grows with P, e.g. 0.06*log2(P)/log2(512), the effective alpha rises (see Task 12).
Under the "B is serial" assumption alpha = 0.08; if B were fully overlapped/parallel, alpha = 0.02 and S(512) = 502.78.
""")

# ---- Task 10
bytes_cell, arrays, cap = 8, 2, 32 * 2**30
rows = ""
for nodes in (64, 512):
    cells_node = cap / (bytes_cell * arrays); cells = cells_node * nodes
    N = round(cells ** (1/3)); n_node = round(cells_node ** (1/3))
    rows += f"| {nodes} | {nodes*32} GiB | {cells:.3e} | {cells ** (1/3):.0f} | {cells_node ** (1/3):.0f} (per node) |\n"
w("task10_memory_growth.md", f"""# Task 10 - Memory ceiling for a 3D grid

Model: M(P) = c*P with per-node cap 32 GiB. Grid cell state = {arrays} arrays (double-buffered) x {bytes_cell} B = {arrays*bytes_cell} B/cell (assumption; state yours).
Aggregate capacity M_max(P) = 32 GiB * P; N^3 * {arrays*bytes_cell} <= 32 GiB * P  =>  **N_max = (32 GiB * P / {arrays*bytes_cell} B)^(1/3)**.

Per node: 32 GiB/16 B = {cap/16:.3e} cells -> n = {(cap/16) ** (1/3):.0f}^3.

| Nodes | Aggregate memory | Max cells | N_max (global, N x N x N) | Sub-block |
|---|---|---|---|---|
{rows}
Observations
- Under pure weak scaling W(P) = P*W(1), N = N1 * P^(1/3): 8x more nodes (64->512) gives only 2x larger N (~{(512*cap/16)**(1/3)/((64*cap/16)**(1/3)):.0f}x).
- Memory is exactly proportional to P, so weak scaling is always memory-feasible *per node* for this solver; it fails only if the algorithm needs replicated global data (M per node growing with P).
- With 1 array of doubles (8 B/cell): N_max is 2^(1/3)=1.26x larger; with 5 arrays it's 0.74x of the 2-array figures. Adjust by the factor (arrays)^(-1/3).
""")

# ---- Task 16
rows = ""
for P in (1, 8, 27, 64, 125, 512, 1000, 4096):
    rows += f"| {P} | {P**(1/3):.3f} | N1*{P**(1/3):.3f} | {P**(-1/3):.3f} |\n"
w("task16_gemm_scaling.md", f"""# Task 16 - GEMM dimension growth under constant runtime

Flops W(N) = 2N^3, per-processor work W/P. Constant runtime means N^3/P = N1^3, hence **N(P) = N1 * P^(1/3)**.
Memory (3 matrices) = 3N^2 words total = 3 N1^2 P^(2/3), per-processor memory = 3 N1^2 P^(-1/3), so it **shrinks** with P.
Note: ignoring communication. Real 2D-distributed GEMM adds O(N^2/sqrt(P)) per-processor communication, so true weak scaling needs N to grow a bit faster / efficiency decays slowly (isoefficiency Theta(P^1.5) in work for Cannon-style).

| P | N/N1 = P^(1/3) | N | memory per proc relative to P=1 |
|---|---|---|---|
{rows}
Example N1 = 4096: P=8 -> 8192; P=64 -> 16384; P=512 -> 32768; P=4096 -> 65536.
Total *memory* scales as P^(2/3) while total *work* scales as P: GEMM is compute-rich, so memory is not the binding constraint (contrast with Sun-Ni, Task 11).
""")

# ---- Task 17
w("task17_stencil_scaling.md", f"""# Task 17 - 7-point 3D stencil

Weak scaling: each of P ranks keeps an n^3 sub-block, so global N = n P^(1/3), total volume = P n^3 (proportional to P).
Per-rank compute: ~8 flops * n^3 (7 loads, 6 add/1 mul-ish). Per-rank halo: 6 faces * n^2 words (interior rank).
**Comm/compute ratio = 6 n^2 / (c n^3) = 6/(c n)**, which is **independent of P**. Surface-to-volume stays constant, so the parallel overhead is constant and alpha does not grow.
Efficiency per Gustafson: E = 1 - alpha(P-1)/P tends to a constant.

Contrast:
- Strong scaling (fixed N): n = N/P^(1/3), so ratio = 6 P^(1/3)/(cN), which **degrades** as P^(1/3).
- Isoefficiency: weak scaling already satisfies it; W = Theta(P).
Caveats: (1) latency term: each halo message has startup alpha_net, constant per step, so per-step time constant (good). (2) Global reductions (e.g., residual norm, dt) cost O(log P): the real source of degradation. (3) Ranks on the machine boundary have fewer faces, so interior-rank count matters; on 3D torus topologies neighbour exchange is O(1) hops.
Table (n=128 per rank, c=8): ratio = 6/(8*128) = 0.00586 per cell-update; same for P=1..16384; global N = 128*P^(1/3): P=8 -> 256, P=64 -> 512, P=512 -> 1024, P=4096 -> 2048.
""")

# ---- Task 18 numbers
rows = ""
for P in (1, 4, 16, 64, 256, 1024):
    N2 = 1e6 * math.sqrt(P)
    # BH: N log N / P = N1 log N1 / 1; solve N by iteration
    N1 = 1e6; tgt = N1 * math.log2(N1); N = N1 * P
    for _ in range(100): N = tgt * P / math.log2(N)
    rows += f"| {P} | {N2:.3e} | {N:.3e} | {N/N1:.1f} |\n"
w("task18_table.tmp", rows)
