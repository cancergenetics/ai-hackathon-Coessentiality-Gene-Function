
# Introduction

A large part of the human protein-coding genome still has no experimentally established function. Research attention
is concentrated and self-reinforcing: a small minority of genes accounts for half of all publications, and the genes
studied today are mostly those that were studied first [Stoeger2018; Stoeger2022; Pandey2014; Edwards2011].
Annotation resources inherit this imbalance [Haynes2018], and even in well-studied organisms about 20%
<!-- src: LITERATURE.md --> of proteins lack an informative functional description [Wood2019]. Calls to close the gap
ask for agreed measures of what is "understudied" and for systematic data that link unknown proteins to known biology
[Kustatscher2022; Oprea2018; Rocha2023]. No single measure is canonical. Experimental Gene Ontology (GO) evidence
[GO2023], the UniProt annotation score [UniProtHelp_AnnotationScore; UniProt2025] and literature-attention labels such
as the IDG "Tdark" class [Oprea2018; Sheils2021] each capture a different aspect of knownness, and each lags the
literature by a different amount. Any list of "uncharacterised" genes therefore contains some genes whose function is
already published [Kang2016; Callegari2016; Stroud2016].

Genome-scale CRISPR knockout screens offer one route to such links. The Cancer Dependency Map (DepMap) measures the
fitness effect of knocking out each gene in more than 1,000 <!-- src: results/assessability/splithalf_runs.md (1,361 lines in 26Q3) -->
cancer cell lines, with models that correct for copy number and screen dynamics [Tsherniak2017; Meyers2017;
Dempster2021]. Genes whose loss affects the same cell lines, that is co-essential genes, tend to act in the same complex
or pathway [Pan2018; Boyle2018; Kim2019; Wainberg2021]. Co-essentiality has proposed or supported functions for several
genes that were uncharacterised a few years ago: SLC25A51 as a mitochondrial NAD⁺ transporter [Kory2020; Luongo2020;
Girardi2020], C12orf49/SPRING1 in SREBP processing [Kim2019; Bayraktar2020; Loregger2020; Aregger2020], TMEM189/PEDS1
as the plasmalogen desaturase and C15orf57/CCDC32 in AP-2-mediated endocytosis [Wainberg2021; GallegoGarcia2019;
Werner2020], C16orf72/HAPSTR1 in stress signalling [Amici2022], C14orf80 and C16orf59 (TEDC1/2) with δ/ε-tubulin
[Pan2018], and C7orf26/INTS15 as an Integrator subunit [Pan2022; Offley2023]. Network construction has also improved,
through covariance whitening and generalised least squares (GLS) [Wainberg2021; Gheorghe2022], dimensionality reduction
and normalisation [Hassan2023; Pan2022]; related balancing of correlation networks has been developed for predicting
gene buffering [Rohde2025]. The method used here, zavg_BEF, averages three label-free views of the DepMap gene-effect
matrix: whitened profile similarity, overlap of genome-wide partner lists, and proximity in a graph embedding. On
co-complex pairs held out from its development it ranked pairs better than GLS [Coessentiality_tool]. We treat it as one
implementation of co-essentiality and compare it throughout with GLS and Pearson correlation, so that the results
speak to co-essentiality rather than to one tool. Besides shared dependency, DepMap also records co-*advantage*: pairs
of genes whose knockout increases fitness in the same cell lines, as expected for members of one growth-restraining
pathway.

Co-essentiality is now one of several genome-scale sources of function for uncharacterised genes. Genome-scale
Perturb-seq groups genes by the transcriptional consequences of their knockdown and placed C7orf26 in Integrator
[Replogle2022]; affinity-purification and cell-imaging maps such as hu.MAP 3.0 and OpenCell assign proteins to complexes
and compartments [Fischer2025; Cho2022]; proteome-wide AlphaFold screens propose direct interactions [Burke2023;
Schmid2025]; phylogenetic modelling now propagates function to most human genes [Feuermann2025]; and machine-learning
GO predictors are benchmarked in the CAFA challenges [Zhou2019]. A useful evaluation of co-essentiality must therefore
ask what it adds to these sources, especially to homology and physical interaction data, and not only whether it beats
chance.

Four things are missing before co-essentiality predictions for uncharacterised genes can be used with known confidence.

**Pre-registration.** In most studies the set of genes treated as uncharacterised, and the rules for accepting a
prediction, were chosen with the network in view. Undisclosed analytic flexibility inflates apparent effects, and
pre-registration is the standard guard against it [Simmons2011; Nosek2018]. We found no co-essentiality study that fixed
its list of target genes before computing any gene–gene quantity.

