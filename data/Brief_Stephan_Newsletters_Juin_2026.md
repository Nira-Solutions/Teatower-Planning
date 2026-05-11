# Brief Stephan — Newsletters Juin 2026

**À :** Stephan
**De :** Nicolas Raes
**Date :** 11 mai 2026
**Objet :** Lancement des 2 premières campagnes Mailchimp de la roadmap B2B 12 mois
**Envoi prévu :** mardi 9 juin 2026, 9h00

---

## Le contexte en 30 secondes

On démarre une **roadmap B2B sur 12 mois** (juin 2026 → mai 2027) avec un objectif simple : **+200 K€ de CA additionnel** sur la base actuelle de 881 K€. La mécanique : 1 ou 2 campagnes Mailchimp ciblées par mois, segment par segment (Horeca, Revendeur, GMS, Grossiste), avec une offre claire chacune.

Tu pilotes la partie newsletter Mailchimp de bout en bout. Moi je m'occupe des données Odoo (segmentation, tags, codes promo, tracking). Aurélie pilote la suite : commandes entrantes, encodage des codes promo, SAV. Jérôme appuie en relance commerciale J+10 sur les comptes prioritaires.

---

## Juin 2026 — 2 campagnes en parallèle

| Campagne | Cible | Volume | Offre | Tag Odoo | CA cible |
|---|---|---|---|---|---|
| **A — Horeca actif** | Cafés, restos, salons de thé qui commandent activement | 178 | 3+1 sur boîtes HC25 | `MC-202606-HORECA-ACTIF` | +5 K€ |
| **B — Horeca dormant** | Horeca qui n'a pas commandé depuis 6 mois | 11 | 3+1 sur boîtes HC25 + relance Jérôme | `MC-202606-HORECA-DORMANT` | +1 K€ |
| **C — Revendeur dormant** | Revendeurs qui n'ont pas commandé depuis 6 mois | 105 | -10% sur réassort libre ≥ 300€ | `MC-202606-REVENDEUR-DORMANT` | +8 K€ |
| **TOTAL** | | **294** | | | **+14 K€** |

*Note : ne pas confondre avec les chiffres initiaux de la roadmap (qui étaient 222 Horeca + 54 Revendeur dormant). Les chiffres ci-dessus sont la segmentation finale après dedup et filtrage strict (is_company + au moins 1 commande historique).*

---

## Le système de code promo (ESSENTIEL pour mesurer la conversion)

### Pourquoi un code promo ?

Sans code, on ne sait pas qui revient grâce à l'email vs qui aurait commandé de toute façon. Avec code, on mesure **exactement** :
- Combien de destinataires ont ouvert l'email → métrique Mailchimp
- Combien ont cliqué → métrique Mailchimp
- **Combien ont commandé (= ROI réel)** → tracking via le code mentionné dans le devis Odoo

### Format du code

**`TT-J26-XXXXXX`**

| Élément | Signification |
|---|---|
| `TT` | Teatower |
| `J26` | Juin 2026 (mois de la campagne) |
| `XXXXXX` | 6 caractères uniques par client (hash MD5 dérivé du partner_id Odoo) |

Exemples réels :
- `TT-J26-E96A7E` → ASBL Restaurants Universitaires (Horeca actif)
- `TT-J26-D08DA3` → ACR PETITJEAN Boulangerie THIBAUT (Revendeur dormant)
- `TT-J26-003405` → BELGALITA FOOD Brasserie Liégeoise (Horeca dormant)

Chaque client reçoit **son propre code unique**. Il ne peut pas être partagé.

### Comment l'insérer dans Mailchimp

1. Tu importes le CSV `data/mailchimp_juin_2026.csv` dans Mailchimp (colonnes : email, name, segment, promo_code, last_order_date, partner_id)
2. Tu crées un **merge field** `PROMO_CODE` dans l'audience Mailchimp (mappé sur la colonne CSV)
3. Dans le template email, tu insères le merge tag `*|PROMO_CODE|*` à l'endroit où tu veux afficher le code
4. Mailchimp remplace automatiquement par le code de chaque destinataire à l'envoi

Exemple de phrasing dans le mail :

