# INAFM1 — candidate report (Template A) + experiment plan (Template B)

Prepared under DESIGN §6.5. Template A is Part I; Template B is Part II of this same file (the task fixed
`reports/INAFM1.md` as the only writable report path for this gene, so the experiment plan is kept here as a clearly
marked part rather than in `reports/INAFM1_experiments.md`).

Unblinded literature search date: **2026-10-30** (Europe PMC incl. preprint sources, UniProt, GO/GOA, hu.MAP 3.0,
Predictomes, project ledgers). Red-team review (Appendix B): **pending**.

---

# Part I — Template A

## 0. Bench summary (for a bench biologist; plain words)

- **Claim:** INAFM1, a 142-aa single-pass membrane protein with no published function, behaves in CRISPR fitness data
  like a member of the pathway that handles polyubiquitylated proteins at the ER–proteasome interface. Its three
  strongest co-dependency partners are NFE2L1 (NRF1), NGLY1 and DDI2 — the three components of the proteolytic
  activation of NRF1 that drives proteasome "bounce-back" — while the term the pipeline actually assigned,
  *polyubiquitin modification-dependent protein binding* (GO:0031593), is carried by the weaker partners RAD23B, VCP and
  UBQLN1. The claim is therefore "INAFM1 functions in / supports polyubiquitin-dependent protein handling at the
  ER–proteasome interface", **not** that it is a subunit of anything.
- **Confidence:** **p_cal = 0.0367** [95% CI 0.016–0.060] = the expected probability that *the module term*
  (GO:0031593) is confirmed by D1-type experimental annotation within ~8 years. It is a hit probability for the term
  only; it says nothing about the relationship type, and nothing about the NRF1-axis reading in the paragraph above,
  which is an interpretation of the partner list rather than the calibrated object. Tier: none (p_cal fill; rank 37 of
  the primary top 40). No U gene reached Tier A or Tier B.
- **Strongest reason to doubt:** the prediction fails the lineage leave-out check — removing Skin lines changes the top
  term to a porphyrin/heme term and only 56% of the neighbourhood survives — and no orthogonal class supports it
  (physical: no support, p = 1.0000; co-abundance, localisation, perturbation phenotype and structure: not measured).
  The gene is dependency-flat (4 of 1361 lines below −0.5), so the whole signal comes from small covariation.
- **First experiment:** knock out INAFM1 in two dependent lines with three guides plus a guide-resistant cDNA rescue and
  ask whether NRF1 processing and the proteasome bounce-back after acute proteasome inhibition change beyond what a
  matched-essentiality control gene (MRPL55) does; time ~8 weeks; approximate cost ~€25–35k (details in Part II).
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

- Symbol: **INAFM1** | HGNC ID: **HGNC:27406** | previous symbols / aliases: **PRR24** (no alias symbols) |
  UniProt: **C9JVW0** | band: **19q13.32** | Ensembl ENSG00000257704 | Entrez 255783 | DepMap column `INAFM1 (255783)`
- D1 / D2 / D3 values: **True / True (UniProt annotation score 2) / True** (D3_pubmed True, D3_tdark False; focused
  PMIDs 0, all PMIDs 4; TDL Tbio) | curation-lag audit flag: **not in the audit sample**
- Stratum (§1.4): family **other**; expression **expressed** (not lineage-restricted); informativeness tertile **mid**;
  core **False**; headline stratum True; tool background True; low_coverage False; paralogues in matrix **0**
- Hypothesis (one sentence): **INAFM1 functions in / supports polyubiquitin modification-dependent protein binding
  (GO:0031593) — operationally, the handling of polyubiquitylated substrates at the ER–proteasome interface, the
  compartment in which its three top partners NFE2L1, NGLY1 and DDI2 act.**
- Relationship type: **d** — "type unresolved" by the §4.4 script rule (no coupling or TF flag → not e; no P/A/S support
  → not a; no EC/transport keyword and single-pass, not ≥ 4 TM → not c; no assembly label → not b). Type **c**
  (membrane-anchored supplier/client of the module) is the strongest competing assignment and is argued in §8; it is not
  assignable from the recorded evidence, because the §4.4 rule for c needs a transporter/enzyme domain or ≥ 4 TM
  helices, and INAFM1 has one TM helix and no catalytic domain.
- Novelty class: **N3** (agent L, search date recorded in `results/m7/L/HGNC_27406.md`; unblinded re-search 2026-10-30
  below confirms it)
- LLM-recall-probe flag (§6.2): **not known** ("recognised: no"; confidence none; recalled function verbatim
  "unknown"); probe answer logged at `results/m7/recall_probe_90.tsv`; matches network top term: **no**
  (the prediction is therefore independent of the probe agent's background knowledge)
- Calibrated probability p_cal: **0.0367** [95% CI **0.016–0.060**, cluster bootstrap, 2000 refits]; calibration family:
  **other**; covariates inside H's 5th–95th percentile: **yes** (support category `in_support`)
- Tier: **none (p_cal fill)**; rank in primary top 40: **37**. Top-40-only label: **demoted — lineage_leaveout**.

## 2. The protein

- Domains (InterPro): **IPR029162 (InaF-motif)**; Pfam **PF15018**; no annotated functional domain (`Domain [FT]` empty).
  TM / signal peptide / MTS: **one transmembrane helix (aa 36–56, "Helical"), single-pass; no signal peptide, no transit
  peptide**. The rest of the 142-aa protein is disordered and low-complexity (UniProt regions 1–22, 61–83, 99–142; Gly-,
  Pro- and basic/acidic-biased stretches). AlphaFold pLDDT (global, AFDB v6): **59.5** — low, consistent with a short
  protein that is one helix plus disorder.
- Protein names (UniProt): "Putative transmembrane protein INAFM1 (InaF-motif-containing protein 1) (Proline-rich
  protein 24)". Length 142 aa. Protein existence: evidence at protein level. UniProt `FUNCTION` comment: **empty**.
  Subcellular location (UniProt, ECO:0000305 = inferred by curator): "Membrane; Single-pass membrane protein."
- Deepest orthologue: the InaF motif is shared with the *Drosophila* inaF locus proteins; PMID:17968007 states the motif
  is found in "organisms as diverse as nematodes, fish, and humans". The human genome has two InaF-motif genes, INAFM1
  and INAFM2; PMID:41650465 states that INAFM2 "arose earlier than INAFM1 evolutionarily". No orthology-based function
  transfer is possible: the *Drosophila* INAF proteins are TRP-channel auxiliary subunits (PMID:32434796), a function
  with no counterpart in the predicted module, and sharing a 32-aa motif is not sharing a function.
- Class H (homology) evidence for the predicted term: **no IBA/ISO annotation for g** (bundle §6). The gene's only GO
  annotation of any kind in the current GAF is `INAFM1 located_in GO:0016020 GO_REF:0000044 IEA` — an electronic,
  CC-only membrane call.
- Source keys: UniProt C9JVW0; PMID:17968007; PMID:32434796; PMID:41650465; `reports/data/INAFM1/bundle.md` §8; GOA
  2026-05-21. All appear in Appendix A.

## 3. Dependency profile

- Mean / SD of Chronos effect: **−0.080 / 0.133**; median −0.081; 5th percentile −0.295; min −0.942. Fraction of lines
  < −0.5: **0.0029 (4 of 1361 lines)**; common-essential or selective: **neither — the gene is essentially
  dependency-flat**; NaN fraction: **0.0000** (value in all 1361 lines).
