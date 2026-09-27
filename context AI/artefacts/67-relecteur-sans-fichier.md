# Le relecteur ne lit plus le fichier de fiches entier — notes et journal
## Lien
https://claude.ai/artifact/1gHM68m8ZBH5BNUbdU31Dm
## Résultat
vlp.py relecture ne rend plus FICHIER= ; l'agent vlp:relecture a pour consigne de ne pas ouvrir le fichier de fiches ; rel1-carte.py mesure toujours les lectures, sans FICHIER=.
## Notes
- FFE1 : test-vlp.py OK (code 0) ; mutant FICHIER= remis : ÉCART relecture : un fichier hors fiche, code 1 ; pyright vlp.py + test-vlp.py 0 erreur
- FFE2 : --sans-fichier : 20/20 relecteurs réels au même chemin que FICHIER= ; TOTAL entier 1→0, plage 2→0, grep 0→0 (rejeux REV, carte à 51-relecture.md) ; 3 sans chemin des deux côtés ; pyright 0 errors
## Journal
- 2026-09-26 : FFE2 : sans FICHIER=, rel1-carte.py rate les 19 rejeux REV (carte à 51-relecture.md) ; juste sur les 20 relecteurs réels
## Bilan
- Livré : vlp.py relecture ne rend plus FICHIER= ; l'agent vlp:relecture n'ouvre pas le fichier de fiches ; rel1-carte.py le retrouve par APRÈS= et la carte (--sans-fichier)
- Surpris : sans FICHIER=, rel1-carte.py rate les 19 rejeux REV : leur carte nommait 51-relecture.md, pas le fichier relu
