# DESIGN.md — v2 (after review round 1)

Sections marked **[PRE-SPECIFIED]** are frozen at acceptance (git tag `design-frozen`). Any later change is logged in
the revision log with reason and date, and affected results are reported under both the frozen and the changed rule.
Round-1 reviews: `reviews/round1_*.md`; disposition of every item: `reviews/round1_disposition.md`.

## 0. Goal, claims and decision branches

**Fixed goal (PROMPT.md).** Use the co-essentiality tool (zavg_BEF; github.com/cancergenetics/ai-hackathon-Coessentiality
@ 3c684c9, read-only) on DepMap Public 26Q3 CRISPR Chronos gene effects as the primary hypothesis generator for the
functions of a pre-registered list of uncharacterised human genes; orthogonal data reinforce/downweight; literature
checks and experiments for the best predictions; reviewed paper, per-candidate reports, REPORT.md.
Scope rule: work on characterised genes (§3) only calibrates confidence; no function is proposed for genes outside U.

**Pre-specified claims [PRE-SPECIFIED]** (each with its metric; reported whichever way they fall):
- **C1 Census** — fraction of U that is scorable, expressed and assessable (§4.2), by stratum (§1.4).
- **C2 Accuracy & calibration** — temporal hold-out (§3): precision@1 of zavg_BEF vs prior-only and matched-gene nulls
  (primary), vs GLS/Pearson (key secondary), calibration error, named positive-control recovery.
- **C3 Catalogue** — calibrated predictions for assessable U genes; headline = expected number of correct top
  predictions Σ p_cal (with cluster-bootstrap CI), not a count of "hits"; plus false-positive rate estimated from
  non-expressed U genes (§4.2) and matched-gene/decoy runs (§5.4).
- **C4 Candidates** — literature-checked, blinded-judged top candidates with relationship type, alternative
  explanations and tiered experiments.

**Decision branches [PRE-SPECIFIED]**
- If the C2 primary fails (zavg_BEF not better than both nulls): no calibrated claims for U; the paper reports C1, C2
  and the top candidates as unranked hypotheses labelled "uncalibrated".
- If calibration on H is poor (calibration-slope 95% CI excludes 1 *and* ECE CI excludes 0): report p_cal from the
  cross-fitted model only with that caveat; no recalibration beyond the pre-specified model.
- Low-yield branch: if fewer than 10 genes reach Tier A, the paper leads with C1–C2; the top-40 list is filled Tier A,
  then Tier B, then by p_cal, labelled by tier (§6.1). Thresholds are never relaxed post hoc.
- If GLS equals or beats zavg_BEF on the hold-out, this is stated plainly; zavg_BEF remains the pre-specified generator.

## 1. Pre-registration of uncharacterised genes **[PRE-SPECIFIED]**
Inputs (DATA.md): HGNC complete set (2026-04-23), GO (ontology 2026-07-26; goa_human GAF 2026-05-21), UniProt 2026_03,
gene2pubmed (2026-10-29), TCRD TDL (2023), DepMap 26Q3 header and single-gene summaries (§1.4), DepMap 26Q3 expression.

1.1 **Universe**: HGNC Approved, locus_group "protein-coding gene" (19,296).
1.2 **Criteria**, computed by one function `knownness.d1(gaf, obo, release)` used for every release:
- **D1**: zero informative GO BP/MF terms with evidence in {EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC}; NOT rows excluded;
  generic binding terms (GO:0005515, GO:0005488, GO:0042802, GO:0042803, roots; full list in the script) do not count;
  HTP/HDA/HMP/HGI/HEP, IEA, ISS/ISO/ISA/ISM/IGC, IBA/IBD/IKR/IRD, RCA, NAS, ND ignored; CC-only does not count.
- **D2**: UniProt annotation score ≤ 2 (max over reviewed entries).
- **D3**: ≤ 10 focused PubMed records (PMIDs linked to ≤ 10 human genes in gene2pubmed) **or** IDG Tdark.
- **U = D1 ∩ (D2 ∪ D3)**. Exact |U| and |U ∩ DepMap| are written into `preregistration/CRITERIA.md` at freeze
  (annotation-only estimate ≈ 5.2k / 4.6k).
1.3 **No gene is ever removed from U.** Genes without a DepMap column or UniProt mapping are "not scorable".
1.4 **Pre-registered strata** (reporting only; computed at freeze, single-gene data only — no pairwise computation):
- *Family*: chemosensory/epidermal (HGNC groups: olfactory receptors, taste receptors, KRTAP, LCE, …), tandem clusters
  (gene with ≥ 2 Ensembl paralogues within 1 Mb; includes chr19 KZFP clusters), other.
