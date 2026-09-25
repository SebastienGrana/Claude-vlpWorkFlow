> **QUAND LIRE** : on joue une fiche `FFE*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache FFE<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier FFE — Le relecteur ne lit plus le fichier de fiches entier

**À quoi il sert.** `vlp.py relecture` rend `FICHIER=`, le chemin du fichier de fiches entier — la suite
du chantier que `REL` a retirée de la carte. `REL1` : 1 `Read` entier sur 42 relecteurs, 2 par plage.

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 2 fiches, `FFE1` à jouer.

**Session** : 555d49cb-4290-478c-b89c-a33e35bf87b4

## Le socle commun

Image : le correcteur a déjà sa copie ; on cesse de lui tendre le cahier où sont les suivantes.

**Décidé au cadrage (2026-09-26, par l'utilisateur).**

1. Option B : retirer la ligne `FICHIER=` partout, et une consigne d'une ligne dans l'agent.
2. Mesure de l'après : `rel1-carte.py` adapté, relancé plus tard sur de vrais relecteurs ; pas d'essai payant.
3. Dehors : la ligne « fichier de fiches courant » de `carte --relecteur` reste (le chemin est
   de toute façon dans l'en-tête du diff) ; aucun mur dans les worktrees — un critère qui lit
   le fichier de fiches (`valider`, `page`) y serait refusé à tort.

| Où | Quoi |
|---|---|
| `scripts/vlp.py` `cmd_relecture` | écrit `APRÈS=`, `AVANT=`, `FICHIER=` d'une ligne, puis `cmd_socle` et `cmd_extraire` — la fiche et le socle sont **déjà** rendus |
| `scripts/vlp.py`, docstring, entrée `relecture <fiche>` | nomme `FICHIER=` dans la liste de ce qu'imprime la commande |
| `agents/relecture.md`, étape 1 | cite `FICHIER=` dans la sortie de `relecture` |
| `scripts/test-vlp.py`, test « relecture : un fichier hors fiche » | cherche `FICHIER=%s` dans ses `reperes` ordonnés |
| `context AI/38-audit-scripts/rel1-carte.py` | trouve le fichier de fiches par la ligne `FICHIER=` du premier résultat d'outil |

Du Python touché passe `pyright` sur ses fichiers : zéro erreur, compte brut au compte rendu.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `FFE1` | Retirer `FICHIER=` de `relecture` | rien |
| `FFE2` | Faire trouver le fichier à `rel1-carte.py` sans `FICHIER=` | rien |

Les deux sont indépendantes ; FFE1 d'abord, puisque c'est elle qui rend FFE2 nécessaire.

---

<!-- FICHE:FFE1 -->
## FFE1 [x] — Retirer `FICHIER=` de `relecture`

**Session** : 555d49cb-4290-478c-b89c-a33e35bf87b4
**Dépend de** : rien.
**Fichiers** : scripts/vlp.py, scripts/test-vlp.py, agents/relecture.md — et rien d'autre.

**Prompt**
Dans `cmd_relecture`, n'écris plus la ligne `FICHIER=` : la sortie commence par `APRÈS=` puis
`AVANT=`, et le socle suit. Garde la variable interne, qui sert au socle, à la fiche et aux
lignes `HORS FICHE`. Retire `FICHIER=` de la docstring du module (entrée `relecture`).

Dans `agents/relecture.md`, étape 1 : retire `FICHIER=` de la liste, et ajoute une seule
phrase — la fiche et le socle sont dans cette sortie ; n'ouvre pas le fichier de fiches, il
porte la suite du chantier.

Dans le test « relecture : un fichier hors fiche » de `test-vlp.py`, retire `FICHIER=` des
`reperes` et vérifie qu'aucune ligne de la sortie ne commence par `FICHIER=`.

**Critère de fin**
`py scripts/test-vlp.py` : tous les tests passent, compte brut affiché. Mutant : remettre
l'écriture de `FICHIER=` dans `cmd_relecture` — le test « relecture : un fichier hors fiche »
tombe. `pyright scripts/vlp.py scripts/test-vlp.py` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:FFE2 -->
## FFE2 [x] — Faire trouver le fichier à `rel1-carte.py` sans `FICHIER=`

**Session** : 604feeb1-8133-4ead-812f-c613e4dc1688
**Dépend de** : rien.
**Fichiers** : context AI/38-audit-scripts/rel1-carte.py — et rien d'autre.

**Prompt**
Après FFE1, un relecteur ne reçoit plus `FICHIER=` : l'instrument compterait 0 lecture, qu'il
y en ait ou non. Fais-lui reconstituer le chemin autrement : le dossier `APRÈS=` du résultat
de `relecture`, joint au chemin de la ligne « fichier de fiches courant » de la carte reçue
par le relecteur (étendue `(X1..X3)` retirée si elle y est). Vérifie d'abord, sur une
transcription réelle, où ces deux lignes se trouvent. `FICHIER=`, s'il est là, reste prioritaire.

Ajoute une option `--sans-fichier` qui ignore `FICHIER=` et force la nouvelle voie. Une
transcription où aucun chemin n'est trouvé reste signalée sur sa ligne, comme aujourd'hui.
Mets la docstring à jour.

**Critère de fin**
`py "context AI/38-audit-scripts/rel1-carte.py"` puis la même avec `--sans-fichier` : les deux
lignes `TOTAL` donnent les mêmes `entier`, `plage` et `grep`, comptes bruts affichés côte à
côte ; aucune transcription signalée sans chemin dans la seconde qui ne l'était pas dans la
première. Mutant : ne plus retirer l'étendue `(X1..X3)` — les comptes du `--sans-fichier`
tombent. `pyright` sur le fichier : 0 erreur.
<!-- /FICHE -->
