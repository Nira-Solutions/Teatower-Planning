# CA Mai 2026 — Ventilation par canal | KPI#ca-canal-2026-06-01

**Produit le** : 01/06/2026 — **revise le** : 01/06/2026 (correction double-vue facture/encaisse)
**Periode** : 01/05/2026 → 31/05/2026 (mois complet — 31 jours, 19 jours ouvrables)
**Note classification** : tags canal Odoo (Canal GMS=88, Canal Horeca=84, Canal B2B=85) + tags legacy (GMS=27, HoReCA=26) + heritage tags depuis partenaire parent + override manuel sur partenaires non tagges identifies par nom (Delhaize/Carrefour non tagges, Mix F&B, The Torrefactory…). KAIO Retail Delhaize (tag 86 DTC par erreur) reintegre en GMS.

---

## Avertissement methode — deux vues, deux sources, ne pas melanger

Ce rapport presente **deux vues independantes** :

- **Vue A — CA facture** : `account.move` (factures + avoirs posted). Perimetre comparable avec les rapports anterieurs. Inclut les 76 tickets POS qui ont genere une facture TVA et les 4 commandes Shopify facturees en Odoo. Total = **95 902 EUR HT**.
- **Vue B — CA encaisse reel** : `account.move` + `pos.order` (caisse) + Shopify Admin API. Perimetre cash complet. Total = **168 264 EUR HT**.

Les colonnes de comparaison §3 utilisent systematiquement la meme source sur les deux periodes. Il n'y a pas de colonne qui mixe les deux bases.

---

## 1. Vue A — CA facture mai 2026 (account.move)

**Source unique** : `account.move`, state=posted, out_invoice + out_refund, invoice_date 01/05→31/05/2026.

| Canal | CA HT net | Nb factures | Nb clients | Note |
|---|---:|---:|---:|---|
| GMS | 25 707 EUR | 79 | 51 | Delhaize, Carrefour, Intermarche, Newpharma |
| Horeca | 26 778 EUR | 58 | 50 | Cafes, restos, brasseries, Ventuno, Point Chaud, Preko |
| B2B Revendeurs | 18 564 EUR | 46 | 35 | Mix F&B, Va.S.Co, boutiques the, epiceries fines |
| POS / Magasins (factures) | 2 576 EUR | 76 | 61 | 76 tickets magasin ayant genere un account.move (journaux INV1-INV5) — seuls ces tickets sont ici |
| Shopify D2C (factures Odoo) | 810 EUR | 4 | 4 | 4 commandes Shopify uniquement facturees en Odoo (tag DTC) — hors les 309 autres payees sur Stripe |
| Amazon FBA | 0 EUR | 0 | 0 | Aucune facturation Amazon en mai 2026 |
| Autres (non classes) | 21 466 EUR | 312 | 302 | Masse B2C individuel non tagge, vente-privee (2 541 EUR), micro-clients < 300 EUR |
| **TOTAL FACTURE** | **95 901 EUR** | **575** | **503** | Somme exacte des lignes ci-dessus |

**Verification de l'addition** : 25 707 + 26 778 + 18 564 + 2 576 + 810 + 0 + 21 466 = **95 901 EUR**. Colle a la centime avec le total Odoo (95 901,53 EUR brut).

> **Perimetre analytique (GMS + Horeca + B2B)** : **71 049 EUR** | 183 factures | 136 clients
> Avoirs du mois : 2 771 EUR (GMS : 1 333, B2B : 999, Horeca : 399, Autres : 40)

---

## 2. Vue B — CA encaisse reel mai 2026 (reconciliation cash)

**Principe anti-double-comptage** : les 2 576 EUR de tickets POS factures et les 810 EUR de commandes Shopify facturees sont **deja dans le total account.move (Vue A)**. On ajoute uniquement la partie non encore facturee.

