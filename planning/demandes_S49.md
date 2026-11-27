# Demandes / contraintes pour la prep S49 (2026-11-30 → 2026-12-04)

> À scanner **obligatoirement** au début de la génération de la queue S49.

## Cadences

| Magasin | Demande | Contraintes |
|---|---|---|
| INTERMADIS SA - Intermarché Hannut #121874 (Rue de Hesbaye 1, 4280 Hannut) | **Passage toutes les 2 semaines** — demande du magasin relevée par Gilles le 19/11 (`[LOGISTIQUE 2026-11-19]`), validée par Nicolas le 19/11. Cadence 14 j posée dans `CADENCE_OVERRIDE_PID` + REGLES §5. Dernière visite le 19/11 (installation display) → **à placer en S49, cible jeu 03/12** (au plus tard ven 04/12). Ensuite S51 (~17/12), puis S53 (~31/12). | MATIN uniquement (le responsable n'est plus là l'après-midi), **jamais le mercredi**. Livraison 6h-13h. Contact : Ilanna (+32 19 51 20 06), sinon Mr Wereau, Benjamin ou Valentin. Stock à la réserve, réassort au GUN. |

> Prévisionnel à recaler : S49 ne contient pas Hannut pour l'instant ; S50 le place lun 07/12 (18 j, trop tard et redondant après un passage S49) → le retirer de S50 et le placer en S51 (pas le mer 16/12).

## Reportés du lundi 23/11 (S48) — cédés pour la livraison S06828 Carrefour Herstal

| Magasin | Contraintes |
|---|---|
| Carrefour Hyper Boncelles #60001 | Pas le mardi, arrivée avant 11:05 (7h-11h30) |
| FQMS - Proxy Delhaize Quadrilatère (Huy) #125351 | Pas le mardi, de préférence le mercredi |

## Cédés en S48 pour les dépôts boutiques par Gilles (Nicolas 20/11)

Aucun n'est dû selon les classes Pareto (§19) : à replacer seulement quand ils redeviennent dus.

| Magasin | Classe | Contraintes |
|---|---|---|
| Affilié 045190 - Proxy Delhaize Maransart #113217 | MEDIUM | Toujours demander avant de remplir, pas le lundi |
| Proxy Delhaize Rixensart #50967 | MEDIUM | — |
| Carrefour Market Angleur (Belle-Île) #121196 | LOW | — |
| Affilié 049480 - Delhaize Welkenraedt #59514 | MEDIUM | Pas le mercredi |
| Carrefour Market Lontzen #113675 | LOW | — |

## Reportés du mercredi 25/11 (S48) — cédés pour le RDV Carrefour Hyper Auderghem

| Magasin | Contraintes |
|---|---|
| Affilié 044471 - Delhaize Materne #113498 | Pas le mardi, 30 j minimum entre deux passages |
| Affilié 043366 - AD Fosses-la-Ville #5441 | Jamais le mardi (Tier A, déjà en retard) |

## Passages ratés / non faits remontés de Slack #merchandiser (import du 19/11)

| Magasin | Motif | Statut |
|---|---|---|
| Carrefour Market Braine-l'Alleud #8339 | « Pas fait ! À remettre au planning » (Gilles 18/11) | **à placer S49** (absent du prévisionnel) |
| Proxy Delhaize St Michel #9461 | Pas fait le 18/11 (même message) | prévu S50 jeu 10/12 — avancer en S49 si possible |
| Proxy Delhaize Ma Campagne #124701 | Responsable absent le 18/11 → urgence télévente 19/11 | prévu S50 jeu 10/12 |
| GIMALEX SA - Delhaize Fragnée #5580 | Responsable absent le 19/11 → urgence télévente 20/11 | prévu S51 mer 16/12 — avancer en S49 (pas le lundi) |
| SRL Spydis - Intermarché Spy #116686 | Cédé du ven 27/11 (boutique Waterloo en 2ème stop, REGLES §18) — reprise des glacés promise | **à placer S49** |

## Cédés de S48 pour les RDV Debroux (mar 24/11) et Ferme de la Princesse (ven 27/11) — ajoutés le 20/11

Annoncés « à replacer S49 » dans `demandes_S48.md`, mais absents de cette liste jusqu'ici.

| Magasin | Origine | Statut |
|---|---|---|
| Micamik SRL - Spar Godinne #122995 | Cédé mar 24/11 (changement display Debroux) | **à placer S49** |
| Antheco SA - Intermarché Anthée #122991 | Cédé mar 24/11 (changement display Debroux) | **à placer S49** |
| SRL AD LLN - Delhaize de Louvain-la-Neuve #3223 | Cédé ven 27/11 (échange display Ferme de la Princesse) | ✅ replacé S48 mar 24/11 15:00 (demande Nicolas 20/11) — livraison S06837 + display EM0107 |
| Dynamic Food SRL - Spar Louvain-la-Neuve #113216 | Cédé ven 27/11 (idem) | **à placer S49** |
| Spar Gembloux #123297 | Cédé ven 27/11 (idem) — passage mensuel demandé par le magasin | **à placer S49** |

## Classes Pareto (REGLES §19) — 1re semaine d'application

