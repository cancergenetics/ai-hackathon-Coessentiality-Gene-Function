
# Results

The study design is summarised in Fig 1A; the notation is defined at the start of the Methods. Results are labelled
[pre-specified] (frozen design, DESIGN.md v2.3), [deviation] (a change logged in DEVIATIONS.md; the Methods list the
rows that were logged only after the affected result existed), [exploratory] (post hoc, before review; H looks logged in
LOOKS.md), [post-review exploratory] (requested by the referees; results/revision/, summarised in S4 Fig) or
[descriptive] (computed for presentation only).

## The tool reproduces its published performance on DepMap 26Q3

Before any prediction for the pre-registered genes, we checked the tool on our data (Fig 1A). With the tool's own
command-line scripts, the internal-test average precision was 0.3451 for zavg_BEF, 0.2423 for GLS, 0.1463 for Spearman
and 0.1341 for Pearson <!-- src: results/verification/tool_reproduction.md -->. The published values are 0.345, 0.242,
0.146 and 0.134 <!-- src: results/verification/tool_reproduction.md -->, so every method fell inside the pre-specified
tolerance of ±0.005 <!-- src: results/verification/tool_reproduction.md -->. All 14
<!-- src: results/verification/sanity_checks.md --> sanity checks passed, including Chronos sign, exact symmetry and
median within-complex scores of 4.06–16.90 <!-- src: results/verification/sanity_checks.md --> for seven reference
complexes. Our GLS and Pearson rows matched the tool's to 2.96 × 10⁻⁷
<!-- src: results/verification/baseline_rows.md -->.

The ranker was then chosen once, on 2,519 <!-- src: results/calibration/loo_ranker_choice.md --> characterised
leave-one-out (LOO) genes, by the frozen mean-reciprocal-rank (MRR) rule [pre-specified]. Raw neighbour support (R1)
won with an MRR of 0.169, against 0.140 for the hypergeometric ranker (R2), 0.111 for the empirical ranker (R3) and
0.073 for prior-only <!-- src: results/calibration/loo_ranker_choice.md --> (S1A Fig). Every circularity variant gave
the same choice. When annotation rows were shuffled among genes of similar annotation count, R1 precision@1 fell from
0.139 to 0.015, below the prior-only level of 0.036 <!-- src: results/calibration/label_shuffle.md --> (S1B Fig). The
choice and the calibration specification were logged before the hold-out was opened (LOOKS.md, commit f0922e1).

## C1: at most one in eight pre-registered genes is assessable

**Census.** Of the 4,924 <!-- src: results/assessability/assessability_U.tsv --> pre-registered genes, 4,275
<!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> have a DepMap column and 4,271 (86.7%)
<!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> are scorable (Fig 1B). Of these, 2,722
<!-- src: results/assessability/summary.md --> are expressed in DepMap lines, and 842 (19.7% of scorable)
<!-- src: results/assessability/summary.md --> have a split-half reproducibility p below 0.05 regardless of expression.
The pre-specified C1 count, genes that are scorable, expressed and assessable, is **646 (13.1% of U)**
<!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv -->. This count applies the design's definition of
"expressed", which includes lineage-restricted genes; the frozen gene table predates that wording, and with its
expression column the count is 635 (12.9%) <!-- src: results/assessability/summary.md --> [deviation; both reported]. In
the headline stratum (expressed, not chemosensory or epidermal, not in a tandem cluster), 598 of 2,525
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> genes are assessable (590 of 2,439
<!-- src: results/assessability/summary.md --> with the frozen column). A rank-biased-overlap version of the
reproducibility statistic gave 704 assessable genes, against 635 with set overlap on the same (frozen) expression column
<!-- src: results/assessability/summary.md -->; the two statistics are closely correlated (Spearman 0.991
<!-- src: results/assessability/summary.md -->).

**Strata.** Assessability tracked the strength of a gene's dependency profile (Fig 1C). Only 2 of 516
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> chemosensory and epidermal genes and 46 of
742 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> tandem-cluster genes were assessable,
against 598 of 3,666 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> other genes. Among
genes with any dependency (≥ 1% of lines below −0.5 <!-- src: preregistration/CRITERIA.md -->), 427 of 1,105
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> were assessable, compared with 219 of
3,170 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> without. By profile variability,
the counts were 437, 138 and 71 of 1,425 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv -->
genes in the high, middle and low tertiles. Secreted proteins (13 of 297
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv -->) and genes outside the tool background (31
of 484 <!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv -->) were rarely assessable. Mean
R(g) was 0.041 in U against 0.078 in H and 0.112 in the LOO sample <!-- src: results/assessability/summary.md -->
(S2A Fig).

