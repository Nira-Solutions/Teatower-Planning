src = open("build_c0196_v2.py", encoding="utf-8").read()
R = [
 ('fill="url(#vichy)"/>\')\nbody.append(f\'<rect x="0" y="{LIDLINE-0.6}"', 'fill="{CORAL}"/>\')\nbody.append(f\'<rect x="0" y="{LIDLINE-0.6}"'),
 ('height="{H1-FOLD}" fill="url(#vichy)" opacity=".35"/>', 'height="{H1-FOLD}" fill="{CORAL}"/>'),
 ('lid = [f\'<rect width="{W2}" height="{H2}" fill="url(#vichy)"/>\']', 'lid = [f\'<rect width="{W2}" height="{H2}" fill="{CORAL}"/>\']'),
 ('<rect width="7" height="7" fill="{CORAL}"/>', '<rect width="7" height="7" fill="{CORAL}"/>'),
 ('palette (V2 : corail du doypack 279)', 'palette (V3 : corail uni du doypack 279)'),
]
for a, b in R:
    assert a in src, a[:60]; src = src.replace(a, b)
# fond uni : pas de grain papier
src = src.replace('<circle cx="1.3" cy="2.1" r=".18" fill="{CREAM2}"/>', '').replace('<circle cx="4.9" cy="5.6" r=".22" fill="{CREAM2}"/>', '').replace('<circle cx="5.6" cy="1.0" r=".14" fill="{CREAM2}"/>', '')
open("build_c0196_v3.py", "w", encoding="utf-8").write(src); print("v3 ok")
