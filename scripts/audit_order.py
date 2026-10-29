#!/usr/bin/env python
"""audit_order.py -- chronology audit for the pre-registration gate (DESIGN.md v2.2 §1.6, §9).

Run by a fresh agent at M4, M6 and M9. Prints a markdown report to stdout and exits 1 if anything is flagged.

Reports
  * commit and tag-object times of the tags ``preregistration-v1`` and ``design-frozen`` (and whether they point to the
    same commit);
  * for each "pairwise-derived" path group (results/u_predictions*, results/ledger/, results/holdout/*metrics*, matrix
    manifests, plus other pairwise result dirs): the first commit touching it, its time, and whether it is the tag commit
    or an ancestor of it (i.e. committed before/with the tag). FLAG if so, or if the tag does not exist yet;
  * mtimes of files under results/ (working tree, tracked or not) against the tag time: pairwise-derived files whose mtime
    predates the tag are FLAGGED; the count of other files older than the tag is informational (annotation-only
    outputs legitimately predate it). mtimes are advisory: a git checkout/copy resets them.

Usage: python audit_order.py [--root REPO] [--tags preregistration-v1,design-frozen]
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
TAGS = ("preregistration-v1", "design-frozen")
PRIMARY_TAG = "preregistration-v1"
# path groups that only exist once DepMap pairwise quantities have been computed
GROUPS = {
    "U predictions": ["results/u_predictions*"],
    "prediction ledger": ["results/ledger/"],
    "hold-out metrics": ["results/holdout/*metrics*"],
    "matrices manifests": ["results/matrices/*manifest*", "results/matrices*manifest*"],
    "other pairwise outputs": ["results/calibration/", "results/loo/", "results/assessability/", "results/orthogonal/",
                               "results/matrices/", "results/neighbours/", "results/splithalf/"],
}


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def parse_t(s):
    return datetime.fromisoformat(s).astimezone(timezone.utc) if s else None


def fmt(t):
    return t.strftime("%Y-%m-%d %H:%M:%SZ") if t else "—"


def tag_info(root, tag):
    commit = git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}")
    if not commit:
        return None
    ctime = parse_t(git(root, "log", "-1", "--format=%cI", commit))
    ref = git(root, "for-each-ref", "--format=%(creatordate:iso-strict)", f"refs/tags/{tag}")
    return dict(commit=commit, commit_time=ctime, tag_time=parse_t(ref) if ref else None)


def first_commit(root, specs):
    """Earliest commit (by history order, --reverse) touching any pathspec -> (sha, time, subject) or None."""
    out = git(root, "log", "--reverse", "--format=%H%x09%cI%x09%s", "--", *specs)
    if not out:
        return None
    sha, t, subj = out.splitlines()[0].split("\t", 2)
    return sha, parse_t(t), subj


def is_ancestor(root, a, b):
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=root).returncode == 0


def matches_group(rel, specs):
    for s in specs:
        if s.endswith("/"):
            if rel.startswith(s):
                return True
        elif fnmatch.fnmatch(rel, s):
            return True
    return False


def build_report(root=DEFAULT_ROOT, tags=TAGS):
    root = Path(root).resolve()
    flags: list[str] = []
    L = ["# Chronology audit", "", f"Repository: `{root}`  ", f"Generated: {fmt(datetime.now(timezone.utc))}", ""]
    if git(root, "rev-parse", "--is-inside-work-tree") != "true":
        return "\n".join(L + ["**FLAG: not a git working tree**"]), ["not a git working tree"]

    # ---- tags
    L += ["## Tags", "", "| tag | commit | commit time (UTC) | tag-object time (UTC) |", "|---|---|---|---|"]
    info = {}
    for t in tags:
        i = tag_info(root, t)
        info[t] = i
        if i:
            L.append(f"| {t} | `{i['commit'][:10]}` | {fmt(i['commit_time'])} | {fmt(i['tag_time'])} |")
        else:
            L.append(f"| {t} | **missing** | — | — |")
    if info.get(PRIMARY_TAG) and info.get("design-frozen"):
        same = info[PRIMARY_TAG]["commit"] == info["design-frozen"]["commit"]
        L += ["", f"`{PRIMARY_TAG}` and `design-frozen` point to {'the same commit' if same else 'DIFFERENT commits'}."]
        if not same:
            flags.append("preregistration-v1 and design-frozen point to different commits (DESIGN §1.6: same freeze commit)")
    ptag = info.get(PRIMARY_TAG)
    if not ptag:
        L += ["", f"Tag `{PRIMARY_TAG}` does not exist yet: any pairwise-derived output below is premature."]

    # ---- first commits
    L += ["", "## First commit touching pairwise-derived outputs", "",
          "| group | first commit | commit time (UTC) | subject | vs tag |", "|---|---|---|---|---|"]
    for name, specs in GROUPS.items():
        fc = first_commit(root, specs)
        if fc is None:
            L.append(f"| {name} | none | — | — | no commits |")
            continue
        sha, t, subj = fc
        if not ptag:
            verdict = "**FLAG: committed, tag absent**"
            flags.append(f"{name}: committed in {sha[:10]} but tag {PRIMARY_TAG} does not exist")
        elif sha == ptag["commit"] or is_ancestor(root, sha, ptag["commit"]):
            verdict = "**FLAG: at or before tag**"
            flags.append(f"{name}: first commit {sha[:10]} ({fmt(t)}) is at/before {PRIMARY_TAG} ({ptag['commit'][:10]})")
        else:
            verdict = "after tag (ok)"
            if t < ptag["commit_time"]:
                verdict += " — note: commit timestamp earlier than tag commit's (clock/rebase?)"
                flags.append(f"{name}: commit {sha[:10]} is after the tag in history but has an earlier timestamp")
        L.append(f"| {name} | `{sha[:10]}` | {fmt(t)} | {subj[:60]} | {verdict} |")

    # ---- any pairwise-derived file inside the tag tree
    if ptag:
        names = git(root, "ls-tree", "-r", "--name-only", ptag["commit"]) or ""
        inside = [n for n in names.splitlines() if any(matches_group(n, s) for s in GROUPS.values())]
        L += ["", f"Pairwise-derived paths inside the `{PRIMARY_TAG}` tree: {len(inside)}"]
        for n in inside[:20]:
            L.append(f"- `{n}`")
        if inside:
            flags.append(f"{len(inside)} pairwise-derived path(s) inside the {PRIMARY_TAG} tree")

    # ---- mtimes
    L += ["", "## mtimes under results/ vs tag time", ""]
    res = root / "results"
    if not ptag:
        L.append("Tag absent: nothing to compare. Pairwise-derived files present in results/ (any mtime):")
    ref_time = (ptag["commit_time"] if ptag else None)
    older_other, bad = 0, []
    present = []
    if res.is_dir():
        for p in res.rglob("*"):
            if not p.is_file() or ".git" in p.parts:
                continue
            rel = p.relative_to(root).as_posix()
            mt = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
            pw = any(matches_group(rel, s) for s in GROUPS.values())
            if pw:
                present.append((rel, mt))
                if ref_time and mt < ref_time:
                    bad.append((rel, mt))
            elif ref_time and mt < ref_time:
                older_other += 1
    if ptag:
        L += [f"Reference time: `{PRIMARY_TAG}` commit {fmt(ref_time)}.",
              f"- Non-pairwise result files older than the tag (annotation-only; informational): {older_other}",
              f"- Pairwise-derived files present: {len(present)}; with mtime before the tag: **{len(bad)}**"]
        for rel, mt in bad[:30]:
            L.append(f"  - FLAG `{rel}` mtime {fmt(mt)}")
        if bad:
            flags.append(f"{len(bad)} pairwise-derived file(s) with mtime before {PRIMARY_TAG}")
    else:
        for rel, mt in present[:30]:
            L.append(f"- FLAG `{rel}` mtime {fmt(mt)}")
        if present:
            flags.append(f"{len(present)} pairwise-derived file(s) in results/ but tag {PRIMARY_TAG} absent")
        else:
            L.append("- none")
    L += ["", "(mtimes are advisory; a checkout or copy resets them.)", "", "## Result", ""]
    L += [f"**FLAGS ({len(flags)}):**"] + [f"- {f}" for f in flags] if flags else ["No ordering violations found."]
    return "\n".join(L) + "\n", flags


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--tags", default=",".join(TAGS))
    a = ap.parse_args(argv)
    md, flags = build_report(a.root, tuple(a.tags.split(",")))
    sys.stdout.write(md)
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
