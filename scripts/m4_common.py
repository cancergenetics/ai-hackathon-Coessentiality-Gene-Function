"""m4_common.py -- shared helpers for the M4 computation scripts (scripts/10_*.py ... 16_*.py).

Not a numbered pipeline step. Every numbered script calls ``gate_check()`` (src/gate.py::check with the tool commit
and the DepMap gene-effect checksum) before reading pairwise DepMap information, and writes a run manifest with
``write_manifest``.

Gene index convention: the order of the DepMap CRISPRGeneEffect.csv columns (= the tool model's gene order); every
column maps to exactly one HGNC Approved record through results/ids/hgnc_hub.tsv (depmap_column, Entrez-based).
"""
from __future__ import annotations

import json
import os
import platform
import re
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from src import gate  # noqa: E402

TOOL_DIR = ROOT / "external" / "coessentiality"
TOOL_COMMIT = "3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf"
EFFECT_CSV = "data/raw/depmap/CRISPRGeneEffect.csv"
HUB_TSV = "results/ids/hgnc_hub.tsv"
U_TSV = "preregistration/uncharacterised_genes.tsv"
PARALOGUE_TSV = "data/raw/ensembl/ensembl116_human_paralogues.tsv"
DERIVED = ROOT / "data" / "derived"
FULL_DIR = DERIVED / "matrices" / "zavg_full"


def gate_check(data_files=(EFFECT_CSV,)) -> dict:
    """src/gate.py::check() with the tool commit and raw-data checksums (raises GateError)."""
    g = gate.check(tool_dir=str(TOOL_DIR), tool_commit=TOOL_COMMIT, data_files=list(data_files))
    return {k: v for k, v in g.items() if k != "files"} | {"n_freeze_files": len(g["files"])}


def frozen() -> dict:
    """config/frozen.yaml as {section: {key: entry}} (entries are one-line JSON flow mappings; no PyYAML needed,
    same parser as scripts/07_check_frozen_yaml.py)."""
    out, group = {}, None
    for line in (ROOT / "config" / "frozen.yaml").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            group = line.strip().rstrip(":")
            out[group] = {}
            continue
        k, _, v = line.strip().partition(": ")
        out[group][k] = json.loads(v)
    return out


def fz(section: str, key: str):
    return frozen()[section][key]["value"]


def peak_rss_gb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(r / (1e9 if platform.system() == "Darwin" else 1e6), 3)


def git_head() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def sha(path) -> str:
    return gate.sha256_file(ROOT / path)


def write_manifest(path, script: str, gate_info: dict, inputs, seed, t0: float, extra: dict | None = None) -> dict:
    """Run manifest: script, git HEAD, gate summary, SHA-256 of inputs, seed, runtime, peak RSS, extras."""
    man = dict(script=script, created=time.strftime("%Y-%m-%dT%H:%M:%S"), git_head=git_head(), gate=gate_info,
               inputs={str(p): sha(p) for p in inputs}, seed=seed,
               runtime_s=round(time.perf_counter() - t0, 1), peak_rss_gb=peak_rss_gb(),
               python=sys.version.split()[0], platform=platform.platform())
    if extra:
        man.update(extra)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(man, indent=1, default=str) + "\n")
    return man


# ------------------------------------------------------------------------------------------ data
def load_effect() -> pd.DataFrame:
    """CRISPRGeneEffect (lines x genes) as float32, cached under data/derived/depmap/ (keyed by the CSV SHA-256).
    Values equal coessential.data.load_depmap (pandas read, cast to float32)."""
    cache = DERIVED / "depmap"
    h = sha(EFFECT_CSV)
    npy, meta = cache / "effect_f32.npy", cache / "effect_meta.json"
    if npy.exists() and meta.exists():
        m = json.loads(meta.read_text())
        if m.get("sha256") == h:
            X = np.load(npy)
            return pd.DataFrame(X, index=pd.Index(m["lines"], name="ModelID"), columns=pd.Index(m["genes"]))
    df = pd.read_csv(ROOT / EFFECT_CSV, index_col=0)
    X = df.values.astype(np.float32)
    cache.mkdir(parents=True, exist_ok=True)
    np.save(npy, X)
    meta.write_text(json.dumps(dict(sha256=h, lines=[str(x) for x in df.index], genes=list(df.columns))))
    return pd.DataFrame(X, index=pd.Index([str(x) for x in df.index], name="ModelID"), columns=df.columns)


def load_hub() -> pd.DataFrame:
    return pd.read_csv(ROOT / HUB_TSV, sep="\t", dtype=str, keep_default_na=False, na_values=[""])


