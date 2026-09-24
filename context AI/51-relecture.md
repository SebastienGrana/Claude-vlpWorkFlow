> **QUAND LIRE** : on joue une fiche `REV*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache REV<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier REV — Relire chaque fiche avant son commit

**À quoi il sert.** `/vlp:enchainer` commite un `FAITE` à case cochée sans relire ; la
nuit du 2026-09-24, dix fiches de code sur dix étaient à reprendre (TODO n° 48). Un
relecteur neuf relira chaque `FAITE` avant le commit, et un refus arrêtera la chaîne.

**Fait.** Rien. Ouvert le 2026-09-24, cadré en 4 fiches, `REV1` à jouer.

**Session** : 2f9a46f3-70ad-4145-a7c8-ada5aefa0034

## Le socle commun

**Le circuit visé**, à chaque `FAITE` d'`/vlp:enchainer` — aujourd'hui
`skills/enchainer/SKILL.md:68-74` : `cocher --verifier`, puis le commit.

1. Le chef lance `vlp.py cocher <fichier> <fiche> --verifier` : case `[x]`, et le dernier
   commit n'est pas du sous-agent. Sortie 1 : `RETOUR`, comme aujourd'hui. `SANS GIT` :
   rien ne se commite, fiche suivante sans relecture.
2. `Skill`, `skill: "vlp:relire"`, `args` : `<fiche> [<sha>]` — skill forkée, agent
   `vlp:relecture` neuf. Il lance `vlp.py relecture`, lit le diff entier, rejoue dans
   AVANT puis dans APRÈS les commandes que le diff touche, applique en dernier le mutant
   du critère dans APRÈS, puis `relecture --retirer`. Premier mot : `ACCEPTÉE — <ce qui
   a été rejoué, comptes bruts>` ou `REFUSÉE — <défauts, une ligne>`.
3. `ACCEPTÉE` : le commit d'aujourd'hui, fiche suivante. `REFUSÉE`, ou aucun statut :
   `vlp.py cocher <fichier> <fiche> --refuser "<première ligne du Result>"`, puis arrêt
   comme un `BLOQUÉE` — bilan, page marquée bloquée. La reprise se fait par `/vlp:tache`.

**Décidé au cadrage.** Toute fiche `FAITE` est relue, code ou doc (`MTK2`, de la doc,
disait faux deux fois). Le relecteur tourne sur `opus`, au choix de l'utilisateur —
`sonnet` était proposé.

**Invariants.**
- `HEAD` ne bouge pas avant `ACCEPTÉE` : l'instantané de `relecture` passe par un index
  temporaire (`GIT_INDEX_FILE`), jamais par l'index réel ni par un commit de branche.
- Le relecteur n'écrit jamais sous `PROJET=` et ne lance aucune commande `git` : le
  script crée et retire AVANT et APRÈS (`skills/tache/references/tache-blocage.md:48-51`).
  Une sous-commande qui écrit ne se rejoue que dans AVANT ou APRÈS.
- Le contrat du relecteur vit dans `enchainement.md` ; l'agent, la skill et la méthode y
  renvoient sans le recopier.
- Fiche de code : le test s'écrit d'abord et se voit tomber ; le critère nomme son
  mutant (`methode-chantier.md`, « Anatomie d'une fiche »).

**Ce qui existe** (au 2026-09-24).

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `cmd_cocher` | `scripts/vlp.py:470` | `--verifier` : `CASE <fiche> [x]` sort 0, `[ ]` sort 1 ; `--date` |
| `fichier_courant` | `scripts/vlp.py:234` | le fichier de fiches d'une carte, `None` s'il vaut « aucun » |
| `cmd_extraire`, `socle` | `scripts/vlp.py:372`, docstring `:17-22` | la fiche entre marqueurs ; le socle |
| `COMMIT_FICHE` | `scripts/vlp.py:955` | `^([A-Z]{1,3}[0-9]+) :` — laisse passer `VAL1:` |
| `verifier(nom, cond, sortie)` | `scripts/test-vlp.py:55` | un test ; dépôts Git bâtis comme à `:490` |
| bloc **Tentatives** | `skills/tache/references/tache-blocage.md:14-19` | son format, sous le titre |
| `skills/jouer/SKILL.md`, `agents/fiche.md` | — | les modèles de la skill et de l'agent neufs |

Une ligne **Fichiers** nomme ses chemins entre accents graves, parfois sur deux lignes et
mêlés de noms de fonction (`context AI/49-cadrage-compte.md`, fiche `CAD1`).

**Les témoins** — commits de sous-agent hors `HEAD` ; leurs défauts sont au journal de
`context AI/08-etat.md`, entrées « <fiche>, relue par le chef ».

| Fiche | Fautif | Corrigé | Défaut du journal |
|---|---|---|---|
| `CAD1` | `e41925c` | `8bb748d` | tests relâchés (cinq `in`) ; session entre marqueur et titre |
| `PLA1` | `eb2a6b0` | `7d16873` | plage écrite deux fois, dans `creer` puis `regenerer` |
| `VAL1` | `72035f2` | `c5123af` | `claude_exe=` non initialisé ; commentaire, message et README repris |

**Dehors.** `/vlp:tache` ; le hook `SubagentStop` (`CON`) ; le `CLAUDE.md` global dans
les sous-agents (`GLO`) ; le modèle de `vlp:fiche` ; un projet sans Git, qui reste sans
relecture.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `REV1` | Préparer la relecture par script | rien |
| `REV2` | Contrôler la tête et refuser par script | rien |
| `REV3` | Écrire le relecteur et le brancher | `REV1`, `REV2` |
| `REV4` | Prouver la relecture sur les commits de la nuit | `REV3` |

`REV1` et `REV2` se jouent dans n'importe quel ordre. Toutes par `/vlp:tache` : la
relecture n'existe pas encore.

---

<!-- FICHE:REV1 -->
## REV1 [ ] — Préparer la relecture par script

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (sous-commande `relecture`, docstring du module),
`scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `relecture <fiche> [--sha S]`, et `relecture --retirer`. Tests
d'abord, vus en échec.

