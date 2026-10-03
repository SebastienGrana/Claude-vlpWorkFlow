# Aller plus vite sans coder moins bien — notes et journal
## Résultat
Coder plus vite et mieux. Une fiche attend moins ses tests et lit moins de contexte — mesuré avant (VIT1) et après (VIT13) — sans qu'un seul contrôle soit retiré ; le code qu'elle laisse est sain, facile à maintenir et documenté.
## Notes
- VIT1 : Entrée « VIT1 — la base » dans 08-etat.md, six lignes avec commande et comptes bruts ; machine libérée : test-vlp 571 et 535 s, test-boucle 425 et 428 s, mutant 538 s attrapé par NUI27 (a), lancements 362 et 71 ms ; chaque soustraction dite « estimé ».
- VIT2 : le mutant joue dans une copie du kit et s'arrête sur le test attendu ; dépend de VIT1
- VIT3 : les fichiers d'un commit lus en un appel Git ; dépend de VIT1
- VIT4 : un dépôt modèle copié dans les tests ; dépend de VIT1
- VIT5 : vlp.py devient un lanceur mince, le code en cache ; dépend de VIT2
- VIT6 : boucle.py appelle vlp sans nouveau processus ; dépend de VIT5
- VIT7 : test-boucle en parallèle de test-vlp ; dépend de VIT3, VIT4, VIT6
- VIT8 : un seul Python par hook ; dépend de VIT5
- VIT9 : une carte des symboles, des fiches sans numéros de ligne
- VIT10 : les tests rangés en groupes nommés, un seul jouable ; dépend de VIT9
- VIT11 : la suite entière exigée au commit ; dépend de VIT10
- VIT12 : le relecteur ne rejoue que le nouveau test avant ; dépend de VIT2, VIT10
- VIT13 : la fin mesurée, avant/après ; dépend de toutes
## Journal
## Bilan
