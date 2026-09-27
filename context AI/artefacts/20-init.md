# Un projet neuf qui ne ment pas — notes et journal
## Lien
https://claude.ai/artifact/8p27CpH1GuMgtE9ECWcwoj
## Résultat
vlp.py renvois rend 0 absent sur un projet neuf posé par l'eval init, qui passe ; 08-etat en dur 7 → 0 dans templates/ et commands/
## Notes
- I1 : test-vlp.py OK (4 cas etat ajoutés) ; 08-etat dans templates/ et commands/ 7 → 0 ; vlp.py etat "context AI" → ETAT=08-etat.md
- I2 : test-vlp.py OK (3 cas renvois) ; vlp.py renvois . sur le kit : 39 nommés · 1 absent → 0 absent ; awk dans init.md 1 → 0 ; /vlp:check gagne H
- I3 : eval init seule : score 1, 25 tours, 0,37 $ ; sur le projet posé, vlp.py renvois → 2 nommés · 0 absents ; fichier posé 01-etat.md = ETAT=01-etat.md
## Journal
- 2026-09-17 : I2 : vlp.py renvois lit la 1re cellule des tables de l'index et la dernière du routage de CLAUDE.md — toutes les cellules prenaient vlp.py, cité dans un intitulé de tâche, pour un fichier. Sur ce kit : 39 nommés, 1 absent (scripts/carte.py, retiré en S) → 0.
## Bilan
- Livré : vlp.py etat nomme le fichier d'état (08-etat en dur 7 → 0) ; vlp.py renvois dans /vlp:check (kit : 39 nommés, 1 → 0 absent) ; eval init score 1, 25 tours, 0,37 $, projet posé sans renvoi mort.
- Surpris : lire toutes les cellules prenait vlp.py, cité dans un intitulé du routage, pour un fichier ; l'eval init a pris 25 tours pour un plafond de 25.
