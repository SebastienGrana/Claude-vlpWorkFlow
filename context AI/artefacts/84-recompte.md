# Comprendre les écarts du recompte avant de l'écrire — notes et journal
## Résultat
Les 24 écarts de recompter ont chacun leur cause ; les deux défauts de mesure trouvés sont réparés, puis le recompte est écrit sur la feuille de route.
## Notes
- ECA1 : lance_clore : interprète Python en tête de segment, heredocs cat/tee tus (sans_heredoc sorti de ecrit_git) ; 13 cas ; mutants ancien motif (5 textes pris) et sans sans_heredoc : ÉCART ; recompter : BAC, EST, FFE, REL écart 0 ; corpus 82 appels gardés, 20 textes écartés ; test-vlp OK ; pyright 0 errors
- ECA2 : plages(clos) : la fiche sans commit d'un clos s'arrête au premier commit suivant qui nomme le préfixe ; heure_clore passe clos=True, parts_aux_commits clos=fin is not None ; test Q2 2 tours, TOTAL 400 000 · 4 tours ; mutant clos ignoré : 700 000 · 7 tours, ÉCART ; recompter : LEC écart 0, 0 positif, 19 négatifs = −15 390 303 ; test-vlp OK ; pyright 0 errors
## Journal
## Bilan
