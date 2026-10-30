---
title: "A pre-registered, temporally validated evaluation of co-essentiality function predictions for uncharacterised human genes: modest accuracy, narrow reach and many already-published functions"
---

<!-- manuscript/manuscript.md — assembled from manuscript/drafts/01–04, reports/, results/m7/ and manuscript/figures/;
revised after manuscript review round 1 (reviews/ms_round1_*.md; response in reviews/ms_round1_response.md).
Every number carries a src comment naming the committed file it comes from; scripts/80_build_manuscript.sh strips these
comments in the rendered PDF/DOCX only. Labels in square brackets inside Results: [pre-specified] = DESIGN.md v2.3 at
tag design-frozen; [deviation] = logged in DEVIATIONS.md (Methods states which rows were logged after the affected
result); [exploratory] = post hoc, before manuscript review; [post-review exploratory] = requested by the round-1
referees, computed by scripts/90_revision_analyses.py into results/revision/ (H-touching analyses logged in LOOKS.md,
2026-10-30), no frozen rule changed; [descriptive] = computed for presentation by scripts/60_figures.py,
scripts/61_figure5.py or scripts/62_figS4.py (manuscript/figures/source_data/), not a pre-specified test. Citations are
numbered in order of first appearance; keys were resolved against references/literature_refs.tsv. -->

**Short title:** Pre-registered evaluation of co-essentiality predictions

[Human author(s), affiliations and ORCID iDs to be completed. Under PLOS policy AI tools cannot be authors; the
human author(s) named here take responsibility for the work. Human oversight: [to be completed by the human authors]
(role to be confirmed).]

**Corresponding author:** [name and e-mail to be completed]

# Abstract

**Background.** Thousands of human genes lack an experimentally established function. Co-essentiality
in CRISPR screens has suggested functions for several, but how often such predictions prove correct, and for how many
genes, has not been measured under a pre-registered, time-split design.

**Methods.** We pre-registered 4,924 <!-- src: preregistration/CRITERIA.md --> uncharacterised genes from annotation
data alone and froze the list and analysis design before computing any gene–gene quantity. We applied a
co-essentiality method (zavg_BEF) to DepMap 26Q3, tested it on a hold-out of 809
<!-- src: results/holdout_eval/core.md --> genes uncharacterised in 2018 and annotated since, calibrated its scores
(p_cal), and compared top predictions with blindly retrieved literature against decoys. AI agents ran the study.

**Results.** 646 genes (13.1%) <!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> passed the
assessability test; allowing for its false-call rate, about 243 (4.9%)
<!-- src: results/revision/a6_assessability_null_adjusted.tsv --> remain [post-review]. Hold-out top-term
precision was 0.030 (95% CI 0.018–0.043), above prior-only (0.000) and matched-gene (0.005) nulls and
indistinguishable from GLS (difference +0.006, −0.005 to +0.017)
<!-- src: results/holdout_eval/SUMMARY.md -->; it was 0.182 for complex membership and 0.012 after reweighting to the
pre-registered genes <!-- src: results/holdout_eval/SUMMARY.md -->. Homology transfer reached 0.218
<!-- src: results/holdout_eval/SUMMARY.md -->; adding co-essentiality where homology made no prediction gained 0.006
<!-- src: results/revision/a7_combination_rules.tsv -->. Calibration was not detectably poor but rested on 24 events
(slope 0.82, 95% CI 0.51–1.13) <!-- src: results/revision/a4_calibration_models.tsv -->. Among 2,583 in-support genes,
about 30.5 top terms should be confirmed if each gene is later annotated, about 4.9 (2.2–8.1) unconditionally <!-- src: results/ledger/pcal_summary.json; results/revision/numbers_a3.json -->. Judges supported 18 of the 40 top
predictions (16 on the GO term alone) against 3 of 120 decoys <!-- src: results/revision/a5_judging_sensitivity.tsv -->,
but 31 of these genes already had published functions <!-- src: results/m7/judge/analysis_main.md --> and 34 had a
co-essential or physical link in earlier catalogues <!-- src: results/revision/a2_novelty_overlap.tsv -->.

**Conclusions.** Co-essentiality gives specific but low-accuracy predictions that add little to homology. Many
"uncharacterised" genes have published functions, partly because literature-based definitions miss complex subunits. Only one of ten candidate reports, PLEKHH3 with PTEN and PLEKHA1, has no precedent in
the catalogues we checked.

# Author summary

By the definition we used, about one human protein-coding gene in four (4,924 of 19,296
<!-- src: preregistration/CRITERIA.md -->) has no experimentally established function in the main annotation database
and has been little studied. One way to find clues is to look for genes whose loss harms the same cancer cell lines. Such
"co-essential" genes often work together. Before looking at any co-essentiality data, we fixed the list of genes and
wrote down every analysis and decision rule. We then tested the method the way it would be used in practice: we
predicted functions for genes that were unknown in 2018 and checked the predictions against what scientists have
discovered since. The method beat chance, but rarely, and much less often than transferring knowledge from related
genes; other co-essentiality methods did as well. Its confidence scores were not detectably wrong, but they rest on few
confirmed predictions and assume that a gene will be studied at all. The strongest predictions mostly matched functions
that were already published but had not entered the databases, and most had already been suggested by earlier
co-essentiality or protein-interaction maps. Part of this "curation lag" comes from how we defined an uncharacterised
gene: counting only papers about few genes misses proteins described as members of large complexes. We offer ten
detailed candidate reports with experiments that could confirm or refute them. The study was run by AI agents; we
describe the checks that constrained their work and the points where those checks were incomplete.
