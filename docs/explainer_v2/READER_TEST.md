# Reader test of explainer_v2/README.md

Reader profile: molecular biologist, basic statistics, not on the project, 15 minutes. Read only the README and the five PNGs.

## Part 1. Answers from memory

**(a) What the method does, in three sentences.**
It takes human genes that databases call "uncharacterised" and looks up which genes, across about 1,360 CRISPR-knockout cancer cell lines, are needed by the same cell lines (co-essential partners). It then guesses the gene's function as the Gene Ontology (GO) term most of its partners share, and attaches a probability that the guess is right. The project's real point is to test this honestly: the gene list was frozen first, scoring used functions discovered after 2018, and the result is a weak signal that mostly rediscovers things already known.

**(b) Steps and why each is needed.**
1. Freeze the gene list (4,924 genes) from database criteria before any analysis, so genes can't be picked because the method works on them.
2. Find each gene's top 25 co-essential partners with an existing tool, after removing same-chromosome-arm genes and paralogues, because CRISPR cutting artefacts and duplicated genes mimic co-essentiality.
3. Check that the partner list reproduces when the cell lines are split in two halves, compared with look-alike genes. Unknown genes are often not expressed or not needed, so their "partners" are noise.
4. Let the partners vote for a GO term, and convert the strength of the vote into a calibrated probability, fitted on the post-2018 test set. Confidence learned on well-studied genes would be overconfident.
5. Test it three ways: against annotations added after 2018, against blinded literature judges that also see decoys, and against independent data (protein interactions and similar).

**(c) Did it work? Three tests and verdicts.**
- Post-2018 annotations (809 genes): top guess right for about 3%, against 0.5% for chance. Verdict: beats chance, but weak. It is tied with an older co-essentiality score and far below homology (about 22%).
- Is the stated confidence honest: yes, predicted and observed rates match (3.1%). But the highest confidence is only 0.14, so nothing reaches "confident".
- Literature judges: 18 of 40 real predictions supported against 3 of 120 decoys. Verdict: much better than decoys, but 16 of the 18 were already published. (The independent-data test barely separated real from fake and was not used for ranking.)

**(d) Two design decisions and the evidence behind them.**
- Scoring on post-2018 annotations instead of leave-one-out. Evidence: leave-one-out gave about 14% on known genes against 3% on future ones, and a model calibrated on known genes promised 8.9% but delivered 3.1%.
- Comparing reproducibility against look-alike genes instead of keeping the top 5%. Evidence: a statistics reviewer said a cut-off is not a test against chance, and the non-expressed-gene control then showed a 13% leak, which cut the estimated number of real-signal genes to about 320.
(Also: dropping the robustness checks to labels, because 221 of 269 candidates failed them.)

**(e) Most surprising finding.**
"Uncharacterised" mostly means "not yet curated". In a random sample of 50 genes from the list, 42% already had an experimentally established function. Close second: homology beats the method roughly 7 to 1.

**(f) When not to use it.**
- As a general gene annotator (use homology or interaction data first).
- For genes that fail the reproducibility check (about 87% of the list).
- To claim novelty without checking earlier co-essentiality and interaction catalogues.
- For "machinery" genes (mitochondria, ribosome, DNA repair, and so on), which have no calibrated confidence.

## Part 2. Reading experience

### Confusions, undefined terms, contradictions, length

1. **Reproducible genes versus calibrated genes (646 vs 2,583).**
   - Quote: "Genes that fail still get a prediction, flagged, and cannot enter the shortlist." Later: "Only genes that resemble the test set get one (2,583 genes)." Fine print: "About 82% of the expected confirmations come from genes that fail the reproducibility check."
   - Why: three gene sets (646 reproducible, 2,583 calibrated, 4,271 measured) are never reconciled, and the funnel figure omits 2,583. The 82% line seems to undercut the whole purpose of Step 3. It is hard to see which genes the headline "about 5 confirmations out of 2,583" refers to.
