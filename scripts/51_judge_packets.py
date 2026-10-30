#!/usr/bin/env python
"""51_judge_packets.py -- build blinded judge packets for M7 (DESIGN.md §6.4).

Inputs : results/m7/statements.tsv, results/m7/answer_key.tsv (set membership), results/m7/L/HGNC_*.md,
         results/m7/gene_packets/*.txt, results/ids/hgnc_hub.tsv, data/raw/uniprot/uniprot_human_reviewed.tsv,
         data/raw/hgnc/hgnc_complete_set.txt (approved/previous/alias names, added to the redaction list).
Outputs: results/m7/judge/packets/J###.md, packet_key.tsv (ONLY place with the J -> gene map), batches/*.txt,
         leak_check.tsv.   J numbering = random.Random(0).shuffle over genes sorted by hgnc number.
Run: ./.env/bin/python -I scripts/51_judge_packets.py
"""
import csv
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import redact as RD  # noqa: E402

M7 = ROOT / "results/m7"
OUT = M7 / "judge"
HEADER = ("You are judging whether published literature supports four candidate statements about an anonymised human "
          "gene (GENE_X). Use ONLY the evidence listed below — do not use your own background knowledge and do not "
          "search. For each statement A–D, score +1 if the evidence directly supports the statement (the gene is "
          "reported to function in the stated process or module, or a closely equivalent one), −1 if the evidence "
          "contradicts it (the gene is shown to function in an incompatible process/compartment), and 0 if the "
          "evidence does not address it. Evidence flagged DepMap-derived = yes must be ignored (treat as absent). "
          "Give one line of justification per statement citing the evidence row(s). Output a 4-row table: "
          "slot | score | justification.")


def tsv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def hnum(h):
    return int(h.split(":")[1])


SEPS = "[\\-_\\s.\u2010\u2011\u2012\u2013\u2014\u2212]?"


def extra_symbol_patterns(symbols):
    """Looser symbol patterns than src/redact.py (which allows only a dash at letter/digit transitions and has no
    '.' separator): optional dash/underscore/space/dot at every letter/digit transition and at '.', e.g. 'ELP 6',
    'p40.5', 'p40 5'. Short purely alphabetic tokens (<=4) are skipped (kept case-sensitive in redact.py)."""
    out = []
    for t in symbols:
        al = re.sub(r"[^A-Za-z0-9]", "", t)
        if len(al) < 3 or re.search(r"\s", t) or (al.isalpha() and len(al) <= 4):
            continue
        parts = re.findall(r"[A-Za-z]+|[0-9]+|[^A-Za-z0-9]+", t)
        pat, prev = [], False
        for q in parts:
            if q[0].isalnum():
                pat.append((SEPS if prev else "") + re.escape(q))
                prev = True
            else:
                pat.append(SEPS)
                prev = False
        out.append(re.compile(r"(?<![A-Za-z0-9])(?i:" + "".join(pat) + r")(?![A-Za-z0-9])"))
    return out


