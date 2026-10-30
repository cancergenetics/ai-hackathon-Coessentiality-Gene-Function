# TM2D1 — deep-dive candidate report (Template A + Template B)

Primary top-40 rank 28 · predicted module: response to endoplasmic reticulum stress (GO:0034976) · novelty class N2 · literature search date 2026-10-30.
Companion report: `reports/TM2D2.md` (paralogue, same predicted module, rank 21). **The shared module analysis (TM2D1, TM2D2, CHIC2) is in `reports/TM2D2.md` §12, and the shared family/partner literature synthesis is in `reports/TM2D2.md` §7.3**; this report gives the TM2D1-specific evidence and refers there. M-keys are verified in `reports/TM2D2.md` Appendix A.1; T-keys are in Appendix A.2 below.

Deviation from the template's file layout (recorded, not a rule change): DESIGN §6.5 places Template B in `reports/TM2D1_experiments.md`; this assignment restricted writing to `reports/TM2D1.md` and `reports/TM2D2.md`, so Template B is included below as Part 2. Content and required fields are unchanged.

---

# Part 1. Template A

## 0. Bench summary (for a bench biologist; plain words)
- **Claim:** Cancer cell lines that grow poorly without TM2D1 also grow poorly without its paralogue TM2D2 and without three membrane-associated ubiquitin/quality-control proteins (JOSD1, AUP1, STUB1; also STUB1's adaptor CHIC2) [M53, M54]. The model calls this module "response to endoplasmic reticulum stress" (with "ERAD pathway" equally scored) [T11, T13]. Claim: TM2D1 *functions in / supports* the ER-stress response; relationship type unresolved (d). This is shared dependency, not a physical interaction.
- **Confidence:** p_cal = 0.0452 (95% interval 0.016–0.087) [T12] = expected probability (about 4.5%) that TM2D1 is later annotated to "response to endoplasmic reticulum stress" by experimental (D1-evidence) GO annotation within about 8 years [M65]; it covers the module term only, not the relationship type [M66]. Tier: none (p_cal fill) [M67].
- **Strongest reason to doubt:** the term rests on two partners (AUP1, STUB1) and is lost if either is removed [T14]; TM2D1's GLS network gives a different top term (lymphocyte activation) [T15]; no orthogonal class supports it after correction (§6); and TM2D1's dependency does not co-vary with the core HRD1–SEL1L–UBE2G2 ERAD machinery [M61, M62].
- **First experiment:** acute CRISPRi knockdown of TM2D1 in MAPAC-HS-77 and LXF-289 (dependent) and PANFR0344_T1 (non-dependent), next to AUP1, JOSD1, STUB1 knockdowns and a matched-essentiality control (PCM1), reading the UPR panel (BiP/HSPA5, CHOP/DDIT3, ATF4, spliced XBP1) and tunicamycin sensitivity; time about 6–8 weeks; approximate cost USD 10–15k (author's estimate). Details in Part 2 of this file; it can share arms and controls with the TM2D2 plan.
- Cancer-line essentiality is not organismal function: dependency in DepMap lines says the gene is needed for proliferation there, not what it does in the organism. In human blood, TM2D1 loss-of-function alleles are selected *for* in clonal expansions (penetrance 27%) [M27].

## Definitions used in this template
Relationship types (a–e) and novelty classes (N1–N3) as defined in `reports/TEMPLATE_candidate.md` (DESIGN §4.4, §1.5, §6.3).

## 1. Header
- Symbol: TM2D1 | HGNC ID: HGNC:24142 | previous symbols / aliases: — / BBP (beta-amyloid-binding protein; collides with branch-point-binding protein SF1 and butyl benzyl phthalate in searches) | UniProt: Q9BX74 | band: 1p31.3
- D1 / D2 / D3 values: True / False (UniProt annotation score 5) / True (D3_pubmed True, D3_tdark False; focused PMIDs 6; TDL Tbio) | curation-lag audit flag: not in the audit sample
- Stratum (§1.4): family other; expression expressed (not lineage-restricted); informativeness tertile high; core False
- Hypothesis (one sentence): TM2D1 functions in / supports the response to endoplasmic reticulum stress (GO:0034976), as part of a shared-dependency module with TM2D2, AUP1, JOSD1, STUB1 and CHIC2.
- Relationship type: **d (type unresolved)** under the DESIGN §4.4 text; the script rule returned **c** via the "Multi-pass membrane protein" ≥ 4-TM proxy [M74], but TM2D1 has two TM helices (129–149, 154–174) [T2, T3] and no enzyme/transporter keyword. No P/A/S support (type a excluded). Claim wording "functions in / supports".
- Novelty class: N2 (agent L) [T31]; unblinded search date 2026-10-30
- LLM-recall-probe flag (§6.2): **known** (confidence medium) — "binds beta-amyloid (BBP); its Drosophila homolog almondex is needed for Notch signalling" [T26]; probe answer logged at `results/m7/recall_probe_90.tsv`; matches network top term: no. The prediction (ER stress) is therefore not derived from the recalled function, but TM2D1 is a recognised gene.
- Calibrated probability p_cal: 0.0452 [95% CI 0.016–0.087] [T12]; calibration family: other; covariates inside H's 5th–95th percentile: yes (in_support)
- Tier: none (p_cal fill); rank in top 40: 28 (no demotion label; DEMETER2 not measured [T16])

## 2. The protein
- Domains (InterPro): IPR007829 TM2; IPR050932 TM2D1-3-like; Pfam PF05154 (TM2 domain 118–166). Signal peptide 1–37 [T4]; two TM helices 129–149 and 154–174 [T2, T3], with the C-terminal segment 175–207 annotated extracellular/luminal [T39]; N-glycosylated [T5]; no MTS. AlphaFold pLDDT: not retrieved. Deepest orthologue: metazoan only (absent from yeasts) [M9]; fly orthologue CG10795/*biscotti* [T34, M8].
- UniProt function: "May participate in amyloid-beta-induced apoptosis via its interaction with beta-APP42" [T1]; the G-protein-coupling claim of the original paper was not supported [M4].
- Class H (homology) evidence: no IBA/ISO annotation to the predicted term (bundle §6). Family-level data: fly Notch/γ-secretase step [M5–M7]; human TM2D3 ER localisation and ER-stress phenotype [M15–M18].
- Source keys: T1–T5, T34, T39, M4–M9, M15–M18.

## 3. Dependency profile
- Mean / SD of Chronos effect: −0.219 / 0.189 [T35]; fraction of lines < −0.5: 0.0676 (92 lines) [T40]; selective (not common-essential); NaN fraction 0.0000
- Expression: log2(TPM+1) ≥ 1 in 100% of lines (≥ 2 in 99.9%) [T41]; median 5.78. Dependency vs own expression: Spearman ρ = −0.023 (n = 1,292), no coupling; scatter in `reports/data/TM2D1/fig_profile.png` panel (b).
- Lineage enrichment (descriptive): Biliary Tract (36 lines; mean −0.277; MW p 0.0255), Bladder/Urinary Tract (34; −0.264; p 0.1519), Head and Neck (77; −0.263; p 0.0443).
- Split-half assessability: R(g) = 0.288 [T36]; null R0 mean 0.001 and maximum 0.024 over 200 matched genes, so every null value (and hence the 95th percentile) is below R(g); empirical p = 0.0050; assessable: yes. RBO R 0.463 (p 0.0050).
- Figure 1 (profile panel): `reports/data/TM2D1/fig_profile.png` (TM2D1 vs rank-1 partner JOSD1, raw Pearson r = 0.17 [M61]; chosen lines D1, D2 and control C marked).

## 4. Neighbourhood
Top-10 partners (K = 25; TM2D2 and TM2D3 excluded by the built-in paralogue rule):

| # | partner | zavg_BEF | z_B / z_E / z_F | GLS rank | partner function and essentiality (mean effect; frac < −0.5) | band | paralogue / shared-guide flag | hu.MAP-train |
|---|---|---|---|---|---|---|---|---|
| 1 | JOSD1 | 18.63 | 31.3/18.6/6.0 | 2 | membrane-associated deubiquitinase [M34, M35]; −0.16; 0.026 | 22q13.1 | no / not checkable | no |
| 2 | AUP1 | 17.31 | 27.5/15.3/9.1 | 1 | ERAD accessory factor; ER + lipid droplets; UBE2G2 recruitment [M29–M31]; in term; −0.14; 0.039 | 2p13.1 | no | no |
| 3 | STUB1 | 17.30 | 32.2/16.6/3.1 | 127 | E3 ligase CHIP, ER quality control [M36]; CHIC2 partner [M37–M40]; in term; −0.23; 0.079 | 16p13.3 | no | no |
| 4 | PCNX1 | 14.85 | 24.3/15.8/4.5 | 5 | uncharacterised (U gene); −0.04; 0.004 | 14q24.2 | paralogue of PCNX3 (other partner) | no |
| 5 | ZDHHC6 | 13.22 | 20.8/15.6/3.3 | 131 | ER S-acyltransferase [M43]; +0.08; 0.002 | 10q25.2 | no | no |
| 6 | CHIC2 | 11.27 | 17.5/13.4/2.9 | 310 | palmitoylated membrane adaptor of STUB1 [M37–M41]; −0.05; 0.007 | 4q12 | no | no |
| 7 | PCNX3 | 10.29 | 15.3/10.8/4.8 | 4 | uncharacterised (U gene); BioPlex edge with TM2D1; −0.41; 0.327 | 11q13.1 | paralogue of PCNX1 | no |
| 8 | MMD | 10.09 | 12.6/12.6/5.1 | 3 | GO: neuron differentiation; −0.03; 0.002 | 17q22 | no | no |
| 9 | ATP13A1 | 9.35 | 13.2/10.7/4.2 | 11 | ER P5A-ATPase dislocase [M42]; −0.21; 0.071 | 19p13.11 | no | no |
| 10 | DLG5 | 8.24 | 11.9/9.8/3.0 | 199 | GO: cell polarity, Hippo signalling; −0.23; 0.109 | 10q22.3 | no | yes (gene; pair no) |

No partner on chromosome 1. Shared-guide flags not evaluable.
- Figure 2 (neighbourhood network): `reports/data/TM2D1/fig_network.png`; module view `reports/data/TM2D_module/fig_module.png`.
- Top 3 terms (R1):

| term | S | p_emp | hypergeometric p (descriptive) | leave-one-partner-out (rank kept / supporting partners) |
|---|---|---|---|---|
| GO:0034976 response to endoplasmic reticulum stress | 34.612 | 0.0061 | 0.0185 | 0/2 [T14] |
| GO:0036503 ERAD pathway | 34.612 | 0.0020 | 0.0033 | 0/2 [T13] |
| GO:0043549 regulation of kinase activity | 21.753 | 0.0201 | 0.0024 | 2/3 |

- Second-ranked term: GO:0036503 ERAD pathway — tied on S with the top term and placed second by the ascending-GO-id tie-break [M75].

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | pass | arm 1p; no top-10 partner on chr 1; TM2D2, TM2D3 excluded as paralogues |
| Bidirectional-promoter / overlapping / readthrough partners | pass | 0/2 supporting partners flagged |
| Copy-number co-amplification | pass | AUP1 r = −0.01; STUB1 r = −0.03 |
| Hub-driven call (>50% of S from top-1% in-degree) | pass | hub share 0.00 |
| Lineage leave-out | pass | Biliary Tract removed (36 lines); same top term; N(g) overlap 0.84 [T17] |
| K = 10 / 50 | pass | same top term at both |
| Dependency vs own expression; TF / lineage-marker enrichment | pass | ρ = −0.023; TFs in N(g) 1, OR 0.51, q 1.0 |
| TP53 / p53-axis correlation | pass | p 0.6489, q 0.7415 [T37] |
| DEMETER2 replication | not measured | no supporting partner in DEMETER2 [T16] |
| GLS network top term (descriptive) | **different** | GO:0046649 lymphocyte activation [T15]; STUB1 is rank 127 and CHIC2 rank 310 in TM2D1's GLS row |
| Shared-sgRNA and per-guide check | not possible (guide maps / guide-level data not available) | recorded |

## 6. Orthogonal evidence matrix (four states: not measured / no support / supports / contradicts)

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | BioPlex/BioGRID-LTP/STRING-exp group; HCM SAINT | no support | 0 edges to the 151 term members; BioPlex edges ATG9A, DPY19L4, PCNX3, TM2D3 [T21]; BioGRID-LTP: APP; HCM not measured | 1.0000 | yes (family "other": any class) |
| A co-abundance | CCLE proteomics (ProteomeHD: not measured) | no support | member mean percentile 0.547 vs null 0.507, p 0.0420 [T18], not significant after Holm across 4 measured classes; pair-level TM2D1–AUP1 r 0.41 (97th percentile) [T20], TM2D1–CHIC2 0.34 (92%) [T42]; top co-abundant protein TM2D3 (0.63), also APP (0.59) [T19] | 0.0420 (class Simes; fails Holm) | yes |
| L localisation | HPA v25.1 (Approved) | no support | nucleoplasm, vesicles; no high-reliability call [T22] | 1.0000 | yes |
| G perturbation phenotype | Perturb-seq K562 GW | no support | member mean 0.488 vs null 0.508 [T44] | 0.9051 | yes |
| S structure | Burke 2023 AF2 | not measured | TM2D1 not modelled | — | yes |
| H homology | IBA/ISO | no annotation to the term | — | reported only | — |

Reported but not counted: hu.MAP 3.0 places TM2D1 with TM2D3 (0.918), PCNX3 (0.879) [M46, M47] and in complexes with PCNX3 and with TSPAN17/TSPAN14/KCNN4 [T9, T10], not with AUP1 (0.16) [M48]; Predictomes: TM2D1–TM2D3 SPOC 0.971, TM2D1–TM2D2 0.965 [M49, M51], no rows with AUP1, JOSD1, STUB1 or CHIC2 [M52]. No contradiction. False-support rate of the rule on decoys 0.223 [M70].

## 7. Literature (blinded step, then synthesis)

### 7.1 Blinded summary (agent L, `results/m7/L/HGNC_24142.md`)
Eight items, none DepMap-derived: UniProt function (Aβ-induced apoptosis via beta-APP42; functional); BBP binds Aβ and sensitises cells to Aβ toxicity (2001; functional); BBP does not couple directly to G proteins (2003; functional); UniProt caution on the G-protein claim (mention); fly TM2D family knockouts (functional, family level); TM2D1 overexpression reverses anaesthetic effects in colorectal cancer cells (functional); TM2D1 among bioinformatic hub genes for ankylosing spondylitis with sarcopenia (mention).

### 7.2 Blinded verdicts
Real statement (slot B, "response to endoplasmic reticulum stress") 0 [T27, T28]; decoys 0, 0, 0; judges J1 0 [T29], J2 0 [T30]; adjudicator n/a. TM2D1 contributes d = 0 to the primary sign-flip test.

### 7.3 Unblinded synthesis
Shared family and partner literature: see `reports/TM2D2.md` §7.3 (verdict there: supports at family level via TM2D3's ER localisation and ER-stress phenotype [M15–M18], refines the module away from canonical HRD1 ERAD [M62], does not contradict). TM2D1-specific evidence:
- TM2D1 was cloned as BBP, an amyloid-β-binding protein whose expression made cells vulnerable to Aβ toxicity [M2, M3]; the proposed G-protein coupling was not confirmed [M4]. UniProt's function line rests on these papers [T1]. These findings neither support nor contradict an ER-stress role; an Aβ-binding, N-glycosylated [T5] two-TM protein [T2, T3] with a luminal C-terminus [T39] is compatible with residence in the secretory pathway, but no study has localised endogenous TM2D1 to the ER (HPA: nucleoplasm/vesicles, Approved only [T22]).
- In a genome-wide phagocytosis screen TM2D1 was among the strongest regulators together with TM2D2 and TM2D3 [M24]; the family is required together in flies, where *bisc* is the TM2D1 orthologue [M5, M6, T34].
- Cancer-cell overexpression studies report that TM2D1 promotes hepatocellular carcinoma cell proliferation and EMT [T6] and reverses anaesthetic effects in colorectal cancer cells [T7]; both are single-lab overexpression studies and do not address ER stress.
- In UK Biobank blood, TM2D1 LoF alleles drive CN-LOH clonal expansions with 27% penetrance [M27], the second highest after TM2D3 [M26] — in blood, losing TM2D1 confers a proliferative advantage, the opposite sign to the cancer-line dependency.
- CCLE proteomics (project data, not literature): TM2D1 protein co-varies most with TM2D3 and also with APP [T19], consistent with the family complex and the Aβ literature, and with AUP1 at the 97th percentile [T20].
- Verdict for TM2D1: **literature neither supports nor contradicts the ER-stress call directly; family-level evidence (TM2D3) supports it; the strongest gene-specific literature (Aβ binding) is orthogonal to it.** No DepMap-derived literature found.
- Closest prior publication and what co-essentiality adds: as for TM2D2 (`reports/TM2D2.md` §7.3) — Gabillard-Lefort et al. 2025 (TM2D3, ER stress) [M15–M18] and Salazar et al. 2021 (family acts together) [M5, M6]. For TM2D1 specifically, the closest are Kajkowski et al. 2001 [M2, M3] and Haney et al. 2018 [M24]; co-essentiality adds the link to AUP1/JOSD1/STUB1–CHIC2, not found in the literature as of 2026-10-30.
- Prior prediction lists containing this gene: Wainberg 2021 — not in the main text [M72], supplementary not checked (unknown); hu.MAP 3.0 — yes (TM2D3, PCNX3, TSPAN17/TSPAN14/KCNN4 complexes; no ER-stress member) [T9, T10, M46, M47]; Replogle 2022 — TM2D1 perturbed in K562 GW (profile measured; top correlated perturbations SIRT7, SRPRB, r 0.21 [T43]), no module call checked; Predictomes — TM2D family interfaces only [M49, M51, M52].
- Post-freeze (after 2026-10-29) papers confirming the prediction: none found (Europe PMC, 2026-10-30).

## 8. Alternative explanations
- **Paralogue artefact (TM2D1–TM2D2 zavg_BEF 31.70):** handled as in `reports/TM2D2.md` §8 — the paralogues are excluded from each other's lists [M53], but their lists overlap almost entirely [M54], so TM2D1 and TM2D2 are one observation. Guide cross-cutting between TM2D1 and TM2D2/TM2D3 cannot be excluded without guide-level data; it would not create the shared correlation with partners on other chromosomes.
- **Proximity, CN, hub, lineage, TP53:** no flags (§5).
- **Network-construction dependence:** TM2D1's GLS network gives a different top term [T15], and STUB1 drops to GLS rank 127 — the ER-stress call is less stable for TM2D1 than for TM2D2 (whose GLS top term is the same [Q14 in `reports/TM2D2.md`]).
- **Label artefact:** term carried by AUP1 and STUB1 only, lost if either is removed [T14]; the third-ranked term (regulation of kinase activity) is more robust to partner removal (2/3) but has lower S.
- **Strongest competing biological hypothesis:** a plasma-membrane/endosomal receptor-homeostasis module (TM2D3–Notch surface presentation [M14]; STUB1–CHIC2–cytokine receptors [M37, M38]; JOSD1 at the plasma membrane [M34]); for TM2D1 an additional reading is an Aβ/APP-related membrane function [M2, T19]. Separating experiment: Part 2 §6.
- **Supplier/client:** TM2D1 may be a client of the AUP1 or STUB1–CHIC2 machinery; Tier-1 partner-level westerns address this.

## 9. Falsifying observations
Written from the prediction before the unblinded literature search, after the bundle (which shows the orthogonal matrix) had been seen — not fully blind.
1. Acute TM2D1 knockdown in MAPAC-HS-77 and LXF-289 does not change BiP/HSPA5, CHOP/DDIT3, ATF4 or XBP1 splicing, nor tunicamycin sensitivity, beyond the matched-essentiality control (PCM1) at matched growth effect, while AUP1/JOSD1/STUB1 knockdowns do.
2. TM2D1 knockdown leaves NHK-HA ERAD substrate turnover unchanged.
3. Endogenously tagged TM2D1 has no ER pool in either dependent line.
4. TM2D1 + AUP1 (or + JOSD1) double knockdown is additive or synergistic for growth.
5. Guide-resistant TM2D1 cDNA does not rescue the growth defect.

## 10. Experiments
See Part 2 of this file (Template B); shared design with `reports/TM2D2.md` Part 2.

## 11. Novelty and external benchmarks
hu.MAP 3.0 and Predictomes support a TM2D family complex [M46, M49, M51] and place TM2D1 with PCNX3 and tetraspanins [T9, T10], not with the ER-stress partners [M48, M52]. Wainberg 2021: not in the main text [M72]. Replogle 2022: TM2D1 profile measured, no support for the term (§6). What is new: TM2D1's shared dependency with AUP1, JOSD1 and STUB1–CHIC2 and the resulting ER-stress prediction (not found in the literature as of 2026-10-30); module-level interpretation in `reports/TM2D2.md` §12.

## Appendix A. Evidence ledger
Verification procedure as described in `reports/TM2D2.md` Appendix A (texts in `results/m7/scratch_reports_tm2d/texts/`, script `verify.py`, PMIDs resolved in Europe PMC, DOIs in Crossref, 2026-10-30). "⇥" marks a tab and "⏎" a line break inside a span.

### A.1 Shared rows
The shared M-keys (M1–M83) are listed with verbatim spans and verification in `reports/TM2D2.md`, Appendix A.1 (all verified = Y; same verification run, `results/m7/scratch_reports_tm2d/verify_result.json`).

### A.2 TM2D1-specific rows (T-keys)
| Key | Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|---|
| T1 | UniProt TM2D1 function statement | UniProt:Q9BX74 (entry v145, 2026-09-02); checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "May participate in amyloid-beta-induced apoptosis via its interaction with beta-APP42." (text read: database entry) | Y |
| T2 | TM2D1 topology: signal peptide 1-37, two TM helices 129-149 and 154-174 | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "FT   TRANSMEM        129..149" (text read: database entry) | Y |
| T3 | TM2D1 second TM helix | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "FT   TRANSMEM        154..174" (text read: database entry) | Y |
| T4 | TM2D1 signal peptide | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "FT   SIGNAL          1..37" (text read: database entry) | Y |
| T5 | TM2D1 is N-glycosylated | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "-!- PTM: N-glycosylated. {ECO:0000269\|PubMed:11278849}." (text read: database entry) | Y |
| T6 | TM2D1 promotes HCC cell proliferation/EMT when overexpressed | PMID:33948373; checked in `results/m7/scratch_reports_tm2d/texts/33948373.abs.txt` | "TM2D1 overexpression induced HCC cell proliferation, migration and invasion" (text read: abstract) | Y |
| T7 | TM2D1 overexpression reverses anaesthetic effects in CRC cells | PMID:38920064 (DOI 10.2174/0113862073281046240527165415); checked in `results/m7/scratch_reports_tm2d/texts/38920064.abs.txt` | "TM2D1 overexpression reversed the effect of sevoflurane and propofol on colorectal cancer cell biology behaviors" (text read: abstract) | Y |
| T8 | TM2D1 RefSeq transcript | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "RefSeq; NP_114416.1; NM_032027.3." (text read: database entry) | Y |
| T9 | hu.MAP 3.0 complexes containing TM2D1 | data/raw/humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv; checked in `data/raw/humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv` | "huMAP3_11644.1,6,Q9BX74 Q9H6A9,TM2D1 PCNX3" (text read: file) | Y |
| T10 | hu.MAP 3.0 complex TSPAN17-TM2D1 | data/raw/humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv; checked in `data/raw/humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv` | "huMAP3_04803.1,1,Q96FV3 Q9BX74,TSPAN17 TM2D1" (text read: file) | Y |
| T11 | Predicted term, S, supporting partners | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| S / supporting partners / term size (current V2) \| 34.612 / 2 / 151 \|" (text read: file) | Y |
| T12 | p_cal and CI | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| p_cal 95% interval \| 0.016–0.087 (cluster bootstrap, 2000 refits) \|" (text read: file) | Y |
| T13 | Top-2 terms tie at S 34.612 | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| 2 \| GO:0036503 \| ERAD pathway \| 34.612 \| 2 \| 62 \| 0.0033 \| 0.0020 \| other \| 0/2 \|" (text read: file) | Y |
| T14 | LOPO: term loses rank 1 if either supporting partner is removed | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| 1 \| GO:0034976 \| response to endoplasmic reticulum stress \| 34.612 \| 2 \| 151 \| 0.0185 \| 0.0061 \| other \| 0/2 \|" (text read: file) | Y |
| T15 | GLS top term differs | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| GLS network top term (K = 25, §3.1 exclusions) † \| different \| GO:0046649 lymphocyte activation \|" (text read: file) | Y |
| T16 | DEMETER2 not measured | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| DEMETER2 replication (mean partner r ≥ 95th pct of random sets) \| not measured \| partners in D2 0; mean r —; null 95th pct — \|" (text read: file) | Y |
| T17 | Lineage leave-out retained | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| Lineage leave-out \| retained \| removed Biliary Tract (36 lines; mean effect -0.277); top term after refit GO:0034976 response to endoplasmic reticulum stress; N(g) overlap 0.84 \|" (text read: file) | Y |
| T18 | Orthogonal A class p 0.0420 (CCLE proteomics) - not significant after Holm | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| CCLE_proteomics \| A \| continuous \| True \| 125 \| 0.547 \| 0.507 \| 0.0420 \|  \|" (text read: file) | Y |
| T19 | CCLE proteomics: TM2D1 top co-abundant protein TM2D3 (0.63), APP (0.59) | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| CCLE_proteomics \| yes \| TM2D3 (0.63), ADAM28 (0.61), UBTD1 (0.60), APP (0.59)" (text read: file) | Y |
| T20 | CCLE proteomics TM2D1-AUP1 r 0.41 (97th pct) | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| AUP1 \| N \| n.m. \| N \| N \| n.m. \| N \| n.m. (g) \| 0.41 (97%) \|" (text read: file) | Y |
| T21 | BioPlex3 interactors of TM2D1 | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| BioPlex3 \| yes \| 4 \| 0 \| ATG9A, DPY19L4, PCNX3, TM2D3 \|" (text read: file) | Y |
| T22 | HPA localisation (Approved): nucleoplasm, vesicles | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "reliability Approved; main: Nucleoplasm; additional: Vesicles" (text read: file) | Y |
| T23 | Chosen dependent lines | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| ACH-002672 \| MAPAC-HS-77 \| Pancreas \| Pancreatic Adenocarcinoma \| -0.57 \| -0.48 \| 6.50 \| 0.99 \| mut \| -10.98 \| 0.98 \| DMEM:F12 + 20% horse serum (MF-007-011) \|" (text read: file) | Y |
| T24 | Second dependent line | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| ACH-000787 \| LXF-289 \| Lung \| Non-Small Cell Lung Cancer \| -0.69 \| -0.40 \| 4.53 \| 0.76 \| mut \| -9.84 \| 0.97 \| F12 + 10% FBS (MF-004-001) \|" (text read: file) | Y |
| T25 | Control line | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| ACH-003035 \| PANFR0344_T1 \| Pancreas \| Pancreatic Adenocarcinoma \| -0.19 \| -0.17 \| 6.98 \| 1.18 \| mut \| -7.32 \| 0.95 \| OPAC:Ad+++ (1:1) (MF-031-002) \|" (text read: file) | Y |
| T26 | Recall probe: recognised (medium) | results/m7/recall_probe_90.tsv; checked in `results/m7/recall_probe_90.tsv` | "HGNC:24142 ⇥ TM2D1 ⇥ TM2-domain membrane protein that binds beta-amyloid (BBP); its Drosophila homolog almondex is needed for Notch signalling. ⇥ medium ⇥ yes" (text read: file) | Y |
| T27 | Blinded judging: real 0, decoys 0 | results/m7/judge/analysis_main_genes.tsv; checked in `results/m7/judge/analysis_main_genes.tsv` | "J005 ⇥ HGNC:24142 ⇥ TM2D1 ⇥ top40 ⇥ 28 ⇥ 0.0 ⇥ 0.0 ⇥ 0 ⇥ 0.0 ⇥ N2" (text read: file) | Y |
| T28 | Real statement was slot B | results/m7/answer_key.tsv; checked in `results/m7/answer_key.tsv` | "M7-019 ⇥ HGNC:24142 ⇥ TM2D1 ⇥ top40 ⇥ 28 ⇥ 4 ⇥ B" (text read: file) | Y |
| T29 | J1 scored slot B 0 | results/m7/judge/scores/J1_main1.tsv; checked in `results/m7/judge/scores/J1_main1.tsv` | "J005 ⇥ B ⇥ 0 ⇥ Rows 1-5 amyloid-beta binding/toxicity; ER stress not addressed" (text read: file) | Y |
| T30 | J2 scored slot B 0 | results/m7/judge/scores/J2_main1.tsv; checked in `results/m7/judge/scores/J2_main1.tsv` | "J005 ⇥ B ⇥ 0 ⇥ Beta-amyloid toxicity/caspase-dependent vulnerability only; ER stress response not shown." (text read: file) | Y |
| T31 | Agent L novelty class N2 | results/m7/L/HGNC_24142.md; checked in `results/m7/L/HGNC_24142.md` | "novelty_class: N2" (text read: file) | Y |
| T32 | Matched-essentiality control PCM1 (recomputed) | results/m7/scratch_reports_tm2d/ctrl.py -> ctrl_out.txt; checked in `results/m7/scratch_reports_tm2d/ctrl_out.txt` | "PCM1   -0.259        0.136 -0.018       -0.54       -0.74" (text read: file (recomputed)) | Y |
| T33 | Module-gene effects in chosen lines (recomputed) | results/m7/scratch_reports_tm2d/lines.py -> lines_out.txt; checked in `results/m7/scratch_reports_tm2d/lines_out.txt` | "TM2D1         -0.57       -0.69       -0.58       -0.60       -0.80       -0.44       -0.19        0.41" (text read: file (recomputed)) | Y |
| T34 | fly orthologue of TM2D1 is CG10795/bisc | PMID:34905536 (DOI 10.1371/journal.pgen.1009962); checked in `results/m7/scratch_reports_tm2d/texts/34905536.full.txt` | "Null alleles of fly orthologs of TM2D2 (CG11103/amrt) and TM2D1 (CG10795/bisc) phenotypically mimics the loss of TM2D3 (amx)" (text read: full text) | Y |
| T35 | TM2D1 dependency profile: mean/SD | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| Mean / SD Chronos \| -0.219 / 0.189 \|" (text read: file) | Y |
| T36 | TM2D1 split-half R | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| Split-half R(g) (seeds 0–4, K = 25) \| 0.288 \|" (text read: file) | Y |
| T37 | TP53 no flag | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| TP53 status (Mann–Whitney, BH q < 0.05 over primary top 40) \| no flag \| mut 902 / WT 459; p 0.6489; q 0.7415; median diff (mut − WT) -0.007 \|" (text read: file) | Y |
| T38 | Antibodies listed for TM2D1 | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "Antibodypedia; 46902; 62 antibodies from 19 providers." (text read: database entry) | Y |
| T39 | TM2D1 C-terminal segment 175-207 annotated extracellular (luminal side) | UniProt:Q9BX74; checked in `results/m7/scratch_reports_tm2d/texts/uniprot_Q9BX74.txt` | "FT   TOPO_DOM        175..207 ⏎ FT                   /note="Extracellular"" (text read: database entry) | Y |
| T40 | TM2D1 frac lines < -0.5 | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| Fraction of lines < −0.5 (n) \| 0.0676 (92) \|" (text read: file) | Y |
| T41 | TM2D1 expressed in essentially all lines | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| Fraction lines log2(TPM+1) ≥ 1 / ≥ 2 \| 1.000 / 0.999 \|" (text read: file) | Y |
| T42 | CCLE proteomics TM2D1-CHIC2 r 0.34 (92nd pct) | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| CHIC2 \| N \| n.m. \| n.m. \| N \| n.m. \| N \| n.m. (g) \| 0.34 (92%) \|" (text read: file) | Y |
| T43 | K562 GW Perturb-seq: TM2D1 top correlated perturbations | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| PerturbSeq_K562_GW \| yes \| SIRT7 (0.21), SRPRB (0.21)" (text read: file) | Y |
| T44 | K562 GW Perturb-seq support test for the term | reports/data/TM2D1/bundle.md; checked in `reports/data/TM2D1/bundle.md` | "\| PerturbSeq_K562_GW \| G \| continuous \| True \| 123 \| 0.488 \| 0.508 \| 0.9051 \|  \|" (text read: file) | Y |

## Appendix B. Red-team review
Written by a separate agent that argues the artefact explanation (hub, mitochondrial or ribosomal dominance, proximity, lineage, multifunctional partners, curation lag). Appended unedited.
- Reviewer / model / date: pending
- Review text: pending
- Lint result (claims without a verified source): pending
- PI response (separate, below the review): pending

---

# Part 2. Template B: experiment plan (TM2D1)

Same design as `reports/TM2D2.md` Part 2 (tiers, readouts, decision rule); this part gives TM2D1's lines, controls and reagents. MAPAC-HS-77 and LXF-289 also depend on TM2D2 (−0.65, −0.67) [M83 and `reports/TM2D2.md` Q24], so TM2D1 and TM2D2 arms (and the TM2D1+TM2D2 double knockdown) can share one experiment and its controls.

## 1. Context
- Gene: TM2D1 | hypothesis: TM2D1 functions in / supports the response to ER stress (GO:0034976), as part of a shared-dependency module with TM2D2, AUP1, JOSD1, STUB1 and CHIC2 | relationship type: d (type unresolved; script c via a TM-count proxy TM2D1 does not meet [T2, T3, M74]) | novelty class: N2
- LLM-recall-probe flag: known (medium; Aβ binding/Notch, not ER stress) | calibrated probability: 0.0452 (calibration family other) | tier: none (p_cal fill)
- Strongest alternative explanation: plasma-membrane/endosomal receptor homeostasis (Notch surface presentation [M14], STUB1–CHIC2 cytokine-receptor control [M37, M38], JOSD1 [M34]) or an APP/Aβ-related membrane function [M2, T19]; network-construction dependence (GLS top term differs [T15]).
- Decisive experiment (one sentence): acute CRISPRi knockdown of TM2D1 (3 guides, plus guide-resistant cDNA rescue arm) in MAPAC-HS-77 and LXF-289 and in the non-dependent PANFR0344_T1, side by side with AUP1, JOSD1 and STUB1 knockdowns and the matched-essentiality control PCM1, measuring the UPR panel (HSPA5/BiP, DDIT3/CHOP, ATF4; XBP1 splicing) at day 4–5 and the tunicamycin dose–response; refuted if TM2D1 knockdown moves none of these beyond PCM1 at matched growth effect.
- Falsifying observation (copied from Template A §9): acute TM2D1 knockdown in MAPAC-HS-77 and LXF-289 does not change BiP/HSPA5, CHOP/DDIT3, ATF4 or XBP1 splicing, nor tunicamycin sensitivity, beyond the matched-essentiality control (PCM1) at matched growth effect, while AUP1/JOSD1/STUB1 knockdowns do.

## 2. Cell lines (selection rule)
- Two dependent lines (TM2D1 ≤ −0.5; JOSD1 ≤ −0.3; expressed; not amplified; TP53-mutant first; best screen quality; second line from another lineage):
  - ACH-002672 MAPAC-HS-77 (pancreatic adenocarcinoma): TM2D1 −0.57, JOSD1 −0.48, log2(TPM+1) 6.50, relative CN 0.99, TP53 mutant, DMEM:F12 + 20% horse serum [T23]
  - ACH-000787 LXF-289 (NSCLC): TM2D1 −0.69, JOSD1 −0.40, 4.53, CN 0.76, TP53 mutant, F12 + 10% FBS [T24]
  - Other module genes in these lines (recomputed, descriptive): MAPAC-HS-77 TM2D2 −0.65, TM2D3 −0.20, AUP1 −0.11, STUB1 −0.40; LXF-289 TM2D2 −0.67, TM2D3 −0.44, AUP1 −0.20, STUB1 −0.23 [T33, M83]. AUP1 itself is barely a dependency in these lines, so AUP1 knockdown is a mechanistic positive control, not a growth-matched one.
- Control line (expresses TM2D1, not dependent, same lineage as line 1): ACH-003035 PANFR0344_T1, TM2D1 −0.19, log2(TPM+1) 6.98 [T25]. Caveat: it is grown in organoid medium (OPAC:Ad+++); if it cannot be run in parallel, the next non-dependent pancreatic line must be chosen by the same rule (not done here).
- Common-essential genes: no (6.8% of lines < −0.5 [T40]). Controls: guide-resistant cDNA rescue, two non-targeting guides, AAVS1 cutting control, matched-essentiality control gene.
- Baseline medium: the DepMap screen media — DMEM:F12 + 20% horse serum (MAPAC-HS-77; MF-007-011), F12 + 10% FBS (LXF-289; MF-004-001), OPAC:Ad+++ (1:1) (PANFR0344_T1; MF-031-002). Tunicamycin/thapsigargin arms are sensitising, not baseline.
- Essential-gene confound control: CRISPRi knockdown of TM2D1 time-matched to AUP1/JOSD1/STUB1 knockdown, against PCM1 (mean effect −0.259, frac < −0.5 0.136; MAPAC-HS-77 −0.54, LXF-289 −0.74; r with TM2D1 −0.018; centriolar-satellite module, unrelated) [T32]. Readouts compared at matched population-doubling loss (day 4–5).

## 3. Reagents
- 3 sgRNAs per gene (CRISPRi TSS guides, e.g. Dolcetto/hCRISPRi-v2; Brunello for KO arm): sequences **not retrieved in this report** (no local library file; to fill before ordering); 2 non-targeting guides; AAVS1 cutting control. Per-guide DepMap effects not available locally.
- Sequence-level off-target check of every guide: **pending** (Cas-OFFinder or CRISPOR, GRCh38; no perfect or 1-mismatch site in another gene, explicitly none in TM2D2, TM2D3 or the partner loci).
- CRISPRi guides if the locus is amplified: not required (CN 0.99, 0.76); CRISPRi used for acute titratable knockdown.
- Guide-resistant cDNA: TM2D1 NM_032027.3 / NP_114416.1 [T8], silent PAM/seed mutations for the KO arm.
- Validated antibody, or endogenous tag: Antibodypedia lists 62 antibodies [T38]; validate on knockout lysate. Endogenous C-terminal small epitope tag (HA/ALFA): N-terminal signal peptide 1–37 [T4] precludes N-terminal tags; C-terminal segment 175–207 is luminal/extracellular [T39].
- Partner / organelle antibodies and UPR panel: as in `reports/TM2D2.md` Part 2 §3 (AUP1, JOSD1, STUB1, CHIC2, UBE2G2; calnexin, GM130, EEA1, LAMP1, Na+/K+-ATPase; BiP, CHOP, ATF4; XBP1s RT-PCR; NHK-HA reporter [M32]); add APP (TM2D1 co-varies with APP protein [T19]).

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of TM2D1 with AUP1, JOSD1, STUB1 (TM2D2/TM2D3 as reference) | days | Confident, conserved interface | No interface (does not exclude types b–e) | yes | TM2D1–TM2D3 SPOC 0.971 and TM2D1–TM2D2 0.965 already in Predictomes [M49, M51]; no confident interface expected with AUP1/JOSD1/STUB1 [M52] |
| 1 | Competitive growth (GFP mix), 3 guides plus rescue, dependent vs control lines | 2–3 wk | Dropout only in MAPAC-HS-77 / LXF-289; rescued | No dropout, or no rescue | yes (prerequisite) | ≥ 2 of 3 guides deplete by day 14 in dependent lines only; cDNA restores |
| 1 | Essential-gene confound control: acute TM2D1 knockdown time-matched to partner knockdown, vs PCM1 | 2–4 wk | UPR panel and tunicamycin response change beyond PCM1 at matched growth effect | Same change as PCM1 | **yes — decisive** | Right: HSPA5, DDIT3, ATF4, XBP1s up; tunicamycin IC50 down, same direction as AUP1/JOSD1/STUB1 knockdown (cf. TM2D3 loss [M16]; Aup1 knockdown [M33]). Wrong: TM2D1 ≈ PCM1 |
| 1 | Localisation with markers | 2–4 wk | ER pool (calnexin) | Plasma membrane/endosome/nucleus only | yes | HPA call nucleoplasm/vesicles (Approved) [T22]; an ER pool is not yet shown |
| 1 | Module-specific readout after KO: NHK-HA cycloheximide chase | 2–4 wk | NHK-HA stabilised, as after AUP1 loss [M32] | Normal | yes | secondary; tied "ERAD pathway" term, expected weaker (`reports/TM2D2.md` §12.4) |
| 1 | Partner protein levels after TM2D1 KO (and the reverse) | 2 wk | Co-destabilisation (types a/b) | Stable (favours c/d) | yes | AUP1, JOSD1, STUB1, CHIC2, TM2D2, TM2D3, APP |
| 2 | IP-MS / TurboID of tagged TM2D1 vs an unrelated tagged ER membrane control | 1–2 mo | Partners enriched (SAINT) | Absent, or another module appears | if Tier 1 positive | TM2D3 and PCNX3 expected (BioPlex [T21]); AUP1/JOSD1/STUB1/CHIC2 would support physical membership |
| 2 | BN-PAGE / SEC co-migration | 1 mo | Co-migrates; KO stalls assembly | Separate | optional | TM2D complex with/without TM2D1 |
| 2 | Double KO with partner (epistasis) | 1–2 mo | No extra defect | Additive or synergistic | yes | TM2D1+AUP1, TM2D1+JOSD1, TM2D1+TM2D2 in MAPAC-HS-77 |
| 2 | Arrayed CRISPRi Perturb-seq with partners | 2 mo | Signatures cluster | Distinct | optional | K562 GW profile of TM2D1 shows no term support [T44] |
| 3 | Interface mutants fail to rescue; reconstitution, activity or structure | 6–12 mo | Interface or activity required | Mutants rescue | later | conserved TM2 domain / DRF motif [M10] |

Type-specific rows: none (type d).

## 5. Module readouts
| Module | Readouts |
|---|---|
| Other (module not listed): response to ER stress / ERAD | UPR panel ATF4, HSPA5, DDIT3 (+ XBP1s), tunicamycin sensitivity; source PMID 40449487 [M16]; NHK cycloheximide chase; source PMID 34879065 [M32] |

Chosen readout: UPR panel + tunicamycin dose–response (decisive); NHK-HA chase (secondary).

## 6. Experiment that separates the alternative explanation
- Alternative: plasma-membrane / endosomal receptor homeostasis, or an APP-related membrane function | experiment: in the same knockdown samples, measure surface Notch1 and Notch2 by flow cytometry (reduced in Tm2d3-deficient cells [M14]) and run a cell-surface biotinylation proteome, next to the UPR panel; also blot APP, with which TM2D1 protein co-varies in CCLE proteomics [T19] | readout if prediction right: UPR panel shifted beyond PCM1 and an ER pool of tagged TM2D1, with surface changes at most secondary | readout if alternative right: surface receptor levels (Notch1/2 or others) fall with no UPR change beyond PCM1 and no ER pool.

## 7. Decision rule (fixed in advance)
- **Supported:** dropout rescued AND module-specific readout concordant (UPR panel / tunicamycin beyond PCM1) AND localisation compatible (ER pool) AND Tier-2 physical or epistatic support.
- **Refuted:** a dropout that is not rescued, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else. Report it as such and propose an alternative relationship type (for example surface-receptor homeostasis, type d).

## 8. Evidence ledger
Template B claims use the keys of Appendix A (T-keys here, M-keys in `reports/TM2D2.md` Appendix A.1; all verified = Y). Rows used: T2–T4, T8, T19, T21–T25, T32, T33, T38–T40, T44, M2, M10, M14, M16, M32–M34, M37, M38, M49, M51, M52, M74, M83.

## 9. Red-team review
Separate agent; asks what would make the experiment uninformative (off-target guides, proximity effects, lineage dependence, rescue failure, assay insensitivity). Appended unedited.
- Reviewer / model / date: pending
- Review text: pending
- PI response (separate): pending
