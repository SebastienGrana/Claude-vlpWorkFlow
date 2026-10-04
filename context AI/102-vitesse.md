> **QUAND LIRE** : on joue une fiche `VIT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache VIT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier VIT — Aller plus vite sans coder moins bien

**Ouvert.** le 2026-10-03.

**À quoi il sert.** Coder plus vite et mieux (le mot de l'utilisateur, 2026-10-03). Une fiche attend ses tests : un
mutant rejoue toute la suite (médiane 602 s, A1) et `test-vlp.py` passe 86 % de son temps à lancer des processus
(105,7 s sur 123,2 s, A2). VIT raccourcit l'attente sans retirer un contrôle, et laisse le code qu'il touche sain,
maintenable et documenté. Ensuite : la méthode du kit, puis la TODO re-cadrée (n° 99), avant de reprendre NUI.

**Fait.** `VIT1`, la base (2026-10-04). Plan revu après elle (entrée du même jour dans `08-etat.md`) : `VIT4` retirée,
son numéro non repris ; `VIT14` ajoutée après `VIT2`, puis retirée le même jour (non reproduite, 0 échec sur 24
paires ; choix de l'utilisateur), son numéro non repris. Critères de code sain au socle (2026-10-04) ; `VIT15`, leur cliquet,
ajoutée avant `VIT2`, faite le 2026-10-04 ; `VIT16`, qui verrouille ses gains à chaque fiche, ajoutée après elle (choix de
l'utilisateur, page « Choix de VIT15 », Q1). NUI en pause, reprise à `NUI28` après VIT et la méthode (n° 99).

**Session** : bf7412ea-120b-47fa-933e-6b54b408b2f4

## Le socle commun

**D'où il vient.** Deux audits indépendants (A1, A2) et leur synthèse croisée, le 2026-10-03. La synthèse est
versionnée : `context AI/103-audit-vitesse.md`. A1 et A2, restés dans le scratchpad de la session bf7412ea,
**disparaîtront** — leurs chiffres utiles sont recopiés ici, avec leur source.
Décisions : https://claude.ai/artifact/3maXrvHBKj85QYybrnPubx. Chaque fiche remesure ce dont elle dépend, avant/après.
**La base** : l'entrée « VIT1 — la base » de `context AI/08-etat.md` (2026-10-04) — l'« avant » d'un critère s'y lit.

**Les décisions de l'utilisateur** (2026-10-03) — la page, Q1 à Q9 :
- Q1 VIT **avant** la fin de NUI. Q2 mutant arrêté sur **le test attendu** (`--attendu`), pas sur le premier écart.
- Q3 `vlp.py` devient un **lanceur mince** : il garde son nom et sa ligne de commande, son code va dans un module voisin
  mis en cache (`.pyc`). Q4 relecteur : AVANT ne joue **que le nouveau test**, APRÈS reste complet.
- Q5 **pas de cache** de résultats de tests (faux vert). Q6 `boucle.py` appelle `vlp` **dans son processus**.
- Q7 hooks : **un seul Python**, choisi à l'installation. Q8 plafond Bash (10 min) **inchangé**.
- Q9 plugins sans rapport : **l'utilisateur** les désactive lui-même, après la mesure de `VIT1`.
- Puis, au questionnaire : un code **sain, maintenable, documenté**, exigé ici plutôt qu'en fiches de plus ; après
  VIT, la méthode du kit puis la TODO (n° 99) ; un chantier plus gros accepté, pourvu qu'il avance.
- Puis, page des critères (2026-10-04, https://claude.ai/artifact/LbQN638o6ZZFk6jC1t1uz7) : D1 et D2 gardées ;
  Q1 le cliquet, Q2 la docstring de toute fonction touchée, Q3 ruff, Q4 les tests sans longueur ni docstring,
  Q5 la synthèse versionnée, Q6 les dossiers `vlp-carte-*` en TODO.

**Les invariants — aucune fiche ne les casse.**
- **Aucun contrôle retiré** : les `verifier(` de `test-vlp.py` et de `test-boucle.py` (en occurrences :
  `grep -o "verifier(" <fichier> | wc -l`) ne baissent jamais ; comptés avant et après, comptes bruts au critère.
- **Une suite complète, verte, avant chaque commit** ; `VIT11` la fait exiger par script.
- **Stdlib seule**, Python 3 ; les scripts restent lançables par `py -3` et `python3`, Windows, Linux et macOS.
- **Les sorties ne changent pas**, hors ce que la fiche ajoute : une commande imprime au caractère près ce qu'elle
  imprimait.
- Un gain se **mesure** avant/après, par la même commande, comptes bruts ; un gain estimé se dit estimé.
- **Code sain, maintenable, documenté** : chaque fiche laisse le code qu'elle touche plus propre qu'elle ne l'a
  trouvé. Les critères, comptés avant/après sur les fonctions touchées, comptes bruts au critère :
  - **Les seuils** — ceux de ruff par défaut : complexité 10, branches 12, arguments 5, instructions 50, blocs
    imbriqués 5.
  - **Le cliquet** — une fonction neuve passe les cinq seuils ; une vieille fonction touchée n'empire sur aucun
    compte (« empirer » : la docstring de `scripts/sante.py`). Les fonctions déjà au-dessus (56 sur 474 hors tests,
    ruff sur `74550d4`) attendent `REF` (n° 96).
  - **La docstring** — toute fonction neuve ou touchée a la sienne : au moins une phrase à l'impératif, en
    français, finie par un point (PEP 257).
  - **Les tests** (`test-*.py`) — mêmes seuils, sauf les instructions et la docstring : un long scénario reste
    permis, le nom `tester_…` sert d'étiquette.
  - **L'outil** — `vlp.py sante` (`VIT15`) : ruff s'il est présent, sinon un compte `ast` de la bibliothèque
    standard — égal à ruff sur tout le kit, mais dit « estimé ». La suite joue `vlp.py sante --cliquet` ;
    `vlp.py sante --base` verrouille un gain.
- Jusqu'à `VIT2` livrée, le mutant se joue à l'ancienne (`vlp.py mutant` mute le vrai fichier ~10 min : ni suite ni
  édition pendant ce temps) ; après, par `--attendu`. « Mutant attrapé », dans un critère, vise la forme du moment.

**Où vit quoi** (des noms, pas des numéros de ligne : ils dérivent à chaque commit).

| Symbole | Fichier | Ce qu'il fait |
|---|---|---|
| `cmd_mutant` | `scripts/vlp.py` | casse un fichier en place, joue la suite avec `VLP_TOUS_ECARTS=1`, rend le fichier |
| `sante.principal` | `scripts/sante.py` | les cinq comptes, la base `scripts/sante-base.json` et le cliquet ; chargé par `vlp.py sante` |
| `PAR_ARGUMENTS`, `options_<commande>` | `scripts/vlp.py` | la répartition et les options, hors de `main` et `repartir` — au-dessus des seuils : une sous-commande neuve passe par eux |
| `KIT_EXCLUS` | `scripts/vlp.py` | ce qu'une copie du kit laisse de côté |
| `textes_contexte` | `scripts/vlp.py` | lit les `.md` du contexte ; avec `rev`, un `git show` par fichier |
| `premier_lancement` | `scripts/vlp.py` | le tampon qui empêche un hook d'agir deux fois |
| `verifier`, `appel`, `ECARTS` | `scripts/test-vlp.py` | un contrôle ; `vlp` appelé dans le processus ; les écarts |
| `tester_boucle` | `scripts/test-vlp.py` | lance `test-boucle.py` en série — lui ignore `VLP_TOUS_ECARTS` (synthèse) |
| `vlp`, `kit` | `scripts/boucle.py` | `vlp.py` en sous-processus ; `vlp.py` chargé comme module |
| hooks | `hooks/hooks.json` | 7 entrées, chacune en `python3` puis en `py` |
| relecteur | `agents/relecture.md` | rejoue AVANT, APRÈS, puis le mutant |

**Ce qu'on ne fait pas ici.** Découper le cœur en plusieurs modules (après VIT : la méthode, n° 99, puis `REF`, n° 96) ;
un cache de résultats (Q5) ; changer le plafond Bash (Q8) ; toucher aux réglages de l'utilisateur (Defender, fichier
d'échange, plugins : Q9).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `VIT1` | Mesurer la base | rien |
| `VIT15` | Le cliquet du code sain : ruff s'il est là, sinon un compte maison | `VIT1` |
| `VIT16` | `/vlp:tache` verrouille les gains : `sante --base` à chaque fiche | `VIT15` |
| `VIT2` | Muter une copie du kit, arrêté sur le test attendu | `VIT1` |
| `VIT3` | Lire les fichiers d'un commit en un seul appel Git | `VIT1` |
| `VIT5` | Faire de `vlp.py` un lanceur mince | `VIT2` |
| `VIT6` | Appeler `vlp` dans le processus de `boucle.py` | `VIT5` |
| `VIT7` | Lancer `test-boucle` en parallèle de `test-vlp` | `VIT3`, `VIT6` |
| `VIT8` | Un seul Python dans les hooks | `VIT5` |
| `VIT9` | Une carte des symboles, et des fiches sans numéros de ligne | rien |
| `VIT10` | Ranger les tests en groupes nommés, et n'en jouer qu'un | `VIT9` |
| `VIT11` | La suite complète exigée au commit | `VIT10` |
| `VIT12` | Le relecteur ne rejoue que le nouveau test dans AVANT | `VIT2`, `VIT10` |
| `VIT13` | Mesurer la fin, avant/après | `VIT7`, `VIT8`, `VIT11`, `VIT12` — et, par elles, toutes |

Jouées dans l'ordre du fichier — `VIT15` puis `VIT16` avant `VIT2`, `VIT4` et `VIT14` retirées —, les dépendances tiennent. `VIT5` à `VIT8` touchent le démarrage des scripts, `VIT10`
et `VIT11` tout `test-vlp.py` : une à la fois.

---

<!-- FICHE:VIT1 -->
## VIT1 [x] — Mesurer la base

**Session** : 460c9244-0d39-4a2e-9804-ea49b5ad1cb0
**Dépend de** : rien.
**Fichiers** : `context AI/08-etat.md` (une entrée datée) — et rien d'autre ; aucun script modifié.

**Prompt**
Mesure, sur l'état de `main`, ce que `VIT13` comparera : chaque commande recopiée telle quelle dans l'entrée, pour
être rejouée à l'identique. Rien d'autre ne tourne pendant une mesure de durée.
1. Les suites : `test-vlp.py` entier, puis `test-boucle.py` seul, en alternance, deux fois chacun ; début et fin par
   `date`, jamais estimés. La part de `test-vlp` sans `test-boucle` ne se mesure pas ici : une soustraction se dit
   « estimée, bruitée ».
2. Le mutant de `NUI27`, à l'ancienne : durée, seul en machine (il mute le vrai `vlp.py`).
3. Les lancements : `py -3 scripts/vlp.py lignes CHANTIER.md` et `py -3 -c pass`, 20 fois chacun, médiane et max.
4. Le contexte de départ d'une fiche : le premier tour d'une session `/vlp:tache` récente, par `mesure-tokens.py`.
5. Les `verifier(` des deux fichiers de tests, en occurrences (l'invariant du socle).
6. La charge pendant les mesures : processus `claude` et `python`, mémoire réservée (`Win32_OperatingSystem`).
Écris le tout en une entrée datée du fichier d'état, titre « VIT1 — la base », une ligne par mesure.

**Critère de fin**
L'entrée existe, six lignes, chacune avec sa commande et ses comptes bruts ; aucune estimation sans le mot « estimé ».
<!-- /FICHE -->

---

<!-- FICHE:VIT15 -->
## VIT15 [x] — Le cliquet du code sain : ruff s'il est là, sinon un compte maison

**Session** : 460c9244-0d39-4a2e-9804-ea49b5ad1cb0
**Dépend de** : `VIT1`.
**Fichiers** : `scripts/vlp.py` (une sous-commande `sante`), `scripts/test-vlp.py`, et la base du cliquet (un
fichier de données versionné, nommé au compte rendu).

**Prompt**
Le socle fixe les critères de code sain (seuils de ruff, cliquet, docstring, tests) ; rien ne les compte encore. Choix
de l'utilisateur (page des critères, Q3 ruff, puis « R a », 2026-10-04) : **ruff s'il est présent, sinon un compte
maison**. ruff 0.16.10 est installé chez lui ; ailleurs dans le groupe, il peut manquer.
1. `vlp.py sante [<fichiers>]` rend, fonction par fonction, les cinq comptes du socle et la présence d'une docstring.
   ruff trouvé (`ruff`, ou `py -3 -m ruff`) : ses comptes, par sa sortie JSON ; absent : un compte par `ast`, et une
   ligne qui dit « sans ruff, comptes estimés ». Les scripts restent stdlib seule : ruff est appelé, jamais importé.
2. `--base` écrit la base, fonction par fonction ; `--cliquet` compare à elle et sort 1 si une vieille fonction
   empire, si une fonction neuve passe un seuil, ou si une fonction neuve ou touchée n'a pas de docstring — les tests
   (`test-*.py`) sans les instructions ni la docstring. Dis comment tu suis une fonction touchée, renommée ou déplacée.
3. `test-vlp.py` joue `--cliquet` sur le kit : un compte qui empire fait tomber la suite.
4. Les tests ne dépendent pas de ruff : le chemin `ast` est testé partout ; le chemin ruff, sur une sortie JSON
   enregistrée, et en vrai seulement s'il est installé.

**Critère de fin**
1. `vlp.py sante` sur le kit, avec et sans ruff : comptes bruts, et les écarts entre les deux nommés.
2. `py -3 scripts/test-vlp.py` → `OK` ; `verifier(` avant ≤ après ; mutant attrapé (une fonction qui empire passe le
   cliquet) ; pyright 0 ; les critères de code sain du socle, sur `sante` elle-même.
<!-- /FICHE -->

---

<!-- FICHE:VIT16 -->
## VIT16 [x] — `/vlp:tache` verrouille les gains : `sante --base` à chaque fiche

**Session** : e0f4a0ef-3594-4d44-bf7c-cb752cb41675
**Dépend de** : `VIT15`.
**Fichiers** : `skills/tache/SKILL.md` (l'étape 6 bis), `agents/fiche.md` (l'étape qui coche), `scripts/sante.py`,
`scripts/vlp.py` (`options_sante`, la docstring de `sante`), `scripts/test-vlp.py`.

**Prompt**
Sans `--base`, une fonction qui a maigri peut regrossir jusqu'à son ancien compte sans alerte. Choix de l'utilisateur
(page « Choix de VIT15 », Q1 « tache », 2026-10-04) : **`/vlp:tache` reprend la base à son étape 6 bis, à chaque
fiche**. Deux pièges, lus dans `sante.principal` et `sante.poser_base` :
- `sante` vise le kit par défaut (`--racine`) : lancé depuis un autre projet, `--base` réécrirait la base du kit ;
- `--base` crée une base là où il n'y en a pas : un projet équipé sans cliquet en recevrait une.
1. `--si-base`, avec `--base` : sans base sous la racine, une ligne `SANS BASE`, sort 0, rien d'écrit ; avec une base,
   comme `--base`. L'option passe par `options_sante` (le cliquet : `main` et `repartir` n'empirent pas).
2. L'étape 6 bis gagne une ligne, `sante --base --si-base --racine .`, avant `cocher` : une `GARDE:` (la base se
   relâcherait, donc une fonction empire) arrête l'étape, rien de coché ni de commité. Court : tout ajout dans une
   commande se paye à chaque exécution.
3. Le chemin `agents` (`agents/fiche.md`) : la même ligne là où il coche, ou dis pourquoi non.
4. Mesure la durée de la ligne sur le kit, avec et sans ruff (médiane de 5) : le prix payé à chaque fiche.

**Critère de fin**
1. Cas : racine sans base, `--si-base` → `SANS BASE`, sort 0, aucun fichier créé ; racine du kit → `BASE …`, sort 0 ;
   lancé hors du kit avec `--racine .` → la base du kit identique à l'octet (sha1 avant = après).
2. `py -3 scripts/test-vlp.py` → `OK` ; `verifier(` avant ≤ après ; mutant attrapé (`--si-base` ignoré : une base
   créée) ; pyright 0 ; les critères de code sain du socle, mesurés ; la durée de la ligne, comptes bruts.
<!-- /FICHE -->

---

<!-- FICHE:VIT2 -->
## VIT2 [x] — Muter une copie du kit, arrêté sur le test attendu

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `methode-chantier.md` (le paragraphe du mutant).

**Prompt**
`cmd_mutant` mute le vrai fichier le temps de toute la suite (médiane 602 s, A1) : toute session qui charge le plugin
tourne mutée, et un `.pyc` validé par la date à la seconde et la taille peut servir le mauvais code (synthèse).
1. Copie le kit dans un dossier temporaire (`KIT_EXCLUS` dit quoi laisser), mute la copie, joue la suite de la copie.
   Le vrai fichier n'est jamais écrit : son empreinte avant = après. D'abord, la suite verte dans la copie non mutée ;
   un test qui lit le dépôt Git du kit : dis lequel, et comment tu le traites.
2. `--attendu "<début du libellé>"` : la sortie se lit ligne à ligne ; dès que cet écart tombe, l'arbre de processus
   est tué (`test-boucle.py` compris) → `MUTANT ATTRAPÉ`. La suite finit sans lui → `MUTANT VIVANT pour <libellé>`,
   sort 1, avec les écarts vus. `test-boucle.py` sort au premier écart, `VLP_TOUS_ECARTS` ou non.
   La suite s'arrête sans cet écart, en erreur → `MUTANT PLANTÉ`, sort 1, avec ses dernières lignes ; jamais
   `ATTRAPÉ` sur un arrêt, même après un autre écart (vu à `VIT1` : un `ÉCART`, puis une suite arrêtée à 11 s au lieu
   de ~600, a rendu `MUTANT ATTRAPÉ 1 écart(s)`, `scripts/vlp.py:7731-7733`).
3. `--tous`, ou aucune des deux options : l'ancien comportement (tous les écarts), dans la copie — les appels déjà
   écrits marchent ; un arrêt en erreur s'y dit aussi `MUTANT PLANTÉ`.
4. Dans `test-vlp.py`, l'appel `tester_boucle()` passe en dernier : un écart de `test-vlp` tombe alors avant
   `test-boucle`, les trois quarts de la suite (`VIT1`). Le test de `NUI27` venait après cet appel : `--attendu` seul
   n'y aurait rien gagné. Mêmes contrôles ; seul l'ordre des lignes de sortie change.
Le paragraphe du mutant dans `methode-chantier.md` : `--attendu` devient la forme par défaut.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK`. Cas : vrai fichier inchangé (sha1) pendant et après ; `--attendu` juste →
   `MUTANT ATTRAPÉ` ; `--attendu` d'un test qui ne tombe pas → `MUTANT VIVANT pour …`, sort 1 ; une suite qui
   s'arrête en erreur après un autre écart → `MUTANT PLANTÉ`, sort 1.
2. Le mutant de `NUI27` rejoué avec `--attendu` : durée avant (`VIT1`) / après, comptes bruts.
3. pyright 0 ; `verifier(` avant ≤ après ; les critères de code sain du socle, mesurés.
<!-- /FICHE -->

---

<!-- FICHE:VIT3 -->
## VIT3 [x] — Lire les fichiers d'un commit en un seul appel Git

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`.

**Prompt**
`textes_contexte` avec `rev` lance un `git show` par fichier `.md` : 986 appels, 32,1 s des 123,2 s de `test-vlp.py`
hors `test-boucle` ; `vlp.py ouverts . --rev HEAD` prend 3 727 ms contre 356 ms sans `--rev` (A2). Lis-les en un seul
`git cat-file --batch` : une entrée par fichier, le contenu lu à la taille annoncée. Même résultat au caractère près,
fichier absent compris.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK` ; un test compare l'ancien et le nouveau lecteur sur un dépôt à 3 fichiers.
2. `vlp.py ouverts . --rev HEAD` : durée avant/après, 5 essais, médiane.
3. Mutant attrapé (une entrée décalée) ; pyright 0 ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT5 -->
## VIT5 [x] — Faire de `vlp.py` un lanceur mince

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT2`.
**Fichiers** : `scripts/vlp.py`, un module voisin (nom à choisir, dit dans le compte rendu), `scripts/test-vlp.py`,
`scripts/boucle.py` (son `kit()`), `CLAUDE.md` (règle 4 : où vit la mécanique).

**Prompt**
Lancé en script, `vlp.py` est recompilé à chaque fois (la compilation seule : 183 ms, A1) ; importé, son `.pyc` sert —
A2 estime le gain à ~240 ms par lancement (462 → 226 ms). `scripts/vlp.py` garde son nom, sa ligne de commande et sa
docstring (la doc des sous-commandes) ; tout son code passe dans le module voisin, qu'il importe et lance. Les
`mod.X = …` des tests visent le module qui porte `X`. Si `PYTHONDONTWRITEBYTECODE` empêche le `.pyc` :
`sys.dont_write_bytecode = False` avant l'import (A1 : −26 % sur un cas de nuit, 8,9 → 6,6 s, une seule mesure). Le
`.pyc` se valide par la date à la seconde et la taille (synthèse) : la copie de `VIT2` en écarte le mutant ; dis si un
autre cas reste. `${CLAUDE_PLUGIN_ROOT}` et les chemins des hooks ne changent pas.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK`, `verifier(` même compte.
2. `py -3 scripts/vlp.py lignes CHANTIER.md` : médiane de 20 lancements avant (`VIT1`) / après.
3. Mutant attrapé sur le module ; pyright 0 sur les fichiers touchés ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT6 -->
## VIT6 [x] — Appeler `vlp` dans le processus de `boucle.py`

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT5`.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py`.

**Prompt**
`boucle.py` lance `vlp.py` en sous-processus à chaque geste (sa fonction `vlp`), alors qu'il le charge déjà comme
module (`kit()`). Appelle `main` du module avec une sortie capturée et le dossier voulu, au lieu d'un sous-processus.
Garde le même `(code, sortie)`. Les variables d'environnement et le dossier courant d'un appel ne doivent pas fuir sur
le suivant ; garde 1 ou 2 vrais sous-processus testés (synthèse). `faux-claude.py` simule `claude` : lui garde ses
sous-processus. Avant d'écrire, vérifie que `main` est réentrant (état global, `sys.exit`) ; s'il ne l'est pas, dis
où et arrête-toi (`RETOUR`). A1 estime le gain à −35 à −45 % de `test-boucle`.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` → `OK`, durée avant/après ; `verifier(` même compte.
2. Mutant attrapé (la sortie capturée tronquée) ; pyright 0 ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT7 -->
## VIT7 [x] — Lancer `test-boucle` en parallèle de `test-vlp`

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT3`, `VIT6`.
**Fichiers** : `scripts/test-vlp.py`.

**Prompt**
`tester_boucle` attend `test-boucle.py` en série, au milieu de la suite. Lance-le au **début** (`subprocess.Popen`),
joue le reste, récolte-le à la fin : même contrôle, même message d'écart. L'arrêt au premier écart (sans
`VLP_TOUS_ECARTS`) tue le processus lancé. La mémoire réservée était à 84 % le 2026-10-03 (A1, A2 ; WinError 1455
déjà vu) : mesure le pic, et garde une variable pour revenir en série.

**Critère de fin**
`py -3 scripts/test-vlp.py` → `OK` ; durée avant/après, 2 essais ; un écart forcé dans `test-boucle` sort toujours
son `ÉCART:` ; pyright 0 ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT8 -->
## VIT8 [x] — Un seul Python dans les hooks

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT5`.
**Fichiers** : `hooks/hooks.json`, `scripts/test-vlp.py` (il compte les entrées exactes de `hooks.json`),
`skills/init/SKILL.md` si l'installation choisit l'interprète.

**Prompt**
Chaque hook est écrit en `python3` puis en `py` : là où les deux existent, chaque appel d'outil lance deux `vlp.py`
(« All matching hooks run in parallel », https://code.claude.com/docs/en/hooks, lu le 2026-10-03 : CPU et mémoire,
pas d'attente). `hooks.json` est dans le plugin, partagé par toutes les machines : il ne peut pas porter un choix
propre à une machine. Trouve une forme à **un seul lancement** qui marche partout, sans `sh` (chantiers G, X, Y) ;
décision de l'utilisateur : choisie à l'installation. Si aucune forme ne tient sans fichier propre à la machine dans
le kit, arrête-toi (`RETOUR`) avec les options et leur prix.

**Critère de fin**
`py -3 scripts/test-vlp.py` → `OK` ; un appel d'outil ne lance plus qu'un `vlp.py` par hook (compté) ; pyright 0.
<!-- /FICHE -->

---

<!-- FICHE:VIT9 -->
## VIT9 [x] — Une carte des symboles, et des fiches sans numéros de ligne

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `methode-chantier.md` (« Anatomie d'une fiche »),
`context AI/101-chef-de-nuit.md` (socle et fiches restantes de NUI).

**Prompt**
Les fiches citent des lignes, et le code bouge : 7 renvois sur 7 périmés dans NUI (synthèse) ; `101-chef-de-nuit.md`
porte 105 renvois `vlp.py:<n>`, tout `context AI/` 366 (comptés le 2026-10-03) ; son socle met `cmd_mutant` à 5569,
il est à 7687. `vlp.py symboles <fichier> [<nom>…]` : par `pyclbr` (bibliothèque standard ; il donne `lineno` et
`end_lineno`, vu sous Python 3.14.6), une ligne `nom début-fin` par fonction ou classe de premier niveau ; avec des
noms, leurs seules lignes — `vlp.py` en a 332, la liste entière ne se lit pas. `methode-chantier.md` : une fiche cite
un **nom**, jamais une ligne. Réécris en noms les renvois `vlp.py:<n>` du socle et des fiches non cochées de NUI.

**Critère de fin**
`py -3 scripts/test-vlp.py` → `OK` (un test sur un fichier à 3 fonctions) ; plus aucun `vlp.py:<chiffre>` dans le
socle et les fiches non cochées de NUI (`grep -o … | wc -l`) ; mutant attrapé ; pyright 0 ; les critères de code
sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT10 -->
## VIT10 [x] — Ranger les tests en groupes nommés, et n'en jouer qu'un

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT9`.
**Fichiers** : `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
`test-vlp.py` est un script plat : 41 blocs `with` nus au niveau du module (A2) ; on ne peut pas jouer un seul groupe,
et pyright y touche déjà son seuil « too complex to analyze » (vu sur `NUI2`). Passe chaque bloc dans une fonction
`tester_*` nommée, appelée à la même place, sans changer ce qu'il vérifie ; un nom réutilisé d'un bloc à l'autre (le
`t` d'un dossier temporaire) casse en silence : relis chaque déplacement. Puis `--seul <motif>` (ou `VLP_SEUL`) : ne
joue que les groupes dont le nom ou un libellé porte le motif (295 libellés portent un code de fiche, A2) ; sans lui,
tout.

**Critère de fin**
`py -3 scripts/test-vlp.py` → `OK`, `verifier(` même compte ; `--seul NUI27` → ses contrôles seuls, durée ; mutant
attrapé ; pyright 0 ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT11 -->
## VIT11 [x] — La suite complète exigée au commit

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
**Dépend de** : `VIT10`.
**Fichiers** : `scripts/test-vlp.py`, `scripts/vlp.py`, `skills/tache/SKILL.md` (une ligne).

**Prompt**
Avec `--seul`, on itère vite ; le commit, lui, exige la suite entière. Verte et complète, la suite écrit l'empreinte du
kit qu'elle a jouée (hors Git, `KIT_EXCLUS` laissé de côté) ; dans le kit seulement (un projet équipé a ses propres
tests), le commit d'une fiche refuse si l'empreinte du kit courant n'y est pas. Où refuser — `cocher`, ou le contrôle
avant commit du chantier `VAL` : choisis, et dis pourquoi. Ce n'est pas un cache (Q5) : l'empreinte n'évite aucun
test, elle prouve que la suite entière a tourné sur ce code-là. `/vlp:tache` le dit en une ligne.

**Critère de fin**
`py -3 scripts/test-vlp.py` → `OK` ; une modification non jouée → refus ; après une suite verte → accepté ; mutant
attrapé ; pyright 0 ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT12 -->
## VIT12 [ ] — Le relecteur ne rejoue que le nouveau test dans AVANT

**Dépend de** : `VIT2`, `VIT10`.
**Fichiers** : `agents/relecture.md`, `enchainement.md` si le contrat le cite — et rien d'autre.

**Prompt**
AVANT a été vert au commit précédent : y rejouer la suite entière ne prouve rien de neuf. Dans AVANT, le relecteur
joue **le seul test que la fiche ajoute**, par `--seul` (`VIT10`) : il doit y sortir en écart ; dans APRÈS, la suite
**entière**, puis le mutant par `vlp.py mutant --attendu` (`VIT2`) au lieu d'un `Edit` à la main. Ne change rien
d'autre au contrat.

**Critère de fin**
`agents/relecture.md` dit les trois étapes ainsi ; `py -3 scripts/test-vlp.py` → `OK` (les tests qui lisent
`relecture.md`) ; `valider` sur le fichier de fiches courant sans écart.
<!-- /FICHE -->

---

<!-- FICHE:VIT13 -->
## VIT13 [ ] — Mesurer la fin, avant/après

**Dépend de** : `VIT7`, `VIT8`, `VIT11`, `VIT12` — et, par elles, toutes les autres.
**Fichiers** : `context AI/08-etat.md` (une entrée datée) — et rien d'autre.

**Prompt**
Rejoue les six mesures de `VIT1`, par les mêmes commandes, recopiées depuis son entrée. Une table : mesure, avant,
après, écart en %. Ajoute les critères de code sain, avant/après, et la durée des fiches de VIT de commit à commit, à
côté de celle des dernières fiches de NUI : un repère, pas une preuve (le travail diffère). Le contexte de départ
dépend aussi des plugins chargés (Q9) : dis lesquels l'étaient de chaque côté, et ne prête pas au code ce qui revient
à leur retrait. Dis ce qui n'a pas gagné, et pourquoi si on le sait.

**Critère de fin**
L'entrée « VIT13 — avant/après » existe : six lignes, les critères et la durée des fiches, comptes bruts des deux côtés.
<!-- /FICHE -->
