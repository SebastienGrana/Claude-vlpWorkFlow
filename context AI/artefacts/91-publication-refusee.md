# Une publication refusée n'arrête plus le chantier — notes et journal
## Résultat
Une page refusée par la limite du jour attend dans une liste et part plus tard, sans bloquer ni case ni clôture ; on la relit en local, sans cache, en largeur téléphone.
## Notes
- LOC1 : 4 résultats Artifact en 429 sur 223 occurrences brutes hors session (269 avec) ; événement PostToolUseFailure, champ error ; cause du blocage : prompt et critère (visuel) de BTN6 ; VALIDE
- LOC2 : suite OK (exit 0) ; 5 mutants tombent, témoin OK ; pyright 0 erreur ; hook essayé en sous-processus : proposition 02:00 / 02:10 une fois
- LOC3 : La règle dans ARTEFACTS.md, les commandes y renvoient et republient la liste (après LOC2)
- LOC4 : vlp.py apercu et servir : launch.json écrit par script, hors du dépôt (indépendante)
- LOC5 : Essai réel, visuel : liste vidée par le hook, page à 375 px sans cache (après LOC3, LOC4)
## Journal
- 2026-09-29 : LOC2 : la liste ne tient que les pages sous artefacts/ ; les pages Cairn du scratchpad (3 refus du 2026-09-27) n'y entrent pas, le hook se tait ; le champ error est à vérifier en vrai par LOC5
## Bilan
