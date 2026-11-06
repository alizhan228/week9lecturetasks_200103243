# Weak-scaling benchmark (Task 22)
```
g++ -O3 -march=native -fopenmp weak_scale_bench.cpp -o weak_scale_bench
./weak_scale_bench 5 200000000 8000000 > ../results.csv                  # threads 1,2,4,..,hw max
./weak_scale_bench 5 200000000 8000000 16 1 2 4 8 16 > ../results.csv    # explicit thread list
```
Args: reps, k (iterations per thread), serial_iters, max_threads, optional explicit thread list.
Pin threads for clean results: `OMP_PROC_BIND=close OMP_PLACES=cores`.
Then: `python3 ../fit_gustafson.py`.
