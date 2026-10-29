# Round 1 review: data, algorithms, compute

Tool not run; `external/coessentiality/results/` not opened; raw files inspected by header only.

## Assessment

Feasible on the 24 GB / 8-core laptop: the public API (`CoessentialityModel`, `zavg_block`, `all_pairs.score_all_pairs`, `protein_genes`) gives full matrices unmodified (about 3.4 GB, minutes per run). The main risks are not compute but (i) silent identifier/ontology-version errors, (ii) benchmark leakage (hu.MAP tuning, matched-null contamination, IPI "with" columns), (iii) split-half runs that change the background set, (iv) sources lacking the pair-level score §5 assumes.

## 1. Identifier mapping

1.1 **MUST** Build one hub table `hgnc_hub` (key `hgnc_id`) with columns: entrez, ensg, primary and secondary UniProt, cytoband arm, in_matrix, bg, low_coverage, matrix_index. Why: the tool's gene set (`protein_genes`, 18,429) differs from the pre-registered universe (18,370 in DepMap), and matrix order is neither DepMap nor HGNC order. Key everything on `hgnc_id`, assert against `genes.tsv`, never index by position.
1.2 **MUST** Mapping rule per source, no symbol joins except as a last resort: Entrez (BioGRID, BioPlex, Human Cell Map preys, DEMETER2 row ids, ORCS) -> HGNC; ENSG (OpenCell, HPA, Perturb-seq var/obs) -> HGNC `ensembl_gene_id`, fallback ENSG -> Entrez via `ensembl116_gene_coordinates.tsv`; UniProt (hu.MAP, Complex Portal, ProteomeHD, Burke, GAF, CCLE) -> strip isoform/`-PRO_` suffix, then HGNC `uniprot_ids`; STRING ENSP -> ENSG through `aliases` (not `preferred_name`, which lags HGNC by years); Human Cell Map SAINT (symbols, RefSeq NP) via the `preys`/`baits` tables to Entrez. Ambiguity rule (same as the tool's `ambiguous`): an identifier that maps to >1 gene (histones, ProteomeHD protein groups with `;`) is dropped and counted, never expanded or picked.
1.3 **MUST** Each loader writes mapping QC (n ids, mapped, ambiguous, unmapped) to `results/id_map/qc_<source>.tsv`; a retention threshold is a test.
1.4 **SHOULD** Add UniProt `sec_ac.txt` (secondary to primary) and NCBI `gene_history` to the manifest. The 2018 GAF loses 6.7% of accessions under current HGNC; genes wrongly lacking t0 annotations would enter hold-out set H spuriously.
1.5 
## 2. Pre-registration inputs

2.1 **MUST** D1 includes TAS/IC evidence, but `gene_knownness_features.tsv` has no column separating TAS/IC from ISS/ISO/ISA/ISM/IGC/RCA/NAS (`n_comp_BPMF` merges them). D1 as written cannot be computed. Add `n_exp_or_TASIC_informative_BPMF_lowthroughput` in `02_gene_knownness_table.py` before freezing.
2.2 **MUST** Define "scorable" = row in the tool's `genes.tsv`. Report U genes outside it (DepMap-absent, no UniProt, non-BG/low-coverage) as separate not-scorable categories. Make the hash gate read a committed `preregistration/FREEZE.sha256`, and also check the tool commit (3c684c9) and the DepMap SHA-256 in `config/data_checksums.tsv`.

## 3. Data usable as described in §5

3.1 **MUST** Pair-level score per source, specified before viewing predictions: BioPlex (pInt edges), OpenCell (edge), BioGRID (low-throughput physical edge, count), STRING physical `experimental` channel (score; contains orthology transfer and imported BioGRID/IntAct, so same class P, not independent), Human Cell Map (BFDR<=0.01), CCLE proteomics and ProteomeHD (computed pairwise Pearson with >=30 shared lines / supplied score), Perturb-seq (Pearson of perturbation profiles over measured genes, excluding both perturbed genes' own transcripts; only perturbed genes are covered: ~11k K562, ~2.3k essential), DEMETER2 (computed Pearson; lines map via Model.csv `CCLEName`), Olivieri (Pearson over 28-31 screens), Burke (pDockQ).
3.2 **MUST** Percentile and null for continuous sources are computed over pairs of genes covered by that source. For binary sources, matched random partners are matched on source degree/assayed status (bait-prey coverage is very uneven: absence of an edge is uninformative for unbaited or poorly detected genes, so P can only support, never contradict).
3.3 **MUST** Define "partner-in-predicted-term" for support: all scorable members of term t (not only the K neighbours), count of g-member supported pairs vs matched random gene sets of the same size and degree.
3.4 **SHOULD** Not independent, so do not count towards the Tier A "orthogonal class" rule: hu.MAP (tool tuned on it; integrates P and A data), DEMETER2 (same lines and confounders as CRISPR), Burke (pair selection came from HuRI/hu.MAP; no coverage for most U genes), CCLE proteomics (shared lines). Report them as descriptive.
3.5 **MUST** Licences: Olivieri bioRxiv xlsx is CC BY-NC-ND. Prefer the same screens from BioGRID ORCS (Entrez ids, 31 screens, identical 17,382 genes) as primary and keep the xlsx for cross-check only. Never commit edge/pair tables from Olivieri, BioPlex, ProteomeHD, MitoCarta, CCLE or OpenCell; commit only per-prediction support counts and aggregate statistics.
3.6 **SHOULD** Drop pooled ORCS drug screens (mixed score types and coverage). Allow only single-lab, single-score-type sets with >=15 screens and >=10k genes (Olivieri, Lau 2020); compute similarity only for genes with a |NormZ|>=3 hit, else noise dominates.
3.7 **MUST** Lock `xlrd` (MitoCarta `.xls`), `h5py`/`anndata` (h5ad); use locked `networkx` `louvain_communities(seed=...)` (igraph/leidenalg absent).

## 4. Running the tool; split-half; baselines

4.1 **MUST** Own driver `scripts/05_run_tool.py` that (a) verifies the hash gate, (b) loads X via `data.load_depmap`, (c) builds `CoessentialityModel(X, Config())`, (d) calls `all_pairs.protein_genes` and `score_all_pairs(threshold=6)` (the CLI default of 3 yields up to 20 M candidate rows), (e) writes matrices to `data/derived/` (git-ignored) and a manifest copy plus top-100 neighbour tables to `results/`. Run serially, 8 BLAS threads.
4.2 **MUST** Before ranking, set the diagonal to -inf and restrict columns to BG genes. The stored matrices have NaN diagonals, and `argpartition` on NaN silently returns self as a neighbour under descending selection. Add a test that no gene is its own neighbour and all neighbours are BG.
4.3 **MUST** Split-half halves must be **stratified**, not random. (i) Missingness is block-structured (library-wise): a random split can push a gene across the 10% NaN threshold in one half and change BG, K and the neighbour universe; a gene observed in few lines can become all-NaN in a half, where `CoessentialityModel.__init__` raises. (ii) Stratify within missingness-pattern x lineage, and keep lines with the same `PatientID` (Model.csv) in the same half. Assert BG(half) == BG(full); compare top-25 only among genes BG in both halves and full. For halves, skip the dense matrices: use `zavg_block` and keep top-50 neighbours per gene. Tool seed stays at 0; only the split uses seeds 0-4.
4.4 **MUST** GLS and Pearson full matrices: `Baselines.score` on 170 M pairs is gather-bound and too slow. Compute blockwise: Pearson via masked matmuls (NaN to 0, mask M: n=MM', Sx=X M', Sxx=X² M', Sxy=XX', exact pairwise-complete r); GLS via per-pattern-pair `_whiten` (private; do not modify the tool) with the same block warping as `Baselines._gls`. Gate: equals `Baselines.score` on 5,000 random pairs to 1e-6. Count distinct missingness patterns first; if >200, group by BG-only.

## 5. hu.MAP train-pair reproduction

5.1 **MUST** Run `score_pairs(method='zavg_BEF', add_gls=True)` plus Pearson/Spearman on the 3,314 + 631,465 train pairs; evaluate with HT-AP on `side == ift` using the tool's `protein_assignment.csv` (documented in CLUSTER_ASSIGNMENT.md; it is an input split, not a result, but it sits in `results/`, so the PI must authorise copying it). Targets: ift HT-AP 0.345 (zavg), 0.242 (GLS), 0.146 (Spearman), 0.134 (Pearson); same input SHA-256 so tolerance should be tight (|delta|<=0.003); dev 0.470 is a 5-seed CV mean, expect agreement within 0.01 only.
5.2 **MUST** Stratify V1/hu.MAP calibration by membership in the 1,151 train proteins (tuned-on set); primary V1 numbers exclude them. Collapse redundant complexes (Jaccard>=0.7) in hu.MAP/Complex Portal.

## 6. Annotation sources

6.1 **MUST** GO propagation: along `is_a` and `part_of` only, using the **current** `go-basic.obo` for every release. t0 GAF rows with obsolete ids are remapped via `replaced_by` (unique) else dropped; the 2018 obo only decides "term existed at t0". Hold-out targets = current-propagated terms minus t0-propagated terms (both via current obo), with GAF date > 2018-07-02, restricted to terms alive at t0 and 5-300 genes at t0. This removes re-parenting artefacts.
6.2 **MUST** Drop `NOT`, and for CC drop `colocalizes_with`/`contributes_to`. For leakage control, drop IPI rows whose `with/from` field contains the query gene when scoring that gene.
6.3 **MUST** Temporal complexes are GO CC (descendants of GO:0032991) only; Complex Portal and hu.MAP exist only as current releases.
6.4 **MUST** Complex Portal: parse the `Expanded participant list` column; strip `(n)`, isoform and `-PRO_` suffixes; drop CHEBI/URS/CPX tokens; require >=3 mapped genes for complexes (the 5-300 window removes most complexes; use a per-vocabulary size window: complexes 3-300, others 5-300, fixed on the full annotation, not per query).
6.5 **SHOULD** MitoCarta: sheet "A Human MitoCarta3.0", key `HumanGeneID` (Entrez); optional `MitoPathways` as extra V2 vocabulary. Reactome lowest level: leaf test on `All_Levels`.
6.6 **MUST** Matched-gene null: exclude candidates annotated to any evaluation term of g (else a same-complex "matched" gene makes the null trivially correct); match also on BG status.
6.7 **SHOULD** Broad terms inflate precision@1 and S favours large terms: report by term-size bin and add a p-ranked variant as sensitivity.
6.8 **SHOULD** Paralog control: flag any Ensembl paralog and, separately, >=80% identity in either direction (multi-targeting guides give near-identical profiles). Same-arm uses HGNC `location` (Ensembl coordinates lack centromeres).
6.9 **SHOULD** Low-coverage (non-BG) genes are scored by mean imputation and Nystrom extension (`E` is not a true eigenvector); calibrate them separately, and exclude them from Tier A unless their stratum meets the criterion.
6.10 **SHOULD** The split-half null overlap is ~0 (25²/17.5k = 0.04 expected), so "95th percentile" admits nearly everything; set the assessable cut from the calibration curve (§3.4 ii).

## 7. Verification scripts / toy tests (reuse `external/.../mvp/tests/toy.py` generators)

`tests/`: test_idmap (ambiguous/retired symbols); test_go_propagation (obsolete/replaced_by, NOT, part_of); test_predictor (hypergeometric vs scipy, planted module recovery, self exclusion); test_baselines_matrix; test_splithalf (BG invariance, no all-NaN gene); test_heldout_leakage (query removed from its term background); test_hash_gate; test_support_null (null gives ~5% false positives). An independent agent re-derives the 5.1 numbers and 10 random neighbour lists.

## 8. Pipeline

`03_build_idmap.py` -> `results/id_map/`; `04_build_annotations.py` -> term-gene tables (TSV.gz, committed except MitoCarta); `05_run_tool.py`, `05b_baselines.py`, `05c_splithalf.py`, `05d_repro_humap.py`; `06_neighbours.py` (top-100); `07_predictor_benchmark.py`; `08_evidence_<source>.py` + `08z_evidence_qc.py` (positive/negative control sensitivity); `09_prioritise.py`. **Committed**: scripts, tests, manifests, QC tables, neighbour tables, benchmark results, U predictions. **Git-ignored**: `data/raw`, `data/derived` (matrices, edge lists), `external/`.
