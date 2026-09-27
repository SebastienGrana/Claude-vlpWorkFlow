# Des boutons sur les pages — notes et journal
## Résultat
Les pages du kit ont des boutons : tout déplier, copier la commande d'une fiche, filtrer la feuille par état, et un graphique du coût des chantiers clos. La page relue à chaque fiche ne grossit que de quelques balises.
## Notes
- BTN1 : test-vlp.py OK, 15 contrôles BTN1 (16 joués) ; mutants : vlp.js retiré de recopier_joints → (a) tombe ; balise posée sans vérifier → (c) tombe (bloc seul ; suite entière : tombe d'abord sur « page : régénérer deux fois ne change rien ») ; pyright 0 erreur (1 avant de ranger les aides dans la fonction)
- BTN2 : grep 'files: vlp.css' → 0 ligne ; FILES : chantier 2, enchainer 1, init 1, tache 1, cloture 1, ARTEFACTS 2 ; test-vlp.py OK (code 0, 500 verifier)
- BTN3 : UTF-8 ; Tout déplier 7/7 puis 0 (BTN et feuille) ; 5 Copier pour 5 fiches non faites ; clic → « Sélectionné : fais Ctrl+C » (presse-papiers refusé dans l'app), fiche non repliée ; 375 px : 375/375 (page enveloppée) ; mutant boucle retirée → 1→1 et 0→0 ; vu par l'utilisateur
- BTN4 : Feuille régénérée, javascript_tool : À faire 5/6 cartes, #clos masqué ; En cours 1/6, #encours visible ; Clos : #todo masqué, details.clos ouvert ; Tout 6/6, replis rendus. 375 px (cadre) : scrollWidth = clientWidth = 360 sous les 4 filtres. Mutant « À faire » sans badge : 6/6, il tombe.
- BTN5 : test-vlp.py OK (code 0), 9 contrôles BTN5 : 3 barres en 1:2:4, la plus récente à droite, FILES nomme couts.svg, balise une fois, feuille sans coût ni fichier ni balise ; mutants hauteur constante et ordre non retourné → tombent ; pyright 0 erreur (1 avant de ranger les tests dans tester_joints)
- BTN6 : régénérer et republier kit, Cairn et BTN, mesurer avant et après ; dépend de toutes ; visuel
- BTN7 : test-vlp.py OK (code 0), 3 contrôles BTN7 : décompte <p class=resume-todo><strong>…</strong> · …</p> sans style=, un seul après deux feuille ; details.lecture fermé une fois, comparer 0 perdus, 2e feuille inchangée ; sans préambule aucun ; FEU3 sans retouche ; mutants details sans vérifier → (b) tombe, RESUME_TODO sans l'ancienne forme → (a) tombe ; pyright 0 erreur
## Journal
- 2026-09-27 : BTN1 : même une aide ou une constante au niveau du module fait tomber pyright sur test-vlp.py (Code is too complex to analyze) — les aides d'un test vont dans sa fonction tester_<nom>().
- 2026-09-27 : BTN7 ajoutée (choix A1, sur un commentaire de la feuille du kit et une remarque sur celle de Cairn) : décompte mis en valeur, texte d'avant la liste replié ; jouée avant BTN6, qui republie les feuilles une seule fois.
- 2026-09-27 : clore n'écrit pas de ligne FILES : cloture.md prend celle de clore, sinon celle de vlp.py joints ; BTN5 rend ce repli inutile.
- 2026-09-27 : BTN3 : une page servie en local telle quelle mesure 980 px de large à 375 × 812 (pas de meta viewport dans les gabarits ; claude.ai l'ajoute lui-même) — mesurer la largeur sur une copie enveloppée (38-audit-scripts/replie.py:25-27), comme FEU et PLI : là, 375 = 375. Vaut pour BTN4 et BTN6.
## Bilan
