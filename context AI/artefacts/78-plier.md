# La page de chantier plus courte et lisible — notes et journal
## Résultat
La page d'un chantier se replie : fiches finies et vieux journal repliés, bilan en haut une fois clos, rien de coupé ; son CSS vit dans un vlp.css joint. Mesuré avant/après en écrans et en tokens de relecture.
## Notes
- PLI1 : Hauteur en écrans et tokens d'un read de la page REV, avant tout changement
- PLI2 : templates/vlp.css, gabarits en <link>, recopié à chaque page/feuille
- PLI3 : Une page régénérée perd son <style> pour le <link> · dépend de PLI2
- PLI4 : Chaque publication joint vlp.css par files · dépend de PLI2
- PLI5 : Chaque fiche repliable, ouverte si en cours · dépend de PLI3
- PLI6 : Journal : 3 dernières visibles ; bilan en haut si clos · dépend de PLI5
- PLI7 : Mesure après, feuille du kit republiée, affichage constaté · dépend de PLI1, PLI4, PLI6
## Journal
## Bilan
