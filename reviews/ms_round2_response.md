# Response to reviewers, manuscript round 2

Manuscript: *A pre-registered, temporally validated evaluation of co-essentiality function predictions for
uncharacterised human genes: modest accuracy, narrow reach and many already-published functions.*

We thank both referees and the number auditor. Every numbered item is answered below. "Done" names the change and where
it is; "Not done" gives the reason. Section names refer to `manuscript/src/*.md`, which are rebuilt into
`manuscript/manuscript.md`, `.docx` and `.pdf` by `scripts/79_assemble_manuscript.py` and
`scripts/80_build_manuscript.sh`. Material moved out of the Results is in the new S1 Text
(`manuscript/supplementary/S1_Text.md`).

## Ground rules for this revision

- **No pre-specified result was changed.** The following are unchanged:
  - the IUT and its CIs;
  - the calibration table;
  - Σp_cal 30.5 (13.8–49.7);
  - the judged primary result (18/40 vs 3/120, p = 2.2 × 10⁻⁴);
  - the census (646 / 635).
- **No H outcome was read.** The only new computation is `scripts/92_round2_numbers.py`, which reads U-side
  assessability, the top-40 lists and the judging files. It writes `results/revision/a10_round2_numbers.tsv` and
  `a10_assessability_excess_and_implied.tsv`; the Methods call it A10. Every other number is already in
  `results/revision/` or is arithmetic on reported values.
- **Renumbering.**
  - Table 2 (the rediscovery list) is now Table A in S1 Text.
  - The candidate-report table is now Table 2, and the notation table is now Table 3.
  - S1 Text is the new supplementary results.
  - The frozen design is now S2 Text, and the responses and prompts are now S3 Text.
- **Not committed.**

---

## Referee 1 (functional genomics), `ms_round2_referee_domain.md`

### New problems

**N1. The curation-lag decomposition over-attributes to complex membership.** Done. See MUST 1 and 2.

**N2. Residual overstatement.** Done.
- C2 heading: changed (MUST 3).
- Author summary: changed (MUST 4).
- "Five independent hypotheses": the heading now reads "… and five hypotheses, four of them previously proposed".

**N3. DEMETER2 inconsistency.** Done.
- DEMETER2 is removed from the "Main caveat" cells of Table 2 (formerly Table 3) for RBM34, TM2D2 and C5orf34.
- The table caption and legend now say that DEMETER2 non-replication is omitted as an unvalidated check.
- The flag is still reported in Fig 4 and S1 Text.

**N4. Revision narration in Results.** Done.
- The following passages were removed from the Results: "our first draft read it unconditionally", "After seeing the
  primary results" and "After peer review, each report gained …".
- The history is now in Methods, in two places:
  - a new "Revision history" paragraph under "Post-review exploratory analyses";
  - one sentence in the "Hold-out set" paragraph.

### MUST

**1. Results C1 wording.** Done, using your text.
- The paragraph is renamed "Curation lag and the definition of 'uncharacterised' [post-review exploratory]".
- It now states that:
  - 13 of 21 N1 genes rest on evidence from 2021 or later;
  - the other 8 rest on older evidence, and 6 of them are flagged, 5 by UniProt score 5;
  - none is a Complex Portal subunit;
  - literature-route genes were N1 more often: 19/34 vs 2/16 (56% vs 13%, 3–36%);
  - flagged genes were N1 more often than unflagged genes: 13/22 vs 8/28;
  - with the cellular-component part of the flag restricted to complex terms (165 U genes), the contrast is 10/18 vs
    11/32 (p = 0.23);
  - among selected candidates, definition artefacts dominate (30/40 and 20/20 flagged; 13 and 17 Complex Portal
    subunits).
- The paragraph also says that the broad flag counts localisation-only CC annotations.
- It closes with: "In the random sample, then, most of the gap is recent work not yet curated and the rest is older
  work that the definition could not see; complex membership accounts for it only among the top candidates."
- Sources: `a1_U_entry_flags.tsv`, `a1_N1_rates_by_route_and_flag.tsv` and `a1_flag_counts.tsv`.

**2. The same correction elsewhere.** Done.
- **Discussion:** the paragraph now opens "Part of this, and most of it among top candidates, is not slow curation but a
  property of our definition". The evidence sentences repeat the 13/21 split and contrast it with the top 40 (30 flagged,
  13 Complex Portal subunits). The claim "complex subunits described in multi-subunit papers entered U" now reads "genes
  studied mainly in multi-gene papers entered U".
