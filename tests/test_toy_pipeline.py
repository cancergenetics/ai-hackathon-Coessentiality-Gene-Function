"""End-to-end toy pipeline (DESIGN.md v2 §2.5) on synthetic data with known answers, using the REAL tool.

Synthetic matrix: 300 cell lines x 2,000 genes (seed 0).
  * gene baseline: mean ~ N(-0.1, 0.3), noise SD ~ logNormal(0, 0.25) (heterogeneous profile covariates);
  * lineage nuisance factor: 6 lineages (with 2-line patients); 400 genes get lineage-specific shifts
    (SD 1.0 x gene SD) -- the dominant line-space structure, as on real DepMap data;
  * 36 planted modules, sizes 3-30: 24 strong (loading 0.7-1.0 x gene SD) and 12 weak (0.25-0.4);
  * 40 'chromosome arms' x 50 genes (random assignment); in 8 arms a 12-gene proximity block shares a CN-like
    factor (loading 0.9 x gene SD);
  * missingness: 60 genes miss a 40-line 'library' block (13% NaN -> non-background); 100 genes miss 2% at random.
Vocabulary: one term per module (minus held-out members), 6 parent terms (each the union of 6 module terms; DAG
module -> parent), one term per proximity block (7 of its 12 genes; the other 5 are queries), 80 random decoy terms
(sizes 5-150). Queries (unannotated): ~20% of each module (>= 1) and 5 genes per proximity block.
Null matrix: same gene means / SDs / missingness and vocabulary, no lineage, module or proximity structure;
400 random query genes.

Tool configuration for the toy (``TOY_CFG``) -- why it differs from the published Config():
  * k = 5 PCs removed (published 20): the planted lineage nuisance has rank 5 (6 lineages, centred); removing 20
    PCs from 300 lines x 2,000 genes would also remove the 20 largest planted modules (each module is one PC).
    On DepMap (1.1k lines x 18k genes) the published k = 20 removes screen/lineage nuisance (tool docs).
  * q = 1.25% -> tool K = 25 neighbours of ~1.9k BG genes (published 0.25% -> K = 44 of ~17.5k BG genes; 0.25% of
    1.9k would be K = 5, smaller than most planted modules).
  * d = 64 embedding dimensions (published 512 = 2.9% of BG genes; 64 is ~3.4% of 1.9k; d must be < |BG| - 2).
  * tau, max_nan, n_null, seed, block: published values.
Real DepMap runs use ``coess_matrix.PUBLISHED_CONFIG`` (= Config()); ``coess_matrix.is_published_config`` is recorded
in every manifest, so the toy settings cannot leak into the real run. Predictor settings are the pre-registered
ones (K = 25 neighbours, >= 2 supporting partners, same-arm exclusion, top-5 most-specific pruning) except: term-size
window 2-200 (planted modules are 3-30 genes; real window 5-200) and M = 200 matched genes (2,000-gene toy; real
M = 500). Matching uses mode='relaxed' (M nearest by Mahalanobis); the 0.2-SD caliper cannot supply M genes
(see the 'matching' block of the summary and docs/PIPELINE.md).

Acceptance (§2.5): strong-module held-out genes recover their module term at precision@1 >= 0.8; same-arm exclusion
removes proximity-driven calls; on the null matrix p_emp ~ Uniform (KS p > 0.01; tie-randomised p_emp, one
data-independent random term per query), genes with any BH-significant term <= 5%, assessable rate 5% +/- 2%
(randomised rule; the 'percentile' rule as written in DESIGN v2 is reported alongside).

Run: .env/bin/python -I -m pytest -q tests/test_toy_pipeline.py          (~1-2 min)
     .env/bin/python -I tests/test_toy_pipeline.py                       (prints the JSON summary)
"""
import json
import os
import sys
import tempfile
import time

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp
from scipy.stats import kstest
from statsmodels.stats.multitest import multipletests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import coess_matrix as cm  # noqa: E402
from src import neighbours as nbm  # noqa: E402
from src import predictor as pr  # noqa: E402
from src import splithalf as sh  # noqa: E402
from coessential.method import Config  # noqa: E402

