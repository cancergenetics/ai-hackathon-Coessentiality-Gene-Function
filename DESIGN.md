# DESIGN.md — v2.3 (after review rounds 1–2 and the round-2 disposition; frozen at tag `design-frozen`)

Sections marked **[PRE-SPECIFIED]** are frozen at the `design-frozen` tag. Sections 2, 7, 8 and 9 are also frozen; the
markers show where claims are decided. After the tag this file is not edited; later changes are logged in
`DEVIATIONS.md` with reason and date, and affected results are reported under both the frozen and the changed rule.
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
  number of top-term predictions that later annotation would confirm; false-call rate from clean-negative U genes (§4.2)
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
expressed (log2(TPM+1) ≥ 1 in ≥ 10% of DepMap lines with expression; clean negative = log2(TPM+1) < 0.5 in ≥ 95% of
lines; lineage-restricted expressed = expressed in ≥ 50% of lines of any lineage with ≥ 10 lines, counts as expressed,
assessable, and type (e) if flagged); descriptive strata: HPA tissue/testis-enriched, TM/secreted; low_coverage
(non-background, imputed); profile informativeness (SD tertile within U, any-dependency = ≥ 1% lines < −0.5, NaN
fraction); core (≤ 3 focused PMIDs and Tdark). Headlines for U and for the expressed, non-chemosensory, non-tandem
stratum.
1.5 **Curation-lag audit** (before any U prediction): the 50-gene random U sample (seed 0) — the same sample is the
random arm of the §6.2 recall probe — audited by an agent **with no access to co-essentiality outputs** (current and
previous symbols, aliases, UniProt, PubMed, Europe PMC/bioRxiv); classes N1 established / N2 partial / N3 none.
1.6 **Freeze and gate**: `preregistration/uncharacterised_genes.tsv`, `CRITERIA.md`, `PROVENANCE.md`, `FREEZE.sha256`
(covers the list, criteria, DESIGN.md, config/term_families.tsv, config/frozen.yaml, config/seeds.yaml, src/knownness.py,
src/gate.py, the tool commit hash 3c684c9 and the SHA-256 of the DepMap gene-effect, CN and mutation files);
`gate.check()` verifies every entry and the tag. The files are committed with explicit paths and tagged
`preregistration-v1` and `design-frozen`. LOOKS.md and CLAIMS.tsv are created at freeze. Before the tag, the only
permitted reader of DepMap gene-effect values is the allow-listed single-gene strata script (§1.4, per-gene marginals
only); every pairwise script calls gate.check(); audit_order.py checks that no pairwise output predates the tag.
`scripts/audit_order.py` is run by a fresh agent at M4, M6 and M9 and also checks commit chronology. Until the tag, the
tool clone's `results/predictions/` is hidden by sparse checkout (`scripts/verify_sparse.sh`). Freeze artefacts:
PROVENANCE.md records how and when the list was built (annotation-only build during design review, before any pairwise
computation), the criteria-commit hash, builder-script commit, input SHA-256s, every look at |U| and any criteria edit,
and is verified by a fresh agent; `scripts/verify_sparse.sh` writes `preregistration/sparse_check.txt` at freeze and at
M6 start; `tests/test_d1_equivalence.py` requires `knownness.d1()` to reproduce the D1/D2/D3/U columns of the committed
feature table (the script-02 copy is retired); `audit_order.py` output is saved as `reviews/audit_order_M4.md`, `_M6.md`,
`_M9.md` and M6 must pass before `results/ledger/` exists; CLAIMS.tsv is seeded with |U|, |H|, MDE; `scripts/INDEX.tsv`
is created; RESEARCH_TREE.md is updated and the freeze-commit diff is listed in PROVENANCE.md.

