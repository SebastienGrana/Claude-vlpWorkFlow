# Un bac d'essai par script — notes et journal
## Lien
https://claude.ai/artifact/MGhXaCPyDFwXztJrPRuKFd
## Résultat
vlp.py bac pose le bac en un appel ; vlp.py transcription retrouve, sur les deux vraies transcriptions de FIL3, les chiffres de son journal
## Notes
- BAC1 : test-vlp.py OK ; valider sort 0 (VALIDE 2 fiches, 0 écarts) ; extraire F1/F2 non vides ; 12 n*.txt ; « un appel par message » 2 (grep -o | wc -l) ; claude -p 2 ; 2e appel GARDE, code 1 ; mutant sans « L'ordre des fiches » → ÉCART ; pyright 0 errors
- BAC2 : test OK, 2 mutants tombent ; rejeu F1/F2 : TOURS=8, 7 appels, averti tour 7 (Read non / Bash oui), HOOK_ERREURS=7 pour 7, RETOUR end_turn — sans écart avec FIL3 ; pyright 0 errors
## Journal
## Bilan
- Livré : vlp.py bac pose le bac d'essai de FIL3 en un appel ; vlp.py transcription compte la transcription d'un sous-agent et retrouve, sur F1 et F2, les chiffres du journal FIL3
- Surpris : rien : le rejeu tombe juste du premier coup, is_error absent sur un Read réussi vaut non
- Estimé : estimé 1 fiches ≈3,90 $ · cadré 2 · joué 2 fiches ≈6,82 $
