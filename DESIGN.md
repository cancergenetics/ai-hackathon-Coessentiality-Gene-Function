# DESIGN.md — v2.2 (after review rounds 1–2; frozen at tag `design-frozen`)

Sections marked **[PRE-SPECIFIED]** are frozen at the `design-frozen` tag. Any later change is logged in the revision log
with reason and date, and affected results are reported under both the frozen and the changed rule.
Reviews: `reviews/round1_*.md`, `reviews/round2_*.md`; dispositions: `reviews/round1_disposition.md`,
`reviews/round2_disposition.md`.

## 0. Goal, claims and decision branches

**Fixed goal (PROMPT.md).** Use the co-essentiality tool (zavg_BEF; github.com/cancergenetics/ai-hackathon-Coessentiality
@ 3c684c9, read-only) on DepMap Public 26Q3 CRISPR Chronos gene effects as the primary hypothesis generator for the
functions of a pre-registered list of uncharacterised human genes (U); orthogonal data reinforce/downweight; literature
checks and experiments for the best predictions; reviewed paper, per-candidate reports, REPORT.md.
Scope rule: analyses of characterised genes (§3) only calibrate confidence; no function is proposed for genes outside U.

**Claims [PRE-SPECIFIED]** (reported whichever way they fall):
- **C1 Census** — fraction of U that is scorable, expressed and assessable (§4.2), by stratum (§1.4).
- **C2 Accuracy & calibration** — temporal hold-out (§3): precision@1 of zavg_BEF vs prior-only and matched-gene nulls
  (primary), vs GLS (key secondary), calibration, named positive-control recovery.
- **C3 Catalogue** — calibrated predictions for assessable U genes; headline = Σ p_cal with CI (§3.7), the expected
  number of top-term predictions that later annotation would confirm; false-call rate from non-expressed U genes (§4.2)
  and matched-gene/decoy runs (§5.4).
- **C4 Candidates** — literature-checked, blinded-judged top candidates with relationship type, alternative
  explanations and tiered experiments.

**Decision branches [PRE-SPECIFIED]**
- C2 primary fails → no calibrated claims for U; top 40 = assessable, expressed U genes ranked by the frozen ranker's
  top-term score; labelled "uncalibrated".
- Calibration poor on H (calibration-slope 95% CI excludes 1 **or** intercept CI excludes 0) → p_cal still reported from
  the pre-specified model with that caveat; no other recalibration.
- < 10 genes in Tier A → paper leads with C1–C2; top 40 filled Tier A → Tier B → p_cal, labelled by tier. Thresholds are
  never relaxed post hoc.
- < 100 U genes scorable, expressed and assessable → C3 descriptive without tiers; top 40 by p_cal.
- GLS ≥ zavg_BEF on the hold-out → stated plainly; zavg_BEF remains the pre-specified generator.

## 1. Pre-registration of uncharacterised genes **[PRE-SPECIFIED]**
Inputs (DATA.md): HGNC complete set (2026-04-23), GO (ontology 2026-07-26; goa_human GAF 2026-05-21), UniProt 2026_03,
gene2pubmed (2026-10-29), TCRD TDL (2023), DepMap 26Q3 header; single-gene summaries and expression for strata only.

1.1 **Universe**: HGNC Approved, locus_group "protein-coding gene" (19,296).
1.2 **Criteria**, one function `src/knownness.py::d1()` for every release (current and archives):
- **D1**: zero informative GO BP/MF terms with evidence in {EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC}; NOT rows excluded;
  generic binding terms (GO:0005515, GO:0005488, GO:0042802, GO:0042803, roots; full list in code) do not count; IPI
  counts only for non-generic terms regardless of with/from; `contributes_to` counts; HTP/HDA/HMP/HGI/HEP, IEA,
  ISS/ISO/ISA/ISM/IGC, IBA/IBD/IKR/IRD, RCA, NAS, ND ignored; CC-only does not count.
