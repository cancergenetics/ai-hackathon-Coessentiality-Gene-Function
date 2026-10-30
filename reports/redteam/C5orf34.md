# Red-team review — reports/C5orf34.md

- Reviewer: adversarial reviewer agent (role `red_team`), model Claude Opus 5.5
- Date: 2026-10-30
- Scope: Appendix A + Appendix C.8 ledgers, every number against the cited project file, hypothesis attack, experiment plan.
- Independence: reviewer did not write the report. All checks re-run from primary sources (Europe PMC REST, Crossref,
  AlphaFold DB, GOA GAF, InterPro/HPA logs, `data/raw/*`, `results/ledger/*`, `results/m7/*`, and
  `data/derived/matrices/zavg_full/zavg_BEF.npy`). The report's own `verify_spans.log` was **not** taken as evidence;
  every span below was re-fetched.

---

## 1. Ledger spot-check (18 of the 24 Appendix A rows + all 7 Appendix C.8 rows)

| # | Row | Source | Result |
|---|---|---|---|
| 1 | F1 "knockdown of C5orf34 significantly suppressed A549 and SPCA1 cells proliferation and motility" | PMID:30771479 | **PASS** |
| 2 | F2 cell-cycle modulation in LUAD | PMID:38951221 | **PASS** |
| 3 | F3 "there is no pan-cancer investigation of C5orf34 at present" | PMID:38078888 | **PASS** |
| 4 | F4 gestational-diabetes CpG | PMID:27019060 | **PASS** |
| 5 | F5 "Uncharacterized C17orf53, … C5orf34, …" + "205 … 53 of which are functionally uncharacterized" | PMID:30452682 | **PASS** (both spans, full text) — but see §1.1, the row is materially incomplete |
| 6 | F6 "ARHGEF39 C5orf34 CENPF CHTF18" in the 268-gene p53-LIN37/DREAM table | PMID:31400114 | **PASS** (full text) |
| 7 | F7a "we characterized two recently identified A-C linker proteins, CCDC77 and WDR67, and discovered MIIP…" | PMID:40707486 | **PASS** (full text PMC12290023) |
| 8 | F7b the cross-DepMap sentence + the 12-gene list | PMID:40707486 | **PASS, verbatim and complete** — the quoted list is exactly the paper's. The *use* made of it is wrong; see §1.2. |
| 9 | F8 SPICE1 depletion impairs centriole duplication | PMID:20736305 | **PASS** |
| 10 | F9 CEP120/SPICE1 localise CEP135 to procentrioles | PMID:23810536 | **PASS** |
| 11 | F10 USP28–53BP1–p53–p21 axis | PMID:27432896 | **PASS** |
| 12 | F11 Wainberg "108 uncharacterized genes" | PMID:33859415 | **PASS** |
| 13 | F12 three Crossref titles | 3 DOIs | **PASS** (exact) |
| 14 | F14 pLDDT 72.06, v6 | `af_Q96MH7.json` | **PASS** |
| 15 | F15 percentile 0.948; SPICE1 MW p 8.30e-01, diff −0.000 | `tp53_global.txt`, `tp53_partners.txt` | **PASS** |
| 16 | F17 `huMAP3_02211.1,1,P35443 P49746 Q96MH7 Q99726,THBS4 THBS3 SLC30A3 C5orf34` | humap3 CSV | **PASS** (byte-exact; the other three complexes in §6 also verified) |
| 17 | F18 `LURA1_HUMAN__CE034_HUMAN__877aa,…,0.570,…` | predictomes CSV.gz | **PASS**, and the §6 list (LURAP1 0.570, CHMP4B 0.501, RCCD1 0.485, DOCK5 0.462) is the **complete, unfiltered** top 4 |
| 18 | F19–F22 Brunello / Cas-OFFinder / dTAG / AID2 | 4 PMIDs | **PASS** |
| 19 | F23, F24 U-ExM method + A–C linker depletion phenotype | PMID:40707486 | **PASS** (both) |
| 20 | C.8 line/PPME1/SPICE1 rows | `ctrl_lines.txt`, bundle §10 | **PASS** (C5orf34 −0.63/−0.66; SPICE1 −0.76/−0.63; PPME1 −0.68/−0.66; control SNU-638 −0.03) |

Not independently re-fetched: F13 (InterPro API, logged in `scratch_reports_rbm34/interpro/`) and F16 (HPA API,
logged in `hpa_c5orf34.json`) — both are API captures with the response text quoted, and I confirmed the log files
exist; I did not re-query the APIs. I did confirm independently that C5orf34 has **zero rows** in
`data/raw/go/current/goa_human.gaf.gz`, which corroborates the "genuinely dark protein" statement in §2.

