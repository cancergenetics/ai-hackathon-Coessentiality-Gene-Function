"""Freeze-time power simulation for the primary hold-out comparison (DESIGN §3.5, O7).

Uses only the annotation-derived hold-out H (results/holdout/H_genes.tsv) and its PMID clusters; no DepMap data.
Model: paired binary hit@1 for method A (zavg_BEF) and comparator B. Baseline hit rate pB; A = B + delta on average.
Within-cluster correlation is induced by a shared cluster-level latent (probit scale, intra-cluster correlation rho).
Decision rule as pre-specified: paired cluster bootstrap percentile 95% CI of mean(A - B) excludes 0.
Output: results/holdout/power_sim.md
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
SEED = 0
N_SIM = 400
N_BOOT = 1000          # reduced from the analysis' 10,000 for simulation speed (percentile CI is stable at 1,000)


def simulate_once(rng, clusters, pB, delta, rho):
    n_cl = clusters.max() + 1
    u = rng.normal(size=n_cl)[clusters]                      # shared cluster latent
    eA, eB = rng.normal(size=(2, len(clusters)))
    s = np.sqrt(rho)
    latB = s * u + np.sqrt(1 - rho) * eB
    latA = s * u + np.sqrt(1 - rho) * eA
    hitB = latB < norm.ppf(pB)
    hitA = latA < norm.ppf(pB + delta)
    return hitA.astype(float) - hitB.astype(float)


def cluster_boot_ci(diff, clusters, rng):
    n_cl = clusters.max() + 1
    sums = np.bincount(clusters, weights=diff, minlength=n_cl)
    cnts = np.bincount(clusters, minlength=n_cl)
    idx = rng.integers(0, n_cl, size=(N_BOOT, n_cl))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return np.percentile(means, [2.5, 97.5])


def main():
    H = pd.read_csv(ROOT / "results/holdout/H_genes.tsv", sep="\t")
    clusters = pd.factorize(H["pmid_cluster"])[0]
    rng = np.random.default_rng(SEED)
    rows = []
    for pB in (0.05, 0.15):
        for rho in (0.2, 0.5):
            for delta in (0.02, 0.04, 0.06, 0.08):
                wins = 0
                for _ in range(N_SIM):
                    d = simulate_once(rng, clusters, pB, delta, rho)
                    lo, _hi = cluster_boot_ci(d, clusters, rng)
                    wins += lo > 0
                rows.append(dict(pB=pB, rho=rho, delta=delta, power=wins / N_SIM))
    res = pd.DataFrame(rows)
    out = ROOT / "results/holdout/power_sim.md"
    lines = ["# Power simulation for the primary hold-out comparison (freeze-time, annotation only)", "",
             f"|H| = {len(H)}, PMID clusters = {clusters.max() + 1}; seed {SEED}; {N_SIM} simulations x {N_BOOT} "
             "cluster-bootstrap replicates; decision = percentile 95% CI of mean paired difference excludes 0.",
             "Outcomes independent between methods given the cluster latent (conservative: real methods share "
             "neighbourhoods, which increases concordance and power).", "",
             "| baseline hit@1 (comparator) | intra-cluster rho | true difference | power |", "|---|---|---|---|"]
    lines += [f"| {r.pB:.2f} | {r.rho:.1f} | {r.delta:.2f} | {r.power:.2f} |" for r in res.itertuples()]
    mde = res[res.power >= 0.8].groupby(["pB", "rho"])["delta"].min()
    lines += ["", "Minimum simulated difference with power >= 0.80, by (baseline, rho):", ""]
    lines += [f"- baseline {k[0]:.2f}, rho {k[1]:.1f}: {v:.2f}" for k, v in mde.items()]
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
