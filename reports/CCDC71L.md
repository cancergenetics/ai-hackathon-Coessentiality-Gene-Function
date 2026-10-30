# CCDC71L — candidate report (Template A) + experiment plan (Template B)

Prepared 2026-10-30. Numbers are copied from `reports/data/CCDC71L/bundle.md` (machine-generated from `results/ledger/*`) or are marked † where recomputed for this report (scripts and outputs in `results/m7/scratch_reports_ccdc71l/`). Every non-ledger statement about gene function carries a key from Appendix A.

Deviation from the template's file layout (recorded, not a rule change): DESIGN §6.5 places Template B in `reports/CCDC71L_experiments.md`; this assignment restricted writing to `reports/CCDC71L.md`, so Template B is included below as Part II. Content and required fields are unchanged.

---

# Part I — Template A

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** CCDC71L, a small, very basic coiled-coil protein with no annotated function, behaves across 1,361 CRISPR-screened cancer lines as if it worked in the **chromatin-silencing machinery** — its bias-corrected co-dependency neighbourhood is Polycomb-dominated (SUZ12, EED, BMI1, RING1, CBX4, CBX8, PHC3, MTF2) and also contains the HP1–SMCHD1–LRIF1 heterochromatin arm. It is **not** claimed to be a stable subunit of any of these complexes; the relationship type is **d, pathway member** ("functions in / supports epigenetic regulation of gene expression"). Unblinded literature adds one specific, testable refinement: CCDC71L carries a canonical **PxVxL motif at residues 223–227** †, the motif through which proteins dock on the HP1 chromo-shadow domain [A-C1, A-C3], and the single strongest orthogonal datum for this protein is structural — among the **364** Predictomes pairs containing CBX5/HP1α, CCDC71L has the **3rd-highest SPOC score (0.903)**, behind only SUV39H2 (0.910) and CBX1 (0.906) and ahead of CBX3 (0.889) and histone H3 (0.782), in a file where only 0.785% of 1,614,047 pairs exceed 0.9 †.
- **Confidence:** **p_cal = 0.0635** [95% CI 0.026–0.113] = the model-estimated probability that the *module term* (GO:0040029, epigenetic regulation of gene expression) is the term this gene later gains by direct-evidence GO annotation over a horizon like the hold-out's (≈8 years). It is a hit probability for the term only — not for the relationship type, and not a probability that the biology described above is true. Tier: none (filled by p_cal; no gene in this study reached Tier A or B).
- **Strongest reason to doubt (three parts, all material):** (i) **The neighbourhood exists only after bias correction.** In raw Chronos correlation CCDC71L's partners are weak — SUZ12 r = 0.120 (rank 250 of 18,433 in g's own correlation row), BMI1 0.107 (428), MEN1 0.093 (735), BAHD1 0.061 (2,263), LRIF1 0.040 (4,105), PHF19 0.022 (6,298); only SMCHD1 (0.206, rank 18) is near the top, and g's actual top raw correlates are a junk list (MAGEL2 0.333, TENM2 0.310, KRTAP1-3 0.307) †. What carries the call is split-half reproducibility (R = 0.272, p = 0.0050), not correlation amplitude. (ii) CCDC71L is 21.3% Arg+Lys with net charge +30 † and is already recovered as a prey of histone and centromere baits (CENPA, HIST1H2BG SaintScore 1.00; HIST1H3A 0.50; APEX1 0.49) †, so non-specific chromatin association is the **prior**, not a devil's advocate position. (iii) The term label is a minority outcome under perturbation: **2 of the 3 refits tried (lineage leave-out, K = 10) select GO:0001221 instead**, and the gene carries the lineage-leave-out demotion.
- **First experiment:** endogenous knock-in tagging of CCDC71L in KMS-20 and HCC-33, followed by IP-MS against a PxVxL-motif point mutant and a composition-matched scrambled bait, asking whether CCDC71L is chromatin-associated and HP1-bound and whether that depends on the motif; time ≈ 10–14 weeks; approximate cost ≈ US$35–50k (details in Part II). **Expect it to go against us as often as not:** the only admitted localisation source (HPA, Approved) calls Actin filaments / Golgi / Cytosol, and the L-class statistic is *below* null (0.313 vs 0.425, p 0.9990), so Falsification #1 (§9) is, on admitted evidence, more likely to fire than not.
- Cancer-line essentiality is not organismal function: dependency in DepMap lines says the gene is needed for proliferation there, not what it does in the organism.

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

