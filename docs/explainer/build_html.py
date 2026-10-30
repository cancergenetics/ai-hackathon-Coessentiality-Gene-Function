"""Build docs/explainer/explainer.html: one self-contained interactive page from the Markdown explainer.

Sources: METHOD.md, JOURNEY.md, INSIGHTS.md, journey_data.json and figures/ (all in docs/explainer/). The page has three
tabs (Method, How we got here, Insights). Markers in the Markdown become interactive widgets:

  <!-- widget:pipeline --> + the image paragraph after it      -> clickable pipeline diagram (figures/pipeline.svg inline)
  <!-- widget:timeline --> + image paragraph (+ caption)       -> timeline drawn from journey_data.json; circles open cards
  <!-- worked:start --> ... <!-- worked:end -->                -> step-by-step worked-example viewer (one h3 per panel)
  <a id="tp-N"></a> + h2 section in JOURNEY.md                -> expandable turning-point card

Links between the three Markdown files become in-page links (switching tab when needed); links to other repository
files become GitHub links. Figures are inlined (base64 PNG, inline SVG), CSS and JS are inline, and the page makes no
network requests. Markdown is rendered with markdown-it-py (already in config/requirements.lock.txt).

Usage (from the project root):
    ./.env/bin/python -I docs/explainer/build_html.py
"""
import base64
import html
import json
import posixpath
import re
from datetime import datetime, timedelta
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
OUT = HERE / "explainer.html"
REPO_URL = "https://github.com/cancergenetics/ai-hackathon-Coessentiality-Gene-Function/blob/main/"
TABS = [("method", "Method", "METHOD.md"), ("journey", "How we got here", "JOURNEY.md"),
        ("insights", "Insights", "INSIGHTS.md")]
FILE_TAB = {f: t for t, _, f in TABS}
GROUP_COLOUR = {"design": "#56B4E9", "evaluation": "#E69F00", "predictions": "#009E73", "writing": "#CC79A7"}
GROUP_LABEL = {"design": "Design and freeze", "evaluation": "Evaluation", "predictions": "Predictions and checks",
               "writing": "Manuscript and review"}

MD = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable("table")


# ------------------------------------------------------------------------------------------------ helpers
def slugify(text: str) -> str:
    t = re.sub(r"<[^>]+>", "", html.unescape(text)).strip().lower()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"[\s_]+", "-", t).strip("-")


def explicit_ids(md_text: str) -> set:
    return set(re.findall(r'<a id="([^"]+)"></a>', md_text))


def add_heading_ids(h: str, tab: str) -> tuple[str, set]:
    seen = set()

    def rep(m):
        level, inner = m.group(1), m.group(2)
        base = f"{tab}-{slugify(inner)}"
        hid, k = base, 1
        while hid in seen:
            k += 1
            hid = f"{base}-{k}"
        seen.add(hid)
        return f'<h{level} id="{hid}">{inner}</h{level}>'
    return re.sub(r"<h([1-6])>(.*?)</h\1>", rep, h, flags=re.S), seen


def fix_links(h: str, tab: str, explicit: set, heading_ids: set) -> str:
    def internal(frag: str, target_tab: str) -> str:
        if frag in explicit:
            return f"#{frag}"
        cand = f"{target_tab}-{frag}"
        if cand in heading_ids:
            return f"#{cand}"
        raise ValueError(f"unresolved anchor #{frag} (tab {target_tab})")

    def rep(m):
        href = html.unescape(m.group(1))
        if href.startswith(("http://", "https://", "mailto:", "data:")):
            return f'href="{html.escape(href)}" target="_blank" rel="noopener"'
        if href.startswith("#"):
            return f'href="{internal(href[1:], tab)}"'
        path, _, frag = href.partition("#")
        if path in FILE_TAB:
            return f'href="{internal(frag, FILE_TAB[path]) if frag else "#tab-" + FILE_TAB[path]}"'
        repo_path = posixpath.normpath(posixpath.join("docs/explainer", path))
        url = REPO_URL + repo_path + (f"#{frag}" if frag else "")
        return f'href="{html.escape(url)}" target="_blank" rel="noopener"'
    return re.sub(r'href="([^"]+)"', rep, h)


