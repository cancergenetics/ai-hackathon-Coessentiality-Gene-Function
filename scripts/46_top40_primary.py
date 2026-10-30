"""Primary top 40 under the low-yield branch (PI decision, DEVIATIONS 2026-10-30).

No U gene reaches Tier A or B (max p_cal 0.141), so the frozen fill key (DESIGN §0, §6.1: Tier A -> Tier B -> p_cal) reduces
to p_cal order. Top-40-only check failures (lineage leave-out, DEMETER2, TP53) are tier caps ("Tier B at best") and are
inert when no gene is tiered: they are carried as labels. Built-in artefact exclusions (§4.3) and contradictions (§5.3)
remain exclusions. Mitochondrial-family calls <= 6 of the top 20 (§6.1).

Pool: scorable U genes with a prediction, expressed (DESIGN definition), assessable, p_cal in support.
Inputs: results/ledger/tiers_all.tsv, results/ledger/checks_all_evaluated.tsv (labels).
Output: results/ledger/top40_primary.tsv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "results/ledger"


def as_bool(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def main():
    t = pd.read_csv(L / "tiers_all.tsv", sep="\t")
    pool = t[as_bool(t.has_prediction) & as_bool(t.expressed_design) & as_bool(t.assessable_design)
             & (t.support_category == "in_support")].copy()
    pool["excluded"] = as_bool(pool.excl43) | as_bool(pool.contradiction)
    elig = pool[~pool.excluded].sort_values(["p_cal", "symbol"], ascending=[False, True])
    top, n_mito20 = [], 0
    for r in elig.itertuples():
        if len(top) < 20 and r.family == "mitochondrial":
            if n_mito20 >= 6:
                continue
            n_mito20 += 1
        top.append(r.Index)
        if len(top) == 40:
            break
    out = elig.loc[top].reset_index(drop=True)
    out.insert(0, "rank", range(1, len(out) + 1))
    chk = pd.read_csv(L / "checks_all_evaluated.tsv", sep="\t")
    keep = [c for c in chk.columns if c not in out.columns or c == "hgnc_id"]
    out = out.merge(chk[keep], on="hgnc_id", how="left")
    out.to_csv(L / "top40_primary.tsv", sep="\t", index=False)
    print(f"pool {len(pool)}, excluded (§4.3/contradiction) {int(pool.excluded.sum())}, eligible {len(elig)}")
    print(out[["rank", "symbol", "top_term_name", "family", "p_cal"]].to_string(index=False))


if __name__ == "__main__":
    main()
