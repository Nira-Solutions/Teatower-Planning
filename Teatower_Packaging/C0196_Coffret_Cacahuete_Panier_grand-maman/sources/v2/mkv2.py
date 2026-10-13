src = open("build_c0196.py", encoding="utf-8").read()
R = [
 # palette
 ('CREAM2 = "#EFE1C6"', 'CREAM2 = "#E27A6B"\nCORAL = "#EC8475"\nCORALD = "#D9624F"\nCORALL = "#F6B3A8"\nINK = "#1E1A18"\nWHITE = "#FFF8F2"'),
 # fond papier corail
 ('<rect width="7" height="7" fill="{CREAM}"/>', '<rect width="7" height="7" fill="{CORAL}"/>'),
 # vichy corail
 ('<rect width="2.5" height="5" fill="{RED}" opacity=".45"/>', '<rect width="2.5" height="5" fill="{CORALD}" opacity=".55"/>'),
 ('<rect width="5" height="2.5" fill="{RED}" opacity=".45"/>', '<rect width="5" height="2.5" fill="{CORALD}" opacity=".55"/>'),
 # liseré sous le couvercle + pointillés
 ('fill="{REDD}" opacity=".7"/>\')', 'fill="{CORALD}" opacity=".9"/>\')'),
 ('r=".45" fill="{RED}" opacity=".55"/>', 'r=".45" fill="{WHITE}" opacity=".8"/>'),
 # coeurs épars
 ('    body.append(heart(x, y, s, RED, .55))', '    body.append(heart(x, y, s, WHITE, .75))'),
 # panneau 4 : carré blanc + logo noir, façon doypack
 ('body.append(f\'<path d="M{c4-bw/2},{by} h{bw} v{bw} h{-bw+4} a4,4 0 0 1 -4,-4Z" fill="url(#ttred)"/>\')',
  'body.append(f\'<path d="M{c4-bw/2-1.8},{by-1.8} h{bw+3.6} v{bw+3.6} h{-bw-3.6+5.5} a5.5,5.5 0 0 1 -5.5,-5.5Z" fill="{CORALL}"/>\')\nbody.append(f\'<path d="M{c4-bw/2},{by} h{bw} v{bw} h{-bw+4} a4,4 0 0 1 -4,-4Z" fill="#FFFFFF"/>\')'),
 ('lg, lh = logo(c4 - 12.5, by + 4.6, 25, "#FBEFE0")', 'lg, lh = logo(c4 - 12.5, by + 4.6, 25, INK)'),
 ('font-size="3.3" letter-spacing=".55" fill="{BROWN}"', 'font-size="3.3" letter-spacing=".55" fill="{WHITE}"'),
 ('font-size="6.2" fill="{RED}" text-anchor="middle">Le panier de grand-maman', 'font-size="6.2" fill="{WHITE}" text-anchor="middle">Le panier de grand-maman'),
 ('body.append(heart(c4 + 34.5, by + bw + 10.8, .9, RED, .9))', 'body.append(heart(c4 + 34.5, by + bw + 10.8, .9, WHITE, .9))'),
 # couvercle : logo blanc/noir, accents corail
 ('lid.append(f\'<path d="M{lx},{ly} h{bw2} v{bw2} h{-bw2+4} a4,4 0 0 1 -4,-4Z" fill="url(#ttred)"/>\')',
  'lid.append(f\'<path d="M{lx-1.5},{ly-1.5} h{bw2+3} v{bw2+3} h{-bw2-3+5} a5,5 0 0 1 -5,-5Z" fill="{CORAL}"/>\')\nlid.append(f\'<path d="M{lx},{ly} h{bw2} v{bw2} h{-bw2+4} a4,4 0 0 1 -4,-4Z" fill="#FFFFFF"/>\')'),
 ('lg, lh = logo(cx - 11, ly + 4, 22, "#FBEFE0")', 'lg, lh = logo(cx - 11, ly + 4, 22, INK)'),
 ('font-size="8.2" fill="{RED}" text-anchor="middle">Le panier<', 'font-size="8.2" fill="{CORALD}" text-anchor="middle">Le panier<'),
 ('font-size="8.2" fill="{RED}" text-anchor="middle">de grand-maman<', 'font-size="8.2" fill="{CORALD}" text-anchor="middle">de grand-maman<'),
 ('font-size="4.6" fill="{RED}" text-anchor="middle">Comme chez', 'font-size="4.6" fill="{CORALD}" text-anchor="middle">Comme chez'),
 ('lid.append(heart(cx - 18, cy - 12, .6, RED, .6) + heart(cx + 18, cy - 12, .6, RED, .6))', 'lid.append(heart(cx - 18, cy - 12, .6, CORAL, .8) + heart(cx + 18, cy - 12, .6, CORAL, .8))'),
 ('ACC = RED', 'ACC = CORALD'),
 ('TXT = BROWN', 'TXT = WHITE'),
]
for a, b in R:
    n = src.count(a)
    assert n >= 1, ("NOT FOUND", a[:70])
    src = src.replace(a, b)
# trous de dentelle / napperon / coeurs de la fiche en corail
src = src.replace('fill="{RED}" opacity=".35"/>\')', 'fill="{CORALD}" opacity=".45"/>\')')
src = src.replace('stroke="{RED}" stroke-width=".25" stroke-dasharray=".8 .6" opacity=".6"', 'stroke="{CORALD}" stroke-width=".25" stroke-dasharray=".8 .6" opacity=".7"')
src = src.replace('fill="{RED}" opacity=".28"/>', 'fill="{CORALD}" opacity=".4"/>').replace('fill="{RED}" opacity=".22"/>', 'fill="{CORALD}" opacity=".35"/>').replace('fill="{RED}" opacity=".2" transform', 'fill="{CORALD}" opacity=".3" transform')
src = src.replace('stroke="{RED}" stroke-width=".3" stroke-dasharray="1 .9" opacity=".5"', 'stroke="{CORALD}" stroke-width=".3" stroke-dasharray="1 .9" opacity=".6"')
src = src.replace('body.append(heart(tagx + 6.2, yy - 1.0, .42, RED))', 'body.append(heart(tagx + 6.2, yy - 1.0, .42, CORALD))')
src = src.replace('font-size="4.4" fill="{RED}" text-anchor="end">x2', 'font-size="4.4" fill="{CORALD}" text-anchor="end">x2')
src = src.replace('# ---------- palette ----------', '# ---------- palette (V2 : corail du doypack 279) ----------')
open("build_c0196_v2.py", "w", encoding="utf-8").write(src)
print("v2 ok")
