# -*- coding: utf-8 -*-
"""Coffret 10 sachets (gabarit Giftbox 2026) — générateur commun aux 8 références GMS.
Usage : gen_box.py <out> <logo.svg> <boxes.json> <clé>
Génère 2 HTML (corps + couvercle) aux dimensions exactes du gabarit Giftbox 2026,
coordonnées en mm (origine haut-gauche de la page, fond perdu = page entière)."""
import math, os, re, sys

OUT = sys.argv[1]
LOGO_SVG = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# ---------- palette (V3 : corail uni du doypack 279) ----------
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
import json
CFG = json.load(open(sys.argv[3], encoding="utf-8"))[sys.argv[4]]
FAM = {
    "corail":  ("#EC8475", "#D9624F", "#F6B3A8", "#FFF8F2"),
    "sauge":   ("#C5D3A8", "#6F8752", "#E3EAD2", "#33402A"),
    "rooibos": ("#C24F4C", "#8F2F2E", "#E69A97", "#FFF8F2"),
    "marine":  ("#5A6584", "#3A4362", "#A9B1C7", "#FFF8F2"),
}
CORAL, CORALD, CORALL, WHITE = FAM[CFG["family"]]

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


# ---------- ingrédients (unité ≈ 8 mm de haut, centrés sur 0,0) ----------
_CLIP = [0]


def _g(cx, cy, s, inner):
    return f'<g transform="translate({cx:.2f},{cy:.2f}) scale({s})">{inner}</g>'


def ing_ananas(cx, cy, s=1):
    _CLIP[0] += 1
    i = _CLIP[0]
    hatch = "".join(f'<line x1="{-4+k*1.1:.2f}" y1="-2.2" x2="{k*1.1:.2f}" y2="4.6" stroke="#B57A1F" stroke-width=".18"/>'
                    f'<line x1="{4-k*1.1:.2f}" y1="-2.2" x2="{-k*1.1:.2f}" y2="4.6" stroke="#B57A1F" stroke-width=".18"/>' for k in range(8))
    inner = (f'<path d="M0,-1.6 L-2.4,-5.2 L-.9,-2.5 L-1.2,-6 L0,-2.8 L1.2,-6 L.9,-2.5 L2.4,-5.2Z" fill="#4E8A3E"/>'
             f'<path d="M0,-1.9 L-1.3,-4.6 L0,-3.2 L1.3,-4.6Z" fill="#6FAE52"/>'
             f'<clipPath id="ana{i}"><ellipse cx="0" cy="1.2" rx="2.5" ry="3.15"/></clipPath>'
             f'<ellipse cx="0" cy="1.2" rx="2.5" ry="3.15" fill="#EDB53E" stroke="#B57A1F" stroke-width=".15"/>'
             f'<g clip-path="url(#ana{i})">{hatch}</g>'
             f'<ellipse cx="-.9" cy=".2" rx=".5" ry="1.4" fill="#FFF3C4" opacity=".35"/>')
    return _g(cx, cy, s, inner)


def ing_cerise(cx, cy, s=1):
    inner = ('<path d="M-1.4,1.0 C-1.1,-1.2 -.2,-3 .7,-4.1 M1.6,1.4 C1.5,-.6 1.1,-2.6 .7,-4.1" stroke="#5B3A1E" stroke-width=".32" fill="none" stroke-linecap="round"/>'
             f'{leaf(.7, -4.1, -25, 3.2)}'
             '<circle cx="-1.4" cy="2.3" r="1.8" fill="#B5122F"/><circle cx="1.6" cy="2.6" r="1.8" fill="#C81A38"/>'
             '<ellipse cx="-2" cy="1.6" rx=".45" ry=".65" fill="#FFFFFF" opacity=".5"/><ellipse cx="1" cy="1.9" rx=".45" ry=".65" fill="#FFFFFF" opacity=".5"/>')
    return _g(cx, cy, s, inner)


def ing_papaye(cx, cy, s=1):
    seeds = "".join(f'<circle cx="{x}" cy="{y}" r=".33" fill="#2A1A12"/>' for x, y in [(-.4, -.6), (.4, -.2), (-.3, .5), (.45, .9), (-.35, 1.5), (.3, 2.0), (0, -1.2)])
    inner = ('<ellipse cx="0" cy="0" rx="2.8" ry="4" fill="#8FAE3E"/>'
             '<ellipse cx="0" cy=".1" rx="2.3" ry="3.5" fill="#F59443"/>'
             '<ellipse cx="0" cy=".5" rx="1.1" ry="2.2" fill="#F7C27A"/>' + seeds)
    return _g(cx, cy, s, inner)


