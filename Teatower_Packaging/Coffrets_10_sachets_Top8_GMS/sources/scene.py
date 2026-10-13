# -*- coding: utf-8 -*-
"""Rendus de présentation : (1) photo de groupe des 8 coffrets, (2) display 1-8 Eco garni.
Usage : scene.py <dossier boxes> <sortie_dir>"""
import base64, io, json, os, sys
from PIL import Image

BOX, OUT = sys.argv[1], sys.argv[2]
ORDER = ["279", "832", "735", "631", "880", "751", "628", "723"]
CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_parts", "boxes.json"), encoding="utf-8"))
PX = [115.2, 205.2, 295.2, 385.2]
PW = [90, 90, 90, 89.5]


def b64(im, q=None):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def faces(k, maxw=520):
    body = Image.open(os.path.join(BOX, k, "C0196_PRINT_0.png")).convert("RGB")
    lid = Image.open(os.path.join(BOX, k, "C0196_PRINT_1.png")).convert("RGB")
    sb, sl = body.width / 567.3125, lid.width / 336.598

    def c(im, s, x0, y0, x1, y1):
        r = im.crop((round(x0 * s), round(y0 * s), round(x1 * s), round(y1 * s)))
        if r.width > maxw:
            r = r.resize((maxw, round(r.height * maxw / r.width)))
        return b64(r), r.size

    f = {"panel": [c(body, sb, PX[i], 68.2, PX[i] + PW[i], 123.2) for i in range(4)],
         "top": c(lid, sl, 148.1, 121.9, 242.1, 217.1),
         "front": c(lid, sl, 148.1, 217.1, 242.1, 252.1)}
    r = lid.crop((round(242.1 * sl), round(122.5 * sl), round(277.1 * sl), round(216.5 * sl))).transpose(Image.TRANSPOSE).transpose(Image.FLIP_LEFT_RIGHT)
    r = r.resize((maxw, round(r.height * maxw / r.width)))
    f["right"] = (b64(r), r.size)
    return f


F = {k: faces(k) for k in ORDER}


class Proj:
    def __init__(self, ux, uy, uz):
        self.ux, self.uy, self.uz = ux, uy, uz

    def P(self, x, y, z, ox, oy):
        return (ox + x * self.ux[0] + y * self.uy[0] + z * self.uz[0], oy + x * self.ux[1] + y * self.uy[1] + z * self.uz[1])

    def img(self, im, origin, A, La, B, Lb, ox, oy, shade=0, light=0):
        (href, (w, h)) = im
        o = self.P(*origin, ox, oy)
        a = (A[0] * La / w, A[1] * La / w)
        c = (B[0] * Lb / h, B[1] * Lb / h)
        s = f'<g transform="matrix({a[0]:.5f} {a[1]:.5f} {c[0]:.5f} {c[1]:.5f} {o[0]:.2f} {o[1]:.2f})"><image href="{href}" width="{w}" height="{h}" preserveAspectRatio="none"/>'
        if shade: s += f'<rect width="{w}" height="{h}" fill="#000" opacity="{shade}"/>'
        if light: s += f'<rect width="{w}" height="{h}" fill="#fff" opacity="{light}"/>'
        return s + "</g>"

    def poly(self, pts, ox, oy, fill, extra=""):
        q = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.P(*p, ox, oy) for p in pts))
        return f'<polygon points="{q}" fill="{fill}" {extra}/>'


LW, LD, LH, BH = 94.0, 95.2, 35.0, 90.0


def box(pr, f, front_i, right_i, x, y, z, ox, oy, top=True):
    """Coffret fermé dont le coin avant-gauche-bas du couvercle est en (x,y,z)."""
    down = (-pr.uz[0], -pr.uz[1])
    ix, iy = 2.0, 2.6
    s = [pr.img(f["panel"][front_i], (x + ix, y + iy, z + 55), pr.ux, 90, down, 55, ox, oy),
         pr.img(f["panel"][right_i], (x + ix + 90, y + iy, z + 55), pr.uy, 90, down, 55, ox, oy, shade=.16)]
    p1, p2, p3 = pr.P(x + ix, y + iy, z + 55, ox, oy), pr.P(x + ix + 90, y + iy, z + 55, ox, oy), pr.P(x + ix + 90, y + iy + 90, z + 55, ox, oy)
    s.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f} L{p3[0]:.1f},{p3[1]+6:.1f} L{p2[0]:.1f},{p2[1]+6:.1f} L{p1[0]:.1f},{p1[1]+6:.1f}Z" fill="url(#lidshadow)" opacity=".45"/>')
    s.append(pr.img(f["front"], (x, y, z + BH), pr.ux, LW, down, LH, ox, oy))
    s.append(pr.img(f["right"], (x + LW, y, z + BH), pr.uy, LD, down, LH, ox, oy, shade=.16))
    if top:
        s.append(pr.img(f["top"], (x, y + LD, z + BH), pr.ux, LW, (-pr.uy[0], -pr.uy[1]), LD, ox, oy, light=.05))
    return "".join(s)


DEFS = '''<defs>
 <radialGradient id="bg" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#FBF7F2"/><stop offset="1" stop-color="#E7DCD1"/></radialGradient>
 <linearGradient id="lidshadow" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>
 <filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
 <filter id="blur2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>'''


import re as _re
_LOGO = open(r"C:/Users/FlowUP/OneDrive/Teatower/brand/Teatower_logo_compact.svg", encoding="utf-8").read()
_LVB = _re.search(r'viewBox="([^"]+)"', _LOGO).group(1)
_LIN = _re.search(r"<svg[^>]*>(.*)</svg>", _LOGO, _re.S).group(1)


def logo(x, y, w, col="#1E1A18"):
    vb = [float(v) for v in _LVB.split()]
    return f'<svg x="{x}" y="{y}" width="{w}" height="{w*vb[3]/vb[2]:.2f}" viewBox="{_LVB}" fill="{col}">{_LIN}</svg>'


FONTCSS = open(os.path.join(OUT, "fonts_local.css"), encoding="utf-8").read()


def html(svg, w, h):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTCSS} html,body{{margin:0;background:#fff}}</style></head><body>{svg}</body></html>'


# ---------- (1) photo de groupe ----------
K = 2.45
pr = Proj((0.95 * K, 0.22 * K), (0.55 * K, -0.36 * K), (0, -K))
W, H = 2400, 1350
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}<rect width="{W}" height="{H}" fill="url(#bg)"/>',
     f'<rect y="{H*0.62:.0f}" width="{W}" height="{H*0.38:.0f}" fill="#E0D3C6" opacity=".55"/>']
