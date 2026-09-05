# Installer le kit dans un projet

## Le chemin court — deux copies, une commande

**1. Poser les trois commandes**, une fois par machine :

```bash
cp "<chemin>/Claude-vlpWorkflow/commands/"*.md ~/.claude/commands/
```

Elles deviennent `/chantier`, `/tache` et `/vlp-init`, disponibles partout.

**2. Poser le kit près des projets** — n'importe où, mais `/vlp-init` le
cherche d'abord dans le dossier courant, son parent, puis `~` :

```bash
cp -r "<chemin>/Claude-vlpWorkflow" ~/Claude-vlpWorkflow
```

**3. Équiper le projet.** Ouvrir une session **dans le dossier du projet**, et
lancer :

```
/vlp-init
```

Sept questions, et c'est fini : `CHANTIER.md`, `CLAUDE.md` et le dossier de
contexte sont posés, et la **feuille de route** du projet est publiée comme
artefact. Puis `/clear`, et `/chantier` pour ouvrir le premier chantier.

## Ce que `/vlp-init` demande

Prépare ces sept réponses, elles vont vite :

1. le projet en une phrase — ce qu'il fait, ce qu'il ne fait pas ;
2. un alias court (`md`, `cairn`, `api`) — il ne sert que dans un workspace ;
3. le nom du dossier de contexte (`context AI/` par défaut) ;
4. la **livraison** : la commande qui met le code en place, ou « aucune » ;
5. la **vérification** : une commande que la session lance et lit elle-même,
   ou un geste que seul l'utilisateur peut faire ;
6. trois ou quatre **contraintes d'écriture** propres au projet ;
7. les **chantiers qu'on voit venir** : deux à cinq, une ligne chacun — c'est
   la TODO de départ, celle que la feuille de route affichera.

## Le chemin manuel, si l'on préfère

Même résultat, sans commande :

| Copier | Vers | Puis |
|---|---|---|
| `commands/*.md` | `~/.claude/commands/` | rien |
| `templates/CHANTIER.md` | racine du projet | remplir les `<…>` |
| `templates/CLAUDE.md` | racine du projet | remplir, ou fusionner avec l'existant |
| `templates/context AI/methode-chantier.md` | `context AI/09-chantiers.md` | rien à changer |
| `templates/context AI/00-INDEX.md` | `context AI/00-INDEX.md` | remplir |
| `templates/context AI/NN-etat.md` | `context AI/08-etat.md` | remplir la TODO ordonnée |
| `templates/artefact-feuille-de-route.html` | `context AI/artefacts/` | remplir, publier, et coller l'URL dans `CHANTIER.md` |

`templates/context AI/fichier-de-fiches.md` et `templates/artefact-chantier.html`
ne se copient pas à l'installation : c'est `/chantier` qui s'en sert, une fois
par chantier.

Les artefacts sont optionnels : un projet sans eux marche exactement pareil,
les commandes disent seulement en une ligne qu'elles n'en ont pas. Leur
convention — nommage, URL, budget — est dans `ARTEFACTS.md`.

## Vérifier que ça marche

Depuis le dossier du projet :

```
/chantier
```

Il doit annoncer le projet **sans rien demander** et proposer des chantiers
tirés du fichier d'état. S'il demande lequel, c'est que `CHANTIER.md` n'est pas
à la racine, ou que la session a été ouverte au niveau du workspace.

## Dans un workspace, plusieurs projets équipés

Rien à faire de plus : chaque projet porte son `CHANTIER.md`, et les commandes
les trouvent par `ls */CHANTIER.md`. Depuis le workspace, elles demandent
lequel — ou acceptent l'alias en premier argument : `/tache cairn N2`. Depuis
le dossier d'un projet, l'alias est inutile.
