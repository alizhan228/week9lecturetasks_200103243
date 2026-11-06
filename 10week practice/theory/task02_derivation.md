# Task 02 - Derivation of Gustafson's scaled speedup

**Setup.** Let a program run on P identical processors. Normalize the measured parallel wall-time to 1:

1. T_P = s + p = 1, where s = serial time (one processor busy, P-1 idle), p = time in the parallel region (all P busy). Justification: normalization of units; s is also the serial fraction alpha *as observed on the parallel machine*.

2. Work done in the parallel region: P processors x p time = pP units (assuming perfect balance and that each unit takes 1 processor-time unit on a single processor).

3. Time for the same scaled problem on one processor: the serial part still takes s; the parallel region's pP units of work executed sequentially take pP. So T_1 = s + pP. (Justification: a single processor performs serial and parallel work one after another with no overlap.)

4. Scaled speedup = T_1 / T_P = (s + pP) / (s + p) = s + pP. (Justification: definition; denominator is 1 by step 1.)

5. Substitute p = 1 - s and alpha = s:  S(P) = alpha + (1-alpha)P = alpha + P - alpha P = **P - alpha(P - 1)**. QED.

6. Efficiency: E = S/P = (1-alpha) + alpha/P = 1 - alpha(P-1)/P.

**Sanity checks.** P = 1: S = 1. alpha = 0: S = P. alpha = 1: S = 1 (everything serial). Slope dS/dP = 1 - alpha.

**Assumptions.** (i) Serial time independent of P, (ii) parallel region perfectly load balanced, (iii) no parallel overhead apart from the serial part, (iv) the one-processor run is hypothetical (it may not fit in memory; see Task 11).
