# Red-team review — ANKRD52

- Reviewer: adversarial red-team agent (role `red_team`), did not write the reports under review
- Model / date: Claude Opus 5.5 / 2026-10-30
- Material reviewed: `reports/ANKRD52.md`, `reports/ANKRD52_experiments.md`, `reports/data/ANKRD52/bundle.md`, `results/ledger/*`, `results/m7/L/HGNC_26614.md`, `results/m7/judge/*`, `results/m7/scratch_reports_trappc5/*`, `results/holdout_eval/SUMMARY.md`, `DESIGN.md`, `DEVIATIONS.md`; independent Europe PMC queries
- **Verdict: ACCEPT WITH REVISIONS**

---

## 1. Ledger spot-check (all 23 rows re-verified independently, not 10)

Protocol as for TRAPPC5: PMID re-resolved through Europe PMC (`EXT_ID:<pmid> AND SRC:MED`, core), abstract and PMC full text re-fetched by this reviewer, spans matched after Unicode normalisation.

| Row | PMID resolves | DOI as listed | Span verbatim | Supports the claim as worded |
|---|---|---|---|---|
| A1, A2, A3, A4, A5, A6, A7, A22, A23 | Y (28114302, Nature 2017, PMC5302127) | Y | Y (A1/A2 abstract; rest full text) | Y |
| A8, A9 | Y (18186651, Biochemistry 2008) | Y | Y (abstract) | Y |
| A10 | Y (34853298, Nat Commun 2021) | Y | Y (abstract) | Y |
| A11 | Y (35638597, eLife 2022) | Y | Y (abstract) | Y |
| A12, A13, A21 | Y (37402366, Mol Cell 2023) | Y | Y (A12/A13 full text; A21 abstract) | Y — **but under-reports the source's scope, §3(b)** |
| A14 | Y (33096142, BBA Mol Cell Res 2021) | Y | Y (abstract) | Y |
| A15 | Y (39014521, Cancer Sci 2024) | Y | Y (abstract) | Y |
| A16 | Y (38296907, Biochem Genet 2024) | Y | Y (abstract) | Y |
| A17 | Y (24035497, Mol Cell 2013) | Y | Y (abstract) | Y |
| A18 | Y (33789117, Cell Rep 2021) | Y | Y (abstract) | Y |
| A19 | Y (37712432, EMBO Rep 2023) | Y | Y (abstract) | Y |
| A20 | Y (21187329, JCB 2011) | Y | Y (abstract) | Y |
| T21, T22 | Y (33859415, Nat Genet 2021) | Y | Y | Y |
| L4, L5 | UniProt Q8NB46 REST copy (annotation score 3; no SUBCELLULAR LOCATION comment — re-checked) | — | Y | Y |
| P1–P4 | project files | — | Y (re-derived, §2) | Y |

**Failures: none.** No fabricated citation, no mis-attributed span, and every span supports its sentence.

## 2. Numbers re-derived from project files

- Profile: mean −0.243, SD 0.231, < −0.5 in 0.1242 (169/1361) — **exact**. Partner means AGO2 −0.090 (1.8 %), XPO5 −0.710, DICER1 −0.547, DGCR8 −0.520, DROSHA −0.484, TNRC6A −0.065, TNRC6B −0.072, TARBP2 −0.110, PPP6C −0.595, PPP6R1 +0.032, PPP6R2 −0.131, PPP6R3 −0.322, CSNK1A1 −0.792, ANKRD28 +0.020, ANKRD44 +0.028 — **all exact**.
- **Reciprocity: ANKRD52 is rank 1 in AGO2's own genome-wide row (zavg 25.76)**, ahead of XPO5 23.85, DICER1 23.07, DROSHA 21.98, TNRC6A 21.32, DGCR8 20.44, TNRC6B 17.38, TARBP2 13.80, CNOT9 10.72, PPP6C 10.65 — **exact**.
- Paralogue and kinase ranks in ANKRD52's row: ANKRD28 82 (2.87), ANKRD44 16,460 (−0.62), CSNK1A1 6,911 (0.01), AGO1 8,276, AGO3 5,212, PPP6C 8, PPP6R1 11, PPP6R3 14 — **exact**. PPP6C's own top partners (PTPA 21.79, PPP6R3 20.60, CYB5R4 20.03, TIPRL 18.42, LCMT1 16.61, PPME1 14.54, then ANKRD52 13.62) — **exact**.
- Figure 1 correlations (r = 0.37, ρ = 0.35 vs AGO2) — exact. Lines: SLR 20 −0.685 / AGO2 −0.502 / MRPS35 −0.671; LN382 −0.539 / −0.332 / −0.534; 253J-BV +0.145. Max |Δ| to MRPS35 = 0.014; MRPS35 genome-wide −0.500 — **exact**.
- p_cal 0.141024 (rank 1, not demoted), covariates 10.682 / 0.472 / 0.859 / 0.172; TP53 p 0.2415, q 0.4129, median diff +0.0219; TF 2 / OR 1.0667 / p 0.5719 / q 1.0; coupling ρ +0.0245; Cervix 18 lines, mean −0.3287, leave-out retained, overlap 0.92; 0/8 locus and CN flags; in-degree 37 — **all exact**.
- Orthogonal: P_group 0.2827 (Simes 0.5654), ProteomeHD 0.0140, CCLE 0.3287 (class 0.0280), HPA 0.0210, G and S not measured; Holm at α/3 = 0.0167 → no supporting class — **exact and correctly reasoned**.
- Judging (J071 d = 1.0, N1 16/31, κ 0.975) and hold-out numbers — **exact**.

