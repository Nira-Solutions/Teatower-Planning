# Règles de planification merchandiser — Teatower

> Règles durables à **relire systématiquement** avant toute génération de planning ou tournée.

---

## 0. Source maître Odoo — script `build_planning_pool.py` (REGLE DURE)

**Toute génération de queue ou de planning hebdomadaire DOIT commencer par l'exécution du script :**

```bash
python C:\Users\FlowUP\OneDrive\Teatower-Planning\scripts\build_planning_pool.py
```

Le script dérive en temps réel depuis Odoo la liste maître de tous les magasins GMS (Statut, Tier, last_visit, next_visit, retard) — sans dépendre du fichier Excel.

**Le fichier `Displays Teatower B2B.xlsx` est désormais en archive read-only.** Source unique = Odoo.

### Logique de dérivation (résumée — détail dans le script)

**Statut Actif/Arret :**
- Arret si `sale_warn=block` ET `[ARRET YYYY-MM-DD]` dans `res.partner.comment`
- Actif sinon

**Tier (cycle visite) :**
| Tier | avg_mois (12m) | Cycle |
|---|---|---|
| A | ≥ 400 € | 21 j |
| B | 100-400 € | 28 j |
| C | 30-100 € | 42 j |
| X | < 30 € | 90 j |

**Override nouveau client** : si `first_so_date >= today - 90j` ET `so_count >= 1` → minimum Tier B (cycle 28j). Évite qu'une 1ʳᵉ implantation soit classée X faute d'historique.

**last_visit_effective** = max(
- max(`stock.picking` outgoing done où `partner_shipping_id` = magasin),
- max(`[VISITE YYYY-MM-DD]` parsés dans `res.partner.comment`),
- max(`sale.order.date_order` confirmé)
)

**next_visit** = `last_visit_effective + cycle_days`

### Convention "visite sans réassort"

Nicolas signale en conversation "Gilles est passé à X le YYYY-MM-DD sans réassort". On patche `res.partner.comment` du magasin avec `[VISITE YYYY-MM-DD Gilles — sans réassort]`. Le script parse ces tags. Voir memory `feedback-planning-visites-sans-reassort`.

### Procédure

1. **Avant toute autre étape** : exécuter `build_planning_pool.py`. Sortie dans `data/planning_pool_<date>.{csv,md}`.
2. Lire en priorité la section OVERDUE du fichier markdown généré.
3. Confronter à : (a) exclusions ponctuelles (memory `project_*_no_visit_*`), (b) magasins confirmés visités S-1.
4. Logger dans `planning/LOG.md` le nb de candidats scannés ET intégrés à la queue.
5. **Si un Tier A ou B avec retard > 14j n'est pas intégré**, justifier explicitement le motif.

### Contexte

Règle instaurée le **2026-05-13** suite à l'omission **Delhaize Genval** (#5582, Tier B, cible 06/05, display quasi vide constaté Nicolas) : magasin jamais inscrit en queue S20 v1→v5. Investigation suite : **8 GMS implantés récemment** (Bertrix, Bièvre, Godinne, Manhay, Ath, Spar Namur NDB, Enghien, Hyper Ans) étaient absents du fichier Excel Displays, donc invisibles à toute génération de queue tant qu'on dépendait de ce fichier. Le script Odoo les récupère tous automatiquement. Plus aucun client GMS gagné par Jérôme ne peut tomber dans l'angle mort.

---

## 1. Devis non confirmés — JAMAIS dans le planning

**Règle dure** : un `sale.order` en état `draft` (devis) ou `sent` (devis envoyé) ne peut **pas** être la base d'une entrée de planning merchandiser (implantation, remplissage, visite).

- Seuls les **bons de commande confirmés** sont planifiables : `sale.order.state` ∈ { `sale`, `done` }.
- S'applique même si le devis contient des notes, commentaires ou un brief détaillé.
- **Raison** : un devis peut être annulé ou modifié. Planifier une implantation sur un devis fait perdre du temps au merchandiser si la commande ne se transforme pas en SO confirmée.

### Procédure

1. Avant d'ajouter une visite liée à un SO (queue ou planning hebdo) : **vérifier `state`** via XML-RPC.
   - `sale` / `done` → OK, planifiable.
   - `draft` / `sent` → **refuser l'entrée**, attendre confirmation du SO.
   - `cancel` → refuser et retirer toute entrée existante.
