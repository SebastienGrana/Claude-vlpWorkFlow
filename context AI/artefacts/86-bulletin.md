# /vlp:check lit le contrat — notes et journal
## Lien
https://claude.ai/artifact/4fci5zHKJC6fQpyCBwgwZ3
## Résultat
/vlp:check dit, sans rien rejouer, combien de sous-agents ont tourné depuis l'ouverture du chantier, combien ont écrit dans Git, combien sans statut en tête.
## Notes
- CHK1 : contrat --ouverture F : borne = plus ancien commit qui ajoute F (git log --diff-filter=A), filtre par l'heure du sous-agent lui-même, ligne DEPUIS ; F non commité : GARDE code 1 ; test dépôt temporaire (F à T0+1000, parent à 200, sous-agents à 500 et 1500 → CONTRAT 1) ; mutants heure parente → 0 listé, filtre retiré → 2 listés : ÉCART ; réel : CHK CONTRAT 0, depuis FOR CONTRAT 11 · 3 écrivent dans Git · 1 sans statut ; test-vlp OK ; pyright 0 errors
- CHK2 : /vlp:check : vérification I, contrat --ouverture sur le fichier de fiches courant, sautée si « aucun » ; huit → neuf, A à H → A à I ; +12 −2 lignes ; grep -c contrat --ouverture 1, huit 0 ; bloc I lancé par le lien du plugin : DEPUIS puis CONTRAT 0 ; test-vlp OK ; rejouer /vlp:check après /reload-plugins : geste de l'utilisateur, au rapport
## Journal
## Bilan
- Livré : vlp.py contrat --ouverture F : les sous-agents partis depuis le commit qui ajoute le fichier de fiches, par leur heure à eux ; /vlp:check le lance en vérification I
- Surpris : Le premier commit qui nomme le préfixe est souvent l'ajout à la TODO ; 28 sous-agents sur 103 sont partis dans une session de cadrage, qu'aucune des deux bornes proposées ne rangeait juste
- Estimé : estimé 0,5 fiches ≈2,07 $ (taux plat) · cadré 2 · joué 2 fiches 2,22 $
