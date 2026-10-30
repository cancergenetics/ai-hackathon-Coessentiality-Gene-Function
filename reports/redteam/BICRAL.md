# Red-team review — reports/BICRAL.md

- Reviewer: adversarial reviewer agent (role `red_team`), model Claude Opus 5.5
- Date: 2026-10-30
- Scope: Appendix A + Part II ledgers, every number against the cited project file, hypothesis attack, experiment plan.
- Independence: reviewer did not write the report; all checks re-run from primary sources (Europe PMC REST, UniProt,
  AlphaFold DB, `data/raw/*`, `results/ledger/*`, `results/m7/*`).

---

## 1. Ledger spot-check (all 32 rows of Appendix A + Part II §8 checked)

**Method.** PMIDs resolved via `EXT_ID:` queries to the Europe PMC REST API (`resultType=core`); spans matched
normalised against title+abstract, then full text, then by exact-phrase full-text search where EPMC serves no XML.
Project-file rows grepped from the cited file.

| # | Row (abbreviated) | Source | Result |
|---|---|---|---|
| 1 | 1079 aa, PF15249, IPR015671/IPR052438, no TM, score 5 | UniProt Q6AI39 + bundle §8 | **PASS** |
| 2 | FUNCTION + SUBUNIT (GBAF; BICRA/BICRAL mutually exclusive) | UniProt Q6AI39 | **PASS** (bundle §8 carries the FUNCTION verbatim with `ECO:0000269/PubMed:29374058`) |
| 3 | pLDDT 45.7, AFDB v6 | `af_Q6AI39.json` | **PASS** (45.72) |
| 4 | GAF rows: IDA to GO:0016514 (CC), IPI to GO:0005515, NAS rows | GOA 2026-05-21 | **PASS on the quoted spans**; see §1.1 for a misdescription in the body |
| 5 | GBAF defined by mutually exclusive GLTSCR1/GLTSCR1L | PMID:29374058 | **PASS** (abstract) |
| 6 | GLTSCR1/1L KO reduces PC3 proliferation | PMID:29374058 | **PASS** (abstract) |
| 7 | "GLTSCR1L purification resolved full ncBAF complexes" (+ "in Fx 10–11 and subcomplexes in fractions 6–7") | PMID:30343899 | **PASS** (EPMC serves no full-text XML for PMC6791824; both spans confirmed by exact-phrase full-text search, 1 hit = 30343899) |
| 8 | GLTSCR1/1L each associate exclusively with BRD9 | PMID:30510198 | **PASS** (full text) |
| 9 | GLTSCR1L contacts SMARCC1/SMARCD1 via a long helix | PMID:41402274 | **PASS** (full text) |
| 10 | BRD9 and GLTSCR1L largely dispensable in vitro | PMID:42377898 | **PASS** (abstract) |
| 11 | ncBAF defined by BRD9 + GLTSCR1/1L, no ARID1/2 | PMID:42377898 | **PASS** (abstract) |
| 12 | ncBAF at CTCF sites and promoters | PMID:30397315 | **PASS** (abstract) |
| 13 | GLTSCR domain + DUF3512 underlie the dependency | PMID:30397315 | **PASS** (full text) |
| 14 | BRD9 sub-complex lacks SMARCB1 | PMID:31015438 | **PASS** (abstract) |
| 15 | BRD9 in SS18-SSX BAF complexes | PMID:30431433 | **PASS** (abstract) |
| 16 | GLTSCR1/L antibodies unreliable for western | PMID:30431433 | **PASS** (full text) |
| 17 | SF3B1-mutant cancers; ncBAF contains GLTSCR1/1L | PMID:31597964 | **PASS** (abstract) |
| 18 | BRD4 ET domain binds NSD3, JMJD6, CHD4, GLTSCR1 | PMID:21555454 | **PASS** (abstract) |
| 19 | Pan 2018: GLTSCR1's top fitness correlations SMARCD1/BRD9 | PMID:29778836 | **PASS** (no EPMC XML for PMC6152908; span confirmed by exact-phrase search, 1 hit = 29778836) |
| 20 | 2026 survey: BICRA/BICRAL important in a prostate line | PMID:42629553 | **PASS** (full text) |
| 21 | hu.MAP 3.0 complex + pair rows | PMID:40425816 + `data/raw/humap3/*` | **PASS** (`huMAP3_03221.1` contains Q6AI39; `BICRAL BCL7C 0.9994122982025146`, `SMARCA4 BICRAL 0.997423529624939` present, tab-separated) |
| 22 | Replogle 2022 did not measure BICRAL | PMID:35688146 + `support_sources.tsv` | **PASS** |
| 23 | Wainberg 2021 out of scope (score 5 > 2) | PMID:33859415 + UniProt | **PASS** |
| 24 | Predictomes 88 pairs; SMARCD1 0.468/0.420, BRD9 0.438/0.756 | `predictome_BICRAL.csv` | **PASS** (88 unique rows, no header; both rows verbatim) |
| 25 | Raw r: SMARCD1 0.268, BRD9 0.252, BICRA 0.164, SMARCA4 0.081 | `depmap_checks.out` | **PASS as quoted**, materially incomplete — see §1.2 |
| 26 | Yamato/SYO-1 paralogue-switch effects | `depmap_checks.out` | **PASS as quoted** — see §3.1 |
| 27 | BICRAL effect vs BICRA expr ρ = −0.057 | `depmap_checks.out` | **PASS** (p = 0.041, n = 1292) — but see §3.1 on interpretation |
| 28 | MRPS10 matched control −0.57 / −0.74 | `matched_ctrl.py` out | **PASS** |
| 29 | Bundle supplies all §1–§6 numerics; `top40_primary.tsv` rank 33 | project files | **PASS** |
| 30 | Judging: real +1, decoys 0, d = +1.0; 18/40 vs 3/120, p = 0.0002174 | `judge/*` | **PARTIAL FAIL** — see §1.3 |
| 31 | Recall probe recognised the gene, named the complex | `recall_probe_90.tsv` via bundle §9 | **PASS** |
| 32 | p_cal definition; calibration not poor | DESIGN.md L178–179; `holdout_eval/SUMMARY.md` | **PASS** (holdout precision@1 0.030 confirms the "3%" in §0) |

