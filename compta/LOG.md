# LOG Compta Teatower

## 2026-04-21 — Complément batch facturation S05434 (1 facture — run 3)

- Type : création + posting + envoi (1 SO, 1 facture Odoo)
- Source : S05434 signalée par Nicolas — picking TT/PICK/08689 type=internal/done (même cause que run 2)
- Méthode : création manuelle account.move, action_post, account.move.send.wizard (ubl_bis3)
- Facture créée : id=36545, INV/2026/02168
- Partenaire : SRL Spydis - Intermarche Spy (id=116686)
- Montant HT : 315,10 EUR (305,10 SO + 10 TRANSPORT) | TTC : 335,51 EUR
- Echéance : 2026-05-21 (30 jours)
- Envoi Peppol : peppol_verification_state=valid — partner forcé invoice_sending_method=peppol — peppol_move_state=processing
- Total cumulé jour : 9 317,69 EUR HT / 9 900,49 EUR TTC (26 factures, runs 1+2+3)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05434 — run 3")

## 2026-04-21 — Complément batch facturation S05448–S05453 (5 factures — run 2)

- Type : création + posting + envoi batch (5 SO, 5 factures Odoo)
- Source : SO confirmés par Nicolas — pickings internal done (TT/PICK/08711, 08713, 08714, 08715, 08716)
- Méthode : création manuelle account.move (wizard delivered inapplicable — pickings type=internal), action_post, account.move.send.wizard
- Note méthode : le wizard sale.advance.payment.inv refuse car les pickings sont de type internal et non outgoing — création ligne par ligne avec qty_delivered et discount=30% repris des SO
- Factures créées : 5 (IDs Odoo 36540–36544)
- Numéros attribués : INV/2026/02163 à INV/2026/02167
- Montant total HT : 1 770,30 EUR | TTC : 1 884,05 EUR
- TRANSPORT ajouté : 5 factures (10 EUR HT, compte 700000, TVA 21% — absent des SO)
- Lignes EM0072 (SRP Kraft Horeca) : conservées avec disc=100% (subtotal=0) comme dans les SO
- Envoi Peppol (UBL BIS3) : 5 factures toutes en peppol_state=processing
  - INV/02163 (Delhaize de Bouge, id 36540) — uuid f7eb688b-9214-4a8b-98f8-f79d7da30066 — échéance 2026-06-20 (délai Delhaize 60j)
  - INV/02164 (BOISDIS Naninne, id 36541) — uuid 700b53f5-0f18-4194-b6c8-1df4c3da4b94
  - INV/02165 (BOISDIS Naninne, id 36542) — uuid 0fb63a93-dd91-4f56-a4cf-98ea4cee4e39
  - INV/02166 (SA Barthe Assesse, id 36543) — uuid 26b4776f-6ac1-44ac-ad91-10d0fd26e293
  - INV/02167 (Lambertdis Spar Manhay, id 36544) — uuid d0ee1e08-6b97-4157-8c41-e06c29a79b1a
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complément 5 SO — run 2")

## 2026-04-21 — Batch facturation S05351–S05439 (20 factures)

