# Chronology audit M9 (DESIGN §1.6, §9)

Run by an independent agent that produced no results, 2026-10-30, on HEAD f845eb2 (working tree has only the two audit edits below plus untracked referee files).
Tags: `preregistration-v1` and `design-frozen` both -> `afed1dd446a683071b7fdd91127641bbb5f3648a`, commit and tag time 2026-10-29 21:00:14Z.

## Change made (audit tooling only)

- `scripts/audit_order.py`: GROUPS extended with `hold-out evaluation` (`results/holdout_eval/`), `M7 literature and judging` (`results/m7/`) and `post-review revision analyses` (`results/revision/`). `results/ledger/` was already covered by the `prediction ledger` group, so it is unchanged. Matching logic (`matches_group`, prefix for trailing `/`) untouched; all earlier behaviour kept.
- `tests/test_audit_order.py`: one new test (`test_flags_later_milestone_dirs_before_tag`) that a file in each of the four directories committed before the tag is flagged. 5 of 5 tests in that file pass.

## Results

| # | check | verdict | evidence |
|---|---|---|---|
| 1 | `./.env/bin/python -I scripts/audit_order.py` | PASS (exit 0, "No ordering violations found") | first commits after tag: ledger a6dc4f0 (10-30 04:55Z), holdout_eval 7db89d2 (10-29 22:50Z), m7 c54f61e (10-30 05:05Z), revision feb6172 (10-30 08:15Z), matrices 8fcf923 (10-29 21:44Z), other pairwise 386283e (10-29 21:27Z). Pairwise paths inside the tag tree: 0. Pairwise-derived files in the working tree: 951, with mtime before the tag: 0. 23 annotation-only result files older than the tag (informational). mtimes advisory |
| 2 | `bash scripts/verify_sparse.sh` | PASS | tag exists; `external/coessentiality/results/predictions` absent; tool clone clean; tool HEAD = 3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf |
| 3 | `gate.check()` | PASS | returns tag preregistration-v1 @ afed1dd446, freeze sha256 687075e680b8a051e6482de5bb052c903afaf2942ae5a25a34cef79e5965da04, n_files 10; matches README and manuscript |
| 4 | no pairwise output predates tag `preregistration-v1` | PASS | `git ls-tree -r afed1dd` has under `results/` only agent_runs, config_checks, data_checks, env_setup.log, holdout (7 annotation/sizing/power-simulation files), ids, preregistration; nothing under matrices, assessability, verification, calibration, ledger, holdout_eval, m7, revision, orthogonal. The earliest post-tag commits (d009249, d1bc3f2, b2b3a53, 21:01-21:16Z) are the random-50 sample, recall probe and curation audit (annotation only). First pairwise commit 386283e at 21:27:56Z, 27 min after the tag |
| 5 | LOOKS.md rows precede or annotate the H-outcome commits | PASS with caveat | specification row (ranker R1, calibration spec, cluster fallback) committed f0f7aa3 (10-29 22:19:48Z), 31 min before the first look 7db89d2 (22:50:36Z). Every later H-touching commit has its LOOKS row in the same commit: 7db89d2 (M5b primary look, row +1; fa0fca2 20 s later only fills the commit column), d8959e8 (verification), 4eb041c (exploratory complementarity), feb6172 (post-review analyses; commit column filled by 0cb1373). No H outcome was committed without a row; no commit touches `results/holdout_eval/` other than 7db89d2 and 4eb041c. Caveat: for the four look rows other than the specification row, "row before run" cannot be shown from git (row and result share a commit). The manuscript already says this |
| 6 | FREEZE.sha256 files unchanged at HEAD | PASS | `shasum -a 256 -c preregistration/FREEZE.sha256`: all 10 OK; `git diff afed1dd HEAD` empty for the 10 frozen paths and for `FREEZE.sha256` itself (0 later commits touch them); SHA-256 of FREEZE.sha256 = 687075e6...da04 |
| 7 | tags still identical and annotated at the freeze commit | PASS | `git for-each-ref` creatordate 2026-10-29T21:00:14Z for both |
| 8 | full test suite `./.env/bin/python -I -m pytest -q tests/` | PASS | 160 passed, 1 skipped, 1 warning (openpyxl) in 54 s |

## Notes

- `GROUPS` entries `U predictions` (`results/u_predictions*`) and `hold-out metrics` (`results/holdout/*metrics*`) match no files; the real outputs are in `results/ledger/` and `results/holdout_eval/`, now covered. `results/calibration/`, `results/assessability/`, `results/verification/` were already in the first-commit check through other groups or are annotation-or-verification outputs committed after the tag.
- Manuscript Methods (line 1426) says the globs "do not cover the hold-out and ledger outputs". The ledger glob existed; the M6 audit ran before the ledger was created. Update the sentence and add that this M9 audit ran on all four directories by an independent agent.
- Not checked: git author/committer timestamps are self-reported (no remote); a rebased or amended history would not show here. `reviews/audit_order_M6.md` and this file are the only chronology audits that cover the later milestones.
