---
description: Équipe un projet de la méthode chantiers/fiches — pose CHANTIER.md et le dossier de contexte
argument-hint: (rien) | <chemin du projet>
allowed-tools: Bash(pwd:*), Bash(cd:*), Bash(ls:*), Bash(cat:*), Bash(grep:*), Bash(mkdir:*), Bash(cp:*), Bash(dirname:*), Read, Edit, Write, Artifact
---

Équipe **un** projet de la méthode « chantiers et fiches » : après ça,
`/chantier` et `/tache` marchent dedans sans qu'on ait à leur dire où on est.

Cette session ne code pas et ne cadre aucun chantier : elle pose des fichiers.
Ne lance rien d'autre ensuite ; c'est `/chantier` qui prend la suite, dans une
session neuve.

## 0. Le projet à équiper

Si `$1` est donné, c'est ce dossier. Sinon :

```bash
pwd; ls -d */ 2>/dev/null | head -20; ls CHANTIER.md CLAUDE.md 2>/dev/null
```

- Si le dossier courant ressemble à un projet (du code, un dépôt), c'est lui.
- S'il ressemble à un workspace (plusieurs projets côte à côte), **demande
  lequel** — n'en équipe qu'un à la fois.
- Si `CHANTIER.md` existe déjà, arrête-toi : le projet est déjà équipé. Dis ce
  qu'il contient plutôt que de l'écraser.

## 1. Retrouver le kit

Les gabarits à recopier sont dans le dossier `Claude-vlpWorkflow`.

```bash
ls -d ../Claude-vlpWorkflow ~/Claude-vlpWorkflow 2>/dev/null
```

`./Claude-vlpWorkflow` — une copie **dans** le projet — n'est volontairement
pas cherché : une copie posée là ne se met jamais à jour, et c'est comme ça que
le kit a divergé sur quatre projets sans que rien ne le signale. Il n'en existe
qu'un, à côté des projets ou dans `~`.

Si aucun ne répond, demande son chemin. Ne réinvente pas les gabarits de
mémoire : ils portent des titres de sections et des marqueurs que `/tache` lit
au `sed`.

## 2. Le questionnaire — sept réponses, pas une de plus

Pose-les d'un coup, avec une proposition par défaut pour chacune :

1. **Le projet en une phrase** — ce qu'il fait, et ce qu'il ne fait pas.
2. **L'alias court** (`md`, `cairn`, `api`…) : il ne sert que dans un
   workspace où plusieurs projets sont équipés. Par défaut, le nom du dossier
   en minuscules.
3. **Le dossier de contexte** : `context AI/` par défaut.
4. **La livraison** : la commande qui met le code en place (`./deploy.sh`,
   `npm run build`, ou **aucune**).
5. **La vérification** : comment on sait qu'une fiche est passée. Deux formes
   seulement — une **commande** que la session lance et lit elle-même, ou un
   **geste de l'utilisateur** (recharger dans un jeu, regarder un écran).
6. **Les contraintes d'écriture** propres au projet : les trois ou quatre
   règles qu'on regrette de ne pas avoir écrites. Chemins interdits, API à ne
   jamais appeler, langue du code, dossier qu'on n'édite jamais.
7. **Les chantiers qu'on voit venir** : deux à cinq, en une ligne chacun,
   ordonnés par ce qui débloque le reste. C'est la TODO de départ — elle sera
   remaniée, l'important est qu'elle existe. Si le projet a déjà des notes qui
   la contiennent, propose-la remplie plutôt que de la demander à blanc.

## 3. Poser les fichiers

Recopie depuis le kit, en remplaçant les `<…>` par les réponses :

| Depuis le kit | Vers le projet | Rôle |
|---|---|---|
| `templates/CHANTIER.md` | `CHANTIER.md` (racine) | la carte que lisent `/chantier` et `/tache` |
| `templates/CLAUDE.md` | `CLAUDE.md` (racine) | l'entrée : identité, état, règles, routage |
| `templates/context AI/00-INDEX.md` | `<contexte>/00-INDEX.md` | un fichier = un sujet |
| `templates/context AI/NN-etat.md` | `<contexte>/08-etat.md` | l'état daté et la TODO ordonnée |
| `templates/artefact-feuille-de-route.html` | `<contexte>/artefacts/feuille-de-route.html` | la page publiable du projet |

