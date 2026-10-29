# Round 1 review: statistics (DESIGN.md v1)

## Assessment

The design is pre-specified, has a temporal hold-out, and its nulls are right in spirit. Six gaps should be fixed before any DepMap computation:

1. The primary endpoint is underspecified (vocabulary, targets, clustering).
2. The term score is biased by term size and hubs; the hypergeometric p carries BH-FDR but drives no decision.
3. The assessability threshold is not well defined.
4. Calibration transferred from characterised genes to U will be optimistic.
5. Orthogonal support has uncontrolled multiplicity and degree bias.
6. The 20-gene blinded literature test detects only very large effects.

**Expected sample size and power** (feature table only, no DepMap values):

- 5,781 DepMap genes had 0 experimental informative BP/MF terms in GO 2018-07 and ≤ 10 focused PMIDs before the cut-off.
- Of these, 1,142 now have ≥ 1 low-throughput experimental informative term; 710 have ≥ 2.
- After removing circular PMIDs, targets outside 5–300 genes and NaN ≥ 10%, expect **H ≈ 700–1,000**. The 2018 column counts HTP codes, so it only approximates D1(t0).
- All 14 named controls pass the t0 filters.

Assume n ≈ 800, a design effect of about 1.3 (shared papers and complexes) and 10–20% discordant pairs. The minimum detectable paired precision@1 difference is then about **3.5–4.5 points** (80% power, two-sided α = 0.05). The primary is adequately powered unless weak-signal genes dilute the effect. The 14 controls are a descriptive case series: they can detect only differences of about 40 points.

## Concrete changes

### A. Predictor and term scoring

