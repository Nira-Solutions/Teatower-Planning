# MO state=confirmed pre-fix - 2026-04-23

Genere : 2026-04-23T10:50:50.491488

Total : **45** MO encore `state=confirmed` apres le cleanup du matin (`07_execute.py`).
Ce sont des MO creees AVANT le fix de ce matin (residus du flood ou MO manuelles).

## Arbitrage Nicolas

- (A) cancel + unlink si aucune raw move done (standard route fix)
- (B) laisser si MO legit en cours de prod (p.ex. C0200 coffret Matcha)
- (C) convertir en PO si le produit doit etre achete chez fournisseur

| MO | Produit | Qty | Create | Origin | OP | User |
|---|---|---|---|---|---|---|
| TT/MO/02853 (id=2855) | [I0301] Tisane tropicale (20 infusettes) | 525.0 | 2025-12-11 14:16 | OP/13686 | OP/13686 | OdooBot |
| TT/MO/03079 (id=3082) | [05V0852] Verveine Odorante - BIO (250 g vrac) | 3.0 | 2026-01-09 13:34 | OP/13532 | OP/13532 | OdooBot |
| TT/MO/03121 (id=3124) | [05V0856] Sorbet framboise - BIO (500 g vrac) | 20.0 | 2026-01-15 12:17 | OP/13533 | OP/13533 | OdooBot |
| TT/MO/03218 (id=3221) | [I0727] L'après-repas (20 infusettes) | 100.0 | 2026-01-27 08:56 | OP/13712 | OP/13712 | OdooBot |
| TT/MO/03233 (id=3236) | [V0835] Aloe Fraisa (50g vrac) | 30.0 | 2026-01-27 14:30 | OP/13965 | OP/13965 | OdooBot |
| TT/MO/03299 (id=3302) | [V0376] Coup de foudre (100 g vrac) | 30.0 | 2026-02-03 14:31 | OP/13906 | OP/13906 | OdooBot |
| TT/MO/03316 (id=3319) | [V0666] English Breakfast  (100 g vrac) | 30.0 | 2026-02-04 14:31 | OP/13925 | OP/13925 | OdooBot |
| TT/MO/03356 (id=3359) | [I0376] Coup de foudre (20 infusettes) | 100.0 | 2026-02-08 14:30 | OP/13689 | OP/13689 | OdooBot |
| TT/MO/03435 (id=3438) | [I0778] Spéculoos & Cie (20 infusettes) | 100.0 | 2026-02-16 14:51 | OP/13725 | OP/13725 | OdooBot |
| TT/MO/03458 (id=3461) | [V0839] Caramel Beurre salé (100 g vrac) | 30.0 | 2026-02-19 14:30 | OP/13969 | OP/13969 | OdooBot |
| TT/MO/03525 (id=3528) | [I0729] Relax BIO (20 infusettes) | 125.0 | 2026-02-24 12:27 | OP/13714 | OP/13714 | OdooBot |
| TT/MO/03570 (id=3573) | [V0600] La lampe merveilleuse (100 g vrac) | 60.0 | 2026-03-02 14:30 | OP/13908 | OP/13908 | OdooBot |
| TT/MO/03574 (id=3577) | [I0839] Caramel Beurre salé (20 infusettes) | 100.0 | 2026-03-03 13:23 | OP/13745 | OP/13745 | OdooBot |
| TT/MO/03583 (id=3586) | [SRPV0880] SRP 6x V0880 - Blue Earl grey BIO VRAC | 150.0 | 2026-03-04 10:48 | OP/35539 | OP/35539 | OdooBot |
| TT/MO/03589 (id=3592) | [I0859] Délice de Montélimar (20 infusettes) | 100.0 | 2026-03-05 19:16 | OP/13755 | OP/13755 | OdooBot |
| TT/MO/03597 (id=3600) | [V0767] Earl grey (100 g vrac) | 120.0 | 2026-03-06 14:30 | OP/13943 | OP/13943 | OdooBot |
| TT/MO/03605 (id=3608) | [V0610] Earl Grey Supérieur (100 g vrac) | 90.0 | 2026-03-07 14:29 | OP/13912 | OP/13912 | OdooBot |
| TT/MO/03627 (id=3630) | [I0900] Bora Bora - BIO (20 infusettes) | 75.0 | 2026-03-10 09:48 | OP/13776 - S05133 | OP/13776 | OdooBot |
| TT/MO/03641 (id=3644) | [V0854] Camomille Matricaire - BIO (50g vrac) | 90.0 | 2026-03-10 14:30 | OP/13978 | OP/13978 | OdooBot |
| TT/MO/03663 (id=3666) | [05V0880] Blue Earl Grey BIO (500 g vrac) | 22.0 | 2026-03-12 14:29 | OP/13539 | OP/13539 | OdooBot |
| TT/MO/03677 (id=3680) | [I0728] Jardin gourmand (20 infusettes) | 150.0 | 2026-03-13 14:30 | OP/13713 | OP/13713 | OdooBot |
| TT/MO/03717 (id=3720) | [C0102] Assortiment découverte | 140.0 | 2026-03-18 08:55 | OP/13636 | OP/13636 | OdooBot |
| TT/MO/03729 (id=3732) | [V0685] Darjeeling SF FTGFOP1 - BIO (100 g vrac) | 60.0 | 2026-03-18 14:30 | OP/13928 | OP/13928 | OdooBot |
| TT/MO/03745 (id=3748) | [V0772] Black Mango (100 g vrac) | 60.0 | 2026-03-20 09:40 | OP/13944 | OP/13944 | OdooBot |
| TT/MO/03773 (id=3776) | [V0852] Verveine Odorante - BIO (50g vrac) | 90.0 | 2026-03-21 14:29 | OP/13977 | OP/13977 | OdooBot |
| TT/MO/03774 (id=3777) | [V0900] Bora Bora - BIO (100 g vrac) | 90.0 | 2026-03-21 14:29 | OP/14004 | OP/14004 | OdooBot |
| TT/MO/03772 (id=3775) | [V0775] Promenade à venise (100 g vrac) | 60.0 | 2026-03-21 14:29 | OP/13946 | OP/13946 | OdooBot |
| TT/MO/03795 (id=3798) | [I0772] Black Mango (20 infusettes) | 75.0 | 2026-03-25 16:35 | OP/13722 | OP/13722 | OdooBot |
| TT/MO/03798 (id=3801) | [I0773] New York (20 infusettes) | 100.0 | 2026-03-25 21:18 | OP/13723 | OP/13723 | OdooBot |
| TT/MO/03804 (id=3807) | [I0635] Silhouette (20 infusettes) | 325.0 | 2026-03-26 12:35 | OP/13702 | OP/13702 | OdooBot |
| TT/MO/03803 (id=3806) | [I0631] Le thé des amoureux (20 infusettes) | 550.0 | 2026-03-26 12:35 | OP/13699 | OP/13699 | OdooBot |
| TT/MO/03809 (id=3812) | [I0638] Sérénité - BIO (20 infusettes) | 200.0 | 2026-03-26 14:20 | OP/13703 | OP/13703 | OdooBot |
| TT/MO/03813 (id=3816) | [I0617] Liberté (20 infusettes) | 125.0 | 2026-03-26 14:30 | OP/13696 | OP/13696 | OdooBot |
| TT/MO/03814 (id=3817) | [I0634] Gourmandise (20 infusettes) | 200.0 | 2026-03-26 14:30 | OP/13701 | OP/13701 | OdooBot |
| TT/MO/03893 (id=3896) | [V0729] Relax BIO (80 g vrac) | 120.0 | 2026-03-27 14:29 | OP/13936 | OP/13936 | OdooBot |
| TT/MO/03892 (id=3895) | [V0728] Jardin gourmand (80 g vrac) | 90.0 | 2026-03-27 14:29 | OP/13935 | OP/13935 | OdooBot |
| TT/MO/03901 (id=3904) | [V0880] Blue Earl Grey BIO (100 g vrac) | 300.0 | 2026-03-27 14:29 | OP/13995 | OP/13995 | OdooBot |
| TT/MO/03890 (id=3893) | [V0638] Sérénité - BIO (100 g vrac) | 200.0 | 2026-03-27 14:29 | OP/13922 | OP/13922 | OdooBot |
| TT/MO/03904 (id=3907) | [I0885] Cococabana (20 infusettes) | 75.0 | 2026-03-28 14:30 | OP/13770 | OP/13770 | OdooBot |
| TT/MO/03906 (id=3909) | [I0685] Darjeeling SF FTGFOP1 - BIO (20 infusettes) | 75.0 | 2026-03-29 11:05 | OP/13707 | OP/13707 | OdooBot |
| TT/MO/03909 (id=3912) | [V0681] Menthe douce - BIO (50 g vrac) | 30.0 | 2026-03-29 14:29 | OP/13927 | OP/13927 | OdooBot |
| TT/MO/03910 (id=3913) | [V0778] Spéculoos & Cie (100 g vrac) | 30.0 | 2026-03-29 14:29 | OP/13947 | OP/13947 | OdooBot |
| TT/MO/03911 (id=3914) | [V0859] Délice de Montélimar (100 g vrac) | 60.0 | 2026-03-29 14:58 | OP/13981 | OP/13981 | OdooBot |
| TT/MO/03918 (id=3921) | [V0836] Ayurveda - BIO (100 g vrac) | 60.0 | 2026-03-30 14:29 | OP/13966 | OP/13966 | OdooBot |
| TT/MO/04126 (id=4129) | [I0880] Blue Earl Grey BIO (20 infusettes) | 200.0 | 2026-04-21 15:09 | OP/13769 | OP/13769 | OdooBot |

**Total** : 45 MO confirmed