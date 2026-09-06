# Installer le kit

## La règle avant tout le reste : un seul kit

Le kit **ne se copie pas dans les projets**. Il vit à **un** endroit — à côté
de tes projets, ou dans `~` — et tous les projets équipés le lisent là.

Ce n'est pas une préférence de rangement. Le kit a existé en six exemplaires,
et ils avaient divergé de cinq cents lignes sans qu'aucun ne le signale : une
copie posée dans un projet est une copie que personne ne met plus à jour. C'est
pour ça que les commandes ne cherchent jamais `./Claude-vlpWorkflow`.

## Le chemin court — une copie, une commande

**1. Poser les cinq commandes**, une fois par machine :

```bash
cp "<chemin>/Claude-vlpWorkflow/commands/"*.md ~/.claude/commands/
```

Elles deviennent `/vlp-init`, `/chantier`, `/tache`, `/vlp-sync` et
`/vlp-check`, disponibles partout. **C'est la seule copie de l'installation** —
et la seule fois où tu la fais à la main : ensuite, `/vlp-sync` la refait pour
toi quand le kit change.

**2. Choisir où vit le kit.** N'importe où, tant qu'il n'y en a qu'un.
`/vlp-init` le cherche dans le dossier parent du projet, puis dans `~` :

```
ProgPerso/
  Claude-vlpWorkflow/   <- le kit, une fois
  MonProjet/            <- les projets, à côté
  UnAutreProjet/
```

Ne le déplace pas après coup sans mettre à jour la ligne « **kit** » des
`CHANTIER.md` déjà posés — `/vlp-check` te dira lesquels mentent.

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
ne se copient pas non plus à l'installation : c'est `/chantier` qui s'en sert,
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
/chantier
```

Il doit annoncer le projet **sans rien demander** et proposer des chantiers
tirés du fichier d'état. S'il demande lequel, c'est que `CHANTIER.md` n'est pas
à la racine, ou que la session a été ouverte au niveau du workspace.

Et quand un doute revient plus tard — la page publiée ne ressemble plus au
fichier, un chantier semble orphelin, une session s'est interrompue au mauvais
moment :

```
/vlp-check
```

Elle mesure et compare sans rien écrire : fichier de fiches présent, fiches
extractibles, cases cochées contre page publiée, lettres non réutilisées, coût
par session, URL bien enregistrées. Elle propose les corrections ; c'est toi
qui décides lesquelles partent.

## Quand le kit change

Tu améliores une commande **dans le kit**, jamais dans `~/.claude/commands/` :
une retouche faite là sera écrasée sans prévenir. Puis :

```
/vlp-sync
```

Elle montre l'écart avant de le combler, et te laisse lire une différence
inattendue plutôt que de l'écraser en silence. Les commandes rechargées
prennent effet à la session suivante.

## Dans un workspace, plusieurs projets équipés

Rien à faire de plus : chaque projet porte son `CHANTIER.md`, et les commandes
les trouvent par `ls */CHANTIER.md`. Depuis le workspace, elles demandent
lequel — ou acceptent l'alias en premier argument : `/tache cairn N2`. Depuis
le dossier d'un projet, l'alias est inutile.
