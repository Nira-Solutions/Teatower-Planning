
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

