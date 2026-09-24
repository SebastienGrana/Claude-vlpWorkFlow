---
description: Relit une fiche rendue FAITE dans un sous-agent vlp:relecture neuf, avant son commit, et rend ACCEPTÉE ou REFUSÉE. Appelée par /vlp:enchainer, une fois par FAITE.
argument-hint: <fiche> [<sha>]
context: fork
agent: vlp:relecture
background: false
user-invocable: false
allowed-tools: Bash(python3:*), Bash(py:*), Bash(echo:*), PowerShell(python3:*), PowerShell(py:*), PowerShell(echo:*)
---

Fiche à relire, et le commit s'il y en a un :

$ARGUMENTS

Kit : ${CLAUDE_PLUGIN_ROOT}

La carte du projet — `PROJET=`, puis `CHANTIER.md` en entier :

!`py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py; python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais; py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python py --relais; echo fin`

La racine est le dossier de `PROJET=`. Ton premier appel, depuis elle, avec la
lecture de ton étape 1 (`<python>` : la valeur de `PYTHON=` dans la carte ; `--sha`
seulement si un commit est donné) :

```bash
<python> "<kit>/scripts/vlp.py" relecture <fiche> --sha <sha>
```

Pas de `PROJET=`, ou une `GARDE:` : rends `REFUSÉE` avec la sortie brute.
