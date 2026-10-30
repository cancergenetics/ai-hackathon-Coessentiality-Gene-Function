# Red-team review — TRAPPC5

- Reviewer: adversarial red-team agent (role `red_team`), did not write the reports under review
- Model / date: Claude Opus 5.5 / 2026-10-30
- Material reviewed: `reports/TRAPPC5.md`, `reports/TRAPPC5_experiments.md`, `reports/data/TRAPPC5/bundle.md`, `results/ledger/*`, `results/m7/L/HGNC_23067.md`, `results/m7/judge/*`, `results/m7/scratch_reports_trappc5/*`, `results/holdout_eval/SUMMARY.md`, `DESIGN.md`, `DEVIATIONS.md`; independent Europe PMC queries
- **Verdict: ACCEPT WITH REVISIONS**

---

## 1. Ledger spot-check (all 26 rows re-verified independently, not 10)

Protocol: each PMID re-resolved through the Europe PMC REST API (`EXT_ID:<pmid> AND SRC:MED`, resultType core) by this reviewer, with a freshly fetched abstract and (where a PMC record exists) full text; each verbatim span matched after Unicode/punctuation normalisation. Caches written to the reviewer scratchpad, not to the project.

| Row | PMID resolves | DOI as listed | Span found verbatim | Supports the claim as worded |
|---|---|---|---|---|
| T1, T2 | Y (21525244, Mol Biol Cell 2011) | Y | Y (abstract) | Y |
| T3, T4, T5 | Y (34018214, EMBO J 2021) | Y | Y (T3 abstract; T4, T5 full text) | Y |
| T6, T7 | Y (33277614, Commun Biol 2020) | Y | Y (full text) | Y |
| T8 | Y (18585354, Cell 2008) | Y | Y (abstract) | Y |
| T9 | Y (29273580, JCB 2018) | Y | Y (abstract) | Y |
| T10 | Y (41801064, JCB 2026) | Y | Y (abstract) | Y — yeast, and the report says so |
| T11 | Y (42483769, J Cell Sci 2026) | Y | Y (abstract) | Y, **with a caveat** (below) |
| T12, T26 | Y (42738849, Cells 2026) | Y | Y (full text) | Y |
| T13, T25 | Y (39273027, Cells 2024) | Y | Y (abstract / full text) | T13 Y; T25 supports orthology, not "deepest orthologue" |
| T14, T15, T15b | Y (39769094, IJMS 2024) | Y | Y (full text) | Y; T15b correctly marked review-level |
| T16 | Y (35425722, J Hepatocell Carcinoma 2022) | Y | Y (abstract) | Y |
| T17 | Y (38564972, Mol Genet Metab 2024) | Y | Y (abstract) | Y |
| T18 | Y (22406856, Nat Methods 2012) | Y | Y (abstract) | Y |
| T19 | Y (28536105, J Cell Sci 2017) | Y | Y (abstract) | Y |
| T20 | Y (31429971, EMBO J 2019) | Y | Y (abstract) | Y |
| T21, T22 | Y (33859415, Nat Genet 2021) | Y | Y (full text / abstract) | Y |
| T23 | Y (17110339, Cell 2006) | Y | Y (abstract) | Y |
| T24 | Y (32258032, Front Cell Dev Biol 2020) | Y | Y (abstract) | Y |
| L1, L2, L3 | UniProt Q8IUR0 REST copy | — | Y | Y |
| P1–P4 | project files | — | Y (re-derived, §2 below) | Y |

**Failures: none.** No fabricated PMID, no mis-attributed span, no span that fails to support its sentence. The three 2026 PMIDs (41801064, 42483769, 42738849) are real and correctly cited; I checked them specifically because high PMIDs are the usual place fabrication hides.

Two wording notes, not failures:
- **T11 is from *Aspergillus nidulans***, not metazoa. The report flags T10 as yeast and T3 as *Drosophila* but presents T11 ("subcomplex composition, not core composition, is what directs TRAPP") without its organism. Add "(in an ascomycete)". The same abstract also says TRAPPC11/12/13 **target TRAPPIII to autophagy**, which cuts against reading the human TRAPPIII-arm dependency as a secretory-route statement; it deserves a sentence.
- **T25** ("TRAPPC5 (Trs31p ortholog)") supports orthology but not the §2 claim "**deepest** orthologue". Either re-source or soften.

## 2. Numbers re-derived from project files

Re-computed independently from `data/raw/depmap/CRISPRGeneEffect.csv` restricted to the 1,361 manifest lines, from `data/derived/matrices/zavg_full/zavg_BEF.npy`, and from `results/ledger/*`:

