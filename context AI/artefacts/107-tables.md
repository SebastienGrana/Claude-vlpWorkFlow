# Les tables de vlp.py ne se coupent plus en silence — notes et journal
## Résultat
Une table Markdown mal découpée rend une GARDE au lieu d'une coupe muette ; clore lit la TODO avant d'écrire ; vlp.py oter retire une ligne de la TODO.
## Notes
- TAB1 : Entrée TAB1 au journal : 12 lecteurs relevés, 1 qui tronque (noms_de_table), 3 gardes, 8 sans effet, 0 jette ; git diff --stat scripts/ vide
- TAB2 : MUTANT ATTRAPÉ (cellules_de tolérante) ; rapide 6 contrôles verts ; suite entière code 0, 0 ÉCART ; pyright 0 errors ; RENVOIS 129 nommés · 0 absents, inchangé
- TAB3 : Reproduit : GARDE … CHANTIER.md et fiches écrits, feuille non écrite ; après : GARDE … rien écrit, sort 1, empreintes identiques ; TODO saine passe ; MUTANT ATTRAPÉ ; suite code 0, 0 ÉCART ; pyright 0 errors
- TAB4 : 6 contrôles : rangée ôtée, numéro marqué, journal ; absent, ouvert, clos → GARDE, sort 1, fichier inchangé ; MUTANT ATTRAPÉ (refus du clos sauté) ; sur le kit, oter TAB → GARDE chantier ouvert ; suite code 0, 0 ÉCART ; pyright 0 errors
## Journal
## Bilan
