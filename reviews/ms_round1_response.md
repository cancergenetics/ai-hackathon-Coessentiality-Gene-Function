# Response to reviewers, manuscript round 1

Manuscript: *A pre-registered, temporally validated evaluation of co-essentiality function predictions for
uncharacterised human genes: modest accuracy, narrow reach and many already-published functions* (previous title:
"Pre-registered and calibrated function predictions ... reveal modest accuracy and widespread curation lag").

We thank the five reviewers. Every numbered item is answered below. "Done" names the change and where it is. "Not
done" gives the reason. Section names refer to `manuscript/src/*.md`, rebuilt into `manuscript/manuscript.md`, `.docx`
and `.pdf` by `scripts/79_assemble_manuscript.py` and `scripts/80_build_manuscript.sh`.

## Ground rules for the revision

- **No pre-specified result was changed.** These stay as they were:
  - the IUT and its CIs;
  - the calibration table;
  - Σp_cal 30.5 (13.8–49.7);
  - the judged primary result (18/40 vs 3/120, p = 2.2 × 10⁻⁴);
  - the census (646 / 635).
- **New analyses.** All new analyses were requested by the referees. They were run by `scripts/90_revision_analyses.py`
  into `results/revision/` (summary: `results/revision/SUMMARY.md`).
  - The analyses that read H outcomes (A3, A4, A7, A8) were logged in LOOKS.md (row dated 2026-10-30) before they ran.
  - In the text they are labelled **[post-review exploratory]**.
  - Every new number carries a `<!-- src: file -->` tag.
- **New figure and tables.**
  - **S4 Fig** (`scripts/62_figS4.py` → `manuscript/figures/FigS4.png/.svg`, source data `source_data/FigS4*.tsv`):
    - A: N1 rates by entry route and definition-artefact flag;
    - B: novelty overlap with earlier catalogues;
    - C: null-adjusted assessability;
    - D: calibration-model comparison.
  - **S9 Table:** novelty overlap, `results/revision/a2_novelty_overlap.tsv`.
  - **S10 Table:** decisive experiments, `manuscript/supplementary/S10_Table_decisive_experiments.tsv`.
  - **Table 4:** notation, in Methods.
- **Changes outside the manuscript text.**
  - **References:**
    - `references/old_meta.tsv`: Fischer 2025 pages.
    - `references/new_meta.tsv` and `references/literature_refs.tsv`: Holm 1979 added.
    - `scripts/79_assemble_manuscript.py`: prints "Available from: URL" for a record that has no DOI.
  - **`README.md`:** the prompts paragraph now points to `docs/AGENT_PROMPTS.md`, and the run order gains rows for
    scripts 62, 90 and 91.
- **Not committed.**

---

## Referee 1 (functional genomics), `ms_round1_referee_domain.md`

**M1. The definition admits characterised complex subunits, which confounds the curation-lag claim (MUST).** Done.

- **New Results paragraph** (C1, "Much of this reflects the definition of 'uncharacterised' [post-review exploratory]"):
  - Counts: 3,819 D3-only; 2,248 with score ≥ 4 (1,261 with score 5); 288 Complex Portal subunits; 1,218 with
    experimental GO CC; 1,933 with any flag.
  - Random-50 N1 rate by route: 19/34 (56%) for D3-only vs 2/16 (13%) for D1&D2.
  - By flag: 13/22 vs 8/28.
  - The split you asked for: 13 of 21 N1 genes have evidence from 2021 or later (lag in the usual sense). The other 8
    have older evidence, and 6 of those 8 carry a definition-artefact flag.
  - The paragraph says plainly that much of the "lag" reflects the pre-registered definition, which follows Wainberg's
    D2 only in part.
- **C4, re-stratified:**
  - 37/40 top-40 genes and 20/20 S20 genes entered through D3 alone; 30/40 and 20/20 carry a flag.
  - N1 rate among the 90 candidates: 58/80 for D3-only vs 1/10.
  - Judged support in the top 40: 17/30 with a flag vs 1/10 without.
- **Table 2** gains a "UniProt score; CP" column.
- **S4A Fig** shows the N1 rates.
- **Title and headings:**
  - The title no longer says "widespread curation lag".
  - The Discussion heading "Curation lag is a central finding" is now "Published functions, uncurated or invisible to
    the definition". It states the definitional limitation and gives a stricter definition for future work.