- *Expression*: expressed = log2(TPM+1) ≥ 1 in ≥ 10% of DepMap lines with expression data; else "not expressed".
- *Profile informativeness*: Chronos SD, number of lines with effect < −0.5, NaN fraction (tertiles of SD within U;
  "any-dependency" = ≥ 1% lines < −0.5).
- *Core*: ≤ 3 focused PMIDs **and** Tdark.
- Headline numbers are given for U and for the expressed, non-chemosensory, non-tandem stratum.
1.5 **Curation-lag audit (before any U prediction is computed)**: random 50 U genes (seed 0); an agent with no network
access searches current symbol, previous symbols, aliases (HGNC), UniProt, PubMed, Europe PMC/bioRxiv; classes:
N1 function established / N2 partial / N3 no functional literature. Estimate = expected rediscovery rate for C3.
1.6 **Freeze and gate**: `preregistration/uncharacterised_genes.tsv` + `CRITERIA.md` + `FREEZE.sha256` committed and
tagged `preregistration-v1`; hash and commit recorded in RESEARCH_TREE.md. Until then the tool clone's
`results/predictions/` is excluded by sparse checkout. Every DepMap pairwise script calls `gate.check()` (verifies the
hash and the tag). `scripts/audit_order.py` (run by a fresh agent) checks commit order and file mtimes.

## 2. Infrastructure and verification (M4)
2.1 **Identifier hub** `hgnc_hub.tsv` keyed on hgnc_id: Entrez (DepMap columns, gene2pubmed, BioGRID), UniProt (GO,
hu.MAP, Complex Portal, ProteomeHD, Human Cell Map), Ensembl ENSG (HPA, OpenCell), ENSP via STRING aliases, symbol
only as last resort with collision flags; per-source mapping QC tables (mapped/ambiguous/dropped). No symbol joins
when an ID exists.
2.2 **Tool matrices**: via `coessential.method.CoessentialityModel` API (unmodified); full matrices for zavg_BEF,
z_B, z_E, z_F (float32, git-ignored) with an explicit gene index (hgnc_id). GLS and Pearson full matrices by our own
blockwise implementation, verified against the tool's `Baselines.score` on ≥ 100k random pairs (max abs diff < 1e-4).
Neighbour extraction: diagonal set to −inf, restricted to background genes; assertion tests.
2.3 **Reproduction**: the tool's published internal-test HT-AP (zavg_BEF 0.345, GLS 0.242, Spearman 0.146, Pearson
0.134) recomputed with the tool's evaluate CLI and `results/splits/protein_assignment.csv` (PI authorises reading this
one file; it lists proteins and clusters, not predictions). Tolerance ±0.005.
2.4 **Sign/orientation assertions**: Chronos more negative = more essential (known common essentials have mean < −0.5;
known non-essentials ≈ 0); matrix symmetric; known co-complex pairs (e.g. Integrator, CCT, mitoribosome) score > 3.
2.5 **Toy pipeline test**: synthetic matrix (≈300 lines × 2,000 genes) with planted modules (3–30 genes), a lineage
nuisance factor and planted proximity blocks. Acceptance: held-out module members recover module term at
precision@1 ≥ 0.8 for strong modules; on a null matrix p_emp ~ Uniform (KS p > 0.01), genes with any BH-significant
term ≤ 5%, assessable rate 5% ± 2%; proximity blocks removed by same-arm exclusion.

## 3. Calibration on characterised genes (M5) **[PRE-SPECIFIED]**
3.1 **Predictor** (identical for calibration and U):
- N(g) = top K = 25 background genes by zavg_BEF, **after excluding** g, genes on the same chromosome arm as g, and
  Ensembl paralogues of g (sensitivity: without exclusions; K = 10, 50).
