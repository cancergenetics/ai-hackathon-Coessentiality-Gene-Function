
# Results

The study design is summarised in Fig 1A; the notation is defined at the start of the Methods. Results are labelled
[pre-specified] (frozen design, DESIGN.md v2.3), [deviation] (a change logged in DEVIATIONS.md; the Methods list the
rows that were logged only after the affected result existed), [exploratory] (post hoc, before review; H looks logged in
LOOKS.md), [post-review exploratory] (analyses requested by the referees and computed after peer review into
results/revision/; no frozen rule changed) or [descriptive] (computed for presentation only). [post-review] alone marks a
table column or report statement added after peer review that is not itself an analysis. Detailed sensitivity and
secondary analyses, and the list of literature-supported predictions, are in S1 Text.

## The tool reproduces its published performance on DepMap 26Q3

With the tool's own scripts, the internal-test average precision on our data was 0.3451 for zavg_BEF and 0.2423 for GLS,
within the pre-specified ±0.005 of the published values
<!-- src: results/verification/tool_reproduction.md -->, and all 14 <!-- src: results/verification/sanity_checks.md --> sanity checks passed (S1 Text). The term ranker was then
chosen once, on 2,519 <!-- src: results/calibration/loo_ranker_choice.md --> characterised leave-one-out (LOO) genes, by
the frozen mean-reciprocal-rank rule [pre-specified]: raw neighbour support (R1; MRR 0.169
<!-- src: results/calibration/loo_ranker_choice.md -->) (S1A Fig). The choice and the calibration specification were
logged before the hold-out was opened (LOOKS.md, commit fa21808).

## C1: at most one in eight pre-registered genes is assessable

**Census [pre-specified].** Of the 4,924 <!-- src: results/assessability/assessability_U.tsv --> pre-registered genes,
4,271 (86.7%) <!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> are scorable (Fig 1B). Of these,
2,722 <!-- src: results/assessability/summary.md --> are expressed in DepMap lines, and 842 (19.7% of scorable)
<!-- src: results/assessability/summary.md --> have a split-half reproducibility p below 0.05 regardless of expression.
The pre-specified C1 count, genes that are scorable, expressed and assessable, is **646 (13.1% of U)**
<!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv -->. This count applies the design's definition of
"expressed", which includes lineage-restricted genes; with the expression column of the frozen gene table, which
predates that wording, the count is 635 (12.9%) <!-- src: results/assessability/summary.md --> [deviation; both
reported]. In the headline stratum (expressed, not chemosensory or epidermal, not in a tandem cluster), 598 of 2,525
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> genes are assessable. Assessability tracked
the strength of the dependency profile: 427 of 1,105
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> genes with any dependency (≥ 1% of lines
below −0.5 <!-- src: preregistration/CRITERIA.md -->) were assessable, against 219 of 3,170
<!-- src: manuscript/figures/source_data/Fig1c_assessable_by_stratum.tsv --> without (Fig 1C; other strata and a
rank-biased-overlap sensitivity in S1 Text).

**The reproducibility null is anti-conservative, so 646 is an upper bound.** Clean-negative genes, which are not
expressed in at least 95% of lines, reached split-half p < 0.05 in 153 of 1,167 cases (13.1%)
<!-- src: results/assessability/summary.md -->, well above the nominal 5%: 27.2%
<!-- src: results/assessability/summary.md --> among clean negatives with some dependency and 9.7%
<!-- src: results/assessability/summary.md --> among those without (S2B Fig). Requiring expression removes the genes in
which this was measured without showing that the problem disappears in expressed genes. [Post-review exploratory] If
the clean-negative false-call rates apply to expressed genes of the same dependency class, about 392 (329–462) of the
635 calls on the frozen expression column are expected under the null, leaving an excess of 243 (173–306) calls, 4.9%
(3.5–6.2%) of U, over the null expectation <!-- src: results/revision/a6_assessability_null_adjusted.tsv --> (S4C Fig).
Because some expected false calls fall on genes that also carry real signal, the excess understates the number of such
genes: at full power it implies at least about 324 (248–389) genes, 6.6% of U, with real reproducible signal, and more
at lower power <!-- src: results/revision/a10_assessability_excess_and_implied.tsv --> (S1 Text). This is a lower bound
under an untested assumption. The pre-specified count of 646 <!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> stands as the C1 result, read as an upper bound on the
genes that pass the reproducibility test for reasons other than chance.

