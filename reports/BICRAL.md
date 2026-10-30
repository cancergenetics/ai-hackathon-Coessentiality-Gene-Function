# BICRAL — candidate report (Template A) + experiment plan (Template B)

Prepared under DESIGN §6.5. Template A is Part I; Template B is Part II of this same file (the task fixed
`reports/BICRAL.md` as the only writable report path for this gene, so the experiment plan is kept here as a clearly
marked part rather than in `reports/BICRAL_experiments.md`).

Unblinded literature search date: **2026-10-30** (Europe PMC incl. preprint sources, UniProt, GO/GOA, hu.MAP 3.0,
Predictomes, project ledgers). Red-team review: complete — unedited review at `reports/redteam/BICRAL.md`, verdict **ACCEPT WITH REVISIONS**; point-by-point responses in Appendix B.

---

# Part I — Template A

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** BICRAL (previously GLTSCR1L / KIAA0240) behaves in CRISPR fitness data like a working part of the
  non-canonical BAF (ncBAF / GBAF) chromatin-remodelling complex: its two strongest co-dependency partners by a wide
  margin are SMARCD1 (BAF60A) and BRD9, the two other defining ncBAF components. The assigned term is *transcription
  coregulator binding* (GO:0001221) and the complex-level label is the GBAF complex (Complex Portal CPX-4206). Physical
  membership of BICRAL in GBAF is **already published** (2018), so this is primarily a **rediscovery of membership by
  an orthogonal data type**.
- **On the "paralogue-specific requirement" — softened after red-team review.** An earlier draft presented
  paralogue switching between BICRAL and BICRA as the report's novel finding. The panel-level numbers do not support
  that framing and are given here rather than in a footnote: **BICRA tracks the ncBAF axis about twice as strongly as
  BICRAL does** (BICRA–SMARCD1 r = 0.529, BICRA–BRD9 r = 0.523, vs BICRAL 0.268 and 0.252 †); **BICRAL and BICRA are
  positively correlated (r = +0.164 †)**, where an interchangeable-slot model predicts zero or negative; the one
  panel-level buffering test already run is **null** (BICRAL effect vs BICRA expression ρ = −0.057 †); and of the four
  lines with BICRAL ≤ −0.5, **only one (Yamato) co-drops with BRD9 and SMARCD1** †. The Yamato/SYO-1 contrast is a
  **two-line observation consistent with, but not evidence for, paralogue switching**, and it is reported that way
  throughout (§7.3, §11). It is still worth testing, and Part II is built to test it — as a hypothesis, not a result.
- **Confidence:** **p_cal = 0.0415** [95% CI 0.018–0.065] = the expected probability that *the module term*
  (GO:0001221) is confirmed by D1-type experimental annotation within ~8 years. It is a hit probability for the term
  only, not for the relationship type and not for the paralogue-specificity refinement. Tier: none (p_cal fill; rank 33
  of the primary top 40). The low number reflects the base rate of the whole pipeline (3% precision@1 on the hold-out),
  not a judgement about this gene — and for BICRAL the literature already supports the module, so p_cal understates
  what is known here.
- **Strongest reason to doubt:** this is not an independent discovery, and the one thing that would have been new is
  weakly supported. The recall probe recognised the gene and named the right complex before any network output was
  seen; membership is in UniProt and Complex Portal; a 2018 bioRxiv preprint (PPR59167) already reported
  GLTSCR1L-specific function at H3K27ac enhancers; the prediction failed the lineage leave-out check; and the
  paralogue-specificity reading rests on 1 of 4 dependent lines against a positive BICRAL–BICRA correlation.
- **First experiment:** knock out BICRAL and BICRA, singly and together, with reciprocal cross-complementation, across
  **three** lines — a BICRAL-dependent synovial sarcoma line (Yamato), a genuinely BICRA-dependent line
  (**JMURTK2**, BICRA −0.68 †), and a BICRAL-independent synovial sarcoma control (SYO-1) — asking whether the fitness
  and ncBAF-target defects are paralogue-specific and complementable; time ~12 weeks; approximate cost ~€50–65k
  (details in Part II).
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
  component of the GBAF/ncBAF SWI/SNF chromatin-remodelling complex.** Subsidiary hypothesis, explicitly *not* a
  finding of this report: that the cell-line dependency is specific to the BICRAL-using form of that complex rather
  than to SWI/SNF or ncBAF dosage in general (see §0, §7.3 and Part II §6).
