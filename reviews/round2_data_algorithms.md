# Round 2 review: data, algorithms, compute (DESIGN v2.1)

No DepMap values opened; nothing run on DepMap.

## 1. Round-1 must-fixes

Closed: hub, QC tables, unmodified tool API, diagonal/BG assertions, blockwise GLS/Pearson, temporal annotation rules, hu.MAP strata, pair scores, stratified halves, size fallbacks.

Residual (minor):
- **A. Split-half universe.** `CoessentialityModel.__init__` raises on any all-NaN column (method.py l.126), so the driver must drop those columns first. BG(half) can differ from BG(full): compute R(g) on B* = BG(A) ∩ BG(B) ∩ BG(full), keeping top-60 per gene per half, filtering to B*, then taking the top 25.
- **B. Assessability ties.** Chance overlap is about 0.04 genes, so the 95th percentile of R0 is 0 for most genes and "R > q95" becomes "R > 0" with undefined error. Define p_R = (1 + #{m: R0(g,m) ≥ R(g)})/(1 + M) < 0.05, consistent with the toy test (5% ± 2%).
- **C. Predictor leakage.** v2.1 qualifier rules cover D1 only. Also drop, from the annotation tables used for neighbours, IPI rows whose `with/from` contains the query and CC `colocalizes_with`, identically for LOO, H and U.
- **D. Still deferred:** `sec_ac`/`gene_history` in the hub; retention thresholds as tests; package lock (xlrd, h5py/anndata, networkx; `anndata` is not installed); Complex Portal window 3–300; BG-status matching.

## 2. §5.1b against `data/raw`

Implementable, with these fixes:
1. **BioPlex** (Entrez, pInt) fine. "Measured" = appears as a node (edges only are published).
2. **OpenCell:** ENSG on both ends; edge = row present.
3. **BioGRID:** both organism IDs 9606, `Experimental System Type` = physical, ≥ 1 row with `Throughput` = "Low Throughput".
4. **STRING:** name the file: `physical.links.detailed`, `experimental` ≥ 400. It imports BioGRID/IntAct/BioPlex data; one class, counted once.
5. **Human Cell Map:** 193 baits only, bait–prey pairs; resolve via its own `preys`/`baits` tables (Entrez/HGNC); measured = in `saint` ∪ `not-significant`.
6. **ProteomeHD:** groups like `A0AVT1;A0AVT1-2` are isoforms. Strip isoform suffixes, drop only if > 1 gene remains (the round-1 rule would discard most rows). Pairs are stored once: symmetrise.
7. **CCLE proteomics:** key `Uniprot_Acc`; map lines to ModelID via `Model.csv` `CCLEName`; collapse replicate columns before the ≥ 50 lines rule.
8. **Perturb-seq:** `obs.gene_transcript` parses to ENSG; `obs.fold_expr` (median 0.16, 7% NaN). "Significant knockdown" is undefined; fix it now (e.g. fold_expr ≤ 0.3, ≥ 25 cells). Exclude both genes' own transcripts from profiles (dropped in v2.1).
9. **Chemogenomic:** the ORCS tar holds 1,952 files with **no screen metadata**, and SCORE.1 changes meaning between screens, so Olivieri screens cannot be identified and pooled Pearson is meaningless. Make the class Olivieri `Zscores_28screens` only (internal use). Its strict-OOXML xlsx loads in neither openpyxl nor pandas (empty sheet list); use calamine or LibreOffice conversion, with a loader test. Drop "drug screens" from §5.1.
10. **Support test:** (a) state partners = {g} × (N(g) ∩ t), statistic = supported pair count (round-1 3.3). (b) For continuous sources, match null partners on hubness (mean row-score decile) and, for Perturb-seq, phenotype strength; otherwise essential-module partners win trivially. (c) Class p = Bonferroni minimum over its measured sources, then Holm. (d) §5.2 needs a binary call for continuous sources: row percentile ≥ 95. (e) Burke: pair presence is selected (HuRI ∪ hu.MAP); draw nulls from covered pairs; HuRI itself is absent from `data/raw`. (f) Commit the localisation vocabulary map and define "match" (≥ 1 shared compartment) before U is viewed.

## 3. Compute (24 GB, 8 cores; tool: 137 s, 4.1 GB per run)

**R3 (M=500 × all terms): cheap if done once for all genes.** S_all = W·A (W: 25 non-zeros per gene; A: ≈ 2 M gene–term non-zeros) has about 40 M non-zeros (< 0.5 GB) and takes seconds. Per query, gather the 500 matched rows over its ≈ 2–3 k candidate terms and count S(m,t) ≥ S(g,t): ≈ 1 M comparisons, 5–20 ms. For 25k queries that is 1–2 min per configuration on 8 cores. Allow ≈ 20 configurations (rankers, K, no-exclusion, GLS, Pearson, halves): about 2 h. Compute R3 for all BG genes (the matched-gene null comparator needs the matched gene's own p_emp), store top-200 terms each, and everything else is a lookup. A dense 18k × 15k float32 matrix (1.1 GB) also fits.

**Design change: the target-based exclusion cannot apply to U.** §3.4 excludes matched genes annotated to g's targets, but U genes have none, so the null would differ between calibration and U. Exclude per candidate term (m ∉ t; denominator 1 + M_t), identically everywhere.

**Caliper vs M.** In the Mahalanobis space (mean, log SD, NaN fraction) a 0.2 radius holds about 40 genes at the density peak, not 500 (and not 200). Pre-specify: take the M nearest, report distance and SMD balance, keep the 0.2 caliper only for the 5-match primary comparator, match without replacement within query, and flag genes with fewer than M admissible matches (no R3 call).

**§4.2.** Ten half-runs at ≈ 3–6 min each (about 600 lines): ≤ 1 h serially, peak RSS ≈ 6 GB; no dense half matrices are needed. R0 comes from one sparse product N_A·N_Bᵀ (≈ 11 M non-zeros) read at the matched entries: seconds. Six full matrices need 8 GB of disk.

## 4. New risks

- The ranker is chosen on LOO, whose current annotations include DepMap-derived ones: apply the §3.2.3 circularity flag to LOO targets too.
- p_emp has a floor of 1/501, so ties are frequent: test the ties-by-S rule on the planted-module toy.
- Non-BG (imputed/Nyström) genes: add `low_coverage` as a stratum; exclude from Tier A unless H has such genes.

**Verdict: READY AFTER MINOR CHANGES** — A, B, C; §5.1b items 8–10 of section 2 (knockdown rule, Olivieri-only chemogenomics with loader, support-test definitions); per-term null exclusion; M-nearest matching rule.
