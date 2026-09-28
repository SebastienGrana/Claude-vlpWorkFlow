# La plage de l'en-tête et la dernière fiche — notes et journal
## Résultat
Une plage de fiches se borne par numéro : REV, rangé dans le désordre, s'affiche REV1–REV8 et non plus REV1–REV4, en-tête, feuille, index et CHANTIER.md compris.
## Notes
- PLG1 : bornes(ids) par numéro entier ; plage + 4 plages .. de clore/ouvrir l'appellent, plus aucun ids[-1] ; 4 tests (REV1–REV8, X9–X10, U1, ouvrir Q2,Q1 → Q1..Q2) ; mutant ids[0], ids[-1] : ÉCART ; test-vlp OK ; pyright 0 errors
## Journal
## Bilan
- Livré : bornes(ids) : une plage de fiches va du plus petit au plus grand numéro, en-tête, feuille, index et CHANTIER.md compris
- Surpris : Aucun test existant ne dépendait de l'ordre du fichier : les anciens tests sont passés avant même le test neuf
- Estimé : estimé 0,5 fiches ≈2,12 $ (taux plat) · cadré 1 · joué 1 fiches 1,21 $
