#!/usr/bin/env python
"""33_holdout_secondary.py -- M5b secondary batch on the temporal hold-out H (DESIGN.md v2.3 §3.3, §3.6, §8:
'secondary batch run once, reported all or none').

Uses the primary H set, targets, circularity exclusion, matched-null selection and clusters of scripts/32
(data/derived/holdout_eval/core.pkl). Every analysis keeps ranker R1 and the >= 2-partner reportability rule.
  1. Pearson (scripts/16 rows; same exclusions and predictor) -- zavg - Pearson, two-sided.
  2. Homology baseline: candidate terms the gene carries at t0 through IEA/ISS/IBA annotations (t0 GAF, same row
     rules as V2 otherwise, current obo, propagated) ranked by t0 frequency, then all other candidates by frequency.
  3. PPI module transfer: N(g) = top-25 scorable partners by hu.MAP 3.0 probability (all-PPI file), weight =
     probability; coverage reported. (U complementarity needs U predictions: M6.)
  4. t0 = 2019-07: H rebuilt with scripts/04 ``build_holdout`` at GO 2019-07-01 (cut-off PMID 2019-07-01), V2 at
     2019-07 for neighbour membership; circularity, matched null and clusters recomputed by the same rules.
  5. PMID-dated targets: only targets whose supporting PMIDs are all >= the 2018-07 cut-off
     (H_targets.support_all_pmids_post_cutoff); other targets dropped from targets and lists.
  6. K = 10 and K = 50 neighbours (first K of the stored top-100 lists).
  7. No exclusions: N(g) from the full matrix without same-arm / paralogue exclusion.
  8. U-reweighted estimate (§3.6): logistic U-eligible vs H on mean effect, SD, NaN fraction, top-K mean zavg, R(g),
     coverage percentile; U-eligible = scorable U genes inside H's 5th-95th percentiles of top-K mean zavg, R(g) and
     coverage percentile (the §3.7 support covariates that need no U prediction); inverse-odds weights trimmed at the
     1st/99th percentile; refitted in each of 10,000 cluster-bootstrap replicates of H.
  9. LOO-fitted calibration: the §3.7 model fitted on the LOO benchmark (scripts/30 R1 outcomes; current-release
     percentiles) and evaluated on H.
Outputs: results/holdout_eval/secondary.md, secondary.tsv, secondary_results.json, loo_fitted_reliability.tsv,
secondary_manifest.json.
Run: .env/bin/python -I scripts/33_holdout_secondary.py   (after scripts/32)
"""
import importlib.util
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

import m5b_common as B  # noqa: E402
from src import calibration as cal  # noqa: E402
from src import knownness as kn  # noqa: E402
from src import metrics as mt  # noqa: E402

log = C.log
OUT, DER = B.OUT, B.DER
CORE = pd.read_pickle(DER / "core.pkl")
P, Tp, Dp, T_all, nulls, TT = (CORE[k] for k in ("P", "Tp", "Dp", "T_all", "nulls", "TT"))
clP = np.array([CORE["cl_primary"][g] for g in P])
clmap = CORE["cl_primary"]
PG = pd.read_csv(OUT / "per_gene_core.tsv", sep="\t", index_col="pos")
assert list(PG.index) == list(P)
RES = dict(dry_run=B.DRY, n_boot=B.NBOOT)
rows = []
timing = {}

