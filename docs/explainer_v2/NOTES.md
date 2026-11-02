# Fact list for docs/explainer_v2/README.md

Every factual claim in the readable explainer, with the file it comes from, for fact-checking. Paths are relative to
the project root. "Old explainer" means `docs/explainer/` (independently reviewed; see `reviews/explainer_review.md`).
Where the old explainer and a results file could disagree, the results file was checked and is listed first.

## Scope, data and genes

| Fact in README | Value used | Source |
|---|---|---|
| Protein-coding genes; pre-registered list | 19,296; 4,924 ("about one in four") | `preregistration/CRITERIA.md` lines 8, 15 |
| Measurable (scorable) in DepMap | 4,271 | `results/ledger/pcal_summary.json` (`n_scorable`); `preregistration/CRITERIA.md` |
| DepMap release and cell lines | 26Q3, 1,361 lines | `docs/explainer/worked_example_output/worked_example.json` (`step1.n_lines_total`); old METHOD Step 2 |
| Definition: no informative experimental GO BP/MF, and UniProt score ≤ 2 or ≤ 10 focused papers (papers listing ≤ 10 genes) or Tdark | as stated; Tdark called "the dark protein class of the Illuminating the Druggable Genome programme" | `DESIGN.md` §1; old METHOD Step 1 |
| List frozen by hash; gate refuses to run otherwise; independent re-derivation matched | — | old METHOD Step 1; old JOURNEY TP1; `preregistration/PROVENANCE.md` |
| Random 50: 42% already had a function | 21/50, 29–56% | `results/audit/curation_lag_audit.md` line 15 |
| Audit 16 minutes after freeze | `b2b3a53` vs `afed1dd` | old JOURNEY TP1 |
| Complex Portal subunits on the list | 288 | `results/revision/SUMMARY.md` §A1 |
| No gene removed after the freeze | — | old JOURNEY TP1 |

## Method steps

| Fact | Value | Source |
|---|---|---|
| Tool published in the cancergenetics GitHub organisation by the Ryan lab, University College Dublin; itself AI-built during a hackathon; required by the brief | — | `external/coessentiality/README.md` (Disclaimer, line 7); `PROMPT.md`; `references/literature_refs.tsv` (Coessentiality_tool) |
| Tool: three views (cleaned-profile similarity, partner-list overlap, network-map closeness), used unchanged; reproduced published benchmark | AP 0.3451 vs 0.345 | old METHOD Step 2; `results/verification/` |
| 25 partners; same-arm and paralogue exclusions; Lazar 2024 rationale | — | old METHOD Step 4; `DESIGN.md` §3.1 |
| Exclusions changed accuracy little | 3.3% without vs 3.0% with | `results/holdout_eval/SUMMARY.md` (secondary batch, "No same-arm / paralogue exclusion") |
| Split halves five times, 200 matched ("look-alike") genes, plus expression requirement; failing genes still get a flagged prediction and cannot enter the shortlist | — | old METHOD Step 3; `results/assessability/summary.md` |
| Pass the reproducibility check | 646 (13.1%) | `results/ledger/M6_SUMMARY.md`; `results/assessability/summary.md` line 13 |
| Non-expressed controls passing | 13% (153/1,167 clean negatives); 27% with any dependency | `results/assessability/summary.md` line 34; old METHOD Step 3 |
| "About 320 genes, roughly 1 in 15" carry real signal | 322 (242–388), 6.5% on the 646 basis; manuscript 324 / ~320 (6.6%) on the 635 basis | `results/revision/a10_assessability_excess_and_implied.tsv`; old DISCREPANCIES B13 |
| Olfactory/skin (chemosensory/epidermal) families | 2 of 516 passed; mostly not expressed (7 of 407 scorable are expressed) | `results/assessability/summary.md` line 25 |
| Look-alike genes matched on mean effect, spread and missing data | — | old METHOD Step 3 |
| "At least ~320" is a lower bound under the untested assumption that the non-expressed false-pass rate applies to expressed genes | — | `results/revision/SUMMARY.md` §A6; old METHOD Step 3 |
| Term score = sum of partner scores; ≥ 2 supporting partners; three pre-declared rankers, simplest (R1) won | MRR 0.169 vs 0.140 vs 0.111 | `results/calibration/loo_ranker_choice.md`; old JOURNEY TP4 |
| Calibration: logistic regression on partner strength, annotated-partner share, term size, reproducibility and term family; term size and reproducibility got zero weight (README mentions term size only) | — | `results/holdout_eval/SUMMARY.md` ("Calibration model for U"); old DISCREPANCIES B18 |
| Genes with calibrated confidence | 2,583 | `results/ledger/pcal_summary.json` |
| Confidence learned on known genes promised ~3× too much | 8.9% vs 3.1% | `results/holdout_eval/SUMMARY.md` ("LOO-fitted calibration on H") |
| Meaning of confidence: exact term recorded from experiments within ~8 years, given the gene gets new annotation | — | old METHOD Step 5; `results/revision/a3_pcal_conditional.md` |
| 2018 test set: GO of 2 July 2018; 820 genes, 809 after circularity filter (106 of 5,965 targets removed) | — | `results/holdout_eval/SUMMARY.md` ("H") |
| SLC25A51 18/19, FIRRM 14/15 targets from DepMap-citing papers | — | old JOURNEY TP2; `results/holdout/circularity_summary.md` |
| Specification written 31 minutes before the single look | `fa21808` 22:19 → `aa381fc` 22:50 | old JOURNEY TP5; `LOOKS.md` |
| Blind literature agent, two judges, three decoys per gene, names hidden, judges validated first | — | old METHOD Step 7; `docs/AGENT_PROMPTS.md` |
| Independent data classes (interaction, co-abundance, localisation, Perturb-seq, structure) | — | old METHOD Step 6 |

