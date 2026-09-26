# La page de chantier plus courte et lisible — notes et journal
## Résultat
La page d'un chantier se replie : fiches finies et vieux journal repliés, bilan en haut une fois clos, rien de coupé ; son CSS vit dans un vlp.css joint. Mesuré avant/après en écrans et en tokens de relecture.
## Notes
- PLI1 : grep ^## Mesures : 1 ; 51-relecture avant : 2977 px = 3,45 écrans (1536 × 864) ; Artifact read : ctx 92 462 → 100 257 = 7 795 tokens
- PLI2 : test-vlp.py OK (0 echec) ; pyright vlp.py+test-vlp.py 0 erreur ; grep -c style-tag sur les deux gabarits : 0 et 0
- PLI3 : test-vlp.py OK (0 echec) ; pyright vlp.py+test-vlp.py 0 erreur ; grep -c "details.clos {" scripts/vlp.py = 0
- PLI4 : vlp.css par fichier (publiantes/mentions) : ARTEFACTS 9/3, chantier 4/2, init 4/1, enchainer 2/1, tache 2/1, cloture 4/2 ; renvois 0 absents ; pre-commit exit 0
- PLI5 : test-vlp.py OK ; tester_fiches_repliees : 3 blocs, 1 ouvert (en cours), comparer 0 perdus, ancienne forme lue ; mutants tout ouvrir et nouvelle forme seule : tombent ; pyright 0 erreur
- PLI6 : test-vlp.py OK ; journal 7 → 3 visibles + 4 repliées, abri 7 dans l'ordre ; 2 → aucun bloc ; bilan avant les fiches après clore ; 2 mutants tombent ; pyright 0 erreur
- PLI7 : Replié 3,45 → 2,18 écrans (2977 → 1886 px), déplié 3,63 ; Artifact read 7 795 → 5 842 tokens (−25 %) ; comparer 0 ligne perdue ; feuille republiée v153 avec vlp.css, pages vues stylées par l'utilisateur ; page jetable supprimée
## Journal
## Bilan