2. **"Already published" counts look inconsistent.**
   - Quote: "16 of the 18 already had a published function" versus the table's "Already published / prior catalogue link / no prior: 31/40 / 34/40 / 6/40."
   - Why: if 31 of 40 were already published but only 18 were judge-supported, where did the other 13 go? 16/18 and 31/40 are never connected.
3. **The 3% is secretly conditional.**
   - Quote: "That is the chance that curators record exactly this term ... *if* the gene gets any new annotation."
   - Why: only here do I learn that the 809 test genes are, by construction, genes that did gain annotation. That is crucial for reading the 3% in Test 1, but it is not stated there. It is also the reason for the "30 versus 5" jump, which arrives as a surprise in Test 2.
4. **The homology baseline.**
   - Quote: "ranking the gene's own computer-inferred GO terms from 2018".
   - Why: how do "uncharacterised" genes have inferred terms, and is this a fair comparator, given they were allowed in the 2018 annotation but are excluded from the experimental-evidence definition? The figure labels it "Homology (sequence similarity)", which suggests something different. The 22% is the most important number in the document and is the least explained.
5. **"Look-alike genes" used for three different things** (reproducibility null, chance baseline for accuracy, independent-data control). It is defined only in the glossary, and I was not sure it was the same construct each time.
6. **Undefined jargon met in the body.**
   - Hash/fingerprint (explained, fine).
   - "c-statistic", "Brier skill", "slope 0.82" (table only, no gloss).
   - "Perturb-seq", "hu.MAP 3.0", "RNA-interference screens", "module label", "tiers", "machinery genes" (first appears in section 7 as an "uncalibrated list" that was never introduced), "PI agent" (principal investigator, defined mid-sentence).
   - "robustness checks" (leave out the most dependent cancer type) are not a step in section 3, yet they appear in section 7 and the table.
7. **"The project had to use a co-essentiality scoring tool from the same lab."**
   - Why: same lab as whom? Who imposed this? It reads as a rule from nowhere. The tool is also a three-part score (profile similarity, partner overlap, network distance), but I never learn why that tool is credible beyond "reproduced its benchmark".
8. **Eight partners vs seven blue bars.**
   - Quote: "Eight partners vote for ... " and, in the figure, "8 of 25 partners vote for it", while the figure's blue bars number seven and the eighth (PPP6C) is grey. Minor, but made me re-count.
9. **Step 3 numbers.**
   - Quote: "Only 646 of 4,924 genes (13%) passed ... Allowing for this, about 320 genes, roughly 1 in 15." I had to re-read to see that 646 is not the real count, and that "expressed vs not" is the control. The explanation of a "leak that was 13% not 5%" is compressed. The table then gives 241 / 322 / 243 / 635-gene variant, which is more than I can follow.
10. **Different percentages for "how good".** 3%, 12%, 18%, 14%, 8.9%, 1%, 22%: each is defined in a different bullet or section. I wanted a single comparison table in the main text rather than at the bottom as a list of file paths.
11. **Opening claim vs finding.** Section 1: "no experimentally supported function ... and little focused literature" versus finding 1: 42% already had an established function. The text does explain this, but the problem section presents the 4,924 as unstudied, so the result reads as a contradiction of the premise rather than a caveat.
12. **Too long and too detailed.**
    - Section 7 (the AI-team history) is about a fifth of the document and is mostly process. "Where it went in circles" and "Who did what" are interesting but are not needed to understand the method.
    - The fine-print table has 20 rows with file paths (`results/...`) that mean nothing to a reader without the repo.
    - Step 5 mixes in the stories of SLC25A51 and FIRRM and a "31 minutes before" detail; they are good evidence but interrupt the explanation of the three tests.
13. **Dates and timing.** "Sixteen minutes after the freeze" and "31 minutes before the data were opened" are precise but I could not tell which clock they relate to. The timeline figure shows UTC times, but the start (20:00) is not tied to a date in the axis.
14. **Citations in-line** (Stoeger 2018; Haynes 2018; Gillis & Pavlidis 2011, 2012) are dense in section 2 and break the flow for a non-specialist; fine as superscripts.
15. **Tone.** "Honest" is repeated a lot in the title, subheads and text. It feels like self-assessment; the evidence already shows it.

