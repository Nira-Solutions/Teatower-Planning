# Dossier AWEX — Coffrets cadeaux d'entreprise

**Date** : 2026-05-21
**Demande entrante** : Sherilyn Baltus, Admin Officer Export — AWEX
**Objet** : Offre 10 coffrets thé qualitatifs + tarif dégressif
**Statut** : Préparation offre — envoi piloté manuellement par Nicolas
**Pivot** : focus sur **C0102 Assortiment Découverte + C0200 Coffret Matcha + Taste the World**

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

### Option A — C0200 Coffret assortiment Matcha *(recommandé "premium signature")*

| Champ | Valeur |
|---|---|
| Code interne | C0200 |
| Stock dispo | **150 u** (175 virtuel) ✅ |
| Prix de vente conseillé HT | 55,66 € |
| Prix de vente conseillé TTC (6 %) | ~59,00 € |
| Coût std Odoo | 14,28 € |
| Contenu | 3 Doypacks vrac 50 g : Matcha japonais, Matcha Fruit de la passion, Matcha Biscuit |
| Packaging | Boîte cartonnée Soft Touch 20×12×8 cm (EM0108) |
| DDM | 18-24 mois (à confirmer sur lot) |
| Saisonnalité | All year |
| Personnalisation | Sticker boîte, carte insérée, ruban siglé |

### Option B — C0102 Assortiment Découverte *(volume / découverte)*

| Champ | Valeur |
|---|---|
| Code interne | C0102 |
| Stock dispo | **108 u** (308 virtuel) ✅ |
| Prix de vente conseillé HT | 14,15 € |
| Prix de vente conseillé TTC (6 %) | ~15,00 € |
| Coût std Odoo | non renseigné *(à fiabiliser)* |
| Contenu | 8 thés Teatower × 3 sachets-échantillons = **24 sachets** : Oasis du Désert BIO, Vert Jasmin, Panier de Grand-Maman, Pêche de Vigne BIO, English Breakfast, Blue Earl Grey BIO, Sencha BIO, Lady Dodo |
| Packaging | Boîte carton imprimée Teatower (EM079) |
| DDM | 18-24 mois |
| Saisonnalité | All year |
| Personnalisation | Carte insérée, sticker fenêtre boîte |

### Option C — Coffret Taste the World *(C0106 refondu — nouveau design)*

| Champ | Valeur |
|---|---|
| Code interne | **C0106** (Odoo id 4263) — relancé avec nouveau packaging |
| Design | BAT imprimeur "Boite ronde_PRINT.pdf" (Google Drive, modifié 09/04/2026) |
| Lien Drive | https://drive.google.com/drive/u/1/folders/12A1l8uFyeDV_ELKfNW-cRwNBF8X5FJXK |
| Packaging | **Boîte métal ronde** Desjardins D0018, design "Collection gourmande / Belgian Tea House" |
| Contenu | **8 saveurs × 6 sachets** = 48 sachets-enveloppes : Earl Grey BIO, Sencha BIO, Vert Jasmin, English Breakfast, Oasis du Désert BIO, Pêche de Vigne BIO, Lady Dodo, Panier de Grand-Maman |
| Stock actuel | **–8 u** (rupture sur ancien design) → réappro à programmer pour nouveau BAT |
| Prix de vente conseillé actuel | 33,02 € HT (~35 € TTC) — à valider sur le nouveau lot |
| Coût std Odoo | 0 € *(à fiabiliser via purchase)* |
| Personnalisation | Sticker logo AWEX collé sur boîte métal, ruban siglé, carte glissée |
| Disponibilité | Production à relancer (BAT validé 04/2026) — date à confirmer avec packaging/production |

**Positionnement** : boîte métal ronde = packaging très "cadeau corporate / collector", ancrage Liège fort (adresse imprimée Rue Saint-Paul 7), 48 sachets pour cuver longtemps le cadeau → fort potentiel sur AWEX. Mais nécessite **réappro avant livraison** (stock négatif).

