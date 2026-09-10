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
import argparse, json, os, sys, xmlrpc.client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def itf14_elements(code):
    """Suite (est_une_barre, largeur en modules) du symbole ITF-14."""
    if len(code) % 2:
        raise ValueError('ITF exige un nombre pair de chiffres')
    elements = []
    for _ in range(4):                              # start : n b, n s, n b, n s
        elements.append((len(elements) % 2 == 0, NARROW))
    for i in range(0, len(code), 2):
        bars, spaces = PATTERNS[code[i]], PATTERNS[code[i + 1]]
        for k in range(5):
            elements.append((True, WIDE if bars[k] == 'w' else NARROW))
            elements.append((False, WIDE if spaces[k] == 'w' else NARROW))
    for is_bar, w in ((True, WIDE), (False, NARROW), (True, NARROW)):   # stop
        elements.append((is_bar, w))
    return elements


def itf14_svg(code, width_mm=76.0, height_mm=19.0, quiet=10):
    """SVG ITF-14 : barres + bearer bar (cadre epais impose par la norme)."""
    elements = itf14_elements(code)
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


def grammages():
    """{'V0631': 80, ...} depuis le catalogue GMS ; {} si le fichier manque."""
    path = os.path.join(ROOT, 'gms-catalog', 'catalog.json')
    if not os.path.exists(path):
        return {}

    def walk(o):
        if isinstance(o, dict):
            if 'code' in o and 'grammage_g' in o:
                yield o
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)

    with open(path, encoding='utf-8') as f:
        return {x['code']: x['grammage_g'] for x in walk(json.load(f))
                if str(x.get('code', '')).startswith('V0')}


def par_ref(spec):
    """'K071273' -> valeur unique ; 'SRPV0631=K07,SRPV0121=K12' -> dict par ref.

    Retourne (defaut, {ref: valeur}). Une valeur vide laisse un champ a remplir
    a la main sur la planche imprimee.
    """
    if not spec:
        return '', {}
    if '=' not in spec:
        return spec.strip(), {}
    out = {}
    for part in spec.split(','):
        ref, _, val = part.partition('=')
        out[ref.strip()] = val.strip()
    return '', out


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
.trace { display: flex; gap: 4mm; font-size: 9pt; margin-top: 1.6mm; }
.trace > div { flex: 1; display: flex; align-items: baseline; gap: 1.5mm; }
.trace .k { font-weight: 700; letter-spacing: .04em; white-space: nowrap; }
.trace .v { flex: 1; font-family: "Courier New", monospace; font-weight: 700;
            border-bottom: .35mm solid #000; min-height: 3.6mm; padding-left: .5mm;
            outline: none; }
