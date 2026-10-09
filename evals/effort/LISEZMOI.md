# evals/effort — le juge de l'effort (MET4, mis à l'abri par EFF2)

- **Ce qu'il mesure** : 3 fiches de code et 1 de conception rejouées en Opus 5.5 à `medium`, `high` et `xhigh` ; par essai, commits, suite entière, pyright, cliquet, `verifier(`, relecteur et coût — une ligne dans `met4-resultats.jsonl`.
- ⚠️ **Il appelle le modèle** (`claude -p`, payant), contrairement à `scripts/` qui reste à zéro appel : `--borne` en $ est exigée pour jouer.
- **À blanc, sans aucun appel** : `py -3 evals/effort/met4-juge.py --kit <kit> --essais-dir <essais> --a-blanc --essais VIT23:high` liste ce qui serait joué.
- **Jouer** : `py -3 evals/effort/met4-juge.py --kit <kit> --essais-dir <essais> --conception VIT12 --essais VIT23:high --borne <USD>` — de jour seulement, jamais sous la boucle de nuit.
- **Le tableau** : `py -3 evals/effort/met4-tableau.py` lit le jsonl et `traces/` (non versé, exclu par `.gitignore`) et imprime du markdown.
- `claude-relais.py` : lancé par `boucle.py --claude`, il ajoute la consigne « premier plan » ; le kit lui vient de `MET4_KIT`, posé par le juge.
- Les résultats de `medium` et `xhigh` (2026-10-07) sont dans le jsonl ; leur lecture, au journal `context AI/08-etat.md`, entrée « MET4 ».
