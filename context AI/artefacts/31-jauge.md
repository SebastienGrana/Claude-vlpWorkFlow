# Des fichiers de tête qui ne grossissent plus — notes et journal
## Lien
https://claude.ai/artifact/CHfV4GdKDQ35zXxFa5FbR8
## Résultat
CLAUDE.md et CHANTIER.md du kit sous leur seuil de vlp.py, et une clôture simulée n'y ajoute plus de ligne
## Notes
- J1 : 8 clôtures mesurées : CLAUDE.md +2 lignes/chantier (103 → 117), CHANTIER.md +1 (64 → 71), index +1 (53 → 60) ; gain estimé ≈ 0,1 $/session ; seuils 80/50/80, 5 clos gardés
- J2 : tests OK, assertions 92 → 94 ; renvois . : POIDS CLAUDE.md 118/80 · CHANTIER.md 71/50 · index 61/80, 2 AVERTISSEMENT (pas 3 : index sous seuil), RENVOIS 62 nommés · 0 absents, exit 0
- J3 : tests OK, 94 → 96 ; copie compactée (CLAUDE.md 118 → 75, CHANTIER.md 71 → 47) : avant ouvrir 74/47/61, après clore 74/47/62 (écart 0/0/+1) ; relance clore et ouvrir refusées, diff -r vide ; valider VALIDE ; trou trouvé : ouvrir rouvrait un fichier CLOS, refusé désormais
- J4 : POIDS CLAUDE.md 118 → 80/80 · CHANTIER.md 71 → 47/50 · index 61/80, 0 avertissement ; RENVOIS 42 nommés · 0 absents ; validate OK (1 avertissement voulu) ; feuille identique ; plugin 3.3.6 ; eval chantier non rejouée (skills/chantier inchangé)
## Journal
## Bilan
- Livré : Seuils des fichiers de tête dans vlp.py (renvois écrit POIDS), clore et ouvrir compactent ; CLAUDE.md 118 → 80, CHANTIER.md 71 → 47 ; plugin 3.3.6, tests 92 → 96 (6,83 $ à la mesure)
- Surpris : le gain en dollars est petit (≈ 0,1 $ par session) ; ouvrir rouvrait un fichier CLOS, trou trouvé par la relance
