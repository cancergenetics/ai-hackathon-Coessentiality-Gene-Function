# Referee 1 report (functional genomics / CRISPR screens / protein complexes)

**Manuscript:** "Pre-registered and calibrated function predictions for uncharacterised human genes from DepMap co-essentiality reveal modest accuracy and widespread curation lag" (PLOS Computational Biology)

**Recommendation: major revision**

## Summary of claims

The authors pre-registered 4,924 "uncharacterised" protein-coding genes (U), defined from annotation data alone. They then ran one co-essentiality method (zavg_BEF) on DepMap 26Q3 and make four claims.

- **C1:** 13% of U is assessable.
- **C2:** On a temporal hold-out (809 genes uncharacterised in GO 2018-07 and annotated since), top-term precision is 0.030. That beats the prior-only and matched-gene nulls. It does not differ from GLS or Pearson, and it falls well below homology (0.218) and hu.MAP transfer (0.049). The logistic calibration model is not detectably miscalibrated out of fold.
- **C3:** Calibrated probabilities for U are low (maximum 0.141; about 30 expected confirmations).
- **C4:** In blinded LLM judging, 18 of 40 top predictions were supported versus 3 of 120 decoys, but 31 of the 40 genes already have published functions. The authors present this as "curation lag". Ten red-teamed candidate reports follow.

The design is unusually transparent. The pre-registration, the temporal hold-out, the circularity filtering, the honest reporting of negative and secondary results, and the clean-negative and decoy controls are real strengths. The study is a useful corrective to anecdotal co-essentiality claims. However, several central interpretations need reframing, and some analyses that a domain reader will expect are missing. All of the fixes below can be done with data already in the repository.

## Major concerns

### M1. The "uncharacterised" definition admits well-characterised complex subunits, which confounds the curation-lag claim (MUST)

Table 2 is dominated by textbook complex subunits: CNOT10/11 (CCR4-NOT), MED31 and MED9 (Mediator), PSMD13 (proteasome), SSR4/TRAP, PHC3/PRC1, NDUFB10/NDUFA2/NDUFA11/NDUFB4 (complex I), COMMD2/3/4/8/10, ELP5/6, TADA2B, NUP43. I checked `preregistration/uncharacterised_genes.tsv` and found the following.

- **Annotation scores:** 3,819 of 4,924 U genes entered through D3 alone. 2,248 of them have a UniProt annotation score of 4–5, and 1,261 have the maximum score of 5. Ten are IDG Tclin.
- **Complex Portal:** 288 U genes are curated Complex Portal subunits. This includes 13 of the primary top 40 and 17 of S20.
- **Top 40:** 20 of the top 40 have annotation score 5.

The cause is mechanical:
- D1 ignores GO cellular-component evidence, and complex membership is mostly curated as CC.
- D3 counts only "focused" PMIDs (≤10 genes per paper), so subunits characterised in multi-subunit papers look unstudied.

Much of what the paper calls *curation lag* (42% N1; 78% N1 in the top 40) is therefore a gap created by the definition, not slow curation. This also explains why co-essentiality's best calls are "rediscoveries".

**Fix:**
- In C1 and Fig 1, report how many U genes have each of: experimental GO CC annotation, Complex Portal or CORUM membership, or UniProt score ≥4.
- Re-stratify the 50-gene audit, the top-40/S20 N1 fractions and the judging results by these flags.
- Split "curation lag" into (a) function published after t0 but not curated, and (b) function known but invisible to D1/D3. The audit's dates already allow this: 13 of 21 N1 genes have evidence from 2021 or later, so 8 do not.
- Soften the title and the Discussion heading "Curation lag is a central finding" accordingly.
- State plainly that this is a limitation of the pre-registered definition, which mirrors Wainberg et al.'s D2 only partially.

### M2. Conclusions are about one AI-generated, unpublished method, but the results speak to co-essentiality generically (MUST)

zavg_BEF does not differ from GLS (+0.006, CI −0.005 to +0.017) or Pearson (+0.002) on the primary endpoint. The abstract omits this, although it is arguably the most generalisable C2 result. The tool's hyper-parameters were also tuned on hu.MAP 3.0 co-complex pairs, which were built after t0 and include complexes containing H genes. That is a route by which post-t0 knowledge enters the predictor, and the manuscript discusses it only for the hu.MAP baseline.

**Fix:**
- Add the GLS/Pearson parity to the abstract.
- Present C2 and C3 as properties of co-essentiality, of which zavg_BEF is one implementation.
- Add a sentence on hu.MAP-tuning leakage, noting that parity with untuned Pearson bounds its effect.
- Ref 38 needs an archival DOI. The method description in Methods should be sufficient for reimplementation without the GitHub repository.

### M3. The calibration claims are stronger than the evidence (MUST)

