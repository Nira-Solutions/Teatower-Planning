# Brief Stephan — Newsletters Juin 2026

**À :** Stephan
**De :** Nicolas Raes
**Date :** 11 mai 2026
**Objet :** Lancement des 2 premières campagnes Mailchimp de la roadmap B2B 12 mois
**Envoi prévu :** mardi 9 juin 2026, 9h00

---

## Le contexte en 30 secondes

On démarre une **roadmap B2B sur 12 mois** (juin 2026 → mai 2027) avec un objectif simple : **+200 K€ de CA additionnel** sur la base actuelle de 881 K€. La mécanique : 1 ou 2 campagnes Mailchimp ciblées par mois, segment par segment (Horeca, Revendeur, GMS, Grossiste), avec une offre claire chacune.

Tu pilotes la partie newsletter Mailchimp de bout en bout. Moi je m'occupe des données Odoo (segmentation, tags, tracking). Vanessa pilote la suite : commandes entrantes, application de l'offre, SAV. Jérôme appuie en relance commerciale J+10 sur les comptes prioritaires.

**Principe juin** : on cible UNIQUEMENT les clients dormants (qui n'ont pas commandé depuis > 6 mois). On n'envoie PAS aux Horeca actifs — pas de promo à des clients qui commandent déjà = pas de cannibalisation.

---

## Juin 2026 — 2 campagnes en parallèle

| Campagne | Volume | Offre | CA cible |
|---|---|---|---|
| **A — Horeca dormant** (sans commande > 6 mois) | 11 | 3+1 sur boîtes HC25 + relance Jérôme | +1 K€ |
| **B — Revendeur dormant** (sans commande > 6 mois) | 105 | -10% sur réassort libre ≥ 300€ + relance Jérôme top 20 | +8 K€ |
| **TOTAL** | **116** | | **+9 K€** |

**Tags Odoo correspondants** (à utiliser pour créer les 2 audiences Mailchimp) :
- A → `MC-202606-HORECA-DORMANT`
- B → `MC-202606-REVENDEUR-DORMANT`

---

## Tracking de la conversion (sans code promo)

**On ne demande PAS aux clients de saisir un code.** C'est trop compliqué à suivre côté opérationnel.

À la place, on tracke automatiquement via croisement de listes Odoo :

1. **On sait qui a reçu chaque mailing** (tag Odoo `MC-202606-HORECA-DORMANT` ou `MC-202606-REVENDEUR-DORMANT`)
2. **On sait qui a commandé** (sale.order date_order entre le 9 juin et le 9 juillet)
3. **Croisement** → on identifie automatiquement les conversions, sans code à saisir, sans champ à remplir

**Workflow Vanessa** : elle traite les commandes comme d'habitude. Si l'offre est mentionnée par le client (3+1 ou -10%), elle l'applique sur le devis. Pas de code à saisir, pas de champ supplémentaire.

**Reporting J+30 (9 juillet)** : je sors la liste "partners taggés campagne juin qui ont passé commande dans la fenêtre 9 juin → 9 juillet" → liste exhaustive des conversions, CA généré, taux de réactivation.

---

## Les 2 templates à concevoir

### Template A — Horeca dormant (11 destinataires)

**Ton** : "Vous nous manquez", retour aux fondamentaux, sincère mais pas larmoyant
**Objet email proposé** : "Cela fait un moment... 3+1 pour reprendre tranquillement ?"
**Angle** : On a remarqué qu'on ne s'est plus parlé. Voici une offre pour reprendre contact sans pression.
**Particularité** : Jérôme va appeler le top 5 de cette liste à J+10 si pas de retour

**Contenu obligatoire** :
- Offre : 3 boîtes HC25 achetées = 4ᵉ offerte, 1 réf au choix par tranche de 3
- Min 6 boîtes, port offert dès 200 €, valable juin uniquement
- **Phrase d'accroche dédiée** : "Nous avons remarqué que cela fait quelques mois que nous ne nous sommes pas parlés..."
- CTA simple : "Répondez à cet email pour passer commande, ou appelez Vanessa au [numéro]"
- Mention "Jérôme reste à votre disposition pour un échange, n'hésitez pas"

### Template B — Revendeur dormant (105 destinataires)

**Ton** : Libre, respectueux, "vous choisissez ce que vous voulez", pas une opé promo classique
**Objet email proposé** : "Reprenons contact — votre choix, -10% sur toute la gamme 🍵"
**Angle** : Pas de SKU forcé, pas de pack imposé. C'est *votre* réassort, à *votre* rythme. Juste -10% pour reprendre tranquillement.
**Particularité** : Jérôme va appeler le top 20 (CA historique ≥ 2 K€) à J+10

**Contenu obligatoire** :
- Offre : **-10% sur toute commande ≥ 300 €**, frais de port offerts dès 250 €
- 1 commande maximum par client, valable juin uniquement
- **Phrase d'accroche dédiée** : "Cela fait un moment que nous n'avons plus eu de vos nouvelles. Plutôt que vous proposer un assortiment imposé, nous vous laissons carte blanche..."
- CTA simple : "Passez commande via notre catalogue ou contactez Vanessa"
- Lien vers le catalogue produits (page Shopify pro)

---

## Calendrier de production

| Date | Échéance | Qui |
|---|---|---|
| **11 mai (fait)** | Roadmap validée + tags Odoo posés + CSV généré | Nicolas |
| **15 mai (J-25)** | Brief créatif validé (objets, angles, visuels) | Stephan + Nicolas |
| **20 mai (J-20)** | Import CSV dans Mailchimp + création des 2 audiences | Stephan |
| **25 mai (J-15)** | Premiers drafts des 2 templates Mailchimp | Stephan |
| **27 mai (J-13)** | Revue templates + ajustements | Nicolas |
| **2 juin (J-7)** | Envoi de test interne (à nicolas@, vanessa@, stephan@, jerome@) | Stephan |
| **3 juin (J-6)** | Brief Jérôme : liste top 20 Revendeur + top 5 Horeca dormants | Nicolas |
| **9 juin 9h00 (J)** | **Envoi des 2 campagnes (par segment)** | Stephan |
| **12 juin (J+3)** | Relance Mailchimp aux non-ouvreurs (objet alternatif) | Stephan |
| **19 juin (J+10)** | Appels relance Jérôme top 20 + top 5 | Jérôme |
| **9 juillet (J+30)** | Reporting CA + ROI campagne via croisement listes Odoo | Nicolas |

---

## KPI à tracker

### Métriques Mailchimp (que tu nous remontes)

| Métrique | Cible |
|---|---|
| Taux d'ouverture moyen sur les 2 campagnes | ≥ 35% (sectoriel B2B premium) — visuel "vous nous manquez" booste l'ouverture |
| Taux de clic moyen | ≥ 8% |
| Désabonnements | < 0,5% |
| Bounces | attendu 5-10 sur 116 destinataires (~5-8%) — emails dormants = base partiellement périmée, c'est normal |

### Métriques business (qu'on calcule via Odoo, automatique)

| Métrique | Cible |
|---|---|
| Commandes générées par les destinataires entre 9 juin et 9 juillet | 16-18 |
| CA additionnel | +9 K€ |
| Réactivations Revendeur dormant | 13-15 sur 105 (~13%) |
| Réactivations Horeca dormant | 3 sur 11 (sur petit volume) |

---

## Workflow récap (qui fait quoi)

```
NICOLAS  → segmente Odoo, tag, exporte CSV (email + nom uniquement)
            ↓
STEPHAN  → importe CSV Mailchimp, crée 2 audiences, designe 2 templates
            ↓
            envoie les 2 mailings le 9 juin
            ↓
CLIENT   → reçoit email, passe commande en mentionnant l'offre (sans code)
            ↓
VANESSA  → reçoit la commande, applique l'offre sur le devis Odoo
            (3+1 ou -10% selon segment) — pas de code à saisir
            ↓
JEROME   → appelle top 20 Revendeur + top 5 Horeca dormants à J+10
            ↓
NICOLAS  → J+30 reporting : croisement automatique "partners taggés MC-202606-*
            qui ont commandé entre 9 juin et 9 juillet" → liste conversions, CA, ROI
            → ajuste la campagne juillet (Collection Glacée) en fonction
```

---

## Points d'attention

1. **Pas de chevauchement** : un même partner = 1 seul tag (dedup déjà faite). Aucun client ne recevra 2 mailings différents.

2. **Bounces probables** : sur 116 dormants, attendre 5-10 bounces (emails obsolètes des contacts qui ont changé). Vanessa nettoiera la liste Odoo en parallèle.

3. **Anti-spam** : ne pas envoyer les 2 mailings dans la même minute. Stephan, planifie :
   - 9h00 → Revendeur dormant (105 destinataires)
   - 9h30 → Horeca dormant (11 destinataires)

4. **A/B testing** : si Mailchimp Pro le permet, tester 2 objets sur 10-20% de la base Revendeur dormant (105 = campagne principale) — l'objet gagnant part au reste.

5. **Pas d'envoi aux Horeca actifs** : les 178 cafés/restos qui commandent activement ne reçoivent RIEN cette campagne (décision Nicolas : éviter la cannibalisation, ils commandent déjà). Ils restent en base, on les sollicitera plus tard avec une mécanique adaptée.

6. **Limite du tracking sans code** : si un client transfère le mail à un copain qui n'est pas dans la liste, on ne le saura pas. Acceptable car volume marginal sur 116 dormants.

---

## Prochaine étape pour toi

1. Lis ce brief, dis-moi si l'angle / le ton / le calendrier te conviennent
2. Si OK, on bloque un point de 30 min cette semaine pour aligner sur les visuels
3. Tu peux déjà commencer à brainstormer les objets email et les accroches

---

**Fichiers de référence** :
- CSV Mailchimp (à venir, sans colonne code promo) : `C:\Users\FlowUP\OneDrive\Teatower\data\mailchimp_juin_2026.csv`
- Roadmap complète : `Roadmap_B2B_2026-2027.pdf`
- Proposition offre juin : `Offre_Juin_2026_Proposition.pdf`
