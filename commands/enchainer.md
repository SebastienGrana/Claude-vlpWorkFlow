---
description: Enchaîne plusieurs fiches du chantier courant, chacune dans un sous-agent neuf, jusqu'à un arrêt prévu ou le plafond
argument-hint: (rien) | <alias>
allowed-tools: Bash(python3:*), Bash(python:*), Bash(grep:*), Bash(cat:*), Bash(ls:*), Bash(pwd:*), Bash(cd:*), Agent, Artifact
---

Arguments reçus :

$ARGUMENTS

Joue à la suite les fiches non cochées du fichier de fiches courant, chacune
dans un sous-agent neuf `vlp:fiche` (`agents/fiche.md`) — jamais deux fiches
dans le même contexte. Le contrat qu'il rend (`FAITE`, `RETOUR`, `BLOQUÉE`)
est dans `${CLAUDE_PLUGIN_ROOT}/enchainement.md`, qui fait foi.

Plafond : **5 fiches** par lancement, puis arrêt avec bilan même si tout se
passait bien.

## 1. Trouver le projet et le fichier de fiches courant

La carte du projet, lue avant ton premier tour par le script que `tache.md`
injecte aussi :

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte 2>/dev/null || python "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte`

`PROJET=` : c'est le projet, `CHANTIER.md` suit. `VOISIN=… alias=…` : si le
premier argument est l'un de ces alias, relance la carte sur ce dossier
(`python "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte "<dossier>"`), sinon demande
lequel. Sortie vide ou consigne de la lancer : lance-la toi-même, une fois.
`AUCUN_PROJET`, `GARDE:`, fichier de fiches courant à « aucun », ou
`PROCHAINE=aucune` : arrête-toi ici — il n'y a rien à enchaîner.

## 2. Annoncer le plan

Valide le fichier — un `(visuel)` hors de sa ligne ne se verrait pas —, puis
liste, dans l'ordre du fichier, les titres et les lignes `**Critère de fin**` :

```bash
PY=$(for p in python3 python; do "$p" -c "" 2>/dev/null && { echo "$p"; break; }; done); "$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" valider "<fichier de fiches courant>"; grep -n -E '^## [A-Z][0-9]|^\*\*Critère de fin\*\*' "<fichier de fiches courant>"
```

Un écart de `valider` : arrête-toi et montre-le.

**Garde.** Si le fichier compte des lignes mais que ce `grep` n'en rend
aucune, arrête-toi et montre la sortie brute — comme une `GARDE:` de la
carte.

Retiens les fiches non cochées (sans `[x]`), dans l'ordre du fichier. La série
à jouer s'arrête à la première rencontrée dont la ligne `**Critère de fin**`
porte `(visuel)` — incluse — ou au plafond de 5, ce qui vient en premier ; les
autres arrêts (dépendance non cochée, bloc Tentatives, décision non tranchée)
ne se voient qu'en jouant la fiche, pas ici.

Annonce cette série en une ligne avant de commencer, par exemple : « je joue
E5 → E7, arrêt prévu à E7 (visuel) ». Tu n'attends pas de réponse.

## 3. Jouer chaque fiche

Une fois, avant la première fiche, extrais le socle — il vaut pour toutes.
S'il ne rend rien, arrête-toi (garde de `tache.md` étape 1) :

```bash
PY=$(for p in python3 python; do "$p" -c "" 2>/dev/null && { echo "$p"; break; }; done); "$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" socle "<fichier de fiches courant>"
```

Puis pour chaque fiche de la série, dans l'ordre :

0. Extrais la fiche. Moins de cinq lignes rendues ou une `GARDE:` : arrête-toi
   et montre la sortie brute (garde de `tache.md` étape 1).
   ```bash
   PY=$(for p in python3 python; do "$p" -c "" 2>/dev/null && { echo "$p"; break; }; done); "$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" extraire "<fichier de fiches courant>" <fiche>
   ```
   Si sa ligne **Dépend de** nomme une fiche non cochée — titres de l'étape 2,
   plus celles cochées depuis —, ou qu'elle porte déjà un bloc **Tentatives**,
   c'est un arrêt imprévu : traite-le comme un `RETOUR` (étape 3 bis) sans
   ouvrir de sous-agent.
