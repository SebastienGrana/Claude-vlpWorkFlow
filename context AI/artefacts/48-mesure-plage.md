# mesure-tokens.py se lit et se borne en ligne de commande — notes et journal
## Lien
https://claude.ai/artifact/AQoaT856X9GdAwddf4mTrJ
## Résultat
--plage DEBUT FIN borne la mesure, heures ou commits ; la docstring dit la syntaxe ; la ligne périmée de 34-agent-sans-git.md est marquée.
## Notes
- MTK1 : borne() lit une heure ISO ou un commit ; main passe la plage à mesurer ; ne dépend de rien.
- MTK2 : une docstring de module ; la phrase périmée marquée, renvoi daté vers CPT2 ; dépend de MTK1.
## Journal
- 2026-09-24 : MTK1 : le sous-agent a écrit ses tests après le code, sans écart vu ; le chef a rejoué le mutant. Repris : un fichier suivi par Git passait pour un commit (sans --) ; sept mutants tombent.
- 2026-09-24 : MTK2 : la docstring du sous-agent disait faux deux fois (heure « locale », code de sortie) et recopiait COLONNES ; reprise en dix-neuf lignes, code de sortie essayé sur trois cas ; le marquage dit où lire la preuve (40-cout-juste.md, CPT2).
## Bilan
- Livré : mesure-tokens.py se borne en ligne de commande : --plage DEBUT FIN, heures ISO ou commits Git, une borne illisible sort 1 ; une docstring dit la syntaxe ; la phrase périmée de 34-agent-sans-git.md est marquée d'un renvoi vers CPT2
- Surpris : Le sous-agent MTK1 a écrit ses tests après le code, sans écart vu, et un fichier suivi par Git passait pour un commit ; la docstring de MTK2 disait faux deux fois. Sept mutants prouvent les reprises.