**The reproducibility null is anti-conservative, so 646 is an upper bound.** Clean-negative genes, which are not
expressed in at least 95% of lines, reached split-half p < 0.05 in 153 of 1,167 cases (13.1%)
<!-- src: results/assessability/summary.md -->, well above the nominal 5%. The rate was 27.2%
<!-- src: results/assessability/summary.md --> among clean negatives with some dependency and 9.7%
<!-- src: results/assessability/summary.md --> among those without (S2B Fig). The matched-gene null of the
reproducibility test is therefore anti-conservative for genes with any dependency signal, and requiring expression
removes the genes in which this was measured without showing that the problem disappears in expressed genes. [Post-review
exploratory] If the clean-negative false-call rates apply to expressed genes of the same dependency class, about 392
(329–462) of the 635 calls on the frozen expression column are expected under the null, leaving 243 (173–306) genes,
4.9% (3.5–6.2%) of U, assessable beyond the null <!-- src: results/revision/a6_assessability_null_adjusted.tsv -->
(241, 169–306, under the design's expression definition; 269–271 with rates by profile-SD tertile
<!-- src: results/revision/a6_assessability_null_adjusted.tsv -->; S4C Fig). This is a bound under an untested
assumption, not an estimate of specificity; the pre-specified count of 646 stands as the C1 result, but it should be read
as an upper bound on the genes to which co-essentiality can speak.

**Published but uncurated functions.** An auditor with no access to co-essentiality output classed a pre-specified random sample of 50 U
genes (Fig 1D). For 21 genes (42%, Wilson 95% CI 29–56%) <!-- src: results/audit/curation_lag_audit.md --> the auditor
found direct functional evidence in a focused study (N1). Thirteen (26%) <!-- src: results/audit/curation_lag_audit.md -->
had partial evidence (N2) and 16 (32%) <!-- src: results/audit/curation_lag_audit.md --> had none (N3). Moving the
three borderline calls gave N1 rates between 38% and 46% <!-- src: results/audit/curation_lag_audit.md -->. For 13 of
the 21 <!-- src: results/audit/curation_lag_audit.md --> N1 genes the key evidence dates from 2021 or later. In a
closed-book recall probe, a language model without tools "recognised" 24 of the 50
<!-- src: results/audit/recall_probe_random50.tsv --> genes: 18 of 21 N1, 3 of 13 N2 and 3 of 16 N3 genes
<!-- src: manuscript/figures/source_data/Fig1d_curation_lag_audit.tsv -->. Roughly four in ten "uncharacterised" genes
thus already have published functions, so novelty must be checked against the literature (C4).

**Much of this reflects the definition of "uncharacterised" [post-review exploratory].** U required no experimental GO
biological-process or molecular-function annotation (D1) plus either a low UniProt annotation score (D2) or low focused
literature (D3). Of the 4,924 U genes, 3,819 entered through D3 alone; 2,248 have a UniProt annotation score of 4 or 5
(1,261 the maximum of 5), 288 are curated Complex Portal subunits and 1,218 have an experimental GO cellular-component
annotation, which D1 ignores <!-- src: results/revision/a1_flag_counts.tsv -->. In all, 1,933 U genes carry at least one
of these definition-artefact flags (score 5, Complex Portal subunit or experimental GO CC)
<!-- src: results/revision/a1_flag_counts.tsv -->. D3 counts only papers about at most ten genes, so subunits described
in multi-subunit papers look unstudied. In the random 50, the N1 rate was 19 of 34 (56%, 40–71%) for genes that entered
through D3 alone and 2 of 16 (13%, 4–36%) for genes with a UniProt score of at most 2, and 13 of 22 (59%) for flagged
against 8 of 28 (29%) for unflagged genes <!-- src: results/revision/a1_N1_rates_by_route_and_flag.tsv --> (S4A Fig).
Of the 21 N1 genes, 13 have key evidence from 2021 or later, which curation could not yet be expected to reflect; for
the other 8 the evidence is older, and 6 of these 8 carry a definition-artefact flag
<!-- src: results/revision/a1_U_entry_flags.tsv -->. Much of what we call curation lag is therefore a gap created by the
pre-registered definition, which follows Wainberg et al.'s D2 only in part: function that is published, often for
complex membership, but invisible to a BP/MF-only, focused-literature definition. The remainder, about a quarter of the
random sample, is recent work not yet curated.

