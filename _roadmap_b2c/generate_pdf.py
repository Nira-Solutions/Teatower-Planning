"""Genere le PDF de la roadmap B2C Teatower Juin -> Decembre 2026."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "Roadmap_B2C_Teatower_Juin-Dec_2026.pdf"

NAVY = colors.HexColor("#0E2A47")
TEAL = colors.HexColor("#2E7D6B")
SAND = colors.HexColor("#F5F1E8")
INK = colors.HexColor("#1A1A1A")
GREY = colors.HexColor("#666666")
LIGHT_GREY = colors.HexColor("#E5E5E5")
ALERT = colors.HexColor("#B23A48")

styles = getSampleStyleSheet()

H_TITLE = ParagraphStyle(
    "TitleBig", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=26, leading=32, textColor=NAVY, alignment=TA_LEFT, spaceAfter=6,
)
H_SUB = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontName="Helvetica",
    fontSize=12, leading=16, textColor=GREY, alignment=TA_LEFT, spaceAfter=20,
)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=16, leading=20, textColor=NAVY, spaceBefore=16, spaceAfter=8,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=12, leading=15, textColor=TEAL, spaceBefore=10, spaceAfter=4,
)
BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10, leading=14, textColor=INK, spaceAfter=6,
)
BODY_BOLD = ParagraphStyle(
    "BodyBold", parent=BODY, fontName="Helvetica-Bold",
)
NOTE = ParagraphStyle(
    "Note", parent=BODY, fontSize=9, textColor=GREY, leading=12,
)
RULE = ParagraphStyle(
    "Rule", parent=BODY, fontName="Helvetica-Bold", fontSize=10,
    textColor=NAVY, backColor=SAND, borderPadding=6, leftIndent=0,
)
ALERT_STYLE = ParagraphStyle(
    "Alert", parent=BODY, fontName="Helvetica-Bold", fontSize=10,
    textColor=ALERT, backColor=colors.HexColor("#FBE9EB"),
    borderPadding=6,
)

CELL = ParagraphStyle(
    "Cell", parent=BODY, fontSize=9, leading=11, spaceAfter=0,
)
CELL_BOLD = ParagraphStyle(
    "CellBold", parent=CELL, fontName="Helvetica-Bold",
)
CELL_HEADER = ParagraphStyle(
    "CellHeader", parent=CELL, fontName="Helvetica-Bold",
    textColor=colors.white, fontSize=9, leading=11,
)


def header_footer(canv, doc):
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, fill=1, stroke=0)
    canv.setFont("Helvetica-Bold", 9)
    canv.setFillColor(colors.white)
    canv.drawString(15 * mm, A4[1] - 6 * mm, "TEATOWER  -  Roadmap B2C 2026")
    canv.drawRightString(A4[0] - 15 * mm, A4[1] - 6 * mm,
                         f"Page {doc.page}")
    canv.setFont("Helvetica", 8)
    canv.setFillColor(GREY)
    canv.drawString(15 * mm, 10 * mm,
                    f"Genere le {date.today().strftime('%d/%m/%Y')}  -  "
                    "Confidentiel - usage interne")
    canv.restoreState()


def table(data, col_widths, header=True, zebra=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    s = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.3, LIGHT_GREY),
    ]
    if header:
        s.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                s.append(("BACKGROUND", (0, i), (-1, i), SAND))
    t.setStyle(TableStyle(s))
    return t


def P(text, style=BODY):
    return Paragraph(text, style)


def C(text, bold=False):
    return Paragraph(text, CELL_BOLD if bold else CELL)


def CH(text):
    return Paragraph(text, CELL_HEADER)


def main() -> None:
    story = []

    # ===== PAGE DE GARDE =====
    story.append(Spacer(1, 4 * cm))
    story.append(P("Roadmap B2C 2026", H_TITLE))
    story.append(P("Shopify + Magasins TT Namur / Liege / Waterloo", H_SUB))
    story.append(P("Juin -> Decembre 2026", ParagraphStyle(
        "PageDateSub", parent=H_SUB, fontSize=14, textColor=TEAL,
    )))
    story.append(Spacer(1, 2 * cm))

    story.append(P("Cadre de la roadmap", H1))
    story.append(P(
        "<b>1. Aucune reduction en pourcentage.</b> Toutes les mecaniques "
        "promo sont en logique <b>'Buy X, Get Y'</b> (achat de X -> "
        "cadeau Y offert).", RULE,
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(P(
        "<b>2. Catalogue existant uniquement.</b> Aucun SKU ou programme "
        "nouveau a creer. On utilise ce qui est deja rode chez Teatower.",
        RULE,
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(P(
        "<b>3. Y = SKU en sur-stock.</b> Le cadeau offert cible "
        "prioritairement des produits identifies comme stock dormant "
        "(44 515 EUR identifies sur 129 SKU). Double benefice : "
        "promo + ecoulement.", RULE,
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(P(
        "<b>4. Boites metal A0913-A0921 : reserve Noel.</b> Stock dispo "
        "fin octobre 2026 -> activable des le 1er novembre (Black Tea "
        "Friday).", RULE,
    ))

    story.append(PageBreak())

    # ===== DIAGNOSTIC =====
    story.append(P("Diagnostic rapide", H1))
    story.append(P(
        "Sur les 10 derniers mois : 23 579 EUR Shopify + 241 585 EUR POS "
        "magasins. Trois leviers sous-exploites identifies :", BODY,
    ))
    story.append(P(
        "<b>1. Panier moyen plafonne</b> autour de 20-25 EUR. Les "
        "accessoires (theieres fonte 45-59 EUR, set matcha, boites metal) "
        "sont peu cross-vendus avec le the. Un client qui prend 1 the a "
        "11 EUR ne repart pas avec une boite metal a 3,90 EUR.", BODY,
    ))
    story.append(P(
        "<b>2. Saisonnalite tres concentree.</b> Pics juillet-aout (thes "
        "glaces) et novembre-decembre (Noel/Avent). Creux profonds en "
        "mars, avril, juin, septembre.", BODY,
    ))
    story.append(P(
        "<b>3. Stock dormant B2C : 44 515 EUR sur 129 SKU.</b> Coffret "
        "Matcha C0200 = 0 vente sur 6 mois (150 unites stockees). Thes "
        "glaces GI0916 surcharges (783 unites, 10 mois de couverture). "
        "Accessoires premium (theieres, services a the) en sur-stock "
        "structurel. Voir top 20 dans le scan dedie.", BODY,
    ))

    story.append(Spacer(1, 6 * mm))

    # ===== 3 SKU STARS =====
    story.append(P("Les 3 SKU stars a transformer en cadeau Y", H1))

    stars = [
        [CH("SKU"), CH("Probleme stock"), CH("Mecanique BXGY proposee")],
        [
            C("<b>C0200</b><br/>Coffret Matcha", bold=True),
            C("150 u. en stock<br/><b>0 vente sur 6 mois</b><br/>2 142 EUR immobilises"),
            C("<b>'Panier >= 60 EUR = coffret matcha offert'</b><br/>"
              "Gros CTA Shopify + magasins. Ecoulement attendu : "
              "50-80 u./mois."),
        ],
        [
            C("<b>GI0916</b><br/>Vergers d'Ete<br/>(the glace)", bold=True),
            C("783 u. en stock<br/>10,2 mois de couverture<br/>2 349 EUR immobilises"),
            C("<b>'2 thes/infusettes achetes = 1 GI0916 offert'</b><br/>"
              "Periode juin -> aout. Ecoulement attendu : "
              "4 a 6 semaines."),
        ],
        [
            C("<b>V0727</b><br/>L'apres-repas<br/>(vrac 80g)", bold=True),
            C("416 u. en stock<br/>23,8 mois de couverture<br/>1 335 EUR immobilises"),
            C("<b>'2 vrac achetes = 1 V0727 offert'</b><br/>"
              "Upsell vrac toute l'annee. Mecanique de fond."),
        ],
    ]
    story.append(table(stars, col_widths=[3.5 * cm, 5 * cm, 8.5 * cm]))

    story.append(PageBreak())

    # ===== CALENDRIER MOIS PAR MOIS =====
    story.append(P("Calendrier operationnel Juin -> Decembre 2026", H1))

    months = [
        [CH("Mois"), CH("Mecanique principale"), CH("Declencheur"),
         CH("Cadeau Y (SKU sur-stocke)")],
        [
            C("<b>Juin</b>", bold=True),
            C("Lancement socle BXGY"),
            C("Panier Shopify >= 25 EUR"),
            C("<b>I0617 Liberte</b> (401 u.) OU<br/>"
              "<b>I0820 Marrakech BIO</b> (576 u.)<br/>au choix client"),
        ],
        [
            C("<b>Juin (1-14)</b>", bold=True),
            C("Fete des peres (14/06)"),
            C("2 thes 'robustes' achetes"),
            C("Emballage cadeau + carte<br/>(geste boutique, pas de SKU)"),
        ],
        [
            C("<b>Juillet-Aout</b>", bold=True),
            C("Pic the glace"),
            C("2 thes vrac ou infusettes"),
            C("<b>GI0916 Vergers d'Ete</b><br/>"
              "(ecoulement 783 u.)"),
        ],
        [
            C("<b>Septembre</b>", bold=True),
            C("Rentree, upsell vrac"),
            C("2 vrac achetes"),
            C("<b>V0727 L'apres-repas</b> OU<br/>"
              "<b>V0863 Masala Chai</b>"),
        ],
        [
            C("<b>Septembre-Octobre</b>", bold=True),
            C("Push panier eleve"),
            C("Panier >= 60 EUR"),
            C("<b>C0200 Coffret Matcha</b><br/>"
              "(ecoulement 150 u. - star)"),
        ],
        [
            C("<b>Octobre</b>", bold=True),
            C("Halloween Noir"),
            C("2 thes noirs achetes"),
            C("<b>V0253 Voyage a Venise</b><br/>"
              "(402 u. en stock)"),
        ],
        [
            C("<b>Novembre</b>", bold=True),
            C("Bascule socle Noel"),
            C("2 thes achetes"),
            C("<b>Boite metal A0913-A0921</b><br/>"
              "(stock OK fin oct)"),
        ],
        [
            C("<b>27-30 Novembre</b>", bold=True),
            C("BLACK TEA FRIDAY (4j)"),
            C("2 thes achetes"),
            C("<b>Boite metal + livraison gratuite</b><br/>"
              "(E-com only)"),
        ],
        [
            C("<b>Decembre</b>", bold=True),
            C("Noel - panier eleve"),
            C("Panier >= 80 EUR"),
            C("<b>A1135 Set Matcha</b> OU<br/>"
              "<b>A1089 Theiere fonte 1,2L</b>"),
        ],
        [
            C("<b>Decembre</b>", bold=True),
            C("Noel - cadeau 'wow'"),
            C("Panier >= 100 EUR"),
            C("<b>A1118 Service a the 4 tasses</b><br/>"
              "(23 u. - SKU rare)"),
        ],
    ]
    story.append(table(months, col_widths=[3 * cm, 4.5 * cm, 4 * cm, 5.5 * cm]))

    story.append(PageBreak())

    # ===== BUNDLE MATCHA =====
    story.append(P("Bundle Matcha - mecanique signature", H1))
    story.append(P(
        "Quatre SKU sur-stockes graviteant autour du matcha. Mecanique "
        "permanente proposee :", BODY,
    ))
    story.append(P(
        "<b>'Achat A1135 (Coffret Matcha) ou V0615 (Gyokuro) = "
        "A1074 (Fouet electrique) + A1075 (Verre double paroi) offerts'</b>",
        RULE,
    ))
    story.append(Spacer(1, 4 * mm))

    bundle = [
        [CH("SKU"), CH("Nom"), CH("Stock"), CH("Valeur immob."), CH("Role")],
        [C("A1135", bold=True), C("Coffret Matcha Traditionnel"),
         C("51 u."), C("964 EUR"), C("Trigger (X)")],
        [C("V0615", bold=True), C("Gyokuro Asahi BIO 50g"),
         C("39 u."), C("550 EUR"), C("Trigger (X)")],
        [C("A1074", bold=True), C("Fouet electrique Matcha"),
         C("107 u."), C("944 EUR"), C("Cadeau (Y)")],
        [C("A1075", bold=True), C("Verre Matcha double paroi"),
         C("108 u."), C("702 EUR"), C("Cadeau (Y)")],
    ]
    story.append(table(bundle, col_widths=[2 * cm, 6 * cm, 2.2 * cm,
                                            3 * cm, 3.8 * cm]))
    story.append(Spacer(1, 4 * mm))
    story.append(P(
        "<b>Impact :</b> 3 160 EUR de stock dormant ecoule en bundle. "
        "Le client repart avec le kit matcha complet. Mise en avant "
        "Shopify (collection 'Univers Matcha') + magasins.", BODY,
    ))

    story.append(Spacer(1, 6 * mm))

    # ===== ALERTES STOCK =====
    story.append(P("Alertes stock a traiter cette semaine", H1))
    story.append(P(
        "<b>ALERTE 1 - PO en cours sur SKU deja sur-stockes.</b> Quatre "
        "purchase orders fournisseurs vont livrer des accessoires dans "
        "les 60 jours alors que le stock est deja excessif :",
        ALERT_STYLE,
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(P(
        "<b>A1133, A1131, A1130, A1059</b> - reception +18 a +48 unites "
        "prevue. Action : bloquer ou retarder ces 4 PO. Decision a "
        "deleguer a l'agent purchase.", BODY,
    ))
    story.append(Spacer(1, 5 * mm))
    story.append(P(
        "<b>ALERTE 2 - Anomalie valorisation coffrets C0xxx.</b> "
        "6 references coffrets cumulent 11 592 unites en stock pour "
        "seulement 2 142 EUR de valeur (standard_price proche de zero). "
        "Indique un parametrage BoM/cout casse sur certains coffrets. "
        "A investiguer cote compta + production.", ALERT_STYLE,
    ))

    story.append(PageBreak())

    # ===== ACTIONS IMMEDIATES =====
    story.append(P("Actions immediates - avant 1er juin 2026", H1))

    actions = [
        [CH("#"), CH("Action"), CH("Delai"), CH("Qui"), CH("Setup")],
        [
            C("1", bold=True),
            C("<b>Corriger prix GI0xxx -> 9,50 EUR</b> (5 thes glaces)"),
            C("J+3"),
            C("Validation Nicolas<br/>Execution batch Shopify"),
            C("15 min via API Shopify"),
        ],
        [
            C("2", bold=True),
            C("<b>Setup 'Panier >= 25 EUR = I0617/I0820 offert'</b> "
              "sur Shopify"),
            C("J+5"),
            C("Moi (config)"),
            C("Shopify Functions 'Buy X Get Y' natif - 1h"),
        ],
        [
            C("3", bold=True),
            C("<b>Setup 'Achat 2 vrac = 1 V0727 offert'</b> "
              "sur Shopify"),
            C("J+5"),
            C("Moi (config)"),
            C("Shopify Functions - 30 min"),
        ],
        [
            C("4", bold=True),
            C("<b>Brief equipes boutique</b> Namur/Liege/Waterloo "
              "(scripts BXGY + emballage cadeau)"),
            C("J+7"),
            C("Nicolas - visio 15 min"),
            C("Script imprime fourni"),
        ],
        [
            C("5", bold=True),
            C("<b>Verif stock emballage cadeau + cartes</b> dans les "
              "3 boutiques avant fete des peres"),
            C("J+7"),
            C("Stock-manager"),
            C("Audit boutique"),
        ],
        [
            C("6", bold=True),
            C("<b>Bloquer / retarder PO A1133/A1131/A1130/A1059</b>"),
            C("J+5"),
            C("Agent purchase + Nicolas"),
            C("Contact fournisseur(s)"),
        ],
    ]
    story.append(table(actions, col_widths=[1 * cm, 6.5 * cm, 1.5 * cm,
                                              3.5 * cm, 4.5 * cm]))

    story.append(Spacer(1, 8 * mm))

    # ===== ECHEANCIER NOVEMBRE =====
    story.append(P("Echeancier bascule Noel (a preparer en octobre)", H1))
    nov_actions = [
        [CH("Date"), CH("Action")],
        [C("28-30 oct", bold=True),
         C("Verifier reception stock boites metal A0913-A0921 (controle "
           "qualite + repartition 3 boutiques + Havelange)")],
        [C("1er nov", bold=True),
         C("Bascule mecanique : '2 thes achetes = boite metal offerte' "
           "(remplace I0617/I0820/V0727 comme socle)")],
        [C("15 nov", bold=True),
         C("Setup Black Tea Friday (e-com) : compteur, page dediee, "
           "email Mailchimp programme par Stephan")],
        [C("27 nov 00h", bold=True),
         C("BLACK TEA FRIDAY ON - 2 thes + boite + livraison gratuite "
           "(4 jours)")],
        [C("1er dec", bold=True),
         C("Bascule paniers eleves : 'Panier >= 80 EUR = A1135 ou A1089 "
           "offert', 'Panier >= 100 EUR = A1118 offert'")],
    ]
    story.append(table(nov_actions, col_widths=[3 * cm, 14 * cm]))

    story.append(Spacer(1, 1 * cm))

    # ===== FOOTER FINAL =====
    story.append(P(
        "Sources : scan stock Odoo XML-RPC du 21/05/2026 "
        "(C:/Users/FlowUP/OneDrive/Teatower/_promo_scan/), "
        "audit P&L Teatower 2025-2026, forecast V0 12 mois.", NOTE,
    ))
    story.append(P(
        "Roadmap construite par Nira (agent principal Teatower) avec "
        "delegation aux agents Marketing et Odoo. "
        "Document de travail - a valider en CODIR.", NOTE,
    ))

    # ===== BUILD =====
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Roadmap B2C Teatower Juin-Dec 2026",
        author="Teatower / Nira",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"PDF genere : {OUT}")
    print(f"Taille : {OUT.stat().st_size / 1024:.1f} Ko")


if __name__ == "__main__":
    main()