- Symbol: **CCDC71L** | HGNC ID: **HGNC:26685** | previous symbols: **C7orf74**; alias: **FLJ36031** | UniProt: **Q8N9Z2** | band: **7q22.3**
- D1 / D2 / D3 values: **True / True (UniProt annotation score 2) / True** (D3_pubmed True, D3_tdark True; focused PMIDs 2, all PMIDs 22; TDL Tdark) | curation-lag audit flag: **not in the audit sample**
- Stratum (§1.4): family **other**; expression **expressed** (not lineage-restricted); informativeness tertile **high**; core **True** (headline stratum True; tool background True; low_coverage False)
- Hypothesis (one sentence): **CCDC71L functions in epigenetic regulation of gene expression (GO:0040029)**, in the chromatin-silencing neighbourhood shared by Polycomb complexes and the HP1–SMCHD1–LRIF1 heterochromatin arm.
- Relationship type: **d** — type unresolved by the §4.4 script rule and unresolved by the evidence: no admitted orthogonal class supports the call after Holm correction (§6), so a type-(a) subunit claim is not permitted; coupling and TF flags are negative, so type e is not assigned by rule (but see §8).
- Novelty class: **N2** (agent L; search date recorded in `results/m7/L/HGNC_26685.md`, which carries UniProt's 2026 release as its most recent source).
- LLM-recall-probe flag (§6.2): **not known** ("recognised: no; confidence: none; recalled function: 'unknown'"); probe answer logged at `results/m7/recall_probe_90.tsv`; matches network top term: **no**. The prediction is therefore not a restatement of the probe agent's background knowledge.
- Calibrated probability p_cal: **0.0635** [95% CI **0.026–0.113**, cluster bootstrap, 2,000 refits]; calibration family: **other**; covariates inside H's 5th–95th percentile: **yes** (support category `in_support`).
- Tier: **none (p_cal fill)**; rank in primary top 40: **16**. Top-40-only label: **demoted — lineage_leaveout**.

**What p_cal means here (exact).** The calibration model was fitted on the temporal hold-out H (820 genes; primary H = 809), where t0 = GO 2018-07-02 and the outcome is "the top reportable V2 term is among the terms the gene gained by D1-evidence annotation between t0 and the current release" (`results/holdout_eval/SUMMARY.md`). On H the observed rate of that event was **0.030** (95% CI 0.018–0.043) against 0.000 for prior-only and 0.005 for the matched-gene null; out-of-fold calibration gave slope 0.819 (Wald 0.512–1.127), intercept −0.006 (Wald −0.437–+0.426), Brier 0.0294, c-statistic 0.855, and the pre-registered poor-calibration rule was not met. So p_cal = 0.0635 means: *in a world like H, about 6 such predictions in 100 would later be confirmed by curators as a direct-evidence annotation to that term over roughly an 8-year horizon.* It does not cover the relationship type, the HP1 refinement, or any partner-level claim. The M6 caveat applies: with an H hit rate of 3% and the frozen covariates, no U gene could exceed p_cal 0.141 (`results/ledger/M6_SUMMARY.md`).

## 2. The protein

- Domains (InterPro **IPR026695**; Pfam **PF15374**); UniProt "Coiled-coil domain-containing protein 71L", 235 aa; **no** transmembrane, signal-peptide or transit-peptide keyword; no domain features annotated; UniProt Function [CC], Subcellular location [CC] and Sequence similarities are all empty. Protein existence: evidence at protein level; annotation score 2.0.
- AlphaFold (AFDB v6, Q8N9Z2): mean pLDDT **60.0**, 34% of residues > 70 † — mostly low-confidence/disordered, consistent with a coiled-coil plus long low-complexity stretches.
- Composition † (recomputed from the UniProt canonical sequence): **21.3% Arg+Lys, 8.5% Asp+Glu, 12.8% Pro, net charge +30**; residues ~120–160 are an Arg/Pro-rich block (`ARRPVPRAAARRRRRGARAAAARRRKPRPPPPPPPPP`). One canonical **PxVxL** motif, residues **223–227 (PMVRL)**, and no other PxVxL in the sequence †.
- Class H (homology) evidence: **no IBA/ISO annotation of g to the predicted term** (support.tsv homology field) — the homology class contributes nothing here. A porcine orthologue (named FLJ36031/pFLJ) has been studied functionally [A-C7], but in adipocyte biology, not chromatin.
- Source keys: A-C1, A-C3, A-C7 (all in Appendix A); protein features from `reports/data/CCDC71L/bundle.md` §8; composition, pLDDT and motif position are † recomputations in `results/m7/scratch_reports_ccdc71l/`.

## 3. Dependency profile

- Mean / SD of Chronos effect: **−0.063 / 0.154**; median −0.057; 5th percentile −0.316; min −1.176; fraction of lines < −0.5: **0.0096 (13 of 1,361)**; status: **selective, not common-essential**; NaN fraction **0.0000**.
- Expression: log2(TPM+1) ≥ 1 in **97.2%** of lines (≥ 2 in 91.4%); median 3.72. Dependency-vs-expression coupling: Spearman ρ = **0.000** (n = 1,292) — no coupling flag. Scatter: panel (b) of `reports/data/CCDC71L/fig_profile.png`.
- Lineage enrichment (descriptive, lineages with ≥ 10 lines): Bladder/Urinary Tract n = 34, mean −0.111, MW p 0.0879; Peripheral Nervous System n = 47, mean −0.097, p 0.4265; Ovary/Fallopian Tube n = 62, mean −0.095, p 0.0273. No lineage reaches a corrected threshold, but see §5 — removing the first of these changes the top term.
- Split-half assessability: **R(g) = 0.272**; null mean 0.002, max 0.096 over 200 matched genes; empirical p = **0.0050**; RBO R = 0.278, p 0.0050 → **assessable: yes**. The neighbourhood is reproducible even though the dependency amplitude is small.

**Raw co-dependency magnitudes (†, disclosed in full).** The reported neighbourhood is produced by the `zavg_BEF` bias correction, which is what the method is for; in *raw* pairwise-complete Pearson correlation of Chronos profiles (n = 1,361 lines, 18,433 genes in g's row) the same partners are weak:

| partner | role in the call | raw r | rank in g's correlation row |
|---|---|---|---|
| SMCHD1 | supporting partner, top-10 | **0.206** | **18** |
| EED | top-10 | 0.128 | 182 |
| SUZ12 | rank-1 partner (zavg 13.80) | **0.120** | **250** |
| BMI1 | supporting partner, top-10 | 0.107 | 428 |
| MEN1 | supporting partner | 0.093 | 735 |
| BAHD1 | supporting partner | 0.061 | 2,263 |
| LRIF1 | supporting partner | **0.040** | 4,105 |
| PHF19 | supporting partner | **0.022** | 6,298 |
| CBX1 / CBX5 / CBX3 (HP1) | *not* in N(g) | −0.105 / −0.014 / −0.010 | 18,197 / 11,517 / 10,887 |

g's top raw correlates are MAGEL2 0.333, TENM2 0.310, KRTAP1-3 0.307, SRSF8 0.295, GPHB5 0.293 — the low-variance junk that dominates an uncorrected correlation row. **Stated plainly: four of the six supporting partners that Part II proposes to test have raw co-dependency of 0.02–0.11, and the HP1 proteins have none at all; the signal exists only post-correction, and what licenses it is the split-half reproducibility above, not the size of any correlation.** (For contrast, the companion report's gene PLEKHH3 has its two top partners as the #1 and #2 raw correlates genome-wide — this gene is not in that position.) Lineage-demeaning the profiles leaves the partner correlations essentially unchanged (SUZ12 0.120 → 0.108; SMCHD1 0.206 → 0.203; EED 0.128 → 0.116) †, so a lineage covariate is not what produces them.
- Figure 1 (profile panel): `reports/data/CCDC71L/fig_profile.png` — (a) CCDC71L effect vs SUZ12 effect across lines, five most dependent lineages coloured; (b) effect vs own expression; chosen lines circled (D1, D2), control squared (C).

## 4. Neighbourhood

Top-10 partners (zavg_BEF; GLS rank = rank in g's GLS row after §3.1 exclusions; in_term = annotated to GO:0040029):

| partner | zavg_BEF | z_B/z_E/z_F | GLS rank | in_term | partner mean eff | frac < −0.5 | CE | band | same chr | paralogue | hub (in-degree) | hu.MAP-train | partner function (top GO annotations, ledger) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SUZ12 | 13.80 | 24.6/13.8/3.0 | 1079 | no | −0.35 | 0.287 | no | 17q11.2 | no | no | **69 HUB** | no / pair no | H3K9me2/3 reader activity; transcription corepressor binding |
| EED | 12.59 | 19.6/14.0/4.2 | 46 | no | −0.32 | 0.263 | no | 11q14.2 | no | no | **69 HUB** | no / pair no | transcription corepressor binding; transcription coregulator binding |
| BMI1 | 11.51 | 17.0/13.9/3.6 | 13 | **yes** | 0.06 | 0.014 | no | 10p12.2 | no | other partner | 49 | no / pair no | segmentation; positive regulation of ubiquitin-protein transferase activity |
| CBX4 | 11.17 | 17.2/13.3/3.0 | 174 | no | −0.05 | 0.005 | no | 17q25.3 | no | other partner | 41 | no / pair no | SUMO ligase activity; SUMO binding |
| SMCHD1 | 10.71 | 11.7/13.6/6.8 | 1 | **yes** | −0.11 | 0.063 | no | 18p11.32 | no | no | 41 | no / pair no | sex-chromosome dosage compensation; dosage compensation by inactivation of X |
| RING1 | 9.98 | 16.4/11.2/2.4 | 2079 | no | −0.17 | 0.033 | no | 6p21.32 | no | other partner | 43 | no / pair no | — |
| PHC3 | 9.67 | 15.2/11.2/2.6 | 249 | no | 0.09 | 0.003 | no | 3q26.2 | no | no | 47 | no / pair no | — (itself a U gene, primary top-40 rank 3) |
| MTF2 | 8.02 | 13.8/9.0/1.3 | 3676 | no | −0.08 | 0.018 | no | 1p22.1 | no | other partner | 41 | no / pair no | transcription corepressor / coregulator binding |
| CBX8 | 7.22 | 11.4/8.1/2.1 | 822 | no | 0.10 | 0.002 | no | 17q25.3 | no | other partner | 34 | no / pair no | H3K27me3 reader activity; histone H3 reader activity |
| CDYL | 7.15 | 8.1/9.5/3.9 | 62 | no | −0.08 | 0.015 | no | 6p25.1 | no | no | 36 | no / pair no | 3-hydroxyacyl-CoA dehydratase / enoyl-CoA hydratase activity |

The **six supporting partners** for the called term (j ∈ N(g) ∩ term with z > 0) are **BMI1, SMCHD1, LRIF1, PHF19, MEN1, BAHD1** (`results/ledger/u_flag_partners.tsv`); LRIF1, PHF19, MEN1 and BAHD1 sit in N(g) (K = 25) outside the top 10. None is flagged for locus, copy-number or hub status.

- Figure 2 (neighbourhood network): `reports/data/CCDC71L/fig_network.png` — g, its top-10 partners, and the 54 edges with zavg_BEF ≥ 3 among the 11 nodes; 17 of those edges have physical support in an admitted P source (SUZ12–EED, SUZ12–BMI1, SUZ12–MTF2, SUZ12–CDYL, EED–BMI1, EED–RING1, EED–MTF2, BMI1–CBX4, BMI1–RING1, BMI1–PHC3, BMI1–CBX8, CBX4–RING1, CBX4–PHC3, CBX4–CBX8, RING1–PHC3, RING1–CBX8, PHC3–CBX8). **None of those physical edges involves CCDC71L itself** — the partners form a real complex network into which CCDC71L is wired only by co-dependency.

Top 3 terms (R1; p_emp from the matched-gene null †; hypergeometric p descriptive):

| rank | term | name | S | n_sup | size | p_hyper | p_emp † | LOPO rank kept † |
|---|---|---|---|---|---|---|---|---|
| 1 | GO:0040029 | epigenetic regulation of gene expression | 45.407 | 6 | 143 | 0.0000 | 0.0020 | 3/6 |
| 2 | GO:0045814 | negative regulation of gene expression, epigenetic | 39.789 | 5 | 78 | 0.0000 | 0.0040 | 0/5 |
| 3 | GO:0001221 | transcription coregulator binding | 39.404 | 4 | 101 | 0.0000 | 0.0020 | 2/4 |

- Second-ranked term: **GO:0045814 negative regulation of gene expression, epigenetic** (also the most specific term in the top 5). The top 5 is closed under one theme: epigenetic silencing, corepressor binding and H3 reader activity (GO:0001222, GO:0140006 complete it).
- Leave-one-partner-out: the top term keeps R1 after 3 of 6 single supporting-partner removals; the second-ranked term keeps rank after 0 of 5. The *theme* is stable; the exact GO label is not (see §5).
- V1 / V1′ module label: **GO:0031519 PcG protein complex** (10 supporting partners) — descriptive only; p_cal does not attach to it.

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | **pass** | g arm 7q; 0 of the top-10 partners on chromosome 7. The one paralogue in the matrix (CCDC71, confirmed from `data/derived/paralogues_by_matrix_index.npz` †) is excluded by construction — and independently shows **no** co-dependency with CCDC71L (Pearson r = −0.017 over 1,361 lines †), so the signal is not paralogue bleed-through. |
| Bidirectional-promoter / overlapping / readthrough partners | **pass** | 0 of 6 supporting partners flagged (strand-agnostic superset rule, DEVIATIONS 2026-10-29). |
| Copy-number co-amplification | **pass** | 0 of 6 flagged; BMI1 r = 0.01, SMCHD1 0.03, LRIF1 0.05, PHF19 0.01, MEN1 −0.03, BAHD1 0.01. |
| Hub-driven call (> 50% of S from top-1% in-degree) | **pass** | hub share 0.00; 0 hub partners among the supporting partners (SUZ12 and EED are hubs but are **not** supporting partners for this term). |
| **Lineage leave-out** | **FAIL** | Removing Bladder/Urinary Tract (34 lines; mean effect −0.111) and refitting the tool gives top term **GO:0001221 transcription coregulator binding**, not GO:0040029; N(g) overlap after refit 0.80. This is the gene's top-40 demotion label. |
| **K = 10 / 50** | **K = 10 FAIL / K = 50 pass** | K = 10 top term GO:0001221 transcription coregulator binding †; K = 50 top term GO:0040029 †; GLS network (K = 25) top term GO:0040029 †. |
| Dependency vs own expression; TF / lineage-marker enrichment | **pass** | ρ = 0.000 (n = 1,292); TFs in N(g) = 2, OR 1.07, p 0.5719, q 1.0000. |
| TP53 / p53-axis correlation | **pass** | 902 mutant vs 459 WT; p 0.1808, q 0.3803; median difference −0.007. |
| DEMETER2 replication | **not measured** | 0 supporting partners present in DEMETER2 — no flag, and no replication either. |
| Shared-sgRNA and per-guide check | not possible (guide maps / guide-level data not available) | recorded |

**Honest reading of the failures.** What flips is the rank order between **GO:0040029 "epigenetic regulation of gene expression" (biological_process, 143 genes, 6 supporting partners) and GO:0001221 "transcription coregulator binding" (molecular_function, 101 genes, 4 supporting partners)**, on a margin of ~6 S-units out of 45. These two terms are **not** nested and cannot be: they sit in different GO ontologies (`namespace: biological_process`, `is_a` GO:0006338/GO:0010468, vs `namespace: molecular_function`, `is_a` GO:0008134; `data/raw/go/current/go-basic.obo` †). (The *rank-2* term GO:0045814 **is** a true descendant of GO:0040029 — an earlier draft of this report transferred that relationship onto the wrong pair.) The distinction matters: a coregulator-*binding* MF term is a binding assertion that under DESIGN §4.4 would point toward the physical/type-a claim this report explicitly says it is not entitled to make, whereas the called BP term licenses "acts in pathway M". Flipping between them is not cosmetic relabelling.

Nor is this "one failure seen twice": **of the three perturbations tried, two (Bladder/Urinary Tract removal; K = 10) select GO:0001221, and only K = 50 and the GLS K = 25 network retain GO:0040029.** The called label is the minority outcome. What does *not* change is the neighbourhood itself: after removing the 34 Bladder lines the raw partner correlations move by ≤ 0.005 in every case (SUZ12 0.120 → 0.119; EED 0.128 → 0.130; SMCHD1 0.206 → 0.205; LRIF1 0.040 → 0.044; BMI1 0.107 → 0.109; MEN1 0.093 → 0.093; BAHD1 0.061 → 0.057; PHF19 0.022 → 0.025) †, and N(g) overlap is 0.80. Every alternative top term in every refit is a chromatin-silencing or corepressor term. I therefore report the call at the level the data support — the **module family** (chromatin silencing) — and treat the specific identifier GO:0040029 as **not robust**, which is also the strict pre-registered reading.

## 6. Orthogonal evidence matrix (four states: not measured / no support / supports / contradicts)

Class p = Simes within class; Holm across the 4 measured classes at α = 0.05. **No class supports the call**; there is no contradiction.

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | P_group (BioPlex 3.0 / STRING-exp / BioGRID-LTP / OpenCell), HCM SAINT | **no support** | g has 0 edges to any of the 10 co-essential partners in any admitted P source. g's own edges: BioPlex3 degree 6 (CBX3\*, CHCHD2, H2AB3, NEUROG3, NHLH2, TNFSF12); STRING-exp degree 6 (CBX3\*, LRIF1\*, ADNP, CHAMP1, NEUROG3, POGZ); HCM-SAINT degree 4 (CBX3\*, CENPA, HIST1H2BG/H2BC8, **ZNF330** — the bundle's "NOAZFP" is the file's `ZNF330_target` bait label, alias NOA36, not a gene symbol †). \* = annotated to the predicted term. 2 of 143 term members are edges (P_group p 0.0150; HCM_SAINT p 0.0440 → Simes 0.0300) | 0.0300 raw → **0.120 Holm** | family "other" → any class is diagnostic; diagnostic class measured = True, supports = False |
| A co-abundance | CCLE proteomics (ProteomeHD: g not measured) | **no support** | mean member row percentile 0.530 vs null 0.489. Best partner pairs: SMCHD1 r 0.39 (100th percentile of g's row), CDYL 0.24 (98th), EED 0.13 (83rd), SUZ12 0.08 (71st) | 0.0539 → 0.162 Holm | yes (any) |
| L localisation | HPA v25.1 (admitted); OpenCell / Human Cell Map / MitoCarta for contradiction only | **no support** | fraction of members sharing a compartment with g 0.313 vs null 0.425 — *below* null. HPA (Approved): Actin filaments, Golgi apparatus, Cytosol. Human Cell Map (prey, not bait): chromatin (NMF), chromatin + nucleoplasm (SAFE). Term compartment: nucleus; g scored multi-localised | 0.9990 → 0.999 Holm | yes (any) |
| G perturbation phenotype | Perturb-seq K562 genome-wide (K562-essential and RPE1-essential: g not measured) | **no support** | mean member percentile 0.526 vs null 0.502. Best partner pairs: SMCHD1 r 0.06 (98th), CDYL 0.06 (98th), EED 0.03 (88th), SUZ12 0.03 (86th) | 0.1758 → 0.352 Holm | yes (any) |
| S structure | Burke 2023 AF2 | **not measured** | g not modelled | — | yes (any) |
| H homology | orthologue IBA/ISO | reported only | no IBA/ISO annotation of g to the term | reported only | — |

Reported but not counted (per DESIGN §5.1): **hu.MAP 3.0** — CCDC71L is a member of **8** hu.MAP3.0 complexes †, one of which (huMAP3_11539.1, 33 subunits, ComplexConfidence field = 6; the direction of that scale is not asserted here) contains **CBX1, CBX3, CBX5, ATRX, SUV39H2, EHMT1, EHMT2, ADNP, POGZ, CHAF1A/B, MAD2L2**; the four smallest (huMAP3_00567.1, 01455.1, 01516.1, 01776.1; confidence field 1) pair CCDC71L with H2AB2/H2AB3, ZNF275, ZNF335, NEUROG2/3 and CSRP2 †; its non-independent all-PPI degree is 63, of which 6 are term members (ATRX, CBX1, CBX3, CBX5, SUV39H2, ZNF335). **Predictomes / Schmid 2025** — CCDC71L appears in 38 scored pairs †. Its highest SPOC scores are with the three HP1 proteins: **CBX5 0.903, CBX1 0.734, CBX3 0.683** (KIRC 0.332 / 0.254 / 0.638) †. The informative framing is the reciprocal one: among the **364 Predictomes pairs that contain CBX5**, CCDC71L ranks **3rd by SPOC**, behind SUV39H2 (0.910) and CBX1 (0.906) and ahead of CBX3 (0.889) and histone H3 (0.782), with the paralogue CCDC71 6th (0.820); across the whole file only **0.785%** of 1,614,047 pairs exceed SPOC 0.9 †. **The omitted negative, reported here: CCDC71L–LRIF1 SPOC = 0.000 (KIRC 0.330)** † — the only Predictomes pair between g and one of its *supporting partners* is negative, and LRIF1 is named in §0/§7 and slated for IP-MS and epistasis in Part II. "Absence of an interaction is never a contradiction" (§5.3) applies, but selective presentation of the same table does not; both values stand together. SPOC is a trained classifier that "effectively separates true and false AF-M predictions of PPIs" [A-C13]. **DEMETER2** — not measured.

**Independence: what these sources do and do not add.** Three cautions, all of which cut against an earlier, stronger version of this section:

1. **SPOC is not independent of co-essentiality or of BioGRID.** Its own paper states the classifier was given "genome-wide features of each protein pair that were external to AlphaFold, including co-dependency data from DEPMAP" and "high throughput interaction experiments from the BioGRID database" [A-C21], and reports that "among biological features, it was the number of independent experiments supporting an interaction in the BioGRID database (21%)" that mattered most [A-C22]. A SPOC score therefore already contains DepMap co-dependency and BioGRID PPI evidence; it cannot be counted as an independent third data type.
2. **The "three P sources" are not three independent experiments.** STRING's experimental channel aggregates IMEx/BioGRID records, which include the BioPlex and Human Cell Map datasets that are the other two sources. CBX3 appearing in all three admitted P sources may be one or two primary experiments counted three times. The §6 statistic inherits this (P_group p 0.0150, HCM_SAINT p 0.0440, Simes 0.0300) — the class fails Holm in any case, so nothing downstream depends on it.
3. **The co-dependency data do not point at HP1 at all.** r(CCDC71L, CBX5) = −0.014, r(CBX1) = −0.105, r(CBX3) = −0.010 †, and no HP1-family protein is in N(g) at K = 25 (SUZ12, EED, BMI1, CBX4, SMCHD1, RING1, PHC3, MTF2, CBX8, CDYL, AEBP2, PSIP1, CRAMP1, LRIF1, PCGF1, UBE2E1, DOT1L, UBR7, PHF19, FCRL6, MEN1, BAHD1, CHD8, PPIL1, EHMT1) †.

**Where the orthogonal data actually point.** The co-essentiality neighbourhood is **Polycomb-dominated and contains no HP1 protein**. The HP1 arm enters this report by two other routes only: (a) the physical sources (CBX3 in BioPlex/STRING-exp/HCM-SAINT, with the non-independence caveat above; LRIF1 in STRING-exp) and (b) the structural SPOC scores, which are themselves partly DepMap/BioGRID-derived. SMCHD1 is g's best co-abundance and best Perturb-seq partner, and SMCHD1–LRIF1 is the one route by which the co-dependency data touch the HP1 axis at all. Both arms live inside GO:0040029, so the called term survives either reading; the mechanistic refinement is HP1-directed, and it rests on the physical/structural evidence, **not** on convergence of independent data types.

## 7. Literature (blinded step, then synthesis)

**Blinded summary of agent L's evidence items** (`results/m7/L/HGNC_26685.md`; 7 items; search terms CCDC71L; C7orf74; FLJ36031; Q8N9Z2; plus a DepMap/co-essentiality query):

| # | claim | level | DepMap-derived |
|---|---|---|---|
| 1 | UniProt carries no function/location annotation | mention | no |
| 2 | Porcine orthologue FLJ36031 is a positive regulator of fat deposition in cultured intramuscular adipocytes | **functional** | no |
| 3 | CCDC71L is downstream of a LINC00514/miR ceRNA axis; its overexpression rescues TNBC proliferation/migration | **functional** | no |
| 4 | Upregulated in HNSCC; prognostic marker tied to lipid metabolism and immune infiltration (bioinformatic) | mention | no |
| 5 | GWAS locus (CCDC71L-PIK3CG) for platelet count | mention | no |
| 6 | 3'UTR variant rs2286149 near PIK3CG associated with carotid intima-media thickness | mention | no |
| 7 | Pig skeletal-muscle expression linked to lipid-metabolism genes | mention | no |

L's own summary: no biochemical mechanism, partners or localisation are known. Novelty class **N2**.

**Blinded verdicts** (`results/m7/judge/`; packet J079; statements carried the V2 term + V1′ label only, relationship type omitted per DEVIATIONS 2026-10-30):

- Real statement (slot A, "functions in epigenetic regulation of gene expression; module context: PcG protein complex"): **0 (unaddressed)** from both judges. J1: "Row 1: no functional annotation; no Polycomb evidence." J2: "Rows 1-7: no Polycomb/epigenetic evidence."
- Decoys (slots B, C, D — sodium ion transmembrane transporter activity; carboxylic acid transmembrane transporter activity; tRNA metabolic process): **0, 0, 0** from both judges.
- Judges J1, J2; adjudicator not required (no disagreement on this packet). Overall κ for the judging run = 0.975 over 360 statements; d (real − mean decoy) for this gene = **0.000**.

So the blinded step is **neutral**: the published record as agent L assembled it neither supports nor contradicts the call. Within the primary top 40 the real statements beat decoys overall (18/40 real supported vs 3/120 decoys, exact sign-flip p = 0.0002174), but that signal came almost entirely from N1 genes (16 of 31); the two N3 genes and 5 of 7 N2 genes, this one included, were unaddressed.

**Unblinded synthesis** (every sentence carries an Appendix-A key):

CCDC71L carries one canonical PxVxL sequence [A-C1], the motif that docks proteins into the HP1 chromo-shadow domain and whose presence in partner proteins is required for HP1β to reach heterochromatin [A-C3]. The one paper that notices this is about the *paralogue* CCDC71, whose BioID shows a strong association with HP1 isoforms that the authors attribute to PxVxL-like motifs "and/or through further associations with the related CCDC71L protein" [A-C2] — i.e. CCDC71L's HP1 connection has been *hypothesised in print, never tested*. Two of CCDC71L's six supporting partners belong to a defined HP1-linked silencing pathway: SMCHD1's chromatin binding genome-wide depends on LRIF1, which bridges it to H3K9me2/3 nucleosomes [A-C4], and depletion of LRIF1 (HBiX1) or SMCHD1 — but not of PRC2 — decompacts the inactive X [A-C5]. The remaining supporting partners (BMI1, PHF19) and the dominant top-10 partners sit in the Polycomb system, where PRC1 deposits H2AK119ub1 and PRC2 deposits H3K27 methylation [A-C6]; those two marks give the module its assayable readouts (Part II §5). Outside chromatin, the published record on CCDC71L is about lipid and tumour phenotypes: a porcine orthologue is a positive regulator of fat deposition in cultured intramuscular adipocytes [A-C7]; overexpression rescues the anti-tumour effect of LINC00514 knockdown in TNBC cells [A-C8]; it is described as acting in cellular lipid metabolism in an HNSCC prognostic analysis [A-C9]; and its locus is a GWAS signal for platelet count [A-C10] and carotid intima-media thickness [A-C11], in both cases as the neighbour of PIK3CG, which makes those signals locus-level, not protein-level. A pig muscle RNA-seq study groups it with lipid-metabolism genes [A-C12]. **A chromatin or HP1 function for CCDC71L itself was not found in the literature as of the 2026-10 searches reported here.**

**Closest prior publication and what co-essentiality adds.** The closest is the ATRX BioID study [A-C1, A-C2]: it reports a canonical PxVxL motif in CCDC71L and speculates that CCDC71L may mediate CCDC71's HP1 association — a sequence observation and a hypothesis, with no experiment on CCDC71L. Co-essentiality adds an orthogonal, genome-scale argument that CCDC71L's *fitness requirement* tracks the chromatin-silencing machinery across 1,361 lines (R = 0.272, empirical p 0.0050), and it names a specific partner set (BMI1, SMCHD1, LRIF1, PHF19, MEN1, BAHD1) that a targeted experiment can test. It also sharpens the reading: the physical/structural hints [A-C13, §6] favour the HP1 arm (CBX5/CBX1/CBX3) over the PcG core that dominates the co-dependency ranking.

**Important procedural note — the blinded step for this gene is uninformative, not neutral.** The ATRX/PxVxL item [A-C1, A-C2] is a full-text Europe PMC hit for the query `"CCDC71L"`, yet it is absent from agent L's blinded evidence set (`results/m7/L/HGNC_26685.md`, 7 items, search terms including `CCDC71L`). It was therefore never available to the judges. Both the **N2 class** and the judges' verdict (**real 0, decoys 0, d = 0.000**) rest on an evidence set that demonstrably missed the single most relevant paper for this gene. The correct reading is not "the literature neither supports nor contradicts the call" but "**the blinded evidence set was incomplete, so the blinded step cannot speak to this call either way**". The pre-registered statistic is reported above exactly as scored and is not revised; the item is disclosed here as what it is — the most informative literature item for this gene, retrieved only after unblinding.

**Prior prediction lists containing this gene.** Wainberg 2021 [A-C15]: the 108-gene prediction list is not held locally and only the abstract could be retrieved (which names TMEM189 and C15orf57); membership cannot be verified either way — recorded as *not verifiable*. hu.MAP 3.0 [A-C14]: **yes**, CCDC71L is placed in 8 complexes, including one HP1/H3K9-methyltransferase complex (§6) — but the co-essentiality tool's hyper-parameters were tuned on hu.MAP 3.0 train pairs (LITERATURE.md), so this is agreement, not independent confirmation; CCDC71L is not itself a hu.MAP-train gene and no g–partner pair is a training positive. Replogle 2022 [A-C16]: CCDC71L is measured in the K562 genome-wide Perturb-seq screen (§6) but the string "CCDC71L" does not occur in the retrieved full text †, so it is not among that paper's function assignments. Predictomes [A-C13, A-C19]: CCDC71L appears in the scored pair set (38 pairs) with high SPOC scores to CBX5/CBX1/CBX3 †.

**Post-freeze (after 2026-10-29) papers confirming the prediction:** none found.

## 8. Alternative explanations

For each §5 artefact, the evidence against it:

- *Same-arm / paralogue / guide bleed-through.* Excluded by construction, and independently: the single matrix paralogue CCDC71 does not co-vary with CCDC71L (r = −0.017) †.
- *Locus and copy-number artefacts.* 0 of 6 supporting partners flagged; CN correlations ≤ 0.05.
- *Hub-driven call.* Hub share 0.00. The two hub partners (SUZ12, EED, in-degree 69) contribute to the ranking of the *theme* but not to S for this term.
- *Lineage-driven dependency (type e).* Coupling ρ = 0.000; TF enrichment OR 1.07 (p 0.5719); no lineage reaches a corrected threshold. The rule therefore does not assign type e. **But** the lineage leave-out failure shows the label is sensitive to 34 of 1,361 lines, which is the signature of a weak, distributed signal rather than a robust one; a reader who weights that failure heavily should treat the call as "chromatin-silencing neighbourhood" rather than as a specific term.
- *Curation lag / rediscovery.* Not in the audit sample; the recall probe did not recognise the gene; agent L found no chromatin literature. Rediscovery is unlikely, which is also why there is no external check.

**Strongest competing biological hypotheses.**

1. **Non-specific chromatin stickiness — this is the prior, not a devil's-advocate position.** CCDC71L is 21.3% Arg+Lys with net charge +30 and 12.8% proline †, and it is **already observed behaving as a generic basic chromatin prey**: in the Human Cell Map it is recovered from the baits CENPA (SaintScore 1.00), HIST1H2BG (1.00), HIST1H3A (0.50) and APEX1 (0.49) as well as CBX3 (1.00) †; its BioPlex/HCM partners include histones (H2AB3, H2BC8) and several bHLH transcription factors (NEUROG2/3, NHLH2, BHLHA15). A 235-aa, 21%-basic, net +30 protein appearing in histone and centromere pulldowns is the textbook profile of an affinity-proteomics artefact. Under this hypothesis both the physical hints and the co-dependency (shared sensitivity of any chromatin-tethered protein to chromatin-state perturbation) arise without CCDC71L having a defined role. **The report's position is that this explanation must be excluded before the HP1 refinement is believed, not that it is unlikely.** **Separated by:** Part II Tier-1 localisation + Tier-2 IP-MS *with the PxVxL point mutant and the named composition-matched scrambled bait* — a stickiness explanation predicts that the interactome is unchanged by a 3-residue motif mutation and that the scrambled bait recovers a similar histone set, whereas a genuine HP1 interaction predicts motif-dependent loss of CBX1/3/5 against an otherwise retained interactome.
2. **HP1-arm membership rather than Polycomb membership.** The independent data (§6) favour HP1/SMCHD1–LRIF1 over PRC1/PRC2. Both are inside the called term, so this does not change the term, but it changes every mechanistic prediction and the choice of readout. **Separated by:** CUT&RUN co-occupancy with H3K9me3 vs H2AK119ub1/H3K27me3 after knock-in tagging (Part II §5–6).
3. **Regulatory co-dependency (type e) at the level of chromatin state rather than pathway membership.** CCDC71L's own expression does not predict its dependency (ρ = 0.000), which argues against the standard type-e pattern, but a shared upstream chromatin-state covariate across lines cannot be excluded from DepMap alone. **Separated by:** the essential-gene confound control in Part II Tier 1 (matched-essentiality control gene KLHDC3) plus the module-specific readout: a type-e explanation predicts no module-specific chromatin change at matched growth effect.
4. **Supplier/client (type c) or assembly factor (type b).** No enzymatic or transport keyword, no TM helices, no assembly term among the partners — neither type is supported by any evidence; recorded as not assigned rather than excluded.

## 9. Falsifying observations (written before §6 and §7 were read)

1. **Localisation.** If endogenously tagged CCDC71L (knock-in, both dependent lines) is not nuclear/chromatin-associated — for example if it is confined to Golgi and actin structures, as the HPA Approved call would suggest — then "epigenetic regulation of gene expression" is the wrong module and the call is refuted.
2. **Module readout.** If acute depletion of CCDC71L (degron or CRISPRi, time-matched to partner depletion) changes none of the module's readouts — global and locus-level H2AK119ub1, H3K27me3 and H3K9me3; derepression of Polycomb/HP1 target genes — beyond what a matched-essentiality control gene from an unrelated module produces at the same growth effect, the call is refuted.
3. **Genetic placement.** If CCDC71L knockout in the two dependent lines shows no epistatic relationship with BMI1/SMCHD1/LRIF1 depletion (fully additive growth effects and independent transcriptional signatures), the "pathway member" relationship type is refuted even if some chromatin association exists.
4. **Motif (refinement only).** If the PxVxL mutant behaves identically to wild type in every assay and no HP1 isoform is recovered by IP-MS, the HP1 refinement is refuted — this does **not** by itself refute the module call, which could still run through the Polycomb arm.

## 10. Experiments

See **Part II** below (Template B; DESIGN §6.5 names `reports/CCDC71L_experiments.md`, see the note at the top of this file).

## 11. Novelty and external benchmarks

- **Wainberg 2021** [A-C15]: agreement not verifiable (list not held locally; only the abstract retrievable).
- **hu.MAP 3.0** [A-C14]: agreement — CCDC71L is placed in 8 complexes, one of them with CBX1/CBX3/CBX5/ATRX/SUV39H2/EHMT1/EHMT2 †. This is partly non-independent (the tool was tuned on hu.MAP 3.0 train pairs) and is reported as agreement only.
- **Replogle 2022** [A-C16]: measured, not assigned a function.
- **Predictomes / Schmid 2025** [A-C13, A-C19]: scored pairs exist; highest SPOC scores to CBX5/CBX1/CBX3 †.

**What is new here.** Two things, both modest. First, a genome-scale *fitness* argument placing CCDC71L in the chromatin-silencing neighbourhood, with a named, testable partner set (BMI1, SMCHD1, LRIF1, PHF19, MEN1, BAHD1) — this is not in the literature as of 2026-10, though §3 shows the raw correlations behind it are small and the term label is not robust. Second — and stated precisely, because an earlier draft overclaimed it — **not** a convergence of independent data types: SPOC is itself trained on DepMap co-dependency and BioGRID interactions [A-C21, A-C22], STRING-exp aggregates BioPlex/HCM, and the co-dependency data contain no HP1 protein at all (§6). The defensible new observation is narrower and still worth an experiment: **CCDC71L is the 3rd-highest-scoring SPOC partner of CBX5 among 364 scored CBX5 pairs (0.903), ahead of CBX3 and histone H3, with the paralogue CCDC71 6th — while the one Predictomes pair between CCDC71L and a supporting partner, LRIF1, scores 0.000** †. That turns a published *speculation* [A-C2] into a specific, falsifiable experiment. What is **not** new: the existence of a PxVxL motif in CCDC71L, which is already in print [A-C1].

---

# Part II — Template B: experiment plan

Rules (DESIGN §6.5): one decisive, falsifiable experiment; expected readouts for both "right" and "wrong"; cell lines chosen by rule; essential-gene confound control; DepMap screen medium as baseline; sequence-level guide off-target check.

## 1. Context

- Gene: **CCDC71L** | hypothesis: CCDC71L functions in / supports epigenetic regulation of gene expression (GO:0040029), most specifically in the HP1–SMCHD1–LRIF1 silencing arm | relationship type: **d** | novelty class: **N2**
- LLM-recall-probe flag: **not known** | calibrated probability: **p_cal 0.0635** (family "other") | tier: **none (p_cal fill)**; primary top-40 rank 16; demotion label: lineage_leaveout
- Strongest alternative explanation: non-specific chromatin association by a highly basic, low-complexity protein (21.3% R+K, net +30 †), producing both the physical hints and a shared sensitivity to chromatin-state perturbation without pathway membership.
- **Decisive experiment (one sentence):** knock an endogenous mNeonGreen–HaloTag–3×FLAG cassette into *CCDC71L* in KMS-20 and HCC-33, and ask — in the same cells, against an isogenic PxVxL point mutant (P223A/V225A/L227A) and the named composition-scrambled bait scCCDC71L (§3) — whether CCDC71L is chromatin-associated, co-purifies HP1 isoforms (CBX1/CBX3/CBX5) and co-occupies H3K9me3 domains, with the motif mutation as the internal specificity control.
- Falsifying observation (copied from Template A §9, item 1): if endogenously tagged CCDC71L is not nuclear/chromatin-associated in either dependent line, the module call is refuted.

## 2. Cell lines (selection rule)

Rule applied (bundle §10; rank-1 partner **SUZ12** used for the partner criterion; strict rule, no relaxation needed): g ≤ −0.5, partner ≤ −0.3, g expressed log2(TPM+1) ≥ 2, locus not amplified (relative CN < 1.5), high screen quality, TP53-mutant preferred, second line from another lineage. Funnel: 1,361 lines → 13 with g ≤ −0.5 → 10 adding the partner criterion → 10 adding expression → 6 after the amplification filter.

**Two dependent lines:**

| ModelID | name | lineage / disease | g effect | SUZ12 effect | g expr (log2 TPM+1) | g CN | TP53 | ScreenNNMD / ROCAUC | medium (DepMap screen medium = baseline) |
|---|---|---|---|---|---|---|---|---|---|
| ACH-000426 | **KMS-20** | Lymphoid / mature B-cell neoplasm | −0.54 | −0.73 | 4.47 | 1.05 | mutant | −4.33 / 0.88 | RPMI + 10% FBS (MF-001-001) |
| ACH-000515 | **HCC-33** | Lung / lung neuroendocrine tumour | −0.54 | −0.57 | 4.39 | 1.37 | mutant | −3.94 / 0.89 | RPMI + 20% FBS (MF-001-020) |

HCC-33's CN of 1.37 is below the 1.5 amplification threshold but close to it; CRISPRi arms are specified below for that reason. Back-up lines meeting the rule, in order: HT-1376 (ACH-000724, Bladder, −0.53/−0.66, MEM + 10% FBS), HCM-CSHL-0155-C50 (ACH-003360, Breast, −0.86/−0.56, organoid MF-051-008), PA-1 (ACH-001374, Ovary, TP53 WT), GI-ME-N (ACH-001344, PNS, TP53 WT). **Note for interpretation:** HT-1376 is a Bladder/Urinary Tract line, the lineage whose removal flips the top term (§5); using it as a third line is a deliberate stress test, not a confirmation line.

**Control line that expresses g but does not depend on it (same lineage as line 1):** ACH-001119 **Mac-2A** (Lymphoid, mature T/NK neoplasm), g effect **+0.15**, expression **8.33**, CN 1.05, TP53 WT, NNMD −4.13, RPMI + 15% FBS (MF-001-017).

**Common-essential handling:** CCDC71L is **not** common-essential (13/1,361 lines < −0.5), so the RPE1-hTERT TP53⁻/⁻ or HEK293T degron route is **not required**. A degron is nevertheless used for the acute-depletion arm (below) because the growth effect is small and slow.

**Baseline medium:** each line's DepMap screen medium, as tabled above. No carbon-source change is used; if any sensitised condition is added later it is a separate arm.

**Essential-gene confound control (required):** acute (dTAG degron) or hypomorphic (CRISPRi titration) depletion of CCDC71L, time-matched to BMI1/SMCHD1/LRIF1 depletion, run beside a **matched-essentiality control gene from an unrelated module: KLHDC3** — Chronos effect in the two chosen lines **−0.559 (KMS-20) and −0.562 (HCC-33)**, genome-wide mean −0.037, SD 0.177 †, i.e. matched to CCDC71L's −0.543/−0.543 (mean −0.063). KLHDC3 is a CRL2/KLHDCX-family C-degron substrate receptor [A-C17, A-C20] — a ubiquitin-ligase module with no relation to chromatin silencing. Alternative matched controls, if KLHDC3 proves unsuitable: KLHDC3 → MOSMO (−0.470/−0.651, mean −0.055) or IFRD2 (−0.537/−0.431, mean −0.102) †.

## 3. Reagents

- **3 sgRNAs** targeting *CCDC71L* plus **2 non-targeting guides** and an **AAVS1 cutting control**. Per-guide DepMap effects are not available locally and no guide-library file is held in this project (`DATA.md` lists no Avana/Brunello guide map), so **guide sequences are not stated here**: they are to be taken from a published library (Brunello / Avana *CCDC71L* guides) at execution time and concordance across the three guides is checked inside the experiment. Stating sequences from memory would be an unverified claim and is deliberately omitted.
- **Sequence-level off-target check of every guide** before use: genome-wide mismatch search (e.g. Cas-OFFinder / CRISPOR against GRCh38), requiring no perfect or 1-mismatch protospacer in any other gene and, specifically, none in *CCDC71* (the gene's only matrix paralogue, excluded from N(g) by design but a plausible guide off-target given the shared N-terminal identity noted in [A-C1]) or in the loci of BMI1/SMCHD1/LRIF1/PHF19/MEN1/BAHD1. Tool and full result recorded in the experiment log.
- **CRISPRi guides** (dCas9-KRAB, TSS-proximal) as a parallel arm in HCC-33 given its CN of 1.37, and as the hypomorphic-titration arm in both lines.
- **Guide-resistant cDNA** (ORFeome *CCDC71L*, codon-wobbled at the three protospacers) for rescue; plus the **PxVxL point mutant P223A/V225A/L227A** on the same backbone.
- **Named charge-matched control bait: composition-scrambled CCDC71L ("scCCDC71L").** The same 235 residues in a randomised order (fixed seed, recorded), expressed from the same promoter with the same tag — matched by construction on length (235 aa), amino-acid composition, net charge (+30), R+K fraction (21.3%), proline fraction (12.8%), predicted disorder and expression level, and verified to enter the nucleus by the same fractionation assay used for the WT bait (if it does not, an SV40 NLS is appended and the WT bait carries the same appendage). A scramble is preferred to a natural basic protein because no natural protein matches all of those axes simultaneously; a secondary natural control may be added by the stated criteria (200–270 aa, ≥ 18% R+K, net ≥ +20, nuclear, no GO:0040029 annotation) but is not required.
- **Endogenous knock-in** (mNeonGreen–HaloTag–3×FLAG, N- and C-terminal versions, since the PxVxL motif is 8 residues from the C-terminus and a C-terminal tag may occlude it — the N-terminal knock-in is the primary reagent).
- **Antibodies:** no validated CCDC71L antibody is known to this project, which is why endogenous tagging is primary. Partner and mark antibodies: SUZ12, EED, BMI1, RING1, CBX4, CBX8, PHC3, SMCHD1, LRIF1, CBX1/CBX3/CBX5 (HP1β/γ/α), H2AK119ub1, H3K27me3, H3K9me3, H3 total; plus HP1-independent nuclear markers (lamin B1, nucleolin) and the Golgi marker GM130 (to test the HPA Approved Golgi call directly).

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of CCDC71L with CBX5, CBX3, SMCHD1/LRIF1 and SUZ12 (ipTM/pDockQ) | days | Confident, conserved interface | No interface (does not exclude types b–e) | **yes** | PxVxL(223–227) docked into the CBX5 chromo-shadow-domain dimer groove, ipTM ≥ 0.6 / pDockQ ≥ 0.23; prior expectation set by Predictomes SPOC 0.903 for CBX5 †. No interface predicted for SUZ12/EED |
| 1 | Competitive growth (GFP/mCherry mix), 3 guides + guide-resistant cDNA rescue, 2 dependent lines vs Mac-2A control | 2–3 wk | Dropout only in dependent lines; rescued by WT cDNA | No dropout, or no rescue (off-target or proximity) | **yes** | log2 fold-depletion of edited cells ≈ 0.4–0.8 over 14–21 population doublings in KMS-20/HCC-33 (consistent with Chronos −0.54), ≤ 0.1 in Mac-2A; rescue restores to ≤ 0.15; all 3 guides concordant. **Power (†, computed):** 3 guides × 4 biological replicates = 12 independent log2FC measurements; a two-sided one-sample t-test at α = 0.05 detects a 0.40 log2 depletion with power 1.00 at between-replicate SD 0.15 or 0.20 and 0.99 at SD 0.30. Per *guide* (n = 4) the same effect has power 0.93 / 0.76 / 0.45 at those SDs — the design is powered at gene level but **not** at guide level, so a single discordant guide is uninformative. The SD must be estimated in a pilot (AAVS1 + non-targeting arms) before the run; if it exceeds 0.30, replicates rise to 6 per guide |
| 1 | **Essential-gene confound control:** dTAG/CRISPRi-titrated depletion of CCDC71L time-matched to BMI1/SMCHD1/LRIF1 depletion, vs KLHDC3 (matched essentiality, unrelated module) | 2–4 wk | Chromatin readouts change beyond KLHDC3's at matched growth effect | Same change as KLHDC3 (general sickness, not module function) | **yes** | At a growth effect matched within ±15%: ≥ 1.5-fold change in global H3K9me3 or H2AK119ub1 (quantitative western, spike-in-normalised) and ≥ 50 differentially expressed Polycomb/HP1 target genes in CCDC71L-depleted cells, with KLHDC3-depleted cells within ±1.2-fold and < 10 such genes |
| 1 | Localisation with markers (endogenous knock-in, live + fixed) | 2–4 wk | Nuclear/chromatin, partially overlapping HP1 foci | Incompatible compartment (e.g. exclusively Golgi/actin) | **yes** | ≥ 70% of mNG signal nuclear; Pearson colocalisation with CBX5/HP1α foci ≥ 0.4 and with H3K9me3 ≥ 0.4; GM130 colocalisation < 0.2. A dominantly Golgi/actin pattern (HPA Approved call) is falsification #1 |
| 1 | Module-specific readout after KO (see §5) | 2–4 wk | Phenocopies partner KO | Normal | **yes** | See §5 |
| 1 | Partner protein levels after CCDC71L KO (and the reverse) | 2 wk | Co-destabilisation (types a/b) | Stable (favours c/d) | **yes** | CBX1/3/5, SMCHD1, LRIF1, BMI1, SUZ12 levels within ±20% expected under type d; > 40% loss of any one would argue for a/b and would require revisiting the type |
| 2 | **IP-MS of endogenously tagged CCDC71L vs (i) PxVxL mutant, (ii) scCCDC71L composition-scrambled bait, (iii) untagged parental**, SAINT scoring | 1–2 mo | Partners enriched; HP1 loss specific to the motif mutant | Absent, or another module appears, or identical interactome in the mutant (stickiness) | **yes (decisive)** | WT: CBX1/CBX3/CBX5 SAINT BFDR ≤ 0.01 with ≥ 4-fold enrichment over scCCDC71L; mutant: HP1 isoforms lost (≥ 4-fold down) while ≥ 80% of other high-confidence preys retained — **with ADNP, POGZ and CHAMP1 pre-specified as permitted co-losses and excluded from that 80% denominator**, because ADNP forms the HP1-containing ChAHP complex with CHD4 [A-C24] and POGZ/CHAMP1 co-occur with ADNP in g's own STRING-exp interactor set, so a chromo-shadow-domain-dock mutation may legitimately take them with it; scoring them as retained-or-lost would otherwise decide the experiment the wrong way. Expected low-prior preys from existing data: CBX3 (all three admitted P sources, with the non-independence caveat of §6), LRIF1, ADNP, CHAMP1, POGZ |
| 2 | CUT&RUN of tagged CCDC71L with H3K9me3, H3K27me3, H2AK119ub1 | 1–2 mo | Co-occupancy with one arm; KO redistributes that mark | Random/promoter-background distribution | **yes** | ≥ 40% of CCDC71L peaks inside H3K9me3 domains (HP1 arm) **or** inside H3K27me3/H2AK119ub1 domains (PcG arm) vs ≤ 10% expected by chance; the arm that wins selects the mechanism |
| 2 | Double KO / epistasis with BMI1, SMCHD1, LRIF1 | 1–2 mo | No extra defect (same pathway) | Additive or synergistic (parallel pathways) | **yes** | Growth-interaction score \|π\| < 0.1 for same-pathway partners vs > 0.2 for an unrelated essential gene |
| 2 | Arrayed CRISPRi Perturb-seq with the six supporting partners | 2 mo | Signatures cluster | Distinct | no (deferred; Tier-2 budget spent on IP-MS + CUT&RUN) | — |
| 3 | PxVxL-interface mutants fail to rescue; reconstitution with recombinant HP1 | 6–12 mo | Interface required for function | Mutants rescue fully | contingent on Tier 2 | Growth rescue by PxVxL mutant < 50% of WT rescue if the HP1 interface is functionally required |

Type-specific rows: relationship type is **d**, for which the template specifies no extra row. The type-(e) row is nevertheless retained as an alternative-explanation control, because §8 keeps a lineage/chromatin-state explanation alive:

| Type | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| e (control for the alternative) | CUT&RUN/ChIP of tagged CCDC71L at the partners' target loci + a silenced reporter assay | 1–2 mo | CCDC71L occupies the targets; reporter derepression depends on CCDC71L | No occupancy; reporter unchanged → the co-dependency is regulatory, not functional | **yes** | ≥ 2-fold reporter derepression on CCDC71L depletion, matched to the BMI1/SMCHD1 positive control and absent in the KLHDC3 arm |

## 5. Module readouts

| Module | Readouts |
|---|---|
| Other (module not listed): epigenetic regulation of gene expression / Polycomb and HP1 silencing | Global and locus-level **H2AK119ub1** and **H3K27me3** (PRC1/PRC2 arm) and **H3K9me3** (HP1 arm) by spike-in-normalised western and CUT&RUN; derepression of Polycomb/HP1 target genes by RNA-seq; inactive-X compaction (Barr-body area, in a female line) as the SMCHD1–LRIF1-specific readout. Source: PRC1 mono-ubiquitylates H2A at K119 and PRC2 methylates H3K27 [A-C6, Appendix A row C6]; LRIF1 mediates SMCHD1's H3K9me2/3-dependent chromatin binding [A-C4]; depletion of LRIF1(HBiX1) or SMCHD1, but not PRC2, decompacts the inactive X [A-C5] |

**Chosen readout:** H3K9me3 / H2AK119ub1 / H3K27me3 CUT&RUN co-occupancy plus spike-in western, with target-gene derepression by RNA-seq as the functional complement. The Barr-body/Xi-compaction assay is run only if a suitable female line is added (none of KMS-20, HCC-33, Mac-2A is selected on that basis).

## 6. Experiment that separates the alternative explanation

- **Alternative:** CCDC71L's chromatin association and co-dependency are a non-specific consequence of its highly basic, low-complexity sequence (21.3% R+K, net +30 †), not pathway membership.
- **Experiment:** the Tier-2 IP-MS run as a three-way comparison — endogenously tagged WT CCDC71L, the isogenic PxVxL point mutant (P223A/V225A/L227A), and the named composition-scrambled bait scCCDC71L (§3) expressed at matched level — with SAINT scoring against the untagged parental, plus a salt-series wash (150/300/500 mM NaCl) and benzonase treatment to separate protein-mediated from nucleic-acid-mediated associations.
- **Readout if the prediction is right:** HP1 isoforms (CBX1/3/5) and LRIF1 are enriched in WT at BFDR ≤ 0.01, survive benzonase and 300 mM salt, and are specifically lost in the PxVxL mutant while the rest of the interactome is retained; scCCDC71L recovers histones but not HP1.
- **Readout if the alternative is right:** WT and PxVxL-mutant interactomes are indistinguishable; scCCDC71L recovers a similar histone/basic-protein set; HP1 enrichment collapses with benzonase or above 150 mM salt.

## 7. Decision rule (fixed in advance)

- **Supported:** dropout in both dependent lines rescued by guide-resistant cDNA **AND** a module-specific chromatin readout that changes beyond the KLHDC3 matched-essentiality control at matched growth effect **AND** nuclear/chromatin localisation of the endogenous protein **AND** Tier-2 physical (HP1/LRIF1 by IP-MS, motif-dependent) or epistatic (|π| < 0.1 with BMI1/SMCHD1/LRIF1) support.
- **Refuted:** a dropout that is not rescued, or incompatible localisation (non-nuclear in both dependent lines).
- **Ambiguous:** anything else — reported as such, with the alternative relationship type proposed. Specifically: chromatin localisation and HP1 binding **without** any module readout change ⇒ propose type a/c against a different module (HP1 bodies) rather than type d against GO:0040029; module readout change **without** HP1 binding ⇒ the Polycomb arm, retaining type d.

## 8. Evidence ledger (Part II)

| Claim | Source | Verbatim span | Verified |
|---|---|---|---|
| H2AK119ub1 / H3K27me are the assayable products of PRC1 / PRC2, so they report on the Polycomb arm of the module | PMID:34400841 (DOI 10.1038/s41580-021-00398-y) | "Polycomb repressive complex 1 (PRC1) mono-ubiquitylates histone H2A at Lys119 (H2AK119ub1)" (full text, PMC7612013) | **Y** |
| H3K9me2/3 reports on the SMCHD1–LRIF1 arm; LRIF1 is required for SMCHD1 chromatin binding | PMID:42303997 (DOI 10.1038/s41467-026-74427-9) | "chromatin binding of SMCHD1 genome-wide, including on the Xi, is critically dependent on the protein LRIF1 that mediates interaction with H3K9me2/3-modified nucleosomes" (full text, PMC13434421) | **Y** |
| Xi compaction is a PRC2-independent readout of the SMCHD1/LRIF1 arm | PMID:23542155 | "Depletion of HBiX1 or SMCHD1, but not Polycomb repressive complex 2 (PRC2), resulted in Xi decompaction" (abstract) | **Y** |
| PxVxL mutation is a valid specificity control for HP1 binding | PMID:14765118 (DOI 10.1038/sj.emboj.7600088) | "targeting of HP1beta to heterochromatin requires shadow domain interactions with PXVXL-containing proteins in addition to chromo domain recognition of Lys-9-methylated histone H3" (abstract) | **Y** |
| KLHDC3 belongs to an unrelated (CRL2 C-degron ubiquitin) module | PMID:39548056 (DOI 10.1038/s41467-024-54126-z); PMID:41606720 | "reveal principles of C-degron recognition across the KLHDCX family" (full text, PMC11568203); "KLHDC3 deficiency in mice reveals essential roles in development, survival, and adiposity via the DesCEND ubiquitin pathway" (title/full text, PMC12922316) | **Y** |
| KLHDC3 Chronos effects −0.559 (KMS-20) / −0.562 (HCC-33), genome-wide mean −0.037 | `data/raw/depmap/CRISPRGeneEffect.csv` via `results/m7/scratch_reports_ccdc71l/ctrl.py` † | recomputed value, not a literature claim | **Y** (recomputed) |
| Cell lines, effects, expression, CN, TP53 status, media | `reports/data/CCDC71L/bundle.md` §10 (from `results/ledger/*` and DepMap) | ledger rows | **Y** |

## 9. Red-team review (Part II)

- **Reviewer / date:** separate `red_team` agent, 2026-10-30. Its scope covered Parts I and II together, so the single unedited review at `reports/redteam/CCDC71L.md` serves both; **verdict ACCEPT WITH REVISIONS**.
- **Experiment-specific findings and responses** (what would make the experiment uninformative: off-target guides, proximity effects, lineage dependence, rescue failure, assay insensitivity) are carried in the point-by-point table in Appendix B, which covers every Part II item the reviewer raised; each Part II change is marked there with the section it landed in.
- **PI response (separate):** every required Part II fix was made rather than argued with. Nothing in the reviewer's text has been edited, abridged or answered inline.

---

## Appendix A. Evidence ledger

Every claim in this report that is not a ledger row from `results/ledger/*.tsv` or `reports/data/CCDC71L/bundle.md` has a row here. Verification method: each PMID/DOI was resolved through the Europe PMC REST API on 2026-10-30, the abstract or full text retrieved, and the span checked as a substring of the retrieved text after stripping markup tags and collapsing whitespace (script: `results/m7/scratch_reports_ccdc71l/verify.py`, span list `spans.tsv`; **39/39 spans pass after the red-team revision**, which added A-C21, A-C22 and A-C24 and corrected A-C13's provenance). Rows that failed were deleted, not kept. The red-team reviewer re-resolved every row independently and found no span failure.

| Key | Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|---|
| A-C1 | Human CCDC71L contains a canonical PxVxL motif | PMID:34780483 / DOI 10.1371/journal.pgen.1009909 | "A canonical PxVxL sequence is also found in the human CCDC71L protein" (text read: full text, PMC8629390) | Y |
| A-C2 | The paralogue CCDC71 associates strongly with HP1 isoforms, possibly via CCDC71L | PMID:34780483 / DOI 10.1371/journal.pgen.1009909 | "Our analysis clearly demonstrates a strong association between CCDC71 and HP1 isoforms" (full text, PMC8629390) | Y |
| A-C3 | PxVxL motifs dock on the HP1 chromo-shadow domain and are required for HP1 heterochromatin targeting | PMID:14765118 / DOI 10.1038/sj.emboj.7600088 | "targeting of HP1beta to heterochromatin requires shadow domain interactions with PXVXL-containing proteins in addition to chromo domain recognition of Lys-9-methylated histone H3" (abstract) | Y |
| A-C4 | SMCHD1's chromatin binding depends on LRIF1, which reads H3K9me2/3 nucleosomes | PMID:42303997 / DOI 10.1038/s41467-026-74427-9 | "chromatin binding of SMCHD1 genome-wide, including on the Xi, is critically dependent on the protein LRIF1 that mediates interaction with H3K9me2/3-modified nucleosomes" (full text, PMC13434421) | Y |
| A-C5 | The SMCHD1–LRIF1(HBiX1) Xi-compaction pathway is PRC2-independent | PMID:23542155 | "Depletion of HBiX1 or SMCHD1, but not Polycomb repressive complex 2 (PRC2), resulted in Xi decompaction" (abstract) | Y |
| A-C6 | PRC1 deposits H2AK119ub1; PRC2 deposits H3K27 methylation | PMID:34400841 / DOI 10.1038/s41580-021-00398-y | "Polycomb repressive complex 1 (PRC1) mono-ubiquitylates histone H2A at Lys119 (H2AK119ub1)" (full text, PMC7612013) | Y |
| A-C7 | A porcine orthologue of CCDC71L positively regulates fat deposition in cultured intramuscular adipocytes | PMID:23301040 | "functions as a positive regulator of fat deposition in cultured intramuscular adipocytes" (full text, PMC3536781) | Y |
| A-C8 | CCDC71L overexpression rescues the anti-tumour effect of LINC00514 knockdown in TNBC cells | PMID:33757509 / DOI 10.1186/s12935-021-01875-2 | "Rescue assay verified that overexpressed CCDC71L countervailed the anti-tumor influence of LINC00514 knockdown" (full text, PMC7986463) | Y |
| A-C9 | CCDC71L is described as acting in cellular lipid metabolism (HNSCC prognostic analysis) | PMID:38367702 / DOI 10.1016/j.jormas.2024.101799 | "Coiled-coil domain containing 71 like (CCDC71L) exerts an important role in cellular lipid metabolic process" (abstract) | Y |
| A-C10 | The CCDC71L–PIK3CG locus is a replicated GWAS signal for platelet count | PMID:29066854 | "we replicated three known genome-wide significant loci in our cohort (at CCDC71L-PIK3CG, BAK1 and ARHGEF3)" (full text, PMC5669488) | Y |
| A-C11 | A CCDC71L 3'UTR variant upstream of PIK3CG associates with carotid intima-media thickness | PMID:24951662 / DOI 10.1161/circgenetics.113.000116 | "A 3' untranslated region CCDC71L variant (rs2286149), upstream from PIK3CG, was the most significant finding" (abstract) | Y |
| A-C12 | CCDC71L is grouped with lipid-metabolism genes in pig skeletal-muscle RNA-seq | PMID:38647104 / DOI 10.1002/jsfa.13551 | "played dominant roles in the lipid metabolism" (abstract) | Y |
| A-C13 | SPOC is a trained classifier separating true from false AlphaFold-Multimer PPI predictions (Predictomes) | PMID:40015271 / DOI 10.1016/j.molcel.2025.01.034 | "we used machine learning on curated datasets to train a structure prediction and omics-informed classifier (SPOC)" (text read: **abstract** — corrected provenance; the PMC11931459 full text renders the expansion with spaced capitals, so this exact string occurs in the abstract only. The second SPOC span used in §6, "effectively separates true and false AF-M predictions of PPIs", **is** in the full text) | Y |
| A-C21 | SPOC's feature set includes DepMap co-dependency and BioGRID interaction data, so it is not independent of them | PMID:40015271 / DOI 10.1016/j.molcel.2025.01.034 | "co-dependency data from DEPMAP" (full text, PMC11931459; in context: "genome-wide features of each protein pair that were external to AlphaFold, including co-dependency data from DEPMAP … and high throughput interaction experiments from the BioGRID database") | Y |
| A-C22 | BioGRID experiment counts are the single most important biological feature in SPOC | PMID:40015271 / DOI 10.1016/j.molcel.2025.01.034 | "the number of independent experiments supporting an interaction in the BioGRID database" (full text, PMC11931459; in context "…(21%)") | Y |
| A-C24 | ADNP forms the HP1-containing ChAHP complex with CHD4 — the basis for pre-specifying ADNP/POGZ/CHAMP1 as permitted co-losses in the PxVxL-mutant IP-MS | PMID:29795351 / DOI 10.1038/s41586-018-0153-8 | "ADNP interacts with the chromatin remodeller CHD4 and the chromatin architectural protein HP1 to form a stable complex, which we refer to as ChAHP" (abstract) | Y |
| A-C14 | hu.MAP 3.0 integrates > 25,000 MS experiments into > 15,000 human complexes | PMID:40425816 / DOI 10.1038/s44320-025-00121-5 | "we integrated >25,000 mass spectrometry experiments using a machine learning approach to identify >15,000 human protein complexes" (full text, PMC12222714) | Y |
| A-C15 | Wainberg 2021 predicts functions for 108 uncharacterised genes | PMID:33859415 / DOI 10.1038/s41588-021-00840-z | "predicts the functions of 108 uncharacterized genes" (abstract; full text not retrievable) | Y |
| A-C16 | Replogle 2022 assigns function to poorly characterised genes from genome-scale Perturb-seq | PMID:35688146 / DOI 10.1016/j.cell.2022.05.013 | "We use transcriptional phenotypes to predict the function of poorly characterized genes" (full text, PMC9380471) | Y |
| A-C17 | KLHDC3 is a member of the KLHDCX C-degron E3 ligase family | PMID:39548056 / DOI 10.1038/s41467-024-54126-z | "reveal principles of C-degron recognition across the KLHDCX family" (full text, PMC11568203) | Y |
| A-C19 | The Predictomes proteome-wide screen ranks all ~200 million human protein pairs before structural modelling | DOI 10.1101/2025.11.10.687652 (Europe PMC PPR1117736; Crossref resolved 2026-10-30) | "a classifier called KIRC (Knowledge-Informed Rapid Classifier), trained on biological features, was used to rank all 200 million possible protein pairs in the human proteome by their interaction likelihood" (abstract) | Y |
| A-C20 | KLHDC3 acts in the DesCEND/CRL2 ubiquitin pathway (unrelated module) | PMID:41606720 / DOI 10.1186/s12864-026-12574-5 | "KLHDC3 deficiency in mice reveals essential roles in development, survival, and adiposity via the DesCEND ubiquitin pathway" (full text, PMC12922316) | Y |

Project-file sources used for numbers (not literature claims): `reports/data/CCDC71L/bundle.md` (all ledger values, partners, flags, orthogonal states, cell lines, figures); `results/ledger/top40_primary.tsv` (rank 16, p_cal, demotion); `results/ledger/M6_SUMMARY.md` (tier branch, Σp_cal, caveats); `results/holdout_eval/SUMMARY.md` (hold-out rates and calibration); `results/m7/report_selection.md` (selection rule); `results/m7/L/HGNC_26685.md` (blinded literature items); `results/m7/judge/analysis_main_genes.tsv`, `results/m7/judge/analysis_main.md`, `results/m7/judge/scores/*` (blinded verdicts); `results/m7/recall_probe_90.tsv` (recall probe); `DEVIATIONS.md` (operationalisations); `data/raw/humap3/*`, `data/raw/predictomes2025/*` (hu.MAP 3.0 and Predictomes values marked †); `data/raw/depmap/CRISPRGeneEffect.csv` († recomputed correlations and control-gene effects). Recomputation scripts: `results/m7/scratch_reports_ccdc71l/{lines.py,lines3.py,par.py,ctrl.py,verify.py}`.

## Appendix B. Red-team review

- **Reviewer / date:** separate `red_team` agent (did not write this report), 2026-10-30.
- **Review text (unedited):** `reports/redteam/CCDC71L.md`. It is kept as a separate file rather than inlined, unedited and unabridged, because this assignment permitted writing only to `reports/CCDC71L.md`; nothing in it has been altered or omitted.
- **Verdict: ACCEPT WITH REVISIONS.** The reviewer independently re-resolved all 19 Appendix-A keys and the Part II ledger (no span failures), recomputed every number in the report (all reproduced exactly, including the Predictomes and hu.MAP values), ran an independent Europe PMC sweep that **upheld** the claim that no chromatin/HP1 function for CCDC71L is published, and could not break the type-e (lineage) defence.
- **Lint result (claims without a verified source):** pass — no claim in the revised report lacks either a project-file source or a verified Appendix-A key. The reviewer found one *provenance* error (A-C13 labelled full text, actually abstract), now corrected.

### Response to red team (point by point)

| # | Red-team point | Response | Where fixed |
|---|---|---|---|
| R1 | "Three independent data types" is indefensible: SPOC is trained on DepMap co-dependency and BioGRID; STRING-exp aggregates BioPlex/HCM; raw co-dependency with CBX1/3/5 is −0.105 to −0.010 and no HP1 protein is in N(g) | **Accepted in full.** The claim is deleted everywhere. §6 now carries an explicit three-point non-independence subsection citing the Predictomes paper's own feature list [A-C21, A-C22], and §11 states the narrower defensible claim instead | §0, §6 ("Independence: what these sources do and do not add"), §11 |
| R2 | Use the reciprocal framing: CCDC71L is 3rd of 364 CBX5 SPOC pairs | **Accepted.** Recomputed independently (SUV39H2 0.910, CBX1 0.906, CCDC71L 0.903, CBX3 0.889, CCDC71 6th at 0.820; 0.785% of 1,614,047 pairs exceed 0.9) and now the headline structural statement | §0, §6, §11 |
| R3 | Selective reporting: CCDC71L–LRIF1 SPOC 0.000 omitted | **Accepted.** Reported beside the CBX1/3/5 values, with the explicit note that it is the only Predictomes pair between g and a supporting partner and that it is negative | §6, §11 |
| R4 | Raw co-dependency magnitudes undisclosed (SUZ12 0.120 rank 250; LRIF1 0.040; PHF19 0.022; top raw correlates are junk) | **Accepted.** A full raw-correlation table is added with ranks, g's top raw correlates, and the plain statement that the signal exists only post-correction and is carried by split-half reproducibility, not amplitude. Also surfaced in §0 as doubt (i), including the contrast with the companion PLEKHH3 report | §3 (new table), §0 |
| R5 | GO:0040029 (BP) and GO:0001221 (MF) are not nested; the flip occurs in 2 of 3 refits, not "the same failure twice" | **Accepted.** Both corrected, with the obo namespaces and `is_a` parents quoted, the misattribution explained (GO:0045814 is the true descendant), and the consequence spelled out: an MF binding term would point at a type-a claim this report is not entitled to make | §5 |
| R6 | Stickiness is the prior, not a devil's-advocate position (HCM prey of CENPA/HIST1H2BG/HIST1H3A/APEX1) | **Accepted.** §8 alternative 1 now states it as the prior and cites the four bait recoveries with SaintScores; §0 doubt (ii) does the same | §0, §8 |
| R7 | Name the charge-matched control bait | **Accepted.** Named: **scCCDC71L**, a composition-scrambled CCDC71L (fixed seed) matched by construction on length, composition, net charge, proline fraction, disorder and expression, with nuclear-import verification; used throughout Part II in place of the earlier unspecified "charge-matched bait" | Part II §3, §4, §6 |
| R8 | PxVxL-mutant criterion is confounded by ChAHP (ADNP/POGZ/CHAMP1) | **Accepted.** Those three are pre-specified as permitted co-losses and excluded from the 80% retention denominator, with the ChAHP citation added to the ledger [A-C24] | Part II §4 (Tier 2), Appendix A |
| R9 | No power statement for the Tier-1 competition assay | **Accepted.** Computed and stated: 3 guides × 4 replicates gives power 1.00/1.00/0.99 at SD 0.15/0.20/0.30 for a 0.40 log2 effect, but only 0.93/0.76/0.45 per guide — powered at gene level, not guide level; pilot SD estimate required | Part II §4 (Tier 1) |
| R10 | §0 does not price in that HPA predicts Falsification #1 will fire | **Accepted.** §0's first-experiment bullet now states that on admitted evidence refutation is more likely than not | §0 |
| R11 | "5 complexes" (§7) contradicts "8" (§6/§11) | **Accepted.** Corrected to 8 | §7 |
| R12 | "NOAZFP" is not a gene symbol; the bait is ZNF330 (alias NOA36) | **Accepted.** Corrected, with the file's `ZNF330_target` label noted | §6 |
| R13 | A-C13's span is in the abstract, not the full text | **Accepted.** Provenance corrected in the ledger row, with the distinction explained | Appendix A |
| R14 | The blinded step should be reported as uninformative (incomplete evidence set), not neutral | **Accepted.** §7's procedural note is rewritten to say exactly that, while leaving the pre-registered statistic unrevised | §7 |
| R15 | AlphaFold pLDDT could not be re-verified (AFDB returned 403 to the reviewer) | **Noted, no change.** The value is marked † and is not load-bearing; it is recomputable from `results/m7/scratch_reports_ccdc71l/` by anyone the endpoint serves. Flagged here as independently unchecked |  — |
| R16 | Credit: lineage leave-out failure is correctly diagnosed; type-e defence holds; HT-1376 stress test and the *CCDC71* off-target requirement are good | **Noted.** The lineage-removal partner-correlation stability (≤ 0.005) and the lineage-demeaned correlations are now reported explicitly rather than asserted | §3, §5 |
