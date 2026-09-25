> **QUAND LIRE** : on joue une fiche `RLG*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache RLG<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier RLG — Le gardien derrière le relecteur

**À quoi il sert.** `vlp.py gardien` refuse `git commit/add/reset` au seul `vlp:fiche`. Le
relecteur `vlp:relecture` lance des commandes sans que rien ne l'empêche d'écrire dans Git.
RLG étend le refus de `PreToolUse` au relecteur (TODO n° 60).

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 1 fiche, `RLG1` à jouer. Cadré seul :
l'utilisateur dormait ; les 🟡 tranchés ici sont à valider au réveil.

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675

## Le socle commun

| Fait vérifié | Où |
|---|---|
| `cmd_gardien(entree, sortie)` sort muet si `"fiche"` n'est pas dans `agent_type` — **pour les deux événements** | `scripts/vlp.py`, `def cmd_gardien` |
| `ECRIT_GIT` ne vise que `commit`, `add`, `reset` (avec `-C` éventuels) : `git diff`, `git log`, `git worktree` passent | `scripts/vlp.py`, `ECRIT_GIT =` |
| les worktrees de relecture sont posés et retirés par `vlp.py relecture` lui-même (`git_texte`, sous-processus), jamais par une commande de l'agent | `scripts/vlp.py`, `def retirer_relectures` |
| le relecteur finit par `ACCEPTÉE` ou `REFUSÉE` (`VERDICTS`), pas par un mot de `STATUTS` : `verdict_fin` le renverrait à tort | `scripts/vlp.py`, `VERDICTS`, `def verdict_fin` |
| tests du gardien : bloc « gardien (chantier CON4) », fonction `gardien(d)` ; un test y dit « sous-agent vlp:relecture laissé passer » | `scripts/test-vlp.py` |
| tests : `py scripts/test-vlp.py` ; pyright sur les fichiers touchés ; une fiche de code nomme son mutant | `methode-chantier.md` |

Décidé au cadrage, seul : le 🟡 de la TODO (« sauf les `git worktree` que `vlp.py relecture`
pose ») tombe — l'agent ne tape jamais `git worktree`, et `ECRIT_GIT` ne le vise pas.

**Dehors.** `SubagentStop` du relecteur (juger son verdict en tête) : autre chantier.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `RLG1` | Refuser l'écriture Git au relecteur | rien |

---

<!-- FICHE:RLG1 -->
## RLG1 [x] — Refuser l'écriture Git au relecteur

**Tentatives** (2026-09-25) — résolu par le chef : garde `dict` sur l'entrée et sur `tool_input`, `agent_type` chaîne ou muet ; deux tests ajoutés.
1. FAITE refusée à la relecture.
2. FAITE refusée à la relecture.
Erreur : REFUSÉE — régression prouvée : gardien plante pour un vlp:relecture dont le tool_input n'est pas un objet

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_gardien`, le filtre d'entrée laisse passer un `agent_type` qui contient « fiche »
**ou** « relecture ». `SubagentStop` reste réservé à « fiche » : un relecteur qui s'arrête
sort muet. Sur `PreToolUse`, la raison du refus nomme le bon agent et son fichier :
`vlp:fiche` → `agents/fiche.md`, `vlp:relecture` → `agents/relecture.md`. Mets à jour la
ligne `gardien` de la docstring du module. Dans `test-vlp.py`, le test « sous-agent
vlp:relecture laissé passer » devient « refusé » ; ajoute : un relecteur qui lance
`git diff` passe ; un `SubagentStop` de relecteur dont `last_assistant_message` commence
par `ACCEPTÉE` sort muet.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`. Mutant : filtre remis à « fiche » seul — le test
« relecteur refusé » tombe. pyright : 0 erreur sur les deux fichiers.
<!-- /FICHE -->