- **D2**: UniProt annotation score ≤ 2 (max over reviewed entries).
- **D3**: ≤ 10 focused PubMed records (PMIDs linked to ≤ 10 human genes in gene2pubmed) **or** IDG Tdark.
- **U = D1 ∩ (D2 ∪ D3)**; exact |U|, |U ∩ DepMap|, |U scorable| in `preregistration/CRITERIA.md`.
1.3 **No gene is ever removed from U.** Genes without a DepMap column or UniProt mapping are "not scorable".
1.4 **Strata** (reporting only; single-gene data; computed after the list hash is written, in the same freeze commit):
family (chemosensory/epidermal via named HGNC groups; tandem cluster = ≥ 2 Ensembl paralogues within 1 Mb; other);
expressed (log2(TPM+1) ≥ 1 in ≥ 10% of DepMap lines with expression); profile informativeness (SD tertile within U,
any-dependency = ≥ 1% lines < −0.5, NaN fraction); core (≤ 3 focused PMIDs and Tdark). Headlines for U and for the
expressed, non-chemosensory, non-tandem stratum.
1.5 **Curation-lag audit** (before any U prediction): the 50-gene random U sample (seed 0) — the same sample is the
random arm of the §6.2 recall probe — audited by an agent **with no access to co-essentiality outputs** (current and
previous symbols, aliases, UniProt, PubMed, Europe PMC/bioRxiv); classes N1 established / N2 partial / N3 none.
1.6 **Freeze and gate**: `preregistration/uncharacterised_genes.tsv`, `CRITERIA.md`, `PROVENANCE.md` (how and when the
list was built: annotation-only build during design review, before any pairwise computation), `FREEZE.sha256`
(covers the list, criteria, DESIGN.md, config/term_families.tsv, config/frozen.yaml, config/seeds.yaml, src/knownness.py)
committed with explicit paths and tagged `preregistration-v1` and `design-frozen`. LOOKS.md and CLAIMS.tsv are created at
freeze. Every DepMap pairwise script calls `src/gate.py::check()`. `scripts/audit_order.py` (run by a fresh agent at M4,
M6, M9) checks commit chronology and that no pairwise output predates the tag. Until the tag, the tool clone's
`results/predictions/` is hidden by sparse checkout (`scripts/verify_sparse.sh`).

## 2. Infrastructure and verification (M4)
2.1 **Identifier hub** `results/ids/hgnc_hub.tsv` keyed on hgnc_id (Entrez, UniProt, ENSG, ENSP via STRING aliases;
symbol only as last resort with collision flags); per-source mapping QC tables.
2.2 **Matrices**: one full zavg_BEF matrix (float32, git-ignored, gene index by hgnc_id) via the tool API (unmodified).
GLS and Pearson: rows only for H, the LOO sample (§3.2) and named controls, against all background genes, verified
against the tool's `Baselines.score` on ≥ 100k random pairs (max abs diff < 1e-4). z_B/z_E/z_F for reported pairs via
the tool's pair scorer. Neighbour extraction: diagonal −inf, background genes only; assertion tests.
2.3 **Reproduction**: the tool's published internal-test HT-AP (zavg_BEF 0.345, GLS 0.242, Spearman 0.146, Pearson
0.134) recomputed with its evaluate CLI and `results/splits/protein_assignment.csv` (PI-authorised; lists proteins and
clusters only). Tolerance ±0.005.
2.4 **Sign/orientation assertions** (common essentials mean < −0.5; matrix symmetric; Integrator/CCT/mitoribosome pairs
score > 3) and a **label-shuffle control** (permuted annotations → precision@1 at prior level).
2.5 **Toy pipeline test** (synthetic ~300 lines × 2,000 genes, planted modules 3–30, lineage nuisance, proximity
blocks; real tool with documented toy Config). Acceptance: strong-module held-out members precision@1 ≥ 0.8 and ≥ 80%
assessable; proximity calls removed by same-arm exclusion; null matrix: p_emp ~ U(0,1) (KS p > 0.01), ≤ 5% genes with any
BH-significant term, ≤ 7% genes assessable.
2.6 **Orthogonal source admission (§5.2)** run here, before any U prediction exists.

