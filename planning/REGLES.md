# Règles de planification merchandiser — Teatower

> Règles durables à **relire systématiquement** avant toute génération de planning ou tournée.

---

## 1. Clients en statut "Arret" — EXCLUSION TOTALE

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

## 2. Autres règles (rappel depuis la skill)

- **Base** : Zone d'activité Nord 33, 5377 Baillonville
- **Horaire** : 8h30 – 16h30 (retour obligatoire à 16h30)
- **Capacité** : 5 à 6 visites / jour, 30 min par visite
- **Hyper** : toujours le matin (avant 12h), jamais l'après-midi
- **Exclusions Odoo permanentes** : "Delhaize Le Lion" et "Carrefour Belgium" (comptes centraux)
- **Remarques magasin** (champ `comment` Odoo) : contraintes jours/horaires obligatoires à respecter

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
