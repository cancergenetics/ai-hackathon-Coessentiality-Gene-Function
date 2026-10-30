# Pre-registered and calibrated function predictions for uncharacterised human genes from DepMap co-essentiality

> **This is an AI-generated research project.** The question, design, code, analyses, literature screens,
> blinded judging, candidate reports, red-teaming and the manuscript were produced by AI agents (Claude models)
> working under an AI "PI" agent, following the brief in `PROMPT.md`. **No human has verified the results,
> the literature claims or the manuscript text.** Everything here, including this README, is unverified by
> humans, so treat all numbers and biological hypotheses as provisional. Some process claims (timestamps, who
> ran what) are self-reported by the agents; the repository has no git remote, so tags are not externally
> time-stamped (see `reviews/ms_round1_reproducibility.md`).

Paper (assembled draft, `manuscript/manuscript.md`, `.docx`, `.pdf`):
*"Pre-registered and calibrated function predictions for uncharacterised human genes from DepMap
co-essentiality reveal modest accuracy and widespread curation lag"*.

The project applies the published co-essentiality tool (`zavg_BEF`, https://github.com/cancergenetics/ai-hackathon-Coessentiality,
commit `3c684c9`, used read-only) to DepMap 26Q3 CRISPR screens. It pre-registers a list of 4,924 uncharacterised
genes (U) before looking at any pairwise DepMap information, calibrates the predictor on a temporal hold-out (H),
and checks the top candidates by blinded literature judging.

## Repository map

| Path | Content |
|---|---|
| `PROMPT.md` | The original task brief (verbatim). |
| `RESEARCH_TREE.md` | Research record: milestone status M0-M9, decision notes (D2 = freeze). |
| `DESIGN.md`, `LITERATURE.md` | Frozen design (v2.3) and literature review. |
| `DATA.md` | Every dataset: source, version, SHA-256, licence. |
| `DEVIATIONS.md`, `LOOKS.md` | Logged deviations from the design; log of looks at the hold-out H. |
| `LESSONS.md`, `CLAIMS.tsv` | Process rules; partial claim-to-source map (6 rows). |
| `config/` | `seeds.yaml`, `frozen.yaml`, `requirements.lock.txt`, `data_checksums.tsv`, data manifests, `term_families.tsv`, `tf_list.tsv`, `localisation_map.tsv`, `agent_scopes.yaml` (a template). |
| `src/` | Analysis modules (`gate.py`, `knownness.py`, `coess_matrix.py`, `neighbours.py`, `predictor.py`, `metrics.py`, `calibration.py`, `splithalf.py`, `orthogonal.py`, `support.py`, `ledger.py`, `vocab.py`, `redact.py`, `hgnc_hub.py`). Described in `docs/PIPELINE.md`. |
| `scripts/` | Numbered pipeline steps (table below), shared helpers `m4_common.py`, `m5_common.py`, `m5b_common.py`, `m6_common.py`, and audit/check utilities. |
| `tests/` | pytest suite (toy pipeline with known answers, gate, metrics, calibration, ...). |
| `preregistration/` | Frozen gene list `uncharacterised_genes.tsv`, `CRITERIA.md`, `FREEZE.sha256`, `PROVENANCE.md`, `sensitivity_sets.tsv`, `sparse_check.txt`. |
| `results/` | Committed result tables and manifests, by stage: `ids`, `preregistration`, `holdout`, `matrices`, `verification`, `assessability`, `orthogonal`, `calibration`, `holdout_eval`, `ledger`, `audit`, `m7`, `config_checks`, `data_checks`, `env_setup.log`, `agent_runs.tsv`. |
| `reports/` | Ten per-candidate reports (ANKRD52, BICRAL, C5orf34, CCDC71L, INAFM1, PLEKHH3, RBM34, TM2D1, TM2D2, TRAPPC5), experiment plans, evidence bundles (`reports/data/`), red-team files (`reports/redteam/`). |
| `verify/` | Independent re-derivations (U, H, hold-out primary result) by separate agents. |
| `reviews/` | Design reviews (rounds 1-2), milestone retrospectives, manuscript review round 1 (including the reproducibility audit that motivated this README), `audit_order_M4.md`, `audit_order_M6.md`. |
| `manuscript/` | `src/` (markdown parts), `figures/` (+ `source_data/`), `manuscript.md/.docx/.pdf`. |
| `references/` | `literature_refs.tsv` and Crossref metadata used by script 79. |
| `data/` (git-ignored) | `raw/`, `derived/`, `cache/`. About 10 GB when complete (raw 5.8 GB, derived 4.6 GB; the full matrix `data/derived/matrices/zavg_full/zavg_BEF.npy` is 1.3 GB). |
| `external/` (git-ignored) | The tool clone `external/coessentiality/`. |
| `.env/` (git-ignored) | Conda environment (Python 3.12). |

