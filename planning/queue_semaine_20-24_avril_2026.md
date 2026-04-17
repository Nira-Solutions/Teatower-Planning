# Planning Merchandiser — Semaine du 20 au 24 avril 2026

> **Merchandiser** : Jerome Carlier | **Base** : Baillonville (5377) | **Horaire** : 08h30 - 16h30
> Genere le 2026-04-15, **v5 corrigee** le 2026-04-17 par agent planning Teatower.
> **32 visites** au total sur 5 jours (dont 4 implantations).
> **Tous les trajets verifies via OSRM** (Open Source Routing Machine).

---

## Corrections v4 → v5

1. **Spar Manhay (Lambertdis)** : corrige de VISITE 30min a **IMPLANTATION 1h** (mardi).
2. **AD Fosses-la-Ville** : deplace du mercredi au **lundi** — trajet Saint-Severin→Fosses = 62 min non compte en v4, provoquait un retour a 17:42. Fosses est a 13 min de Spy, s'integre parfaitement dans la route lundi. Contrainte respectee : pas de visite le mardi (lundi OK).
3. **CM Barvaux** : **retire** — visite effectuee la semaine passee (S19).
4. **Jeudi entierement reordonne** : les CP etaient faux en v4 (zigzag Ferrieres→Ottignies = 111 min !). Route corrigee : Anhee en premier, puis sud, retour via Ferrieres. Ottignies retire (reporte S21).
5. **Genappe + Lasne** retires du lundi : retour Lasne→Baillonville = 70 min (pas 45 min en v4). Depassement 17:03.
6. **ITM Jambes** retire du mardi : libere le temps pour Manhay IMPLANTATION 1h.
7. **Delhaize Marche** retire du vendredi : depassement 16:59 avec 7 stops. Reporte (20 min de Baillonville).
8. **Aucun mail client envoye** (sauf implantations). **Aucun event calendrier Odoo cree.**
9. **Lien Google Maps** integre pour chaque journee.

---

## Regles appliquees