## 2. Infrastructure and verification (M4)
2.1 **Identifier hub** `results/ids/hgnc_hub.tsv` keyed on hgnc_id (Entrez, UniProt, ENSG, ENSP via STRING aliases;
symbol only as last resort with collision flags); per-source mapping QC tables; retired UniProt accessions (`sec_ac`)
and HGNC `gene_history` resolved in the hub; retention thresholds of each mapping are asserted in tests; environment
pinned by `config/requirements.lock.txt`.
2.2 **Matrices**: one full zavg_BEF matrix (float32, git-ignored, gene index by hgnc_id) via the tool API (unmodified).
GLS and Pearson: rows only for H, the LOO sample (§3.2), named controls and the U top-40 genes, against all background
genes, verified against the tool's `Baselines.score` on ≥ 100k random pairs (max abs diff < 1e-4). z_B/z_E/z_F for
reported pairs via the tool's pair scorer. Neighbour extraction: diagonal −inf, background genes only; assertion tests.
2.3 **Reproduction**: the tool's published internal-test HT-AP (zavg_BEF 0.345, GLS 0.242, Spearman 0.146, Pearson
0.134) recomputed with its evaluate CLI and `results/splits/protein_assignment.csv` (PI-authorised; lists proteins and
clusters only). Tolerance ±0.005.
2.4 **Sign/orientation assertions** (common essentials mean < −0.5; matrix symmetric; Integrator/CCT/mitoribosome pairs
score > 3) and a **label-shuffle control** (permuted annotations → precision@1 at prior level).
2.5 **Toy pipeline test** (synthetic ~300 lines × 2,000 genes, planted modules 3–30, lineage nuisance, proximity
blocks; real tool with documented toy Config). Acceptance: strong-module held-out members precision@1 ≥ 0.8 and ≥ 80%
assessable; proximity calls removed by same-arm exclusion; null matrix: p_emp ~ U(0,1) (KS p > 0.01), ≤ 5% genes with any
BH-significant term, ≤ 7% genes assessable. The ties-by-S rule of R3 (p_emp floor 1/501) is tested on the planted-module
toy.
2.6 **Orthogonal source admission (§5.2)** run here, before any U prediction exists.

## 3. Calibration on characterised genes (M5) **[PRE-SPECIFIED]**
3.0 **Vocabularies.** **V2** (primary) = GO BP + MF terms, annotations propagated over is_a/part_of with the current obo;
a gene is a member of term t if it has a D1-evidence-code annotation (non-NOT) to t or a descendant at the release in
use (same codes for targets, neighbour membership, backgrounds and prior-only); `colocalizes_with` dropped; candidate
terms: 5–200 annotated scorable genes at the release in use, for V2, V1 and V1′. **V1** = GO CC descendants of
GO:0032991 (same rules; hu.MAP excluded). **V1′** (module label) = V1 ∪ Complex Portal ∪ MitoCarta3.0 pathways (current only). Module family of
a term: `config/term_families.tsv` (family → GO ancestor IDs, fixed order, first match wins, else "other"; families:
mitochondrial, nuclear RNA machinery, ribosome biogenesis/translation, DNA replication/repair, ER/Golgi/secretory/lipid,
centrosome/cilia/mitosis, signalling/lineage, other). p_cal, tiers and judged statements attach to the **V2 top
reportable term**; V1/V1′ are descriptive labels. For neighbour membership (S, backgrounds, A_t, prior-only), annotation
rows with evidence IPI whose with/from field contains the query gene are dropped when that query is scored; applied
identically in LOO, H and U.
3.1 **Predictor** (identical for calibration and U):
- N(g) = top K = 25 background genes by score, excluding g, genes on g's chromosome arm and Ensembl paralogues of g.
- S(g,t) = Σ_{j∈N(g), j∈t} max(z_gj, 0), precomputed as a gene × term matrix per release.
- Rankers (exactly three): R1 raw S; R2 hypergeometric p (n = |N(g) ∩ annotated background|; background = scorable genes
  with ≥ 1 V2 annotation at the release, query removed); R3 empirical p_emp(g,t) = (1 + #{m ∈ M(g) \ A_t : S(m,t) ≥
  S(g,t)}) / (1 + |M(g) \ A_t|), A_t = genes annotated to t at the release; ties by S.
- **Matched list M(g)**: one list of 500 scorable genes per gene, nearest by Mahalanobis distance on (mean effect, log
  SD, NaN fraction), with BG status an exact-match covariate, excluding g, N(g), same-arm genes and paralogues of g;
  caliper 0.2 in Mahalanobis units on standardised covariates with nearest-available fallback (violation rate reported,
  with SMD balance of M(g)); seed 0. First 5 = null comparator; first 200 = assessability null; all 500 = R3.
