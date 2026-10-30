# Independent review of docs/explainer/ (README, METHOD, JOURNEY, INSIGHTS, DISCREPANCIES, explainer.html)

Reviewer: independent agent (wrote none of the explainer). Date: 2026-10-30. Nothing in docs/explainer/ was edited.

## Verdict

**Accept after minor revision.** The explainer is unusually accurate and honest. I checked about 80 numbers against
results files and found no fabricated or wrong headline value. The remaining problems are presentation problems. One is
substantive: the "stays silent" framing of Step 3 does not match how the headline expected-confirmation number is
built. There is also a denominator mix-up in the assessability excess. INSIGHTS does not meet the "half a page, ruthlessly
ranked" test. The HTML is current, self-contained and has all the required widgets.

### What was checked

- **Numbers verified against their sources.** Every value below matches:
  - Headline: 4,924 / 4,271 / 19,296; 646 (13.1%); 13% and 27% false-pass rates; 2/516; 43/742.
  - Hold-out size: 820 / 5,965 / 106 / 809.
  - Hold-out precision: P@1 0.030 (0.018–0.043); null 0.005 (0.003–0.008); prior-only 0.000; GLS 0.023, Δ +0.006
    (−0.005 to +0.017); Pearson +0.002; homology 0.218 (0.184–0.253); hu.MAP 0.049; Q5 0.117 (0.067–0.174);
    Q1/Q2 0; complexes 0.182 (0.093–0.286); reweighted 0.012 (0.007–0.019); no-exclusion 0.033; combination 0.224
    (+0.006, +0.001 to +0.012); 15/24 complementary.
  - Ties and leave-one-out: 401/820 ties, 393 labels, 0.032; LOO 2,519 genes, MRR 0.169/0.140/0.111/0.073,
    P@1 0.139 → shuffled 0.015; term-size medians 131 vs 35.
  - Calibration: LOO-fitted 0.089 vs 0.031; slope 0.82 (0.51–1.13); c 0.855; Brier skill 0.021; 24 events in 775
    genes; coefficients −6.3155, 0.28504, 1.70378; −11.86 for the family with 0/111 hits.
  - Expected confirmations and novelty: Σp_cal 30.5 (13.8–49.7); unconditional 4.90 (2.23–8.05); annotation-gain rate
    820/5,051 = 16%; max p_cal 0.141; 2,583 in support; 269 → 245 eligible; 7–14/40 overlap with simpler models;
    20/40 overlap for the clean-first list.
  - Top-40 checks and support: 221/269 failed; 182/204 RNAi non-replication; orthogonal support 32/28/22% (n = 247)
    and 62.5/47.5/25% (n = 40); 11/12 sources admitted; 2,538 known complexes.
  - Judging: 18/40 vs 3/120, p = 0.000217; term-only 16/40, p = 7.1e-4; N1 31; 16 of the 18 supported genes are N1;
    S20 19/20 vs 2/60; extra30 1/30; κ = 0.975; validation 9/10 vs 1/30; recall probe 43/59 and 52/90.
  - Curation-lag audit: 42% (29–56%); 19/34 vs 2/16; 288 subunits; 1,261 with score 5; 3,819 genes; 13 recent and
    8 old N1 cases.
  - Novelty: 34/40 had a prior link; 3/10 in Supp. Data 3; 9/10 had a prior co-essential link.
  - Tool checks: AP 0.3451; 2.96e-7; 14/14; 17,525 background genes; circularity 1.8% and 71.7%; clusters 709 and
    63.5%.
  - Worked example: `reproduction_check.tsv` is 159/159; the split-half overlaps 10/10/13/13/13 give R = 0.472;
    excluded genes (TARBP2 13.42, rank 9) and term scores match the TSVs.
- **DOIs (Crossref).** All 17 DOIs I queried resolve to the cited first author, year and topic. These include Wainberg,
  Stoeger, Haynes, Rocha, Oprea, Pan, Kim, Dede, Lazar, Gillis ×2, Radivojac, Zhou, Van Calster, Rahman, Dempster and
  Fischer.