def inline_images(h: str) -> str:
    def rep(m):
        src = m.group(1)
        p = HERE / src
        if src.startswith(("http", "data:")) or not p.exists():
            raise ValueError(f"image not found: {src}")
        mime = {"png": "image/png", "svg": "image/svg+xml"}[p.suffix[1:]]
        return f'src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}" loading="lazy"'
    h = re.sub(r'<img src="([^"]+)"', lambda m: "<img " + rep(m), h)
    return h.replace("<img ", '<img class="fig" ')


def wrap_tables(h: str) -> str:
    return re.sub(r"(<table>.*?</table>)", r'<div class="table-wrap">\1</div>', h, flags=re.S)


def hhmm(s: str) -> str:
    d = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    return d.strftime("%d %b %H:%M").lstrip("0")


# ------------------------------------------------------------------------------------------------ widgets
def pipeline_widget(h: str) -> str:
    svg = (HERE / "figures/pipeline.svg").read_text()
    svg = re.sub(r"<\?xml[^>]*>", "", svg)
    svg = re.sub(r'\swidth="560" height="980"', ' class="pipeline-svg"', svg, count=1)
    svg = svg.replace('role="img" aria-labelledby="pl-title pl-desc"', 'role="group" aria-labelledby="pl-title"', 1)

    def stage(m):
        n = m.group(1)
        title = re.search(r"<title>(.*?)</title>", m.group(0)).group(1)
        return (f'<g class="pl-stage" id="pl-stage-{n}" data-step="{n}" tabindex="0" role="link" '
                f'aria-label="{html.escape(title)}. Go to step {n}.">')
    svg = re.sub(r'<g class="pl-stage" id="pl-stage-(\d)" data-step="\d">\s*<title>.*?</title>',
                 lambda m: stage(m) + re.search(r"<title>.*?</title>", m.group(0)).group(0), svg, flags=re.S)
    fig = (f'<figure class="pipeline" id="pipeline-fig">{svg}<figcaption>Click a stage (or focus it and press Enter) '
           'to read that step.</figcaption></figure>')
    new, n = re.subn(r"<!-- widget:pipeline -->\s*<p><img[^>]*></p>", fig, h, flags=re.S)
    assert n == 1, "pipeline marker not found"
    return new


def timeline_svg(data: dict) -> str:
    t0 = datetime.strptime(data["range"][0], "%Y-%m-%dT%H:%M:%SZ")
    t1 = datetime.strptime(data["range"][1], "%Y-%m-%dT%H:%M:%SZ")
    W, X0, X1 = 900, 30, 880
    span = (t1 - t0).total_seconds()

    def x(s):
        d = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
        return X0 + (d - t0).total_seconds() / span * (X1 - X0)

    out = [f'<svg class="timeline-svg" viewBox="0 0 {W} 210" role="group" aria-label="Project timeline, 29 to 30 '
           'October 2026 (UTC), with eight turning points">',
           '<defs><pattern id="tl-hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
           'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="tl-hatchline"/></pattern></defs>']
    BY0, BY1 = 112, 136
    for p in data["phases"]:
        xa, xb = x(p["start"]), x(p["end"])
        out.append(f'<rect x="{xa:.1f}" y="{BY0}" width="{xb - xa:.1f}" height="{BY1 - BY0}" '
                   f'fill="{GROUP_COLOUR[p["group"]]}" class="tl-band"><title>{html.escape(p["label"])} '
                   f'({p["milestones"]}), {hhmm(p["start"])}–{hhmm(p["end"])} UTC</title></rect>')
    for g in data["gaps"]:
        xa, xb = x(g["start"]), x(g["end"])
        out.append(f'<rect x="{xa:.1f}" y="{BY0}" width="{xb - xa:.1f}" height="{BY1 - BY0}" fill="url(#tl-hatch)" '
                   f'class="tl-gap"><title>{html.escape(g["label"])}: {html.escape(g["note"])}</title></rect>')
    # axis ticks every 2 h on even hours
    tick = t0.replace(minute=0, second=0)
    if tick < t0:
        tick += timedelta(hours=1)
    if tick.hour % 2:
        tick += timedelta(hours=1)
    while tick <= t1:
        xs = X0 + (tick - t0).total_seconds() / span * (X1 - X0)
        lab = tick.strftime("%H:%M") + (tick.strftime(" · %d Oct").replace(" 0", " ") if tick.hour == 0 else "")
        out.append(f'<line x1="{xs:.1f}" x2="{xs:.1f}" y1="{BY1}" y2="{BY1 + 6}" class="tl-axis"/>'
                   f'<text x="{xs:.1f}" y="{BY1 + 20}" class="tl-tick" text-anchor="middle">{lab}</text>')
        tick += timedelta(hours=2)
    out.append(f'<text x="{X0}" y="{BY1 + 20}" class="tl-tick" text-anchor="start" dy="16">29 Oct</text>')
    for tp in data["turning_points"]:
        n = tp["n"]
        y = 40 if n % 2 else 80
        xa, xb, xc = x(tp["time_start"]), x(tp["time_end"]), x(tp["time"])
        out.append(f'<line x1="{xa:.1f}" x2="{xb:.1f}" y1="{y}" y2="{y}" class="tl-span"/>'
                   f'<line x1="{xc:.1f}" x2="{xc:.1f}" y1="{y + 12}" y2="{BY0}" class="tl-stem"/>')
        label = f"Turning point {n}: {tp['title']}. {tp['key_number']}. Open card."
        out.append(f'<g class="tl-tp" data-tp="{tp["id"]}" tabindex="0" role="link" aria-label="{html.escape(label)}">'
                   f'<title>TP{n}: {html.escape(tp["title"])} ({hhmm(tp["time"])} UTC)</title>'
                   f'<circle cx="{xc:.1f}" cy="{y}" r="12"/>'
                   f'<text x="{xc:.1f}" y="{y + 4.5}" text-anchor="middle">{n}</text></g>')
    # legend
    lx = X0
    for g, col in GROUP_COLOUR.items():
        out.append(f'<rect x="{lx}" y="186" width="14" height="10" fill="{col}"/>'
                   f'<text x="{lx + 19}" y="195" class="tl-leg">{GROUP_LABEL[g]}</text>')
        lx += 19 + 7.2 * len(GROUP_LABEL[g]) + 18
    out.append(f'<rect x="{lx}" y="186" width="14" height="10" fill="url(#tl-hatch)" class="tl-gap"/>'
               f'<text x="{lx + 19}" y="195" class="tl-leg">No commits / pause</text>')
    out.append("</svg>")
    return "".join(out)


