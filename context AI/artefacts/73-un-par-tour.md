# Le filet n'avertit qu'une fois par tour — notes et journal
## Lien
https://claude.ai/artifact/4UNShx5pLGhqsSFxZ7H5u3
## Résultat
L'eval filet-rate rejouée à plafond 5 montre au plus un avertissement par tour, là où RAT1 en comptait 13 dans le même tour ; un test et ses mutants le gardent.
## Notes
- TOU1 : test + mutant (AVERTIS_PAR_TOUR=1:4 le fait tomber) ; eval filet-rate plafond 5 : TOURS=4, AVERTISSEMENTS=13, AVERTIS_PAR_TOUR=2:12,3:1, 0,155 $ — clé de TOU2 confirmée
- TOU2 : test-vlp.py : OK, code 0, 0 écart ; mutant sans tampon et mutant clé sans le tour tombent chacun sur leur test ; pyright 0 errors
- TOU3 : Plafond 5 : AVERTISSEMENTS=3, AVERTIS_PAR_TOUR=2:1,3:1,4:1 (TOU1 : 13, 2:12,3:1). Plafond 80 : AVERTISSEMENTS=0. Eval 0,144 $ chacune.
## Journal
## Bilan
- Livré : Le filet n'avertit plus qu'une fois par tour : filet-rate à plafond 5 passe de 13 avertissements (2:12,3:1) à 3 (2:1,3:1,4:1), témoin 80 à 0
- Surpris : rejouer.sh sous WSL demande bash -lc (sinon claude introuvable) ; HOOK_ERREURS=4 dans les deux rejeux
- Estimé : estimé 0,5 fiches ≈2,01 $ · cadré 3 · joué 3 fiches ≈5,86 $
