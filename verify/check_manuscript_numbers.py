#!/usr/bin/env python3
"""Number verifier for manuscript/manuscript.md.

Step 1 (extraction): split the manuscript into sentences and table cells, find every
number, and attach it to the `<!-- src: path -->` tag that follows it in the same
sentence (or, for table cells, to the cell's own tag or the table's trailing comment).
Numbers with no tag are listed separately.

Step 2 (screening): open each cited source file and look for the value, allowing the
rounding implied by the manuscript's own precision (and %/fraction and a x 10^-n
rewrites). A screening hit only shows that the value occurs somewhere in the file; the
semantic check (is it the *right* quantity) is a human/agent judgement and is recorded
in reviews/ms_round1_numbers.md.

Usage:  python3 verify/check_manuscript_numbers.py [--out units.tsv] [--json out.json]
Read-only with respect to the repository.
"""
import argparse, glob, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MS = ROOT / "manuscript" / "manuscript.md"

TAG_RE = re.compile(r"<!--\s*src:\s*(.*?)\s*-->", re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
SUP = str.maketrans("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789")

WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
WORD_RE = re.compile(
    r"\b(?:(twenty|thirty|forty|fifty)-(one|two|three|four|five|six|seven|eight|nine)|"
    r"(twenty|thirty|forty|fifty)|(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen))\b", re.I)

# numeric token: optional sign, digits with thousands commas, decimals, optional x 10^n
NUM_RE = re.compile(
    r"(?<![A-Za-z0-9_.\-/#])(?P<sign>[−\-+])?(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?:\s*×\s*10(?P<exp>[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+))?(?P<pct>%)?(?![A-Za-z0-9_])")
SKIP_CONTEXT = [
    re.compile(r"\[\d+(?:[–,\-]\d+)*(?:,\s*\d+)*\]"),                 # citations
    re.compile(r"\b(?:Fig|Figs|Table|Tables|S\d+ Fig|S\d+ Table|S\d+ Text|S\d+ Data)\s*\d+[A-Z]?(?:\s*and\s*\d+[A-Z])?"),
    re.compile(r"\bS\d+(?:[–-]S?\d+)?\s+(?:Fig|Table|Reports?|Text|Data)\b"),
    re.compile(r"\bS\d+\b"),                                          # S20
    re.compile(r"\(\s*[A-D]\s*\)"),
    re.compile(r"\d{4}-\d{2}-\d{2}"),                                 # dates
    re.compile(r"\bv\d+(?:\.\d+)*\b"),
    re.compile(r"\b[Vv]\d+[′']?\b"), re.compile(r"\b[CRDN]\d\b"),    # C1, R1, D1, N1, V1
    re.compile(r"\bTier [AB]\b"),
    re.compile(r"\bQ\d\b"),
]


def git_tracked():
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout
        return set(out.split("\n"))
    except Exception:
        return None


def parse_paths(tag_text):
    """Pull file paths out of a src tag; bare names inherit the previous path's directory."""
    # strip parenthetical annotations
    t = re.sub(r"\([^()]*\)", " ", tag_text)
    toks = re.findall(r"[\w./*\-]+\.(?:md|tsv|json|yaml|yml|txt|py|sh|csv)\b|[\w./*\-]*\*[\w./*\-]*", t)
    out, last_dir = [], ""
    for tk in toks:
        if "/" not in tk and last_dir:
            tk = last_dir + tk
        elif "/" in tk:
            last_dir = tk.rsplit("/", 1)[0] + "/"
        out.append(tk)
    return out


def resolve(path):
    p = ROOT / path
    if "*" in path:
        return sorted(glob.glob(str(p)))
    return [str(p)] if p.exists() else []


_file_nums = {}


def file_numbers(fp):
    if fp in _file_nums:
        return _file_nums[fp]
    try:
        txt = Path(fp).read_text(errors="replace")
    except Exception:
        txt = ""
    vals = []
    for m in re.finditer(r"(?<![A-Za-z0-9_])(-?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?)(?![A-Za-z_])", txt):
        s = m.group(1).replace(",", "")
        try:
            vals.append(float(s))
        except ValueError:
            pass
    # also pick up numbers glued to letters in tables, e.g. "0.141," handled; unicode minus
    for m in re.finditer(r"−(\d+\.?\d*)", txt):
        vals.append(-float(m.group(1)))
    _file_nums[fp] = vals
    return vals


def value_of(m):
    s = m.group("num").replace(",", "")
    v = float(s)
    dec = len(s.split(".")[1]) if "." in s else 0
    if m.group("exp"):
        v *= 10 ** int(m.group("exp").translate(SUP))
        dec = 12  # compare in relative terms
        return v, dec, True
    if m.group("sign") in ("−", "-"):
        v = -v
    return v, dec, False


def screen(v, dec, sci, pct, vals, signed_ok=True):
    """True if some file number is consistent with the manuscript value v (given precision)."""
    cands = [v]
    if pct:
        cands.append(v / 100.0)
    for f in vals:
        for c, scale in [(c, 1.0) for c in cands] + ([(v, 100.0)] if pct else []):
            pass
    for f in vals:
        if sci:
            if v != 0 and abs(f - v) / abs(v) < 0.06:   # 2 s.f. rounding
                return True
            continue
        if dec == 0:
            if abs(f - v) < 1e-9 or (pct and abs(f * 100 - v) < 0.5 and f <= 1.0 and abs(f * 100 - v) < 0.5):
                return True
            if abs(abs(f) - abs(v)) < 1e-9:
                return True
        else:
            tol = 0.5 * 10 ** (-dec) + 1e-9
            if abs(f - v) <= tol or abs(abs(f) - abs(v)) <= tol:
                return True
            if pct and abs(f * 100 - v) <= tol:
                return True
            if pct and abs(f - v / 100) <= tol / 100:
                return True
    return False


def find_numbers(text):
    """Return list of (token, value, dec, sci, pct, span) in text after masking skip contexts."""
    masked = text
    for rx in SKIP_CONTEXT:
        masked = rx.sub(lambda m: " " * len(m.group(0)), masked)
    # mask gene-like tokens (letters adjacent to digits) already excluded by lookarounds
    res = []
    for m in NUM_RE.finditer(masked):
        v, dec, sci = value_of(m)
        tok = text[m.start():m.end()]
        is_year = (not sci) and dec == 0 and 1990 <= abs(v) <= 2035 and "," not in m.group("num")
        res.append(dict(tok=tok.strip(), v=v, dec=dec, sci=sci, pct=bool(m.group("pct")),
                        year=is_year, pos=m.start(), word=False))
    for m in WORD_RE.finditer(masked):
        if m.group(1):
            v = TENS[m.group(1).lower()] + WORDS[m.group(2).lower()]
        elif m.group(3):
            v = TENS[m.group(3).lower()]
        else:
            v = WORDS[m.group(4).lower()]
        res.append(dict(tok=m.group(0), v=float(v), dec=0, sci=False, pct=False, year=False,
                        pos=m.start(), word=True))
    return sorted(res, key=lambda r: r["pos"])


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[*\"“_])|(?<=:)\s+(?=\*\*)")


def section_of(headings):
    return " > ".join(h for h in headings if h)


def parse_manuscript():
    lines = MS.read_text().split("\n")
    units = []          # dict(line, section, kind, text, tags(list of tag text), nums)
    headings = ["", ""]
    i, n = 0, len(lines)
    # skip YAML header and leading comment
    in_refs = False
    while i < n:
        ln = lines[i]
        if ln.startswith("# "):
            headings = [ln[2:].strip(), ""]
            in_refs = ln.strip() in ("# References",)
            i += 1; continue
        if ln.startswith("## "):
            headings[1] = ln[3:].strip(); i += 1; continue
        if in_refs or not ln.strip() or ln.startswith("---") or ln.startswith("title:") or ln.startswith("!["):
            i += 1; continue
        if ln.lstrip().startswith("<!--") and "-->" not in ln:
            # multi-line comment block (header or table footnote) - skip
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1; continue
        if ln.lstrip().startswith("<!--") and ln.strip().endswith("-->"):
            i += 1; continue
        if ln.startswith("|"):
            # table block
            start = i
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append((i + 1, lines[i])); i += 1
            # trailing comment
            j = i
            while j < n and not lines[j].strip():
                j += 1
            trail = []
            if j < n and lines[j].lstrip().startswith("<!--"):
                k = j
                blk = lines[k]
                while "-->" not in lines[k]:
                    k += 1; blk += "\n" + lines[k]
                trail = [t for t in TAG_RE.findall(blk)]
            for ln_no, row in rows[2:]:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                for ci, c in enumerate(cells):
                    units.append(dict(line=ln_no, section=section_of(headings), kind="table-cell",
                                      raw=c, trail=trail, col=ci, rowhead=cells[0][:40]))
            continue
        # paragraph
        blk_lines = []
        start = i + 1
        while i < n and lines[i].strip() and not lines[i].startswith("|") and not lines[i].startswith("#"):
            blk_lines.append(lines[i]); i += 1
        blk = "\n".join(blk_lines)
        if blk.lstrip().startswith("<!--") and blk.rstrip().endswith("-->") and blk.count("<!--") == 1 and "src:" not in blk[:12]:
            continue
        if re.match(r"^\d+\. ", blk):
            continue
        units.append(dict(line=start, section=section_of(headings), kind="para", raw=blk, trail=[]))
    return units


def split_sentences(raw):
    """Split paragraph into sentences, keeping tags inline."""
    raw = re.sub(r"\s*\n\s*", " ", raw)
    # protect tags from splitting: replace '.' inside tags
    prot = TAG_RE.sub(lambda m: m.group(0).replace(".", "․"), raw)
    parts = SENT_SPLIT.split(prot)
    # a sentence-final tag after the period goes with previous sentence: handle by re-attaching
    sents = []
    for p in parts:
        p = p.replace("․", ".")
        if sents and re.match(r"^\s*<!--\s*src:", p):
            sents[-1] += " " + p
        else:
            sents.append(p)
    return sents


def analyse(units, tracked):
    rows = []   # one row per (sentence/cell)
    for u in units:
        if u["kind"] == "para":
            sents = split_sentences(u["raw"])
        else:
            sents = [u["raw"]]
        for s in sents:
            tags = list(TAG_RE.finditer(s))
            plain = COMMENT_RE.sub("", s)
            # segments: text before each tag (since previous tag)
            segs, prev = [], 0
            for m in tags:
                segs.append((s[prev:m.start()], m.group(1)))
                prev = m.end()
            tail = s[prev:]
            tail_nums = find_numbers(COMMENT_RE.sub("", tail))
            if u["kind"] == "table-cell" and not tags and u["trail"]:
                segs = [(s, " ; ".join(u["trail"]))]
                tail_nums = []
            entry = dict(line=u["line"], section=u["section"], kind=u["kind"],
                         text=re.sub(r"\s+", " ", plain).strip(), tagged=[], untagged=[])
            for seg, tag in segs:
                paths = parse_paths(tag)
                files = []
                for p in paths:
                    files += [(p, f) for f in (resolve(p) or [None])]
                for nm in find_numbers(COMMENT_RE.sub("", seg)):
                    res = dict(nm)
                    res["tag"] = tag
                    hits, missing = [], []
                    for p, f in files:
                        if f is None:
                            missing.append(p); continue
                        if screen(nm["v"], nm["dec"], nm["sci"], nm["pct"], file_numbers(f)):
                            hits.append(os.path.relpath(f, ROOT))
                    res["hit_files"] = hits
                    res["missing_files"] = missing
                    res["untracked"] = [p for p, f in files if f and tracked is not None
                                        and os.path.relpath(f, ROOT) not in tracked]
                    res["status"] = "hit" if hits else ("nofile" if (missing and not hits and len(missing) == len(files)) else "miss")
                    entry["tagged"].append(res)
            for nm in tail_nums:
                entry["untagged"].append(nm)
            if entry["tagged"] or entry["untagged"]:
                rows.append(entry)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write per-number TSV here")
    ap.add_argument("--json", help="write full JSON here")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    tracked = git_tracked()
    rows = analyse(parse_manuscript(), tracked)
    ntag = sum(len(r["tagged"]) for r in rows)
    nhit = sum(1 for r in rows for x in r["tagged"] if x["status"] == "hit")
    nmiss = sum(1 for r in rows for x in r["tagged"] if x["status"] == "miss")
    nofile = sum(1 for r in rows for x in r["tagged"] if x["status"] == "nofile")
    nun = sum(1 for r in rows for x in r["untagged"] if not x["year"])
    if a.out:
        with open(a.out, "w") as fh:
            fh.write("line\tsection\tstatus\ttoken\ttag\tsentence\n")
            for r in rows:
                for x in r["tagged"]:
                    fh.write(f"{r['line']}\t{r['section']}\t{x['status']}\t{x['tok']}\t{x['tag']}\t{r['text'][:300]}\n")
                for x in r["untagged"]:
                    if not x["year"]:
                        fh.write(f"{r['line']}\t{r['section']}\tUNTAGGED\t{x['tok']}\t\t{r['text'][:300]}\n")
    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=1, default=str))
    if not a.quiet:
        print(f"sentences/cells with numbers: {len(rows)}")
        print(f"tagged numbers: {ntag}  screening hit: {nhit}  miss (needs manual look): {nmiss}  no resolvable file: {nofile}")
        print(f"untagged numbers (excluding years): {nun}")
        ut = {p for r in rows for x in r['tagged'] for p in x['untracked']}
        if ut:
            print("cited but not git-tracked:", sorted(ut))


if __name__ == "__main__":
    main()