2. Si un devis se trouve dans une queue (`planning/queue_*.md`) ou dans le planning publié, **le retirer** et logger dans `planning/LOG.md`.
3. Une fois le devis confirmé (passage à `sale`), l'entrée peut être (re-)créée normalement.

---

## 2. Clients en statut "Arret" — EXCLUSION TOTALE

**Source officielle** : `C:\Users\FlowUP\Downloads\Claude\Claude\Teatower\Displays Teatower B2B (1).xlsx`

- Feuilles : `Displays TT GMS` et `Displays TT Revendeurs`
- **Colonne A = Statut**. Valeurs connues : `Actif`, `Arret`.
- **Tout client avec statut = "Arret" ne doit plus être :**
  - livré (sale_warn = block dans Odoo, bloque toute nouvelle SO)
  - visité par le merchandiser (ne jamais apparaître dans `planning/queue_*.md` ni dans un planning hebdomadaire)

### Procédure à chaque run de planification

1. **Première étape — TOUJOURS** : ouvrir le fichier Excel ci-dessus, extraire la liste des clients `Arret` (feuilles GMS + Revendeurs).
2. Construire un **set d'exclusion** (par nom de magasin **et** nom de société) et l'appliquer avant de tirer les candidats Odoo.
3. En complément, exclure côté Odoo tout partenaire avec `sale_warn = 'block'` contenant `[ARRET` dans le champ `comment`.
4. Si un client "Arret" apparaît malgré tout dans une file `planning/queue_*.md`, **le retirer** et logger dans `planning/LOG.md`.

### Maintenance

- Quand Nicolas signale un nouvel arrêt, mettre à jour :
  - le fichier Excel (Statut → `Arret` + motif dans `Remarques`)
  - la fiche Odoo : `comment` (préfixe `[ARRET YYYY-MM-DD]`), `sale_warn = 'block'`, `sale_warn_msg`
  - les opportunités CRM ouvertes : **ne pas les toucher** (décision de Nicolas au cas par cas)

### Dernière synchro effectuée

- **2026-04-15** : 24 clients "Arret" extraits, 20 fiches Odoo mises à jour (comment + sale_warn), 4 non trouvés dans Odoo (AD Leuze 044908, Intermarché Farcienne INTERFAR, Intermarché Genval ULTRA FRAIS, Intermarché Rixensart Rixalilm). 0 opportunité CRM ouverte sur ces 20 partenaires.

---

## 3. JAMAIS de depassement horaire (REGLE DURE)

**Fenetre journee Gilles : 08:30 -> 17:00 (8h de travail + 30 min de pause = 8h30 total). JAMAIS depassee.**

### Application

1. Depart Baillonville : jamais avant **08:30**. Pause dejeuner : **30 min exactement**.
2. Pour chaque journee, calculer l'heure de retour estimee a la base (Baillonville 5377) en additionnant :
   - l'heure de fin de la derniere visite/implantation
   - le temps de trajet retour vers Baillonville
