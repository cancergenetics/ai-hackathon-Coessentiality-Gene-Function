# Round 2 disposition (DESIGN.md v2.2)

## Resolution (PI, v2.3)

Every O item (O1–O20) and every I item (I1–I12) below is now **adopted** in `DESIGN.md` v2.3, with three modifications:
- **O5 (adopted-modified):** no `lock_depmap.sh` and no chmod. Instead §1.6 states that before the tag the only permitted reader of DepMap gene-effect values is the allow-listed single-gene strata script (§1.4, per-gene marginals only), every pairwise script calls `gate.check()`, and `audit_order.py` checks that no pairwise output predates the tag.
- **O11 (placeholders set):** localisation sources are admitted if their agreement rate with GO CC on H genes has lower 95% CI > 0.6 on ≥ 200 H genes.
- **O17 (caveat only):** the hu.MAP 3.0 post-t0 caveat is added; BioPlex 2.0 is not added (PI S3 stands).

I3 is adopted: after the tag DESIGN.md is not edited; deviations go to `DEVIATIONS.md` (created, empty table). O19 is applied to `reports/TEMPLATE_candidate.md` and `reports/TEMPLATE_experiments.md`. The text of sections A–C below is the pre-resolution record and is left unchanged.

Every must-fix and should item in the five round-2 reviews, checked against the **text** of the current `DESIGN.md` v2.2 (not the revision-log claims). `§` = DESIGN v2.2. Reviews: `round2_external_PI.md` (PI), `round2_statistics.md` (ST), `round2_data_algorithms.md` (DA), `round2_ai_failure_modes.md` (AI), `round2_biology_prior_work.md` (BIO).
Dispositions: **Adopted** (§ cited), **Adopted-modified** (how), **Not adopted** (reason if DESIGN states one; otherwise "no reason stated"), **OPEN — not addressed**.
Revision-log claims were checked item by item: every phrase of the v2.2 log is present in the body. The gaps below are items the log does not claim, or claims only in part.

Repo state noted while checking (does not change dispositions): `config/` has `seeds.yaml`, `term_families.tsv`, `requirements.lock.txt`, manifests, but no `frozen.yaml`; `scripts/` has no `audit_order.py`, `verify_sparse.sh` or `INDEX.tsv`; `preregistration/` has no `PROVENANCE.md`, `FREEZE.sha256`; no `LOOKS.md`/`CLAIMS.tsv`. All are due at the freeze, so this is only a reminder. `reports/TEMPLATE_*.md` were not revised for round-2 BIO section 3 (checked).

---

## A. OPEN items: exact text changes (apply as DESIGN v2.3 before the freeze commit)

Priority: **[F]** changes a frozen rule or a number, fix before tagging; **[P]** process/definition detail, fix before tagging but low risk; **[L]** low, can go to `CRITERIA.md`/code.

**O1 [F] Neighbour-annotation leakage via IPI with/from (PI N6b; DA residual C).**
Current: §3.2.1 "the query's annotations removed from all counts"; §1.2 "IPI counts only for non-generic terms regardless of with/from" (this governs D1 for the gene itself, not neighbour membership).
Change: append to §3.0: "For neighbour membership (S, backgrounds, A_t, prior-only), annotation rows with evidence IPI whose with/from field contains the query gene are dropped when that query is scored; applied identically in LOO, H and U."

**O2 [F] Circularity flag not applied to LOO targets (DA §4 risk 1).**
Current: §3.2.1 LOO has no circularity statement; §3.2.3 speaks of "every PMID supporting a target" in the hold-out context only.
Change: append to §3.2.1: "LOO targets are checked with §3.2.3; flagged targets are excluded from the ranker-choice MRR (unscannable ones included, counts reported)."

**O3 [F] Calibration-covariate scale (ST C1 vs §3.7; see I2).** See I2 for the text.

**O4 [F] `FREEZE.sha256` contents (AI §1 Gate, §3.2).**
Current §1.6: "`FREEZE.sha256` (covers the list, criteria, DESIGN.md, config/term_families.tsv, config/frozen.yaml, config/seeds.yaml, src/knownness.py)".
Change to: "`FREEZE.sha256` (covers the list, criteria, DESIGN.md, config/term_families.tsv, config/frozen.yaml, config/seeds.yaml, src/knownness.py, src/gate.py, the tool commit hash 3c684c9 and the SHA-256 of the DepMap gene-effect, CN and mutation files); `gate.check()` verifies every entry and the tag."

