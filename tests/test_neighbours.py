"""Toy tests for src/neighbours.py: self / background / same-arm / paralogue exclusion, NaN handling, ties, padding.

Run: .env/bin/python -I -m pytest -q tests/test_neighbours.py
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import neighbours as nbm  # noqa: E402


def matrix():
    """6 genes. Hand-made symmetric scores with a NaN diagonal (as stored)."""
    S = np.array([[np.nan, 5, 4, 3, 2, 1],
                  [5, np.nan, 1, 1, 1, 6],
                  [4, 1, np.nan, 2, 2, np.nan],
                  [3, 1, 2, np.nan, 0, 0],
                  [2, 1, 2, 0, np.nan, 0],
                  [1, 6, np.nan, 0, 0, np.nan]], dtype=np.float32)
    return S


def test_self_never_neighbour_even_with_nan_diagonal():
    S = matrix()
    nb = nbm.top_k(S, K=5)
    for r, ids in zip(nb.rows, nb.ids):
        assert r not in ids[ids >= 0]
    assert list(nb.ids[0]) == [1, 2, 3, 4, 5]
    nbm.assert_valid(nb)


def test_nan_scores_are_never_selected_and_padding():
    S = matrix()
    nb = nbm.top_k(S, K=5, rows=[2])
    assert list(nb.ids[0]) == [0, 3, 4, 1, -1]          # gene 5 has NaN score with gene 2; ties 3,4 by index
    assert np.isnan(nb.z[0, 4])


def test_background_restriction():
    S = matrix()
    bg = np.array([1, 0, 1, 1, 1, 1], bool)
    nb = nbm.top_k(S, K=2, bg=bg)
    nbm.assert_valid(nb, bg=bg)
    assert list(nb.ids[0]) == [2, 3]
    assert list(nb.ids[1]) == [5, 0]                    # non-BG query still gets BG neighbours


def test_same_arm_and_paralogue_exclusion():
    S = matrix()
    arm = nbm.arm_codes(["1p", "1p", "2q", None, "2q", ""])
    assert list(arm) == [0, 0, 1, -1, 1, -1]
    par = nbm.index_sets({"g0": ["g2"], "g9": ["g0"]}, [f"g{i}" for i in range(6)])
    assert set(par) == {0} and list(par[0]) == [2]
    nb = nbm.top_k(S, K=2, arm=arm, paralogues=par)
    nbm.assert_valid(nb, arm=arm, paralogues=par)
    assert list(nb.ids[0]) == [3, 4]                    # 1 same arm, 2 paralogue
    assert list(nb.ids[3]) == [0, 2]                    # unknown arm: no arm exclusion
    assert list(nb.ids[2]) == [0, 3]                    # 4 same arm (2q)


def test_extra_exclusion_and_block_source_equivalence():
    rng = np.random.default_rng(0)
    A = rng.standard_normal((50, 50)).astype(np.float32)
    A = (A + A.T) / 2
    np.fill_diagonal(A, np.nan)
    extra = {0: np.array([int(np.nanargmax(A[0]))])}

    class Src:
        shape = A.shape

        def iter_blocks(self, rows):
            for s in range(0, len(rows), 7):
                r = np.asarray(rows[s:s + 7])
                yield r, A[r].astype(np.float64)

    a = nbm.top_k(A, K=10, extra=extra, block=13)
    b = nbm.top_k(Src(), K=10, extra=extra)
    assert np.array_equal(a.ids, b.ids)
    assert extra[0][0] not in a.ids[0]
    nbm.assert_valid(a)
    df = a.to_frame([f"g{i}" for i in range(50)])
    assert len(df) == 500 and df["query"].iloc[0] == "g0"


def test_source_is_not_modified():
    S = matrix()
    before = S.copy()
    nbm.top_k(S, K=3, bg=np.ones(6, bool), arm=np.zeros(6, int) - 1)
    assert np.array_equal(S, before, equal_nan=True)


def test_assert_valid_catches_self():
    nb = nbm.Neighbours(rows=np.array([0]), ids=np.array([[0, 1]]), z=np.array([[2.0, 1.0]]), K=2)
    with pytest.raises(AssertionError):
        nbm.assert_valid(nb)
