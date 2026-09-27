# Ce que le chiffre de clôture ne voit pas — notes et journal
## Lien
https://claude.ai/artifact/X4cHWn5EP1baX4WcFSCnr7
## Résultat
Le chiffre que clore inscrit égale celui que cout recompte ensuite ; l'écart d'ESD et des 19 clos est expliqué, cause par cause, en comptes bruts.
## Notes
- APC1 : test-vlp.py OK (code 0) ; mutant sans borne : ÉCART, à clore = TOTAL 400 000 · 4 tours (code 1) ; cout --a-clore sur ESD : à clore 16 735 386 · 198 tours = inscrit 16 735 386 (écart 0) ; après clore 1 771 130 · 8 tours ; reste non expliqué 0
- APC2 : Tests OK (code 0), mutant tombé (code 1) ; table APC2 : 5 entièrement + 14 en partie + 0 pas du tout = 19, 0 sans appel clore ; choix (b) écrit au socle
- APC3 : Tests OK (code 0) ; mutant sans arrêt à clore : ÉCART, recompté 400 000 contre 300 000 inscrit (code 1) ; test : clore inscrit 300 000 = TOTAL cout 300 000 · 3 tours ; ESD : TOTAL 18 506 516 → 16 735 386, après clore 1 771 130 → 0 ; pyright scripts/ 0 → 0 erreur
## Journal
## Bilan
- Livré : le chiffre de clôture égale le recompté : la recompte d'un clos s'arrête à l'appel clore ; recompter --a-clore décompose l'écart des 19 clos
- Surpris : 14 des 19 clos gardent un reste de 10 952 704 que l'après-clore n'explique pas : leur inscrit est sous ce que clore voyait
