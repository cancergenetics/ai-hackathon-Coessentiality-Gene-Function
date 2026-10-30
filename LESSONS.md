# LESSONS.md — process rules for running this project efficiently

One line per rule, with evidence. Final pruning after M9 (history: reviews/retro_M3.md, retro_M7.md, retro_M9.md).

1. Make "blind" and "no-look" rules mechanisms with a log (gate, LOOKS, leak check, audit_order). (`991c5f1`; M4/M6/M9 audits)
2. Log ranker and calibration spec before the single look at held-out data; label later looks exploratory. (`47631ed` → `aa381fc`; `b39691d`)
3. Specify every operational detail pre-freeze in an executable spec; dry-run the pipeline. (12–13 of 22 deviations; 401/820 ties)
4. The PI, not the implementing agent, fixes ordering, fill and endpoint semantics, including inside agent prompts. (clean-first fill; `acdad5a`)
5. Every headline number states estimand, denominator and conditioning; a value-match check is not enough. (Σp_cal 30.5 vs 4.9; 646 vs ~243)
6. Apply measured null rates back to every census or count before reporting it. (clean-negative 27%/10%)
7. One implementation per definition; an independent agent re-derives it from raw files. (7 vs 22 terms; 809/809)
8. Stratify definition-dependent claims by entry route/flag at first audit, and fix the novelty baseline (prior catalogues) before selection. (3,819 D3-only; 9/10 prior)
9. Validate any gate or check on known positives and negatives before it can demote or support. (221/269 fail; DEMETER2)
10. Blinded judging needs decoys, a known-gene validation set, two judges plus adjudicator, a leak check; κ is not validity. (18/40 vs 3/120; 9/10 vs 1/30)
11. Writer → independent red-team → revision; 5–6 role reviewers, at most 2 rounds, round 2 as ID'd diffs; check process claims against logs. (10/10 reports; round 2 minor)
12. Commit narrow with explicit paths, checkpoint before long agent runs; scripts and hashes, not bulk files; terse logs. (`afed1dd`; `379827f`)
