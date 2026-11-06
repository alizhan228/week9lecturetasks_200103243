# Task 19 - Monte Carlo: where does alpha come from?

Monte Carlo is the textbook weak-scaling workload: each of P workers draws k samples; total samples kP; time stays ~constant.

## Sources of serial fraction
1. **PRNG seeding/stream management.** Naive "seed = rank" gives correlated streams. Options: leapfrog or block-splitting of one stream (needs O(log n) jump-ahead or O(P) setup), Mersenne-Twister jump-ahead (expensive, ~ms per stream), SPRNG/parameterized generators, or **counter-based generators (Philox, Threefry)** where stream = (key=rank, counter) and setup is O(1), so it removes the serial part.
2. **Reduction of partial sums** (mean, variance, histogram): a binary tree costs ceil(log2 P) steps of latency t_r each; a linear gather costs (P-1) t_r.
3. **Output serialization / checkpointing** (rank 0 writes results) - O(1) to O(P) depending on whether each rank writes.
4. **Initialization/geometry/model loading** and MPI startup.
5. **Load imbalance** when samples have variable cost (path termination) - appears as idle time, so it increases alpha.
6. **Variance combination**: need a parallel (Chan) algorithm to avoid precision loss.

## Quantifying the reduction (assume T_work = 100 s, serial init + output 0.1 s, t_r = 20 microseconds per level/message, P = 65,536)
| Reduction | Reduction time | T_P | alpha = serial/T_P | S(P) = P - alpha(P-1) | E |
|---|---|---|---|---|---|
| tree: 16 levels | 0.32 ms | 100.1003 s | 0.00100 | 65,470 | 0.9990 |
| linear gather: 65,535 messages | 1.31 s | 101.4107 s | 0.01391 | 64,624 | 0.9861 |

The tree reduction contributes only ~0.3% of the serial time; the **init/output** dominates alpha. Reducing the 0.1 s serial section by 10x improves S more than any reduction optimization. The logarithmic reduction becomes visible only when the per-level latency is large (e.g., 100 us over a congested WAN) or when the reduced object is big (histograms: bandwidth term proportional to size x log P).

**Recommendation:** counter-based RNG, tree (or hardware-offloaded) reductions, one-file-per-rank or collective parallel I/O, overlap output with computation. Expected weak scaling efficiency > 98% to 10^5 cores.