**O5 [F] DepMap files readable before the tag (AI §1, §3.3).**
Current: only "Every DepMap pairwise script calls `src/gate.py::check()`" (§1.6).
Add to §1.6: "`scripts/lock_depmap.sh` removes read permission from the DepMap gene-effect, CN and mutation files until a script verifies the tag; the only pre-tag reader is the allow-listed single-gene strata script (§1.4), which emits per-gene marginals only."

**O6 [P] Agent scopes lack read-inputs and run log (AI §1 blind roles, §3.5).**
Current §9: "`config/agent_scopes.yaml` lists each agent task's allowed write paths".
Change to: "`config/agent_scopes.yaml` lists, for each role (audit, probe, L, judge, red-team), the working directory, allowed input files and allowed write paths; blind roles run in a directory containing only an ID/symbol file; each run appends role, model ID, input hashes and timestamp to `results/agent_runs.tsv`."

**O7 [F] Power simulation not named (AI §1; round-1 R1-3).**
Current §3.5 states effective n and the "< 300 underpowered" label only.
Add to §3.5: "A power simulation (`results/holdout/power_sim.md`; PI writes, a fresh agent verifies) giving the minimum detectable difference for both primary comparisons is committed at freeze and its MDE seeded in CLAIMS.tsv."

**O8 [P] Freeze artefacts (AI §3 items 1, 3, 4, 6, 7, 8; §2.2, §2.3).** Add one sentence to §1.6:
"Freeze artefacts: PROVENANCE.md records the criteria-commit hash, builder-script commit, input SHA-256s, every look at |U| and any criteria edit, and is verified by a fresh agent; `scripts/verify_sparse.sh` writes `preregistration/sparse_check.txt` at freeze and at M6 start; `tests/test_d1_equivalence.py` requires `knownness.d1()` to reproduce the D1/D2/D3/U columns of the committed feature table (the script-02 copy is retired); `audit_order.py` output is saved as `reviews/audit_order_M4.md`, `_M6.md`, `_M9.md` and M6 must pass before `results/ledger/` exists; CLAIMS.tsv is seeded with |U|, |H|, MDE; `scripts/INDEX.tsv` is created; RESEARCH_TREE.md is updated and the freeze-commit diff is listed in PROVENANCE.md."

**O9 [F] Negative-control purity and lineage-restricted genes (BIO C2).**
Current §1.4: "expressed (log2(TPM+1) ≥ 1 in ≥ 10% of DepMap lines with expression)"; §4.2 "Non-expressed U genes are scored anyway as a negative control".
Change: §1.4 add "clean negative = log2(TPM+1) < 0.5 in ≥ 95% of lines; lineage-restricted expressed = expressed in ≥ 50% of lines of any lineage with ≥ 10 lines (counts as expressed; assessable; type (e) if flagged); descriptive strata: HPA tissue/testis-enriched, TM/secreted". §4.2: "the false-call rate is computed on clean negatives".

**O10 [F] Missing §4.3 threshold and tier consequence (BIO C3; see I5).**
Current §4.3: "TF/lineage-marker enrichment of partners" has no list, test or cut-off.
Change: "TF/lineage-marker enrichment: partners vs the TF list in `config/` (named, frozen), one-sided Fisher OR > 3 and q < 0.05 → flag." Consequence text: see I5.

**O11 [F] Localisation class gaps (BIO C4).**
Current §5.1b vocabulary: "nucleus, nucleolus, cytosol, mitochondrion, ER, Golgi, plasma membrane, vesicles/endosome/lysosome, centrosome/cilium, cytoskeleton"; §5.3 "protein not multi-localised"; §5.2 admission covers co-complex odds ratios only.
Change: add "peroxisome, lipid droplet, nuclear envelope" to the vocabulary; define "multi-localised = ≥ 2 compartments in any admitted source"; commit the source-to-vocabulary map at M4; §5.2 add "localisation sources are admitted if their compartment calls agree with GO CC on H genes (agreement rate lower 95% CI > 0.6, ≥ 200 genes)". (The 0.6 and 200 are placeholders for the PI to set.)