1. Ouvre un sous-agent neuf : `Agent`, `subagent_type: "vlp:fiche"`, en
   avant-plan. Son message est autoportant ; `CHANTIER.md`, lu à l'étape 1,
   ne se relit pas — recopie-en les lignes :
   ```
   Racine : <racine du projet>
   Kit : ${CLAUDE_PLUGIN_ROOT}
   Fichier de fiches : <chemin absolu>
   Livraison : <ligne de CHANTIER.md>
   Vérification : <ligne de CHANTIER.md>
   Contraintes d'écriture : <section de CHANTIER.md>
   Socle : <sortie de socle>
   Fiche : <sortie de extraire>
   ```
2. Lis le premier mot du compte rendu, et note pour le bilan les tokens et
   les appels d'outils du bloc `<usage>` que rend `Agent`.
   - `FAITE` : relance la carte (`vlp.py carte`) ; `PROCHAINE=aucune` : il ne
     reste aucune fiche non cochée. C'est alors la
     dernière du chantier : va à l'étape 5 (Clore le chantier), sans jouer la
     suite. Sinon, passe à la fiche suivante de la série — sauf si c'est la
     5ᵉ fiche jouée dans ce lancement : passe alors directement au bilan.
   - `RETOUR` ou `BLOQUÉE` : va à l'étape 3 bis.

## 3 bis. Gérer un arrêt

`RETOUR` — pose un questionnaire (`AskUserQuestion`) construit depuis le
compte rendu du sous-agent, ou, pour un arrêt imprévu (étape 3.0), depuis la
fiche extraite : ce qu'on attend de l'utilisateur, et pourquoi. Si la réponse
lève le blocage, coche la fiche (`## <fiche> [ ]` → `[x]`, une seule ligne) ;
sinon, laisse la case telle quelle.

Puis **prolonge la série** : les fiches non cochées qui suivent, jusqu'à la
prochaine `(visuel)` incluse, sans dépasser le plafond compté depuis le début
du lancement — et reprends l'étape 3 sur la première.

`BLOQUÉE` — arrête-toi : le sous-agent a déjà écrit le bloc Tentatives dans la
fiche. Passe au bilan.

## 4. Bilan

Quand la série est jouée en entier, que le plafond de 5 est atteint, ou qu'un
`BLOQUÉE` a mis fin à l'étape 3, affiche un bilan : une ligne par fiche jouée —
statut, `subagent_tokens` et `tool_uses` lus dans le `<usage>` de son `Agent`,
comptes bruts, jamais estimés ; « — » pour une fiche arrêtée avant sous-agent.

Puis régénère la page du chantier, **une seule fois** pour tout le lancement —
sauf si la ligne « artefact du chantier » vaut « aucun », ou si l'étape 5 suit
(la clôture la republie elle-même) : `vlp.py page`, un `--note` par fiche
faite, puis la publication,

```bash
cat "${CLAUDE_PLUGIN_ROOT}/references/tache-page.md"
```

et, si un `BLOQUÉE` a clos la série, le marquage de la page bloquée :

```bash
cat "${CLAUDE_PLUGIN_ROOT}/references/tache-blocage.md"
```

`label` : les fiches jouées, par exemple `E5→E7`.

## 5. Clore le chantier

Si l'étape 3 a détecté qu'aucune fiche ne reste non cochée, le chantier est
fini : applique la clôture décrite dans `${CLAUDE_PLUGIN_ROOT}/cloture.md`, à
l'identique de ce que `/vlp:tache` fait à sa propre étape 7 — cette commande
ne la recopie pas. Affiche ensuite le bilan de l'étape 4 pour les fiches
jouées dans ce lancement, puis les deux liens et la suite que `cloture.md`
demande de donner.