def gene_index(columns) -> pd.DataFrame:
    """One row per DepMap column (matrix order): matrix_index, depmap_column, hgnc_id, symbol, scorable, location,
    ensembl_gene_id, in_universe. Raises if a column has no or several HGNC records."""
    hub = load_hub()
    m = hub[hub.depmap_column.notna()].set_index("depmap_column")
    if m.index.duplicated().any():
        raise ValueError("duplicated depmap_column in hub")
    cols = pd.Index(columns)
    miss = cols.difference(m.index)
    if len(miss):
        raise ValueError(f"{len(miss)} DepMap columns without an HGNC record, e.g. {list(miss[:3])}")
    t = m.loc[cols, ["hgnc_id", "symbol", "scorable", "location", "ensembl_gene_id", "in_universe"]]
    t = t.reset_index(drop=True)
    t.insert(0, "depmap_column", np.asarray(cols, dtype=object))
    t["scorable"] = t.scorable.astype(str) == "True"
    t["in_universe"] = t.in_universe.astype(str) == "True"
    t.insert(0, "matrix_index", np.arange(len(t)))
    return t


_ARM = re.compile(r"^(\d{1,2}|X|Y)\s*(p|q)")


def arm_of(location) -> tuple[str | None, str]:
    """Chromosome arm from an HGNC cytogenetic location -> (arm label or None, rule).

    '17q24.3' -> '17q'; ranges ('1p36.33-p36.32') -> arm of the first band; a range crossing the centromere
    ('10p11.21-q11.21') or a PAR location ('Xp22.33 and Yp11.2') -> arm of the first band, rule recorded;
    'mitochondria' -> 'MT' (the mitochondrial genome is treated as one arm); anything else (no p/q: 'X', '19 not on
    reference assembly', 'reserved', empty) -> None = unknown (no same-arm exclusion)."""
    if not isinstance(location, str) or not location.strip():
        return None, "missing"
    s = location.strip()
    if s.lower().startswith("mitochondri"):
        return "MT", "mitochondria"
    m = _ARM.match(s)
    if not m:
        return None, "no_arm"
    arm = m.group(1) + m.group(2)
    rest = s[m.end():]
    if " and " in s:
        return arm, "multi_location_first"
    if "-" in rest:
        other = re.findall(r"[-]\s*(?:\d{1,2}|X|Y)?(p|q)", rest)
        if other and any(o != m.group(2) for o in other):
            return arm, "spans_centromere_first"
    if "cen" in rest:
        return arm, "spans_centromere_first"
    return arm, "band"


def arms_for(index: pd.DataFrame) -> pd.DataFrame:
    a = [arm_of(x) for x in index.location]
    return pd.DataFrame(dict(arm=[x[0] for x in a], arm_rule=[x[1] for x in a]), index=index.index)


def paralogue_map(index: pd.DataFrame) -> dict:
    """{matrix position: sorted int array of matrix positions of Ensembl 116 paralogues (all homology types, as in
    the pre-registered tandem-cluster stratum)}; symmetric; cached in data/derived/."""
    cache = DERIVED / "paralogues_by_matrix_index.npz"
    key = sha(PARALOGUE_TSV) + "|" + sha(HUB_TSV)
    if cache.exists():
        z = np.load(cache, allow_pickle=False)
        if str(z["key"]) == key and len(z["ptr"]) == len(index) + 1:
            ptr, ids = z["ptr"], z["ids"]
            return {i: ids[ptr[i]:ptr[i + 1]] for i in range(len(index)) if ptr[i + 1] > ptr[i]}
    p = pd.read_csv(ROOT / PARALOGUE_TSV, sep="\t", usecols=[0, 2], dtype=str)
    p.columns = ["a", "b"]
    p = p.dropna()
    ens = index.dropna(subset=["ensembl_gene_id"])
    pos = pd.Series(ens.matrix_index.values, index=ens.ensembl_gene_id.values)
    pos = pos[~pos.index.duplicated(keep=False)]
    a, b = pos.reindex(p.a).values, pos.reindex(p.b).values
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok].astype(np.int64), b[ok].astype(np.int64)
    a, b = np.r_[a, b], np.r_[b, a]
    keep = a != b
    pairs = np.unique(np.c_[a[keep], b[keep]], axis=0)
    n = len(index)
    counts = np.bincount(pairs[:, 0], minlength=n)
    ptr = np.r_[0, np.cumsum(counts)]
    ids = pairs[:, 1]
    np.savez(cache, key=np.array(key), ptr=ptr, ids=ids)
    return {i: ids[ptr[i]:ptr[i + 1]] for i in range(n) if ptr[i + 1] > ptr[i]}


def load_full_index() -> pd.DataFrame:
    """genes.tsv of the full zavg_BEF matrix (written by scripts/10_full_matrix.py)."""
    return pd.read_csv(FULL_DIR / "genes.tsv", sep="\t", dtype={"gene": str, "hgnc_id": str})


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
