"""Planche d'etiquettes imprimables pour les SRP 6x VRAC (references SRPVxxxx).

Lit Odoo (product.product, default_code like 'SRPV'), rend un code barre ITF-14
en SVG pur (aucune dependance externe) et sort un HTML A4 pret a imprimer.

Format : Avery L7165 / 99,1 x 67,7 mm, 8 etiquettes par feuille A4 (2 x 4).

CODE IMPRIME -- par defaut, le barcode Odoo tel quel, soit la convention maison
"1" + EAN-13 complet : c'est lui que les scanners lisent en reception et en
expedition, puisque c'est lui qui est dans product.product.barcode.
ATTENTION : ce code n'est pas un GTIN-14 conforme GS1 -- coller "1" devant un
EAN-13 entier laisse en place l'ancienne cle de controle, qui devient fausse
(le GTIN-14 se construit sur les 12 premiers chiffres, cle recalculee).
--gs1 imprime la version a cle recalculee, mais elle ne matchera plus Odoo
tant que les barcodes n'y sont pas repris. Le script signale l'ecart a chaque run.

Usage:
    "C:/Program Files/LibreOffice/program/python.exe" scripts/build_etiquettes_srp.py
    ... --refs SRPV0121,SRPV0895        (sous-ensemble)
    ... --gs1                           (cle GTIN-14 recalculee)
    ... --out chemin/etiquettes.html
"""
import argparse, os, sys, xmlrpc.client

URL = 'https://tea-tree.odoo.com'
DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'
PWD = os.environ.get('ODOO_PWD')          # depot PUBLIC : jamais de mot de passe en clair

# ---------------------------------------------------------------- ITF-14 (Interleaved 2 of 5)
PATTERNS = {
    '0': 'nnwwn', '1': 'wnnnw', '2': 'nwnnw', '3': 'wwnnn', '4': 'nnwnw',
    '5': 'wnwnn', '6': 'nwwnn', '7': 'nnnww', '8': 'wnnwn', '9': 'nwnwn',
}
NARROW = 1.0
WIDE = 2.5          # ratio 1:2.5, dans la tolerance GS1 (2.2 - 3.0)


def gtin14_key(first13):
    """Cle de controle GTIN-14 : poids 3-1 depuis la gauche sur 13 chiffres."""
    s = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(first13))
    return str((10 - s % 10) % 10)


def gtin14_ok(code):
    return (len(code) == 14 and code.isdigit()
            and gtin14_key(code[:13]) == code[13])


def to_gtin14(code):
    """1 + EAN-13 complet -> GTIN-14 conforme (cle recalculee sur 12 chiffres)."""
    base = code[:13]
    return base + gtin14_key(base)


def itf14_svg(code, width_mm=76.0, height_mm=19.0, quiet=10):
    """SVG ITF-14 : barres + bearer bar (cadre epais impose par la norme)."""
    if len(code) % 2:
        raise ValueError('ITF exige un nombre pair de chiffres')
    elements = []                                   # (is_bar, largeur en modules)
    for ch in 'nnnn':                               # start : n b, n s, n b, n s
        elements.append((len(elements) % 2 == 0, NARROW))
    for i in range(0, len(code), 2):
        bars, spaces = PATTERNS[code[i]], PATTERNS[code[i + 1]]
        for k in range(5):
            elements.append((True, WIDE if bars[k] == 'w' else NARROW))
            elements.append((False, WIDE if spaces[k] == 'w' else NARROW))
    for is_bar, w in ((True, WIDE), (False, NARROW), (True, NARROW)):   # stop
        elements.append((is_bar, w))

    modules = sum(w for _, w in elements)
    bearer = 4.5                                    # epaisseur du cadre, en modules
    total_w = modules + 2 * quiet
    total_h = 60.0                                  # hauteur logique des barres
    unit = width_mm / total_w                       # mm par module

    bars, x = [], quiet
    for is_bar, w in elements:
        if is_bar:
            bars.append(f'<rect x="{x:.3f}" y="{bearer:.2f}" width="{w:.3f}" '
                        f'height="{total_h - 2 * bearer:.2f}"/>')
        x += w
    frame = (f'<rect x="0" y="0" width="{total_w:.3f}" height="{bearer:.2f}"/>'
             f'<rect x="0" y="{total_h - bearer:.2f}" width="{total_w:.3f}" height="{bearer:.2f}"/>'
             f'<rect x="0" y="0" width="{bearer:.2f}" height="{total_h:.2f}"/>'
             f'<rect x="{total_w - bearer:.3f}" y="0" width="{bearer:.2f}" height="{total_h:.2f}"/>')
    return (f'<svg class="bc" viewBox="0 0 {total_w:.3f} {total_h:.2f}" '
            f'width="{width_mm}mm" height="{height_mm}mm" preserveAspectRatio="none" '
            f'shape-rendering="crispEdges">{frame}{"".join(bars)}</svg>')


def human(code):
    """15413393004169 -> 1 5413393 00416 9 (lecture GS1)."""
    return f'{code[0]} {code[1:8]} {code[8:13]} {code[13]}'