- Profile: mean −0.724, SD 0.238, fraction < −0.5 = 0.8582 (1168/1361) — **exact**.
- Partner ranks in TRAPPC5's full row: TRAPPC3 1, TRAPPC1 2, TRAPPC11 3, TRAPPC4 4, TRAPPC2L 5, TRAPPC13 6, TRAPPC8 7, TRAPPC12 8, RAB1A 9, RAB1B 12, **TRAPPC10 134**, TRAPPC14 4810, TRAPPC6B 3599, TRAPPC3L 12531, TBC1D14 8143, **TRAPPC9 14766**, TRAPPC6A 16010 — **all exact** (`ranks.tsv`).
- Chronos means: TRAPPC8 −1.390 (97.1 %), TRAPPC11 −0.941 (93.7 %), TRAPPC13 −0.191, TRAPPC12 +0.014, TRAPPC9 −0.145 (1.5 %), TRAPPC10 −0.029 (1.5 %), TRAPPC6A −0.125, TRAPPC6B −0.087, TRAPPC3 −1.719, TRAPPC1 −1.303, TRAPPC4 −1.001, TRAPPC2L −0.249, GOSR2 −1.004 — **all exact**.
- Figure 1 correlations (r = 0.27, ρ = 0.18 vs TRAPPC3) — exact.
- Lines: MSKPCa16 −0.620 / TRAPPC3 −1.756 / NDUFAF8 −0.676; HKGZ-CC −0.983 / −1.931 / −0.941; 22Rv1 −0.013. Max |Δ| to NDUFAF8 = 0.056 (reported 0.055 — rounding, acceptable). Genome-wide NDUFAF8 −0.630 — exact.
- p_cal 0.114020, rank 4, demotion label TP53, in-support covariates (zavg 10.944, R 0.512, cov 0.786, size 0.800); TP53 n 902/459, p 0.001562, q 0.0062, median diff −0.0394; TF 0 / OR 0.240 / p 1.0; lineage Cervix 18 lines, mean −0.824, leave-out retained, overlap 0.88; hub share 0.00, 0/9 locus and CN flags — **all exact** against `u_pcal.tsv`, `top40_primary.tsv`, `u_flags.tsv`.
- Orthogonal class p-values (P 0.0010/Simes 0.0020; A 0.0010; L 0.0010; G 0.0010; S 0.7013 with 3 measured members, null 0.908) — exact against `support_sources.tsv` / `support.tsv`.
- Hold-out and judging numbers (p@1 0.030 [0.018–0.043], slope 0.819 [0.512–1.127], Brier 0.0294, c 0.855, Σp_cal 2.04 [1.05–3.24], J074 d = 1.0, 18/40 vs 3/120, p = 0.0002174, κ = 0.975) — exact against `results/holdout_eval/SUMMARY.md`, `M6_SUMMARY.md`, `results/m7/judge/*`.

**One internal numeric contradiction.** §4 ends "three of four TRAPPIII-specific subunits are in TRAPPC5's top 8". It is **four of four** (C11 3, C13 6, C8 7, C12 8), as §7 itself states. Fix §4.

## 3. Attack on the hypothesis

The module call is conceded as a rediscovery, correctly. The reviewable claim is therefore only: *TRAPPC5's proliferation requirement tracks the TRAPPIII-specific arm and not the TRAPPII arm.* It survives, but more weakly than the report implies.

**(a) The TRAPPII comparison is uninformative as currently argued (most serious).** `ranks.tsv` contains the diagnostic the report does not report: TRAPPC9's own top-15 partners are **PSCA, DENND3, FAM135B, TSNARE1, SLC45A4, JAK3, …** — i.e. TRAPPC9's profile has no recoverable structure at all, and even its obligate partner TRAPPC10 ranks only 34 (zavg 3.24) in it. A gene whose profile carries no signal cannot fail to co-vary informatively with anything. "TRAPPC5 does not track TRAPPII" and "TRAPPII profiles are noise" are not distinguished by any analysis in the report. Separately, TRAPPC10 at **rank 134 of ~18,000 (top 0.8 %)** is described as absence of co-variation; that is an overstatement of the asymmetry.

**(b) The report concedes its own strongest alternative without using the evidence that rebuts it.** §8's "strongest competing hypothesis" is that the asymmetry merely reflects the arms' differential essentiality. The report's own numbers argue against that: **TRAPPC12 (mean +0.014) and TRAPPC13 (−0.191) are non-dependencies yet rank 8 and 6**, with SDs (0.159, 0.251) comparable to TRAPPC9 (0.147) and TRAPPC10 (0.159). Essentiality magnitude therefore does not determine rank, and the concession is too generous. Make this argument explicitly — then the residual alternative is specifically *profile informativeness of C9/C10*, which (a) says is untested.