# rangée arrière (4) puis rangée avant (4), décalées
rows = [(ORDER[4:], 330, 820, 3), (ORDER[:4], 150, 1215, 3)]
for keys, x0, y0, fi in rows:
    for j, k in enumerate(keys):
        ox, oy = x0 + j * 540, y0
        c = pr.P(LW / 2, LD / 2, 0, ox, oy)
        s.append(f'<ellipse cx="{c[0]+18:.1f}" cy="{c[1]+14:.1f}" rx="250" ry="62" fill="#3a2a22" opacity=".18" filter="url(#blur)"/>')
        s.append(box(pr, F[k], fi, 0, 0, 0, 0, ox, oy))
s.append("</svg>")
open(os.path.join(OUT, "groupe.html"), "w", encoding="utf-8").write(html("".join(s), W, H))

# ---------- (2) display 1-8 Eco ----------
# Cotes Prodigital (plan 23/03/2026) : dos 301 × 1360 mm, profondeur ≈ 390 mm, étagères tous les ≈ 310 mm,
# fronton 317 mm de large ; 2 piles de 3 coffrets par étagère.
DW, DD, DHt = 301.0, 390.0, 1360.0
SHELVES = [254.0, 570.0, 879.0, 1189.0]
LIP = 42.0
RED, REDD, REDL = "#DF4A40", "#B8342C", "#F08A7C"
K2 = 0.78
pd = Proj((0.97 * K2, 0.16 * K2), (0.50 * K2, -0.30 * K2), (0, -K2))
W2, H2 = 1500, 1650
ox, oy = 500, 1500
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}">{DEFS}<rect width="{W2}" height="{H2}" fill="url(#bg)"/>',
     f'<rect y="{oy-60}" width="{W2}" height="{H2-oy+60}" fill="#E0D3C6" opacity=".55"/>']
c = pd.P(DW / 2, DD / 2, 0, ox, oy)
s.append(f'<ellipse cx="{c[0]+30:.1f}" cy="{c[1]+10:.1f}" rx="300" ry="70" fill="#3a2a22" opacity=".22" filter="url(#blur)"/>')
# dos (intérieur) et flanc gauche (intérieur)
s.append(pd.poly([(0, DD, 0), (DW, DD, 0), (DW, DD, DHt), (0, DD, DHt)], ox, oy, "#C93E35"))
s.append(pd.poly([(0, 0, 0), (0, DD, 0), (0, DD, DHt), (0, 0, DHt)], ox, oy, "#B5362E"))
# pied (sous la 1re étagère)
s.append(pd.poly([(0, 0, 0), (DW, 0, 0), (DW, 0, SHELVES[0]), (0, 0, SHELVES[0])], ox, oy, RED))
pa = pd.P(DW / 2, 0, SHELVES[0] * .55, ox, oy)
s.append(f'<g transform="translate({pa[0]:.1f},{pa[1]:.1f}) skewY(9.4)"><rect x="-58" y="-34" width="116" height="62" rx="6" fill="#FFF6EE"/>'
         f'<text x="0" y="-6" font-family="Poppins" font-weight="700" font-size="17" fill="{REDD}" text-anchor="middle">COFFRETS</text>'
         f'<text x="0" y="16" font-family="Poppins" font-weight="600" font-size="13" fill="#4A2E1F" text-anchor="middle">10 sachets</text></g>')
