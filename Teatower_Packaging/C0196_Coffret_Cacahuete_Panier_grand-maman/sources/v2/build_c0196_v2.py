# -*- coding: utf-8 -*-
"""C0196 Coffret Cacahuète 2026 — version « Panier de grand-maman ».
Génère 2 HTML (corps + couvercle) aux dimensions exactes du gabarit Giftbox 2026,
coordonnées en mm (origine haut-gauche de la page, fond perdu = page entière)."""
import math, os, re, sys

OUT = sys.argv[1]
LOGO_SVG = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# ---------- palette (V2 : corail du doypack 279) ----------
CREAM = "#F7EEDC"
CREAM2 = "#E27A6B"
CORAL = "#EC8475"
CORALD = "#D9624F"
CORALL = "#F6B3A8"
INK = "#1E1A18"
WHITE = "#FFF8F2"
RED = "#C8242F"
REDD = "#9E1B26"
BROWN = "#4A2E1F"
WICK = "#B57E45"
WICKD = "#8A5A2E"
WICKL = "#D7A468"
KRAFT = "#D9B584"
LEAF = "#5F8150"
LEAFD = "#3F5E36"
GOLD = "#C49A55"
LAV = "#8B7BB8"

logo_raw = open(LOGO_SVG, encoding="utf-8").read()
logo_vb = re.search(r'viewBox="([^"]+)"', logo_raw).group(1)
logo_inner = re.search(r"<svg[^>]*>(.*)</svg>", logo_raw, re.S).group(1)
logo_inner = re.sub(r"<title>.*?</title>", "", logo_inner)


def logo(x, y, w, color):
    vb = [float(v) for v in logo_vb.split()]
    h = w * vb[3] / vb[2]
    return f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" viewBox="{logo_vb}" style="color:{color}" fill="{color}">{logo_inner}</svg>', h


DEFS = f"""
<defs>
  <pattern id="vichy" width="5" height="5" patternUnits="userSpaceOnUse">
    <rect width="5" height="5" fill="#FBF6EC"/>
    <rect width="2.5" height="5" fill="{CORALD}" opacity=".55"/>
    <rect width="5" height="2.5" fill="{CORALD}" opacity=".55"/>
  </pattern>
  <pattern id="vichyS" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="3" fill="#FBF6EC"/>
    <rect width="1.5" height="3" fill="{RED}" opacity=".45"/>
    <rect width="3" height="1.5" fill="{RED}" opacity=".45"/>
  </pattern>
  <pattern id="wicker" width="6" height="4" patternUnits="userSpaceOnUse">
    <rect width="6" height="4" fill="{WICKD}"/>
    <ellipse cx="1.5" cy="1" rx="1.6" ry=".85" fill="{WICK}"/>
    <ellipse cx="4.5" cy="3" rx="1.6" ry=".85" fill="{WICK}"/>
    <ellipse cx="1.2" cy=".8" rx=".8" ry=".3" fill="{WICKL}" opacity=".8"/>
    <ellipse cx="4.2" cy="2.8" rx=".8" ry=".3" fill="{WICKL}" opacity=".8"/>
  </pattern>
  <pattern id="paper" width="7" height="7" patternUnits="userSpaceOnUse">
    <rect width="7" height="7" fill="{CORAL}"/>
    <circle cx="1.3" cy="2.1" r=".18" fill="{CREAM2}"/>
    <circle cx="4.9" cy="5.6" r=".22" fill="{CREAM2}"/>
    <circle cx="5.6" cy="1.0" r=".14" fill="{CREAM2}"/>
  </pattern>
  <linearGradient id="ttred" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0" stop-color="#B71C31"/><stop offset="1" stop-color="#E8273F"/>
  </linearGradient>
  <linearGradient id="glass" x1="0" x2="1">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/>
    <stop offset=".35" stop-color="#FFFFFF" stop-opacity=".15"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity=".35"/>
  </linearGradient>
</defs>
"""


