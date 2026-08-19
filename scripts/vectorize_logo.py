# -*- coding: utf-8 -*-
"""
Vectorisation du logo Teatower (PNG aplat binaire -> SVG)
---------------------------------------------------------
Aucun outil de vectorisation n'est installe sur le poste (ni Inkscape, ni
potrace, ni Illustrator) : ce script fait le trace lui-meme. C'est possible
parce que la source est un aplat noir/blanc PUR (pas de degrade, pas
d'antialiasing significatif) - le cas ideal pour un trace exact.

Chaine :
  1. seuillage RGBA -> 2 masques (le carre noir ; les formes blanches)
  2. extraction des contours par ARETES entre pixel interieur et exterieur
     (plus robuste que le suivi de Moore : gere nativement les trous des
     lettres 'a', 'e', 'o', 'B', 'R' et les composantes multiples)
  3. chainage des aretes en boucles fermees
  4. simplification Douglas-Peucker (supprime l'escalier du bitmap)
  5. lissage Catmull-Rom -> Bezier cubique, avec DETECTION DE COINS :
     un sommet dont l'angle depasse le seuil reste anguleux (empeche
     d'arrondir les empattements de BELGIAN TEA HOUSE et les angles
     de la pagode)
  6. sortie SVG, un <path> par couleur en fill-rule evenodd

Usage : python vectorize_logo.py
"""
import io, math
from PIL import Image, ImageChops

SRC = 'data/Logo_TeaTower_CarreNoir.png'
OUT = 'brand/Teatower_logo_blanc_carre_noir.svg'
OUT_INK = 'brand/Teatower_logo_blanc_transparent.svg'

EPS_DP = 0.5       # px : tolerance Douglas-Peucker
ANGLE_COIN = 50.0  # deg : au-dela, le sommet reste anguleux
ANGLE_PLAT = 6.0   # deg : en-deca, on emet une DROITE (garde BELGIAN TEA HOUSE net)
TENSION = 1.0


# ---------------------------------------------------------------- masques
def masques(path):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    a = im.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
    lum = im.convert('L').point(lambda v: 255 if v >= 128 else 0)
    opaque = a                            # tout le carre (fond + glyphes)
    encre = ImageChops.multiply(a, lum)   # glyphes blancs opaques
    return opaque, encre, w, h


# -------------------------------------------------- pixels de bord (rapide)
def _pixels_ou(mask, dx, dy):
    """pixels de mask dont le voisin (dx,dy) est HORS mask"""
    w, h = mask.size
    shifted = ImageChops.offset(mask, dx, dy)
    # ImageChops.offset est circulaire : on neutralise la bande qui a boucle
    if dy > 0:
        shifted.paste(0, (0, 0, w, dy))
    elif dy < 0:
        shifted.paste(0, (0, h + dy, w, h))
    if dx > 0:
        shifted.paste(0, (0, 0, dx, h))
    elif dx < 0:
        shifted.paste(0, (w + dx, 0, w, h))
    return ImageChops.subtract(mask, shifted)


def _coords(img, w, h):
    data = img.tobytes()
    out = []
    for y in range(h):
        row = data[y * w:(y + 1) * w]
        i = row.find(255)
        while i != -1:
            out.append((i, y))
            i = row.find(255, i + 1)
    return out


def aretes(mask, w, h):
    """dict point_depart -> liste de points d'arrivee (sens horaire, y vers le bas)"""
    E = {}

    def add(p, q):
        E.setdefault(p, []).append(q)

    # voisin au-dessus hors masque -> arete haute, vers la droite
    for x, y in _coords(_pixels_ou(mask, 0, 1), w, h):
        add((x, y), (x + 1, y))
    # voisin a droite hors masque -> arete droite, vers le bas
    for x, y in _coords(_pixels_ou(mask, -1, 0), w, h):
        add((x + 1, y), (x + 1, y + 1))
    # voisin en dessous hors masque -> arete basse, vers la gauche
    for x, y in _coords(_pixels_ou(mask, 0, -1), w, h):
        add((x + 1, y + 1), (x, y + 1))
    # voisin a gauche hors masque -> arete gauche, vers le haut
    for x, y in _coords(_pixels_ou(mask, 1, 0), w, h):
        add((x, y + 1), (x, y))
    return E