- S(g,t) = Σ_{j∈N(g), j∈t} max(z_gj, 0).
- Candidate rankers (exactly three): R1 raw S; R2 hypergeometric p (n = |N(g) ∩ annotated background|; background =
  scorable genes with ≥ 1 annotation in the vocabulary at the release used, query removed); R3 matched-gene empirical
  p_emp(g,t) = (1 + #{m: S(m,t) ≥ S(g,t)})/(1 + M), M = 500 matched genes (§3.4), ties by S.
- **Ranker choice**: once, on the LOO benchmark (§3.2.1; non-U, non-H genes), by mean reciprocal rank of the first
  correct term (terms 5–200); the chosen ranker is frozen and logged in LOOKS.md before the temporal hold-out is opened.
- A term is reportable only with ≥ 2 supporting partners in N(g). Reported outputs: top term; most specific term among
  the top 5 (ancestors dropped when a descendant is ranked); hypergeometric p is descriptive only.
3.2 **Benchmarks**
1. *LOO* (non-U, non-H scorable genes): ranked terms vs the gene's own current D1-evidence annotations (propagated).
   Used for ranker choice and as a sensitivity calibration only.
2. *Temporal hold-out (primary)*: t0 = GO 2018-07-02. H = scorable genes meeting D1 at t0 (same function, t0 GAF) and
   ≤ 10 focused PMIDs with PMID < 2018-07 cut-off, with ≥ 1 target. Targets T(g) = propagated current D1-evidence BP/MF
   terms minus propagated t0 terms (all propagation and ID mapping with the current obo; alt_id/replaced_by resolved;
   dropped obsolete terms counted), size 5–200 at t0. Neighbour annotations: t0 release only.
   Sensitivity: t0 = 2019-07; ≤ 5 PMIDs. Named controls (descriptive case series): SPRING1, PEDS1, CCDC32, INTS15,
   HAPSTR1, SLC25A51, TEDC1, TEDC2, POU2AF2, POU2AF3, TMEM242; weaker FIRRM, AIRIM, TMEM41B — rank of true term.
3. *Circularity*: every PMID supporting a target annotation is queried in Europe PMC full text for DepMap-derived
   analysis ("DepMap", "co-essential*", "coessential*", "codependen*", "co-dependen*", "Project Achilles"); flagged
   annotations are excluded from the primary analysis and analysed separately; sensitivity of the query reported on
   controls with known discovery route (e.g. CCDC32).
4. *Secondary vocabularies*: V1 complexes = GO CC descendants of GO:0032991 (same archives; hu.MAP excluded);
   V1′ module level = V1 ∪ MitoCarta3.0 pathways ∪ Complex Portal complexes (current only). Reported with and without
   ETC complex I and the mitoribosome, and stratified by membership of hu.MAP 3.0 train proteins (tool-tuning leakage).
3.3 **Comparators**: GLS, Pearson (same predictor); prior-only (t0 term frequencies, same background and size filter);
homology baseline (gene's own t0 IEA/ISS/IBA terms, then frequency); matched-gene null (5 matches per gene).
**Primary test** (intersection–union): paired precision@1 difference zavg_BEF − prior-only > 0 **and** zavg_BEF −
matched-null > 0, each with cluster-bootstrap 95% CI excluding 0. Key secondary: zavg_BEF − GLS (two-sided), by
neighbourhood-size stratum. Also MRR, AUPRC (|T| ≥ 3), precision@1 restricted to terms ≤ 50 genes, size distribution
of top-1 terms per method, and the primary metric on each split-half network.
3.4 **Matched genes**: Mahalanobis on (mean effect, log SD, NaN fraction), caliper 0.2 SD, without replacement;
excluding N(g), same-arm genes and genes annotated to g's targets; balance reported (SMD < 0.1).
3.5 **Unit and resampling**: gene; clusters = connected components linking H genes that share a supporting PMID or
appear in each other's N(g); paired cluster bootstrap, 10,000 replicates (seed 0), percentile and BCa CIs; design
effect reported. |H|, |T| distribution, cluster count and minimum detectable effect computed at freeze (annotation
only) and written into CRITERIA.md; if effective n < 300, the primary is pre-declared underpowered.
3.6 **Covariate shift**: SMDs between H, U and LOO on mean effect, SD, NaN fraction, top-K mean zavg, R(g) (§4.2),
neighbourhood annotation coverage; metrics by signal quintile; U-reweighted estimate (inverse-odds weights from logistic
U-vs-H model, trimmed 1st/99th percentile).
3.7 **Calibration model**: monotone (constrained-sign) logistic regression of hit@1 on top-K mean zavg_BEF, R(g),
neighbourhood annotation coverage, log top-term size and module family (mito / large machinery > 30 subunits / other),
10-fold cluster cross-fitting on H (seeds 0–4 for fold assignment). Reliability diagram, Brier, calibration intercept
and slope with CIs. LOO-fitted model: sensitivity only. U genes with any covariate outside H's 5th–95th percentile get
no p_cal. p_cal = probability that the prediction is confirmed by later annotation (conservative).

## 4. Hypothesis generation for U (M6) **[PRE-SPECIFIED]**
4.1 Predictor §3.1 with current annotations (V2 primary for calibration; V1/V1′ reported for every gene; tiers use the
module-level call). Per gene: top-10 partners with zavg_BEF, z_B/z_E/z_F, GLS rank, annotations, essentiality,
chromosome/distance, paralogue and hub flags, hu.MAP-train membership.
4.2 **Assessability**: split cell lines into halves stratified by OncotreeLineage, keeping each PatientID together
(seeds 0–4); run the tool on each half (genes all-NaN in a half are recorded and treated as not reproducible).
R(g) = mean_s |N_A^s(g) ∩ N_B^s(g)| / K; null R0(g,m) = mean_s |N_A^s(g) ∩ N_B^s(m)| / K over M = 200 matched genes;
assessable if R(g) > 95th percentile of R0(g,·) **and** expressed (§1.4). Non-expressed U genes are scored anyway as a
**negative control**: the rate at which they receive Tier-A-like calls estimates the false-call rate. RBO as sensitivity.
4.3 **Artefact checks**: built in — same-arm and paralogue exclusion. Computed for every reported prediction:
bidirectional-promoter/overlapping/readthrough loci among partners (Ensembl coordinates; TSS < 1 kb, opposite strands);
copy-number co-amplification (correlation of g's effect with partners' CN, OmicsCNGeneWGS); hub-driven calls (> 50% of S
from top-1% in-degree neighbours). For the top 40 only: lineage leave-out, g's dependency vs its own expression and
TF/lineage-marker enrichment of partners (→ relationship type e), TP53-status/p53-axis correlation, DEMETER2
replication (partner correlation in shared lines ≥ 95th percentile of g's random-partner distribution). Not possible
(recorded): shared-sgRNA check and per-guide check (guide maps / guide-level data not available).
4.4 **Relationship type** per prediction: (a) subunit — only with physical, co-abundance or structural support;
(b) assembly/maturation factor; (c) supplier/client; (d) pathway member; (e) lineage/transcriptional programme.
Without type-(a) support the claim reads "functions in / supports module M".
4.5 Clustering of the kNN graph: supplementary figure only.

## 5. Orthogonal evidence **[PRE-SPECIFIED rules, fixed before viewing U predictions]**
5.1 **Classes** (independent of DepMap): (P) physical — BioPlex 3.0, OpenCell, BioGRID low-throughput physical,
STRING experiments channel, Human Cell Map SAINT; (A) co-abundance — ProteomeHD; CCLE proteomics (shared cell lines;
counted but flagged); (L) localisation — HPA v25.1, OpenCell, Human Cell Map NMF; (G) perturbation phenotype —
Perturb-seq (only if g perturbed with significant on-target knockdown), chemogenomic profiles (BioGRID ORCS copy of
Olivieri 2020 + drug screens; DepMap/Avana-type screens excluded); (S) structure — Burke 2023 AF2 (coverage limited);
(H) homology — orthologue experimental function (GO IBA/ISO, reported only). Not counted as independent: hu.MAP 3.0
(tool tuning + integrates BioPlex; reported), DEMETER2 (robustness, §4.3), Predictomes/HumanNet/STRING text-mining,
database and co-expression channels (circular; Predictomes reported only as external comparison).
5.2 **Source admission**: each source's co-complex odds ratio on non-hu.MAP complexes (Complex Portal/GO CC) vs
degree-matched random pairs; kept only if the lower 95% CI > 2 (reported).
5.3 **Four states per class**: not measured / no support / supports / contradicts. Support: g–partner pairs (partners
in the predicted module) exceed degree-matched random partners, empirical p = (1+b)/(1+B), B = 1,000; continuous
sources use per-gene row percentiles; Holm across the classes covering g. Absence of an interaction is never a
contradiction. Contradiction: incompatible localisation from ≥ 2 high-reliability sources (HPA Enhanced/Supported,
OpenCell, Human Cell Map), protein not multi-localised.
5.4 **Diagnostic class by module family** (Tier A needs support from the diagnostic class when measured):
mitochondrial → L or A; nuclear RNA machinery → G (Perturb-seq) or L; ribosome biogenesis/translation → G or L;
DNA replication/repair → G (chemogenomic) or L; ER/Golgi/secretory/lipid → L; centrosome/cilia/mitosis → L or P;
signalling/lineage → P. Empirical false-support rate of the whole rule estimated on matched-gene and decoy predictions
and reported beside the Tier A count.

## 6. Prioritisation, literature validation, experiments (M7) **[PRE-SPECIFIED]**
6.1 **Tiers**: Tier A = scorable, expressed, assessable, p_cal ≥ 0.5 (within support), passes §4.3 built-in checks
and computed flags, diagnostic-class support when measured, no contradiction. Tier B = p_cal ≥ 0.3 or Tier A minus
the diagnostic-support condition. Ranking within tier by p_cal, then supporting classes. Top 40 filled Tier A → Tier B
→ p_cal. At most ⅓ of the top 20 may be OXPHOS/mitoribosome calls (next eligible gene substitutes).
6.2 **LLM recall probe**: before any agent sees network output for a candidate, a fresh, tool-less agent is asked for
the function of each top-40 gene and 40 random U genes (symbol + aliases only); answers are logged; genes the model
"knows" are flagged so predictions cannot be confused with background knowledge.
6.3 **Novelty screen**: for each top-40 gene, agent L (blind to our prediction; no access to network outputs) writes
structured evidence items (claim, source, verbatim span, PMID/DOI, evidence level functional / high-throughput /
mention, DepMap-derived yes/no) and assigns N1/N2/N3.
6.4 **Blinded judging**: a script turns each prediction into a templated statement (module term + relationship type;
no partner names; gene names redacted from L's evidence). Each gene: real statement + 3 decoys (predictions of other U
genes matched on compartment and term size; no overlap with the real term; seed 0), random order. Two independent
judges score +1 supported / 0 unaddressed / −1 contradicted; κ reported; a third adjudicates. DepMap-derived support
counts as unaddressed. Primary: exact one-sided sign-flip test on real − mean(decoy). Secondary: 30 extra U genes
sampled across p_cal bins (support vs p_cal). Pipeline validated first on 10 H genes with known answers; acceptance
fixed now: ≥ 7/10 real supported and ≤ 3/30 decoys supported.
6.5 **Reports**: 8–10 genes, Template A (`reports/TEMPLATE_candidate.md`) with experiment Template B
(`reports/TEMPLATE_experiments.md`) — one decisive falsifiable experiment, expected readouts if right/wrong, DepMap
cell-line selection rule, strongest alternative explanation. Each report gets an unedited red-team review by a separate
agent; claims without a verified source fail a lint.
6.6 **External benchmarks** (agreement only, never tuning): Wainberg 2021 predictions, hu.MAP 3.0 uncharacterised-protein
hypotheses, Replogle 2022 assignments, Predictomes; overlap with U reported up front.

## 7. Statistics
Gene = unit; cluster bootstrap (§3.5); seeds [0–4] (`config/seeds.yaml`); BH is not used as a U-level error statement —
Σ p_cal with CI is (§0 C3); hypergeometric p descriptive; Holm across orthogonal classes. All thresholds fixed here.

## 8. Compute
Full matrices ≈ 1.35 GB float32 each (zavg_BEF, z_B, z_E, z_F, GLS, Pearson); 10 split-half runs; ≈ 2–3 min per tool
run; matched-gene nulls by matrix ops. Matrices git-ignored; summaries committed.

## 9. AI-agent safeguards
Hash gate + tag + audit_order; one-look log (LOOKS.md) for the temporal hold-out; machine-generated prediction ledger
(`results/ledger/*.tsv`) written before any narrative; numbers in the manuscript inserted from result files by script;
single metrics module with toy tests; script-resolved HGNC identifiers; claim-level citation verification (verbatim
supporting span); blinded judging with redaction; LLM recall probe; red-team review per report; every result checked
by an agent that did not produce it, re-deriving from raw outputs; frozen config hashed; agent tasks scoped to one
script/question with a ≤ 300-word summary.

## 10. Deliverables
`manuscript/` (paper, figures, references), `reports/<GENE>.md`, REPORT.md, LESSONS.md, RESEARCH_TREE.md.

## Revision log
- v0, v1 (2026-10-29): skeleton; criteria from LITERATURE.md.
- v2 (2026-10-29): round-1 reviews integrated (claims/branches; strata; assessability null; calibration on H with
  cross-fitting and support restriction; three-ranker choice on LOO; endpoint fully specified; circularity full-text
  query; cluster bootstrap; covariate shift; relationship types; expression negative control; four-state,
  family-specific orthogonal rules with Holm and admission test; blinded judging with 3 decoys, 2 judges; templates;
  AI safeguards). Disposition: `reviews/round1_disposition.md`.
