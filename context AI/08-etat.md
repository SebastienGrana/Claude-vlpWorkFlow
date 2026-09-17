> **QUAND LIRE** : on reprend après une longue interruption, on choisit le
> prochain chantier, ou on doute d'une décision passée. Les cinq lignes de
> `CLAUDE.md` suffisent dans la plupart des cas — ouvrir ceci seulement quand
> elles ne suffisent pas.

# État du projet — daté

## Où on en est

- **2026-09-10** — le kit est un plugin Claude Code, v3.0.0 (« degré 3 »), chargé
  en place par un lien dans `~/.claude/skills/vlp`. Quatre commandes :
  `/vlp:init`, `/vlp:chantier`, `/vlp:tache`, `/vlp:check`.
- **2026-09-10** — les degrés 2 et 3 sont poussés sur GitHub, avec la ligne de
  clone ajoutée au README, à INSTALLATION et au TLDR.
- **2026-09-10** — le kit s'équipe lui-même de la méthode (`/vlp:init`).
- Abandonné : enchaîner les fiches automatiquement (chantier E clos le
  2026-09-10, voir le journal) — puis remis tel quel le 2026-09-17.
- **2026-09-17** — v3.1.0 : cinq commandes ; `/vlp:enchainer` et l'agent
  `vlp:fiche` déclarés dans toute la doc.
- **2026-09-17** — audit complet du kit (`12-audit.md`) : 11 bugs, 7
  fragilités, 19 transcripts mesurés. Constat central : une fiche coûte
  28 à 66 tours (recompté par le chantier T) ; la commande ne pèse que ~8 % du premier tour. Les dix
  chantiers qui en sortent sont la TODO ci-dessous.
- **2026-09-17** — chantier T clos (TODO n° 2) : les tours et le coût pondéré
  se mesurent ; les numéros de la TODO sont gardés, le 2 est retiré.
- **2026-09-17** — chantier B clos (TODO n° 1) : les bugs de l'audit sont
  corrigés ; le 1 est retiré, 6 et 10 ne dépendent plus de rien.
- **2026-09-17** — chantier R clos (TODO n° 3) : `/vlp:tache` prescrit 9
  appels au lieu de 14 ; le 3 est retiré, 8 ne dépend plus de rien.
- **2026-09-17** — chantier S clos (TODO n° 4) : la mécanique vit dans
  `scripts/vlp.py` ; le 4 est retiré, 5 ne dépend plus de rien.
- **2026-09-17** — chantier H clos (TODO n° 5) : un hook `PostToolUse` valide
  un fichier de fiches à l'écriture ; `SessionStart` écarté ; le 5 est retiré.
- **2026-09-17** — chantier V clos (TODO n° 6) : `claude plugin eval` passe 3 cas sous
  Windows, `validate` avant commit ; le 6 est retiré, ses cas Bash passent au 11.
- **2026-09-17** — chantier D clos (TODO n° 7) : la doctrine tient en trois docs à la
  racine, chaque seuil dans `vlp.py` ; le 7 est retiré.
- **2026-09-17** — chantier I clos (TODO n° 10) : `/vlp:init` nomme son fichier d'état
  par `vlp.py etat`, `/vlp:check` voit les renvois morts ; le 10 est retiré.
- **2026-09-17** — chantier K clos (TODO n° 8) : les cinq commandes vivent dans `skills/` (v3.2.0) ;
  le 8 est retiré, 9 ne dépend plus de rien.
- **2026-09-17** — chantier N clos (TODO n° 9) : `/vlp:enchainer` réparé par la skill forkée `vlp:jouer` (v3.3.0) ;
  le 9 est retiré.
