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
