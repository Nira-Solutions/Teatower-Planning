# Setup Google Sheets pour agent Compta

L'agent Compta doit pouvoir lire/écrire dans ton fichier de suivi paiements Google Sheets. Pour ça, on passe par un **service account Google** (robot utilisateur) auquel tu partages le fichier.

## Étapes (15 min, une seule fois)

### 1. Créer un projet Google Cloud

1. Va sur https://console.cloud.google.com/
2. En haut à gauche, sélecteur de projet → **Nouveau projet**
3. Nom : `Teatower Compta` → Créer

### 2. Activer les APIs nécessaires

Dans le projet, menu latéral → **APIs et services** → **Bibliothèque**. Active ces deux APIs :
- **Google Sheets API** (chercher "Sheets" → Activer)
- **Google Drive API** (chercher "Drive" → Activer)

### 3. Créer le service account

1. Menu → **APIs et services** → **Identifiants**
2. **Créer des identifiants** → **Compte de service**
3. Nom : `teatower-compta-bot`
4. ID : auto
5. Ignore les étapes 2 et 3 (rôles, utilisateurs) → **Terminé**

### 4. Générer la clé JSON

1. Dans la liste des comptes de service, clique sur `teatower-compta-bot@...`
2. Onglet **Clés** → **Ajouter une clé** → **Créer une clé** → **JSON** → Créer
3. Un fichier `.json` se télécharge. **Renomme-le** `google_service_account.json` et place-le ici :
   ```
   C:\Users\FlowUP\Downloads\Claude\Claude\Teatower\compta\google_service_account.json
   ```
4. **IMPORTANT** : ce fichier est déjà dans `.gitignore` (à vérifier), **ne le commit jamais**.

### 5. Partager le Google Sheet avec le service account

1. Ouvre le JSON et copie la valeur `client_email` (ressemble à `teatower-compta-bot@teatower-compta.iam.gserviceaccount.com`)
2. Ouvre ton fichier paiements : https://docs.google.com/spreadsheets/d/1tpQQ5vTr5ekQesJKmkJi86cq9dG7sIFZ/edit
3. Bouton **Partager** (en haut à droite)
4. Colle le `client_email` → rôle **Éditeur** → Envoyer (décoche "Notifier")

### 6. Installer les libs Python

```bash
pip install gspread google-auth openpyxl
```

### 7. Tester

```bash
python compta/forecast_echeancier.py --test
```

Si ça retourne `✓ Accès OK — X onglets trouvés`, c'est bon.

---

## Ce que l'agent fera ensuite

Une fois le setup fait, dis à Nira : *"Compta, génère le forecast dans mon fichier paiements"*. L'agent :
1. Lit l'onglet existant (récurrents manuels)
2. Query Odoo (factures fournisseurs non payées + récurrents détectés)
3. Crée/met à jour un onglet **Forecast** avec échéancier J+7 / J+30 / >30j
4. Logge dans `compta/LOG.md`

Tu peux automatiser via un cron Claude Code chaque lundi matin (je peux le setup quand tu veux).
