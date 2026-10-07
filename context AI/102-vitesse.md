> **QUAND LIRE** : on joue une fiche `VIT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache VIT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier VIT — Coder plus vite et mieux

**Ouvert.** le 2026-10-03.

**À quoi il sert.** Coder plus vite et mieux (le mot de l'utilisateur, 2026-10-03). Une fiche attend ses tests : un
mutant rejoue toute la suite (médiane 602 s, A1) et `test-vlp.py` passe 86 % de son temps à lancer des processus
(105,7 s sur 123,2 s, A2). VIT raccourcit l'attente sans retirer un contrôle, et laisse le code qu'il touche sain,
maintenable et documenté. Ensuite : la méthode du kit, puis la TODO re-cadrée (n° 99), avant de reprendre NUI.

**CLOS** le 2026-10-07. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** VIT1..VIT25 (2026-10-07) : coder plus vite et mieux : suite 553 → 180 s, mutant 538 → 6 s, test-boucle 426,5 → 176 s, lancement 362 → 208 ms (mesurés à VIT13, repris par VIT18) ; cliquet du code sain, sante --base à chaque fiche, contrôle rapide avant la suite, mutant visé sur son groupe, carte des symboles, py -3 dans les commandes ; xhigh pour les fiches de code (VIT25, tranché le 2026-10-07) — estimé non noté · cadré 23 · joué 23 fiches 322,08 $ (242,53 $ avant les essais hors bac, recomptés par `MET2` le 2026-10-07).

**Session** : bf7412ea-120b-47fa-933e-6b54b408b2f4

**Session** : 8a6e5503-99d5-4490-b4c1-1e8a52e5efda

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
  L'effort du modèle passe à **Max** après `VIT13` (`b31bbe9`, dit par l'utilisateur) : les tours et le $ des fiches
  suivantes se lisent à côté de ce changement.
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
- Le mutant se joue par `vlp.py mutant --attendu` (`VIT2`) : sans `--test`, il ne joue que les groupes qui portent
  ce libellé, et la suite entière s'ils ne l'attrapent pas (`VIT21`) ; `--test` garde le dernier mot. « Mutant
  attrapé », dans un critère, vise cette forme.

**Où vit quoi** (des noms, pas des numéros de ligne : ils dérivent à chaque commit).

| Symbole | Fichier | Ce qu'il fait |
|---|---|---|
| `cmd_mutant` | `scripts/vlp_coeur.py` | mute une copie du kit, y joue les tests — avec `--attendu`, arrêtés sur cet écart ; le vrai fichier n'est jamais écrit |
| `sante.principal` | `scripts/sante.py` | les cinq comptes, la base `scripts/sante-base.json` et le cliquet ; chargé par `vlp.py sante` |
| `PAR_ARGUMENTS`, `options_<commande>` | `scripts/vlp_coeur.py` | la répartition et les options, hors de `main` et `repartir` — au-dessus des seuils : une sous-commande neuve passe par eux |
| `KIT_EXCLUS` | `scripts/vlp_coeur.py` | ce qu'une copie du kit laisse de côté |
| `textes_contexte` | `scripts/vlp_coeur.py` | lit les `.md` du contexte ; avec `rev`, un `git show` par fichier |
| `premier_lancement` | `scripts/vlp_coeur.py` | le tampon qui empêche un hook d'agir deux fois |
| `decouper`, `plages` | `scripts/vlp_coeur.py` | la plage d'une fiche, du commit d'avant au sien — celle de `cout` |
| `points`, `temps`, `tape` | `scripts/mesure-tokens.py` | la ligne de temps d'une session, son temps actif, l'attente de l'utilisateur (`--actif`) |
| `verifier`, `appel`, `ECARTS` | `scripts/test-vlp.py` | un contrôle ; `vlp` appelé dans le processus ; les écarts |
| `groupe`, `tester_*` | `scripts/test-vlp.py` | un groupe de contrôles nommé ; `--seul <motif>` n'en joue que certains (`VIT10`) |
| `tester_boucle` | `scripts/test-vlp.py` | récolte `test-boucle.py`, lancé en parallèle dès le début (`VIT7`) — lui ignore `VLP_TOUS_ECARTS` (synthèse) |
| `vlp`, `kit` | `scripts/boucle.py` | `vlp.py` appelé dans le processus (`VIT6`) ; `vlp_coeur.py` chargé comme module |
| hooks | `hooks/hooks.json` | 8 entrées, chacune en `python3` puis en `py -3` (`VIT8`) |
| relecteur | `agents/relecture.md` | rejoue le nouveau test dans AVANT, la suite dans APRÈS, puis le mutant (`VIT12`) |

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
| `VIT17` | Le compteur d'une fiche : où passe son temps | `VIT13` |
| `VIT18` | Le rapport : ce que VIT a gagné, et les pistes pour gagner plus | `VIT17` |
| `VIT19` | Le contrôle avant commit ne laisse plus passer | rien |
| `VIT20` | La carte avertit d'une session qui a déjà joué une fiche | rien |
| `VIT21` | Le mutant visé sur son groupe, par défaut | rien |
| `VIT22` | Raccourcir `test-boucle` | rien |
| `VIT23` | Un contrôle rapide avant la suite entière | `VIT21` |
| `VIT24` | `test-mesure-tokens.py` dans la suite, `py -3` dans les commandes | rien |
| `VIT25` | Mesurer l'effort du modèle sur 3 fiches | `VIT19` à `VIT24` |

Jouées dans l'ordre du fichier — `VIT15` puis `VIT16` avant `VIT2`, `VIT4` et `VIT14` retirées —, les dépendances tiennent. `VIT5` à `VIT8` touchent le démarrage des scripts, `VIT10`
et `VIT11` tout `test-vlp.py` : une à la fois. `VIT17` et `VIT18`, ajoutées après `VIT13`, ouvrent la suite de VIT.
`VIT19` à `VIT25` viennent des cartes de `VIT18` (entrée « Les réponses aux cartes de VIT18 et de MET », 2026-10-05),
dans l'ordre choisi par l'utilisateur : d'abord celles qui servent aux fiches suivantes, la mesure de l'effort en
dernier. `VIT19` à `VIT24` touchent toutes `test-vlp.py` : une à la fois.

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
## VIT12 [x] — Le relecteur ne rejoue que le nouveau test dans AVANT

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
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
## VIT13 [x] — Mesurer la fin, avant/après

**Session** : 72db946f-cd44-4a3b-8ec4-39b6d2872e1d
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

---

<!-- FICHE:VIT17 -->
## VIT17 [x] — Le compteur d'une fiche : où passe son temps

**Session** : f7fe9ffa-fa40-4dc6-86ff-f51b00a9eec5
**Dépend de** : `VIT13`.
**Fichiers** : `scripts/mesure-tokens.py`, `scripts/vlp_coeur.py`, `scripts/vlp.py` (sa docstring),
`scripts/test-vlp.py`, `context AI/08-etat.md` (une entrée datée).

**Prompt**
Pour accélérer le travail d'un LLM, il faut savoir où passe le temps d'une fiche : à produire, à attendre un outil, à
attendre l'utilisateur. `VIT13` a chronométré des commandes, pas une fiche ; le chantier « méthode » (n° 99) aura
besoin de ces mesures. `vlp.py compteur <fichier de fiches> [<fiche>…]` : une ligne par fiche, sur la plage de `cout`
(`decouper`), puis `TOTAL` :
- la durée de commit à commit, et le temps actif de `--actif` découpé en **modèle**, **outils**, **attente**, **autre** :
  chaque écart entre deux lignes voisines va à la sorte de la ligne qui le ferme — une ligne assistant ; un
  `tool_result` ou une `task-notification` (tâche de fond) ; un message tapé ou la réponse d'un `AskUserQuestion` ; le
  reste. Les quatre font l'actif ;
- le temps d'outil par sorte, appels comptés : suite entière, suite `--seul`, `test-boucle`, mutant, pyright, Git,
  publication, le reste ;
- tours et $, ceux de `cout` ; les garde-fous lus dans les sorties : suites vertes sur jouées, `ÉCART:`,
  `MUTANT ATTRAPÉ`, `GARDE:`, verdict du relecteur — un tiret s'il n'y en a pas.
Déjà publié : la télémétrie officielle (OpenTelemetry, `duration_ms` par outil, code.claude.com/docs/en/monitoring-usage,
lu le 2026-10-04) — écartée : elle ne voit que l'avenir et demande un collecteur. On reste dans `mesure-tokens.py`,
stdlib seule ; la même page prévient que le format des transcriptions est interne et change d'une version à l'autre :
un champ absent se dit, jamais en silence. Joue le compteur sur VIT et NUI (`101-chef-de-nuit.md`) ; la plage de
`VIT17` porte aussi le cadrage qui l'a ajoutée (le biais de la TODO n° 103 `PRP`) : dis-le à côté de son chiffre.

**Critère de fin**
`vlp.py compteur "context AI/102-vitesse.md"` → une ligne par fiche, modèle + outils + attente + autre = actif à la
minute ; une transcription faite main donne son découpage exact (groupe neuf de `test-vlp.py`) ; recoupé sur la session
72db946f jusqu'à sa ligne `cost-state` (`totalToolDuration` 73,4 min, `totalAPIDuration` 63,4 min) : l'écart se dit ;
l'entrée « VIT17 — où passe le temps » de `08-etat.md`, VIT et NUI, trois constats ; `py -3 scripts/test-vlp.py` →
`OK`, `verifier(` en hausse ; mutant attrapé ; pyright 0 ; les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT18 -->
## VIT18 [x] — Le rapport : ce que VIT a gagné, et les pistes pour gagner plus

**Session** : 34c4592e-8d5d-490d-a4f2-24a7abb0c81e
**Dépend de** : `VIT17`.
**Fichiers** : `context AI/08-etat.md` (une entrée datée) ; la page, hors du dépôt, par `vlp.py chef page` — aucun
code.

**Prompt**
L'utilisateur veut savoir de combien VIT a accéléré le travail d'un LLM, puis ce qu'il faudrait ajouter, enlever ou
modifier pour aller plus vite, sainement ; il validera. Une seule page à cartes — la page ponctuelle d'`ARTEFACTS.md`,
remplie par `vlp.py chef page` (sa forme : la docstring de `vlp.py`) :
1. **En haut, les gains**, en clair d'abord (une image simple), comptes bruts à côté : la table de l'entrée « VIT13 —
   avant/après » de `08-etat.md`, et où passe le temps d'une fiche (« VIT17 »). Ce qui n'a pas gagné se dit aussi.
2. **Puis les pistes**, une carte chacune : ajouter, enlever ou modifier ; ce qu'elle change, ➕/➖, son coût (dit
   estimé), la mesure qui prouverait le gain. Leurs sources : les plus gros postes de `VIT17` ; ce qui n'a pas gagné ;
   les constats laissés hors fiches — les commandes du kit lancent `py` sans `-3` (détour par le `#!`), des fiches NUI
   cochées gardent des renvois par numéro de ligne, les vieux worktrees de `.claude/worktrees/` un ancien
   `relecture.md` ; la télémétrie officielle vue à `VIT17` ; ce que la doc officielle conseille pour aller vite
   (« Recherche web » du `CLAUDE.md` de l'utilisateur, trois recherches au plus ; lien et date par piste).
3. **Une carte de plus** : la question restée ouverte sur la page du chantier (fil du 2026-10-03) — le titre
   devient-il « Coder plus vite et mieux » ?
Publie la page et donne son lien. Une piste validée deviendra une fiche de VIT par `/vlp:chantier`, pas ici.

**Critère de fin**
La page publiée ; son lien dans l'entrée « VIT18 — le rapport » de `08-etat.md`, une ligne par carte ; les gains en
haut, comptes bruts ; chaque piste porte sa source ; le bouton copie rend une réponse par carte (essayé dans le
navigateur intégré).
<!-- /FICHE -->

---

<!-- FICHE:VIT19 -->
## VIT19 [x] — Le contrôle avant commit ne laisse plus passer

**Session** : 42ecf5f1-631e-44ba-acf8-9fbab5d27430
**Dépend de** : rien.
**Fichiers** : `.githooks/pre-commit`, `scripts/vlp_coeur.py` (`trouver_claude`, `cmd_claude`), `scripts/vlp.py` (sa
docstring), `scripts/test-vlp.py`.

**Prompt**
Carte 9 de `VIT18` — c'est aussi la ligne n° 101 `EXE` de la TODO (2026-10-04), que cette fiche fait : sa ligne sortira
de la TODO à la clôture de VIT, sur le oui de l'utilisateur. Constat du cadrage (2026-10-05) : l'app range désormais
`claude.exe` un dossier plus bas, sous `Packages` comme sous `%APPDATA%/Claude` (`EXE`) —
`claude-code/<version>/<empreinte>/claude.exe` (ici `2.1.288/36aa8c97bf86`). `trouver_claude` et `.githooks/pre-commit`
cherchent `claude-code/*/claude.exe` : 0 trouvé, « claude introuvable, validate sauté », sortie 0 — le commit passe sans
`claude plugin validate`. Le test du hook, dans `test-vlp.py`, recopie le même motif et se tait de même (`SAUTÉ:`).
1. Une seule recherche : `trouver_claude` lit les deux profondeurs (la plus haute version) ; le pre-commit et le test la
   demandent à `vlp.py claude` au lieu de recopier le motif (`CLAUDE.md`, règle 3).
2. Le refus, choisi par l'utilisateur : l'app est là (un dossier `claude-code` sous `Packages/Claude_*` ou sous
   `%APPDATA%/Claude`) mais aucun `claude.exe` → le pre-commit **refuse** le commit et dit pourquoi ; ni app ni
   `claude` → il avertit et laisse passer (un clone chez quelqu'un sans Claude). `vlp.py claude` distingue les deux cas.
3. Le commit de la fiche passe par le vrai hook : `claude plugin validate` y tourne.

**Critère de fin**
Trois cas en dossiers faits main (comme les tests voisins de `trouver_claude`) : `claude.exe` à la seconde profondeur →
trouvé ; dossier de l'app sans `claude.exe` → pre-commit sorti 1, sa raison dite ; rien → avertissement, sortie 0. Ici,
`py -3 scripts/vlp.py claude` → `CLAUDE …/claude.exe` ; le test du hook ne dit plus `SAUTÉ:` ; le commit de la fiche ne
dit plus « validate sauté » ; `py -3 scripts/test-vlp.py` → `OK`, `verifier(` en hausse ; mutant attrapé ; pyright 0 ;
les critères de code sain du socle.
<!-- /FICHE -->

---

<!-- FICHE:VIT20 -->
## VIT20 [x] — La carte avertit d'une session qui a déjà joué une fiche

**Session** : 25d14f1a-0b12-4403-be39-abe6b5c74fe6
**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py` (`carte_injectee`), `scripts/vlp.py` (sa docstring), `scripts/test-vlp.py`,
`skills/tache/SKILL.md`.

**Prompt**
Carte 6 de `VIT18`. « Une fiche, une session neuve » (`methode-chantier.md`, « Les trois temps ») ne se vérifie nulle
part ; `VIT3` à `VIT12` ont été jouées dans une seule session, `ctx_dernier` 302 283 (« VIT13 ») : chaque tour y relit
tout le passé. La session se connaît : `CLAUDE_CODE_SESSION_ID`, non vide dans le Bash de l'app (vu au cadrage) ;
`cocher` et `ouvrir` l'écrivent déjà sur les lignes `**Session** : <id>` du fichier de fiches (docstring de `vlp.py`).
- La carte de `/vlp:tache` : cet id déjà sur une ligne `**Session**` du fichier courant — une fiche jouée, ou le
  cadrage en tête — → une ligne `AVERTISSEMENT:` qui la nomme et dit `/clear` d'abord. Sinon, la sortie ne change pas
  (socle, « les sorties ne changent pas »). Id vide ou absent : rien, sans erreur.
- `/vlp:tache` relaie l'avertissement à l'utilisateur en une ligne.
- Pas de fausse alarme sous `/vlp:enchainer` : un chef y joue plusieurs fiches par conception — dis comment la carte
  le sait.
- L'id est-il vu par l'injection `!` des commandes, pas seulement par le Bash ? Vérifie-le en vrai, ou dis-le non
  vérifié (un `/reload-plugins` est un geste de l'utilisateur : demande-le dès le départ).

**Critère de fin**
Groupe neuf de `test-vlp.py` : id sur une fiche cochée → `AVERTISSEMENT:` qui la nomme ; sur la ligne du cadrage → de
même ; id absent ou vide, ou chef de `/vlp:enchainer` → sortie identique au caractère près à celle d'avant ; l'injection
vérifiée en vrai, ou dite non vérifiée ; `OK`, `verifier(` en hausse ; mutant attrapé ; pyright 0 ; code sain.
<!-- /FICHE -->

---

<!-- FICHE:VIT21 -->
## VIT21 [x] — Le mutant visé sur son groupe, par défaut

**Session** : 17d950aa-47f3-44c8-a41f-13ecc4e4896b
**Dépend de** : rien (`VIT2` et `VIT10` sont faites).
**Fichiers** : `scripts/vlp_coeur.py` (`cmd_mutant`), `scripts/vlp.py` (sa docstring), `scripts/test-vlp.py`,
`agents/relecture.md`, la ligne du socle de ce fichier qui dit comment se joue le mutant.

**Prompt**
Carte 2 de `VIT18`. Le mutant est le plus gros poste d'outil de NUI : 203 min pour 50 appels (« VIT17 »). Mesuré à
« VIT13 » sur le mutant de `NUI27` : `--attendu` seul, 105 s ; avec `--test "… test-vlp.py --seul NUI27"`, 6 s. Sans
`--test`, `cmd_mutant` lance toujours la suite entière.
- Par défaut, `--attendu` donné sans `--test` : ne jouer que le ou les groupes qui portent ce contrôle. Trouve
  comment : `--seul` lit le nom ou le texte d'un groupe (`VIT10`) — dis si le libellé de `--attendu` y suffit, ou ce
  qu'il faut de plus.
- Le piège : un motif qui ne trouve aucun groupe sort 1 par une `GARDE:` ; pris pour un écart, il donnerait un faux
  `MUTANT ATTRAPÉ`. Sans groupe sûr, retombe sur la suite entière, et dis-le dans la sortie.
- `--test` donné garde le dernier mot. Le relecteur et la ligne du socle suivent.

**Critère de fin**
Le mutant de `NUI27`, par la commande de l'entrée « VIT1 — la base » de `08-etat.md` sans `--test` → `MUTANT ATTRAPÉ`,
sa durée mesurée avant/après (comptes bruts, à côté des 6 s de « VIT13 ») ; un `--attendu` sans groupe → suite
entière, dite ; un groupe qui ne porte pas le contrôle ne rend jamais `ATTRAPÉ` (cas de test) ; `OK`, `verifier(` en
hausse ; mutant attrapé ; pyright 0 ; code sain.
<!-- /FICHE -->

---

<!-- FICHE:VIT22 -->
## VIT22 [x] — Raccourcir `test-boucle`

**Session** : 17d950aa-47f3-44c8-a41f-13ecc4e4896b
**Dépend de** : rien.
**Fichiers** : `scripts/test-boucle.py`, `scripts/boucle.py` si la cause y est, `context AI/08-etat.md` (une entrée
datée).

**Prompt**
Carte 1 de `VIT18`. `test-boucle.py` tourne en parallèle de `test-vlp.py` (`VIT7`) : 176 s, pour ≈ 180 s de suite
entière (« VIT13 ») — c'est lui qui en fixe la durée. Tant qu'il dure autant, raccourcir `test-vlp.py` ne sert à rien.
1. Mesure d'abord où passe son temps, cas par cas, le plus lent en tête ; et ce que dure `test-vlp.py` quand
   `test-boucle` ne le retient pas (s'il n'existe aucun moyen de le lancer seul, dis-le).
2. Raccourcis les plus lents sans retirer un contrôle : processus évitables (`VIT6` appelle déjà `vlp` dans le
   processus), attentes fixes, cas indépendants en parallèle. Pas de cache de résultats (Q5).
3. Rejoue les deux mesures de « VIT13 » sur ces deux fichiers, deux passages chacun, par la même commande.

**Critère de fin**
L'entrée « VIT22 — test-boucle » de `08-etat.md` : temps par cas avant/après, `test-boucle` et suite entière, deux
passages, comptes bruts ; `verifier(` de `test-boucle.py` jamais en baisse (compté avant/après) ; `OK` ; un mutant sur
un cas raccourci, attrapé ; pyright 0 ; code sain.
<!-- /FICHE -->

---

<!-- FICHE:VIT23 -->
## VIT23 [x] — Un contrôle rapide avant la suite entière

**Session** : 17d950aa-47f3-44c8-a41f-13ecc4e4896b
**Dépend de** : `VIT21` (le groupe qui porte un contrôle : même mécanique).
**Fichiers** : `scripts/vlp_coeur.py` ou `scripts/test-vlp.py` (selon la forme choisie), `scripts/vlp.py` (sa
docstring), `skills/tache/SKILL.md`, `scripts/test-vlp.py`.

**Prompt**
Carte 3 de `VIT18`. Une suite entière coûte ≈ 3 min (« VIT13 ») ; dans « VIT17 », 3 suites jouées sur 20 sont rouges
dans VIT, 5 sur 29 dans NUI — autant d'attentes pour un écart qu'un contrôle de quelques secondes aurait vu.
- Un contrôle rapide, en une commande : les groupes de la fiche (`--seul`), pyright sur les fichiers touchés s'il est
  là, `sante --cliquet`. Choisis sa forme, dis pourquoi ; sa durée se mesure en secondes.
- `/vlp:tache` le prescrit avant la suite entière, dans le kit : rouge, on corrige avant de lancer la suite.
- Il ne remplace rien : `cocher` exige toujours la suite entière verte (`VIT11`) ; aucun contrôle retiré.

**Critère de fin**
La commande rend vert ou rouge, sa durée mesurée (comptes bruts) ; un écart semé dans le groupe d'une fiche → rouge,
sans lancer la suite entière (cas de test) ; `skills/tache/SKILL.md` la nomme avant la suite ; `OK`, `verifier(` en
hausse ; mutant attrapé ; pyright 0 ; code sain.
<!-- /FICHE -->

---

<!-- FICHE:VIT24 -->
## VIT24 [x] — `test-mesure-tokens.py` dans la suite, `py -3` dans les commandes

**Session** : 17d950aa-47f3-44c8-a41f-13ecc4e4896b
**Dépend de** : rien.
**Fichiers** : `scripts/test-vlp.py`, `skills/*/SKILL.md` (les 8 lignes qui injectent la carte), `scripts/vlp_coeur.py`
(`carte_injectee`) si `PYTHON=` change de forme, `scripts/vlp.py` (sa docstring).

**Prompt**
Cartes 10 et 11 de `VIT18`.
1. `test-mesure-tokens.py` n'est lancé par rien (`grep -c test-mesure-tokens scripts/test-vlp.py` → 0, le 2026-10-05) ;
   joué seul le 2026-10-04 : `OK` en 0,8 s. La suite le lance, et son échec la rend rouge.
2. Les 8 `SKILL.md` lancent la carte par `py "…/vlp.py"`, et elle rend `PYTHON=py` : `py` lit le `#!` de `vlp.py` et
   relance le `python3` du PATH, +77 ms par appel (« VIT8 »). Passe l'injection et `PYTHON=` à `py -3`, donc toutes les
   commandes qui suivent ; le relais `python3` (Linux, macOS) ne change pas. `skills/enchainer/SKILL.md` dit « `py -3`
   si `PYTHON=py` » : simplifie-le.
3. Mesure `py` contre `py -3` : 20 lancements de `vlp.py lignes CHANTIER.md` chacun, médianes (la mesure 3 de `VIT1`).

**Critère de fin**
La suite lance `test-mesure-tokens.py`, et un échec semé la rend rouge (cas de test) ; les 8 injections et `PYTHON=` en
`py -3` (comptés par `grep`) ; une session neuve montre `PYTHON=py -3` dans sa carte ; médianes avant/après, comptes
bruts ; `OK`, `verifier(` en hausse ; mutant attrapé ; pyright 0 ; code sain.
<!-- /FICHE -->

---

<!-- FICHE:VIT25 -->
## VIT25 [x] — Mesurer l'effort du modèle sur 3 fiches

**Session** : 17d950aa-47f3-44c8-a41f-13ecc4e4896b
**Dépend de** : `VIT19` à `VIT24` — elle mesure l'état final, et en rejoue trois.
**Fichiers** : `context AI/08-etat.md` (une entrée datée) — aucun code ; un outil d'essai qui manquerait se dit avant.

**Prompt**
Carte 4 de `VIT18`, précisée par l'utilisateur le 2026-10-05 : l'effort Max est au socle depuis `VIT13` ; faut-il le
garder ? Mesurer Max, xhigh, high et medium sur 3 fiches.
1. D'abord le publié (doc `model-config` ; billet « Spending your effort », 2026-09-25 — cités à `VIT18`) : ce qui est
   déjà su ne se mesure pas. Et comment fixer l'effort d'un `claude -p`, mot pour mot.
2. Le plan : 3 fiches de code déjà jouées, de tailles différentes (💡 parmi `VIT19` à `VIT24`), chacune rejouée à
   chaque niveau depuis le commit d'avant elle, dans un worktree, jamais sur `main` — 12 essais. Pièges connus : le
   plugin chargé suit `main`, pas le worktree (`ESR`) ; un rejeu peut recevoir la carte du chantier en cours.
3. **Le coût, avant tout lancement** : par niveau et au total, tiré du coût réel des 3 fiches (`cout --session`).
   **Montre-le à l'utilisateur et arrête-toi jusqu'à son oui** : rien ne se lance sans.
4. Après son oui, par essai : tours, $, minutes (`compteur`), et la qualité — suite verte, mutant attrapé, verdict du
   relecteur. Un essai par case : un repère, pas une preuve ; dis-le.

**Critère de fin**
Le coût estimé montré, et le oui de l'utilisateur noté avant le premier essai ; l'entrée « VIT25 — l'effort » de
`08-etat.md` : 12 lignes (fiche × niveau), coût et qualité, comptes bruts ; la recommandation pour le socle, que
l'utilisateur tranche.
<!-- /FICHE -->