def timeline_widget(h: str, data: dict) -> str:
    m = re.search(r"<!-- widget:timeline -->\s*<p><img[^>]*></p>\s*(<p><em>(.*?)</em></p>)?", h, flags=re.S)
    assert m, "timeline marker not found"
    cap = m.group(2) or ""
    cap = re.sub(r"\s*Data:.*$", "", cap, flags=re.S)
    fig = (f'<figure class="timeline" id="timeline-fig"><div class="tl-scroll">{timeline_svg(data)}</div>'
           f'<figcaption>{cap} Click a numbered circle to open its turning point. '
           f'Data: <a href="{REPO_URL}docs/explainer/journey_data.json" target="_blank" rel="noopener">'
           f'journey_data.json</a>.</figcaption>'
           '<p class="tl-controls"><button type="button" id="tp-open-all">Open all turning points</button> '
           '<button type="button" id="tp-close-all">Close all</button></p></figure>')
    return h[:m.start()] + fig + h[m.end():]


def tp_cards(h: str, data: dict) -> str:
    tps = {tp["id"]: tp for tp in data["turning_points"]}
    pat = re.compile(r'<p><a id="(tp-\d+)"></a></p>\s*<h2 id="[^"]*">(.*?)</h2>(.*?)(?=<p><a id="tp-\d+"></a></p>|<h2|$)',
                     re.S)

    def rep(m):
        tid, title, body = m.group(1), m.group(2), m.group(3)
        tp = tps[tid]
        step = (f'<a class="chip" href="#step-{tp["method_step"]}">Shaped Method step {tp["method_step"]} →</a>'
                if tp.get("method_step") else '<a class="chip" href="#limitations">Fixed the caveats in the Method →</a>')
        return (f'<details class="tp-card" id="{tid}"><summary><span class="tp-n" aria-hidden="true">{tp["n"]}</span>'
                f'<span class="tp-head"><span class="tp-title">{title}</span>'
                f'<span class="tp-key">{html.escape(tp["key_number"])}</span></span></summary>'
                f'<div class="tp-body"><p class="tp-lead"><strong>In short.</strong> {html.escape(tp["summary"])}</p>'
                f'{body}<p>{step}</p></div></details>')
    new, n = pat.subn(rep, h)
    assert n == len(tps), f"expected {len(tps)} turning points, found {n}"
    return new