**Published but uncurated functions [pre-specified].** An auditor with no access to co-essentiality output classed a
pre-specified random sample of 50 U genes (Fig 1D). For 21 genes (42%, Wilson 95% CI 29–56%)
<!-- src: results/audit/curation_lag_audit.md --> the auditor found direct functional evidence in a focused study (N1);
13 <!-- src: results/audit/curation_lag_audit.md --> had partial evidence (N2) and 16
<!-- src: results/audit/curation_lag_audit.md --> had none (N3). Moving the three borderline calls gave N1 rates between
38% and 46% <!-- src: results/audit/curation_lag_audit.md -->. A closed-book language-model recall probe "recognised" 18
of the 21 N1 genes <!-- src: manuscript/figures/source_data/Fig1d_curation_lag_audit.tsv --> (S1 Text). Roughly four in
ten "uncharacterised" genes thus already have published functions, so novelty must be checked against the literature
(C4).

**Curation lag and the definition of "uncharacterised" [post-review exploratory].** U required no experimental GO
biological-process or molecular-function annotation (D1) plus either a low UniProt annotation score (D2) or low focused
literature (D3). Of the 4,924 U genes, 3,819 entered through D3 alone <!-- src: results/revision/a1_flag_counts.tsv -->.
D3 counts only papers about at most ten genes, so genes studied mainly in multi-gene papers look unstudied. We therefore
flagged genes with a UniProt annotation score of 5 (1,261), curated Complex Portal subunits (288) and genes with an
experimental GO cellular-component annotation (1,218) <!-- src: results/revision/a1_flag_counts.tsv -->, which D1 ignores; this last flag also counts localisation-only
annotations. In all, 1,933 U genes carry at least one of these definition-artefact flags
<!-- src: results/revision/a1_flag_counts.tsv -->. In the random sample, 13 of 21 N1 genes rest on evidence from 2021 or
later (curation lag in the usual sense) <!-- src: results/revision/a1_U_entry_flags.tsv -->. The other 8 rest on older evidence; 6 of these are flagged, mostly (5) by
UniProt score 5 <!-- src: results/revision/a1_U_entry_flags.tsv -->. None is a Complex Portal subunit. Literature-route
genes were N1 more often (19/34 vs 2/16; 56% vs 13%, 3–36%), as were flagged genes (13/22 vs 8/28)
<!-- src: results/revision/a1_N1_rates_by_route_and_flag.tsv --> (S4A Fig); with the cellular-component part of the
flag restricted to complex terms (165 U genes <!-- src: results/revision/a1_flag_counts.tsv -->), the contrast is 10/18
vs 11/32 (p = 0.23) <!-- src: results/revision/a1_N1_rates_by_route_and_flag.tsv -->. Among selected candidates,
definition artefacts dominate (30/40 and 20/20 flagged; 13 and 17 Complex Portal subunits
<!-- src: results/revision/a1_flag_counts.tsv -->; C4). In the random sample, then, most of the gap is recent work not
yet curated and the rest is older work that the definition could not see; complex membership accounts for it only among
the top candidates.

## C2: co-essentiality beats a matched-gene null on a temporal hold-out, with low absolute accuracy

