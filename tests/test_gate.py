"""Toy tests for src/gate.py: the pre-registration hash gate, on throw-away git repositories.

Run: .env/bin/python -I -m pytest -q tests/test_gate.py
"""
import hashlib
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import gate  # noqa: E402


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def make_repo(tmp_path, tag=True, list_files=("preregistration/uncharacterised_genes.tsv",
                                              "preregistration/CRITERIA.md")):
    repo = tmp_path / "repo"
    (repo / "preregistration").mkdir(parents=True)
    files = {"preregistration/uncharacterised_genes.tsv": b"hgnc_id\nHGNC:1\nHGNC:2\n",
             "preregistration/CRITERIA.md": b"# criteria\n|U| = 2\n"}
    for p, b in files.items():
        (repo / p).write_bytes(b)
    lines = [f"{sha(files[p])}  {p}" for p in list_files]
    (repo / gate.FREEZE_FILE).write_text("# frozen\n" + "\n".join(lines) + "\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "freeze")
    if tag:
        git(repo, "tag", "-a", gate.TAG, "-m", "pre-registration")
    return repo


def test_passes_on_valid_freeze(tmp_path):
    repo = make_repo(tmp_path)
    info = gate.check(repo)
    assert info["n_files"] == 2 and len(info["tag_commit"]) == 40


def test_lightweight_tag_ok(tmp_path):
    repo = make_repo(tmp_path, tag=False)
    git(repo, "tag", gate.TAG)
    assert gate.check(repo)["n_files"] == 2


def test_refuses_without_freeze_file(tmp_path):
    repo = tmp_path / "empty"
    repo.mkdir()
    git(repo, "init", "-q")
    with pytest.raises(gate.GateError, match="not frozen"):
        gate.check(repo)


def test_refuses_without_tag(tmp_path):
    repo = make_repo(tmp_path, tag=False)
    with pytest.raises(gate.GateError, match="does not exist"):
        gate.check(repo)


def test_refuses_on_modified_file(tmp_path):
    repo = make_repo(tmp_path)
    with open(repo / "preregistration/uncharacterised_genes.tsv", "ab") as fh:
        fh.write(b"HGNC:3\n")
    with pytest.raises(gate.GateError, match="working tree"):
        gate.check(repo)


def test_refuses_when_listed_file_missing(tmp_path):
    repo = make_repo(tmp_path)
    os.remove(repo / "preregistration/CRITERIA.md")
    with pytest.raises(gate.GateError, match="missing"):
        gate.check(repo)


def test_refuses_when_tag_lacks_file(tmp_path):
    """File listed and hashed correctly in the working tree, but added after the tag."""
    repo = make_repo(tmp_path, list_files=("preregistration/uncharacterised_genes.tsv",))
    extra = b"late addition\n"
    (repo / "preregistration/late.txt").write_bytes(extra)
    with open(repo / gate.FREEZE_FILE, "a") as fh:
        fh.write(f"{sha(extra)}  preregistration/late.txt\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "late")
    with pytest.raises(gate.GateError, match="hash mismatch \\(tag"):
        gate.check(repo)                                # FREEZE.sha256 itself differs from the tagged copy


def test_refuses_when_tag_content_differs(tmp_path):
    """Working tree and FREEZE consistent, but the tagged commit has different content (re-frozen without retag)."""
    repo = make_repo(tmp_path)
    p = "preregistration/CRITERIA.md"
    new = b"# criteria\n|U| = 3\n"
    (repo / p).write_bytes(new)
    txt = (repo / gate.FREEZE_FILE).read_text().splitlines()
    txt = [f"{sha(new)}  {p}" if line.endswith(p) else line for line in txt]
    (repo / gate.FREEZE_FILE).write_text("\n".join(txt) + "\n")
    with pytest.raises(gate.GateError, match="tag"):
        gate.check(repo)


def test_malformed_freeze(tmp_path):
    with pytest.raises(gate.GateError):
        gate.parse_freeze("abc  file\n")
    with pytest.raises(gate.GateError):
        gate.parse_freeze(f"{'0' * 64}  ../outside\n")
    with pytest.raises(gate.GateError, match="no files"):
        gate.parse_freeze("# only a comment\n")
    assert gate.parse_freeze(f"{'A' * 64} *bin.dat\n") == {"bin.dat": "a" * 64}


def test_project_gate_currently_refuses():
    """Pre-registration is not frozen yet in this repository, so the gate must refuse."""
    if os.path.exists(os.path.join(ROOT, gate.FREEZE_FILE)):
        pytest.skip("project already frozen")
    with pytest.raises(gate.GateError):
        gate.check()
