"""Toy tests for src/vocab.py: V2 row rules (NOT, colocalizes_with, evidence, aspect, alt_id/obsolete, scorable),
propagation, candidate window, IPI with/from leakage rule, LOO query removal, sparse-correction scoring against a
brute-force re-propagation (predictor functions on the explicit per-query membership), label shuffle.

Run: .env/bin/python -I -m pytest -q tests/test_vocab.py
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import knownness as kn  # noqa: E402
from src import vocab  # noqa: E402
from src.neighbours import Neighbours  # noqa: E402

OBO = """format-version: 1.2
data-version: toy

[Term]
id: GO:0008150
name: biological_process
namespace: biological_process

[Term]
id: GO:0000001
name: tA
namespace: biological_process
is_a: GO:0008150

[Term]
id: GO:0000002
name: tB
namespace: biological_process
is_a: GO:0000001
alt_id: GO:0000099

[Term]
id: GO:0000003
name: tC
namespace: biological_process
relationship: part_of GO:0000001

[Term]
id: GO:0000004
name: old
namespace: biological_process
is_obsolete: true

[Term]
id: GO:0000005
name: old2
namespace: biological_process
is_obsolete: true
replaced_by: GO:0000003

[Term]
id: GO:0005575
name: cellular_component
namespace: cellular_component

