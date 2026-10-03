> **QUAND LIRE** : on cherche la source d'un chiffre « (synthèse) », « A1 » ou « A2 » d'une fiche `VIT`.
> Versionnée le 2026-10-04 (page des critères de `VIT`, Q5) ; les rapports A1 et A2 ne le sont pas.
> Les numéros de ligne cités sont ceux du 2026-10-03 : ils ont dérivé depuis.

# Synthèse des deux audits vitesse — kit vlp (2026-10-03)

Relecteur des rapports `audit-vitesse.md` (**A1**) et `audit-vitesse-2.md` (**A2**).
Statuts : ✅ établi (source ou mesure citée) · 💡 proposé · ❓ inconnu.
Lecture seule : aucun test lancé, aucun fichier du projet touché, aucune écriture Git.

⚠️ `scripts/vlp.py` et `scripts/test-vlp.py` sont **modifiés, non commités** (+108 / +92 lignes, `git diff --stat`).
Les numéros de ligne ci-dessous sont ceux de l'arbre de travail à 19:45.

---

## 1. Verdict en 3 lignes

- ✅ Les deux audits disent juste sur l'essentiel : **le temps part dans les suites de tests rejouées en entier**, surtout par le **mutant** (suite entière, sans arrêt) et par le **relecteur** (AVANT + APRÈS + mutant).
- ✅ Deux chiffres sont à corriger : `test-vlp.py` sans boucle ≈ **123 s** (mesure directe de A2), pas « 0 à 1 min » ; `test-boucle.py` ≈ **6 à 7 min** sous charge, pas « ~220 s ».
- ⚠️ Les deux **sous-estiment le risque qualité** de trois pistes : le mutant arrêté au premier écart, le cache de résultats, et le `.pyc` couplé à un mutant rapide.

---

## 2. Vérifications à la source

