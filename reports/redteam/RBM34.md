# Red-team review — reports/RBM34.md

- Reviewer: adversarial reviewer agent (role `red_team`), model Claude Opus 5.5
- Date: 2026-10-30
- Scope: Appendix A + Appendix C.8 ledgers, every number against the cited project file, hypothesis attack, experiment plan.
- Independence: reviewer did not write the report. All checks re-run from primary sources (Europe PMC REST
  `EXT_ID:`/`fullTextXML`/exact-phrase search, Crossref, AlphaFold DB, GOA GAF, `data/raw/*`, `results/ledger/*`,
  `results/m7/*`, and `data/derived/matrices/zavg_full/zavg_BEF.npy`). The report's own
  `verify_spans.log` was **not** taken as evidence; every span below was re-fetched.

---

## 1. Ledger spot-check (25 of the 35 Appendix A rows + all 9 Appendix C.8 rows)

**Method.** PMID resolved via Europe PMC `EXT_ID:` (`resultType=core`); span matched case-, whitespace- and
dash-normalised against title+abstract, then full text; where EPMC serves no full text, an exact-phrase EPMC search was
used. Project-file rows were read from the cited file.

| # | Row | Source | Result |
|---|---|---|---|
| 1 | E1 "Nop12 x RBM34 Important for 5.8S folding Talkish et al ( 2014 )" | PMID:36762427 | **PASS** (full text PMC10068337; I also read the surrounding table to confirm the column order is yeast → human, so the orthology reading is correct, not inferred) |
| 2 | E2 title span, Pwp1/Nop12 5.8S folding | PMID:24636992 | **PASS** (title) |
| 3 | E3 "Deletion of NOP12 significantly inhibits 27SA(3) pre-rRNA processing…" | PMID:24636992 | **PASS** (abstract) |
| 4 | E4 "In the absence of Nop12 and Pwp1, rRNA helix 5 is not stably formed." | PMID:24636992 | **PASS** (abstract) |
| 5 | E5 Nop12-tagged particles cluster with Nog2/Rix1 | PMID:35139378 | **PASS** (full text) |
| 6 | E6 "PWP1 Pwp1 Structural RBM34 Nop12 Structural" | PMID:35925480 | **PASS** (full text, table) |
| 7 | E9 HCC knockout phenotype | PMID:36643033 | **PASS** |
| 8 | E10 FGFR2 / PI3K-AKT | PMID:36643033 | **PASS** |
| 9 | E11 osteosarcoma knockdown | PMID:38058813 | **PASS** (EPMC returns no DOI for this record; the report claims none, so no mismatch) |
| 10 | E12 CMSS1–RBM34–DDX5 / hTERT | PMID:39710061 | **PASS** |
| 11 | E13 "The network neighborhood of RBM34 was enriched for genes involved in rRNA processing" | PMID:39663389 | **PASS** — EPMC `fullTextXML` for PMC12036749 errors (HTTP 500); exact-phrase search returns hitCount 1, that PMID. Verified, but by a different route than the report's script. |
| 12 | E14 MERS nsp3.2 rRNA-processing interactors | PMID:34186245 | **PASS** (full text) |
| 13 | E15 NUMA1/NS1 influenza interactors | PMID:30572664 | **PASS** (full text) |
| 14 | E16 WDR89 nucleolar / interacts with nucleolar proteins | PMID:42848503 | **PASS as quoted** — but materially incomplete; see §1.1. |
| 15 | E17 PWP1 Pol I rRNA transcription | PMID:29065309 | **PASS** |
| 16 | E18–E22 DDX31/CEBPZ/TCOF1/PINX1/RPF1 factor-table rows | PMID:36762427 | **PASS** (all five found in full text) |
| 17 | E23 5S RNP / p53 | PMID:24120868 | **PASS** |
| 18 | E24 p53-independent processing defects | PMID:23973377 | **PASS** (abstract) |
| 19 | E25 Wainberg "108 uncharacterized genes" | PMID:33859415 | **PASS** |
| 20 | E26–E29 Brunello / Cas-OFFinder / dTAG / AID2 | PMIDs 26780180, 24463181, 29581585, 33177522 | **PASS** (all four) |
| 21 | E30, E32 Crossref titles | 3 DOIs | **PASS** (titles match Crossref exactly) |
| 22 | E31 pLDDT 69.44, model v6 | `af_P42696.json` | **PASS** (`globalMetricValue` 69.44, `latestVersion` 6) |
| 23 | E33 GOA IBA row to GO:0000463 | `goa_human.gaf.gz` | **PASS** (`RBM34 involved_in GO:0000463 GO_REF:0000033 IBA P 20221209`, exact) |
| 24 | E34 GO:0000463 not a descendant of GO:0006354 | `go_anc.py` re-run | **PASS** (re-executed; output matches the quoted line) |
| 25 | E35 TP53 not a genome-wide shift | `tp53_global.txt` | **PASS** (median −0.0007; RBM34 percentile 0.945) |
| 26 | C.8 cell-line / CAMLG / PWP1 rows | `ctrl_lines.txt`, bundle §10 | **PASS** (CAMLG −0.63/−0.55, PWP1 −0.91/−0.91, RBM34 −0.62/−0.54) |

