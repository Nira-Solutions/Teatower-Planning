# Règles de planification merchandiser — Teatower

> Règles durables à **relire systématiquement** avant toute génération de planning ou tournée.

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

**Le merchandiser ne peut JAMAIS depasser l'horaire de fin : 16h30.**

### Application

1. Pour chaque journee, calculer l'heure de retour estimee a la base (Baillonville 5377) en additionnant :
   - l'heure de fin de la derniere visite/implantation
   - le temps de trajet retour vers Baillonville
2. Si le retour estime depasse 16h30, la derniere visite (ou l'avant-derniere si necessaire) doit etre :
   - deplacee a un autre jour de la meme semaine, OU
   - reportee a la semaine suivante
3. Lors de la generation du planning, **refuser** toute entree qui provoquerait un depassement — ne jamais inscrire une visite "sous reserve de validation".
4. Les implantations (duree longue, souvent 1h30) et les magasins eloignes de Baillonville (Enghien, Mons, Tournai, etc.) sont les premiers candidats au report si le timing est serre.

### Contexte

Regle instauree le 15/04/2026 suite au depassement prevu pour l'implantation Delhaize Enghien (S05413) le lundi 20/04 (retour estime 17h25, +55min). L'implantation a ete reportee a la semaine du 27/04.

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

## 5. Autres regles (rappel depuis la skill)

- **Base** : Zone d'activite Nord 33, 5377 Baillonville
- **Horaire** : 8h30 - 16h30 (retour obligatoire a 16h30)
- **Capacite** : 6 a 8 visites / jour (objectif maximisation), 30 min par visite
- **Hyper** : toujours le matin (avant 12h), jamais l'apres-midi
- **Exclusions Odoo permanentes** : "Delhaize Le Lion" et "Carrefour Belgium" (comptes centraux)
- **Remarques magasin** (champ `comment` Odoo) : contraintes jours/horaires obligatoires a respecter
- **Maximisation** : si un retour est prevu avant 14h30, ajouter des clients dans la zone jusqu'a la limite 16h30

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