base = B.Base()
gt, G = base.gt, base.G
v2t0 = B.build_v2(base, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
S_main = B.Scored(v2t0, base.nb, base.matches, set(P) | {m for g in P for m in nulls[g]}, "zavg t0")
Ez = B.evaluate(P, S_main.r1, Tp, Dp, S_main.sizes)
assert np.allclose(Ez.hit1.values, PG.hit1_zavg.values), "re-scored zavg differs from scripts/32"


def cl(genes):
    return np.array([clmap[int(g)] for g in genes])


def comparator_row(name, e_comp, extra=None):
    r = B.pdiff(Ez.hit1, e_comp.hit1, clP)
    b = B.mci(e_comp.hit1.values, clP)
    d = dict(analysis=name, kind="comparator", n=len(P), p1_method=e_comp.hit1.mean(), p1_method_lo=b["ci_percentile"][0],
             p1_method_hi=b["ci_percentile"][1], coverage=e_comp.has_pred.mean(), p1_zavg=Ez.hit1.mean(),
             d_zavg_minus_method=r["estimate"], d_lo=r["ci_percentile"][0], d_hi=r["ci_percentile"][1],
             d_bca_lo=r["ci_bca"][0], d_bca_hi=r["ci_bca"][1], mrr_method=e_comp.rr.mean())
    if extra:
        d.update(extra)
    return d


def variant_row(name, genes, e, clv, extra=None):
    d = dict(analysis=name, kind="variant", n=len(genes), p1_zavg=e["net"].hit1.mean(),
             p1_prior=e["prior"].hit1.mean(), p1_null=e["null"].hit1.mean(), coverage=e["net"].has_pred.mean())
    b = B.mci(e["net"].hit1.values, clv)
    d.update(p1_zavg_lo=b["ci_percentile"][0], p1_zavg_hi=b["ci_percentile"][1])
    for b_ in ("prior", "null"):
        r = B.pdiff(e["net"].hit1, e[b_].hit1, clv)
        d.update({f"d_{b_}": r["estimate"], f"d_{b_}_lo": r["ci_percentile"][0], f"d_{b_}_hi": r["ci_percentile"][1],
                  f"d_{b_}_bca_lo": r["ci_bca"][0], f"d_{b_}_bca_hi": r["ci_bca"][1]})
    d["iut_pass"] = bool(d["d_prior_lo"] > 0 and d["d_null_lo"] > 0)
    if extra:
        d.update(extra)
    return d


# ============================================================================================ 1. Pearson
nb_p = B.baseline_network(base, "pearson", P)
Sp = B.Scored(v2t0, nb_p, base.matches, P, "Pearson t0")
rows.append(comparator_row("Pearson (R1)", B.evaluate(P, Sp.r1, Tp, Dp, S_main.sizes)))

# ============================================================================================ 2. homology
g0 = kn.read_gaf(str(C.ROOT / B.T0_DIR / "goa_human.gaf.gz"))
g0 = g0[~kn.is_not_qualified(g0.qualifier)]
g0 = g0[~g0.qualifier.fillna("").str.split("|").apply(lambda x: "colocalizes_with" in x)]
g0 = g0[g0.aspect.isin(["P", "F"]) & g0.evidence.isin(["IEA", "ISS", "IBA"])]
res = {t: base.onto.resolve(t)[0] for t in g0.go_id.unique()}
g0 = g0.assign(go_id=g0.go_id.map(res)).dropna(subset=["go_id"])
Pset = set(P)
hom = {}
for a, t in zip(g0.acc.values, g0.go_id.values):
    for h in base.acc_map.get(kn.strip_isoform(a), ()):
        p = base.pos.get(h)
        if p in Pset:
            hom.setdefault(p, set()).add(t)
hom_cols = {}
for p, ts in hom.items():
    s = set()
    for t in ts:
        s |= base.onto.ancestors(t)
    hom_cols[p] = {v2t0.col[t] for t in s if t in v2t0.col}
hl, hcov = {}, {}
for g in P:
    pl = S_main.prior(g)
    hc = [c for c in pl if c in hom_cols.get(g, set())]            # prior order = frequency desc, ties GO id
    hcov[g] = bool(hc)
    hl[g] = hc + [c for c in pl if c not in set(hc)]
eh = B.evaluate(P, hl, Tp, Dp, S_main.sizes)
rows.append(comparator_row("Homology baseline (t0 IEA/ISS/IBA, then frequency)", eh,
                           dict(coverage=float(np.mean([hcov[g] for g in P])))))
RES["homology"] = dict(rows=len(g0), genes_with_homology_terms=int(sum(hcov.values())))

# ============================================================================================ 3. PPI
t = time.perf_counter()
nb_h, hst = B.humap_network(base, P)
Shm = B.Scored(v2t0, nb_h, base.matches, P, "hu.MAP PPI t0")
ehm = B.evaluate(P, Shm.r1, Tp, Dp, S_main.sizes)
rows.append(comparator_row("PPI module transfer (hu.MAP 3.0 top-25)", ehm,
                           dict(n_with_partner=hst["queries_with_partner"])))
RES["ppi"] = dict(hst, coverage_reportable=float(ehm.has_pred.mean()))
timing["ppi_s"] = round(time.perf_counter() - t, 1)

# ============================================================================================ 4. t0 = 2019-07
t = time.perf_counter()
v2_19 = B.build_v2(base, f"{B.T19_DIR}/goa_human.gaf.gz", label="2019-07")
if not B.DRY:
    spec = importlib.util.spec_from_file_location("hold04", C.ROOT / "scripts" / "04_holdout_sizing.py")
    h04 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h04)
    pc = kn.load_hgnc_pc(str(C.ROOT / "data/raw/hgnc/hgnc_complete_set.txt"))
    hub = pd.read_csv(C.ROOT / "results/ids/hgnc_hub.tsv", sep="\t", dtype=str, keep_default_na=False)
    scorable = (hub.set_index("hgnc_id").scorable == "True").to_dict()
    g2p = kn.load_g2p(str(C.ROOT / "data/raw/ncbi_gene/gene2pubmed_9606.tsv"))
    ann_cur, _ = kn.d1_annotations(str(C.ROOT / "data/raw/go/current/goa_human.gaf.gz"), base.onto, base.acc_map,
                                   resolve_mode="strict")
    prop_cur = kn.propagate_annotations(ann_cur, base.onto)
    ctx = dict(pc=pc, acc_map=base.acc_map, onto_cur=base.onto, g2p=g2p, ann_cur=ann_cur, prop_cur=prop_cur,
               scorable=scorable)
    cut = pd.read_csv(C.ROOT / B.CUTOFFS, sep="\t", dtype={"cutoff_date": str}).set_index("cutoff_date").cutoff_pmid
    R19 = h04.build_holdout("2019-07-01", int(cut["2019-07-01"]), C.fz("holdout", "h_max_focused_pmids"), ctx)
    acg = {g: d for g, d in ann_cur[ann_cur.hgnc_id.isin(set(R19["H"]))].groupby("hgnc_id")}
    t19 = []
    for h in R19["H"]:
        a = acg[h]
        anc = [base.onto.ancestors(x) for x in a.go_id]
        for term in sorted(R19["targets"][h]):
            m = np.array([term in s for s in anc])
            t19.append(dict(pos=base.pos[h], go_id=term, pmids=kn.pmids_from_refs(a.reference.values[m])))
    T19 = pd.DataFrame(t19)
