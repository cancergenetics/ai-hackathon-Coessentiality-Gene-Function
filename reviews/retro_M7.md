# Retrospective M4–M7 (fresh-process reviewer)

## 1. What should we stop doing?

1. **Writing design documents inside DEVIATIONS cells.** The M5b row is nine sub-decisions in one cell; the §4.3 and M6 rows are similar. DEVIATIONS is 2,733 words and dates are not monotone. Put mechanics in a `results/<milestone>/SPEC.md` committed before the run; keep one line in the log.
2. **Letting implementing agents choose ordering semantics.** The M6 "clean-first" fill ranked p_cal≈0 genes above p_cal≥0.06 genes and kept MARF1/STK40 despite §4.3 exclusions; the PI overrode it (`top40_primary.tsv`).
3. **Gating on unvalidated checks.** Top-40-only checks failed 221/269 pool genes (DEMETER2 non-replication 182/204); never tried on H or negatives first.
4. **Committing bulk artefacts file by file** (repeats M3 stop 2): `de0aacb` (100 L files), `41c7cb2` (100 packets), `6fb9c3f` (20 PNGs, 1,100-line script).
5. **Long first-draft reports.** Drafts ran 209–599 lines (BICRAL 599 → 474); every red-team still found numeric or framing errors. Cap length; require a numbers-check script per report.
6. **Burying the strict reading in a caveat.** Judges credited module-label matches (D6); only 16/40 are supported on terms alone. Report both beside the headline 18/40.

## 2. What worked well

- **Specification before look.** Ranker chosen on LOO and calibration spec logged (`f0922e1`) before H was opened once (`7db89d2`); stronger baselines (homology 0.218) were reported anyway.
- **Independent verification.** `reviews/audit_order_M4.md`/`_M6.md` passed; the M5b verifier found the R1 tie-break (401/820 tied) and the 646/635 expressed-count gap.
- **Blinded validation design.** Zero leaks (`41c7cb2`), judge validation on 10 H genes first (`691244d`: 9/10 vs ≤1/30), two judges plus adjudicator (κ 0.975), sign-flip p=0.0002 (`584f2f9`); report selection fixed beforehand (`8c858a5`).
- **Honest low-yield handling.** Max p_cal 0.141 triggered the pre-specified branch; S20 and extra30 were declared before literature work and kept separate (extra30 1/30: support tracks p_cal).
- **Writer → red-team → revision.** 10/10 reports revised; TM2D1/2 downgraded (`fececea`); RBM34 "elongation" shown to be a vocabulary artefact; ~300 spans checked, no fabricated citations.

## 3. DEVIATIONS since the freeze: 21 rows

| Class | n | Rows |
|---|---|---|
| Unspecified detail, filled | 12 | admission, RBO p, LOO details, M5b, TF list, M6 scoring, artefact flags, top-40 checks, tiers/type, fill iteration, R1 tie-break, judged statements |
| Interpretation / implementation gap | 3 | contradiction rule, expressed definition (646 vs 635), low-yield fill |
| Real change or addition | 4 | cluster fallback, S20, HPA tissue stratum dropped, recall-probe scope |
| Erratum | 2 | cluster count, compute note |

The tie-break was found only after M5b; just 4/21 changed what the study does.

**Most preventive specification:** an executable parameter spec in `frozen.yaml` (every script parameter, tie-break, fill rule, covariate release, named list file), validated by a full pipeline dry run on LOO plus a mock U before the tag. That would have prevented about 12–14 rows.

## 4. Proposed pruned LESSONS.md (12 rules)

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
