#!/usr/bin/env python
"""91_claims_from_manuscript.py -- populate CLAIMS.tsv rows automatically from manuscript/manuscript.md (manuscript
review round 1, reproducibility request). POST-REVIEW tooling; reads only.

Every number in the manuscript that carries a `<!-- src: ... -->` tag becomes one row, using the extraction and
screening functions of verify/check_manuscript_numbers.py (imported, not modified): the number is attached to the tag
that follows it in the same sentence (or, for a table cell, the table's trailing comment), and the screening step
reports whether the value occurs (to the manuscript's precision) in a cited file. Years and untagged numbers are
skipped. The generating script is inferred from the source path (lookup table below; blank if unknown).

Columns: CLAIMS.tsv's (claim_id, manuscript_location, statement, value, source_file, source_key, script, verified_by)
+ line, screen_status (hit / miss / nofile), cited_paths. source_key is left blank for the PI.
Default output: results/revision/CLAIMS_preview.tsv (the PI moves it to CLAIMS.tsv).
Run: .env/bin/python -I scripts/91_claims_from_manuscript.py [--out PATH]
"""
from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cmn", ROOT / "verify/check_manuscript_numbers.py")
cmn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmn)

SCRIPT_BY_PATH = [
    (r"results/holdout_eval/(core|per_gene_core|comparisons_core|splithalf|v1|circularity_sensitivity|controls_case_series|covariate_smd|signal_quintiles|top1_size)",
     "scripts/32_holdout_core.py"),
    (r"results/holdout_eval/secondary", "scripts/33_holdout_secondary.py"),
    (r"results/holdout_eval/(calibration|reliability_oof)|results/calibration/model_H", "scripts/34_calibration_fit.py"),
    (r"results/holdout_eval/(fig_|SUMMARY)", "scripts/35_holdout_figures.py"),
    (r"results/holdout_eval/exploratory", "scripts/36_holdout_exploratory.py"),
    (r"results/calibration/loo_", "scripts/30_loo_ranker_choice.py"),
    (r"results/calibration/label_shuffle", "scripts/31_label_shuffle.py"),
    (r"results/ledger/u_predictions|results/ledger/u_top5|results/ledger/u_partners", "scripts/40_u_predictions.py"),
    (r"results/ledger/(u_pcal|pcal_summary|negative_control_pcal)", "scripts/41_pcal.py"),
    (r"results/ledger/u_flag", "scripts/42_artefact_flags.py"),
    (r"results/ledger/(support|false_support|negative_control\.tsv)", "scripts/43_orthogonal_support.py"),
    (r"results/ledger/(tiers_all|top40\.tsv|top40_checks|top40_fill|prelim_top40|checks_all|top40_partners)",
     "scripts/44_tiers_top40.py"),
    (r"results/ledger/(M6_SUMMARY|m6_results|figdata)", "scripts/45_m6_summary.py"),
    (r"results/ledger/top40_primary", "scripts/46_top40_primary.py"),
    (r"results/m7/judge/(analysis|scores|leak_check|disagreements)", "scripts/52_judge_analysis.py"),
    (r"results/m7/judge/packets|scripts/51_judge_packets", "scripts/51_judge_packets.py"),
    (r"results/m7/(s20|extra30|hval10|probe_list|answer_key|statements|report_selection)", "scripts/50_m7_prep.py"),
    (r"results/m7/L/", "agent L (literature screen)"),
    (r"results/m7/recall_probe|results/audit/recall_probe", "agent recall probe"),
    (r"results/audit/curation_lag", "agent audit (DESIGN §1.5)"),
    (r"results/audit/random50", "scripts/09_random_u_sample.py"),
    (r"results/assessability/", "scripts/15_assessability.py"),
    (r"results/holdout/(H_genes|H_targets|holdout_sizing)", "scripts/04_holdout_sizing.py"),
    (r"results/holdout/circularity", "scripts/05_circularity_query.py"),
    (r"results/holdout/power_sim", "scripts/08_power_simulation.py"),
    (r"results/orthogonal/", "scripts/20_source_admission.py"),
    (r"results/verification/tool_reproduction", "scripts/11_reproduce_tool.py"),
    (r"results/verification/sanity", "scripts/12_sanity_checks.py"),
    (r"results/verification/matched", "scripts/13_matched_lists.py"),
    (r"results/verification/baseline", "scripts/16_baseline_rows.py"),
    (r"manuscript/figures/source_data/(Fig5|Table2)", "scripts/61_figure5.py"),
    (r"manuscript/figures/source_data/", "scripts/60_figures.py"),
    (r"preregistration/", "scripts/03_build_preregistration.py"),
    (r"results/preregistration/", "scripts/02_gene_knownness_table.py"),
    (r"results/revision/", "scripts/90_revision_analyses.py"),
    (r"^(DESIGN\.md|config/frozen\.yaml|DEVIATIONS\.md|LOOKS\.md|PROMPT\.md|docs/)", "(specification/log document; no script)"),
    (r"^verify/", "verify/rederive_holdout.py; verify/rederive_prereg.py"),
    (r"results/matrices/", "scripts/10_full_matrix.py"),
    (r"^reports/", "agent report writer (scripts/70_report_bundles.py inputs)"),
    (r"^reviews/", "(review document; no script)"),
    (r"config/requirements", "(environment lock; no script)"),
]


def script_for(paths: list[str]) -> str:
    out = []
    for p in paths:
        for rx, s in SCRIPT_BY_PATH:
            if re.search(rx, p):
                if s not in out:
                    out.append(s)
                break
    return "; ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "results/revision/CLAIMS_preview.tsv"))
    a = ap.parse_args()
    rows = cmn.analyse(cmn.parse_manuscript(), cmn.git_tracked())
    out, n = [], 0
    for r in rows:
        for x in r["tagged"]:
            if x["year"]:
                continue
            n += 1
            paths = cmn.parse_paths(x["tag"])
            src = x["hit_files"] or paths
            out.append(dict(claim_id=f"M{n:04d}", manuscript_location=r["section"] or "front matter",
                            statement=r["text"][:240], value=x["tok"], source_file="; ".join(src), source_key="",
                            script=script_for(src), verified_by="verify/check_manuscript_numbers.py",
                            line=r["line"], screen_status=x["status"], cited_paths="; ".join(paths)))
    df = pd.DataFrame(out)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, sep="\t", index=False)
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import revision_common as RC
    R = RC.Registry("a9", "A9. CLAIMS.tsv preview from manuscript src tags (reproducibility) [post-review tooling]")
    f = "results/revision/CLAIMS_preview.tsv"
    R.add("tagged numbers extracted (years excluded)", len(df), f)
    R.add("screening hit / miss (value found in a cited file?)",
          f"{int((df.screen_status == 'hit').sum())} / {int((df.screen_status == 'miss').sum())}", f,
          "miss rows need a manual look (rounding, derived values, wrong file)")
    R.add("rows with a generating script inferred", int((df.script != "").sum()), f)
    R.note("scripts/91_claims_from_manuscript.py reuses verify/check_manuscript_numbers.py extraction/screening; "
           "source_key left blank for the PI; the PI moves the preview to CLAIMS.tsv.")
    R.save()
    print(f"{len(df)} tagged numbers -> {a.out}; screening: {df.screen_status.value_counts().to_dict()}; "
          f"script inferred for {int((df.script != '').sum())}")


if __name__ == "__main__":
    main()
