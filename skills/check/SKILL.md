---
description: Vérifie qu'un projet équipé est cohérent — fichiers, cases cochées, page publiée, coûts
argument-hint: (rien) | <chemin du projet>
allowed-tools: Bash(python3:*), Bash(py:*), Bash(echo:*), PowerShell(python3:*), PowerShell(py:*), PowerShell(echo:*), Read, Artifact
---

Contrôle un projet équipé de la méthode. **Cette commande n'écrit rien.** Elle
mesure, elle compare, elle dit ce qui cloche, et elle propose des corrections
que l'utilisateur accepte ou non. Si elle se met à réparer d'elle-même, elle
devient la septième source de vérité.

À lancer quand on doute : après une session interrompue, avant de reprendre un
chantier laissé de côté, ou quand la page publiée ne ressemble plus au fichier.

## 1. Lire la carte

!`py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py; python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais; py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py --relais; echo fin`

`<python>`, plus bas : la valeur de `PYTHON=` ci-dessus.

Retiens : le **kit**, le **dossier de contexte**, le **fichier de fiches
courant**, l'**artefact du chantier**, l'**artefact feuille de route**.

Si la carte ne dit pas `PROJET=`, le projet n'est pas équipé : dis-le, propose
`/vlp:init`, et arrête-toi. Rien d'autre n'a de sens sans lui.

## 2. Les huit vérifications

Lance-les d'un bloc, puis commente la sortie ligne à ligne.

**A — Le fichier de fiches courant existe.**

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lignes "<fichier de fiches courant>" "<contexte>/*.md"
```

Une ligne « courant » qui nomme un fichier absent envoie chaque `/vlp:tache` dans
le vide. Une ligne « aucun » alors qu'un fichier de chantier récent n'est pas
clos est l'erreur inverse : un chantier orphelin, que plus rien ne rouvrira.

**B — Les fiches sont extractibles.**

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" valider "<fichier de fiches courant>"
```

Une ligne par écart — marqueurs, sections, critère —, puis le bilan
`VALIDE|INVALIDE`. Un marqueur ouvrant sans son fermant ferait avaler à
l'extraction tout le reste du fichier ; un titre sans marqueurs n'est pas
extractible du tout.

**C — Les cases cochées et la page publiée disent la même chose.**

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" page "<fichier de fiches courant>" "<artefact du chantier local>" --verifier
```

`--verifier` n'écrit rien. Le fichier a raison : sur `EN RETARD`, **la page
est en retard** — dis-le, nomme les fiches des lignes `ÉCART:`, et propose de
la régénérer, sans le faire tant que l'utilisateur n'a pas répondu.

**D — Les lettres de fiches ne se marchent pas dessus.**

La ligne « Lettres de fiche déjà prises » est dans la carte, les fichiers du
dossier de contexte dans la sortie de **A** — rien à relancer.

Chaque fichier de chantier consomme une lettre. Une lettre réutilisée fait que
`/vlp:tache D2` trouve deux fiches et en joue une au hasard.

**E — Le coût par session.**

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lignes "<fichier de fiches courant>" "<artefact du chantier local>"
```

Le socle est compté dans le bilan de `valider`, en B.

Un avertissement de socle en B, ou une page au-delà de `SEUIL_PAGE` : ils se
relisent à *chaque* fiche. Dis de combien et propose quoi retirer.

**F — Les URL sont écrites.**

Les deux lignes d'artefact de `CHANTIER.md` portent-elles une URL, ou encore
« aucun » ? Une URL non écrite n'est pas récupérable : la session suivante
publierait un doublon du même nom au lieu de mettre à jour la page.

Pour vérifier qu'une URL est vivante, `Artifact action:"read"` — **une seule**,
celle du chantier. Ne relis pas la feuille de route en même temps : le but est
de mesurer un coût, pas de le doubler.

**G — Le plugin est bien chargé, et c'est le bon kit.**

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lignes "${CLAUDE_PLUGIN_ROOT}" "${CLAUDE_PLUGIN_ROOT}/methode-chantier.md" "${CLAUDE_PLUGIN_ROOT}/cloture.md" "~/.claude/commands/*.md"
```

Trois choses à lire dans cette sortie :

1. **Le chemin réel de la ligne `DOSSIER`** doit être le kit réel — celui que la
   ligne « kit » de `CHANTIER.md` nomme. S'ils diffèrent, deux kits coexistent :
   dis lesquels, et lequel des deux les commandes utilisent vraiment (c'est
   celui du plugin).
2. **Si `${CLAUDE_PLUGIN_ROOT}` sort tel quel**, sans être remplacé, cette
   commande ne tourne pas dans le plugin mais en copie simple. Dis-le : c'est
   exactement la configuration que le plugin remplace.
3. **Si `~/.claude/commands/` contient encore `chantier.md` ou `tache.md`**,
   d'anciennes copies traînent. Elles offrent un `/chantier` et un `/tache` sans
   préfixe, qui ne sont plus mis à jour et qui divergeront. Propose de les
   déplacer — pas de les supprimer.

**H — Les renvois mènent quelque part.**

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" renvois .
```

Chaque ligne `ABSENT:` est un fichier que l'index ou le routage de `CLAUDE.md`
nomme et qui n'existe pas : une session l'ouvrira pour rien. Propose de retirer
la ligne, ou de créer le fichier s'il manque vraiment. Un `AVERTISSEMENT:` avant
`POIDS` dit un fichier de tête au-delà du seuil de `vlp.py` : à compacter, pas une erreur.

## 3. Rendre le verdict

Une liste, une ligne par vérification, de `A` à `H` : `A ✓` ou
`A ✗ — <ce qui cloche>`.
Affiche **les comptes bruts à côté du verdict** (« 4 contre 6 »).

Puis les corrections proposées, **par ordre de gravité**, chacune en une ligne
avec le geste exact. Et rien de plus : c'est l'utilisateur qui décide laquelle
part, et dans quelle session.
