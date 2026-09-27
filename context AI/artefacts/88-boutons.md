# Des boutons sur les pages — notes et journal
## Résultat
Les pages du kit ont des boutons : tout déplier, copier la commande d'une fiche, filtrer la feuille par état, et un graphique du coût des chantiers clos. La page relue à chaque fiche ne grossit que de quelques balises.
## Notes
- BTN1 : test-vlp.py OK, 15 contrôles BTN1 (16 joués) ; mutants : vlp.js retiré de recopier_joints → (a) tombe ; balise posée sans vérifier → (c) tombe (bloc seul ; suite entière : tombe d'abord sur « page : régénérer deux fois ne change rien ») ; pyright 0 erreur (1 avant de ranger les aides dans la fonction)
- BTN2 : grep 'files: vlp.css' → 0 ligne ; FILES : chantier 2, enchainer 1, init 1, tache 1, cloture 1, ARTEFACTS 2 ; test-vlp.py OK (code 0, 500 verifier)
- BTN3 : boutons Tout déplier et Copier la commande ; dépend de BTN1 ; visuel
- BTN4 : filtre de la feuille par état : à faire, en cours, clos ; dépend de BTN1 ; visuel
- BTN5 : couts.svg, une barre par chantier clos, écrit par vlp.py ; dépend de BTN1
- BTN6 : régénérer et republier kit, Cairn et BTN, mesurer avant et après ; dépend de toutes ; visuel
- BTN7 : décompte en gras et plus grand, style dans vlp.css ; texte d'avant la liste replié (Cairn 177 mots) ; ajoutée sur commentaire (A1) ; ne dépend de rien
## Journal
- 2026-09-27 : BTN1 : même une aide ou une constante au niveau du module fait tomber pyright sur test-vlp.py (Code is too complex to analyze) — les aides d'un test vont dans sa fonction tester_<nom>().
- 2026-09-27 : BTN7 ajoutée (choix A1, sur un commentaire de la feuille du kit et une remarque sur celle de Cairn) : décompte mis en valeur, texte d'avant la liste replié ; jouée avant BTN6, qui republie les feuilles une seule fois.
- 2026-09-27 : clore n'écrit pas de ligne FILES : cloture.md prend celle de clore, sinon celle de vlp.py joints ; BTN5 rend ce repli inutile.
## Bilan
