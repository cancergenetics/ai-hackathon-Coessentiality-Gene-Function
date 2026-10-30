#!/usr/bin/env python
"""42_artefact_flags.py -- M6 step 3: DESIGN.md v2.3 §4.3 artefact flags for every reported U prediction
(operationalisation: DEVIATIONS.md 2026-10-29 '§4.3 artefact flags' row).

Supporting partners of a prediction = j in N(g) (K = 25) with z > 0 that are members of the V2 top term under g's
per-query removals (exactly the partners that make up S(g,t)).
* locus: partner gene body overlapping / within 1 kb (gap < 1 kb) of g's or another supporting partner's gene body
  (Ensembl 116 coordinates, strand-agnostic proxy for bidirectional/overlapping loci), or HGNC locus_type readthrough;
* CN co-amplification: Pearson r(g's Chronos effect, partner's OmicsCNGeneWGS) over shared lines (>= 20) > 0.3;
* hub: partner in the top 1% of in-degree of the K-NN graph (tool-background genes); hub-driven prediction = > 50% of
  S(g,t) from hub partners.
Exclusion (not Tier A): partners carrying any flag >= half of the supporting partners, or hub-driven.
Outputs: results/ledger/u_flags.tsv (per gene), u_flag_partners.tsv (per supporting partner), 42_manifest.json.
Run: .env/bin/python -I scripts/42_artefact_flags.py   (after scripts/40)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
gate = C.gate_check(data_files=(C.EFFECT_CSV, "data/raw/depmap/OmicsCNGeneWGS.csv"))
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import ledger as LG  # noqa: E402

log = C.log
K = B.K
WIN = C.fz("artefacts", "bidirectional_tss_max_bp")
RCN = C.fz("artefacts", "cn_coamplification_pearson_r")
HUBS = C.fz("artefacts", "hub_s_fraction")
FRAC = C.fz("artefacts", "flag_fraction_blocks_tier_a")
MIN_LINES = 20

base = B.Base()
gt = base.gt
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
D = pd.read_pickle(M6.DER / "u_scores.pkl")
P = M6.read_tsv("u_predictions.tsv")
hub, coord = D["hub"], D["coord"]
hg = pd.read_csv(C.ROOT / M5.HGNC, sep="\t", dtype=str, usecols=["hgnc_id", "locus_type"])
readthrough = {base.pos[h] for h in hg[hg.locus_type == "readthrough"].hgnc_id if h in base.pos}
log(f"readthrough genes in the matrix: {len(readthrough)}")

effect = C.load_effect()
E = effect.values
cn_df = M6.default_entry("data/raw/depmap/OmicsCNGeneWGS.csv") if not (M6.DER / "cn_wgs.npy").exists() else None
CN, cn_rows = M6.omics_by_position(cn_df if cn_df is not None else pd.DataFrame(), gt, cache="cn_wgs")
del cn_df
lines = [x for x in effect.index if x in set(cn_rows)]
ei = effect.index.get_indexer(lines)
ci = pd.Index(cn_rows).get_indexer(lines)
Esub, CNsub = E[ei], CN[ci]
log(f"CN: {CN.shape}; shared lines with the effect matrix: {len(lines)}; genes with CN: "
    f"{int(np.isfinite(CN).any(0).sum())}")

rows, prow = [], []
ranked = D["ranked2"]
for r in P[P.has_prediction.astype(bool)].itertuples():
    g = int(r.matrix_index)
    col = ranked[g][0]
    sup = M6.supporting(v2, g, col, base.ids100[g, :K], base.z100[g, :K])
    js = [j for j, _ in sup]
    zs = np.array([z for _, z in sup])
    lf = LG.locus_flags(coord.get(g), {j: coord.get(j) for j in js}, window=WIN, readthrough=readthrough)
    rcn = LG.pearson_pairwise(Esub[:, g], CNsub[:, js], min_n=MIN_LINES) if js else np.array([])
    cnf = np.nan_to_num(rcn, nan=-np.inf) > RCN
    hb = hub[js] if js else np.array([], bool)
    share = LG.hub_share(zs, hb)
    hub_driven = bool(np.isfinite(share) and share > HUBS)
    F = pd.DataFrame(dict(locus=[lf[j] for j in js], cn=cnf, hub=hb))
    excl, ffrac = LG.exclusion_43(F, hub_driven, FRAC)
    for k, j in enumerate(js):
        prow.append(dict(hgnc_id=r.hgnc_id, symbol=r.symbol, partner_hgnc_id=gt.hgnc_id.values[j],
                         partner_symbol=gt.symbol.values[j], z=zs[k], locus_flag=lf[j], cn_r=rcn[k], cn_flag=bool(cnf[k]),
                         hub_flag=bool(hb[k]), any_flag=bool(lf[j] or cnf[k] or hb[k])))
    rows.append(dict(hgnc_id=r.hgnc_id, symbol=r.symbol, top_term=r.top_term, n_supporting=len(js),
                     n_locus=int(sum(lf.values())), n_cn=int(cnf.sum()), n_cn_measured=int(np.isfinite(rcn).sum()),
                     n_hub=int(hb.sum()), hub_share=share, hub_driven=hub_driven, frac_any_flag=ffrac,
                     excl43=excl,
                     flagged_partners="|".join(gt.symbol.values[j] for k, j in enumerate(js)
                                               if lf[j] or cnf[k] or hb[k])))
FL = pd.DataFrame(rows)
FP = pd.DataFrame(prow)
FL.to_csv(M6.OUT / "u_flags.tsv", sep="\t", index=False, float_format="%.6g")
FP.to_csv(M6.OUT / "u_flag_partners.tsv", sep="\t", index=False, float_format="%.6g")
summ = dict(n_predictions=len(FL), n_excluded=int(FL.excl43.sum()), n_hub_driven=int(FL.hub_driven.sum()),
            n_with_locus_flag=int((FL.n_locus > 0).sum()), n_with_cn_flag=int((FL.n_cn > 0).sum()),
            n_with_hub_partner=int((FL.n_hub > 0).sum()), n_shared_lines_cn=len(lines),
            partner_flag_rates=dict(locus=float(FP.locus_flag.mean()), cn=float(FP.cn_flag.mean()),
                                    hub=float(FP.hub_flag.mean())))
C.write_manifest(M6.OUT / "42_manifest.json", "scripts/42_artefact_flags.py", gate,
                 ["results/ledger/u_predictions.tsv", "data/raw/depmap/OmicsCNGeneWGS.csv",
                  "data/raw/ensembl/ensembl116_gene_coordinates.tsv", M5.HGNC], seed=0, t0=T_START, extra=summ)
log(f"done: {summ}")
