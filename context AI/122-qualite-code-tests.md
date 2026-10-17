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

## Ce que je conseille (💡 proposé — rien n'est tranché ; 17 idées)

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

**C. Des tests plus rapides** (chiffres : section « Mesures de durée », en bas de cette note)

9. 💡 **Lancer les groupes de tests en parallèle**, comme `rapide` le fait déjà pour une fiche.
10. 💡 **Un dépôt Git d'essai commun**, au lieu de 41 `git init` écrits dans `test-vlp.py`, **76** lancés
    par une suite (mesuré le 2026-10-16) ; déjà dans `REF` : ≈ 18 tests posent `GIT_CONFIG_GLOBAL` à la main.
11. 💡 **Des tests « small »** (Google) : sortir du disque et des sous-processus ce qui peut l'être.
12. 🟡 **`cocher` sans la suite entière pour une fiche sans `.py`** : à trancher par l'utilisateur
    (aujourd'hui, `VIT11` l'exige toujours).
16. 🟡 **La protection de Windows, qui analyse ce qu'on lance** (demandé par l'utilisateur le
    2026-10-16 : « le firewall Windows […] analyse souvent ce que l'on fait et ça ralentit notre
    travail »). À prendre en compte au cadrage :
    - **C'est la protection en temps réel de Microsoft Defender**, pas le pare-feu (confirmé par
      l'utilisateur le 2026-10-16) : elle regarde chaque fichier ouvert et chaque programme lancé.
    - **Les mesures de la sous-session la croisent** : l'utilisateur l'avait coupée pendant la nuit du
      2026-10-15 au 16, et l'a **réactivée juste avant 00:56:37** (heure lue par `date`). Chaque durée
      reportée ici dit son état : coupée, active, ou à cheval — une mesure à cheval ne vaut pour aucun.
    - **Mesuré ensuite** (section « Mesures de durée ») : **+ 40 s (+ 13 %)** avec la protection active,
      surtout sur le groupe qui lit des fichiers ; lancer `git` presque pas ralenti (43 → 44 ms). Une
      mesure de chaque côté : un faisceau. Réduire le nombre d'appels `git` (idée 10) aide quand même :
      5 094 appels par suite.
    - **Ce que dit Microsoft** (doc officielle, lue le 2026-10-16) : le « performance mode » de Defender
      sur un **Dev Drive** reporte l'analyse après l'ouverture du fichier — **Windows 11 seulement**
      ([Protect Dev Drive using performance mode](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-endpoint-antivirus-performance-mode)) ;
      la machine est en Windows 10 (19045). Une exclusion de dossier coupe l'analyse et ouvre un trou
      de protection : à garder étroite et rare
      ([Exclusions in Microsoft Defender Antivirus](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-antivirus-exclusions-overview)).
    - ⚠️ **Un réglage de sécurité est un geste de l'utilisateur**, jamais d'une fiche : Claude ne touche
      pas aux réglages de sécurité. Une fiche peut **mesurer** (suite chronométrée, avec et sans une
      exclusion que l'utilisateur pose lui-même sur le dossier du kit), puis lui **présenter** le gain
      et le risque ; il tranche.

**D. Relecture et méthode**

13. 💡 **`vlp:relecture` regarde aussi la qualité** : test supprimé ou désactivé, fonction non
    demandée, fichier qui grossit — et seulement ce qui touche la justesse (Anthropic).
14. 💡 **Un commit de rangement, un commit de comportement** (Beck, « Tidy First ») : règle de la méthode.
15. 💡 **Le guide reste court** : ce qu'un script peut garder devient un script, pas une phrase
    (Anthropic, « over-specified CLAUDE.md »).

**E. Des données typées** (demandé par l'utilisateur le 2026-10-17)

17. 💡 **Typer les données lues avec `TypedDict` ou `dataclass`** (module standard), vérifiées par
    `pyright` : 11 `json.load(s)` dans les scripts d'exécution (`grep -n "json.load" scripts/*.py`,
    2026-10-17), un seul `@dataclass` (`scripts/mesure-tokens.py:477`). Non essayé ; aucun bug de donnée
    mal formée relevé à ce jour. **Écarté : `pydantic`** (accord de l'utilisateur le 2026-10-17) — un
    paquet à l'exécution, contraire à « zéro paquet » (`methode-chantier.md:537`). 🟡 **`NumPy`**, sa
    question : avis contre — paquet à l'exécution lui aussi, et le kit ne fait que des sommes
    (42 `sum(`, 4 `round(`, 1 `import statistics` dans les 5 scripts d'exécution, 2026-10-17).

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
dans la TODO. Retouchée le 2026-10-16 à 01:13, après les mesures : l'ajout (6) nomme `HOME` et les durées.
Sur son oui, elle remplace la ligne n° 96 de `08-etat.md` et se place juste après `ISO` (n° 137).
Copie de sauvegarde, **version d'avant la retouche** : `ref-en-attente.patch` (scratchpad de la séance d'`ISO1`, jetable).

- **Titre** : `REF` — La qualité du code et des tests : fichiers plus courts, tests rapides et bien écrits, guides et garde-fous
- **Ajouté à la fin de « Ce qu'il apporte »**, après `<br>` : **Élargi et passé en V1 le 2026-10-16, placé juste après `ISO`** (questionnaire d'`ISO1`, réponses de l'utilisateur : fondre ici le chantier « qualité du code et des tests », un seul chantier long plutôt que plusieurs). **Le constat** : la règle des 1 000 lignes (« Coder dans le kit », `MET7`) n'a aucune garde, et les fichiers ont continué de grossir — `test-vlp.py` 5 879 lignes (2026-10-01), 8 694 (2026-10-07), 10 448 (2026-10-16) ; `vlp_coeur.py` 8 446 puis 10 206 ; `pytest` n'est pas branché (`git grep -i pytest`, 2026-10-16). **Ajouts** : (4) des garde-fous par script — taille de fichier, test supprimé ou désactivé, forme des tests ; (5) un guide court des tests dans « Coder dans le kit » — un comportement par test, le test d'abord, un commit de rangement à part ; (6) des tests plus rapides — isoler `HOME` (un groupe lit les 3,1 Go de transcripts réels de l'utilisateur), groupes en parallèle, dépôt d'essai commun ; la suite dure 313 s seule, 353 s protection de Windows active (2026-10-16) ; (7) `vlp:relecture` regarde aussi la qualité ; deux questions à l'utilisateur au cadrage : brancher `pytest`, et `cocher` sans la suite entière pour une fiche sans `.py`. Mesures, 9 sources et 17 idées : `context AI/122-qualite-code-tests.md`.
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

## Mesures de durée — nuit du 2026-10-15 au 16

**Image simple** : la suite, c'est surtout **5 000 petits lancements de `git`** ; et un groupe qui relit
**tout l'historique de Claude** de l'utilisateur, 3,1 Go.

**Source** : la session « Mesurer puis accélérer la suite test-vlp.py », note `duree-test-vlp-2026-10-16.md`
(notes partagées de l'app, hors dépôt), recopiée ici. Code mesuré : commit `2b32499`. Machine : 8 cœurs,
Windows 10, Python 3.14.6. Heures lues par `date`, durées par `date +%s`.

**Commandes** : `python scripts/test-vlp.py` ; chronométré par groupe : `python <scratchpad>/chrono.py
scripts/test-vlp.py <sortie.json>`. ⚠️ `chrono.py` est jetable (scratchpad de la sous-session, pas dans le
dépôt). Sa méthode, pour le refaire : il joue `test-vlp.py` tel quel, enveloppe l'appel `f()` qui suit
`JOUES.append(f.__name__)` d'un chrono, et compte par groupe `subprocess.Popen`, appels `git`, `git init`,
`tempfile.mkdtemp`. Surcoût vérifié nul : `--seul tester_matin` 210 s puis 146 s brut, 167 s puis 167 s chronométré.

### La suite entière — chaque durée avec l'état de la protection

Protection en temps réel coupée à **00:34:08**, réactivée juste avant **00:56:37** (idée 16).

| Passage | Début → fin | Durée | Code | Protection | Charge |
|---|---|---|---|---|---|
| 1 | 23:48:35 → 23:57:39 | 544 s | 0 | active | une autre suite entière (`ISO1`) en même temps |
| 2 | 23:57:57 → 00:03:50 | 353 s | 1 | active | seule ; rouge au passage de minuit (défaut 2) |
| A, chronométré | 00:07:14 → 00:17:51 | 637 s | 0 | active | `pyright` d'une autre session dès 00:12:21 |
| 3 | 00:30:36 → 00:37:47 | 431 s | 0 | à cheval | logiciels fermés pendant le passage |
| **B, chronométré** | 00:37:57 → 00:43:10 | **313 s** | 0 | **coupée** | machine allégée — **la référence** |
| après correctif minuit | 00:52:48 → 00:58:44 | 356 s | 0 | à cheval | — |
| **C, chronométré** | 00:59:17 → 01:05:10 | **353 s** | 0 | **active** | code `f386792` : + 1 partie de 1,4 s |

➡️ Sous charge, la même suite passe de **313 à 637 s** : une mesure ne vaut que seule sur la machine.

### Ce qui coûte — passage B, 313 s

- **166 groupes** ; **5 139 sous-processus**, dont **5 094 `git`** (99 %) ; **76 `git init`** ; **281** dossiers
  temporaires. Comptes identiques aux trois passages chronométrés.
- **89 groupes appellent `git`** : **299,4 s** (96 %). Les 77 autres : 13,4 s.
- 123 groupes sous 1 s : 30,3 s à eux tous.
- `test-boucle.py` seul : **179 s** (00:03:51 → 00:06:50), sa partie `canal` 160,5 s. Lancé en fond dès le
  début (`VIT7`, `scripts/test-vlp.py:144`) : c'est le **plancher** de la suite tant qu'il dure.

| # | Groupe | B coupée | C active | (A) | `git` | `git init` | ms par `git` (B) |
|---|---|---|---|---|---|---|---|
| 1 | `tester_matin` | 95,6 s | 98,6 s | (183,1) | 2 234 | 28 | 43 |
| 2 | `tester_heures_commits` | 42,0 s | 63,1 s | (71,7) | 58 | 5 | 724 |
| 3 | `tester_ailleurs` | 10,3 s | 11,0 s | (19,4) | 256 | 4 | 40 |
| 4 | `tester_commit_au_titre` | 8,5 s | 8,2 s | (26,3) | 18 | 2 | 473 |
| 5 | `tester_carte_git` | 8,4 s | 11,2 s | (10,8) | 146 | 1 | 57 |
| 6 | `tester_arp3_marque` | 8,3 s | 7,7 s | (14,0) | 136 | 0 | 61 |
| 7 | `tester_fusionner` | 7,7 s | 8,1 s | (17,3) | 186 | 2 | 42 |
| 8 | `tester_lettres_doublon` | 7,4 s | 7,4 s | (15,8) | 160 | 2 | 46 |
| 9 | `tester_relecture` | 6,9 s | 6,4 s | (10,7) | 137 | 2 | 50 |
| 10 | `tester_courant_de` | 6,3 s | 5,1 s | (10,5) | 139 | 1 | 45 |

- Les 10 font **201,5 s des 313** (64 %).
- `tester_matin` seul fait **2 234 des 5 094** appels `git` (44 %).

### La protection de Windows — coupée ou active

- **313 → 353 s : + 40 s (+ 13 %).**
- Dont **+ 21 s** sur `tester_heures_commits` (42,0 → 63,1 s), le groupe qui **lit des fichiers** (défaut 1).
- `tester_matin` bouge à peine (95,6 → 98,6 s) : **43 → 44 ms** par appel `git`. Lancer `git` n'est
  presque pas ralenti par la protection.
- ⚠️ **Une mesure de chaque côté**, sur une machine où un même groupe varie de ± 20 % : un faisceau, pas une
  preuve. Corrige l'indice de l'idée 16 (≈ 75 ms par `git`, pris sous charge) : seule, la machine fait 43 ms.

### Deux défauts trouvés en mesurant

1. ❌ **Fuite hors du bac** : `tester_heures_commits` (`scripts/test-vlp.py:878`) lance `cout` sans isoler
   `HOME` ; `essais_hors_bac` lit alors **les vrais transcripts** de l'utilisateur (`scripts/vlp_coeur.py:655`
   puis `:657`, le `glob` de `~/.claude/projects/*/*.jsonl`) — **1 337 fichiers, 3,1 Go** (`ls … | wc -l`,
   `du -sh`, 2026-10-16).
   - Profil rejoué le 2026-10-16 à 01:10 (`python -m cProfile -s cumtime scripts/test-vlp.py --seul
     tester_heures_commits`) : **26,3 s** en tout, dont **20,6 s** dans `essais_hors_bac` (11 appels) et
     **19,2 s** dans `origine_de` (**8 523** appels). La sous-session avait lu 28,3 s et 20,9 s.
   - ➡️ La durée **grandit avec l'historique**, et le test dépend de la machine qui le joue.
   - Deux autres fonctions lisent ce dossier : `essais_de` (`vlp_coeur.py:532`) et `cmd_essai` (`:580`).
     **Non vérifié** : si des tests les appellent sans isoler `HOME`.
2. ✅ **Passage de minuit** : `test-boucle.py` relisait la date après minuit, la boucle non (passage 2, ÉCART
   « NUI4 (e) … carnet `2026-10-15.jsonl` »). Corrigé au commit `f386792`, sur la branche
   `refs/heads/claude/xenodochial-poincare-ac89b4` : le test lit sa date une fois et la passe à `boucle.py` ;
   partie `minuit` ajoutée, mutant attrapé, `test-vlp.py` vert, pyright 0 avant et après.
   - ⚠️ **Ni poussé ni fusionné** dans `main` ; fait hors du brief (mesurer, pas coder). 🟡 Fusion sur le oui
     de l'utilisateur.

### Les pistes — 💡 proposé, 🟡 à trancher

- 💡 **Piste A — isoler `HOME`** dans les tests qui lancent `cout` : retire **42 à 63 s** et la dépendance à
  la machine. C'est aussi une correction : un test ne lit pas les données de l'utilisateur.
- 💡 **Piste B — les groupes en 4 processus** : ≈ 180 s selon la sous-session, **non mesuré** ; le plancher
  est `test-boucle.py`, 179 s.
- 💡 **`tester_matin` d'abord** pour le dépôt d'essai commun (idée 10) : 44 % des appels `git`.
- 💡 **Une option `--chrono` dans `test-vlp.py`**, pour rejouer ce tableau sans le script jetable.
- 🟡 **`cocher` sans la suite entière** pour une fiche sans `.py` (idée 12).

## Les réponses du cadrage de `REF` (2026-10-17)

Page à cartes https://claude.ai/artifact/CChuXu6B6YUZqL1xCp8qRS (version 4) ; 21 réponses sur 21,
toutes égales à l'avis donné ; le découpage en 26 fiches validé tel quel (« on va partir sur ce que
tu proposes »). Le pourquoi de chaque avis : la section suivante.

| Carte | Retenu |
|---|---|
| D1 | migrer vers pytest, côte à côte, l'ancienne suite gardée jusqu'aux portes de parité |
| D2 | photographier le comportement d'abord (`syrupy` ou `pytest-regtest`, par essai) |
| D3 | l'isolation en un seul `conftest.py` (HOME, USERPROFILE, Git) ; un dépôt modèle copié |
| D4 | hooks en Python seul ; l'atelier sous `uv`, un seul `pyproject.toml`, outils d'atelier exigés |
| D5 | garder `vlp.py mutant` et `sante` ; `sante` sans `--isolated` |
| D6 | la garde de taille : 6e compte de `sante`, bloquante ; pylint après la découpe |
| D7 | `coverage` + `diff-cover`, 90 % des lignes changées ; aucun seuil global |
| D8 | toute la suite avant de cocher, toujours |
| D9 | Defender hors du chantier |
| D10 | la découpe dans `REF`, après un plan ; façade, module d'état ; les restes pendant la découpe |
| Q1 | moins de `git` d'abord, puis `pytest-xdist` sous délai de garde |
| Q2 | les tests existants en lecture seule pendant une fiche qui code, par un hook |
| Q3 | le test d'abord, vu échouer, avec la liste des tests concernés |
| Q4 | le relecteur rapporte tout, avec gravité et confiance |
| Q5 | une fiche d'essai de mutation automatique, `poodle` d'abord |
| Q6 | les consignes découpées par mode de chargement, le kit et le `CLAUDE.md` global (accord ligne à ligne) |
| Q7 | l'inventaire des règles écrites, puis leur conversion en hooks |
| Q8 | une fiche d'inventaire des erreurs ; l'utilisateur choisit ce qui entre |
| Q9 | les revues par angle, chaque défaut vérifié, deux passes vides pour finir |
| Q10 | Opus écrit, Fable relit |
| Q11 | une fiche d'essai de `TypedDict` |

## Recherche du 2026-10-17 — quatre sous-agents, au cadrage de `REF`

**Le point de départ, dit par l'utilisateur ce jour-là** : le kit sert lui seul, sur son PC
(`CLAUDE.md`, « Pour qui ») ; ni le coût ni le temps ne freinent `REF` ; zéro régression ; l'outil
éprouvé d'abord, quitte à réécrire. Quatre sous-agents Sonnet, lecture seule, sans plafond de pages :
23 + 22 + 8 + 9 recherches web, ≈ 186 pages ou fichiers bruts lus. Toutes les lectures du 2026-10-17.
Rangs : doc = doc officielle ; dépôt ; article (relu par des pairs) ; preprint ; blog ; forum.
⚠️ Les citations passent par WebFetch (petit modèle, ≈ 125 caractères) : les faits décisifs ont été
relus sur le texte brut (`curl`) ou mesurés ; les autres sont plausibles, non revérifiés.

### Versions (PyPI JSON, 2026-10-17)

| Outil | Version | Date | Licence | Chez lui |
|---|---|---|---|---|
| pytest | 9.1.1 | 2026-06-19 | MIT | **installé** |
| pytest-xdist | 3.8.0 | 2025-07-01 | MIT | non |
| coverage | 7.16.2 | 2026-09-27 | Apache-2.0 | 7.16.0 |
| diff-cover | 10.6.0 | 2026-09-22 | Apache-2.0 | non |
| syrupy | 6.1.1 | 2026-09-13 | MIT | non |
| pytest-regtest | 2.7.0 | 2026-07-09 | MIT | non |
| uv | 0.13.1 | 2026-10-14 | MIT OR Apache-2.0 | **installé** |
| ruff | 0.17.1 | 2026-10-15 | MIT | 0.16.10 |
| pyright | 1.1.414 | 2026-09-10 | MIT | 1.1.414 |
| poodle (mutation) | 1.3.4 | 2026-04-05 | MIT | non |
| cosmic-ray (mutation) | 8.7.0 | 2026-08-09 | MIT | non |
| mutmut | 3.8.0 | 2026-09-12 | BSD-3 | non — WSL seulement |

### Les tests : migrer vers pytest sans rien perdre

- **Côte à côte** : l'ancienne suite et la nouvelle tournent ensemble ; l'ancienne ne part qu'aux portes
  de parité — « a gradual process of modernization » ([Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html), blog, 2024-08-22) ;
  « 34% of the systems rely on both testing frameworks » ([Barbosa et Hora, SANER 2022](https://homepages.dcc.ufmg.br/~andrehora/pub/2022-saner-test-migration.pdf), article).
- **Portes de parité proposées** (💡 sous-agent) : manifeste `ast` des 986 `verifier("nom"…)` ; mêmes
  verdicts par groupe ; couverture ligne et branche ≥ référence ; diff de `pytest --collect-only -q`.
- **pytest ne doit jamais importer `test-vlp.py` tel quel** : ses 175 `groupe(...)` au niveau du module
  lanceraient la suite à la collecte, une fois par worker. Sous pytest, un `SystemExit` pendant un test
  n'échoue que ce test ([runner.py](https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/runner.py), dépôt) ;
  pendant la collecte, il arrête tout.
- **Photographier le comportement d'abord** (tests de caractérisation, Feathers) : `syrupy` (zéro
  dépendance hors pytest) ou `pytest-regtest` (« Changing code with no or little testing setup yet »,
  [PyPI](https://pypi.org/project/pytest-regtest/)) ; aucune source ne tranche : essayer sur 3 vraies sorties.
  Chemins temporaires et dates à filtrer avant la comparaison.
- ❌ **Windows ignore `HOME`** : « Changed in version 3.8: No longer uses `HOME` on Windows » —
  `USERPROFILE` est lu ([doc Python](https://docs.python.org/3/library/os.path.html#os.path.expanduser)) ; Git lit `HOME`
  ([doc git](https://git-scm.com/docs/git#_environment_variables)). Poser **les deux**, comme le `pytester`
  de pytest. `test-vlp.py` pose `USERPROFILE` sur 12 lignes (compté le 2026-10-17), pas dans
  `tester_heures_commits` (défaut 1 plus haut) ; `vlp_coeur.py` lit `os.path.expanduser("~")`.
- **Git** : `GIT_CONFIG_GLOBAL` (Git ≥ 2.32) remplace `$HOME/.gitconfig` ; `GIT_CONFIG_NOSYSTEM=1`.
  Mesuré chez lui (une série, Defender actif) : un `git` seul **32 ms** ; `git init` + `add` + `commit`
  **208 ms** ; `copytree` d'un dépôt modèle **25 ms** — le coût est le nombre de processus.
- ⚠️ **xdist sous Windows + Python 3.14** : blocage intermittent après la fin des tests, « ~50%
  reproduction rate on a 2000-test suite » ([issue #1313](https://github.com/pytest-dev/pytest-xdist/issues/1313), ouverte) ;
  contre-témoignage dans [#1289](https://github.com/pytest-dev/pytest-xdist/issues/1289). Délai externe et repli `-n 0`.
- **Smells** : aucun détecteur mûr en ligne de commande ; aucun plugin pour « test supprimé ou `skip`
  ajouté » — comparer `--collect-only` avant/après, `-rs`, plus ruff `PT018`, `PLR0915`, `C901` sur `tests/`.

### Les outils de qualité : garder, ajouter

- **`vlp.py mutant` : garder** — aucun outil n'exprime « ce test-là doit attraper ce mutant »
  (`--attendu`). Ce qui manque : une **campagne sur les lignes changées** — Google mute « only changed
  code during code review » ([arXiv 2102.11378](https://arxiv.org/abs/2102.11378), résumé lu). Candidats :
  `poodle` (CI Windows, Python 3.10 à 3.14, commande libre) ; `cosmic-ray` (`cr-filter-git`, mais CI
  Linux seule et pas de 3.14 déclaré). Tout `vlp_coeur.py` : ≈ 8 000 nœuds mutables, ≈ 11 jours en
  séquentiel (calcul du sous-agent, pas une mesure).
- **`vlp.py sante` : garder** — aucun standard ne le remplace ; même idée que les « bulk suppressions »
  d'ESLint ([blog](https://eslint.org/blog/2025/04/introducing-bulk-suppressions/), 2025-04-04) ; la baseline de ruff
  est une issue ouverte depuis 2022 ([#1149](https://github.com/astral-sh/ruff/issues/1149)).
- **Garde de taille** : ruff n'a pas `too-many-lines` (« not compatible with the formatter »,
  [issue 970](https://github.com/astral-sh/ruff/issues/970)) ; pylint `C0302` a un seuil fixe, sans cliquet → écrire la garde
  (un 6e compte dans `sante`), pylint après la découpe.
- **Couverture** : `coverage run --branch` avec `patch = subprocess` (7.10 et après ; `pytest-cov` 7
  a retiré les sous-processus), puis `diff-cover --fail-under` sur les lignes changées. Google :
  « per-commit coverage goals of 99% are reasonable, and 90% is a good lower threshold »
  ([blog Google](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html), 2020-08-07) ; Fowler : utile pour
  trouver le non-testé, « of little use as a numeric statement » ([bliki](https://martinfowler.com/bliki/TestCoverage.html)).
- **Hooks de commit** : `pre-commit` refuse `core.hooksPath` ; `prek` l'honore. Garder le hook maison,
  qui appelle une seule sous-commande de `vlp.py`, testable.
- **Types** : garder pyright ; `ty` est en bêta (« ty does not yet have a stable API », [README](https://github.com/astral-sh/ty)).

### L'outillage : uv à l'atelier, Python seul dans les hooks

- **Hooks** : rester sans paquet. Les plugins officiels d'Anthropic lancent `python3` sans `uv`
  ([claude-plugins-official](https://github.com/anthropics/claude-plugins-official)) ; `uv run` ajoute **+40 à +90 ms**
  par lancement (mesuré chez lui, bruit > 30 ms) ; un hook dont le lanceur ne démarre pas laisse
  l'action se faire (doc hooks), sauf `"onFailure": "block"` ; `uv` est en 0.x (cassant à chaque
  version mineure). La doc des plugins ne parle que des dépendances Node.
- **Atelier** : `uv` + un seul `pyproject.toml` (`[dependency-groups] dev`, `uv.lock`) pour ruff,
  pytest, coverage et pyright — « A "pyrightconfig.json" file always takes precedent over
  "pyproject.toml" » : migrer puis retirer le `.json`. `target-version` passe de `py39` à `py314`.
- ⚠️ **`hooks/hooks.json` lance chaque hook deux fois**, `python3` (Python 3.14.7, 136 ms) et `py -3`
  (3.14.6, 85 ms) ; `vlp_hook.py` s'en protège par un tampon. Deux Python pour un même hook.
- ⚠️ **Le piège de la découpe** : `test-vlp.py` assigne des attributs du module (`mod.TAMPON_HOOKS =
  None`…) ; une fois `vlp_coeur.py` coupé, l'assignation ne toucherait que la façade, sans erreur.
  Parade proposée : façade avec `__all__`, les globales changées par les tests dans un module d'état lu
  par `etat.NOM` ; la liste des noms publics comparée avant et après.

### Les consignes et l'IA

- **Taille** : « target under 200 lines per CLAUDE.md file. Longer files consume more context and
  reduce adherence » ([doc memory](https://code.claude.com/docs/en/memory)) ; « Keep SKILL.md under 500 lines »
  ([doc skills](https://code.claude.com/docs/en/skills)). Le `CLAUDE.md` global de l'utilisateur : **265** lignes ;
  celui du kit : 87 ; `methode-chantier.md` : 582 ; le plus long `SKILL.md` : 293 (`wc -l`, 2026-10-17).
- **Une consigne n'est pas une garantie** : « CLAUDE.md instructions which are advisory, hooks are
  deterministic » ([best practices](https://code.claude.com/docs/en/best-practices)) ; les modèles oublient en
  silence quand les règles s'empilent (IFScale, preprint 2025 : « omission errors »).
- ❌ **La carte de `/vlp:chantier` arrive coupée** : une injection garde « roughly 30,000 characters »,
  au-delà un fichier et un aperçu de 2 000 ([tools-reference](https://code.claude.com/docs/en/tools-reference)) ; la carte
  pesait **53,5 Ko** au cadrage de `REF`, reçue en aperçu (constaté dans la séance, 2026-10-17).
  Recoupe la ligne `ALC` de la TODO (n° 130).
- **Tricher aux tests est documenté** : « modifying the problematic tests themselves to match the
  code's output » (carte système de Claude 3.7, Anthropic, 2025) ; « Hiding tests from agents reduces
  cheating success rate to near zero » ([ImpossibleBench](https://arxiv.org/html/2510.20270v1), preprint) ; dire « ne
  triche pas » a eu un effet « nearly negligible » (METR, sur o3).
- **Écrire les tests** : « have one Claude write tests, then another write code to pass them »
  (best practices) ; « It's important to confirm that the tests fail before implementing the code »
  ([Willison](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/), guide) ; nuance : des consignes TDD sans
  contexte ont **augmenté** les régressions, une carte des tests concernés les a réduites (TDAD, preprint 2026).
- **Relecteur** : sur Sonnet 5, « only report high-severity issues » fait taire des bugs trouvés —
  tout rapporter avec gravité et confiance, filtrer à part (guide de prompt) ; un relecteur « will
  usually report some, even when the work is sound » : ne demander que la justesse.
- **Contradictions** : vérifier par sous-agent — conseillé par Claude Code et Fable 5, déconseillé
  par la page Opus 5 ; ton ferme — Anthropic contre, superpowers pour ; fichiers de contexte — moins de
  réussite (ETH, preprint) contre −28,64 % de temps (Lulla, preprint).

## L'inventaire des erreurs (`REF1`)

**Fait le 2026-10-17** (`Q8` : réparer toutes les erreurs connues ; l'utilisateur choisit ce qui entre).
Lu par grep et par plages, jamais un fichier de fiches entier ; chaque défaut encore cité a été
**revérifié dans le code du jour** quand une commande le permettait (colonne « Preuve », « revérifié ») ;
les autres sont cités tels que leur source les écrit. Estimations en fiches : **estimé, non mesuré**.

### Les comptes bruts, par source

| Source | Lu | Défauts gardés | Écartés |
|---|---|---:|---|
| (1) la TODO (`08-etat.md:379-399`) | 19 lignes | **10** (E1–E10) | 9 lignes sans défaut : `REF` (ce chantier), `CAR`, `DER` (une enquête), `HOR`, `EVR`, `RMS`, `SCO`, `BDD`, `BIL` — des ajouts ou des mesures |
| (2) « Restes repérés », « Hors du chantier », et les « **Laissé ouvert** » des clôtures | 1 + 7 sections, 11 lignes du journal | **6** (E11–E16) | 7 sections « Hors du chantier » : des choix de périmètre, 0 défaut neuf ; restes déjà en TODO : 2 ; réparés depuis : 6 ; autres projets ou questions ouvertes : le reste |
| (3) les audits `12` et `AVL` | 18 constats (`12`), 9 + 5 pistes (`AVL1`, `AVL2`), 33 constats (`AVL3`), 2 pannes (`AVL4`), 5 « Restent ouverts » (`AVL9`) | **7** (E17–E23) | `12` : 14 corrigés, 2 périmés, 2 vrais déjà en TODO (`VAR`, `COP`) ; `AVL3` : 28 sur 33 faits ou en TODO |
| (4) le cadrage (« Recherche du 2026-10-17 », « Deux défauts trouvés en mesurant », socle de `REF`) | 9 défauts | **6** (E24–E29) | la carte coupée fondue dans E3 ; le passage de minuit réparé (`f386792` est dans `main` : `git merge-base --is-ancestor` → 0) |
| **Total** | | **29** | |

⚠️ La source (2) déborde de la fiche : elle nommait « Restes repérés » et « Hors du chantier » ; les
« **Laissé ouvert** » des clôtures (`08-etat.md`) disent la même chose et ont donné 4 défauts sur 6.

**Réparés en route, sans carte** (vus dans le code ou le journal du jour) : `trier` lit la dépendance
de `RMS` (`est_bloque`, `scripts/vlp_coeur.py:4397-4405`) ; le prix de `claude-haiku-5-5` est dans
`scripts/mesure-tokens.py` (3 lignes) ; `evals/effort/traces/` est ignoré (`.gitignore:3`) ; `equiper`
sur un dossier absent rend une `GARDE:` (`scripts/vlp_coeur.py:1827-1829`) ; le plafond qui comptait
le rejeu et la voie gardée après un conflit (`GAI1`, `08-etat.md:3551`) ; `oter` et la ligne de `TAB`
(`clore` retire la ligne depuis `RTO`) ; le passage de minuit. Les consignes globales `A4`, `A5`, `C1`
d'`AVL3` : faites dans le `CLAUDE.md` global (lu le 2026-10-17).

### La liste

| N° | Défaut | Preuve | Effet | Fiches | Recoupe `REF` |
|---|---|---|---|---|---|
| E1 | `VCL` — des tours qui disparaissent du compte : 14 tours · 1,91 $ de `TAB` comptés nulle part ; le coût d'`AMD` qui baisse (43,20 → 37,80 $) ; `cout` ne range pas les tentatives d'une fiche refusée ; `recompter --ecrire` laisse la page d'un clos à moitié juste | `08-etat.md:382` ; `ENA5` 3,25 → 7,64 $ depuis `CPF` pour ≈ 20,94 $ réels (`08-etat.md:3564`) | le coût par fiche d'un clos est faux, le total juste | ≈ 4 (TODO) | aucune |
| E2 | `VAR` — `${CLAUDE_PLUGIN_ROOT}` en clair dans `cloture.md`, lu par `vlp.py lire`, où rien ne le remplace | revérifié : `vlp.py lire cloture.md` en porte **5** lignes | un modèle qui recopie la ligne lance `/scripts/vlp.py` ; aucun raté vu | 1 | aucune |
| E3 | `ALC` + la carte coupée — la carte de `/vlp:chantier` passe la limite d'une injection (≈ 30 000 caractères) : reçue en aperçu | 53,5 Ko au cadrage de `REF` (« Les consignes et l'IA ») ; la TODO en fait 68 % (`118-audit-du-kit.md`, `AVL3`) | le cadrage décide sur une carte coupée | 1 | **`REF2`** |
| E4 | `EFC` — `/vlp:tache` doit annoncer l'effort tiré de la méthode, qu'il lui est interdit d'ouvrir | `AVL3` `A2` ; revérifié : `EFFORT=` dans `scripts/vlp_coeur.py` → **0** | l'effort annoncé se devine | 1 | aucune |
| E5 | `LIR` — `clore` ne dit pas quels fichiers relire avant de republier la feuille | 10 refus sur 50 à `APR` (`08-etat.md:388`) | une publication refusée, puis rejouée | 1 | aucune |
| E6 | `COP` — un nombre recopié dans plusieurs commandes sans test qui compare les copies (« deux tentatives » ×6, « trois majuscules » ×3) | `AVL3` `A10` ; revérifié : aucun test ne compare ces copies | une copie diverge en silence ; la règle 3 n'est pas tenue | 1 | aucune |
| E7 | `HER` — **déjà réparé par `ISO2`**, la ligne de TODO est restée | `chantiers_ailleurs` (`scripts/vlp_coeur.py:6965-6982`), docstring « ISO2, TODO 140 » ; `08-etat.md:3510` ; ⚠️ le cas exact d'`ENA5` n'est pas rejoué | une ligne morte, injectée à chaque cadrage | 0 | — |
| E8 | `ATT` — `mutant --attendu` ne reconnaît l'attendu qu'en début de libellé : `MUTANT VIVANT` pour un mutant attrapé | deux fois de suite, clôture d'`ENA` (`08-etat.md:391`) | un verdict de mutant à l'envers | 1 | aucune |
| E9 | `CAN`, points (4) à (8) — deux canaux d'une nuit prennent le même numéro (`113-rto.md`, `113-ctr.md`) ; une `(visuel)` jouée avant l'arrêt ; l'archive sans liens ; le résumé des clos perdu à la fusion (2 fois) ; une branche republie la feuille sans les clos de `main` | `08-etat.md:397` ; `61b2300` | des pages fausses après une nuit à deux canaux | ≈ 3 à 4 sur les 6 à 7 de `CAN` | aucune |
| E10 | `SOL` — un bloc Tentatives soldé garde le motif d'avant ; une tête hors gabarit se récrit | rejoué par sonde le 2026-10-13 (`08-etat.md:398`) ; jamais vu sur une vraie fiche | le chef compare un refus au mauvais motif | 1 | aucune |
| E11 | `git` absent des `allowed-tools` d'`/vlp:enchainer`, quand le chef commite en worktree (`ISO6`) | revérifié : `skills/enchainer/SKILL.md:4` ; reste d'`ENA5` (`119-ena.md:405`) ; ⚠️ qui lance `git` là : non vérifié | une demande de permission par `git`, hors mode auto | ½ | aucune |
| E12 | `commiter` compte `scripts/sante-base.json` parmi les communs de tout projet | `119-ena.md:407` ; 💡 changé par une autre fiche, il partirait dans le mauvais commit (déduit, non vu) | un commit de fiche qui emporte un fichier d'une autre | ½ | aucune |
| E13 | `relecture --retirer` en parallèle effacerait les copies de l'autre relecteur | dit par un relecteur d'`ISO`, non vérifié (`08-etat.md:3546`, (3)) | un relecteur sans ses copies, un refus faux | 1 | aucune |
| E14 | `vlp.py mutant` rend `MUTANT PLANTÉ` sur un juge sans `ÉCART:` | `08-etat.md:3546`, (4) ; non revérifié | un verdict de mutant faux | ½ | aucune |
| E15 | une même séance, trois chiffres : `clore` du bac « non mesuré », `vlp.py cout` 3,20 $, `mesure-tokens.py --actif` 3,42 $ | `08-etat.md:3554`, (2) et (3) ; cause non vérifiée | deux outils du kit ne s'accordent pas sur un coût | 1 | aucune |
| E16 | `clore` du kit sort `GARDE: pas ISO (kit)` : la page d'enchaînement n'est pas refaite | `08-etat.md:3554`, (4) ; non revérifié | la page d'enchaînement en retard après une clôture | ½ | aucune |
| E17 | la docstring de `vlp.py`, où `CLAUDE.md` envoie lire les sous-commandes, pèse **62 851** octets (54 523 à `AVL1`) ; `--help` rend **7** lignes | revérifié (`ast`, `--help`) ; `AVL1`, piste 5 | lire une sous-commande coûte toute la docstring, ou un grep | 1 | `REF7`, `REF16` (en partie) |
| E18 | une séance de nuit charge le `CLAUDE.md` global, qui commite après chaque tâche, et `nuit.md`, qui l'interdit (`nuit.md:19`) | `AVL3` `A11` ; `nuit.md` ne nomme pas le global (grep : 0) ; ⚠️ ce qui arrête un commit de nuit : non lu | un commit hors de la boucle, possible | 1 | `REF16`, `REF17` (en partie) |
| E19 | le repli « copie simple » dans `~/.claude/commands/` survit au chantier `K` | `AVL3` `B11` ; revérifié : 4 lignes (`skills/chantier/SKILL.md:183,185`, `skills/check/SKILL.md:107`, `skills/init/SKILL.md:50`) ; le kit sert son auteur seul, en plugin (`CLAUDE.md`, « Pour qui ») | du texte mort, payé à chaque lancement | 0 (sans fiche) | `REF25` |
| E20 | comparer à la page en ligne avant de republier une feuille : `comparer` existe, aucune commande ne le cite | `AVL3` `C2`, raté de peu à `VOI6` ; revérifié : 0 citation dans `skills/*/SKILL.md`, `cloture.md`, `ARTEFACTS.md` | une feuille republiée efface ce qu'une autre branche y a mis (recoupe E9) | ½ | aucune |
| E21 | une définition d'agent changée n'est pas vue par la séance ouverte ; rien n'avertit | `AVL3` `C4`, raté à `FOR` ; revérifié : aucune alerte dans `scripts/vlp_coeur.py` ; noté « après · 1 » à `AVL8`, jamais versé | une mesure faite sur l'ancien agent | 1 | aucune |
| E22 | `sante --base` dans un worktree en retard sur `main` recale la base sur un autre état | `AVL3` `C7` ; remis à la main deux fois (`AVL1`, `AVL2`) | le cliquet juge contre une base fausse | ½ | aucune |
| E23 | une séance CLI de plus de 30 jours est effacée (`cleanupPeriodDays`) : le recompte d'un vieux clos la perd sans le dire | `118-audit-du-kit.md:1328-1329` (doc lue le 2026-10-11) | un recompte qui baisse en silence (recoupe E1) | 1 | aucune |
| E24 | un test lit les vrais transcripts : `tester_heures_commits` n'isole ni `HOME` ni `USERPROFILE` | 1 337 fichiers, 3,1 Go ; 20,6 s sur 26,3 s du test (« Deux défauts trouvés en mesurant ») | test lent, lié à la machine, qui lit des données privées | — | **`REF4`** |
| E25 | chaque hook se lance deux fois, `python3` (3.14.7) puis `py -3` (3.14.6) ; le tampon de `vlp_hook.py` évite le double effet | « L'outillage » ci-dessus ; **gardé exprès** à `VIT8` (`08-etat.md:2643`) | deux Python pour un hook, ≈ 85 ms de plus par entrée | 0 | aucune (`REF10` en tient compte) |
| E26 | le piège de l'état global : `test-vlp.py` change des attributs du module (`mod.TAMPON_HOOKS = None`…) ; coupé, `vlp_coeur.py` ne verrait plus l'assignation, sans erreur | « L'outillage » ci-dessus | des tests verts qui ne testent plus rien, après la découpe | — | **`REF18`** |
| E27 | `.githooks/pre-commit` saute `pyright` s'il manque, et le commit passe | revérifié : `.githooks/pre-commit:27` | la règle « pyright avant le commit » n'est pas garantie | ½ | `REF3` (en partie : la règle, pas le hook) |
| E28 | le cliquet de `sante.py` lance ruff `--isolated` : il ne lit pas `pyproject.toml` | revérifié : `scripts/sante.py:252` | le cliquet ne juge pas aux règles du dépôt | — | **`REF3`** |
| E29 | aucune garde de taille de fichier : `test-vlp.py` 5 879 → 10 448 lignes (2026-10-01 → 2026-10-16) | la ligne `REF` de la TODO (`08-etat.md:381`) | les fichiers grossissent sans frein | — | **`REF9`** |

**La page à cartes** : une carte par défaut, trois réponses (« dans `REF` », « garder en TODO »,
« abandonné ») ; les réponses s'écrivent ici, puis les fiches neuves se placent après `REF3`.

### Les réponses (2026-10-17)

Page https://claude.ai/artifact/5L3gARLfctW9wELerNyP1A (version 1) ; 29 réponses sur 29, collées dans
la séance ; **27 égales à l'avis donné**, deux écarts : `Q20` (E20, `comparer`) « dans `REF` » au lieu de
« garder en TODO » ; `Q25` (E25, deux Python) « garder en TODO » au lieu d'« abandonné ».

| Réponse | Défauts | Ce qui suit |
|---|---|---|
| dans `REF` (22) | E2–E6, E8, E10–E14, E16–E20, E22, E24, E26–E29 | 15 défauts en 13 fiches neuves, `REF27` à `REF39`, après `REF3` ; E27 ajouté à `REF3` ; E3, E24, E26, E28, E29 déjà couverts (`REF2`, `REF4`, `REF18`, `REF3`, `REF9`) ; ⚠️ E14 trouvé réparé après la page (`1c9a4a0`, `verdict_juge`) : pas de fiche |
| garder en TODO (6) | E1, E9, E15, E21, E23, E25 | E1 (`VCL`) et E9 (`CAN`) : rien ne change ; E15 et E23 joints à `VCL`, E21 et E25 en lignes neuves : **en attente du 2e oui** (ci-dessous) |
| abandonné (1) | E7 | la ligne `HER` (n° 140) retirée par `vlp.py oter` |

| Fiche | Défauts |
|---|---|
| `REF27` | E2 (`VAR`) |
| `REF28` | E4 (`EFC`) |
| `REF29` | E5 (`LIR`), E20 |
| `REF30` | E6 (`COP`) |
| `REF31` | E8 (`ATT`) |
| `REF32` | E10 (`SOL`) |
| `REF33` | E11, E12 |
| `REF34` | E13 |
| `REF35` | E16 — le symptôme réparé à la main (`cfa68e4`), la cause reste |
| `REF36` | E17 |
| `REF37` | E18 |
| `REF38` | E19 — la carte disait « sans fiche » : une fiche de rangement, la plus courte, le garde tracé |
| `REF39` | E22 |

**À la clôture de `REF`**, retirer de la TODO les lignes couvertes : `VAR` (128), `ALC` (130), `EFC`
(131), `LIR` (132), `COP` (133), `SOL` (138), `ATT` (141).

**Versés le 2026-10-17, sur le 2e oui de l'utilisateur** (`methode-chantier.md`, « La TODO ne grossit
pas ») — TODO n° 114 (`VCL`, points 7 et 8 ; score 15 → 10, rangée après `HOR`), 144 (`AGT`), 145 (`PYU`) :

- **`VCL` (n° 114), point (7)** : une même séance, trois chiffres — `clore` du bac « non mesuré »,
  `vlp.py cout` 3,20 $, `mesure-tokens.py --actif` 3,42 $ (clôture de `GAI`, 2026-10-17) ; cause non
  vérifiée (E15). Coût : ≈ +1 fiche (estimé, non mesuré).
- **`VCL`, point (8)** : les vieilles séances CLI effacées — une séance de ligne de commande de plus de
  30 jours disparaît (`cleanupPeriodDays`, doc lue le 2026-10-11) ; le recompte d'un vieux clos la perd
  sans le dire ; remède : une `GARDE:` quand une séance citée manque (`AVL9`, Q33 ; E23). Coût : ≈ +1 fiche
  (estimé, non mesuré).
- **Ligne neuve `AGT` — Une définition d'agent changée, la séance avertit** : après une retouche
  d'`agents/`, la séance ouverte garde l'ancienne définition (raté à `FOR`) ; la carte avertirait quand
  `agents/` a changé depuis le début de la séance ; testé (`AVL3` `C4`, noté « après · 1 » à `AVL8` ; E21).
  **après · score 5 (1 × 5)** · 1 fiche · ≈ 4,40 $ (estimé, non mesuré) · dépend de : —.
- **Ligne neuve `PYU` — Chaque hook lancé par un seul Python** : chaque entrée de `hooks/hooks.json`
  part deux fois, `python3` puis `py -3` ; le tampon de `vlp_hook.py` évite le double effet ; gardé exprès
  à `VIT8` (la doc des hooks n'avait pas de forme à un seul lancement sans shell) ; ≈ 85 ms de plus par
  entrée (E25). Ce qu'elle ferait : relire la doc des hooks du jour ; une forme à un seul lancement, on
  la prend, testée ; sinon la ligne se retire. **après · score 5 (1 × 5)** · 1 fiche · ≈ 4,40 $ (estimé,
  non mesuré) · dépend de : —.

## Les nombres recopiés (`REF30`)

**Relevé le 2026-10-17** (défaut `E6`, ligne `COP` de la TODO), par grep dans `skills/`, `agents/`,
`methode-chantier.md`, `enchainement.md`, `cloture.md`, `nuit.md` et `CHANTIER.md`. **5 nombres,
12 copies.** Le test `tester_nombres_recopies` (`scripts/test-vlp.py`, table `NOMBRES_RECOPIES`) les
compare : une ligne `ÉCART:` par copie qui diffère de sa source, ou dont le motif ne se retrouve plus.

| Nombre | Source | Copies |
|---|---|---|
| deux tentatives, puis `BLOQUÉE` | `methode-chantier.md`, « Ce que `/vlp:tache` garantit » | `skills/tache/SKILL.md` ; `agents/fiche.md` ; `enchainement.md` ; `tache-blocage.md` ×2 (titre, commentaire de tête) ; `methode-chantier.md`, table des sources — **6** |
| trois majuscules d'un préfixe | `methode-chantier.md`, « Trois lettres, depuis le 2026-09-17 » | `CHANTIER.md` ; `skills/chantier/SKILL.md` — **2** |
| cinq lignes : une fiche plus courte arrête | `skills/tache/SKILL.md`, « Gardes » | `skills/jouer/SKILL.md` ; `skills/enchainer/SKILL.md` (prompt du sous-agent) — **2** |
| deux tours pour un questionnaire | `methode-chantier.md`, « Les règles qui valent partout » | `skills/tache/references/tache-contraintes.md` — **1** |
| 5 fiches par lancement d'`enchainer` | `skills/enchainer/SKILL.md`, « Plafond » | `skills/enchainer/references/refus.md` — **1** |

Écartés : les seuils de `vlp.py` (page, fiche, socle) — les commandes y renvoient sans recopier ;
« 5 refus » (`methode-chantier.md`) et « 10 refus » (`cloture.md`) — des faits datés, pas des règles ;
« trois à cinq lignes » du bloc Tentatives — une seule occurrence.