**O12 [P] Relationship-type precedence and judge brief (BIO C1).**
Current §4.4 lists evidence per type but no order and no "unresolved" outcome; §6.4 does not tell judges that p_cal covers the module only.
Change: §4.4 add "Assignment is script-applied in this order: e (§4.3 coupling or TF enrichment); a (only with P/A/S support); c (transporter/enzyme domain, or ≥ 4 TM helices and no complex-like partners); b (not a stable subunit and in an assembly term or MitoCarta assembly pathway); else d, recorded as 'type unresolved'." §6.4 add "Judges are told the statement's type is not covered by p_cal".

**O13 [P] Size window for V1′ (ST B1).**
Current §3.0 states 5–200 for V2 and "same rules" for V1; V1′ (Complex Portal, MitoCarta) has no window. DA D also notes the open 3–300 Complex Portal window.
Change: "candidate terms: 5–200 annotated scorable genes at the release in use, for V2, V1 and V1′".

**O14 [F] Non-background (imputed) genes (DA §4 risk 3, D "BG-status matching").**
Current: DESIGN never says how non-BG genes are treated; matching covariates (§3.1) omit BG status; no `low_coverage` stratum in §1.4.
Add: §1.4 "low_coverage (non-background, imputed) as a stratum"; §3.1 "BG status is an exact-match covariate for M(g)"; §6.1 "low_coverage genes are excluded from Tier A unless H contains such genes".

**O15 [P] §5.1b source definitions still loose (DA §2 items 1, 4, 7, 8, 9, 10b, 10e).** Add to §5.1b:
"BioPlex measured = appears as a node. STRING: `physical.links.detailed`, experimental ≥ 400; because it imports BioGRID/IntAct/BioPlex it is counted with them as one P source group. CCLE proteomics: key Uniprot_Acc, lines mapped to ModelID via Model.csv CCLEName, replicate columns collapsed before the ≥ 50-line rule. Perturb-seq: g's own transcript and the partner's transcript are excluded from profiles; a perturbation counts only with ≥ 25 cells. Chemogenomics: Olivieri `Zscores_28screens` only (the ORCS copy has no screen metadata and is not used); loader test required (xlsx loads in neither openpyxl nor pandas). Burke: null pairs are drawn from pairs covered by Burke (HuRI ∪ hu.MAP). Continuous-source nulls are matched on hubness (mean row-score decile) and, for Perturb-seq, on phenotype strength."

**O16 [P] Report-selection and mito-cap residuals (BIO C5, C6).**
Current §6.1 "Mitochondrial-family calls ≤ ⅓ of the top 20 and ≤ ⅓ of reports"; §6.5 "8–10 genes … plus up to 2 N1 genes".
Change: "≤ ⅓ of the top 20 (≤ 6) and ≤ 3 reports, counting N1 exemplars; other N1 genes appear in a rediscovery table with rate and CI". (Rounding of ⅓ × 8–10 is otherwise undefined.)

**O17 [L] PPI comparator caveat and BioPlex 2.0 (BIO C8; conflicts with PI S3).**
Current §3.3: hu.MAP 3.0 comparator; BioPlex comparator was cut.
Change: add to the PPI comparator sentence: "hu.MAP 3.0 post-dates t0 and so favours the comparator (conservative for our claim)". Do not add BioPlex 2.0 (PI S3 cut it).

**O18 [L] Deferred infrastructure items (DA residual D).**
Current §2.1 has no `sec_ac`/`gene_history`; no retention-threshold tests; package lock exists (`config/requirements.lock.txt`) but is not cited.
Change §2.1: "retired UniProt accessions (`sec_ac`) and HGNC `gene_history` resolved in the hub; retention thresholds of each mapping are asserted in tests; environment pinned by `config/requirements.lock.txt`."

**O19 [P] Template-level items (BIO §3).** Not in DESIGN and not in `reports/TEMPLATE_*.md`.
Change §6.5: "Template A opens with a Section 0 bench summary (claim in plain words; confidence = expected hit probability; strongest reason to doubt; first experiment with time and cost; cancer-line essentiality is not organismal function); ledger and red-team go to an appendix. Template B requires acute or hypomorphic depletion time-matched to partner depletion with a matched-essentiality control gene from an unrelated module; for common-essential genes the controls are rescue, non-targeting guides and a control essential gene; the DepMap screen medium is the baseline (galactose is a sensitised condition); type-specific rows (b BN-PAGE and pulse-chase; c uptake/metabolite and bypass rescue; e ChIP/reporter); an 'other' readout row sourced from a ledger-verified paper; a sequence-level off-target check of guides; decision rule 'Supported = dropout rescued AND module-specific readout concordant AND localisation compatible AND Tier-2 physical or epistatic support'."