**À briefer si AWEX accroche sur cette option** :
- `purchase` : relance commande boîtes D0018 + sachets enveloppes (Kirchner Fischer / Mount Everest)
- `production` : MO assemblage Cellmade pour la qté visée
- `product-data` : mettre à jour la fiche Odoo C0106 (description, photos du nouveau design, BoM si différente)

---

## 4. Grille tarifaire dégressive — règle Nicolas du 21/05/2026

> **Règle de base** : remise de 30 % sur le Prix de Vente Conseillé pour la qté demandée (10 u). Progression sur paliers 300 / 500 / 1000+, jusqu'à **45 %** pour 1000+.

### Grille proposée

| Qté | Remise sur PV conseillé |
|---|---|
| 10 | **–30 %** |
| 300 | **–35 %** |
| 500 | **–40 %** |
| 1000+ | **–45 %** |

### Application Option A — C0200 Coffret Matcha (PV conseillé HT 55,66 €)

| Qté | Remise | Prix net HT/u | Total HT | Marge brute estimée |
|---|---|---|---|---|
| 10 | –30 % | 38,96 € | 389,60 € | **70 %** |
| 300 | –35 % | 36,18 € | 10 854 € | **67 %** |
| 500 | –40 % | 33,40 € | 16 700 € | **64 %** |
| 1000+ | –45 % | 30,61 € | — | **53 %** ✅ |

> Marges calculées sur coût std Odoo 14,28 € — hors logistique, hors personnalisation. **C0200 reste rentable à tous les paliers.**

### Application Option B — C0102 Assortiment Découverte (PV conseillé HT 14,15 €) 🚨

Coût de revient reconstitué par `purchase` (BoM Odoo + supplierinfo) : **7,80 € / coffret** (scénario assemblage Cellmade/Prison de Marche — 7,05 € sachets + 0,75 € boîte EM079).

| Qté | Remise | Prix net HT/u | Marge € | Marge % | Verdict |
|---|---|---|---|---|---|
| 10 | –30 % | 9,91 € | 2,11 € | **21 %** | ✅ profitable |
| 300 | –35 % | 9,20 € | 1,40 € | **15 %** | ⚠️ acceptable |
| 500 | –40 % | 8,49 € | 0,69 € | **8 %** | ⚠️ très serré (transport offert peut basculer en perte) |
| 1000+ | –45 % | 7,78 € | –0,02 € | **–0,2 %** | 🟥 **POINT MORT / PERTE** |

**🚨 ALERTE — Décision Nicolas requise** :

L'assemblage Cellmade pèse 0,2936 € par sachet × 24 sachets = 7,05 € de pure main-d'œuvre par coffret, ce qui plombe la marge à grande qté. **Trois leviers possibles** :

1. **Plafonner la remise C0102 à –35 % (palier 500)** → reste profitable à tous les paliers, mais on perd l'argument "–45 % à 1000+" pour ce SKU
2. **Basculer l'assemblage in-house** (matière brute Kirchner ~3,95 € / coffret) → marge à 1000+ remonte à 49 % — nécessite arbitrage opérationnel (capacité atelier)
3. **Annoncer grille uniforme mais sortir C0102 du dégressif au-delà de 500 u** dans la note de bas de devis

→ Quelle option tu retiens ? Je peux briefer `production` pour évaluer la faisabilité d'un assemblage in-house si tu vises l'option 2.

### Application Option C — C0106 Taste the World (PV conseillé HT 33,02 €)

| Qté | Remise | Prix net HT/u | Total HT |
|---|---|---|---|
| 10 | –30 % | 23,11 € | 231,10 € |
| 300 | –35 % | 21,46 € | 6 438 € |
| 500 | –40 % | 19,81 € | 9 905 € |
| 1000+ | –45 % | 18,16 € | — |

⚠️ Marge réelle non calculable (coût std à 0 €). À fiabiliser par `purchase` avant remise grosse qté — même alerte que C0102 puisque le coût est dominé par 48 sachets-enveloppes × tarif assemblage (potentiellement encore plus pénalisant que C0102 si Cellmade).