**Failures: 0 of 25 on verbatim-span grounds.** The 2025 A–C linker paper [F7], flagged for scrutiny, is quoted
accurately and at length, including the part that works against the report (the DepMap provenance of the discovery).
The problems are a numeric error (§1.2), an unchecked datum in a cited paper (§1.1), and omissions.

### 1.1 F5 contains a directly relevant result that was not checked

PMID:30452682 did not only list C5orf34 among the 53 orphans. It screened **28** of them by GFP knock-in-free cDNA
transfection and reports: "nuclear localization was the most frequently observed (15/28) followed by
**centrosomal-like localization (11/28)** and cytosol (9/28)", with only C18orf54, C3orf14 and CCDC150 confirmed by
γ-tubulin co-localisation, and "Confocal images of **all 28 proteins screened** can be found in Supplementary Data S1."

The report's §7 says only that "27 such orphans were screened … C5orf34 was *not* among the proteins shown to be
centrosomal, so this paper neither supports nor refutes the localisation." That is true of the three γ-tubulin
confirmations, but it leaves the decisive question unasked: **was C5orf34 one of the 28, and if so, which of the three
bins did it fall into?** If it is one of the 11 showing centrosomal-like staining, this is the single strongest
orthogonal datum in existence for the prediction, and the report's "not one orthogonal class supports it today" (§11)
would be wrong. If it is in the nuclear or cytosolic bin, that is a published localisation result pointing away from
the centriole, in a paper the report already cites. Either way it is in Supplementary Data S1 of an open-access paper
and it changes the report. (The identities of the 28 are not in the main text; I could not resolve them here.)

The abstract also says 27 and the body says 28; the report copies 27 without noting the paper's own discrepancy.

### 1.2 "Eight of those twelve" is wrong — it is seven

§7 states: "Eight of those twelve are in C5orf34's K = 25 neighbourhood." Recomputed from the project's own matrix
(`data/derived/matrices/zavg_full/zavg_BEF.npy`), C5orf34's unfiltered top 25 is:

```
SPICE1 13.31, MIIP 12.80, CCDC77 12.59, TBC1D31 12.35, WRAP73 12.25, CEP41 10.49, CEP135 9.32, CEP44 9.08,
PCM1 8.83, CEP295 8.64, PPP1R35 7.33, CCSAP 6.24, GIGYF2 6.06, POC1A 5.94, CEP57 5.56, SEMA3C 4.64,
CCDC198 4.46, CEP63 4.26, CEP120 4.07, ZDHHC3 4.02, SIGLEC8 3.84, DKK2 3.78, PCDHGA12 3.71, DCLRE1A 3.60, CCP110 3.58
```

Of the paper's twelve (WDR8 = WRAP73, SPICE1, CEP135, TUBE1, TUBD1, TEDC2, RTTN, CEP44, CEP295, PPP1R35, CEP152,
MIIP), **seven** are present: WRAP73, SPICE1, CEP135, CEP44, CEP295, PPP1R35, MIIP. TUBE1, TUBD1, TEDC2, RTTN and
CEP152 appear nowhere in the top 30. CCDC77 and TBC1D31 are in the neighbourhood but they are the paper's *query*
genes, not members of the twelve — the most likely source of the off-by-one. Correct the sentence to seven.

A related transparency point: `results/ledger/*` publishes only the **top 10** partners and the 8 supporting partners,
so this load-bearing sentence is **not reproducible from the shipped ledger**. Either publish N(g) at K = 25 or cite
the matrix path.

### 1.3 The 2025 paper had C5orf34 in front of it and did not take it — in both directions

Also recomputed from the same matrix, C5orf34 is **rank 10 in CCDC77's own neighbourhood (z 12.59) and rank 10 in
TBC1D31/WDR67's (z 12.35)** — above PPP1R35, CCSAP, CEP120, TUBE1, TUBD1 and TEDC2, several of which [F7] *did* list
and validate. [F7] ran "a cross-DepMap analysis … among the top 100 genes" of exactly those two queries and named
twelve, explaining that "11 out of these 12 genes encode characterized centriolar proteins". C5orf34 appears nowhere in
the paper's text (I grepped the full text for `C5orf34`, `CE034` and `Q96MH7`: zero hits).

This cuts both ways and the report makes neither cut:

- **For the prediction:** the co-dependency is considerably stronger than §0/§3 concede. The report's framing —
  "C5orf34 hangs off that clique by co-essentiality alone", "raw Chronos r with SPICE1 = 0.06" — undersells a gene that
  sits at rank 10 of both A–C linker queries. That ranking is the real evidence, and it is independent of this
  pipeline's scoring choices.