def worked_widget(h: str) -> str:
    m = re.search(r"<!-- worked:start -->(.*?)<!-- worked:end -->", h, flags=re.S)
    assert m, "worked-example markers not found"
    body = m.group(1)
    heads = list(re.finditer(r'(?:<p><a id="([^"]+)"></a></p>\s*)?<h3 id="([^"]*)">(.*?)</h3>', body, flags=re.S))
    panes = []
    for i, hm in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        content = body[hm.end():end]
        pid = hm.group(1) or f"we-{i + 1}"
        panes.append((pid, hm.group(2), hm.group(3), content))
    nav, divs = [], []
    for i, (pid, hid, title, content) in enumerate(panes):
        short = re.sub(r"<[^>]+>", "", title)
        num, _, label = short.partition(" · ")
        num = num.replace("Step ", "").replace("Hold-out control", "H")
        nav.append(f'<button type="button" role="tab" class="wk-tab" id="wk-tab-{i}" data-i="{i}" '
                   f'aria-controls="{pid}" aria-selected="{"true" if i == 0 else "false"}" '
                   f'tabindex="{0 if i == 0 else -1}"><span class="wk-n">{num}</span>'
                   f'<span class="wk-t">{html.escape(label.split(" (")[0].split(":")[0])}</span></button>')
        divs.append(f'<section class="wk-pane" role="tabpanel" id="{pid}" data-i="{i}" aria-labelledby="wk-tab-{i}"'
                    f'{"" if i == 0 else " hidden"}><h3 id="{hid}">{title}</h3>{content}</section>')
    viewer = (f'<div class="worked" id="worked"><div class="wk-nav" role="tablist" aria-label="Worked example steps">'
              f'{"".join(nav)}</div><div class="wk-body">{"".join(divs)}</div>'
              '<div class="wk-ctrl"><button type="button" id="wk-prev">← Previous</button>'
              '<span id="wk-pos" aria-live="polite"></span><button type="button" id="wk-next">Next →</button></div></div>')
    return h[:m.start()] + viewer + h[m.end():]


