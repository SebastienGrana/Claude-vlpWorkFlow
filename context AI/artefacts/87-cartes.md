# La feuille de route plus courte et lisible — notes et journal
## Résultat
La feuille de route de Cairn, cartes fermées, tient en 5 écrans d'ordinateur au plus ; la TODO ne défile plus de côté ; rien de son texte n'est perdu, seulement replié.
## Notes
- FEU1 : ## Mesures écrit (grep -c = 1) : kit 3,39 écrans (2931 px), Cairn 13,79 (11 913 px) ; aucun défilement de côté à 1536, TODO et clos défilent à 375 ; Artifact read 23 274 / 22 378 tokens ; page_vs_source Cairn rangs 16 · entiers 15 (le rang au badge en cours)
- FEU2 : test_zone_todo vert : cartes → forme cartes, fin avant ZONE:clos, badge relu rang 30 ; tableau → mêmes bornes que zone() ; zone vide → ValueError. Mutant (borne retirée, tableau d'abord) → forme tableau, ligne des clos, le test tombe. 3 suites OK, pyright 0 erreur ; Cairn feuille --verifier identique (16 rangs)
- FEU3 : test_feuille_en_cartes vert : tableau d'avant (préambule + badge) → 0 <table>, 3 cartes pour 3 rangs, cellules via cellule_md, badge rang 4 ; 2e appel inchangée ; vigile PAGE SAINE. Mutant (détail vide) → ÉCART feuille : TODO rendue. Tests OK, pyright 0 erreur
- FEU4 : test_sommaire vert : feuille sans sommaire → 1 nav sous </header>, 3 liens, id encours/todo/clos 1 fois chacun, dans l'ordre ; 2e appel inchangée. Mutant (garde déjà posé retirée) → ÉCART feuille : idempotente ; seul, 2 nav et 2 id encours. Tests OK, pyright 0 erreur
- FEU5 : page_vs_source Cairn tableau : ancien rangs 16 · entiers 15 (= FEU1), nouveau 16 · 16 — l'écart est le badge en cours, retiré comme FEU1 le demandait (badge gardé : 16 · 15). Copie en cartes : ancien 29 · 0 (table des clos), nouveau 16 · 16. rejeu.py code 0 sur les deux formes (todo_lignes 16, coches 2). Mutant (borne retirée, tableau d'abord) → 29 · 0. pyright 3 → 2 erreurs
- FEU6 : Les feuilles du kit et de Cairn régénérées, mesurées, republiées ; tu les regardes. Après FEU1, FEU4, FEU5.
- FEU7 : tests verts, pyright 0 erreur, grep -c "la feuille de route</a>" context AI/artefacts/87-cartes.html rend 1
- FEU8 : tests verts, pyright 0 erreur, mutant (borne basse) tombe, vlp.py feuille sur copie kit à 7 rangs rend 7 chantiers possibles · 2 petits, 1 moyen, 2 gros, 2 pas estimés · 1 bloqué · ≈17 fiches estimées
## Journal
- 2026-09-27 : FEU1 : à 1536 × 864 aucune feuille ne défile de côté, le défilement de l'audit se voit à 375 × 812 ; le critère de FEU6 s'y remesure. page_vs_source.py ne retrouve pas le rang au badge « en cours » (kit 6/7, Cairn 15/16) : à régler en FEU5.
- 2026-09-27 : FEU7 et FEU8 ajoutées sur deux commentaires de l'utilisateur : un lien vers la feuille de route sur cette page ; le détail des chantiers possibles (petits ≤ 1 fiche, moyens 2 à 4, gros ≥ 5, pas estimés, bloqués, total). FEU6 attend FEU8.
- 2026-09-27 : FEU2 : pyright refuse test-vlp.py si un test s'ajoute au niveau du module (Code is too complex to analyze) — un nouveau test va dans une fonction test_<nom>() appelée juste après.
## Bilan