# ---------- motifs ----------
def scallop_strip(length, depth=4.2, r=2.1, color="#FFFDF7", holes=True):
    """Dentelle : bande qui part du bord (y=0) vers l'intérieur (y négatif), festons côté intérieur."""
    n = max(1, round(length / (2 * r)))
    rr = length / n / 2
    s = [f'<rect x="0" y="{-depth + rr:.2f}" width="{length:.2f}" height="{depth - rr:.2f}" fill="{color}"/>']
    for i in range(n):
        cx = rr + 2 * rr * i
        s.append(f'<circle cx="{cx:.2f}" cy="{-depth + rr:.2f}" r="{rr:.2f}" fill="{color}"/>')
        if holes:
            s.append(f'<circle cx="{cx:.2f}" cy="{-depth + rr:.2f}" r="{rr*0.32:.2f}" fill="{CORALD}" opacity=".45"/>')
    s.append(f'<line x1="0" x2="{length:.2f}" y1="{-0.9:.2f}" y2="{-0.9:.2f}" stroke="{CORALD}" stroke-width=".25" stroke-dasharray=".8 .6" opacity=".7"/>')
    return "".join(s)


def twine(length, y):
    return (f'<line x1="-1" x2="{length+1:.2f}" y1="{y}" y2="{y}" stroke="#A9814C" stroke-width="1.5"/>'
            f'<line x1="-1" x2="{length+1:.2f}" y1="{y}" y2="{y}" stroke="#E2C48F" stroke-width="1.5" stroke-dasharray=".9 .9" opacity=".9"/>')


def bow(cx, cy, s=1.0):
    return f'''<g transform="translate({cx},{cy}) scale({s})">
  <path d="M0,0 C-4,-7 -12,-7 -12,-1 C-12,4 -5,3 0,0Z" fill="#C79A5E" stroke="#8C6532" stroke-width=".5"/>
  <path d="M0,0 C4,-7 12,-7 12,-1 C12,4 5,3 0,0Z" fill="#C79A5E" stroke="#8C6532" stroke-width=".5"/>
  <path d="M-1,1 C-3,5 -5,9 -7,12" stroke="#A9814C" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M1,1 C3,5 4,9 7,11" stroke="#A9814C" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <circle r="1.9" fill="#B88A50" stroke="#8C6532" stroke-width=".5"/>
</g>'''


def heart(cx, cy, s, color=RED, op=1):
    return (f'<path transform="translate({cx},{cy}) scale({s})" opacity="{op}" fill="{color}" '
            f'd="M0,1.6 C-2.6,-0.2 -2.4,-2.6 -1.1,-2.6 C-.4,-2.6 0,-2 0,-1.6 C0,-2 .4,-2.6 1.1,-2.6 C2.4,-2.6 2.6,-.2 0,1.6Z"/>')


def leaf(x, y, ang, L=5, color=LEAF):
    return (f'<path transform="translate({x},{y}) rotate({ang})" fill="{color}" '
            f'd="M0,0 C{L*.35},{-L*.35} {L*.75},{-L*.3} {L},0 C{L*.75},{L*.3} {L*.35},{L*.35} 0,0Z"/>')


def daisy(cx, cy, r=3, heart_col="#E9B53F"):
    s = [f'<g transform="translate({cx},{cy})">']
    for i in range(10):
        a = i * 36
        s.append(f'<ellipse cx="0" cy="{-r*0.62:.2f}" rx="{r*0.22:.2f}" ry="{r*0.5:.2f}" fill="#FFFDF7" stroke="#E6D6B8" stroke-width=".15" transform="rotate({a})"/>')
    s.append(f'<circle r="{r*0.3:.2f}" fill="{heart_col}"/></g>')
    return "".join(s)


def rose(cx, cy, r=2.2, col=RED):
    return (f'<g transform="translate({cx},{cy})"><circle r="{r}" fill="{col}"/>'
            f'<path d="M{-r*.5},0 A{r*.5},{r*.5} 0 1 1 {r*.3},{r*.35} A{r*.25},{r*.25} 0 1 1 0,{-r*.1}" '
            f'fill="none" stroke="{REDD}" stroke-width="{r*.16:.2f}" stroke-linecap="round"/></g>')


def lavender(x, y, h, ang):
    s = [f'<g transform="translate({x},{y}) rotate({ang})">',
         f'<line x1="0" y1="0" x2="0" y2="{-h}" stroke="{LEAFD}" stroke-width=".5"/>']
    for i in range(7):
        yy = -h + i * 1.5
        s.append(f'<ellipse cx="-.7" cy="{yy:.2f}" rx=".75" ry="1.1" fill="{LAV}"/>')
        s.append(f'<ellipse cx=".7" cy="{yy+.6:.2f}" rx=".75" ry="1.1" fill="{LAV}" opacity=".85"/>')
    s.append("</g>")
    return "".join(s)


