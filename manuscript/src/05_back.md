
# Data and code availability

All code, configuration, pre-registration files, design documents and reviews, committed results, figure source data
and candidate reports are in the project repository [repository URL and archival DOI to be added on deposition]. The
layout is: `PROMPT.md` (the fixed goal), `DESIGN.md` (frozen design v2.3), `DEVIATIONS.md` and `LOOKS.md` (change and
hold-out logs), `RESEARCH_TREE.md` (decision record), `CLAIMS.tsv` (number-to-file map), `preregistration/` (the frozen
list U, criteria, provenance and `FREEZE.sha256`), `config/` (frozen parameters, seeds, pinned environment, agent
scopes), `src/` and `scripts/` (pipeline, numbered in execution order), `tests/` and `verify/` (unit tests, toy-data
checks and independent re-derivations), `results/` (per-milestone results, including the hold-out evaluation, the
prediction ledger and the blinded-judging files), `reports/` (ten candidate reports, experiment plans and red-team
reviews), `reviews/` (design reviews and audits) and `manuscript/` (this text, figures and source data; rendered by
`scripts/80_build_manuscript.sh`).

`DATA.md` lists the source, version, URL, SHA-256 checksum and licence of every dataset; `scripts/check_data.sh`
verifies local copies against `config/data_checksums.tsv`. Raw and restricted data, and large derived matrices, are
not redistributed: they are excluded from the repository and regenerated from the public sources by script. DepMap
26Q3 files are available from the DepMap portal under CC BY 4.0 <!-- src: DATA.md --> [DepMap_web]. The Olivieri et al.
chemogenomic screen table [Olivieri2020] is licensed CC BY-NC-ND <!-- src: DATA.md -->; it was used internally for the
admission test only and is not redistributed in any form. The co-essentiality tool was used read-only at commit 3c684c9
<!-- src: DATA.md --> [Coessentiality_tool] and is not redistributed.

# Acknowledgements

[To be completed.]

# Competing interests

The authors have declared that no competing interests exist.

# References

<!-- REFERENCES -->

# Figure legends

![](figures/Fig1.png)

**Fig 1. Study design, census of the pre-registered genes and curation lag.** (A) Workflow. The list of uncharacterised
genes (U) and the analysis design were frozen before any gene–gene DepMap quantity was computed (blue, C1); the tool was
verified and the ranker chosen on characterised leave-one-out (LOO) genes (grey); accuracy and calibration were tested
on a temporal hold-out H of genes uncharacterised at the July 2018 GO release, opened once (orange, C2); the calibrated
model was then applied to U and evaluated against clean-negative, matched-gene and decoy controls (green, C3), and the
top predictions went to literature validation (C4). (B) Census of U: HGNC protein-coding genes, pre-registered genes,
genes with a DepMap 26Q3 column, scorable genes, scorable and expressed genes, and assessable genes (scorable, expressed
and split-half reproducible beyond a matched-gene null); percentages are of U. (C) Fraction of U genes assessable by
pre-registered stratum (labels give assessable/stratum size); "expressed" includes lineage-restricted genes; SD tertiles
and dependency classes are within U; "core" denotes genes with at most 3 focused PMIDs that are Tdark. (D) Curation-lag
audit of a pre-specified random sample of 50 U genes, classed by an auditor without access to co-essentiality output as
N1 (function established), N2 (partial) or N3 (none). Bars show the fraction in each class with Wilson 95% confidence
intervals; the dark part of each bar is the fraction "recognised" by a closed-book language-model recall probe. Source
data: manuscript/figures/source_data/Fig1b_census_funnel.tsv, Fig1c_assessable_by_stratum.tsv,
Fig1d_curation_lag_audit.tsv.

![](figures/Fig2.png)