def ing_peche(cx, cy, s=1):
    inner = ('<path d="M.4,-2.9 C.6,-3.6 .9,-4 1.2,-4.3" stroke="#5B3A1E" stroke-width=".3" fill="none"/>'
             f'{leaf(.9, -3.9, -20, 3.4)}'
             '<circle cx="0" cy=".4" r="3.2" fill="#F6A65A"/>'
             '<ellipse cx="1.1" cy=".8" rx="2.2" ry="2.6" fill="#E8604A" opacity=".6"/>'
             '<path d="M.3,-2.7 C-.7,-.9 -.7,1.4 .2,3.5" stroke="#C9503C" stroke-width=".25" fill="none" opacity=".7"/>'
             '<ellipse cx="-1.4" cy="-.6" rx=".6" ry="1" fill="#FFE2B8" opacity=".55"/>')
    return _g(cx, cy, s, inner)


def ing_mangue(cx, cy, s=1):
    _CLIP[0] += 1
    i = _CLIP[0]
    inner = (f'<linearGradient id="mg{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F7CD45"/><stop offset=".55" stop-color="#F28F2E"/><stop offset="1" stop-color="#E0533A"/></linearGradient>'
             f'{leaf(-1.6, -3.0, -150, 3.2)}'
             f'<path d="M-2.2,-2.6 C.5,-4.2 3.6,-2.2 3,1 C2.5,3.7 -.4,4.4 -2.2,2.8 C-3.4,1.6 -3.6,-1.4 -2.2,-2.6Z" fill="url(#mg{i})"/>'
             '<ellipse cx="-1.2" cy="-1.2" rx=".6" ry="1.1" fill="#FFF4C8" opacity=".45" transform="rotate(30 -1.2 -1.2)"/>')
    return _g(cx, cy, s, inner)


def ing_orange(cx, cy, s=1):
    dots = "".join(f'<circle cx="{x}" cy="{y}" r=".12" fill="#C4650E" opacity=".6"/>' for x, y in [(-1, -.5), (.8, -1), (1.4, .8), (-1.5, 1), (0, 1.8), (.3, -.1), (-.4, -1.8), (1.8, -.4)])
    inner = ('<path d="M0,-2.9 L.2,-3.6" stroke="#5B3A1E" stroke-width=".35"/>' + leaf(.2, -3.4, -15, 3.2) +
             '<circle cx="0" cy=".3" r="3.2" fill="#F28C1C"/><circle cx="0" cy=".3" r="3.2" fill="none" stroke="#D2700F" stroke-width=".15"/>' + dots +
             '<ellipse cx="-1.3" cy="-.8" rx=".6" ry="1" fill="#FFE0A8" opacity=".5"/>')
    return _g(cx, cy, s, inner)


def ing_citron(cx, cy, s=1):
    inner = (leaf(-.4, -2.4, -150, 3.0) +
             '<ellipse cx="3.2" cy=".3" rx=".7" ry=".5" fill="#F0C92E"/><ellipse cx="-3.2" cy=".3" rx=".7" ry=".5" fill="#F0C92E"/>'
             '<ellipse cx="0" cy=".3" rx="3.2" ry="2.5" fill="#F5D33D"/>'
             '<ellipse cx="-1" cy="-.5" rx="1.2" ry=".5" fill="#FFF6C2" opacity=".55"/>')
    return _g(cx, cy, s, inner)


def ing_bergamote(cx, cy, s=1):
    inner = ('<path d="M0,-2.6 L.1,-3.4" stroke="#5B3A1E" stroke-width=".35"/>' + leaf(.1, -3.2, -30, 3.4) + leaf(.1, -3.2, -160, 2.6, LEAFD) +
             '<circle cx="0" cy=".5" r="3" fill="#D3D23E"/><ellipse cx="1" cy="1" rx="2" ry="2.4" fill="#9DB23A" opacity=".5"/>'
             '<circle cx="0" cy="3.4" r=".3" fill="#9DB23A"/><ellipse cx="-1.2" cy="-.4" rx=".6" ry=".9" fill="#FBF6C8" opacity=".5"/>')
    return _g(cx, cy, s, inner)


def ing_rose(cx, cy, s=1):
    pet = "".join(f'<ellipse cx="0" cy="-1.7" rx="1.75" ry="1.45" fill="#E2557A" stroke="#B83558" stroke-width=".12" transform="rotate({a})"/>' for a in range(0, 360, 72))
    inner = (leaf(-.6, 2.4, 150, 3.2) + leaf(.6, 2.4, 30, 3.2) +
             f'<g transform="translate(0,-.6)">{pet}<circle r="1.6" fill="#C93A62"/>'
             '<path d="M-.8,0 A.8,.8 0 1 1 .5,.55 A.45,.45 0 1 1 0,-.2" fill="none" stroke="#8E2244" stroke-width=".22" stroke-linecap="round"/></g>')
    return _g(cx, cy, s, inner)


