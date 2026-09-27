# Repeindre une page sans recompter — notes et journal
## Résultat
Les 90 pages de chantiers clos (kit et Cairn) au format PLI, chiffres de coût inchangés, remises en ligne par lots ; les pages sans lien listées.
## Notes
- HAB1 : Test tester_forme : après --forme, total 11 262 523, hors 5 000 et coûts 1 111 / 2 222 identiques ; vlp.css lié, fiches repliées, bilan en haut, vigile PAGE SAINE ; --creer refusé ; mutant --forme ignoré → le test du total tombe ; pyright 0 erreur.
- HAB2 : Test tester_repeindre : 3 clos (2 anciens, 1 au format) → 2 repeintes · 0 avec lien · 2 sans lien · 0 refusées · 1 déjà ; relancé 0 repeintes ; --a-blanc 0 octet changé ; mutant sans filtre → tombe ; parcours commun clos_du_projet avec recompter. À blanc : kit 64 repeintes, 3 déjà, 1 sans page ; Cairn 17, 2 déjà. pyright 0.
- HAB3 : Le lien en ligne rangé dans le .md de chaque page, retrouvé par la liste des artefacts et Git ; dépend de HAB2.
- HAB4 : Le kit repeint, un 1er lot de 15 en ligne, coût mesuré ; critère visuel ; dépend de HAB3.
- HAB5 : Les lots suivants du kit, taille fixée par HAB4.
- HAB6 : Cairn repeint et remis en ligne, rien de son contenu dans le kit ; dépend de HAB4.
## Journal
## Bilan