## ANKRD52 (worked example)

| Fact | Value | Source |
|---|---|---|
| Rank 1 of the top 40 | rank 1 | `results/ledger/top40_primary.tsv` row 1 |
| Experimental GO rows only "protein binding"; 6 focused of 62 papers; UniProt score 3 | — | `docs/explainer/worked_example_output/worked_example.json` (`step0`) |
| Top partners AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8, TNRC6B; PPP6C 8th | scores 25.8 … 13.6 | `docs/explainer/worked_example_output/step2_neighbours_top25.tsv` |
| TARBP2 excluded (same arm, Dicer cofactor) | would have ranked 9th | old METHOD worked example Step 4 |
| Split-half overlap about 12 of 25; look-alikes about 0 | R = 0.472 (10,10,13,13,13); null mean 0.0037 | `worked_example.json` (`step3`); old METHOD worked example |
| Prediction "regulatory ncRNA-mediated gene silencing" (GO:0031047), 8 supporting partners | S = 158.11 | `worked_example.json` (`step4`); `docs/explainer/worked_example_output/step4_top5_terms.tsv` |
| PP6 phosphatase term ranks 37th | — | old METHOD worked example Step 4 |
| Confidence 0.141, highest of 2,583 | 0.14102 | `results/ledger/pcal_summary.json` (`max_p_cal`); `results/ledger/top40_primary.tsv` |
| Judges: real statement +1/+1; three decoys 0/0 (synaptic transmission, deacylase activity, dicarboxylic acid metabolism) | packet J071 | `docs/explainer/worked_example_output/step7_judging.tsv` |
| Function already published (AGO2 dephosphorylation cycle, PMID 28114302) | Golden 2017 | old METHOD worked example Step 1; `references/literature_refs.tsv` (Golden2017) |
| Earlier catalogues linked it to the microRNA machinery | Kim 2019; Wainberg 2021 | old METHOD worked example Step 1 |

## Results (scorecard)

