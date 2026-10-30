---
title: "S1 Text. Supplementary results: verification, sensitivity and secondary analyses, the rediscovery table and the candidate-report narrative"
---

<!-- S1 Text for "A pre-registered, temporally validated evaluation of co-essentiality function predictions for
uncharacterised human genes". Material moved from the main Results in revision round 2 (reviews/ms_round2_*.md), with
its numbers and src tags unchanged unless stated. Labels as in the main text: [pre-specified], [deviation],
[exploratory], [post-review exploratory] (analyses requested by the referees, computed after peer review into
results/revision/; no frozen rule changed) and [descriptive]; [post-review] alone marks a table column added after review.
Citations are given by author and year; full references are in the main text. -->

# S1 Text

This text holds the detailed verification, sensitivity and secondary analyses summarised in one sentence each in the
main Results, the list of literature-supported predictions (Table A, formerly Table 2 of the main text) and the full
narrative of the ten candidate reports. Section headings follow the main Results. Every number carries a source comment
in the Markdown source (`manuscript/supplementary/S1_Text.md`).

## A. Tool verification and ranker choice

With the tool's own command-line scripts, the internal-test average precision was 0.3451 for zavg_BEF, 0.2423 for GLS,
0.1463 for Spearman and 0.1341 for Pearson <!-- src: results/verification/tool_reproduction.md -->. The published values
are 0.345, 0.242, 0.146 and 0.134 <!-- src: results/verification/tool_reproduction.md -->, so every method fell inside
the pre-specified tolerance of ±0.005 <!-- src: results/verification/tool_reproduction.md -->. All 14
<!-- src: results/verification/sanity_checks.md --> sanity checks passed, including Chronos sign, exact symmetry and
median within-complex scores of 4.06–16.90 <!-- src: results/verification/sanity_checks.md --> for seven reference
complexes. Our GLS and Pearson rows matched the tool's to 2.96 × 10⁻⁷ <!-- src: results/verification/baseline_rows.md -->.

The ranker was chosen once, on 2,519 <!-- src: results/calibration/loo_ranker_choice.md --> characterised
leave-one-out (LOO) genes, by the frozen mean-reciprocal-rank (MRR) rule [pre-specified]. Raw neighbour support (R1)
won with an MRR of 0.169, against 0.140 for the hypergeometric ranker (R2), 0.111 for the empirical ranker (R3) and
0.073 for prior-only <!-- src: results/calibration/loo_ranker_choice.md --> (S1A Fig). Every circularity variant gave
the same choice. When annotation rows were shuffled among genes of similar annotation count, R1 precision@1 fell from
0.139 to 0.015, below the prior-only level of 0.036 <!-- src: results/calibration/label_shuffle.md --> (S1B Fig).

## B. C1: census details

**Rank-biased overlap.** A rank-biased-overlap version of the reproducibility statistic gave 704 assessable genes,
against 635 with set overlap on the same (frozen) expression column <!-- src: results/assessability/summary.md -->; the
two statistics are closely correlated (Spearman 0.991 <!-- src: results/assessability/summary.md -->). In the headline
stratum, 590 of 2,439 <!-- src: results/assessability/summary.md --> genes are assessable with the frozen expression
column.

**Strata.** Only 2 of 516 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> chemosensory
and epidermal genes and 46 of 742 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv -->
tandem-cluster genes were assessable, against 598 of 3,666
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> other genes. By profile variability, the
counts were 437, 138 and 71 of 1,425 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> genes
in the high, middle and low tertiles. Secreted proteins (13 of 297
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv -->) and genes outside the tool background (31
of 484 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv -->) were rarely assessable. Mean R(g)
was 0.041 in U against 0.078 in H and 0.112 in the LOO sample <!-- src: results/assessability/summary.md --> (S2A Fig).