def main():
    stm = tsv(M7 / "statements.tsv")
    key = {r["hgnc_id"]: r["set"].lower() for r in tsv(M7 / "answer_key.tsv")}
    hub = {r["hgnc_id"]: r for r in tsv(ROOT / "results/ids/hgnc_hub.tsv")}
    hg = {r["hgnc_id"]: r for r in tsv(ROOT / "data/raw/hgnc/hgnc_complete_set.txt")}
    up = {r["Entry"]: r for r in tsv(ROOT / "data/raw/uniprot/uniprot_human_reviewed.tsv")}
    genes = sorted({r["hgnc_id"] for r in stm}, key=hnum)
    assert len(genes) == 100 and set(genes) == set(key)
    order = genes[:]
    random.Random(0).shuffle(order)
    jid = {g: f"J{i + 1:03d}" for i, g in enumerate(order)}

    (OUT / "packets").mkdir(parents=True, exist_ok=True)
    (OUT / "batches").mkdir(parents=True, exist_ok=True)
    idents = {}
    leaks = []
    for g in genes:
        h = hub[g]
        packet_txt = (M7 / "gene_packets" / f"{g.replace(':', '_')}.txt").read_text()
        pk = dict(l.split(": ", 1) for l in packet_txt.splitlines() if ": " in l)
        accs = sorted({a for a in re.split(r"[|;, ]+", (h["uniprot_ids"] + "|" + pk.get("uniprot_accessions", "")))
                       if a})
        prevs = RD.split_list(h["prev_symbols"]) + RD.split_list(pk.get("previous_symbols", ""))
        aliases = RD.split_list(h["alias_symbols"]) + RD.split_list(pk.get("alias_symbols", ""))
        syms = list(dict.fromkeys([h["symbol"], *prevs, *aliases]))
        pnames = []
        for a in accs:
            if a in up:
                pnames += RD.parse_uniprot_protein_names(up[a]["Protein names"])
        hr = hg.get(g, {})
        hnames = [hr.get("name", "")] + RD.split_list(hr.get("prev_name", "")) + RD.split_list(hr.get("alias_name", ""))
        hnames = [n for n in hnames if n]
        pnames = list(dict.fromkeys(pnames + hnames))
        red0 = RD.Redactor(symbols=syms, accessions=accs, names=pnames)
        extra = extra_symbol_patterns(syms)

        class _R:      # src/redact.py first, then the looser symbol variants (space/dot between letter/digit)
            @staticmethod
            def redact(t, r=red0, e=extra):
                t = r.redact(t)
                for x in e:
                    t = x.sub(RD.PLACEHOLDER, t)
                return t
        red = _R()
        idents[g] = (syms, accs, pnames)

        L = (M7 / "L" / f"{g.replace(':', '_')}.md").read_text()
        lines = L.splitlines()
        ti = next(i for i, l in enumerate(lines) if l.startswith("| "))
        j = ti
        while j < len(lines) and lines[j].startswith("|"):
            j += 1
        tail = [l for l in lines[j:] if l.strip()]
        assert len(tail) == 1, g
        cells = [[c.strip() for c in r.strip().strip("|").split(" | ")] for r in lines[ti + 2:j]]
        assert all(len(c) in (6, 7) for c in cells), g
        cells = [c[-6:] for c in cells]          # drop the optional '#' column; renumbered below
        hdr = "| # | claim | source | year | verbatim supporting sentence | evidence level | DepMap-derived |"
        rows = [hdr, "|---|---|---|---|---|---|---|"] + [f"| {n} | " + " | ".join(c) + " |"
                                                       for n, c in enumerate(cells, 1)]
        table = "\n".join(red.redact(r) for r in rows)
        summary = "**Summary.** " + red.redact(re.sub(r"^\*\*Summary\.\*\*\s*", "", tail[0]))
        sts = sorted([r for r in stm if r["hgnc_id"] == g], key=lambda r: r["slot"])
        assert [s["slot"] for s in sts] == list("ABCD")
        stext = "\n".join(f"- **{s['slot']}**: {red.redact(s['statement'])}" for s in sts)
        md = (f"# Packet {jid[g]}\n\n## Instructions\n\n{HEADER}\n\n## Literature evidence about GENE_X\n\n{table}\n\n"
              f"{summary}\n\n## Candidate statements\n\n{stext}\n")
        (OUT / "packets" / f"{jid[g]}.md").write_text(md)

    with open(OUT / "packet_key.tsv", "w") as f:
        f.write("J_id\thgnc_id\tset\n")
        for g in sorted(genes, key=lambda x: jid[x]):
            f.write(f"{jid[g]}\t{g}\t{key[g]}\n")

    ids = sorted(jid.values())
    hv = [j for g, j in jid.items() if key[g] == "hval10"]
    hv = sorted(hv)
    rest = [j for j in ids if j not in set(hv)]
    assert len(hv) == 10 and len(rest) == 90
    (OUT / "batches/hval_batch.txt").write_text("\n".join(hv) + "\n")
    for i in range(3):
        (OUT / f"batches/main_batch{i + 1}.txt").write_text("\n".join(rest[30 * i:30 * i + 30]) + "\n")

    # ---- independent leak check (superset regex: optional [-_ ‐-−] between EVERY character) ----
    D = "[\\-_\\s‐‑‒–—−]?"
    allsyms = {r["symbol"] for r in hub.values() if len(r["symbol"]) >= 3}
    nleak = 0
    other = []
    with open(OUT / "leak_check.tsv", "w") as lf:
        lf.write("J_id\tkind\ttoken\tcontext\n")
        for g in genes:
            txt = (OUT / "packets" / f"{jid[g]}.md").read_text()
            body = txt.split("## Literature evidence", 1)[1]
            syms, accs, pnames = idents[g]
            for tok in [*syms, *accs, *pnames]:
                alnum = re.sub(r"[^A-Za-z0-9]", "", tok)
                if len(alnum) < 3:
                    continue
                words = [w for w in re.split(r"[\s\-‐-−_]+", tok) if w]
                pat = "[\\-_\\s‐‑‒–—−]+".join(
                    D.join(re.escape(c) for c in w) for w in words)
                flags = 0 if (alnum.isalpha() and len(alnum) <= 4) or tok in accs else re.I
                for m in re.finditer(f"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])", body, flags):
                    nleak += 1
                    c = body[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
                    lf.write(f"{jid[g]}\tIDENT\t{tok}\t{c}\n")
            for pat_s in (hub[g]["hgnc_id"], hub[g]["symbol"]):
                pass
            if re.search(r"HGNC:\d+|p_cal|top40|extra30|hval10|s20", txt, re.I):
                nleak += 1
                lf.write(f"{jid[g]}\tMETA\t-\tbookkeeping string present\n")
            st = body.split("## Candidate statements", 1)[1]
            for w in set(re.findall(r"[A-Za-z0-9\-]{3,}", st)):
                if w in allsyms and w != hub[g]["symbol"]:
                    other.append((jid[g], w))
    print("packets", len(ids), "hval", len(hv), "leaks", nleak, "other-symbol-in-statements", len(other), other)
    print("skipped(<3 alnum) tokens:", {g: RD.Redactor(symbols=idents[g][0]).skipped for g in genes
                                       if RD.Redactor(symbols=idents[g][0]).skipped})


if __name__ == "__main__":
    main()
