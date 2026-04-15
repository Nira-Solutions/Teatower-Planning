# Batch Facturation — Commandes à facturer — 2026-04-15

## Résumé exécutif

| Indicateur | Valeur |
|---|---|
| SO scannés (action 358 Odoo) | **85** |
| Factures brouillon créées | **34** |
| Montant total HT facturé | **14 561,15 EUR** |
| Montant total TTC facturé | **15 461,18 EUR** |
| SO Amazon exclus | 36 (741,40 EUR HT) |
| SO à 0 EUR exclus | 5 |
| SO sans livraison exclus | 8 |
| Avoirs draft détectés (non comptés) | 2 |
| Erreurs création | 0 (fausse alarme XML-RPC résolue) |

Toutes les factures sont en **état brouillon (draft)**. Aucune n'a été postée. Nicolas doit valider manuellement avant envoi.

---

## Factures brouillon créées (34)

Mode : facturation sur quantités livrées (`qty_delivered`).

| # | ID Odoo | Commande | Client | HT (EUR) |
|---|---|---|---|---|
| 1 | DRAFT-36200 | S05398 | Chez Lison - Café Littéraire | 112,35 |
| 2 | DRAFT-36201 | S05396 | Van Der Valk Hotel Charleroi Airport | 242,50 |
| 3 | DRAFT-36202 | S05395 | ILLICO RESTO SRL | 90,00 |
| 4 | DRAFT-36203 | S05393 | Europadrinks - Drankenhandel Geert Swinnens | 825,00 |
| 5 | DRAFT-36204 | S05394 | Brasserie Maziers Srl | 187,50 |
| 6 | DRAFT-36205 | S05392 | Cafes Delahaut | 600,00 |
| 7 | DRAFT-36206 | S05389 | Sunparks Leisure N.V. - Inzake De Haan | 315,00 |
| 8 | DRAFT-36207 | S05386 | Delhaize Le Lion S.A — Affilié 048875 Sombreffe | 174,35 |
| 9 | DRAFT-36208 | S05385 | Delhaize Le Lion S.A — Affilié 043131 Fernelmont | 388,98 |
| 10 | DRAFT-36209 | S05384 | 2u S.A. - Carrefour Market Ciney | 367,84 |
| 11 | DRAFT-36210 | S05383 | Etablissements Schnongs - AD Ciney | 424,45 |
| 12 | DRAFT-36211 | S05379 | Ruiters Minina - Le Brunch de Ginette | 240,00 |
| 13 | DRAFT-36212 | S05378 | Ruiters Minina - Le Brunch de Ginette | 240,00 |
| 14 | DRAFT-36213 | S05377 | Cercle Historique Terre de Durbuy — La Maison des Mégalithes | 270,37 |
| 15 | DRAFT-36214 | S05376 | Passion Cuisine SRL - Au gré des saisons | 70,00 |
| 16 | DRAFT-36215 | S05368 | Café Ventuno | 1 200,00 |
| 17 | DRAFT-36216 | S05367 | Pascal CHERAIN | 29,05 |
| 18 | DRAFT-36217 | S05355 | Carrefour Belgium - Corporate Village | 794,44 |
| 19 | DRAFT-36218 | S05364 | Sorescol S.A. | 787,50 |
| 20 | DRAFT-36219 | S05363 | Moulins Burette s.a. | 1 406,12 |
| 21 | DRAFT-36220 | S05358 | Cafés Antillia | 690,00 |
| 22 | DRAFT-36221 | S05357 | Spinée SA | 256,13 |
| 23 | DRAFT-36222 | S05356 | Clotuche Caroline Suzanne | 28,00 |
| 24 | DRAFT-36224 | S05354 | The Torrefactory Project Sa | 1 950,00 |
| 25 | DRAFT-36225 | S05353 | All in One sprl - Nicolas Bissot | 230,00 |
| 26 | DRAFT-36226 | S05352 | SRL Tartine & Gourmandise | 140,00 |
| 27 | DRAFT-36227 | S05350 | Au Comptoir Local | 575,19 |
| 28 | DRAFT-36228 | S05344 | Administration communale de Marche | 115,06 |
| 29 | DRAFT-36229 | S05340 | Carrefour Belgium - Corporate Village | 435,86 |
| 30 | DRAFT-36230 | S05334 | SRL Le Tailvent - L'insolite | 60,00 |
| 31 | DRAFT-36231 | S05324 | Smart fridges srl - Frigo Loco | 480,00 |
| 32 | DRAFT-36232 | S05303 | Carrefour Belgium - Corporate Village | 416,06 |
| 33 | DRAFT-36233 | S05225 | Hôtel Le Beau Séjour | 42,99 |
| 34 | DRAFT-36234 | S05139 | Hello Bio sprl (Pure) | 376,41 |
| | | **TOTAL HT** | | **14 561,15** |

