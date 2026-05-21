# Dossier AWEX — Coffrets cadeaux d'entreprise

**Date** : 2026-05-21
**Demande entrante** : Sherilyn Baltus, Admin Officer Export — AWEX
**Objet** : Offre 10 coffrets thé qualitatifs + tarif dégressif
**Statut** : Préparation offre — envoi piloté manuellement par Nicolas
**Pivot v3** : Mise en avant C0102 + grille plafonnée à –40 % + pas de personnalisation + délai 8 semaines hors stock

---

## 1. Fiche prospect

### Identité
- **Raison sociale** : AWEX — Agence Wallonne à l'Exportation
- **Type** : Agence parapublique wallonne (export / promotion économique)
- **VAT** : BE0267314479
- **Adresse** : Place Sainctelette 2, 1080 Bruxelles
- **Site** : awex.be / wallonia.be

### État dans Odoo
| Élément | Statut |
|---|---|
| Partner | **Existe** — `res.partner` id **2808** "Awex" |
| Contact historique | Marie DELINCE — m.delince@awex.be — 0493 64 29 44 (fiche doublon 5701) |
| Nouveau contact | **Sherilyn Baltus** — Admin Officer Export — *non créée* |
| Historique commandes | **Aucune** (jamais client) |
| Lead CRM | **Aucun** |

### À traiter post-validation Nicolas
1. Créer contact enfant `Sherilyn Baltus` sous partner 2808
2. Fusionner doublon 5701 (Marie Delince) → contact enfant de 2808
3. Créer `crm.lead "AWEX — 10 coffrets cadeaux entreprise"` — stade Qualification — assigné Jérôme
4. Créer devis Odoo draft

---

## 2. Angle commercial

**Storytelling** : Teatower = **maison wallonne** (Namur / Liège / Waterloo). AWEX = agence wallonne d'export. Mise en avant de l'ancrage local commun = différenciation immédiate face à toute offre concurrente nationale ou française. À tenir dans l'email et dans le devis.

**Profil acheteur** : institutionnel parapublic → attentes = sérieux, lisibilité fiscale HT/TTC, DDM claire, capacité de monter en volume si la commande s'étend à plus de bénéficiaires (délégations, partenaires étrangers en visite, événements export, etc.).

---

## 3. Catalogue retenu — 3 options

### ⭐ Option A — C0102 Assortiment Découverte *(MISE EN AVANT)*

| Champ | Valeur |
|---|---|
| Code interne | C0102 |
| Stock dispo | **108 u** (308 virtuel) ✅ |
| Prix de vente conseillé HT | 14,15 € |
| Prix de vente conseillé TTC (6 %) | ~15,00 € |
| Coût de revient (Cellmade) | 7,80 € *(reconstitué par `purchase`)* |
| Contenu | **8 thés Teatower × 3 sachets-échantillons = 24 sachets** : Oasis du Désert BIO, Vert Jasmin, Panier de Grand-Maman, Pêche de Vigne BIO, English Breakfast, Blue Earl Grey BIO, Sencha BIO, Lady Dodo |
| Packaging | Boîte carton imprimée Teatower (EM079) |
| DDM | 18-24 mois |
| Saisonnalité | All year |

**Pourquoi recommandé** : produit signature, contenu varié (8 saveurs) qui plait à un public corporate large, prix d'entrée accessible permettant à AWEX d'envisager du volume, stock immédiat 108 u (couvre la qté demandée).

### Option B — C0200 Coffret assortiment Matcha *(premium tendance)*

| Champ | Valeur |
|---|---|
| Code interne | C0200 |
| Stock dispo | **150 u** (175 virtuel) ✅ |
| Prix de vente conseillé HT | 55,66 € |
| Prix de vente conseillé TTC (6 %) | ~59,00 € |
| Coût std Odoo | 14,28 € |
| Contenu | 3 Doypacks vrac 50 g : Matcha japonais, Matcha Fruit de la passion, Matcha Biscuit |
| Packaging | Boîte cartonnée Soft Touch 20×12×8 cm (EM0108) |
| DDM | 18-24 mois |
| Saisonnalité | All year |

### Option C — C0106 Coffret Taste the World *(nouveau design 2026)*

| Champ | Valeur |
|---|---|
| Code interne | **C0106** (Odoo id 4263) — relancé avec nouveau packaging |
| Design | BAT imprimeur "Boite ronde_PRINT.pdf" (Google Drive, modifié 09/04/2026) |
| Lien Drive | https://drive.google.com/drive/u/1/folders/12A1l8uFyeDV_ELKfNW-cRwNBF8X5FJXK |
| Packaging | **Boîte métal ronde** Desjardins D0018, design "Collection gourmande / Belgian Tea House" |
| Contenu | **8 saveurs × 6 sachets = 48 sachets-enveloppes** : Earl Grey BIO, Sencha BIO, Vert Jasmin, English Breakfast, Oasis du Désert BIO, Pêche de Vigne BIO, Lady Dodo, Panier de Grand-Maman |
| Stock actuel | **–8 u** (rupture sur ancien design) → réappro à programmer |
| Prix de vente conseillé HT | 33,02 € (~35 € TTC) |
| Coût std Odoo | 0 € *(à fiabiliser via `purchase`)* |
| Délai | **8 semaines** (production à relancer avec nouveau BAT) |

