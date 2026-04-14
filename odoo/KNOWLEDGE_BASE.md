# KNOWLEDGE_BASE — Agent Odoo Teatower

> Base de référence personnelle construite à partir de la doc officielle Odoo 18 FR (https://www.odoo.com/documentation/18.0/fr/).
> Objectif : relire ce fichier en début de session pour savoir **où chercher l'info officielle** avant de toucher à la base Teatower (tea-tree.odoo.com, DB `tsc-be-tea-tree-main-18515272`).
> Règle d'or : avant toute modif critique, ouvrir l'URL de la section concernée, vérifier le vocabulaire technique (nom de modèle, nom de champ), puis agir.

---

## 1. Inventaire / Stock

### Concepts clés
- **Warehouse** (`stock.warehouse`) : entrepôt logique. Chaque warehouse a un code (ex : `WH`, `TT`, `WAT`, `LIE`, `NAM`). Chez nous, chaque magasin GMS servi via réassort est un warehouse ou une location enfant.
- **Location** (`stock.location`) : arborescence physique/virtuelle. Types : `internal`, `view`, `transit`, `customer`, `supplier`, `inventory` (loss), `production`. Les types `customer`/`supplier`/`production`/`inventory` sont **virtuels** — ils permettent l'équilibre de la double-écriture stock.
- **Route + Rule** (`stock.route`, `stock.rule`) : la route décrit un chemin ; chaque règle (push/pull) déclenche un `stock.move` entre deux locations. La combinaison routes produit/warehouse explique les flux 1/2/3-steps.
- **Picking 1-step / 2-step / 3-step** : 1 = vendor→stock ou stock→customer direct ; 2 = ajout input/output ; 3 = quality check et packing. Ne pas confondre avec le module Quality (qui fonctionne indépendamment).
- **Orderpoint** (`stock.warehouse.orderpoint`) : règle de réapprovisionnement min/max par (product, location). Déclenche RFQ ou MO selon la route configurée sur le produit (`buy` / `manufacture`).
- **Reservation methods** (par `stock.picking.type`) : `at_confirm`, `manual`, `by_date`. Impacte `stock.move.reserved_availability` et les `stock.quant.reserved_quantity`.
- **Allow Negative Stock** : au niveau de la category produit (`property_valuation` + option sur `product.category`). Permet les mouvements sortants quand le stock théorique est négatif. À manier avec précaution (valorisation faussée).

### Modèles Odoo impliqués
- `stock.warehouse` — champs : `code`, `lot_stock_id`, `in_type_id`, `out_type_id`, `reception_steps`, `delivery_steps`.
- `stock.location` — `usage`, `location_id` (parent), `company_id`, `removal_strategy_id`, `cyclic_inventory_frequency`.
- `stock.picking` / `stock.move` / `stock.move.line` — `location_id`, `location_dest_id`, `product_uom_qty`, `quantity_done`, `state` (`draft`→`confirmed`→`assigned`→`done`/`cancel`), `priority`.
- `stock.quant` — `product_id`, `location_id`, `quantity`, `reserved_quantity`, `inventory_quantity` (comptage), `inventory_diff_quantity`.
- `stock.warehouse.orderpoint` — `product_id`, `location_id`, `product_min_qty`, `product_max_qty`, `qty_multiple`, `trigger` (`auto`/`manual`), `route_id`, `qty_to_order`.
- `stock.route` / `stock.rule` — `action` (`push`/`pull`/`pull_push`), `procure_method` (`make_to_stock`/`make_to_order`), `location_src_id`, `location_dest_id`.

### Pièges / gotchas
- Un orderpoint se déclenche sur le **stock prévisionnel** (forecasted = on-hand + incoming − outgoing), pas sur on-hand seul. Une commande client récente peut faire rouvrir une orderpoint alors que le stock réel paraît OK.
- Règle spéciale **0/0/1** (min=0, max=0, to_order=1) = MTO sans réservation — utile pour les kits à la commande.
- Le champ `qty_multiple` arrondit la qty commandée vers le haut (ex : multiple=12, besoin 15 → commande 24).
- MPS et orderpoints auto **ne doivent pas coexister** sur les mêmes produits (MPS = workflow manuel).
- `stock.quant.inventory_quantity` ne modifie rien tant que `action_apply_inventory()` n'a pas été appelé.
- Les types `customer`/`supplier` sont virtuels — un produit "livré" vit techniquement dans la location `Partners/Customers`. C'est normal.
- Un picking avec `state='done'` est figé : pour corriger il faut un **return** (`stock.return.picking`), pas un `write` sur move.line.

### Doc officielle
- Inventaire overview : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory.html
- Orderpoints : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/reordering_rules.html
- Replenishment (vue d'ensemble) : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment.html
- Daily operations / flux 1-2-3 steps : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/shipping_receiving/daily_operations.html
- Locations : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/use_locations.html
- Inventaire physique : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.html
- Reservation methods : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/shipping_receiving/reservation_methods.html
- Valorisation : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/using_inventory_valuation.html

### Applicabilité Teatower
- **1716 orderpoints** min/max (produit × magasin GMS). WAT 363, LIEGE 378, NAM 370… Formule maison : `min = ventes/semaine × 2`, `max = ventes/semaine × 2.5`, uniquement pour SKU `I0xxx` et `V0xxx`. Voir `project_orderpoints_magasins.md`.
- **Réassort magasin** = `stock.picking` TT/Stock → WAT/Stock avec `priority=1` (étoile logistique). Voir `feedback_transferts_internes.md`.
- **Routes GMS/Stock** configurées par magasin — toujours vérifier `route_ids` sur le produit avant de créer une orderpoint.
- Audits récents : `odoo/audit_stocks_negatifs_2026-04-14.md`, `odoo/inventaire_ttstock_*.md` — pattern : checker `stock.quant` par location TT/Stock pour traquer les négatifs.

---

## 2. Ventes / Sale

### Concepts clés
- **Devis → commande → facture** : `sale.order` en `draft` devient `sale` à la confirmation, crée les `stock.picking` et `account.move` selon `invoice_policy` du produit (`order` ou `delivery`).
- **Partenaire invoice vs shipping** : `partner_id` (client commercial), `partner_invoice_id` (facturation), `partner_shipping_id` (livraison). **Trois peuvent être différents** — crucial pour GMS franchisés AD.
- **Pricelist** (`product.pricelist`) : règles multi-niveaux (discount/formula/fixed), filtrables par pays, période, min_quantity. La "default pricelist" est la première sans country group.
- **Mode de livraison** (`delivery.carrier`) : ligne de frais automatique à la confirmation (`sale.order.carrier_id`).
- **Remises** : `discount` sur la ligne, ou remise globale via pricelist, ou section "discount" sur l'order.

### Modèles impliqués
- `sale.order` — `partner_id`, `partner_invoice_id`, `partner_shipping_id`, `pricelist_id`, `payment_term_id`, `carrier_id`, `state`, `client_order_ref`, `team_id`, `user_id`, `warehouse_id`.
- `sale.order.line` — `product_id`, `product_uom_qty`, `price_unit`, `discount`, `tax_id`, `route_id`, `qty_delivered`, `qty_invoiced`.
- `product.pricelist` / `product.pricelist.item` — `applied_on`, `compute_price`, `fixed_price`, `percent_price`, `date_start`/`date_end`, `min_quantity`.

### Pièges / gotchas
- `price_unit` sur la ligne est **cached** : un changement de pricelist ne met PAS à jour les lignes déjà créées. Appeler `action_update_prices()`.
- Les remises "Formula" sont invisibles client ; les "Discount" sont affichées sur le devis PDF.
- La conversion devis→commande crée autant de pickings que de routes distinctes sur les lignes.
- `client_order_ref` = notre champ pour les bons de commande clients (GMS).
- Un `sale.order` annulé (`state='cancel'`) ne peut pas être réactivé proprement — mieux vaut dupliquer.

### Doc
- Ventes overview : https://www.odoo.com/documentation/18.0/fr/applications/sales/sales.html
- Pricelists : https://www.odoo.com/documentation/18.0/fr/applications/sales/sales/products_prices/prices/pricing.html
- Amazon Connector : https://www.odoo.com/documentation/18.0/fr/applications/sales/sales/amazon_connector.html

### Applicabilité Teatower
- Clients AD = **franchisés Delhaize** : `partner_id` = contrat commercial (HQ), `partner_shipping_id` = magasin. Voir `feedback_odoo_commandes_gms.md`.
- Répliquer l'historique à la création de devis : partner/invoice/shipping = derniers de la commande précédente (`feedback_orders_history.md`).
- Attacher systématiquement le **PDF source** au devis via `ir.attachment` (`res_model='sale.order'`, `res_id=order.id`). Voir `feedback_orders_attach_pdf.md`.
- Format réf : `IOxxx` → **toujours** réécrit en `I0xxx` (zéro, pas "O").

---

## 3. Achats / Purchase

### Concepts clés
- **RFQ → PO** : `purchase.order` en `draft`/`sent` (RFQ) devient `purchase` à la confirmation. Génère un `stock.picking` de réception.
- **Vendor pricelist** (`product.supplierinfo`) : prix par fournisseur, quantité min, délai, devise, partner_id. **Le premier partner_id de la liste = fournisseur par défaut** utilisé par orderpoints `buy`.
- **Invoice control policies** : `on_order_qty` (facturer sur ce qui est commandé) ou `on_received_qty` (sur ce qui est reçu). Impacte la réconciliation facture fournisseur.
- **3-way match** : PO + réception + facture doivent matcher avant paiement.

### Modèles impliqués
- `purchase.order` / `purchase.order.line` — `partner_id`, `date_order`, `date_planned`, `state`, `picking_type_id`, `product_qty`, `price_unit`.
- `product.supplierinfo` — `partner_id`, `product_tmpl_id`, `product_id`, `min_qty`, `price`, `delay` (lead time jours), `currency_id`, `date_start`/`date_end`.

### Gotchas
- Un orderpoint `buy` sans `product.supplierinfo` ne peut pas créer de RFQ — erreur typique.
- Le `delay` fournisseur s'ajoute au `delay` produit (`product.template.seller_ids.delay` + `product.template.produce_delay`).
- Les écarts de prix entre PO et facture restent sur l'écart comptable tant qu'on ne les régularise pas manuellement.

### Doc
- Purchase overview : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/purchase.html

### Applicabilité Teatower
- Kirchner Fischer = fournisseur principal thé → skill `po-kirchner` dédié pour import PDF → Excel Odoo.
- Les supplierinfo Kirchner sont extraites dans `data/odoo_supplierinfo.json`.

---

## 4. Fabrication / MRP

### Concepts clés
- **mrp.production** : ordre de fabrication (MO). States : `draft`, `confirmed`, `progress`, `done`, `cancel`.
- **mrp.bom types** :
  - `normal` : crée un MO, consomme les composants, produit le fini.
  - `phantom` (= "kit" dans l'UI vente) : **pas de MO** ; à la vente/livraison, les composants sont expédiés directement en lieu et place du produit parent.
  - `subcontract` : sous-traitance.
- **Backflush** : consommation automatique des composants au done du MO (vs "Manual Consumption" qui force la saisie).
- **MTO (Make-to-Order)** : route qui chaîne vente → MO automatique sans passer par stock.
- **Component availability check** : `components_availability` sur MO, indique si les composants sont dispos avant de lancer.

### Modèles impliqués
- `mrp.production` — `product_id`, `product_qty`, `bom_id`, `state`, `date_planned_start`, `location_src_id`, `location_dest_id`, `move_raw_ids`, `move_finished_ids`.
- `mrp.bom` — `product_tmpl_id`, `product_id`, `product_qty`, `type` (`normal`/`phantom`/`subcontract`), `code`, `bom_line_ids`.
- `mrp.bom.line` — `product_id`, `product_qty`, `product_uom_id`, `operation_id`.

### Gotchas
- Phantom (kit) : **les stats de vente sont sur le parent**, mais le stock réel est sur les composants. Un phantom sans composants en stock bloque la livraison.
- Un MO en `progress` qui n'est jamais clôturé bloque les composants en réservation — scan régulier recommandé.
- Changer une BoM n'affecte pas les MO déjà confirmés.

### Doc
- MRP overview : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/manufacturing.html
- BoM config : https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/manufacturing/basic_setup/bill_configuration.html

### Applicabilité Teatower
- Échantillons `E0xxx` et certains displays sont gérés en **kit (phantom)** — stock réel sur boîtes individuelles.
- Packaging Amazon FBA : BoM phantom avec composants = boîte individuelle + emballage.

---

## 5. Comptabilité / Accounting

### Concepts clés
- **Double-écriture** : chaque transaction = N `account.move.line` dont somme débit = somme crédit.
- **account.move** : facture client (`out_invoice`), avoir (`out_refund`), facture fournisseur (`in_invoice`), avoir fournisseur (`in_refund`), écriture diverse (`entry`).
- **Lettrage** (reconciliation) : match entre ligne facture et ligne paiement. `full_reconcile_id` sur `account.move.line`.
- **Journaux** (`account.journal`) : ventes, achats, banque, caisse, OD. Chaque `account.move` appartient à un journal.
- **Taxes BE** : 21% standard, 6% denrées alimentaires (thé = 6%), 0% export intracom. Fiscal positions mappent les taxes selon le pays du client.
- **Comptabilité analytique** (`account.analytic.account`, `account.analytic.line`) : suivi par projet/dimension, indépendante du plan comptable.

### Modèles impliqués
- `account.move` — `move_type`, `partner_id`, `invoice_date`, `invoice_date_due`, `state` (`draft`/`posted`/`cancel`), `payment_state`.
- `account.move.line` — `account_id`, `debit`, `credit`, `partner_id`, `reconciled`, `full_reconcile_id`, `analytic_distribution`.
- `account.tax` — `amount`, `type_tax_use`, `tax_group_id`, `price_include`.
- `account.journal` — `code`, `type`, `default_account_id`.
- `account.payment` / `account.payment.register` : enregistrement des paiements.

### Gotchas
- Une facture `posted` ne peut être modifiée : passer par avoir (`out_refund`) ou "Reset to Draft" (bouton conditionnel).
- Le thé alimentaire est à **6%** en BE — ne pas laisser la tax par défaut 21% sur les produits.
- Les fiscal positions s'appliquent via `partner_id.property_account_position_id`. Client export UE B2B → reverse charge (0%), requiert VAT valide.
- L'analytique en 18 utilise `analytic_distribution` (JSON dict), plus `analytic_account_id` simple.

### Doc
- Accounting overview : https://www.odoo.com/documentation/18.0/fr/applications/finance/accounting.html
- Taxes : https://www.odoo.com/documentation/18.0/fr/applications/finance/accounting/taxes.html

### Applicabilité Teatower
- Forecast compta publié en HTML — scripts `compta/forecast_odoo.xlsx` + dashboard Pages.
- CA ~1.74M EUR / 15 mois. Delhaize, Carrefour, Smartbox = top clients.

---

## 6. CRM

### Concepts clés
- **Lead vs Opportunity** : `crm.lead` est le modèle unique (`type='lead'` ou `type='opportunity'`). Un lead qualifié devient opportunity.
- **Stages** (`crm.stage`) : colonnes Kanban du pipeline, avec probabilité par défaut.
- **Activities** (`mail.activity`) : tâches planifiées (appel, email, meeting) sur tout modèle — pas seulement CRM.
- **Predictive lead scoring** : Odoo calcule une probabilité basée sur l'historique (win/lost).
- **Lost reasons** (`crm.lost.reason`) : tagger les perdues pour analyse.

### Modèles impliqués
- `crm.lead` — `partner_id`, `stage_id`, `expected_revenue`, `probability`, `team_id`, `user_id`, `tag_ids`, `date_deadline`, `active` (unarchive = lost récupéré).
- `crm.stage` — `sequence`, `is_won`, `probability`.

### Gotchas
- Une opportunité "won" ne fait PAS créer de `sale.order` automatiquement — bouton "New Quotation" requis.
- `active=False` = archive (souvent = lost). Filtres par défaut masquent les archivés.

### Doc
- CRM overview : https://www.odoo.com/documentation/18.0/fr/applications/sales/crm.html

### Applicabilité Teatower
- Pipeline B2B : Horeca, GMS, hôtellerie (Radisson = gros deal en cours).
- Script call B2B + templates CRM dans les docx racine.

---

## 7. Produit

### Concepts clés
- **product.template vs product.product** : template = fiche produit générique ; product = variante. Un template sans variante a 1 product.product associé (auto).
- **Variantes** : via `product.attribute` et `product.attribute.value` sur le template.
- **Catégorie** (`product.category`) : pilote la valorisation (`property_cost_method` : `standard`/`fifo`/`average`) et les comptes comptables (`property_stock_account_input_categ_id`, etc.).
- **Taxes par défaut** : `taxes_id` (vente) et `supplier_taxes_id` (achat) sur le template.
- **Codes barres** : `barcode` sur `product.product` (pas template). Unicité recommandée.

### Modèles impliqués
- `product.template` — `name`, `default_code`, `list_price`, `standard_price`, `type` (`consu`/`service`/`combo` en 18 — "storable" a été remplacé par `is_storable` sur `consu`), `categ_id`, `taxes_id`.
- `product.product` — variante, `barcode`, `default_code` peut différer du template.
- `product.category` — hiérarchique, `property_valuation` (`manual_periodic`/`real_time`), `property_cost_method`.

### Gotchas
- En Odoo 18 le champ `type='product'` a disparu : c'est désormais `type='consu'` + `is_storable=True`. Mauvais filtre = liste vide.
- Le coût (`standard_price`) est stocké sur `product.product`, pas template, en multi-company.

### Applicabilité Teatower
- ~500 SKUs : `I0xxx` (infusions), `V0xxx` (vrac), `E0xxx` (échantillons), displays, packs.
- `odoo_products_all.json` = snapshot complet, `teatower_products_raw.json` = extraction brute.

---

## 8. Configuration technique

### Concepts clés
- **ir.cron** : tâches planifiées (scheduler). `nextcall`, `interval_type`, `model_id`, `code`. Lancement manuel via "Run Manually".
- **ir.attachment** : fichiers attachés, polymorphique via `res_model` + `res_id`. Peut stocker en filestore ou DB.
- **base.automation** : règles automatisées (trigger on_create/on_write/on_unlink/on_time + server action).
- **ir.sequence** : numérotation (factures, devis…). `prefix`, `suffix`, `padding`, `implementation` (`standard`/`no_gap`).
- **Record rules** (`ir.rule`) : ACL au niveau ligne, par groupe, via `domain_force`.
- **Multi-company** : `res.company`, `company_id` sur presque tous les modèles, `company_ids` sur `res.users`.

### Modèles
- `ir.cron`, `ir.attachment`, `base.automation`, `ir.sequence`, `ir.rule`, `ir.model.fields`, `ir.actions.server`.

### Gotchas
- `base.automation` avec trigger "on_time" : scheduler tourne toutes les 4h par défaut (40min si délai < 2400min).
- `ir.sequence` avec `implementation='no_gap'` est **transactionnel** — lock sur table, impacte perfo en écriture massive.
- `ir.attachment` en `storage='file'` : supprimer un record ne supprime pas forcément le fichier disque — `cron_vacuum` le fait.

### Doc
- Automated actions : https://www.odoo.com/documentation/18.0/fr/applications/studio/automated_actions.html

---

## 9. Intégrations & API

### Concepts clés
- **XML-RPC** : endpoints `/xmlrpc/2/common` (auth) et `/xmlrpc/2/object` (exec). Utilisé par Python via `xmlrpc.client`.
- **JSON-RPC** : `/jsonrpc` — recommandé pour web/JS, équivalent fonctionnel.
- **API Key** : créer dans Préférences utilisateur → Account Security. Remplace le password en clair. Non récupérable après création.
- **Webhooks** : `base.automation` peut émettre des webhooks sortants. Webhooks entrants via `mail.thread` message_process ou custom controller.
- **Methods clés** : `search`, `search_read`, `read`, `create`, `write`, `unlink`, `search_count`, `fields_get`, `name_search`.

### Doc
- External API : https://www.odoo.com/documentation/18.0/fr/developer/reference/external_api.html

### Applicabilité Teatower
- Accès via JSON-RPC, DB `tsc-be-tea-tree-main-18515272`. Credentials dans `reference_credentials.md`.
- Amazon Connector actif ; Shopify côté site Teatower (pas de connecteur natif stable en FR 18, prévoir custom).

---

## Commandes XML-RPC typiques (Python)

```python
import xmlrpc.client
URL  = "https://tea-tree.odoo.com"
DB   = "tsc-be-tea-tree-main-18515272"
USER = "nicolas@teatower.be"
KEY  = "<API_KEY>"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid    = common.authenticate(DB, USER, KEY, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def rpc(model, method, args, kwargs=None):
    return models.execute_kw(DB, uid, KEY, model, method, args, kwargs or {})
```

### 1 — Lister les produits `I0xxx` avec stock
```python
rpc('product.product', 'search_read',
    [[['default_code', '=like', 'I0%']]],
    {'fields': ['default_code', 'name', 'qty_available', 'list_price'], 'limit': 500})
```

### 2 — Lire orderpoints d'un magasin (location WAT/Stock)
```python
rpc('stock.warehouse.orderpoint', 'search_read',
    [[['location_id.complete_name', '=', 'WAT/Stock']]],
    {'fields': ['product_id','product_min_qty','product_max_qty','qty_multiple','trigger']})
```

### 3 — Créer un devis GMS avec partner_invoice/shipping
```python
rpc('sale.order', 'create', [{
    'partner_id': 1234,
    'partner_invoice_id': 1234,
    'partner_shipping_id': 5678,
    'client_order_ref': 'I05380',
    'order_line': [(0, 0, {'product_id': 42, 'product_uom_qty': 12, 'price_unit': 3.20})],
}])
```

### 4 — Confirmer une commande
```python
rpc('sale.order', 'action_confirm', [[order_id]])
```

### 5 — Attacher un PDF à un devis
```python
import base64
with open('bc.pdf','rb') as f: data = base64.b64encode(f.read()).decode()
rpc('ir.attachment', 'create', [{
    'name': 'BC_client.pdf', 'datas': data,
    'res_model': 'sale.order', 'res_id': order_id, 'type': 'binary',
}])
```

### 6 — Stock par produit et location
```python
rpc('stock.quant', 'search_read',
    [[['product_id','=', pid], ['location_id.usage','=','internal']]],
    {'fields': ['location_id','quantity','reserved_quantity']})
```

### 7 — Créer un transfert interne TT/Stock → WAT/Stock
```python
picking_id = rpc('stock.picking', 'create', [{
    'picking_type_id': 5,  # Internal Transfer type
    'location_id': tt_stock_id,
    'location_dest_id': wat_stock_id,
    'priority': '1',  # étoile
    'move_ids_without_package': [(0,0,{
        'name': 'Réassort WAT',
        'product_id': pid, 'product_uom_qty': 24,
        'product_uom': uom_id,
        'location_id': tt_stock_id, 'location_dest_id': wat_stock_id,
    })],
}])
rpc('stock.picking','action_confirm',[[picking_id]])
rpc('stock.picking','action_assign',[[picking_id]])
```

### 8 — Mettre à jour min/max d'une orderpoint
```python
rpc('stock.warehouse.orderpoint', 'write',
    [[op_id], {'product_min_qty': 24, 'product_max_qty': 30, 'qty_multiple': 6}])
```

### 9 — Lire factures non lettrées d'un partenaire
```python
rpc('account.move', 'search_read',
    [[['partner_id','=', pid], ['move_type','=','out_invoice'],
      ['state','=','posted'], ['payment_state','in',['not_paid','partial']]]],
    {'fields': ['name','invoice_date','amount_total','amount_residual']})
```

### 10 — Créer un RFQ (PO draft) vers Kirchner
```python
rpc('purchase.order', 'create', [{
    'partner_id': kirchner_id,
    'order_line': [(0,0,{
        'product_id': pid, 'name': 'Thé vrac X',
        'product_qty': 100, 'product_uom': uom_id, 'price_unit': 4.50,
        'date_planned': '2026-05-01',
    })],
}])
```

---

## Ma bibliothèque de référence

| URL | Usage |
|-----|-------|
| https://www.odoo.com/documentation/18.0/fr/ | Racine doc Odoo 18 FR |
| https://www.odoo.com/documentation/18.0/fr/developer/reference/external_api.html | XML-RPC / JSON-RPC, API keys |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory.html | Hub Inventaire |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment.html | Méthodes de réapprovisionnement |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/reordering_rules.html | Orderpoints min/max détaillé |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/shipping_receiving/daily_operations.html | Flux 1/2/3 steps, routes, rules |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/shipping_receiving/reservation_methods.html | Reservation methods |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/use_locations.html | Types de locations |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.html | Inventaire physique / ajustements |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/using_inventory_valuation.html | Valorisation stock |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/purchase.html | Hub Achats |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/manufacturing.html | Hub MRP |
| https://www.odoo.com/documentation/18.0/fr/applications/inventory_and_mrp/manufacturing/basic_setup/bill_configuration.html | BoM normal/kit/phantom |
| https://www.odoo.com/documentation/18.0/fr/applications/sales/sales.html | Hub Ventes |
| https://www.odoo.com/documentation/18.0/fr/applications/sales/sales/products_prices/prices/pricing.html | Pricelists |
| https://www.odoo.com/documentation/18.0/fr/applications/sales/sales/amazon_connector.html | Amazon Connector |
| https://www.odoo.com/documentation/18.0/fr/applications/sales/crm.html | Hub CRM |
| https://www.odoo.com/documentation/18.0/fr/applications/finance/accounting.html | Hub Comptabilité |
| https://www.odoo.com/documentation/18.0/fr/applications/finance/accounting/taxes.html | Taxes, fiscal positions |
| https://www.odoo.com/documentation/18.0/fr/applications/studio/automated_actions.html | base.automation |
| https://www.odoo.com/documentation/18.0/fr/applications/general/integrations.html | Intégrations générales (Gmail, Outlook, GCloud…) |

---

## Réflexes de session
1. Avant toute modif d'orderpoint : re-lire la section 1 (formule min/max Teatower).
2. Avant toute création `sale.order` GMS : vérifier `partner_id` vs `partner_shipping_id` + format réf `I0xxx`.
3. Avant tout `stock.picking` interne : `priority='1'` pour étoile, types et locations explicitement nommés.
4. Toujours attacher le PDF source via `ir.attachment`.
5. Jamais de `--amend`/`reset --hard` git, toute modif dashboard/public = commit + push immédiat.
