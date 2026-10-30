#!/usr/bin/env bash
# 80_build_manuscript.sh -- render manuscript/manuscript.md to manuscript/manuscript.docx and manuscript/manuscript.pdf.
#
# Route (no LaTeX engine is installed on the build machine):
#   1. strip every <!-- ... --> comment (src tags, notes) into a temporary copy; the markdown source is never changed;
#   2. pandoc (2.12) -> manuscript.docx, figures embedded from manuscript/figures/;
#   3. pandoc -> self-contained HTML (figures inlined as data URIs, print CSS) -> PDF with headless Google Chrome.
# If Chrome is not found, only the .docx is written and the script says so. A LaTeX engine (xelatex) is used instead of
# Chrome when one is on PATH, unless BUILD_PDF_ROUTE=chrome is set.
# Usage: bash scripts/80_build_manuscript.sh        (from anywhere; paths are resolved from the script location)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MS="$ROOT/manuscript"
SRC="$MS/manuscript.md"
PANDOC="${PANDOC:-pandoc}"
command -v "$PANDOC" >/dev/null 2>&1 || PANDOC="$(command -v pandoc || true)"
[ -n "$PANDOC" ] || { echo "pandoc not found" >&2; exit 1; }
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

BUILD="$(mktemp -d "${TMPDIR:-/tmp}/ms_build.XXXXXX")"
trap 'rm -rf "$BUILD"' EXIT

# 1. strip comments; give figures full text width
python3 -I - "$SRC" "$BUILD/clean.md" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
PUNCT = r"(?=[,.;:)\]])"
C = r"<!--(?:(?!-->).)*-->"   # one comment; never spans a comment end
prev = None
while prev != s:
    prev = s
    s = re.sub(r"\n[ \t]*" + C + PUNCT, "", s, flags=re.S)   # comment on its own line before punctuation
    s = re.sub(r"[ \t]*" + C + PUNCT, "", s, flags=re.S)     # inline comment before punctuation
s = re.sub(C, "", s, flags=re.S)                              # any remaining comment
s = re.sub(r"[ \t]{2,}", " ", s)                                     # collapse runs of spaces left behind
s = re.sub(r"^(!\[[^\]]*\]\([^)]+\))[ \t]*$", r"\1{width=100%}", s, flags=re.M)
assert "<!--" not in s and "src:" not in s, "comment stripping failed"
open(sys.argv[2], "w", encoding="utf-8").write(s)
PY

# 2. DOCX
"$PANDOC" "$BUILD/clean.md" -f markdown -t docx --resource-path="$MS" -o "$MS/manuscript.docx"
echo "wrote $MS/manuscript.docx"

# 3. PDF
cat > "$BUILD/print.css" <<'CSS'
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
html { font-size: 10.5pt; }
body { font-family: "Times New Roman", Times, serif; line-height: 1.38; max-width: none; margin: 0; color: #111; background: #fff; }
h1.title { font-size: 17pt; line-height: 1.25; margin: 0 0 10pt 0; }
h1 { font-size: 13.5pt; margin: 16pt 0 6pt 0; page-break-after: avoid; }
h2 { font-size: 11.5pt; margin: 12pt 0 4pt 0; page-break-after: avoid; }
p { margin: 0 0 6pt 0; text-align: left; }
table { border-collapse: collapse; width: 100%; font-size: 7.6pt; line-height: 1.22; margin: 6pt 0 10pt 0; page-break-inside: auto; }
th, td { border: 0.5pt solid #999; padding: 2pt 3pt; vertical-align: top; text-align: left; }
th { background: #eee; }
tr { page-break-inside: avoid; }
img { max-width: 100%; height: auto; display: block; margin: 8pt auto 4pt auto; page-break-inside: avoid; }
ol li { margin-bottom: 2pt; font-size: 9pt; word-break: break-word; }
code { font-size: 8.5pt; }
CSS

if command -v xelatex >/dev/null 2>&1 && [ "${BUILD_PDF_ROUTE:-}" != "chrome" ]; then
  "$PANDOC" "$BUILD/clean.md" --pdf-engine=xelatex --resource-path="$MS" -V geometry:margin=18mm -o "$MS/manuscript.pdf"
  echo "wrote $MS/manuscript.pdf (xelatex)"
elif [ -x "$CHROME" ]; then
  "$PANDOC" "$BUILD/clean.md" -f markdown -t html5 --standalone --self-contained --resource-path="$MS" \
    --css="$BUILD/print.css" --metadata pagetitle="Manuscript" -o "$BUILD/manuscript.html"
  "$CHROME" --headless --disable-gpu --no-sandbox --user-data-dir="$BUILD/chrome" --no-pdf-header-footer --print-to-pdf-no-header \
    --print-to-pdf="$MS/manuscript.pdf" "file://$BUILD/manuscript.html" >/dev/null 2>&1
  [ -s "$MS/manuscript.pdf" ] || { echo "Chrome did not write the PDF" >&2; exit 1; }
  echo "wrote $MS/manuscript.pdf (pandoc HTML -> headless Chrome)"
else
  echo "No LaTeX engine and no Chrome found: PDF not built (DOCX only)." >&2
fi
