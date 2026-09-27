# Des boutons sur les pages — notes et journal
## Résultat
Les pages du kit ont des boutons : tout déplier, copier la commande d'une fiche, filtrer la feuille par état, et un graphique du coût des chantiers clos. La page relue à chaque fiche ne grossit que de quelques balises.
## Notes
- BTN1 : vlp.js joint et copié par vlp.py, ligne FILES, charset en tête des gabarits ; ne dépend de rien
- BTN2 : les 7 files: vlp.css des commandes pointent vers la ligne FILES ; dépend de BTN1
- BTN3 : boutons Tout déplier et Copier la commande ; dépend de BTN1 ; visuel
- BTN4 : filtre de la feuille par état : à faire, en cours, clos ; dépend de BTN1 ; visuel
- BTN5 : couts.svg, une barre par chantier clos, écrit par vlp.py ; dépend de BTN1
- BTN6 : régénérer et republier kit, Cairn et BTN, mesurer avant et après ; dépend de toutes ; visuel
## Journal
## Bilan
