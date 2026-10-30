# ANKRD52 — candidate report (Template A) — **N1 rediscovery exemplar**

All numbers are copied from `reports/data/ANKRD52/bundle.md` (machine-generated from `results/ledger/*`), or, where marked †, from the descriptive recomputations in `results/m7/scratch_reports_trappc5/` (scripts `ranks.py`, `profiles.py`, `lines.py`, `ctrl2.py`). Literature sentences carry an Appendix-A key; every key is verified (PMID resolves through the Europe PMC API and the verbatim span occurs in the retrieved abstract or full text; `verify.py`, `verify_out.json`). Search date 2026-10-30.

This gene was selected as the highest-ranked N1 (already-characterised) gene in the primary top 40, to show how precisely the pipeline recovers a published mechanism and where it stops short (`results/m7/report_selection.md`). It is reported as validation; no novelty is claimed for the module.

> **Post-review correction (2026-10-31).** Wainberg 2021 was previously discussed only as out of scope for its 108
> uncharacterised-gene predictions, and the earliest DepMap co-dependency publication was given as Shui et al. 2023. The
> Wainberg 2021 supplementary tables and Kim 2019 Tables S5/S6 have now been checked (`data/raw/revision_downloads/`;
> record in `results/revision/report_novelty_corrections.md`): **Wainberg 2021 already published ANKRD52 in d = 0.9
> co-essential modules with the miRNA machinery** ({AGO2, ANKRD52, DGCR8, DICER1, DROSHA, XPO5} and {AGO2, ANKRD52,
> DICER1, TARBP2, XPO5}, "miRNA loading onto RISC") **and with PP6** ({ANKRD52, PPP2R4, PPP6C, PPP6R1}), with AGO2 as
> its strongest pair; **Kim 2019** lists ANKRD52–AGO2/XPO5/PPP6C/DICER1 pairs and a 2-gene cluster {AGO2, ANKRD52}.
> Changes: §0 "Strongest reason to doubt" now cites these earlier catalogues; the §7 "what genuinely remains new" and
> "prior prediction lists" items and §11 are corrected — the "miRNA-shaped rather than PP6-shaped" observation is
> downgraded because both catalogues already show ANKRD52's strongest co-essential links to be miRNA-machinery genes.
> Nothing else was changed.

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** ANKRD52 acts in microRNA-mediated gene silencing. In plain words: the protein is needed for the small-RNA silencing machinery to work, and cells that need Argonaute-2, Dicer, Drosha, Exportin-5 and the TNRC6 proteins also need ANKRD52. The relationship is **d — pathway member**, not a subunit of the silencing complex: ANKRD52 is physically a subunit of the phosphatase PP6, and acts *on* the pathway rather than in its complex.
- **Confidence:** p_cal = **0.1410** [95% CI 0.065–0.244] — the expected probability that the predicted GO term (GO:0031047 regulatory ncRNA-mediated gene silencing) is confirmed by a later D1-evidence annotation. It is not a probability about the relationship type. This is the highest p_cal among the **2,583 in-support U genes that received a p_cal** (of 4,271 scorable; 1,421 got none and 133 are upper-bound only, `results/ledger/pcal_summary.json`); tier: none (0 Tier A / 0 Tier B).
- **Strongest reason to doubt:** nothing here is new. The mechanism was published in 2017 [A1], and the AGO2–ANKRD52/PPP6C co-dependency in DepMap itself was published in 2023 [A12] — and, *corrected 2026-10-31*, earlier still as co-essential modules/pairs in Kim 2019 (Tables S5/S6: ANKRD52–AGO2, –XPO5, –PPP6C, –DICER1; cluster {AGO2, ANKRD52}) and Wainberg 2021 (Supplementary Data 2: miRNA-machinery and PP6 modules containing ANKRD52, "miRNA loading onto RISC"); the recall probe recognised the gene; and the orthogonal physical evidence points at PP6, not at RISC (P class: no support). The only defensible claim is that the pipeline re-derived a true, published pathway assignment blind.
- **Headroom problem, stated up front:** if ANKRD52 matters for fitness by letting AGO2 accumulate in its inactive phosphorylated form, its effect should not much exceed AGO2 loss of function — yet AGO2 knockout is near-neutral (mean −0.090; < −0.5 in 1.8% of lines; −0.502 and −0.332 in the two chosen lines †) while ANKRD52 is consistently stronger (−0.243; −0.685 and −0.539 †). Either phospho-AGO2 is dominant-negative rather than null, or other Argonautes are involved (AGO1 is also hyperphosphorylated on ANKRD52 loss [A7]), or part of the dependency is not miRNA-mediated at all. The experiments name which escape is being tested.
- **First experiment:** test whether ANKRD52's *fitness* requirement runs through the AGO2 phospho-cycle — knock in non-phosphorylatable AGO2(S824–S834→A) in two ANKRD52-dependent lines and ask whether it rescues ANKRD52 loss; time ~12–16 weeks; approximate cost £40–55k (details in `reports/ANKRD52_experiments.md`).
- Cancer-line essentiality is not organismal function: dependency in DepMap lines says the gene is needed for proliferation there, not what it does in the organism. Note in particular that in HCT116 — the line in which the mechanism was discovered [A23] — neither ANKRD52 (−0.08) nor AGO2 (−0.08) is a proliferation dependency †; the co-essentiality signal lives in the covariance across 1361 lines, not in essentiality itself.

## Definitions used in this template

**Relationship type (DESIGN §4.4).**

| Code | Type | Claim allowed |
|---|---|---|
| a | Stable subunit | Only with physical, co-abundance or structural support. |
| b | Assembly or maturation factor | "Required for assembly or maturation of M". |
| c | Supplier or client | Transporter, enzyme, or substrate of an import or insertion machinery that co-varies with M. |
| d | Pathway member | "Acts in pathway M". |
| e | Lineage or transcriptional programme | Regulatory co-dependency; not a function call. |

**Novelty class (DESIGN §1.5, §6.3).** N1 established (rediscovery; curation lag) — reported as validation, never dropped. N2 partial/indirect. N3 none found.

---

## 1. Header