# ------------------------------------------------------------------------------------------------ page
CSS = r"""
:root{--bg:#fbfaf7;--surface:#ffffff;--surface2:#f1efe9;--ink:#1d1d1f;--muted:#5d5a54;--line:#dcd6ca;
--accent:#2b6cb0;--accent2:#b4441b;--code:#f3f1ec;--focus:#d55e00;--shadow:0 1px 3px rgba(0,0,0,.08)}
@media (prefers-color-scheme: dark){:root{--bg:#15171b;--surface:#1f2329;--surface2:#2a2e35;--ink:#ececec;
--muted:#a7abb3;--line:#3d434c;--accent:#7fb2ec;--accent2:#f0915f;--code:#262a31;--focus:#f0915f;
--shadow:0 1px 3px rgba(0,0,0,.4)}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,
Helvetica,Arial,sans-serif}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--focus);
outline-offset:2px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:8px;background:var(--surface);padding:6px 10px;z-index:9}
header.site{background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.wrap{max-width:900px;margin:0 auto;padding:0 16px}
header.site h1{font-size:1.05rem;margin:0;padding:12px 0 4px;line-height:1.3}
header.site p.sub{margin:0 0 6px;color:var(--muted);font-size:.85rem}
.tabs{display:flex;gap:4px;overflow-x:auto}
.tabs button{font:inherit;font-size:.95rem;background:none;border:0;border-bottom:3px solid transparent;color:var(--muted);
padding:8px 12px;cursor:pointer;white-space:nowrap}
.tabs button[aria-selected=true]{color:var(--ink);border-bottom-color:var(--accent);font-weight:600}
main{padding:8px 0 48px}
section.tab-panel[hidden]{display:none}
h1,h2,h3,h4{line-height:1.3}
h1{font-size:1.6rem;margin:1.2rem 0 .6rem}h2{font-size:1.3rem;margin:2rem 0 .6rem;padding-top:.4rem;
border-top:1px solid var(--line)}h3{font-size:1.1rem;margin:1.6rem 0 .5rem}
p,li{max-width:76ch}
code{background:var(--code);padding:.1em .3em;border-radius:4px;font-size:.88em;overflow-wrap:anywhere}
pre{background:var(--code);padding:12px;border-radius:8px;overflow-x:auto;font-size:.82rem;line-height:1.45}
pre code{background:none;padding:0;overflow-wrap:normal}
blockquote{margin:1rem 0;padding:.6rem 1rem;background:var(--surface);border-left:4px solid var(--accent2);
border-radius:6px;box-shadow:var(--shadow)}
blockquote p{margin:.4rem 0}
.table-wrap{overflow-x:auto;margin:.8rem 0;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
table{border-collapse:collapse;font-size:.88rem;width:100%}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:var(--surface2)}
tr:last-child td{border-bottom:0}
img.fig{max-width:100%;height:auto;display:block;margin:.6rem auto;background:#fff;border-radius:6px;padding:6px;
border:1px solid var(--line)}
figure{margin:1rem 0}
figcaption{color:var(--muted);font-size:.85rem;margin-top:.4rem}
figure.pipeline{text-align:center}
.pipeline-svg{width:100%;max-width:560px;height:auto}
.pl-stage{cursor:pointer}
.pl-stage:hover .pl-box,.pl-stage:focus .pl-box{stroke:var(--accent);stroke-width:2.5}
.pl-stage:focus{outline:none}
.pl-stage:focus .pl-box{stroke:var(--focus);stroke-width:3}
.tl-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:4px}
.timeline-svg{width:100%;min-width:640px;height:auto;display:block;font-family:inherit}
.tl-tick,.tl-leg{fill:var(--muted);font-size:12px}
.tl-axis{stroke:var(--muted)}
.tl-span{stroke:var(--muted);stroke-width:2;opacity:.6}
.tl-stem{stroke:var(--muted);stroke-dasharray:2 3}
.tl-hatchline{stroke:var(--muted);stroke-width:2}
.tl-gap{stroke:var(--line)}
.tl-tp{cursor:pointer}
.tl-tp circle{fill:#d55e00;stroke:var(--surface);stroke-width:2}
.tl-tp text{fill:#fff;font-size:13px;font-weight:700;pointer-events:none}
.tl-tp:hover circle,.tl-tp:focus circle{stroke:var(--ink);stroke-width:3}
.tl-tp:focus{outline:none}
.tl-controls button,.wk-ctrl button{font:inherit;font-size:.9rem;padding:6px 12px;border:1px solid var(--line);
border-radius:6px;background:var(--surface);color:var(--ink);cursor:pointer}
.wk-ctrl button:disabled{opacity:.45;cursor:default}
details.tp-card{background:var(--surface);border:1px solid var(--line);border-radius:8px;margin:.8rem 0;
box-shadow:var(--shadow)}
details.tp-card>summary{list-style:none;cursor:pointer;display:flex;gap:12px;align-items:flex-start;padding:12px 14px}
details.tp-card>summary::-webkit-details-marker{display:none}
details.tp-card>summary::after{content:"+";margin-left:auto;color:var(--muted);font-size:1.3rem;line-height:1}
details.tp-card[open]>summary::after{content:"−"}
.tp-n{flex:0 0 auto;width:30px;height:30px;border-radius:50%;background:#d55e00;color:#fff;font-weight:700;
display:flex;align-items:center;justify-content:center}
.tp-head{display:flex;flex-direction:column}
.tp-title{font-weight:650;font-size:1.02rem}
.tp-key{color:var(--accent2);font-size:.88rem;font-weight:600}
.tp-body{padding:0 16px 12px;border-top:1px solid var(--line)}
.tp-lead{background:var(--surface2);padding:8px 10px;border-radius:6px}
.chip{display:inline-block;padding:3px 10px;border-radius:999px;background:var(--surface2);text-decoration:none;
font-size:.88rem;border:1px solid var(--line)}
.worked{border:1px solid var(--line);border-radius:10px;background:var(--surface);margin:1rem 0;box-shadow:var(--shadow)}
.wk-nav{display:flex;flex-wrap:wrap;gap:4px;padding:8px;border-bottom:1px solid var(--line)}
.wk-tab{font:inherit;font-size:.82rem;display:flex;gap:6px;align-items:center;padding:4px 10px 4px 4px;
border:1px solid var(--line);border-radius:999px;background:var(--bg);color:var(--ink);cursor:pointer}
.wk-tab .wk-n{display:inline-flex;min-width:22px;height:22px;border-radius:50%;align-items:center;justify-content:center;
background:var(--surface2);font-weight:700;font-size:.78rem}
.wk-tab[aria-selected=true]{border-color:var(--accent);background:var(--surface2)}
.wk-tab[aria-selected=true] .wk-n{background:var(--accent);color:var(--surface)}
.wk-body{padding:0 16px}
.wk-pane h3{margin-top:1rem}
.wk-ctrl{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 16px;
border-top:1px solid var(--line)}
#wk-pos{color:var(--muted);font-size:.88rem}
footer{color:var(--muted);font-size:.82rem;border-top:1px solid var(--line);padding:16px 0 32px}
:target{scroll-margin-top:110px}
[id]{scroll-margin-top:110px}
@media (max-width:600px){body{font-size:15px}header.site{position:static}[id],:target{scroll-margin-top:8px}h1{font-size:1.35rem}h2{font-size:1.15rem}
.wk-tab .wk-t{display:none}.wk-tab{padding:4px}}
"""

