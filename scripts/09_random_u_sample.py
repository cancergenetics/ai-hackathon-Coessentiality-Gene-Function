"""Random sample of 50 pre-registered U genes (seed 0) shared by the curation-lag audit (DESIGN §1.5) and the
random arm of the LLM recall probe (§6.2). Sampling frame: all U genes, sorted by hgnc_id."""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
U = pd.read_csv(ROOT / "preregistration/uncharacterised_genes.tsv", sep="\t")
U = U.assign(_n=U.hgnc_id.str.replace("HGNC:", "").astype(int)).sort_values("_n")
idx = np.random.default_rng(0).choice(len(U), size=50, replace=False)
S = U.iloc[np.sort(idx)][["hgnc_id", "symbol"]]
hub = pd.read_csv(ROOT / "results/ids/hgnc_hub.tsv", sep="\t", dtype=str)
cols = ["hgnc_id", "prev_symbols", "alias_symbols", "uniprot_ids", "location"]
S = S.merge(hub[cols], on="hgnc_id", how="left")
S.to_csv(ROOT / "results/audit/random50_U_sample.tsv", sep="\t", index=False)
print(len(S), list(S.columns))
