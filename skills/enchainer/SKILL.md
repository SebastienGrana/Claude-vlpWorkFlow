---
description: Enchaîne les fiches du chantier courant une après l'autre, chacune sur une page blanche (sous-agent neuf), jusqu'à un arrêt prévu ou le plafond
argument-hint: (rien) | <alias>
model: sonnet
allowed-tools: Bash(python3:*), Bash(py:*), Bash(echo:*), PowerShell(python3:*), PowerShell(py:*), PowerShell(echo:*), Skill, Artifact
---

Arguments reçus :

$ARGUMENTS

Joue à la suite les fiches non cochées du fichier de fiches courant, chacune
par la skill `vlp:jouer` — forkée dans un sous-agent neuf `vlp:fiche`, jamais
deux fiches dans le même contexte. Tu ne lis ni le socle ni les fiches : la
skill les donne au sous-agent. Le contrat qu'il rend (`FAITE`, `RETOUR`,
`BLOQUÉE`) est dans `${CLAUDE_PLUGIN_ROOT}/enchainement.md`, qui fait foi.

Plafond : **5 fiches** par lancement, puis arrêt avec bilan même si tout se
passait bien.

## 1. Trouver le projet et le fichier de fiches courant

La carte du projet, lue avant ton premier tour :

!`py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py; python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais; py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py --relais; echo fin`

`PROJET=` : c'est le projet, `CHANTIER.md` suit. `VOISIN=… alias=…` : un
workspace — `vlp:jouer` ne joue que le projet du dossier courant ; dis-le, et
demande de relancer depuis ce dossier. Sortie vide ou consigne de la lancer :
lance-la toi-même, une fois. `AUCUN_PROJET`, `GARDE:`, fichier de fiches
courant à « aucun », ou `PROCHAINE=aucune` : arrête-toi — il n'y a rien à
enchaîner.

## 2. Annoncer le plan — un appel

Valide le fichier — un `(visuel)` hors de sa ligne ne se verrait pas —, puis
liste, dans l'ordre du fichier, titres, dépendances, blocs Tentatives et
critères de fin (`<python>` : la valeur de `PYTHON=` dans la carte) :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" valider "<fichier de fiches courant>" --plan
```

Un écart de `valider` : arrête-toi et montre-le. **Garde** : fichier non vide
mais `grep` muet → arrête-toi et montre la sortie brute.

Retiens les fiches non cochées, dans l'ordre ; une fiche cochée n'est ni
rejouée ni vérifiée, même écrite dans cette session. La série s'arrête à la première
dont la ligne `**Critère de fin**` porte `(visuel)` — incluse —, ou au plafond
de 5. Annonce-la en une ligne (« je joue E5 → E7, arrêt prévu à E7
(visuel) ») ; tu n'attends pas de réponse. Dis aussi où suivre : « suivi :
panneau Tâches de l'app, clique sur le sous-agent ; Ctrl+O pour le détail ».

## 3. Jouer chaque fiche

Pour chaque fiche de la série, dans l'ordre :

0. **Arrêt imprévu, sans sous-agent** : sa ligne **Dépend de** nomme une fiche
   ni cochée ni rendue `FAITE` dans ce lancement, ou elle porte un bloc
   **Tentatives** (tout lu à l'étape 2). Traite-le comme un `RETOUR`
   (étape 3 bis).
1. Un seul appel : `Skill`, `skill: "vlp:jouer"`, `args` : la fiche.
2. Lis le premier mot du `Result` rendu. Ce n'est pas un statut : prends la
   première ligne qui **commence** par `FAITE`, `RETOUR` ou `BLOQUÉE` ; aucune,
   c'est « aucun statut » ci-dessous.
   - `FAITE` sur la fiche `(visuel)` de l'étape 2 : c'est un `RETOUR`. Case
     cochée par le sous-agent : remets `## <fiche> [ ]` (une ligne), puis 3 bis.
   - `FAITE` : commite la fiche — `git add -A; git commit -m "<fiche> : <titre>"`,
     sans demander (`methode-chantier.md`) ; le sous-agent ne commite jamais.
     Puis passe à la suivante. Après la dernière de la série, relance la
     carte (`vlp.py carte`) : `PROCHAINE=aucune` → étape 5 ; sinon étape 4.
   - `RETOUR` ou `BLOQUÉE` : étape 3 bis.
   - Aucun statut (le sous-agent s'est arrêté avant son compte rendu) : c'est
     un `RETOUR` — dis-le, avec le `Result` brut.

## 3 bis. Gérer un arrêt

`RETOUR` — pose un questionnaire (`AskUserQuestion`) construit depuis le
`Result`, ou depuis les lignes de l'étape 2 pour un arrêt imprévu : ce qu'on
attend de l'utilisateur, et pourquoi. Si la réponse lève le blocage, coche la
fiche (`## <fiche> [ ]` → `[x]`, une seule ligne) ; sinon, laisse la case.
Aucun autre outil : ni lecture, ni copie, ni vérification, ni correction —
c'est le travail d'une fiche, pas du chef.
Puis prolonge la série — jusqu'à la prochaine `(visuel)` incluse, sans
dépasser le plafond compté depuis le début — et reprends l'étape 3.

`BLOQUÉE` — arrête-toi : le sous-agent a écrit le bloc Tentatives. Étape 4.

## 4. Bilan

Une ligne par fiche jouée : statut, et la première ligne du `Result` —
comptes bruts du critère compris ; « — » pour un arrêt sans sous-agent. Le
coût se lit sur la session, pas ici : un `Result` ne porte pas d'usage.

Puis régénère la page du chantier, **une seule fois** pour tout le lancement —
sauf si « artefact du chantier » vaut « aucun », ou si l'étape 5 suit. La page
porte le nom du fichier de fiches, en `.html`, dans `<contexte>/artefacts/` ;
un `--note` par fiche faite, le critère constaté en une ligne :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" page "<fichier de fiches courant>" --note <fiche> "<critère constaté>"
```

Une `GARDE:` ou une sortie non nulle : une ligne, et continue. Sinon, deux
appels : `Artifact` `action: "read"` sur l'`url` de « artefact du chantier »,
puis `Artifact` avec le `file_path` de la page **et** cette `url`, sans
`favicon`, `label` : les fiches jouées (`E5→E7`). Rien d'autre à lire : les règles de la page sont dans
`skills/tache/references/tache-page.md`, pour `/vlp:tache`.

Si un `BLOQUÉE` a clos la série, marque aussi la page bloquée :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire skills/tache/references/tache-blocage.md
```

## 5. Clore le chantier

Plus aucune fiche non cochée : applique la clôture, à l'identique de
`/vlp:tache` à sa propre étape 7 — cette commande ne la recopie pas.

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire cloture.md
```

Affiche ensuite le bilan de l'étape 4, puis les deux liens et la suite que
`cloture.md` demande.