## C2: co-essentiality beats both nulls on a temporal hold-out, with low absolute accuracy

**Hold-out set.** H contained 820 genes that lacked experimental function at the July 2018 GO release, with 5,965
<!-- src: results/holdout_eval/core.md --> gene–target pairs. Removing 106 <!-- src: results/holdout_eval/core.md -->
pairs whose supporting papers cite DepMap or co-essentiality work left 809 <!-- src: results/holdout_eval/core.md -->
genes with a target (11 <!-- src: results/holdout_eval/core.md --> genes lost every target). The PMID + N(g) cluster graph put 63.5% <!-- src: results/holdout_eval/core.md --> of H in one
component, so under the fallback rule set before H was opened [deviation] the primary confidence intervals use the
PMID-only clusters (703 <!-- src: results/holdout_eval/comparisons_core.tsv --> clusters among primary genes).
Effective sample sizes were 719 and 722 <!-- src: results/holdout_eval/core.md --> (underpowered threshold 300).

**Primary test [pre-specified].** zavg_BEF placed a later-confirmed term at rank 1 for 24
<!-- src: verify/holdout_verification.md --> of 809 genes: precision@1 0.030 (95% CI 0.018–0.043)
<!-- src: results/holdout_eval/SUMMARY.md -->. The prior-only ranking scored 0.000 and the matched-gene null 0.005
(0.003–0.008) <!-- src: results/holdout_eval/SUMMARY.md --> (Fig 2A). Both paired differences exclude zero: +0.030
(+0.018 to +0.043) versus prior-only and +0.025 (+0.013 to +0.038) versus the matched null
<!-- src: results/holdout_eval/SUMMARY.md --> (Fig 2B). The intersection–union test therefore passes, as it does with
BCa intervals and with the PMID + N(g) clusters <!-- src: results/holdout_eval/SUMMARY.md -->. Prior-only always
proposes the most frequent candidate terms (median size 200 genes <!-- src: results/holdout_eval/SUMMARY.md -->), none
of which was new for an H gene; this arm is degenerate at rank 1, so the intersection–union test was in effect decided by
the matched-gene null, and "beats both nulls" should be read with that in mind. An independent agent re-implemented the evaluation from the design documents and
reproduced hit@1 for 809 of 809 <!-- src: verify/holdout_verification.md --> genes, for all three methods.

The result held in every pre-specified robustness check. Precision@1 on the ten split-half networks ranged from 0.025 to
0.038 <!-- src: results/holdout_eval/SUMMARY.md -->, and both differences excluded zero in 10 of 10
<!-- src: results/holdout_eval/SUMMARY.md --> (S2C Fig). Across the circularity sensitivities precision@1 was
0.030–0.032 <!-- src: results/holdout_eval/SUMMARY.md -->, and the test passed in all five. The R1 tie-break was not
specified in the design; implemented as ascending GO identifier, it affects 401 of 820 <!-- src: DEVIATIONS.md --> H
genes, and the reverse order gives 0.032 <!-- src: DEVIATIONS.md --> with the primary still passing [deviation].
Restricting candidates and targets to terms with at most 50 genes gave 0.029 (0.017–0.044) on 649
<!-- src: results/holdout_eval/SUMMARY.md --> genes. Other pre-specified metrics were weaker. The MRR difference from
prior-only was +0.010 (−0.004 to +0.025) <!-- src: results/holdout_eval/SUMMARY.md --> and did not exclude zero;
prior-only often places a true term just below rank 1. Predicted terms were broad: the median top-1 term had 132
annotated genes (IQR 84–176), and only 13% <!-- src: results/holdout_eval/SUMMARY.md --> had 50 or fewer. For GO
complexes (V1; 77 <!-- src: results/holdout_eval/SUMMARY.md --> H genes with a complex target), precision@1 was 0.182
(0.093–0.286) against 0.013 for prior-only and 0.005 for the null <!-- src: results/holdout_eval/SUMMARY.md -->;
removing ETC complex I and the mitoribosome from targets and lists left this unchanged
<!-- src: results/holdout_eval/SUMMARY.md -->.

