"""m5_common.py -- shared loaders for the M5 calibration scripts (scripts/30_*.py, 31_*.py). Not a pipeline step.

Gene positions = rows of the full zavg_BEF matrix (data/derived/matrices/zavg_full/genes.tsv). N(g) = first K = 25
of the stored top-100 neighbour lists (scripts/13); M(g) = the 500-gene matched lists (scripts/13).
V2 (current) = src/vocab.build_v2 on the current goa_human GAF with the current go-basic.obo and the HGNC/UniProt
accession map of scripts/03-04 (``knownness.build_acc_map``).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

from src import knownness as kn  # noqa: E402
from src import vocab  # noqa: E402
from src.neighbours import Neighbours  # noqa: E402

RAW = C.ROOT / "data" / "raw"
GAF_CUR = "data/raw/go/current/goa_human.gaf.gz"
OBO_CUR = "data/raw/go/current/go-basic.obo"
HGNC = "data/raw/hgnc/hgnc_complete_set.txt"
UNIPROT = "data/raw/uniprot/uniprot_human_reviewed.tsv"
NB_NPZ = "data/derived/neighbours/full_top100.npz"
MATCH_NPZ = "data/derived/matched/matched_lists.npz"
LOO_TSV = "results/loo_sample.tsv"
INPUTS = [GAF_CUR, OBO_CUR, HGNC, UNIPROT, NB_NPZ, MATCH_NPZ, LOO_TSV, "data/derived/matrices/zavg_full/genes.tsv"]


def load_index() -> pd.DataFrame:
    gt = C.load_full_index()
    gt["scorable"] = gt.scorable.astype(str) == "True"
    gt["bg"] = gt.bg.astype(int).astype(bool)
    return gt


def load_neighbours(K: int, G: int) -> Neighbours:
    z = np.load(C.ROOT / NB_NPZ, allow_pickle=False)
    assert (z["rows"] == np.arange(G)).all()
    return Neighbours(rows=np.arange(G), ids=z["ids"][:, :K].astype(np.int64), z=z["z"][:, :K], K=K)


def load_matches() -> dict:
    z = np.load(C.ROOT / MATCH_NPZ, allow_pickle=False)
    q, ids = z["queries"], z["ids"]
    return {int(a): ids[i][ids[i] >= 0].astype(np.int64) for i, a in enumerate(q)}


def load_loo(gt: pd.DataFrame) -> pd.DataFrame:
    loo = pd.read_csv(C.ROOT / LOO_TSV, sep="\t", dtype={"hgnc_id": str})
    assert (gt.hgnc_id.values[loo.matrix_index.values] == loo.hgnc_id.values).all()
    assert gt.scorable.values[loo.matrix_index.values].all()
    return loo


def acc_map() -> dict:
    pc = kn.load_hgnc_pc(str(C.ROOT / HGNC))
    up = pd.read_csv(C.ROOT / UNIPROT, sep="\t", dtype=str, keep_default_na=False)
    return kn.build_acc_map(pc, up)[0]


def build_current_v2(gt: pd.DataFrame, lo: int, hi: int) -> vocab.V2:
    t = time.perf_counter()
    onto = kn.GoOntology.from_obo(str(C.ROOT / OBO_CUR), "current")
    v = vocab.build_v2(str(C.ROOT / GAF_CUR), onto, acc_map(), gt.hgnc_id.values, gt.scorable.values, lo=lo, hi=hi)
    v.stats["obo_data_version"] = onto.release
    C.log(f"V2 current built in {time.perf_counter() - t:.0f} s: {v.stats['n_columns']} columns, "
          f"{v.stats['n_candidate_terms_base']} base candidate terms, B = {v.stats['n_annotated_background']}")
    return v
