# Round 1 disposition (DESIGN.md v2)

Disposition of every numbered item in the six round-1 reviews against `DESIGN.md` v2 (current file). Section numbers (§) refer to DESIGN v2. Milestones: M3 freeze, M4 verification, M5 calibration, M6 hypothesis generation, M7 deep-dives, M8 manuscript, M9 final.
Dispositions: **Adopted** (cites DESIGN section), **Adopted-modified** (says how), **Deferred** (to a milestone), **Not adopted** (reason), **Not possible** (data or tool not available). Priorities are the reviewer's own (M = must, S = should, C = could).

## OPEN items (must-fix, not addressed by DESIGN v2, not covered by a PI decision)

Each is marked **OPEN — PI decision needed** in its table below.

1. **OPEN — PI decision needed** (prior_work 3.2, M): no PPI-only guilt-by-association comparator (hu.MAP 3.0, BioPlex, STRING experiments) and no Wainberg-style module-transfer comparator on the temporal hold-out (§3.3 lists GLS, Pearson, prior-only, homology, matched null only); no explicit report of which U predictions rest on co-essentiality alone (no physical support).
2. **OPEN — PI decision needed** (prior_work 3.5, M): hold-out timing. (a) Targets are defined by release difference (§3.2.2), so old papers curated after t0 count as "new"; the review asks that a term count only if its supporting PMID postdates t0. (b) t0 = 2018-07-02 is later than Pan 2018 (16 May 2018), which already placed TEDC1/2 (named controls in §3.2.2); move t0 or drop TEDC1/TEDC2 from the controls.
3. **OPEN — PI decision needed** (prior_work 3.3, M): prospective audit of earlier prediction lists (Wainberg 108, hu.MAP 472, Replogle, Kim): what has since been shown experimentally (circularity blacklist applied). §6.6 covers only agreement and overlap with U.
4. **OPEN — PI decision needed** (data_algorithms 3.1, M): pair-level score definition per orthogonal source (BioPlex pInt, OpenCell edge, STRING experimental score, CCLE/ProteomeHD Pearson with ≥ 30 shared lines, Perturb-seq profile correlation, etc.) is not written into §5; it must be fixed before U predictions are viewed.
5. **OPEN — PI decision needed** (data_algorithms 4.3 residual, M): split-half stratification within missingness pattern × lineage and the assertion BG(half) = BG(full). §4.2 stratifies by OncotreeLineage and keeps PatientID together, but instead of preserving BG it records all-NaN genes as not reproducible.
6. **OPEN — PI decision needed** (data_algorithms 6.2, M): annotation-leakage rules not in §3: drop IPI rows whose `with/from` contains the query gene when scoring that gene; drop `colocalizes_with`/`contributes_to` for CC. (Only NOT rows are excluded, §1.2.)
7. **OPEN — PI decision needed** (ai_failure_modes 2 residual, M): pre-specified fallbacks for \|U\| (or \|U ∩ scorable\|) outside an expected range and for "too few scorable U genes", plus the minimum n per calibration-reliability bin. §0 covers C2 failure, poor calibration, low Tier A yield and GLS ≥ zavg_BEF only.

## PI decisions applied to items not adopted or modified

| Topic | Decision | Reason recorded |
|---|---|---|
| UniProt 2018 D2(t0) | Not adopted | Archived UniProt release too large; D1 + D3 at t0 define H (§3.2.2). |
| Per-guide sgRNA and shared-guide checks | Not possible | DepMap guide maps and guide-level data not available locally; the portal is not scriptable (recorded in §4.3). |
| Mendelian class M (OMIM/ClinVar), CiliaCarta | Not adopted | Data not obtained; homology class H kept (§5.1). |
| CCLE metabolomics | Not adopted | Could-have; out of time budget. |
| HAP1 GI map (Billmann 2026) | Not obtained | Data not obtained; not used as a diagnostic class in §5.4. |
| Benjamini–Bogomolov hierarchical FDR | Not adopted | Σ p_cal is the U-level error statement; p-values descriptive (§0 C3, §7). |
| Clustering of the kNN graph | Demoted | Supplementary figure only (§4.5). |
| Lineage / p53 / DEMETER2 / expression checks | Restricted | Top 40 only (§4.3). |
| Physical removal of the tool's results/predictions | Implemented as git sparse checkout | The tool repo itself is never modified (§1.6). |