- Expression: log2(TPM+1) ≥ 1 in **99.7%** of lines (≥ 2 in 88.1%); median log2(TPM+1) **2.92**. Spearman
  ρ(effect, own expression) = **−0.107** (n = 1292) → no dependency–expression coupling flag (threshold |ρ| > 0.3).
  Dependency-vs-expression scatter: panel (b) of `reports/data/INAFM1/fig_profile.png`.
- Lineage enrichment (descriptive, Mann–Whitney vs other lines): **Skin** n = 75, mean −0.146, MW p = 0.0000;
  **CNS/Brain** n = 133, mean −0.116, p = 0.0015; **Eye** n = 15, mean −0.106, p = 0.6612. The effect sizes are small
  (≈ 0.05–0.07 Chronos units below the rest) but Skin drives the top term (§5).
- Split-half assessability: **R(g) = 0.192**; null (200 matched genes) mean 0.002, max 0.032; #R0 ≥ R = 0;
  empirical p = **0.0050**; RBO R = 0.493, p = 0.0050 → **assessable: yes**. In plain terms, the neighbourhood is
  reproducible across independent halves of the cell-line panel far more often than for matched genes, which is the
  reason this flat profile is analysable at all.
- Figure 1 (profile panel): **`reports/data/INAFM1/fig_profile.png`** — (a) INAFM1 vs NFE2L1 Chronos effect across
  1361 lines (Pearson r = 0.12, Spearman ρ = 0.13); (b) effect vs own expression; the two chosen dependent lines (D1,
  D2) and the control (C) are marked. Panel (a) makes the honest point visible: the two chosen dependent lines sit far
  below the cloud on the INAFM1 axis while their NFE2L1 effect is unremarkable — the pairwise raw correlation is weak
  and the zavg_BEF signal is a whitened, panel-wide statistic, not a line-by-line co-dropout.

## 4. Neighbourhood

Top-10 partners (`results/ledger/u_partners.tsv`; GLS rank = rank in g's GLS row after the §3.1 exclusions):

| rank | partner | zavg_BEF | z_B / z_E / z_F | GLS rank | in term | partner function and essentiality | chr & distance | paralogue / shared-guide | hu.MAP-train |
|---|---|---|---|---|---|---|---|---|---|
| 1 | NFE2L1 | 18.73 | 33.3 / 18.3 / 4.5 | 5 | no | ER-tethered CNC-bZIP transcription factor of the proteasome bounce-back; mean eff −0.13, 4.6% of lines < −0.5; not CE | 17q21.32, not g's chr | no / n.a. | gene yes, pair no |
| 2 | NGLY1 | 18.26 | 30.2 / 18.5 / 6.1 | 1 | no | cytosolic peptide:N-glycanase (deglycosylation / sequence editing); mean eff −0.20, 10.9%; not CE; **hub** (in-degree 73) | 3p24.2 | no | no / no |
| 3 | DDI2 | 18.21 | 29.9 / 18.3 / 6.4 | 2 | no | aspartyl (retroviral-type) protease, NRF1 endoprotease / Ub shuttle; mean eff −0.17, 6.3%; not CE | 1p36.21 | no | no / no |
| 4 | RAD23B | 12.91 | 22.8 / 14.3 / 1.6 | 2787 | **yes** | UBL–UBA proteasome shuttle factor; mean eff −0.17, 5.1%; not CE | 9q31.2 | no | gene yes, pair no |
| 5 | IPO9 | 6.52 | 8.3 / 9.9 / 1.3 | 2546 | no | importin-9; mean eff −0.80, 82.0% of lines < −0.5; not CE | 1q32.1 | no | no / no |
| 6 | AKIRIN1 | 6.46 | 9.3 / 8.9 / 1.2 | 1181 | no | akirin family (paralogue AKIRIN2 imports 20S proteasomes); mean eff −0.32, 17.6%; **in U** | 1p34.3 | no | no / no |
| 7 | FBXO42 | 5.64 | 13.0 / 2.9 / 1.1 | 4934 | no | F-box protein (SCF substrate receptor); mean eff −0.15, 12.7%; **in U** | 1p36.13 | no | no / no |
| 8 | VCP | 5.05 | 6.9 / 7.0 / 1.2 | 2427 | **yes** | p97 AAA-ATPase, ERAD retrotranslocation; mean eff −2.59, 99.9% of lines < −0.5; **common-essential** | 9p13.3 | no | gene yes, pair no |
| 9 | FAM171B | 5.01 | 8.5 / 4.8 / 1.7 | 2246 | no | uncharacterised; mean eff −0.12, 1.8%; **in U** | 2q32.1 | no | no / no |
| 10 | RHCG | 4.59 | 7.4 / 5.5 / 0.8 | 4806 | no | ammonium transporter; mean eff −0.06, 0.2% | 15q26.1 | no | no / no |

The third supporting partner, **UBQLN1** (ubiquilin-1, a UBL–UBA shuttle factor), sits in the K = 25 list outside the
top 10; it appears in the bundle's CN check (r = 0.04). None of the top-10 partners is on g's chromosome; no paralogue
or shared-guide flag is raised (and no paralogue of INAFM1 exists in the matrix).

- Figure 2 (neighbourhood network): **`reports/data/INAFM1/fig_network.png`** — g plus its top-10 partners, edges at
  zavg_BEF ≥ 3; blue nodes (RAD23B, VCP) are annotated to the predicted term; solid black edges carry physical support
  in an admitted P source. 41 edges among the 11 nodes, **4 with physical support (NGLY1–RAD23B, NGLY1–VCP,
  DDI2–RAD23B, RAD23B–VCP)** — the partners are physically interlinked with each other, but **none of the solid edges
  touches INAFM1**.

Top 3 terms (R1; `results/ledger/u_top5.tsv`):

| rank | term | S | p_emp | hypergeometric p (descriptive) | leave-one-partner-out stability |
|---|---|---|---|---|---|
| 1 | GO:0031593 polyubiquitin modification-dependent protein binding (size 42) | 22.044 | 0.0020 | 0.0000 | rank kept after 2 of 3 single-partner removals |
| 2 | GO:0061136 regulation of proteasomal protein catabolic process (size 153) | 22.044 | 0.0040 | 0.0016 | 1 of 3 |
| 3 | GO:0140030 modification-dependent protein binding (size 62) | 22.044 | 0.0020 | 0.0001 | 1 of 3 |

Second-ranked term: **GO:0061136 regulation of proteasomal protein catabolic process**. Ranks 4–5 (GO:0032434,
GO:2000058) are also proteasome-regulation terms with 2 supporting partners each. The whole top-5 is one coherent
ubiquitin–proteasome block; the specific label among them is not well determined (identical S for ranks 1–3, broken by
the ascending-GO-id tie-break recorded in DEVIATIONS).

**The most important structural fact about this neighbourhood.** The three strongest partners (NFE2L1, NGLY1, DDI2;
zavg_BEF ≈ 18.2–18.7) are *not* annotated to the predicted term. The term is carried by RAD23B (12.91), VCP (5.05) and
UBQLN1. So the label GO:0031593 is supported by the second tier of the neighbourhood, while the signal that makes this
gene interesting at all is the first tier — the NRF1 proteolytic-activation axis. Both readings point into the same
biology (polyubiquitylated-substrate handling at the ER–proteasome interface), but they are not the same statement, and
only the term carries p_cal.

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | **pass** | g arm 19q; 0 of the top-10 partners on g's chromosome; 0 paralogues of g in the matrix |
| Bidirectional-promoter / overlapping / readthrough partners | **pass** | 0 of 3 supporting partners flagged |
| Copy-number co-amplification | **pass** | 0 of 3 flagged; RAD23B r = 0.05, VCP r = 0.00, UBQLN1 r = 0.04 |
| Hub-driven call (> 50% of S from top-1% in-degree) | **pass** | hub share 0.00; 0 hub partners among the supporting partners (NGLY1 is a hub but is not a supporting partner) |
| Lineage leave-out | **FAIL** | removing Skin (75 lines; mean effect −0.146) changes the top term to GO:0006778 porphyrin-containing compound metabolic process; N(g) overlap only **0.56** |
| K = 10 / 50 | **mixed** | K = 10 gives the same top term; K = 50 gives GO:0061136 regulation of proteasomal protein catabolic process (the rank-2 term — same block, different label) |
| Dependency vs own expression; TF / lineage-marker enrichment | **pass** | ρ = −0.107 (n = 1292), no flag; TFs in N(g) = 1, OR 0.51, p 0.8592, q 1.0000 |
| TP53 / p53-axis correlation | **pass** | mut 902 / WT 459; p 0.2236, q 0.4129; median difference (mut − WT) 0.015 |
| DEMETER2 replication | **not measured** | 0 of the partners are present in DEMETER2, so no replication is possible (not a pass) |
| Shared-sgRNA and per-guide check | **not possible** (guide maps / guide-level data not available) | recorded |
| GLS network (descriptive, §2.2) | **different** | the GLS K = 25 neighbourhood's top term is GO:0006869 lipid transport — the call does not survive a change of scoring statistic |

Two of these deserve weight rather than a tick: the **lineage leave-out failure** (the single reason this gene is
labelled "demoted" in `results/ledger/top40_primary.tsv`) and the **GLS disagreement**. Together they say the call rests
on a particular statistic applied to a panel in which Skin lines contribute disproportionately.

## 6. Orthogonal evidence matrix (four states: not measured / no support / supports / contradicts)

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | BioPlex 3.0, OpenCell, BioGRID-LTP, STRING-exp (one P source group); Human Cell Map SAINT | **no support** | 0 edges to the 42 term members; g's only STRING-experiments interactor genome-wide is **AGO2** (not a term member); g is not a node in BioPlex, OpenCell, BioGRID-LTP or HCM; no pair with any top-10 partner is measured in BioPlex/OpenCell/BioGRID/HCM, and STRING-exp reports no edge to any of them | 1.0000 (Simes within class; no Holm correction needed with one measured class) | family "other" → any class is diagnostic |
| A co-abundance | ProteomeHD; CCLE proteomics | **not measured** | g absent from both | — | — |
| L localisation | HPA v25.1 (admitted); OpenCell, Human Cell Map, MitoCarta (contradiction rule only) | **not measured** | g not in HPA; not tagged in OpenCell; not a prey or bait in Human Cell Map; assessed and not listed in MitoCarta3.0 | — | — |
| G perturbation phenotype | Perturb-seq K562 GW / K562 essential / RPE1 essential (Replogle 2022) | **not measured** | g not perturbed/measured in any of the three | — | — |
| S structure | Burke 2023 AF2 | **not measured** | g not modelled | — | — |
| H homology | orthologue IBA/ISO | reported only | no IBA/ISO annotation for g | reported only | n.a. |

Supporting classes: **none**. Diagnostic class measured / supports: **True / False**. Contradiction: **False**
(term compartments cytosol|nucleus; g not multi-localised; HPA-only contradiction: False). Members tested: 42.

Reported but not counted: **hu.MAP 3.0** — INAFM1/C9JVW0 does not appear in the hu.MAP 3.0 complex list or pair files at
all, so hu.MAP has no opinion. **DEMETER2** — no partners in common. **Predictomes** — 81 modelled pairs with C9JVW0,
best kirc_score 0.284 (INAFM1–TMEM100), and none with any of the top-10 partners; no pair reaches a confident-interface
level. Absence of an interaction is never a contradiction: for a 142-aa single-pass protein that is absent from every
large interactome bait/prey set, "no support" here mostly means "not looked at".

## 7. Literature (blinded step, then synthesis)

**Blinded summary of agent L's evidence items** (`results/m7/L/HGNC_27406.md`; 3 items, all level *mention*, all
DepMap-derived = no): (1) UniProt records only a subcellular location, no function; (2) INAFM1 appears in a
bioinformatic list of six genes whose expression may associate with prognosis in TMPRSS2-ERG prostate cancer
(PMID:30866732); (3) PRR24 appears among five differentially expressed genes in neuropathic-pain tissue
(PMID:36816032). Agent L recorded explicit collision exclusions (PRR24 = "percent reduction in parasitaemia at 24 h";
"inAFM1" = "in aflatoxin M1"; the *Drosophila* inaF locus shares only the motif name) and concluded the function is
uncharacterised → **N3**.

