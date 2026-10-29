# Round 2 review: statistics (DESIGN.md v2.1)

All round-1 items appear in the text. What remains are gaps that leave choices for later, plus one label leak. Fixes are wording only.

## A. Round-1 must-fixes: implementation check

**A1. Endpoint (§3.3): the denominator, the term evaluated and the candidate set are unstated.**
Add: "Hit@1 = top-ranked *reportable* term (≥ 2 supporting partners) ∈ T(g). Denominator = all H genes. No reportable term scores 0, and coverage is reported. Candidates = V2 terms with 5–200 annotated background genes at t0. The ranker and reportability rule chosen for zavg_BEF apply unchanged to GLS, Pearson, PPI, split-half networks and the matched null. Primary network = full-data zavg_BEF. 'Precision@1 ≤ 50' restricts both candidates and targets; genes with no such target are dropped and counted."

**A2. Ranker (§3.1).** Correct. Add: "MRR ties (< 0.005) → R3, then R1. RR = 0 if no correct term is ranked; in LOO the query's annotations are removed from counts."

**A3. Matched genes (§3.4): label leak and inconsistencies.**
- Leak: R3 uses the §3.4 matched genes, and §3.4 excludes "genes annotated to g's targets". The ranking of g's terms then depends on T(g), which is undefined for U.
- The 500/200/5 draws are unrelated; the caliper cannot supply 500 for extreme genes; paralogues are not excluded.

Replace with: "Per gene, one list of 500 matched scorable genes, ordered by Mahalanobis distance on (mean effect, log SD, NaN fraction). Excluded: g, N(g), same-arm genes and paralogues. No replacement within g; seed 0. If fewer than 500 fall within the 0.2 SD caliper, take the nearest and report the violation rate. First 5 = null comparator; first 200 = assessability null; all 500 = R3. R3: p_emp(g,t) = (1 + #{m ∈ M(g) \ A_t : S(m,t) ≥ S(g,t)}) / (1 + |M(g) \ A_t|), where A_t = genes annotated to t at the release used. The null comparator alone skips genes annotated to T(g). Null hit = mean over the 5 matches of [m's top reportable term ∈ T(g)]."

**A4. Cluster bootstrap (§3.5).** N(g) is gated, so clusters cannot exist at freeze; percentile vs BCa is undecided. Add: "Clusters fixed once (shared PMIDs + zavg_BEF N(g)) for all comparisons; PMID-only at freeze. Decision on the percentile CI; BCa reported. Effective n = |H| / design effect. If underpowered, decided as specified, with that label."

**A5. Covariate shift (§3.6).** Add: "Weight model = the six SMD covariates; target = U genes eligible for p_cal; refitted per bootstrap replicate; applied to each method's precision@1 and both primary differences."

**A6. Calibration (§3.7, §0).**
- (i) §0 uses an ECE CI "excluding 0"; a bootstrap ECE CI almost never contains 0, and §3.7 omits ECE. Replace with "slope CI excludes 1 **or** intercept CI excludes 0".
- (ii) Signs: "≥ 0 for top-K mean zavg, R(g) and coverage (= fraction of N(g) with ≥ 1 V2 annotation); ≤ 0 for log term size; family unconstrained."
- (iii) "H metrics use out-of-fold predictions averaged over seeds 0–4; U p_cal comes from the model fitted on all of H."
- (iv) "Support = continuous covariates within H's 5th–95th percentiles and a family with ≥ 30 H genes; share of H inside reported. Bins = deciles of out-of-fold p_cal, merged to ≥ 30."
- (v) The Σ p_cal CI method is missing: "Refit on 2,000 cluster-bootstrap resamples of H (seed 0), percentile CI. Report for all U genes with p_cal and for Tier A."

**A7. Assessability (§4.2).** Differing half backgrounds deflate R(g); null ties near 0 can fail the "5% ± 2%" toy test (§2.5) spuriously. Add: "Half-neighbour lists are restricted to BG_A ∩ BG_B ∩ BG_full, with §3.1 exclusions. The rule is strict, R > q95. Toy acceptance: ≤ 7% of null genes and ≥ 80% of planted strong-module genes assessable."

**A8. Orthogonal support (§5.2–5.3): not yet implementable.**
No Holm α, no within-class combination rule; statistic and member set deferred to M6 although §5 must be frozen first.

Add: "Members = scorable genes annotated to the called term, excluding g. Statistics: binary sources, number of g–member edges; continuous sources, mean member row percentile; localisation, fraction of members sharing a compartment with g. Null: 1,000 equal-size sets, degree-matched within the source. Simes within a class; Holm across classes at α = 0.05 per gene. Admission: continuous scores dichotomised at the 95th row percentile; OR CI by bootstrap over complexes."

**A9. Blinded judging (§6.4).** Add: "Adjudicated scores. A decoy is not the real term, an ancestor or a descendant, and has Jaccard < 0.1 with it. Exact enumeration, one-sided α = 0.05; reported by N-class. If H validation fails: one logged revision, re-validation on 10 new H genes; a second failure is reported as 'not validated'."

## B. Internal consistency

1. **Size windows.** The disposition defers a 3–300 complex window, which conflicts with 5–200. Freeze "5–200 at the release used, for V2, V1 and V1′".
2. **V2 vs V1′.** p_cal is fitted on the V2 top term, but tiers use the V1′ call (§4.1). Add: "p_cal, tiers and judged statements attach to the V2 top reportable term; V1′ is a descriptive label."
3. **Tier B.** Add: "also requires all Tier A conditions except p_cal ≥ 0.5 and diagnostic support."
4. **C2-fail branch.** Add: "Top 40 by the frozen ranker's top-term score among assessable, expressed genes."
5. **LOOKS.md.** Consistent; LOOKS.md must also record the calibration specification before H is opened.

## C. New problems

1. **Release shift in calibration covariates.**
   - H covariates use t0 annotations, U current ones, so coverage and term size are larger in U. The monotone model extrapolates upward; the support check misses this.
   - Fix: "Coverage and log term size enter as within-release percentile ranks; raw scale as sensitivity."
2. **Horizon.** p_cal = "probability of D1-evidence confirmation within about 8 years".
3. **Seeds.** Add matched-list and Σ p_cal bootstrap seeds to `config/seeds.yaml`.

**Verdict: READY AFTER MINOR CHANGES (listed):** A1, A3, A4, A6(i)–(v), A7, A8, B1, B2 and C1 are required before freeze. Others recommended.