- **Against the novelty framing:** experts running the same analysis on the same public data, one year before the
  freeze, had this gene in their top 100 for both queries and filtered it out — most plausibly by the "characterized
  centriolar proteins" criterion, i.e. precisely because it is dark. The report should say so. It is also the honest
  answer to "what would make this prediction uninteresting": the signal was already visible and was passed over, not
  missed.

### 1.4 One-sided reporting of the raw correlations

§0, §3 and §5 all repeat the SPICE1 raw Chronos r = 0.06 as the headline caveat. `raw_r.txt` also contains **CCDC77
0.21, CEP135 0.16, CEP41 0.14, CEP44 0.12, WRAP73 0.08, CEP295 0.08** — i.e. the single weakest pair was chosen as the
representative. The error is in the conservative direction, which is the right instinct, but it is still selective: the
report should quote the range (−0.01 to 0.21) or the mean, not the minimum.

### 1.5 Smaller inaccuracies

- §7 / §11: "not among the **1,974 rows**" — the file has 1,974 lines including a header, so **1,973 rows**. (Same
  off-by-one as the RBM34 report.)
- §2: the AlphaFold banding "31.3% very high, 35.4% confident, 23.0% very low" silently drops `fractionPlddtLow`
  = 0.102. The quoted figures are exact; the set is incomplete.
- §6 says "Under the frozen Tier-A rule this prediction … passes only because `config/term_families.tsv` maps
  GO:1902115 to 'other'." GO:1902115 is **not in** `term_families.tsv` at all; it falls to "other" by default. The
  conclusion is right, the mechanism as stated is not.
- The report gives rank 31 in the primary top 40 and never states that C5orf34 is **absent from
  `results/ledger/top40.tsv`** (the clean-first sensitivity list) altogether — the bundle records this explicitly
  ("gene not in top40.tsv"). For a gene whose §0 already says there is no orthogonal support, "under the alternative
  frozen reading this gene is not a candidate at all" is material and belongs in §11.

---

## 2. Numbers re-checked against files

Every machine number I could re-derive matches `reports/data/C5orf34/bundle.md`, `results/ledger/*`,
`results/m7/judge/*`, `DESIGN.md`, `DEVIATIONS.md` and the raw data:

- Profile: mean/SD −0.070/0.164; frac < −0.5 0.0132 (18/1361); median −0.056; 5th pct −0.362; min −0.800;
  expression 0.973/0.847, median 2.99; ρ 0.061 (n = 1292); R 0.424, R0 max 0.184, p 0.0050, RBO 0.627. **match**
- Partners: every zavg, z_B/z_E/z_F, GLS rank, mean effect, frac and band in §4 matches `u_partners.tsv` row for row.
  **match**
- Supporting 8 (SPICE1, WRAP73, CEP135, CEP295, PPP1R35, CCSAP, CEP120, CCP110) with CN r 0.04/−0.05/−0.03/0.04/
  0.03/−0.03/−0.05/−0.03. **match** (`u_flag_partners.tsv`)
- Terms: S 64.727 / 43.697 / 43.697 / 41.601 / 39.581; sizes 165/69/79/67/168; LOPO 8/8 and 1/6. **match**
- Orthogonal: P 1 edge vs 0.431, p 0.3457; G 0.453 vs 0.455, p 0.5485; A/L/S not measured; members 165; BioPlex
  degree 17, OpenCell 2, STRING-exp 7, huMAP3 8. **match**
- TP53: p 1.19e-05, diff +0.0355, 902/459, percentile 0.948; partner diffs SPICE1 −0.000 (p 0.83), WRAP73 −0.005,
  CEP135 +0.019, CEP44 +0.022, PCM1 −0.026, CEP295 +0.044. **match**
- DEMETER2: 7 partners, mean r 0.055 vs null 0.073; recomputed CEP295 0.196 (n 285), CEP135 0.136, TBC1D31 −0.146,
  CCSAP −0.128. **match** (`d2_pairs.txt`)
- Lineage leave-out N(g) overlap 0.80; K = 10/50 same term; GLS top term GO:0031346. **match**
- M6: `centrosome_cilia_mitosis (< 30 H genes) 119` → no p_cal family, so calibration in "other". DESIGN §5.4
  centrosome/cilia/mitosis → **L or P**. DEMETER2 fails 182/204. **match**
- Judging: packet J065, slots A–D all 0 from both judges, J1's justification verbatim; κ 0.975 / 360 statements;
  real 18, decoys 3/120, p 0.0002174. **match**
