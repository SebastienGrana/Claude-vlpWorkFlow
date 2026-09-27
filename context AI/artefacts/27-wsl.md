# Evals sous WSL2 — notes et journal
## Lien
https://claude.ai/artifact/BTzA23mPmYQKAnUvT1Pkpd
## Résultat
Les cas d'eval tache et chantier joués depuis Ubuntu sous WSL2, avec graders, tours et coût relevés
## Notes
- W1 : Ubuntu 26.04.1 : claude 2.1.274, bubblewrap 0.11.1, socat 1.8.1.1 ; loggedIn true (claude.ai) ; AppArmor sans objet
- W2 : Sous Ubuntu : chantier 3/3 (5 tours, 0,27 $) ; tache 2/3 puis 3/3 après fixture corrigée (4 tours, 0,20 $ chacun) ; 0,67 $ d'evals sur 3 $
## Journal
- 2026-09-17 : W2 : le cas tache échouait par sa fixture (T2 dépendait de T1 non cochée), pas par la skill ; dépendance retirée, 3/3.
## Bilan
- Ubuntu 26.04.1 sous WSL2 (Claude Code 2.1.274, bubblewrap 0.11.1, socat 1.8.1.1) ; les cas d'eval wsl2 joués depuis Linux : chantier 3/3 (5 tours), tache 3/3 (4 tours) après une fixture corrigée — T2 dépendait de T1 non cochée, la skill demandait à raison ; 0,67 $ d'evals.
- Ce qui a surpris : le seul échec venait du cas, écrit sous Windows et jamais joué ; et le terminal ouvert avant l'installation ne voyait pas claude (exec bash -l).