def strawberry(cx, cy, s=1):
    seeds = "".join(f'<ellipse cx="{dx}" cy="{dy}" rx=".18" ry=".3" fill="#F6D58A"/>'
                    for dx, dy in [(-1, -.5), (.6, -.8), (-.3, .8), (1, .5), (0, -1.6), (-1.3, -1.6), (1.3, -1.7), (.2, 2)])
    return f'''<g transform="translate({cx},{cy}) scale({s})">
<path d="M0,3.6 C-2.8,1.6 -3.2,-1.6 -2.3,-2.6 C-1.4,-3.4 1.4,-3.4 2.3,-2.6 C3.2,-1.6 2.8,1.6 0,3.6Z" fill="{RED}"/>
{seeds}
<path d="M-2.2,-2.6 L-.9,-3.2 L0,-4.3 L.9,-3.2 L2.2,-2.6 L.9,-2.4 L0,-1.9 L-.9,-2.4Z" fill="{LEAF}"/></g>'''


def jam_jar(cx, base, w, h, jam=RED, label="Fraise"):
    x0 = cx - w / 2
    cap_h = h * 0.26
    return f'''<g>
<rect x="{x0:.2f}" y="{base-h:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1.6" fill="{jam}"/>
<rect x="{x0:.2f}" y="{base-h:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1.6" fill="url(#glass)"/>
<rect x="{x0+w*.12:.2f}" y="{base-h*.6:.2f}" width="{w*.76:.2f}" height="{h*.3:.2f}" rx=".6" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".2"/>
<text x="{cx:.2f}" y="{base-h*.6+h*.21:.2f}" font-family="Caveat" font-weight="600" font-size="{h*.2:.2f}" fill="{BROWN}" text-anchor="middle">{label}</text>
<path d="M{x0-1.4:.2f},{base-h+cap_h*.5:.2f} Q{cx:.2f},{base-h-cap_h*1.1:.2f} {x0+w+1.4:.2f},{base-h+cap_h*.5:.2f}
 L{x0+w+0.9:.2f},{base-h+cap_h*.95:.2f} L{x0+w*.75:.2f},{base-h+cap_h*.7:.2f} L{cx:.2f},{base-h+cap_h*1.05:.2f}
 L{x0+w*.25:.2f},{base-h+cap_h*.7:.2f} L{x0-0.9:.2f},{base-h+cap_h*.95:.2f}Z" fill="url(#vichyS)" stroke="{REDD}" stroke-width=".2"/>
<line x1="{x0-.3:.2f}" x2="{x0+w+.3:.2f}" y1="{base-h+cap_h*.55:.2f}" y2="{base-h+cap_h*.55:.2f}" stroke="#A9814C" stroke-width=".7"/>
</g>'''