- Sans `--sha`, un instantané de l'arbre du dépôt courant — suivis et non suivis, selon
  `.gitignore` — en objet commit de parent `HEAD` : index temporaire (`GIT_INDEX_FILE`),
  `read-tree HEAD`, `add -A`, `write-tree`, `commit-tree`. Avec `--sha`, ce commit-là.
- Deux worktrees détachés dans le dossier temporaire du système (`tempfile`) : APRÈS sur
  le commit, AVANT sur son parent ; ceux d'un appel précédent (`vlp-relecture-*`) sont
  retirés d'abord.
- Imprime, dans l'ordre : `APRÈS=<dossier>`, `AVANT=<dossier>`, `FICHIER=<chemin>` — le
  fichier de fiches que nomme la carte d'APRÈS (`fichier_courant`) —, le socle et la
  fiche comme `socle` et `extraire`, `git diff --name-status`, une ligne
  `HORS FICHE <chemin>` par fichier changé absent de la ligne **Fichiers** — hors le
  fichier de fiches et `artefacts/` —, puis le diff entier.
- `--retirer` : `git worktree remove --force` sur chaque `vlp-relecture-*`, puis
  `prune` ; imprime `RETIRÉ <n>`.
- Pas de dépôt, commit inconnu, fiche absente : `GARDE: <raison>`, sort 1.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec trois tests écrits d'abord et vus en échec.
« relecture : l'instantané prend l'arbre sans bouger HEAD » — un fichier modifié et un
non suivi sont dans APRÈS, `HEAD` et `git status --porcelain` identiques avant et après ;
mutant : `add -A` sur l'index réel. « relecture : un fichier hors fiche » — `a.py`
nommé, `b.py` non, le fichier de fiches touché : une seule ligne, `HORS FICHE b.py` ;
mutant : le fichier de fiches plus exclu. « relecture : --retirer » — `git worktree list`
revient à une ligne ; mutant : un seul worktree retiré. Sur le vrai dépôt,
`relecture CAD1 --sha e41925c` imprime `FICHIER=` sur `context AI/49-cadrage-compte.md`
et la fiche `CAD1` ; `--retirer` rend `RETIRÉ 2`.
<!-- /FICHE -->

---