**GLS (key secondary) [pre-specified].** GLS reached 0.023 (0.013–0.035) <!-- src: results/holdout_eval/SUMMARY.md -->.
The two-sided difference, zavg_BEF minus GLS, was +0.006 (−0.005 to +0.017) <!-- src: results/holdout_eval/SUMMARY.md -->:
no detectable difference (Fig 2A and 2B), and the interval rules out an advantage for zavg_BEF of more than 1.7 points (upper bound +0.017
<!-- src: results/holdout_eval/SUMMARY.md -->).
Together with the Pearson result below, the hold-out accuracy is a property of co-essentiality, of which zavg_BEF is one
implementation, rather than of this tool. The tool's hyper-parameters were tuned on hu.MAP 3.0 co-complex pairs
[Coessentiality_tool], a resource built after t0 that contains complexes with H genes, so post-t0 knowledge could in
principle enter zavg_BEF; parity with untuned Pearson correlation bounds the size of any such benefit. By the size of the gene's smallest target, the difference was +0.011 (−0.002
to +0.024) for targets of at most 50 genes and −0.013 (−0.032 to 0.000) for larger ones
<!-- src: results/holdout_eval/SUMMARY.md -->. Secondary metrics without multiplicity control favoured zavg_BEF modestly
(MRR +0.016, +0.005 to +0.027) <!-- src: results/holdout_eval/SUMMARY.md -->.

**Secondary batch [pre-specified, reported in full].** Pearson correlation matched zavg_BEF (0.027; difference +0.002,
−0.009 to +0.014) <!-- src: results/holdout_eval/SUMMARY.md -->. Two non-co-essentiality baselines did better (Fig 2A
and 2B). The homology baseline, which uses the gene's own t0 electronic, sequence-similarity and phylogenetic
annotations, made a prediction for 57% <!-- src: results/holdout_eval/SUMMARY.md --> of H genes, yet reached
precision@1 0.218 (0.184–0.253), exceeding zavg_BEF by 0.188 (0.153–0.225) <!-- src: results/holdout_eval/SUMMARY.md -->.
Module transfer from hu.MAP 3.0 interaction partners [Fischer2025] reached 0.049 (0.034–0.066), 0.020 (0.004–0.037)
<!-- src: results/holdout_eval/SUMMARY.md --> above zavg_BEF; hu.MAP 3.0 was built after t0, which favours it, as the
design anticipated. The primary test also passed with t0 = 2019-07, with post-cut-off-dated targets, at K = 10 and 50,
and without same-arm and paralogue exclusions (precision@1 0.028–0.034) <!-- src: results/holdout_eval/SUMMARY.md -->.
H genes have stronger co-essentiality signal than U genes (standardised mean difference in top-K mean zavg_BEF +0.253,
in R(g) +0.228) <!-- src: results/holdout_eval/SUMMARY.md -->. Reweighted to the covariate distribution of U,
precision@1 fell to 0.012 (0.007–0.019), and both primary differences still excluded zero (+0.012 and +0.008, lower
bound 0.002) <!-- src: results/holdout_eval/SUMMARY.md -->.

**Accuracy is concentrated in the strongest signals [pre-specified core].** By quintile of top-K mean zavg_BEF,
precision@1 was 0 in the two lowest quintiles and 0.117 (0.067–0.174) in the highest (top-K mean 5.4–15.5)
<!-- src: results/holdout_eval/fig_signal_quintiles.tsv --> (Fig 2C). GLS showed
the same gradient, reaching 0.074 <!-- src: results/holdout_eval/fig_signal_quintiles.tsv --> in the top quintile.
Prior-only scored 0 in every quintile. Precision@1 was not broken
down by module family, because 552 of the 775 H genes with a prediction fall in the "other" family
<!-- src: results/revision/a4_family_hits_H.tsv -->.