### Clarity ratings (1-5)

| Section | Rating | Comment |
|---|---|---|
| Opening paragraph | 5 | Clear, punchy, sets expectations. |
| 1. The problem | 4 | Good. The 1-in-4 number is a bit hard to square with later finding 1. |
| 2. Idea in 60 seconds | 4 | Co-essentiality and guilt by association are well explained. The leave-one-out trap is clear. |
| 3. Method, Steps 1-2 | 4 | The "What / Why / ANKRD52" format works very well. The pairing of Step 2's three-part score is slightly dense. |
| 3. Step 3 | 3 | Reproducibility logic is fine; the leak and "1 in 15" arithmetic is rushed. |
| 3. Step 4 | 3 | "Voting", "calibration" are good; conditionality and the 2,583 are confusing. |
| 3. Step 5 | 3 | Three tests packed into one bullet list; lots of numbers; the SLC25A51/FIRRM aside. |
| 4. ANKRD52 | 5 | Short and the figure carries it. |
| 5. Scorecard | 4 | Verdict-first format is excellent. Homology comparison and the bridge from 3% to 5 expected hits need more setup. |
| 6. Five things learned | 4 | Great content. Item 3 and 5 have numbers that feel hard to place. |
| 7. How the AI team got here | 2 | Long, process-heavy, uses terms from outside the method (PI agent, tiers, robustness checks). |
| 8. Fine print | 2 | Useful for experts, but the table is a wall with repo file paths. The caveats are the best part and are buried at the end. |
| 9. Glossary | 4 | Useful; should be introduced earlier or include "look-alike" contexts and c-statistic. |

### Figures

- **Most helpful: the scorecard (d_scorecard.png).** It puts the 3.0% against 0.5%, 2.3% and 21.8% on one axis, so the "weak but above chance, far below homology" story lands in two seconds. The promised/delivered bars make calibration intuitive. A small flaw: the light-blue 2 supported-but-not-already-published is unlabelled, and the y axis says "%" while the labels are counts.
- **Next: ANKRD52 (c_ankrd52.png)** shows how every step looks on one gene; the reproducibility bar (12 vs ~0) is very clear. Slightly small text.
- **Funnel (a_funnel.png)**: good for scale, but it hides how the calibrated set (2,583) relates to the 646, and "log scale" makes the bars look more alike than the numbers are.
- **Pipeline (b_pipeline.png)**: clean but mostly restates the headings; I would have liked it to show what goes in and out of each step (list, partner list, flag, guess+probability).
- **Least helpful: timeline (e_journey.png).** Six numbered dots with a two-word label each and a time axis; it tells me nothing about what happened or why, and the "overnight run" band is unexplained.

### Five changes that would most improve understanding

1. **Add one main-text comparison table or "numbers at a glance"** (3% vs 0.5% vs 2.3% vs 22%; 14% leave-one-out; the 3% / 12% / 18% subgroups), and explain the homology baseline in one plain sentence (what it ranks, why it exists for "unknown" genes). Say clearly that homology is the real yardstick.
2. **State the conditioning up front.** In Test 1 and Step 4, say that the 809 test genes are by definition genes that gained annotation, and put the "30 to 5 expected confirmations" derivation in one short paragraph.
3. **Reconcile the gene sets.** Add 2,583 (calibrated) to the funnel and explain how it overlaps with 646 (reproducible) and why 82% of expected hits come from genes that failed the check. Also fix the 16/18 vs 31/40 vs 34/40 "already published" tangle with one sentence defining each.
4. **Shrink section 7 and the fine-print table.** Keep the six decisions as three-line "evidence, decision" boxes; move "Who did what / circles" to the linked journey document; drop file paths from the table and replace with plain-language labels. Move the caveats up before the table.
5. **Define terms where first used and cut the unnecessary ones**: look-alike genes, robustness checks, machinery genes, c-statistic / Brier skill, Perturb-seq, hu.MAP. Replace the timeline figure with a decision-and-evidence figure (what was tried, what evidence changed it), or add a sentence per dot.
