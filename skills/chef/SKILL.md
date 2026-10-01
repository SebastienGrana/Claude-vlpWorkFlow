---
description: "Prépare le lancement de plusieurs chantiers d'affilée, à toute heure : trie la TODO, pose toutes les questions dans une page à cartes, écrit le plan ; avec `matin`, range la nuit passée : fusion, rapport, réponses"
argument-hint: (rien) | <date du plan AAAA-MM-JJ> | matin [<date de la nuit AAAA-MM-JJ>]
allowed-tools: Bash(python3:*), Bash(py:*), Bash(echo:*), Bash(git branch --show-current:*), Bash(git check-ignore:*), Bash(git rev-parse:*), Bash(git add:*), Bash(git commit:*), PowerShell(python3:*), PowerShell(py:*), PowerShell(echo:*), PowerShell(git branch --show-current:*), PowerShell(git check-ignore:*), PowerShell(git rev-parse:*), PowerShell(git add:*), PowerShell(git commit:*), Read, Write, Artifact
---

Arguments reçus :

$ARGUMENTS

Prépare le lancement de **plusieurs chantiers d'affilée**, joués sans humain : tu juges, les scripts écrivent.
**L'heure est libre** : prépare quand l'utilisateur veut lancer, de jour comme de nuit. Cette session **n'ouvre
aucun chantier et n'écrit aucun code** : elle produit un plan. Un argument qui est une date `AAAA-MM-JJ` est
celle du plan (`--date`) ; sans argument, le jour. L'argument **`matin`** change tout : après la section 0, va à
« Le matin » et saute les sections 1 à 4.

## La carte du projet — lue avant ton premier tour

!`py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py; python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais; py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py --relais; echo fin`

## 0. Avant tout outil

- **Ton modèle** : le chef décide, il se joue en **Opus 5.5** (`claude-opus-5-5`). Si ta session en déclare
  un autre : dis-le en une ligne, demande s'il faut continuer, et **n'appelle aucun outil avant le oui** ;
  sans oui, arrête-toi.
- **`NUIT=1`** : une session de nuit ne joue pas `/vlp:chef` — arrête-toi, voir `nuit.md`.
- **`AUCUN_PROJET`**, ou pas de `PROJET=` : arrête-toi (`/vlp:init`). **`GARDE:`** : arrête-toi, sortie brute.
- **`PLUGIN_RETARD=`** : dis-la en une ligne.
- Un script ou un champ qui manque : arrête-toi et dis lequel, **n'invente rien**.

## 1. Trier : le script d'abord, puis ton jugement

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" trier "<PROJET>"
```

`<python>` : la valeur de `PYTHON=`. Lis la sortie brute ; une `GARDE:` se dit à l'utilisateur et **ne se
contourne pas** : arrête-toi. Puis juge ce que le script ne voit pas :

- **Dépendance implicite** — l'un change ce que l'autre appelle ou mesure : **même canal**, dans l'ordre.
- **Chaque marque** (`MARQUES`) : une carte pour l'utilisateur, ou « écarté : <raison> » ; jamais ignorée.
- **Un taux `indice` ne multiplie rien** : il dit seulement qu'il y a trop peu de mesures.
- **`SOIR <code>`** (le mot est celui du script : « à découper avec l'utilisateur avant le lancement ») :
  étape 2.

## 2. Un chantier à découper avant le lancement

Pose une carte « découpage validé » : tu proposes les fiches (titres, ordre) et le préfixe, il valide. Sa
réponse entre au plan sous `découpage : …`, que la conduite de nuit suit telle quelle ; ou « écarter ce
lancement ». **N'ouvre rien sur `main`** : un chantier ouvert y passerait aux deux canaux (`GARDE` d'`ouvrir`).

## 3. La page à cartes

Rassemble **toutes** les questions en une page, une carte chacune, vulgarisée (une image d'abord, le jargon
après), qui dit **ce que chaque option change** :

- par chantier prêt : les questions de l'étape 3 de `/vlp:chantier`, et le préfixe de son étape 4 ;
- l'ordre et le canal, A ou B, de chaque chantier — à valider ;
- la borne : en **$** et en **nombre de chantiers**, le premier atteint arrête tout ;
- les cartes de l'étape 2 ; une leçon que `trier` imprime va dans le pourquoi de la carte qu'elle touche.

Les fichiers vont dans le dossier du carnet, `<git-common-dir>/vlp-nuit/`, que donne
`git rev-parse --path-format=absolute --git-common-dir` : écris-y `chef-<date>.json`, puis

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" chef page --questions "@<carnet>/chef-<date>.json" --sortie "<carnet>/chef-<date>.html"
```

Sa forme et ses `GARDE:` : docstring de `vlp.py`, `chef page`. `PAGE SAINE <n> blocs`, puis `CARTES D1 Q1…` :
garde cette liste, elle dit quelle réponse est laquelle. Publie la page **telle qu'elle sort** (`Artifact`, sans
la retoucher), donne le lien, et demande à l'utilisateur de coller ses réponses (bouton « Copier mes
réponses »). **N'avance pas avant : rien ne se devine.**

