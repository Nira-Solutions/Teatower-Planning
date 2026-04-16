import xmlrpc.client, sys
sys.stdout.reconfigure(encoding='utf-8')
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

jerome_partner_id = 6494
jerome_user_id = 12

# Find Chili Peppers (Intermarche Tilff) partner ID
tilff_ids = models.execute_kw(DB, uid, PWD, 'res.partner', 'search', [[
    ['name', 'ilike', 'Chili Peppers'],
    ['is_company', '=', True],
]], {'limit': 1})
tilff_id = tilff_ids[0] if tilff_ids else 0
print(f"Chili Peppers ID: {tilff_id}")
if tilff_ids:
    tp = models.execute_kw(DB, uid, PWD, 'res.partner', 'read', [tilff_ids], {'fields': ['name','street','zip','city','phone']})[0]
    tilff_loc = f"{tp.get('street','')} {tp.get('zip','')} {tp.get('city','')}"
    print(f"  {tp['name']} | {tilff_loc} | tel:{tp.get('phone','')}")
else:
    tilff_loc = "4130 Esneux"

events_to_create = [
    # MARDI 21/04 - Namur zone
    # 08:30-09:00 Carrefour Hyper Jambes (HYPER = matin obligatoire)
    {
        'name': 'Remplissage Teatower - Carrefour Hyper Jambes (S05355)',
        'start': '2026-04-21 06:30:00',
        'stop': '2026-04-21 07:00:00',
        'partner_ids': [(6, 0, [9046, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Avenue prince de Liege 57-59, 5100 Jambes',
        'description': '<p>Remplissage - S05355 (842 EUR, livraison partielle). HYPER = matin obligatoire. Balisages + arrets rayon. Tel: +32 81 33 20 11</p>'
    },
    # 10:15-10:45 Intermarche Naninne (OVERDUE Tier A)
    {
        'name': 'Remplissage Teatower - Intermarche Naninne (OVERDUE Tier A)',
        'start': '2026-04-21 08:15:00',
        'stop': '2026-04-21 08:45:00',
        'partner_ids': [(6, 0, [2812, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Chaussee de Marche 860, 5100 Naninne',
        'description': '<p>Tier A OVERDUE (21j/20j max). Contact: Stephanie. Tel: 081 63 36 96</p>'
    },
    # 11:00-11:30 Intermarche Bouge (OVERDUE Tier B)
    {
        'name': 'Remplissage Teatower - Intermarche Bouge (OVERDUE Tier B)',
        'start': '2026-04-21 09:00:00',
        'stop': '2026-04-21 09:30:00',
        'partner_ids': [(6, 0, [3297, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Chaussee de Louvain 257, 5000 Bouge',
        'description': '<p>Tier B OVERDUE (49j/35j max). Contact: Dany Decoster. Tel: 081569346</p>'
    },
    # 11:45-12:15 Intermarche Belgrade (OVERDUE Tier B)
    {
        'name': 'Remplissage Teatower - Intermarche Belgrade (OVERDUE Tier B)',
        'start': '2026-04-21 09:45:00',
        'stop': '2026-04-21 10:15:00',
        'partner_ids': [(6, 0, [2821, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Allee des Ormes 15, 5001 Belgrade',
        'description': '<p>Tier B OVERDUE (49j/35j max). Contact: Stephanie. Tel: 081260187</p>'
    },
    # 13:00-13:30 Intermarche Floriffoux (Tier B)
    {
        'name': 'Remplissage Teatower - Intermarche Floriffoux (Tier B)',
        'start': '2026-04-21 11:00:00',
        'stop': '2026-04-21 11:30:00',
        'partner_ids': [(6, 0, [2958, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue Emeree 4, 5150 Floriffoux',
        'description': '<p>Tier B (35j/35j, a la limite). Contact: Loredana / Manon. Tel: 081 44 05 39</p>'
    },
    # MERCREDI 22/04 - Liege zone
    # 09:00-09:30 Delhaize Embourg
    {
        'name': 'Remplissage Teatower - Delhaize Embourg (Tier A, S05409)',
        'start': '2026-04-22 07:00:00',
        'stop': '2026-04-22 07:30:00',
        'partner_ids': [(6, 0, [2909, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Voie de l ardenne 57, 4053 Embourg',
        'description': '<p>Remplissage S05409 (208 EUR). Contact: Kevin Demarteau. Tel: 043 61 25 69</p>'
    },
    # 09:45-10:15 Intermarche Tilff
    {
        'name': 'Remplissage Teatower - Intermarche Tilff (Tier A)',
        'start': '2026-04-22 07:45:00',
        'stop': '2026-04-22 08:15:00',
        'partner_ids': [(6, 0, [tilff_id, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': tilff_loc,
        'description': '<p>Tier A (14j/20j). Visite reguliere haute frequence.</p>'
    },
    # 10:30-11:00 Intermarche Faimes
    {
        'name': 'Remplissage Teatower - Intermarche Faimes (Tier B, S05407)',
        'start': '2026-04-22 08:30:00',
        'stop': '2026-04-22 09:00:00',
        'partner_ids': [(6, 0, [3210, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue De Huy 27, 4317 Faimes',
        'description': '<p>Remplissage S05407 (378 EUR). Tel: 019678378</p>'
    },
    # 11:15-11:45 Intermarche Villers Le Bouillet (mercredi = jour prefere)
    {
        'name': 'Remplissage Teatower - Intermarche Villers Le Bouillet (Tier B, S05406)',
        'start': '2026-04-22 09:15:00',
        'stop': '2026-04-22 09:45:00',
        'partner_ids': [(6, 0, [115879, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue du Chateau d eau 1, 4530 Villers-Le-Bouillet',
        'description': '<p>Remplissage S05406 (275 EUR). Mercredi = jour prefere. Contact: Christophe ou Johan. Tel: +32 85 31 69 11</p>'
    },
    # JEUDI 23/04 - Beauraing/Rochefort/Ciney axis
    # 08:30-09:00 Carrefour Market Beauraing (OVERDUE Tier A)
    {
        'name': 'Remplissage Teatower - Carrefour Market Beauraing (OVERDUE Tier A)',
        'start': '2026-04-23 06:30:00',
        'stop': '2026-04-23 07:00:00',
        'partner_ids': [(6, 0, [2905, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue de Rochefort 37, 5570 Beauraing',
        'description': '<p>Tier A OVERDUE (22j/20j max). Contact: Therese / Alison. Tel: 082/71 02 30</p>'
    },
    # 09:30-10:00 AD Rochefort (OVERDUE Tier B)
    {
        'name': 'Remplissage Teatower - AD Rochefort (OVERDUE Tier B)',
        'start': '2026-04-23 07:30:00',
        'stop': '2026-04-23 08:00:00',
        'partner_ids': [(6, 0, [7692, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue de Marche 112-114, 5580 Rochefort',
        'description': '<p>Tier B OVERDUE (46j/35j max). Tel: +32 84 21 01 03</p>'
    },
    # 10:30-11:00 Carrefour Market Ciney
    {
        'name': 'Remplissage Teatower - Carrefour Market Ciney (Tier B, S05384)',
        'start': '2026-04-23 08:30:00',
        'stop': '2026-04-23 09:00:00',
        'partner_ids': [(6, 0, [2773, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue du commerce 44, 5590 Ciney',
        'description': '<p>Remplissage S05384 (390 EUR). Contact: Eric Watelet. Tel: 083 21 21 63</p>'
    },
    # 11:15-11:45 AD Ciney
    {
        'name': 'Remplissage Teatower - AD Ciney (Tier B, S05383)',
        'start': '2026-04-23 09:15:00',
        'stop': '2026-04-23 09:45:00',
        'partner_ids': [(6, 0, [7678, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Chemin de Crahiat 18A, 5590 Ciney',
        'description': '<p>Remplissage S05383 (450 EUR). Contact: Donnay David. Tel: +32 83 21 27 55</p>'
    },
    # VENDREDI 24/04 - Luxembourg province route
    # 09:00-09:30 AD Bastogne (OVERDUE Tier A)
    {
        'name': 'Remplissage Teatower - AD Bastogne (OVERDUE Tier A)',
        'start': '2026-04-24 07:00:00',
        'stop': '2026-04-24 07:30:00',
        'partner_ids': [(6, 0, [8558, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Route de Marche 112-114, 6660 Bastogne',
        'description': '<p>Tier A OVERDUE (22j/20j max). Contact: Valentin Gilson. Tel: +32 61 21 70 84</p>'
    },
    # 10:15-10:45 Carrefour Market Hotton
    {
        'name': 'Remplissage Teatower - Carrefour Market Hotton (Tier B, S05372)',
        'start': '2026-04-24 08:15:00',
        'stop': '2026-04-24 08:45:00',
        'partner_ids': [(6, 0, [2979, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Rue de la Jonction 16, 6990 Hotton',
        'description': '<p>Remplissage S05372 (393 EUR). Contact: Gauthier Lempereur. Tel: 084 46 73 44</p>'
    },
    # 11:15-11:45 Carrefour Market Barvaux
    {
        'name': 'Remplissage Teatower - Carrefour Market Barvaux (Tier B, S05405)',
        'start': '2026-04-24 09:15:00',
        'stop': '2026-04-24 09:45:00',
        'partner_ids': [(6, 0, [2811, jerome_partner_id])],
        'user_id': jerome_user_id,
        'location': 'Route de Marche 26, 6940 Barvaux/Ourthe',
        'description': '<p>Remplissage S05405 (250 EUR). Contact: Nathalie Warnier. Tel: 086 21 13 79</p>'
    },
]

created = []
for ev in events_to_create:
    try:
        eid = models.execute_kw(DB, uid, PWD, 'calendar.event', 'create', [ev])
        created.append((eid, ev['name'], ev['start']))
        print(f"CREATED event #{eid}: {ev['name']} @ {ev['start']} UTC")
    except Exception as e:
        print(f"ERROR creating {ev['name']}: {e}")

print(f"\nTotal created: {len(created)}")
for c in created:
    print(f"  #{c[0]}: {c[1]}")
