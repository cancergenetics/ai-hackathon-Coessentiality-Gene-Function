# PIPELINE.md — analysis modules, artefacts and verification

Implements DESIGN.md v2 §2 (infrastructure), §3.1 (predictor), §3.3–3.5 (comparators, matching, resampling), §3.7
(calibration), §4.2 (assessability) and §5.3 (empirical p by resampling). Every module lives in `src/`, is imported
as `from src import <module>` (repository root on `sys.path`), and has toy tests in `tests/` with hand-computed or
simulation-known answers. Run everything with

```
.env/bin/python -I -m pytest -q tests/          # ~40 s; the toy pipeline (§2.5) is tests/test_toy_pipeline.py
.env/bin/python -I tests/test_toy_pipeline.py   # prints the toy acceptance summary (JSON)
```

The co-essentiality tool (`external/coessentiality`, commit 3c684c9, installed editable in `.env`) is used through
its public Python API and is never modified. None of the modules reads DepMap files: callers pass DataFrames.
**Every script that computes or reads pairwise DepMap information calls `gate.check()` first.**

## 1. Data flow

```
CRISPRGeneEffect (lines x genes) ──► coess_matrix.fit_model ──► write_tool_matrices ──► zavg_BEF / z_B / z_E / z_F .npy
        │                                   (tool, Config())                               + genes.tsv + manifest.json
        ├──► coess_matrix.write_baseline_matrix ──► pearson.npy, gls.npy (+ verify_against_baselines)
        ├──► splithalf.split_halves ──► half_neighbours (tool refit per half, block API) ──► reproducibility ──► assessable
        └──► predictor.profile_covariates ──► match_genes
zavg_BEF.npy ──► neighbours.top_k (self/BG/same-arm/paralogue exclusion) ──► predictor.term_scores
     ──► hypergeom_p, empirical_p ──► score_table ──► top_terms (most-specific pruning)
     ──► metrics (hit@1, RR, AP, cluster bootstrap, sign-flip, calibration) ──► calibration (p_cal, Σ p_cal)
```

## 2. Modules

