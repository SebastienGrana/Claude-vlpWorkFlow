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
  51 à 128 tours ; la commande ne pèse que ~8 % du premier tour. Les dix
  chantiers qui en sortent sont la TODO ci-dessous.

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée,
ordonné par ce qui débloque le reste. Le détail de chacun est dans
`12-audit.md`.

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 1 | Corriger les bugs de l'audit | `/vlp:check` D honnête, `$ARGUMENTS`, page orpheline, titres, chemins `**Session**`, gabarits sans fichiers fantômes, README, `.gitignore` | 2 fiches | rien |
| 2 | Compter les tours, pondérer le coût | `mesure-tokens.py` rend tours, appels d'outils, contexte 1er/dernier tour, coût pondéré (cache ≠ frais) ; `**Session**` via `${CLAUDE_CODE_SESSION_ID}` | 5 fiches | rien |
| 3 | Réduire les tours de `/vlp:tache` | carte injectée par `` !`cat CHANTIER.md` ``, lectures groupées, corps ≤ 150 lignes, le rare en fichiers de référence | 4 fiches | 2 |
| 4 | Un script `vlp.py` pour la mécanique | extraire, socle, état, régénérer la page, valider — remplace les `sed`/`awk` et le HTML retapé par le modèle | 5 fiches | 2 |
| 5 | Hooks du kit | `PostToolUse` valide un fichier de fiches à l'écriture ; `SessionStart` injecte la carte ; fin des « recopie à l'identique » | 3 fiches | 4 |
| 6 | Evals du plugin | `claude plugin eval` sur un bac à sable, graders gratuits, baseline sans plugin ; `validate` avant commit | 3 fiches | 1 |
| 7 | Fusionner la doctrine | cinq fichiers de doc → trois ; chaque nombre vit une fois | 3 fiches | rien |
| 8 | Migrer `commands/` → `skills/` | un dossier par commande, `disable-model-invocation`, variante `context: fork` + `vlp:fiche` | 3 fiches | 3 |
| 9 | `/vlp:enchainer` : réparer ou retirer | chef ≤ 3 tours par fiche via la skill forkée, ou suppression — aux chiffres de 2 | 3 fiches | 2, 8 |
| 10 | Un projet neuf qui ne ment pas | `/vlp:init` crée ce que l'index et le routage nomment ; numéro d'état pris à la suite | 2 fiches | 1 |

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
  `**Session**`) : input 258, output 54 987, cache_creation 612 191,
  cache_read 12 363 023, **total 13 030 459 tokens**.
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
  feuille de route, au format `≈15,4M (15 389 496)` ; M reporté après coup, E
  « non mesurable ». Laissé ouvert : pas de cumul entre projets (exclu) ; une
  fiche jouée par `/vlp:enchainer` n'a pas de ligne `**Session**`, donc aucun
  coût affiché. Constat qui vaut au-delà de C : le coût affiché en fin de fiche
  est un instantané, la session consomme encore après (C1 : 4 393 030 affichés
  sur la page à la fiche, 6 406 759 mesurés à la clôture). Total brut mesuré
  sur les sessions de C1 et C2 : input 272, output 104 483, cache_creation
  372 768, cache_read 14 911 973, **total 15 389 496 tokens**.
- **2026-09-17** — T1 : sans `message.id`, `mesure-tokens.py` repère un tour
  par `requestId`, puis par sa ligne ; sur la ligne `TOTAL`, `ctx_1er` et
  `ctx_dernier` valent `-`, un contexte ne se somme pas. Mesuré sur C1 : le
  cache écrit mêle 5 min (47 978) et 1 h (26 375) — T3 ne peut pas tout
  compter au prix 1 h.
