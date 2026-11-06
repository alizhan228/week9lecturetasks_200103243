# Task 09 - Three-phase simulation

| Phase | Share of parallel time | Treated as |
|---|---|---|
| A: disk I/O + parameter broadcast | 2% | serial |
| B: boundary message-passing sync | 6% | serial (per the sheet's framing) |
| C: core flux computation | 92% | parallel |

alpha = 0.02 + 0.06 = **0.08**; p = 0.92.

| P | alpha | S(P)=P-0.08(P-1) | E |
|---|---|---|---|
| 512 | 0.08 | 471.12 | 0.9202 |
| 2048 | 0.08 | 1884.24 | 0.9200 |

Worked: P=512: 512 - 0.08*511 = 512 - 40.88 = 471.12. P=2048: 2048 - 0.08*2047 = 2048 - 163.76 = 1884.24.

Alternative: S = s + pP = 0.08 + 0.92P gives the same (0.08+471.04=471.12; 0.08+1884.16=1884.24).

Critique: phase B (halo exchange) is not truly serial; it is parallel but non-scaling communication. If it's
treated as a fraction that grows with P, e.g. 0.06*log2(P)/log2(512), the effective alpha rises (see Task 12).
Under the "B is serial" assumption alpha = 0.08; if B were fully overlapped/parallel, alpha = 0.02 and S(512) = 502.78.
