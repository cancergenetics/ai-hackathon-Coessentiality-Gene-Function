# RESEARCH_TREE.md — research record (PI memory; resume from here after a context reset)

Legend: [ ] planned · [~] in progress · [x] done · [-] abandoned/negative · [!] key finding

## Status summary (latest first)

### M9 — project complete (2026-10-30)
Manuscript final (v3, `manuscript/manuscript.pdf`, 36 pp; source `manuscript/src/`; S1 Text in `manuscript/supplementary/`)
after two review rounds: round 1 major revision (both referees) → post-review exploratory analyses
(`results/revision/`) and reframing → round 2 minor revision (both referees; all post-review numbers independently
recomputed) → final edits; number check clean (every miss hand-confirmed); 101 verified references; CLAIMS.tsv
regenerated (1,291 rows). Ten candidate reports carry red-team reviews and post-review novelty corrections (9/10 had
prior co-essentiality predictions; only PLEKHH3 is new). M9 chronology audit PASS (gate, sparse checkout, no pairwise
output before the freeze tag); 160 tests pass. REPORT.md and final LESSONS.md (12 rules) written.

Headline (honest) message: pre-registered, calibrated co-essentiality gives real but modest accuracy (hold-out
precision@1 0.030 vs 0.005 null; ≈ GLS; homology 0.218), only a few hundred "uncharacterised" genes carry usable signal,
expected confirmations are few (≈ 5 unconditional), and literature-supported predictions are mostly rediscoveries of
published-but-uncurated or previously predicted function — with a small set of testable hypotheses and experiments.

**Open items needing a human:** author list, CRediT, funding, human-oversight statement; repository deposit (DOI);
wet-lab validation; optional human curation of the judged statements.

### M8 — manuscript v1 reviewed; revision in progress (2026-10-31) — RESUME HERE
Manuscript v1 (manuscript/manuscript.md/.pdf/.docx; source manuscript/src/, built by scripts/79 + 80) went through
review round 1 (reviews/ms_round1_*.md): domain and statistics referees → major revision; numbers 948/953 match;
references 99/100 OK; reproducibility audit (README added; docs/AGENT_PROMPTS.md added). Post-review exploratory
analyses are committed (results/revision/SUMMARY.md): null-adjusted assessable ≈ 243 (4.9% of U); unconditional
Σp_cal ≈ 4.9; curation lag concentrated in D3-only entry route (56% vs 13% N1); 34/40 top-40 genes have prior
catalogue support (Wainberg 2021 already predicted CCDC71L, C5orf34, INAFM1; only PLEKHH3 has none); term-only judging
16/40, p = 7.1e-4; homology-else-zavg 0.224.

**Interrupted (usage limit):** two agents were stopped mid-task — (1) manuscript text revision + reviews/ms_round1_response.md
+ FigS4 (scripts/62); (2) report novelty corrections (results/revision/report_novelty_corrections.md). Any uncommitted
edits they left in manuscript/src/, reports/, scripts/62_figS4.py are UNREVIEWED: inspect `git status`/`git diff`, then
finish or `git restore`. LOOKS.md row for the post-review H look needs its commit filled.

**Remaining:** finish the two revision tasks; rebuild manuscript; review round 2 (referees re-review + numbers check);
REPORT.md (approach, follow-ups, limitations, remaining ideas); final LESSONS pruning; audit_order M9 by a fresh agent;
final commit. Optional: deposit repo (Zenodo) — needs the user.