1. **Must: use a size- and hub-adjusted ranking.**
   - Problem: S(g,t) grows with term size and with how densely neighbours are annotated. Top-1 terms will drift toward the largest allowed terms (~300 genes) and toward hub complexes (ribosome, OXPHOS).
   - Fix: rank by a matched-gene empirical p, p_emp(g,t) = (1 + #{m: S(m,t) ≥ S(g,t)}) / (1 + M), with ties broken by S.
   - Use M = 500 matched genes (#10). Exclude g, N(g), same-arm genes and genes annotated to t.
   - Cheap; adjusts for term size, multifunctionality and essentiality at once.
   - Keep S-ranking as a sensitivity analysis.
   - Flag predictions with > 50% of S from top-1% in-degree neighbours.
2. **Must: define the hypergeometric test, then demote it.**
   - Set n = |N(g) ∩ annotated background|, not 25. The background is scorable genes with ≥ 1 annotation in the vocabulary at the release in use (t0 for the temporal benchmark), with the query removed.
   - Neighbours are mutually co-essential: one complex entering N(g) adds about 8 non-independent "successes". The p is therefore anti-conservative, and BH within a gene is not an FDR.
   - Label it descriptive, or replace it with p_emp.

### B. Endpoint, metrics, unit of inference

3. **Must: specify the primary endpoint completely.**
   - Vocabulary: V2 (GO BP+MF), on which H is defined.
   - Targets: T(g) = propagated current terms with D1 evidence codes, minus the propagated t0 set from the same code.
   - Map IDs with the current ontology (alt_id, replaced_by), counting dropped obsolete targets.
   - Apply the 5–300 size filter using t0 sizes. Exclude genes with empty T(g) and report the count.
   - Compute D1(t0) and D1(now) with one function. The archived feature column includes HTP, so it is not D1.
   - Key secondary: V1 complexes from GO CC "protein-containing complex" terms in the same archives, excluding hu.MAP (tuning leakage).
4. **Must: treat the gene as the unit and resample clusters.**
   - Hold-out genes are not independent: TEDC1/2, POU2AF2/3 and Integrator subunits share neighbourhoods and papers.
   - Clusters are connected components of a graph linking hold-out genes that share a supporting PMID or appear in each other's N(g).
   - Use a paired cluster bootstrap (10,000 replicates, seed 0, BCa).
   - Report the numbers of genes and clusters and the design effect.
5. **Should: choose metrics that fit few targets per gene.**
   - Per-gene AUPRC equals 1/rank when |T(g)| = 1. Report reciprocal rank, and AUPRC only for |T(g)| ≥ 3.
   - Restrict term-centric macro averages to LOO terms with ≥ 10 genes.
   - Add precision@1 weighted by information accretion (Clark & Radivojac 2013), or restricted to terms of ≤ 50 genes; propagation makes generic hits cheap.
   - Report the size distribution of top-1 terms for every method.
6. **Should: set the baselines precisely.**
   - Compute prior-only frequencies at t0, on the same background and size filter.
   - Add a homology baseline: rank by the gene's t0 IBA/ISS/IEA terms, then by frequency.

### C. Temporal hold-out

7. **Must: handle covariate shift between H and U.**
   - Post-2018 characterised genes are enriched for strong DepMap signal (co-essentiality found some); U is the less essential residue.
   - Report standardised mean differences between H, U and LOO on six label-free covariates: mean effect, SD, NaN fraction, top-K mean zavg, R(g) (#11) and neighbourhood annotation coverage.
   - Report metrics by signal quintile.
   - Report a U-reweighted estimate using inverse-odds weights from a logistic model of U vs H, trimmed at the 1st and 99th percentiles.
8. **Must: detect circularity systematically.**
   - A hand-compiled blacklist misses papers that used DepMap without being cited in LITERATURE.md.
   - Run a pre-specified Europe PMC full-text query on every supporting PMID ("DepMap", "co-essential*", "codependen*", "Project Achilles").
   - Exclude flagged annotations from the primary analysis and analyse them separately.
   - Report the query's sensitivity on controls whose discovery route is known (for example CCDC32).
9. **Should: align H with U and record power in advance.**
   - Add D2(t0) from UniProt 2018_07 annotation scores and report the subset of H that meets it.
   - Sensitivity analyses: t0 = 2019-07, and ≤ 5 PMIDs.
   - Compute |H|, the |T(g)| distribution, the cluster count and the minimum detectable effect now, without DepMap, and record them in DESIGN.md. If the effective n is below 300, pre-declare the primary underpowered.

### D. Null models

10. **Must: specify the matched-gene null.**
    - Match on Mahalanobis distance over mean effect, log SD and NaN fraction; caliper 0.2 SD; without replacement.
    - Exclude N(g), same-arm genes and genes annotated to g's targets.
    - Report balance (standardised mean difference < 0.1).
    - Five matches suffice for the paired precision@1 contrast (efficiency about 0.83). Gene-level null quantiles (#1, #11) need M ≥ 200.
    - Could add: for LOO, permute annotation sets within bins of annotation count × in-degree. Degree-preserving rewiring adds little, since out-degree is fixed at K.

### E. Assessability

11. **Must: redefine the split-half null.**
    - The problem: matched genes' own reproducibility includes real signal, so the current rule keeps the top 5% of each essentiality stratum. That is a quantile, not a null.
    - Statistic: R(g) = mean over seeds s of |N_A^s(g) ∩ N_B^s(g)| / K.
    - Null: R0(g,m) = mean over s of |N_A^s(g) ∩ N_B^s(m)| / K, for M = 200 matched genes m. This captures overlap driven by hubs and essentiality.
    - Rule: g is assessable if R(g) exceeds the 95th percentile of R0(g,·).
    - Measure overlap as the top-25 intersection, with RBO as a sensitivity analysis.
    - Stratify the half-splits by lineage. Fix background genes and K at their full-data values, or record them per half.
    - Toy acceptance: null genes are assessable at 5% ± 2%.

### F. Calibration

12. **Must: calibrate on the temporal hold-out, not LOO.**
    - Characterised genes carry many annotations, which inflates their base rate of top-1 hits. U genes have few true terms and poorly annotated neighbourhoods.
    - Fit a monotone logistic model of hit@1 on top-K mean zavg, R(g), neighbourhood annotation coverage and log top-term size, with 10-fold cluster cross-fitting on H. Use LOO only as a sensitivity analysis.
    - 1-D isotonic on two binned covariates is undefined; if kept, use pre-specified 2-D isotonic.
    - Report a reliability diagram, the Brier score, and calibration intercept and slope with CIs.
13. **Must: respect the support of the calibration data.**
    - U genes with covariates outside H's 5th–95th percentile range get no calibrated probability.
    - Report the expected number of correct Tier A top terms, Σ p_cal, with a CI. This is the U-level error statement and replaces BH.
    - Calibrate the exact pipeline used for U (ranking rule, same-arm removal, K).
    - p_cal = probability of confirmation by later annotation (conservative, since annotation is incomplete).

### G. Multiple testing

14. **Should: state the role of p-values.**
    - BH within a gene controls nothing across about 4,500 U genes, and the tier rule uses no p-value.
    - Either drop BH and rely on #13, or, if p_emp gates claims, use Benjamini & Bogomolov (2014): Simes per gene, BH across genes at q = 0.1, then BH within selected genes at q·R/m.

### H. Orthogonal support

15. **Must: correct for degree bias and record coverage.**
    - PPI and proteomics coverage favours studied, abundant proteins.
    - For continuous sources, use per-gene row percentiles, not the global random-pair 95th percentile.
    - Match random partners on degree in each source, with an empirical p from B ≥ 1,000 draws, (1+b)/(1+B).
    - Code "not covered" separately from "not supported".
    - Keep a source only if the lower 95% CI of its co-complex odds ratio (non-hu.MAP complexes) exceeds 2.
16. **Must: control multiplicity across classes.**
    - With about 5 classes at p < 0.05, "≥ 1 class supports" fires up to about 23% of the time under the null.
    - Apply Holm across the classes covering g.
    - Estimate the empirical false-support rate by running the full rule on matched-gene and decoy predictions, and report it next to the Tier A count.

### I. Blinded literature validation

17. **Must: fix the power and the analysis.**
    - With 20 pairs and a binary outcome, an exact McNemar test has about 80% power only for differences of about 35–40 points (for example 50% vs 10%). "Unaddressed" will dominate for U genes.
    - (a) Use 3 decoys per gene, matched on compartment and term size or information content (seed 0).
      - Score each statement +1 supported, 0 unaddressed, −1 contradicted.
      - Primary test: exact one-sided sign-flip permutation on real minus mean-decoy score.
    - (b) As a secondary, judge 30 more U genes sampled across p_cal bins, and fit support against p_cal. This is the only direct calibration check on U.
    - (c) Use two independent judges and report Cohen's κ; a third adjudicates disagreements.
    - (d) Support whose only source is co-essentiality-derived counts as "unaddressed".

### J. Criterion and toy tests

18. **Should: pre-specify the decision logic and toy tests.**
    - Beating both nulls is an intersection-union test, so no multiplicity adjustment is needed.
    - Pre-specify what failure implies (no calibrated claims for U) and a fallback if Tier A is empty.
    - Report the primary metric on each split-half network; gene resampling ignores network uncertainty.
    - Toy null-matrix acceptance: genes with any BH-significant term ≤ 0.05, and p_emp uniform (KS p > 0.01).
