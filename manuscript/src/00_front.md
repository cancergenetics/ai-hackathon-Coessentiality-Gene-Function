---
title: "Pre-registered and calibrated function predictions for uncharacterised human genes from DepMap co-essentiality reveal modest accuracy and widespread curation lag"
---

<!-- manuscript/manuscript.md — assembled from manuscript/drafts/01–04, reports/, results/m7/ and manuscript/figures/.
Every number carries a src comment naming the committed file it comes from; scripts/80_build_manuscript.sh strips these
comments in the rendered PDF/DOCX only. Labels in square brackets inside Results: [pre-specified] = DESIGN.md v2.3 at
tag design-frozen; [deviation] = logged in DEVIATIONS.md before the affected result was computed; [exploratory] = post
hoc, logged in LOOKS.md; [descriptive] = computed for presentation by scripts/60_figures.py or scripts/61_figure5.py
(manuscript/figures/source_data/), not a pre-specified test. Citations are numbered in order of first appearance;
keys were resolved against references/literature_refs.tsv (all rows verified). -->

**Short title:** Pre-registered co-essentiality function predictions

[Authors and affiliations to be completed]

AI-generated research project; human oversight: [to be completed by the human authors].

**Corresponding author:** [to be completed]

# Abstract

**Background.** Thousands of human protein-coding genes lack an experimentally established function. Co-essentiality
in CRISPR screens has suggested functions for several of them, but how often such predictions prove correct, and for
how many uncharacterised genes the approach can say anything, has not been measured prospectively.

**Methods.** We pre-registered 4,924 <!-- src: preregistration/CRITERIA.md --> uncharacterised genes from annotation data
alone and froze the list and analysis design under a cryptographic hash before computing any gene–gene quantity. We
then applied a co-essentiality method (zavg_BEF) to DepMap 26Q3 CRISPR screens, tested it on a temporal hold-out of 809
<!-- src: results/holdout_eval/core.md --> genes that were uncharacterised in 2018 and annotated since, converted scores
into calibrated probabilities (p_cal), and judged the top predictions against blindly retrieved literature, with decoy
statements as controls. A team of AI agents ran the study under explicit safeguards.

**Results.** Only 646 genes (13.1%) <!-- src: manuscript/figures/source_data/Fig1b_census_funnel.tsv --> were
assessable. On the hold-out, precision of the top-ranked term was 0.030 (95% CI 0.018–0.043), above prior-only (0.000)
and matched-gene (0.005) nulls <!-- src: results/holdout_eval/SUMMARY.md -->, but below transfer from homology (0.218)
and protein interactions (0.049) <!-- src: results/holdout_eval/SUMMARY.md -->. Calibration was adequate (slope 0.82)
<!-- src: results/holdout_eval/calibration.md -->. No pre-registered gene exceeded p_cal 0.141; about 30.5 (13.8–49.7)
of 2,583 calibrated top terms are expected to be confirmed <!-- src: results/ledger/pcal_summary.json -->. Judges
supported 18 of the 40 top predictions against 3 of 120 decoys (p = 0.0002), but 31 of the 40 genes already had
published functions <!-- src: results/m7/judge/analysis_main.md -->; 42% (29–56%) of random pre-registered genes were
in the same state <!-- src: results/audit/curation_lag_audit.md -->. Ten candidates received red-teamed reports,
including INAFM1 with the NRF1-activation axis, PLEKHH3 with PTEN and PLEKHA1, and a TP53-conditional centriole module
for C5orf34.

**Conclusions.** Co-essentiality gives specific and calibrated, but low-accuracy, function predictions that complement
homology and interaction data. Many "uncharacterised" genes are uncurated rather than unstudied.

# Author summary

By the definition we used, about one human protein-coding gene in four (4,924 of 19,296
<!-- src: preregistration/CRITERIA.md -->) has no experimentally established function in the main annotation database
and has been little studied. One way to find clues is to look for genes whose loss harms the same cancer cell lines. Such
"co-essential" genes often work together. Before looking at any
co-essentiality data, we fixed the list of genes and wrote down every analysis and decision rule. We then tested the method the way it would be used in practice: we predicted functions for genes that were unknown in
2018 and checked the predictions against what scientists have discovered since. The method beat chance, but rarely, and less often than transferring knowledge from related genes. Its confidence scores were
honest, showing how likely each prediction is to hold up. The strongest predictions mostly matched
functions that were already published but had not yet entered the databases, so many "unknown" genes are known but
uncurated. We offer ten detailed candidate reports with experiments that could confirm or refute them. The
study was run by AI agents, and we describe the checks that kept their work honest.
