> **QUAND LIRE** : on joue une fiche `ESR*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ESR<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ESR — Un essai rechargé voit le code du worktree

**À quoi il sert.** `~/.claude/skills/vlp` suit le dossier principal (`main`), pas le worktree où
une fiche écrit : un `/reload-plugins` y recharge l'ancien code (vu à `REG3`). La carte dira le retard.

**Estimé.** 1 fiches · ≈3,02 $ — ≈3,02 $/fiche sur 82 clos (le 2026-09-29).

**Fait.** Rien. Ouvert le 2026-09-29, cadré en 1 fiche, `ESR1` à jouer.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `KIT` | `scripts/vlp.py:998` | le kit du `vlp.py` qui tourne — lancé par `${CLAUDE_PLUGIN_ROOT}`, le lien `~/.claude/skills/vlp` |
| `carte(depart, sortie, relecteur)` | `scripts/vlp.py:684` | écrit `PROJET=`, `CHANTIER.md`, les `ATTENTE=`, puis TODO ou fiches |
| `git_texte(args, cwd)` | `scripts/vlp.py:1111` | `(code, texte)` de `git`, jamais un traceback |
| injection de la carte | `skills/check/SKILL.md:17`, `skills/tache/SKILL.md` | `/vlp:check` et `/vlp:tache` lisent la carte avant leur 1er tour |

**Tranché au cadrage (2026-09-29, l'utilisateur)** :
- une clé **`PLUGIN_RETARD=`** dans la carte — pas une `GARDE:`, qui arrête `/vlp:tache`
  (`skills/tache/SKILL.md:45`) ; vue par `/vlp:tache` et `/vlp:check`, une ligne de consigne chacune ;
- le script **dit** le retard et la commande à coller, il **n'écrit rien** dans le dossier principal ;
- ne comptent que les commits qui touchent le code du plugin : `skills/`, `agents/`, `hooks/`,
  `scripts/`, `templates/`, `.claude-plugin/`, `methode-chantier.md`, `cloture.md`,
  `enchainement.md`, `ARTEFACTS.md` (lus par les commandes).

**Muette** (aucune ligne) : kit qui n'est pas un dépôt Git, projet d'un autre dépôt (Cairn…),
projet au même dossier que le kit, retard nul, `--relecteur`, git qui ne répond pas.

**Dehors** : avancer `main` ; les worktrees des autres projets ; `vlp.py niveau` (entrée `NUI` (b)).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ESR1` | Dire dans la carte le retard du plugin chargé | rien |

Une seule fiche.

---

<!-- FICHE:ESR1 -->
## ESR1 [x] — Dire dans la carte le retard du plugin chargé

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `skills/tache/SKILL.md`,
`skills/check/SKILL.md` — et rien d'autre.

**Prompt**
Écris `retard_plugin(racine, kit=KIT)` : `None` dans les cas muets du socle ; sinon
`(n, principal, branche)` — `n` = `git rev-list --count <HEAD du kit>..HEAD -- <chemins du socle>`
lancé dans `racine`, `principal` = `realpath(kit)`, `branche` = la branche de `racine` (`HEAD`
détaché : son sha court). Même dépôt = même `git rev-parse --git-common-dir` (chemins résolus).
`carte` l'appelle après les `ATTENTE=`, hors `--relecteur`, et écrit
`PLUGIN_RETARD=<n> commit(s) de code du plugin absents du plugin chargé — avant un /reload-plugins : git -C "<principal>" merge --ff-only <branche>`.
Docstring de `carte` : la clé. `skills/tache/SKILL.md` (liste des lignes de la carte) et
`skills/check/SKILL.md` (après la carte) : une ligne chacune — la dire, lancer sa commande
seulement sur le oui de l'utilisateur.

**Critère de fin**
1. Test dans `scripts/test-vlp.py`, sur un dépôt temporaire (`git init`, commit, `git worktree
   add`) : commit dans `scripts/` du worktree → `retard_plugin(wt, kit=principal)` rend `n == 1` et
   la branche ; commit de plus dans `context AI/` seul → toujours 1 ; kit = worktree → `None` ;
   autre dépôt → `None` ; `carte` sur le worktree avec ce kit → une ligne `PLUGIN_RETARD=1`.
2. Mutant : chemins du socle retirés du `rev-list` → le test tombe ; fichier rendu à l'octet.
3. `py scripts/vlp.py carte` dans ce worktree : la ligne, ou son absence, dite avec `git log
   --oneline main..HEAD -- scripts skills` en regard (comptes bruts).
4. `py scripts/test-vlp.py` : `OK` ; pyright 0 erreur sur les deux `.py`.
<!-- /FICHE -->
