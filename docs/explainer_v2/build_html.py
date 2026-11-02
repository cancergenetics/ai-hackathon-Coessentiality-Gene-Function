"""Build docs/explainer_v2/explainer.html: one self-contained, single-scroll page from README.md.

- Markdown is rendered with markdown-it-py (already in the project environment).
- Figures are inlined as base64 PNG; CSS and JS are inline; the page makes no network requests.
- A sticky table of contents lists the numbered sections (left column on wide screens, top bar on phones).
- The five-step pipeline figure is clickable: each box jumps to its step.
- "Fine print", "Glossary" and "References" are collapsible <details> blocks.
- Light and dark themes follow prefers-color-scheme.
- Links to other repository files become GitHub links.

Usage (from the project root):
    ./.env/bin/python -I docs/explainer_v2/build_html.py
"""
import base64
import html
import posixpath
import re
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / "README.md"
OUT = HERE / "explainer.html"
REPO_URL = "https://github.com/cancergenetics/ai-hackathon-Coessentiality-Gene-Function/blob/main/"
COLLAPSIBLE = ("Fine print", "Glossary", "References")

MD = MarkdownIt("commonmark", {"html": False, "typographer": False}).enable("table")


def slug(text):
    s = re.sub(r"<[^>]+>", "", text)
    s = html.unescape(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def fix_link(href):
    """Repository-relative links -> GitHub; keep external and in-page links."""
    if re.match(r"^(https?:|mailto:|#)", href):
        return href
    path = posixpath.normpath(posixpath.join("docs/explainer_v2", href))
    return REPO_URL + path


def inline_img(match):
    src, alt = match.group("src"), match.group("alt")
    data = base64.b64encode((HERE / src).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{alt}" loading="lazy">'


def build():
    body = MD.render(SRC.read_text())

    # Headings: ids + TOC (h2 only).
    toc = []

    def head(m):
        level, inner = m.group(1), m.group(2)
        hid = slug(inner)
        if level == "2":
            label = re.sub(r"<[^>]+>", "", inner)
            toc.append((hid, html.unescape(label)))
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = re.sub(r"<h([23])>(.*?)</h\1>", head, body)

    # Step ids for the clickable pipeline.
    step_ids = re.findall(r'<h3 id="(step-\d[^"]*)">', body)

    # Links.
    body = re.sub(r'href="([^"]+)"', lambda m: f'href="{html.escape(fix_link(html.unescape(m.group(1))))}"', body)

    # Images (inline) and the clickable pipeline.
    img_re = re.compile(r'<img src="(?P<src>figures/[^"]+\.png)" alt="(?P<alt>[^"]*)" ?/?>')

    def figure(m):
        tag = inline_img(m)
        if "b_pipeline" in m.group("src"):
            links = "".join(
                f'<a class="hot" style="left:{i * 20}%" href="#{sid}" aria-label="Go to step {i + 1}"></a>'
                for i, sid in enumerate(step_ids[:5]))
            return (f'<span class="fig wide pipeline"><span class="inner">{tag}{links}</span></span>'
                    '<span class="hint">Click a step to jump to it.</span>')
        wide = "" if "a_funnel" in m.group("src") else " wide"
        return f'<span class="fig{wide}"><span class="inner">{tag}</span></span>'

    body = img_re.sub(figure, body)

    # Tables scroll sideways on phones.
    body = body.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")

    # Blockquotes after the disclaimer become callout boxes.
    first = body.find("<blockquote>")
    body = body[:first] + body[first:].replace("<blockquote>", '<blockquote class="note">', 1)
    rest_start = body.find("</blockquote>") + len("</blockquote>")
    body = body[:rest_start] + body[rest_start:].replace("<blockquote>", '<blockquote class="box">')

    # Wrap each h2 section in <section>; make some collapsible.
    parts = re.split(r'(?=<h2 id=")', body)
    out = []
    for part in parts:
        m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>(.*)', part, re.S)
        if not m:
            out.append(part)
            continue
        hid, title, content = m.groups()
        plain = re.sub(r"^\d+\.\s*", "", re.sub(r"<[^>]+>", "", title))
        if plain in COLLAPSIBLE:
            out.append(f'<section id="{hid}"><details><summary><h2>{title}</h2></summary>{content}'
                       f'</details></section>')
        else:
            out.append(f'<section id="{hid}"><h2>{title}</h2>{content}</section>')
    body = "".join(out)

    title = re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", body).group(1))
    toc_html = "".join(f'<li><a href="#{hid}">{html.escape(label)}</a></li>' for hid, label in toc)
    page = TEMPLATE.replace("%TITLE%", html.escape(title)).replace("%TOC%", toc_html).replace("%BODY%", body)
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page) / 1e6:.2f} MB)")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%TITLE%</title>
<style>
:root {
  color-scheme: light;
  --bg: #fcfcfb; --surface: #ffffff; --ink: #1a1a19; --ink2: #52514e; --rule: #e2e0db;
  --accent: #2a78d6; --accent-soft: #eef4fc; --warm-soft: #fdf3ec; --warm: #c4561f;
  --shadow: 0 1px 2px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --bg: #161615; --surface: #1f1f1e; --ink: #f0efec; --ink2: #c3c2b7; --rule: #383733;
    --accent: #6aa5ee; --accent-soft: #1b2a3d; --warm-soft: #33241b; --warm: #f08a5d;
    --shadow: none;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 16px; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 17px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
.layout { display: grid; grid-template-columns: 240px minmax(0, 760px); gap: 48px; justify-content: center;
  padding: 32px 24px 80px; }
nav.toc { position: sticky; top: 24px; align-self: start; font-size: 14px; }
nav.toc .label { font-weight: 700; color: var(--ink2); text-transform: uppercase; letter-spacing: .06em;
  font-size: 12px; margin-bottom: 8px; }
nav.toc ol { list-style: none; margin: 0; padding: 0; border-left: 2px solid var(--rule); }
nav.toc li a { display: block; padding: 5px 12px; color: var(--ink2); text-decoration: none;
  border-left: 2px solid transparent; margin-left: -2px; }
nav.toc li a:hover { color: var(--ink); }
nav.toc li a.active { color: var(--accent); border-left-color: var(--accent); font-weight: 600; }
main { min-width: 0; }
h1 { font-size: 32px; line-height: 1.2; margin: 0 0 16px; }
h2 { font-size: 25px; line-height: 1.25; margin: 48px 0 12px; padding-top: 8px; border-top: 1px solid var(--rule); }
h3 { font-size: 19px; margin: 32px 0 8px; }
p, li { max-width: 72ch; }
a { color: var(--accent); }
strong { font-weight: 650; }
code { font-size: 14px; background: var(--accent-soft); padding: 1px 4px; border-radius: 4px; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 32px 0; }
blockquote { margin: 20px 0; padding: 12px 18px; border-radius: 8px; }
blockquote p { margin: 6px 0; }
blockquote.note { background: var(--warm-soft); border-left: 4px solid var(--warm); font-size: 15px; }
blockquote.box { background: var(--accent-soft); border-left: 4px solid var(--accent); }
blockquote.box ul { padding-left: 20px; margin: 6px 0; }
.tablewrap { overflow-x: auto; margin: 16px 0; border: 1px solid var(--rule); border-radius: 8px;
  background: var(--surface); box-shadow: var(--shadow); }
table { border-collapse: collapse; width: 100%; font-size: 15px; }
th, td { text-align: left; vertical-align: top; padding: 8px 12px; border-bottom: 1px solid var(--rule); }
th { font-weight: 650; background: var(--accent-soft); }
tr:last-child td { border-bottom: 0; }
.fig { display: block; position: relative; margin: 20px 0 8px; background: #ffffff; border-radius: 10px;
  padding: 10px; border: 1px solid var(--rule); box-shadow: var(--shadow); }
.fig .inner { display: block; position: relative; }
.fig img { display: block; width: 100%; height: auto; }
.pipeline .hot { position: absolute; top: 0; bottom: 0; width: 20%; border-radius: 10px; }
.pipeline .hot:hover, .pipeline .hot:focus-visible { background: rgba(42,120,214,.12); outline: 2px solid #2a78d6; }
.hint { display: block; font-size: 13px; color: var(--ink2); margin-bottom: 12px; }
details > summary { cursor: pointer; list-style: none; }
details > summary::-webkit-details-marker { display: none; }
details > summary h2 { display: block; }
details > summary h2::after { content: "  \\25B8 show"; font-size: 14px; font-weight: 400; color: var(--ink2); }
details[open] > summary h2::after { content: "  \\25BE hide"; }
@media (max-width: 900px) {
  .layout { display: block; padding: 0 16px 64px; }
  nav.toc { position: sticky; top: 0; z-index: 5; background: var(--bg); margin: 0 -16px 16px;
    padding: 8px 16px; border-bottom: 1px solid var(--rule); }
  nav.toc .label { display: none; }
  nav.toc ol { display: flex; gap: 4px; overflow-x: auto; border-left: 0; scrollbar-width: none; }
  nav.toc li a { white-space: nowrap; border-left: 0; margin: 0; padding: 4px 10px; border-radius: 999px;
    background: var(--surface); border: 1px solid var(--rule); }
  nav.toc li a.active { border-color: var(--accent); }
  html { scroll-padding-top: 60px; }
  body { font-size: 16px; }
  h1 { font-size: 26px; margin-top: 8px; }
  h2 { font-size: 22px; }
  .fig { padding: 4px; }
  .fig.wide { overflow-x: auto; }
  .fig.wide .inner { min-width: 680px; }
  .fig.wide::after { content: "scroll sideways →"; display: block; font-size: 12px; color: #52514e; padding: 2px 4px; }
}
</style>
</head>
<body>
<div class="layout">
<nav class="toc" aria-label="Contents"><div class="label">Contents</div><ol>%TOC%</ol></nav>
<main>
%BODY%
</main>
</div>
<script>
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.toc a'));
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  // Open a collapsed section when its TOC link is used.
  links.forEach(function (a) {
    a.addEventListener('click', function () {
      var sec = document.getElementById(a.getAttribute('href').slice(1));
      var d = sec && sec.querySelector('details');
      if (d) d.open = true;
    });
  });
  function openHash() {
    var t = location.hash && document.getElementById(location.hash.slice(1));
    var d = t && (t.querySelector('details') || t.closest('details'));
    if (d) d.open = true;
  }
  openHash();
  window.addEventListener('hashchange', openHash);
  if (!('IntersectionObserver' in window)) return;
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      links.forEach(function (a) { a.classList.remove('active'); });
      var a = byId[e.target.id];
      if (a) {
        a.classList.add('active');
        if (a.scrollIntoView && window.innerWidth <= 900) {
          a.parentNode.parentNode.scrollLeft = a.offsetLeft - 16;
        }
      }
    });
  }, { rootMargin: '-10% 0px -80% 0px' });
  document.querySelectorAll('main section[id]').forEach(function (s) { obs.observe(s); });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