### Note Pascal CHERAIN (S05367) — livraison partielle
SO commandé à 224,52 EUR HT mais facturé à 29,05 EUR HT car la majorité des lignes
(`qty_delivered = 0`) ont déjà été facturées (`qty_invoiced > 0`) sur une facture précédente.
Seules les lignes restant à facturer (livré non encore facturé) sont incluses. A vérifier si cohérent.

---

## Avoirs draft détectés (2) — A examiner

Ces deux SO avaient déjà une facture postée et le wizard a généré un avoir en draft (type `out_refund`).
Ces avoirs ne sont PAS des factures et ne doivent pas être confondus. Nicolas doit décider de les valider ou annuler.

| ID Odoo | Commande | Client | Montant HT |
|---|---|---|---|
| DRAFT-36223 (avoir) | #48483 | ann philippe verhelle | 30,00 |
| DRAFT-36235 (avoir) | #46356 | Lidwine Fetten | 0,94 |

---

## Amazon exclus (36) — Pour information

Commandes détectées via `origin` contenant "Amazon Order". Non facturées.

| Commande | Client | HT (EUR) |
|---|---|---|
| S05125 | Kim PHAM-MOENS | 24,54 |
| S05124 | Aurelie Beaupain | 34,90 |
| S04599 | Dorine Masselus | 17,92 |
| S04598 | Christine HABAY | 17,92 |
| S04594 | gérimont wilfried | 17,92 |
| S04583 | Priscilla | 17,92 |
| S04577 | Hérion Charlotte | 17,92 |
| S04576 | Etienne Tack | 14,15 |
| S04575 | Florence Mathy | 14,15 |
| S04574 | Helga Verbiest | 26,41 |
| S04573 | Siciliano jessica | 17,92 |
| S04572 | Alexandre Annegarn | 13,20 |
| S04571 | Justine besohe | 14,15 |
| S04570 | reynaerts | 17,92 |
| S04560 | bricout candice | 17,92 |
| S04543 | julien wyns | 17,92 |
| S04542 | Mandy La Porta | 17,92 |
| S04541 | Dietrich Thibaut | 17,92 |
| S04534 | GANCI | 27,36 |
| S04525 | Angelino Carbone | 17,92 |
| S04524 | Louise Slivinski | 32,07 |
| S04523 | Ragoen | 17,92 |
| S04518 | Emmanuelle Breyne | 17,92 |
| S04512 | brogna giacomo | 17,92 |
| S04511 | celine van kerkhoven | 17,92 |
| S04510 | Isabelle Jadot | 17,92 |
| S04509 | Francesca Parrinello | 32,07 |
| S04488 | Serafima Kan | 28,30 |
| S04487 | Cimino | 28,30 |
| S04489 | Marie de Drée | 11,32 |
| S04473 | BADA Frederic | 14,15 |
| S04462 | Angélique Thérère | 28,30 |
| S04446 | Alexandre Grégoire | 14,15 |
| S04445 | Julie Hanrion | 22,64 |
| S04444 | Luiza Koziol | 28,30 |
| S04443 | Moreaux Cindy | 28,30 |
| | **Total Amazon HT** | **741,40** |

---

## SO à 0 EUR exclus (5)

| Commande | Client | Motif probable |
|---|---|---|
| S05400 | Laetitia Mariette | 0 EUR — offert / marketing |
| S05397 | Newpharma, Valentine Pavier | 0 EUR — offert / marketing |
| S05370 | Marketing Teatower | Usage interne |
| S05369 | Marketing Teatower | Usage interne |
| S05339 | Perte marchandise | Perte interne |

---

## SO sans livraison exclus (8)

Commandes confirmées mais `qty_delivered = 0` sur toutes les lignes. Rien à facturer.

| Commande | Client | HT (EUR) |
|---|---|---|
| S05382 | NDB Diffusion - Spar Namur | 346,67 |
| S05381 | BTL SRL - Break Time | 1 132,08 |
| S05403 | Brasserie - Restaurant Volle Gas | 110,00 |
| S05402 | La Thé Box | 305,13 |
| S05401 | Virelles Nature | 255,12 |
| S05380 | Lambertdis SRL - Spar Manhay | 581,14 |
| S05375 | Carrefour Market Remouchamps | 173,78 |
| S05351 | Carrefour Belgium - Corporate Village | 499,30 |
| | **Total HT en attente livraison** | **3 403,22** |