- Type : création + posting + envoi batch (23 SO, 20 factures Odoo)
- Source : sale.order invoice_status=to_invoice, state=sale/done, picking outgoing done
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 20 (IDs Odoo 36509–36528)
- Numéros attribués : INV/2026/02137 à INV/2026/02156
- Montant total HT : 7 232,29 EUR | TTC : 7 680,93 EUR
- Corrections avant posting : 5 lignes supprimées (I0880 x3, I0859 x1, I0376 x1) — qty_delivered=0 inclus par erreur dans le wizard
- Partenaires forcés peppol : 5 (Lambertdis, NDB Diffusion, PGHM, Le 7 by Juliette, Labrassine)
- Envoi Peppol (UBL BIS3) : 9 factures — INV/02137 (Cafés Préko, 75ca7ecd), INV/02138 (DB Kfé, 37eab94a), INV/02139 (Delhaize, 28e8393f), INV/02141 (Le 7 Juliette, 90c3b497), INV/02152 (Lambertdis, 06a1b47b), INV/02153 (NDB Diffusion, cec483d4), INV/02154 (Villa d'Olne, a646b0b7), INV/02155 (PGHM, d0829a62), INV/02156 (Labrassine, 3266785d) — statut : processing
- Envoi email : 9 factures — INV/02140 (La Thé Box), INV/02143 (Alcodis), INV/02144 (Cafes Delahaut), INV/02145 (Sunparks De Haan), INV/02146 (Volle Gas), INV/02147 (Carrefour Remouchamps), INV/02148 (Carrefour Belgium), INV/02149 (BTL SRL), INV/02150 (Virelles Nature)
- Non envoyées : 2 — INV/02142 (Smartbox Group, 60 EUR), INV/02151 (Clotuche Caroline Suzanne, 28 EUR) — pas d'email ni Peppol valide
- Review : S05424 Marketing Teatower (707,55 EUR HT, partenaire interne, action Nicolas requise)
- Sans livraison (non traitées) : 19 SO (S05404, S05412, S05425, S05426, S05429, S05434, S05435, S05436, S05440, S05442, S05444, S05445, S05447–S05453)
- Rapport scan : compta/reports/shipped_not_invoiced_2026-04-21.md
- Rapport batch : compta/reports/invoicing_batch_2026-04-21.md

## 2026-04-15 — Batch S05405-S05409 : correction renvoi Peppol (3 factures)

- Type : correction invoice_sending_method + renvoi Peppol
- Partenaires mis à jour (invoice_sending_method -> peppol) : SA VILLERSEM (115879), DelEmbourg invoice addr (5733), DelEmbourg parent (2909), SA Faimine invoice addr (9196), SA Faimine parent (3210)
- INV/2026/02094 (DelEmbourg) — peppol_state=processing | uuid=2dc8107b-51cc-45dc-98f8-62aeab83dd4c
- INV/2026/02095 (SA Faimine) — peppol_state=processing | uuid=a4cf80f7-24c5-4b50-a50d-d6a915855a2c
- INV/2026/02096 (SA VILLERSEM) — peppol_state=processing | uuid=f58a082f-029c-48c1-972d-ef807690dfa2
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation S05405–S05409

- Type : création + posting + envoi batch (5 SO)
- Source : S05405 / S05406 / S05407 / S05408 / S05409 — tous state=sale, tous entièrement livrés
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 5 (IDs Odoo 36242–36246)
- Numéros attribués : INV/2026/02092 à INV/2026/02096
- Montant total HT : 1 240,03 EUR | TTC : 1 314,43 EUR
- Envoi Peppol : 2 factures — S05405 (BARVO/Carrefour Barvaux, uuid 8caf61ac) + S05408 (GIMALEX/Delhaize Fragnée, uuid 9766cd23) — statut : processing
- Envoi email : 3 factures — S05406 (SA VILLERSEM), S05407 (SA Faimine), S05409 (DelEmbourg)
- Fallback email : S05406 + S05409 (Peppol EAS/endpoint configurés sur partenaire mais invoice_sending_method non défini)
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation : TRANSPORT + Posting + Envoi

- Type : correction transport + validation + envoi batch
- Lignes TRANSPORT ajoutées : 2 nouvelles factures draft créées (Odoo 36236, 36237) pour S05403 (Volle Gas) et S05375 (Carrefour Remouchamps) — 10 EUR HT chacune, produit [TRANSPORT], compte 700000, TVA 21%
- Les 7 autres lignes TRANSPORT des SO concernés étaient déjà facturées (qty_inv=1)
- action_post : 36 factures postées (IDs 36200–36237, hors avoirs 36223/36235) — 0 échec
- Numéros attribués : INV/2026/02055 à INV/2026/02090
- Montant total HT batch complet : 14 581,15 EUR | TTC : 15 482,38 EUR
- Envoi Peppol : 14 factures (Van Der Valk, ILLICO RESTO, Europadrinks, Delhaize x2, Pascal CHERAIN, Moulins Burette, Cafés Antillia, Spinée SA, All in One, SRL Tartine, Au Comptoir Local, Smart fridges, Carrefour Remouchamps TRANSPORT)
- Envoi email : 21 factures
- Non envoyé : 1 (INV/2026/02077 — Clotuche Caroline Suzanne, id=122331, pas d'email ni Peppol)
- Rapport mis à jour : compta/reports/invoicing_batch_2026-04-15.md

## 2026-04-15 — Batch facturation (34 factures draft créées)

- Type : création factures clients batch
- Source : sale.order invoice_status=to_invoice, state=sale/done (85 SO scannés)
- Méthode : sale.advance.payment.inv wizard, mode "delivered" (qty_delivered)
- Factures draft créées : 34 (IDs Odoo 36200–36234 sauf 36223/36235 qui sont des avoirs)
- Montant total HT : 14 561,15 EUR | TTC : 15 461,18 EUR
- Exclus Amazon : 36 SO (741,40 EUR HT) — détectés via origin "Amazon Order"
- Exclus 0 EUR : 5 SO (Marketing Teatower, Newpharma, Laetitia Mariette, Perte marchandise)
- Exclus sans livraison : 8 SO (3 403,22 EUR HT en attente livraison)
- Avoirs draft détectés : 2 (36223 ann philippe verhelle, 36235 Lidwine Fetten) — à examiner
- Rapport : compta/reports/invoicing_batch_2026-04-15.md
- Statut : DRAFT — Nicolas doit valider (action_post) avant envoi

## 2026-04-15 — Rapport commandes expédiées non facturées

- Type : analyse / rapport
- Source : sale.order (state: sale/done, invoice_status: to invoice, picking outgoing: done)
- Résultat : 70 SO to_invoice identifiées, dont 70 avec au moins un outgoing picking done
- Montant total HT : 14 173,10 EUR
- Rapport : compta/reports/shipped_not_invoiced_2026-04-15.md
- Top 3 : The Torrefactory Project Sa (1 950 EUR) / Carrefour Belgium (1 646 EUR) / Moulins Burette (1 406 EUR)
- Alerte : 34 commandes e-commerce de déc. 2025 (> 120 jours) non régularisées

## 2026-04-14 — Rapprochement bancaire ING (165 lignes)

### Identification des 165
- Source : `account.bank.statement.line` is_reconciled=False, journal ING BE30 3631 6408 2311 (id=14)
- Composition : 165 lignes ING uniquement (+ 77 autres journaux cash/caisse non traitées)
- Positives (encaissements) : 63 — Négatives (paiements) : 102

### Matches sûrs trouvés : 11
Critères : même montant exact (écart ≤ 0,01 EUR), même partenaire (direct ou commercial_parent), date BSL dans [date_facture - 5j, date_facture + 180j]

| BSL id | Date | Montant | Facture | Partenaire | Résultat |
|--------|------|---------|---------|------------|---------|
| 17823 | 2026-04-10 | +403,97 EUR | INV/2026/01151 | Belgradis - Intermarché Belgrade | lettré |
| 17827 | 2026-04-10 | +181,26 EUR | INV/2026/01521 | Les Mignées (via Quoibion Gestim) | lettré |
| 17813 | 2026-04-09 | +1 792,19 EUR | INV/2026/01178 | Pharmacie Saint Pierre SA | lettré |
| 17800 | 2026-04-09 | +90,00 EUR | INV/2026/01415 | l'Apaq-W | lettré |
| 17772 | 2026-04-08 | +345,10 EUR | INV/2026/01258 | SA Barthe - Intermarché Assesse | lettré |
| 17771 | 2026-04-08 | +715,50 EUR | INV/2026/01308 | Sorescol S.A. | lettré |
| 16934 | 2026-03-01 | -31,00 EUR | RESA670 | ING Belgique SA | lettré |
| 16651 | 2026-02-16 | -281,85 EUR | RESA573 | Easyplug S.R.L. / Ez Charge | lettré |
| 16646 | 2026-02-16 | -46,88 EUR | RESA671 | Action Belgium BVBA | lettré |
| 16398 | 2026-02-04 | -112,56 EUR | RESA686 | Happy Family Wouip | lettré |
| 16118 | 2026-01-21 | -14,52 EUR | RESA532 | ING Belgique SA | lettré |

**Total lettrés : 11 / 11 matches sûrs (100%)**

### Méthode technique utilisée
1. `account.move.line.write([susp_ml_id], {'account_id': acct_receivable_or_payable, 'partner_id': partner_id})` — remplace la ligne compte de passage (499000) par le compte tiers correct
2. `account.move.action_post([bsl_move_id])` — reposte l'écriture après modification
3. `account.move.line.reconcile([susp_ml_id, invoice_ml_id])` — lettrage des deux lignes tiers

### Résultat
- ING non rapprochées avant : 165
- ING non rapprochées après : 154
- Lettrées automatiquement : 11
- En review : 27 (Vilna Gaon x3, Shyfter ambigus x2, ING frais ambigus x3, partenaires sans facture ouverte x19)
- Sans partenaire ni match : 127

### Fichiers générés
- `compta/review/lettrages_review_2026-04-14.md` — détail des 27 cas en attente
| 2026-04-14 | 367 | - |
