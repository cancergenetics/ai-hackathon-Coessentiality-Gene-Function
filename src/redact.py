"""Gene-name redaction for blinded judging (DESIGN.md v2.3 §6.4: "gene names redacted from L's evidence").

Given the identifiers of one gene (current symbol, previous symbols, aliases, UniProt accessions, protein names,
HGNC approved / previous names), ``Redactor(tokens).redact(text)`` replaces every occurrence with ``GENE_X``.

Matching rules
* Word boundaries are alphanumeric: a match may not be preceded or followed by ``[A-Za-z0-9]``. Paralogues therefore
  survive (``TMEM120A`` is untouched when redacting ``TMEM120B``; ``SLC25A5`` / ``SLC25A51`` do not cross-match).
* Symbol-like tokens (no whitespace): case-insensitive (``C8orf33`` = ``C8ORF33`` = ``c8orf33``); an optional hyphen
  (ASCII or Unicode dash) is allowed at every letter/digit transition (``TMEM-120B``, ``C8-orf-33``), and at the
  token's own separators the separator may be a dash, underscore, space or absent (``HLA-DRB1`` = ``HLA DRB1`` =
  ``HLADRB1`` = ``HLA‐DRB1``).
* Short purely alphabetic tokens (<= 4 letters, e.g. aliases ``SET``, ``CAP``) are matched case-sensitively as given,
  so English words are not redacted. Tokens shorter than 3 alphanumeric characters are not used (reported in
  ``Redactor.skipped``).
* ``CnORFm`` / ``CXorfm`` symbols also redact the spelled-out form "chromosome n open reading frame m".
* UniProt accessions: case-sensitive, with an optional isoform suffix (``Q8NB46-2``).
* Multi-word names (protein names, HGNC names): case-insensitive, any run of whitespace/dashes between words matches
  any other such run ("domain-containing" = "domain containing").
* Longer tokens are tried first, so a full protein name is replaced as one unit.
Known limitation: glued suffixes such as ``Ankrd52fl/fl`` are not matched (alphanumeric boundary); the boundary is what
protects paralogues.
"""
from __future__ import annotations

import re
from typing import Iterable

PLACEHOLDER = "GENE_X"
_DASH = "\\-\u2010\u2011\u2012\u2013\u2014\u2212"
_TRANS = f"[{_DASH}]?"                 # optional dash at a letter/digit transition
_SEP = f"(?:[{_DASH}_ ]?)"             # the token's own separator: dash, underscore, space or nothing
_WS = f"[\\s{_DASH}]+"                 # between words of a multi-word name
_BL, _BR = r"(?<![A-Za-z0-9])", r"(?![A-Za-z0-9])"
_ORF = re.compile(r"^C(\d+|X|Y)orf(\d+)$", re.I)
_ACC = re.compile(r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})$")
GENERIC_NAMES = {"protein", "uncharacterized protein", "putative uncharacterized protein", "uncharacterised protein",
                 "putative protein", "hypothetical protein", "transmembrane protein", "open reading frame"}


def split_list(x) -> list[str]:
    """'A|B' / 'A, B' / NaN -> ['A', 'B'] (HGNC pipe lists; quotes stripped)."""
    if x is None or (isinstance(x, float) and x != x):
        return []
    return [s.strip().strip('"').strip() for s in re.split(r"[|;,]", str(x)) if s.strip().strip('"').strip()]


def parse_uniprot_protein_names(s: str) -> list[str]:
    """UniProt 'Protein names' field -> [recommended name, alternative names...]; EC numbers, 'Cleaved into'/'Includes'
    blocks' brackets are dropped (their parenthesised names are kept), nested parentheses are respected."""
    if not s:
        return []
    s = re.sub(r"\[(Cleaved into|Includes):", " (", str(s)).replace("]", ")")
    out, depth, cur, main = [], 0, [], []
    for ch in s:
        if ch == "(":
            if depth == 0:
                cur = []
            else:
                cur.append(ch)
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)
            if depth == 0:
                out.append("".join(cur).strip())
            else:
                cur.append(ch)
        elif depth == 0:
            main.append(ch)
        else:
            cur.append(ch)
    names = [" ".join("".join(main).split())] + [" ".join(x.split()) for x in out]
    names = [n.rstrip(";").strip() for n in names]
    return [n for n in names if n and not re.match(r"^EC\s", n) and n.lower() not in GENERIC_NAMES]


