"""
Maximize Jerome's week 20-24 April 2026.
Create additional calendar.event entries in Odoo for the slots identified.
All times in UTC (Brussels = UTC+2 in April CEST).
"""
import xmlrpc.client, sys
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://tea-tree.odoo.com'
DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'
PWD = 'Teatower123'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
print(f"Authenticated uid={uid}")

jerome_partner_id = 6494
jerome_user_id = 12

events_to_create = [
    # =====================================================================
    # LUNDI 20/04 - HAINAUT
    # Existing: #386 Delhaize Gosselies 11:15-12:15 (UTC 09:15-10:15)
    # ADD: Intermarche Gosselies BEFORE (same town, 5 min away)
    # ADD: Intermarche Gerpinnes AFTER lunch (25 min from Gosselies)
    # =====================================================================
    {
        'name': 'Remplissage Teatower - Intermarche Gosselies (Tier C)',
        'start': '2026-04-20 07:30:00',  # 09:30 local
        'stop': '2026-04-20 08:00:00',   # 10:00 local
        'partner_ids': [(6, 0, [2927, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue Pont a Migneloux 13, 6041 Gosselies',
        'description': '<p>Tier C (15j/50j). Contact: Valentin Schirru. Tel: 071/35.40.10. Meme zone que Delhaize Gosselies.</p>',
    },
    # 11:15-12:15 = Delhaize Gosselies (existing #386)
    # 12:30-13:30 = pause dejeuner
    {
        'name': 'Remplissage Teatower - Intermarche Gerpinnes (OVERDUE Tier B)',
        'start': '2026-04-20 12:00:00',  # 14:00 local
        'stop': '2026-04-20 12:30:00',   # 14:30 local
        'partner_ids': [(6, 0, [2971, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Route De Philippeville 196, 6280 Gerpinnes',
        'description': '<p>Tier B OVERDUE (85j/35j max). Contact: Elodie Botte, Geraldine ou Max pour signature. Tel: 071216909. 25 min depuis Gosselies.</p>',
    },

    # =====================================================================
    # MARDI 21/04 - NAMUR
    # Existing: 08:30 Hyper Jambes, 09:00 Spar Namur, 10:15 Naninne,
    #           11:00 Bouge, 11:45 Belgrade, 13:00 Floriffoux
    # Retour estime 14h30 -> ADD 2 visits after Floriffoux
    # =====================================================================
    # After Floriffoux (13:30), Assesse is 15 min away on the way back to Baillonville
    {
        'name': 'Remplissage Teatower - Intermarche Assesse (Tier A)',
        'start': '2026-04-21 12:00:00',  # 14:00 local
        'stop': '2026-04-21 12:30:00',   # 14:30 local
        'partner_ids': [(6, 0, [3209, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue Melville Wilson 3, 5330 Assesse',
        'description': '<p>Tier A (14j/20j). Contact: Anne Buttiens. Tel: 083 66 05 70. Sur la route retour Baillonville depuis Floriffoux.</p>',
    },
    # Fernelmont is 20 min from Floriffoux, also on the N4 towards Baillonville
    {
        'name': 'Remplissage Teatower - AD Fernelmont (Tier B, demande Tamara)',
        'start': '2026-04-21 11:15:00',  # 13:15 local (just before Floriffoux at 13:00 -> reorder: Fernelmont first after lunch)
        'stop': '2026-04-21 11:45:00',   # 13:45 local
        'partner_ids': [(6, 0, [2952, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': "Rue d'Eghezee 16, 5380 Fernelmont",
        'description': '<p>Tier B (22j/35j). Contact: Tamara Geurts. Tel: +32 81 83 04 55. DEMANDE 10/04: remplir rayon + stopper 3 ref pour thes glaces.</p>',
    },

    # =====================================================================
    # MERCREDI 22/04 - LIEGE
    # Existing: 09:00 Embourg, 09:45 Tilff, 10:30 Faimes, 11:15 Villers,
    #           12:15 Torrefactory Mediacite
    # After Torrefactory (~13:15), Jerome is IN Liege city center
    # ADD: Delhaize Bois-de-breux (10 min from Mediacite)
    # ADD: Delhaize Liege Ardente (10 min from Bois-de-breux)
    # ADD: Proxy Saint-Severin (on route back to Baillonville, 30 min from Liege)
    # =====================================================================
    {
        'name': 'Remplissage Teatower - Delhaize Bois-de-breux (Tier B)',
        'start': '2026-04-22 11:30:00',  # 13:30 local
        'stop': '2026-04-22 12:00:00',   # 14:00 local
        'partner_ids': [(6, 0, [8169, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue de Herve 280, 4030 Liege',
        'description': '<p>Tier B (20j/35j). Contact: Landauer Olivier, Demany, Poppov ou Ghislaine. Tel: +32 4 365 74 07. 10 min depuis Mediacite.</p>',
    },
    {
        'name': 'Remplissage Teatower - Delhaize Liege Ardente (Tier C)',
        'start': '2026-04-22 12:15:00',  # 14:15 local
        'stop': '2026-04-22 12:45:00',   # 14:45 local
        'partner_ids': [(6, 0, [120156, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Chaussee de Tongres 269, 4000 Liege',
        'description': '<p>Tier C (36j/50j). Contact: Kevin Demarteau 0468 37 62 65. The en rayon. 10 min depuis Bois-de-breux.</p>',
    },
    {
        'name': 'Remplissage Teatower - Proxy Delhaize Saint-Severin (Tier C)',
        'start': '2026-04-22 13:15:00',  # 15:15 local
        'stop': '2026-04-22 13:45:00',   # 15:45 local
        'partner_ids': [(6, 0, [113445, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Route du Condroz 243, 4550 Nandrin',
        'description': '<p>Tier C (20j/50j). Picking recent TT/OUT/07305 (01/04). Contact: Mme Dessart, Renaud ou Philippe. Tel: +32 4 372 09 85. Sur la route retour Baillonville.</p>',
    },

    # =====================================================================
    # JEUDI 23/04 - NAMUR SUD
    # Existing: 08:30 Beauraing, 09:30 Rochefort, 10:30 Ciney,
    #           11:15 AD Ciney, 12:30 Proxy Couronne
    # After Proxy Couronne (~13:30)
    # ADD: Intermarche Anhee (OVERDUE 99j, on Dinant axis, 20 min from Beauraing route)
    # ADD: Delhaize Beauraing (same town as Carrefour Beauraing, can be done early)
    # =====================================================================
    # Delhaize Beauraing can be added right after Carrefour Market Beauraing (same street!)
    {
        'name': 'Remplissage Teatower - Delhaize Beauraing (Tier C)',
        'start': '2026-04-23 07:00:00',  # 09:00 local
        'stop': '2026-04-23 07:30:00',   # 09:30 local
        'partner_ids': [(6, 0, [116008, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': '150 rue de Rochefort, 5570 Beauraing',
        'description': '<p>Tier C (14j/50j). Contact: Mme Sovet, demander Gregory. Tel: +32 82 71 36 97. Meme rue que Carrefour Market Beauraing.</p>',
    },
    # Anhee after Proxy Couronne (on the Meuse valley, between Dinant and Namur)
    {
        'name': 'Remplissage Teatower - Intermarche Anhee (OVERDUE Tier C)',
        'start': '2026-04-23 12:00:00',  # 14:00 local
        'stop': '2026-04-23 12:30:00',   # 14:30 local
        'partner_ids': [(6, 0, [8869, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Chaussee de Dinant 127, 5537 Anhee',
        'description': '<p>Tier C OVERDUE (99j/50j max). Contact: Christophe. Tel: +32 82 71 39 84. Contrainte: jamais le lundi. Jeudi OK.</p>',
    },

    # =====================================================================
    # VENDREDI 24/04 - LUXEMBOURG
    # Existing: 09:00 Bastogne, 10:15 Hotton, 11:15 Barvaux
    # After Barvaux (11:45), Marche is only 15 min away!
    # ADD: Delhaize Marche (OVERDUE A tier! 23j)
    # ADD: Carrefour Market Marche (same town, C tier, 14j)
    # ADD: Carrefour Market Bastogne (same town as AD Bastogne, OVERDUE 72j)
    # Reorder: Bastogne clients together, then route south to north
    # =====================================================================
    # Carrefour Market Bastogne right after AD Bastogne (same town)
    {
        'name': 'Remplissage Teatower - Carrefour Market Bastogne (OVERDUE Tier C)',
        'start': '2026-04-24 07:30:00',  # 09:30 local
        'stop': '2026-04-24 08:00:00',   # 10:00 local
        'partner_ids': [(6, 0, [2864, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Route de Marche 149, 6600 Bastogne',
        'description': '<p>Tier C OVERDUE (72j/50j max). Contact: Fabienne Antoine. Tel: +32 61 21 23 42. Se presenter le matin. Meme ville que AD Bastogne.</p>',
    },
    # Delhaize Marche after Barvaux (15 min drive)
    {
        'name': 'Remplissage Teatower - Delhaize Marche (OVERDUE Tier A)',
        'start': '2026-04-24 09:45:00',  # 11:45 local
        'stop': '2026-04-24 10:15:00',   # 12:15 local
        'partner_ids': [(6, 0, [8159, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Avenue de France 39, 6900 Marche-en-Famenne',
        'description': '<p>Tier A OVERDUE (23j/20j max). Tel: +32 470 26 16 92. 15 min depuis Barvaux. En rayon depuis septembre.</p>',
    },
    # Carrefour Market Marche (same town, 5 min)
    {
        'name': 'Remplissage Teatower - Carrefour Market Marche (Tier C)',
        'start': '2026-04-24 10:30:00',  # 12:30 local -> right before lunch
        'stop': '2026-04-24 11:00:00',   # 13:00 local
        'partner_ids': [(6, 0, [3120, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Avenue du Monument 1, 6900 Marche-en-Famenne',
        'description': '<p>Tier C (14j/50j). Meme ville que Delhaize Marche. Tel: 084 31 30 76. Retour Baillonville 20 min.</p>',
    },
]

print(f"\n{len(events_to_create)} events to create\n")

created = []
for ev in events_to_create:
    try:
        eid = models.execute_kw(DB, uid, PWD, 'calendar.event', 'create', [ev])
        created.append((eid, ev['name'], ev['start']))
        print(f"CREATED #{eid}: {ev['name']} @ {ev['start']} UTC")
    except Exception as e:
        print(f"ERROR: {ev['name']}: {e}")

print(f"\nTotal created: {len(created)}")
for c in created:
    print(f"  #{c[0]}: {c[1]}")
