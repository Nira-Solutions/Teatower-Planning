# -*- coding: utf-8 -*-
"""Saveurs en visuels principaux + drapeau belge + suppression « Dans mon panier »."""
src = open("build_c0196.py", encoding="utf-8").read()

FRUITS = r'''

# ---------- fruits (saveurs principales) ----------
def _drupes(cx, cy, s, rows, col, dark, hi, r=.62):
    g = [f'<g transform="translate({cx},{cy}) scale({s})">']
    n = len(rows)
    for k, w in enumerate(rows):
        y = -3.0 + k * 6.2 / (n - 1)
        m = max(1, round(w / 1.15))
        for j in range(m):
            x = -w / 2 + (j + .5) * w / m
            g.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{col}" stroke="{dark}" stroke-width=".12"/>')
            g.append(f'<circle cx="{x-.2:.2f}" cy="{y-.22:.2f}" r="{r*.28:.2f}" fill="{hi}" opacity=".7"/>')
    g.append(f'<path d="M-2,-3.6 L-.7,-3.2 L0,-4.4 L.7,-3.2 L2,-3.6 L.9,-2.7 L0,-2.9 L-.9,-2.7Z" fill="{LEAF}"/>')
    g.append('</g>')
    return "".join(g)


def raspberry(cx, cy, s=1):
    return _drupes(cx, cy, s, [4.6, 5.8, 6.2, 5.8, 4.8, 3.2], "#D8355A", "#A51E40", "#FFFFFF")


def blackberry(cx, cy, s=1):
    return _drupes(cx, cy, s, [4.2, 5.4, 5.8, 5.8, 5.4, 4.4, 2.8], "#3B1A3E", "#1E0B20", "#9C7AB0")


def cassis(cx, cy, s=1):
    g = [f'<g transform="translate({cx},{cy}) scale({s})">']
    g.append(leaf(-.6, -3.6, -150, 3.4) + leaf(-.4, -3.8, -100, 3.8) + leaf(0, -3.6, -40, 3.2))
    g.append(f'<path d="M0,-3.4 C.2,-1.5 -.4,0 -1.6,1.6 M0,-2 C1,-1 2,-.4 2.6,.8 M-.2,-1.2 C.6,0 .6,1.2 .4,2.4" stroke="{LEAFD}" stroke-width=".25" fill="none"/>')
    for x, y in [(-1.9, 1.7), (.4, 2.5), (2.6, 1.0), (-.6, -.1), (1.5, -.9)]:
        g.append(f'<circle cx="{x}" cy="{y}" r="1.3" fill="#2B1433" stroke="#140818" stroke-width=".1"/>')
        g.append(f'<circle cx="{x-.4}" cy="{y-.4}" r=".32" fill="#8C6EA0" opacity=".8"/>')
        g.append(f'<circle cx="{x+.15}" cy="{y+1.05}" r=".22" fill="#140818"/>')
    g.append('</g>')
    return "".join(g)


def fruit_icon(name, cx, cy, s=1):
    if name == "Fraise":
        return strawberry(cx, cy + .2 * s, .9 * s)
    if name == "Framboise":
        return raspberry(cx, cy + .3 * s, .75 * s)
    if name == "Mûre":
        return blackberry(cx, cy + .3 * s, .7 * s)
    return cassis(cx, cy + .2 * s, .85 * s)


def ribbon(cx, cy, w, h, a, b):
    x0, x1 = cx - w / 2, cx + w / 2
    t = h * .55
    return (f'<path d="M{x0-t},{cy-h/2+1.2} L{x0+1},{cy-h/2+1.2} L{x0+1},{cy+h/2+1.2} L{x0-t},{cy+h/2+1.2} L{x0-t+2.2},{cy+1.2}Z" fill="{ACC}"/>'
            f'<path d="M{x1+t},{cy-h/2+1.2} L{x1-1},{cy-h/2+1.2} L{x1-1},{cy+h/2+1.2} L{x1+t},{cy+h/2+1.2} L{x1+t-2.2},{cy+1.2}Z" fill="{ACC}"/>'
            f'<rect x="{x0}" y="{cy-h/2}" width="{w}" height="{h}" rx=".8" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".4"/>'
            f'<text x="{cx}" y="{cy+h*.2:.2f}" font-family="Playfair Display" font-weight="700" font-size="{h*.56:.2f}" fill="{BROWN}" text-anchor="middle">{a} <tspan fill="{ACC}" font-style="italic">&amp;</tspan> {b}</text>')


_FLAG_N = [0]


def flag_round(cx, cy, r, ring="#FFFFFF"):
    _FLAG_N[0] += 1
    i = _FLAG_N[0]
    w = 2 * r / 3
    return (f'<clipPath id="fl{i}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<circle cx="{cx}" cy="{cy}" r="{r+.55}" fill="{ring}"/>'
            f'<g clip-path="url(#fl{i})"><rect x="{cx-r}" y="{cy-r}" width="{w+.05:.3f}" height="{2*r}" fill="#000000"/>'
            f'<rect x="{cx-r+w:.3f}" y="{cy-r}" width="{w+.05:.3f}" height="{2*r}" fill="#FDDA24"/>'
            f'<rect x="{cx-r+2*w:.3f}" y="{cy-r}" width="{w:.3f}" height="{2*r}" fill="#EF3340"/></g>')


def flag_rect(x, y, w, h):
    t = w / 3
    return (f'<rect x="{x}" y="{y}" width="{t+.03:.3f}" height="{h}" fill="#000"/><rect x="{x+t:.3f}" y="{y}" width="{t+.03:.3f}" height="{h}" fill="#FDDA24"/>'
            f'<rect x="{x+2*t:.3f}" y="{y}" width="{t:.3f}" height="{h}" fill="#EF3340"/>')


def tricolore_line(x0, x1, y, h=1.0, seg=3.0):
    s = []
    x, k = x0, 0
    cols = ["#000000", "#FDDA24", "#EF3340"]
    while x < x1:
        w = min(seg, x1 - x)
        s.append(f'<rect x="{x:.2f}" y="{y}" width="{w+.02:.2f}" height="{h}" fill="{cols[k%3]}"/>')
        x += seg; k += 1
    return "".join(s)

'''
src = src.replace("\n# ---------- EAN-13 ----------", FRUITS + "\n# ---------- EAN-13 ----------", 1)

