# Red-team review — reports/INAFM1.md

- Reviewer: adversarial reviewer agent (role `red_team`), model Claude Opus 5.5
- Date: 2026-10-30
- Scope: Appendix A + Part II ledgers, every number against the cited project file, hypothesis attack, experiment plan.
- Independence: reviewer did not write the report; all checks re-run from primary sources (Europe PMC REST, UniProt,
  AlphaFold DB, `data/raw/*`, `results/ledger/*`, `results/m7/*`).

---

## 1. Ledger spot-check (26 rows checked; Appendix A has 26 rows, so this is a full audit, not a sample)

**Method.** Each PMID resolved via `EXT_ID:` query to the Europe PMC REST API (`resultType=core`); the quoted span was
matched case- and whitespace-normalised against title+abstract, then against full text (`/{PMCID}/fullTextXML`), then —
where EPMC returns no full text — against an exact-phrase full-text search. Project-file rows were grepped from the
cited file.

| # | Row (abbreviated) | Source | Result |
|---|---|---|---|
| 1 | 142 aa, single-pass, TM 36–56, PF15018/IPR029162, no FUNCTION | UniProt C9JVW0 + bundle §8 | **PASS** |
| 2 | pLDDT 59.5, AFDB v6 | `af_C9JVW0.json` | **PASS** (59.47, latestVersion 6) |
| 3 | Only GO row is IEA CC membrane | GOA 2026-05-21 | **PASS** (`INAFM1 located_in GO:0016020 GO_REF:0000044 IEA 20260428`, sole row) |
| 4 | InaF motif conserved nematodes→humans | PMID:17968007 | **PASS** (abstract) |
| 5 | fly inaF = TRP auxiliary subunits | PMID:32434796 | **PASS** (abstract) |
| 6 | "INAFM1 (not studied in this article) and ROME (INAFM2)" | PMID:41650465 | **PASS** (full text PMC13012068) |
| 7 | ROME KO not associated with growth dependence, 24 lines | PMID:41650465 | **PASS** (full text) |
| 8 | prostate prognosis gene list | PMID:30866732 | **PASS** (abstract) |
| 9 | PRR24 in neuropathic-pain DE list | PMID:36816032 | **PASS** (abstract) |
| 10 | NFE2L1 bounce-back | PMID:20385086 | **PASS** (abstract) |
| 11 | p97/VCP retrotranslocation | PMID:24448410 | **PASS** (abstract) |
| 12 | NGLY1 essential for Nrf1 activation | PMID:29202016 | **PASS** (abstract) |
| 13 | NGLY1 sequence editing of SKN-1A | PMID:31002798 | **PASS** (abstract) |
| 14 | DDI2 cleaves/activates Nrf1 | PMID:27528193 | **PASS** (abstract) |
| 15 | DDI2 needs poly-Ub NRF1 | PMID:32521225 | **PASS** (abstract) |
| 16 | Ddi2 ERAD shuttling factor | PMID:35358511 | **PASS** (abstract) |
| 17 | AKIRIN2 nuclear proteasome import | PMID:34711951 | **PASS** (abstract) |
| 18 | Wainberg 2021 benchmark | PMID:33859415 | **PASS** (title/abstract; absence of INAFM1 in retrieved text is correctly flagged as "not verified absence") |
| 19 | hu.MAP 3.0; INAFM1 absent | PMID:40425816 + `data/raw/humap3/*` | **PASS** (0 matches for INAFM1/C9JVW0 in complexes CSV and pair files) |
| 20 | Replogle 2022; g not measured | PMID:35688146 + `support_sources.tsv` | **PASS** |
| 21 | Predictomes: **81** pairs, best kirc 0.284 (TMEM100) | `predictome_INAFM1.csv` | **FAIL (minor)** — the file holds **82** unique data rows, no header. Best row and partner-absence claims are correct. |
| 22 | Raw Chronos r: NGLY1 0.214, DDI2 0.168, NFE2L1 0.117 | `depmap_checks.out` | **PASS as quoted**, but see §1.1 — materially incomplete |
| 23 | MRPL55 matched control −0.80 / −0.98 | `matched_ctrl.py` out | **PASS** |
| 24 | All §1–§6 numerics from bundle | `reports/data/INAFM1/bundle.md` | **PASS** except §1.2 below |
| 25 | p_cal definition; calibration not poor | DESIGN.md L178–179; `holdout_eval/SUMMARY.md` L14 | **PASS** (span is split across a line break in DESIGN.md but is verbatim) |
| 26 | Judging: real 0, decoys 0, d = 0 | `judge/analysis_main_genes.tsv`, J1/J2 `main3` | **PASS** (`J082 HGNC:27406 INAFM1 top40 37 0.0 0.0 0 0.0 N3`; all four slots "Not addressed by the evidence") |

