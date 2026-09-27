# Le coût juste, aux deux bords du chantier — notes et journal
## Lien
https://claude.ai/artifact/4qLntEK1rWKQSQbSpwwJYW
## Résultat
Dans une session qui enchaîne plusieurs chantiers, chacun ne compte que le sien : hors fiches part du commit d'avant l'ouverture et finit à la clôture, la première fiche se mesure avant son commit, et clore régénère les coûts de la page.
## Notes
- FIN1 : L'origine et la clôture bornent hors fiches ; VAL passe de 18 654 046 à 6 924 438 tokens ; ne dépend de rien.
- FIN2 : Sans commit de fiche, la fiche part de l'ouverture au lieu de toute la session (OUV, n° 42) ; dépend de FIN1.
- FIN3 : clore passe la page par regenerer : la clôture et la dernière fiche commitée y sont comptées ; dépend de FIN1.
## Journal
## Bilan
- Livré : Chaque chantier ne compte que le sien : hors fiches part du dernier commit étranger avant l'ouverture et finit à la clôture ; la première fiche se mesure avant son commit ; clore régénère les coûts de la page
- Surpris : Les trois sous-agents ont rendu du code à reprendre, et deux fois des tests creux ou absents, même nommés avec leurs valeurs ; chaque reprise est prouvée par un mutant.
