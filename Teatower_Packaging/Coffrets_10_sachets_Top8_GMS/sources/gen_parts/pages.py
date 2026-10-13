

def ribbon(cx, cy, w, h, a, b=None):
    x0, x1 = cx - w / 2, cx + w / 2
    t = h * .55
    txt = a if b is None else f'{a} <tspan fill="{ACC}" font-style="italic">&amp;</tspan> {b}'
    return (f'<path d="M{x0-t},{cy-h/2+1.2} L{x0+1},{cy-h/2+1.2} L{x0+1},{cy+h/2+1.2} L{x0-t},{cy+h/2+1.2} L{x0-t+2.2},{cy+1.2}Z" fill="{ACC}"/>'
            f'<path d="M{x1+t},{cy-h/2+1.2} L{x1-1},{cy-h/2+1.2} L{x1-1},{cy+h/2+1.2} L{x1+t},{cy+h/2+1.2} L{x1+t-2.2},{cy+1.2}Z" fill="{ACC}"/>'
            f'<rect x="{x0}" y="{cy-h/2}" width="{w}" height="{h}" rx=".8" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".4"/>'
            f'<text x="{cx}" y="{cy+h*.2:.2f}" font-family="Playfair Display" font-weight="700" font-size="{h*.56:.2f}" fill="{BROWN}" text-anchor="middle">{txt}</text>')


def hero(p, names):
    out = [leaf(p + 44, 99, -160, 11) + leaf(p + 46, 99, -20, 11) + leaf(p + 45, 100, -95, 9, LEAFD)]
    if len(names) == 2:
        out.append(ing(names[0], p + 30, 90, 3.15) + ing(names[1], p + 60, 91, 3.15))
        w = max(44, 4.9 * 0.53 * (len(names[0]) + len(names[1]) + 3) + 14)
        out.append(ribbon(p + 45, 112, min(w, 70), 8.6, names[0], names[1]))
    else:
        if names[0] in ("Rooibos", "Thé noir", "Thé vert", "Verveine", "Menthe"):
            out.append(f'<circle cx="{p+45}" cy="90.5" r="17.5" fill="#FFF8EE" opacity=".9"/><circle cx="{p+45}" cy="90.5" r="17.5" fill="none" stroke="{KRAFT}" stroke-width=".5"/>')
        out.append(ing(names[0], p + 45, 90, 3.8))
        w = max(40, 4.9 * 0.55 * len(names[0]) + 18)
        out.append(ribbon(p + 45, 112, w, 8.6, names[0]))
    return "".join(out)


def placeholder_ean(x, y, w, h, sku):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF"/>'
            f'<rect x="{x+6}" y="{y+2}" width="{w-9}" height="{h-7}" fill="none" stroke="#999" stroke-width=".3" stroke-dasharray="1 .8"/>'
            f'<text x="{x+6+(w-9)/2}" y="{y+h/2}" font-family="Poppins" font-weight="600" font-size="2.2" fill="#777" text-anchor="middle">EAN À ATTRIBUER</text>'
            f'<text transform="translate({x+3.6},{y+h-2}) rotate(-90)" font-family="Poppins" font-weight="600" font-size="2.3">{sku}</text>')


# ---------- page 1 : corps ----------
W1, H1 = 567.3125, 260.8636
PX = [115.2, 205.2, 295.2, 385.2]
PW = [90, 90, 90, 89.5]
TOP, FOLD, LIDLINE = 33.2, 123.2, 68.2

body = [f'<rect width="{W1}" height="{H1}" fill="{CORAL}"/>']
body.append(f'<rect x="0" y="{LIDLINE-0.6}" width="{W1}" height=".6" fill="{CORALD}" opacity=".9"/>')
for i in range(64):
    x = 117.5 + i * 5.6
    if x > 472: break
    body.append(f'<circle cx="{x:.2f}" cy="{LIDLINE+2.6}" r=".45" fill="{WHITE}" opacity=".8"/>')

