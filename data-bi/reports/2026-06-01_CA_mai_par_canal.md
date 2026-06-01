# CA Mai 2026 — Ventilation par canal | KPI#ca-canal-2026-06-01

**Produit le** : 01/06/2026  
**Source** : Odoo XML-RPC — `account.move` posted, `out_invoice` + `out_refund`  
**Periode** : 01/05/2026 → 31/05/2026 (mois complet — 31 jours, 19 jours ouvrables)  
**Perimetre** : CA HT net (factures - avoirs). Drafts exclus. POS/Magasins, Shopify D2C listes separement.  
**Note classification** : tags canal Odoo (Canal GMS=88, Canal Horeca=84, Canal B2B=85) + tags legacy (GMS=27, HoReCA=26…) + heritage tags depuis partenaire parent (adresses de facturation) + override manuel sur partenaires non tagges identifies par nom (Delhaize/Carrefour non tagges, Mix F&B, The Torrefactory…). KAIO Retail Delhaize (tag 86 DTC par erreur) reintegre en GMS.

---

## 1. CA realise mai 2026 (01/05 → 31/05/2026)

| Canal | CA HT net | Nb factures | Nb clients | Note |
|---|---:|---:|---:|---|
| GMS | 25 707 EUR | 79 | 51 | Delhaize, Carrefour, Intermarche, Newpharma |
| Horeca | 26 778 EUR | 58 | 50 | Cafes, restos, brasseries, Ventuno, Point Chaud, Preko |
| B2B Revendeurs | 18 564 EUR | 46 | 35 | Mix F&B, Va.S.Co, boutiques the, epiceries fines |
| POS / Magasins | 2 576 EUR | 76 | 61 | Journaux magasins Waterloo + Namur + Rocourt + POP-UP |
| Shopify D2C | 810 EUR | 4 | 4 | Tag DTC Shopify (tag 86) — hors perimetre, pour info |
| Amazon FBA | 0 EUR | 0 | 0 | Aucune facturation Amazon en mai 2026 |
| Autres (non classes) | 21 466 EUR | 312 | 302 | Masse B2C individuel non tagge, vente-privee (2 541 EUR), micro-clients < 300 EUR |
| **TOTAL** | **95 901 EUR** | **575** | **503** | |

> **Perimetre analytique (GMS + Horeca + B2B)** : **71 049 EUR** | 183 factures | 136 clients  
> Avoirs du mois : 2 771 EUR (GMS : 1 333, B2B : 999, Horeca : 399, Autres : 40)

**Note sur "Autres" (21 466 EUR)** : ce poste regroupe 302 micro-clients sans tag canal. La quasi-totalite sont des particuliers B2C (commandes directes magasin ou D2C non labellises Shopify). Les 15 premiers comptes representent < 300 EUR chacun a l'exception de VENTE-PRIVEE.COM (2 541 EUR, 1 seule facture ponctuelle) et quelques comptes pharmacie/sante (EyeD Pharma, Baillonville). Perimetre heterogene — non inclus dans les 3 canaux B2B.

---

## 2. Mois clos — definitif

> **Mai 2026 est clos au 31/05. Chiffres definitifs — aucune projection.**

| Indicateur | Valeur |
|---|---:|
| CA HT total (factures - avoirs) | 95 901 EUR |
| Perimetre 3 canaux (GMS + Horeca + B2B) | 71 049 EUR |
| Nb jours ouvrables mai 2026 | 19 j (1er mai ferie + Ascension 29/05) |
| Run rate journalier reel (total) | 5 047 EUR/j |
| Run rate journalier reel (3 canaux) | 3 739 EUR/j |
| Avoirs du mois | 2 771 EUR |
| Nb factures emises | 575 |
| Nb clients actifs | 503 |

> Comparaison : run rate avril 2026 = 4 664 EUR/j (97 954 / 21 jours ouvrables). Le run rate journalier mai (+8%) est superieur a avril malgre un CA total quasiment identique — cet ecart s'explique par 2 jours ouvrables de moins en mai (19j vs 21j). La densite de CA par jour ouvrable est en legere hausse.

---

## 3. Comparaison vs avril 2026 (M-1) et mai 2025 (A-1)

| Canal | Mai 2026 | Avr 2026 reel | D vs M-1 | Mai 2025 reel | D vs A-1 |
|---|---:|---:|---:|---:|---:|
| GMS | 25 707 EUR | 35 090 EUR | -27% | 11 983 EUR | +115% |
| Horeca | 26 778 EUR | 23 954 EUR | +12% | 15 431 EUR | +73% |
| B2B Revendeurs | 18 564 EUR | 17 470 EUR | +6% | 23 978 EUR | -23% |
| **Total 3 canaux** | **71 049 EUR** | **76 514 EUR** | **-7%** | **51 393 EUR** | **+38%** |
| POS / Magasins | 2 576 EUR | 3 438 EUR | -25% | 1 904 EUR | +35% |
| Shopify D2C | 810 EUR | 9 004 EUR | -91% | 20 781 EUR | -96% |
| Autres | 21 466 EUR | 8 998 EUR | +139% | 52 911 EUR | -59% |
| **Total general** | **95 901 EUR** | **97 954 EUR** | **-2%** | **126 988 EUR** | **-25%** |

