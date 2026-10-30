# Referee 2 (statistics and methodology), manuscript round 1

**Recommendation: major revision.** The design (frozen plan, one-look log, IUT, cluster bootstrap, out-of-fold calibration, decoy-controlled judging) is unusually disciplined. I recomputed the headline numbers from the committed files and they reproduce: IUT deltas, the calibration table, Σp_cal, sign-flip p = 2.17×10⁻⁴, Fisher p = 5.6×10⁻⁵ and 0.014, Wilson intervals, and the 21 deviation rows. The problems are interpretation and labelling; one (M1) changes the C3 headline.

## MUST

**M1. p_cal and Σp_cal are conditional on the gene being annotated.** H requires at least one target (holdout_sizing.md): only 820 of 5,051 eligible t0-uncharacterised genes (16.2%) gained any experimental BP/MF term in the 5–200 window. p_cal therefore estimates P(top term confirmed | the gene receives new experimental annotation). It is not the unconditional probability of confirmation within about 8 years, which is how the Abstract, C3, the Discussion ("can be read as a probability of later confirmation"), the Limitations and DESIGN §3.7 read it.
- Under a crude constant rescaling, 30.5 becomes about 4.9. U (genes still uncharacterised 8 years later) makes even that optimistic.
- The bootstrap CI (13.8–49.7) reflects parameter uncertainty only. The Poisson-binomial SD of the realised count is a further ±5.5 (Σp(1−p) = 29.8).
- Fix: define p_cal as conditional everywhere. Add the rescaled figure as [exploratory]. State that the CI is for the expectation, not a prediction interval. The design wording was frozen, but the interpretation is wrong and must be corrected.

**M2. "No pre-registered gene exceeded p_cal 0.141" (Abstract).** This holds only for the 2,583 in-support genes. 1,421 genes have no p_cal, including the strongest signals and S20. Write "no in-support gene".

**M3. "Calibration was adequate" overstates the evidence.**
- The model rests on 24 events in 775 genes. Slope 0.82 has Wald CI 0.51–1.13 and bootstrap CI 0.59–1.09. The Brier CI (0.0198–0.0412) contains the constant-rate Brier (0.0300). The top decile over-predicts (0.170 vs 0.115). The c-statistic (0.855) is given without a CI.
- The signalling/lineage coefficient (−11.86, from 0 of 111) is quasi-separation. src/metrics clips these p to 1e-6, which creates high-leverage points in the slope fit and inflates c, because every signalling gene ranks below every hit.
- Fix: in the Abstract, write "not detectably miscalibrated (24 events; slope 0.82, 95% CI 0.51–1.13)". Give the c CI and the slope and c without the signalling family. In Results, give the bootstrap CIs beside the Wald ones; §7 makes gene-cluster resampling the default.

**M4. Module-label crediting is an unlogged operationalisation of the primary C4 endpoint.** DESIGN §6.4 scores "the statement". The OR rule ("process or module") appears only in the scripts/51 judge prompt. DEVIATIONS logs only the descriptive term-only re-reading, and it does so inside the recall-probe row. Both adjudications went to "supported" on module grounds. All three supported decoys were term-based (justifications for J045, J056 and J091), so module crediting helped only real statements.
- The term-only result is still significant: 16/40 vs 3/120. My exact sign-flip from analysis_main_genes.tsv, setting YPEL5 and DPCD to 0, gives p = 7.1×10⁻⁴.
- Fix: log the rule as a deviation (operational, set before judging). Report the term-only test beside the primary in Results and give "16 on terms alone" in the Abstract. p_cal covers the term, not the label.

**M5. Discussion: "69 of 100 candidate and validation genes".** This count includes 10 H genes that are N1 by construction, and the candidates were selected on p_cal, so it is not a prevalence. Use 59/90 and say it does not estimate prevalence; only the random-50 audit (42%, 29–56%) does.

**M6. The union analysis is an oracle comparison.** "Adding it raised precision from 0.218 to 0.236" credits a hit if either of two guesses is right. The deployable rule "homology when it predicts, else zavg_BEF" gives (176 + 5)/809 = 0.224 (+0.006). Report it; call 0.236 an upper bound.

**M7. C1: the sentence "The expression requirement carries the specificity" does not follow.** The filter removes the genes in which the null's anti-conservativeness was measured; it does not show that the problem disappears in expressed genes.
- Take the clean-negative false-call rates (27.2% with any dependency, 9.7% without) and apply them to the 785 and 1,840 expressed scorable genes. That gives about 392 of the 635 calls expected under the null.
- Fix: replace the sentence. Report this as a bound: roughly 240 genes, or 5% of U, exceed what the null rates predict.

**M8. Inferential tests labelled [descriptive].** The Fisher tests (18/40 vs 1/30; N1 only, 16/31 vs 1/11) and the McNemar test (support rule, real vs decoy) are p-values from tests chosen post hoc. Relabel them [exploratory], log them in LOOKS.md, and soften the Discussion's "the ranking reflects the correctness … not merely the fame". That rests on one uncorrected p = 0.014 with only 11 N1 genes in extra30.

