> **QUAND LIRE** : on joue une fiche `TAB*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache TAB<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier TAB — Les tables de `vlp.py` ne se coupent plus en silence

**Ouvert.** le 2026-10-08.

**À quoi il sert.** `PIP` n'a gardé que la TODO : les autres tables Markdown lues par `vlp.py` peuvent tronquer
une ligne mal découpée sans rien dire ; `clore` écrit avant de lire la TODO ; et une ligne de TODO se retire à la main.

**Estimé.** 7 fiches · ≈28 $ — ≈3,95 $/fiche sur 91 clos (le 2026-10-08).

**Fait.** Rien. Ouvert le 2026-10-08 (nuit, canal A), cadré en 4 fiches par le plan du soir (`context AI/106-nuits.md`, « TAB »), `TAB1` à jouer.

**Session** : d0a38db6-ada6-4167-acf3-bc2c5e81333f

## Le socle commun

Le code vit dans `scripts/vlp_coeur.py` ; `scripts/vlp.py` le lance et porte la liste des sous-commandes dans sa
docstring. Les tests sont dans `scripts/test-vlp.py`. Un symbole se cite par son nom ; sa ligne du jour :
`vlp.py symboles scripts/vlp_coeur.py <nom>`.

| Symbole (`vlp_coeur.py`) | Ce qu'il fait |
|---|---|
| `todo_du_fichier(lignes)` | rangs de la table `\| # \| Chantier \|` ; une ligne qui n'a pas 5 cellules lève une `ValueError` qui la nomme (`PIP`) — **la garde de référence** |
| `SEPARATEUR` | regex de la ligne `\|---\|` sous un en-tête |
| `cellule_md(texte)` | rend une cellule en HTML, `\|` redevient `\|` |
| `cmd_clore(a, sortie)` | la clôture ; écrit fiches, index, `CHANTIER.md`, puis la feuille — qui peut buter : `GARDE: … — CHANTIER.md et fiches écrits, feuille non écrite` |
| `lignes_de(chemin)`, `lignes_du_projet(projet, rel, libelle)`, `ecrire_lignes(chemin, lignes)` | lire, et écrire un fichier entier |

Invariants, valables pour toutes les fiches :

- Une coupe découverte se dit : `GARDE: <ce qui cloche>` sur la sortie, **sort 1**, et **rien d'écrit** — tout se
  calcule avant la première écriture. Un fichier s'écrit par `.tmp` puis `os.replace`.
- Une barre dans une cellule s'écrit `\|` (`PIP`) ; le découpage se fait par `re.split(r"(?<!\\)\|", …)`, comme
  `todo_du_fichier`, jamais par `split("|")`. Une ligne de table s'ouvre **et se ferme** par une barre non
  échappée : sans barre finale, `[1:-1]` perd sa dernière cellule en silence, en-tête compris (refus de `TAB2`,
  2026-10-08) — elle se refuse, jamais ne se lit (0 cas sur 761 lignes, kit et 4 projets, le 2026-10-09).
- Chaque test bâtit son projet dans un dossier temporaire (`tempfile`), jamais le vrai dépôt ; un nouveau bloc se
  met **dans une fonction** (`test-vlp.py` est au seuil de complexité de pyright) et ne réutilise pas le `t`
  d'un `with` voisin. Chaque test a son mutant, joué par `vlp.py mutant … --attendu "<début du libellé>"`.
- `pyright` à zéro erreur sur les fichiers touchés, compte brut au compte rendu.

**Dehors** : le refactoring de `vlp_coeur.py` (`REF`) ; les tables des pages HTML ; toute TODO d'un autre projet
que pour les tests.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `TAB1` | Relever les lecteurs de tables qui coupent en silence | rien |
| `TAB2` | Leur donner la garde de la TODO | `TAB1` |
| `TAB3` | `clore` lit la TODO avant sa première écriture | rien |
| `TAB4` | Retirer une ligne de la TODO par `vlp.py oter` | rien |

