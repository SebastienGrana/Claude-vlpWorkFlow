# Aller plus vite sans coder moins bien — notes et journal
## Résultat
Coder plus vite et mieux. Une fiche attend moins ses tests et lit moins de contexte — mesuré avant (VIT1) et après (VIT13) — sans qu'un seul contrôle soit retiré ; le code qu'elle laisse est sain, facile à maintenir et documenté.
## Notes
- VIT1 : Entrée « VIT1 — la base » dans 08-etat.md, six lignes avec commande et comptes bruts ; machine libérée : test-vlp 571 et 535 s, test-boucle 425 et 428 s, mutant 538 s attrapé par NUI27 (a), lancements 362 et 71 ms ; chaque soustraction dite « estimé ».
- VIT2 : test-vlp OK (code 0, 2 SAUTÉ connus) ; 3 cas VIT2 verts, 3 mutants attrapés ; NUI27 --attendu : MUTANT ATTRAPÉ en 144,1 / 139,5 / 140,8 s contre 538 s (VIT1), vrai vlp.py inchangé (RENDU) ; pyright 0 ; verifier( 765 → 768 / 82 → 82 ; cmd_mutant 9/11/5/47/2 → 4/4/2/23/1
- VIT3 : test-vlp OK (code 0) ; ancien et nouveau lecteur égaux sur 3 fichiers et un dossier en .md (CRLF, \r, accents), et sur les 98 .md du kit ; ouverts . --rev HEAD : 3 699 → 499 ms (médianes de 5), sortie identique ; 2 mutants attrapés (LF sauté, \r seul) ; pyright 0 ; verifier( 768 → 770 / 82 → 82 ; cliquet tenu
- VIT5 : test-vlp OK (code 0) en 437 s ; vlp.py lignes CHANTIER.md : 318 → 210 ms (médianes de 20 ; VIT1 362 ms ; 213 ms sous PYTHONDONTWRITEBYTECODE=1) ; mutant NUI27 sur vlp_coeur.py attrapé en 112 s ; pyright 0 ; verifier( 770 / 82 inchangés ; cliquet tenu (3 touchées, 0 neuve)
- VIT6 : test-boucle OK : 330 → 184 s (−44 %, une mesure de chaque côté) ; verifier( 82 → 83 (le test qui compare au vrai sous-processus) ; mutant « sortie tronquée » attrapé ; pyright 0 ; suite complète OK en 305 s
- VIT7 : test-boucle en parallèle de test-vlp ; dépend de VIT3, VIT6, VIT14
- VIT8 : option de l'utilisateur : deux lanceurs gardés, le second sans charger le cœur (importtime : 1 puis 0) ; second lanceur 292 → 77 ms (py -3, le #! évité) / 129 ms (python3) ; verifier( 770 → 771 ; mutant attrapé ; pyright 0 ; suite OK en 286 s
- VIT9 : une carte des symboles, des fiches sans numéros de ligne
- VIT10 : les tests rangés en groupes nommés, un seul jouable ; dépend de VIT9
- VIT11 : la suite entière exigée au commit ; dépend de VIT10
- VIT12 : le relecteur ne rejoue que le nouveau test avant ; dépend de VIT2, VIT10
- VIT13 : la fin mesurée, avant/après ; dépend de VIT7, VIT8, VIT11, VIT12 — et, par elles, de toutes
- VIT14 : les deux cas de clôture fragiles sous charge, reproduits puis corrigés à la cause ; dépend de VIT1
- VIT15 : sante sur le kit : 794 fonctions, 63 au-dessus d'un seuil, 525 docstrings ; ast = ruff 0.16.10 sur 794/794, listes avec et sans ruff identiques ; cliquet tenu contre 74550d4 (745 vieilles dont 2 touchées, 42 neuves, 2 améliorées) ; suite OK en 520 s ; verifier( 749 → 763 et 82 → 82 ; mutant attrapé, 4 écarts en 510 s ; pyright 0 ; sante.py 39 fonctions, 0 au-dessus d'un seuil, 39 docstrings
- VIT16 : --si-base sans base : SANS BASE, sort 0, rien écrit (projet vide et hors du kit, sha1 de la base du kit inchangé) ; kit : BASE 795 fonctions, sort 0 ; test-vlp OK ; verifier( 763→765 (boucle 82→82) ; mutant attrapé (1 écart) ; pyright 0 ; principal 6/5/3/14/2→7/6/3/16/2, options_sante instr. 9→10, test neuf 1/1/0/25/2, docstrings oui, AST=RUFF 592/592 ; durée médiane de 5 : 2,85 s avec ruff, 1,66 s sans
## Journal
- 2026-10-04 : plan revu après VIT1 : VIT4 retirée, ≈ 4 à 6 s par suite et rien après VIT7 (D1) ; VIT14 ajoutée, deux cas de clôture fragiles sous charge (D2) ; VIT2 passe tester_boucle() en dernier ; VIT13 nomme ses dépendances
- 2026-10-04 : critères de code sain tranchés (page des critères) : cliquet, docstring de toute fonction touchée, tests sans longueur ; outil : ruff s'il est là, d'où VIT15, ajoutée avant VIT2
- 2026-10-04 : VIT15 : le compte ast égale ruff sur tout le kit (794/794) ; une sous-commande neuve de vlp.py passe par options_<commande> et PAR_ARGUMENTS, main et repartir étant au-dessus des seuils ; qui lance sante --base en fin de fiche reste à trancher (méthode, n° 99)
- 2026-10-04 : VIT2 : la copie du mutant garde context AI/ (NIV1 et JUG2 lisent le vrai dépôt) ; une copie peut rester après taskkill, effacer_copie réessaie 2 s
- 2026-10-04 : VIT5 : une fonction déplacée et touchée à la fois paraît neuve au cliquet ; déplacer d'abord (sante --base), toucher ensuite
## Bilan
