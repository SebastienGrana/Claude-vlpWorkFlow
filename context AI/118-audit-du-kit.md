> **QUAND LIRE** : on choisit le prochain chantier du kit, on cherche la preuve d'une mesure ou
> d'un constat de l'audit du 2026-10-11 (chantier `AVL`), ou on veut savoir ce que devient un
> constat de `12-audit.md`. Une section `## AVL<n>` par fiche : n'ouvrir que celle qu'on cherche.

# Audit du kit — 2026-10-11 (chantier AVL)

Prend le relais de `context AI/12-audit.md`, l'audit du 2026-09-17. Statuts : ✅ établi, source
citée · 🟡 à décider · 💡 proposé. Le dépôt est public : des 4 projets équipés, rien que des
comptes, des codes et des noms de fichiers.

## AVL1 — Lire le kit : ce qu'il a, en chiffres

Mesuré le 2026-10-11, sur la branche `claude/audit-cairn-angle-6b2d80` à jour de `main`
(fusion `59db548`). Toutes les commandes se lancent depuis la racine du kit.

### Les tailles, dossier par dossier

✅ Fichiers suivis par Git, lignes par `wc -l` :

```bash
for d in scripts skills agents hooks templates evals exemples .claude-plugin .githooks archive "context AI"; do printf '%s | %s | %s\n' "$d" "$(git ls-files -- "$d" | wc -l)" "$(git ls-files -z -- "$d" | xargs -0 cat | wc -l)"; done
```

| Dossier | Fichiers | Lignes |
|---|---:|---:|
| `scripts/` | 12 | 26 120 |
| `skills/` | 12 | 1 280 |
| `agents/` | 2 | 123 |
| `hooks/` | 1 | 192 |
| `templates/` | 11 | 2 061 |
| la racine (doctrine et réglages) | 13 | 1 504 |
| `evals/` | 28 | 1 119 |
| `exemples/` | 6 | 478 |
| `.claude-plugin/`, `.githooks/`, `archive/` | 4 | 151 |
| `context AI/` | 348 | 38 202 |
| **Total** | **437** | **71 230** |

- ✅ La doctrine à la racine : 9 `.md`, 1 469 lignes — `methode-chantier.md` 491, `ARTEFACTS.md`
  248, `README.md` 177, `lecons-mesure.md` 158, `cloture.md` 129, `CLAUDE.md` 80, `nuit.md` 80,
  `enchainement.md` 60, `CHANTIER.md` 46 (`git ls-files | grep -v / | grep '\.md$' | tr '\n' '\0' | xargs -0 wc -l`).
- ✅ Le code pèse **79 %** des lignes hors contexte (26 120 sur 33 028) ; le contexte, **54 %**
  de tout le dépôt (38 202 sur 71 230).
- ✅ Fichier par fichier (`py -3 scripts/vlp.py lignes scripts/*.py skills/*/SKILL.md agents/*.md`) :

| Fichier | Lignes | Au cadrage |
|---|---:|---:|
| `scripts/test-vlp.py` | 9 472 | 9 460 |
| `scripts/vlp_coeur.py` | 9 128 | 9 116 |
| `scripts/test-boucle.py` | 1 844 | 1 844 |
| `scripts/boucle.py` | 1 485 | 1 485 |
| `scripts/mesure-tokens.py` | 812 | 812 |
| `scripts/vlp.py` | 604 | — |
| `scripts/sante.py` | 522 | — |
| `scripts/test-mesure-tokens.py` | 493 | — |
| `scripts/faux-claude.py` | 370 | — |
| `scripts/carnet.py` | 243 | — |
| `scripts/vlp_hook.py` | 87 | — |
| 8 `skills/*/SKILL.md` | 1 159 | 1 159 |
| `agents/fiche.md` · `agents/relecture.md` | 73 · 50 | — |

- ✅ Les +12 lignes de `test-vlp.py` et de `vlp_coeur.py` depuis le cadrage viennent de `main`
  (`0ab7c46`, la plage « `X1` à `X5` » de « Dépend de ») : `git diff --stat 633818c HEAD -- scripts`.
- ✅ Les 8 commandes : `chantier` 293, `tache` 184, `init` 170, `enchainer` 162, `chef` 146,
  `check` 144, `jouer` 31, `relire` 29 lignes.

### Les sous-commandes de `vlp.py`