- **Abstract conclusion and Author summary:** both now read "miss genes studied mainly in multi-gene papers, including,
  among our top candidates, many complex subunits".

**3. C2 heading.** Done. The heading is now "C2: co-essentiality beats a matched-gene null on a temporal hold-out, with
low absolute accuracy".

**4. Author summary, "has been little studied".** Done. It now reads "… and was classed as little studied by our
literature criterion; many such genes in fact have published functions."

**5. Placeholders.** Not done; they cannot be completed by the AI agents that prepared this revision.
- Placeholders now marked "[… to be completed by the human authors]":
  - authorship, affiliations and ORCID iDs;
  - the human-oversight line;
  - the corresponding author;
  - the oversight and accountability statement;
  - CRediT;
  - acknowledgements and funding;
  - the archival DOI.
- The earlier provisional name in the oversight line was removed, because nobody has confirmed it.

### SHOULD

**1. Cut the Results; move Table 2 to Supporting Information.** Done.
- The Results fell from about 8.9k words (text plus tables) to about 5.4k: 4.8k of text plus 0.6k for Table 2.
- We followed your plan:
  - **Tool reproduction:** two sentences.
  - **C1:** strata reduced to one sentence plus Fig 1C. The rank-biased-overlap result moved to S1 Text.
  - **C2:**
    - robustness reduced to one sentence;
    - calibration about 250 words, with separation, the bootstrap and the simpler models in S1 Text and S4D Fig;
    - named controls about 150 words;
    - complementarity shortened.
  - **C3:** "Other sensitivities", the clean-negative false calls, the artefact flags, the orthogonal-support detail and
    the top-40 checks moved to S1 Text, each with a one-sentence summary. The summaries are in "Controls for the
    catalogue" and "Top 40".
  - **C4:**
    - the recall probe is merged with the literature screen;
    - judge validation is merged with agreement;
    - the module-crediting mechanics are in Methods (A5) and S1 Text;
    - Table 2 is now Table A in S1 Text.
  - **Candidate reports:** about 700 words, covering the rediscoveries in brief plus PLEKHH3 and C5orf34. The rest is in
    S1 Text section F and S1–S10 Reports.
  - **Discussion:**
    - the AI-safeguards section is halved (about 330 → 170 words);
    - "Circularity" is merged into "Context, direction, vocabulary and circularity".
- Every moved number keeps its source tag.

**2. Candidate heading.** Done: "Ten candidate reports: three rediscoveries, one partial rediscovery and five hypotheses,
four of them previously proposed".

**3. DepMap-only checks for PLEKHH3 and C5orf34.** Not run. We applied your fallback wording.
- **Abstract:** PLEKHH3 is now "a low-amplitude co-advantage signal not yet controlled for lineage".
- **Results:** state that lineage-adjusted and PTEN-null-excluded partial correlations were not run. For C5orf34, they
  state that the centriole-module coherence check in TP53-wild-type lines was not run, so the TP53 condition is "an
  observation to be tested". The phrase "What is new is the condition" is removed.
- **Table 2:**
  - PLEKHH3 status is now "hypothesis (no precedent found)", with the caveat "not yet controlled for lineage or PTEN-null
    lines";
  - C5orf34 status is now "TP53 condition untested".
- **Limitations and Future work:** both list the two checks as not run.
- We did not run the checks in this round, because the brief for this revision allowed text changes and U-side
  arithmetic only. They need no hold-out data and are the first step the Future work names.

**4. DEMETER2 in Table 3.** Done (N3).

**5. Revision narration.** Done (N4).

---

## Referee 2 (statistics), `ms_round2_referee_stats.md`

### MUST

**M1. Unconditional wording.** Done, using your text, in three places:
- the C3 "Σp_cal [pre-specified headline]" paragraph;
- the Fig 3B legend, which also gives the 4.9 [post-review exploratory] figure;
- the Introduction's C3 bullet ("that would be confirmed if every gene gained new experimental annotation (a
  conditional quantity)").

The Top-40 paragraph and C4 now say "would be confirmed if every gene were later annotated".

**M2. Abstract 4.9.** Done. The Abstract now reads "about 4.9 (2.2–8.1) if the 2018 cohort's annotation rate applies
[post-review exploratory]". The Results and Discussion carry the same assumption.