- Lines: SNU-1750 −0.63 / SPICE1 −0.76 / expr 3.07 / CN 1.01 / NNMD −11.16; HAP1 −0.66 / −0.63 / 4.44 / 1.13 /
  −4.95; SNU-638 −0.03; funnel 1361 → 18 → 8 → 6 → 5; PPME1 genome-wide −0.327. **match**
- Network edge counts (55 edges, 15 physical, none involving C5orf34). **match**

Numeric errors found: **one** of substance (§1.2, eight → seven) plus the 1,974/1,973 off-by-one.

---

## 3. Attack

### 3.1 Zero orthogonal support

The report states this plainly in §0, §6, §8 and §11 — "not one orthogonal class supports it today", "every independent
dataset that has looked at C5orf34 has put it somewhere other than the centriole, or has not looked at all" — and it
correctly identifies that the one diagnostic class for the term's true family (L or P) that was measured gives no
support. That is the correct call and it is made without hedging. The prediction rests entirely on one modality.

Two things would make it fairer rather than softer: (i) §1.1, the unchecked localisation bin in a paper already cited,
which is the cheapest available orthogonal datum; (ii) §1.3, the rank-10-in-both-queries fact, which is the strongest
*within*-modality evidence and is currently absent.

### 3.2 DepMap-derived circularity of [F7]

