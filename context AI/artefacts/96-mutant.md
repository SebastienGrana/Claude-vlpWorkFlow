# Le mutant par un outil du kit — notes et journal
## Résultat
vlp.py mutant casse le code exprès, joue les tests sans s'arrêter au premier écart, les liste, et rend le fichier à l'octet près : plus de script de mutant réécrit à la main.
## Notes
- MUT1 : vlp.py mutant et VLP_TOUS_ECARTS, texte ou @fichier, CRLF géré, tests et mutant du mutant ; ne dépend de rien
## Journal
## Bilan
- Livré : vlp.py mutant casse le code exprès (texte ou @fichier, CRLF suivi), joue les tests avec VLP_TOUS_ECARTS=1, liste tous les écarts et rend le fichier à l'octet dans un finally
- Surpris : 72 transcriptions et 275 appels avaient joué un mutant à la main, pas une seule ; et avec tous les écarts, le mutant stash de VRB en fait tomber 2, pas 1
- Estimé : estimé 1 fiches ≈3,01 $ · cadré 1 · joué 1 fiches 1,76 $
