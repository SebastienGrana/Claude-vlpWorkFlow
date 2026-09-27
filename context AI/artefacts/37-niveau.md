# Remettre les projets équipés à niveau — notes et journal
## Lien
https://claude.ai/artifact/JjSivR23MGDLhyFJeHtD4e
## Résultat
Une sous-commande vlp.py diagnostique et remet à niveau un projet équipé ; les cinq projets y passent, et la carte injectée ne crie plus.
## Notes
- NIV1 : Ligne d'injection sous PowerShell : kit 60 -> 59 lignes, 1 -> 0 message de lanceur ; dossier non equipe 6 -> 5, 1 -> 0 ; relue par bash 58 lignes, 0 ; py scripts/test-vlp.py imprime OK
- NIV2 : 5 bilans bruts : Cairn 3 ecarts/2 avert., MapDecorator 2/1, TrackGen 2/1, ProjetONZSM 2/0, bac 5/0 — Cairn CLAUDE.md 89/80 et 2 renvois absents, TrackGen CHANTIER.md 51/50, feuille absente du bac tous retrouves ; test-vlp.py imprime OK
- NIV3 : niveau sur le bac des tests : 4 écarts sans --ecrire, 3 corrigés avec, 1 restant (renvoi absent, à la main) ; py scripts/test-vlp.py imprime OK
- NIV4 : Cairn, MapDecorator, TrackGen, ProjetONZSM : 0 écarts · 0 avertissements ; bac à sable : 1 écart assumé (page du chantier, son socle interdit tout artefact). Fichiers de tête : Cairn CLAUDE.md 89→80, index 111→71 ; MapDecorator CLAUDE.md 84→79, index 73→74 ; TrackGen CHANTIER.md 51→47.
## Journal
- 2026-09-17 : 2>"<chemin>" est la seule redirection d'erreur que PowerShell et bash lisent pareil ; la trace part dans relais-python.err au lieu d'etre jetee
- 2026-09-17 : vlp.py niveau diagnostique un projet equipe sans rien ecrire ; imprevu : la table des clos traine dans les CINQ CHANTIER.md, pas le seul Cairn — NIV4 s'elargit ; entree n. 22 de la TODO corrigee (une copie locale de methode-chantier.md n'est pas un ecart)
- 2026-09-18 : clore ne retirait pas la table des clos de CHANTIER.md, contrairement à ce que la fiche supposait : niveau --ecrire la retire lui-même, et jamais si l'index ne nomme pas chacun de ses fichiers
- 2026-09-18 : 2026-09-18 — les cinq projets à niveau ; le bac garde 1 écart assumé : niveau réclame la page du chantier même quand l'artefact vaut « aucun ».
## Bilan
- Livré : vlp.py niveau : un projet équipé se diagnostique et se corrige en un appel, et les cinq projets équipés sont passés — quatre à 0 écart, le bac à 1 écart assumé
- Surpris : niveau --ecrire ne retire la table des chantiers clos que si l'index nomme chacun de ses fichiers : MapDecorator citait mockups/TACHES-UI.md, hors du dossier de contexte et absent de l'index
