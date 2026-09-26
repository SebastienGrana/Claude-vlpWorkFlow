# La page de chantier plus courte et lisible — notes et journal
## Résultat
La page d'un chantier se replie : fiches finies et vieux journal repliés, bilan en haut une fois clos, rien de coupé ; son CSS vit dans un vlp.css joint. Mesuré avant/après en écrans et en tokens de relecture.
## Notes
- PLI1 : grep ^## Mesures : 1 ; 51-relecture avant : 2977 px = 3,45 écrans (1536 × 864) ; Artifact read : ctx 92 462 → 100 257 = 7 795 tokens
- PLI2 : test-vlp.py OK (0 echec) ; pyright vlp.py+test-vlp.py 0 erreur ; grep -c style-tag sur les deux gabarits : 0 et 0
- PLI3 : test-vlp.py OK (0 echec) ; pyright vlp.py+test-vlp.py 0 erreur ; grep -c "details.clos {" scripts/vlp.py = 0
- PLI4 : vlp.css par fichier (publiantes/mentions) : ARTEFACTS 9/3, chantier 4/2, init 4/1, enchainer 2/1, tache 2/1, cloture 4/2 ; renvois 0 absents ; pre-commit exit 0
- PLI5 : Chaque fiche repliable, ouverte si en cours · dépend de PLI3
- PLI6 : Journal : 3 dernières visibles ; bilan en haut si clos · dépend de PLI5
- PLI7 : Mesure après, feuille du kit republiée, affichage constaté · dépend de PLI1, PLI4, PLI6
## Journal
## Bilan
