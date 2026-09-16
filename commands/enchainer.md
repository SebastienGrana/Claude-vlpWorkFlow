---
description: Enchaîne plusieurs fiches du chantier courant, chacune dans un sous-agent neuf, jusqu'à un arrêt prévu ou le plafond
argument-hint: (rien) | <alias>
allowed-tools: Bash(sed:*), Bash(grep:*), Bash(awk:*), Bash(cat:*), Bash(wc:*), Bash(ls:*), Bash(pwd:*), Bash(cd:*), Bash(dirname:*), Agent, Artifact
---

Joue à la suite les fiches non cochées du fichier de fiches courant, chacune
dans un sous-agent neuf `vlp:fiche` (`agents/fiche.md`) — jamais deux fiches
dans le même contexte. Le contrat qu'il rend (`FAITE`, `RETOUR`, `BLOQUÉE`)
est décrit une seule fois, dans `${CLAUDE_PLUGIN_ROOT}/enchainement.md` ;
c'est lui qui fait foi, cette commande ne le recopie pas.

Plafond : **5 fiches** par lancement, puis arrêt avec bilan même si tout se
passait bien.

## 1. Trouver le projet et le fichier de fiches courant

Ce repérage est celui de `tache.md`, étapes 0 et 0 bis — à l'identique, sans
le recopier ici :

```bash
sed -n '/^## 0\. /,/^## 1\. /p' "${CLAUDE_PLUGIN_ROOT}/commands/tache.md"
```

Applique ce que cette plage dit, avec les arguments de cette commande à la
place de ceux de `tache.md` (`$1` est l'alias s'il y a plusieurs projets
voisins, sinon rien — il n'y a pas de fiche à distinguer ici). Si le repérage
s'arrête — aucun `CHANTIER.md`, alias ambigu, fichier de fiches courant à
« aucun » — arrête-toi ici, de la même façon : il n'y a rien à enchaîner.

## 2. Annoncer le plan

Liste, dans l'ordre du fichier, les titres et les lignes `**Critère de
fin**` :

```bash
grep -n -E '^## [A-Z][0-9]|^\*\*Critère de fin\*\*' "<fichier de fiches courant>"
```

**Garde.** Si le fichier compte des lignes mais que ce `grep` n'en rend
aucune, arrête-toi et montre la sortie brute — comme à l'étape 0 bis de
`tache.md`.

Retiens les fiches non cochées (sans `[x]`), dans l'ordre du fichier. La série
à jouer s'arrête à la première rencontrée dont la ligne `**Critère de fin**`
porte `(visuel)` — incluse — ou au plafond de 5, ce qui vient en premier ; les
autres arrêts (dépendance non cochée, bloc Tentatives, décision non tranchée)
ne se voient qu'en jouant la fiche, pas ici.

Annonce cette série en une ligne avant de commencer, par exemple : « je joue
E5 → E7, arrêt prévu à E7 (visuel) ». Tu n'attends pas de réponse.

## 3. Jouer chaque fiche

Une fois, avant la première fiche, extrais le socle — il vaut pour toutes.
S'il ne rend rien, arrête-toi (garde de `tache.md` étape 4) :

```bash
awk '/^## Le socle/{f=1} f && /^## L.*ordre des fiches/{exit} f' "<fichier de fiches courant>"
```

Puis pour chaque fiche de la série, dans l'ordre :

0. Extrais la fiche. Moins de cinq lignes rendues : arrête-toi et montre la
   sortie brute (garde de `tache.md` étape 1).
   ```bash
   sed -n '/^<!-- FICHE:<fiche> -->$/,/^<!-- \/FICHE -->$/p' "<fichier de fiches courant>"
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
   Socle : <sortie de l'awk>
   Fiche : <sortie du sed>
   ```
2. Lis le premier mot du compte rendu, et note pour le bilan les tokens et
   les appels d'outils du bloc `<usage>` que rend `Agent`.
   - `FAITE` : vérifie par `grep -n '^## [A-Z][0-9]'` s'il reste une fiche non
     cochée dans le fichier de fiches. S'il n'en reste aucune, c'est la
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
(la clôture la republie elle-même) : les quatre gestes de `tache.md` 6 bis,

```bash
sed -n '/^## 6 bis/,/^## 7\./p' "${CLAUDE_PLUGIN_ROOT}/commands/tache.md"
```

et, si un `BLOQUÉE` a clos la série, le marquage de blocage de son étape 5 :

```bash
awk '/marque le blocage/,/Cette section se retire/' "${CLAUDE_PLUGIN_ROOT}/commands/tache.md"
```

`label` : les fiches jouées, par exemple `E5→E7`.

## 5. Clore le chantier

Si l'étape 3 a détecté qu'aucune fiche ne reste non cochée, le chantier est
fini : applique la clôture décrite dans `${CLAUDE_PLUGIN_ROOT}/cloture.md`, à
l'identique de ce que `/vlp:tache` fait à sa propre étape 7 — cette commande
ne la recopie pas. Affiche ensuite le bilan de l'étape 4 pour les fiches
jouées dans ce lancement, puis les deux liens et la suite que `cloture.md`
demande de donner.
