# Mesurer les tokens consommés — notes et journal
## Lien
https://claude.ai/code/artifact/6736d2af-e88e-4e72-b485-d9dbef1951fa
## Résultat
Un script (scripts/mesure-tokens.py) somme les tokens d'usage à partir des transcripts JSONL de session, et affiche le résultat — comptes bruts — à la fin de chaque fiche jouée et à la clôture du chantier.
## Notes
- M1 : grep "scripts/" CLAUDE.md rend une ligne, dans une règle 4 qui dit « exception, assumée ».
- M2 : Sur un JSONL réel : total 13 878 232, 0 ligne invalide, comptes bruts.
- M3 : Rejoué en vrai : fiche 4 741 448 tokens, cumul chantier 5 325 704 — deux tables brutes avant la main.
- M4 : Chemin script qualifié par ${CLAUDE_PLUGIN_ROOT} (bug trouvé en testant sur Cairn) ; décompte confirmé, section commit/push à deux questionnaires écrite.
## Journal
- 2026-09-10 : M2 : confirmé sur un vrai JSONL, usage vit sous message.usage, uniquement sur les lignes type: "assistant".
- 2026-09-11 : M4 : chemin relatif scripts/mesure-tokens.py introuvable hors du kit — qualifié par ${CLAUDE_PLUGIN_ROOT} dans tache.md et cloture.md.
## Bilan
- Livré : scripts/mesure-tokens.py (comptes bruts depuis un JSONL de transcript), affichage du coût en fin de fiche (tache.md) et à la clôture (cloture.md), proposition de commit/push à la clôture — jamais sans confirmation.
- A surpris : chemin relatif du script introuvable hors du kit, résolu contre le cwd du projet équipé plutôt que le sien — corrigé par ${CLAUDE_PLUGIN_ROOT}/scripts/mesure-tokens.py, trouvé en testant sur Cairn.