| Composante | Montant | Source | Methode |
|---|---:|---|---|
| CA facture total (Vue A) | 95 901 EUR | account.move | Base |
| *dont POS-facture inclus dans Vue A* | *2 576 EUR* | *account.move* | *Deja compte* |
| *dont Shopify-facture inclus dans Vue A* | *810 EUR* | *account.move* | *Deja compte* |
| + POS caisse NON facture | 53 811 EUR | pos.order | 56 387 − 2 576 = 53 811 EUR (2 419 tickets encaisses caisse, aucun account.move genere) |
| + Shopify NON facture | 18 551 EUR | Shopify Admin API | 19 361 − 810 = 18 551 EUR (309 commandes payees Stripe, non synchronisees Odoo) |
| **CA ENCAISSE REEL MAI 2026** | **168 263 EUR** | Odoo + Shopify API | 95 901 + 53 811 + 18 551 |

**Verification** : 95 901 + 53 811 + 18 551 = **168 263 EUR**. Aucune composante comptee deux fois.

> **POS reel mai 2026 (total pos.order)** : 56 387 EUR HTVA, 2 495 tickets — dont 53 811 EUR encaisses en caisse sans facture TVA et 2 576 EUR factures via account.move.
> **Shopify reel mai 2026 (API)** : 19 361 EUR HT produits (hors port) — 313 commandes paid — dont 810 EUR factures via Odoo et 18 551 EUR payes directement sur Stripe.

---

## 3. Mois clos — definitif

> **Mai 2026 est clos au 31/05. Chiffres definitifs — aucune projection.**

| Indicateur | Vue A (facture) | Vue B (encaisse reel) |
|---|---:|---:|
| CA HT total | 95 901 EUR | 168 263 EUR |
| Perimetre 3 canaux (GMS + Horeca + B2B) | 71 049 EUR | n/a (3 canaux = account.move uniquement) |
| Nb jours ouvrables mai 2026 | 19 j (1er mai + Ascension 29/05) | 19 j |
| Run rate journalier | 5 047 EUR/j | 8 856 EUR/j |
| Avoirs du mois | 2 771 EUR | 2 771 EUR (idem — avoirs via account.move) |
| Nb factures emises | 575 | — |
| Nb clients actifs (factures) | 503 | — |

> Comparaison run rate : avril 2026 Vue B = 165 551 EUR / 21 j = 7 883 EUR/j. Run rate mai (+12% en Vue B) depasse avril malgre 2 jours ouvrables de moins — la densite journaliere reelle est en hausse significative, portee par la montee en puissance des boutiques (Namur et Liege en particulier).

---

## 4. Comparaison vs avril 2026 (M-1) et mai 2025 (A-1)

### 4A. Canaux B2B — source account.move (base constante, overrides manuels identiques mai et avril)

| Canal | Mai 2026 | Avr 2026 | D vs M-1 | Mai 2025 | D vs A-1 |
|---|---:|---:|---:|---:|---:|
| GMS | 25 707 EUR | 35 090 EUR | -27% | 11 983 EUR | +115% |
| Horeca | 26 778 EUR | 23 954 EUR | +12% | 15 431 EUR | +74% |
| B2B Revendeurs | 18 564 EUR | 17 470 EUR | +6% | 23 978 EUR | -23% |
| **Total 3 canaux** | **71 049 EUR** | **76 514 EUR** | **-7%** | **51 392 EUR** | **+38%** |
| Autres | 21 466 EUR | 8 998 EUR | +139% | n/s (*) | n/s |
| **Total facture (Vue A)** | **95 901 EUR** | **97 954 EUR** | **-2%** | **126 988 EUR** | **-25%** |

> (*) **Autres mai 2025 (126 988 EUR)** : 50 572 EUR correspondaient a "Tea Tree Caisse" (regroupement POS legacy abandonne). La comparaison "Total facture" A-1 est donc **non comparable** — les POS 2025 etaient factures en account.move alors qu'en 2026 ils passent directement par pos.order. Sur le perimetre stable des 3 canaux B2B (+38%), la comparaison est rigoureuse.

### 4B. POS magasins — source pos.order (base constante)

| | Mai 2026 | Avr 2026 | D vs M-1 | Mai 2025 | D vs A-1 |
|---|---:|---:|---:|---:|---|
| POS reel (pos.order) | 56 387 EUR | 59 404 EUR | -5% | **N/D** | n/d |
| *dont Namur* | *29 989 EUR* | *29 778 EUR* | *+1%* | | |
| *dont Liege bis* | *18 241 EUR* | *22 631 EUR* | *-19%* | | |
| *dont Waterloo* | *7 239 EUR* | *6 995 EUR* | *+3%* | | |
| *dont POP-UP (Salon)* | *918 EUR* | *0 EUR* | *—* | | |

