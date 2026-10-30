# TRAPPC5 — candidate report (Template A)

All numbers are copied from `reports/data/TRAPPC5/bundle.md` (machine-generated from `results/ledger/*`), or, where marked †, from the descriptive recomputations in `results/m7/scratch_reports_trappc5/` (scripts `ranks.py`, `profiles.py`, `lines.py`, `ctrl.py`, `ctrl2.py`). Literature sentences carry an Appendix-A key; every key is verified (PMID resolves through the Europe PMC API and the verbatim span occurs in the retrieved abstract or full text; `verify.py`, `verify_out.json`). Search date 2026-10-30.

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** TRAPPC5 is a stable subunit of the human TRAPP tethering complexes and is required for Golgi vesicle transport; in our data its requirement tracks the TRAPPIII-specific arm (TRAPPC8/C11/C12/C13) and not the TRAPPII-specific arm (TRAPPC9/C10). Relationship type **a** (stable subunit) for TRAPP; the TRAPPIII-vs-TRAPPII refinement is the part that is new here.
- **Confidence:** p_cal = **0.1140** [95% CI 0.000–0.274] — the expected probability that the predicted GO term (GO:0048193 Golgi vesicle transport) is confirmed by a later D1-evidence annotation; it is *not* the probability that the relationship type (subunit) is right, and it is not a probability about the TRAPPIII refinement. Tier: none (the top 40 is a p_cal fill; no gene reached Tier A or B).
- **Strongest reason to doubt:** the module call is a rediscovery of textbook TRAPP membership (UniProt already lists TRAPPC5 as a TRAPP component [L1]), so the only part that is not already in the databases — the TRAPPIII-leaning dependency — rests on correlation between Chronos profiles, and TRAPPII subunits are near-dispensable for proliferation in DepMap lines (TRAPPC9 mean −0.145, TRAPPC10 −0.029 †), which alone can produce the asymmetry without any difference in TRAPPC5's complex usage.
- **First experiment:** degron depletion of TRAPPC5 in two dependent lines with RUSH ER→Golgi cargo release read out against a matched-essentiality control gene (NDUFAF8) and against TRAPPC8 (TRAPPIII) vs TRAPPC9 (TRAPPII) depletion; time ~10–14 weeks; approximate cost £35–50k (details in `reports/TRAPPC5_experiments.md`).
- Cancer-line essentiality is not organismal function: dependency in DepMap lines says the gene is needed for proliferation there, not what it does in the organism.

## Definitions used in this template

**Relationship type (DESIGN §4.4).**

| Code | Type | Claim allowed |
|---|---|---|
| a | Stable subunit | Only with physical, co-abundance or structural support. |
| b | Assembly or maturation factor | "Required for assembly or maturation of M". |
| c | Supplier or client | Transporter, enzyme, or substrate of an import or insertion machinery that co-varies with M. |
| d | Pathway member | "Acts in pathway M". |
| e | Lineage or transcriptional programme | Regulatory co-dependency; not a function call. |

**Novelty class (DESIGN §1.5, §6.3).** N1 established; N2 partial or indirect; N3 no functional literature. Assigned by agent L blind to our prediction.

---

## 1. Header

- Symbol: TRAPPC5 | HGNC ID: HGNC:23067 | previous symbols: — | aliases: MGC52424 / TRS31 | UniProt: Q8IUR0 | band: 19p13.2 (Ensembl ENSG00000181029; Entrez 126003)
- D1 / D2 / D3: True / False (UniProt annotation score 4) / True (D3_pubmed True, D3_tdark True; focused PMIDs 2, all PMIDs 50; TDL Tdark) | curation-lag audit flag: not in the audit sample
- Stratum (§1.4): family **other**; expression **expressed** (log2(TPM+1) ≥ 1 in 99.7% of lines); informativeness tertile **high**; core **True**
- Hypothesis (one sentence): TRAPPC5 functions in Golgi vesicle transport as a subunit of the TRAPP tethering complexes, and its proliferation requirement co-varies with the TRAPPIII-specific subunits rather than the TRAPPII-specific ones.
- Relationship type: **a** (script rule and clean-first list agree: P and A classes support; complex-like V1′ label CP:CPX-4750)
- Novelty class: **N2** (search date 2026-10-30) — complex membership is in UniProt and in the structural literature; gene-specific functional work on TRAPPC5 itself was not retrieved by agent L.
- LLM-recall-probe flag (§6.2): **known**; probe answer logged at `results/m7/recall_probe_90.tsv` — "Core subunit of the TRAPP complexes, which tether ER-to-Golgi vesicles and act as a Rab1 GEF."; matches network top term: **yes**. The prediction is therefore **not independent of background knowledge**: a tool-less LLM already states the module.
- Calibrated probability p_cal: **0.1140** [95% CI 0.000–0.274, cluster bootstrap, 2000 refits]; calibration family **ER_Golgi_secretory_lipid**; covariates inside H's 5th–95th percentile: **yes** (in_support; top-K mean zavg 10.944, R 0.512, coverage pct 0.786, size pct 0.800)
- Tier: none (p_cal fill; 0 Tier A and 0 Tier B genes in M6); rank in primary top 40: **4**; top-40-only demotion label: **TP53**