> Votre code personnel pour bénéficier de l'offre : **`*|PROMO_CODE|*`**
> *Mentionnez-le simplement lors de votre commande.*

### Comment c'est tracké côté Odoo (rôle d'Aurélie)

Quand un client commande et mentionne son code :
1. Aurélie crée le devis Odoo comme d'habitude
2. **Elle saisit le code dans le champ "Référence client" du devis** (`client_order_ref`)
3. Plus tard, en fin de campagne (J+30), je lance une requête Odoo : "Quels SO ont une référence commençant par `TT-J26-` ?" → liste exhaustive des conversions

### Lookup d'un code (si client appelle sans contexte)

Le fichier CSV `data/mailchimp_juin_2026.csv` est la **source de vérité**. Ouvre-le dans Excel, Ctrl+F sur le code → tu trouves immédiatement le client, son segment, son email, son dernier achat.

---

## Les 3 templates à concevoir

### Template A — Horeca actif (178 destinataires)

**Ton** : Chaleureux, complice, "vous êtes nos partenaires, voici un petit boost été"
**Objet email proposé** : "Préparez votre saison estivale : 3 boîtes achetées, la 4ᵉ offerte 🍃"
**Angle** : C'est l'été qui arrive, vos clients vont chercher des moments thé, on vous facilite la rotation
**CTA** : Commander (avec code) ou répondre à l'email pour passer commande à Aurélie
**Visuels** : terrasse, ambiance estivale, boîtes HC25 en mise en scène

**Contenu obligatoire** :
- Rappel offre : 3 boîtes achetées = 4ᵉ offerte, 1 réf au choix par tranche de 3
- Min 6 boîtes, port offert dès 200 €
- Valable juin uniquement
- Code personnel `*|PROMO_CODE|*`
- Mention "Pour toute question, répondez à cet email ou appelez Aurélie"

### Template B — Horeca dormant (11 destinataires)

**Ton** : "Vous nous manquez", retour aux fondamentaux, sincère mais pas larmoyant
**Objet email proposé** : "Cela fait un moment... 3+1 pour reprendre tranquillement ?"
**Angle** : On a remarqué qu'on ne s'est plus parlé. Voici une offre pour reprendre contact sans pression.
**Particularité** : Jérôme va appeler le top 5 de cette liste à J+10 si pas de retour

**Contenu obligatoire** :
- Même offre que Template A (3+1 HC25, port offert 200€, valable juin)
- **Phrase d'accroche dédiée** : "Nous avons remarqué que cela fait quelques mois que nous ne nous sommes pas parlés..."
- Code personnel `*|PROMO_CODE|*`
- Mention "Jérôme reste à votre disposition pour un échange, n'hésitez pas"

### Template C — Revendeur dormant (105 destinataires)

**Ton** : Libre, respectueux, "vous choisissez ce que vous voulez", pas une opé promo classique
**Objet email proposé** : "Reprenons contact — votre choix, -10% sur toute la gamme 🍵"
**Angle** : Pas de SKU forcé, pas de pack imposé. C'est *votre* réassort, à *votre* rythme. Juste -10% pour reprendre tranquillement.
**Particularité** : Jérôme va appeler le top 20 (CA historique ≥ 2 K€) à J+10

**Contenu obligatoire** :
- Offre : **-10% sur toute commande ≥ 300 €**, frais de port offerts dès 250 €
- 1 commande maximum par client, valable juin uniquement
- **Phrase d'accroche dédiée** : "Cela fait un moment que nous n'avons plus eu de vos nouvelles. Plutôt que vous proposer un assortiment imposé, nous vous laissons carte blanche..."
- Code personnel `*|PROMO_CODE|*`
- Lien vers le catalogue produits (page Shopify pro)

---

## Calendrier de production

