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
| *(racine du kit)* `methode-chantier.md` | on ouvre un chantier, ou on le découpe en fiches — ici le projet **est** le kit, la méthode est donc à la racine |

## Chantiers — un fichier de fiches par chantier

| Fichier | Lire quand |
|---|---|
| `09-enchainer.md` | on joue une fiche `E*` — chantier **clos**, abandonné, « Enchaîner les fiches » |
| `10-mesure.md` | on joue une fiche `M*` — chantier **ouvert** « Mesurer les tokens », `M1..M4` |

## Le kit lui-même — à la racine, hors de ce dossier

Ces fichiers ne se lisent pas en série : chacun répond à une question précise.

| Fichier | Lire quand |
|---|---|
| `commands/<nom>.md` | on modifie cette commande-là |
| `cloture.md` | on touche aux cinq écritures d'une clôture |
| `CONVENTION-FICHIERS.md` | on se demande où vit quoi dans un projet équipé |
| `ARTEFACTS.md` | on touche aux pages publiées : nommage, URL, budget |
| `INSTALLATION.md` | on change la mise en place |