- **2026-09-17** — chantier P clos (TODO n° 13) : un lanceur `scripts/vlp` sans accolade (v3.3.2) ; le 13
  est retiré, le 14 ouvert (une fiche visuelle n'arrête pas `/vlp:enchainer`).
- **2026-09-17** — chantier A clos (TODO n° 14) : une fiche `(visuel)` arrête `/vlp:enchainer` (v3.3.3) ; le 14
  est retiré, reste le 11.
- **2026-09-17** — chantier G clos (TODO n° 15) : Git for Windows requis par le kit, écrit dans `README.md` ; le 15
  est retiré, le 16 ouvert (le kit sans `sh`).
- **2026-09-17** — chantier W clos (TODO n° 11) : les evals `tache` et `chantier` passent sous Ubuntu (WSL2) ; le 11
  est retiré, reste le 16.
- **2026-09-17** — chantier X clos (TODO n° 16, renoncé) : hook et carte sans `sh` sondés sous Windows et Ubuntu ;
  rien d'appliqué — gain visible nul tant que le corps des skills exige `sh` ; le 16 est reformulé avec la recette.
- **2026-09-17** — chantier F clos (TODO n° 17) : `vlp.py feuille` et `vlp.py clore` écrivent la feuille de route et la clôture
  de `CHANTIER.md` (plugin 3.3.4, tests 59 → 73, eval chantier 3/3) ; avant : 15 tours sur 77 (X), 11 sur 61 (W) ; 8 781 743 tokens.
- **2026-09-17** — chantier O clos (TODO n° 18) : `vlp.py ouvrir` et `clore` étendu écrivent index, routage et « Où on en est »
  de `CLAUDE.md`, « Fait. » et `ZONE:bilan` (plugin 3.3.5, tests 73 → 91, eval chantier 3/3) ; avant : 12 tours sur 64 (F), 8 sur 77 (X) ; 9 842 371 tokens.

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée,
ordonné par ce qui débloque le reste. Le détail de chacun est dans
`12-audit.md`.

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 16 | Le kit sans `sh` | Faire tourner le kit sous Windows sans Git Bash. Mesuré (chantier X, `28-sans-sh.md`) : hook = paire exec `python3` + `py` (une erreur non bloquante à chaque écriture, partout) ; carte injectée = `py … carte \|\| python3 … carte` (propre sous pwsh 7, Git Bash et Ubuntu). Reste avant tout gain visible : les 17 appels `sh` du corps des skills et de `cloture.md`, les allowed-tools (sondes faites en `bypassPermissions`), PowerShell 5.1 (refuse `\|\|`), macOS, Python du Store seul | 3 fiches | — |

## Journal des décisions

Une ligne par décision imprévue tranchée en cours de fiche — jamais un résumé
de ce que le code dit déjà.

- **2026-09-10** — les fichiers de projet du kit (`CHANTIER.md`, `CLAUDE.md`,
  `context AI/`) sont publiés sur GitHub avec lui : le kit s'utilise et se
  développe en groupe.
- **2026-09-10** — E1 : `/vlp:init` publie une feuille de route, E1 l'interdisait ;
  la fiche l'a emporté, le bac à sable n'a aucune page (à retenir pour E7).
- **2026-09-10** — E3 : mesuré en vrai, `allowed-tools` du frontmatter d'une
  commande ne contraint pas son exécution rejouée via `Skill` dans un
  sous-agent (une commande Bash hors liste s'exécute sans refus) — contredit la
  doc officielle lue en E2 sur l'héritage strict du mode de permission ; E4-E6
  ne peuvent donc pas compter sur `allowed-tools` seul pour empêcher un
  sous-agent d'écrire hors de son périmètre.
- **2026-09-10** — E6 : un run S2+S3 de `/vlp:enchainer` coûte 143,5k tokens
  (S3 seul : 74 503, 11 appels d'outils) — jugé inacceptable, cible ÷5. Cause :
  coût ≈ contexte × tours, et un `general-purpose` porte tous les outils et
  `tache.md` entier. E7 réécrite : agent de plugin dédié (son corps seul comme
  prompt système, doc officielle), fiche pré-extraite, artefact une fois.
- **2026-09-10** — Chantier E **clos, abandonné** après E7. Mesures : un
  sous-agent `vlp:fiche` démarre à ~9k tokens et rend une fiche en 13-16k
  (S1 12 965, S2 13 163, S3 15 830) ; mais le chef est une session principale
  au socle de ~70k (plugins, skills, outils) qui fait ~12 appels par fiche
  (75k → 119k pour 3 fiches) : l'enchaînement coûte plus que le jeu manuel.
  `subagent_tokens` mesure le contexte du dernier tour, pas un cumul. Retirés :
  `/vlp:enchainer`, `agents/fiche.md`, `enchainement.md`, mode `enchaine` de
  `tache.md` ; gardée : la marque `(visuel)`. Levier restant, hors du kit :
  désactiver les plugins inutiles pour baisser le socle de session.
- **2026-09-10** — M2 : confirmé sur un vrai JSONL, `usage` vit sous
  `message.usage` (pas à la racine de la ligne), et seules les lignes
  `type: "assistant"` le portent — `scripts/mesure-tokens.py` s'y fie.
- **2026-09-11** — M4 : chemin relatif `scripts/mesure-tokens.py` introuvable
  depuis un projet équipé (résolu contre son propre cwd, pas contre le kit) —
  qualifié par `${CLAUDE_PLUGIN_ROOT}/scripts/mesure-tokens.py` dans
  `commands/tache.md` et `cloture.md`. Bug trouvé en testant sur Cairn, pas
  prévu par la fiche.
- **2026-09-11** — Chantier M **clos**. Livré : `scripts/mesure-tokens.py`
  (comptes bruts depuis un JSONL de transcript), affichage du coût en fin de
  fiche (`tache.md`) et à la clôture (`cloture.md`), proposition de
  commit/push à la clôture — jamais sans confirmation, à chaque fois. Total
  brut mesuré sur les sessions de M3 et M4 (seules fiches à porter une ligne
  `**Session**`), recompté par T5 : 100 tours, 94 appels, input 200, output
  45 607, cache_creation 265 871, cache_read 11 050 576, **total 11 362 254
  tokens**, 3,73 $.
- **2026-09-17** — `/vlp:enchainer` **remis tel quel**, à la demande, coût
  connu. `commands/enchainer.md`, `agents/fiche.md` et `enchainement.md`
  (version E7) n'avaient jamais été commités : reconstitués depuis les
  transcripts du 2026-09-10 (écritures rejouées, 0 désynchro). Deux retouches :
  la plage de lignes lue dans `tache.md`, décalée de 7 par M et C, devient les
  repères `## 0.` → `## 1.` ; le contrat ne nomme plus le mode `enchaine`, qui
  reste retiré. Non corrigé : ~12 appels du chef par fiche ; une fiche
  enchaînée ne reçoit pas de ligne `**Session**`, donc aucun coût sur la page ;
  le bilan lit `subagent_tokens`, le contexte du dernier tour et non un cumul.
- **2026-09-17** — Chantier C **clos**. Livré : le coût en tokens sur toutes
  les pages — par fiche et en total sur l'artefact de chantier (fiches à ligne
  `**Session**`), colonne Tokens et total cumulé dans la table des clos de la
  feuille de route, au format `≈7,8M (7 816 316)` ; M reporté après coup, E
  « non mesurable ». Laissé ouvert : pas de cumul entre projets (exclu) ; une
  fiche jouée par `/vlp:enchainer` n'a pas de ligne `**Session**`, donc aucun
  coût affiché. Constat qui vaut au-delà de C : le coût affiché en fin de fiche
  est un instantané, la session consomme encore après (C1 : 4 393 030 affichés
  sur la page à la fiche, 6 406 759 mesurés à la clôture). Total brut mesuré
  sur les sessions de C1 et C2, recompté par T5 : 68 tours, 68 appels, input
  136, output 50 466, cache_creation 173 480, cache_read 7 592 234, **total
  7 816 316 tokens**, 2,54 $.
- **2026-09-17** — T1 : sans `message.id`, `mesure-tokens.py` repère un tour
  par `requestId`, puis par sa ligne ; sur la ligne `TOTAL`, `ctx_1er` et
  `ctx_dernier` valent `-`, un contexte ne se somme pas. Mesuré sur C1 : le
  cache écrit mêle 5 min (47 978) et 1 h (26 375) — T3 ne peut pas tout
  compter au prix 1 h.
- **2026-09-17** — T2 : un fichier passé plusieurs fois à `mesure-tokens.py`
  (un id et son chemin, ou deux fiches d'une même session) n'est compté qu'une
  fois. T2 à T5 jouées d'affilée dans la session de T1, à la demande de
  l'utilisateur : le coût d'une fiche y est l'écart du compteur de session
  depuis la clôture de la fiche précédente.
- **2026-09-17** — T3 : un tour à comptes nuls (les 120 `<synthetic>` des
  transcripts) coûte 0 sans prix ; un tour `speed: fast` compte comme modèle
  inconnu, la grille ne donnant pas le prix de son cache ; `--grille` affiche
  la table de ratios. Les ratios ne sont pas communs (cache lu 0,025 sur
  Fable 5.1, 0,1 ailleurs) : modèle inconnu → `equiv` et `usd` valent `?`.
- **2026-09-17** — T4 : le cumul passe l'id de la session en tête du flux
  envoyé à `xargs -0` : sous macOS, `xargs` ne lance rien sur une entrée vide.
  Vérification jouée sans geste de l'utilisateur (fiches enchaînées) : les
  blocs de `tache.md` et `cloture.md` exécutés tels qu'écrits ; le rejeu réel
  de `/vlp:tache` sur un projet équipé reste à faire.
- **2026-09-17** — T5 : M et C recomptés ; anciens chiffres : M 13 030 459, C 15 389 496, une fiche « 51 à 128 tours ».
  Nouveaux : M 11 362 254 (100 tours), C 7 816 316 (68 tours), une fiche
  `/vlp:tache` = 28 à 66 tours. L'ancien script comptait chaque ligne
  `assistant` : ×1,7 à ×2,2 sur huit des neuf sessions de l'audit, ×4,6 sur
  E7 (128 lignes pour 28 tours : appels d'outils en parallèle). Le bilan de M
  ne baisse que de ×1,15 : il avait été pris avant la fin de ses sessions.
  Les pages de chantier M et C gardent les anciens chiffres : archives.
- **2026-09-17** — Chantier T **clos**. Livré : `scripts/mesure-tokens.py`
  compte une fois par tour (`message.id`) et rend tours, appels d'outils par
  outil, contexte du premier et du dernier tour, coût pondéré `equiv` et `usd`
  (`--grille`) ; il accepte un id de session seul et ne compte un fichier
  qu'une fois ; `scripts/test-mesure-tokens.py` le teste. La ligne `**Session**`
  s'écrit par `CLAUDE_CODE_SESSION_ID`. M et C recomptés. Laissé ouvert : le
  rejeu réel de `/vlp:tache` sur un projet équipé (T4) ; les pages de M et C
  gardent leurs anciens chiffres. Constat qui vaut au-delà de T : cinq fiches
  jouées d'affilée dans une session coûtent de plus en plus par tour (181 k en
  T3, 247 k en T4, 293 k en T5) — `/clear` entre deux fiches reste la règle.
  Total brut mesuré sur la session de T1..T5 : 89 tours, 95 appels, input 478,
  output 121 027, cache_creation 512 926, cache_read 15 560 204, **total
  16 194 635 tokens**, 16,55 $.
- **2026-09-17** — B1 : `$1` n'est pas le premier argument mais le **second**
  (index à partir de 0) — mesuré sur deux textes reçus : `/vlp:chantier chantier
  n° 1 …` a lu `n°` et `1` ; `/vlp:tache B1` a laissé `$1` littéral. Les quatre
  commandes lisent `$ARGUMENTS` ; sans lui, Claude Code ajoute `ARGUMENTS: …` en
  fin de texte. Reste à rejouer pour de vrai : `/reload-plugins`, puis
  `/vlp:tache` et `/vlp:chantier` avec arguments sur un projet équipé.
- **2026-09-17** — Chantier B **clos**. Livré : bugs 1, 2, 3, 5, 6, 7, 8, 10
  et 11 de `12-audit.md` corrigés, chacun prouvé par un grep avant/après —
  `/vlp:check` D trouve sa ligne ; `$ARGUMENTS` dans les quatre commandes ; plus
  de `${CLAUDE_PLUGIN_ROOT}` dans un fichier de données ; gabarits sans fichiers
  fantômes ni titre inversé ; `.gitignore` ; page orpheline retirée ; titres des
  pages E et M alignés ; lignes `**Session**` réduites à l'id (M et C : totaux
  identiques). Laissé ouvert : le rejeu réel de `/vlp:tache` et
  `/vlp:chantier` avec arguments après `/reload-plugins` ; les `CHANTIER.md`
  des autres projets équipés gardent `${CLAUDE_PLUGIN_ROOT}` sur la ligne
  « méthode » (inoffensif : `chantier.md` nomme le chemin lui-même). B1 à B3
  jouées d'affilée dans la session du cadrage, à la demande. Total brut mesuré
  sur cette session : 41 tours, 48 appels, input 82, output 35 226,
  cache_creation 147 563, cache_read 5 159 640, **total 5 342 511 tokens**,
  4,94 $.
- **2026-09-17** — R1 : dans une commande de plugin, `` !`…` `` exécute `pwd`,
  `head`, `a && b` et un script du plugin (`python "${CLAUDE_PLUGIN_ROOT}/…"`,
  variable substituée) ; la boucle `while` + `$(…)` de l'étape 0 n'est pas
  exécutée mais rendue au modèle (« run this first »), soit un tour. Une
  commande modifiée n'est pas relue sans `/reload-plugins` ; une neuve est vue
  en différé. `tache.md` prescrit 14 appels fixes sur le chemin heureux.
  L'essai sur `check.md` (sonde glissée dans une commande chargée) a été
  refusé par le mode auto, non contourné.
- **2026-09-17** — R2 : `references/` créé (contraintes 8, blocage 35, page 74
  lignes) ; `tache.md` 385 → 289 lignes. Les contraintes se lisent dans le même
  appel que le socle (aucun appel ajouté) ; la règle « artefact du chantier =
  aucun → sauter » reste dans `tache.md` seul. `enchainer.md` et
  `agents/fiche.md` ne découpent plus `tache.md`, sauf l'étape 0 (R3).
- **2026-09-17** — R3 : l'étape 0 devient `scripts/carte.py` (testé,
  `test-carte.py`), injecté par `tache.md` et `enchainer.md` via
  `` !`python3 … 2>/dev/null || python …` `` — repli prouvé par une sonde, le
  `python3` de Windows étant un faux raccourci (sortie 49). Choix validé par
  l'utilisateur, au lieu du repli en prose prévu par la fiche ; il anticipe un
  morceau du chantier `vlp.py`. Bug trouvé : sous Windows et macOS,
  `[ -f "$d/CHANTIER.md" ]` prend `commands/chantier.md` pour la carte — la
  boucle de l'étape 0 remontait donc au mauvais dossier depuis `commands/` ;
  `carte.py` compare le nom exact. `tache.md` 289 → 228 lignes ; l'étape 0 bis
  disparaît (`PROCHAINE=` dans la carte) ; fiche, socle et contraintes en un
  appel. Reste à rejouer pour de vrai : `/reload-plugins`, puis `/vlp:tache`
  sans argument sur un projet équipé.
- **2026-09-17** — R4 : corps de `tache.md` 150 lignes (`awk 'NR>5' | wc -l`) ;
  appels prescrits sur le chemin heureux 14 → 9 (0 et 0 bis injectés, socle et
  contraintes dans l'appel de la fiche, coût et page en un appel, coche et
  Session en une édition) ; octets relus par fiche 18 471 → 11 518. La liste
  des cinq écritures de clôture, recopiée de `cloture.md`, est retirée. Tours
  réels des fiches R, jouées d'affilée dans la session du cadrage — donc à
  contexte croissant et non comparables aux 28–66 tours de l'audit : R1 11,
  R2 12, R3 17, R4 9. Reste à faire pour de vrai :
  `/reload-plugins`, puis `/vlp:tache` sans argument dans une session neuve
  sur un projet équipé, mesuré par `mesure-tokens.py` — seul chiffre qui
  confirmera le gain en tours.
- **2026-09-17** — Chantier R **clos**. Livré : `commands/tache.md` en 150
  lignes de corps (385 avant) ; la carte du projet injectée avant le 1er tour
  par `scripts/carte.py` (testé, `test-carte.py`), aussi dans `enchainer.md` ;
  fiche, socle et contraintes en un appel ; coût et page en un appel ; blocage,
  page et contraintes dans `references/`, lus aussi par `enchainer.md` et
  `agents/fiche.md` — plus aucune commande ne découpe `tache.md` ; point 13
  corrigé. Appels prescrits sur le chemin heureux 14 → 9 ; octets relus par
  fiche 18 471 → 11 518. Laissé ouvert : le gain en **tours réels** n'est pas
  mesuré — il faut `/reload-plugins`, puis `/vlp:tache` dans une session neuve
  sur un projet équipé, et `mesure-tokens.py` sur cette session ; la page
  (6 bis) coûte toujours 5 appels, c'est le chantier `vlp.py`. Constat qui vaut
  au-delà de R : `[ -f "$d/CHANTIER.md" ]` est vrai pour `chantier.md` sous
  Windows et macOS — `/vlp:chantier` et `/vlp:init` gardent cette boucle ; et
  une commande de plugin modifiée n'est pas relue sans `/reload-plugins`. R1 à
  R4 jouées d'affilée dans la session du cadrage, à la demande. Total brut
  mesuré sur cette session à la clôture : 75 tours, 87 appels, input 150,
  output 77 488, cache_creation 197 055, cache_read 11 565 458, **total
  11 840 151 tokens**, 9,69 $.
- **2026-09-17** — S1 : `vlp.py extraire` s'arrête au marqueur ouvrant suivant quand
  un fermant manque, avec une `GARDE` — le `sed` de `tache.md` avalait la fiche
  suivante sans rien dire. Sur les fichiers sains, sortie identique au `sed`.
  S1 à S5 jouées d'affilée dans la session du cadrage, à la demande : le coût
  d'une fiche y est l'écart du compteur de session.
- **2026-09-17** — S2 : `vlp.py valider` ignore `(visuel)` entre accents graves,
  même quand le code en ligne commence sur la ligne d'avant (E5 le faisait passer
  pour un marqueur). Sur 09 à 16 : un seul écart, le `(visuel)` de C1
  (`11-conso.md:88`), laissé tel quel (archive). La commande rechargée injecte
  déjà `vlp.py carte` : l'injection du nouveau script est prouvée en vrai.
