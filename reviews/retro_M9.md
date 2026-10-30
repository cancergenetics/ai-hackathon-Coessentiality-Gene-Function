# Retrospective M8 (manuscript) and project overall (fresh-process reviewer)

## 1. What should we stop doing?

1. **Treating the numbers-check as validation.** Round 1 matched 948/953 tokens, yet the real errors were estimand or denominator errors (`ms_round1_numbers.md`; referee stats M7).
2. **Unconditioned headline numbers.** Σp_cal 30.5 assumes every gene gains annotation (unconditional 4.9). The 646/635 census was not null-adjusted (about 243); the fix was itself a lower bound (round 2 M4).
3. **Judging novelty by literature screen alone.** `cb6b460`: 9/10 report genes had catalogue predictions (Wainberg 2021).
4. **Endpoint rules living only in agent prompts.** Module-label crediting was logged retrospectively (`017fa97`).
5. **Unchecked process claims.** "Fresh agents ran audit_order" (M6 analyst did), "deviations logged before results" (false for 2–3), one-row `agent_runs.tsv`.
6. **Bloat and revision narrative.** ~19k words; Results 8.9k (referee asks 5.5k). Revision-introduced overclaims (N1 over-attributed to complexes) surfaced only in round 2.
7. **Unguarded long agent runs.** `69ac1ca`: usage limit left unreviewed edits.

## 2. What worked well

- **Spec before single look**, with later exploration labelled `[post-review exploratory]` and logged first (`7db89d2`; `feb6172`). No pre-specified result changed in revision.
- **Role-specific referees:** major → minor in one round; Done/Not-done response letter (`ms_round1_response.md`).
- **Independent audits:** 809/809 re-derivation; `audit_order_M9` (tooling extended, 5/5 tests); round-2 numbers check.
- **Honest negative framing** (GLS parity, homology 0.218, low p_cal); reports corrected (`cb6b460`).

## 3. What manuscript review caught that earlier steps missed

| Finding | Should have been caught at |
|---|---|
| Conditional p_cal / Σ (30.5 vs 4.9) | M6 headline; DESIGN stats review |
| Assessability null overcount (646 → ~243) | M4 verifier (checked count, not null); M6 clean-negative rates never applied back |
| Novelty vs prior catalogues (1/10 new) | DESIGN prior-work reviewer; M7 report selection |
| "Uncharacterised" definition artefact (3,819 D3-only; 2,248 UniProt ≥4) | DESIGN data reviewer; random-50 audit (`b2b3a53`) should be stratified by entry route |
| Unlogged module crediting; κ read as validity | Judge validation spec (`691244d`) |
| "Calibration adequate" on 24 events | M5b look; events-per-parameter rule |

Pattern: every miss was a definition or denominator issue, found by readers asking "per what?".

## 4. Proposed FINAL LESSONS.md (12 rules)

1. Make "blind" and "no-look" rules mechanisms with a log (gate, LOOKS, leak check, audit_order). (`41c7cb2`; M4/M6/M9 audits)
2. Log ranker and calibration spec before the single look at held-out data; label later looks exploratory. (`f0922e1` → `7db89d2`; `feb6172`)
3. Specify every operational detail pre-freeze in an executable spec; dry-run the pipeline. (12–13 of 22 deviations; 401/820 ties)
4. The PI, not the implementing agent, fixes ordering, fill and endpoint semantics, including inside agent prompts. (clean-first fill; `017fa97`)
5. Every headline number states estimand, denominator and conditioning; a value-match check is not enough. (Σp_cal 30.5 vs 4.9; 646 vs ~243)
6. Apply measured null rates back to every census or count before reporting it. (clean-negative 27%/10%)
7. One implementation per definition; an independent agent re-derives it from raw files. (7 vs 22 terms; 809/809)
8. Stratify definition-dependent claims by entry route/flag at first audit, and fix the novelty baseline (prior catalogues) before selection. (3,819 D3-only; 9/10 prior)
9. Validate any gate or check on known positives and negatives before it can demote or support. (221/269 fail; DEMETER2)
10. Blinded judging needs decoys, a known-gene validation set, two judges plus adjudicator, a leak check; κ is not validity. (18/40 vs 3/120; 9/10 vs 1/30)
11. Writer → independent red-team → revision; 5–6 role reviewers, at most 2 rounds, round 2 as ID'd diffs; check process claims against logs. (10/10 reports; round 2 minor)
12. Commit narrow with explicit paths, checkpoint before long agent runs; scripts and hashes, not bulk files; terse logs. (`afed1dd`; `69ac1ca`)