The model was fitted on 24–25 events with four continuous covariates plus an eight-level family factor, so events per parameter are about 2.
- Two coefficients sit at their bound.
- One family coefficient (−11.86) reflects separation.
- The slope CI (0.51–1.13) is wide.
- The Brier score improves on a constant by about 2%.

"Calibration was adequate" and "a reported p_cal can be read as a probability" overstate this.

**Fix:**
- Rephrase as "not detectably miscalibrated, with wide uncertainty".
- Report the Brier skill score and calibration-in-the-large.
- Add, as an exploratory sensitivity analysis, a one- or two-covariate model (top-K mean zavg_BEF plus term size, no family term) refitted out of fold on H. Show how Σp_cal and the top-40 composition change.
- Note that "within about eight years" extrapolates the 2018–2026 curation rate, which may not be stationary given PAN-GO and similar efforts.

### M4. Novelty against existing co-essentiality and interaction catalogues is not quantified (MUST)

The reports compare against published catalogues only as "agreement". The main text never says how many top-40, S20 or report predictions were already proposed elsewhere:
- Wainberg 2021 module assignments
- Pan 2018 and Kim 2019 networks
- FIREWORKS
- hu.MAP 3.0 complex assignments (e.g., CCDC71L sits in 8 hu.MAP complexes)
- Replogle 2022 Perturb-seq clusters

Without this, C4 cannot be judged.

**Fix:** Add a supplementary table, summarised in one sentence in Results, giving per-gene overlap with each resource. hu.MAP 3.0 and Perturb-seq are already in `data/raw/`; Wainberg's and Pan's supplementary tables are public. Use this table to restate how many reports are genuinely new hypotheses.

### M5. Positioning (SHOULD)

The introduction treats co-essentiality in isolation. Function assignment to uncharacterised genes now comes at scale from several other sources:
- Perturb-seq (Replogle 2022, which also placed C7orf26 in Integrator)
- hu.MAP 3.0 and OpenCell
- proteome-wide AlphaFold interaction screens (Burke 2023, Predictomes 2025 and later proteome-wide efforts)
- PAN-GO phylogenetic annotation (Feuermann 2025)
- deep-learning GO predictors benchmarked in recent CAFA rounds

The homology and hu.MAP results make this context essential, because co-essentiality's added value is about 0.02 over homology. "To our knowledge [temporal validation] has not been applied to co-essentiality" should be checked against Rahman 2021/FLEX, Hassan 2023 and Billmann 2026, and softened.

**Fix:** Add one paragraph to the Introduction and one to the Discussion. In the Discussion, frame the contribution as an evaluation standard (pre-registration, temporal hold-out, calibration, circularity) rather than as a predictor.

### M6. The primary endpoint is mismatched to what co-essentiality predicts (SHOULD)

The primary target is BP/MF terms of 5–200 genes, with CC excluded. Raw-sum R1 favours large terms (median top-1 term size 132; 13% ≤50 genes), and outputs such as "cell population proliferation" or "Golgi vesicle transport" are barely functional statements. For GO complexes (V1), precision was 0.182 (0.093–0.286), six times the headline. The "modest accuracy" conclusion is therefore partly a property of the endpoint.

**Fix:**
- Keep the pre-registered primary, but give V1 equal visibility in the abstract and in Fig 2A.
- Report precision@1 by module family.
- Report the literature-based precision the data already provide: among N1 genes, the predicted function matched the published one for 16 of 31 in the top 40 and 1 of 11 in extra30. That is a direct, curation-independent accuracy estimate.

### M7. The blinded judging test is easy, and it is judged only by models from the same family as the agents that ran the study (SHOULD)

Decoys are other genes' top terms matched only on family and term size. For any gene with literature, the real statement wins almost by construction, so the 18/40 versus 3/120 contrast mainly measures how much literature exists.

**Fix:**
- Add within-gene decoys using the existing pipeline: the gene's own rank-2 to rank-5 terms, or its GLS or prior-only top term. This tests whether the *top* prediction is preferred over the method's alternatives.
- Have a human expert score the 40 primary packets and a random subset of decoys (COULD), and report agreement with the LLM adjudication.
- Report term-only support (16/40) as the primary reading, with module-label support as the secondary one.

### M8. Unexplained failures of the named controls (SHOULD)

INTS15 has 8 clean new terms and TMEM41B has 16, yet no clean true term was ranked for either (Fig 2E). INTS15 is a flagship co-essentiality discovery.

**Fix:** For each control, say whether the true term was not reportable (no two supporting neighbours annotated at t0), fell outside the 5–200 window, or was ranked but below rank 1. This tells readers whether the vocabulary and t0 annotations, rather than the network, limit accuracy.

### M9. The candidate section and Table 3 (MUST for the text items; SHOULD for the analyses)