**Blinded verdicts** (packet J082, `results/m7/judge/`): real statement **0** (unaddressed); decoys **0, 0, 0**; judges
J1 and J2 agreed on all four slots (justification for every slot: "Not addressed by the evidence"), so no adjudicator
was needed; d = real − mean(decoys) = **0.0**. The gene contributes a tie to the primary sign-flip test and is one of
the 2 N3 genes in the top 40, both of which scored 0 — exactly what "no functional literature exists" implies: blinded
judging cannot support an N3 prediction, it can only fail to contradict it.

**Unblinded synthesis (2026-10-30).** A full unblinded search (Europe PMC, all previous symbols and the accession:
`INAFM1` 32 hits, `PRR24` 68 hits, `"InaF motif"` 12 hits, `C9JVW0` 0 hits; plus targeted searches crossing the gene
with NFE2L1/NRF1, NGLY1, DDI2, VCP/p97, proteasome and ubiquitin) reproduces agent L's conclusion and adds nothing
functional. Every INAFM1/PRR24 hit is an omics gene-list appearance; the gene is named in no paper that studies it.
Three further points come from the unblinded search and matter for the hypothesis:

1. **The protein-family name is a false friend.** INAFM1 is named for a 32-aa transmembrane motif defined in
   *Drosophila*: "This conserved sequence defines an inaF motif, representatives of which are found in proteins from
   organisms as diverse as nematodes, fish, and humans" [PMID:17968007]. The fly INAF proteins are TRP-channel
   auxiliary subunits [PMID:32434796]. No vertebrate TRP link has been shown for INAFM1, and TRP channels are not in
   the predicted module. The motif supports "small single-pass membrane protein that can act as an auxiliary subunit of
   a larger membrane-associated machine" as a *structural analogy only*.
