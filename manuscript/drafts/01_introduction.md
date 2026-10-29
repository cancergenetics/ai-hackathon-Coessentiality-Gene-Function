# Introduction

<!-- Draft 1 (scientific writer). Citations are keys of references/literature_refs.tsv. Every number carries a
src comment. Claims C1–C4 are stated without results (DESIGN.md v2.3 §0). -->

A large part of the human protein-coding genome still has no experimentally established function. Research attention
is concentrated and self-reinforcing: a small minority of genes accounts for half of all publications, and the genes
studied today are mostly those that were studied first [Stoeger2018; Stoeger2022; Pandey2014; Edwards2011].
Annotation resources inherit this imbalance [Haynes2018], and even in well-studied organisms about 20% <!-- src: LITERATURE.md -->
of proteins lack an informative functional description [Wood2019]. Calls to close this gap ask for agreed measures
of what is "understudied" and for systematic data that link unknown proteins to known biology [Kustatscher2022;
Oprea2018; Rocha2023]. No single measure is canonical. Experimental Gene Ontology (GO) evidence [GO2023], the UniProt
annotation score [UniProtHelp_AnnotationScore; UniProt2025] and literature-attention labels such as the IDG
"Tdark" class [Oprea2018; Sheils2021] each capture a different aspect of knownness. Each also lags the literature by
a different amount, so any list of "uncharacterised" genes contains some genes whose function is already published
[Kang2016; Callegari2016; Stroud2016].

Genome-scale CRISPR knockout screens give one route to such links. The Cancer Dependency Map (DepMap) measures the
fitness effect of knocking out each gene in more than 1,000 <!-- src: results/assessability/splithalf_runs.md (1,361 lines in 26Q3) --> cancer cell lines, with
models that correct for copy number and screen dynamics [Tsherniak2017; Meyers2017; Dempster2021]. Genes whose loss
affects the same cell lines, that is co-essential genes, tend to act in the same complex or pathway [Pan2018;
Boyle2018; Kim2019; Wainberg2021]. Co-essentiality has proposed or supported functions for several genes that were
uncharacterised a few years ago: SLC25A51 as a mitochondrial NAD⁺ transporter [Kory2020; Luongo2020; Girardi2020],
C12orf49/SPRING1 in SREBP processing [Kim2019; Bayraktar2020; Loregger2020; Aregger2020], TMEM189/PEDS1 as the
plasmalogen desaturase and C15orf57/CCDC32 in AP-2-mediated endocytosis [Wainberg2021; GallegoGarcia2019; Werner2020],
C16orf72/HAPSTR1 in stress signalling [Amici2022], C14orf80 and C16orf59 (TEDC1/2) with δ/ε-tubulin [Pan2018], and
C7orf26/INTS15 as an Integrator subunit [Pan2022; Offley2023]. Network construction has also improved, through
covariance whitening and generalised least squares (GLS) [Wainberg2021; Gheorghe2022], dimensionality reduction and
normalisation [Hassan2023; Pan2022] and per-gene balancing [Rohde2025]. The method used here, zavg_BEF, averages three
label-free views of the DepMap gene-effect matrix: whitened profile similarity, overlap of genome-wide partner lists,
and proximity in a graph embedding. On co-complex pairs held out from its development it ranked pairs better than GLS
[Coessentiality_tool].

Four things are missing before co-essentiality predictions for uncharacterised genes can be used with known
confidence.

**Pre-registration.** In most studies the set of genes treated as uncharacterised, and the rules for accepting a
prediction, were chosen with the network in view. Flexible choices made after the data are seen make results look
better than they are. We found no co-essentiality study that fixed its list of target genes before computing any
gene–gene quantity.

