# PROVENANCE — how and when the pre-registered gene list was built

**What is frozen**: `preregistration/uncharacterised_genes.tsv` (U, 4,924 genes; 4,275 with a DepMap column; 4,271
scorable), `preregistration/CRITERIA.md`, and the files listed in `preregistration/FREEZE.sha256`, at git tags
`preregistration-v1` and `design-frozen` (same commit). DESIGN.md v2.3 §1 is the specification.

**Chronology (2026-10-29)**
1. Annotation datasets downloaded and checksummed (commit a25e6fb); per-gene knownness feature table built from
   annotation only (3eabdba).
2. DESIGN v1 → review round 1 (six reviewers) → v2/v2.1 → review round 2 (five reviewers) → v2.2 → disposition
   check → v2.3 (this freeze).
3. While the design was under review, U was **built** (not frozen) by `scripts/03_build_preregistration.py` using
   `src/knownness.py::d1()` — annotation data only. The only DepMap content read before the freeze: the CSV header
   (gene columns) and single-gene marginal summaries (per-gene mean, SD, NaN fraction, fraction of lines < −0.5;
   `results/preregistration/depmap_gene_summaries.tsv`) used for reporting strata, plus per-gene expression summaries.
   **No gene–gene (pairwise) quantity was computed on DepMap data before the freeze**, and the tool's genome-wide
   predictions were hidden by sparse checkout (`scripts/verify_sparse.sh`).
4. Strata (§1.4) were computed in the same script run as the list. They do not affect membership of U: an independent
   agent re-derived U and H from raw files with its own code (no access to `src/knownness.py`) and reproduced U
   (4,924), H (820 genes, 5,965 targets) and every per-gene criterion column exactly
   (`verify/prereg_verification.md`; verdict "VERIFIED WITH MINOR DISCREPANCIES (explained)" — the only differences
   arise if the 7-term instead of the documented 22-term generic-binding list is used: 17 U genes, 1 H gene; the
   22-term list in code is the frozen definition).
5. Criteria edits after the list was first built: DESIGN v2.2/v2.3 changed no criterion of §1.2. TAS/IC were counted as
   known from v2 onward (before the first build). Looks at |U| before the freeze: annotation-only estimate (~5.2k, PI
   review round 1), first build 4,924; no criterion was changed after either look.
6. Hold-out sizing (`scripts/04_holdout_sizing.py`), circularity query (`scripts/05_circularity_query.py`) and power
   simulation (`scripts/08_power_simulation.py`) are annotation-only and were run before the freeze.

**D1 implementation note**: `scripts/02_gene_knownness_table.py` columns are descriptive features only (its
"experimental" counts include HTP codes and exclude TAS/IC); the frozen definition is `src/knownness.py::d1()`, whose
output is reproduced by the independent re-derivation `verify/rederive_prereg.py`.

**Freeze commit**: recorded in RESEARCH_TREE.md (decision note D2) together with the SHA-256 of `FREEZE.sha256`.