2. **The paralogue INAFM2 was characterised in 2026 and INAFM1 was explicitly not.** PMID:41650465 renames INAFM2
   "ROME" and reports a plasma-membrane glycoprotein that binds β-catenin and vimentin and drives metastasis; that
   paper states the human genome contains "INAFM1 (not studied in this article) and ROME (INAFM2)". This is the closest
   prior publication to our gene, and it does two things: it confirms that the family can carry real vertebrate
   function, and it confirms that INAFM1 itself remains unexamined. It also offers a competing biology (Wnt/β-catenin,
   cytoskeleton) which our neighbourhood does not point at. Notably, the same paper reports that in DepMap "ROME KO was
   not associated with growth dependence" in the lines where data existed — a reminder that family members can be
   functionally important and dependency-flat at the same time.
3. **The partner module is extremely well characterised, and INAFM1 is in none of it.** The NRF1 bounce-back axis is
   established: NFE2L1/Nrf1 "is necessary for induced proteasome gene transcription in mouse embryonic fibroblasts
   (MEFs)" [PMID:20385086]; Nrf1 is "retrotranslocated to the cytosolic side of the membrane in a manner that depends on
   p97/VCP" [PMID:24448410]; NGLY1 "is essential for Nrf1 activation in response to proteasome inhibition"
   [PMID:29202016] and edits the sequence of SKN-1A/Nrf1 [PMID:31002798]; DDI2 "is required to cleave and activate Nrf1"
   [PMID:27528193] and does so only on highly poly-ubiquitylated NRF1 [PMID:32521225]; DDI2 also acts as a shuttling
   factor in ERAD [PMID:35358511]; and the rank-6 partner's paralogue AKIRIN2 is "essentially required for nuclear
   protein degradation" by importing 20S proteasomes [PMID:34711951]. The three term-carrying partners RAD23B, VCP and
   UBQLN1 are the canonical ubiquitin-shuttle/retrotranslocation arm of the same interface. In other words, our top
   partners are not a random assortment: ranks 1–3 are the three proteins of one pathway, ranks 4/8 and UBQLN1 are the
   shuttle factors that feed it. **None of these papers mentions INAFM1.**

**Is any of it DepMap-derived?** None of the three evidence items agent L recorded is DepMap-derived. Of the
background papers used above, PMID:35271393 (NGLY1/NFE2L1 and ferroptosis) uses DepMap portal data for KEAP1-mutant
drug sensitivity, and PMID:41650465 consults DepMap for ROME dependency; neither statement is used here to support the
INAFM1 claim. The claim therefore does not re-enter the evidence through a DepMap-derived publication.

**Closest prior publication and what co-essentiality adds beyond it.** The closest is PMID:41650465 (the INAFM2/ROME
characterisation), which adds nothing about INAFM1 beyond confirming that it is unstudied. Co-essentiality adds the
only functional signal that exists for this gene: a reproducible (split-half R = 0.192, p = 0.0050) neighbourhood whose
top three members are the three proteins of the NRF1 proteolytic-activation axis.

**Prior prediction lists containing this gene:** **none found.**
- *Wainberg 2021* (PMID:33859415): INAFM1/PRR24 is not named anywhere in the retrieved full text. Their uncharacterised
  set was UniProt annotation score ≤ 2, which INAFM1 satisfies, so it could have been in scope; the per-gene
  supplementary prediction tables were not retrieved, so this is "not found in the retrieved text", not a verified
  absence.
- *hu.MAP 3.0* (PMID:40425816): INAFM1 (C9JVW0) is absent from the complex table and the pair files — no prediction.
- *Replogle 2022* (PMID:35688146): INAFM1 is not measured in K562 genome-wide, K562 essential or RPE1 essential
  Perturb-seq (ledger `support_sources.tsv`: "g not measured") — no prediction.
- *Predictomes* (reported only): 81 pairs involving C9JVW0, none with a top-10 partner and none at a confident-interface
  score — no prediction.
- **Post-freeze (after 2026-10-29) papers confirming the prediction:** none.

## 8. Alternative explanations

For each artefact check in §5, the evidence against it:

- **Chromosomal proximity / same-arm artefact:** excluded by construction; 0 of 10 partners share g's chromosome.
- **Paralogue cross-reactivity of guides:** INAFM1 has 0 paralogues in the matrix; the InaF-motif relative INAFM2 is not
  a sequence paralogue at the level Ensembl records here. Guide-level confirmation is nevertheless impossible in the
  data (no guide maps) and is pushed into the experiment (Part II §3).
- **Copy-number co-amplification:** r ≤ 0.05 for all three supporting partners.
- **Hub-driven call:** hub share of S is 0.00. NGLY1 is a hub (in-degree 73) but contributes to the neighbourhood, not
  to the term's S.
- **Lineage artefact: NOT excluded.** This is the live one. Skin lines are the most dependent lineage (mean −0.146,
  MW p = 0.0000) and removing them changes the top term entirely. A melanocyte/keratinocyte-specific covariation —
  for example shared sensitivity to proteotoxic or pigment-related stress — could generate the neighbourhood without
  INAFM1 participating in the pathway. The experiment must therefore be run in non-Skin lines (it is: Esophagus/Stomach
  and Prostate), which is a deliberate stress test of the prediction rather than a convenience.
- **Statistic-dependence:** the GLS version of the same neighbourhood gives an unrelated top term (lipid transport).
  The call is not robust to swapping the scoring statistic, and the report should not be read as if it were.
- **Expression-driven (type e) artefact:** ρ(effect, own expression) = −0.107 and only 1 TF among the partners — no
  support for a transcriptional-programme explanation.

**Strongest competing biological hypothesis.** That INAFM1 is a **membrane-anchored supplier/client (type c)** rather
than a pathway component: a single-pass ER/membrane protein whose loss perturbs the membrane environment in which NRF1
is retrotranslocated and processed, producing co-dependency with NFE2L1/NGLY1/DDI2 without INAFM1 being part of the
machinery. A weaker but real alternative is that the dependency is a **generic proteostasis-sickness correlation**: the
four lines with an effect below −0.5 may simply be lines with narrow proteostasis margins, so any gene whose loss
nudges proteostasis co-varies with the NRF1 axis. The experiment that separates these is the module-specific readout
combined with the matched-essentiality control (Part II §6): a pathway member or a client should change NRF1 processing
specifically, whereas a generic-sickness correlate should move the readout no more than an unrelated gene matched for
growth effect.

## 9. Falsifying observations (written before §6 and §7 were read)

1. **INAFM1 knockout does not alter NRF1 (NFE2L1) processing or the proteasome bounce-back.** Specifically: in both
   dependent lines, after acute proteasome inhibition, the ratio of cleaved (~95–110 kDa) to full-length NRF1 and the
   induction of proteasome subunit transcripts (PSMA/PSMB panel) differ from the non-targeting control by no more than
   the matched-essentiality control gene does at the same growth effect. This would refute the module call in its
   mechanistic form.
2. **INAFM1 protein is not in a compartment where the module operates, and does not co-purify with any of it.**
   Specifically: endogenously tagged INAFM1 localises to the plasma membrane (or any compartment excluding ER /
   nuclear envelope / cytosolic face) in both dependent lines, and IP-MS/TurboID of tagged INAFM1 recovers no NRF1-axis
   or shuttle-factor protein (NFE2L1, NGLY1, DDI2, VCP, RAD23B, UBQLN1, proteasome subunits) above a tagged control.
   Combined with (1) this would make the whole GO:0031593 call untenable and would point back at the INAFM2/ROME-style
   plasma-membrane biology instead.

## 10. Experiments

See **Part II** of this file (Template B).

## 11. Novelty and external benchmarks

