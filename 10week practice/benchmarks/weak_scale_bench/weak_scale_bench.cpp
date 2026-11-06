// Task 22: OpenMP weak-scaling benchmark.
// Per-thread work k is constant (midpoint-rule integration of 4/(1+x^2) over [0,1] -> pi).
// Total work = k * P.  A fixed serial section (serial_iters) models the serial fraction alpha.
// Build: g++ -O3 -march=native -fopenmp weak_scale_bench.cpp -o weak_scale_bench
// Run:   ./weak_scale_bench [reps=5] [k] [serial_iters] [max_threads=hw] [t1 t2 ...]
#include <omp.h>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
using namespace std;

static double serial_section(long n) {
    volatile double acc = 0; for (long i = 0; i < n; ++i) acc += sin(i * 1e-6); return acc;
}

int main(int argc, char** argv) {
    int reps = argc > 1 ? atoi(argv[1]) : 5;
    long k = argc > 2 ? atol(argv[2]) : 200000000L;
    long ser = argc > 3 ? atol(argv[3]) : 8000000L;
    int maxT = argc > 4 ? atoi(argv[4]) : omp_get_num_procs();
    vector<int> counts;
    if (argc > 5) for (int i = 5; i < argc; ++i) counts.push_back(atoi(argv[i]));
    else { for (int t = 1; t <= maxT; t *= 2) counts.push_back(t); if (counts.back() != maxT) counts.push_back(maxT); }
    printf("threads,run,time_s,pi\n");
    for (int P : counts) {
        omp_set_num_threads(P);
        for (int r = 0; r < reps; ++r) {
            double t0 = omp_get_wtime();
            serial_section(ser);
            long N = k * P;                      // weak scaling: N grows with P
            double h = 1.0 / N, sum = 0.0;
            #pragma omp parallel for reduction(+:sum) schedule(static)
            for (long i = 0; i < N; ++i) { double x = (i + 0.5) * h; sum += 4.0 / (1.0 + x * x); }
            double pi = sum * h;
            printf("%d,%d,%.6f,%.12f\n", P, r, omp_get_wtime() - t0, pi);
        }
    }
}
