# RESEARCH_TREE.md — research record (PI memory; resume from here after a context reset)

Legend: [ ] planned · [~] in progress · [x] done · [-] abandoned/negative · [!] key finding

## Status summary (latest first)

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
- [~] M4 Tool verification: full matrix, reproduction, sign checks, split-half, source admission, audit + probe
- [ ] M5 Calibration: how well does the network predict function for characterised genes (incl. temporal hold-out)
- [ ] M6 Hypothesis generation for pre-registered genes; orthogonal evidence integration
- [ ] M7 Literature deep-dives + experiments for top candidates; per-candidate reports
- [ ] M8 Manuscript, figures, references; review rounds
- [ ] M9 REPORT.md, final LESSONS pruning