**Failures: 0 of 34 on verbatim-span grounds.** No fabricated PMID, no fabricated span, no DOI mismatch, no
misattributed quotation. The yeast *Nop12* claims specifically called out for scrutiny (E1–E6) are all genuine, and E1's
table orientation is correct. The problems below are **selective quotation and omission**, not invention.

### 1.1 Selective quotation inside a "verified" row (E16) — most important required fix

The abstract of PMID:42848503, from which E16 is drawn, continues past the quoted sentence:

> "Depletion of WDR89 leads to accumulation of p53 in the nucleus, p21 accumulation and G2/M cell cycle arrest 24 hours
> post-irradiation."

WDR89 is the **rank-1 co-essentiality partner** (zavg 16.39) and the report's headline novelty claim. The one sentence
from that abstract the report does not quote is the one that bears on the report's own unresolved TP53 flag: the rank-1
partner has a published p53-accumulation / p21 / arrest phenotype. §5's "honest reading" argues the p53 flag is
*informative about mechanism* for nucleolar genes generally; it should say that the partner the report leans on hardest
is already documented as a p53-arrest trigger, which is an alternative route to the same co-dependency that does not
require the nucleolar-module reading.

The same abstract also shows that E16 is itself a **DepMap-correlation paper** ("Dependency Map correlation analysis
reveals WDR89…"), published 2026-10-08 (pre-freeze). §7 presents WDR89 as "until now unstudied" and §11 presents it as
what is new here. The dating is handled correctly, but the method provenance is not stated.

### 1.2 The p53 axis is inside N(g), and the report does not say so

Recomputed from the project's own matrix (`data/derived/matrices/zavg_full/zavg_BEF.npy`), RBM34's unfiltered top-25
neighbourhood contains **RPS27L (rank 15, z 7.61) and MDM4 (rank 18, z 7.37)**; WDR89's own top-25 contains **MDM4
(10.99), PPM1D (9.96), MDM2 (7.54), RPS27L (8.06)**. The report publishes only the top 10, where no p53-axis gene
appears, and then argues in §5 and §8 that the p53 signal is a downstream consequence of impaired ribosome biogenesis.
That argument is weakened by the fact that canonical p53-axis genes are *themselves* neighbourhood members. This is the
single strongest unaddressed alternative explanation for this gene and it is checkable in one line of code.

### 1.3 Selective reporting of Predictomes (§6, "reported but not counted")

The report lists RBM34's Predictomes pairs as "PWP1 spoc 0.976 … followed by NOC2L 0.807, ABT1 0.622, WDR46 0.605,
RBM28 0.578". Re-read from `data/raw/predictomes2025/20251110_hs_predictome_pair_scores.csv.gz`, the true descending
order is:

```
PWP1 0.976 | NOC2L 0.807 | SRP72 0.675 | SRSF5 0.653 | ABT1 0.622 | WDR46 0.605 | PKHA4 0.601 | MYCN 0.598
```

SRP72, SRSF5, PKHA4 and MYCN — none nucleolar-biogenesis — have been dropped from a list presented as a ranked tail,
and RBM34–RBM28 (0.578) is promoted into fifth place. The PWP1 top hit is real and is the striking part; the filtered
tail makes the convergence look cleaner than it is. Contrast with the C5orf34 report, which lists its Predictomes top 4
complete and unfiltered.

### 1.4 Asymmetric per-pair reporting of Burke 2023 vs Predictomes

§6 says Burke 2023 modelled 21 pairs with "none with pDockQ ≥ 0.23" and gives no per-pair numbers, while giving four
decimal-precision Predictomes scores. The bundle's own pair table has **RBM34–PWP1 pDockQ 0.138** (the best of the 21)
and RBM34–DDX31 0.049. Stating that PWP1 is also Burke's best RBM34 pair would be fairer to the hypothesis *and* a
sharper calibration of the Tier-0 expectation in C.4 ("a PWP1 interface at ipTM ≥ 0.5"), which currently has no stated
prior from the one AF2 dataset already in hand.

### 1.5 Smaller inaccuracies

- §7 / §11: "not among the **1,974 rows** of `annotated_embedding_coordinates.csv`". The file has 1,974 *lines*
  including a header, i.e. **1,973 rows**. (Same off-by-one appears in the C5orf34 report.)
- §2: the AlphaFold banding "30.9% very high, 23.5% low, 27.7% very low" silently drops `fractionPlddtConfident`
  = 0.179. The three quoted figures are exact; the set is incomplete.
- §1 / §5: the bundle records **22 paralogues of RBM34 in the matrix**; the report never states this and C.3's
  off-target acceptance criterion lists only partner loci. For an RRM-family gene with 22 matrix paralogues, guide
  specificity against paralogues belongs in the acceptance rule. (The C5orf34 report *does* use its 0-paralogue count
  as an argument, so the omission here is asymmetric.)
- §11 / §1: the report gives rank 5 (primary top 40) and never mentions that in the clean-first sensitivity list
  (`results/ledger/top40.tsv`) RBM34 is **rank 29**. Both numbers are in the project files; the reader of a single
  report cannot tell how fill-order-dependent the rank is.
- E7's provenance: the UniProt nucleolar annotation is `ECO:0000269/PubMed:12429849` — Scherl et al. 2002, *Functional
  proteomic analysis of human nucleolus*, whose abstract states it "permitted the assignment of hypothetical functions
  for 43 proteins for which no functional information is available. Notably, a role in ribosome biogenesis was proposed
  for 31 proteins." The report cites the UniProt line but never the primary paper, and never checks whether
  KIAA0117/RBM34 is one of those 31. Given that §11 turns on how much of this function was already proposed, that check
  is required before the novelty paragraph can stand. (I could not retrieve the 2002 full text here — subscription
  only in EPMC — so this is an open item, not a finding against the report.)
- GOA also carries `RBM34 located_in GO:0005730 GO_REF:0000052 IDA C 20251115` and two HDA rows for GO:0003723. The
  report's D1 = True ("no informative GO BP/MF/CC") is the frozen pipeline's call, but a reader weighing "how dark is
  this gene" should be told there is an experimental (IDA) nucleolus annotation, since the supporting L class is
  precisely a localisation argument.

---

## 2. Numbers re-checked against files

Every machine number I could re-derive matches. Specifically re-verified against `reports/data/RBM34/bundle.md`,
`results/ledger/*`, `results/m7/judge/*`, `DESIGN.md`, `DEVIATIONS.md`, `results/ledger/M6_SUMMARY.md` and raw data:

- Profile: mean/SD −0.226/0.191; frac < −0.5 0.0705 (96/1361); median −0.218; 5th pct −0.544; min −1.357; ρ(effect,
  expression) −0.013 (n = 1292); R 0.480, R0 max 0.080, p 0.0050, RBO 0.394. **all match**
- Partners: every zavg, z_B/z_E/z_F, GLS rank, mean effect, frac, band and distance in §4 matches `u_partners.tsv`
  row for row; RPF1 distance 150,632,000 bp. **match**
- Supporting partners POLR1E/POLR1H/POLR1G/POLR1A/POLR1B with CN r −0.00/0.01/0.08/0.03/−0.01. **match**
  (`u_flag_partners.tsv`)
- Top-5 terms, S 47.498, sizes 54/21/13, LOPO 2/5, p_emp 0.0020. **match**
- Orthogonal: P_group 2 vs 2.730 p 0.7652; HCM-SAINT 2 vs 0.140 p 0.0070; class P Simes 0.0140; ProteomeHD 0.774 vs
  0.643; CCLE 0.636 vs 0.511; HPA 1.000 vs 0.518; Perturb-seq 0.538 vs 0.639 p 0.9930; 54 members. **match**
- TP53: p 1.38e-05, median diff +0.0346, 902/459, genome-wide percentile 0.945, per-line means −0.149 / −0.1486;
  partner diffs DDX31 +0.133, WDR89 +0.078, RPF1 +0.075, PWP1 +0.071. **match** (`tp53_partners.txt`, `tp53_global.txt`)
- DEMETER2: 5 partners, mean r 0.041 vs null 0.058; recomputed best pair PWP1 r 0.125 n 593; POLR1G/POLR1H absent.
  **match** (`d2_pairs.txt`)
- M6: DEMETER2 fails 182/204 measured. κ = 0.975 over 360 statements; real 18 supported, decoys 3/120, p 0.0002174;
  J084 slots A–D all 0 with the quoted justification verbatim in `J2_main3.tsv`. **match**
- DEVIATIONS 2026-10-30 row: "ascending GO id (deterministic)". DESIGN §5.4 ribosome biogenesis/translation → G or L.
  **match**
- hu.MAP 3.0: `huMAP3_04541.1,1,P42696 Q68D10,SPTY2D1 RBM34` — one complex, confidence 1. **match**
- Recall probe verbatim, lines/media/CN/NNMD table, network edge counts (47 edges, 15 physical). **match**

I found **no numeric error** other than the 1,974/1,973 off-by-one in §1.5.

---

## 3. Attack

### 3.1 Is this a rediscovery, and is the report honest about it?

**Yes, and yes — with one framing problem.** The substantive function (Nop12-like 60S maturation factor) is already
(i) in two review tables by orthology [E1, E6], (ii) in GO as an IBA annotation to GO:0000463 [E33], and (iii) partly
recalled by the LLM probe itself ("possibly nucleolar or involved in ribosome biogenesis"). The report says so, in §0,
§1, §7 and §11, in plain words ("closer to a rediscovery than to a novel call"). That is more candid than most of the
pass and I do not propose to soften the ACCEPT on these grounds.

The framing problem is the order of §0. The **Claim** bullet leads with the Nop12/60S-maturation reading — which is a
literature transfer, not the method's output — and the fact that the method predicted something else (GO:0006354) is
deferred to the *Confidence* and *Strongest reason to doubt* bullets. A bench reader skimming §0 will credit the
pipeline with a claim the pipeline did not make. The fix is one sentence, not a rewrite: state in the Claim bullet that
the method's output is the Pol I transcription-elongation label and that the maturation reading comes from the
orthologue literature.

### 3.2 "Transcription elongation" vs Pol I vs ribosome biogenesis

**Handled correctly, and this is the best part of the report.** §4's "Which module does the evidence really point to?"
is exactly right: the five supporting partners are all POLR1 subunits (verified in `u_flag_partners.tsv`); GO:0006354 is
reached only through its descendant GO:0006362 (verified by re-running `go_anc.py`); the three top terms are tied on S
and partner set; the tie-break is ascending GO id (verified in DEVIATIONS); and K = 50 moves the label to GO:0006360
(verified in the bundle). Calling the label "a vocabulary artefact of the tie-break rule" is accurate and unusually
honest. The report also states that a future experimental GO:0000463 annotation would score as a **miss** for the
predicted term — i.e. it concedes its own p_cal is pointed at the wrong branch.

One thing is missing. The GLS network row in §5 reads "**different** | top term on the GLS neighbourhood is GO:0006816
calcium ion transport", and that is the end of it. Every other check failure gets a paragraph of honest reading; this
one gets none — even though the holdout found zavg − GLS = +0.006 with a CI including 0 (`holdout_eval/SUMMARY.md`),
i.e. GLS is not a weaker method on H, and the GLS ranks of the Pol I partners in this gene's own table are 434, 3155
and 2920. Under a decorrelated neighbourhood the module does not merely shift, it vanishes. This deserves a paragraph
in §8, not a table cell.

### 3.3 DEMETER2 non-replication and the TP53 flag

*DEMETER2.* The report's defence is correct on the facts (182/204 measured pool genes fail; PWP1 is the best
recomputed pair at r 0.125) and correctly labelled a failure. No objection.

