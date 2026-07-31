# Queue S32 — 03-07/08/2026 (vue Nicolas, pas le planning Gilles)

Généré le 30/07/2026 depuis `planning_pool_2026-07-30.csv` (100 actifs, 42 OVERDUE)
et `televente_pool_2026-07-30.csv` (58 magasins, 37 en retard).

- **Merch Gilles** : 30 visites sur 5 jours, 18 des 42 OVERDUE couverts.
- **Télévente Vanessa** : 30 appels sur 5 jours (6/j), 35 dus → 5 en overflow, 11 en winback.
- **Exclusivité** : garde-fou du builder OK, aucun magasin merch présent en télévente.
- **Fériés** : aucun cette semaine (le 15/08 tombe un samedi).

## OVERDUE non planifiés et pourquoi

| Retard | Magasin | Motif |
|---:|---|---|
| 133j | Proxy Delhaize Le Beau Rivage (#8779) | `[REGLE: 30j min]` — visité en S28, 27j seulement |
| 122j | Delhaize Wavre (#3226) | **NO-MERCH posé** — le client refuse le merchandiser |
| 108j | AD Jambes Materne (#5916) | visité S30, espacement 14j |
| 78j | Carrefour Market Marche (#3120) | visité S30 |
| 73j | Intermarché Floriffoux (#2958) | visité S28 **et** S30 |
| 64j | Hyper Carrefour Fleron (#7760) | `[REGLE: 30j min]` — 27j seulement |
| 41j | Proxy Delhaize Maransart (#113217) | visité S30 |
| 41j | Carrefour Market La Chasse (#59558) | visité S30 |
| 37j | Proxy Delhaize Bosvoorde (#5830) | visité S30 — **et doublon télévente, voir plus bas** |
| 35j | Delhaize Ottignies (#6838) | éligible (S28) — écarté, journée BW déjà à 6 stops → **réserve S33** |
| 34j | Delhaize Fragnée (#5580) | visité S31 (29/07) |
| 34j | Intermarché Spy (#116686) | éligible (S28) — écarté, journée Namur pleine → **réserve S33** |
| 28j | Intermarché Nivelles (#3153) | visité S30 |
| 28j | Delhaize Genval (#5582) | visité S31 (30/07) |
| 27j | Carrefour Market Hotton (#2979) | visité S30 |
| 27j | Delhaize Ciney/Rochefort/Neufchâteau/Bastogne (#7070) | **fiche sans adresse** — non planifiable, voir plus bas |
| 17j | Carrefour Market Barvaux (#2811) | visité S29, réserve |
| 17j | Delhaize Barvaux (#119817) | visité S29, réserve |
| 15j | Delhaize Boondael (#5426) | visité S30 |
| 13j | Delhaize Ath (#123144) | **110 km, isolé** — aucun autre stop en Hainaut cette semaine ; à grouper avec Mons / Enghien en S33 |
| 3j | AD Sombreffe (#5449) | visité S31 (27/07) |
| 2j | Intermarché Belgrade (#2821) | visité S31 (27/07) |
| 1j | Proxy Delhaize St Michel (#9461) | visité S31 (30/07) |
| 1j | Carrefour Market Uccle Bascule (#5484) | visité S31 (30/07) |

## Corrections Odoo posées le 30/07

- **#3226 Delhaize Wavre** → `[NO-MERCH 2026-07-30]`. Le `comment` disait déjà « le client ne veut pas
  de merchandiser, il préfère gérer son display lui-même », mais sans tag le magasin remontait en tête
  de file à 122j de retard à chaque génération. Le tag le sort du pool. Suivi commande uniquement.
- **#122991 Intermarché Anthée** → tag `[À IMPLANTER 2026-06-15]` clôturé en `[IMPLANTÉ …]`.
  L'implantation a bien eu lieu (SO S05737 du 05/06, livraison 08/06) et le magasin est passé en pool
  télévente. Le tag ouvert déclenchait une fausse alerte implantation à chaque planning.

## Anomalies de données à traiter

**Trois fuites d'exclusivité par fiche enfant.** Le pool traite certaines adresses de livraison comme
des magasins autonomes. Quand le parent est en télévente, la même boutique existe dans les deux pools :

| Fiche merch | Parent en télévente |
|---|---|
| #5830 (nom vide) | #3191 Proxy Delhaize Bosvoorde — SPRL BROOMCORNER |
| #124364 « Luana Stolfo » | #124363 Centrale Intermarché |
| #5752 (nom vide) | #2994 Intermarché Forest — FREYARVOR |

Aucune n'est dans le planning S32, donc pas d'incident cette semaine. Mais le garde-fou du builder
compare des `pid`, pas des magasins : il ne voit pas qu'un enfant et son parent sont le même point de
vente. À corriger dans `build_planning_pool.py` en remontant au `commercial_partner_id`.

**Dix fiches actives sans nom.** #5830, #6838 (Ottignies), #5580 (Fragnée), #5484 (Uccle Bascule),
#5878 (Remouchamps), #5750 (Assesse), #7693 (Rochefort), #5825 (Woluwe), #7679 (Ciney), #5752 (Forest).
Elles sortent en `store_name` vide dans le pool et en « ? » dans les listes. Deux conséquences : elles
sont invisibles à la sélection manuelle, et si elles atterrissent dans le planning, Gilles lit une ligne
sans nom de magasin.

**#7070 Delhaize Ciney / Rochefort / Neufchâteau / Bastogne** : ni rue, ni code postal, ni ville. C'est
une fiche de facturation groupée pour quatre magasins. 27j de retard mais impossible à router. La note
terrain de Nicolas du 02/07 dit « Delhaize Rochefort — contact Guisset », et il existe par ailleurs une
fiche #7693 « SA Marer - AD Rochefort » (sans nom, avg 257 €, 25 km) qui pourrait être le bon
interlocuteur. À arbitrer : soit compléter l'adresse de #7070, soit le basculer en fiche de facturation
pure et planifier #7693.

**Trois adresses sans code postal** corrigées à la main dans le planning : Delhaize Etalle (6740),
AD Fernelmont (5380), Delhaize Longdoz (4020). À renseigner dans Odoo, sinon le calcul de distance
retombe sur le nom de ville.

## Contrôle non mécanisable

**Congés annuels d'août.** La première semaine d'août est la plus risquée de l'année pour les affiliés
indépendants (Delhaize affiliés, AD, Spar). Je n'ai pas de moyen de lire les horaires Google de façon
fiable depuis ici, donc l'ouverture des 30 magasins n'est pas vérifiée. Les plus exposés sont les petits
affiliés : Etalle, Bertrix, Recogne, Bouffioulx, Fernelmont, Welkenraedt, Spa, Barchon, St-Séverin,
Ferrières. Vanessa passe ses appels lundi — le plus simple est qu'elle confirme l'ouverture des magasins
du mardi au vendredi au fil de ses appels, et que Gilles téléphone avant de partir sur les deux plus
longs déplacements (Arlon 79 km, Kraainem 81 km).
