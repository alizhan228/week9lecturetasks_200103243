# Task 04 - Asymptotic efficiency

**Gustafson:** E(P) = S/P = 1 - alpha(P-1)/P = (1-alpha) + alpha/P.
lim_{P->inf} E(P) = (1-alpha) + 0 = **1 - alpha**.
Proof: alpha/P -> 0. E decreases monotonically from 1 (P=1) to 1-alpha since dE/dP = -alpha/P^2 < 0. Even for alpha = 0.2, E >= 0.8 for every P.

**Amdahl:** E_A(P) = S_A/P = 1/(P s + (1-s)) -> **0** as P -> infinity, as 1/(sP) (since the denominator grows linearly). E_A(P) <= 1/(sP) so even s = 0.001 gives E < 10% at P = 10^4... precisely E_A(10^4) = 1/(10+0.999) = 9.1%.

**Deduction.** Under Gustafson the machine is asymptotically 1-alpha utilized; under Amdahl, utilization vanishes. Gustafson's E does not tend to 1 because the serial section idles P-1 cores for a fraction alpha of wall-time: exactly alpha(P-1)/P of the capacity is wasted. Also S_G(P) - S_A(P) -> infinity for any 0 < s < 1.
| alpha=s | P | E_Gustafson | E_Amdahl |
|---|---|---|---|
| 0.04 | 16 | 0.9625 | 0.6250 |
| 0.04 | 1024 | 0.9600 | 0.0239 |
| 0.04 | 16384 | 0.9600 | 0.0015 |