- **Not done:**
  - CORUM membership could not be checked (CORUM is not in `data/raw`, and the fetch failed on its TLS certificate).
  - Fig 1C and Fig 3D were not redrawn; S4A Fig carries the flag stratification instead.

**M2. The conclusions are about one AI-generated method. GLS/Pearson parity belongs in the Abstract; hu.MAP tuning
leakage; Ref 38 DOI.**

- Done:
  - **Abstract:** now gives the GLS difference (+0.006, −0.005 to +0.017).
  - **Results C2 (GLS paragraph):** states that the interval excludes a zavg_BEF advantage of more than 1.7 points, and
    that accuracy is a property of co-essentiality.
  - **hu.MAP-tuning leakage:** stated in Results C2, Methods ("The co-essentiality method") and Limitations. Parity with
    untuned Pearson bounds its effect.
  - **Introduction:** frames zavg_BEF as one implementation, with GLS and Pearson as comparators throughout.
- Ref 38 (partly not done):
  - It has no archival DOI; the tool belongs to a third party and we do not redistribute it.
  - The Methods now state that the description is meant to allow reimplementation without the repository.
  - Data availability states that the tool has no archival DOI.

**M3. The calibration claims overstate the evidence (MUST).** Done.

- **Wording:** "not detectably miscalibrated, with wide uncertainty" in the Abstract, Results C2 (Calibration) and the
  Discussion.
- **Added:**
  - 3.4 events per parameter;
  - bootstrap slope CI 0.59–1.09;
  - c 0.855 (0.805–0.903);
  - Brier skill 0.021;
  - calibration-in-the-large +0.0001;
  - the Brier CI contains the constant-rate value.
- **Separation:** 0/111 signalling genes, upper bound 0.027. Without the signalling genes the slope is 0.82 and c is
  0.830.
- **Simpler-model sensitivity, cross-fitted out of fold:**
  - zavg_BEF-only model: slope 0.93 (0.60–1.25), c 0.835, Brier skill 0.037.
  - With coverage added: slope 0.89, c 0.832.
  - Σp over the same 2,583 genes: 41.6 and 38.6.
  - Top-40 overlap with the primary list: 7/40 and 14/40, because mitoribosomal and ribosome-biogenesis genes enter when
    there is no family term.
  - Shown in S4D Fig.