Agreement with prior catalogues: **none of the four catalogues made this prediction.** Wainberg 2021 does not name the
gene in its retrieved full text (supplementary tables not retrieved); hu.MAP 3.0 does not contain the protein;
Replogle 2022 did not measure it; Predictomes contains only low-scoring pairs, none with a partner.

What is new here: for a gene with **zero** functional literature as of 2026-10-30, this is the first evidence of any
kind that places it in a pathway — a reproducible co-dependency neighbourhood whose three strongest members are NFE2L1,
NGLY1 and DDI2. Against that, the honest accounting is: p_cal = 0.0367, the lineage leave-out fails, no orthogonal
class supports it, and blinded judging returned 0 because there is nothing in the literature to judge against. The
contribution is a testable hypothesis with a cheap decisive test, not a function call.

## Appendix A. Evidence ledger

Every claim that is not a ledger row has a row here. "Verified" = the PMID/DOI resolved through the Europe PMC REST API
and the quoted span was found in the retrieved text (abstract or full text as stated); project-file rows were checked
against the file. Rows marked N would have to be deleted before submission — there are none.

| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| INAFM1 is a 142-aa single-pass membrane protein with no UniProt FUNCTION comment; TM helix 36–56; InaF-motif (PF15018/IPR029162) | UniProt C9JVW0 (REST, release 2026_03; last annotation update 2026-09-02) and `reports/data/INAFM1/bundle.md` §8 | "SUBCELLULAR LOCATION: Membrane {ECO:0000305}; Single-pass membrane protein {ECO:0000305}." / Transmembrane feature 36–56 "Helical" / Pfam PF15018, InterPro IPR029162 (text read: UniProt JSON record + bundle table) | Y |
| AlphaFold global pLDDT for C9JVW0 is 59.5 (AFDB v6, model created 2025-08-01) | AlphaFold DB API `https://alphafold.ebi.ac.uk/api/prediction/C9JVW0` | globalMetricValue 59.47, latestVersion 6 (text read: API JSON) | Y |
| INAFM1's only current GO annotation is an electronic CC-only membrane call | `data/raw/go/current/goa_human.gaf.gz` (GOA 2026-05-21) | "INAFM1 located_in GO:0016020 GO_REF:0000044 IEA 20260428 UniProt" (text read: GAF rows for INAFM1) | Y |
| The InaF motif is a 32-aa transmembrane motif conserved from nematodes to humans | PMID:17968007 (DOI 10.1073/pnas.0708368104) | "This conserved sequence defines an inaF motif, representatives of which are found in proteins from organisms as diverse as nematodes, fish, and humans." (text read: abstract) | Y |
| The *Drosophila* inaF locus encodes TRP-channel auxiliary subunits | PMID:32434796 (DOI 10.1534/genetics.120.303268) | "our studies support a model in which the inaF locus encodes a family of at least three TRP auxiliary subunits." (text read: abstract) | Y |
| The 2026 characterisation of the paralogue INAFM2/ROME explicitly does not study INAFM1 | PMID:41650465 (DOI 10.1158/2767-9764.crc-26-0068) | "INAFM1 (not studied in this article) and ROME (INAFM2)" (text read: full text, Europe PMC PMC13012068) | Y |
| ROME (INAFM2) KO showed no growth dependence in the DepMap lines with data | PMID:41650465 | "in the Broad Institute's DepMap database, ROME KO was not associated with growth dependence in 24 different cancer cell lines" (text read: full text) | Y |
| INAFM1's published appearances are omics gene-list mentions only (prostate-cancer prognosis list) | PMID:30866732 (DOI 10.1142/s0219720019500033) | "TOB1, GALNT7, INAFM1, APELA, RAC3, and NNMT" (text read: abstract) | Y |
| PRR24 (previous symbol) appears in a neuropathic-pain differential-expression list | PMID:36816032 (DOI 10.3389/fgene.2023.1127167) | "GTF2H2, KLHL5, LRRC37A4P, PRR24, and MRPL23" (text read: abstract and full text) | Y |
| NFE2L1/Nrf1 drives the proteasome bounce-back response | PMID:20385086 (DOI 10.1016/j.molcel.2010.02.029) | "is necessary for induced proteasome gene transcription in mouse embryonic fibroblasts (MEFs)" (text read: abstract) | Y |
| NRF1 retrotranslocation from the ER depends on p97/VCP | PMID:24448410 (DOI 10.7554/eLife.01856) | "retrotranslocated to the cytosolic side of the membrane in a manner that depends on p97/VCP" (text read: abstract and full text) | Y |
| NGLY1 is required for NRF1 activation after proteasome inhibition | PMID:29202016 (DOI 10.1021/acscentsci.7b00224) | "the cytosolic enzyme N-glycanase 1 (NGLY1, the human PNGase) is essential for Nrf1 activation" (text read: abstract and full text) | Y |
| NGLY1 acts by sequence editing of SKN-1A/Nrf1 | PMID:31002798 (DOI 10.1016/j.cell.2019.03.035) | "PNG-1/NGLY1 peptide:N-glycanase edits the sequence of SKN-1A protein" (text read: abstract and full text) | Y |
| DDI2 is the protease that cleaves and activates NRF1 | PMID:27528193 (DOI 10.7554/eLife.18357) | "the aspartyl protease DNA-damage inducible 1 homolog 2 (DDI2) is required to cleave and activate Nrf1" (text read: abstract and full text) | Y |
| DDI2 cleaves NRF1 only when NRF1 is highly poly-ubiquitylated (ubiquitin-directed endoprotease) | PMID:32521225 (DOI 10.1016/j.molcel.2020.05.035) | "DDI2 is indeed capable of cleaving NRF1 in vitro but only when NRF1 protein is highly poly-ubiquitylated" (text read: abstract and full text) | Y |
| DDI2 also works as an ERAD shuttling factor delivering K11/K48 chains to the proteasome | PMID:35358511 (DOI 10.1016/j.jbc.2022.101875) | "Ddi2 appears to function as a shuttling factor in endoplasmic reticulum-associated protein degradation" (text read: abstract) | Y |
| AKIRIN2 (paralogue of the rank-6 partner AKIRIN1) imports 20S proteasomes into the nucleus | PMID:34711951 (DOI 10.1038/s41586-021-04035-8) | "AKIRIN2, that is essentially required for nuclear protein degradation" (text read: abstract) | Y |
| Wainberg 2021 is the co-essentiality benchmark whose predictions we check against | PMID:33859415 (DOI 10.1038/s41588-021-00840-z) | "co-essential modules assigns function to uncharacterized genes" (text read: title/abstract and full text; INAFM1 and PRR24 do not occur in the retrieved full text) | Y |
| hu.MAP 3.0 is the complex atlas we check against; it does not contain INAFM1 | PMID:40425816 (DOI 10.1038/s44320-025-00121-5) and `data/raw/humap3/*` | "atlas of human protein complexes" (text read: title/abstract); grep for C9JVW0 / INAFM1 in `hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv`, `humap3_all_ppis_202305.pairsWprob.gz`: 0 matches | Y |
| Replogle 2022 is the Perturb-seq benchmark; INAFM1 was not measured | PMID:35688146 (DOI 10.1016/j.cell.2022.05.013) and `results/ledger/support_sources.tsv` | "genome-scale Perturb-seq" (text read: title/abstract) / ledger note "g not measured" for PerturbSeq_K562_GW, PerturbSeq_K562_essential, PerturbSeq_RPE1_essential | Y |
| Predictomes contains 81 C9JVW0 pairs, best kirc_score 0.284, none with a top-10 partner | `data/raw/predictomes2025/20251110_hs_predictome_pair_scores.csv.gz` (copy of the extracted rows at `results/m7/scratch_reports_inafm1/predictome_INAFM1.csv`) | "INAM1_HUMAN__TM100_HUMAN__276aa,C9JVW0:Q9NV29,0.284,0.020,78,365,0,0,0,0" (text read: extracted file; 81 data rows) | Y |
| Raw pairwise Chronos correlations of INAFM1 with its top partners are modest (NGLY1 r = 0.214, DDI2 r = 0.168, NFE2L1 r = 0.117; n = 1361) | recomputed † from `data/raw/depmap/CRISPRGeneEffect.csv` by `results/m7/scratch_reports_inafm1/depmap_checks.py` | "INAFM1 vs NGLY1 pearson r=0.214 spearman=0.205 n=1361" (text read: script output `depmap_checks.out`) | Y |
| MRPL55 is a matched-essentiality control gene (effect −0.80 in ACH-002837 and −0.98 in ACH-000956, vs INAFM1 −0.79 / −0.94) from an unrelated module (mitoribosome) | recomputed † from `data/raw/depmap/CRISPRGeneEffect.csv` by `results/m7/scratch_reports_inafm1/matched_ctrl.py` | "MRPL55 -0.80 -0.98 -0.55 0.20" (text read: script output) | Y |
| All numeric prediction, robustness, orthogonal and cell-line values in §1–§6 and Part II §2 | `reports/data/INAFM1/bundle.md` (machine-generated from `results/ledger/*`, `results/assessability/assessability_U.tsv`, `results/m7/recall_probe_90.tsv`) and `results/ledger/top40_primary.tsv` row rank 37 | bundle tables §1–§10, copied without retyping (text read: file) | Y |
| p_cal means the probability that the top term is confirmed by D1-evidence annotation within ~8 years, and the calibration is not poor | `DESIGN.md` §3.7 and `results/holdout_eval/SUMMARY.md` | "p_cal = probability that the top term is confirmed by D1-evidence annotation within ~8 years (conservative)." / "slope 95% CI includes 1 and intercept 95% CI includes 0 (Wald) -> calibration not poor; p_cal reported without the poor-calibration caveat." (text read: files) | Y |
| Blinded judging outcome for INAFM1: real 0, decoys 0, d = 0 | `results/m7/judge/analysis_main_genes.tsv`, `results/m7/judge/scores/J1_main3.tsv`, `.../J2_main3.tsv` | "J082 HGNC:27406 INAFM1 top40 37 0.0 0.0 0 0.0 N3" (text read: file) | Y |

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