3. Si le retour estime depasse **17:00**, la derniere visite (ou l'avant-derniere si necessaire) doit etre :
   - deplacee a un autre jour de la meme semaine, OU
   - reportee a la semaine suivante
4. Lors de la generation du planning, **refuser** toute entree qui provoquerait un depassement — ne jamais inscrire une visite "sous reserve de validation".
5. Les implantations et les magasins eloignes de Baillonville (Enghien, Mons, Tournai, etc.) sont les premiers candidats au report si le timing est serre.
6. Afficher l'heure de retour de chaque jour avec mention « OK <=17:00 » dans le rendu.

### Contexte

Regle instauree le 15/04/2026 suite au depassement prevu pour l'implantation Delhaize Enghien (S05413) le lundi 20/04 (retour estime 17h25, +55min). L'implantation a ete reportee a la semaine du 27/04.

Historique plafond : 16h30 -> 16h45 (2026-05-29, Nicolas) -> **fenetre 08:30-17:00** (2026-06-04, Nicolas : « l'horaire de Gilles doit etre 8h + 30 minutes de pause donc 8h30. Donc 8h30 - 17h00. Il ne peut JAMAIS etre depasse »).

---

## 4. Responsable/contact absent — NE PAS planifier ce jour-la (REGLE DURE)

**Si le responsable ou contact cle d'un magasin est absent un jour donne, il est INTERDIT de planifier la visite ce jour-la.**

### Principe

Le merchandiser doit pouvoir interagir avec le responsable rayon ou le gerant pour :
- faire signer la reception du remplissage
- discuter de la commande suivante
- signaler des problemes (peremptions, produits manquants, facing)
- obtenir l'acces aux reserves si necessaire

Sans le responsable, la visite perd 50 a 80 % de sa valeur. Le merchandiser fait du remplissage "a l'aveugle" sans feedback ni possibilite de commande.

### Application

1. **Avant de planifier** : verifier le champ `comment` (Notes internes) de la fiche partenaire Odoo. Les contraintes connues sont du type :
   - "pas de passage le mercredi responsable absent"
   - "pas le jeudi car le responsable rayon n'est pas la"
   - "Monsieur Garnier absent les mercredis"
   - "Madame Galletas pas presente le jeudi"
2. **Si le contact est absent le jour prevu** : deplacer la visite a un autre jour de la semaine ou reporter a la semaine suivante.
3. **Exceptions** : si le magasin a un contact secondaire present ce jour-la (ex: Delhaize Ottignies — Mme Galletas absente jeudi mais Jolan Cailleu present), la visite est autorisee avec le contact secondaire.

### Contraintes connues au 2026-04-16

| Magasin | Contrainte | Source |
|---|---|---|
| Proxy Delhaize Ferrieres | Responsable absent le mercredi | Odoo comment |
| AD Soumagne | Mr Garnier absent les mercredis | Odoo comment |
| Delhaize Ottignies | Mme Galletas absente le jeudi (mais Jolan Cailleu present) | Odoo comment |
| CM Remouchamps | Responsable rayon absent le jeudi | Odoo comment |
| Proxy Delhaize Linthout | Pas de visite le mercredi | Odoo comment |
| CM Butgenbach | Pas de visite le mercredi | Odoo comment |
| AD Fosses-la-Ville | Pas de visite le mardi. Preference mercredi (Leslie presente toute la journee) | Odoo comment |
| Delhaize Barchon | Ferme le lundi matin, ouvre a midi | Odoo comment |
| ITM Anhee | Jamais le lundi, visite le matin | Odoo comment |
| ITM Hamoir | Pas mardi apres-midi ni mercredi | Odoo comment |
| CM Hannut (P.R.MACLEKY) | Visite uniquement le jeudi | Odoo comment |
| Delhaize Fragnee | Pas de visite le lundi | Odoo comment |
| Hyper Boncelles | Pas le mardi. Horaire 7h-11h30 | Odoo comment |
| ITM Villers-le-Bouillet | Mercredi ou vendredi matin | Odoo comment |
| CM Etterbeek Cinquantenaire | Ne souhaite PAS de suivi merchandiser | Odoo comment — EXCLU |
| Delhaize LLN | Mr Snaps absent le jeudi | Odoo comment |

### Historique

- **2026-04-16** : regle creee suite au bug planning S20 v3 (Proxy Ferrieres planifie mercredi malgre responsable absent). Corrige en v4 (deplace au jeudi).

---

## 5. Cadences specifiques (overrides par magasin)

**Certains magasins ont une cadence de visite override, differente de leur Tier par defaut.**

| Magasin | Odoo ID | Tier | Cadence par defaut | Cadence override | Source |
|---|---|---|---|---|---|
| Distriparenthese - Intermarche Gosselies (6041) | 2927 | C | 50j (Tier C) | **28j (4 semaines)** | Nicolas 2026-04-20 |
| Lambertdis SRL - Spar Manhay (televente) | 122944 | B | 28j | **25j** (espacer les reassorts) | Nicolas 2026-06-10 |

### Application

Lors de la generation du planning, si un magasin figure dans ce tableau, utiliser la cadence override au lieu de `max_days` du Tier. Un magasin est OVERDUE uniquement si `days_since_last > cadence_override`.

**IMPLEMENTE (2026-06-10)** : les overrides sont desormais codes dans les scripts
(`CADENCE_OVERRIDE_PID`) — `build_planning_pool.py` (merch) ET `build_televente_pool.py`
(televente, ou loge Spar Manhay). Pour ajouter un override, editer le dict par pid.

---

## 6. Autres regles (rappel depuis la skill)

- **Base** : Zone d'activite Nord 33, 5377 Baillonville
- **Horaire** : 08:30 - 17:00 (8h travail + 30 min pause — regle 04/06/2026, cf. §3)
- **Capacite** : 6 a 8 visites / jour (objectif maximisation), 25 min par visite/implantation
- **Hyper** : toujours le matin (avant 12h), jamais l'apres-midi
- **Exclusions Odoo permanentes** : "Delhaize Le Lion" et "Carrefour Belgium" (comptes centraux)
- **Remarques magasin** (champ `comment` Odoo) : contraintes jours/horaires obligatoires a respecter
- **Maximisation** : si un retour est prevu avant 14h30, ajouter des clients dans la zone jusqu'a la limite 17:00

---

## 7. Champs terrain merchandiser — CONTROLE STOCK / METHODE REASSORT / REGLE MAGASIN (REGLE DURE, 2026-06-10)

**Chaque magasin peut porter 3 infos terrain affichees sous lui dans la tournee. Source = tags dans `res.partner.comment` Odoo** (jamais un fichier separe). Le pool les parse (`build_planning_pool.py`), le rendu les affiche.

| Champ planning | Tag Odoo (dans `comment`) | Sens |
|---|---|---|
| **CONTROLE STOCK** | `[STOCK: reserve]` (ou `[STOCK: ailleurs ...]`) | Ou controler le stock AVANT remplissage (s'il y a du stock en reserve) |
| **METHODE REASSORT** | `[REASSORT: GUN]` (ou `manuel`, `bon papier`, ...) | Methode de remplissage attendue en magasin |
| **REGLE MAGASIN** | `[REGLE: etiquettes sur produits + antivol]` | Regle specifique magasin (etiquetage, antivol, acces reserve, ...) |

### Application

1. Un champ ne s'affiche **que s'il est renseigne** pour le magasin. **Pas de valeur par defaut** (pas de "GUN" automatique — Nicolas 10/06/2026).
2. Pour renseigner : ajouter le tag dans le champ Notes internes (`comment`) de la fiche Odoo. Plusieurs tags cohabitent avec `[VISITE]`, `[ARRET]`, `[IMPL]`, `[NO-MERCH]`.
3. Ces 3 champs **remplacent** les anciennes "notes / brief" verbeuses sous chaque magasin (cf. §8).

---

## 8. Format du planning — EPURE pour le merchandiser (REGLE DURE, 2026-06-10)

**Le planning publie est l'outil de terrain de Gilles. Il doit etre LISIBLE, pas un rapport.**

### Ce qu'on RETIRE

- **Le gros recap / la "reflexion" en haut** de chaque semaine (cartes de synthese Visites/Jours/Implantations/km, blocs `.alert` explicatifs de version, justifications de deplacement). Le merchandiser n'a pas besoin du raisonnement de l'agent.
- **Les notes/brief verbeux apres l'adresse** de chaque magasin (anciens `Brief : ...`, dump du `comment` Odoo).

### Ce qu'on GARDE — ligne magasin epuree

Sous chaque magasin, dans cet ordre, uniquement :
1. **Adresse**
2. **Contact** (regle "contacts visibles" — extrait du `comment` / contacts enfants, non tronque)
3. **CONTROLE STOCK** — si renseigne (§7)
4. **METHODE REASSORT** — si renseigne (§7)
5. **REGLE MAGASIN** — si renseigne (§7)
6. **Trajet Google Maps** (lien) — toujours

Le bandeau d'en-tete jour minimal (date, nb de stops, zone, heure de retour `OK <=17:00`) reste autorise : c'est operationnel, pas de la "reflexion".

---

## 9. Implantations — premiers stops + maximum 3/jour (REGLE DURE, 2026-06-10)

1. **Les implantations sont planifiees en PREMIERS stops de la journee.** Le materiel d'implantation (display, stock de lancement) charge dans la camionnette bloque la place pour le reste : il faut le sortir en premier. Une implantation tardive = camionnette bloquee toute la journee.
2. **Maximum 3 implantations par jour.** Au-dela, pas assez de place dans la camionnette pour charger tout le materiel + le reassort des autres visites.
3. Si un jour cumule >3 implantations candidates, en reporter a un autre jour de la semaine ou a S+1.
4. Combine avec §3 (horaire) : les implantations restent les premieres candidates au report si le timing serre (une implantation = plus longue qu'une visite).

---

## 10. Planning genere en cours de semaine — visites a venir NON faites (REGLE DURE renforcee, 2026-06-10)

**Quand on genere un planning (ex. le jeudi pour S+1), les visites deja planifiees mais PAS ENCORE EXECUTEES de la semaine courante (vendredi, voire le jour meme) ne doivent PAS etre traitees comme faites.**

1. Avant de tirer les candidats S+1, scanner les jours **restants** (non executes) de la semaine courante S(n) et **exclure leurs magasins** du nouveau planning (pas de doublon).
2. Ne jamais considerer un magasin "a jour" sur la seule base qu'il figure dans un planning futur : la source de "derniere visite" reste la derniere SO Odoo + tags `[VISITE]` (cf. §0), jamais un planning .md/.html.
3. Inversement, ne pas re-planifier en S+1 un magasin du vendredi S(n) en pensant qu'il est "en retard" : il va etre fait vendredi.

### Contexte

Regle initiale 28/05/2026 (incident doublon jour restant). Durcie le 10/06/2026 (Nicolas : "planning genere jeudi, bien faire attention que les visites du vendredi ne sont pas faites, pas toujours respecte").

---

## 11. Force merch — gros clients gardes pour Gilles (2026-06-10)

Certains gros clients que la regle de segmentation televente (refs<=10 OU dist>60km & refs<20) enverrait a tort chez Vanessa restent suivis **physiquement par Gilles**. Codes dans `build_televente_pool.py` (`FORCE_MERCH_PIDS` / `FORCE_MERCH_TOKENS`) — exclus du pool televente, donc presents en merch.

| Magasin | Odoo ID | Raison |
|---|---|---|
| KAIO Retail invest - Delhaize Ottignies | 3016 / 5649 / 6838 | Gros client, juste au-dela du seuil distance (Nicolas 10/06/2026) |
| Affilie 044725 - Delhaize Kraainem | 2914 | Gros client garde en merch (Nicolas 10/06/2026) |

---

## Liste complète des clients "Arret" au 2026-04-15

| Magasin | Société | Odoo ID | Motif |
|---|---|---|---|
| AD Leuze | Affilié 044908 - AD Leuze-Eghezée | NON TROUVÉ | Stop pour l'instant car pas assez de vente |
| AL DISTRIBUTION - Intermarché Monnaie | idem | 2776 | — |
| Carrefour market - Genval | idem | 7006 | Pas commandé depuis Avril 2025 |
| Carrefour Market Bertrix | Carrefour Market Bertrix SRL | 7883 | Plus de passage avant retour client |
| Delhaize Alsemberg | Affilié 040270 | 5427 | — |
| Delhaize Fort Jaco (Uccle) | Affilié 043185 AD Fort Jaco | 5446 | — |
| Delhaize Haccourt | DelHaccourt SRL | 2910 | Mme Daniels refuse le display (trop cher, bcp de perte) |
| Delhaize Hankar | Affilié 043870 | 5686 | Ne continue pas la collaboration |
| Delhaize LEOPOLD III | Affilié 044765 | 5772 | — |
| Delhaize Mozart | Affilié 045630 | 5543 | Commande annulée, pas assez de place. Client à relancer |
| Delhaize Braine l'Alleud | Affilié 041395 | 5645 | Stand by — Coraline/Romain souhaitent être contactés |
| Delhaize De Fré | Affilié 042405 | 5539 | Client évalue s'il continue (contact Mme Turk avant prochain passage) |
| Delhaize Waterloo | Affilié 049385 | 5573 | Baisse de vente depuis ouverture Waterloo ; pense arrêter |
| Intermarché Couillet | Coudis SA | 2850 | Arrête — plus de vol que de vente |
| Intermarché Eghezee | SA MOFER | 3213 | Stop — réorg, trop de fournisseurs. Relancer à l'arrivée thés glacés |
| Intermarché Farcienne | INTERFAR | NON TROUVÉ | Magasin fermé définitivement en janvier 2025 |
| Intermarché Genval | S.A. ULTRA FRAIS | NON TROUVÉ | — |
| Intermarché Gozée | CAP GOZEE | 2845 | Plus intéressé par la gamme. Client perdu |
| Intermarché Lambusart | SA LAMBUSIM | 3212 | Plus intéressé. Client perdu |
| Intermarché Rixensart | Rixalilm | NON TROUVÉ | — |
| Intermarché Bois de Villers | DISESM SA | 2923 | Mail 23/01/2026 — arrêt collab |
| Intermarché  Braine l'alleud | Magbraine.SA | 3116 | Nouveau gérant, Jérôme doit reprendre contact avant prochaine visite |
| Intermarché Andenne | Distrifresh SRL | 2925 | Nouveau gérant ; magasin stop la gamme TT |
| Intermarché Uccle | VDK FOOD RETAIL | 116724 | Voudrait qu'on reprenne la marchandise ; suivi Jérôme avant prochaine visite |
