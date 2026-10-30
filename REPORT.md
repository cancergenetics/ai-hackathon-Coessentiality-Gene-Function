# REPORT.md — approach, results, follow-ups, limitations, remaining ideas

Project: use the label-free co-essentiality tool zavg_BEF (github.com/cancergenetics/ai-hackathon-Coessentiality @
3c684c9) on DepMap 26Q3 CRISPR screens to propose functions for pre-registered uncharacterised human genes.
Run autonomously by an AI PI agent (Claude Opus 5.5) delegating to Opus/Sonnet 5.5 sub-agents, 2026-10-29 → 2026-10-30.
Paper: `manuscript/manuscript.pdf` (source `manuscript/src/`); candidate reports: `reports/`; record:
`RESEARCH_TREE.md`, `DEVIATIONS.md`, `LOOKS.md`, `LESSONS.md`. Nothing here has been verified by a human or at the bench.

## 1. Approach (what was done, in order)

| Milestone | What | Key artefacts |
|---|---|---|
| M0 Set-up | Prompt saved; tool pinned read-only; the exact DepMap 26Q3 files the tool was built on found on the user's machine (checksums match the tool's DATA.md) | `PROMPT.md`, `DATA.md`, `scripts/00_get_tool.sh` |
| M1 Literature & data | `LITERATURE.md` (Crossref-verified references); annotation data (GO current + 5 archives, gene2pubmed, UniProt, Unknome, TCRD) and orthogonal data (hu.MAP 3.0, BioPlex, OpenCell, HPA, Human Cell Map, STRING, BioGRID, Perturb-seq, ProteomeHD, AF2, chemogenomics, Complex Portal, MitoCarta); per-gene knownness table | `LITERATURE.md`, `config/data_checksums.tsv`, `results/preregistration/` |
| M2 Design | DESIGN v1 → v2.3 through 2 review rounds (11 role-specific reviewers) and 2 item-by-item disposition checks | `DESIGN.md`, `reviews/round*` |
| M3 Pre-registration | U = D1 ∩ (D2 ∪ D3) = 4,924 genes frozen before any gene–gene computation (tag `preregistration-v1`, hash gate); independently re-derived; hold-out H (820 genes, t0 = GO 2018-07) sized; power simulated | `preregistration/`, `results/holdout/`, `verify/` |
| M4 Verification & census | Tool reproduces its published HT-AP to within 0.0003; 14/14 sanity checks; split-half assessability; orthogonal-source admission; curation-lag audit; LLM recall probe | `results/verification/`, `results/assessability/`, `results/orthogonal/`, `results/audit/` |
| M5 Calibration | Ranker chosen on a LOO set, spec logged, then one look at H; calibration model fitted; independent re-derivation of the primary (809/809 per-gene agreement) | `results/calibration/`, `results/holdout_eval/`, `LOOKS.md` |
| M6 Predictions | Every scorable U gene scored; calibrated probabilities; artefact flags; orthogonal support; top 40 | `results/ledger/` |
| M7 Literature validation | Blind literature agents (100 genes) → redacted packets → judge validation on known genes → two blinded judges + adjudicator with 3 decoys per gene; 10 deep-dive reports, each red-teamed and revised | `results/m7/`, `reports/`, `reports/redteam/` |
| M8 Paper | Manuscript assembled with numbers sourced by tag; review round 1 (2 referees + numbers, references, reproducibility audits) → post-review analyses → revision → round 2 | `manuscript/`, `reviews/ms_round*`, `results/revision/` |

## 2. Main results (pre-specified unless marked)

- **Census (C1).** 4,924 genes pre-registered; 4,271 scorable; 646 pass the frozen assessability rule (13.1%), but
  clean-negative (non-expressed) genes pass the split-half test at 13%, so the null-adjusted estimate of genes with a
  real, reproducible co-essentiality signal is ≈ 243 (173–306), ≈ 4.9% of U [post-review].
