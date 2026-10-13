src = open("build_c0196.py", encoding="utf-8").read()
a = src.index('items = [("La nana de Wépion"')
b = src.index('body.append("</g>")', a)
new = '''ACC = RED
mid = x0 + 45
body.append(f'<text x="{tagx+17}" y="{tagy+29}" font-family="Caveat" font-weight="600" font-size="13" fill="{ACC}" text-anchor="middle">10×</text>')
body.append(f'<text x="{tagx+30}" y="{tagy+21.4}" font-family="Playfair Display" font-weight="700" font-size="4.3" fill="{BROWN}">Le panier</text>')
body.append(f'<text x="{tagx+30}" y="{tagy+26.6}" font-family="Playfair Display" font-weight="700" font-size="4.3" fill="{BROWN}">de grand-maman</text>')
body.append(f'<text x="{tagx+30}" y="{tagy+30.8}" font-family="Poppins" font-size="2.5" fill="#8A6A55" letter-spacing=".15">INFUSION DE FRUITS</text>')
body.append(strawberry(tagx + 9, tagy + 35.6, .62) + strawberry(tagx + tagw - 9, tagy + 35.6, .62))
body.append(f'<text x="{mid}" y="{tagy+36.6}" font-family="Poppins" font-size="2.75" fill="{BROWN}" text-anchor="middle">Fraise · Mûre · Cassis · Framboise</text>')
body.append(f'<text x="{mid}" y="{tagy+tagh-2.6}" font-family="Playfair Display" font-style="italic" font-weight="500" font-size="2.6" fill="#8A6A55" text-anchor="middle">10 sachets d’infusion</text>')
'''
src = src[:a] + new + src[b:]
for o, n in [('>THÉS &amp; INFUSIONS</text>\')', '>INFUSION DE FRUITS</text>\')'),
             ('THÉS &amp; INFUSIONS FAITS AVEC AMOUR', 'INFUSION DE FRUITS FAITE AVEC AMOUR')]:
    assert o in src, o; src = src.replace(o, n)
open("build_c0196.py", "w", encoding="utf-8").write(src)
m = open("mkv2.py", encoding="utf-8").read()
if "ACC = RED" not in m:
    m = m.replace(" ('font-size=\"7\" fill=\"{RED}\"", " ('ACC = RED', 'ACC = CORALD'),\n ('font-size=\"7\" fill=\"{RED}\"", 1)
    open("mkv2.py", "w", encoding="utf-8").write(m)
print("patched", src.count("INFUSION DE FRUITS"))
