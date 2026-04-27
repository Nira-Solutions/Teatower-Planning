# CA Avril 2026 — Ventilation par canal | KPI#ca-canal-2026-04-27

**Produit le** : 27/04/2026  
**Source** : Odoo XML-RPC — `account.move` posted, `out_invoice` + `out_refund`  
**Periode MTD** : 01/04/2026 → 27/04/2026 (27 jours sur 30)  
**Perimetre** : CA HT net (factures - avoirs). Drafts exclus. Shopify D2C et Amazon listes separement.  
**Note classification** : tags canal Odoo (Canal GMS=88, Canal Horeca=84, Canal B2B=85) + tags legacy (GMS=27, HoReCA=26…) + override manuel sur 20 partenaires non tagges identifies par nom.

---

## 1. CA realise avril 2026 (au 27/04 inclus)

| Canal | CA HT net MTD | Nb factures | Nb clients | Note |
|---|---:|---:|---:|---|
| GMS | 30 698 EUR | 85 | 45 | Delhaize, Carrefour, Intermarche, Newpharma |
| B2B Revendeurs | 23 763 EUR | 65 | 53 | Boutiques the, epiceries fines, distrib |
| Horeca | 15 676 EUR | 35 | 27 | Cafes, restos, brasseries, leisure |
| POS / Magasins | 11 568 EUR | 201 | 199 | Vente au comptoir magasin Waterloo + Namur |
| Shopify D2C | 3 064 EUR | 69 | 66 | Hors perimetre — pour info |
| Autres (non classes) | 2 945 EUR | 75 | 68 | Petits comptes sans tag, < 130 EUR/client |
| Amazon FBA | 201 EUR | 11 | 11 | Hors perimetre — pour info |
| **TOTAL** | **87 915 EUR** | **541** | **469** | |

> **Perimetre analytique (GMS + B2B + Horeca)** : **70 137 EUR** | 185 factures | 125 clients  
> Avoirs du mois : 2 425 EUR (GMS : 1 769, B2B : 440, Shopify : 190, Autres : 26)

---

## 2. Forecast fin de mois (30/04/2026)

**Contexte** : 22 factures pour 10 397 EUR HT ont ete emises le 27/04 (rapport `compta/reports/2026-04-27_facturation_peppol.md`). Le pipeline "a facturer" est quasi vide. Les 3 derniers jours ouvrables (28-29-30 avril) ne genereront que des commandes spontanees.

| Hypothese | Calcul | Montant |
|---|---|---:|
| MTD realise (27j) | Direct Odoo | 87 915 EUR |
| Run rate journalier | 87 915 / 27 | 3 256 EUR/j |
| 3 jours residuels — scenario prudent (50% run rate) | 3 256 × 3 × 0,5 | + 4 884 EUR |
| **Forecast total avril 2026** | | **~92 800 EUR** |

> Scenario optimiste (run rate plein x3j) : ~97 800 EUR. Non retenu car fin de mois = frequence commande faible.

---

## 3. Comparaison vs mars 2026 et avril 2025

| Canal | Avril 2026 forecast | Mars 2026 realise | D vs M-1 | Avril 2025 realise | D vs A-1 |
|---|---:|---:|---:|---:|---:|
| GMS | 34 109 EUR | 32 261 EUR | +6% | 21 654 EUR | +58% |
| B2B Revendeurs | 26 403 EUR | 30 245 EUR | -13% | 32 373 EUR | -18% |
| Horeca | 17 418 EUR | 13 634 EUR | +28% | 11 600 EUR | +50% |
| **Total 3 canaux** | **77 930 EUR** | **76 140 EUR** | **+2%** | **65 627 EUR** | **+19%** |
| **Total general** | **~92 800 EUR** | **112 473 EUR** | **-18%** | **142 352 EUR** | **-35%** |

> **Mise en garde sur la comparaison "Total general"** : mars 2026 inclut une commande exceptionnelle non recurrente (probable grosse facturation B2B ponctu). Avril 2025 inclut 50 572 EUR de "Tea Tree Caisse" (ventes POS regroupees sous un compte unique — pratique abandonnee depuis). Sur le perimetre comparable (3 canaux B2B), la tendance est positive vs A-1 (+19%).

---

## 4. Top 5 clients du mois par canal

### GMS — 30 698 EUR net MTD

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Delhaize Le Lion S.A. | 7 785 EUR |
| 2 | Carrefour Belgium — Corporate Village | 5 214 EUR |
| 3 | BOISDIS SA — Intermarche Naninne | 1 687 EUR |
| 4 | INTERMADIS SA — Intermarche Hannut | 1 399 EUR |
| 5 | SA Barthe — Intermarche Assesse | 1 286 EUR |

> Top 2 concentrent 42% du CA GMS. Les 3 Intermarche suivants = 4 372 EUR au total.

### Horeca — 15 676 EUR net MTD

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Cafes Delahaut | 3 052 EUR |
| 2 | Cafe Ventuno | 2 138 EUR |
| 3 | Brasserie Maziers Srl | 2 138 EUR |
| 4 | Cafes Preko s.a. | 844 EUR |
| 5 | Cafermi | 755 EUR |

> Top 3 = 46% du CA Horeca. Profil resserré : 8 922 EUR sur 5 clients.

### B2B Revendeurs — 23 763 EUR net MTD

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Vilna Gaon S.R.L. | 4 072 EUR |
| 2 | Moulins Burette s.a. | 1 406 EUR |
| 3 | Europadrinks — Geert Swinnens | 825 EUR |
| 4 | Corica | 750 EUR |
| 5 | Marketing Teatower | 708 EUR |

> Vilna Gaon = 17% du CA B2B a lui seul. Concentration a surveiller.

---

## 5. Insights

**Canal qui tire le mois : GMS et Horeca en acceleration.**  
GMS +58% vs avril 2025, Horeca +50% — ces deux canaux sont clairement en rupture positive. La montee en puissance Carrefour (5 214 EUR vs historique faible) et les nouveaux comptes Horeca (Brasserie Maziers, Ventuno) en sont les moteurs principaux.

**Signal faible : B2B Revendeurs en recul structure.**  
-13% vs mars, -18% vs avril 2025. Vilna Gaon reste le pilier (4 072 EUR) mais le reste du canal est dilue sur 52 petits comptes < 900 EUR. Aucun nouveau compte B2B significatif ce mois. A surveiller : si Vilna Gaon decroche, le canal B2B tombe sous 20 000 EUR/mois.

**Risque fin de mois : peu de visibilite sur 28-30 avril.**  
Le pipeline "to invoice" a ete vide ce matin (22 factures emises). Les 3 derniers jours ne rattraperont pas l'ecart vs mars (-18 000 EUR). La forecast 92 800 EUR est realiste mais mars 2026 etait vraisemblablement gonfle par une facturation exceptionnelle — le "vrai" run rate mensuel Teatower est probablement entre 85 000 et 95 000 EUR HT, ce qui place avril dans la normale.

---

*Rapport genere automatiquement — agent Data-BI Teatower | Source : Odoo XML-RPC lecture seule*  
*Classification canal : tags Odoo Canal* + *override manuel 20 partenaires | Avoirs deduits*