**Calibration [pre-specified].** The calibration model was fitted on the 775
<!-- src: results/holdout_eval/calibration.md --> H genes with a top term and evaluated by 10-fold cluster
cross-fitting. Out of fold, the calibration slope was 0.82 (Wald 95% CI 0.51–1.13) and the intercept −0.01 (−0.44 to
0.43) <!-- src: results/holdout_eval/calibration.md --> (Fig 2D). Neither interval crosses the pre-specified
poor-calibration bound, so the pre-specified caveat branch was not triggered. That is a statement about detectability,
not adequacy. The model rests on 24 events among 775 genes, with seven parameters besides the intercept (3.4 events per
parameter); the cluster-bootstrap slope interval is 0.59–1.09, the c-statistic is 0.855 (cluster-bootstrap 0.805–0.903),
and the mean prediction exceeds the observed rate by only 0.0001 <!-- src: results/revision/a4_calibration_models.tsv -->
[post-review exploratory]. With a 3.1% <!-- src: results/holdout_eval/calibration.md --> base rate, the Brier score
(0.0294) was barely below that of a constant-rate prediction (0.0300) <!-- src: results/holdout_eval/calibration.md -->,
a Brier skill of 0.021 <!-- src: results/revision/a4_calibration_models.tsv -->, and the Brier interval (0.0198–0.0412)
<!-- src: results/holdout_eval/calibration.md --> contains the constant-rate value. We therefore describe p_cal as not
detectably miscalibrated, with wide uncertainty. In the five lowest deciles (p_cal ≤ 0.013) no prediction was
confirmed; in the top decile, a mean prediction of 0.170 compared with an observed rate of 0.115 (0.062–0.205)
<!-- src: results/holdout_eval/calibration.md -->. Two of the four sign-constrained coefficients, for R(g) and term
size, were fitted at their bound of 0 <!-- src: results/holdout_eval/calibration.md -->. The signalling/lineage family
had no hits in H and received a coefficient of −11.86 <!-- src: results/holdout_eval/calibration.md -->, which sets its
p_cal to about zero. This is quasi-separation: 0 of 111 signalling genes were hits, and the one-sided 95% upper bound
on their hit rate is 0.027 <!-- src: results/revision/a4_family_hits_H.tsv; results/revision/numbers_a4.json -->. Because every signalling gene ranks
below every hit, separation also inflates the c-statistic; without the signalling genes the out-of-fold slope was
unchanged (0.82, 0.51–1.13) and c fell to 0.830 (664 genes) <!-- src: results/revision/numbers_a4.json -->
[post-review exploratory]. As a further sensitivity, models with top-K mean zavg_BEF alone (24 events per parameter),
or with annotation coverage added, cross-fitted in the same way, gave slopes of 0.93 (0.60–1.25) and 0.89 (0.57–1.21),
c-statistics of 0.835 and 0.832, and Brier skills of 0.037 and 0.036
<!-- src: results/revision/a4_calibration_models.tsv --> (S4D Fig): the simpler models calibrate at least as well as the
frozen one, which is consistent with over-parameterisation of the frozen model rather than with signal it misses. Five families had only 10–19 H genes each <!-- src: results/holdout_eval/calibration.md --> and so
receive no p_cal under the support rule. A model fitted on LOO genes instead (secondary) predicted a mean of 0.089
against an observed 0.031 on H, with intercept −1.39 (−1.84 to −0.95) <!-- src: results/holdout_eval/SUMMARY.md -->.
Current annotations of characterised genes therefore overstate, roughly threefold, the chance that a prediction for a
newly studied gene will be confirmed.

