#!/usr/bin/env python3
"""Task 23/24: mean/std per thread count, least-squares fit of alpha, plots.
Weak-scaling scaled speedup: S(P) = P * T(1) / T(P)  (work grows P-fold, time should stay constant).
Gustafson: S = P - alpha(P-1)  =>  (P - S) = alpha (P-1); LSQ through the origin:
alpha = sum((P-1)(P-S)) / sum((P-1)^2)."""
import csv, os, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "results.csv")
data = {}
for r in csv.DictReader(open(src)):
    data.setdefault(int(r["threads"]), []).append(float(r["time_s"]))
Ps = np.array(sorted(data)); mean = np.array([np.mean(data[p]) for p in Ps])
std = np.array([np.std(data[p], ddof=1) if len(data[p]) > 1 else 0 for p in Ps]); n = np.array([len(data[p]) for p in Ps])
S = Ps * mean[0] / mean
relerr = np.sqrt((std / mean) ** 2 + (std[0] / mean[0]) ** 2)
Serr = S * relerr / np.sqrt(np.maximum(n, 1))   # standard error
m = Ps > 1
alpha = float(np.sum((Ps[m] - 1) * (Ps[m] - S[m])) / np.sum((Ps[m] - 1) ** 2)) if m.any() else float("nan")
print("   P   mean_T   std_T        S    SE(S)      E")
for p, mu, sd, s, e in zip(Ps, mean, std, S, Serr): print(f"{p:4d} {mu:9.4f} {sd:8.4f} {s:8.3f} {e:7.3f} {s/p:6.3f}")
print(f"alpha_observed = {alpha:.5f}")
with open(os.path.join(here, "results_summary.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["P", "mean_T", "std_T", "S", "S_stderr", "E", "alpha_fit"])
    for p, mu, sd, s, e in zip(Ps, mean, std, S, Serr): w.writerow([p, mu, sd, s, e, s / p, alpha])
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
x = np.linspace(1, Ps.max(), 300)
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(x, x, "k:", label="Ideal (linear)")
ax.plot(x, x - alpha * (x - 1), label=f"Gustafson fit (alpha={alpha:.4f})")
ax.plot(x, 1 / (alpha + (1 - alpha) / x), "--", label="Amdahl, same fraction")
ax.errorbar(Ps, S, yerr=Serr, fmt="o", capsize=3, label="Measured (mean, SE)")
ax.set(xlabel="Threads P", ylabel="Scaled speedup", title="Weak scaling: measured vs theory"); ax.grid(alpha=.3); ax.legend()
out = os.path.join(here, "..", "plots", "scaling_comparison")
fig.tight_layout(); fig.savefig(out + ".png", dpi=300); fig.savefig(out + ".pdf")
