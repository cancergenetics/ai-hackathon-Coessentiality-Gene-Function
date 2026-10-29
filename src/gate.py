"""gate.py -- pre-registration hash gate (DESIGN.md v2 §1.6, §9).

Every script that reads DepMap *pairwise* information (tool matrices, neighbour lists, baselines, split-half runs)
must call ``gate.check()`` first. The gate refuses (raises ``GateError``) unless ALL of the following hold:

1. ``preregistration/FREEZE.sha256`` exists and lists >= 1 file, one per line in ``sha256sum`` format
   (``<64 hex>  <path relative to the repository root>``; ``#`` comment lines and blank lines ignored; a ``*``
   binary-mode marker before the path is accepted).
2. Every listed file exists in the working tree and its SHA-256 equals the listed hash.
3. The git tag ``preregistration-v1`` exists and resolves to a commit.
4. That commit contains every listed file with exactly the listed content (hash of ``git show <tag>:<path>``),
   and contains ``FREEZE.sha256`` itself with content identical to the working-tree copy (so the hash list cannot
   be edited after tagging).

Optional extra checks (off unless arguments are given): the tool clone is at a given commit, and raw data files
match ``config/data_checksums.tsv`` (``<sha256>  <path>`` lines).

The gate never modifies anything. It returns a small dict (tag commit, number of files, hashes) that callers write
into their run manifest.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE_FILE = "preregistration/FREEZE.sha256"
TAG = "preregistration-v1"
_LINE = re.compile(r"^([0-9a-fA-F]{64}) [ *](.+)$")


class GateError(RuntimeError):
    """Raised when the pre-registration gate is not satisfied."""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_freeze(text: str, label: str = FREEZE_FILE) -> dict[str, str]:
    """{relative path: lower-case sha256} from sha256sum-format text. Raises GateError on malformed lines,
    absolute paths, '..' components or duplicate paths."""
    out: dict[str, str] = {}
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = _LINE.match(s)
        if not m:
            raise GateError(f"{label}:{n}: malformed line {line!r}")
        h, p = m.group(1).lower(), m.group(2).strip()
        if os.path.isabs(p) or ".." in Path(p).parts:
            raise GateError(f"{label}:{n}: path must be relative and inside the repository: {p!r}")
        if p in out:
            raise GateError(f"{label}:{n}: duplicate path {p!r}")
        out[p] = h
    if not out:
        raise GateError(f"{label} lists no files")
    return out


def _git(root: Path, *args: str, binary: bool = False):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode().strip()


def check(root=ROOT, freeze_file: str = FREEZE_FILE, tag: str = TAG, tool_dir=None, tool_commit: str | None = None,
          data_files=None, checksums_file: str = "config/data_checksums.tsv") -> dict:
    """Verify the pre-registration gate (see module docstring). Returns a summary dict; raises GateError.

    tool_dir / tool_commit: if both given, ``git -C tool_dir rev-parse HEAD`` must start with tool_commit.
    data_files: optional iterable of repository-relative paths whose SHA-256 must equal the entry in checksums_file.
    """
    root = Path(root).resolve()
    fpath = root / freeze_file
    if not fpath.is_file():
        raise GateError(f"pre-registration not frozen: {fpath} does not exist")
    freeze_bytes = fpath.read_bytes()
    listed = parse_freeze(freeze_bytes.decode())

    # 2. working tree
    for p, h in listed.items():
        f = root / p
        if not f.is_file():
            raise GateError(f"listed file missing from working tree: {p}")
        got = sha256_file(f)
        if got != h:
            raise GateError(f"hash mismatch (working tree) for {p}: listed {h[:12]}.., found {got[:12]}..")

    # 3. tag
    if _git(root, "rev-parse", "--is-inside-work-tree") != "true":
        raise GateError(f"{root} is not a git working tree")
    commit = _git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}")
    if not commit:
        raise GateError(f"git tag {tag!r} does not exist (or does not point to a commit)")

    # 4. tag content
    for p, h in [(freeze_file, sha256_bytes(freeze_bytes)), *listed.items()]:
        blob = _git(root, "show", f"{commit}:{p}", binary=True)
        if blob is None:
            raise GateError(f"tag {tag} ({commit[:10]}) does not contain {p}")
        got = sha256_bytes(blob)
        if got != h:
            raise GateError(f"hash mismatch (tag {tag}) for {p}: expected {h[:12]}.., tagged {got[:12]}..")

    out = dict(tag=tag, tag_commit=commit, freeze_file=freeze_file, freeze_sha256=sha256_bytes(freeze_bytes),
               n_files=len(listed), files=listed)

    # optional: tool commit
    if tool_dir is not None and tool_commit:
        head = _git(Path(tool_dir), "rev-parse", "HEAD")
        if not head or not head.startswith(tool_commit):
            raise GateError(f"tool clone {tool_dir} is at {head!r}, expected {tool_commit}")
        out["tool_commit"] = head

    # optional: raw data checksums
    if data_files:
        ref = parse_freeze((root / checksums_file).read_text(), label=checksums_file)
        out["data"] = {}
        for p in data_files:
            if p not in ref:
                raise GateError(f"{p} not listed in {checksums_file}")
            got = sha256_file(root / p)
            if got != ref[p]:
                raise GateError(f"data checksum mismatch for {p}")
            out["data"][p] = got
    return out