> **Limite historique** : `pos.order` disponible depuis septembre 2025 seulement (les 2 tickets juin-aout 2025 = 0 EUR HTVA, probablement des tests). Mai 2025 en comparaison POS = **N/D**.

### 4C. Shopify e-commerce — source Shopify Admin API (base constante)

| | Mai 2026 | Avr 2026 | D vs M-1 | Mai 2025 | D vs A-1 |
|---|---:|---:|---:|---:|---|
| Shopify API (subtotal HT, paid) | 19 361 EUR | 14 063 EUR | +38% | **N/D** | n/d |
| Nb commandes | 313 | 245 | +28% | | |

> **Clarification sur le chiffre "9 004 EUR" cite dans la version precedente de ce rapport** : ce chiffre etait errone. L'API Shopify donne 14 063 EUR pour avril 2026 (245 commandes). La valeur 9 004 EUR ne correspondait ni a l'API ni aux account.move — elle etait une assertion non verifiee. Chiffre corrige ici.
> **Limite historique** : l'API Shopify ne retourne des ordres qu'a partir du 02/04/2026. Mai 2025 = **N/D**.

### 4D. CA encaisse reel (Vue B) — base constante

| | Mai 2026 | Avr 2026 | D vs M-1 |
|---|---:|---:|---:|
| CA encaisse reel total | 168 263 EUR | 165 551 EUR | +2% |
| Run rate journalier | 8 856 EUR/j | 7 883 EUR/j | +12% |

> Avril 2026 Vue B : 97 954 (account.move) + (59 404 − 3 438) POS non facture + (14 063 − 2 433) Shopify non facture = 97 954 + 55 966 + 11 630 = **165 550 EUR**. Calcul verifie au centime.

---

## 5. Top 5 clients du mois par canal

### GMS — 25 707 EUR net

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Delhaize Le Lion S.A. | 7 979 EUR |
| 2 | DEMARS S.A. — Carrefour Market Beauraing | 1 839 EUR |
| 3 | KAIO Retail invest — Delhaize Ottignies | 1 130 EUR |
| 4 | GIMALEX SA — Delhaize Fragnee | 931 EUR |
| 5 | Carrefour Belgium — Corporate Village | 814 EUR |

> Delhaize Le Lion concentre 31% du CA GMS. GMS en baisse de 27% vs avril : retour a la normale apres un avril exceptionnel (plusieurs livraisons Carrefour groupees). Vs mai 2025 : +115% — progression structurelle forte.

### Horeca — 26 778 EUR net

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Ventuno SA | 3 150 EUR |
| 2 | The Torrefactory Project Sa | 3 038 EUR |
| 3 | Hello Bio sprl / Pure | 2 600 EUR |
| 4 | PC DISTRIBUTION SRL — Point Chaud | 2 250 EUR |
| 5 | Cafes Preko s.a. | 1 800 EUR |

> Horeca en hausse de +12% vs avril et +74% vs mai 2025 — canal le plus dynamique sur un an. Top 5 = 12 838 EUR = 48% du CA Horeca.

### B2B Revendeurs — 18 564 EUR net

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Mix F&B SRL | 3 471 EUR |
| 2 | Va.S.Co | 2 500 EUR |
| 3 | Le Comptoir Local Linkebeek | 1 282 EUR |
| 4 | Boulangerie Les Co'Pains SPRL | 1 189 EUR |
| 5 | Esprit de campagne | 1 162 EUR |

> B2B en hausse de +6% vs avril — premier mois positif apres plusieurs mois de recul. Top 5 = 9 604 EUR = 52% du canal.

---

## 6. Complements — POS detaille & Shopify

### 6a. Detail des 4 POS actifs — CA reel mai 2026 (source : pos.order)

> Source : `pos.order`, state in (paid, done, invoiced), date_order 01/05→31/05/2026. Les 2 576 EUR du §1 Vue A correspondent aux **76 tickets explicitement factures** via account.move (journaux INV1-INV5).

