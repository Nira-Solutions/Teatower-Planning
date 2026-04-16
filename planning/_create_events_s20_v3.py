#!/usr/bin/env python3
"""Create calendar events for S20 (20-24 april 2026) planning v3."""
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
LOGIN = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"
JEROME_ID = 6494

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, LOGIN, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

def create_event(name, start, stop, location, description, partner_ids=None):
    vals = {
        "name": name,
        "start": start,
        "stop": stop,
        "location": location,
        "description": f"<p>{description}</p>",
        "partner_ids": [[6, 0, partner_ids or [JEROME_ID]]],
    }
    eid = models.execute_kw(DB, uid, PASSWORD, "calendar.event", "create", [vals])
    print(f"  Created event #{eid}: {name}")
    return eid

created = []

# === LUNDI 20/04 ===
print("=== LUNDI 20/04 ===")

created.append(create_event(
    "Implantation Teatower - Delhaize Enghien (flanc TG)",
    "2026-04-20 06:30:00", "2026-04-20 08:00:00",
    "Square de la Dodane, 7850 Enghien",
    "IMPLANTATION flanc de tete de gondole. SO S05413 (366,81 EUR). Duree 1h30. Contact: Mme Mestdag (boss), Mme Luba (rayon).",
    [123041, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Gosselies (Distriparenthese)",
    "2026-04-20 09:00:00", "2026-04-20 09:30:00",
    "Rue Pont a Migneloux 13, 6041 Gosselies",
    "Remplissage. Tier C, 16j. Contact: Valentin Schirru. Tel: 071/35.40.10",
    [2927, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Floriffoux (Floridis SA, OVERDUE)",
    "2026-04-20 10:00:00", "2026-04-20 10:30:00",
    "Rue Emeree 4, 5150 Floriffoux",
    "OVERDUE 2j (cycle 35j Tier B). Remplissage complet. Contact: Loredana / Manon. Tel: 081 44 05 39",
    [2958, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Spy (SRL Spydis)",
    "2026-04-20 11:00:00", "2026-04-20 11:30:00",
    "Route de Saussin 45, 5190 Jemeppe-sur-Sambre",
    "Remplissage regulier. Tier B, 16j. Contact: Emilie / Dorian. Tel: +32 71 78 74 39",
    [116686, JEROME_ID]
))

# === MARDI 21/04 ===
print("\n=== MARDI 21/04 ===")
# Event #413 (Spar Namur) already exists

created.append(create_event(
    "Visite Teatower - Delhaize de Bouge (Affilie 041345)",
    "2026-04-21 07:45:00", "2026-04-21 08:15:00",
    "Chaussee de Louvain 336, 5004 Namur",
    "Visite merchandiser. Priorite Gilles. Contact: Mme Destree / Grandjean / Augustaine. Tel: +32 81 21 48 88",
    [114681, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Bouge (Windmill SA, OVERDUE)",
    "2026-04-21 08:30:00", "2026-04-21 09:00:00",
    "Chaussee de Louvain 257, 5000 Bouge",
    "OVERDUE 16j (cycle 35j Tier B). Remplissage complet. Contact: Dany Decoster. Tel: 081569346",
    [3297, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Naninne (BOISDIS SA, OVERDUE Tier A)",
    "2026-04-21 09:15:00", "2026-04-21 09:45:00",
    "Chaussee de Marche 860, 5100 Naninne",
    "OVERDUE 3j (cycle 20j Tier A). Remplissage complet. Contact: Stephanie. Tel: 081 63 36 96",
    [2812, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Belgrade (Belgradis, OVERDUE)",
    "2026-04-21 10:00:00", "2026-04-21 10:30:00",
    "Allee des Ormes 15, 5001 Belgrade",
    "OVERDUE 16j (cycle 35j Tier B). Remplissage complet. Contact: Stephanie. Tel: 081260187",
    [2821, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - AD Fosses-la-Ville (OVERDUE)",
    "2026-04-21 11:00:00", "2026-04-21 11:30:00",
    "Rue du Cimetiere 5, Fosses-la-Ville",
    "OVERDUE. Visite de reprise. Priorite Gilles. Contact: Leslie. Tel: 071 71 29 12. Pref mercredi, mardi PM OK.",
    [5441, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Assesse (SA Barthe, Tier A)",
    "2026-04-21 11:45:00", "2026-04-21 12:15:00",
    "Rue Melville Wilson 3, 5330 Assesse",
    "Remplissage regulier Tier A (15j). Contact: Anne Buttiens. Tel: 083 66 05 70. Route retour Baillonville.",
    [3209, JEROME_ID]
))

# === MERCREDI 22/04 ===
print("\n=== MERCREDI 22/04 ===")

created.append(create_event(
    "Visite Teatower - Hyper Carrefour Boncelles (OVERDUE)",
    "2026-04-22 06:00:00", "2026-04-22 07:30:00",
    "Rue du Condroz 16, 4100 Boncelles",
    "OVERDUE 171j. Hyper = matin (7h-11h30). Contact: Robert Stassin. Tel: +32 4 338 86 11. Priorite Gilles. Pas le mardi.",
    [7431, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Tilff (Chili Peppers, Tier A)",
    "2026-04-22 07:45:00", "2026-04-22 08:15:00",
    "Avenue des Ardennes 8, 4130 Esneux",
    "Remplissage regulier Tier A (16j). Tel: +32 479 32 28 39",
    [116869, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Hyper Carrefour Fleron",
    "2026-04-22 08:30:00", "2026-04-22 09:00:00",
    "Rue de la Clef 30, 4620 Fleron",
    "Visite merchandiser. Hyper = matin. Priorite Gilles. Tel: +32 4 355 86 11",
    [7078, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Barchon (BARCHONEW SRL)",
    "2026-04-22 09:15:00", "2026-04-22 09:45:00",
    "Rue Champs de Tignee 32, 4671 Barchon",
    "Remplissage. Tier C, 21j. Contact: Jerome ou Jovani. Tel: +32 4 362 27 33. Priorite Gilles.",
    [119815, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Bois-de-breux",
    "2026-04-22 10:00:00", "2026-04-22 10:30:00",
    "Rue de Herve 280, 4030 Liege",
    "Remplissage. Tier B, 21j. Contact: Olivier Landauer. Tel: +32 4 365 74 07. Priorite Gilles.",
    [8169, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Liege Ardente",
    "2026-04-22 11:00:00", "2026-04-22 11:30:00",
    "Chaussee de Tongres 269, 4000 Liege",
    "Remplissage. Tier C, 37j. Contact: Kevin Demarteau 0468 37 62 65.",
    [120156, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Proxy Delhaize Saint-Severin",
    "2026-04-22 11:45:00", "2026-04-22 12:15:00",
    "Route du Condroz 243, 4550 Nandrin",
    "Remplissage. Tier C, 21j. Contact: Mme Dessart / Renaud / Philippe. Tel: +32 4 372 09 85. Priorite Gilles.",
    [113445, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Proxy Delhaize Ferrieres",
    "2026-04-22 12:30:00", "2026-04-22 13:00:00",
    "Rue du Pre du Fa 6A, 4190 Ferrieres",
    "Visite merchandiser. Priorite Gilles. Contact: Bernard Counasse / Martine Georis. Tel: +32 86 40 02 27. NOTE: responsable absent mercredi.",
    [119818, JEROME_ID]
))

# === JEUDI 23/04 ===
print("\n=== JEUDI 23/04 ===")

created.append(create_event(
    "Visite Teatower - CM Beauraing (DEMARS SA, OVERDUE Tier A)",
    "2026-04-23 06:30:00", "2026-04-23 07:00:00",
    "Rue de Rochefort 37, 5570 Beauraing",
    "OVERDUE 4j (cycle 20j Tier A). Remplissage complet. Contact: Therese / Alison. Tel: 082/71 02 30",
    [2905, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Beauraing (SA Beausov New)",
    "2026-04-23 07:00:00", "2026-04-23 07:30:00",
    "150 rue de Rochefort, 5570 Beauraing",
    "Remplissage. Tier C, 15j. Contact: Mme Sovet / Gregory. Tel: +32 82 71 36 97",
    [116008, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - AD Rochefort (SA Marer, OVERDUE)",
    "2026-04-23 07:45:00", "2026-04-23 08:15:00",
    "Rue de Marche 112-114, 5580 Rochefort",
    "OVERDUE 13j (cycle 35j Tier B). Remplissage complet. Tel: +32 84 21 01 03. Priorite Gilles.",
    [7692, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Anhee (Holebo SA, OVERDUE)",
    "2026-04-23 08:45:00", "2026-04-23 09:15:00",
    "Chaussee de Dinant 127, 5537 Anhee",
    "OVERDUE 50j (cycle 50j Tier C). Visite urgente. Contact: Christophe. Tel: +32 82 71 39 84. Jamais le lundi.",
    [8869, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - ITM Jambes (JAMBIS SA)",
    "2026-04-23 10:00:00", "2026-04-23 10:30:00",
    "Rue de la Poudriere 14, 5100 Jambes",
    "Remplissage regulier. Tier B, 15j. Contact: Faustine. Tel: 081306878",
    [3000, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Ottignies (KAIO, OVERDUE Tier A)",
    "2026-04-23 11:30:00", "2026-04-23 12:00:00",
    "Bois Pinchet 2, 1495 Villers-La-Ville",
    "OVERDUE 2j (cycle 20j Tier A). Remplissage. Contact: Jolan Cailleu. Tel: 010 40 15 69. Priorite Gilles.",
    [3016, JEROME_ID]
))

# === VENDREDI 24/04 ===
print("\n=== VENDREDI 24/04 ===")

created.append(create_event(
    "Implantation Teatower - Carrefour Market Bievre",
    "2026-04-24 06:30:00", "2026-04-24 07:30:00",
    "Rue de Bouillon 54, 5555 Bievre",
    "IMPLANTATION display complet Teatower. Nouveau client. SO en creation par Jerome. Partner: Cafermi (ID 7440).",
    [7440, JEROME_ID]
))

created.append(create_event(
    "Implantation Teatower - Proxy Delhaize Maissin",
    "2026-04-24 08:00:00", "2026-04-24 09:00:00",
    "Avenue de France 13, 6852 Maissin",
    "IMPLANTATION display complet Teatower. Nouveau client GMS (Proxy Delhaize). SO en creation par Jerome.",
    [JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - AD Bastogne (SA Marer, OVERDUE Tier A)",
    "2026-04-24 09:30:00", "2026-04-24 10:00:00",
    "Route de Marche 112-114, 6660 Bastogne",
    "OVERDUE 4j (cycle 20j Tier A). Remplissage complet. Contact: Valentin Gilson. Tel: +32 61 21 70 84",
    [8558, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - CM Bastogne (Pascalino, OVERDUE)",
    "2026-04-24 10:00:00", "2026-04-24 10:30:00",
    "Route de Marche 149, 6600 Bastogne",
    "OVERDUE 23j (cycle 50j Tier C). Contact: Fabienne Antoine. Tel: +32 61 21 23 42",
    [2864, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - CM Hotton (HODICA SA)",
    "2026-04-24 11:00:00", "2026-04-24 11:30:00",
    "Rue de la Jonction 16, 6990 Hotton",
    "Remplissage S05372. Tier B, 7j. Contact: Gauthier Lempereur. Tel: 084 46 73 44",
    [2979, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - CM Barvaux (BARVO SA)",
    "2026-04-24 11:45:00", "2026-04-24 12:15:00",
    "Route de Marche 26, 6940 Barvaux/Ourthe",
    "Remplissage S05405. Tier B. Contact: Nathalie Warnier. Tel: 086 21 13 79",
    [2811, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Barvaux (Affilie 040990)",
    "2026-04-24 12:15:00", "2026-04-24 12:45:00",
    "Rue Petit-Barvaux 6, 6940 Barvaux-sur-Ourthe",
    "Visite merchandiser. Priorite Gilles. Contact: Bernard Counasse. Tel: +32 86 36 60 08",
    [119817, JEROME_ID]
))

created.append(create_event(
    "Visite Teatower - Delhaize Marche (N.B.S. RETAIL, OVERDUE Tier A)",
    "2026-04-24 13:00:00", "2026-04-24 13:30:00",
    "Avenue de France 39, 6900 Marche-en-Famenne",
    "OVERDUE 4j (cycle 20j Tier A). Remplissage complet. Tel: +32 470 26 16 92. Priorite Gilles.",
    [8159, JEROME_ID]
))

print(f"\n=== Total: {len(created)} events created ===")
print(f"Event IDs: {created}")
print("Event #413 (Spar Namur implantation) preserved.")
