---
description: Enchaîne les fiches du chantier courant une après l'autre, dans cette session (par défaut), chacune sur une page blanche (agents, un sous-agent neuf) ou en session neuve par script (clear), jusqu'à un arrêt prévu ou le plafond
argument-hint: (rien) | agents [<largeur>] | agents file | clear | <alias> | <alias> agents
allowed-tools: Bash(python3:*), Bash(py:*), Bash(echo:*), PowerShell(python3:*), PowerShell(py:*), PowerShell(echo:*), Skill, Agent, Artifact
---

Arguments reçus :

$ARGUMENTS

Joue à la suite les fiches non cochées du fichier de fiches courant.

Plafond : **5 fiches** par lancement, puis arrêt avec bilan même si tout se
passait bien.

**Sans argument (ou `main`) : aucun sous-agent.** Tu joues chaque fiche
toi-même, par `vlp:tache`, dans cette session (étape 3, point 1) ; ni
`vlp:jouer` ni `vlp:relire`. Le contexte grossit d'une fiche à l'autre.

**`agents` dans les arguments : un sous-agent neuf par fiche**, `vlp:fiche`
lancé par l'outil `Agent` en arrière-plan, jamais deux fiches dans le même
contexte — **plusieurs à la fois, chacune dans son worktree** : 2 d'office, un
nombre fixe cette largeur (`agents 3`) ; `agents file` les joue une à la fois,
sans worktree. Tu ne lis ni le socle ni les fiches : le sous-agent les lit
lui-même. Le contrat qu'il rend (`FAITE`, `RETOUR`, `BLOQUÉE`) est dans
`${CLAUDE_PLUGIN_ROOT}/enchainement.md`, qui fait foi. Le worktree part du commit
courant si `worktree.baseRef` vaut `"head"` dans les réglages — geste de
l'utilisateur, refusé au modèle (`ISO1`) ; sinon d'`origin/main`, où ce qui
n'est pas poussé manque : le sous-agent rend `RETOUR`.

