# Chronology audit

Repository: `<project root>`  
Generated: 2026-10-29 21:56:00Z

## Tags

| tag | commit | commit time (UTC) | tag-object time (UTC) |
|---|---|---|---|
| preregistration-v1 | `afed1dd446` | 2026-10-29 21:00:14Z | 2026-10-29 21:00:14Z |
| design-frozen | `afed1dd446` | 2026-10-29 21:00:14Z | 2026-10-29 21:00:14Z |

`preregistration-v1` and `design-frozen` point to the same commit.

## First commit touching pairwise-derived outputs

| group | first commit | commit time (UTC) | subject | vs tag |
|---|---|---|---|---|
| U predictions | none | — | — | no commits |
| prediction ledger | none | — | — | no commits |
| hold-out metrics | none | — | — | no commits |
| matrices manifests | `8fcf923b78` | 2026-10-29 21:44:41Z | M4: full zavg_BEF matrix, tool reproduction (PASS), sanity c | after tag (ok) |
| other pairwise outputs | `386283e71a` | 2026-10-29 21:27:56Z | M4: orthogonal loaders, support test, source admission (12 p | after tag (ok) |

Pairwise-derived paths inside the `preregistration-v1` tree: 0

## mtimes under results/ vs tag time

Reference time: `preregistration-v1` commit 2026-10-29 21:00:14Z.
- Non-pairwise result files older than the tag (annotation-only; informational): 23
- Pairwise-derived files present: 11; with mtime before the tag: **0**

(mtimes are advisory; a checkout or copy resets them.)

## Result

No ordering violations found.

---

# Independent audit findings (role: audit, M4)

Run: `scripts/audit_order.py` exit 0 (output above); `bash scripts/verify_sparse.sh` PASS (tag exists; results/predictions absent from working tree; tool clone clean, HEAD 3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf).

| check | verdict | evidence |
|---|---|---|
| (a) tags identical; FREEZE verifies | PASS | `git rev-parse preregistration-v1^{commit} design-frozen^{commit}` both `afed1dd446a683071b7fdd91127641bbb5f3648a`. `gate.check()` returned without GateError: n_files 10, freeze_sha256 687075e6...da04. Freeze file is `preregistration/FREEZE.sha256` (not repo root). |
| (b) no pairwise DepMap outputs before tag | PASS | `git log --name-only` to the tag: no path under results/matrices, results/assessability, results/verification or any sanity/neighbour list/zavg/matrix file. Only hits are source code (src/coess_matrix.py, src/neighbours.py, their tests, commit a25e6fb) and orthogonal-data manifests (config/data_manifest_*.tsv). Tag tree results/ holds only annotation/hold-out/ID/prereg files; largest blobs are annotation tables. Note: results/preregistration/depmap_gene_summaries.tsv is a per-gene DepMap summary (not pairwise), present pre-tag. First post-tag pairwise commit is 386283e/8fcf923 (21:27-21:44Z, tag 21:00Z). |
| (c) FREEZE files unchanged at HEAD | PASS | `shasum -a 256 -c preregistration/FREEZE.sha256`: all 10 OK; `git diff --stat preregistration-v1 HEAD` over those paths empty (they are not in the diff name list). Data hashes in header comments not re-verified here (raw data not in git). |
| (d) power_sim reproducible | PASS | Copy of scripts/08_power_simulation.py with only the ROOT constant made absolute and output path pointed to scratchpad (<scratchpad>); `diff` vs results/holdout/power_sim.md: byte-identical. results/holdout and the script unchanged since tag. |
| M4 numbers (summary.md) | PASS | Own script on assessability_U.tsv + frozen U table: U 4,924 unique, same ID set as frozen; scorable 4,271; scorable & expressed 2,625; p<0.05 among scorable 842; assessable (scorable & expressed & p<0.05) 635, identical gene-by-gene to stored column; `expressed` equals frozen column; headline stratum (expressed, not chemosensory, not tandem) recomputed 2,439 genes, 2,343 scorable, 590 assessable; assessable_design 646; lineage-restricted 106. All match summary.md. |

Overall: PASS on all checks; no ordering violations. Only file written: this report (uncommitted).