def basket(cx, base):
    """Panier en osier garni. base = fond du panier (mm)."""
    g = [f'<g transform="translate({cx},{base})">']
    # anse (derrière)
    g.append(f'<path d="M-25,-22 C-25,-49 25,-49 25,-22" fill="none" stroke="{WICKD}" stroke-width="3.6" stroke-linecap="round"/>')
    g.append(f'<path d="M-25,-22 C-25,-49 25,-49 25,-22" fill="none" stroke="{WICKL}" stroke-width="1.4" stroke-dasharray="1.6 1.4" stroke-linecap="round"/>')
    # contenu
    g.append(lavender(-21, -21, 15, -18) + lavender(-18.5, -21, 17, -8) + lavender(-16, -21, 13, 4))
    g.append(jam_jar(-6.5, -23.5, 12, 15, RED, "Fraise"))
    g.append(jam_jar(8.5, -23.5, 10.5, 12, "#4B1E3F", "Mûre"))
    g.append(strawberry(20.5, -24, 1.15) + strawberry(16.5, -21.5, 1.0))
    g.append(leaf(21, -27, -120, 4.5) + leaf(14, -23, -150, 4))
    # serviette vichy qui déborde
    g.append(f'<path d="M-33,-24 L-12,-24 L-27,-9 Z" fill="url(#vichy)" stroke="{REDD}" stroke-width=".25"/>')
    g.append(f'<path d="M12,-24 L33,-24 L27,-10 Z" fill="url(#vichy)" stroke="{REDD}" stroke-width=".25"/>')
    # corps
    g.append(f'<path d="M-31,-21.5 L31,-21.5 L26.5,-2.2 Q25.8,0 23,0 L-23,0 Q-25.8,0 -26.5,-2.2 Z" fill="url(#wicker)"/>')
    g.append(f'<path d="M-31,-21.5 L31,-21.5 L26.5,-2.2 Q25.8,0 23,0 L-23,0 Q-25.8,0 -26.5,-2.2 Z" fill="none" stroke="{BROWN}" stroke-width=".35" opacity=".6"/>')
    # rebord tressé
    g.append(f'<rect x="-33.5" y="-25" width="67" height="4.4" rx="2.2" fill="{WICKD}"/>')
    for i in range(23):
        x = -32.3 + i * 2.95
        g.append(f'<ellipse cx="{x:.2f}" cy="-22.8" rx="1.65" ry="1.5" fill="{WICK}" transform="rotate(35 {x:.2f} -22.8)"/>')
    # serviette retombante devant
    g.append(f'<path d="M-27,-9 L-25.5,-21 L-17,-21 Z" fill="url(#vichy)" stroke="{REDD}" stroke-width=".25" opacity=".95"/>')
    # étiquette cœur
    g.append(f'<line x1="21" y1="-20" x2="19.5" y2="-14" stroke="#A9814C" stroke-width=".4"/>')
    g.append(heart(19.2, -11.6, 1.25, RED))
    g.append(f'<ellipse cx="0" cy="1.2" rx="28" ry="1.4" fill="{BROWN}" opacity=".12"/>')
    g.append("</g>")
    return "".join(g)