| module | spec | main functions | inputs | outputs |
|---|---|---|---|---|
| `gate.py` | §1.6, §9 | `check()` | `preregistration/FREEZE.sha256` (sha256sum format), git tag `preregistration-v1`; optional tool commit, `config/data_checksums.tsv` | summary dict (tag commit, hashes) for run manifests; raises `GateError` |
| `coess_matrix.py` | §2.2, §4.2, §8 | `fit_model`, `write_tool_matrices`, `ModelBlockSource`, `verify_tool_matrices`, `pearson_matrix`, `gls_matrix`, `write_baseline_matrix`, `verify_against_baselines`, `open_matrix` | gene-effect DataFrame (lines × genes), optional line subset / gene subset, `Config` | float32 `.npy` matrices (memmap), `genes.tsv` (matrix_index, gene, model_index, bg, nan_fraction, mean, sd [+ extra columns e.g. hgnc_id]), `manifest.json` (config, published_config flag, lines, n_bg, K_tool, dropped all-NaN genes, null moments, runtime, peak RSS) |
| `neighbours.py` | §2.2, §3.1, §4.3 | `top_k`, `arm_codes`, `index_sets`, `assert_valid` | score matrix / memmap / block source; BG mask; arm labels; paralogue sets; extra exclusions | `Neighbours` (ids G×K with −1 padding, z float32), long table via `to_frame` |
| `predictor.py` | §3.1, §3.4 | `term_scores`, `hypergeom_p`, `profile_covariates`, `match_genes`, `balance`, `empirical_p`, `score_table`, `most_specific`, `top_terms` | `Neighbours`, sparse annotation matrix A (genes × terms; query rows empty), annotated-background mask, term-size mask, GO ancestor map | per-(gene, term) table: S, n_sup, x, n_draw, p_hyper, p_emp, M_t, reportable, rank_R1/R2/R3; per-gene top1 and most-specific term; matching summary and SMD balance table |
| `metrics.py` | §3.3, §3.5, §3.7, §6.4 | `hit_at_1`, `reciprocal_rank`, `average_precision`, `hit_at_1_restricted`, `per_gene_metrics`, `clusters_from_links`, `cluster_bootstrap_mean`, `paired_cluster_bootstrap`, `sign_flip_test`, `cohens_kappa`, `reliability_diagram`, `ece`, `brier`, `calibration_intercept_slope` | ranked term lists, target sets, per-gene paired values, cluster labels, probabilities/outcomes | dicts / DataFrames (estimates, percentile + BCa CIs, design effect, p-values) |
| `splithalf.py` | §4.2 | `split_halves`, `background_check`, `half_neighbours`, `reproducibility`, `assessable` | Model table (OncotreeLineage, PatientID), effect DataFrame, seeds 0–4, common BG mask, arms, paralogues, matched genes (M = 200) | half labels per line; BG-invariance table; R(g), R0(g,·); assessability flags under three rules |
| `calibration.py` | §0 C3, §3.7 | `MonotoneLogistic`, `cluster_folds`, `cross_fit`, `support_mask`, `p_cal`, `sum_pcal` | H covariates (top-K mean zavg, R(g), coverage, log term size, family dummies), hit@1, clusters, pre-specified signs; U covariates | out-of-fold p for H, ensemble p_cal for U (NaN outside H's 5th–95th pct), Σ p_cal with cluster-bootstrap CI |

### Definitions fixed in code (please review before freeze)
* **Supporting partner**: j ∈ N(g) ∩ t with z_gj > 0 (S uses max(z, 0)). The hypergeometric x counts all
  members of N(g) ∩ t regardless of sign; n = |N(g) ∩ annotated background|.
* **p_emp, matched genes annotated to t**: dropped per term (M_t ≤ M), so a matched gene that belongs to t is never
  used as a null for t. This is how the §3.4 rule "exclude genes annotated to g's targets" is applied when targets
  are unknown (U genes); for H genes callers additionally pass the targets' members as `extra` exclusions.
* **Ranking ties**: R2/R3 ties by S (desc), then term index; R1 ties by term index. Only reportable terms (≥ 2
  supporting partners) are ranked; a gene with no reportable term has no prediction and scores hit@1 = 0, RR = 0.
* **AUPRC**: non-interpolated AP over the ranked list; targets never ranked contribute 0; genes with |T| < 3 → NaN.
* **Same-arm exclusion**: genes with unknown arm get no arm exclusion (callers report how many).
* **Tool matrices**: upper triangle = `z_block` value, lower = mirror, diagonal NaN, float32 — identical to the
  tool's `all_pairs.score_all_pairs` zavg_BEF (tested bit-for-bit); components are stored as float32 (the tool's
  all_pairs uses float16).
* **GLS covariance** is estimated on all columns of the matrix passed (as `Baselines(X)` does): pass the full DepMap
  matrix and select genes with `gidx`.

## 3. Artefacts: committed vs git-ignored

| artefact | location | git |
|---|---|---|
| tool / baseline matrices (`zavg_BEF`, `z_B`, `z_E`, `z_F`, `pearson`, `gls` `.npy`, 1.35 GB each at 18.4k genes) | `data/derived/matrices/<run>/` | ignored (`/data/`, `*.npy`) |
| split-half fits (no dense matrices; neighbour arrays only) | `data/derived/splithalf/` | ignored |
| `genes.tsv` gene index (+ hgnc_id), `manifest.json` copies (config, K, BG, lines, null moments, hashes, runtime) | `results/matrices/<run>/` | committed |
| top-100 neighbour tables per gene (TSV.gz), split-half R/R0/assessability tables | `results/neighbours/`, `results/splithalf/` | committed |
| predictor score tables, top terms, ledger, metrics/bootstrap outputs, calibration outputs | `results/benchmark/`, `results/ledger/`, `results/calibration/` | committed |
| baseline verification (`verify_against_baselines`, `verify_tool_matrices` dicts) | `results/matrices/<run>/verification.json` | committed |
| toy pipeline summary (synthetic) | `TOY_SUMMARY_OUT=results/verification/toy_pipeline.json` | committed if written |
| raw inputs (DepMap, GO, …) | `data/raw/` | ignored (DATA.md lists source, version, checksum, licence) |

