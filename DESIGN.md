# DESIGN.md — v1 (PI draft for review round 1)

Status: draft for review. Revision log at the bottom. Sections marked **[PRE-SPECIFIED]** are frozen once the design is
accepted; any later change is logged with reason and date, and results are reported under both the frozen and the
changed rule.

## 0. Fixed goal (PROMPT.md; not negotiable)
Use the co-essentiality tool (zavg_BEF; github.com/cancergenetics/ai-hackathon-Coessentiality @ 3c684c9, used read-only)
on DepMap CRISPR screens (Public 26Q3 Chronos `CRISPRGeneEffect.csv`) as the **primary hypothesis generator** for the
functions of a **pre-registered list of uncharacterised human genes**. Orthogonal datasets may reinforce or downweight
predictions. For the most promising predictions: comprehensive literature search (what is known; does it support us)
and proposed experiments. Deliverables: reviewed paper (abstract, introduction, methods, results, discussion, figures,
full references), per-candidate reports, REPORT.md.

Scope decision: calibration on *characterised* genes (§3) is in scope only as a means to attach honest confidence to
predictions for the pre-registered genes; no function is proposed for any gene outside the pre-registered list.

## 1. Pre-registration of uncharacterised genes **[PRE-SPECIFIED]**
Inputs (versions/checksums in DATA.md): HGNC complete set (file dated 2026-04-23), GO current (ontology 2026-07-26,
goa_human GAF generated 2026-05-21), UniProt 2026_03, NCBI gene2pubmed (2026-10-29), TCRD/Pharos TDL (2023 mapping),
DepMap 26Q3 header (column names only). Feature table: `results/preregistration/gene_knownness_features.tsv`
(`scripts/02_gene_knownness_table.py`).

- **Universe**: HGNC Approved, locus_group "protein-coding gene" (19,296 genes).
- **D1 (primary, "no experimental functional annotation")**: zero informative GO BP or MF terms supported by
  low-throughput experimental (EXP, IDA, IPI, IMP, IGI, IEP) or author/curator (TAS, IC) evidence, NOT-qualified rows
  excluded; IPI/IDA to generic binding terms (protein binding GO:0005515, binding, identical protein binding, protein
  homodimerization activity, ontology roots; full list in the script README) do not count. High-throughput codes
  (HTP, HDA, HMP, HGI, HEP), IEA, ISS/ISO/ISA/ISM, IBA/IBD/IKR/IRD, RCA, NAS, ND are ignored. CC-only annotation does not
  count as functional.
