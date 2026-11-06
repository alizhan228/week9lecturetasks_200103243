# Task 07 - Maximum tolerable serial fraction

S(P) = P - alpha(P-1) >= S_min
=> alpha(P-1) <= P - S_min
=> **alpha_max = (P - S_min)/(P - 1)** (P>1, so the inequality direction is preserved)

Numbers: P = 8192, S_min = 7500:
alpha_max = (8192 - 7500) / (8192 - 1) = 692 / 8191 = **0.084483** (about 8.448%)

Check: S = 8192 - 0.084483*8191 = 7500.0000. OK. Equivalent efficiency requirement E >= 0.9155.
Interpretation: up to ~8.45% of the *parallel-run* wall time may be serial. Any alpha above 0.084483 fails the 7,500 requirement.