- **Accuracy (C2).** On the temporal hold-out (809 genes uncharacterised in 2018, annotated since), precision@1 of the
  predicted GO term = 0.030 (0.018–0.043) vs 0.000 prior-only and 0.005 matched-gene null — primary test passes,
  robust to every split-half network and circularity sensitivity, independently re-derived. No advantage over GLS
  (+0.006, CI spans 0). A trivial homology baseline (the gene's own 2018 electronic/phylogenetic terms) scores 0.218;
  hu.MAP PPI transfer 0.049. Co-essentiality hits are largely distinct from homology hits; a deployable
  homology-else-co-essentiality rule adds +0.006 [exploratory]. Signal is concentrated in the strongest-dependency
  quintile (0.117).
- **Calibration.** Out-of-fold slope 0.82 (0.51–1.13), c 0.86 on 24 events: not detectably miscalibrated, but thin.
  p_cal is conditional on a gene being annotated later; unconditional expected confirmations ≈ 5 across the calibrated
  catalogue [post-review]. Max p_cal 0.141 → the pre-registered low-yield branch (no Tier A/B genes).
- **Catalogue (C3).** Predictions for 4,137 genes with flags; orthogonal support separated real from null predictions
  only weakly (0.32 vs 0.28 matched vs 0.22 decoy).
- **Literature (C4).** Blinded judges supported 18/40 top predictions vs 3/120 decoys (sign-flip p = 0.0002; term-only
  16/40, p = 7×10⁻⁴); secondary uncalibrated strong-signal list S20: 19/20; low-p_cal genes: 1/30. But most supported
  genes already had published function: 42% of a random U sample (and 59/90 judged candidates) are N1 — largely an
  artefact of the PubMed-count entry criterion (D3-only entrants 56% N1 vs 13%) [post-review]. 34/40 top genes appear
  in prior catalogues (Wainberg 2021, Kim 2019, hu.MAP 3.0, Predictomes) [post-review].
- **Candidates (reports/).** Ten red-teamed reports with decisive experiments. Post-review check: 9/10 genes already
  had a prior co-essentiality prediction or module (`results/revision/report_novelty_corrections.md`). Only PLEKHH3 is
  new — a putative PI(3,4)P2-arm brake on PI3K/AKT (co-advantage with PTEN/PLEKHA1, its #1/#2 genome-wide correlates).
  Wainberg 2021 had already predicted INAFM1 (DDI2/NFE2L1/NGLY1 module), CCDC71L (PRC2) and C5orf34 (centriole
  elongation); our reports add calibration, orthogonal evidence, literature checks, refinements (CCDC71L HP1/PxVxL arm;
  C5orf34 TP53-conditional dependency) and decisive experiments. TM2D1/TM2D2 (AUP1/JOSD1/STUB1 module) are a tentative
  ER/protein-QC co-dependency; RBM34, BICRAL, TRAPPC5 and ANKRD52 are largely rediscoveries serving as positive controls.

## 3. What this means

Pre-registered and calibrated, co-essentiality is a real but modest source of functional evidence for the dark genome:
it recovers module-level function for genes with strong dependency (often already published but uncurated), is
complementary to homology, and is honest about the large majority of "uncharacterised" genes for which cancer-cell
growth screens carry no information. The strongest contribution is the evaluation framework (pre-registration, temporal
hold-out with circularity filtering, calibration, blinded literature judging with decoys), not a list of discoveries.

## 4. Follow-ups

**Experimental (from the reports; one decisive experiment each):**
1. PLEKHH3 — acute dTAG depletion in PTEN-competent LN-428 / OVCAR-5 (isogenic PTEN-null vs restored), pAKT-S473/T308
   kinetics and PI(3,4)P2 biosensor at matched depletion depth.
2. INAFM1 — KO + guide-resistant rescue in NRF1-axis-dependent lines (OVCAR8, 22Rv1), NRF1 cleavage and proteasome
   bounce-back vs NGLY1/DDI2 KO, plus K48/K11 conjugate readout.
3. CCDC71L — endogenous tag IP-MS (WT vs PxVxL mutant vs charge-matched scramble) with CUT&RUN (H3K9me3 vs H2AK119ub1).
4. C5orf34 — endogenous tag + expansion microscopy, centriole counts after acute depletion, in isogenic RPE1 TP53+/+ vs −/−.
5. TM2D1/TM2D2 — acute CRISPRi with UPR time course and tunicamycin response vs AUP1/JOSD1/STUB1 arms (null → refuted).
6. RBM34, TRAPPC5, BICRAL, ANKRD52 — mechanistic refinements (pre-rRNA processing; TRAPPIII-vs-II epistasis; BICRAL/BICRA
   cross-complementation; degron-vs-cutting control for the circANKRD52 locus).

**Computational:**
- Re-run on newer DepMap releases and on independent screens (Sanger Project Score; RNAi as robustness) to test stability.
- Extend calibration targets beyond GO terms to module-level (complex/pathway) confirmations, which would raise both the
  number of calibration events and the usefulness of p_cal.
- Combine co-essentiality with homology and PPI in a jointly calibrated model (the exploratory complementarity result).
- Rebuild the uncharacterised definition with an experimental-CC criterion and full-text-aware literature counts.
- Repeat the blinded judging with heterogeneous judges (different model families, human curators) to bound κ inflation.

## 5. Limitations

Single DepMap release; GO incompleteness and curation lag bias both targets and the "uncharacterised" list; the
calibration rests on 24 events; tiers and orthogonal-support rules turned out uninformative at this effect size; machinery
families (mitochondrial, DNA repair, ribosome, nuclear RNA, centrosome) fell outside calibration support and were handled
by a post hoc secondary list; judges were two instances of one LLM and credited module-label matches (logged
retrospectively); literature agents can miss full-text-only evidence (e.g. CCDC71L); tool hyper-parameters were tuned on
hu.MAP 3.0, which post-dates t0; 22 logged deviations after the freeze (mostly unspecified operational details; some
retrospective); no wet-lab validation; no human verification of any result.

## 6. Remaining ideas (not pursued)

Module-level V1′ calibration; genome-wide Perturb-seq profile matching as a second hypothesis generator for essential U
genes; lineage-specific co-essentiality for tissue-restricted genes; AlphaFold-Multimer screens of top partner pairs for
type-(a) subunit claims; prospective registration of the ten experiments with predicted outcomes; a living catalogue
that re-scores predictions as GO releases accrue (true prospective validation).

## 7. Process notes

See `LESSONS.md` (12 rules) and the retrospectives `reviews/retro_M3.md`, `reviews/retro_M7.md`. What paid off most:
hash-gated pre-registration, logging the spec before a single look at held-out data, independent re-derivation of every
headline number, blinded judging with decoys and a validation set, and writer → red-team → revision for every report.
Biggest avoidable cost: operational details left unspecified at freeze (tie-breaks, fill rules), which generated most
post-freeze deviations.