**Failures: 1 of 26 (row 21, off-by-one).** No fabricated PMID, no fabricated span, no DOI mismatch. Ledger quality is
high; the problems below are omission and framing, not invention.

### 1.1 Material omission inside a "verified" row (row 22)

The same script output (`results/m7/scratch_reports_inafm1/depmap_checks.out`) that supplies the quoted correlations
also contains:

```
INAFM1 vs RAD23B pearson r=-0.009   INAFM1 vs VCP pearson r=0.052   INAFM1 vs UBQLN1 pearson r=-0.007
```

**RAD23B, VCP and UBQLN1 are the only three partners annotated to the predicted term GO:0031593** — i.e. the three
genes that actually generate the label have raw Chronos correlations with INAFM1 of essentially zero. The report quotes
raw correlations only for the three partners that are *not* in the term. §3 of the report presents the raw-correlation
row as an honesty check ("the honest point visible"); as written it is selective. This is the single most important
required fix.

### 1.2 Omitted pipeline output that contradicts the narrative

`reports/data/INAFM1/bundle.md` §2 records **V1 label: GO:0005643 nuclear pore; V1′ label: GO:0005643 nuclear pore
(supporting partners 2)**. The report never states this. The companion BICRAL report leans heavily on its V1′ label
(GBAF) as "the most informative output for this gene"; suppressing the INAFM1 V1′ label — which points at the nuclear
pore, not the ER–proteasome interface — is asymmetric reporting of the same pipeline field.

### 1.3 Smaller inaccuracies

- §2 calls the shared motif "a 32-aa motif"; PMID:41650465 describes the INAFM1/ROME–INAF homology as "approximately
  21 amino acids". The 32-aa figure is not sourced in Appendix A.
- §7 "DepMap-derived" audit lists PMID:35271393 as background, but that PMID appears in no Appendix A row; it is cited
  in the body without a ledger row (the appendix preamble claims every non-ledger claim has a row).

---

## 2. Numbers against project files

All of the following reproduce exactly: mean/SD −0.080/0.133, median −0.081, p5 −0.295, min −0.942, 4/1361 < −0.5
(0.0029), NaN 0.0000, expression 99.7%/88.1%, median 2.92, ρ = −0.107 (n = 1292), R(g) = 0.192 with p = 0.0050 and RBO
0.493, lineage table (Skin 75/−0.146/p 0.0000; CNS 133/−0.116/0.0015; Eye 15/−0.106/0.6612), top-10 partner table
(zavg_BEF, z_B/z_E/z_F, GLS ranks, in_term flags, CN r values), S = 22.044, p_emp 0.0020, LOPO 2/3, 1/3, 1/3, hub share
0.00, TF OR 0.51 (p 0.8592), TP53 p 0.2236, GLS top term GO:0006869, K=10 same / K=50 GO:0061136, lineage leave-out to
GO:0006778 with overlap 0.56, P-class p = 1.0000 with 42 members tested, STRING-exp sole interactor AGO2, 41 network
edges / 4 physical, cell-line table and funnel (4 → 0), p_cal 0.0367 [0.016–0.060], rank 37, demoted/lineage_leaveout.

**One discrepancy of substance is a self-report, not an error**: `top40_primary.tsv` confirms `in_support` and
`demoted True lineage_leaveout`; the report states both.

---

## 3. Attack on the hypothesis

### 3.1 The term and the story are supported by disjoint, individually weak evidence

The report's own structure concedes this (§4 "most important structural fact"), but it under-rates the consequence:

- The **label** GO:0031593 comes from RAD23B (12.91), VCP (5.05) and UBQLN1, whose **raw** co-dependency with INAFM1 is
  r ≈ 0.00, −0.01 and 0.05. VCP is common-essential (99.9% of lines < −0.5): a near-invariant column contributes almost
  no usable covariance and is a classic whitening artefact magnet.
- The **story** (NRF1 axis) comes from NFE2L1/NGLY1/DDI2, which are **not three independent observations**. Recomputed
  from `CRISPRGeneEffect.csv`: NGLY1–DDI2 r = 0.536, NFE2L1–DDI2 r = 0.475, NFE2L1–NGLY1 r = 0.436. They are one tight
  co-dependency block. INAFM1's attachment to that block is a single weak axis (r = 0.117–0.214), counted three times in
  the report's rhetoric ("ranks 1–3 are the three proteins of one pathway").

