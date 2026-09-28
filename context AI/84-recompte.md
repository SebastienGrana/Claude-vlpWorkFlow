> **QUAND LIRE** : on joue une fiche `ECA*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ECA<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ECA — Comprendre les écarts du recompte avant de l'écrire

**À quoi il sert.** `recompter .` à blanc montre 24 clos à écart (19 négatifs, 5 positifs). ECA
en établit chaque cause, répare les deux défauts de mesure trouvés, puis écrit le recompte sur la
feuille de route.

**Estimé.** 1,5 fiches · ≈6,34 $ — ≈4,22 $/fiche sur 71 clos (le 2026-09-27).

**CLOS** le 2026-09-27. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** ECA1..ECA3 (2026-09-27) : Les 24 écarts du recompte expliqués au jeton près ; un appel clore n'est plus un texte cité (lance_clore), la fiche sans commit d'un clos s'arrête au commit suivant ; recompte écrit : 19 cellules, 1 140 424 192 → 1 125 033 889 — estimé 1,5 fiches ≈6,34 $ (taux plat) · cadré 3 · joué 3 fiches 5,74 $.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Mesuré au cadrage (2026-09-27, scripts du brouillon `mesure_eca2.py`, `mesure_eca3.py`,
`mesure_eca4.py`, `simule_lec.py`) — chaque écart recompté trois fois face au chiffre inscrit :

| Clos | Recompté jusqu'au commit | À l'appel `clore` actuel | À un `clore` qui ne prend plus un texte |
|---|---|---|---|
| 19 négatifs (JUG … CPT) | écart **0** sur 19 | −434 097 à −2 682 260 | inchangé |
| BAC, EST, FFE, REL | +727 063 à +1 243 660 | +113 988 à +487 650 | écart **0** sur 4 |
| LEC | +9 660 526 | aucun appel trouvé | aucun appel trouvé |

- **Négatifs** : le chiffre inscrit court jusqu'au commit de clôture (règle `REC`), le recompte
  s'arrête à l'appel `clore` (règle `APC`). Rien à réparer : c'est ce que `--ecrire` corrige.
- **BAC, EST, FFE, REL** : `APPEL_CLORE` prend pour un appel le **texte** « Coût du chantier : N
  (`vlp.py clore`) » qu'un `echo` ou un heredoc écrit dans `08-etat.md`. Sur tout
  `~/.claude/projects` : 101 commandes attrapées, 82 vrais appels, 19 textes (commit `-m`,
  `--note`, `--resultat`, heredoc, code de test).
- **LEC** : LEC5 n'a pas de commit `LEC5 :` (son travail est dans « Journal : … pour LEC5 »,
  `c331deb`) ; `plages` la fait courir « jusqu'au bout du transcript » — la session a continué
  après la clôture. L'arrêter au commit suivant qui nomme `LEC` rend 41 160 098 = l'inscrit.

| Symbole | `scripts/vlp.py` | Rôle |
|---|---|---|
| `APPEL_CLORE` | `:849` | le motif d'un appel `clore` |
| `heure_clore(chemin, lignes)` | `:852` | l'heure du dernier appel dans la dernière plage hors fiches |
| `decouper` | `:894` | passe `fin` = `heure_clore` pour un clos |
| `HEREDOC`, `ecrit_git` | `:1505`, `:1509` | le corps d'un heredoc reçu par `cat`/`tee` tu (chantier `ECH`) |
| `plages(fiches_, heures, gardes)` | `:2014` | les plages des fiches et hors fiches |
| `parts_aux_commits(…, fin)` | `:2048` | la découpe ; `fin` coupe la dernière plage hors fiches |
| `cmd_recompter` | `:3150` | `--ecrire` n'écrit que la table `ZONE:clos` de la feuille |

Hors champ : un clos **sans** appel `clore` reste recompté jusqu'au commit — décidé par `APC`, testé
(`scripts/test-vlp.py`, « recompter --a-clore : sans appel clore, la ligne le dit »).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ECA1` | Un appel `clore` est une commande lancée, pas un texte cité | rien |
| `ECA2` | La fiche sans commit d'un clos s'arrête au commit suivant | rien |
| `ECA3` | Écrire le recompte sur la feuille de route | `ECA1`, `ECA2` |

