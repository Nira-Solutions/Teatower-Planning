# -*- coding: utf-8 -*-
"""Mockup 3D (boîte fermée) à partir des rendus PNG du PRINT (corps = page 0, couvercle = page 1).
Usage : mockup.py <dossier_build> <titre> <sortie.html>"""
import base64, io, math, os, sys
from PIL import Image

B, TITLE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
body = Image.open(os.path.join(B, "C0196_PRINT_0.png")).convert("RGB")
lid = Image.open(os.path.join(B, "C0196_PRINT_1.png")).convert("RGB")
sb = body.width / 567.3125
sl = lid.width / 336.598


def crop(im, s, x0, y0, x1, y1):
    return im.crop((round(x0 * s), round(y0 * s), round(x1 * s), round(y1 * s)))


def b64(im):
    buf = io.BytesIO(); im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


PX = [115.2, 205.2, 295.2, 385.2]
PW = [90, 90, 90, 89.5]
panel = [crop(body, sb, PX[i], 68.2, PX[i] + PW[i], 123.2) for i in range(4)]   # partie visible sous le couvercle
lid_top = crop(lid, sl, 148.1, 121.9, 242.1, 217.1)                             # bas de l'image = face avant (nœud)
lid_front = crop(lid, sl, 148.1, 217.1, 242.1, 252.1)                           # haut = pli
lid_right = crop(lid, sl, 242.1, 122.5, 277.1, 216.5).transpose(Image.TRANSPOSE).transpose(Image.FLIP_LEFT_RIGHT)  # u: avant→arrière, v: pli→bord
lid_left = crop(lid, sl, 113.1, 122.5, 148.1, 216.5).transpose(Image.TRANSPOSE).transpose(Image.FLIP_TOP_BOTTOM)   # u: arrière→avant… (non utilisé)

# projection
K = 3.4  # px / mm
ux = (0.93 * K, 0.30 * K)
uy = (0.62 * K, -0.40 * K)
uz = (0, -K)
LW, LD, LH = 94.0, 95.2, 35.0
BW, BD, BH = 90.0, 90.0, 90.0
ix, iy = (LW - BW) / 2, (LD - BD) / 2


def P(x, y, z, ox, oy):
    return (ox + x * ux[0] + y * uy[0] + z * uz[0], oy + x * ux[1] + y * uy[1] + z * uz[1])


def face(img, origin, A, La, Bv, Lb, ox, oy, shade=0.0, light=0.0):
    w, h = img.size
    o = P(*origin, ox, oy)
    a = (A[0] * La / w, A[1] * La / w)
    c = (Bv[0] * Lb / h, Bv[1] * Lb / h)
    s = f'<g transform="matrix({a[0]:.5f} {a[1]:.5f} {c[0]:.5f} {c[1]:.5f} {o[0]:.2f} {o[1]:.2f})">'
    s += f'<image href="{b64(img)}" width="{w}" height="{h}" preserveAspectRatio="none"/>'
    if shade: s += f'<rect width="{w}" height="{h}" fill="#000" opacity="{shade}"/>'
    if light: s += f'<rect width="{w}" height="{h}" fill="#fff" opacity="{light}"/>'
    return s + "</g>"


def vec(v, k=1): return (v[0] * k, v[1] * k)


def box(front_i, right_i, ox, oy):
    down = vec(uz, -1)
    s = []
    # ombre au sol
    c = P(LW / 2, LD / 2, 0, ox, oy)
    s.append(f'<ellipse cx="{c[0]+30:.1f}" cy="{c[1]+22:.1f}" rx="{LW*K*0.95:.1f}" ry="{LD*K*0.32:.1f}" fill="#3a2a22" opacity=".18" filter="url(#blur)"/>')
    # corps
    s.append(face(panel[front_i], (ix, iy, 55), ux, BW, down, 55, ox, oy))
    s.append(face(panel[right_i], (ix + BW, iy, 55), uy, BD, down, 55, ox, oy, shade=0.16))
    # ombre portée du couvercle sur le corps
    p1, p2, p3 = P(ix, iy, 55, ox, oy), P(ix + BW, iy, 55, ox, oy), P(ix + BW, iy + BD, 55, ox, oy)
    s.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f} L{p3[0]:.1f},{p3[1]+10:.1f} L{p2[0]:.1f},{p2[1]+10:.1f} L{p1[0]:.1f},{p1[1]+10:.1f}Z" fill="url(#lidshadow)" opacity=".5"/>')
    # couvercle
    s.append(face(lid_front, (0, 0, BH), ux, LW, down, LH, ox, oy))
    s.append(face(lid_right, (LW, 0, BH), uy, LD, down, LH, ox, oy, shade=0.16))
    s.append(face(lid_top, (0, LD, BH), ux, LW, vec(uy, -1), LD, ox, oy, light=0.06))
    # arêtes légères
    for a, b in [((0, 0, BH), (LW, 0, BH)), ((LW, 0, BH), (LW, LD, BH)), ((LW, 0, BH), (LW, 0, BH - LH))]:
        pa, pb = P(*a, ox, oy), P(*b, ox, oy)
        s.append(f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" stroke="#fff" stroke-width="1.2" opacity=".35"/>')
    return "".join(s)


W, H = 1800, 1000
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <radialGradient id="bg" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#FBF7F2"/><stop offset="1" stop-color="#E9DFD5"/></radialGradient>
 <linearGradient id="lidshadow" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>
 <filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="16"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect y="{H*0.70:.0f}" width="{W}" height="{H*0.30:.0f}" fill="#E2D6CA" opacity=".55"/>
{box(3, 0, 170, 700)}
{box(1, 2, 1010, 700)}
<text x="{W/2}" y="{H-40}" font-family="Georgia, serif" font-size="26" fill="#6b5446" text-anchor="middle">{TITLE}</text>
</svg>'''
html = f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#fff}}</style></head><body>{svg}</body></html>'
open(OUT, "w", encoding="utf-8").write(html)
print("mockup html", OUT)