# --- panneaux 1 / 2 / 3 ---
a = src.index("# Panneau 1 : panier")
b = src.index("# Panneau 4 : logo")
PANELS = '''ACC = RED
TXT = BROWN
# Panneau 1 : fraise & framboise
p = PX[0]
body.append(leaf(p + 44, 99, -160, 11) + leaf(p + 46, 99, -20, 11) + leaf(p + 45, 100, -95, 9, LEAFD))
body.append(strawberry(p + 31, 89.5, 3.4) + raspberry(p + 60, 91.5, 2.25))
body.append(ribbon(p + 45, 112, 66, 8.6, "Fraise", "Framboise"))
# Panneau 2 : étiquette produit
x0 = PX[1]
mid = x0 + 45
tagx, tagy, tagw, tagh = x0 + 9, 74.5, 72, 44
body.append(f'<path d="M{mid},{LIDLINE+0.4} L{mid},{tagy+3}" stroke="#A9814C" stroke-width=".7"/>')
body.append(f'<rect x="{tagx}" y="{tagy}" width="{tagw}" height="{tagh}" rx="2" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".6" transform="rotate(-1.2 {tagx+tagw/2} {tagy+tagh/2})"/>')
body.append(f'<g transform="rotate(-1.2 {tagx+tagw/2} {tagy+tagh/2})">')
body.append(f'<circle cx="{mid}" cy="{tagy+3}" r="1.1" fill="{CREAM}" stroke="{KRAFT}" stroke-width=".5"/>')
body.append(f'<text x="{mid}" y="{tagy+10.4}" font-family="Caveat" font-weight="600" font-size="6.6" fill="{ACC}" text-anchor="middle">Le panier de grand-maman</text>')
body.append(f'<text x="{mid}" y="{tagy+14.6}" font-family="Poppins" font-weight="600" font-size="2.35" letter-spacing=".25" fill="#8A6A55" text-anchor="middle">INFUSION DE FRUITS · 10 SACHETS</text>')
body.append(f'<line x1="{tagx+10}" x2="{tagx+tagw-10}" y1="{tagy+16.6}" y2="{tagy+16.6}" stroke="{KRAFT}" stroke-width=".4" stroke-dasharray="1 .8"/>')
for k, name in enumerate(["Fraise", "Mûre", "Cassis", "Framboise"]):
    col, row = k % 2, k // 2
    ix_ = tagx + 7.5 + col * 33
    iy_ = tagy + 24 + row * 8.6
    body.append(fruit_icon(name, ix_, iy_, 1.05))
    body.append(f'<text x="{ix_+5}" y="{iy_+1.7:.2f}" font-family="Playfair Display" font-weight="700" font-size="4.9" fill="{BROWN}">{name}</text>')
fy_ = tagy + tagh - 4.4
body.append(flag_rect(tagx + 8.2, fy_ - 2.05, 3.9, 2.6))
body.append(f'<text x="{tagx+13.4}" y="{fy_}" font-family="Poppins" font-size="2.1" fill="{BROWN}">Marque belge créatrice de thés et d’infusions</text>')
body.append("</g>")
# Panneau 3 : mûre & cassis
p = PX[2]
body.append(leaf(p + 44, 99, -160, 11) + leaf(p + 46, 99, -20, 11) + leaf(p + 45, 100, -95, 9, LEAFD))
body.append(blackberry(p + 31, 90.5, 2.55) + cassis(p + 60, 92, 2.7))
body.append(ribbon(p + 45, 112, 60, 8.6, "Mûre", "Cassis"))
'''
src = src[:a] + PANELS + src[b:]