**M3. Top-40 unconditional figure.** Done.
- C3 ("Top 40") now reads "about 0.4–0.6 (signal-adjusted 0.64, 0.32–1.02)" and adds "with 31 of these genes already
  published (C4), their rate is probably higher still".
- C4 (the secondary-sets paragraph, where the 2.50 point sum and the endpoint-gap sentence now sit) gives the same
  range.
- Source: `numbers_a3.json`, `a3_gain_rate_by_signal_quintile.tsv`.

**M4. The null-adjusted census is an excess of calls, not a count.** Done.
- **Abstract:** "calls exceed the null expectation by about 243; under that assumption at least about 320 genes (6.6%)
  carry real signal [post-review exploratory]".
- **C1:** "leaving an excess of 243 (173–306) calls, 4.9% (3.5–6.2%) of U, over the null expectation … at full power it
  implies at least about 324 (248–389) genes, 6.6% of U, with real reproducible signal, and more at lower power … This is
  a lower bound under an untested assumption."
- **Discussion:** "the calls exceed the null by one gene in twenty, implying at least one in fifteen with real signal".
- **S4C Fig legend:** describes the bar as the excess.
- **Methods A6** gives the identity observed = Tπ + (N − T)α, and **S1 Text B** sets out both quantities.
- **New values:** the full-power lower bound and its interval come from the new `a10_assessability_excess_and_implied.tsv`:
  - 324 (248–389) by any-dependency class;
  - 325 (251–387) by SD tertile;
  - the intervals use the same Jeffreys-Beta and binomial draw scheme, divided by (1 − α) per stratum.
- **Partly done (renaming the column):**
  - We did not rename `implied_true` inside `a6_assessability_null_adjusted.tsv`. That file is generated by
    `scripts/90_revision_analyses.py`, which also reads H outcomes for other analyses. Re-running it would be a new look,
    and editing its output by hand would break the script–file correspondence.
  - The new `a10` file carries both quantities under correct names (`excess_calls_over_null`,
    `implied_true_full_power`).
  - Methods A6 and S1 Text state that `implied_true` in `a6` is the excess.

**M5. "Logged before they were run" is unverifiable.** Done, using your text.
- **Methods ("Post-review exploratory analyses"):** "were logged in LOOKS.md; the row was committed together with the
  results (b39691d), so the order rests on the agents' record, as for the primary look".
- **"One-look rule" bullet:** only the specification row (fa21808) demonstrably preceded the primary look (aa381fc), by
  31 minutes. The rows for the primary look, the verification re-run, the exploratory look and the post-review analyses
  were each committed with their results (`reviews/audit_order_M9.md`).
- **Front-matter comment:** no longer says "logged … before".
- **Round-1 letter:** we leave `ms_round1_response.md` unchanged as a historical record. This letter supersedes its
  sentence "were logged in LOOKS.md (row dated 2026-10-30) before they ran".

### SHOULD

**S1. Rescaling identity and assumptions.** Done in Methods A3.
- **Identity:** E[unconditional confirmations] = Σ p_i r_i, exact because confirmation requires annotation.
- **The three assumptions behind one r:**
  - the gain rate does not vary with p_cal (shown false for signal);
  - the 2018 rate transfers to genes still uncharacterised in 2026;
  - p_cal transfers to U.
- **Added values:**
  - the survivor-hazard version, 30.5 × 0.145 ≈ 4.4, reported beside 4.9 in C3 and Methods;
  - the unconditional Poisson-binomial SD of about 2.2.
- **Partly done:** the misworded assumption (2) in `a3_pcal_conditional.md` is a script-generated file, so Methods
  states that it is superseded rather than editing it.

**S2. "[post-review]" undefined.** Done.
- [post-review exploratory] is used for every analysis.
- [post-review] alone is defined once, in the Results label paragraph, the front comment and the S1 Text header, as "a
  table column or report statement added after peer review that is not itself an analysis".
- The remaining [post-review] uses are table columns (UniProt score/CP, prior catalogues) and the notation row.

**S3. Calibration wording.** Done.
- **Results:** "Models with one or two covariates calibrate comparably (slopes 0.93 and 0.89, with intervals
  overlapping the frozen model's; c 0.835 vs 0.855)".
- **Discussion:** "simpler models calibrate comparably (S4D Fig), so the data cannot say whether the frozen model is
  over-parameterised".
- **S1 Text:** says that overlapping intervals cannot separate the two explanations.