PLAN = [("279", "832"), ("735", "631"), ("880", "751"), ("628", "723")][::-1]   # du bas vers le haut
for lvl, z in enumerate(SHELVES):
    # plateau
    s.append(pd.poly([(0, 0, z), (DW, 0, z), (DW, DD, z), (0, DD, z)], ox, oy, "#F2D9CF"))
    keys = PLAN[lvl]
    for j, k in enumerate(keys):
        bx = 18 + j * 157
        for h in range(2):
            s.append(box(pd, F[k], 1, 2, bx, 14, z + h * (BH + .5), ox, oy, top=(h == 1)))
    # bandeau de tablette (lèvre avant) avec les noms
    s.append(pd.poly([(0, 0, z), (DW, 0, z), (DW, 0, z - LIP), (0, 0, z - LIP)], ox, oy, "#FFF6EE", f'stroke="{REDD}" stroke-width="1"'))
    for j, k in enumerate(keys):
        tx, ty = pd.P(18 + j * 157 + 47, 0, z - LIP * .58, ox, oy)
        s.append(f'<text transform="translate({tx:.1f},{ty:.1f}) skewY(9.4)" font-family="Playfair Display" font-weight="700" font-size="7.6" fill="#4A2E1F" text-anchor="middle">{CFG[k]["name"]}</text>')
# flanc droit extérieur (par-dessus le contenu)
s.append(pd.poly([(DW, 0, 0), (DW, DD, 0), (DW, DD, DHt), (DW, 0, DHt)], ox, oy, RED))
s.append(pd.poly([(DW, 0, 0), (DW, DD, 0), (DW, DD, 330), (DW, 0, 330)], ox, oy, REDL, 'opacity=".35"'))
# logo + drapeau + mentions sur le flanc (texte plaqué via matrice)
o = pd.P(DW, 0, DHt, ox, oy)
mA = (pd.uy[0], pd.uy[1])
mB = (0, K2)
s.append(f'<g transform="matrix({mA[0]:.4f} {mA[1]:.4f} {mB[0]:.4f} {mB[1]:.4f} {o[0]:.1f} {o[1]:.1f})">'
         f'<path d="M95,120 h110 v110 h-95 a15,15 0 0 1 -15,-15Z" fill="#FFF6EE"/>'
         + logo(105, 130, 90) +
         f'<rect x="122" y="290" width="18.7" height="38" fill="#000"/><rect x="140.7" y="290" width="18.7" height="38" fill="#FDDA24"/><rect x="159.4" y="290" width="18.6" height="38" fill="#EF3340"/>'
         f'<text x="150" y="372" font-family="Poppins" font-weight="600" font-size="19" fill="#FFF6EE" text-anchor="middle">Marque belge</text>'
         f'<text x="150" y="396" font-family="Poppins" font-size="15" fill="#FFF6EE" text-anchor="middle">créatrice de thés</text>'
         f'<text x="150" y="416" font-family="Poppins" font-size="15" fill="#FFF6EE" text-anchor="middle">et d’infusions</text>'
         f'<text x="150" y="560" font-family="Caveat" font-weight="600" font-size="40" fill="#FFF6EE" text-anchor="middle">Coffrets</text>'
         f'<text x="150" y="596" font-family="Caveat" font-weight="600" font-size="40" fill="#FFF6EE" text-anchor="middle">10 sachets</text>'
         f'<text x="150" y="1150" font-family="Poppins" font-size="16" fill="#FFF6EE" text-anchor="middle">Un ingrédient que vous aimez.</text>'
         f'<text x="150" y="1172" font-family="Poppins" font-size="16" fill="#FFF6EE" text-anchor="middle">Une recette que vous n’attendiez pas.</text></g>')
# fronton
HW, HH = 317.0, 300.0
hx = (DW - HW) / 2
s.append(pd.poly([(hx, 0, DHt), (hx + HW, 0, DHt), (hx + HW, 0, DHt + HH), (hx, 0, DHt + HH)], ox, oy, RED, f'stroke="{REDD}" stroke-width="1.2"'))
o = pd.P(hx, 0, DHt + HH, ox, oy)
mA = (pd.ux[0], pd.ux[1])
s.append(f'<g transform="matrix({mA[0]:.4f} {mA[1]:.4f} 0 {K2} {o[0]:.1f} {o[1]:.1f})">'
         f'<path d="M108,26 h100 v100 h-86 a14,14 0 0 1 -14,-14Z" fill="#FFF6EE"/>'
         + logo(117, 36, 82) +
         f'<rect x="228" y="34" width="12" height="24" fill="#000"/><rect x="240" y="34" width="12" height="24" fill="#FDDA24"/><rect x="252" y="34" width="12" height="24" fill="#EF3340"/>'
         f'<text x="158" y="180" font-family="Caveat" font-weight="600" font-size="46" fill="#FFF6EE" text-anchor="middle">Nos coffrets</text>'
         f'<text x="158" y="222" font-family="Poppins" font-weight="600" font-size="20" fill="#FFF6EE" text-anchor="middle" letter-spacing="1.5">10 SACHETS</text>'
         f'<text x="158" y="250" font-family="Poppins" font-size="14" fill="#FFF6EE" text-anchor="middle">Thés &amp; infusions</text></g>')
s.append("</svg>")
open(os.path.join(OUT, "display.html"), "w", encoding="utf-8").write(html("".join(s), W2, H2))
print("scenes ok")