ACC = CORALD
TXT = WHITE
body.append(hero(PX[0], CFG["p1"]))
# Panneau 2 : étiquette produit
x0 = PX[1]
mid = x0 + 45
tagx, tagy, tagw, tagh = x0 + 9, 74.5, 72, 44
body.append(f'<path d="M{mid},{LIDLINE+0.4} L{mid},{tagy+3}" stroke="#A9814C" stroke-width=".7"/>')
body.append(f'<rect x="{tagx}" y="{tagy}" width="{tagw}" height="{tagh}" rx="2" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".6" transform="rotate(-1.2 {tagx+tagw/2} {tagy+tagh/2})"/>')
body.append(f'<g transform="rotate(-1.2 {tagx+tagw/2} {tagy+tagh/2})">')
body.append(f'<circle cx="{mid}" cy="{tagy+3}" r="1.1" fill="{CREAM}" stroke="{KRAFT}" stroke-width=".5"/>')
body.append(f'<text x="{mid}" y="{tagy+10.4}" font-family="Caveat" font-weight="600" font-size="6.6" fill="{ACC}" text-anchor="middle">{CFG["name"]}</text>')
body.append(f'<text x="{mid}" y="{tagy+14.6}" font-family="Poppins" font-weight="600" font-size="2.35" letter-spacing=".25" fill="#8A6A55" text-anchor="middle">{CFG["type"]} · 10 SACHETS</text>')
body.append(f'<line x1="{tagx+10}" x2="{tagx+tagw-10}" y1="{tagy+16.6}" y2="{tagy+16.6}" stroke="{KRAFT}" stroke-width=".4" stroke-dasharray="1 .8"/>')
fl = CFG["flavours"]
if len(fl) == 2:
    slots = [(0, 0.5), (1, 0.5)]
elif len(fl) == 3:
    slots = [(0, 0), (1, 0), (0.5, 1)]
else:
    slots = [(0, 0), (1, 0), (0, 1), (1, 1)]
for name, (col, row) in zip(fl, slots):
    ix_ = tagx + 7.5 + col * 33
    iy_ = tagy + 24 + row * 8.6
    body.append(fruit_icon(name, ix_, iy_, 1.05))
    fsz = min(4.9, 24.5 / (0.56 * len(name)))
    body.append(f'<text x="{ix_+5}" y="{iy_+1.7:.2f}" font-family="Playfair Display" font-weight="700" font-size="{fsz:.2f}" fill="{BROWN}">{name}</text>')
fy_ = tagy + tagh - 4.4
body.append(flag_rect(tagx + 8.2, fy_ - 2.05, 3.9, 2.6))
body.append(f'<text x="{tagx+13.4}" y="{fy_}" font-family="Poppins" font-size="2.1" fill="{BROWN}">Marque belge créatrice de thés et d’infusions</text>')
body.append("</g>")
body.append(hero(PX[2], CFG["p3"]))
# Panneau 4 : logo
c4 = PX[3] + PW[3] / 2
bw = 30
by = 74
body.append(f'<path d="M{c4-bw/2-1.8},{by-1.8} h{bw+3.6} v{bw+3.6} h{-bw-3.6+5.5} a5.5,5.5 0 0 1 -5.5,-5.5Z" fill="{CORALL}"/>')
body.append(f'<path d="M{c4-bw/2},{by} h{bw} v{bw} h{-bw+4} a4,4 0 0 1 -4,-4Z" fill="#FFFFFF"/>')
lg, lh = logo(c4 - 12.5, by + 4.6, 25, INK)
body.append(lg)
body.append(f'<text x="{c4}" y="{by+bw+6.4}" font-family="Playfair Display" font-weight="700" font-size="3.3" letter-spacing=".55" fill="{WHITE}" text-anchor="middle">{CFG["type"]}</text>')
body.append(f'<text x="{c4}" y="{by+bw+13.4}" font-family="Caveat" font-weight="600" font-size="6.2" fill="{WHITE}" text-anchor="middle">{CFG["name"]}</text>')
body.append(flag_round(c4 + bw / 2 + 9, by + 5, 3.3))
body.append(f'<text x="{c4 + bw/2 + 9}" y="{by+12.6}" font-family="Poppins" font-weight="600" font-size="1.95" letter-spacing=".2" fill="{TXT}" text-anchor="middle">MARQUE</text>')
body.append(f'<text x="{c4 + bw/2 + 9}" y="{by+15.1}" font-family="Poppins" font-weight="600" font-size="1.95" letter-spacing=".2" fill="{TXT}" text-anchor="middle">BELGE</text>')
for (x, y, s) in [(PX[0] + 8, 80, .55), (PX[0] + 83, 84, .5), (PX[2] + 82, 79, .5), (PX[1] + 4, 112, .45), (PX[3] + 7, 82, .5), (PX[3] + 82, 92, .5)]:
    body.append(heart(x, y, s, WHITE, .75))
