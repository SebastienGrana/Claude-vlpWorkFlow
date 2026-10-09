# Les tables de vlp.py ne se coupent plus en silence — notes et journal
## Résultat
Une table Markdown mal découpée rend une GARDE au lieu d'une coupe muette ; clore lit la TODO avant d'écrire ; vlp.py oter retire une ligne de la TODO.
## Notes
- TAB1 : Entrée TAB1 au journal : 12 lecteurs relevés, 1 qui tronque (noms_de_table), 3 gardes, 8 sans effet, 0 jette ; git diff --stat scripts/ vide
- TAB2 : MUTANT ATTRAPÉ (cellules_de tolérante) ; rapide 6 contrôles verts ; suite entière code 0, 0 ÉCART ; pyright 0 errors ; RENVOIS 129 nommés · 0 absents, inchangé
- TAB3 : clore refuse une TODO cassée avant d'écrire, test et mutant ; sans dépendance.
- TAB4 : La sous-commande oter, test et mutant ; sans dépendance.
## Journal
## Bilan
