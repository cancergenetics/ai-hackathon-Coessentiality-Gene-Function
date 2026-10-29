"""10_full_matrix.py -- full zavg_BEF matrix on DepMap 26Q3 (DESIGN.md v2.3 §2.2, §8).

Tool: external/coessentiality @ 3c684c9, ``CoessentialityModel`` with the published configuration
(``src.coess_matrix.PUBLISHED_CONFIG`` = ``Config()``, unmodified), fitted on every line and every column of
data/raw/depmap/CRISPRGeneEffect.csv. The matrix (float32, upper triangle = tool block value, lower = mirror,
diagonal NaN) is written to data/derived/matrices/zavg_full/zavg_BEF.npy (git-ignored) with genes.tsv (matrix order =
DepMap column order; hgnc_id via results/ids/hgnc_hub.tsv; background flag, NaN fraction, mean, SD from the model).
Only zavg_BEF is stored densely; z_B/z_E/z_F for reported pairs come from the tool's pair API (§2.2).

Verification: stored values vs the tool's pair API ``model.zavg`` on 100k random pairs (max abs diff).

Outputs: data/derived/matrices/zavg_full/{zavg_BEF.npy, genes.tsv, manifest.json, run_manifest.json};
results/matrices/zavg_full_manifest.json (tool manifest + run manifest, without the 1,361 line IDs list, which is
kept in the derived manifest) and results/matrices/zavg_full_genes.tsv.
Run: .env/bin/python -I scripts/10_full_matrix.py
"""
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

t0 = time.perf_counter()
g = C.gate_check()
C.log(f"gate OK: tag {g['tag_commit'][:10]}, tool {g['tool_commit'][:10]}")

import numpy as np  # noqa: E402

from src import coess_matrix as cm  # noqa: E402

effect = C.load_effect()
idx = C.gene_index(effect.columns)
C.log(f"effect {effect.shape}")
assert cm.is_published_config(cm.PUBLISHED_CONFIG)
fm = cm.fit_model(effect, cm.PUBLISHED_CONFIG)
assert not fm.dropped_genes, fm.dropped_genes
extra = idx.set_index("depmap_column")[["hgnc_id", "symbol", "scorable"]]
man = cm.write_tool_matrices(fm, C.FULL_DIR, kinds=("zavg_BEF",), extra_gene_columns=extra, hash_outputs=True,
                             log=C.log)
C.log("verifying against the pair API")
ver = cm.verify_tool_matrices(fm, C.FULL_DIR, n_pairs=100_000, seed=0)
assert ver["zavg_BEF"]["max_abs_diff"] < 1e-4 and ver["zavg_BEF"]["n_nonfinite_mismatch"] == 0, ver

gt = C.load_full_index()
assert (gt.gene.values == np.asarray(effect.columns)).all()
assert gt.hgnc_id.notna().all() and not gt.hgnc_id.duplicated().any()
summary = dict(n_genes=len(gt), n_bg=int(gt.bg.sum()), K_tool=man["K_tool"], n_lines=man["n_lines"],
               n_scorable=int(gt.scorable.sum()), n_scorable_bg=int((gt.scorable & (gt.bg == 1)).sum()),
               nan_fraction_gt0=int((gt.nan_fraction > 0).sum()))
run = C.write_manifest(C.FULL_DIR / "run_manifest.json", "scripts/10_full_matrix.py", g,
                       [C.EFFECT_CSV, C.HUB_TSV], seed=cm.PUBLISHED_CONFIG.seed, t0=t0,
                       extra=dict(verification_pair_api=ver, summary=summary))

out = C.ROOT / "results" / "matrices"
out.mkdir(parents=True, exist_ok=True)
tool_man = json.loads((C.FULL_DIR / "manifest.json").read_text())
tool_man["lines"] = f"{len(tool_man['lines'])} line IDs (see data/derived/matrices/zavg_full/manifest.json)"
(out / "zavg_full_manifest.json").write_text(json.dumps(dict(tool_manifest=tool_man, run_manifest=run), indent=1,
                                                        default=str) + "\n")
shutil.copy(C.FULL_DIR / "genes.tsv", out / "zavg_full_genes.tsv")
C.log(json.dumps(summary) + f" verification {ver}; runtime {run['runtime_s']} s, peak RSS {run['peak_rss_gb']} GB")
