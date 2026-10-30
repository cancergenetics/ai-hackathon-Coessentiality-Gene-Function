#!/usr/bin/env python
"""45_m6_summary.py -- M6 step 6: results/ledger/M6_SUMMARY.md and figure-ready TSVs (results/ledger/figdata/).

Numbers are read from the ledger files of scripts 40-44 (no recomputation of predictions): support categories,
Sigma p_cal with 95% cluster-bootstrap CIs (all U with p_cal in support; boundary upper-bound sum separately; in-support
expressed & assessable; Tier A), Tier A / B counts, empirical false-support rates (matched-gene and decoy predictions),
the clean-negative false-call rate by informativeness tertile (Tier-A-like = in-support p_cal >= 0.5, reproducibility
p < 0.05, no §4.3 exclusion), the top-40 table and the DESIGN §0 decision branch.
Run: .env/bin/python -I scripts/45_m6_summary.py   (after scripts/44)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
gate = C.gate_check()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m6_common as M6  # noqa: E402

OUT, FIG = M6.OUT, M6.FIG
f3 = M6.fmt
PA = C.fz("tiers", "tier_a_pcal_min")
MINA = C.fz("tiers", "min_tier_a_for_paper_lead")
MINASS = C.fz("tiers", "min_assessable_for_tiers")

P = M6.read_tsv("u_predictions.tsv")
PC = M6.read_tsv("u_pcal.tsv")
FL = M6.read_tsv("u_flags.tsv")
ST = M6.read_tsv("support.tsv")
TOP = M6.read_tsv("top40.tsv")
TIERS = M6.read_tsv("tiers_all.tsv")
FILL = M6.read_tsv("top40_fill_log.tsv")
CHK = M6.read_tsv("checks_all_evaluated.tsv")
S41 = json.loads((OUT / "pcal_summary.json").read_text())
M44 = json.loads((OUT / "44_manifest.json").read_text())
M42 = json.loads((OUT / "42_manifest.json").read_text())
M40 = json.loads((OUT / "40_manifest.json").read_text())
MOD = M6.model()
bz = np.load(M6.DER / "pcal_boot.npz", allow_pickle=True)   # own file (scripts/41)
boot, bh, ok = bz["boot"], list(bz["hgnc_id"]), bz["ok"]
col = {h: i for i, h in enumerate(bh)}


def boot_sum(hs):
    idx = [col[h] for h in hs if h in col]
    if not idx:
        return 0.0, [0.0, 0.0], np.zeros(int(ok.sum()))
    s = boot[ok][:, idx].sum(1)
    return None, [float(np.quantile(s, .025)), float(np.quantile(s, .975))], s


# ------------------------------------------------------------------------------------------ sums
tierA = TIERS[TIERS.tier == "A"].hgnc_id.tolist()
tierB = TIERS[TIERS.tier == "B"].hgnc_id.tolist()
ins = PC[PC.support_category == "in_support"]
ub = PC[PC.support_category == "upper_bound"]
ea = PC.expressed_design.astype(bool) & PC.assessable_design.astype(bool)
sums = {}
for name, hs, val in (("in_support_all", ins.hgnc_id, ins.p_cal.sum()),
                      ("upper_bound_all", ub.hgnc_id, ub.p_cal_upper.sum()),
                      ("in_support_expressed_assessable", PC[ea & (PC.support_category == "in_support")].hgnc_id,
                       PC[ea].p_cal.sum()),
                      ("tier_A", tierA, PC[PC.hgnc_id.isin(tierA)].p_cal.sum()),
                      ("top40", TOP.hgnc_id, TOP.p_cal.sum())):
    _, ci, s = boot_sum(list(hs))
    sums[name] = dict(n=len(list(hs)), sum=float(val), ci=ci)
    if name in ("in_support_all", "upper_bound_all"):
        pd.DataFrame({"replicate": np.arange(len(s)), "sum": s}).to_csv(FIG / f"sigma_pcal_boot_{name}.tsv",
                                                                         sep="\t", index=False, float_format="%.6g")
cat = PC.support_category.value_counts().reindex(["in_support", "upper_bound", "no_pcal", "no_prediction"]).fillna(0)
cat_ea = PC[ea].support_category.value_counts().reindex(cat.index).fillna(0)
CAT = pd.DataFrame(dict(category=cat.index, n_scorable_U=cat.values.astype(int),
                        n_expressed_assessable=cat_ea.values.astype(int)))
CAT.to_csv(FIG / "support_category_counts.tsv", sep="\t", index=False)
rs = pd.Series(S41["reasons_no_pcal"]).sort_values(ascending=False)

# ------------------------------------------------------------------------------------------ negative control
cn = PC[PC.clean_negative.astype(bool)].merge(FL[["hgnc_id", "excl43"]], on="hgnc_id", how="left")
cn = cn.merge(P[["hgnc_id", "assessable_p"]], on="hgnc_id", how="left")
cn["excl43"] = cn.excl43.fillna(False).astype(bool)
cn["tierA_like"] = (cn.support_category == "in_support") & (cn.p_cal >= PA) & (cn.assessable_p < 0.05) & ~cn.excl43
cn["tierB_like"] = (cn.support_category == "in_support") & (cn.p_cal >= 0.3) & (cn.assessable_p < 0.05) & ~cn.excl43
ea_g = PC[ea]
nc_rows = []
for lev, d in [("all", cn)] + list(cn.groupby("sd_tertile_withinU")):
    k = int(d.tierA_like.sum())
    lo, hi = (0.0, 1 - 0.05 ** (1 / len(d))) if k == 0 and len(d) else (np.nan, np.nan)
    nc_rows.append(dict(set="clean negative", tertile=lev, n=len(d), n_with_pcal=int(d.p_cal.notna().sum()),
                        p_cal_median=d.p_cal.median(), p_cal_p90=d.p_cal.quantile(.9), p_cal_max=d.p_cal.max(),
                        n_tierA_like=k, rate_tierA_like=k / len(d) if len(d) else np.nan,
                        rate_upper95_if_zero=hi, n_tierB_like=int(d.tierB_like.sum())))
nc_rows.append(dict(set="expressed & assessable (comparison)", tertile="all", n=len(ea_g),
                    n_with_pcal=int(ea_g.p_cal.notna().sum()), p_cal_median=ea_g.p_cal.median(),
                    p_cal_p90=ea_g.p_cal.quantile(.9), p_cal_max=ea_g.p_cal.max(), n_tierA_like=len(tierA),
                    rate_tierA_like=len(tierA) / len(ea_g), rate_upper95_if_zero=np.nan, n_tierB_like=len(tierB)))
NC = pd.DataFrame(nc_rows)
NC.to_csv(OUT / "negative_control.tsv", sep="\t", index=False, float_format="%.6g")
NC.to_csv(FIG / "negative_control.tsv", sep="\t", index=False, float_format="%.6g")

# ------------------------------------------------------------------------------------------ false support
fs_rows = []
for k in ("real", "matched", "decoy"):
    x = ST[ST.set == k]
    fs_rows.append(dict(set=k, n=len(x), passes_tierA_support_rule=x.diag_ok.mean(),
                        strict_diagnostic_support=x.strict.mean(), any_class_support=x.any_support.mean(),
                        contradiction=x.contradiction.mean(), contradiction_hpa_only=x.contradiction_hpa_only.mean(),
                        diagnostic_class_measured=x.diag_measured.mean(),
                        **{f"supports_{c}": (x[f"state_{c}"] == "supports").mean() for c in "PALGS"}))
FS = pd.DataFrame(fs_rows)
FS.to_csv(OUT / "false_support.tsv", sep="\t", index=False, float_format="%.4f")
FS.to_csv(FIG / "false_support_rates.tsv", sep="\t", index=False, float_format="%.4f")

# ------------------------------------------------------------------------------------------ figdata
PC.merge(P[["hgnc_id", "assessable_p", "top_size", "headline_design"]], on="hgnc_id").to_csv(
    FIG / "pcal_all_U.tsv", sep="\t", index=False, float_format="%.6g")
P[P.has_prediction.astype(bool)].family.value_counts().rename_axis("family").reset_index(name="n").to_csv(
    FIG / "family_counts.tsv", sep="\t", index=False)
TOP[["rank", "symbol", "v2_term", "v2_term_name", "v1p_label_name", "family", "p_cal", "tier", "fill_group",
     "supporting_classes", "relationship_type", "flags", "zmean", "cov_pct"]].to_csv(
    FIG / "top40.tsv", sep="\t", index=False, float_format="%.6g")
FL.to_csv(FIG / "artefact_flags.tsv", sep="\t", index=False, float_format="%.6g")

# ------------------------------------------------------------------------------------------ sensitivity fill
from src import ledger as LG  # noqa: E402
sens = TIERS[TIERS["pool"].astype(bool)].copy()
sens["group"] = np.where(sens.tier == "A", 0, np.where(sens.tier == "B", 1, np.where(
    ~sens.excl43.astype(bool) & ~sens.contradiction.astype(bool), 2, 3)))
SENS = LG.fill_top(sens, n=len(TOP), cap_top=20, cap_max=C.fz("tiers", "mito_cap_top20_max_count"))
SENS["in_primary_top40"] = SENS.hgnc_id.isin(TOP.hgnc_id)
SENS["demoted_top40_check"] = SENS.demote_A.astype(bool)
SENS[["rank", "symbol", "hgnc_id", "top_term", "top_term_name", "family", "p_cal", "group", "excl43", "contradiction",
      "demoted_top40_check", "in_primary_top40"]].to_csv(FIG / "top40_sensitivity_no_demotion.tsv", sep="\t",
                                                          index=False, float_format="%.6g")

# ------------------------------------------------------------------------------------------ decision branch
nA, nB = len(tierA), len(tierB)
n_ass = int(ea.sum())
branch = []
branch.append(f"C2 primary passed at M5b -> calibrated claims for U are permitted (p_cal from the pre-specified model).")
if n_ass < MINASS:
    branch.append(f"< {MINASS} U genes scorable, expressed and assessable -> C3 descriptive without tiers.")
else:
    branch.append(f"{n_ass} U genes scorable, expressed and assessable (≥ {MINASS}) -> tiers apply.")
if nA < MINA:
    branch.append(f"**{nA} genes in Tier A (< {MINA}) -> low-yield branch: the paper leads with C1–C2; the top 40 is "
                  f"filled Tier A -> Tier B -> p_cal and labelled by tier. Thresholds are not relaxed.**")
else:
    branch.append(f"{nA} genes in Tier A (≥ {MINA}) -> catalogue-led branch.")

# ------------------------------------------------------------------------------------------ markdown
fl_ex = FL.excl43.astype(bool)
L = ["# M6 — hypothesis generation for the pre-registered uncharacterised genes U: SUMMARY", "",
     f"Generated by scripts/45_m6_summary.py ({time.strftime('%Y-%m-%dT%H:%M:%S')}) from the machine ledger of "
     "scripts 40–44 (DESIGN.md v2.3 §4–§6.1; operational details: DEVIATIONS.md rows dated 2026-10-29, M6). "
     "No narrative or literature was used; no orthogonal evidence was seen before the ledger (u_predictions.tsv, "
     "u_partners.tsv) was written.", "",
     "## Decision branch (DESIGN §0)", ""] + [f"- {b}" for b in branch] + [
     "", "## Census of predictions", "",
     f"- Scorable U genes: {len(P):,}; with a top reportable V2 term (R1, ≥ 2 supporting partners): "
     f"{int(P.has_prediction.sum()):,}; scorable, expressed and assessable (DESIGN definition): {n_ass:,}.",
     f"- Module family of the top term: " + ", ".join(f"{k} {v}" for k, v in
                                                      P[P.has_prediction.astype(bool)].family.value_counts().items()) + ".",
     "", "| support category (§3.7) | scorable U | expressed & assessable |", "|---|---|---|"]
L += [f"| {r.category} | {r.n_scorable_U:,} | {r.n_expressed_assessable:,} |" for r in CAT.itertuples()]
L += ["", "Reasons for no p_cal (a gene can have several): " + "; ".join(f"{k} {v}" for k, v in rs.items()) + ".",
      f"Families with p_cal (≥ 30 H genes): {', '.join(MOD['families_kept'])}; the frozen fit gives "
      f"signalling_lineage a coefficient of {MOD['coef']['fam_signalling_lineage']:+.2f} (no H hits in that family), so "
      "its p_cal values are ≈ 0.",
      "", "## Σ p_cal (expected number of top-term predictions later confirmed by D1-evidence annotation, ~8 years)", "",
      "95% percentile CIs from 2,000 cluster-bootstrap refits of the §3.7 model on H (PMID-only primary clusters, seed 0).",
      "", "| set | n | Σ p_cal | 95% CI |", "|---|---|---|---|"]
lab = dict(in_support_all="all U with p_cal (in support)", upper_bound_all="boundary genes (upper bound; summed separately)",
           in_support_expressed_assessable="in support, expressed & assessable", tier_A="Tier A", top40="top 40")
for k, v in sums.items():
    L.append(f"| {lab[k]} | {v['n']:,} | {v['sum']:.2f} | {v['ci'][0]:.2f}–{v['ci'][1]:.2f} |")
L += ["", f"Largest in-support p_cal: {S41['max_p_cal']:.3f}; largest upper-bound p_cal: "
      f"{S41['max_p_cal_upper']:.3f}. Genes with p_cal ≥ 0.3: {S41['n_pcal_ge_tierB']}; ≥ 0.5: {S41['n_pcal_ge_tierA']}.",
      "", "## Tiers (§6.1)", "",
      f"- **Tier A: {nA}. Tier B: {nB}.** Pool for the p_cal fill (expressed, assessable, in-support p_cal): "
      f"{int(TIERS['pool'].astype(bool).sum()):,}.",
      f"- The frozen calibration model caps in-support p_cal at {S41['max_p_cal']:.3f} for U (top-K mean zavg ≤ H 95th "
      f"percentile {MOD['support']['bounds_5_95']['zmean'][1]:.2f}, coverage percentile ≤ "
      f"{MOD['support']['bounds_5_95']['cov_pct'][1]:.3f}), so no U gene can reach the Tier B threshold (0.3); the top 40 "
      "is the p_cal fill.",
      f"- Top-40 fill converged in {M44['iterations']} iterations; genes evaluated by the top-40 checks: "
      f"{M44['n_checked']} (the whole fill pool); demoted (lineage leave-out / DEMETER2 / TP53; monotone): "
      f"{M44['n_demoted']} (per gene: checks_all_evaluated.tsv). Final top 40: "
      f"{int((TOP.fill_group == 'p_cal fill (clean)').sum())} clean fill genes (the whole clean pool), then "
      f"{int((TOP.fill_group == 'p_cal fill (flagged)').sum())} flagged fill genes by p_cal.",
      f"- Top-40 checks over all {len(CHK)} evaluated pool genes: lineage leave-out top term retained "
      f"{int(CHK.leaveout_retained.astype(bool).sum())}/{len(CHK)}; DEMETER2 measured {int(CHK.d2_measured.astype(bool).sum())}, "
      f"not replicated (flag) {int(CHK.d2_flag.astype(bool).sum())}; TP53 nominal p < 0.05 "
      f"{int((CHK.tp53_p < 0.05).sum())}; |coupling ρ| > 0.3 {int(CHK.coupling_flag.astype(bool).sum())} "
      "(q-values are computed over the final top 40 only; top40_checks.tsv).",
      "", "## §4.3 artefact flags (every reported prediction)", "",
      f"- Predictions flagged: locus {M42['n_with_locus_flag']}, CN co-amplification {M42['n_with_cn_flag']}, ≥ 1 hub "
      f"partner {M42['n_with_hub_partner']}, hub-driven (> 50% of S) {M42['n_hub_driven']}; **excluded from Tier A "
      f"(≥ half of supporting partners flagged, or hub-driven): {int(fl_ex.sum())} of {len(FL):,}.**",
      f"- Hub = top 1% in-degree of the K = 25 graph among tool-background genes (in-degree ≥ "
      f"{M40['hub_in_degree_threshold']}; {M40['n_hub_genes']} genes). Locus flag is strand-agnostic (no strand in "
      "Ensembl 116 coordinates; DEVIATIONS).",
      "", "## Orthogonal support and empirical false-support rate (§5.3–§5.4)", "",
      "Scope: in-support p_cal ≥ 0.3 (none) ∪ the top 40 (preliminary and final entrants); equal-size matched-gene and "
      "decoy prediction sets. 'Rule' = the Tier-A support condition (diagnostic-class support when a diagnostic class "
      "is measured, and no contradiction).", "",
      "| prediction set | n | passes Tier-A support rule | strict diagnostic support | any class supports | "
      "contradiction (4 sources) | contradiction (HPA only) | P | A | L | G | S |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in FS.itertuples():
    L.append(f"| {r.set} | {r.n} | {r.passes_tierA_support_rule:.3f} | {r.strict_diagnostic_support:.3f} | "
             f"{r.any_class_support:.3f} | {r.contradiction:.3f} | {r.contradiction_hpa_only:.3f} | {r.supports_P:.2f} | "
             f"{r.supports_A:.2f} | {r.supports_L:.2f} | {r.supports_G:.2f} | {r.supports_S:.2f} |")
fsm, fsd = FS.set_index("set").loc["matched"], FS.set_index("set").loc["decoy"]
L += ["", f"Empirical false-support rate of the full rule: matched-gene predictions {fsm.passes_tierA_support_rule:.3f} "
      f"(strict {fsm.strict_diagnostic_support:.3f}), decoy predictions {fsd.passes_tierA_support_rule:.3f} (strict "
      f"{fsd.strict_diagnostic_support:.3f}), beside {nA} Tier A genes.",
      "", "## Negative control: clean-negative U genes (§4.2)", "",
      "Tier-A-like = in-support p_cal ≥ 0.5 AND split-half reproducibility p < 0.05 AND no §4.3 exclusion (expression and "
      "orthogonal conditions not applied). One-sided 95% upper bound shown when no call is observed.", "",
      "| set | SD tertile | n | with p_cal | median p_cal | 90th pct | max | Tier-A-like | rate | upper 95% | "
      "Tier-B-like |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in NC.itertuples():
    L.append(f"| {r.set} | {r.tertile} | {r.n:,} | {r.n_with_pcal:,} | {f3(r.p_cal_median)} | {f3(r.p_cal_p90)} | "
             f"{f3(r.p_cal_max)} | {r.n_tierA_like} | {f3(r.rate_tierA_like, 4)} | {f3(r.rate_upper95_if_zero, 4)} | "
             f"{r.n_tierB_like} |")
L += ["", "## Top 40 (p_cal fill: clean genes by p_cal, then flagged genes by p_cal; ties by supporting classes)", "",
      "Types: e lineage/transcriptional programme, a subunit (P/A/S support), c supplier/client, b assembly factor, "
      "d type unresolved (§4.4 script precedence). p_cal covers the V2 module term only, not the type. V1′ label is "
      "descriptive. Flags: see top40.tsv for every condition's pass/fail.", "",
      "| # | symbol | V2 term | V1′ label | family | p_cal | tier | supporting classes | flags | type |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for r in TOP.itertuples():
    tier = r.tier if isinstance(r.tier, str) and r.tier else "fill"
    L.append(f"| {r.rank} | {r.symbol} | {r.v2_term_name} ({r.v2_term}) | "
             f"{r.v1p_label_name if isinstance(r.v1p_label_name, str) else '—'} | {r.family} | {r.p_cal:.3f} | {tier} | "
             f"{r.supporting_classes if isinstance(r.supporting_classes, str) and r.supporting_classes else '—'} | "
             f"{r.flags if isinstance(r.flags, str) and r.flags else '—'} | {r.relationship_type} |")
L += ["", f"**Sensitivity (DEVIATIONS erratum row): top 40 ignoring top-40 demotions** (pure p_cal order after §4.3 "
      f"exclusion/contradiction): {int(SENS.in_primary_top40.sum())} of {len(SENS)} also in the primary top 40; "
      f"{int(SENS.demoted_top40_check.sum())} of them carry a top-40 demotion. List: "
      + ", ".join(f"{r.symbol} ({r.p_cal:.3f}{'*' if r.demoted_top40_check else ''})" for r in SENS.itertuples())
      + " (* = demoted by lineage leave-out / DEMETER2 / TP53). File: figdata/top40_sensitivity_no_demotion.tsv."]
L += ["", "## Fill iterations", "", "| iteration | entrants | left | newly demoted |", "|---|---|---|---|"]
for r in FILL.itertuples():
    L.append(f"| {r.iteration} | {r.entrants if isinstance(r.entrants, str) else ''} | "
             f"{r.left if isinstance(r.left, str) else ''} | {r.newly_demoted if isinstance(r.newly_demoted, str) else ''} |")
L += ["", "## Caveats", "",
      "- Many top-40 genes may be characterised outside GO D1 evidence (U = D1 ∩ (D2 ∪ D3)); novelty is decided at M7 "
      "(LLM recall probe, agent L), not here.",
      "- p_cal is the probability that the V2 top term is confirmed, not that the gene's function is that module; with "
      "an H hit rate of 3% and the frozen covariates, in-support p_cal is ≤ 0.15 for every U gene.",
      "- The locus flag is a strand-agnostic superset of the frozen rule; GLS rows exist for the final top 40 only "
      "(top40_partners_gls.tsv).", "",
      "## Files (results/ledger/)", "",
      "u_predictions.tsv, u_partners.tsv, u_top5.tsv (script 40); u_pcal.tsv, pcal_summary.json, "
      "negative_control_pcal.tsv (41); u_flags.tsv, u_flag_partners.tsv (42); support.tsv, support_sources.tsv, "
      "support_summary.json, prelim_top40.tsv (43; entrant rows appended by 44); top40.tsv, top40_checks.tsv, "
      "checks_all_evaluated.tsv, top40_fill_log.tsv, top40_partners_gls.tsv, tiers_all.tsv (44); negative_control.tsv, "
      "false_support.tsv, figdata/*.tsv (45); manifests 40–45. config/tf_list.tsv (40).", ""]
(OUT / "M6_SUMMARY.md").write_text("\n".join(L))
res = dict(sums=sums, n_tier_A=nA, n_tier_B=nB, n_expressed_assessable=n_ass, branch=branch,
           false_support=FS.to_dict("records"), negative_control=NC.to_dict("records"))
M6.jdump(res, OUT / "m6_results.json")
C.write_manifest(OUT / "45_manifest.json", "scripts/45_m6_summary.py", gate,
                 ["results/ledger/u_pcal.tsv", "results/ledger/top40.tsv", "results/ledger/support.tsv"], seed=0,
                 t0=T_START)
print("\n".join(L[:12]))
