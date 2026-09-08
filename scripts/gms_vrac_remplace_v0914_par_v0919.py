# -*- coding: utf-8 -*-
"""
Remplace la ligne V0914 (Rouge Printanier - BIO) par V0919 (Sortilege d'automne,
Halloween 2026) dans le bon de commande GMS VRAC de Gilles.

Pourquoi une edition XML et pas openpyxl : le classeur embarque un dessin
(xl/drawings/drawing1.xml) qu'openpyxl laisse tomber a la sauvegarde. On patche
donc le ZIP entree par entree : tout ce qu'on ne touche pas est recopie
bit pour bit, mise en forme et logo compris.

Usage :
    python scripts/gms_vrac_remplace_v0914_par_v0919.py <source.xlsx> [<sortie.xlsx>]

Sans <sortie.xlsx>, ecrit a cote de la source en suffixant " - V0919".
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

SHEET = "xl/worksheets/sheet1.xml"
SST = "xl/sharedStrings.xml"

# Colonne -> (ancienne valeur attendue, nouvelle valeur)
REMPLACEMENTS = [
    ("V0914", "V0919"),
    ("Rouge Printanier - BIO", "Sortilege d'automne"),
    ("Infusion de fruits", "Infusion epicee"),
    ("Hibiscus – Cassis – Sureau", "Citrouille – Erable"),
    ("5413393003971", "5413393004138"),
]
# Accents corrects (le fichier source est en UTF-8, on ecrit les vraies formes)
REMPLACEMENTS[1] = ("Rouge Printanier - BIO", "Sortilège d'automne")
REMPLACEMENTS[2] = ("Infusion de fruits", "Infusion épicée")
REMPLACEMENTS[3] = ("Hibiscus – Cassis – Sureau",
                    "Citrouille – Érable")


def lire_sst(xml):
    """Retourne la liste des <si> tels quels + le texte concatene de chacun."""
    items = re.findall(r"<si\b.*?</si>|<si\s*/>", xml, re.S)
    textes = []
    for it in items:
        textes.append("".join(re.findall(r"<t[^>]*>(.*?)</t>", it, re.S)))
    return items, textes


def echappe(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = Path(sys.argv[1])
    if not src.exists():
        raise SystemExit(f"Introuvable : {src}")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(
        f"{src.stem} - V0919{src.suffix}")

    with zipfile.ZipFile(src) as z:
        noms = z.namelist()
        if SHEET not in noms:
            raise SystemExit(f"{SHEET} absent : structure inattendue.")
        contenu = {n: z.read(n) for n in noms}
        infos = {n: z.getinfo(n) for n in noms}

    sst_xml = contenu.get(SST, b"").decode("utf-8")
    sheet_xml = contenu[SHEET].decode("utf-8")
    items, textes = lire_sst(sst_xml)

    # Index de la chaine "V0914" -> identifie la ligne cible
    try:
        idx_ref = textes.index("V0914")
    except ValueError:
        raise SystemExit("La chaine V0914 est absente de sharedStrings.xml.")

    m = re.search(
        r'<row\b[^>]*>(?:(?!</row>).)*?<c[^>]*t="s"[^>]*>\s*<v>%d</v>.*?</row>'
        % idx_ref, sheet_xml, re.S)
    if not m:
        raise SystemExit("Ligne V0914 introuvable dans la feuille.")
    ligne = m.group(0)
    nouvelle = ligne
    nb_si = len(items)
    ajouts = []
    faits, absents = [], []

    for ancien, nouveau in REMPLACEMENTS:
        if ancien in textes:
            i = textes.index(ancien)
            # la valeur partagee peut servir a d'autres lignes : on cree un
            # nouveau <si> et on repointe uniquement la cellule de CETTE ligne
            cible = nb_si + len(ajouts)
            avant = nouvelle
            nouvelle = re.sub(
                r'(<c[^>]*t="s"[^>]*>\s*<v>)%d(</v>)' % i,
                r"\g<1>%d\g<2>" % cible, nouvelle, count=1)
            if nouvelle != avant:
                ajouts.append(f"<si><t>{echappe(nouveau)}</t></si>")
                faits.append((ancien, nouveau, "chaine partagee"))
                continue
            nouvelle = avant
        # sinon : valeur numerique en dur (typiquement l'EAN)
        avant = nouvelle
        nouvelle = re.sub(r"(<v>)%s(</v>)" % re.escape(ancien),
                          r"\g<1>%s\g<2>" % nouveau, nouvelle, count=1)
        if nouvelle != avant:
            faits.append((ancien, nouveau, "valeur numerique"))
        else:
            absents.append(ancien)

    if absents:
        print("ATTENTION, non remplace (a verifier a la main) :")
        for a in absents:
            print("   -", a)

    sheet_xml = sheet_xml.replace(ligne, nouvelle, 1)
    if ajouts:
        bloc = "".join(ajouts)
        sst_xml = sst_xml.replace("</sst>", bloc + "</sst>", 1)
        # count/uniqueCount doivent suivre, sinon Excel rale
        sst_xml = re.sub(r'(<sst[^>]*\buniqueCount=")(\d+)(")',
                         lambda mm: mm.group(1) + str(int(mm.group(2)) + len(ajouts)) + mm.group(3),
                         sst_xml, count=1)
        sst_xml = re.sub(r'(<sst[^>]*\bcount=")(\d+)(")',
                         lambda mm: mm.group(1) + str(int(mm.group(2)) + len(ajouts)) + mm.group(3),
                         sst_xml, count=1)
        contenu[SST] = sst_xml.encode("utf-8")
    contenu[SHEET] = sheet_xml.encode("utf-8")

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n in noms:  # on preserve l'ordre d'origine des entrees
            zi = zipfile.ZipInfo(n, date_time=infos[n].date_time)
            zi.compress_type = infos[n].compress_type
            zi.external_attr = infos[n].external_attr
            z.writestr(zi, contenu[n])

    # relecture de controle
    with zipfile.ZipFile(dst) as z:
        if z.testzip() is not None:
            raise SystemExit("ZIP corrompu apres ecriture.")
        verif = z.read(SST).decode("utf-8")
    for _, nouveau, _ in faits:
        if nouveau not in verif and nouveau not in contenu[SHEET].decode("utf-8"):
            print("ATTENTION : valeur absente du fichier final ->", nouveau)

    print(f"Ecrit : {dst}")
    for ancien, nouveau, comment in faits:
        print(f"   {ancien}  ->  {nouveau}   ({comment})")
    print("\nPrix inchanges : remise 30 %, prix client 6,60 EUR HTVA, "
          "PVC 10,00 EUR TVAC, TVA 6 % (identiques a la ligne V0914).")


if __name__ == "__main__":
    main()