else:
    v2cur = B.build_v2(base, "data/raw/go/current/goa_human.gaf.gz", label="current (dry)")
    loo = pd.read_csv(C.ROOT / "results/loo_sample.tsv", sep="\t")
    cand19 = {t_ for t_, s in zip(v2_19.terms, v2_19.size) if B.LO <= s <= B.HI}
    t19 = []
    for p in loo.matrix_index.values[600:1000]:
        for term in sorted((v2cur.prop.get(int(p), frozenset()) - v2_19.prop.get(int(p), frozenset())) & cand19):
            t19.append(dict(pos=int(p), go_id=term, pmids=B.support_pmids(v2cur, int(p), term)))
    T19 = pd.DataFrame(t19)
fl19 = B.circ_lookup({p for ps in T19.pmids for p in ps})
T19["flagged"] = [s[0] for s in B.target_states(T19.pmids, fl19)]
T19["col"] = T19.go_id.map(lambda x: v2_19.col.get(x, -1))
H19 = sorted(T19.pos.unique().tolist())
T19all = T19.groupby("pos").go_id.apply(set).to_dict()
k19 = T19[~T19.flagged]
P19 = sorted(k19.pos.unique().tolist())
Tp19 = {int(g): set(int(c) for c in d.col if c >= 0) for g, d in k19.groupby("pos")}
Dp19 = {int(g): set(int(c) for c in d.col if c >= 0) for g, d in T19[T19.flagged].groupby("pos")}
n19, _ = B.select_nulls(v2_19, base.matches, P19, T19all)
pm19 = {int(g): set(p for ps in d.pmids for p in ps) for g, d in T19.groupby("pos")}
CL19 = B.clusters_for(H19, pm19, base.nb)
i19 = {g: i for i, g in enumerate(H19)}
cl19 = np.asarray(CL19["primary"])[[i19[g] for g in P19]]
e19, _ = B.method_set(v2_19, base.nb, base.matches, P19, Tp19, Dp19, n19, "2019-07")
rows.append(variant_row("t0 = 2019-07 (H rebuilt)", P19, e19, cl19,
                        dict(n_H=len(H19), clusters=CL19["primary_name"], overlap_with_H=len(set(P19) & set(P)))))
RES["t2019"] = dict(n_H=len(H19), n_primary=len(P19), n_pairs=len(T19), n_flagged=int(T19.flagged.sum()),
                    clusters=CL19["summary"], cluster_rule=CL19["primary_name"],
                    n_new_pmids_queried=int(fl19.attrs.get("n_new_queried", 0)))
timing["t2019_s"] = round(time.perf_counter() - t, 1)