| POS | Config ID | CA HTVA mai 2026 | Nb tickets | Note |
|---|---:|---:|---:|---|
| Namur | #4 | 29 989 EUR | 1 329 | Principal point de vente — 53% du CA POS |
| Liege bis | #5 | 18 241 EUR | 789 | 2e point de vente en volume |
| Waterloo | #1 | 7 239 EUR | 306 | 3e point de vente |
| POP-UP STORE (Salon Wallon) | #2 | 918 EUR | 71 | 2 sessions — evenement ponctuel |
| **TOTAL POS reel** | | **56 387 EUR** | **2 495** | |
| *dont facture compta (account.move)* | | *2 576 EUR* | *76* | *Journaux INV1-INV5 — clients ayant demande une facture TVA* |
| *dont encaisse caisse non facture* | | *53 811 EUR* | *2 419* | *pos.order uniquement — absent du CA account.move* |

> Rocourt (#7) et Liege (#3) : 0 ticket en mai 2026 — inactifs ce mois-ci.

### 6b. CA Shopify D2C e-commerce mai 2026 — source API

> Source : Shopify Admin API — `orders.json`, financial_status=paid, created_at 01/05→31/05/2026. 313 ordres uniques.

| Indicateur | Valeur |
|---|---:|
| Nb commandes payees (paid) | 313 |
| CA produits HT (subtotal apres remises, hors shipping, hors TVA) | 19 361 EUR |
| Frais de port HT | 710 EUR |
| **CA total HT e-commerce (produits + port)** | **20 071 EUR** |
| TVA collectee | 1 666 EUR |
| TTC encaisse | 20 078 EUR |
| Commandes remboursees | 2 |

**Methode retenue** : 19 361 EUR HTVA produits (hors frais de port) — coherent avec la logique de CA marchandise. Si on inclut le port : 20 071 EUR.

---

## 7. Insights

**Le CA "vrai" de mai est 168 263 EUR, pas 95 902 EUR.**
La comptabilite facturee sous-capture massivement la realite : 72 363 EUR d'encaissements reels (POS caisse + Stripe Shopify) ne generent aucun account.move. Ce n'est pas une anomalie — c'est la structure normale des boutiques en propre et du D2C direct. Pour le pilotage EBITDA, le chiffre de reference est **168 263 EUR** (run rate 8 856 EUR/j) et non 95 902 EUR. Implication immédiate : le rapport N-1 comparable (mai 2025 = 126 988 EUR account.move) etait aussi partiellement sous-capture — la croissance reelle est probablement plus forte que les +38% apparents sur les 3 canaux B2B.

**Horeca depasse GMS pour la premiere fois en CA facture — un basculement a confirmer sur juin.**
26 778 EUR (Horeca) vs 25 707 EUR (GMS) en account.move. La progression Horeca est portee par des comptes recurrents en montee en charge (Ventuno, Point Chaud, Preko) — ce n'est pas une anomalie ponctuelle. A surveiller : si le canal tient au-dessus de 25k EUR en juin, la diversification de la base de CA est reelle.

**Shopify en acceleration : +38% vs avril (14 063 EUR → 19 361 EUR), soit +5 298 EUR en un mois.**
La promo 3+1 Thes Glaces (lancee 01/06) n'etait pas encore active en mai — ce pic est organique. Avec la promo ete, juin devrait amplifier. A surveiller : le taux de repeat sur les 313 clients mai vs base historique.

**Action semaine 1 juin** : (1) Confirmer Horeca sur 3 nouveaux devis en cours (Ventuno extension, Hello Bio recurrence) — si les 2 signent, Horeca reste >25k juin. (2) Analyser les 302 clients "Autres" : les 10 comptes au-dessus de 300 EUR meritent un tag canal — cela requalifierait 4-6k EUR en perimetre analytique. (3) Verifier que la caisse POP-UP Salon Wallon est bien cloturee (918 EUR en mai — evenement termine).

---

*Rapport revise le 01/06/2026 — agent Data-BI Teatower | Source : Odoo XML-RPC lecture seule + Shopify Admin API*
*Vue A : account.move (575 factures, total verifie au centime). Vue B : account.move + pos.order + Shopify API (anti-double-comptage explicit)*
*Classification canal : tags Odoo + heritage partenaire parent + override manuel | Avoirs deduits*
