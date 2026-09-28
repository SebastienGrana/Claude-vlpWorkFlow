> **QUAND LIRE** : on joue une fiche `OUV*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache OUV<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier OUV — Une ligne qui s'ouvre par un mot de jauge, sans être une jauge

**À quoi il sert.** Le gardien renvoie un sous-agent dont une ligne s'ouvre par « Imprévu »,
« Pas bon »… même quand c'est une puce (`- Imprévu : j'ai dû…`). OUV exige la forme d'une
jauge : un émoji devant, ou le mot suivi de `—`, `…` ou de la fin de ligne.

**Estimé.** 0,5 fiches · ≈2,12 $ — ≈4,23 $/fiche sur 70 clos (le 2026-09-27).

**CLOS** le 2026-09-27. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** OUV1..OUV1 (2026-09-27) : La règle tete exige la forme d'une jauge : émoji de jauge en tête, ou le mot suivi de —, … ou fin de ligne ; une puce « - Imprévu : » ne fait plus renvoyer — estimé 0,5 fiches ≈2,12 $ (taux plat) · cadré 1 · joué 1 fiches 1,17 $.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Mesuré au cadrage (2026-09-27, `~/.claude/projects`, script du brouillon `mesure_ouv.py`) :
lignes que la règle `tete` prend pour une jauge, dans le dernier message des sous-agents —
émoji + `—`/`…`/fin 72, émoji + autre suite 5, sans émoji + `—`/`…`/fin 2, sans émoji + autre
suite **0** ; chez le chef, sur tous ses messages — 762, 41, 0, 4.

Tranché la nuit du 2026-09-27, l'utilisateur dormant (🟡 de la TODO n° 66) : **l'émoji OU la
suite** — la règle attrape 79 lignes sur 79 chez les sous-agents ; exiger l'émoji seul en
perdrait 2, exiger la suite seule en perdrait 5.

| Symbole | `scripts/vlp.py` | Rôle |
|---|---|---|
| `JAUGE` | `:1596` | les cinq libellés |
| `ouvre(ligne)` | `:1603` | la ligne sans ses marques de tête (émojis compris) |
| `forme_texte(texte, regle)` | `:1611` | `(resume, jauge)` ; la règle `tete` (`:1619`) est celle du gardien et de `forme` |

On ne touche pas aux règles `tout`, `tiret`, `deux` : elles rejouent d'anciennes mesures.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `OUV1` | Exiger la forme d'une jauge dans la règle `tete` | rien |

Une seule fiche.

---

<!-- FICHE:OUV1 -->
## OUV1 [x] — Exiger la forme d'une jauge dans la règle `tete`

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `forme_texte`, règle `tete`, une ligne ne compte pour une jauge que si un émoji de jauge
(✅ 🟢 ⚠ ❌ 🔥) est dans ses marques de tête, ou si le mot est suivi — `**` et `.` permis —
de `—`, `–`, `…` ou de la fin de ligne. « En résumé » ne change pas. Mets à jour la docstring
de `forme` et celle de `forme_texte`.

**Critère de fin**
Tests sur le gardien (`vlp:relecture`, `SubagentStop`) : `REFUSÉE\n- Imprévu : j'ai dû
relancer` → muet ; `ACCEPTÉE\n⚠️ **Imprévu** : x` → renvoyé ; `ACCEPTÉE\nÇa tient, mais…` →
renvoyé ; `ACCEPTÉE\nPas bon — y` → renvoyé. Rejeu de `mesure_ouv.py` : 79 lignes toujours
jauges chez les sous-agents. Mutant : la forme ignorée → le premier test tombe. `test-vlp.py`
finit par `OK` ; pyright 0.
<!-- /FICHE -->