- **Ranker choice**: once, on LOO (§3.2.1), by MRR of the first correct reportable term (RR = 0 if none); ties
  (|ΔMRR| < 0.005) → R3, then R1. Logged in LOOKS.md (with the calibration specification) before H is opened.
- Reportable term: ≥ 2 supporting partners in N(g). Outputs: top reportable term; most specific term among the top 5
  (ancestors of a ranked descendant dropped; descriptive only; not used for p_cal, tiers or judging); hypergeometric p
  descriptive.
3.2 **Benchmarks**
1. *LOO*: a random 3,000 scorable genes not in U or H (seed 0); targets = the gene's own current V2 terms; the query's
   annotations removed from all counts. Ranker choice and sensitivity calibration only. LOO targets are checked with
   §3.2.3; flagged targets are excluded from the ranker-choice MRR (unscannable ones included, counts reported).
2. *Temporal hold-out (primary)*: t0 = GO 2018-07-02. H = scorable genes with D1 at t0 (same function, t0 GAF) and
   ≤ 10 focused PMIDs with PMID < the 2018-07 cut-off, with ≥ 1 target. T(g) = current-propagated minus t0-propagated
   V2 terms (current obo, alt_id/replaced_by resolved, dropped obsolete counted), restricted to candidate terms at t0.
   Neighbour membership at t0. **Endpoint**: hit@1 = top reportable term ∈ T(g); denominator = all H genes (no
   reportable term → 0; coverage reported). The chosen ranker and reportability rule apply unchanged to every comparator
   and network; primary network = full-data zavg_BEF.
   Named controls (case series; rank of true term): SPRING1, PEDS1, CCDC32, INTS15, HAPSTR1, SLC25A51, TEDC1, TEDC2
   (placed by Pan 2018, before t0 — caveat), POU2AF2, POU2AF3, TMEM242; weaker FIRRM, AIRIM, TMEM41B.
   Controls whose new terms all fall outside 5–200 at t0 (SPRING1, TEDC1, TEDC2, POU2AF2, POU2AF3 at build time) are
   not in H; for the case series only, every control is scored with candidate window 2–300 and reported with the rank
   of its best-ranked true term and its top V1′ module label (descriptive; never pooled with the primary).
3. *Circularity*: every PMID supporting a target is checked in Europe PMC (full text where available: "DepMap",
   "co-essential*", "coessential*", "codependen*", "co-dependen*", "Project Achilles"; plus citation of Wainberg 2021,
   Pan 2018, Kim 2019, Boyle 2018, Rahman 2021, Dempster/Meyers DepMap papers). States: flagged / clean / unscannable.
   Primary analysis excludes flagged annotations; sensitivity also excludes unscannable ones; counts reported.