def teapot_scene(cx, base):
    g = [f'<g transform="translate({cx},{base})">']
    g.append(f'<ellipse cx="0" cy="1" rx="36" ry="1.5" fill="{BROWN}" opacity=".12"/>')
    # --- théière (centre x=-11)
    t = -11
    g.append(f'<path d="M{t-15},-17 C{t-22},-19 {t-25},-27 {t-27},-31 L{t-24.5},-31.5 C{t-22},-27 {t-19},-23.5 {t-14},-22.5Z" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".4"/>')  # bec
    g.append(f'<path d="M{t+13},-24 C{t+22},-25 {t+22},-10 {t+12},-9" fill="none" stroke="{BROWN}" stroke-width="3"/>')
    g.append(f'<path d="M{t+13},-24 C{t+22},-25 {t+22},-10 {t+12},-9" fill="none" stroke="#FBF3E2" stroke-width="1.8"/>')
    g.append(f'<path d="M{t-16},-15 C{t-16},-27 {t-9},-30 {t},-30 C{t+9},-30 {t+16},-27 {t+16},-15 C{t+16},-6 {t+10},-1.2 {t+7},-1.2 L{t-7},-1.2 C{t-10},-1.2 {t-16},-6 {t-16},-15Z" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".45"/>')
    g.append(f'<rect x="{t-8}" y="-1.6" width="16" height="1.8" rx=".6" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".4"/>')
    g.append(f'<path d="M{t-15.6},-19 C{t-6},-16.6 {t+6},-16.6 {t+15.6},-19" fill="none" stroke="{GOLD}" stroke-width=".55"/>')
    g.append(f'<path d="M{t-14.5},-7.5 C{t-6},-5.5 {t+6},-5.5 {t+14.5},-7.5" fill="none" stroke="{GOLD}" stroke-width=".55"/>')
    # couvercle
    g.append(f'<path d="M{t-9},-29.2 C{t-8},-34 {t+8},-34 {t+9},-29.2Z" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".4"/>')
    g.append(f'<circle cx="{t}" cy="-34.6" r="1.6" fill="{RED}" stroke="{BROWN}" stroke-width=".3"/>')
    # bouquet sur la panse
    g.append(leaf(t - 4, -12.5, 200, 4.2) + leaf(t + 4, -12.5, -20, 4.2) + leaf(t - 1, -9.5, 110, 3.4))
    g.append(rose(t, -13.3, 2.5) + rose(t - 4.8, -11.3, 1.6, "#E36A6A") + rose(t + 4.8, -11.3, 1.6, "#E36A6A"))
    g.append(f'<circle cx="{t-3}" cy="-16.8" r=".55" fill="{LAV}"/><circle cx="{t+3.2}" cy="-16.5" r=".55" fill="{LAV}"/>')
    # --- tasse + soucoupe (x=+22)
    c = 23
    g.append(f'<ellipse cx="{c}" cy="-1.2" rx="11" ry="1.8" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".4"/>')
    g.append(f'<path d="M{c+7},-9.5 C{c+11.5},-10 {c+11.5},-4.5 {c+6},-4.2" fill="none" stroke="{BROWN}" stroke-width="1.7"/>')
    g.append(f'<path d="M{c+7},-9.5 C{c+11.5},-10 {c+11.5},-4.5 {c+6},-4.2" fill="none" stroke="#FBF3E2" stroke-width=".9"/>')
    g.append(f'<path d="M{c-8},-11 L{c+8},-11 C{c+7.6},-5 {c+4.5},-2.2 {c},-2.2 C{c-4.5},-2.2 {c-7.6},-5 {c-8},-11Z" fill="#FBF3E2" stroke="{BROWN}" stroke-width=".45"/>')
    g.append(f'<ellipse cx="{c}" cy="-11" rx="8" ry="1.4" fill="#B5652E" stroke="{BROWN}" stroke-width=".4"/>')
    g.append(f'<path d="M{c-7.6},-9 L{c+7.6},-9" stroke="{GOLD}" stroke-width=".5"/>')
    g.append(heart(c, -6.2, .95, RED))
    # vapeur
    for dx, d in [(-3, 0), (1.5, 1.6)]:
        g.append(f'<path d="M{c+dx},-13.5 C{c+dx-2.4},-16 {c+dx+2.4},-18 {c+dx},-20.5 C{c+dx-2.4},-23 {c+dx+1.6},-25 {c+dx},-27" fill="none" stroke="{GOLD}" stroke-width=".55" stroke-linecap="round" opacity=".9"/>')
    # biscuits « petit-beurre » devant la tasse
    for i, (bx, by, rot) in enumerate([(c - 8, -14.8, -12), (c + 1, -15.2, 8)]):
        pass
    # marguerites
    g.append(f'<path d="M-33,0 C-33,-6 -34,-10 -36,-15" stroke="{LEAFD}" stroke-width=".5" fill="none"/>')
    g.append(f'<path d="M-31,0 C-31,-4 -30,-8 -29,-11" stroke="{LEAFD}" stroke-width=".5" fill="none"/>')
    g.append(leaf(-33.4, -6, -130, 3.5) + leaf(-30.6, -5, -40, 3.2))
    g.append(daisy(-36, -15.5, 3.2) + daisy(-29, -11.5, 2.6))
    g.append("</g>")
    return "".join(g)


def biscuits(cx, base):
    g = [f'<g transform="translate({cx},{base})">']
    g.append(f'<ellipse cx="0" cy="-0.8" rx="9.5" ry="1.7" fill="#FFFDF7" stroke="{BROWN}" stroke-width=".35"/>')
    for i, (x, y) in enumerate([(-4, -2.4), (3.2, -2.4), (-.4, -4.4)]):
        g.append(f'<rect x="{x-3.4}" y="{y-1.1}" width="6.8" height="2.2" rx=".5" fill="#E2B064" stroke="#A8732F" stroke-width=".3"/>')
        g.append(f'<line x1="{x-2.6}" x2="{x+2.6}" y1="{y}" y2="{y}" stroke="#A8732F" stroke-width=".25" stroke-dasharray=".25 .7"/>')
    g.append("</g>")
    return "".join(g)


