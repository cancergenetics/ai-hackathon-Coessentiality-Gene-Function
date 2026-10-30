---
title: "A pre-registered, temporally validated evaluation of co-essentiality function predictions for uncharacterised human genes: modest accuracy, narrow reach and many already-published functions"
---

<!-- manuscript/manuscript.md — assembled from manuscript/drafts/01–04, reports/, results/m7/ and manuscript/figures/;
revised after manuscript review rounds 1 and 2 (reviews/ms_round1_*.md, reviews/ms_round2_*.md; responses in
reviews/ms_round1_response.md and reviews/ms_round2_response.md). Detailed sensitivity and secondary analyses moved to
manuscript/supplementary/S1_Text.md in round 2.
Every number carries a src comment naming the committed file it comes from; scripts/80_build_manuscript.sh strips these
comments in the rendered PDF/DOCX only. Labels in square brackets inside Results: [pre-specified] = DESIGN.md v2.3 at
tag design-frozen; [deviation] = logged in DEVIATIONS.md (Methods states which rows were logged after the affected
result); [exploratory] = post hoc, before manuscript review; [post-review exploratory] = requested by the referees,
computed by scripts/90_revision_analyses.py (round 1) or scripts/92_round2_numbers.py (round 2, no H outcome read) into
results/revision/ (the LOOKS.md row for the H-touching round-1 analyses was committed with their results, b39691d), no
frozen rule changed; [post-review] alone = a table column or report statement added after review that is not itself an
analysis; [descriptive] = computed for presentation by scripts/60_figures.py,
scripts/61_figure5.py or scripts/62_figS4.py (manuscript/figures/source_data/), not a pre-specified test. Citations are
numbered in order of first appearance; keys were resolved against references/literature_refs.tsv. -->

**Short title:** Pre-registered evaluation of co-essentiality predictions

**Authors:** [Human author(s), affiliations and ORCID iDs: to be completed by the human authors. Under PLOS policy AI
tools cannot be authors; the human author(s) named here take responsibility for the work.]

**Human oversight:** [Name, affiliation and role of the human who oversaw the study: to be completed by the human
authors.]

**Corresponding author:** [Name and e-mail: to be completed by the human authors.]

# Abstract

**Background.** Co-essentiality in CRISPR screens suggests functions for uncharacterised human genes, but its accuracy
and reach have not been measured under a pre-registered, time-split design.

**Methods.** We pre-registered 4,924 <!-- src: preregistration/CRITERIA.md --> uncharacterised genes and froze the
list and design before any gene–gene computation. We tested a co-essentiality method (zavg_BEF; DepMap 26Q3) on
809 <!-- src: results/holdout_eval/core.md --> genes uncharacterised in 2018 and annotated since, calibrated its scores
(p_cal), and judged top predictions against blindly retrieved literature, with decoys. AI agents ran the study.

**Results.** 646 genes (13.1%) <!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> were
assessable; allowing for the test's false-call rate, calls exceed the null expectation by about 243
<!-- src: results/revision/a6_assessability_null_adjusted.tsv -->; under that assumption at least about 320 genes
(6.6%) <!-- src: results/revision/a10_assessability_excess_and_implied.tsv --> carry real signal [post-review
exploratory]. Hold-out top-term precision was 0.030 (95% CI 0.018–0.043), above prior-only and matched-gene (0.005)
nulls and indistinguishable from GLS (difference +0.006, −0.005 to +0.017)
<!-- src: results/holdout_eval/SUMMARY.md -->; it was 0.182 for complex membership, and 0.012 reweighted to
pre-registered genes <!-- src: results/holdout_eval/SUMMARY.md -->. Homology transfer reached 0.218
<!-- src: results/holdout_eval/SUMMARY.md -->, and co-essentiality added 0.006 where homology made no prediction
<!-- src: results/revision/a7_combination_rules.tsv -->. Calibration was not detectably poor but rested on 24 events
<!-- src: results/revision/a4_calibration_models.tsv -->. Among 2,583 in-support genes, about
30.5 top terms should be confirmed if each gene is later annotated, and about 4.9 (2.2–8.1) if the 2018 cohort's
annotation rate applies [post-review exploratory] <!-- src: results/ledger/pcal_summary.json; results/revision/numbers_a3.json -->.
Judges supported 18 of the 40 top predictions (16 on the term alone) against 3 of 120 decoys
<!-- src: results/revision/a5_judging_sensitivity.tsv -->, but 31 of these genes already had published functions
<!-- src: results/m7/judge/analysis_main.md --> and 34 had links in earlier catalogues
<!-- src: results/revision/a2_novelty_overlap.tsv -->.

**Conclusions.** Co-essentiality gives specific, low-accuracy predictions that add little to homology. Many
"uncharacterised" genes have published functions, partly because literature-based definitions miss genes studied mainly
in multi-gene papers, including, among our top candidates, many complex subunits. Of ten candidate reports, only PLEKHH3
(with PTEN and PLEKHA1) lacks a catalogue precedent, and it is a low-amplitude co-advantage signal not yet controlled
for lineage.

# Author summary

By the definition we used, about one human protein-coding gene in four (4,924 of 19,296
<!-- src: preregistration/CRITERIA.md -->) has no experimentally established function in the main annotation database
and was classed as little studied by our literature criterion; many such genes in fact have published functions.
One way to find clues is to look for genes whose loss harms the same cancer cell lines. Such
"co-essential" genes often work together. Before looking at any co-essentiality data, we fixed the list of genes and
wrote down every analysis and decision rule. We then tested the method the way it would be used in practice: we
predicted functions for genes that were unknown in 2018 and checked the predictions against what scientists have
discovered since. The method beat chance, but rarely, and much less often than transferring knowledge from related
genes; other co-essentiality methods did as well. Its confidence scores were not detectably wrong, but they rest on few
confirmed predictions and assume that a gene will be studied at all. The strongest predictions mostly matched functions
that were already published but had not entered the databases, and most had already been suggested by earlier
co-essentiality or protein-interaction maps. Part of this "curation lag" comes from how we defined an uncharacterised
gene: counting only papers about few genes misses genes studied mainly in multi-gene papers, including, among our top
candidates, many complex subunits. We offer ten
detailed candidate reports with experiments that could confirm or refute them. The study was run by AI agents; we
describe the checks that constrained their work and the points where those checks were incomplete.
