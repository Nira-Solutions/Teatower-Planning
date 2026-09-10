# Queue S38 — 14 au 18 septembre 2026

Vue Nicolas / agent. Ce fichier porte le raisonnement, jamais la page de Gilles.

## Contraintes de la semaine

| Contrainte | Traitement |
|---|---|
| Mercredi 16/09 : matinée seulement, retour base 11:30 | Journée réduite à 2 stops — dépôt Namur 09:15-09:35 + Hyper Wépion 09:50-10:15, retour 11:05 |
| Dépôts boutiques Liège, Namur, Rocourt (pas Waterloo) | Liège + Rocourt le mardi 15/09 (colis préparés lundi 14), Namur le mercredi 16/09 (colis préparé mardi 15). Aucun dépôt le lundi (REGLES §13) |

## Semaine générée — 28 stops

| Jour | Zone | Stops | Retour |
|---|---|---:|---|
| Lundi 14/09 | BW est → Nivelles → Sambre | 8 visites | 16:50 |
| Mardi 15/09 | Liège / Hesbaye | 5 visites + 2 dépôts | 15:30 |
| Mercredi 16/09 | Namur — demi-journée | 1 visite + 1 dépôt | 11:05 |
| Jeudi 17/09 | Hainaut → Sambre → Namur | 5 visites | 15:15 |
| Vendredi 18/09 | Baillonville → Liège sud → Vesdre | 6 visites | 15:25 |

## Écartés, et pourquoi

| Magasin | Retard | Motif |
|---|---|---|
| Intermarché Gerpinnes (#2971) | 10j | « Stop pour le moment, contact à reprendre » (Gilles, Slack 04/08) — à rouvrir par Jérôme avant toute visite |
| Proxy Delhaize Le Beau Rivage (#8779) | échéance 18/09 | Règle des 30j minimum : la visite tomberait à 29j. Reprogrammé en S39 |
| AD Jambes Materne (#5916) | 151j | Doublon d'adresse avec #113498, visité le 07/09 |
| AD Fernelmont (#5591) | 45j | Doublon d'adresse avec #2952, visité le 03/09 |
| Pharmacie Han-sur-Lesse (#3182) | 107j | Retirée du planning par Nicolas — **arbitrage à rendre** (voir ci-dessous) |
| Proxy Maransart (#113217) | 4j | Journée du lundi pleine ; passe en S39 |
| Delhaize Kraainem (#2914), CM Woluwe (#5825), Delhaize Boondael (#5426) | 4j | Cluster Bruxelles non rentable seul cette semaine ; à grouper en S39 |
| CM Hotton (#2979), CM Barvaux (#2811), Delhaize Barvaux (#119817) | 3j | Famenne, proche de la base : facile à caser en S39, cède la place aux 8j de la Vesdre |
| Hyper Arlon (#113746) | 10j | Pocket Luxembourg isolé ; couvert par la file télévente |

## Vendredi 11/09 — exclu du tirage (REGLES §10)

Les 8 magasins de la tournée d'aujourd'hui ne sont pas re-planifiés en S38 :
Villers-le-Bouillet, Hyper Herstal, Delhaize St Lambert, Longdoz Médiacité, Fragnée,
Embourg, Bois-de-Breux, Barchon. Ils apparaissent encore OVERDUE dans le pool du 11/09
parce que la tournée n'a pas encore laissé de trace.

⚠️ Le garde-fou de couverture, lancé sur la seule S38, voulait en basculer 5 en télévente.
Relancé sur S37+S38, il ne bascule plus rien. **Toujours laisser le garde-fou lire les deux
semaines** quand on génère un vendredi.

## Arbitrage attendu de Nicolas

**Pharmacie TILMAN Han-sur-Lesse (#3182)** — 197 jours sans visite, 18 €/mois, bloquée
en `FORCE_MERCH_PIDS`. Le garde-fou §14 ne peut pas trancher seul : soit elle repasse au
planning, soit elle sort de FORCE_MERCH pour aller en télévente, soit elle passe en
`[ARRET]`. Elle a déjà été retirée manuellement d'une tournée.

## Tags Odoo posés avant génération

13 tags `[VISITE]` depuis Slack #merchandiser (`scripts/slack_visites_vers_odoo_20260911.py`) :
7 passages du 07/09 et 6 du 08/09. Proxy Lillois exclu — il a généré S06332, sa trace est naturelle.

Deux fiches enrichies au passage : Spar Erezée `[REGLE: pas les lundis ni les mardis]`,
Delhaize Debroux `[REGLE: contrôle marchandise obligatoire]` + `[STOCK: pas de réserve]`.

## Télévente Vanessa — S38

45 magasins dus, capacité 30 appels (6/jour), 15 en overflow. Aucune bascule automatique
cette semaine. Delhaize Ath (#123144) est bien dans le pool Vanessa : la règle §14 est tenue.