**Hold-out set.** H contained 820 genes that lacked experimental function at the July 2018 GO release, with 5,965
<!-- src: results/holdout_eval/core.md --> gene–target pairs. Removing 106 <!-- src: results/holdout_eval/core.md -->
pairs whose supporting papers cite DepMap or co-essentiality work left 809 <!-- src: results/holdout_eval/core.md -->
genes with a target. The PMID + N(g) cluster graph put 63.5% <!-- src: results/holdout_eval/core.md --> of H in one
component, so under the fallback rule set before H was opened [deviation] the primary confidence intervals use the
PMID-only clusters (703 <!-- src: results/holdout_eval/comparisons_core.tsv --> clusters among primary genes).

**Primary test [pre-specified].** zavg_BEF placed a later-confirmed term at rank 1 for 24
<!-- src: verify/holdout_verification.md --> of 809 genes: precision@1 0.030 (95% CI 0.018–0.043)
<!-- src: results/holdout_eval/SUMMARY.md -->. The prior-only ranking scored 0.000 and the matched-gene null 0.005
(0.003–0.008) <!-- src: results/holdout_eval/SUMMARY.md --> (Fig 2A). Both paired differences exclude zero: +0.030
(+0.018 to +0.043) versus prior-only and +0.025 (+0.013 to +0.038) versus the matched null
<!-- src: results/holdout_eval/SUMMARY.md --> (Fig 2B). The intersection–union test therefore passes, as it does with
BCa intervals and with the PMID + N(g) clusters <!-- src: results/holdout_eval/SUMMARY.md -->. Prior-only always
proposes the most frequent candidate terms (median size 200 genes <!-- src: results/holdout_eval/SUMMARY.md -->), none
of which was new for an H gene; this arm is degenerate at rank 1, so the test was in effect decided by the matched-gene
null. An independent agent re-implemented the evaluation from the design documents and reproduced hit@1 for 809 of 809
<!-- src: verify/holdout_verification.md --> genes. The result held in every pre-specified robustness check, including
the ten split-half networks (precision@1 0.025–0.038 <!-- src: results/holdout_eval/SUMMARY.md -->), the circularity
sensitivities, both tie-break orders and t0 = 2019-07 (S2C Fig; S1 Text). For GO complexes (V1; 77
<!-- src: results/holdout_eval/SUMMARY.md --> H genes with a complex target), precision@1 was 0.182 (0.093–0.286)
against 0.013 for prior-only and 0.005 for the null <!-- src: results/holdout_eval/SUMMARY.md -->.

**Comparators [pre-specified].** GLS, the key secondary comparator, reached 0.023 (0.013–0.035)
<!-- src: results/holdout_eval/SUMMARY.md -->; the two-sided difference, zavg_BEF minus GLS, was +0.006 (−0.005 to
+0.017) <!-- src: results/holdout_eval/SUMMARY.md -->, which rules out an advantage for zavg_BEF of more than 1.7 points
<!-- src: results/holdout_eval/SUMMARY.md -->.
Pearson correlation matched zavg_BEF (0.027; difference +0.002, −0.009 to +0.014)
<!-- src: results/holdout_eval/SUMMARY.md -->. The hold-out accuracy is therefore a property of co-essentiality rather
than of this tool. The tool's hyper-parameters were tuned on hu.MAP 3.0 co-complex pairs [Coessentiality_tool], built
after t0, so post-t0 knowledge could in principle enter zavg_BEF; parity with untuned Pearson correlation bounds any such
benefit. Two non-co-essentiality baselines did better (Fig 2A and 2B). The homology baseline, which uses the gene's own
t0 electronic, sequence-similarity and phylogenetic annotations, made a prediction for 57%
<!-- src: results/holdout_eval/SUMMARY.md --> of H genes, yet reached precision@1 0.218 (0.184–0.253), exceeding
zavg_BEF by 0.188 (0.153–0.225) <!-- src: results/holdout_eval/SUMMARY.md -->. Module transfer from hu.MAP 3.0
interaction partners [Fischer2025] reached 0.049 (0.034–0.066) <!-- src: results/holdout_eval/SUMMARY.md -->, favoured
because hu.MAP 3.0 was built after t0. H genes have stronger co-essentiality signal than U genes; reweighted to the
covariate distribution of U, precision@1 fell to 0.012 (0.007–0.019), and both primary differences still excluded zero
<!-- src: results/holdout_eval/SUMMARY.md -->.

