# Task 03 - Serial fraction frame of reference

**Amdahl:** s_1 = serial share of the **uniprocessor** time for a fixed problem size N.
**Gustafson:** alpha = serial share of the **P-processor** time for a problem sized for P processors.

**Conversion.** From Task 02: serial time s', parallel time p' (s'+p' = 1 on P procs). Uniprocessor time for the scaled problem: T_1 = s' + p'P. The uniprocessor serial fraction of the *scaled* problem is

  s_1(P) = s' / (s' + p'P) = alpha / (alpha + (1-alpha)P)  -> 0 as P -> infinity.

**Substitute into Amdahl's law** (it is just the identity T_1/T_P):

  Since s_1 + (1-s_1)/P = [alpha P + (alpha + (1-alpha)P) - alpha] / (P(alpha+(1-alpha)P)) = P / (P(alpha+(1-alpha)P)) = 1/(alpha+(1-alpha)P),

  so S = alpha + (1-alpha)P = Gustafson. The two laws are **identical** once the serial fraction is quoted for the same problem on the same frame of reference.

**Resolution of the paradox.** "A 0.4% serial fraction limits S to 250" is true only for the *fixed* N whose uniprocessor profile has s_1 = 0.4%. Growing the problem with P reduces s_1(P) (e.g., alpha = 0.004, P = 1024: s_1 = 0.004/(0.004+0.996*1024) = 3.9e-6), so the Amdahl ceiling 1/s_1 grows with the problem. Measuring alpha on the parallel machine *bakes in* the scaled problem size, so the serial overhead is a constant fraction of the P-processor timeline and cannot throttle scaling.

**Caveat (critical).** This only holds if serial time is truly independent of problem size. If serial work grows with N (e.g., I/O proportional to output size, sequential setup O(N)), alpha is not constant and the paradox returns (Tasks 12, 13).