JS = r"""
(function(){
  window.addEventListener('error', function(e){ document.documentElement.setAttribute('data-error', String(e.message)); });
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tabs [role=tab]'));
  function activate(id, focus){
    tabs.forEach(function(b){
      var on = b.getAttribute('aria-controls') === id;
      b.setAttribute('aria-selected', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1;
      document.getElementById(b.getAttribute('aria-controls')).hidden = !on;
      if (on && focus) b.focus();
    });
  }
  tabs.forEach(function(b, i){
    b.addEventListener('click', function(){ activate(b.getAttribute('aria-controls')); history.replaceState(null,'','#'+b.getAttribute('aria-controls')); window.scrollTo(0,0); });
    b.addEventListener('keydown', function(e){
      var j = e.key === 'ArrowRight' ? (i+1)%tabs.length : e.key === 'ArrowLeft' ? (i-1+tabs.length)%tabs.length : -1;
      if (j >= 0){ e.preventDefault(); activate(tabs[j].getAttribute('aria-controls'), true); }
    });
  });
  // worked-example viewer
  var wkTabs = Array.prototype.slice.call(document.querySelectorAll('.wk-tab'));
  var wkPanes = Array.prototype.slice.call(document.querySelectorAll('.wk-pane'));
  var cur = 0;
  function showPane(i, focus){
    if (!wkPanes.length) return;
    cur = Math.max(0, Math.min(wkPanes.length-1, i));
    wkPanes.forEach(function(p, k){ p.hidden = k !== cur; });
    wkTabs.forEach(function(b, k){ b.setAttribute('aria-selected', k === cur ? 'true':'false'); b.tabIndex = k === cur ? 0 : -1; });
    document.getElementById('wk-prev').disabled = cur === 0;
    document.getElementById('wk-next').disabled = cur === wkPanes.length-1;
    document.getElementById('wk-pos').textContent = 'Panel ' + (cur+1) + ' of ' + wkPanes.length;
    if (focus) wkTabs[cur].focus();
  }
  wkTabs.forEach(function(b, i){
    b.addEventListener('click', function(){ showPane(i); });
    b.addEventListener('keydown', function(e){
      if (e.key === 'ArrowRight'){ e.preventDefault(); showPane(i+1, true); }
      if (e.key === 'ArrowLeft'){ e.preventDefault(); showPane(i-1, true); }
    });
  });
  if (wkPanes.length){
    document.getElementById('wk-prev').addEventListener('click', function(){ showPane(cur-1); document.getElementById('worked').scrollIntoView({block:'start'}); });
    document.getElementById('wk-next').addEventListener('click', function(){ showPane(cur+1); document.getElementById('worked').scrollIntoView({block:'start'}); });
    showPane(0);
  }
  // navigation to any id, across tabs, into closed cards and hidden panels
  function goTo(id, push){
    var el = id && document.getElementById(id);
    if (!el) return false;
    if (el.classList.contains('tab-panel')){ activate(id); window.scrollTo(0,0); }
    else {
      var panel = el.closest('.tab-panel'); if (panel) activate(panel.id);
      var pane = el.closest('.wk-pane'); if (pane) showPane(+pane.getAttribute('data-i'));
      var d = el.closest('details'); while (d){ d.open = true; d = d.parentElement && d.parentElement.closest('details'); }
      if (el.tagName === 'DETAILS') el.open = true;
      el.scrollIntoView({block:'start'});
      if (!el.hasAttribute('tabindex') && !/^(A|BUTTON|SUMMARY|DETAILS)$/.test(el.tagName)) el.setAttribute('tabindex','-1');
      try { el.focus({preventScroll:true}); } catch(e) {}
    }
    if (push) history.pushState(null, '', '#'+id);
    return true;
  }
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href').length > 1){ if (goTo(a.getAttribute('href').slice(1), true)) e.preventDefault(); }
  });
  function bindJump(sel, attr, prefix){
    Array.prototype.forEach.call(document.querySelectorAll(sel), function(g){
      var go = function(){ goTo(prefix + g.getAttribute(attr), true); };
      g.addEventListener('click', go);
      g.addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); go(); } });
    });
  }
  bindJump('.pl-stage', 'data-step', 'step-');
  bindJump('.tl-tp', 'data-tp', '');
  var oa = document.getElementById('tp-open-all'), ca = document.getElementById('tp-close-all');
  if (oa) oa.addEventListener('click', function(){ document.querySelectorAll('details.tp-card').forEach(function(d){ d.open = true; }); });
  if (ca) ca.addEventListener('click', function(){ document.querySelectorAll('details.tp-card').forEach(function(d){ d.open = false; }); });
  window.addEventListener('hashchange', function(){ goTo(location.hash.slice(1)); });
  if (!(location.hash && goTo(decodeURIComponent(location.hash.slice(1))))) activate('tab-method');
  document.documentElement.setAttribute('data-ready', '1');
})();
"""


