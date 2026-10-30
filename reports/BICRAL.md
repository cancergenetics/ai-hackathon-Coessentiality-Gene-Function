# BICRAL — candidate report (Template A) + experiment plan (Template B)

Prepared under DESIGN §6.5. Template A is Part I; Template B is Part II of this same file (the task fixed
`reports/BICRAL.md` as the only writable report path for this gene, so the experiment plan is kept here as a clearly
marked part rather than in `reports/BICRAL_experiments.md`).

Unblinded literature search date: **2026-10-30** (Europe PMC incl. preprint sources, UniProt, GO/GOA, hu.MAP 3.0,
Predictomes, project ledgers). Red-team review (Appendix B): **pending**.

---

# Part I — Template A

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** BICRAL (previously GLTSCR1L / KIAA0240) behaves in CRISPR fitness data like a working part of the
  non-canonical BAF (ncBAF / GBAF) chromatin-remodelling complex: its two strongest co-dependency partners by a wide
  margin are SMARCD1 (BAF60A) and BRD9, the two other defining ncBAF components. The assigned term is *transcription
  coregulator binding* (GO:0001221) and the complex-level label is the GBAF complex (Complex Portal CPX-4206). Physical
  membership of BICRAL in GBAF is **already published** (2018), so this is a **rediscovery of membership plus a
  refinement**: the co-essentiality data say BICRAL is *functionally required* in particular cell lines, and — the part
  that is genuinely new — that the requirement is **paralogue-specific**: lines depend on BICRAL *or* on its mutually
  exclusive paralogue BICRA, not on both.
- **Confidence:** **p_cal = 0.0415** [95% CI 0.018–0.065] = the expected probability that *the module term*
  (GO:0001221) is confirmed by D1-type experimental annotation within ~8 years. It is a hit probability for the term
  only, not for the relationship type and not for the paralogue-specificity refinement. Tier: none (p_cal fill; rank 33
  of the primary top 40). The low number reflects the base rate of the whole pipeline (3% precision@1 on the hold-out),
  not a judgement about this gene — and for BICRAL the literature already supports the module, so p_cal understates
  what is known here.
- **Strongest reason to doubt:** this is not an independent discovery. The recall probe recognised the gene and named
  the right complex before any network output was seen, the complex membership is in UniProt and Complex Portal, and
  the prediction failed the lineage leave-out check (removing Lymphoid lines changes the top term). What co-essentiality
  adds beyond the 2018 biochemistry is the dependency structure, not the membership.
- **First experiment:** knock out BICRAL and BICRA, singly and together, in a BICRAL-dependent synovial sarcoma line
  (Yamato) and a BICRA-dependent one (SYO-1), and ask whether the fitness and ncBAF-target-gene defects are
  paralogue-specific and complementable across the two; time ~8–10 weeks; approximate cost ~€35–50k (details in
  Part II).
- Cancer-line essentiality is not organismal function: dependency in DepMap lines says the gene is needed for
  proliferation there, not what it does in the organism.

## Definitions used in this template

**Relationship type (DESIGN §4.4).** How the gene g relates to its predicted module M.

| Code | Type | Claim allowed |
|---|---|---|
| a | Stable subunit | Only with physical, co-abundance or structural support. |
| b | Assembly or maturation factor | "Required for assembly or maturation of M". |
| c | Supplier or client | Transporter, enzyme, or substrate of an import or insertion machinery that co-varies with M. |
| d | Pathway member | "Acts in pathway M". |
| e | Lineage or transcriptional programme | Regulatory co-dependency; not a function call. Assigned when g's dependency tracks its own expression, or partners are enriched for TFs or lineage markers. |

Without type-(a) support the claim reads "functions in / supports module M".

**Novelty class (DESIGN §1.5, §6.3).** Assigned by agent L, blind to our prediction, with the search date recorded.

| Class | Meaning |
|---|---|
| N1 | Function established in the literature (rediscovery; curation lag). Reported as validation, never dropped. |
| N2 | Partial or indirect evidence (function related or the complex known; prediction goes beyond it). |
| N3 | No functional literature found. Novelty claims are made only for N3, and for N2 where the prediction goes beyond what is known. |

---

## 1. Header

- Symbol: **BICRAL** | HGNC ID: **HGNC:21111** | previous symbols: **KIAA0240 / GLTSCR1L**; alias symbol: **SMARCK2** |
  UniProt: **Q6AI39** | band: **6p21.1** | Ensembl ENSG00000112624 | Entrez 23506 | DepMap column `BICRAL (23506)`
- D1 / D2 / D3 values: **True / False (UniProt annotation score 5) / True** (D3_pubmed True, D3_tdark True; focused
  PMIDs 0, all PMIDs 27; TDL **Tdark**) → the gene enters U through **D1 ∩ D3**, not through D2 |
  curation-lag audit flag: **not in the audit sample**
- Stratum (§1.4): family **other**; expression **expressed** (not lineage-restricted); informativeness tertile **mid**;
  **core True** (≤ 3 focused PMIDs and Tdark); headline stratum True; tool background True; low_coverage False;
  paralogues in matrix: **1** (BICRA)
- Hypothesis (one sentence): **BICRAL functions in / supports transcription coregulator binding (GO:0001221) as a
  component of the GBAF/ncBAF SWI/SNF chromatin-remodelling complex, and its cell-line dependency is specific to the
  BICRAL-using form of that complex rather than to SWI/SNF in general.**
- Relationship type: **a (stable subunit)** — the only one of the two genes in this pair of reports that earns type a.
  The §4.4 script rule assigns a because the co-abundance (A) and localisation (L) classes support the call and the
  V1′ label is complex-like with 4 supporting partners. Independently, UniProt's `SUBUNIT` comment and the 2018
  biochemistry place BICRAL physically in GBAF (§7), so "subunit" is a literature fact here, not an inference from
  co-essentiality.
- Novelty class: **N2** (agent L; file `results/m7/L/HGNC_21111.md`; unblinded re-search 2026-10-30 below agrees)
- LLM-recall-probe flag (§6.2): **known** — "recognised: yes", confidence medium, recalled function verbatim
  *"GLTSCR1L, a subunit of the non-canonical (GBAF/ncBAF) SWI/SNF chromatin remodelling complex."*; probe answer logged
  at `results/m7/recall_probe_90.tsv`; **matches network top term: yes**. **The prediction is therefore not independent
  of background knowledge**, and every novelty statement in this report is written with that in front of it.
- Calibrated probability p_cal: **0.0415** [95% CI **0.018–0.065**, cluster bootstrap, 2000 refits]; calibration family:
  **other**; covariates inside H's 5th–95th percentile: **yes** (support category `in_support`)
- Tier: **none (p_cal fill)**; rank in primary top 40: **33**. Top-40-only label: **demoted — lineage_leaveout**.

## 2. The protein

- Domains (InterPro): **IPR015671 (GSCR1 domain)** and **IPR052438 (chromatin remodeller / transcription coactivator
  family)**; Pfam **PF15249 (GLTSCR1)**. No `Domain [FT]` features; large disordered stretches (UniProt regions 51–79,
  509–604, 669–691, 837–877, 917–954, with polar / low-complexity / acidic-basic biases). TM / signal peptide / MTS:
  **none**. Length **1079 aa**. AlphaFold pLDDT (global, AFDB v6): **45.7** — very low, as expected for a long,
  largely disordered scaffold subunit; this is a reason the structural (S) class is uninformative here, not evidence
  against the call.
- Protein names (UniProt): "BRD4-interacting chromatin-remodeling complex-associated protein-like (Glioma tumor
  suppressor candidate region gene 1 protein-like)". Protein existence: evidence at protein level; annotation score 5.
- UniProt `FUNCTION` (verbatim): *"Component of SWI/SNF chromatin remodeling subcomplex GBAF that carries out key
  enzymatic activities, changing chromatin structure by altering DNA-histone contacts within a nucleosome in an
  ATP-dependent manner."* UniProt `SUBUNIT` additionally states membership of "the SWI/SNF (GBAF) subcomplex, which
  includes at least BICRA or BICRAL (mutually exclusive), BRD9, SS18, the core BAF subunits, SMARCA2/BRM,
  SMARCA4/BRG1/BAF190A, ACTL6A/BAF53, SMARCC1/BAF155, and SMARCD1/BAF60A". **The mutual exclusivity with BICRA is
  curated, not inferred by us**, and it is the hinge of the refinement in §7.
