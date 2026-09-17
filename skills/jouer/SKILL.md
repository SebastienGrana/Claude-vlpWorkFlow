---
description: Joue une fiche du chantier courant dans un sous-agent vlp:fiche neuf, et rend FAITE, RETOUR ou BLOQUÉE. Appelée par /vlp:enchainer, une fois par fiche.
argument-hint: <fiche>
context: fork
agent: vlp:fiche
background: false
user-invocable: false
allowed-tools: Bash(python3:*), Bash(py:*), Bash(echo:*), PowerShell(python3:*), PowerShell(py:*), PowerShell(echo:*)
---

Fiche à jouer :

$ARGUMENTS

Kit : ${CLAUDE_PLUGIN_ROOT}

La carte du projet — `PROJET=`, puis `CHANTIER.md` en entier : fichier de fiches
courant, livraison, vérification, contraintes d'écriture :

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3; py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py --relais; echo fin`

La racine est le dossier de `PROJET=` ; le fichier de fiches, la ligne « fichier
de fiches courant » sans sa plage. Dans ton premier appel, avec les lectures de
ton étape 1, extrais le socle et la fiche (`<python>` : la valeur de `PYTHON=` dans la carte) :

```bash
<python> "<kit>/scripts/vlp.py" socle "<fichier de fiches>"; <python> "<kit>/scripts/vlp.py" extraire "<fichier de fiches>" <fiche>
```

Pas de `PROJET=`, une `GARDE:`, ou une fiche de moins de cinq lignes : rends
`RETOUR` avec la sortie brute.