**Null-adjusted assessability [post-review exploratory].** Under the stated assumption, observed calls in a stratum are
Tπ + (N − T)α, where N is the number of expressed genes, T the number with real signal, π the power and α the
clean-negative false-call rate. Subtracting Nα therefore gives T(π − α), the excess of calls over the null expectation,
and not T itself. The excess is 243 (173–306) <!-- src: results/revision/a6_assessability_null_adjusted.tsv --> with
rates by any-dependency class and 271 (202–331) <!-- src: results/revision/a6_assessability_null_adjusted.tsv --> with
rates by profile-SD tertile (241 and 269 <!-- src: results/revision/a6_assessability_null_adjusted.tsv --> under the
design's expression definition). At full power (π = 1), T = (observed − Nα)/(1 − α) per stratum, which gives 324
(248–389), 6.6% of U, by dependency class and 325 (251–387) by SD tertile
<!-- src: results/revision/a10_assessability_excess_and_implied.tsv -->; lower power would raise these values. The
`implied_true` column of `a6_assessability_null_adjusted.tsv` is the excess over the null, not an implied count of
true genes; `a10_assessability_excess_and_implied.tsv` gives both quantities under their correct names.

**Recall probe on the random sample.** A closed-book language model without tools "recognised" 24 of the 50
<!-- src: results/audit/recall_probe_random50.tsv --> genes: 18 of 21 N1, 3 of 13 N2 and 3 of 16 N3 genes
<!-- src: manuscript/figures/source_data/Fig1d_curation_lag_audit.tsv -->.

## C. C2: hold-out sensitivity and secondary analyses

**Robustness of the primary test [pre-specified].** Precision@1 on the ten split-half networks ranged from 0.025 to
0.038 <!-- src: results/holdout_eval/SUMMARY.md -->, and both differences excluded zero in 10 of 10
<!-- src: results/holdout_eval/SUMMARY.md --> (S2C Fig). Across the circularity sensitivities precision@1 was
0.030–0.032 <!-- src: results/holdout_eval/SUMMARY.md -->, and the test passed in all five. The R1 tie-break was not
specified in the design; implemented as ascending GO identifier, it affects 401 of 820 <!-- src: DEVIATIONS.md --> H
genes, and the reverse order gives 0.032 <!-- src: DEVIATIONS.md --> with the primary still passing [deviation].
Restricting candidates and targets to terms with at most 50 genes gave 0.029 (0.017–0.044) on 649
<!-- src: results/holdout_eval/SUMMARY.md --> genes. The primary test also passed with t0 = 2019-07, with
post-cut-off-dated targets, at K = 10 and 50, and without same-arm and paralogue exclusions (precision@1 0.028–0.034)
<!-- src: results/holdout_eval/SUMMARY.md -->. Effective sample sizes were 719 and 722
<!-- src: results/holdout_eval/core.md --> (underpowered threshold 300).

**Other metrics [pre-specified].** The MRR difference from prior-only was +0.010 (−0.004 to +0.025)
<!-- src: results/holdout_eval/SUMMARY.md --> and did not exclude zero; prior-only often places a true term just below
rank 1. Predicted terms were broad: the median top-1 term had 132 annotated genes (IQR 84–176), and only 13%
<!-- src: results/holdout_eval/SUMMARY.md --> had 50 or fewer. Removing ETC complex I and the mitoribosome from the V1
targets and lists left V1 precision@1 unchanged <!-- src: results/holdout_eval/SUMMARY.md -->. By the size of the
gene's smallest target, the difference from GLS was +0.011 (−0.002 to +0.024) for targets of at most 50 genes and
−0.013 (−0.032 to 0.000) for larger ones <!-- src: results/holdout_eval/SUMMARY.md -->. Secondary metrics without
multiplicity control favoured zavg_BEF over GLS modestly (MRR +0.016, +0.005 to +0.027)
<!-- src: results/holdout_eval/SUMMARY.md -->. hu.MAP module transfer exceeded zavg_BEF by 0.020 (0.004–0.037)
<!-- src: results/holdout_eval/SUMMARY.md -->. H genes have stronger co-essentiality signal than U genes (standardised
mean difference in top-K mean zavg_BEF +0.253, in R(g) +0.228) <!-- src: results/holdout_eval/SUMMARY.md -->; after
reweighting to U, both primary differences still excluded zero (+0.012 and +0.008, lower bound 0.002)
<!-- src: results/holdout_eval/SUMMARY.md -->. Precision@1 was not broken down by module family, because 552 of the 775
H genes with a prediction fall in the "other" family <!-- src: results/revision/a4_family_hits_H.tsv -->.

**Calibration details.** Two of the four sign-constrained coefficients, for R(g) and term size, were fitted at their
bound of 0 <!-- src: results/holdout_eval/calibration.md -->. In the five lowest deciles (p_cal ≤ 0.013) no prediction
was confirmed; in the top decile, a mean prediction of 0.170 compared with an observed rate of 0.115 (0.062–0.205)
<!-- src: results/holdout_eval/calibration.md -->. [Post-review exploratory] The cluster-bootstrap slope interval is
0.59–1.09, the c-statistic is 0.855 (cluster-bootstrap 0.805–0.903), and the mean prediction exceeds the observed rate
by only 0.0001 <!-- src: results/revision/a4_calibration_models.tsv -->; the Brier interval (0.0198–0.0412)
<!-- src: results/holdout_eval/calibration.md --> contains the constant-rate value. The signalling/lineage family had no
hits in H and received a coefficient of −11.86 <!-- src: results/holdout_eval/calibration.md -->: 0 of 111 signalling
genes were hits, and the one-sided 95% upper bound on their hit rate is 0.027
<!-- src: results/revision/a4_family_hits_H.tsv; results/revision/numbers_a4.json -->. Because every signalling gene
ranks below every hit, separation also inflates the c-statistic; without the signalling genes the out-of-fold slope
was unchanged (0.82, 0.51–1.13) and c fell to 0.830 (664 genes) <!-- src: results/revision/numbers_a4.json -->. Models
with top-K mean zavg_BEF alone (24 events per parameter), or with annotation coverage added, cross-fitted in the same
way, gave slopes of 0.93 (0.60–1.25) and 0.89 (0.57–1.21), c-statistics of 0.835 and 0.832, and Brier skills of 0.037
and 0.036 <!-- src: results/revision/a4_calibration_models.tsv --> (S4D Fig). These intervals overlap the frozen
model's, so the comparison cannot tell over-parameterisation of the frozen model from signal that the simpler models
miss. Five families had only 10–19 H genes each <!-- src: results/holdout_eval/calibration.md --> and so receive no
p_cal under the support rule. The LOO-fitted model had intercept −1.39 (−1.84 to −0.95) on H
<!-- src: results/holdout_eval/SUMMARY.md -->.

**Named controls [pre-specified case series].** AIRIM's true term ranked 89th of 125
<!-- src: results/holdout_eval/controls_case_series.tsv -->. Exclusion of annotations citing DepMap or co-essentiality
papers applied to the single new term of SPRING1, TEDC1, TEDC2, POU2AF2 and POU2AF3, to 4 of 5 for CCDC32, 20 of 23 for
SLC25A51 and 17 of 18 for FIRRM <!-- src: results/holdout_eval/controls_case_series.tsv -->. [Post-review exploratory]
All of INTS15's top ten partners are Integrator subunits or INIP, and its top terms were snRNA metabolism and snRNA
transcription; but of its 11 new GO terms, 8 were not reportable, because fewer than two of its neighbours carried them
at t0, and 3 fell outside the term-size window <!-- src: results/revision/a8_control_target_reasons.tsv -->. TMEM41B's
partners (VMP1, SYVN1, DERL2, SEL1L and others) gave ER-stress and ERAD terms, while 16 of its 17 new terms, including
autophagosome assembly, were supported at t0 by at most one neighbour
<!-- src: results/revision/a8_control_target_reasons.tsv -->. For these controls, t0 annotation of the neighbours, not
the network, limited accuracy. The descriptive module label for SPRING1 was the SREBP–SCAP complex
<!-- src: results/holdout_eval/controls_case_series.tsv -->.

**Complementarity [exploratory].** The oracle union of zavg_BEF and homology was 0.019
<!-- src: results/holdout_eval/exploratory_complementarity.md --> above homology (gene-level bootstrap interval of the
union 0.206–0.266 <!-- src: results/holdout_eval/exploratory_complementarity.md -->; the main text quotes the cluster
bootstrap). The reverse-priority rule, zavg_BEF where it predicts and otherwise homology, reached 0.036
<!-- src: results/revision/a7_combination_rules.tsv -->. In the 81 genes without a hu.MAP partner, zavg_BEF reached 0
<!-- src: results/holdout_eval/exploratory_complementarity.md -->. Within the top five terms, zavg_BEF found a true term
for 0.067 of genes and prior-only for 0.069 <!-- src: results/holdout_eval/exploratory_complementarity.md -->.

## D. C3: catalogue details

**Coverage.** Low neighbourhood annotation coverage was the commonest reason for no p_cal (536
<!-- src: results/ledger/pcal_summary.json --> genes). The family rule removed every prediction in the five
under-represented families: 119 centrosome/cilia/mitosis, 106 ribosome/translation, 97 nuclear RNA machinery, 70 DNA
replication/repair and 49 mitochondrial <!-- src: results/ledger/pcal_summary.json --> genes. Another 96
<!-- src: results/ledger/pcal_summary.json --> genes were excluded because their signal exceeded H's 95th percentile.
The model's ceiling follows from covariates bounded by H's 95th percentiles (top-K mean zavg_BEF ≤ 10.99, coverage
percentile ≤ 0.894 <!-- src: results/holdout_eval/calibration.md -->). The 133 boundary genes add an upper bound of 1.0
(0.5–1.9) <!-- src: results/ledger/pcal_summary.json --> to Σp_cal, and Tier A contributes 0.

**Other sensitivities of Σp_cal [post-review exploratory].** The 403 in-support signalling genes contribute 0.00004
because of the separated family coefficient; at the upper bound of the signalling hit rate they would contribute up to
10.7 <!-- src: results/revision/numbers_a4.json -->. Expressed in-support genes contribute 20.0 of the 30.5
<!-- src: results/revision/numbers_a4.json -->; the remainder comes from non-expressed genes, whose profiles carry
little functional signal. Under the simpler calibration models, Σp over the same 2,583 genes was 41.6 (zavg_BEF only)
and 38.6 (with coverage) <!-- src: results/revision/a4_simple_models_on_U.tsv -->; their top 40s shared only 7 and 14
genes with the primary top 40, because without the family term mitoribosomal and ribosome-biogenesis genes enter
<!-- src: results/revision/a4_simple_model_top40.tsv -->.

**False calls among clean negatives [pre-specified].** Of 1,167 <!-- src: results/ledger/negative_control.tsv -->
scorable clean-negative genes, 708 <!-- src: results/ledger/negative_control.tsv --> received an in-support p_cal. None
was Tier-A-like (rate 0, one-sided 95% upper bound 0.0026) <!-- src: results/ledger/negative_control.tsv -->, and none
was Tier-B-like, in every profile tertile. This zero rate is uninformative, because no expressed gene reached the
thresholds either. Clean negatives had a median p_cal of 0.010 and a maximum of 0.057
<!-- src: results/ledger/negative_control.tsv -->, against 0.014 and 0.141
<!-- src: results/ledger/negative_control.tsv --> for expressed, assessable genes (Fig 3A); p_cal separates the groups
mainly in the upper tail.

**Artefact flags [pre-specified].** Among the 4,137 predictions, locus flags touched 17, copy-number flags 1 and hub
partners 511 <!-- src: results/ledger/M6_SUMMARY.md -->; 218 <!-- src: results/ledger/M6_SUMMARY.md --> predictions were
hub-driven. In total 293 <!-- src: results/ledger/M6_SUMMARY.md --> carry a built-in exclusion from Tier A (a flag on at
least half of the supporting partners, or hub-driven). The locus flag was applied without strand information, as a
superset of the frozen rule [deviation].

**Orthogonal support [pre-specified].** The support test was run on 247 <!-- src: results/ledger/false_support.tsv -->
anchor genes (all candidates evaluated during the top-40 fill), together with one matched-gene prediction and one
decoy-term prediction per anchor. In a paired comparison over the same anchors [exploratory; a post hoc test,
unadjusted], real predictions passed the Tier-A support rule more often than decoys (+0.097; 54 vs 30 discordant pairs;
exact McNemar p = 0.012) <!-- src: manuscript/figures/source_data/derived_numbers.tsv --> but not detectably more often
than matched-gene predictions (+0.040; 47 vs 37; p = 0.33)
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->. Physical-interaction support showed the clearest
contrast (0.12 real, 0.03 matched, 0.01 decoy), whereas co-abundance and localisation support were common in all three
sets <!-- src: results/ledger/false_support.tsv -->. Contradictions were rare (0.004 of real predictions) and arose only
through the four-source localisation reading [deviation]; the HPA-only rule never fired
<!-- src: results/ledger/false_support.tsv -->.

**Top-40 composition and checks.** The pool contains no mitochondrial-family genes
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->, so the mitochondrial cap did not bind. Thirty-six top
terms fall in the "other" family and 4 in ER/Golgi/secretory
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->. The commonest terms are transcription elongation,
epigenetic regulation of gene expression and response to ER stress (3 genes each)
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->. The lineage leave-out changed the top term for 10
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes. DEMETER2 RNAi did not replicate the partner
correlations for 24 of the 30 <!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes in which it could
be measured, and 11 <!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes carry a TP53 flag. Across the
pool, DEMETER2 failed to replicate for 182 of 204 <!-- src: results/ledger/M6_SUMMARY.md --> measured genes, a rate that
may reflect the RNAi data as much as the predictions. The check was never validated on positive controls, and the S20
machinery genes, on which it could have been, have no p_cal and were not scored, so a DEMETER2 flag is not evidence
against a prediction. Twenty-seven of the top 40 have support from at least one orthogonal class, and 25 have
diagnostic-class support <!-- src: manuscript/figures/source_data/derived_numbers.tsv -->; given the false-support
rates above, these counts are not validation.

**Clean-first list.** The "clean-first" list built by the implementing agent, which applied the top-40 checks as
demotions, shares 20 <!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes with the primary top 40 and
has Σp_cal 2.04 (1.05–3.24) <!-- src: results/ledger/M6_SUMMARY.md --> (S3 Table). Only the primary top 40 was judged.
[Post-review exploratory] Of the 20 shared genes, 12 were supported by the judges (11 on the term alone), against 6 of
the 20 primary genes that the clean-first list did not contain (5 on the term alone)
<!-- src: results/revision/a10_round2_numbers.tsv -->. The checks therefore did not pick out the less supported half of
the list, but the clean-first genes not in the primary top 40 were never judged.

## E. C4: judging details

**Recall probe on the candidates [pre-specified; extended to S20 and extra30].** The probe "recognised" 52 of the 90
<!-- src: results/m7/recall_probe_90.tsv --> candidates: 22 of 40 in the top 40, 19 of 20 in S20 and 11 of 30 in
extra30 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Recognition followed the literature
class assigned later by agent L (Fig 5D): 43 of 59 N1, 8 of 24 N2 and 1 of 7 N3 candidates
<!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->.

**Blind literature screen.** Of agent L's 887 evidence items, 518 were focused functional studies and 4 were flagged as
DepMap-derived <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. In extra30 the split was 11 N1,
14 N2 and 5 N3 <!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv -->. Including the 10 H validation
genes, all N1 as expected <!-- src: results/m7/judge/analysis_hval_genes.tsv -->, agent L classed 69 of 100 genes as N1
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Across the 90 candidates, 58 of 80 D3-only genes
were N1 against 1 of 10 genes with a low UniProt score <!-- src: results/revision/a1_N1_rates_by_route_and_flag.tsv -->
[post-review exploratory].

**Judge validation and agreement [pre-specified].** On the validation set, between-instance agreement was κ = 0.931
over 40 statements, with one disagreement <!-- src: results/m7/judge/analysis_hval.md -->, which the adjudicator
resolved as supported; it is the single supported decoy <!-- src: results/m7/judge/scores/ADJ_hval.tsv -->. On the main
sets, both disagreements involved real statements, for WDR7 (S20) and DPCD (top 40); the adjudicator resolved both as
supported because the evidence matched the module label, not the GO term
<!-- src: results/m7/judge/scores/ADJ_main2.tsv --> <!-- src: results/m7/judge/scores/ADJ_main3.tsv -->.

**Module-label crediting.** Three supported real statements rest on the module label alone: YPEL5 (GID/CTLH complex;
Wnt not shown), DPCD (R2TP/PAQosome; transcription elongation not shown) and WDR7 (V-ATPase/RAVE; iron homeostasis not
shown) <!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv, J2_main2.tsv, J2_main3.tsv, ADJ_main2.tsv, ADJ_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->,
and for DDX19A, support for "cell population proliferation" came from cancer cell-line proliferation studies. All six
supported decoys across the sets were supported on the term
<!-- src: results/revision/a5_judging_sensitivity.tsv; results/revision/a5_plus1_basis.tsv -->, so module crediting
helped only real statements.

**Alternative tests [post-review exploratory].** An exact slot-permutation test, which uses the exchangeability of
slots directly, gave p = 2.3 × 10⁻⁷ (term-only 2.6 × 10⁻⁶), and averaging the differences within clusters of genes that
share a module label, because complex-mates share literature, gave p = 0.0022 over 17 non-zero clusters (term-only
0.0058) <!-- src: results/revision/a5_judging_sensitivity.tsv -->. The conclusion does not depend on module crediting or
on gene-level independence.

**Contradicted statements.** The two contradicted top-40 statements, for the N1 genes TLNRD1 and KDF1
<!-- src: results/m7/judge/analysis_main_genes.tsv -->, failed on direction: TLNRD1 promotes rather than inhibits cell
migration, and KDF1 inhibits rather than activates NF-κB signalling
<!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv, J2_main2.tsv, J2_main3.tsv, ADJ_main2.tsv, ADJ_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->.

**Secondary sets.** In extra30, support was 0 of 6 in each of the four lowest p_cal quintiles and 1 of 6 in the
highest <!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv -->. The two extra30 genes whose p_cal
exceeds the top-40 minimum, MARF1 (0.099, contradiction) and TMEM60 (0.037, built-in artefact exclusion), were excluded
from the top 40 <!-- src: results/m7/extra30.tsv -->, which is why the highest extra30 bin overlaps the top-40 range.
Ranks 1–20 of the top 40 had p_cal 0.055–0.141 and ranks 21–40 p_cal 0.036–0.050
<!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv -->.

**Overlap with earlier catalogues [post-review exploratory].** Of the primary top 40, 9 have an edge or cluster in the
2019 co-essentiality network of Kim et al. <!-- src: results/revision/a2_novelty_overlap.tsv; manuscript/figures/source_data/FigS4_derived_numbers.tsv -->.
The six top-40 genes with no prior in any resource are PLEKHH3, LGALS9B, FBXL18, SASH3, DDX19A and DPCD
<!-- src: results/revision/a2_novelty_overlap.tsv -->.

**Table A. Top-40 and S20 predictions judged supported by the literature (blinded, adjudicated).** Formerly Table 2 of
the main text. p_cal is given for the primary top 40 and the uncalibrated top-K mean zavg_BEF (zavg) for S20. UniProt
score; CP: UniProt annotation score and whether the gene is a curated Complex Portal subunit [post-review]. L class,
novelty class from the blind literature agent. Probe, recognised by the closed-book recall probe. Basis: whether judges
cited the GO term (term) or only the module label (module); "generic" marks support from cancer cell-line
proliferation studies. Module labels are shortened; full names are in
manuscript/figures/source_data/Table2_rediscovery.tsv.

| Set, rank | Gene | Predicted GO term | Module label | p_cal | zavg | UniProt score; CP | L class | Probe | Basis |
|---|---|---|---|---|---|---|---|---|---|
| top 40, 1 | ANKRD52 | regulatory ncRNA-mediated gene silencing | RISC complex | 0.141 | – | 3; – | N1 | yes | term |
| top 40, 3 | CNOT10 | regulation of RNA stability | CCR4-NOT deadenylase complex | 0.116 | – | 5; CP | N1 | yes | term |
| top 40, 4 | TRAPPC5 | Golgi vesicle transport | TRAPP III complex | 0.114 | – | 4; CP | N2 | yes | term |
| top 40, 6 | SSR4 | protein N-linked glycosylation | ER protein-containing complex | 0.091 | – | 5; CP | N1 | yes | term |
| top 40, 7 | CNOT11 | regulation of RNA stability | CCR4-NOT deadenylase complex | 0.080 | – | 4; CP | N1 | yes | term |
| top 40, 8 | MED31 | DNA-templated transcription initiation | RNA Pol II transcription regulator complex | 0.079 | – | 5; CP | N1 | yes | term |
| top 40, 9 | YPEL5 | positive regulation of Wnt signaling pathway | GID E3 ubiquitin ligase complex | 0.078 | – | 5; CP | N1 | yes | module |
| top 40, 10 | TMEM208 | establishment of protein localization to membrane | ER protein-containing complex | 0.078 | – | 5; – | N1 | yes | term |
| top 40, 11 | PHC3 | epigenetic regulation of gene expression | PcG protein complex | 0.077 | – | 5; CP | N1 | yes | term |
| top 40, 15 | TMED7 | Golgi vesicle transport | cytoplasmic ubiquitin ligase complex | 0.064 | – | 5; – | N1 | yes | term |
| top 40, 18 | MGA | epigenetic regulation of gene expression | chromatin silencing complex | 0.059 | – | 5; CP | N1 | yes | term |
| top 40, 20 | TMEM209 | nucleus organization | nuclear pore complex | 0.055 | – | 5; – | N1 | no | term |
| top 40, 26 | PSMD13 | regulation of proteasomal protein catabolic process | proteasome complex | 0.047 | – | 5; CP | N1 | yes | term |
| top 40, 27 | COA4 | cytochrome complex assembly | MitoCarta: OXPHOS | 0.046 | – | 4; – | N1 | yes | term |
| top 40, 30 | GRIPAP1 | vesicle-mediated transport to the plasma membrane | vesicle tethering complex | 0.044 | – | 5; – | N1 | yes | term |
| top 40, 33 | BICRAL | transcription coregulator binding | GBAF (SWI/SNF) complex | 0.041 | – | 5; CP | N2 | yes | term |
| top 40, 38 | DDX19A | cell population proliferation | ER protein-containing complex | 0.036 | – | 5; – | N1 | yes | term (generic) |
| top 40, 40 | DPCD | DNA-templated transcription elongation | PAQosome co-chaperone complex | 0.036 | – | 3; – | N1 | no | module (adjudicated) |
| S20, 1 | COMMD3 | endosomal transport | Commander complex | – | 18.5 | 5; CP | N1 | yes | term |
| S20, 2 | COMMD2 | endosomal transport | Commander complex | – | 17.0 | 5; CP | N1 | yes | term |
| S20, 3 | NDUFB10 | NADH dehydrogenase activity | MitoCarta: OXPHOS | – | 16.7 | 5; CP | N1 | yes | term |
| S20, 4 | COMMD4 | endosomal transport | Commander complex | – | 16.4 | 5; CP | N1 | yes | term |
| S20, 5 | NDUFB2 | NADH dehydrogenase activity | respiratory chain complex I | – | 16.3 | 4; CP | N2 | yes | term |
| S20, 6 | NDUFA2 | NADH dehydrogenase activity | respiratory chain complex I | – | 16.3 | 5; CP | N1 | yes | term |
| S20, 7 | COMMD8 | endosomal transport | Commander complex | – | 16.3 | 5; CP | N1 | yes | term |
| S20, 8 | TADA2B | acyltransferase activity (non-amino-acyl groups) | SAGA complex, KAT2A variant | – | 16.2 | 5; CP | N1 | yes | term |
| S20, 9 | NDUFA11 | NADH dehydrogenase activity | MitoCarta: OXPHOS | – | 16.0 | 5; CP | N1 | yes | term |
| S20, 10 | COMMD10 | endosomal transport | Commander complex | – | 15.9 | 5; CP | N1 | yes | term |
| S20, 11 | WDR7 | intracellular iron ion homeostasis | proton-transporting two-sector ATPase complex | – | 15.8 | 3; CP | N1 | yes | module (adjudicated) |
| S20, 12 | WASHC3 | endosomal transport | Commander complex | – | 15.6 | 5; CP | N1 | yes | term |
| S20, 14 | CTU2 | tRNA metabolic process | Elongator holoenzyme complex | – | 15.5 | 5; – | N1 | yes | term |
| S20, 15 | NDUFB4 | NADH dehydrogenase activity | MitoCarta: OXPHOS | – | 15.5 | 4; CP | N1 | yes | term |
| S20, 16 | ELP5 | tRNA metabolic process | Elongator holoenzyme complex | – | 15.2 | 5; CP | N1 | yes | term |
| S20, 17 | ELP6 | tRNA metabolic process | Elongator holoenzyme complex | – | 15.0 | 5; CP | N1 | yes | term |
| S20, 18 | UNC50 | Golgi organization | vesicle tethering complex | – | 14.9 | 5; – | N1 | yes | term |
| S20, 19 | MED9 | regulation of transcription initiation by RNA Pol II | RNA Pol II transcription regulator complex | – | 14.8 | 4; CP | N2 | yes | term |
| S20, 20 | NUP43 | nucleocytoplasmic transport | nuclear pore complex | – | 14.8 | 5; CP | N1 | yes | term |

<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv (scripts/61_figure5.py: analysis_main_genes.tsv,
answer_key_slots.tsv, top40_primary.tsv, s20.tsv, L/index_batch_*.tsv, recall_probe_90.tsv); Basis column read from the
judges' justifications in results/m7/judge/scores/J1_main*.tsv, J2_main*.tsv and ADJ_main*.tsv. Complex labels
shortened (full names in the source TSV). UniProt
annotation score and Complex Portal subunit (CP) from results/revision/a1_U_entry_flags.tsv [post-review]. -->

Unsupported top-40 genes: 20 unaddressed and 2 contradicted (TLNRD1, KDF1); in S20, NR2C2AP was unaddressed
<!-- src: results/m7/judge/analysis_main_genes.tsv -->.

## F. Candidate reports: full narrative

**Review.** No fabricated citation was found among roughly 300 verbatim evidence spans checked
<!-- src: RESEARCH_TREE.md (M7b status summary); reviews/retro_M7.md -->, but every red-team review found numeric or
framing problems that changed the reports. After the first round of peer review, each report gained a statement of
what earlier catalogues had already published [post-review].

**Rediscoveries.** ANKRD52's co-essentiality neighbourhood is the miRNA biogenesis and silencing machinery (AGO2, XPO5,
DICER1, DROSHA, TNRC6A, DGCR8) with PPP6C further down <!-- src: reports/ANKRD52.md (§4) -->, and the AGO2–ANKRD52
co-dependency in DepMap had itself been reported (Fig S5C of Shui et al. 2023). Because AGO2 loss is near-neutral while
ANKRD52 loss is not, and PP6 has other substrates, the prior favours failure of the proposed AGO2 phospho-mutant rescue
of fitness. For BICRAL, an earlier draft's "paralogue-specific requirement" was downgraded after red-team review
because the paralogue BICRA tracks the same axis about twice as strongly (r 0.53 versus 0.27)
<!-- src: reports/BICRAL.md (§0) -->. For TRAPPC5, the only unrecorded element, a dependency that follows the TRAPPIII
arm (TRAPPC8/11/12/13), is one-sided because the TRAPPII-specific subunits have no recoverable co-essentiality structure
<!-- src: reports/TRAPPC5.md (§0, §4) -->, and we have not tested whether the other core subunits (TRAPPC1/3/4) share
the same leaning, in which case it would be a property of TRAPP in cancer lines rather than of TRAPPC5. RBM34's
pre-ribosome module had been reported by Wainberg et al. <!-- src: results/revision/a2_novelty_overlap.tsv -->, and its
predicted term is an artefact of the vocabulary <!-- src: reports/RBM34.md (§0) -->.

