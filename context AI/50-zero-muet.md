> **QUAND LIRE** : on joue une fiche `ZER*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ZER<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ZER — Un vieux chantier ne se recompte plus à zéro

**CLOS** le 2026-09-24. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** ZER1..ZER1 (2026-09-24) : Un chantier clos sans commit de fiche retombe sur ses sessions entières, et le dit ; une découpe qui ne garde aucun tour le dit aussi.

**À quoi il sert.** Depuis `FIN` (la nuit du 2026-09-24), `vlp.py cout` rend un total de **0** sur
dix chantiers clos — M, C, T, S, L, W, X, F, O, Q —, six sans même une `GARDE:`. Aucun n'a de
commit `<ID> :` de fiche : ils datent d'avant la convention. `heures_commits` rend alors `{}` dès
qu'un commit nomme le préfixe — c'est voulu pour la première fiche d'un chantier **en cours**
(`FIN2`) —, et `plages` fait partir la fiche du dernier commit qui nomme le préfixe. Pour un
chantier clos, c'est sa clôture : aucun tour ne tombe après. Avant la nuit, `cout` passait au
repli et le disait. Après ce chantier, un chantier clos sans commit de fiche retombe sur les
sessions entières, sous une ligne qui dit pourquoi, et toute découpe qui ne garde aucun tour le
dit. Trouvé par le recompte à blanc de `RCP` (TODO n° 37).

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `heures_commits` | `scripts/vlp.py:953` à `991` | les heures des commits : `None` pour le repli, avec sa raison dans `pourquoi` ; `({}, …)` sans commit de fiche (ligne 990) |
| `plages` | `scripts/vlp.py:994` | sans commit de fiche, la fiche part du dernier commit qui nomme le préfixe (lignes 1007-1010) |
| `parts_aux_commits` | `scripts/vlp.py:1028` | mesure chaque session et ses sous-agents sur les plages ; `gardes` reçoit les remarques |
| ses appelants | `cmd_cout` (`scripts/vlp.py:398`, l'appel en 421) ; `regenerer` (1187, l'appel en 1195) | la découpe de `cout`, et celle de la page |
| `**CLOS**` | `scripts/vlp.py:1946` et `2125` | un chantier clos : une ligne qui commence par `**CLOS**`, posée par `clore` |
| la docstring | `scripts/vlp.py:25` (`cout`), `52` (`page`) | la syntaxe et la sortie de chaque sous-commande |
| les tests | `scripts/test-vlp.py` : `QFICHES` (446) ; la découpe (466 à 600 — `heures_commits` en 474 à 525, `cout` en 528, le dépôt `ouv` en 571 à 583) ; `plages` (604 à 630) | `verifier(nom, condition, détail)` ; la suite s'arrête au premier écart et l'imprime |

Une fiche de code écrit ses tests **d'abord**, les lance, et cite l'écart qu'ils impriment sur le
code d'avant : c'est son mutant (`methode-chantier.md`, « Anatomie d'une fiche »). Puis elle
corrige, et relance : `OK`.

**Mesuré à l'ouverture, le 2026-09-24.** `vlp.py cout` sur chaque fichier clos (sonde du
scratchpad, zéro écriture), face au `vlp.py` d'avant la nuit (`fda5816`) :
- les dix : 0 commit de fiche ; aujourd'hui `DÉCOUPE aux commits de fiche` et `TOTAL … 0 · 0
  tours` ; avant, `DÉCOUPE aucune — aucun commit « M1 : » ni d'une autre fiche : sessions
  entières` (M), et un total : M 11 362 254, C 7 816 316 — les chiffres de la feuille de route —,
  S 18 930 260 ;
- `git blame` : les lignes 1007-1010 viennent de `bb361ff` (`FIN1`) et `28708a7` (`FIN2`).

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dort ; à revoir au réveil).
- Le repli vaut pour un chantier **clos** sans aucun commit de fiche, et pour lui seul : sa
  ligne `**CLOS**` le dit, sans deviner d'après les messages de commit. En cours, la première
  fiche part toujours de l'ouverture (`FIN2`).
- Une découpe qui ne garde aucun tour le dit par une `GARDE:`, sans changer ses nombres.
- Joué à la main, dans la session du chef : la régression vient de `FIN`, repris cette nuit ; dix
  fiches de code sur dix ont dû être reprises après leur sous-agent.

**Ce qu'on ne fait pas.** Recompter les chantiers clos (`RCP`) : les dix retrouvent le chiffre
d'avant la nuit, sessions entières, pas une découpe — sans commit de fiche, il n'y a rien où
couper. La feuille de route ne change pas.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ZER1` | Le repli pour un chantier clos, et la découpe à zéro dite | rien |

---

<!-- FICHE:ZER1 -->
## ZER1 [x] — Le repli pour un chantier clos, et la découpe à zéro dite

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`heures_commits`, `parts_aux_commits`, `cmd_cout`, `regenerer`,
la docstring), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
1. Tests d'abord, dans `scripts/test-vlp.py`, dans le dépôt `ouv` (ligne 571).
   - `heures_commits` sur `ouv/q.md` : avec `clos=True`, `None` et `pourquoi` vaut
     `["chantier clos sans commit « Q1 : » ni d'une autre fiche"]` ; sans, `({}, [T0 + 100], [T0 + 60])`.
   - `cout` sur `ouv/qz.md` — `ouv/q.md` plus une ligne `**CLOS**` sous le titre — commence par
     `DÉCOUPE aucune — chantier clos sans commit « Q1 : » ni d'une autre fiche : sessions entières,
     sous-agents compris`, puis la table des sessions entières. `page --creer` sur `qz.md` n'a pas
     de ligne hors fiches.
   - `cout` sur `QFICHES` plus `**CLOS**` : la même découpe que `attendu`.
   - Une fiche dont la session n'a de tours qu'avant l'ouverture : `cout` porte
     `GARDE: découpe à zéro — aucun tour de 1 transcript ne tombe dans une plage`.
   Lance `py scripts/test-vlp.py` ; cite l'écart qu'il imprime.
2. `heures_commits(fichier, ids, pourquoi=None, clos=False)` : sans commit de fiche et `clos`,
   `None` et cette raison. `cmd_cout` et `regenerer` passent `clos` : une ligne du fichier
   commence par `**CLOS**`.
3. `parts_aux_commits` : si ni les fiches ni hors fiches n'ont de tour, la `GARDE:` ci-dessus.
4. La docstring : `cout` dit sa découpe, ses replis et cette garde ; `page`, le repli d'un clos.

**Critère de fin**
`py scripts/test-vlp.py` et `py scripts/test-mesure-tokens.py` rendent `OK` ; chaque cas de
l'étape 1 tombe sur un mutant ; `cout` rend aux dix chantiers leur total d'avant la nuit.
<!-- /FICHE -->