**O20 [L] Ties-by-S toy test (DA §4 risk 2).** Add to §2.5: "ties-by-S rule of R3 (p_emp floor 1/501) is tested on the planted-module toy".

---

## B. Internal inconsistencies and ambiguities in DESIGN v2.2

**I1 [F] GLS rows vs U top-40 GLS rank.** §4.1 requires "GLS rank (top 40 only)" for U genes; §2.2 and §8 give GLS/Pearson "rows only for H, the LOO sample … and named controls", so the U top-40 have no GLS rows.
Change §2.2 and §8 to: "rows only for H, the LOO sample, named controls and the U top-40 genes".

**I2 [F] §3.7 percentile ranks vs support logic.** §3.7 says all four covariates enter "as within-release percentile ranks (raw scale = sensitivity)", but the support rule and boundary branch refer to H's 5th–95th percentile "on top-K mean zavg and/or R(g)". If U's top-K mean zavg and R(g) are ranked within U they cannot fall below H's 5th percentile, which defeats N4. ST C1 asked for ranks only for the two release-dependent covariates.
Change §3.7 to: "neighbourhood annotation coverage and log top-term size enter as within-release percentile ranks (ranked against all scorable genes in that release); top-K mean zavg and R(g), which do not depend on the release, enter on their raw scale; raw coverage and size are the sensitivity".

**I3 [F] Hash freeze vs revision log.** The header says later changes "are logged in the revision log", but §1.6 hashes DESIGN.md (including that log) and the gate checks it, so any post-freeze log entry breaks the gate.
Change header to: "After the tag this file is not edited; later changes are logged in `DEVIATIONS.md` with reason and date, and affected results are reported under both the frozen and the changed rule."

**I4 [P] PRE-SPECIFIED markers incomplete.** §2 (tolerance ±0.005, toy acceptance), §7, §8 (core vs secondary), §9 carry decision rules but are not marked, while the header says only marked sections are frozen.
Change header: "Sections 2, 7, 8 and 9 are also frozen; the markers show where claims are decided."

**I5 [F] "No §4.3 exclusion" undefined for top-40-only checks.** §6.1 Tier A needs "no §4.3 exclusion", but §4.3 defines an exclusion only for "Any flag on ≥ half of the supporting partners". Lineage leave-out, dependency–expression coupling, TP53 and DEMETER2 are top-40 only and have no stated consequence.
Change §4.3: "Failing lineage leave-out, or a DEMETER2 or TP53 flag, removes Tier A (the gene is Tier B at best); coupling flags change the relationship type (§4.4)." Without that, genes outside the top 40 cannot be tested.

**I6 [P] U-reweighting is core or secondary?** §3.6 describes it in the covariate-shift section (with weights "refitted per bootstrap replicate"), §3.3 and §8 put "U-reweighting" in the secondary batch; "U-eligible" is undefined.
Change §3.6: "U-eligible = scorable U genes in support for p_cal (§3.7)"; label the reweighted estimate "(secondary batch, §8)"; SMDs and quintile metrics remain core.

**I7 [P] R(g) for H and LOO.** §3.7 and §3.6 use R(g) for H and LOO genes, but §4.2 defines it only for U and null genes.
Change §4.2: "R(g) is computed identically for H, LOO and U genes; R0 and the assessability call apply to U genes and to candidates."

**I8 [P] "Caliper 0.2 SD" under Mahalanobis distance.** §3.1 orders matches by Mahalanobis distance but states the caliper in SD.
Change: "caliper 0.2 in Mahalanobis units on standardised covariates; SMD balance of M(g) reported with the violation rate".

**I9 [P] Member set for the support test.** §5.3 uses members of the V2 term "and, for module label, V1′", but Tier A support and Simes/Holm per gene are defined once.
Change §5.3: "Tier A support uses the V2 member set; V1′ is reported descriptively".

**I10 [L] "Most specific term among the top 5" (§3.1) vs the V2 top reportable term (§3.0).** State: "(descriptive only; not used for p_cal, tiers or judging)".