- **"Within about eight years" (stationarity):** annual hazards are 0.0225 (2018 cohort), 0.0222 (2022 cohort) and
  0.0199 (2018→2022 survivors). PAN-GO-scale efforts could change the rate (Results C3, "p_cal is conditional on later
  annotation").

**M4. Novelty against existing catalogues is not quantified (MUST).** Done.

- New Results paragraph "Overlap with earlier catalogues", with S9 Table and S4B Fig. Top 40:
  - hu.MAP 17/40;
  - Predictomes 20/40;
  - Wainberg GLS pair 19/40;
  - Wainberg module (d ≥ 0.5) 22/40;
  - Kim 2019 9/40;
  - any co-essentiality catalogue 27/40;
  - any resource 34/40.
- Only 6 of the top 40 have no prior. All 20 S20 genes have a prior.
- Wainberg Supp. Data 3 had already predicted functions for CCDC71L, C5orf34 and INAFM1.
- Novelty claims were adjusted in:
  - the Abstract and its Conclusions;
  - the Author summary;
  - Results C4 and the candidate-report section;
  - Table 3 (new "Prior in catalogues" and "Status" columns);
  - the Discussion and Future work.
- Each report also gained a "Prior prediction" bullet (`reports/*.md`, commit cb6b460).
- Not done:
  - Pan 2018 (Cell Press 403; the supplement is not open access).
  - FIREWORKS (no genome-wide table).
  - Replogle 2022 clusters (no assignment file in `data/raw`).
  - These are stated as limits, so the counts are lower bounds.

**M5. Positioning (SHOULD).** Done.

- **Introduction:** a new paragraph on Perturb-seq (including C7orf26/Integrator), hu.MAP 3.0, OpenCell, AlphaFold
  screens, PAN-GO and CAFA.
- **"To our knowledge" claim:** softened, with Rahman 2021, Hassan 2023 and Billmann 2026 cited.
- **Contribution:** framed as an evaluation standard at the end of the Introduction. Future work proposes applying the
  same design to the other sources.

**M6. The primary endpoint is mismatched to what co-essentiality predicts (SHOULD).**

- Done:
  - **V1:** precision 0.182 is now in the Abstract and the Discussion opening.
  - **Endpoint:** the Discussion states that the low headline is partly a property of the endpoint.
  - **Literature-based precision:** among N1 genes, 16/31 in the top 40 (52%) and 1/11 in extra30. This is reported as a
    direct, curation-independent accuracy estimate (Results C4).
- Precision@1 by module family (not done, rebuttal): 552 of the 775 H genes with a prediction fall in the "other" family
  (stated in Results C2), so per-family estimates for the remaining families would rest on 10–111 genes and 0–5 hits.
- Fig 2A was not redrawn.

**M7. The blinded judging test is easy, and judged by the same model family (SHOULD).**

- Done:
  - **Term-only support:** reported beside the primary result in the Abstract ("16 on the GO term alone") and in Results
    C4, with sign-flip p = 7.1 × 10⁻⁴.
  - **"Easy" decoy design:** acknowledged in Results C4 and Limitations.
  - **Wording:** "blinded literature concordance" replaces "stringent validation".
- Not done:
  - Within-gene decoys would need a new blinded judging round (new packets, new judges, a new validation set). That is
    beyond a text revision, and it is named as the needed test.
  - Human expert scoring cannot be supplied by the AI agents. It is listed as a limitation and needs a human
    contributor.

**M8. Unexplained failures of the named controls (SHOULD).** Done.

- **Results C2 ("Named controls"):**
  - INTS15: of 11 new terms, 8 were not reportable (fewer than two neighbours annotated at t0) and 3 were outside the
    window. The network itself was correct (Integrator partners; snRNA terms).
  - TMEM41B: 16 of 17 new terms were not reportable.
- The Fig 2 legend points to the text. The Discussion ("Context, direction and vocabulary") draws the lesson.
- All controls are classified in `results/revision/a8_control_target_reasons.tsv`.

**M9. Candidate section and Table 3 (MUST for the text; SHOULD for the analyses).**

- Text items (MUST), all done:
  - **Abstract:** no longer headlines INAFM1. It names only PLEKHH3, as the one report gene without precedent.
  - **Section heading:** "three rediscoveries, one partial rediscovery and five independent hypotheses".
  - **Table 3:**
    - slimmed to gene, prediction, partners, evidence strength (physical class separated), prior catalogues, main caveat
      and status;
    - the experiments moved to S10 Table;
    - the cell-line controls were updated to the post-red-team replacements (PK-45H for the organoid PANFR0344_T1;
      SCC-4 for SNU-46).
  - **CCDC71L:**
    - the text and S10 Table say that the PxVxL/HP1 IP-MS tests the interaction-derived hypothesis, because HP1 genes
      are not co-dependent (r −0.105 to −0.010);
    - a Polycomb readout (H2AK119ub/H3K27me3) was added;
    - Wainberg's prior H3K27-methyltransferase prediction is stated.
  - **ANKRD52:** the text and S10 Table state that the prior favours failure of the fitness rescue.
  - **C5orf34:**
    - the main text now gives the second-order signal (B-view z 23.8 vs F-view 2.4; raw r with SPICE1 0.06);
    - it notes that GLS gives a different term;
    - it adds the module-homogenisation alternative.
  - **TRAPPC5:** the caveat is added.
  - **PLEKHH3:** the existing partial correlations (0.257/0.298) and the lymphoid absence are reported. S10 Table adds the
    co-advantage readout.
- Analyses on DepMap (SHOULD), not done:
  - C5orf34 module coherence in TP53-WT lines;
  - TRAPPC1/3/4 TRAPPIII leaning;
  - PLEKHH3 lineage-adjusted partial correlations and PTEN-null exclusion.
  - Each needs new matrix computations and report revision. Each is named in the text as untested and listed in S10
    Table as the first step.

**M10. Robustness checks that cannot discriminate (SHOULD).**

- DEMETER2: Results C3 now states that the check was never validated on positive controls. The S20 genes have no p_cal
  and were never scored, so the proposed validation is not possible without new computation; the flag should not be read
  as evidence against a prediction. Limitations repeat this.
- Physical class: Results C3 now calls it the most informative orthogonal readout, and Table 3 reports it separately.
  Fig 4 was not redrawn.

### Minor concerns (Referee 1)

1. **Length; notation.** Partly done.
   - Done: notation table added (Table 4, Methods).
   - Not done: the safeguard and deviation narratives stay in the main text. Referee 2 and the reproducibility audit
     asked for more precision there, not less. The manuscript is about 19,000 words including tables.
2. **Unreachable tiers.** Done. A design lesson is added in the Discussion ("Co-essentiality as calibrated,
   complementary evidence").
3. **Fig 5B top extra30 bin.** Done. MARF1 (contradiction) and TMEM60 (artefact exclusion) explain the overlap with the
   top-40 range (Results C4 and the Fig 5 legend).
4. **Table 2.** Done. p_cal and zavg are now in separate columns, with UniProt score and Complex Portal flag per row.
5. **Prior-only comparator.** Partly done.
   - Done: Results C2 explains the degeneracy (top terms of size 200, never new) and says that the IUT was effectively
     decided by the matched null.
   - Not done: a frequency-weighted random null was not added, because it would be another look at H outcomes.
6. **Fig 2E reasons.** Partly done. The reasons are in Results C2, and the legend points to them; the figure was not
   redrawn.
7. **Figs 1C and 3D.** Not done. Flags are shown in S4A Fig and Table 2 instead.
8. **Authorship (MUST).** Done as far as AI agents can.
   - Added: a PLOS-style "Use of AI tools and author contributions" section, the statement that AI tools cannot be
     authors, a human-oversight placeholder, CRediT and Funding placeholders, and a corresponding-author placeholder.
   - A human must fill these in.
9. **"Stringent form of validation."** Done. Replaced by "blinded literature concordance" (Discussion and C4 heading).
10. **Co-advantage.** Done. Defined in the Introduction.

---

## Referee 2 (statistics), `ms_round1_referee_stats.md`

**M1. p_cal and Σp_cal are conditional on the gene being annotated.** Done.

- **Definition:** p_cal is defined as conditional in:
  - Table 4;
  - Methods (hold-out set), with a note that DESIGN §3.7's wording is corrected in interpretation and the model is
    unchanged;
  - Results C3;
  - the Discussion and Limitations.
- **Rescaled figures [post-review exploratory]:**
  - conditioning rate 775/4,822 = 0.161;
  - unconditional Σ ≈ 4.9 (2.2–8.1);
  - signal-adjusted 5.1 (2.4–8.3);
  - top 40 ≈ 0.40.
- **Interval:** described as an interval for the expectation. The Poisson-binomial SD of about 5.5 is added.
- DESIGN.md itself is frozen and was not edited.

**M2. "No pre-registered gene exceeded p_cal 0.141."** Done. Now "no in-support gene" (Abstract wording removed;
Results C3: "No in-support U gene...", noting the 1,421 genes without p_cal).

**M3. "Calibration was adequate" overstates.** Done. See Referee 1 M3.

- **Abstract:** "not detectably poor but rested on 24 events (slope 0.82, 95% CI 0.51–1.13)".
- **Results:** c CI, bootstrap CIs beside Wald, and slope and c without the signalling family.
- The clipping-induced leverage is addressed by the no-signalling sensitivity.

**M4. Module-label crediting is an unlogged operationalisation.** Done.

- **Deviation log:** DEVIATIONS row dated 2026-10-31 (retrospective; added before this revision).
- **Results C4:** the operationalisation is described, and the primary is labelled "[pre-specified; scoring
  operationalised]".
- **Term-only test:** 16/40, p = 7.1 × 10⁻⁴, in the Abstract and Results. All six supported decoys were term-based.
- **Methods (Judging):** states that the rule was logged after review.

**M5. "69 of 100" in the Discussion.** Done. Now 59/90, explicitly not a prevalence; only the random-50 audit (42%) is
described as a prevalence (Discussion, Results C4).

**M6. The union is an oracle.** Done.

- The union is labelled an oracle upper bound (Results C2 complementarity; Discussion).
- The deployable rule is reported: 0.224 (0.190–0.259), +0.006 (+0.001 to +0.012).
- It is in the Abstract ("adding co-essentiality where homology made no prediction gained 0.006").

**M7. "The expression requirement carries the specificity."** Done.

- The sentence is replaced: "The reproducibility null is anti-conservative, so 646 is an upper bound".
- Null-adjusted bound: 392 expected null calls of 635, 243 (173–306), 4.9% of U. Design definition: 241. By SD tertile:
  269–271.
- In the Abstract and S4C Fig.

**M8. Inferential tests labelled [descriptive].** Done.

- Relabelled "[exploratory; post hoc, unadjusted]":
  - Fisher 18/40 vs 1/30;
  - Fisher N1 16/31 vs 1/11;
  - McNemar (Results C3).
- The "fame" sentence is softened in Results and the Discussion ("suggests ... rests on one exploratory test with 11
  N1 genes").
- These tests do not touch H, so no LOOKS.md row was added. LOOKS.md is the H one-look log. They are listed here and
  labelled in the text.

**S1. κ measures reproducibility, not validity.** Done.

- κ is called "between-instance agreement" (C4 validation and agreement paragraphs).
- Models are named: J1/J2 Claude Sonnet 5.5; adjudicator Claude Opus 5.5 (Methods and Results; `docs/AGENT_PROMPTS.md`).
- The sparse `agent_runs.tsv` is stated (Methods, Reproducibility).
- "Stringent" is dropped.

**S2. Slot-permutation and module-clustered tests.** Done.

- Slot permutation: p = 2.3 × 10⁻⁷ (term-only 2.6 × 10⁻⁶).
- V1′-clustered sign-flip: p = 0.0022, 17 clusters (term-only 0.0058).
- Both in Results C4.

**S3. The prior-only arm is degenerate.** Done. Results C2 qualifies "beats both nulls", and the Discussion opening says
the method "beat a profile-matched null (the prior-only arm was degenerate at rank 1)".

**S4. Abstract omissions.** Done. The U-reweighted 0.012 and the GLS parity are both in the Abstract. The Discussion
adds "about one gene in 80" for U-like genes.

**S5. Σp_cal sensitivities.**

- (a) Done. The 403 signalling genes contribute 0.00004, and up to 10.7 at the upper bound (Results C3).
- (b) Partly done.
  - Done: expressed in-support Σp_cal = 20.0 is reported.
  - Not done: the H hit rate by expression status is not reported.
- (c) Not done. Recalibrating the top-40 p_cal with the out-of-fold slope needs the joint recalibration intercept from
  the OOF predictions on H. That would be a new look at H outcomes not covered by the logged post-review row. The
  conditional-to-unconditional rescaling (0.40) and the decile over-prediction (0.170 vs 0.115, already in Results) are
  reported instead.

**S6. Dependence in C2 (leave-one-module-out).** Not done; added as a limitation (Limitations: "Confidence intervals use
PMID-only clusters ... we did not run a leave-one-module-out sensitivity on H"). It would be a further look at H. The
module-clustered judging test (S2) addresses the parallel concern for C4.

**S7. Deviation impact on C4.**

- Done:
  - The Methods deviations paragraph states that only the pure-p_cal top 40 was judged, although DEVIATIONS promised
    "both rules", and that the lists share 20 genes.
  - Dropping the relationship type is stated to make statements less falsifiable and easier to support (Results C4).
- Not done: support among the 20 shared genes is not tabulated.

**S8. Explain the gap between endpoints.** Done. Results C4 states that 18 (or 16) supported statements sit beside
Σp_cal 2.50 (about 0.4 unconditionally), and that this gap measures how much more lenient literature concordance is
than exact-term curation.

**COULD items.**

- C1. Human re-scoring: not done (needs a human).
- C2. Negative-control bound over the 708 in-support genes: not changed. The frozen negative-control definition uses all
  scorable clean negatives. We agree the 708-gene bound (0.0042) is the more natural denominator; the text already calls
  the zero rate uninformative.
- C3. Literature depth of N1 genes, top 40 vs extra30: not done.
- C4. Logistic regression of support on p_cal: not done. The C4 test remains dichotomised and is labelled exploratory.
- C5. p_cal of report genes named in the Abstract: done in effect. The Abstract now names only PLEKHH3, and Table 3 gives
  every report gene's p_cal.

**Label and number audit.** All four mislabels and the five Abstract/Discussion numbers are corrected as above.

---

## Numbers review, `ms_round1_numbers.md`

**Discrepancies (section 3).**

1. **"9 genes lost all their targets".** Done. Methods (Circularity) now reads: 11 under the primary rule (`core.md`) and
   9 under the fully-circular definition (`circularity_summary.md`). Results C2 gives "11 genes lost every target".
2. **704 compared with 646.** Done. "704 assessable genes, against 635 with set overlap on the same (frozen) expression
   column" (Results C1).
3. **"Within about eight years" tag.** Done. Now tagged `config/frozen.yaml` (Results C3).
4. **"≥ 1% of lines below −0.5" tag.** Done. Tagged `preregistration/CRITERIA.md`.
5. **Table 3 trailing comment.** Done.
   - `reports/<GENE>.md` is replaced by the ten real report paths.
   - `ADJ_main2.tsv` is added for packet-level verdicts (WDR7/J040).
   - The judge-file tags in Results C4 now list J1, J2 and ADJ files.
   - The red-team tag lists the ten real files.

**Process statement (CLAIMS.tsv).** Done. The Methods (Claim tracing) and Data availability now point to the
auto-generated `results/revision/CLAIMS_preview.tsv` (`scripts/91_claims_from_manuscript.py`) and state that the
hand-written CLAIMS.tsv held six claims. The PI still needs to move the preview to `CLAIMS.tsv`.

**Untagged numbers (section 4), all six places.** Done.

- PLEKHH3 (18,433; r 0.424/0.400; PIK3CA −0.186): tagged `reports/PLEKHH3.md (§0)`.
- "(top-K mean 5.4–15.5)": the tag is moved after the parenthesis.
- Fig 2 legend Q1 range: tagged `fig_signal_quintiles.tsv`.
- S2 Fig legend 10,303: tagged `FigS2a_R_by_set.tsv`.
- "(13.1%)": moved inside the tagged sentence.
- "1.2% per gene": tagged `pcal_summary.json`.

**Source-to-source observations.** No manuscript change was needed. Mean R(g) 0.078 is still described as all 820 H
genes.

**Re-check after revision.** `verify/check_manuscript_numbers.py` was re-run on the revised assembly.

- 1,260 tagged numbers: 1,178 screening hits and 82 misses.
- All new misses were inspected. They are rounding of non-integer source values (for example 243.218 → 243), interval
  ends, and restatements tagged with a summary file. Values held only in `results/revision/numbers_a3.json` and
  `numbers_a4.json` are now tagged with those files.
- No value disagrees with its file.
- One untracked cited file is `source_data/FigS4_derived_numbers.tsv`; it is new and not committed.

---

## Reference review, `ms_round1_references.md`

1. **Ref 54 (Fischer 2025) pages.** Done. Now 21(7):911–943 (`references/old_meta.tsv`).
2. **BaCoN [Rohde2025].** Done. The citation is repurposed: "related balancing of correlation networks has been
   developed for predicting gene buffering" (Introduction).
3. **[62,63] coverage vs quality.** Done. Feuermann 2025 is cited for coverage and Škunca 2012 for reliability by
   evidence source (Discussion, "Published functions ...").
4. **TAS/IC.** Done. Methods D1 states that the GO guide classes TAS and IC as author or curator statements, that we
   count them deliberately, and how "experimental" is used in the text.
5. **Holm 1979.** Done. Added as the primary Holm reference (Methods, support test).
   - The paper has no DOI: Crossref returns 404 for 10.2307/4615733, and doi.org has no such handle.
   - It is cited by its JSTOR stable URL, https://www.jstor.org/stable/4615733.
   - The record (Holm S, *Scand J Stat* 1979;6(2):65–70) was verified via OpenAlex W2121044470.
   - The assembler prints "Available from: URL" for DOI-less journal records.
6. **Shui 2023 Fig S5C; TBC1D31/WDR67.** Done. "(Fig S5C of [Shui2023])" and "TBC1D31 (alias WDR67)" (candidate-report
   section).

**Spot-check items.**

- #24 (Billmann 2026): reworded. The flat-profile sentence no longer cites it, and it is now cited for the comparison of
  genetic-interaction maps with co-essentiality (Introduction).
- #15 ([33] as a looser fit for normalisation): left unchanged.

---

## Reproducibility audit, `ms_round1_reproducibility.md`

**M1. Deposit the repository and push tags.**

- Done in text: Data availability now states:
  - deposition with history and tags on acceptance, with a placeholder DOI (10.5281/zenodo.XXXXXXX);
  - freeze commit afed1dd and the tags;
  - the FREEZE.sha256 hash 687075e680b8a051e6482de5bb052c903afaf2942ae5a25a34cef79e5965da04;
  - that git times are self-reported until deposition.
  - Methods (Hash gate) repeats this.
- Not done: the deposit itself and the tag push need a human with an account; there is no remote.

**M2. "Each deviation logged before its result" is false.** Done.

- Methods (Deviations) now lists the four retrospective rows: the R1 tie-break, the 646/635 expression rule, the
  top-40 fill reading and the module-label crediting.
- It states that row dates are non-monotone and that commits give the order.
- The Discussion ("... and what they did not") and the front-matter label definition were also corrected.
- The count is now 22 (21 + the 2026-10-31 row).

**M3. Root README.** Already present (commit c35d171); updated in this revision.

- Prompts paragraph now points to `docs/AGENT_PROMPTS.md`.
- Run-order rows added for 62, 90 and 91.
- Rebuild instructions now include `62_figS4.py`.
- The Methods and Data availability point to README for the run order.

**M4. "Fresh agents ran audit_order."** Text done; audit not done.

- Done: the Methods (Chronology audit) now says the milestone analyst agents ran it, that the globs miss
  `holdout_eval` and `ledger` (checked by hand during review), and that no final-milestone audit is committed.
- Not done: extending the globs and committing an M9 audit. That is a code and audit task for the PI; nothing is
  committed in this revision.

**M5. Soften the scopes claim; agent_runs; prompts.** Done.

- Methods "Agent scopes and prompts":
  - the scopes file is a template;
  - `agent_runs.tsv` has one row;
  - temperatures and seeds were not recorded;
  - prompts are verbatim in `docs/AGENT_PROMPTS.md`;
  - blinding can be audited only from the prompts, packet code and leak check.
- `agent_runs.tsv` was not back-filled, because the runs cannot be reconstructed reliably.

**M6. "Predictomes, HumanNet reported only".** Done. HumanNet is removed ("not obtained or used"). Predictomes and hu.MAP
are described accurately: never used as support; used after review only for the novelty check (Methods, Discussion).

**S1. DATA.md: DepMap URLs and DOIs, HGNC date, unused files, licences.** Not done. Data documentation is outside the
manuscript text. The revision downloads are documented in `results/revision/external_manifest.tsv` (DATA.md-ready).

**S2. Mention the verification re-run and exploratory look next to "one look".** Done (Methods, One-look rule).

**S3. Portable build script and lock file.** Not done. `PANDOC` and `CHROME` environment overrides already exist; README
documents the non-portable lock lines.

**S4. CLAIMS.tsv.** Done. See the numbers review above.

**S5. Seeds.** Documented, not changed. The Methods state that several scripts hard-code seed 0 and that the tool's
internal seed is fixed inside the tool. Model IDs per role are documented in `docs/AGENT_PROMPTS.md`.

**C1–C3.** Not done:

- refresh of `sparse_check.txt`;
- a note that L quotes are short abstract extracts (already in README);
- writing the `check_data.sh` output.

---

## Summary of what remains for a human or a later round

1. Authors, affiliations, corresponding author, the human-oversight statement, CRediT roles and funding.
2. Repository deposition (DOI), tag push, and moving `CLAIMS_preview.tsv` to `CLAIMS.tsv`.
3. Human expert scoring of the judged packets.
4. New computations that would be new looks at H or new matrix work:
   - within-gene decoys (new judging round);
   - leave-one-module-out on H;
   - top-40 recalibration;
   - DepMap controls for C5orf34, TRAPPC5 and PLEKHH3;
   - DEMETER2 validation on S20;
   - per-family precision.
5. DATA.md completion, build portability, and the audit_order glob extension with an M9 audit.
