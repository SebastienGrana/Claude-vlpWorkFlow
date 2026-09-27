> **QUAND LIRE** : on joue une fiche `ECH*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ECH<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ECH — `ECRIT_GIT` ne lit pas le texte d'un heredoc

**À quoi il sert.** Le gardien refuse à un sous-agent un `cat > f <<'EOF'` qui ne fait qu'écrire
les mots `git commit` dans un fichier. ECH fait du corps d'un tel heredoc une donnée, sans
laisser passer un heredoc qui s'exécute.

**Estimé.** 0,5 fiches · ≈2,12 $ — ≈4,24 $/fiche sur 69 clos (le 2026-09-27).

**Fait.** Rien. Ouvert le 2026-09-27, cadré en 1 fiche, `ECH1` à jouer.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Mesuré au cadrage (2026-09-27, 889 transcriptions de `~/.claude/projects`, script du brouillon
`mesure_ech.py`) : `ECRIT_GIT` attrape 1 174 commandes (chef 1 155, sous-agents 19). Le motif
n'est que dans un heredoc pour 18 (chef 13, sous-agents 5), que dans une chaîne citée pour 7
(chef 6, sous-agents 1). Qui reçoit ces heredocs : `cat` 14, `py` 6 (dont 4 derrière une
variable d'environnement). Une chaîne citée porte un vrai `git reset` (`ssh '…'`).

Tranché la nuit du 2026-09-27, l'utilisateur dormant (🟡 de la TODO n° 63) : **seul le corps
d'un heredoc reçu par `cat` ou `tee` est une donnée**. Un heredoc reçu par `py`, `bash`, `sh`…
s'exécute : il reste lu. Les chaînes citées restent lues : `ssh '…'`, `bash -c "…"` exécutent.

| Symbole | `scripts/vlp.py` | Rôle |
|---|---|---|
| `ECRIT_GIT` | `:1501` | le motif `git [-C …] commit\|add\|reset` |
| `lire_contrat` | `:1504` | compte les appels qui écrivent dans Git d'une transcription (`:1526`) |
| gardien `PreToolUse` | `:1769` | refuse l'appel d'un sous-agent `vlp:fiche` ou `vlp:relecture` |

On ne fait pas : le `echo '…' > f` d'un sous-agent (1 cas mesuré) reste refusé — `echo … | sh`
exécute, et un renvoi borne le coût.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ECH1` | Taire le corps d'un heredoc écrit par `cat` ou `tee` | rien |

Une seule fiche.

---

<!-- FICHE:ECH1 -->
## ECH1 [ ] — Taire le corps d'un heredoc écrit par `cat` ou `tee`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris `ecrit_git(commande)` près d'`ECRIT_GIT` : elle retire le corps de chaque heredoc
(`<<EOF`, `<<-EOF`, `<<'EOF'`, `<<"EOF"`) dont la commande qui le reçoit est `cat` ou `tee`,
puis cherche `ECRIT_GIT`. Les deux usages (`lire_contrat` et le gardien) l'appellent. Un
heredoc reçu par autre chose, ou dont la fin manque, reste lu tel quel.

**Critère de fin**
Tests : `cat > f <<'EOF'\ngit commit\nEOF` → le gardien ne refuse pas (sortie vide) ; `tee f
<<EOF\ngit add x\nEOF` → pas d'écriture ; `py - <<'EOF'\n…git commit…\nEOF` → refus ;
`cat > f <<'EOF'\nx\nEOF\ngit commit -m y` → refus ; `ssh h 'git reset --hard'` → refus. Mutant :
`ecrit_git` ne retire rien → le premier test tombe. `test-vlp.py` finit par `OK` ; pyright 0.
<!-- /FICHE -->
