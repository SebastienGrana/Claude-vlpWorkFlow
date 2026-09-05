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
ls -d ./Claude-vlpWorkflow ../Claude-vlpWorkflow ~/Claude-vlpWorkflow 2>/dev/null
```

Si aucun ne répond, demande son chemin. Ne réinvente pas les gabarits de
mémoire : ils portent des titres de sections que `/tache` lit au `sed`.

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
| `templates/context AI/methode-chantier.md` | `<contexte>/09-chantiers.md` | comment on découpe et on exécute |
| `templates/context AI/00-INDEX.md` | `<contexte>/00-INDEX.md` | un fichier = un sujet |
| `templates/context AI/NN-etat.md` | `<contexte>/08-etat.md` | l'état daté et la TODO ordonnée |
| `templates/artefact-feuille-de-route.html` | `<contexte>/artefacts/feuille-de-route.html` | la page publiable du projet |

Si `CLAUDE.md` existe déjà, **ne l'écrase pas** : ajoute-lui seulement la ligne
de routage vers le fichier de méthode et la section « Économie de contexte »
du gabarit, si elle manque.

Renseigne dans `CHANTIER.md` tout ce que le questionnaire a donné, et laisse
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

## 4. Le point que l'on oublie toujours

Si le projet exclut son contexte de git (`.gitignore` contenant `CLAUDE.md` ou
le dossier de contexte), demande si `CHANTIER.md` doit y être ajouté aussi.
Ne modifie `.gitignore` que sur réponse explicite.

## 5. Rendre la main

Récapitule en quatre lignes : les fichiers posés, l'alias retenu, le lien de la
feuille de route, et la commande suivante — `/clear`, puis `/chantier` depuis le
dossier du projet.
