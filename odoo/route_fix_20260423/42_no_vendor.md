# OP TT sans route ET sans vendor - 2026-04-23

Genere : 2026-04-23T10:50:50.272882

Ces OP sont TT/Stock, `route_id=False`, et le produit n'a aucun `product.supplierinfo`.
Le scheduler Odoo ne peut rien faire pour eux (ni Buy, ni MO).

## Arbitrage Nicolas

- (A) ajouter un seller_ids au produit -> puis appliquer route Buy
- (B) supprimer l'OP si produit non commande chez fournisseur
- (C) laisser `route_id=False` si production interne future (ex: coffrets faits maison)

| OP | Produit | Code | Tmpl | Type | min / max | Purchase OK |
|---|---|---|---|---|---|---|
| OP/13497 (id=5073) | 400G Panier Grand Maman | 05V0279 | 3961 | consu | 6.0 / 12.0 | True |
| OP/13502 (id=5078) | Pai Mu Tan - BIO (250 g vrac) | 05V0625 | 3967 | consu | 1.0 / 1.0 | True |
| OP/13536 (id=5112) | Café liégeois (500 g vrac) | 05V0874 | 4004 | consu | 1.0 / 2.0 | True |
| OP/13541 (id=5117) | Vrac 1 kg Lady Dodo | 1V0121 | 4010 | consu | 1.0 / 1.0 | True |
| OP/13542 (id=5118) | Vrac 1 kg Etoiles filantes | 1V0205 | 4011 | consu | 1.0 / 1.0 | True |
| OP/13543 (id=5119) | Vrac 1 kg Le panier de grand maman | 1V0279 | 4012 | consu | 2.0 / 4.0 | True |
| OP/13544 (id=5120) | Vrac 1 kg Détox | 1V0287 | 4013 | consu | 1.0 / 1.0 | True |
| OP/13545 (id=5121) | Vrac 1 kg Sensuali-thé | 1V0607 | 4014 | consu | 1.0 / 1.0 | True |
| OP/13546 (id=5122) | Vrac 1 kg Liberté | 1V0617 | 4015 | consu | 1.0 / 2.0 | True |
| OP/13547 (id=5123) | Vrac 1 kg Sencha_ BE-BIO-01 | 1V0626 | 4016 | consu | 1.0 / 2.0 | True |
| OP/13548 (id=5124) | Vrac 1 kg Le thé des amoureux | 1V0631 | 4017 | consu | 1.0 / 1.0 | True |
| OP/13549 (id=5125) | Vrac 1kg Gourmandise | 1V0634 | 4018 | consu | 4.0 / 9.0 | True |
| OP/13550 (id=5126) | Vrac 1 kg Sérénithé _ BE-BIO-01 | 1V0638 | 4019 | consu | 1.0 / 1.0 | True |
| OP/13551 (id=5127) | Vrac 1 kg Maté vert du brésil | 1V0664 | 4020 | consu | 3.0 / 5.0 | True |
| OP/13552 (id=5128) | Vrac 1 kg English Breakfast | 1V0666 | 4021 | consu | 1.0 / 2.0 | True |
| OP/13553 (id=5129) | Vrac 1 kg Pomme d'Amour | 1V0717 | 4022 | consu | 2.0 / 3.0 | True |
| OP/13554 (id=5130) | Vrac 1 kg Namasté_ BE-BIO-01 | 1V0723 | 4023 | consu | 1.0 / 1.0 | True |
| OP/13555 (id=5131) | Vrac 1 kg Jardin Gourmand | 1V0728 | 4024 | consu | 3.0 / 5.0 | True |
| OP/13556 (id=5132) | Vrac 1 kg Relax_ BE-BIO-01 | 1V0729 | 4025 | consu | 1.0 / 1.0 | True |
| OP/13557 (id=5133) | Vrac 1 kg Jardin de babylone | 1V0734 | 4026 | consu | 1.0 / 1.0 | True |
| OP/13558 (id=5134) | Vrac 1 kg Earl grey | 1V0767 | 4027 | consu | 1.0 / 2.0 | True |
| OP/13559 (id=5135) | Vrac 1 kg Thé du désert | 1V0813 | 4028 | consu | 1.0 / 2.0 | True |
| OP/13560 (id=5136) | Vrac 1 kg Marrakech Sunset BE-BIO-01 | 1V0820 | 4029 | consu | 1.0 / 1.0 | True |
| OP/13561 (id=5137) | Vrac 1 kg Poupée Russe | 1V0821 | 4030 | consu | 1.0 / 1.0 | True |
| OP/13562 (id=5138) | Vrac 1 kg Ginger Hot | 1V0825 | 4031 | consu | 3.0 / 5.0 | True |
| OP/13563 (id=5139) | Vrac 1kg La nana de Wépion | 1V0832 | 4032 | consu | 1.0 / 2.0 | True |
| OP/13564 (id=5140) | Vrac 1kg Couleur Mojito | 1V0847 | 4033 | consu | 0.0 / 0.0 | True |
| OP/13565 (id=5141) | Vrac 1kg Ginger Cool_ BE-BIO-01 | 1V0848 | 4034 | consu | 0.0 / 0.0 | True |
| OP/13566 (id=5142) | Vrac 1kg Camomille matricaire_ BE-BIO-01 | 1V0854 | 4035 | consu | 1.0 / 3.0 | True |
| OP/13567 (id=5143) | Vrac 1kg Masala Chai | 1V0863 | 4036 | consu | 1.0 / 1.0 | True |
| OP/13568 (id=5144) | Vrac 1kg Citron meringué | 1V0868 | 4037 | consu | 1.0 / 1.0 | True |
| OP/13569 (id=5145) | Vrac 1kg Guarana boost | 1V0878 | 4038 | consu | 1.0 / 1.0 | True |
| OP/13570 (id=5146) | Vrac 1kg Amazônia | 1V0879 | 4039 | consu | 0.0 / 0.0 | True |
| OP/13675 (id=5251) | Sencha - BE-BIO-01 - 50 infusettes | H0626 | 4583 | consu | 44.0 / 56.0 | True |
| OP/13748 (id=5324) | Infusettes Milky Oolong_ BE-BIO-01 | I0843 | 4733 | consu | 9.0 / 17.0 | True |
| OP/28706 (id=13978) | Kit Horeca | KIT01 | 10145 | consu | 2.0 / 4.0 | True |
| OP/35537 (id=18730) | SRP 6x V0279 - Panier de grand maman VRAC | SRPV0279 | 10435 | consu | 50.0 / 150.0 | True |
| OP/35538 (id=18731) | SRP 6x V0631 - Thé des amoureux VRAC | SRPV0631 | 10437 | consu | 50.0 / 150.0 | True |
| OP/35539 (id=18732) | SRP 6x V0880 - Blue Earl grey BIO VRAC | SRPV0880 | 10438 | consu | 50.0 / 150.0 | True |
| OP/35540 (id=18733) | SRP 6x V0735 - Pêches de Vignes BIO VRAC | SRPV0735 | 10439 | consu | 50.0 / 150.0 | True |
| OP/35570 (id=18791) | Coffret assortiment Matcha | C0200 | 10485 | consu | 50.0 / 100.0 | True |
| OP/35571 (id=18792) | Vergers d’Été: saveurs: Pomme - Poire | GI0916 | 10209 | consu | 150.0 / 200.0 | True |

**Total** : 42 OP sans vendor