**Accuracy is concentrated in the strongest signals [pre-specified core].** By quintile of top-K mean zavg_BEF,
precision@1 was 0 in the two lowest quintiles and 0.117 (0.067–0.174) in the highest (top-K mean 5.4–15.5)
<!-- src: results/holdout_eval/fig_signal_quintiles.tsv --> (Fig 2C). GLS showed the same gradient, reaching 0.074
<!-- src: results/holdout_eval/fig_signal_quintiles.tsv --> in the top quintile.

**Calibration [pre-specified].** The calibration model was fitted on the 775
<!-- src: results/holdout_eval/calibration.md --> H genes with a top term and evaluated by 10-fold cluster
cross-fitting. Out of fold, the calibration slope was 0.82 (Wald 95% CI 0.51–1.13) and the intercept −0.01 (−0.44 to
0.43) <!-- src: results/holdout_eval/calibration.md --> (Fig 2D). Neither interval crosses the pre-specified
poor-calibration bound, so the caveat branch was not triggered. That is a statement about detectability, not adequacy
[post-review exploratory]. The model rests on 24 events among 775 genes, with seven parameters besides the intercept
(3.4 events per parameter) <!-- src: results/revision/a4_calibration_models.tsv -->. With a 3.1%
<!-- src: results/holdout_eval/calibration.md --> base rate, its Brier score (0.0294) was barely below that of a
constant-rate prediction (0.0300) <!-- src: results/holdout_eval/calibration.md -->, a Brier skill of 0.021
<!-- src: results/revision/a4_calibration_models.tsv -->. The signalling family, with 0 hits among 111 genes, is
quasi-separated, which sets its p_cal to about zero <!-- src: results/revision/a4_family_hits_H.tsv -->. Models with
one or two covariates calibrate comparably (slopes 0.93 and 0.89, with intervals overlapping the frozen model's; c 0.835
vs 0.855) <!-- src: results/revision/a4_calibration_models.tsv --> (S4D Fig; S1 Text). We therefore describe p_cal as
not detectably miscalibrated, with wide uncertainty. A model fitted on LOO genes instead (secondary) predicted a mean of
0.089 against an observed 0.031 on H <!-- src: results/holdout_eval/SUMMARY.md -->: current annotations of
characterised genes overstate, roughly threefold, the chance that a prediction for a newly studied gene will be
confirmed.

**Named controls [pre-specified case series].** Of the 14 named controls, 9
<!-- src: results/holdout_eval/controls_case_series.tsv --> are in H (Fig 2E). TMEM242's true term ranked first of 77
reportable terms and PEDS1's seventh of 79 <!-- src: results/holdout_eval/controls_case_series.tsv -->. For most other
controls no clean true term was ranked, because their new annotations cite DepMap or co-essentiality papers and were
excluded (for example 20 of 23 for SLC25A51 <!-- src: results/holdout_eval/controls_case_series.tsv -->). [Post-review
exploratory] INTS15 and TMEM41B missed for a different reason: their partners were right (Integrator subunits; VMP1 and
ERAD factors), but the terms curators later added were carried by fewer than two of their neighbours at t0
<!-- src: results/revision/a8_control_target_reasons.tsv --> (S1 Text). Because much recent literature on these
controls depends on co-essentiality itself, the case series cannot serve as independent validation.