**`clear` dans les arguments (`main clear` se lit `clear`) : une session neuve
par fiche, par script.**
Après l'étape 1, ni plan ni fiche jouée ici : un seul appel, en arrière-plan
(`run_in_background`), depuis la racine du projet (`<python>` : la valeur de `PYTHON=` dans la carte) :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/boucle.py" . --plafond <le plafond ci-dessus> --model opus --effort medium
```

Chaque fiche y est jouée comme après `/clear` puis `/vlp:tache <fiche>` ; ses
arrêts et sa sortie sont dans sa docstring. Annonce-le en une ligne, modèle et
effort compris, puis, à la
notification de fin, recopie les lignes `FICHE`, `ARRÊT` et `TOTAL` telles
quelles. `GARDE:` : montre-la, rien d'autre.

## 1. Trouver le projet et le fichier de fiches courant

La carte du projet, lue avant ton premier tour :

!`py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python "py -3" --enchaine; python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais --enchaine; py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python "py -3" --relais --enchaine; echo fin`

`PROJET=` : c'est le projet ; `COURANT=`, le fichier de fiches courant
(`methode-chantier.md`, « Le chantier ouvert ») ; `CHANTIER.md` suit. `VOISIN=… alias=…` : un
workspace — le sous-agent ne joue que le projet du dossier courant ; dis-le, et
demande de relancer depuis ce dossier. Sortie vide ou consigne de la lancer :
lance-la toi-même, une fois. `AUCUN_PROJET`, `GARDE:`, `COURANT=aucun`,
ou `PROCHAINE=aucune` : arrête-toi — il n'y a rien à
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
(visuel) ») ; tu n'attends pas de réponse. Avec `agents`, dis aussi la largeur et où suivre :
« suivi : panneau Tâches de l'app, clique sur le sous-agent ; Ctrl+O pour le détail ».

## 3. Jouer chaque fiche

Pour chaque fiche de la série, dans l'ordre — en worktree, dès que `lancables` la donne (point 1) :

0. **Arrêt imprévu, sans sous-agent** : sa ligne **Dépend de** nomme une fiche
   ni cochée ni rendue `FAITE` dans ce lancement, ou elle porte un bloc
   **Tentatives** dont une ligne numérotée n'est pas `FAITE refusée à la
   relecture.` (tout lu à l'étape 2). Traite-le comme un `RETOUR` (étape 3 bis).
1. Un seul appel : `Skill`, `skill: "vlp:tache"`, `args` : la fiche — elle
   coche, publie et commite elle-même. Fiche cochée ensuite : passe à la
   suivante ; sinon, c'est un `RETOUR` (étape 3 bis).
   Avec `agents` : l'outil `Agent` à la place — `skill: "vlp:jouer"` attend la
   fin même en `background: true` (bac `ENA2`, 2026-10-12). `subagent_type:
   "vlp:fiche"`, `run_in_background: true`, `isolation: "worktree"` (sauf `file`), `description` : la fiche, `prompt` :
   `Fiche à jouer : <fiche> — Kit : ${CLAUDE_PLUGIN_ROOT}. Ton premier appel, depuis <PROJET=>,
   avec les lectures de ton étape 1 : <python> "<kit>/scripts/vlp.py" carte --python "<python>";
   <python> "<kit>/scripts/vlp.py" socle "<fichier de fiches courant>"; <python> "<kit>/scripts/vlp.py" extraire "<fichier de fiches courant>" <fiche>.
   Pas de PROJET=, une GARDE:, ou une fiche de moins de cinq lignes : rends RETOUR avec la sortie brute.`
   En worktree, `depuis <PROJET=>` devient `depuis ton dossier courant, ton worktree`, et le prompt ajoute :
   `Dans ce premier appel, git rev-parse --git-path vlp-chantier ; puis écris <fichier de fiches courant> dans ce
   fichier (Write) : le post-it du chantier, que la relecture lit.` Ce qui part se lit, à chaque fois, par
   ```bash
   <python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lancables "<fichier de fiches courant>" --max <largeur> --tourne <les lancées pas encore fusionnées>
   ```
   — chaque id de `LANCABLES` part, dans le même message ; relaie les lignes `INDICE:` en une ligne. Le
   plafond compte chaque départ, rejeu compris.
   Puis rends la main sans autre appel : la conversation reste libre. Le
   `Result` arrive dans la **notification de fin**, à un tour suivant. Puis le point 2.
2. Lis le premier mot du `Result` rendu. Ce n'est pas un statut : prends la
   première ligne qui **commence** par `FAITE`, `RETOUR` ou `BLOQUÉE` ; aucune,
   c'est « aucun statut » ci-dessous.
   - `FAITE` sur la fiche `(visuel)` de l'étape 2 : c'est un `RETOUR`. Case
     cochée par le sous-agent : remets `## <fiche> [ ]` (une ligne), puis 3 bis.
   - `FAITE` : relis d'abord la case et la tête du dépôt —
     `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" cocher "<fichier de fiches courant>" <fiche> --verifier`
     (en worktree, ce fichier pris dans le dossier de la ligne `DOSSIER:` du `Result`, ici comme pour la
     relecture et `commiter` ci-dessous). Sortie 1 — case `[ ]`, ou `TÊTE` : le sous-agent a commité — : c'est un
     `RETOUR` (étape 3 bis). `SANS GIT` : ni relecture ni commit, passe à la
     suivante. Sinon, un seul appel : `Agent`, `subagent_type: "vlp:relecture"`,
     `run_in_background: true`, `description` : `relire <fiche>`, `prompt` : `Fiche à relire : <fiche> — Kit : ${CLAUDE_PLUGIN_ROOT}.
     Ton premier appel, depuis <PROJET=>, avec la lecture de ton étape 1 : <python> "<kit>/scripts/vlp.py"
     carte --python "<python>" --relecteur; <python> "<kit>/scripts/vlp.py" relecture <fiche>.
     Pas de PROJET=, ou une GARDE: : rends REFUSÉE avec la sortie brute.` —
     son `Result` à la notification de fin. Premier mot du `Result` (`enchainement.md`, « Relecture ») :
     `ACCEPTÉE` → commite la fiche par ses seuls fichiers, sans demander (`methode-chantier.md`) —
     `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" commiter "<fichier de fiches courant>" <fiche>` ;
     une ligne `HORS:`, relaie-la ; une `GARDE:`, c'est un `BLOQUÉE`. Le sous-agent ne commite jamais. En
     worktree, puis, d'ici : `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" fusionner "<fichier de fiches courant>" <fiche> --worktree "<dossier>"`.
     `FUSIONNÉ` : un bloc `ÉTAT:` dans le `Result` de la fiche → son texte, sans ses deux lignes, dans un
     fichier du dossier temporaire, puis `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" etat "<fichier d'état>" --texte "<ce fichier>"`
     (`CHANTIER.md`, ligne **fichier d'état**) et `git add -- "<fichier d'état>"; git commit -m "État après <fiche>"`.
     `CONFLIT` : la fiche reste dans `--tourne` jusqu'à ce que plus rien ne tourne ni ne parte, puis repart
     (point 1), depuis la version fusionnée. `GARDE:` : un `BLOQUÉE`. Puis passe à la suivante — en worktree,
     relance `lancables`. `REFUSÉE`, ou aucun verdict →
     `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" cocher "<fichier de fiches courant>" <fiche> --refuser "<première ligne du Result>"`
     — en worktree, sur le fichier d'ici, puis `git add -- "<fichier de fiches courant>"; git commit -m "Refus : <fiche>"` :
     le rejeu part d'ici, la fusion veut un arbre propre —,
     puis, sur `REFUSÉE`, `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire
     skills/enchainer/references/refus.md` et suis-le ; sur aucun verdict,
     traite-le comme un `BLOQUÉE` (étape 3 bis). Après la dernière de la série
     — en worktree, quand plus rien ne tourne ni ne part —,
     relance la carte (`vlp.py carte`) : `PROCHAINE=aucune` → étape 5 ; sinon
     étape 4.
   - `RETOUR` ou `BLOQUÉE` : étape 3 bis — en worktree, plus rien de neuf ne part, et celles qui tournent
     finissent d'abord ; de même après le 2e refus d'une même famille (`refus.md`).
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
comptes bruts du critère compris ; « — » pour un arrêt sans sous-agent ; en worktree, son `DOSSIER:`
s'il n'a pas été fusionné — il reste sur le disque. Le
coût se lit sur la session, pas ici : un `Result` ne porte pas d'usage.

Puis régénère la page du chantier, **une seule fois** pour tout le lancement —
sauf si « artefact du chantier » vaut « aucun », si l'étape 5 suit, ou en mode
`main` : chaque `vlp:tache` l'a déjà republiée. La page
porte le nom du fichier de fiches, en `.html`, dans `<contexte>/artefacts/` ;
un `--note` par fiche faite, le critère constaté en une ligne :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" page "<fichier de fiches courant>" --note <fiche> "<critère constaté>"
```

Une `GARDE:` ou une sortie non nulle : une ligne, et continue. Sinon, deux
appels : `Artifact` `action: "read"` sur l'`url` de « artefact du chantier »,
puis `Artifact` avec le `file_path` de la page, cette `url` et `files` : le JSON
de la ligne `FILES` (`ARTEFACTS.md`), sans
`icon`, `label` : les fiches jouées (`E5→E7`). Rien d'autre à lire : les règles de la page sont dans
`skills/tache/references/tache-page.md`, pour `/vlp:tache`. Puis commite la page seule — aucun commit de
fiche ne l'emporte : `git add -- "<page>" "<page, en .md>"; git commit -m "Page du chantier après <E5→E7>"`.

Si un `BLOQUÉE` a clos la série, marque aussi la page bloquée :

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire skills/tache/references/tache-blocage.md
```

## 5. Clore le chantier

Plus aucune fiche non cochée : applique la clôture, à l'identique de
`/vlp:tache` à sa propre étape 7 — cette commande ne la recopie pas. En mode
`main`, cette étape 7 l'a déjà faite : ne relance pas `clore` (un second appel
sort en `GARDE:`), passe à l'affichage du bilan.

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire cloture.md
```

Affiche ensuite le bilan de l'étape 4, puis les deux liens et la suite que
`cloture.md` demande.