**What p_cal means** (`results/holdout_eval/SUMMARY.md`, `results/ledger/M6_SUMMARY.md`): on the temporal hold-out H, precision@1 of the method was 0.030 (95% CI 0.018–0.043) against 0.000 for the prior-only ranker and 0.005 for the matched-gene null; the §3.7 model fitted on H has out-of-fold slope 0.819 (Wald 0.512–1.127), intercept −0.006, Brier 0.0294, c-statistic 0.855. p_cal is the model's estimate of the probability that *this top term* is later confirmed by a D1-evidence annotation (~8-year horizon). Σp_cal over the whole top 40 is 2.04 (95% CI 1.05–3.24) — i.e. about two of the forty top-term calls are expected to be confirmed by annotation. The in-support maximum over all U genes is 0.141, so no gene could reach the Tier-B threshold of 0.3.

## 2. The protein

- Domains (InterPro): IPR024096; IPR016696; IPR007194; Pfam PF04051; length 188 aa. TM / signal peptide / MTS: none (UniProt keywords; not multi-pass). AlphaFold pLDDT: **not retrieved — no AlphaFold per-residue file is held in the project**. Deepest orthologue: budding-yeast Trs31 [T25]; UniProt places TRAPPC5 in the "TRAPP small subunits family, BET3 subfamily".
- UniProt function (verbatim): "May play a role in vesicular transport from endoplasmic reticulum to Golgi." [L1]; subunit (verbatim): "Component of the multisubunit TRAPP (transport protein particle) complex, which includes at least TRAPPC2, TRAPPC2L, TRAPPC3, TRAPPC3L, TRAPPC4, TRAPPC5, TRAPPC8, TRAPPC9, TRAPPC10, TRAPPC11 and TRAPPC12" [L2]; subcellular location: Golgi apparatus, cis-Golgi network {ECO:0000250}; Endoplasmic reticulum {ECO:0000250} [L3].
- Class H (homology) evidence: homology (IBA/ISO) to the predicted term is present (reported only, §5.1).
- Source keys: L1, L2, L3, T25, T26 (all in Appendix A).

## 3. Dependency profile

- Mean / SD of Chronos effect: **−0.724 / 0.238**; median −0.719; 5th percentile −1.110; min −1.896; fraction of lines < −0.5: **0.8582** (1168 / 1361); common-essential (< −0.5 in ≥ 90% of lines): **no**; NaN fraction 0.0000.
- Expression across lines: log2(TPM+1) ≥ 1 in 99.7% and ≥ 2 in 98.3% of lines; median 4.94. Dependency-vs-expression scatter: `reports/data/TRAPPC5/fig_profile.png` panel (b); Spearman ρ(effect, own expression) = −0.014 (n = 1292).
- Lineage enrichment (descriptive, Mann–Whitney vs other lines): Cervix n 18, mean −0.824, p 0.1102; Bladder/Urinary Tract n 34, −0.789, p 0.0835; Myeloid n 45, −0.781, p 0.0749. No lineage is significant after the leave-out test (below).
- Split-half assessability: R(g) = **0.512**; null mean 0.006, max 0.168 over 200 matched genes; empirical p **0.0050**; RBO 0.646 (p 0.0050); assessable: **yes**.
- Figure 1 (profile panel): `reports/data/TRAPPC5/fig_profile.png` — (a) TRAPPC5 vs TRAPPC3 across 1361 lines (Pearson r = 0.27, Spearman ρ = 0.18), (b) effect vs own expression, with the chosen lines (D1, D2) and control (C) marked.

## 4. Neighbourhood