## Environment setup

The project was run on macOS (Apple, Darwin 25.x) with a conda environment at `.env/` (Python 3.12.16). Peak
memory seen in manifests is 5.6 GB (script 44); 16 GB RAM is comfortable.

```bash
conda create -p .env python=3.12 -y
# The lock file contains two lines that are not portable. Drop them and install the tool from the clone (below):
grep -v -e '^packaging @ file://' -e '^-e git+' config/requirements.lock.txt > /tmp/req_portable.txt
.env/bin/pip install -r /tmp/req_portable.txt
bash scripts/00_get_tool.sh                      # clones the tool, checks out commit 3c684c9, hides its precomputed predictions
.env/bin/pip install -e external/coessentiality/mvp   # package `coessential`, same commit as the lock file's -e line
```

Notes:

- `config/requirements.lock.txt` has 52 lines. The `packaging @ file:///home/conda/...` line is a build-machine
  path; install any recent `packaging` instead. The lock file does not record the Python version (3.12).
- `scripts/00_get_tool.sh` clones https://github.com/cancergenetics/ai-hackathon-Coessentiality into
  `external/coessentiality/`, checks out `3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf`, refuses to continue if the
  clone is modified, and (until the git tag `preregistration-v1` exists) hides `results/predictions/` by sparse
  checkout so the tool's genome-wide predictions cannot be seen before the freeze. `scripts/verify_sparse.sh`
  asserts this.
- All scripts are run as `.env/bin/python -I scripts/<name>.py` from the repository root.
- `scripts/80_build_manuscript.sh` needs pandoc (2.12 was used; set `PANDOC=/path/to/pandoc`) and either xelatex
  or Google Chrome (`CHROME=...`) for the PDF. Without Chrome or LaTeX only the `.docx` is written.

## Data acquisition

Raw data are never committed. Everything goes under `data/raw/<source>/` and is described in `DATA.md`;
SHA-256 values are in `config/data_checksums.tsv` (69 lines).