## 3. Calibration on characterised genes (M5) **[PRE-SPECIFIED]**
3.0 **Vocabularies.** **V2** (primary) = GO BP + MF terms, annotations propagated over is_a/part_of with the current obo;
a gene is a member of term t if it has a D1-evidence-code annotation (non-NOT) to t or a descendant at the release in
use (same codes for targets, neighbour membership, backgrounds and prior-only); `colocalizes_with` dropped; candidate
terms: 5–200 annotated scorable genes at the release in use. **V1** = GO CC descendants of GO:0032991 (same rules;
hu.MAP excluded). **V1′** (module label) = V1 ∪ Complex Portal ∪ MitoCarta3.0 pathways (current only). Module family of
a term: `config/term_families.tsv` (family → GO ancestor IDs, fixed order, first match wins, else "other"; families:
mitochondrial, nuclear RNA machinery, ribosome biogenesis/translation, DNA replication/repair, ER/Golgi/secretory/lipid,
centrosome/cilia/mitosis, signalling/lineage, other). p_cal, tiers and judged statements attach to the **V2 top
reportable term**; V1/V1′ are descriptive labels.
3.1 **Predictor** (identical for calibration and U):
- N(g) = top K = 25 background genes by score, excluding g, genes on g's chromosome arm and Ensembl paralogues of g.
- S(g,t) = Σ_{j∈N(g), j∈t} max(z_gj, 0), precomputed as a gene × term matrix per release.
- Rankers (exactly three): R1 raw S; R2 hypergeometric p (n = |N(g) ∩ annotated background|; background = scorable genes
  with ≥ 1 V2 annotation at the release, query removed); R3 empirical p_emp(g,t) = (1 + #{m ∈ M(g) \ A_t : S(m,t) ≥
  S(g,t)}) / (1 + |M(g) \ A_t|), A_t = genes annotated to t at the release; ties by S.
- **Matched list M(g)**: one list of 500 scorable genes per gene, nearest by Mahalanobis distance on (mean effect, log
  SD, NaN fraction), excluding g, N(g), same-arm genes and paralogues of g; caliper 0.2 SD with nearest-available
  fallback (violation rate reported); seed 0. First 5 = null comparator; first 200 = assessability null; all 500 = R3.
- **Ranker choice**: once, on LOO (§3.2.1), by MRR of the first correct reportable term (RR = 0 if none); ties
  (|ΔMRR| < 0.005) → R3, then R1. Logged in LOOKS.md (with the calibration specification) before H is opened.
- Reportable term: ≥ 2 supporting partners in N(g). Outputs: top reportable term; most specific term among the top 5
  (ancestors of a ranked descendant dropped); hypergeometric p descriptive.
3.2 **Benchmarks**
1. *LOO*: a random 3,000 scorable genes not in U or H (seed 0); targets = the gene's own current V2 terms; the query's
   annotations removed from all counts. Ranker choice and sensitivity calibration only.
2. *Temporal hold-out (primary)*: t0 = GO 2018-07-02. H = scorable genes with D1 at t0 (same function, t0 GAF) and
   ≤ 10 focused PMIDs with PMID < the 2018-07 cut-off, with ≥ 1 target. T(g) = current-propagated minus t0-propagated
   V2 terms (current obo, alt_id/replaced_by resolved, dropped obsolete counted), restricted to candidate terms at t0.
   Neighbour membership at t0. **Endpoint**: hit@1 = top reportable term ∈ T(g); denominator = all H genes (no
   reportable term → 0; coverage reported). The chosen ranker and reportability rule apply unchanged to every comparator
   and network; primary network = full-data zavg_BEF.
   Named controls (case series; rank of true term): SPRING1, PEDS1, CCDC32, INTS15, HAPSTR1, SLC25A51, TEDC1, TEDC2
   (placed by Pan 2018, before t0 — caveat), POU2AF2, POU2AF3, TMEM242; weaker FIRRM, AIRIM, TMEM41B.
