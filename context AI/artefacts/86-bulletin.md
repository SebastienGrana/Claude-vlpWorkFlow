# /vlp:check lit le contrat — notes et journal
## Résultat
/vlp:check dit, sans rien rejouer, combien de sous-agents ont tourné depuis l'ouverture du chantier, combien ont écrit dans Git, combien sans statut en tête.
## Notes
- CHK1 : contrat --ouverture F : borne = plus ancien commit qui ajoute F (git log --diff-filter=A), filtre par l'heure du sous-agent lui-même, ligne DEPUIS ; F non commité : GARDE code 1 ; test dépôt temporaire (F à T0+1000, parent à 200, sous-agents à 500 et 1500 → CONTRAT 1) ; mutants heure parente → 0 listé, filtre retiré → 2 listés : ÉCART ; réel : CHK CONTRAT 0, depuis FOR CONTRAT 11 · 3 écrivent dans Git · 1 sans statut ; test-vlp OK ; pyright 0 errors
## Journal
## Bilan
