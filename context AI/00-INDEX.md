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
| *(racine du kit)* `methode-chantier.md` | on ouvre un chantier, ou on le découpe en fiches — ici le projet **est** le kit, la méthode est donc à la racine |

## Chantiers — un fichier de fiches par chantier

| Fichier | Lire quand |
|---|---|
| `09-enchainer.md` | on joue une fiche `E*` — chantier **clos**, abandonné, « Enchaîner les fiches » ; commande remise telle quelle le 2026-09-17 |
| `10-mesure.md` | on joue une fiche `M*` — chantier **clos** « Mesurer les tokens », `M1..M4` |
| `11-conso.md` | on joue une fiche `C*` — chantier **clos** « Afficher la conso sur toutes les pages », `C1..C2` |
| `13-tours.md` | on joue une fiche `T*` — chantier **clos** « Compter les tours, pondérer le coût », `T1..T5` |
| `14-bugs.md` | on joue une fiche `B*` — chantier **clos** « Corriger les bugs de l'audit », `B1..B3` |
| `15-reduire.md` | on joue une fiche `R*` — chantier **en cours** « Réduire les tours de `/vlp:tache` », `R1..R4` |

## Le kit lui-même — à la racine, hors de ce dossier

Ces fichiers ne se lisent pas en série : chacun répond à une question précise.

| Fichier | Lire quand |
|---|---|
| `commands/<nom>.md` | on modifie cette commande-là |
| `agents/fiche.md`, `enchainement.md` | on touche au sous-agent de `/vlp:enchainer`, ou à son contrat de retour |
| `scripts/mesure-tokens.py` | on touche à la mesure des tokens |
| `scripts/carte.py` | on touche à la carte injectée par `/vlp:tache` et `/vlp:enchainer` avant leur 1er tour |
| `references/` | on touche au blocage, à la page de chantier ou aux trois contraintes d'une fiche |
| `cloture.md` | on touche aux cinq écritures d'une clôture |
| `CONVENTION-FICHIERS.md` | on se demande où vit quoi dans un projet équipé |
| `ARTEFACTS.md` | on touche aux pages publiées : nommage, URL, budget |
| `INSTALLATION.md` | on change la mise en place |
