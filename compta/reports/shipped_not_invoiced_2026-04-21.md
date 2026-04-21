# Rapport commandes expédiées non facturées — 2026-04-21

Date de scan : 2026-04-21
Dernière run : 2026-04-15 (batch S05405–S05409 + 34 factures)

## Périmètre

- Source : sale.order (state: sale/done, invoice_status: to invoice)
- Total SO to_invoice trouvées : 86
- Exclus Amazon (origin "Amazon Order") : 36 SO
- Exclus 0 EUR (Marketing Teatower x2, Cafes Delahaut 0 EUR, Sefora Jacobs, Laetitia Mariette, Newpharma 0 EUR, Perte marchandise) : 7 SO
- Exclus sans picking outgoing done : 19 SO
- Exclus Marketing Teatower S05424 (707,55 EUR HT — partenaire interne, mis en review) : 1 SO

## SO candidates retenues — 23 SO, 20 factures générées

Odoo regroupe certains SO par partenaire (ex. S05410+S05414 -> Cafés Préko, S05431+S05422+S05439 -> Smartbox).

| SO | Partenaire | HT SO (EUR) | Notes |
|----|-----------|-------------|-------|
| S05351 | Carrefour Belgium - Corporate Village | 499,30 | Toutes lignes livrées |
| S05375 | Carrefour Market Remouchamps | 173,78 | Livraison partielle (I0859 non livré, corrigé) |
| S05380 | Lambertdis SRL - Spar Manhay | 581,14 | I0880 non livré, corrigé |
| S05381 | BTL SRL - Break Time | 1 132,08 | Toutes lignes livrées |
| S05382 | NDB Diffusion - Spar Namur | 346,67 | Reliquat : I0880 seul (21,80 EUR) |
| S05401 | Virelles Nature | 255,12 | I0376+I0880 non livrés, corrigés |
| S05402 | La Thé Box | 305,13 | Toutes lignes livrées |
| S05403 | Brasserie - Restaurant Volle Gas | 110,00 | Transport inclus |
| S05410 | Cafés Préko s.a. | 750,00 | Regroupé avec S05414 |
| S05413 | Delhaize Le Lion S.A | 346,08 | I0880 non livré, corrigé |
| S05414 | Cafés Préko s.a. | 94,34 | Regroupé avec S05410 |
| S05415 | DB Kfé SRL | 615,00 | Toutes lignes livrées |
| S05419 | Villa d'Olne | 100,00 | Transport inclus |
| S05420 | PGHM Distribution-Proxy Delhaize Maissin | 693,48 | Toutes lignes livrées |
| S05421 | Alcodis SA | 60,00 | Transport inclus |
| S05422 | Smartbox Group | 20,00 | Regroupé avec S05431+S05439 |
| S05423 | Clotuche Caroline Suzanne | 28,00 | Pas d'email ni Peppol |
| S05428 | Cafes Delahaut | 750,00 | Toutes lignes livrées |
| S05431 | Smartbox Group | 20,00 | Regroupé avec S05422+S05439 |
| S05432 | Le 7 by Juliette | 450,00 | Toutes lignes livrées |
| S05433 | Labrassine Brice - Le Walhère Roi | 110,00 | Transport inclus |
| S05438 | Sunparks Leisure N.V. - Inzake De Haan | 315,00 | Toutes lignes livrées |
| S05439 | Smartbox Group | 20,00 | Regroupé avec S05422+S05431 |

## SO en review (non facturées)

| SO | Partenaire | HT | Motif review |
|----|-----------|-----|-------------|
| S05424 | Marketing Teatower | 707,55 | Partenaire interne, coffrets usage marketing, facturation interne à confirmer par Nicolas |
| S05453 | Lambertdis SRL - Spar Manhay | 50,19 | Pas de picking outgoing done |
| S05452 | SA Barthe - Intermarché Assesse | 388,95 | Pas de picking outgoing done |
| S05451 | BOISDIS SA - Intermarché Naninne | 231,15 | Pas de picking outgoing done |
| S05450 | BOISDIS SA - Intermarché Naninne | 602,28 | Pas de picking outgoing done |
| S05449 | Windmill SA - Intermarché Bouge | 349,34 | Pas de picking outgoing done |
| S05448 | Delhaize Le Lion S.A (041345) | 447,73 | Pas de picking outgoing done |
| S05447 | NDB Diffusion - Spar Namur | 18,82 | Pas de picking outgoing done |
| S05444 | Brasserie Maziers Srl | 600,00 | Pas de picking outgoing done |
| S05445 | CPSP Belgie NV (Sunparks Kempense Meren) | 240,00 | Pas de picking outgoing done |
| S05442 | Hello Bio sprl (Pure) | 656,56 | Pas de picking outgoing done |
| S05440 | Next Cap SRL | 224,82 | Pas de picking outgoing done |
| S05436 | Delhaize Le Lion S.A (043366 Fosses) | 398,22 | Pas de picking outgoing done |
| S05435 | Floridis SA - Intermarché Floriffoux | 400,19 | Pas de picking outgoing done |
| S05434 | SRL Spydis - Intermarché Spy | 305,10 | Pas de picking outgoing done |
| S05429 | Pharmacie Tilman S.A. | 584,71 | Pas de picking outgoing done |
| S05404 | Gmp La Louvière - Delhaize La Louvière | 480,16 | Pas de picking outgoing done |
| S05426 | Intermarché Forest - FREYARVOR | 494,62 | Pas de picking outgoing done |
| S05425 | Gerpidis SA - Intermarché Gerpinnes | 632,65 | Pas de picking outgoing done |
| S05412 | Newpharma | 242,55 | Pas de picking outgoing done |

## Total candidats retenus HT (avant corrections lignes)

7 232,29 EUR HT | 7 680,93 EUR TTC (après correction lignes non-livrées)
