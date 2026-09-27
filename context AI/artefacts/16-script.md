# Un script vlp.py pour la mécanique — notes et journal
## Lien
https://claude.ai/artifact/MDYKgdDhAKsPJE4cp1TK6u
## Résultat
scripts/vlp.py, testé, offre carte, extraire, socle, sessions, valider et page ; carte.py est retiré ; les commandes l'appellent au lieu des sed/awk et du HTML retapé — gain prouvé avant/après, comptes bruts à côté.
## Notes
- S1 : test-vlp.py : OK (contre-épreuve en échec). carte 65 lignes, extraire R3 24, socle 74 : diff vide avec carte.py, sed et awk. carte.py : 0 appel restant, retiré.
- S2 : test-vlp.py : OK, 11 écarts testés + contre-épreuve en échec. Sur 09 à 16 : 7 bilans, 6 VALIDE, 1 INVALIDE — le (visuel) de C1 (11-conso.md:88), laissé tel quel.
- S3 : test-vlp.py : OK, 10 cas de page + 2 contre-épreuves en échec. --verifier sur R : À JOUR, 0 écart ; --creer sur S : 5 fiches, 136 lignes.
- S4 : sed/awk de mécanique : tache 5→0 (1 exemple de plage), enchainer 2→0, cloture 1→0. Blocs 1 et 6 bis exécutés tels qu'écrits. Appels prescrits 9→5, octets relus 11 530→9 463.
- S5 : sed/awk 11 → 1 (prose), carte.py 4 → 0, /vlp:chantier étape 0 : 2 appels → 0 ; valider VALIDE 5 fiches · socle 50 · 0 écarts
## Journal
- 2026-09-17 : S1 : un marqueur fermant oublié ne fait plus avaler la fiche suivante — l'extraction s'arrête au marqueur ouvrant suivant et le dit. Fiches jouées d'affilée dans la session du cadrage, à la demande.
- 2026-09-17 : S2 : valider ignore (visuel) cité entre accents graves, même sur deux lignes. Seul écart des archives : C1. La commande rechargée injecte déjà vlp.py carte — prouvé en vrai.
- 2026-09-17 : S3 : page remesure les sessions à chaque régénération ; une session partagée garde les coûts déjà affichés, retire la part que l'ancienne page n'attribuait à aucune fiche (le cadrage) et donne le reste à la dernière. Une page close ne se régénère pas (sur R, la session a continué après la clôture).
- 2026-09-17 : S4 : /vlp:tache prescrit 5 appels au lieu de 9 ; la publication part sans read — dans une session neuve, un refus possible, à rejouer pour de vrai. Bash(sed:*) reste pour les plages des fiches ; agents/fiche.md inchangé (aucun sed/awk).
- 2026-09-17 : S5 : le repli python3 || python ne vaut que pour carte (sortie toujours 0) ; valider, page, extraire passent par PY=$(…). À rejouer après /reload-plugins : /vlp:chantier, /vlp:init, /vlp:check.
- 2026-09-17 : S5 : republier le même contenu après un refus est refusé une seconde fois — il faut lire l'URL, puis publier (3 appels) ; tache-page.md dit encore « republie ».
## Bilan
- Livré : scripts/vlp.py (carte, extraire, socle, sessions, valider, page), testé par test-vlp.py ; carte.py retiré ; tache, enchainer, chantier, init, check, tache-page.md et cloture.md l'appellent.
- Avant → après : lignes sed/awk 11 → 1 (prose) · appels à carte.py 4 → 0 · appels prescrits de /vlp:tache 9 → 5 · /vlp:chantier étape 0 2 → 0 · page retapée à chaque fiche → régénérée par le script.
- Coût à l'étape 3 de la clôture : ≈17,2M (17 193 402) · 106 tours · 15,72 $ ; le total ci-dessus compte la session jusqu'à la régénération de la page.
- Surpris : le repli python3 || python double un appel qui sort 1 ; un refus de publication se répète si l'on ne relit pas l'URL. Reste ouvert : rejouer chantier, init et check après /reload-plugins ; corriger tache-page.md.