1. **VISITE = 30 min** | **IMPLANTATION = 1h** sur place.
2. **Trajets = OSRM** (simulation routiere reelle, pas d'estimation).
3. **Retour Baillonville MAX 16h30** — toutes les journees verifiees.
4. **Clients ARRET exclus** (tag [ARRET] dans Odoo).
5. **Jerome = merchandiser uniquement** (pas de prospection).
6. **27 magasins S16 exclus** (visites Gilles 13-17 avril).
7. **Contraintes responsable/contact respectees** (cf. REGLES.md §4).

---

## Lundi 20/04 — Hainaut (Enghien) + Sambre + Fosses-la-Ville

| Heure | Type | Magasin | Trajet |
|---|---|---|---|
| 10:10-11:10 | IMPLANTATION | Delhaize Enghien | 100 min / 128 km depuis Baillonville |
| 11:58-12:28 | VISITE | ITM Gosselies (Distriparenthese) | 48 min / 55 km |
| 12:47-13:17 | VISITE | ITM Spy (SRL Spydis) | 19 min / 21 km |
| 13:30-14:00 | VISITE | AD Fosses-la-Ville | 13 min / 11 km |
| 14:14-14:44 | VISITE | ITM Floriffoux (Floridis SA) | 14 min / 12 km |

> **Retour Baillonville : ~15:34** (trajet retour : 50 min / 64 km). Marge : 56 min.
> **Distance totale** : 288 km | **5 stops** (1 implantation + 4 visites)
> **Google Maps** : https://www.google.com/maps/dir/50.334,5.283/50.6908,3.9647/50.4621,4.431/50.4793,4.667/50.3955,4.697/50.455,4.738/50.334,5.283

### 10:10-11:10 | IMPLANTATION | Delhaize Enghien | S05413

- **Adresse** : Square de la Dodane, 7850 Enghien
- **Contact** : Mme Mestdag (boss), Mme Luba (rayon)
- **Brief** : IMPLANTATION flanc de tete de gondole. Installer le display Teatower selon planogramme. SO S05413 (366,81 EUR). Duree 1h.
- **Produits cles** : display + assortiment S05413

### 11:58-12:28 | VISITE | Intermarche Gosselies (Distriparenthese) | S05316

- **Adresse** : Rue Pont a Migneloux 13, 6041 Gosselies
- **Contact** : Valentin Schirru | Tel : 071/35.40.10
- **Tier** : C | Derniere commande : 15j
- **Brief** : Controle facing et remplissage presentoir.

### 12:47-13:17 | VISITE | Intermarche Spy (SRL Spydis) | S05319

- **Adresse** : Route de Saussin 45, 5190 Jemeppe-sur-Sambre
- **Contact** : Emilie / Dorian | Tel : +32 71 78 74 39
- **Tier** : B | Derniere commande : 15j
- **Brief** : Remplissage regulier.

### 13:30-14:00 | VISITE | AD Fosses-la-Ville (Affilie 043366) | S02185

- **Adresse** : Rue du Cimetiere 5, Fosses-la-Ville
- **Contact** : Leslie | Tel : 071 71 29 12
- **Tier** : C | Derniere commande : 247j | OVERDUE | Priorite Gilles
- **Brief** : OVERDUE. Visite de reprise. Deplace du mercredi au lundi (trajet mercredi impossible depuis Liege). Contrainte : pas le mardi (respecte).

### 14:14-14:44 | VISITE | Intermarche Floriffoux (Floridis SA) | S05126

- **Adresse** : Rue Emeree 4, 5150 Floriffoux
- **Contact** : Loredana / Manon | Tel : 081 44 05 39
- **Tier** : B | Derniere commande : 36j | OVERDUE (cycle 35j)
- **Brief** : Remplissage complet. OVERDUE 1 jour.

---

## Mardi 21/04 — Namur + Manhay (implantation)

| Heure | Type | Magasin | Trajet |
|---|---|---|---|
| 09:04-10:04 | IMPLANTATION | Spar Namur (NDB Diffusion) | 35 min / 41 km depuis Baillonville |
| 10:10-10:40 | VISITE | Delhaize de Bouge | 5 min / 3 km |
| 10:41-11:11 | VISITE | ITM Bouge (Windmill SA) | 2 min / 1 km |
| 11:23-11:53 | VISITE | ITM Naninne (BOISDIS SA) | 12 min / 7 km |
| 12:09-12:39 | VISITE | ITM Belgrade (Belgradis) | 15 min / 9 km |
| 12:58-13:28 | VISITE | ITM Assesse (SA Barthe) | 19 min / 19 km |
| 14:26-15:26 | IMPLANTATION | Spar Manhay (Lambertdis SRL) | 58 min / 61 km |

> **Retour Baillonville : ~16:10** (trajet retour : 43 min / 37 km). Marge : 20 min.
> **Distance totale** : 177 km | **7 stops** (2 implantations + 5 visites)
> **Google Maps** : https://www.google.com/maps/dir/50.334,5.283/50.4645,4.867/50.474,4.883/50.472,4.8785/50.4305,4.874/50.448,4.854/50.38,5.01/50.288,5.675/50.334,5.283

### 09:04-10:04 | IMPLANTATION | Spar Namur (NDB Diffusion) | S05382

- **Adresse** : Rue des Echasseurs 1, 5000 Namur
- **Contact** : info@sparnamur.com | Tel : +32 81 81 31 87
- **Brief** : IMPLANTATION display complet + 16 references. Mettre en place le presentoir Teatower avec l'assortiment complet. 16 SRP Kraft Horeca pour la presentation.
- **Note Jerome** : "ok pour implantation semaine prochaine"

### 10:10-10:40 | VISITE | Delhaize de Bouge (Affilie 041345)

- **Adresse** : Chaussee de Louvain 336, 5004 Namur
- **Contact** : Mme Destree / Grandjean / Augustaine | Tel : +32 81 21 48 88
- **Tier** : D (nouveau) | Priorite Gilles
- **Brief** : Visite merchandiser. Verification display et accessoires (filtre boule A0271, filtre pince A0374).

### 10:41-11:11 | VISITE | Intermarche Bouge (Windmill SA) | S05042

- **Adresse** : Chaussee de Louvain 257, 5000 Bouge
- **Contact** : Dany Decoster | Tel : 081569346
- **Tier** : B | Derniere commande : 50j | OVERDUE (cycle 35j)
- **Brief** : OVERDUE 15 jours. Remplissage complet. Priorite Gilles.

### 11:23-11:53 | VISITE | Intermarche Naninne (BOISDIS SA) | S05269

- **Adresse** : Chaussee de Marche 860, 5100 Naninne
- **Contact** : Stephanie | Tel : 081 63 36 96
- **Tier** : A | Derniere commande : 22j | OVERDUE (cycle 20j)
- **Brief** : OVERDUE 2 jours. Remplissage complet. Priorite Gilles.

### 12:09-12:39 | VISITE | Intermarche Belgrade (Belgradis) | S05047

- **Adresse** : Allee des Ormes 15, 5001 Belgrade
- **Contact** : Stephanie | Tel : 081260187
- **Tier** : B | Derniere commande : 50j | OVERDUE (cycle 35j)
- **Brief** : OVERDUE 15 jours. Remplissage complet.

### 12:58-13:28 | VISITE | Intermarche Assesse (SA Barthe) | S05330

- **Adresse** : Rue Melville Wilson 3, 5330 Assesse
- **Contact** : Anne Buttiens | Tel : 083 66 05 70
- **Tier** : A | Derniere commande : 14j
- **Brief** : Remplissage regulier. Sur route vers Manhay.

### 14:26-15:26 | IMPLANTATION | Spar Manhay (Lambertdis SRL) | S05380

- **Adresse** : Rue d Erezee, 6960 Manhay
- **Contact** : - | Tel : +32 86 45 55 87
- **Tier** : C | Derniere commande : 4j
- **Brief** : **IMPLANTATION** (nouveau client depuis 11/04). Mise en place complete du display Teatower. Duree 1h.
- **CORRECTION v5** : etait "check 30min" en v4, corrige en IMPLANTATION 1h.

---

## Mercredi 22/04 — Liege

| Heure | Type | Magasin | Trajet |
|---|---|---|---|
| 09:05-09:35 | VISITE | Hyper Carrefour Boncelles | 36 min / 37 km depuis Baillonville |
| 09:51-10:21 | VISITE | ITM Tilff (Chili Peppers) | 16 min / 9 km |
| 10:41-11:11 | VISITE | Hyper Carrefour Fleron | 20 min / 15 km |
| 11:27-11:57 | VISITE | Delhaize Barchon | 16 min / 10 km |
| 12:15-12:45 | VISITE | Delhaize Bois-de-breux | 18 min / 14 km |
| 13:01-13:31 | VISITE | ITM Herve (LEHDIS SA) | 16 min / 18 km |
| 13:51-14:21 | VISITE | Delhaize Liege Ardente | 20 min / 20 km |
| 14:48-15:18 | VISITE | Proxy Delhaize Saint-Severin | 27 min / 25 km |

> **Retour Baillonville : ~15:41** (trajet retour : 24 min / 25 km). Marge : 48 min.
> **Distance totale** : 174 km | **8 stops** (8 visites)
> **Google Maps** : https://www.google.com/maps/dir/50.334,5.283/50.581,5.53/50.565,5.585/50.621,5.685/50.668,5.742/50.645,5.626/50.639,5.794/50.638,5.587/50.506,5.415/50.334,5.283
>
> **Fosses-la-Ville retire** : trajet Saint-Severin→Fosses = 62 min. Retour avec Fosses = 17:42 (depassement de 1h12). Fosses deplace au lundi (13 min depuis Spy).

### 09:05-09:35 | VISITE | Hyper Carrefour Boncelles | S03883

- **Adresse** : Rue du Condroz 16, 4100 Boncelles
- **Contact** : Robert Stassin | Tel : +32 4 338 86 11
- **Tier** : C | Derniere commande : 170j | OVERDUE | Priorite Gilles
- **Brief** : OVERDUE. Hyper = matin obligatoire (horaire 7h-11h30). Demander Mr Stassin pour faire la commande. Contrainte : pas le mardi.

### 09:51-10:21 | VISITE | Intermarche Tilff (Chili Peppers) | S05313

- **Adresse** : Av. des Ardennes 8, 4130 Esneux
- **Contact** : Christine Castermans | Tel : +32 479 32 28 39
- **Tier** : A | Derniere commande : 15d
- **Brief** : Remplissage regulier haute frequence.

### 10:41-11:11 | VISITE | Hyper Carrefour Fleron

- **Adresse** : Rue de la Clef 30, 4620 Fleron
- **Contact** : - | Tel : +32 4 355 86 11
- **Tier** : D | Priorite Gilles
- **Brief** : Visite merchandiser. Hyper = matin obligatoire.

### 11:27-11:57 | VISITE | Delhaize Barchon (BARCHONEW SRL) | S05290

- **Adresse** : Rue Champs de Tignee 32, 4671 Barchon
- **Contact** : Jerome ou Jovani | Tel : +32 4 362 27 33
- **Tier** : C | Derniere commande : 20j | Priorite Gilles
- **Brief** : Remplissage. Contrainte : ferme lundi matin, ouvre a partir de midi le lundi. Mercredi OK.

### 12:15-12:45 | VISITE | Delhaize Bois-de-breux | S05288

- **Adresse** : Rue de Herve 280, 4030 Liege
- **Contact** : Olivier Landauer / Demany / Poppov / Ghislaine | Tel : +32 4 365 74 07
- **Tier** : B | Derniere commande : 20j | Priorite Gilles
- **Brief** : Remplissage.

### 13:01-13:31 | VISITE | Intermarche Herve (LEHDIS SA) | S04866

- **Adresse** : Rue du Pont 17, 4650 Herve
- **Contact** : Samuel Royen | Tel : -
- **Tier** : C | Derniere commande : 75j | OVERDUE (cycle 50j) | Priorite Gilles
- **Brief** : OVERDUE 25 jours. Remplissage. Verification etat display.

### 13:51-14:21 | VISITE | Delhaize Liege Ardente (Delardentes SRL) | S05146

- **Adresse** : Chaussee de Tongres 269, 4000 Liege
- **Contact** : Kevin Demarteau 0468 37 62 65
- **Tier** : C | Derniere commande : 36j
- **Brief** : Remplissage. The en rayon. Sur route retour vers Condroz.

### 14:48-15:18 | VISITE | Proxy Delhaize Saint-Severin (D-trois SRL) | S05286

- **Adresse** : Route du Condroz 243, 4550 Nandrin
- **Contact** : Mme Dessart / Renaud / Philippe | Tel : +32 4 372 09 85
- **Tier** : C | Derniere commande : 20j | Priorite Gilles
- **Brief** : Remplissage. Dernier stop, sur route retour via le Condroz.

---

## Jeudi 23/04 — Namur sud (Anhee/Beauraing/Rochefort) + Ferrieres + Hannut

| Heure | Type | Magasin | Trajet |
|---|---|---|---|
| 09:09-09:39 | VISITE | ITM Anhee (Holebo SA) | 39 min / 41 km depuis Baillonville |
| 10:09-10:39 | VISITE | CM Beauraing (DEMARS SA) | 30 min / 28 km |
| 10:40-11:10 | VISITE | Delhaize Beauraing | 1 min / 0.3 km |
| 11:35-12:05 | VISITE | AD Rochefort (SA Marer) | 25 min / 24 km |
| 12:55-13:25 | VISITE | Proxy Delhaize Ferrieres | 50 min / 46 km |
| 14:37-15:07 | VISITE | CM Hannut (P.R.MACLEKY) | 72 min / 86 km |

> **Retour Baillonville : ~16:03** (trajet retour : 56 min / 62 km). Marge : 26 min.
> **Distance totale** : 285 km | **6 stops** (6 visites)
> **Google Maps** : https://www.google.com/maps/dir/50.334,5.283/50.31,4.875/50.11,4.957/50.1085,4.958/50.16,5.222/50.393,5.613/50.671,5.079/50.334,5.283
>
> **Route reordonnee v5** : Anhee en premier (plus proche de Baillonville), puis descente vers Beauraing/Rochefort, remontee via Ferrieres, fin par Hannut (UNIQUEMENT le jeudi). Ottignies retire (zigzag 111 min Ferrieres→Ottignies, reporte S21).

### 09:09-09:39 | VISITE | Intermarche Anhee (Holebo SA) | S04667

- **Adresse** : Chaussee de Dinant 127, 5537 Anhee
- **Contact** : Christophe | Tel : +32 82 71 39 84
- **Tier** : C | Derniere commande : 99j | OVERDUE (cycle 50j)
- **Brief** : OVERDUE 49 jours. Visite urgente. Contrainte : jamais le lundi + visite le matin. Jeudi matin OK.

### 10:09-10:39 | VISITE | Carrefour Market Beauraing (DEMARS SA) | S05256

- **Adresse** : Rue de Rochefort 37, 5570 Beauraing
- **Contact** : Therese / Alison | Tel : 082/71 02 30
- **Tier** : A | Derniere commande : 23j | OVERDUE (cycle 20j)
- **Brief** : OVERDUE 3 jours. Remplissage complet.

### 10:40-11:10 | VISITE | Delhaize Beauraing (SA Beausov New) | S05325

- **Adresse** : 150 rue de Rochefort, 5570 Beauraing
- **Contact** : Mme Sovet / Gregory | Tel : +32 82 71 36 97
- **Tier** : C | Derniere commande : 14j
- **Brief** : Remplissage. Meme rue que Carrefour Beauraing, 300m.

### 11:35-12:05 | VISITE | AD Rochefort (SA Marer) | S05081

- **Adresse** : Rue de Marche 112-114, 5580 Rochefort
- **Contact** : - | Tel : +32 84 21 01 03
- **Tier** : B | Derniere commande : 47j | OVERDUE (cycle 35j) | Priorite Gilles
- **Brief** : OVERDUE 12 jours. Remplissage complet.

### 12:55-13:25 | VISITE | Proxy Delhaize Ferrieres (Affilie 043151)

- **Adresse** : Rue du Pre du Fa 6A, 4190 Ferrieres
- **Contact** : Bernard Counasse / Martine Georis | Tel : +32 86 40 02 27
- **Tier** : D | Priorite Gilles
- **Brief** : Visite merchandiser. Responsable absent le mercredi — jeudi OK (Bernard Counasse ou Martine Georis present(e)).

### 14:37-15:07 | VISITE | Carrefour Market Hannut (P.R.MACLEKY Srl) | S04705

- **Adresse** : Rue de Tirlemont 46, 4280 Hannut
- **Contact** : Rolant Barbara | Tel : -
- **Tier** : C | Derniere commande : 96j | OVERDUE (cycle 50j)
- **Brief** : OVERDUE 46 jours. Contrainte : visite UNIQUEMENT le jeudi. Remplissage + preparation thes glaces.

---

## Vendredi 24/04 — Namur sud / Luxembourg (2 implantations)

| Heure | Type | Magasin | Trajet |
|---|---|---|---|
| 09:32-10:32 | IMPLANTATION | CM Bievre | 63 min / 65 km depuis Baillonville |
| 10:58-11:58 | IMPLANTATION | Proxy Delhaize Maissin | 25 min / 13 km |
| 12:49-13:19 | VISITE | AD Bastogne (SA Marer) | 51 min / 60 km |
| 13:21-13:51 | VISITE | CM Bastogne (Pascalino) | 2 min / 1 km |
| 14:33-15:03 | VISITE | CM Hotton (HODICA SA) | 43 min / 51 km |
| 15:15-15:45 | VISITE | Delhaize Barvaux | 11 min / 11 km |

> **Retour Baillonville : ~16:07** (trajet retour : 22 min / 19 km). Marge : 23 min.
> **Distance totale** : 219 km | **6 stops** (2 implantations + 4 visites)
> **Google Maps** : https://www.google.com/maps/dir/50.334,5.283/49.935,5.02/49.946,5.146/50.0,5.715/50.002,5.71/50.267,5.446/50.353,5.494/50.334,5.283
>
> **CM Barvaux retire** (visite effectuee S19). **Delhaize Marche retire** (depassement 16:59 avec 7 stops, reporte — 20 min de Baillonville).

### 09:32-10:32 | IMPLANTATION | Carrefour Market Bievre

- **Adresse** : Rue de Bouillon 54, 5555 Bievre
- **Contact** : A confirmer
- **Brief** : IMPLANTATION display complet Teatower. Nouveau client GMS. SO en cours de creation par Jerome. Partner Odoo : Cafermi (ID 7440).

### 10:58-11:58 | IMPLANTATION | Proxy Delhaize Maissin | S05420

- **Adresse** : Avenue de France 13, 6852 Maissin
- **Contact** : A confirmer
- **Brief** : IMPLANTATION display complet Teatower. Nouveau client GMS (Proxy Delhaize). SO S05420 (735 EUR) confirme.

### 12:49-13:19 | VISITE | AD Bastogne (SA Marer) | S05258

- **Adresse** : Route de Marche 112-114, 6660 Bastogne
- **Contact** : Valentin Gilson | Tel : +32 61 21 70 84
- **Tier** : A | Derniere commande : 23j | OVERDUE (cycle 20j)
- **Brief** : OVERDUE 3 jours. Remplissage complet.

### 13:21-13:51 | VISITE | Carrefour Market Bastogne (Pascalino) | S04883

- **Adresse** : Route de Marche 149, 6600 Bastogne
- **Contact** : Fabienne Antoine | Tel : +32 61 21 23 42
- **Tier** : C | Derniere commande : 72j | OVERDUE (cycle 50j)
- **Brief** : OVERDUE 22 jours. Se presenter le matin de preference. Meme ville que AD Bastogne.

### 14:33-15:03 | VISITE | Carrefour Market Hotton (HODICA SA) | S05372

- **Adresse** : Rue de la Jonction 16, 6990 Hotton
- **Contact** : Gauthier Lempereur | Tel : 084 46 73 44
- **Tier** : B | Derniere commande : 6j
- **Brief** : Remplissage post-livraison S05372.

### 15:15-15:45 | VISITE | Delhaize Barvaux (Affilie 040990)

- **Adresse** : Rue Petit-Barvaux 6, 6940 Barvaux-sur-Ourthe
- **Contact** : Bernard Counasse (gerant) | Tel : +32 86 36 60 08
- **Tier** : D | Priorite Gilles
- **Brief** : Visite merchandiser. Nouveau client — controle post-implantation.

---

## Resume de la semaine

| Jour | Stops | Types | Zone | Retour | Marge | km |
|---|---|---|---|---|---|---|
| Lundi 20/04 | 5 | 1 IMPL + 4 VISITE | Hainaut + Sambre + Fosses | ~15:34 | 56 min | 288 |
| Mardi 21/04 | 7 | 2 IMPL + 5 VISITE | Namur + Luxembourg (Manhay) | ~16:10 | 20 min | 177 |
| Mercredi 22/04 | 8 | 8 VISITE | Liege | ~15:41 | 48 min | 174 |
| Jeudi 23/04 | 6 | 6 VISITE | Namur sud + Ferrieres + Hannut | ~16:03 | 26 min | 285 |
| Vendredi 24/04 | 6 | 2 IMPL + 4 VISITE | Namur sud / Luxembourg | ~16:07 | 23 min | 219 |
| **TOTAL** | **32** | 4 implantations + 28 visites | | | | **1143** |

### Comparaison v4 → v5

| Metrique | v4 | v5 | Raison |
|---|---|---|---|
| Total visites | 38 | 32 | -6 stops irrealisables (trajets reels) |
| Lundi | 6 stops, ret 15:50 | 5 stops, ret 15:34 | -Genappe, -Lasne, +Fosses |
| Mardi | 8 stops, ret 15:40 | 7 stops, ret 16:10 | -Jambes, Manhay = IMPL 1h |
| Mercredi | 9 stops, ret 16:00 | 8 stops, ret 15:41 | -Fosses (trajet 62min non compte) |
| Jeudi | 7 stops, ret 15:45 | 6 stops, ret 16:03 | -Ottignies (zigzag 111min), route reordonnee |
| Vendredi | 8 stops, ret 15:50 | 6 stops, ret 16:07 | -CM Barvaux (S19), -Marche (depassement) |
| Trajets | Estimes manuellement | OSRM (simulation reelle) | Plus aucune estimation |
| Google Maps | Non integre | Lien par journee | Verification possible |

### Magasins reportes S21+

| Magasin | Raison du report | Zone |
|---|---|---|
| ITM Genappe (S05279) | Retour lundi 17:03 avec Enghien. Journee BW necessaire. | BW |
| Crf Express Lasne (S05281) | Idem Genappe. | BW |
| Delhaize Ottignies (S05282) | Zigzag Ferrieres→Ottignies = 111 min. Journee BW necessaire. | BW |
| Delhaize Marche (S05259) | Vendredi depassement avec 7 stops. A 20min de Baillonville, facile a placer. | Namur |
| ITM Jambes (S05327) | Retire mardi pour permettre Manhay IMPL. Facilement planifiable un autre jour. | Namur |
| CM Barvaux (S05405) | Visite effectuee S19 — pas de revisite S20. | Luxembourg |

### Magasins prioritaires Gilles NON planifies S20

| Magasin | Zone | Raison du report |
|---|---|---|
| Proxy Delhaize Etterbeek | BXL | Client ne souhaite pas le suivi merchandiser. EXCLU definitivement. |
| Hyper Carrefour Arlon | Luxembourg | Pas de SO confirme. Hyper loin (1h30). |
| Hyper Carrefour Waterloo MSJ | BW | Pas de SO confirme (Tier D). |
| Proxy Delhaize Bosvoorde | BXL | Reporter en journee BXL (S22+). |
| CM La Chasse | BXL | Reporter en journee BXL (S22+). OVERDUE 153j. |
| ITM Hamoir | Liege | Contrainte : pas mardi PM ni mercredi. Reporter S21. |

---

## Notes de Jerome extraites des commandes Odoo

| SO | Client | Note Jerome | Integre dans |
|---|---|---|---|
| S05413 | Delhaize Enghien | "Commande confirmee — Implantation semaine du 20/04/2026" | Lundi 20/04, implantation Enghien |
| S05382 | Spar Namur (NDB Diffusion) | "ok pour implantation semaine prochaine" | Mardi 21/04, implantation Spar Namur |
| S05420 | Proxy Delhaize Maissin | SO confirme dans Odoo (735 EUR) | Vendredi 24/04, implantation Maissin |
| S05380 | Spar Manhay (Lambertdis SRL) | Nouveau client depuis 11/04 | Mardi 21/04, **IMPLANTATION** (corrige v5) |