- Gene: **INAFM1** | hypothesis: INAFM1 functions in / supports polyubiquitin modification-dependent protein binding
  (GO:0031593) at the ER–proteasome interface, operationally the NFE2L1(NRF1)–NGLY1–DDI2 axis | relationship type:
  **d (type unresolved)** | novelty class: **N3**
- LLM-recall-probe flag: **not known** | calibrated probability: **p_cal = 0.0367** (calibration family "other") |
  tier: **none (p_cal fill, rank 37)**
- Strongest alternative explanation: INAFM1 is a membrane-anchored supplier/client (type c) whose loss perturbs the
  membrane environment of NRF1 retrotranslocation without being part of the machinery; or the co-dependency is a
  generic proteostasis-margin correlation.
- **Decisive experiment (one sentence):** knock out INAFM1 (3 guides + guide-resistant cDNA rescue) in two dependent
  lines and measure NRF1 processing and proteasome-subunit induction after acute proteasome inhibition, time-matched
  against NGLY1 and DDI2 knockouts and against a matched-essentiality control gene from an unrelated module.
- Falsifying observation (copied from Template A §9): INAFM1 knockout does not alter the cleaved/full-length NRF1 ratio
  or proteasome-subunit transcript induction by more than the matched-essentiality control gene does at the same growth
  effect.

## 2. Cell lines (selection rule)

Rule (DESIGN §6.5 / Template B): two dependent lines with Chronos ≤ −0.5 for g and ≤ −0.3 for the top partner, g
expressed (log2(TPM+1) ≥ 2), locus not amplified, high screen quality, preferably TP53-null.

**Criterion actually applied: relaxed — the partner criterion was dropped**, because the funnel empties: of 1361 lines,
4 have g ≤ −0.5, and **0** of those also have NFE2L1 ≤ −0.3. This is a direct consequence of the flat profile and is
stated here rather than hidden: there is no line in DepMap where INAFM1 and its rank-1 partner co-drop.

Chosen dependent lines (from `reports/data/INAFM1/bundle.md` §10):

| ModelID | name | lineage / disease | g effect | partner (NFE2L1) effect | g expr log2(TPM+1) | g CN | TP53 | screen NNMD / ROCAUC | medium |
|---|---|---|---|---|---|---|---|---|---|
| ACH-002837 | HCM-BROD-0100-C15 | Esophagus/Stomach, esophagogastric adenocarcinoma | −0.79 | 0.13 | 3.96 | 1.23 | mut | −4.55 / 0.89 | OPAC:Ad+++ (1:1) (MF-031-002) |
| ACH-000956 | 22Rv1 | Prostate, prostate adenocarcinoma | −0.94 | −0.28 | 2.46 | 0.98 | mut | −4.29 / 0.92 | RPMI + 10% FBS (MF-001-001) |

Backup (rank 3 of the funnel): ACH-000151 JM1 (Lymphoid, B-ALL; g −0.51, NFE2L1 −0.29, expr 2.22, CN 0.95, TP53 WT).
Neither chosen line is a Skin line, so the experiment is also a test of the lineage-artefact concern in §8.

Control line that expresses g but does not depend on it, same lineage as line 1:

| ModelID | name | lineage / disease | g effect | g expr | TP53 | NNMD / ROCAUC | medium |
|---|---|---|---|---|---|---|---|
| ACH-000452 | TE-8 | Esophagus/Stomach, esophageal squamous cell carcinoma | −0.16 | 4.63 | mut | −10.85 / 0.96 | RPMI + 10% FBS (MF-001-001) |

- Common-essential gene? **No** (0.29% of lines < −0.5). A degron/CRISPRi line is therefore not required for viability
  reasons, but an **auxin-inducible degron (AID2) knock-in in RPE1-hTERT TP53⁻/⁻ is added as a second arm** anyway,
  because the whole point of the readout is acute kinetics: NRF1 processing must be measured before any secondary
  proteostasis adaptation. Controls for the knockout arm: guide-resistant cDNA rescue, 2 non-targeting guides, AAVS1
  cutting control, and a control essential gene (below).
- Baseline medium: **the DepMap screen medium of each chosen line** — OPAC:Ad+++ (1:1) (MF-031-002) for
  HCM-BROD-0100-C15, RPMI + 10% FBS (MF-001-001) for 22Rv1 and TE-8. Any proteasome-inhibitor or proteotoxic-stress
  condition is a **sensitised arm, not the baseline**, and is analysed separately.