**I11 [L] Clusters (§3.5).** "(PMID-only version at freeze for power)" does not say which version drives the primary CI.
Change: "primary CIs use PMID + N(g) clusters; the PMID-only version is used only for the freeze-time power simulation".

**I12 [L] Half-list restriction order (§4.2; DA residual A).** "restricted to BG_A ∩ BG_B ∩ BG_full with the §3.1 exclusions" does not say that the top-25 is taken after restriction.
Change: "N_A^s, N_B^s = the top 25 after restriction to BG_A ∩ BG_B ∩ BG_full (top-60 per half retained before filtering)".

---

## C. Disposition tables

### C1. round2_external_PI.md

| Item | Disposition | DESIGN evidence / note |
|---|---|---|
| N1 tiers on V2, not V1′ | Adopted | §3.0 last sentence ("p_cal, tiers and judged statements attach to the V2 top reportable term; V1/V1′ are descriptive"); §6.1; §3.7 Σ p_cal. |
| N2 define V2; neighbour codes; term families | Adopted | §3.0 (V2 definition; "same codes for targets, neighbour membership, backgrounds and prior-only"; `config/term_families.tsv`, fixed order, first match, else "other"); frozen in §1.6. |
| N3 §1.5 "no network access" | Adopted | §1.5 now "with no access to co-essentiality outputs" (PubMed etc. listed as sources). |
| N4 support rule / upper-bound branch | Adopted | §3.7 Support (5th–95th, boundary p_cal as upper bound, not tiered, summed separately, counts per category). Residual scale problem: I2. |
| N5 split-half common universe | Adopted | §4.2 (BG_A ∩ BG_B ∩ BG_full, both R and R0). Clarification I12. |
| N6a drop `colocalizes_with` | Adopted | §3.0 ("`colocalizes_with` dropped"). |
| N6b LOO: drop neighbour IPI with/from = query | **OPEN — not addressed** | O1. §1.2 covers D1 of the gene itself only; §3.2.1 removes only the query's own annotations. |
| N7 one matching function; caliper only for 5-match null; flag violations; report balance | Adopted-modified | §3.1 Matched list: nearest by Mahalanobis, caliper 0.2 with nearest-available fallback, violation rate reported, first 5/200/500 nested. Functionally equivalent, but not stated as caliper-only for the 5; balance (SMD) not reported: I8. |
| N8 circularity "unscannable" | Adopted | §3.2.3 (flagged/clean/unscannable; primary excludes flagged; sensitivity excludes unscannable; counts reported). |
| N9 judge validation on known current target | Adopted | §6.4 (10 H genes, "real" statement = known current target term). |
| S1 one full matrix | Adopted-modified | §2.2, §8 (one zavg_BEF matrix; GLS/Pearson rows; z_B/E/F via pair scorer). Flaw: U top-40 GLS rank has no rows (I1). |
| S2 orthogonal on candidates only; admission at M4 | Adopted | §5 header (p_cal ≥ 0.3, top 40, matched/decoy sets); §2.6, §5.2. |
| S3 core/secondary tiers; cuts | Adopted | §8 Analysis tiers; §3.3 secondary batch; BioPlex comparator, AUPRC and ≤ 5-PMID cut absent from body. Ambiguity: I6. |
| S4 merge random samples | Adopted | §1.5, §6.2. |
| S5 precompute S per release | Adopted | §3.1 ("precomputed as a gene × term matrix per release"), §8. |

### C2. round2_statistics.md

