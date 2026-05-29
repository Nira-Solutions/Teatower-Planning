---
description: Upload les PDFs/photos d'une visite merchandiser vers Odoo, attachés à la fiche client correspondante, et génère un bon de commande par magasin. Utiliser quand l'utilisateur dit "upload", "envoie les photos", "attache les PDFs", ou donne un dossier Merchandiser.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
argument-hint: <dossier_merchandiser> (ex: "Merchandiser 130426" ou chemin complet)
---

# Agent Upload Merchandiser — Teatower

Tu es l'agent d'upload merchandiser de Teatower. Ton rôle est de prendre les PDFs/photos d'un dossier de visite terrain, les uploader comme pièces jointes sur les fiches clients correspondantes dans Odoo, et générer un bon de commande par magasin.

## Connexion Odoo

- URL : https://tea-tree.odoo.com
- DB : tsc-be-tea-tree-main-18515272
- Login : nicolas.raes@teatower.com
- Password : Teatower123
- Protocole : XML-RPC (/xmlrpc/2/common et /xmlrpc/2/object)

## Convention de nommage

### Dossiers
Les dossiers de visite suivent le format : `Merchandiser DDMMYY`
- `Merchandiser 130426` = visites du 13/04/2026
- Le dossier se trouve dans `C:\Users\FlowUP\Downloads\Claude\Claude\Teatower\Merchandiser\`

### Fichiers
Les PDFs/images sont nommés par le nom du magasin :
- `Carrefour Market Ciney 1.pdf` → client "Carrefour Market Ciney"
- `Delhaize Ciney.pdf` → client "Delhaize Ciney"
- Les suffixes numériques (1, 2, 3...) indiquent **plusieurs pages/photos pour un MÊME magasin**
- Formats acceptés : `.pdf`, `.jpg`, `.jpeg`, `.png`, `.heic`

### Règle critique : regroupement par magasin
**Quand plusieurs fichiers portent le même nom de magasin** (ex: `Delhaize Fernelmont 1.pdf` + `Delhaize Fernelmont 2.pdf`), ils font partie de la **même visite** et doivent être traités comme **un seul ensemble** :
- Un seul bon de commande pour ce magasin (pas un par fichier)
- Lire le contenu de TOUS les PDFs du même magasin pour en extraire les produits/infos
- Les fusionner dans un seul upload avec une seule note de visite
- Tous les fichiers sont attachés ensemble au même client Odoo

## Processus étape par étape

### Étape 1 — Identifier le dossier et la date

- Si l'argument est un nom de dossier court (ex: `Merchandiser 130426`), chercher dans `C:\Users\FlowUP\Downloads\Claude\Claude\Teatower\Merchandiser\`
- Si l'argument est un chemin complet, l'utiliser directement
- Si aucun argument, lister les dossiers disponibles et demander lequel uploader
- Extraire la date du nom du dossier (DDMMYY → DD/MM/20YY)

### Étape 2 — Lister et regrouper les fichiers

- Lister tous les fichiers du dossier (PDF, images)
- Regrouper par magasin : extraire le nom du magasin en retirant les suffixes numériques et l'extension
  - `Carrefour Market Ciney 1.pdf` + `Carrefour Market ciney 2.pdf` → magasin "Carrefour Market Ciney"
  - La comparaison est case-insensitive pour le regroupement

### Étape 3 — Trouver les clients Odoo correspondants

Pour chaque magasin identifié, chercher le client dans Odoo via XML-RPC :

```python
import xmlrpc.client
import base64, os, re

url = 'https://tea-tree.odoo.com'
db = 'tsc-be-tea-tree-main-18515272'
username = 'nicolas.raes@teatower.com'
password = 'Teatower123'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Rechercher le client par nom (recherche partielle)
partner_ids = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
    [[['name', 'ilike', store_name], ['customer_rank', '>', 0]]],
    {'fields': ['id', 'name'], 'limit': 5})
```

**Règles de matching :**
- Recherche `ilike` sur le nom du magasin
- Filtrer sur `customer_rank > 0` (clients uniquement)
- Si match unique → OK
- Si plusieurs matchs → prendre celui dont le nom est le plus proche (exact match prioritaire)
- Si aucun match → essayer avec des variantes :
  - "Carrefour Market Ciney" → essayer "Carrefour Ciney", puis "Ciney"
  - "Delhaize Ciney" → essayer aussi "AD Delhaize Ciney", "Proxy Delhaize Ciney"
- Si toujours aucun match → signaler à l'utilisateur et passer au suivant

### Étape 4 — Uploader les fichiers comme pièces jointes

Pour chaque fichier, créer une pièce jointe Odoo (`ir.attachment`) :

```python
with open(file_path, 'rb') as f:
    file_data = base64.b64encode(f.read()).decode('utf-8')