3. *Circularity*: every PMID supporting a target is checked in Europe PMC (full text where available: "DepMap",
   "co-essential*", "coessential*", "codependen*", "co-dependen*", "Project Achilles"; plus citation of Wainberg 2021,
   Pan 2018, Kim 2019, Boyle 2018, Rahman 2021, Dempster/Meyers DepMap papers). States: flagged / clean / unscannable.
   Primary analysis excludes flagged annotations; sensitivity also excludes unscannable ones; counts reported.
4. *Secondary vocabularies*: V1 (with/without ETC complex I and mitoribosome; stratified by hu.MAP-train membership).
3.3 **Comparators**: prior-only (t0 frequencies, same candidates); matched-gene null (null hit = mean over the first 5
matches of [m's top reportable term ∈ T(g)]; the comparator alone additionally skips matches annotated to T(g)); GLS
(key secondary, two-sided, by neighbourhood-size stratum); secondary batch (reported all or none): Pearson, homology
baseline (t0 IEA/ISS/IBA terms then frequency), PPI module transfer (N(g) = top-25 by hu.MAP 3.0 probability; coverage
and "co-essentiality alone" complementarity on U), t0 = 2019-07, PMID-dated targets, K = 10/50, no exclusions,
U-reweighting, LOO-fitted calibration. **Primary test** (intersection–union): precision@1(zavg_BEF) − prior-only > 0
**and** − matched-null > 0, each with cluster-bootstrap 95% percentile CI excluding 0 (BCa also reported). Also MRR,
precision@1 with candidates and targets restricted to terms ≤ 50 genes (genes without such a target dropped and
counted), top-1 term size distribution, primary metric on each split-half network.
3.4 *(merged into §3.1 matched list)*
3.5 **Clusters**: connected components linking H genes sharing a supporting PMID or appearing in each other's
zavg_BEF N(g) — fixed once for all comparisons (PMID-only version at freeze for power); paired cluster bootstrap 10,000
replicates (seed 0). Effective n = |H| / design effect; if < 300 the primary is labelled underpowered (still decided).
3.6 **Covariate shift**: SMDs between H, U and LOO on mean effect, SD, NaN fraction, top-K mean zavg, R(g),
neighbourhood annotation coverage; metrics by signal quintile; U-reweighted estimate: logistic model U-eligible vs H on
those six covariates, inverse-odds weights trimmed 1st/99th percentile, refitted per bootstrap replicate, applied to
each method's precision@1 and both primary differences.
3.7 **Calibration model**: logistic regression of hit@1 on top-K mean zavg_BEF (≥ 0), R(g) (≥ 0), neighbourhood
annotation coverage = fraction of N(g) with ≥ 1 V2 annotation (≥ 0), log top-term size (≤ 0), as within-release
percentile ranks (raw scale = sensitivity), plus module family (unconstrained); sign constraints enforced. H metrics
from out-of-fold predictions (10-fold cluster cross-fitting, fold seeds 0–4, averaged); U p_cal from the model fitted on
all H. Reliability diagram (deciles of out-of-fold p_cal, merged to ≥ 30 genes), Brier, calibration intercept and slope
with CIs. **Support**: covariates within H's 5th–95th percentiles and family with ≥ 30 H genes → p_cal; below the 5th
percentile only on top-K mean zavg and/or R(g) → boundary p_cal as an upper bound (not tiered; summed separately);
any other out-of-support → no p_cal; counts per category reported. Σ p_cal CI: refit on 2,000 cluster-bootstrap
resamples of H (seed 0), percentile CI; reported for all U genes with p_cal and for Tier A. p_cal = probability that
the top term is confirmed by D1-evidence annotation within ~8 years (conservative).

## 4. Hypothesis generation for U (M6) **[PRE-SPECIFIED]**
4.1 Predictor §3.1 with current annotations for every scorable U gene; per gene: top-10 partners with zavg_BEF,
z_B/z_E/z_F, GLS rank (top 40 only), annotations, essentiality, chromosome/distance, paralogue and hub flags,
hu.MAP-train membership. Machine-generated ledger `results/ledger/u_predictions.tsv` written before any narrative.
4.2 **Assessability**: split cell lines into halves stratified by OncotreeLineage × screen library (where recorded),
keeping PatientID together (seeds 0–4); all-NaN columns in a half dropped (recorded). Half-neighbour lists for g and for
null genes are restricted to BG_A ∩ BG_B ∩ BG_full with the §3.1 exclusions. R(g) = mean_s |N_A^s(g) ∩ N_B^s(g)|/K;
R0(g,m) = mean_s |N_A^s(g) ∩ N_B^s(m)|/K for the first 200 matches. Assessable iff empirical p = (1 + #{m: R0(g,m) ≥
R(g)})/201 < 0.05 **and** expressed. Non-expressed U genes are scored anyway as a negative control (rate of Tier-A-like
calls = false-call rate, reported by informativeness tertile). RBO = sensitivity.
4.3 **Artefact checks**. Built in: same-arm and paralogue exclusion. Flags for every reported prediction (fixed
thresholds): bidirectional/overlapping/readthrough loci among supporting partners (TSS < 1 kb opposite strands, or
overlapping gene bodies); CN co-amplification (Pearson r between g's effect and a supporting partner's CN > 0.3);
hub-driven (> 50% of S from partners in the top 1% of in-degree in the K-NN graph). Any flag on ≥ half of the supporting
partners → not Tier A. Top 40 only: lineage leave-out (top term retained after removing the most dependent lineage);
dependency–expression coupling (|Spearman ρ| between g's effect and its own expression > 0.3 → relationship type e
considered) and TF/lineage-marker enrichment of partners; TP53-status difference in g's effect (Mann–Whitney q < 0.05
flag); DEMETER2 replication (mean partner correlation in shared lines ≥ 95th percentile of g's random-partner
distribution). Not possible (recorded): shared-sgRNA and per-guide checks (guide-level data unavailable).
4.4 **Relationship type** (a subunit — only with physical, co-abundance or structural support; b assembly/maturation
factor; c supplier/client; d pathway member; e lineage/transcriptional programme): assigned in the top-40 review by
explicit evidence recorded in the ledger (b: partners' assembly-factor annotations + no stable-complex support; c:
transporter/enzyme domain + module-level partners; d: pathway-level partners without complex focus; e: §4.3 coupling or TF
enrichment). p_cal covers the module term only, not the type. Without type-a support the claim reads "functions in /
supports module M".
4.5 Clustering of the K-NN graph: supplementary figure only.

