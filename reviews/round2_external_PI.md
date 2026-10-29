# Design review, round 2: external PI (DESIGN.md v2.1)

No DepMap values or tool results were read.

## 1. Round-1 must-fix items

My round-1 items:
- **Adequate as written:** 1 (claims and low-yield branch), 4 (ranker), 6 (size and strata of U; exact counts due at freeze).
- **Adequate, but each has a residual flaw:** 2 (assessability → N5), 3 (calibration on H → N4), 5 (supported vs known → N3).
- **7–11 (should/could):** adequate, except that the tier/vocabulary change introduced N1.

OPEN items 1–7 in the disposition are resolved, apart from part of OPEN 5 (→ N5) and part of OPEN 6 (→ N6).

## 2. New problems in v2/v2.1 (MUST fix before freeze)

**N1. Tiers rest on an uncalibrated call.**
- §4.1 says calibration uses V2 but "tiers use the module-level call" (V1′), while §6.1 sets tier thresholds on p_cal.
- V1′ (current releases only) cannot be calibrated temporally.
- **Fix:** p_cal, tiers and Σ p_cal all refer to the V2 top term. The V1′ module is a descriptive label attached to it.

**N2. Three definitions are missing.**
- "V2" is never defined.
- The evidence codes that make a *neighbour* a member of term t are not stated. This affects S(g,t), the backgrounds and prior-only, and on U, IEA vs D1 codes changes coverage greatly.
- No rule maps a term to the "module family" used in §3.7 and §5.4.
- **Fix:**
  - V2 = GO BP+MF, propagated over is_a/part_of with the current obo.
  - Neighbour membership uses the D1 evidence codes, the same codes as targets, at the release in use.
  - Commit and freeze `config/term_families.tsv`: family → GO ancestor IDs. The first match in a fixed order wins; otherwise "other".

**N3. §1.5 contradicts itself.**
- An agent "with no network access" cannot search PubMed.
- **Fix:** replace that phrase with "with no access to co-essentiality outputs".

**N4. The support rule will silently drop much of U.**
- Requiring four covariates inside H's 5th–95th percentiles excludes about 30% of H, and more of U.
- **Fix:** the model is monotone in signal, so use that. U genes below H's 5th percentile on top-K mean zavg or R(g) get the boundary p_cal as an *upper bound*.
  - These genes cannot be tiered.
  - They are summed separately as an upper-bound Σ.
  - Genes outside support in any other direction get no p_cal.
  - Report the counts in each category.

**N5. Split-half neighbour universes differ.**
- **Fix:** compute N_A and N_B (for both R and R0) only over genes that are background genes in both halves and in the full data.

**N6. Leakage residual (part of OPEN 6).**
- **Fix:** drop `colocalizes_with` from V1.
- In LOO, drop neighbour annotations whose IPI with/from field contains the query gene.

**N7. Matching fails for tail genes.**
- At M = 200 or 500, the 0.2-SD caliper cannot be met for strong essentials or genes with a high NaN fraction.
- **Fix:** use one function, `match(g, M, exclusions)`.
  - Apply the caliper only to the 5-match primary null.
  - Otherwise take the nearest M genes by Mahalanobis distance, flag caliper violations and report balance.

**N8. The circularity scan only sees open-access full text.**
- **Fix:** mark PMIDs without full text as "unscannable".
  - The primary analysis excludes flagged annotations only.
  - Add one sensitivity analysis on targets whose PMIDs are all scannable.
  - Report the unscannable fraction.

**N9. Judge validation confounds pipeline accuracy with judge validity.**
- **Fix:** in the 10-H-gene validation, the "real" statement is a known current target term, not the pipeline's prediction.

## 3. Over-complexity: simplifications that keep validity (SHOULD)

**S1. Use one full matrix, not six.**
- Only zavg_BEF needs a full matrix.
- Compute GLS and Pearson *rows* for H, the LOO sample and the named controls (against all background genes).
- Compute U's top-10 partners pairwise via `score_pairs`; this also gives z_B, z_E and z_F.
- This removes the riskiest step (blockwise GLS over about 170 M pairs) and about 5 GB of intermediates.

**S2. Run orthogonal evidence on candidates only.**
- §5 is the largest build.
- Compute it for these genes only:
  - U genes with p_cal ≥ 0.3;
  - the top 40;
  - equal-size sets of matched-gene and decoy predictions (for the false-support rate).
- Run source admission (§5.2) at M4, before any U prediction exists.

**S3. Tier the analyses so the core finishes first.**
- **Core** (the manuscript blocks on these): primary test, GLS secondary, calibration, precision@1 restricted to terms of ≤ 50 genes, circularity exclusion, named controls, V1 ± hu.MAP-train genes.
- **Secondary** (one batch script, reported all or none): Pearson, homology baseline, PPI comparator, t0 = 2019, PMID-dated targets, K = 10/50, no exclusions, U-reweighting, LOO calibration.
- **Cut:**
  - the BioPlex comparator: hu.MAP 3.0 already integrates BioPlex;
  - AUPRC: redundant with MRR when |T| is small;
  - the ≤ 5-PMID sensitivity: it overlaps the "core" stratum.

**S4. Merge the random samples.**
- Use the same 50 random U genes (seed 0) for the §1.5 audit and for the random arm of the §6.2 recall probe.

**S5. Precompute S once per annotation release.**
- Store S as a gene × term matrix, so that p_emp becomes table lookups.

## 4. Per section

Changes needed: §0 N1 · §1 N3 · §2 S1 · §3 N2, N4, N6–N8, S3, S5 · §4 N1, N5 · §5 S2 · §6 N9, S4 · §8 S1, S5. §7, §9 and §10: no change needed.

## 5. Judgement

The design is sound, within scope, and addresses round 1.

The must-fix items are definitional gaps plus one inconsistency. Left open, each would be settled after U predictions are visible, which the freeze exists to prevent. No further round is needed: the PI can apply them and check them off.

The simplifications cut finishing risk without removing any control behind a headline claim.

**Verdict: READY AFTER MINOR CHANGES (listed)**: apply N1–N9 before the `design-frozen` tag. S1–S5 are strongly recommended.
