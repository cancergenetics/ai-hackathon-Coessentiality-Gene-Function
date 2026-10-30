import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("ja", Path(__file__).resolve().parents[1] / "scripts/52_judge_analysis.py")
ja = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ja)


def test_signflip_known_answers():
    assert ja.signflip_p([1, 1, 1])[0] == 1 / 8          # all positive: only the observed pattern is as extreme
    assert ja.signflip_p([1, -1])[0] == 0.75             # sum 0: 3 of 4 patterns >= 0
    assert ja.signflip_p([0, 0])[0] == 1.0               # no informative genes
    p, n = ja.signflip_p([2, 0, 1])
    assert n == 2 and p == 0.25


def test_kappa():
    a = np.array([1, 0, -1, 1]); assert ja.kappa(a, a) == 1.0
    b = np.array([1, 1, 1, 1]); assert ja.kappa(b, b) != ja.kappa(a, b)