## 5. Orthogonal evidence **[PRE-SPECIFIED; run for U genes with p_cal ≥ 0.3, the top 40, and equal-size matched-gene and decoy prediction sets]**
5.1 **Classes** (independent of DepMap): (P) physical — BioPlex 3.0, OpenCell, BioGRID low-throughput physical, STRING
experiments channel, Human Cell Map SAINT; (A) co-abundance — ProteomeHD (isoform groups collapsed to genes), CCLE
proteomics (shared lines; flagged); (L) localisation — HPA v25.1, OpenCell, Human Cell Map NMF, MitoCarta3.0; (G)
perturbation phenotype — Perturb-seq K562 GW / RPE1 / K562 essential (only if g perturbed with on-target knockdown ≥ 30%
as reported in the dataset), chemogenomic profiles (Olivieri 2020 screens only; ORCS copy or bioRxiv table, whichever
parses, documented); (S) structure — Burke 2023 AF2; (H) homology — orthologue IBA/ISO annotation (reported only). Not
independent (reported only): hu.MAP 3.0, DEMETER2 (robustness §4.3), Predictomes, HumanNet, STRING text-mining/database/
co-expression.
5.1b **Pair scores**: BioPlex edge in either line; OpenCell reported interaction; BioGRID physical non-HTP; STRING
experiments ≥ 400; Human Cell Map SAINT BFDR ≤ 0.01; ProteomeHD score, per-gene row percentile; CCLE proteomics Pearson r
(pairwise complete ≥ 50 lines), row percentile; Perturb-seq Pearson r of pseudo-bulk z profiles; chemogenomic Pearson r
across screens (≥ 10 shared); Burke pDockQ ≥ 0.23; localisation compartment-set match on a common vocabulary (nucleus,
nucleolus, cytosol, mitochondrion, ER, Golgi, plasma membrane, vesicles/endosome/lysosome, centrosome/cilium,
cytoskeleton).
5.2 **Admission** (at M4): co-complex odds ratio on non-hu.MAP complexes (Complex Portal/GO CC) vs degree-matched random
pairs (continuous scores dichotomised at the 95th row percentile; CI by bootstrap over complexes); kept if lower 95% CI
> 2.
5.3 **Support test**: members = scorable genes annotated to the called V2 term (and, for module label, V1′), excluding g.
Statistic: binary sources — number of g–member edges; continuous — mean member row percentile; localisation — fraction
of members sharing a compartment with g. Null: 1,000 equal-size member sets, degree-matched within the source;
empirical p = (1+b)/(1+B). Simes across sources within a class; Holm across measured classes at α = 0.05 per gene.
States: not measured / no support / supports / contradicts. Absence of an interaction is never a contradiction.
Contradiction: incompatible localisation from ≥ 2 high-reliability sources (HPA Enhanced/Supported, OpenCell, Human Cell
Map, MitoCarta), protein not multi-localised.
5.4 **Diagnostic class by family** (Tier A needs support from a diagnostic class when one is measured): mitochondrial →
L or A; nuclear RNA machinery → G or L; ribosome biogenesis/translation → G or L; DNA replication/repair → G or L;
ER/Golgi/secretory/lipid → L; centrosome/cilia/mitosis → L or P; signalling/lineage → P; other → any class. Empirical
false-support rate of the full rule on matched-gene and decoy predictions reported beside the Tier A count.