---

## 1. External PI (`round1_external_PI.md`)

| # | Short title | Pri | Disposition | DESIGN § / reason |
|---|---|---|---|---|
| 1 | Claim structure and low-yield branch | M | Adopted | §0 (C1–C4, decision branches, low-yield branch with tier-labelled top-40). |
| 2 | Fix assessability rule | M | Adopted-modified | §1.4 (single-gene informativeness as pre-registered strata, not a filter), §4.2 (true null: R0 over 200 matched genes; 95th percentile, not 99th; plus expression). Split-half label permutation replaced by matched-gene null (statistics 11). |
| 3 | Calibration must transfer to U-like genes | M | Adopted-modified | §3.7 (calibration fitted on H, the most U-like set, with SD/mean-effect-type covariates via R(g), coverage, family; cross-fitted; support restriction), §3.6 (covariate shift, U-reweighted estimate), §0 (branch). Isotonic refit on H after miscalibration not adopted: p_cal stays the pre-specified cross-fitted model with a caveat. U-like LOO subset: LOO is sensitivity only. |
| 4 | Term granularity and ranker | M | Adopted-modified | §3.1: three rankers (R1 raw S, R2 hypergeometric, R3 matched-gene p_emp in place of "S / expectation"), chosen once on LOO (non-U, non-H); term size 5–200; ≥ 2 supporting partners; ancestors dropped when a descendant ranks (not full elim). IC-/Smin-weighted precision@1 not adopted: replaced by precision@1 restricted to terms ≤ 50 genes and size distribution of top-1 terms (§3.3). |
| 5 | Supported vs already known; no DepMap-derived literature | M | Adopted | §6.3 (agent L blind; N1/N2/N3; DepMap-derived yes/no flag), §6.4 (DepMap-derived support counts as unaddressed), §1.5 (50-gene curation-lag audit before any U prediction; estimate = expected rediscovery rate). Novelty claims only for N3 (and N2 beyond known): Template A. |
| 6 | Exact U size and strata | M | Adopted | §1.2 (exact \|U\|, \|U ∩ DepMap\| written to CRITERIA.md at freeze; ≈ 5.2k / 4.6k), §1.4 (family, expression, informativeness, core strata; headline for U and expressed non-chemosensory non-tandem). RESEARCH_TREE.md "~2.1–2.6k" entry to be corrected at freeze (§1.6, M3). |
| 7 | Tier fallback; coverage-aware support | S | Adopted-modified | §6.1 (top-40 filled A, then B, then p_cal, tier-labelled), §4.1 (tiers use the module-level call V1′ rather than V1), §5.3 (four states separate "not measured" from "no support"; contradiction needs ≥ 2 high-reliability exclusive localisations, multi-localised exempt). |
| 8 | Strengthen success criteria | S | Adopted | §0 C2, §3.3 (GLS key secondary, two-sided, by neighbourhood-size stratum), §3.7 (calibration), §3.2.2–3.2.3 (named controls, circular annotations excluded), §0 (GLS ≥ zavg_BEF stated plainly). |
| 9 | Power the blinded literature test | S | Adopted-modified | §6.4: top 40 blind-judged; 3 decoys; exact sign-flip test on real − mean(decoy) instead of McNemar; 30 extra U genes across p_cal bins; reports on 8–10 genes (§6.5). Unaddressed rate reported via N-classes. |
| 10 | Rebalance effort | S | Adopted-modified | Clustering to supplementary (§4.5); lineage and related checks top 40 only (§4.3); deep-dive and experiment effort expanded (§6.5, Template A/B). D1/D2/D3 sensitivity matrix: none specified in v2; per-criterion counts go to CRITERIA.md at freeze (Deferred, M3). |
| 11 | Tool-tuning leakage into V1 hold-out | C | Adopted | §3.2.4 (V1 with and without hu.MAP train proteins; hu.MAP excluded from V1). |