**PLEKHH3.** The co-dependency is absent in lymphoid lines <!-- src: reports/PLEKHH3.md (§0) -->. The checks that need
only DepMap data, lineage-adjusted partial correlations and an analysis excluding PTEN-null lines, were not run; until
they are, the signal is a low-amplitude co-advantage not yet controlled for lineage.

**C5orf34.** The signal is second-order: it comes from partner-list overlap (B-view z 23.8 with SPICE1) rather than
direct correlation (F-view z 2.4; raw r with SPICE1 0.06), and GLS gives a different top term
<!-- src: reports/C5orf34.md (§0, §4, §5) -->. Whether the centriole module itself loses coherence in TP53-wild-type
lines, a DepMap-only check, was not run; the experimental plan requires an isogenic TP53 arm.

**CCDC71L.** The Polycomb-dominated neighbourhood exists only after bias correction, the protein's high basic charge
makes non-specific chromatin association the prior <!-- src: reports/CCDC71L.md (§0) -->, and Wainberg et al. had
predicted an H3K27-methyltransferase function from a module with 8 of our top 10 partners
<!-- src: reports/CCDC71L.md (§0) -->. Its proposed IP-MS against a PxVxL mutant tests HP1 binding, a refinement
suggested by structural and hu.MAP data; the HP1 proteins themselves are not co-dependent with CCDC71L (r −0.105 to
−0.010) <!-- src: reports/CCDC71L.md (§3) -->, so that experiment tests the interaction-derived hypothesis, and a
Polycomb readout (H2AK119ub and H3K27me3 at Polycomb targets) is needed to test the co-essentiality one (S10 Table).

**TM2D1 and TM2D2.** They form a single observation: a co-dependency star with AUP1, JOSD1, STUB1 and CHIC2 whose "ER
stress" label rests on two partners and which shows no co-variation with the core ERAD machinery or UPR genes
<!-- src: reports/TM2D1.md (§0); reports/TM2D2.md (§0) -->; the shared dependency was already in Wainberg et al.'s
modules <!-- src: results/revision/a2_novelty_overlap.tsv -->.

**INAFM1.** The weakest report: its predicted term rests on partners with near-zero raw correlation, and its strongest
partners (NFE2L1, NGLY1, DDI2, the NRF1-activation axis) form one correlated axis to which it attaches weakly (r
0.12–0.21) <!-- src: reports/INAFM1.md (§0) -->; Wainberg et al. had predicted a related ubiquitination function
<!-- src: results/revision/a2_novelty_overlap.tsv -->.

**Orthogonal support.** Of the seven reports that are not rediscoveries, only RBM34 has admitted orthogonal support for
its term, and none was supported by the blinded judges, as expected for genes with partial or no literature.