## 6. Prioritisation, literature validation, experiments (M7) **[PRE-SPECIFIED]**
6.1 **Tiers**: Tier A = scorable, expressed, assessable, p_cal ≥ 0.5 (in support), no §4.3 exclusion, diagnostic-class
support when measured, no contradiction. Tier B = all Tier A conditions except p_cal ≥ 0.5 (needs ≥ 0.3) and/or
diagnostic support. Ranking within tier by p_cal, then number of supporting classes. Top 40 filled Tier A → Tier B →
p_cal. Mitochondrial-family calls ≤ ⅓ of the top 20 and ≤ ⅓ of reports (next eligible substitutes).
6.2 **LLM recall probe**: before any agent sees network output for them, a fresh, tool-less agent states what it knows of
each top-40 gene and the 50 random U genes (symbol + aliases only); logged; "recognised" genes flagged.
6.3 **Novelty screen**: agent L (no access to co-essentiality outputs or our predictions) writes structured evidence
items (claim, source, verbatim span, PMID/DOI, level functional/high-throughput/mention, DepMap-derived y/n) and assigns
N1/N2/N3 for each top-40 gene.
6.4 **Blinded judging**: script-templated statements (V2 term + V1′ label + relationship type; no partner names; gene
names redacted from L's evidence). Per gene: real + 3 decoys (other U genes' predictions matched on family and term size;
not the real term, an ancestor or descendant; Jaccard of member sets < 0.1; seed 0), random order. Two independent
judges, +1 supported / 0 unaddressed / −1 contradicted; κ; third adjudicates; adjudicated scores analysed. DepMap-derived
support = unaddressed. Primary: exact one-sided sign-flip test (enumeration) on real − mean(decoy), α = 0.05; reported
by N-class. Secondary: 30 extra U genes across p_cal bins (support vs p_cal). Validation first on 10 H genes where the
"real" statement is a known current target term: accept if ≥ 7/10 real supported and ≤ 3/30 decoys supported; if
failed, one logged revision and re-validation on 10 new H genes; a second failure is reported as "not validated".
6.5 **Reports**: 8–10 genes chosen as the highest-ranked top-40 genes with N2/N3 novelty plus up to 2 N1 genes as
rediscovery exemplars, respecting the mito cap; Template A + B (`reports/TEMPLATE_*.md`); one decisive falsifiable
experiment with readouts if right/wrong; essential-gene confound control; DepMap cell-line rule; strongest alternative.
Each report gets an unedited red-team review by a separate agent; claims without verified sources fail a lint.
6.6 **External benchmarks** (agreement only): Wainberg 2021, hu.MAP 3.0 uncharacterised-protein hypotheses, Replogle
2022, Predictomes; overlap with U reported. Could: hit rate of Wainberg 2021 predictions since.

