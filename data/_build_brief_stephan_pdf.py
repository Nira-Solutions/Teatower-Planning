"""Convertit le brief Stephan markdown en PDF."""
import markdown
from xhtml2pdf import pisa
from pathlib import Path

ROOT = Path(__file__).parent
MD = ROOT / "Brief_Stephan_Newsletters_Juin_2026.md"
PDF = ROOT.parent / "Brief_Stephan_Newsletters_Juin_2026.pdf"

md_text = MD.read_text(encoding="utf-8")
html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "sane_lists", "toc"],
)

CSS = """
@page {
  size: A4 landscape;
  margin: 1.2cm 1.2cm 1.5cm 1.2cm;
  @frame footer {
    -pdf-frame-content: footer_content;
    bottom: 0.5cm; left: 1.2cm; right: 1.2cm; height: 0.6cm;
  }
}
body {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 10pt;
  line-height: 1.45;
  color: #222;
}
h1 {
  color: #0c4a30;
  font-size: 20pt;
  border-bottom: 2px solid #0c4a30;
  padding-bottom: 4px;
  margin-top: 0;
}
h2 {
  color: #0c4a30;
  font-size: 14pt;
  margin-top: 18px;
  border-bottom: 1px solid #d4a373;
  padding-bottom: 2px;
}
h3 {
  color: #6b4423;
  font-size: 11.5pt;
  margin-top: 14px;
  background: #f4e9d8;
  padding: 4px 8px;
  border-left: 3px solid #d4a373;
}
h4 {
  color: #6b4423;
  font-size: 10.5pt;
  margin-top: 12px;
}
strong { color: #0c4a30; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 9pt;
}
th {
  background: #0c4a30;
  color: white;
  padding: 6px 8px;
  text-align: left;
  border: 1px solid #0c4a30;
  font-weight: bold;
}
td {
  padding: 5px 8px;
  border: 1px solid #ccc;
  vertical-align: top;
  word-wrap: break-word;
}
tr:nth-child(even) td { background: #f8f5ef; }
ul, ol { margin: 4px 0; padding-left: 22px; }
li { margin-bottom: 3px; }
hr { border: 0; border-top: 1px solid #d4a373; margin: 14px 0; }
code { background: #f4e9d8; padding: 1px 3px; font-size: 9pt; }
pre { background: #f4e9d8; padding: 10px; border-left: 3px solid #d4a373; font-size: 9pt; font-family: 'Courier New', monospace; }
blockquote { border-left: 3px solid #d4a373; padding-left: 12px; color: #555; font-style: italic; margin: 10px 0; }
"""

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{html_body}
<div id="footer_content" style="text-align:center; font-size:8pt; color:#888;">
Brief Stephan - Newsletters Juin 2026 - Teatower - page <pdf:pagenumber/>/<pdf:pagecount/>
</div>
</body></html>"""

with open(PDF, "wb") as f:
    result = pisa.CreatePDF(html, dest=f, encoding="utf-8")

if result.err:
    print(f"ERREUR : {result.err} erreurs lors de la conversion")
    raise SystemExit(1)

print(f"PDF généré : {PDF}")
print(f"Taille : {PDF.stat().st_size / 1024:.1f} Ko")