- **D2**: UniProt (Swiss-Prot) annotation score ≤ 2 (max over the gene's reviewed entries; Wainberg et al. 2021 definition).
- **D3 ("low literature attention")**: ≤ 10 "focused" PubMed records in gene2pubmed (PMIDs linked to ≤ 10 human genes)
  **or** IDG Tdark.
- **Pre-registered set U = D1 ∩ (D2 ∪ D3)**. Genes not in DepMap 26Q3 stay in U but are reported as "not scorable".
- Sensitivity sets reported (not used for selection): D1, D2, D3 alone and pairwise overlaps.
- **Curation-lag audit**: an agent with no access to network outputs audits a random sample of 50 U genes (seed 0) by
  literature search and classifies each as truly uncharacterised / partially characterised / characterised-but-uncurated.
  Audit results are reported; **no gene is removed from U** (the list stays as registered); audit flags are carried into
  the candidate reports.
- **Freeze**: `preregistration/uncharacterised_genes.tsv` + `preregistration/CRITERIA.md` committed; SHA-256 and commit
  hash recorded in RESEARCH_TREE.md **before the tool is run on DepMap data** (enforced: the run scripts refuse to run
  unless the registered file exists with the recorded hash).

## 2. Tool installation check and verification (M4)
- Tool toy tests (done: 16 passed, 2 skipped needing the authors' cache).
- **Reproduction**: run the tool's `predict_pairs` on the hu.MAP 3.0 train pairs and confirm the published dev-scale
  numbers (AP on train pairs) within tolerance — this confirms correct installation on 26Q3; the run touches only
  labelled known pairs, not U.
- **Our toy test**: synthetic gene-effect matrix (n lines ≈ 300, n genes ≈ 2,000) with planted modules of sizes 3–30,
  a shared nuisance factor (lineage), and planted "proximity" blocks; the full pipeline (tool → neighbour enrichment →
  tiers) must recover planted module labels for held-out module members and must give nominal false-positive rates on a
  null matrix with no modules. Known-answer checks for the enrichment statistics.
- Implementation: we call the tool's Python API (`coessential.method.CoessentialityModel`) without modifying it; we
  compute the full gene × gene zavg_BEF matrix (and z_B, z_E, z_F; GLS and Pearson baselines from the tool).

## 3. Calibration on characterised genes (M5) **[PRE-SPECIFIED]**
Purpose: estimate how often a neighbourhood-based functional prediction is right, as a function of measurable evidence
strength, so that U predictions carry calibrated confidence.

**Annotation vocabularies** (prediction targets):
- V1 (primary; matches the tool's training signal): protein complexes — Complex Portal human (current), GO CC terms
  descending from "protein-containing complex" (GO:0032991) with experimental evidence, and hu.MAP 3.0 complexes
  (flagged: partially dependent, the tool was tuned on hu.MAP 3.0 train pairs).
- V2 (secondary): GO BP and MF, experimental evidence (as D1), propagated to ancestors (true-path rule), terms with
  5–300 annotated scorable genes; Reactome pathways (lowest-level, 5–300 genes).

**Predictor (single, pre-specified)**: for query gene g, neighbours N(g) = top K = 25 genes by zavg_BEF (excluding g,
excluding genes not in background). Term score S(g,t) = Σ_{j∈N(g), j annotated t} max(z_gj, 0). Term p-value: one-sided
hypergeometric of |N(g) ∩ t| vs the scorable annotated background; BH-FDR within gene. Ranked list per gene = terms by
S, ties by p. (K = 25 is fixed a priori; K = 10 and 50 reported as sensitivity.)

**Benchmarks** (all on genes NOT in U):
1. Leave-one-gene-out (the query's own annotations are not used for its neighbours' labels — trivially true — and the
   query is removed from term backgrounds): per-gene AUPRC and precision@1/@3 of ranked terms vs the gene's own
   annotations; macro-averaged over genes and over terms.
2. **Temporal hold-out (primary validation)**: t0 = GO release 2018-07-02. Hold-out genes H = genes meeting D1 at t0 and
   ≤ 10 focused PubMed records with PMID < cut-off for 2018-07 (PMID-number date proxy), that have ≥ 1 new informative
   experimental BP/MF term (or complex) in the current release. Targets: the terms acquired since t0. Network
   annotations used for prediction: t0 release only. Named subset: literature positive controls (SPRING1, PEDS1, CCDC32,
   INTS15, HAPSTR1, SLC25A51, TEDC1, TEDC2, POU2AF2, POU2AF3, TMEM242; weaker: FIRRM, AIRIM, TMEM41B).
   Circularity: new annotations whose supporting PMIDs are co-essentiality/DepMap papers (blacklist compiled from
   LITERATURE.md before scoring) are reported separately; primary metric excludes them.
3. **Comparators**: GLS and Pearson (same predictor, tool's implementations); **prior-only null** (rank terms by
   annotation frequency — multifunctionality baseline, Gillis & Pavlidis 2011); **matched-gene null** (replace g by a
   gene matched on mean effect, SD and NaN fraction — 5 matches, seeds 0–4).
4. **Confidence model**: precision@1 of the top term as a function of (i) the top-K mean zavg_BEF of g, (ii) split-half
   reproducibility of N(g) (§4.2), binned; isotonic fit on benchmark 1, checked on benchmark 2. Output: calibrated
   probability that the top-ranked term is a correct annotation.

Primary success criterion for using the tool on U: on the temporal hold-out, zavg_BEF precision@1 exceeds both the
prior-only and matched-gene nulls (paired bootstrap over genes, 95% CI excludes 0). Reported whichever way it falls.

## 4. Hypothesis generation for U (M6) **[PRE-SPECIFIED]**
4.1 Same predictor as §3 on V1 and V2, using current annotations, for every scorable U gene. Also report the top-10
named co-essential partners with their zavg_BEF, annotations, and flags.
4.2 **Assessability**: split-half reproducibility — split cell lines randomly in halves (seeds 0–4), run the tool on each
half, compute Jaccard/RBO overlap of top-25 neighbours of g across halves; genes whose mean overlap is below the 95th
percentile of the matched-gene null overlap are "not assessable" (no prediction made, not "negative").
4.3 **Artefact controls** (each prediction must survive): (a) recompute after removing neighbours on the same
chromosome arm (Ensembl coordinates/HGNC cytoband); (b) paralog flag (Ensembl 116) for top partners; (c) MitoCarta /
large-complex stratification — report predictions by compartment and compare the U prediction distribution against the
matched-gene null distribution; (d) low-coverage genes (NaN ≥ 10%) flagged; (e) lineage-restricted signal check: does
the top-partner correlation persist after removing the most dependent lineage?
4.4 **Clustering view**: communities in the zavg_BEF kNN graph (Leiden/Louvain, seed 0, resolution fixed a priori; seeds
1–4 for stability) to report U genes embedded in coherent modules; descriptive only.

## 5. Orthogonal evidence **[PRE-SPECIFIED rules, set before viewing U predictions]**
Independent classes (data obtained; see DATA.md): (P) physical — BioPlex 3.0 (293T, HCT116), OpenCell (2022),
BioGRID 5.0.262 low-throughput physical, STRING v12.5 *experiments* channel only, Human Cell Map SAINT bait–prey;
hu.MAP 3.0 flagged partially dependent (tool tuned on its train pairs; hu.MAP also integrates BioPlex). HuRI could not
be downloaded (host unreachable) — HuRI edges partly present in BioGRID. (A) co-abundance — CCLE proteomics (Nusinow
2020; shares cell lines with DepMap, flagged), ProteomeHD (Kustatscher 2019; independent). (L) localisation — HPA v25.1,
OpenCell, Human Cell Map NMF/SAFE. (G) other perturbation — DEMETER2 co-dependency, genome-wide Perturb-seq (Replogle
2022, K562 GW + RPE1/K562 essential pseudo-bulk) profile similarity, chemogenomic profile similarity (Olivieri 2020
NormZ; BioGRID ORCS drug-exposure screens with DepMap/Avana-type screens removed). (S) structure — Burke 2023 AF2 pDockQ
(pre-selected pairs; coverage limited). Excluded for circularity: HumanNet, SPOC/Predictomes (uses DepMap as a feature;
reported only as an external comparison), STRING text-mining/database/co-expression channels.
- Pair-level support rule per continuous source: similarity ≥ 95th percentile of random-pair distribution; binary
  sources: edge present. Each source's sensitivity is first measured on known co-complex pairs (positive control) and
  random pairs (negative control); sources with no enrichment are dropped (reported).
- Prediction-level support: observed number of supported (g, partner-in-predicted-term) pairs vs the expectation from
  matched random partners; class supports the prediction if one-sided p < 0.05. Localisation supports if g's compartment
  matches the predicted term's dominant compartment; **contradiction** (e.g. nuclear-only protein predicted in a
  mitochondrial matrix complex) downweights.

## 6. Prioritisation, literature validation, experiments (M7) **[PRE-SPECIFIED]**
- **Tier A**: assessable; calibrated P(top term correct) ≥ 0.5; survives same-arm removal; no paralog-only support;
  ≥ 1 orthogonal class supports, none contradicts. **Tier B**: calibrated ≥ 0.3 or orthogonal-only shortfall. Rank
  within tier by calibrated probability, then number of supporting classes.
- Top 20 (Tier A first) go to literature deep-dives with **blinded judging**: agent L (blind to our prediction) writes
  what is known about the gene (all symbols/aliases, PubMed, Europe PMC incl. preprints); agent J sees L's summary and
  two candidate function statements in random order — our prediction and a **decoy** (the prediction for a different U
  gene, matched on compartment class where possible) — and classifies each as supported / contradicted / unaddressed.
  Primary literature-validation metric: support rate of real vs decoy (paired). Then unblinded deep-dive.
- Per-candidate report (top ~8–10): evidence chain, partners, orthogonal support, literature, novelty, alternative
  explanations, and proposed experiments (e.g. tagged-protein localisation, IP-MS/proximity labelling, CRISPR KO with
  complex-specific readouts, epistasis with predicted partners, rescue).
- External benchmarks (agreement only, never tuning): Wainberg 2021's 108 predictions; hu.MAP 3.0 uncharacterised-protein
  hypotheses.

## 7. Statistics
BH-FDR for multiple testing; bootstrap CIs (genes resampled; 1,000 replicates, seed 0); seeds [0,1,2,3,4]
(`config/seeds.yaml`). All thresholds above are fixed before U predictions are computed.

## 8. Compute
Full gene × gene matrices (≈18.4k²; float32 ≈1.35 GB each) for zavg_BEF, components, GLS, Pearson; ≈2–3 min per tool run
on the 24 GB laptop; split-half: 10 extra runs. Matrices are git-ignored; summaries committed.

## 9. AI-agent failure-mode safeguards
Pre-registration hash gate; agents never read predictions outside their task; hallucinated references blocked by
Crossref/PubMed verification of every citation; blinded literature judging with decoys; independent re-implementation
check of key numbers (one agent computes, another re-derives from raw outputs); toy tests with known answers; no metric,
control or label changed after seeing results (any change logged and both versions reported); research tree as memory.

## 10. Deliverables
`manuscript/` (paper + figures + references), `reports/<GENE>.md` per top candidate, REPORT.md, LESSONS.md, tree.

## Revision log
- v0 (2026-10-29): skeleton. v1 (2026-10-29): criteria and analyses specified from LITERATURE.md §3.4/§4/§6.
