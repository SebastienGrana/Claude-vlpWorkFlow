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

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée,
ordonné par ce qui débloque le reste. Le détail de chacun est dans
`12-audit.md`.

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 3 | Réduire les tours de `/vlp:tache` | carte injectée par `` !`cat CHANTIER.md` ``, lectures groupées, corps ≤ 150 lignes, le rare en fichiers de référence | 4 fiches | rien |
| 4 | Un script `vlp.py` pour la mécanique | extraire, socle, état, régénérer la page, valider — remplace les `sed`/`awk` et le HTML retapé par le modèle | 5 fiches | rien |
| 5 | Hooks du kit | `PostToolUse` valide un fichier de fiches à l'écriture ; `SessionStart` injecte la carte ; fin des « recopie à l'identique » | 3 fiches | 4 |
| 6 | Evals du plugin | `claude plugin eval` sur un bac à sable, graders gratuits, baseline sans plugin ; `validate` avant commit | 3 fiches | rien |
| 7 | Fusionner la doctrine | cinq fichiers de doc → trois ; chaque nombre vit une fois | 3 fiches | rien |
| 8 | Migrer `commands/` → `skills/` | un dossier par commande, `disable-model-invocation`, variante `context: fork` + `vlp:fiche` | 3 fiches | 3 |
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