---

## 4. Grille tarifaire dégressive — règle Nicolas 21/05/2026

> **Règle** : remise progressive de **–30 % à –40 %** sur le Prix de Vente Conseillé HT, par paliers 10 / 300 / 500 / 1000+.

### Grille proposée

| Qté | Remise sur PV conseillé |
|---|---|
| 10 | **–30 %** |
| 300 | **–33 %** |
| 500 | **–37 %** |
| 1000+ | **–40 %** |

### Application — Option A C0102 Assortiment Découverte (PV HT 14,15 €)

| Qté | Remise | Prix net HT/u | Total HT | Marge € | Marge % |
|---|---|---|---|---|---|
| 10 | –30 % | 9,91 € | 99,10 € | 2,11 € | **21 %** ✅ |
| 300 | –33 % | 9,48 € | 2 844 € | 1,68 € | **18 %** ✅ |
| 500 | –37 % | 8,91 € | 4 455 € | 1,11 € | **12 %** ✅ |
| 1000+ | –40 % | 8,49 € | — | 0,69 € | **8 %** ⚠️ |

> Marges calculées sur coût de revient reconstitué 7,80 € / coffret (assemblage Cellmade). **Profitable à tous les paliers** dans la nouvelle grille plafonnée à –40 %.

### Application — Option B C0200 Coffret Matcha (PV HT 55,66 €)

| Qté | Remise | Prix net HT/u | Total HT | Marge brute |
|---|---|---|---|---|
| 10 | –30 % | 38,96 € | 389,60 € | **63 %** |
| 300 | –33 % | 37,29 € | 11 187 € | **62 %** |
| 500 | –37 % | 35,07 € | 17 535 € | **59 %** |
| 1000+ | –40 % | 33,40 € | — | **57 %** |

> Marges calculées sur coût std Odoo 14,28 €. Marges très confortables sur tous les paliers.

### Application — Option C C0106 Taste the World (PV HT 33,02 €)

| Qté | Remise | Prix net HT/u | Total HT |
|---|---|---|---|
| 10 | –30 % | 23,11 € | 231,10 € |
| 300 | –33 % | 22,12 € | 6 636 € |
| 500 | –37 % | 20,80 € | 10 400 € |
| 1000+ | –40 % | 19,81 € | — |

⚠️ Coût std C0106 à 0 € dans Odoo → marges réelles à fiabiliser avant remise grosse qté. Risque similaire à C0102 (assemblage Cellmade × 48 sachets). À briefer `purchase` si AWEX accroche sur ce SKU.

---

## 5. Livraison & délais

| Cas | Délai | Tarif HT |
|---|---|---|
| Stock disponible immédiat | 3-5 jours ouvrables | 15,00 € forfait Bruxelles (offerte ≥ 500 € HT) |
| **Réapprovisionnement (hors stock)** | **8 semaines** | Idem |
| Retrait gratuit boutique | Sur RDV | Gratuit — Namur / Liège / Waterloo |

**Couverture stock vs paliers** :
- C0102 (108 u) : couvre 10 + 100 unités, **8 sem au-delà**
- C0200 (150 u) : couvre 10 + 140 unités, **8 sem au-delà**
- C0106 Taste the World : **8 sem dès la 1ʳᵉ unité** (rupture actuelle)

---

## 6. Email réponse — prêt à envoyer