# ---------------------------------------------------------------- Odoo
def fetch(refs=None):
    if not PWD:
        sys.exit('ODOO_PWD absent de l\'environnement (voir memoire reference_odoo_creds).')
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    dom = [('default_code', 'like', 'SRPV')]
    if refs:
        dom = [('default_code', 'in', refs)]
    return models.execute_kw(DB, uid, PWD, 'product.product', 'search_read',
                             [dom], {'fields': ['default_code', 'name', 'barcode'],
                                     'order': 'default_code'})


def libelle(name):
    """'SRP 6x V0121 - Lady Dodo VRAC' -> ('Lady Dodo', 'V0121')."""
    unit = ''
    if ' - ' in name:
        head, tail = name.split(' - ', 1)
        unit = head.replace('SRP 6x', '').strip()
        name = tail
    return name.replace(' VRAC', '').strip(), unit


CSS = """
@page { size: A4 portrait; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; background: #ececec; font-family: "Helvetica Neue", Arial, sans-serif; }
.sheet {
  width: 210mm; height: 297mm; margin: 0 auto 6mm; background: #fff; padding: 13mm 4.75mm;
  display: grid; grid-template-columns: repeat(2, 99.1mm); grid-auto-rows: 67.7mm;
}
.lbl {
  padding: 4.5mm 5mm; display: flex; flex-direction: column; justify-content: space-between;
  overflow: hidden; color: #000;
}
.top { display: flex; justify-content: space-between; align-items: flex-start; gap: 3mm; }
.ref { font-size: 13pt; font-weight: 700; letter-spacing: .04em; }
.colis { font-size: 8.5pt; font-weight: 700; border: 1.1pt solid #000; padding: .7mm 2mm; white-space: nowrap; }
.prod { font-size: 15pt; font-weight: 700; line-height: 1.12; margin: 1mm 0 0; }
.unit { font-size: 8.5pt; letter-spacing: .06em; color: #444; margin-top: 1mm; }
.bcwrap { text-align: center; }
.bc { display: block; margin: 0 auto; }
.bc rect { fill: #000; }
.digits { font-family: "Courier New", monospace; font-size: 10.5pt; font-weight: 700;
          letter-spacing: .11em; margin-top: 1.1mm; }
.warn { font-size: 9pt; font-weight: 700; color: #b00; }
/* reperes de decoupe : ecran uniquement */
@media screen { .lbl { outline: .3mm dashed #c9c9c9; outline-offset: -.15mm; } }
@media print { body { background: #fff; } .sheet { margin: 0; page-break-after: always; } }
"""


def render(prods, out, gs1=False):
    cards, skipped, bad_key = [], [], []
    for p in prods:
        ref = p['default_code']
        prod, unit = libelle(p['name'])
        code = (p['barcode'] or '').strip()
        if len(code) != 14 or not code.isdigit():
            skipped.append((ref, f'barcode absent ou pas a 14 chiffres ({code or "vide"})'))
            continue
        if not gtin14_ok(code):
            bad_key.append((ref, code, to_gtin14(code)))
        if gs1:
            code = to_gtin14(code)
        cards.append(f"""<div class="lbl">
  <div>
    <div class="top"><span class="ref">{ref}</span><span class="colis">COLIS DE 6</span></div>
    <div class="prod">{prod}</div>
    <div class="unit">unite : {unit}</div>
  </div>
  <div class="bcwrap">{itf14_svg(code)}<div class="digits">{human(code)}</div></div>
</div>""")

    per_page = 8
    pages = [cards[i:i + per_page] for i in range(0, len(cards), per_page)] or [[]]
    sheets = []
    for page in pages:
        blanks = ['<div class="lbl"></div>'] * (per_page - len(page))
        sheets.append('<div class="sheet">' + ''.join(page + blanks) + '</div>')

    html = (f'<title>Etiquettes SRP 6x VRAC</title>\n<style>{CSS}</style>\n'
            + '\n'.join(sheets) + '\n')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    return len(cards), skipped, bad_key


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', help='liste SRPVxxxx separee par des virgules')
    ap.add_argument('--gs1', action='store_true',
                    help='imprimer le GTIN-14 a cle recalculee au lieu du barcode Odoo')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'etiquettes', 'Etiquettes_SRP_6x_VRAC.html'))
    a = ap.parse_args()

    refs = [r.strip() for r in a.refs.split(',')] if a.refs else None
    prods = fetch(refs)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    n, skipped, bad_key = render(prods, a.out, gs1=a.gs1)
    src = 'GTIN-14 conforme (cle recalculee)' if a.gs1 else 'barcode Odoo tel quel'
    print(f'{n} etiquettes ecrites ({src}) -> {a.out}')
    for ref, why in skipped:
        print(f'  ignore {ref} : {why}')
    if bad_key:
        print(f'\n{len(bad_key)} code(s) a cle de controle GTIN-14 fausse dans Odoo :')
        for ref, cur, fix in bad_key:
            print(f'  {ref:12} Odoo {cur}  ->  conforme {fix}')
        print('  (voir l\'en-tete du script : "1" + EAN-13 complet garde une cle perimee)')
    if not n:
        sys.exit(1)