**S4. N1 accuracy CI and scope.** Done. C4 now reads "Among top-40 genes with published function, selected on p_cal,
the predicted function matched the published one for 16 of 31 (52%, Wilson 95% CI 35–68%); on the GO term alone it
matched for 14 of 31 (45%), because YPEL5 and DPCD are N1 genes supported on the module label only". It adds "a
curation-independent estimate of accuracy within that selected group, on a lenient endpoint". Source:
`a10_round2_numbers.tsv`.

**S5. Shared genes with the clean-first list.** Done, in S1 Text D ("Clean-first list"). Of the 20 shared genes, 12 were
supported (11 on the term), against 6 of the 20 that were not shared (5 on the term). Source: `a10_round2_numbers.tsv`.
The Results keep the one-sentence pointer.

**S6. DEVIATIONS row dated after its commit.** Partly done.
- **What happened:** the row was committed in acdad5a with the date 2026-10-31. Commit 090a7d8, made before this
  review arrived, then corrected that date in place. This went against the append-only convention.
- **Done:** the Methods now refer to the row by commit: "logged retrospectively during manuscript review in commit
  acdad5a; the row's date was first written as a later day and corrected in place in commit 090a7d8, so the commit, not
  the date, records when it was logged."
- **Not done:** we did not append an erratum row to `DEVIATIONS.md`. That file sits outside the manuscript tree, and a
  new row would change the count of 22 rows cited throughout. We recommend that the human authors add a "record note
  (not a deviation)" row at deposition.

### Label audit

- "[post-review]" is now defined (S2).
- The Abstract 4.9 is now labelled (M2).
- "Remain" is replaced by "excess" (M4).
- The 0.4 gap is now 0.4–0.6 with the signal-adjusted value (M3).
- "At least as well" is now "comparably" (S3).
- "Logged before they were run" is removed (M5).

---

## Number audit, `ms_round2_numbers.md`

- **A1:** done. The Wilson interval is now "3–36%" (C1).
- **A2:** done. The oracle union is now quoted with the cluster bootstrap, "0.236 (cluster bootstrap 0.202–0.272)"
  (source `a7_combination_rules.tsv`). The gene-level interval is reported, labelled as such, in S1 Text. The Discussion
  quotes the point value only.
- **A3:** done. The Discussion now reads "about one gene in 83".
- **A4:** done. The Methods "Chronology audit" bullet now states:
  - the globs covered the prediction ledger from the first commit, but the M6 audit ran before the ledger existed;
  - they did not cover the hold-out, M7 or post-review outputs;
  - during revision they were extended, and an independent agent ran the audit on all four directories
    (`reviews/audit_order_M9.md`: PASS).
- **"[post-review]" label:** defined once (S2 above).
- **R1–R3 (REPORT.md):** fixed in commit ed9a54b; no manuscript change.

---

## Verification after this revision

- **`verify/check_manuscript_numbers.py`** on the rebuilt manuscript reports:
  - 837 tagged numbers: 773 screening hits and 64 misses;
  - no unresolvable paths;
  - 239 untagged numbers, down from 249. Tags were added for the new numbers.
- **The 64 misses:**
  - 57 are carried over from the round-2 audit, where they were confirmed by hand;
  - 7 are new and were confirmed by hand:
    - 320 (Abstract) is the requested rounding of 324;
    - 324 (twice), 248 and 389 are printed from unrounded values in `a10_assessability_excess_and_implied.tsv`
      (324.29, 248.16, 388.57), and the screen requires an exact match for integers;
    - 1.02 (twice) is 1.024 in `numbers_a3.json`, where the JSON-escaped en dash (`\u2013`) defeats the screen.
- **S1 Text, run through the same extraction:** 474 tagged numbers, 445 hits and 29 misses.
  - All 29 are counts, number words or derived values moved unchanged from the round-2-confirmed Results, plus the new
    `a10` values.
- **`CLAIMS.tsv`:** regenerated from the manuscript and S1 Text by `scripts/91_claims_from_manuscript.py`.
  - It has 1,291 rows, with CLAIMS.tsv's original header kept.
  - The script gains an `--also` option (default: S1 Text) and maps `a10_` files to `scripts/92_round2_numbers.py`.
- **Length:**
  - Results are now 4.8k words of text plus 0.6k for Table 2, against 7.3k plus 1.6k before;
  - S1 Text is 3.3k words plus 1.1k for Table A;
  - the Abstract has 300 words;
  - the PDF has 36 pages, against 39 before.
