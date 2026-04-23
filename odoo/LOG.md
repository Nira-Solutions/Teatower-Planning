
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
