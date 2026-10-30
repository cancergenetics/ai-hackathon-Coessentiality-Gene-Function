# Red-team review — reports/CCDC71L.md

Reviewer role: `red_team` (adversarial, did not write the report). Date: 2026-10-30.
Scope: `reports/CCDC71L.md` (Parts I and II, Appendix A). The report was not edited.

**Method.** Every PMID/DOI in Appendix A and in the Part II ledger was re-resolved through the Europe PMC REST API by the reviewer, independently of `results/m7/scratch_reports_ccdc71l/verify.py` (fresh `fullTextXML` / `resultType=core` fetches; markup stripped, whitespace collapsed, spans matched as substrings). Numbers were recomputed from `data/raw/depmap/CRISPRGeneEffect.csv`, `data/raw/humap3/*`, `data/raw/predictomes2025/*`, `data/raw/string/*`, `data/raw/bioplex/*`, `data/raw/humancellmap/saint-latest.txt`, `data/derived/neighbours/full_top100.npz`, `data/derived/paralogues_by_matrix_index.npz`, `results/ledger/*` and `data/raw/go/current/go-basic.obo`. The UniProt canonical sequence was re-downloaded from `rest.uniprot.org` and diffed against the copy in the authors' scratch directory.

---

## 1. Ledger spot-check (20 entries checked; 19 Appendix-A rows + the Part II rows)

**Result: no span failures.** All 19 Appendix-A keys (A-C1…A-C17, A-C20) and all six literature rows of the Part II ledger resolve to a real record, and every quoted span is present verbatim in the cited article after the normalisation the report declares. Rows A-C10, A-C13, A-P-style subscript cases (A-C13) match only after whitespace/markup collapsing, which is exactly the stated method.

**PMID 34780483 (A-C1, A-C2) — specifically requested, and it passes.** PMID 34780483 = DOI 10.1371/journal.pgen.1009909 = PMC8629390 exists and is the ATRX/CCDC71 BioID paper. Both spans are verbatim. More importantly, the report's *characterisation* of this source survives reading it in context, which is the harder test:

- A-C1 in context: "The mouse protein contains two canonical PxVxL sequences… A canonical PxVxL sequence is also found in the human CCDC71L protein, a shorter family member that shares a high degree of identity within the N-terminal half of CCDC71 and its C-terminal extremity". The report's claim — that the motif's existence is already in print and is *not* novel (§11) — is correct, and the supplementary figure "S3 Fig … A: PxVxL motif in human CCDC71L" confirms it is a sequence observation only.
- A-C2 in context: "Our analysis clearly demonstrates a strong association between CCDC71 and HP1 isoforms, likely mediated by non-canonical PxVxL motifs in human cells (and canonical ones in mice) **and/or through further associations with the related CCDC71L protein**". The report's reading — "hypothesised in print, never tested" (§7) — is accurate and not overstated. No experiment in that paper touches CCDC71L.

**One defect (provenance, not substance).** A-C13's span *"we used machine learning on curated datasets to train a structure prediction and omics-informed classifier (SPOC)"* is annotated "(full text, PMC11931459)". It is verbatim in the **Europe PMC abstract**, not in the PMC full text: the full text renders the expansion with spaced capitals and no hyphen — "train a S tructure P rediction and O mics informed C lassifier (SPOC)". The authors' own `verify.py` concatenates title + abstract + full text into one string, so the check passed while the provenance label is wrong. The second SPOC span used in §6 ("effectively separates true and false AF-M predictions of PPIs") *is* in the full text. Fix the source label on A-C13.

**Procedural finding that the report raises but under-weights.** PMID 34780483 is a full-text Europe PMC hit for the query `"CCDC71L"` (125 hits on my own sweep), yet it is absent from agent L's blinded item list (`results/m7/L/HGNC_26685.md`, 7 items, search terms include `CCDC71L`). The report discloses this honestly in §7 ("Important procedural note"). But the consequence is stated too mildly: the N2 class and the judges' verdict of "0 (unaddressed), d = 0.000" both rest on a search that demonstrably missed the single most relevant paper. The blinded step for this gene should be reported as **uninformative because the evidence set was incomplete**, not as "neutral".

**Independent literature sweep (reviewer).** Europe PMC `"CCDC71L"` = 125 records; `"CCDC71L" AND (HP1 OR chromatin OR heterochromatin OR Polycomb OR CBX)` = 38, all GWAS-locus, eQTL or bulk-omics mentions; `SRC:PPR` = 1 (the TNBC ceRNA preprint already cited). The report's claim that no chromatin/HP1 function for CCDC71L is published is **upheld**.

