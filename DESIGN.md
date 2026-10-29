# DESIGN.md — v0 (PI draft, pre-review; to be revised with LITERATURE.md)

## 0. Fixed goal (from PROMPT.md; not negotiable)
Use the co-essentiality tool (zavg_BEF, commit 3c684c9) on DepMap CRISPR screens (26Q3 Chronos) to propose putative
functions for **pre-registered uncharacterised human genes**; use orthogonal datasets to reinforce/downweight; do
comprehensive literature checks and propose experiments for the best predictions; deliver a reviewed paper with
figures and references, per-candidate reports, and REPORT.md.

## 1. Pre-registration of uncharacterised genes (before any network computation)  [details TBD from LITERATURE.md]
- Universe: HGNC Approved protein-coding genes. Report how many are measured in DepMap 26Q3 (column presence only — not
  network analysis); genes not measured are listed but cannot be characterised by the tool.
- Candidate criteria (objective, scriptable, versioned inputs): absence of informative experimental GO annotation;
  low focused-publication count (gene2pubmed); low UniProt annotation score; optional Unknome knownness.
- Output: `preregistration/uncharacterised_genes.tsv` + criteria document; committed, SHA-256 recorded in
  RESEARCH_TREE.md **before** the tool is run on DepMap data.

## 2. Tool verification (M4)
- Run tool's own toy tests; reproduce a published number (hu.MAP train-pair AP) to confirm correct installation.
- Our own toy test: planted modules in synthetic gene-effect matrix → method must recover them; null matrix → no
  enrichment beyond nominal rates.

## 3. Calibration on characterised genes (M5) — how much should we trust a neighbourhood?
- Leave-one-gene-out GO prediction from co-essential neighbours for characterised genes; compare zavg_BEF vs GLS vs
  Pearson and vs a term-prevalence (multifunctionality) null.
- Temporal hold-out: genes "uncharacterised" by the same criteria at an archived GO release (T0), annotated since →
  were their new terms predicted? Flag annotations derived from co-essentiality papers (circularity).
- Per-gene informativeness: split-half (cell lines) reproducibility of each gene's neighbour list, seeds 0–4.
- Output: empirical precision as a function of evidence strength → confidence tiers for predictions.

## 4. Hypothesis generation for pre-registered genes (M6)
- For each pre-registered gene: neighbour ranking by zavg_BEF; GO/complex/pathway enrichment of top neighbours with a
  degree/annotation-preserving null; complex membership via hu.MAP/CORUM neighbours.
- Confounder flags: genomic proximity of neighbours (CN artefacts), paralogs, low-variance/noise profiles,
  lineage-restricted signals.

## 5. Orthogonal evidence (M6)
- Pre-specified per-source support rule, with positive (known co-complex pairs) and negative (random pairs) controls
  measured before use. Sources: BioPlex, hu.MAP, OpenCell, HuRI, BioGRID physical, CCLE co-abundance, HPA/OpenCell/
  HCM localisation, Perturb-seq, chemogenomic screens, DEMETER2, STRING without text-mining.

## 6. Prioritisation and literature validation (M7)
- Composite pre-specified ranking; top N to blinded literature review: literature summary written blind to our
  prediction; separate judge compares real vs decoy predictions (randomised order) → support rate vs decoy.
- Per-candidate reports with proposed experiments.

## 7. Reproducibility
Seeds `config/seeds.yaml`; data `DATA.md`; scripts numbered; all results committed; any result reviewed by an agent
that did not produce it.
