> **QUAND LIRE** : on joue une fiche `PIP*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache PIP<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier PIP — Une barre verticale dans une cellule de la TODO se signale

**À quoi il sert.** Une barre verticale non échappée dans une cellule de la TODO coupe la ligne
en trop de cellules ; `todo_du_fichier` jette les cellules en trop sans rien dire, et la feuille
affiche un décompte faux (≈267 fiches au lieu de ≈13, clôture d'`ARC`). Après PIP, une telle
ligne arrête `feuille` par une `GARDE:` qui la nomme, et `niveau` la compte comme un écart.

**Estimé.** 1 fiches · ≈2,98 $ — ≈2,98 $/fiche sur 87 clos (le 2026-09-29).

**CLOS** le 2026-09-29. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** PIP1..PIP1 (2026-09-29) : Une ligne de TODO qui n'a pas 5 cellules rend une GARDE dans feuille et un ÉCART dans niveau, au lieu d'un décompte faux — estimé 1 fiches ≈2,98 $ · cadré 1 · joué 1 fiches 2,41 $.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

**Mesuré au cadrage (2026-09-29)** :
- `todo_du_fichier` (`scripts/vlp.py:3223`) découpe par `re.split(r"(?<!\\)\|", …)` : la barre
  **échappée** est déjà ignorée ; une barre **non échappée** coupe la ligne, et
  `rangs.append(cellules[:5])` jette le reste ; une ligne à 4 cellules est jetée entière (`>= 5`).
  Essai : `| 2 | Y | a \`x | y\` | 3 fiches | — |` → `['2', 'Y', 'a \`x', 'y\`', '3 fiches']`.
- Le ≈267 venait de `borne_haute_cout` : il lisait « 256 » (de `sha256sum`) dans la cellule
  « Coût » décalée.
- Le rendu est **déjà juste** : `cellule_md` (`scripts/vlp.py:3218`) remplace `\|` par `|` avant
  d'afficher — ``a `sed x \| sha256sum` b`` → `sed x | sha256sum`. Seul manque un test.
- La note de la ligne 89 de la TODO (« la barre échappée a reproduit le défaut (≈281) ») est
  **fausse** : la première version de cette ligne avait aussi une barre non échappée.
- `niveau` appelle `feuille()` (`scripts/vlp.py:4718`) et rend une `ValueError` en
  `ÉCART: feuille:` (`:4725`) ; `cmd_feuille` la rend en `GARDE:` (`:3647`), `clore` aussi
  (`:5052`, « feuille non écrite »).

**Tranché au cadrage (l'utilisateur)** :
- une ligne de TODO qui n'a pas **exactement 5 cellules** : `GARDE:`, la feuille n'est pas
  écrite — pas un simple avertissement ;
- la barre échappée reste lue comme un caractère (déjà le cas) ; un test le verrouille ;
- une fiche ; le fichier prend le numéro **100** — la règle devient « deux chiffres ou plus »
  (`methode-chantier.md`, `skills/chantier/SKILL.md`), aucun script ne suppose deux chiffres
  (grep sur `scripts/` et `hooks/` : 0 motif).

**Invariant** : une TODO saine (5 cellules par ligne) donne exactement la même feuille qu'avant.

**Dehors** : les autres tables Markdown lues par `vlp.py` (index, clos) ; réécrire une ligne
cassée à la place de l'utilisateur.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `PIP1` | Une ligne de TODO mal découpée rend une GARDE | rien |

---

<!-- FICHE:PIP1 -->
## PIP1 [x] — Une ligne de TODO mal découpée rend une GARDE

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `todo_du_fichier`, une ligne de la table dont le découpage ne donne pas exactement 5
cellules lève une `ValueError` qui dit : le numéro de la ligne (première cellule), le nombre de
cellules trouvé, et « une barre verticale dans une cellule s'écrit `\|` ». Plus de
`cellules[:5]` ni de ligne jetée en silence. Docstring de `todo_du_fichier` à jour. Test dans
`scripts/test-vlp.py` : une TODO saine → même rang qu'avant ; une barre non échappée (6
cellules) → `feuille` rend `GARDE:` avec le numéro, sort 1, la page n'a pas bougé ; une ligne à
4 cellules → `GARDE:` aussi ; `niveau` sur le même projet → une ligne `ÉCART: feuille:` ; une
barre échappée dans du code → 5 cellules, et `cellule_md` la rend sans barre oblique inverse.

**Critère de fin**
1. `py scripts/vlp.py feuille .` sur le kit : pas de `GARDE:` (la TODO réelle est saine).
2. Mutant par `vlp.py mutant` : la garde ramenée à `>= 5` → un test tombe.
3. `py scripts/test-vlp.py` : `OK` ; pyright 0 erreur sur `scripts/vlp.py`.
4. `vlp.py niveau` en lecture seule sur les quatre projets équipés : aucun écart **nouveau** dû à
   la garde (comptes seulement pour Cairn).
<!-- /FICHE -->
