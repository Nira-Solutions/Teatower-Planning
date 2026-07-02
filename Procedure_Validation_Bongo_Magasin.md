# Procédure — Valider un coffret Bongo en magasin

**Pour :** équipe magasin (boutiques Teatower)
**Client Odoo concerné :** Smartbox Group
**Principe :** un client se présente avec un coffret **Bongo / Smartbox**. On vérifie et on « consomme » le bon chez Bongo, PUIS on encode la vente au POS. Le rapprochement se fera ensuite entre notre facture à Smartbox et les bongos validés de leur côté.

> ⚠️ **Ordre obligatoire : d'abord valider chez Bongo (Étape 1), ensuite encaisser dans Odoo (Étape 2).**
> Si on encaisse sans avoir validé le bon chez Bongo, on ne sera pas payé (pas de matching).

---

## Étape 1 — Vérifier et enregistrer le bongo chez Smartbox/Bongo

1. Ouvrir la plateforme partenaires Bongo :
   **https://partners.smartbox-group.com/s/**

2. Se connecter avec les accès Teatower :
   - **Identifiant :** `jerome.carlier@noenature.com`
   - **Mot de passe :** `Teatower5377$`

3. Encoder les **9 chiffres** du coffret Bongo (le code imprimé sur le bon / le coffret).

4. La plateforme indique :
   - ✅ **Bon valide** → continuer.
   - ❌ **Bon invalide / déjà utilisé / expiré** → **ne pas encoder la vente**. Expliquer au client que le bon n'est pas utilisable.

5. Sur la plateforme, **enregistrer l'utilisation** du bon (marquer comme consommé chez Bongo).
   → C'est cette étape qui permet le matching : le bon passe côté Bongo en « utilisé », et on facturera ce même bon à Smartbox.

6. **Noter les 9 chiffres** — on va les reporter sur la vente Odoo (Étape 2, point 4).

---

## Étape 2 — Encoder la vente au POS Odoo

1. Ouvrir le **POS** en magasin.

2. Ajouter au panier le **produit Bongo correspondant au choix du client** (tous présents dans le POS) :
   - **Bongo Anniversaire**
   - **Bongo Émotion**
   - **Bongo Évasion**
   - **Bongo Famille**

   > 🧩 Le produit Bongo est un **kit** dans Odoo : à la vente, Odoo **déduit automatiquement du stock les produits contenus** dans le coffret. Rien à faire de plus côté stock.

3. Sélectionner le paiement **« Compte client »** (paiement sur compte, pas cash ni carte).
   → La vente sera facturée plus tard à **Smartbox Group**.

4. **Reporter le numéro à 9 chiffres du bongo** dans la vente (référence / note de la commande POS).
   → Indispensable pour rapprocher notre facture avec les bongos validés chez Smartbox.

5. Valider / clôturer la vente.

---

## Rappels

- **Toujours Étape 1 avant Étape 2.** Pas de validation Bongo = pas de paiement.
- Un bon **invalide/déjà utilisé** ne se vend pas.
- Paiement **« Compte client »** uniquement (client = Smartbox Group).
- Le **numéro à 9 chiffres** doit figurer sur la vente pour le matching à la facturation.
- Le produit Bongo est un **kit** → le stock des produits inclus se décrémente tout seul.

---

*Procédure Teatower — à jour au 02/07/2026.*