if CFG.get("ean"):
    body.append(ean13_svg(CFG["ean"], 125.6, 128.5, 32.4, 19.6, CFG["sku"]))
else:
    body.append(placeholder_ean(125.6, 128.5, 32.4, 19.6, CFG["sku"]))

# ---------- page 2 : couvercle ----------
W2, H2 = 336.598, 363.033
lid = [f'<rect width="{W2}" height="{H2}" fill="{CORAL}"/>']
FX0, FX1, FY0, FY1 = 148.1, 242.1, 121.9, 217.1
cx, cy = (FX0 + FX1) / 2, (FY0 + FY1) / 2
SIDE = 35


def side_group(length):
    return scallop_strip(length, depth=5.2, r=2.2) + twine(length, -SIDE + 13)


lid.append(f'<g transform="translate(148.7,252.1)">{side_group(92.8)}</g>')
lid.append(f'<g transform="translate(241.5,86.9) rotate(180)">{side_group(92.8)}</g>')
lid.append(f'<g transform="translate(113.1,216.5) rotate(-90) scale(1,-1)">{side_group(94)}</g>')
lid.append(f'<g transform="translate(277.1,122.5) rotate(90) scale(1,-1)">{side_group(94)}</g>')
front = " · ".join(f.upper() for f in fl)
fs_front = 2.75 if len(front) <= 36 else 2.75 * 36 / len(front)
lid.append(f'<rect x="153" y="233.6" width="62" height="9.6" rx="1.2" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".45"/>')
lid.append(f'<text x="184" y="239.6" font-family="Poppins" font-weight="600" font-size="{fs_front:.2f}" letter-spacing=".12" fill="{BROWN}" text-anchor="middle">{front}</text>')
lid.append(bow(227, 252.1 - SIDE + 13, .9))
lid.append(f'''<g transform="rotate(180 195.1 104.4)">
<rect x="160.1" y="96.6" width="70" height="11.2" rx="1.4" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".5"/>
<text x="195.1" y="101.6" font-family="Caveat" font-weight="600" font-size="4.6" fill="{CORALD}" text-anchor="middle">{CFG["back1"]}</text>
<text x="195.1" y="105.6" font-family="Poppins" font-size="2.1" fill="{BROWN}" text-anchor="middle" letter-spacing=".2">{CFG["back2"]}</text>
</g>''')
R = 40
n = 30
lid.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#FFFDF7"/>' + "".join(
    f'<circle cx="{cx+R*math.cos(2*math.pi*i/n):.2f}" cy="{cy+R*math.sin(2*math.pi*i/n):.2f}" r="4.4" fill="#FFFDF7"/>' for i in range(n)))
for i in range(n):
    a = 2 * math.pi * (i + .5) / n
    lid.append(f'<circle cx="{cx+(R-1.2)*math.cos(a):.2f}" cy="{cy+(R-1.2)*math.sin(a):.2f}" r=".9" fill="{CORALD}" opacity=".4"/>')
    a = 2 * math.pi * i / n
    lid.append(f'<circle cx="{cx+(R+1.4)*math.cos(a):.2f}" cy="{cy+(R+1.4)*math.sin(a):.2f}" r="1.25" fill="{CORALD}" opacity=".35"/>')
