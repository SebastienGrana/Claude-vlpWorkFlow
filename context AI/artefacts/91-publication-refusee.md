# Une publication refusée n'arrête plus le chantier — notes et journal
## Résultat
Une page refusée par la limite du jour attend dans une liste et part plus tard, sans bloquer ni case ni clôture ; on la relit en local, sans cache, en largeur téléphone.
## Notes
- LOC1 : 4 résultats Artifact en 429 sur 223 occurrences brutes hors session (269 avec) ; événement PostToolUseFailure, champ error ; cause du blocage : prompt et critère (visuel) de BTN6 ; VALIDE
- LOC2 : suite OK (exit 0) ; 5 mutants tombent, témoin OK ; pyright 0 erreur ; hook essayé en sous-processus : proposition 02:00 / 02:10 une fois
- LOC3 : titre 1 (ARTEFACTS.md:92) ; renvois grep -o : ARTEFACTS 1, cloture 1, chantier 2, tache 1, tache-page 1, init 1 ; phrase d'échec restante seulement hors refus (liste au compte rendu) ; renvois : 0 nouvel avertissement (CLAUDE.md 81/80 déjà là, non touché) ; test-vlp.py : OK code 0
- LOC4 : suite OK (grep -c 'verifier(' : 576 → 593, +17 contrôles), pyright 0 erreur avant et après, 3 mutants tombent (en-tête no-store retiré, check-ignore ignoré, remplacer = ajouter), git ls-files .claude/ = 0 ligne, servir lancé pour de vrai : 200, Cache-Control: no-store, cadre 375 px
- LOC5 : Essai réel, visuel : liste vidée par le hook, page à 375 px sans cache (après LOC3, LOC4)
## Journal
- 2026-09-29 : LOC2 : la liste ne tient que les pages sous artefacts/ ; les pages Cairn du scratchpad (3 refus du 2026-09-27) n'y entrent pas, le hook se tait ; le champ error est à vérifier en vrai par LOC5
## Bilan