### M7b — ten deep-dive candidate reports, red-teamed (2026-10-30)
Ten reports (selection fixed before judging) were written from machine-generated evidence bundles, then reviewed by
independent red-team agents (all ACCEPT WITH REVISIONS; zero fabricated citations across ~300 verified spans, but each
review found real framing or numeric issues) and revised. Conclusions: **INAFM1** (N3) — novel, co-dependent with the
NFE2L1–NGLY1–DDI2 (NRF1 activation) axis; label rests on weak term partners, hypothesis framed accordingly.
**PLEKHH3** (N3) — co-*advantage* with PTEN/PLEKHA1 (its #1/#2 genome-wide correlates), a putative PI(3,4)P2-arm brake
on PI3K/AKT. **CCDC71L** (N2) — Polycomb-dominated co-dependency, HP1-arm physical hints (PxVxL), lineage-fragile.
**TM2D1/TM2D2** (N2) — tentative ER/protein-QC co-dependency (AUP1/JOSD1/STUB1, CHIC2), weak partner magnitudes.
**C5orf34** (N2) — centriole-assembly (A–C linker) co-dependency conditional on TP53 status. **RBM34** (N2) — nucleolar
rRNA production (yeast Nop12 orthologue: largely rediscovery; "transcription elongation" is a vocabulary artefact).
**BICRAL** (N2) — GBAF/ncBAF subunit (rediscovery; paralogue-specificity downgraded). **TRAPPC5** (N2) — TRAPP core,
dependency tracks the TRAPPIII arm. **ANKRD52** (N1 exemplar) — exact pathway-level rediscovery of PP6–AGO2 miRNA
regulation.

**Decision note D7.** Proceed to manuscript assembly (Discussion, Abstract, Table 3 candidates), number verification,
two manuscript review rounds, REPORT.md. Narrative: calibrated, pre-registered co-essentiality gives honest, low but real
accuracy; most confident predictions are rediscoveries of uncurated literature; a handful of genuinely novel,
testable hypotheses with explicit experiments.

### M7a — blinded literature validation (2026-10-30)
Closed-book recall probe: 52/90 candidates "recognised" by the LLM (mostly complex members). Blind literature screen
(agent L, 100 genes, verbatim-checked evidence): 69 N1 / 24 N2 / 7 N3 — confirming heavy curation lag among
database-"uncharacterised" genes. Judge validation on 10 H genes passed (9/10 real, 1/30 decoys). Main blinded judging
(2 judges + adjudicator, κ = 0.975): **primary top 40: 18/40 real predictions supported vs 3/120 decoys, exact
sign-flip p = 0.0002**; S20 (secondary, uncalibrated strong signals): 19/20 vs 2/60 (p = 2e-6); extra30 (lower p_cal,
calibration check): 1/30 — support tracks p_cal. Support is concentrated in N1 genes (16/31) — the predictions mostly
recover published-but-uncurated functions; N2 2/7, N3 0/2.

**Decision note D6.** Paper framing: co-essentiality + calibration recovers function for curation-lag genes with high
specificity against decoys; genuinely novel predictions (N2/N3) are hypotheses with modest prior support. Deep-dive
reports (10 genes, fixed before judging) proceed. Caveat to report: judges credited module-label matches ("process or
module" rule), applied identically to decoys.

### M6 — predictions for U: low-yield branch (2026-10-30)
All 4,271 scorable U genes were scored with the H code path (4,137 have a reportable top term). Calibrated
probabilities are low everywhere: max p_cal 0.141, so **no gene reaches Tier A (≥0.5) or Tier B (≥0.3)** — the
pre-specified low-yield branch applies (paper leads with C1–C2; top 40 by p_cal). Σp_cal = 30.5 (95% CI 13.8–49.7)
expected confirmed top terms over 2,583 in-support genes; 5.5 (2.8–8.6) among 269 expressed+assessable in-support genes.
Negative control: 1,167 clean-negative genes, median p_cal 0.010, zero Tier-A-like calls. Orthogonal support rule
passes 0.32 of real vs 0.28 matched-gene vs 0.22 decoy predictions (n = 247 each): weak separation. Top-40-only checks
are strict: 221/269 pool genes fail ≥ 1 (DEMETER2 non-replication 182/204; leave-out changes top term in ~50%).

Primary top 40 (pure p_cal order; DEVIATIONS) is led by ANKRD52, CCDC174, CNOT10, TRAPPC5, RBM34, SSR4, CNOT11, MED31,
YPEL5, TMEM208 … — many are known complex subunits whose GO lacks experimental BP/MF (curation lag), others plausible
novel calls (TM2D1/TM2D2/CHIC2 ER-stress module, C8orf33, TANGO6, CCDC71L, PLEKHH3). Calibration support removes every
prediction in five machinery families and the strongest signals, so a secondary uncalibrated list S20 was defined
(DEVIATIONS) before any literature step.

**Decision note D5.** Fill key = p_cal (demotions inert without tiers); M6 agent's clean-first list = sensitivity.
Add S20. M7: recall probe → blind literature screen (L) → judge validation on 10 H genes → blinded judging (top 40 + S20
+ extra 30) → deep-dive reports.

### M5 — temporal hold-out: primary passes, modest absolute accuracy (2026-10-30)
On LOO (3,000 characterised genes) the frozen rule chose ranker R1 (raw S; MRR 0.169 vs R2 0.140, R3 0.111, prior
0.073); label shuffle collapses it (p@1 0.015). Ranker + calibration spec + a cluster fallback were logged (LOOKS.md,
f0922e1) before H was opened once (7db89d2). On H (809 genes with targets after circularity exclusion), zavg_BEF
precision@1 = 0.030 (95% CI 0.018–0.043) vs prior-only 0.000 and matched-gene null 0.005: **primary IUT passes**
(Δ +0.030 and +0.025, CIs exclude 0; also in all 10 split-half networks and all circularity sensitivities). zavg_BEF vs
GLS +0.006 (−0.005 to +0.017): no detectable difference. Calibration out-of-fold slope 0.82 (0.51–1.13), intercept
−0.01, c-statistic 0.86 → p_cal permitted.

The honest picture: absolute accuracy for exact GO-term prediction of later-annotated genes is low and concentrated in
the strongest-signal quintile (p@1 0.117; bottom quintiles 0). Two secondary baselines beat co-essentiality on H: the
gene's own t0 electronic/phylogenetic annotations (homology, 0.218) and hu.MAP PPI transfer (0.049). Named controls:
only TMEM242 rank 1; most controls lose their targets to circularity flags (their annotations cite DepMap-based work).
These shape the paper: co-essentiality is a calibrated, complementary signal for a minority of genes with strong
dependency, not a general annotator.

**Decision note D4.** Proceed to M6 under the "calibrated" branch. Plan an exploratory (post hoc, logged in LOOKS)
complementarity analysis: zavg_BEF on H genes lacking homology predictions, and union/agreement with homology and PPI.
Independent re-derivation of the primary is running before results are relied on.

### M4 — tool verified on DepMap 26Q3; census of assessable genes (2026-10-30)
The tool reproduces its published internal-test HT-AP exactly (zavg_BEF 0.3451, GLS 0.2423, Spearman 0.1463, Pearson
0.1341 vs 0.345/0.242/0.146/0.134) and passes 14/14 sanity checks (Chronos sign, symmetry, Integrator/CCT/mitoribosome
medians 10.9/7.6/5.1). Ten lineage × library-stratified split-half runs completed. Our GLS/Pearson rows match the tool
to < 3e-7. Orthogonal admission: 12 pair sources admitted (BioPlex OR 86 … Burke AF2 OR 3.7); Olivieri 2020 dropped
(OR 1.87, lower CI 1.58); localisation: only HPA admitted (others too few H genes).

**C1 census:** of 4,924 pre-registered genes, 4,271 are scorable, ~2.7k expressed, and **646 (13%) assessable**
(635 with the freeze-time expression column) — 590 in the headline stratum; only 2/516 chemosensory and 43/742 tandem
genes. Curation-lag audit: 42% (95% CI 29–56%) of random U genes already have established functional literature
(N1), 26% partial, 32% none. Closed-book probe: the LLM "recognises" 24/50 (mostly family-level). Caveat: clean-negative
genes reach split-half p < 0.05 at 13% (null anti-conservative for genes with some dependency) — the expression
requirement carries the specificity; reported in C1.

**Decision note D3.** Primary assessable count applies DESIGN §1.4 fully (646); contradiction rule uses the four named
localisation sources (DEVIATIONS.md). Next: M5a LOO ranker choice + label-shuffle (H closed), then log ranker +
calibration spec in LOOKS.md and open H once.

### M2–M3 — design frozen and gene list pre-registered (2026-10-29)
DESIGN.md went v1 → v2 → v2.1 → v2.2 → v2.3 through two review rounds (round 1: external PI, statistics,
data/algorithms, AI failure modes, prior work, biology/experiments; round 2: five reviewers, all "ready after minor
changes") and two item-by-item disposition checks, which caught 7 and then 32 small gaps. Key design features: claims
C1–C4 with pre-written decision branches; U = D1 ∩ (D2 ∪ D3); temporal hold-out H (t0 = GO 2018-07-02) as the primary
validation with prior-only and matched-gene nulls; calibration on H with cross-fitting and support restriction;
assessability by split-half reproducibility vs a cross-gene null plus an expression requirement; non-expressed genes as
a negative control; four-state, family-specific orthogonal evidence; blinded literature judging with decoys.

The pre-registered list U has 4,924 genes (4,275 in DepMap, 4,271 scorable); H has 820 genes and 5,965 targets
(power: MDE ≈ 0.04–0.06 precision@1). An independent agent re-derived U and H from raw files with its own code and
reproduced both exactly. Pipeline modules pass 99 tests incl. a toy test with planted modules (precision@1 1.00 on
strong modules; proximity calls removed; null calibrated); our GLS/Pearson match the tool's to < 5e-7. Next (M4): full
zavg_BEF matrix on DepMap 26Q3, reproduction of the tool's published HT-AP, sign checks, split-half runs, orthogonal
source admission, curation-lag audit and recall probe on the random 50 U genes.

**Decision note D2 (freeze).** Freeze commit afed1dd, tags `preregistration-v1` and `design-frozen`;
`preregistration/FREEZE.sha256` SHA-256 = 687075e680b8a051e6482de5bb052c903afaf2942ae5a25a34cef79e5965da04.
`gate.check()` passes. Named controls SPRING1, TEDC1/2, POU2AF2/3 fall outside the 5–200 term window and are not in H;
they stay in the descriptive case series (window 2–300). Kept the frozen (conservative) assessability rule
(toy null false-assessable 1.7%). Matching caliper will mostly fall back to nearest-M (violation rate reported).

### M1 — literature and data (2026-10-29)
LITERATURE.md (≈6.8k words, 123 Crossref-verified references) recommends: pre-register U = D1 ∩ (D2 ∪ D3) (no
experimental functional GO; UniProt score ≤ 2 or low literature/Tdark); calibrate on characterised genes with a
CAFA-style temporal hold-out (t0 ≈ 2018) using ≈11 genes whose function was first proposed via co-essentiality as named
positive controls; complexes as primary vocabulary; explicit controls for proximity/CN artefacts, mito dominance,
multifunctionality, and circularity (CCDC32 GO cites Wainberg 2021; Predictomes/HumanNet embed DepMap). Annotation
data (GO current + 5 archives, gene2pubmed, UniProt 2026_03, Unknome, TCRD, Reactome) and orthogonal data (hu.MAP 3.0,
OpenCell, HPA v25.1, Human Cell Map, STRING v12.5, BioGRID 5.0.262, ORCS, Olivieri 2020, Perturb-seq, ProteomeHD,
Burke AF2, Predictomes, Complex Portal, MitoCarta3.0) obtained; all 66 checksums verify. Not obtained: HuRI (host
down), CORUM (TLS failure).

A per-gene knownness table (19,296 protein-coding genes; 18,370 in DepMap) is built from annotation only. Under the
descriptive overlaps, D1 ∩ D3-type sets are ~2.1–2.6k genes. DESIGN.md v1 written and sent to review round 1 (external
PI, statistics, data/algorithms, AI failure modes, prior work, biology/experiments). No DepMap values read yet.

**Decision note D1.** Adopt literature-recommended U = D1 ∩ (D2 ∪ D3); keep every audited gene in U (no post hoc
removal). Exclude Predictomes/HumanNet/STRING text-mining from evidence (circular). UniProt annotation score is coarse
(TMEM14C scores 5) — used only via D2's ≤ 2 rule.

### M0 — set-up (2026-10-29)
Project initialised: prompt saved verbatim (`PROMPT.md`), git repository created, co-essentiality tool cloned read-only at
commit `3c684c9` (`scripts/00_get_tool.sh`). DepMap 26Q3 `CRISPRGeneEffect.csv` and companion files were found on the
user's machine with SHA-256 identical to the tool's own `DATA.md`, so the tool is applied to exactly the release it was
built on. Orthogonal data already available locally: BioPlex 3.0, CCLE proteomics (Nusinow 2020), DEMETER2 RNAi,
Ensembl 116 paralogues, hu.MAP 3.0 train pairs, DepMap expression. Seeds fixed in `config/seeds.yaml`.

Next: literature + dataset survey (LITERATURE.md) and a feasibility survey of public annotation/orthogonal datasets run
in parallel by agents; then DESIGN.md with explicit, reviewable pre-registration criteria for "uncharacterised"; design
review rounds; freeze and commit the gene list **before any co-essentiality computation on DepMap data**.

**Decision note D0.** Use the user-provided 26Q3 files rather than a figshare release (24Q4): the tool's hyper-parameters
(K = 0.25% of background genes, 20 PCs removed, ridge) were frozen on 26Q3, and the portal is not scriptable here.
Pre-registration hygiene rule: no agent reads the tool's `results/predictions/` or runs the scorer on DepMap until the
pre-registered list is committed and its hash recorded here.

## Tree

- [x] M0 Set-up: repo, PROMPT.md, tool pinned, user data verified (checksums), seeds fixed
- [x] M1 Literature and datasets
  - [x] LITERATURE.md: co-essentiality for function prediction, defining "uncharacterised", orthogonal datasets, validation designs
  - [x] Datasets obtained + checksummed (HuRI, CORUM unavailable)
  - [x] Knownness feature table (annotation-only)
- [x] M2 Design: DESIGN v2.3 after 2 review rounds (11 reviews) + 2 disposition checks; tag design-frozen
- [x] M3 Pre-registration: U = 4,924 genes frozen (tag preregistration-v1, afed1dd); independently re-derived
  - [x] Hold-out H = 820 genes / 5,965 targets; circularity flags (1.5% PMIDs); power sim
  - [x] Pipeline modules + toy tests (99 pass)
- [x] M4 Tool verification: reproduction PASS, sanity 14/14, split-half 10 runs, admission, C1 = 646 assessable
  - [!] 42% of "uncharacterised" genes have functional literature (curation lag)
  - [x] Recall probe random 50 (24 recognised)
- [x] M5 Calibration: R1 chosen on LOO; one look at H — primary IUT PASS (p@1 0.030 vs 0.005); calibration c 0.86
  - [!] Homology baseline (0.218) and PPI transfer (0.049) beat co-essentiality on H; signal in top quintile (0.117)
  - [x] Independent re-derivation of H primary: VERIFIED (809/809 agreement)
  - [x] Exploratory: co-essentiality hits largely distinct from homology hits; hit@5 ≈ prior
- [x] M6 Predictions for 4,137 U genes; max p_cal 0.141 → low-yield branch; top 40 by p_cal; S20 secondary list
  - [-] Orthogonal support barely separates real from null predictions (0.32 vs 0.28 vs 0.22)
- [x] M7 Literature deep-dives + experiments for top candidates; per-candidate reports
  - [!] Blinded judging primary PASS: 18/40 vs 3/120 decoys, p = 0.0002; S20 19/20; extra30 1/30
  - [x] L screen 100 genes: 69 N1 / 24 N2 / 7 N3; recall probe 52/90
  - [x] Deep-dive reports (10 genes): written, red-teamed, revised
- [x] M8 Manuscript: v1 → round 1 (major) → revision → round 2 (minor) → final v3
- [x] M9 REPORT.md, final LESSONS pruning, M9 chronology audit