[Term]
id: GO:0000010
name: cc
namespace: cellular_component
is_a: GO:0005575
"""


def gaf_row(acc, go, ev="IDA", qual="involved_in", aspect="P", wf=""):
    return dict(db="UniProtKB", acc=acc, symbol="x", qualifier=qual, go_id=go, reference="PMID:1", evidence=ev,
                with_from=wf, aspect=aspect, db_name="", synonyms="", db_type="protein", taxon="taxon:9606",
                date="20200101", assigned_by="X", extension="", gene_product_form="")


ONTO = kn.GoOntology.from_obo(OBO, "toy")
GENES = [f"HGNC:{i}" for i in range(6)]
ACC = {f"P{i}": {f"HGNC:{i}"} for i in range(6)}
SCOR = np.array([True, True, True, True, True, False])


def small_v2(lo=1, hi=10):
    rows = [gaf_row("P0", "GO:0000002"),                                   # kept -> tB, tA
            gaf_row("P0", "GO:0000003", qual="NOT|involved_in"),             # NOT -> dropped
            gaf_row("P1", "GO:0000099"),                                    # alt_id -> tB
            gaf_row("P1", "GO:0000003", ev="IEA"),                          # IEA -> dropped
            gaf_row("P2", "GO:0000002", ev="IPI", qual="enables", aspect="F", wf="UniProtKB:P0-2|UniProtKB:P9"),
            gaf_row("P2", "GO:0000005"),                                    # obsolete, replaced_by tC
            gaf_row("P3", "GO:0000004"),                                    # obsolete, no replacement -> dropped
            gaf_row("P3", "GO:0000010", aspect="C"),                        # CC -> dropped
            gaf_row("P3", "GO:0000003", qual="colocalizes_with"),           # colocalizes_with -> dropped
            gaf_row("P4", "GO:0000002", ev="IPI", wf="UniProtKB:P0"),      # IPI naming gene 0 (only row of gene 4)
            gaf_row("P5", "GO:0000002")]                                    # gene 5 not scorable -> dropped
    gaf = pd.DataFrame(rows, columns=kn.GAF_COLS)
    return vocab.build_v2(gaf, ONTO, ACC, GENES, SCOR, lo=lo, hi=hi)


def test_row_rules_and_propagation():
    v = small_v2()
    st = v.stats
    assert st["not_rows_removed"] == 1 and st["colocalizes_with_rows_removed"] == 1
    assert st["rows_obsolete_dropped"] == 1 and st["rows_alt_id"] == 1 and st["rows_replaced_by"] == 1
    assert st["rows_mapped_not_scorable"] == 1
    assert list(v.terms) == ["GO:0000001", "GO:0000002", "GO:0000003"]       # roots are generic, CC never kept
    M = pd.DataFrame(v.A.toarray(), columns=v.terms).astype(int)
    assert M.loc[0].tolist() == [1, 1, 0]
    assert M.loc[1].tolist() == [1, 1, 0]
    assert M.loc[2].tolist() == [1, 1, 1]                                      # tC via part_of -> tA
    assert M.loc[3].tolist() == [0, 0, 0] and not v.annotated[3]
    assert M.loc[4].tolist() == [1, 1, 0]
    assert M.loc[5].tolist() == [0, 0, 0]
    assert v.size.tolist() == [4, 4, 1]
    assert v.rows.loc[v.rows.evidence == "IPI", "partners"].tolist() == [(0,), (0,)]   # P9 unmapped, isoform stripped


def test_ipi_rule_and_loo():
    v = small_v2()
    rem = v.removal(0, loo=True)
    # gene 0's own row removed; gene 2 loses nothing from IPI tB? gene 2 keeps tC -> tA, loses tB; gene 4 loses all
    assert sorted(rem.rows) == [0, 2, 4]
    assert v.terms[rem.rows[2]].tolist() == ["GO:0000002"]
    assert v.terms[rem.rows[4]].tolist() == ["GO:0000001", "GO:0000002"]
    assert rem.lost_bg == {4}
    sz = v.query_sizes(rem)
    assert sz.tolist() == [2, 1, 1]
    A_g, B_g = v.explicit_view(0, loo=True)
    assert (np.asarray(A_g.sum(0)).ravel() == sz).all()
    assert B_g.tolist() == [False, True, True, False, False, False]
    # not-LOO: query row untouched
    rem2 = v.removal(0, loo=False)
    assert sorted(rem2.rows) == [2, 4]
    # a query nobody names: only its own row
    assert sorted(v.removal(1, loo=True).rows) == [1] and v.removal(1, loo=False).rows == {}


def random_toy(seed, G=70, n_terms=30, K=6, M=15):
    rng = np.random.default_rng(seed)
    lines = ["format-version: 1.2", "", "[Term]", "id: GO:0008150", "name: bp", "namespace: biological_process", ""]
    ids = [f"GO:{i:07d}" for i in range(1, n_terms + 1)]
    for i, t in enumerate(ids):
        lines += ["[Term]", f"id: {t}", f"name: t{i}", "namespace: biological_process"]
        if i == 0 or rng.random() < 0.2:
            lines.append("is_a: GO:0008150")
        else:
            ps = rng.choice(i, size=min(i, rng.integers(1, 3)), replace=False)
            for j, p in enumerate(ps):
                lines.append(f"is_a: {ids[p]}" if j == 0 else f"relationship: part_of {ids[p]}")
        lines.append("")
    onto = kn.GoOntology.from_obo("\n".join(lines), "toy")
    genes = [f"HGNC:{i}" for i in range(G)]
    acc = {f"Q{i}": {f"HGNC:{i}"} for i in range(G)}
    scor = rng.random(G) > 0.05
    rows = []
    for i in range(G):
        for _ in range(rng.integers(0, 5)):
            ev = rng.choice(["IDA", "IPI", "IPI", "IEA", "IMP"])
            wf = ""
            if ev == "IPI":
                wf = "|".join(f"UniProtKB:Q{p}" for p in rng.choice(G, size=rng.integers(1, 3), replace=False))
            rows.append(gaf_row(f"Q{i}", ids[rng.integers(n_terms)], ev=ev, wf=wf))
    gaf = pd.DataFrame(rows, columns=kn.GAF_COLS)
    v = vocab.build_v2(gaf, onto, acc, genes, scor, lo=2, hi=12)
    nid = np.zeros((G, K), np.int64)
    nz = np.zeros((G, K), np.float32)
    for g in range(G):
        nid[g] = rng.choice(np.delete(np.arange(G), g), size=K, replace=False)
        nz[g] = np.sort(rng.normal(1.0, 1.0, K))[::-1].round(3)
    nb = Neighbours(rows=np.arange(G), ids=nid, z=nz, K=K)
    matches = {g: rng.choice(np.setdiff1d(np.arange(G), np.r_[g, nid[g]]), size=M, replace=False)
               for g in range(G)}
    return v, nb, matches


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
@pytest.mark.parametrize("loo", [True, False])
def test_corrected_scoring_equals_bruteforce(seed, loo):
    v, nb, matches = random_toy(seed)
    qs = np.flatnonzero(v.scorable)
    sc = vocab.score_queries(v, nb, matches, qs, loo=loo)
    n_ipi = 0
    for g in qs:
        ref = vocab.explicit_scores(v, nb, matches, int(g), loo=loo)
        got = sc.table[sc.table["query"] == g]
        ref_r, got_r = ref[ref.reportable].set_index("term"), got[got.reportable].set_index("term")
        assert sorted(ref_r.index) == sorted(got_r.index), g
        assert set(ref.term) == set(got.term), g
        for c in ("S", "p_hyper", "p_emp") if len(ref_r) else ():
            np.testing.assert_allclose(got_r.loc[ref_r.index, c].values.astype(float),
                                       ref_r[c].values.astype(float), rtol=1e-9, atol=1e-12, err_msg=f"{g} {c}")
        for c in ("n_sup", "x", "M_t", "rank_R1", "rank_R2", "rank_R3"):
            assert (got_r.loc[ref_r.index, c].values == ref_r[c].values).all(), (g, c)
        A_g, _ = v.explicit_view(int(g), loo)
        assert (sc.sizes[list(qs).index(g)] == np.asarray(A_g.sum(0)).ravel()).all()
        n_ipi += sc.info.set_index("query").loc[g, "n_ipi_genes"] > 0
    assert n_ipi > 5                                                     # the IPI rule was exercised


def test_label_shuffle_preserves_sizes():
    v, nb, matches = random_toy(5, G=200)
    p, tab = v.permuted(seed=0, block=5)
    assert (np.asarray(p.A.sum(0)).ravel() == v.size).all()
    assert (p.annotated == v.annotated).all()
    assert tab.moved.mean() > 0.5
    assert np.abs(tab.count_after - tab.count_before).max() <= tab.count_before.max()
    assert not p.ipi_rule and p.removal(int(np.flatnonzero(v.annotated)[0])).rows.keys() <= {
        int(np.flatnonzero(v.annotated)[0])}
