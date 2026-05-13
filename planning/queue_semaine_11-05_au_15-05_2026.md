# Planning semaine du 11 au 15 mai 2026 (S20) — v1 PUBLIÉ

> Créée le 29/04/2026, validée Nicolas le 04/05 (3 décisions) et publiée. Merchandiser : Gilles | Base : Baillonville (5377) | Horaire : 08h30 - 16h30.

---

## 🔴 OMISSION DÉTECTÉE 13/05 — Delhaize Genval

**Constat Nicolas 13/05** : display **Delhaize Genval (Affilié 043540 — Av. Albert 1er 13, 1332 La Hulpe — Gilles Verleyen 026 54 17 02)** quasi vide. Magasin **jamais inscrit en queue S20 (v1→v5)**.

**Pourquoi raté** : aucune des 5 versions du planning n'a effectué le scan exhaustif du `Displays Teatower B2B.xlsx` filtré sur `Statut=Actif AND Prochaine Visite ≤ vendredi_S20`. Les versions ont été construites sur (a) SO confirmés à livrer, (b) reports S-1, (c) demandes ponctuelles Nicolas/Jérôme, (d) audits Odoo ciblés SO récentes. **Le Displays n'a jamais été utilisé comme source maître.**

**Aggravation** : mardi 12/05 (Bxl Sud-Est v5), Gilles a fait **Proxy Rixensart 13:45-14:15** — soit à **5 km de Delhaize Genval**, sur le même axe. Avec 30 min de marge, le détour aurait coûté ~15 min aller-retour. Le magasin a été manqué de très près.

**Fiche Displays B2B au 13/05** :
- Statut **Actif** | Tier **B** | Cycle **28 jours**
- Dernière visite **2026-04-08** | Prochaine visite cible **2026-05-06** (retard 7j)
- CA cumulé **5 307 €** depuis 06/2024 | Avg **279 €/mois**
- Mise en place : **None** dans Displays (à valider sur place — display M0005 ? rayon ?)
- Contact : Gilles Verleyen — gilles.verleyen@delhaize-genval.be — 026 54 17 02

**Décision** : S20 trop avancée (mercredi en cours, jeudi+vendredi déjà bookés Gosselies/Gembloux + Famenne/BLC). **Reporté en TÊTE de S21** (18-22/05), jour BW Est dédié. Appel téléphonique Gilles Verleyen aujourd'hui pour : (1) lui expliquer le retard, (2) noter le besoin réassort exact, (3) caler RDV S21.

**Correctif méthodo durable** :
- Règle dure **§0** ajoutée à `planning/REGLES.md` : scan Displays exhaustif obligatoire avant toute génération de queue.
- Script reproductible : `data/_scan_overdue_s20.py`.
- Mémoire : `feedback_planning_scan_displays_obligatoire.md`.

---

## Validations Nicolas du 04/05

1. **Circuit Bxl Sud-Est mardi 12/05** : Boondael (Delhaize, réorga + thés glacés, contact Mr Daniel) → Bosvoorde → Debroux Auderghem → Rixensart, retour Baillonville 15:45.
2. **Alivim Gilson + Gembloux jeudi 14/05** : Nicolas pensait 2 magasins distincts ; Odoo confirme **un seul partner = Alivim SRL #123294 (Spar Gembloux Pascal Gilson)**, Chaussée de Namur 52, 5030 Gembloux. Donc 1ʳᵉ implantation Spar Gembloux Alivim. **AD Delhaize Gembloux #2913** ajouté en visite l'après-midi (2 SO récentes 28/04 + 30/04 confirmées, sur la zone, 2 min en voiture).
3. **Hyper Carrefour Gosselies #122466** : ajouté **jeudi 14/05 matin** (Hyper = matin obligatoire, contact Vincent ou Benjamin, 8h-12h). SO ref S05332 du 03/04 (688,94 €) confirmée sale — visite remplissage zone Hainaut. Lundi 11/05 (Lontzen) opposé géographique, mardi (Bxl Sud-Est) opposé. Mercredi (Namur-Sud) possible mais Materne II Jambes prioritaire 09:00. Jeudi route logique Gosselies → Gembloux (24 min E42) → AD Gembloux (2 min) → retour Baillonville. **Bomerée laissé en suspens** : Nicolas n'a validé QUE Gosselies, pas Bomerée. Bomerée non casable jeudi sans dépasser 16h30 (Gosselies+Bomerée+Alivim+AD = trop long).