## 2. Statistics (`round1_statistics.md`)

| # | Short title | Pri | Disposition | DESIGN § / reason |
|---|---|---|---|---|
| 1 | Size- and hub-adjusted ranking (p_emp) | M | Adopted-modified | §3.1 (R3 matched-gene p_emp, M = 500; ties by S), §3.4 (matching; excludes N(g), same-arm, genes annotated to g's targets), §4.3 (hub flag > 50% of S). Ranker chosen once among three on LOO rather than fixed; S-ranking kept as candidate R1. |
| 2 | Define hypergeometric test, demote it | M | Adopted | §3.1 (n = \|N(g) ∩ annotated background\|, query removed), §7 (descriptive only). |
| 3 | Fully specify primary endpoint | M | Adopted-modified | §3.2.2 (V2; T(g) = propagated current D1-evidence minus t0, current obo with alt_id/replaced_by, dropped obsolete counted; ≥ 1 target; one function for D1, §1.2), §3.2.4 (V1 GO CC, hu.MAP excluded). Size window 5–200 (not 5–300) at t0. |
| 4 | Gene unit, cluster bootstrap | M | Adopted | §3.5 (clusters by shared PMID or neighbour overlap; paired cluster bootstrap 10,000, seed 0, percentile and BCa; design effect reported). |
| 5 | Metrics for few targets | S | Adopted-modified | §3.3 (MRR, AUPRC for \|T\| ≥ 3, precision@1 terms ≤ 50, size distribution of top-1 terms). Information-accretion weighting not adopted (replaced by size restriction); macro averages restricted to LOO terms ≥ 10 genes not specified (Deferred, M5). |
| 6 | Baselines | S | Adopted | §3.3 (prior-only from t0 frequencies, same background and size filter; homology baseline). |
| 7 | Covariate shift H vs U | M | Adopted | §3.6 (SMDs, signal quintiles, inverse-odds U-reweighted estimate trimmed 1st/99th). |
| 8 | Systematic circularity detection | M | Adopted | §3.2.3 (Europe PMC full-text query on every supporting PMID; flagged annotations excluded and analysed separately; sensitivity on controls such as CCDC32). |
| 9 | Align H with U; power in advance | S | Adopted-modified | UniProt 2018 D2(t0): Not adopted (archived UniProt release too large; D1 + D3 at t0 define H). Sensitivity t0 = 2019-07 and ≤ 5 PMIDs: §3.2.2. \|H\|, \|T\|, clusters, MDE at freeze; underpowered if effective n < 300: §3.5. |
| 10 | Matched-gene null specification | M | Adopted | §3.4 (Mahalanobis, caliper 0.2 SD, without replacement, exclusions, SMD < 0.1; 5 matches for primary, M = 500 for p_emp, 200 for assessability). LOO annotation-permutation null (could) not adopted: not in v2. |
| 11 | Split-half null | M | Adopted | §4.2 (R(g), R0 over 200 matched genes, 95th percentile, top-25 overlap, RBO sensitivity, lineage-stratified halves, seeds 0–4), §2.5 (null genes assessable at 5% ± 2%). |
| 12 | Calibrate on temporal hold-out | M | Adopted | §3.7 (monotone logistic on top-K mean zavg, R(g), coverage, log term size, family; 10-fold cluster cross-fitting; reliability diagram, Brier, intercept and slope with CIs; LOO sensitivity only). Pre-specified 2-D isotonic not used. |
| 13 | Respect calibration support; Σ p_cal | M | Adopted | §3.7 (no p_cal outside H's 5th–95th percentile; identical pipeline; p_cal = confirmation probability), §0 C3 and §7 (Σ p_cal with cluster-bootstrap CI). |
| 14 | Role of p-values; BH scope | S | Adopted-modified | §7 (BH dropped as U-level error statement; hypergeometric p descriptive; Σ p_cal). Benjamini–Bogomolov hierarchical FDR: Not adopted (Σ p_cal is the U-level error statement; p-values descriptive). |
| 15 | Orthogonal degree bias; coverage | M | Adopted | §5.3 (row percentiles for continuous sources; degree-matched random partners, B = 1,000, (1+b)/(1+B); four states), §5.2 (source admission: co-complex odds ratio lower 95% CI > 2 on non-hu.MAP complexes). |
| 16 | Multiplicity across classes | M | Adopted | §5.3 (Holm across classes covering g), §5.4 (false-support rate on matched-gene and decoy predictions reported beside Tier A count). |
| 17 | Blinded literature test power and analysis | M | Adopted | §6.4 (3 decoys matched on compartment and term size, +1/0/−1 scoring, exact one-sided sign-flip, 30 extra U genes across p_cal bins, two judges with κ and third adjudicator, DepMap-derived support = unaddressed). |
| 18 | Decision logic and toy tests | S | Adopted | §0 (failure branches, Tier A fallback), §3.3 (intersection–union primary; primary metric on each split-half network), §2.5 (null-matrix acceptance: KS p > 0.01, ≤ 5% any-significant term). |

## 3. Data and algorithms (`round1_data_algorithms.md`)

Item 1.5 is an empty heading in the review (no content). Sections 7 and 8 are unnumbered headings and are listed as 7 and 8.

| # | Short title | Pri | Disposition | DESIGN § / reason |
|---|---|---|---|---|
| 1.1 | Hub table keyed on hgnc_id | M | Adopted | §2.1 (hub on hgnc_id), §2.2 (explicit hgnc_id gene index; never positional). |
| 1.2 | Per-source mapping rule, ambiguity dropped and counted | M | Adopted | §2.1 (Entrez/UniProt/ENSG/ENSP routes; symbol only as last resort with collision flags; no symbol joins when an ID exists; mapped/ambiguous/dropped). |
| 1.3 | Mapping QC tables | M | Adopted | §2.1 (per-source QC tables); retention-threshold test in M4 tests. |
| 1.4 | sec_ac and gene_history in manifest | S | Deferred (M4) | Not stated in v2; add to the hub build and data manifest (spurious H members from retired accessions). |
| 1.5 | (empty heading) | — | n/a | No content in the review. |
| 2.1 | D1 includes TAS/IC; feature table lacks the column | M | Adopted-modified | §1.2: D1 is computed from the GAF by one function `knownness.d1(gaf, obo, release)`, so the missing feature-table column is not needed. |
| 2.2 | "Scorable"; gate reads FREEZE.sha256 | M | Adopted-modified | §1.3 (not-scorable categories), §1.6 (FREEZE.sha256, tag, gate.check). Tool commit and DepMap SHA-256 checks are covered by the hashed frozen config (§9), not stated in §1.6. |
| 3.1 | Pair-level score per source | M | **OPEN — PI decision needed** | §5.1 defines classes and §5.3 the test, but per-source pair scores (see OPEN 4) are not specified. |
| 3.2 | Null over source-covered pairs; degree-matched | M | Adopted | §5.3 (per-gene row percentiles; degree-matched partners; absence never a contradiction). |
| 3.3 | Partner-in-predicted-term definition | M | Adopted-modified | §5.3 (partners in the predicted module vs degree-matched random sets); "all scorable members of t, not only K neighbours" to be stated in the M6 evidence scripts. |
| 3.4 | Non-independent sources | S | Adopted-modified | §5.1 (hu.MAP, DEMETER2 not counted). Burke 2023 kept as counted class S (coverage limited) and CCLE proteomics counted but flagged, contrary to the review. |
| 3.5 | Licences; ORCS preferred over Olivieri xlsx | M | Adopted-modified | §5.1 (Olivieri via BioGRID ORCS). Commit policy (no edge tables for Olivieri, BioPlex, ProteomeHD, MitoCarta, CCLE, OpenCell) Deferred (M4, `.gitignore` and `data/derived`); §8. |
| 3.6 | Drop pooled drug screens | S | Deferred (M6) | §5.1 still lists drug screens; admission test §5.2 decides whether any source enters. |
| 3.7 | Lock xlrd, h5py/anndata, networkx | M | Deferred (M4) | Environment lock; not in DESIGN. |
| 4.1 | Own driver script, threshold = 6, gate check | M | Adopted | §2.2 (API, unmodified tool), §1.6 (every pairwise script calls gate.check()); driver details in M4 scripts. |
| 4.2 | Diagonal −inf, BG-only columns | M | Adopted | §2.2 (assertion tests). |
| 4.3 | Stratified split-half; BG invariance | M | **OPEN — PI decision needed** | Lineage stratification and PatientID grouping adopted (§4.2, seeds 0–4); missingness-pattern stratification and BG(half) = BG(full) assertion not adopted (OPEN 5). |
| 4.4 | Blockwise GLS and Pearson | M | Adopted-modified | §2.2 (own blockwise implementation; verified against `Baselines.score` on ≥ 100k pairs, max abs diff < 1e-4, looser than the review's 1e-6 on 5,000 pairs). |
| 5.1 | hu.MAP train-pair reproduction | M | Adopted-modified | §2.3 (tool's HT-AP 0.345/0.242/0.146/0.134; PI authorises reading `protein_assignment.csv`); tolerance ±0.005 rather than ≤ 0.003. |
| 5.2 | Stratify by hu.MAP train proteins; collapse redundant complexes | M | Adopted-modified | §3.2.4 (stratified by train membership). Jaccard ≥ 0.7 collapse of complexes Deferred (M5, annotation build). |
| 6.1 | GO propagation with current obo | M | Adopted-modified | §3.2.2 (current obo for all releases; alt_id/replaced_by; obsolete counted). is_a/part_of-only propagation and GAF-date filter to be fixed in `04_build_annotations.py` (M5); targets sized at t0 within 5–200. |
| 6.2 | Drop NOT, colocalizes_with; IPI with/from leakage | M | **OPEN — PI decision needed** | NOT rows excluded (§1.2); the other rules not specified (OPEN 6). |
| 6.3 | Temporal complexes = GO CC only | M | Adopted | §3.2.4 (V1 = GO CC descendants of GO:0032991; Complex Portal and MitoCarta current only). |
| 6.4 | Complex Portal parsing; per-vocabulary size windows | M | Deferred (M5) | V1′ includes Complex Portal (§3.2.4); parsing rules and complex window (3–300) to go into config before the hold-out look (§9). |
| 6.5 | MitoCarta sheet/keys; Reactome leaf | S | Deferred (M5) | MitoCarta pathways in V1′ (§3.2.4); parsing details in annotation build. |
| 6.6 | Matched null excludes genes annotated to evaluation terms; match on BG | M | Adopted-modified | §3.4 (excludes N(g), same-arm, genes annotated to g's targets); BG status match not stated (M5). |
| 6.7 | Term-size bins; p-ranked variant | S | Adopted | §3.3 (precision@1 ≤ 50 genes, size distribution of top-1 terms), §3.1 (R2/R3 rankers). |
| 6.8 | Paralogue ≥ 80% identity; same-arm via HGNC | S | Adopted-modified | §3.1 (Ensembl paralogues and same arm excluded; sensitivity without exclusions), §4.3 (paralogue flags). Identity ≥ 80% flag Deferred (M4). |
| 6.9 | Low-coverage (non-BG) genes | S | Deferred (M5/M6) | NaN fraction is a covariate and stratifier (§1.4, §3.4, §3.7); separate calibration and Tier A exclusion for non-BG genes to be decided with the calibration data. |
| 6.10 | Assessable cut from calibration curve | S | Adopted-modified | §4.2 keeps the pre-specified 95th-percentile matched-gene null; calibration uses R(g) as a covariate and restricts p_cal to H's support (§3.7). |
| 7 | Verification scripts / toy tests | — | Adopted | §2.4, §2.5, §9 (toy generators, tests, independent re-derivation of reproduction numbers). |
| 8 | Pipeline layout; what is committed | — | Adopted | §8 (matrices git-ignored, summaries committed), §10; script numbering in `scripts/` (M4–M7). |

## 4. AI failure modes (`round1_ai_failure_modes.md`)

| # | Short title | Pri | Disposition | DESIGN § / reason |
|---|---|---|---|---|
| 1 | Tamper-evident freeze; physical exclusion of predictions | M | Adopted-modified | §1.6 (hash, tag `preregistration-v1`, gate, `scripts/audit_order.py` run by a fresh agent). Physical removal of `results/predictions/` implemented as git sparse checkout (repo itself never modified), not chmod. Guard-module-unchanged check not stated. |
| 2 | Gate-failure and wrong-size fallbacks | M | **OPEN — PI decision needed** | §0 branches cover C2, calibration, low Tier A yield; \|U\| range, too few scorable genes and bin minimum n not covered (OPEN 7). |
| 3 | Power simulation; one-look rule; cluster bootstrap | M | Adopted-modified | §3.5 (MDE and effective n at freeze; clusters), §9 and §3.1 (LOOKS.md one-look log; both versions reported). Power by simulation with real \|H\| folded into §3.5 computation. |
| 4 | frozen.yaml and drift test | S | Adopted-modified | §9 (frozen config hashed), header (changes logged with both rules reported); `config/frozen.yaml` pytest in M4. |
| 5 | Prediction ledger before narrative | M | Adopted | §9 (`results/ledger/*.tsv` before any narrative), §6.5, Template A. |
| 6 | Closed-book recall probe | M | Adopted-modified | §6.2 (tool-less agent; top-40 plus 40 random U genes; answers logged; genes flagged). Review also asks for the 50-gene audit sample: random U sample covers it. |
| 7 | Fixed-schema evidence table; falsification; red team | M | Adopted | §6.5, Template A (§9 falsifying observations written before literature; §13 red-team, unedited). |
| 8 | Remove cherry-picking route | S | Adopted-modified | §6.1 (top 40 by rule: tier, then p_cal), §0 C3 and §9 (full ledger), §3.2.2 (named controls labelled descriptive case series). Rule "never recompute precision from the literature-supported subset" not stated; add to M7 lint. |
| 9 | Script-resolved identifiers | M | Adopted | §2.1, §9 (script-resolved HGNC IDs; collision flags). |
| 10 | Claim-level citation verification | M | Adopted | §9, §6.5 (claims without verified source fail a lint), Template A evidence ledger (verbatim span, verified Y/N). |
| 11 | Harden blinded judging | M | Adopted | §6.3, §6.4 (templated statements, redaction, 3 decoys matched on compartment and term size, no overlapping terms, seed 0, random order, L without network outputs). |
| 12 | Validate blinded pipeline on known answers | M | Adopted-modified | §6.4: 10 H genes, ≥ 7/10 real supported, ≤ 3/30 decoys supported (review: 6 genes, 4/6 and 1/6); two judges, adjudicator; different models "where possible" not stated. |
| 13 | ID-mapping contract and tests | M | Adopted | §2.1, §9, §2.2 (explicit gene index); renames and many-to-many cases in M4 `test_idmap`. |
| 14 | Sign and orientation assertions | M | Adopted-modified | §2.4 (Chronos sign, symmetry, known complexes > 3), §2.5 (toy). Label-shuffle control on real data and K off-by-one tests Deferred (M4). |
| 15 | Single metrics module; numbers by script | S | Adopted | §9 (single metrics module with toy tests; manuscript numbers inserted from result files by script). |
| 16 | Claims ledger; independent re-derivation | M | Adopted-modified | §9 (every result checked by an agent that did not produce it, from raw outputs). `CLAIMS.tsv` format and K sweep by verifiers set in M4. |
| 17 | Task sizing; duplicate-work guard | S | Adopted-modified | §9 (one script/question per task, ≤ 300-word summary). `scripts/INDEX.tsv`, DAG and model assignment Deferred (M4). |
| 18 | Earlier project's rules in §9 | S | Adopted-modified | §7 (seeds), §3.2.4 (without ETC-I and mitoribosome), §3.3 (size-restricted precision). Macro per-term reporting and results without the ten largest terms Deferred (M5). |
| 19 | Scope-creep lint | C | Deferred (M8) | §0 scope rule stated; lint script at manuscript stage. |
| 20 | Retrospective prompt per milestone | C | Deferred (each milestone close, LESSONS.md §10) | Process item; not in DESIGN. |

## 5. Prior work (`round1_prior_work.md`)

| # | Short title | Pri | Disposition | DESIGN § / reason |
|---|---|---|---|---|
| 3.1 | Remove tuning leakage from V1 | M | Adopted-modified | §3.2.4 (stratify by hu.MAP train membership; report with and without). Complex-disjoint held-out complexes from the tool's splits not adopted; primary endpoint is V2 temporal, so V1 is secondary (§3.2.2). |
| 3.2 | Added value over existing evidence | M | **OPEN — PI decision needed** | No PPI-only or module-transfer comparator in §3.3 (OPEN 1). |
| 3.3 | Prospective audit of earlier lists | M | Adopted-modified | §6.6 (overlap with U up front; "previously proposed" flag, Template A §7). Experimental hit-rate audit of earlier lists **OPEN — PI decision needed** (OPEN 3). |
| 3.4 | Novelty policy | M | Adopted-modified | §6.3 (N1 established, N2 partial, N3 none; maps to the review's N0/N1/N2 respectively), Template A (N1 never dropped, reported as rediscovery; "not found as of date" wording). |
| 3.5 | Fix hold-out timing | M | **OPEN — PI decision needed** | Release-diff targets and t0 versus Pan 2018 (OPEN 2). |
| 3.6 | Circularity by text scan | M | Adopted-modified | §3.2.3 (full-text scan of every supporting PMID; with and without). Query terms omit "Avana" and "Chronos" (list in §3.2.3). |
| 3.7 | Selection bias in H | M | Adopted | §3.6 (metrics by signal quintile; reweighting), §3.7 (p_cal only within H's support), §0 C1 (assessable fraction). |
| 3.8 | V1 without ETC-I and mitoribosome | M | Adopted | §3.2.4. |
| 3.9 | Unknome, Tdark, Wood 2019 overlaps | S | Deferred (M3) | Unknome table is on disk (DATA.md); overlap table in CRITERIA.md at freeze; neXtProt uPE1 only after definition check. |
| 3.10 | D3 threshold, 95th percentile as sensitivity; minimum screened lines | S | Adopted-modified | §3.2.2 (≤ 5 PMID sensitivity), §1.4 (NaN fraction, SD strata). Minimum screened-line rule Deferred (M3, single-gene data in CRITERIA.md); D3/95th-percentile sensitivities not specified. |
| 3.11 | Repeat novelty search for Tier A/B at submission | S | Deferred (M8) | §6.3 does the top-40 search before reports; repeat at submission; post-freeze papers counted separately (Template A §7). |
| 3.12 | Add shinyDepMap, lncRNA module paper, DepMap co-dependency tool, coessentiality.net to LITERATURE | S | Deferred (M8) | Not part of the errata pass; add with the manuscript related-work section. |
| 3.13 | Degree-preserving rewiring null | C | Not adopted | Statistics review: adds little because out-degree is fixed at K; matched-gene null (§3.4) used instead. |
| 3.14 | CORUM 4.0 | C | Not adopted | Data not obtained (CORUM download blocked by an untrusted TLS certificate; verification not disabled, DATA.md). Complex Portal and GO CC used. |
| 3.15 | Compare at matched K against Wainberg's published GLS | C | Not adopted | GLS is re-implemented and compared directly on the same predictor (§2.2, §3.3); K = 10/50 sensitivity (§3.1). |
| §1 | Dedicated Europe PMC/bioRxiv sweep 2022–2026 for prior systematic work | M | Deferred (M8) | Run and log before any claim that no calibrated pre-registered co-essentiality re-annotation exists. |
| E1 | INTS15: re-attribute INTS10 destabilisation to Pan2022 | fix | Adopted | LITERATURE.md §1.3, §2.1 INTS15 row; errata section. |
| E2 | Wainberg journal; 102/220 belong to bioRxiv v1 | fix | Adopted | LITERATURE.md §1.2 table; errata section; `references/literature_refs.tsv` note (journal already correct). |
| E3 | TIMM29/DMAC1 framing | fix | Adopted | LITERATURE.md §2.2 negative lessons; errata section. |
| E4 | TEDC1/2 "7-year" lag | fix | Adopted | LITERATURE.md §2.1 TEDC row ("up to 7 years", Pan 2018 note); errata section. |
| E5 | Rahman 1,697 qualifier | fix | Adopted | LITERATURE.md §1.2 table; errata section. |
| E6 | Billmann "113 genes" | fix | Adopted | LITERATURE.md §1.3 marked [unverified]; errata section. |
| gap | Sparse newly added genes dominate top co-dependencies | — | Adopted | LITERATURE.md §1.4 item 9; minimum screened-line rule see 3.10. |
| 4.1 | N-class for every Tier A/B prediction | — | Adopted-modified | §6.3 (top 40; N1/N2/N3 labels). |
| 4.2 | Never drop N0; rediscovery rate with CI | — | Adopted | §1.5 (rediscovery estimate), §6.3, Template A. |
| 4.3 | Separate kinds of "already published" | — | Adopted | §1.5 (curation lag), §6.6 (prior lists), §6.3 (experimental papers; evidence level), Template A §7. |
| 4.4 | "Not found as of date"; preprints and post-freeze separate | — | Adopted | Template A (wording; post-freeze papers counted separately), §6.3. |
| 4.5 | Report states novelty class, prior work, what co-essentiality adds | — | Adopted | §6.5, Template A §1, §7, §11. |

## 6. Biology and experiments (`round1_biology_experiments.md`)

| # | Short title | Pri | Disposition | DESIGN § / reason |
|---|---|---|---|---|
| 1 | Relationship type a–e; module-level vocabulary V1′ | M | Adopted | §4.4 (types; no type-(a) without physical/co-abundance/structural support), §3.2.4 (V1′ = V1 ∪ MitoCarta ∪ Complex Portal; precision at both levels). |
| 2 | Expression and reachability annotations; negative control | M | Adopted-modified | §1.4 (expression stratum, < 10% lines = not expressed), §4.2 (non-expressed U genes scored as negative control; false-call rate), §0 C1 (assessability by stratum). CiliaCarta: Not adopted (data not obtained). HPA/GTEx tissue-enriched and secreted/TM annotations not in §1.4 (Deferred, M3, add to strata at freeze if available). |
| 3 | Artefact checks f, g, h, copy number | M | Adopted-modified | §4.3 (overlapping/bidirectional loci; copy-number co-amplification; expression and TF/lineage enrichment → type e; TP53 axis; the last two and DEMETER2 restricted to the top 40). Shared-sgRNA and per-guide check: not possible (guide maps / guide-level data not available locally; portal not scriptable). |
| 4 | Four-state orthogonal evidence; diagnostic class by family | M | Adopted-modified | §5.3 (four states; contradiction rule), §5.4 (diagnostic class by family; Tier A support when measured). Table condensed to the diagnostic class per family; HAP1 GI map (Billmann 2026) not obtained, so ER/Golgi diagnostic is L only. |
| 5 | Calibrate by family; cap mitochondrial dominance | M | Adopted | §3.7 (family covariate: mito / large machinery > 30 subunits / other), §6.1 (≤ ⅓ of top 20 OXPHOS/mitoribosome). |
| 6 | Homology (H) and Mendelian (M) classes | S | Adopted-modified | §5.1 class H (reported only). Class M (OMIM/ClinVar): Not adopted (data not obtained; homology class H kept). |
| 7 | Guide-level and modality robustness; DEMETER2 | S | Adopted-modified | §4.3 (DEMETER2 replication with pre-specified threshold, top 40). Per-guide check: not possible (guide-level data not available locally). |
| 8 | Screen top 40 for curation lag before reports | S | Adopted | §6.3 (blind novelty screen of the top 40, before reports in §6.5), §1.5 (50-gene audit). |
| 9 | Adopt Template A | M | Adopted | §6.5; `reports/TEMPLATE_candidate.md`. |
| 10 | Adopt Template B | M | Adopted | §6.5; `reports/TEMPLATE_experiments.md`. |
| 11 | CCLE metabolomics for type (c) | C | Not adopted | Could-have; out of time budget. |