**One factual error.** §5 states "ANKRD52 is the only gene in the primary top 10 with no failed check of any kind." `results/ledger/top40_primary.tsv` shows **MED31 (rank 8) is also undemoted with no flag** — and is strictly cleaner on two counts: its DEMETER2 check was *measured and replicated* (ANKRD52's is "not measured"), and it has four supporting orthogonal classes (ANKRD52 has none). Correct or delete the sentence.

**One wording slip.** "the highest p_cal of any of the 4,271 scorable uncharacterised genes" — only **2,583** of the 4,271 received a p_cal (`pcal_summary.json`). It is the maximum over the scored subset; say so.

## 3. Attack on the hypothesis

The report is unusually honest: it concedes N1, concedes the recall probe, concedes that the P class points at PP6 and not RISC, and concedes that the DepMap co-dependency itself was published [A12]. The attack therefore targets the three things it still claims to add.

**(a) The locus collision is under-weighted, and the missing literature makes it worse (most serious).** §8 treats ci-ankrd52 only as a Pol II regulator [A17] and dismisses the alternative because non-phosphorylatable AGO2 rescues silencing [A22]. But the locus's circular RNA is independently reported to **act in the miRNA pathway and promote proliferation**: *CircANKRD52 Promotes the Tumorigenesis of Hepatocellular Carcinoma by Sponging miR-497-5p* (PMID 33845641) and *CircANKRD52 Augments the Growth and Invasion of Melanoma Cells by Sponging miR-141-3p* (PMID 41173801); see also PMID 34453665 on ci-ankrd52 degradation, which agent L flagged but the report does not cite. A circRNA from this locus that is proliferation-promoting *and* miRNA-coupled is exactly the shape of artefact that would generate both the dependency and its covariance with miRNA machinery under CRISPR cutting. The [A22] rescue argument is still good (hyperphosphorylation of AGO2 requires loss of the phosphatase protein), but it is an argument about the *reporter* phenotype in HCT116, not about the *fitness* phenotype in the dependent lines — which is the claim at issue. Cite these papers, and promote Alternative B in the experiment plan from a sub-bullet to a Tier-1 arm.

**(b) Prior art is under-reported, which weakens contributions (ii) and (iii).** The report cites [A12] only for the AGO2–ANKRD52/PPP6C sentence. Shui et al. 2023's Methods state: "Gene effect scores from CRISPR mediated knockout of **AGO2, ANKRD52, DICER1, XPO5, TNRC6A, DROSHA, and PPP6C** in all cell lines were extracted and plotted" (Fig. 6A, Fig. S5C). That is the pan-miRNA-machinery DepMap comparison across all lines — i.e. most of what §7(iii) claims as "generality across contexts" and part of §7(ii). What genuinely remains new is narrower: the **PP6-vs-miRNA contrast** (ANKRD28 rank 82, ANKRD44 16,460, PPP6R1/2/3 non-dependencies, PPP6C's own phosphatase-shaped neighbourhood) and the blind, calibrated, artefact-screened derivation. Re-state §7(ii)/(iii) and §11 accordingly.

