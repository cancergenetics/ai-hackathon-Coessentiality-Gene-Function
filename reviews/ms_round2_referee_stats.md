# Referee 2 (statistics and methodology), manuscript round 2

**Recommendation: minor revision.** Every round-1 MUST item was addressed in substance, and no pre-specified result was altered. What remains: one estimator error in a new Abstract number (M4), surviving unconditional wording (M1–M3), and an unsupported chronology claim (M5). All are text edits; none needs a new look at H.

## Verification

Every post-review number in the Abstract, C1–C4, the Discussion and Methods matches `results/revision/`. Independently recomputed:
- **Σp_cal** from `results/ledger/u_pcal.tsv` (2,583 in-support genes): 30.49. The Poisson-binomial SD is 5.46 (2.21 unconditional), and the expressed in-support subset sums to 20.0.
- **Unconditional Σp_cal:** 30.49 × 775/4,822 = 4.90. For the top 40: 2.50 × 0.161 = 0.40.
- **Exact sign-flip test** from `a5_judging_per_gene.tsv`, using integer-scaled differences: primary p = 2.17 × 10⁻⁴ (20 non-zero), term-only p = 7.13 × 10⁻⁴ (18 non-zero).
- **Null-adjusted census:** 62/228 × 785 + 91/939 × 1,840 = 391.8 expected false calls, so 635 − 391.8 = 243.2 (4.94% of U).
- Novelty counts (17/20/19/22/9/27/34 of 40) and the deployable rule (181/809 = 0.224).

## MUST

**M1. Unconditional wording survives in three places.**
- C3 "Σp_cal [pre-specified headline]" reads: "the expected number of top terms that later experimental annotation will confirm within about eight years". Replace with: "the expected number of top terms that would be confirmed if every gene gained new experimental BP/MF annotation within about eight years (conditional; see below)".
- Make the same change in the Fig 3B legend.
- Do the same in the Introduction's C3 bullet ("that later annotation would confirm").

**M2. Abstract, "about 4.9 (2.2–8.1) unconditionally".** Add the assumption and the label: "about 4.9 (2.2–8.1) if the 2018 cohort's annotation rate applies [post-review exploratory]".

**M3. Top-40 unconditional figure.** The authors' own A3 shows that the constant-rate assumption fails in the highest signal quintile (gain rate 0.25 vs 0.13–0.14), and the top 40 sits there. The signal-adjusted value is 0.64 (0.32–1.02; `a3_gain_rate_by_signal_quintile.tsv`, `numbers_a3.json`), against the 0.40 that is reported.
- In C3 ("about 0.40 (0.21–0.64) for the primary top 40") and in C4 (in the sentence on the 2.50 point sum and in the endpoint-gap sentence), report "about 0.4–0.6 (signal-adjusted 0.64, 0.32–1.02)".
- Add that, with 31 genes already published, their rate is probably higher still.

**M4. The null-adjusted census subtracts expected false calls from all expressed genes, including genes with real signal.**
- Under the stated assumption, observed = Tπ + (N − T)α. So obs − Nα = T(π − α), and T = (obs − Nα)/(π − α) ≥ (obs − Nα)/(1 − α).
- 243 is therefore the excess of calls over the null expectation, not the number of genes that "remain" assessable.
- At full power the per-stratum correction gives 206.5/0.728 + 36.7/0.903 ≈ 324 (6.6% of U; SD tertiles ≈ 325); more at lower power.
- Edit the Abstract to: "allowing for its false-call rate, calls exceed the null expectation by about 243; under that assumption at least about 320 genes (6.6%) carry real signal".
- Edit C1 to: "leaving an excess of 243 (173–306) calls … implying at least about 324 genes with real reproducible signal at full power; this is a lower bound under an untested assumption".
- Rename `implied_true` in `a6_*.tsv` and recompute its interval with the 1/(1 − α) correction (U and clean negatives only).

**M5. The claim that the post-review H analyses were logged before they ran is unverifiable.** The LOOKS.md row for the post-review analyses first appears in commit b39691d, the same commit as `results/revision/`. In Methods ("Post-review exploratory analyses") and in the response letter, replace "were logged in LOOKS.md before they were run" with: "were logged in LOOKS.md; the row was committed together with the results (b39691d), so the order rests on the agents' record, as for the primary look".

## SHOULD

**S1. State the rescaling identity and its assumptions** in Methods A3.
- The identity: E[unconditional confirmations] = Σ p_i r_i, which is exact because confirmation requires annotation.
- One r assumes the gain rate does not vary with p_cal (shown false), that the 2018 rate transfers to genes uncharacterised in 2026, and that p_cal transfers to U.
- Report the survivor-hazard version, 30.5 × 0.145 ≈ 4.4, beside 4.9, and the unconditional Poisson-binomial SD (≈ 2.2).
- In `a3_pcal_conditional.md`, assumption (2) ("independent of whether the top term is right") is not the assumption required. Restate it as above.

**S2. "[post-review]" is used 8 times but never defined.** Use "[post-review exploratory]" or define it.

**S3. Calibration sensitivity.** Replace "the simpler models calibrate at least as well … consistent with over-parameterisation rather than with signal it misses" (Results) and "at least as well" (Discussion) with "comparably (slopes 0.93 and 0.89, with intervals overlapping the frozen model's; c 0.835 vs 0.855)". Overlapping intervals cannot discriminate the explanations.

**S4. Results C4, the "direct, curation-independent estimate of accuracy" (16/31, 52%).**
- Add the Wilson CI (35–68%) and the term-only count, 14/31 (45%; YPEL5 and DPCD are N1 with module-only support).
- Qualify the scope as "among top-40 genes with published function, selected on p_cal".

**S5. Round-1 S7 can be answered without H.** By my count, 12 of the 20 genes shared with the clean-first list were supported (11 on the term alone), against 6 of the 20 that were not shared. Report this.

**S6. DEVIATIONS row dated 2026-10-31 was committed on 2026-10-30** (acdad5a), so its date lies after its own commit. Add an erratum row; do not edit the original. In the Methods, refer to the row by its commit rather than its date.

## Label audit

- **Correct and consistent:** the C4 primary "[pre-specified; scoring operationalised]" with its "[deviation, logged after the result]"; Fisher/McNemar "[exploratory; post hoc, unadjusted]"; A1–A8 "[post-review exploratory]"; Σp_cal 30.5 kept as the pre-specified headline.
- **Inconsistent:** "[post-review]" (S2), and the unlabelled 4.9 in the Abstract (M2).
- **Still overreaching:** "remain" for 243 (M4), the 0.4 gap (M3), "at least as well" (S3), and "logged before they were run" (M5).
- **Acceptable deferrals:** leave-one-module-out, top-40 recalibration and hit rate by expression status need further H looks; correctly listed as limitations.
