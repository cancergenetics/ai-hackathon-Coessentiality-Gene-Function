# Review round 2: AI-agent failure modes

Read: PROMPT, DESIGN v2.1, round-1 review and disposition, RESEARCH_TREE, LESSONS, git log/status, tool-clone git state (not `results/`). No DepMap data touched.

## 1. Are the round-1 must-fixes executable?

Mostly adopted in prose, but several have no owner, trigger or proof file. Checked against the repository: `gate.py`, `scripts/audit_order.py`, `LOOKS.md`, `CLAIMS.tsv`, `config/frozen.yaml`, `scripts/INDEX.tsv` and `preregistration/*` do not exist yet. That is fine before the freeze, but §1.6/§9 should name who creates each, when, and what file shows it ran.

- **Gate (R1-1).** §1.6 says the gate verifies "the hash and the tag", but `FREEZE.sha256` has no stated contents. The round-1 requirement that the guard module is unchanged is not stated. `audit_order.py` has "a fresh agent" but no schedule and no output file.
- **Physical exclusion.** The sparse checkout is real (`core.sparseCheckout=true`, `!/results/predictions/`; tool tree clean at 3c684c9). It is only git config. The blobs stay in `.git`, and one `git sparse-checkout disable` undoes it silently. Nothing proves it was still in force at freeze.
- **DepMap itself is ungated.** `data/raw/depmap/CRISPRGeneEffect.csv` sits readable in the tree. `gate.check()` protects only scripts that call it; an ad hoc `pd.read_csv` by any agent bypasses it. The pre-freeze single-gene strata (§1.4: SD, lines < −0.5, NaN fraction) need an explicit allow-listed reader.
- **Blind roles (§1.5 audit, §6.2 probe, §6.3 agent L, §6.4 judges).** "Blind", "no network access" and "tool-less" are instructions, not mechanisms. Nothing says which directory they run in or which files they may read.
- **Power simulation (R1-3).** Folded into the §3.5 sizing, but no script, file or owner is named.
- **CLAIMS.tsv, INDEX.tsv, `frozen.yaml`.** Deferred "to M4". The first claims (|U|, |H|, MDE) arrive at M3, so the ledger must exist at freeze.

## 2. Current process state

1. **WIP committed early.** LESSONS 4 admits the v2.1 commit swept in other agents' files (the two templates and LITERATURE errata, none of which went through round 1). Now `src/knownness.py` is untracked, which is correct. The same mistake must not happen at the freeze commit.
2. **Out-of-scope or duplicate code.** `src/` is not in DESIGN or the layout. `src/knownness.py` re-implements D1/D2/D3 that `scripts/02_gene_knownness_table.py` already computed into the committed 19,296-row feature table. DESIGN §1.2 says "one function … for every release". Two implementations can disagree silently, and the frozen list is whichever one runs last.
3. **Stale record.** RESEARCH_TREE.md still says "~2.1–2.6k" and "v1 in round 1". DESIGN says ≈ 5.2k. The tree does not mention v2, v2.1 or the disposition. PROMPT requires a milestone retrospective with a fresh agent; LESSONS 5–7 are PI-written.
4. **No agent writes into the tool clone** (status clean). Good.
5. **Building the list before the design is frozen: acceptable, with conditions.** The pre-registered thing is the list and criteria; the guarantee is blindness to network data. That holds because the criteria text was committed first (0bbb46c, 20:23:04), inputs are annotation only, and DepMap was read for the header only (per README). The real risks are (a) criteria tuned after seeing |U|, with ≈ 5.2k already seen, and (b) the feature table already existing in history, so "pre-registration" means the tag, not first existence. Neither is fatal if documented. Strata must be computed after the list hash is written, so single-gene DepMap values cannot influence membership.

## 3. Minimal additions (all before tagging `preregistration-v1`)

1. `preregistration/PROVENANCE.md` (PI writes; a fresh agent verifies). It records the timeline, the criteria-commit hash, the builder-script commit and input SHA-256s, and the statement "no DepMap values beyond the header; no pairwise computation". It also records every look at |U| and any criteria edit since v2.1 (currently none), with sizes under both versions if one occurs.
2. `FREEZE.sha256` lists: list, CRITERIA.md, `gate.py`, `config/frozen.yaml`, `knownness.py`, the tool commit and the DepMap file hashes. `gate.check()` verifies all of them.
3. `scripts/lock_depmap.sh`: `chmod a-r` on the gene-effect, CN and mutation files now. The only reader before the tag is `scripts/03_single_gene_strata.py`, which emits per-gene marginals only. Unlock happens only via a script that verifies the tag. Also add `scripts/verify_sparse.sh`, which writes `preregistration/sparse_check.txt` showing that the config and exclusion are active and that no file under `results/predictions/` exists. It runs at freeze and again at M6 start.
4. `tests/test_d1_equivalence.py`: `knownness.d1()` must reproduce the D1/D2/D3/U columns of the committed feature table exactly. Retire or import the script-02 copy. One commit, explicit paths, containing the list, `knownness.py`, the test and `CRITERIA.md`.
5. `config/agent_scopes.yaml`: for each role (audit, probe, L, judge, red-team) the working directory and allowed inputs. Blind agents run in a directory with only an ID or symbol file. Each run appends to `results/agent_runs.tsv` (role, model ID, input hashes, timestamp).
6. Create at the tag: `LOOKS.md`, `CLAIMS.tsv` (seed rows |U|, |H|, MDE), `DEVIATIONS` (as the revision log), `scripts/INDEX.tsv`, `config/frozen.yaml` (thresholds). Add `results/holdout/power_sim.md` (owner: PI; verifier: fresh agent).
7. `reviews/audit_order_M4.md`, `_M6.md`, `_M9.md`, written by a fresh agent running `audit_order.py`. M6 must pass before any ledger exists.
8. Update RESEARCH_TREE (v2.1, round 2, corrected |U|) in the freeze commit. Commit the freeze with explicit paths only; the commit diff is listed in PROVENANCE.md.

Not needed: further changes to §6 judging or citation safeguards.

**Verdict: READY AFTER MINOR CHANGES (items 1–8 above, none requiring DESIGN redesign; add one sentence to §1.6 pointing to them).**
