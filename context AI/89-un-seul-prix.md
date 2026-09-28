> **QUAND LIRE** : on joue une fiche `TAU*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache TAU<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier TAU — Un seul prix pour un chantier

**À quoi il sert.** Le kit a deux prix pour un même chantier : `cout` pèse chaque tour à son vrai prix
(BTN : 47,08 $), `clore`, `ouvrir` et la feuille multiplient les tokens par une constante vieillie
(BTN : ≈79 $). TAU ne garde que le premier, partout, et recale ce qui est déjà écrit.

**Estimé.** 1 fiches · ≈4,42 $ — ≈4,42 $/fiche sur 76 clos (le 2026-09-28).

**Fait.** Rien. Ouvert le 2026-09-28, cadré en 4 fiches, `TAU1` à jouer.

**Session** : e0de453b-59d9-45d0-bf5b-1df1796056fb

## Le socle commun

**Décidé au cadrage (2026-09-28).**
- Un seul prix : le **pondéré** de `cout`, celui du « Coût du chantier » des pages. La louche
  (`USD_PAR_MTOKENS` = 0,8371, `estimation_usd`) disparaît du code et des docs.
- Anciens : le **joué** écrit à la louche est recalé sur le prix de sa page ; un vieil **estimé**
  ne se refait pas, il est marqué `(taux plat)`. Le total de la feuille passe au prix mesuré.
- Le prix vit **une fois par chantier clos**, en tête de sa cellule Tokens sur la feuille ; estimé
  et total le lisent là, sans rouvrir les pages.
- Dehors : Cairn et les autres projets (le code change pour eux, `prix` n'y est pas lancé) ;
  `mesure-tokens.py` ; le prix par fiche des pages, déjà juste.

**Le format** (💡 retenu au cadrage : en tête, car `BRUT` et `TOTAL_MESURE` exigent `)</td>`) :
- cellule : `47,08 $ · ≈95,0M (94 966 950)` — les préfixes existants (`recompté (REC)…`) suivent le `$` ;
- joué : `joué 7 fiches 47,08 $` (mesuré : pas de `≈`) ; prix inconnu : `joué 7 fiches ? $`, et pas de `$` en cellule ;
- vieil estimé : `≈25 $ (taux plat)`, là où il est écrit (ligne `**Estimé.**`, texte `estimé N fiches ≈X $`) ;
- un `$` se formate comme `ligne_cout` : `"%.2f"`, virgule — une seule fonction pour les deux.

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `total_mesure` | `scripts/vlp.py` `cmd_clore` | `(tokens, tours, usd, n)` rendu par `regenerer` ; `usd` est le pondéré |
| `ligne_cout` | `scripts/vlp.py` | `≈…M (…) · N tours · 47,08 $` — le `$` de la page |
| ligne de `ZONE:clos` | `cmd_clore`, bloc `<td class="mono">%s</td>` | la ligne que `clore` ajoute à la feuille |
| `BRUT`, `TOTAL_MESURE` | `scripts/vlp.py` | lisent le brut `(…)` avant `</td>` — à ne pas casser |
| `moyenne_clos` | `scripts/vlp.py` | `(tokens, fiches, clos)` des lignes mesurées — sert l'estimé d'`ouvrir` |
| `resume_clos`, pied de table | `scripts/vlp.py` | le total de la feuille, aujourd'hui à la louche |
| `cmd_recompter` | `scripts/vlp.py` | parcours ligne de `ZONE:clos` → fichier de fiches → page, à réutiliser |
| `ESTIME` | `scripts/vlp.py` | lit `**Estimé.** N fiches · ≈X $` — le `(taux plat)` après ne le gêne pas |

Tests : `scripts/test-vlp.py`, chacun dans son propre projet temporaire ; une aide de test vit dans
sa fonction `tester_<nom>()` (pyright tombe sinon, journal de BTN1). pyright : 0 erreur avant commit.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `TAU1` | Clore au prix mesuré, et le poser sur la feuille | rien |
| `TAU2` | Lire ce prix pour l'estimé et le total, retirer la louche | `TAU1` |
| `TAU3` | Un script `prix` pour les chantiers déjà clos | `TAU1` |
| `TAU4` | Passer le kit au prix mesuré, et republier | `TAU2`, `TAU3` |

`TAU2` et `TAU3` se jouent dans n'importe quel ordre après `TAU1`.

---

<!-- FICHE:TAU1 -->
## TAU1 [x] — Clore au prix mesuré, et le poser sur la feuille

**Session** : 3eba6c37-5458-4d5b-9c08-f6430394419a
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_clore`, le joué prend `total_mesure[2]` (le pondéré) au lieu de repasser les tokens par
`estimation_usd` ; format du socle. Sors de `ligne_cout` une petite fonction qui formate un `$`, et
sers-t'en pour les deux. La ligne que `clore` ajoute à `ZONE:clos` porte ce prix en tête de sa
cellule Tokens ; prix inconnu (`None`) : `? $` au joué, rien en cellule. Ne touche ni à `ouvrir`, ni
au total de la feuille (`TAU2`). Mets la docstring de `clore` à jour (le texte `joué <J> fiches ≈<Y> $`).

