# Task 06 - Parametric speedup, alpha = 0.04

Formulas: S(P) = P - alpha(P-1); E(P) = S/P = 1 - alpha(P-1)/P.

| P | S(P) | E(P) | E % | Lost cores P-S |
|---|------|------|-----|------|
| 16 | 16-0.04(16-1) = 15.40 | 0.96250 | 96.250% | 0.60 |
| 64 | 64-0.04(64-1) = 61.48 | 0.96062 | 96.062% | 2.52 |
| 256 | 256-0.04(256-1) = 245.80 | 0.96016 | 96.016% | 10.20 |
| 1024 | 1024-0.04(1024-1) = 983.08 | 0.96004 | 96.004% | 40.92 |
| 4096 | 4096-0.04(4096-1) = 3932.20 | 0.96001 | 96.001% | 163.80 |
| 16384 | 16384-0.04(16384-1) = 15728.68 | 0.96000 | 96.000% | 655.32 |

## Evaluation
- Efficiency does **not** degrade meaningfully as P grows exponentially: it falls from 0.9625 (P=16) and
  saturates at 1 - alpha = 0.96. Only the first doublings matter, because (P-1)/P -> 1 quickly.
- Absolute lost capacity P - S = alpha(P-1) grows linearly (0.6 core at P=16, ~655 cores at P=16384), but that is a constant 4% of the machine.
- Contrast: Amdahl with s=0.04 caps at 25x regardless of P.
- Caveat: constant alpha is an assumption; real alpha(P) usually grows (see Task 12).