**Framing and Table 3 (MUST):**
- The abstract headlines INAFM1, which by the authors' own account is the weakest hypothesis: dependency-flat (4 of 1,361 lines < −0.5) and attached to the NRF1 axis at r 0.12–0.21. Replace it with PLEKHH3 and C5orf34, or qualify it.
- The heading "three rediscoveries, seven testable hypotheses" overcounts. RBM34 is a partial rediscovery, and TM2D1/TM2D2 are one observation. Write "three rediscoveries, one partial, five independent hypotheses".
- Table 3 is too dense for a main table. Keep gene, prediction, evidence strength, main caveat and status in the main table, and move the experiments to S Table.

**CCDC71L:** The "decisive experiment" (IP-MS against a PxVxL mutant) tests HP1 binding. HP1 proteins (CBX1/3/5) are not co-dependent with CCDC71L (r −0.10 to −0.01), and Polycomb CBX proteins lack the chromoshadow domain that PxVxL binds. The experiment therefore tests the hu.MAP-derived hypothesis, not the co-essentiality one. Say so, or add a PRC1/PRC2 readout such as H2AK119ub or H3K27me3 at Polycomb targets.

**Controls that can be run on existing DepMap data (SHOULD):**
- **C5orf34:** Test whether the centriole module itself (SPICE1/CEP135/CEP295/WRAP73 pairwise) loses coherence in the 459 TP53-WT lines. If it does, TP53-conditionality is a property of the module (p53 arrest homogenising dependency), not of C5orf34. Also note in the main text that the signal is second-order (B-view z 23.8 versus F-view 2.4; raw r with SPICE1 0.06) and that GLS gives a different term.
- **TRAPPC5:** Show whether the "TRAPPIII-leaning" profile is shared by the other core subunits (TRAPPC1/3/4). If it is, it is a property of TRAPP in cancer lines, not a TRAPPC5-specific hypothesis.
- **PLEKHH3:** Report lineage-adjusted partial correlations with PTEN and PLEKHA1 and the result after excluding PTEN-null lines. Add a competitive-growth (co-advantage) readout alongside pAKT.
- **ANKRD52:** AGO2 loss is near-neutral. State that the prior therefore favours failure of AGO2 phospho-mutant rescue, because PP6 has other substrates.
- **Cell lines:** Several proposed lines (PANFR0344_T1, ETCC-016, MAPAC-HS-77) are organoid or rare models. Give an accessible alternative with matched dependency.

### M10. Robustness checks that cannot discriminate (SHOULD)

The DEMETER2 check fails for 182 of 204 genes and was never validated on positive controls. Validate it on the S20 machinery genes (Commander, complex I, Elongator), which are already scored. If it fails those too, drop it as a tier cap.

The orthogonal "Tier-A support rule" does not separate real from matched-gene predictions (0.32 versus 0.28). Consider reporting the physical class alone, which does discriminate (0.12 / 0.03 / 0.01), as the primary orthogonal readout in Table 3 and Fig 4.

## Minor concerns

1. **Length (SHOULD).** About 20,000 words with dense bracketed labels and heavy notation (U, H, N1–N3, V1/V1′/V2, R1–R3, S20, extra30, Tier A/B). Move the AI-safeguard and deviation narratives, the artefact-flag mechanics and the support-test details to S Text. Add a notation table.
2. **Unreachable tiers (SHOULD).** The Tier A/B thresholds (0.5/0.3) could not be reached by construction. Say this in the Discussion as a design lesson rather than only in C3.
3. **Fig 5B (SHOULD).** The top extra30 bin (0.020–0.099) overlaps the top-40 p_cal range. Explain how fill-pool genes outside the top 40 reach p_cal of 0.099 (artefact exclusions?), or mark the excluded genes.
4. **Table 2 (COULD).** It mixes p_cal and uncalibrated zavg in one column. Split them, and flag Complex Portal membership per row.
5. **Prior-only comparator (COULD).** At 0.000 it is degenerate. Briefly explain why (the most frequent terms are never new terms), and consider a frequency-weighted random draw as an additional null.
6. **Fig 2E (COULD).** Add the reason category requested in M8.
7. **Figs 1C and 3D (COULD).** Annotate with the Complex Portal / CC flags requested in M1.
8. **Authorship (MUST).** PLOS requires human authors, a statement on AI use and contributions, and corresponding-author details. These are currently placeholders.
9. **Language (SHOULD).** "Stringent form of validation" for the LLM judging is too strong, given the shared model family and that the evidence came from a single retrieval agent. Use "blinded literature concordance".
10. **Wording (COULD).** "Co-*advantage*" is a useful term. Define it once in the Introduction.

## Assessment

The methodological framework is valuable and could become a template for evaluating co-essentiality and other network predictors. The main scientific conclusions are directionally correct: low absolute accuracy, a narrow reach, and complementarity with homology and interaction data. But the paper's most striking claim, widespread curation lag, is substantially driven by its own knownness definition. The candidate section and abstract also over-present weak hypotheses. Addressing M1–M4 and M9, mostly text and re-tabulation of existing outputs, would make the paper suitable for PLOS Computational Biology.
