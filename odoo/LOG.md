
## 2026-06-03 — Fix double-TVA Shopify à la cause racine (backfill pays parents + cron) — WRITE, validé Nicolas

- **Type** : Correction donnée partenaire + automation. AUCUNE écriture sur factures/écritures/FP existantes (passif 260 factures hors scope). Tout réversible.
- **Cause racine confirmée** : connecteur Emipro crée un parent B2C Shopify SANS `country_id` et des enfants (invoice/delivery) AVEC le pays. L'auto-apply FP se base sur le pays du parent → parent sans pays → aucune FP → lignes restent en taxe HT 3/8 → double-TVA.
- **VOLET 1 dry-run** (`_tva_shopify_dryrun.py/.json`) : 168 parents Shopify (`is_shopify_customer=True`, `country_id=False`, `parent_id=False`) sans pays. 167 non-ambigus à traiter (162 BE, 4 FR, 1 DE), 1 ambigu exclu (#120294 Daniel quetelard = BE+FR divergents, laissé pour décision Nicolas), 0 sans enfant avec pays. Logique : recopie pays enfant, priorité `delivery` > `invoice`.
- **VOLET 2 backfill** (`_tva_shopify_backfill.py`) : `country_id` écrit sur 167 parents (valeur avant = False pour tous). Rollback complet dans `_tva_shopify_backfill_rollback.json` (ids + pays avant/après + enfant source). 0 skip. AUCUN recalcul des SO/factures passées.
- **VOLET 3 automation** : `ir.cron` id=**82** "[TVA-SHOPIFY] Backfill pays parents Shopify (anti double-TVA)", `model_id=87 res.partner`, intervalle 1h, périmètre strict `is_shopify_customer=True` (jamais B2B/GMS manuels), même logique non-ambiguë (skip si pays enfants divergents). Réversible : `active=False` (1 clic) ou `unlink([82])`. Choix cron > base.automation : plus simple, idempotent, désactivable d'1 clic, ne dépend pas du timing d'écriture enfant→parent du connecteur.
- **TEST FP** (`_tva_shopify_validate.py`) : devis draft temporaires créés sur 3 parents backfillés puis supprimés (aucun impact compta/stock). Résultat : BE #110830 → FP EU B2C ✔, FR #107220 → OSS B2C France ✔, DE #105153 → OSS B2C Allemagne ✔. Double-TVA stoppée, OSS préservé.
- **Run cron manuel** : idempotent, ne reste que l'ambigu #120294. OK.
- **Fichiers** : `odoo/_tva_shopify_dryrun.*`, `_tva_shopify_backfill.py`, `_tva_shopify_backfill_rollback.json`, `_tva_shopify_validate.*`, `_tva_shopify_create_cron.py`, `_tva_shopify_fpmap.json`.

## 2026-06-03 — Investigation config connecteur Shopify (mapping TVA) — LECTURE SEULE

- **Type** : Diagnostic config, AUCUNE écriture Odoo (validation Nicolas requise avant tout fix).
- **Demande** : comprendre pourquoi certaines commandes Shopify prennent 128/129 (TTC, correct) et d'autres 3/8 (HT, double-TVA sur prix déjà TTC), trouver le point de réglage centralisé.
- **Connecteur** : Emipro (`shopify.instance.ept`, suffixe `.ept`). Instance id=1 "Odoo x Shopify", créée 2025-11-10. Option `apply_tax_in_order = "odoo_tax"` (Odoo Default Tax Behaviour) → la taxe = taxe par défaut de la fiche produit, remappée par la position fiscale du client. Le connecteur N'IMPORTE PAS les taxes Shopify.
- **Cause racine** : tous les produits sale_ok sont en taxe HT par défaut (1024 en `8`=6% HT, 392 en `3`=21% HT, seulement 1 en TTC). La conversion HT→TTC repose ENTIÈREMENT sur la position fiscale. FP "EU B2C" (id=2) remappe 3→129 et 8→128 (correct) ; FP "Belgium B2B" (id=1) ne remappe rien (normal, B2B HT). Quand le partenaire Shopify n'a pas de pays / pas de FP auto, ou que la FP est posée sur l'en-tête après figeage des lignes, le remap ne s'applique pas → lignes restent 3/8 → double-TVA.
- **Preuve** : SO #48985 (FP=False) lignes en 8/3 vs SO #48986 (FP=EU B2C) lignes en 128 — même connecteur, même jour, 1h30 d'écart. Mapping EU B2C stable depuis 2025-03-31.
- **Impact mesuré (12 mois)** : 260 factures touchées / 2963. TVA réellement surfacturée B2C ≈ 1218 EUR. Postes : produits thé/accessoires 1142 EUR, livraison Bpost 118 EUR, ateliers 53 EUR (discounts en négatif -95). Belgium B2B (67 factures) = faux positif (HT B2B légitime).
- **Produits techniques en cause** : "Livraison Bpost"/"Livraison point relais" (taxe 3=21% HT, devraient être 129 TTC ou exonéré selon politique), "Shopify Discount Product"/"DISC" (taxe 8=6% HT).
- **Reco livrée** : voir rapport. Solution la plus propre = forcer la FP côté connecteur/partenaire B2C (fiabiliser le pays à l'import) + s'assurer que les produits techniques (livraison/discount) sont mappés par la FP. Détail des options (a/b/c) dans le rapport remis à Nicolas.
- **Fichiers** : `odoo/_diag_tva_shopify_step5.py` à `step16.py` + JSON associés.

## 2026-05-29 — Plan GMS Option A — EXÉCUTION RÉELLE (WRITE)

- **Type** : Configuration Odoo — écriture réelle (validée par Nicolas, Plan A uniquement)
- **Demande** : Câbler le Plan A (sortie GMS native depuis warehouse GMS wh=2). Pas de Plan C, pas d'orderpoints, pas d'inventaire.
- **Correction d'un raccourci du script dry-run** : le script parlait de "route 17". En réalité l'ID 17 = `stock.rule` "GMS: Stock → Customers (MTO)" (déjà active), portée par la route 1 (Replenish on Order / MTO). La vraie cause racine était bien le **picking type 13 inactif** que cette règle utilise.
- **A1 (geste central)** : `stock.picking.type` id 13 "Stock Merchandiser: Bons de livraison" (OUT, src GMS/Stock 2737 → dest Partners/Customers 5, warehouse 2) — `active` **False → True**.
- **A2** : NON appliqué (pas de filet salesperson, property_warehouse_id uid 6 non touché — conforme à la décision).
- **A3** : devis `S05388` (id 8075, Antheco SA / Intermarché Anthée) — re-vérifié AVANT write : state=draft, picking_ids=[] → conditions OK. `warehouse_id` **1 (Teatower) → 2 (Stock Merchandiser)**.
- **Vérifs post-write** :
  - picking type 13 : active=True confirmé.
  - règle 17 fonctionnelle : active=True, MTO, GMS/Stock → Customers, picking type 13.
  - S05388 : state=draft, warehouse_id=2 confirmé.
  - Non-ambiguïté : la SEULE règle de sortie client portée par le picking type 13 du WH2 est la règle 17. La règle 14 (route 9) va vers TT/Stock, pas vers le client → aucun conflit de résolution.
- **Test bout-en-bout (lecture seule, aucune donnée créée)** : une SO confirmée sur warehouse_id=2 résout désormais sa livraison via la règle 17 → génère un picking **picking_type 13 (GMS/OUT), location_id=GMS/Stock, location_dest_id=Partners/Customers**. C'est le flux GMS voulu. Réappro GMS/Stock = règle 22 (route 12, TT/Stock→GMS/Stock, picking type 23) / orderpoints — hors périmètre de cette tâche.
- **Impact** : 2 records modifiés (picking.type 13, sale.order 8075). 0 erreur. Le flux de sortie GMS est désormais vivant et natif sur le warehouse GMS.

## 2026-05-29 — Plan GMS Option A (warehouse dédié) + scripts DRY-RUN

- **Type** : Diagnostic + plan + scripts (LECTURE SEULE, aucune écriture Odoo)
- **Demande** : Nicolas — Option A retenue (warehouse GMS wh=2, route native GMS->Customers, réappro auto TT/Stock->GMS/Stock). Produire plan A->D + scripts dry-run.
- **Constats recon** (`odoo/_gms_planA_recon.json`) :
  - Picking type 13 "Stock Merchandiser: Bons de livraison" (OUT GMS) = INACTIF -> route 17 morte. Cause racine du flux GMS cassé.
  - Aucun champ default warehouse sur res.partner ; property_warehouse_id existe sur res.users seulement. Pas de user "Gilles".
  - 828 SO GMS confirmées sur wh=1 (Teatower) + 1 devis draft (S05388). Sortie réelle GMS forcée manuellement sur pickings TT/PICK (src=GMS/Stock).
  - Route 13 redondante : 0 produit/template -> désactivable. Rules parasites 21(Buy)/18(Manufacture) vers GMS/Stock.
  - Orderpoints GMS : 2 sans route (18715 TEST, 18777 Display) à supprimer ; 12 avec qty_multiple=0 à corriger ; 7 SKU vendus sans orderpoint (dont 4 saisonniers Noël à valider).
- **Livrables** : `odoo/gms_planA_warehouse_outflow.py`, `gms_planB_van_reload.py`, `gms_planC_cleanup_config.py`, `gms_planD_reservation.py` (tous DRY_RUN=True), recon `odoo/_gms_planA_recon.py`.
- **Statut** : EN ATTENTE validation Nicolas avant tout write.

## 2026-05-28 — Config Peppol 22 partners email (batch 02728-02771)

- **Type** : Configuration Peppol res.partner
- **Demande** : Nicolas — activer Peppol sur les 22 partners qui ont recu email le 28/05
- **Methode** : reverse engineering sur 21 partners Peppol confirmes (eas 0208/9925 BE) + verification via button_account_peppol_check_partner_endpoint
- **Pattern Teatower** : Belgique = eas 0208 (BCE) endpoint sans BE, OU eas 9925 (BE VAT) endpoint avec BE prefixe
- **Resultat** :
  - 13/22 partenaires passes en method=peppol (verif=valid)
  - 1 VAT normalise : Sandrine Tahir BE0786 417 996 -> BE0786417996 (reste not_valid, email maintenu)
  - 6 restes email (not_valid Peppol) : Boulangerie Co'Pains, Brasserie Wolkraft, D.BRAIVES, Esprit de campagne, Cafes Delahaut (Facturation), Hello Bio (facturation)
  - 2 restes email (pas de VAT) : Carrefour Belgium Corporate Village, Faire.Com
  - Actions : write invoice_sending_method=peppol sur IDs [116231, 5437, 5432, 123845, 5625, 123843, 7027, 5448, 6024, 123901, 5572, 123969, 10103]
- **Pas de re-envoi des factures deja envoyees** — config pour futures factures uniquement

## 2026-05-28 — Batch post + envoi 44 factures B2B (Peppol + Email)

- **Type** : action_post + account.move.send.wizard (Peppol / Email)
- **Demande** : Nicolas GO post + envoi 28/05/2026
- **Factures postees** : 44/44 — IDs 38824 a 38867 — INV/2026/02728 a INV/2026/02771
- **38823 (La Gloriette)** : laissee en draft (anomalie, decision Nicolas en attente)
- **Split envoi** :
  - Peppol envoye : 21 factures (IDs : 38824, 38826, 38829, 38830, 38831, 38836, 38837, 38838, 38840, 38842, 38844, 38847, 38848, 38851, 38852, 38857, 38859, 38863, 38864, 38865, 38867)
  - Email envoye : 22 factures (IDs : 38825, 38827, 38828, 38832, 38833, 38834, 38835, 38839, 38841, 38843, 38845, 38846, 38849, 38850, 38853, 38855, 38856, 38858, 38860, 38861, 38862, 38866)
    - dont 38843 (Boulangerie Les Co'Pains BE0600867290) : Peppol refuse (not_valid), fallback email OK
  - Manuel a traiter : 38854 (Faire.Com, 127,20 EUR) — aucun email ni Peppol
- **Total envoye** : 43 factures sur 44 — 21 594,95 EUR TTC
- **Echec final** : 0 (38843 resolu en email fallback)
- **A traiter manuellement** : 38854 Faire.Com (enregistrer email dans Odoo ou envoyer manuellement)

## 2026-05-28 — Batch facturation B2B GO Nicolas (45 SO brouillon)

- **Type** : Creation factures clients (out_invoice) + forçage transport
- **Demande** : Nicolas GO facturation B2B "bien livre" 28/05/2026
- **Scope** : 55 SO to_invoice dans dump _tmp_to_invoice.json, 8 exclues manuellement
- **Etape 1 - Transport force** : 12 lignes [TRANSPORT] qty_delivered forcees a qty_ordered via write XML-RPC
  - SO concernees : S05596, S05603, S05605, S05614, S05628, S05632, S05630, S05641, S05642, S05655, S05660, S05663
- **Etape 2 - Wizard** : sale.advance.payment.inv mode `delivered` sur 45 SO
  - 45 factures brouillon creees (IDs Odoo 38823 a 38867)
  - Toutes en etat `draft` — NON postees, en attente validation Nicolas
- **Total HT brouillon** : 20 546,78 EUR
- **SO sautees** : #48143 (Jessica Masula, Shopify, 0 livraison), S05621 (Jarosz Amazon, 0 livraison)
- **Anomalie S05484** : Facture brouillon 38823 = 59,44 EUR HT (2 lignes non encore livrees : 05V0880 Blue Earl Grey + 05V0717 Pomme d'amour). Les 10 autres lignes (154,27 EUR HT) etaient deja facturees anterieurement (qty_invoiced=1). A supprimer si livraison pas confirmee.
- **Exclues batch** (decision Nicolas) : S00738/S04347/S05192 (anciens), S05643/S05644/S05652 (livraison Gilles imminente), S05454/S05600 (montant 0)

## 2026-05-26 — Correction tags res.partner.category (audit data-bi forecast Mai 2026 B2B)

- **Type** : Ecriture XML-RPC `res.partner.write` (category_id)
- **Demande** : Nicolas valide correction de 3 partners mal tagges detectes par audit forecast
- **Diagnostic** :
  - Mapping tag IDs Odoo confirme : 27=GMS, 28=Revendeur, 85=Canal B2B Direct, 86=Canal DTC Shopify (3476 partners B2C), 88=Canal GMS
  - Pattern observe : GMS magasins enfants utilisent surtout tag 88 (Canal GMS), tag 27 (GMS) est plutot sur personnes morales facturantes (104/119 partners 27 ont aussi 88)
  - Pattern Revendeur : combo standard [85, 28] (Canal B2B Direct + Revendeur) sur 'Le Comptoir Local Linkebeek', 'Esprit de campagne', 'Au Comptoir Local'
- **Actions** (instruction Nicolas suivie strictement, pas d'ajout 88/85 non demande) :
  - #123449 VENTE-PRIVEE.COM : `[]` -> `[28 Revendeur]` (ajout)
  - #9461 Proxy Delhaize St Michel (parent #2912 Delhaize Le Lion) : `[86 Canal DTC Shopify]` -> `[27 GMS]` (retrait 86 + ajout 27)
  - #123069 Carrefour Market Bievre (parent #6596 Carrefour Belgium) : `[]` -> `[27 GMS]` (ajout)
- **Note pour Nicolas** : Pour coherence avec autres magasins enfants Delhaize/Carrefour, les tags 88 (Canal GMS) pourraient aussi etre ajoutes a #9461 et #123069. Idem 85 (Canal B2B Direct) pour #123449. Non fait — strict respect du brief. A statuer.
- **Impact** : 3 partners modifies, 0 erreur
- **Scripts** : `odoo/_tag_audit_step{1,2,3,4,5}.py`, `odoo/_tag_audit_apply.py`, log JSON `odoo/_tag_audit_apply_log.json`

## 2026-05-13 — AUDIT LECTURE SEULE : Ecart P&L vs Tresorerie — Dethlefsen & Balk + Kirchner Fischer

- **Type** : Audit lecture seule (aucune ecriture creee — regle dure respectee)
- **Perimetre** : account.move (in_invoice), purchase.order, stock.picking pour partenaires 6398 (Dethlefsen) et 7195/9989 (Kirchner)
- **Resultat** :
  - Kirchner Fischer : 6 POs receptionnees non facturees = 170 754,05 EUR de charges manquantes au P&L (P00470 66k, P00480 64k, P00495 32k + 3 reliquats anciens)
  - Dethlefsen & Balk : 24 POs receptionnees partiellement ou totalement non facturees = 20 127,85 EUR
  - Total trou charges : 190 881,90 EUR (bornee haute — certains PO partiellement livres)
  - Comptes d'imputation OK : 600000 "Purchases of Raw Materials" utilise sur TOUTES les factures postees des 2 fournisseurs (pas de derive vers compte 31 stocks)
  - 3 factures Dethlefsen en DRAFT (non postees) : R1155295 (-1,03 EUR), R1155015 (432,97 EUR), R1154396 (184,45 EUR) — a valider/poster
  - P00501 et P00518 Dethlefsen (6 331,62 EUR) : PO confirmes mais reception en statut "assigned" (pas encore done) — pas inclus dans le trou
  - P00528 Kirchner (31 375 EUR) : livraison prevue 2026-07-03, pas encore receptionnee — pas inclus
- **Recommandation** : saisir prioritairement factures Kirchner P00470 + P00480 + P00495 (163k), puis FNP provision en OD pour les PO sans facture recue. Aucune ecriture faite sans validation Nicolas.

## 2026-05-07 — POS POP-UP STORE restreint aux 8 produits du salon "C'est bon c'est Wallon" (10-11 mai 2026)

- **Demande** : limiter les produits vendables sur le POS du stand au seul contenu du transfert interne `POP/INT/00028` (TT/Stock -> POP/Stock).
- **Picking source** : id=42283, state=`assigned`, 8 lignes, location_dest=POP/Stock (id 4575).
  - GI0916 Vergers d'ete Pomme-Poire (50), GI0832 La Nana de Wepion (50), GI0735 Peche de Vigne BIO (50), GI0820 Marrakech Sunset BIO (50), GI0912 Passion Exotique (50), GI0634 Gourmandise glacee (50), A1055 Mug Lorenzo (12), A0557 Carafe the glace 1.5L (8).
- **POS cible** : `pos.config` id=2, name=`POP-UP STORE` (warehouse Teatower, picking_type id 73 "POP-UP STORE: Commandes du PdV"). Sans ambiguite — c'est l'unique POS avec `limit_categories=True` et picking_type dedie POP-UP.
- **Etat avant** : `iface_available_categ_ids=[68]` (categ MIA26, 19 produits visibles dont seulement 2 du picking).
- **Approche choisie** : creation d'une nouvelle `pos.category` "Salon Wallon 2026" (id=69), ajout de cette categ aux 8 product.template du picking via `(4, 69)` (sans toucher aux pos_categ_ids existantes), puis switch `pos.config #2.iface_available_categ_ids = [69]`. **Non destructif** : aucune modif sur les autres POS (Waterloo, Liege, Namur, Liege bis, Rocourt) et aucun produit n'a perdu de categorie.
- **Verification** : `product.template` filtre `pos_categ_ids in [69] AND available_in_pos=True` -> exactement 8 produits, identiques au picking.
- **Snapshot rollback** : `odoo/pos_salon_wallon_2026_snapshot.json` (etat avant + after + script rollback).
- **Plan rollback lundi 12 mai** :
  1. `pos.config.write([2], {'iface_available_categ_ids': [(6,0,[68])]})` -> remet la categ MIA26.
  2. Optionnel : retirer la categ des 8 templates via `pos_categ_ids=[(3,69)]`, puis `pos.category.unlink([69])`.
- **Impact** : 0 SO impactee, 0 PO impactee, POS POP-UP STORE pret pour le salon ce week-end (10-11 mai).

## 2026-05-05 — P00523 Marketing Teatower : remplacement 56 lignes -> 16 lignes @ -100%

- **Demande** : remplacer les 56 lignes (complement) du PO P00523 (id=527, partner Marketing Teatower id=3127) par 16 lignes de stock marketing existant, toutes a 100% de discount. Total cible : 154 unites, 0,00 EUR.
- **Etat initial** : PO state=`purchase`, picking TT/IN/00752 (id 42526) state=`assigned`, amount_total=764,07 EUR.
- **Procedure executee** :
  1. `purchase.order.button_cancel` -> PO=cancel, picking 42526=cancel.
  2. `purchase.order.button_draft` -> PO=draft.
  3. `purchase.order.line.unlink` x56 -> 0 ligne restante.
  4. Resolution 16 default_code -> product.product (tous trouves).
  5. `purchase.order.line.create` x16 avec `discount=100.0`, `taxes_id=[(6,0,[])]`, `name=product.name`. Champ `discount` natif Odoo 18 OK.
  6. price_unit calcule par Odoo via seller_ids/standard_price (C0187 et C0188 a 0 EUR — pas de prix d'achat reference, mais discount 100% donc subtotal=0 OK).
  7. `purchase.order.button_confirm` -> PO=purchase, nouveau picking TT/IN/00754 (id 42536) genere, state=`assigned`.
- **Resultat final** : 16 lignes, 154 unites, amount_total=**0,00 EUR**, picking TT/IN/00754 assigned, ancien picking 42526 reste en `cancel`.
- **URLs** :
  - PO : https://tea-tree.odoo.com/odoo/purchase/527
  - Picking : https://tea-tree.odoo.com/odoo/inventory/42536

## 2026-05-05 — S05534 VENTE-PRIVEE : application FP Intra-Community + restore prix XLSX

- **Demande Nicolas** : sur S05534 (sale.order id=8404, partner 123449 VENTE-PRIVEE.COM, VAT FR70434317293, FR), appliquer la fiscal position intracommunautaire B2B pour passer la TVA 6% en autoliquidation.
- **Diagnostic FP candidates** : 1 seule FP intracom dispo cote Teatower = `account.fiscal.position` id=**3 "Intra-Community"** (`country_group_id=European Union`, `country_id=False`, `vat_required=True`, `auto_apply=True`). Mapping verifie : tax 8 (6% BE Goods) -> tax 13 (0% EU M Intra-Community Goods). Choix evident — la FP couvre tout l'UE B2B avec VAT requis.
- **Etat AVANT** : FP=3 deja set sur la SO mais 72 lignes encore `tax_id=[8]` (recompute jamais tourne). `amount_untaxed=2571.48`, `amount_tax=154.33`, `amount_total=2725.81`. Partner 123449 : `property_account_position_id=False`.
- **ACTION 1 — Recompute taxes** : appel `sale.order.action_update_taxes([8404])` -> les 72 lignes mappees `tax_id=[8]` → `tax_id=[13]` ✓. **MAIS** je rappelle aussi `action_update_prices` par erreur -> recompute pricelist standard, prix unitaires passent des tarifs Vente-Privee (4.55/4.93/5.00) aux tarifs B2B Odoo defaut (9.434/10.3774). amount_untaxed grimpe a 5798.41.
- **ACTION 2 — Restore prix originaux** : recupere XLSX source via `ir.attachment` id=79084 (`TEATOWE1.231645...xlsx`) attache au SO. Mapping default_code -> price (col "External reference" / "Unit price" du XLSX). 72/72 lignes matchees, 0 unmatched. `sale.order.line.write({'price_unit': new})` sur 72 lignes -> 0 erreur.
- **ACTION 3 — Set FP sur partner** : `property_account_position_id=3` ecrit sur `res.partner` 123449 (parent VENTE-PRIVEE.COM), 123479 (Sarah Walschap, contact facturation), 123480 (Beaune, contact livraison). Toutes futures SO de ce client partiront directement avec la FP intracom.
- **Etat APRES (final)** :
  - FP S05534 = `[3, 'Intra-Community']` ✓
  - 72/72 lignes `tax_id=[13]` (0% EU Intra-Community Goods) ✓
  - `amount_untaxed=2571.48`, `amount_tax=0.00`, `amount_total=2571.48` ✓ (= total source XLSX exact)
  - Partner 123449 / 123479 / 123480 : `property_account_position_id=[3, Intra-Community]` ✓
- **Lesson learned** : sur `action_update_taxes` ca passe en XML-RPC bien que l'erreur `cannot marshal None` apparaisse (la methode renvoie `None`). Ne **JAMAIS** appeler `action_update_prices` ensuite si la SO a des prix negocies — il recompute la pricelist par defaut. Pour seulement re-mapper les taxes, `action_update_taxes` suffit.
- **URL SO** : https://tea-tree.odoo.com/odoo/sales/8404

## 2026-05-05 — Creation PO Marketing Teatower P00523 (S05534 Carrefour 231645)

- **Demande Nicolas** : creer un PO interne pour reception du stock cote marketing, lie au devis client S05534 (Carrefour 231645). 56 lignes, 362 unites, codes V0/I0/C0.
- **Partner** : 24 partners "Marketing Teatower" trouves, aucun avec supplier_rank>0. Fallback : partner company exact id=3127 "Marketing Teatower" (les 23 autres = sous-contacts personnes physiques `Marketing Teatower, Prenom Nom`).
- **Mapping produits** : 56/56 codes default_code mappes vers product.product, 0 unmapped.
- **PO cree** : `purchase.order` id=527, name=**P00523**, draft -> confirm -> state=`purchase`. amount_total=764.07 EUR (prix d'achat Odoo par defaut, taxes_id=[]).
- **Picking de reception genere** : id=42526, name=**TT/IN/00752**, state=`assigned`, dest=TT/Entree (loc id=9).
- **URLs** :
  - PO : https://tea-tree.odoo.com/odoo/purchase/527
  - Picking : https://tea-tree.odoo.com/odoo/action-stock.action_picking_tree_all/42526
- **Origin** : `S05534 - Carrefour 231645 (PO marketing)`.
- **Script** : `_create_po_marketing.py` + source `_po_marketing_lines.json`.

## 2026-04-29 — Push Shopify 5 GI0 a 9,50 EUR TTC (manual_update_product_to_shopify)

- **Demande Nicolas** : 5 thes glaces GI0634/0735/0820/0911/0912 toujours a 8,50 sur teatower.com alors qu'il les avait demandes a 9,50 TTC. Corriger a la source Odoo, eviter qu'un sync ecrase Shopify.
- **Diagnostic** :
  - Pricelist e-commerce identifiee = `id=3 "Odoo x Shopify PriceList (EUR)"` (champ `shopify_pricelist_id` sur `shopify.instance.ept` id=1 "Odoo x Shopify").
  - TVA 6% (denree alimentaire), `price_include=false` -> list_price en HT.
  - `list_price` template = 8.9623 EUR HT (= 9.50 TTC) sur les 5 produits -> deja coherent.
  - Items pricelist 3 deja a `fixed_price=9.5` (write_date 14:19, suite a l'update du log 9/9 plus haut). **Cote Odoo : rien a corriger.**
- **Cause racine** : pas de re-export automatique vers Shopify apres update pricelist -> les variants Shopify gardaient l'ancien prix 8,50 jusqu'au prochain push manuel.
- **Action** : declenchement du wizard `shopify.process.import.export.manual_update_product_to_shopify`
  - wizard id=64, `shopify_is_set_price=True` (basic_detail / image / publish = False).
  - `active_ids = [75,76,77,79,80]` sur `shopify.product.template.ept`.
  - Resultat : `True`, write_date des 5 templates passe a 15:06:47 -> push API Shopify confirme.
- **Mapping produits** (ID Odoo / SKU / shopify_template_id / pricelist_item / fixed_price avant -> apres) :
  - 4571 GI0634 Gourmandise / sh#75 / item#112 / 8.50 -> 9.50 (avant mission Nicolas), 9.50 -> 9.50 (push Shopify aujourd'hui)
  - 4572 GI0735 Peche de Vigne BIO / sh#79 / item#116 / idem
  - 4574 GI0820 Marrakech Sunset BIO / sh#80 / item#117 / idem
  - 7062 GI0911 Paradise Punch / sh#76 / item#113 / idem
  - 7061 GI0912 Passion Exotique / sh#77 / item#114 / idem
- **Sync auto** : crons Shopify actifs (`Process Products Queue`, `Process Export Stock Queue`) tournent toutes les ~5-15 min. Le push manuel a ete fait, donc les 9,50 sont deja en ligne.
- **A verifier cote Nicolas** : ouvrir teatower.com (cache navigateur a vider) sur les 5 fiches produit, confirmer l'affichage 9,50 EUR.

## 2026-04-29 — Pricelist Shopify : aligner 9 GI0 thes glaces a 9,50 EUR

- **Demande Nicolas** : tous les GI0xxx (thes glaces) doivent afficher 9,50 EUR TTC sur teatower.com. GI0916 deja corrige (29/04 11h33), 9 autres encore a 8,50 sur la pricelist 3 "Odoo x Shopify PriceList".
- **Diagnostic HT/TTC** : sur GI0916 ref, `list_price` Odoo = 8.9623 (HT, TVA 6% non incluse) -> ×1.06 = 9.50 TTC. Le `fixed_price` pricelist = 9.50 matche le TTC affiche cote Shopify. Decision : ecrire 9.50 (meme valeur que GI0916 deja ok).
- **Updates fixed_price 8.50 -> 9.50** (pricelist_id=3, applied_on=variant) :
  - item 111 GI0868, 112 GI0634, 113 GI0911, 114 GI0912, 115 GI0847, 116 GI0735, 117 GI0820, 330 GI0832, 331 GI0880 -> **9/9 OK**.
- **7 SKUs absents de la pricelist verifies** (GI0617, GI0813, GI0821, GI0822, GI0826, GI0848, GI0917) :
  - Tous actifs dans Odoo, taxe 6%, mais **aucun n'est exporte sur Shopify** (table `shopify.product.template.ept` : 0 record pour ces tmpl_id, alors que GI0916 ref y figure avec `exported_in_shopify=True`).
  - Decision : **ne pas creer de pricelist_item** -> inutile tant que Shopify ne les connait pas. A signaler a Nicolas s'il faut les publier.
- **Sanity finale** : 10 items GI0 sur la pricelist 3 = tous a 9.50.
- **Propagation Shopify** : attendre prochain cron "Shopify: Process Products Queue" (~10 min).

## 2026-04-27 — Fix route Buy -> Manufacture sur 249 OP I0/V0 avec BoM active

- **Demande Nicolas** : GO pour appliquer le fix planifie dans l'audit precedent (249 OP TT/Stock I0/V0 avec BoM active mais route Buy par erreur, suite au script `11_restore_buy_route.py` du 23/04 qui n'avait pas verifie la presence de BoM).
- **Cause racine** : `11_restore_buy_route.py` se contentait de checker `seller_ids` -> Buy. Or 249 produits I0/V0 ont a la fois un vendor (composants) ET une BoM active (assembles en interne) -> la route correcte est Manufacture, pas Buy.
- **Fix Odoo** : `odoo/route_fix_20260423/12_fix_buy_to_manufacture.py`
  - Lecture des 249 OP IDs depuis `i0v0_buy_with_bom_TO_FIX.json`.
  - Resolution route Manufacture : `stock.route` id=6.
  - `write({route_id: 6})` par chunks de 100 : 100 + 100 + 49 = **249/249 OK, 0 erreur**.
- **Sanity post-fix** :
  - Verif directe : 249/249 OP ont bien `route_id=Manufacture` (id=6).
  - Query d'audit complete (OP TT/Stock + I0/V0 + BoM active + route=Buy) : **0 ligne** (attendu 0). Verdict OK.
  - Reste 128 OP TT/Stock I0/V0 sur Buy mais sans BoM active = legitimes (achats purs).
- **Patch script** `11_restore_buy_route.py` :
  - Ajout `ROUTE_MANUFACTURE = 6`.
  - STEP 2 : query `mrp.bom` actives sur les `tpl_ids` -> set `tpls_with_bom`.
  - Logique split : si BoM active -> Manufacture (priorite, meme si vendor present), sinon si vendor -> Buy, sinon arbitrage.
  - STEP 3 dedouble en 3a (write Manufacture) + 3b (write Buy).
  - Commentaire d'audit ajoute en docstring + au-dessus du nouveau bloc.
  - Validation : `python -m py_compile` OK.
- **Rapport** : `odoo/route_fix_20260423/12_fix_report.json`.

## 2026-04-23 (apres-midi v2) — Restauration route Buy sur 256 OP TT + rapports arbitrage

- **Demande Nicolas** : appliquer `11_restore_buy_route.py` pour remettre route Buy sur les OP TT orphelins et produire les 2 rapports d'arbitrage.
- **Script** : `odoo/route_fix_20260423/11_restore_buy_route.py` (idempotent, chunk de 100).
- **Resultats** :
  - OP TT sans route au depart : **298** (match LOG precedent).
  - **256** OP avec `seller_ids` → `write({route_id: 5})` : 256/256 OK, 0 erreur, verif remaining=0.
  - **42** OP sans vendor → `odoo/route_fix_20260423/42_no_vendor.md` pour arbitrage (A: add seller_ids + Buy, B: unlink OP, C: laisser False).
  - **45** MO `state=confirmed` pre-fix → `odoo/route_fix_20260423/45_confirmed_mo_pre_fix.md` (dont TT/MO/04126 du 21/04 Blue Earl Grey BIO, 17 autres MO recents + MO plus anciennes 2026-03-27 → 2026-04-21).
- **Sanity (`10_daily_sanity.py`) APRES fix** : **GREEN** (0 alerte).
  - `n_tpl_mfg=1` (C0200 only ✓), `n_ops_mfg=0` ✓, `n_recent_mo_24h=0` ✓, `wh_tt_routes=[29,2,3]` ✓ (pas de 6), `route_buy_active=True` ✓.
- **Rapports** : `odoo/route_fix_20260423/11_restore_report.json` (raw data OP + MO), `42_no_vendor.md`, `45_confirmed_mo_pre_fix.md`.
- **Next arbitrage Nicolas** :
  - 42 OP sans vendor → decider par produit (ajouter fournisseur, supprimer OP, ou laisser).
  - 45 MO confirmed → cancel/unlink en masse si aucune raw done, ou garder les legit (C0200).

## 2026-04-23 (apres-midi) — Diagnostic "200+ OP supprimes" : en realite 199 MO annulees, 0 OP supprime

- **Question Nicolas** : "j'ai supprime 200+ orderpoints ce matin, toi tu n'en as trouve que 6, ou est le gap ?"
- **Verification faite** :
  - `mail.message` modele=orderpoint auteur=Nicolas aujourd'hui : **0**
  - OP crees aujourd'hui : **0** | OP modifies aujourd'hui : **31** (dont 6 modifs Nicolas a 08:29, set `route_id=False` sur GI0735/GI0820/GI0832/GI0634/GI0912/GI0916 — pas des suppressions)
  - Gaps dans la sequence OP/xxxxx : le gros gap 35158->35379 (220 manquants) date du 2025-11-04/05, **pas d'aujourd'hui**
  - Max OP/35572, sequence.next=35573 : pas de creation aujourd'hui
- **Trouvaille reelle** : `mrp.production` `state=cancel` `write_date >= 2026-04-23` = **199 MO cancelled** (198 par user 10 logistique@noenature.com a 06:xx = scheduler batch, 1 par Nicolas a 07:xx).
- **Conclusion** : Nicolas a confondu "MO cancelled" avec "OP supprimes". Il a utilise l'action de masse "Cancel" sur la vue Manufacturing, pas sur Orderpoints. Aucun OP n'a ete supprime par lui.
- **Cascade expliquee** :
  - Le 21/04 la route Manufacture etait encore rattachee au WH TT -> scheduler a genere des MO sur 198 OP differents (origin OP/xxxxx)
  - Mon fix b592d25 ce matin a nettoye la config (route Buy reactivee + Manufacture decrochee du WH + 17 MO residuels), mais laissait 198 MO deja confirmed avant mon passage que le scheduler ne pouvait plus reconduire.
  - Nicolas a cancelled en masse ces 199 MO "fantomes" via l'UI (action correcte, aucun dommage collateral).
- **Etat final verifie** :
  - Les 198 OP referenced dans les origins existent TOUJOURS en base (aucun supprime)
  - 80 ont route=Buy (OK, scheduler les reprendra normalement), **118 ont route=False** -> scheduler ne fera rien pour eux
  - Zoom TT : **298 OP sans route** dont 256 produits avec `seller_ids` (devraient etre Buy) et 42 sans vendor
  - MO encore `confirmed` en base : **45** (creees entre 2026-03-27 et 2026-04-21, pre-fix) -> a passer en revue avec Nicolas
- **Action recommandee** : script batch pour remettre `route_id=Buy` sur les 256 OP TT NO_ROUTE avec seller_ids. Les 42 sans seller_ids : a purger ou assigner un fournisseur d'abord. Les 45 MO confirmed pre-fix : 1 MO recent 21/04 (TT/MO/04126 Blue Earl Grey BIO) -> a cancel. Les autres sont vieilles (mars), Nicolas doit arbitrer au cas par cas.
- **Files** : diag pas de script persiste (ad-hoc `/tmp/trace_op*.py`). Prochain step = script `odoo/route_fix_20260423/11_restore_buy_route.py` sur demande de Nicolas.

## 2026-04-23 — Route Buy reactivee + Manufacture isolee C0200 + 17 MO residuels nettoyes

- **Symptome** (Nicolas 23/04 matin) : produits basculent en "Fabriquer" au lieu de "Acheter", plus dans les achats mais dans les MO. Supprimait des MO a la main depuis le module Manufacturing.
- **Cause racine DECOUVERTE** :
  - **Route Buy (id=5) etait DESACTIVEE** (+ ses 8 rules inactives : 7, 21, 33, 44, 55, 67, 79, 97). Aucune trace mail.message sur qui/quand → desactivee avant mise en place du tracking, probablement en meme temps que le decroche Manufacture du 21/04.
  - **Warehouse TT (id=1) avait `route_ids=[29, 2, 3, 6]`** : la route Manufacture (6) etait rattachee au WH, donc **tous les produits du WH TT la voyaient**, meme sans l'avoir sur template/categ.
  - Consequence : scheduler 07:23-07:55 → 17 MO creees (draft/confirmed) ce matin sur des thes (I0xxx, V0xxx, GI0xxx) qui devraient etre achetes.
  - Les 6 orderpoints glaces (OP/13672, 13673, 13674, 14047, 14328, 35571) avaient aussi `route_id=6` explicite (pas nettoyes par le run du 21/04).
- **Actions** (scripts dans `odoo/route_fix_20260423/`) :
  1. `07_execute.py STEP 1` : reactive route Buy + 8 rules → `active=True` ✓
  2. `07_execute.py STEP 2` : retire route 6 de `warehouse.TT.route_ids` → `[29, 2, 3]` ✓
  3. `07_execute.py STEP 3` : `route_id=False` sur 6 orderpoints glaces ✓
  4. `07_execute.py STEP 4` : cancel + unlink 17 MO draft/confirmed (raw_done=0, 0 erreur) ✓
  5. `09_harden.py` : sequence Buy rules = 10, Manufacture = 30 → Buy prioritaire si jamais un WH mal configure.
- **Final check** :
  - `product.template` route=6 : **1** (C0200 ✓)
  - `stock.warehouse.orderpoint` route=6 : **0**
  - `stock.warehouse.TT.route_ids` = [29, 2, 3] ✓
  - `stock.route` Buy active=True ✓ | Manufacture rules sequence=30 ✓
  - 4 MO `state=done` de C0200/I0600/GI0634/GI0820/GI0912 preservees (validees par Nicolas, pas du flood).
- **Garde-fou cree** : `odoo/route_fix_20260423/10_daily_sanity.py` → detecte 5 anomalies (Buy inactive, WH TT contient MFG, tpl hors whitelist C0200, OP MFG hors whitelist, MO recent sans BoM active). A brancher en GitHub Action cron quotidien.
- **Rapports** : `odoo/route_fix_20260423/execute_report.json`, `plan.json`, `diag_wide.json`.

## 2026-04-21 — Flood MO : unlink final des 194 MO cancel (nettoyage base)
- **Contexte** : suite action 1 (commit e1560ee, 194 MO passes en `cancel`), Nicolas demande suppression definitive.
- **Garde-fous pre-unlink** (script `odoo/_unlink_mo_flood.py`) :
  - Count flood `state=cancel` + `create_date >= 2026-04-21 12:00:00` = **194** (match exact).
  - `stock.move` raw avec `state=done` liees : **0**.
  - `stock.move` finished avec `state=done` liees : **0**.
  - MO lies a SO active via `procurement_group_id` : **0** (aucun warning).
- **Unlink** : batch de 50 → 50 / 50 / 50 / 44 = **194/194 OK, 0 erreur**.
- **Post-verif** :
  - `mrp.production.search_count([('state','=','cancel'),('create_date','>=','2026-04-21 12:00:00')])` = **0**.
  - `mrp.production.search_count([('create_date','>=','2026-04-21 12:00:00')])` = **0** (aucun MO du jour, les 2 MO de 12:49 etaient tous dans le flood).
- **Rapport** : `odoo/_unlink_mo_flood_report.json`.
- **Statut final** : base 100% nettoyee du flood. Aucun residu MO flood. Anti-recidive (route 6 detachee + OP route_id=False) toujours en place.

## 2026-04-21 — Flood MO corrige : 194 MO annules + route Manufacture isolee C0200 + OP nettoyes

- **Contexte** : reactivation route Manufacture (id=6) avant 14:29 → cron scheduler a généré 194 `mrp.production` draft/confirmed sur 194 produits (pas uniquement C0200).
- **Cause racine** : 687 `product.template` portaient `route_ids=[6]` + 293 `stock.warehouse.orderpoint` avaient `route_id=6` hors C0200.
- **ACTION 1 — Annulation MO** : `_cancel_mo_flood.py --execute` → 194/194 cancel, 0 échec, 0 raw move done (garde-fou OK).
- **ACTION 2 — Détachement route 6** : `_remove_manufacture_route.py` → 686/686 templates nettoyés (write `(3,6)`), 0 échec. Reste 1 seul template avec route 6 = **10485 (C0200)**.
- **ACTION 3 — Vérifs** :
  - Route 6 `Manufacture` toujours `active=True` (gardée pour C0200).
  - C0200 (10485) : `route_ids=[6]` ✓.
  - Echantillon 5 random (GI0735, V0607, E0888, E0280, V0847) : route 6 absente ✓.
  - MO après 12:00 : total=194, cancel=194, draft/confirmed/progress/to_close/done=0 ✓.
- **ACTION 4 — Anti-récidive OP** : `_clean_orderpoints_route6.py` → 293 OP avec `route_id=6` (0 sur C0200) passés à `route_id=False`. Post-vérif = 0 OP avec route 6.
- **Scripts** : `odoo/_cancel_mo_flood.py`, `odoo/_remove_manufacture_route.py`, `odoo/_clean_orderpoints_route6.py`, `odoo/_final_check_mo_flood.py`.
- **Garantie** : scheduler demain 14:29 ne peut plus re-flooder — aucun OP n'a plus la route Manufacture assignée, et aucun template hors C0200 ne porte la route.

## 2026-04-21 — Torrefactory Part 2 : TF005/TF010 + images 10 refs
- **Mission 1** : creation des 2 refs Colombie manquantes (feuille "Gamme Bio" BDC 2026 Torrefactory).
  - TF005 Cafe Colombie Bio - Grain 500 gr : tmpl=**10494**, product=**7742**, supplierinfo=**1934** (PA 11.48, PVC 15.94, carton 9).
  - TF010 Cafe Colombie Bio - Moulu 250 gr : tmpl=**10495**, product=**7743**, supplierinfo=**1935** (PA 6.08, PVC 8.44, carton 12).
  - Meme template que les 8 existants : categ_id=104 "All / Cafe", type=consu, is_storable=True, taxes=[8] (6% sale), supplier_taxes=[18] (6% M purchase), UoM=1, description_purchase "BDC 2026 Bio + Certisys + franco 250 EUR".
- **Mission 2** : scraping og:image Torrefactory + upload image_1920 sur les 10 `product.template`.
  - 6 URLs scrapees (og:image cdn.shopify), toutes renvoient un PNG 490-535 KB.
  - 10/10 templates OK, 0 erreur. Tailles stockees :

| Code | tmpl | KB | URL source |
|---|---|---|---|
| TF001 | 10486 | 490.4 | /files/ethiopia-bio-cafe-torrefactory.png |
| TF002 | 10487 | 519.7 | /files/CafeengrainsBrazil.png |
| TF003 | 10488 | 496.5 | /files/CafeengrainsCostaRica.png |
| TF004 | 10489 | 491.0 | /files/Cafeengrainsespressobio.png |
| TF005 | 10494 | 523.4 | /files/CafeengrainsColombie.png |
| TF006 | 10490 | 535.0 | /files/Decafactory_1.png |
| TF007 | 10491 | 490.4 | /files/ethiopia-bio-cafe-torrefactory.png |
| TF008 | 10492 | 519.7 | /files/CafeengrainsBrazil.png |
| TF009 | 10493 | 496.5 | /files/CafeengrainsCostaRica.png |
| TF010 | 10495 | 523.4 | /files/CafeengrainsColombie.png |

- Choix notables :
  - Image partagee entre grain 500g et moulu 250g de meme origine (pas de visuel dedie moulu sur Torrefactory, assume OK — meme packaging pictural).
  - og:image servi en HTTP par Shopify CDN, pas besoin de fallback twitter:image.
  - Pas de `ir.attachment` separe : ecriture directe base64 sur `product.template.image_1920` (Odoo regenere auto image_128/512/1024).
- Scripts : `odoo/_create_torrefactory_part2.py`, `odoo/_verify_torrefactory_images.py`. Report : `odoo/_tmp_report_torrefactory_part2.json`.

## 2026-04-21 — Creation 8 refs cafe Torrefactory (BDC 2026 Conventionnel)
- Fournisseur **The Torrefactory Project Sa** (res.partner id=3260, VAT BE0679686720) : `supplier_rank` passé 0 → 1 pour le rendre selectionnable sur supplierinfo.
- Nouvelle `product.category` "Cafe" id=**104** sous All (parent_id=1), au meme niveau que "The Noir", "The Vert", "Rooibos", "Mate".
- 8 `product.template` creés avec `type='consu'`, `is_storable=True`, `taxes_id=[8]` (6% sale), `supplier_taxes_id=[18]` (6% M purchase), UoM=Units, categorie Cafe, `description_purchase` mentionnant BDC 2026 + Certisys BE-BIO-01 + cartonnage + franco 250 EUR.
- Chaque produit a 1 `product.supplierinfo` lié a Torrefactory #3260 (price=PA HTVA, product_code=TF00X, min_qty=carton).

| Code | Nom | tmpl | product | supplierinfo | PA | PVC | Carton |
|---|---|---|---|---|---|---|---|
| TF001 | Cafe Ethiopie Bio - Grain 500 gr | 10486 | 7734 | 1926 | 12.57 | 17.45 | 9 |
| TF002 | Cafe Bresil - Grain 500 gr | 10487 | 7735 | 1927 | 10.80 | 15.00 | 9 |
| TF003 | Cafe Costa Rica - Grain 500 gr | 10488 | 7736 | 1928 | 11.48 | 15.94 | 9 |
| TF004 | Cafe Espresso Bio - Grain 500 gr | 10489 | 7737 | 1929 | 11.48 | 15.94 | 9 |
| TF006 | Cafe Decafactory (decafeine) - Grain 500 gr | 10490 | 7738 | 1930 | 12.84 | 17.83 | 9 |
| TF007 | Cafe Ethiopie Bio - Moulu 250 gr | 10491 | 7739 | 1931 | 6.42 | 8.92 | 12 |
| TF008 | Cafe Bresil - Moulu 250 gr | 10492 | 7740 | 1932 | 5.74 | 7.97 | 12 |
| TF009 | Cafe Costa Rica - Moulu 250 gr | 10493 | 7741 | 1933 | 6.08 | 8.44 | 12 |

- **Codes reservés non créés** : TF005 (Colombie grain) + TF010 (Colombie moulu) — absents du BDC Torrefactory, Nicolas doit clarifier.
- Scripts : `odoo/_tmp_create_torrefactory.py`, report JSON : `odoo/_tmp_report_torrefactory.json`.
- Choix notables :
  - Categorie "Cafe" placée sous All (pas sous "All / Saleable") pour coherence avec les categories thé existantes.
  - `min_qty` du supplierinfo = cartonnage Torrefactory (9 pour grain 500g, 12 pour moulu 250g) plutot que 1 → aligne les commandes sur la realité fournisseur.
  - Taxes 6% confirmées (convention Teatower denrees alimentaires BE), UoM=Units.
- **Point d'attention** : pas encore de `delay` (lead time fournisseur) ni de franco port configurés sur partner #3260 — a MAJ apres 1ere commande réelle.

## 2026-04-21 — Diag route Fabriquer absente (C0200)
- Produit C0200 "Coffret assortiment Matcha" (product.product id=7733, template id=10485, type=consu, is_storable=true, catégorie "Coffret" id=65).
- BoM existante : mrp.bom id=7681, type=normal, actif, lié au template.
- Orderpoint existant : id=18791 TT/Stock min=50 max=100, route_id=false.
- Module `mrp` installé.
- **Aucune route Manufacture/Fabriquer en base** : `stock.route` ne contient que des routes inter-entrepôts (Réappro GMS/WAT/LIEGE/NAM/POP-UP, etc.). Aucune `stock.rule` avec action='manufacture'.
- Catégorie "Coffret" : route_ids=[], total_route_ids=[].
- Cause racine : la route standard "Manufacture" fournie par le module MRP n'existe pas ou a été supprimée/désactivée → impossible à sélectionner sur orderpoint.

## 2026-04-21 — Réactivation route Manufacture + attache C0200
- Diagnostic corrigé (active_test=False) : la route `stock.route` id=6 "Manufacture" existait en base mais **archivée** (active=False, product_selectable=True). 8 `stock.rule` action='manufacture' aussi archivées (WH id=8, GMS id=18, LIEGE id=30, WAT id=41, NAM id=52, COPIE-POP id=64, COPIE-Sales id=76, OPA id=94) toutes liées à route_id=6.
- **Option A retenue** : simple `write {'active': True}` (pas d'upgrade du module mrp nécessaire, pas de création manuelle).
- Actions :
  - `stock.route` id=6 : `active=True`, `product_selectable=True` confirmés.
  - `stock.rule` ids [8, 18, 30, 41, 52, 64, 76, 94] : tous réactivés `active=True`.
  - `product.template` id=10485 (C0200) : `route_ids=[(4, 6)]` → route Manufacture cochée (auparavant route_ids=[]).
  - `product.product` id=7733 hérite bien route_ids=[6].
- Vérif finale : orderpoint 18791 (TT/Stock, min=50, max=100) a toujours route_id=false (sélection UI à faire par Nicolas), mais la route Manufacture est maintenant proposable dans le menu.
- Scripts : `odoo/_reactivate_manufacture_route.py` (diag), `odoo/_reactivate_manufacture_route_step2.py` (réactivation). Snapshot JSON : `odoo/_manufacture_route_diag.json`.
- Next user action : dans Odoo UI, ouvrir l'orderpoint OP/35570, sélectionner "Manufacture" dans le champ Route, sauver. Puis Run Scheduler (ou bouton "Order" sur l'orderpoint) pour générer le Manufacturing Order.


## 2026-04-21 — URGENT : Flood MO suite réactivation route Manufacture
- **Cause** : cron `Procurement: run scheduler` (ir.cron id=32) a tourné à 14:30:05 (lastcall), juste après la réactivation route Manufacture + 8 stock.rule (commit d67ef22). Trigger mass-procurement sur tous les orderpoints dont `qty_available < product_min_qty` avec route Manufacture héritée.
- **Volume** : **194 MO créés** aujourd'hui (192 produits distincts), tous entre 14:29:38 et 14:29:53 (2 autres à 12:49 pré-existants). Qty totale cumulée = **9829 unités**.
- **State** : 100% en `confirmed` (194/194). 0 en progress/done. 0 raw_move consommé (`stock.move` state=done lié à ces MO = 0). 🟢 Entièrement récupérable.
- **Origine** : 100% `orderpoint_id` renseigné, origin `OP/...`. Confirme bien scheduler orderpoint, aucune action utilisateur/SO en cause.
- **Périmètre routes** :
  - 293 orderpoints pointent route_id=6 (Manufacture).
  - 687 `product.template` ont route Manufacture cochée (héritage batch probable — à investiguer).
  - 0 `product.category` avec route Manufacture directe.
- **Script d'annulation préparé** : `odoo/_cancel_mo_flood.py` (dry-run par défaut, `--execute` pour lancer). Cible stricte : `state in (draft,confirmed) AND create_date >= 2026-04-21 12:00:00` → 194 MO. Vérif anti-casse : bloque si un seul raw move done détecté.
- **En attente validation Nicolas pour exécution.**
- Diag snapshot : `odoo/_mo_flood_diag.json`. Scripts : `odoo/_diag_mo_flood.py`, `odoo/_mo_flood_extra.py`, `odoo/_cancel_mo_flood.py`.
- **Next cron** : 2026-04-22 14:29:39 → si on n'a pas retiré la route Manufacture des 687 produits / 293 orderpoints d'ici là, le flood reviendra. Piste : soit désactiver le cron temporairement, soit retirer route_ids=6 des templates non concernés (garder uniquement C0200 id=10485 qui était la cible initiale).