**Named controls [pre-specified case series].** Of the 14 named controls, 9
<!-- src: results/holdout_eval/controls_case_series.tsv --> are in H (Fig 2E). TMEM242's true term ranked first of 77
reportable terms and PEDS1's seventh of 79; AIRIM's ranked 89th of 125
<!-- src: results/holdout_eval/controls_case_series.tsv -->. For the other controls no clean true term was ranked,
mostly because their new annotations cite DepMap or co-essentiality papers and were excluded. This applied to the single
new term of SPRING1, TEDC1, TEDC2, POU2AF2 and POU2AF3, to 4 of 5 for CCDC32, 20 of 23 for SLC25A51 and 17 of 18 for
FIRRM <!-- src: results/holdout_eval/controls_case_series.tsv -->. [Post-review exploratory] INTS15 and TMEM41B missed
for a different reason: the network was right but the t0 vocabulary could not express it. All of INTS15's top ten
partners are Integrator subunits or INIP, and its top terms were snRNA metabolism and snRNA transcription; but of its 11
new GO terms, 8 were not reportable, because fewer than two of its neighbours carried them at t0, and 3 fell outside the
term-size window <!-- src: results/revision/a8_control_target_reasons.tsv -->. TMEM41B's partners (VMP1, SYVN1, DERL2,
SEL1L and others) gave ER-stress and ERAD terms, while 16 of its 17 new terms, including autophagosome assembly, were
supported at t0 by at most one neighbour <!-- src: results/revision/a8_control_target_reasons.tsv -->. For these
controls, t0 annotation of the neighbours, not the network, limited accuracy. (The descriptive module label for SPRING1 was the
SREBP–SCAP complex <!-- src: results/holdout_eval/controls_case_series.tsv -->.) Much of the recent literature on these
controls depends on co-essentiality itself, so the case series cannot serve as independent validation.

**Complementarity [exploratory; post hoc, logged in LOOKS.md].** After seeing the primary results, we asked whether
co-essentiality adds to the stronger baselines. Both zavg_BEF and homology were right for 9
<!-- src: results/holdout_eval/exploratory_complementarity.md --> genes; zavg_BEF alone was right for 15 genes and
homology alone for 167 <!-- src: results/holdout_eval/exploratory_complementarity.md -->, so the union, which credits a
gene if either method is right, reached 0.236 (0.206–0.266), 0.019 <!-- src: results/holdout_eval/exploratory_complementarity.md -->
above homology. That union is an oracle upper bound, not a usable rule. [Post-review exploratory] The deployable rule
"homology where it makes a prediction, otherwise zavg_BEF" reached 0.224 (0.190–0.259), a gain over homology of +0.006
(+0.001 to +0.012); the reverse priority reached 0.036 <!-- src: results/revision/a7_combination_rules.tsv -->. In the
348 genes without a homology prediction, zavg_BEF reached 0.014 (0.003–0.029; 5 hits)
<!-- src: results/holdout_eval/exploratory_complementarity.md -->, and in the 81 genes without a hu.MAP partner, 0
<!-- src: results/holdout_eval/exploratory_complementarity.md -->. Within the top five terms, zavg_BEF found a true term
for 0.067 of genes and prior-only for 0.069 <!-- src: results/holdout_eval/exploratory_complementarity.md -->.
Co-essentiality thus adds a few distinct correct calls but does not replace homology- or interaction-based annotation.

## C3: calibrated predictions for U are uniformly low, and the low-yield branch applies

**Coverage of the catalogue.** All 4,271 <!-- src: results/ledger/pcal_summary.json --> scorable U genes were scored
with the hold-out code path, and 4,137 <!-- src: results/ledger/pcal_summary.json --> received a reportable top term.
Of these, 2,583 <!-- src: results/ledger/pcal_summary.json --> were inside calibration support, 133
<!-- src: results/ledger/pcal_summary.json --> received only a boundary upper bound and 1,421
<!-- src: results/ledger/pcal_summary.json --> were out of support (Fig 3D). Low neighbourhood annotation coverage was the
commonest reason (536 <!-- src: results/ledger/pcal_summary.json --> genes). The family rule removed every prediction in
the five under-represented families: 119 centrosome/cilia/mitosis, 106 ribosome/translation, 97 nuclear RNA machinery,
70 DNA replication/repair and 49 mitochondrial <!-- src: results/ledger/pcal_summary.json --> genes. Another 96
<!-- src: results/ledger/pcal_summary.json --> genes were excluded because their signal exceeded H's 95th percentile.
Calibration therefore leaves out the machinery modules and the strongest signals, where co-essentiality is best
established and, on H, most accurate (Fig 2C). Among the 646 assessable genes, 269
<!-- src: results/ledger/M6_SUMMARY.md --> are in support. A secondary, uncalibrated list (S20) of the strongest
predictions without p_cal was defined before any literature step [deviation] and is analysed under C4.