- ✅ **56** sous-commandes, toutes dans la docstring : les noms des entrées « - \`nom » de la
  docstring (56, `matin` et `nuits` y ont deux entrées) sont ceux de `sous.add_parser(` dans
  `scripts/vlp_coeur.py:8878` et suivantes. S'y ajoutent `ajouter`, `lister`, `retirer` et `hook`,
  au second niveau sous `attente` (`vlp_coeur.py:8968-8977`).
- ✅ La docstring : 584 lignes, 54 523 octets (`ast.get_docstring(…, clean=False)`) ; `vlp.py`
  n'a pas une fonction, c'est elle plus 20 lignes de lanceur (604 lignes).
- ✅ `vlp.py <sous-commande> --help` répond (argparse), sans description : `usage` et arguments nus.

### Les suites de tests

| Suite | Comment elle se lance | Ce qu'elle joue | Durée |
|---|---|---|---|
| `scripts/test-vlp.py` | `py -3 scripts/test-vlp.py` | 883 appels `verifier(` ; lance les deux voisines | ✅ **260 s**, `OK`, code 0 |
| `scripts/test-boucle.py` | par `test-vlp.py`, dès son début (`test-vlp.py:165`) | `boucle.py` et `faux-claude.py` | « ~180 s », écrit à `test-vlp.py:165`, non remesuré seul |
| `scripts/test-mesure-tokens.py` | par `test-vlp.py` (`test-vlp.py:7455`, VIT24) | `mesure-tokens.py` | non mesurée seule |
| `vlp.py rapide <motif>` | avant la suite, dans le kit | groupes `--seul`, pyright des `.py` touchés, cliquet | ✅ 2,4 s (`AVL1` : aucun groupe) |
| `evals/` | `claude plugin eval` | 9 cas (`chantier`, `check`, `effort`, `filet`, `filet-bash`, `filet-rate`, `hook`, `init`, `tache`) | non lancée : payante, hors fiche |
| `.githooks/pre-commit` | à chaque commit | pyright si un `.py` est indexé, puis `claude plugin validate` (`:51`) | — |

- ✅ La durée : un passage, le 2026-10-11 de 19:13:21 à 19:17:41, `SORTIE=0 DUREE=260 s`, sortie
  `OK`. Les dernières écrites : 288,5 s le 2026-10-06 (`08-etat.md:2802`, VIT22), `real 3m44.266s`
  le 2026-10-08 (`08-etat.md:3147`, NUI20). « ~10 min » n'est plus l'ordre de grandeur.
- ✅ Ce passage vaut pour `cocher` : l'empreinte de la suite verte laisse `context AI/` de côté
  (`vlp_coeur.py:7142`, `KIT_EXCLUS`).

### La santé du code

✅ `py -3 scripts/vlp.py sante --racine .` (ruff 0.16.10 ; seuils : complexité 10 · branches 12 ·
arguments 5 · instructions 50 · imbrication 5) :

```
TOTAL 10 fichiers · 1060 fonctions · 59 au-dessus d'un seuil · 787 avec docstring
AST=RUFF 1060/1060 fonctions
```

| Fichier | Fonctions | Au-dessus d'un seuil | Sans docstring |
|---|---:|---:|---:|
| `vlp_coeur.py` | 467 | 35 | 78 |
| `boucle.py` | 57 | 15 | 5 |
| `mesure-tokens.py` | 36 | 3 | 7 |
| `test-vlp.py` | 314 | 3 | 119 |
| `faux-claude.py` | 17 | 1 | 9 |
| `test-boucle.py` | 84 | 1 | 39 |
| `test-mesure-tokens.py` | 21 | 1 | 9 |
| `carnet.py` | 20 | 0 | 7 |
| `sante.py` | 39 | 0 | 0 |
| `vlp_hook.py` | 5 | 0 | 0 |

- ✅ Les dépassements, par compte (une fonction peut en cumuler) : complexité 42 · branches 27 ·
  arguments 21 · instructions 16 · imbrication 5.
- ✅ Les six pires, par complexité : `repartir` (`vlp_coeur.py:9049`) 37 · `cmd_clore`
  (`vlp_coeur.py:6521`) 37, 190 instructions · `cmd_ouvrir` (`vlp_coeur.py:6824`) 29 · `main`
  (`boucle.py:1365`) 28 · `cmd_niveau` (`vlp_coeur.py:5914`) 27 · `main` (`mesure-tokens.py:699`) 27.
- ✅ Le cliquet tient : `vlp.py sante --cliquet --racine .` → `CLIQUET 1060 fonctions · vieilles 1058,
  dont touchées 2, renommées ou déplacées 0 · neuves 2` puis `CLIQUET TENU`.
- ✅ pyright 1.1.414 sur `scripts/` (`pyrightconfig.json` : `include` `scripts`, mode `standard`) :
  **0 errors, 0 warnings, 0 informations**, 11 fichiers analysés (`pyright scripts/ --outputjson`).

### Les 18 constats de `12-audit.md`, aujourd'hui

Ses constats numérotés (lignes 49 à 110). Ses « mesures brutes » (lignes 13 à 45) sont des coûts
de séance : c'est `AVL2`.

| # | Constat du 2026-09-17 | Aujourd'hui | Preuve du 2026-10-11 |
|---|---|---|---|
| 1 | `/vlp:check` cherche « Lettres prises » | ✅ corrigé | `commands/` n'existe plus ; `skills/check/SKILL.md:67` et `vlp_coeur.py:3407` disent « Lettres de fiche déjà prises » |
| 2 | `$1` / `$2` substitués avant lecture | ✅ corrigé | `grep -n '\$1\|\$2' skills/*/SKILL.md skills/*/references/*.md agents/*.md` : 0 ligne ; `$ARGUMENTS` dans 7 `SKILL.md` sur 8 (pas `check`) |
| 3 | `${CLAUDE_PLUGIN_ROOT}` littéral hors des commandes | ✅ vrai, déplacé | 0 dans `CHANTIER.md` et `templates/`, mais 5 lignes de `cloture.md` (5, 27, 54, 80, 103), que les commandes lisent par `vlp.py lire cloture.md` (`skills/tache/SKILL.md:179`) : `py -3 scripts/vlp.py lire cloture.md \| grep -c CLAUDE_PLUGIN_ROOT` → 5, rien n'est substitué ; la variable est vide dans le shell (`echo "${CLAUDE_PLUGIN_ROOT:-vide}"` → `vide`). `CLAUDE.md:39` la réserve aux commandes et à `hooks/hooks.json`. Piste 2 |
| 4 | La TODO du kit est vide | ✅ corrigé | `08-etat.md:365`, « La TODO ordonnée » : 12 lignes |
| 5 | `00-route.html` orpheline | ✅ corrigé | le fichier n'existe plus |
| 6 | Trois formats de titre de page | ✅ corrigé | 111 pages `.html` suivies dans `context AI/artefacts/` : 109 titres `vlp — …`, 2 hors chantier (« Essai ALE base », « Bilan des 22 chantiers ») |
| 7 | Deux formats de chemin dans `**Session**` | ✅ corrigé | `git grep -nE '^\*\*Session\*\* : .*[/\\]' -- "context AI"` : 0 ligne. ⚠️ Reste vrai à côté : des chemins de la machine dans le dépôt, piste 1 |
| 8 | Gabarits qui promettent des fichiers absents | ✅ corrigé | `01-projet`, `02-architecture`, `18-code` : 0 occurrence dans `templates/` et `skills/init/` ; `08-etat` n'est plus figé par `init` (0) ; gabarit `templates/context AI/NN-etat.md` |
| 9 | `(visuel)` hors de sa ligne, invisible | ✅ corrigé | `valider` le signale (`vlp_coeur.py:1588`) ; `/vlp:enchainer` valide d'abord (`skills/enchainer/SKILL.md:57`) |
| 10 | Le README se contredit sur les pages | ✅ corrigé | « tenues à jour à chaque fiche » : 0 dans `README.md` |
| 11 | Pas de `.gitignore` | ✅ corrigé | `.gitignore` porte `__pycache__/` ; `git status --porcelain \| grep -c pycache` : 0 |
| 12 | Une commande découpe l'autre au `sed` / `awk` | ✅ corrigé | `grep -nE '\bsed\b\|\bawk\b' skills/*/SKILL.md agents/*.md` : 1 ligne, l'interdit lui-même (`skills/tache/SKILL.md:92`) ; le partagé vit dans `skills/tache/references/` |
| 13 | « `Bash` n'est ouvert que pour lire » | ✅ corrigé | la phrase : 0 ; `skills/tache/SKILL.md:27` dit « n'interdit rien d'autre » |
| 14 | Règles dupliquées | ✅ vrai | même grep, hors `context AI/`, `exemples/`, `archive/` : « 250 lignes » 6 → 0 fichier, « six copies » 5 → 2, mais « comptes bruts » 10 → 15, « un seul endroit\|une seule fois » 7 → 8. Une occurrence n'est pas forcément une copie : non trié, c'est `AVL3` |
| 15 | La page de chantier retapée par le modèle | ✅ corrigé | `vlp.py page` la réécrit (`skills/tache/references/tache-page.md`) |
| 16 | Le kit ne se teste pas | ✅ corrigé | 3 suites (`test-vlp.py` vert, 260 s) ; 9 cas d'eval ; `claude plugin validate` au pre-commit (`.githooks/pre-commit:51`) |
| 17 | Fiches hors norme (E7 46 lignes, C1 34, norme ~20) | ✅ périmé | E7 et C1 sont clos ; la norme a changé : `vlp.py lignes` → `SEUILS page 250 · fiche 50 · socle 80` ; la plus longue fiche d'`AVL`, `AVL7`, fait 28 lignes |
| 18 | `/vlp:enchainer` remis « tel quel », « commode mais plus cher » | ✅ périmé | « commode » : 0 dans `README.md` et `skills/enchainer/SKILL.md` ; le défaut d'aujourd'hui est autre — le mode `agents` à réparer, ligne `ENA` de la TODO (`08-etat.md`) |

**Bilan** : 18 constats = **14 corrigés + 2 vrais + 2 périmés**.

### Les pistes que la lecture suggère

💡 Proposé : ni recherche de l'existant (`AVL6`), ni plan de découpe (`REF`). Coût en fiches à
4,40 $ — estimé.

1. **Des chemins de la machine dans le dépôt public** — 13 lignes, 5 fichiers de `context AI/`,
   portent `C:/Users/<nom>` ou `C:\Users\<nom>` (`git grep -c "C:[\\/]Users[\\/]<nom>"`). La règle
   globale dit « aucun chemin local dans un dépôt ». 1 fiche (≈ 4,40 $) : remplacer par `~`, et un
   contrôle qui refuse le motif au commit. 🟡 À décider : l'historique déjà poussé les garde.
2. **`${CLAUDE_PLUGIN_ROOT}` en clair dans `cloture.md`** (constat 3) — un modèle qui recopie la
   ligne lance `"/scripts/vlp.py"` ; ça ne marche que s'il devine le chemin vu ailleurs. 1 fiche
   (≈ 4,40 $) : `vlp.py lire` substitue la racine du kit, ou `cloture.md` écrit `<kit>`, et un
   test.
3. **`vlp_coeur.py` porte 35 des 59 dépassements**, dont `cmd_clore` à 190 instructions — nourrit
   `REF`, déjà dans la TODO ; pas de nouvelle ligne.
4. **273 fonctions sur 1 060 sans docstring (26 %)**, dont 119 dans `test-vlp.py` — le cliquet
   refuse une fonction neuve ou touchée sans docstring (`sante.py:425`) ; les anciennes sont pour
   `REF`.
5. **La docstring de `vlp.py` pèse 54 523 octets** pour 56 sous-commandes, et `CLAUDE.md` y
   renvoie : `AVL3` mesure ce qu'un modèle en lit ; `--help` existe mais ne dit rien.
6. **« comptes bruts » dans 15 fichiers** : copie ou renvoi ? `AVL3` le trie.
7. **La date du dernier passage des evals** : non vérifiée ; `evals/results/` est ignoré par Git.
8. **Sans fiche** : à la clôture d'`AVL`, la ligne de routage de `CLAUDE.md` qui mène à
   `12-audit.md` pour « choisir le prochain chantier » pointe vers ce fichier.
9. **Sans fiche** : la base de santé n'a pas suivi `0ab7c46` (`main`) — `sante --base --si-base
   --racine .` y ajoute 2 fonctions (`deplier_plages`) et en change 2 ; non commité ici (fiche
   d'audit), la prochaine fiche de code la verrouille.

## AVL2 — Mesurer les séances du kit depuis le 2026-09-17

Mesuré le 2026-10-11, sans script dans le kit : les coûts des clos sont **recopiés** de ce que
leurs clôtures ont écrit, pas remesurés ; seul le hors chantier est mesuré, par
`scripts/mesure-tokens.py`.

### Les clos, chantier par chantier

✅ **103** chantiers clos depuis le 2026-09-17 (105 à l'archive, moins `E` le 2026-09-10 et `M` le
2026-09-11) :

```bash
grep -oE '<td class="mono">2026-[0-9]{2}-[0-9]{2}</td>' "context AI/artefacts/archive-clos.html" | grep -oE '2026-[0-9-]+' | awk '$1 >= "2026-09-17"' | wc -l
```

- ✅ Les sources : le **$** est celui de la cellule « Tokens » de `context AI/artefacts/archive-clos.html`
  (posé à la clôture, recalé par `prix` et `recompter`) ; les **fiches**, le « joué N fiches » de la
  ligne **Fait.** du fichier de fiches, sinon la plage de l'archive, marquée « (plage) » ;
  l'**estimé**, celui de la ligne **Fait.**.
- ✅ Les deux sources concordent : les 49 chantiers qui écrivent un `$` dans leur ligne **Fait.** et
  dans l'archive disent le même, **0** écart.
- ✅ La ligne **Fait.** de 54 clos, jusqu'au 2026-09-26, n'écrit pas de `$` : l'archive seule le porte.
- « — » : aucun estimé écrit (clos au plus tard le 2026-09-26, jour d'`EST`) ; « non noté » : la ligne le dit ;
  « (taux plat) » : l'estimé est à l'ancien taux, marqué par `prix` (chantier `TAU`).

| Chantier | Clos le | Fiches | $ | $ par fiche | Estimé |
|---|---|---:|---:|---:|---|
| `A` | 2026-09-17 | 2 (plage) | 4,78 | 2,39 | — |
| `B` | 2026-09-17 | 3 (plage) | non écrit | — | — |
| `C` | 2026-09-17 | 2 (plage) | non écrit | — | — |
| `D` | 2026-09-17 | 6 (plage) | 6,06 | 1,01 | — |
| `F` | 2026-09-17 | 4 (plage) | 7,45 | 1,86 | — |
| `G` | 2026-09-17 | 2 (plage) | 6,91 | 3,46 | — |
| `H` | 2026-09-17 | 4 (plage) | 11,63 | 2,91 | — |
| `I` | 2026-09-17 | 3 (plage) | 5,27 | 1,76 | — |
| `J` | 2026-09-17 | 4 (plage) | 6,83 | 1,71 | — |
| `K` | 2026-09-17 | 3 (plage) | 4,88 | 1,63 | — |
| `L` | 2026-09-17 | 3 (plage) | 5,82 | 1,94 | — |
| `N` | 2026-09-17 | 3 (plage) | 5,83 | 1,94 | — |
| `O` | 2026-09-17 | 5 (plage) | 8,25 | 1,65 | — |
| `P` | 2026-09-17 | 3 (plage) | 5,61 | 1,87 | — |
| `Q` | 2026-09-17 | 5 (plage) | 16,26 | 3,25 | — |
| `R` | 2026-09-17 | 4 (plage) | 9,69 | 2,42 | — |
| `S` | 2026-09-17 | 5 (plage) | 16,03 | 3,21 | — |
| `T` | 2026-09-17 | 5 (plage) | non écrit | — | — |
| `U` | 2026-09-17 | 5 (plage) | 12,12 | 2,42 | — |
| `V` | 2026-09-17 | 4 (plage, V2 abandonnée) | non écrit | — | — |
| `W` | 2026-09-17 | 2 (plage) | 5,66 | 2,83 | — |
| `X` | 2026-09-17 | 3 (plage) | 8,73 | 2,91 | — |
| `Y` | 2026-09-17 | 5 (plage) | 18,10 | 3,62 | — |
| `Z` | 2026-09-17 | 4 (plage) | 9,30 | 2,33 | — |
| `NIV` | 2026-09-18 | 4 (plage) | 18,85 | 4,71 | — |
| `CPT` | 2026-09-23 | 4 (plage) | 17,02 | 4,25 | — |
| `REP` | 2026-09-23 | 4 (plage) | non écrit | — | — |
| `CAD` | 2026-09-24 | 1 (plage) | 5,73 | 5,73 | — |
| `CAS` | 2026-09-24 | 2 (plage) | 5,61 | 2,81 | — |
| `FIL` | 2026-09-24 | 3 (plage) | 27,43 | 9,14 | — |
| `FIN` | 2026-09-24 | 3 (plage) | 8,33 | 2,78 | — |
| `MTK` | 2026-09-24 | 2 (plage) | 4,92 | 2,46 | — |
| `PLA` | 2026-09-24 | 2 (plage) | 5,72 | 2,86 | — |
| `SAG` | 2026-09-24 | 5 (plage) | 10,10 | 2,02 | — |
| `TAR` | 2026-09-24 | 3 (plage) | 6,80 | 2,27 | — |
| `VAL` | 2026-09-24 | 1 (plage) | 3,05 | 3,05 | — |
| `ZER` | 2026-09-24 | 1 (plage) | 5,90 | 5,90 | — |
| `APC` | 2026-09-25 | 3 (plage) | 7,33 | 2,44 | — |
| `CON` | 2026-09-25 | 5 (plage) | 7,05 | 1,41 | — |
| `ESD` | 2026-09-25 | 3 (plage) | 8,98 | 2,99 | — |
| `ESS` | 2026-09-25 | 4 (plage) | 8,19 | 2,05 | — |
| `FOR` | 2026-09-25 | 3 (plage) | 7,45 | 2,48 | — |
| `GAR` | 2026-09-25 | 3 (plage) | 2,61 | 0,87 | — |
| `GLO` | 2026-09-25 | 3 (plage) | 6,10 | 2,03 | — |
| `JUG` | 2026-09-25 | 3 (plage) | 5,66 | 1,89 | — |
| `LEC` | 2026-09-25 | 5 (plage) | 16,26 | 3,25 | — |
| `PYT` | 2026-09-25 | 2 (plage) | 3,71 | 1,85 | — |
| `REC` | 2026-09-25 | 4 (plage) | 9,09 | 2,27 | — |
| `REV` | 2026-09-25 | 4 (plage) | 56,44 | 14,11 | — |
| `RLG` | 2026-09-25 | 1 (plage) | 3,61 | 3,61 | — |
| `UNI` | 2026-09-25 | 2 (plage) | 4,47 | 2,23 | — |
| `ABR` | 2026-09-26 | 5 | 9,73 | 1,95 | 3 fiches ≈12 $ (taux plat) |
| `ALE` | 2026-09-26 | 3 | 6,78 | 2,26 | 2 fiches ≈7,98 $ (taux plat) |
| `BAC` | 2026-09-26 | 2 | 5,01 | 2,50 | 1 fiches ≈3,90 $ (taux plat) |
| `ENC` | 2026-09-26 | 3 (plage) | 7,47 | 2,49 | — |
| `EST` | 2026-09-26 | 3 | 6,29 | 2,10 | 1 fiches ≈3,91 $ (taux plat) |
| `EVF` | 2026-09-26 | 4 | 14,24 | 3,56 | 2 fiches ≈7,79 $ (taux plat) |
| `FFE` | 2026-09-26 | 2 (plage) | 3,93 | 1,97 | — |
| `IDX` | 2026-09-26 | 3 | 6,49 | 2,16 | non noté |
| `RAT` | 2026-09-26 | 1 | 0,72 | 0,72 | 0,5 fiches ≈2,03 $ (taux plat) |
| `REL` | 2026-09-26 | 3 (plage) | 4,59 | 1,53 | — |
| `SON` | 2026-09-26 | 1 | 0,62 | 0,62 | 0,5 fiches ≈2,02 $ (taux plat) |
| `TOU` | 2026-09-26 | 3 | 4,62 | 1,54 | 0,5 fiches ≈2,01 $ (taux plat) |
| `VOI` | 2026-09-26 | 6 | 11,24 | 1,87 | 3 fiches ≈12 $ (taux plat) |
| `CHK` | 2026-09-27 | 2 | 2,22 | 1,11 | 0,5 fiches ≈2,07 $ (taux plat) |
| `ECA` | 2026-09-27 | 3 | 5,74 | 1,91 | 1,5 fiches ≈6,34 $ (taux plat) |
| `ECH` | 2026-09-27 | 1 | 1,36 | 1,36 | 0,5 fiches ≈2,12 $ (taux plat) |
| `FEU` | 2026-09-27 | 8 | 26,77 | 3,35 | 4 fiches ≈17 $ (taux plat) |
| `HAB` | 2026-09-27 | 6 | 26,45 | 4,41 | 2 fiches ≈8,09 $ (taux plat) |
| `OUV` | 2026-09-27 | 1 | 1,17 | 1,17 | 0,5 fiches ≈2,12 $ (taux plat) |
| `PLG` | 2026-09-27 | 1 | 1,21 | 1,21 | 0,5 fiches ≈2,12 $ (taux plat) |
| `PLI` | 2026-09-27 | 7 | 17,96 | 2,57 | 5 fiches ≈20 $ (taux plat) |
| `TYP` | 2026-09-27 | 1 | 1,64 | 1,64 | 1 fiches ≈4,16 $ (taux plat) |
| `VID` | 2026-09-27 | 2 | 6,20 | 3,10 | 0,5 fiches ≈2,02 $ (taux plat) |
| `BTN` | 2026-09-28 | 7 | 47,08 | 6,73 | 6 fiches ≈25 $ (taux plat) |
| `ENQ` | 2026-09-28 | 3 | 7,38 | 2,46 | 1 fiches ≈2,97 $ |
| `TAU` | 2026-09-28 | 4 | 20,05 | 5,01 | 1 fiches ≈4,42 $ |
| `ARC` | 2026-09-29 | 2 | 5,54 | 2,77 | 2 fiches ≈6,00 $ |
| `CLI` | 2026-09-29 | 1 | 1,74 | 1,74 | 1 fiches ≈3,01 $ |
| `ESR` | 2026-09-29 | 1 | 1,41 | 1,41 | 1 fiches ≈3,02 $ |
| `JNT` | 2026-09-29 | 3 | 4,83 | 1,61 | 3 fiches ≈9,00 $ |
| `LOC` | 2026-09-29 | 5 | 11,74 | 2,35 | 1 fiches ≈2,97 $ |
| `MUT` | 2026-09-29 | 1 | 1,76 | 1,76 | 1 fiches ≈3,01 $ |
| `PAR` | 2026-09-29 | 7 | 39,62 | 5,66 | non noté |
| `PIP` | 2026-09-29 | 1 | 2,41 | 2,41 | 1 fiches ≈2,98 $ |
| `REG` | 2026-09-29 | 3 | 7,07 | 2,36 | 1 fiches ≈3,03 $ |
| `VRB` | 2026-09-29 | 1 | 1,18 | 1,18 | 1 fiches ≈3,02 $ |
| `VIT` | 2026-10-07 | 23 | 322,08 | 14,00 | non noté |
| `ARP` | 2026-10-08 | 4 | 10,09 | 2,52 | 2,5 fiches ≈9,93 $ |
| `BRA` | 2026-10-08 | 1 | 3,32 | 3,32 | 1 fiches ≈3,95 $ |
| `MET` | 2026-10-08 | 10 | 71,38 | 7,14 | non noté |
| `NUI` | 2026-10-08 | 38 | 172,49 | 4,54 | 6 fiches ≈18 $ |
| `CTR` | 2026-10-09 | 1 | 3,70 | 3,70 | 1 fiches ≈3,99 $ |
| `ENV` | 2026-10-09 | 1 | 4,09 | 4,09 | 1 fiches ≈4,02 $ |
| `MUW` | 2026-10-09 | 1 | 3,19 | 3,19 | 1 fiches ≈4,02 $ |
| `NPB` | 2026-10-09 | 1 | 1,80 | 1,80 | 1 fiches ≈4,01 $ |
| `PRP` | 2026-10-09 | 4 | 10,52 | 2,63 | 4 fiches ≈16 $ |
| `RTD` | 2026-10-09 | 1 | 1,49 | 1,49 | 1 fiches ≈4,01 $ |
| `RTO` | 2026-10-09 | 1 | 3,66 | 3,66 | 1 fiches ≈3,99 $ |
| `TAB` | 2026-10-09 | 4 | 11,71 | 2,93 | 7 fiches ≈28 $ |
| `EFF` | 2026-10-10 | 3 | 20,59 | 6,86 | 3 fiches ≈12 $ (taux plat) |
| `ACA` | 2026-10-11 | 8 | 28,28 | 3,54 | 6 fiches ≈24 $ |
| `AMD` | 2026-10-11 | 7 | 37,80 | 5,40 | 6 fiches ≈24 $ |

**Bilan des clos** :

- ✅ **98** clos portent un `$` : **369** fiches, **1 472,07 $**, soit **3,99 $** la fiche.
- ✅ **5** clos n'ont que des tokens, pas de `$` : `B`, `C`, `T`, `V`, `REP` — 18 fiches par leur
  plage (`V` : 3 jouées, `V2` abandonnée). L'archive les dit « non recompté » (`B`, `C`, `T`,
  `V`) ou « recompté (REC) » sans prix (`REP`).
- ✅ Les plus chers à la fiche : `REV` 14,11 $ · `VIT` 14,00 $ · `FIL` 9,14 $ · `MET` 7,14 $ ·
  `EFF` 6,86 $ · `BTN` 6,73 $.

### La tendance, semaine par semaine

✅ Par date de clôture (un chantier compte en entier dans la semaine où il se clôt), les 98 clos
chiffrés :

| Semaine du | Clos | Fiches | $ | $ par fiche |
|---|---:|---:|---:|---:|
| 2026-09-14 (du 17 au 20) | 21 | 79 | 194,06 | 2,46 |
| 2026-09-21 | 48 | 143 | 420,01 | 2,94 |
| 2026-09-28 | 13 | 39 | 151,81 | 3,89 |
| 2026-10-05 | 16 | 108 | 706,19 | 6,54 |
| **Total** | **98** | **369** | **1 472,07** | **3,99** |

- ✅ `VIT` seul pèse 322,08 $ (23 fiches) dans la dernière semaine ; sans lui : 384,11 $ pour 85
  fiches, **4,52 $** la fiche.
- ✅ La fiche coûte de plus en plus : 2,46 → 2,94 → 3,89 → 4,52 $ (sans `VIT`).
- non mesuré : **pourquoi**. 💡 Pistes à vérifier, pas des causes : le relecteur à chaque fiche
  (`REV`, 2026-09-25), l'effort `xhigh` puis `high` (`VIT`, `EFF`), des fiches de code plus
  grosses, un contexte de départ plus lourd.

### L'estimé face au joué

- ✅ **45** clos portent un estimé chiffré : estimé **91** fiches · **348,03 $** ; joué **167**
  fiches · **574,89 $** — **×1,65** en $, **×1,84** en fiches.
- ✅ Sans les 21 estimés « (taux plat) », dont le $ n'est pas au même prix : 24 clos, estimé 52,5
  fiches · 191,35 $, joué 97 fiches · 357,25 $ — **×1,87** en $, **×1,85** en fiches.
- ✅ L'écart grandit : semaine du 2026-09-21 **×1,25** en $ (19 clos, 29,5 → 60 fiches) · du
  2026-09-28 **×1,64** (12 clos, 20 → 32) · du 2026-10-05 **×1,96** (14 clos, 41,5 → 75).
- ✅ 4 clos disent « estimé non noté » (`IDX`, `PAR`, `VIT`, `MET`) ; 54, clos au plus tard le
  2026-09-26, jour d'`EST`, n'en ont pas.
- ➡️ Le cadrage sous-estime d'un facteur proche de **2**, en fiches comme en $ : le socle d'`AVL`
  l'a déjà pris en compte (facilité tirée du haut de la fourchette).

### Le hors chantier

✅ **67** séances du kit qu'aucune ligne `**Session**` ne cite ont des tours entre le 2026-09-17 et
le 2026-10-11 (sur 267 transcripts du kit actifs depuis le 2026-09-17, 200 cités) :

| Séances | Tours | $ | Minutes actives | dont attente | Pauses retirées |
|---:|---:|---:|---:|---:|---:|
| 67 | 2 733 | **297,56** | 1 586 | 475 | 47 |

- ✅ Dont leurs sous-agents : 162 tours, 9,80 $ (les séances seules : 2 571 tours, 287,76 $).
- ✅ Le hors chantier fait **16,8 %** de la période : 297,56 $ sur 1 769,63 $ (1 472,07 $ de clos
  chiffrés + 297,56 $).
- ✅ 3 des 203 ids cités ne sont dans aucun dossier de transcripts du kit (cités d'ailleurs, non
  cherché).

La commande, depuis la racine du kit (Git Bash) :

```bash
grep -h '^\*\*Session' "context AI/"*.md /d/ProgPerso/Claude-vlpWorkflow/.claude/worktrees/*/"context AI/"*.md | grep -oE '[0-9a-f]{8}-[0-9a-f-]{27}' | sort -u > cites.txt
find ~/.claude/projects -maxdepth 2 -path '*/D--ProgPerso-Claude-vlpWorkflow*' -name '*.jsonl' -newermt 2026-09-17 | grep -v -F -f cites.txt | tr '\n' '\0' | xargs -0 py -3 scripts/mesure-tokens.py --plage 2026-09-17T00:00:00 2026-10-11T23:59:59 --actif
```

💡 Tri de ma main, par le premier message de chaque séance (une séance a souvent fait plus d'une
chose) :

| Nature | Séances | Tours | $ |
|---|---:|---:|---:|
| discussion, règle, ligne de TODO | 28 | 1 294 | 144,11 |
| cadrage par `/vlp:chantier`, non cité | 6 | 289 | 38,45 |
| tâche en worktree hors chantier | 13 | 305 | 26,45 |
| fiche ou contrôle non cité | 7 | 158 | 22,19 |
| chef ou matin | 5 | 211 | 18,84 |
| revue de code | 1 | 73 | 17,94 |
| hors du kit, ou sans objet au premier message | 4 | 207 | 17,18 |
| nuit (`claude -p`) non citée | 3 | 34 | 2,60 |

- ✅ La plus grosse : « Audit complet des artefacts Cairn » (2026-09-22), 358 tours, 42,91 $ —
  14 % du hors chantier.
- ⚠️ Une part est du travail de chantier sans ligne `**Session**` : les cadrages d'avant `CAD`
  (2026-09-24, depuis lequel le cadrage compte), les fiches de `V` (aucune ligne `**Session**`,
  `18-evals.md`). Elle n'est ni dans un chantier, ni ailleurs : ici.
- non mesuré : la part des séances citées qui tombe hors de leur découpe (après un `clore`, entre
  deux chantiers) — comme pour Cairn (`ACA2`).

### Les transcripts d'avant le 2026-10-03

✅ **Retrouvés : oui, 192 séances.** Le dossier du chemin C: existe encore :
`~/.claude/projects/C--Users-<nom>-Documents-ProgPerso-Claude-vlpWorkflow`, **162** séances et
**111** sous-agents (fichiers du 2026-09-10 au 2026-10-04), plus **30** séances et 2 sous-agents
dans 10 dossiers de worktrees.

- ✅ Toutes sont aussi sur D: : 0 séance seulement sur C: ; sur les 162 du dossier principal, 1
  fichier diffère entre les deux copies (`cmp`). D: en a 28 de plus, toutes commencées à partir
  du 2026-10-03 12:47 UTC, la séance du déménagement.
- ✅ D: seul suffit donc à la mesure ci-dessus.

```bash
cd ~/.claude/projects
comm -3 <(ls C--Users-<nom>-Documents-ProgPerso-Claude-vlpWorkflow/*.jsonl | xargs -n1 basename | sort) <(ls D--ProgPerso-Claude-vlpWorkflow/*.jsonl | xargs -n1 basename | sort) | awk -F'\t' '{print ($1 ? "C seul" : "D seul")}' | sort | uniq -c
```

### Les pistes

💡 Proposé — sans recherche de l'existant (`AVL6`).

1. **Le hors chantier ne paraît nulle part** : 297,56 $, 16,8 % de la période, sur aucune page.
   Un `vlp.py hors <projet> --depuis D` ferait en un appel les deux commandes ci-dessus — 1 fiche
   (≈ 4,40 $). 🟡 À décider : le montrer sur la feuille de route ?
2. **Comprendre la hausse du $ par fiche** (2,46 → 4,52 $) avant d'en chercher le remède :
   `vlp.py compteur` par chantier, comme `ACA2` pour Cairn — 1 fiche d'audit.
3. **L'estimé ×1,85** : une règle d'estimation qui double le compte du cadrage, ou qui le tire de
   l'historique des clos — pour `AVL7`.
4. **Sans fiche** : les 5 clos sans `$` (`B`, `C`, `T`, `V`, `REP`) — `prix` ne pose rien sur une
   page sans `$` ; les laisser tels quels, ou les marquer « non chiffré » sur l'archive.
5. **La première fiche d'un chantier perd ses tours derrière un commit d'étape.** ✅ Vu sur ce
   chantier : `cout` rend `AVL1 · 0 · 0 tours · 0,00 $`, et son travail tombe « hors fiches ».
   `plages` fait partir la première fiche du « dernier commit antérieur qui nomme le préfixe »
   (`scripts/vlp_coeur.py:2576`) : mon commit de suivi `AVL1 : case cochée…` (19:22:41), posé
   avant le commit au titre `AVL1 : Lire le kit…` (19:22:43), en est devenu le début — deux
   secondes. Le total du chantier ne change pas, seul son partage. Les fiches suivantes partent du
   commit de la précédente : non touchées. 💡 Le début de la première fiche ignorerait les commits
   de cette même fiche — 1 fiche de code, avec son test.
