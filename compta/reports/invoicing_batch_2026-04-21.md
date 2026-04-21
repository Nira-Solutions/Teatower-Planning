# Rapport batch facturation — 2026-04-21

Date : 2026-04-21
Batch : S05351 / S05375 / S05380 / S05381 / S05382 / S05401 / S05402 / S05403 / S05410 / S05413 / S05414 / S05415 / S05419 / S05420 / S05421 / S05422 / S05423 / S05428 / S05431 / S05432 / S05433 / S05438 / S05439

## Résumé

- Factures créées et postées : 20
- Total HT : 7 232,29 EUR
- Total TTC : 7 680,93 EUR
- Peppol envoyés : 9 (statut : processing)
- Email envoyés : 9
- Non envoyés : 2 (Smartbox, Clotuche — pas d'email ni Peppol valide)

## Corrections appliquées avant posting

| Facture | Partenaire | Ligne supprimée | Raison |
|---------|-----------|-----------------|--------|
| INV/2026/02139 (36511) | Delhaize Le Lion | I0880 Blue Earl Grey (qty=4, 29,06 EUR) | qty_delivered=0 dans S05413 |
| INV/2026/02147 (36519) | Carrefour Market Remouchamps | I0859 Délice de Montélimar (qty=6, 43,59 EUR) | qty_delivered=0 dans S05375 |
| INV/2026/02150 (36522) | Virelles Nature | I0376 Coup de foudre (qty=5, 36,32 EUR) + I0880 (qty=5, 36,33 EUR) | qty_delivered=0 dans S05401 |
| INV/2026/02152 (36524) | Lambertdis SRL - Spar Manhay | I0880 Blue Earl Grey (qty=10, 72,66 EUR) | qty_delivered=0 dans S05380 |

Cause : le wizard sale.advance.payment.inv en mode "delivered" a inclus des lignes avec qty_delivered=0 (produit vraisemblablement en rupture / reliquat futur). Ces lignes ont été supprimées du draft avant posting.

## Partenaires Peppol forcés (invoice_sending_method -> peppol)

| Partenaire ID | Nom | Ancienne méthode | Nouvelle méthode |
|--------------|-----|-----------------|-----------------|
| 122944 | Lambertdis SRL - Spar Manhay | (vide) | peppol |
| 122958 | NDB Diffusion - Spar Namur | (vide) | peppol |
| 123067 | PGHM Distribution-Proxy Delhaize Maissin | (vide) | peppol |
| 3059 | Le 7 by Juliette | email | peppol |
| 123140 | Labrassine Brice - Le Walhère Roi | (vide) | peppol |

## Tableau des factures postées

| ID Odoo | Numéro | Partenaire | Origin SO | HT (EUR) | TTC (EUR) | Canal | UUID Peppol / Note |
|---------|--------|-----------|-----------|----------|----------|-------|---------------------|
| 36509 | INV/2026/02137 | Cafés Préko s.a. | S05410, S05414 | 844,34 | 895,00 | Peppol | 75ca7ecd-b4b3-4c0a-8309-f70ee2197004 |
| 36510 | INV/2026/02138 | DB Kfé SRL | S05415 | 615,00 | 651,90 | Peppol | 37eab94a-5f43-4fd3-afd5-66b3371f69dc |
| 36511 | INV/2026/02139 | Delhaize Le Lion S.A | S05413 | 317,02 | 336,01 | Peppol | 28e8393f-0d44-44f7-a78b-39c2934d71c1 |
| 36512 | INV/2026/02140 | La Thé Box | S05402 | 305,13 | 323,47 | Email | lisa.terrade@lathebox.fr |
| 36513 | INV/2026/02141 | Le 7 by Juliette | S05432 | 450,00 | 477,00 | Peppol | 90c3b497-e771-479e-9519-0725700f122d |
| 36514 | INV/2026/02142 | Smartbox Group | S05431, S05422, S05439 | 60,00 | 72,60 | Non envoyé | Peppol not_valid, pas d'email |
| 36515 | INV/2026/02143 | Alcodis SA | S05421 | 60,00 | 63,60 | Email | alcopay100@alcogroup.com |
| 36516 | INV/2026/02144 | Cafes Delahaut | S05428 | 750,00 | 795,00 | Email | compta@cafesdelahaut.be |
| 36517 | INV/2026/02145 | Sunparks Leisure N.V. | S05438 | 315,00 | 333,90 | Email | invoice.belgium@groupepvcp.com |
| 36518 | INV/2026/02146 | Brasserie - Restaurant Volle Gas | S05403 | 110,00 | 116,60 | Email | invoices.fc21@90folies.com |
| 36519 | INV/2026/02147 | Carrefour Market Remouchamps | S05375 | 130,19 | 138,00 | Email | ms.market066@outlook.com |
| 36520 | INV/2026/02148 | Carrefour Belgium - Corporate Village | S05351 | 499,30 | 529,30 | Email | produits_locaux@carrefour.com |
| 36521 | INV/2026/02149 | BTL SRL - Break Time | S05381 | 1 132,08 | 1 200,00 | Email | breaktimemediacite@gmail.com |
| 36522 | INV/2026/02150 | Virelles Nature | S05401 | 182,47 | 199,00 | Email | sebastien.pierret@aquascope.be |
| 36523 | INV/2026/02151 | Clotuche Caroline Suzanne | S05423 | 28,00 | 29,68 | Non envoyé | Peppol not_verified, pas d'email |
| 36524 | INV/2026/02152 | Lambertdis SRL - Spar Manhay | S05380 | 508,48 | 539,00 | Peppol | 06a1b47b-84b8-4f75-848f-d7a49ae036c5 |
| 36525 | INV/2026/02153 | NDB Diffusion - Spar Namur | S05382 | 21,80 | 23,11 | Peppol | cec483d4-562f-44f5-b0f2-1ae0571b4460 |
| 36526 | INV/2026/02154 | Villa d'Olne | S05419 | 100,00 | 106,00 | Peppol | a646b0b7-cea2-4415-a8d4-d0218d0154ff |
| 36527 | INV/2026/02155 | PGHM Distribution-Proxy Delhaize Maissin | S05420 | 693,48 | 735,16 | Peppol | d0829a62-e079-4f54-b7da-b2055d86363b |
| 36528 | INV/2026/02156 | Labrassine Brice - Le Walhère Roi | S05433 | 110,00 | 116,60 | Peppol | 3266785d-dc9e-46c1-a4fa-fcec98e76da7 |

**Total HT : 7 232,29 EUR | Total TTC : 7 680,93 EUR**

## Alertes et cas en review

### S05424 Marketing Teatower — MIS EN REVIEW (non facturé)
- Partenaire interne "Marketing Teatower"
- 434 coffrets Marrakech Sunset à 0 EUR (usage promo) + 49 coffrets à 14,15 EUR = 707,55 EUR HT
- Une ligne "subtotal=0" (prix remisé à 100%) et une ligne à prix normal sur même produit
- Action requise : Nicolas doit confirmer si ces 49 coffrets doivent être refacturés ou passés en sortie stock sans facturation

### Smartbox Group — INV/2026/02142 — Non envoyé
- 3 SO regroupées (S05431, S05422, S05439) — 60,00 EUR HT / 72,60 EUR TTC
- Peppol not_valid, aucun email renseigné sur le partenaire
- A envoyer manuellement depuis l'interface Odoo ou via contact Smartbox

### Clotuche Caroline Suzanne — INV/2026/02151 — Non envoyé
- 28,00 EUR HT / 29,68 EUR TTC
- Peppol not_verified, aucun email renseigné
- Déjà signalée comme sans canal lors du batch du 15/04
- A envoyer par courrier ou demander coordonnées email

## Dates

- invoice_date : 2026-04-21
- invoice_date_due : 2026-05-21 (30 jours)
- Format EDI Peppol : UBL BIS3

---

## Complement 5 SO — 2026-04-21 (run 2)

Date execution : 2026-04-21
SO factures : S05448, S05450, S05451, S05452, S05453

### Contexte

Ces 5 SO avaient ete exclues du batch principal (run 1) au motif "sans livraison done" (pickings outgoing not found). Nicolas a confirme les livraisons. Verification : tous les pickings sont de type `internal` (TT/PICK/08711, 08713, 08714, 08715, 08716), state=done, toutes les quantites livrees correspondent aux quantites commandees.

Le wizard `sale.advance.payment.inv` (mode delivered) echoue car il ne prend pas en compte les pickings de type internal. Les factures ont ete creees manuellement ligne par ligne en reprenant `qty_delivered` et `discount=30%` directement depuis les lignes SO.

### Controles pre-post

- Comptes : 700000 (Sales in Belgium) sur toutes les lignes produit — conforme au batch principal
- TVA : 6% (tax id=8) alimentaire, 21% (tax id=3) sur TRANSPORT
- Lignes EM0072 SRP Kraft Horeca : discount=100% conserve (subtotal=0) — offert, conforme au SO
- TRANSPORT : ajoute sur les 5 factures (10 EUR HT, TVA 21%, compte 700000)
- Echeance : +30j sauf Delhaize (delai 60j gere par Odoo automatiquement via payment term Delhaize)

### Tableau des 5 factures

| ID Odoo | Numero | Partenaire | Origin SO | HT (EUR) | TTC (EUR) | Canal | UUID Peppol |
|---------|--------|-----------|-----------|----------|----------|-------|-------------|
| 36540 | INV/2026/02163 | Delhaize Le Lion S.A | S05448 | 457,73 | 486,70 | Peppol | f7eb688b-9214-4a8b-98f8-f79d7da30066 |
| 36541 | INV/2026/02164 | BOISDIS SA - Intermarche Naninne | S05450 | 612,28 | 650,51 | Peppol | 700b53f5-0f18-4194-b6c8-1df4c3da4b94 |
| 36542 | INV/2026/02165 | BOISDIS SA - Intermarche Naninne | S05451 | 241,15 | 257,14 | Peppol | 0fb63a93-dd91-4f56-a4cf-98ea4cee4e39 |
| 36543 | INV/2026/02166 | SA Barthe - Intermarche Assesse | S05452 | 398,95 | 424,40 | Peppol | 26b4776f-6ac1-44ac-ad91-10d0fd26e293 |
| 36544 | INV/2026/02167 | Lambertdis SRL - Spar Manhay | S05453 | 60,19 | 65,30 | Peppol | d0ee1e08-6b97-4157-8c41-e06c29a79b1a |

**Total HT run 2 : 1 770,30 EUR | Total TTC run 2 : 1 884,05 EUR**

**Total HT run 2 : 1 770,30 EUR | Total TTC run 2 : 1 884,05 EUR**

**Total batch cumulé (run 1 + run 2) : 9 002,59 EUR HT | 9 564,98 EUR TTC**

---

## Complement S05434 — 2026-04-21 (run 3)

Date execution : 2026-04-21
SO facture : S05434

### Contexte

S05434 (SRL Spydis - Intermarche Spy) signalée par Nicolas comme livrée mais absente des runs 1 et 2. Cause confirmée : picking TT/PICK/08689 de type `internal` (state=done) — même pattern que S05448-53. Le wizard sale.advance.payment.inv ne détecte pas les pickings internal. Facture créée manuellement ligne par ligne.

### Controles pre-post

- Partenaire : SRL Spydis - Intermarche Spy (id=116686)
- Picking : TT/PICK/08689, type=internal, state=done
- Toutes les qty_delivered = qty_ordered (5, 6, 7, 7, 8, 6, 3, 3)
- Comptes : 700000 (id=320) sur toutes les lignes
- TVA : 6% (tax id=8) sur les 8 lignes produit (thes vrac + infusettes, alimentaire)
- TVA : 21% (tax id=3) sur TRANSPORT
- TRANSPORT : 10 EUR HT ajouté (livraison effective)
- Discount : 30% sur toutes les lignes produit (conforme SO)
- Echeance : 2026-05-21 (30 jours — payment term "30 Days" sur le partenaire)
- Journal : id=9, Customer Invoices

### Facture postée

| ID Odoo | Numero | Partenaire | Origin SO | HT (EUR) | TTC (EUR) | Canal | Etat Peppol |
|---------|--------|-----------|-----------|----------|----------|-------|-------------|
| 36545 | INV/2026/02168 | SRL Spydis - Intermarche Spy | S05434 | 315,10 | 335,51 | Peppol | processing |

Note HT : SO affichait 305,10 EUR (sans transport). Avec TRANSPORT 10 EUR HT : total facture = 315,10 EUR HT.

### Détail des lignes

| Produit | Qte | PU (EUR) | Disc | HT ligne |
|---------|-----|----------|------|----------|
| V0628 Oasis du désert BIO (100g vrac) | 5 | 9,434 | 30% | 33,02 |
| V0723 Namaste BIO (80g vrac) | 6 | 9,434 | 30% | 39,62 |
| V0279 Le panier de grand maman (80g vrac) | 7 | 9,434 | 30% | 46,23 |
| V0832 La Nana de Wepion (100g vrac) | 7 | 9,434 | 30% | 46,23 |
| V0914 Infusion du Printemps 2026 | 8 | 9,434 | 30% | 52,83 |
| I0121 Lady Dodo (20 infusettes) | 6 | 10,3774 | 30% | 43,59 |
| I0878 Guarana Boost (20 infusettes) | 3 | 10,3774 | 30% | 21,79 |
| I0631 Le the des amoureux (20 infusettes) | 3 | 10,3774 | 30% | 21,79 |
| TRANSPORT | 1 | 10,00 | 0% | 10,00 |

### Envoi Peppol

- Partner peppol_verification_state=valid avant ce run
- invoice_sending_method forcé à peppol (était False)
- Wizard account.move.send.wizard id=2913, format ubl_bis3
- peppol_move_state=processing apres action_send_and_print

### Total cumulé mis à jour

| Run | SO | Factures | HT (EUR) | TTC (EUR) |
|-----|-----|----------|---------|----------|
| Run 1 | 23 SO (20 regroupés) | 20 | 7 232,29 | 7 680,93 |
| Run 2 | S05448/50/51/52/53 | 5 | 1 770,30 | 1 884,05 |
| Run 3 | S05434 | 1 | 315,10 | 335,51 |
| **TOTAL** | | **26** | **9 317,69** | **9 900,49** |

### Statut envoi

- Toutes les 5 factures : peppol_move_state=processing (UBL BIS3)
- BOISDIS (36541, 36542) : adresse facturation 5506 peppol_verification_state=not_verified, mais le wizard a selectionne Peppol via invoice_sending_method du partenaire parent (2812, verification_state=valid) — envoi processing, a surveiller
- Delhaize (36540) : echeance 2026-06-20 (delai 60j configure sur le partenaire, non modifie)

### Remarques

- S05449 absent de la liste : non mentionne dans la demande Nicolas (probablement non livre)
- Aucune SO sans qty_delivered — les 5 confirmees sont toutes entierement livrees

---

## Complement S05435 + S05436 — 2026-04-21 (run 4)

Date execution : 2026-04-21
SO factures : S05435, S05436

### Contexte

S05435 (Floridis SA - Intermarche Floriffoux) et S05436 (Delhaize AD Fosses-la-Ville) signalees par Nicolas — meme pattern que runs 2 et 3 : picking de type `internal` (TT/PICK/08690 et TT/PICK/08691), state=done. Le wizard sale.advance.payment.inv ne detecte pas les pickings internal. Factures creees manuellement ligne par ligne.

### Controles pre-post

- S05435 : 9 lignes produit, toutes qty_delivered = qty_ordered (6 a 10 unites), disc=30%, TVA 6% (tax id=8)
- S05436 : 10 lignes produit, toutes qty_delivered = qty_ordered (3 a 10 unites), disc=30%, TVA 6% (tax id=8)
- Comptes : 700000 (id=320) sur toutes les lignes produit et TRANSPORT
- TRANSPORT : 10 EUR HT, TVA 21% (tax id=3), ajoutee sur les 2 factures
- Echeance S05435 : 2026-05-21 (30 jours — payment term "30 Days")
- Echeance S05436 : 2026-06-20 (60 jours — payment term "60 jours" Delhaize)
- Journal : id=9, Customer Invoices

### Tableau des 2 factures

| ID Odoo | Numero | Partenaire | Origin SO | HT (EUR) | TTC (EUR) | Canal | Etat Peppol |
|---------|--------|-----------|-----------|----------|----------|-------|-------------|
| 36556 | INV/2026/02169 | Floridis SA - Intermarche Floriffoux | S05435 | 410,19 | 436,31 | Peppol | processing |
| 36557 | INV/2026/02170 | Affilie 043366 - AD Fosses-la-Ville | S05436 | 408,22 | 434,22 | Peppol (not_verified) | processing |

Note HT S05435 : SO affichait 400,19 EUR (9 lignes produit). Avec TRANSPORT 10 EUR HT : total facture = 410,19 EUR HT.
Note HT S05436 : SO affichait 398,22 EUR (10 lignes produit). Avec TRANSPORT 10 EUR HT : total facture = 408,22 EUR HT.

### Detail lignes S05435 (Floridis - Intermarche Floriffoux)

| Produit | Qte | PU (EUR) | Disc | HT ligne |
|---------|-----|----------|------|----------|
| V0914 Infusion du Printemps 2026 | 10 | 9,434 | 30% | 66,04 |
| I0628 Oasis du desert - BIO (20 infusettes) | 6 | 10,3774 | 30% | 43,59 |
| I0631 Le the des amoureux (20 infusettes) | 4 | 10,3774 | 30% | 29,06 |
| I0669 Vert Jasmin (20 infusettes) | 3 | 10,3774 | 30% | 21,79 |
| I0751 I love you (20 infusettes) | 5 | 10,3774 | 30% | 36,32 |
| I0205 Etoiles filantes (20 infusettes) | 3 | 10,3774 | 30% | 21,79 |
| I0735 Peche de vigne - BIO (20 infusettes) | 8 | 10,3774 | 30% | 58,11 |
| I0723 Namaste BIO (20 infusettes) | 7 | 10,3774 | 30% | 50,85 |
| I0832 La Nana de Wepion (20 infusettes) | 10 | 10,3774 | 30% | 72,64 |
| TRANSPORT | 1 | 10,00 | 0% | 10,00 |

### Detail lignes S05436 (Delhaize AD Fosses-la-Ville)

| Produit | Qte | PU (EUR) | Disc | HT ligne |
|---------|-----|----------|------|----------|
| V0631 Le the des amoureux (80 g vrac) | 5 | 9,434 | 30% | 33,02 |
| V0878 Guarana Boost (100 g vrac) | 5 | 9,434 | 30% | 33,02 |
| V0205 Etoiles filantes (100 g vrac) | 8 | 9,434 | 30% | 52,83 |
| V0723 Namaste BIO (80 g vrac) | 4 | 9,434 | 30% | 26,42 |
| V0279 Le panier de grand maman (80 g vrac) | 5 | 9,434 | 30% | 33,02 |
| V0832 La Nana de Wepion (100 g vrac) | 5 | 9,434 | 30% | 33,02 |
| V0868 Citron meringue (100 g vrac) | 4 | 9,434 | 30% | 26,42 |
| V0914 Infusion du Printemps 2026 | 10 | 9,434 | 30% | 66,04 |
| I0751 I love you (20 infusettes) | 3 | 10,3774 | 30% | 21,79 |
| I0279 Le panier de grand maman (20 infusettes) | 10 | 10,3774 | 30% | 72,64 |
| TRANSPORT | 1 | 10,00 | 0% | 10,00 |

### Envoi

- S05435 Floridis : peppol_verification_state=valid, invoice_sending_method=peppol (deja configure). Wizard account.move.send.wizard id=2914, format ubl_bis3 — peppol_move_state=processing
- S05436 Delhaize AD Fosses : peppol_verification_state=not_verified, email=ad.fosses@hotmail.be. Odoo a selectionne Peppol automatiquement (wizard 2915). La facture a ete envoyee a l'acces Peppol (message chatter confirme). peppol_move_state=processing. A surveiller : si le reseau Peppol rejette (not_verified), relance email manuelle vers ad.fosses@hotmail.be depuis l'interface Odoo.

### Total cumule mis a jour

| Run | SO | Factures | HT (EUR) | TTC (EUR) |
|-----|-----|----------|---------|----------|
| Run 1 | 23 SO (20 regroupes) | 20 | 7 232,29 | 7 680,93 |
| Run 2 | S05448/50/51/52/53 | 5 | 1 770,30 | 1 884,05 |
| Run 3 | S05434 | 1 | 315,10 | 335,51 |
| Run 4 | S05435, S05436 | 2 | 818,41 | 870,53 |
| **TOTAL** | | **28** | **10 136,10** | **10 771,02** |
