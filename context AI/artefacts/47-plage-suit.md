# La plage des fiches suit le fichier — notes et journal
## Lien
https://claude.ai/artifact/BQkFrqxxJvCnu7vn7q55TS
## Résultat
Une fiche ajoutée après l'ouverture ne laisse plus de plage figée : page et ouvrir relancés remettent l'en-tête de la page et la ligne d'index à la plage du fichier, et /vlp:chantier dit de les relancer après un redécoupage.
## Notes
- PLA1 : regenerer réécrit la plage de l'en-tête par plage() ; une fiche seule s'affiche X1 ; ne dépend de rien.
- PLA2 : ouvrir relancé rafraîchit la plage de sa ligne d'index (index ~1) ; /vlp:chantier le dit ; ne dépend de rien.
## Journal
- 2026-09-24 : PLA1 : le sous-agent a commité seul (définition d'agent d'avant CAS, CLAUDE.md global) ; commit défait et refait par le chef. La plage s'écrit à un seul endroit, regenerer ; quatre mutants tombent.
- 2026-09-24 : PLA2 : le sous-agent réécrivait la ligne d'index entière, titre compris, et son test « une seule ligne » passait avec une ligne doublée ; repris, la plage seule, cinq mutants tombent.
## Bilan
- Livré : La plage des fiches suit le fichier : l'en-tête de la page et la ligne d'index d'un chantier ouvert suivent le fichier, et /vlp:chantier dit de relancer ouvrir, page et feuille après un redécoupage
- Surpris : Le sous-agent PLA1 a commité seul — sa définition d'agent date d'avant CAS, et le CLAUDE.md global demande un commit par tâche ; les deux fiches ont rendu du code à reprendre, neuf mutants prouvent les reprises.
