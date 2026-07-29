# Revue lettrage ING — 29/07/2026

Script : `compta/lettrage_12_ing_20260729.py` (dry-run puis `--apply`).
Périmètre de départ : **49 lignes non lettrées sur BNK1** (ING BE30 3631 6408 2311) + les
miroirs BNK2 nécessaires aux virements internes.

Résultat : **BNK1 49 → 34** lignes à rapprocher, **BNK2 40 → 35**.
15 lignes ING traitées, aucune erreur, aucun lettrage à l'aveugle.

Règle d'écart appliquée (validée par Nicolas le 26/07, reconfirmée le 29/07) :
écart ≤ **5,00 €** → write-off `657100` (client a sous-payé) / `757100` (trop-perçu) ;
écart > 5,00 € → lettrage **partiel** sans write-off, jamais d'imputation forcée.

---

## A. Encaissements clients (4)

| BSL | Date | Montant | Client | Document(s) | Écart | Traitement |
|---|---|---|---|---|---|---|
| 19980 | 27/07 | 472,49 | SA Barthe - Intermarché Assesse | INV/2026/03139 (472,51) | **−0,02** | write-off `657100` → `MISC/26-27/07/0200` |
| 19981 | 27/07 | 305,91 | Wonka S.A. - Intermarché Heusy | INV/2026/03210 (305,90) | **+0,01** | write-off `757100` → `MISC/26-27/07/0201` |
| 19914 | 22/07 | 720,44 | Spar Vaux-sur-Sûre | INV/2026/03528 (680,54) + INV/2026/03512 (39,90) | 0,00 | lettrage exact sur 2 factures |
| 19815 | 16/07 | 111,55 | Faire.Com | INV/2026/02758 (127,20) | −15,65 | **partiel** — commission Faire retenue, 15,65 restent ouverts |

Les 4 lignes sont identifiées par communication structurée belge (`***000/0040/71370***`,
`***000/0041/09261***`, `***000/0042/65976***`) ou par IBAN émetteur.

**Spar Vaux-sur-Sûre** : le paiement de 720,44 correspond au *total* de INV/2026/03528, mais
cette facture portait déjà 39,90 lettrés. Les 39,90 excédentaires soldent exactement
INV/2026/03512 (39,90) émise le même jour — 680,54 + 39,90 = 720,44 pile.

**Faire** : écart de 15,65 = commission Faire retenue à la source. Au-delà de la tolérance de
5 €, donc **pas** de write-off : la facture reste `partial` avec 15,65 ouverts, à imputer en
commission quand le flux Faire sera repris à la racine (cf. `project_faire_flux_mal_impute`).

## B. Paiements fournisseurs (6)

| BSL | Date | Montant | Fournisseur | Document(s) | Preuve | Traitement |
|---|---|---|---|---|---|---|
| 19499 | 02/07 | −59,90 | SD Worx | RESA1152 (réf. 8705453) | libellé `1BT1014 87054530` + montant exact | soldé |
| 19808 | 16/07 | −82,64 | EZCharge / EasyPlug | RESA1141 | comm. structurée `***000/0267/48657***` | soldé |
| 19672 | 10/07 | −47,19 | Shyfter SA | RESA1165 (réf. 2026070568) | libellé carte `INVOICE 2026070568` | soldé |
| 19675 | 10/07 | −8 129,06 | Kirchner + Mount Everest | RESA853 + RESA852 + RESA847 + RESA854 | 1 631,79 + 5 922,67 + 433,60 + 141,00 = **8 129,06 pile** | soldé |
| 19806 | 16/07 | −2 545,24 | Kirchner | RESA748 + RESA747 | 401,64 + 2 143,60 = **2 545,24 pile** | soldé (voir ci-dessous) |
| 19477 | 01/07 | −110,63 | SD Worx | RESA1155 (réf. 8644575) | libellé `1BT1014 86445751` | **partiel** (acompte sur 16 979,07) |

**BSL 19675** : le libellé bancaire est tronqué par ING et ne cite que 3 des 4 factures
(`RGK 26-03222`, `RGK26-03223`, `RGK26-03268`). La 4ᵉ, `RGK26-03333` = 433,60, est déduite
par différence et tombe pile. Note : `RGK26-03223` (141,00) est facturée par **Mount Everest
Tea Company** (partenaire distinct de Kirchner) — le lettrage est multi-partenaires, ce qui
est correct puisque le prélèvement SEPA est unique.

**BSL 19806 — délettrage préalable assumé.** `RESA747` (RGK26-02511, 2 143,60) portait un
lettrage partiel de 199,41 avec la note de crédit `RBILL/26-27/07/0001` (GSK26-000261). Or le
relevé montre que Kirchner a prélevé la facture **pleine** (401,64 + 2 143,60) : la note de
crédit n'a donc **pas** été déduite. Le script a retiré cette imputation
(`account.move.line.remove_move_reconcile`) avant de lettrer. Conséquence voulue :
`RBILL/26-27/07/0001` redevient ouverte à hauteur de 199,41 et sera déduite d'un prélèvement
Kirchner ultérieur. C'est la réalité bancaire, attestée par le libellé du relevé.

