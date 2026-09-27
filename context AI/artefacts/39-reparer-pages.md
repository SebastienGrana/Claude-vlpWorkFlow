# Réparer les pages publiées — notes et journal
## Lien
https://claude.ai/artifact/FApkrdZqHKoyH2y6NSzrDv
## Résultat
Sur les cinq feuilles de route, plus de Markdown brut ni de lien cassé : 0 · 0 · 0 dans vlp.py niveau, et aucune page réécrite à la main.
## Notes
- REP1 : py scripts/test-vlp.py : OK, code 0 · grep -c verifier( : 154 → 166 (+12, 9 demandés) · feuille du kit --verifier : identique
- REP2 : py scripts/test-vlp.py : OK, code 0 · grep -c verifier( : 166 → 171 (+5) · champ retire les chevrons <https://…> d'une URL, cmd_ouvrir les retire avant d'écrire --artefact
- REP3 : py scripts/test-vlp.py : OK, code 0 · grep -c verifier( : 171 → 178 (+7, 5 demandés) · niveau lit 2 · 1 · 1 sur une ligne close brute, 0 · 0 · 0 après --ecrire, et une seconde passe ne change rien · le kit est déjà à 0 · 0 · 0
- REP4 : niveau, ligne MARKDOWN après : 0 · 0 · 0 sur les cinq · avant, sur le disque : kit 0 · 0 · 0, Cairn 426 · 1 · 1 (= audit), MapDecorator 0 · 0 · 1, TrackGen 4 · 0 · 0, ProjetONZSM 2 · 0 · 0 · republiée : Cairn, version 51 ; MapDecorator, TrackGen, ProjetONZSM gardées en ligne (déjà à 0 · 0 · 0), décision de l'utilisateur ; kit inchangé
## Journal
- 2026-09-23 : REP1 : la fiche ne disait pas comment `REP3` rejouerait une ligne close. Tranché : `gras_et_liens` prend la ligne `<tr>` entière, toute balise hors mono bornant le gras — sinon deux `**` seuls, dans deux cellules, s'apparient par-dessus `</td><td>`, et un `**` d'attribut `href` se convertit. `REP3` n'a pas à découper en cellules.
- 2026-09-23 : REP3 : sous `/vlp:enchainer`, le sous-agent `vlp:fiche` (fork de `vlp:jouer`) s'est arrêté sans statut quatre fois — une sur REP2, trois sur REP3 —, traité chaque fois en `RETOUR`. REP2 est passée au rejeu ; REP3 s'est faite à la main, par `/vlp:tache REP3`. Cause non diagnostiquée : à creuser avant de rejouer une fiche de code par `/vlp:enchainer`.
- 2026-09-23 : REP4 : MapDecorator, TrackGen et ProjetONZSM ne sont pas republiées, sur décision de l'utilisateur. Leurs pages en ligne, faites à la main, sont déjà à 0 · 0 · 0, et leur version régénérée perd du contenu : TODO de MapDecorator hors table, donc lue vide ; lettres entre backticks ignorées ; source de TrackGen sans accents. Les quatre feuilles voisines sont hors de git, pas la seule de Cairn : quatre copies `.avant-REP`.
- 2026-09-23 : REP4 : sans `--ecrire`, la ligne `MARKDOWN` de `niveau` compte la page régénérée, pas celle du disque — muette sur la TODO et la zone « en cours ». L'« avant » a donc été pris par `markdown_brut` sur le disque (Cairn 426 · 1 · 1, comme l'audit). Défaut de `REP3`, laissé en suivi par l'utilisateur.
## Bilan
- Livré : plus de Markdown brut ni de lien cassé sur les feuilles de route : vlp.py convertit gras, liens et chevrons, niveau compte et migre les lignes closes ; cinq feuilles à 0 · 0 · 0, Cairn republiée
- Surpris : une ligne de coût « ? $ » ne se relit pas, la page a perdu le coût par fiche (repris de git) ; le sous-agent vlp:fiche s'est arrêté sans statut quatre fois, REP3 faite à la main