1. **DepMap 26Q3 (user-provided, no fetch script).** Download from the DepMap portal
   (https://depmap.org/portal/, Downloads page, release 26Q3, CC BY 4.0) into `data/raw/depmap/`. The files carry
   no version stamp, and `DATA.md` records the release as "26Q3 (user-stated)", with no file URL or DOI. Use
   the checksums below to confirm you have the same files.

   | File (`data/raw/depmap/`) | SHA-256 |
   |---|---|
   | CRISPRGeneEffect.csv | `1e0c492944a7297c0eda179081a1e81a1cfe41a97628facd7eddbdda1a7504ee` |
   | Model.csv | `65eb1895800e71a963a3ab56e5d08c8d006cb0d9e7aa68f7e34a3810a2a3cbc7` |
   | ModelCondition.csv | `a1edda78cd60718e5c99690ce8ab80315b65ddc9346643338d2c1c774fc51326` |
   | CRISPRConfounders.csv | `0e098325d53403d7852f3a773477d20a508a9bf29f43e10fe28bf0f550b35779` |
   | OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv | `252d1fedc7014953b19ffe5d68151b4df973c8078b12c9e5ccd97e292548d177` |
   | OmicsProfiles.csv | `4241e537f0b23139c0e525b4d78fb53ee65c5507771a33e2cd5debd78f7179ea` |
   | OmicsCNGeneWGS.csv | `31cace66f202adaace306d975b5661c8b77ea82f07d2ed34045eec9c7958fcd6` |
   | OmicsSomaticMutationsMatrixDamaging.csv | `736b7a82b4d1f234dc597a409d104186c282f01b0caa56365c27ff987ae49e20` |
   | OmicsSomaticMutationsMatrixHotspot.csv | `0cbdacdce2355d2dd600d3741a36ae093dbe77d7bee44bde97411b1e96973058` |

2. **hu.MAP 3.0 training pairs (user-provided)** in `data/raw/humap_train/` (`Train_positive_pairs.txt`,
   `Train_negative_pairs.txt`; checksums in `config/data_checksums.tsv`). Used by script 11 only.
3. **Annotation and orthogonal datasets (fetched).** `bash scripts/01a_fetch_annotation_data.sh` (HGNC, GO,
   NCBI gene, UniProt, Ensembl, Reactome, HPA, TCRD READMEs, and others) and
   `bash scripts/01b_fetch_orthogonal_data.sh` (STRING, BioPlex, HuRI, OpenCell, BioGRID, BioGRID ORCS,
   Olivieri 2020 tables, MitoCarta, ProteomeHD, CCLE proteomics, Predictomes, and others). Both are idempotent, never
   overwrite existing files and skip files over 3 GB. CORUM could not be fetched (untrusted TLS certificate).
   Then run `01b_check_annotation_data.py`, `01c_check_orthogonal_data.py` and `01d_build_data_md_tables.py` to
   write checks and manifests. Upstream files change over time, so re-downloaded files may not match the committed
   SHA-256 values; `DATA.md` is the record of what was used.
4. **Verify:** `bash scripts/check_data.sh` (runs `shasum -a 256 -c config/data_checksums.tsv`).

## Run order

All commands run from the repository root. "Gate" means the script calls `src/gate.check()`, which refuses to run
unless `preregistration/FREEZE.sha256` is intact and the git tag `preregistration-v1` exists and contains the same
file contents. Runtimes are wall-clock seconds from the committed manifests or logs (one macOS machine); "n/r" means
not recorded. Scripts 02-09 ran before the freeze and read annotation data only (plus single-gene DepMap marginal
summaries, see `preregistration/PROVENANCE.md`). **Do not re-run 03 after the freeze**: it rewrites the frozen list.

| # | Script | Purpose (from its docstring) | Main outputs | Runtime | Gate |
|---|---|---|---|---|---|
| 0 | `00_get_tool.sh` | Fetch the co-essentiality tool at the pinned commit; hide its predictions until the tag exists | `external/coessentiality/` | n/r | no |
| 1a | `01a_fetch_annotation_data.sh` | Idempotent download of gene-annotation datasets | `data/raw/<source>/`, `results/data_checks/fetch_annotation.log` | n/r | no |
| 1b | `01b_fetch_orthogonal_data.sh` | Fetch and checksum orthogonal datasets; writes manifest | `data/raw/<source>/`, `config/data_manifest_orthogonal.tsv` | n/r | no |
| 1b' | `01b_check_annotation_data.py` | Checksum, document and sanity-check annotation downloads | `config/data_manifest_annotation.tsv`, `results/data_checks/annotation_data_checks.md` | n/r | no |
| 1c | `01c_check_orthogonal_data.py` | Sanity-check the orthogonal datasets (does not open DepMap files) | `results/data_checks/orthogonal_data_checks.md` | n/r | no |
| 1d | `01d_build_data_md_tables.py` | Render manifests into `DATA.md` tables and refresh `config/data_checksums.tsv` | `DATA.md`, `config/data_checksums.tsv` | n/r | no |
| 2 | `02_gene_knownness_table.py` | Per-gene "knownness" feature table (annotation only) | `results/preregistration/gene_knownness_features.tsv` | n/r | no |
| 2a | `02a_pmid_date_cutoffs.py` | PMID-number cut-offs used as a date proxy for "published before date" | `results/preregistration/pmid_date_cutoffs.tsv` | n/r | no |
| 3 | `03_build_preregistration.py` | Build the pre-registered list of uncharacterised genes U (4,924) | `preregistration/uncharacterised_genes.tsv`, `sensitivity_sets.tsv` | n/r | no |
| 4 | `04_holdout_sizing.py` | Temporal hold-out H (820 genes, 5,965 targets); annotation only | `results/holdout/H_genes.tsv`, `H_targets.tsv`, `holdout_sizing.md` | n/r | no |
| 5 | `05_circularity_query.py` | DepMap-circularity flags for hold-out target annotations | `results/holdout/circularity_flags.tsv`, `circularity_annotations.tsv` | n/r | no |
| 6 | `06_check_term_families.py` | Verify `config/term_families.tsv` against current GO | `results/config_checks/term_families_check.md` | n/r | no |
| 7 | `07_check_frozen_yaml.py` | Cross-check `config/frozen.yaml` against `DESIGN.md` | `results/config_checks/frozen_yaml_check.md` | n/r | no |
| 8 | `08_power_simulation.py` | Freeze-time power simulation for the primary hold-out comparison | `results/holdout/power_sim.md` | n/r | no |
| 9 | `09_random_u_sample.py` | Random sample of 50 U genes (seed 0) for the curation-lag audit and recall probe | `results/audit/random50_U_sample.tsv` | n/r | no |
| **F** | *freeze* | Write `preregistration/FREEZE.sha256`, commit, tag `preregistration-v1` and `design-frozen` (freeze commit `afed1dd`); done by hand, no script | tags, `FREEZE.sha256` | - | - |
| 10 | `10_full_matrix.py` | Full `zavg_BEF` matrix on all 1,361 lines (tool at default Config) | `data/derived/matrices/zavg_full/zavg_BEF.npy` (1.3 GB), `results/matrices/zavg_full_*` | 155 s (4.3 GB RAM) | yes |
| 11 | `11_reproduce_tool.py` | Reproduce the tool's published internal-test HT-AP (tolerance +-0.005) | `results/verification/tool_reproduction.md` | 225 s | yes |
| 12 | `12_sanity_checks.py` | Sign and orientation assertions on DepMap and the matrix | `results/verification/sanity_checks.md` | 16 s | yes |
| 13 | `13_matched_lists.py` | Full-data neighbour lists N(g) and matched lists M(g) | `data/derived/neighbours/`, `data/derived/matched/`, `results/verification/matched_lists.md` | 75 s | yes |
| 14 | `14_splithalf.py` | Split-half tool runs (5 seeds x 2 halves) for assessability | `data/derived/splithalf/*.npz`, `results/assessability/splithalf_runs.md` | 1,425 s | yes |
| 15 | `15_assessability.py` | Split-half reproducibility R(g) and the assessability call (claim C1) | `results/assessability/assessability_U.tsv`, `R_all.tsv`, `summary.md` | 32 s | yes |
| 16 | `16_baseline_rows.py` | GLS and Pearson baseline rows | `data/derived/baselines/`, `results/verification/baseline_rows.md` | 52 s | yes |
| 20 | `20_source_admission.py` | Orthogonal source admission against GO / complex gold standards (before any U prediction) | `results/orthogonal/admission*.{tsv,md,json}` | 115 s | no (no gate call in the script) |
| 30 | `30_loo_ranker_choice.py` | Ranker choice on the leave-one-out benchmark (M5a) | `results/calibration/loo_ranker_choice.*` | 72 s | yes |
| 31 | `31_label_shuffle.py` | Label-shuffle control on the LOO benchmark | `results/calibration/label_shuffle.*` | 100 s | yes |
| 32 | `32_holdout_core.py` | The single pre-registered look at H, core analyses (logged in `LOOKS.md`) | `results/holdout_eval/core*.{md,json,tsv}` | 297 s | yes |
| 33 | `33_holdout_secondary.py` | Secondary batch on H | `results/holdout_eval/secondary*` | 176 s | yes |
| 34 | `34_calibration_fit.py` | Calibration model fitted on H, as logged in `LOOKS.md` | `results/holdout_eval/calibration*`, `results/calibration/model_H.json` | 4.7 s | yes |
| 35 | `35_holdout_figures.py` | Figure data and single summary of the H look (reads outputs of 32-34 only) | `results/holdout_eval/SUMMARY.md`, `fig_*.tsv`, `manuscript/figures/m5b_*` | n/r | yes |
| 36 | `36_holdout_exploratory.py` | Exploratory, post hoc look at H (complementarity with homology) | `results/holdout_eval/exploratory_complementarity.*` | n/r | yes |
| 40 | `40_u_predictions.py` | TF list and machine-generated prediction ledger for every scorable U gene | `results/ledger/u_predictions.tsv`, `u_partners.tsv` (10 MB) | 187 s | yes |
| 41 | `41_pcal.py` | Calibrated probabilities p_cal for U predictions | `results/ledger/u_pcal.tsv`, `pcal_summary.json` | 10 s | yes |
| 42 | `42_artefact_flags.py` | Artefact flags for every reported U prediction | `results/ledger/u_flags.tsv` | 29 s | yes |
| 43 | `43_orthogonal_support.py` | Orthogonal support for predictions, with null controls | `results/ledger/support*.tsv`, `negative_control*.tsv` | 111 s | yes |
| 44 | `44_tiers_top40.py` | Tiers, top-40 fill and top-40-only checks (the slowest step) | `results/ledger/tiers_all.tsv`, `top40*.tsv` | 3,311 s (5.6 GB RAM) | yes |
| 45 | `45_m6_summary.py` | M6 summary and figure-ready TSVs | `results/ledger/M6_SUMMARY.md`, `figdata/` | 3.5 s | yes |
| 46 | `46_top40_primary.py` | Primary top 40 under the low-yield branch (PI decision in `DEVIATIONS.md`) | `results/ledger/top40_primary.tsv` | n/r | no direct call (reads ledger tables) |
| 50 | `50_m7_prep.py` | M7 candidate lists, blinded-judging statements and blind-agent inputs | `results/m7/{s20,extra30,hval10,statements,probe_list,answer_key}.tsv`, `manifest.json` | 15 s | no |
| 51 | `51_judge_packets.py` | Build blinded judge packets (J### to gene map only in `packet_key.tsv`) | `results/m7/judge/packets/`, `batches/`, `packet_key.tsv` | n/r | no |
| 52 | `52_judge_analysis.py` | Validation check and primary analysis of blinded judging | `results/m7/judge/analysis_{main,hval}.md` | n/r | no |
| 60 | `60_figures.py` | Manuscript figures for claims C1-C3 (no new analysis) | `manuscript/figures/Fig1-4.*`, `FigS1-3.*`, `source_data/` | n/r | no |
| 61 | `61_figure5.py` | Figure 5 and Table 2 for claim C4 (no new judging) | `manuscript/figures/Fig5.*`, `Table2_rediscovery.tsv` | n/r | no |
| 70 | `70_report_bundles.py` | Evidence bundles for the ten deep-dive candidates | `reports/data/<gene>/`, `bundle_summary.tsv` | 133 s | yes |
| 79 | `79_assemble_manuscript.py` | Assemble `manuscript/src/*.md` with keyed citations into `manuscript.md` | `manuscript/manuscript.md` | n/r | no |
| 80 | `80_build_manuscript.sh` | Render `.md` to `.docx` and `.pdf` | `manuscript/manuscript.docx`, `.pdf` | n/r | no |

Utilities (not pipeline steps): `scripts/check_data.sh` (verify raw-data checksums), `scripts/verify_sparse.sh`
(assert the tool's predictions are hidden and the clone is pristine, pinned at `3c684c9`),
`scripts/audit_order.py` (chronology audit of the gate; output in `reviews/audit_order_M4.md`, `audit_order_M6.md`),
and the helper modules `m4_common.py` (scripts 10-16), `m5_common.py` (30-31), `m5b_common.py` (32-35) and
`m6_common.py` (40-45). Every step also writes a manifest or log next to its outputs.

Total compute for the gated numerical pipeline (10-16, 30-36, 40-45, 70) is roughly 1.6 hours on the recorded
runtimes, dominated by script 44. Disk use is about 10 GB.

### Agent-only steps (not scriptable)

These steps were carried out by AI agents with web/literature access or by judgement, and cannot be re-run
from a script. Their outputs are committed, so they can be inspected.

| Step | What | Where the outputs are |
|---|---|---|
| Design and literature | `LITERATURE.md`, `DESIGN.md` v1 to v2.3, 11 independent reviews in two rounds plus disposition checks | `LITERATURE.md`, `DESIGN.md`, `reviews/round1_*.md`, `reviews/round2_*.md` |
| Independent re-derivations | U and H re-derived from raw files by agents without access to `src/knownness.py`; hold-out primary result re-derived | `verify/` (e.g. `verify/prereg_verification.md`, `verify/rederive_prereg.py`) |
| Curation-lag audit, recall probe (random 50) | Literature check of whether "uncharacterised" genes have functional papers; recall probe of an LLM on the same genes | `results/audit/curation_lag_audit.{md,tsv}`, `results/audit/recall_probe_random50.tsv` |
| L literature screens (100 genes) | Per-gene literature novelty screen (N1/N2/N3) with short abstract quotations | `results/m7/L/`, `results/m7/L_batches/`, `results/m7/report_selection.md` |
| Recall probe (90 genes) | LLM recall probe on selected genes | `results/m7/probe_list.tsv`, `results/m7/recall_probe_90.tsv`, `results/m7/answer_key*.tsv` |
| Blinded judging | Judges score statements against decoys from anonymised packets; analysis by script 52 | `results/m7/judge/` (`packets/`, `batches/`, `scores/`, `packet_key.tsv`, `leak_check.tsv`, `disagreements.tsv`, `analysis_*.md`) |
| Candidate reports and red-teaming | Ten reports with experiment plans, then adversarial review and revision | `reports/*.md`, `reports/redteam/*.md`, scratch dirs `results/m7/scratch_reports_*` (git-ignored) |
| Manuscript writing and review | Draft parts, two referee reports, number/reference/reproducibility audits | `manuscript/src/`, `manuscript/drafts/`, `reviews/ms_round1_*.md` |

**Prompts.** The only verbatim prompt committed is the PI brief, `PROMPT.md`. The task prompts given to the L,
judge, recall-probe, report-writer and red-team agents were **not committed**, and no seeds or temperatures
were recorded for LLM calls. Blinding therefore cannot be audited from prompts alone (the packet design is in
`scripts/50_m7_prep.py`, `scripts/51_judge_packets.py` and `DESIGN.md` §6.4). `config/agent_scopes.yaml` is a
template for agent write scopes, and `results/agent_runs.tsv` has one row (model ID `claude-sonnet-5-5`), so
it is not a complete record of agent runs. These agent steps are not reproducible in the strict sense.

## Seeds

`config/seeds.yaml` fixes the seed list `[0, 1, 2, 3, 4]` (mirrored in `config/frozen.yaml`). Seed 0 is used for
single-run stochastic steps and all five for repeated steps (the ten split-half runs in script 14 use seeds 0-4,
and `09_random_u_sample.py` uses seed 0). Not every script reads `seeds.yaml`: several RNGs hard-code `0` or a
shared constant in `m*_common.py`. The tool's own internal seed (random-pair reference for `zavg_BEF`) is fixed
inside the tool and not overridden. LLM steps have no recorded seeds.

## Pre-registration

- Git tags: `preregistration-v1` and `design-frozen`, both at freeze commit `afed1dd`
  (see `RESEARCH_TREE.md`, decision note D2). There is no git remote, so tags are local and their times are
  self-reported.
- `preregistration/FREEZE.sha256` lists the frozen files (the design, `config/frozen.yaml`, `config/seeds.yaml`,
  `src/knownness.py`, `src/gate.py`, `config/term_families.tsv`, the gene list and criteria, and the checksums of three DepMap files). Its own SHA-256 is
  `687075e680b8a051e6482de5bb052c903afaf2942ae5a25a34cef79e5965da04`. Check the list with
  `(cd . && shasum -a 256 -c preregistration/FREEZE.sha256)` and its hash with
  `shasum -a 256 preregistration/FREEZE.sha256`.
- `preregistration/PROVENANCE.md` documents how and when U was built, what DepMap content had been read before
  the freeze (header and single-gene marginal summaries only), and the independent re-derivation.
- The gate (`src/gate.py`) is enforced in every script that reads pairwise DepMap information.
  `scripts/audit_order.py` checks the commit chronology against the tag.
- Known limitations of the record (from `reviews/ms_round1_reproducibility.md`): some deviations were logged after
  the results they affect (R1 tie-break, top-40 fill, assessability count); the H look has a logged verification
  re-run and an exploratory look (`LOOKS.md`).

## Rebuilding figures and the manuscript

```bash
.env/bin/python -I scripts/60_figures.py      # Fig1-4, FigS1-3 -> manuscript/figures/
.env/bin/python -I scripts/61_figure5.py      # Fig5 and Table 2
.env/bin/python -I scripts/79_assemble_manuscript.py   # manuscript/src/*.md -> manuscript/manuscript.md
bash scripts/80_build_manuscript.sh           # .docx and .pdf (pandoc; Chrome or xelatex for PDF)
```

Figures read committed result tables, so the first two need no raw data. Figures `m5b_*` are written by script 35.
Script 79 reads `references/literature_refs.tsv` and the Crossref metadata TSVs in `references/`.
Crossref metadata were fetched by `scripts/78_crossref_metadata.py` (key<TAB>DOI on stdin) into `references/old_meta.tsv` and `new_meta.tsv`.

## Tests

```bash
.env/bin/python -I -m pytest -q tests/          # about 40 s; toy data with known answers, no DepMap needed
.env/bin/python -I tests/test_toy_pipeline.py   # prints the toy acceptance summary (JSON)
```

99 tests passed when the modules were completed (M3); `tests/` has since gained further files
(`test_audit_order.py`, `test_judge_analysis.py`, `test_ledger.py`, `test_orthogonal.py`, `test_support.py`,
`test_redact.py`, and others). The count was not re-checked when this README was written.

## Licences and restricted data

- **Code and text in this repository** have no LICENSE file yet. Add one before redistribution.
- **DepMap 26Q3**: CC BY 4.0, but **do not redistribute the raw files** or the full matrix. They are git-ignored and
  not in history. Note that the repository does commit DepMap-derived result tables (for example
  `results/ledger/u_partners.tsv`, 10 MB), which are not raw data.
- **Olivieri et al. 2020 tables** (CC BY-NC-ND): **never redistribute.** Only admission summary statistics appear in
  the results, with no pair-level table.
- **The co-essentiality tool** has no LICENSE file at commit `3c684c9`. It is used read-only, never modified and not
  redistributed (`external/` is git-ignored).
- **Other datasets** (STRING, BioPlex, HuRI, OpenCell, BioGRID, MitoCarta, CCLE proteomics, ProteomeHD,
  hu.MAP, HGNC, GO, ...) are downloaded by the user under their own terms. Some licences are recorded as
  "unverified" in `DATA.md`. Several downloaded files (Predictomes, Reactome, BioGRID ORCS, OmicsProfiles,
  gene_info, TCRD READMEs) are used by no analysis script. `results/m7/L/` contains short verbatim abstract
  sentences for literature screening.
- `data/`, `external/`, `.env/`, `*.npy`, `*.npz`, `*.parquet` and scratch directories are git-ignored.
