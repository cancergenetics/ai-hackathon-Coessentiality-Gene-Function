# RESEARCH_TREE.md — research record (PI memory; resume from here after a context reset)

Legend: [ ] planned · [~] in progress · [x] done · [-] abandoned/negative · [!] key finding

## Status summary (latest first)

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
- [~] M1 Literature and datasets
  - [~] LITERATURE.md: co-essentiality for function prediction, defining "uncharacterised", orthogonal datasets, validation designs
  - [~] Dataset feasibility survey (sources, versions, licences, sizes)
- [ ] M2 Design: DESIGN.md + up to 3 review rounds
- [ ] M3 Pre-registration: frozen list of uncharacterised genes (committed + hashed before any network analysis)
- [ ] M4 Tool verification: toy tests, reproduction of published numbers, sanity controls
- [ ] M5 Calibration: how well does the network predict function for characterised genes (incl. temporal hold-out)
- [ ] M6 Hypothesis generation for pre-registered genes; orthogonal evidence integration
- [ ] M7 Literature deep-dives + experiments for top candidates; per-candidate reports
- [ ] M8 Manuscript, figures, references; review rounds
- [ ] M9 REPORT.md, final LESSONS pruning