## 7. Statistics
Gene = unit; cluster bootstrap (§3.5); seeds `config/seeds.yaml` (global [0–4]; matched lists 0; bootstraps 0);
Σ p_cal with CI is the U-level error statement; hypergeometric p descriptive; Simes/Holm for orthogonal support.

## 8. Compute
One full zavg_BEF matrix (~1.35 GB float32); 10 split-half runs (≤ 1 h total); GLS/Pearson rows for H, LOO sample and
controls; S as gene × term matrices; p_emp by lookup. Matrices git-ignored; summaries committed.
**Analysis tiers**: core (blocks the manuscript) = §3 primary, GLS secondary, calibration, ≤ 50-term precision,
circularity, controls, V1 ± hu.MAP-train; secondary batch (§3.3) run once, reported all or none.

## 9. AI-agent safeguards
Hash gate + tags + audit_order (M4, M6, M9) + verify_sparse; LOOKS.md (one look at H, after ranker and calibration
spec are logged); CLAIMS.tsv (every manuscript number → result file); numbers inserted by script; prediction ledger before
narrative; single metrics module with toy tests; script-resolved HGNC identifiers; claim-level citation verification with
verbatim span; blinded judging with redaction and judge validation; LLM recall probe; red-team per report; independent
re-derivation of key numbers by an agent that did not produce them; `config/agent_scopes.yaml` lists each agent task's
allowed write paths; agents commit nothing — the PI commits with explicit paths.

## 10. Deliverables
`manuscript/` (paper, figures, references), `reports/<GENE>.md`, REPORT.md, LESSONS.md, RESEARCH_TREE.md.

## Revision log
- v0, v1 (2026-10-29): skeleton; criteria from LITERATURE.md.
- v2 (2026-10-29): round-1 reviews integrated. v2.1: seven OPEN disposition items resolved.
- v2.2 (2026-10-29): round-2 reviews integrated (all five "ready after minor changes"): V2 defined and p_cal/tiers on
  V2; neighbour evidence codes; term families file; single matched list with per-term label exclusion and caliper
  fallback; endpoint denominator; cluster definition and percentile CI; covariate-shift weights; calibration signs,
  percentile covariates, support with upper-bound branch, Σ p_cal bootstrap; assessability empirical p on common
  background; orthogonal statistic/Simes/Holm/admission at M4, candidate-only scope; Olivieri-only chemogenomics;
  Perturb-seq knockdown rule; artefact thresholds; relationship-type rules; judge validation on true terms; report
  selection rule; circularity unscannable state; simplifications (one full matrix; analysis tiers; BioPlex comparator,
  AUPRC and ≤ 5-PMID sensitivity cut; merged random samples). Disposition: `reviews/round2_disposition.md`.