So: three partners that carry the term but not the signal, and three partners that carry the signal but not the term,
with p_cal attached only to the former. The report says this once and then argues from the latter throughout §0, §7 and
Part II.

### 3.2 The hub check gives false reassurance

The §4.3 hub rule is computed over **term-supporting** partners only (hub share 0.00, 0 hub partners). But the
signal-carrying partners are near-hubs: in-degree 63 (NFE2L1), 73 (NGLY1, flagged HUB), 65 (DDI2) against a
partner-population median of 26 and 99th percentile of 67 (n = 14,417 partner rows in `u_partners.tsv`). All three sit
in the top ~1.7% of in-degree, and they appear in the top-10 of 11, 12 and 9 of the 4,271 U genes respectively. The
narrative-bearing neighbourhood is therefore exactly the part of the graph the hub check does not protect. The report
should say "the hub rule does not cover the partners I argue from", not "hub-driven call: pass".

### 3.3 Lineage / heme alternative is stronger than the report allows

Removing Skin flips the top term to GO:0006778 porphyrin metabolism — and the bundle shows why: NFE2L1's own top
annotations are `GO:0006783 heme biosynthetic process; GO:0006779 porphyrin-containing compound biosynthetic`. The two
competing labels are generated by the *same* partner carrying different annotation sets. That is not "the replacement
term left the biology entirely"; it is "the term is whatever annotation set the one strong partner happens to carry in
that refit". With N(g) overlap only 0.56 and GLS giving lipid transport, three statistics give three biologies.

### 3.4 Flat profile → the four "dependent" lines may be screen outliers

Panel SD is 0.133; the two chosen lines sit at −0.79 and −0.94, i.e. 5–6 SD from the mean of an otherwise flat
distribution, in a gene with no paralogue buffering explanation offered. For such genes, extreme single-line Chronos
values are routinely screen artefacts (clone effects, low guide efficiency, outlier normalisation). The report does not
consider this, although it is the most likely reason Tier 1 would fail. `INAFM2` **is** present in the DepMap matrix
(`INAFM2 (100505573)`; mean +0.154, 0 lines < −0.5, r with INAFM1 = −0.010) — a free negative control the report does
not use, and a partial answer to the guide-cross-reactivity worry it raises in §8.

### 3.5 Internal inconsistency on paralogue function transfer

§2 correctly refuses to transfer fly INAF function to INAFM1 ("sharing a 32-aa motif is not sharing a function"), then
§7.3 and §4 use **AKIRIN1** (rank 6) as proteasome-axis corroboration *via its paralogue AKIRIN2*'s 20S-import
function. AKIRIN1 has no such published role. The same rule should apply in both directions; as written, paralogue
transfer is rejected when it hurts the hypothesis and accepted when it helps.

### 3.6 Literature search

Re-run independently: `TITLE_ABS:"INAFM1" OR "PRR24" OR "InaF-motif"` returns 5 records (the two omics lists, the two
collision papers correctly excluded by agent L, and PMID:17968007); no functional paper exists, and no paper links
INAFM1 to NRF1/NGLY1/DDI2/proteasome/ubiquitin. **The N3 call and "no prior prediction list" statements survive.** No
missing key literature found. `results/m7/L/HGNC_27406.md` matches the blinded summary in §7 (3 items, all level
*mention*, all DepMap-derived = no, with explicit collision exclusions).

### 3.7 Overclaiming