**Failures: 1 partial (row 30) + 2 material omissions (§1.1, §1.2).** No fabricated PMID, DOI or span. Every one of the
"future-dated" PMIDs (41402274, 41409030, 42377898, 42629553) resolves with a matching title and DOI.

### 1.1 Misdescription of the GAF rows (§2 body text)

The report says the NAS rows are "**NAS** rows from Complex Portal". They are not: the NAS rows cite papers
(`BICRAL involved_in GO:0006338 PMID:29374058 NAS`, `… GO:0045596 PMID:30510198 NAS`, `BICRAL part_of GO:0140288
PMID:29374058 NAS`). The Appendix A row quotes them correctly; only the prose is wrong. Related, and more important for
the project's framing: UniProt carries an **experimental** FUNCTION comment for BICRAL (`ECO:0000269/PubMed:29374058`),
so "nobody has published an experimentally-supported statement of what BICRAL *does*" is true only of the GO BP/MF
evidence codes, not of the literature. The report should say "the GO record lags", not "nobody has published".

### 1.2 Material omission inside a "verified" row (row 25)

`CRISPRGeneEffect.csv` (recomputed here, n = 1361) gives the correlations the report does **not** print:

| pair | r |
|---|---|
| **BICRA–SMARCD1** | **0.529** |
| **BICRA–BRD9** | **0.523** |
| BICRAL–SMARCD1 | 0.268 |
| BICRAL–BRD9 | 0.252 |
| BICRAL–BICRA | +0.164 |
| BRD9–SMARCD1 | 0.672 |

The paralogue BICRA tracks the ncBAF fitness axis **about twice as strongly as BICRAL does**. The report's §7.3 and §11
argue that BICRAL has a *specific, paralogue-switched* requirement; the panel-level fact is that both paralogues sit on
the same axis, with BICRA the dominant one, and that BICRAL and BICRA are **positively** correlated. This is the single
most damaging omitted number and the required fix below.

### 1.3 Judging row (row 30)

The quoted justification span `"J030 C 1 Rows 1,2,5: component of GBAF/ncBAF SWI/SNF chromatin remodelling complex."`
appears **only in `J2_main1.tsv`**. `J1_main1.tsv` reads `J030 C 1 Rows 1,2: subunit of GBAF SWI/SNF chromatin
remodeling complex`. The row cites both judge files as the source of one span, and §7's "citing evidence rows 1, 2
(and 5)" papers over the difference. The scores themselves (+1/+1, decoys 0, d = +1.0) and the headline 18/40 vs 3/120
with p = 0.0002174 all verify.

---

## 2. Numbers against project files