def boucles(E):
    """chaine les aretes en polygones fermes"""
    E = {k: list(v) for k, v in E.items()}
    out = []
    for s in list(E.keys()):
        while E.get(s):
            poly = [s]
            cur, prev_d = s, None
            while True:
                cands = E.get(cur)
                if not cands:
                    break
                if len(cands) == 1 or prev_d is None:
                    nxt = cands[0]
                else:
                    # sommet ambigu (pixels en contact diagonal) : on prend le
                    # virage le plus a droite -> avant-plan 4-connexe, les deux
                    # blobs diagonaux restent separes
                    def score(q, cur=cur, prev_d=prev_d):
                        d = (q[0] - cur[0], q[1] - cur[1])
                        cross = prev_d[0] * d[1] - prev_d[1] * d[0]
                        dot = prev_d[0] * d[0] + prev_d[1] * d[1]
                        return (-cross, -dot)
                    nxt = sorted(cands, key=score)[0]
                cands.remove(nxt)
                prev_d = (nxt[0] - cur[0], nxt[1] - cur[1])
                cur = nxt
                if cur == s:
                    break
                poly.append(cur)
            if len(poly) >= 4:
                out.append(poly)
    return out


# ------------------------------------------------------------ simplification
def douglas_peucker(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    nrm = math.hypot(dx, dy)
    dmax, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        if nrm:
            d = abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / nrm
        else:
            d = math.hypot(p[0] - a[0], p[1] - a[1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return douglas_peucker(pts[:idx + 1], eps)[:-1] + douglas_peucker(pts[idx:], eps)
    return [a, b]


def simplifie_ferme(poly, eps):
    # on coupe la boucle en 2 arcs : DP degenere sur un contour ferme
    n = len(poly)
    if n < 8:
        return poly
    h = n // 2
    a = douglas_peucker(poly[:h + 1], eps)
    b = douglas_peucker(poly[h:] + [poly[0]], eps)
    res = a[:-1] + b[:-1]
    return res if len(res) >= 3 else poly


# ------------------------------------------------------------------ lissage
def _f(v):
    s = '%.2f' % v
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s if s not in ('-0', '') else '0'


def _angle(p0, p1, p2):
    """angle de changement de direction au sommet p1, en degres"""
    v1 = (p1[0] - p0[0], p1[1] - p0[1])
    v2 = (p2[0] - p1[0], p2[1] - p1[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return 180.0
    cosang = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
    return math.degrees(math.acos(cosang))


def vers_bezier(pts, seuil_coin, seuil_plat, tension):
    """polygone ferme -> data SVG, coins preserves et droites gardees droites

    Les tangentes sont normalisees puis remises a l'echelle de la CORDE du
    segment courant (parametrage par longueur d'arc). Une Catmull-Rom uniforme
    (P2-P0)/6 explose des que deux segments voisins ont des longueurs tres
    differentes - c'est ce qui creait un pic dans le coin arrondi du carre et
    bombait les lettres droites de BELGIAN TEA HOUSE.
    """
    n = len(pts)
    if n < 3:
        return ''

    ang = [_angle(pts[(i - 1) % n], pts[i], pts[(i + 1) % n]) for i in range(n)]
    coin = [a > seuil_coin for a in ang]

    def tangente(i):
        """direction unitaire de la courbe au sommet i"""
        if coin[i]:
            return None
        p0, p2 = pts[(i - 1) % n], pts[(i + 1) % n]
        vx, vy = (p2[0] - p0[0]) * tension, (p2[1] - p0[1]) * tension
        nrm = math.hypot(vx, vy)
        return None if nrm == 0 else (vx / nrm, vy / nrm)

    tg = [tangente(i) for i in range(n)]

    d = ['M%s,%s' % (_f(pts[0][0]), _f(pts[0][1]))]
    for i in range(n):
        p1, p2 = pts[i], pts[(i + 1) % n]
        j = (i + 1) % n
        # segment entre 2 sommets plats et sans courbure -> vraie droite
        if ang[i] < seuil_plat and ang[j] < seuil_plat:
            d.append('L%s,%s' % (_f(p2[0]), _f(p2[1])))
            continue
        L = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 3.0
        t1, t2 = tg[i], tg[j]
        if t1 is None:
            ux, uy = (p2[0] - p1[0]), (p2[1] - p1[1])
            m = math.hypot(ux, uy) or 1.0
            t1 = (ux / m, uy / m)
        if t2 is None:
            ux, uy = (p2[0] - p1[0]), (p2[1] - p1[1])
            m = math.hypot(ux, uy) or 1.0
            t2 = (ux / m, uy / m)
        c1 = (p1[0] + t1[0] * L, p1[1] + t1[1] * L)
        c2 = (p2[0] - t2[0] * L, p2[1] - t2[1] * L)
        d.append('C%s,%s %s,%s %s,%s' % (_f(c1[0]), _f(c1[1]), _f(c2[0]),
                                         _f(c2[1]), _f(p2[0]), _f(p2[1])))
    d.append('Z')
    return ''.join(d)


def trace(mask, w, h, label):
    polys = [p for p in boucles(aretes(mask, w, h)) if len(p) >= 8]
    simples = [simplifie_ferme(p, EPS_DP) for p in polys]
    ds = [vers_bezier(s, ANGLE_COIN, ANGLE_PLAT, TENSION) for s in simples if len(s) >= 3]
    print('  %-22s %4d contours | %7d pts -> %6d apres simplification'
          % (label, len(polys), sum(len(p) for p in polys), sum(len(s) for s in simples)))
    return ' '.join(ds)


def main():
    print('Vectorisation du logo Teatower')
    opaque, encre, w, h = masques(SRC)
    print('  source %s (%dx%d)' % (SRC, w, h))
    d_fond = trace(opaque, w, h, 'carre noir')
    d_encre = trace(encre, w, h, 'formes blanches')

    # artboard recadre sur le pave noir : la marge transparente de la source
    # est arbitraire et genante des qu'on place le logo dans une maquette.
    # Les DEUX fichiers gardent le meme viewBox -> ils restent interchangeables
    # au meme emplacement (calage identique).
    x0, y0, x1, y1 = opaque.getbbox()
    bw, bh = x1 - x0, y1 - y0
    print('  artboard recadre : %d,%d %dx%d (ratio %.3f)' % (x0, y0, bw, bh, bw / float(bh)))
    entete = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d" '
              'width="%d" height="%d" role="img" aria-label="Teatower">'
              '<title>Teatower</title>' % (x0, y0, bw, bh, bw, bh))
    svg = (entete
           + '<path fill="#000000" fill-rule="evenodd" d="%s"/>' % d_fond
           + '<path fill="#FFFFFF" fill-rule="evenodd" d="%s"/>' % d_encre
           + '</svg>')
    io.open(OUT, 'w', encoding='utf-8').write(svg)
    print('  -> %s  (%.0f Ko)' % (OUT, len(svg) / 1024))

    svg2 = (entete
            + '<path fill="#FFFFFF" fill-rule="evenodd" d="%s"/>' % d_encre
            + '</svg>')
    io.open(OUT_INK, 'w', encoding='utf-8').write(svg2)
    print('  -> %s  (%.0f Ko)' % (OUT_INK, len(svg2) / 1024))


if __name__ == '__main__':
    main()
