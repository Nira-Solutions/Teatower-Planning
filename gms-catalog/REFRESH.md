# Catalogue GMS — Pipeline de mise à jour

Page publique : <https://nira-solutions.github.io/Teatower-Planning/gms-catalog/>
Affiche QR : <https://nira-solutions.github.io/Teatower-Planning/gms-catalog/qr.html>

## Contenu
- `index.html` — page de recherche (statique, lit `catalog.json`)
- `catalog.json` — catalogue produits (généré depuis Odoo)
- `qr-catalog-gms.png` — QR code vers la page (vert Teatower)
- `qr.html` — affiche imprimable avec le QR

## Comment rafraîchir le catalogue depuis Odoo

Depuis `C:\Users\FlowUP\OneDrive\Teatower` :

```bash
python _gms_build_catalog.py   # regénère _gms_catalog.json
python _gms_publish.py         # met à jour gms-catalog/catalog.json + QR
git add gms-catalog/ && git commit -m "gms-catalog: refresh" && git push
```

## Critères de sélection des produits

Union de :
1. **Réappro orderpoint GMS** — produits avec un point de commande sur le warehouse `Stock Merchandiser` (code `GMS`).
2. **Vendus 12 derniers mois** — produits présents dans des SO confirmées de clients tagués `GMS` (id 27) ou `Canal GMS` (id 88).

Drapeaux affichés sur chaque ligne : `Réappro` (sélection officielle) / `Vendu 12m` (historique).

Exclusions : services (`TRANSPORT`, livraison, frais).
