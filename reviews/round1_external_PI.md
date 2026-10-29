# Design review, round 1: external PI (overall scientific judgement)

Inputs: PROMPT, DESIGN v1, LITERATURE (summary, §1.4–§6), DATA, knownness README, tool README/METHOD. No tool results or
DepMap values were read; U was sized from the annotation-only feature table.

## Overall assessment

The design is careful and better than most published co-essentiality "function atlases": hash-gated pre-registration,
a temporal hold-out with named positive controls, matched nulls, proximity/paralog controls, a circularity blacklist and
blinded literature judging. Scope and controls are right.

The main weakness is the paper, not the controls. The design does not yet say what the paper claims, or what it
claims if the yield is low.

The most likely bad outcome is a paper whose top candidates are one of three things:
- **Rediscoveries:** curation-lag genes whose function is already published, presented as new.
- **Coarse, bias-driven calls:** "mitochondrial translation", or a chr19 ZNF-cluster neighbourhood.
- **Inflated confidence:** a model calibrated on well-measured characterised genes, applied to U's flat profiles.

Also: the assessability rule (§4.2) is mis-specified, the tree's list size does not match the definition, the ranker
favours large terms, and literature "support" is not separated from "already known". All are fixable before the freeze.

## Proposed changes

**1. Pre-specify the claim structure and a low-yield branch (§0/§10 new "Claims" subsection). MUST.**
Write down the four claims the paper will make, each with its pre-specified metric:
- (C1) A census: the fraction of U with assessable co-essentiality signal, by stratum. A finding in its own right.
- (C2) Accuracy and calibration on the temporal hold-out.
- (C3) A catalogue of calibrated predictions for U. The headline is the *expected number of correct predictions*,
  Σ calibrated P, with a bootstrap CI, not the count of "hits".
- (C4) Literature-checked candidates with experiments.

Add a pre-written branch for low yield: if fewer than about 10 genes reach Tier A, the paper leads with C1 and C2, and
the deep-dives cover the best available genes, labelled by tier. Otherwise a weak result invites post hoc threshold relaxation.

**2. Fix the assessability rule (§4.2). MUST.**
"Below the 95th percentile of the matched-gene null overlap" compares a U gene's split-half stability with that of
*other real genes*. That would label most genes non-assessable, and the reference is not a null. Replace it with two
parts:
- (a) A **single-gene profile-informativeness rule**, frozen now before any pairwise computation (LITERATURE §3.3). It
  uses Chronos SD, the number of lines with effect < −0.5, NaN fraction, and expression from
  OmicsExpression (e.g. TPM ≥ 1 in ≥ 10% of lines). Use it as a pre-registered stratifier, not as a filter on U.
- (b) Split-half top-25 overlap tested against a true null: overlap under random partner sets, or under split-halves
  with gene labels permuted within each half. Use a stated quantile, e.g. 99th.

Report the assessable fraction per stratum. This number is claim C1.

**3. Make calibration transfer to U-like genes (§3.4). MUST.**
U genes are less essential, lower-variance and lower-expressed than the calibration genes (LITERATURE §3.3). A confidence
model on top-K mean zavg_BEF and split-half overlap, fitted on characterised genes, will very likely be overconfident on
U. Required changes:
- (i) Add profile SD, mean effect and expression as covariates, or fit within strata from change 2a.
- (ii) Report calibration (ECE or reliability curve, with bootstrap CI) separately on a *U-like* subset of benchmark 1,
  matched on those features, and on the temporal hold-out. Hold-out genes were D1 at t0, so they are the most U-like
  genes available.
- (iii) Pre-specify the response to miscalibration on the hold-out. If the ECE CI excludes 0, refit isotonic regression
  on hold-out genes with 5-fold CV (seeds 0–4) and report both versions.

**4. Control term granularity and redesign the ranker on calibration data only (§3 Predictor). MUST.**
S(g,t) = Σ max(z,0) over annotated neighbours grows with term size. The top term will drift toward mitoribosome,
complex I and ribosome biogenesis, which are the biases LITERATURE §1.4 warns about. That produces calls that are
correct but uninformative.

Fix it as follows:
- Cap V2 terms at ≤ 200 genes.
- Report the most specific significant term after DAG-aware pruning (elim/parent–child).
- Require ≥ 2 supporting partners that remain after same-arm and paralog removal.
- Allow **one** pre-specified choice among at most three rankers: raw S, hypergeometric p, and S divided by its
  expectation under term frequency. Make the choice on benchmark 1 (LOGO, non-U genes) only. The temporal hold-out stays
  untouched as confirmation.

Also report precision@1 weighted by information content (or Smin, Clark & Radivojac 2013), so that coarse terms do not
score as successes.

