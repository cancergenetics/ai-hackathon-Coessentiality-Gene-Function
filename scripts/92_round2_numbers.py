#!/usr/bin/env python3
"""92_round2_numbers.py -- derived numbers requested in manuscript review round 2 [post-review exploratory].

Reads only U-side and judging files (no hold-out outcome is read):
  results/assessability/assessability_U.tsv            (A6 with the 1/(1 - alpha) correction; stats referee M4)
  results/ledger/top40_primary.tsv, results/ledger/top40.tsv, results/revision/a5_judging_per_gene.tsv
                                                       (support among genes shared with the clean-first list; stats S5)
  results/revision/a5_judging_per_gene.tsv             (Wilson CIs for N1 accuracy; stats S4)
  results/ledger/pcal_summary.json, results/revision/a3_pcal_conditional.md
                                                       (survivor-hazard rescaling of Sigma p_cal; stats S1; arithmetic only)
Writes:
  results/revision/a10_assessability_excess_and_implied.tsv
  results/revision/a10_round2_numbers.tsv
Run: .env/bin/python -I scripts/92_round2_numbers.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta as Beta

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "results/revision"
SEED, NS, NU = 0, 100_000, 4924


def read(p):
    return pd.read_csv(ROOT / p, sep="\t")


def as_bool(s):
    return s.astype(str).str.lower().isin(["true", "1"])


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


rows = []

# ---------------------------------------------------------------- A6 corrected (stats M4)
A = read("results/assessability/assessability_U.tsv")
for c in ("scorable", "expressed", "clean_negative", "p_lt_alpha", "assessable", "expressed_design",
          "assessable_design", "any_dependency"):
    A[c] = as_bool(A[c])
sc = A[A.scorable]
cn = sc[sc.clean_negative]
rng = np.random.default_rng(SEED)
out = []
for strat in ("any_dependency", "sd_tertile_withinU"):
    for expcol, acol, lab in (("expressed", "assessable", "frozen expressed (635)"),
                              ("expressed_design", "assessable_design", "DESIGN expressed (646)")):
        ex = sc[sc[expcol]]
        obs = 0
        exc_pt = imp_pt = 0.0
        exc_d = np.zeros(NS)
        imp_d = np.zeros(NS)
        for lev, d in ex.groupby(strat):
            c = cn[cn[strat] == lev]
            k, n = int(c.p_lt_alpha.sum()), len(c)
            ne, no = len(d), int(d[acol].sum())
            a = k / n
            ad = Beta(k + 0.5, n - k + 0.5).rvs(NS, random_state=rng)
            fd = rng.binomial(ne, ad)
            obs += no
            exc_pt += no - ne * a
            imp_pt += (no - ne * a) / (1 - a)
            exc_d += no - fd
            imp_d += (no - fd) / (1 - ad)
        out.append(dict(stratifier=strat, expression=lab, observed=obs,
                        excess_calls_over_null=exc_pt, excess_lo=np.quantile(exc_d, .025),
                        excess_hi=np.quantile(exc_d, .975),
                        implied_true_full_power=imp_pt, implied_lo=np.quantile(imp_d, .025),
                        implied_hi=np.quantile(imp_d, .975), implied_frac_U=imp_pt / NU,
                        implied_frac_U_lo=np.quantile(imp_d, .025) / NU,
                        implied_frac_U_hi=np.quantile(imp_d, .975) / NU))
T = pd.DataFrame(out)
f_t = "results/revision/a10_assessability_excess_and_implied.tsv"
T.to_csv(ROOT / f_t, sep="\t", index=False)
for r in T.itertuples():
    rows.append((f"{r.stratifier}, {r.expression}: excess of assessable calls over null expectation (95% int.)",
                 f"{r.excess_calls_over_null:.0f} ({r.excess_lo:.0f}–{r.excess_hi:.0f})", f_t))
    rows.append((f"{r.stratifier}, {r.expression}: implied genes with real signal at full power, "
                 f"(obs - N alpha)/(1 - alpha) per stratum (95% int.); % of U",
                 f"{r.implied_true_full_power:.0f} ({r.implied_lo:.0f}–{r.implied_hi:.0f}); "
                 f"{100 * r.implied_frac_U:.1f}% ({100 * r.implied_frac_U_lo:.1f}–{100 * r.implied_frac_U_hi:.1f}%)", f_t))

# ---------------------------------------------------------------- support among shared genes (stats S5)
P = read("results/ledger/top40_primary.tsv")
C = read("results/ledger/top40.tsv")
J = read("results/revision/a5_judging_per_gene.tsv")
J = J[J.set == "top40"].copy()
shared = set(P.symbol) & set(C.symbol)
J["shared"] = J.symbol.isin(shared)
f_j = "results/revision/a5_judging_per_gene.tsv"
for sh, lab in ((True, "shared with the clean-first list"), (False, "not shared with the clean-first list")):
    d = J[J.shared == sh]
    rows.append((f"top-40 genes {lab}: n; supported (primary); supported on term only",
                 f"{len(d)}; {(d.real == 1).sum()}; {(d.real_term == 1).sum()}", f_j))

# ---------------------------------------------------------------- N1 accuracy CIs (stats S4)
F = read("results/revision/a1_U_entry_flags.tsv")
n1 = set(F[(F.in_top40.astype(str) == "True") & (F.L_class == "N1")].symbol)
d = J[J.symbol.isin(n1)]
k, kt, n = int((d.real == 1).sum()), int((d.real_term == 1).sum()), len(d)
lo, hi = wilson(k, n)
lot, hit = wilson(kt, n)
rows.append(("top-40 N1 genes: supported (primary), Wilson 95% CI",
             f"{k}/{n} = {100 * k / n:.0f}% ({100 * lo:.0f}–{100 * hi:.0f}%)", f_j))
rows.append(("top-40 N1 genes: supported on term only, Wilson 95% CI",
             f"{kt}/{n} = {100 * kt / n:.0f}% ({100 * lot:.0f}–{100 * hit:.0f}%); module-only: "
             + ", ".join(sorted(d[(d.real == 1) & (d.real_term != 1)].symbol)), f_j))

# ---------------------------------------------------------------- survivor-hazard rescaling (stats S1)
S = json.loads((ROOT / "results/ledger/pcal_summary.json").read_text())
sig = float(S["sum_pcal_in_support"])
r_surv = 0.145  # results/revision/a3_pcal_conditional.md, survivors row, p over 7.88 y at constant hazard 0.01988
rows.append(("unconditional Sigma p_cal with the 2018->2022 survivor hazard (0.145 over 7.88 y)",
             f"{sig:.1f} x 0.145 = {sig * r_surv:.1f}", "results/ledger/pcal_summary.json; results/revision/a3_pcal_conditional.md"))

R = pd.DataFrame(rows, columns=["key", "value", "file"])
R.to_csv(RV / "a10_round2_numbers.tsv", sep="\t", index=False)
print(R.to_string())
print(T.to_string())