**Ce qui ne se copie pas, et pourquoi.** `methode-chantier.md`, `cloture.md`
et `templates/context AI/fichier-de-fiches.md` restent dans le kit. Ce sont des
règles de travail, pas des données de projet : recopiées, elles existeraient en
autant d'exemplaires qu'il y a de projets, et une correction de méthode n'en
atteindrait aucun. Là où elles sont, elles servent tous les projets à la fois.

Le partage est celui-ci, et il vaut la peine d'être retenu :

- **le kit porte le moteur** — les commandes, la méthode, la clôture, les
  gabarits ;
- **le projet porte ses données** — `CHANTIER.md`, `CLAUDE.md`, son état, ses
  fichiers de fiches, ses pages publiées.

Un projet équipé avant cette règle garde sa copie de la méthode : sa ligne
« méthode » la nomme, et rien ne va la lui retirer. C'est seulement qu'on n'en
fabrique plus de nouvelle.

Si `CLAUDE.md` existe déjà, **ne l'écrase pas** : ajoute-lui seulement la ligne
de routage vers le fichier de méthode et la section « Économie de contexte »
du gabarit, si elle manque.

Renseigne dans `CHANTIER.md` tout ce que le questionnaire a donné, la ligne
« **méthode** » avec `<kit>/methode-chantier.md`, **et la
ligne `- **kit** :` avec le chemin résolu à l'étape 1** — c'est par elle que
`/chantier` retrouvera ses gabarits sans chercher. Laisse
« fichier de fiches courant : **aucun** » — c'est `/chantier` qui la remplira.

## 3 bis. Publier la feuille de route

La réponse 7 remplit la TODO du fichier d'état **et** la zone `ZONE:todo` du
gabarit `<contexte>/artefacts/feuille-de-route.html`. Remplis aussi l'en-tête
(nom du projet, alias, la phrase de la réponse 1), laisse « Chantier en cours »
sur « aucun », et vide la table des clos.

Publie ensuite, une seule fois :

- `file_path` : `<contexte>/artefacts/feuille-de-route.html`
- `favicon` : `🗺️` — c'est la première publication, c'est la seule fois où il
  se passe
- `description` : `La TODO ordonnée de <Projet> et l'état de ses chantiers.`

Puis **recopie l'URL rendue** dans la ligne « **artefact feuille de route** »
de `CHANTIER.md`, dans le même geste. Une URL non écrite est une URL perdue :
la prochaine session publierait un doublon du même nom.

Si la publication échoue, dis-le en une ligne, laisse la ligne à « aucun » et
continue : le projet est équipé quand même.

## 3 ter. Autoriser la livraison et la vérification

`/tache` n'a **pas** `Bash` ouvert : elle ne peut lire que `sed`, `grep`,
`awk`, `cat`, `tail`, `head`, `ls`, `wc`. Les commandes des réponses 4 et 5 —
`./deploy.sh`, `mvn -q test`, `npm run build`… — n'en font pas partie, et
seront **refusées** à chaque fiche si rien ne les autorise.

Elles se déclarent une fois, dans `.claude/settings.json` **du projet** :

```json
{
  "permissions": {
    "allow": ["Bash(./deploy.sh)", "Bash(mvn -q test)"]
  }
}
```

Écris-y les commandes exactes des réponses 4 et 5, et rien de plus large : le
but est qu'une fiche puisse livrer et vérifier, pas qu'elle puisse tout faire.
Si le fichier existe déjà, **ajoute** à sa liste `allow` sans rien retirer.

Si la livraison est « aucune » et la vérification un geste de l'utilisateur, il
n'y a rien à autoriser — dis-le en une ligne.

## 4. Le point que l'on oublie toujours

Si le projet exclut son contexte de git (`.gitignore` contenant `CLAUDE.md` ou
le dossier de contexte), demande si `CHANTIER.md` doit y être ajouté aussi.
Ne modifie `.gitignore` que sur réponse explicite.

## 5. Rendre la main

Récapitule en quatre lignes : les fichiers posés, l'alias retenu, le lien de la
feuille de route, et la commande suivante — `/clear`, puis `/chantier` depuis le
dossier du projet.