<!-- FICHE:REV2 -->
## REV2 [ ] — Contrôler la tête et refuser par script

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_cocher`, son analyseur d'options, docstring de
`cocher`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Deux options de `cocher`. Tests d'abord, vus en échec.

- `--verifier` garde sa ligne `CASE`, et lit en plus le dernier commit du dépôt du
  fichier de fiches : si son sujet nomme la fiche — `^<fiche>\s*:`, qui prend aussi le
  `VAL1:` que `COMMIT_FICHE` laisse passer —, il ajoute `TÊTE <sha> <sujet>` et sort 1.
  Hors d'un dépôt Git : une ligne `SANS GIT`, et la sortie ne dépend que de la case.
- `--refuser <motif>` remet `[ ]` sur le titre, et écrit juste sous lui le bloc de
  `tache-blocage.md` : `**Tentatives** (<date>) — non résolu.`, `1. FAITE refusée à la
  relecture.`, `Erreur : <motif>`. Un bloc déjà là ne se double pas : il gagne la ligne
  numérotée suivante, et son `Erreur :` prend le nouveau motif. `--date` fixe la date,
  comme pour `--resolu`. Imprime `REFUSÉ <fiche>` ; fiche introuvable : `GARDE:`, sort 1.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec trois tests écrits d'abord et vus en échec.
« cocher --verifier : un commit du sous-agent » — sujets `VAL1: x` et `VAL1 : x` : sort 1
et une ligne `TÊTE` ; `VAL10 : y` : sort 0 ; mutant : `COMMIT_FICHE` au lieu du motif,
et `VAL1:` passe. « cocher --verifier : sans Git » — `SANS GIT`, sort 0 sur `[x]` ;
mutant : la tête lue sans tester le dépôt. « cocher --refuser » — titre `[ ]`, les trois
lignes exactes ; un second refus donne `2.`, un seul `**Tentatives**`, un seul
`Erreur :` ; mutant : un second bloc ouvert.
<!-- /FICHE -->

---

<!-- FICHE:REV3 -->
## REV3 [ ] — Écrire le relecteur et le brancher

**Dépend de** : `REV1`, `REV2`.
**Fichiers** : `enchainement.md`, `agents/relecture.md` (nouveau),
`skills/relire/SKILL.md` (nouveau), `skills/enchainer/SKILL.md` (étape 3),
`methode-chantier.md` (lignes 178–179) — et rien d'autre.

**Prompt**
Le circuit du socle, en prose courte : chaque mot d'une commande se paye à chaque
exécution.

- `enchainement.md`, une section « Relecture » : `ACCEPTÉE — …` ou `REFUSÉE — …` en
  premier mot, le détail sur la même ligne ; aucun statut vaut `REFUSÉE`. Un défaut : ce
  que la fiche ne demande pas, un test qui ne tombe pas sur le mutant, un bug, une doc
  qui dit faux, une sortie qui change entre AVANT et APRÈS sans que la fiche l'explique,
  un `HORS FICHE` non justifié.
- `agents/relecture.md`, sur le modèle d'`agents/fiche.md` : `model: opus`, le `maxTurns`
  de `fiche.md`, outils `Read`, `Edit`, `Bash`, `PowerShell`. Premier appel :
  `relecture <fiche> [--sha S]` et `lire enchainement.md` ; puis le diff, les commandes
  rejouées, le mutant en dernier, `--retirer`, le verdict. `Edit` dans APRÈS seulement ;
  aucun `git`, aucun commit, même si un `CLAUDE.md` en demande un.
- `skills/relire/SKILL.md`, sur le modèle de `skills/jouer/SKILL.md` : forkée,
  `agent: vlp:relecture`, `args` : `<fiche> [<sha>]`.
- `skills/enchainer/SKILL.md`, étape 3, la puce `FAITE` : le circuit du socle, `SANS GIT`
  et `REFUSÉE` compris.
- `methode-chantier.md:178-179` : le chef commite après un `FAITE` accepté à la
  relecture — un renvoi à `enchainement.md`, pas une recopie.

**Critère de fin**
`py scripts/vlp.py lire agents/relecture.md skills/relire/SKILL.md` imprime les deux
fichiers et sort 0 ; `Grep` trouve `vlp:relire` et `--refuser` dans
`skills/enchainer/SKILL.md`, `ACCEPTÉE` et `REFUSÉE` dans `enchainement.md` ; le commit
de la fiche passe le hook `pre-commit`, qui valide les manifestes.
<!-- /FICHE -->

---

<!-- FICHE:REV4 -->
## REV4 [ ] — Prouver la relecture sur les commits de la nuit

**Dépend de** : `REV3`.
**Fichiers** : `context AI/08-etat.md` (une entrée au journal) — et rien d'autre.

**Prompt**
Avant la fiche, l'utilisateur fait `/reload-plugins` : une définition d'agent se charge
au démarrage (TODO n° 49, `CON`). `vlp:relecture` absent de ta liste d'agents : rends la
main.

Lance `Skill`, `skill: "vlp:relire"`, `args` : `CAD1 e41925c` — seul d'abord. Mesure son
coût en tours, tokens et $ par `scripts/mesure-tokens.py` sur la transcription du
sous-agent (sa docstring dit comment). Annonce le coût des cinq autres, extrapolé, et
attends l'accord avant de lancer `PLA1 eb2a6b0`, `VAL1 72035f2`, puis les corrigés
`CAD1 8bb748d`, `PLA1 7d16873`, `VAL1 c5123af`.

Après chaque relecture : `git worktree list` n'a qu'une ligne, `git status` n'a pas
bougé. Un défaut des témoins manqué : dis lequel ; ne change pas de modèle, c'est à
l'utilisateur d'en décider. Écris la table au journal de `08-etat.md`, datée.

**Critère de fin**
Une table de six lignes — commit · verdict · défauts nommés · défaut des témoins
retrouvé (oui/non) · tours · tokens · $ — où les trois fautifs sont `REFUSÉE` en nommant
le défaut de leur ligne des témoins (socle), et les trois corrigés `ACCEPTÉE`. Dessous,
le coût moyen d'une relecture, face à la reprise de la nuit : 16,51 $ pour 14 fiches
(TODO n° 48).
<!-- /FICHE -->
