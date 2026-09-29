> **QUAND LIRE** : on joue une fiche `VRB*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache VRB<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier VRB — Le gardien ne voit que trois verbes Git

**À quoi il sert.** `ECRIT_GIT` ne vise que `commit`, `add`, `reset` : `git checkout <fichier>`
et `git stash` échappent au gardien et à `contrat`. Le chantier passe à une liste blanche des lectures.

**Estimé.** 1 fiches · ≈3,02 $ — ≈3,02 $/fiche sur 81 clos (le 2026-09-29).

**Fait.** Rien. Ouvert le 2026-09-29, cadré en 1 fiche, `VRB1` à jouer.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `ECRIT_GIT` | `scripts/vlp.py:1581` | le motif, aujourd'hui `commit\|add\|reset` après `git [-C x]…` |
| `ecrit_git(commande)` | `scripts/vlp.py:1629` | `ECRIT_GIT` sur `sans_echo(sans_heredoc(commande))` |
| `contrat` | `scripts/vlp.py:1685` | compte les appels `ecrit_git` d'un sous-agent |
| gardien `PreToolUse` | `scripts/vlp.py:1969` | refuse l'appel (`permissionDecision: deny`) pour `vlp:fiche` et `vlp:relecture` |
| tests existants | `scripts/test-vlp.py:3522-3529` | heredoc, `echo`/`printf`, `echo … \| sh`, `ssh h 'git reset --hard'` |

**Tranché au cadrage (2026-09-29, l'utilisateur)** :
- **Liste blanche** : un appel Git passe s'il lit — `diff`, `status`, `log`, `show`, `rev-parse`,
  `ls-files`, `blame`, `grep` ; **tout autre verbe est une écriture**, inconnu compris.
- **Tout `checkout` et `switch` bloqués**, branche comme fichier : un sous-agent ne change pas de branche.
- La liste vit **dans `vlp.py` seul** ; `ecrit_git` garde son nom (appelé à deux endroits).

**Mesuré au cadrage** — 202 transcriptions, 145 sous-agents `vlp:*`, comptes bruts du texte des
commandes (heredoc compris) : `commit` 38, `diff` 22, `add` 15, `status` 8, `log` 6, `checkout` 2,
`rev-parse` 2, `show` 2, `stash` 2, `worktree` 2 (texte de test), `reset` 1. Toute lecture
observée est dans la liste blanche.

**Invariant nouveau** : `git` doit être **en position de commande** — début, après `;` `&&` `||`
`|` `(` `$(` `` ` `` `&` (PowerShell), une quote ouvrante (cas `ssh h 'git …'`), ou un chemin
(`…/git.exe`). Sinon `grep -c git f` serait lu comme le verbe `f`, et bloqué.

**Dehors** : la session principale (mode `main` d'`enchainer`, défaut depuis REG) — le gardien ne
voit que les sous-agents ; les alias Git (`git -c alias.x=…`) ; le texte des `agents/*.md`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `VRB1` | Passer `ECRIT_GIT` en liste blanche | rien |

Une seule fiche.

---

<!-- FICHE:VRB1 -->
## VRB1 [x] — Passer `ECRIT_GIT` en liste blanche

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Réécris `ECRIT_GIT` (ou remplace-le par une fonction appelée depuis `ecrit_git`) : repère
chaque `git` en position de commande (socle), saute ses options globales (`-C x`, `-c k=v`,
`--no-pager`, `-P`, `--git-dir=…`, `--work-tree=…`), lis le verbe ; l'appel écrit si ce verbe
n'est pas dans la liste blanche du socle, ou s'il n'y a pas de verbe lisible. Garde
`sans_heredoc` et `sans_echo` en amont. Mets à jour le commentaire et la docstring.
Le message du gardien dit déjà « n'écrit pas dans Git » : ne le change pas.

Dans `scripts/test-vlp.py`, à côté des cas existants (qui restent verts), ajoute :
- `True` : `git checkout f.py`, `git checkout main`, `git switch x`, `git stash`,
  `git -C x stash`, `git restore f`, `git clean -fd`, `git push`, `git rebase main`, `git merge x`,
  `cd x && git stash`, `& git.exe push` ;
- `False` : `git diff --cached`, `git status`, `git --no-pager log -1`, `git show HEAD:f`,
  `git rev-parse --show-toplevel`, `git ls-files`, `git -C x log`, `grep -c git f`,
  `ls .git`, `echo git`.

**Critère de fin**
1. `py scripts/test-vlp.py` : 0 échec, compte brut des tests affiché.
2. Deux mutants, chacun fait tomber au moins un test, fichier rendu à l'octet près : (a) `stash`
   ajouté à la liste blanche ; (b) l'ancrage « position de commande » retiré.
3. Rejeu sur les transcriptions `~/.claude/projects/*/*/subagents/*.jsonl` d'agent `vlp:*` : liste
   de chaque appel Bash/PowerShell où l'ancien motif et le nouveau diffèrent, avec son verbe —
   comptes bruts ; aucune lecture (verbe de la liste blanche) ne doit y figurer comme écriture.
<!-- /FICHE -->
