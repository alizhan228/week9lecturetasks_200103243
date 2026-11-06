# Task 05 - nCUBE/10 and the "Amdahl pessimism" fallacy

**Context.** Amdahl's 1967 argument had been read as "massively parallel machines are futile: with ~10% serial work, speedup <= 10; even 1% gives 100 at most". Sandia National Laboratories (Gustafson, Montry, Benner) built applications on a 1024-node nCUBE/10 hypercube (each node a custom processor with its own small local memory; message passing).


**Why that seemed impossible.** Amdahl with s = 0.4% on P = 1024 gives S = 1/(0.004 + 0.996/1024) = 1/(0.004973) = **201**; even s = 0.1% gives 506. The measured >1000 was 5x above the "ceiling".

**How problem expansion dismantles the ceiling.**
1. They measured the serial fraction on the **1024-processor run** (about 0.4% serial time, i.e. alpha ~ 0.004).
2. Gustafson: S = 1024 - 0.004*1023 = **1019.9**. This matches the measured values.
3. The one-processor equivalent of the scaled problem would have had serial fraction ~ 0.004/(0.004+0.996*1024) ~ 4e-6, so Amdahl's own formula with that fraction gives ~1020 as well (Task 03).
4. Physically: the serial portion (setup, I/O, host communication) was nearly independent of grid size while the computation scaled with the grid - they used the memory and the time budget of the larger machine to refine the mesh.

**Lessons/limits.** Speedup was *scaled* speedup: it measures more work per unit time and not a faster solution to the original problem. The 1-processor baseline was extrapolated, since the scaled problem would not fit in one node's memory. The result mattered because it removed the argument that large parallel machines are useless for scientific computing.
