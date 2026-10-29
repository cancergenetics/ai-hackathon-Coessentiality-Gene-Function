"""Toy tests for src/predictor.py: S, supporting partners, hypergeometric p (vs a direct count), matched genes,
empirical p, reportability, ranking and most-specific pruning. Expected values worked out by hand.

Run: .env/bin/python -I -m pytest -q tests/test_predictor.py
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp
from scipy.stats import hypergeom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import predictor as pr  # noqa: E402
from src.neighbours import Neighbours  # noqa: E402

# 10 genes, 3 terms. t0 = {1,2,3}, t1 = {1,2,3,4,5} (parent of t0), t2 = {6,7}. Gene 0 = query (unannotated);
# gene 8, 9 unannotated (not in annotated background).
A = sp.csr_matrix(np.array([[0, 0, 0],
                            [1, 1, 0], [1, 1, 0], [1, 1, 0],
                            [0, 1, 0], [0, 1, 0],
                            [0, 0, 1], [0, 0, 1],
                            [0, 0, 0], [0, 0, 0]], dtype=float))
# N(0) = [1, 2, 6, 8] with z = [3, 2, 1.5, -0.5]
NB = Neighbours(rows=np.array([0]), ids=np.array([[1, 2, 6, 8]]), z=np.array([[3.0, 2.0, 1.5, -0.5]]), K=4)


def test_term_scores_by_hand():
    ts = pr.term_scores(NB, A)
    S = ts.S.toarray()[0]
    assert S.tolist() == [5.0, 5.0, 1.5]
    assert ts.n_sup.toarray()[0].tolist() == [2, 2, 1]
    assert ts.x.toarray()[0].tolist() == [2, 2, 1]
    assert ts.n_draw.tolist() == [3]                        # gene 8 not in annotated background


def test_negative_z_partner_counts_for_x_not_support():
    nb = Neighbours(rows=np.array([0]), ids=np.array([[1, 2, 3]]), z=np.array([[3.0, 0.0, -1.0]]), K=3)
    ts = pr.term_scores(nb, A)
    assert ts.S.toarray()[0, 0] == 3.0 and ts.n_sup.toarray()[0, 0] == 1 and ts.x.toarray()[0, 0] == 3


def test_hypergeometric_against_direct_formula():
    ts = pr.term_scores(NB, A)
    p = pr.hypergeom_p(ts, A).toarray()[0]
    # background B = genes 1..7 (7 genes), query 0 not in B; n = 3 draws; t0: K=3, x=2; t1: K=5, x=2; t2: K=2, x=1
    for t, (K, x) in enumerate([(3, 2), (5, 2), (2, 1)]):
        assert p[t] == pytest.approx(hypergeom.sf(x - 1, 7, K, 3))
    # same thing by brute-force enumeration for t0
    from itertools import combinations
    draws = list(combinations(range(1, 8), 3))
    assert p[0] == pytest.approx(np.mean([len({1, 2, 3} & set(d)) >= 2 for d in draws]))


def test_hypergeometric_removes_annotated_query():
    """If the query itself is in the annotated background, N and K_t exclude it."""
    nb = Neighbours(rows=np.array([1]), ids=np.array([[2, 3, 6]]), z=np.ones((1, 3)), K=3)
    ts = pr.term_scores(nb, A)
    p = pr.hypergeom_p(ts, A).toarray()[0]
    assert p[0] == pytest.approx(hypergeom.sf(1, 6, 2, 3))   # N = 7 - 1, K_t0 = 3 - 1, x = 2


def test_score_table_ranks_and_reportability():
    ts = pr.term_scores(NB, A)
    tab = pr.score_table(ts, pr.hypergeom_p(ts, A), term_names=["t0", "t1", "t2"])
    tab = tab.set_index("term_id")
    assert not tab.loc["t2", "reportable"]                  # only one supporting partner
    assert np.isnan(tab.loc["t2", "rank_R1"])
    # R1: S ties (5 = 5) broken by term index -> t0 first; R2: t0 has the smaller p
    assert tab.loc["t0", "rank_R1"] == 1 and tab.loc["t1", "rank_R1"] == 2
    assert tab.loc["t0", "rank_R2"] == 1


def test_most_specific():
    anc = {"t0": {"t0", "t1"}, "t1": {"t1"}, "t2": {"t2"}}
    assert pr.most_specific(["t1", "t2", "t0"], anc) == ["t2", "t0"]
    assert pr.most_specific(["t2", "t1"], anc) == ["t2", "t1"]
    assert pr.most_specific(["t1", "t0"], lambda t: anc[t]) == ["t0"]


def test_matching_strict_relaxed_and_exclusions():
    rng = np.random.default_rng(0)
    G = 400
    cov = pd.DataFrame(dict(mean=rng.normal(size=G), log_sd=rng.normal(size=G), nan_fraction=np.zeros(G)))
    cov.loc[0] = [0.0, 0.0, 0.0]
    pool = np.ones(G, bool)
    arm = np.r_[np.zeros(10, int), np.ones(G - 10, int)]
    nb = Neighbours(rows=np.array([0]), ids=np.array([[11, 12]]), z=np.ones((1, 2)), K=2)
    m = pr.match_genes(cov, [0], pool, M=50, caliper=0.2, mode="strict", nb=nb, arm=arm,
                       paralogues={0: [13]}, extra={0: [14]})
    got = m.matches[0]
    assert not np.isin(got, [0, 11, 12, 13, 14, *range(10)]).any()
    sd = cov.values.std(0)
    assert (np.abs(cov.values[got, :2]) <= 0.2 * sd[:2] + 1e-12).all()
    assert len(got) == m.n_admissible[0] < 50              # caliper binds: fewer than M
    r = pr.match_genes(cov, [0], pool, M=50, caliper=0.2, mode="relaxed")
    assert len(r.matches[0]) == 50 and r.n_outside_caliper[0] > 0
    d = np.einsum("ij,jk,ik->i", cov.values[r.matches[0]], np.linalg.pinv(np.cov(cov.values, rowvar=False)),
                  cov.values[r.matches[0]])
    assert (np.diff(d) >= -1e-12).all()                     # nearest first


def test_global_without_replacement_and_balance():
    rng = np.random.default_rng(1)
    G = 300
    cov = pd.DataFrame(dict(mean=rng.normal(size=G), log_sd=rng.normal(size=G), nan_fraction=rng.random(G) * .1))
    q = np.arange(20)
    pool = np.ones(G, bool)
    pool[q] = False
    m = pr.match_genes(cov, q, pool, M=5, caliper=None, global_without_replacement=True)
    allm = np.concatenate(list(m.matches.values()))
    assert len(allm) == 100 and len(np.unique(allm)) == 100
    b = pr.balance(cov, q, m)
    assert set(b.covariate) == {"mean", "log_sd", "nan_fraction"}
    assert (b.smd.abs() < 0.5).all()


def test_empirical_p_by_hand():
    # S_all for 4 genes x 1 term: query 0 has S = 2; matches 1, 2, 3 with S = 3, 2, 0; gene 3 annotated -> dropped
    S_all = sp.csr_matrix(np.array([[2.0], [3.0], [2.0], [0.0]]))
    Ann = sp.csr_matrix(np.array([[0.0], [0.0], [0.0], [1.0]]))
    ts = pr.TermScores(rows=np.array([0]), S=S_all[[0]], n_sup=S_all[[0]], x=S_all[[0]], n_draw=np.array([2]))
    m = pr.Matches(matches={0: np.array([1, 2, 3])}, n_admissible={}, n_outside_caliper={}, M=3, caliper=None,
                   mode="relaxed")
    terms, p, Mt = pr.empirical_p(ts, S_all, m, Ann)[0]
    assert Mt.tolist() == [2] and p[0] == pytest.approx((1 + 2) / (1 + 2))
    terms, p, Mt = pr.empirical_p(ts, S_all, m, Ann, drop_annotated=False)[0]
    assert Mt.tolist() == [3] and p[0] == pytest.approx(3 / 4)
    _, pr_, _ = pr.empirical_p(ts, S_all, m, Ann, randomize_ties=True, seed=0)[0]
    assert 1 / 3 <= pr_[0] <= 1.0                           # (1 + U * 2) / 3


def test_empirical_p_uniform_under_exchangeability():
    """Query and matched S drawn from the same continuous distribution with point mass at 0 -> randomized p is
    Uniform(0,1); conservative p is super-uniform."""
    from scipy.stats import kstest
    rng = np.random.default_rng(2)
    nq, M = 2000, 99
    pr_all, pc_all = [], []
    for _ in range(nq):
        s = rng.exponential(size=M + 1) * (rng.random(M + 1) < 0.3)
        S_all = sp.csr_matrix(s[:, None])
        ts = pr.TermScores(rows=np.array([0]), S=S_all[[0]], n_sup=S_all[[0]], x=S_all[[0]], n_draw=np.array([1]))
        m = pr.Matches(matches={0: np.arange(1, M + 1)}, n_admissible={}, n_outside_caliper={}, M=M, caliper=None,
                       mode="relaxed")
        ann = sp.csr_matrix((M + 1, 1))
        pr_all.append(pr.empirical_p(ts, S_all, m, ann, all_terms=True, randomize_ties=True,
                                     seed=int(rng.integers(1 << 30)))[0][1][0])
        pc_all.append(pr.empirical_p(ts, S_all, m, ann, all_terms=True)[0][1][0])
    assert kstest(pr_all, "uniform").pvalue > 0.01
    assert np.mean(np.array(pc_all) <= 0.05) <= 0.05 + 0.015