# ---------- EAN-13 ----------
L_ = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
G_ = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
R_ = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]
PAR = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13_svg(code, x, y, w, h, sku):
    d = [int(c) for c in code]
    chk = (10 - (sum(d[i] * (3 if i % 2 else 1) for i in range(12)) % 10)) % 10
    assert chk == d[12], f"EAN check digit KO {code}"
    bits = "101" + "".join((L_ if PAR[d[0]][i] == "L" else G_)[d[i + 1]] for i in range(6)) + "01010" + "".join(R_[d[i + 7]] for i in range(6)) + "101"
    guard = set(range(0, 3)) | set(range(45, 50)) | set(range(92, 95))
    pad_l, quiet = 7.0, 3.5
    mod = (w - pad_l - quiet) / (95 + 4)
    bx = x + pad_l + 4 * mod
    bar_h = h - 5.2
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF"/>']
    for i, b in enumerate(bits):
        if b == "1":
            hh = bar_h + (1.6 if i in guard else 0)
            s.append(f'<rect x="{bx+i*mod:.3f}" y="{y+1.6:.2f}" width="{mod+0.004:.3f}" height="{hh:.2f}" fill="#000"/>')
    fs = 2.35
    ty = y + 1.6 + bar_h + 2.4
    s.append(f'<text x="{bx-1.2:.2f}" y="{ty:.2f}" font-family="Poppins" font-size="{fs}" text-anchor="end">{code[0]}</text>')
    s.append(f'<text x="{bx+(3+21)*mod:.2f}" y="{ty:.2f}" font-family="Poppins" font-size="{fs}" text-anchor="middle" letter-spacing=".12">{code[1:7]}</text>')
    s.append(f'<text x="{bx+(50+21)*mod:.2f}" y="{ty:.2f}" font-family="Poppins" font-size="{fs}" text-anchor="middle" letter-spacing=".12">{code[7:]}</text>')
    s.append(f'<text transform="translate({x+3.6},{y+h-2}) rotate(-90)" font-family="Poppins" font-weight="600" font-size="2.3">{sku}</text>')
    return "".join(s)


# ---------- page 1 : corps ----------
W1, H1 = 567.3125, 260.8636
PX = [115.2, 205.2, 295.2, 385.2]
PW = [90, 90, 90, 89.5]
TOP, FOLD, LIDLINE = 33.2, 123.2, 68.2

body = [f'<rect width="{W1}" height="{H1}" fill="url(#paper)"/>']
# bande vichy (zone cachée par le couvercle) + liseré
body.append(f'<rect x="0" y="0" width="{W1}" height="{LIDLINE}" fill="url(#vichy)"/>')
body.append(f'<rect x="0" y="{LIDLINE-0.6}" width="{W1}" height=".6" fill="{CORALD}" opacity=".9"/>')
# frise fine de petits cœurs sous le couvercle
for i in range(64):
    x = 117.5 + i * 5.6
    if x > 472: break
    body.append(f'<circle cx="{x:.2f}" cy="{LIDLINE+2.6}" r=".45" fill="{WHITE}" opacity=".8"/>')

# Panneau 1 : panier
body.append(basket(PX[0] + 45, FOLD - 4.5))
# Panneau 2 : fiche recette / contenu
x0 = PX[1]
tagx, tagy, tagw, tagh = x0 + 9, 74.5, 72, 44
body.append(f'<path d="M{x0+45},{LIDLINE+0.4} L{x0+45},{tagy+3}" stroke="#A9814C" stroke-width=".7"/>')
body.append(f'<rect x="{tagx}" y="{tagy}" width="{tagw}" height="{tagh}" rx="2" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".6" transform="rotate(-1.2 {tagx+tagw/2} {tagy+tagh/2})"/>')
body.append(f'<g transform="rotate(-1.2 {tagx+tagw/2} {tagy+tagh/2})">')
body.append(f'<circle cx="{x0+45}" cy="{tagy+3}" r="1.1" fill="{CREAM}" stroke="{KRAFT}" stroke-width=".5"/>')
body.append(f'<text x="{x0+45}" y="{tagy+11.2}" font-family="Caveat" font-weight="600" font-size="7" fill="{CORALD}" text-anchor="middle">Dans mon panier…</text>')
body.append(f'<line x1="{tagx+14}" x2="{tagx+tagw-14}" y1="{tagy+13.6}" y2="{tagy+13.6}" stroke="{KRAFT}" stroke-width=".4" stroke-dasharray="1 .8"/>')
items = [("La nana de Wépion", "I"), ("Le thé des amoureux", "T"), ("Délice de Montélimar", "T"), ("Sérénité · BIO", "I"), ("Masala Chai", "I")]
for i, (n, t) in enumerate(items):
    yy = tagy + 18.6 + i * 4.45
    body.append(heart(tagx + 6.2, yy - 1.0, .42, CORALD))
    body.append(f'<text x="{tagx+8.4}" y="{yy}" font-family="Poppins" font-size="2.95" fill="{BROWN}">{n} <tspan fill="#8A6A55">({t})</tspan></text>')
    body.append(f'<text x="{tagx+tagw-6}" y="{yy+0.3}" font-family="Caveat" font-weight="600" font-size="4.4" fill="{CORALD}" text-anchor="end">x2</text>')
