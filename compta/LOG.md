# LOG Compta Teatower

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
