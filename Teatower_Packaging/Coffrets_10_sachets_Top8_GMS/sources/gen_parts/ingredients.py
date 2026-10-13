

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