---

## 5. Personnalisation (sur devis, en sus)

| Prestation | Prix HT/u | Conditions |
|---|---|---|
| Sticker logo AWEX sur boîte | 0,50 € | Dès 10 u |
| Carte cartonnée personnalisée recto/verso | 1,20 € | Dès 20 u |
| Ruban siglé AWEX | sur devis | Dès 50 u |
| Sur-emballage cadeau (papier kraft + nœud) | 1,80 € | sur demande |

## 6. Livraison

| Mode | Prix HT | Conditions |
|---|---|---|
| Livraison Bruxelles (Place Sainctelette) | 15,00 € forfait | **Offerte dès 500 € HT** |
| Délai standard | 3-5 jours ouvrables | Stock dispo |
| Retrait gratuit en boutique | 0 € | Namur / Liège / Waterloo |

---

## 7. Email réponse — prêt à envoyer

```
Objet : Offre coffrets cadeaux d'entreprise — AWEX

Madame Baltus,

Nous vous remercions pour votre demande et avons le plaisir de vous adresser
notre proposition de coffrets de thé pour vos cadeaux d'entreprise.

En tant que maison wallonne de thés et infusions (Namur, Liège, Waterloo),
nous sommes particulièrement honorés de pouvoir vous accompagner sur ce projet
qui rejoint nos valeurs communes d'ancrage et de rayonnement de la Wallonie.

Nous vous proposons deux références disponibles immédiatement, plus une
troisième en cours de conception que nous serions heureux de vous présenter
en avant-première.

──────────────────────────────────────────────────
OPTION A — COFFRET ASSORTIMENT MATCHA (recommandé)
──────────────────────────────────────────────────
• 3 Doypacks vrac de 50 g :
   – Matcha japonais
   – Matcha Fruit de la passion
   – Matcha Biscuit
• Boîte cartonnée Soft Touch (format 20×12×8 cm)
• DDM : 18 mois minimum à compter de la livraison
• Prix de vente conseillé HT : 55,66 €
• Prix net AWEX HT (10 unités, -30 %) : 38,96 €
• Soit 41,30 € TTC (TVA 6 %)

──────────────────────────────────────────────────
OPTION B — COFFRET ASSORTIMENT DÉCOUVERTE
──────────────────────────────────────────────────
• 8 thés et infusions Teatower, 3 sachets-échantillons de chacun :
   Oasis du Désert BIO, Vert Jasmin, Panier de Grand-Maman,
   Pêche de Vigne BIO, English Breakfast, Blue Earl Grey BIO,
   Sencha BIO, Lady Dodo
• Boîte carton imprimée Teatower
• DDM : 18 mois minimum
• Prix de vente conseillé HT : 14,15 €
• Prix net AWEX HT (10 unités, -30 %) : 9,91 €
• Soit 10,50 € TTC (TVA 6 %)

──────────────────────────────────────────────────
OPTION C — COFFRET « TASTE THE WORLD » (notre signature)
──────────────────────────────────────────────────
• Boîte métal ronde collector, design « Belgian Tea House »
• 8 saveurs × 6 sachets = 48 sachets-enveloppes :
   Earl Grey BIO, Sencha BIO, Vert Jasmin, English Breakfast,
   Oasis du Désert BIO, Pêche de Vigne BIO, Lady Dodo,
   Panier de Grand-Maman
• DDM : 18 mois minimum
• Prix de vente conseillé HT : 33,02 €
• Prix net AWEX HT (10 unités, -30 %) : 23,11 €
• Soit 24,50 € TTC (TVA 6 %)
• Nouveau design lancé en 2026 — délai de livraison à confirmer
  selon volumes (réapprovisionnement à programmer)

──────────────────────────────────────────────────
TARIFICATION DÉGRESSIVE (sur tous nos coffrets)
──────────────────────────────────────────────────
   10 unités    : -30 % sur le prix de vente conseillé
  300 unités    : -35 %
  500 unités    : -40 %
 1000+ unités   : -45 %

À titre d'exemple sur l'Option A (Coffret Matcha) :
   10 unités    :  38,96 € HT / coffret  (389,60 € HT)
  300 unités    :  36,18 € HT / coffret
  500 unités    :  33,40 € HT / coffret
 1000+ unités   :  30,61 € HT / coffret

──────────────────────────────────────────────────
PERSONNALISATION OPTIONNELLE
──────────────────────────────────────────────────
• Sticker logo AWEX sur boîte : 0,50 € HT/u (dès 10 u)
• Carte cartonnée personnalisée (recto/verso) : 1,20 € HT/u (dès 20 u)
• Ruban siglé AWEX : sur devis (dès 50 u)
• Sur-emballage cadeau : 1,80 € HT/u

──────────────────────────────────────────────────
LIVRAISON
──────────────────────────────────────────────────
• Bruxelles (Place Sainctelette) : 15,00 € HT forfait
  (offerte dès 500 € HT)
• Délai standard : 3 à 5 jours ouvrables pour le stock disponible
• Retrait gratuit possible en boutique (Namur / Liège / Waterloo)

──────────────────────────────────────────────────

Nous restons à votre entière disposition pour affiner cette proposition,
organiser une dégustation découverte de nos coffrets, ou ajuster les options
de personnalisation selon vos besoins.

Bien cordialement,

Nicolas Raes
Teatower SA
Maison wallonne de thés et infusions
nicolas.raes@teatower.com
www.teatower.com
```

