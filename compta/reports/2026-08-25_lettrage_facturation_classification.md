# Passe du 25/08/2026 — lettrage ING · facturation Peppol · classification canal

## 1. Lettrage ING

Scan de départ : **95 lignes** non lettrées ING (14) + Belfius (36). Seuls les cas
corroborés sont traités — la communication structurée BE reste la clé maître.

| BSL | Date | Montant | Pièce | Clé |
|---|---|---|---|---|
| 20528 | 23/08 | +777,07 | INV/2026/03524 — Teroir de Magerotte | comm. structurée `000/0042/65572`, exact |
| 20488 | 20/08 | −2.299,22 | RESA1243 / FC26356017 — ING Equipment Lease | IBAN émetteur + montant exact, seule facture ouverte |

ING : **95 → 93 lignes**. Script : `compta/lettrage_26_ing_20260825.py`.

### Non traités — pièce ou arbitrage manquant

| Ligne | Montant | Blocage |
|---|---|---|
| ING 20381 Delhaize | +2.652,97 | avis `/ADV/2000058526` non fourni ; subset-sum sur 91 factures ouvertes = **18 combinaisons**, aucune unique |
| ING 19660 / 20373 ITM Alimentaire | +637,24 / +160,61 | partenaire inexistant (IBAN BE75 3701 0623 0851) ; paiements de la centrale Intermarché — exiger les avis 0000287398 / 0000290027 |
| ING 20522 Amazon Payments | +41,21 | settlement marketplace, pas un règlement client |
| ING 19625 Kirchner | −12.837,54 | 46 factures ouvertes, aucun subset unique — exiger l'avis de prélèvement |
| ING 19944 Proximus | −200,00 | aucune facture ouverte à ce montant → acompte ou facture non encodée |
| ING divers | — | Radius, Sendcloud, Google Cloud, Skeepers, CILE, Douanes : aucune facture d'achat ouverte, ce sont des charges directes à imputer |

Belfius (26 lignes) : hors périmètre de la demande, inchangé.

## 2. Facturation PRO — Peppol uniquement

Périmètre : `sale.order` `state=sale` / `invoice_status=to invoice`, hors teams B2C/web,
qty **livrées** uniquement, transport forcé.