- Symbol: ANKRD52 | HGNC ID: HGNC:26614 | previous symbols: — | aliases: FLJ34236 / PP6-ARS-C | UniProt: Q8NB46 | band: 12q13.3 (Ensembl ENSG00000139645; Entrez 283373)
- D1 / D2 / D3: True / False (UniProt annotation score 3) / True (D3_pubmed True, D3_tdark False; focused PMIDs 6, all PMIDs 62; TDL Tbio) | curation-lag audit flag: not in the audit sample
- Stratum (§1.4): family **other**; expression **expressed** (log2(TPM+1) ≥ 1 in 99.9% of lines); informativeness tertile **high**; core **False**; paralogues in the matrix: 3
- Hypothesis (one sentence): ANKRD52 acts in regulatory ncRNA-mediated gene silencing (miRNA pathway).
- Relationship type: **d — type unresolved / pathway member** (script rule: no P, A or S support for the *predicted* module; complex-like V1′ label but no physical support for it). This is the correct conservative outcome: the literature says ANKRD52 is a stable subunit of PP6 [A8, A15, A16] that acts on the miRNA pathway by dephosphorylating AGO2 [A1], i.e. a pathway member with respect to the predicted module, not a RISC subunit.
- Novelty class: **N1** (search date 2026-10-30).
- LLM-recall-probe flag (§6.2): **known**; probe answer at `results/m7/recall_probe_90.tsv` — "Ankyrin-repeat regulatory subunit C of the PP6 phosphatase (PP6-ARS-C)."; matches the network top term: **no** — the probe recalled the PP6 subunit identity but not the miRNA-pathway function. The prediction is therefore not independent of background knowledge about the protein's identity, but the probe did not state the predicted module.
- Calibrated probability p_cal: **0.1410** [95% CI 0.065–0.244, cluster bootstrap, 2000 refits]; calibration family **other**; covariates inside H's 5th–95th percentile: **yes** (in_support; top-K mean zavg 10.682, R 0.472, coverage pct 0.859, size pct 0.172)
- Tier: none (p_cal fill); rank in primary top 40: **1**; top-40-only demotion label: none (no lineage-leave-out, DEMETER2 or TP53 flag).

**What p_cal means** (`results/holdout_eval/SUMMARY.md`, `results/ledger/M6_SUMMARY.md`): on the temporal hold-out H, precision@1 was 0.030 (95% CI 0.018–0.043) vs 0.000 for the prior-only ranker and 0.005 for the matched-gene null; the calibration model fitted on H has out-of-fold slope 0.819 (Wald 0.512–1.127), intercept −0.006, Brier 0.0294, c-statistic 0.855. p_cal estimates the probability that *this top term* is confirmed by a later D1-evidence GO annotation (~8-year horizon) — for an N1 gene this is a statement about the GO curation process, not about the biology, which is already settled. Σp_cal over the top 40 is 2.04 (1.05–3.24).

## 2. The protein

- Domains (InterPro): IPR002110 (ankyrin repeat); IPR036770; IPR050889; Pfam PF00023, PF12796, PF13637; length 1076 aa. TM / signal peptide / MTS: none. AlphaFold pLDDT: **not retrieved — no AlphaFold per-residue file is held in the project**. Deepest orthologue: not determined from project files; UniProt records no "sequence similarities" line for this entry.
- UniProt protein name: "Serine/threonine-protein phosphatase 6 regulatory ankyrin repeat subunit C (PP6-ARS-C)"; function (verbatim): "Putative regulatory subunit of protein phosphatase 6 (PP6) that may be involved in the recognition of phosphoprotein substrates." [L4]; subunit (verbatim, ECO:0000269 from PubMed 18186651): "Protein phosphatase 6 (PP6) holoenzyme is proposed to be a heterotrimeric complex formed by the catalytic subunit, a SAPS domain-containing subunit (PP6R) and an ankyrin repeat-domain containing regulatory subunit (ARS). Interacts with PPP6R1" [L5]. UniProt lists **no** subcellular location.
- Class H (homology) evidence: no IBA/ISO annotation to the predicted term for this gene (reported only).
- Source keys: L4, L5, A8, A15, A16 (Appendix A).

## 3. Dependency profile

- Mean / SD of Chronos effect: **−0.243 / 0.231**; median −0.227; 5th percentile −0.638; min −1.445; fraction of lines < −0.5: **0.1242** (169 / 1361); common-essential: **no**; NaN fraction 0.0000. ANKRD52 is a *selective*, generally weak dependency.
- Expression: log2(TPM+1) ≥ 1 in 99.9% and ≥ 2 in 97.0% of lines; median 3.94. Spearman ρ(effect, own expression) = +0.024 (n = 1292); scatter in `reports/data/ANKRD52/fig_profile.png` panel (b).
- Lineage enrichment (descriptive): Cervix n 18, mean −0.329, p 0.0511; Pleura n 21, −0.307, p 0.3408; Skin n 75, −0.302, p 0.0134. Skin's nominal p is not corrected and the leave-out test (on Cervix, the lowest-mean lineage) passes.
- Split-half assessability: R(g) = **0.472**; null mean 0.004, max 0.200 over 200 matched genes; empirical p **0.0050**; RBO 0.726 (p 0.0050); assessable: **yes**.
- Figure 1: `reports/data/ANKRD52/fig_profile.png` — (a) ANKRD52 vs AGO2 across 1361 lines (Pearson r = 0.37, Spearman ρ = 0.35), (b) effect vs own expression; chosen lines D1/D2 and control C marked.

## 4. Neighbourhood

