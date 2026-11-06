# Task 08 - Amdahl vs Gustafson, s = alpha = 0.08, P = 128

Amdahl: S = 1/(s + (1-s)/P) = 1/(0.08 + 0.92/128) = 1/(0.08 + 0.007188) = 1/0.087188 = **11.470**
Gustafson: S = P - alpha(P-1) = 128 - 0.08*127 = 128 - 10.16 = **117.84**

Discrepancy
- Gustafson over Amdahl: (117.84-11.470)/11.470 = **927.4%** (ratio 10.27x)
- Amdahl below Gustafson: (117.84-11.470)/117.84 = **90.3%**
- Efficiency: Amdahl 0.0896 vs Gustafson 0.9206.

Why they diverge: the two models hold different things constant. Amdahl fixes problem size, so the parallel part
shrinks as 1/P and the serial part dominates (limit 1/s = 12.5). Gustafson fixes runtime, so the parallel work grows
with P and the serial part becomes a fixed, shrinking *share* of the total work (limit E -> 1-alpha). As P grows, Amdahl
saturates at 12.5 while Gustafson grows linearly with slope 1-alpha = 0.92; the gap grows without bound.
(Note: the same numeric 0.08 means different things: serial share of 1-core time vs. of P-core time, so the comparison is a model contrast, not a like-for-like prediction of one program.)
