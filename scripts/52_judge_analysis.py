"""Blinded literature judging: validation check and primary analysis (DESIGN §6.4).

Inputs: results/m7/judge/scores/{J1,J2}_<batch>.tsv (packet_id, slot, score, justification),
optional results/m7/judge/scores/ADJ_<batch>.tsv (adjudicated rows for disagreements: packet_id, slot, score, ...),
results/m7/judge/packet_key.tsv, results/m7/answer_key.tsv, results/m7/L/index_batch_*.tsv (novelty class).

Mode `hval`: judge validation on the 10 hold-out genes. Accept iff >= 7/10 real statements supported (+1) and
<= 3/30 decoys supported, using adjudicated scores (agreement rows + adjudications).
Mode `main`: per gene, d = real score - mean(decoy scores); primary = exact one-sided sign-flip test (full enumeration
of the 2^n sign patterns over genes with d != 0) for the primary top 40; S20 and extra30 analysed separately; by
novelty class. Cohen's kappa between J1 and J2 (3-class) reported.
Outputs: results/m7/judge/analysis_<mode>.md and per-gene TSV.
"""
import glob
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
J = ROOT / "results/m7/judge"


def load_scores(batches):
    out = {}
    for judge in ("J1", "J2", "ADJ"):
        fr = [pd.read_csv(f, sep="\t") for b in batches for f in glob.glob(str(J / f"scores/{judge}_{b}.tsv"))]
        if fr:
            d = pd.concat(fr)
            d["score"] = d["score"].astype(int)
            out[judge] = d.set_index(["packet_id", "slot"])["score"]
    return out


def kappa(a, b):
    cats = [-1, 0, 1]
    n = len(a)
    po = np.mean(a == b)
    pe = sum((np.sum(a == c) / n) * (np.sum(b == c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def signflip_p(d):
    d = np.asarray([x for x in d if x != 0], float)
    n = len(d)
    if n == 0:
        return 1.0, 0
    obs = d.sum()
    if n <= 22:
        cnt = sum(1 for s in itertools.product((1, -1), repeat=n) if np.dot(s, np.abs(d)) >= obs - 1e-12)
        return cnt / 2 ** n, n
    rng = np.random.default_rng(0)
    sims = (rng.choice((1, -1), size=(200_000, n)) * np.abs(d)).sum(1)
    return (1 + np.sum(sims >= obs - 1e-12)) / 200_001, n


def main(mode):
    batches = ["hval"] if mode == "hval" else ["main1", "main2", "main3"]
    S = load_scores(batches)
    j1, j2 = S["J1"], S["J2"]
    idx = j1.index.intersection(j2.index)
    k = kappa(j1[idx].values, j2[idx].values)
    final = j1[idx].where(j1[idx] == j2[idx])
    if "ADJ" in S:
        adj = S["ADJ"].reindex(idx)
        final = final.fillna(adj)
    n_unres = int(final.isna().sum())
    pk = pd.read_csv(J / "packet_key.tsv", sep="\t")
    ak = pd.read_csv(ROOT / "results/m7/answer_key.tsv", sep="\t")
    key = pk.merge(ak[["hgnc_id", "symbol", "real_slot", "rank_in_set"]], on="hgnc_id")
    rows = []
    for r in key.itertuples():
        if r.J_id not in final.index.get_level_values(0):
            continue
        sc = {s: final.get((r.J_id, s), np.nan) for s in "ABCD"}
        real = sc[r.real_slot]
        dec = [v for s, v in sc.items() if s != r.real_slot]
        rows.append(dict(J_id=r.J_id, hgnc_id=r.hgnc_id, symbol=r.symbol, set=r.set, rank=r.rank_in_set,
                         real=real, decoy_mean=np.nanmean(dec), n_decoy_supported=int(np.sum(np.array(dec) == 1)),
                         d=real - np.nanmean(dec)))
    G = pd.DataFrame(rows)
    Lx = pd.concat([pd.read_csv(f, sep="\t", header=None) for f in glob.glob(str(ROOT / "results/m7/L/index_batch_*.tsv"))])
    G = G.merge(Lx.iloc[:, [0, 2]].set_axis(["hgnc_id", "nclass"], axis=1), on="hgnc_id", how="left")
    G.to_csv(J / f"analysis_{mode}_genes.tsv", sep="\t", index=False)
    L = [f"# Blinded judging — {mode}", "", f"Judge agreement: Cohen's kappa = {k:.3f} over {len(idx)} statements; "
         f"disagreements {int((j1[idx] != j2[idx]).sum())}; unresolved after adjudication {n_unres}.", ""]
    if mode == "hval":
        nreal = int((G.real == 1).sum()); ndec = int(G.n_decoy_supported.sum())
        ok = nreal >= 7 and ndec <= 3
        L += [f"Real (known target term) supported: {nreal}/{len(G)}; decoys supported: {ndec}/{3 * len(G)}.",
              f"**Validation {'PASSED' if ok else 'FAILED'}** (accept: >= 7/10 real and <= 3/30 decoys)."]
    else:
        for s in ["top40", "s20", "extra30"]:
            g = G[G.set == s]
            p, n = signflip_p(g.d.values)
            L += [f"## {s} (n = {len(g)})", "",
                  f"- real supported {int((g.real == 1).sum())}, unaddressed {int((g.real == 0).sum())}, contradicted "
                  f"{int((g.real == -1).sum())}; decoys supported {int(g.n_decoy_supported.sum())}/{3 * len(g)}",
                  f"- mean d = real − mean(decoys) = {g.d.mean():.3f}; exact one-sided sign-flip p = {p:.4g} "
                  f"(n non-zero = {n}){'  ← PRIMARY' if s == 'top40' else ''}", ""]
            for c, gc in g.groupby("nclass"):
                L.append(f"  - {c}: n {len(gc)}, real supported {int((gc.real == 1).sum())}, mean d {gc.d.mean():.3f}")
            L.append("")
    (J / f"analysis_{mode}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hval")