*TP53.* The direction (KO less damaging in TP53-mutant lines) and the shared direction across all ten partners are
real and verified. The nucleolar-stress reading [E23] is plausible. But §1.1 and §1.2 above are both unaddressed: the
rank-1 partner is published as a p53-arrest trigger, and two p53-axis genes sit in N(g) at ranks 15 and 18. The honest
conclusion is weaker than the report's — part of this neighbourhood may be a *p53-surveillance co-dependency block*
that includes nucleolar genes, rather than a nucleolar block that happens to signal through p53. The experiment already
mitigates this (TP53-mutant lines, p53-independent readout), so the fix is to the text, not the plan.

### 3.4 Relationship type

Type **a** by the frozen rule, argued to **b**. The argument is sound and the evidence is laid out fairly: the only
term-member physical edges are 2 Human Cell Map SAINT edges, in a map where pre-ribosomes and Pol I co-purify, and the
P_group test actually comes in *below* its null (2 vs 2.730, p 0.7652) — i.e. the entire P-class support is one source
with two edges. The report states all of this. Good.

### 3.5 Experiments (Appendix C)

Strong plan: the dual-channel degron readout genuinely separates the two hypotheses, CAMLG is matched per-line (not
just genome-wide) and verified, PWP1 is the right comparator, and the decision rule is fixed in advance. Weaknesses:

1. **Guide specificity vs the 22 matrix paralogues** (§1.5) is not in the C.3 acceptance criterion.
2. **Tier-0 has no stated prior** although Burke's RBM34–PWP1 pDockQ (0.138) is in the bundle (§1.4).
3. **Falsifying observation 1 has no sensitivity floor.** "Processing profile unchanged at the time point where PWP1
   depletion already shows a defect" is only falsifying if the assay is shown to detect a defect of the expected size;
   the plan should state the minimum detectable shift in the 32S/(32S+12S) and 7S/32S ratios from the replicate noise
   it already proposes to measure against CAMLG.
4. **RPE1-ss77** (ACH-002463) is listed as the natural non-cancer comparator; its WDR89 effect is −1.21 and its RBM34
   effect −0.59, which makes it arguably a better D2 than YAPC for the partner-comparison arms. Worth one line saying
   why it was not promoted.

### 3.6 Missing literature

My own EPMC sweeps (`RBM34 AND (rRNA OR nucleolus OR ribosome OR "pre-rRNA")`, 57 hits; `"RBM34"` 2024–2026, 39 hits)
turned up **no** human-cell experiment demonstrating a pre-rRNA processing or Pol I role for RBM34. The report's
carefully worded negative claim in §11 survives. The one open item is Scherl 2002 (§1.5).