**Fig 2. Temporal hold-out: accuracy, calibration and named controls.** (A) Precision@1 (fraction of the 809 primary
hold-out genes whose top reportable GO term was later annotated with experimental evidence) with 95% cluster-bootstrap
confidence intervals (PMID-only clusters, 10,000 replicates). Above the line: pre-specified core comparisons; below:
the secondary batch (hu.MAP 3.0 interaction-partner transfer; the gene's own t0 electronic, sequence-similarity and
phylogenetic annotations). (B) Paired differences, zavg_BEF minus comparator, with 95% cluster-bootstrap intervals. The
primary intersection–union test requires both upper comparisons (prior-only, matched-gene null) to exclude zero; GLS is
the key secondary comparison. (C) Precision@1 by quintile of the gene's top-K mean zavg_BEF (Q1 2.7–3.7 to Q5 5.4–15.5)
for zavg_BEF, GLS and the matched-gene null, with 95% intervals; prior-only scored 0 in every quintile. (D) Reliability
diagram of the pre-specified calibration model (out-of-fold, 10-fold cluster cross-fitting) and of a secondary model
fitted on LOO genes, in bins of at least 30 genes; observed hit@1 with Wilson 95% intervals; dashed line, perfect
calibration. (E) Named positive controls: number of GO terms gained since t0 (window 2–300 genes), split into clean
terms and terms whose supporting papers cite DepMap or co-essentiality work (excluded), with the rank of the best clean
true term among the gene's reportable terms. †, not in H (no new term in the 5–200 window); case series only. Source data:
manuscript/figures/source_data/Fig2a_precision_by_method.tsv, Fig2b_paired_differences.tsv, Fig2c_signal_quintiles.tsv,
Fig2d_reliability.tsv, Fig2e_named_controls.tsv.

![](figures/Fig3.png)

**Fig 3. Calibrated catalogue for the pre-registered genes.** (A) Cumulative distribution of calibrated probability
(p_cal) for expressed, assessable genes within calibration support (n = 269), for all in-support U genes (n = 2,583) and
for in-support clean-negative genes, which are not expressed in at least 95% of lines (n = 708). The Tier B (0.3) and
Tier A (0.5) thresholds lie off scale. (B) Σp_cal, the expected number of top terms that later experimental annotation
will confirm, with percentile 95% confidence intervals from 2,000 cluster-bootstrap refits of the calibration model; the
boundary-gene value is an upper bound, and the primary top 40 is a point sum. (C) Fraction of real, matched-gene and
decoy-term predictions (247 anchors each) meeting the Tier-A orthogonal support condition (rule), the strict and any-class
variants, and support from individual classes (P, physical; A, co-abundance; L, localisation; G, Perturb-seq), with 95%
confidence intervals. (D) U genes with a reportable top term by module family, coloured by calibration support category
(p_cal within support; boundary upper bound only; no p_cal), with the number of hold-out genes per family in parentheses.
Families with fewer than 30 hold-out genes receive no p_cal. Source data: manuscript/figures/source_data/Fig3a_*.tsv,
Fig3b_sigma_pcal.tsv, Fig3c_orthogonal_support_*.tsv, Fig3d_family_support_category.tsv.

![](figures/Fig4.png)

**Fig 4. The primary top 40.** (A) The 40 highest p_cal values among expressed, assessable, in-support U genes after
built-in artefact exclusions and contradictions, labelled with the predicted GO term and coloured by its module family.
(B) Top-40-only checks and orthogonal evidence: lineage leave-out (refit without the most dependent lineage changes the
top term), DEMETER2 RNAi replication of partner correlations, TP53-status flag (BH q < 0.05), orthogonal classes that
support the predicted term after Holm correction, and support from the family's diagnostic class. ×, check failed (a
Tier B cap, inert because no gene reached a tier); ·, passed; –, not measured or none. Source data:
manuscript/figures/source_data/Fig4_top40_primary.tsv.

![](figures/Fig5.png)

