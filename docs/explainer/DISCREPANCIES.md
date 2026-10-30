# Discrepancies, open questions and judgement calls

This file lists every place where the sources for [JOURNEY.md](JOURNEY.md) and [INSIGHTS.md](INSIGHTS.md) disagree
with each other or with the code and results, and what the explainer uses. When they disagree, the explainer trusts
committed results and git history over narrative files (RESEARCH_TREE.md, REPORT.md, LESSONS.md, retrospectives, commit
messages) and over the PI's own account of the turning points.

## A. The PI's account of the turning points vs the record

| # | PI's account | What the record shows | Used in the explainer |
|---|---|---|---|
| <a id="a1"></a>A1 | TP2: the round-1 design reviews (`3e6b162`) produced the CAFA-style temporal hold-out "instead of only leave-one-out". | The temporal hold-out was already the *primary* validation in DESIGN v1 (`f1cb5c3`/`3238906`, §3 "Temporal hold-out (primary validation)"), as recommended by LITERATURE.md §4.1. It also included a circularity blacklist and prior-only and matched-gene nulls. Round 1 hardened it: Europe PMC full-text circularity query (statistics item 8), hold-out defined by the same D1 function at t0, calibration fitted on the hold-out rather than isotonic on leave-one-out (item 12), cluster bootstrap and intersection–union test (items 4, 18), and leave-one-out restricted to ranker choice. | Literature origin, review hardening ([TP2](JOURNEY.md#tp-2)). |
| <a id="a2"></a>A2 | TP3: "only ≈ 243 genes carry signal beyond the null". | The round-2 statistics referee (M4, [reviews/ms_round2_referee_stats.md](../../reviews/ms_round2_referee_stats.md)) showed that 243 is the *excess of calls over the null expectation*, not a count of genes. Under the stated assumption, at least about 320–324 genes (6.6%) carry real signal (`results/revision/a10_assessability_excess_and_implied.tsv`). The final manuscript abstract uses this wording. RESEARCH_TREE.md (M8, M9 headline), REPORT.md §2 ("null-adjusted estimate of genes with a real, reproducible co-essentiality signal is ≈ 243"), LESSONS.md rule 5 and retro_M9 still use the superseded reading. | "Excess of about 241 calls; at least about 322 genes under an untested assumption" (646-call basis; see B13). |
| <a id="a3"></a>A3 | TP8: "9/10 report genes already had prior co-essentiality predictions (Wainberg 2021 Supp. Data 3)". | Only 3/10 (CCDC71L, C5orf34, INAFM1) appear in Wainberg 2021 Supplementary Data 3, the explicit function predictions for uncharacterised genes. 9/10 had *some* prior co-essentiality link with ≥ 1 of their top-10 partners: a GLS pair, a module at d ≥ 0.5, or a Kim 2019 edge or cluster ([results/revision/SUMMARY.md §A2](../../results/revision/SUMMARY.md); [report_novelty_corrections.md](../../results/revision/report_novelty_corrections.md)). The A2 notes say these flags "do not check that the resource assigned the same function". REPORT.md §2 ("9/10 genes already had a prior co-essentiality prediction or module") and retro_M9 §1.3 ("9/10 report genes had catalogue predictions (Wainberg 2021)") blur the same distinction. | "9/10 had a published co-essential link; 3 were explicit Wainberg 2021 predictions". |
| <a id="a4"></a>A4 | TP5: "calibration good (c 0.86)". | This rests on 24 events in 775 genes. The slope CI is 0.51–1.13 (Wald), Brier skill over a constant is about 2%, and one family coefficient (−11.86, signalling, 0/111 hits) reflects quasi-separation that inflates c. The referees had the claim reworded to "not detectably miscalibrated". | "Not detectably off … rests on 24 correct calls". |
| <a id="a5"></a>A5 | TP7: judge validation "9/10 vs 1/30". | Correct for the final adjudicated file. At commit `1eb08ea` the file and the commit message say **0/30** decoys with one disagreement unresolved. Adjudication, committed in `020b0ed`, made it 1/30. Both pass the ≤ 3/30 bar. retro_M7 writes "≤1/30". | 9/10 vs 1/30, noting adjudication in `020b0ed`. |
| <a id="a6"></a>A6 | TP2: circularity "stripped most of the famous success stories (SPRING1, SLC25A51, FIRRM)". | True for SLC25A51 (18/19 hold-out targets flagged) and FIRRM (14/15). SPRING1 was not in the hold-out at all: its new terms fell outside the 5–200 term window. In the case series (window 2–300), both of its 2 targets were flagged. | Stated separately in [TP2](JOURNEY.md#tp-2). |
| <a id="a7"></a>A7 | TP3: "non-expressed control genes passed the reproducibility test 13% of the time" found "later (stats referee, `b39691d`)". | The 13% rate was measured and reported at M4 (`0e76668`, results/assessability/summary.md; RESEARCH_TREE M4 caveat). What the referee added was applying the rate back to the expressed genes, and rejecting the sentence "the expression requirement carries the specificity". | Rate at M4, consequence at review. |
| <a id="a8"></a>A8 | Human input: "otherwise only status questions … no scientific direction". | Not verifiable: there is no session transcript in the repository. The commits are consistent with it: a usage-limit stop at `379827f`, resumption about 1 h later, and publication commits from `16de609` onward. | Stated as the PI's account. |
| <a id="a9"></a>A9 | "~60+ subagents (Opus/Sonnet)". | Not verifiable. DESIGN §9 requires every role run to be appended to `results/agent_runs.tsv`, but that file has a single row (the curation-lag audit). Model assignments for blinded roles come from docs/AGENT_PROMPTS.md only. | "About 60 by the PI's estimate; not logged". |

## B. Internal inconsistencies between project files

| # | Where | Disagreement | Resolution / note |
|---|---|---|---|
| <a id="b1"></a>B1 | Dates throughout | Git (UTC) puts every research commit between 2026-10-29 19:39 and 2026-10-30 10:26. But RESEARCH_TREE.md heads M8 "(2026-10-31)", results/revision/report_novelty_corrections.md is dated 2026-10-31, docs/AGENT_PROMPTS.md says "2026-10-29 to 2026-10-31", and a DEVIATIONS row was first dated 2026-10-31 (corrected in `090a7d8`). DEVIATIONS and LOOKS rows mix 10-29 and 10-30 for work committed on 10-29 UTC (e.g. rows committed in `0e76668` at 21:55 UTC are dated 10-30), and RESEARCH_TREE M4/M5 headings say 10-30. | The explainer uses git commit times only. The agents' clock or date reasoning was not UTC-consistent. |
| <a id="b2"></a>B2 | [LOOKS.md](../../LOOKS.md) specification row | The commit column says `47631ed` (the M5a results commit). The row itself was added in `fa21808`, committed in the same second (22:19:48). | Immaterial to the order: both precede the look `aa381fc` by 31 min. |
| <a id="b3"></a>B3 | [DEVIATIONS.md](../../DEVIATIONS.md) rows that say "set BEFORE" | (i) The M5b row ("set BEFORE any H outcome was computed") was committed in `aa381fc`, the same commit as the hold-out results. (ii) The M6 rows ("set BEFORE any U prediction was computed"; artefact flags, top-40 checks, support/tiers, fill iteration) were committed in `8e7e47f` at 23:07:36. But `results/ledger/40_manifest.json`–`43_manifest.json` show the U predictions written at 23:03:17–23:06:28. Git cannot confirm the claimed order. The final erratum row concedes late logging only for the exploratory LOOKS rows and the module-label row. | Not evidence of a violation, but the claim is unverifiable. Flagged in [INSIGHTS Eng-2](INSIGHTS.md#ins-eng-2). |
| <a id="b4"></a>B4 | DEVIATIONS row count | The file has 23 rows. The manuscript, REPORT.md, LESSONS.md and the round-2 numbers check cite 22. The 23rd (the Methods/LOOKS wording erratum) was added in `a739f06`, after the round-2 numbers check. retro_M7 counted 21 at its time. Classification also differs: "12 unspecified details" (retro_M7), "12–13 of 22" (LESSONS), "13 filled operational details" (manuscript). | The explainer says "22 post-freeze deviation entries" (the substantive ones), "about 13" filled details. |
| <a id="b5"></a>B5 | retro_M9 §2 vs DEVIATIONS erratum and audit_order_M9 | retro_M9 says later exploratory looks were "labelled … and logged first (`aa381fc`; `b39691d`)". audit_order_M9 check 5 and the final DEVIATIONS erratum say the LOOKS rows for those looks were committed *with* their results; only the specification row preceded the primary look. | The audit is followed. |
| <a id="b6"></a>B6 | RESEARCH_TREE M4 / early manuscript vs referee | "The expression requirement carries the specificity" (RESEARCH_TREE M4) does not follow from the data (round-1 stats M7). | Superseded wording. |
| <a id="b7"></a>B7 | REPORT.md §2 "646 pass the frozen assessability rule (13.1%)" | 646 applies the DESIGN §1.4 text in full (a logged deviation). The frozen list's own `expressed` column gives 635 (12.9%). | Both numbers given ([TP3](JOURNEY.md#tp-3), [E5](INSIGHTS.md#ins-eng-5)). |
| <a id="b8"></a>B8 | Assessability null on toy data | RESEARCH_TREE D2 says "toy null false-assessable 1.7%". DESIGN v2.3 §2.5 sets the acceptance at ≤ 7%, while round-1 statistics item 11 asked for 5% ± 2%. On real data the clean-negative rate was 13%. | The toy data did not predict the real anti-conservativeness; reported as such. |
| <a id="b9"></a>B9 | LITERATURE.md §3.4 vs DESIGN §1.2 (criterion D3) | The literature review recommended a *fractional* gene2pubmed count (each paper weighted 1/n genes, papers with > 50 genes dropped) below a quantile. DESIGN froze "≤ 10 focused PMIDs (papers linked to ≤ 10 human genes)". The frozen rule is the one the domain referee identified as admitting complex subunits studied in multi-gene papers. The change was made pre-freeze, so it is not a deviation, but no record explains it. | Mentioned in [TP1](JOURNEY.md#tp-1) only as the mechanism. Why the recommendation changed is an open question. |
| <a id="b10"></a>B10 | Retro_M7 "judge validation … (`1eb08ea`: 9/10 vs ≤1/30)" | See A5. | — |
| <a id="b11"></a>B11 | Manuscript Methods (per audit_order_M9 notes) said the audit globs "do not cover the hold-out and ledger outputs". The ledger glob existed, and M9 extended the globs. | Not checked whether the final manuscript text was updated. | Open. |
| <a id="b12"></a>B12 | journey_data.json gap note, JOURNEY timeline caption, C1 (before this edit) | They said script 44 "ran 03:57–04:52 (55 min)" and that the gap is unexplained. `results/ledger/44_manifest.json` records only completion (04:52:43) and `runtime_s` 3,310.5 measured with `time.perf_counter()` (`scripts/44_tiers_top40.py` line 29), which excludes macOS sleep. The PI's note (C1) says the run started before midnight and the machine slept. | journey_data.json note and the JOURNEY caption now point to C1; the code is consistent with the PI's account, which is still self-reported. |
| <a id="b13"></a>B13 | Assessable-signal excess and lower bound | The manuscript (abstract "at least about 320 (6.6%)"; Results "243 (173–306) … 324 (248–389)") and REPORT.md quote the values for the **635** calls under the frozen list's expression column. The pre-specified count everyone quotes is **646** (DESIGN definition of "expressed"), for which `results/revision/a10_assessability_excess_and_implied.tsv` gives an excess of 241 (168–306) and a full-power implied count of 322 (242–388), 6.5% of U. Earlier explainer drafts mixed the two bases. | **Fixed after review.** The explainer now uses the 646 basis everywhere (241; ≥ ~322; 6.5%) and says that the manuscript's 243/324 refer to 635 calls. |
| <a id="b14"></a>B14 | Ranker-choice gene count | JOURNEY TP4 says the ranker was chosen on "3,000 known genes"; the manuscript and `results/calibration/loo_ranker_choice.md` report 2,519 after circular targets were removed. | **Fixed after review:** JOURNEY TP4 now says "3,000 sampled known genes (2,519 kept a target …)"; METHOD.md uses 2,519. |
| <a id="b15"></a>B15 | Orthogonal-support rates | JOURNEY TP6 and INSIGHTS Meth-7 give 32% / 28% / 22% (real / matched / decoy, 247 anchors each, `results/ledger/false_support.tsv`); worked_example_notes.md gives 62.5% / 47.5% / 25% (`results/ledger/support_summary.json`, the 40 primary top-40 anchors). | Both correct for their denominators; METHOD.md states both with denominators. |
| <a id="b16"></a>B16 | Worked-example step numbering | worked_example_notes.md numbers its sections 0–7 by pipeline stage (0 pre-registration, 1 input profile, 2 scoring and neighbour list, …); METHOD.md has seven steps, and puts the neighbour list with its same-arm/paralogue exclusions in Step 4 (as the design does, DESIGN §3.1). | A mapping note was added to worked_example_notes.md; METHOD.md panel titles use the method's numbering. |
| <a id="b17"></a>B17 | Same-arm / paralogue exclusion | DESIGN §3.1 motivates it as an artefact guard; on the hold-out, removing it did not lower accuracy (0.033 without vs 0.030 with, `results/holdout_eval/SUMMARY.md`, secondary batch), and for ANKRD52 it removed a true partner (TARBP2). | Not a contradiction: the guard is justified by the synthetic proximity test, not by hold-out accuracy. Stated in METHOD.md Step 4. |
| <a id="b18"></a>B18 | Role of split-half reproducibility | Documents present R(g) as both the assessability gate and a calibration covariate. In the fitted model (`results/calibration/model_H.json`) its coefficient is 0 (shrunk to its sign bound), so R(g) does not change any p_cal. | METHOD.md describes assessability as a gate, not a confidence score. |
| <a id="b19"></a>B19 | Expected confirmations among genes with a usable signal (explainer-derived) | The manuscript gives Σp_cal over the 2,583 in-support genes (30.5 conditional; about 4.9 unconditional) and, in Results, 5.5 (2.8–8.6) over the 269 expressed, assessable genes, but never the unconditional value for those 269, nor the share of Σp_cal that comes from genes failing the usable-signal rule. From `results/ledger/pcal_summary.json` and `results/ledger/u_pcal.tsv`: 5.494 of 30.487 (18%) comes from the 269 assessable genes, so **82% comes from genes that fail Step 3**. Rescaled by the same annotation-gain rate as the manuscript's 4.9 (775/4,822 = 0.161), the 269 genes give **≈ 0.88** (≈ 0.45–1.39 from the conditional CI, ignoring uncertainty in the rate). | Derived for this explainer, not stated in the manuscript; marked as such in METHOD.md and README.md. Prompted by the explainer review (MUST 1). |

## C. Open questions (not resolvable from the repository)

1. <a id="c1"></a>**The 4.8-hour gap.** There are no commits between 23:11 (`70864b2`) and 04:55 (`c4eadf5`). Manifests show U
   predictions written at 23:03–23:06 and the top-40 checks script running 03:57–04:52 (55 min). The DEVIATIONS erratum
   mentions an earlier fill iteration in which 33/40 genes were demoted, which implies earlier, unrecorded runs of
   script 44. What happened in between (idle time, repeated runs, a stall) is not recorded in git.
   *PI note (resolved):* the computer was asleep for most of this interval. The top-40 checks were refitting the co-essentiality tool once per left-out cancer lineage (about 2–3 min each); file timestamps show 19 refits done by 23:59, then nothing until 04:13, when the machine woke and the run resumed (process CPU time ≈ 61 min over ~5 h wall clock). The earlier 33/40 demotion iteration ran inside the same script before the final fill.
   *Explainer check:* the code supports this note. Script 44's `runtime_s` (3,310 s) comes from `time.perf_counter()`,
   which on macOS does not advance while the machine sleeps, so "03:57–04:52" (completion time minus runtime) is not
   the run's wall-clock span; see B12.
2. <a id="c2"></a>**Did judge validation finish before main judging started?** Validation was committed at 05:35:46 and main judging
   at 05:38:14. Commit times cannot show that the main judges started only after validation passed, as DESIGN §6.4
   requires. The validation was also committed before adjudication was complete (A5).
3. <a id="c3"></a>**History rewrite.** `16de609` rewrote all commit hashes after scrubbing local paths. The M9 chronology audit ran
   before the rewrite (on `0cde51b`). Tags still point to `afed1dd` with the original time (checked here), and the
   hashes cited in the docs resolve. Whether *all* timestamps were preserved was not re-audited after the rewrite.
4. <a id="c4"></a>**How much of the leave-one-out vs hold-out gap (0.139 vs 0.030) is leakage and how much is population difference?**
   The record reports standardised differences between the gene sets but no matched comparison. [INSIGHTS Meth-1](INSIGHTS.md#ins-meth-1)
   marks the explanation as believed.
5. <a id="c5"></a>**Why the homology baseline is so strong.** It may partly be that curators later confirm electronically suggested
   terms (a form of circularity in the other direction). Not tested.
6. <a id="c6"></a>**The tool's hyper-parameters were tuned on hu.MAP 3.0 (Fischer 2025, doi:10.1038/s44320-025-00121-5)**, which
   post-dates the 2018 start date. The referee argued that parity with untuned Pearson bounds this leak. It is not
   measured directly.

## D. Things I was unsure mattered

- **Single-gene DepMap reads before the freeze.** PROVENANCE.md records that per-gene marginals (mean, SD, NaN fraction,
  dependency fraction, expression) were read before the freeze to build strata. The design allowed this, and no pair
  quantity was computed. The phrase "frozen before any network computation" is accurate; "before reading DepMap" would
  not be.
- **Commit timing vs work timing.** Design review rounds appear to take 12 and 8 minutes (commits 20:06 → 20:18 →
  20:31). Reviews may have run while earlier commits were being prepared, so durations in the timeline are lower bounds
  on effort, not measurements.
- **"Prior-only = 0.000" on the hold-out.** The most frequent terms are never new terms for these genes, so this null is
  degenerate (domain referee minor 5). The matched-gene null (0.005) is the informative comparator, and the explainer
  quotes it.
- **N1 counts in the top 40 (31/40).** The blind literature agent assigned these. The random-50 audit was single-scored
  with three borderline calls (38–46% under alternative readings).
- **Recall probe.** "Recognised" (52/90; 24/50 random) is a model's self-rated confidence, not a check of correctness.

## Review

An independent review of this explainer ([reviews/explainer_review.md](../../reviews/explainer_review.md); verdict:
accept after minor revision) raised 5 MUST and 12 SHOULD items. All were addressed:

- **MUST 1** ("stays silent"): METHOD, README and JOURNEY now say that every scorable gene gets a written prediction
  and that genes failing Step 3 are flagged and kept off the shortlist. The share of Σp_cal from those genes (82%) and the
  expected confirmations among the 269 assessable genes (5.5 conditional, ≈ 0.9 unconditional) are stated and marked as
  explainer-derived ([B19](#b19)).
- **MUST 2–3** (denominator, one number): the 646-call basis is used everywhere (excess ≈ 241, at least ≈ 322, 6.5%),
  including the pipeline figure, JOURNEY TP3, INSIGHTS and journey_data.json ([B13](#b13)).
- **MUST 4**: Step 3 now says plainly that the gate was never tested on the hold-out and that the evidence is indirect.
- **MUST 5**: INSIGHTS opens with a ranked half-page summary (four biological, four methodological insights); three
  narrower insights moved to a "lower-ranked" section.
- **SHOULD 6**: insight labels renamed Bio-/Meth-/Eng- (anchors `ins-bio-N`, `ins-meth-N`, `ins-eng-N`); JOURNEY TP7
  says "referee items M4 and S1"; INSIGHTS Eng-1 no longer uses milestone names.
- **SHOULD 7**: AP, c-statistic, Brier score/skill, Tdark, TPM, extra30, GLS (README), the BH family and "judging packet"
  are defined at first use or in the METHOD glossary.
- **SHOULD 8**: "paper-count route" replaced by "literature-attention route (D3: few focused papers or Tdark) without a
  low UniProt score" in METHOD, JOURNEY and INSIGHTS.
- **SHOULD 9**: JOURNEY TP4 gives 3,000 sampled vs 2,519 with a target ([B14](#b14)).
- **SHOULD 10**: the JOURNEY timeline caption gives the PI's account and its consistency with the manifest timer ([C1](#c1)).
- **SHOULD 11**: the artefact row of the "How it differs" table says the benefit was shown on synthetic data only.
- **SHOULD 12–13**: INSIGHTS Meth-1 title reworded; Bio-4 limits "only PLEKHH3" to the ten report genes and adds 6/40.
- **SHOULD 14**: source links added to Eng-7, Eng-9, Eng-11 and Eng-12; every A/B row and C item here now has an anchor.
- **SHOULD 15**: the worked-example term table shows rank 3 and notes its tie with rank 4.
- **SHOULD 16**: Dede 2020 is now cited for paralogue-buffered non-hits; DOIs added for Dempster 2021 and Fischer 2025.
- **SHOULD 17**: README describes explainer.html as METHOD, JOURNEY and INSIGHTS in one page.
- The review's optional cut candidates were not applied.