body.append(f'<text x="{x0+45}" y="{tagy+tagh-2.6}" font-family="Playfair Display" font-style="italic" font-weight="500" font-size="2.6" fill="#8A6A55" text-anchor="middle">10 sachets · (T) thé · (I) infusion</text>')
body.append("</g>")
# Panneau 3 : théière + tasse
body.append(teapot_scene(PX[2] + 47, FOLD - 4.5))
body.append(biscuits(PX[2] + 71, FOLD - 4.5 + 0.0) if False else "")
# Panneau 4 : logo
c4 = PX[3] + PW[3] / 2
bw = 30
by = 74
body.append(f'<path d="M{c4-bw/2-1.8},{by-1.8} h{bw+3.6} v{bw+3.6} h{-bw-3.6+5.5} a5.5,5.5 0 0 1 -5.5,-5.5Z" fill="{CORALL}"/>')
body.append(f'<path d="M{c4-bw/2},{by} h{bw} v{bw} h{-bw+4} a4,4 0 0 1 -4,-4Z" fill="#FFFFFF"/>')
lg, lh = logo(c4 - 12.5, by + 4.6, 25, INK)
body.append(lg)
body.append(f'<text x="{c4}" y="{by+bw+6.4}" font-family="Playfair Display" font-weight="700" font-size="3.3" letter-spacing=".55" fill="{WHITE}" text-anchor="middle">THÉS &amp; INFUSIONS</text>')
body.append(f'<text x="{c4}" y="{by+bw+13.4}" font-family="Caveat" font-weight="600" font-size="6.2" fill="{WHITE}" text-anchor="middle">Le panier de grand-maman</text>')
body.append(leaf(c4 - 33, by + bw + 11.5, 200, 4) + daisy(c4 - 36.5, by + bw + 10.5, 2.4))
body.append(heart(c4 + 34.5, by + bw + 10.8, .9, WHITE, .9))
# petits cœurs épars
for (x, y, s) in [(PX[0] + 8, 80, .55), (PX[0] + 83, 84, .5), (PX[2] + 82, 79, .5), (PX[1] + 4, 112, .45), (PX[3] + 7, 82, .5), (PX[3] + 82, 92, .5)]:
    body.append(heart(x, y, s, WHITE, .75))
# rabats de fond : vichy discret + code-barre (même place que l'original)
body.append(f'<rect x="0" y="{FOLD}" width="{W1}" height="{H1-FOLD}" fill="url(#vichy)" opacity=".35"/>')
body.append(ean13_svg("5413393004060", 125.6, 128.5, 32.4, 19.6, "C0196"))

# ---------- page 2 : couvercle ----------
W2, H2 = 336.598, 363.033
lid = [f'<rect width="{W2}" height="{H2}" fill="url(#vichy)"/>']
FX0, FX1, FY0, FY1 = 148.1, 242.1, 121.9, 217.1   # face supérieure
cx, cy = (FX0 + FX1) / 2, (FY0 + FY1) / 2
SIDE = 35


def side_group(length, front):
    s = [scallop_strip(length, depth=5.2, r=2.2), twine(length, -SIDE + 13)]
    return "".join(s)


# avant (bord libre y=252.1), arrière (bord libre y=86.9, tourné 180°), gauche/droite
lid.append(f'<g transform="translate(148.7,252.1)">{side_group(92.8, True)}</g>')
lid.append(f'<g transform="translate(241.5,86.9) rotate(180)">{side_group(92.8, False)}</g>')
lid.append(f'<g transform="translate(113.1,122.5) rotate(90)">{side_group(94, False)}</g>'.replace("rotate(90)", "rotate(90) scale(1,-1)") if False else
           f'<g transform="translate(113.1,216.5) rotate(-90) scale(1,-1)">{side_group(94, False)}</g>')
