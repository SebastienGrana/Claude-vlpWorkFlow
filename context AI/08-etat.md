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

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée,
ordonné par ce qui débloque le reste. Le détail de chacun est dans
`12-audit.md`.

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 5 | Hooks du kit | `PostToolUse` valide un fichier de fiches à l'écriture ; `SessionStart` injecte la carte ; fin des « recopie à l'identique » | 3 fiches | rien |
| 6 | Evals du plugin | `claude plugin eval` sur un bac à sable, graders gratuits, baseline sans plugin ; `validate` avant commit | 3 fiches | rien |
| 7 | Fusionner la doctrine | cinq fichiers de doc → trois ; chaque nombre vit une fois | 3 fiches | rien |
| 8 | Migrer `commands/` → `skills/` | un dossier par commande, `disable-model-invocation`, variante `context: fork` + `vlp:fiche` | 3 fiches | rien |
| 9 | `/vlp:enchainer` : réparer ou retirer | chef ≤ 3 tours par fiche via la skill forkée, ou suppression — aux chiffres de 2 | 3 fiches | 8 |
| 10 | Un projet neuf qui ne ment pas | `/vlp:init` crée ce que l'index et le routage nomment ; numéro d'état pris à la suite | 2 fiches | rien |

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