- **Links.** All relative links and anchors in the five .md files resolve. Each of TP1–8 is linked from a METHOD step,
  and each TP links back to its step(s).
- **HTML (headless Chrome, `--dump-dom` and a screenshot):**
  - Present and working: 3 tabs (Method / How we got here / Insights), a clickable pipeline (8 `data-step` stages
    bound to step anchors), 8 expandable TP `<details>` with open-all/close-all, and a worked-example viewer (8 panel
    tabs, Prev/Next).
  - It was built 10 s after the last .md edit. The text matches METHOD, JOURNEY and INSIGHTS paragraph by paragraph.
  - It has no `<link>`, `@import`, `fetch` or external `src`. All http(s) URLs are ordinary hyperlinks to the GitHub
    repo, so there are no external requests.

## Required fixes

### MUST

1. **METHOD.md first screen, "In three sentences"** (and README "In three sentences"; README step 3).
   - **Current text:** "the method stays silent when that partner list does not reproduce in two halves of the cell lines".
   - **Problem:** this is not what the pipeline does. A term is written for all 4,137 genes. p_cal is given to 2,583
     genes, and only 269 of them are assessable (M6_SUMMARY.md support table). Of the conditional Σp_cal of 30.5, only
     5.49 comes from assessable genes (`results/ledger/u_pcal.tsv`, my sum). So the headline "~4.9 expected
     confirmations over 2,583 calibrated genes" comes about 82% from genes the reader has been told the method is
     silent about.
   - **Fix:** say "flags genes whose partner list does not reproduce … and excludes them from the shortlist". In the
     Key numbers row and in Step 5, add that Σp_cal over the 269 assessable genes is 5.5 conditional, about 0.9
     unconditional (reviewer's arithmetic: 5.49 × 0.161; mark it so, or take the value from results). Keep the
     pipeline-figure footnote, which already says this correctly.
2. **METHOD.md Step 3 "What goes wrong without it"; Results table row C1; README Key results.**
   - **Current text:** "646 assessable calls exceed the null expectation by about 243 (173–306), which implies at least
     ~324 (6.6%, 248–389)".
   - **Problem:** 243 (173–307) and 324 (248–389) belong to the frozen expressed column, 635 calls. For 646 calls,
     `results/revision/a10_assessability_excess_and_implied.tsv` gives an excess of 241 (168–306) and an implied 322
     (242–388).
   - **Fix:** either attribute the numbers to "the 635 calls under the frozen expression column", or use 241/322.
3. **Harmonise "~320" and "~324"** (JOURNEY TP3 and INSIGHTS S2 vs METHOD and README; DISCREPANCIES B13 records this
   but does not fix it).
   - **Problem:** the explainer contradicts itself on the same estimate.
   - **Fix:** use one value everywhere, consistent with fix 2.
4. **METHOD.md Step 3 "What goes wrong without it"; "How it differs" table row "When to abstain".**
   - **Current text:** "accuracy was 0 in the two weakest fifths of genes by partner strength".
   - **Problem:** that is evidence for partner strength (zmean), not for the split-half gate. The gate itself was never
     evaluated on the hold-out: no precision is reported for assessable vs non-assessable H genes, and R(g) received
     zero calibration weight.
   - **Fix:** add "*Not tested directly:* the hold-out was not split by the assessability gate; the evidence above is
     for partner strength, which the gate correlates with."
5. **INSIGHTS.md top.**
   - **Problem:** categories 1 and 2 are 18 entries over about 130 lines, so they fail the "half a page" test.
   - **Fix:**
     - Add a ranked half-page block under "The main point": the 3–4 domain insights and the 3–4 method insights, one
       line each with their key number. Suggested order:
       - Domain: S3 (3.0% vs homology 21.8%), S1 (42% curation lag), S2 (13% / ≥ ~322), S5 (rediscoveries).
       - Method: M1 (LOO about 5×), M2 (conditional p_cal, 30.5 → 4.9), M3 (apply the control's error rate), M4
         (homology baseline).
     - Demote S8, M8 and M10 to category 3 or cut them (see cut candidates).

### SHOULD

6. **INSIGHTS.md IDs collide with project names.**
   - **Problem:** insight IDs M1–M10 and S1–S8 collide with milestone names (E1: "PASS at M4, M6, M9") and with
     referee item IDs (JOURNEY TP7 "Where: … M4, S1").
   - **Fix:** rename the insights to "Bio-1…" and "Meth-1…" (D and R prefixes are already in use). Or write E1 as
     "at three chronology audits (after hold-out, predictions, final)", and TP7 as "referee items M4 and S1".
7. **Undefined terms at first use:**
   - "AP" (INSIGHTS S4 and E10; pipeline figure): average precision on the tool's co-complex benchmark.
   - "c-statistic" and "Brier skill" (METHOD Step 5 and Results table; JOURNEY TP5): add to the glossary.
   - "BH family" (INSIGHTS E12).
   - "Tdark" (METHOD Step 1, JOURNEY TP1): "IDG class for proteins with almost no literature".
   - "TPM".
   - "extra30" (METHOD Results table, used before its glossary entry).
   - "GLS" in README Key results (README has no glossary): add "(Wainberg 2021's corrected correlation)".
   - "packet J071" (METHOD worked example Step 7): say "in its judging packet".
8. **"Paper-count route" is imprecise** (METHOD Step 1; JOURNEY TP1; INSIGHTS S1).
   - **Current text:** "entered through the paper-count route alone (3,819)" / "qualified only through a low count of
     focused papers".
   - **Problem:** D3 = ≤ 10 focused papers **or** Tdark (`src/knownness.py::d3`). The 3,819 genes are "D3 without D2".
   - **Fix:** "through the literature-attention route (D3: few focused papers or Tdark) without a low UniProt score".
9. **JOURNEY.md TP4: "3,000 known genes".**
   - **Problem:** METHOD says 2,519, and DISCREPANCIES B14 notes the mismatch but leaves it.
   - **Fix:** "3,000 sampled known genes (2,519 scorable after removing circular targets)".
10. **JOURNEY.md timeline caption.**
    - **Current text:** "no commits for 4.8 h … (git does not say why; see DISCREPANCIES C1)".
    - **Problem:** C1 now records the PI note (machine asleep), and the explainer checked that note against
      `perf_counter`.
    - **Fix:** "(the machine was asleep, by the PI's account, consistent with the run manifest; see C1)".
11. **METHOD.md "How it differs" table, row Artefacts.**
    - **Current text:** "Removes CRISPR-cutting and copy-number look-alikes (Lazar 2024)".
    - **Problem:** this states a benefit that was shown only on synthetic data. On the hold-out, accuracy was 3.3%
      without the exclusion vs 3.0% with it.
    - **Fix:** append "(shown on synthetic data; no measurable effect on the hold-out)".
12. **INSIGHTS.md M1 title: "Leave-one-out … overstated accuracy about fivefold".**
    - **Problem:** the body and DISCREPANCIES C4 say that part of the gap is a population difference.
    - **Fix:** "Leave-one-out accuracy was about five times the accuracy on newly annotated genes".
13. **INSIGHTS.md S5: "Only PLEKHH3 … had no prior".**
    - **Problem:** this is true only of the 10 report genes. 6/40 of the top 40 had no prior (PLEKHH3, LGALS9B, FBXL18,
      SASH3, DDX19A, DPCD).
    - **Fix:** "Of the ten deep-dive genes, only PLEKHH3 …; 6 of the top 40 had no prior in any resource checked".
14. **INSIGHTS.md source links.**
    - **Problem:** E6–E9, E11 and E12 have no link to a source.
    - **Fix:** link E6 to PROVENANCE (already done), E7 to holdout_eval/SUMMARY.md, E9 to `src/vocab.py`, E11 to
      AGENT_PROMPTS.md and E12 to DEVIATIONS.md. Also give DISCREPANCIES rows anchors, so that "DISCREPANCIES C4/C1"
      links land on the row.
15. **METHOD.md worked example, Step 4 term table.**
    - **Problem:** it lists ranks 1, 2, 4, 5 and silently skips rank 3 (regulatory ncRNA-mediated post-transcriptional
      gene silencing, S = 92.00, tied with rank 4).
    - **Fix:** show rank 3, or note "(rank 3 ties rank 4 — the parent/child tie of Step 4)". It is a nice live
      illustration of the tie problem.
16. **METHOD.md Step 3, Dede 2020 citation.**
    - **Problem:** the paper is about paralog buffering masking hits in Cas9 screens. It does not support "barely
      expressed … flat noise … arbitrary partners".
    - **Fix:** cite it for "many expressed genes are never hits, often because of paralog buffering" (as LITERATURE.md
      §1.4 does). Also add DOIs where the METHOD glossary names Dempster 2021 and Fischer 2025 without them.
17. **README "explainer.html … All of the above as one interactive page".**
    - **Problem:** the HTML has no README or DISCREPANCIES content.
    - **Fix:** say "METHOD, JOURNEY and INSIGHTS as one interactive page", or add a DISCREPANCIES tab.

## Checklist answers

1. **Can someone read only the first screen of METHOD.md and explain the method in three sentences?** Yes. The
   one-sentence and three-sentence summaries plus the Key numbers box are clear and self-contained. However, "stays
   silent" misdescribes the abstention (MUST 1).
2. **Does every step have a "why" a reader would accept and a "what goes wrong without it" backed by evidence?** Mostly
   yes, and candidly:
   - Step 1 admits that it brings no measured accuracy gain.
   - Steps 4 and 6 report that their guards and checks did little.
   - Step 3's evidence is indirect: partner-strength quintiles, not the gate itself (MUST 4).
3. **Would a reader of JOURNEY understand why the final method looks the way it does?** Yes. The main point maps
   "fix the rule first, test on the future, cut every count by its control" onto the steps. Each TP ends with the step
   it produced, the Step 2 exception is explained, and DISCREPANCIES separates the PI's account from the record.
4. **Is the top of INSIGHTS (categories 1 and 2) on half a page and ruthlessly ranked?** No. There are 18 multi-line
   entries (about 130 lines). The ranking is defensible, but a reader cannot get the top insights in half a page
   (MUST 5).

## Overclaiming / understatement

- **Overclaims:** the abstention framing (MUST 1), the artefact-exclusion benefit (SHOULD 11), the M1 title
  (SHOULD 12), and "Only PLEKHH3" (SHOULD 13).
- **Elsewhere the tone is right:** post-review numbers are tagged, "believed" vs "shown" is used consistently, and
  conditional p_cal, GLS parity and the homology gap are stated up front.
- **No understatement found.** If anything, the 0.32 vs 0.28 orthogonal-support rates could be given their CIs.

## Cut candidates (a reader would not miss them)

- The per-step "Code:" lines in METHOD Steps 1–7. They duplicate the table in "Pseudocode and where each step lives".
- The METHOD Results table row "Tool reproduction" (duplicates Step 2).
- INSIGHTS E4, E5 and E13. They repeat TP4, TP3 and DISCREPANCIES B1/A9.
- The JOURNEY appendix rows that repeat INSIGHTS M7 and M8 (tiers, robustness checks, orthogonal support).
- DISCREPANCIES section D bullets 2–3 (commit timing, prior-only degenerate). They are already covered in the body.
- The JOURNEY "Words used below" list could link to the METHOD glossary instead of re-defining 12 terms.