**5. Separate "supported" from "already known", and remove co-essentiality from the literature arm (§6). MUST.**
For deep-dive genes, literature support often *means* the function is already published but not curated (the
TIMM29/DMAC1 pattern). Required changes:
- Agent L classifies each gene **before** judging: (N1) function established in the literature, (N2) partial or
  indirect evidence, (N3) no functional literature.
- Report agreement with the literature as validation (N1/N2), and novelty claims only for N3 (and N2 where the
  prediction goes beyond what is known).
- L and J must exclude, or flag separately, DepMap-derived sources: the DepMap portal co-dependency tab, Wainberg's atlas,
  FIREWORKS, Predictomes, and papers on the circularity blacklist. Otherwise "support" is our own signal returning.
- Run the 50-gene curation-lag audit **before** U predictions; its estimate is the expected rediscovery rate for C3.

**6. Pin the exact size and composition of U, and pre-register strata (§1). MUST.**
RESEARCH_TREE.md states "~2.1–2.6k genes". From the feature table, the D1-approximately ∩ (D2 ∪ D3) rule gives about
5,200 genes, about 4,600 of them in DepMap. The OR with "≤ 10 focused PMIDs **or** Tdark" makes D3 permissive, and D2
then adds almost nothing. About 317 olfactory receptors, 356 ZNFs, 75 KRTAPs and many testis genes are included.

The size is acceptable for a census (D1 is the stringent part), but:
- (i) State the exact |U| and |U ∩ scorable| in DESIGN.md before the freeze, and correct the tree entry.
- (ii) Pre-register reporting strata. Do not remove these genes from U:
  - chemosensory and epidermal families (OR, TAS2R, KRTAP, LCE);
  - chr19 KZFP clusters and other tandem families, which are a proximity-artefact hot spot, and the tool shows a residual
    OR artefact;
  - expressed vs not expressed in DepMap lines;
  - a strict "core" subset (≤ 3 focused PMIDs and Tdark).

Headline numbers should be given for U and for the expressed, non-tandem stratum.

**7. Pre-specify the tier fallback and make orthogonal support coverage-aware (§6 tiers). SHOULD.**
- P ≥ 0.5 may yield zero genes. Fix how the top 20 are filled: Tier A, then Tier B by calibrated P, all labelled by tier.
- Base tiers on the V1 (complex) prediction. Treat V2 as secondary.
- For each class, separate "not covered" from "covered, no support". Requiring support penalises the least-studied genes,
  and that bias should be visible.
- Count localisation as a contradiction only when HPA reliability is Enhanced or Supported and the localisation is
  exclusive. About half of proteins are multi-localised.

**8. Strengthen the success criteria (§3). SHOULD.**
Beating the prior-only and matched-gene nulls is close to guaranteed, so it is not informative as a primary criterion.
Keep it, and add these, reported whichever way they fall:
- (a) zavg_BEF vs GLS on the temporal hold-out, two-sided, stratified by neighbourhood/complex size. The tool ties GLS
  on small complexes, and U genes probably sit there.
- (b) Calibration error from change 3.
- (c) Named positive-control recovery: rank of the true term for each of the 11 genes, with circular annotations excluded.

The prompt fixes zavg_BEF as primary. If GLS is equal or better, say so plainly.

**9. Power the blinded literature test (§6). SHOULD.**
With 20 genes, mostly "unaddressed" verdicts, and a paired real-vs-decoy comparison, there is almost no power.
- Blind-judge the top 40, which is cheap with agents. Keep full deep-dive reports for 8–10.
- Pre-specify an exact sign test (McNemar) on discordant pairs.
- Report the "unaddressed" rate as a measure of novelty.

**10. Rebalance effort. SHOULD.**
Cut or demote:
- §4.4 clustering, to a supplementary figure (COULD);
- §4.3(e) lineage check, to top candidates only;
- the D1/D2/D3 sensitivity matrix, to one table.

Add effort to the deep-dives and experiments. Each candidate report should name:
- one *decisive, falsifiable* experiment, with its expected readout if the prediction is right and if it is wrong;
- the DepMap cell lines where the gene and its predicted partners are co-dependent, as the recommended experimental
  model;
- the strongest alternative explanation, and the experiment that would separate it from the prediction.

**11. Note tool-tuning leakage into the V1 hold-out (§3.2). COULD.**
zavg_BEF's few hyper-parameters were tuned on hu.MAP 3.0 (2025), which encodes post-t0 complex knowledge. The leakage is
minor, but report the V1 temporal metric with hu.MAP-only complexes excluded.

## Sections needing no change

- **§2 (verification):** sound as written.
- **§5 (orthogonal classes):** right as designed, apart from change 7.
- **§7–§10:** adequate (statistics reviewer: check BH scope across genes × terms).
