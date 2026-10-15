> **QUAND LIRE** : on cadre le chantier « qualité du code et des tests du kit » — tests plus rapides,
> tests bien écrits, guides de bonne pratique et garde-fous dans le kit — ou on cherche d'où vient une
> de ses idées. Rassemblé le 2026-10-15 et le 2026-10-16, pendant `ISO1`, à la demande de l'utilisateur.

# La qualité du code et des tests du kit — ce qu'on a trouvé, avant le cadrage

## Ce que veut l'utilisateur (ses mots, 2026-10-15)

- Si les tests sont mal écrits, rien ne garantit que le code soit bon.
- `ruff` (et `pytest`, qu'il croyait branché) n'ont pas suffi : le bot a produit des fichiers géants
  qui testent tout d'un bloc.
- Il veut des guides de bonne pratique **dans le kit**, inspirés de ce que font les autres, et
  « implémenter tout ce qui est possible en vue de faire du bon travail ».
- **Un seul chantier, hors `ISO`**, qui réunit : la vitesse des tests, des tests bien écrits, les guides.
  Il préfère un chantier long à plusieurs.
- Il l'a demandé en **V1** de la TODO, et dans la page d'enchaînement (`context AI/ordre.md`).

## Ce qui est mesuré dans le kit

| Fait | Compte brut | Commande, date |
|---|---|---|
| `scripts/test-vlp.py` | **10 448** lignes | `wc -l scripts/*.py`, 2026-10-16 |
| `scripts/vlp_coeur.py` | **10 206** lignes | idem |
| `scripts/test-boucle.py`, `boucle.py`, `mesure-tokens.py` | 1 845, 1 485, 814 | idem |
| Vérifications dans `test-vlp.py` | 960 `verifier(` | `grep -o 'verifier(' \| wc -l`, 2026-10-15 |
| Programmes lancés à part | 60 `subprocess.run/Popen/check_output` | idem |
| Dépôts Git créés | 41 `git init` | idem |
| Dossiers temporaires | 175 `TemporaryDirectory`/`mkdtemp` | idem |
| Tests lancés en parallèle | **0** (aucun `ThreadPool`, `multiprocessing`, `concurrent`) | `grep`, idem |
| `pytest` | **absent** du code du kit : ni `pyproject.toml`, ni `scripts/` ; seulement dans `exemples/fichier-de-fiches-cairn.md` | `git grep -i pytest`, 2026-10-16 |

**La règle existe, rien ne la garde.** `methode-chantier.md`, « Coder dans le kit » (`MET7`, 2026-10-07),
dit déjà : un fichier de plus de 1 000 lignes ne grossit plus — et « Aucun script ne le garde encore ».
Les fichiers ont continué de grossir :

| Fichier | 2026-10-01 | 2026-10-07 | 2026-10-16 |
|---|---|---|---|
| `test-vlp.py` | 5 879 | 8 694 | **10 448** |
| `vlp_coeur.py` | (`vlp.py` 6 631) | 8 446 | **10 206** |

Sources des deux premières colonnes : la ligne `REF` de la TODO (`08-etat.md`, n° 96).
➡️ Une règle écrite sans garde-fou mécanique n'a pas tenu. C'est le cœur du chantier.

**Ce que voient les outils d'aujourd'hui** :

- `ruff` (réglé par `pyproject.toml`, `MET5`) et le cliquet de `sante.py` jugent **chaque fonction** :
  style, complexité. Aucun ne voit la **taille d'un fichier** ni la **façon d'écrire un test**.
- ⚠️ Le cliquet lance ruff `--isolated` : il ne voit pas `pyproject.toml` (connu, `MET5`, renvoyé à `REF`).
- `cocher` exige la suite entière verte le jour même (`VIT11`), même pour une fiche sans code (`ISO1`
  n'a touché que deux `.md`). `vlp.py rapide <fiche>` lance déjà en parallèle les seuls groupes d'une fiche.

## Ce que font les autres — les sources

Recherche du 2026-10-15 : 9 recherches réussies, 2 échouées ; 2 pages lues par extraits complets,
2 fichiers lus par extraits.

1. **Anthropic, doc officielle** — [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices.md),
   lue le 2026-10-15 :
   - « Give Claude a way to verify its work » : un contrôle que Claude lance lui-même, qui rend
     réussite ou échec. Quatre niveaux de rigueur : dans le prompt, `/goal`, un **hook `Stop`** qui
     empêche de finir tant que le contrôle échoue, ou une **relecture par un sous-agent neuf**.
   - « Add an adversarial review step » : un relecteur qui ne voit que le diff ; lui dire de ne
     signaler que ce qui touche la justesse, sinon il pousse à la sur-ingénierie.
   - « The over-specified CLAUDE.md » : trop long, la moitié est ignorée ; ce que Claude fait déjà
     bien se retire, ou devient un hook.
2. **Google, « Software Engineering at Google », ch. 12 « Unit Testing »** —
   [abseil.io](https://abseil.io/resources/swe-book/html/ch12.html), lu le 2026-10-15 :
   - « Each test should cover only a single behavior » ; un « and » dans le nom d'un test signale
     souvent deux comportements.
   - Pas de logique dans un test : du code en ligne droite, juste à la lecture.
   - « DAMP, Not DRY » : un peu de répétition est permise si le test devient plus clair.
   - Les tests « small » : un seul processus, sans attente ni disque ni réseau — rapides et sûrs.
3. **Kent Beck, « Augmented Coding: Beyond the Vibes »** (25 juin 2025) —
   [newsletter.kentbeck.com](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) :
   - Trois alertes avec une IA : les boucles, les fonctions non demandées, la triche (tests
     désactivés ou supprimés).
   - Ses consignes : un test à la fois ; juste assez de code pour le faire passer ; ranger seulement
     quand tout est vert ; **jamais un rangement et un changement de comportement dans le même commit** ;
     tous les tests à chaque fois, sauf les longs ; des petits commits fréquents.
4. **`obra/superpowers`**, plugin Claude Code, licence MIT —
   [skill `test-driven-development`](https://github.com/obra/superpowers) (lue le 2026-10-15) :
   - le test d'abord, vu rouge, puis le code minimal ; du code écrit avant son test est effacé ;
   - un test : un comportement, un nom clair, du vrai code (pas de faux objets sans nécessité) ;
   - une liste des « rationalisations » qui font sauter la règle, réfutées une à une.
5. **pytest, doc officielle** — [Good Integration Practices](https://docs.pytest.org/goodpractices.html) :
   un dossier `tests/` à côté du code, des fichiers `test_*.py` ; un fichier de test par module est
   une **convention** d'équipe, pas une règle de pytest.
6. **pylint** — `max-module-lines`, défaut **1000**, message C0302 `too-many-lines`
   ([source de `format.py`, miroir 2024](https://decoder-genetics.wustl.edu/software/conda/lib/python3.1/site-packages/pylint/checkers/format.py) ;
   version actuelle non revérifiée).
7. **Les hooks de qualité**, blogs (rang : communauté) : un hook `PostToolUse` sur `Write|Edit` lance
   le linter, un hook `Stop` lance les tests. Le blocage par `Stop` est confirmé par la doc officielle (point 1).
8. **Les « test smells »** (Meszaros, « xUnit Test Patterns », 2007, cité de seconde main) : *Eager
   Test* (un test qui vérifie trop), *Assertion Roulette* (beaucoup d'assertions sans message), *Slow
   Tests*, *Conditional Test Logic*.
9. 🟡 **Taille de fichier et IA** : un faisceau d'indices (LoCoBench-Agent, arXiv 2511.13998 ; un fil
   NVIDIA), **aucune étude** qui mesure l'effet de la taille seule. Le seuil de 1 000 reste une convention.

## Ce que je conseille (💡 proposé — rien n'est tranché)

**A. Garde-fous mécaniques — le plus important** (la leçon : une règle sans script n'a pas tenu)

1. 💡 **Une garde de taille** : un fichier Python au-dessus de 1 000 lignes ne grossit plus, un
   nouveau reste dessous. Quelques lignes de script, zéro paquet ; branchée au cliquet `sante` ou
   au commit. Déjà prévue par `REF` (fiche 3 du re-cadrage `MET10`).
2. 💡 **Le cliquet voit `pyproject.toml`** : retirer `--isolated`, ou passer le réglage (dette `MET5`).
3. 💡 **Un hook ou une garde qui repère un test supprimé ou désactivé** dans un diff (alerte de Beck).
4. 💡 **Une garde de forme des tests** : nombre de `verifier` par fonction de test, longueur d'un test,
   logique (`if`, `for`) dans un test — seuils à fixer au cadrage.

**B. Des tests bien écrits**

5. 💡 **Un guide court des tests**, dans `methode-chantier.md`, « Coder dans le kit » (pas un fichier
   de plus) : un comportement par test, un nom qui le dit, pas de logique, un message clair à l'échec,
   un fichier de test par module.
6. 💡 **Le test d'abord** dans les fiches qui codent : le critère de fin dit « test écrit, vu échouer,
   puis passer » (superpowers, Beck).
7. 💡 **Découper `test-vlp.py`** en un fichier par module testé, au rythme de la découpe de
   `vlp_coeur.py` (plan de `REF`).
8. 🟡 **Brancher `pytest`** comme outil d'atelier (permis s'il est optionnel avec un repli, règle du
   2026-10-05) : il apporte la découverte des tests, le parallèle (`pytest-xdist`), les marqueurs
   « lent ». Coût : migrer 960 vérifications, ou faire tourner les deux côte à côte. À trancher.

**C. Des tests plus rapides** (chiffres à venir de la session « Mesurer puis accélérer la suite
test-vlp.py », lancée le 2026-10-15)

9. 💡 **Lancer les groupes de tests en parallèle**, comme `rapide` le fait déjà pour une fiche.
10. 💡 **Un dépôt Git d'essai commun**, au lieu de 41 `git init` (déjà dans `REF` : ≈ 18 tests posent
    `GIT_CONFIG_GLOBAL` à la main).
11. 💡 **Des tests « small »** (Google) : sortir du disque et des sous-processus ce qui peut l'être.
12. 🟡 **`cocher` sans la suite entière pour une fiche sans `.py`** : à trancher par l'utilisateur
    (aujourd'hui, `VIT11` l'exige toujours).

**D. Relecture et méthode**

13. 💡 **`vlp:relecture` regarde aussi la qualité** : test supprimé ou désactivé, fonction non
    demandée, fichier qui grossit — et seulement ce qui touche la justesse (Anthropic).
14. 💡 **Un commit de rangement, un commit de comportement** (Beck, « Tidy First ») : règle de la méthode.
15. 💡 **Le guide reste court** : ce qu'un script peut garder devient un script, pas une phrase
    (Anthropic, « over-specified CLAUDE.md »).

## Ce qui existe déjà — à ne pas refaire

- **`REF`** (TODO n° 96, V2, score 3) : la découpe de `vlp_coeur.py`, `boucle.py` et des tests, la garde
  de taille, le renommage des fichiers à tiret, les 33 `if a.cmd ==` en `set_defaults`, les 211
  remarques de ruff, le cliquet `--isolated`, l'outil commun des dépôts Git d'essai.
  ➡️ Le nouveau chantier **la recouvre** : la fondre dedans, ou l'élargir, est une réponse de la TODO
  (« fondre dans une entrée existante qu'on nomme », `methode-chantier.md`, « La TODO ne grossit pas »).
- **« Coder dans le kit »** (`methode-chantier.md:514`) : style ruff, 1 000 lignes, PEP 8, argparse,
  prose courte. Rien sur **la façon d'écrire un test**, ni sur le test d'abord.
- **`vlp.py rapide`** (`VIT23`) : les groupes d'une fiche, en parallèle.
- **`sante`** : le cliquet par fonction.

## Pièges connus pour le cadrage

- ⚠️ **`ISO` est ouvert dans le dossier principal** : `/vlp:chantier` y passe en « reprendre », il n'ouvre
  pas un second chantier. Le nouveau se cadre **dans un worktree**, ou après `ISO`.
- ⚠️ **Deux suites entières en même temps faussent les durées** (vu le 2026-10-15 : 23:43 et 23:48).
  Une mesure se fait seule sur la machine.
- ⚠️ La TODO ne grossit pas sans **deux oui** : l'idée, puis la ligne écrite relue.
- ⚠️ `test-vlp.py` est au seuil de complexité de pyright : un `verifier` ajouté au niveau du module
  le casse (mémoire `NUI2`) ; découper les tests aide aussi là.

## La ligne de TODO proposée — en attente du 2e oui

Premier oui donné le 2026-10-16 (questionnaire d'`ISO1`) : **fondre dans `REF`**, en V1, **juste après `ISO`**.
La ligne ci-dessous est écrite, **pas encore relue ni confirmée** par l'utilisateur : elle n'est **pas**
dans la TODO. Sur son oui, elle remplace la ligne n° 96 de `08-etat.md` et se place juste après `ISO` (n° 137).
Copie de sauvegarde : `ref-en-attente.patch` (scratchpad de la séance d'`ISO1`, jetable).

- **Titre** : `REF` — La qualité du code et des tests : fichiers plus courts, tests rapides et bien écrits, guides et garde-fous
- **Ajouté à la fin de « Ce qu'il apporte »**, après `<br>` : **Élargi et passé en V1 le 2026-10-16, placé juste après `ISO`** (questionnaire d'`ISO1`, réponses de l'utilisateur : fondre ici le chantier « qualité du code et des tests », un seul chantier long plutôt que plusieurs). **Le constat** : la règle des 1 000 lignes (« Coder dans le kit », `MET7`) n'a aucune garde, et les fichiers ont continué de grossir — `test-vlp.py` 5 879 lignes (2026-10-01), 8 694 (2026-10-07), 10 448 (2026-10-16) ; `vlp_coeur.py` 8 446 puis 10 206 ; `pytest` n'est pas branché (`git grep -i pytest`, 2026-10-16). **Ajouts** : (4) des garde-fous par script — taille de fichier, test supprimé ou désactivé, forme des tests ; (5) un guide court des tests dans « Coder dans le kit » — un comportement par test, le test d'abord, un commit de rangement à part ; (6) des tests plus rapides — groupes en parallèle, dépôt d'essai commun, durées mesurées par la session « Mesurer puis accélérer la suite test-vlp.py » ; (7) `vlp:relecture` regarde aussi la qualité ; deux questions à l'utilisateur au cadrage : brancher `pytest`, et `cocher` sans la suite entière pour une fiche sans `.py`. Mesures, 9 sources et 15 idées : `context AI/122-qualite-code-tests.md`.
- **Coût estimé** (remplace la case) : **V1 · score 5 (5 × 1)** · élargi le 2026-10-16, estimé en séance sans mesure : 11 à 17 fiches, ≈ 40 à 62 $ au prix par fiche du re-cadrage `MET10` (22 à 33 $ pour 6 à 9 fiches) ; le refactoring, chiffré par son bilan → 17 fiches en tout
- **Dépend de** : `ISO`

**Dans `context AI/ordre.md`**, sur le même oui :

- au chemin conseillé, juste après la ligne `SEL`, deux pas du projet `kit` : `ISO`, note « en cours depuis
  le 2026-10-15 », puis `REF`, note « juste après `ISO` (2026-10-16) » ;
- aux décisions, après « L'estimé d'un cadrage se double » : « **`REF` élargi, en V1, juste après `ISO`** :
  la qualité du code et des tests y est fondue, un seul chantier long (questionnaire d'`ISO1`, 2026-10-16). »

⚠️ Le score 5 est bas (facilité 1 au-delà de 8 fiches) ; la place voulue par l'utilisateur prime
(`methode-chantier.md`, « L'ordre »). Vérifié avant de le mettre à l'abri : `vlp.py trier .` lisait
`REF` « dépendance non close : `ISO` », `vlp.py ordre` rendait 23 pas, code 0.

## Mesures de durée — à venir

La session « Mesurer puis accélérer la suite test-vlp.py » (2026-10-15) mesure la durée totale et par
groupe, seule sur la machine, en trois passages. Ses chiffres s'ajoutent ici, avec leur commande.