---

## 2. Recheck of numbers

All of the following were reproduced exactly (reviewer recomputation, independent script).

| Claim in report | Reviewer value | Verdict |
|---|---|---|
| PxVxL at 223–227 (PMVRL), unique in the sequence | one match, residues 223–227, `PMVRL`; no other `P.V.L` in 235 aa | ✔ |
| UniProt sequence used = canonical Q8N9Z2 | re-downloaded `Q8N9Z2.fasta` is byte-identical to the authors' copy; 235 aa, UniProt annotation score 2.0, no domain/signal/TM features, Regions 1–30 and 109–167 "Disordered" | ✔ |
| 21.3% R+K, 8.5% D+E, 12.8% Pro, net +30; motif 8 residues from the C-terminus | 21.3 / 8.5 / 12.8, net +30; 235 − 227 = 8 | ✔ |
| Chronos mean −0.063, SD 0.154, 13/1,361 < −0.5, NaN 0 | −0.063 / 0.154 / 13 (0.0096) / 0 NaN over 1,361 lines | ✔ |
| CCDC71 paralogue r = −0.017; one matrix paralogue | r = −0.017; `paralogues_by_matrix_index.npz` gives exactly `['CCDC71']` | ✔ |
| Top-10 partners and zavg_BEF (SUZ12 13.80 … CDYL 7.15) | identical from `full_top100.npz` row 2259 | ✔ |
| Six supporting partners BMI1, SMCHD1, LRIF1, PHF19, MEN1, BAHD1; no locus/CN/hub flags | identical in `u_flag_partners.tsv`, CN r 0.007–0.050 | ✔ |
| Top-3 terms, S, n_sup, size, p_hyper | identical in `u_top5.tsv` (S 45.407 / 39.789 / 39.404) | ✔ |
| p_cal 0.0635 [0.026–0.113], rank 16, demotion `lineage_leaveout`, R 0.272, RBO 0.278 | identical in `top40_primary.tsv` and `reports/data/CCDC71L/bundle.md` | ✔ |
| KLHDC3 −0.559 (KMS-20) / −0.562 (HCC-33), genome-wide mean −0.037, SD 0.177 | −0.559 / −0.562 / −0.037 / 0.177 | ✔ |
| Line effects: KMS-20 and HCC-33 g = −0.54, SUZ12 −0.73 / −0.57; Mac-2A g = +0.15 | −0.543 / −0.543; −0.725 / −0.574; +0.147 | ✔ |
| **Predictomes: 38 scored pairs; SPOC CBX5 0.903, CBX1 0.734, CBX3 0.683 (KIRC 0.332 / 0.254 / 0.638)** | exactly these values, 38 pairs | ✔ |
| hu.MAP 3.0: 8 complexes; huMAP3_11539.1 = 33 subunits, confidence 6, contains CBX1/CBX3/CBX5/ATRX/SUV39H2/EHMT1/EHMT2/ADNP/POGZ/CHAF1A/B/MAD2L2; four smallest at confidence 1 pair g with H2AB2/H2AB3, ZNF275, ZNF335, NEUROG2/3, CSRP2 | 8 complexes; 11539.1 has 33 members and all twelve named proteins; the four confidence-1 complexes are as described | ✔ |
| BioPlex3 degree 6 (CBX3, CHCHD2, H2AB3, NEUROG3, NHLH2, TNFSF12) | 6 edges, found under the alias **FLJ36031** in `BioPlex_293T_Network_10K`; same six partners | ✔ |
| STRING-exp degree 6 (CBX3, LRIF1, ADNP, CHAMP1, NEUROG3, POGZ) | 6 edges at experimental score ≥ 400 (CBX3 589, NEUROG3 573, CHAMP1 527, POGZ 512, LRIF1 508, ADNP 495); next is RPS19BP1 at 389 | ✔ |
| HCM-SAINT degree 4 | 4 baits at BFDR 0.00: CBX3 (1.00), CENPA (1.00), HIST1H2BG (1.00), ZNF330 (0.98) | ✔ value, ✘ name |

**Numerical / labelling errors found (all minor):**

1. **Internal inconsistency on hu.MAP.** §6 and §11 say CCDC71L is in **8** hu.MAP 3.0 complexes (correct). §7 "Prior prediction lists containing this gene" says **5**. One of the two numbers must be deleted.
2. **"NOAZFP" is not a gene symbol.** The fourth HCM-SAINT bait is **ZNF330** (alias NOA36); the file labels it `ZNF330_target`. Correct the symbol in §6.
3. **A-C13 provenance** (above): abstract, not full text.
4. AlphaFold pLDDT (mean 60.0, 34% > 70) could not be re-verified — the AFDB file endpoint returned HTTP 403 to this reviewer. It is marked † and is not load-bearing; flagged as unchecked, not as wrong.