**Fig 5. Blinded literature validation.** (A) Adjudicated scores for real statements (supported, unaddressed,
contradicted) and the fraction of decoy statements supported (Wilson 95% intervals; three decoys per gene), for the 10
hold-out validation genes, the primary top 40, and the secondary S20 and extra30 sets. p-values are exact one-sided
sign-flip tests of real minus mean decoy score; κ is Cohen's κ between the two judges. (B) Fraction of real statements
supported by p_cal bin: the five extra30 quintiles (fill-pool genes outside the top 40) and the two halves of the primary
top 40, with Wilson 95% intervals; diamonds, mean p_cal of the bin. (C) Left, novelty class of each set (N1, function
established; N2, partial; N3, none), from the curation-lag auditor for the random 50 and from the blind literature agent
L otherwise. Right, fraction of real statements supported within each class and set, with Wilson 95% intervals.
(D) Fraction of genes "recognised" by the closed-book recall probe, by novelty class, for the random 50 U genes and for
the 90 candidates, with Wilson 95% intervals. Source data: manuscript/figures/source_data/Fig5a_judging_by_set.tsv,
Fig5b_support_vs_pcal.tsv, Fig5c_novelty_class.tsv, Fig5d_recall_probe.tsv, Fig5_derived_numbers.tsv.

![](figures/FigS1.png)

**S1 Fig. Ranker choice on leave-one-out genes.** (A) Mean reciprocal rank (MRR) of the first correct reportable term
and precision@1, with gene-level 95% intervals, for the three pre-specified rankers and prior-only on 2,519 characterised
LOO genes; R1 was chosen by the frozen MRR rule. (B) Precision@1 with real and shuffled annotation labels (labels
permuted among genes of similar annotation count; seed 0, with seeds 1–4 as ticks). Source data:
manuscript/figures/source_data/FigS1a_loo_rankers.tsv, FigS1b_label_shuffle.tsv.

![](figures/FigS2.png)

