# 🍵 Sondage « Teatower, c'est quoi ? » — mise en route

Tout est gratuit, aucune carte bancaire, tes données restent dans **ton** Google Drive.

**Ce que tu obtiens :**
- Un **formulaire web** brandé Teatower que tu partages par lien à l'équipe.
- Un **Google Sheet** privé qui se remplit tout seul (1 ligne = 1 personne).
- Un **dashboard d'analyse** automatique (moyennes, top valeurs, tous les verbatims) → directement exploitable pour le CA d'Alexandre.

---

## Étape 1 — Créer le réceptacle (Google Sheet + script)  ⏱️ 3 min

1. Va sur **https://sheets.new** (crée un nouveau Google Sheet). Nomme-le `Sondage Teatower`.
2. Menu **Extensions → Apps Script**.
3. Efface le code par défaut, **colle tout le contenu de `Code.gs`** (le fichier de ce dossier).
4. *(Optionnel)* en haut du code, change `var SECRET = 'teatower2026';` par un mot de passe à toi.
5. Clique **💾 Enregistrer**.

## Étape 2 — Déployer le Web App  ⏱️ 1 min

1. En haut à droite : **Déployer → Nouveau déploiement**.
2. Roue crantée ⚙️ → **Application Web**.
3. Règle :
   - **Exécuter en tant que** : *Moi (ton email)*
   - **Qui a accès** : *Tout le monde*  ← important pour que l'équipe puisse répondre
4. **Déployer**. Autorise l'accès quand Google demande (clique *Avancé → Accéder à (non sécurisé)* si l'écran d'avertissement Google apparaît — c'est normal pour tes propres scripts).
5. **Copie l'URL** qui finit par `/exec`. Elle ressemble à :
   `https://script.google.com/macros/s/AKfy....../exec`

## Étape 3 — Brancher le formulaire  ⏱️ 30 s

➡️ **Envoie-moi (Nira) cette URL `/exec`.**
Je la colle dans le formulaire (`SCRIPT_URL`), je commit + push, et le formulaire est en ligne à :

```
https://nira-solutions.github.io/Teatower-Planning/sondage/
```

*(Si tu veux le faire toi-même : ouvre `sondage/index.html`, remplace `__SCRIPT_URL__` par ton URL.)*

---

## Utilisation au quotidien

**Partager à l'équipe** — envoie ce lien (Slack / email / WhatsApp) :
> 👉 https://nira-solutions.github.io/Teatower-Planning/sondage/

**Voir le récap de tout** — deux options :
1. **Le Google Sheet** lui-même : chaque réponse = 1 ligne, tu filtres/tries comme tu veux.
2. **Le dashboard d'analyse** (recommandé pour le CA) — ouvre :
   ```
   https://script.google.com/macros/s/AKfy....../exec?key=teatower2026
   ```
   (remplace `teatower2026` si tu as changé le `SECRET`). Bouton **🖨️ Imprimer / PDF** intégré pour annexer au CA.

---

## Notes

- Le formulaire est public (seul le lien permet d'y accéder) — adapté à un sondage interne. Pas d'email requis pour répondre, réponses anonymes possibles (prénom optionnel).
- Si tu modifies `Code.gs` plus tard : **Déployer → Gérer les déploiements → ✏️ → Nouvelle version**. L'URL `/exec` reste la même.
- Une question à ajouter/retirer ? Dis-le moi, je synchronise formulaire + dashboard.
