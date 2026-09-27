# Ouvrir et clore par script — notes et journal
## Lien
https://claude.ai/artifact/Srsfk2hqchvLPSuQ6BXc9e
## Résultat
Une ouverture et une clôture ne gardent à la main que les publications Artifact et le texte de jugement ; tours à la main comptés avant (O1) et après (O5).
## Notes
- O1 : Mesuré : à la main, F 12 tours sur 64 (ouverture 7, clôture 5), X 8 sur 77 (5, 3), O ouverture 7 sur 20 ; 0 refus. Formats réels relevés, O2/O3 recalés.
- O2 : vlp.py ouvrir : tests OK, 73 → 81 assertions ; bac copié : grep -c 0 → 1 pour CLAUDE.md, index, CHANTIER.md, les trois identiques au vrai ; relance : diff -r vide.
- O3 : clore étendu : tests OK, 81 → 87 assertions ; bac copié : routage clos 20 → 21, index clos 20 → 21, section hidden 2 → 1 ; Fait. remplace Où on en est ; bilan gardé par page.
- O4 : clore --resume : tests OK, 87 → 91 assertions (même date, autre date, déjà là, section absente) ; bac copié : (chantier O) 0 → 1 dans CLAUDE.md, chaîne du jour prolongée.
- O5 : Branché : /vlp:chantier 279 → 270 lignes (ouvrir + feuille en un appel), cloture.md 83 → 74 (4 temps) ; plugin 3.3.5 ; validate OK (1 avertissement voulu), RENVOIS 60 · 0 absent, eval chantier WSL2 3/3 (5 tours, 0,29 $).
## Journal
## Bilan
- Livré : vlp.py ouvrir et clore étendu écrivent index, routage et Où on en est de CLAUDE.md, CHANTIER.md, Fait. et ZONE:bilan ; branchés dans /vlp:chantier et cloture.md ; plugin 3.3.5, tests 73 → 91, eval chantier 3/3 (8,25 $, plus 0,29 $ d'eval).
- Surpris : L'index n'est pas trié par numéro (25, 21, 20 après 29) : ouvrir insère après le plus grand numéro. Ce fichier-ci portait Où on en est au lieu de Fait. : clore remplace les deux. Avant : 12 tours sur 64 (F) et 8 sur 77 (X) passés à la main.