# --- panneau 4 : badge drapeau + suppression de la marguerite décorative
o = "body.append(heart(c4 + 34.5, by + bw + 10.8, .9, RED, .9))"
assert o in src
src = src.replace(o, o + '''
body.append(flag_round(c4 + bw / 2 + 9, by + 5, 3.3))
body.append(f'<text x="{c4 + bw/2 + 9}" y="{by+12.6}" font-family="Poppins" font-weight="600" font-size="1.95" letter-spacing=".2" fill="{TXT}" text-anchor="middle">MARQUE</text>')
body.append(f'<text x="{c4 + bw/2 + 9}" y="{by+15.1}" font-family="Poppins" font-weight="600" font-size="1.95" letter-spacing=".2" fill="{TXT}" text-anchor="middle">BELGE</text>')''')

# --- liseré tricolore très fin à la base, tout autour
o = "# rabats de fond"
src = src.replace(o, "body.append(tricolore_line(PX[0], PX[3] + PW[3], FOLD - 2.4, 1.0, 3.0))\n" + o, 1)

# --- couvercle : drapeau au-dessus du logo, fruits aux coins, étiquette saveurs sur la face avant
o = "lid.append(lg)"
assert src.count(o) == 1
src = src.replace(o, o + "\nlid.append(flag_round(cx, ly - 4.6, 2.4))", 1)
o = "# nœud de ficelle sur la face avant (twine à 13 mm du bord libre)\nlid.append(bow(195.1, 252.1 - SIDE + 13, 1.0))"
assert o in src
src = src.replace(o, '''# étiquette saveurs + nœud sur la face avant
lid.append(f'<rect x="153" y="233.6" width="62" height="9.6" rx="1.2" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".45"/>')
lid.append(f'<text x="184" y="239.6" font-family="Poppins" font-weight="600" font-size="2.75" letter-spacing=".12" fill="{BROWN}" text-anchor="middle">FRAISE · MÛRE · CASSIS · FRAMBOISE</text>')
lid.append(bow(227, 252.1 - SIDE + 13, .9))''')
o = "lid.append(heart(cx - 18, cy - 12, .6, RED, .6) + heart(cx + 18, cy - 12, .6, RED, .6))"
assert o in src
src = src.replace(o, o + '''
for name, (fx, fy) in zip(["Fraise", "Mûre", "Cassis", "Framboise"], [(FX0 + 9.5, FY0 + 9.5), (FX1 - 9.5, FY0 + 9.5), (FX0 + 9.5, FY1 - 9.5), (FX1 - 9.5, FY1 - 9.5)]):
    lid.append(f'<circle cx="{fx}" cy="{fy}" r="6.2" fill="#FFFDF7" opacity=".92"/>')
    lid.append(fruit_icon(name, fx, fy, 1.25))''')

open("build_c0196.py", "w", encoding="utf-8").write(src)

# --- V2 : retirer le patch « Dans mon panier » (le texte n'existe plus) ; texte du badge en blanc
m = open("mkv2.py", encoding="utf-8").read()
m = m.replace(" ('font-size=\"7\" fill=\"{RED}\" text-anchor=\"middle\">Dans mon panier', 'font-size=\"7\" fill=\"{CORALD}\" text-anchor=\"middle\">Dans mon panier'),\n", "")
if "TXT = BROWN" not in m:
    m = m.replace(" ('ACC = RED', 'ACC = CORALD'),", " ('ACC = RED', 'ACC = CORALD'),\n ('TXT = BROWN', 'TXT = WHITE'),")
open("mkv2.py", "w", encoding="utf-8").write(m)
print("patched v4")