---

## 3. Attacks

### 3.1 The lineage leave-out failure is correctly diagnosed, but mis-described

The report's defence (§5, "Honest reading") is that the failure is a knife-edge in term ranking, not a change of neighbourhood. **I tested this and it holds.** Removing the 34 Bladder/Urinary Tract lines changes the raw partner correlations by ≤ 0.005 in every case (SUZ12 0.120 → 0.119; EED 0.128 → 0.130; SMCHD1 0.206 → 0.205; LRIF1 0.040 → 0.044; BMI1 0.107 → 0.109; MEN1 0.093 → 0.093; BAHD1 0.061 → 0.057). The neighbourhood genuinely does not move; only the term label does. Credit where due.

But the sentence used to soften it is wrong on the facts:

> "the *rank order between two nested, near-synonymous chromatin terms* (GO:0040029 … vs GO:0001221 …)"

From `data/raw/go/current/go-basic.obo`: **GO:0040029 is a `biological_process`** (`is_a` GO:0006338, GO:0010468); **GO:0001221 is a `molecular_function`** (`is_a` GO:0008134). They are in different ontologies and therefore cannot be nested in either direction, they have different member sets (143 vs 101) and different supporting-partner counts (6 vs 4). (The rank-2 term GO:0045814 *is* a true descendant of GO:0040029 — the report appears to have transferred that relationship onto the wrong pair.) The distinction matters for the claim being made: a *coregulator-binding* MF is a binding assertion that, under DESIGN §4.4, would point toward a physical/type-a claim the report explicitly says it is not entitled to make, whereas the called BP term licenses "acts in pathway M". Flipping between them is not a cosmetic relabelling.

Second, "the same failure seen twice" understates the rate. Of the three refits reported, **two of three** (Bladder removal; K = 10) select GO:0001221 and only K = 50 and the GLS K = 25 network retain GO:0040029. The term label is a minority outcome across the perturbations actually tried. §0's "Strongest reason to doubt" should say so.

### 3.2 The undisclosed weakness: the neighbourhood is invisible in raw co-dependency space

This is the most serious omission in the report. Pearson correlations of CCDC71L's Chronos profile against its own partners, over all 1,361 lines:

| partner | r | rank in g's genome-wide correlation row (18,433 genes) |
|---|---|---|
| SUZ12 (rank-1 partner, zavg 13.80) | **0.120** | **250** |
| EED | 0.128 | — |
| SMCHD1 (supporting) | 0.206 | 18 |
| BMI1 (supporting) | 0.107 | — |
| MEN1 (supporting) | 0.093 | — |
| BAHD1 (supporting) | 0.061 | — |
| LRIF1 (supporting) | **0.040** | — |
| PHF19 (supporting) | **0.022** | — |

g's actual top raw correlates are a junk list — MAGEL2 0.333, TENM2 0.310, KRTAP1-3 0.307, SRSF8 0.295, GPHB5 0.293 — i.e. the kind of low-expression, low-variance genes that dominate an uncorrected correlation row. The entire reported neighbourhood is manufactured by the `zavg_BEF` bias correction. That is what the method is for, and split-half R = 0.272 at p = 0.0050 says the corrected neighbourhood is reproducible, so this is not a refutation. But the report quotes raw r freely when it helps the case (CCDC71 −0.017 in §5 and §8; co-abundance r for SMCHD1/CDYL/EED/SUZ12 in §6) and never once for the partners themselves. A reader of §0 ("its dependency profile tracks Polycomb") will not guess that four of the six partners the experiment plan proposes to test have raw co-dependency of 0.02–0.11. **Disclose the raw magnitudes and state plainly that the signal exists only post-correction.** The contrast with the companion PLEKHH3 report, where PTEN and PLEKHA1 are g's #1 and #2 raw correlates genome-wide, is stark and should be acknowledged rather than left for a reviewer to find.

### 3.3 The independence claim in §0/§6/§11 is wrong, twice over

§11: "the convergence of **three independent data types** (co-dependency, physical interactors in three P sources, AF-based SPOC scores) on **HP1**". Each of the three legs fails:

