"""Patch v7 : vraies photos (sans filtre cartoon) sous coque plastique scellée façon jouet."""
import os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter_pack_single_day.html")
s = open(p, encoding="utf-8").read()

# 1) retour aux vraies images
s = s.replace("mix-blend-mode:multiply;filter:url(#toon)}", "mix-blend-mode:multiply;filter:saturate(1.1)}")
s = re.sub(r'<svg width="0" height="0" style="position:absolute">\s*<filter id="toon".*?</svg>\n', "", s, flags=re.S)

# 2) coque plastique bombée + rebord scellé
css = """
  /* coque plastique thermoformée autour de chaque produit (blister jouet) */
  .dome{position:absolute;left:50%;top:50%;width:214px;height:138px;transform:translate(-50%,-50%);
    border-radius:72px/62px;border:2px solid rgba(255,255,255,.95);
    background:
      radial-gradient(ellipse 55% 38% at 30% 20%,rgba(255,255,255,.80),rgba(255,255,255,0) 70%),
      radial-gradient(ellipse 70% 40% at 50% 115%,rgba(0,0,0,.10),rgba(0,0,0,0) 70%),
      linear-gradient(180deg,rgba(255,255,255,.10),rgba(190,215,235,.14));
    box-shadow:0 7px 10px rgba(0,0,0,.25),0 0 0 6px rgba(255,255,255,.45),0 0 0 7px rgba(0,0,0,.08),
      inset 0 0 0 4px rgba(255,255,255,.45),inset -10px -12px 18px rgba(0,0,0,.14)}
  .dome::after{content:"";position:absolute;right:26px;top:14px;width:13px;height:46px;border-radius:8px;
    background:linear-gradient(180deg,rgba(255,255,255,.9),rgba(255,255,255,.2));transform:rotate(20deg)}
  .dome::before{content:"";position:absolute;left:22px;bottom:14px;width:40px;height:8px;border-radius:6px;
    background:rgba(255,255,255,.55);transform:rotate(-8deg)}
  /* rebord thermoscellé sur le grand compartiment */
  .main{outline:6px solid rgba(255,255,255,.10);outline-offset:4px}
"""
if ".dome{" not in s:
    s = s.replace("  .label{", css + "\n  .label{", 1)

# 3) insérer une coque dans chaque petit compartiment (avant le reflet)
parts = s.split('<div class="bub side"')
for i in range(1, len(parts)):
    if '<div class="dome"></div>' not in parts[i].split('</div>\n\n')[0]:
        parts[i] = parts[i].replace('<div class="gloss"></div>', '<div class="dome"></div>\n      <div class="gloss"></div>', 1)
s = '<div class="bub side"'.join(parts)

open(p, "w", encoding="utf-8").write(s)
print("toon restant:", "toon" in s, "| domes:", s.count('<div class="dome"></div>'))