**(c) Co-essentiality demonstrably fails to recover complex membership here, which bounds the inference.** TRAPPC6A (rank 16,010) and TRAPPC6B (3,599) are bona fide core subunits with no co-essentiality to TRAPPC5; TRAPPC2/TRAPPC2B are not even in the background set. A method that misses 2–4 of 7 core subunits cannot treat the absence of C9/C10 as evidence of route specificity. This belongs in §8, not only as the "quantitative spread" observation in §7.

**(d) Orthogonal support is presented without the project's own false-positive baseline.** P/A/L/G all "support", but `M6_SUMMARY.md` records an empirical false-support rate of **0.279 for matched-gene predictions and 0.223 for decoys**. For a textbook complex, P/A/G support is near-guaranteed and the diagnostic L call is coarse (HPA "Vesicles", Approved only). Quote the baseline where PALG is cited.

**(e) Circularity is handled well.** hu.MAP (train gene) and Predictomes (DepMap as a feature) are reported-not-counted; the recall probe is flagged "known"; §11 claims no novelty for the module. Independent Europe PMC searches found no prior publication of a TRAPPIII-vs-TRAPPII co-dependency statement for TRAPPC5, and only four TRAPPC5-titled records exist, so the "no human TRAPPC5-specific functional study beyond [T16]" claim holds as of today.

**(f) Artefact classes.** Lineage, CN, locus, hub, expression-coupling, TF: all re-derived and clean. The TP53 flag is correctly described as a power artefact (−0.039 Chronos against SD 0.238, n = 1361) and is inert given zero Tier A/B genes.

## 4. Attack on the experiments

**(a) The "decisive experiment" does not test the claim.** The claim is about *which complex carries the proliferation requirement*; the decisive experiment is a RUSH transport assay. Worse, the §6 success criterion — "TRAPPC5 is recovered in both assemblies at comparable stoichiometry, **but only** the Rab1/TRAPPIII arm readouts collapse on depletion" — is close to incoherent for a shared core subunit: if TRAPPC5 is stoichiometric in both complexes, its acute loss should disable both. As written the "prediction right" branch is nearly unreachable, so the test is not a fair one. **The Tier-2 TRAPPC8-vs-TRAPPC9 epistasis plus arm-specific rescue is the only arm that addresses the claim and should be promoted to Tier 1 and named decisive.**

**(b) The falsifier in §9.3 has almost no dynamic range.** TRAPPC9 is a non-dependency (mean −0.145; < −0.5 in 1.5 % of lines; in D1/D2 it will be near zero), so "TRAPPC9 co-depletion is epistatic to TRAPPC5" is barely measurable in these lines. Either state the expected effect size and power, or move the TRAPPII arm to a context where TRAPPII function is assayable (Rab11-dependent cargo, not growth).

**(c) Cell lines are a practical risk.** Both dependent lines are low-passage organoid-type models (MSKPCa16 requires prostate organoid medium; HKGZ-CC is an IPN-of-bile-duct line), neither with established degron knock-in, and D1's effect (−0.62) is modest. The plan acknowledges this and lists substitutes, but the whole decisive programme rests on biallelic knock-in in these two models. Consider promoting the RPE1-hTERT *TP53*⁻/⁻ / HEK293T degron context from "third context" to a primary line for the mechanistic arms.

**(d) Good practice to keep.** Matched-essentiality control (NDUFAF8, |Δ| ≤ 0.056 in both lines), pre-declared off-target acceptance rule, guide-resistant rescue, pre-registered decision rule, and the honest note that §9 was written after the literature was read.

## 5. Required fixes (ordered)

1. **Re-frame the TRAPPII comparison.** Report TRAPPC9's own neighbourhood (top-15 partners are unrelated genes; TRAPPC10 only rank 34 in it) and state that the TRAPPII arm carries no detectable co-essentiality signal with anything, so the asymmetry is consistent with — and cannot presently be separated from — uninformative TRAPPII profiles. Stop describing TRAPPC10 (rank 134, top 0.8 %) as absence of co-variation.
2. **Make the decisive experiment match the claim.** Promote TRAPPC8-vs-TRAPPC9 epistasis + arm-specific rescue to Tier 1 and decisive; drop or re-write the incoherent §6 "prediction right" branch; state the expected effect size for the TRAPPC9 arm given its −0.145 mean.
3. **Fix §4 "three of four" → "four of four"**, add the C12/C13 rebuttal of the arm-dispensability alternative and the C6A/C6B/C2 counter-caveat to §8, mark T11 as *Aspergillus* (with its autophagy-targeting conclusion), re-source or soften "deepest orthologue" [T25], and cite the 0.279 / 0.223 false-support baseline wherever PALG support is claimed.
