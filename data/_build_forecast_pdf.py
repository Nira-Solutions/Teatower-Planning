"""Convertit le forecast B2B markdown en PDF."""
import markdown
from xhtml2pdf import pisa
from pathlib import Path

ROOT = Path(__file__).parent
MD = ROOT / "Forecast_B2B_2026-2027.md"
PDF = ROOT.parent / "Forecast_B2B_2026-2027.pdf"

md_text = MD.read_text(encoding="utf-8")
html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "sane_lists", "toc"],
)

CSS = """
@page {
  size: A4 portrait;
  margin: 1.8cm 1.5cm;
  @frame footer {
    -pdf-frame-content: footer_content;
    bottom: 0.6cm; left: 1.5cm; right: 1.5cm; height: 0.8cm;
  }
}
body {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 9pt;
  line-height: 1.4;
  color: #222;
}
h1 {
  color: #0c4a30;
  font-size: 19pt;
  border-bottom: 2px solid #0c4a30;
  padding-bottom: 4px;
  margin-top: 0;
}
h2 {
  color: #0c4a30;
  font-size: 13pt;
  margin-top: 18px;
  border-bottom: 1px solid #d4a373;
  padding-bottom: 2px;
}
h3 {
  color: #6b4423;
  font-size: 11pt;
  margin-top: 12px;
  background: #f4e9d8;
  padding: 4px 8px;
  border-left: 3px solid #d4a373;
}
strong { color: #0c4a30; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 8pt;
}
th {
  background: #0c4a30;
  color: white;
  padding: 5px 6px;
  text-align: left;
  border: 1px solid #0c4a30;
}
td {
  padding: 4px 6px;
  border: 1px solid #ccc;
  vertical-align: top;
}
tr:nth-child(even) td { background: #f8f5ef; }
ul, ol { margin: 4px 0; padding-left: 18px; }
li { margin-bottom: 2px; }
hr { border: 0; border-top: 1px solid #d4a373; margin: 14px 0; }
code { background: #f4e9d8; padding: 1px 3px; font-size: 8pt; }
"""

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{html_body}
<div id="footer_content" style="text-align:center; font-size:8pt; color:#888;">
Forecast Opérationnel B2B Teatower 2026-2027 — Confidentiel — page <pdf:pagenumber/>/<pdf:pagecount/>
</div>
</body></html>"""

with open(PDF, "wb") as f:
    result = pisa.CreatePDF(html, dest=f, encoding="utf-8")

if result.err:
    print(f"ERREUR : {result.err} erreurs lors de la conversion")
    raise SystemExit(1)

print(f"PDF généré : {PDF}")
print(f"Taille : {PDF.stat().st_size / 1024:.1f} Ko")
