# Aller plus vite sans coder moins bien — notes et journal
## Résultat
Coder plus vite et mieux. Une fiche attend moins ses tests et lit moins de contexte — mesuré avant (VIT1) et après (VIT13) — sans qu'un seul contrôle soit retiré ; le code qu'elle laisse est sain, facile à maintenir et documenté.
## Notes
- VIT1 : Entrée « VIT1 — la base » dans 08-etat.md, six lignes avec commande et comptes bruts ; machine libérée : test-vlp 571 et 535 s, test-boucle 425 et 428 s, mutant 538 s attrapé par NUI27 (a), lancements 362 et 71 ms ; chaque soustraction dite « estimé ».
- VIT2 : le mutant joue dans une copie du kit et s'arrête sur le test attendu ; dépend de VIT1
- VIT3 : les fichiers d'un commit lus en un appel Git ; dépend de VIT1
- VIT5 : vlp.py devient un lanceur mince, le code en cache ; dépend de VIT2
- VIT6 : boucle.py appelle vlp sans nouveau processus ; dépend de VIT5
- VIT7 : test-boucle en parallèle de test-vlp ; dépend de VIT3, VIT6, VIT14
- VIT8 : un seul Python par hook ; dépend de VIT5
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
## Bilan