**Critère de fin**
Un test dans `test-vlp.py` clôt un chantier de bac dont le prix mesuré est connu, et vérifie : le
texte `joué N fiches X,XX $` (page, `.md`, `**Fait.**`) avec X,XX = l'usd de la découpe ; la cellule
qui commence par `X,XX $ · ` ; `couts_clos` et `moyenne_clos` qui lisent toujours son brut. Un
second cas, prix `None` : `? $`, cellule sans `$`. Mutant : remettre `estimation_usd` au joué → le
test tombe. `test-vlp.py` OK ; pyright 0 erreur (compte brut dans le compte rendu).
<!-- /FICHE -->

---

<!-- FICHE:TAU2 -->
## TAU2 [x] — Lire ce prix pour l'estimé et le total, retirer la louche

**Session** : 3eba6c37-5458-4d5b-9c08-f6430394419a
**Dépend de** : `TAU1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `ARTEFACTS.md` — et rien d'autre.

**Prompt**
Un motif lit le `$` en tête d'une cellule de `ZONE:clos`. `moyenne_clos` somme aussi ces `$`, sur
les seules lignes qui en portent ; l'estimé d'`ouvrir` devient cette moyenne $/fiche × N (même
ligne `**Estimé.**`). Le total de la feuille (`resume_clos` et le pied de table) somme les `$` des
lignes : toutes mesurées → `X $` ; une partie → `X $ sur K clos mesurés` ; aucune → pas de `$`.
Retire `USD_PAR_MTOKENS` et `estimation_usd` ; réécris le paragraphe d'`ARTEFACTS.md` qui les
nomme (« Ce coût est une **estimation** ») et les docstrings d'`ouvrir` et `feuille`.

**Critère de fin**
`grep -c "estimation_usd\|USD_PAR_MTOKENS" scripts/vlp.py ARTEFACTS.md` → 0 et 0. Un test : une
feuille de trois clos, deux avec `$` et un sans → total `… sur 2 clos mesurés`, estimé = somme des
deux `$` ÷ leurs fiches × N ; une feuille sans aucun `$` → ni `$` au total ni estimé en `$`
(`GARDE:` dite). Mutant : compter la ligne sans `$` comme 0 $ dans la moyenne → le test tombe.
`test-vlp.py` OK ; pyright 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:TAU3 -->
## TAU3 [x] — Un script `prix` pour les chantiers déjà clos

**Session** : 3eba6c37-5458-4d5b-9c08-f6430394419a
**Dépend de** : `TAU1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute `vlp.py prix <projet> [--a-blanc]`, sur le parcours de `cmd_recompter`. Pour chaque ligne de
`ZONE:clos` : lis le `$` du `cout-total` de sa page ; pose-le en tête de la cellule s'il n'y est
pas ; dans le fichier de fiches, le `.md` d'abri et la page, remplace `joué N fiches ≈X $` par le
prix mesuré et marque le vieil estimé `(taux plat)` (format du socle). Une page sans `$` : rien
d'écrit, compté. Rejoué, il n'écrit plus rien. Sortie : `PRIX <n> posés · <n> déjà · <n> sans prix ·
<n> joués recalés · <n> estimés marqués`, et une ligne par fichier écrit. Documente-le dans la
docstring du script.

**Critère de fin**
Un test bâtit un projet de deux clos (l'un avec `$` en page, l'autre sans) : premier passage →
`1 posés · 0 déjà · 1 sans prix · 1 joués recalés · 1 estimés marqués` ; second → `0 posés · 1 déjà`,
fichiers identiques à l'octet ; `--a-blanc` n'écrit rien. Mutant : marquer `(taux plat)` sans
regarder s'il y est déjà → le second passage le double, le test tombe. `test-vlp.py` OK ; pyright 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:TAU4 -->
## TAU4 [ ] — Passer le kit au prix mesuré, et republier

**Dépend de** : `TAU2`, `TAU3`.
**Fichiers** : `context AI/artefacts/*` et les fichiers de fiches que `prix` nomme ;
`context AI/89-un-seul-prix.md` (sa ligne `**Estimé.**`, écrite à la louche à l'ouverture).

**Prompt**
Lance `prix . --a-blanc`, puis `prix .` ; recopie les comptes bruts. Marque à la main l'estimé de
TAU lui-même `(taux plat)`. Régénère la feuille (`feuille .`). Compare la feuille à sa version en
ligne (`vlp.py comparer`) avant de la republier, avec `files` de la ligne `FILES` ; republie chaque
page que `prix` a écrite (lire la version en ligne d'abord, 200 publications par jour au plus).

**Critère de fin**
`prix .` rejoué → `0 posés` ; `grep -l "joué [0-9]* fiches ≈" "context AI"` → 0 fichier ;
`feuille . --verifier` → `identique` ; le total de la feuille égal à la somme des `$` de ses lignes
(calcul donné) ; nombre de pages republiées = nombre de pages écrites par `prix`.
<!-- /FICHE -->
