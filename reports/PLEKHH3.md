# PLEKHH3 — candidate report (Template A) + experiment plan (Template B)

Prepared 2026-10-30. Numbers are copied from `reports/data/PLEKHH3/bundle.md` (machine-generated from `results/ledger/*`) or are marked † where recomputed for this report (scripts and outputs in `results/m7/scratch_reports_ccdc71l/`). Every non-ledger statement about gene function carries a key from Appendix A.

Deviation from the template's file layout (recorded, not a rule change): DESIGN §6.5 places Template B in `reports/PLEKHH3_experiments.md`; this assignment restricted writing to `reports/PLEKHH3.md`, so Template B is included below as Part II. Content and required fields are unchanged.

---

# Part I — Template A

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** PLEKHH3 is an uncharacterised PH–MyTH4–FERM protein whose fitness profile across 1,361 CRISPR-screened cancer lines runs with the **brakes on PI3K/AKT signalling**: its three top partners — PLEKHA1 (TAPP1), PTEN and PTPN13 (PTPL1) — are exactly the PI(3,4)P₂ adaptor/phosphatase module, and TSC1, TSC2 and DDIT4 follow immediately behind. Critically, this is a co-dependency among genes whose **knockout helps cells grow** (mean Chronos: PTEN +0.377, PLEKHA1 +0.219, PLEKHH3 +0.087 †), so the claim is that PLEKHH3 **restrains** PI3K/AKT output, in the same direction as PTEN and TAPP1, rather than being required for it. Relationship type **d, pathway member** ("functions in / supports regulation of PI3K/AKT signal transduction"); no subunit claim is made.
- **Confidence:** **p_cal = 0.0757** [95% CI 0.030–0.127] = the model-estimated probability that the *module term* (GO:0051896, regulation of phosphatidylinositol 3-kinase/protein kinase B signal transduction) is the term this gene later gains by direct-evidence GO annotation over a horizon like the hold-out's (≈8 years). It is a hit probability for the term only — not for the relationship type, not for the direction of the effect, and not a probability that the biology above is true. Tier: none (filled by p_cal; no gene in this study reached Tier A or B).
- **What makes this more than a 172-gene GO term firing by chance:** PLEKHA1 and PTEN are not merely high-ranking partners, they are PLEKHH3's **#1 and #2 correlates among all 18,433 genes** in the matrix (r = 0.424 and 0.400) †, and the signal is confined to the PI3K/mTOR brake set — TSC2 0.246 (rank 4), TSC1 0.240 (5), NPRL2 0.204 (8), DDIT4 0.193 (9), DEPDC5 0.187 (12) — while generic tumour suppressors are flat (TP53 **0.014**, ARID1A 0.015, APC 0.021, RB1 0.053, SMAD4 −0.049, CDKN2A −0.051) and the pathway's *accelerator* runs the other way (PIK3CA **−0.186**, rank 18,427 of 18,433) †. A generic "deleting any brake helps" covariate cannot produce that pattern.
- **Strongest reason to doubt:** the three supporting partners are **not three independent observations** — r(PTEN, PLEKHA1) = 0.453, so the effective support is ≈ 2 partners (partials: r(g,PTEN|PLEKHA1) = 0.257, r(g,PLEKHA1|PTEN) = 0.298) †, which is exactly why leave-one-partner-out is 0/3; one of the three (PTEN) is a network hub, leaving the prediction **one flag short of the §4.3 automatic exclusion**; and the whole profile is low-amplitude (mean +0.087, SD 0.160, only 2 of 1,361 lines below −0.5). A PI3K-pathway-*specific* state covariate therefore remains fully consistent with the data even though the generic version is excluded.
- **First experiment:** knock out / degrade PLEKHH3 in two **named PTEN-wild-type, solid-lineage** backgrounds — **LN-428** (ACH-000455, glioblastoma) and **OVCAR-5** (ACH-001151, high-grade serous ovarian) — and measure AKT pathway output (pAKT-S473/T308, pPRAS40, pS6) and PI(3,4)P₂ dynamics after growth-factor stimulation, against a guide-resistant cDNA rescue, a PH-domain point mutant and a knockdown-depth-matched control gene; time ≈ 8–10 weeks; approximate cost ≈ US$25–40k (details in Part II). These replace the rule-selected lines for the decisive readout: within Lymphoid — the lineage of both JURKAT and the LP-1 control — the predicted co-dependency **does not exist** (r(PLEKHH3, PTEN) = −0.037, n = 97), whereas it is 0.45–0.55 in CNS/Brain, Skin, Lung, Breast and Ovary †.
- Cancer-line essentiality is not organismal function: dependency in DepMap lines says the gene is needed for proliferation there, not what it does in the organism. For this gene the point is sharper still — PLEKHH3 is **not** a dependency in the usual sense; its loss is mildly *advantageous* in most lines, and the "dependent" lines used in Part II sit at the extreme tail of a distribution centred above zero.

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