- AD Delhaize Fernelmont #2952 passe TOP (15 j) : dernière visite 13/11 → **à placer mar 01/12** (mar/ven ≥ 13:20 ; 18 j, sous la limite dure de 21 j).
- TOP et HIGH dus = jamais reportés : si la semaine déborde, céder un MEDIUM ou un LOW.

## Cédés de S48 pour l'Hyper Carrefour Bierges (mar 24/11) — ajoutés le 20/11

Bierges #8689 ajouté en 1er stop mar 24/11 (fenêtre mar/jeu 6h-11h45) : reprise glacés + anciens Noël, implantation coffrets Noël C0197 + C0198 (commande encodée par Nicolas), réassort. Cédés (classes les plus basses / les plus faciles à replacer près de la base) :

| Magasin | Classe | Dernière visite | Statut |
|---|---|---|---|
| Affilié 044780 - Proxy Delhaize Le Beau Rivage (Dinant) #8779 | LOW (90 j) | 29/09 | à placer S49-S50 (règle 30 j min OK) |
| 2u S.A. - Carrefour Market Ciney #2773 | MEDIUM (60 j) | 20/10 | à placer S49 (sinon garder le passage déjà prévu plus tard) |
| LSL RETAIL SPRL - Intermarché Chaumont-Gistoux #10134 | MEDIUM (60 j) | 20/10 | cédé pour Delhaize LLN (mar 24/11) — à placer S49 |

## Demandes du 20/11 (Nicolas)

- **BARVO S.A. - Carrefour Market Barvaux #2811** : ✅ placé **lun 30/11 08:55 (1er stop, matin)** — reprise des thés glacés + installation Noël si Nathalie Warnier valide (urgence télévente lun 23/11 pour confirmer). Pas la semaine S48 (décision Nicolas). Visite du lun 14/12 retirée (trop rapprochée).
  - Cédés du lun 30/11 pour tenir le retour 15:30 : Carrefour Market Grâce-Hollogne #113627 (MEDIUM, dernière 06/11) et Proxy Delhaize Tihange #124180 (LOW, dernière 05/11) — pas dus avant janvier/février, à replacer au fil des semaines.
- **D-trois SRL - Proxy Delhaize Saint-Séverin #113445** : **passé en télévente** (FORCE_TELEVENTE_PIDS, `build_televente_pool.py`) — plus de responsable sur place, refs absentes de la camionnette. Visite du lun 07/12 retirée. Urgence télévente lun 23/11 pour organiser la reprise des glacés + Noël.

## Recalage du ven 27/11 (Nicolas 27/11) — tournée changée sur le terrain

Tournée réelle du ven 27/11 : centrale Intermarché Gosselies → boutique Waterloo → **Intermarché Naninne #5755 → Delhaize Salzinnes #114704 → Delhaize Bouge #114681** (avancés du ven 04/12) → **boutique Teatower Namur**. Tag `[VISITE 2026-11-27 Gilles]` posé dans Odoo sur les 3 magasins.

| Magasin | Statut |
|---|---|
| Intermarché Naninne #5755, Delhaize Salzinnes #114704, Delhaize Bouge #114681 | ✅ visités le 27/11 → **retirés du ven 04/12** |
| NIVALIM - Intermarché Nivelles #3153 (HIGH) | non visité le 27/11 → ✅ **ven 04/12 12:12** |
| Gemblouxim - Intermarché Gembloux #123346 | non visité le 27/11 → ✅ **ven 04/12 13:36** (retiré du jeu 17/12, passage mensuel) |
| Spar Gembloux #123297 | ✅ **ven 04/12 14:06** |
| Carrefour Market Braine-l'Alleud #8339 | ✅ **ven 04/12 11:29** (à la place de Proxy Lillois, LOW pas dû) |
| SPRL Ferme de la Princesse - Traiteur Pistral #114857 (échange display EM0107 ×8 → EM0106 ×16) | non fait le 27/11 → **à placer S50** (cf. `demandes_S50.md`) |
| Carrefour Market Courcelles #124365 (reprise glacés) | non fait le 27/11 → **à placer S50** (cf. `demandes_S50.md`) |
| Affilié 043366 - AD Fosses-la-Ville #5441 (TOP) | ✅ **mer 02/12 13:10** |
| FQMS - Proxy Delhaize Quadrilatère (Huy) #125351 | ✅ **mer 02/12 11:24** |
| INTERMADIS SA - Intermarché Hannut #121874 (14 j) | ✅ **jeu 03/12 09:35 (1er stop, matin)** → Bierges passe 2ème stop 10:50 (fenêtre 11:45 OK) ; retiré du lun 07/12 |
| AD Spa, CM Lierneux, Spar Erezée (mer 02/12) · CM Waterloo, Proxy Bosvoorde (jeu 03/12) · Proxy Lillois (ven 04/12) | retirés : pas encore dus selon les classes Pareto (§19) |
| SRL Spydis - Intermarché Spy #116686 (HIGH, reprise glacés) | ✅ **mer 02/12 13:56** après Fosses (retour 15:11) — demande Nicolas 27/11 ; retiré du lun 21/12 |
