# Un seul prix pour un chantier — notes et journal
## Résultat
clore, ouvrir et la feuille de route donnent le prix mesuré de cout — plus de taux plat ; les joués déjà écrits sont recalés, les vieux estimés marqués (taux plat)
## Notes
- TAU1 : test-vlp.py OK (exit 0) ; 2 cas TAU1 : joué 12,34 $ et cellule « 12,34 $ · ≈2,0M (2 000 000) », puis ? $ sans $ en cellule ; couts_clos [('u', 2000000)], moyenne_clos (2000000, 1, 1) ; mutant estimation_usd → ÉCART ; pyright 0 errors
- TAU2 : l'estimé et le total de la feuille lisent ce prix ; la constante 0,8371 disparaît ; après TAU1
- TAU3 : vlp.py prix remplit les anciennes lignes et recale les anciens joués ; après TAU1
- TAU4 : le kit passé au prix mesuré, feuille et pages republiées ; après TAU2 et TAU3
## Journal
## Bilan
