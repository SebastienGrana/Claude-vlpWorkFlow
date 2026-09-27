# Le cadrage compte dans le coût du chantier — notes et journal
## Lien
https://claude.ai/artifact/3VpZLJALSxTaFfzbDHpGNF
## Résultat
ouvrir note la session du cadrage en tête du fichier de fiches ; cout et la page la mesurent, ses tours d'avant l'ouverture dans hors fiches.
## Notes
- CAD1 : ouvrir pose **Session** avant le premier ## ; parts_aux_commits mesure les sessions de l'en-tête ; ne dépend de rien.
## Journal
- 2026-09-24 : CAD1 : case vide et commit du sous-agent au 80e appel ; ses tests relâchés au lieu de fixer l'environnement ; la session allait dans la fiche. Repris : avant la première ligne ##, en-tête mesuré après les fiches, tests exacts ; neuf mutants tombent.
## Bilan
- Livré : ouvrir note la session du cadrage avant la première ligne ## du fichier de fiches ; cout et la page la mesurent comme celles des fiches, ses tours d'avant l'ouverture dans hors fiches
- Surpris : Le sous-agent a plafonné à 80 appels : le filet a tiré, il a commité au lieu de cocher et rendu FAITE sur une case vide ; il avait relâché ses tests au lieu de fixer l'environnement. Neuf mutants prouvent la reprise.