**Handled well.** §7 explicitly says that because the A–C linker discovery is itself DepMap-derived it counts as
*unaddressed* under DESIGN §6.4, "and the same caution applies to reading it as independent confirmation here". The
blinded judges scored it 0, consistent with that. I would strengthen rather than weaken this paragraph, with §1.3: the
circularity is sharper than stated, because the overlap is not generic (centriole genes co-depend) but specific
(C5orf34 is rank 10 of both of that paper's own query genes). The report currently treats [F7] as a neighbouring
success story; it is better described as the same analysis, run by others, with this gene filtered out for being dark.

### 3.3 The TP53 flag — centriole loss → p53 activation

This is the most interesting attack surface and the report gets halfway. It gives the two readings ([F6] p53–DREAM
repression of C5orf34 itself; [F10] USP28–53BP1–p53–p21 arrest after centriole loss), and then supplies the
observation that kills the second one: **the centriolar partners do not share the flag** (SPICE1 p 0.83, diff −0.000;
WRAP73 −0.005; CEP135 +0.019 — all verified). It calls this "the single most uncomfortable observation in the report"
and leaves it unresolved.

Leaving it unresolved is one step short. The logic is sharp and should be stated: *if* the dependency were a
centriole-duplication dependency, the USP28–53BP1 route predicts the partners carry the same TP53 asymmetry, and they
do not; what remains is reading (i), in which the TP53 association is a property of C5orf34's own p53–DREAM-controlled
**expression**, which is the signature of relationship type **e**, the report's own strongest competing hypothesis.
The flag is therefore mild positive evidence *for* type e, not a neutral curiosity.

Two cheap checks would settle a lot and belong in the report, not the lab:

- Recompute the TP53 Mann–Whitney **stratified by C5orf34 expression** (or partial out expression). ρ(effect,
  expression) is only 0.061, which argues against the DREAM reading; making that argument explicitly would largely
  rescue the report's position.
- Recompute N(g) and the top term **within TP53-mutant lines only** (n = 902). If the centriolar neighbourhood
  survives, the p53 axis is not generating it; if it collapses, the type-e reading wins. Both are one script.

### 3.4 Lineage effects and weak statistics

Reported honestly: 18 of 1,361 lines below −0.5, mean −0.070, and N(g) overlap after removing Eye is 0.80 — "the
weakest neighbourhood stability of the genes reported in this pass", in the report's own words. The split-half result
(R 0.424 vs null max 0.184) is the right counterweight and is correctly described as reproducibility, not effect size.
No objection. Add §1.5's clean-first-list absence here.

### 3.5 Missing literature

I found no publication placing C5orf34 at the centriole or assigning it a molecular function; the §7 negative claim
survives. C5orf34 has zero GOA rows, which I verified directly. The open items are §1.1 (Supplementary Data S1 of
PMID:30452682) and §1.3 (Fig. 1a of PMID:40707486 — the report should state whether C5orf34 is visible in that
published figure, since it is rank 10 in both of that figure's queries).

### 3.6 Experiments (Appendix C) and cell lines

The plan is well matched to the problem — localisation first, phenotype second, growth-matched PPME1 control, a
TP53-wild-type arm, a ciliogenesis arm for the second alternative, and a decision rule fixed in advance. The cell-line
selections are rule-derived and every number checks out. Four weaknesses:

1. **The decisive experiment can fail for reasons unrelated to the hypothesis, and falsifying observation 1 does not
   allow for that.** C5orf34's median expression across lines is log2(TPM+1) = 2.99 and 3.07 in D1 — a low-abundance
   protein, with no validated antibody, detected only through a knock-in tag, against a centriole that occupies a
   fraction of a percent of cell volume. "No centriolar signal → downgrade to type e" needs a stated detection floor:
   a positive-control knock-in of a comparably low-abundance centriolar protein in the same line and the same U-ExM
   pipeline, with the minimum detectable molecules-per-centriole reported. Without it, the cheapest outcome of the
   cheapest experiment is an uninterpretable negative.
2. **HAP1 is the weakest screen in the funnel.** NNMD −4.95 against SNU-1750's −11.16 (and the selection rule sorts by
   NNMD ascending = better screen). The report praises HAP1 for near-haploidy and clean knock-ins but does not mention
   that its −0.66 effect comes from the noisiest of the five qualifying screens, nor HAP1's well-known tendency to
   diploidise in culture — which matters for a centriole-number readout.
3. **The dropout arm is under-powered by construction.** C.4 asks for log2FC ≈ −0.7 with 3 guides × 3 replicates from a
   Chronos −0.63/−0.66 dependency, and the decision rule in C.7 requires "dropout rescued by guide-resistant cDNA" as a
   conjunct. If the dropout is not detectable, the whole rule returns "ambiguous" regardless of the localisation and
   centriole-count results. Either state the power calculation or demote the dropout conjunct.
4. **Tier-2 IP-MS is listed as "yes" but §6 already predicts its outcome**: three interaction resources place C5orf34
   with CSNK2B/FKBP5/DNAJC7/THBS3/RADX/TBCC and none with a centriolar protein. The report notes this in the "if wrong"
   cell; it should carry the same caution into C.7, where Tier-2 physical support is a required conjunct for
   "Supported".

---

## 4. Verdict

**ACCEPT WITH REVISIONS.**

This is the more honest of the two reports and the more fragile prediction, and it says so itself: a dark protein, no
orthologue, no localisation, no interaction evidence, one modality, two failed checks, and a §0 that leads with
"apart from the DepMap profile there is **no orthogonal support at all**". The ledger is clean — 25 of 25 checked spans
verified, including every row drawn from the 2025 A–C linker paper — and the DepMap-circularity of that paper is
disclosed unprompted. One substantive numeric error and three omissions block acceptance as written.

**Required (blocking):**

1. **Fix "eight of those twelve" → seven** (§7), and either publish N(g) at K = 25 or cite
   `data/derived/matrices/zavg_full/zavg_BEF.npy` so the claim is reproducible from the shipped files.
2. **Add the rank-10 fact and its two edges** (§1.3): C5orf34 is rank 10 in both CCDC77's and TBC1D31/WDR67's own
   neighbourhoods, above several genes [F7] validated; [F7] nonetheless does not mention it anywhere. Say this in §7
   (it strengthens the co-dependency evidence) and in §11 (it weakens the novelty framing — the signal was visible and
   was filtered out for being uncharacterised).
3. **Resolve or escalate the TP53 observation** (§3.3): state that the partners' failure to share the flag argues
   against the USP28–53BP1 reading and therefore *for* type e, and run the two one-script checks — TP53 difference
   stratified by C5orf34 expression, and N(g)/top term recomputed within the 902 TP53-mutant lines.

**Recommended (non-blocking):**

4. Retrieve Supplementary Data S1 of PMID:30452682 and state whether C5orf34 was among the 28 screened and in which
   localisation bin (§1.1); note the paper's own 27/28 discrepancy.
5. Quote the range of raw partner correlations (−0.01 to 0.21), not only the SPICE1 minimum (§1.4).
6. State that C5orf34 is absent from `results/ledger/top40.tsv` entirely; fix "1,974 rows" → 1,973; add the omitted
   `fractionPlddtLow` 0.102; correct the `term_families.tsv` mechanism (unmapped → default "other", not mapped).
7. Add a detection floor to falsifying observation 1 and a positive-control knock-in to the C.4 Tier-1 localisation
   arm; note HAP1's NNMD −4.95 and diploidisation risk; state the power calculation behind the dropout arm or demote it
   from the C.7 conjunction.

**Lint result (claims without a verified source):** none found. Every gene-function sentence I checked in §§0–8 and
§11 carries an F-key, and every F-key I checked resolves and supports its claim as worded; the one unsupported
statement is the arithmetic in §1.2, which cites a project file rather than a paper.

**PI response:** pending.
