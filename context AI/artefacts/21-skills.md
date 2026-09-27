# Migrer commands → skills — notes et journal
## Lien
https://claude.ai/artifact/SnRg17z3ojPU3jTk9pQpD7
## Résultat
commands/ n'existe plus, les cinq commandes vivent dans skills/, evals Windows 3/3, validate propre, 0 renvoi mort
## Notes
- K1 : skills/check/SKILL.md (renommage 100 %) ; eval check score 1, 19 tours, 0,19 $ ; avec disable-model-invocation score 0,5, Skill 0 appel, 9 tours, 0,11 $ → écarté ; validate 1 avertissement voulu
- K2 : commands/ et references/ absents, skills/ 5 dossiers ; references/ 5 lignes → skills/tache/references/ ; tests OK ; suite Windows 3/3 : check 15 tours 0,19 $, hook 2 tours 0,05 $, init 22 tours 0,30 $ (0,55 $)
- K3 : grep des renvois 17 → 12 lignes, 0 renvoi mort (3 replis ~/.claude/commands/, 1 donnée de test, 8 vers skills/tache/references/) ; vlp.py renvois 41 nommés · 0 absent ; validate 1 avertissement voulu ; tests OK ; plugin 3.2.0
## Journal
- 2026-09-17 : K1 : disable-model-invocation écarté — eval check sans : score 1, 19 tours, 0,19 $ ; avec : score 0,5, Skill 0 appel, 9 tours, 0,11 $. La skill reste tapable, le modèle ne peut plus l'appeler.
## Bilan
- Livré : les cinq commandes et references/ vivent dans skills/ (renommages sans changer un octet), renvois de la doc 17 → 12 lignes sans renvoi mort, plugin 3.2.0, evals Windows 3/3 (0,55 $).
- Surpris : disable-model-invocation bloque l'appel par l'outil Skill (score 1 → 0,5), écarté ; une commande déplacée disparaît de la session en cours jusqu'à /reload-plugins.