```
Objet : Offre coffrets cadeaux d'entreprise — AWEX

Madame Baltus,

Nous vous remercions pour votre demande et avons le plaisir de vous adresser
notre proposition de coffrets de thé pour vos cadeaux d'entreprise.

En tant que maison wallonne de thés et infusions (Namur, Liège, Waterloo),
nous sommes particulièrement honorés de pouvoir vous accompagner sur ce projet
qui rejoint nos valeurs communes d'ancrage et de rayonnement de la Wallonie.

Nous vous proposons trois références de notre collection, à adapter selon
votre cible et votre budget :

──────────────────────────────────────────────────
OPTION A — COFFRET ASSORTIMENT DÉCOUVERTE (notre recommandation)
──────────────────────────────────────────────────
• 8 thés et infusions Teatower, 3 sachets-échantillons de chacun
  (24 sachets au total) :
   – Oasis du Désert BIO       – Blue Earl Grey BIO
   – Vert Jasmin               – Sencha BIO
   – Panier de Grand-Maman     – Lady Dodo
   – Pêche de Vigne BIO        – English Breakfast
• Boîte carton imprimée Teatower
• DDM : 18 mois minimum à compter de la livraison
• Prix de vente conseillé HT : 14,15 €
• Prix net AWEX HT (10 unités, -30 %) : 9,91 €
• Soit 10,50 € TTC (TVA 6 %)

──────────────────────────────────────────────────
OPTION B — COFFRET ASSORTIMENT MATCHA
──────────────────────────────────────────────────
• 3 Doypacks vrac de 50 g :
   – Matcha japonais
   – Matcha Fruit de la passion
   – Matcha Biscuit
• Boîte cartonnée Soft Touch (format 20×12×8 cm)
• DDM : 18 mois minimum
• Prix de vente conseillé HT : 55,66 €
• Prix net AWEX HT (10 unités, -30 %) : 38,96 €
• Soit 41,30 € TTC (TVA 6 %)

──────────────────────────────────────────────────
OPTION C — COFFRET « TASTE THE WORLD » (signature 2026)
──────────────────────────────────────────────────
• Boîte métal ronde collector, design « Belgian Tea House »
• 8 saveurs × 6 sachets = 48 sachets-enveloppes :
   – Earl Grey BIO             – Oasis du Désert BIO
   – Sencha BIO                – Pêche de Vigne BIO
   – Vert Jasmin               – Lady Dodo
   – English Breakfast         – Panier de Grand-Maman
• DDM : 18 mois minimum
• Prix de vente conseillé HT : 33,02 €
• Prix net AWEX HT (10 unités, -30 %) : 23,11 €
• Soit 24,50 € TTC (TVA 6 %)

──────────────────────────────────────────────────
TARIFICATION DÉGRESSIVE (applicable à toutes nos références)
──────────────────────────────────────────────────
   10 unités    : -30 % sur le prix de vente conseillé
  300 unités    : -33 %
  500 unités    : -37 %
 1000+ unités   : -40 %

À titre d'exemple sur l'Option A (Coffret Découverte) :
   10 unités    :   9,91 € HT / coffret  (99,10 € HT)
  300 unités    :   9,48 € HT / coffret
  500 unités    :   8,91 € HT / coffret
 1000+ unités   :   8,49 € HT / coffret

──────────────────────────────────────────────────
DÉLAIS DE LIVRAISON
──────────────────────────────────────────────────
• Stock disponible : 3 à 5 jours ouvrables
• Réapprovisionnement (au-delà du stock) : 8 semaines
• Retrait gratuit en boutique : Namur / Liège / Waterloo

──────────────────────────────────────────────────
LIVRAISON
──────────────────────────────────────────────────
• Bruxelles (Place Sainctelette) : 15,00 € HT forfait
  (offerte dès 500 € HT de commande)

──────────────────────────────────────────────────

Nous restons à votre entière disposition pour affiner cette proposition,
organiser une dégustation découverte de nos coffrets en boutique, ou répondre
à toute question complémentaire.

Bien cordialement,

Nicolas Raes
Teatower SA
Maison wallonne de thés et infusions
nicolas.raes@teatower.com
www.teatower.com
```

---

## 7. Données à valider / compléter avant envoi

- [x] ~~Taste the World~~ → C0106 refondu, BAT Drive validé 09/04/2026
- [x] ~~Coût C0102~~ → 7,80 € reconstitué via `purchase`
- [x] ~~Marge C0102 grille~~ → plafond –40 % garde 8 % de marge à 1000+
- [x] ~~Personnalisation~~ → retirée de l'offre
- [x] ~~Délai hors stock~~ → 8 semaines intégré
- [ ] **Email Sherilyn Baltus** : confirmer adresse exacte (probablement `s.baltus@awex.be`)
- [ ] **DDM lot C0200** : lire étiquette stock pour confirmer DLUO ≥ 18 mois
- [ ] **Coût std C0106 Taste the World** : à fiabiliser par `purchase` avant remise grosse qté
- [ ] **Réappro C0106** : briefer purchase + production pour relance avec nouveau BAT (boîtes D0018 + assemblage)
- [ ] **Update Odoo standard_price C0102 → 7,80 €** : sur GO Nicolas (corriger aussi EM079 et E0666)

---

## 8. Checklist post-validation Nicolas (sur GO)

1. **sales-crm** (write) :
   - Créer contact enfant Sherilyn Baltus sous partner 2808
   - Fusionner doublon 5701 → contact enfant 2808
   - Créer `crm.lead "AWEX — 10 coffrets cadeaux entreprise"` (Qualification, assigné Jérôme)
   - Activité de relance J+7 si pas de retour

2. **support-order** (write) :
   - Créer devis Odoo draft S0xxxx (partner 2808)
     - Ligne 1 : 10× C0102 à 9,91 € HT *(Option A mise en avant)*
     - Ligne 2 : Transport forfait 15 € HT
     - Note pied : grille dégressive 300/500/1000+ + délai 8 sem hors stock
     - Conditions paiement : 30 jours fin de mois (à confirmer)
     - Validité devis : 30 jours

3. **purchase + production** (si AWEX accroche sur C0106 ou monte en volume) :
   - Relancer commande boîtes D0018 + sachets
   - Briefer assemblage Cellmade avec nouveau BAT "Boite ronde_PRINT.pdf"
   - Évaluer faisabilité assemblage in-house si volume > 500 u pour préserver marge

---

*Dossier préparé par Nira — données Odoo extraites le 2026-05-21 — pivot v3 : C0102 mis en avant, grille –30/–40 plafonnée, sans personnalisation, délai 8 sem hors stock*