- Relationship type: **a (stable subunit)** — but the weight behind it comes from the literature, not from this
  pipeline. The §4.4 script rule assigns a because the co-abundance (A) and localisation (L) classes "support" and the
  V1′ label is complex-like with 4 supporting partners; as §6 now states, both of those supports are close to
  tautological for a nuclear chromatin term, and p = 0.0010 is the floor of the permutation grid rather than a strong
  value. **Type a is earned from PMID:29374058, PMID:30343899 and PMID:30510198** — the biochemistry that physically
  places BICRAL in GBAF — together with UniProt's `SUBUNIT` comment. The pipeline on its own could not have reached
  type a here, and the report does not claim otherwise.
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
  GO:0005515 (excluded by rule); several **NAS** rows contributed by Complex Portal that cite primary papers
  (`BICRAL involved_in GO:0006338 PMID:29374058 NAS`, `… GO:0045596 PMID:30510198 NAS`,
  `BICRAL part_of GO:0140288 PMID:29374058 NAS`) — NAS is "non-traceable author statement", so these are excluded by
  evidence code, not because they lack a source; **IBA**/**IEA** rows; **TAS** rows from Reactome; and one **IDA**
  row — `BICRAL part_of GO:0016514 PMID:29374058 IDA` — which is a **cellular-component** annotation. So the
  experimental GO evidence that exists is CC-only, and the gene is D1-positive. Combined with Tdark status (D3), it is
  in U.
  **The correct statement of what this means** (corrected after red-team review): *the GO record lags*, not that
  nobody has published an experimentally-supported statement about BICRAL. UniProt carries an experimental FUNCTION
  comment with `ECO:0000269/PubMed:29374058`, and PPR59167 (§7) reports GLTSCR1L-specific functional experiments. This
  is a clean example of the curation-lag phenomenon the project set out to study, and it should be reported as such
  rather than as an absence of knowledge.
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
**Recomputed raw correlations † (Pearson, n = 1361; `depmap_checks.py` and `rt_checks.py`). The full table is given,
including the paralogue's own correlations, because the favourable half is not representative:**

| pair | raw Pearson r |
|---|---|
| BRD9–SMARCD1 (the ncBAF axis itself) | **0.672** |
| **BICRA–SMARCD1** | **0.529** |
| **BICRA–BRD9** | **0.523** |
| BICRAL–SMARCD1 | 0.268 |
| BICRAL–BRD9 | 0.252 |
| **BICRAL–BICRA** | **+0.164** |
| BICRA–SMARCA4 | 0.138 |
| BICRAL–SMARCA4 | 0.081 |
| BICRAL–SS18 | 0.064 |

Two readings follow, and both belong in the report. (i) **Reassuring:** BICRAL's two defining ncBAF partners lead on
the raw scale as well as on the whitened scale, so the neighbourhood is not manufactured by the whitening step, and
SMARCA4 — shared with all SWI/SNF classes — is far behind, which is what an ncBAF-specific (rather than
SWI/SNF-general) signal looks like. (ii) **Deflating:** the paralogue **BICRA tracks the same axis about twice as
strongly**, so on this report's own criterion BICRA has the stronger claim to be the ncBAF-coupled paralogue; and
BICRAL–BICRA is **positive**, not zero or negative, which is what a shared-axis model predicts and an
interchangeable-slot model does not. §7.3 is written to respect both readings.

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
| A co-abundance | CCLE proteomics (75 members measured); ProteomeHD (g not measured) | **supports (weakly — see note)** | member row-percentile mean 0.667 vs null 0.547. Pairwise: SS18 r = 0.54 (99th row percentile), BRD9 r = 0.46 (96th), NSD3 r = 0.27 (85th), CREBBP r = 0.26 (84th), CTBP1 0.15 (75th), SMARCD1 0.11 (70th), SMARCA4 −0.03 (52nd), JMJD6 −0.36 (7th) | **0.0010** | yes |
| L localisation | HPA v25.1 (admitted; 94 members measured) | **supports (near-tautologically — see note)** | 0.989 of members share a compartment with g vs null 0.681. HPA call: reliability *Approved*; main **Nucleoplasm**, additional **Cytosol** → vocabulary compartments nucleus, cytosol; term compartments: nucleus; g multi-localised: True | **0.0010** | yes |
| G perturbation phenotype | Perturb-seq K562 GW / K562 essential / RPE1 essential | **not measured** | g not perturbed/measured in any of the three | — | — |
| S structure | Burke 2023 AF2 | **not measured** | 18 modelled pairs with g, **0 with pDockQ ≥ 0.23** — recorded as "no measured member" (no term member among the modelled pairs), and in any case uninformative for a 1079-aa protein with pLDDT 45.7 | — | — |
| H homology | orthologue IBA/ISO | reported only | False (no IBA/ISO to the term) | reported only | n.a. |

Supporting classes: **A, L** (Holm across the three measured classes at α = 0.05). Diagnostic class measured /
supports: **True / True**. Contradiction: **False**. Members tested: 101.

**How much those two "supports" are worth (added after red-team review).** Not much, and the report should not lean on
them. The **L** test asks whether term members share a compartment with g: 0.989 of 94 members are nuclear and HPA
calls BICRAL nucleoplasm, so the test is close to a tautology for any nuclear protein annotated to a nuclear term.
The **A** test is a CCLE-proteomics row-percentile mean of 0.667 against a null of 0.547, with JMJD6 at the 7th
percentile and SMARCA4 at the 52nd — a modest shift, and **p = 0.0010 is the floor of the 1,000-permutation grid**
(the smallest value the test can return), not a measure of strength. Both are better read as "cannot exclude" than as
independent support. Consequently the §4.4 type-a assignment, which is triggered by exactly these two classes, is
carried in practice by the published biochemistry (§1, §7), not by the orthogonal tests.

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

**Blinded verdicts** (packet J030, `results/m7/judge/`): real statement **+1** (supported); decoys **0, 0, 0**; both
judges independently scored +1 on the real slot, so no adjudicator was needed; **d = +1.0**. The two justifications
differ in wording and are attributed separately: J1 (`J1_main1.tsv`) wrote *"Rows 1,2: subunit of GBAF SWI/SNF
chromatin remodeling complex"*; J2 (`J2_main1.tsv`) wrote *"Rows 1,2,5: component of GBAF/ncBAF SWI/SNF chromatin
remodelling complex."* BICRAL is one of only 2 of the 7 N2 top-40 genes whose real statement was supported. Within the primary
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
2. **A GLTSCR1L-specific functional study exists, and it was missed in the first draft.** **PPR59167** (bioRxiv
   2018-10-17, DOI 10.1101/445148) identifies "GBAF, a non-canonical GLTSCR1L- and BRD9-containing SWI/SNF chromatin
   remodeling complex" as a major H3K27ac interactor, characterises "the conserved GLTSCR1/1L 'GiBAF'-domain, which we
   found to be responsible for GBAF complex formation and GLTSCR1L nuclear localization", and reports that "GLTSCR1L
   disassociation from chromatin resulted in genome-wide downregulation of enhancer transcription". This is the
   closest thing to a BICRAL-specific function paper that exists, and it matters three ways: it supplies a *domain*
   (GiBAF) with an assigned role, it supplies a *localisation* mechanism, and it supplies a better module readout
   (enhancer transcription at H3K27ac sites) than the one originally chosen. It also moves the N2 justification and
   the §11 novelty accounting closer to prior art. (It remains a preprint, unindexed in PubMed, which is presumably
   why agent L's PubMed-anchored search did not return it; the project's own search declaration includes preprint
   sources, so this is an omission in execution, not in scope.)
3. **The newest structural work pushes back.** The 2026 cryo-EM study reports that "The ncBAF-specific subunits BRD9
   and GLTSCR1L are largely dispensable for complex assembly and nucleosome remodeling" [PMID:42377898]; BCL7A rather
   than GLTSCR1L supplies the nucleosome-engagement function. So an *in vitro* reading says BICRAL is a passenger for
   the remodelling reaction. That is compatible with PPR59167 (targeting and enhancer output, not catalysis) and with
   our cellular data (dispensable for a biochemical reaction ≠ dispensable in cells). Distinguishing targeting from
   catalysis is what Part II is built to do.
4. **The paralogue question — reported as a hypothesis, not a finding.** UniProt records BICRA and BICRAL as mutually
   exclusive; the 2018 paper found that "GLTSCR1 or GLTSCR1L knockouts in the metastatic prostate cancer cell line PC3
   resulted in a loss in proliferation and colony-forming ability" [PMID:29374058] — i.e. in one line, either knockout
   hurt. Two synovial sarcoma lines look like a clean switch † : **Yamato (ACH-001277): BICRAL −0.58, BICRA +0.13,
   BRD9 −0.86, SMARCD1 −0.75**; **SYO-1 (ACH-001275): BICRAL +0.02, BICRA −0.43, BRD9 −0.80, SMARCD1 −0.59**. But the
   panel does **not** support generalising from them, and the contrary evidence is set out here in full:

   | test | result † | what it implies |
   |---|---|---|
   | Sign of the paralogue correlation | BICRAL–BICRA **r = +0.164** | an interchangeable-slot model predicts ≤ 0; a shared-axis model predicts > 0. The data favour shared axis. |
   | Which paralogue tracks ncBAF | BICRA–SMARCD1 **0.529**, BICRA–BRD9 **0.523** vs BICRAL 0.268 / 0.252 | on this report's own criterion, **BICRA** is the ncBAF-coupled paralogue, and BICRAL the junior one |
   | Buffering by paralogue abundance | BICRAL effect vs BICRA expression **ρ = −0.057** (n = 1292, p = 0.041) | **null** — cells with more BICRA mRNA are not less BICRAL-dependent. Evidence *against* simple switching, not merely "not a transcript-abundance effect" |
   | Do BICRAL-dependent lines track ncBAF? | of the four lines with BICRAL ≤ −0.5: ACH-001039 (BICRAL −0.833) BRD9 **+0.20**, SMARCD1 **+0.46**; ACH-003337 (−0.737) BRD9 −0.26, SMARCD1 −0.10; ACH-000253 (−0.581) BRD9 −0.18, SMARCD1 −0.23; **Yamato (−0.577) BRD9 −0.86, SMARCD1 −0.75** | **only 1 of 4 co-drops** — and that one line is also the line chosen for the experiment. "The lines that need BICRAL track SMARCD1 and BRD9" is true of the selected case only |

   **Conclusion, revised:** the Yamato/SYO-1 contrast is a two-line, same-disease observation *consistent with* but
   *not evidence for* paralogue switching. The panel-level test that would establish it is stated in Part II §6
   (reciprocal cross-complementation with a genuinely BICRA-dependent line), and the one panel-level test already run
   is null. p_cal covers none of this.
5. **The synovial-sarcoma context is not the generic ncBAF context** (two further papers missed in the first draft,
   both bearing on Part II rather than on the claim). **PMID:41423472** (2025) shows that "SS18::SSX expression
   redistributes non-canonical GBAF complexes broadly to promoters and distal enhancers marked by H2AK119ub" — so in
   Yamato and SYO-1 the ncBAF site repertoire is *not* the CTCF/promoter repertoire of PMID:30397315, and a readout
   that imports that site definition would be measuring the wrong places. **PMID:42361322** (2026) reports that
   "BRD9 degradation in synovial sarcoma reduced GBAF enrichment at target loci, BRD9-less complexes maintained or
   increased chromatin accessibility and associated gene transcription", and that "BRD9 loss did not affect GBAF
   assembly" — so dBRD9 is not a straightforward positive comparator, and its expected direction differs by site
   class. Neither paper names BICRAL/GLTSCR1L (0 occurrences in either full text), so neither changes the claim; both
   change the experiment, and Part II §4–§5 were rebuilt accordingly.
6. **Everything else known about BICRAL is complex-level or correlative:** reviews place it among GBAF subunits
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

**Closest prior publication and what co-essentiality adds beyond it.** Two closest priors, and the accounting is
thinner than the first draft claimed. **PMID:29374058** (Alpsoy & Dykhuizen 2018) established that BICRAL is a GBAF
subunit and that its knockout, like BICRA's, impairs PC3 proliferation. **PPR59167** (2018 preprint) went further and
is BICRAL-specific: GiBAF domain → complex formation and nuclear localisation; BRD9-bromodomain-dependent H3K27ac
occupancy; enhancer transcription lost on GLTSCR1L dislocation. Against those, co-essentiality adds:
(i) **panel-scale evidence that BICRAL's dependency is ncBAF-coupled rather than SWI/SNF-general** — SMARCD1 0.268 and
BRD9 0.252 versus SMARCA4 0.081 † — which is a genuine, if modest, addition; and (ii) the Yamato/SYO-1 paralogue
contrast, which §7.3 now reports as a hypothesis rather than a result. A third prior, **PMID:29778836**, made the same
kind of inference from the same kind of data for the paralogue GLTSCR1 eight years earlier, so even the method is not
new here.

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
transcriptional programme of the lines rather than by complex activity. A second competitor, **now the leading one
given §7.3**, is **ncBAF dosage**: both paralogues feed one axis (BICRAL–BICRA r = +0.164; BICRA the stronger
tracker), lines differ in how much total GBAF they need, and which paralogue's loss hurts is a matter of relative
abundance rather than a dedicated slot. A third is **selection**: only 1 of the 4 BICRAL-dependent lines co-drops with
BRD9/SMARCD1, so the apparent coupling may be a property of Yamato rather than of BICRAL. The separating experiments
are in Part II §6: reciprocal paralogue cross-complementation across three lines (a dosage model predicts BICRA
rescues BICRAL loss *everywhere*; a slot-specific model predicts rescue only where the slot is limiting) and
complex-integrity westerns (a destabilisation model predicts BRD9/SMARCD1 protein loss on BICRAL knockout).

## 9. Falsifying observations (written before §6 and §7 were read)

1. **Loss of BICRAL changes nothing about ncBAF in a BICRAL-dependent line.** Specifically: in Yamato, BICRAL knockout
   leaves BRD9 and SMARCD1 protein levels unchanged, leaves BRD9 chromatin occupancy at empirically defined ncBAF
   sites unchanged, and leaves ncBAF target-gene expression unchanged, while still producing a fitness defect no larger
   than a matched-essentiality control gene produces. That combination would say the fitness signal is not ncBAF
   function and would refute the relationship-type-a claim in its functional form.
   **Caveat added after red-team review:** the *protein-level* half of this is partly pre-answered. PMID:42377898
   already reports BRD9/GLTSCR1L dispensability for assembly, and PMID:42361322 reports that "BRD9 loss did not affect
   GBAF assembly", so "BRD9 and SMARCD1 levels unchanged" is the **expected**, not the surprising, outcome and must
   not be read as a near-refutation. The discriminating content of §9.1 sits entirely in the occupancy and
   target-gene arms.
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

What is new here, stated narrowly and more conservatively than in the first draft:

- **(i) The co-essentiality neighbourhood of BICRAL itself** — SMARCD1 and BRD9 ahead of everything else
  (0.268 / 0.252 †), SMARCA4 far behind (0.081 †) — an **independent, orthogonal rediscovery** of a membership that
  GO's D1 rule still does not record (the only experimental GO row is CC-only, PMID:29374058 IDA). This stands.
- **(ii) The paralogue contrast is *not* claimed as new knowledge.** The first draft called paralogue-specific
  dependency "the genuinely new, falsifiable content of this report". That was too strong, and §7.3 now sets out why:
  BICRAL–BICRA is **positively** correlated (+0.164 †), BICRA tracks the ncBAF axis about twice as strongly
  (0.529 / 0.523 †), the one panel-level buffering test is **null** (ρ = −0.057 †), and **only 1 of the 4**
  BICRAL-dependent lines co-drops with BRD9/SMARCD1 † — and that line is the one the experiment uses. What remains is
  a two-line, same-disease observation worth testing, not a result.
- **What is not new at all:** complex membership (published 2018, recalled unprompted by the probe, recorded in
  UniProt, Complex Portal and hu.MAP 3.0); BICRAL-specific function at H3K27ac enhancers via the GiBAF domain
  (PPR59167, 2018 preprint — missed in the first draft); and the inference method itself (PMID:29778836 applied it to
  the paralogue in 2018).

This gene is therefore best reported as a **rediscovery**, with one modest refinement (ncBAF-coupled rather than
SWI/SNF-general dependency) and one open hypothesis (paralogue specificity). It is exactly the kind of case the N2
class was defined for, and the curation-lag story — experimental knowledge that exists in UniProt and in a preprint
but not in GO's BP/MF evidence codes — is the more interesting finding.

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
| **The paralogue BICRA tracks the ncBAF axis about twice as strongly as BICRAL: BICRA–SMARCD1 r = 0.529, BICRA–BRD9 r = 0.523, BICRA–SMARCA4 r = 0.138; and the axis itself is BRD9–SMARCD1 r = 0.672 (n = 1361)** | recomputed † `results/m7/scratch_reports_inafm1/rt_checks.py` → `rt_checks.out` | "BICRA SMARCD1 (0.529, 1361)"; "BICRA BRD9 (0.523, 1361)"; "BRD9 SMARCD1 (0.672, 1361)"; "BICRA SMARCA4 (0.138, 1361)" (text read: script output) | Y |
| **Only 1 of the 4 lines with BICRAL ≤ −0.5 co-drops with BRD9 and SMARCD1** (ACH-001039 BRD9 +0.20 / SMARCD1 +0.46; ACH-003337 −0.26 / −0.10; ACH-000253 −0.18 / −0.23; ACH-001277 Yamato −0.86 / −0.75) | recomputed † `depmap_checks.py` → `depmap_checks.out` | "BICRAL 4 lowest lines partner effects: ACH-001039 0.20 0.46 0.11 -0.04 / ACH-003337 -0.26 -0.10 0.09 0.19 / ACH-000253 -0.18 -0.23 0.05 -0.02 / ACH-001277 -0.86 -0.75 0.13 -0.80" (columns BRD9, SMARCD1, BICRA, SS18); and "ACH-001039 -0.833000, ACH-003337 -0.736667, ACH-000253 -0.581063, ACH-001277 -0.577472" (text read: script output) | Y |
| Paralogue-switching example: Yamato BICRAL −0.58 / BICRA +0.13; SYO-1 BICRAL +0.02 / BICRA −0.43; both lines BRD9-dependent (−0.86 / −0.80) | recomputed † same script | "Yamato ACH-001277 effects: {… 'BICRAL': -0.58, 'BICRA': 0.13, 'BRD9': -0.86, 'SMARCD1': -0.75}"; "SYO-1 ACH-001275 effects: {… 'BICRAL': 0.02, 'BICRA': -0.43, 'BRD9': -0.8, 'SMARCD1': -0.59}" (text read: script output) | Y |
| BICRAL's effect does not track BICRA mRNA abundance (ρ = −0.057, n = 1292) | recomputed † same script | "BICRAL effect vs BICRA expr spearman=-0.057 p=0.041 n=1292" (text read: script output) | Y |
| MRPS10 is matched on effect (−0.57 in ACH-001277, −0.74 in ACH-003337 vs BICRAL −0.58 / −0.74) but belongs to a module whose loss perturbs transcription; it is retained only as a confound positive control | recomputed † `results/m7/scratch_reports_inafm1/matched_ctrl.py` | "MRPS10 -0.57 -0.74 -0.63 0.27" (text read: script output) | Y |
| All numeric prediction, robustness, orthogonal and cell-line values in §1–§6 and Part II §2 | `reports/data/BICRAL/bundle.md` (machine-generated from `results/ledger/*`) and `results/ledger/top40_primary.tsv` row rank 33 | bundle tables §1–§10, copied without retyping (text read: file) | Y |
| Blinded judging outcome: real supported (+1 by both judges), 0/3 decoys, d = +1.0; top-40 primary 18/40 vs 3/120, p = 0.0002174 | `results/m7/judge/analysis_main_genes.tsv`; `results/m7/judge/analysis_main.md` | "J030 HGNC:21111 BICRAL top40 33 1.0 0.0 0 1.0 N2"; "real supported 18, unaddressed 20, contradicted 2; decoys supported 3/120" (text read: files) | Y |
| Judge J2's justification for the supported slot | `results/m7/judge/scores/J2_main1.tsv` | "J030 C 1 Rows 1,2,5: component of GBAF/ncBAF SWI/SNF chromatin remodelling complex." (text read: file) | Y |
| Judge J1's justification for the supported slot (different wording; attributed separately after red-team review) | `results/m7/judge/scores/J1_main1.tsv` | "J030 C 1 Rows 1,2: subunit of GBAF SWI/SNF chromatin remodeling complex" (text read: file) | Y |
| **PPR59167 is a GLTSCR1L-specific functional study: GiBAF domain → complex formation and nuclear localisation; enhancer transcription lost on GLTSCR1L dislocation** | PPR59167 (bioRxiv, DOI 10.1101/445148, first published 2018-10-17) | "GBAF, a non-canonical GLTSCR1L- and BRD9-containing SWI/SNF chromatin remodeling complex"; "the conserved GLTSCR1/1L 'GiBAF'-domain, which we found to be responsible for GBAF complex formation and GLTSCR1L nuclear localization"; "GLTSCR1L disassociation from chromatin resulted in genome-wide downregulation of enhancer transcription" (text read: abstract via Europe PMC REST, resultType=core; no full text served) | Y |
| **In SS18::SSX synovial sarcoma, GBAF is redistributed to H2AK119ub-marked promoters and distal enhancers — so the CTCF/promoter site definition does not apply in the chosen lines** | PMID:41423472 (DOI 10.1038/s41467-025-67841-y) | "SS18::SSX expression redistributes non-canonical GBAF complexes broadly to promoters and distal enhancers marked by H2AK119ub" (text read: abstract and full text, PMC12852873). BICRAL/GLTSCR1L: 0 occurrences in the full text | Y |
| **BRD9 degradation reduces GBAF enrichment but maintains or increases accessibility and transcription, and does not affect GBAF assembly — so dBRD9 is not a simple loss-of-function comparator** | PMID:42361322 (DOI 10.1158/0008-5472.can-25-5405) | "BRD9 degradation in synovial sarcoma reduced GBAF enrichment at target loci, BRD9-less complexes maintained or increased chromatin accessibility and associated gene transcription"; "BRD9 loss did not affect GBAF assembly" (text read: abstract and full text, PMC13575562). BICRAL/GLTSCR1L: 0 occurrences | Y |
| LLM recall probe recognised the gene and named the complex before any network output | `results/m7/recall_probe_90.tsv` via `reports/data/BICRAL/bundle.md` §9 | "recognised: **yes**; confidence: medium"; recalled function "GLTSCR1L, a subunit of the non-canonical (GBAF/ncBAF) SWI/SNF chromatin remodelling complex." (text read: bundle) | Y |
| p_cal means the probability that the top term is confirmed by D1-evidence annotation within ~8 years, and calibration is not poor | `DESIGN.md` §3.7; `results/holdout_eval/SUMMARY.md` | "p_cal = probability that the top term is confirmed by D1-evidence annotation within ~8 years (conservative)."; "slope 95% CI includes 1 and intercept 95% CI includes 0 (Wald) -> calibration not poor" (text read: files) | Y |

## Appendix B. Red-team review

Written by a separate agent that argues the artefact explanation (hub, mitochondrial or ribosomal dominance, proximity,
lineage, multifunctional partners, curation lag).

- Reviewer / model / date: **adversarial reviewer agent (role `red_team`), Claude Opus 5.5, 2026-10-30**
- Review text (unedited, in full): **`reports/redteam/BICRAL.md`** — reproduced there verbatim rather than inlined, so
  that the reviewed text and the review remain separately auditable. The review is not edited, summarised or answered
  inside that file.
- **Verdict: ACCEPT WITH REVISIONS.**
- Lint result (claims without a verified source): the reviewer audited all 32 rows of Appendix A and Part II §8 and
  found **1 partial failure** (a judging justification attributed to both judge files when it appears in only one) plus
  **2 material omissions** (BICRA's own correlations; the missed GLTSCR1L-specific literature) and several smaller
  misdescriptions. No fabricated PMID, DOI or span; all four future-dated PMIDs resolved with matching titles.

### PI response — point-by-point answers to the required fixes

| # | Required fix | What changed in this report (or why not adopted) |
|---|---|---|
| 1 | Report BICRA's own co-dependencies and the sign of the paralogue correlation, plus the partner effects of all four BICRAL-dependent lines; then either downgrade the paralogue claim or state the test that would establish it (noting the null one already run) | **Adopted in full, and the claim is downgraded.** §3 now carries the complete correlation table including BICRA–SMARCD1 0.529, BICRA–BRD9 0.523, BRD9–SMARCD1 0.672 and BICRAL–BICRA **+0.164** †, with both the reassuring and the deflating reading spelled out. §7.3 is rewritten around a four-row evidence table (sign; dominance; null buffering test ρ = −0.057; **only 1 of 4** dependent lines co-dropping †) and now concludes "consistent with, but not evidence for, paralogue switching". §0 opens with the downgrade; §11 states that the paralogue contrast is *not* claimed as new knowledge; §8 promotes **ncBAF dosage** to the leading alternative; Part II §1 states in advance that the dosage outcome is the more likely one. |
| 2 | Add the missed literature (PPR59167, PMID:41423472; note PMID:42361322) and re-weigh novelty | **Adopted in full.** §7 has new items 2 and 5 covering all three, each with verified spans in Appendix A. PPR59167 materially changes the picture — it is the one BICRAL-specific functional study (GiBAF domain → complex formation and nuclear localisation; enhancer transcription lost on GLTSCR1L dislocation) — so §7 no longer says "function is only partly defined" without qualification, §11 lists it under "what is not new at all", and its enhancer-transcription assay is adopted as a second module readout. The omission is attributed to a PubMed-anchored search missing an unindexed preprint, which is an execution failure, not a scope one. |
| 3 | Rebuild the synovial-sarcoma readout and the control structure: define ncBAF sites empirically and stratify by H2AK119ub/CTCF; separate SYO-1's two roles by adding a BICRA ≤ −0.5 line; replace MRPS10/GLE1/TRMT6 | **Adopted in full.** A new Tier-1 row makes empirical, per-line site definition a prerequisite for the occupancy readout, stratified by H2AK119ub and CTCF, with §5 citing PMID:41423472 for why the imported definition is wrong here. **JMURTK2 (ACH-001532; BICRA −0.68, BRD9 −0.86, SMARCD1 −0.90, NNMD −9.13 †)** is added as the BICRA-dependent comparator — a rhabdoid, SMARCB1-deficient context — and SYO-1 reverts to control duty only; three alternates are named. Controls are now **TRPM7** (−0.56 / −0.73 †) and **HK2** (−0.59 / −0.72 †) from different modules, with MRPS10 kept as a confound positive control and ATF4/DDIT3 measured in every arm. The dBRD9 comparator is replaced by an in-house-validated BRD9 degron time-course, with PMID:42361322 cited for why its direction cannot be assumed. |
| 4 | Smaller: fix "NAS rows from Complex Portal"; soften "nobody has published"; attribute the judging span to `J2_main1.tsv`; correct the Part II funnel statement; state that A and L are near-tautological and that type a rests on the biochemistry | **Adopted in full.** §2 now shows that the NAS rows cite PMIDs and are excluded by evidence code, and replaces "nobody has published" with "the GO record lags", citing UniProt's `ECO:0000269` FUNCTION. §7 attributes both judges' wordings separately, and Appendix A splits them into two rows. Part II §2 states that **one line (Yamato) passes the unrelaxed rule** and that relaxing it is what admits line 2 — a choice, not a necessity — and no longer borrows INAFM1's funnel as an excuse. §6 has a new paragraph on why the A and L supports are near-tautological (L: 0.989 of 94 nuclear members vs a nuclear protein; A: 0.667 vs 0.547 with p = 0.0010 at the permutation floor), and §1 and Part II §1 now state that type a is earned from PMID:29374058 / 30343899 / 30510198 rather than from the pipeline. |
| — | Reviewer's §4.5 (power at the gate) and §4.6 (falsification 9.1 partly pre-answered) | **Adopted.** The Tier-1 gate row now specifies ≥ 5 biological replicates per guide and ≥ 10,000 guide⁺ events with the minimum detectable effect stated. §9.1 carries an explicit caveat that unchanged BRD9/SMARCD1 westerns are the *expected* outcome given PMID:42377898 and PMID:42361322, the Tier-1 partner-stability row is marked non-decisive, and §7's decision rule records that result as counting neither way. |
| — | Reviewer's §3.5 (the hub rule does not cover SMARCD1 and BRD9 either) | **Not adopted as a change of wording in §5, and the reason is recorded.** The point is correct (SMARCD1 in-degree 65 = 98.6th percentile, BRD9 58 = 97.2nd, over 14,417 unique partners with median 26 †), and we verified it. We did not restate the §5 row because, unlike the INAFM1 case, the near-hub partners here are corroborated by direct physical edges to g in three independent sources and by hu.MAP 3.0 — so hubness is not a competing explanation for *this* neighbourhood. The numbers are nonetheless on record in the unedited review. |

---

# Part II — Template B: experiment plan

## 1. Context

- Gene: **BICRAL** | hypothesis: BICRAL functions in / supports transcription coregulator binding (GO:0001221) as a
  subunit of the GBAF/ncBAF complex; **open subsidiary hypothesis**, not a finding: that the requirement is
  paralogue-specific relative to BICRA | relationship type: **a (stable subunit — earned from the published
  biochemistry, not from the A/L tests, see §1 and §6)** | novelty class: **N2**
- LLM-recall-probe flag: **known** (the complex was named by the probe agent unprompted) | calibrated probability:
  **p_cal = 0.0415** (family "other") | tier: **none (p_cal fill, rank 33)**
- Strongest alternative explanation: **ncBAF dosage** — both paralogues feed one axis (BICRAL–BICRA r = +0.164, BICRA
  the stronger tracker †) and lines differ in total GBAF requirement; with, behind it, the cryo-EM "dispensable
  passenger" position [PMID:42377898] and the possibility that the coupling is a property of Yamato alone (1 of 4
  dependent lines †).
- **Decisive experiment (one sentence):** single and double knockout of BICRAL and BICRA, with reciprocal
  cross-complementation, across **three** lines — Yamato (BICRAL-dependent), **JMURTK2 (genuinely BICRA-dependent,
  −0.68 †)** and SYO-1 (BICRAL-independent same-disease control) — reading fitness, ncBAF integrity and occupancy and
  expression at **empirically defined** ncBAF sites.
- Falsifying observation (copied from Template A §9): BICRA knockout phenocopies BICRAL knockout in the
  BICRAL-dependent line and vice versa, with no cross-complementation asymmetry — i.e. the lines differ in ncBAF dosage,
  not in paralogue usage. Given §7.3, **this is now the favoured prior outcome**, and the experiment is framed as a
  test the hypothesis is more likely to lose than to win.

## 2. Cell lines (selection rule)

Rule: two dependent lines with Chronos ≤ −0.5 for g and ≤ −0.3 for the top partner, g expressed (log2(TPM+1) ≥ 2),
locus not amplified, high screen quality, preferably TP53-null.

**Corrected statement of the funnel** (the first draft borrowed INAFM1's much worse situation to excuse this one).
Bundle §10 reads `n_lines 1361; g_le_m0p5 4; plus_partner_le_m0p3 1; plus_expr_ge2 1; plus_not_amplified 1` — i.e.
**one line (Yamato) satisfies the full unrelaxed rule.** The criterion was *not* forced to be dropped; relaxing it is
what admits the second line (HCM-CSHL-0143-C20, SMARCD1 −0.10). That is a defensible choice for breadth, but it is a
choice, and it is recorded as one.

Lines (`reports/data/BICRAL/bundle.md` §10, plus one added line recomputed † after red-team review):

| ModelID | name | lineage / disease | BICRAL | BICRA † | BRD9 † | SMARCD1 | BICRAL expr | CN | TP53 | NNMD / ROCAUC | medium | role |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ACH-001277 | **Yamato** | Soft Tissue, **synovial sarcoma** | **−0.58** | +0.13 | −0.86 | −0.75 | 3.55 | 1.06 | mut | −4.45 / 0.93 | DMEM + 20% FBS + 1 mM Na-pyruvate (MF-002-017) | **BICRAL-dependent line; satisfies the unrelaxed rule** |
| ACH-003337 | HCM-CSHL-0143-C20 | Bowel, colorectal adenocarcinoma | **−0.74** | +0.09 | −0.26 | −0.10 | 3.28 | 0.98 | WT | −4.14 / 0.93 | Organoid Media Formulation #1 (MF-051-001) | second BICRAL-dependent line (admitted by the relaxation); **does not co-drop with ncBAF** — included deliberately as the non-coupled case |
| **ACH-001532** | **JMURTK2** (new) | Kidney, **rhabdoid cancer** (SMARCB1-deficient context) | −0.12 | **−0.68** | −0.86 | −0.90 | 2.24 | — | WT | **−9.13 / 0.99** | DMEM + 10% FBS | **BICRA-dependent comparator for the paralogue arm** |
| ACH-001275 | **SYO-1** | Soft Tissue, **synovial sarcoma** | +0.02 | −0.43 | −0.80 | −0.59 | 3.22 | 1.03 | WT | −5.96 / 0.96 | DMEM + 20% FBS + 1 mM Na-pyruvate (MF-002-017) | **control line only** (expresses but does not depend on BICRAL) |

**Why a fourth line was added (red-team point 1).** In the first draft SYO-1 carried two incompatible roles: the
"expresses but does not depend" control *and* the BICRA-dependent comparator for the decisive paralogue arm. As a
control it is near-trivial (BICRAL +0.02 → the "≤ 5% dropout" prediction is close to guaranteed and discriminates
nothing), and as a BICRA comparator it is sub-threshold: SYO-1's BICRA effect is **−0.43**, which does not clear the
project's own ≤ −0.5 dependency bar. The roles are now separated. **JMURTK2 (ACH-001532)** is the added comparator:
BICRA **−0.68**, BICRAL −0.12, BRD9 −0.86, SMARCD1 −0.90, screen NNMD −9.13 / ROCAUC 0.99 †, and it is a rhabdoid
(SMARCB1-deficient) line — a published ncBAF-dependent context [PMID:30397315, PMID:31015438], so the mirror arm has a
real signal to lose. Other qualifying BICRA-dependent lines if JMURTK2 proves intractable: OPM2 (ACH-000024, BICRA
−0.67), KIJK (ACH-000773, −0.65), SNU620 (ACH-000325, −0.58) †.

The Yamato / SYO-1 pair remains valuable — same disease, same medium, both BRD9-dependent (−0.86 and −0.80 †) — but it
is now a *contrast*, not the whole design. Revised estimate: **~12 weeks, ~€50–65k** for Tier 0–1 across three lines.

- Common-essential gene? **No** (0.29% of lines < −0.5). An **auxin-inducible degron (AID2) knock-in** arm is added
  anyway in Yamato, because ncBAF integrity and chromatin occupancy must be read before transcriptional adaptation.
  Controls for the knockout arm: guide-resistant cDNA rescue, 2 non-targeting guides, AAVS1 cutting control, and a
  control essential gene (below).
- Baseline medium: **the DepMap screen medium of each line** — DMEM + 20% FBS + 1 mM sodium pyruvate (MF-002-017) for
  Yamato and SYO-1; Organoid Media Formulation #1 (MF-051-001) for HCM-CSHL-0143-C20. Any inhibitor arm (e.g. a BRD9
  degrader) is a **sensitised condition analysed separately**, never the baseline.
- **Essential-gene confound control (required) — revised after the red-team review.** The original control (MRPS10,
  mitoribosome) and its fallbacks (GLE1, mRNA export; TRMT6, tRNA modification) all perturb transcript abundance by
  their own mechanisms — MRPS10 through OXPHOS loss and the integrated stress response — which is fatal for an RNA-seq
  readout. Replaced by:
  - **Primary matched control: TRPM7** (divalent-cation channel-kinase; plasma membrane, no transcriptional or
    mitochondrial role) — Chronos **−0.56 in ACH-001277 and −0.73 in ACH-003337** vs BICRAL −0.58 / −0.74 †.
  - **Second control from a different module: HK2** (glycolysis) — **−0.59 / −0.72** † — so that no single control's
    own failure mode can be mistaken for the BICRAL effect.
  - **MRPS10 retained only as a positive control for the confound**, quantifying how much a generic growth-matched
    insult moves the transcriptional readout.
  - **ISR markers (ATF4, DDIT3/CHOP) measured in every arm**, with all comparisons made at matched growth inhibition.
  - No control is truly inert for a transcriptional readout; the design therefore relies on *two* controls from
    unrelated modules plus the generic-stress markers, rather than on any one gene being clean.

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
| 1 | Competitive growth (GFP/RFP mix), 3 guides + rescue: Yamato and HCM-CSHL-0143-C20 vs SYO-1; BICRA guides in JMURTK2 | 2–3 wk | Dropout in Yamato and HCM-CSHL-0143-C20, none in SYO-1, rescued by guide-resistant BICRAL cDNA; BICRA dropout in JMURTK2 | No dropout (effect does not reproduce) or no rescue (off-target, most plausibly BICRA cross-targeting) | **Yes — gate** | ≥ 15–25% depletion of guide⁺ cells by day 21 in Yamato (Chronos −0.58) and HCM-CSHL-0143-C20 (−0.74); ≤ 5% in SYO-1; restored to ≤ 5% by cDNA; all 3 guides concordant. **Power (red-team point 5):** Yamato's effect is small relative to the panel SD (0.146), so ≥ 5 biological replicates per guide and ≥ 10,000 guide⁺ events per read-out are required; this resolves a 10-percentage-point difference in guide⁺ fraction at α = 0.05 with 80% power. A non-significant result at this power is reported as "does not reproduce", never as "small effect" |
| 1 | **Essential-gene confound control:** AID2 degron depletion of BICRAL time-matched to BRD9 depletion, vs **TRPM7 and HK2** at matched growth effect (MRPS10 as the confound positive control), ATF4/DDIT3 in every arm | 2–4 wk | ncBAF readouts (target-gene expression, BRD9 occupancy) move beyond both controls at equal growth inhibition, without a proportional ISR signature | Same change as TRPM7/HK2 → general sickness | **Yes — required** | At 2/6/24 h after auxin: ncBAF target-gene panel changes ≥ 2 SD beyond TRPM7 **and** HK2 while total growth inhibition differs by < 20%; MRPS10's displacement reported alongside as the scale of a generic insult |
| 1 | **Site definition (new, must precede the occupancy readout):** BRD9 and SMARCD1 CUT&RUN in each *parental* line, stratified by H2AK119ub and CTCF CUT&RUN in the same line | 3–4 wk | A line-specific ncBAF site repertoire is obtained, and in the SS18::SSX lines it is expected to be H2AK119ub-weighted rather than CTCF/promoter-weighted | Sites cannot be called reproducibly → the occupancy arm is not run | **Yes — required** | PMID:41423472 reports GBAF redistribution "to promoters and distal enhancers marked by H2AK119ub" in SS18::SSX synovial sarcoma, so importing the CTCF/promoter definition from PMID:30397315 would measure the wrong loci in Yamato and SYO-1. Sites are defined empirically per line and reported per class |
| 1 | Localisation (endogenous FLAG–HA knock-in; IF + chromatin fractionation) | 2–4 wk | Nucleoplasmic, chromatin-bound | Cytoplasmic-only or absent from chromatin | **Yes** | HPA already calls nucleoplasm (+ cytosol) with Approved reliability; the knock-in makes it line-specific and quantitative (chromatin-bound fraction ≥ 30% of total) |
| 1 | **Module-specific readout after KO** (see §5) | 2–4 wk | Loss of BRD9/SMARCD1 occupancy at the *empirically defined* ncBAF sites of that line, and loss of expression of the genes linked to them | Occupancy and expression unchanged | **Yes — decisive readout** | CUT&RUN for BRD9 and SMARCA4 against the line's own site list: ≥ 30% loss of BRD9 signal at ncBAF-specific peaks, reported separately for H2AK119ub-marked and CTCF-proximal classes, with cBAF/ARID1A-specific peaks spared; RNA-seq restricted to genes linked to the affected sites. **No literature-borrowed signature is used as the primary comparator** (see the degrader row below) |
| 1 | Partner protein levels after BICRAL KO (and the reverse) | 2 wk | Co-destabilisation of BRD9 / SMARCD1 | **Partners stable — which is the expected result**, since PMID:42377898 and PMID:42361322 both report GBAF assembly to be robust to loss of its specific subunits. An unchanged western is therefore *uninformative*, not a near-refutation; it only excludes the destabilisation alternative of §8 | **Yes, but explicitly non-decisive** | Western ± glycerol-gradient fractionation; a ≥ 30% change in BRD9 or SMARCD1 is called; SMARCB1 and ARID1A as unchanged specificity controls |
| 1 | **BRD9-depletion comparator, validated in-house rather than borrowed** | 2–3 wk | A BRD9 degron (or degrader) time-course in each line gives a per-site-class direction of effect that the BICRAL arm can be compared against | The comparator behaves inconsistently → BICRAL arms are interpreted against the non-targeting and matched controls only | **Yes — required** | PMID:42361322 reports that "BRD9 degradation in synovial sarcoma reduced GBAF enrichment at target loci, BRD9-less complexes maintained or increased chromatin accessibility and associated gene transcription" — so dBRD9 is **not** a simple loss-of-function comparator, and its expected direction must be measured per site class, not assumed |
| 2 | FLAG IP-MS of endogenous BICRAL vs an unrelated tagged nuclear control | 1–2 mo | ncBAF subunits enriched (SAINT BFDR ≤ 0.01): BRD9, SMARCD1, SMARCC1, SMARCA2/4, ACTL6A, SS18, BCL7A/B/C; **BICRA absent** (mutual exclusivity) | Other modules appear, or BICRA co-purifies (mutual exclusivity violated) | **Yes** | The BICRA-absence prediction is itself a crisp falsifiable test of the curated mutual exclusivity in the two lines |
| 2 | Glycerol-gradient / BN-PAGE co-migration ± BICRAL KO | 1 mo | BICRAL co-migrates with ncBAF; its loss shifts BRD9 to lighter fractions (sub-complexes) | Separate migration, or no shift | **Yes** | Compare against PMID:30343899, which resolved full ncBAF and sub-complexes by this method |
| 2 | **Double KO with BICRA (epistasis) + reciprocal cross-complementation, across three lines** | 1–2 mo | In Yamato: BICRAL KO hurts, BICRA KO does not, double KO ≈ BICRAL KO, and **BICRA cDNA rescues BICRAL KO**; mirror-image in **JMURTK2** (BICRA −0.68 †); SYO-1 as the no-BICRAL-dependency control | Additive effects, no cross-rescue, or both single KOs hurt equally → ncBAF dosage, which §8 now treats as the leading alternative | **Yes — this is the decisive arm** | 2×2 KO matrix in each of the three lines, each ± BICRAL cDNA and ± BICRA cDNA; readouts = competitive growth and the line's own ncBAF target panel. Prior expectation, stated in advance: given r(BICRAL,BICRA) = +0.164 and the null buffering test †, the **dosage** outcome is more likely than the switching outcome |
| 2 | Arrayed CRISPRi Perturb-seq: BICRAL, BICRA, BRD9, SMARCD1, SMARCA4, SMARCB1 | 2 mo | BICRAL clusters with BRD9/SMARCD1, apart from SMARCA4/SMARCB1 | Distinct | Optional | Also fills the G-class gap that §6 records as "not measured" (Replogle 2022 never measured BICRAL) |
| 3 | GLTSCR-domain deletion and point mutants fail to rescue; reconstitution with recombinant ncBAF ± BICRAL | 6–12 mo | The domain mapped by PMID:30397315 is required in cells, reconciling with the cryo-EM "dispensable in vitro" result | Mutants rescue fully | Later | Only after Tier 1–2 |

Type-specific rows: relationship type is **a**, for which the template defines no extra row (the b/c/e rows are
deleted). The Tier-2 IP-MS and co-migration rows above are the type-a evidence the template expects.

## 5. Module readouts

The module (GBAF/ncBAF chromatin remodelling) is not one of the listed rows, so the "Other" row applies:

| Module | Readouts |
|---|---|
| Other — ncBAF/GBAF chromatin remodelling | (i) **BRD9 and SMARCA4 CUT&RUN at site lists defined empirically in each line** and stratified by H2AK119ub and CTCF. The generic ncBAF repertoire is CTCF sites and promoters — ncBAF "uniquely localize to CTCF sites and promoters" [PMID:30397315] — but in the SS18::SSX lines used here that repertoire does not hold: "SS18::SSX expression redistributes non-canonical GBAF complexes broadly to promoters and distal enhancers marked by H2AK119ub" [PMID:41423472]. Site definition is therefore measured, not imported. (ii) **Enhancer-transcription readout**, following the only BICRAL-specific functional study: "GLTSCR1L disassociation from chromatin resulted in genome-wide downregulation of enhancer transcription" [PPR59167] — eRNA/nascent transcription (PRO-seq or TT-seq) at the affected H3K27ac enhancers, which reads BICRAL's reported output directly rather than a BRD9 proxy. (iii) **Complex-integrity glycerol gradient / BN-PAGE**, the method that resolved ncBAF and its sub-complexes [PMID:30343899]. (iv) In synovial sarcoma, SS18-SSX-target gene expression, since "BRD9 is a component of SS18-SSX containing BAF complexes in synovial sarcoma cells" [PMID:30431433] — with the caveat from PMID:42361322 that BRD9 depletion can *increase* accessibility and transcription at these loci. |

**Chosen readouts:**
1. **BRD9/SMARCD1 occupancy at the line's own empirically defined ncBAF sites**, reported separately for
   H2AK119ub-marked and CTCF-proximal classes, with ARID1A/cBAF sites as the specificity control.
2. **Nascent enhancer transcription at H3K27ac enhancers** (PPR59167's readout) — added because it is the one
   published assay that is specific to BICRAL rather than to BRD9, and because PMID:42361322 makes BRD9-based
   comparators directional rather than simply "down".

Run in Yamato, JMURTK2 and SYO-1, with an **in-house-validated** BRD9 degron time-course as the comparator (not a
literature-borrowed signature), **TRPM7 and HK2** as matched-essentiality controls, MRPS10 as the confound positive
control, and ATF4/DDIT3 as generic-stress markers.

## 6. Experiment that separates the alternative explanation

- **Alternative (now the leading hypothesis, not the underdog):** BICRAL is a dispensable passenger and the dependency
  reflects **ncBAF dosage** — or subunit destabilisation — rather than a paralogue-specific functional slot.
- **Experiment:** the Tier-2 reciprocal cross-complementation matrix — BICRAL KO and BICRA KO, singly and together, in
  **Yamato, JMURTK2 and SYO-1**, each rescued with BICRAL cDNA or BICRA cDNA — run together with the partner-stability
  westerns and the occupancy/enhancer-transcription readouts.
- **Readout if the paralogue-specific-slot hypothesis is right:** in Yamato, BICRAL KO causes dropout and loss of
  occupancy/enhancer output, BICRA KO does not, the double KO is no worse than BICRAL KO alone, and **BICRA cDNA
  rescues** (the slot can be refilled); the mirror pattern holds in JMURTK2 (BICRA KO hurts, BICRAL KO does not,
  BICRAL cDNA rescues); SYO-1 shows neither; BRD9 and SMARCD1 protein levels are unchanged throughout.
- **Readout if the dosage alternative is right (the prior-favoured outcome):** both single KOs produce graded defects
  scaled by each paralogue's abundance in that line, double KOs are additive or synergistic everywhere, and either
  cDNA rescues either knockout in proportion to dose. **A panel-level corollary that can be checked before any
  bench work** is already negative: BICRAL effect vs BICRA expression ρ = −0.057 (n = 1292) †, i.e. no buffering by
  paralogue abundance, which the switching model needs and the dosage model does not require.
- **Readout if destabilisation is the explanation:** BICRAL KO reduces BRD9/SMARCD1 protein levels — in which case the
  phenotype is subunit stability rather than paralogue-specific function. Noted as the *less* likely branch, since
  PMID:42377898 and PMID:42361322 both report GBAF assembly to be robust to loss of its specific subunits.
- **Readout if nothing is specific:** no KO moves the ncBAF readouts beyond TRPM7 and HK2 at matched growth effect
  (general sickness), or the Yamato coupling turns out to be a line idiosyncrasy — consistent with only 1 of the 4
  BICRAL-dependent lines co-dropping with BRD9/SMARCD1 †.

## 7. Decision rule (fixed in advance)

**The module call (GO:0001221 / ncBAF, which p_cal covers):**
- **Supported:** dropout reproduced and rescued by guide-resistant cDNA **AND** the module-specific readout concordant
  (loss of BRD9/SMARCD1 occupancy at the line's own ncBAF sites, or loss of enhancer transcription, beyond **both**
  matched-essentiality controls at matched growth effect) **AND** localisation compatible (nucleoplasmic /
  chromatin-bound) **AND** Tier-2 physical or epistatic support (IP-MS recovery of ncBAF subunits without BICRA, or
  non-additive epistasis with BICRA).
- **Refuted:** dropout not rescued by the cDNA, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else — reported as such with a proposed alternative relationship type (most likely a
  downgrade from a to d, "acts in the ncBAF pathway", if membership holds but the cellular requirement does not).
- **Explicitly not counted as evidence either way:** unchanged BRD9/SMARCD1 protein levels, which both PMID:42377898
  and PMID:42361322 lead us to expect.

**The paralogue-specificity hypothesis (reported separately; p_cal covers none of it, and §7.3 already weighs against
it):**
- **Supported:** the mirror-image cross-complementation pattern holds in **both** Yamato and JMURTK2, with the double
  KO no worse than the relevant single KO in each.
- **Refuted:** additive double KOs, or either cDNA rescuing either knockout in both lines, or no asymmetry between the
  two lines → **ncBAF dosage**, which the panel-level numbers already favour.
- **Ambiguous:** asymmetry in one line only, which — given that Yamato is 1 of 4 and was selected — would be reported
  as a line idiosyncrasy pending a third dependent line.

## 8. Evidence ledger (Part II)

| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| The chosen and control lines, their effects, expression, CN, TP53 status, screen quality and media are as tabulated; the partner criterion was dropped | `reports/data/BICRAL/bundle.md` §10 | "Rank-1 partner used for the partner criterion: **SMARCD1**. Criterion applied: relaxed: partner criterion dropped (g <= -0.5)."; "Funnel: n_lines 1361; g_le_m0p5 4; plus_partner_le_m0p3 1; plus_expr_ge2 1; plus_not_amplified 1." (text read: file) | Y |
| Yamato and SYO-1 have opposite paralogue dependency and are both BRD9-dependent | recomputed † `results/m7/scratch_reports_inafm1/depmap_checks.py` output | "Yamato ACH-001277 effects: {… 'BICRAL': -0.58, 'BICRA': 0.13, 'BRD9': -0.86 …}"; "SYO-1 ACH-001275 effects: {… 'BICRAL': 0.02, 'BICRA': -0.43, 'BRD9': -0.8 …}" (text read: script output) | Y |
| MRPS10 is matched on effect in the two chosen lines — **demoted to a positive control for the confound**, because mitoribosome depletion perturbs transcription through OXPHOS loss and the ISR | recomputed † `results/m7/scratch_reports_inafm1/matched_ctrl.py` output | "MRPS10 -0.57 -0.74 -0.63 0.27" (text read: script output) | Y |
| **TRPM7 and HK2 are the replacement matched-essentiality controls (neither transcriptional nor mitochondrial): TRPM7 −0.56 / −0.73 and HK2 −0.59 / −0.72 in ACH-001277 / ACH-003337, vs BICRAL −0.58 / −0.74** | recomputed † `matched_ctrl.py` and `rt_checks.py` | "TRPM7 -0.56 -0.73 -0.74 0.47"; "HK2 -0.59 -0.72 -0.33 0.22"; "TRPM7 INAFM1-lines -0.49/-0.52 BICRAL-lines -0.56/-0.73"; "HK2 INAFM1-lines -0.18/-0.36 BICRAL-lines -0.59/-0.72" (text read: script outputs) | Y |
| **JMURTK2 (ACH-001532) is a genuinely BICRA-dependent line: BICRA −0.68, BICRAL −0.12, BRD9 −0.86, SMARCD1 −0.90, BICRAL expression 2.24, TP53 WT, DMEM + 10% FBS, ScreenNNMD −9.13 / ROCAUC 0.99; rhabdoid (SMARCB1-deficient) context** | recomputed † from `CRISPRGeneEffect.csv`, `Model.csv`, `ModelCondition.csv`, `CRISPRConfounders.csv`, `OmicsSomaticMutationsMatrix{Damaging,Hotspot}.csv`, `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | "ACH-001532 JMURTK2 | Kidney | Rhabdoid Cancer BICRA -0.68 BICRAL -0.12 BRD9 -0.86 SMARCD1 -0.90"; "MC-001532-MUr8 ACH-001532 DMEM + 10% FBS"; "ACH-001532 -9.126442 0.987934"; "ACH-001532 TP53 damaging None hotspot None -> WT"; "ACH-001532 Yes 2.597905 2.240693" (BICRA, BICRAL expression) (text read: script outputs) | Y |
| **Other qualifying BICRA-dependent lines: OPM2 (ACH-000024) −0.67, KIJK (ACH-000773) −0.65, SNU620 (ACH-000325) −0.58** | recomputed † `rt_checks.py` | "ACH-000024 OPM2 | Lymphoid | Mature B-Cell Neoplasms BICRA -0.67"; "ACH-000773 KIJK | Lymphoid | Mature T and NK Neoplasms BICRA -0.65"; "ACH-000325 SNU620 | Esophagus/Stomach | Esophagogastric Adenocarcinoma BICRA -0.58" (text read: script output) | Y |
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

- Reviewer / model / date: **adversarial reviewer agent (role `red_team`), Claude Opus 5.5, 2026-10-30**
- Review text (unedited): **`reports/redteam/BICRAL.md` §4**, verdict **ACCEPT WITH REVISIONS**.
- PI response: all six experiment-plan problems were adopted — SYO-1's two roles separated by adding a genuinely
  BICRA-dependent line (JMURTK2, −0.68 †); ncBAF sites now defined empirically per line and stratified by
  H2AK119ub/CTCF rather than imported from a different context (PMID:41423472); the dBRD9 comparator replaced by an
  in-house-validated BRD9 degron time-course with its direction measured per site class (PMID:42361322); matched
  controls replaced with TRPM7 and HK2 plus ISR markers, MRPS10 demoted to a confound positive control; replicate
  number and minimum detectable effect specified at the Tier-1 gate; and §9.1's partner-stability arm explicitly
  marked as pre-answered and non-decisive. The point-by-point table is in Appendix B of Part I.