The report is careful about physical interaction (type a is explicitly refused; "none of the solid edges touches
INAFM1"). The overclaim is elsewhere: §0's headline sentence ("behaves … like a member of the pathway that handles
polyubiquitylated proteins at the ER–proteasome interface") and the ER localisation assumption. **No evidence places
INAFM1 in the ER.** UniProt says only "Membrane … Single-pass" (ECO:0000305, curator inference); HPA has no entry;
OpenCell/HCM have no tag. The ER–proteasome interface is an inference from partner compartments, and the one published
family member (INAFM2/ROME) is a **plasma-membrane** glycoprotein. "ER–proteasome interface" should appear only as the
hypothesis to be tested, never in the claim sentence.

---

## 4. Experiment plan (Part II)

Strengths: the gate structure is right (dropout + rescue before anything else), the matched-essentiality control is
required rather than optional, lines are deliberately non-Skin, and the refusal to invent guide sequences is correct.

Problems:

1. **Both matched-essentiality controls are mitochondrial.** MRPL55 (mitoribosome) and the fallback RPUSD4
   (mitochondrial RNA pseudouridylation) both cause OXPHOS failure, which activates the integrated stress response and
   perturbs proteostasis and proteasome-subunit transcription — the exact readout. The control is thus anti-correlated
   with informativeness: it may move the NRF1/bounce-back readout for its own reasons and mask a true effect, or move
   it so much that any INAFM1 effect looks unremarkable. Required: a non-mitochondrial, non-proteostatic matched gene
   (e.g. an unrelated trafficking or splicing-independent gene at the same per-line Chronos value), or at minimum two
   controls from different modules with the ISR (ATF4/CHOP) measured alongside.
2. **The decisive readout tests the wrong object.** NRF1 processing reads the rank-1–3 axis, which is *not* the
   calibrated term and *not* what p_cal covers. A clean negative leaves GO:0031593 untouched (UBQLN1/RAD23B-type
   shuttle function would be unaffected). Add a readout for the term itself — e.g. K48/K11 poly-Ub conjugate handling
   and shuttle-factor engagement (TUBE/UBQLN1-RAD23B pulldowns) — or state plainly that the experiment tests the
   interpretation rather than the prediction.
3. **The chosen lines do not co-drop with the readout's pathway.** In ACH-002837 NFE2L1 = +0.13 and in ACH-000956
   NFE2L1 = −0.28 (`depmap_checks.out`); neither line is NRF1-axis-dependent. If NRF1 processing is unperturbed, the
   plan cannot distinguish "INAFM1 is not in the pathway" from "this line does not need the pathway". Add an
   NRF1-axis-dependent line (e.g. one where NGLY1/DDI2 are dependencies) as a positive-context arm.
4. **ACH-002837 (HCM-BROD-0100-C15) is an HCMI organoid-derived model** cultured in OPAC:Ad+++; degron knock-in,
   clonal selection, CUT&RUN-grade cell numbers and 21-day competitive growth in such a model are far more demanding
   than the €25–35k / 8-week budget implies. 22Rv1 plus JM1 (the backup) would be a more realistic pair; keep the
   organoid line as confirmation only.
5. **Tier-0 AF-Multimer is correctly down-weighted but still listed first**; with pLDDT 59.5 and 82 Predictome pairs at
   max kirc 0.284, it will consume time and produce an uninterpretable negative. Fine as written only because the row
   says so.
6. **Falsification asymmetry.** §9.1 is falsifiable; §9.2 ("no co-purification") is weak for a 142-aa single-pass
   protein with transient contacts, as §6 itself argues ("no support here mostly means not looked at"). The decision
   rule's "Refuted" branch (incompatible localisation in both lines) is the only crisp one; the "Supported" branch
   requires Tier-2 evidence that the report's own priors say is unlikely to appear.

---

## 5. Verdict

**ACCEPT WITH REVISIONS.** The report is unusually honest about its weaknesses (flat profile, lineage failure, GLS
disagreement, no orthogonal support, N3 judging tie) and its ledger is 25/26 clean. It is not acceptable as written
because the evidence that carries the calibrated label and the evidence that carries the narrative are disjoint, and
only the favourable half of an already-computed correlation table is reported.

### Required fixes

1. **Report the raw Chronos correlations for the term-carrying partners** (RAD23B r = −0.009, VCP r = 0.052, UBQLN1
   r = −0.007) in §3/§4 and in Appendix A row 22, next to the three already given; state explicitly that GO:0031593 is
   generated by partners with near-zero raw co-dependency, and that VCP is common-essential.
2. **Restate the hub check as not covering the lead partners.** Give the in-degree percentiles (NFE2L1 63 ≈ 98.3rd,
   NGLY1 73 ≈ 99.4th, DDI2 65 ≈ 98.6th; population median 26, p99 67) and the fact that NFE2L1/NGLY1/DDI2 are mutually
   correlated at r = 0.44–0.54, so ranks 1–3 are one axis, not three.
3. **Report the suppressed V1/V1′ label (GO:0005643 nuclear pore)** from bundle §2, and drop "ER–proteasome interface"
   from the claim sentence in §0 and §1 (keep it as the hypothesis to be tested); no evidence localises INAFM1 to the
   ER.
4. Fix Predictomes 81 → 82 pairs; add a ledger row for PMID:35271393; drop or source the "32-aa" motif length
   (PMID:41650465 says ~21 aa); remove the AKIRIN1-via-AKIRIN2 inference or apply the same no-paralogue-transfer rule
   used for INAFM2.
5. **Experiment:** replace or supplement the mitochondrial matched controls; add a term-level readout (poly-Ub
   conjugate handling / shuttle engagement) alongside NRF1 processing; add one NRF1-axis-dependent line; use INAFM2
   (present in the matrix, r = −0.010 with INAFM1) as a free specificity control for guide cross-reactivity; reconsider
   the HCMI organoid line as a primary engineering target.