- **Essential-gene confound control (required):** acute depletion of INAFM1 time-matched to NGLY1/DDI2 depletion, read
  against **MRPL55** — Chronos −0.80 in ACH-002837 and −0.98 in ACH-000956 (INAFM1: −0.79 and −0.94), module =
  mitochondrial large ribosomal subunit, unrelated to ubiquitin–proteasome biology. Matching is on the *same two lines*,
  not on the panel mean. Secondary matched control if MRPL55 proves to perturb proteostasis: RPUSD4 (−0.79 / −0.92).

## 3. Reagents

- **3 sgRNAs against INAFM1 + 2 non-targeting + AAVS1 cutting control.** Sequences are **not listed here**: the project
  holds no guide library file and no guide-level DepMap data (recorded as "not possible" in §5 of Template A), and
  writing plausible-looking 20-mers would be an unverified claim. Procedure instead: take the 4 INAFM1 guides from
  Brunello and the 4 from the Avana library used by the DepMap screens that produced the effects above, select 3 that
  (i) target distinct exons upstream of the TM helix (aa 36–56) or within it, (ii) pass the off-target check below.
  Per-guide concordance is then established inside the experiment (all 3 guides must drop out, and all 3 must be
  rescued by the cDNA).
- **Sequence-level off-target check of every guide:** genome-wide mismatch search (Cas-OFFinder, GRCh38, up to 3
  mismatches + DNA/RNA bulges of 1) with the explicit acceptance rule: no perfect or 1-mismatch site in any other
  protein-coding gene, and in particular none in NFE2L1, NGLY1, DDI2, RAD23B, VCP, UBQLN1, IPO9, AKIRIN1/2 or any
  proteasome subunit. Result to be recorded in the experiment's ledger; tool and version named in the methods.
- CRISPRi guides if the locus is amplified: **not needed** — CN is 1.23 and 0.98 in the two lines (threshold 1.5).
- Guide-resistant cDNA: INAFM1 ORF (ORFeome / synthesised from the C9JVW0 CDS) with silent PAM/seed mutations for all
  three guides, lentiviral, doxycycline-inducible, in two forms — untagged and C-terminally HaloTag/mNG — plus a
  **TM-deleted (Δ36–56) variant** to ask whether membrane anchoring is required.
- Validated antibody: **no validated INAFM1 antibody is known to exist** (the protein is absent from HPA). The plan does
  not depend on one: detection is by **endogenous C-terminal HaloTag–mNG knock-in** (and the inducible tagged cDNA as a
  positive control for the antibody-free detection chain).
- Antibodies for partners and markers: NRF1/NFE2L1 (must resolve full-length ~120 kDa and the cleaved ~95–110 kDa
  species), NGLY1, DDI2, VCP, RAD23B, UBQLN1, PSMA/PSMB panel (e.g. PSMB5, PSMA1), and organelle markers calnexin (ER),
  LAP2β or lamin B1 (nuclear envelope), Na⁺/K⁺-ATPase (plasma membrane), EEA1/LAMP1 (endosome/lysosome), GM130 (Golgi).

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of INAFM1 with NFE2L1, NGLY1, DDI2 (and, as a second set, RAD23B/VCP/UBQLN1); ipTM/pDockQ | days | Confident, conserved interface | No interface (does **not** exclude types b–e, and for a 142-aa mostly-disordered protein a negative is nearly uninformative) | **Yes (cheap, run first, weighted lightly)** | ipTM ≥ 0.5 or pDockQ ≥ 0.23 for at least one pair, with the interface mapping to the TM helix or a conserved InaF-motif face; Predictomes already reports no confident pair with these partners, so the prior is low |
| 1 | Competitive growth (GFP/RFP mix), 3 guides + rescue, 2 dependent lines vs TE-8 control line | 2–3 wk | Dropout in HCM-BROD-0100-C15 and 22Rv1 but not TE-8, rescued by guide-resistant cDNA | No dropout (the DepMap effect does not reproduce), or dropout not rescued (off-target) | **Yes — gate for everything below** | ≥ 20–25% depletion of guide⁺ cells by day 21 in both dependent lines (consistent with Chronos −0.79/−0.94), ≤ 5% in TE-8, restored to ≤ 5% by the cDNA; all 3 guides concordant |
| 1 | **Essential-gene confound control:** AID2 degron depletion of INAFM1 time-matched to NGLY1/DDI2 degradation, vs MRPL55 at matched growth effect | 2–4 wk | NRF1/proteasome readout changes beyond MRPL55's change at matched growth inhibition | Same change as MRPL55 → general sickness, not module function | **Yes — required** | At 4/8/24 h after auxin: NRF1 cleaved/full-length ratio and PSMB5/PSMA1 mRNA induction differ from MRPL55 by ≥ 2 SD of the control replicates, while total growth inhibition differs by < 20% |
| 1 | Localisation with markers (endogenous HaloTag–mNG knock-in) | 2–4 wk | ER / nuclear envelope / cytosolic-face membrane signal, overlapping calnexin or LAP2β | Plasma-membrane-only or endolysosomal-only signal in both lines → incompatible with the module | **Yes** | Pearson/Mander's overlap with calnexin > 0.5 and clearly above the Na⁺/K⁺-ATPase overlap; the INAFM2/ROME result makes a plasma-membrane outcome a real possibility |
| 1 | **Module-specific readout after KO** (see §5) | 2–4 wk | Phenocopies NGLY1 or DDI2 KO: blunted NRF1 cleavage and blunted proteasome-subunit induction after bortezomib/carfilzomib | Normal NRF1 processing and normal bounce-back | **Yes — this is the decisive readout** | Cleaved/full-length NRF1 ratio reduced ≥ 2-fold vs non-targeting at 4–8 h of 20 nM carfilzomib; PSMB5/PSMA1 mRNA induction reduced ≥ 40%; 20S chymotrypsin-like activity recovery at 24 h reduced; NGLY1 KO and DDI2 KO run in parallel as the positive comparators |
| 1 | Partner protein levels after INAFM1 KO (and NGLY1/DDI2 KO → INAFM1-Halo levels) | 2 wk | Co-destabilisation (would argue a/b) | Partners stable (favours c/d) — the expected outcome under our own type assignment | **Yes** | Western for NFE2L1 (both species), NGLY1, DDI2, VCP, RAD23B, UBQLN1; a ≥ 30% change is called |
| 2 | IP-MS / TurboID of tagged INAFM1 vs an unrelated tagged single-pass membrane control | 1–2 mo | NRF1-axis or shuttle-factor proteins enriched (SAINT BFDR ≤ 0.01) | Absent, or a different module appears (e.g. TRP/channel or cytoskeletal partners) | **Yes, conditional on Tier-1 passing** | TurboID preferred over IP-MS given a single-pass protein and likely transient contacts |
| 2 | BN-PAGE / SEC co-migration | 1 mo | INAFM1 co-migrates with an NRF1-axis species; KO changes the migration of NRF1 intermediates | Separate | Conditional | Low prior (no stable complex expected for type d) |
| 2 | Double KO with NGLY1 and with DDI2 (epistasis) | 1–2 mo | No extra defect beyond the single KO (same pathway) | Additive/synergistic (parallel pathways) | **Yes, conditional** | Growth and NRF1 readout in the 2×2 design; this is the test that distinguishes "in the pathway" from "parallel route into the same phenotype" |
| 2 | Arrayed CRISPRi Perturb-seq with NFE2L1/NGLY1/DDI2/VCP + INAFM1 | 2 mo | Transcriptional signatures cluster (proteasome-subunit programme) | Distinct signature | Optional | Replogle 2022 never measured INAFM1, so this would also fill the G-class gap that §6 records as "not measured" |
| 3 | TM-deletion and InaF-motif point mutants fail to rescue | 6–12 mo | Membrane anchoring / motif face required | Mutants rescue → the function is in the disordered tail | Later | Only after Tier 1–2 support |