| Fact | Value | Source |
|---|---|---|
| Top guess right: this method | 3.0% (1.8–4.3%), 24 of 809 | `results/holdout_eval/SUMMARY.md`; `results/holdout_eval/fig_precision_by_method.tsv` |
| Look-alike (matched-gene) null; prior-only | 0.5% (0.3–0.8%); 0.0% | same |
| GLS; Pearson | 2.3% (1.3–3.5%), Δ +0.006 (−0.005 to +0.017); 2.7% | same |
| Homology; hu.MAP transfer | 21.8% (18.4–25.3%); 4.9% | same (secondary batch) |
| Strongest fifth; weakest two fifths; complex membership; reweighted to U | 11.7% (6.7–17.4%); 0%; 18.2%; 1.2% | `results/holdout_eval/SUMMARY.md` (quintiles, U-reweighted); old METHOD results table (complex membership) |
| Homology-else-co-essentiality | 22.4% (+0.6 points, +0.1 to +1.2) | `results/revision/a7_combination_rules.tsv` |
| 15 of 24 co-essentiality hits missed by homology | — | old INSIGHTS Bio-1; old JOURNEY TP5 |
| Leave-one-out accuracy | 13.9% (0.1385, 2,519 genes) | `results/calibration/label_shuffle.md` line 7 |
| Calibration: mean out-of-fold 0.031 vs observed 0.031; slope 0.82 (0.51–1.13); c 0.855; Brier 0.0294 vs 0.0300 constant (≈2% skill); 24 events | — | `results/holdout_eval/calibration.md`; `results/holdout_eval/SUMMARY.md` |
| No gene ≥ 0.3 or ≥ 0.5 | 0, 0 | `results/ledger/pcal_summary.json` |
| Expected confirmations: 30.5 (13.8–49.7) conditional; ~4.9 (2.2–8.1) unconditional; annotation rate 16% ("1 in 6") | 775/4,822 = 0.161 | `results/ledger/M6_SUMMARY.md`; `results/revision/numbers_a3.json`; manuscript abstract |
| 82% of expected confirmations from genes failing the reproducibility check; ~1 (0.9) for 269 assessable genes | derived for the old explainer | old DISCREPANCIES B19; `results/ledger/M6_SUMMARY.md` (Σp_cal 5.49 over 269) |
| Simpler models share 7–14 of the top 40 | — | old METHOD Step 5; `results/revision/a4_simple_model_top40.tsv` |
| Literature: 18/40 vs 3/120, p = 0.0002 | — | `results/m7/judge/analysis_main.md` |
| GO term only 16/40, p = 7 × 10⁻⁴; module-label rule not logged before judging | — | `results/revision/a5_judging_sensitivity.tsv`; old JOURNEY TP7 |
| 16 of 18 supported were already published (N1); 31/40 N1 | — | `results/m7/judge/analysis_main.md` (N1 rows) |
| Judge validation 9/10 vs 1/30 | — | `results/m7/judge/analysis_hval.md` |
| 30 lower-confidence genes: 1/30 supported | — | `results/m7/judge/analysis_main.md` (extra30) |
| Strong uncalibrated list: 19/20 supported, 20/20 with earlier links | — | `results/m7/judge/analysis_main.md` (s20); `results/revision/SUMMARY.md` §A2 |
| Independent-data support 32% / 28% / 22% (247 each) | — | `results/ledger/M6_SUMMARY.md` |
| Robustness checks failed 221 of 269 | — | `results/ledger/M6_SUMMARY.md` |
| 34/40 prior link; 6/40 no prior; 3 of 10 report genes in Wainberg 2021 Supp. Data 3 (CCDC71L, C5orf34, INAFM1) | — | `results/revision/SUMMARY.md` §A2 |
| 9 of 10 reports needed novelty corrections; only PLEKHH3 no precedent (proposed PI3K/AKT brake, co-advantage partner of PTEN) | — | `results/revision/report_novelty_corrections.md`; manuscript abstract; old JOURNEY TP8 |

## Journey and roles

