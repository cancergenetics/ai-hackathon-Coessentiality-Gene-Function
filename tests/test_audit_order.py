"""Tiny tests for scripts/audit_order.py on throw-away git repositories.

Run: .env/bin/python -I -m pytest -q tests/test_audit_order.py
"""
import importlib.util
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("audit_order", os.path.join(ROOT, "scripts", "audit_order.py"))
ao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ao)


def git(repo, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def commit(repo, files, msg, date):
    for p, txt in files.items():
        f = repo / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(txt)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg, date=date)


def freeze(repo, date):
    git(repo, "tag", "-a", "preregistration-v1", "-m", "p", date=date)
    git(repo, "tag", "-a", "design-frozen", "-m", "d", date=date)


def init(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q")
    return repo


def test_clean_chronology(tmp_path):
    repo = init(tmp_path)
    commit(repo, {"preregistration/FREEZE.sha256": "x\n", "results/ids/hub.tsv": "a\n"}, "freeze",
           "2026-01-01T00:00:00+00:00")
    freeze(repo, "2026-01-01T00:00:00+00:00")
    commit(repo, {"results/ledger/u_predictions.tsv": "g\n", "results/holdout/H_metrics.tsv": "m\n",
                  "results/matrices/manifest.tsv": "m\n"}, "preds", "2026-02-01T00:00:00+00:00")
    t = time.time() + 3600  # files written after the tag
    for p in repo.joinpath("results").rglob("*"):
        if p.is_file():
            os.utime(p, (t, t))
    md, flags = ao.build_report(repo)
    assert flags == [], md
    assert "No ordering violations found" in md and "after tag (ok)" in md


def test_flags_pairwise_output_before_tag(tmp_path):
    repo = init(tmp_path)
    commit(repo, {"results/u_predictions_v0.tsv": "g\n"}, "early preds", "2025-12-01T00:00:00+00:00")
    commit(repo, {"preregistration/FREEZE.sha256": "x\n"}, "freeze", "2026-01-01T00:00:00+00:00")
    freeze(repo, "2026-01-01T00:00:00+00:00")
    md, flags = ao.build_report(repo)
    assert any("U predictions" in f and "at/before" in f for f in flags), md
    assert ao.main(["--root", str(repo)]) == 1


def test_flags_when_tag_missing(tmp_path):
    repo = init(tmp_path)
    commit(repo, {"results/ledger/u_predictions.tsv": "g\n"}, "preds", "2026-01-01T00:00:00+00:00")
    md, flags = ao.build_report(repo)
    assert any("tag preregistration-v1 does not exist" in f for f in flags), md


def test_flags_old_mtime(tmp_path):
    repo = init(tmp_path)
    commit(repo, {"preregistration/FREEZE.sha256": "x\n"}, "freeze", "2026-03-01T00:00:00+00:00")
    freeze(repo, "2026-03-01T00:00:00+00:00")
    commit(repo, {"results/holdout/x_metrics.tsv": "m\n"}, "metrics", "2026-04-01T00:00:00+00:00")
    old = time.mktime((2026, 1, 15, 0, 0, 0, 0, 0, -1))
    os.utime(repo / "results/holdout/x_metrics.tsv", (old, old))
    md, flags = ao.build_report(repo)
    assert any("mtime before" in f for f in flags), md


def test_flags_later_milestone_dirs_before_tag(tmp_path):
    """results/holdout_eval/, results/m7/, results/revision/ and results/ledger/ are pairwise-derived (M9 extension)."""
    for d in ("results/holdout_eval/core.md", "results/m7/s20.tsv", "results/revision/a3.tsv", "results/ledger/top40.tsv"):
        sub = tmp_path / d.split("/")[1]
        sub.mkdir()
        repo = init(sub)
        commit(repo, {d: "x\n"}, "early", "2025-12-01T00:00:00+00:00")
        commit(repo, {"preregistration/FREEZE.sha256": "x\n"}, "freeze", "2026-01-01T00:00:00+00:00")
        freeze(repo, "2026-01-01T00:00:00+00:00")
        md, flags = ao.build_report(repo)
        assert any("at/before" in f for f in flags), (d, md)
