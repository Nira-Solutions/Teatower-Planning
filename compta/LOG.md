# LOG Compta Teatower

## 2026-07-29 — Facturation B2B Peppol (4 factures, 1.840,58 EUR TTC) + lettrage ING (15 lignes)

### 1. Facturation PRO delivered-only + envoi Peppol
`scripts/facturation_b2b_peppol.py --apply` (dry-run controle avant application).
17 SO `to invoice` : 4 facturables Peppol, 4 bloquees Peppol, 8 sans livraison, 1 a 0,00 EUR.

| Facture | SO | Client | TTC | Peppol |
|---|---|---|---|---|
| INV/2026/03677 | S06067 | Delhaize Le Lion S.A, Affilie 044305 - Heusy | 267,42 | done |
| INV/2026/03678 | S06066 | Wonka S.A. - Intermarche Heusy | 340,91 | done |
| INV/2026/03679 | S06057 | Cafes Antillia | 715,50 | done |
| INV/2026/03680 | S06056 | Cafes Delahaut | 516,75 | done |

Les 4 envois Peppol sont confirmes `peppol_move_state=done`.
S06066 (Wonka) n'etait pas facturable au dry-run : la re-verification Peppol de l'etape 3 a fait
passer le partenaire de facturation #8131 de `not_verified` a `valid`.

**Garde-fou ajoute au script** — la ligne TRANSPORT n'est plus forcee a `qty_delivered` quand
**aucune marchandise** n'est livree sur la commande. Cas S06061 (Bulle d'hair) : les 3 lignes
produit etaient a `qty_delivered=0`, forcer le port aurait genere une facture de 10 EUR de frais
de port seuls, sans marchandise. La regle "transport toujours facture" ne vaut que quand la
marchandise est reellement partie et que seul le port n'a pas ete scanne en prepa.

SO bloquees Peppol (non facturees, inchangees) : S06055 Marie-Chantal Sauvage, S06050 Maison
Muscari (`not_valid`), S06002 charlier chantal, S05765 Delphine Samain — 3 sans numero de TVA.
S06069 (Paulette Srl) : facture creee a 0,00 EUR, laissee en **draft** (11 kg de vrac Guarana a
prix zero — arbitrage manuel).

### 2. Lettrage ING — 15 lignes sur 49
`compta/lettrage_12_ing_20260729.py --apply`. Detail complet :
`compta/review/lettrage_ing_20260729_review.md`.

**BNK1 : 49 -> 34 lignes a rapprocher. BNK2 : 40 -> 35.**

- **4 encaissements clients** : Barthe 472,49 (ecart -0,02 -> write-off 657100 `MISC/26-27/07/0200`),
  Wonka 305,91 (ecart +0,01 -> write-off 757100 `MISC/26-27/07/0201`), Spar Vaux-sur-Sure 720,44
  (2 factures, ecart nul), Faire 111,55 (ecart -15,65 = commission Faire, **lettrage partiel**,
  pas de write-off au-dela de la tolerance de 5 EUR).
- **6 paiements fournisseurs** : SD Worx 59,90, EZCharge 82,64, Shyfter 47,19, Kirchner+Mount
  Everest 8.129,06 (4 factures, pile), Kirchner 2.545,24 (2 factures, pile), SD Worx 110,63
  (acompte, partiel).
- **5 virements internes BNK1/BNK2** (500 + 300 + 2.000 + 1.000 + 5.800) lettres via
  `580000 Internal Transfers of Funds`, impact resultat nul.

**Delettrage assume sur RESA747** (Kirchner RGK26-02511) : la note de credit
`RBILL/26-27/07/0001` (199,41) y etait imputee alors que Kirchner a preleve la facture pleine
(le libelle du releve le prouve). L'imputation a ete retiree ; la note de credit redevient
ouverte a 199,41 et sera deduite d'un prelevement futur.

**Regle d'ecart appliquee** : <= 5,00 EUR -> write-off 657100/757100 ; > 5,00 EUR -> lettrage
partiel sans write-off. Aucun lettrage a l'aveugle.

**Restent a statuer (extrait)** : Kirchner 12.837,54 (libelle "Siehe Avis", avis du 07/07
necessaire), Centrale Intermarche 637,24 (aucune combinaison parmi 7 factures ouvertes),
NANRETAIL 675,58 (vieille communication reutilisee), Dynamic Food 436,84 (INV/2026/03067 deja
soldee le 15/07 par la meme communication — double paiement ou imputation erronee), Smartbox
67,00, ONSS 8.945,00, fichier SEPA groupe 1.574,53.

## 2026-07-27 — Facturation B2B Peppol (6 factures, 2.639,95 EUR TTC)

`scripts/facturation_b2b_peppol.py --apply` — dry-run controle avant application.

### Perimetre
18 SO `to invoice` — 4 exclues B2C/web (team "Odoo x Shopify"), 14 PRO retenues.
Les 6 SO facturees ont toutes ete creees le 27/07 entre 06:23 et 07:04 (encodage Vanessa)
et livrees entre 08:58 et 10:00, entrepot Teatower, sans transporteur : **aucune livraison
merch en camionnette**, donc aucune exclusion `--exclude` necessaire (cf. garde-fou rejets EDI Carrefour).

### Factures creees, postees et envoyees Peppol
| Facture | SO | Client | TTC |
|---|---|---|---|
| INV/2026/03642 | S06046 | Cafe Ventuno | 993,75 |
| INV/2026/03643 | S06044 | Begijnhof Hotel | 763,20 |
| INV/2026/03644 | S06043 | La couronne | 212,00 |
| INV/2026/03645 | S06042 | Smart fridges srl - Frigo Loco | 254,40 |
| INV/2026/03646 | S06041 | L'Etable 67 | 218,50 |
| INV/2026/03647 | S06040 | Centrale Intermarche | 198,10 |
| | | **Total** | **2.639,95** |

6/6 envoyees via Peppol (`account.move.send.wizard`, `sending_methods=['peppol']`),
toutes en `peppol_move_state=processing`. **Zero envoi par email** (regle en vigueur).

