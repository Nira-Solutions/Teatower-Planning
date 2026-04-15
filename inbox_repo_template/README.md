# Teatower Orders Inbox

Réception et traitement des commandes B2B déposées via https://nira-solutions.github.io/Teatower-Planning/commande.html

## Flux

1. La personne remplit le formulaire web → proxy Deno → crée `inbox/<order_id>/order.json` ici
2. Le workflow `process.yml` se déclenche automatiquement sur chaque push dans `inbox/**`
3. `scripts/process.py` :
   - Match le nom client dans Odoo
   - Valide les SKU
   - Crée un `sale.order` en brouillon
   - Déplace la commande dans `archive/<order_id>/` avec un `result.json`
4. Sur erreur (client inconnu, SKU manquant) : la commande reste dans `inbox/` avec un fichier `ERROR.txt` — revue humaine nécessaire.

## Secrets GitHub requis

- `ODOO_URL` — ex: `https://tea-tree.odoo.com`
- `ODOO_DB` — ex: `tsc-be-tea-tree-main-18515272`
- `ODOO_USER` — ex: `nicolas.raes@teatower.com`
- `ODOO_PWD` — mot de passe Odoo

## Archivage OneDrive

Clone ce repo localement dans ton OneDrive → le dossier `archive/` sera synchronisé automatiquement vers OneDrive Teatower.