**Complementarity [exploratory; post hoc, logged in LOOKS.md].** zavg_BEF alone was right for 15 genes, homology alone
for 167 and both for 9 <!-- src: results/holdout_eval/exploratory_complementarity.md -->. The oracle union, which credits
a gene if either method is right, reached 0.236 (cluster bootstrap 0.202–0.272)
<!-- src: results/revision/a7_combination_rules.tsv -->, an upper bound rather than a usable rule. [Post-review
exploratory] The deployable rule "homology where it makes a prediction, otherwise zavg_BEF" reached 0.224
(0.190–0.259), a gain over homology of +0.006 (+0.001 to +0.012) <!-- src: results/revision/a7_combination_rules.tsv -->;
in the 348 genes without a homology prediction, zavg_BEF reached 0.014 (5 hits)
<!-- src: results/holdout_eval/exploratory_complementarity.md -->. Co-essentiality thus adds a few distinct correct calls
but does not replace homology- or interaction-based annotation.

## C3: calibrated predictions for U are uniformly low, and the low-yield branch applies

**Coverage of the catalogue.** All 4,271 <!-- src: results/ledger/pcal_summary.json --> scorable U genes were scored
with the hold-out code path, and 4,137 <!-- src: results/ledger/pcal_summary.json --> received a reportable top term.
Of these, 2,583 <!-- src: results/ledger/pcal_summary.json --> were inside calibration support, 133
<!-- src: results/ledger/pcal_summary.json --> received only a boundary upper bound and 1,421
<!-- src: results/ledger/pcal_summary.json --> were out of support (Fig 3D). The support rule removed every prediction
in five under-represented machinery families and 96 <!-- src: results/ledger/pcal_summary.json --> genes whose signal
exceeded H's 95th percentile (S1 Text), so calibration leaves out the domain where co-essentiality is best established
and, on H, most accurate (Fig 2C). Among the 646 assessable genes, 269 <!-- src: results/ledger/M6_SUMMARY.md --> are
in support. A secondary, uncalibrated list (S20) of the strongest predictions without p_cal was defined before any
literature step [deviation] and is analysed under C4.

**Calibrated probabilities and decision branch [pre-specified].** No in-support U gene reached the Tier B threshold of
0.3, let alone the Tier A threshold of 0.5. The largest in-support p_cal was 0.141
<!-- src: results/ledger/pcal_summary.json -->; among expressed, assessable genes in support the median was 0.014 and the
90th percentile 0.047 <!-- src: results/ledger/pcal_summary.json --> (Fig 3A). This ceiling follows from the model: with
an H hit rate of 3% <!-- src: results/holdout_eval/calibration.md --> and covariates bounded by H's 95th percentiles,
the fitted model cannot reach 0.3 inside support <!-- src: results/ledger/M6_SUMMARY.md -->. With no Tier A or Tier B
gene <!-- src: results/ledger/M6_SUMMARY.md -->, the pre-specified low-yield branch applies: the paper leads with C1 and
C2, the top 40 is filled by p_cal, and thresholds are not relaxed. Because C2 passed and at least 100 genes are
assessable, the catalogue remains calibrated rather than descriptive.

**Σp_cal [pre-specified headline].** Summed over the 2,583 in-support genes, the expected number of top terms that would
be confirmed if every gene gained new experimental BP/MF annotation within about eight years
<!-- src: config/frozen.yaml --> (conditional; see below) is **30.5 (95% CI 13.8–49.7)**
<!-- src: results/ledger/pcal_summary.json -->, a mean of about 1.2% per gene
<!-- src: results/ledger/pcal_summary.json --> (Fig 3B). Over the 269 expressed, assessable genes in support it is 5.5
(2.8–8.6) <!-- src: results/ledger/pcal_summary.json -->. The interval reflects parameter uncertainty in the
expectation; it is not a prediction interval for the realised count, which has a further Poisson-binomial standard
deviation of about 5.5 <!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->.