def ing_bleuet(cx, cy, s=1):
    pet = "".join(f'<path d="M0,-.7 L-1,-2.9 L-.55,-3.35 L-.15,-3 L.25,-3.4 L.6,-3 L1,-2.95Z" fill="#3F6FD6" stroke="#2C52A8" stroke-width=".1" transform="rotate({a})"/>' for a in range(0, 360, 45))
    inner = ('<path d="M0,1 C.1,2.5 .1,3.5 0,4.4" stroke="#4E7A3E" stroke-width=".35" fill="none"/>' + leaf(0, 3.4, -60, 2.6) +
             f'<g transform="translate(0,-.6)">{pet}<circle r="1" fill="#26398A"/>'
             '<circle cx="-.35" cy="-.2" r=".18" fill="#7D98F0"/><circle cx=".3" cy=".25" r=".18" fill="#7D98F0"/><circle cx=".2" cy="-.4" r=".15" fill="#7D98F0"/></g>')
    return _g(cx, cy, s, inner)


def ing_lavande(cx, cy, s=1):
    inner = lavender(-1.1, 4.2, 8, -14) + lavender(0, 4.2, 8.8, 0) + lavender(1.2, 4.2, 7.8, 14)
    return _g(cx, cy, s, inner)


def _leaf_ellipse(x, y, rx, ry, ang, col, vein):
    return (f'<g transform="translate({x},{y}) rotate({ang})"><ellipse rx="{rx}" ry="{ry}" fill="{col}"/>'
            f'<line x1="0" y1="{-ry*.85}" x2="0" y2="{ry*.85}" stroke="{vein}" stroke-width=".14"/></g>')


def ing_menthe(cx, cy, s=1):
    c, v = "#4F9B4F", "#2F6B33"
    inner = ('<path d="M0,4.4 C0,1.5 .1,-1.5 .2,-4.6" stroke="#3F7A3A" stroke-width=".35" fill="none"/>' +
             _leaf_ellipse(-1.5, 2.4, 1.05, 1.95, -55, c, v) + _leaf_ellipse(1.6, 2.2, 1.05, 1.95, 55, c, v) +
             _leaf_ellipse(-1.4, -.2, .95, 1.8, -45, "#5CAA57", v) + _leaf_ellipse(1.5, -.4, .95, 1.8, 45, "#5CAA57", v) +
             _leaf_ellipse(-.9, -2.7, .8, 1.5, -30, "#6DB962", v) + _leaf_ellipse(1.1, -2.8, .8, 1.5, 30, "#6DB962", v) +
             _leaf_ellipse(.2, -4.4, .6, 1.1, 0, "#7FC46F", v))
    return _g(cx, cy, s, inner)


def ing_verveine(cx, cy, s=1):
    c, v = "#86AE4F", "#5A7F31"
    inner = ('<path d="M0,4.4 L0,1.6" stroke="#5A7F31" stroke-width=".35"/>' +
             "".join(_leaf_ellipse(math.sin(math.radians(a)) * 2.0, 1.5 - math.cos(math.radians(a)) * 2.0, .62, 2.6, a, c if k % 2 else "#9BC060", v)
                     for k, a in enumerate([-62, -30, 0, 30, 62])) +
             '<circle cx="-.5" cy="-3.9" r=".35" fill="#FFFFFF"/><circle cx=".4" cy="-4.2" r=".3" fill="#F3E9FF"/><circle cx="0" cy="-3.5" r=".3" fill="#FFFFFF"/>')
    return _g(cx, cy, s, inner)


def _tea_sprig(col1, col2, bud, extra=""):
    v = "#2F4F24"
    return ('<path d="M0,4.4 C.2,1.5 0,-1.5 -.2,-3.6" stroke="#5B4A2E" stroke-width=".35" fill="none"/>' +
            _leaf_ellipse(-1.7, 1.9, 1.2, 2.6, -55, col1, v) + _leaf_ellipse(1.7, 1.3, 1.2, 2.6, 55, col2, v) +
            _leaf_ellipse(-1.1, -1.5, 1.0, 2.1, -30, col2, v) + _leaf_ellipse(1.0, -2.0, .95, 2.0, 32, col1, v) +
            f'<ellipse cx="-.2" cy="-4.2" rx=".55" ry="1.15" fill="{bud}"/>' + extra)


def ing_the_vert(cx, cy, s=1):
    return _g(cx, cy, s, _tea_sprig("#5E8C3A", "#6E9E45", "#A8CE72"))