---

<!-- FICHE:ECA1 -->
## ECA1 [x] — Un appel `clore` est une commande lancée, pas un texte cité

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Sors de `ecrit_git` une fonction `sans_heredoc(commande)` (la commande, corps des heredocs reçus
par `cat`/`tee` tus) ; `ecrit_git` l'appelle. Ajoute `lance_clore(commande)` : vrai si, après
`sans_heredoc`, un segment (début, `;`, `&`, `|`, `(`, fin de ligne) s'ouvre — affectations
`X=y` et `$x =` permises — par un interprète Python (`py`, `python`, `python3`, chemin et `.exe`
permis), options, puis un chemin qui finit par `vlp.py`, puis `clore`. `heure_clore` s'en sert à
la place de `APPEL_CLORE.search`. Mets à jour les docstrings.

**Critère de fin**
`tester_lance_clore` : vrais — `py scripts/vlp.py clore .`, `cd "C:/k" && py "C:/k/scripts/vlp.py"
clore .`, `export A=b; py …`, un heredoc puis l'appel, `$o = py "$kit/scripts/vlp.py" clore`,
`python3 -X utf8 scripts/vlp.py clore .` ; faux — l'`echo` et le heredoc de la ligne de bilan,
un `git commit -m` qui cite, un `page --resultat` qui cite, un `cat > t.ps1 <<'EOF'` qui écrit
l'appel. Mutant : l'ancien motif → ÉCART. `recompter .` : BAC, EST, FFE, REL à écart 0.
`test-vlp.py` finit par `OK` ; pyright 0.
<!-- /FICHE -->

---

<!-- FICHE:ECA2 -->
## ECA2 [x] — La fiche sans commit d'un clos s'arrête au commit suivant

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
`plages` prend `clos=False` : pour un clos, la dernière fiche sans commit va jusqu'au premier
commit suivant qui nomme le préfixe, comme la dernière plage hors fiches, au lieu du bout du
transcript. `heure_clore` passe `clos=True` ; `parts_aux_commits` passe `clos=fin is not None` —
`fin` n'est donné que pour un clos. Mets à jour les docstrings de `plages` et `parts_aux_commits`.

**Critère de fin**
`tester_clos_sans_commit` : un clos Q, commits `Chantier Q ouvert` (100), `Q1 : Créer` (300),
`Journal : la mesure de Q2` (600), `Chantier Q clos` (900) ; tours à 200, 400, 500, l'appel
`clore` à 700, puis 800, 1000, 1100. `cout q.md` : Q2 2 tours, TOTAL 400 000 · 4 tours. Mutant :
`clos` ignoré → TOTAL 700 000 · 7 tours. `recompter .` : LEC à écart 0. `test-vlp.py` finit par
`OK` ; pyright 0.
<!-- /FICHE -->

---

<!-- FICHE:ECA3 -->
## ECA3 [x] — Écrire le recompte sur la feuille de route

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `ECA1`, `ECA2`.
**Fichiers** : `context AI/artefacts/feuille-de-route.html` — et rien d'autre.

**Prompt**
Lance `py scripts/vlp.py recompter .` : plus aucun écart positif, les 19 négatifs aux valeurs du
socle. Puis `py scripts/vlp.py recompter . --ecrire`, et relis le `git diff` de la feuille.

**Critère de fin**
`ÉCRIT <n> cellules · total <avant> → <après>`, `<n>` = 19, `<après>` = `<avant>` − la somme des
19 écarts ; relancé, `ÉCRIT 0 cellules`. Le diff ne touche que ces 19 cellules, le pied et le
résumé. `vlp.py vigile` sur la feuille : OK.
<!-- /FICHE -->