**Temporal validation.** Predictors are usually checked by leave-one-out recovery of current annotations or of known
complexes. These checks are vulnerable in three ways. First, current annotations can be circular: experimental GO
annotations for CCDC32 cite the co-essentiality paper that proposed its function [Wainberg2021], and integrated
networks used as "independent" support already contain DepMap data [KimCY2022; Schmid2025]. Second,
guilt-by-association performance often reflects node degree and multifunctionality rather than specific edges
[Gillis2011; Gillis2012]. Third, a few large complexes dominate the strongest DepMap correlations; ETC complex I and the
mitoribosome supplied about 76% <!-- src: LITERATURE.md --> of true-positive pairs at precision 0.5
<!-- src: LITERATURE.md --> in one benchmark [Rahman2021]. The test that matches how predictions are used is
prospective in form: take genes that were uncharacterised at a past date, predict their function without the
annotations added since, and score the predictions against those later annotations. This is the design of the Critical
Assessment of Functional Annotation (CAFA) [Radivojac2013; Jiang2016; Zhou2019], made possible by archived GO releases
[GO_archive_web]. Benchmarks of co-essentiality networks have scored them against current reference annotations or
complexes [Rahman2021; Hassan2023], and genetic-interaction maps have been compared with them [Billmann2026]; in the
studies we reviewed we did not find a time-split test of co-essentiality function predictions against later
experimental annotation.

**Calibration.** Co-essentiality scores are ranking scores, not probabilities [Coessentiality_tool]. An experimentalist
choosing which prediction to test needs to know how often a prediction of a given strength turns out to be right, and a
reader of a catalogue needs to know how many of its entries are expected to be correct. Neither can be read from a rank
or an enrichment p-value; both need a model fitted against an external outcome and checked out of sample.

**An honest census.** Many uncharacterised genes are poor subjects for co-essentiality. They are less often essential,
often not expressed in cancer cell lines, and often buffered by paralogues [Dede2020; DeKegel2019]. A flat knockout
profile carries no co-essentiality information, however the network is built. Genes in tandem clusters are exposed to proximity and
copy-number artefacts, because Cas9 cutting causes chromosome-arm truncations and amplified regions give correlated
effects [Lazar2024; Meyers2017; Kim2019]. The fraction of the uncharacterised genome to which co-essentiality can speak
at all is rarely reported, so the reach of the approach is hard to judge.

Here we apply zavg_BEF, with GLS and Pearson as comparators, to DepMap CRISPR gene effects to predict functions for a pre-registered list of uncharacterised
human genes, and we address the four gaps directly. The list was built from annotation data alone and frozen, together
with the full analysis design, under a cryptographic hash and git tags before any pairwise DepMap quantity was computed.
The design fixed four claims, and the decision rule for each, before the analyses that test them; each claim is reported
whichever way it falls.

- **C1, census.** The fraction of the pre-registered genes that is scorable in DepMap, expressed in the screened cell
  lines, and assessable, meaning that its co-essentiality neighbourhood is reproducible across independent halves of the
  cell lines beyond what profile-matched genes achieve, reported by stratum.
- **C2, accuracy and calibration.** On a temporal hold-out of genes that were uncharacterised in the GO release of July
  2018 <!-- src: DESIGN.md --> and gained experimental annotations since, the precision of the top predicted term
  against a prior-only predictor and a matched-gene null (the primary test) and against GLS (key secondary), together
  with the calibration of a pre-specified probability model and the recovery of named positive controls.
- **C3, catalogue.** Calibrated predictions for every assessable pre-registered gene, headlined by the expected number of
  top-term predictions that would be confirmed if every gene gained new experimental annotation (a conditional
  quantity), with false-call rates from non-expressed genes and from
  matched-gene and decoy predictions.
- **C4, candidates.** A short list of top candidates, each with a literature check, a blinded comparison against decoy
  statements, a stated relationship type and alternative explanations, and a tiered experimental plan.

Orthogonal datasets (physical interaction, co-abundance, localisation, perturbation and structure data) entered only
through a pre-specified support test, and only if they recovered known complexes on genes outside the uncharacterised
list. The main contribution is the evaluation standard (pre-registration, a temporal hold-out, calibration and
circularity control) rather than a new predictor. The study was planned and run by a team of AI agents under a
human-specified goal; the safeguards this required, and their gaps, are part of the Methods and are assessed in the
Discussion. After peer review we added analyses requested by the referees; they are labelled [post-review exploratory]
and change no pre-specified result.
