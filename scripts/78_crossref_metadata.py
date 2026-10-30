"""Fetch Crossref metadata for reference keys. Usage: key<TAB>doi lines on stdin -> key + author/year/title/journal/vol/issue/page/doi on stdout.
Produced references/old_meta.tsv and references/new_meta.tsv (input: DOIs from references/literature_refs.tsv)."""
import json, sys, re, html, urllib.request, urllib.parse, time
def get(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "manuscript-ref-check (mailto:none@example.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["message"]
    except Exception as e:
        return {"error": str(e)}
def clean(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    return html.unescape(re.sub(r"\s+", " ", t)).strip()
def fmt(m):
    if "error" in m: return "ERROR " + m["error"]
    au = m.get("author", [])
    names = []
    for a in au:
        if "family" in a:
            ini = "".join(p[0] for p in a.get("given","").replace("-"," ").replace(".", " ").split() if p)
            names.append(f"{a['family']} {ini}".strip())
        elif "name" in a: names.append(a["name"])
    yr = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
    return "\t".join([";".join(names), str(yr), clean((m.get("title") or [""])[0]), clean((m.get("container-title") or [""])[0]), m.get("volume",""), m.get("issue",""), m.get("page", m.get("article-number","")), m.get("DOI","")])
for line in sys.stdin:
    k, d = line.split()
    print(k + "\t" + fmt(get(d)), flush=True)
    time.sleep(0.2)