- Symbol: **PLEKHH3** | HGNC ID: **HGNC:26105** | previous symbols: **none**; alias: **FLJ21019** | UniProt: **Q7Z736** | band: **17q21.2**
- D1 / D2 / D3 values: **True / False (UniProt annotation score 3) / True** (D3_pubmed True, D3_tdark True; focused PMIDs **0**, all PMIDs 22; TDL Tdark) | curation-lag audit flag: **not in the audit sample**
- Stratum (§1.4): family **other**; expression **expressed** (not lineage-restricted); informativeness tertile **high**; core **True** (headline stratum True; tool background True; low_coverage False)
- Hypothesis (one sentence): **PLEKHH3 functions in regulation of phosphatidylinositol 3-kinase/protein kinase B signal transduction (GO:0051896)**, as a negative regulator acting with the PI(3,4)P₂ adaptor/phosphatase arm (PLEKHA1/TAPP1 – PTPN13/PTPL1 – PTEN).
- Relationship type: **d** — type unresolved by the §4.4 script rule and unresolved by the evidence: no admitted orthogonal class supports the call after Holm correction (§6), so a type-(a) subunit claim is not permitted; coupling (ρ = 0.102) and TF (OR 0.51) flags are negative, so type e is not assigned by rule — but type e remains the leading alternative (§8).
- Novelty class: **N3** (agent L; `results/m7/L/HGNC_26105.md`; L's search covered PLEKHH3, FLJ21019, Q7Z736 and a 97-hit full-text sweep, all expression/omics/association mentions).
- LLM-recall-probe flag (§6.2): **not known** ("recognised: no; confidence: low; recalled function: 'Protein with PH, MyTH4 and FERM domains; function unknown.'"); probe answer logged at `results/m7/recall_probe_90.tsv`; matches network top term: **no**. The probe agent recalled the domain architecture but no function, so the prediction is not a restatement of background knowledge.
- Calibrated probability p_cal: **0.0757** [95% CI **0.030–0.127**, cluster bootstrap, 2,000 refits]; calibration family: **other**; covariates inside H's 5th–95th percentile: **yes** (support category `in_support`).
- Tier: **none (p_cal fill)**; rank in primary top 40: **12**. Top-40-only labels: **not demoted** (lineage leave-out retained; DEMETER2 not measured; TP53 p 0.968).

**What p_cal means here (exact).** The calibration model was fitted on the temporal hold-out H (820 genes; primary H = 809), where t0 = GO 2018-07-02 and the outcome is "the top reportable V2 term is among the terms the gene gained by D1-evidence annotation between t0 and the current release" (`results/holdout_eval/SUMMARY.md`). On H the observed rate was **0.030** (95% CI 0.018–0.043) against 0.000 prior-only and 0.005 for the matched-gene null; out-of-fold calibration slope 0.819 (Wald 0.512–1.127), intercept −0.006 (Wald −0.437–+0.426), Brier 0.0294, c-statistic 0.855; the poor-calibration rule was not met. So p_cal = 0.0757 means: *in a world like H, about 8 such predictions in 100 would later be confirmed by curators as a direct-evidence annotation to that term over roughly an 8-year horizon.* It covers neither the relationship type nor the direction (negative vs positive regulation) nor any partner-level claim. The M6 caveat applies: no U gene could exceed p_cal 0.141 under the frozen covariates (`results/ledger/M6_SUMMARY.md`).

## 2. The protein

- Domains (UniProt, PROSITE-ProRule): **PH 95–199**, **MyTH4 237–399**, **FERM 404–754**; Pfam PF00373 (FERM M), PF00784 (MyTH4), PF21989; InterPro IPR051724, IPR019749, IPR014352, IPR035963, IPR019748, IPR000299, IPR000857, IPR038185, IPR011993, IPR001849. Length 793 aa. **No** transmembrane keyword and **not** multi-pass; a **signal-peptide keyword is present** (UniProt keyword "Signal") — an unusual combination with a cytosolic PH–MyTH4–FERM architecture, and a point worth checking experimentally rather than assuming. UniProt Function [CC], Subcellular location [CC] and Sequence similarities are empty; protein existence: evidence at protein level; annotation score 3.0; keywords also include Methylation and Phosphoprotein.
- AlphaFold (AFDB v6, Q7Z736): mean pLDDT **74.2**, 69% of residues > 70 † — a well-predicted multi-domain fold with disordered linkers, unlike the CCDC71L case.
- Class H (homology) evidence: **no IBA/ISO annotation of g to the predicted term**. The PH/MyTH4/FERM architecture is itself ancient — the *C. elegans* protein MAX-1 is described as "the PH/MyTH4/FERM myosin-like protein" and acts with the UNC-5 netrin receptor [A-P9] — but no orthology assignment between MAX-1 and PLEKHH3 was verified here, and none is claimed. The human family paralogues PLEKHH1 and PLEKHH2 are present in the DepMap matrix but are **not** in the project's Ensembl paralogue list for PLEKHH3 (`data/derived/paralogues_by_matrix_index.npz`: 0 paralogues †), so they were never excluded — they simply do not co-vary (§8).
- Source keys: A-P9 (Appendix A); domain/feature values from `reports/data/PLEKHH3/bundle.md` §8; pLDDT † recomputed.

## 3. Dependency profile

- Mean / SD of Chronos effect: **+0.087 / 0.160**; median +0.078; 5th percentile −0.156; min −0.533; fraction of lines < −0.5: **0.0015 (2 of 1,361)**; status: **not common-essential — and not, on any usual reading, a dependency at all**; NaN fraction **0.0000**.
- Expression: log2(TPM+1) ≥ 1 in **99.0%** of lines (≥ 2 in 93.9%); median 3.48. Dependency-vs-expression coupling: Spearman ρ = **0.102** (n = 1,292) — below the 0.3 flag threshold. Scatter: panel (b) of `reports/data/PLEKHH3/fig_profile.png`.
- **Direction of the signal (recomputed †, central to the interpretation).** Over all 1,361 lines, Pearson r(PLEKHH3, PLEKHA1) = **0.424**, r(PLEKHH3, PTEN) = **0.400**, r(PLEKHH3, TSC1) = 0.240, r(PLEKHH3, TSC2) = 0.246, r(PLEKHH3, DDIT4) = 0.193, r(PLEKHH3, PTPN13) = 0.117. All of these genes have positive mean effects (PTEN +0.377, PLEKHA1 +0.219, DDIT4 +0.039, TSC1 +0.002, PTPN13 +0.006; TSC2 −0.118, FOXO3 −0.271). The co-dependency is therefore largely co-*advantage*: lines in which deleting a PI3K/mTOR brake speeds growth are lines in which deleting PLEKHH3 does too.
- **Specificity of the co-advantage (†, recomputed; the single strongest argument for the call).** Ranks are in g's own genome-wide correlation row (18,433 genes, pairwise complete):

| PI3K/mTOR brakes | r | rank | generic tumour suppressors / pathway accelerators | r | rank |
|---|---|---|---|---|---|
| PLEKHA1 | **0.424** | **1** | NF2 | 0.172 | 21 |
| PTEN | **0.400** | **2** | NF1 | 0.127 | 85 |
| TSC2 | 0.246 | 4 | RB1 | 0.053 | 2,433 |
| TSC1 | 0.240 | 5 | APC | 0.021 | 6,088 |
| NPRL2 (GATOR1) | 0.204 | 8 | ARID1A | 0.015 | 6,944 |
| DDIT4 | 0.193 | 9 | **TP53** | **0.014** | 7,171 |
| DEPDC5 (GATOR1) | 0.187 | 12 | SMAD4 | −0.049 | 15,481 |
| PTPN13 | 0.117 | 142 | CDKN2A | −0.051 | 15,689 |
| GRB10 | 0.117 | 145 | **PIK3CA** | **−0.186** | **18,427** |

PLEKHA1 and PTEN are g's top two correlates genome-wide; the effect is confined to brakes on PI3K/mTOR and is absent for TP53, RB1, APC, ARID1A, SMAD4 and CDKN2A; the pathway's accelerator PIK3CA runs in the opposite direction and is the 7th most *anti*-correlated gene in the whole row (as a brake should, if PLEKHH3 is one). AKT1 (−0.100) and MTOR (−0.085) are likewise negative. This disposes of the generic-proliferation-covariate reading of the signal (§8).

- Lineage enrichment (descriptive, lineages with ≥ 10 lines, lowest mean effect): Myeloid n = 45, mean +0.008, MW p 0.0004; Lymphoid n = 97, mean +0.013, p 0.0000; Uterus n = 38, mean +0.018, p 0.0052. These are the *least positive* lineages, not negative ones.
- **Where the co-dependency actually lives (†, within-lineage, n ≥ 60) — this drives the Part II line choice:**

| lineage | n | r(PLEKHH3, PTEN) | r(PLEKHH3, PLEKHA1) |
|---|---|---|---|
| Skin | 75 | 0.550 | 0.510 |
| CNS/Brain | 133 | 0.518 | 0.455 |
| Ovary/Fallopian Tube | 62 | 0.465 | 0.409 |
| Lung | 126 | 0.458 | 0.367 |
| Breast | 67 | 0.451 | 0.627 |
| Pancreas | 71 | 0.446 | 0.136 |
| Esophagus/Stomach | 96 | 0.444 | 0.145 |
| Head and Neck | 77 | 0.379 | 0.437 |
| Bowel | 85 | 0.261 | 0.022 |
| **Lymphoid** | **97** | **−0.037** | **+0.020** |

- **Lineage robustness (†, influence jackknife — more informative than the pre-registered check).** Removing each lineage with n ≥ 20 in turn changes r(PLEKHH3, PTEN) by at most **+0.036 / −0.024** (largest: removing Lymphoid, +0.036; Bone, −0.024) and r(PLEKHH3, PLEKHA1) by at most **+0.006 / −0.028** (Bone). Lineage-demeaning every profile leaves r(PTEN) = **0.380** and r(PLEKHA1) = **0.392**. The call is far more lineage-robust than the single pre-registered removal demonstrates (§5).
- Split-half assessability: **R(g) = 0.264**; null mean 0.003, max 0.120 over 200 matched genes; empirical p = **0.0050**; RBO R = 0.560, p 0.0050 → **assessable: yes**. The neighbourhood is highly reproducible (RBO 0.560 is the stronger of the two genes reported in this pair).
- Figure 1 (profile panel): `reports/data/PLEKHH3/fig_profile.png` — (a) PLEKHH3 effect vs PLEKHA1 effect across lines, five most dependent lineages coloured; (b) effect vs own expression; chosen lines circled (D1, D2), control squared (C).

## 4. Neighbourhood

Top-10 partners (zavg_BEF; GLS rank = rank in g's GLS row after §3.1 exclusions; in_term = annotated to GO:0051896):

| partner | zavg_BEF | z_B/z_E/z_F | GLS rank | in_term | partner mean eff | frac < −0.5 | CE | band | same chr | paralogue | hub (in-degree) | hu.MAP-train | partner function (top GO annotations, ledger) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLEKHA1 (TAPP1) | 24.40 | 38.3/19.6/15.2 | **1** | **yes** | 0.22 | 0.000 | no | 10q26.13 | no | no | 65 | no / pair no | ruffle organization; phosphatidylinositol-3,4-bisphosphate binding |
| PTEN | 19.61 | 31.3/16.9/10.7 | **2** | **yes** | 0.38 | 0.015 | no | 10q23.31 | no | no | **70 HUB** | no / pair no | meiotic spindle organization; spindle assembly in female meiosis |
| PTPN13 (PTPL1) | 12.35 | 19.0/14.0/4.1 | 9 | **yes** | 0.01 | 0.001 | no | 4q21.3 | no | other partner | 39 | no / pair no | PI3K regulatory subunit binding; phosphatidylinositol-3,4,5-trisphosphate binding |
| TSC1 | 11.14 | 19.0/10.9/3.5 | 285 | no | 0.00 | 0.099 | no | 9q34.13 | no | no | 52 | no / pair no | ATPase inhibitor activity; negative regulation of ATP-dependent activity |
| TSC2 | 10.77 | 17.8/10.8/3.7 | 48 | no | −0.12 | 0.184 | no | 16p13.3 | no | no | 55 | no / pair no | Hsp90 protein binding; negative regulation of TORC1 signaling |
| KCTD5 | 10.51 | 20.3/8.8/2.5 | 206 | no | −0.08 | 0.069 | no | 16p13.3 | no | other partner | 33 | no / pair no | — |
| DDIT4 (REDD1) | 9.12 | 15.4/9.8/2.2 | 3519 | no | 0.04 | 0.007 | no | 10q22.1 | no | no | 50 | no / pair no | negative regulation of TOR signaling; response to hypoxia |
| MGAT4B | 7.84 | 9.1/11.0/3.4 | 101 | no | −0.01 | 0.002 | no | 5q35.3 | no | no | 23 | no / pair no | N-glycan processing |
| FOXO3 | 7.77 | 13.6/8.0/1.7 | 3418 | no | −0.27 | 0.104 | no | 6q21 | no | no | 65 | **yes** / pair no | mitochondrial transcription; positive regulation of neuron apoptotic process |
| ZNF608 | 7.55 | 14.4/7.9/0.3 | 8152 | no | −0.03 | 0.005 | no | 5q23.2 | no | no | 35 | no / pair no | — (itself a U gene) |

The **three supporting partners** for the called term are exactly **PLEKHA1, PTEN, PTPN13** (`results/ledger/u_flag_partners.tsv`). Seven of the top ten are negative regulators of PI3K/AKT/mTOR output (PLEKHA1, PTEN, PTPN13, TSC1, TSC2, DDIT4, and FOXO3 as the pathway's transcriptional output).

**The coherence extends past the top ten, and that matters more than the top-ten count** (†, from `data/derived/neighbours/full_top100.npz` row 11610): at K = 25, N(g) also contains **AKT1S1/PRAS40 (rank 11, zavg 7.13)** and **GRB10 (rank 19, zavg 5.51)** — two further direct brakes/substrates of the AKT–mTORC1 axis — together with PTPN12 (13), ABRAXAS2 (15) and **PTGES3/p23 (rank 21, zavg 5.36)**. AKT1S1 is literally the protein whose phosphorylation (pPRAS40-T246) the Part II readout proposes to measure, so its presence in N(g) is a pre-registration of that readout rather than a post-hoc choice. Adding the GATOR1 subunits NPRL2 (raw r 0.204, rank 8) and DEPDC5 (0.187, rank 12) from §3, the neighbourhood is pathway-coherent on nine or ten independent genes, not three — which is the main reason to take it seriously despite the orthogonal null results. (Honest counterweight: AKT1S1's *raw* correlation is modest, r = 0.056, rank 2,184 †; GRB10's is 0.117, rank 145.)

- Figure 2 (neighbourhood network): `reports/data/PLEKHH3/fig_network.png` — g, its top-10 partners and the 45 edges with zavg_BEF ≥ 3 among the 11 nodes; only **3** of those edges have physical support in an admitted P source (PLEKHA1–PTPN13, TSC1–TSC2, TSC2–DDIT4). This is a *pathway* neighbourhood, not a complex: unlike the Polycomb case, the partners themselves are mostly not in physical contact. That is consistent with relationship type d and inconsistent with type a.

Top 3 terms (R1; p_emp from the matched-gene null †; hypergeometric p descriptive):

| rank | term | name | S | n_sup | size | p_hyper | p_emp † | LOPO rank kept † |
|---|---|---|---|---|---|---|---|---|
| 1 | GO:0051896 | regulation of phosphatidylinositol 3-kinase/protein kinase B signal transduction | 56.363 | 3 | 172 | 0.0030 | 0.0020 | **0/3** |
| 2 | GO:0006661 | phosphatidylinositol biosynthetic process | 44.012 | 2 | 49 | 0.0031 | 0.0020 | 0/2 |
| 3 | GO:0008654 | phospholipid biosynthetic process | 44.012 | 2 | 185 | 0.0393 | 0.0040 | 0/2 |

- Second-ranked term: **GO:0006661 phosphatidylinositol biosynthetic process** (family ER_Golgi_secretory_lipid); GO:0030165 PDZ domain binding and GO:0045017 glycerolipid biosynthetic process complete the top 5. GO:0051896 is also the **"most specific term in the top 5"** — but that label carries DESIGN §3.1's technical meaning (ancestors of a ranked descendant are dropped), **not** "smallest": GO:0051896 has 172 members while GO:0030165 in the same top 5 has 48. The whole top 5 is a phosphoinositide theme; GO:0030165 "PDZ domain binding" is a notable fourth, given that PTPN13's PDZ1 domain is the documented docking site for TAPP1 [A-P2].
- **Leave-one-partner-out: 0/3** — removing any single supporting partner costs the term its R1 rank. The right diagnosis is **non-independence, not three-way fragility**: r(PTEN, PLEKHA1) = **0.453** †, so the three partners are closer to **≈ 2 effective observations**. Partial correlations show neither is a pass-through of the other — r(g, PTEN | PLEKHA1) = **0.257**, r(g, PLEKHA1 | PTEN) = **0.298** † — so the module is not a single-gene artefact, but a term that needs ≥ 2 supporting partners to be reportable at all, resting on two correlated partners plus a weak third (PTPN13, partial 0.060 †), must lose its rank under any single removal. That is arithmetic, not an independent failure mode. It remains the weakest point of the call (§5, §8).
- V1 / V1′ module label: **GO:0101031 protein folding chaperone complex** (2 supporting partners) — descriptive only, and in this case uninformative/misleading: it is driven by TSC1/TSC2 (Hsp90-related annotations), not by a real chaperone complex. p_cal does not attach to it. The blinded statement unfortunately carried this label (§7).

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | **pass** | g arm 17q; 0 of the top-10 partners on chromosome 17. The project's paralogue list is empty for PLEKHH3 †; PLEKHH1 and PLEKHH2 are in the matrix and were not excluded — and do not co-vary (r = 0.049 and −0.123 †), so no family cross-talk is present. |
| Bidirectional-promoter / overlapping / readthrough partners | **pass** | 0 of 3 supporting partners flagged. |
| Copy-number co-amplification | **pass** | 0 of 3 flagged; PLEKHA1 r = −0.03, PTEN r = −0.00, PTPN13 r = 0.02. |
| Hub-driven call (> 50% of S from top-1% in-degree) | **pass (but narrowly)** | hub share **0.35**; 1 hub partner (PTEN, in-degree 70). Below the 0.5 threshold, but one third of the evidence rests on the most heavily connected tumour-suppressor node in the graph — and `bundle.md` records "flagged: PTEN" explicitly. The §4.3 built-in exclusion fires when ≥ half of the supporting partners carry a flag: with **1 of 3 flagged, this prediction is one flag short of automatic exclusion from Tier A.** |
| **Lineage leave-out** | **pass — but the check as run is close to uninformative** | Removing Myeloid (45 lines; mean effect +0.008) and refitting gives the same top term GO:0051896; N(g) overlap 0.84. The removed lineage is defined (DEVIATIONS 2026-10-29) as the one with g's *lowest mean effect*; for a gene centred at +0.087 that selects the least growth-advantaged lineage, which has no particular relationship to where the *correlation* lives. The informative test is the influence jackknife in §3: max |Δr| 0.036 (PTEN) and 0.028 (PLEKHA1) over all lineages with n ≥ 20, and lineage-demeaned r = 0.380 / 0.392. Read the pass from the jackknife, not from the pre-registered removal. |
| **K = 10 / 50** | **pass / pass** | Both give GO:0051896 †; the GLS network (K = 25) also gives GO:0051896 †. The term label is stable under every refit tried — in sharp contrast to the leave-one-partner-out result. |
| Dependency vs own expression; TF / lineage-marker enrichment | **pass** | ρ = 0.102 (n = 1,292); TFs in N(g) = 1, OR 0.51, p 0.8592, q 1.0000. |
| TP53 / p53-axis correlation | **pass** | 902 mutant vs 459 WT; p 0.9683, q 0.9683; median difference +0.002. |
| DEMETER2 replication | **not measured** | 0 supporting partners present in DEMETER2 — no flag, and no replication either. |
| Shared-sgRNA and per-guide check | not possible (guide maps / guide-level data not available) | recorded |

**Honest reading.** PLEKHH3 passes every pre-registered top-40 check — it is one of the few genes in the primary top 40 with no demotion label (`results/ledger/M6_SUMMARY.md`: 221 of 269 evaluated pool genes were demoted). The fragility is elsewhere and is not captured by any of the boxes above: the term rests on ≈ 2 effective partners (r(PTEN, PLEKHA1) = 0.453), one of the three is a hub and the prediction is one flag short of §4.3 exclusion, and the underlying dependency amplitude is tiny. **Robustness to *line* resampling (lineage leave-out, K) is not robustness to *partner* resampling, and only the former is a pre-registered check** — and even the line-resampling check is run on the wrong lineage, so the real line-robustness evidence is the jackknife in §3, which is post hoc.

## 6. Orthogonal evidence matrix (four states: not measured / no support / supports / contradicts)

Class p = Simes within class; Holm across the 4 measured classes at α = 0.05. **No class supports the call**; there is no contradiction.

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | P_group (BioPlex 3.0 / STRING-exp / BioGRID-LTP / OpenCell); HCM SAINT: g not measured | **no support** | g has 0 edges to any of the 10 co-essential partners in any admitted P source. g's own edges: BioPlex3 degree 46 (CX3CL1\*, RET\*, plus ACVR2B, AMHR2, EFNB1/2, FLRT1, CXCR4, IL4R, PTGER3, RELT, SKAP1, several ion channels…); BioGRID-LTP degree 2 (PRNP, SOX2); STRING-exp degree 6 (CCNF, CDC123, EFNB2, SKAP1, SOX2, TGFBR2). 2 of 172 term members are edges | 0.1578 → **0.473 Holm** | family "other" → any class is diagnostic; diagnostic class measured = True, supports = False |
| A co-abundance | CCLE proteomics (ProteomeHD: g not measured) | **no support** | mean member row percentile 0.454 vs null 0.475 — below null. Best partner pairs: PTPN13 r 0.15 (89th percentile), PLEKHA1 0.14 (87th), KCTD5 0.12 (83rd); PTEN −0.04 (23rd) | 0.7992 → 0.799 Holm | yes (any) |
| L localisation | HPA v25.1 (admitted); OpenCell / Human Cell Map / MitoCarta for contradiction only | **no support** | fraction of members sharing a compartment with g 0.124 vs null 0.101. HPA (Approved): **Golgi apparatus only**. OpenCell: not tagged. Human Cell Map: neither prey nor bait. MitoCarta: assessed, not listed. Term compartments: none assigned; g **not** multi-localised | 0.2178 → 0.473 Holm | yes (any) |
| G perturbation phenotype | Perturb-seq K562 genome-wide (K562-essential, RPE1-essential: g not measured) | **no support** | mean member percentile 0.555 vs null 0.497 — the nearest miss of the four. **PTEN is the single highest-scoring gene in g's entire Perturb-seq row (r 0.23, 100th percentile)** †; TSC1 0.08 (96th), DDIT4 0.04 (89th), PLEKHA1 0.04 (87th); MGAT4B −0.07 (5th) | **0.0360** raw → **0.144 Holm** | yes (any) |
| S structure | Burke 2023 AF2 | **not measured** | g not modelled | — | yes (any) |
| H homology | orthologue IBA/ISO | reported only | no IBA/ISO annotation of g to the term | reported only | — |

Reported but not counted (DESIGN §5.1): **hu.MAP 3.0** — PLEKHH3 is a member of **8** hu.MAP3.0 complexes †, all of them receptor/membrane clusters (e.g. huMAP3_01062.1 = PTPRD, TGFBR2, PLEKHH3, ComplexConfidence field 1 — the direction of that scale is not asserted here; huMAP3_09249.1 = BMPR1A, ACVR2B, PLEKHH3; huMAP3_11149.1, 32 subunits, is a death-receptor/TGF-β-receptor cluster) †; non-independent all-PPI degree 56, of which 2 are term members (CX3CL1, FGFR1). **hu.MAP 3.0 places PLEKHH3 with receptors, not with PTEN/PLEKHA1/PTPN13 — it does not support the specific PI(3,4)P₂-arm hypothesis.** **Predictomes / Schmid 2025** — PLEKHH3 appears in 134 scored pairs †. Two rankings, kept distinct (an earlier draft reported the KIRC-ranked set as if it were the SPOC-ranked set): by **KIRC** the top pairs are TGFBR2 0.696, SKAP1 0.634, MAPK4 0.618, EFNB2 0.618; by **SPOC** — the classifier that matters — they are **GPRC5B 0.617, RFXANK 0.569, TMEM9B 0.557**, then MAPK4 0.556, KCNE3 0.551, SOX2 0.532, TMED7 0.515, **PTGES3 0.510**, UBXN6 0.510 †. **RFXANK is also a BioPlex interactor of PLEKHH3** (HCT116 network, pInt 0.798 †), so that pair is reproducible across two sources and is the single most interesting structural hit for this gene — and it has nothing to do with the called module. **PTGES3/p23 (SPOC 0.510) is the one Predictomes pair linking g to its own co-essentiality neighbourhood** (N(g) rank 21, zavg 5.36 †). There is **no scored pair with PTEN, PLEKHA1 or PTPN13** †. **DEMETER2** — not measured. Absence of an interaction is never a contradiction.

**Where the orthogonal data actually point.** Every physical and structural source that has data on PLEKHH3 puts it near **membrane receptors** (PTPRD, TGFBR2, ACVR2A/B, BMPR1A, ERBB2, FGFR1, EPHA2, AXL, JAK1, IFNGR1, RET, EFNB1/2); HPA puts it in the Golgi. None of this contradicts a role in regulating PI3K/AKT — receptor-proximal membrane adaptors are exactly where that regulation happens — but none of it supports the specific PLEKHA1/PTEN/PTPN13 arm either. The one pair-level hint that does is PTEN as the top Perturb-seq correlate, and the G class fails Holm (0.036 → 0.144).

## 7. Literature (blinded step, then synthesis)

**Blinded summary of agent L's evidence items** (`results/m7/L/HGNC_26105.md`; 6 items):

| # | claim | level | DepMap-derived |
|---|---|---|---|
| 1 | UniProt carries no function, location or interaction annotation | mention | no |
| 2 | PLEKHH3 protein level changes with severity in obstructive sleep apnoea (grouped with endothelial tight-junction genes; expression association only) | mention | no |
| 3 | A PLEKHH3::BRAF kinase fusion is reported in a mesenchymal neoplasm | mention | no |
| 4 | A truncating variant segregates in a familial prostate-cancer pedigree (candidate; no functional test) | mention | no |
| 5 | Named as a possible regulator in a BET/SYK-inhibition transcriptomic response in B-cell lymphoma cells | mention | no |
| 6 | Downregulated by a plant extract in an ovarian cancer line (RT-qPCR) | mention | no |

L's own summary: no focused functional study exists; the record is transcriptomic/omics mentions, a fusion case report and a segregating truncating variant. **Every item is level "mention"; there is not one functional study of PLEKHH3.** Novelty class **N3**.

**Blinded verdicts** (`results/m7/judge/`; packet J059; statements carried the V2 term + V1′ label only):

- Real statement (slot D, "functions in regulation of phosphatidylinositol 3-kinase/protein kinase B signal transduction; module context: protein folding chaperone complex"): **0 (unaddressed)** from both judges. J1: "No evidence row addresses this process/activity." J2: "Not addressed by evidence (no PI3K/AKT evidence)."
- Decoys (slots A, B, C — regulation of actin cytoskeleton organization; cytokine receptor binding; cell junction organization): **0, 0, 0** from both judges. (Note that decoy A and C are *closer* to the sleep-apnoea tight-junction mention than the real statement is, and the judges still scored them 0 — the blinding worked as intended.)
- Judges J1, J2; adjudicator not required. Run-level κ = 0.975 over 360 statements; d (real − mean decoy) for this gene = **0.000**.

The blinded step is therefore **uninformative by construction** for an N3 gene: there is no literature for judges to score against. In the primary top 40 the real-vs-decoy signal (18/40 vs 3/120, sign-flip p = 0.0002174) came from N1 genes (16/31 supported); both N3 genes scored 0.

**Unblinded synthesis** (every sentence carries an Appendix-A key):

The three supporting partners are a documented module, independently of co-essentiality. TAPP1 (PLEKHA1) is constitutively associated with PTPL1/PTPN13 [A-P1], binding principally through PTPL1's first PDZ domain [A-P2] — which is why "PDZ domain binding" is the fourth-ranked term for PLEKHH3 (§4). Genetic knock-in of PI(3,4)P₂-binding-dead TAPP1/TAPP2 raises Akt activity, showing that these adaptors "function as negative regulators of the insulin and PI3K signalling pathways" [A-P3]. PTEN completes the arm as the enzyme: beyond its canonical PIP₃ activity, "PTEN also functions as a PI(3,4)P₂ 3-phosphatase, both in vitro and in vivo" [A-P4], and PI(3,4)P₂ itself is predominantly a class I PI3K product that is also hydrolysed by PTEN [A-P5, A-P6]. So PLEKHH3's three term-annotated partners are not three arbitrary members of a 172-gene GO term: they are the adaptor, the scaffolded phosphatase and the lipid phosphatase of one PI(3,4)P₂-centred negative-feedback arm, and the co-dependency places PLEKHH3 with them in the direction of *restraining* the pathway (§3 †).

The gene's own domain architecture is compatible with that placement without proving it: PLEKHH3 has a PH domain (95–199) that could, like TAPP1's, read a 3-phosphoinositide, followed by MyTH4 and FERM domains that in the one studied human family member couple membrane signalling to kinase activation — PLEKHH2 binds β-arrestin1 through its FERM domain, displacing FAK and thereby activating FAK autophosphorylation and the PI3K/AKT pathway [A-P7, A-P8]. Note the direction: PLEKHH2 is reported as a *positive* regulator in lung cancer cells [A-P8], whereas the co-essentiality direction for PLEKHH3 is negative — the family architecture supports "acts on PI3K/AKT", not the sign. In the invertebrate, the PH/MyTH4/FERM protein MAX-1 acts with the UNC-5 netrin receptor [A-P9], i.e. this architecture is used for receptor-proximal regulation, consistent with PLEKHH3's receptor-rich physical neighbourhood (§6).

Against this, the published record on PLEKHH3 itself is thin and non-functional: a protein-level association with obstructive sleep apnoea severity [A-P10]; a PLEKHH3::BRAF fusion in a mesenchymal neoplasm [A-P11]; a truncating variant segregating in a prostate-cancer family [A-P12]; and a bioinformatic nomination as a possible regulator in BET/SYK-inhibited lymphoma cells [A-P13]. **A function for PLEKHH3 in PI3K/AKT regulation, or any other pathway, was not found in the literature as of the 2026-10 searches reported here.** Two of those items are weakly consistent with a growth-signalling role — a BRAF fusion partner is, at minimum, expressed and 5'-donor-competent in a MAPK-driven tumour [A-P11], and a truncating germline variant segregating with cancer is what one would expect of a lost brake [A-P12] — but neither is evidence of function and neither was counted.

**Closest prior publication and what co-essentiality adds.** There is no prior publication on PLEKHH3's function; the closest relevant work is on its partners [A-P1, A-P2, A-P3, A-P4] and on the family paralogue PLEKHH2 [A-P7, A-P8]. Co-essentiality adds the only genome-scale, orthogonal argument that exists for placing PLEKHH3 in a pathway at all, and it adds a *direction* (brake, not accelerator) and a *named arm* (PI(3,4)P₂/TAPP1–PTPN13–PTEN) that make the hypothesis falsifiable in a two-month experiment.

**Prior prediction lists containing this gene.** Wainberg 2021 [A-P14]: list not held locally, only the abstract retrievable — membership *not verifiable*. hu.MAP 3.0 [A-P15]: PLEKHH3 is placed, but with receptors, not with the predicted arm (§6) — partial agreement on "membrane/receptor-proximal", disagreement on the specific module; also partly non-independent (tool tuned on hu.MAP 3.0 train pairs). Replogle 2022 [A-P16]: PLEKHH3 is measured in the K562 genome-wide screen (§6) but "PLEKHH3" does not occur in the retrieved full text †, so it is not among that paper's function assignments. Predictomes [A-P17]: 134 scored pairs, none with PTEN/PLEKHA1/PTPN13 †.

**Post-freeze (after 2026-10-29) papers confirming the prediction:** none found.

## 8. Alternative explanations

For each §5 artefact, the evidence against it:

- *Paralogue / family cross-talk.* PLEKHH1 r = 0.049 and PLEKHH2 r = −0.123 with PLEKHH3 † — no family-wide co-variation, so the signal is not multi-targeting guides or family redundancy.
- *Locus / copy-number.* 0 of 3 supporting partners flagged; |r| ≤ 0.03. PTEN and PLEKHA1 are both on chromosome 10 but on different arms from each other's relevance here and none on 17q.
- *Hub-driven call.* Hub share 0.35 — below threshold but non-trivial; the call does not survive removal of PTEN (LOPO 0/3), so PTEN's hub status is a genuine concern rather than a formality.
- *Lineage-driven.* Lineage leave-out passes; the three most "dependent" lineages are merely the least growth-advantaged.
- *TP53 axis.* p 0.9683 — no relation.
- *Curation lag.* Not in the audit sample; recall probe negative; agent L found no functional literature. Rediscovery is very unlikely for an N3 gene.

**Strongest competing biological hypotheses.**

1. **Regulatory co-dependency on PI3K-pathway state (type e in substance, though not by the §4.3 rule).** Every strong partner is a brake on PI3K/AKT/mTOR. A line's benefit from losing any one brake depends on how much that pathway constrains its growth — a *shared covariate*, which can generate correlated effects with no shared molecular function. **The generic version is excluded** (§3 †): if the signal were "deleting any growth brake helps in permissive lines", TP53 (0.014), RB1 (0.053), APC (0.021), ARID1A (0.015), SMAD4 (−0.049) and CDKN2A (−0.051) would track PLEKHH3 too, and they do not, while PIK3CA runs the other way (−0.186). **The PTEN-genotype version is excluded:** the correlation holds within PTEN-wild-type lines (r = 0.390, n = 1,215) and within PTEN-damaging-mutant lines (r = 0.354, n = 146) †, and PLEKHH3's own expression barely predicts its effect (ρ = 0.102). **What survives:** a covariate specific to how much the *PI3K/mTOR* axis constrains a given line, independent of PTEN genotype, remains fully consistent with everything above. That is the leading alternative, and Part II §6 is designed around it: a shared-covariate explanation predicts that removing PLEKHH3 changes *growth* in pathway-constrained lines without changing *AKT pathway output* at matched depletion.
2. **Downstream effector rather than regulator (type c/d boundary).** PLEKHH3's PH domain might read PI(3,4)P₂ as an *output* of the arm, making it a client of the module rather than a regulator of it. Both readings sit inside GO:0051896 but differ in every mechanistic prediction. **Separated by:** epistasis and the direction of the pAKT change (Part II Tier 2).
3. **Receptor-proximal adaptor with a different primary pathway.** All independent physical data put PLEKHH3 among receptors (§6), and HPA puts it in the Golgi; the primary function might be receptor trafficking or stability, with PI3K/AKT effects secondary. **Separated by:** surface-receptor levels and trafficking assays run alongside the signalling readout (Part II Tier 1 localisation arm), and by whether the pAKT phenotype survives in a single-receptor-stimulus system.
4. **Low-amplitude noise.** With mean +0.087 and SD 0.160, S is built on small fluctuations. **Evidence against:** split-half reproducibility R = 0.264 with empirical p = 0.0050 and RBO 0.560 — the neighbourhood is reproducible across independent halves of the cell-line panel, which noise would not be.
5. **Subunit (type a) or assembly factor (type b).** No P/A/S class supports the call; only 3 of 45 edges among the top-10 partner network have physical support, and none involves g. Neither type is assigned.
6. **Wrong topology — the mechanism, not just the refinement, could be impossible.** UniProt Q7Z736 carries not merely a "Signal" keyword but an actual sequence feature **`SIGNAL 1..18`** with `CHAIN 19..793` † — though the evidence code is **ECO:0000255** (automatic assertion from a sequence model), i.e. a *prediction*, not an experiment. If that annotation is right, the PH (95–199), MyTH4 and FERM domains are extracytosolic and **cannot** read cytosolic PI(3,4)P₂, which would invalidate the proposed mechanism rather than merely the refinement — and HPA's Golgi-only call is consistent with a secretory-pathway protein. Every signalling arm of Part II presupposes cytosolic topology. **Separated by:** a protease-protection / N-glycosylation-scanning topology test added as step 0 of Part II, before any lipid-binding or membrane-recruitment work is funded.

## 9. Falsifying observations (written before §6 and §7 were read)

1. **Signalling.** If acute depletion of PLEKHH3 (degron or CRISPRi, time-matched to PTEN/PLEKHA1 depletion) changes neither the amplitude nor the kinetics of AKT pathway output — pAKT-S473, pAKT-T308, pPRAS40-T246, pS6-S235/236 after serum/insulin/EGF stimulation — beyond what a matched-essentiality control gene from an unrelated module produces at the same growth effect, in both dependent lines, the "regulation of PI3K/AKT" call is refuted.
2. **Lipid binding and membrane recruitment.** If the recombinant PLEKHH3 PH domain binds neither PI(3,4)P₂ nor PI(3,4,5)P₃ above background in a protein–lipid overlay/liposome assay, **and** endogenously tagged PLEKHH3 never relocates to the plasma membrane after growth-factor stimulation, the membrane-adaptor refinement is refuted (the broad term could still hold through an indirect route).
3. **Pathway placement.** If PLEKHH3 loss confers the same growth advantage in PTEN-null and isogenic PTEN-restored cells, and shows no interaction with a class I PI3K or AKT inhibitor dose-response, the placement in this pathway is refuted.
4. **Direction.** If PLEKHH3 depletion *decreases* AKT output (positive regulator, as reported for PLEKHH2), the term may survive but the hypothesis as stated — a brake acting with PTEN/TAPP1 — is refuted and must be rewritten.

## 10. Experiments

See **Part II** below (Template B; DESIGN §6.5 names `reports/PLEKHH3_experiments.md`, see the note at the top of this file).

## 11. Novelty and external benchmarks

- **Wainberg 2021** [A-P14]: agreement not verifiable (list not held locally).
- **hu.MAP 3.0** [A-P15]: PLEKHH3 is placed in 8 complexes, all receptor/membrane clusters, **not** with PTEN/PLEKHA1/PTPN13 † — this catalogue does not agree with the specific prediction.
- **Replogle 2022** [A-P16]: measured in the K562 genome-wide screen, not assigned a function; its pseudo-bulk profile's top correlate is PTEN †.
- **Predictomes / Schmid 2025** [A-P17, A-P18]: 134 scored pairs, none with the three supporting partners †; its best SPOC hits (GPRC5B 0.617, RFXANK 0.569, TMEM9B 0.557) are receptor/membrane proteins, and RFXANK is corroborated by BioPlex (pInt 0.798) †. Note that SPOC is itself trained partly on DepMap co-dependency and BioGRID data [A-P20, A-P21], so it is not independent of the signal under test.

**What is new here.** For an N3 gene with zero focused publications, everything in the hypothesis is new: a pathway assignment, a direction (negative regulation), a named arm (PI(3,4)P₂/TAPP1–PTPN13–PTEN) and a reproducible partner set. The sharpest new observation, added after red-team review, is the **specificity** of the co-advantage: PLEKHA1 and PTEN are PLEKHH3's #1 and #2 correlates among 18,433 genes, the effect is confined to PI3K/mTOR brakes, it is absent for TP53/RB1/APC/ARID1A/SMAD4/CDKN2A, and PIK3CA runs the other way at rank 18,427 †. The hypothesis goes beyond all four external catalogues, and in the case of hu.MAP 3.0 it disagrees with the one placement that exists. That cuts both ways: novelty here means no independent source corroborates the call, and the orthogonal matrix is four nulls (§6). The honest summary is a well-formed, falsifiable hypothesis at p_cal 0.0757, not a finding.

---

# Part II — Template B: experiment plan

Rules (DESIGN §6.5): one decisive, falsifiable experiment; expected readouts for both "right" and "wrong"; cell lines chosen by rule; essential-gene confound control; DepMap screen medium as baseline; sequence-level guide off-target check.

## 1. Context

- Gene: **PLEKHH3** | hypothesis: PLEKHH3 functions in / supports regulation of PI3K/AKT signal transduction (GO:0051896) as a negative regulator acting with the PI(3,4)P₂ arm (PLEKHA1/TAPP1 – PTPN13 – PTEN) | relationship type: **d** | novelty class: **N3**
- LLM-recall-probe flag: **not known** | calibrated probability: **p_cal 0.0757** (family "other") | tier: **none (p_cal fill)**; primary top-40 rank 12; no demotion label
- Strongest alternative explanation: the co-dependency reflects each line's PI3K-pathway *state* — a shared covariate across genes that brake the pathway — rather than a shared molecular function.
- **Decisive experiment (one sentence):** in **LN-428 and OVCAR-5** — two named PTEN-wild-type, PI3K-competent, adherent lines from lineages in which the predicted co-dependency is actually present (within-lineage r(PLEKHH3, PTEN) 0.518 and 0.465) — deplete PLEKHH3 acutely (dTAG degron) and measure growth-factor-stimulated AKT pathway output (pAKT-S473/T308, pPRAS40, pS6) and PI(3,4)P₂ membrane dynamics against (i) a guide-resistant WT cDNA rescue, (ii) a PH-domain lipid-binding mutant, (iii) PTEN and PLEKHA1 depletion as positive controls for the arm, and (iv) a **knockdown-depth-matched** control gene from an unrelated module — the question being whether PLEKHH3 loss moves pathway output at matched depletion. **Step 0, gating everything: a topology test of the predicted `SIGNAL 1..18` (§8 alternative 6).**
- Falsifying observation (copied from Template A §9, item 1): no change in AKT pathway amplitude or kinetics beyond the matched-essentiality control, in both lines, refutes the call.

**Why the dropout assay is not the decisive experiment here (stated up front).** PLEKHH3's effect distribution is centred at +0.087 with only 2 of 1,361 lines below −0.5. The bundle's line-selection rule had to be **relaxed** (the partner criterion was dropped) because no line satisfied g ≤ −0.5 together with partner ≤ −0.3. A competitive-growth dropout experiment is therefore underpowered and, worse, ambiguous in sign — in most lines the prediction is a mild growth *advantage*. The decisive test must be the signalling readout; the growth assays below are controls and context, not the endpoint.

## 2. Cell lines (selection rule)

Rule applied (bundle §10; rank-1 partner PLEKHA1; **relaxed: partner criterion dropped**, g ≤ −0.5 only). Funnel: 1,361 lines → 2 with g ≤ −0.5 → **0** after adding the partner criterion → 0 after expression → 0 after the amplification filter; hence the relaxation, which is recorded here as a limitation, not a choice of convenience.

**Two "dependent" lines (the only two in the panel with g ≤ −0.5):**

| ModelID | name | lineage / disease | g effect | PLEKHA1 effect | g expr (log2 TPM+1) | g CN | TP53 | ScreenNNMD / ROCAUC | medium (DepMap screen medium = baseline) |
|---|---|---|---|---|---|---|---|---|---|
| ACH-000995 | **JURKAT** | Lymphoid / T-lymphoblastic leukaemia-lymphoma | −0.51 | **+0.14** | 2.70 | 1.04 | mutant | −4.19 / 0.91 | RPMI + 10% FBS (MF-001-001) |
| ACH-003013 | **PANFR0034** | Pancreas / pancreatic adenocarcinoma | −0.53 | **+0.20** | 2.67 | 1.26 | mutant | −1.71 / 0.75 | OPAC:Ad+++ (1:1) (MF-031-002) |

Note the partner effects are **positive** in both lines: these lines are atypical for the predicted module, which is precisely why they cannot carry the inference alone. PANFR0034 also has a markedly worse screen quality (NNMD −1.71 vs −4.19). **PTEN status of these lines (DepMap damaging/hotspot matrices, default entries †): JURKAT carries 2 damaging PTEN mutations and 0 hotspot; PANFR0034 and the control LP-1 carry none.** JURKAT is therefore PTEN-deficient, which matters directly: the decisive readout needs at least one PTEN-competent background, so JURKAT alone cannot carry it (below).

**The rule-selected lines are the wrong backgrounds for the decisive readout, and the reason is quantitative.** Within Lymphoid — JURKAT's lineage and LP-1's — the predicted co-dependency **does not exist**: r(PLEKHH3, PTEN) = **−0.037** (n = 97) and r(PLEKHH3, PLEKHA1) = **+0.020**, against 0.45–0.55 in CNS/Brain, Skin, Ovary, Lung and Breast (§3 †). Two of the three rule-selected lines are drawn from the one lineage in which the relationship is absent, and the third (PANFR0034) has poor screen quality. JURKAT is therefore **demoted from "dependent line" to what the data say it is: a negative-lineage, PTEN-null line in which the hypothesis predicts the *smallest* signalling effect** — a useful specificity control, not a test bed.

**Named signalling backgrounds (addition to the §2 rule; the added criterion is stated and pre-registered here, not at execution time).** Selection: (i) lineage with within-lineage r(PLEKHH3, PTEN) > 0.4; (ii) PTEN with 0 damaging and 0 hotspot mutations (`OmicsSomaticMutationsMatrixDamaging/Hotspot`, default entries); (iii) PLEKHH3 expressed ≥ 2 log2(TPM+1); (iv) PLEKHH3 locus not amplified (CN < 1.5); (v) ScreenNNMD ≤ −2.5; (vi) adherent growth (for TIRF imaging); then best screen quality, one line per lineage. Applied to all 1,361 lines this yields the two below †:

| ModelID | name | lineage / disease | lineage r(g,PTEN) | g effect | PTEN effect | PLEKHA1 effect | g expr | g CN | PTEN status | NNMD / ROCAUC | growth | medium |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ACH-000455 | **LN-428** | CNS/Brain / glioblastoma, IDH-wild-type | 0.518 | +0.061 | +0.419 | +0.091 | 3.12 | 0.61 | 0 damaging / 0 hotspot | −15.37 / 0.99 | adherent | DMEM + 10% FBS (MF-002-001) |
| ACH-001151 | **OVCAR-5** | Ovary/Fallopian Tube / high-grade serous | 0.465 | +0.153 | +0.798 | +0.242 | 3.62 | 1.27 | 0 damaging / 0 hotspot | −13.04 / 0.96 | adherent | RPMI + 5% FBS (MF-001-014) |

Both have a strongly positive PTEN effect (+0.42, +0.80), i.e. the PI3K axis is intact *and* growth-constraining — the condition the readout needs. LN-428's PLEKHH3 CN of 0.61 is a shallow loss (well under the 1.5 amplification threshold) with expression 3.12, so CRISPRi is not required for CN reasons. Back-ups by the same rule, in order: NCI-H2171 (ACH-000525, Lung, NNMD −14.62 — but suspension, so imaging arms would need adaptation), YUHOIN (ACH-002847, Skin), LN-443 (ACH-000673, CNS/Brain), HCC1806 (ACH-000624, Breast — weaker, PTEN effect only +0.065).

**Retained from the rule, with their roles restated:** JURKAT (ACH-000995) and PANFR0034 (ACH-003013) are kept as the only two lines in the panel with g ≤ −0.5, for the Tier-1 growth arm and as the negative-lineage / PTEN-null specificity control; **LP-1** (ACH-000204, Lymphoid, g +0.27, expression 7.01, CN 1.02, IMDM + 10% FBS) is kept as the non-dependent high-expression control for guide toxicity and localisation — its ~17-fold higher expression than JURKAT on the log2 scale is useful for imaging, and its Lymphoid origin is now a feature of that role rather than a liability.

**Common-essential handling:** PLEKHH3 is **not** common-essential (2/1,361 lines < −0.5), so the RPE1-hTERT TP53⁻/⁻ / HEK293T degron route is **not required** by the rule. A dTAG degron is used anyway, because the decisive readout is an acute signalling measurement where chronic adaptation would confound the result.

**Baseline medium:** each line's DepMap screen medium as tabled. Serum starvation + timed stimulation (insulin, IGF-1, EGF) is a defined stimulation protocol applied on top of that baseline, declared as its own arm; no carbon-source change is used.

**Essential-gene confound control — re-derived, with a second branch, because matching on growth is degenerate in the decisive backgrounds.** In LN-428 and OVCAR-5, PLEKHH3's own effects are **+0.061 and +0.153**, i.e. neutral: **699 genes** match them within ±0.06 with a matched genome-wide mean †, so "growth effect matched within ±15%" does not identify a control there, and SLC30A5's matching does not transfer (its effects in LN-428/OVCAR-5 are **−0.138 / +0.003** †, unlike the −0.555 / −0.663 it shows in JURKAT/PANFR0034). The control is therefore split by arm:

- **Growth arm (JURKAT, PANFR0034):** matched-essentiality control **SLC30A5 (ZnT5)** — effects **−0.555 / −0.663**, genome-wide mean +0.013, SD 0.174 †, matched to PLEKHH3's −0.506 / −0.533; an unrelated metal-transport module [A-P19]. Alternatives: **C10orf90** (−0.487/−0.489, mean −0.026) or **ZNF22** (−0.559/−0.475, mean −0.037) †; avoid MAPKBP1 (MAPK-adjacent).
- **Signalling arm (LN-428, OVCAR-5), where PLEKHH3 depletion has no fitness effect:** matching is on **depletion depth, not growth** — dTAG degradation quantified by the HA/FKBP12^F36V knock-in western (target: ≥ 90% loss at 4 h, measured per experiment) and, for the CRISPRi arm, on knockdown depth by RT-qPCR (target bands 50 ± 10%, 75 ± 10%, 90 ± 5%). The paired control gene is depleted to the **same measured depth** over the same window, and is chosen as a neutral-effect, unrelated-module gene in *these* lines (SLC30A5 qualifies on effect in LN-428/OVCAR-5 and is retained for continuity across arms; its depth, not its Chronos value, is what is matched here). Any pathway readout is reported as the difference between PLEKHH3 and control at matched depth, with the growth effect of both reported alongside as a covariate rather than as the matching variable.

## 3. Reagents

- **3 sgRNAs** targeting *PLEKHH3* plus **2 non-targeting guides** and an **AAVS1 cutting control**. Per-guide DepMap effects are not available locally and no guide-library file is held in this project (`DATA.md` lists no Avana/Brunello guide map), so **guide sequences are not stated here**: they are to be taken from a published library at execution time, with three-guide concordance checked inside the experiment. Stating sequences from memory would be an unverified claim and is deliberately omitted.
- **Sequence-level off-target check of every guide** before use: genome-wide mismatch search (Cas-OFFinder / CRISPOR against GRCh38) requiring no perfect or 1-mismatch protospacer in any other gene and specifically none in *PLEKHH1*, *PLEKHH2* (family members present in the matrix and **not** excluded as paralogues by the pipeline †) or in the loci of PLEKHA1, PTEN, PTPN13, TSC1, TSC2. Tool and result recorded.
- **CRISPRi guides** (dCas9-KRAB, TSS-proximal) for the hypomorphic titration arm; PLEKHH3's locus is not amplified in either line (CN 1.04 / 1.26) so CRISPRi is not required for that reason.
- **Endogenous dTAG knock-in** (FKBP12^F36V–HA at the endogenous locus) — primary reagent for acute depletion; plus an endogenous **mNeonGreen–HaloTag** knock-in for localisation and membrane-recruitment imaging.
- **Guide-resistant cDNA** (ORFeome *PLEKHH3*, codon-wobbled at the protospacers) for rescue; plus a **PH-domain lipid-binding mutant**. The PH domain spans 95–199; the mutated residue(s) must be chosen from a structure-guided alignment of the PLEKHH3 PH domain to characterised 3-phosphoinositide-binding PH domains (the TAPP1 R211L knock-in allele is the precedent for a binding-dead PH point mutant [A-P3]) — the specific residue number for PLEKHH3 is **not asserted here**, because no alignment was performed for this report; determining it is part of step 0 of the plan, alongside the topology test.
- **Antibodies / probes:** no validated PLEKHH3 antibody is known to this project (hence endogenous tagging). pAKT-S473, pAKT-T308, total AKT, pPRAS40-T246, pS6-S235/236, pS6K-T389, pFOXO3-T32, total PTEN, PLEKHA1, PTPN13, TSC2, GM130 (Golgi, to test the HPA Approved call directly), plasma-membrane marker. **PI(3,4)P₂ biosensor:** the high-avidity tandem TAPP1-PH biosensor [A-P5]; **PIP₃ biosensor:** standard AKT-PH or BTK-PH reporter, with the caveat that over-expressed lipid biosensors can themselves buffer the lipid.

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| **0 (gating)** | **Topology test of the predicted `SIGNAL 1..18`**: protease-protection of the endogenous HA-tagged knock-in in semi-permeabilised cells, plus N-glycosylation-site scanning (engineered NxS/T reporters in the PH and FERM domains, Endo H / PNGase F shift) | days–2 wk | Domains are cytosolic (protease-sensitive, unglycosylated): the whole signalling plan is valid | Domains are lumenal/glycosylated: the proposed mechanism is impossible and the plan stops here (§8 alternative 6) | **yes** | PH/FERM epitopes degraded by proteinase K without detergent; no Endo H-sensitive shift in the engineered reporters. The UniProt feature carries evidence code ECO:0000255 (prediction, not experiment) †, so a cytosolic result is the expected outcome — but two months of lipid work are gated on it |
| 0 | AF-Multimer of PLEKHH3 with PLEKHA1, PTEN, PTPN13 (ipTM/pDockQ); plus structure-guided PH-domain alignment to select the lipid-binding mutant | days | Confident interface, most plausibly PLEKHH3-FERM/PH with PTPN13 PDZ or PLEKHA1 | No interface (expected; does not exclude type d) | **yes** | Prior expectation is **negative**: Predictomes holds no scored pair between PLEKHH3 and any of the three † and the partner network has almost no physical edges (§4). A positive result (ipTM ≥ 0.6) would be a genuine surprise and would upgrade the type question to a |
| 1 | Competitive growth (GFP/mCherry mix), 3 guides + rescue, JURKAT and PANFR0034 vs LP-1 control | 2–3 wk | Modest dropout only in the two dependent lines; rescued | No dropout, or no rescue | **yes (as control, not endpoint)** | log2 depletion ≈ 0.3–0.6 over 14–21 doublings in JURKAT/PANFR0034 (consistent with Chronos ≈ −0.5), ≈ 0 or slight enrichment in LP-1; all 3 guides concordant. A null result here does **not** refute the hypothesis (see §1) |
| 1 | **Essential-gene confound control (two branches, §2):** dTAG depletion of PLEKHH3 time-matched to PTEN and PLEKHA1 depletion, vs a control gene matched on *growth* in JURKAT/PANFR0034 and on *depletion depth* in LN-428/OVCAR-5 | 2–4 wk | Pathway readout moves beyond the control's at matched depletion | Same as the control (general sickness) | **yes** | Signalling arm (LN-428, OVCAR-5): at ≥ 90% degron loss measured per experiment and matched within ±10% between PLEKHH3 and control, ≥ 1.5-fold change in pAKT-S473/total AKT at 10–30 min post-stimulation, control within ±1.2-fold. Growth arm (JURKAT, PANFR0034): growth effect matched within ±15% against SLC30A5 (−0.555 / −0.663 †). **Growth matching is not used in the signalling backgrounds, where PLEKHH3 is neutral (+0.061 / +0.153) and 699 genes would qualify** † |
| 1 | Localisation with markers (endogenous mNG knock-in; LP-1 as the high-expression background) | 2–4 wk | Plasma-membrane and/or endomembrane pools; stimulus-dependent membrane recruitment | Exclusively Golgi and stimulus-insensitive | **yes** | ≥ 1.5-fold increase in plasma-membrane:cytosol ratio within 5 min of insulin/EGF, co-timed with the PI(3,4)P₂ biosensor; GM130 overlap quantified (HPA calls Golgi — if the protein is static and purely Golgi-resident, alternative 3 in §8 gains) |
| 1 | **Module-specific readout after KO/degradation** (see §5) | 2–4 wk | Phenocopies PTEN/PLEKHA1 depletion in direction | Normal | **yes (decisive)** | See §5 and §6 |
| 1 | Partner protein levels after PLEKHH3 depletion (and the reverse) | 2 wk | Co-destabilisation would indicate a/b | Stable (favours c/d) | **yes** | PTEN, PLEKHA1, PTPN13, TSC2 within ±20% — expected under type d |
| 2 | **AP-MS (primary)** of tagged PLEKHH3 vs a **membrane-localised, size-matched control bait** (a ~750–850 aa single-pass or membrane-anchored protein of unrelated function, same tag, same promoter — not a soluble GFP control); TurboID only as a secondary, separately-controlled arm | 1–2 mo | Arm members or a coherent receptor set enriched (SAINT) | Absent, or an unrelated module appears | **yes** | AP-MS is primary because the receptor-heavy prior from BioPlex (§6) is itself AP-MS-derived and a proximity method would not be comparable to it. Prior from existing data favours **receptors** (PTPRD, TGFBR2, ACVR2A/B, BMPR1A, EPHA2, JAK1) over PTEN/PLEKHA1/PTPN13; recovery of PLEKHA1 or PTPN13 at BFDR ≤ 0.01 would be the single most informative positive, and **RFXANK** is the one pair with both BioPlex (pInt 0.798) and SPOC (0.569) support † |
| 2 | Lipid binding: recombinant PLEKHH3 PH domain vs PI(3,4)P₂, PI(3,4,5)P₃, PI(4,5)P₂ (liposome sedimentation + SPR) | 1 mo | Selective 3-phosphoinositide binding | No binding above background | **yes** | K_d ≤ 10 µM for PI(3,4)P₂ or PIP₃ with ≥ 5-fold selectivity over PI(4,5)P₂; abolished by the structure-guided point mutant |
| 2 | Double KO / epistasis with PTEN and with PLEKHA1 | 1–2 mo | No extra pathway effect beyond the partner alone (same arm) | Additive/synergistic (parallel arms) | **yes** | Pathway-interaction score on pAKT: \|π\| < 0.15 for same-arm partners vs > 0.3 for an unrelated control gene |
| 2 | Drug-interaction grid: PLEKHH3-depleted vs control against a class I PI3K inhibitor, an AKT inhibitor and rapamycin | 1 mo | Shifted IC50 consistent with a lost brake | No shift anywhere | **contingent** | **Run only if the Tier-1 signalling readout is positive, and powered on its observed effect size.** A ≥ 2-fold IC50 shift from a gene whose mean Chronos effect is +0.087 is optimistic and this arm is unpowered as a standalone test; if the pAKT change is ≥ 1.5-fold, the expected IC50 shift is estimated from it before the grid is run, with ≥ 4 biological replicates per dose series |
| 2 | Arrayed CRISPRi Perturb-seq with PTEN, PLEKHA1, PTPN13, TSC1/2 | 2 mo | Transcriptional signatures cluster with the arm | Distinct | no (deferred; prior supplied by Replogle K562 data, where PTEN is already g's top correlate †) | — |
| 3 | PH-domain interface mutants fail to rescue; reconstitution | 6–12 mo | Lipid binding required for the pathway phenotype | Mutants rescue fully | contingent on Tier 2 | Rescue by PH mutant < 50% of WT rescue on the pAKT readout |

Type-specific rows: relationship type is **d**, for which the template specifies no extra row. The **type-e** row is retained because §8 makes "regulatory co-dependency on pathway state" the leading alternative, and the **type-c** row is retained because "client rather than regulator" is alternative 2:

| Type | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| c (alternative 2) | PI(3,4)P₂/PIP₃ supply and bypass: stimulate or clamp the lipid (SHIP2 inhibition, INPP4B knockdown, PTEN re-expression) and ask whether PLEKHH3's membrane recruitment follows the lipid and whether the pathway phenotype is bypassed | 1–2 mo | PLEKHH3 recruitment tracks PI(3,4)P₂ and the phenotype is rescued by clamping the lipid → client/effector (type c reading) | Recruitment independent of the lipid; phenotype not bypassed → regulator (type d reading) | **yes** | Membrane recruitment correlates with biosensor intensity (Pearson ≥ 0.6 across conditions) if client |
| e (leading alternative) | Pathway-state control: compare PLEKHH3 depletion in isogenic PTEN-null vs PTEN-restored cells and in PI3K-inhibited vs untreated cells, reading growth **and** pAKT separately, with JURKAT (negative lineage, PTEN-null) as the predicted-no-effect specificity line | 1–2 mo | Pathway output changes at matched depletion depth → function, not state | Growth changes track pathway constraint while pAKT is unchanged → regulatory co-dependency (type e); the module call is then not a function call | **yes** | pAKT-S473 fold-change ≥ 1.5 in PTEN-restored cells and attenuated in PTEN-null cells, with the growth effect in both explained by pathway constraint |

## 5. Module readouts

| Module | Readouts |
|---|---|
| Other (module not listed): regulation of PI3K/AKT signal transduction | **Phospho-signalling time course** after serum starvation and timed insulin/IGF-1/EGF stimulation: pAKT-S473, pAKT-T308, pPRAS40-T246, pS6-S235/236, pS6K-T389, pFOXO3-T32 (western + phospho-flow for single-cell distributions). **Lipid dynamics:** plasma-membrane PI(3,4)P₂ with the high-avidity tandem TAPP1-PH biosensor and PIP₃ with a standard PH reporter, live TIRF. Source for assay validity: the high-avidity TAPP1-PH biosensor was developed and validated as a selective and specific PI(3,4)P₂ reporter and shows that the lipid is predominantly a class I PI3K product also hydrolysed by PTEN [A-P5, A-P6]; TAPP-family PI(3,4)P₂ binding is genetically established as a negative regulatory input to Akt [A-P3] |

**Chosen readout:** pAKT-S473/T308 amplitude and decay kinetics after timed growth-factor stimulation (primary), with plasma-membrane PI(3,4)P₂ biosensor dynamics (secondary) and downstream pPRAS40/pS6 (tertiary) — all measured against the confound control at matched depletion depth in LN-428/OVCAR-5 and at matched growth effect in JURKAT/PANFR0034 (§2).

## 6. Experiment that separates the alternative explanation

- **Alternative:** the co-dependency reflects each line's PI3K-pathway state (a shared covariate across genes that restrain the pathway), not a function of PLEKHH3 in that pathway.
- **Experiment:** in LN-428 and OVCAR-5 and in an isogenic pair derived from one of them (PTEN knocked out vs parental, and PI3K-inhibited vs untreated), deplete PLEKHH3 acutely with dTAG and measure **growth effect and pAKT output as separate endpoints**, with PTEN and PLEKHA1 depletion as same-arm positive controls, the depth-matched control gene (§2) as the confound control, and JURKAT — negative lineage (r = −0.037), PTEN-null — as the line where the hypothesis predicts the smallest effect.
- **Readout if the prediction is right:** PLEKHH3 depletion raises stimulated pAKT-S473/T308 by ≥ 1.5-fold or prolongs its decay (t½ increased ≥ 1.5-fold) in the PI3K-competent background, in the same direction as PLEKHA1 depletion [A-P3], and this change exceeds the depth-matched control arm; the change is attenuated where the arm is already disabled (PTEN-null) and smallest in JURKAT.
- **Readout if the alternative is right:** growth effects track how much the pathway constrains the line, while pAKT amplitude and kinetics are indistinguishable from the depth-matched control in every background, including LN-428 and OVCAR-5. The call would then be reported as a **type-e regulatory co-dependency, not a function call** (DESIGN §4.4), and Template A's claim rewritten accordingly.

## 7. Decision rule (fixed in advance)

- **Supported:** dropout (where present) rescued by guide-resistant cDNA **AND** the module-specific signalling readout changed beyond the depth-matched control (§2), in both PI3K-competent backgrounds (LN-428, OVCAR-5) **AND** localisation compatible (any membrane/endomembrane pool, with or without stimulus-dependent recruitment) **AND** Tier-2 physical (PLEKHA1/PTPN13/PTEN by IP-MS) or epistatic (|π| < 0.15 with PTEN or PLEKHA1 on the pAKT readout) support.
- **Refuted:** a dropout that is not rescued, or incompatible localisation in both dependent lines (e.g. exclusively lumenal/secreted — which the UniProt `SIGNAL 1..18` sequence feature makes worth testing explicitly, and which the Tier-0 topology test now decides before the rest of the plan runs), or no pathway-readout change in any background.
- **Ambiguous:** anything else — reported as such with an alternative relationship type proposed. Specifically: pathway readout changes **without** epistasis or physical support ⇒ retain type d but drop the "PI(3,4)P₂ arm" refinement; lipid binding and membrane recruitment **without** a pathway readout change ⇒ propose type **c** (client/effector of the arm); growth effects **without** any pathway readout change ⇒ propose type **e** and withdraw the function call.

## 8. Evidence ledger (Part II)

| Claim | Source | Verbatim span | Verified |
|---|---|---|---|
| TAPP-family PI(3,4)P₂ binding is a negative regulatory input to Akt, so pAKT is the right endpoint and a PH point mutant is the right specificity control | PMID:21204784 (DOI 10.1042/BJ20102012) | "function as negative regulators of the insulin and PI3K signalling pathways" (abstract) | **Y** |
| The high-avidity tandem TAPP1-PH biosensor is a validated, selective PI(3,4)P₂ reporter | PMID:30591513 (DOI 10.1083/jcb.201809026) | "we developed a high-sensitivity genetically encoded biosensor for PI(3,4)P2, demonstrating high selectivity and specificity of the sensor for the lipid" (full text, PMC6400549) | **Y** |
| PI(3,4)P₂ is hydrolysed by PTEN, so PTEN status must be controlled in the lipid readout | PMID:30591513 | "we show that PI(3,4)P2 is also subject to hydrolysis by the tumor suppressor lipid phosphatase PTEN" (full text, PMC6400549) | **Y** |
| PTEN acts on PI(3,4)P₂ as well as PIP₃ — the isogenic PTEN arm is therefore informative for both lipids | PMID:29056325 (DOI 10.1016/j.molcel.2017.09.024) | "Here we show that PTEN also functions as a PI(3,4)P2 3-phosphatase, both in vitro and in vivo." (full text, PMC5678281; subscript markup removed) | **Y** |
| TAPP1–PTPN13 association runs through PTPL1's first PDZ domain — the pair-wise interaction to test by IP-MS | PMID:14516276 (DOI 10.1042/BJ20031154) | "PTPL1 binds to TAPP1 and TAPP2, principally though its first PDZ domain" (abstract) | **Y** |
| SLC30A5 is a ZnT-family zinc transporter (unrelated module) | PMID:39790720 (DOI 10.1002/jmd2.12465) | "SLC30A5 variant affecting function of ZnT5 zinc transporter" (title/full text, PMC11712426) | **Y** |
| SLC30A5 Chronos effects −0.555 (JURKAT) / −0.663 (PANFR0034), genome-wide mean +0.013 | `data/raw/depmap/CRISPRGeneEffect.csv` via `results/m7/scratch_reports_ccdc71l/ctrl.py` † | recomputed value, not a literature claim | **Y** (recomputed) |
| Cell lines, effects, expression, CN, TP53 status, media, selection funnel | `reports/data/PLEKHH3/bundle.md` §10 (from `results/ledger/*` and DepMap) | ledger rows | **Y** |
| LN-428 / OVCAR-5 selection values (lineage r 0.518 / 0.465; g effect +0.061 / +0.153; PTEN effect +0.419 / +0.798; expression 3.12 / 3.62; CN 0.61 / 1.27; 0 damaging and 0 hotspot PTEN mutations; NNMD −15.37 / −13.04; adherent; DMEM + 10% FBS / RPMI + 5% FBS) | `data/raw/depmap/{CRISPRGeneEffect,Model,OmicsExpressionTPMLogp1HumanProteinCodingGenes,OmicsCNGeneWGS,CRISPRConfounders,OmicsSomaticMutationsMatrix*}.csv` via `results/m7/scratch_reports_ccdc71l/rt_lines.py` † | recomputed values, not literature claims | **Y** (recomputed) |
| In LN-428/OVCAR-5, 699 genes match PLEKHH3's effect within ±0.06 with matched genome-wide mean; SLC30A5's effects there are −0.138 / +0.003 | `data/raw/depmap/CRISPRGeneEffect.csv` † | recomputed value | **Y** (recomputed) |
| UniProt Q7Z736 carries `SIGNAL 1..18` / `CHAIN 19..793`, evidence ECO:0000255 (prediction) | UniProt Q7Z736 flat file (`rest.uniprot.org`, retrieved 2026-10-30; copy in scratch) | "FT   SIGNAL          1..18" … "/evidence=\"ECO:0000255\"" | **Y** |

## 9. Red-team review (Part II)

- **Reviewer / date:** separate `red_team` agent, 2026-10-30. Its scope covered Parts I and II together, so the single unedited review at `reports/redteam/PLEKHH3.md` serves both; **verdict ACCEPT WITH REVISIONS**.
- **Experiment-specific findings and responses** (what would make the experiment uninformative: off-target guides, proximity effects, lineage dependence, rescue failure, assay insensitivity, biosensor buffering, the near-zero fitness amplitude) are carried in the point-by-point table in Appendix B, which covers every Part II item the reviewer raised; each Part II change is marked there with the section it landed in.
- **PI response (separate):** every required Part II fix was made rather than argued with. Nothing in the reviewer's text has been edited, abridged or answered inline.

---

## Appendix A. Evidence ledger

Every claim in this report that is not a ledger row from `results/ledger/*.tsv` or `reports/data/PLEKHH3/bundle.md` has a row here. Verification method: each PMID/DOI was resolved through the Europe PMC REST API on 2026-10-30, the abstract or full text retrieved, and the span checked as a substring of the retrieved text after stripping markup tags and collapsing whitespace (script: `results/m7/scratch_reports_ccdc71l/verify.py`, span list `spans.tsv`; **39/39 spans pass after the red-team revision**, which added A-P20 and A-P21). Rows that failed were deleted, not kept. The red-team reviewer re-resolved every row independently and found no span failure.

| Key | Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|---|
| A-P1 | TAPP1 (PLEKHA1) is constitutively associated with PTPL1/PTPN13 | PMID:14516276 / DOI 10.1042/BJ20031154 | "endogenously expressed TAPP1, is constitutively associated with the protein-tyrosine-phosphatase-like protein-1 (PTPL1 also known as FAP-1)" (text read: abstract) | Y |
| A-P2 | The TAPP1–PTPN13 interaction runs through PTPL1's first PDZ domain | PMID:14516276 / DOI 10.1042/BJ20031154 | "PTPL1 binds to TAPP1 and TAPP2, principally though its first PDZ domain" (abstract) | Y |
| A-P3 | PI(3,4)P₂-binding TAPP1/TAPP2 act as negative regulators of insulin/PI3K signalling (knock-in genetics) | PMID:21204784 / DOI 10.1042/BJ20102012 | "function as negative regulators of the insulin and PI3K signalling pathways" (abstract) | Y |
| A-P4 | PTEN is a PI(3,4)P₂ 3-phosphatase in addition to its PIP₃ activity | PMID:29056325 / DOI 10.1016/j.molcel.2017.09.024 | "Here we show that PTEN also functions as a PI(3,4)P2 3-phosphatase, both in vitro and in vivo." (full text, PMC5678281; subscript markup removed) | Y |
| A-P5 | A validated high-avidity PI(3,4)P₂ biosensor exists (tandem TAPP1-PH) | PMID:30591513 / DOI 10.1083/jcb.201809026 | "we developed a high-sensitivity genetically encoded biosensor for PI(3,4)P2, demonstrating high selectivity and specificity of the sensor for the lipid" (full text, PMC6400549) | Y |
| A-P6 | PI(3,4)P₂ is also hydrolysed by PTEN | PMID:30591513 / DOI 10.1083/jcb.201809026 | "we show that PI(3,4)P2 is also subject to hydrolysis by the tumor suppressor lipid phosphatase PTEN" (full text, PMC6400549) | Y |
| A-P7 | The family member PLEKHH2 uses its FERM domain to bind β-arrestin1 and displace FAK | PMID:36209201 / DOI 10.1038/s41419-022-05307-5 | "PLEKHH2 binding to β-arrestin1 through the FERM domain competitively inhibits" (full text, PMC9547923) | Y |
| A-P8 | PLEKHH2 overexpression activates the PI3K/AKT pathway (direction: positive) | PMID:36209201 / DOI 10.1038/s41419-022-05307-5 | "It also enhanced the phosphorylation of FAK and promoted the activity of the PI3K/AKT pathway." (full text, PMC9547923) | Y |
| A-P9 | A PH/MyTH4/FERM protein (MAX-1) acts with the UNC-5 receptor in *C. elegans* — the architecture is used for receptor-proximal regulation | PMID:35348689 / DOI 10.1093/genetics/iyac047 | "The PH/MyTH4/FERM myosin-like protein was previously shown to act with UNC-5 in VD axon guidance" (abstract) | Y |
| A-P10 | PLEKHH3 protein levels change with obstructive sleep apnoea severity (expression association only) | PMID:28520763 / DOI 10.1371/journal.pone.0176575 | "Protein expression levels of two genes related to endothelial tight junction (AMOT P130, and PLEKHH3)" (full text, PMC5435176) | Y |
| A-P11 | A PLEKHH3::BRAF fusion is reported in a mesenchymal neoplasm | PMID:42236131 / DOI 10.1136/jcp-2026-210784 | "identifying six kinase gene fusions (including novel IQSEC1::RAF1 and PLEKHH3::BRAF variants)" (abstract) | Y |
| A-P12 | A truncating PLEKHH3 variant segregates in a familial prostate-cancer pedigree | PMID:26585945 | "3 truncating variants, CYP3A43, DOK3, and PLEKHH3, demonstrated complete segregation" (abstract) | Y |
| A-P13 | PLEKHH3 is nominated bioinformatically as a possible regulator in BET/SYK-inhibited B-cell lymphoma cells | PMID:36230614 / DOI 10.3390/cancers14194691 | "PLEKHH3, DHRS2 and FOXP1-AS1 were identified as possible key regulators" (full text, PMC9564024) | Y |
| A-P14 | Wainberg 2021 predicts functions for 108 uncharacterised genes | PMID:33859415 / DOI 10.1038/s41588-021-00840-z | "predicts the functions of 108 uncharacterized genes" (abstract; full text not retrievable) | Y |
| A-P15 | hu.MAP 3.0 integrates > 25,000 MS experiments into > 15,000 human complexes | PMID:40425816 / DOI 10.1038/s44320-025-00121-5 | "we integrated >25,000 mass spectrometry experiments using a machine learning approach to identify >15,000 human protein complexes" (full text, PMC12222714) | Y |
| A-P16 | Replogle 2022 assigns function to poorly characterised genes from genome-scale Perturb-seq | PMID:35688146 / DOI 10.1016/j.cell.2022.05.013 | "We use transcriptional phenotypes to predict the function of poorly characterized genes" (full text, PMC9380471) | Y |
| A-P17 | SPOC is a trained classifier separating true from false AlphaFold-Multimer PPI predictions (Predictomes) | PMID:40015271 / DOI 10.1016/j.molcel.2025.01.034 | "we used machine learning on curated datasets to train a structure prediction and omics-informed classifier (SPOC)" (full text, PMC11931459) | Y |
| A-P18 | The Predictomes proteome-wide screen ranks all ~200 million human protein pairs before structural modelling | DOI 10.1101/2025.11.10.687652 (Europe PMC PPR1117736; Crossref resolved 2026-10-30) | "a classifier called KIRC (Knowledge-Informed Rapid Classifier), trained on biological features, was used to rank all 200 million possible protein pairs in the human proteome by their interaction likelihood" (abstract) | Y |
| A-P19 | SLC30A5 encodes the ZnT5 zinc transporter (unrelated module, matched-essentiality control) | PMID:39790720 / DOI 10.1002/jmd2.12465 | "SLC30A5 variant affecting function of ZnT5 zinc transporter" (title/full text, PMC11712426) | Y |
| A-P20 | SPOC's feature set includes DepMap co-dependency and BioGRID interaction data, so Predictomes scores are not independent of co-essentiality | PMID:40015271 / DOI 10.1016/j.molcel.2025.01.034 | "co-dependency data from DEPMAP" (full text, PMC11931459; in context: "genome-wide features of each protein pair that were external to AlphaFold, including co-dependency data from DEPMAP … and high throughput interaction experiments from the BioGRID database") | Y |
| A-P21 | BioGRID experiment counts are the single most important biological feature in SPOC | PMID:40015271 / DOI 10.1016/j.molcel.2025.01.034 | "the number of independent experiments supporting an interaction in the BioGRID database" (full text, PMC11931459; in context "…(21%)") | Y |

Project-file sources used for numbers (not literature claims): `reports/data/PLEKHH3/bundle.md` (all ledger values, partners, flags, orthogonal states, cell lines, figures); `results/ledger/top40_primary.tsv` (rank 12, p_cal, no demotion); `results/ledger/M6_SUMMARY.md` (tier branch, Σp_cal, caveats); `results/holdout_eval/SUMMARY.md` (hold-out rates and calibration); `results/m7/report_selection.md` (selection rule); `results/m7/L/HGNC_26105.md` (blinded literature items); `results/m7/judge/analysis_main_genes.tsv`, `results/m7/judge/analysis_main.md`, `results/m7/judge/scores/*`, `results/m7/answer_key_slots.tsv` (blinded verdicts and slot assignment); `results/m7/recall_probe_90.tsv` (recall probe); `DEVIATIONS.md` (operationalisations); `data/raw/humap3/*`, `data/raw/predictomes2025/*` (hu.MAP 3.0 and Predictomes values marked †); `data/derived/paralogues_by_matrix_index.npz` († 0 paralogues); `data/raw/depmap/CRISPRGeneEffect.csv` and `OmicsSomaticMutationsMatrixDamaging.csv` († recomputed correlations, PTEN-stratified correlations and control-gene effects). Recomputation scripts: `results/m7/scratch_reports_ccdc71l/{lines.py,lines3.py,par.py,ctrl.py,verify.py}`.

## Appendix B. Red-team review

- **Reviewer / date:** separate `red_team` agent (did not write this report), 2026-10-30.
- **Review text (unedited):** `reports/redteam/PLEKHH3.md`. It is kept as a separate file rather than inlined, unedited and unabridged, because this assignment permitted writing only to `reports/PLEKHH3.md`; nothing in it has been altered or omitted.
- **Verdict: ACCEPT WITH REVISIONS.** The reviewer independently re-resolved all 19 Appendix-A keys and the Part II ledger (no span failures), reproduced every number to three decimal places, ran an independent Europe PMC sweep that **upheld** the N3 class and the statement that no functional study of PLEKHH3 exists, and judged agent L's search for this gene complete. Several of the reviewer's attacks *strengthened* the call (specificity of the co-advantage; lineage robustness) while exposing one genuine defect the report had not seen.
- **Lint result (claims without a verified source):** pass — no claim in the revised report lacks either a project-file source or a verified Appendix-A key.

### Response to red team (point by point)

| # | Red-team point | Response | Where fixed |
|---|---|---|---|
| R1 | **The decisive experiment was specified in the one lineage where the predicted relationship is absent**: within-lineage r(PLEKHH3, PTEN) = −0.037 in Lymphoid (n = 97) vs 0.45–0.55 in CNS/Brain, Skin, Lung, Breast, Ovary; JURKAT and LP-1 are both Lymphoid; "fix the models at execution time" leaves the decisive arm unpre-registered | **Accepted in full — this was the report's most serious defect.** The within-lineage table is now in §3. Two PTEN-wild-type solid-lineage backgrounds are **named now** with all selection values recomputed (**LN-428**, ACH-000455, CNS/Brain, lineage r 0.518; **OVCAR-5**, ACH-001151, Ovary, lineage r 0.465), the selection rule gains the explicit criterion "lineage r(PLEKHH3, PTEN) > 0.4" plus adherent growth for imaging, back-ups are listed in order, and **JURKAT is demoted to a negative-lineage, PTEN-null specificity control in which the hypothesis predicts the smallest effect** | §0, §3, Part II §1, §2, §4, §6 |
| R2 | The matched-essentiality control is not executable where the decisive readout is taken: PLEKHH3 is neutral there, so "growth matched ±15%" is undefined and SLC30A5's matching does not transfer | **Accepted.** Verified independently: in LN-428/OVCAR-5, PLEKHH3's effects are +0.061/+0.153 and **699 genes** match them; SLC30A5 is −0.138/+0.003 there, not −0.555/−0.663 †. The confound control is now **split by arm** — growth-matched (SLC30A5) in JURKAT/PANFR0034, **depletion-depth-matched** (≥ 90% degron loss matched within ±10%; CRISPRi depth bands 50/75/90%) in the signalling backgrounds — and every decision rule, readout and §7 branch that referenced "matched growth effect" now references matched depletion where appropriate | Part II §2, §4, §5, §6, §7 |
| R3 | Missing specificity evidence: PTEN/PLEKHA1 are g's #1/#2 correlates genome-wide; signal confined to PI3K/mTOR brakes; TP53 0.014, PIK3CA −0.186 | **Accepted; this is now the report's lead argument.** Full table recomputed and added (brakes vs generic suppressors, with ranks), summarised in §0, and used in §8 to retire the generic-covariate version of the type-e alternative while keeping the PI3K-specific version alive | §0, §3, §8 |
| R4 | Re-frame LOPO 0/3 as non-independence: r(PTEN, PLEKHA1) = 0.453, partials 0.257 / 0.298 → ≈ 2 effective partners; and note the §4.3 exclusion is one flag away | **Accepted.** Both recomputed (plus PTPN13 partial 0.060) and used in §4 and §0; §5 now records "flagged: PTEN" and that 1 of 3 flags leaves the prediction one flag short of automatic exclusion | §0, §4, §5 |
| R5 | The pre-registered lineage leave-out tests the wrong lineage (lowest mean effect ≠ where the correlation lives); report the jackknife instead | **Accepted.** §5 now says the check as run is close to uninformative and points to the new §3 jackknife: max |Δr| +0.036/−0.024 (PTEN) and +0.006/−0.028 (PLEKHA1) over all lineages with n ≥ 20, lineage-demeaned r = 0.380 / 0.392. (Reported with both signs; the reviewer's "at most −0.024" refers to the most negative change, the largest magnitude is +0.036 from removing Lymphoid) | §3, §5 |
| R6 | §6's Predictomes list was ranked by the wrong column; true top SPOC pairs are GPRC5B 0.617, RFXANK 0.569, TMEM9B 0.557; RFXANK is also a BioPlex interactor | **Accepted.** KIRC- and SPOC-ranked lists are now separated and both given; RFXANK's BioPlex corroboration (HCT116, pInt 0.798) is reported as the single most interesting structural hit — and explicitly as one unrelated to the called module | §6, §11, Part II §4 |
| R7 | PLEKHH3–PTGES3 (SPOC 0.510) links g to a rank-21 co-dependency partner and was omitted | **Accepted.** Reported in §6 with its N(g) rank and zavg | §6 |
| R8 | Add AKT1S1 (rank 11) and GRB10 (rank 19) to the §4 neighbourhood narrative | **Accepted**, with NPRL2/DEPDC5 and PTGES3, and with the honest counterweight that AKT1S1's *raw* correlation is weak (0.056, rank 2,184). AKT1S1's presence in N(g) also pre-registers the pPRAS40 readout | §4 |
| R9 | `SIGNAL 1..18` is a sequence feature, not a keyword; if real, the PH/MyTH4/FERM domains are extracytosolic and the mechanism is impossible; no arm tests it | **Accepted — promoted to a first-class alternative and a gating experiment.** §8 gains alternative 6; Part II gains a **Tier-0 gating topology test** (protease protection + N-glycosylation scanning) run before any lipid or membrane-recruitment work, and the ledger records the feature with its ECO:0000255 (prediction, not experiment) evidence code | §8, Part II §1, §4, §8 |
| R10 | Tier-2 bait control must be membrane-localised and size-matched, not soluble; state whether AP-MS or TurboID is primary | **Accepted.** AP-MS is declared primary (because the receptor-heavy prior is AP-MS-derived and a proximity method would not be comparable), with a ~750–850 aa membrane-anchored control bait; TurboID is a separately controlled secondary arm | Part II §4 |
| R11 | The drug-interaction grid is optimistic and unpowered | **Accepted.** Made contingent on a positive Tier-1 signalling result and powered on its observed effect size, with ≥ 4 replicates per dose series | Part II §4 |
| R12 | The PH-domain point mutant is undefined, yet the lipid arm, Tier-3 rescue and the type-c branch depend on it | **Accepted.** The structure-guided alignment is now explicitly part of step 0 alongside the topology test, so both gate the costing | Part II §3, §4 |
| R13 | "Most specific term in the top 5" could be misread as "smallest" (172 vs 48 members) | **Accepted.** The technical meaning (DESIGN §3.1) and the member counts are now stated inline | §4 |
| R14 | Credit: the co-advantage reading survives attack; the report is candid about LOPO, hub PTEN and amplitude; the direction conflict with PLEKHH2 is correctly flagged | **Noted.** The surviving form of the type-e alternative (a PI3K-specific, non-PTEN-genotype state covariate) is stated explicitly rather than left implicit, so the strengthened case is not mistaken for a settled one | §8 |