**S2 Fig. Split-half reproducibility.** (A) Fraction of genes with split-half reproducibility R(g) at least x for U
(n = 4,271 scorable), H (n = 820), the LOO sample (n = 3,000) and other scorable genes (n = 10,303). (B) Fraction of
scorable U genes with split-half p < 0.05 against the matched-gene null, by expression group (expressed under the
design's definition, not expressed, clean negatives, and clean negatives with and without any dependency), with Wilson
95% intervals; dashed line, nominal 0.05. (C) Precision@1 on H for each of the ten split-half networks (seed/half), with
95% cluster-bootstrap intervals and the matched-gene null; dashed line, full network. Source data:
manuscript/figures/source_data/FigS2a_R_by_set.tsv, FigS2b_reproducibility_rate.tsv, FigS2c_splithalf_networks.tsv.

![](figures/FigS3.png)

**S3 Fig. Admission of orthogonal evidence sources.** (A) Co-complex odds ratio (95% interval, bootstrap over 2,538
complexes not derived from hu.MAP) for each pair source, by class (P, physical; A, co-abundance; G, Perturb-seq; S,
structure). Sources were admitted if the lower bound exceeded 2 (dashed line); hu.MAP 3.0 (grey) was not independent of
DepMap and was reported only; the Olivieri 2020 screens (red) were not admitted. (B) Agreement of localisation sources
with GO cellular component on hold-out genes (Wilson 95% interval). Admission required a lower bound above 0.6 (dashed
line) and at least 200 hold-out genes; red, not admitted. Source data: manuscript/figures/source_data/FigS3a_pair_admission.tsv,
FigS3b_localisation_admission.tsv.

# Table legends

**Table 1. Principal data sources.** Version and use of each input; URLs, SHA-256 checksums and licences are in
DATA.md. Restricted-licence files were used internally and are not redistributed.

**Table 2. Top-40 and S20 predictions judged supported by the literature (blinded, adjudicated).** p_cal is given for the
primary top 40 and the uncalibrated top-K mean zavg_BEF for S20. L class, novelty class from the blind literature agent.
Probe, recognised by the closed-book recall probe. Basis: whether judges cited the GO term (term) or only the module label
(module); "generic" marks support from cancer cell-line proliferation studies. Module labels are shortened; full names
are in the source file (manuscript/figures/source_data/Table2_rediscovery.tsv).

**Table 3. The ten candidate reports.** For each report gene: rank and p_cal in the primary top 40; the predicted GO term
and relationship type (a, stable subunit; b, assembly or maturation factor; d, pathway member, type unresolved); the
strongest co-essential partners; orthogonal classes supporting the term after Holm correction (P, physical; A,
co-abundance; L, localisation; G, Perturb-seq); the blind literature agent's novelty class and the adjudicated verdict on
the real statement; the main caveat after red-team review; and the first decisive experiment. Full reports, experiment
plans and red-team reviews: S1–S10 Reports.

# Supporting information

**S1 Table. Pre-registered list of uncharacterised genes (U).** 4,924 genes with D1–D3 values and strata.
`preregistration/uncharacterised_genes.tsv`; criteria in `preregistration/CRITERIA.md`; freeze hashes in
`preregistration/FREEZE.sha256`.

**S2 Table. Prediction ledger for all scorable U genes.** Top term, V1/V1′ labels, p_cal, support category, artefact
flags and top-10 partners. `results/ledger/u_predictions.tsv`, `u_pcal.tsv`, `u_top5.tsv`, `u_partners.tsv`,
`u_flags.tsv`, `tiers_all.tsv`.

**S3 Table. Primary top 40 with checks, and sensitivity lists.** `results/ledger/top40_primary.tsv`,
`top40_checks.tsv`, `top40_partners_gls.tsv`; clean-first sensitivity list `results/ledger/top40.tsv`; S20 and extra30
in `results/m7/s20.tsv` and `results/m7/extra30.tsv`.

**S4 Table. Hold-out evaluation per gene and secondary analyses.** `results/holdout_eval/per_gene_core.tsv`,
`comparisons_core.tsv`, `secondary.tsv`, `circularity_sensitivity.tsv`, `calibration_oof.tsv`, `controls_case_series.tsv`,
`exploratory_complementarity.tsv`.

**S5 Table. Orthogonal evidence.** Source admission (`results/orthogonal/admission.md`) and support calls for real,
matched-gene and decoy predictions (`results/ledger/support.tsv`, `false_support.tsv`, `support_sources.tsv`).

**S6 Table. Curation-lag audit and recall probes.** `results/audit/curation_lag_audit.tsv`,
`results/audit/recall_probe_random50.tsv`, `results/m7/recall_probe_90.tsv`.

**S7 Table. Blind literature screen and blinded judging.** Agent L evidence (`results/m7/L/`), statements and answer key
(`results/m7/statements.tsv`, `answer_key_slots.tsv`), judge packets, scores and analyses (`results/m7/judge/`).

**S8 Table. Deviations and hold-out looks.** `DEVIATIONS.md` and `LOOKS.md`.

**S1–S10 Reports. Candidate reports.** `reports/ANKRD52.md` (with `ANKRD52_experiments.md`), `reports/TRAPPC5.md` (with
`TRAPPC5_experiments.md`), `reports/RBM34.md`, `reports/PLEKHH3.md`, `reports/CCDC71L.md`, `reports/TM2D2.md`,
`reports/TM2D1.md`, `reports/C5orf34.md`, `reports/BICRAL.md`, `reports/INAFM1.md`; red-team reviews in
`reports/redteam/`; machine-generated evidence bundles in `reports/data/`.

**S1 Text. Frozen study design.** `DESIGN.md` v2.3 (tag `design-frozen`) and design reviews (`reviews/`).

**S1 Data. Figure source data.** `manuscript/figures/source_data/`.