| Item | Disposition | DESIGN evidence / note |
|---|---|---|
| A1 endpoint (denominator, reportable term, candidates, comparators, ≤ 50) | Adopted | §3.2.2 Endpoint; §3.1 reportable (≥ 2 partners); §3.0 candidates 5–200; §3.3 ≤ 50 restriction with dropped-gene count. |
| A2 ranker ties, RR = 0, LOO removal | Adopted | §3.1 Ranker choice; §3.2.1. |
| A3 matched-gene rewrite | Adopted-modified | §3.1: one list of 500, Mahalanobis, exclusions (g, N(g), same arm, paralogues), caliper fallback with violation rate, seed 0, nested 5/200/500, R3 per-term exclusion M(g)\A_t, §3.3 null skips matches annotated to T(g). Caliper units: I8. |
| A4 clusters; percentile vs BCa | Adopted | §3.5 (fixed once, PMID-only at freeze, effective n, underpowered label); §3.3 percentile primary, BCa also. Clarification I11. |
| A5 covariate-shift weights | Adopted-modified | §3.6 (six covariates, 1st/99th trimming, refit per replicate, applied to all methods and both differences). "U-eligible" undefined: I6. |
| A6(i) slope/intercept criterion | Adopted | §0 decision branch. |
| A6(ii) sign constraints | Adopted | §3.7 (≥ 0, ≥ 0, ≥ 0, ≤ 0; family unconstrained). |
| A6(iii) out-of-fold over seeds 0–4; U model on all H | Adopted | §3.7. |
| A6(iv) support; bins | Adopted | §3.7 (5th–95th; family ≥ 30; deciles merged ≥ 30). |
| A6(v) Σ p_cal CI | Adopted | §3.7 (2,000 cluster-bootstrap refits, percentile; all U with p_cal and Tier A). |
| A7 assessability common background; toy | Adopted-modified | §4.2 uses empirical p < 0.05 (DA B form) rather than "R > q95"; §2.5 toy ≤ 7% null, ≥ 80% planted. |
| A8 orthogonal support rule | Adopted | §5.3 (members, statistics, 1,000 degree-matched nulls, Simes within class, Holm at α = 0.05); §5.2 (95th-percentile dichotomisation, bootstrap over complexes). Member-set ambiguity: I9. |
| A9 judging details | Adopted | §6.4 (adjudicated scores, decoy rules incl. Jaccard < 0.1, enumeration, by N-class, validation-failure rule). |
| B1 size windows | Adopted-modified | §3.0 5–200 for V2 and V1; V1′ unspecified: O13. |
| B2 V2 vs V1′ | Adopted | §3.0. |
| B3 Tier B wording | Adopted | §6.1. |
| B4 C2-fail branch | Adopted | §0 decision branches. |
| B5 LOOKS.md records calibration spec | Adopted | §3.1 Ranker choice; §9. |
| C1 release shift: percentile ranks | Adopted-modified | §3.7 adopts ranks, but for all four covariates rather than the two release-dependent ones; conflicts with the support logic: I2. |
| C2 horizon | Adopted | §3.7 ("~8 years (conservative)"). |
| C3 seeds | Adopted | §7 (matched lists 0, bootstraps 0, global 0–4); `seeds.yaml` is frozen in §1.6. |

### C3. round2_data_algorithms.md

