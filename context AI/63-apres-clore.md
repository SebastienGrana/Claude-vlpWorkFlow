> **QUAND LIRE** : on joue une fiche `APC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache APC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier APC — Ce que le chiffre de clôture ne voit pas

**À quoi il sert.** `clore` inscrit un coût plus bas que celui que `cout` recompte ensuite :
+1 771 130 pour `ESD`, de +434 097 à +2 682 260 sur 19 clos (TODO n° 67). APC mesure d'où vient
l'écart, sur `ESD` puis sur les 19, et fait que le chiffre inscrit le rattrape.

**CLOS** le 2026-09-25. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** APC1..APC3 (2026-09-25) : le chiffre de clôture égale le recompté : la recompte d'un clos s'arrête à l'appel clore ; recompter --a-clore décompose l'écart des 19 clos.

**Session** : 017ee825-1356-4f4f-b03c-776d16c1a7a4

## Le socle commun

Mesuré au cadrage, 2026-09-25 : `py scripts/vlp.py cout "context AI/62-essais-sans-decoupe.md"`
rend `TOTAL … (18 506 516) · 206 tours`, dont `hors fiches … (5 466 984) · 36 tours` ; la
feuille de route inscrit 16 735 386 pour `ESD`. Commits (heure locale, `git log`) : `ESD3`
19:12:50, `Chantier ESD clos` 19:14:08, `Dette ESD` 19:22:48, menu 19:23:26.

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `plages` | `scripts/vlp.py:1634` | hors fiches = (origine → 1re fiche) + (dernière fiche → **1er commit suivant qui nomme le préfixe**, la clôture) ; **sans lui, jusqu'au bout** (`INFINI`, `:1664`) |
| `parts_aux_commits` | `scripts/vlp.py:1668` | mesure chaque plage dans chaque transcript (`mesure().mesurer(chemin, plage)`, secondes UTC) |
| `decouper` → `cout`, `recompte` | `:565`, `:520`, `:2307` | la recompte, **après** le commit de clôture |
| `couts` → `couts_aux_commits` | `:1772`, `:1759` | le même `parts_aux_commits`, appelé par `regenerer` (`:1860`) dans `cmd_clore` (`:2867`) — **avant** le commit de clôture |
| `total_chantier` | `scripts/vlp.py:2895` | le chiffre que `clore` inscrit |
| `cmd_recompter` | `scripts/vlp.py:2377` | une ligne `<X> inscrit … · recompté … · écart …` par clos |
| `transcript(chemin, tours, heures)` | `scripts/test-vlp.py:284` | un jsonl de test, 100 000 tokens par tour, heures en secondes UTC |

**Hypothèse de travail, non prouvée.** Les deux chiffres passent par le même `parts_aux_commits` ;
seule la fin de la dernière plage diffère : au `clore`, le bout du transcript à cet instant ;
ensuite, le commit de clôture. L'écart serait les tours entre l'appel `clore` et ce commit
(republications, `cloture.md` temps 3 et 4). Le menu et le push, eux, tombent après le commit :
la recompte ne les voit pas non plus. L'heure de l'appel `clore` : la ligne `timestamp` du
`tool_use` dont la commande contient `vlp.py` et ` clore`, dans une session du chantier.

**Ce qu'on ne fait pas.** `NIV` et `H` (écarts sans explication, TODO n° 67) restent dehors.
Les chiffres des clos déjà recomptés (`REC`, `ESD`) ne se réécrivent pas. Un test bâtit son
projet dans un dossier temporaire (`methode-chantier.md`, « Anatomie d'une fiche »).
Choix de l'utilisateur en `APC2` (2026-09-25) : **(b)**, la recompte s'arrête à l'appel `clore`,
et les republications sortent du coût, par une règle écrite. On ne fait pas (a), réécrire le
chiffre après le commit de clôture, ni (c), ne rien changer. Les 19 clos déjà réécrits gardent
leur chiffre (écart affiché −15 183 055 dans `recompter`) ; le reste de 10 952 704 n'est pas corrigé.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `APC1` | Décomposer l'écart d'`ESD` | rien |
| `APC2` | Décomposer l'écart des 19 clos, puis choisir le correctif | `APC1` |
| `APC3` | Appliquer le correctif choisi | `APC2` |

Rien n'est parallélisable : chaque fiche lit la mesure de la précédente.

---

<!-- FICHE:APC1 -->
## APC1 [x] — Décomposer l'écart d'`ESD`

**Session** : e7f318cf-d991-4985-b746-0fccf3648249
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
Donne à `vlp.py cout` une option `--a-clore` : elle cherche l'heure de l'appel `clore` dans les
sessions du fichier (voir le socle) et ajoute deux lignes après `TOTAL`, au format de `ligne_parts` :
`à clore` — le total si la dernière plage hors fiches s'arrêtait à cette heure — et `après clore` —
la différence, avec ses tours. Pas d'appel `clore` trouvé : une `GARDE:` qui le dit, pas de ligne.
Réutilise `parts_aux_commits` (une borne de fin optionnelle), n'en écris pas un second.
Test dans `test-vlp.py`, sur un projet bâti en dossier temporaire : deux fiches commitées, un
transcript dont un tour porte un `tool_use` `vlp.py clore`, des tours après lui et avant le commit
de clôture ; `à clore` et `après clore` attendus en nombres. Mutant : ignorer la borne (`à clore`
égal à `TOTAL`) doit faire tomber le test.
Puis lance-le sur `context AI/62-essais-sans-decoupe.md` et écris au journal du fichier d'état une
table `## <date> — APC1` : inscrit, `à clore`, recompté, `après clore` (tokens, tours), et le reste
non expliqué — chaque ligne nomme les quantités qu'elle compare.