Top-10 partners (`results/ledger/u_partners.tsv`; GLS rank = rank in TRAPPC5's GLS row after the §3.1 exclusions):

| partner | zavg_BEF | z_B / z_E / z_F | GLS rank | partner function and essentiality | chromosome and distance | paralogue / shared-guide flag | hu.MAP-train |
|---|---|---|---|---|---|---|---|
| TRAPPC3 | 21.89 | 36.0 / 20.0 / 9.7 | 1 | TRAPP core (BET3); common-essential, mean −1.72, 99.4% of lines < −0.5 | 1p34.3; different chromosome | no | gene yes / pair no |
| TRAPPC1 | 21.19 | 35.3 / 19.7 / 8.6 | 2 | TRAPP core (BET5); common-essential, mean −1.30, 98.7% | 17p13.1; different chr | paralogue of another partner | gene yes / pair no |
| TRAPPC11 | 20.82 | 35.7 / 19.7 / 7.1 | 4 | **TRAPPIII-specific**; common-essential, mean −0.94, 93.7%; annotated to the predicted term | 4q35.1; different chr | no | no / pair no |
| TRAPPC4 | 20.10 | 34.0 / 19.1 / 7.2 | 3 | TRAPP core (TRS23); common-essential, mean −1.00, 96.5%; in term | 11q23.3; different chr | paralogue of another partner | gene yes / pair no |
| TRAPPC2L | 16.22 | 27.3 / 16.9 / 4.4 | 23 | TRAPP core (Tca17); not essential, mean −0.25, 13.3% | 16q24.3; different chr | no | gene yes / pair no |
| TRAPPC13 | 16.04 | 26.2 / 16.1 / 5.9 | 5 | **TRAPPIII-specific**; not essential, mean −0.19, 10.2% | 5q12.3; different chr | no | gene yes / pair yes |
| TRAPPC8 | 15.73 | 25.7 / 17.5 / 4.1 | 173 | **TRAPPIII-specific** (Trs85); common-essential, mean −1.39, 97.1% | 18q12.1; different chr | no | no / pair no |
| TRAPPC12 | 12.01 | 20.6 / 12.5 / 2.9 | 692 | **TRAPPIII-specific**; not essential, mean 0.01, 0.4%; in term | 2p25.3; different chr | no | no / pair no |
| RAB1A | 11.62 | 19.3 / 11.6 / 3.9 | 150 | TRAPP substrate GTPase; not essential, mean −0.19, 7.0%; in term | 2p14; different chr | paralogue of another partner | no / pair no |
| GOSR2 | 11.13 | 19.2 / 12.4 / 1.8 | 2911 | Golgi SNARE; common-essential, mean −1.00, 97.1%; in term | 17q21.32; different chr | no | no / pair no |

Shared-sgRNA / per-guide checks are not possible (guide-level data unavailable; recorded in DESIGN §4.3).

Figure 2 (neighbourhood network): `reports/data/TRAPPC5/fig_network.png` — 55 edges with zavg_BEF ≥ 3 among the 11 nodes, 35 of them with physical support in an admitted P source.

Top 3 terms (R1, K = 25):

| term | name | S | p_emp | hypergeometric p (descriptive) | leave-one-partner-out stability |
|---|---|---|---|---|---|
| GO:0048193 | Golgi vesicle transport | 106.184 | 0.0020 | 0.0000 | rank kept after 8 of 9 single-partner removals |
| GO:0007030 | Golgi organization | 91.432 | 0.0020 | 0.0000 | 6 of 8 |
| GO:0006888 | ER to Golgi vesicle-mediated transport | 83.242 | 0.0020 | 0.0000 | 6 of 6 |

Second-ranked term: **GO:0007030 Golgi organization**. Most specific term in the top 5: GO:0007030. V1 label GO:0099023 vesicle tethering complex; V1′ label **CP:CPX-4750 TRAPP III complex, TRAPPC2 variant** (7 supporting partners).

**Recomputed neighbourhood detail † (`ranks.py`, full zavg_BEF row, background genes, no exclusions).** Ranks of TRAPP genes in TRAPPC5's row: TRAPPC3 1, TRAPPC1 2, TRAPPC11 3, TRAPPC4 4, TRAPPC2L 5, TRAPPC13 6, TRAPPC8 7, TRAPPC12 8, RAB1A 9, RAB1B 12, **TRAPPC10 134, TRAPPC14 4810, TRAPPC6B 3599, TRAPPC3L 12531, TBC1D14 8143, TRAPPC9 14766, TRAPPC6A 16010**. Chronos means over the 1361 tool lines †: TRAPPC8 −1.390 (97.1% of lines < −0.5), TRAPPC11 −0.941 (93.7%), TRAPPC13 −0.191, TRAPPC12 +0.014 versus **TRAPPC9 −0.145 (1.5%) and TRAPPC10 −0.029 (1.5%)**; TRAPPC6A −0.125, TRAPPC6B −0.087. The TRAPPII-specific subunits are thus neither co-essential with TRAPPC5 nor dependencies in their own right in these lines, while three of four TRAPPIII-specific subunits are in TRAPPC5's top 8.

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | pass | g on 19p; 0 of the top-10 partners on g's chromosome |
| Bidirectional-promoter / overlapping / readthrough partners | pass | 0 of 9 supporting partners flagged (strand-agnostic superset rule, DEVIATIONS 2026-10-29) |
| Copy-number co-amplification | pass | 0 of 9 flagged; max \|r\| 0.06 (TRAPPC11 0.05, TRAPPC4 −0.06, TRAPPC12 −0.00, RAB1A −0.02, GOSR2 0.03, RAB1B 0.04, PREB −0.05, ARFRP1 −0.01, COG1 0.02) |
| Hub-driven call (> 50% of S from top-1% in-degree) | pass | hub share 0.00; 0 hub partners; g's own in-degree 34 (not a hub) |
| Lineage leave-out | pass | Cervix (18 lines, mean −0.824) removed, tool refitted: top term still GO:0048193; N(g) overlap 0.88 |
| K = 10 / 50 | pass | same top term at both K |
| Dependency vs own expression; TF / lineage-marker enrichment | pass | ρ = −0.014 (n 1292); 0 TFs in N(g), OR 0.24, p 1.0000, q 1.0000 |
| TP53 / p53-axis correlation | **fail (flag)** | 902 mutant vs 459 WT lines; Mann–Whitney p 0.0016, BH q 0.0062; **median difference (mut − WT) = −0.039**, i.e. a 0.04-Chronos shift against a gene SD of 0.238 — statistically detectable in 1361 lines, biologically negligible. Under DESIGN §4.3 this caps the gene at Tier B; with 0 Tier A/B genes the cap is inert, and the primary top 40 is pure p_cal order (DEVIATIONS 2026-10-30). |
| DEMETER2 replication | not measured | 0 supporting partners present in DEMETER2 |
| Shared-sgRNA and per-guide check | not possible (guide maps / guide-level data not available) | recorded |
| GLS network top term (descriptive) | different | GO:0006888 ER-to-Golgi vesicle-mediated transport — a descendant of the called term, not a conflict |

## 6. Orthogonal evidence matrix (four states)

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | BioPlex 3.0 / OpenCell / BioGRID-LTP / STRING-exp (one source group) + Human Cell Map SAINT | **supports** | edges to TRAPPC3, TRAPPC1, TRAPPC11, TRAPPC4, TRAPPC2L, TRAPPC13, TRAPPC8, TRAPPC12 in the P group; 8 edges to the 177 term members vs null mean 0.736; HCM-SAINT: g has 0 interactors | P_group 0.0010; HCM_SAINT 1.0000; class (Simes) **0.0020** | no (ER/Golgi diagnostic class is L) |
| A co-abundance | ProteomeHD; CCLE proteomics | **supports** | CCLE r: TRAPPC11 0.68, TRAPPC12 0.65, TRAPPC3 0.62, TRAPPC4 0.60, TRAPPC8 0.58 (all 100th row percentile) | ProteomeHD 0.0010; CCLE 0.0010; class **0.0010** | no |
| L localisation | HPA v25.1 | **supports** | HPA reliability Approved, main location **Vesicles** → vocabulary "vesicles/endosome/lysosome"; 0.338 of term members share a compartment vs null 0.166 | **0.0010** | **yes — this is the diagnostic class for ER_Golgi_secretory_lipid, and it supports** |
| G perturbation phenotype | Perturb-seq K562 GW / K562 essential / RPE1 essential | **supports** | RPE1: TRAPPC11 r 0.93, TRAPPC8 0.89, TRAPPC3 0.88, TRAPPC1 0.86, STX5 0.90, BET1 0.87 | 0.0010 / 0.0010 / 0.0010; class **0.0010** | no |
| S structure | Burke 2023 AF2 | **no support** | pair-level: TRAPPC3 pDockQ 0.680, TRAPPC2B 0.625, TRAPPC2 0.614, TRAPPC4 0.451 (4 of 13 modelled pairs ≥ 0.23); the class test fails only because the 3 measured *term members* already have a null mean of 0.908 | 0.7013 | no |
| H homology | orthologue IBA/ISO | reported only | IBA/ISO annotation to the term present | reported only | — |

Holm across the four measured classes at α = 0.05: P, A, L, G all support; diagnostic class (L) measured and supporting; **no contradiction** (HPA Vesicles is compatible with Golgi/ER; MitoCarta assessed and not listed; OpenCell not tagged; Human Cell Map neither prey nor bait); g is not multi-localised.

Reported but not counted (not independent of DepMap or of the training set): hu.MAP 3.0 places TRAPPC5 in complex huMAP3_04127.1 (confidence 1) with TRAPPC1/2L/3/4/6A/6B/8/9/10/11/12/13/14 and TBC1D14 †; DEMETER2 not measured; Predictomes gives TRAPPC3–TRAPPC5 SPOC 0.998 and TRAPPC4–TRAPPC5 0.958 † (Predictomes uses DepMap Chronos as a feature, so it is circular here).

## 7. Literature (blinded step, then synthesis)

**Blinded summary of agent L's items** (`results/m7/L/HGNC_23067.md`, 5 items, N2): two UniProt mentions (ER-to-Golgi role; TRAPP membership), one complex-level mention from the 2011 identification of TRAPPC11/TRAPPC12 (gene not named in the abstract), one review title on TRAPP as Rab1/Rab11 exchange factors, and one functional item — a hepatocellular-carcinoma paper reporting that the gene promotes proliferation, migration, invasion and EMT. Agent L's own summary: "Gene-specific mechanistic or structural data on TRAPPC5 were not retrieved."

**Blinded verdicts** (`results/m7/judge/`, packet J074): real statement **+1**; decoys **0, 0, 0** (endosomal transport / Commander complex; steroid metabolic process / MitoCarta metals-and-cofactors; lipid transport / TREX-2). Judges J1 and J2 agreed on all four slots (no adjudication needed); d = real − mean(decoy) = **1.0**. Context: over the primary top 40, 18 of 40 real statements were supported against 3 of 120 decoys, exact one-sided sign-flip **p = 0.0002174**, judge κ = 0.975 over 360 statements.

**Unblinded synthesis.** TRAPPC5 is one of the seven conserved core subunits shared by the metazoan TRAPPII and TRAPPIII complexes [T26], and the structural literature places it precisely: in the cryo-EM structure of metazoan TRAPPIII, TRAPPC5 and TRAPPC2 bind one of the two TRAPPC3 copies while TRAPPC6 and TRAPPC2L bind the other [T4], and the TRAPPIII-specific arm subunit TRAPPC8 contacts density formed by TRAPPC3b together with TRAPPC5 [T5], with TRAPPC8 and TRAPPC11 holding the catalytic core "like a pair of tongs" [T3]. Functionally, the yeast orthologue Trs31 does not touch the GTPase directly but "allosterically regulates the TRAPPI interface with Ypt1p" [T8]; in the human TRAPPII complex, hydrogen–deuterium exchange on Rab binding changes in TRAPPC2L, TRAPPC4 and TRAPPC5 only [T6], and the TRAPPC5 regions involved are not in direct Rab contact but contact the TRAPPC4 C-terminus, "likely highlighting an allosteric conformational change that accompanies Rab binding" [T7]. The complexes themselves are functionally split: both metazoan complexes activate Rab1 and only TRAPPII also activates Rab11 [T9], and the most recent yeast work assigns TRAPPI/TRAPPII to early/late Golgi secretion and restricts TRAPPIII's Ypt1 activation to autophagy [T10]; subcomplex composition, not core composition, is what directs TRAPP to one route or the other [T11]. Human genetics supports the core/arm distinction indirectly: TRAPPC11 patient cells show defective ER–Golgi transport and hypoglycosylation [T17], whereas for TRAPPC5 a 2024 review states "There are no reported pathogenic variants in TRAPPC5 in ClinVar" [T14] and "there are no reported disease associations with TRAPPC5" [T15]. Humanised-yeast work shows TRAPPC5 is among the subunits that cannot replace their yeast counterpart, singly [T13] or in a partly humanised core where "Attempts to replace yeast TRS31 with human C5 were unsuccessful" [T12] — so no genetic assay for human TRAPPC5 function currently exists in yeast. Direct evidence on human TRAPPC5 loss of function is confined to one cancer-biology paper [T16]; a 2024 review describes TRAPPC5 as essential in yeast and human, interacting closely with TRAPPC3 and stabilising TRAPPC8 binding to the core [T15b], but that is a review assertion, not primary data in the retrieved text.

**Closest prior publication and what co-essentiality adds.** The closest prior statements are the cryo-EM architecture [T3, T4, T5] and the human TRAPPII HDX study [T6, T7]: both already place TRAPPC5 in the core, adjacent to TRAPPC3b and to the TRAPPC8 arm. Co-essentiality adds nothing to the membership call (hence N2 and the "known" recall-probe flag) and adds one loss-of-function statement they do not make: across 1361 cancer lines the *requirement* for TRAPPC5 co-varies with the TRAPPIII arm (TRAPPC11 rank 3, TRAPPC13 rank 6, TRAPPC8 rank 7, TRAPPC12 rank 8 †) and not with the TRAPPII arm (TRAPPC9 rank 14766, TRAPPC10 rank 134 †), while TRAPPC9 and TRAPPC10 are themselves dispensable (mean −0.145 and −0.029 †). Read with [T10] and [T11], this is a testable, cell-autonomous prediction about which TRAPP subtype carries the proliferation-relevant load in human cells — something the structural and yeast work leaves open (the structure is of a *Drosophila* complex [T3]; the complex-specificity assignment [T10] is from yeast). The second open point our data speak to is the quantitative spread within the core: TRAPPC3 (−1.72), TRAPPC1 (−1.30), TRAPPC4 (−1.00) and TRAPPC8 (−1.39) are far stronger dependencies than TRAPPC5 (−0.724), and TRAPPC2L (−0.25), TRAPPC6A (−0.125) and TRAPPC6B (−0.087) are nearly dispensable †, which is not what a single obligate octamer would predict and matches [T2]'s conclusion that the mammalian fundamental unit differs from the yeast one.

**Prior prediction lists containing this gene.** Wainberg 2021 defined uncharacterised genes as UniProt annotation score ≤ 2 [T21] and predicted functions for 108 such genes [T22]; TRAPPC5's annotation score is 4, so it is outside that set and is not one of the 108. hu.MAP 3.0 contains TRAPPC5 in a 15-gene TRAPP complex (confidence 1) †, i.e. hu.MAP already makes the complex call — this is why hu.MAP is reported, not counted (TRAPPC5 is a hu.MAP-train gene; the TRAPPC5–partner pairs are not training positives). Replogle 2022: TRAPPC5 does not appear in the annotated embedding-coordinates file that carries the cluster labels †, although the gene is measured in all three Perturb-seq pseudo-bulk datasets used here (§6). Predictomes: present (TRAPPC3–TRAPPC5 SPOC 0.998 †) but circular.

**Post-freeze (after 2026-10-29) papers confirming the prediction:** none found as of 2026-10-30.

## 8. Alternative explanations

- *Proximity / locus artefacts.* Excluded by construction (same-arm, paralogue) and by the per-partner checks: 0 of 9 supporting partners carry a locus or CN flag, and all top-10 partners are on other chromosomes (§5).
- *Hub-driven enrichment.* Hub share 0.00; the signal comes from eight named TRAPP genes, not from promiscuous high-in-degree nodes.
- *Lineage / expression programme.* Lineage leave-out keeps the top term; ρ(effect, expression) = −0.014; no TF enrichment. Type **e** is excluded.
- *TP53 axis.* The only failed check. The effect size (median difference −0.039 Chronos units between 902 mutant and 459 WT lines, against SD 0.238) cannot generate a correlation structure of z ≈ 21 with eight TRAPP genes; and the partners are not p53-axis genes. The flag is a power artefact of 1361 lines, and it caps the tier rather than contradicting the call.
- *Curation lag / circularity.* The module call is already in UniProt [L2] and hu.MAP, and the recall probe recognised the gene — this is a rediscovery, not a discovery. It is reported as validation of the pipeline, and no novelty claim is made for the module term.
- **Strongest competing biological hypothesis.** The TRAPPIII-leaning dependency may be an artefact of *differential essentiality of the arms* rather than of differential complex usage: if the TRAPPII-specific subunits are dispensable for proliferation in these lines for a reason unrelated to TRAPPC5 (e.g. SH3BP5-family GEFs supplying Rab11 activation in parallel, as in [T9]'s *parcas* result), then TRAPPC5 would co-vary with the TRAPPIII arm regardless of how its molecules are distributed between the two complexes. A second competing hypothesis is that TRAPPC5's correlation with TRAPPC8/C11 reflects complex *stability* (loss of TRAPPC5 destabilises the core and so phenocopies arm loss) rather than a route-specific function. The experiment that separates these is in `reports/TRAPPC5_experiments.md` §6: BN-PAGE/SEC of TRAPPII vs TRAPPIII assemblies and TRAPPC9-vs-TRAPPC8 epistasis after acute TRAPPC5 depletion, with Rab1 and Rab11 activation measured separately.

## 9. Falsifying observations

(These were drafted from the machine bundle, §1–§5 only. Honest note on ordering: unlike the template's intent, the report author had already read the literature for this gene before writing the rest of the report; the statements below are experimental outcomes and do not depend on §6/§7.)

1. Acute depletion of TRAPPC5 in both dependent lines leaves ER→Golgi cargo transport (RUSH) and Golgi morphology indistinguishable from the matched-essentiality control gene at the same growth inhibition — i.e. the proliferation defect is general sickness, not a Golgi-transport defect.
2. Tagged TRAPPC5 fails to co-purify TRAPP subunits (IP-MS/BN-PAGE), or TRAPP subunit levels and assembly are unchanged after TRAPPC5 loss — which would refute the type-**a** (stable subunit) call and demand a weaker claim.
3. TRAPPC5 depletion impairs Rab11-dependent (TRAPPII) transport at least as much as Rab1-dependent (TRAPPIII/early) transport, and TRAPPC9 co-depletion is epistatic to TRAPPC5 — which would refute the TRAPPIII-leaning refinement that is the only part of this call not already in the databases.

## 10. Experiments

See `reports/TRAPPC5_experiments.md` (Template B).

## 11. Novelty and external benchmarks

The module call (Golgi vesicle transport; TRAPP) is a **rediscovery**: it is in UniProt [L1, L2], in hu.MAP 3.0 †, in the structural literature [T3, T4] and in the tool-less LLM recall probe. No novelty is claimed for it. TRAPPC5 is not in Wainberg 2021's 108 predictions (annotation score 4 vs their ≤ 2 cut-off [T21, T22]) and is absent from the Replogle 2022 annotated-embedding cluster file †. What is **not found in the literature as of 2026-10-30** is (i) a loss-of-function comparison that places human TRAPPC5's proliferation requirement with the TRAPPIII-specific arm rather than the TRAPPII arm, and (ii) any human TRAPPC5-specific functional or disease study beyond the single HCC paper [T16] — the TRAPPopathies review states there are no reported TRAPPC5 disease associations [T15] and no ClinVar pathogenic variants [T14]. The gene therefore illustrates curation lag within a well-studied complex (D1 true, UniProt annotation score 4, TDL Tdark, 2 focused PMIDs) rather than genuine functional darkness.

## Appendix A. Evidence ledger

Verification protocol: each PMID was resolved through the Europe PMC REST API (`search?query=EXT_ID:<pmid> AND SRC:MED`, resultType core); the DOI returned is listed; the verbatim span was then searched in the retrieved abstract and, where a PMC full text was fetched (Europe PMC `fullTextXML` or the NCBI BioC endpoint), in that full text. Script and output: `results/m7/scratch_reports_trappc5/verify.py`, `claims.json`, `verify_out.json`. All rows below are verified **Y**; no unverified claim is cited anywhere in this report.

| Key | Claim | Source (PMID / DOI / file) | Verbatim span | Verified |
|---|---|---|---|---|
| L1 | UniProt's function statement for TRAPPC5 | UniProt Q8IUR0 (`reports/data/TRAPPC5/bundle.md` §8; REST copy `results/m7/scratch_reports_trappc5/uniprot_Q8IUR0.json`, retrieved 2026-10-30) | "FUNCTION: May play a role in vesicular transport from endoplasmic reticulum to Golgi." | Y |
| L2 | UniProt lists TRAPPC5 as a TRAPP component | UniProt Q8IUR0, SUBUNIT (ECO:0000269, PubMed 21525244) | "Component of the multisubunit TRAPP (transport protein particle) complex, which includes at least TRAPPC2, TRAPPC2L, TRAPPC3, TRAPPC3L, TRAPPC4, TRAPPC5, TRAPPC8, TRAPPC9, TRAPPC10, TRAPPC11 and TRAPPC12" | Y |
| L3 | UniProt subcellular location (inferred by similarity) | UniProt Q8IUR0 | "SUBCELLULAR LOCATION: Golgi apparatus, cis-Golgi network {ECO:0000250}. Endoplasmic reticulum {ECO:0000250}." | Y |
| T1 | TRAPPC11/TRAPPC12 are human TRAPP components acting early in ER-to-Golgi traffic | PMID:21525244 / 10.1091/mbc.e10-11-0873 | "we demonstrate that the novel proteins are bona fide components of human TRAPP and implicate C4orf41 and TTC-15 (which we call TRAPPC11 and TRAPPC12, respectively) in ER-to-Golgi trafficking at a very early stage" (abstract) | Y |
| T2 | Mammalian TRAPP's fundamental unit differs from yeast TRAPP I | PMID:21525244 | "Our data are consistent with the absence of a TRAPP I-equivalent complex in mammalian cells" (abstract) | Y |
| T3 | TRAPPIII architecture: C8/C11 arms clamp the core | PMID:34018214 / 10.15252/embj.2020107608 | "The TRAPPIII-specific subunits TRAPPC8 and TRAPPC11 hold the catalytic core like a pair of tongs, with TRAPPC12 and TRAPPC13 positioned at the joint between them." (abstract) | Y |
| T4 | TRAPPC5's position in the core octamer | PMID:34018214 | "TRAPPC5 and TRAPPC2 bind one TRAPPC3 (C3b), and TRAPPC6 and TRAPPC2L bind the other (C3a)" (full text) | Y |
| T5 | TRAPPC5 lies at the TRAPPC8-arm attachment point | PMID:34018214 | "TRAPPC8 is linked to density formed by the connection of the first two α‐helices of TRAPPC3b and TRAPPC5" (full text) | Y |
| T6 | Rab binding changes HDX in TRAPPC2L, TRAPPC4 and TRAPPC5 only | PMID:33277614 / 10.1038/s42003-020-01459-2 | "were identified in the TRAPPC2L, TRAPPC4, and TRAPPC5 in the presence of Rab GTPases with no other changes in other TRAPP subunits" (full text) | Y |
| T7 | TRAPPC5's Rab-responsive regions are allosteric, not contact | PMID:33277614 | "Regions in TRAPPC5 with decreased exchange are not proposed to be in direct contact with Rab substrates, however, these regions are in contact with the c-terminal region of TRAPPC4, likely highlighting an allosteric conformational change that accompanies Rab binding" (full text) | Y |
| T8 | Yeast Trs31 acts allosterically on the Ypt1 interface | PMID:18585354 / 10.1016/j.cell.2008.04.049 | "The Trs31p subunit does not interact directly with the GTPase but allosterically regulates the TRAPPI interface with Ypt1p." (abstract) | Y |
| T9 | Metazoan TRAPPII additionally activates Rab11 | PMID:29273580 / 10.1083/jcb.201705068 | "both activate Rab1, whereas one, TRAPPII, also activates Rab11" (abstract) | Y |
| T10 | TRAPPIII's Ypt1 activation is restricted to autophagy (yeast) | PMID:41801064 / 10.1083/jcb.202507166 | "Thus, TRAPPI and TRAPPII activate Ypt1 and Ypt31 in early- and late-Golgi, respectively, ascribing TRAPPIII in Ypt1 activation only in autophagy." (abstract) | Y |
| T11 | Subcomplex recruitment, not the core, decides TRAPP's route | PMID:42483769 / 10.1242/jcs.264822 | "Both are recruited to core TRAPP by Tca17, which therefore plays a crucial role by determining the physiological role of TRAPP." (abstract) | Y |
| T12 | Human TRAPPC5 cannot replace yeast TRS31 even in a humanised core | PMID:42738849 / 10.3390/cells15171555 | "Attempts to replace yeast TRS31 with human C5 were unsuccessful, as evidenced by the lack of viable colonies following transformation on G418 plates" (full text) | Y |
| T13 | Which human TRAPP subunits complement in yeast | PMID:39273027 / 10.3390/cells13171457 | "core yeast subunits were humanized by replacing them with their human orthologs, and TRAPPC1, TRAPPC2, TRAPPC2L, TRAPPC6A, and TRAPPC6B were found to successfully replace their yeast counterparts" (abstract) | Y |
| T14 | No ClinVar pathogenic TRAPPC5 variants | PMID:39769094 / 10.3390/ijms252413329 | "There are no reported pathogenic variants in TRAPPC5 in ClinVar." (full text) | Y |
| T15 | No reported TRAPPC5 disease associations | PMID:39769094 | "However, there are no reported disease associations with TRAPPC5." (full text) | Y |
| T15b | Review assertion on TRAPPC5's role in the core | PMID:39769094 | "TRAPPC5 is another core protein of the TRAPP complex and is essential in yeast and in humans. It has a close interaction with TRAPPC3 and stabilizes the binding of TRAPPC8 to the core." (full text; review-level, not primary data) | Y |
| T16 | The one functional TRAPPC5 loss/gain-of-function study | PMID:35425722 / 10.2147/jhc.s352948 | "TRAPPC5 was highly expressed in HCC tissues, and it could enhance the proliferation, migration, invasion and epithelial-mesenchymal transition (EMT) process of HCC cells." (abstract) | Y |
| T17 | TRAPPC11 deficiency gives ER–Golgi transport and glycosylation defects | PMID:38564972 / 10.1016/j.ymgme.2024.108469 | "membrane trafficking assays in our patient showed defective abnormal endoplasmic reticulum-Golgi transport as well as decreased expression of LAMP2, and ICAM-1 glycoproteins" (abstract) | Y |
| T18 | RUSH assay principle (Tier-1 readout) | PMID:22406856 / 10.1038/nmeth.1928 | "Biotin addition causes a synchronous release of the reporter from the hook." (abstract) | Y |
| T19 | TRAPPC13 loss reduces Rab1a/Rab1b activity and impairs autophagy | PMID:28536105 / 10.1242/jcs.199521 | "TRAPPC13 depletion reduces Rab1a and Rab1b activity, impairs autophagy" (abstract) | Y |
| T20 | TRAPP controls COPII recruitment and ER export under stress | PMID:31429971 / 10.15252/embj.2019101704 | "The TRAPP complex associates with and drives the recruitment of the COPII coat to stress granules (SGs) leading to vesiculation of the Golgi complex and arrest of ER export." (abstract) | Y |
| T21 | Wainberg 2021's definition of "uncharacterised" | PMID:33859415 / 10.1038/s41588-021-00840-z | "we first enumerated 1,321 uncharacterized genes from the UniProt database with a UniProt annotation score (a heuristic measure of protein annotation content) of ≤2" (full text) | Y |
| T22 | Wainberg 2021 predicted functions for 108 genes | PMID:33859415 | "predicts the functions of 108 uncharacterized genes" (abstract) | Y |
| T23 | TRAPP core architecture is a flat, elongated particle | PMID:17110339 / 10.1016/j.cell.2006.09.029 | "The complex is organized through lateral juxtaposition of the subunits into a flat and elongated particle." (abstract) | Y |
| T24 | TRAPPIII-specific subunits have roles beyond ER–Golgi (ciliogenesis) | PMID:32258032 / 10.3389/fcell.2020.00148 | "We found a ciliopathy protein, oral-facial-digital syndrome 1 (OFD1), interacting with the TRAPPIII-specific subunits TRAPPC8 and TRAPPC12." (abstract) | Y |
| T25 | TRAPPC5's yeast orthologue is Trs31 | PMID:39273027 | "TRAPPC5 (Trs31p ortholog)" (full text) | Y |
| T26 | TRAPPC5 is in the core shared by TRAPPII and TRAPPIII | PMID:42738849 | "Both of these complexes share a conserved common core of subunits (TRAPPC1, TRAPPC2, TRAPPC2L, TRAPPC3, TRAPPC4, TRAPPC5, and TRAPPC6A/B)" (full text) | Y |
| P1 | All §1–§6 numbers | `reports/data/TRAPPC5/bundle.md` (from `results/ledger/u_predictions.tsv`, `u_partners.tsv`, `u_top5.tsv`, `u_pcal.tsv`, `u_flags.tsv`, `support.tsv`, `support_sources.tsv`, `top40_primary.tsv`, `checks_all_evaluated.tsv`) | machine-generated; not retyped | Y |
| P2 | Meaning and calibration of p_cal | `results/holdout_eval/SUMMARY.md`; `results/ledger/M6_SUMMARY.md` | "precision@1 zavg_BEF 0.030 vs prior-only 0.000"; "slope 0.819"; "top 40 … 40 … 2.04 … 1.05–3.24" (Σ p_cal table row, pipes removed so the cell renders) | Y |
| P3 | Blinded-judging outcome | `results/m7/judge/analysis_main_genes.tsv` (row J074), `analysis_main.md`, `scores/J{1,2}_main3.tsv` | "J074	HGNC:23067	TRAPPC5	top40	4	1.0	0.0	0	1.0	N2"; "real supported 18, unaddressed 20, contradicted 2; decoys supported 3/120" | Y |
| P4 | Recomputed ranks, Chronos profiles, line choices, matched controls (marked †) | `results/m7/scratch_reports_trappc5/{ranks.py,ranks.tsv,profiles.py,lines.py,line_effects.tsv,ctrl.py,ctrl2.py}` | scripts and outputs in the scratch directory | Y |

## Appendix B. Red-team review

**pending** — to be written by a separate agent and appended unedited.

- Reviewer / model / date: pending
- Review text: pending
- Lint result (claims without a verified source): pending
- PI response: pending
