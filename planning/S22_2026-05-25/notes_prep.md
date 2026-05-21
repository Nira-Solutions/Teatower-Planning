# Notes préparation S22 (25-29 mai 2026)

> Pré-notes Nicolas avant génération du planning S22 — à intégrer lors du build.
> **État** : page S22 PAS encore publiée dans `index.html` (au 21/05). Build prévu après scan Displays Excel + pool Odoo + intégration ci-dessous.

---

## ⚠️ Lundi 25/05/2026 = JOUR FÉRIÉ — Lundi de Pentecôte (Belgique)

- **Pentecôte** : dimanche 24/05
- **Lundi de Pentecôte** : lundi 25/05 — **JOUR FÉRIÉ légal en Belgique**
- **Conséquence planning S22** : **PAS DE VISITE LUNDI 25/05** (aucun magasin GMS ouvert pour livraisons commerciales merch, et Gilles férié)
- Mettre bandeau visible `<span class="badge badge-ferie">JOUR FÉRIÉ — Lundi de Pentecôte</span>` en tête de la journée lundi
- **À reporter** : tout ce qui aurait normalement été planifié lundi → caser sur mar/mer/jeu/ven

**Mémoire associée** : `feedback_planning_jours_feries_be.md` — vérifier les jours fériés BE avant chaque build planning.

---

## Mardi 26/05 — passage Teatower Namur (10 min, dépôt commande) — EXCEPTION

- **Type** : STOP COURT — dépôt commande
- **Durée sur place** : 10 minutes (pas une vraie visite merch)
- **Lieu** : Boutique Teatower Namur (Rue du Pont 3, 5000 Namur)
- **Objet** : amener une commande
- **Insertion** : à caser sur l'axe Liège du mardi 26/05 (boucle Fragnée + Barchon + Herve + Fleron + retour via Namur) **OU** sur l'axe Namur si la boucle Liège ne passe pas Namur centre
- **Tag à afficher** : `EXCEPTION — dépôt commande (10 min)` — pour qu'on sache que ce stop déroge à la règle "pas de boutiques TT dans le planning"
- **Exception ponctuelle** : demande explicite Nicolas (20/05) — ne pas reproduire S23 sans nouvelle demande

---

## Mardi 26/05 — Delhaize Fragnée MAINTENU (Nicolas confirme 21/05)

- Maintenir Fragnée mardi 26/05 (info confirmée Nicolas 21/05).
- Caler dans la boucle Liège (Fragnée + Barchon + Herve + Fleron + ITM Spy + ITM Floriffoux + dépôt TT Namur).

---

## Mercredi 27/05 — Delhaize Bertrix dans la boucle Luxembourg