Never commit pair/edge tables from restricted-licence sources (DESIGN §5; round-1 review 3.5).

## 4. Toy pipeline (§2.5) — `tests/test_toy_pipeline.py`

Synthetic 300 lines × 2,000 genes: 36 planted modules (sizes 3–30; 24 strong, 12 weak), a lineage nuisance (6
lineages, 400 genes, dominant line-space structure; 2-line patients), 40 "arms" with 8 proximity blocks of 12
genes sharing a CN-like factor, block and random missingness (60 non-BG genes). Vocabulary: module terms, 6 parent
terms (DAG), proximity-block terms, 80 random decoys; ~20% of each module and 5 genes per block held out as
unannotated queries. Null matrix: same means/SDs/missingness/vocabulary, no structure, 400 queries. The REAL tool
is fitted on both matrices (and on 5 × 2 split halves of each).

**Tool configuration for the toy** (`TOY_CFG = Config(k=5, q=1.25, d=64)`, other fields published): k = 5 PCs
removed because the planted nuisance has rank 5 and removing 20 PCs of a 300 × 2,000 matrix would remove the 20
largest planted modules; q = 1.25% gives tool K = 24 (0.25% of 1.9k BG genes would be K = 5, smaller than most
modules); d = 64 keeps the embedding at ~3% of BG genes as in the published 512/17.5k. These settings cannot reach the
real run: real runs use `coess_matrix.PUBLISHED_CONFIG` (= `Config()`), and every manifest records
`published_config: true/false`. Predictor settings are the pre-registered ones except the term-size window (2–200,
planted modules are small) and M = 200 matched genes.

**Results (seed 0; 22 s for the whole toy incl. 22 tool fits)**

| check | acceptance | result |
|---|---|---|
| tool matrices vs pair API (20k pairs) | < 1e-4 | max diff 2.8e-7 |
| strong modules, precision@1 (R3; top1 ∈ {module, parent}) | ≥ 0.8 | 1.00 (74 queries); most-specific term = module 1.00; R1 0.99, R2 1.00 |
| weak modules, precision@1 (R3) | report | 0.60 (R1 0.36, R2 0.51) |
| proximity queries calling own block term at top1, no exclusion | positive control | 1.00 (39) |
| … with same-arm exclusion (own term even reportable) | 0 | 0.00; no gene has a same-arm neighbour |
| null: tie-randomised p_emp, one random term per query, KS vs U(0,1) | p > 0.01 | p = 0.135 (all pairs: p = 0.60); conservative p_emp ≤ 0.05 in 4.7% |
| null: genes with any BH-significant term (all eligible terms) | ≤ 5% | 0.0% (p_emp); 1.5% (hypergeometric) |
| null: assessable rate, randomised rule | 5% ± 2% | 5.4% (percentile rule 3.4%, conservative 3.0%) |
| structured: assessable, strong-module genes / noise genes | report | 100% / 6.3% |

Seeds 1–3 (robustness, not part of the test): strong precision@1 0.99–1.00; KS p 0.15–0.90; randomised assessable
rate 5.4–6.7%; same-arm exclusion 1.0 → 0.0 on every seed.

## 5. Findings that need a PI decision before freeze

1. **Caliper vs M (§3.4).** A per-covariate caliper of 0.2 SD on three covariates admits ~0.1% of genes: on the toy,
   strict matching gives a median of 26 matches (never 200); at 18k genes it would give ~20–30, not 500. The toy
   uses `mode='relaxed'` (M nearest by Mahalanobis; 87% of matches lie outside the caliper; SMD mean −0.005, log SD
   0.08, NaN fraction 0.25). Options: drop the per-pair caliper and require balance SMD < 0.1; or keep the caliper
   with M = "all within caliper, minimum 20".
2. **BH on p_emp is nearly vacuous.** p_emp ≥ 1/(1+M) (0.002 at M = 500), while BH over thousands of GO terms needs
   p ≲ 1e-5 for the first rejection, so "genes with any BH-significant term" is ~0 by construction; BH restricted to
   reportable terms (selected by the ≥ 2-partner rule) is anti-conservative on the null (8.5–13.5% across seeds).
   p_emp should be used as a ranking statistic (as DESIGN §3.1 does) and never with BH.