**Temporal validation.** Predictors are usually checked by leave-one-out recovery of current annotations or of known
complexes. These checks are vulnerable in three ways. First, current annotations can be circular: experimental GO
annotations for CCDC32 cite the co-essentiality paper that proposed its function [Wainberg2021], and integrated
networks used as "independent" support already contain DepMap data [KimCY2022; Schmid2025]. Second,
guilt-by-association performance often reflects node degree and multifunctionality rather than specific edges
[Gillis2011; Gillis2012]. Third, a few large complexes dominate the strongest DepMap correlations; ETC complex I and
the mitoribosome supplied about 76% <!-- src: LITERATURE.md --> of true-positive pairs at precision 0.5 <!-- src: LITERATURE.md --> in one
benchmark [Rahman2021]. The test that matches how predictions are used is prospective in form. It takes genes that
were uncharacterised at a past date, predicts their function without the annotations added since, and scores the
predictions against those later annotations. This is the design of the Critical Assessment of Functional Annotation
(CAFA) [Radivojac2013; Jiang2016; Zhou2019]. Archived GO releases make it possible [GO_archive_web]. To our knowledge
it has not been applied to co-essentiality function prediction.

**Calibration.** Co-essentiality scores are ranking scores, not probabilities [Coessentiality_tool]. An experimentalist
choosing which prediction to test needs to know how often a prediction of a given strength turns out to be right, and
a reader of a catalogue needs to know how many of its entries are expected to be correct. Neither can be read from a
rank or an enrichment p-value. Both need a model fitted against an external outcome and checked out of sample.

**An honest census.** Many uncharacterised genes are poor subjects for co-essentiality. They are less often essential,
often not expressed in cancer cell lines, and often buffered by paralogues [Dede2020; DeKegel2019]. A flat
knockout profile carries no network information [Billmann2026]. Genes in tandem clusters are exposed to proximity and
copy-number artefacts, because Cas9 cutting causes chromosome-arm truncations and amplified regions give correlated
effects [Lazar2024; Meyers2017; Kim2019]. The fraction of the uncharacterised genome to which co-essentiality can speak
at all is rarely reported, so the reach of the approach is hard to judge.

In this study we apply zavg_BEF to DepMap CRISPR gene effects to predict functions for a pre-registered list of
uncharacterised human genes, and we address the four gaps directly. The list was built from annotation data alone and
frozen, together with the full analysis design, under a cryptographic hash and git tags before any pairwise DepMap
quantity was computed. The design fixed four claims, and the decision rule for each, before the analyses that test
them. Each claim is reported whichever way it falls.

- **C1, census.** The fraction of the pre-registered genes that is scorable in DepMap, expressed in the screened cell
  lines, and assessable, meaning that its co-essentiality neighbourhood is reproducible across independent halves of
  the cell lines beyond what profile-matched genes achieve. The fraction is reported by stratum, including
  chemosensory and tandem-cluster families.
- **C2, accuracy and calibration.** On a temporal hold-out of genes that were uncharacterised in the GO release of
  July 2018 <!-- src: DESIGN.md --> and gained experimental annotations since, the precision of the top predicted term compared
  with a prior-only predictor and a matched-gene null (the primary test) and with GLS (key secondary), together with
  the calibration of a pre-specified probability model and the recovery of named positive controls.
- **C3, catalogue.** Calibrated predictions for every assessable pre-registered gene. The headline is the expected
  number of top-term predictions that later annotation would confirm, with a confidence interval, together with
  false-call rates from non-expressed genes and from matched-gene and decoy predictions.
- **C4, candidates.** A short list of top candidates. Each has a literature check, a blinded comparison against decoy
  statements, a stated relationship type and alternative explanations, and a tiered experimental plan.

Orthogonal datasets enter only through a pre-specified support test. Physical interaction, co-abundance,
localisation, perturbation and structure data are admitted as evidence only if they recover known complexes on genes
outside the uncharacterised list. The study was planned and run by a team of AI agents under a human-specified goal.
The safeguards this required (hash gating, a one-look rule for the hold-out, blinded roles, and independent
re-derivation of key numbers) are part of the Methods.
