# Task 12 - Gustafson with communication overhead

**Model.** Normalize the compute time on P processors to 1 (s + p = 1, as in Task 02) and add a communication/synchronization time C(P), expressed relative to that compute time (C(1) = 0):

  T_P = s + p + C(P) = 1 + C(P),     T_1 = s + pP.

**Modified scaled speedup**

  S_C(P) = (s + pP) / (1 + C(P)) = [P - s(P-1)] / (1 + C(P)),    E_C(P) = S_C(P)/P.

This is the "fixed work per processor" reading: the problem grows as in Gustafson, runtime grows by the factor 1 + C(P).

**Fixed-time reading.** If the per-processor work is cut by C(P) so runtime stays 1, then p' = p - C(P) and S = s + (1 - s - C(P))P = P - (s + C(P))P + s, i.e. approximately alpha_eff = s + C(P) replaces alpha.

**Choices for C(P)** (c = cost of one exchange relative to compute)
| Pattern | C(P) |
|---|---|
| tree reduction / broadcast | c log2 P |
| halo exchange on a 2D mesh with sqrt(P) diameter | c sqrt(P) |
| nearest-neighbour halo | c (constant) |
| all-to-all | c P |

**Limits.** With C = c log2 P: E_C -> (1-s)/(1 + c log2 P), which goes to 0 slowly, so weak scaling no longer has a floor at 1 - alpha. With C = c sqrt(P), E decays like P^(-1/2).

**Numeric example** (s = 0.02, P = 1024)
- log model, c = 0.01: C = 0.1, S = 1003.54 / 1.1 = **912.3**, E = 0.891 (plain Gustafson: 1003.5).
- sqrt model, c = 0.001: C = 0.032, S = 1003.54 / 1.032 = **972.4**, E = 0.950.

**Fitting.** Measure T_P at several P, normalize by T_1 of the per-processor problem, and regress T_P/T_1 - 1 against log2 P or sqrt(P) to estimate c.
