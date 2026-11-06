# Task 13 - Where Gustafson's weak-scaling premise breaks

Gustafson needs (a) serial work independent of problem size, (b) parallel work scalable so that per-processor time is constant, (c) no overhead growing with P.

## Case 1 - Conjugate-gradient/Krylov solvers for elliptic PDEs (iteration count grows with N)
Poisson on an N^3 grid: condition number kappa ~ N^2, CG iterations ~ sqrt(kappa) ~ N. Weak scaling keeps points per processor fixed, so N ~ P^(1/3), and **iterations grow ~P^(1/3)**. Per-iteration time is constant (stencil + O(log P) dot-product reductions), so total time T ~ P^(1/3) log P: the **fixed-time premise fails** because problem growth changes the algorithmic time complexity (work ~ N^4 rather than N^3). At P = 4096, N grows 16x, iterations 16x. Scaled speedup computed as P*T(1)/T(P) collapses to P^(2/3). The fixes are algorithmic (multigrid/preconditioning gives iteration count O(1)), not parallel.

## Case 2 - 3D FFT / global transposes / parallel sorting (all-to-all)
Each step performs an all-to-all exchange: each rank sends ~n^3 data, but on a 3D torus the bisection bandwidth per node falls as P^(-1/3). Communication time per node grows ~P^(1/3) (and message-startup counts grow as P) even though local data n^3 is fixed. The compute is O(n^3 log N), which grows only logarithmically, so alpha_eff(P) -> 1 and E -> 0. Contention on shared links is the cause. Gustafson's assumption (c) fails.

## Other examples
Branch-and-bound with unpredictable pruning; dense LU with pivoting (global pivot reductions); algorithms with a sequential bottleneck proportional to N (e.g., serial output of N results: serial time grows with the problem size, so alpha is not constant).

**General diagnosis.** Check: (1) does time per unit of the scaled problem stay constant on one core? (2) does any term grow with P (latency, contention, load imbalance)? (3) does the memory footprint per node stay within the cap? A negative answer to any means Gustafson overestimates.