**8 factures postées et transmises Peppol — 3.892,03 € TTC** (toutes en `processing`,
passage `done` sous 12 h par le cron #43).

| Facture | SO | Client | Montant | Compte de produit |
|---|---|---|---|---|
| INV/2026/03975 | S06236 | SRL Guchet Thunus — Au gré du vent | 957,70 | 700500 Revendeurs |
| INV/2026/03976 | S06237 | ORSA FUND SA | 89,10 | 700700 Institutions |
| INV/2026/03977 | S06235 | Smart fridges — Frigo Loco | 636,00 | 700300 Horeca |
| INV/2026/03978 | S06227 | La Vieille Demeure | 203,12 | 700300 Horeca |
| INV/2026/03979 | S06226 | JM Wines & Events | 539,29 | 700300 Horeca |
| INV/2026/03980 | S06221 | La Folle Epoque — Muriel Maron | 254,40 | 700300 Horeca |
| INV/2026/03981 | S06218 | Cocon Life store | 418,42 | 700500 Revendeurs |
| INV/2026/03982 | S06215 | Cafés Delahaut | 795,00 | 700300 Horeca |

La Folle Epoque était bloquée (EAS 9925) : fiche corrigée en 0208 → repassée `valid`, facturée.
**JM Wines & Events serait parti en 700000** sans la correction du point 3.

### Non facturées

- **Peppol non vérifiable → non facturées** (règle) : S06150 Jean-marie Houyon, S06136 Dragon Phenix — fiches sans n° d'entreprise (particuliers ; flux B2C, pas Peppol).
- **Rien de livré** : S06242 Cafés Antillia, S06234 Centrale Intermarché, S06228 Brasserie RN, S06222 Baaz & Co, S05815 Pharmacie Bia.

## 3. Classification canal (compte de résultats)

### Le mécanisme
Le canal du P&L vient du **compte de produit**, qui vient de la **position fiscale** :
FP 6 GMS → 700600 · FP 7 Horeca → 700300 · FP 8 Revendeurs → 700500 · FP 35 Institutions → 700700.
Sans FP canal, Odoo applique « Belgium B2B » qui ne mappe rien → le CA tombe en **700000**.
Aucune FP canal n'a de tax map : les poser est **sans impact TVA ni résultat**.

### Corrigé (`compta/fp_canal_rattrapage_20260825.py`)

- **47 fiches clients** ont reçu leur FP canal : 25 Horeca, 12 Revendeurs, 7 Institutions, 4 GMS.
  Garde-fous : un seul canal dans les tags, `is_company` **ou** TVA renseignée, et FP actuelle
  vide ou « Belgium B2B » — on n'écrase **jamais** une FP à enjeu TVA (Intra-Community, OSS).
- **7 commandes ouvertes** réalignées sur la FP de leur fiche : S00652 AD Rochefort → GMS,
  S06226 JM Wines → Horeca, S00730 La ferme du vieux Bure → Revendeurs, S00632 Cafermi →
  Revendeurs, S00722 HM25 → Horeca, S06234 Centrale Intermarché → GMS, S06228 Brasserie RN → Horeca.

Rollback : `compta/_rollback_fp_20260825.json`.

### La fuite réelle
Une SO encodée **avant** la correction de la fiche garde « Belgium B2B » et sa facture retombe
en 700000, même si le client est corrigé depuis. Vérifié : les dernières factures en 700000 sur
des clients GMS/Horeca viennent toutes de SO datées ≤ 19/08 au matin — le flux est propre en
amont depuis, il ne reste que la traîne. C'est pour ça que l'étape 2 (réalignement des SO) est
obligatoire à chaque passe.

### À arbitrer — 3 points

**a) Reclassement de l'historique 700000 → comptes canal** (présentation pure, résultat inchangé).
Non fait : écriture comptable = accord explicite requis.

| Exercice | CA en 700000 | dont GMS | dont Horeca | dont Revendeurs | dont Institutions | dont non identifié |
|---|---|---|---|---|---|---|
| FY25-26 | 730.519 | 273.213 | 247.863 | 172.368 | 13.978 | 23.097 |
| FY26-27 (2 mois) | 22.766 | 16.642 | −393 | 2.729 | — | 3.788 |

Sans ce reclassement, le P&L par canal FY25-26 n'est pas lisible dans Odoo.

**b) 16 fiches en conflit** — une FP canal est posée mais contredit les tags (ex. Deckers Nathalie
FP Horeca / tag Canal GMS ; INFRABEL FP Revendeurs / tag Institution ; NIJSKENS-Rochefrais
FP Revendeurs / tags Grossiste+HoReCA). Arbitrage métier, non touchées.

**c) 153 fiches de particuliers portent un tag canal** (132 en « Canal GMS ») — Geraldine/Coralie
Duchateau & co, paniers Shopify. Aucun impact P&L (pas de FP), mais ça pollue toute analyse
par tag — QBR, forecast, segments e-mail. À nettoyer.

Restent 26 partenaires sans tag ni FP avec du CA en 700000 sur FY26-27 (3.788 €) — plus gros :
Too Good To Go 1.215 €, Maison Muscari 420 €, Mayrine Toffoli 325 €. À classer à la main.

## Scripts

- `compta/scan_lettrage_20260825.py` · `compta/match_lettrage_20260825.py` (lecture seule)
- `compta/lettrage_26_ing_20260825.py` (`--apply`)
- `compta/fp_canal_rattrapage_20260825.py` (`--apply`)
- `scripts/facturation_b2b_peppol.py` (`--apply`)