def ing_the_noir(cx, cy, s=1):
    curls = "".join(f'<path d="M{x-.5},{y} q.5,-.6 1,0" stroke="#2A1F1A" stroke-width=".45" fill="none" stroke-linecap="round"/>' for x, y in [(-2.4, 4.2), (-1.2, 4.6), (0, 4.3), (1.2, 4.7), (2.3, 4.2), (-.6, 3.8), (.8, 3.9)])
    return _g(cx, cy, s, _tea_sprig("#5B8A47", "#6C9C55", "#A5CB7E", curls))


def ing_rooibos(cx, cy, s=1):
    import random
    rnd = random.Random(7)
    sticks = []
    for _ in range(150):
        a = rnd.uniform(0, math.pi)
        r = rnd.uniform(0, 1) ** .5
        x = math.cos(a) * 3.2 * r * (1 if rnd.random() > .5 else -1)
        y = 3.6 - math.sin(a) * 3.6 * r
        ang = rnd.uniform(0, 180)
        L = rnd.uniform(.7, 1.4)
        col = rnd.choice(["#B4502A", "#9A3E20", "#C8693A", "#7E3218"])
        dx, dy = math.cos(math.radians(ang)) * L / 2, math.sin(math.radians(ang)) * L / 2
        sticks.append(f'<line x1="{x-dx:.2f}" y1="{y-dy:.2f}" x2="{x+dx:.2f}" y2="{y+dy:.2f}" stroke="{col}" stroke-width=".42" stroke-linecap="round"/>')
    inner = ('<path d="M-.2,-.4 C-.2,-2 0,-3.4 .3,-4.6" stroke="#7E5A2E" stroke-width=".3" fill="none"/>' +
             "".join(f'<line x1="{.1+(k%2*2-1)*.1:.2f}" y1="{-1-k*.7:.2f}" x2="{(k%2*2-1)*1.1:.2f}" y2="{-1.6-k*.7:.2f}" stroke="#6E9A45" stroke-width=".22" stroke-linecap="round"/>' for k in range(5)) +
             "".join(sticks))
    return _g(cx, cy, s, inner)


INGS = {
    "Fraise": lambda cx, cy, s: strawberry(cx, cy, s),
    "Framboise": lambda cx, cy, s: raspberry(cx, cy, s * .95),
    "Mûre": lambda cx, cy, s: blackberry(cx, cy, s * .95),
    "Cassis": lambda cx, cy, s: cassis(cx, cy, s * .95),
    "Ananas": ing_ananas, "Cerise": ing_cerise, "Papaye": ing_papaye, "Pêche": ing_peche, "Mangue": ing_mangue,
    "Orange": ing_orange, "Citron": ing_citron, "Bergamote": ing_bergamote, "Rose": ing_rose, "Bleuet": ing_bleuet,
    "Lavande": ing_lavande, "Menthe": ing_menthe, "Verveine": ing_verveine,
    "Thé vert": ing_the_vert, "Thé noir": ing_the_noir, "Rooibos": ing_rooibos,
}


def ing(name, cx, cy, s=1):
    return INGS[name](cx, cy, s)


def fruit_icon(name, cx, cy, s=1):
    return ing(name, cx, cy, .82 * s)


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
# logo Teatower en grand (sans napperon)
LB = 56
lx, ly = cx - LB / 2, FY0 + 7
lid.append(f'<path d="M{lx-2.4},{ly-2.4} h{LB+4.8} v{LB+4.8} h{-LB-4.8+8} a8,8 0 0 1 -8,-8Z" fill="{CORALL}"/>')
lid.append(f'<path d="M{lx},{ly} h{LB} v{LB} h{-LB+6} a6,6 0 0 1 -6,-6Z" fill="#FFFFFF"/>')
lg, lh = logo(cx - LB * .42, ly + LB * .5 - LB * .84 * 1346 / 1573 / 2, LB * .84, INK)
lid.append(lg)
lid.append(flag_round(lx + LB - 6, ly + 6, 3.2))
ll = CFG["lid_lines"]
if len(ll) == 2:
    for k, t in enumerate(ll):
        lid.append(f'<text x="{cx}" y="{ly+LB+8.6+k*7.0:.2f}" font-family="Caveat" font-weight="600" font-size="7.6" fill="{WHITE}" text-anchor="middle">{t}</text>')
    ty = ly + LB + 21.4
else:
    lid.append(f'<text x="{cx}" y="{ly+LB+12:.2f}" font-family="Caveat" font-weight="600" font-size="10" fill="{WHITE}" text-anchor="middle">{ll[0]}</text>')
    ty = ly + LB + 19
lid.append(f'<text x="{cx}" y="{ty:.2f}" font-family="Playfair Display" font-weight="700" font-size="2.5" letter-spacing=".5" fill="{WHITE}" text-anchor="middle">{CFG["type"]}</text>')
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