# ============================================================================================ 5. PMID-dated targets
dated = TT.support_all_pmids_post_cutoff.astype(str).str.lower().eq("true").values
mask = (~TT.flagged.values) & dated
kd = TT[mask]
Pd = sorted(kd.pos.unique().tolist())
Tpd = {int(g): set(int(c) for c in d.col if c >= 0) for g, d in kd.groupby("pos")}
Dpd = {int(g): set(int(c) for c in d.col if c >= 0) for g, d in TT[~mask].groupby("pos")}
ed = dict(net=B.evaluate(Pd, S_main.r1, Tpd, Dpd, S_main.sizes),
          prior=B.evaluate(Pd, {g: S_main.prior(g) for g in Pd}, Tpd, Dpd, S_main.sizes),
          null=B.evaluate_null(Pd, nulls, S_main.r1, Tpd, Dpd, S_main.sizes))
rows.append(variant_row("PMID-dated targets (all supporting PMIDs ≥ 2018-07 cut-off)", Pd, ed, cl(Pd)))

# ============================================================================================ 6-7. K and exclusions
for k in C.fz("comparators", "secondary_k_values"):
    ek, _ = B.method_set(v2t0, base.nb_k(k), base.matches, P, Tp, Dp, nulls, f"K={k}")
    rows.append(variant_row(f"K = {k}", P, ek, clP))
t = time.perf_counter()
nb_nx = B.noexcl_network(base, set(P) | {m for g in P for m in nulls[g]})
enx, _ = B.method_set(v2t0, nb_nx, base.matches, P, Tp, Dp, {g: nulls[g] for g in P}, "no exclusions")
rows.append(variant_row("No same-arm / paralogue exclusion", P, enx, clP))
timing["noexcl_s"] = round(time.perf_counter() - t, 1)

# ============================================================================================ 8. U-reweighting
t = time.perf_counter()
Upos, cov_cur_pct = CORE["Upos"], CORE["cov_cur_pct"]
Hc = PG[PG.has_pred_zavg.astype(bool)]
lo5, hi95 = (np.percentile(Hc[["zmean", "R", "cov_pct"]].values, q, axis=0) for q in (5, 95))
UX = np.column_stack([base.zmean[Upos], base.R[Upos], cov_cur_pct[Upos]])
Uel = Upos[((UX >= lo5) & (UX <= hi95)).all(1)]
mean_eff, sd_eff, nanf = base.cov["mean"].values, np.exp(base.cov.log_sd.values), base.cov.nan_fraction.values
XU = np.column_stack([mean_eff[Uel], sd_eff[Uel], nanf[Uel], base.zmean[Uel], base.R[Uel], cov_cur_pct[Uel]])
XH = PG[["mean_effect", "sd", "nan_fraction", "zmean", "R", "cov_pct"]].values.astype(float)
HIT = {m: PG[f"hit1_{m}"].values.astype(float) for m in ("zavg", "prior", "null", "gls")}
TRIM = C.fz("covariate_shift", "weight_trim_percentiles")


def weights(idx):
    Xh = XH[idx]
    f = B.logistic_fit(np.r_[Xh, XU], np.r_[np.zeros(len(Xh)), np.ones(len(XU))])
    p = f(Xh)
    w = p / (1 - p)
    a, b = np.percentile(w, TRIM)
    return np.clip(w, a, b)


w0 = weights(np.arange(len(P)))
wp1 = {m: float(np.sum(w0 * HIT[m]) / w0.sum()) for m in HIT}
labs, inv = np.unique(clP, return_inverse=True)
members = [np.flatnonzero(inv == c) for c in range(len(labs))]
rng = np.random.default_rng(B.SEED)
bd = {b_: np.empty(B.NBOOT) for b_ in ("prior", "null", "gls")}
bz = np.empty(B.NBOOT)
for i in range(B.NBOOT):
    idx = np.concatenate([members[c] for c in rng.integers(0, len(labs), len(labs))])
    w = weights(idx)
    bz[i] = np.sum(w * HIT["zavg"][idx]) / w.sum()
    for b_ in bd:
        bd[b_][i] = np.sum(w * (HIT["zavg"][idx] - HIT[b_][idx])) / w.sum()
uw = dict(n_H=len(P), n_U_scorable=len(Upos), n_U_eligible=len(Uel), weight_min=float(w0.min()),
          weight_max=float(w0.max()), ess=float(w0.sum() ** 2 / np.sum(w0 ** 2)), p1=wp1,
          p1_zavg_ci=tuple(np.quantile(bz, [0.025, 0.975])))
