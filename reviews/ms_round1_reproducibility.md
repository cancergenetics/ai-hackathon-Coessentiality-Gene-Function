# Manuscript round 1: reproducibility and integrity audit

Scope: manuscript.md (Methods, safeguards, availability, Supporting information), PROMPT.md, DATA.md, config/, DEVIATIONS.md, LOOKS.md, preregistration/, reviews/audit_order_M*.md, git log (64 commits, UTC). `data/` listed only; `check_data.sh` not run.

## Scripts run
- `audit_order.py`: no violations. Both tags point to afed1dd (2026-10-29 21:00:14); first pairwise commit 386283e (21:27:56). Blind spot: its globs match nothing for "U predictions" and "hold-out metrics". By hand, `results/holdout_eval` first appears in 7db89d2 (22:50) and `results/ledger` in a6dc4f0, both after the tag.
- `verify_sparse.sh`: PASS. Committed `sparse_check.txt` still says "tag does not exist" (written pre-tag; stale).
- All 10 `FREEZE.sha256` files re-hash identically; the hash of FREEZE.sha256 (687075e6…) matches RESEARCH_TREE D2. DESIGN, frozen.yaml, seeds.yaml and knownness.py are unchanged since afed1dd.

## (1) Process claims
- **Pre-registration timing and hash:** supported by history. No git remote exists, so tags and timestamps are self-reported (M1).
- **One look at H:** largely true. Spec row f0f7aa3 (22:19) precedes the look 7db89d2 (22:50); dry runs used LOO genes (`scripts/32` dry branch). The look's LOOKS row was committed together with the results, so "row before run" rests on the agent's word. LOOKS also logs a verification re-run and a post hoc exploratory look; Methods mention neither.
- **21 deviations:** count correct. "Each logged before the results it affects were computed" is false for at least two. The R1 tie-break was "found by independent verifier after M5b" (d8959e8), and the top-40 fill was "decided after M6". The 646/635 assessability gap was found after M4 output. Row dates are non-monotone and disagree with commits (spec row dated 10-30, committed 10-29).
- **Independent re-derivations, κ, sign-flip, red-teams:** supported (`verify/*.md`; κ 0.931 and 0.975, p = 0.0002, 18/40 vs 3/120 in `results/m7/judge/analysis_*.md`; 10 red-team files, each report revised afterwards).
- **"Fresh agents ran audit_order":** overstated. The M6 file says it was run "by the M6 analyst agent". DESIGN.md (line 69) requires M4, M6 and M9; no M9 audit is committed.
- **"Agent scopes restricted each role":** overstated. `agent_scopes.yaml` is headed TEMPLATE. `results/agent_runs.tsv` has one row (DESIGN §9 wants every run), and `results/agent_log/` is absent. No agent prompts (L, judges, recall probe, writers, red-team) are committed, so blinding cannot be audited.
- **"CLAIMS.tsv maps manuscript numbers":** only 6 rows. The real mapping is 81 `<!-- src -->` comments, 13 of which are not file paths.

## (2) DATA.md versus use
- Every checksummed file has source, version, SHA-256 and licence in DATA.md, and every `data/raw` path in scripts/ and src/ is covered.
- Downloaded but used by no analysis script: Predictomes, Reactome, BioGRID ORCS, OmicsProfiles, gene_info, TCRD READMEs. Unknome feeds only the retired script 02. DATA.md is titled "datasets used".
- Methods say Predictomes and HumanNet "were reported only". Neither is in any result, and HumanNet is in no data file.
- DepMap rows are "26Q3 (user-stated)", with no URL or DOI, and the files "carry no version stamp". HGNC has "download date unknown".
- Licences "unverified": BioPlex, CCLE proteomics, ProteomeHD, MitoCarta, hu.MAP training files.

## (3) Scripts and run order
Every script and path named in the manuscript exists. There is **no top-level README**; `docs/PIPELINE.md` covers modules, not script order. Not reproducible as written:
- `80_build_manuscript.sh` hardcodes `pandoc` (env override exists).
- `requirements.lock.txt` has `packaging @ file:///home/conda/...` and no Python version.
- DepMap files are "user-provided", with no fetch script.
- The sparse-checkout step (`00_get_tool.sh`) and `m4/m5/m5b/m6_common.py` are undocumented for a reader.

## (4) Restricted and copyrighted material
Nothing under `data/` or `external/` is tracked. Scratch dirs (about 13 MB of cached literature) are gitignored and never entered history. Olivieri (CC BY-NC-ND) appears only as admission summary statistics, with no pair table. `results/m7/L/` (105 files, 385 kB) holds short verbatim abstract sentences. The largest tracked file is the DepMap-derived `u_partners.tsv` (10 MB). `support.tsv` carries per-pair p-values from admitted sources (BioPlex and MitoCarta terms unverified).

## (5) Seeds
`seeds.yaml` is [0–4] and mirrored in `frozen.yaml`, but only about 7 scripts read it; most RNGs hardcode 0 or `B.SEED`. The tool's internal seed is not recorded. LLM steps have no recorded seeds, temperatures or prompts, so agent steps are not reproducible.

## (6) Supporting information
All listed S1–S8 Tables, 10 reports, S1 Text and S1 Data exist. Separate experiment-plan files exist only for ANKRD52 and TRAPPC5; the others are inside the reports.

## Fixes
**MUST**
- M1. Deposit the repo (Zenodo or OSF) and push the tags. Cite afed1dd, the FREEZE.sha256 hash and the DOI, and say git times are self-reported.
- M2. Correct "each before the results it affects" and list the tie-break, top-40 fill and assessability count as post-result changes.
- M3. Add a root `README.md` with the following content.
  - Python 3.12 and a portable lock.
  - DepMap URLs and DOIs.
  - Run order: 00, 01a–d, 02–09, FREEZE and tag, 10–16, 20, 30–36, 40–46, 50–52, 60–61, 70, 79–80.
  - Which steps call the gate and which are agent-only.
  - Runtimes and disk (6 matrices at 1.35 GB each).
  - Seeds and expected outputs.
- M4. Fix "fresh agents ran audit_order". Commit an M9 audit and extend the globs to `holdout_eval`, `m7` and `ledger`.
- M5. Soften the scopes claim, complete `agent_runs.tsv`, and commit role prompts or templates for the blinded agents.
- M6. Remove "Predictomes, HumanNet reported only", or add the analysis. Drop HumanNet or add it to DATA.md.

**SHOULD**
- S1. Add DepMap URLs and DOIs and the HGNC date. Mark unused files "not used in analyses". Resolve the "unverified" licences.
- S2. Mention the verification re-run and the exploratory look next to "one look". Add a dating note to LOOKS and DEVIATIONS (do not edit rows).
- S3. Make the build script and lock file portable.
- S4. Expand CLAIMS.tsv or drop the claim. Fix the 13 non-file src comments.
- S5. Read seeds from `seeds.yaml` everywhere. Record the tool's seed and each agent's model ID and temperature.

**COULD**
- C1. Refresh `sparse_check.txt`.
- C2. Note that L quotes are short abstract extracts.
- C3. Print the `check_data.sh` output into `results/data_checks/`.