def _alnum_len(tok: str) -> int:
    return len(re.sub(r"[^A-Za-z0-9]", "", tok))


def symbol_pattern(tok: str) -> str:
    parts = re.findall(r"[A-Za-z]+|[0-9]+|[^A-Za-z0-9]+", tok)
    out, prev_alnum = [], False
    for p in parts:
        if p[0].isalnum():
            if prev_alnum:
                out.append(_TRANS)
            out.append(re.escape(p))
            prev_alnum = True
        else:
            out.append(_SEP)
            prev_alnum = False
    body = "".join(out)
    alpha_only = tok.isalpha()
    if alpha_only and len(tok) <= 4:
        return f"{_BL}{re.escape(tok)}{_BR}"
    return f"{_BL}(?i:{body}){_BR}"


def phrase_pattern(name: str) -> str:
    words = [w for w in re.split(f"[\\s{_DASH}]+", name) if w]
    return f"{_BL}(?i:{_WS.join(re.escape(w) for w in words)}){_BR}"


def accession_pattern(acc: str) -> str:
    return f"{_BL}{re.escape(acc)}(?:-\\d+)?{_BR}"


class Redactor:
    """Compile once per gene; ``redact(text)`` returns the redacted text."""

    def __init__(self, symbols: Iterable[str] = (), accessions: Iterable[str] = (), names: Iterable[str] = (),
                 placeholder: str = PLACEHOLDER):
        self.placeholder = placeholder
        self.skipped: list[str] = []
        pats: dict[str, tuple[int, str]] = {}
        for s in symbols:
            s = str(s).strip()
            if not s:
                continue
            if _alnum_len(s) < 3:
                self.skipped.append(s)
                continue
            if re.search(r"\s", s):
                pats.setdefault(phrase_pattern(s), (len(s), s))
            else:
                pats.setdefault(symbol_pattern(s), (len(s), s))
            m = _ORF.match(s)
            if m:
                ph = f"chromosome {m.group(1)} open reading frame {m.group(2)}"
                pats.setdefault(phrase_pattern(ph), (len(ph), ph))
        for a in accessions:
            a = str(a).strip()
            if a:
                pats.setdefault(accession_pattern(a), (len(a), a))
        for n in names:
            n = " ".join(str(n).split())
            if not n or n.lower() in GENERIC_NAMES:
                continue
            if _alnum_len(n) < 3:
                self.skipped.append(n)
                continue
            p = phrase_pattern(n) if re.search(r"\s", n) else symbol_pattern(n)
            pats.setdefault(p, (len(n), n))
        order = sorted(pats.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
        self.tokens = [v[1] for _, v in order]
        self._re = re.compile("|".join(f"(?:{p})" for p, _ in order)) if order else None

    def redact(self, text: str) -> str:
        if self._re is None or not text:
            return text
        return self._re.sub(self.placeholder, text)

    def hits(self, text: str) -> list[str]:
        return [] if self._re is None or not text else [m.group(0) for m in self._re.finditer(text)]


def gene_redactor(symbol: str, prev_symbols=(), alias_symbols=(), uniprot_ids=(), protein_names=(),
                  hgnc_names=(), placeholder: str = PLACEHOLDER) -> Redactor:
    """Convenience constructor from HGNC hub / UniProt fields (lists or pipe-separated strings)."""
    def lst(x):
        return split_list(x) if isinstance(x, (str, float)) or x is None else [str(y) for y in x]
    syms = [symbol, *lst(prev_symbols), *lst(alias_symbols)]
    names = []
    for p in (protein_names if not isinstance(protein_names, str) else [protein_names]):
        names += parse_uniprot_protein_names(p)
    names += [n for n in (lst(hgnc_names) if not isinstance(hgnc_names, str) else [hgnc_names]) if n]
    return Redactor(symbols=syms, accessions=lst(uniprot_ids), names=names, placeholder=placeholder)