def build() -> str:
    data = json.loads((HERE / "journey_data.json").read_text())
    texts = {f: (HERE / f).read_text() for _, _, f in TABS}
    explicit = set().union(*(explicit_ids(t) for t in texts.values()))
    rendered, heading_ids = {}, set()
    for tab, _, f in TABS:
        h, ids = add_heading_ids(MD.render(texts[f]), tab)
        rendered[tab] = h
        heading_ids |= ids
    clash = explicit & heading_ids
    assert not clash, f"id clash: {clash}"
    panels = []
    for tab, label, f in TABS:
        h = fix_links(rendered[tab], tab, explicit, heading_ids)
        if tab == "method":
            h = pipeline_widget(h)
            h = worked_widget(h)
        if tab == "journey":
            h = timeline_widget(h, data)
            h = tp_cards(h, data)
        h = wrap_tables(inline_images(h))
        panels.append(f'<section class="tab-panel" id="tab-{tab}" role="tabpanel" aria-labelledby="tabbtn-{tab}"'
                      f'{"" if tab == "method" else " hidden"}>{h}</section>')
    tabbtns = "".join(f'<button type="button" role="tab" id="tabbtn-{t}" aria-controls="tab-{t}" '
                      f'aria-selected="{"true" if t == "method" else "false"}" tabindex="{0 if t == "method" else -1}">'
                      f'{label}</button>' for t, label, _ in TABS)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Gene Function Explainer</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
<h1>Predicting functions of uncharacterised genes from co-essentiality</h1>
<p class="sub">An explainer of an AI-run project. Not verified by a human.</p>
<nav class="tabs" role="tablist" aria-label="Explainer sections">{tabbtns}</nav>
</div></header>
<main id="main" class="wrap">
{"".join(panels)}
</main>
<footer class="wrap">Built by docs/explainer/build_html.py from METHOD.md, JOURNEY.md, INSIGHTS.md and
journey_data.json. Self-contained: no network requests. Links to repository files open GitHub
(<a href="{REPO_URL}docs/explainer/README.md" target="_blank" rel="noopener">explainer README</a>,
<a href="{REPO_URL}docs/explainer/DISCREPANCIES.md" target="_blank" rel="noopener">discrepancies</a>).</footer>
<script>{JS}</script>
</body>
</html>
"""
    # final check: every in-page link resolves
    ids = set(re.findall(r'\sid="([^"]+)"', page))
    missing = sorted({h for h in re.findall(r'href="#([^"]+)"', page) if h not in ids})
    assert not missing, f"unresolved in-page links: {missing}"
    return page


if __name__ == "__main__":
    page = build()
    OUT.write_text(page)
    print(f"wrote {OUT} ({len(page.encode()) / 1e6:.2f} MB)")
