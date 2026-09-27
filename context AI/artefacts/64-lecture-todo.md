# /vlp:chantier ne lit plus l'état en entier — notes et journal
## Lien
https://claude.ai/artifact/RbR7LdkD8BamZqUFqLzJGY
## Résultat
La carte imprime la TODO et le format des fiches ; /vlp:chantier ne lit plus 08-etat.md (2 137 lignes) ni la méthode (376) en entier, et une vraie séance mesurée avant/après le prouve en tokens.
## Notes
- LEC1 : avant 2f9a46f3 (Read tronqué à 453/1 222 l.) : tours 3, ctx_dernier 110 515, equiv 285 200, 1.14 $ ; après à la main 44909b3f : tours 6, ctx_dernier 85 624, equiv 122 263, 0.49 $ ; table des 5 projets au journal
- LEC2 : joué à la main après 4 refus : test-vlp.py OK, pyright 0 errors, mutant tué (ÉCART premier titre TODO) ; kit à « aucun » : TODO 356–392 puis 37 lignes ; 5 projets : chemins justes, Cairn 20a sans TODO, 10-etat 158–434
- LEC3 : joué à la main : test-vlp.py OK, pyright 0 errors, mutant tué (ÉCART trois sections) ; kit : méthode 288–361 puis 74 lignes, texte imprimé ; Cairn et MapDecorator sans « Les deux formes de critère de fin » → METHODE=absente
- LEC4 : joué à la main : SKILL.md 278 → 277 lignes ; étape 1 : « en entier » 0, TODO=absente 1, METHODE=absente 1 ; pre-commit RC 0 ; « Où vit quoi » : la TODO par la carte
- LEC5 : Une vraie séance après, mesurée et comparée à LEC1 — ton geste d'abord. Après LEC1 et LEC4.
## Journal
## Bilan
- Livré : sans chantier ouvert, la carte imprime la TODO et le format des fiches ; /vlp:chantier ne relit plus 08-etat.md ni la méthode
- Surpris : LEC2 refusée 4 fois à la relecture (fiche floue deux fois, sous-agent, règle du chef inapplicable), passée à la main ; l'après coûte 0.59 $ contre 1.14 $ avant, mais plus que le cadrage à la main (0.49 $), 3 appels du montage compris
