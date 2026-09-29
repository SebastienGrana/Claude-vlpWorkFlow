# Un seul prix pour un chantier — notes et journal
## Lien
https://claude.ai/artifact/D6EDGTsi9xFkgmf23YxhP7
## Résultat
clore, ouvrir et la feuille de route donnent le prix mesuré de cout — plus de taux plat ; les joués déjà écrits sont recalés, les vieux estimés marqués (taux plat)
## Notes
- TAU1 : test-vlp.py OK (exit 0) ; 2 cas TAU1 : joué 12,34 $ et cellule « 12,34 $ · ≈2,0M (2 000 000) », puis ? $ sans $ en cellule ; couts_clos [('u', 2000000)], moyenne_clos (2000000, 1, 1) ; mutant estimation_usd → ÉCART ; pyright 0 errors
- TAU2 : grep -c estimation_usd|USD_PAR_MTOKENS -> 0 et 0 ; test-vlp.py OK ; mutant (ligne sans $ comptée 0 $) demasque : ÉCART EST1 ; pyright 0 errors
- TAU3 : test-vlp.py OK ; pyright 0 erreur ; mutant (marquer (taux plat) sans regarder) démasqué : ÉCART second passage
- TAU4 : prix . a rejoué 0 posés · 70 déjà · 7 sans prix, feuille . --verifier identique, total 661,15 $ = somme des 70 lignes (dette resommer corrigée), 22 pages republiées (21 chantiers + feuille)
## Journal
## Bilan
- Livré : prix mesuré posé pour clore et republier, plus de taux plat sur le joué ni sur l'estimé ; les 22 pages déjà closes recalées à leur prix réel, la feuille republiée
- Surpris : cmd_prix ne rafraîchissait jamais le résumé/pied de la feuille : figé sur l'ancien calcul au taux plat (≈1092 $) au lieu du mesuré (661,15 $) ; corrigé, testé (mutant), pyright propre
- Estimé : estimé 1 fiches ≈4,42 $ · cadré 4 · joué 4 fiches 20,05 $
