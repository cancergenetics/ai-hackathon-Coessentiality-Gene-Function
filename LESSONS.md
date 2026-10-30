# LESSONS.md — process rules for running this project efficiently

One line per rule, with evidence. Pruned at each milestone (M3: reviews/retro_M3.md; M7: reviews/retro_M7.md).

1. Make "blind" and "no-look" rules mechanisms with a log (gate, LOOKS, leak check). (`41c7cb2`; audit_order_M4/M6)
2. Log ranker and calibration spec before the single look at held-out data. (`f0922e1` → `7db89d2`)
3. Specify every operational detail pre-freeze (tie-breaks, fills, covariate release, list files) and dry-run the whole pipeline. (12/21 deviations; 401/820 ties)
4. The PI, not the implementing agent, fixes ordering and fill semantics. (clean-first fill overridden)
5. Validate any gate on known positives and negatives before it can demote. (221/269 failures)
6. One implementation per definition; an independent agent re-derives it from raw files. (7 vs 22 terms; 646 vs 635)
7. Writer → independent red-team → writer revision, with a numbers-check script. (10/10 reports revised)
8. Blinded judging needs decoys, a known-gene validation set, two judges plus adjudicator, and a leak check. (18/40 vs 3/120; 9/10 vs 1/30)
9. Declare secondary and sensitivity lists before any literature step; keep them separate. (S20, extra30)
10. Use 5–6 role-specific reviewers, at most 2 rounds, later rounds as diffs with item IDs, disposition checked against text.
11. Commit narrow with explicit paths; scripts, hashes and manifests, not bulk derived files. (`afed1dd`; `6fb9c3f`)
12. Keep logs terse (one-line deviation, spec in a file), update the tree each milestone, give parallel agents separate scratch dirs. (M5b row; M7 batch ad overwrite)
