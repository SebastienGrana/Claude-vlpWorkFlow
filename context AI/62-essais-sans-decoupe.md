> **QUAND LIRE** : on joue une fiche `ESD*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ESD<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ESD — Les essais d'un chantier sans découpe, puis republier

**À quoi il sert.** `ESS` compte les essais `claude -p` dans le prix de leur fiche, mais pas sur
`DÉCOUPE aucune` : 9 clos (`X` `G` `A` `P` `L` `N` `Y` `U` `Q`) gardent 7,1299 $ d'essais hors chiffre.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 3 fiches, `ESD1` à jouer.

**Session** : 09d96d28-50bd-4b5e-916b-bc2b413e33f2

## Le socle commun

**Le fait qui porte le chantier** (`py scripts/vlp.py recompter .`, au cadrage) : les 9 sont
`gardé — DÉCOUPE aucune (chantier clos sans commit « X1 : » ni d'une autre fiche)` ; `recompte`
rend `None`, le chiffre inscrit reste. `cmd_cout`, sur cette branche, imprime les tables de
`mesure().main(ids)` sans `essais_de`.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `essais_de(session)` | `scripts/vlp.py:480` | les transcripts d'essais d'une session, triés ; [] sans dossier |
| `cmd_cout` | `scripts/vlp.py:520` | branche `DÉCOUPE aucune` à la l. 544 |
| `parts_aux_commits` | `scripts/vlp.py:1662` | comment un essai et ses sous-agents se mesurent (sortes 2 et 3) |
| `ligne_parts` / `ligne_cout` / `plus` | `scripts/vlp.py:1718` | le format d'une ligne de coût |
| `recompte(chemin)` | `scripts/vlp.py`, `def recompte` | (recompté ou None, méthode) ; `totaux(decoupe)[2]` = la part essais |
| `marquer` / `MARQUE_REC` / `MARQUE_GARDE` | `scripts/vlp.py:2303` | la cellule réécrite ; `BRUT` lit le nombre en fin de cellule |
| `cmd_recompter` | `scripts/vlp.py:2317` | `--ecrire` déclaré l. 3082 |

**Décidé au cadrage** (2026-09-25) :
- un gardé reçoit **son chiffre inscrit + ses essais** — rien d'autre ne se recalcule ;
- `--ecrire` n'écrit **que la part essais** : `REC` (+651 030, 0 essai) et `ESS` (+763 058, 0 essai,
  tout en `hors fiches`) restent tels quels — leur cause est celle de la TODO n° 67 ;
- un essai ne s'ajoute **qu'une fois** : un second `--ecrire` ne change plus rien ;
- on republie la **feuille de route seule**, pas les bilans de `SAG` ni de `FIL`.

💡 Proposé, la fiche peut dire mieux : une option `recompter --essais`, qui laisse intact le
`--ecrire` de `REC`.

**Dehors** : la cause des écarts de `REC` et `ESS` (TODO n° 67) ; les evals ; le dossier absent de
`X` (0,2829 $, ESS1) ; les pages de bilan.

Tests : `py scripts/test-vlp.py` ; `pyright` sur `scripts/vlp.py`, compte avant et après.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ESD1` | Montrer les essais d'un chantier sans découpe | rien |
| `ESD2` | Ajouter les essais au chiffre recompté, une fois | `ESD1` |
| `ESD3` | Écrire les essais et republier | `ESD2` |

Rien n'est parallélisable : chaque fiche se sert de la précédente.

---

<!-- FICHE:ESD1 -->
## ESD1 [ ] — Montrer les essais d'un chantier sans découpe

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`.

**Prompt**
Écris une fonction qui rend la somme des essais de sessions entières — pour chaque id,
`essais_de`, chaque essai mesuré en entier avec ses sous-agents, comme `parts_aux_commits` le
fait sur une plage. Elle rend le même tuple que les parts (tokens, tours, $, nombre).
Dans `cmd_cout`, branche `DÉCOUPE aucune`, après les tables de `mesure().main(ids)` : une ligne
`essais` au format `ligne_parts`, seulement s'il y en a — une sortie sans essai ne change pas
d'un octet. `recompte` s'en servira en `ESD2` : ne l'y branche pas encore.

**Critère de fin**
Un test dans `scripts/test-vlp.py` : un fichier sans commit de fiche, une session à 2 essais →
la ligne `essais` dit 2 ; sans essai → pas de ligne. **Mutant** : ne pas appeler `essais_de` fait
tomber le test. `py scripts/vlp.py cout "context AI/<fichier de L>.md"` : la ligne `essais`
montre ≈ 1,26 $ (table ESS4) ; celui de `Z` : aucune ligne.
<!-- /FICHE -->

---

<!-- FICHE:ESD2 -->
## ESD2 [ ] — Ajouter les essais au chiffre recompté, une fois

**Dépend de** : `ESD1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`.

**Prompt**
Dans `recompter`, un mode qui n'écrit que la part essais (le socle en propose l'option) :
- un gardé `DÉCOUPE aucune` → inscrit + essais de `ESD1` ;
- un chantier découpé → inscrit + min(part essais, écart) : jamais au-delà du recompté ;
- tout autre gardé, ou 0 essai → la cellule ne change pas.
La cellule garde son brut en fin (`BRUT`) et porte une marque d'essais en tête, que `marquer`
lit : si elle y est, on n'ajoute rien. Le mode sans `--ecrire` affiche l'écart par chantier et
la somme, comme `recompter` aujourd'hui.

**Critère de fin**
Un test : un gardé à 1 essai → le chiffre + l'essai ; **second passage → cellule identique**.
**Mutant** : ignorer la marque fait tomber le test (l'essai compté deux fois). `py scripts/vlp.py
recompter . --essais` : `SAG` +506 675, `FIL` +583 782, `REC` et `ESS` +0, les 9 avec leurs essais.
<!-- /FICHE -->

---

<!-- FICHE:ESD3 -->
## ESD3 [ ] — Écrire les essais et republier

**Dépend de** : `ESD2`.
**Fichiers** : la feuille de route locale (`page_feuille`), `context AI/08-etat.md`.

**Prompt**
Lance le mode de `ESD2` sans écrire, note sa somme ; puis avec `--ecrire`, et lis `ÉCRIT … total
A → B`. B − A doit égaler la somme d'avant. Relance-le : `ÉCRIT 0 cellules`. Republie la feuille
de route : `Artifact` `read` sur son URL (`CHANTIER.md`), puis publish du fichier local à cette
`url`, sans `favicon`. Au journal de `08-etat.md`, une section `ESD3` : la table chantier →
inscrit / essais ajoutés, les comptes bruts. À la ligne TODO n° 67, ajoute `ESS` (+763 058,
0 essai, tout en `hors fiches`).

**Critère de fin**
`ÉCRIT` au premier passage avec B − A = la somme affichée, `ÉCRIT 0 cellules` au second ; la
feuille republiée montre les 11 cellules marquées (9 gardés, `SAG`, `FIL`).
<!-- /FICHE -->