## 4. Le plan

Écris `chef-<date>-plan.json` dans le même dossier — forme : docstring de `vlp.py`, `plan`. Par chantier : le
**canal** et l'**estimé** retenus, chacun avec **sa raison** (une puce de `reponses`), et `découpage : …`
s'il l'a validé ; un chantier qu'il écarte n'y entre pas. Garde ses réponses brutes dans `chef-<date>.md`.

**Avant** `plan ecrire` : `git branch --show-current` ≠ `main`, ou le fichier des nuits ignoré : dis-le et
arrête-toi — **aucun `checkout`**. Ignoré, c'est `git check-ignore "<contexte>/NN-nuits.md"` qui imprime
son nom ; le fichier absent, un nom de cette forme suffit.

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" plan ecrire "<PROJET>" --json "<carnet>/chef-<date>-plan.json" [--date <date>]
```

`PLAN <fichier> · <date> · <n> chantiers` : `git add` de ce fichier **et** de l'index (ligne `index` de
`CHANTIER.md` : le jour où `plan` crée le fichier, il l'y déclare), puis un commit au sujet
`Plan du <date> : <n> chantiers` — qui n'est pas celui d'une fiche. Enfin donne la ligne de lancement de la docstring de
`boucle.py` (« Lancer une nuit ») : `py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/boucle.py" --nuit --lancer "<PROJET>"`,
plus `--date <date>` si le lancement tombe un autre jour. **Tu ne la lances pas** : c'est lui, à l'heure
qu'il veut.

## Le matin

L'argument est `matin`, suivi de la date de la nuit (celle du carnet et des branches `nuit/<date>-*`) **s'il la donne** :
sans date, le script cherche la nuit à ranger, tu ne devines rien. **Un appel par geste**, sa sortie lue en entier ; une
`GARDE:` se montre brute, et tu t'arrêtes.

### M1. Fusionner, puis le rapport

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" matin "<PROJET>" ["<date>"]
```

Sans date, la sortie dit `NUIT <date>` : cette date sert à tous les appels qui suivent. `GARDE: plusieurs nuits à
ranger` : donne-lui les dates, demande laquelle, relance avec elle. `GARDE: aucune nuit à ranger` : dis-le, rien à faire.
Un `ARRÊT … conflit` sur du **code** rend la main à l'utilisateur : tu t'arrêtes. `ATTENTE=` : republie d'abord ces
pages (`ARTEFACTS.md`, « Une publication refusée »). `PLUGIN_RETARD=` : dis-la — `/reload-plugins` est son geste,
jamais le tien. Puis le rapport, sans fusion ni commit, rejouable :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" matin "<PROJET>" "<date>" --rapport "<carnet>/chef-<date>-matin.json"
```

`KIT ?`, `ÉCART` et `NOTE SANS SORTE` : dis chacun en une ligne, ils sont aussi dans le JSON. Ajoute-y **une à trois
leçons**, en cartes de décision (`decisions.cartes`, les cinq champs ; la ligne de la leçon, telle qu'elle s'écrirait,
va dans `choix`), tirées des `cause` et `reecriture` du carnet, dans la forme de `NUI11` (docstring de `vlp.py`,
`nuits lecon`) : une cause, pas un constat. Rien à en tirer : n'en invente pas. Puis la page, comme à la section 3 :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" chef page --questions "@<carnet>/chef-<date>-matin.json" --sortie "<carnet>/chef-<date>-matin.html"
```

Publie-la **telle qu'elle sort** (refus : `ARTEFACTS.md`), donne le lien, demande de coller ses réponses.
**N'avance pas avant.**

### M2. Ses réponses, une à une

- **Leçon gardée** : `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" nuits lecon "<ligne>" --projet "<PROJET>"`. Une
  leçon tenue sur deux nuits (son `N` et ses `nuits`) : propose-la pour `methode-chantier.md` — **deux oui**.
- **Reste versé** : le second oui. Écris la ligne, montre-la, ne commite qu'après son accord (`methode-chantier.md`,
  « La TODO ne grossit pas »).
- **Case 3 ou 4, faire** : comme `cloture.md` (menu de fin) le dit — une tâche, un commit à elle.
- **Mis de côté**, reprendre : nomme la branche, rien d'autre. Abandonner ou rejouer (la nuit suivante repart de `main`) :
  donne `git branch -D <branche>`, **tu ne la lances jamais** ; rejouer garde la ligne de la TODO, que le tri du soir reprend.

### M3. Finir

Un commit du matin pour ce que M2 a écrit : `git add` des fichiers nommés, sujet `Matin <date> : <n> réponses`. Puis
`git push` : **une question à lui seul**, jamais une carte — un push publie, il ne se lance que sur son oui explicite. Enfin
« Pour finir » (`cloture.md`) : le dernier message, sans appel d'outil après lui.

Tu ne fais pas : la fusion à la main, le remplisseur de page, le soir, le reste de `nuit.md`.