Top-10 partners (`results/ledger/u_partners.tsv`; GLS rank = rank in ANKRD52's GLS row after the §3.1 exclusions):

| partner | zavg_BEF | z_B / z_E / z_F | GLS rank | partner function and essentiality | chromosome and distance | paralogue / shared-guide flag | hu.MAP-train |
|---|---|---|---|---|---|---|---|
| AGO2 | 25.76 | 43.3 / 20.6 / 13.4 | 1 | Argonaute-2, RISC core; weak dependency, mean −0.09, 1.8% of lines < −0.5; annotated to the predicted term | 8q24.3; different chromosome | no | no / pair no |
| XPO5 | 24.40 | 42.9 / 20.2 / 10.1 | 3 | pre-miRNA nuclear export; mean −0.71, 76.3%; in term | 6p21.1; different chr | no | no / pair no |
| DICER1 | 23.69 | 41.5 / 19.8 / 9.7 | 2 | pre-miRNA processing; mean −0.55, 56.6%; in term | 14q32.13; different chr | no | no / pair no |
| DROSHA | 22.37 | 40.1 / 20.0 / 7.0 | 6 | pri-miRNA processing; mean −0.48, 41.8%; in term | 5p13.3; different chr | no | no / pair no |
| TNRC6A | 21.00 | 36.6 / 19.8 / 6.6 | 5 | GW182, RISC effector; mean −0.06, 0.7%; in term | 16p12.1; different chr | paralogue of another partner | no / pair no |
| DGCR8 | 20.05 | 34.5 / 19.2 / 6.4 | 8 | Microprocessor; mean −0.52, 51.5%; in term | 22q11.21; different chr | no | no / pair no |
| TNRC6B | 16.27 | 28.1 / 17.1 / 3.7 | 38 | GW182 paralogue; mean −0.07, 0.8%; in term | 22q13.1; different chr | paralogue of another partner | no / pair no |
| PPP6C | 13.62 | 20.9 / 11.8 / 8.3 | 4 | **PP6 catalytic subunit**; mean −0.59, 61.5%; *not* annotated to the predicted term | 9q33.3; different chr | no | no / pair no |
| CNOT9 | 10.96 | 14.6 / 13.7 / 4.6 | 28 | CCR4-NOT (deadenylation, downstream of RISC); mean −0.50, 49.0% | 2q35; different chr | no | no / pair no |
| PPP6R1 | 7.54 | 8.9 / 8.5 / 5.2 | 7 | PP6 SAPS subunit; mean +0.03, 0.2% | 19q13.42; different chr | paralogue of another partner | no / pair no |

Shared-sgRNA / per-guide checks are not possible (guide-level data unavailable).

Figure 2: `reports/data/ANKRD52/fig_network.png` — 54 edges with zavg_BEF ≥ 3 among the 11 nodes; only 14 have physical support, and the ANKRD52 ones are to PPP6C, PPP6R1 and TNRC6B, i.e. to PP6 (plus one BioGRID-LTP edge), not to RISC.

Top 3 terms (R1, K = 25):

| term | name | S | p_emp | hypergeometric p (descriptive) | leave-one-partner-out stability |
|---|---|---|---|---|---|
| GO:0031047 | regulatory ncRNA-mediated gene silencing | 158.114 | 0.0020 | 0.0000 | rank kept after all 8 single-partner removals |
| GO:0016441 | post-transcriptional gene silencing | 115.689 | 0.0020 | 0.0000 | 5 of 6 |
| GO:0035194 | regulatory ncRNA-mediated post-transcriptional gene silencing | 92.003 | 0.0020 | 0.0000 | 1 of 5 |

Second-ranked term: **GO:0016441 post-transcriptional gene silencing**; most specific term in the top 5: GO:0035195 miRNA-mediated post-transcriptional gene silencing; V1 and V1′ label: **GO:0016442 RISC complex** (5 supporting partners).

**Recomputed neighbourhood detail † (`ranks.py`, `profiles.py`).**
- **Reciprocity:** ANKRD52 is AGO2's rank-1 partner in AGO2's own genome-wide row (zavg_BEF 25.76), ahead of XPO5 (23.85), DICER1 (23.07), DROSHA (21.98), TNRC6A (21.32), DGCR8 (20.44), TNRC6B (17.38), TARBP2 (13.80), CNOT9 (10.72) and PPP6C (10.65).
- **Paralogue specificity:** of the three PP6 ankyrin-repeat (ARS) subunits, only ANKRD52 is in this neighbourhood — in ANKRD52's row ANKRD28 ranks 82 (zavg 2.87) and ANKRD44 ranks 16460 (−0.62); their Chronos means are +0.020 and +0.028 (essentially dispensable) versus ANKRD52's −0.243.
- **The phosphatase, not the kinase:** PPP6C ranks 8 (13.62) but the opposing kinase CSNK1A1 ranks 6911 (0.01) despite being a strong dependency in its own right (mean −0.792) — co-essentiality recovers the partner whose loss has the *same* directional consequence, not the antagonist.
- **PP6 vs miRNA shape:** in PPP6C's own row the top partners are PTPA (21.79), PPP6R3 (20.60), CYB5R4 (20.03), TIPRL (18.42), LCMT1 (16.61), PPME1 (14.54), then ANKRD52 (13.62) — i.e. PPP6C's profile is phosphatase-shaped, while ANKRD52's is miRNA-pathway-shaped. PPP6R1 (+0.032), PPP6R2 (−0.131) and ANKRD28/44 are not dependencies; PPP6R3 is weak (−0.322).
- **Covariance robustness (red-team request) †:** the ANKRD52–AGO2 Chronos correlation is r = 0.367 (ρ = 0.351) over all 1361 lines; dropping the 5% of lines with the most extreme joint |z| leaves r = 0.290 (ρ = 0.307, n = 1293); a 30-lineage jackknife moves it only between r = 0.347 (dropping CNS/Brain, n = 133) and r = 0.377 (dropping Bone); and it is not a poor-screen artefact — in the 251 best-quality screens (ScreenNNMD < −10) r = 0.416 versus 0.359 in the remaining 1110. The covariance is therefore distributed across lines and lineages rather than carried by a handful of outliers, which matters because AGO2, TNRC6A and TNRC6B are themselves near-zero dependencies.
- **Partner essentiality spread:** XPO5 −0.710, DICER1 −0.547, DGCR8 −0.520, DROSHA −0.484 are moderate dependencies, while AGO2 (−0.090), TNRC6A (−0.065), TNRC6B (−0.072) and TARBP2 (−0.110) are not — the module is detected through profile covariance, not through shared strong essentiality.

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | pass | g on 12q; 0 of the top-10 partners on g's chromosome |
| Bidirectional-promoter / overlapping / readthrough partners | pass | 0 of 8 supporting partners flagged |
| Copy-number co-amplification | pass | 0 of 8 flagged; max \|r\| 0.06 (AGO2 0.02, XPO5 −0.02, DICER1 −0.06, DROSHA −0.02, TNRC6A −0.04, DGCR8 0.06, TNRC6B −0.03, DDX6 0.03) |
| Hub-driven call | pass | hub share 0.00; 0 hub partners; g's in-degree 37 (not a hub) |
| Lineage leave-out | pass | Cervix (18 lines, mean −0.329) removed and the tool refitted: top term still GO:0031047; N(g) overlap 0.92 |
| K = 10 / 50 | pass | same top term at both K |
| Dependency vs own expression; TF / lineage-marker enrichment | pass | ρ = +0.024 (n 1292); 2 TFs in N(g), OR 1.07, p 0.5719, q 1.0000 |
| TP53 / p53-axis correlation | pass | 902 mutant vs 459 WT; p 0.2415, q 0.4129; median difference +0.022 |
| DEMETER2 replication | not measured | 0 supporting partners present in DEMETER2 |
| Shared-sgRNA and per-guide check | not possible (guide maps / guide-level data not available) | recorded |
| GLS network top term (descriptive) | same | GO:0031047 |

ANKRD52 is one of two genes in the primary top 10 with no failed check of any kind; **MED31** (rank 8) is the other and is strictly cleaner — its DEMETER2 check was *measured and replicated* (mean partner r 0.064 vs null 95th percentile 0.049) where ANKRD52's is "not measured", and it has four supporting orthogonal classes (PALG) where ANKRD52 has none (`results/ledger/top40_primary.tsv`).

## 6. Orthogonal evidence matrix (four states)

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | BioPlex 3.0 / OpenCell / BioGRID-LTP / STRING-exp (one group) + Human Cell Map SAINT | **no support** | 1 edge to the 62 term members vs null mean 0.327 (the BioGRID-LTP TNRC6B edge); ANKRD52's actual physical partners are PPP6C, PPP6R1, PPP6R2, PPP6R3, ANKRD28, HUWE1, USP10, ZRANB1, CLEC16A, TULP3 — PP6, not RISC | P_group 0.2827; HCM_SAINT 1.0000; class **0.5654** | family "other" → any class can serve as diagnostic |
| A co-abundance | ProteomeHD; CCLE proteomics | **no support** | ProteomeHD stat 0.621 vs null 0.524 (p 0.0140); CCLE 0.539 vs 0.523 (p 0.3287); CCLE pair r: PPP6C 0.46 (100th pct), PPP6R1 0.33, XPO5 0.29, CNOT9 0.28, DICER1 0.21, AGO2 0.06 | class **0.0280**, but Holm across 3 measured classes (0.0210, 0.0280, 0.5654) requires ≤ 0.0167 → **no support** |  |
| L localisation | HPA v25.1 | **no support** | HPA Approved: Mitochondria; Nucleoplasm → vocabulary "mitochondrion, nucleus"; 0.709 of term members share a compartment vs null 0.569 | class **0.0210**; smallest of the three class p-values, so Holm compares it with α/3 = 0.0167 → not rejected, and testing stops |  |
| G perturbation phenotype | Perturb-seq K562 GW / K562 essential / RPE1 essential | **not measured** | ANKRD52 is not among the perturbed genes in any of the three datasets | — |  |
| S structure | Burke 2023 AF2 | **not measured** | 1 modelled pair with g, 0 with pDockQ ≥ 0.23; no measured term member | — |  |
| H homology | orthologue IBA/ISO | reported only | no IBA/ISO annotation for g | reported only | — |

**No orthogonal class supports the predicted module, and there is no contradiction** (term compartments cytosol|nucleus; HPA gives mitochondrion+nucleus, OpenCell cytoplasmic, Human Cell Map NMF microtubule cytoskeleton, MitoCarta assessed and not listed; g is multi-localised, so the contradiction rule cannot fire). This is exactly the pattern expected for a **type-d** relationship: the protein's stable physical partners are its own complex (PP6), while its functional partners are the pathway it regulates. The type rule's refusal to call "subunit" is therefore a correct, not a missing, result — and the published mechanism [A1, A5] states the AGO2 interaction is RNA-independent but transient enough that it does not appear as a RISC co-complex in the admitted P sources.

Reported but not counted: hu.MAP 3.0 places ANKRD52 in huMAP3_01958.1 (confidence 1) with PPP6C, ANKRD28, ANKRD44, PPP6R1, PPP6R2, PPP6R3 and MRNIP — i.e. **hu.MAP assigns ANKRD52 to PP6, not to the miRNA pathway** †. Predictomes (circular: uses DepMap as a feature) scores ANKRD52–PPP6R3 0.997, ANKRD52–PPP6R2 0.991, ANKRD52–PPP6R1 0.974, ANKRD28–ANKRD52 0.934, but ANKRD52–AGO2 only 0.329 †. DEMETER2: not measured.

## 7. Literature (blinded step, then synthesis)

**Blinded summary of agent L's items** (`results/m7/L/HGNC_26614.md`, 11 items, N1): two UniProt items (putative PP6 regulatory subunit; PP6 heterotrimer), a 2008 proteomics item identifying Ankrd28/44/52 as PP6-associated ankyrin proteins, two items from a 2017 Nature paper describing an AGO2 phosphorylation cycle with dephosphorylation by the ANKRD52-PPP6C complex and global impairment of miRNA silencing when the cycle is inactivated, a 2021 tumour-immunology item on patient mutations and miR-155/SOCS1, a 2021 TAZ/PAK1 item, a 2024 PP6-stemness item, a 2024 pan-cancer item, a 2023 review item listing ANKRD52-PPP6C among kinases/phosphatases acting on miRNA biogenesis machinery, and one flagged collision (the circular intronic RNA ci-ankrd52, excluded from protein-function evidence). Agent L recorded the collision explicitly and marked every item DepMap-derived = no.

**Blinded verdicts** (`results/m7/judge/`, packet J071): real statement (slot C: "functions in regulatory ncRNA-mediated gene silencing; module context: RISC complex") **+1** from both judges; decoys **0, 0, 0** (synaptic transmission / HDAC complex; deacylase activity / telomere cap complex; dicarboxylic acid metabolism / plasma-membrane receptor complex); d = **1.0**. J1's justification: "Row 4: GENE_X-PPP6C dephosphorylates AGO2 and sustains miRNA-mediated silencing; row 5 miRNA silencing impaired; row 6 miR-155/SOCS1." Context: primary top 40, 18/40 real supported vs 3/120 decoys, exact sign-flip **p = 0.0002174**; N1 subset 16/31 supported, mean d 0.419; judge κ = 0.975.

**Unblinded synthesis.** ANKRD52 is one of three ankyrin-repeat regulatory subunits of protein phosphatase 6, identified by mass spectrometry as co-precipitating with the PP6 catalytic subunit and the SAPS subunit PP6R1 [A8], with the proposal that "the SAPS and ankyrin repeat regulatory subunits determine the function and specificity of PP6" [A9]; PP6 is a heterotrimer of PP6c, a PP6R and an ANKRD28/44/52 scaffold [A15, A16], consistent with UniProt [L4, L5]. The function that our prediction names was established by a genome-wide CRISPR screen with a miR-19 EGFP reporter in HCT116 [A23], which found "interacting components of the serine/threonine protein phosphatase 6 (PPP6) complex (ANKRD52 and PPP6C)" among the top hits [A6] and showed that "target engagement by Argonaute 2 (AGO2) triggers its hierarchical, multi-site phosphorylation by CSNK1A1 on a set of highly conserved residues (S824-S834), followed by rapid dephosphorylation by the ANKRD52-PPP6C phosphatase complex" [A1], with the consequence that "inactivation of this phosphorylation cycle globally impairs miRNA-mediated silencing" [A2]. Loss of ANKRD52 or PPP6C causes AGO2 to accumulate in the phosphorylated form in multiple human cell lines [A3] and also hyperphosphorylates AGO1 [A7]; the complex binds AGO2 RNA-independently [A5]; miRNA abundance itself is unchanged [A4], so this is a silencing-competence effect, not a biogenesis effect; and non-phosphorylatable AGO2 rescues silencing in ANKRD52-null cells [A22]. Independent structural and kinase work supports the cycle: CK1α phosphorylates the AGO2 eukaryotic insertion after target binding to promote target release [A11], and CK1A1 is a priming kinase for the cluster [A19]. The pathway has physiological consequences: tumours inactivate the machinery, and "re-introduction of ANKRD52 frequent patient mutations dampens the JAK-STAT-interferon-γ signaling and antigen presentation in cancer cells, largely by abolishing miR-155-targeted silencing of suppressor of cytokine signaling 1 (SOCS1)" [A10]; oncogenic K-Ras suppresses global miRNA activity through the same axis [A21], and that study reports Ankrd52 knockout in MEFs raising Ago2 Ser825/829 phosphorylation [A13]. PP6 has other, unrelated substrates — Aurora A T-loop [A20], MEK [A18] — and ANKRD52 itself has been reported as a transcriptionally repressed tumour suppressor acting on PAK1 phosphorylation in lung adenocarcinoma [A14]. Finally, the locus produces a well-studied circular intronic RNA, ci-ankrd52, which regulates Pol II transcription [A17]; this is a *locus-level* collision and says nothing about the protein — agent L flagged it correctly, and our dependency data cannot distinguish a CRISPR cutting effect on the protein-coding gene from one on the intronic RNA (see §8).

**How precisely does the co-essentiality prediction recover the published mechanism?** Very precisely at the level of *pathway*, not at all at the level of *mechanism*:

| Published element [key] | Recovered by our pipeline? | Evidence |
|---|---|---|
| ANKRD52 acts in miRNA-mediated silencing [A1, A2] | **Yes** — top term GO:0031047, S 158.114, p_emp 0.0020, stable at K = 10/50 and under GLS | bundle §2, §5 |
| AGO2 is the relevant Argonaute [A1] | **Yes, and sharply** — AGO2 is rank 1 for ANKRD52 and ANKRD52 is rank 1 for AGO2 †; AGO1 ranks 8276 and AGO3 5212 † (whereas [A7] reports AGO1 is also hyperphosphorylated — the dependency data do not see that) | `ranks.py` |
| PPP6C is the catalytic partner [A1] | **Yes** — PPP6C rank 8 (zavg 13.62), GLS rank 4 | bundle §4 |
| It is ANKRD52 specifically, not ANKRD28/44 [A8] | **Yes** — ANKRD28 rank 82, ANKRD44 rank 16460 † | `ranks.py` |
| The wider miRNA machinery (DICER1, DROSHA, DGCR8, XPO5, TNRC6A/B) [A2] | **Yes** — all six in the top 7 partners | bundle §4 |
| The kinase CSNK1A1 [A1, A11, A19] | **No** — rank 6911 † despite being a strong dependency (mean −0.792) †; an antagonistic enzyme does not co-vary | `ranks.py`, `profiles.py` |
| The substrate and the residues (AGO2 S824–S834) [A1] | **No** — co-essentiality has no substrate resolution | — |
| The direction (dephosphorylation sustains silencing) [A2, A22] | **No** — the method is sign-agnostic about mechanism | — |
| ANKRD52 is physically a PP6 subunit [A8, A15] | **Partly, and only as a confound** — PPP6C/PPP6R1 appear as partners 8 and 10, and the orthogonal P class and hu.MAP both point at PP6 †; the module call would have been PP6 had PP6 been the stronger signal | bundle §6 |

**What, if anything, does it add?** Three things, each modest and each stated with its limit. (i) *Blindness and rank*: the assignment was produced without the literature, and it is the single highest-confidence call in the whole uncharacterised set (p_cal 0.141, rank 1 of 40), with no failed artefact check — so it is a clean positive control for the pipeline. (ii) *Shape of the dependency*: ANKRD52's profile is miRNA-pathway-shaped rather than PP6-shaped (PPP6C's own top partners are PTPA, PPP6R3, CYB5R4, TIPRL, LCMT1, PPME1 †), and the other PP6 regulatory subunits are not dependencies at all †. In proliferating cancer lines, therefore, the non-redundant fitness contribution of ANKRD52 appears to run through the miRNA arm of PP6 rather than through PP6's Aurora A [A20] or MEK [A18] substrates — a quantitative, pan-lineage statement that the HCT116-based discovery screen [A23] could not make. (iii) *Robustness of the covariance*: it survives a 30-lineage jackknife (r 0.347–0.377), removal of the 5% most extreme lines (r 0.290) and restriction to the best screens (r 0.416) †.