`TAB3` et `TAB4` ne dépendent pas de `TAB1` ; toutes touchent `test-vlp.py` : à jouer l'une après l'autre.

---

<!-- FICHE:TAB1 -->
## TAB1 [x] — Relever les lecteurs de tables qui coupent en silence

**Session** : 3f47d6b9-9a6d-45ba-8289-028c74b240e2
**Session** : e86f6d35-8adb-4809-bac9-de327c523bb2 (relire)
**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py` (lecture seule), `context AI/08-etat.md` (le journal) — et rien d'autre.

**Prompt**
Relève, sans rien corriger, chaque endroit de `vlp_coeur.py` qui lit une table Markdown ligne à ligne : un
`split("|")`, un `strip("|")`, un `re.split` sur `|`, un `startswith("| ")` suivi d'un découpage. Cherche-les par
`grep -n` sur ces motifs, puis lis chaque fonction trouvée.

Pour chacune, dis : son nom, la table qu'elle lit (TODO, index, archive de l'index, table des clos, autre), ce
qu'elle fait d'une ligne qui a trop ou trop peu de cellules — **garde** (lève ou rend `GARDE:`), **tronque**
(lit la mauvaise cellule), **jette** (saute la ligne), ou **sans effet** (n'utilise que la première cellule).
Essaie chaque cas douteux sur une ligne fabriquée, par un appel Python d'une ligne : un verdict se prouve.

Écris le relevé au journal de `08-etat.md` (`## Journal des décisions`), une entrée `## 2026-10-08 — TAB1` : un
tableau « fonction · table · verdict · preuve », puis la liste de celles que `TAB2` doit garder.

**Critère de fin**
L'entrée `TAB1` existe au journal ; elle donne le nombre brut de lecteurs relevés et, pour chacun, le verdict et
l'appel qui le prouve ; aucun fichier de `scripts/` n'est modifié (`git diff --stat scripts/` vide).
<!-- /FICHE -->

---

<!-- FICHE:TAB2 -->
## TAB2 [x] — Leur donner la garde de la TODO

**Tentatives** (2026-10-09) — résolu par : cellules_de refuse une ligne sans barre finale (pas de barre finale), pour les trois lecteurs ; test et mutant ajoutés

**Session** : 23bf8e86-3386-40fa-9ac4-e194f42d135c
**Session** : fa25bc3b-29ea-4e52-ab83-95de6b1afdb5 (relire)
**Session** : 790ba1d9-c8d7-4603-8479-b30ce961b7a7
**Dépend de** : `TAB1`.
**Fichiers** : `scripts/vlp_coeur.py`, `scripts/test-vlp.py`, `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Le code de la tentative refusée est déjà là (commit `2d40dfd`) : `cellules_de`, la garde de `noms_de_table`,
`noms_des_sources` et `chemins_de_carte` pour `cmd_renvois`, ses tests `TAB2 : …`. **Pars de lui, ne le réécris
pas** : lis `git show 2d40dfd -- scripts/`, puis corrige le seul défaut que le relecteur a relevé (le refus, plus
haut) — `cellules_de` perd la dernière cellule d'une ligne sans barre finale, en-tête compris, sans rien dire.

`cellules_de` refuse une telle ligne : une ligne qui ne finit pas par une barre non échappée (après `strip`) lève
une `ValueError` qui le dit (« pas de barre finale »). Les trois appelants — `noms_de_table`, `todo_du_fichier`,
`nuits_du_fichier` — y gagnent la même garde ; leurs messages nomment toujours la ligne. Une ligne qui ne
commence pas par `|` n'est pas une ligne de table : ne change pas ce critère.

L'entrée `## 2026-10-08 — TAB2` du journal de `08-etat.md` dit « gardé » d'une tentative refusée : réécris-la en
`## 2026-10-09 — TAB2`, ce qui est vrai après ta correction. Retire sa puce « Imprévu » : la fuite des variables de
nuit est réglée par `ENV` (clos le 2026-10-09).