.trace .v:empty::before { content: attr(data-ph); color: #bbb; font-weight: 400; }
.trace .v:focus { background: #fff6cc; }
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


def page(title, css, body, script=''):
    """Document complet.

    lang="fr" + translate="no" + <meta name="google" content="notranslate"> :
    sans ca, Chrome detecte la page comme anglaise et la traduit tout seul chez
    le destinataire -- "Lady Dodo" devient "Dame Dodo" et "Lot" devient
    "Parcelle". Sur une etiquette logistique, le nom produit et le numero de lot
    ne doivent jamais bouger.
    """
    return (f'<!doctype html>\n<html lang="fr" translate="no">\n<head>\n'
            f'<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta name="google" content="notranslate">\n'
            f'<title>{title}</title>\n<style>{css}</style>\n</head>\n'
            f'<body class="notranslate">\n{body}\n'
            + (f'<script>{script}</script>\n' if script else '')
            + '</body>\n</html>\n')


JS = r"""
// Lot et DDM editables : on tape dans une case, les 8 etiquettes de la meme
// reference suivent. Les valeurs sont gardees dans le navigateur (localStorage)
// pour survivre a un rechargement ; l'impression les prend telles qu'affichees.
(function () {
  var KEY = 'srp-etiquettes-v1', mem = {};
  try { mem = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { mem = {}; }

  function cells() { return document.querySelectorAll('.trace .v'); }
  function id(el) { return el.dataset.ref + '|' + el.dataset.f; }

  cells().forEach(function (el) {
    var v = mem[id(el)];
    if (v && !el.textContent.trim()) el.textContent = v;

    el.addEventListener('input', function () {
      var val = el.textContent.replace(/\s+/g, ' ').trim();
      cells().forEach(function (o) { if (o !== el && id(o) === id(el)) o.textContent = val; });
      mem[id(el)] = val;
      try { localStorage.setItem(KEY, JSON.stringify(mem)); } catch (e) {}
    });

    // pas de retour a la ligne ni de mise en forme collee
    el.addEventListener('keydown', function (e) { if (e.key === 'Enter') e.preventDefault(); });
    el.addEventListener('paste', function (e) {
      e.preventDefault();
      var t = (e.clipboardData || window.clipboardData).getData('text');
      document.execCommand('insertText', false, t.replace(/\s+/g, ' ').trim());
    });
  });
})();
"""


def render(prods, out, gs1=False, lot='', lots=None, ddm='', ddms=None, mixte=False):
    cards, skipped, bad_key = [], [], []
    gram = grammages()
    lots, ddms = lots or {}, ddms or {}
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
        g = gram.get(unit)
        colis = f'COLIS DE 6 &times; {g} g' if g else 'COLIS DE 6'
        cards.append(f"""<div class="lbl">
  <div>
    <div class="top"><span class="ref" translate="no">{ref}</span><span class="colis">{colis}</span></div>
    <div class="prod" translate="no">{prod}</div>
    <div class="unit">unite : <span translate="no">{unit}</span></div>
    <div class="trace">
      <div><span class="k" translate="no">Lot</span><span class="v" contenteditable="true"
           spellcheck="false" translate="no"
           data-f="lot" data-ref="{ref}" data-ph="a completer">{lots.get(ref, lot)}</span></div>
      <div><span class="k" translate="no">DDM</span><span class="v" contenteditable="true"
           spellcheck="false" translate="no"
           data-f="ddm" data-ref="{ref}" data-ph="MM/AAAA">{ddms.get(ref, ddm)}</span></div>
    </div>
  </div>
  <div class="bcwrap">{itf14_svg(code)}<div class="digits">{human(code)}</div></div>
</div>""")

    per_page = 8
    if mixte:
        pages = [cards[i:i + per_page] for i in range(0, len(cards), per_page)] or [[]]
    else:
        # une reference par planche : 8 etiquettes identiques, prete a coller sur un lot
        pages = [[c] * per_page for c in cards] or [[]]
    sheets = []
    for pg in pages:
        blanks = ['<div class="lbl"></div>'] * (per_page - len(pg))
        sheets.append('<div class="sheet">' + ''.join(pg + blanks) + '</div>')

    html = page('Etiquettes SRP 6x VRAC', CSS, '\n'.join(sheets), JS)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    return len(cards), skipped, bad_key


INDEX_CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #f4f4f2; color: #1a1a1a; padding: 28px 20px 60px;
       font: 15px/1.5 "Helvetica Neue", Arial, sans-serif; }
.wrap { max-width: 860px; margin: 0 auto; }
h1 { font-size: 21px; margin: 0 0 4px; letter-spacing: -.01em; }
.sub { color: #666; font-size: 13.5px; margin: 0 0 22px; }
ul { list-style: none; margin: 0; padding: 0;
     display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 9px; }
a.card { display: block; background: #fff; border: 1px solid #e0e0dc; border-radius: 7px;
         padding: 11px 13px; text-decoration: none; color: inherit; }
a.card:hover { border-color: #9a9a92; background: #fffdf5; }
.r { font-weight: 700; font-size: 14px; letter-spacing: .03em; }
.n { font-size: 13.5px; margin-top: 1px; }
.g { font-size: 11.5px; color: #777; margin-top: 3px; letter-spacing: .04em; }
.note { margin-top: 26px; font-size: 13px; color: #666; border-top: 1px solid #e0e0dc;
        padding-top: 14px; }
@media (prefers-color-scheme: dark) {
  body { background: #17171a; color: #ececec; }
  a.card { background: #212126; border-color: #34343a; }
  a.card:hover { border-color: #6a6a76; background: #26262c; }
  .sub, .g, .note { color: #a0a0a8; }
  .note { border-top-color: #34343a; }
}
"""


def write_index(made, path):
    """Page d'accueil : une carte par planche."""
    gram = grammages()
    items = []
    for p, fname in made:
        prod, unit = libelle(p['name'])
        g = gram.get(unit)
        items.append(
            f'<li><a class="card" href="{fname}">'
            f'<div class="r">{p["default_code"]}</div>'
            f'<div class="n">{prod}</div>'
            f'<div class="g">unite {unit} &middot; colis de 6'
            + (f' &times; {g} g' if g else '') + '</div></a></li>')
    body = (f'<div class="wrap"><h1>Etiquettes SRP 6&times; VRAC</h1>'
            f'<p class="sub">{len(made)} planches &middot; une reference par planche, '
            f'8 etiquettes identiques (Avery L7165, 99,1 &times; 67,7 mm)</p>'
            f'<ul>{"".join(items)}</ul>'
            f'<p class="note">Ouvrir une planche, cliquer sur <b>Lot</b> et sur <b>DDM</b> '
            f'pour les saisir &mdash; les 8 etiquettes suivent &mdash; puis imprimer.</p></div>')
    html = page('Etiquettes SRP 6x VRAC', INDEX_CSS, body)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


def render_split(prods, outdir, **kw):
    """Un fichier HTML par reference + un index."""
    os.makedirs(outdir, exist_ok=True)
    made, skipped, bad_key = [], [], []
    for p in prods:
        fname = p['default_code'] + '.html'
        path = os.path.join(outdir, fname)
        n, sk, bk = render([p], path, **kw)
        skipped += sk
        bad_key += bk
        if n:
            made.append((p, fname))
        elif os.path.exists(path):
            os.remove(path)
    write_index(made, os.path.join(outdir, 'index.html'))
    return made, skipped, bad_key


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', help='liste SRPVxxxx separee par des virgules')
    ap.add_argument('--gs1', action='store_true',
                    help='imprimer le GTIN-14 a cle recalculee au lieu du barcode Odoo')
    ap.add_argument('--lot', help='lot unique, ou "SRPV0631=K071273,SRPV0121=K07..." ; '
                                  'vide = champ a remplir a la main')
    ap.add_argument('--ddm', help='DDM unique (ex. 10/2028), ou "REF=valeur,..." ; '
                                  'vide = champ a remplir a la main')
    ap.add_argument('--mixte', action='store_true',
                    help='8 references differentes par planche (defaut : 8 etiquettes '
                         'identiques, une seule reference par planche)')
    ap.add_argument('--split', metavar='DOSSIER',
                    help='un fichier HTML par reference + index.html dans ce dossier')
    ap.add_argument('--out', default=os.path.join(ROOT, 'etiquettes',
                                                  'Etiquettes_SRP_6x_VRAC.html'))
    a = ap.parse_args()

    refs = [r.strip() for r in a.refs.split(',')] if a.refs else None
    prods = fetch(refs)
    lot, lots = par_ref(a.lot)
    ddm, ddms = par_ref(a.ddm)
    src = 'GTIN-14 conforme (cle recalculee)' if a.gs1 else 'barcode Odoo tel quel'
    kw = dict(gs1=a.gs1, mixte=a.mixte, lot=lot, lots=lots, ddm=ddm, ddms=ddms)

    if a.split:
        made, skipped, bad_key = render_split(prods, a.split, **kw)
        n = len(made)
        print(f'{n} planches ecrites ({src}) -> {a.split}')
        print(f'  index -> {os.path.join(a.split, "index.html")}')
    else:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        n, skipped, bad_key = render(prods, a.out, **kw)
        print(f'{n} planches ecrites ({src}) -> {a.out}')
    for ref, why in skipped:
        print(f'  ignore {ref} : {why}')
    if bad_key:
        print(f'\n{len(bad_key)} code(s) a cle de controle GTIN-14 fausse dans Odoo :')
        for ref, cur, fix in bad_key:
            print(f'  {ref:12} Odoo {cur}  ->  conforme {fix}')
        print('  (voir l\'en-tete du script : "1" + EAN-13 complet garde une cle perimee)')
    if not n:
        sys.exit(1)