**p_cal is conditional on later annotation [post-review exploratory].** H contains only genes that gained at least one
experimental target, so p_cal estimates the probability that the top term is confirmed *given that the gene receives
new experimental BP/MF annotation*, not the unconditional probability of confirmation (Methods). Of the 4,822
t0-eligible genes with a reportable top term, 775 (16.1%, 15.1–17.1%) gained such annotation over the 7.9-year horizon
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->. If the 2018 cohort's
annotation rate applies to U, the unconditional expectation over the 2,583 in-support genes is about 4.9 (2.2–8.1), with
a Poisson-binomial SD of the realised count of about 2.2
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->. Gaining annotation is not
independent of signal (gain rate 0.13–0.14 in the four lower quintiles of top-K mean zavg_BEF and 0.25 in the highest
<!-- src: results/revision/a3_gain_rate_by_signal_quintile.tsv; results/revision/numbers_a3.json -->); with
quintile-specific rates the expectation is 5.1 (2.4–8.3)
<!-- src: results/revision/a3_gain_rate_by_signal_quintile.tsv; results/revision/numbers_a3.json -->, and with the lower
hazard of 2018 genes still uncharacterised in 2022, which resemble U, it is about 4.4
<!-- src: results/revision/a10_round2_numbers.tsv -->. The annual hazard was similar for the 2018 cohort, a 2022 cohort
and those survivors (0.0225, 0.0222 and 0.0199)
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->, but large phylogenetic and
AI-assisted annotation efforts [Feuermann2025] could change it.

**Top 40 [pre-specified fill; deviation in its reading].** The fill pool held 269
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> expressed, assessable, in-support genes, of which 24
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> were removed by a built-in artefact exclusion (23) or a
contradiction (1). With no tiered gene, the frozen order Tier A → Tier B → p_cal reduces to p_cal. The top-40-only
checks (lineage leave-out, DEMETER2 RNAi replication [McFarland2018] and TP53 status) are tier caps, so they are shown
as labels, not demotions (PI ruling before any literature step) [deviation]. The primary top 40 is therefore the 40
highest p_cal values after exclusions (Fig 4). p_cal ranges from 0.036 to 0.141
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->, and the sum is 2.50
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> (point estimate): about two to three of these 40 top
terms would be confirmed if every gene were later annotated. [Post-review exploratory] The top 40 lies in the highest
signal quintile, where the annotation rate is higher, so the unconditional expectation is about 0.4–0.6 (signal-adjusted
0.64, 0.32–1.02) <!-- src: results/revision/a3_gain_rate_by_signal_quintile.tsv; results/revision/numbers_a3.json -->;
with 31 <!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv --> of these genes already published (C4), their rate is probably higher still. Thirty-three of the 40
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes fail at least one top-40 check. The DEMETER2
check failed for 182 of 204 <!-- src: results/ledger/M6_SUMMARY.md --> measured pool genes and was never validated on
positive controls, so a DEMETER2 flag is not evidence against a prediction (S1 Text). The implementing agent's
"clean-first" list, which applied the checks as demotions, shares 20
<!-- src: manuscript/figures/source_data/derived_numbers.tsv --> genes with the primary top 40 (S3 Table).

**Controls for the catalogue [pre-specified].** None of the 708 <!-- src: results/ledger/negative_control.tsv -->
in-support clean-negative genes reached either tier threshold, which is uninformative because no expressed gene did
either; their p_cal was lower mainly in the upper tail (maximum 0.057 against 0.141
<!-- src: results/ledger/negative_control.tsv -->; Fig 3A). Artefact flags gave a built-in Tier-A exclusion to 293 of the 4,137
<!-- src: results/ledger/M6_SUMMARY.md --> predictions, mostly hub-driven (S1 Text). Orthogonal support
separated real from control predictions only weakly: over 247 anchors, the Tier-A support rule was met by 0.320 of real
predictions, 0.279 of matched-gene predictions and 0.223 of decoy-term predictions
<!-- src: results/ledger/false_support.tsv --> (Fig 3C; paired tests in S1 Text). Orthogonal "support" therefore upgrades
no prediction; physical-interaction support gave the clearest contrast, and Table 2 reports it separately.
