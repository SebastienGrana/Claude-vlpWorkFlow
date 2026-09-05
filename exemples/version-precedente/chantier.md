---
description: Ouvre une séance de travail : propose les chantiers possibles, puis cadre celui qu'on choisit en fiches
argument-hint: (rien) | md | md annulation
allowed-tools: Bash(cd:*), Bash(sed:*), Bash(grep:*), Bash(ls:*), Read, Edit, Write
---

Ouvre une séance de travail. Selon ce qui est donné :

- **rien** → demande le projet, puis propose les chantiers possibles ;
- **`$1` seul** (`md` ou `cairn`) → propose les chantiers possibles de ce projet ;
- **`$1` et `$2`** → cadre directement le chantier `$2`.

Dans tous les cas, cette session **n'écrit pas de code** : elle produit un
fichier de fiches, et rien d'autre. Le code viendra après, une fiche par
session, via `/tache $1 <fiche>`.

## La règle qui prime sur tout : cadrer coûte moins cher que se tromper

Le cadrage se paye **une fois** ; ce qu'il oublie se repaye à chaque fiche.
Donc lis peu, mais lis juste, et **demande plutôt que deviner** : au moindre
choix ouvert — quel chantier, l'ordre des fiches, une frontière, un compromis
— pose un questionnaire au lieu de trancher seul.

N'ouvre aucun fichier que les étapes ci-dessous ne nomment pas. Pas d'agent,
pas de recherche large.

## 0. La table des projets

| `$1` | Dossier | Méthode | Chantiers possibles | Préfixe de fiche |
|---|---|---|---|---|
| `md` | `C:/Users/<utilisateur>/Documents/ProgPerso/MapDecorator` | `context AI/09-chantiers.md` | `context AI/08-etat.md` (la TODO ordonnée) | une lettre libre (`T`, `U` sont pris) |
| `cairn` | `C:/Users/<utilisateur>/Documents/ProgPerso/Cairn-VlpLib` | `context AI/21-methode-chantier.md` | `context AI/20a-chantiers.md`, puis `context AI/10-etat.md` | une lettre libre |

Si `$1` est vide, demande lequel des deux avant d'aller plus loin. Si `$1` n'est
ni `md` ni `cairn`, arrête-toi et dis-le.

```bash
cd "<dossier de la table>" && pwd
```

## 1. Lire la méthode, puis les chantiers possibles

Dans cet ordre, ces fichiers, en entier — ils sont courts — et rien d'autre :

1. le fichier « **Méthode** » : ce qu'est un fichier de fiches, à quoi
   ressemble une fiche ;
2. le ou les fichiers « **Chantiers possibles** » : ce qui reste à faire, et
   ce qui est déjà fait — pour ne pas refiche du travail existant.

## 2. Si le chantier n'est pas donné : le proposer

Saute cette étape si `$2` est renseigné.

Sinon, sors de ces fichiers **deux à quatre chantiers candidats**, et pose un
questionnaire pour choisir. Pour chacun, dis en une ou deux lignes :

- ce qu'il apporte, concrètement ;
- ce qu'il coûte, en nombre de fiches estimé ;
- ce qu'il **débloque ou bloque** — une dépendance connue.

Donne ton avis, y compris sur ceux que tu écartes : dis lequel tu ferais en
premier et pourquoi. L'utilisateur veut un échange d'idées, pas un menu.

Si un chantier est déjà ouvert (un fichier de fiches avec des fiches non
cochées, visible dans la table de `~/.claude/commands/tache.md`), dis-le
**avant** de proposer autre chose : on n'en ouvre pas deux à la fois.

## 3. Comprendre le chantier retenu — en questions

Ne présume pas de ce que son nom veut dire. Pose un questionnaire qui couvre :

- **Le résultat visible** : à quoi on saura que le chantier est fini.
- **La frontière** : ce qui est dedans, et surtout ce qui est **dehors**.
- **Les inconnues** : ce qu'il faudra mesurer ou vérifier avant d'écrire.

Puis, et seulement alors, ouvre les fichiers de contexte que ses réponses
désignent — via la table de routage de `CLAUDE.md` si tu ne sais pas lequel.
Un par question, pas leurs voisins.

## 4. Proposer le découpage, avant de l'écrire

Annonce en clair la liste des fiches : un titre chacune, une ligne de contenu,
et les dépendances. Demande validation, et propose explicitement de fusionner
ou de scinder. Une fiche vise **une séance** : si son prompt fait plus de vingt
lignes, c'est deux fiches.

## 5. Écrire le fichier de fiches

Un fichier de `context AI/`, numéroté à la suite, contenant dans cet ordre :

1. la ligne « **QUAND LIRE** » ;
2. l'état du chantier en deux lignes ;
3. une section `## Le socle commun` : les API, invariants et noms que *toutes*
   les fiches utilisent — c'est la seule plage que `/tache` relira à chaque
   fiche, donc rien d'inutile dedans ;
4. une section `## L'ordre des fiches` : la liste et les dépendances ;
5. les fiches, séparées par `---`, au format donné par le fichier « Méthode ».

Ces deux titres de section se recopient **à l'identique** : `/tache` les lit
par `sed`, un titre reformulé casse l'extraction.

## 6. Déclarer, puis rendre la main

Trois écritures, le jour même — un index qui ment coûte plus cher que le
fichier lui-même :

1. une ligne dans `context AI/00-INDEX.md` ;
2. une ligne dans la table de routage de `CLAUDE.md` ;
3. la ligne « Fichier de fiches courant » du projet dans la table de l'étape 0
   de `C:/Users/<utilisateur>/.claude/commands/tache.md`.

Puis arrête-toi : annonce la première fiche à jouer, et rappelle de faire
`/clear` avant de lancer `/tache $1 <fiche>`. **N'enchaîne pas sur la première
fiche dans cette session** — elle traînerait derrière elle tout le cadrage, ce
qui est exactement ce que la méthode évite.
