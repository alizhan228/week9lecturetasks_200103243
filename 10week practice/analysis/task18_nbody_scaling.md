# Task 18 - N-body scaling at constant time per iteration

Weak scaling here means: choose N(P) so time per step stays constant. Per-step cost for an algorithm with work f(N): f(N)/P = f(N1). Baseline N1 = 10^6 particles on one processor.

## Direct all-pairs, f = N^2
N^2/P = N1^2 -> **N = N1 sqrt(P)**. Total work grows P (as required), but particles per processor N/P = N1/sqrt(P) *shrinks*. Communication: each processor needs all N positions (O(N) data), so comm per processor ~ N1 sqrt(P) grows, while compute per processor is constant: **comm/compute ratio ~ sqrt(P) / N1 * const** grows -> the parallel (non-scaling) fraction rises as sqrt(P): alpha_eff(P) = O(sqrt(P)/N1). With ring/systolic pipelining comm can overlap compute until sqrt(P) ~ N1.

## Barnes-Hut, f = N log N
N log N / P = N1 log N1 -> N log2 N = P N1 log2 N1 (solve iteratively). Result (N1 = 10^6):

| P | N all-pairs | N Barnes-Hut | ratio N_BH/N1 |
|---|---|---|---|
| 1 | 1.000e+06 | 1.000e+06 | 1.0 |
| 4 | 2.000e+06 | 3.657e+06 | 3.7 |
| 16 | 4.000e+06 | 1.347e+07 | 13.5 |
| 64 | 8.000e+06 | 4.988e+07 | 49.9 |
| 256 | 1.600e+07 | 1.858e+08 | 185.8 |
| 1024 | 3.200e+07 | 6.949e+08 | 694.9 |

So Barnes-Hut supports a **much larger N (~P / log factor)** at the same time per step, but: (i) tree construction and top-of-tree/essential-tree exchange have serial or O(log P) parts, (ii) irregular, data-dependent traversal causes load imbalance, (iii) the communication per processor is O(N/P)^(2/3)-like surface data plus the "locally essential tree", so alpha_eff grows slowly (about log P) but not constant. Expect weak-scaling efficiency to decay more gently than all-pairs but not stay at 1 - alpha.

## Serial/parallel ratio shift
- All-pairs: serial part (integration update, I/O) is O(N) while parallel is O(N^2/P): serial share = O(N P / N^2) = O(P/N) = O(sqrt(P)/N1) *grows* with sqrt(P) at constant time.
- Barnes-Hut: the non-scaling part is the top of the tree and the global exchange, roughly O(log P) per step against O(N/P log N) local work, so the serial share is small when N/P is large and grows only slowly (about log P / (N/P)).
Conclusion: both methods weak scale in *work*, but the tree code keeps the communication-to-compute ratio far lower and is the realistic choice at scale; all-pairs is attractive only for GPUs / small N with very high flop efficiency.