- **2026-09-17** — S3 : `vlp.py page` remesure chaque session `**Session**` à chaque
  régénération ; une session portée par plusieurs fiches (jouées d'affilée) garde
  sur les premières le coût déjà affiché et donne le reste à la dernière, moins la
  part que l'ancienne page n'attribuait à aucune fiche (le cadrage) — sans cette
  soustraction, S3 affichait 5 673 095 au lieu de 3 830 649. Régénérer
  une page close remet donc ses coûts à jour : sur R, la session a continué après la
  clôture (11 840 151 → 13 103 584 tokens) et R4 prend l'écart — les pages closes ne
  se régénèrent pas. `--verifier` ne compare que les états et l'avancement.
- **2026-09-17** — S4 : `/vlp:tache` prescrit 5 appels sur le chemin heureux au lieu
  de 9 (1 : fiche, socle, contraintes et `tache-page.md` ; 5 : vérifier ; 6 : coche
  et Session ; 6 bis : coût + `vlp.py page`, puis publier) ; octets relus par fiche
  11 530 → 9 463. La publication part sans `read` : dans une session neuve elle
  peut être refusée une fois (le refus rend la version en ligne) — à rejouer pour de
  vrai. `Bash(sed:*)` reste dans `tache.md` pour les plages citées par les fiches.
  `agents/fiche.md` n'avait aucun `sed`/`awk` : inchangé.
- **2026-09-17** — S5 : le repli `python3 … || python …` ne vaut que pour une
  sous-commande qui sort toujours 0 (`carte`) ; sur `valider`, `page` ou
  `extraire`, un écart relance le script en double — ces appels passent par
  `PY=$(for p in python3 python; …)`. `/vlp:chantier` étape 0 : 2 appels → 0.
  À rejouer après `/reload-plugins` : `/vlp:chantier`, `/vlp:init`, `/vlp:check`
  sur un projet équipé et sur le bac à sable. Le refus de publication prévu en S4
  est arrivé : republier le même contenu est **refusé une seconde fois** — il faut
  `Artifact action: "read"` sur l'URL, puis publier (3 appels). `tache-page.md`
  dit encore « republie » : à corriger.
- **2026-09-17** — Chantier S **clos**. Livré : `scripts/vlp.py` (carte, extraire,
  socle, sessions, valider, page), testé par `scripts/test-vlp.py` ; `carte.py`
  retiré ; les cinq commandes, `tache-page.md` et `cloture.md` l'appellent. Avant → après :
  lignes `sed`/`awk` 11 → 1 (prose), appels à `carte.py` 4 → 0, appels prescrits
  de `/vlp:tache` 9 → 5, de `/vlp:chantier` étape 0 2 → 0, page retapée à chaque
  fiche → régénérée par le script. Coût : 17 193 402 tokens · 106 tours ·
  15,72 $ (2 sessions, S1 à S4 dans celle du cadrage). Laissé ouvert : rejouer
  `/vlp:chantier`, `/vlp:init`, `/vlp:check` après `/reload-plugins` ;
  `tache-page.md` (« republie » → `read` puis publier) ; `init.md` 3 ter dit
  encore que `/vlp:tache` ne lit qu'au `sed`/`awk` (TODO 10).
- **2026-09-17** — H1 : un kit lié dans `~/.claude/skills/vlp` **charge** ses hooks
  après `/reload-plugins` (« 3 hooks » annoncés pour 4 posés). Sur Windows avec Git
  Bash, en forme shell : `python` et `py` parlent (exit 2 → stderr rendu au modèle,
  `${CLAUDE_PLUGIN_ROOT}` substitué en `C:/Users/znorr/.claude/skills/vlp`) ; `python3`
  (faux raccourci) échoue **muet** ; la forme `args` (sans shell) ne se déclenche pas.
  Forme retenue pour H3 : la boucle `PY=$(for p in python3 python; …)` des commandes,
  qui ne relance pas le script en double. Restes de S soldés : `tache-page.md` lit
  avant de publier (« republie » 2 → 0) ; `/vlp:check` rejoué, A–G passent (socle 51,
  page 133) ; `/vlp:init` rejoué sur un dossier vide du scratchpad : `AUCUN_PROJET`
  puis `PROJET=` après pose, questionnaire répondu par défaut et publication
  **neutralisée** (pas d'artefact de test) ; `init.md` 3 ter reste faux (TODO 10).
- **2026-09-17** — H2 : `vlp.py hook` reconnaît un fichier de fiches à un marqueur
  `<!-- FICHE:X1 -->` ou à `## Le socle commun` **hors bloc de code** — sinon
  `methode-chantier.md`, `commands/chantier.md` et le gabarit, qui en montrent,
  seraient validés à chaque édition. Le gabarit de fiches passe (`VALIDE 0 fiches`) ;
  `exemples/fichier-de-fiches-cairn.md` (N1 sans marqueurs) et `11-conso.md:88`
  seront signalés s'ils sont édités : archives, laissées telles quelles. Un appel :
  0,19 à 0,21 s. Sous Git Bash, un patch Python passé en heredoc à `python -` a
  perdu ses échappements de saut de ligne (deux fois) ; écrit dans un fichier, il passe.
- **2026-09-17** — H3 : le hook `PostToolUse` est branché (`hooks/hooks.json`, forme
  `PY=$(for p in python3 python; …)`) ; `/reload-plugins` annonce « 1 hook ». Prouvé
  en vrai : un `Write` intact rend `VALIDE 1 fiches · socle 4 lignes` en contexte
  additionnel, sans bloquer ; un `Edit` qui retire `<!-- /FICHE -->` rend l'écart
  (ligne 15, `INVALIDE`) et la consigne ; la coche de H3 par `Edit` rend
  `VALIDE 4 fiches · socle 51 lignes`. `commands/chantier.md` : appel `valider` dans
  un bloc 1 → 0 (nommé une fois en prose, repli si le hook ne tourne pas), appels
  prescrits de l'étape 6 inchangés (1 : `wc -l`) ; lignes `identique|marqueur`
  16 → 15. Règle 4 de `CLAUDE.md` : `${CLAUDE_PLUGIN_ROOT}` vaut aussi dans
  `hooks/hooks.json`. Non couvert : les écritures par Bash (`sed -i`, heredoc), que
  `Write|Edit` ne voit pas — `vlp.py page` et les coches scriptées y échappent.
- **2026-09-17** — H4 : `SessionStart` (`startup|clear` → `vlp.py carte`) **écarté**.
  Mesuré sur deux sessions neuves d'un seul mot : avec, ctx_1er 60 609, 2 tours,
  122 861 tokens (`01afcef7`, carte injectée, `PROCHAINE=H4` présent) ; sans,
  ctx_1er 58 635, 1 tour, 58 936 tokens (`b50ef5e2`). La carte (65 lignes,
  4 111 octets) ajoute 1 974 tokens à chaque tour de toute session du projet,
  vlp ou non, et ne retire aucune injection : elle ne part qu'au démarrage et
  après `/clear`, alors que `PROCHAINE` change en cours de session (H1 → H4 dans
  celle du chantier). Le second tour de la session « avec » (un `git diff`) n'est
  pas attribuable à la carte.
- **2026-09-17** — Chantier H **clos**. Livré : `vlp.py hook` (testé, 5 cas) et
  `hooks/hooks.json` — un `PostToolUse` `Write|Edit` qui valide un fichier de
  fiches à l'écriture : sain → la ligne `VALIDE` en contexte, cassé → l'écart et
  la consigne, prouvé en vrai après `/reload-plugins` ; `commands/chantier.md`
  n'appelle plus `valider` dans un bloc (1 → 0), consignes `identique|marqueur`
  16 → 15 ; règle 4 étendue à `hooks/hooks.json` ; `tache-page.md` lit avant de
  publier ; `/vlp:check` et `/vlp:init` rejoués. Laissé ouvert : les écritures par
  Bash échappent au hook ; sans Git Bash, Windows lance les hooks en PowerShell et
  la forme `PY=$(…)` y casse (non testé) ; appels prescrits de `/vlp:chantier`
  étape 6 inchangés (1, `wc -l`). Constat qui vaut au-delà de H : un kit lié dans
  `~/.claude/skills/` charge ses hooks, et `python3` y échoue muet sous Windows.
  Fiches jouées d'affilée dans la session du cadrage, à la demande. Total brut
  mesuré sur cette session : 87 tours, 95 appels, input 174, output 66 514,
  cache_creation 217 798, cache_read 14 364 692, **total 14 649 178 tokens**,
  11,02 $.
- **2026-09-17** — V1 : cas eval `check` créé avec `case.yaml` + `fixture.sh`. Apprentissages : (1) fixtures non copiées au cwd du run — solution `scaffold_script: fixture.sh` (fichier, pas inline) qui écrit les fichiers en heredoc, pas de `cp` ; (2) `Skill` refusé sans `allowed_tools` déclaré dans le cas (confus avec `allowed_tools` du frontmatter) ; (3) `allowed_tools` du cas ne peut pas élargir au lancement, d'où `--allow-tools` en flag ; (4) hooks du plugin tournent (`PostToolUse`), personnels absents ; Artifact off dans eval. Runs : échecs 0,10 / 0,069 / 0,068 $ (Skill refusé, max_turns 10 dépassé), succès 0,2375 $ en 26 tours (max_turns 15, score 1). Bac à sable : CHANTIER.md (kit relatif `~/.claude/skills/vlp`), `context AI/08-etat.md` (1 fiche cochée `C1[x]` sur fichier inexistant `context AI/fiches-inexistant.md`), graders regex+tool_used. Cas retenu : `scaffold` + `--trust-plugin` (Bash sandbox unavailable sous Windows). Plafond V1..V4 : 0,35 $ par run.
- **2026-09-17** — V2 **bloquée** : `/vlp:tache` et `/vlp:chantier` injectent leur carte
  par `` !`python … carte` `` ; sans Bash, l'injection est refusée et le run s'arrête au
  2e tour (score 0,5 et 0,33, 0,045 $ chacun). Avec `--allow-tools Bash`, le run est
  refusé avant de tourner (0,00 $) : Windows n'a pas de sandbox, la doc exige WSL2 (ou
  Linux avec `bubblewrap` et `socat`). WSL2 est actif ici, mais Ubuntu n'est pas
  initialisé (seule distribution : `docker-desktop`). Cas `tache` et `chantier` écrits,
  tag `wsl2`, jouables sous WSL2 (TODO n° 11). `V4` ne dépend plus de `V2`. Incident : le
  sous-agent `vlp:fiche` a exécuté une fixture à la racine du kit (`CHANTIER.md` et
  `08-etat.md` écrasés) — restaurés par `git checkout`, rien perdu ; la fiche est reprise
  par le chef, le sous-agent (8 tours par reprise) relancé 4 fois pour V1.
- **2026-09-17** — V3 : les cas `init` et `hook` passent **sous Windows**, sans Bash.
  `init` : `allowed_tools` sans Bash, `--allow-tools Write Edit` (ce ne sont pas des
  shells, ils s'accordent sans sandbox) — le modèle se passe des blocs Bash de
  `init.md` ; score 1, 19 tours, 0,385 $ ; `CHANTIER.md` et `*/08-etat.md` posés,
  `Artifact` appelé 0 fois (l'outil est off dans un run). `hook` : `Write` d'un fichier
  de fiches sans `<!-- /FICHE -->` ; score 1, 2 tours, 0,096 $, puis 0,05 $ au rejeu
  `--keep-temp` qui prouve l'origine : la trace porte l'erreur `PostToolUse:Write` de
  `vlp.py hook` (« marqueur ouvrant sans fermant », `INVALIDE 1 fiches`) — les hooks du
  plugin tournent dans un run, sous Windows, hors sandbox. Grader resserré sur
  `INVALIDE [0-9]+ fiches`. La trace d'un run réussi est effacée sans `--keep-temp`.
- **2026-09-17** — V4 : `marketplace.json` reçoit sa `description` ; `claude plugin
  validate` sur le marketplace : 1 avertissement → 0. Sur `plugin.json`, 1 avertissement
  **gardé** : « CLAUDE.md at the plugin root is not loaded » — voulu, le kit est aussi un
  projet ; d'où pas de `--strict`. `.githooks/pre-commit` valide les deux manifestes,
  activé par `git config core.hooksPath .githooks` (ligne dans `INSTALLATION.md`). Prouvé :
  sans `claude` dans le PATH, il le dit et laisse passer (exit 0) ; un `plugin.json`
  cassé est refusé (exit 1, aucun commit), le message nommant `marketplace.json` qui
  l'embarque ; ce commit-ci est passé par la garde. Suite Windows (`check`, `init`,
  `hook`) : 3 cas sur 3, score 1 chacun ; 3 runs, 39 tours (17, 20, 2), 0,93 $ (0,563,
  0,315, 0,054) — `check` coûtait 0,24 $ en V1 : le coût d'un cas varie du simple au
  double, le plafond vaut pour le lancement. Non joués (tag `wsl2`) : `tache`, `chantier`.
- **2026-09-17** — Chantier V **clos**, V2 abandonnée. Livré : `evals/` et trois cas qui
  passent sous Windows — `check` (incohérence vue), `init` (fichiers posés, 0 `Artifact`),
  `hook` (`INVALIDE` du hook dans la trace) : 3 runs, 39 tours, 0,93 $ ;
  `.githooks/pre-commit` qui lance `claude plugin validate` (manifeste cassé refusé) ;
  `marketplace.json` 1 → 0 avertissement ; `.gitattributes` garde les `.sh` en LF.
  Laissé ouvert : `tache` et `chantier` écrits (tag `wsl2`) mais jamais passés — Bash est
  refusé sous Windows faute de sandbox (TODO n° 11) ; 1 avertissement voulu sur
  `plugin.json` (`CLAUDE.md` à la racine) ; la garde se saute si `claude` n'est pas dans
  le PATH (cas de cette machine). Constats qui valent au-delà de V : une commande qui
  injecte par `` !`…` `` ne se teste pas sous Windows ; les hooks du plugin tournent
  dans un run d'eval ; le sous-agent `vlp:fiche` (8 tours) ne tient pas une fiche
  d'essais — relancé 4 fois pour V1, il a exécuté une fixture à la racine du kit ; V3 et
  V4 jouées par le chef. Total brut mesuré à la clôture — session du cadrage et des
  fiches : 104 tours, 114 appels, input 216, output 75 395, cache_creation 199 167,
  cache_read 16 479 432, **total 16 754 210 tokens**, 12,12 $ ; sous-agents : 49 tours,
  71 appels, total 2 562 465 tokens, 0,68 $ ; soit **19 316 675 tokens**, 12,80 $ — plus
  17 lancements d'eval, 2,25 $ (prix catalogue, hors transcripts).
- **2026-09-17** — Chantier D **clos**. Livré : docs racine 8 → 5 (`README` absorbe
  `INSTALLATION` et le TLDR, 398 → 141 lignes ; la méthode absorbe `CONVENTION-FICHIERS`,
  248 → 202, et porte seule « un seul endroit » et « comptes bruts ») ; `SEUIL_SOCLE = 80`
  dans `vlp.py`, qui avertit ; `250` dans 6 fichiers → 1 (`vlp.py`), `80 lignes` 2 → 1
  (`test-vlp.py`) ; ARTEFACTS, cloture, enchainement 265 → 233 lignes ; commandes 872 → 868.
  `validate` propre ; evals Windows 3/3, 40 tours (16, 2, 22), 0,55 $ (V4 : 39 tours,
  0,93 $). Laissé ouvert : `comptes bruts` reste dans 10 fichiers comme ordre d'agir
  (commandes, gabarits), pas comme règle recopiée. Constat qui vaut au-delà de D :
  `/vlp:enchainer` a joué D1 avec un sous-agent `vlp:fiche` coupé 3 fois à 8 tours
  (`maxTurns: 8`) — D2 à D6 jouées à la main dans une seule session ; `claude` absent
  du PATH, trouvé sous `%APPDATA%/Claude/claude-code/<version>/claude.exe`. Total brut
  mesuré — session des fiches : 54 tours, 62 appels, total 6 218 533 tokens, 5,21 $ ;
  sous-agent D1 : 24 tours, 945 694 tokens, 0,20 $ ; soit **7 164 227 tokens**, 5,41 $,
  plus 0,55 $ d'evals ; cadrage non mesuré (pas de ligne `**Session**`).
- **2026-09-17** — I2 : vlp.py renvois lit la 1re cellule des tables de l'index et la dernière du routage de CLAUDE.md — toutes les cellules prenaient vlp.py, cité dans un intitulé de tâche, pour un fichier. Sur ce kit : 39 nommés, 1 absent (scripts/carte.py, retiré en S) → 0.
- **2026-09-17** — Chantier I **clos**. Livré : `vlp.py etat` (fichier d'état présent, sinon le premier
  numéro libre) appelé par `/vlp:init`, gabarits en `<NN>-etat.md` (`08-etat` en dur dans `templates/` et
  `commands/` 7 → 0) ; `vlp.py renvois` (fichiers nommés par l'index et le routage, absents) en
  vérification H de `/vlp:check` — sur ce kit 39 nommés, 1 → 0 absent (`scripts/carte.py`) ; `init.md`
  3 ter ne recopie plus les outils de `/vlp:tache` (`awk` 1 → 0) ; tests `OK` (7 cas ajoutés). Prouvé :
  eval `init` seule, score 1, 25 tours, 0,37 $ ; sur le projet posé, `renvois` 2 nommés · 0 absent,
  `01-etat.md` = `ETAT=01-etat.md`. Laissé ouvert : les projets équipés ne sont pas repassés à
  `renvois` ; l'eval `init` a pris 25 tours pour `max_turns: 25` — à la limite ; `/vlp:chantier` étape 5
  numérote encore par `ls`. Cadrage, I1 à I3 et clôture dans une seule session, à la demande. Total brut
  mesuré : 45 tours, 59 appels, input 90, output 32 373, cache_creation 155 279, cache_read
  6 355 087, **total 6 542 829 tokens**, 5,54 $, plus 0,37 $ d'eval.
- **2026-09-17** — K3 : une commande déplacée en cours de session **disparaît** de la session : `Skill vlp:tache` rend
  `Unknown skill` après K2 (l'ancienne `commands/tache.md` n'existe plus, la skill n'est vue qu'après
  `/reload-plugins`) — K3 et la clôture jouées en suivant la procédure déjà en contexte.
- **2026-09-17** — Chantier K **clos**. Livré : `commands/*.md` → `skills/<nom>/SKILL.md` (5 renommages sans
  changer un octet), `references/` → `skills/tache/references/` (5 chemins réécrits dans `tache`, `enchainer`,
  `agents/fiche.md`) ; renvois de la doc 17 → 12 lignes, 0 mort ; `vlp.py renvois` 41 nommés · 0 absent ;
  plugin 3.2.0 ; `validate` 1 avertissement voulu ; evals Windows 3/3 (check 15, hook 2, init 22 tours ; 0,55 $).
  Écarté aux chiffres : `disable-model-invocation` (eval `check` score 1 → 0,5, `Skill` 0 appel). Laissé ouvert :
  `context: fork` (TODO n° 9) ; la substitution de `${CLAUDE_PLUGIN_ROOT}` et `` !`…` `` dans une skill n'est
  lue dans aucune trace (les cas qui injectent sont tag `wsl2`) ; rejouer `/vlp:tache` après `/reload-plugins`.
  Cadrage, K1 à K3 et clôture dans une seule session, à la demande. Total brut mesuré : 47 tours, 61 appels, input 94, output 31 360, cache_creation 130 838, cache_read
  6 041 359, **total 6 203 651 tokens**, 5,11 $, plus 0,85 $ d'evals.
- **2026-09-17** — K1 : `disable-model-invocation: true` **écarté** — mesuré sur l'eval `check` : sans, score 1, 19 tours,
  0,19 $ ; avec, score 0,5, `Skill` appelé 0 fois, 9 tours, 0,11 $ (la skill reste tapable, `vlp:check` dans
  `slash_commands`, mais le modèle ne peut plus l'appeler — or les evals et « lance /vlp:… » passent par `Skill`).
  `commands/check.md` → `skills/check/SKILL.md` sans changer un octet ; `${CLAUDE_PLUGIN_ROOT}` substitué selon la
  doc des skills, non relu dans une trace (le run réussi n'a pas `--keep-temp`).
- **2026-09-17** — N1 : une skill `context: fork` + `agent: vlp:fiche` + `background: false` **joue une fiche** (meta
  `agentType: vlp:fiche`, foreground) ; `$ARGUMENTS` et `` !`python … vlp.py socle|extraire` `` substitués avant le
  sous-agent — la doc ne nomme pas les agents de plugin, ils passent. Sonde headless (`claude -p`, Sonnet 5 en chef,
  Haiku en sous-agent) sur 2 fiches triviales. Essai 1 : chef 3 tours, 2 `Skill`, S1 `RETOUR` (le `cat` du kit bloqué hors
  du dossier de travail), S2 `FAITE`, 0,30 $. Essai 2, `--add-dir` du kit : **chef 3 tours pour 2 fiches** (2 `Skill`,
  ctx 46 238 → 47 230, 140 841 tokens, 0,06 $) ; sous-agents 6 et 8 tours (5 et 10 appels, 68 455 et 93 569 tokens,
  0,03 $ chacun) ; **2 fiches cochées sur 2** ; 0,12 $. Total sonde 0,42 $. Surprise : S2 a atteint `maxTurns: 8` après sa
  coche, sans compte rendu — le chef reçoit « Skill execution completed » et le lit comme un statut. Les transcripts d'un
  bac à sable du scratchpad dépassent 260 caractères : Python ne les ouvre qu'après copie.
- **2026-09-17** — N2 : `/vlp:enchainer` **réparé** — seuil chef ≤ 3 tours par fiche, mesuré en N1 à 3 tours pour
  2 fiches. Une skill forkée ne boucle pas : nouvelle skill `vlp:jouer` (`context: fork`, `agent: vlp:fiche`,
  `background: false`, `user-invocable: false`) qui injecte la carte ; le chef ne lit plus ni socle ni fiche, un
  `Skill` par fiche. `maxTurns` 8 → 25 (D1 : 24 tours en trois relances). Lignes : `enchainer` 145 → 105,
  `fiche.md` 35 → 38, `enchainement.md` 14 → 14, `jouer` 0 → 31. Rejeu réel headless sur le bac à sable : chef
  3 tours, 2 `Skill` ; sous-agents 7 et 7 tours (9 et 10 appels) ; 2/2 `FAITE` ; 321 021 tokens, 0,14 $ —
  `${CLAUDE_PLUGIN_ROOT}` et `` !`…` `` **substitués dans une skill de plugin** (trace : `Kit : C:/Users/znorr/.claude/skills/vlp`,
  `PROJET=C:…`). Plugin 3.3.0 ; `validate` : marketplace passe, `plugin.json` 1 avertissement voulu.
- **2026-09-17** — Chantier N **clos**. Livré : `/vlp:enchainer` **réparé** — skill interne `vlp:jouer`
  (`context: fork`, `agent: vlp:fiche`, `background: false`, `user-invocable: false`) qui injecte la carte ; le chef
  fait un `Skill` par fiche et ne lit ni socle ni fiche (`enchainer` 145 → 105 lignes) ; `maxTurns` 8 → 25 ; un
  compte rendu sans statut vaut `RETOUR` (`enchainement.md`) ; doc alignée (renvois périmés 4 → 0, `vlp.py renvois`
  44 nommés · 0 absent) ; plugin 3.3.0 ; evals Windows 3/3 (check 21, hook 2, init 26 tours ; 0,62 $). Mesuré en
  headless : chef 3 tours pour 2 fiches, 2/2 `FAITE`, 0,14 $. Laissé ouvert : `background: false` n'est prouvé qu'en
  `-p`, où une skill forkée attend toujours — à rejouer en session interactive après `/reload-plugins`, sur un vrai
  chantier ; un workspace (`VOISIN=`) n'est pas joué par `vlp:jouer` ; l'eval `init` a pris 26 tours pour
  `max_turns: 25` et passe. Constats qui valent au-delà de N : une skill de plugin substitue `${CLAUDE_PLUGIN_ROOT}`
  et `` !`…` `` (prouvé par trace) ; en `-p`, un `cat` du kit hors du dossier de travail est bloqué — `--add-dir` ;
  les transcripts d'un bac à sable du scratchpad dépassent 260 caractères, Python ne les ouvre qu'après copie.
  Cadrage, N1 à N3 et clôture dans une seule session, à la demande. Total brut mesuré au bilan : 45 tours, 54 appels,
  input 92, output 42 158, cache_creation 163 490, cache_read 6 285 334, **total 6 491 074 tokens**, 5,83 $, plus
  0,56 $ de sondes headless (3 lancements) et 0,62 $ d'evals.
- **2026-09-17** — Premier `/vlp:enchainer` réel après N, sur MapDecorator (session `8a854f86`, partie enchaîneur
  isolée après `/reload-plugins`) : `background: false` **tient en session interactive** — le chef appelle
  `vlp:jouer` pour P2, attend, lit `RETOUR` (rechargement en jeu), questionne, ne coche pas, s'arrête avant P3.
  Chef (Opus) 15 tours, 14 appels (Bash 9, Artifact 2, AskUserQuestion 2, Skill 1), ctx 94 408 → 108 267,
  1 507 553 tokens, 2,07 $ ; sous-agent (Haiku) 22 tours pour `maxTurns: 25`, 21 appels, 537 087 tokens, 0,13 $.
  Loin du « un appel par fiche » : P1, déjà écrite dans la session, vérifiée et cochée par le chef ; ≈ 5 tours
  d'action du chef après le `RETOUR` (copie de fichier, lecture du log) ; ≈ 6 tours pour la page (lecture de
  `tache-page.md`, `vlp.py page --help`, `ls` du HTML, `page`, `read`, publier). Devient la TODO n° 12.
- **2026-09-17** — L2 : la doc des skills confirme `model:` (« The override applies for the rest of the current turn ») ;
  `model: sonnet` posé sur `skills/enchainer/SKILL.md` — tout le lancement, questions comprises, puis la session
  reprend son modèle. `maxTurns` de `vlp:fiche` 25 → 30 : 22 tours mesurés sur MapDecorator laissaient 3 tours de
  marge, et un plafond atteint rend un compte rendu sans statut. `enchainer` 110 → 114 lignes (étape 3 bis : aucun
  autre outil que la question et la case ; étape 2 : une fiche cochée n'est ni rejouée ni vérifiée).
- **2026-09-17** — L3 : sonde headless (bac à sable, S1 scriptable, S2 `(visuel)`, `--model opus`). Chef **7 tours** pour 2
  fiches (Bash 2, Grep 1, Skill 2, ToolSearch 1), S1 `FAITE`, S2 `RETOUR` ; reprise « ne coche pas » : **2 tours**, page
  en **1 appel** Bash (publication coupée par `--max-budget-usd 0.5`). Total chef 9 tours, 7 appels, 407 951 tokens,
  0,78 $ pondéré ; avant : 15 tours, 14 appels, 2,07 $ (MapDecorator, en session). Sous-agents 9 et 6 tours (13 et 8
  appels) pour `maxTurns: 30`. **`model: sonnet` bascule le chef** : tout le lancement en `claude-sonnet-5` malgré
  `--model opus`, témoin sans skill en `claude-opus-5` ; une réponse en **texte** est un nouveau prompt, le chef repasse
  en Opus (la reprise : 0,51 $ pour 2 tours). En `-p`, `Artifact` existe, `AskUserQuestion` non. Surprise : le motif
  `PY=$(for p in …)` est refusé en `-p` (« Contains brace with quote character ») — TODO n° 13. Plugin 3.3.1 ; evals
  Windows 3/3 (check 19, hook 2, init 23 tours ; 1,00 $). Sondes : 1,26 $ en 3 lancements.
- **2026-09-17** — Chantier L **clos**. Livré : le chef de `/vlp:enchainer` allégé — page en un appel (plus de `cat
  tache-page.md`), aucune action après un `RETOUR` hors la question et la case, `model: sonnet` sur la skill,
  `maxTurns` de `vlp:fiche` 25 → 30 ; plugin 3.3.1 ; evals Windows 3/3 (1,00 $). Mesuré en headless : chef 15 → 9
  tours, 14 → 7 appels, 2,07 $ → 0,78 $ pondéré. Laissé ouvert : la publication de la page n'est pas mesurée (plafond
  de budget) ; en session interactive, une réponse par `AskUserQuestion` devrait garder Sonnet (même tour), non
  prouvé ; le motif `PY=$(for …)` refusé en `-p` (TODO n° 13). Cadrage, L1 à L3 et clôture dans une seule session, à
  la demande. Total brut mesuré au bilan : 52 tours, 58 appels, input 106, output 37 918, cache_creation 154 946,
  cache_read 7 131 593, **total 7 324 563 tokens**, 6,06 $, plus 1,26 $ de sondes headless (3 lancements) et 1,00 $
  d'evals.
- **2026-09-17** — P1 : lanceur `scripts/vlp` (sh, essaie `python3`, `python`, `py` par `-c ""`, puis `exec` ; aucun →
  exit 127) ; 3 tests ajoutés à `test-vlp.py` (relaie la sortie, relaie le code, 127) ; `.gitattributes` force LF.
  Surprise : `${0%/*}` ne coupe pas un chemin en `\` (appel depuis Python) — `case` sur les deux séparateurs.
  Sondes `-p` en Sonnet, bac à sable vide, une commande imposée : (a) ancien motif, `Bash(python3:*) Bash(python:*)` →
  **refusé** « Contains brace with quote character (expansion obfuscation) », 2 tours, 1 appel, 0,20 $ ; (b) `sh
  "<kit>/scripts/vlp" etat ctx`, `Bash(sh:*)` → **passe**, `ETAT=01-etat.md`, 2 tours, 1 appel, 0,05 $ ; (c) même
  commande sans `--allowedTools` → « This command requires approval », 2 tours, 0,05 $ : `Bash(sh:*)` est nécessaire.
  Interactif (cette session, mode auto) : l'ancien motif **passe** sans refus (`PY=python`). PowerShell sans Git Bash :
  `sh` introuvable (le PATH n'a que `Git/cmd` et `Git/mingw64/bin`) et l'ancien motif y est une `ParserError` — pas
  de régression, les deux cassent pareil.
- **2026-09-17** — P2 : deux imprévus. `tache` 6 bis et `cloture.md` lançaient aussi `mesure-tokens.py` par `"$PY"` →
  le lanceur prend `mesure` en premier argument (test ajouté) ; `tache` 6 bis portait un second bloc `{ echo "$S"; … }`
  (accolade + guillemet) → `sh …/vlp sessions "$F" | … | xargs -0 sh …/vlp mesure "$S"`, même liste d'ids. Comptes :
  anciens motifs 0 ; appels au lanceur 25 ; `allowed-tools` `Bash(python3:*), Bash(python:*)` → `Bash(sh:*)` (6 skills).
- **2026-09-17** — P3 : sonde `/vlp:enchainer` en `-p` (Opus en session, chef `model: sonnet`), bac à sable à deux
  fiches (Z2 en `(visuel)`), `--allowedTools Skill`, 0,45 $ : **0** « Contains brace », **0** exit 49, **0** `python3`,
  0 refus de permission ; `sh …/scripts/vlp` passe sous `Bash(sh:*)` chez le chef (`valider`, `carte`) et dans les deux
  sous-agents (`socle`, `extraire`). Chef 14 tours, 19 appels, 0,38 $ — dont 4 appels jusqu'au second `Skill` et la carte,
  15 pour une clôture ; sous-agents 8 tours / 9 appels (0,04 $) et 6 tours / 8 appels (0,03 $). L3 : chef 9 tours / 7
  appels, sous-agents 9 et 6 tours. Surprise : le sous-agent a rendu `FAITE` sur Z2 `(visuel)` — le chef n'a pas
  demandé, il a clos (TODO n° 14). Evals Windows 3/3 (check 18, hook 2, init 21 tours ; 0,59 $). TODO n° 13 retirée.
- **2026-09-17** — Chantier P **clos**. Livré : le lanceur `scripts/vlp` (sh ; `python3`, `python`, `py` testés par `-c ""`,
  `exec` ; `mesure` lance `mesure-tokens.py` ; 4 tests) ; les 18 lancements `PY=$(for …)` et `python3 … || python …`
  remplacés par 25 appels `sh …/scripts/vlp`, `allowed-tools` → `Bash(sh:*)` ; plugin 3.3.2 ; evals Windows 3/3
  (0,59 $). Prouvé en `-p` : ancien motif refusé, lanceur passant ; sonde `/vlp:enchainer` sans refus ni exit 49.
  Laissé ouvert : sans Git Bash (PowerShell), `sh` est introuvable — l'ancien motif y cassait aussi ; le sous-agent
  rend `FAITE` sur une fiche `(visuel)` (TODO n° 14). Cadrage, P1 à P3 et clôture dans une seule session, à la
  demande. Total brut mesuré au bilan : 49 tours, 61 appels, input 98, output 42 838, cache_creation 162 143,
  cache_read 6 581 627, **total 6 786 706 tokens**, 5,98 $, plus 0,75 $ de sondes headless (4 lancements) et
  0,59 $ d'evals.
- **2026-09-17** — A2 : sonde `/vlp:enchainer` en `-p` (Opus en session, chef `model: sonnet`), bac à deux fiches (Z2 en
  `(visuel)`), `--allowedTools Skill "Bash(sh:*)"`, 0,22 $ : le sous-agent de Z2 lit la ligne `ARRÊT:` et rend **`RETOUR`**
  sans cocher ; le chef pose la question en texte et **ne clôt pas** — bac après sonde : `## Z2 [ ]` 1, `CLOS` 0,
  `CHANTIER.md` inchangé. Chef **5 tours, 4 appels** (Skill 2, Bash 1, ToolSearch 1), 254 530 tokens, 0,14 $ ; P3 : 14 tours,
  19 appels dont 15 de clôture, 0,38 $. Sous-agents Z1 6 tours / 8 appels (0,06 $), Z2 4 tours / 4 appels (0,03 $) ; P3 : 8
  et 6 tours. 0 « Contains brace », 0 exit 49. Non exercé : le verrou du chef (`FAITE` sur `(visuel)` → décocher), le
  sous-agent n'ayant pas désobéi. Evals Windows 3/3 (check 5, hook 2, init 22 tours ; 0,81 $). TODO n° 14 retirée.
- **2026-09-17** — Chantier A **clos**. Livré : `vlp.py extraire` écrit `ARRÊT: critère de fin (visuel) — livre, puis rends
  RETOUR sans cocher` sous une fiche `(visuel)` (tests 58 → 60) ; `agents/fiche.md` en fait sa règle de tête ; le contrat et
  `/vlp:enchainer` lisent `FAITE` sur une `(visuel)` en `RETOUR`, case décochée ; plugin 3.3.3 ; evals 3/3. Mesuré en `-p` :
  Z2 rendue `RETOUR`, non cochée, 0 clôture ; chef 14 → 5 tours, 19 → 4 appels, 0,38 → 0,14 $. Laissé ouvert : le verrou du
  chef n'est pas exercé (le sous-agent a obéi) ; en session interactive, la question passe par `AskUserQuestion`, non
  rejoué ; sans Git Bash, `sh` introuvable (inchangé). Cadrage, A1, A2 et clôture dans une seule session, à la demande.
  Total brut mesuré au bilan : 39 tours, 55 appels, input 82, output 27 984, cache_creation 155 030, cache_read
  5 582 393, **total 5 765 489 tokens**, 5,04 $, plus 0,22 $ de sonde headless (1 lancement) et 0,81 $ d'evals.
- **2026-09-17** — G1 : un poste Windows sans Git ne se simule pas par l'environnement (PATH sans Git, CLAUDE_CODE_GIT_BASH_PATH faux : l'outil Bash reste) ; on le simule par shell: powershell sur le hook ou la skill. Sans Git Bash, sh casse hook (exit 1, muet) et injection (skill en échec) ; la forme exec python …/vlp.py hook passe.
- **2026-09-17** — Chantier G **clos** (`26-gitbash.md`, G1..G2). Livré : preuve, par la doc et 3 sondes `-p`
  (`shell: powershell` sur un hook et une skill de bac à sable), que sans Git Bash le hook `sh` rend exit 1 sans
  rien dire au modèle et qu'une skill à `!`sh …`` échoue avant tout tour ; Git for Windows écrit requis dans
  `README.md`. Laissé ouvert : le kit sans `sh` (TODO n° 16). Total brut mesuré au bilan : 57 tours, 82 appels,
  input 114, output 44 487, cache_creation 155 316, cache_read 7 797 623, **total 7 997 540 tokens**, 6,56 $,
  plus 0,115 $ de sondes headless (5 lancements), 0 $ d'evals (non rejouées : aucun fichier chargé n'a changé).
- **2026-09-17** — W2 : le cas `tache` (V2) échouait sous Linux par sa fixture, pas par la skill — T2 dépendait de T1
  non cochée, et `/vlp:tache` s'arrête alors pour demander ; dépendance retirée, 3/3. Écrit sous Windows, jamais joué avant.
- **2026-09-17** — **Chantier W clos** (`27-wsl.md`, W1..W2) : Ubuntu 26.04.1 sous WSL2 (Claude Code 2.1.274, bubblewrap 0.11.1, socat 1.8.1.1) ; les cas d'eval wsl2 joués depuis Linux : chantier 3/3 (5 tours), tache 3/3 (4 tours) après une fixture corrigée — T2 dépendait de T1 non cochée, la skill demandait à raison ; 0,67 $ d'evals. Laissé ouvert : le kit sans `sh`
  (TODO n° 16) ; l'eval `init` reste jouée sous Windows. Total brut mesuré au bilan : 54 tours, 53 appels, input 110,
  output 26 896, cache_creation 141 808, cache_read 7 137 125, **total 7 305 939 tokens**, 5,66 $, plus 0,67 $ d'evals.
- **2026-09-17** — **Chantier X clos** (`28-sans-sh.md`, X1..X3, X3 tranchée « renoncer ») : sans `sh`, aucun nom de Python commun (Windows : `python3` = Store, exit 49 ; Ubuntu : `python3` seul) ; hook = paire exec `python3` + `py` (une erreur non bloquante de chaque côté) ; carte = `python3 … || python …` salie par le message du Store collé devant `PROJET=` (pwsh 7 et Git Bash), `py … || python3 …` propre sous pwsh 7, Git Bash et Ubuntu ; une injection dont la dernière commande échoue fait échouer la skill à 0 tour ; `shell: powershell` = pwsh 7.6.6 même ôté du PATH, 5.1 refuse `||`. Rien
  d'appliqué : tous les postes qui font tourner le kit ont déjà `sh` ; la recette est dans la TODO n° 16. Piège : Git Bash convertit `-p "/sonde"` en `C:/Program Files/Git/sonde` (`MSYS_NO_PATHCONV=1`). Total brut mesuré au bilan : 68 tours, 72 appels, input 136,
  output 64 657, cache_creation 201 370, cache_read 10 655 472, **total 10 921 635 tokens**, 8,96 $, plus 0,90 $ de sondes.
