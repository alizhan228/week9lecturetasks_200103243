# Task 14 - Isoefficiency of a Gustafson-compliant program

**Definitions (Grama, Gupta, Kumar).** W = serial work (T_1). Total overhead T_o(W,P) = P T_P - W. Efficiency E = W/(W + T_o). For constant E: **W = K T_o(W,P)** with K = E/(1-E). The isoefficiency function is the growth W(P) that satisfies it.

**Gustafson program.** Using the Task 02 units: T_P = 1, T_1 = W = alpha + (1-alpha)P.
T_o = P*1 - W = P - alpha - (1-alpha)P = alpha P - alpha = **alpha(P-1)**.

Proof of E: W/(W+T_o) = [alpha + (1-alpha)P] / P = 1 - alpha(P-1)/P. matches Task 02.

**Isoefficiency:** W = K alpha (P-1) -> **W = Theta(P)**: linear isoefficiency, the best achievable (W must grow at least linearly or processors idle). Equivalent: constant E requires W/P constant, which is *exactly* what weak scaling does. So **weak scaling with constant alpha is isoefficient by construction**; the efficiency settles at 1-alpha.

**Critique.** The result is built-in because Gustafson's model fixes T_o = Theta(P) (idle processors during the serial part). Real overheads are larger:
- With comm. term C(P)=c log P (Task 12): T_o = Theta(P log P) -> isoefficiency Theta(P log P).
- With C = c sqrt(P): Theta(P^1.5).
- 2D-distributed GEMM (Cannon): Theta(P^1.5) in work (N ~ sqrt(P)... N^3 ~ P^1.5) - see Task 16.
Isoefficiency is therefore more discriminating than Gustafson's law: it asks *how fast* work must grow, and exposes the cases where memory (W <= memory M ~ P) can't keep up.
**Memory check:** if isoefficiency W = Theta(P^x) with x > 1 and memory grows ~P, weak-scaling can't be sustained once W(P) outgrows memory: Sun-Ni link (Task 11).
