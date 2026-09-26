# Index du contexte vlp

**`CLAUDE.md`, à la racine, est le fichier d'entrée** : il porte l'identité du
projet, l'état en cinq lignes, les règles, et une table « tâche → fichier » qui
suffit dans presque tous les cas. Cet index-ci ne sert que lorsque la tâche n'y
figure pas.

Un fichier = un sujet. **Ne charger que ce que la tâche demande.**
Chaque fichier s'ouvre sur une ligne « QUAND LIRE » : elle seule décide. Si
elle ne décrit pas la tâche en cours, le fichier n'est pas à ouvrir, même s'il
a l'air proche.

## Stable — ce qui ne bouge presque plus

| Fichier | Lire quand |
|---|---|
| `08-etat.md` | on reprend après une interruption, ou on choisit quoi faire ensuite |
| `12-audit.md` | on choisit le prochain chantier du kit, ou on cherche la preuve d'un bug ou d'une mesure de l'audit du 2026-09-17 |
| `38-audit-artefacts.md` | on choisit un chantier sur les pages publiées (six proposés, A à F), ou on cherche la preuve d'un défaut de page relevé le 2026-09-22 ; ses scripts sont dans `38-audit-scripts/`, sa page dans `artefacts/` |
| `00-INDEX-archive.md` | on relit un chantier clos — chacun y a sa ligne, triée par numéro |
| `75-index-archive.md` | on joue une fiche `IDX*` — chantier **ouvert** « L'index ne garde que le vivant », `IDX1..IDX3` |
| `35-bilan.md` | on doit expliquer le kit — d'où il vient, ce qu'il sait faire aujourd'hui, ce qu'il ne promet pas ; les 22 chantiers chiffrés |
| *(racine du kit)* `methode-chantier.md` | on ouvre un chantier, ou on le découpe en fiches — ici le projet **est** le kit, la méthode est donc à la racine |

## Chantiers — un fichier de fiches par chantier

| Fichier | Lire quand |
|---|---|

## Le kit lui-même — à la racine, hors de ce dossier

Ces fichiers ne se lisent pas en série : chacun répond à une question précise.

| Fichier | Lire quand |
|---|---|
| `skills/<nom>/SKILL.md` | on modifie cette commande-là |
| `agents/fiche.md`, `enchainement.md` | on touche au sous-agent de `/vlp:enchainer`, ou à son contrat de retour |
| `scripts/mesure-tokens.py` | on touche à la mesure des tokens |
| `scripts/vlp.py` | on touche à la mécanique des commandes — carte, extraction, validation, page, hook ; ses sous-commandes sont dans sa docstring |
| `skills/tache/references/` | on touche au blocage, à la page de chantier ou aux contraintes d'une fiche |
| `cloture.md` | on touche aux cinq écritures d'une clôture |
| `ARTEFACTS.md` | on touche aux pages publiées : nommage, URL, budget |
| `README.md` | on change la mise en place, ou la présentation du kit |