Reproduce exactly: mean/SD −0.007/0.146, median −0.009, p5 −0.222, min −0.833, 4/1361 < −0.5, expression 99.2%/74.6%,
median 2.40, ρ = −0.039, R(g) = 0.160 (null max 0.112) with p = 0.0050, RBO 0.387, lineage table (Lymphoid 97/−0.074;
Thyroid 11/−0.056; Uterus 38/−0.050), top-10 partner table incl. GLS ranks 2 and 1 for SMARCD1/BRD9, S = 36.747 vs
36.707 vs 29.485, LOPO 1/5, 2/5, 0/3, CN r values, hub share 0.00, TF OR 1.07, TP53 p 0.1902, lineage leave-out to
GO:0140463 with overlap 0.72, K=10 GO:0140993 / K=50 same, GLS top term GO:0002020, P p = 0.2128 with the BioPlex /
BioGRID / STRING degrees and interactor lists, A 0.667 vs 0.547 (p 0.0010) with the per-partner CCLE values, L 0.989 vs
0.681 (p 0.0010), Burke 18 pairs / 0 ≥ 0.23, network 45 edges / 13 physical incl. the three touching BICRAL, p_cal
0.0415 [0.018–0.065], rank 33, V1′ = CPX-4206 with 4 supporting partners.