**Calibrated probabilities [pre-specified].** No in-support U gene reached the Tier B threshold of 0.3, let alone the
Tier A threshold of 0.5. The largest in-support p_cal was 0.141 <!-- src: results/ledger/pcal_summary.json -->; the
1,421 <!-- src: results/ledger/pcal_summary.json --> genes without p_cal, which include the strongest signals and S20, have no calibrated value to compare. Among
expressed, assessable genes in support the median was 0.014 and the 90th percentile 0.047
<!-- src: results/ledger/pcal_summary.json --> (Fig 3A). This ceiling follows from the model: with an H hit rate of 3%
<!-- src: results/holdout_eval/calibration.md --> and covariates bounded by H's 95th percentiles (top-K mean zavg_BEF ≤
10.99, coverage percentile ≤ 0.894 <!-- src: results/holdout_eval/calibration.md -->), the fitted model cannot reach
0.3 inside support <!-- src: results/ledger/M6_SUMMARY.md -->.

**Σp_cal [pre-specified headline].** Summed over the 2,583 in-support genes, the expected number of top terms that later
experimental annotation will confirm within about eight years <!-- src: config/frozen.yaml --> is **30.5 (95% CI
13.8–49.7)** <!-- src: results/ledger/pcal_summary.json -->, a mean of about 1.2% per gene
<!-- src: results/ledger/pcal_summary.json --> (Fig 3B). Over the 269 expressed, assessable genes in support it is 5.5
(2.8–8.6) <!-- src: results/ledger/pcal_summary.json -->. The 133 boundary genes add an upper bound of 1.0 (0.5–1.9)
<!-- src: results/ledger/pcal_summary.json -->, and Tier A contributes 0. The interval reflects parameter uncertainty
in the expectation; it is not a prediction interval for the realised count, which has a further Poisson-binomial
standard deviation of about 5.5 <!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->.

**p_cal is conditional on later annotation [post-review exploratory].** The model was fitted on H, and H contains only
genes that gained at least one experimental target. p_cal therefore estimates the probability that the top term is
confirmed *given that the gene receives new experimental BP/MF annotation*, not the unconditional probability of
confirmation; the design text and our first draft read it unconditionally. Of the 4,822 t0-eligible genes with a
reportable top term, 775 (16.1%, 15.1–17.1%) gained such annotation over the 7.9-year horizon
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->. Scaling by this rate, the unconditional expectation over the
2,583 in-support genes is about 4.9 (2.2–8.1), and about 0.40 (0.21–0.64) for the primary top 40
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->. Gaining annotation is not independent of signal (gain rate
0.13–0.14 in the four lower quintiles of top-K mean zavg_BEF and 0.25 in the highest
<!-- src: results/revision/a3_gain_rate_by_signal_quintile.tsv; results/revision/numbers_a3.json -->); with quintile-specific rates the expectation is 5.1
(2.4–8.3) <!-- src: results/revision/a3_gain_rate_by_signal_quintile.tsv; results/revision/numbers_a3.json -->. The annual hazard of gaining annotation
was similar for the 2018 cohort, a 2022 cohort and 2018 genes still uncharacterised in 2022 (0.0225, 0.0222 and 0.0199)
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->, so the rate has been roughly stationary, but large
phylogenetic and AI-assisted annotation efforts [Feuermann2025] could change it, and U genes, which stayed
uncharacterised until 2026, may be annotated more slowly than the 2018 cohort.

**Other sensitivities of Σp_cal [post-review exploratory].** The 403 in-support signalling genes contribute 0.00004
because of the separated family coefficient; at the upper bound of the signalling hit rate they would contribute up to
10.7 <!-- src: results/revision/numbers_a4.json -->. Expressed in-support genes contribute 20.0 of the 30.5
<!-- src: results/revision/numbers_a4.json -->; the remainder comes from non-expressed genes, whose profiles we
argue carry little functional signal. Under the simpler calibration models, Σp over the same 2,583 genes was 41.6 (zavg_BEF
only) and 38.6 (with coverage) <!-- src: results/revision/a4_simple_models_on_U.tsv -->; their top 40s shared only 7 and
14 genes with the primary top 40, because without the family term mitoribosomal and ribosome-biogenesis genes enter
<!-- src: results/revision/a4_simple_model_top40.tsv -->.