4. *Secondary vocabularies*: V1 (with/without ETC complex I and mitoribosome; stratified by hu.MAP-train membership).
3.3 **Comparators**: prior-only (t0 frequencies, same candidates); matched-gene null (null hit = mean over the first 5
matches of [m's top reportable term ∈ T(g)]; the comparator alone additionally skips matches annotated to T(g)); GLS
(key secondary, two-sided, by neighbourhood-size stratum); secondary batch (reported all or none): Pearson, homology
baseline (t0 IEA/ISS/IBA terms then frequency), PPI module transfer (N(g) = top-25 by hu.MAP 3.0 probability; hu.MAP 3.0
post-dates t0 and so favours the comparator (conservative for our claim); coverage and "co-essentiality alone"
complementarity on U), t0 = 2019-07, PMID-dated targets, K = 10/50, no exclusions,
U-reweighting, LOO-fitted calibration. **Primary test** (intersection–union): precision@1(zavg_BEF) − prior-only > 0
**and** − matched-null > 0, each with cluster-bootstrap 95% percentile CI excluding 0 (BCa also reported). Also MRR,
precision@1 with candidates and targets restricted to terms ≤ 50 genes (genes without such a target dropped and
counted), top-1 term size distribution, primary metric on each split-half network.
3.4 *(merged into §3.1 matched list)*
3.5 **Clusters**: connected components linking H genes sharing a supporting PMID or appearing in each other's
zavg_BEF N(g) — fixed once for all comparisons; primary CIs use PMID + N(g) clusters; the PMID-only version is used only
for the freeze-time power simulation; paired cluster bootstrap 10,000 replicates (seed 0). Effective n = |H| / design
effect; if < 300 the primary is labelled underpowered (still decided). A power simulation (`results/holdout/power_sim.md`;
PI writes, a fresh agent verifies) giving the minimum detectable difference for both primary comparisons is committed at
freeze and its MDE seeded in CLAIMS.tsv.
3.6 **Covariate shift**: SMDs between H, U and LOO on mean effect, SD, NaN fraction, top-K mean zavg, R(g),
neighbourhood annotation coverage; metrics by signal quintile (SMDs and quintile metrics remain core, §8); U-reweighted
estimate (secondary batch, §8): logistic model U-eligible vs H on those six covariates, where U-eligible = scorable U
genes in support for p_cal (§3.7), inverse-odds weights trimmed 1st/99th percentile, refitted per bootstrap replicate,
applied to each method's precision@1 and both primary differences.
3.7 **Calibration model**: logistic regression of hit@1 on top-K mean zavg_BEF (≥ 0), R(g) (≥ 0), neighbourhood
annotation coverage = fraction of N(g) with ≥ 1 V2 annotation (≥ 0), log top-term size (≤ 0), plus module family
(unconstrained); sign constraints enforced. Neighbourhood annotation coverage and log top-term size enter as
within-release percentile ranks (ranked against all scorable genes in that release); top-K mean zavg and R(g), which do
not depend on the release, enter on their raw scale; raw coverage and size are the sensitivity. H metrics from out-of-fold predictions (10-fold cluster cross-fitting, fold seeds 0–4, averaged); U p_cal from the model fitted on
all H. Reliability diagram (deciles of out-of-fold p_cal, merged to ≥ 30 genes), Brier, calibration intercept and slope
with CIs. **Support**: covariates within H's 5th–95th percentiles and family with ≥ 30 H genes → p_cal; below the 5th
percentile only on top-K mean zavg and/or R(g) → boundary p_cal as an upper bound (not tiered; summed separately);
any other out-of-support → no p_cal; counts per category reported. Σ p_cal CI: refit on 2,000 cluster-bootstrap
resamples of H (seed 0), percentile CI; reported for all U genes with p_cal and for Tier A. p_cal = probability that
the top term is confirmed by D1-evidence annotation within ~8 years (conservative).

## 4. Hypothesis generation for U (M6) **[PRE-SPECIFIED]**
4.1 Predictor §3.1 with current annotations for every scorable U gene; per gene: top-10 partners with zavg_BEF,
z_B/z_E/z_F, GLS rank (top 40 only, §2.2), annotations, essentiality, chromosome/distance, paralogue and hub flags,
hu.MAP-train membership. Machine-generated ledger `results/ledger/u_predictions.tsv` written before any narrative.
4.2 **Assessability**: split cell lines into halves stratified by OncotreeLineage × screen library (where recorded),
keeping PatientID together (seeds 0–4); all-NaN columns in a half dropped (recorded). Half-neighbour lists for g and for
null genes use the §3.1 exclusions: N_A^s, N_B^s = the top 25 after restriction to BG_A ∩ BG_B ∩ BG_full (top-60 per
half retained before filtering). R(g) = mean_s |N_A^s(g) ∩ N_B^s(g)|/K; R0(g,m) = mean_s |N_A^s(g) ∩ N_B^s(m)|/K for the
first 200 matches. R(g) is computed identically for H, LOO and U genes; R0 and the assessability call apply to U genes
and to candidates. Assessable iff empirical p = (1 + #{m: R0(g,m) ≥ R(g)})/201 < 0.05 **and** expressed. Non-expressed U
genes are scored anyway as a negative control (rate of Tier-A-like calls = false-call rate, computed on clean negatives
(§1.4) and reported by informativeness tertile). RBO = sensitivity.
4.3 **Artefact checks**. Built in: same-arm and paralogue exclusion. Flags for every reported prediction (fixed
thresholds): bidirectional/overlapping/readthrough loci among supporting partners (TSS < 1 kb opposite strands, or
overlapping gene bodies); CN co-amplification (Pearson r between g's effect and a supporting partner's CN > 0.3);
hub-driven (> 50% of S from partners in the top 1% of in-degree in the K-NN graph). Any flag on ≥ half of the supporting
partners → not Tier A. Top 40 only: lineage leave-out (top term retained after removing the most dependent lineage);
dependency–expression coupling (|Spearman ρ| between g's effect and its own expression > 0.3 → relationship type e
considered) and TF/lineage-marker enrichment (partners vs the TF list in `config/` (named, frozen), one-sided Fisher
OR > 3 and q < 0.05 → flag); TP53-status difference in g's effect (Mann–Whitney q < 0.05 flag); DEMETER2 replication
(mean partner correlation in shared lines ≥ 95th percentile of g's random-partner distribution). Failing lineage
leave-out, or a DEMETER2 or TP53 flag, removes Tier A (the gene is Tier B at best); coupling flags change the relationship
type (§4.4). Not possible (recorded): shared-sgRNA and per-guide checks (guide-level data unavailable).
4.4 **Relationship type** (a subunit — only with physical, co-abundance or structural support; b assembly/maturation
factor; c supplier/client; d pathway member; e lineage/transcriptional programme): assigned in the top-40 review from
explicit evidence recorded in the ledger (b: partners' assembly-factor annotations + no stable-complex support; c:
transporter/enzyme domain + module-level partners; d: pathway-level partners without complex focus; e: §4.3 coupling or TF
enrichment). Assignment is script-applied in this order: e (§4.3 coupling or TF enrichment); a (only with P/A/S support);
c (transporter/enzyme domain, or ≥ 4 TM helices and no complex-like partners); b (not a stable subunit and in an assembly
term or MitoCarta assembly pathway); else d, recorded as "type unresolved". p_cal covers the module term only, not the
type. Without type-a support the claim reads "functions in / supports module M".
4.5 Clustering of the K-NN graph: supplementary figure only.

## 5. Orthogonal evidence **[PRE-SPECIFIED; run for U genes with p_cal ≥ 0.3, the top 40, and equal-size matched-gene and decoy prediction sets]**
5.1 **Classes** (independent of DepMap): (P) physical — BioPlex 3.0, OpenCell, BioGRID low-throughput physical, STRING
experiments channel, Human Cell Map SAINT; (A) co-abundance — ProteomeHD (isoform groups collapsed to genes), CCLE
proteomics (shared lines; flagged); (L) localisation — HPA v25.1, OpenCell, Human Cell Map NMF, MitoCarta3.0; (G)
perturbation phenotype — Perturb-seq K562 GW / RPE1 / K562 essential (only if g perturbed with on-target knockdown ≥ 30%
as reported in the dataset), chemogenomic profiles (Olivieri 2020 screens only, §5.1b); (S) structure — Burke 2023 AF2;
(H) homology — orthologue IBA/ISO annotation (reported only). Not independent (reported only): hu.MAP 3.0, DEMETER2 (robustness §4.3), Predictomes, HumanNet, STRING text-mining/database/
co-expression.
5.1b **Pair scores**: BioPlex edge in either line; OpenCell reported interaction; BioGRID physical non-HTP; STRING
experiments ≥ 400; Human Cell Map SAINT BFDR ≤ 0.01; ProteomeHD score, per-gene row percentile; CCLE proteomics Pearson r
(pairwise complete ≥ 50 lines), row percentile; Perturb-seq Pearson r of pseudo-bulk z profiles; chemogenomic Pearson r
across screens (≥ 10 shared); Burke pDockQ ≥ 0.23; localisation compartment-set match on a common vocabulary (nucleus,
nucleolus, cytosol, mitochondrion, ER, Golgi, plasma membrane, vesicles/endosome/lysosome, centrosome/cilium,
cytoskeleton, peroxisome, lipid droplet, nuclear envelope; multi-localised = ≥ 2 compartments in any admitted source;
the source-to-vocabulary map is committed at M4). Source definitions: BioPlex measured = appears as a node. STRING:
`physical.links.detailed`, experimental ≥ 400; because it imports BioGRID/IntAct/BioPlex it is counted with them as one P
source group. CCLE proteomics: key Uniprot_Acc, lines mapped to ModelID via Model.csv CCLEName, replicate columns
collapsed before the ≥ 50-line rule. Perturb-seq: g's own transcript and the partner's transcript are excluded from
profiles; a perturbation counts only with ≥ 25 cells. Chemogenomics: Olivieri `Zscores_28screens` only (the ORCS copy has
no screen metadata and is not used); loader test required (xlsx loads in neither openpyxl nor pandas). Burke: null pairs
are drawn from pairs covered by Burke (HuRI ∪ hu.MAP). Continuous-source nulls are matched on hubness (mean row-score
decile) and, for Perturb-seq, on phenotype strength.
5.2 **Admission** (at M4): co-complex odds ratio on non-hu.MAP complexes (Complex Portal/GO CC) vs degree-matched random
pairs (continuous scores dichotomised at the 95th row percentile; CI by bootstrap over complexes); kept if lower 95% CI
> 2. Localisation sources are admitted if their compartment calls agree with GO CC on H genes (agreement rate lower 95%
CI > 0.6, ≥ 200 H genes; annotation agreement only, no hit@1 outcome is used).
5.3 **Support test**: members = scorable genes annotated to the called V2 term, excluding g; Tier A support uses the V2
member set; V1′ is reported descriptively.
Statistic: binary sources — number of g–member edges; continuous — mean member row percentile; localisation — fraction
of members sharing a compartment with g. Null: 1,000 equal-size member sets, degree-matched within the source;
empirical p = (1+b)/(1+B). Simes across sources within a class; Holm across measured classes at α = 0.05 per gene.
States: not measured / no support / supports / contradicts. Absence of an interaction is never a contradiction.
Contradiction: incompatible localisation from ≥ 2 high-reliability sources (HPA Enhanced/Supported, OpenCell, Human Cell
Map, MitoCarta), protein not multi-localised (≥ 2 compartments in any admitted source, §5.1b).
5.4 **Diagnostic class by family** (Tier A needs support from a diagnostic class when one is measured): mitochondrial →
L or A; nuclear RNA machinery → G or L; ribosome biogenesis/translation → G or L; DNA replication/repair → G or L;
ER/Golgi/secretory/lipid → L; centrosome/cilia/mitosis → L or P; signalling/lineage → P; other → any class. Empirical
false-support rate of the full rule on matched-gene and decoy predictions reported beside the Tier A count.

## 6. Prioritisation, literature validation, experiments (M7) **[PRE-SPECIFIED]**
6.1 **Tiers**: Tier A = scorable, expressed, assessable, p_cal ≥ 0.5 (in support), no §4.3 exclusion, diagnostic-class
support when measured, no contradiction; low_coverage genes (§1.4) are excluded from Tier A unless H contains such
genes. Tier B = all Tier A conditions except p_cal ≥ 0.5 (needs ≥ 0.3) and/or diagnostic support. Ranking within tier by p_cal, then number of supporting classes. Top 40 filled Tier A → Tier B →
p_cal. Mitochondrial-family calls ≤ ⅓ of the top 20 (≤ 6) and ≤ 3 reports, counting N1 exemplars (next eligible
substitutes).
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
"real" statement is a known current target term (judges are told the statement's type is not covered by p_cal): accept
if ≥ 7/10 real supported and ≤ 3/30 decoys supported; if failed, one logged revision and re-validation on 10 new H genes; a second failure is reported as "not validated".
6.5 **Reports**: 8–10 genes chosen as the highest-ranked top-40 genes with N2/N3 novelty plus up to 2 N1 genes as
rediscovery exemplars, respecting the mito cap; other N1 genes appear in a rediscovery table with rate and CI;
Template A + B (`reports/TEMPLATE_*.md`); one decisive falsifiable experiment with readouts if right/wrong; DepMap
cell-line rule; strongest alternative. Template A opens with a Section 0 bench summary (claim in plain words;
confidence = expected hit probability; strongest reason to doubt; first experiment with time and cost; cancer-line
essentiality is not organismal function); ledger and red-team go to an appendix. Template B requires acute or hypomorphic
depletion time-matched to partner depletion with a matched-essentiality control gene from an unrelated module (the
essential-gene confound control); for common-essential genes the controls are rescue, non-targeting guides and a control
essential gene; the DepMap screen medium is the baseline (galactose is a sensitised condition); type-specific rows (b
BN-PAGE and pulse-chase; c uptake/metabolite and bypass rescue; e ChIP/reporter); an "other" readout row sourced from a
ledger-verified paper; a sequence-level off-target check of guides; decision rule "Supported = dropout rescued AND
module-specific readout concordant AND localisation compatible AND Tier-2 physical or epistatic support". Each report
gets an unedited red-team review by a separate agent; claims without verified sources fail a lint.
6.6 **External benchmarks** (agreement only): Wainberg 2021, hu.MAP 3.0 uncharacterised-protein hypotheses, Replogle
2022, Predictomes; overlap with U reported. Could: hit rate of Wainberg 2021 predictions since.

## 7. Statistics
Gene = unit; cluster bootstrap (§3.5); seeds `config/seeds.yaml` (global [0–4]; matched lists 0; bootstraps 0);
Σ p_cal with CI is the U-level error statement; hypergeometric p descriptive; Simes/Holm for orthogonal support.

## 8. Compute
One full zavg_BEF matrix (~1.35 GB float32); 10 split-half runs (≤ 1 h total); GLS/Pearson rows for H, LOO sample,
controls and the U top-40 genes; S as gene × term matrices; p_emp by lookup. Matrices git-ignored; summaries committed.
**Analysis tiers**: core (blocks the manuscript) = §3 primary, GLS secondary, calibration, ≤ 50-term precision,
circularity, controls, V1 ± hu.MAP-train, SMDs and quintile metrics (§3.6); secondary batch (§3.3) run once, reported
all or none.

## 9. AI-agent safeguards
Hash gate + tags + audit_order (M4, M6, M9) + verify_sparse; LOOKS.md (one look at H, after ranker and calibration
spec are logged); CLAIMS.tsv (every manuscript number → result file); numbers inserted by script; prediction ledger before
narrative; single metrics module with toy tests; script-resolved HGNC identifiers; claim-level citation verification with
verbatim span; blinded judging with redaction and judge validation; LLM recall probe; red-team per report; independent
re-derivation of key numbers by an agent that did not produce them; `config/agent_scopes.yaml` lists, for each role
(audit, probe, L, judge, red-team), the working directory, allowed input files and allowed write paths; blind roles run in a directory
containing only an ID/symbol file; each run appends role, model ID, input hashes and timestamp to
`results/agent_runs.tsv`; agents commit nothing — the PI commits with explicit paths.

## 10. Deliverables
`manuscript/` (paper, figures, references), `reports/<GENE>.md`, REPORT.md, LESSONS.md, RESEARCH_TREE.md,
DEVIATIONS.md (post-tag changes only).

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
- v2.3 (2026-10-29): all open items of `reviews/round2_disposition.md` applied (O1–O20, I1–I12), with PI decisions:
  O5 adopted-modified (pre-tag DepMap reads limited to the allow-listed single-gene strata script; no `lock_depmap.sh`,
  no chmod), O11 localisation admission threshold set (agreement lower 95% CI > 0.6 on ≥ 200 H genes), O17 caveat only
  (no BioPlex 2.0), I3 adopted (file not edited after the tag; deviations go to `DEVIATIONS.md`). Changes: IPI with/from
  leakage rule, circularity applied to LOO, freeze hash contents and freeze artefacts, power simulation, clean-negative
  and lineage-restricted strata, `low_coverage` stratum and BG-status matching, §4.3 TF threshold and tier consequences,
  localisation vocabulary and admission, type precedence, V1′ size window, §5.1b source definitions, mito cap rounding
  and rediscovery table, PPI comparator caveat, deferred infrastructure, Template A/B requirements (§6.5), ties-by-S
  toy test; GLS rows for the U top 40, percentile ranks for release-dependent covariates only, header and PRE-SPECIFIED
  scope, U-eligible definition, R(g) for H/LOO/U, Mahalanobis caliper, V2 member set for support, cluster version,
  half-list restriction order.
