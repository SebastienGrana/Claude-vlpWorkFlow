# Réduire les tours de /vlp:tache — notes et journal
## Lien
https://claude.ai/artifact/CWC5awkprtgXwgyyP1CoeC
## Résultat
tache.md tient en 150 lignes de corps, reçoit CHANTIER.md avant le premier tour, lit fiche, titres et socle en un seul appel, range le rare dans references/ — et le gain est prouvé avant/après, en tours et en dollars.
## Notes
- R1 : !`…` : 5 essais sur 6 marchent (pwd, variable du plugin, head, a && b, script python) ; la boucle de l'étape 0 non. Avant : 14 appels prescrits. Sondes retirées.
- R2 : references/ : contraintes 8, blocage 35, page 74 lignes ; tache.md 385 → 289 ; seul enchainer.md:26 lit encore tache.md (étape 0, pour R3).
- R3 : Bloc groupé exécuté sur R3 : fiche 23 lignes, socle 63, contraintes, en une sortie ; « que pour lire » : 0 ligne. carte.py testé (OK, contre-épreuve en échec). tache.md 289 → 228.
- R4 : Corps 150 lignes ; appels prescrits 14 → 9 ; octets relus par fiche 18 471 → 11 518. Bloc de l'étape 6 exécuté tel qu'écrit : deux tables + page en une sortie.
## Journal
- 2026-09-17 : R1 : !`…` exécute pwd, head, a && b et un script du plugin ; la boucle while + $(…) est rendue au modèle (un tour). Une commande modifiée n'est pas relue sans /reload-plugins.
- 2026-09-17 : R2 : les contraintes se lisent dans le même appel que le socle ; la règle « artefact = aucun → sauter » reste dans tache.md seul.
- 2026-09-17 : R3 : l'étape 0 devient scripts/carte.py injecté (choix validé, au lieu d'un repli en prose). Bug trouvé : sous Windows et macOS, commands/chantier.md passait pour CHANTIER.md.
- 2026-09-17 : R4 : la liste des cinq écritures de clôture, recopiée de cloture.md, est retirée de tache.md. Le gain en tours réels reste à mesurer sur un rejeu dans une session neuve.
## Bilan
- Livré : tache.md en 150 lignes de corps (385 avant), la carte du projet injectée avant le premier tour par scripts/carte.py, fiche + socle + contraintes en un appel, coût + page en un appel, le rare dans references/. Appels prescrits 14 → 9 ; octets relus par fiche 18 471 → 11 518.
- Ce qui a surpris : sous Windows et macOS, la recherche du projet prenait commands/chantier.md pour CHANTIER.md ; une commande modifiée n'est pas relue sans /reload-plugins. Reste à mesurer le gain en tours réels, sur un rejeu dans une session neuve.