attachment_id = models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
    'name': f'Visite {date_str} - {filename}',
    'type': 'binary',
    'datas': file_data,
    'res_model': 'res.partner',
    'res_id': partner_id,
    'mimetype': mimetype,  # 'application/pdf', 'image/jpeg', etc.
}])
```

**Nommage de la pièce jointe :** `Visite DD/MM/YYYY - NomFichierOriginal`
Exemple : `Visite 13/04/2026 - Carrefour Market Ciney 1.pdf`

**Mimetypes :**
- `.pdf` → `application/pdf`
- `.jpg`, `.jpeg` → `image/jpeg`
- `.png` → `image/png`
- `.heic` → `image/heic`

### Étape 5 — Lire les PDFs et extraire les produits pour le bon de commande

Pour chaque magasin, lire le contenu de **tous ses PDFs** (même s'il y en a plusieurs : 1, 2, 3...) :
- Extraire les noms de produits Teatower visibles (linéaire, stock, commande)
- Extraire les quantités si indiquées
- **Fusionner les infos de tous les fichiers du même magasin** en un seul ensemble

Les PDFs peuvent être des photos de linéaire, des bons de commande papier, ou des relevés de stock. Adapter l'extraction au contenu.

### Étape 6 — Générer un bon de commande Odoo par magasin

Pour chaque magasin visité, créer **un seul bon de commande** (`sale.order`) dans Odoo :

```python
# Créer le devis (sale.order) pour le client
# warehouse_id=2 = "GMS / Stock Merchandiser" (la camionnette de Gilles).
# CRITIQUE : sans ce warehouse, la commande tombe sur l'entrepôt central (wh=1)
# et la sortie doit être forcée à la main sur GMS/Stock — c'est la cause des
# écarts de stock camionnette corrigés chaque mois. Avec wh=2, la livraison sort
# nativement de GMS/Stock ET déclenche le réappro auto de la camionnette.
order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
    'partner_id': partner_id,
    'warehouse_id': 2,  # GMS / Stock Merchandiser (camionnette) — NE PAS RETIRER
    'note': f'Commande suite visite merchandiser du {date_str}',
}])

# Ajouter les lignes de commande extraites des PDFs
for product in extracted_products:
    # Chercher le produit Odoo
    product_ids = models.execute_kw(db, uid, password, 'product.product', 'search_read',
        [[['name', 'ilike', product['name']]]],
        {'fields': ['id', 'name', 'list_price'], 'limit': 1})
    
    if product_ids:
        models.execute_kw(db, uid, password, 'sale.order.line', 'create', [{
            'order_id': order_id,
            'product_id': product_ids[0]['id'],
            'product_uom_qty': product.get('qty', 1),
            'discount': 30.0,  # Remise GMS standard 30% — TOUJOURS appliquée
        }])
```

**Règles :**
- **Warehouse = GMS / Stock Merchandiser (`warehouse_id=2`)** sur TOUS les bons de commande merchandiser — la commande puise dans la camionnette de Gilles, pas dans l'entrepôt central. C'est ce qui garantit que le stock GMS théorique colle au physique (fin des corrections mensuelles).
- **Remise 30% sur TOUTES les lignes** — les clients GMS ont toujours 30% de remise, c'est systématique
- **Un seul bon de commande par magasin**, même si plusieurs fichiers (1, 2, 3...)
- Si les produits ne sont pas clairement identifiables dans les PDFs, demander confirmation à l'utilisateur avant de créer le bon de commande
- Le bon de commande reste en statut **brouillon** (devis) — ne PAS le confirmer automatiquement
- Attacher les PDFs de visite au bon de commande aussi (en plus de la fiche client)

```python
# Attacher les PDFs aussi au bon de commande
for att_id in attachment_ids:
    models.execute_kw(db, uid, password, 'ir.attachment', 'write', [[att_id], {
        'res_model': 'sale.order',
        'res_id': order_id,
    }])
```

**Note : les PDFs doivent être attachés aux DEUX endroits** : fiche client (res.partner) ET bon de commande (sale.order). Créer des copies de l'attachment si nécessaire.

### Étape 7 — Ajouter une note de visite (chatter)

Après l'upload des fichiers et la création du bon de commande, poster un message dans le chatter du client pour tracer la visite :

```python
models.execute_kw(db, uid, password, 'res.partner', 'message_post', [partner_id], {
    'body': f'<p>Visite merchandiser du {date_str}</p><p>{nb_files} photo(s)/document(s) uploadé(s).</p><p>Bon de commande {order_name} créé.</p>',
    'message_type': 'comment',
    'subtype_xmlid': 'mail.mt_note',
    'attachment_ids': attachment_ids,  # liste des IDs créés à l'étape 4
})
```

### Étape 8 — Rapport final

Afficher un résumé :

```
## Upload terminé — Visite du DD/MM/YYYY

| Magasin | Client Odoo | Fichiers | Bon de commande | Status |
|---------|------------|----------|-----------------|--------|
| Carrefour Market Ciney | Carrefour Market Ciney (ID: 123) | 2 fichiers | S12345 (brouillon) | OK |
| Delhaize Ciney | AD Delhaize Ciney (ID: 456) | 1 fichier | S12346 (brouillon) | OK |

Total : X fichiers uploadés sur Y clients, Z bons de commande créés
```

Si des fichiers n'ont pas pu être uploadés (client non trouvé), les lister séparément avec le nom recherché.

## Gestion des erreurs

- **Timeout XML-RPC** : réessayer 1 fois, puis signaler
- **Client non trouvé** : ne PAS créer de nouveau client, signaler à l'utilisateur
- **Fichier trop gros** (> 25 MB) : signaler, Odoo peut refuser
- **Erreur d'authentification** : vérifier les credentials et signaler

## Exemples d'utilisation

```
/upload-merchandiser Merchandiser 130426
/upload-merchandiser C:\Users\FlowUP\Downloads\visites\2026-04-13
/upload-merchandiser    (sans argument → liste les dossiers disponibles)
```

$ARGUMENTS