**Decision branch [pre-specified].** Tier A has 0 genes and Tier B has 0 <!-- src: results/ledger/M6_SUMMARY.md -->.
With fewer than 10 Tier A genes, the pre-specified low-yield branch applies: the paper leads with C1 and C2, the top 40
is filled by p_cal, and thresholds are not relaxed. Because C2 passed and 646 genes are assessable (≥ 100), the
catalogue remains calibrated rather than descriptive.

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
hub-driven. In total 293 <!-- src: results/ledger/M6_SUMMARY.md --> carry a built-in exclusion from Tier A (a flag on
at least half of the supporting partners, or hub-driven). The locus flag was applied without strand information, as a
superset of the frozen rule [deviation].

**Orthogonal support separates real from control predictions only weakly [pre-specified].** The support test was run on
247 <!-- src: results/ledger/false_support.tsv --> anchor genes (all candidates evaluated during the top-40 fill),
together with one matched-gene prediction and one decoy-term prediction per anchor. The Tier-A support rule was met by
0.320 of real predictions, 0.279 of matched-gene predictions and 0.223 of decoy predictions
<!-- src: results/ledger/false_support.tsv --> (Fig 3C). In a paired comparison over the same anchors [exploratory; a post hoc test, unadjusted],
real predictions passed the rule more often than decoys (+0.097; 54 vs 30 discordant pairs; exact McNemar p = 0.012)
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> but not detectably more often than matched-gene
predictions (+0.040; 47 vs 37; p = 0.33) <!-- src: manuscript/figures/source_data/derived_numbers.tsv -->.
Physical-interaction support showed the clearest contrast (0.12 real, 0.03 matched, 0.01 decoy), whereas co-abundance
and localisation support were common in all three sets <!-- src: results/ledger/false_support.tsv -->. Contradictions
were rare (0.004 of real predictions) and arose only through the four-source localisation reading [deviation]; the
HPA-only rule never fired <!-- src: results/ledger/false_support.tsv -->. At the gene level, orthogonal "support" under
this rule is weak evidence. It is reported for every candidate but upgrades no prediction; the physical class alone is
the most informative orthogonal readout, and Table 3 reports it separately.

**Top 40 [pre-specified fill; deviation in its reading].** The fill pool held 269
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> expressed, assessable, in-support genes, of which 24
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> were removed by a built-in artefact exclusion (23) or a
contradiction (1). With no tiered gene, the frozen order Tier A → Tier B → p_cal reduces to p_cal. The top-40-only
checks are tier caps ("Tier B at best"), so they are shown as labels, not demotions (PI ruling before any literature
step) [deviation]. The primary top 40 is therefore the 40 highest p_cal values after exclusions (Fig 4). The pool
contains no mitochondrial-family genes <!-- src: manuscript/figures/source_data/derived_numbers.tsv -->, so the
mitochondrial cap did not bind. p_cal in the top 40 ranges from 0.036 to 0.141
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->, and the sum is 2.50
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> (point estimate): about two to three of these 40 top
terms are expected to be confirmed if every gene is later annotated, and about 0.4 unconditionally
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json --> [post-review exploratory]. Thirty-six top terms fall in the "other" family and 4 in ER/Golgi/secretory
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->. The commonest terms are transcription elongation,
epigenetic regulation of gene expression and response to ER stress (3 genes each)
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->.

The top-40-only checks were strict. Thirty-three of the 40
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes fail at least one. The lineage leave-out changed
the top term for 10 <!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes. DEMETER2 RNAi
[McFarland2018] did not replicate the partner correlations for 24 of the 30
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes in which it could be measured, and 11
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes carry a TP53 flag. Across the pool, DEMETER2 failed
to replicate for 182 of 204 <!-- src: results/ledger/M6_SUMMARY.md --> measured genes, a rate that may reflect the RNAi
data as much as the predictions; we report it without adjustment. The check was never validated on positive controls,
and the S20 machinery genes, on which it could have been, have no p_cal and were not scored, so a DEMETER2 flag should
not be read as evidence against a prediction. Twenty-seven of the top 40 have support from at least
one orthogonal class, and 25 have diagnostic-class support
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->; given the false-support rates above, these counts
should not be read as validation. The "clean-first" list built by the implementing agent shares 20
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes with the primary top 40 and has Σp_cal 2.04
(1.05–3.24) <!-- src: results/ledger/M6_SUMMARY.md -->; it is reported as a sensitivity analysis (S3 Table).