for b_ in bd:
    uw[f"d_{b_}"] = wp1["zavg"] - wp1[b_]
    uw[f"d_{b_}_ci"] = tuple(np.quantile(bd[b_], [0.025, 0.975]))
RES["u_reweighted"] = uw
rows.append(dict(analysis="U-reweighted (inverse-odds, trimmed 1/99)", kind="reweighted", n=len(P),
                 p1_zavg=wp1["zavg"], p1_zavg_lo=uw["p1_zavg_ci"][0], p1_zavg_hi=uw["p1_zavg_ci"][1],
                 p1_prior=wp1["prior"], p1_null=wp1["null"], p1_method=wp1["gls"],
                 d_prior=uw["d_prior"], d_prior_lo=uw["d_prior_ci"][0], d_prior_hi=uw["d_prior_ci"][1],
                 d_null=uw["d_null"], d_null_lo=uw["d_null_ci"][0], d_null_hi=uw["d_null_ci"][1],
                 d_zavg_minus_method=uw["d_gls"], d_lo=uw["d_gls_ci"][0], d_hi=uw["d_gls_ci"][1],
                 iut_pass=bool(uw["d_prior_ci"][0] > 0 and uw["d_null_ci"][0] > 0),
                 extra_note=f"U-eligible {len(Uel)}; ESS {uw['ess']:.0f}; method = GLS"))
timing["reweight_s"] = round(time.perf_counter() - t, 1)

# ============================================================================================ 9. LOO-fitted calibration
fams = B.load_families()
LP = pd.read_csv(C.ROOT / "results/calibration/loo_per_gene.tsv.gz", sep="\t")
LP = LP[LP.has_pred_R1.astype(bool)].copy()
LP["zmean"], LP["R"] = base.zmean[LP.pos.values], base.R[LP.pos.values]
LP["cov_pct"] = cov_cur_pct[LP.pos.values]
LP["size_pct"] = B.pct_rank(np.log(LP.top1size_R1.values.astype(float)), np.log(CORE["ref_size_cur"][base.scor]))
LP["family"] = [B.family_of(t_, base.onto, fams) for t_ in LP.top1_R1]
kept, ref, fcnt = B.fams_kept(Hc)
XL, names, signs = B.design(LP, kept, ref)
XHc, _, _ = B.design(Hc, kept, ref)
mL = cal.MonotoneLogistic(signs).fit(XL, LP.hit1_R1.values.astype(float))
pH = mL.predict_proba(XHc)
yH = Hc.hit1_zavg.values.astype(float)
lf = B.calib_metrics(pH, yH)
lf.update(n_loo=len(LP), loo_hit_rate=float(LP.hit1_R1.mean()), converged=mL.converged_,
          coef=dict(zip(names, mL.coef_.tolist())), families_kept=kept, reference_family=ref)
RES["loo_fitted_calibration"] = lf
RLO = B.reliability(pH, yH)
RLO.to_csv(OUT / "loo_fitted_reliability.tsv", sep="\t", index=False, float_format="%.5f")
rows.append(dict(analysis="LOO-fitted calibration evaluated on H", kind="calibration", n=len(Hc),
                 extra_note=f"Brier {lf['brier']:.4f}; intercept {lf['intercept']:+.3f} "
                            f"({B.fmt_ci(lf['intercept_ci'], 3, True)}); slope {lf['slope']:.3f} "
                            f"({B.fmt_ci(lf['slope_ci'], 3)}); mean p {lf['mean_pred']:.3f} vs observed "
                            f"{lf['obs_rate']:.3f}"))

# ============================================================================================ outputs
SEC = pd.DataFrame(rows)
SEC.to_csv(OUT / "secondary.tsv", sep="\t", index=False, float_format="%.6f")
RES["timing"] = timing
man = C.write_manifest(OUT / "secondary_manifest.json", "scripts/33_holdout_secondary.py", gate,
                       [*B.M5.INPUTS, f"{B.T0_DIR}/goa_human.gaf.gz", f"{B.T19_DIR}/goa_human.gaf.gz",
                        "data/derived/baselines/pearson_rows.npy",
                        "data/raw/humap3/humap3_all_ppis_202305.pairsWprob.gz",
                        "results/calibration/loo_per_gene.tsv.gz"] + ([] if B.DRY else ["results/holdout_eval/per_gene_core.tsv"]),
                       seed=B.SEED, t0=T_START, extra=dict(timing=timing))
RES["runtime_s"] = man["runtime_s"]
B.jdump(RES, OUT / "secondary_results.json")