1. **SPOC is not independent of the other two — by construction.** The Predictomes paper states its classifier uses "genome-wide features of each protein pair that were external to AlphaFold, including **co-dependency data from DEPMAP**, coexpression data, T5 protein language model embeddings, subcellular colocalization predictions from DeepLoc 2.0, hit profiles from the BioORCS CRISPR screen database, and **high throughput interaction experiments from the BioGRID database**" (PMC11931459, full text), and reports that "among biological features, it was the number of independent experiments supporting an interaction in the BioGRID database (21%)" that mattered most. A SPOC score therefore already contains DepMap co-dependency and BioGRID PPI evidence. Calling it a third independent data type is not defensible.
2. **The "three P sources" are not three independent experiments.** STRING's experimental channel aggregates IMEx/BioGRID records, which include the BioPlex and Human Cell Map datasets that are the other two "sources". CBX3 appearing "in all three physical-evidence sources we admit" (§0) is, on the evidence available here, one or two primary experiments counted three times. The §6 statistic (`P_group p 0.0150`; `HCM_SAINT p 0.0440`; Simes 0.0300) inherits the same problem — and the class fails Holm anyway, so nothing downstream breaks; only the rhetoric does.
3. **The co-dependency data do not point at HP1 at all.** r(CCDC71L, CBX5) = **−0.014**, r(CBX1) = **−0.105**, r(CBX3) = **−0.010**; no HP1-family protein is in N(g) at K = 25 (the list is SUZ12, EED, BMI1, CBX4, SMCHD1, RING1, PHC3, MTF2, CBX8, CDYL, AEBP2, PSIP1, CRAMP1, LRIF1, PCGF1, UBE2E1, DOT1L, UBR7, PHF19, FCRL6, MEN1, BAHD1, CHD8, PPIL1, EHMT1). The HP1 arm enters the report only via SMCHD1/LRIF1 and via the physical/structural sources. §6's own closing paragraph says this correctly ("The co-essentiality neighbourhood is Polycomb-dominated; every independent physical, structural and co-abundance hint … points at HP1 … instead"); §11 then contradicts it by describing the three as converging.

**A fairer — and stronger — statement is available.** I ranked all 364 Predictomes pairs that contain CBX5: CCDC71L is the **3rd highest SPOC score of 364**, behind only SUV39H2 (0.910) and CBX1 (0.906), and ahead of CBX3 (0.889) and histone H3 (0.782); the paralogue CCDC71 is 6th (0.820). Across the whole file only 0.785% of pairs exceed SPOC 0.9. That is a genuinely specific structural hit and it is the best thing in this report. It should replace the independence claim rather than be buried under it.

### 3.4 Selective reporting inside the Predictomes table

The report lists CCDC71L's three high HP1 SPOC scores and omits the only other Predictomes pair that involves a gene from N(g): **CCDC71L–LRIF1, SPOC 0.000** (KIRC 0.330). LRIF1 is a *supporting partner*, is a STRING-exp interactor of g, is named in §0 and §7 as part of the mechanistic refinement, and is slated for IP-MS and epistasis in Part II. The one structural prediction that exists for a g–supporting-partner pair is negative, and it is not reported. "Absence of an interaction is never a contradiction" (§6) is accepted; selective presentation of the same table is not. Report the LRIF1 value beside the CBX1/3/5 values.

### 3.5 AP-MS stickiness: well designed, but the prior is stronger than the report admits, and two controls are not executable as written

The §8 alternative-1 treatment (charge-matched bait, benzonase, 150/300/500 mM salt series, PxVxL point mutant) is the right design and is better than most reports of this kind. Three problems remain:

- **The stickiness hypothesis is already partly observed, not hypothetical.** In `humancellmap/saint-latest.txt`, CCDC71L is recovered as a *prey* of the baits CENPA (SaintScore 1.00), HIST1H2BG (1.00), HIST1H3A (0.50) and APEX1 (0.49) as well as CBX3. A 235-aa, 21.3%-basic, net +30 protein that appears in histone and centromere bait pulldowns is the textbook profile. The report should state that the alternative is the *prior*, not a devil's-advocate position.
- **The charge-matched control bait is unspecified** ("an unrelated Arg/Lys-rich 235-aa protein, e.g. a nucleolar-targeting-free basic control"). Without a named protein, matched for length, pI, disorder fraction, nuclear import and expression level, the specificity control cannot be executed or costed. Name it.
- **The PxVxL-mutant readout is confounded.** The decision criterion is "HP1 isoforms lost (≥ 4-fold down) while ≥ 80% of other high-confidence preys retained". But three of g's own documented interactors — ADNP, POGZ, CHAMP1 (STRING-exp) — are the ChAHP complex, which is itself HP1-associated; a mutation that breaks a chromo-shadow-domain dock may well take them with it, which would be scored as "stickiness" under the stated rule. Either pre-specify ADNP/POGZ/CHAMP1 as *permitted* co-losses, or add a second, independent specificity control (e.g. an HP1 CSD-groove mutant on the CBX5 side).