| Item | Disposition | DESIGN evidence / note |
|---|---|---|
| Res. A split-half universe; all-NaN columns | Adopted | §4.2 (all-NaN columns dropped and recorded; common background). Order of top-25 vs restriction: I12. |
| Res. B assessability p-form | Adopted | §4.2 (1 + #{R0 ≥ R})/201 < 0.05. |
| Res. C leakage: IPI with/from; `colocalizes_with` | Adopted-modified | `colocalizes_with` dropped (§3.0); IPI with/from in neighbour tables **OPEN**: O1. |
| Res. D sec_ac/gene_history | **OPEN — not addressed** | O18 (deferred). |
| Res. D retention thresholds as tests | **OPEN — not addressed** | O18 (§2.1 has only QC tables). |
| Res. D package lock | **OPEN — not addressed** in DESIGN (lock file exists in `config/`) | O18. |
| Res. D Complex Portal window | **OPEN — not addressed** | O13. |
| Res. D BG-status matching | **OPEN — not addressed** | O14. |
| §2.1 BioPlex measured = node | **OPEN — not addressed** | O15 (§5.1b states edge only). |
| §2.2 OpenCell | Adopted | §5.1b "OpenCell reported interaction". |
| §2.3 BioGRID | Adopted | §5.1b "BioGRID physical non-HTP" (§5.1 BioGRID low-throughput physical). |
| §2.4 STRING file, one source group | Adopted-modified | §5.1b "STRING experiments ≥ 400"; file name and overlap with BioGRID/BioPlex not handled: O15. |
| §2.5 Human Cell Map | Adopted-modified | §5.1/5.1b "SAINT BFDR ≤ 0.01", 193-bait scope and measured = saint ∪ not-significant not stated: O15. |
| §2.6 ProteomeHD isoforms | Adopted | §5.1 "isoform groups collapsed to genes"; row percentile §5.1b. |
| §2.7 CCLE proteomics mapping | **OPEN — not addressed** | O15 (DESIGN gives ≥ 50 pairwise lines only). |
| §2.8 Perturb-seq knockdown rule | Adopted-modified | §5.1 "on-target knockdown ≥ 30% as reported" (reviewer example was fold_expr ≤ 0.3 and ≥ 25 cells; no minimum cells; own-transcript exclusion not stated): O15. |
| §2.9 chemogenomics Olivieri only | Adopted-modified | §5.1 "Olivieri 2020 screens only; ORCS copy or bioRxiv table, whichever parses". Review says the ORCS copy has no screen metadata and cannot be used; loader test absent; drug screens dropped (done): O15. |
| §2.10a partners/statistic | Adopted-modified | §5.3 uses members of the called term (ST A8) instead of N(g) ∩ t; statistic = edge count. |
| §2.10b hubness-matched nulls | Adopted-modified | §5.3 "degree-matched within the source"; hubness deciles for continuous sources and phenotype strength for Perturb-seq not stated: O15. |
| §2.10c Bonferroni min vs Simes | Not adopted (no reason stated) | §5.3 uses Simes within class (ST A8), then Holm. |
| §2.10d binary call for continuous in admission | Adopted | §5.2 (95th row percentile). |
| §2.10e Burke covered pairs | **OPEN — not addressed** | O15. |
| §2.10f localisation vocabulary map frozen; "match" | Adopted-modified | §5.1b vocabulary and §5.3 "sharing a compartment"; map not committed at M4: O11. |
| §3 R3 compute | Adopted | §3.1, §8 (gene × term matrix, lookup). |
| §3 per-term null exclusion | Adopted | §3.1 R3 (M(g)\A_t). |
| §3 caliper vs M | Adopted-modified | §3.1 (fallback and violation rate; SMD balance not reported; no "fewer than M admissible → no R3 call" rule): I8. |
| §3 §4.2 compute | Adopted | §8 (10 split-half runs ≤ 1 h); six matrices removed (§2.2). |
| §4 LOO circularity flag | **OPEN — not addressed** | O2. |
| §4 ties-by-S test | **OPEN — not addressed** | O20. |
| §4 `low_coverage` stratum | **OPEN — not addressed** | O14. |

### C4. round2_ai_failure_modes.md

| Item | Disposition | DESIGN evidence / note |
|---|---|---|
| §1 Gate: FREEZE contents; guard module; audit schedule/output | Adopted-modified | §1.6 lists list, criteria, DESIGN, term_families, frozen.yaml, seeds.yaml, knownness.py; audit_order at M4, M6, M9. Missing gate.py, tool commit, DepMap hashes, audit output files: O4, O8. |
| §1 Sparse checkout proof | Adopted-modified | §1.6 names `scripts/verify_sparse.sh`; no proof file or M6 re-run stated: O8. |
| §1 DepMap ungated | **OPEN — not addressed** | O5. |
| §1 Blind roles are instructions only | Adopted-modified | §9 `agent_scopes.yaml` (write paths only); inputs, directories, run log missing: O6. |
| §1 Power simulation | **OPEN — not addressed** | O7. |
| §1 CLAIMS/INDEX/frozen.yaml at freeze | Adopted-modified | §1.6 (LOOKS.md, CLAIMS.tsv at freeze; frozen.yaml in hash). `scripts/INDEX.tsv`, seed rows: O8. |
| §2.1 WIP committed early | Adopted | §1.6 "committed with explicit paths"; §9 "agents commit nothing". |
| §2.2 duplicate D1 code | Adopted-modified | §1.2 one function in `src/knownness.py`; equivalence test and retirement of script-02 copy: O8. |
| §2.3 stale RESEARCH_TREE; fresh-agent retrospective | **OPEN — not addressed** | O8 (§10 only lists the file). |
| §2.4 tool clone untouched | Adopted | §0 (read-only). |
| §2.5 list built before freeze, conditions | Adopted-modified | §1.6 PROVENANCE.md "how and when the list was built"; §1.4 strata after hash. Contents (commit hashes, input SHA-256, looks at |U|) not stated: O8. |
| §3.1 PROVENANCE.md | Adopted-modified | As above: O8. |
| §3.2 FREEZE.sha256 | Adopted-modified | O4. |
| §3.3 lock_depmap.sh; sparse_check.txt | **OPEN — not addressed** | O5, O8. |
| §3.4 test_d1_equivalence | **OPEN — not addressed** | O8. |
| §3.5 agent_scopes + agent_runs.tsv | Adopted-modified | O6. |
| §3.6 LOOKS, CLAIMS, DEVIATIONS, INDEX, frozen.yaml, power_sim | Adopted-modified | LOOKS, CLAIMS, frozen.yaml in §1.6; DEVIATIONS replaced by revision log (conflicts with the hash: I3); INDEX, power_sim: O7, O8. |
| §3.7 audit_order outputs M4/M6/M9 | Adopted-modified | §1.6 schedule only; output files and "M6 passes before ledger" not stated: O8. |
| §3.8 RESEARCH_TREE update; explicit paths; §1.6 pointer sentence | Adopted-modified | Explicit paths adopted (§1.6); rest and the pointer sentence: O8. |

### C5. round2_biology_prior_work.md

| Item | Disposition | DESIGN evidence / note |
|---|---|---|
| C1 type assignment rules | Adopted-modified | §4.4 gives rules for a–e and states p_cal covers the module only; precedence, TM criterion, "type unresolved", judge brief missing: O12. |
| C2 clean negatives | **OPEN — not addressed** | O9 (§4.2 uses "non-expressed", reports by informativeness tertile — that part adopted). |
| C2 lineage-restricted expressed | **OPEN — not addressed** | O9. |
| C2 HPA/TM strata | **OPEN — not addressed** | O9. |
| C3 numeric §4.3 thresholds | Adopted-modified | §4.3 numeric for bidirectional, CN, hub, coupling, TP53, DEMETER2. Missing TF/lineage enrichment threshold and consequence of top-40-only flags: O10, I5. |
| C4 family mapping; "other" | Adopted | §3.0 term_families (includes "other"); §5.4 other → any class. |
| C4 MitoCarta in class L | Adopted | §5.1 (L includes MitoCarta3.0). |
| C4 vocabulary additions; multi-localised | **OPEN — not addressed** | O11. |
| C4 localisation admission | **OPEN — not addressed** | O11 (§5.2 applies a co-complex test that does not fit localisation sources). |
| C5 mito cap | Adopted-modified | §6.1 ≤ ⅓ of top 20 and of reports (stricter than review's ≤ ½ / ≤ 3); rounding: O16. |
| C6 report selection | Adopted-modified | §6.5 (highest-ranked N2/N3 plus up to 2 N1); rediscovery table with rate/CI absent; N1 and cap interplay: O16. |
| C7 citation flag | Adopted | §3.2.3 (Wainberg 2021, Pan 2018, Kim 2019, Boyle 2018, Rahman 2021, Dempster/Meyers); review's "Pan 2018 or 2022" — only 2018 listed; unscannable fraction and sensitivity: adopted. |
| C8 PPI line | Adopted-modified | §3.3 "coverage and 'co-essentiality alone' complementarity on U"; BioPlex 2.0 not adopted (cut per PI S3; no reason in body); post-t0 caveat: O17. |
| Tmpl A: Section 0 bench summary | **OPEN — not addressed** | O19; template also lacks it. |
| Tmpl A: p_cal covers module only | Adopted | §4.4 (DESIGN); template not checked beyond the §1 definitions (contains "Without type-(a) support…" text). |
| Tmpl A: ledger/red-team to appendix | **OPEN — not addressed** | O19. |
| Tmpl B: essential-gene confound | Adopted-modified | §6.5 "essential-gene confound control"; no acute-depletion, time-matching or matched-essentiality control: O19. |
| Tmpl B: common-essential controls | Adopted-modified | Template names degron/CRISPRi; rescue/non-targeting/control-essential list not stated: O19. |
| Tmpl B: medium | **OPEN — not addressed** | O19 (§6.5 "DepMap cell-line rule" covers lines only). |
| Tmpl B: type-specific rows | **OPEN — not addressed** | O19. |
| Tmpl B: "other" readout row | **OPEN — not addressed** | O19. |
| Tmpl B: sequence-level off-target check | **OPEN — not addressed** | O19 (template says guides concordance in experiment only). |
| Tmpl B: decision rule | **OPEN — not addressed** | O19 (template §7 still reads "≥ 2 of the 3 Tier-1", although Refuted was rewritten). |