---

## Erreurs

Aucune erreur de création. Une fausse alarme XML-RPC sur S05356 (Clotuche) due à une valeur `None`
dans la réponse du serveur — la facture DRAFT-36222 a bien été créée et vérifiée.

---

---

## Correction TRANSPORT + Posting + Envoi — 2026-04-15 (suite)

### Lignes TRANSPORT — Analyse complète

9 lignes TRANSPORT (produit id=7059, 10 EUR HT, TVA 21%, compte 700000) détectées sur l'ensemble des SO scannés.

| SO | Situation | Action |
|---|---|---|
| S05398 | qty_inv=1 — déjà dans INV/2026/02055 (batch) | Rien (déjà inclus) |
| S05396 | qty_inv=1 — déjà dans INV/2026/02056 (batch) | Rien (déjà inclus) |
| S05395 | qty_inv=1 — déjà dans INV/2026/02057 (batch) | Rien (déjà inclus) |
| S05376 | qty_inv=1 — déjà dans INV/2026/02069 (batch) | Rien (déjà inclus) |
| S05353 | qty_inv=1 — déjà dans INV/2026/02079 (batch) | Rien (déjà inclus) |
| S05352 | qty_inv=1 — déjà dans INV/2026/02080 (batch) | Rien (déjà inclus) |
| S05367 | qty_inv=1 — déjà facturé sur INV/2026/02018 (posted antérieur) | Rien |
| S05403 | qty_inv=0, SO sans livraison — Brasserie Volle Gas | **Facture créée : INV/2026/02089** |
| S05375 | qty_inv=0, SO sans livraison — Carrefour Remouchamps | **Facture créée : INV/2026/02090** |

**Lignes TRANSPORT ajoutées : 2 — Montant HT : 20,00 EUR (TTC : 24,20 EUR)**

---

### Factures postées (36)

Toutes les 36 factures ont été passées en statut `posted` via `action_post()`. Zéro échec.

| Indicateur | Valeur |
|---|---|
| Factures postées | **36** |
| dont batch original | 34 |
| dont nouvelles TRANSPORT | 2 |
| Montant total HT | **14 581,15 EUR** |
| Montant total TTC | **15 482,38 EUR** |
| Avoirs draft (36223, 36235) | Non postés — décision Nicolas |

Numéros attribués : INV/2026/02055 à INV/2026/02090 (hors avoirs).

| ID Odoo | N° Facture | Client | HT (EUR) | SO |
|---|---|---|---|---|
| 36200 | INV/2026/02055 | Chez Lison - Café Littéraire | 112,35 | S05398 |
| 36201 | INV/2026/02056 | Van Der Valk Hotel Charleroi Airport | 242,50 | S05396 |
| 36202 | INV/2026/02057 | ILLICO RESTO SRL | 90,00 | S05395 |
| 36203 | INV/2026/02058 | Europadrinks - Drankenhandel Geert Swinnens | 825,00 | S05393 |
| 36204 | INV/2026/02059 | Brasserie Maziers Srl | 187,50 | S05394 |
| 36205 | INV/2026/02060 | Cafes Delahaut | 600,00 | S05392 |
| 36206 | INV/2026/02061 | Sunparks Leisure N.V. | 315,00 | S05389 |
| 36207 | INV/2026/02062 | Delhaize Le Lion S.A — Affilié 048875 | 174,35 | S05386 |
| 36208 | INV/2026/02063 | Delhaize Le Lion S.A — Affilié 043131 | 388,98 | S05385 |
| 36209 | INV/2026/02064 | 2u S.A. - Carrefour Market Ciney | 367,84 | S05384 |
| 36210 | INV/2026/02065 | Etablissements Schnongs - AD Ciney | 424,45 | S05383 |
| 36211 | INV/2026/02066 | Ruiters Minina - Le Brunch de Ginette | 240,00 | S05379 |
| 36212 | INV/2026/02067 | Ruiters Minina - Le Brunch de Ginette | 240,00 | S05378 |
| 36213 | INV/2026/02068 | Cercle Historique Terre de Durbuy | 270,37 | S05377 |
| 36214 | INV/2026/02069 | Passion Cuisine SRL - Au gré des saisons | 70,00 | S05376 |
| 36215 | INV/2026/02070 | Café Ventuno | 1 200,00 | S05368 |
| 36216 | INV/2026/02071 | Pascal CHERAIN | 29,05 | S05367 |
| 36217 | INV/2026/02072 | Carrefour Belgium - Corporate Village | 794,44 | S05355 |
| 36218 | INV/2026/02073 | Sorescol S.A. | 787,50 | S05364 |
| 36219 | INV/2026/02074 | Moulins Burette s.a. | 1 406,12 | S05363 |
| 36220 | INV/2026/02075 | Cafés Antillia | 690,00 | S05358 |
| 36221 | INV/2026/02076 | Spinée SA | 256,13 | S05357 |
| 36222 | INV/2026/02077 | Clotuche Caroline Suzanne | 28,00 | S05356 |
| 36224 | INV/2026/02078 | The Torrefactory Project Sa | 1 950,00 | S05354 |
| 36225 | INV/2026/02079 | All in One sprl - Nicolas Bissot | 230,00 | S05353 |
| 36226 | INV/2026/02080 | SRL Tartine & Gourmandise | 140,00 | S05352 |
| 36227 | INV/2026/02081 | Au Comptoir Local | 575,19 | S05350 |
| 36228 | INV/2026/02082 | Administration communale de Marche | 115,06 | S05344 |
| 36229 | INV/2026/02083 | Carrefour Belgium - Corporate Village | 435,86 | S05340 |
| 36230 | INV/2026/02084 | SRL Le Tailvent - L'insolite | 60,00 | S05334 |
| 36231 | INV/2026/02085 | Smart fridges srl - Frigo Loco | 480,00 | S05324 |
| 36232 | INV/2026/02086 | Carrefour Belgium - Corporate Village | 416,06 | S05303 |
| 36233 | INV/2026/02087 | Hôtel Le Beau Séjour | 42,99 | S05225 |
| 36234 | INV/2026/02088 | Hello Bio sprl (Pure) | 376,41 | S05139 |
| 36236 | INV/2026/02089 | Brasserie - Restaurant Volle Gas (TRANSPORT) | 10,00 | S05403 |
| 36237 | INV/2026/02090 | Carrefour Market Remouchamps (TRANSPORT) | 10,00 | S05375 |

