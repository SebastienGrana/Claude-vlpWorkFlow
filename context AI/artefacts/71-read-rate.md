# Un Read raté réveille-t-il le filet ? — notes et journal
## Lien
https://claude.ai/artifact/LwBycLXrBXgoWzEHzMVH77
## Résultat
Oui ou non, mesuré : un Read sur un fichier absent déclenche-t-il le filet, à plafond bas ?
## Notes
- RAT1 : OUI : plafond 5, PREMIER_AVERTISSEMENT tour=2 outil=Read is_error=oui hook=PostToolUseFailure:Read ; témoin 80 : 0. Imprévu : 13 avertissements dans un tour.
## Journal
- 2026-09-26 : RAT1 : plafond 5 au lieu de 10, décidé seul la nuit — à 6, les Read tombaient trop tôt ; à valider.
## Bilan
- Livré : un Read raté réveille le filet : PostToolUseFailure:Read, prouvé à plafond 5 par evals/filet-rate/ (témoin 80 muet)
- Surpris : 13 avertissements dans un seul tour : le filet répète son texte à chaque appel groupé
- Estimé : estimé 0,5 fiches ≈2,03 $ · cadré 1 · joué 1 fiches ≈1,43 $
