# Corriger les bugs de l'audit — notes et journal
## Lien
https://claude.ai/artifact/NSx145qiALVfwmHc57Yrdq
## Résultat
Chaque bug relevé par l'audit du 2026-09-17 (1, 2, 3, 5, 6, 7, 8, 10, 11) a un grep qui le montrait avant, et le même grep le montre corrigé.
## Notes
- B1 : $1/$2 dans commands/ et agents/ : 0 ligne (8 avant) ; $ARGUMENTS seul sur sa ligne : 1 par commande (0 avant)
- B2 : Lettres de fiche déjà prises dans check.md : 1 (0 avant) ; CLAUDE_PLUGIN_ROOT hors commandes : 0 (3) ; fichiers fantômes : 0 (4) ; titre inversé : 0 (1)
- B3 : __pycache__ hors git status ; Session en chemin : 0 (7 avant) ; M 11 362 254 et C 7 816 316 identiques avant/après ; 00-route retirée ; 7 titres en « vlp — »
## Journal
- 2026-09-17 : B1 : $1 n'est pas le premier argument mais le second (index à partir de 0), mesuré sur deux textes reçus. Reste à rejouer pour de vrai : /reload-plugins, puis /vlp:tache et /vlp:chantier avec arguments sur un projet équipé.
## Bilan
- Livré : neuf bugs de l'audit corrigés, chacun prouvé par un grep avant/après — /vlp:check D trouve sa ligne, $ARGUMENTS dans quatre commandes, plus de variable dans les fichiers de données, gabarits sans fichiers fantômes, .gitignore, page orpheline retirée, titres alignés, lignes Session réduites à l'id.
- A surpris : $1 désigne le second argument, pas le premier. Reste à rejouer pour de vrai : /reload-plugins, puis /vlp:tache et /vlp:chantier avec arguments. Total : 41 tours, 5 342 511 tokens, 4,94 $.
