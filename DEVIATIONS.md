# DEVIATIONS.md

Log of changes to the frozen design after the `design-frozen` tag (DESIGN.md is not edited after the tag). Each entry gives the date, the DESIGN section, the change, the reason, and the results affected; affected results are reported under both the frozen and the changed rule.

| Date | Section | Change | Reason | Affected results |
|---|---|---|---|---|
| 2026-10-29 | §5.3 contradiction rule (interpretation, not a change) | The contradiction rule uses the four sources it names explicitly (HPA Enhanced/Supported, OpenCell, Human Cell Map, MitoCarta) irrespective of §5.2 localisation admission; L-class *support* uses only admitted sources (HPA). | §5.2 admission failed OpenCell/HCM/MitoCarta only for coverage (< 200 H genes: 30/153/73), not agreement (0.78–0.92); without this reading the frozen contradiction rule could never fire. | Contradiction calls; reported also with HPA-only contradiction (which never fires). |
| 2026-10-29 | §5.2 admission (unspecified details filled) | Bootstrap 1,000 reps; complex size 2–300; GO CC complex membership from direct annotations (propagated as sensitivity; same verdicts); continuous pair = edge if mean of two row percentiles ≥ 0.95. | DESIGN/frozen.yaml silent; choices made before any U prediction existed. | results/orthogonal/admission.md |
