# Installer le kit

## La règle avant tout le reste : le kit ne se copie pas

Le kit est un **plugin Claude Code**. Il vit à **un** endroit — à côté de tes
projets, ou dans `~` — et il est *chargé* depuis là. Il n'en existe aucune
copie : ni dans les projets, ni dans `~/.claude/commands/`.

Ce n'est pas une préférence de rangement. Le kit a existé en six exemplaires,
qui avaient divergé de cinq cents lignes sans qu'aucun ne le signale : une
copie posée quelque part est une copie que personne ne met plus à jour. Le
plugin ne résout pas ce problème en le surveillant — il lui retire son terrain.

## Le chemin court — un lien, et c'est tout

**1. Choisir où vit le kit.** N'importe où, tant qu'il n'y en a qu'un :

```
ProgPerso/
  Claude-vlpWorkflow/   <- le kit, une fois
  MonProjet/            <- les projets, à côté
  UnAutreProjet/
```

**2. Le déclarer à Claude Code**, une fois par machine. Un dossier posé dans
`~/.claude/skills/` et portant un `.claude-plugin/plugin.json` se charge tout
seul, dans tous les projets, sans marketplace ni installation. Et ce dossier
peut être un **lien** vers le kit réel — donc rien n'est copié.

Sur Windows (PowerShell, sans droits administrateur) :

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\vlp" -Target "<chemin>\Claude-vlpWorkflow"
```

Sur macOS ou Linux :

```bash
ln -s "<chemin>/Claude-vlpWorkflow" ~/.claude/skills/vlp
```

Les commandes deviennent `/vlp:init`, `/vlp:chantier`, `/vlp:tache` et
`/vlp:check`, disponibles partout. Le préfixe `vlp:` n'est pas décoratif :
c'est le nom du plugin, et il évite qu'un `/tache` d'ailleurs prenne la place
du tien.

**Si tu déplaces le kit**, refais le lien — et mets à jour la ligne
« **kit** » des `CHANTIER.md` déjà posés, qui la mentionne pour les humains.
`/vlp:check` te dira lesquels mentent.

**3. Équiper le projet.** Ouvrir une session **dans le dossier du projet**, et
lancer :

```
/vlp:init
```

Sept questions, et c'est fini : `CHANTIER.md`, `CLAUDE.md` et le dossier de
contexte sont posés, et la **feuille de route** du projet est publiée comme
artefact. Puis `/clear`, et `/vlp:chantier` pour ouvrir le premier chantier.

## Ce que `/vlp:init` demande

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
| *(rien — le lien de l'étape 2 suffit)* | — | les commandes se chargent depuis le kit |
| `templates/CHANTIER.md` | racine du projet | remplir les `<…>`, dont la ligne « kit » |
| `templates/CLAUDE.md` | racine du projet | remplir, ou fusionner avec l'existant |
| `templates/context AI/00-INDEX.md` | `context AI/00-INDEX.md` | remplir |
| `templates/context AI/NN-etat.md` | `context AI/08-etat.md` | remplir la TODO ordonnée |
| `templates/artefact-feuille-de-route.html` | `context AI/artefacts/` | remplir, publier, et coller l'URL dans `CHANTIER.md` |

**Ce qui ne se copie jamais.** `methode-chantier.md` et `cloture.md` restent
dans le kit : ce sont des règles de travail, pas des données de projet, et les
commandes les y lisent au moment voulu. Recopiées dans chaque projet, elles
existeraient en autant d'exemplaires qu'il y a de projets, et une correction de
méthode n'en atteindrait aucun.

`templates/context AI/fichier-de-fiches.md` et `templates/artefact-chantier.html`
ne se copient pas non plus à l'installation : c'est `/vlp:chantier` qui s'en sert,
une fois par chantier.

Un projet équipé **avant** cette règle garde sa copie de la méthode — sa ligne
« méthode » la nomme, et rien ne va la lui retirer. On cesse simplement d'en
fabriquer de nouvelles.

Les artefacts sont optionnels : un projet sans eux marche exactement pareil,
les commandes disent seulement en une ligne qu'elles n'en ont pas. Leur
convention — nommage, URL, budget — est dans `ARTEFACTS.md`.

## Vérifier que ça marche

Depuis le dossier du projet :

```
/vlp:chantier
```

Il doit annoncer le projet **sans rien demander** et proposer des chantiers
tirés du fichier d'état. S'il demande lequel, c'est que `CHANTIER.md` n'est pas
à la racine, ou que la session a été ouverte au niveau du workspace.

Et quand un doute revient plus tard — la page publiée ne ressemble plus au
fichier, un chantier semble orphelin, une session s'est interrompue au mauvais
moment :

```
/vlp:check
```

Elle mesure et compare sans rien écrire : fichier de fiches présent, fiches
extractibles, cases cochées contre page publiée, lettres non réutilisées, coût
par session, URL bien enregistrées. Elle propose les corrections ; c'est toi
qui décides lesquelles partent.

## Quand le kit change

Tu édites le fichier dans le kit. C'est fini — il n'y a **rien à
synchroniser** : le plugin lit le kit là où il est, il n'en a pas de copie.

Pour que la session en cours voie la modification :

```
/reload-plugins
```

Sinon, la session suivante la verra d'elle-même.

C'est le vrai gain de la version plugin : la question « ma copie installée
est-elle à jour ? » n'a plus de sens, parce qu'il n'y a plus de copie.

## Dans un workspace, plusieurs projets équipés

Rien à faire de plus : chaque projet porte son `CHANTIER.md`, et les commandes
les trouvent par `ls */CHANTIER.md`. Depuis le workspace, elles demandent
lequel — ou acceptent l'alias en premier argument : `/vlp:tache cairn N2`. Depuis
le dossier d'un projet, l'alias est inutile.
