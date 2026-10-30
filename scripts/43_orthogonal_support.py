#!/usr/bin/env python
"""43_orthogonal_support.py -- M6 step 4: orthogonal support (DESIGN.md v2.3 §5.3-§5.4; DEVIATIONS.md 2026-10-29
interpretation row and M6 support/tiers row) for the §5 scope: U genes with in-support p_cal >= 0.3, plus the top 40
of the preliminary §6.1 ranking (scripts/m6_common.pool_table / rank_pool on scripts 41-42 outputs, before support),
plus equal-size sets of matched-gene predictions (first match of M(g) not annotated to the term, tested with g's
term) and decoy predictions (g tested with another U gene's top term of the same family, size-matched, not related,
member Jaccard < 0.1; seed 0) to estimate the empirical false-support rate of the full rule.

Support test: src/support.py on the admitted independent sources (P_group = BioPlex/OpenCell/BioGRID LTP/STRING
experiments union, Human Cell Map SAINT, ProteomeHD, CCLE proteomics, three Perturb-seq screens, Burke 2023 AF2, HPA);
members = scorable genes annotated to the called V2 term (current), excluding the tested gene; 1,000 degree-matched
null sets; Simes within class, Holm across classes (alpha 0.05). Contradiction: the four named high-reliability
localisation sources (HPA-only contradiction also reported). Diagnostic class by family (§5.4).
Script 44 adds rows for later top-40 entrants with the same function (support_for).
Outputs: results/ledger/support.tsv, support_sources.tsv, support_summary.json, prelim_top40.tsv, 43_manifest.json.
Run: .env/bin/python -I scripts/43_orthogonal_support.py   (after scripts/41, 42)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
gate = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402

log = C.log
PB = C.fz("orthogonal", "scope_min_pcal")
NTOP = C.fz("orthogonal", "scope_top_n")

base = B.Base()
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
P = M6.read_tsv("u_predictions.tsv")
PC = M6.read_tsv("u_pcal.tsv")
FL = M6.read_tsv("u_flags.tsv")

d = M6.pool_table(PC, FL)
pre = M6.rank_pool(d, NTOP)
pre.to_csv(M6.OUT / "prelim_top40.tsv", sep="\t", index=False, float_format="%.6g")
scope_p = PC[(PC.p_cal >= PB)].hgnc_id.tolist()
anchors = list(dict.fromkeys(pre.hgnc_id.tolist() + sorted(scope_p)))
log(f"support scope: {len(scope_p)} genes with p_cal >= {PB}; preliminary top {NTOP}; {len(anchors)} anchors")

runner = M6.SupportRunner()
cands = M6.decoy_candidates(P, v2)
Pi = P.set_index("hgnc_id")
rows = []
t = time.perf_counter()
for h in anchors:
    r = Pi.loc[h]
    rows += M6.support_for(dict(hgnc_id=h, symbol=r.symbol, pos=int(r.matrix_index), term=r.top_term,
                                family=r.family), runner, v2, base, cands, base.onto)
runner.save()
log(f"support for {len(rows)} predictions in {time.perf_counter() - t:.0f} s")
ST = pd.DataFrame(rows)
ST["scope"] = np.where(ST.anchor_hgnc_id.isin(pre.hgnc_id), "prelim_top40", "pcal_ge_0.3")
ST.to_csv(M6.OUT / "support.tsv", sep="\t", index=False, float_format="%.6g")
M6.source_rows(runner, rows).to_csv(M6.OUT / "support_sources.tsv", sep="\t", index=False, float_format="%.6g")


def rates(x):
    return dict(n=len(x), passes_rule=float(x.diag_ok.mean()) if len(x) else np.nan,
                strict_diag_support=float(x.strict.mean()) if len(x) else np.nan,
                any_class_support=float(x.any_support.mean()) if len(x) else np.nan,
                contradiction=float(x.contradiction.mean()) if len(x) else np.nan,
                diag_measured=float(x.diag_measured.mean()) if len(x) else np.nan)


SUMM = {k: rates(ST[ST.set == k]) for k in ("real", "matched", "decoy")}
SUMM["n_anchors"] = len(anchors)
SUMM["n_scope_pcal_ge_0.3"] = len(scope_p)
M6.jdump(SUMM, M6.OUT / "support_summary.json")
C.write_manifest(M6.OUT / "43_manifest.json", "scripts/43_orthogonal_support.py", gate,
                 ["results/ledger/u_predictions.tsv", "results/ledger/u_pcal.tsv", "results/ledger/u_flags.tsv",
                  "results/orthogonal/admission.tsv"], seed=0, t0=T_START, extra=SUMM)
log(f"done: {SUMM}")