| Affirmation | Statut | Preuve |
|---|---|---|
| `hooks.json` lance `python3` ET `py` | ✅ | `hooks/hooks.json` : **7 entrées**, chacune doublée (PostToolUse ×3, PostToolUseFailure ×2, PreToolUse ×2, SubagentStop ×1 — chaque fois `python3` puis `py`) |
| Les deux tournent vraiment | ✅ | `which -a` : `python3` ×2 et `py` ×2 sur le PATH ; le tampon `premier_lancement` (`vlp.py:550-556`) évite l'**action** double, pas le **démarrage** double ; son docstring dit « les deux lanceurs partent ensemble » |
| Hooks en parallèle | ✅ | doc officielle, mot pour mot : « All matching hooks run in parallel. » ([hooks](https://code.claude.com/docs/en/hooks), lu le 2026-10-03) |
| Dédoublonnage des deux | ❌ | même page : « If you define the same handler in more than one settings file, it runs once. A plugin's or skill's copy of the same handler stays separate. » — `python3` et `py` sont deux handlers |
| `cmd_mutant` relance toute la suite | ✅ | `vlp.py:7653` : défaut = `test-vlp.py` voisin ; `test-vlp.py:6049` lance `test-boucle.py` → le mutant paie aussi test-boucle |
| … sans arrêt au premier écart | ✅ | `vlp.py:7660` `VLP_TOUS_ECARTS="1"` ; `test-vlp.py:76` ne sort plus. **Mais** `test-boucle.py:76-79` ignore cette variable et sort au 1er écart |
| … dans le vrai fichier | ✅ | `vlp.py:7656-7666` : `open(fichier, "wb")` puis restitution dans un `finally` |
| Relecteur : AVANT, APRÈS, mutant | ✅ | `agents/relecture.md:29-32` : « Rejoue le critère de fin … dans AVANT puis dans APRÈS », puis « le mutant … relance le test » |
| `textes_contexte` : un `git show` par fichier | ✅ | `vlp.py:5840-5842` : boucle `for n in noms: git_texte(["show", …])` |
| `test-vlp.py` lance `test-boucle` en série | ✅ | `test-vlp.py:6043` `subprocess.run` (bloquant), appelé `:6049` ; **10 groupes** `tester_*()` viennent après (`:6091` à `:7072`) |
| Numéros de ligne périmés dans `101-chef-de-nuit.md` | ✅ | **7 sur 7** vérifiés : `carte` 714 → **814**, `cmd_cocher` 1055 → **1162**, `cmd_gardien` 2027 → **2183**, `todo_du_fichier` 3223 → **3415**, `cmd_clore` 4850 → **5924**, `cmd_ouvrir` 5134 → **6219**, `cmd_mutant` 5569 → **7632** ; **105** renvois `vlp.py:N` dans le fichier (A2 disait 91) |
| Plafond de 10 min de l'outil Bash | ✅ | doc officielle, mot pour mot : « Maximum timeout the model can set for a foreground Bash or PowerShell tool command, in milliseconds (default: 600000, or 10 minutes). » ([env-vars](https://code.claude.com/docs/en/env-vars), lu le 2026-10-03) |
| … puis bascule en arrière-plan | ✅ | doc officielle : « A command that starts in the foreground and then moves to the background, for example at its timeout, gets 30 minutes from the move » ([tools-reference](https://code.claude.com/docs/en/tools-reference), lu le 2026-10-03) |
| `test-vlp.py` appelle `vlp` dans son processus | ✅ | `test-vlp.py:252-254` `appel()` → `mod.main(argv, s)` |
| `depot_matin` reconstruit le dépôt | ✅ | **15** occurrences de `depot_matin(` (A2 disait 17 appels ; une est la définition, `:6127`) |
| Aucun `.pyc` écrit depuis une session Claude (A1) | ❌ | `PYTHONDONTWRITEBYTECODE=1` bien posé dans le shell ; mais `scripts/__pycache__/vlp.cpython-314.pyc` est daté **19:19:44** aujourd'hui → un lanceur l'écrit (hook ou terminal) ; il est **périmé** (source 19:42:31) |
| La carte : 3 lancements | ✅ | `skills/tache/SKILL.md:17` ; les 2 relais se taisent après import (`vlp.py:893-899`) mais paient le démarrage |

---

## 3. Contradictions

### 3.1 `test-vlp.py` sans `test-boucle` — **tranchée**
- A2 : **123,2 s**, mesure directe (`a2-profil.py` exécute chaque nœud du module, saute `tester_boucle`, ne chronomètre que `subprocess.run`).
- A1 : « ~0 à 1 min », par **soustraction** de deux chiffres pris à des moments différents (479–551 s moins 496 s).
- ✅ Verdict : **~2 min sous charge** (A2). La soustraction de A1 est trop bruitée pour conclure.

### 3.2 `test-boucle.py` — **tranchée en ordre de grandeur**
- A2 : ~220 s, **extrapolé à la ligne** depuis 60 s de profil (ligne 442 sur 1 660). Les cas n'ont pas le même coût : l'extrapolation linéaire ne tient pas.
- A1 : 496 s, relevé dans une transcription (une seule mesure, sous charge).
- Recoupement : suite entière 479–551 s (A1) − 123 s (A2) ≈ **356 à 428 s** pour test-boucle dans la suite.
- ✅ Verdict : **~6 à 8 min sous charge** ; 220 s est trop bas. ❓ La valeur poste au repos reste à mesurer.

### 3.3 Hooks en série ou en parallèle — **tranchée**
- ✅ En parallèle (doc officielle, citée plus haut). A1 laissait la question ouverte.
- Conséquence : le doublon `python3`/`py` coûte du **CPU et de la mémoire**, pas de la latence (latence = le plus lent des deux, ~0,45 s, A2).
- Donc la piste « un seul handler » gagne **peu de secondes** ; le **lanceur mince** gagne la latence.

### 3.4 Mutant : « arrêt au 1er écart » (A1) contre « mutant ciblé » (A2) — **ouverte, à trancher par mesure**
- Les deux visent le même temps mort. Voir les risques en section 4.

---

## 4. Ce que les deux ont raté — la qualité

### 4.1 Le mutant arrêté au premier écart
- ✅ Aujourd'hui, `MUTANT ATTRAPÉ` compte **n'importe quel** `ÉCART:` (`vlp.py:7672-7676`).
- ✅ La règle dit pourtant que le mutant est « le code cassé exprès que **ce test** doit faire tomber » (`methode-chantier.md:383-386`).
- ❌ Avec l'arrêt au premier écart : si un vieux test tombe d'abord, on ne sait plus si **le test de la fiche** tombe. Un test creux passerait.
- 💡 Parade : `mutant … --attendu "<libellé>"` → s'arrête **quand ce libellé tombe** ; sinon `MUTANT VIVANT pour <libellé>`. C'est plus rapide **et** plus strict qu'aujourd'hui.

### 4.2 Le mutant ciblé (sous-ensemble de tests)
- Le risque n'est pas un faux vert : un sous-ensemble rend `VIVANT` plus souvent, c'est une **fausse alarme**.
- Le vrai risque : un sous-ensemble mal lié ne contient pas le test nommé. Même parade : `--attendu`.

### 4.3 Le cache de résultats (A1, piste 2)
- ❌ Une clé « `scripts/*.py` + `.md` lus » donne un **faux vert** :
  - ✅ les tests lisent hors de `scripts/` : `templates` ×**32**, `methode-chantier.md` ×9, `SKILL.md` ×7, `hooks.json` ×6, `cloture.md` ×5, `nuit.md` ×4, `plugin.json` ×3 (`grep -o` dans `test-vlp.py`) ;
  - ✅ le résultat dépend de la machine : **22** tests sur `shutil.which` / plateforme ; des `SAUTÉ:` (git absent, hors Windows, `claude.exe` absent — `test-vlp.py:653-3282`) ; un `OK` d'ici n'est pas un `OK` ailleurs ;
  - deux Python différents (`python3` 3.14.7, `py` 3.14.6, A1).
- ❌ Plus grave : le relecteur existe pour **ne pas croire** le sous-agent (« Tu ne l'as pas écrite : cherche ce qui cloche », `agents/relecture.md:9-10`). Lui faire reprendre un vert écrit par le joueur retire le contrôle.
- 💡 Parade : un cache n'est sûr que s'il est **écrit par un script** (jamais par un agent), avec une clé = **tout le kit suivi par Git** (`git ls-files -s` + diff non commité) + version de Python + version de Git + les lignes `SAUTÉ:`. Et le relecteur garde au moins son **mutant** dans APRÈS.
- 💡 Plus simple et sans risque : la piste de A2 — **AVANT = le seul nouveau test**. AVANT ne sert qu'à voir ce test tomber sur l'ancien code.

### 4.4 `.pyc` + mutant rapide : un risque neuf
- ✅ Python valide un `.pyc` par **date de modification (à la seconde) et taille** du source (mode par défaut, PEP 552).
- 💡 Scénario : un mutant de même taille (`<` → `>`, `1` → `0`) écrit, un `.pyc` compilé dessus, puis le source rendu **dans la même seconde** → même date, même taille → **le code muté tourne en production**, sans erreur.
- Aujourd'hui, la suite de 10 min l'empêche ; un mutant de 2 s (pistes « arrêt » et « lanceur mince ») le rend possible.
- 💡 Parades : jouer le mutant **dans une copie** (jamais le vrai fichier) ; ou `PYTHONPYCACHEPREFIX` vers un dossier jetable pendant le mutant ; ou `.pyc` en mode `checked-hash`.

### 4.5 La copie pour le mutant (A1 : « une copie de `scripts/` »)
- ❌ Insuffisant : `test-vlp.py` lit `../templates` (`test-vlp.py:1042, 1987, 2353`…) et `RACINE = dirname(ICI)` (`:2184`).
- 💡 Copier le **kit entier** (hors `.git`, `context AI`, `__pycache__` — la liste `KIT_EXCLUS` existe déjà, `vlp.py:6486`).

### 4.6 Le vrai fichier muté, vu par tous
- ✅ Les hooks lancent `${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py`, et le plugin suit le dossier principal (mémoire « Plugin chargé = main »).
- 💡 Pendant un mutant de `vlp.py` dans `main`, **le `gardien` de toutes les sessions tourne muté** : il peut laisser passer ce qu'il doit bloquer. A1 le dit en passant ; c'est un argument **qualité**, pas seulement vitesse, pour la copie.

### 4.7 Tests sélectifs pendant l'itération
- Une régression ailleurs passe pendant l'itération : c'est voulu.
- 💡 Parade obligatoire : **une suite complète avant le commit**, vérifiée **par un script** (règle 4 du projet), pas par la prose. Par exemple `cocher --verifier` exige un `OK` complet daté après la dernière écriture.

### 4.8 Parallélisme
- ✅ Mémoire déjà en défaut (WinError 1455, mémoire du 2026-10-02).
- 💡 Ordre : **réduire les processus d'abord** (lanceur mince, `cat-file --batch`), paralléliser ensuite. Les deux audits le disent ; je confirme l'ordre.

### 4.9 Petit constat en passant
- ✅ **468** fichiers `vlp-carte-*` traînent dans `%TEMP%` (le ménage de `tampon_neuf`, `vlp.py:565-568`, ne vise que `vlp-hook-` et `vlp-filet-`). Pas un sujet de vitesse ; une fuite.

---

## 5. Accords des deux audits

- ✅ (vérifié) Le mutant rejoue toute la suite, test-boucle compris.
- ✅ (vérifié) Le relecteur rejoue AVANT, APRÈS, mutant.
- ✅ (vérifié) Hooks doublés `python3`/`py`.
- ✅ (vérifié) Numéros de ligne périmés dans les fiches.
- ✅ (mesuré par les deux, concordant) Un `vlp.py` lancé coûte ~0,3–0,5 s ; le même appel en processus 5–19 ms.
- ✅ (mesuré par les deux) Copier un dépôt modèle : ~56 ms contre 363–508 ms pour `git init` + commits.
- 💡 Pistes communes : lanceur mince, test-boucle en parallèle, carte de symboles, `MEMORY.md` allégé, découpage de `vlp.py` **après** la carte.
- Attention : le « −26 % » du lanceur mince n'a **qu'une mesure** (A1, 3 essais alternés sur un cas). A2 confirme le mécanisme (−240 ms par lancement), pas le pourcentage.

---

## 6. Pistes fusionnées, classées par gain sur coût

| # | Piste | Gain (source) | Coût | Risque qualité → parade |
|---|---|---|---|---|
| 1 | **Mutant dans une copie du kit, arrêté quand le test attendu tombe** (`--attendu`) | ~600 s → **1–3 min** par mutant, 1 à 3 par fiche (A1 mesure 602 s médiane ; gain estimé A1/A2) | 1 fiche | **baisse** du risque (plus de vrai fichier muté) ; parade 4.1 et 4.5 |
| 2 | **Relecteur : AVANT = le seul nouveau test** | **−1 suite** en mode agents (~6–8 min, estimé A2) | ½ fiche (prose de `relecture.md`) | faible ; APRÈS reste complet |
| 3 | **Lanceur mince** `vlp.py` + `.pyc` | −240 ms par lancement (A2 mesure) ; −26 % sur un cas nuit (A1, 1 mesure) ; aussi la latence des hooks | 1 fiche | `.pyc` + mutant (4.4) → faire **après** la piste 1 |
| 4 | **`git cat-file --batch`** dans `textes_contexte` | `ouverts --rev` 3,7 s → ~0,4 s (A2 mesure) ; `git show` = 986 appels, 32 s de la suite (A2) | 1 fiche | faible ; test existant `tester_ouverts` |
| 5 | **Dépôt modèle copié** dans `depot_matin` (15 appels) | `tester_matin` = 73 s, 59 % de test-vlp (A2 mesure) ; gain 💡 −30 à −50 s | ½–1 fiche | nul si le dépôt modèle est neuf par test (copie) |
| 6 | **test-boucle en parallèle** de test-vlp | suite = max au lieu de somme : **−~2 min** (💡, sur 123 s A2) | ½ fiche | mémoire (1455) → après les pistes 3–5 |
| 7 | **Hooks à un seul handler** (+ `async` pour `attente hook`) | CPU/mémoire ÷2 ; latence faible (hooks parallèles, doc) | ½ fiche (+ `test-vlp.py` verrouille `hooks.json`) | postes sans `py` ou sans `python3` → choisir à `/vlp:init` |
| 8 | **Carte de symboles** `vlp.py symboles` (ast) ; fiches citent des noms | −1 à −5 tours/fiche (💡, A1 et A2, non mesuré) | 1 fiche + nettoyage du socle NUI | nul |
| 9 | **Tests sélectifs** `--seul <groupe>` pendant l'itération | −8 à −15 min/fiche (💡 A1) | 2 fiches (41 blocs `with` nus → fonctions nommées) | régression manquée → parade 4.7, **suite complète exigée par script** |
| 10 | **Plafond Bash** `BASH_MAX_TIMEOUT_MS` à 1 800 000 | évite la bascule à 600 s et les tours de suivi | réglage utilisateur | nul |
| 11 | `MEMORY.md` 13 Ko → ~4 Ko | ~2,5 k jetons/tour (💡 A1) | ½ séance, hors code | nul |
| 12 | **`/clear` rappelé par `cocher`** | contexte médian **186 k** jetons (A1 mesure) → 💡 40–70 k | ½ fiche | nul |
| 13 | test-boucle en 3 lots (`ProcessPoolExecutor`) | 💡 ÷2 à ÷3 | 1 fiche | mémoire → en dernier |
| 14 | `boucle.py` appelle `vlp` dans son processus | 💡 −35 à −45 % de test-boucle (A1) | 1–2 fiches | change la production ; état global → garder 1–2 vrais sous-processus testés |
| 15 | Cache de résultats de suite | −16 min/fiche en mode agents (💡 A1) | 1 fiche | **faux vert** (4.3) → à ne faire qu'avec la clé large, écrit par script ; **déconseillé** tant que la piste 2 suffit |
| 16 | Découper `vlp.py` en modules | lecture ; sélection naturelle | 3–6 fiches | régressions, conflits → après 8 et 9 |

---

## 7. Décisions pour l'utilisateur

- **Plafond Bash** : régler `BASH_MAX_TIMEOUT_MS` (réglage de sa main) — oui à 30 min / non.
- **`vlp.py` devient un lanceur mince** (règle « un seul fichier » déplacée) — oui / variante `scripts/v.py` / non.
- **Mutant : arrêt quand le test attendu tombe** — oui avec `--attendu` / garder la suite entière / sous-ensemble ciblé (A2).
- **Relecteur : AVANT réduit au nouveau test** — oui / non.
- **Cache de résultats** — abandonné / gardé avec clé large écrite par script.
- **`boucle.py` en processus** (« boucle.py lance la vraie mécanique ») — oui / non.
- **Hooks : un seul interprète** choisi à l'installation — oui / garder le doublon pour la portabilité.
- **Plugins sans rapport** (`data`, `design`, `engineering`) désactivés dans ce projet — oui / non.

---

## 8. Découpage proposé — chantier « vitesse »

1. **VIT1 — Mesure de base** : chronos poste au repos de test-vlp seul, test-boucle seul, un mutant ; comptes bruts. Aucune dépendance.
2. **VIT2 — Mutant dans une copie, `--attendu`** : copie du kit, arrêt quand le libellé tombe, `--tous` garde l'ancien. Dépend de VIT1.
3. **VIT3 — AVANT = le nouveau test** dans `agents/relecture.md`. Dépend de VIT2 (même commande de mutant).
4. **VIT4 — `git cat-file --batch` dans `textes_contexte`**. Dépend de VIT1.
5. **VIT5 — Dépôt modèle copié dans `depot_matin`**. Dépend de VIT1.
6. **VIT6 — Lanceur mince + `.pyc`**. Dépend de VIT2 (risque 4.4).
7. **VIT7 — test-boucle en parallèle**. Dépend de VIT4, VIT5, VIT6 (moins de processus d'abord).
8. **VIT8 — Hooks à un seul handler**. Dépend de VIT6 ; touche `hooks.json` et `test-vlp.py`.
9. **VIT9 — Carte de symboles + socle NUI sans numéros**. Indépendante.
10. **VIT10 — `--seul` + suite complète exigée par `cocher --verifier`**. Dépend de VIT9 (noms de groupes).
11. **VIT11 — Mesure de fin** : mêmes chronos que VIT1, avant/après. Dépend de tout.

---

Coût web : **0 recherche, 3 pages lues** (env-vars, hooks, tools-reference ; extraits mot pour mot).