**What it does not add — corrected after red-team review.** The DepMap observation is not ours, and it is broader in the source than we first reported: Shui et al. 2023 state that "Gene effect scores from CRISPR mediated knockout of AGO2, ANKRD52, DICER1, XPO5, TNRC6A, DROSHA, and PPP6C in all cell lines were extracted and plotted" [A24], i.e. the pan-miRNA-machinery DepMap comparison across all lines was already published [A12], together with Ankrd52-knockout MEF data [A13]. That removes most of claim (iii) and part of (ii) as novel. **What genuinely remains new is narrow:** the PP6-versus-miRNA contrast (ANKRD28 rank 82, ANKRD44 rank 16,460, PPP6R1/R2 non-dependencies, PPP6C's own phosphatase-shaped neighbourhood †) and the blind, calibrated, artefact-screened derivation itself. *Narrowed further 2026-10-31:* the miRNA-dominant shape is itself visible in earlier catalogues — Wainberg 2021 puts ANKRD52 in both miRNA-machinery and PP6 co-essential modules with AGO2 (p = 2e-19) and XPO5 (2e-12) ahead of PPP6C (3e-11), and Kim 2019 clusters ANKRD52 with AGO2 alone — so only the explicit PP6-paralogue/regulatory-subunit quantification above is not in prior work. We claim re-derivation, not discovery.

**Closest prior publication:** [A1] (Golden et al. 2017, Nature) for the mechanism and [A12] (Shui et al. 2023, Molecular Cell) for the DepMap co-dependency. Our contribution relative to them is the blind, calibrated, artefact-screened re-derivation described above.

**Prior prediction lists containing this gene.** Wainberg 2021 used UniProt annotation score ≤ 2 [T21] for its 108 predictions [T22]; ANKRD52's score is 3, so it is outside that set. *Corrected 2026-10-31 (supplementary tables checked):* its Supplementary Data 2 nevertheless contains ANKRD52 in modules 2209 (d = 0.9: AGO2, ANKRD52, DGCR8, DICER1, DROSHA, XPO5; "miRNA loading onto RISC involved in gene silencing by miRNA", 807.7-fold), 4854 (d = 0.9: AGO2, ANKRD52, DICER1, TARBP2, XPO5; same term, 1453.9-fold), 4397 (d = 0.9: ANKRD52, PPP2R4, PPP6C, PPP6R1; no enriched term), 353 (d = 0.5, 14 genes, miRNA term; adds TNRC6A, PPP6C) and 1695 (d = 0.5, 15 genes; "protein serine/threonine phosphatase complex"); Supplementary Data 1 pairs ANKRD52 with AGO2 (p = 2e-19), XPO5 (2e-12), PPP6C (3e-11), DICER1 (3e-09), TARBP2 (7e-07), PPP6R1 (2e-05) and TNRC6A (7e-05). Kim 2019: Table S5 pairs ANKRD52–AGO2 (PCC 0.477), –XPO5 (0.461), –PPP6C (0.368), –DICER1 (0.353); Table S6 cluster 348 = {AGO2, ANKRD52}. hu.MAP 3.0 contains ANKRD52 but assigns it to PP6 †. Replogle 2022: ANKRD52 is not among the perturbed genes in the three Perturb-seq datasets used here (bundle §6) and does not appear in the annotated embedding-coordinates file †. Predictomes: present, but circular, and scores the AGO2 pair low (0.329) †.

**Post-freeze (after 2026-10-29) papers confirming the prediction:** none found as of 2026-10-30.

## 8. Alternative explanations

- *Proximity / locus / CN artefacts.* All partners are on other chromosomes; 0 of 8 supporting partners carry a locus or CN flag.
- *Hub-driven, lineage or expression-programme effects.* Hub share 0.00; lineage leave-out passes; ρ(effect, expression) +0.024; no TF enrichment (OR 1.07) — type **e** excluded.
- *TP53 axis / screen-quality artefacts.* No TP53 flag (p 0.2415).
- **The ci-ankrd52 / circANKRD52 collision (upgraded after red-team review; the most serious artefact hypothesis here).** CRISPR cutting at the ANKRD52 locus destroys both the protein-coding gene and the circular RNAs made from it. Those circular RNAs are not inert bystanders: ci-ankrd52 is a positive regulator of Pol II transcription [A17] and forms R-loops more readily than its cognate pre-mRNA [A27], while circANKRD52 is independently reported to be **miRNA-coupled and proliferation-promoting** — it "possessed a tumor-promoting effect by acting as a sponge of miR-497-5p and thereby upregulated BIRC5 in HCC cells" [A25], and in melanoma "Knockdown of circANKRD52 repressed the growth and invasion of melanoma cells in vitro and in vivo, whereas ectopic expression of circANKRD52 promoted these effects" [A26]. A proliferation-promoting, miRNA-sponging RNA from this locus is precisely the shape of artefact that could generate both the dependency and its covariance with miRNA machinery under CRISPR cutting. The AGO2-5XA rescue [A22] remains a good argument — hyperphosphorylation of AGO2 requires loss of the phosphatase *protein* — but it is an argument about the **reporter** phenotype in HCT116, not about the **fitness** phenotype in the dependent lines, which is the claim at issue. The experiment plan therefore promotes degron-versus-cutting and ci-ankrd52 knockdown to a Tier-1 arm.
- *PP6-general rather than miRNA-specific requirement.* ANKRD52 loss removes a PP6 substrate-targeting subunit; the fitness effect could be mediated by any PP6 substrate (Aurora A [A20], MEK [A18], PAK1 [A14]) and the miRNA-pathway partners could co-vary for an unrelated reason. Against this: the other ARS subunits are dispensable and PPP6C's own neighbourhood is phosphatase-shaped †. **Strongest competing biological hypothesis**, and the one the decisive experiment targets.
- *Curation lag.* The gene is N1: the function is published [A1] and has been for nine years, but GO's D1-evidence annotations had not captured it at the pre-registration freeze. This is the exemplar's point — the pipeline's "uncharacterised" set is defined by annotation state, not by literature state.

## 9. Falsifying observations

(Drafted from the machine bundle, §1–§5. Honest note on ordering: the template asks that §9 be written before §6/§7 are read; for this gene the author had already read the literature, so the statements below are framed as experimental outcomes that do not depend on §6/§7.)

1. Acute degron depletion of ANKRD52 protein in two dependent lines leaves miRNA reporter silencing and AGO2 phosphorylation unchanged relative to a matched-essentiality control gene — i.e. the dependency has nothing to do with the silencing pathway.
2. Knock-in of non-phosphorylatable AGO2 does not rescue the proliferation defect of ANKRD52 loss in dependent lines, while a PP6-substrate-specific intervention elsewhere does — i.e. the *fitness* requirement runs through other PP6 substrates and the module assignment, though true at pathway level, does not explain the dependency that generated it.
3. Degron depletion of the ANKRD52 protein (RNA intact) produces no fitness defect while exonic cutting does, and/or knockdown of circANKRD52 alone reproduces the defect — i.e. the DepMap signal was a locus artefact [A25, A26, A27] rather than a protein function.

## 10. Experiments

See `reports/ANKRD52_experiments.md` (Template B).

## 11. Novelty and external benchmarks

No novelty is claimed. The module assignment is a **rediscovery** of a mechanism published in 2017 [A1] and of a DepMap co-dependency published in 2023 [A12]; it is **not found in the literature as of 2026-10-30** only in the narrow sense that no publication states that ANKRD52's dependency profile is miRNA-pathway-shaped rather than PP6-shaped (§7 (ii)) — *corrected 2026-10-31:* and even that shape is implicit in two earlier co-essentiality catalogues, Kim 2019 (ANKRD52 clustered with AGO2 alone) and Wainberg 2021 (miRNA-machinery and PP6 modules, AGO2 the strongest pair), which predate Shui 2023 and recover the same module; only the explicit PP6-subunit/paralogue quantification is not in prior work. The broader "generality across lines" claim has been withdrawn: Shui et al. 2023 already extracted and plotted DepMap effects for AGO2, ANKRD52, DICER1, XPO5, TNRC6A, DROSHA and PPP6C across all lines [A24]. ANKRD52 is outside Wainberg 2021's annotation-score ≤ 2 set [T21, T22], but its supplementary modules already contain the same miRNA-machinery assignment (§7; *corrected 2026-10-31*); hu.MAP 3.0 contains it but assigns PP6 †; Replogle 2022 did not perturb it (bundle §6); Predictomes is circular here. The value of this report is as a calibration point: the pipeline's single highest-confidence uncharacterised-gene call, made blind, is correct at the level of pathway, silent at the level of mechanism, and correctly conservative about the relationship type.

## Appendix A. Evidence ledger

Verification protocol: each PMID resolved through the Europe PMC REST API (`search?query=EXT_ID:<pmid> AND SRC:MED`, resultType core); the DOI returned is listed; the verbatim span was searched in the retrieved abstract and, where a PMC full text was fetched (Europe PMC `fullTextXML` or the NCBI BioC endpoint), in that full text. Script and output: `results/m7/scratch_reports_trappc5/verify.py`, `claims.json`, `verify_out.json`. All rows verified **Y**.

| Key | Claim | Source (PMID / DOI / file) | Verbatim span | Verified |
|---|---|---|---|---|
| L4 | UniProt's function statement for ANKRD52 | UniProt Q8NB46 (`reports/data/ANKRD52/bundle.md` §8; REST copy `results/m7/scratch_reports_trappc5/uniprot_Q8NB46.json`, 2026-10-30) | "FUNCTION: Putative regulatory subunit of protein phosphatase 6 (PP6) that may be involved in the recognition of phosphoprotein substrates." | Y |
| L5 | UniProt's PP6 heterotrimer statement | UniProt Q8NB46, SUBUNIT (ECO:0000269, PubMed 18186651) | "Protein phosphatase 6 (PP6) holoenzyme is proposed to be a heterotrimeric complex formed by the catalytic subunit, a SAPS domain-containing subunit (PP6R) and an ankyrin repeat-domain containing regulatory subunit (ARS). Interacts with PPP6R1" | Y |
| A1 | The AGO2 phospho-cycle and ANKRD52-PPP6C as its phosphatase | PMID:28114302 / 10.1038/nature21025 | "target engagement by Argonaute 2 (AGO2) triggers its hierarchical, multi-site phosphorylation by CSNK1A1 on a set of highly conserved residues (S824-S834), followed by rapid dephosphorylation by the ANKRD52-PPP6C phosphatase complex" (abstract) | Y |
| A2 | Inactivating the cycle impairs silencing globally | PMID:28114302 | "inactivation of this phosphorylation cycle globally impairs miRNA-mediated silencing" (abstract) | Y |
| A3 | ANKRD52/PPP6C loss accumulates phospho-AGO2 in several lines | PMID:28114302 | "Deficiency of ANKRD52 or PPP6C in multiple human cell lines similarly led to accumulation of phosphorylated AGO2" (full text) | Y |
| A4 | miRNA abundance is not reduced (not a biogenesis effect) | PMID:28114302 | "The steady-state abundance of representative miRNAs was not decreased" (full text) | Y |
| A5 | The AGO2–ANKRD52-PPP6C interaction is RNA-independent | PMID:28114302 | "AGO2 and ANKRD52-PPP6C interacted in an RNA-independent manner" (full text) | Y |
| A6 | ANKRD52 and PPP6C were screen hits without a prior miRNA-pathway role | PMID:28114302 | "interacting components of the serine/threonine protein phosphatase 6 (PPP6) complex (ANKRD52 and PPP6C)" (full text) | Y |
| A7 | AGO1 is also hyperphosphorylated on ANKRD52 loss | PMID:28114302 | "We also observed enhanced phosphorylation of AGO1 in ANKRD52" (full text) | Y |
| A22 | Non-phosphorylatable AGO2 rescues silencing in ANKRD52-null cells | PMID:28114302 | "expression of AGO25XA or AGO2S828A, but not wild-type AGO2, rescued repression of the miR-19 EGFP reporter in ANKRD52" (full text) | Y |
| A23 | The miR-19 EGFP reporter screen system (HCT116) | PMID:28114302 | "Enhanced green fluorescent protein (EGFP) transcripts with or without a 3' untranslated region (UTR) harboring eight imperfectly complementary binding sites for miR-19, an abundant miRNA, were expressed in the stably diploid cell line HCT116" (full text) | Y |
| A8 | Ankrd28/44/52 co-precipitate with PP6c and PP6R1 | PMID:18186651 / 10.1021/bi7022877 | "Mass spectrometry identified coprecipitating proteins as PP6 catalytic subunit and three ankyrin repeat proteins (Ankrd28, Ankrd44, and Ankrd52)." (abstract) | Y |
| A9 | The regulatory subunits determine PP6 specificity | PMID:18186651 | "We propose that the SAPS and ankyrin repeat regulatory subunits determine the function and specificity of PP6." (abstract) | Y |
| A10 | ANKRD52 patient mutations dampen IFN-γ signalling via miR-155/SOCS1 | PMID:34853298 / 10.1038/s41467-021-27331-3 | "Genetic inactivation of the machinery or re-introduction of ANKRD52 frequent patient mutations dampens the JAK-STAT-interferon-γ signaling and antigen presentation in cancer cells, largely by abolishing miR-155-targeted silencing of suppressor of cytokine signaling 1 (SOCS1)." (abstract) | Y |
| A11 | Target binding primes AGO2's eukaryotic insertion for CK1α phosphorylation | PMID:35638597 / 10.7554/elife.76908 | "binding of miRNA-loaded human Ago2 to target RNA with complementarity to the seed and 3' supplementary regions of the miRNA primes the EI for hierarchical phosphorylation by CK1α" (abstract) | Y |
| A12 | The AGO2–ANKRD52/PPP6C co-dependency was already reported from DepMap | PMID:37402366 / 10.1016/j.molcel.2023.06.008 | "genome-wide CRISPR knock-out (KO) screens in human cancer cell lines (DepMap 21Q2 Public+Score, CERES) revealed strong positive co-dependency between AGO2 and ANKRD52/PPP6C" (full text) | Y |
| A13 | Ankrd52 knockout raises Ago2 Ser825/829 phosphorylation in MEFs | PMID:37402366 | "Ankrd52 KO in mouse embryonic fibroblasts (MEFs) increased Ago2 phosphorylation at the Ser825/829 sites, as measured by mass spectrometry (MS)" (full text) | Y |
| A21 | Oncogenic K-Ras suppresses global miRNA activity (same axis) | PMID:37402366 | "K-RasG12D promotes global suppression of miRNA activity" (abstract) | Y |
| A14 | ANKRD52/PP6c loss raises PAK1 phosphorylation (another PP6 substrate) | PMID:33096142 / 10.1016/j.bbamcr.2020.118891 | "Knockdown of ANKRD52 or PP6c resulted in upregulated PAK1 phosphorylation." (abstract) | Y |
| A15 | PP6 is a heterotrimer with ANKRD28/44/52 scaffolds | PMID:39014521 / 10.1111/cas.16271 | "Protein phosphatase 6 functions as a heterotrimer with a catalytic subunit (PP6c), regulatory subunits (PP6Rs; PP6R1, PP6R2, and PP6R3), and scaffold subunits (ANKRD28, ANKRD44, and ANKRD52)." (abstract) | Y |
| A16 | ANKRD52 is a PP6 holoenzyme component | PMID:38296907 / 10.1007/s10528-023-10645-w | "Ankyrin repeat domain 52 (ANKRD52) is a regulatory component of the protein phosphatase 6 (PP6) holoenzyme." (abstract) | Y |
| A24 | Shui 2023 already plotted DepMap effects for the whole miRNA-machinery set | PMID:37402366 / 10.1016/j.molcel.2023.06.008 | "Gene effect scores from CRISPR mediated knockout of AGO2, ANKRD52, DICER1, XPO5, TNRC6A, DROSHA, and PPP6C in all cell lines were extracted and plotted" (full text) | Y |
| A25 | circANKRD52 sponges miR-497-5p and promotes HCC tumorigenesis (locus collision) | PMID:33845641 / 10.1177/09636897211008874 | "circANKRD52 possessed a tumor-promoting effect by acting as a sponge of miR-497-5p and thereby upregulated BIRC5 in HCC cells" (abstract) | Y |
| A26 | circANKRD52 knockdown represses melanoma growth and invasion (locus collision) | PMID:41173801 / 10.1111/jcmm.70909 | "Knockdown of circANKRD52 repressed the growth and invasion of melanoma cells in vitro and in vivo, whereas ectopic expression of circANKRD52 promoted these effects" (abstract) | Y |
| A27 | ci-ankrd52 forms R-loops more readily than its cognate pre-mRNA | PMID:34453665 / 10.1007/s11427-021-1993-6 | "One ciRNA, ciankrd52, shows a stronger ability of R-loop formation than that of its cognate pre-mRNA by maintaining a locally open RNA structure in vitro" (abstract) | Y |
| A17 | ci-ankrd52 (locus collision) regulates Pol II transcription | PMID:24035497 / 10.1016/j.molcel.2013.08.017 | "One abundant such RNA, ci-ankrd52, largely accumulates to its sites of transcription, associates with elongation Pol II machinery, and acts as a positive regulator of Pol II transcription." (abstract) | Y |
| A18 | PP6 has unrelated substrates (MEK) | PMID:33789117 / 10.1016/j.celrep.2021.108928 | "we identify PPP6C, a phosphatase frequently mutated or downregulated in melanoma, as a major MEK phosphatase in cells exhibiting oncogenic ERK pathway activation" (abstract) | Y |
| A19 | CK1A1 primes the AGO2 cluster in humans | PMID:37712432 / 10.15252/embr.202357250 | "In humans, we show that CK1A1 also acts as a priming kinase of this cluster on AGO2." (abstract) | Y |
| A20 | PP6 is the Aurora A T-loop phosphatase (another substrate) | PMID:21187329 / 10.1083/jcb.201008106 | "We find that the protein phosphatase 6 (PP6) holoenzyme is the major T-loop phosphatase for Aurora A, an essential mitotic kinase." (abstract) | Y |
| T21 | Wainberg 2021's definition of "uncharacterised" | PMID:33859415 / 10.1038/s41588-021-00840-z | "we first enumerated 1,321 uncharacterized genes from the UniProt database with a UniProt annotation score (a heuristic measure of protein annotation content) of ≤2" (full text) | Y |
| T22 | Wainberg 2021 predicted functions for 108 genes | PMID:33859415 | "predicts the functions of 108 uncharacterized genes" (abstract) | Y |
| P1 | All §1–§6 numbers | `reports/data/ANKRD52/bundle.md` (from `results/ledger/*`) | machine-generated; not retyped | Y |
| P2 | Meaning and calibration of p_cal | `results/holdout_eval/SUMMARY.md`; `results/ledger/M6_SUMMARY.md` | "precision@1 zavg_BEF 0.030 vs prior-only 0.000"; "slope 0.819"; "top 40 … 40 … 2.04 … 1.05–3.24" (Σ p_cal table row, pipes removed so the cell renders) | Y |
| P3 | Blinded-judging outcome | `results/m7/judge/analysis_main_genes.tsv` (row J071), `analysis_main.md`, `scores/J{1,2}_main3.tsv` | "J071	HGNC:26614	ANKRD52	top40	1	1.0	0.0	0	1.0	N1"; "N1: n 31, real supported 16, mean d 0.419" | Y |
| P4 | Recomputed ranks, profiles, line effects, matched control (†) | `results/m7/scratch_reports_trappc5/{ranks.py,ranks.tsv,profiles.py,lines.py,line_effects.tsv,ctrl2.py}` | scripts and outputs in the scratch directory | Y |
| P5 | Red-team-requested recomputations: lineage jackknife, outlier-line and screen-quality checks of the ANKRD52–AGO2 covariance; per-line ANKRD52/AGO2/AGO1 effects; TP53-matched control-line search | `results/m7/scratch_reports_trappc5/rt_checks.py` (run 2026-10-30) | script output in the scratch directory | Y |
| P6 | MED31 is also unflagged, with DEMETER2 measured and replicated and four supporting classes; 2,583 genes received a p_cal | `results/ledger/top40_primary.tsv`; `results/ledger/pcal_summary.json` | MED31 row: demote_A False, d2_measured True, d2_replicated True, supporting_classes PALG; "'in_support': 2583" | Y |

## Appendix B. Red-team review

- Reviewer / model / date: adversarial red-team agent (role `red_team`; did not write this report) / Claude Opus 5.5 / 2026-10-30
- **Verdict: ACCEPT WITH REVISIONS**
- Review text: the unedited review is at **`reports/redteam/ANKRD52.md`**; it is not reproduced or paraphrased here so that the reviewer's wording stands on its own.
- Lint result (claims without a verified source): **pass** — the reviewer independently re-resolved all 23 ledger rows through Europe PMC and re-matched every span; no failures. All project numbers re-derived exact, including the Holm reasoning on the orthogonal classes.

### Response to red team (point by point)

| # | Required fix | Response | Where |
|---|---|---|---|
| 1 | Take the locus collision seriously: cite PMID 33845641 and 41173801 (circANKRD52 sponges miRNAs, promotes proliferation) and PMID 34453665; say that the [A22] rescue addresses the reporter, not the fitness phenotype | **Accepted in full.** §8's bullet is rewritten and upgraded to "the most serious artefact hypothesis here", with three new verified rows (A25, A26, A27) and the explicit reporter-vs-fitness distinction; §9's third falsifier is reworded around degron-vs-cutting | §8, §9, Appendix A (A25–A27) |
| 2 | Promote the degron-vs-cutting / ci-ankrd52-knockdown contrast to Tier 1 | **Accepted.** It is now a Tier-1 row in the experiment plan with pre-declared outcomes, and the modality rationale is restated in §3 of that file | `ANKRD52_experiments.md` §4, §6 |
| 3 | Correct "the only gene in the primary top 10 with no failed check" (MED31 also has none, cleaner on two counts) | **Accepted.** §5 now names MED31 and states both respects in which it is cleaner (DEMETER2 measured and replicated; four supporting classes vs none) | §5, Appendix A row P6 |
| 4 | "Highest p_cal of the 4,271 scorable" → of the 2,583 scored | **Accepted.** Corrected in §0 with the breakdown (1,421 no p_cal, 133 upper-bound) | §0 |
| 5 | Re-scope the novelty claim: Shui 2023 already extracted and plotted DepMap effects for AGO2, ANKRD52, DICER1, XPO5, TNRC6A, DROSHA and PPP6C | **Accepted.** New verified row A24; §7 carries a "What it does not add — corrected after red-team review" paragraph that withdraws most of (iii) and part of (ii), leaving only the PP6-vs-miRNA contrast and the blind derivation; §11 repeats the withdrawal | §7, §11, Appendix A (A24) |
| 6 | Address the headroom problem (AGO2 KO near-neutral while ANKRD52 is not); name the escape being tested and power the rescue | **Accepted.** A dedicated bullet is now the third line of §0; the experiment plan states the per-line comparison (AGO2 −0.502/−0.332 vs ANKRD52 −0.685/−0.539 †), names AGO1 co-hyperphosphorylation [A7] and dominant-negative phospho-AGO2 as the two escapes, tests them explicitly, and replaces the "≥ 70% rescue" criterion with one scaled to the AGO2 baseline | §0, `ANKRD52_experiments.md` §1, §4 |
| 7 | Add a lineage jackknife / outlier-line check of the ANKRD52–AGO2 covariance | **Accepted.** New §4 bullet †: full r 0.367; 5% most extreme lines dropped r 0.290; 30-lineage jackknife r 0.347–0.377; best-screen subset r 0.416 (n 251) vs 0.359 | §4, Appendix A row P5 |
| 8 | Control-line TP53 mismatch (D1/D2 mutant, 253J-BV WT, CN NaN) | **Accepted.** The rule-selected control is kept but the mismatch is stated, the primary comparator is made isogenic (degron ± ligand, AAVS1 controls), and a TP53-mutant same-lineage cross-line control is added: 639V (ACH-000973), ANKRD52 −0.039, AGO2 −0.177, expression 4.45, ScreenNNMD −15.25 † | `ANKRD52_experiments.md` §2 |
| 9 | State the minimum detectable rescue for the decisive experiment | **Accepted.** Stated in the Tier-2 decisive row and in §7's decision rule | `ANKRD52_experiments.md` §4, §7 |

No point was rejected.