## SHOULD

**S1. κ = 0.975 measures reproducibility, not validity.** Two instances of the same model family read identical evidence tables under one rubric, about 30 packets per context, and 87% of statements were scored 0. Near-perfect agreement is expected. Validity rests on hval (9/10, 1/30) and the 3/120 decoy rate.
- Call κ "between-instance agreement" and say which model ran J1, J2 and ADJ.
- results/agent_runs.tsv has a single row, although DESIGN §9 requires every agent run to be logged.
- Drop "a stringent form of validation" from the Discussion.

**S2. The sign-flip test is valid but conservative; report two robustness checks.** Slot exchangeability does not imply a symmetric null for real − mean(decoy). The test it does imply, an exact slot permutation, gives p ≈ 2.3×10⁻⁷ (term-only 2.6×10⁻⁶). Complex-mates also share literature (CNOT10/CNOT11, ER-complex genes, Commander in S20). Averaging d within V1′-label clusters (17 non-zero) gives a sign-flip p of 0.0022. Report both; the conclusion is unchanged.

**S3. The prior-only arm is degenerate.** Its top-1 term has size 200 (IQR 200–200) and precision 0.000, so the IUT is effectively decided by the matched-null arm. MRR vs prior-only does not exclude zero, and at top-5 zavg_BEF is 0.067 vs 0.069 for prior-only. Qualify "the signal is real and specific" accordingly.

**S4. Abstract omissions.** Add the U-reweighted precision@1 of 0.012 (0.007–0.019): "one gene in 33" applies to H, not to U-like genes. Also add the key secondary: GLS and Pearson do not differ from zavg_BEF (Δ +0.006, −0.005 to +0.017). The CI rules out a zavg_BEF advantage larger than 1.7 points.

**S5. Σp_cal sensitivities.**
- (a) Because of the separation, the 403 in-support signalling genes contribute 0.00004. The exact upper bound for 0/111 (2.7%) would allow up to about +11.
- (b) Clean negatives contribute 7.6 of 30.5 (25%), although the paper argues that non-expressed profiles carry no functional signal. Report Σp_cal for expressed in-support genes (20.0) and the H hit rate by expression status.
- (c) The top 40 is the upper tail of p_cal, where the model over-predicts. Report Σ = 2.50 also after applying the out-of-fold intercept and slope, as a labelled sensitivity.

**S6. Dependence in C2.** 17 of the 24 hits lie in the giant PMID+N(g) component, including RPP38/RPP40, SEC11A/SPCS2 and 5 of 19 ribosome-biogenesis genes. PMID-only clusters ignore that dependence, and a bootstrap whose largest component holds 63.5% of genes is unreliable. Add a leave-one-module-out (V1′) or jackknife sensitivity for the primary differences.

**S7. Deviation impact on C4.**
- DEVIATIONS promises results "under both rules", but only the pure-p_cal top 40 was judged. Report support among the 20 genes shared with the clean-first list.
- Dropping the relationship type makes statements less falsifiable and easier to support.

**S8. Explain the gap between endpoints.** 18 (or 16) literature-supported statements sit beside a Σp_cal of 2.50, which is about 0.4 unconditional after M1. That gap quantifies how much more lenient "literature mentions the process or module" is than "the exact GO term is curated experimentally". Say so explicitly.

## COULD

- **C1.** Human re-scoring of all non-zero statements plus 20 random zeros.
- **C2.** Negative control: the upper bound should use the 708 genes that could be Tier-A-like (0/708 gives 0.0042), not 1,167.
- **C3.** Support the fame argument with existing data. L's literature depth does not differ between N1 genes in the top 40 and in extra30 (median 6 focused items each; Mann–Whitney p = 0.70).
- **C4.** Replace the dichotomised top-40 vs extra30 contrast with a logistic regression of support on p_cal across the 70 fill-pool genes.
- **C5.** Give the p_cal (0.04–0.08) of the report genes named in the Abstract, so that readers weigh INAFM1, PLEKHH3 and C5orf34 appropriately.

## Label and number audit

- **Correct:** IUT without adjustment; cluster fallback (logged before the H look); tie-break sensitivity; S20 and extra30 labels; LOO-fitted threefold over-prediction.
- **Mislabelled:** the C4 primary needs "[pre-specified; scoring operationalised]" (M4); Fisher and McNemar tests (M8).
- **Low-yield branch:** handled honestly. The paper leads with C1–C2, thresholds were not relaxed, and the reinterpretation of the fill was logged before the literature step.
- **Numbers inconsistent or misleading in the Abstract or Discussion:** the p_cal ceiling (M2), Σp_cal meaning (M1), "adequate" calibration (M3), 69/100 (M5) and 0.236 (M6). All else matched its source.