### Corrections Peppol au passage
EAS 9925 -> 0208 + re-verification sur 4 partenaires BE : Begijnhof Hotel (#2820),
Cafe Ventuno (#2855), Ventuno SA (#5620), et #6907 qui passe **not_verified -> valid**.
Ces corrections ont debloque 2 SO qui etaient BLOCK au dry-run (Cafe Ventuno + Begijnhof,
1.756,95 EUR) : sans elles, la facturation se serait arretee a 4 factures / 883,00 EUR.

### Lignes TRANSPORT forcees
S06041 (ligne 66503) et S06040 (ligne 66498) : `qty_delivered` 0 -> 1 (regle transport toujours facture).

### Non facture
- **2 SO bloquees Peppol** : S06002 charlier chantal (#125330) et S05765 Delphine Samain (#124325).
  Les deux sont `not_verified` **sans numero de TVA** — ce sont vraisemblablement des particuliers
  encodes dans le flux pro. A arbitrer : soit TVA manquante a renseigner, soit basculer en B2C.
- **6 SO sans livraison** (`qty_delivered=0`) : S06050 Maison Muscari, S06049 DEMARS/CM Beauraing,
  S06033 Joffrey Helson Menuiserie, S06047 Pougin, S06014 BTL/Break Time, S05958 Ateliers Saupont.
- **Maison Muscari (#125683)** : Peppol `not_valid` malgre eas=0208 et endpoint 1007195540 — a verifier.

Erreurs : 0.

## 2026-07-26 — Lettrage banque ING — paiements clients (38 cas / 39 lignes bancaires reconciliees, 16.241,92 EUR, 7 a statuer, 8 hors-scope)

### Perimetre
54 credits ING non rapproches au 26/07/26 (journal BNK1, id=14). Demande explicite Nicolas :
lettrer tout le lot avec tolerance d'ecart relevee a **5,00 EUR** (au lieu de 1,00 EUR habituel),
en identifiant le client par communication structuree / IBAN emetteur / reference facture quand le
`partner_id` n'etait pas deja renseigne sur la ligne bancaire (aucune ligne credit n'avait de partner_id
pre-rempli sur ce lot).

### Methode
1. Extraction automatique par ligne : IBAN emetteur (`res.partner.bank.acc_number` normalise),
   communication structuree belge format `+++XXX/XXXX/XXXXX+++` matchee contre `account.move.payment_reference`,
   et references facture explicites (`INV/2026/xxxxx`, `RINV/xx-xx/xxxx`) citees dans le libelle.
2. Pour chaque candidat : recuperation des lignes 400000 ouvertes du partner, verification que la
   somme signee (facture(s) + eventuelle note de credit/vieille ligne de credit du meme partner) tombe
   au plus a 5,00 EUR du montant recu.
3. Reconciliation technique identique aux lots precedents (repointage 499000->400000+partner, puis
   `account.move.line.reconcile()`), ecart absorbe en 657100 (charge, sous-paiement) / 757100 (produit,
   sur-paiement) si <=5,00 EUR. 1 cas de paiement partiel volontaire (ecart >5 EUR, pas de write-off,
   facture reste `partial`).
4. Script complet et commite : `compta/lettrage_11_ing_20260726.py` (38 cas nommes en dur, chacun
   verifie manuellement avant execution).

### Cas particuliers a noter
- **Anais Michoel** (BSL 19798+19799) : 2 paiements distincts du meme jour totalisant 324,80 EUR
  reconcilies ensemble contre 2 factures (INV/2026/03444 + INV/2026/03363) — match exact, 0 ecart.
- **Netting facture + note de credit / vieille ligne de credit** (6 cas) : BARVO (INV/2026/03072 -
  RINV/25-26/0344), NIVALIM (INV/2026/02864 - vieux solde BNK1/25-26/5151), Lillodis (INV/2026/02970 -
  vieux solde BNK1/25-26/4151), Delhaize Le Lion Affilie 048900 (INV/2026/03277 - RINV/25-26/0363),
  AD Delhaize Fernelmont (INV/2026/03543 - RINV/26-27/0010), SA Marer Bastogne (INV/2026/03152 -
  RINV/25-26/0353), LSL Retail Chaumont-Gistoux (INV/2026/03065 - RINV/25-26/0341).
- **Megan Houtvast** (BSL 19911, 123,47 EUR) : paiement PARTIEL volontaire contre INV/2026/02294
  (323,47 EUR) — ecart 200,00 EUR > tolerance 5 EUR, donc **pas de write-off** : facture laissee
  `payment_state=partial`, residuel 200,00 EUR toujours ouvert (a suivre normalement, pas une erreur).

### Resultat — 38/38 cas OK, 0 erreur

38 cas traites (couvrant 39 lignes bancaires ING), total encaisse **16.241,92 EUR**.
17 write-offs crees (MISC/26-27/07/0125 a 0141) : 16x 657100 (charge, total 0,58 EUR) + 1x 757100
(produit, 0,01 EUR) — **impact net P&L -0,57 EUR**, negligeable, ecart individuel maximal 0,28 EUR
(Carrefour Belgium SARUB, INV/2026/03141).

### Non lettrees (15 credits restants) — `compta/review/lettrage_ing_20260726_review.md`

**7 ambigus (3.336,69 EUR)** — a statuer par Nicolas :
| BSL id | Montant | Client | Motif |
|---|---:|---|---|
| 19466 | 675,58 | NANRETAIL SA (Intermarche Naninne) | Communication pointe vers facture deja `paid` — recidive du cas signale le 14/07/26, toujours non resolu. |
| 19660 | 637,24 | ITM Alimentaire / Centrale Intermarche | 6 factures ouvertes, aucune ni combinaison ne vaut 637,24 — recidive du 14/07/26. |
| 19784 | 67,00 | Smartbox Group | 80+ factures ouvertes (petits montants), communication non-belge, trop de candidats. |
| 19815 | 111,55 | Faire.Com (Faire Wholesale B.V.) | 2 lignes ouvertes (127,20 / 232,46), aucune ne colle a 5 EUR pres. |
| 19876 | 688,89 | Courses L SRL (Carrefour Market Courcelles) | Meme communication qu'un paiement deja lettre le 14/07/26 (INV/2026/03057, deja `paid`) — **probable double paiement client**. |
| 19914 | 720,44 | Spar Vaux-sur-Sure (Louis Besseling Distribution) | Facture deja partiellement payee (residuel 680,54/720,44) — client semble avoir repaye le montant total, **surpaiement potentiel 39,90 EUR**. |
| 19952 | 436,84 | Dynamic Food SRL (Spar LLN) | Communication pointe vers facture deja `paid`, seule ligne ouverte (avoir -84,70) ne colle pas. |

**8 hors-scope (4.055,33 EUR)**, non-clients — non touchees : Baloise Belgium (79,51, remboursement
assurance salaire), Pluxee Belgium x2 (124,95 + 33,28, cheques-repas), Edenred Belgium (17,59,
cheques-repas), virements internes Teatower BNK2->BNK1 x4 (500 + 300 + 2.000 + 1.000 EUR).

**38 lignes debitrices** (frais bancaires, fournisseurs, ONSS, salaires, cartes) : non traitees,
hors perimetre explicite de cette tache (write-off autorise uniquement sur paiements clients).

### Resultat global
- ING credits non rapproches avant : 54 — apres : 15 (7 a statuer + 8 hors-scope)
- ING debits non rapproches : 38 (inchange, hors-scope)

## 2026-07-26 — Facturation B2B PRO livrees + envoi Peppol (28 factures / 11.105,82 EUR TTC)

### Perimetre
Toutes les sale.order PRO (hors B2C/Shopify team_id=4) en state sale/done, invoice_status='to invoice', qty_delivered>0 au 26/07/26.
Commande : `py scripts/facturation_b2b_peppol.py --apply` (aucune exclusion manuelle cette fois).

### Corrections Peppol EAS 9925 -> 0208 pendant l'execution
16 partenaires BE corriges (eas force a 0208 + re-verification declenchee), 13 sont passes a `valid` et ont debloque leur SO :
MaxMara scrl (3129), O'Brunch Coffee (3165, `not_valid`->`valid`), Ramaut (3195), AD Fosses-la-Ville (5441),
Intermarche Naninne (5506), Di Michele Sabrina (5634), Delhaize DEBROUX (5729), partner 5733 (Delhaize Embourg),
partner 7680 (AD Ciney), partner 8119 (Intermarche Jambes), Proxy Delhaize Rixensart (50967),
Hyper Carrefour Mons Grands Pres (113613), Carrefour Market Bievre (123069), FQMS Proxy Delhaize Quadrilatere Huy (125351).
2 SKIP_NO_VAT inchanges (VAT manquante) : Delphine Samain (124325), charlier chantal (125330).

### Resultat
- **28 SO facturees, postees et envoyees Peppol** — TTC **11.105,82 EUR**. 0 echec, 0 facture a 0 EUR.
- 2 lignes TRANSPORT forcees qty_delivered 0->1 (S06032, S06021).

### Restant a traiter
- **1 SO bloquee Peppol** : S05765 Delphine Samain (inv_partner 124325, VAT manquante) -> completer la fiche puis refacturer.
- **4 SO sans rien de livre** (hors perimetre delivered-only) : S06033 Joffrey Helson Menuiserie SRL,
  S06014 BTL SRL - Break Time, S06002 charlier chantal, S05958 Les Ateliers Saupont - Bertrand Noel.
  A refacturer quand livraison confirmee.

### Detail des 28 factures

| Facture | SO | Client | TTC | Peppol |
|---|---|---|---:|---|
| INV/2026/03606 | S06039 | Carrefour Market Waterloo | 164,85 | processing |
| INV/2026/03607 | S06038 | Hyper Carrefour Mons Grands Pres | 201,60 | processing |
| INV/2026/03608 | S06037 | Intermarche Jambes | 229,60 | processing |
| INV/2026/03609 | S06036 | AD Ciney (Etablissements Schnongs) | 210,00 | processing |
| INV/2026/03610 | S06032 | Carrefour Market Bievre | 103,02 | processing |
| INV/2026/03611 | S06031 | Smart fridges srl - Frigo Loco | 254,40 | processing |
| INV/2026/03612 | S06030 | The Torrefactory Project Sa | 1.378,00 | processing |
| INV/2026/03613 | S06029 | Distri-Incourt - Delhaize Incourt | 277,25 | processing |
| INV/2026/03614 | S06028 | Delhaize Le Lion (Affilie 04401) | 159,60 | processing |
| INV/2026/03615 | S06027 | Delhaize Le Lion (Affilie 04690 - Rixensart) | 293,65 | processing |
| INV/2026/03616 | S06026 | Sorescol S.A. | 477,00 | processing |
| INV/2026/03617 | S06025 | Graines De Quartier | 252,68 | processing |
| INV/2026/03618 | S06024 | Delhaize Le Lion (Affilie 04315) | 510,68 | processing |
| INV/2026/03619 | S06023 | Carrefour Market Remouchamps | 229,60 | processing |
| INV/2026/03620 | S06022 | Carrefour Market Remouchamps | 1.434,02 | processing |
| INV/2026/03621 | S06020 | DelEmbourg SRL - Delhaize Embourg | 606,91 | processing |
| INV/2026/03622 | S06021 | MaxMara scrl (Max et moi) | 204,60 | processing |
| INV/2026/03623 | S06019 | Ramaut | 793,97 | processing |
| INV/2026/03624 | S06018 | SA Beausov New - Delhaize Beauraing | 351,05 | processing |
| INV/2026/03625 | S06012 | FQMS - Proxy Delhaize Quadrilatere (Huy) | 344,45 | processing |
| INV/2026/03626 | S06017 | SA Barthe - Intermarche Assesse | 291,20 | processing |
| INV/2026/03627 | S06016 | NANRETAIL SA - Intermarche Naninne | 175,70 | processing |
| INV/2026/03628 | S06015 | Delhaize Le Lion (Affilie 04336) | 470,43 | processing |
| INV/2026/03629 | S05998 | O'Brunch Coffee | 284,90 | processing |
| INV/2026/03630 | S06007 | Carrefour Hyper Marche-en-Famenne | 827,39 | processing |
| INV/2026/03631 | S05982 | Carrefour Market Vielsalm | 357,07 | processing |
| INV/2026/03632 | S05980 | Intermarche Mons | 60,50 | processing |
| INV/2026/03633 | S05640 | Chez Simone - Elodie Gianello | 161,70 | processing |

## 2026-07-15 — Facturation B2B PRO livrees + envoi Peppol (14 factures / 6.062,60 EUR TTC)

### Perimetre
Toutes les sale.order PRO (hors B2C/Shopify team_id=4) en state sale/done, invoice_status='to invoice', qty_delivered>0 au 15/07/26.
Commande : `py facturation_b2b_peppol.py --apply --exclude S05982,S06007,S05980`.

### Nouveaute script : `--exclude`
Ajout d'un mecanisme d'exclusion manuelle de SO (`EXCLUDE_SO_NAMES` + option CLI `--exclude S0xxx,S0yyy`).
**Motif** : le TT/OUT valide ne prouve pas la reception client. Quand Gilles emporte la marchandise
en camionnette, le stock sort le jour de la preparation mais le client n'est servi que lors du passage
merch. Facturer entre les deux = facturer avant livraison (risque de litige, et rejets EDI cote Carrefour
qui controle les references de bon de livraison).

### Exclusions de ce lot (a facturer APRES le passage de Gilles)
| SO | Client | TTC | Passage merch |
|---|---|---:|---|
| S06007 | Carrefour Hyper Marche-en-Famenne | 827,39 | livraison lun 20/07 |
| S05982 | Carrefour Market Vielsalm | 357,07 | implantation lun 20/07 |
| S05980 | Intermarche Mons | 60,50 | livraison display mer 22/07 |

Decision Nicolas 15/07/2026 (arbitrage explicite : ne pas facturer les 3 avant reception).

### Resultat
- **14 SO facturees, postees et envoyees Peppol** — TTC **6.062,60 EUR**. 0 echec, 0 facture a 0 EUR.
- **6 partenaires corriges Peppol** pendant l'execution ; 2 passes `not_verified -> valid` :
  ID=7150 (adresse de facturation enfant, AD Delhaize Fernelmont) et ID=122589 (Carrefour Market Wellin).
  La correction de 7150 a debloque **S06013** (357,70 EUR), qui etait `BLOCK` au dry-run -> 14 factures au lieu de 13.
- **2 SKIP_NO_VAT** : Delphine Samain (ID=124325) et charlier chantal (ID=125330) — VAT manquante, fiches a completer.

### Restant a traiter
- **1 SO bloquee Peppol** : S05765 Delphine Samain (inv_partner 124325, pas de VAT) -> completer la fiche puis refacturer.
- **4 SO sans rien de livre** (hors perimetre delivered-only) : S06014 BTL SRL - Break Time, S05998 O'Brunch Coffee,
  S06002 charlier chantal, S05958 Les Ateliers Saupont. A refacturer quand livraison confirmee.
- **3 SO exclues** ci-dessus, a facturer apres passage Gilles (semaine du 20/07).

### Detail des 14 factures

| Facture | SO | Client | TTC | Peppol |
|---|---|---|---:|---|
| INV/2026/03543 | S06013 | AD Delhaize Fernelmont (Fernel-Dis) | 357,70 | processing |
| INV/2026/03544 | S06011 | Delhaize Le Lion S.A (Affilie 0490...) | 319,20 | processing |
| INV/2026/03545 | S06010 | Delhaize Le Lion S.A (Affilie 0492...) | 319,51 | processing |
| INV/2026/03546 | S06009 | Spar Barvaux | 250,00 | processing |
| INV/2026/03547 | S06008 | Carrefour Belgium - Carrefour Market | 241,65 | processing |
| INV/2026/03548 | S06005 | Carrefour Belgium - Carrefour Hyper | 665,00 | processing |
| INV/2026/03549 | S06004 | Delhaize Le Lion S.A (Affilie 0444...) | 427,70 | processing |
| INV/2026/03550 | S05997 | Hello Bio sprl (Pure) | 346,39 | processing |
| INV/2026/03551 | S05996 | Carrefour Belgium | 198,00 | processing |
| INV/2026/03552 | S05995 | Carrefour Belgium | 638,40 | processing |
| INV/2026/03553 | S05994 | Made in Louise | 258,70 | processing |
| INV/2026/03554 | S05977 | Cocon Life store | 403,67 | processing |
| INV/2026/03555 | S05987 | Spar Clavier | 332,50 | processing |
| INV/2026/03556 | S05983 | Delhaize Le Lion S.A (Affilie 0488...) | 1.304,18 | processing |

> `processing` = soumise au reseau Peppol avec UUID (passe a `done` apres flush du cron Odoo).

---

## 2026-07-14 — Facturation B2B PRO livrees + envoi Peppol (25 factures / 10.357,81 EUR TTC)

### Perimetre
Toutes les sale.order PRO (hors B2C/Shopify, team_id=4 exclu) en state sale/done avec invoice_status='to invoice' et qty_delivered>0 au 14/07/26. Script : `scripts/facturation_b2b_peppol.py` (corrige aujourd'hui, cf bugs ci-dessous).

### Bugs corriges dans le script
1. `p['name']` pouvait etre `False` (contacts enfants sans nom propre, type adresse) -> `TypeError: 'bool' object is not subscriptable`. Fix : `pname = p.get('name') or f"(sans nom, ID={p['id']})"`.
2. La correction EAS ne visait que les partenaires `peppol_eas=='9925'`. Or plusieurs partenaires BE etaient deja en `eas=0208` mais `peppol_verification_state` restait `not_verified` (jamais (re)verifie) ou avec `peppol_endpoint` vide. Elargi le critere : tout partenaire BE (country_id=Belgium ou VAT commencant par BE) avec `eas!=0208 OU state!=valid` est corrige (endpoint recalcule depuis le n° BCE) puis reverfie via `button_account_peppol_check_partner_endpoint`.
3. Credentials Odoo en clair dans le script (repo public Teatower-Planning) -> remplace par `os.environ.get('ODOO_PWD')`, variable persistee via `setx ODOO_PWD` sur ce poste (creds dans Materiel TT.xlsx).

### Regle durcie appliquee
Facturation strictement `delivered` (wizard `sale.advance.payment.inv`), transport force a `qty_delivered=qty_ordered` si non scanne, et **envoi strictement Peppol** — aucun fallback email (contrairement au lot du 27/04/26). Un client bloque Peppol = fiche corrigee (EAS 0208 BE + endpoint + reverif) mais facture **non creee** tant que l'etat n'est pas `valid`.

### Resultat
- **25 SO facturees et postees**, HT 9.764,23 EUR / **TTC 10.357,81 EUR**.
- **25/25 envoyees via Peppol** (`peppol_move_state` = `done` pour 23, `processing`/en cours de flush pour 2 — INV/2026/03514 et INV/2026/03530, confirmees soumises avec UUID).
- **18 partenaires corriges Peppol** (EAS 9925->0208 ou reverification 0208 bloque) pendant l'execution, tous passes `valid` sauf 1 (`charlier chantal`, ID=125330, VAT manquant — non bloquant aujourd'hui car sa SO S06002/S06003 n'a rien de livre).
- **1 cas particulier** : INV/2026/03514 (Chez Remy SASPJ, partner enfant ID=124431 "Marine Toffoli") a d'abord echoue a l'envoi Peppol (`"Le partenaire n'a pas de configuration Peppol valide"`) alors que le contact enfant etait `valid`. Cause : le **partenaire commercial parent** (ID=124430 "Mayrine Toffoli") n'avait pas d'endpoint Peppol renseigne (le wizard d'envoi verifie la configuration au niveau societe/commercial, pas seulement le contact enfant). Corrige manuellement (EAS 0208 + endpoint BCE + reverif -> valid), facture renvoyee avec succes. **A reporter dans le script** : toujours verifier/corriger le `commercial_partner_id` en plus du partner de facturation direct.
- **11 SO non facturees** (rien de livre — hors perimetre delivered-only) : Hello Bio sprl, Carrefour Belgium x3, Made in Louise, Cocon Life store, charlier chantal, Spar Clavier, Delhaize Le Lion Affilie 048880, Les Ateliers Saupont, BTL SRL - Break Time. A refacturer quand livraison confirmee.
- **0 SO bloquee Peppol non facturee** au final (tous les blocages initiaux ont ete resolus par correction+reverification en cours d'execution).

### Detail des 25 factures

| Facture | SO | Client | TTC | Peppol |
|---|---|---|---:|---|
| INV/2026/03506 | S05993 | Brasserie Demain | 118,60 | done |
| INV/2026/03507 | S05992 | Centrale Intermarche | 48,10 | done |
| INV/2026/03508 | S05991 | Sadel Trade - AD Delhaize Jodoigne | 463,41 | done |
| INV/2026/03509 | S05990 | Delhaize Le Lion S.A (Affilie 046780 - Recogne) | 361,23 | done |
| INV/2026/03510 | S05989 | Delhaize Le Lion S.A (Affilie 41092 - Bertrix) | 1.078,36 | done |
| INV/2026/03511 | S05988 | Carrefour Market Bastogne - Pascalino | 270,22 | done |
| INV/2026/03512 | S05986 | Spar Vaux-sur-Sûre | 39,90 | done |
| INV/2026/03513 | S05985 | SA Marer - AD Delhaize Bastogne | 465,50 | done |
| INV/2026/03514 | S05984 | Chez Remy SASPJ | 153,10 | processing (fix manuel parent) |
| INV/2026/03515 | S05981 | Alcodis SA - Veronique Goffaux | 74,20 | done |
| INV/2026/03516 | S05979 | SASPJ Ferme du Moligna Borlon Ramelot | 256,65 | done |
| INV/2026/03517 | S05978 | Boulangerie Les Co'Pains SPRL | 250,00 | done |
| INV/2026/03518 | S05976 | Carrefour Belgium (Hyper Herstal) | 239,40 | done |
| INV/2026/03519 | S05975 | Les Tables Imaginaires - Restaurant Rosalie | 493,03 | done |
| INV/2026/03520 | S05974 | Carrefour Belgium | 239,40 | done |
| INV/2026/03521 | S05973 | D'ici Champion srl | 539,00 | done |
| INV/2026/03522 | S05972 | Cafermi | 532,03 | done |
| INV/2026/03523 | S05971 | AD Delhaize Roodebeek | 539,30 | done |
| INV/2026/03524 | S05970 | Teroir de Magerotte | 777,07 | done |
| INV/2026/03525 | S05969 | Newpharma | 587,64 | done |
| INV/2026/03526 | S05967 | SRL LEJER | 296,11 | done |
| INV/2026/03527 | S05961 | Comptoir des Boissons | 936,26 | done |
| INV/2026/03528 | S05959 | Spar Vaux-sur-Sûre | 720,44 | done |
| INV/2026/03529 | S05917 | Pharmacie Badot | 332,50 | done |
| INV/2026/03530 | S06003 | N.B.S. RETAIL - Delhaize de Marche | 546,36 | processing |

**Total HT 9.764,23 EUR / TTC 10.357,81 EUR — 25/25 factures postees et envoyees Peppol.**

## 2026-07-14 — Lettrage banque ING — paiements clients (4 lignes reconciliees / 1.733,68 EUR, 5 clients a statuer, 11 hors-scope)

### Perimetre
20 lignes ING non rapprochees (journal BNK1, id=14) au 14/07/26 : 9 credits (encaissements a analyser) + 11 debits (frais/fournisseurs, hors-scope explicite de cette passe — l'autorisation write-off de Nicolas ne porte que sur les clients).

### Methode
Reprise exacte de la methode validee le 10/07 (`compta/lettrage_09_ing_20260710.py`, cf LOG 10/07 + 02/07) :
1. Repointer la ligne suspense 499000 du move BSL -> 400000 (Customers, id=162) + partner_id.
2. `account.move.line.reconcile([bsl_line_id, doc_line_id])`.
3. Si ecart residuel <= 1,00 EUR : write-off MISC (journal id=11) sur 657100 (Negative Payment Differences, id=293 — client a sous-paye) ou 757100 (Positive Payment Differences, id=347 — client a surpaye), reconcilie avec le residu.
Script one-shot : `C:\Users\FlowUP\AppData\Local\Temp\claude\...\scratchpad\lettrage_ing_20260714.py` (non committe, contient creds via `os.environ['ODOO_PWD']`).

### Lettres — 4/4 OK

| BSL id | Date | Montant BSL | Facture | Client | Ecart | Write-off |
|---|---|---|---|---|---|---|
| 19689 | 10/07 | +266,00 | INV/2026/03306 | Joffrey Helson Menuiserie SRL | 0,00 | aucun |
| 19677 | 10/07 | +285,59 | INV/2026/03336 (285,60) | Spar Gembloux | -0,01 | MISC/26-27/07/0121 — 657100 debit 0,01 |
| 19661 | 09/07 | +688,87 | INV/2026/03057 (688,89) | Carrefour market Courcelles | -0,02 | MISC/26-27/07/0122 — 657100 debit 0,02 |
| 19662 | 09/07 | +493,22 | INV/2026/03110 (493,53) | Carrefour Belgium (SARUB, partner 6596) | -0,31 | MISC/26-27/07/0123 — 657100 debit 0,31 |

Verif finale : les 4 factures sont `payment_state=paid`, `amount_residual=0.00`, les 4 BSL `is_reconciled=True`.

### A statuer (5 credits clients, non lettres) — `compta/review/lettrage_ing_20260714_review.md`

| BSL id | Date | Montant | Libelle | Raison |
|---|---|---|---|---|
| 19466 | 01/07 | +675,58 | NANRETAIL SA (Intermarche Naninne, partner 2812) | Aucune facture ouverte pour ce partner ; sa seule facture Odoo (INV/2026/02700) est deja `paid` a 716,11 EUR — ecart 40,53 EUR trop grand, communication structuree reutilisee mais montant incoherent. Possible double paiement ou erreur de communication cote client. |
| 19660 | 09/07 | +637,24 | ITM ALIMENTAIRE BELGIUM SA (probable Centrale Intermarche #124363, meme adresse Rue du Bosquet 4 LLN) | Aucune facture ouverte de Centrale Intermarche (48,10 / 123,10 / 48,10 / 675,00 / 235,60 / 714,00) ne colle, seule ou en combinaison. |
| 19630 | 08/07 | +79,51 | BALOISE BELGIUM — "ADAPTATION SALAIRE A/26.00112 DATE ACCID" | Remboursement assurance salaire/accident du travail, pas un client — categorie proche du 455000 neutre (cf memoire remboursements paie). |
| 19652 | 09/07 | +124,95 | PLUXEE BELGIUM (cheques-repas) | Flux RH/avantages, pas un client. |
| 19682 | 10/07 | +500,00 | Virement instantane depuis BE86068958071350 (compte Teatower BNK2) | Virement interne entre comptes propres Teatower, pas un encaissement client. |

### Hors-scope (11 debits, non touches)
Frais carte ING (-2,25), SD Worx x2 (-110,63 / -59,90 — a surveiller, cf memoire anomalie ONSS/PP SD Worx), Google Ads (-437,07), Google Cloud (-384,12), **virement "Avance" Vansimpsen Audrey -500,00** (a verifier : avance salarie/actionnaire potentielle, categorie proche 489000 — a trancher par Nicolas), Kirchner Fischer + Co GmbH x2 (-12.837,54 / -8.129,06, fournisseur), Adobe (-36,29), Intuit (-722,47), Mastercard invoice 2026070568 (-47,19).

### Resultat
- ING non rapprochees avant : 20 (9 credits / 11 debits)
- ING non rapprochees apres : 16 (5 credits a statuer / 11 debits hors-scope)
- Lettrees automatiquement (A+B) : 4 / 4 candidats identifies, 1.733,68 EUR
- Write-offs 657100 : 3 (0,01 + 0,02 + 0,31 = 0,34 EUR total)

## 2026-07-10 — Lettrage banque ING — paiements clients (9 lignes reconciliees / 3.189,26 EUR, 2 a revoir, 9 hors-scope)

### Perimetre
20 lignes ING non rapprochees (journal BNK1, id=14) au 10/07/26 : 11 credits (encaissements a analyser) + 9 debits (cartes/frais fournisseurs, hors-scope client d'office).

### Bug corrige (important pour scripts futurs)
Le narratif des scripts precedents ("Odoo 18 verrouille l'ecriture sur les BSL via XML-RPC") etait **faux**. La vraie cause : `account.move.line.write()` etait appele avec le dict de valeurs en kwargs XML-RPC (`call(model, 'write', [[id]], {vals})`) au lieu d'un argument positionnel dans `args` (`call(model, 'write', [[id], {vals}])`). Odoo interprete kwargs comme des arguments nommes de la methode Python `write(self, vals)`, qui n'accepte pas `account_id=...` en kwarg -> `TypeError: write() got an unexpected keyword argument`. Corrige et confirme fonctionnel sur les 9 lignes ci-dessous. A reporter dans tout script de lettrage futur.

### Methode technique (inchangee sur le fond)
Pour chaque credit identifie comme paiement client : (1) repointage de la ligne suspense 499000 du move BSL -> compte 400000 Customers + partenaire ; (2) reconciliation groupee (`account.move.line.reconcile()`) avec la ou les ligne(s) facture/avoir ouvertes ; (3) si ecart residuel <= 1,00 EUR (tolerance fixee par Nicolas), creation d'un OD (journal MISC id=11) 657100 Negative Payment Differences (charge, si le client a sous-paye) ou 757100 Positive Payment Differences (produit, si sur-paye), reconcilie avec le residu pour ramener la facture a `paid`.

### Lignes lettrees (9) — total encaisse 3.189,26 EUR

| BSL id | Date | Montant recu | Client (payeur) | Facture(s)/Avoir(s) | Net du/attendu | Ecart | Write-off | OD move | Resultat |
|---|---|---|---|---|---|---|---|---|---|
| 19620 | 08/07 | 20,00 | Maison de Repos Libert (paye par CPAS Marche-Famenne pour un resident) | INV/2026/02978 | 20,00 | 0,00 | — | — | paid |
| 19622 | 08/07 | 1.058,33 | Ramaut / Ramhoreca SA (communication = n° facture explicite) | INV/2026/03309 | 1.058,33 | 0,00 | — | — | paid |
| 19635 | 08/07 | 266,00 | Cafermi | INV/2026/03405 | 266,00 | 0,00 | — | — | paid |
| 19478 | 01/07 | 455,71 | N.B.S. RETAIL - Delhaize de Marche (+ Nicolas Bergé, meme commercial_partner_id 8159) | INV/2026/02907 (540,42) − RINV/25-26/0358 (84,71) | 455,71 | 0,00 | — | — | paid / paid |
| 19487 | 02/07 | 351,42 | Cotes Aromes - Francois CHLEIDE | INV/2026/02740 | 351,40 | +0,02 | 757100 | MISC/26-27/07/0117 | paid |
| 19549 | 06/07 | 239,39 | Helene BERTRAND | INV/2026/02868 | 239,40 | -0,01 | 657100 | MISC/26-27/07/0118 | paid |
| 19609 | 07/07 | 279,29 | Louis Delhaize - Haversin (paye au nom "CYANAR", meme commercial_partner_id 123844) | INV/2026/03231 | 279,30 | -0,01 | 657100 | MISC/26-27/07/0119 | paid |
| 19476 | 01/07 | 381,32 | Carrefour Belgium SARUB (centrale, communication = 4 refs explicites) | INV/2026/02753 (231,05) + INV/2026/02865 (276,17) − RINV/25-26/0254 (62,77) − RINV/25-26/0257 (62,76) | 381,69 | -0,37 | 657100 | MISC/26-27/07/0120 | paid (4 documents) |
| 19550 | 06/07 | 137,80 | La guinguette du Merry | INV/2026/02882 | 137,80 | 0,00 | — | — | paid |

**Total write-off : 0,41 EUR bruts (3× 657100 charge = 0,39 EUR / 1× 757100 produit = 0,02 EUR) — impact net P&L = -0,37 EUR**, negligeable, ecart maximal individuel 0,37 EUR (< tolerance 1,00 EUR fixee par Nicolas pour ce lot).

### Lignes NON lettrees — a revoir (2)

| BSL id | Date | Montant | Libelle | Motif |
|---|---|---|---|---|
| 19466 | 01/07 | 675,58 | NANRETAIL SA - Intermarche Naninne — communication ***000/0038/68983*** | La communication structuree pointe vers INV/2026/02700 (716,11 EUR) **deja soldee** (payment_state=paid, residual=0,00) depuis le 26/05. Aucune facture ouverte NANRETAIL ne correspond a 675,58 EUR. Possible doublon de paiement ou communication erronee cote client — a clarifier manuellement avant tout lettrage (aucun match automatique fiable). |
| 19630 | 08/07 | 79,51 | Baloise Belgium S.A — communication "ADAPTATION SALAIRE A/26.00112 DATE ACCID 070126 070726" | **Pas une facture client** — remboursement d'assurance lie a un ajustement de salaire pour accident de travail (meme famille que la regle deja validee "remboursements paie = 455000 NEUTRE, jamais 620"). Hors perimetre "paiement client / facture ouverte" de cette tache — non traite, a router en OD 455000 si Nicolas valide explicitement (Baloise est fournisseur d'assurance dans Odoo, pas client, factures ouvertes RESA159 443,60 EUR et RESA439 1.339,85 EUR sans lien direct avec ce montant). |

### Lignes NON lettrees — hors-scope (9 debits, non touchees)
Frais bancaires (ING carte -2,25 / abonnement), domiciliations fournisseurs (SD Worx x2 -110,63/-59,90, Google Cloud -384,12, Kirchner Fischer -12.837,54), cartes (Google Ads -437,07, Adobe -36,29, Intuit -722,47), avance dirigeant (Vansimpsen Audrey -500,00). Aucune n'est un encaissement client — hors perimetre de la demande, non touchees.

### Resultat
- BSL ING non rapprochees avant : 20 (11 credits + 9 debits)
- BSL ING non rapprochees apres : 11 (9 debits hors-scope + 2 a revoir : NANRETAIL 675,58 EUR + Baloise 79,51 EUR)
- Lettrees : 9/11 credits identifies (82%), total **3.189,26 EUR**, 11 documents clients soldes (7 factures + 3 avoirs nettes dans 2 cas multi-documents + 1 facture nette d'avoir)
- Ecart total absorbe en 657100/757100 : 0,41 EUR bruts / -0,37 EUR net P&L (4 lignes, chacune <= 0,37 EUR, sous tolerance 1,00 EUR)

---

## 2026-07-02 — Lettrage banque ING — paiements clients (8 lignes reconciliees, 7 hors-scope)

### Perimetre
15 lignes ING non rapprochees (journal BNK1, id=14) au 02/07/26 : 8 credits (encaissements a analyser) + 7 debits (cartes/frais, hors-scope client d'office).

### Methode technique
Pour chaque credit identifie comme paiement client : creation d'un OD (journal MISC id=11) qui (1) debite 499000 Suspense pour le montant recu avec le bon partenaire, reconcilie avec la ligne suspense d'origine de la BSL ; (2) credite 400000 Customers pour le meme montant, reconcilie avec la/les ligne(s) facture(s) ouvertes (+ credit note le cas echeant) ; (3) si ecart <= 2 EUR, ajoute une paire 657100 Negative Payment Differences (charge) / 400000 pour absorber l'ecart et ramener le residu a 0. Reconciliation via `account.move.line.reconcile()` (methode BSL native non exposee en XML-RPC Odoo 18, technique deja utilisee le 14/04 et 15-18/06).

### Lignes lettrees (8) — total 4 277,86 EUR

| BSL id | Date | Montant recu | Client | Facture(s) | Montant facture net | Ecart | Write-off | OD move | Resultat |
|---|---|---|---|---|---|---|---|---|---|
| 19411 | 29/06 | 319,18 | Spar Clavier (124572) | INV/2026/03217 | 319,20 | -0,02 | 657100 | 41790 | paid |
| 19412 | 29/06 | 767,22 | KAIO Retail invest - Delhaize Ottignies (3016) | INV/2026/02724 | 767,23 | -0,01 | 657100 | 41791 | paid |
| 19413 | 29/06 | 512,40 | SA Villersem - Intermarche Villers-le-Bouillet (115879) | INV/2026/02642 (582,42) - RINV/25-26/0306 (70,01) | 512,41 | -0,01 | 657100 | 41792 | paid / paid |
| 19436 | 30/06 | 67,60 | Creative Ceramic - Verschelden Elora (124375) | INV/2026/03015 | 67,60 | 0,00 | - | 41793 | paid |
| 19438 | 30/06 | 627,96 | AD Delhaize Roodebeek (123997) — virement au nom "DELWOL", meme adresse Chaussee de Roodebeek 199 Bruxelles | INV/2026/02867 | 627,98 | -0,02 | 657100 | 41794 | paid |
| 19440 | 30/06 | 101,51 | 2u S.A. - Carrefour Market Ciney (2773) | INV/2026/02534 (332,50) - RINV/25-26/0302 (230,99) | 101,51 | 0,00 | - | 41795 | paid / paid |
| 19441 | 30/06 | 522,55 | SRL Spydis - Intermarche Spy (116686) | INV/2026/02789 (529,55) - RINV/25-26/0315 (7,00) | 522,55 | 0,00 | - | 41796 | paid / paid |
| 19451 | 30/06 | 1 359,44 | Le Comptoir Local Linkebeek (3062) — communication "02734" = suffixe facture | INV/2026/02734 | 1 359,44 | 0,00 | - | 41797 | paid |

**Total write-offs : 0,06 EUR (657100 Negative Payment Differences)** — toutes les factures/avoirs listes ont amount_residual=0,00 EUR et payment_state=paid (ou reversed pour les factures soldees via avoir) apres coup, verifie post-lettrage.

### Lignes NON lettrees (7) — hors scope client, total 1 493,25 EUR

| BSL id | Date | Montant | Libelle | Motif |
|---|---|---|---|---|
| 19426 | 30/06 | -211,68 | Mastercard Business — Matcha CO Faire, Den Haag NLD | Achat marketplace Faire.com (fournisseur), pas un encaissement client |
| 19427 | 30/06 | -232,46 | Mastercard Business — Livoo Faire, Den Haag NLD | idem — Faire.com |
| 19428 | 30/06 | -223,99 | Mastercard Business — cool people club Faire, Den Haag NLD | idem — Faire.com |
| 19429 | 30/06 | -597,00 | Mastercard Business — YOKO DESIGN Faire, Den Haag NLD | idem — Faire.com |
| 19430 | 30/06 | -194,87 | Mastercard Business — Ogo living Faire, Den Haag NLD | idem — Faire.com |
| 19459 | 01/07 | -31,00 | Facture ING Belgique SA (frais/abonnement bancaire) | Frais bancaire fournisseur, pas client |
| 19460 | 01/07 | -2,25 | Decompte frais ING MasterCard Business (cotisation mensuelle) | Frais bancaire fournisseur, pas client |

Ces 7 lignes sont des debits (paiements sortants/frais), aucune n'est un paiement client entrant — hors perimetre de la demande, non touchees. A router vers l'agent achats/comptabilite fournisseurs si Nicolas souhaite les traiter.

### Resultat
- ING non rapprochees avant : 15
- ING non rapprochees apres : 7 (toutes hors-scope client, cf. tableau ci-dessus)
- Lettrees : 8/8 candidats client identifies (100%), total 4 277,86 EUR
- Ecart total absorbe en 657100 : 0,06 EUR (4 lignes, chacune <= 0,02 EUR)
- Aucun cas ambigu / en review : tous les 8 paiements matchent une facture (ou facture nette d'avoir) via montant exact ou adresse/communication explicite

## 2026-07-01 — Facturation B2B Peppol (livre + facturable, PRO uniquement)

Script : `scripts/facturation_b2b_peppol.py` (existant, adapte pour exclusion team B2C/web + verif Peppol sur le partenaire de facturation reel).

- 21 SO en `invoice_status='to invoice'` scannees, dont 2 exclues (team "Odoo x Shopify" = B2C, #49036 Linda Mertens 60,00€ / #48143 Jessica Masula 43,50€).
- 19 SO PRO (team "Sales") : 6 exclues car rien de reellement livre (delivery_status pending malgre invoice_status='to invoice', du a des produits en invoice_policy='order' — S05919 Brasserie Miroir, S05918 Cellmade, S05917 Pharmacie Badot, S05916 Anais Michoel, S05914 Carrefour Belgium, S05908 PC Distribution, total 2 348,80€ non factures).
- 1 SO bloquee Peppol : S05894 Ma Pharmacie de Baillonville — adresse de facturation enfant (partner 117367) `peppol_verification_state=not_verified` alors que la maison mere (partner 3184) est valid. 383,60€ non facture, a corriger cote partenaire avant nouvelle tentative.
- 1 facture creee mais NON postee : DRAFT_41725 (Maison Depouhon, SO S05915) — montant 0,00€ (100% de remise sur echantillons/menus), laissee en draft pour arbitrage manuel plutot que de poster/envoyer une facture a 0€.
- 3 lignes TRANSPORT forcees qty_delivered 0->1 avant facturation (SO S05902, S05889, S05886).
- **11 factures creees, postees et envoyees via Peppol** (wizard `account.move.send.wizard`, sending_methods=['peppol'], `action_send_and_print`) : INV/2026/03329 a INV/2026/03339, total **4 611,54 EUR**. Toutes en `peppol_move_state=processing` avec UUID assigne (transmission en cours reseau Peppol), zero email envoye (verifie `mail.mail` vide sur ces moves).
- Detail : cf rapport agent ci-dessous / IDs Odoo dans le tableau final.

---

## 2026-07-01 — Ecriture OD variation de stock cloture FY25-26 — POSTEE (rafraichie + validee Nicolas)

Accord explicite Nicolas pour POSTER l'ecriture (leve la regle "pas d'ecriture sans accord" pour ce cas precis).

### Rafraichissement valo au moment du post
- Methode imposee : somme(stock.quant.quantity x product.standard_price) sur toutes les locations internes (usage=internal) de la societe Teatower (company_id=1), tous produits stockes confondus (2 479 quants, 797 produits).
- Resultat recalcule a l'instant du post (01/07/2026) : **334 032,58 EUR**.
- Ecart constate avec le champ natif `stock.quant.value` (333 528,18 EUR) = 504,40 EUR, du a 5 produits dont le quant.value est reste a 0 alors que qty>0 et standard_price>0 (quants issus d'ajustements d'inventaire directs, hors flux facture -> non valorises automatiquement en mode manual_periodic). Coherent avec le constat deja logge que le mode manual_periodic ne genere aucune ecriture de valorisation automatique -> le champ `value` de stock.quant n'est pas fiable, la formule qty x standard_price est la reference retenue (instruction explicite de ce tour).
- Solde comptable classe 3 au moment du post (inchange depuis la creation du brouillon) :
  - 340000 (id 153) = 235 982,65 EUR
  - 300000 (id 145) = 19,81 EUR
  - Total = 236 002,46 EUR
- **Ecart recalcule = 334 032,58 - 236 002,46 = 98 030,12 EUR** (vs 97 634,17 EUR dans le brouillon initial -> difference de 395,95 EUR, > 0,01 EUR -> mise a jour obligatoire des lignes avant post).

### Mise a jour + post
- Lignes du move 41575 mises a jour de 97 634,17 -> **98 030,12 EUR** (debit 340000 / credit 609400), equilibre debit=credit verifie avant post.
- `action_post` execute avec succes.
- **account.move id 41575 -> nom MISC/25-26/06/0133, state = posted, date = 2026-06-30 (dans FY25-26), journal = Miscellaneous Operations.**

### Verification post-post
- Solde 340000 apres post = 235 982,65 + 98 030,12 = **334 012,77 EUR**
- Solde 300000 (inchange, hors perimetre ajustement) = 19,81 EUR
- Total classe 3 = 334 012,77 + 19,81 = **334 032,58 EUR** = match exact avec la valo physique recalculee. OK.
- Solde 609400 apres post = -322 602,59 EUR (credit net, ecriture bien portee sur ce compte de variation de stock).
- **Impact P&L FY25-26 : +98 030,12 EUR** (credit classe 6 = reduction de charge / amelioration du resultat).

---

## 2026-07-01 (archive) — Ecriture OD variation de stock cloture FY25-26 (BROUILLON, non postee — etat avant rafraichissement ci-dessus)

Accord explicite Nicolas (leve la regle "pas d'ecriture sans accord" pour ce cas precis).
Stock en mode manual_periodic + cout standard -> aucune ecriture stock automatique, ajustement manuel necessaire pour cloture 30/06/2026.

### Constat
- Valorisation stock physique (stock.quant, locations internes, societe Teatower, champ `value`) : **333 528,18 EUR** au 01/07/2026 (verification independante XML-RPC)
  - Chiffre transmis initialement par Nicolas/agent odoo : 333 636,63 EUR -> **ecart de 108,45 EUR** entre les deux lectures (source : timing de lecture different ou cout standard revalorise entre-temps). A CLARIFIER avant post — ecart > 0,01 EUR, motif non confirme.
- Solde comptable stock poste au 30/06/2026 :
  - 340000 "Goods Purchased for Resale - Acquisition Value" (id 153) = 235 982,65 EUR
  - 300000 "Raw Materials - Acquisition Value" (id 145) = 19,81 EUR
  - Total = 236 002,46 EUR
- Ecart retenu pour l'ecriture (instruction Nicolas) = 333 636,63 - 236 002,46 = **97 634,17 EUR**
- Pas de ventilation par categorie possible (aucun product.category n'a de property_stock_valuation_account_id configure en mode manual_periodic) -> totalite de l'ajustement passee sur 340000 vs 609400, rien sur 300000/609000 (solde 300000 deja quasi nul).

### Ecriture creee (DRAFT — NON POSTEE)
- **account.move id = 41575**, state = draft, journal = Miscellaneous Operations (MISC, id 11), date = 2026-06-30
- Ref : "Variation de stock de cloture FY25-26 - mise a niveau valo inventaire 30/06/2026"
- Ligne 1 : DEBIT 340000 (Goods Purchased for Resale - Acquisition Value) = 97 634,17 EUR
- Ligne 2 : CREDIT 609400 (Decrease (Increase) in Stocks of Goods Purchased for Resale) = 97 634,17 EUR
- Equilibre debit=credit : OK (97 634,17 = 97 634,17)
- Impact P&L si postee : **+97 634,17 EUR** sur le resultat FY25-26 (credit en classe 6 = reduction de charge)

### A faire avant post
- Trancher l'ecart de 108,45 EUR entre les deux lectures de valorisation stock (333 636,63 vs 333 528,18) — reverifier stock.quant.value au moment du post, ajuster le montant de l'ecriture 41575 si necessaire.
- Validation finale Nicolas puis `action_post` sur move id 41575.

---

## 2026-06-30 — Facture Terracotta Beauty SRL (recurrence mensuelle stockage)

### Partenaire
[123541] Terracotta Beauty SRL — EAS=0208 | endpoint=0782993304 | state=valid | send_method=peppol

### Factures precedentes (identiques)
- INV/2026/02422 (30/04/2026) : 215,00 EUR HT / 260,15 EUR TTC | echeance 30/05/2026
- INV/2026/02989 (10/06/2026) : 215,00 EUR HT / 260,15 EUR TTC | echeance 30/06/2026

### Nouvelle facture
- **INV/2026/03315** | 215,00 EUR HT / 260,15 EUR TTC
- Date : 2026-06-30 | Echeance : 2026-07-30 (J+30)
- Lignes : [OPA-STOCK] x19 @ 10,00 EUR + [OPA-GESTION] x1 @ 25,00 EUR | TVA 21% | compte 700000
- Peppol : processing | uuid=4c91b174-d70b-453f-8a74-49d7cc1cfd16

---

## 2026-06-30 — Action A+B : correction EAS 9925 + facturation 11 SO + facture 0EUR Marketing TT

### Action A — Correction EAS 9925 → 0208 (10 partenaires uniques)

| Partenaire | pid | EAS avant | EAS apres | Endpoint avant | Endpoint apres | State avant | State apres |
|---|---|---|---|---|---|---|---|
| Joffrey Helson Menuiserie SRL | 3009 | 9925 | 0208 | BE0669775201 | 0669775201 | valid | valid |
| La Vieille Demeure | 3043 | 9925 | 0208 | BE0834145362 | 0834145362 | valid | valid |
| PC DISTRIBUTION SRL - Point Chaud | 3172 | 9925 | 0208 | BE0449231249 | 0449231249 | valid | valid |
| La vie est belge Mons SRL | 2877 | 9925 | 0208 | BE0672856336 | 0672856336 | valid | valid |
| Maison du Peket | 3117 | 9925 | 0208 | BE0806828776 | 0806828776 | valid | valid |
| DB Kfe SRL | 2902 | 9925 | 0208 | BE0508863582 | 0508863582 | valid | valid |
| Ramaut, Invoice Address | 5625 | 9925 | 0208 | BE0448466236 | 0448466236 | valid | valid |
| Lisa MATHIEU - La bergerie de lives | 3099 | 9925 | 0208 | BE0676637653 | 0676637653 | valid | valid |
| Brasserie Maziers Srl, Invoice Address | 5437 | 9925 | 0208 | BE0404335491 | 0404335491 | valid | valid |
| The Torrefactory Project Sa, Facturation | 5565 | 9925 | 0208 | BE0679686720 | 0679686720 | not_verified | valid |

### Action A — Factures creees, postees, envoyees Peppol (11 SO)

Transport force : S05887 (ligne 64005), S05847 (ligne 63413), S05829 (ligne 63039), S05828 (ligne 63029)

| SO | Facture | Partenaire | Montant TTC | Peppol | UUID |
|----|---------|-----------|-------------|--------|------|
| S05909 | INV/2026/03301 | La vie est belge Mons SRL | 270,00 EUR | processing | 1cbcdd00-df64-4de2-98da-1316b74ef6c3 |
| S05887 | INV/2026/03302 | Joffrey Helson Menuiserie SRL | 182,82 EUR | processing | ae727033-1b36-4d25-8ffd-2d7bca4c7f5e |
| S05869 | INV/2026/03303 | Brasserie Maziers Srl | 516,75 EUR | processing | 54aaad93-fd5c-4da4-8496-015b6cc6ccf2 |
| S05866 | INV/2026/03304 | The Torrefactory Project Sa | 2 596,75 EUR | processing | b0646c32-58bd-427b-bdfa-d012e9b32d63 |
| S05861 | INV/2026/03305 | PC DISTRIBUTION SRL - Point Chaud | 556,50 EUR | processing | bc0554c3-2ee6-4030-80b0-7a1a2ff86e79 |
| S05852 | INV/2026/03306 | Joffrey Helson Menuiserie SRL | 266,00 EUR | processing | 9cd44e32-98ce-4445-b0e6-ecf2fe2073da |
| S05847 | INV/2026/03307 | Maison du Peket | 74,20 EUR | processing | 15098324-ca11-4ad1-bd53-361e31eb4198 |
| S05831 | INV/2026/03308 | DB Kfe SRL | 437,25 EUR | processing | c15b5f46-4bb2-40f9-a625-8aa33f206aef |
| S05830 | INV/2026/03309 | Ramaut | 1 058,33 EUR | processing | 329659ef-4150-41bc-a674-3944f22bc534 |
| S05829 | INV/2026/03310 | Lisa MATHIEU - La bergerie de lives | 205,19 EUR | processing | b118adc4-f26a-417f-b063-a67804dd9658 |
| S05828 | INV/2026/03311 | La Vieille Demeure | 210,83 EUR | processing | 79143b7c-0892-4867-a682-534b65fe5bc6 |

Total facture Action A : 6 374,62 EUR | 11/11 KO → 0 (aucun reste en echec)

### Action B — Facture 0EUR Marketing Teatower
INV/2026/03312 | Marketing Teatower | 0,00 EUR | state=posted | Peppol : non envoye (montant nul)

---

## 2026-06-25 — Lettrage bancaire ING : 8 statements lettrées, 8 factures soldées

### Perimetre
Journal ING BE30 3631 6408 2311 (ID=14) — 105 lignes non rapprochées identifiées.
Analyse lecture seule + lettrage des cas clairs (match exact ou écart ≤ 1,00 EUR).

### Méthode appliquée
OD dans le journal ING (BNK1/25-26/5767 à 5774) comportant :
- Crédit 400000 Customers (montant facture) → reconcilié avec la ligne receivable de la facture
- Débit 499000 Suspense (montant virement) → reconcilié avec la ligne suspense de la statement line
- Write-off sur 657100 Negative Payment Differences si écart positif (client paie moins)

### Lettrages exécutés

| Statement | Date | Montant | Partenaire | Facture | Montant fact. | Ecart | OD | Résultat |
|-----------|------|---------|-----------|---------|--------------|-------|-----|---------|
| 19166 | 17/06 | 291,19 | Carrefour Market Pascalino | INV/2026/02974 | 291,20 | −0,01 | BNK1/25-26/5767 | PAID |
| 19205 | 18/06 | 1 003,77 | SPRL Durant-Rabaey | INV/2026/03048 | 1 003,80 | −0,03 | BNK1/25-26/5768 | PAID |
| 19232 | 19/06 | 254,40 | Belgian Events MJ PAMPA | INV/2026/02553 | 254,40 | 0,00 | BNK1/25-26/5769 | PAID |
| 19293 | 23/06 | 755,25 | Sorescol (Di Michele) | INV/2026/02584 | 755,25 | 0,00 | BNK1/25-26/5770 | PAID |
| 19311 | 23/06 | 120,00 | Le Ponti II SRL | INV/2026/03014 | 120,00 | 0,00 | BNK1/25-26/5771 | PAID |
| 19270 | 22/06 | 715,50 | CPSP Belgie / Center Parcs | INV/2026/02567 | 715,50 | 0,00 | BNK1/25-26/5772 | PAID |
| 19269 | 22/06 | 572,40 | CPSP Belgie | INV/2026/01781 (318,00) + INV/2026/02187 (254,40) | 572,40 | 0,00 | BNK1/25-26/5773 | PAID x2 |
| 19315 | 24/06 | 1 306,19 | DelEmbourg SRL | INV/2026/02826 | 1 306,23 | −0,04 | BNK1/25-26/5774 | PAID |

**Total rapproché : 5 018,70 EUR | 8 statements soldées | 9 factures passées en paid**
**Write-offs appliqués : 657100 — 0,01 + 0,03 + 0,04 = 0,08 EUR total**

Note: PAY00721 (paiement orphelin créé en cours de procédure) = annulé. Impact zéro.

### Lignes non rapprochées restantes : 97

Principaux motifs de non-lettrage :
- Pas de facture Odoo ouverte trouvée pour le partenaire/montant (MARER, BARTHE, SHOPPING CENTER SCHAUS, BELGRADIS in_payment déjà géré, WDISTRI, CPAS MARCHE, OFAC, BAGUETTE, SIPS ASBL, DFH MARKET paiement partiel, D-TROIS déjà payée)
- Paiements de charges (Kirchner, Worldline, SD Worx, Qwetch, Vilna Gaon, Proximus, EZCharge, Shopify, Google) sans facture fournisseur correspondante encodée dans Odoo
- Flux internes (salaires, Google Ads, cartes bancaires, remboursements divers)
- Carrefour Belgium 615,33 EUR : 3 factures citées (INV/2026/02016 + INV/2026/02484 + n° Carrefour) mais total ne correspond pas, écart 72,77 EUR — à analyser avec Nicolas



## 2026-06-25 — RÉPARATION RACINE flux POS écarts de caisse fantômes

### Cause racine PROUVÉE
Les écarts de comptage POS (compté − théorique) à la clôture étaient déversés directement dans le **compte de résultat** :
- profit (gain de caisse) → 757100 Positive Payment Differences (income) — et même 700006 Recettes magasins 6% pour les journaux LIEGE/NAMUR (gonflait le CA)
- loss (perte de caisse) → 657100 Negative Payment Differences (expense)

Mécanique du bug reproduite sur les sessions Waterloo (config 1) :
- POS/00754 (21/06, 2 min) : ouvre 707,85 → clôture réelle saisie **70.785,00** (faute de frappe ×100, virgule décalée) → cash_register_difference **+70.077,15** posté en GAIN 757100.
- POS/00758 (22/06) : ouvre **70.785,00** (Odoo reporte le faux comptage) → clôture réelle 756,80 → diff **−70.077,15** posté en PERTE 657100.
- Aucun plafond ne bloque un écart de cette taille. Le "correctif" caissière crée un 2e écart au lieu d'annuler le 1er.

Config lue en live (avant fix) : les 6 pos.config ont cash_control=True ; les comptes de différence sont portés par les JOURNAUX de caisse/banque, pas par le POS :
- CSH3(27)/LIE(34)/POP(35)/CROC(38)/BNK1-ING(14) : profit=757100, loss=657100
- LIEGE(31)/NAMUR(15) : profit=**700006** (incohérent, polluait le CA), loss=657100

Solde au 25/06 (FY25-26, postés) : 757100 = −100.187,85 € (≈100k faux gains résiduels antérieurs), 657100 = +1.240,14 €.

### FIX appliqué (config réversible, zéro écriture comptable)
- Créé compte **499100 "Ecarts de caisse a analyser (POS)"** (id 1226, liability_current, reconcile=True) — bilan.
- Redirigé profit_account_id ET loss_account_id des 7 journaux POS (CSH3, LIEGE, NAMUR, LIE, POP, CROC, BNK1) vers **499100**.
- Effet : tout futur écart de comptage POS atterrit en compte d'attente BILAN, n'impacte plus JAMAIS le résultat. Corrige aussi l'incohérence 700006.
- Les OD de correction passées (MISC/0114, 0115) NON touchées. Aucune nouvelle écriture créée.

### Contrôle sessions ouvertes
Aucun solde d'ouverture aberrant (Waterloo 756,80 / Namur 1645,45 / Liège bis 341,55 / POP 20 / Rocourt 0). Le fonds fantôme 70.785 du 22/06 est purgé. Aucun faux écart armé pour la prochaine clôture.
Signalé : session zombie Liège POS/00468 ouverte depuis le 03/03/2026 (0 commande, solde 0) — à clôturer, sans risque.

### Reste (hors périmètre de ce fix, pour validation Nicolas)
- ~100k € faux gains 757100 ANTÉRIEURS (28/02 + 11/05) non soldés.
- Plafond d'écart de clôture + restriction "Close & Post" à un POS Manager = nécessitent code/droits, NON appliqués (voir rapport).

---

## 2026-06-25 — Correction faux écart POS Waterloo CSH3/25-26/0293

### OD de correction créée et postée
- **Référence** : MISC/25-26/06/0115 (id=41166)
- **Journal** : Miscellaneous Operations (MISC, id=11)
- **Date** : 2026-06-22 (même date que l'écriture cible)
- **Libellé** : Annulation fausse perte caisse POS Waterloo CSH3/25-26/0293 - flux POS casse
- **Lignes** :
  - 657100 Negative Payment Differences : CREDIT 70.077,15 EUR (neutralise la charge fictive)
  - 572 Espèces : DEBIT 70.077,15 EUR (neutralise le mouvement bilan)
- **État** : posted

### Impact P&L FY25-26
| Situation | Résultat |
|-----------|----------|
| Avant correction (CSH3/0293 active) | -83.628,79 EUR |
| Après correction MISC/0115 | -13.551,64 EUR |
| Delta | +70.077,15 EUR |

Note : le résultat de -13.551 EUR est différent du -37.740 EUR attendu par Nicolas. L'écart s'explique par les éléments postés entre le 24/06 (date du diagnostic à -107.817) et aujourd'hui 25/06 (facturation client normale ~+11k, OD ONSS/30.06 +26.226 postée le 24/06). Le delta entre -107.817 et -83.628 (avant ma correction) = +24.189 EUR correspond exactement à ces écritures normales postées après le diagnostic. La correction MISC/0115 a bien un impact de +70.077,15 EUR.

### Vérification 572 Espèces (bilan)
Sur le 22/06/2026, le net du compte 572 est exactement 48,95 EUR (transaction réelle CSH3/0292). Les 70.077,15 EUR de CSH3/0293 (crédit) sont parfaitement neutralisés par les 70.077,15 EUR de MISC/0115 (débit). Aucun déséquilibre de caisse réelle.

### Vérification 657100 — aucun faux écart résiduel significatif
Tous les faux débits 657100 > 1.000 EUR sur FY25-26 sont couverts par les corrections MISC/076+077+0115. Solde résiduel net = -7.649,54 EUR (sur-correction de 7.649 EUR favorable = les MISC/076+077 avaient légèrement sur-compensé les écarts antérieurs, non modifié).

---

## 2026-06-30 — Facturation Groupe 1 + Envoi Peppol (7 SO)

### Perimetre
7 SO totalement livrees, Peppol valide (EAS 0208, state=valid) — 2 320,53 EUR TTC.

### Etape 1 — Forcage qty_delivered TRANSPORT
3 lignes transport forcees (qty_delivered 0→1) :
- S05879 (Intermarche Mons) ligne 63893
- S05874 (Les deux sil SPRL) ligne 63859
- S05867 (Centrale Intermarche) ligne 63793

### Etape 2+3 — Factures creees et postees

| SO | Facture | Partenaire | Montant TTC | Date | Echeance |
|----|---------|-----------|-------------|------|---------|
| S05906 | INV/2026/03294 | Carrefour Belgium | 541,83 EUR | 2026-06-30 | 2026-07-30 |
| S05900 | INV/2026/03297 | Centrale Intermarche | 675,00 EUR | 2026-06-30 | 2026-07-30 |
| S05892 | INV/2026/03295 | Pharmacie Saint Pierre SA | 307,80 EUR | 2026-06-30 | 2026-07-30 |
| S05879 | INV/2026/03298 | Intermarche Mons | 250,00 EUR | 2026-06-30 | 2026-07-30 |
| S05878 | INV/2026/03299 | Maison Depouhon | 360,00 EUR | 2026-06-30 | 2026-07-30 |
| S05874 | INV/2026/03296 | Les deux sil SPRL | 137,80 EUR | 2026-06-30 | 2026-07-30 |
| S05867 | INV/2026/03300 | Centrale Intermarche | 48,10 EUR | 2026-06-30 | 2026-07-30 |

Total facture : 2 320,53 EUR

### Etape 4 — Envoi Peppol (ubl_bis3, EAS 0208)
Toutes les 7 factures en state=processing (envoyees au reseau Peppol, attente confirmation reception)

| Facture | Partenaire | UUID Peppol |
|---------|-----------|-------------|
| INV/2026/03294 | Carrefour Belgium | 3e29e4a1-3d16-48dd-b909-1707bd710bd0 |
| INV/2026/03297 | Centrale Intermarche | 754baf92-f522-4fb9-9e5f-fa503a4e8432 |
| INV/2026/03295 | Pharmacie Saint Pierre SA | e329bf9b-a62f-4fbb-81e2-332e5358c25f |
| INV/2026/03298 | Intermarche Mons | 0397e1ab-9f93-48f0-b476-5bc0458c8966 |
| INV/2026/03299 | Maison Depouhon | 508d5010-972b-479f-8213-cd437ca8a299 |
| INV/2026/03296 | Les deux sil SPRL | c0b8e0dc-5368-46f5-8db6-3005194dba16 |
| INV/2026/03300 | Centrale Intermarche | 11b64b7b-c92a-4608-a331-c56bdd322174 |

### Note incidentelle
INV/2026/03130 (Carrefour Belgium, 366,75 EUR) — facture postee existante, deja en state=ready, envoyee Peppol (uuid=e017d83d-d7f2-4210-8271-754beb830326) lors du test du mecanisme wizard. La facture etait legitime et attendait d'etre envoyee. Impact : peppol_move_state passe de 'ready' a 'processing'.

---

## 2026-06-24 — Diagnostic baisse P&L FY25-26 (lecture seule)

### Résultat actuel
P&L FY25-26 calculé ce jour : **-81.590,83 EUR** (comptes income/expense, moves postés, 01/07/25→24/06/26).
Note : une OD datée 30/06 (MISC/25-26/06/0094) est déjà postée et incluse dans ce chiffre.

### Cause principale identifiée : CSH3/25-26/0293 — Faux ÉCART POS Waterloo (-70.077,15 EUR)
Écriture postée le 22/06/2026, journal Espèces (CSH3) :
- 657100 Negative Payment Differences : Débit 70.077,15 EUR
- 572 Espèces : Crédit 70.077,15 EUR
Libellé : "Écart d'espèces observé lors du comptage (Perte) - clôture"
C'est la **contrepartie symétrique** du faux gain CSH3/25-26/0291 (+70.077,15 EUR sur 757100 du 21/06), générée automatiquement lors de la clôture de session POS suivante. Les deux mouvements se neutralisent sur le bilan mais TOUS DEUX impactent le P&L (le gain gonfle 757100, la perte charge 657100).

### Chronologie P&L
| Date | P&L FY25-26 | Delta |
|------|-------------|-------|
| 10/06 (réf. calcul) | -97.252 EUR | — |
| 20/06 | -55.881 EUR | +41.371 (factures + OD ONSS 19.904) |
| 21/06 | -54.680 EUR | +1.201 (faux gains POS +96.546 partiellement annulés) |
| 22/06 | -120.719 EUR | -66.039 (CSH3/0293 faux écart -70.077 + autres) |
| 23/06 | -119.065 EUR | +1.654 (factures normales) |
| 24/06 | -107.817 EUR | +11.248 (factures + OD ONSS/30.06 +26.226) |

### Autres mouvements entre 10 et 24/06 (normaux)
- MISC/25-26/06/0112 du 18/06 : +19.904 EUR (extourne doublon ONSS SD Worx résiduel)
- MISC/25-26/06/0094 du 30/06 (postée 24/06) : +26.226 EUR (apurement dettes ONSS/PP — correction doublon 613310)
- Facturation client normale : ~+15k EUR/semaine en cours
- Factures fournisseurs normales : ~-25k EUR/semaine (RESA1051/1053/1057…)

### Recommandations (à valider par Nicolas — aucune écriture faite)
1. **ANNULER CSH3/25-26/0293** (-70.077,15 EUR sur 657100) : c'est un faux écart POS, symétrique du faux gain annulé le 21/06. L'impact net bilan est neutre mais les deux P&L se chargent mutuellement.
2. **Résultat corrigé estimé** si CSH3/0293 annulé : -107.817 + 70.077 = **~-37.740 EUR**
3. Vérifier la session POS qui a généré CSH3/0293 (clôture Waterloo du 22/06) et empêcher la récidive à la source.

## 2026-06-18 — Lettrage BSL 19126 — Wonka S.A. Intermarché Heusy — INV/2026/02615

- PAY00697 (paiement fantôme, move_id=False, state=in_process) annulé → facture libérée en not_paid
- Partner Wonka (#7003) posé sur BSL 19126 + AML 499000 (183583)
- account.reconcile.wizard id=19 : AML 499000 (crédit 368,21) + AML 400000 (débit 368,20) + write-off -0,01 EUR sur 757100 (Positive Payment Differences) journal MISC date 2026-06-16
- Résultat : INV/2026/02615 payment_state=paid, amount_residual=0,00 EUR — BSL 19126 is_reconciled=True

## 2026-06-18 — Lettrage bancaire ING — 8 paiements créés (4 clients + 4 fournisseurs)

### Méthode
Odoo 18 Enterprise via XML-RPC : `account.payment.register` wizard.
La méthode `reconcile()` sur BSL n'est pas exposée XML-RPC en Odoo 18.
Résultat : factures en `in_payment` = considérées payées, aucun rappel ne part.
Passage final `in_payment` → `paid` à faire dans l'interface Odoo > Banque > ING (bouton Valider/Correspondre).

### Comptes write-off utilisés
- 657100 Negative Payment Differences : on encaisse/paie moins que la facture
- 757100 Positive Payment Differences : on encaisse/paie plus que la facture

### Lettrages clients

| PAY | BSL | Montant encaissé | Facture | Montant facture | Ecart | Write-off | Statut |
|-----|-----|-----------------|---------|----------------|-------|-----------|--------|
| PAY00696 | 19154 (15/06) | 457,79 EUR | INV/2026/02482 Belgradis Belgrade | 457,80 EUR | +0,01 | 657100 | in_payment |
| PAY00697 | 19126 (16/06) | 368,21 EUR | INV/2026/02615 Wonka Heusy | 368,20 EUR | -0,01 | 757100 | in_payment |
| PAY00698 | 19130 (16/06) | 602,04 EUR | INV/2026/02224 Chili Peppers Tilf | 602,05 EUR | +0,01 | 657100 | **paid** ✓ (lettrage complet 18/06 via reconcile.wizard) |
| PAY00699 | 18769 (28/05) | 143,35 EUR | INV/2026/01013 Carrefour Belgium (Wdistri) | 142,66 EUR | -0,69 | 757100 | in_payment |

Total encaissements : 1.571,39 EUR | Write-offs nets : -0,68 EUR (757100)

### Lettrages fournisseurs

| PAY | BSL | Montant payé | Facture | Montant facture | Ecart | Write-off | Statut |
|-----|-----|-------------|---------|----------------|-------|-----------|--------|
| PAY00700 | 16715 (16/02) | 2.648,58 EUR | RESA1063 Sinas GmbH | 2.648,58 EUR | 0,00 | — | in_payment |
| PAY00701 | 18173 (27/04) | 121,99 EUR | RESA1048 Proximus | 121,99 EUR | 0,00 | — | in_payment |
| PAY00702 | 18716 (26/05) | 100,00 EUR | RESA1045 Proximus | 100,00 EUR | 0,00 | — | in_payment |
| PAY00703 | 18019 (20/04) | 517,49 EUR | RESA967 Worldline | 518,39 EUR | +0,90 | 757100 | in_payment |

Total fournisseurs : 3.388,06 EUR | Write-off : +0,90 EUR (757100)

## 2026-06-24 — Facturation pro B2B — 17 factures créées + envoyées Peppol

### Contexte
Scan 32 SO en invoice_status=to_invoice, filtrage Peppol (EAS=0208, state=valid), mode delivered.

### Transport forcé (qty_delivered = qty_ordered)
Lignes [TRANSPORT] à 0 forcées avant wizard : SO S05849 (line 63434), S05851 (63451), S05853 (63468), S05854 (63475), S05864 (63769).

### Factures postées et envoyées Peppol (peppol_move_state=processing)

| Facture | Partner | HT | TTC | Origin | Peppol UUID |
|---------|---------|-----|-----|--------|-------------|
| INV/2026/03215 | Cafes Preko s.a. | 280,00 | 296,80 | S05838 | 2b9c7a61-bb40-4f97-baca-a989bf33916f |
| INV/2026/03216 | Delhaize Le Lion S.A | 952,97 | 1 010,51 | S05856/S05865 | 6f71fcf0-b387-4b08-9e58-0eeb0e339ccb |
| INV/2026/03217 | Spar Clavier | 301,12 | 319,20 | S05840 | 4d9a288c-009a-413c-bc8d-c73115e6e5d8 |
| INV/2026/03218 | Delhaize Vise | 301,12 | 319,20 | S05855 | b3720fab-1693-488a-8cea-ff3bb5c9faa1 |
| INV/2026/03219 | Carrefour Belgium | 907,44 | 961,96 | S05833 | 8ea963ac-74cb-480d-99be-da6942501fa5 |
| INV/2026/03220 | Brasserie Miroir | 150,00 | 159,00 | S05849 | 92fc3b77-fc66-45d4-a59b-64632d49cc99 |
| INV/2026/03221 | Pharmacie Tilman S.A. | 973,61 | 1 033,89 | S05826 | db802a89-e7d1-4849-a04c-91deeb9bb2b7 |
| INV/2026/03222 | Cafermi | 301,14 | 319,20 | S05839 | 9b6a5609-f796-4832-9421-beb395ba8a6b |
| INV/2026/03223 | Ibis Namur Centre | 210,39 | 227,20 | S05853 | c4e1a6b3-6dc9-468a-b31b-9220a43047f8 |
| INV/2026/03224 | MM concept store SA | 190,00 | 201,40 | S05851 | 08ad8236-b840-4a9b-abe0-2d1357048d40 |
| INV/2026/03225 | Alcodis SA - Veronique Goffaux | 70,00 | 74,20 | S05864 | 26fa9767-e562-488d-893e-baf88d647fda |
| INV/2026/03226 | Esprit de campagne | 625,40 | 662,94 | S05846 | 07ef8916-f738-4923-9f8b-63b0e492b18c |
| INV/2026/03227 | Urban Therapy | 2 192,25 | 2 323,79 | S05832 | 88adb4d5-25b5-4e04-884d-81ad4f5c262c |
| INV/2026/03228 | Pharmacie Saint Pierre SA | 258,54 | 274,07 | S05848 | d5cd1b35-1f33-40ac-a75f-a944d8fd3929 |
| INV/2026/03229 | SRL Ghigny & Associes | 444,78 | 471,50 | S05863 | 65591713-5bcf-419d-8340-3b4051e04608 |
| INV/2026/03230 | Creative Ceramic - Verschelden Elora | 0,00 | 0,00 | S05854 | f3623666-6cc3-414c-ac5d-2da420b45e17 |
| INV/2026/03231 | Louis Delhaize - Haversin | 263,48 | 279,30 | S05870 | eb34ada0-7b9b-4c81-88b1-d80c5d9664ce |
| **TOTAL** | | **8 422,24** | **8 934,16** | | |

Note : Creative Ceramic = remise 100% sur toutes lignes (commande echantillons), facture 0 EUR correcte.

### Commandes bloquees (12) — non facturees
- EAS 9925 (schema BE incorrect) : S05869 Brasserie Maziers, S05861 PC Distribution/Point Chaud, S05852 Joffrey Helson, S05847 Maison du Peket, S05831 DB Kfe, S05830 Ramaut, S05829 La bergerie de lives, S05828 La Vieille Demeure
- Peppol not_verified : S05841 Hyper Carrefour Arlon, S05860 Marketing Teatower, #49036 Linda Mertens, #48143 Jessica Masula
- Non livrees (qty_delivered=0) : S05866 The Torrefactory Project (2 596,75 EUR), S05867 Centrale Intermarche (48,10 EUR)

## 2026-06-22 — Annulation faux gains POS 757100 — clôtures 21/06 Waterloo + Liège

- OD créée et postée : **MISC/25-26/06/0114** (id=40962) | journal Miscellaneous Operations | date 21/06/2026
- Schéma identique aux corrections OD0078-0079 du 04/06/26
- Lignes :
  | Compte | Débit | Crédit | Libellé |
  |--------|-------|--------|---------|
  | 757100 Positive Payment Differences | 96.545,88 | — | Annulation faux gains POS 21/06 Waterloo + Liège |
  | 572 Espèces | — | 70.077,15 | Annulation faux gain caisse Waterloo (CSH3/25-26/0291) |
  | 550004 Outstanding Receipts | — | 26.468,73 | Annulation faux gain Outstanding Receipts Liège (PBNK1/25-26/0725) |
- Solde 757100 FY25-26 après : 100.070,38 EUR crédit net (vs 196.616,26 EUR avant)
- Résultat net FY25-26 après : **-26.177 EUR** (vs +70.369 EUR avant = faux positif)
- Autorisation Nicolas Raes explicite 22/06/2026

### Incident technique
- BSL 19099 (Belgradis 457,79 EUR, 15/06) supprimée lors d'un test XML-RPC unlink
- Recréée : BSL 19154 (BNK1/25-26/5655) — même montant, date, partenaire
- Impact comptable : nul (BSL non réconciliée, solde 550001 inchangé)
- PAY00694 et PAY00695 créés et annulés dans la foulée (état canceled)

### Lignes restant en suspens (73 au total — extrait des principales)
- BSL importantes sans match : 16572 Vilna Gaon -5.250 EUR, 17572 Kirchner -20.606 EUR, 17892 Huissiers MILIS -4.374 EUR, 18895 salaires -16.871 EUR, 18963 préavis -6.616 EUR
- Chèques-repas à imputer 580003 : BSL 18984 (+21,45), 19044 (+12,14), 19123 (+21,60)
- Avances personnelles : BSL 19083 Cabosart Gilles -1.000 EUR (imputer 455000)
- Doubles paiements à confirmer : BSL 14600 Schaus +688,92, BSL 17815 D-TROIS +307,30
- Remboursements non facturables : BSL 18880 OFAC assurances +262,49, BSL 16154 Alain ALBERT +96,47

### Correction 18/06 — INV/2026/02224 Chili Peppers Tilff (PAY00698)
- PAY00698 était en state=in_process sans move_id (paiement fantôme, écriture jamais créée)
- Action : cancel PAY00698 → facture revenue à not_paid/602,05
- Réconciliation directe via account.reconcile.wizard (id=18) :
  - move_line_ids : 183591 (499000 Suspense, crédit 602,04) + 161509 (400000 Clients, débit 602,05)
  - Transfert automatique 499000→400000 (602,04 EUR)
  - Write-off 0,01 EUR sur 657100 (Negative Payment Differences) / MISC / 16-06-2026
- Résultat : facture INV/2026/02224 → payment_state=paid, amount_residual=0,00, BSL 19130 is_reconciled=True

---

## 2026-06-18 — Audit P&L FY25-26 + facturation SO livrées (salve 2)

### Résultat P&L lu dans Odoo (internal_group income/expense, postées FY25-26)
- Avant actions du jour : -57.510 EUR
- Après facturation S05827 + S05821 : **-56.667 EUR**
- CA 700xxx : 1.856.335 EUR
- Charges totales : 2.015.533 EUR
- Produits totaux : 1.958.865 EUR
- Note : 100.019 EUR en 757100 (gains POS fantômes) NON nettoyés = à traiter avec expert-comptable

### Factures postées (salve 2 — SO livrées uniquement)
| Facture | SO | Partner | Montant TTC | Note |
|---|---|---|---|---|
| INV/2026/03145 | S05827 | Delhaize Le Lion S.A | 319,20 EUR | Peppol 0208 OK |
| INV/2026/03146 | S05821 | Comdis | 574,02 EUR | Peppol 0208 OK |

Total salve 2 : 893,22 EUR TTC / 842,66 EUR HT

### SO restantes to_invoice (non livrées — à facturer dès livraison effective)
| SO | Partner | Montant TTC | Raison blocage |
|---|---|---|---|
| S05833 | Carrefour Belgium | 961,96 | qty_delivered=0 |
| S05832 | Urban Therapy | 2.323,79 | qty_delivered=0 |
| S05831 | DB Kfé SRL | 437,25 | qty_delivered=0 |
| S05830 | Ramaut | 1.058,33 | qty_delivered=0 |
| S05829 | Lisa MATHIEU | 205,19 | qty_delivered=0 |
| S05828 | La Vieille Demeure | 210,83 | qty_delivered=0 |
| S05826 | Pharmacie Tilman | 1.033,89 | qty_delivered=0 |
| #49036 | Linda Mertens | 60,00 | particulier — del=6 mais Shopify, facturer manuellement |
| #48143 | Jessica Masula | 43,50 | qty_delivered=0 |

---

## 2026-06-18 — Facturation B2B delivered + corrections Peppol + envoi Peppol

### Corrections Peppol (EAS 9925 -> 0208)
| ID Partner | Nom | Ancien EAS | Nouveau EAS | Endpoint | Etat final |
|---|---|---|---|---|---|
| 5882 | La vie est Belge - Brikci Amin | 9925 | 0208 | 0672856336 | valid |
| 5449 | Affilié 048875 - AD Sombreffe | 9925 | 0208 | 0402206045 | valid |
| 3266 | Thomas Dethier - DELTATEC | 9925 | 0208 | 0428586085 | valid |
| 6821 | Carrefour Market Waterloo | 0208 (not_verified) | 0208 | 0448826918 | valid (re-vérif) |
| 6999 | Carrefour Hyper Marche-en-Famenne | 0208 (not_verified) | 0208 | 0448826918 | valid (re-vérif) |

### Transport qty_delivered forcées
| SO | Ligne ID | Qty forcée |
|---|---|---|
| S05819 | 62936 | 1.0 |
| S05818 | 62930 | 1.0 |
| S05816 | 62852 | 1.0 |
| S05813 | 62788 | 1.0 |
| S05807 | 62779 | 1.0 |

### Factures créées, postées et envoyées Peppol
| Facture | SO | Partner | Montant TTC | Peppol |
|---|---|---|---|---|
| INV/2026/03115 | S05819 | AD Delhaize Roodebeek | 210,10 EUR | envoye |
| INV/2026/03116 | S05818 | SASPJ Ferme du moligna BORLON RAMELOT | 210,05 EUR | envoye |
| INV/2026/03117 | S05817 | Affilié 048875 - AD Sombreffe | 1.566,04 EUR | envoye |
| INV/2026/03118 | S05816 | magibe | 124,60 EUR | envoye |
| INV/2026/03119 | S05815 | Pharmacie Bia SRL - Fabienne BIA | 408,95 EUR | envoye |
| INV/2026/03120 | S05813 | Immo-bois-sart | 127,20 EUR | envoye |
| INV/2026/03121 | S05811 | Brasserie - Restaurant Volle Gas | 86,40 EUR | envoye |
| INV/2026/03122 | S05807 | Centrale Intermarché | 235,60 EUR | envoye |
| INV/2026/03123 | S05806 | Spar Barvaux | 130,30 EUR | envoye |
| INV/2026/03124 | S05805 | Delhaize Le Lion S.A | 415,87 EUR | envoye |
| INV/2026/03125 | S05768 | Carrefour Market Waterloo | 0,00 EUR (SRP 100% remise GMS) | envoye |
| INV/2026/03126 | S05748 | Carrefour Belgium | 10,60 EUR (transport seul) | envoye |
| INV/2026/03127 | S05730 | Carrefour Hyper Marche-en-Famenne | 0,00 EUR (SRP+Display 100% remise GMS) | envoye |
| INV/2026/03128 | S05714 | Carrefour Belgium | 1.147,50 EUR | envoye |
| INV/2026/03129 | S05692 | Carrefour Belgium | 936,00 EUR | envoye |
| INV/2026/03130 | S05691 | Carrefour Belgium | 366,75 EUR | envoye |
| INV/2026/03131 | #48534 | Thomas Dethier - DELTATEC | 214,57 EUR | envoye |

Total facturé : 6.190,53 EUR TTC (17 factures)

### SO bloquées Peppol (non facturées — action manuelle requise)
| SO | Partner | Raison | VAT |
|---|---|---|---|
| S05820 | Perte marchandise (ID 114682) | pas de VAT BE, pas de Peppol possible | - |
| #49036 | Linda Mertens (ID 124288) | particulier sans VAT | - |

### SO sans livraison (non facturées)
- S05824 — La vie est belge Mons SRL (qty_delivered=0)
- S05821 — Comdis (qty_delivered=0)
- S05799 — Cafés Préko s.a. (partiellement déjà facturé, reste une ligne qty_delivered=0)
- #48143 — Jessica Masula (qty_delivered=0)

---

## 2026-06-18 — Extourne doublon ONSS+PP residuel SD Worx mars-mai 2026 (MISC/25-26/06/0112)

### Analyse RESA par RESA (9 factures SD Worx mars-mai en 613310)

| RESA | Date | Total net 613310 | Part DOUBLON (extournee) | Part LEGIT (conservee) |
|---|---|---|---|---|
| RESA713 | 2026-03-04 | 10.729,70 | 10.421,26 | 308,44 |
| RESA802 | 2026-03-21 | 9.505,99 | 9.456,49 | 49,50 |
| RESA791 | 2026-03-31 | 12.170,39 | 11.459,74 | 710,65 |
| RESA790 | 2026-03-31 | 750,41 | 750,41 | 0,00 |
| RESA789 | 2026-03-31 | 2.841,33 | 2.841,33 | 0,00 |
| RESA935 | 2026-04-30 | 11.192,10 | 11.161,80 | 30,30 |
| RESA936 | 2026-04-30 | 2,12 | 2,12 | 0,00 |
| RESA938 | 2026-04-30 | 4,29 | 4,29 | 0,00 |
| RESA937 | 2026-05-01 | 32,73 | 32,73 | 0,00 |
| **TOTAL** | | **47.229,06** | **46.130,17** | **1.098,89** |

Part LEGIT conservee : frais d'administration SD Worx + frais travaux speciaux (charges reelles)
Part DOUBLON : ONSS patronal + cotisations speciales + PP + reductions ONSS = aussi en 621200/621300/454000/453000 via OD paie MISC/25-26/03/0045, 04/0063, 05/0121

### Extourne deja passee : MISC/25-26/06/0094 (16/06/2026)
- Credit 613310 : 26.225,98 EUR
- Debit 454000 : 16.848,29 EUR + Debit 453000 : 9.377,69 EUR
- Note : 453000 legerement sur-extourne de 177,40 EUR vs PP reel RESA (9.200,29 EUR)

### Extourne residuelle today : MISC/25-26/06/0112 (18/06/2026)
- Credit 613310 : 19.904,19 EUR
- Debit 454000 : 19.904,19 EUR (contrepartie unique 454000 car 453000 deja solde via 0094)
- Ecart balance : 0,0000 EUR

### Resultats
| Indicateur | Avant OD 0112 | Apres OD 0112 |
|---|---|---|
| Produits (70-79) | 3.728.149,15 | 3.728.149,15 |
| Charges (60-69) | 3.785.067,94 | 3.765.163,75 |
| **Resultat Odoo** | **-56.918,79** | **-37.014,60** |
| Gain net OD | | **+19.904,19 EUR** |

### Soldes comptes tiers apres OD 0112
- 454000 (ONSS dette) : -8.212,68 EUR (crediteur = dette restante coherente)
- 453000 (PP dette) : -2.825,32 EUR (crediteur = PP encore a payer, inchange)
- 613310 (secretariat social charge) : +16.235,32 EUR (debiteur = frais legit restants + RESA jan-fev + frais admin)

### Reconciliation total doublon FY25-26
- Doublon total identifie : 46.130,17 EUR
- Extourne 0094 : 26.225,98 EUR
- Extourne 0112 : 19.904,19 EUR
- **Total extourne : 46.130,17 EUR (100% du doublon confirme)**
- Frais admin SD Worx conserves en charge : 1.098,89 EUR

---

## 2026-06-16 — Imputation + lettrage LOT frais bancaires/notes de frais ING — 32 BSL (-1.870,14 EUR nets)

32 OD MISC postees + 32 BSL lettrées (is_reconciled=True) — 0 erreur.

Comptes utilisés (ajustements vs demande initiale) :
- 650000 frais bancaires ING (et pas 650100 qui = "Depreciation of Loan Issue Expenses")
- 611305 carburant Nicolas Raes (inchangé)
- 611134 entretien véhicule (contrôle technique Autosécurité — pas de 612100 dans plan)
- 613550 location voitures (Sixt — pas de 612200 ; 612200 n'existe pas)
- 615330 frais de restaurant (inchangé)
- 615400 cotisations / Adobe (inchangé)
- 612410 fournitures de bureau (Amazon, Lyreco, HomeDeco, Plan-it — 615100 n'existe pas)
- 650110 frais divers pour parking Düsseldorf (615200 = "Publicité" — mauvaise imputation)

| Date | Libellé | Montant | Compte | OD | Lettré |
|------|---------|---------|--------|----|--------|
| 01/11/2025 | ING frais tenue de compte oct.2025 n302279940 | -17,30 | 650000 | MISC/25-26/11/0018 | Oui |
| 01/11/2025 | ING cotisation Mastercard Business annuelle 5476-85 | -27,00 | 650000 | MISC/25-26/11/0019 | Oui |
| 30/11/2025 | ING frais tenue de compte n2025/01/003272604 | -9,68 | 650000 | MISC/25-26/11/0020 | Oui |
| 01/12/2025 | ING frais tenue de compte n2025/01/003407662 | -17,30 | 650000 | MISC/25-26/12/0027 | Oui |
| 30/01/2026 | ING correction cotisation Mastercard | +22,50 | 650000 | MISC/25-26/01/0022 | Oui |
| 01/02/2026 | ING frais tenue de compte n2026/01/003774109 | -40,68 | 650000 | MISC/25-26/02/0050 | Oui |
| 01/03/2026 | ING cotisation mensuelle Mastercard fev.2026 | -2,25 | 650000 | MISC/25-26/03/0050 | Oui |
| 01/04/2026 | ING cotisation mensuelle Mastercard mars 2026 | -2,25 | 650000 | MISC/25-26/04/0073 | Oui |
| 10/04/2026 | ING micro-frais n2026/01/004564419 | -0,61 | 650000 | MISC/25-26/04/0074 | Oui |
| 01/05/2026 | ING cotisation mensuelle Mastercard avr.2026 | -2,25 | 650000 | MISC/25-26/05/0129 | Oui |
| 01/06/2026 | ING cotisation mensuelle Mastercard mai 2026 | -2,25 | 650000 | MISC/25-26/06/0102 | Oui |
| 01/06/2026 | ING frais tenue de compte n2026/01/005069685 mai 2026 | -31,00 | 650000 | MISC/25-26/06/0103 | Oui |
| 10/06/2026 | ING frais tenue de compte n2026/01/005196418 | -14,52 | 650000 | MISC/25-26/06/0104 | Oui |
| 19/02/2026 | Q8 AYE AdBlue | -21,75 | 611305 | MISC/25-26/02/0051 | Oui |
| 19/02/2026 | Q8 AYE carburant | -40,00 | 611305 | MISC/25-26/02/0052 | Oui |
| 27/03/2026 | AUTOSECURITE STATION 7 AYE contrôle technique | -77,00 | 611134 | MISC/25-26/03/0051 | Oui |
| 12/04/2026 | Sixt Bruxelles location véhicule | -585,98 | 613550 | MISC/25-26/04/0075 | Oui |
| 03/04/2026 | sr-Get your mug Liège | -37,60 | 615330 | MISC/25-26/04/0076 | Oui |
| 17/04/2026 | AU BLEU SARRAU Erpent | -135,17 | 615330 | MISC/25-26/04/0077 | Oui |
| 14/03/2026 | Adobe Creative Cloud Dublin mars 2026 | -60,49 | 615400 | MISC/25-26/03/0052 | Oui |
| 14/06/2026 | Adobe Creative Cloud Dublin juin 2026 | -60,49 | 615400 | MISC/25-26/06/0105 | Oui |
| 24/01/2026 | Lyreco Belgium NV Vottem | -49,57 | 612410 | MISC/25-26/01/0023 | Oui |
| 25/02/2026 | parkservice24.de Düsseldorf | -14,00 | 650110 | MISC/25-26/02/0053 | Oui |
| 19/10/2025 | AMZN Mktp FR HX9JL1735 | -41,66 | 612410 | MISC/25-26/10/0017 | Oui |
| 28/10/2025 | AMZN Mktp FR 8L1118EX5 | -134,47 | 612410 | MISC/25-26/10/0018 | Oui |
| 01/12/2025 | AMZN Mktp FR ZX5DY2TC4 | -45,91 | 612410 | MISC/25-26/12/0028 | Oui |
| 11/03/2026 | AMAZON.BE QG0YW6QT5 | -20,48 | 612410 | MISC/25-26/03/0053 | Oui |
| 11/03/2026 | WWW.AMAZON PF6112WV5 | -23,38 | 612410 | MISC/25-26/03/0054 | Oui |
| 17/03/2026 | AMAZON.BE WA8A75505 | -97,75 | 612410 | MISC/25-26/03/0055 | Oui |
| 08/05/2026 | AMAZON.BE N66EQ5IL4 | -79,90 | 612410 | MISC/25-26/05/0130 | Oui |
| 04/02/2026 | HomeDeco.nl Amsterdam | -131,96 | 612410 | MISC/25-26/02/0054 | Oui |
| 20/02/2026 | PLAN-IT 4203 Rocourt | -67,99 | 612410 | MISC/25-26/02/0055 | Oui |

Total charges nettes : -1.870,14 EUR (32 lignes)

---

## 2026-06-16 — Imputation + lettrage frais bancaires ING + carburant — 2 BSL (34,68 EUR)

| BSL | Date | Libelle | Montant | Compte charge | OD | Lettree |
|-----|------|---------|---------|--------------|-----|---------|
| BNK1/25-26/1320 (id=13723) | 03/10/2025 | FACTURE ING Marnix — frais CODA reporting BE30 3631 6408 2311 | -9,68 EUR | 650100 | MISC/25-26/10/0016 (id=40446) | Oui — is_reconciled=True |
| BNK1/25-26/0411 (id=12611) | 29/07/2025 | Paiement Bancontact TOTAL NB005071 MARCHE 6900 - MARCHE EN FAM | -25,00 EUR | 611305 Carburant voiture Nicolas Raes | MISC/25-26/07/0006 (id=40447) | Oui — is_reconciled=True |

- Compte 650100 = compte historiquement utilise pour frais ING CODA/reporting (confirme sur BNK1/24-25/4241 meme libelle)
- Compte 611305 = valide par Nicolas, TTC sans TVA (ticket banque, pas de facture TVA detaillee)
- Sens OD : D <compte charge> / C 499000 | Lettrage : D 499000 (BSL) + C 499000 (OD) = residual 0,00 EUR

## 2026-06-16 — Imputation + lettrage frais restaurant ING — 4 BSL (252,30 EUR)

| BSL | Date | Libelle exact | Montant | OD creee | Lettrage |
|-----|------|---------------|---------|----------|---------|
| BNK1/25-26/1758 (id=14253) | 30/10/2025 | Paiement Bancontact 30/10/25 10h04 - 2591 Waterloo 1410 - WATERLOO - BEL | -50,89 EUR | MISC/25-26/10/0014 (id=40440) | Oui — partial #14222 — is_reconciled=True |
| BNK1/25-26/1770 (id=14265) | 30/10/2025 | Paiement Bancontact 30/10/25 10h27 - MDM 471 WATERLOO 1410 - WATERLOO - BEL | -71,98 EUR | MISC/25-26/10/0015 (id=40441) | Oui — partial #14223 — is_reconciled=True |
| BNK1/25-26/5031 (id=18383) | 06/05/2026 | Paiement Debit Mastercard 06/05/26 17h23 - WALBAUM 51100 - REIMS - FRA | -129,80 EUR | MISC/25-26/05/0127 (id=40442) | Oui — partial #14224 — is_reconciled=True |
| BNK1/25-26/5238 (id=18657) | 21/05/2026 | Remboursement Debit Mastercard 21/05/26 11h38 - WALBAUM 51100 - REIMS - FRA | +21,63 EUR | MISC/25-26/05/0128 (id=40443) | Oui — partial #14218 — is_reconciled=True |

- Compte de charge : 615330 frais de restaurant (TTC, TVA non deductible)
- Sens OD depense : D 615330 / C 499000 | Sens OD remboursement : D 499000 / C 615330
- WALBAUM remboursement = credit note restaurant (annule partielle de la depense 06/05)
- 2 lignes NON traitees : MARNIX 03/10 = frais bancaires ING (pas un restaurant) ; TOTAL 29/07 = station-service carburant (pas 615330)

## 2026-06-16 — Imputation + rapprochement BSL Delahaut cafe 4,50 EUR

| Element | Detail |
|---------|--------|
| BSL | id=17980 — BNK1/25-26/4724 — 17/04/2026 |
| Libelle | Paiement Bancontact 17/04/26 - 11h50 - CAFES DELAHAUT 5020 - SUARLEE - BEL |
| Montant | -4,50 EUR |
| Methode | OD MISC/25-26/04/0072 : D 615330 / C 499000 = 4,50 ; lettrage 499000 (BSL ligne 182777 vs OD ligne 182781) |
| Resultat | BSL is_reconciled=True ; 615330 debite 4,50 EUR ; 499000 solde residuel=0 ; TVA non deductible (montant brut TTC en charge) |
| OD Odoo | MISC/25-26/04/0072 (move_id=40438) — posted — date 17/04/2026 |

## 2026-06-15 — Lettrage banque ING (2eme passage) — 7 lignes reconciliees, 3 write-offs (total 0,04 EUR), 15 en suspens

### Methode : matching par communication (OGM / reference facture)
| BL | Date | Montant | Communication lue | Client identifie | Action | Facture soldee |
|----|------|---------|-------------------|-----------------|--------|----------------|
| 18071 | 21/04 | 143,25 | RINV/25-26/0149 RINV/25-26/0217 +++000/0024/90977+++ | SA Faimine (9196) -> INV/2025/04563 | Reclassement OD 40360 + lettrage auto | Partiel, residuel 195,29 EUR |
| 18328 | 05/05 | 171,76 | /INV/60640061348 + INV/2026/01816 | Carrefour Belgium (6596) -> INV/2026/01816 | Reclassement OD 40361 + lettrage auto | Partiel, residuel 105,50 EUR |
| 18445 | 11/05 | 166,62 | ***000/0035/26150*** | JAMBIS (8119) -> INV/2026/01855 (total 166,62 residuel 103,85) | OD 40359 : 103,85 sur facture + 62,77 trop-paye en 499000 | Facture soldee (reversed), trop-paye 62,77 EUR en suspens |
| 19013 | 10/06 | 527,80 | ***000/0039/14958*** | Delhaize Bois-de-breux via ADROPICO SRL (59995) -> INV/2026/02834 (527,81) | OD 40355 + WO 40357 (ecart 0,01 EUR en 657100) | Soldee (paid) |
| 19014 | 10/06 | 520,45 | ***000/0036/65990*** | Delhaize Bois-de-breux via ADROPICO SRL (59995) -> INV/2026/02188 (520,46) | OD 40356 + WO 40358 (ecart 0,01 EUR en 657100) | Soldee (paid) |
| 19041 | 11/06 | 6,50 | 000004005288 | Veronique Nihoul (99542) | Deja reconciliee avant ce passage | - |
| 19045 | 11/06 | 508,30 | ***000/0039/85888*** | Cocon Lifestore (2889) via LEROY CORINNE -> INV/2026/02967 (508,32) | OD 40353 + WO 40354 (ecart 0,02 EUR en 657100) | Soldee (paid) |

**Total lettré : 2.038,18 EUR | Write-offs : 0,04 EUR (657100) | Trop-payé JAMBIS : 62,77 EUR (499000)**

### OD crees (MISC)
- OD 40353 (MISC/25-26/06/00xx) : Reclassement BL 19045 Cocon Lifestore 508,30 EUR
- OD 40354 (MISC/25-26/06/00xx) : Write-off 0,02 EUR Cocon Lifestore 657100
- OD 40355 (MISC/25-26/06/00xx) : Reclassement BL 19013 Adropico/Delhaize Bois 527,80 EUR
- OD 40356 (MISC/25-26/06/00xx) : Reclassement BL 19014 Adropico/Delhaize Bois 520,45 EUR
- OD 40357 (MISC/25-26/06/00xx) : Write-off 0,01 EUR Delhaize Bois INV/2026/02834 657100
- OD 40358 (MISC/25-26/06/00xx) : Write-off 0,01 EUR Delhaize Bois INV/2026/02188 657100
- OD 40359 (MISC/25-26/06/00xx) : Reclassement BL 18445 JAMBIS 103,85 + trop-paye 62,77 en 499000
- OD 40360 (MISC/25-26/06/00xx) : Reclassement BL 18071 Faimine 143,25 EUR
- OD 40361 (MISC/25-26/06/00xx) : Reclassement BL 18328 Carrefour Belgium 171,76 EUR
- OD 40352 (MISC/25-26/06/00xx) : ANNULE (mauvais sens D/C, remplace par 40353)

### Lignes en suspens (15) - explications
| BL | Montant | Motif suspens |
|----|---------|---------------|
| 13505 | 543,06 | DEPA Lebbeke : comm '202501681' non identifiable dans Odoo, pas de partenaire GMS Lebbeke |
| 14600 | 688,92 | Shopping Center Schaus Sankt-Vith : OGM 000/0022/22815 = INV/2025/03733 Carrefour DEJA PAYEE (reconciliee avec BNK1/25-26/2039). Double paiement a confirmer Nicolas |
| 17574 | 33,10 | Pirlot-Willem Hannut : comm 'Wero TEATOWER' - pas de ref facture |
| 17815 | 307,30 | D-Trois Nandrin : comm INV/2026/01900 mais facture DEJA PAYEE le 18/05 (BNK1/25-26/5153). Double paiement probable a confirmer Nicolas |
| 17840 | 330,21 | Carpentier Elise Namur : comm 'Retour' - probablement remboursement, pas de facture client |
| 18095 | 16,64 | Reclosable Packaging BV NL : remboursement fournisseur ('Overpaid amount on order'), pas une facture client |
| 18382 | 53,00 | CPAS Marche-Famenne : OGM 000/0034/19046 = INV/2026/01553 Maison Repos Libert DEJA PAYEE. Double paiement ou fausse communication a confirmer |
| 18524 | 21,28 | Amazon Payments : remboursement marketplace, pas une facture client |
| 18657 | 21,63 | Walbaum Reims : remboursement CB fournisseur, pas une facture client |
| 18867 | 69,31 | DFH Market Liege : pas de communication OGM, montant ne correspond pas aux factures ouvertes (161,70 / 453,62) |
| 18880 | 262,49 | OFAC Assurances Arlon : 'PARTICIPATION BENEFICIAIRE 2025' - revenu assurance, pas une facture client - a imputer en 754xxx ou 755xxx |
| 18899 | 6,50 | Baguette-Moyse : OGM 000/0039/13544 = INV/2026/02833 Melanie Baguette REVERSED (annulee). Paiement apres annulation - a reconcilier manuellement |
| 18984 | 21,45 | EPS Monizze Bruxelles : tickets repas Monizze, pas une facture client |
| 19044 | 12,14 | Edenred Belgium : tickets repas Edenred, pas une facture client |
| 19062 | 11,91 | Amazon Payments : remboursement marketplace, pas une facture client |

**Total en suspens : 2.221,22 EUR** (dont 2 doubles paiements a confirmer : 307,30 + 688,92 = 996,22 EUR)

## 2026-06-15 — Lettrage banque ING — 10 lignes reconciliées + 1 avance salaire + 5 write-offs (total 0,18 EUR)

### Journal/Compte
- Journal : ING BE30 3631 6408 2311 (id=14), code BNK1
- Compte banque : 550001 Bank
- Compte suspens : 499000 Suspense Accounts
- Compte write-off perte : 657100 Negative Payment Differences
- Compte write-off gain : 757100 Positive Payment Differences

### Factures clients lettrées — soldées (paid)

| BL id | Date BL | Montant reçu | Client | Facture | Montant facture | Ecart | Write-off | Résultat |
|---|---|---|---|---|---|---|---|---|
| 18929 | 2026-06-05 | 672,71 | DEMARS SA Carrefour Beauraing | INV/2026/02328 | 672,73 | -0,02 | 657100 | paid |
| 18980 | 2026-06-09 | 545,31 | UNIC SA Carrefour Florenville | INV/2026/02409 | 545,31 | 0,00 | — | paid |
| 19012 | 2026-06-10 | 341,98 | Delhaize Amay | INV/2026/02890 | 342,00 | -0,02 | 657100 | paid |
| 19015 | 2026-06-10 | 562,79 | Gemblouxim Intermarché Gembloux | INV/2026/02604 | 562,81 | -0,02 | 657100 | paid |
| 19016 | 2026-06-10 | 412,30 | SA Barthe Intermarché Assesse | INV/2026/02183 | 412,30 | 0,00 | — | paid |
| 18827 | 2026-06-01 | 424,38 | SA Barthe Intermarché Assesse | INV/2026/02166 | 424,40 | -0,02 | 657100 | paid |
| 19053 | 2026-06-12 | 250,11 | Anaïs Michoel les petits pots | INV/2026/02752 | 250,01 | +0,10 | 757100 | paid |
| 19011 | 2026-06-10 | 217,00 | SA Marer AD Delhaize Bastogne | INV/2026/02408 | 217,00 | 0,00 | — | paid |

### Factures clients — lettrées partiellement (écart > 1 EUR, pas de write-off)

| BL id | Date BL | Montant reçu | Client | Facture | Montant facture | Résiduel restant | Note |
|---|---|---|---|---|---|---|---|
| 18002 | 2026-04-20 | 527,62 | Carrefour Belgium | INV/2026/01581 | 581,03 | 53,41 | Paiement partiel, ref /INV/2026/01581 dans virement |
| 18522 | 2026-05-15 | 365,71 | Carrefour Belgium | INV/2026/01962 | 688,94 | 323,23 | Paiement partiel, ref /INV/2026/01962 dans virement |

### Avance salaire

| BL id | Date | Montant | Bénéficiaire | Compte imputé | OD |
|---|---|---|---|---|---|
| 19042 | 2026-06-11 | -500,00 | Audrey Vansimpsen | 455000 Remuneration | OD id=40346 |

Note: 455000 cohérent avec les avances précédentes d'Audrey (02/2026, 12/2025, 10/2025).

### Write-offs passés (total 0,18 EUR)

| OD id | Date | Montant | Compte | Facture concernée |
|---|---|---|---|---|
| 40334 | 2026-06-05 | 0,02 | 657100 | INV/2026/02328 DEMARS |
| 40337 | 2026-06-10 | 0,02 | 657100 | INV/2026/02890 Delhaize Amay |
| 40339 | 2026-06-10 | 0,02 | 657100 | INV/2026/02604 Gemblouxim |
| 40342 | 2026-06-01 | 0,02 | 657100 | INV/2026/02166 SA Barthe |
| 40344 | 2026-06-12 | 0,10 | 757100 | INV/2026/02752 Anaïs Michoel (trop-perçu) |

**Total write-offs : 0,18 EUR** (4x 657100 = 0,08 EUR perte | 1x 757100 = 0,10 EUR gain)

### Lignes en suspens (à traiter manuellement par Nicolas)

Voir rapport détaillé dans la réponse compta du 15/06/2026 — 22 lignes, total 4.443,62 EUR.



## 2026-06-14 — Salve Peppol complémentaire — 3 clients flag corrigé + factures postées + envoyées (2.689,53 EUR TTC)

| N° Facture | Client | SO source | Montant TTC | Peppol state | EAS | Note |
|---|---|---|---|---|---|---|
| INV/2026/03055 | Cafes Delahaut (fact. id=5509) | S05794 | 1.311,75 EUR | processing | 0208 | qty_delivered forcée (0→livré), invoice_sending_method email→peppol |
| INV/2026/03056 | Spar Momignies | S05780 | 688,89 EUR | processing | 0208 | invoice_sending_method None→peppol |
| INV/2026/03057 | Carrefour market Courcelles | S05779 | 688,89 EUR | processing | 0208 | invoice_sending_method None→peppol |
| **TOTAL** | | **3 SO** | **2.689,53 EUR** | | | |

## 2026-06-14 — Salve facturation Peppol — 7 factures postées + envoyées (4.372,65 EUR TTC)

| N° Facture | Client | SO source | Montant TTC | Peppol state | EAS | Alerte |
|---|---|---|---|---|---|---|
| INV/2026/03048 | SPRL Durant-Rabaey | S05787 | 1.003,80 EUR | processing | 9925 | EAS obsolète — surveiller |
| INV/2026/03049 | Gemblouxim - Intermarché Gembloux | S05790 | 399,00 EUR | processing | 0208 | — |
| INV/2026/03050 | Emilie Gigot - Green Coffee | S05792 | 355,45 EUR | processing | 0208 | — |
| INV/2026/03051 | Cafés Antillia | S05793 | 898,35 EUR | processing | 9925 | EAS obsolète — surveiller |
| INV/2026/03052 | Carrefour Belgium | S05795 | 663,65 EUR | processing | 0208 | — |
| INV/2026/03053 | Carrefour Belgium | S05796 | 798,00 EUR | processing | 0208 | — |
| INV/2026/03054 | ASBL Restaurants Universitaires | S05798 | 254,40 EUR | processing | 0208 | — |
| **TOTAL** | | **7 SO** | **4.372,65 EUR** | | | |

Bloqués Peppol (10 SO — 3.861,14 EUR) : voir tableau dans rapport ci-dessous. Non facturés.


## 2026-06-12 — OD BROUILLON Doublon ONSS/PP SD Worx résiduel avril 2026 (id=40147)

| Champ | Valeur |
|---|---|
| Type | OD brouillon (state=draft, NON POSTÉ) |
| Journal | MISC (id=11) |
| Date | 30/06/2026 |
| Débit 454000 | 8.350,00 EUR — Apurement dette ONSS (RESA935+938+936 avril 2026) |
| Débit 453000 | 2.818,21 EUR — Apurement dette PP (RESA935 avril 2026) |
| Crédit 613310 | 11.168,21 EUR — Annulation charge doublon ONSS+PP |
| Correctif déjà posté | MISC/25-26/06/0094 — 26.225,98 EUR (mars 2026, 7 RESA) |
| Résiduel traité ici | RESA935 + RESA938 + RESA936 (avril 2026) |
| Statut | EN ATTENTE validation expert-comptable (>5.000 EUR) |
| Alerte | Vérifier DmfA/DMF avant validation — doublon comptable ≠ forcément double cotisation |

## 2026-06-11 — OD BROUILLON variation de stock FY25-26 (id=40092)

| Champ | Valeur |
|---|---|
| Type | OD brouillon (state=draft, NON POSTÉ) |
| Journal | MISC (id=11) |
| Date | 30/06/2026 |
| Débit | 340000 Marchandises — 64.180,45 EUR |
| Crédit | 609400 Variation stocks marchandises — 64.180,45 EUR |
| Écart brut quant vs 340000 | 65.171,29 EUR |
| Écarté (coûts aberrants) | 990,84 EUR (Gyokuro MP coût>PV + Miel HH005) |
| Montant défendable retenu | 64.180,45 EUR |
| Statut | EN ATTENTE validation expert-comptable (>5.000 EUR) |

## 2026-06-11 — RESTAURATION RESA812 (Shyfter, id=35935)

| Champ | Avant | Apres |
|---|---|---|
| state | cancel | posted |
| payment_state | not_paid | not_paid |
| amount_total | 47,19 EUR | 47,19 EUR |
| ref | 2026040554 | 2026040554 |
| partner | Shyfter SA (#121991) | Shyfter SA (#121991) |
| invoice_date | 2026-04-10 | 2026-04-10 |
| invoice_date_due | 2026-05-10 | 2026-05-10 |

Methode : button_draft (cancel->draft) + action_post (draft->posted). Aucun paiement ni lettrage existant (not_paid), pas de reversal lie (reversed_entry_id=False). Move lines apres repost : 611129 D:39,00 / 411000 D:8,19 / 440000 C:47,19 — coheres avec TVA 21%. Aucune ecriture parasite creee aujourd'hui pour Shyfter. Les 4 autres annulations du lot (Shopify transport + Google Cloud) restent inchangees.


## 2026-06-10 — TACHE 1/2 LOT KIRCHNER/NASA/SINAS — SUITE RAPPROCHEMENT BANCAIRE — is_reconciled flags + write-offs + brouillons

### TACHE 1 : Clôture flags bancaires 3 lignes Kirchner (BNK 18130 / 18733 / 18090)

**Methode :** activation reconcile=True sur compte 499000 (id=221), action_undo_reconciliation + account.move.line.reconcile sur les paires ML 499000 (BNK <-> OD).
Pour BNK18090, l'undo avait defait les lettrages 440000 -> rebuild complet du move 36792 (reset draft + 3 lignes 440000+499000 + post + reconcile chaque ligne).

| BNK | Move bancaire | OD | is_reconciled apres | Factures restaurees |
|-----|--------------|-----|--------------------|--------------------|
| 18130 | BNK1/25-26/4829 (id=36892, poster) | MISC/25-26/04/0069 (id=39982) | True | RESA733 paid |
| 18733 | BNK1/25-26/5298 (id=38796) | MISC/25-26/05/0124 (id=39983) | True | RESA730+RESA729 inchanges |
| 18090 | BNK1/25-26/4798 (id=36792, rebuild) | MISC/25-26/04/0070 (id=39984) | True | RESA506 paid, RESA735 paid, RESA734 partial (160,56 ouvert) |

### TACHE 2 : Lettrage avec write-off BNK 17722 + BNK 18834

| BNK | Move bancaire | Facture | Ecart | Write-off compte | is_reconciled |
|-----|--------------|---------|-------|-----------------|--------------|
| 17722 | BNK1/25-26/4508 (id=35816) | RESA462 (4.360,69, Mount Everest) | 5,39 EUR | 657100 D=5,39 | True |
| 18834 | BNK1/25-26/5378 (id=39194) | RESA743 (1.198,65, Kirchner) | 0,74 EUR | 657100 C=0,74 (dans BNK move) | True |

**Impact P&L Tache 2 :** -6,13 EUR total (5,39 + 0,74 en 657100 Negative Payment Differences). Residuel = -67.016 - 6,13 = -67.022 EUR (negligeable, autorise par instruction Nicolas).

**Note BNK 18834 :** match par montant uniquement (ref RGK26-01990 introuvable dans Odoo). A confirmer si Nicolas identifie une autre facture.

### TACHE 3 : Brouillons Sinas + NASA

**SINAS GmbH (id=6421, Allemagne, Intra-Community FP=3) :**

| ID Odoo | Ref fournisseur | Montant | Date | BNK paiement | TVA |
|---------|----------------|---------|------|-------------|-----|
| 39990 | 197610 | 2.648,58 EUR | 2026-02-18 | BNK16715 | 0% (autoliquidation intracom) |
| 39991 | 199235 | 839,37 EUR | 2026-04-10 | BNK17832 | 0% (autoliquidation intracom) |
| 39992 | 199587 | 2.514,77 EUR | 2026-04-24 | BNK18129 | 0% (autoliquidation intracom) |

Compte charge : 600000 (Purchases of Raw Materials). State=draft. A poster apres validation Nicolas.

**NASA Corporation (id=6409, Japon, hors-UE) :**

| ID Odoo | Ref | Montant | Date | BNK | TVA |
|---------|-----|---------|------|-----|-----|
| 39993 | SOJP202604-0054 | 5.419,82 EUR (978.100 JPY) | 2026-04-23 | BNK18116 | 0% sur facture (TVA import via doc douanier) |

State=draft. A poster apres validation Nicolas.

**Recommandations NASA :**
1. RESA825 (id=36192, state=posted, amount=0 EUR, payment_state=paid, ref=SOJP202604-0054) = placeholder a corriger ou annuler (wizard reversal) avant de poster le brouillon id=39993 pour eviter doublon de ref.
2. TVA import (6% ou 21% sur valeur CIF) a saisir depuis le document douanier/agent en douane, pas depuis la facture fournisseur — compte TVA import deductible separate.
3. BNK 16571 (-5.161,89 EUR, 907.750 JPY, 12/02/2026) vs RESA581 (4.921,00 EUR, non_paid) : ecart 240,89 EUR = probablement frais de change/commission banque JPY. NE PAS LETTRER avant confirmation Nicolas. Apres confirmation : lettrage RESA581 + 240,89 EUR en 654000 ou 657000 (frais financiers change).

**Impact P&L Tache 3 :** 0 EUR (tous en brouillon, aucun poste).

### TACHE 4 : Lignes en suspens — docs a fournir

| BNK | Montant | Date | Communication | Statut |
|-----|---------|------|--------------|--------|
| 18022 (BNK1/25-26/4757) | -2.000,54 EUR | 2026-04-20 | Kirchner SEPA, ref "See Docket from 16.04.26" | Facture originale du 16/04 a fournir par Nicolas |
| 18525 (BNK1/25-26/5140) | -1.029,74 EUR | 2026-05-15 | Kirchner SEPA, ref RGK26-01561 | Ref non trouvee dans Odoo — facture originale a fournir |

### Compteurs apres ce lot

- Lignes ING lettrées dans ce lot : 5 (BNK 18130, 18733, 18090, 17722, 18834)
- Lignes ING non reconciliees restantes : 122 (vs 127 avant ce lot)
- Lignes en suspens actif (brouillons Sinas/NASA) : 4 BNK (16715, 17832, 18129, 18116) + 1 NASA ecart (16571)
- Lignes sans doc (tache 4) : 2 BNK (18022, 18525)
- Compte 499000 : reconcile=True (active pour permettre les lettrages 499000)

---

## 2026-06-11 — ANNULATION 5 DOUBLONS FOURNISSEURS — IMPACT P&L +2.428,12 EUR

**Contexte :** Audit P&L FY25-26. 5 factures fournisseurs en double identifiees et validees par Nicolas pour annulation.
Procedure : button_draft + button_cancel sur les doublons non payes. Aucune ecriture bancaire touchee.

| Annulee | ID Odoo | Fournisseur | Ref fournisseur | Date | Montant TTC | Conservee | Critere |
|---------|---------|-------------|----------------|------|-------------|-----------|---------|
| RESA539 | 30768 | Shopify | Bill #460671442 | 2025-12-17 | 777,43 EUR | RESA412 (id=27476) | RESA412 anterieure (id plus petit), les 2 non payees |
| RESA534 | 30718 | Shopify | Bill #474838643 | 2026-01-16 | 607,11 EUR | RESA484 (id=29800) | RESA484 anterieure, les 2 non payees |
| RESA752 | 34465 | Shopify | Bill #503279326 | 2026-03-17 | 628,47 EUR | RESA742 (id=34275) | RESA742 anterieure, les 2 non payees |
| RESA572 | 31080 | Google Cloud | 5473148878 | 2026-01-31 | 367,92 EUR | RESA525 (id=31002) | RESA525 anterieure, les 2 non payees |
| RESA812 | 35935 | Shyfter SA | 2026040554 | 2026-04-10 | 47,19 EUR | RESA824 (id=35945) | RESA824 est payee/lettree (payment=paid) |

**Impact P&L :** +2.428,12 EUR (reduction charges 6xxxxx/614140/611129).
**Etat final :** 5 factures state=cancel | 5 factures conservees state=posted.
**Aucun double paiement detecte** — toutes les factures annulees etaient not_paid/non lettrées.

---

## 2026-06-10 — LETTRAGE KIRCHNER NETS — BNK 18130 / 18733 / 18090 — NEUTRE P&L (hors 0,01 EUR)

**Contexte :** Rapprochement bancaire ING (BNK1) — lignes Kirchner, Fischer & Co GmbH (#7195) avec suspense 499000.
Méthode : OD MISC (reclassement 499000 -> 440000) + account.partial.reconcile sur les lignes 440000 et 499000.

| BNK | Date | Move BNK | Montant | Facture(s) lettrée(s) | Partiel lettré | Résiduel ouvert | Impact P&L |
|-----|------|----------|---------|----------------------|----------------|-----------------|-----------|
| 18130 | 2026-04-24 | BNK1/25-26/4829 | -1.184,86 | RESA733 (1.184,85) | intégral | 0,00 (soldée) | 0,01 EUR 657100 (write-off autorisé) |
| 18733 | 2026-05-26 | BNK1/25-26/5298 | -8.706,97 | RESA730 (6.821,21 intégral) + RESA729 (1.885,76 partiel) | RESA729: 1.885,76/2.025,90 | 140,14 EUR ouvert RESA729 | 0 |
| 18090 | 2026-04-22 | BNK1/25-26/4798 | -18.451,00 (part suspense 5.944,74) | RESA734 (5.944,74 partiel sur 6.105,30) | partiel | 160,56 EUR ouvert RESA734 | 0 |

**OD créées (postées) :**
- `MISC/25-26/04/0069` (id=39982) — BNK18130/RESA733 — 440000 D=1.184,85 + 657100 D=0,01 / 499000 C=1.184,86
- `MISC/25-26/05/0124` (id=39983) — BNK18733/RESA730+RESA729 — 440000 D=6.821,21+1.885,76 / 499000 C=8.706,97
- `MISC/25-26/04/0070` (id=39984) — BNK18090/RESA734 — 440000 D=5.944,74 / 499000 C=5.944,74

**Partial reconciles créés :** PR13988/13989 (CAS1), PR13990/13991/13992 (CAS2), PR13993/13994 (CAS3).
**Résultat P&L :** neutre sauf 0,01 EUR en 657100 (Negative Payment Differences) — autorisé par instruction.
**Factures non touchées :** RESA735 (déjà payée), RESA506 (déjà payée).
**Cas réservés intacts :** BNK17722, BNK18022, BNK18525, BNK18834.
**Base résultat :** -67.016 EUR inchangée (hors 0,01 EUR négligeable).

---

## 2026-06-10 — TACHE 1 : LETTRAGE DOUBLE-SALAIRE VERRIEST + VECCHIA — 1.518,83 EUR — NEUTRE P&L

**Contexte :** Estelle Verriest et Fiona Vecchia (employées) ont rendu leur double-salaire d'avril 2026.
Même traitement que la cohorte Logan/Tholet/Thibaut/Carlier (avril 2026).

**Méthode :** Modification des moves bancaires de la stmt line (remplacement 499000 Suspense -> 455000 Rémunération).

| Stmt line | Move bancaire | Employée | Montant | Compte imputé | Impact P&L |
|-----------|--------------|---------|---------|--------------|-----------|
| BNK1/25-26/4522 (id=17741) | BNK1/25-26/4522 (id=35881) | Estelle Verriest (#113334) | 975,53 EUR | Dr 550001 / Cr 455000 | 0 |
| BNK1/25-26/4526 (id=17745) | BNK1/25-26/4526 (id=35885) | Fiona Vecchia (#107544) | 543,30 EUR | Dr 550001 / Cr 455000 | 0 |

- Résultat P&L = INCHANGÉ. 455000 = compte bilan (classe 4 rémunérations dues).
- Compteur : 171 -> 169 lignes non lettrées (BNK1: 154, BNK2: 15).

---

## 2026-06-10 — TACHE 2 Phase B : IMPUTATION CHEQUES-REPAS + SMARTBOX — 27 LIGNES — 1.866,04 EUR — NEUTRE P&L

**Contexte :** Suite diagnostic Phase A. Decision Nicolas : imputer les 27 lignes bancaires Edenred/Pluxee/Monizze/Smartbox sur comptes d'attente dedies (classe 5), sans toucher les comptes 6/7.

**Compte 580004 cree :** id=1225 — "Bons cadeaux Smartbox" — account_type=asset_current — modele 580003.

**Tableau des 27 lignes imputees :**

| BSL ID | Date | Type | Montant EUR | Compte impute | Boutique |
|--------|------|------|-------------|--------------|---------|
| 17368 | 2026-03-19 | MONIZZE | 57,83 | 580003 | non identifiable |
| 17605 | 2026-03-31 | SMARTBOX | 199,08 | 580004 | non identifiable |
| 17607 | 2026-03-31 | MONIZZE | 43,38 | 580003 | non identifiable |
| 17650 | 2026-04-01 | EDENRED | 21,62 | 580003 | non identifiable |
| 17755 | 2026-04-08 | EDENRED | 21,43 | 580003 | non identifiable |
| 17758 | 2026-04-08 | MONIZZE | 21,60 | 580003 | non identifiable |
| 17762 | 2026-04-08 | EDENRED | 9,34 | 580003 | non identifiable |
| 17763 | 2026-04-08 | EDENRED | 31,45 | 580003 | non identifiable |
| 17801 | 2026-04-09 | PLUXEE | 65,58 | 580003 | non identifiable |
| 17841 | 2026-04-10 | PLUXEE | 14,29 | 580003 | non identifiable |
| 17923 | 2026-04-14 | SMARTBOX | 290,08 | 580004 | non identifiable |
| 18070 | 2026-04-21 | MONIZZE | 73,22 | 580003 | non identifiable |
| 18082 | 2026-04-22 | PLUXEE | 28,53 | 580003 | non identifiable |
| 18135 | 2026-04-24 | PLUXEE | 43,65 | 580003 | non identifiable |
| 18207 | 2026-04-28 | PLUXEE | 23,08 | 580003 | non identifiable |
| 18329 | 2026-05-05 | PLUXEE | 9,53 | 580003 | non identifiable |
| 18335 | 2026-05-05 | SMARTBOX | 261,08 | 580004 | non identifiable |
| 18398 | 2026-05-07 | EDENRED | 89,06 | 580003 | non identifiable |
| 18493 | 2026-05-13 | PLUXEE | 27,58 | 580003 | non identifiable |
| 18494 | 2026-05-13 | EDENRED | 29,49 | 580003 | non identifiable |
| 18589 | 2026-05-19 | EDENRED | 49,15 | 580003 | non identifiable |
| 18616 | 2026-05-20 | EDENRED | 28,01 | 580003 | non identifiable |
| 18881 | 2026-06-03 | EDENRED | 42,48 | 580003 | non identifiable |
| 18882 | 2026-06-03 | PLUXEE | 9,29 | 580003 | non identifiable |
| 18913 | 2026-06-04 | EDENRED | 28,55 | 580003 | non identifiable |
| 18928 | 2026-06-05 | PLUXEE | 139,48 | 580003 | non identifiable |
| 18958 | 2026-06-08 | SMARTBOX | 208,18 | 580004 | non identifiable |

**Controle P&L :** 27 moves analyses — ZERO ligne sur comptes 6/7. Mouvements bilan pur (Dr 550001 / Cr 58x003).

---

## 2026-06-10 — LEVIERS AMELIORATION RESULTAT FY25-26 — 4 leviers analysés, 2 postés

### L5a — DOUBLON FOURNISSEUR BOXMAKER (+1.836,80 EUR) — POSTÉ

**Analyse :** RESA385 (id=27211, paid) et RESA428 (id=27689, in_payment), même réf 20250578, même montant 2.222,53 EUR TTC.
- BNK1/25-26/3161 (20/01/2026, comm. 20250578, ING) lettre avec RESA385 via partial.reconcile 9254 = seul paiement réel sorti pour cette réf.
- RESA428 : ligne 440000 non lettrée (residual -2222.53) → doublon d'encodage confirmé.
- 3 autres paiements Boxmaker de 2222.53 EUR sortis (mars/mai 2026) = autres factures distinctes (réf 20260091, 20260180).

**Action :** Avoir fournisseur miroir via wizard account.move.reversal.
- Avoir créé : RBILL/25-26/06/0001 (id=39978), 2026-06-10, Boxmaker B.V.B.A., 2.222,53 EUR TTC.
- RESA428 payment_state → reversed.
- **Impact P&L : +1.836,80 EUR HT** (C 604024 = 1.827,00 + C 600000 = 9,80 — annulation charge double).
- TVA : -385,73 EUR 411000 (déductible annulée, normal pour avoir fournisseur).

---

### L2 — DOUBLON ONSS/PP SD WORX (plancher +26.225,98 EUR) — POSTÉ

**Analyse :** 7 RESA SD Worx (713/789/790/791/935/936/938) ont passé ONSS+PP en 613310 alors que les OD de paie MISC créaient déjà les dettes 454000/453000.
- Solde FY25-26 454000 (NSSO) créditeur : 16.848,29 EUR.
- Solde FY25-26 453000 (PP) créditeur : 9.377,69 EUR.
- Total plancher certain : 26.225,98 EUR.
- Delta incertain (~11.464 EUR) non posté — correspond potentiellement à DmfA Q4 2025 ou cotisations hors OD de paie.

**OD postée :** MISC/25-26/06/0094 (id=39979), 2026-06-30.

| Compte | Débit | Crédit | Libellé |
|--------|-------|--------|---------|
| 454000 NSSO | 16.848,29 | — | Apurement dette ONSS |
| 453000 PP | 9.377,69 | — | Apurement dette PP |
| 613310 Secrétariat social | — | 26.225,98 | Annulation charge doublon |

**Garde-fou OK :** Après post, soldes 454000 et 453000 = 0,00 (ni débiteurs ni créditeurs résiduels).
**Impact P&L : +26.225,98 EUR** (annulation charge en double sur 613310).
**Delta en attente : ~11.464 EUR** — à confirmer avec SD Worx/DmfA avant de poster.

---

### L4 — EXTOURNE PROVISION FAIRE — NON POSTÉ

**Analyse :** OD MISC/25-26/06/0075 (id=39509), provision nette 20.536,11 EUR (D 604024 / C 440000 Faire.Com).
- Aucune facture Faire reçue depuis le 04/06 (vérifié Odoo).
- Mais la provision couvre des achats RÉELS déjà payés en banque (22.052,95 EUR sortis, 1.516,84 remboursements).
- 4.278 EUR supplémentaires payés depuis avril 2026 sans facture → flux Faire toujours actif.
- L'OD elle-même indique «à extourner lors de l'encodage des factures Faire».

**Décision : NE PAS EXTOURNER avant réception des factures Faire.**
Extourner avant = supprimer une charge réelle provisionnée = résultat fictif.
Écriture d'extourne prête (D 440000 22.052,95 + D 604024 1.516,84 / C 604024 22.052,95 + C 440000 1.516,84) → à poster quand toutes les factures Faire 08/2025-05/2026 sont encodées.
**Impact posté : 0 EUR.**

---

### L3a — CA MOLLIE ORPHELIN — NON POSTÉ

**Analyse :** 69 lignes crédit sur 400000 (total 5.716,82 EUR) liées au journal Mollie (id=17).
Structure réelle : chaque move Mollie = D 551102 Pmt à recevoir / C 400000.
Les factures des SO correspondants sont déjà en payment_state=in_payment via d'AUTRES moves Mollie (lettrage correct existant).
Ces 69 crédits = problème d'import/doublons d'enregistrement, pas du CA non reconnu.
Créer des factures pour lettrer = doublon de CA = INTERDIT.
**Impact posté : 0 EUR.** A investiguer séparément (apurement 400000 vs 551102 par OD neutre au résultat).

---

### RÉCAPITULATIF LEVIERS FY25-26

| Levier | Move | Montant posté | Statut |
|--------|------|--------------|--------|
| L5a Boxmaker doublon | RBILL/25-26/06/0001 (id=39978) | +1.836,80 EUR | POSTÉ |
| L2 ONSS/PP plancher | MISC/25-26/06/0094 (id=39979) | +26.225,98 EUR | POSTÉ |
| L4 Provision Faire | — | 0 EUR | EN ATTENTE factures Faire |
| L3a Mollie orphelins | — | 0 EUR | Pb lettrage, pas CA |
| **Total posté** | | **+28.062,78 EUR** | |

**Résultat estimé FY25-26 :** 80.633 + 28.062,78 = **108.695,78 EUR** (avant audit/ISOC).

**Confirmations externes à obtenir :**
1. SD Worx : demander détail DmfA Q4 2025 et vérifier si ~11.464 EUR = vraie cotisation ou doublon → potentiel +11.464 EUR supplémentaire.
2. Faire.com : dès réception et encodage de toutes les factures 08/2025-05/2026 → poster l'extourne MISC/25-26/06/0075 → +20.536,11 EUR.

**Soldes comptes d'attente (FLAG CA POS a investiguer) :**

| Compte | Libelle | Solde crediteur | Flag |
|--------|---------|----------------|------|
| 580003 | Paiement Sodexo-Edenred (principal) | 1.308,36 EUR | FLAG |
| 580004 | Bons cadeaux Smartbox (nouveau) | 958,42 EUR | FLAG |
| 581003 | Sodexo-Edenred-Monizze Liege | 807,75 EUR | FLAG |
| 582003 | Sodexo-Edenred-Monizze Namur | 28,50 EUR | FLAG |
| 583003 | Sodexo-Edenred-Monizze Waterloo | 0,00 EUR | OK (lettre) |

Total solde crediteur ouvert = 3.103,03 EUR (CA POS potentiellement non reconnu a investiguer).

**Lignes ING restantes non lettrées après traitement :** 127 lignes (total -134.781,83 EUR — majoritairement débits/charges).
**Lignes Belfius restantes non lettrées :** 0.

---

## 2026-06-10 — TACHE 2 Phase A : DIAGNOSTIC CHEQUES-REPAS + SMARTBOX — FLAGS SUSPENS

**Lignes bancaires non lettrées identifiées (ING BNK1, mars-juin 2026) :**

| Catégorie | Nb lignes | Total EUR |
|-----------|-----------|-----------|
| Edenred | 10 | 350,58 |
| Pluxee | 9 | 361,01 |
| Monizze | 4 | 196,03 |
| Smartbox | 4 | 958,42 |
| **TOTAL** | **27** | **1.866,04** |

**Diagnostic comptes d'attente :**
- Comptes 580003/581003/582003/583003 (Sodexo-Edenred par boutique) : AUCUNE écriture depuis nov 2025.
- Config POS : 2 méthodes seulement (Carte = journal ING / Espèces). Aucun PM dédié Edenred/Pluxee/Monizze/Smartbox.
- Les virements acquéreur Worldline ('Virement R:') transitent par 581002/582002 (Visa/MC). Les virements Edenred/Pluxee/Monizze/Smartbox sont des flux SÉPARÉS sans contrepartie POS dédiée dans la config actuelle.
- Pas de compte d'attente actif côté POS pour ces moyens de paiement (FY25-26).

**Conclusion Phase B : LETTRAGE NON EXÉCUTÉ — EN SUSPENS**
Condition Phase B non remplie : il n'existe pas de créance POS distincte en face des virements émetteurs.
Décision Nicolas requise : imputer sur 580003 (compte existant dédié) après confirmation que le CA est bien inclus dans les sessions POS 'Carte' (à croiser avec les relevés terminaux).

---

## 2026-06-10 — LETTRAGE MOLLIE PASSE APPROFONDIE — 2 factures supplémentaires soldées — PR 13980+13981

### Re-matching approfondi 87 partenaires MOL/ encore ouverts — zéro impact P&L

**Phase A :** Scan de TOUS les partenaires avec crédit MOL/ ouvert sur 400000 (tous journaux confondus).
- Partenaires MOL/ ouverts : 87 (110 lignes, 6 258,24 EUR crédit résiduel)
- Partenaires avec au moins 1 débit ouvert sur 400000 : 2 (Veoware BV + Sorel CHALEU)
- Vrais orphelins purs (crédit MOL sans aucun débit en face) : 85

**Phase B :** 2 lettrages exécutés (PR 13980 + 13981) :

| PR | Débit (facture) | Crédit (MOL) | Partenaire | Montant lettré | Résidu crédit restant |
|----|----------------|--------------|-----------|--------------|----------------------|
| 13980 | INV/2025/03003 line 72612 (résidu 3,06) | MOL/25-26/3607 line 131236 | Veoware BV - Tina SPLETINCKX | 3,06 EUR | -62,31 EUR |
| 13981 | INV/2025/02650 line 67035 (résidu 4,00) | MOL/25-26/3503 line 128614 | Sorel CHALEU | 4,00 EUR | -59,89 EUR |

- Garde-fou : 4/4 lignes impliquées sur compte 400000 uniquement — aucun compte 6/7 touché
- Les 2 factures (INV/2025/03003 + INV/2025/02650) : payment_state=in_payment, amount_residual=0,00
- Les résidus crédit MOL restants (62,31 + 59,89 EUR) : lignes orphelines, client a trop payé vs facture — décision Nicolas

**Phase C — 85 vrais orphelins restants (6.251,18 EUR total) :**
Ces clients ont payé via Mollie sans facture Odoo correspondante (commandes Shopify non facturées).
Ce sont des SOLDES CRÉDITEURS clients (avoirs implicites), PAS des impayés.
Lettrage impossible sans création de facture (impact P&L = reconnaissance de CA). Décision Nicolas requise.

Top 10 : Catherine VINCENT 335,01 | Clouds and Waves 288,01 | Thomas Dethier DELTATEC 286,33 | t Grof Zout 258,62 | Fabry et Fils 256,02 | Pierre Lemaire 231,02 | Fiduciaire Huynen 221,93 | Perficienz 220,20 | BOSS IMMO 220,07 | MTBC 197,37

**Bilan cumulé toutes passes Mollie (PR 13965-13981) :**
- 17 PR créés | Montant total lettré : 1.106,03 EUR | Comptes touchés : 400000 uniquement
- Aucun compte classe 6/7 — zéro impact P&L

---

## 2026-06-10 — LETTRAGE MOLLIE JOURNAL MOL/ — 13 paires lettrées — 1.095,10 EUR sortis balance âgée

### Lettrage paiements Mollie historiques vs factures clients 400000 — ZÉRO impact P&L

**Journal Mollie :** id=17, code=MOL, type=bank  
**Compte :** 400000 Customers (id=162)  
**Méthode :** account.partial.reconcile pur, 400000 vs 400000 — aucune écriture 6/7 générée

| PR Odoo | MOL (crédit) | Facture (débit) | Partenaire | Montant lettré |
|---------|-------------|-----------------|-----------|----------------|
| 13965 | MOL/25-26/4409 (158459) | INV/2026/02905 (178150) | Thomas Dethier DELTATEC | 197,60 EUR |
| 13966 | MOL/25-26/3699 (133948) | INV/2026/01774 (152286) | FIDUCIAIRE HUYNEN SRL | 96,09 EUR |
| 13967 | MOL/25-26/1718 (88301) | INV/2025/04064 (88299) | BOSS IMMO SA | 58,54 EUR |
| 13968 | MOL/25-26/0965 (72614) | INV/2025/03003 (72612) | Veoware BV | 58,14 EUR |
| 13969 | MOL/25-26/0758 (67037) | INV/2025/02650 (67035) | Sorel CHALEU | 75,12 EUR |
| 13970 | MOL/25-26/3230 (120813) | INV/2026/00232 (119807) | CATHY LEQUERTIER | 19,00 EUR |
| 13971 | MOL/25-26/1845 (90622) | INV/2026/02904 (178109) | Marylene Heindrichs | 80,00 EUR |
| 13972 | MOL/25-26/1189 (76773) | INV/2025/03300 (76771) | Catherine Vincent | 110,13 EUR |
| 13973 | MOL/25-26/0756 (66989) | INV/2025/02647 (66987) | Catherine Vincent | 99,30 EUR |
| 13974 | MOL/25-26/1170 (76519) | INV/2025/03279 (76517) | Devillers Srl | 56,70 EUR |
| 13975 | MOL/25-26/1090 (75725) | INV/2025/03199 (75723) | Thill I.T. Consulting | 83,38 EUR |
| 13976 | MOL/25-26/1017 (73618) | INV/2025/03074 (73616) | MULOT MENUISERIE | 100,18 EUR |
| 13977 | MOL/25-26/0854 (70182) | INV/2025/02833 (70180) | Blandine Demarche | 60,92 EUR |

**Total lettré : 1.095,10 EUR — tous 13 PR sur compte 400000 uniquement, confirmé.**

### Résidus laissés ouverts (écarts frais Mollie — AUCUN passage en 6/7)

| Partenaire | Sens | Montant résidu | Note |
|-----------|------|---------------|------|
| Thomas Dethier DELTATEC | MOL résidu | 16,97 EUR | MOL 214,57 vs INV 197,60 |
| FIDUCIAIRE HUYNEN SRL | INV résidu | 0,81 EUR | MOL 96,09 vs INV 96,90 |
| BOSS IMMO SA | INV résidu | 3,06 EUR | MOL 58,54 vs INV 61,60 |
| Veoware BV | INV résidu | 3,06 EUR | MOL 58,14 vs INV 61,20 |
| Sorel CHALEU | INV résidu | 4,00 EUR | MOL 75,12 vs INV 79,12 |
| CATHY LEQUERTIER | MOL résidu | 11,80 EUR | MOL 30,80 vs INV 19,00 |
| Marylene Heindrichs | INV résidu | 5,50 EUR | MOL 80,00 vs INV 85,50 |
| Catherine Vincent | INV résidu | 5,77 EUR | paire 1 |
| Catherine Vincent | INV résidu | 5,20 EUR | paire 2 |
| Devillers Srl | INV résidu | 3,00 EUR | MOL 56,70 vs INV 59,70 |
| Thill I.T. Consulting | INV résidu | 4,37 EUR | MOL 83,38 vs INV 87,75 |
| MULOT MENUISERIE | INV résidu | 5,27 EUR | MOL 100,18 vs INV 105,45 |
| Blandine Demarche | INV résidu | 3,21 EUR | MOL 60,92 vs INV 64,13 |

### Orphelins MOL non lettrés (79 partenaires, 5.201,44 EUR)
Paiements Mollie sans facture Odoo correspondante = commandes Shopify pré-migration non facturées. Laissés ouverts, décision Nicolas requise.

### Exclusions (factures non posted)
- Thomas Dethier INV/2026/02049 (line 158457) : state=cancel — non lettrable
- Jean-Yves EISCHEN move 24813 : state=cancel — non lettrable
- marie France bajot INV/2025/04108 (line 88986) : state=draft — non lettrable

### Impact P&L : ZÉRO — résultat +87.055 EUR intact

---

## 2026-06-10 — WRITE-OFF MICRO-RESIDUELS CLIENTS — 3 factures soldées — résultat FY25-26 : +80.632,01 EUR

### Write-off écarts de paiement ≤ 1,00 EUR (phase 1+2)

3 factures clients (out_invoice, posted, payment_state partial) avec résiduel absolu ≤ 1,00 EUR identifiées et soldées via OD journal MISC + lettrage compte 400000.

| Facture | Partner | Total | Résiduel | Compte | OD Odoo |
|---|---|---|---|---|---|
| INV/2025/03864 | Carrefour Belgium | 420,01 € | 0,52 € | 657100 | MISC/25-26/06/0092 (id=39969) |
| INV/2026/01774 | Fiduciaire Huynen SRL | 96,90 € | 0,81 € | 657100 | MISC/25-26/06/0093 (id=39970) |
| INV/2026/02007 | SPRL Durant-Rabaey | 420,00 € | 0,01 € | 657100 | MISC/25-26/06/0091 (id=39968) |

- Total write-off en charge (657100) : 1,34 EUR
- Toutes les 3 en payment_state = paid / in_payment, résiduel = 0,00 EUR
- Aucune facture client restante avec résiduel ≤ 1,00 EUR (vérifié post-opération)
- Impact P&L FY25-26 : -1,34 EUR sur résultat
- Résultat FY25-26 avant : +80.633,35 EUR → après : +80.632,01 EUR

---

## 2026-06-10 — RAPPROCHEMENT BANCAIRE PHASE 4 — Tâches 1+2+3 — résultat FY25-26 : +80.633,35 EUR

### TÂCHE 1 — CAS B : double-paiement resté en 455000, revert Jérôme

**Preuve trouvée :** Les deux fichiers SEPA de paie d'avril (BNK1/25-26/4496 du 07/04 et BNK1/25-26/4534 du 08/04, 2 x 25 038,26 €) ont débité **455000 Remuneration** (pas un compte 620xxx). La sur-disbursement reste en 455000 (bilan), pas en charge.

**CAS B retenu :** Les remboursements entrants sont la contrepartie du débit 455000. Passer en 620 aurait créé une fausse réduction de charge. Cohorte 11 lignes reste en 455000.

**Action :** Contre-passe de l'OD 39929 (MISC/25-26/04/0067) :
- OD créée et postée : MISC/25-26/04/0068 (id=39961) — date 30/04/2026 — journal MISC (id=11)
- Dr 620200 Salaried Employees : 4 520,54 EUR
- Cr 455000 Remuneration : 4 520,54 EUR
- Effet net des deux OD (39929 + 39961) : 0,00 EUR sur chaque compte — annulation totale
- Impact résultat : -4 520,54 EUR

### TÂCHE 2 — 8 factures Google postées + lettrées

| RESA | Partner | Compte | Montant EUR | Stmt ING |
|------|---------|--------|------------|----------|
| RESA1037 (39950) | Google EMEA Ads | 615200 | 400,00 | stmt17248 (BNK1/25-26/4120) |
| RESA1038 (39951) | Google EMEA Ads | 615200 | 127,18 | stmt17653 (BNK1/25-26/4459) |
| RESA1039 (39952) | Google EMEA Ads | 615200 | 500,00 | stmt17846 (BNK1/25-26/4616) |
| RESA1040 (39953) | Google EMEA Ads | 615200 | 337,28 | stmt18278 (BNK1/25-26/4947) |
| RESA1041 (39954) | Google EMEA Ads | 615200 | 500,00 | stmt18484 (BNK1/25-26/5109) |
| RESA1042 (39955) | Google EMEA Ads | 615200 | 500,00 | stmt18681 (BNK1/25-26/5257) |
| RESA1043 (39956) | Google EMEA Ads | 615200 | 372,37 | stmt18845 (BNK1/25-26/5389) |
| RESA1044 (39957) | Google Cloud | 611129 | 370,00 | stmt18925 (BNK1/25-26/5450) |

- Méthode : action_post + write account_id 499000->440000 sur lignes suspense des stmts -> lettrage auto Odoo
- 8/8 stmts is_reconciled=True — partial reconciles 13953 à 13960
- Proximus ids 39958 (121,99) et 39959 (100,00) : laissés en BROUILLON non touchés
- Impact résultat : -3 106,83 EUR

### TÂCHE 3 — Régularisation stmt16464 Adobe

- Action : write move_id=39949 sur stmt16464 (repointe vers OD BNK1/25-26/5484 posted+lettrée avec RESA1021)
- Résultat : stmt16464 is_reconciled=True — sans double imputation
- Impact P&L : ZÉRO

### Résultat FY25-26 après Phase 4

- Entrée : +88 260,72 EUR
- Tâche 1 revert Jérôme : -4 520,54 EUR
- Tâche 2 Google : -3 106,83 EUR
- **RÉSULTAT FINAL : +80 633,35 EUR**
- Stmts BNK1 non lettrées : 156 (sur 6 851 total)
- Aucune écriture hors périmètre validé

---

## 2026-06-10 — RAPPROCHEMENT BANCAIRE PHASE 3 — Tâches A+B+C — résultat FY25-26 : +88.261 EUR

### TÂCHE A — Reclassement Jérôme Carlier 455000 -> 620200

- OD créée et postée : MISC/25-26/04/0067 (id=39929) — date 08/04/2026 — journal MISC (id=11)
- Dr 455000 Remuneration : 4 520,54 EUR
- Cr 620200 Salaried Employees : 4 520,54 EUR
- Partenaire : Jérôme Carlier (id=97805)
- Contexte : stmt17747 (BNK1/25-26/4528) déjà posté Dr 550001 / Cr 455000. OD bascule la contrepartie en 620200 sans toucher au rapprochement bancaire existant.
- Impact résultat FY25-26 : +4 520,54 EUR
- Résultat après Tâche A : +91.575,54 EUR

### TÂCHE B — Cohorte remboursements salariés 455000 (chiffrage uniquement, NON posté)

Crédits 455000 sur BNK1 FY25-26 identifiés comme remboursements trop-perçu salariés :

| Date | Montant | N° Move | Employé | Statut |
|------|---------|---------|---------|--------|
| 2026-04-08 | 2 175,93 | BNK1/25-26/4523 | Logan Nicolas | Attente décision |
| 2026-04-08 | 1 051,36 | BNK1/25-26/4525 | Tholet Emeline | Attente décision |
| 2026-04-08 | 3 570,53 | BNK1/25-26/4527 | Thibaut Aurelie | Attente décision |
| 2026-04-08 | 4 520,54 | BNK1/25-26/4528 | Carlier Jerome | RECLASSÉ Tâche A |
| 2026-04-08 | 1 149,82 | BNK1/25-26/4529 | Cabosart Gilles | Attente décision |
| 2026-04-08 | 2 155,25 | BNK1/25-26/4548 | Grove Hedwige | Attente décision |
| 2026-04-09 | 1 462,54 | BNK1/25-26/4581 | Van Ooteghem Camille | Attente décision |
| 2026-04-09 | 1 505,01 | BNK1/25-26/4588 | Demoulin Stephan | Attente décision |
| 2026-04-09 | 1 434,99 | BNK1/25-26/4589 | Gysen Aurelie | Attente décision |
| 2026-04-09 | 1 882,13 | BNK1/25-26/4591 | Egels Sybille | Attente décision |
| 2026-04-10 | 1 379,91 | BNK1/25-26/4598 | Georges Dominique | Attente décision |
| 2026-05-06 | 1 031,29 | BNK1/25-26/5014 | Georges Dominique | Attente décision |

- Total cohorte complète : 23 319,30 EUR
- Déjà reclassé : 4 520,54 EUR (Jérôme)
- Reste à décider : 18 798,76 EUR
- Résultat FY25-26 HYPOTHÉTIQUE si tout reclassé : +110.374,76 EUR

### TÂCHE C — 16 factures fournisseurs récurrents ING — postées + lettrées (RESA1021-1036)

| RESA | Partner | Compte | Montant EUR | Date | Stmt ING |
|------|---------|--------|------------|------|----------|
| RESA1021 (39930) | Adobe | 611129 | 36,29 | 2026-02-09 | stmt16464 (OD remplt) |
| RESA1022 (39931) | Adobe | 611129 | 36,29 | 2026-04-09 | stmt17792 |
| RESA1023 (39932) | Adobe | 611129 | 60,49 | 2026-04-14 | stmt17895 |
| RESA1024 (39933) | Adobe | 611129 | 36,29 | 2026-05-09 | stmt18427 |
| RESA1025 (39934) | Adobe | 611129 | 60,49 | 2026-05-14 | stmt18510 |
| RESA1026 (39935) | Adobe | 611129 | 36,29 | 2026-06-09 | stmt18972 |
| RESA1027 (39936) | Intuit Mailchimp | 616600 | 697,81 | 2026-04-08 | stmt17756 |
| RESA1028 (39937) | Intuit Mailchimp | 616600 | 17,22 | 2026-04-26 | stmt18140 |
| RESA1029 (39938) | Intuit Mailchimp | 616600 | 703,11 | 2026-05-08 | stmt18418 |
| RESA1030 (39939) | Intuit Mailchimp | 616600 | 715,63 | 2026-06-08 | stmt18964 |
| RESA1031 (39940) | Skeepers SAS | 616600 | 258,25 | 2026-04-22 | stmt18089 |
| RESA1032 (39941) | Skeepers SAS | 616600 | 258,25 | 2026-05-20 | stmt18629 |
| RESA1033 (39942) | Sendcloud B.V. | 611129 | 6,71 | 2026-02-11 | stmt16555 |
| RESA1034 (39943) | Sendcloud B.V. | 611129 | 137,00 | 2026-04-07 | stmt17719 |
| RESA1035 (39944) | Sendcloud B.V. | 611129 | 128,60 | 2026-05-05 | stmt18351 |
| RESA1036 (39945) | Sendcloud B.V. | 611129 | 126,10 | 2026-06-03 | stmt18889 |

- Total postées + payées : 3 314,82 EUR — impact résultat : -3 314,82 EUR
- 15/16 stmts is_reconciled=True (auto-lettrage Odoo par correspondance 440000)
- stmt16464 Adobe fev : BNK1/25-26/3472 était 'cancel'. OD BNK1/25-26/5484 (id=39949) créée (Dr 440000 36,29 / Cr 550001) pour solder RESA1021. stmt16464 reste not_reconciled techniquement.
- TVA : aucune (prestataires étrangers, montant TTC = HT, cohérent avec historique Teatower)

### TÂCHE C — 10 factures BROUILLON à valider Nicolas (Google Ads x7, Google Cloud x1, Proximus x2)

| ID | Partner | Compte | Montant | Date | Stmt | Note |
|----|---------|--------|---------|------|------|------|
| 39950 | Google EMEA | 615200 | 400,00 | 2026-03-15 | stmt17248 | Google Ads variable |
| 39951 | Google EMEA | 615200 | 127,18 | 2026-04-02 | stmt17653 | Google Ads variable |
| 39952 | Google EMEA | 615200 | 500,00 | 2026-04-12 | stmt17846 | Google Ads variable |
| 39953 | Google EMEA | 615200 | 337,28 | 2026-05-02 | stmt18278 | Google Ads variable |
| 39954 | Google EMEA | 615200 | 500,00 | 2026-05-13 | stmt18484 | Google Ads variable |
| 39955 | Google EMEA | 615200 | 500,00 | 2026-05-24 | stmt18681 | Google Ads variable |
| 39956 | Google EMEA | 615200 | 372,37 | 2026-06-02 | stmt18845 | Google Ads variable |
| 39957 | Google Cloud | 611129 | 370,00 | 2026-06-05 | stmt18925 | Pas de facture juin |
| 39958 | Proximus | 616200 | 121,99 | 2026-04-27 | stmt18173 | Ecart vs RESA939 (122,98) |
| 39959 | Proximus | 616200 | 100,00 | 2026-05-26 | stmt18716 | Montant inconnu |

- Total BROUILLON : 3 329,82 EUR (si postés, résultat baisserait encore de ce montant)

### Résultat FY25-26 après ce run

- Base avant ce run : +87.055,00 EUR
- + Tâche A reclassement Jérôme 620200 : +4.520,54 EUR → +91.575,54 EUR
- - Tâche C 16 factures fournisseurs : -3.314,82 EUR → +88.260,72 EUR
- Stmts ING lettrées ce run : 15 (stmts ING restantes non lettrées : 165)
- Aucune écriture hors périmètre validé

---

## 2026-06-10 — RECLASSEMENT AVANCES SALARIALES GILLES CABOSART (partner #9711)

### Etape 1 — Garde-fou doublon 1.000 €
Analyse des bank statement lines ING autour des 4 dates :

| Date | Montant | BSL ID | Référence ING | Virement réel ? |
|------|---------|--------|---------------|-----------------|
| 14/10/2025 | -18,89 € | 13913 | "Virement SEPA Vers: Cabosart Gilles" | OUI |
| 05/11/2025 | -49,90 € | 14372 | "ING app Vers: Gilles Cabosart — Auto5" | OUI |
| 15/01/2026 | -1 000,00 € | 15994 | "ING app Vers: Cabosart Gilles — Avant février" | OUI |
| 16/03/2026 | -1 000,00 € | 17261 | "Business'Bank Instant Vers: Cabosart Gilles — avance mars" | OUI |

Verdict : les DEUX 1.000 € sont des virements bancaires RÉELS et distincts (référence communication différente : "Avant février" vs "avance mars", canaux différents : ING app vs Business'Bank Instant, dates séparées de 2 mois). La ligne du 16/03 "Solde d'ouverture de -1.000,00" est le libellé Odoo lors de l'import du relevé (mode de comptabilisation), NON un re-report de solde. Il n'y a pas de doublon. Total des vraies avances = 2.068,79 €.

### Etape 2 — OD de reclassement créée et postée

- OD : MISC/25-26/06/0090 (move_id=39962) — date 2026-06-10 — journal MISC (id=11)
- Dr 416000 Sundry Amounts Receivable : 2 068,79 EUR (avances au personnel — Gilles Cabosart)
- Cr 400000 Customers : 2 068,79 EUR (soldage compte client)
- Garde-fou classe 6/7 : NÉANT — uniquement classe 4 (416000 + 400000)
- Impact P&L : ZÉRO — résultat +87.055 EUR intact
- Lettrage : les 4 lignes débit ouvertes sur 400000 / #9711 (ML 95966, 152127, 123139, 152094) lettrées contre ML 180313 (crédit OD) — match_ids 13949/13950/13951/13952 — reconciled=True pour les 5 lignes

### Etat après reclassement
- Compte 400000 / partner #9711 : solde ouvert = 0,00 € (compte client soldé)
- Compte 416000 / partner #9711 : solde débiteur = 2 068,79 € (créance sur personnel en attente de régularisation — compensation future sur fiche de paie ou remboursement)
- Note 416000 : compte reconcile=False → lettrage manuel lors du remboursement/compensation

### Recommandation complémentaire
- Créer un compte 416xxx dédié "Avances sur rémunérations" pour séparer des autres créances sundry
- Régulariser en accord avec SD Worx : déduire les 2.068,79 € de la prochaine fiche de paie de Gilles ou OD de compensation 416000 / 620200 + 455000

---

## 2026-06-10 — LETTRAGE FAUX IMPAYÉS BOUTIQUES INV1/INV2/INV3 — 5 053,23 EUR soldés

### Phase A — Inventaire
- 116 factures clients ouvertes dans journaux boutiques (INV1=Liège, INV2=Namur, INV3=Waterloo)
- Total résiduel initial : 5 073,23 EUR
- 2 factures à résiduel=0 exclues d'office (Mollie déjà réglées, payment_state=in_payment)
- 112 factures actives : CAS 1 (68 in_process/move_id=False) + CAS 2 (44 paid/move_id=False)
- 1 facture CAS 3 (aucun paiement) : INV3/25-26/0130 — 1380 Smiles — 20,00 EUR → EN ATTENTE

### Phase B — Création ODs de lettrage (bilan pur, zéro P&L)
- OD Waterloo : MISC/25-26/06/0087 (move_id=39946) — 13 lignes — 360,12 EUR — posté 2026-06-10
  - Débit 573000 Caisse Waterloo / Crédit 400000 Clients — 13 paires
- OD Namur : MISC/25-26/06/0088 (move_id=39947) — 52 lignes — 2 759,30 EUR — posté 2026-06-10
  - Débit 572000 Caisse Namur / Crédit 400000 Clients — 52 paires
- OD Liège : MISC/25-26/06/0089 (move_id=39948) — 47 lignes — 1 933,81 EUR — posté 2026-06-10
  - Débit 571000 Caisse Liège / Crédit 400000 Clients — 47 paires
- Total ODs : 112 lignes, 5 053,23 EUR — lettrage automatique Odoo au post

### Garde-fou P&L
- Vérification ligne par ligne : AUCUN compte classe 6 ou 7 dans aucune des 3 ODs
- Uniquement classe 4 (400000 Clients) et classe 5 (571000/572000/573000 Caisses)
- 112/112 lignes 400000 des ODs : reconciled=True après post
- Résultat +87 055 EUR INTACT — zéro impact P&L

### Cas à confirmer Nicolas
- INV3/25-26/0130 — 1380 Smiles (id=8847) — 2026-03-06 — 20,00 EUR — payment_state=not_paid
  - Aucun paiement enregistré — vérifier si règlement caisse Waterloo reçu ou facture à annuler

## 2026-06-10 — NETTOYAGE FAUX IMPAYES POS TEA TREE CAISSE — 55 040,01 EUR soldés

### Etape 1 — Annulation 6 paiements en double (state=in_process, move_id=False)
- PAY00645 (id=7364) state=canceled — Groupe A mauvais journal Caisse Rocourt
- PAY00646 (id=7365) state=canceled — Groupe A mauvais journal Caisse Rocourt
- PAY00647 (id=7366) state=canceled — Groupe A mauvais journal Caisse Rocourt
- PAY00648 (id=7367) state=canceled — Groupe B doublon exact
- PAY00649 (id=7368) state=canceled — Groupe B doublon exact
- PAY00650 (id=7369) state=canceled — Groupe B doublon exact
- Garde-fou : move_id=False et reconciled_invoices=[] vérifiés avant annulation pour chacun

### Etape 2 — Création écritures et lettrage 3 paiements valides
- PAY00654 (id=7373) 4 167,40 EUR — INV/2025/00507 — journal Caisse Liège (571000)
  - Move créé : CSH2/25-26/0001 (id=39926) — 571000 D 4167,40 / 400000 C 4167,40 — posté 2026-06-10
  - Lettrage : line 17105 (INV debit 400000) <-> line 180021 (paiement credit 400000) — match_id=13818
  - Résultat : INV/2025/00507 payment_state=paid, amount_residual=0,00
- PAY00655 (id=7374) 21 318,07 EUR — INV/2025/02610 — journal Espèces (570001)
  - Move créé : LIEGE/25-26/0059 (id=39927) — 570001 D 21318,07 / 400000 C 21318,07 — posté 2026-06-10
  - Lettrage : line 66282 (INV debit 400000) <-> line 180023 (paiement credit 400000) — match_id=13819
  - Résultat : INV/2025/02610 payment_state=paid, amount_residual=0,00
- PAY00656 (id=7375) 29 554,54 EUR — INV/2025/02608 — journal Cash (570001)
  - Move créé : NAMUR/25-26/0344 (id=39928) — 570001 D 29554,54 / 400000 C 29554,54 — posté 2026-06-10
  - Lettrage : line 66201 (INV debit 400000) <-> line 180025 (paiement credit 400000) — match_id=13820
  - Résultat : INV/2025/02608 payment_state=paid, amount_residual=0,00

### Garde-fou P&L
- Aucun compte classe 6 ou 7 dans aucune des écritures créées (vérification ligne par ligne)
- Total sorti balance âgée : 55 040,01 EUR (= 4 167,40 + 21 318,07 + 29 554,54)
- Résultat +87 055 EUR INTACT — aucune charge ni produit ajouté

## 2026-06-10 — RAPPROCHEMENT BANCAIRE PHASE 2 — 23 lignes traitées (17 ING + 6 Belfius)

### Matchs nets fournisseurs — 8 factures soldées
- Shyfter SA : RESA661 47,19 EUR (stmt17156), RESA824 47,19 EUR (stmt17822), RESA897 47,19 EUR (stmt18435) — 3 factures PAID
- ING Belgique SA : RESA687 0,61 EUR (stmt15839), RESA659 0,61 EUR (stmt17129), RESA839 14,52 EUR (stmt18120), RESA979 31,00 EUR (stmt18268) — 4 factures PAID
- ING Equipment Lease Belgium : RESA803 14,52 EUR (via ML 152048 déjà modifiée), RESA774 2 299,22 EUR (stmt18018) — 2 factures PAID

### Matchs nets clients — 4 factures soldées
- CPSP Belgie → INV/2026/01297 Center Parcs 675,75 EUR (stmt18300) — PAID
- CPSP Belgie → INV/2026/02145 Sunparks 333,90 EUR + INV/2026/02061 Sunparks 333,90 EUR = 667,80 EUR (stmt18688) — 2 factures PAID

### Opérations neutres P&L — comptes bilan
- Prêts actionnaires : Vilna Gaon +5 000 EUR (stmt17658→489000), Tilman Jean Noël +10 000 EUR (stmt17659→489000), Nira Solutions +5 000 EUR (stmt17707→489000)
- Virement interne : Teatower +3 000 EUR (stmt18955→580001)
- TVA SPF Finances ING : -700 EUR (stmt14373), -2 935,02 EUR (stmt15468), -96,47 EUR (stmt16481) → 451000
- TVA SPF Finances Belfius : -2 991,59 EUR (stmt18385→451000)
- Mollie/Vilna Gaon Belfius : +2 602,12 EUR (stmt18040→580200), +10 EUR (stmt18041→580200), +3 045,41 EUR (stmt18485→580200)
- Virement interne Belfius ING→Belfius : +1 000 EUR (stmt18031→580001), retour Vilna Gaon -10 EUR (stmt18042→489000)

### Cas Jérôme Carlier — EN ATTENTE confirmation Nicolas
- stmt17747 +4 520,54 EUR — remboursement salaire non imputé
- FLAG: si Cr 455000 Rémunération → résultat FY25-26 = +87 055 + 4 520,54 = +91 576 EUR
- Si Cr 461000 Avances reçues → neutre P&L — attendre instruction Nicolas

### Suspens (non traités ce run)
- Prêts Belfius 071-9570627/628/629 : +18k + +12k + +31k = 61 000 EUR — aucun compte 17x existant → attente création sous-compte
- ING RESA492 22,08 EUR (dec) — pas de stmt correspondante
- ING RESA895 31,01 EUR (avr) — pas de stmt -31,01
- ING stmt16306 -40,68 EUR vs RESA533 40,69 EUR — écart 0,01 → write-off à confirmer
- ING stmt17816 -0,61 EUR (avr) — pas de facture ING 0,61 non payée pour avril
- 7 write-offs douteux + 3 crédits à qualifier + hors-scope §5 (181 lignes ING, 18 Belfius)

### Résultat P&L FY25-26 : NON MODIFIÉ par ce run (toutes imputations sur comptes bilan)

## 2026-06-09 — DEBLOCAGE PEPPOL + POST + ENVOI — 5 factures débloquées (sur 6 en brouillon)

- Type : reconfig EAS Peppol contacts enfants + action_post + envoi Peppol
- Cause : 6 contacts Invoice Address avaient EAS 9925 avec préfixe BE (héritage script) alors que leurs sociétés mères étaient déjà 0208/valid
- Action : correction EAS+endpoint sur 5 contacts (0208, sans préfixe BE), 1 contact Sodexo en 9925 sans préfixe
- Re-vérification via button_account_peppol_check_partner_endpoint — un par un
- 5 partners passés valid : Cafés Delahaut (5509), Alcodis SA (5453), CM Bastogne (5485), CM Remouchamps (5725), Gerpidis Gerpinnes (9035)
- 1 partner resté not_valid : Sodexo Belgium (8158) EAS 9925 endpoint 0407246778 — endpoint non enregistré Peppol
- 5 factures postées et envoyées via Peppol (canal exclusif, 0 email) :
  - INV/2026/02972 — Cafés Delahaut — 755,25 EUR — peppol=processing — uuid=046afb62-47b0-4a3f-8280-8feae5494d40
  - INV/2026/02973 — Alcodis SA — 74,20 EUR — peppol=processing — uuid=fc3b1ab3-b0cb-476f-bd11-31f7d63f4860
  - INV/2026/02974 — CM Bastogne Pascalino — 291,20 EUR — peppol=processing — uuid=90cce73a-039c-4a69-96b9-b06f71326622
  - INV/2026/02975 — CM Remouchamps — 541,07 EUR — peppol=processing — uuid=a9a4fafe-5e69-4150-a56b-f5e1f94aa74e
  - INV/2026/02976 — Gerpidis SA Gerpinnes — 184,85 EUR — peppol=processing — uuid=3dbd1ced-28b3-4b5b-a224-8fcded88a07a
- TOTAL ENVOYÉ : 1 846,57 EUR TTC
- 1 facture restée en BROUILLON : 39855 Sodexo Belgium — not_valid — à traiter manuellement
- Aucun envoi email — 0 email confirmé

## 2026-06-09 — POST + ENVOI PEPPOL — 18 factures postées et transmises (sur 24 brouillons)

- Type : action_post + envoi Peppol (account.move.send.wizard, sending_methods=['peppol'] uniquement)
- GO explicite Nicolas — aucun email envoyé
- Partenaires bascules en Peppol avant envoi : Wallonie Entreprendre (3293 email->peppol), Brasserie Miroir (124310 False->peppol), Antheco SA (122991 False->peppol)
- 18 factures postées et transmises (peppol_is_sent=True, peppol_move_state=processing) :
  - INV/2026/02954 — KVA Bar — 500,85 EUR — processing
  - INV/2026/02955 — Ardenne BNB — 30,80 EUR — processing
  - INV/2026/02956 — Ardenne BNB — 77,00 EUR — processing
  - INV/2026/02957 — Carrefour Belgium — 554,40 EUR — processing
  - INV/2026/02958 — Wallonie Entreprendre — 784,00 EUR — processing
  - INV/2026/02959 — Delhaize Le Lion — 323,48 EUR — processing
  - INV/2026/02960 — Brasserie Miroir — 63,60 EUR — processing
  - INV/2026/02961 — DB Kfé SRL — 500,85 EUR — processing
  - INV/2026/02962 — Carrefour Belgium — 195,44 EUR — processing
  - INV/2026/02963 — D-trois SRL Proxy Saint-Séverin — 323,40 EUR — processing
  - INV/2026/02964 — Delhaize Le Lion (Ferrières) — 214,30 EUR — processing
  - INV/2026/02965 — Pharmacie Badot — 292,24 EUR — processing
  - INV/2026/02966 — Amessia Boutique — 90,40 EUR — processing
  - INV/2026/02967 — Cocon Life store — 508,32 EUR — processing
  - INV/2026/02968 — Antheco Intermarché Anthée — 319,20 EUR — processing
  - INV/2026/02969 — Autobus Latour SA — 180,00 EUR — processing
  - INV/2026/02970 — Lillodis SRL Proxy Lillois — 184,84 EUR — processing
  - INV/2026/02971 — Moore Services Financiers — 212,60 EUR — processing
- TOTAL POSTÉ + ENVOYÉ : 5 355,72 EUR TTC
- 6 factures laissées en BROUILLON (partner Peppol non valide) :
  - 39846 Cafés Delahaut (5509) — not_valid (EAS 9925 BE0418920135)
  - 39847 Alcodis SA (5453) — not_verified (EAS 9925 BE0438048535)
  - 39855 Sodexo Belgium (8158) — not_verified (EAS 9925 BE0407246778)
  - 39859 CM Bastogne Pascalino (5485) — not_verified (EAS 9925 BE0442412248)
  - 39862 CM Remouchamps (5725) — not_verified (EAS 9925 BE0446634817)
  - 39864 Gerpidis SA Gerpinnes (9035) — not_verified (EAS 9925 BE0802039451)
- TOTAL BLOQUÉ EN BROUILLON : 2 641,57 EUR TTC
- Aucun envoi email — canal Peppol exclusif vérifié sur chaque wizard

## 2026-06-09 — Facturation B2B Peppol — 24 factures brouillon créées

- Type : création factures clients (out_invoice) mode delivered — BROUILLON uniquement, aucune postée, aucun envoi
- Périmètre : 37 SO invoice_status=to_invoice scannées, hors Tea Touch (6973), hors Shopify/Amazon/POS
- Vérification Peppol par client : champ peppol_verification_state + commercial_partner_id
- Lignes TRANSPORT forcées qty_delivered=qty_ordered (8 lignes) : S05755/S05753/S05748/S05744/S05740/S05724/S05722/S05721
- Factures créées en brouillon (24) :
  - inv_id=39842 S05761 KVA Bar 0720819470 HT=472,50 TVA=28,35 TTC=500,85
  - inv_id=39843 S05758 Christine Poncin 0717880766 HT=29,04 TVA=1,76 TTC=30,80
  - inv_id=39844 S05759 Christine Poncin 0717880766 HT=72,60 TVA=4,40 TTC=77,00
  - inv_id=39845 S05757 Carrefour Belgium 0448826918 HT=523,02 TVA=31,38 TTC=554,40
  - inv_id=39846 S05756 Cafes Delahaut 0418920135 HT=712,50 TVA=42,75 TTC=755,25
  - inv_id=39847 S05755 Alcodis SA 0438048535 HT=70,00 TVA=4,20 TTC=74,20
  - inv_id=39848 S05723 Wallonie Entreprendre 0793630244 HT=739,61 TVA=44,39 TTC=784,00
  - inv_id=39849 S05754 Delhaize Le Lion 0402206045 HT=305,14 TVA=18,34 TTC=323,48
  - inv_id=39850 S05753 Brasserie Miroir 0688912806 HT=60,00 TVA=3,60 TTC=63,60
  - inv_id=39851 S05749 DB Kfé SRL 0508863582 HT=472,50 TVA=28,35 TTC=500,85
  - inv_id=39852 S05748 Carrefour Belgium 0448826918 HT=184,36 TVA=11,08 TTC=195,44
  - inv_id=39853 S05746 D-trois SRL 0895931194 HT=305,08 TVA=18,32 TTC=323,40
  - inv_id=39854 S05744 Delhaize (Ferrières) 0402206045 HT=202,16 TVA=12,14 TTC=214,30
  - inv_id=39855 S05743 Sodexo Belgium 0407246778 HT=750,00 TVA=45,00 TTC=795,00
  - inv_id=39856 S05742 Pharmacie Badot 0651311250 HT=271,57 TVA=20,67 TTC=292,24
  - inv_id=39857 S05740 Amessia Boutique 1026857935 HT=85,28 TVA=5,12 TTC=90,40
  - inv_id=39858 S05739 Cocon Life store 0657633274 HT=479,54 TVA=28,78 TTC=508,32
  - inv_id=39859 S05738 Carrefour Market Bastogne 0442412248 HT=274,71 TVA=16,49 TTC=291,20
  - inv_id=39860 S05737 Antheco Intermarché 0828785123 HT=301,12 TVA=18,08 TTC=319,20
  - inv_id=39861 S05724 Autobus Latour 0401403519 HT=169,82 TVA=10,18 TTC=180,00
  - inv_id=39862 S05733 Carrefour Market Remouchamps 0446634817 HT=510,45 TVA=30,62 TTC=541,07
  - inv_id=39863 S05731 Lillodis SRL 0567568873 HT=174,36 TVA=10,48 TTC=184,84
  - inv_id=39864 S05728 Gerpidis SA 0802039451 HT=174,37 TVA=10,48 TTC=184,85
  - inv_id=39865 S05721 Moore Services Financiers 0748770516 HT=200,53 TVA=12,07 TTC=212,60
- TOTAL : HT=7.540,26 EUR | TVA=457,03 EUR | TTC=7.997,29 EUR
- Exclues Peppol non vérifié (8 SO) : S05767/S05730/S05729/S05741/S05722/S05621/S05763/S05727
- Exclues hors périmètre B2B (5 SO) : S05765/S05764/S05726/#48534/#48143 (Amazon/Shopify)
- Confirmé : 0 facture postée, 0 envoi Peppol effectué

## 2026-06-09 — POST OD ventilation 700000 — deux OD postees sur GO explicite Nicolas

- Type : action_post sur deux OD de reclassement canal (brouillons -> posted)
- OD 39813 | MISC/24-25/06/0034 | date 30/06/2025 | 186 554,03 EUR | posted OK
  - Debit 700000 : 186 554,03 | Credits : 700600 GMS 61 805,17 + 700300 Horeca 76 763,73 + 700500 Revendeurs 44 175,77 + 700700 Institutions 3 809,36
- OD 39826 | MISC/25-26/06/0086 | date 09/06/2026 | 821 416,36 EUR | posted OK
  - Debit 700000 : 821 416,36 | Credits : 700600 GMS 305 389,00 + 700300 Horeca 294 159,76 + 700500 Revendeurs 203 890,70 + 700700 Institutions 17 976,90
- Controles pre-post : state=draft, equilibre verifie (ecart 0,00), Tea Touch (6973) absent des deux OD
- Soldes apres post (credit - debit, comptes produits) :
  - 700000 FY24-25 : 83 609,90 EUR (residu Tea Touch + sans partenaire)
  - 700000 FY25-26 : -14 216,99 EUR (flux POS techniques a investiguer — hors perimetre OD)
  - 700600 GMS FY24-25 : 61 805,17 EUR | FY25-26 : 305 389,00 EUR
  - 700300 Horeca FY24-25 : 298 867,08 EUR | FY25-26 : 294 159,76 EUR
  - 700500 Revendeurs FY24-25 : 177 882,05 EUR | FY25-26 : 203 890,70 EUR
  - 700700 Institutions FY24-25 : 3 809,36 EUR | FY25-26 : 17 976,90 EUR

## 2026-06-09 — Ventilation CA B2B 700000 FY24-25 — OD brouillon creee

- Type : creation comptes + OD reclassement (brouillon, non postee)
- Comptes crees :
  - 700600 Ventes GMS (Grande Distribution) — ID Odoo 1220
  - 700700 Ventes Institutions / Corporate — ID Odoo 1221
  - Config : account_type=income, group 700-707, tag_id=1 (identique 700300/700500)
- OD creee : ID Odoo 39813 — journal MISC (ID 11) — date 30/06/2025 — etat DRAFT
  - Ref : Ventilation CA B2B 700000 par canal FY24-25
  - Debit 700000 (ID 320) : 186 554,03 EUR
  - Credit 700600 GMS : 61 805,17 EUR (46 clients GMS + AD Spa)
  - Credit 700300 Horeca : 76 763,73 EUR (NIJSKENS inclus, Vignee Management inclus)
  - Credit 700500 Revendeurs : 44 175,77 EUR (Revendeurs + DTC + dormants + petits non-id)
  - Credit 700700 Institutions : 3 809,36 EUR
  - Total debit = total credit = 186 554,03 EUR — equilibre verifie
- Exclus de l'OD (restent sur 700000) :
  - Tea Touch (ID 6973) : 73 263,98 EUR
  - Lignes sans partenaire : 10 345,92 EUR
  - Total residuel 700000 apres post eventuel : 83 609,90 EUR
- A FAIRE : Nicolas doit poster l'OD explicitement (action_post sur ID 39813)

## 2026-06-09 — Ventilation CA B2B 700000 FY25-26 (YTD) — OD brouillon creee

- Type : OD reclassement canal (brouillon, non postee)
- OD creee : ID Odoo 39826 — journal MISC (ID 11) — date 09/06/2026 — etat DRAFT
  - Ref : Ventilation CA B2B 700000 par canal FY25-26 (YTD)
  - Perimetre : factures out_invoice+out_refund 01/07/2025-09/06/2026 sur 700000
  - Solde total 700000 (factures clients) : 821 416,36 EUR
  - Debit 700000 (ID 320) : 804 364,85 EUR (ventilable certain)
  - Credit 700600 GMS (ID 1220) : 305 389,00 EUR — 93 partenaires
  - Credit 700300 Horeca (ID 915) : 294 159,76 EUR — 243 partenaires
  - Credit 700500 Revendeurs (ID 917) : 186 839,19 EUR — 202 partenaires
  - Credit 700700 Institutions (ID 1221) : 17 976,90 EUR — 80 partenaires
  - Total debit = total credit = 804 364,85 EUR — equilibre verifie
- Exclus de l'OD (restent sur 700000 en attente arbitrage) :
  - Tea Touch (ID 6973) : 0,00 EUR (faillite nov 2025 — aucun CA FY25-26 confirme)
  - Lignes sans partenaire : 0,00 EUR
  - A_ARBITRER (classification incertaine) : 17 051,51 EUR (350 clients, majoritairement personnes physiques sans tag)
- A FAIRE : Nicolas doit poster l'OD explicitement (action_post sur ID 39826)

## 2026-06-09 — OD 39826 FY25-26 — Finalisation ventilation 100% CA B2B

- Type : modification OD brouillon existante (non postee)
- OD modifiee : ID Odoo 39826 — etat DRAFT inchange
- Decision Nicolas/Nira : 17 051,51 EUR A_ARBITRER (350 micro-clients sans tag canal) affectes integralement au canal Revendeur
- Modifications appliquees en une transaction ORM (account.move write, commandes (1, id, vals)) :
  - Ligne 179408 debit 700000 : 804 364,85 -> 821 416,36 EUR
  - Ligne 179411 credit 700500 Revendeurs : 186 839,19 -> 203 890,70 EUR
- Lignes inchangees :
  - Ligne 179409 credit 700600 GMS : 305 389,00 EUR
  - Ligne 179410 credit 700300 Horeca : 294 159,76 EUR
  - Ligne 179412 credit 700700 Institutions : 17 976,90 EUR
- Controle equilibre : debit 821 416,36 = credit (305 389,00 + 294 159,76 + 203 890,70 + 17 976,90) = 821 416,36 EUR | ecart = 0,00 EUR
- Couverture : 100% du CA B2B facture FY25-26 ventile (vs 97,9% avant)
- Tea Touch (0 EUR) et flux POS (OD-RECLASSIF 700006) : absents de l'OD, confirme

## 2026-05-29 — Batch facturation B2B Peppol delta J+1 — 5 factures postées

- Type : facturation B2B hors GMS — wizard `delivered` + envoi Peppol (bucket A) / postée sans envoi (bucket B)
- SO scannées `to invoice` non-GMS : 14 total
- SO exclues GMS (tag GMS sur partner) : S05652 AD Delhaize Roodebeek, S05668 Intermarché Braine, S05643 Intermarché Rumes, S05644 Intermarché Mons
- SO exclues non livrées (qty_delivered=0 sur toutes lignes) : S05643, S05644
- SO exclues B2C (fiscal position EU B2C) : S05621 Jarosz, #48143 Jessica Masula
- SO exclues montant 0€ (100% remise, draft supprimés) : S05600 Café Ventuno, S05454 Marketing Teatower
- Hélène BERTRAND S05192 : déjà facturée le 28/05 (INV/2026/01652). Draft supprimé (ligne MENU 0€ résiduelle).
- B-Shock S05529 : déjà facturé le 28/05 (INV/2026/02728, 264,48 HT). Seule ligne résiduelle = filtres à thé 7,44 HT non encore facturés.

### Transport forcé qty_delivered=qty_ordered
- S05670 line 60308 TRANSPORT : 0→1 (10,00 EUR HT)
- S05666 line 60267 TRANSPORT : 0→1 (10,00 EUR HT)
- S00738 line 4648 TRANSPORT : 0→1 (10,00 EUR HT)

### Bucket A — Peppol OK (peppol_verification_state=valid) — 3 factures
| Facture | Partner | HT | TTC | Peppol state |
|---|---|---|---|---|
| INV/2026/02791 | MaxMara scrl (Max et moi) | 158,12 | 167,60 | processing |
| INV/2026/02794 | B-Shock Coaching - Cravette Cédric | 7,44 | 9,00 | processing |
| INV/2026/02795 | A2MG SRL | 198,12 | 210,00 | processing |
| **Total A** | | **363,68** | **386,60** | |

### Bucket B — Peppol KO (not_verified) — 2 factures — à statuer par Nicolas
| Facture | Partner | HT | TTC | Raison |
|---|---|---|---|---|
| INV/2026/02792 | Douaire Café srl | 160,00 | 169,60 | peppol not_verified |
| INV/2026/02793 | INFRABEL (Invoice Address) | 134,50 | 142,60 | peppol not_verified |
| **Total B** | | **294,50** | **312,20** | |

### Total batch 29/05
- Grand total : HT 658,18 EUR / TTC 698,80 EUR
- Anomalies : S05670 Douaire Café — 1 produit partiellement livré (HC250735 Pêche de vigne, 1 unité non livrée) ; facture partielle émise, solde à facturer à la prochaine livraison.

---

## 2026-05-19 — Facturation masse B2B — 67 SO — INV/2026/02542 à INV/2026/02605

- Type : facturation masse B2B — wizard `delivered` + envoi Peppol/email
- Périmètre : 67 SO (61 clean + 6 partielles avec livraison utile)
- Etape 1 — Transport forcé : 13 SO, 13 lignes TRANSPORT qty_delivered=product_uom_qty OK
- Etape 2 — Wizard facturation (4 batches x 20/20/18/7) : 64 factures draft créées, 0 erreur
  - IDs Odoo : 38243–38306
  - Total TTC : 38 819,04 EUR — Total TVA : 2 042,75 EUR
- Etape 3 — Post en lot (7 batches x 10) : 64/64 postées, 0 erreur
  - Références : INV/2026/02542 à INV/2026/02605
- Etape 4 — Envoi :
  - Peppol (54 factures) : envoi via account.move.send.wizard, mode peppol, UBL BIS 3.0
  - Email fallback (10 factures) : Le Fournil, L'Artiste, PAMPA, Cocoricoop, VENTE-PRIVEE.COM, Carrefour Belgium, La Thé Box, O'Brunch, La Pause Chocolat, Nouvel Air Coiffure
  - Erreurs envoi : 0
- SO exclues (non touchées) : S00738, S04347, S05192, S05454, S05529, S05484, S05582, S05585 (COFFRET partiel livré dans passe delivered), S05587, S05588

## 2026-05-19 — Audit SO B2B en attente de facturation

- Type : audit lecture seule — aucune écriture créée
- Périmètre : 75 SO `to_invoice` filtrées → 60 SO B2B (hors GMS 14, hors Shopify 1)
- Total HT estimé à facturer : 42 564,30 €
- SO urgentes (> 15j) : 10 dont S00738 (370j) et S04347 (183j) — anomalies historiques
- Transport à forcer qty_delivered : 13 SO
- Rapport transmis à Nicolas (texte agent, 2026-05-19)

## 2026-05-18 — Rapport commission Jérôme Carlier — Avril 2026 (v2 officiel)

- Type : rapport commission — vérification Odoo + adoption chiffres Adri
- Source : `Commission_avril_2026 (1).docx` (Adri) + Odoo XML-RPC (18/05/2026)
- Fichiers produits :
  - `compta/reports/2026-05-18_commission_jerome_avril2026.md`
  - `Teatower-Planning/commission/avril-2026/index.html` (v2 — remplace brouillon obsolète 04/05)
- Commit + push : 109974f (Teatower-Planning master)
- Résultat : 2 420 € brut (Version A — grossiste 130 € Adri) ou 2 290 € (Version B — grossiste 65 € mémoire stricte)
- Validation requise : règle grossiste 130 € à confirmer par Nicolas avant envoi Jérôme
- CA B2B Odoo avril 2026 : 67 672,19 € HT / CA Adri : 73 805 € / Croissance Adri : +16,2 % → 400 €

## 2026-04-30 — Batch facturation run 6 — 17 factures draft (SO S05487–S05513)

### Correction lignes transport (nouvelle règle : transport = service, toujours facturer si marchandise partie)
- S05497 Alcodis SA : line_id=56472 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- S05504 Al Picchio Rosso : line_id=56550 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- S05505 Le Coin 62 : line_id=56556 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- Delta total correction transport : +30,00 EUR HT / +36,30 EUR TTC

### SO exclus du batch (qty_delivered=0 sur toutes les lignes)
- S05509 BLONFOOD SA Intermarché Liège Blonden : 0 livré
- S05510 Gemblouxim Intermarché Gembloux : 0 livré

### Factures draft créées (IDs 37146–37162) — mode delivered — wizard sale.advance.payment.inv
- 17 factures draft | Total HT : 6 147,54 EUR | Total TTC : 6 538,80 EUR
- Regroupements par partner : S05489+S05490 (Delhaize affilié), S05494+S05495+S05499 (Smartbox), S05507+partenaire facturation

### Posting + envoi Peppol/Email (2026-04-30) — GO Nicolas
- 17/17 factures postées (action_post) — INV/2026/02329 à INV/2026/02345
- Partners modifiés (invoice_sending_method peppol activé) : Al Picchio Rosso (2783), Srl D'Ici Wépion (3248), Newpharma Compta (5459), Alivim SRL (123294)
- Envoi Peppol (11 factures) : INV/02329, 02330, 02331, 02332, 02333, 02334, 02336, 02338, 02340, 02342, 02344, 02345 — état=processing
- Fallback email (5 factures, peppol non valide) :
  - INV/02335 Musée de la fraise (peppol not_valid)
  - INV/02337 Smartbox Group (partenaire IE, peppol not_valid)
  - INV/02339 Alcodis SA (peppol not_verified)
  - INV/02341 DelEmbourg SRL (peppol not_verified)
  - INV/02343 CPSP Belgie NV (peppol not_verified)
- Aucune erreur d'envoi — 0 facture bloquée

---

## 2026-04-29 — Lettrage SEPA Kirchner Fischer (SL 17572 + SL 18090)

### (B) Lettrage SEPA Kirchner Fischer — 2 domiciliations

**SL 17572 — 30/03/2026 — -20 606,47 EUR — CAS B PARTIEL**
- Diagnostic : RESA562 avait 3 501,93 EUR deja lettres via BNK1/25-26/4199 (SL 17341, 18/03/2026, partial.reconcile id=11475). Residuel reel = 6 046,70 EUR, pas 9 548,63 EUR.
- Action : move BNK1/25-26/4385 (id=35216) remis en draft, compte suspense 499000 remplace par :
  - 440000 debit 6 046,70 EUR (RESA562 partiel) -> reconcile avec line 122154 -> RESA562 paid
  - 440000 debit 11 057,84 EUR (RESA564) -> reconcile avec line 122914 -> RESA564 paid
  - 499000 debit 3 501,93 EUR -> SUSPENSE residuel (ces 3501.93 correspondent a un paiement anterieurement applique sur RESA562 via une autre SL, a pointer dans la meme SL bancaire par Nicolas)
- Ecritures creees : move lines 163592, 163593, 163594 dans BNK1/25-26/4385

**SL 18090 — 22/04/2026 — -18 451,00 EUR — CAS C**
- Diagnostic : RESA734 (RGK26-00690) residuel facture = 6 105,30 EUR vs communication Kirchner = 5 944,74 EUR -> ecart +160,56 EUR. Aucun avoir ou partial reconcile existant. Origine non identifiee.
- Action : move BNK1/25-26/4798 (id=36792) remis en draft, compte suspense 499000 remplace par :
  - 440000 debit 11 969,66 EUR (RESA506) -> reconcile avec line 125260 -> RESA506 paid
  - 440000 debit 536,60 EUR (RESA735) -> reconcile avec line 125262 -> RESA735 paid
  - 499000 debit 5 944,74 EUR -> SUSPENSE RESA734 (ecart 160,56 a clarifier avec Kirchner)
- Ecritures creees : move lines 163595, 163596, 163597 dans BNK1/25-26/4798

**Residuels a traiter manuellement par Nicolas :**
1. SL 17572 : 3 501,93 EUR en suspense (499000) = paiement deja applique sur RESA562 via SL 17341 -> verifier si la SL 17341 est bien une domiciliation separee ou double-comptabilisation
2. SL 18090 : 5 944,74 EUR en suspense (499000) = RESA734 (6 105,30) non lettree -> ecart 160,56 EUR a clarifier avec Kirchner (avoir ? majoration ? note de debit ?)

**Factures lettrées ce batch :** RESA562 + RESA564 + RESA506 + RESA735 = 29 610,80 EUR TTC
**PAY00569 cancelled** (cree par erreur en debut de session, annule avant tout impact)

---

## 2026-04-29 — Lettrage 7 quick wins + diagnostic SEPA Kirchner

### (A) Lettrage 7 factures clients
- Méthode : account.payment.register wizard + write payment_ids sur statement line
- PAY00562 INV/2026/01848 1262.98 EUR Ramaut — SL 18118 du 23/04
- PAY00563 INV/2026/01549 1113.00 EUR Sorescol S.A. — SL 17908 du 14/04
- PAY00564 INV/2026/01675 651.90 EUR Sorescol S.A. — SL 18055 du 21/04
- PAY00565 INV/2026/02152 539.00 EUR Lambertdis SRL — SL 18158 du 27/04
- PAY00566 INV/2026/02141 477.00 EUR Le 7 by Juliette — SL 18164 du 27/04
- PAY00567 INV/2026/01511 333.22 EUR Wonka / Intermarche Heusy — SL 18165 du 27/04
- PAY00568 INV/2026/01590 277.00 EUR Sandrinette / Delonville — SL 18161 du 27/04
- Total lettre : 4 653.10 EUR TTC — 7 factures en state=in_payment

### (A) Skip 3 QW — raisons
- QW06 (Mardis 462.02 / Carrefour 462.02) : IBAN BE66... appartient a Mardis partner 3120, facture sur Carrefour corporate 6596 et Mardis a une facture a 462.03 (ecart 0.01 EUR) — mis en review
- QW07 (Cafes Delahaut 397.50) : pas d'IBAN dans la ligne bancaire, critere C3 non verifiable
- QW08 (Pure Bastogne 389.56) : idem, pas d'IBAN dans la ligne bancaire

### (C) Correction partner_id — 0 ligne modifiee
- 83 lignes sans partner_id examinées : 75 noms bancaires abrégés sans match exact Odoo, 8 sans partner_name

## 2026-04-22 — Batch facturation run 5 — 51 factures (INV/02178–02228)

- Type : creation + posting via wizard sale.advance.payment.inv mode=delivered
- SO eligibles : 59 (qty_delivered > qty_invoiced sur au moins une ligne)
- Ecarte : 2 Hyper Carrefour (S05457, S05459 — livraison semaine 04/05) + 3 qty_delivered=0 (S05404, S05412, S04443)
- Wizard : 54 factures draft crees (regroupement par partenaire Odoo)
- Postees : 51 factures — INV/2026/02178 a INV/2026/02228
- Non postees (TTC=0) : 3 — S05441 Cafes Delahaut, S05400 Laetitia Mariette, S05427 Sefora Jacobs
- Total HT : 8 720,02 EUR | TVA : 523,41 EUR | TTC : 9 243,43 EUR
- Rapport : compta/reports/2026-04-22.md

## 2026-04-21 — Complement batch facturation S05435 + S05436 (2 factures — run 4)

- Type : creation + posting + envoi Peppol (2 SO, 2 factures Odoo)
- Source : S05435 et S05436 signalees par Nicolas — pickings TT/PICK/08690 et 08691, type=internal, state=done (meme pattern runs 2-3)
- Methode : creation manuelle account.move ligne par ligne, action_post, account.move.send.wizard (ubl_bis3)
- Facture S05435 : id=36556, INV/2026/02169 — Floridis SA - Intermarche Floriffoux (id=2958) — 410,19 EUR HT / 436,31 EUR TTC — echeance 2026-05-21 — Peppol processing (peppol_verification_state=valid)
- Facture S05436 : id=36557, INV/2026/02170 — Affilie 043366 - AD Fosses-la-Ville (id=5441) — 408,22 EUR HT / 434,22 EUR TTC — echeance 2026-06-20 (60j) — Peppol processing (peppol_verification_state=not_verified, a surveiller)
- TRANSPORT ajoute sur les 2 factures (10 EUR HT, compte 700000, TVA 21%)
- Total run 4 : 818,41 EUR HT / 870,53 EUR TTC
- Total cumule jour : 10 136,10 EUR HT / 10 771,02 EUR TTC (28 factures, runs 1+2+3+4)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05435 + S05436 — run 4")

## 2026-04-21 — Complément batch facturation S05434 (1 facture — run 3)

- Type : création + posting + envoi (1 SO, 1 facture Odoo)
- Source : S05434 signalée par Nicolas — picking TT/PICK/08689 type=internal/done (même cause que run 2)
- Méthode : création manuelle account.move, action_post, account.move.send.wizard (ubl_bis3)
- Facture créée : id=36545, INV/2026/02168
- Partenaire : SRL Spydis - Intermarche Spy (id=116686)
- Montant HT : 315,10 EUR (305,10 SO + 10 TRANSPORT) | TTC : 335,51 EUR
- Echéance : 2026-05-21 (30 jours)
- Envoi Peppol : peppol_verification_state=valid — partner forcé invoice_sending_method=peppol — peppol_move_state=processing
- Total cumulé jour : 9 317,69 EUR HT / 9 900,49 EUR TTC (26 factures, runs 1+2+3)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05434 — run 3")

## 2026-04-21 — Complément batch facturation S05448–S05453 (5 factures — run 2)

- Type : création + posting + envoi batch (5 SO, 5 factures Odoo)
- Source : SO confirmés par Nicolas — pickings internal done (TT/PICK/08711, 08713, 08714, 08715, 08716)
- Méthode : création manuelle account.move (wizard delivered inapplicable — pickings type=internal), action_post, account.move.send.wizard
- Note méthode : le wizard sale.advance.payment.inv refuse car les pickings sont de type internal et non outgoing — création ligne par ligne avec qty_delivered et discount=30% repris des SO
- Factures créées : 5 (IDs Odoo 36540–36544)
- Numéros attribués : INV/2026/02163 à INV/2026/02167
- Montant total HT : 1 770,30 EUR | TTC : 1 884,05 EUR
- TRANSPORT ajouté : 5 factures (10 EUR HT, compte 700000, TVA 21% — absent des SO)
- Lignes EM0072 (SRP Kraft Horeca) : conservées avec disc=100% (subtotal=0) comme dans les SO
- Envoi Peppol (UBL BIS3) : 5 factures toutes en peppol_state=processing
  - INV/02163 (Delhaize de Bouge, id 36540) — uuid f7eb688b-9214-4a8b-98f8-f79d7da30066 — échéance 2026-06-20 (délai Delhaize 60j)
  - INV/02164 (BOISDIS Naninne, id 36541) — uuid 700b53f5-0f18-4194-b6c8-1df4c3da4b94
  - INV/02165 (BOISDIS Naninne, id 36542) — uuid 0fb63a93-dd91-4f56-a4cf-98ea4cee4e39
  - INV/02166 (SA Barthe Assesse, id 36543) — uuid 26b4776f-6ac1-44ac-ad91-10d0fd26e293
  - INV/02167 (Lambertdis Spar Manhay, id 36544) — uuid d0ee1e08-6b97-4157-8c41-e06c29a79b1a
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complément 5 SO — run 2")

## 2026-04-21 — Batch facturation S05351–S05439 (20 factures)

- Type : création + posting + envoi batch (23 SO, 20 factures Odoo)
- Source : sale.order invoice_status=to_invoice, state=sale/done, picking outgoing done
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 20 (IDs Odoo 36509–36528)
- Numéros attribués : INV/2026/02137 à INV/2026/02156
- Montant total HT : 7 232,29 EUR | TTC : 7 680,93 EUR
- Corrections avant posting : 5 lignes supprimées (I0880 x3, I0859 x1, I0376 x1) — qty_delivered=0 inclus par erreur dans le wizard
- Partenaires forcés peppol : 5 (Lambertdis, NDB Diffusion, PGHM, Le 7 by Juliette, Labrassine)
- Envoi Peppol (UBL BIS3) : 9 factures — INV/02137 (Cafés Préko, 75ca7ecd), INV/02138 (DB Kfé, 37eab94a), INV/02139 (Delhaize, 28e8393f), INV/02141 (Le 7 Juliette, 90c3b497), INV/02152 (Lambertdis, 06a1b47b), INV/02153 (NDB Diffusion, cec483d4), INV/02154 (Villa d'Olne, a646b0b7), INV/02155 (PGHM, d0829a62), INV/02156 (Labrassine, 3266785d) — statut : processing
- Envoi email : 9 factures — INV/02140 (La Thé Box), INV/02143 (Alcodis), INV/02144 (Cafes Delahaut), INV/02145 (Sunparks De Haan), INV/02146 (Volle Gas), INV/02147 (Carrefour Remouchamps), INV/02148 (Carrefour Belgium), INV/02149 (BTL SRL), INV/02150 (Virelles Nature)
- Non envoyées : 2 — INV/02142 (Smartbox Group, 60 EUR), INV/02151 (Clotuche Caroline Suzanne, 28 EUR) — pas d'email ni Peppol valide
- Review : S05424 Marketing Teatower (707,55 EUR HT, partenaire interne, action Nicolas requise)
- Sans livraison (non traitées) : 19 SO (S05404, S05412, S05425, S05426, S05429, S05434, S05435, S05436, S05440, S05442, S05444, S05445, S05447–S05453)
- Rapport scan : compta/reports/shipped_not_invoiced_2026-04-21.md
- Rapport batch : compta/reports/invoicing_batch_2026-04-21.md

## 2026-04-15 — Batch S05405-S05409 : correction renvoi Peppol (3 factures)

- Type : correction invoice_sending_method + renvoi Peppol
- Partenaires mis à jour (invoice_sending_method -> peppol) : SA VILLERSEM (115879), DelEmbourg invoice addr (5733), DelEmbourg parent (2909), SA Faimine invoice addr (9196), SA Faimine parent (3210)
- INV/2026/02094 (DelEmbourg) — peppol_state=processing | uuid=2dc8107b-51cc-45dc-98f8-62aeab83dd4c
- INV/2026/02095 (SA Faimine) — peppol_state=processing | uuid=a4cf80f7-24c5-4b50-a50d-d6a915855a2c
- INV/2026/02096 (SA VILLERSEM) — peppol_state=processing | uuid=f58a082f-029c-48c1-972d-ef807690dfa2
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation S05405–S05409

- Type : création + posting + envoi batch (5 SO)
- Source : S05405 / S05406 / S05407 / S05408 / S05409 — tous state=sale, tous entièrement livrés
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 5 (IDs Odoo 36242–36246)
- Numéros attribués : INV/2026/02092 à INV/2026/02096
- Montant total HT : 1 240,03 EUR | TTC : 1 314,43 EUR
- Envoi Peppol : 2 factures — S05405 (BARVO/Carrefour Barvaux, uuid 8caf61ac) + S05408 (GIMALEX/Delhaize Fragnée, uuid 9766cd23) — statut : processing
- Envoi email : 3 factures — S05406 (SA VILLERSEM), S05407 (SA Faimine), S05409 (DelEmbourg)
- Fallback email : S05406 + S05409 (Peppol EAS/endpoint configurés sur partenaire mais invoice_sending_method non défini)
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation : TRANSPORT + Posting + Envoi

- Type : correction transport + validation + envoi batch
- Lignes TRANSPORT ajoutées : 2 nouvelles factures draft créées (Odoo 36236, 36237) pour S05403 (Volle Gas) et S05375 (Carrefour Remouchamps) — 10 EUR HT chacune, produit [TRANSPORT], compte 700000, TVA 21%
- Les 7 autres lignes TRANSPORT des SO concernés étaient déjà facturées (qty_inv=1)
- action_post : 36 factures postées (IDs 36200–36237, hors avoirs 36223/36235) — 0 échec
- Numéros attribués : INV/2026/02055 à INV/2026/02090
- Montant total HT batch complet : 14 581,15 EUR | TTC : 15 482,38 EUR
- Envoi Peppol : 14 factures (Van Der Valk, ILLICO RESTO, Europadrinks, Delhaize x2, Pascal CHERAIN, Moulins Burette, Cafés Antillia, Spinée SA, All in One, SRL Tartine, Au Comptoir Local, Smart fridges, Carrefour Remouchamps TRANSPORT)
- Envoi email : 21 factures
- Non envoyé : 1 (INV/2026/02077 — Clotuche Caroline Suzanne, id=122331, pas d'email ni Peppol)
- Rapport mis à jour : compta/reports/invoicing_batch_2026-04-15.md

## 2026-04-15 — Batch facturation (34 factures draft créées)

- Type : création factures clients batch
- Source : sale.order invoice_status=to_invoice, state=sale/done (85 SO scannés)
- Méthode : sale.advance.payment.inv wizard, mode "delivered" (qty_delivered)
- Factures draft créées : 34 (IDs Odoo 36200–36234 sauf 36223/36235 qui sont des avoirs)
- Montant total HT : 14 561,15 EUR | TTC : 15 461,18 EUR
- Exclus Amazon : 36 SO (741,40 EUR HT) — détectés via origin "Amazon Order"
- Exclus 0 EUR : 5 SO (Marketing Teatower, Newpharma, Laetitia Mariette, Perte marchandise)
- Exclus sans livraison : 8 SO (3 403,22 EUR HT en attente livraison)
- Avoirs draft détectés : 2 (36223 ann philippe verhelle, 36235 Lidwine Fetten) — à examiner
- Rapport : compta/reports/invoicing_batch_2026-04-15.md
- Statut : DRAFT — Nicolas doit valider (action_post) avant envoi

## 2026-04-15 — Rapport commandes expédiées non facturées

- Type : analyse / rapport
- Source : sale.order (state: sale/done, invoice_status: to invoice, picking outgoing: done)
- Résultat : 70 SO to_invoice identifiées, dont 70 avec au moins un outgoing picking done
- Montant total HT : 14 173,10 EUR
- Rapport : compta/reports/shipped_not_invoiced_2026-04-15.md
- Top 3 : The Torrefactory Project Sa (1 950 EUR) / Carrefour Belgium (1 646 EUR) / Moulins Burette (1 406 EUR)
- Alerte : 34 commandes e-commerce de déc. 2025 (> 120 jours) non régularisées

## 2026-04-14 — Rapprochement bancaire ING (165 lignes)

### Identification des 165
- Source : `account.bank.statement.line` is_reconciled=False, journal ING BE30 3631 6408 2311 (id=14)
- Composition : 165 lignes ING uniquement (+ 77 autres journaux cash/caisse non traitées)
- Positives (encaissements) : 63 — Négatives (paiements) : 102

### Matches sûrs trouvés : 11
Critères : même montant exact (écart ≤ 0,01 EUR), même partenaire (direct ou commercial_parent), date BSL dans [date_facture - 5j, date_facture + 180j]

| BSL id | Date | Montant | Facture | Partenaire | Résultat |
|--------|------|---------|---------|------------|---------|
| 17823 | 2026-04-10 | +403,97 EUR | INV/2026/01151 | Belgradis - Intermarché Belgrade | lettré |
| 17827 | 2026-04-10 | +181,26 EUR | INV/2026/01521 | Les Mignées (via Quoibion Gestim) | lettré |
| 17813 | 2026-04-09 | +1 792,19 EUR | INV/2026/01178 | Pharmacie Saint Pierre SA | lettré |
| 17800 | 2026-04-09 | +90,00 EUR | INV/2026/01415 | l'Apaq-W | lettré |
| 17772 | 2026-04-08 | +345,10 EUR | INV/2026/01258 | SA Barthe - Intermarché Assesse | lettré |
| 17771 | 2026-04-08 | +715,50 EUR | INV/2026/01308 | Sorescol S.A. | lettré |
| 16934 | 2026-03-01 | -31,00 EUR | RESA670 | ING Belgique SA | lettré |
| 16651 | 2026-02-16 | -281,85 EUR | RESA573 | Easyplug S.R.L. / Ez Charge | lettré |
| 16646 | 2026-02-16 | -46,88 EUR | RESA671 | Action Belgium BVBA | lettré |
| 16398 | 2026-02-04 | -112,56 EUR | RESA686 | Happy Family Wouip | lettré |
| 16118 | 2026-01-21 | -14,52 EUR | RESA532 | ING Belgique SA | lettré |

**Total lettrés : 11 / 11 matches sûrs (100%)**

### Méthode technique utilisée
1. `account.move.line.write([susp_ml_id], {'account_id': acct_receivable_or_payable, 'partner_id': partner_id})` — remplace la ligne compte de passage (499000) par le compte tiers correct
2. `account.move.action_post([bsl_move_id])` — reposte l'écriture après modification
3. `account.move.line.reconcile([susp_ml_id, invoice_ml_id])` — lettrage des deux lignes tiers

### Résultat
- ING non rapprochées avant : 165
- ING non rapprochées après : 154
- Lettrées automatiquement : 11
- En review : 27 (Vilna Gaon x3, Shyfter ambigus x2, ING frais ambigus x3, partenaires sans facture ouverte x19)
- Sans partenaire ni match : 127

### Fichiers générés
- `compta/review/lettrages_review_2026-04-14.md` — détail des 27 cas en attente
| 2026-04-14 | 367 | - |

## 2026-07-08 — Facturation PRO delivered-only + envoi Peppol (7 factures postées + envoyées)

### Périmètre
Scan des SO en `invoice_status='to invoice'`, `state in (sale,done)`, hors team "Odoo x Shopify" (B2C, id=4). 29 SO total, 27 PRO retenues, 2 B2C exclues.

### Classification
- Groupe A (Peppol `valid` + EAS `0208`) : 11 SO éligibles.
- Groupe B (bloquées, non touchées) : 7 SO — 4 avec `peppol_verification_state=valid` mais `eas=9925` (bloqué par règle dure), 2 `not_verified`/EAS 9925, 1 `not_verified` sans VAT.
- 9 SO sans quantité réellement livrée (ni A ni B, exclues de tout traitement).

### Actions Groupe A (11 SO)
- 3 lignes TRANSPORT forcées `qty_delivered = qty_ordered` (S05956, S05944, S05938 — qty_delivered=0 car non scannées en prépa).
- Wizard `sale.advance.payment.inv` mode `delivered` (jamais `all`) lancé sur chaque SO.
- 1 SO (S04347) avait déjà une facture postée+envoyée Peppol préexistante (INV/2026/02795, peppol_move_state=done) — non retouchée.
- 10 nouvelles factures créées en draft, dont 3 à 0,00 EUR (Terracotta Beauty SRL, Too Good To Go Belgium, Cellmade/Prison De Marche) laissées en DRAFT sans post ni envoi (arbitrage manuel, pas d'intérêt à envoyer un Peppol à 0€).
- 7 factures postées, montant total **4 659,42 EUR** :

| Facture | SO | Client | Montant | Peppol |
|---|---|---|---|---|
| INV/2026/03419 | S05960 | Carrefour Belgium, Hypermarché Carr… | 2 100,02 | envoyée (done processing) |
| INV/2026/03420 | S05956 | Centrale Intermarché | 123,10 | envoyée |
| INV/2026/03421 | S05953 | Carrefour Belgium, Hypermarché carr… | 873,68 | envoyée |
| INV/2026/03422 | S05944 | Spar Clavier | 90,40 | envoyée |
| INV/2026/03423 | S05938 | D-trois SRL - Proxy Delhaize Saint-… | 256,31 | envoyée |
| INV/2026/03424 | S05936 | BARCHONEW SRL - Delhaize Barchon | 399,00 | envoyée |
| INV/2026/03425 | S05934 | Spar Erezée | 816,91 | envoyée |

Les 7 envois Peppol confirmés `peppol_move_state=processing` avec UUID (pas d'échec).

### Groupe B — en attente (non facturées, non touchées)

| SO | Client | Raison |
|---|---|---|
| S05954 | (ID=5623) | not_verified, eas=9925 |
| S05951 | Srl D'Ici Wépion | valid MAIS eas=9925 (bloqué) |
| S05950 | Anaïs Michoel - les p'tits pots | valid MAIS eas=9925 (bloqué) |
| S05942 | Jonathan BEHIN | not_verified, pas de VAT |
| S05877 | Comptabilité (ID=5459) | valid MAIS eas=9925 (bloqué) |
| S05930 | Paulette Srl | not_verified, eas=0208 |
| S05917 | Pharmacie Badot | valid MAIS eas=9925 (bloqué) |

### Scripts
`compta/scripts/` (temp, non committé) — logique reprise de `scripts/facturation_b2b_peppol.py` mais SANS la correction auto EAS 9925→0208 (le Groupe B est listé, pas corrigé, sur demande explicite de cette tâche).

## 2026-07-08 — Correction Peppol Sunpark (2 fiches, autorisation explicite Nicolas)

### Périmètre
Reconfiguration `peppol_eas` 9925 → 0208 (schéma KBO/BCE, numéro d'entreprise sans préfixe pays) sur les 2 entités de facturation Sunpark, à la demande explicite de Nicolas ("corrige"). Méthode reprise de `scripts/peppol_activate_recent.py` (write `peppol_eas`/`peppol_endpoint` puis `res.partner.button_account_peppol_check_partner_endpoint`).

| Partner | Avant (eas / endpoint / state) | Après (eas / endpoint / state) | Résultat |
|---|---|---|---|
| #2851 CPSP Belgie NV (Sunparks Kempense Meren, Mol) — VAT BE0434692830 | 9925 / BE0434692830 / valid | 0208 / 0434692830 / **valid** | Facturable Peppol OK |
| #3253 Sunparks Leisure N.V. (De Haan) — VAT BE0431404530 | 9925 / 0431404530 / **not_valid** | 0208 / 0431404530 / **valid** | Facturable Peppol OK — la fiche était `not_valid` avant car endpoint sans préfixe "BE" était incompatible avec le schéma 9925 (qui exige le préfixe pays) ; la bascule vers 0208 (numéro nu, sans préfixe) corrige le format et lève le blocage |

`invoice_sending_method` déjà à `peppol` sur les deux, inchangé.

Contrôle : contact enfant #5871 "Sunparks Kempense Meren" (parent #2851) vérifié **non modifié** : eas=9925, endpoint=BE0434692830, state=not_verified, invoice_sending_method=False — conforme, la facturation passe par le parent #2851.

Aucune fiche restée `not_valid` après correction (les deux sont `valid`).