**One inconsistency.** §2 of Part II says the partner criterion "was dropped (funnel: 1361 → 4 with g ≤ −0.5 → 1 also
passing SMARCD1 ≤ −0.3)". The funnel in bundle §10 reads `plus_partner_le_m0p3 1; plus_expr_ge2 1;
plus_not_amplified 1` — i.e. **one line (Yamato) satisfies the full unrelaxed rule**. The criterion was not forced to be
dropped; dropping it is what admits line 2 (HCM-CSHL-0143-C20, SMARCD1 −0.10). The report's phrasing ("as for the
companion gene, this is a consequence of a flat profile") borrows INAFM1's much worse funnel (4 → 0) to excuse a
different situation.

---

## 3. Attack on the hypothesis

### 3.1 The one novel claim — paralogue-specific dependency — is the weakest part of the report

The membership call is a rediscovery (the report says so plainly, and credits the recall probe, UniProt, Complex Portal
and hu.MAP). Everything that is claimed as new rests on §7.3. Against it:

- **Sign.** BICRAL–BICRA r = **+0.164**. A mutually exclusive, interchangeable-slot model predicts zero or negative
  co-dependency; a shared-axis model predicts positive. The data give positive.
- **Dominance.** BICRA–BRD9 0.523 and BICRA–SMARCD1 0.529 vs BICRAL's 0.252/0.268. If "tracks SMARCD1 and BRD9" is the
  evidence for a slot-specific requirement, BICRA has twice the evidence, and the report's framing would make BICRAL
  the junior partner on its own criterion.
- **Buffering test is already negative.** The report's own recomputation — BICRAL effect vs BICRA expression
  ρ = −0.057 — is null: cells with more BICRA mRNA are not less BICRAL-dependent. §8 reframes this as "a mild argument
  that paralogue buffering is not a straightforward transcript-abundance effect". It is more naturally read as evidence
  against the switching model, and should be reported that way.
- **n = 2, sub-threshold, and selected after the fact.** SYO-1's BICRA effect is **−0.43**, which does not meet the
  project's own ≤ −0.5 dependency bar; calling SYO-1 "a BICRA-dependent line" (§0, Part II §1) overstates it. The
  symmetric pattern is a two-line anecdote within one disease.
- **The pattern does not hold across the dependent lines.** The four lines with BICRAL ≤ −0.5 are ACH-001039 (−0.833),
  ACH-003337 (−0.737), ACH-000253 (−0.581), ACH-001277/Yamato (−0.577). Their partner effects
  (`depmap_checks.out`): ACH-001039 BRD9 **+0.20**, SMARCD1 **+0.46**; ACH-003337 BRD9 −0.26, SMARCD1 −0.10;
  ACH-000253 BRD9 −0.18, SMARCD1 −0.23. **Only Yamato co-drops** (BRD9 −0.86, SMARCD1 −0.75). The claim "the lines that
  need BICRAL track SMARCD1 and BRD9" (§7, §11) is true of 1 of 4 lines, and Yamato is also the line chosen for the
  experiment. That is selection, and §7/§11 report only the selected case.

### 3.2 Type a ("stable subunit") is earned from the literature, not from the pipeline — the report half-says this

The §4.4 rule assigns a because A and L "support". Both supports are near-trivial for a nuclear chromatin term:
L asks whether term members share a compartment with g — 0.989 of 94 members are nuclear and HPA calls BICRAL
nucleoplasm, so the test is close to a tautology for any nuclear protein; A is a CCLE-proteomics row-percentile mean of
0.667 vs 0.547, with JMJD6 at the 7th percentile and SMARCA4 at the 52nd, and p = 0.0010 is the floor of the
permutation grid, not a strong value. Both p-values should be read as "cannot exclude", not as independent support.
The honest statement — which §1 partly makes — is that type a comes from PMID:29374058/30343899/30510198, and the
pipeline could not have reached it.

### 3.3 Circularity

Three independent routes back into DepMap-type reasoning: (i) the **recall probe recognised the gene and named GBAF**
before any network output (the report states this and should keep it in the abstract of any downstream summary);
(ii) **Pan 2018 (PMID:29778836)** made the same inference from the same data type for the paralogue — verified above;
(iii) **PMID:30397315 and PMID:31015438** are Achilles-derived in part. The report identifies all three. No further
circularity found, and the A/L classes are not DepMap-derived.

### 3.4 Missing literature (two items, both material)

Independent search (`TITLE_ABS:"BICRAL" OR "GLTSCR1L"` → 8 records, matching the report's count; plus targeted searches
on GBAF/H3K27ac/enhancer and on Yamato/SYO-1) turned up two sources the report does not cite:

1. **PPR59167** (bioRxiv 2018-10-17, "The GBAF chromatin remodeling complex binds H3K27ac and mediates enhancer
   transcription"), the only GLTSCR1L-**specific functional** study I could find: it characterises the conserved
   GLTSCR1/1L "GiBAF" domain as responsible for GBAF complex formation and GLTSCR1L nuclear localisation, shows
   GLTSCR1L occupancy at H3K27ac enhancers is BRD9-bromodomain-dependent, and reports genome-wide loss of enhancer
   transcription on GLTSCR1L dislocation. The report's search was declared to include preprint sources, and §7 states
   "function is only partly defined"; this preprint is squarely about BICRAL function and moves the N2 justification
   (and the "what is new" accounting in §11) closer to prior art. It also supplies a better module readout than the
   one chosen (see §4).
2. **PMID:41423472** (2025-12, "Synovial sarcoma reprograms transcription by GBAF activation of polycomb targets and
   loss of CBAF enhancers") shows that in SS18::SSX-driven synovial sarcoma — exactly the Yamato/SYO-1 setting —
   **GBAF is redistributed to H2AK119ub-marked promoters and distal enhancers**, not to its normal site repertoire.
   The planned readout is BRD9 CUT&RUN "at CTCF-proximal/promoter ncBAF sites" from PMID:30397315, which is the wrong
   site definition for the chosen lines.

Also uncited and relevant to the experiment: **PMID:42361322** (2026-09, "BRD9 Degraders Unleash GBAF Chromatin
Remodeling Activity in Synovial Sarcoma"), which complicates the use of dBRD9 as the positive comparator.

### 3.5 Other artefact routes — adequately handled

Chromosomal proximity (0 same-chromosome partners), CN (|r| ≤ 0.06), expression coupling (ρ = −0.039), TF enrichment
(OR 1.07) all check out against the bundle. The hub check is less reassuring than stated for the same reason as in the
companion report: SMARCD1 in-degree 65 and BRD9 58 are the 98.6th and 97.2nd percentiles of the 14,417 partner rows in
`u_partners.tsv` (median 26), and each appears in the top-10 of 10 of the 4,271 U genes — the rule only covers
term-supporting partners, which SMARCD1 and BRD9 are not. Lineage: the report's mitigation (replacement term still
chromatin, overlap 0.72) is fair.

---

## 4. Experiment plan (Part II)

Strengths: the Yamato/SYO-1 same-disease, same-medium pair is a genuinely good design; the IP-MS "BICRA must be absent"
prediction is a crisp, falsifiable test of curated mutual exclusivity; the reciprocal cross-complementation matrix is
the right decisive arm; the BICRA-locus off-target clause and the endogenous-tagging route (given the documented
antibody problem) are correct.

Problems:

1. **SYO-1 carries two incompatible roles.** It is the §2 "control line that expresses g but does not depend on it"
   *and* the BICRA-dependent comparator for the decisive paralogue arm. With BICRAL = +0.02 there, the "≤ 5% dropout in
   SYO-1" prediction is close to guaranteed and cannot discriminate hypotheses; and the mirror-image prediction leans
   on a BICRA effect (−0.43) that does not clear the project's dependency threshold. Add a third line with a genuine
   BICRA dependency (BICRA ≤ −0.5) so the mirror arm has a real signal to lose.
2. **Wrong site definition for the CUT&RUN readout in these lines.** PMID:41423472 (above) shows GBAF redistribution
   to H2AK119ub/polycomb-target sites in SS18::SSX synovial sarcoma. Define ncBAF sites empirically in each line (BRD9
   CUT&RUN in the parental line) and stratify by H2AK119ub and CTCF, rather than importing the CTCF/promoter
   definition from a different context.
3. **The dBRD9 positive comparator may not behave as assumed** (PMID:42361322 reports BRD9 degraders *unleashing* GBAF
   remodelling activity in synovial sarcoma). State the expected direction per site class, or use a BRD9 degron
   time-course with its own validation rather than a literature-borrowed signature.
4. **Matched-essentiality controls are poorly chosen for a transcriptional readout.** MRPS10 (mitoribosome) depletion
   causes OXPHOS loss and an ISR transcriptional response; the stated fallbacks are GLE1 (mRNA export) and TRMT6
   (tRNA modification) — all three perturb transcript abundance by their own mechanisms. Pick a matched control whose
   failure mode does not overlap the RNA-seq readout, and report growth-matched ISR markers alongside.
5. **Power at the gate.** Yamato's Chronos is −0.58 in a panel where the gene's SD is 0.146; the plan's own expectation
   is only 15–25% depletion by day 21. Specify replicate number and the minimum detectable effect, or the Tier-1 gate
   will not be decisive either way.
6. **Falsification 9.1 is partly pre-answered.** PMID:42377898 already reports BRD9/GLTSCR1L dispensability for
   assembly and remodelling in vitro, so "BRD9 and SMARCD1 protein levels unchanged" is the expected, not the
   surprising, outcome; the discriminating content sits entirely in the occupancy/target-gene and
   cross-complementation arms. Say so, and do not let an unchanged-western result be read as a near-refutation.

---

## 5. Verdict

**ACCEPT WITH REVISIONS.** The ledger is clean (1 partial failure in 32 rows, no invention), the numbers reproduce, and
the report is explicit that complex membership is a 2018 rediscovery recalled by the probe. It cannot stand as written
because its only novel claim — paralogue-specific dependency — is argued from the favourable half of an already-computed
correlation table and from one of the four dependent lines, and because the GLTSCR1L-specific functional literature was
missed.

### Required fixes

1. **Report BICRA's own co-dependencies and the sign of the paralogue correlation**: BICRA–SMARCD1 0.529,
   BICRA–BRD9 0.523 (vs BICRAL 0.268 / 0.252) and BICRAL–BICRA **+0.164**; plus the partner effects of all four
   BICRAL-dependent lines (ACH-001039 BRD9 +0.20 / SMARCD1 +0.46; ACH-003337 −0.26 / −0.10; ACH-000253 −0.18 / −0.23;
   Yamato −0.86 / −0.75). Then either downgrade §7.3/§11 to "a two-line observation consistent with, but not evidence
   for, paralogue switching", or state the panel-level test that would actually establish it (and note that the one
   already run — effect vs paralogue expression, ρ = −0.057 — is null).
2. **Add the missed literature and re-weigh novelty**: PPR59167 (GiBAF domain, GLTSCR1L nuclear localisation, H3K27ac
   enhancer occupancy and enhancer transcription) and PMID:41423472 (GBAF redistribution to H2AK119ub sites in
   SS18::SSX synovial sarcoma); note PMID:42361322 for the degrader comparator. Revise "function is only partly
   defined" and the §11 novelty accounting accordingly.
3. **Rebuild the SS-line readout and the control structure**: define ncBAF sites empirically per line and stratify by
   H2AK119ub/CTCF instead of importing the CTCF/promoter definition; separate SYO-1's two roles by adding a line with
   BICRA ≤ −0.5; replace MRPS10/GLE1/TRMT6 with a matched control that does not perturb the transcriptional readout.
4. Smaller: fix "NAS rows from Complex Portal" (they cite PMIDs) and soften "nobody has published … what BICRAL does"
   to a GO-curation statement (UniProt's FUNCTION is ECO:0000269); attribute the judging span to `J2_main1.tsv` (J1's
   wording differs); correct Part II §2 — one line *does* pass the unrelaxed partner criterion
   (`plus_partner_le_m0p3 1`), so the relaxation admits line 2 rather than being forced; state that the A and L
   "supports" are near-tautological for a nuclear term and that type a rests on the published biochemistry.
