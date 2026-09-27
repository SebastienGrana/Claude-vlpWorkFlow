# Le relecteur ne voit pas la suite — notes et journal
## Lien
https://claude.ai/artifact/8TvYiEvHBwzuDBmyVTJVxK
## Résultat
Le relecteur reçoit une carte sans titres de fiches ni PROCHAINE= : un test et son mutant le prouvent, et la skill vlp:relire l'injecte.
## Notes
- REL1 : rel1-carte.py : 42 lignes = 42 vlp:relecture de forme ; TOTAL autres 56 (15) · prochaine 1 (1) · libelles 54 (11) · entier 1 (1) · plage 2 (1) · grep 0
- REL2 : test-vlp.py OK (verifier( 331 → 335), test_carte_relecteur ; mutant « option ignorée » → ÉCART ; carte sans option identique à l'octet ; pyright scripts/ 0 erreur
- REL3 : --relecteur : 3 occurrences sur 1 ligne dans relire (grep -c 1, grep -o 3), 0 dans jouer et enchainer ; ligne injectée dans un bac : 0 titre · 1 PROJET= · 0 PROCHAINE=
## Journal
## Bilan
- Livré : le relecteur reçoit une carte sans titres de fiches ni PROCHAINE= (vlp.py carte --relecteur, injecté par vlp:relire) ; test et mutant
- Surpris : 15 relecteurs sur 42 citaient les titres d'autres fiches ; la ligne fichier de fiches courant donne encore l'étendue (REL1..REL3) ; 1 relecteur a lu le fichier de fiches entier (TODO 70 FFE)
