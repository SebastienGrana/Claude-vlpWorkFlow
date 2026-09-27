# Fusionner la doctrine — notes et journal
## Lien
https://claude.ai/artifact/Pnfr1vfuHWiqM4XHuFP8Eh
## Résultat
Trois docs à la racine (README, méthode, ARTEFACTS) ; chaque seuil dans vlp.py seul, chaque règle dans la méthode seule — comptes bruts avant/après, evals 3/3
## Notes
- D1 : test-vlp.py OK, verifier() 45 → 47 ; grep ARTEFACTS dans vlp.py : 0 ligne ; SEUIL_SOCLE = 80 avertit
- D2 : grep CONVENTION-FICHIERS hors context AI/archive/exemples : rien ; méthode 202 lignes (127 + 121 = 248 avant) ; tests OK
- D3 : grep INSTALLATION|TLDR hors context AI/archive/exemples : rien ; README 141 lignes (162 + 163 + 73 = 398 avant)
- D4 : grep 250|comptes bruts|un seul endroit : 2 lignes, deux renvois à la méthode (cloture:40, enchainement:8) ; lignes 148+102+15 = 265 → 118+101+14 = 233
- D5 : grep 250|80 lignes dans commands et templates : rien ; commands 274/122/146/179/151 = 872 → 273/120/145/179/151 = 868 ; tests OK
- D6 : motifs : 250 6 → 1 fichier (vlp.py), 80 lignes 2 → 1 (test-vlp.py), comptes bruts 9 → 10 (ordres d'agir), un seul endroit|une seule fois 5 → 3 ; validate propre ; evals 3/3, 40 tours, 0,55 $ (V4 : 39 tours, 0,93 $)
## Journal
- 2026-09-17 : D1 jouée par /vlp:enchainer : sous-agent fiche (haiku, maxTurns 8) coupé 3 fois ; D2→D5 à jouer à la main via /vlp:tache
## Bilan
- Livré : trois docs à la racine (README 141 lignes, 398 avant ; méthode 202, 248 avant ; ARTEFACTS) ; chaque seuil dans vlp.py seul (250 : 6 fichiers → 1) ; validate propre, evals 3/3, 40 tours, 0,55 $.
- Surpris : /vlp:enchainer a joué D1 avec un sous-agent coupé 3 fois à 8 tours ; D2 à D6 jouées à la main.
