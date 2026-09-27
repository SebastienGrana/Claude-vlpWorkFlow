# Recompter les chantiers clos au coût juste — notes et journal
## Lien
https://claude.ai/artifact/FVUYKGBisHJK5HEv2RmRnB
## Résultat
La feuille de route porte des chiffres comptés d'une seule façon : chaque clos recompté par cout, les dix sans commit de fiche gardés et marqués, le total resommé, et chaque bilan qui change marqué.
## Notes
- REC1 : test-vlp OK, verifier( 290 → 294, deux mutants tombent ; recompter . : RECOMPTE 48 clos · 23 recomptés · 25 gardés · inscrit 681 541 003 · recompté 700 725 374 · écart +19 184 371 ; JUG recompté 11 306 457 = TOTAL de cout ; git status : scripts seuls ; pyright 0 erreur
- REC2 : journal REC2 : sortie brute de recompter et table par cause ; somme des écarts +19 184 371 = écart RECOMPTE +19 184 371 ; FIL session partagée −22 318 909, REP sous-agents avant CPT +9 982 170, cadrage avant CAD 0 clos, autre 21 clos +31 521 110 ; git status : 08-etat.md seul
- REC3 : tests OK, verifier( 294 → 297 ; après --ecrire total_clos = 1 004 499 = recompté de RECOMPTE ; second passage ÉCRIT 0 cellules ; 3 mutants tombent (parenthèses, balise, pied non resommé) ; pyright 0 errors
- REC4 : ÉCRIT 48 cellules · total 681 541 003 → 700 725 374 ; second passage ÉCRIT 0 ; pied de la feuille 700 725 374 = recompté de RECOMPTE ; bilans marqués 22 = clos à écart non nul citant leur chiffre 22 (23 à écart, H sans chiffre) ; feuille identique, NIVEAU 0 écarts · 2 avertissements (poids CLAUDE.md, index, d'avant) ; feuille de route republiée, version 110
## Journal
- 2026-09-25 : REC1 : 23 clos en DÉCOUPE aucune, pas dix (plus V sans session, E sans plage à l'index) ; FIL −22 318 909 et REP +9 982 170 sortent du lot
- 2026-09-25 : REC2 : 17 recomptés ont leurs fiches inchangées au token près ; tout leur écart est dans hors fiches — la cause n'est pas la session partagée, que 13 d'entre eux portent
## Bilan
- Livré : la feuille de route recomptée par cout : 23 clos recomptés, 25 gardés et marqués non recomptés, total 681 541 003 → 700 725 374 ; 22 bilans marqués (recompté par REC)
- Surpris : 17 recomptés ont leurs fiches inchangées au token près, tout l'écart est dans hors fiches ; FIL perd 22 318 909 tokens, sa session partagée avec SAG