**(c) A mechanistic headroom problem that the report never raises.** If ANKRD52's fitness requirement acts by letting AGO2 accumulate in its inactive phosphorylated form, the effect cannot much exceed AGO2 loss of function — yet **AGO2 knockout is near-neutral** (mean −0.090; 1.8 % of lines < −0.5; −0.50 and −0.33 in D1/D2) while ANKRD52 is consistently stronger (−0.243; −0.685 and −0.539 in D1/D2). Two escapes exist in the report's own ledger — AGO1 is also hyperphosphorylated [A7], and phospho-AGO2 may be dominant-negative rather than null — but neither is invoked. This directly threatens the decisive experiment's success criterion (§4 Tier 2: "rescue ≥ 70 % of the non-targeting control"), which has little room above a near-neutral AGO2 baseline. Pre-declare the per-line ANKRD52-vs-AGO2 effect comparison, state which escape is being tested, and power the rescue accordingly.

**(d) Artefact classes: clean, but one cheap check is missing.** Locus, CN, hub, expression-coupling, TF, TP53 all re-derived and clean; lineage leave-out removes only Cervix. Because AGO2, TNRC6A and TNRC6B are themselves near-zero dependencies, a z ≈ 21–26 covariance between weak profiles deserves one more robustness pass: a full lineage jackknife, or a check that the ANKRD52–AGO2 correlation is not carried by a small subset of lines (e.g. recomputed after dropping the 5 % most extreme lines, or by screen-quality stratum). Cheap, and it would close the obvious reviewer question.

**(e) Relationship type and orthogonal evidence: correct.** Type **d** with zero supporting orthogonal classes is the right conservative outcome and is argued well (physical partners = PP6, functional partners = the regulated pathway). hu.MAP (PP6) and Predictomes (circular; ANKRD52–AGO2 only 0.329) are reported-not-counted correctly.

## 4. Attack on the experiments

- **Decisive experiment (AGO2-5XA knock-in epistasis)**: the right design in principle, and anchored on a published rescue allele [A22] — but see §3(c) on headroom, and note the effect sizes involved: ~1.5–2-fold dropout over 28 days with ≥ 6 replicates is a demanding assay. State the minimum detectable rescue.
- **Control line mismatch**: D1/D2 are TP53-mutant, the control 253J-BV is TP53-WT (and its CN is NaN). For a growth-rescue comparison this is a second variable; either justify or pick a TP53-mutant non-dependent control.
- **HCT116 caveat handled well**: the report explicitly separates the reporter context (where the mechanism is validated, ANKRD52 −0.08) from the fitness context, which is the honest reading.
- **Good practice to keep**: matched-essentiality control MRPS35 (|Δ| ≤ 0.014 in both lines), guides placed outside the ci-ankrd52 intron, degron as the primary modality, paralogue-specific off-target acceptance rule, Phos-tag p-AGO2 as the direct readout, small-RNA-seq as the specificity control, pre-registered decision rule including the realistic "ambiguous" outcome.
- **The Perturb-seq row is well chosen**: ANKRD52 is genuinely absent from all three datasets, so it fills a real "not measured" cell rather than duplicating existing data.

## 5. Required fixes (ordered)

1. **Take the locus collision seriously.** Cite PMID 33845641 and PMID 41173801 (circANKRD52 sponges miRNAs and promotes proliferation) plus PMID 34453665 in §8, state that the [A22] rescue addresses the reporter and not the fitness phenotype, and promote the degron-vs-cutting / ci-ankrd52-knockdown contrast to a Tier-1 experiment.
2. **Correct the two factual statements and re-scope the novelty claim.** Delete or fix "the only gene in the primary top 10 with no failed check" (MED31 also has none, with DEMETER2 measured and replicated and four supporting classes); say "highest of the 2,583 scored" not "of the 4,271 scorable"; and in §7(ii)/(iii) and §11 acknowledge that Shui 2023 already extracted and plotted DepMap effects for AGO2, ANKRD52, DICER1, XPO5, TNRC6A, DROSHA and PPP6C, leaving only the PP6-vs-miRNA contrast as new.
3. **Address the headroom problem and add one robustness pass.** State in both files that AGO2 knockout is near-neutral while ANKRD52 is not, name the escape being tested (AGO1 co-hyperphosphorylation [A7] or dominant-negative phospho-AGO2), power the 5XA rescue against that baseline, and add a lineage jackknife / outlier-line check for the ANKRD52–AGO2 covariance.