TOY_CFG = Config(k=5, q=1.25, d=64)
K = 25
M_MATCH = 200
SEEDS = (0, 1, 2, 3, 4)
N_LINES, G = 300, 2000


# ------------------------------------------------------------------------------------------ simulation
def simulate(seed=0):
    rng = np.random.default_rng(seed)
    lineages = np.array(["Lung", "Breast", "CNS", "Skin", "Bowel", "Blood"])
    lin = rng.choice(len(lineages), N_LINES)
    lines = [f"ACH-{i:06d}" for i in range(N_LINES)]
    model = pd.DataFrame(dict(OncotreeLineage=lineages[lin],
                              PatientID=[f"PT-{i // 2}" if i < 40 else f"PT-{i}" for i in range(N_LINES)]),
                         index=lines)
    model.loc[lines[1:40:2], "OncotreeLineage"] = model.loc[lines[0:40:2], "OncotreeLineage"].values
    lin = pd.Index(lineages).get_indexer(model.OncotreeLineage)
    mu = rng.normal(-0.1, 0.3, G)
    sd = np.exp(rng.normal(0, 0.25, G))
    perm = rng.permutation(G)
    sizes = np.r_[rng.integers(3, 31, 24), rng.integers(3, 31, 12)]
    mods, p = [], 0
    for s in sizes:
        mods.append(np.sort(perm[p:p + s]))
        p += s
    strong = np.r_[np.ones(24, bool), np.zeros(12, bool)]
    lineage_genes = perm[p:p + 400]
    p += 400
    arm = rng.permutation(np.repeat(np.arange(40), G // 40))
    used = np.zeros(G, bool)
    used[perm[:p]] = True
    blocks = []
    for a in range(8):
        cand = np.flatnonzero((arm == a) & ~used)
        blocks.append(np.sort(rng.choice(cand, 12, replace=False)))
    nan_mask = np.zeros((N_LINES, G), bool)
    lib = rng.choice(G, 60, replace=False)
    nan_mask[np.ix_(np.arange(40), lib)] = True
    for g in rng.choice(np.setdiff1d(np.arange(G), lib), 100, replace=False):
        nan_mask[rng.choice(N_LINES, 6, replace=False), g] = True
    truth = dict(model=model, lineage_of_line=lin, mods=mods, strong=strong, lineage_genes=lineage_genes,
                 arm=arm, blocks=blocks, mu=mu, sd=sd, nan_mask=nan_mask, lines=lines)
    return truth, rng


def effect_matrix(truth, rng, null=False):
    eps = rng.standard_normal((N_LINES, G))
    X = truth["mu"] + truth["sd"] * eps
    if not null:
        sd = truth["sd"]
        L = rng.normal(0, 1.0, (6, len(truth["lineage_genes"])))
        X[:, truth["lineage_genes"]] += L[truth["lineage_of_line"]] * sd[truth["lineage_genes"]]
        for m, s in zip(truth["mods"], truth["strong"]):
            a = rng.uniform(0.7, 1.0, len(m)) if s else rng.uniform(0.25, 0.4, len(m))
            X[:, m] += rng.standard_normal((N_LINES, 1)) * a * sd[m]
        for b in truth["blocks"]:
            X[:, b] += rng.standard_normal((N_LINES, 1)) * 0.9 * sd[b]
    X[truth["nan_mask"]] = np.nan
    return pd.DataFrame(X.astype(np.float32), index=truth["lines"], columns=[f"G{j}" for j in range(G)])


def vocabulary(truth, rng):
    """Annotation matrix (held-out queries have empty rows), term names, ancestors, queries."""
    terms, members, queries = [], [], {}
    q_mod, q_prox = [], []
    for i, m in enumerate(truth["mods"]):
        nq = max(1, int(round(0.2 * len(m))))
        q = rng.choice(m, nq, replace=False)
        for g in q:
            queries[int(g)] = f"M{i}"
        q_mod += [(int(g), i) for g in q]
        terms.append(f"M{i}")
        members.append(np.setdiff1d(m, q))
    for j in range(6):
        terms.append(f"P{j}")
        members.append(np.concatenate([members[i] for i in range(j * 6, j * 6 + 6)]))
    for b, blk in enumerate(truth["blocks"]):
        q = rng.choice(blk, 5, replace=False)
        q_prox += [(int(g), b) for g in q]
        for g in q:
            queries[int(g)] = f"X{b}"
        terms.append(f"X{b}")
        members.append(np.setdiff1d(blk, q))
    qset = np.array(sorted(queries))
    pool = np.setdiff1d(np.arange(G), qset)
    for r in range(80):
        terms.append(f"R{r}")
        members.append(np.sort(rng.choice(pool, int(rng.integers(5, 151)), replace=False)))
    rows = np.concatenate(members)
    cols = np.repeat(np.arange(len(terms)), [len(m) for m in members])
    A = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(G, len(terms)))
    A.data[:] = 1.0
    anc = {t: {t} for t in terms}
    for i in range(36):
        anc[f"M{i}"].add(f"P{i // 6}")
    return A, terms, anc, q_mod, q_prox, qset


# ------------------------------------------------------------------------------------------ pipeline pieces
def neighbours_all(Z, bg, arm=None):
    nb = nbm.top_k(Z, K, bg=bg, arm=arm)
    nbm.assert_valid(nb, bg=bg, arm=arm)
    return nb


def predict(Z, bg, arm, A, cov, queries, term_ok, seed=0, randomize=False, all_terms=False):
    """Neighbours for all genes, S for all genes, matched genes and p_emp for the queries, score table."""
    nb = neighbours_all(Z, bg, arm)
    ts_all = pr.term_scores(nb, A)
    qi = np.asarray(queries)
    ts_q = pr.TermScores(rows=qi, S=ts_all.S[qi], n_sup=ts_all.n_sup[qi], x=ts_all.x[qi], n_draw=ts_all.n_draw[qi])
    m = pr.match_genes(cov, qi, bg, M_MATCH, caliper=0.2, mode="relaxed", nb=nb, arm=arm, seed=seed)
    pe = pr.empirical_p(ts_q, ts_all.S, m, A, term_ok=term_ok, all_terms=all_terms, randomize_ties=randomize,
                        seed=seed)
    tab = pr.score_table(ts_q, pr.hypergeom_p(ts_q, A), pe if not randomize else None, term_ok=term_ok)
    return nb, ts_q, m, pe, tab


def splithalf_rates(effect, truth, bg, arm, cov, genes_eval, nb_full, seeds=SEEDS):
    pairs, infos = [], []
    for s in seeds:
        half = sh.split_halves(effect.index, truth["model"], seed=s)
        ids = []
        for h in (0, 1):
            i, _, info = sh.half_neighbours(effect, half.index[half == h], K, TOY_CFG, bg=bg, arm=arm)
            ids.append(i)
            infos.append(info)
        pairs.append(tuple(ids))
    m = pr.match_genes(cov, genes_eval, bg, M_MATCH, caliper=None, mode="relaxed", nb=nb_full, arm=arm, seed=0)
    R, R0 = sh.reproducibility(pairs, K, m.matches)
    a = sh.assessable(R, R0, seed=0)
    return a, infos


# ------------------------------------------------------------------------------------------ the run
def run_pipeline(seed=0):
    """Full toy run; ``seed`` = simulation seed (the null matrix uses seed + 1). Returns the summary dict."""
    t0 = time.perf_counter()
    truth, rng = simulate(seed)
    out = dict(seed=seed, config=dict(toy_tool_config=cm.config_dict(TOY_CFG), K=K, M=M_MATCH, seeds=list(SEEDS)))
    A, terms, anc, q_mod, q_prox, qset = vocabulary(truth, rng)
    tsize = np.asarray(A.sum(0)).ravel()
    term_ok = (tsize >= 2) & (tsize <= 200)
    arm = truth["arm"]

    # ---------------- structured matrix
    eff = effect_matrix(truth, rng)
    t = time.perf_counter()
    fm = cm.fit_model(eff, TOY_CFG)
    tmp = tempfile.mkdtemp(prefix="toy_tool_")
    man = cm.write_tool_matrices(fm, tmp, log=lambda *_: None)
    Z, gt = cm.open_matrix(tmp, "zavg_BEF")
    out["tool_run_s"] = round(time.perf_counter() - t, 2)
    out["tool"] = dict(n_bg=man["n_bg"], K_tool=man["K_tool"], published_config=man["published_config"],
                       verify_pair_api=cm.verify_tool_matrices(fm, tmp, n_pairs=20000)["zavg_BEF"])
    bg = gt.bg.values.astype(bool)
    cov = pr.profile_covariates(eff)
    queries = np.array([g for g, _ in q_mod + q_prox])
    qtrue = {g: f"M{i}" for g, i in q_mod} | {g: f"X{b}" for g, b in q_prox}
    nb, ts_q, m, pe, tab = predict(Z, bg, arm, A, cov, queries, term_ok)
    tab["term_id"] = np.asarray(terms)[tab.term.values]
    out["matching"] = dict(relaxed=m.summary(), balance=pr.balance(cov, queries, m).round(3).to_dict("records"))
    ms = pr.match_genes(cov, queries, bg, M_MATCH, caliper=0.2, mode="strict", nb=nb, arm=arm)
    out["matching"]["strict_caliper_0.2"] = ms.summary()

    strong_q = [g for g, i in q_mod if truth["strong"][i] and bg[g]]
    weak_q = [g for g, i in q_mod if not truth["strong"][i] and bg[g]]
    res = {}
    for r in pr.RANKERS:
        tt = pr.top_terms(tab, r, ancestors=anc, term_col="term_id").set_index("query")
        def prec(qs, strict):
            hits = []
            for g in qs:
                if g not in tt.index:
                    hits.append(0.0)
                    continue
                tgt = qtrue[g]
                ok = {tgt} | ({f"P{int(tgt[1:]) // 6}"} if tgt.startswith("M") else set())
                hits.append(float(tt.loc[g, "most_specific"] == tgt) if strict else float(tt.loc[g, "top1"] in ok))
            return float(np.mean(hits)), len(hits)
        res[r] = dict(strong_p1_propagated=prec(strong_q, False)[0], strong_p1_most_specific=prec(strong_q, True)[0],
                      weak_p1_propagated=prec(weak_q, False)[0], n_strong=len(strong_q), n_weak=len(weak_q))
    out["module_recovery"] = res

    # proximity: same-arm exclusion on vs off
    prox_q = np.array([g for g, _ in q_prox if bg[g]])
    _, _, _, _, tab_off = predict(Z, bg, None, A, cov, prox_q, term_ok)
    tab_on = tab[tab["query"].isin(prox_q)]
    tab_off = tab_off.assign(term_id=np.asarray(terms)[tab_off.term.values])
    def prox_calls(tb):
        tt = pr.top_terms(tb, "R3", ancestors=anc, term_col="term_id").set_index("query")
        top = [tt.loc[g, "top1"] if g in tt.index else None for g in prox_q]
        rep = tb[tb.reportable & tb.term_id.str.startswith("X")]
        own = [((rep["query"] == g) & (rep.term_id == qtrue[g])).any() for g in prox_q]
        return dict(top1_is_own_block_term=float(np.mean([t == qtrue[g] for t, g in zip(top, prox_q)])),
                    own_block_term_reportable=float(np.mean(own)), n=len(prox_q))
    same_arm_frac = float(np.mean([(arm[nb.ids[g][nb.ids[g] >= 0]] == arm[g]).any() for g in range(G)]))
    out["proximity"] = dict(without_exclusion=prox_calls(tab_off), with_exclusion=prox_calls(tab_on),
                            any_same_arm_neighbour_with_exclusion=same_arm_frac)

    # split-half on the structured matrix: positive control for assessability
    t = time.perf_counter()
    eval_genes = np.flatnonzero(bg)
    a_str, _ = splithalf_rates(eff, truth, bg, arm, cov, eval_genes, nb)
    strong_genes = np.concatenate([mm for mm, s in zip(truth["mods"], truth["strong"]) if s])
    noise = np.setdiff1d(eval_genes, np.concatenate([*truth["mods"], truth["lineage_genes"], *truth["blocks"]]))
    a_str = a_str.set_index("gene")
    out["assessability_structured"] = {
        rule: dict(strong_module_genes=float(a_str.loc[np.intersect1d(strong_genes, eval_genes), rule].mean()),
                   noise_genes=float(a_str.loc[noise, rule].mean()))
        for rule in sh.RULES}
    out["splithalf_structured_s"] = round(time.perf_counter() - t, 1)

    # ---------------- null matrix
    rng_null = np.random.default_rng(seed + 1)
    effn = effect_matrix(truth, rng_null, null=True)
    t = time.perf_counter()
    fmn = cm.fit_model(effn, TOY_CFG)
    tmpn = tempfile.mkdtemp(prefix="toy_null_")
    cm.write_tool_matrices(fmn, tmpn, kinds=("zavg_BEF",), log=lambda *_: None)
    Zn, gtn = cm.open_matrix(tmpn, "zavg_BEF")
    bgn = gtn.bg.values.astype(bool)
    covn = pr.profile_covariates(effn)
    qn = np.sort(rng_null.choice(np.setdiff1d(np.flatnonzero(bgn), qset), 400, replace=False))
    An = A.tolil()
    An[qn] = 0                                       # null queries are unannotated
    An = An.tocsr()
    An.eliminate_zeros()
    tsize_n = np.asarray(An.sum(0)).ravel()
    term_ok_n = (tsize_n >= 2) & (tsize_n <= 200)
    nb_n, ts_n, m_n, pe_rand, _ = predict(Zn, bgn, arm, An, covn, qn, term_ok_n, randomize=True, all_terms=True)
    _, _, _, pe_cons, tab_n = predict(Zn, bgn, arm, An, covn, qn, term_ok_n, all_terms=True)
    pick = np.random.default_rng(7)
    one = []
    for g in qn:
        terms_g, p, _ = pe_rand[int(g)]
        one.append(p[pick.integers(len(terms_g))])
    ks = kstest(one, "uniform")
    bh_any, bh_any_rep, bh_hyper, tail, all_rand = [], [], [], [], []
    rep = tab_n[tab_n.reportable]
    n_ok = int(term_ok_n.sum())
    for g in qn:
        terms_g, p, _ = pe_cons[int(g)]
        bh_any.append(multipletests(p, alpha=0.05, method="fdr_bh")[0].any())
        pr_ = rep.loc[rep["query"] == g, "p_emp"].values
        bh_any_rep.append(multipletests(pr_, alpha=0.05, method="fdr_bh")[0].any() if len(pr_) else False)
        ph = tab_n.loc[tab_n["query"] == g, "p_hyper"].values           # terms with S = 0 have p = 1
        bh_hyper.append(multipletests(np.r_[ph, np.ones(n_ok - len(ph))], alpha=0.05, method="fdr_bh")[0].any())
        tail.append(p)
        all_rand.append(pe_rand[int(g)][1])
    tail = np.concatenate(tail)
    a_null, infos = splithalf_rates(effn, truth, bgn, arm, covn, np.flatnonzero(bgn), nb_n)
    out["null"] = dict(
        ks_uniform_p=float(ks.pvalue), ks_stat=float(ks.statistic), n_queries=len(qn),
        frac_genes_any_bh_term_all_terms=float(np.mean(bh_any)),
        frac_genes_any_bh_term_reportable_terms=float(np.mean(bh_any_rep)),
        frac_genes_any_bh_term_hypergeometric=float(np.mean(bh_hyper)),
        min_attainable_p_emp=float(1.0 / (1 + M_MATCH)), n_terms_tested=n_ok,
        ks_uniform_p_all_pairs=float(kstest(np.concatenate(all_rand), "uniform").pvalue),
        conservative_p_le_0_05=float(np.mean(tail <= 0.05)), conservative_p_le_0_01=float(np.mean(tail <= 0.01)),
        reportable_top1_rate=float(tab_n.groupby("query").reportable.any().reindex(qn).fillna(False).mean()),
        assessable_rate={rule: float(a_null[rule].mean()) for rule in sh.RULES},
        n_assessability_genes=int(len(a_null)),
        R_mean=float(a_null.R.mean()), R0_mean=float(a_null.R0_mean.mean()),
        half_bg=[i["n_bg"] for i in infos], half_dropped=[len(i["dropped_all_nan"]) for i in infos])
    out["null_s"] = round(time.perf_counter() - t, 1)
    out["total_s"] = round(time.perf_counter() - t0, 1)
    del Z, Zn
    import shutil
    for d in (tmp, tmpn):
        shutil.rmtree(d, ignore_errors=True)
    return out


@pytest.fixture(scope="module")
def summary():
    s = run_pipeline()
    dest = os.environ.get("TOY_SUMMARY_OUT")
    if dest:
        with open(dest, "w") as fh:
            json.dump(s, fh, indent=1, default=float)
    return s


def test_tool_matrix_consistency(summary):
    assert summary["tool"]["verify_pair_api"]["max_abs_diff"] < 1e-4
    assert not summary["tool"]["published_config"]


def test_strong_modules_recovered(summary):
    r = summary["module_recovery"]["R3"]
    assert r["n_strong"] >= 50
    assert r["strong_p1_propagated"] >= 0.8
    assert r["strong_p1_most_specific"] >= 0.8


def test_same_arm_exclusion_removes_proximity_calls(summary):
    p = summary["proximity"]
    assert p["without_exclusion"]["top1_is_own_block_term"] >= 0.8       # the artefact exists without exclusion
    assert p["with_exclusion"]["own_block_term_reportable"] == 0.0
    assert p["any_same_arm_neighbour_with_exclusion"] == 0.0


def test_null_p_emp_uniform(summary):
    assert summary["null"]["ks_uniform_p"] > 0.01
    assert summary["null"]["conservative_p_le_0_05"] <= 0.05


def test_null_bh(summary):
    """BH within gene over the whole size-eligible vocabulary. NB: with M matched genes p_emp >= 1 / (1 + M), so BH
    over ~100+ terms can hardly reject -- this criterion is weak for p_emp (reported, see docs/PIPELINE.md); BH
    restricted to reportable terms (selected by >= 2 partners) is anti-conservative and is reported only."""
    assert summary["null"]["frac_genes_any_bh_term_all_terms"] <= 0.05
    assert summary["null"]["frac_genes_any_bh_term_hypergeometric"] <= 0.05


def test_null_assessable_rate(summary):
    assert abs(summary["null"]["assessable_rate"]["randomized"] - 0.05) <= 0.02


def test_assessability_positive_control(summary):
    a = summary["assessability_structured"]["randomized"]
    assert a["strong_module_genes"] >= 0.8 and a["noise_genes"] <= 0.1


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=1, default=float))