**Critère de fin**
Les tests `TAB2 : …` du WIP passent toujours, et un nouveau : `TAB2 : une ligne sans barre finale rend GARDE` —
un routage de `CLAUDE.md` dont une ligne (puis l'en-tête seul) n'a pas de `|` final : `renvois` rend `GARDE:`,
sort 1 ; une ligne de TODO sans barre finale lève la `ValueError`. Son mutant, qui rend `cellules_de` tolérante,
le fait tomber (`vlp.py mutant … --attendu "TAB2 : une ligne sans barre finale"`). `renvois` sur le kit rend le
même compte avant et après ta correction, sans `GARDE:` (`RENVOIS 129 nommés · 0 absents` le 2026-10-09). `test-vlp.py` passe en entier ;
`pyright` 0 erreur sur `vlp_coeur.py`. Comptes bruts au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:TAB3 -->
## TAB3 [x] — `clore` lit la TODO avant sa première écriture

**Session** : 790ba1d9-c8d7-4603-8479-b30ce961b7a7
**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Aujourd'hui, sur une TODO cassée (une ligne à 6 cellules), `cmd_clore` écrit le fichier de fiches et `CHANTIER.md`,
puis bute sur la feuille : `GARDE: … — CHANTIER.md et fiches écrits, feuille non écrite`. Reproduis-le d'abord
dans un projet temporaire, et note la sortie brute.

Puis fais lire à `cmd_clore` la TODO du **fichier d'état** de `CHANTIER.md` par `todo_du_fichier`, **avant**
toute écriture, avec les autres gardes du début. Une `ValueError` rend `GARDE: <son message> — rien écrit`, sort 1.
Un projet sans TODO, ou sans fichier d'état, se clôt comme avant : ne change pas son comportement.

**Critère de fin**
Un test `TAB3 : clore sur une TODO cassée rend GARDE, sort 1, rien écrit` : empreintes des fichiers du projet
temporaire identiques avant et après ; un second, `TAB3 : clore sur une TODO saine passe`. Le mutant qui retire
la lecture anticipée fait tomber le premier (`vlp.py mutant … --attendu "TAB3 : clore sur une TODO cassée"`).
`test-vlp.py` passe en entier ; `pyright` 0 erreur. Comptes bruts au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:TAB4 -->
## TAB4 [ ] — Retirer une ligne de la TODO par `vlp.py oter`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py`, `scripts/vlp.py` (sa docstring), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris la sous-commande `vlp.py oter <projet> <code> --raison T [--date D]` (`D` : aujourd'hui par défaut). Dans le
fichier d'état que nomme `CHANTIER.md`, elle tient trois écritures ensemble :

1. la rangée de la TODO dont la 2e cellule commence par `` `<code>` `` disparaît ;
2. dans la phrase de provenance au-dessus de la table, son numéro se retire, ou se marque retiré ; lis d'abord
   la vraie phrase de `context AI/08-etat.md` (`## La TODO ordonnée`) et dis au compte rendu la forme choisie ;
3. une entrée datée au `## Journal des décisions` : le code, son numéro, la raison.

Le numéro n'est jamais réattribué. Elle refuse, par `GARDE:` et sort 1, sans rien écrire : un code absent de la
TODO, un code d'un chantier ouvert (`courant_de`) ou déjà clos (sa lettre est dans « Lettres de fiche déjà
prises » de `CHANTIER.md`). Tout se calcule avant d'écrire ; puis `.tmp` et `os.replace`. La TODO se lit par
`todo_du_fichier`. Ajoute `oter` à la docstring de `vlp.py`.

**Critère de fin**
Tests `TAB4 : …` sur un projet temporaire : la rangée ôtée, le numéro hors de la phrase de provenance, une entrée
au journal (3 vérifications) ; un code absent, ouvert, clos : `GARDE:`, sort 1, empreinte du fichier inchangée
(3 vérifications). Le mutant qui saute le refus d'un code clos fait tomber le sien. `test-vlp.py` passe en
entier ; `pyright` 0 erreur. Comptes bruts au compte rendu.
<!-- /FICHE -->