- **Why a gene with a UniProt FUNCTION comment is in U.** D1 counts only informative GO BP/MF terms with experimental
  evidence codes; CC-only annotations do not count. BICRAL's current GAF rows are: one IPI to the generic binding term
  GO:0005515 (excluded by rule), a set of **NAS** rows from Complex Portal, **IBA**/**IEA** rows, **TAS** rows from
  Reactome, and one **IDA** row — `BICRAL part_of GO:0016514 PMID:29374058 IDA` — which is a **cellular-component**
  annotation. So the experimental evidence that exists is CC-only, and the gene is D1-positive by the letter and the
  spirit of the rule: nobody has published an experimentally-supported statement of what BICRAL *does*. Combined with
  Tdark status (D3), it is in U. This is a clean, instructive example of the curation-lag phenomenon the project set
  out to study, and it should be reported as such rather than treated as a labelling accident.
- Class H (homology) evidence for the predicted term: **False** (no IBA/ISO annotation to GO:0001221).
- Source keys: UniProt Q6AI39; PMID:29374058; PMID:30343899; PMID:30510198; PMID:42377898; GOA 2026-05-21;
  `reports/data/BICRAL/bundle.md` §8. All appear in Appendix A.

## 3. Dependency profile

- Mean / SD of Chronos effect: **−0.007 / 0.146**; median −0.009; 5th percentile −0.222; min −0.833. Fraction of lines
  < −0.5: **0.0029 (4 of 1361)**; common-essential or selective: **neither — essentially dependency-flat with a thin
  tail**; NaN fraction **0.0000**.
- Expression: log2(TPM+1) ≥ 1 in **99.2%** of lines (≥ 2 in 74.6%); median log2(TPM+1) **2.40**. Spearman
  ρ(effect, own expression) = **−0.039** (n = 1292) → no coupling flag. Dependency-vs-expression scatter: panel (b) of
  `reports/data/BICRAL/fig_profile.png`.
- Lineage enrichment (descriptive): **Lymphoid** n = 97, mean −0.074, MW p = 0.0000; **Thyroid** n = 11, mean −0.056,
  p = 0.1395; **Uterus** n = 38, mean −0.050, p = 0.0218. Again small shifts (≈ 0.05–0.07 units).
- Split-half assessability: **R(g) = 0.160**; null mean 0.002, max 0.112; #R0 ≥ R = 0; empirical p = **0.0050**;
  RBO R = 0.387, p = 0.0050 → **assessable: yes**.
- Figure 1 (profile panel): **`reports/data/BICRAL/fig_profile.png`** — (a) BICRAL vs SMARCD1 effect across lines, (b)
  effect vs own expression, with the chosen dependent lines (D1, D2) and the control line (C) marked.
- Recomputed raw correlations † (`results/m7/scratch_reports_inafm1/depmap_checks.py`, n = 1361): BICRAL vs **SMARCD1
  r = 0.268**, vs **BRD9 r = 0.252**, vs **BICRA r = 0.164**, vs SMARCA4 r = 0.081, vs SS18 r = 0.064. The two
  defining ncBAF partners lead on the raw scale as well as on the whitened scale — which is reassuring, because the
  whitened statistic is the one that can manufacture structure.

## 4. Neighbourhood

Top-10 partners (`results/ledger/u_partners.tsv`; GLS rank = rank in g's GLS row after the §3.1 exclusions):

| rank | partner | zavg_BEF | z_B / z_E / z_F | GLS rank | in term | partner function and essentiality | chr & distance | paralogue flag | hu.MAP-train |
|---|---|---|---|---|---|---|---|---|---|
| 1 | SMARCD1 | 20.28 | 32.4 / 19.5 / 9.0 | 2 | no | BAF60A, core ncBAF subunit; mean eff −0.17, 11.9% of lines < −0.5; not CE | 12q13.12 | no | gene yes, pair no |
| 2 | BRD9 | 20.01 | 31.4 / 19.4 / 9.2 | 1 | no | ncBAF-defining bromodomain subunit; mean eff 0.02, 2.7%; not CE | 5p15.33 | no | no / no |
| 3 | CTBP1 | 9.40 | 16.0 / 10.8 / 1.4 | 1445 | **yes** | transcriptional corepressor; mean eff 0.01, 1.6% | 4p16.3 | no | no / no |
| 4 | SMARCA4 | 9.08 | 15.0 / 8.7 / 3.5 | 97 | **yes** | BRG1 ATPase of all SWI/SNF classes; mean eff −0.36, 31.8%; not CE | 19p13.2 | no | gene yes, pair no |
| 5 | CREBBP | 8.79 | 13.7 / 10.4 / 2.2 | 1532 | **yes** | histone acetyltransferase coactivator; mean eff −0.11, 10.7% | 16p13.3 | paralogue of another partner | no / no |
| 6 | JMJD6 | 8.20 | 11.9 / 9.4 / 3.3 | 278 | no | lysyl hydroxylase / arginine demethylase; BRD4-ET-domain interactor; mean eff −0.43, 35.6% | 17q25.1 | no | no / no |
| 7 | BOD1 | 7.98 | 10.2 / 12.9 / 0.8 | 5020 | no | kinetochore–microtubule attachment; mean eff −0.03, 0.4% | 5q35.2 | no | no / no |
| 8 | SETD1B | 7.62 | 11.8 / 9.5 / 1.6 | 1920 | no | H3K4 methyltransferase; mean eff −0.24, 13.9% | 12q24.31 | paralogue of another partner | no / no |
| 9 | NSD3 | 7.17 | 11.7 / 8.1 / 1.7 | 1599 | no | H3K36 methyltransferase; BRD4-ET-domain interactor; mean eff 0.07, 0.4% | 8p11.23 | paralogue of another partner | no / no |
| 10 | SS18 | 6.92 | 12.2 / 6.2 / 2.3 | 820 | no | BAF subunit; fusion partner in synovial sarcoma; mean eff 0.03, 1.4% | 18q11.2 | no | no / no |

The two remaining supporting partners of the top term, **EP300** and **SP1**, sit in the K = 25 list beyond the top 10
(they appear in the bundle's CN check). No top-10 partner is on g's chromosome; BICRA, the Ensembl paralogue, is
excluded by construction from N(g).

- Figure 2 (neighbourhood network): **`reports/data/BICRAL/fig_network.png`** — g plus the top-10 partners, edges at
  zavg_BEF ≥ 3; blue nodes (CTBP1, SMARCA4, CREBBP) are annotated to the predicted term; solid black edges carry
  physical support. 45 edges among the 11 nodes, **13 with physical support, three of which touch BICRAL directly:
  BICRAL–SMARCD1, BICRAL–BRD9, BICRAL–SMARCA4**. This is the structural difference from the INAFM1 case in the
  companion report: here the co-essentiality edges and the physical edges overlap on the gene itself.

Top 3 terms (R1; `results/ledger/u_top5.tsv`):

| rank | term | S | p_emp | hypergeometric p (descriptive) | leave-one-partner-out stability |
|---|---|---|---|---|---|
| 1 | GO:0001221 transcription coregulator binding (size 101) | 36.747 | 0.0020 | 0.0000 | rank kept after 1 of 5 single-partner removals |
| 2 | GO:0140993 histone modifying activity (size 164) | 36.707 | 0.0040 | 0.0000 | 2 of 5 |
| 3 | GO:0006352 DNA-templated transcription initiation (size 146) | 29.485 | 0.0080 | 0.0014 | 0 of 3 |

Second-ranked term: **GO:0140993 histone modifying activity** (S differs from rank 1 by 0.04 — effectively a tie).
V1 label: **GO:0016514 SWI/SNF complex**; **V1′ label: Complex Portal CPX-4206, "GBAF (SWI/SNF) ATP-dependent chromatin
remodeling complex, ACTL6A-BICRA-SMARCA4 variant"** with 4 supporting partners. The V1′ label is the most informative
output for this gene: the pipeline's own complex-level call lands on GBAF, the complex BICRAL is a curated member of.

An honest caveat about the term: GO:0001221 "transcription coregulator binding" is a *binding* term supported by
CTBP1/SMARCA4/CREBBP/EP300/SP1 — generic, multifunctional chromatin proteins. The term is not wrong, but it is a
coarse label for a specific biology, and the leave-one-partner-out column shows it is fragile (rank kept after only 1
of 5 removals; rank 2 after most). The complex-level V1′ call is the sharper statement.

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | **pass** | g arm 6p; 0 of the top-10 partners on g's chromosome; the paralogue BICRA is excluded from N(g) by construction |
| Bidirectional-promoter / overlapping / readthrough partners | **pass** | 0 of 5 supporting partners flagged |
| Copy-number co-amplification | **pass** | 0 of 5 flagged; CTBP1 r = −0.01, SMARCA4 r = 0.05, CREBBP r = −0.01, EP300 r = 0.02, SP1 r = −0.06 |
| Hub-driven call (> 50% of S from top-1% in-degree) | **pass** | hub share 0.00; 0 hub partners |
| Lineage leave-out | **FAIL** | removing Lymphoid (97 lines; mean effect −0.074) changes the top term to GO:0140463 chromatin-protein adaptor activity; N(g) overlap **0.72**. Mitigating: the replacement term is still a chromatin term, so the *module* survives even though the *label* does not — unlike the INAFM1 case, where the replacement term left the biology entirely |
| K = 10 / 50 | **mixed** | K = 10 gives GO:0140993 histone modifying activity (the rank-2 term; still chromatin); K = 50 gives the same top term |
| Dependency vs own expression; TF / lineage-marker enrichment | **pass** | ρ = −0.039 (n = 1292); TFs in N(g) = 2, OR 1.07, p 0.5719, q 1.0000 |
| TP53 / p53-axis correlation | **pass** | mut 902 / WT 459; p 0.1902, q 0.3803; median difference 0.015 |
| DEMETER2 replication | **not measured** | 0 partners present in DEMETER2 |
| Shared-sgRNA and per-guide check | **not possible** (guide maps / guide-level data not available) | recorded |
| GLS network (descriptive, §2.2) | **different** | the GLS K = 25 top term is GO:0002020 protease binding — but note SMARCD1 and BRD9 are GLS ranks 2 and 1 in g's GLS row, i.e. the *neighbourhood* agrees across statistics even though the *term* does not |

The last row matters. For BICRAL the two scoring statistics disagree about the GO label while agreeing completely about
who the top partners are. That is a different and much weaker failure than a neighbourhood that changes identity.

## 6. Orthogonal evidence matrix (four states: not measured / no support / supports / contradicts)

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | BioPlex 3.0, OpenCell, BioGRID-LTP, STRING-exp (one source group); Human Cell Map SAINT | **no support** | g **is** measured (BioPlex degree 5: BCL7A, BCL7C, SMARCD1, SS18L2, ZCCHC10; BioGRID-LTP degree 5: SMARCA4*, ACTL6A, BRD9, CDC5L, DTNBP1; STRING-exp degree 12 incl. SMARCA4*, ACTL6A, BCL7A/C, BRD2, BRD9, SMARCA2, SMARCD1, SS18L2) — but only **1 of its interactors is annotated to the 101-member term**, so the member-set test is not significant. Pairwise with the top-10: SMARCD1 Y(BioPlex, STRING), BRD9 Y(BioGRID, STRING), SMARCA4 Y(BioGRID, STRING); CTBP1/CREBBP/JMJD6/BOD1/SETD1B/NSD3/SS18 no edge | 0.2128 (Simes) | family "other" → any class is diagnostic |
| A co-abundance | CCLE proteomics (75 members measured); ProteomeHD (g not measured) | **supports** | member row-percentile mean 0.667 vs null 0.547. Pairwise: SS18 r = 0.54 (99th row percentile), BRD9 r = 0.46 (96th), NSD3 r = 0.27 (85th), CREBBP r = 0.26 (84th), CTBP1 0.15 (75th), SMARCD1 0.11 (70th), SMARCA4 −0.03 (52nd), JMJD6 −0.36 (7th) | **0.0010** | yes |
| L localisation | HPA v25.1 (admitted; 94 members measured) | **supports** | 0.989 of members share a compartment with g vs null 0.681. HPA call: reliability *Approved*; main **Nucleoplasm**, additional **Cytosol** → vocabulary compartments nucleus, cytosol; term compartments: nucleus; g multi-localised: True | **0.0010** | yes |
| G perturbation phenotype | Perturb-seq K562 GW / K562 essential / RPE1 essential | **not measured** | g not perturbed/measured in any of the three | — | — |
| S structure | Burke 2023 AF2 | **not measured** | 18 modelled pairs with g, **0 with pDockQ ≥ 0.23** — recorded as "no measured member" (no term member among the modelled pairs), and in any case uninformative for a 1079-aa protein with pLDDT 45.7 | — | — |
| H homology | orthologue IBA/ISO | reported only | False (no IBA/ISO to the term) | reported only | n.a. |

Supporting classes: **A, L** (Holm across the three measured classes at α = 0.05). Diagnostic class measured /
supports: **True / True**. Contradiction: **False**. Members tested: 101.

Two readings of the "P: no support" cell are both true and should be stated together: (i) by the pre-specified test,
the physical class does not support the *term*; (ii) BICRAL nonetheless has direct, independently reported physical
edges to SMARCD1, BRD9 and SMARCA4 — the test's member set (101 genes annotated to a broad binding term) is simply a
poor proxy for "the complex this protein sits in". Absence of an interaction is never a contradiction; here it is not
even an absence.

Reported but not counted: **hu.MAP 3.0** places BICRAL in SWI/SNF complexes (e.g. huMAP3_03221.1 and huMAP3_11470.1,
both containing BICRAL, BICRA, BRD9, SMARCA2/4, SMARCC1/2, SMARCD1/2/3, ARID1A/B, ARID2, PBRM1, BCL7A/B/C, SS18,
DPF1/2/3, PHF10 …), and the hu.MAP 3.0 complex-pair file gives BICRAL–BCL7C 0.9994, BICRAL–BCL7A 0.9992,
BICRAL–SMARCC1 0.9990, SMARCA2–BICRAL 0.9976, SMARCA4–BICRAL 0.9974. This is strong but **not independent** of the
P-class sources and is reported only. **Predictomes**: 88 pairs with Q6AI39; the top SWI/SNF ones are BICRAL–SMARCD1
kirc 0.468 / spoc 0.420, BICRAL–BRD9 kirc 0.438 / **spoc 0.756**, BICRAL–BCL7A 0.466, BICRAL–BCL7C 0.366,
BICRAL–ACTL6A 0.346 / spoc 0.625 — again consistent with ncBAF membership, again not independent and not counted.

## 7. Literature (blinded step, then synthesis)

**Blinded summary of agent L's evidence items** (`results/m7/L/HGNC_21111.md`; 6 items, 4 at level *functional*, none
DepMap-derived): UniProt's GBAF FUNCTION comment; PMID:29374058 defining GBAF with the mutually exclusive paralogues
GLTSCR1/GLTSCR1L; PMID:29374058 showing that GLTSCR1 or GLTSCR1L knockout in PC3 prostate-cancer cells reduces
proliferation and colony formation; PMID:42377898 (2026 cryo-EM) finding BRD9 and GLTSCR1L "largely dispensable for
complex assembly and nucleosome remodeling"; PMID:42377898 and PMID:41409030 defining ncBAF by BRD9 + GLTSCR1/GLTSCR1L.
Agent L recorded that BICRA (GLTSCR1) papers were excluded unless BICRAL is named, and assigned **N2**: membership is
established, specific function is not.

**Blinded verdicts** (packet J030, `results/m7/judge/`): real statement **+1** (supported); decoys **0, 0, 0**; judges
J1 and J2 independently scored +1 on the real slot citing evidence rows 1, 2 (and 5), so no adjudicator was needed;
**d = +1.0**. BICRAL is one of only 2 of the 7 N2 top-40 genes whose real statement was supported. Within the primary
top 40 the headline result is 18/40 real supported vs 3/120 decoys, sign-flip p = 0.0002174; BICRAL is one of those 18.

**Unblinded synthesis (2026-10-30).** A full unblinded search (Europe PMC, all previous symbols and the accession;
`BICRAL OR GLTSCR1L OR "GLTSCR1-like" OR KIAA0240 OR SMARCK2` returns 1981 records dominated by the SWI/SNF field, of
which only 8 name the gene in title or abstract) confirms and sharpens agent L's picture:

1. **Membership is established and reproduced.** GBAF/ncBAF was defined by the mutually exclusive paralogues:
   "We termed this complex GBAF because it incorporates two mutually exclusive paralogs, GLTSCR1 … or GLTSCR1L …,
   instead of an ARID protein" [PMID:29374058]. In mouse ESCs, "GLTSCR1 and GLTSCR1L each exclusively associate with
   BRD9, but not with BAF47" [PMID:30510198]. Purifications resolved the complex directly: "GLTSCR1L purification
   resolved full ncBAF complexes" [PMID:30343899]. The 2025 cryo-EM reconstitution used GLTSCR1L as a component and
   found that "GLTSCR1L interacts with coiled-coil SMARCC1 and SMARCD1 subunits mainly through a long helix"
   [PMID:41402274]. **Our rank-1 and rank-2 co-dependency partners, SMARCD1 and BRD9, are exactly the proteins this
   literature pairs BICRAL with.** This is a rediscovery of complex membership by an orthogonal data type.
2. **Function is only partly defined, and the newest structural work pushes back.** The 2026 cryo-EM study reports that
   "The ncBAF-specific subunits BRD9 and GLTSCR1L are largely dispensable for complex assembly and nucleosome
   remodeling" [PMID:42377898]; BCL7A rather than GLTSCR1L supplies the nucleosome-engagement function. So an *in
   vitro* reading says BICRAL is a passenger. Our cellular data say the opposite in specific lines: there are lines
   whose proliferation depends on BICRAL, and whose dependency profile tracks SMARCD1 and BRD9. **These two statements
   are compatible** (dispensable for the biochemical reaction ≠ dispensable in cells, where targeting, stability and
   paralogue availability matter), and distinguishing them is exactly what Part II is built to do.
3. **The refinement that co-essentiality actually adds: paralogue-specific dependency.** UniProt records BICRA and
   BICRAL as mutually exclusive; the 2018 paper found that "GLTSCR1 or GLTSCR1L knockouts in the metastatic prostate
   cancer cell line PC3 resulted in a loss in proliferation and colony-forming ability" [PMID:29374058] — i.e. in one
   line, either knockout hurt. The DepMap panel lets this be asked at scale, and the answer has structure. Two synovial
   sarcoma lines illustrate it † (recomputed from `CRISPRGeneEffect.csv`): **Yamato (ACH-001277): BICRAL −0.58, BICRA
   +0.13, BRD9 −0.86, SMARCD1 −0.75**; **SYO-1 (ACH-001275): BICRAL +0.02, BICRA −0.43, BRD9 −0.80, SMARCD1 −0.59**.
   Both lines need the shared ncBAF machinery (BRD9, SMARCD1); they differ in *which paralogue* carries the
   requirement. Across the panel BICRAL and BICRA effects correlate only weakly (r = 0.164 †) while BICRAL correlates
   better with SMARCD1 (0.268) and BRD9 (0.252) — the pattern expected if the paralogues are interchangeable slots in
   one complex whose occupancy differs between lines. **This paralogue-switching statement is not in the literature we
   retrieved and is the genuinely new, falsifiable content of this report.** It is also the part that p_cal does not
   cover.
4. **Everything else known about BICRAL is complex-level or correlative:** reviews place it among GBAF subunits
   [PMID:33143733]; a 2026 expression survey notes "BICRA and BICRAL have been shown to be important for cell
   proliferation in a prostate cancer cell line" [PMID:42629553]; the ncBAF disease literature (synovial sarcoma and
   rhabdoid tumours [PMID:30397315, PMID:31015438, PMID:30431433]; SF3B1-mutant cancers [PMID:31597964]) is almost
   entirely about BRD9, with GLTSCR1 second and GLTSCR1L a distant third — PMID:30397315 maps the dependency to "the
   GLTSCR domain of GLTSCR1/1L and the DUF3512 of BRD9", which is the closest the field comes to a BICRAL-specific
   functional claim. The BRD4-ET-domain proteomics that first linked GLTSCR1 to this neighbourhood [PMID:21555454] also
   pulled out NSD3 and JMJD6 — our rank-9 and rank-6 partners — which is a second, independent corroboration of the
   neighbourhood's composition from a non-DepMap source.

**Is any of it DepMap-derived?** Agent L's 6 items: none DepMap-derived. Of the background papers used above,
**PMID:30397315 and PMID:31015438 are DepMap/Project-Achilles-derived in part** (Achilles 18Q3 and Project Achilles
screens for the BRD9/ncBAF synthetic-lethality claims), and **PMID:29778836 (Pan et al. 2018) is entirely
co-essentiality-derived** — it already placed the paralogue GLTSCR1 in a SMARCD1/BRD9 fitness module: "one putative
subunit, GLTSCR1, whose highest ranked fitness correlations were with SMARCD1 and BRD9". Those statements are therefore
**not independent evidence for our claim** and are reported here as prior art rather than as confirmation. The
independent (non-DepMap) support is: PMID:29374058, PMID:30343899, PMID:30510198, PMID:41402274, PMID:42377898,
PMID:21555454, UniProt and hu.MAP 3.0.

**Closest prior publication and what co-essentiality adds beyond it.** Closest: **PMID:29374058** (Alpsoy & Dykhuizen
2018), which established that BICRAL is a GBAF subunit and that its knockout, like BICRA's, impairs PC3 proliferation.
Co-essentiality adds two things it does not contain: (i) panel-scale evidence that the BICRAL requirement is specific —
the lines that need BICRAL track SMARCD1 and BRD9, not SWI/SNF generally (SMARCA4 r = 0.08) — and (ii) the
paralogue-switching pattern in §7.3. A second close prior is **PMID:29778836**, which made the same kind of inference
from the same kind of data for the paralogue GLTSCR1 eight years earlier; our result is the BICRAL counterpart and is
not independent of that methodological precedent.

**Prior prediction lists containing this gene:**
- *Wainberg 2021* (PMID:33859415): BICRAL / GLTSCR1L is **not named in the retrieved full text**. Their uncharacterised
  set was UniProt annotation score ≤ 2; BICRAL's score is 5, so it would have been **out of scope** for their
  prediction list. Per-gene supplementary tables were not retrieved.
- *hu.MAP 3.0* (PMID:40425816): **yes — hu.MAP 3.0 places BICRAL in SWI/SNF complexes** (two complex entries; pair
  probabilities ≥ 0.997 with SMARCA2/SMARCA4 and ≥ 0.999 with BCL7A/BCL7C/SMARCC1). This is the one catalogue that
  made an equivalent assignment, and it is reported-only (not independent).
- *Replogle 2022* (PMID:35688146): BICRAL is **not measured** in K562 GW, K562 essential or RPE1 essential Perturb-seq
  (`results/ledger/support_sources.tsv`: "g not measured") — no prediction.
- *Predictomes* (reported only): pairs with SMARCD1, BRD9, BCL7A/C and ACTL6A at moderate scores (above) — consistent,
  not counted.
- *Pan et al. 2018* (PMID:29778836), a co-essentiality catalogue not on the §6.6 list: made the analogous call for the
  paralogue GLTSCR1, not for BICRAL.
- **Post-freeze (after 2026-10-29) papers confirming the prediction:** none.

## 8. Alternative explanations

For each artefact check in §5, the evidence against it:

- **Chromosomal proximity:** 0 of 10 partners on g's chromosome; SMARCD1 (12q13.12) and BRD9 (5p15.33) are far away.
- **Paralogue cross-reactivity:** BICRA is excluded from N(g) by construction, so the SMARCD1/BRD9 signal cannot be
  BICRA's dependency leaking through sequence similarity in the *scoring*. It could still leak through *guides* in the
  original screen — the shared-sgRNA check is impossible here (no guide-level data), so this is handled experimentally
  (Part II §3: three guides in regions divergent from BICRA, plus explicit off-target screening against the BICRA
  locus).
- **Copy-number co-amplification:** |r| ≤ 0.06 for all five supporting partners.
- **Hub-driven call:** hub share 0.00.
- **Lineage artefact: not excluded, but bounded.** Lymphoid lines are the most dependent group and removing them
  changes the label — yet the replacement term is still a chromatin term and the neighbourhood overlap stays at 0.72.
  The experiment is nevertheless run in Soft Tissue and Bowel lines, outside the implicated lineage.
- **Expression-driven (type e):** ρ(effect, own expression) = −0.039; TF enrichment OR 1.07 — no support. (Recomputed †
  cross-check: BICRAL's effect vs **BICRA's** expression ρ = −0.057, n = 1292 — i.e. the dependency is not simply
  tracking how much paralogue is around at the mRNA level, which is a mild argument that paralogue buffering, if it
  exists, is not a straightforward transcript-abundance effect.)
- **Multifunctional-partner artefact:** three of the five term-supporting partners (CREBBP, EP300, SP1) are highly
  pleiotropic chromatin/transcription proteins that appear in many neighbourhoods. This is a real weakness of the
  *term*, and it is why the V1′ complex label and the top-2 partners carry the argument rather than the GO label.
- **Curation lag rather than discovery:** the honest framing. The recall probe named the complex unprompted; UniProt
  and Complex Portal already record membership. What remains unpublished is the function and the dependency structure.

**Strongest competing biological hypothesis.** That BICRAL is a **dispensable passenger** in ncBAF — the 2026 cryo-EM
position [PMID:42377898] — and that the fitness signal reflects something indirect: for example, that BICRAL loss
destabilises BRD9 or SMARCD1 levels rather than complex function, or that the dependency is carried by the
transcriptional programme of the lines rather than by complex activity. A second competitor is that the dependency is a
**general SWI/SNF-dosage** effect, not an ncBAF-specific one. The separating experiments are in Part II §6: paralogue
cross-complementation (a dosage model predicts BICRA rescues BICRAL loss everywhere; a slot-specific model predicts
rescue only where the slot is the limiting factor) and complex-integrity westerns (a destabilisation model predicts
BRD9/SMARCD1 protein loss on BICRAL knockout).

## 9. Falsifying observations (written before §6 and §7 were read)

1. **Loss of BICRAL changes nothing about ncBAF in a BICRAL-dependent line.** Specifically: in Yamato, BICRAL knockout
   leaves BRD9 and SMARCD1 protein levels unchanged, leaves BRD9 chromatin occupancy at ncBAF sites (CTCF-associated
   and promoter sites) unchanged, and leaves ncBAF target-gene expression unchanged, while still producing a fitness
   defect no larger than a matched-essentiality control gene produces. That combination would say the fitness signal is
   not ncBAF function and would refute the relationship-type-a claim in its functional form.
2. **The dependency is not paralogue-specific.** Specifically: BICRA knockout phenocopies BICRAL knockout in the
   BICRAL-dependent line, and BICRAL knockout phenocopies BICRA knockout in the BICRA-dependent line, with no
   cross-complementation asymmetry — i.e. the lines differ in overall ncBAF dosage rather than in which paralogue they
   use. That would refute the one novel claim this report makes beyond the published membership.

## 10. Experiments

See **Part II** of this file (Template B).

## 11. Novelty and external benchmarks

Agreement with prior catalogues: **hu.MAP 3.0 made an equivalent assignment** (BICRAL in SWI/SNF complexes, very high
pair probabilities with ncBAF/BAF members); **Wainberg 2021** could not have — BICRAL's UniProt annotation score of 5
puts it outside their uncharacterised set, and the gene is not named in the retrieved text; **Replogle 2022** did not
measure the gene; **Predictomes** gives consistent but unremarkable pair scores. Pan et al. 2018 (PMID:29778836) is the
true methodological precedent: the same inference, from the same data type, for the paralogue GLTSCR1.

What is new here, stated narrowly: (i) the co-essentiality neighbourhood of BICRAL itself — SMARCD1 and BRD9 ahead of
everything else, SMARCA4 far behind — which is an **independent, orthogonal rediscovery** of a membership that GO's
D1 rule still does not record (the only experimental GO row is CC-only, PMID:29374058 IDA); and (ii) the
**paralogue-specific dependency pattern** between BICRAL and BICRA across the panel, which we did not find in the
literature as of 2026-10-30 and which is directly falsifiable (§9.2, Part II §6). What is **not** new: the complex
membership itself, which was published in 2018 and which the recall probe reproduced before seeing any of our data.
This gene is best reported as a **rediscovery with a refinement**, and it is exactly the kind of case the N2 class was
defined for.

## Appendix A. Evidence ledger

"Verified" = the PMID/DOI resolved through the Europe PMC REST API and the quoted span was found in the retrieved text
(abstract or full text as stated); project-file rows were checked against the file. No unverified rows are included.

| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| BICRAL is a 1079-aa protein with the GLTSCR1 domain (PF15249 / IPR015671, IPR052438), no TM or signal peptide, annotation score 5 | UniProt Q6AI39 (REST; last annotation update 2026-09-02) and `reports/data/BICRAL/bundle.md` §8 | "BRD4-interacting chromatin-remodeling complex-associated protein-like"; Pfam PF15249; InterPro IPR052438, IPR015671; length 1079 (text read: UniProt JSON + bundle table) | Y |
| UniProt records BICRAL as a GBAF component and as mutually exclusive with BICRA | UniProt Q6AI39 FUNCTION and SUBUNIT comments | FUNCTION: "Component of SWI/SNF chromatin remodeling subcomplex GBAF that carries out key enzymatic activities, changing chromatin structure by altering DNA-histone contacts within a nucleosome in an ATP-dependent manner." SUBUNIT: "Component of the SWI/SNF (GBAF) subcomplex, which includes at least BICRA or BICRAL (mutually exclusive), BRD9, SS18, the core BAF subunits…" (text read: UniProt JSON record) | Y |
| AlphaFold global pLDDT for Q6AI39 is 45.7 (AFDB v6) | AlphaFold DB API `https://alphafold.ebi.ac.uk/api/prediction/Q6AI39` | globalMetricValue 45.72, latestVersion 6 (text read: API JSON) | Y |
| BICRAL's only experimental GO row is a cellular-component IDA; the rest are NAS/IBA/IEA/TAS or the generic binding term — hence D1 True | `data/raw/go/current/goa_human.gaf.gz` (GOA 2026-05-21) | "BICRAL part_of GO:0016514 PMID:29374058 IDA 20180731 UniProt"; "BICRAL enables GO:0005515 PMID:32296183 IPI"; "BICRAL involved_in GO:0006338 PMID:29374058 NAS" (text read: GAF rows for BICRAL) | Y |
| GBAF is defined by the mutually exclusive paralogues GLTSCR1 / GLTSCR1L replacing an ARID protein | PMID:29374058 (DOI 10.1074/jbc.ra117.001065) | "We termed this complex GBAF because it incorporates two mutually exclusive paralogs, GLTSCR1 (glioma tumor suppressor candidate region gene 1) or GLTSCR1L (GLTSCR1-like), instead of an ARID protein." (text read: abstract) | Y |
| Knockout of GLTSCR1 or GLTSCR1L reduces proliferation and colony formation in PC3 | PMID:29374058 | "GLTSCR1 or GLTSCR1L knockouts in the metastatic prostate cancer cell line PC3 resulted in a loss in proliferation and colony-forming ability." (text read: abstract) | Y |
| GLTSCR1L purification resolves the full ncBAF complex (ncBAF core = SMARCC1, SMARCD1, GLTSCR1L) | PMID:30343899 (DOI 10.1016/j.cell.2018.09.032) | "GLTSCR1L purification resolved full ncBAF complexes" (text read: full text, PMC6791824) | Y |
| GLTSCR1 and GLTSCR1L each associate exclusively with BRD9 and not with BAF47 | PMID:30510198 (DOI 10.1038/s41467-018-07528-9) | "GLTSCR1 and GLTSCR1L each exclusively associate with BRD9" (text read: full text) | Y |
| In the reconstituted ncBAF cryo-EM structure, GLTSCR1L contacts SMARCC1 and SMARCD1 through a long helix | PMID:41402274 (DOI 10.1038/s41421-025-00858-1) | "GLTSCR1L interacts with coiled-coil SMARCC1 and SMARCD1 subunits mainly through a long helix" (text read: full text) | Y |
| The 2026 cryo-EM study finds BRD9 and GLTSCR1L largely dispensable for assembly and remodelling in vitro | PMID:42377898 (DOI 10.1093/jmcb/mjag020) | "The ncBAF-specific subunits BRD9 and GLTSCR1L are largely dispensable for complex assembly and nucleosome remodeling." (text read: abstract) | Y |
| ncBAF is defined by BRD9 and GLTSCR1/GLTSCR1L and lacks the ARID1/2 scaffold | PMID:42377898 | "The human non-canonical BAF (ncBAF) complex is uniquely defined by the presence of BRD9 and GLTSCR1/GLTSCR1L, as well as the absence of the ARID1/2 scaffold" (text read: abstract) | Y |
| ncBAF complexes localise to CTCF sites and promoters and are synthetic-lethal targets in synovial sarcoma and rhabdoid tumours (DepMap/Achilles-derived in part) | PMID:30397315 (DOI 10.1038/s41556-018-0221-1) | "ncBAF complexes uniquely localize to CTCF sites and promoters" (text read: abstract and full text) | Y |
| The GLTSCR domain of GLTSCR1/1L and the DUF3512 of BRD9 underlie the ncBAF dependency | PMID:30397315 | "the GLTSCR domain of GLTSCR1/1L and the DUF3512 of BRD9" (text read: full text) | Y |
| BRD9 defines a SWI/SNF sub-complex lacking SMARCB1 and is a vulnerability in rhabdoid tumours (Project Achilles-derived) | PMID:31015438 (DOI 10.1038/s41467-019-09891-7) | "BRD9 exists in a unique SWI/SNF sub-complex that lacks SMARCB1" (text read: abstract and full text) | Y |
| BRD9 is a component of SS18-SSX-containing BAF complexes in synovial sarcoma | PMID:30431433 (DOI 10.7554/eLife.41305) | "BRD9 is a component of SS18-SSX containing BAF complexes in synovial sarcoma cells" (text read: abstract and full text) | Y |
| SF3B1-mutant cancers repress BRD9, a component of ncBAF which also contains GLTSCR1 and GLTSCR1L | PMID:31597964 (DOI 10.1038/s41586-019-1646-9) | "non-canonical BAF chromatin-remodelling complex that also contains GLTSCR1 and GLTSCR1L" (text read: abstract) | Y |
| The BRD4 ET domain interacts with NSD3, JMJD6 and GLTSCR1 — an independent, non-DepMap corroboration of the neighbourhood's composition | PMID:21555454 (DOI 10.1128/mcb.01341-10) | "the extraterminal (ET) domain, whose function has to date not been determined, interacts with NSD3, JMJD6, CHD4, GLTSCR1" (text read: abstract) | Y |
| A 2026 expression survey states BICRA and BICRAL are important for proliferation in a prostate cancer line | PMID:42629553 (DOI 10.1186/s13072-026-00696-9) | "BICRA and BICRAL have been shown to be important for cell proliferation in a prostate cancer cell line" (text read: full text) | Y |
| Co-essentiality (RNAi/CRISPR fitness) had already placed the paralogue GLTSCR1 in a SMARCD1/BRD9 module in 2018 — prior art, DepMap-derived | PMID:29778836 (DOI 10.1016/j.cels.2018.04.011) | "one putative subunit, GLTSCR1, whose highest ranked fitness correlations were with SMARCD1 and BRD9" (text read: full text, PMC6152908) | Y |
| hu.MAP 3.0 assigns BICRAL to SWI/SNF complexes with very high pair probabilities | PMID:40425816 (DOI 10.1038/s44320-025-00121-5); `data/raw/humap3/hu.MAP3.0_complexes_…csv`; `…complex_pairs_genenames_20240930.pairsWprob` | "atlas of human protein complexes" (text read: title/abstract); complex row "huMAP3_03221.1,1,…,ARID1A SS18L1 ACTL6B SMARCA2 SMARCA4 SMARCB1 SS18 ARID2 BICRAL SMARCD3 PBRM1 ARID1B …"; pair rows "BICRAL BCL7C 0.9994122982025146", "SMARCA4 BICRAL 0.997423529624939" (text read: files) | Y |
| Replogle 2022 did not measure BICRAL | PMID:35688146 (DOI 10.1016/j.cell.2022.05.013); `results/ledger/support_sources.tsv` | "genome-scale Perturb-seq" (text read: title/abstract); ledger note "g not measured" for PerturbSeq_K562_GW, PerturbSeq_K562_essential, PerturbSeq_RPE1_essential | Y |
| Wainberg 2021 is the benchmark co-essentiality prediction list; BICRAL is not named in its retrieved full text and would be out of scope (annotation score 5 > 2) | PMID:33859415 (DOI 10.1038/s41588-021-00840-z); UniProt Q6AI39 | "co-essential modules assigns function to uncharacterized genes" (text read: title/abstract and full text; BICRAL/GLTSCR1L do not occur in it); UniProt annotationScore 5 | Y |
| Predictomes pairs BICRAL with ncBAF members at moderate scores | `results/m7/scratch_reports_inafm1/predictome_BICRAL.csv` (from `data/raw/predictomes2025/…csv.gz`) | "BICRL_HUMAN__SMRD1_HUMAN__1594aa,Q6AI39:Q96GM5,0.468,0.420,28,994,976,3,4,0"; "BICRL_HUMAN__BRD9_HUMAN__1676aa,Q6AI39:Q9H8M2,0.438,0.756,48,999,997,2,0,0" (text read: file; 88 rows) | Y |
| Raw Chronos correlations: BICRAL–SMARCD1 r = 0.268, BICRAL–BRD9 r = 0.252, BICRAL–BICRA r = 0.164, BICRAL–SMARCA4 r = 0.081 (n = 1361) | recomputed † `results/m7/scratch_reports_inafm1/depmap_checks.py` → `depmap_checks.out` | "BICRAL vs SMARCD1 pearson r=0.268 spearman=0.284 n=1361"; "BICRAL vs BICRA pearson r=0.164 spearman=0.175 n=1361" (text read: script output) | Y |
| Paralogue-switching example: Yamato BICRAL −0.58 / BICRA +0.13; SYO-1 BICRAL +0.02 / BICRA −0.43; both lines BRD9-dependent (−0.86 / −0.80) | recomputed † same script | "Yamato ACH-001277 effects: {… 'BICRAL': -0.58, 'BICRA': 0.13, 'BRD9': -0.86, 'SMARCD1': -0.75}"; "SYO-1 ACH-001275 effects: {… 'BICRAL': 0.02, 'BICRA': -0.43, 'BRD9': -0.8, 'SMARCD1': -0.59}" (text read: script output) | Y |
| BICRAL's effect does not track BICRA mRNA abundance (ρ = −0.057, n = 1292) | recomputed † same script | "BICRAL effect vs BICRA expr spearman=-0.057 p=0.041 n=1292" (text read: script output) | Y |
| MRPS10 is a matched-essentiality control (−0.57 in ACH-001277, −0.74 in ACH-003337 vs BICRAL −0.58 / −0.74) from an unrelated module | recomputed † `results/m7/scratch_reports_inafm1/matched_ctrl.py` | "MRPS10 -0.57 -0.74 -0.63 0.27" (text read: script output) | Y |
| All numeric prediction, robustness, orthogonal and cell-line values in §1–§6 and Part II §2 | `reports/data/BICRAL/bundle.md` (machine-generated from `results/ledger/*`) and `results/ledger/top40_primary.tsv` row rank 33 | bundle tables §1–§10, copied without retyping (text read: file) | Y |
| Blinded judging outcome: real supported (+1 by both judges), 0/3 decoys, d = +1.0; top-40 primary 18/40 vs 3/120, p = 0.0002174 | `results/m7/judge/analysis_main_genes.tsv`, `results/m7/judge/scores/J1_main1.tsv`, `.../J2_main1.tsv`, `results/m7/judge/analysis_main.md` | "J030 HGNC:21111 BICRAL top40 33 1.0 0.0 0 1.0 N2"; "J030 C 1 Rows 1,2,5: component of GBAF/ncBAF SWI/SNF chromatin remodelling complex."; "real supported 18, unaddressed 20, contradicted 2; decoys supported 3/120" (text read: files) | Y |
| LLM recall probe recognised the gene and named the complex before any network output | `results/m7/recall_probe_90.tsv` via `reports/data/BICRAL/bundle.md` §9 | "recognised: **yes**; confidence: medium"; recalled function "GLTSCR1L, a subunit of the non-canonical (GBAF/ncBAF) SWI/SNF chromatin remodelling complex." (text read: bundle) | Y |
| p_cal means the probability that the top term is confirmed by D1-evidence annotation within ~8 years, and calibration is not poor | `DESIGN.md` §3.7; `results/holdout_eval/SUMMARY.md` | "p_cal = probability that the top term is confirmed by D1-evidence annotation within ~8 years (conservative)."; "slope 95% CI includes 1 and intercept 95% CI includes 0 (Wald) -> calibration not poor" (text read: files) | Y |

## Appendix B. Red-team review

Written by a separate agent that argues the artefact explanation (hub, mitochondrial or ribosomal dominance, proximity,
lineage, multifunctional partners, curation lag). Appended unedited.

- Reviewer / model / date: **pending**
- Review text: **pending**
- Lint result (claims without a verified source): **pending**
- PI response (separate, below the review): **pending**

---

# Part II — Template B: experiment plan

## 1. Context

- Gene: **BICRAL** | hypothesis: BICRAL functions in / supports transcription coregulator binding (GO:0001221) as a
  subunit of the GBAF/ncBAF complex, with a **paralogue-specific** cellular requirement relative to BICRA |
  relationship type: **a (stable subunit; P/A/S rule gave a via A+L support, and physical membership is published)** |
  novelty class: **N2**
- LLM-recall-probe flag: **known** (the complex was named by the probe agent unprompted) | calibrated probability:
  **p_cal = 0.0415** (family "other") | tier: **none (p_cal fill, rank 33)**
- Strongest alternative explanation: BICRAL is a dispensable passenger in ncBAF (the 2026 cryo-EM position) and the
  fitness signal is indirect — paralogue dosage or subunit destabilisation rather than complex function.
- **Decisive experiment (one sentence):** single and double knockout of BICRAL and BICRA, with reciprocal
  cross-complementation, in a BICRAL-dependent line (Yamato) and a BICRA-dependent line (SYO-1) of the same disease,
  reading fitness, ncBAF integrity and ncBAF target-gene expression.
- Falsifying observation (copied from Template A §9): BICRA knockout phenocopies BICRAL knockout in the
  BICRAL-dependent line and vice versa, with no cross-complementation asymmetry — i.e. the lines differ in ncBAF dosage,
  not in paralogue usage.

## 2. Cell lines (selection rule)

Rule: two dependent lines with Chronos ≤ −0.5 for g and ≤ −0.3 for the top partner, g expressed (log2(TPM+1) ≥ 2),
locus not amplified, high screen quality, preferably TP53-null. **Criterion applied: relaxed — the partner criterion
was dropped** (funnel: 1361 lines → 4 with g ≤ −0.5 → 1 also passing the SMARCD1 ≤ −0.3 criterion). As for the
companion gene, this is a consequence of a flat profile and is stated rather than hidden.

Chosen dependent lines (`reports/data/BICRAL/bundle.md` §10):

| ModelID | name | lineage / disease | g effect | partner (SMARCD1) effect | g expr log2(TPM+1) | g CN | TP53 | NNMD / ROCAUC | medium |
|---|---|---|---|---|---|---|---|---|---|
| ACH-001277 | **Yamato** | Soft Tissue, **synovial sarcoma** | −0.58 | −0.75 | 3.55 | 1.06 | mut | −4.45 / 0.93 | DMEM + 20% FBS + 1 mM sodium pyruvate (MF-002-017) |
| ACH-003337 | HCM-CSHL-0143-C20 | Bowel, colorectal adenocarcinoma | −0.74 | −0.10 | 3.28 | 0.98 | WT | −4.14 / 0.93 | Organoid Media Formulation #1 (MF-051-001) |

Control line that expresses g but does not depend on it, same lineage as line 1:

| ModelID | name | lineage / disease | g effect | partner effect | g expr | TP53 | NNMD / ROCAUC | medium |
|---|---|---|---|---|---|---|---|---|
| ACH-001275 | **SYO-1** | Soft Tissue, **synovial sarcoma** | +0.02 | −0.59 | 3.22 | WT | −5.96 / 0.96 | DMEM + 20% FBS + 1 mM sodium pyruvate (MF-002-017) |

The Yamato / SYO-1 pair is the asset of this design and the reason the control line does more than control: **same
disease, same medium, both BRD9-dependent (−0.86 and −0.80 †), opposite paralogue dependency (Yamato BICRAL −0.58 /
BICRA +0.13; SYO-1 BICRAL +0.02 / BICRA −0.43 †)**. The decisive experiment is therefore a within-disease comparison
rather than a cross-lineage one, which removes most of the lineage confound that §5 flags.

- Common-essential gene? **No** (0.29% of lines < −0.5). An **auxin-inducible degron (AID2) knock-in** arm is added
  anyway in Yamato, because ncBAF integrity and chromatin occupancy must be read before transcriptional adaptation.
  Controls for the knockout arm: guide-resistant cDNA rescue, 2 non-targeting guides, AAVS1 cutting control, and a
  control essential gene (below).
- Baseline medium: **the DepMap screen medium of each line** — DMEM + 20% FBS + 1 mM sodium pyruvate (MF-002-017) for
  Yamato and SYO-1; Organoid Media Formulation #1 (MF-051-001) for HCM-CSHL-0143-C20. Any inhibitor arm (e.g. a BRD9
  degrader) is a **sensitised condition analysed separately**, never the baseline.
- **Essential-gene confound control (required):** acute degron depletion of BICRAL time-matched to BRD9 degradation
  (dBRD9-type degrader or BRD9 degron), read against **MRPS10** — Chronos −0.57 in ACH-001277 and −0.74 in ACH-003337
  (BICRAL: −0.58 and −0.74), module = mitochondrial small ribosomal subunit, unrelated to chromatin remodelling.
  Secondary matched control if MRPS10 proves to affect transcription indirectly: GLE1 (−0.59 / −0.71) or
  TRMT6 (−0.59 / −0.71).

## 3. Reagents

- **3 sgRNAs against BICRAL, 3 against BICRA, 2 non-targeting, AAVS1 cutting control.** Sequences are **not listed
  here**: the project holds no guide library file and no guide-level DepMap data, and inventing 20-mers would be an
  unverified claim. Procedure: take the BICRAL and BICRA guides from the Avana library used in the DepMap screens that
  produced the effects above (plus Brunello as a second source), require that the 3 chosen BICRAL guides target exons
  encoding regions **outside** the paralogue-conserved GLTSCR domain where possible, and establish per-guide
  concordance inside the experiment (all 3 drop out in Yamato, none in SYO-1, all rescued by the cDNA).
- **Sequence-level off-target check of every guide**, with an explicit paralogue clause: genome-wide mismatch search
  (Cas-OFFinder, GRCh38, ≤ 3 mismatches, 1 DNA/RNA bulge); acceptance requires **no perfect or 1-mismatch site in any
  other protein-coding gene and specifically none in the BICRA locus** (and, for the BICRA guides, none in BICRAL), nor
  in BRD9, SMARCD1, SMARCA2/4, SMARCC1, SS18 or BCL7A/B/C. Result recorded in the experiment's ledger.
- CRISPRi guides if the locus is amplified: **not needed** (CN 1.06 and 0.98).
- Guide-resistant cDNAs: **BICRAL** and **BICRA** ORFs, doxycycline-inducible, each with silent PAM/seed changes for
  all three of its guides, in untagged and 3×FLAG–HA forms; plus a **GLTSCR-domain-deleted BICRAL** variant, because
  PMID:30397315 maps the ncBAF dependency to that domain, so it is the obvious structure–function handle.
- Validated antibody: commercial GLTSCR1L antibodies exist (e.g. the Thermo PA5-56126 reagent used in PMID:31597964)
  but western quality for GLTSCR1/L has been reported as a limiting factor (PMID:30431433 states their antibodies "do
  not facilitate consistent, quality western blotting"). The plan therefore uses **endogenous 3×FLAG–HA knock-in at the
  BICRAL and BICRA loci** as the primary detection route, with the antibody as corroboration only.
- Antibodies for partners and markers: BRD9, SMARCD1 (BAF60A), SMARCA4 (BRG1), SMARCC1 (BAF155), SMARCB1 (BAF47, the
  ncBAF-absent control), ARID1A (cBAF control), SS18, BCL7A, ACTL6A; CTCF (for occupancy co-analysis); lamin B1 and
  histone H3 as fractionation controls.

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of BICRAL with SMARCD1, BRD9, SMARCC1 (ipTM/pDockQ) | days | Confident interface, consistent with the published long-helix contact to SMARCC1/SMARCD1 | No interface | **Yes (cheap; confirmatory only)** | Expect an interface at the GLTSCR-domain/long-helix region; a negative is uninformative given pLDDT 45.7, and Burke 2023 already modelled 18 pairs with 0 above pDockQ 0.23 |
| 1 | Competitive growth (GFP/RFP mix), 3 guides + rescue: Yamato and HCM-CSHL-0143-C20 vs SYO-1 | 2–3 wk | Dropout in Yamato and HCM-CSHL-0143-C20, none in SYO-1, rescued by guide-resistant BICRAL cDNA | No dropout (effect does not reproduce) or no rescue (off-target, most plausibly BICRA cross-targeting) | **Yes — gate** | ≥ 15–25% depletion of guide⁺ cells by day 21 in Yamato (Chronos −0.58) and HCM-CSHL-0143-C20 (−0.74); ≤ 5% in SYO-1; restored to ≤ 5% by cDNA; all 3 guides concordant |
| 1 | **Essential-gene confound control:** AID2 degron depletion of BICRAL time-matched to BRD9 degradation, vs MRPS10 at matched growth effect | 2–4 wk | ncBAF readouts (target-gene expression, BRD9 occupancy) move beyond MRPS10's change at equal growth inhibition | Same change as MRPS10 → general sickness | **Yes — required** | At 2/6/24 h after auxin: ncBAF target-gene panel changes ≥ 2 SD beyond MRPS10 controls while total growth inhibition differs by < 20% |
| 1 | Localisation (endogenous FLAG–HA knock-in; IF + chromatin fractionation) | 2–4 wk | Nucleoplasmic, chromatin-bound | Cytoplasmic-only or absent from chromatin | **Yes** | HPA already calls nucleoplasm (+ cytosol) with Approved reliability; the knock-in makes it line-specific and quantitative (chromatin-bound fraction ≥ 30% of total) |
| 1 | **Module-specific readout after KO** (see §5) | 2–4 wk | Phenocopies partial BRD9 loss: loss of BRD9/SMARCD1 occupancy at ncBAF (CTCF-associated and promoter) sites and loss of ncBAF target-gene expression | Occupancy and expression unchanged | **Yes — decisive readout** | CUT&RUN for BRD9 and SMARCA4: ≥ 30% loss of BRD9 signal at ncBAF-specific peaks (CTCF-proximal/promoter) with cBAF-specific enhancer peaks spared; RNA-seq: significant overlap (hypergeometric p < 1e-5) with the dBRD9 signature in the same line |
| 1 | Partner protein levels after BICRAL KO (and the reverse) | 2 wk | Co-destabilisation of BRD9 / SMARCD1 (expected for a/b) | Partners stable → favours a "targeting/occupancy" rather than "stability" role, and is the key discriminator against the destabilisation alternative in §8 | **Yes** | Western ± glycerol-gradient fractionation; a ≥ 30% change in BRD9 or SMARCD1 is called; SMARCB1 and ARID1A as unchanged specificity controls |
| 2 | FLAG IP-MS of endogenous BICRAL vs an unrelated tagged nuclear control | 1–2 mo | ncBAF subunits enriched (SAINT BFDR ≤ 0.01): BRD9, SMARCD1, SMARCC1, SMARCA2/4, ACTL6A, SS18, BCL7A/B/C; **BICRA absent** (mutual exclusivity) | Other modules appear, or BICRA co-purifies (mutual exclusivity violated) | **Yes** | The BICRA-absence prediction is itself a crisp falsifiable test of the curated mutual exclusivity in the two lines |
| 2 | Glycerol-gradient / BN-PAGE co-migration ± BICRAL KO | 1 mo | BICRAL co-migrates with ncBAF; its loss shifts BRD9 to lighter fractions (sub-complexes) | Separate migration, or no shift | **Yes** | Compare against PMID:30343899, which resolved full ncBAF and sub-complexes by this method |
| 2 | **Double KO with BICRA (epistasis) + reciprocal cross-complementation** | 1–2 mo | In Yamato: BICRAL KO hurts, BICRA KO does not, double KO ≈ BICRAL KO, and **BICRA cDNA rescues BICRAL KO**; mirror-image in SYO-1 | Additive effects, or no cross-rescue, or both single KOs hurt equally | **Yes — this is the decisive arm** | 2×2 KO matrix in both lines, each ± BICRAL cDNA and ± BICRA cDNA; readouts = competitive growth and the ncBAF target panel |
| 2 | Arrayed CRISPRi Perturb-seq: BICRAL, BICRA, BRD9, SMARCD1, SMARCA4, SMARCB1 | 2 mo | BICRAL clusters with BRD9/SMARCD1, apart from SMARCA4/SMARCB1 | Distinct | Optional | Also fills the G-class gap that §6 records as "not measured" (Replogle 2022 never measured BICRAL) |
| 3 | GLTSCR-domain deletion and point mutants fail to rescue; reconstitution with recombinant ncBAF ± BICRAL | 6–12 mo | The domain mapped by PMID:30397315 is required in cells, reconciling with the cryo-EM "dispensable in vitro" result | Mutants rescue fully | Later | Only after Tier 1–2 |

Type-specific rows: relationship type is **a**, for which the template defines no extra row (the b/c/e rows are
deleted). The Tier-2 IP-MS and co-migration rows above are the type-a evidence the template expects.

## 5. Module readouts

The module (GBAF/ncBAF chromatin remodelling) is not one of the listed rows, so the "Other" row applies:

| Module | Readouts |
|---|---|
| Other — ncBAF/GBAF chromatin remodelling | (i) **BRD9 and SMARCA4 CUT&RUN** at ncBAF-specific sites: ncBAF "uniquely localize to CTCF sites and promoters" [PMID:30397315, verified in Appendix A], so loss of BRD9 signal at CTCF-proximal/promoter peaks with cBAF enhancer peaks spared is a complex-specific readout; (ii) **RNA-seq signature overlap with BRD9 degradation**, which "induces downregulation of oncogenic transcriptional programs" in synovial sarcoma [PMID:30431433]; (iii) **complex-integrity glycerol gradient / BN-PAGE**, the method that resolved ncBAF and its sub-complexes [PMID:30343899]; (iv) in synovial sarcoma specifically, SS18-SSX-target gene expression, since "BRD9 is a component of SS18-SSX containing BAF complexes in synovial sarcoma cells" [PMID:30431433] |

**Chosen readout:** *BRD9 CUT&RUN at ncBAF-specific (CTCF-proximal and promoter) sites plus the RNA-seq ncBAF target
panel*, in Yamato vs SYO-1, with BRD9 degradation as the positive comparator, MRPS10 as the matched-essentiality
control, and ARID1A/SMARCB1-dependent cBAF sites as the specificity control.

## 6. Experiment that separates the alternative explanation

- **Alternative:** BICRAL is a dispensable passenger and the dependency reflects ncBAF dosage (or subunit
  destabilisation) rather than a paralogue-specific functional slot.
- **Experiment:** the Tier-2 reciprocal cross-complementation matrix — BICRAL KO and BICRA KO, singly and together, in
  Yamato and SYO-1, each rescued with BICRAL cDNA or BICRA cDNA — run together with the partner-stability westerns.
- **Readout if the prediction (paralogue-specific slot) is right:** in Yamato, BICRAL KO causes dropout and loss of
  BRD9 occupancy/targets, BICRA KO does not, the double KO is no worse than BICRAL KO alone, and **BICRA cDNA rescues**
  (the slot can be refilled); the mirror pattern holds in SYO-1; BRD9 and SMARCD1 protein levels are not reduced.
- **Readout if the alternative is right:** either both single KOs produce comparable defects in both lines with
  additive double KOs (dosage model), or BICRAL KO reduces BRD9/SMARCD1 protein levels (destabilisation model, in which
  case the phenotype is subunit stability rather than paralogue-specific function), or neither KO moves the ncBAF
  readouts beyond MRPS10 at matched growth effect (general sickness).

## 7. Decision rule (fixed in advance)

- **Supported:** dropout reproduced and rescued by guide-resistant cDNA **AND** the module-specific readout concordant
  (loss of BRD9 occupancy at ncBAF sites and of ncBAF target-gene expression, beyond the matched-essentiality control)
  **AND** localisation compatible (nucleoplasmic/chromatin-bound) **AND** Tier-2 physical or epistatic support (IP-MS
  recovery of ncBAF subunits without BICRA, or non-additive epistasis with BICRA).
- **Refuted:** dropout not rescued by the cDNA, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else — reported as such with a proposed alternative relationship type (most likely a
  downgrade from a to d, "acts in the ncBAF pathway", if membership holds but the cellular requirement does not).
- **Separately recorded, because it is the novel claim:** the paralogue-specificity result (§6) is reported as
  supported / refuted / ambiguous on its own, independently of the module call, since p_cal covers only the module term.

## 8. Evidence ledger (Part II)

| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| The chosen and control lines, their effects, expression, CN, TP53 status, screen quality and media are as tabulated; the partner criterion was dropped | `reports/data/BICRAL/bundle.md` §10 | "Rank-1 partner used for the partner criterion: **SMARCD1**. Criterion applied: relaxed: partner criterion dropped (g <= -0.5)."; "Funnel: n_lines 1361; g_le_m0p5 4; plus_partner_le_m0p3 1; plus_expr_ge2 1; plus_not_amplified 1." (text read: file) | Y |
| Yamato and SYO-1 have opposite paralogue dependency and are both BRD9-dependent | recomputed † `results/m7/scratch_reports_inafm1/depmap_checks.py` output | "Yamato ACH-001277 effects: {… 'BICRAL': -0.58, 'BICRA': 0.13, 'BRD9': -0.86 …}"; "SYO-1 ACH-001275 effects: {… 'BICRAL': 0.02, 'BICRA': -0.43, 'BRD9': -0.8 …}" (text read: script output) | Y |
| MRPS10 is matched on effect in the two chosen lines and belongs to an unrelated module | recomputed † `results/m7/scratch_reports_inafm1/matched_ctrl.py` output | "MRPS10 -0.57 -0.74 -0.63 0.27" (text read: script output) | Y |
| ncBAF localises to CTCF sites and promoters — the basis of the complex-specific occupancy readout | PMID:30397315 | "ncBAF complexes uniquely localize to CTCF sites and promoters" (text read: abstract and full text) | Y |
| The ncBAF dependency maps to the GLTSCR domain of GLTSCR1/1L — the basis of the domain-deletion construct | PMID:30397315 | "the GLTSCR domain of GLTSCR1/1L and the DUF3512 of BRD9" (text read: full text) | Y |
| BRD9 degradation produces a defined transcriptional signature in synovial sarcoma — the positive comparator for the RNA-seq readout | PMID:30431433 | "BRD9 is a component of SS18-SSX containing BAF complexes in synovial sarcoma cells" (text read: abstract and full text) | Y |
| GLTSCR1/L westerns are unreliable, motivating endogenous tagging | PMID:30431433 | "current GLTSCR1/L antibodies do not facilitate consistent, quality western blotting" (text read: full text) | Y |
| Glycerol-gradient / density fractionation resolves full ncBAF and its sub-complexes with GLTSCR1L | PMID:30343899 | "GLTSCR1L purification resolved full ncBAF complexes in Fx 10–11 and subcomplexes in fractions 6–7" (text read: full text) | Y |
| BICRA and BICRAL are mutually exclusive in GBAF — the basis of the IP-MS "BICRA absent" prediction | UniProt Q6AI39 SUBUNIT; PMID:29374058 | "includes at least BICRA or BICRAL (mutually exclusive)"; "two mutually exclusive paralogs, GLTSCR1 … or GLTSCR1L …" (text read: UniProt record; abstract) | Y |
| Guide-level DepMap data are unavailable, so per-guide and shared-sgRNA checks happen inside the experiment | `reports/data/BICRAL/bundle.md` §5 | "Shared-sgRNA / per-guide check | not possible | guide-level data not available (recorded)" (text read: file) | Y |
| Burke 2023 modelled 18 pairs with BICRAL and none reached pDockQ ≥ 0.23 (low prior for Tier 0) | `reports/data/BICRAL/bundle.md` §6 | "Burke 2023 AF2: 18 modelled pairs with g; 0 with pDockQ ≥ 0.23: none" (text read: file) | Y |

## 9. Red-team review (Part II)

Separate agent; asks what would make the experiment uninformative (off-target guides — here especially BICRA
cross-targeting, proximity effects, lineage dependence, rescue failure, assay insensitivity, antibody quality).
Appended unedited.

- Reviewer / model / date: **pending**
- Review text: **pending**
- PI response (separate): **pending**