---

## 4. Verdict

**ACCEPT WITH REVISIONS.**

The ledger is clean — 34 of 34 checked spans verified, including every yeast *Nop12* row, which was the specific worry.
Every machine number I could re-derive matches the project files. The report is genuinely honest about the three things
that matter most: that the predicted label is probably on the wrong GO branch, that the biology is closer to a
rediscovery than a discovery, and that two robustness checks fail. The required revisions are about **what is left
out**, not about what is asserted.

**Required (blocking):**

1. **Quote the rest of E16.** Add the p53/p21/G2-M arrest sentence from PMID:42848503 to §5's TP53 discussion, note
   that E16 is itself a DepMap-correlation study, and add **RPS27L (N(g) rank 15) and MDM4 (rank 18)** — reproducible
   from `zavg_BEF.npy` — to §8 as a named alternative: a p53-surveillance co-dependency block rather than a purely
   nucleolar one.
2. **Un-filter the Predictomes list in §6** (insert SRP72 0.675, SRSF5 0.653, PKHA4 0.601, MYCN 0.598 in rank order),
   and give Burke's per-pair RBM34–PWP1 pDockQ 0.138 beside it.
3. **Give the GLS failure a paragraph in §8**, stating the partner GLS ranks (434 / 2920 / 3155) and the holdout result
   that GLS is not detectably worse than zavg_BEF on H.

**Recommended (non-blocking):**

4. Lead §0's Claim bullet with the method's actual output (GO:0006354 / Pol I) before the orthologue-derived reading.
5. State the clean-first rank (29) beside the primary rank (5); fix "1,974 rows" → 1,973; add the omitted
   `fractionPlddtConfident` 0.179; state the 22 matrix paralogues and add paralogue loci to the C.3 off-target
   acceptance rule; note the GOA IDA nucleolus row.
6. Retrieve Scherl et al. 2002 (PMID:12429849) and state whether RBM34/KIAA0117 is among the 31 nucleolar proteins for
   which that paper proposed a ribosome-biogenesis role; cite the primary paper for E7 rather than the UniProt line.
7. Add a minimum-detectable-effect floor to falsifying observation 1 and to C.4 Tier 1.

**Lint result (claims without a verified source):** none found. Every gene-function sentence I checked in §§0–8 and
§11 carries an E-key, and every E-key I checked resolves and supports its claim as worded.

**PI response:** pending.