**BSL 19477 — lettrage partiel.** La référence `8644575` correspond sans ambiguïté à RESA1155,
mais cette facture vaut 16 979,07 : les 110,63 sont un acompte. La ligne de relevé est soldée,
la facture passe en `partial` (16 868,44 ouverts). À noter : **SD Worx cumule ~136 k€ de
factures ouvertes** — problème systémique de non-lettrage des flux sociaux, à traiter à part.

## C. Virements internes BNK1 ↔ BNK2 (5 paires)

Les 2 lignes de relevé miroir sont repointées vers `580000 Internal Transfers of Funds`
(compte lettrable) puis lettrées entre elles. Solde net zéro, **aucun impact résultat**.

| ING | Belfius | Date | Montant | Sens |
|---|---|---|---|---|
| 19682 | 19664 | 10/07 | 500,00 | BNK2 → BNK1 |
| 19812 | 19756 | 16/07 | 300,00 | BNK2 → BNK1 |
| 19813 | 19757 | 16/07 | 2 000,00 | BNK2 → BNK1 |
| 19950 | 19917 | 24/07 | 1 000,00 | BNK2 → BNK1 |
| 19926 | 19890 | 23/07 | 5 800,00 | BNK1 → BNK2 |

---

## Non traité — 34 lignes ING restantes

### 1. Frais et cartes sans facture fournisseur encodée (15) → imputation OD, pas lettrage
Google Ads (19480 −437,07 / 19703 −500,00 / 19972 −500,00), Google Cloud (19607 −384,12),
Adobe (19638 −36,29 / 19728 −60,49), Shopify (19788 −526,99), Intuit (19639 −722,47),
Sendcloud (19780 −24,45), Worldline (19809 −529,78), Radius (19871 −308,80 / 19985 −459,81),
MIAMIO Faire (19853 −342,77), NCA Europe Faire (19857 −180,51), frais ING (19460 −2,25),
ING Mastercard (19804 −755,90).
→ Relèvent du script d'imputation de frais (`compta/od_frais_lettrage.py`), pas du lettrage.

### 2. Encaissements clients sans correspondance fiable (4) — **à statuer**
- **19466 NANRETAIL +675,58** — communication `***000/0038/68983***` = celle de INV/2026/02700,
  déjà payée. Ouvert chez ce client : 487,50 (INV/2026/03234, partielle) + 175,70
  (INV/2026/03627) = 663,20, soit 12,38 d'écart. Le client réutilise une vieille communication :
  aucune imputation certaine.
- **19660 ITM ALIMENTAIRE (Centrale Intermarché) +637,24** — 7 factures ouvertes
  (714,00 / 235,60 / 48,10 / 675,00 / 123,10 / 48,10 / 198,10). **Aucune** combinaison jusqu'à
  4 factures ne donne 637,24, même à 5 € près. Probable retenue centrale à documenter.
- **19784 Smartbox +67,00** — 50 factures ouvertes, aucune combinaison jusqu'à 3 factures ne
  donne 67,00. Les références du libellé (`PDN-001927257`, `PCI-001927370`) n'existent pas
  dans Odoo.
- **19952 DYNAMIC FOOD +436,84** — communication `***000/0040/30348***` = INV/2026/03067
  (521,54), **déjà soldée** par le relevé BSL 19768 du 15/07 (même communication). Le seul
  document ouvert est la note de crédit RINV/25-26/0342 (84,70), et 521,54 − 84,70 = **436,84**
  exactement. Deux lectures possibles : double paiement client, ou paiement du 15/07 mal imputé.
  Nécessite un arbitrage — ne pas lettrer en l'état.

### 3. Flux hors clients (5)
Baloise +79,51 (19630, indemnité accident du travail), Pluxee +124,95 (19652) et +33,28 (19771),
Edenred +17,59 (19826), iPiD +0,01 (19992, micro-dépôt de vérification bancaire — **ne pas**
lettrer contre INV/2026/02482 dont le résiduel de 0,01 n'est qu'une coïncidence).

### 4. Gros débits à documenter (10)
- **19625 Kirchner −12 837,54** — libellé `Siehe Avis vom 07.07.26`, aucune référence facture.
  Aucune combinaison jusqu'à 4 factures parmi les 55 ouvertes (185 341,75 € au total) ne tombe
  sur ce montant. **Il faut l'avis Kirchner du 07/07** pour trancher.
- 19811 ONSS −8 945,00 (comm. `***116/5516/51214***`, aucune facture correspondante)
- 19746 Douanes et Accises −1 040,40 (`970AI8902/F`)
- 19944 Proximus −200,00 (aucune facture Proximus de 200,00 ouverte)
- 19735 −1 574,53 — fichier de virements SEPA **groupé**, à éclater avant lettrage
- Avances salaires : 19610 −500,00 et 19739 −500,00 (Vansimpsen), 19737 −750,00 (van Ooteghem),
  19738 −1 000,00 (Cabosart) → comptes 421/430, pas du lettrage fournisseur