Type-specific row (relationship type **d**; the b/c/e rows are deleted, but the **c** row is retained as the
alternative-explanation arm because type c is the strongest competitor, per §8):

| Type | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| c (alternative) | Bypass rescue: in INAFM1-KO cells, re-express a constitutively active, ER-independent NRF1 fragment (cleaved form, p95/Leu-104-truncated) | 1–2 mo | Bypass restores proteasome-subunit induction and growth → INAFM1 acts upstream of NRF1 cleavage (supplier/client of the processing step) | No rescue → INAFM1 acts elsewhere, or the dependency is not NRF1-mediated at all | **Yes** | PSMB5/PSMA1 induction restored to ≥ 70% of wild-type and competitive-growth dropout reduced by ≥ 50% |

## 5. Module readouts

The predicted module (GO:0031593 polyubiquitin modification-dependent protein binding / the NRF1 arm of it) is not one
of the listed rows, so the "Other" row applies:

| Module | Readouts |
|---|---|
| Other — polyubiquitin-dependent protein handling at the ER–proteasome interface (NRF1 axis) | (i) NRF1/NFE2L1 processing western: ratio of cleaved to full-length NRF1 after acute proteasome inhibition; (ii) proteasome "bounce-back": PSMA/PSMB transcript induction by RT-qPCR and recovery of 20S chymotrypsin-like activity (Suc-LLVY-AMC) after washout; (iii) accumulation of K48/K11-linked polyubiquitylated protein (western, TUBE pulldown); source papers: PMID:20385086 (bounce-back and Nrf1 requirement), PMID:27528193 and PMID:32521225 (DDI2-dependent cleavage; ubiquitin-dependence), PMID:29202016 (NGLY1 requirement), PMID:24448410 (p97/VCP-dependent retrotranslocation) — all verified rows in Appendix A |

**Chosen readout:** *cleaved / full-length NRF1 ratio plus PSMB5 and PSMA1 transcript induction at 4–8 h of 20 nM
carfilzomib*, with NGLY1-KO and DDI2-KO as positive comparators, MRPL55 as the matched-essentiality control, and
non-targeting guides as the negative.

## 6. Experiment that separates the alternative explanation

- **Alternative:** INAFM1 is a generic proteostasis-margin correlate (or a membrane-environment supplier) rather than a
  participant in polyubiquitin-dependent handling.
- **Experiment:** the Tier-1 essential-gene confound control plus the type-c bypass rescue, run together — acute
  INAFM1 depletion vs MRPL55 depletion at matched growth effect, each ± the pre-cleaved NRF1 fragment.
- **Readout if the prediction is right:** INAFM1 depletion blunts NRF1 cleavage and proteasome-subunit induction well
  beyond MRPL55 at the same growth inhibition, and the pre-cleaved NRF1 fragment rescues the transcriptional and
  growth phenotype.
- **Readout if the alternative is right:** INAFM1 and MRPL55 depletion move the readouts by the same amount (generic
  sickness), or INAFM1 depletion blunts the readout but the pre-cleaved NRF1 fragment does not rescue (the dependency
  runs through something other than NRF1 processing).

## 7. Decision rule (fixed in advance)

- **Supported:** dropout reproduced and rescued by guide-resistant cDNA **AND** the module-specific readout concordant
  (NRF1 processing / bounce-back blunted beyond the matched-essentiality control) **AND** localisation compatible
  (ER / nuclear-envelope / cytosolic-face membrane) **AND** Tier-2 physical or epistatic support (TurboID enrichment of
  NRF1-axis proteins, or non-additive epistasis with NGLY1 or DDI2).
- **Refuted:** dropout not rescued by the cDNA, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else — reported as such, with a proposed alternative relationship type (most likely c, with
  the bypass-rescue result deciding).

## 8. Evidence ledger (Part II)

| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| The cell lines, their effects, expression, CN, TP53 status, screen quality and media are as tabulated; the partner criterion was dropped because no line satisfies it | `reports/data/INAFM1/bundle.md` §10 | "Rank-1 partner used for the partner criterion: **NFE2L1**. Criterion applied: relaxed: partner criterion dropped (g <= -0.5)." and "Funnel: n_lines 1361; g_le_m0p5 4; plus_partner_le_m0p3 0; plus_expr_ge2 0; plus_not_amplified 0." (text read: file) | Y |
| MRPL55 is matched on effect in the two chosen lines and belongs to an unrelated module | recomputed † `results/m7/scratch_reports_inafm1/matched_ctrl.py` output | "MRPL55 -0.80 -0.98 -0.55 0.20" (text read: script output) | Y |
| NRF1 processing / proteasome bounce-back is a validated assay for this module | PMID:20385086 | "is necessary for induced proteasome gene transcription in mouse embryonic fibroblasts (MEFs)" (text read: abstract) | Y |
| The cleavage step that the assay reads out is DDI2-dependent and ubiquitin-dependent | PMID:27528193; PMID:32521225 | "the aspartyl protease DNA-damage inducible 1 homolog 2 (DDI2) is required to cleave and activate Nrf1"; "DDI2 is indeed capable of cleaving NRF1 in vitro but only when NRF1 protein is highly poly-ubiquitylated" (text read: abstracts and full texts) | Y |
| NGLY1 loss blunts the same readout (positive comparator) | PMID:29202016 | "the cytosolic enzyme N-glycanase 1 (NGLY1, the human PNGase) is essential for Nrf1 activation" (text read: abstract and full text) | Y |
| The cleaved NRF1 species used for the bypass-rescue arm is generated N-terminal to Leu-104 and is no longer membrane-tethered | PMID:24448410 | "cleaved N-terminal to Leu-104 to yield a fragment that is no longer tethered to the ER membrane" (text read: abstract and full text) | Y |
| Guide-level DepMap data are unavailable, so per-guide checks are done inside the experiment | `reports/data/INAFM1/bundle.md` §5 | "Shared-sgRNA / per-guide check | not possible | guide-level data not available (recorded)" (text read: file) | Y |
| Predictomes gives no confident interface between INAFM1 and any top-10 partner (low prior for Tier 0) | `results/m7/scratch_reports_inafm1/predictome_INAFM1.csv` (from `data/raw/predictomes2025/…csv.gz`) | best row "INAM1_HUMAN__TM100_HUMAN__276aa,C9JVW0:Q9NV29,0.284,0.020,78,365,0,0,0,0"; no row pairs C9JVW0 with NFE2L1, NGLY1, DDI2, RAD23B, VCP or UBQLN1 (text read: file) | Y |

## 9. Red-team review (Part II)

Separate agent; asks what would make the experiment uninformative (off-target guides, proximity effects, lineage
dependence, rescue failure, assay insensitivity). Appended unedited.

- Reviewer / model / date: **pending**
- Review text: **pending**
- PI response (separate): **pending**
