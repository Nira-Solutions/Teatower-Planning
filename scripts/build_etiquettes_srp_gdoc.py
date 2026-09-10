"""Variante Google Docs des etiquettes SRP 6x VRAC.

Google Docs n'affiche pas de SVG : le code barre ITF-14 est donc rasterise en
PNG (encodeur maison, aucune dependance externe) et embarque en data-URI dans
un HTML que Drive convertit en Document. Une planche = une reference, 8
etiquettes identiques dans un tableau 2 x 4, comme la version imprimable.

Lot et DDM restent des champs texte : dans Docs ils s'editent directement.

Usage:
    "C:/Program Files/LibreOffice/program/python.exe" \
        scripts/build_etiquettes_srp_gdoc.py --refs SRPV0631 --out-dir _scratchpad/gdoc
"""
import argparse, base64, os, struct, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_etiquettes_srp import (          # noqa: E402
    fetch, grammages, human, itf14_elements, libelle, par_ref, ROOT)


# ---------------------------------------------------------------- PNG (8 bits, niveaux de gris)
def png_gray(rows, w, h):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)

    def chunk(tag, data):
        body = tag + data
        return (struct.pack('>I', len(data)) + body
                + struct.pack('>I', zlib.crc32(body) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))


def itf14_png(code, scale=4, quiet=10, ratio_hw=19.0 / 76.0):
    """ITF-14 en PNG, proportions identiques a la version imprimee (76 x 19 mm)."""
    elements = itf14_elements(code)
    modules = sum(w for _, w in elements) + 2 * quiet
    w = int(round(modules * scale))
    h = int(round(w * ratio_hw))
    bearer = max(2, int(round(h * 4.5 / 60)))

    WHITE, BLACK = 255, 0
    rows = [[WHITE] * w for _ in range(h)]

    # barres, entre les deux bearer bars horizontales
    x = quiet
    for is_bar, mw in elements:
        if is_bar:
            x0, x1 = int(round(x * scale)), int(round((x + mw) * scale))
            for y in range(bearer, h - bearer):
                for px in range(x0, min(x1, w)):
                    rows[y][px] = BLACK
        x += mw

    # cadre : bearer bars haut/bas + montants gauche/droit (norme ITF-14)
    for y in list(range(bearer)) + list(range(h - bearer, h)):
        rows[y] = [BLACK] * w
    for y in range(h):
        for px in list(range(bearer)) + list(range(w - bearer, w)):
            rows[y][px] = BLACK

    return png_gray(rows, w, h)


def data_uri(png):
    return 'data:image/png;base64,' + base64.b64encode(png).decode('ascii')


# ---------------------------------------------------------------- rendu
CELL = """<td style="padding:10pt 12pt;border:1pt dashed #cccccc;vertical-align:top">
<p style="margin:0;font-size:13pt;font-weight:bold">{ref}</p>
<p style="margin:0;font-size:8pt">COLIS DE 6 &times; {gram}</p>
<p style="margin:6pt 0 0;font-size:14pt;font-weight:bold">{prod}</p>
<p style="margin:0;font-size:8pt;color:#444444">unite : {unit}</p>
<p style="margin:6pt 0 0;font-size:9pt">Lot : {lot}</p>
<p style="margin:0;font-size:9pt">DDM : {ddm}</p>
<p style="margin:6pt 0 0"><img src="{img}" width="250" height="62"></p>
<p style="margin:0;font-size:10pt;font-family:'Courier New'"><b>{digits}</b></p>
</td>"""


def doc_html(p, gram, lot, ddm):
    prod, unit = libelle(p['name'])
    code = (p['barcode'] or '').strip()
    cell = CELL.format(ref=p['default_code'], prod=prod, unit=unit,
                       gram=f'{gram} g' if gram else '&mdash;',
                       lot=lot or '________________',
                       ddm=ddm or '________________',
                       img=data_uri(itf14_png(code)), digits=human(code))
    rows = ''.join(f'<tr>{cell}{cell}</tr>' for _ in range(4))
    return (f'<html><body><table style="border-collapse:collapse">{rows}</table>'
            f'</body></html>')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', help='liste SRPVxxxx separee par des virgules')
    ap.add_argument('--lot')
    ap.add_argument('--ddm')
    ap.add_argument('--out-dir', default=os.path.join(ROOT, '_scratchpad', 'gdoc'))
    a = ap.parse_args()

    refs = [r.strip() for r in a.refs.split(',')] if a.refs else None
    lot, lots = par_ref(a.lot)
    ddm, ddms = par_ref(a.ddm)
    gram = grammages()
    os.makedirs(a.out_dir, exist_ok=True)

    for p in fetch(refs):
        ref = p['default_code']
        code = (p['barcode'] or '').strip()
        if len(code) != 14 or not code.isdigit():
            print(f'  ignore {ref} : barcode absent ou pas a 14 chiffres')
            continue
        _, unit = libelle(p['name'])
        html = doc_html(p, gram.get(unit), lots.get(ref, lot), ddms.get(ref, ddm))
        path = os.path.join(a.out_dir, f'{ref}.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'{ref} -> {path}  ({len(html) // 1024} Ko)')