**Critère de fin**
`py scripts/test-vlp.py` passe, mutant tombé (comptes bruts des deux passages) ; `cout --a-clore`
sur `ESD` affiche `à clore` et `après clore` ; la table dit si `à clore` égale l'inscrit 16 735 386,
et sinon de combien il s'en écarte.
<!-- /FICHE -->

---

<!-- FICHE:APC2 -->
## APC2 [x] — Décomposer l'écart des 19 clos, puis choisir le correctif

**Session** : 2bb1a1be-0e2d-4204-93ac-25d8239cd0e0
**Dépend de** : `APC1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `context AI/08-etat.md` (table `## 2026-09-25 — REC2`, causes 4a et 4b ; journal) — et rien d'autre.

**Prompt**
Donne à `vlp.py recompter` une option `--a-clore` qui ajoute à chaque ligne recomptée `à clore` et
`après clore` (le calcul d'`APC1`, pas un second), ou `sans appel clore` quand il manque. Test et
mutant comme en `APC1`.
Lance `py scripts/vlp.py recompter . --a-clore` et écris la table `## <date> — APC2` au journal,
sortie brute d'abord : pour les 19 clos des causes 4a et 4b de `REC2`, l'écart, la part `après
clore`, et le reste. Compte à part : combien d'écarts l'après-clore explique entièrement, en
partie, pas du tout ; combien de clos sans appel `clore` retrouvé.
Puis rends la main avec les correctifs possibles, chiffrés sur cette table, parmi lesquels :
(a) après le commit de clôture, `clore` ou `recompter` réécrit le chiffre de ce seul chantier —
stable, puisque la recompte s'arrête à ce commit ; (b) la recompte s'arrête à l'appel `clore` —
les deux chiffres coïncident, les republications sortent du coût, et c'est écrit.
ARRÊT: l'utilisateur choisit le correctif ; le choix va dans le socle, sous « Ce qu'on ne fait pas ».

**Critère de fin**
Tests passés, mutant tombé (comptes bruts) ; la table `APC2` couvre les 19 clos, ses trois comptes
sommés font 19 ; le choix de l'utilisateur est écrit dans le socle.
<!-- /FICHE -->

---

<!-- FICHE:APC3 -->
## APC3 [x] — Appliquer le correctif choisi

**Session** : 2bb1a1be-0e2d-4204-93ac-25d8239cd0e0
**Dépend de** : `APC2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `cloture.md` — et rien d'autre.

**Prompt**
Applique le correctif que le socle nomme depuis l'arrêt d'`APC2` — lui seul. Il change le chiffre
que `clore` inscrit (`total_chantier`), ou la fin de la plage de la recompte (`plages`), ou l'ordre
de `cloture.md` : la docstring de la fonction touchée dit la nouvelle règle dans le même geste.
Si `cloture.md` gagne un pas, il pointe vers le script, il ne décrit pas son calcul.
Test sur un projet bâti en dossier temporaire, avec des tours entre l'appel `clore` et le commit de
clôture : après le correctif, chiffre inscrit = chiffre recompté. Mutant : retirer le correctif
refait apparaître l'écart. Rejoue `cout --a-clore` sur `ESD` pour montrer l'avant et l'après.

**Critère de fin**
`py scripts/test-vlp.py` passe, mutant tombé (comptes bruts) ; le test montre inscrit = recompté
en nombres ; `pyright scripts/` sans erreur de plus qu'avant (compte brut avant/après).
<!-- /FICHE -->
