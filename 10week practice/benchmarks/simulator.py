#!/usr/bin/env python3
"""Task 21: Amdahl vs Gustafson simulator.
Usage: python3 simulator.py --alphas 0.001 0.01 0.05 0.2 --out ../plots/simulator_overlay.png
Writes CSV (benchmarks/simulator_output.csv by default) and an overlay plot."""
import argparse, csv, os
import numpy as np

def amdahl(P, s):    return 1.0 / (s + (1.0 - s) / P)
def gustafson(P, a): return P - a * (P - 1.0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmin", type=int, default=1)
    ap.add_argument("--pmax", type=int, default=65536)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.001, 0.01, 0.04, 0.08, 0.20])
    ap.add_argument("--csv", default=os.path.join(os.path.dirname(__file__), "simulator_output.csv"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "plots", "simulator_overlay.png"))
    a = ap.parse_args()
    if not (1 <= a.pmin <= a.pmax <= 65536): ap.error("need 1 <= pmin <= pmax <= 65536")
    for x in a.alphas:
        if not (0.001 <= x <= 0.20): ap.error(f"alpha {x} outside [0.001, 0.20]")
    Ps = np.unique(np.round(2 ** np.linspace(np.log2(a.pmin), np.log2(a.pmax), 200)).astype(int))
    rows = []
    for al in a.alphas:
        for P in Ps:
            sg, sa = gustafson(P, al), amdahl(P, al)
            rows.append((al, int(P), sa, sg, sa / P, sg / P))
    with open(a.csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["alpha", "P", "S_amdahl", "S_gustafson", "E_amdahl", "E_gustafson"])
        w.writerows(rows)
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for al in a.alphas:
        sub = [r for r in rows if r[0] == al]
        p = [r[1] for r in sub]
        l, = ax[0].plot(p, [r[3] for r in sub], label=f"Gustafson a={al}")
        ax[0].plot(p, [r[2] for r in sub], "--", color=l.get_color(), label=f"Amdahl s={al}")
        ax[1].plot(p, [r[5] for r in sub], color=l.get_color(), label=f"Gustafson a={al}")
        ax[1].plot(p, [r[4] for r in sub], "--", color=l.get_color())
    ax[0].plot(Ps, Ps, "k:", label="ideal")
    ax[0].set(xscale="log", yscale="log", xlabel="P", ylabel="Speedup", title="Strong (Amdahl) vs weak (Gustafson)")
    ax[1].set(xscale="log", xlabel="P", ylabel="Efficiency", title="Parallel efficiency (solid=Gustafson, dashed=Amdahl)", ylim=(0, 1.02))
    ax[0].legend(fontsize=6, ncol=2); ax[0].grid(alpha=.3); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(a.out, dpi=200)
    print(f"wrote {a.csv} ({len(rows)} rows) and {a.out}")

if __name__ == "__main__":
    main()