- **Source** : queue S21 v1 (`Planning_S21_v1_18-22_mai_2026.md`) — Bertrix était prévu ven 22/05 13:15 en Luxembourg, **retiré de S21 v3/v4** (S21 ven = Bxl/BW). Reporté S22.
- **Partner** : #123303 — Affilié 41092 - Delhaize Bertrix
- **Adresse** : Route des Gohineaux 2, 6880 Bertrix
- **Contact** : Mr Redouane (manager) — manager@delhaizebertrix.be — +32 61 41 27 36
- **Status** : nouveau client (IMPL faite S19 06/05 — SO S05489 680,44 €). **1ʳᵉ visite merch** post-IMPL.
- **Créneau cible** : 10:30 mercredi 27/05 dans la boucle Luxembourg
- **Compagnons de boucle** (cohérence géo) :
  - **CM Recogne** (zone Libramont/Bertrix)
  - **CM Bastogne CC Port** (#123189 — IMPL faite S19, post-implantation à valider sur place)
  - **AD Bastogne** (Tier A, #SA Marer)
  - éventuellement **CM Bouillon** RDV #425 (si caler)
- **Brief mail** : draft à conserver dans le brief jour (Nicolas demande explicitement "draft mail toujours présent" — appel téléphonique en pratique vu règle 07/05, mais brief texte conservé pour Gilles).
- **Règle 07/05** : pas de mail envoyé depuis Odoo, coordination par appel téléphonique. Le "draft mail" reste un brief écrit que Gilles peut adapter en appel.

---

## Reports S21 → S22 (rappel — depuis index.html ligne 1087)

- Carrefour Market Walcourt #9016 (Tier C, avg 87€) — retiré lundi S21 v2
- Delhaize Ottignies #3016 (Tier B, avg 530€ OVERDUE) — boucle BW
- Hyper Carrefour Fleron #7760 (Tier X) — axe Liège (mardi avec Fragnée)
- Intermarché Herve #120491 — axe Verviers / Liège Est (mardi)
- Delhaize Barchon #119815 — axe Liège Est (mardi avec Fragnée)
- **Intermarché Faimes #3210** (Tier B, 212€ avg, 65j OVERDUE) — retiré jeudi S21 v3 (cap horaire)
- ITM Spy #116686 / ITM Floriffoux #2958 (Namur ouest)
- **Delhaize Bertrix #123303** (cf section dédiée ci-dessus) — mercredi 27/05 boucle Luxembourg

## Demandes nouvelles (à ajouter à la queue)

### Delhaize Bouge #114681 — VISITE demandée par le client

| Champ | Valeur |
|---|---|
| **Partner** | **#114681 — Affilié 041345 - Delhaize de Bouge** |
| **Adresse** | Chaussée de Louvain 336, **5004 Namur (Bouge)** |
| **Tél** | +32 81 21 48 88 |
| **Email** | helene.nols@affiliatesdelhaize.be |
| **Parent** | Delhaize Le Lion S.A (affilié) |
| **Contacts magasin** | **Mme Destrée / Grandjean / Augustaine** |
| **Tier** | **B** — 8 SO confirmées, moyenne **447 € TTC** (mensuel régulier) |
| **Dernière SO** | S05448 du **2026-04-21** — 474,60 € |
| **Source demande** | Nicolas — message 2026-05-19 ("Delhaize Bouge souhaiterait une visite la semaine prochaine") |
| **Date écart** | ~34 jours depuis dernière SO au moment de S22 — cohérent cycle Tier B |
| **Géo** | Axe Namur centre / Hesbaye → cluster avec : ITM Bouge #3297 (proche), Floriffoux, Spy, Belgrade, Jambes, Profondeville |
| **Accessoires** | Magasin a A0271 Filtre boule + A0374 Filtre pince — Gilles peut en avoir en camionnette si besoin réassort |
| **À faire avant** | **Voir suivi avec Jérôme** — souhaite vendre coffrets découvertes ou horeca (note dans comment Odoo). Coordonner brief Gilles ↔ Jérôme avant visite. |

**Tag planning** : VISITE (30 min)
**Justification** : demande directe du magasin, Tier B régulier, écart cohérent.

---

## Magasins basculés APPEL ONLY (NE PLUS INTÉGRER au planning merch)

Décision Nicolas 20/05/2026 — magasins trop petits pour visite Gilles, réassort par téléphone depuis info@teatower.com :

| Partner | ID | Adresse | Tel |
|---|---|---|---|
| Carrefour Express Rhode-Saint-Genèse | #120933 | 1640 Rhode-Saint-Genèse | +32 2 466 68 41 |
| Carrefour Express CHIREC | #120762 | 1160 Auderghem | +32 2 280 40 49 |
| Proxy Delhaize Lillois | #114763 | 1428 Lillois | +32 2 384 48 83 |
| Proxy Delhaize Saint-Séverin | #113445 | 4550 Nandrin | +32 4 372 09 85 |

Tag `[APPEL ONLY — NE PAS VISITER — décision Nicolas 2026-05-20]` posé dans `res.partner.comment` Odoo pour chacun.

**À confirmer Nicolas** : "Carrefour Express Petits Champs" mentionné dans la demande — aucune correspondance trouvée dans Odoo (ni en nom, ni en rue). Vérifier l'orthographe exacte ou le partner_id.

---

## Checklist build S22

- [ ] Scanner Displays Excel (Actif + Prochaine Visite) AVANT toute génération queue
- [ ] Régénérer pool via `Teatower-Planning/scripts/build_planning_pool.py`
- [ ] Exclure tous les magasins visités S21 (revisite interdite — règle S(n-1))
- [ ] Exclure tous les magasins en statut `Arret` (col A Excel)
- [ ] Exclure les 4 magasins APPEL ONLY ci-dessus
- [ ] **Lundi 25/05 = férié** → 0 visite, bandeau visible
- [ ] **Mardi 26/05** : boucle Liège avec Fragnée + dépôt TT Namur 10 min
- [ ] **Mercredi 27/05** : boucle Luxembourg avec Bertrix 10:30 + Recogne + CM Bastogne CC Port + AD Bastogne
- [ ] Densifier jeu/ven pour absorber les reports lundi férié
- [ ] Vérifier cap 16:30 retour Baillonville pour chaque jour
- [ ] Pas de mail / pas de calendar.event (règle 07/05)