| Fact | Value | Source |
|---|---|---|
| Moment 1 span 20:06–20:18: time-split test already primary in DESIGN v1 (`f1cb5c3`, 20:06, from the literature review), hardened by round-1 review (`3e6b162`, 20:18) | — | old DISCREPANCIES A1; old JOURNEY TP2 |
| Moment times (settling commits) | 20:18 (`3e6b162`), 21:00 (`afed1dd`), 21:55 (`0e76668`), 22:50 (`aa381fc`), 04:55 (`c4eadf5`), 07:47 (`3f3a65b`) | `docs/explainer/journey_data.json` |
| Six moments merge the old eight turning points: 1 = TP2, 2 = TP1, 3 = TP3, 4 = TP4+TP5, 5 = TP6, 6 = TP7 caveats + TP8; moment 6 span 07:47–10:26 (`3f3a65b` → `a739f06`) | — | old JOURNEY |
| No commits 23:11:36 (`70864b2`) to 04:55:05 (`c4eadf5`); machine asleep for most of it by the PI's account (03:57 is a sleep-blind timer estimate, not a commit time). Not shown in the v2 figures; the timeline figure was replaced | — | `git log`; old DISCREPANCIES B12, C1 | `docs/explainer/journey_data.json`; old DISCREPANCIES C1 |
| Run span 19:39 29 Oct to 10:26 30 Oct 2026 UTC ("about 15 hours") | 14 h 47 min | old JOURNEY intro |
| First assessability rule was a quantile, not a null (round-1 statistics reviewer) | — | old JOURNEY TP3; `reviews/round1_statistics.md` item 11 |
| PI overrode the "clean-first" fill; separate strong-signal list defined before literature work | — | old JOURNEY TP6 |
| Referees: conditional confidence (30.5 → ~4.9), null-inflated census, complex subunits admitted, novelty unchecked | — | old JOURNEY TP8; `reviews/ms_round1_referee_*.md` |
| Title wording "modest accuracy, narrow reach and many already-published functions" | — | `manuscript/manuscript.md` title |
| PI = Claude Opus 5.5; sub-agents Opus 5.5 and Sonnet 5.5; ~60 by PI estimate; run log has one row | — | old JOURNEY "The research process"; old DISCREPANCIES A9 |
| Human: brief, DepMap files, restart after usage-limit pause, publication instructions; no recorded scientific direction (PI's account, not verifiable) | — | old JOURNEY; old DISCREPANCIES A8 |
| Design reviews found 7 then 32 gaps, fixed within ~1 hour, missed the big problems ("dozens of quick fixes") | — | old JOURNEY "Where it went in circles" |
| 22 post-freeze deviation entries (file has 23; the 23rd is a wording erratum); no longer quoted in v2 | — | `DEVIATIONS.md`; old DISCREPANCIES B4 |
| Human role is the PI's account; no transcript exists | — | old DISCREPANCIES A8 |

## Facts added in revision 2 (after FACT_CHECK.md and READER_TEST.md)

| Fact | Value | Source |
|---|---|---|
| Gene sets: 4,271 measurable; 646 reproducible; 2,583 with confidence; 269 in both | — | `results/ledger/M6_SUMMARY.md` (support-category table) |
| Of top 40: 31 with established function (N1); 16 of those supported; 2 supported among the 9 others (N2); 15 N1 not supported (not addressed or contradicted; 20 unaddressed and 2 contradicted over all 40) | — | `results/m7/judge/analysis_main.md` |
| 34/40 prior link to a top-10 partner, "not necessarily the same function"; 3/40 explicit predictions (Wainberg 2021 Supp. Data 3: CCDC71L, C5orf34, INAFM1) | — | `results/revision/SUMMARY.md` §A2 and its note ("do not check that the resource assigned the same function. Only Wainberg Supp. Data 3 is an explicit function prediction") |
| Support fell with rank: 12/20 for ranks 1–20, 6/20 for ranks 21–40; extra30 1/30; S20 19/20 | — | `manuscript/manuscript.md` line ~480; `results/m7/judge/analysis_main.md` |
| Homology makes a guess for 57% of test genes | coverage 0.570 | `results/holdout_eval/SUMMARY.md` (secondary batch) |
| Homology terms = IEA/ISS/IBA (electronic, sequence similarity, phylogenetic); may partly reflect curators confirming electronic terms (untested) | — | old METHOD Step 5 comparators; old DISCREPANCIES C5 |
| Calibration "not detectably miscalibrated", 24 events; slope 0.82 (0.51–1.13) | — | `results/holdout_eval/calibration.md`; old DISCREPANCIES A4 |
| Leave-one-out gap partly a population difference (known genes more essential, better connected; SMD 0.1–0.5) | — | old INSIGHTS Meth-1; `results/holdout_eval/SUMMARY.md` (covariate SMD table); old DISCREPANCIES C4 |
| Pre-registered look taken once; later logged exploratory analyses touched the test set | — | `LOOKS.md`; FACT_CHECK.md Step 5 note |
| Independent-data sources admitted on known complexes before predictions; final support rule and robustness checks not validated on known positives | 11 of 12 pair sources passed admission | old METHOD Step 6 |
| Robustness checks: lineage leave-out (most dependent lineage), DEMETER2 RNAi replication, TP53 dependence | — | `results/ledger/M6_SUMMARY.md`; old METHOD Step 6 |
| Rahman 2021 documents mitochondrial dominance in screen benchmarks | — | `references/literature_refs.tsv`; old JOURNEY TP6 |
| Figure (e) "claims shrank": 13.9→3.0%; 8.9→3.1%; 646→≥~322; 30.5→~4.9; 18→2 (supported genes not N1) | — | rows above |
| DDX6 is the 8th supporting partner, rank 23 | — | `docs/explainer/worked_example_output/step2_neighbours_top25.tsv` |

## Judgement calls made in this version

- "About 320" real-signal genes rounds both bases (322 on 646; 324 / "about 320" on 635). The fine-print row gives both.
- "About 1 in 8" for 11.7% and "about 1 in 30" for 3.0% are rounded readings of the exact values in the fine print.
- "Homology" is the project's homology baseline: the gene's own 2018 IEA/ISS/IBA GO terms, ranked, then frequency.
  Described as "computer-inferred GO terms ... transferred from related sequences and protein families".
- The funnel now shows 269 (reproducible and calibrated) but skips 245 (after artefact exclusions; old METHOD Step 6).
- Figure (e) shows the share of each first estimate that survived; the 2 "not already characterised" are the supported
  top-40 genes not classed N1 (both N2, partial evidence), so the README says "function not already established".
- Figure (d) panel 2 uses the out-of-fold mean predicted probability (0.031) as "promised" for the 2018-test-set model.