def f3(x):
    return "" if pd.isna(x) else f"{x:.3f}"


L = ["# M5b secondary batch on H (scripts/33; reported all or none)", "",
     f"Generated {man['created']} (runtime {man['runtime_s']} s). Primary H n = {len(P)}; clusters as scripts/32; "
     f"bootstrap {B.NBOOT:,} replicates, seed {B.SEED}." + (" **DRY RUN -- not H.**" if B.DRY else ""), "",
     "## Comparator methods (same predictor, R1, ≥ 2 partners)", "",
     "| method | precision@1 (CI) | coverage | MRR | zavg − method (95% CI) | BCa |", "|---|---|---|---|---|---|"]
for x in SEC[SEC.kind == "comparator"].itertuples():
    L.append(f"| {x.analysis} | {f3(x.p1_method)} ({f3(x.p1_method_lo)}–{f3(x.p1_method_hi)}) | {x.coverage:.3f} | "
             f"{f3(x.mrr_method)} | {x.d_zavg_minus_method:+.3f} ({x.d_lo:+.3f} to {x.d_hi:+.3f}) | "
             f"{x.d_bca_lo:+.3f} to {x.d_bca_hi:+.3f} |")
L += ["", f"zavg_BEF precision@1 = {Ez.hit1.mean():.3f}. hu.MAP: {hst['queries_with_partner']} of {len(P)} H genes "
      f"have ≥ 1 partner ({hst['queries_with_ge2_partners']} ≥ 2); homology terms for {RES['homology']['genes_with_homology_terms']}"
      f" genes.", "", "## Variants of the primary analysis", "",
      "| variant | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) | IUT |", "|---|---|---|---|---|---|---|---|"]
for x in SEC[SEC.kind.isin(["variant", "reweighted"])].itertuples():
    L.append(f"| {x.analysis} | {x.n} | {f3(x.p1_zavg)} ({f3(x.p1_zavg_lo)}–{f3(x.p1_zavg_hi)}) | {f3(x.p1_prior)} | "
             f"{f3(x.p1_null)} | {x.d_prior:+.3f} ({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | {x.d_null:+.3f} "
             f"({x.d_null_lo:+.3f} to {x.d_null_hi:+.3f}) | {'pass' if x.iut_pass else 'fail'} |")
L += ["", f"t0 = 2019-07: |H| = {len(H19)}, primary {len(P19)} ({RES['t2019']['n_flagged']} flagged pairs), clusters "
      f"{CL19['primary_name']} {CL19['summary']}. U-reweighting: U-eligible {len(Uel)} of {len(Upos)} scorable U "
      f"genes; weights {w0.min():.3f}–{w0.max():.3f}, effective sample size {uw['ess']:.0f}; weighted GLS "
      f"precision@1 {wp1['gls']:.3f}, zavg − GLS {uw['d_gls']:+.3f} ({B.fmt_ci(uw['d_gls_ci'], 3, True)}).", "",
      "## LOO-fitted calibration evaluated on H", "",
      f"Model §3.7 fitted on {lf['n_loo']} LOO genes with a prediction (hit rate {lf['loo_hit_rate']:.3f}); applied to "
      f"{lf['n']} H genes with a prediction: mean predicted {lf['mean_pred']:.3f} vs observed {lf['obs_rate']:.3f}; "
      f"Brier {lf['brier']:.4f} (constant-rate reference {lf['brier_ref_constant']:.4f}); calibration intercept "
      f"{lf['intercept']:+.3f} ({B.fmt_ci(lf['intercept_ci'], 3, True)}); slope {lf['slope']:.3f} "
      f"({B.fmt_ci(lf['slope_ci'], 3)}).", "",
      "| bin | n | p range | mean predicted | observed | Wilson 95% CI |", "|---|---|---|---|---|---|"]
for x in RLO.itertuples():
    L.append(f"| {x.bin} | {x.n} | {x.p_min:.3f}–{x.p_max:.3f} | {x.mean_pred:.3f} | {x.obs_rate:.3f} | "
             f"{x.ci_lo:.3f}–{x.ci_hi:.3f} |")
L += ["", "Notes: comparator CIs are paired cluster bootstraps of zavg − method (two-sided). PPI module transfer "
      "uses hu.MAP 3.0, which post-dates t0 (favours the comparator). U complementarity of the PPI comparator "
      "requires U predictions and is deferred to M6.", ""]
(OUT / "secondary.md").write_text("\n".join(L))
log(f"done in {man['runtime_s']} s")