lid.append(f'<g transform="translate(277.1,122.5) rotate(90) scale(1,-1)">{side_group(94, False)}</g>')
# nœud de ficelle sur la face avant (twine à 13 mm du bord libre)
lid.append(bow(195.1, 252.1 - SIDE + 13, 1.0))
# étiquette au dos (lue tête-bêche, comme l'original)
lid.append(f'''<g transform="rotate(180 195.1 104.4)">
<rect x="165.1" y="96.6" width="60" height="11.2" rx="1.4" fill="#FFFDF7" stroke="{KRAFT}" stroke-width=".5"/>
<text x="195.1" y="101.6" font-family="Caveat" font-weight="600" font-size="4.6" fill="{CORALD}" text-anchor="middle">Comme chez grand-maman</text>
<text x="195.1" y="105.6" font-family="Poppins" font-size="2.2" fill="{BROWN}" text-anchor="middle" letter-spacing=".2">THÉS &amp; INFUSIONS FAITS AVEC AMOUR</text>
</g>''')
# napperon en dentelle sur la face supérieure
R = 40
n = 30
dots = []
for i in range(n):
    a = 2 * math.pi * i / n
    dots.append(f'<circle cx="{cx+R*math.cos(a):.2f}" cy="{cy+R*math.sin(a):.2f}" r="4.4" fill="#FFFDF7"/>')
lid.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#FFFDF7"/>' + "".join(dots))
for i in range(n):
    a = 2 * math.pi * (i + .5) / n
    lid.append(f'<circle cx="{cx+(R-1.2)*math.cos(a):.2f}" cy="{cy+(R-1.2)*math.sin(a):.2f}" r=".9" fill="{CORALD}" opacity=".4"/>')
for i in range(n):
    a = 2 * math.pi * i / n
    lid.append(f'<circle cx="{cx+(R+1.4)*math.cos(a):.2f}" cy="{cy+(R+1.4)*math.sin(a):.2f}" r="1.25" fill="{CORALD}" opacity=".35"/>')
for i in range(48):
    a = 2 * math.pi * i / 48
    lid.append(f'<ellipse cx="{cx+(R-6)*math.cos(a):.2f}" cy="{cy+(R-6)*math.sin(a):.2f}" rx="1.6" ry=".55" fill="{CORALD}" opacity=".3" transform="rotate({math.degrees(a):.1f} {cx+(R-6)*math.cos(a):.2f} {cy+(R-6)*math.sin(a):.2f})"/>')
lid.append(f'<circle cx="{cx}" cy="{cy}" r="{R-9}" fill="none" stroke="{CORALD}" stroke-width=".3" stroke-dasharray="1 .9" opacity=".6"/>')
# logo + titre
bw2 = 26
lx, ly = cx - bw2 / 2, cy - 22
lid.append(f'<path d="M{lx-1.5},{ly-1.5} h{bw2+3} v{bw2+3} h{-bw2-3+5} a5,5 0 0 1 -5,-5Z" fill="{CORAL}"/>')
lid.append(f'<path d="M{lx},{ly} h{bw2} v{bw2} h{-bw2+4} a4,4 0 0 1 -4,-4Z" fill="#FFFFFF"/>')
lg, lh = logo(cx - 11, ly + 4, 22, INK)
lid.append(lg)
lid.append(f'<text x="{cx}" y="{cy+13.2}" font-family="Caveat" font-weight="600" font-size="8.2" fill="{CORALD}" text-anchor="middle">Le panier</text>')
lid.append(f'<text x="{cx}" y="{cy+20.6}" font-family="Caveat" font-weight="600" font-size="8.2" fill="{CORALD}" text-anchor="middle">de grand-maman</text>')
lid.append(f'<text x="{cx}" y="{cy+26.2}" font-family="Playfair Display" font-weight="700" font-size="2.4" letter-spacing=".5" fill="{BROWN}" text-anchor="middle">THÉS &amp; INFUSIONS</text>')
lid.append(leaf(cx - 17, cy + 26, 200, 3.2) + daisy(cx - 20, cy + 25.3, 1.9) + leaf(cx + 17, cy + 26, -20, 3.2) + daisy(cx + 20, cy + 25.3, 1.9))
lid.append(heart(cx - 18, cy - 12, .6, CORAL, .8) + heart(cx + 18, cy - 12, .6, CORAL, .8))

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
print("ok")
