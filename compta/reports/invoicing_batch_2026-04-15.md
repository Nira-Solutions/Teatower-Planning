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

*Généré le 2026-04-15 — Agent Compta Teatower*
