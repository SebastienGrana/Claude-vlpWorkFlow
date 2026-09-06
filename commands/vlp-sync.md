---
description: Recopie les commandes du kit vers ~/.claude/commands — le kit source fait foi
argument-hint: (rien) | <chemin du kit>
allowed-tools: Bash(ls:*), Bash(cat:*), Bash(cp:*), Bash(diff:*), Bash(wc:*), Bash(mkdir:*)
---

Met à jour les commandes installées (`~/.claude/commands/`) depuis le kit
source. Rien d'autre : pas de code, pas de chantier, pas de publication.

Cette commande existe parce que le kit a déjà divergé — six copies, cinq cents
lignes d'écart, et aucune alarme. La règle qui l'évite tient en une phrase :
**on édite le kit, on synchronise ; jamais l'inverse.**

## 1. Trouver le kit source

Si `$1` est donné, c'est lui. Sinon :

```bash
ls -d ../Claude-vlpWorkflow ~/Claude-vlpWorkflow 2>/dev/null
```

Un dossier `Claude-vlpWorkflow` **à l'intérieur d'un projet** n'est pas un kit
source : c'est une copie oubliée. Si tu en croises un, dis-le et propose de le
supprimer, ne synchronise pas depuis lui.

Si les deux répondent, **demande lequel** — n'en devine pas un.

## 2. Montrer l'écart avant de le combler

```bash
for f in "<kit>"/commands/*.md; do
  n=$(basename "$f")
  if [ -f ~/.claude/commands/"$n" ]; then
    d=$(diff -q "$f" ~/.claude/commands/"$n" >/dev/null 2>&1 && echo identique || echo DIFFERENT)
  else
    d=ABSENT
  fi
  echo "$n : $d"
done
```

Annonce la liste telle quelle, puis **le sens de la copie** : le kit écrase
l'installé. Si un fichier installé est `DIFFERENT`, c'est peut-être une
retouche faite au mauvais endroit — propose de la lire (`diff`) avant de
l'écraser. Une modification qu'on écrase sans l'avoir vue est une modification
perdue.

## 3. Copier

```bash
mkdir -p ~/.claude/commands
cp "<kit>"/commands/*.md ~/.claude/commands/
ls -la ~/.claude/commands/*.md
```

## 4. Rendre la main

Deux lignes : les fichiers copiés, et le rappel que les commandes rechargées
prennent effet à la session suivante (`/clear`).

Les **gabarits** (`templates/`) ne se copient pas ici : ils restent dans le kit,
où `/chantier` et `/tache` les lisent par le chemin de la ligne « kit ».
