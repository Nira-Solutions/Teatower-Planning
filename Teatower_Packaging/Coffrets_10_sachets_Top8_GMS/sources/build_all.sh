S="$1"; shift; cd "$S"; P="/c/Program Files/LibreOffice/program/python.exe"; CH="/c/Program Files/Google/Chrome/Application/chrome.exe"; LOGO="C:/Users/FlowUP/OneDrive/Teatower/brand/Teatower_logo_compact.svg"
for k in "$@"; do B="$S/boxes/$k"; mkdir -p "$B"; cp build/*.woff build/fonts_local.css "$B/"
  "$P" gen_box.py "$B" "$LOGO" gen_parts/boxes.json $k || exit 1
  for n in corps couvercle; do "$CH" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=5000 --print-to-pdf="$(cygpath -w "$B/$n.pdf")" "file:///$(cygpath -m "$B/$n.html")" 2>/dev/null; done
  "$P" merge.py boxes/$k c0196_src 4 >/dev/null
  T=$("$P" -c "import json;c=json.load(open('gen_parts/boxes.json',encoding='utf-8'))['$k'];print(c['name'])")
  "$P" mockup.py "boxes/$k" "Coffret 10 sachets · $T" "boxes/$k/mockup.html" >/dev/null
  "$CH" --headless=new --disable-gpu --hide-scrollbars --window-size=1800,1000 --screenshot="$(cygpath -w "$B/mockup.png")" "file:///$(cygpath -m "$B/mockup.html")" 2>/dev/null
  echo "$k done"; done