for i in range(48):
    a = 2 * math.pi * i / 48
    ex, ey = cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a)
    lid.append(f'<ellipse cx="{ex:.2f}" cy="{ey:.2f}" rx="1.6" ry=".55" fill="{CORALD}" opacity=".3" transform="rotate({math.degrees(a):.1f} {ex:.2f} {ey:.2f})"/>')
lid.append(f'<circle cx="{cx}" cy="{cy}" r="{R-9}" fill="none" stroke="{CORALD}" stroke-width=".3" stroke-dasharray="1 .9" opacity=".6"/>')
bw2 = 26
lx, ly = cx - bw2 / 2, cy - 22
lid.append(f'<path d="M{lx-1.5},{ly-1.5} h{bw2+3} v{bw2+3} h{-bw2-3+5} a5,5 0 0 1 -5,-5Z" fill="{CORAL}"/>')
lid.append(f'<path d="M{lx},{ly} h{bw2} v{bw2} h{-bw2+4} a4,4 0 0 1 -4,-4Z" fill="#FFFFFF"/>')
lg, lh = logo(cx - 11, ly + 4, 22, INK)
lid.append(lg)
lid.append(flag_round(cx, ly - 4.6, 2.4))
l1, l2 = CFG["lid_lines"] if len(CFG["lid_lines"]) == 2 else (CFG["lid_lines"][0], None)
if l2:
    lid.append(f'<text x="{cx}" y="{cy+13.2}" font-family="Caveat" font-weight="600" font-size="8.2" fill="{CORALD}" text-anchor="middle">{l1}</text>')
    lid.append(f'<text x="{cx}" y="{cy+20.6}" font-family="Caveat" font-weight="600" font-size="8.2" fill="{CORALD}" text-anchor="middle">{l2}</text>')
else:
    lid.append(f'<text x="{cx}" y="{cy+18.4}" font-family="Caveat" font-weight="600" font-size="10" fill="{CORALD}" text-anchor="middle">{l1}</text>')
lid.append(f'<text x="{cx}" y="{cy+26.2}" font-family="Playfair Display" font-weight="700" font-size="2.4" letter-spacing=".5" fill="{BROWN}" text-anchor="middle">{CFG["type"]}</text>')
tw = 2.4 * 0.62 * len(CFG["type"]) / 2 + 3.5
lid.append(leaf(cx - tw, cy + 26, 200, 3.0) + daisy(cx - tw - 2.8, cy + 25.3, 1.8) + leaf(cx + tw, cy + 26, -20, 3.0) + daisy(cx + tw + 2.8, cy + 25.3, 1.8))
lid.append(heart(cx - 18, cy - 12, .6, CORAL, .8) + heart(cx + 18, cy - 12, .6, CORAL, .8))
corner = (fl * 4)[:4]
for name, (fx, fy) in zip(corner, [(FX0 + 9.5, FY0 + 9.5), (FX1 - 9.5, FY0 + 9.5), (FX0 + 9.5, FY1 - 9.5), (FX1 - 9.5, FY1 - 9.5)]):
    lid.append(f'<circle cx="{fx}" cy="{fy}" r="6.2" fill="#FFFDF7" opacity=".92"/>')
    lid.append(fruit_icon(name, fx, fy, 1.25))

FONTCSS = open(os.path.join(OUT, "fonts_local.css"), encoding="utf-8").read()


def page(w, h, content, name):
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONTCSS}
@page {{ size: {w}mm {h}mm; margin: 0; }}
html,body {{ margin:0; padding:0; }}
svg.p {{ display:block; width:{w}mm; height:{h}mm; }}
</style></head><body><svg class="p" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{DEFS}{"".join(content)}</svg></body></html>'''
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(html)


page(W1, H1, body, "corps.html")
page(W2, H2, lid, "couvercle.html")
print("ok", CFG["sku"])