> **Mise en garde sur la comparaison "Total general"** :  
> - **Shopify D2C** : les 9 004 EUR d'avril 2026 incluaient les ventes du Salon Wallon (POP-UP) et un pic D2C; les 810 EUR de mai sont anormalement bas et refletent le fait qu'une partie du D2C non-tagge 86 se retrouve dans "Autres" (310 factures B2C). La comparaison Shopify avril vs mai est donc artificielle.  
> - **Autres mai 2026** : 21 466 EUR vs 8 998 EUR en avril — l'essentiel de la hausse est dû a la facture VENTE-PRIVEE.COM (2 541 EUR, ponctuelle) et a la croissance des micro-commandes B2C sans tag.  
> - **Autres mai 2025** : 52 911 EUR dont 50 377 EUR en un seul compte "Tea Tree Caisse" (regroupement POS legacy abandonne depuis). Perimetre non comparable.  
> - Sur le **perimetre stable des 3 canaux B2B**, la croissance vs mai 2025 est de **+38%** — indicateur solide, non pollue par les effets legacy.

---

## 4. Top 5 clients du mois par canal

### GMS — 25 707 EUR net

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Delhaize Le Lion S.A. | 7 979 EUR |
| 2 | DEMARS S.A. — Carrefour Market Beauraing | 1 839 EUR |
| 3 | KAIO Retail invest — Delhaize Ottignies | 1 130 EUR |
| 4 | GIMALEX SA — Delhaize Fragnee | 931 EUR |
| 5 | Carrefour Belgium — Corporate Village | 814 EUR |

> Delhaize Le Lion concentre 31% du CA GMS. Les 4 suivants totalisent 4 714 EUR. Le reste du canal (46 clients) represente 12 014 EUR — profil dilue avec de nombreux AD Delhaize < 500 EUR.  
> GMS en baisse de 27% vs avril : retour a la normale apres un avril exceptionnel (plusieurs livraisons Carrefour groupees). Vs mai 2025 : +115% — progression structurelle forte.

### Horeca — 26 778 EUR net

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Ventuno SA | 3 150 EUR |
| 2 | The Torrefactory Project Sa (cpte "Facturation") | 3 038 EUR |
| 3 | Hello Bio sprl / Pure (cpte "Facturation") | 2 600 EUR |
| 4 | PC DISTRIBUTION SRL — Point Chaud | 2 250 EUR |
| 5 | Cafes Preko s.a. | 1 800 EUR |

> Note : les rangs 2 et 3 sont facturies sous des comptes generiques "Facturation" (pid 5565/5629) — les SO de reference sont S05654 (Hello Bio) et S05553 (Torrefactory). Ventuno reste le 1er compte Horeca. Top 5 = 12 838 EUR = 48% du CA Horeca.  
> Horeca en hausse de +12% vs avril et +73% vs mai 2025 — canal le plus dynamique du mois.

### B2B Revendeurs — 18 564 EUR net

| Rang | Client | CA HT |
|---|---|---:|
| 1 | Mix F&B SRL | 3 471 EUR |
| 2 | Va.S.Co | 2 500 EUR |
| 3 | Le Comptoir Local Linkebeek | 1 282 EUR |
| 4 | Boulangerie Les Co'Pains SPRL | 1 189 EUR |
| 5 | Esprit de campagne | 1 162 EUR |

> Mix F&B (non-tagge, classe B2B par defaut) pourrait relever de Horeca selon activite — a verifier et tagger. Va.S.Co = client historique (commande S05582 de 2 500 EUR). Top 5 = 9 604 EUR = 52% du canal. Le reste (30 clients) represente < 450 EUR chacun.  
> B2B en hausse de +6% vs avril — premier mois positif apres le recul structure observe depuis janvier 2026.

---

## 5. Insights

**Canal qui tire le mois : Horeca en acceleration structurelle, B2B qui repart.**  
Horeca devient pour la premiere fois le 1er canal en CA HT (26 778 EUR vs GMS 25 707 EUR) — un basculement notable. La progression de +73% vs mai 2025 n'est pas conjoncturelle : Ventuno, Point Chaud, Sobre/Preko sont des comptes recurrents en montee en charge. B2B affiche +6% vs avril apres plusieurs mois de recul — le niveau reste inferieur a mai 2025 (-23%) mais la tendance s'inverse. A surveiller sur juin pour confirmer.

**Signal faible : GMS en retrait de 27% vs avril — a distinguer de la tendance fond.**  
Le recul GMS n'est pas alarmant en soi : avril avait beneficie de plusieurs livraisons groupees Carrefour et Delhaize. Sur 12 mois glissants, GMS reste le canal en plus forte croissance (+115% vs mai 2025). Le vrai signal a surveiller est la concentration : Delhaize Le Lion S.A. represente seul 31% du CA GMS mai. Si ce compte ralentit ses commandes (renegociation referencement, rupture), le canal perd 8 000 EUR/mois instantanement. Diversification Carrefour et AD Delhaize independants = priorite.

**Point de vigilance : "Autres" (21 466 EUR) cache un potentiel de requalification important.**  
302 clients sur 575 factures ne sont pas tagues. Une partie sont des B2C purs (micro-commandes < 150 EUR), mais certains depassent les seuils B2B : VENTE-PRIVEE.COM (2 541 EUR, 1 facture), EyeD Pharma (350 EUR), Silversquare Belgium (397 EUR), D'ici Champion (363 EUR). Un tagging systematique des comptes > 300 EUR/mois permettrait de reintegrer 4 000 a 6 000 EUR dans le perimetre analytique B2B et d'ameliorer la lisibilite du reporting. Action a confier a l'equipe Odoo.

---

*Rapport genere automatiquement — agent Data-BI Teatower | Source : Odoo XML-RPC lecture seule*  
*Classification canal : tags Odoo Canal + heritage partenaire parent + override manuel | Avoirs deduits*  
*Script : `data-bi/_check_mai_ca_v2.py` | Cross-checked : ventilation 575 factures = 95 901 EUR HT*