3. **Assessability rule (§4.2).** "R(g) > 95th percentile of R0" is conservative because R0 is discrete and mostly
   0: null rate 3.4% on the toy and 1.7% in a DepMap-scale combinatorial null (|BG| = 17.5k, K = 25; test in
   `tests/test_splithalf.py`). The tie-randomised rank rule has size ≈ 5% (5.4–6.7% on the toy; 5.0% at scale). The
   small excess on the toy comes from the same-arm exclusion: matched genes are on other arms, so N_B(m) can
   contain g's arm-mates that N_A(g) cannot. Choose the rule before freeze.
4. **"≥ 2 supporting partners" barely filters** when the vocabulary has large terms: every null gene had a
   reportable term on the toy. Reporting still relies on calibration (p_cal), not on this rule.
5. **R0 matched genes** use the §3.4 exclusions (N(g), same arm, paralogues); the toy uses caliper-free matching
   for R0 for the same reason as item 1.

## 6. Tool API notes

* Public API used: `CoessentialityModel` (`z_block`, `zavg`, `null_moments`, `bg`, `K`, `nan_frac`, `mean`, `sd`),
  `Config`, `baselines.Baselines.score`, `baselines.sample_covariance`, `baselines.whitening`,
  `all_pairs.score_all_pairs` (test reference only). Block iteration follows the model's fixed `Config.block`
  blocks (the tool's private `_blocks`, re-implemented) so values are bit-identical to `all_pairs`.
* The model raises on genes with no observation; `fit_model` drops and records them (relevant for split halves).
* Stored tool matrices have a NaN diagonal; `argpartition` on NaN can return self — `neighbours.top_k` maps
  non-finite values to −inf and excludes self explicitly (`assert_valid` checks).
* `all_pairs` stores components as float16; we store float32. Its pair-table step is skipped (not needed).
* GLS is defined per pair of missingness patterns: cost grows with the number of distinct patterns (one whitening,
  O(n³), per distinct shared-line set); count patterns first on real data.
* `Baselines._gls` / `_whiten` are private; we re-implement their arithmetic with the public `whitening` and
  `sample_covariance` and verify against `Baselines.score`.

## 7. Runtime and memory (18.4k genes)

Measured on SYNTHETIC data at DepMap scale (1,100 lines x 18,400 genes, 600 planted modules, a 100-line library
block missing for 900 genes plus 40 small extra missingness patterns -> 60 patterns; published `Config()`, |BG| =
18,378, tool K = 46), this laptop (8 cores, 24 GB), one process. Script kept outside the repository (scratchpad);
no DepMap data were read.

| step | wall time | notes |
|---|---|---|
| tool genome-wide state + null moments (F, B neighbours, ARPACK d = 512) | 85 s | |
| `write_tool_matrices` blocks (18 x 1,024 genes, 4 matrices) + mirror | 48 s + 6 s | 4 x 1.35 GB float32 memmaps |
| total per full tool run | 140 s | 2-3 min, consistent with DESIGN §8 |
| `verify_tool_matrices` (20k pairs) | < 1 s | max diff 4.7e-7 |
| `neighbours.top_k` all genes, K = 25, BG + arm exclusion, from memmap | 6 s | |
| `pearson_matrix` | 52 s | vs `Baselines.score` on 100k pairs: max diff 2.5e-8 |
| `gls_matrix` (60 patterns, 1,830 pattern pairs) | 708 s | vs `Baselines.score` on 100k pairs: max diff 4.5e-7 (verification itself 105 s) |

Peak memory footprint 3.5 GB (max RSS 7.7 GB including resident memmap pages); disk 8.1 GB for the six matrices.
GLS cost scales with the number of distinct shared-line sets (~10-12 s each at 1.1k lines, dominated by warping the
complete-data genes); count missingness patterns on DepMap before running it and, if there are > 200, group by BG
status as in round-1 review 4.4. Split halves (10 fits, no dense matrices: state ~45 s + 18 block evaluations each)
are estimated at ~2 min per half, ~20 min for 5 seeds.