---

### Envois clients

Méthode : wizard `account.move.send.wizard` — Peppol si `invoice_sending_method='peppol'` + endpoint/EAS configurés, sinon email standard.

| Canal | Nb | Factures |
|---|---|---|
| Peppol | **14** | 36201, 36202, 36203, 36207, 36208, 36216, 36219, 36220, 36221, 36225, 36226, 36227, 36231, 36237 |
| Email | **21** | 36200, 36204, 36205, 36206, 36209, 36210, 36211, 36212, 36213, 36214, 36215, 36217, 36218, 36224, 36228, 36229, 36230, 36232, 36233, 36234, 36236 |
| Non envoyé | **1** | 36222 — Clotuche Caroline Suzanne : aucun email ni Peppol configuré |

**Total envoyé : 35/36. Échecs : 0.**

#### Partenaires Peppol (14 factures)

| N° Facture | Client | EAS / Endpoint |
|---|---|---|
| INV/2026/02056 | Van Der Valk Hotel Charleroi Airport | 0208 / 0477295923 |
| INV/2026/02057 | ILLICO RESTO SRL | 9925 / BE0773909253 |
| INV/2026/02058 | Europadrinks - Drankenhandel Geert Swinnens | 0208 / 0478743696 |
| INV/2026/02062 | Delhaize Le Lion S.A (048875) | 0208 / 0402206045 |
| INV/2026/02063 | Delhaize Le Lion S.A (043131) | 0208 / 0402206045 |
| INV/2026/02071 | Pascal CHERAIN | 9925 / BE0724351755 |
| INV/2026/02074 | Moulins Burette s.a. | 0208 / 0444216745 |
| INV/2026/02075 | Cafés Antillia | 9925 / BE0878423387 |
| INV/2026/02076 | Spinée SA | 0208 / 0453910906 |
| INV/2026/02079 | All in One sprl - Nicolas Bissot | 0208 / 0680877543 |
| INV/2026/02080 | SRL Tartine & Gourmandise | 0208 / 0508536158 |
| INV/2026/02081 | Au Comptoir Local | 0208 / 0767441234 |
| INV/2026/02085 | Smart fridges srl - Frigo Loco | 0208 / 0741376146 |
| INV/2026/02090 | Carrefour Market Remouchamps (TRANSPORT) | 9925 / BE0446634817 |

#### Action requise — Clotuche Caroline Suzanne

- Facture INV/2026/02077 (28,00 EUR HT) — postée mais non envoyée.
- Aucun email ni endpoint Peppol configuré sur le partenaire (id=122331).
- Nicolas doit ajouter l'email du client dans Odoo (partenaire 122331) et relancer l'envoi manuellement.

---

*Mis à jour le 2026-04-15 — Agent Compta Teatower*