### 3.6 Type-e regulatory co-dependency

The report's position (coupling ρ = 0.000, TF OR 1.07, no lineage reaching threshold; §8 item 3) is adequately supported and I could not break it: lineage-demeaning the profiles leaves r(CCDC71L, SUZ12) at 0.108 (vs 0.120 raw) and r(SMCHD1) at 0.203 (vs 0.206), so a lineage covariate is not the driver. The residual "shared chromatin-state covariate" cannot be excluded from DepMap, as the report says. No change needed.

### 3.7 Cell lines and the likely outcome of the experiment

- KMS-20 and HCC-33 sit at −0.54 on a distribution centred at −0.063 (they are 2 of only 13 lines below −0.5). The Tier-1 expectation, "log2 fold-depletion ≈ 0.4–0.8 over 14–21 doublings", is at the edge of what a three-guide GFP/mCherry competition resolves reproducibly, and **no power calculation or replicate count is given**. Add one; otherwise a null in Tier 1 will be uninterpretable, which matters because the §7 "Refuted" branch is partly keyed to the dropout.
- **The single admitted localisation source points away from the call.** HPA (Approved) gives Actin filaments / Golgi apparatus / Cytosol; the L-class statistic is 0.313 vs a null of 0.425 — i.e. *below* null, p 0.9990. Falsification #1 and the Tier-1 localisation arm are therefore, on the only admitted evidence, more likely to fire than not. The report acknowledges HPA in §9 but §0's "First experiment" paragraph does not price it in. State the prior probability of refutation honestly in §0.
- HCC-33's CN of 1.37 sits close to the 1.5 threshold and the report handles it correctly with a CRISPRi arm. Using HT-1376 (Bladder) as a declared stress test is a good touch.
- The guide off-target requirement specifically naming *CCDC71* is correct and important given the N-terminal identity noted in [A-C1].

---

## 4. Verdict

**ACCEPT WITH REVISIONS.**

The report is unusually honest about its own failures, the arithmetic is reproducible to the last digit, the ledger is clean, and the experiment plan is decisive and falsifiable. Three things must change before it stands: an independence claim that the cited sources contradict, an undisclosed weakness in the underlying signal, and a mis-described robustness failure. None of these is fatal to the hypothesis; all of them change how a reader should price it.

### Required fixes (in order)

1. **Delete or rewrite the "three independent data types" claim (§0, §6, §11).** SPOC's own paper states it is trained on DepMap co-dependency and BioGRID interaction counts; STRING-exp aggregates BioPlex/HCM; and the co-dependency data point *away* from HP1 (r with CBX1/3/5 = −0.105 to −0.010, no HP1 protein in N(g)). Replace it with the claim the data do support: CCDC71L is the 3rd-highest SPOC partner of CBX5 among 364 scored CBX5 pairs (0.903, behind SUV39H2 and CBX1, ahead of CBX3 and H3), with the paralogue CCDC71 6th — and report the omitted negative, CCDC71L–LRIF1 SPOC 0.000, in the same sentence.
2. **Disclose the raw co-dependency magnitudes.** r(SUZ12) = 0.120 (rank 250 of 18,433 in g's own correlation row), LRIF1 0.040, PHF19 0.022, BAHD1 0.061, SMCHD1 0.206; g's top raw correlates are MAGEL2 / TENM2 / KRTAP1-3. State in §3 or §0 that the neighbourhood exists only after the zavg_BEF bias correction, and that split-half reproducibility — not correlation amplitude — is what carries it.
3. **Correct the description of the robustness failure and the small factual slips.** GO:0040029 (BP) and GO:0001221 (MF) are in different ontologies and are not nested; the flip occurs in 2 of the 3 refits tried, not "the same failure seen twice"; §7's "5 complexes" contradicts §6/§11's "8"; "NOAZFP" should be ZNF330; A-C13's span is in the abstract, not the full text. Additionally: name the charge-matched control bait, pre-specify ADNP/POGZ/CHAMP1 as permitted co-losses in the PxVxL-mutant IP-MS criterion, add a power statement for the Tier-1 competition assay, and state in §0 that the only admitted localisation source (HPA: Golgi/actin/cytosol) predicts Falsification #1 will fire.
