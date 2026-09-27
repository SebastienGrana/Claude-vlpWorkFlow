# Repeindre une page sans recompter — notes et journal
## Résultat
Les 90 pages de chantiers clos (kit et Cairn) au format PLI, chiffres de coût inchangés, remises en ligne par lots ; les pages sans lien listées.
## Notes
- HAB1 : Test tester_forme : après --forme, total 11 262 523, hors 5 000 et coûts 1 111 / 2 222 identiques ; vlp.css lié, fiches repliées, bilan en haut, vigile PAGE SAINE ; --creer refusé ; mutant --forme ignoré → le test du total tombe ; pyright 0 erreur.
- HAB2 : vlp.py repeindre : toutes les pages closes d'un projet, vigile sur chacune ; dépend de HAB1.
- HAB3 : Le lien en ligne rangé dans le .md de chaque page, retrouvé par la liste des artefacts et Git ; dépend de HAB2.
- HAB4 : Le kit repeint, un 1er lot de 15 en ligne, coût mesuré ; critère visuel ; dépend de HAB3.
- HAB5 : Les lots suivants du kit, taille fixée par HAB4.
- HAB6 : Cairn repeint et remis en ligne, rien de son contenu dans le kit ; dépend de HAB4.
## Journal
## Bilan