---

## 8. Données à valider / compléter avant envoi

- [x] ~~Clarification Taste the World~~ → confirmé C0106 refondu, nouveau BAT "Boite ronde_PRINT.pdf" du 09/04/2026 (Drive)
- [x] ~~Coût std C0102~~ → reconstitué à **7,80 €** (scénario Cellmade) par `purchase`
- [x] ~~Grille dégressive~~ → simplifiée à 10/300/500/1000+ avec –30/–35/–40/–45%
- [ ] **🚨 Arbitrage marge C0102** : point mort à 1000+ unités → choisir option 1/2/3 *(cf. § 4 Option B)*
- [ ] **Email Sherilyn Baltus** : confirmer adresse exacte (probablement `s.baltus@awex.be` — sur le mail entrant)
- [ ] **DDM lot C0200** : lire étiquette stock pour confirmer DLUO ≥ 18 mois à la livraison
- [ ] **Coût std C0106 Taste the World** : fiabiliser via `purchase` avant de promettre la grille -45% à 1000+
- [ ] **Réappro C0106** : briefer purchase + production pour relancer boîtes D0018 + assemblage avec nouveau BAT
- [ ] **Update Odoo standard_price** : sur GO Nicolas, mettre 7,80 € sur C0102 + corriger E0666 + EM079 (`feedback_compta_no_pl_changes_without_approval` → demande accord)

---

## 9. Checklist post-validation Nicolas (sur GO)

1. **sales-crm** (write) :
   - Créer contact enfant Sherilyn Baltus sous partner 2808
   - Fusionner doublon 5701 → contact enfant 2808
   - Créer `crm.lead "AWEX — 10 coffrets cadeaux entreprise"` (Qualification, assigné Jérôme)
   - Activité de relance J+7 si pas de retour

2. **support-order** (write) :
   - Créer devis Odoo draft S0xxxx (partner 2808)
     - Ligne 1 : 10× C0200 à 38,96 € HT
     - Ligne 2 : Transport forfait 15 € HT
     - Note pied : grille dégressive 300/500/1000/1000+
     - Conditions paiement : 30 jours fin de mois (à confirmer)
     - Validité devis : 30 jours

3. **product-data + packaging + production** (si AWEX accroche sur Taste the World) :
   - Briefer la remise à plat ou la V2 selon ta réponse § 3 Option C

---

*Dossier préparé par Nira — données Odoo extraites le 2026-05-21 — grille dégressive selon directive Nicolas du 21/05/2026*
