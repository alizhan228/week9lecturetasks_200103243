# Task 20 - Why graph analytics resists Gustafson scaling

**Dense linear algebra (reference).** Regular access, work/memory ratio rises with N (matmul O(N^3)/O(N^2)), static, balanced partition, nearest-neighbour or structured communication, constant per-core compute rate. Weak scaling is easy to define and nearly achievable.

**BFS / PageRank on power-law graphs**
1. **"Problem size" is ambiguous.** Doubling vertices does not double the work per processor, because degree distribution, diameter and frontier sizes change; BFS level count grows with diameter (log N for small-world graphs). Work is data dependent, so "constant time" can't be arranged by sizing.
2. **Irregular memory access.** Pointer chasing, ~1 cache miss per edge, so performance is latency/bandwidth-bound, not flop-bound; per-core rate drops as the graph exceeds cache, TLB and local memory (so the per-node baseline itself shifts with scale).
3. **Load imbalance from skew.** Hubs (vertices with degrees 10^5-10^6) give some partitions much more work; 1D partitioning concentrates edges; 2D/delegate (hub replication) schemes help but cost memory and communication.
4. **Frontier imbalance and synchronization.** BFS is level-synchronous: each level has a barrier and an all-to-all of frontier vertices; early/late levels have tiny frontiers that cannot occupy P processors (the serial fraction is level-count x barrier latency, which grows with P and diameter).
5. **Communication is not surface-to-volume.** Random-like graphs have cut edges ~ (1 - 1/P) of all edges: communication volume per node stays roughly constant or grows relative to compute; bisection bandwidth becomes the bottleneck (cf. Graph500 ranks by TEPS and shows modest efficiency).
6. **Low arithmetic intensity** so the memory wall hits before the parallelism limit.
7. **Weak-scaling definition for graphs** (e.g. Graph500 fixes edge factor 16 and scale = log2 vertices) keeps edges per node constant but not time; PageRank iterations needed for convergence can also vary.

**Conclusion.** The preconditions (a)-(c) from Task 13 are all violated: alpha_eff(P) rises with P, per-core work rate is not constant, balance is data dependent. Use direction-optimizing BFS, vertex delegation, 2D partitioning, asynchronous (non-BSP) methods, graph reordering, and judge scaling with TEPS and traversed-edge throughput per node, not Gustafson's S.