| Date | Échéance | Qui |
|---|---|---|
| **11 mai (fait)** | Roadmap validée + tags Odoo posés + CSV généré | Nicolas |
| **15 mai (J-25)** | Brief créatif validé (objets, angles, visuels) | Stephan + Nicolas |
| **20 mai (J-20)** | Import CSV dans Mailchimp + création des 3 audiences | Stephan |
| **25 mai (J-15)** | Premiers drafts des 3 templates Mailchimp | Stephan |
| **27 mai (J-13)** | Revue templates + ajustements | Nicolas |
| **2 juin (J-7)** | Envoi de test interne (à nicolas@, aurelie@, stephan@, jerome@) | Stephan |
| **3 juin (J-6)** | Brief Jérôme : liste top 20 Revendeur + top 5 Horeca dormants | Nicolas |
| **9 juin 9h00 (J)** | **Envoi des 3 campagnes (par segment)** | Stephan |
| **12 juin (J+3)** | Relance Mailchimp aux non-ouvreurs (objet alternatif) | Stephan |
| **19 juin (J+10)** | Appels relance Jérôme top 20 + top 5 | Jérôme |
| **9 juillet (J+30)** | Reporting CA + ROI campagne (data-bi) | Nicolas |

---

## KPI à tracker

### Métriques Mailchimp (que tu nous remontes)

| Métrique | Cible |
|---|---|
| Taux d'ouverture moyen sur les 3 campagnes | ≥ 35% (sectoriel B2B premium) |
| Taux de clic moyen | ≥ 8% |
| Désabonnements | < 0,5% |
| Bounces | < 2% (sinon = email list à nettoyer) |

### Métriques business (qu'on calcule via Odoo)

| Métrique | Cible |
|---|---|
| Commandes générées via code promo (3 campagnes confondues) | 23-28 |
| CA additionnel | +14 K€ |
| Réactivations Revendeur dormant | 13-15 sur 105 (~13%) |
| Réactivations Horeca dormant | 3 sur 11 (sur petit volume) |

---

## Workflow récap (qui fait quoi)

```
NICOLAS  → segmente Odoo, tag, génère codes promo, exporte CSV
            ↓
STEPHAN  → importe CSV Mailchimp, crée 3 audiences, designe 3 templates
            ↓                                  (avec merge tag *|PROMO_CODE|*)
            envoie les 3 mailings le 9 juin 9h00
            ↓
CLIENT   → reçoit email, voit son code, passe commande en mentionnant le code
            ↓
AURELIE  → reçoit la commande, saisit le code dans "Référence client" du devis Odoo
            ↓
JEROME   → appelle top 20 Revendeur + top 5 Horeca dormants à J+10
            ↓
NICOLAS  → J+30 reporting : requête Odoo "SO avec ref TT-J26-*", calcul CA, ROI
            → ajuste la campagne juillet (Collection Glacée) en fonction
```

---

## Points d'attention

1. **Pas de chevauchement** : un même partner = 1 seul tag (dedup déjà faite). Aucun client ne recevra 2 mailings différents.

2. **Bounces probables** : sur 294 destinataires, attendre 5-10 bounces (emails obsolètes). Aurélie nettoiera la liste Odoo en parallèle.

3. **Anti-spam** : ne pas envoyer les 3 mailings dans la même heure. Stephan, planifie :
   - 9h00 → Horeca actif (178 destinataires)
   - 9h30 → Revendeur dormant (105 destinataires)
   - 10h00 → Horeca dormant (11 destinataires)

4. **A/B testing** : si Mailchimp Pro le permet, tester 2 objets sur 10% de la base pour les 178 Horeca actifs (campagne la plus volumineuse) — l'objet gagnant part au 90% restant.

5. **Confidentialité des codes** : ne pas partager les codes dans des canaux publics (Slack ouvert, etc.). Si un client communique son code à un autre, le tracking se brise.

---

## Prochaine étape pour toi

1. Lis ce brief, dis-moi si l'angle / le ton / le calendrier te conviennent
2. Si OK, on bloque un point de 30 min cette semaine pour aligner sur les visuels
3. Tu peux déjà commencer à brainstormer les objets email et les accroches

---

**Fichiers de référence** :
- CSV Mailchimp : `C:\Users\FlowUP\OneDrive\Teatower\data\mailchimp_juin_2026.csv`
- Roadmap complète : `Roadmap_B2B_2026-2027.pdf`
- Proposition offre juin : `Offre_Juin_2026_Proposition.pdf`