---

## Lundi 11/05 — Liège-Est / Cantons (Lontzen)

| Heure | Magasin | Adresse | Contact magasin | Tel | Type | Brief |
|---|---|---|---|---|---|---|
| 09:35-10:15 | **Carrefour market LONTZEN** (#113675) | Rue Mitoyenne B 910, 4710 Lontzen | **Virginie ou Benjamin** | 087 67 42 27 | Visite | Demande Nicolas 29/04 (avancée du 05/06). Tier C, dernière visite 10/04. Panier moyen ~580 € HT. CM (pas Hyper) → pas de contrainte horaire stricte. Mail magasin : carrefour.lontzen@gmail.com |

**Trajet** : Baillonville → Lontzen 1h05 / 75 km via E25 + E40 → arrivée 09:35 → visite 09:35-10:15 → retour 10:15+1h05 = 11:20. **Journée très light** — opportunité de densifier avec autres GMS Liège-Est si OVERDUE (à scanner avant lundi : Spa, Verviers, Welkenraedt, Eupen).

[Google Maps Baillonville → Lontzen → Baillonville](https://www.google.com/maps/dir/5377+Baillonville/Rue+Mitoyenne+B+910+4710+Lontzen/5377+Baillonville)

**Pas d'IMPLANTATION** = pas de mail (règle §10).

---

## Mardi 12/05 — Bruxelles Sud-Est / BW (validation Nicolas 04/05) — 4 visites

| Heure | Magasin | Adresse | Contact magasin | Tel | Type | Brief |
|---|---|---|---|---|---|---|
| 10:00-10:30 | **Delhaize Boondael** (AL RETAIL #2777, ship #5426) | Av. du Bois de la Cambre 120, 1050 Ixelles | **Mr Daniel** (info Nicolas 04/05) — appel matin Gilles à 9h00 | 02 672 89 48 | Visite + thés glacés | **Réorga + placement thés glacés**. Note Odoo : panier tourniquet (ancien sujet Jérôme). 5 SO confirmées 2025-2026 (last S04716 12/01/26 495,64 €). Backup : François Korosmezey (merchandiser interne) si Mr Daniel pas joignable. Mail magasin : 014024@delhaize.be. |
| 11:15-11:45 | **Proxy Delhaize Bosvoorde** (SPRL BROOMCORNER #3191) | Chaussée de la Hulpe 255, 1170 Watermael-Boitsfort | **Youssef, Mélissa ou Saïd** | 02 672 33 99 | Visite | "Ok suivi Merchandiser une fois par mois" (note Odoo). Mail : Youbech.mesli@gmail.com |
| 12:30-13:00 | **Delhaize Herman DEBROUX Auderghem** (Affilié 044010 #5729) | Av. Hermann Debroux 26, 1160 Auderghem | **à demander sur place** (responsable rayon) | 02 672 87 25 | Visite | Tier B. Mail : Naberkan@delhaize.be. Déjeuner court sur trajet Bosvoorde → Debroux. |
| 13:45-14:15 | **Proxy Delhaize Rixensart** (Affilié 046900 #50967) | Place du Beau Site 4, 1330 Rixensart | **Lara ou Fabienne** (merchandiser) | 02 653 71 18 | Visite | Note Odoo confirmée. Mail : bd.proxyrixensart@gmail.com |

**Route OSRM** :
- Baillonville → Boondael : 79 min / 104 km (départ 08:30 → arrivée 09:50, marge 10 min appel téléphonique 9h)
- Boondael → Bosvoorde : 6 min / 2,1 km
- Bosvoorde → Debroux : 9 min / 4,1 km
- Debroux → Rixensart : 18 min / 16,5 km
- Rixensart → Baillonville : 69 min / 91 km
- **Retour Baillonville ~15:24** (vs 15:45 annoncé — marge 21 min)

[Google Maps tournée complète](https://www.google.com/maps/dir/5377+Baillonville/Avenue+du+Bois+de+la+Cambre+120+1050+Ixelles/Chauss%C3%A9e+de+la+Hulpe+255+1170+Watermael-Boitsfort/Avenue+Hermann+Debroux+26+1160+Auderghem/Place+du+Beau+Site+4+1330+Rixensart/5377+Baillonville)

**Pas d'IMPLANTATION** = pas de mail (règle §10). Boondael : appel téléphonique préalable matin 9h00 par Gilles (à tracer dans brief).

⚠️ **Vérification Arret** : tous les 4 magasins = `Actif` dans `Displays Teatower B2B.xlsx`. Seul "Intermarché Rixensart Rixalilm" est en Arret — c'est un AUTRE magasin (Intermarché, pas Proxy Delhaize) que nous N'AJOUTONS PAS.

---

## Mercredi 13/05 — Namur-Sud / Jambes (reports S19) — 4 visites

| Heure | Magasin | Adresse | Contact magasin | Tel | Type | Brief |
|---|---|---|---|---|---|---|
| 09:00-09:30 | **AD Delhaize Materne II Jambes** (#113498) | Av. Bourgmestre Jean Materne 109, 5100 Namur | **Elise Stroobants** (ou Angélique / Mme Strobant) | +32 81 30 16 88 | Visite + livraison thés glacés + reprise Guarana Boost | **Demande mail magasin 29/04** : (1) livrer thés glacés, (2) remettre en rayon Lady Dodo + Paniers Grand-Maman, (3) reprendre la réf Guarana Boost (note Odoo "ne marche pas bien"). PAS le mardi. Mail : info@gecodis.be. |
| 10:15-10:45 | **AD Delhaize Fosses-la-Ville** (#5441) | Rue du Cimetière 5, 5070 Fosses-la-Ville | **Leslie** (responsable, présente toute la journée mercredi) | — | Visite + thés glacés | Consigne Nicolas note Odoo 20/04 : revisite thés glacés. Mercredi obligatoire (Leslie présente). |
| 12:00-12:30 | **Boutique Teatower Namur centre** | Rue du Pont 3, 5000 Namur | — | — | Stop boutique TT | 30 min — check stock + remontée terrain. Déjeuner rapide sur place ou en route. |
| 13:30-14:00 | **Carrefour Express Profondeville** | 5170 Profondeville | **à demander sur place** | — | Visite | Remplissage zone 5xxx. Sur route retour. |

**Route** : Baillonville → Materne II Jambes (35 min / 30 km via N4) → Fosses-la-Ville (30 min via N922 + N922a) → Boutique Namur Rue du Pont (25 min via Pont des Ardennes) → Profondeville (25 min via N947) → retour Baillonville (45 min via N4) → ~14:45.

[Google Maps tournée complète](https://www.google.com/maps/dir/5377+Baillonville/Avenue+du+Bourgmestre+Jean+Materne+109+5100+Namur/Rue+du+Cimeti%C3%A8re+5+5070+Fosses-la-Ville/Rue+du+Pont+3+5000+Namur/5170+Profondeville/5377+Baillonville)

**Camionnette** : prévoir ramener la réf **Guarana Boost** depuis Materne II Jambes (reprise commande magasin).

**CM Bouillon RDV #425** : pas casable mercredi (Lux trop loin de Namur-Sud), à statuer S21.

**Pas d'IMPLANTATION** = pas de mail (règle §10).

---

## Jeudi 14/05 — Hainaut + Gembloux (validation Nicolas 04/05) — 1 visite Hyper + 1 IMPLANTATION + 1 visite

| Heure | Magasin | Adresse | Contact magasin | Tel | Type | Brief |
|---|---|---|---|---|---|---|
| 09:35-10:35 | **Hyper Carrefour Gosselies** (#122466) | Da Vincilaan 3, 6041 Gosselies | **Vincent** ou **Benjamin** | +32 71 25 06 11 | Visite Hyper (matin obligatoire) | Note Odoo : "Ok pour le suivi merchandiser demander Vincent ou Benjamin. Passage de 8h à 12h". SO S05332 03/04 (688,94 €) confirmée sale. 1ʳᵉ visite merchandiser cette zone. Pas d'email partner connu — pas de mail (règle §10 + email manquant). |
| 11:30-13:00 | **Alivim SRL — Spar Gembloux** (#123294, ship #123297 Pascal Gilson) | Chaussée de Namur 52, 5030 Gembloux | **Pascal Gilson** (gérant) | +32 81 61 63 14 | **IMPLANTATION 1ʳᵉ pose** | SO **S05488 du 29/04 sale (348,61 € TTC)** — nouveau client GMS. Pose Display + mise en rayon + étiquetage + briefing équipe + photos avant/après. **Mail confirmation envoyé** à spar.gembloux.rpcg@gmail.com (mail.mail #12626 sent — règle §10). |
| 13:15-13:45 | **AD Delhaize Gembloux** (Affilié 043561 #2913) | Chaussée de Wavre 42A, 5030 Gembloux | **Chalot Simon** (merchandiser) | 081 61 38 44 | Visite remplissage | 2 min en voiture depuis Alivim. 2 SO récentes : S05490 28/04 (489,38 €) + S05300 30/04 (107,10 €). Tier B/A actif. Mail : delhaize.gembloux@gmail.com. |

**Route OSRM** :
- Baillonville → Gosselies : 64 min / 87 km via E411 + R3 + E42
- Gosselies → Alivim Gembloux : 24 min / 27 km via E42 sortie 14
- Alivim → AD Gembloux : 2 min / 1 km (même rond-point)
- AD Gembloux → Baillonville : 59 min / 71 km via N4
- **Retour Baillonville ~14:45** — marge 1h45 avant 16:30 OK

[Google Maps tournée complète](https://www.google.com/maps/dir/5377+Baillonville/Da+Vincilaan+3+6041+Gosselies/Chauss%C3%A9e+de+Namur+52+5030+Gembloux/Chauss%C3%A9e+de+Wavre+42A+5030+Gembloux/5377+Baillonville)

**Outillage Gilles Alivim** : visseuse + vis, planogramme Teatower GMS, étiquettes prix SKU S05488 à imprimer avant départ Baillonville, cutter, M0005 Display + SRP Kraft préchargés camionnette, photos OBLIGATOIRES upload `Merchandiser/2026-05-14_Alivim_Spar_Gembloux/`.

**Bomerée non ajouté** : Nicolas n'a explicitement validé QUE Gosselies. Bomerée (122467) = SO S05297 27/03 277,26 €, contact Demoulin Michael — non casable jeudi sans dépasser 16h30 (Gosselies+Bomerée+Alivim+AD = retour ~16h05+). À ajouter S21 sur jour dédié Hainaut/Charleroi (Bomerée + autres Charleroi).

---

## Vendredi 15/05 — Famenne / Ourthe (déjà fait — IMPLANTATION Gribouillon)

| Heure | Magasin | Adresse | Contact magasin | Tel | Type | Brief |
|---|---|---|---|---|---|---|
| 09:00-10:30 | **Gribouillon SRL** (partner #123301, ship #123302) | Rue des Chasseurs Ardennais 6 boîte A, 6997 Erezée | **Nathalie Piron** | +32 86 47 72 82 | **IMPLANTATION 1ʳᵉ pose** | SO **S05502 sale 657,78 € HT** — Display GMS 16 produits 2026 (EM0106) + Display M0005 + 16 SRP Kraft + 16 SKU × 6. Marchandise sortie via Liège (TT/OUT/07828 done 04/05). Mail confirmation envoyé legribouillon@hotmail.com (mail.mail #12618). |
| 11:00-11:30 | **Carrefour Market Marche-en-Famenne** | Rue du Carmel 18, 6900 Marche | **à demander sur place** | — | Visite | Sur trajet retour Erezée → Hotton |
| 12:00-12:30 | **Delhaize Hotton** (à confirmer Odoo) | 6990 Hotton | — | — | Visite | Zone Famenne, 15 min de Marche |
| 13:30-14:00 | **Carrefour Market Durbuy** | 6940 Durbuy | — | — | Visite | Retour Baillonville |

**Route** : Baillonville → Erezée (25 min / 27 km via N983) → IMPLANTATION 09:00-10:30 → Marche (25 min) → Hotton (15 min) → Durbuy (20 min) → retour Baillonville (35 min via N86) → ~14:35.

[Google Maps tournée complète](https://www.google.com/maps/dir/5377+Baillonville/Rue+des+Chasseurs+Ardennais+6+6997+Erez%C3%A9e/Rue+du+Carmel+18+6900+Marche-en-Famenne/6990+Hotton/6940+Durbuy/5377+Baillonville)

---

## Récapitulatif S20

| Jour | Visites GMS | Implantations | Boutiques | Zone | Retour estimé |
|---|---|---|---|---|---|
| Lundi 11/05 | 1 (Lontzen) | 0 | 0 | Liège-Est / Cantons | ~11:20 (light) |
| Mardi 12/05 | 4 (Boondael + Bosvoorde + Debroux + Rixensart) | 0 | 0 | **Bruxelles Sud-Est / BW** | ~15:24 |
| Mercredi 13/05 | 3 (Materne II + Fosses + Profondeville) | 0 | 1 (Namur centre) | Namur-Sud / Jambes | ~14:45 |
| Jeudi 14/05 | 2 (Gosselies + AD Gembloux) | 1 (Alivim Spar Gembloux) | 0 | **Hainaut + Gembloux** | ~14:45 |
| Vendredi 15/05 | 3 (Marche + Hotton + Durbuy) | 1 (Gribouillon Erezée) | 0 | Famenne / Ourthe | ~14:35 |
| **Total** | **13 visites GMS** | **2 implantations** | **1 boutique** | | |

## Mails envoyés / pas envoyés

- ✅ **Alivim SRL Spar Gembloux** (spar.gembloux.rpcg@gmail.com) — mail.mail #12626 sent (IMPLANTATION jeudi 14/05 11:30)
- ✅ **Gribouillon SRL** (legribouillon@hotmail.com) — mail.mail #12618 sent 04/05 11:35 (IMPLANTATION vendredi 15/05 matin)
- ❌ Boondael : pas de mail (visite réorga, pas IMPLANTATION pure → règle §10). Appel téléphonique Gilles à 9h le matin avant arrivée.
- ❌ Bosvoorde / Debroux / Rixensart / Materne II Jambes / Fosses / Profondeville / Lontzen / Marche / Hotton / Durbuy / AD Gembloux : visites simples, pas de mail (règle §10).
- ❌ Hyper Gosselies : pas d'email partner connu dans Odoo + visite simple (pas IMPLANTATION) → pas de mail.

## Vérifications standard effectuées

- ✅ **Pas de revisite S(n-1)** : Boondael, Bosvoorde, Debroux, Rixensart, Alivim, AD Gembloux, Gosselies, Bomerée non visités S18 (markdown final v6 fait foi : Boondael retiré v6, Incourt retiré v6) ni S19 (Lux + Liège + Hannut/Ottignies + Manhay).
- ✅ **Pas de stop dans liste Arret** : seul "Intermarché Rixensart Rixalilm" est Arret (différent de Proxy Delhaize Rixensart visé).
- ✅ **Trajets Google Maps simulés** (OSRM) — retour Baillonville ≤ 16:30 chaque jour (max 15:24 mardi).
- ✅ **Contraintes contacts** : Materne II PAS le mardi (planifié mercredi OK), Fosses Leslie mercredi (OK), Hyper Gosselies matin obligatoire 8h-12h (planifié 09:35-10:35 OK).
- ✅ **Contacts visibles** dans markdown (col dédiée) et HTML (badge `.contact-badge`) — non tronqués.

## À-faire avant lundi 11/05

- [ ] Appel préalable Gilles **Boondael Mr Daniel** mardi 12/05 à 9h00 (juste avant arrivée 9h50)
- [ ] Appel préalable Nathalie Piron Gribouillon (086 47 72 82) pour confirmer dispo vendredi 15/05 matin + réception marchandise
- [ ] Charger camionnette mardi : pas de marchandise spéciale (visites)
- [ ] Charger camionnette mercredi : thés glacés Materne II + Fosses, **prévoir ramener Guarana Boost de Materne II**
- [ ] Charger camionnette jeudi : marchandise S05488 Alivim + Display M0005 + SRP Kraft + étiquettes prix imprimées
- [ ] Confirmer dispo Virginie/Benjamin Lontzen lundi (appel préalable possible)
- [ ] Scanner OVERDUE GMS Liège-Est lundi pour densifier la matinée Lontzen (journée light)

## Reports / suspens

- **CM Bouillon RDV #425** : reste actif Odoo, à statuer S21 (Lux + Hainaut/Charleroi journée dédiée)
- **Hyper Carrefour Bomerée** : laissé en suspens — à caser S21 sur jour dédié Hainaut/Charleroi avec d'autres GMS Charleroi (Bomerée + Châtelineau + Couillet hors-Arret etc.)
- **Carrefour Lontzen S20 lundi 11/05** : ajout 29/04 confirmé, journée light — opportunité densification
