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
- **2026-09-17** — chantier J clos (TODO n° 19) : seuils des fichiers de tête dans `vlp.py` (`renvois` écrit `POIDS`), `clore` compacte
  (routage retiré, 5 derniers clos, plus de table dans `CHANTIER.md`) ; `CLAUDE.md` 118 → 80, `CHANTIER.md` 71 → 47 (plugin 3.3.6, tests 92 → 96) ;
  gain estimé ≈ 0,1 $ par session ; ouverture par `ouvrir` : 1 tour d'écriture sur 12 ; 7 579 062 tokens.
- **2026-09-17** — chantier Y clos (TODO n° 16) : le kit sans Git — hook en paire exec, carte `python3 …; py … --relais; echo fin`,
  corps en `<python> "…/vlp.py"` (`cout`, `valider --plan`, `equiper`, `lignes`), `scripts/vlp` retiré (plugin 3.4.0, tests 96 → 100) ;
  bac PowerShell sans `.git` : 0 appel `sh`, fiche cochée ; evals Windows `hook` 1/1, Ubuntu 4/4 (un run d'eval Windows
  n'accorde aucun shell : toute skill à injection se joue en `wsl2`) ; le 16 est retiré, reste le 20 ; 21 917 062 tokens.
- **2026-09-17** — chantier U clos (TODO n° 20) : `/vlp:tache` sans refus sous PowerShell — `vlp.py lire` (plus de `cat` hors projet),
  `cocher` (Session sans `$env:`), `page` sans chemin ; pas d'attente de confirmation sur un critère scriptable (les `allowed-tools`
  tombent au prompt suivant) ; carte `py …; python3 … --relais; py … --relais; echo fin` (plugin 3.4.1, tests 100 → 108) ; bac
  PowerShell : refus 9 → 1 (partie fiche 0) ; evals Windows `hook` 1/1, Ubuntu 4/4 ; laissé ouvert : 5.1 non sondable avec `pwsh` 7,
  macOS, `/vlp:enchainer` sans Git (TODO n° 21) ; 15 933 829 tokens.

- **2026-09-17** — chantier Q clos (TODO n° 21) : `/vlp:enchainer` sans Git — `agents/fiche.md` prend l'outil
  `PowerShell`, lit le kit par `vlp.py lire` (plus de `cat` ni de repli `Read`), coche par `vlp.py cocher` et
  repère une ligne par `valider --plan` (plus de `grep -n`) ; les deux `ls` de `chantier` et `check` passent à
  `vlp.py lignes "<contexte>/*.md"` ; `allowed-tools` 55 → 36 entrées, 19 mortes retirées, 11 dépareillées → 0 ;
  l'étape 5 d'`enchainer` porte enfin `vlp.py lire cloture.md`. Bac PowerShell sans `.git` ni outil `Bash` :
  refus **3 → 0**, deux fiches jouées, cochées et chantier du bac clos (12 tours, 0,3526 $) ; evals Windows
  `hook` 1/1, Ubuntu 4/4. Coût mesuré : enchaîné **0,176 $/fiche** contre **0,42 $/fiche** à la main dans le même
  bac (2,4×) — mais sur fiches triviales en `-p` : en session réelle le chef part de ~78k tokens hors ratio, et un
  `RETOUR` annule le gain. Plugin 3.4.2 ; le 21 est retiré, **la TODO est vide** ; 23 753 914 tokens.

- **2026-09-17** — chantier Z clos (TODO n° 23) : une `GARDE:` au lieu d'un traceback — toute lecture d'un chemin
  venu de `CHANTIER.md` passe par `chemin_garde`/`lignes_gardees` (`vlp.py:143`), donc `clore`, `feuille`, `page`,
  `renvois` et `ouvrir` rendent `GARDE: <phrase>` et sortent 1 ; recensement de 18 couples (7 plantaient), tests
  108 → 115 sites ; `sed` retiré de `skills/tache` (une plage se lit par `Read` offset/limit, inutilisable sans Git).
  Preuve sur Cairn-VlpLib, dont la ligne « fichier de fiches courant » débordait : avant, `carte` et `feuille`
  rendent `GARDE:` et 1 ; ligne remise droite (une seule ligne, pause du chantier `C` sur sa propre puce), après
  `PROCHAINE=P6f` et `FEUILLE todo 0 · encours oui` en code 0 — **0 traceback** dans les deux jeux. Laissé ouvert :
  les 2 renvois absents et les fichiers de tête hors seuil de Cairn-VlpLib (TODO n° 22) ; le 23 est retiré,
  le 24 ouvert (bruit « Python est introuvable » du relais de la carte) ; 11 093 368 tokens.

- **2026-09-17** — `vlp.py niveau <projet>` diagnostique un projet équipé sans rien
  écrire (fiche `NIV2`). Imprévu, et ça élargit `NIV4` : la table des chantiers clos
  traîne dans `CHANTIER.md` des **cinq** projets, pas du seul Cairn-VlpLib comme le
  disait la mesure du matin. Bilans : Cairn 3 écarts · 2 avertissements, MapDecorator
  2 · 1, TrackGen 2 · 1, ProjetONZSM 2 · 0, le bac 5 · 0. L'entrée n° 22 est corrigée :
  une copie locale de `methode-chantier.md` n'est pas un écart, la méthode la tolère.

- **2026-09-18** — chantier NIV clos (TODO n° 22 et 24) : les projets équipés se remettent
  à niveau par script — `vlp.py niveau <projet>` diagnostique (renvois, poids, feuille,
  page, variables, table des clos), `--ecrire` corrige ce qui se déduit, et la carte
  injectée ne crie plus le message du Store. Les cinq passés : Cairn **3 écarts → 0**
  (`CLAUDE.md` 89 → 80, index 111 → 71, 2 renvois morts retirés, 7 chantiers clos du
  routage remplacés par un renvoi à l'index), MapDecorator **3 → 0** (`CLAUDE.md` 84 → 79,
  `mockups/TACHES-UI.md` déclaré à l'index), TrackGen **3 → 0** (`CHANTIER.md` 51 → 47),
  ProjetONZSM **3 → 0**, le bac **5 → 1 écart assumé** : `niveau` réclame la page HTML du
  chantier courant même quand `CHANTIER.md` dit « artefact du chantier : aucun », ce que
  le socle du bac impose. Deux limites laissées : le script ne retire la table des clos
  que si l'index nomme chacun de ses fichiers, et abréger un fichier de tête reste du
  jugement, donc à la main. Les 22 et 24 sont retirés, la TODO est vide ; 21 827 897 tokens.

- **2026-09-23** — chantier REP clos (TODO n° 25) : les feuilles de route ne montrent
  plus de Markdown brut ni de lien cassé. `cellule_md` convertit gras et liens, les
  chevrons d'une URL tombent à la lecture et à l'écriture, et `vlp.py niveau` compte le
  Markdown brut, puis migre les lignes closes avec `--ecrire`. Les cinq feuilles sont à
  0 · 0 · 0 ; Cairn, à 426 · 1 · 1 avant, est republiée ; les trois autres gardent leur
  page en ligne, déjà propre. Laissé ouvert, reformulé en n° 25 : la ligne `MARKDOWN`
  muette sans `--ecrire`, et la régénération qui abîme trois feuilles voisines. Coût par
  fiche, repris de git parce que la page l'a perdu (une ligne `? $` ne se relit pas) :
  REP1 2 702 105 · REP2 4 227 906 · REP3 8 584 756 · REP4 4 840 313 ; 23 126 264 tokens.
  ↳ **Recompté le 2026-09-23 par CPT4** (`vlp.py cout`, coupé aux commits de fiche,
  sous-agents compris) : REP1 3 211 466 · REP2 4 539 690 · REP3 16 480 389 · REP4
  4 889 837 · hors fiches 6 875 079 ; 35 996 461 tokens · 20,61 $. Trois causes : une fiche
  finit à son commit, non plus à sa mesure (REP2 −2 362 507, passés à REP3) ; 5 sous-agents,
  +8 161 098 (REP2 2, REP3 3) ; la clôture comptée jusqu'à son dernier commit, +4 709 099
  hors fiches — elle n'était pas dans REP4.

- **2026-09-23** — chantier CPT clos (TODO n° 31) : un coût juste, fiche par fiche.
  `vlp.py cout` et la page coupent chaque session aux commits de fiche, sous-agents
  compris, avec une ligne « hors fiches » ; `claude-opus-5-5` a son prix, une ligne `? $`
  se relit, et `mesurer` lit les chemins de 260 caractères. REP recompté : 23 126 264 →
  35 996 461 tokens (renvoi ci-dessus). Laissé ouvert : le total d'une clôture ne compte
  pas la clôture en cours, faute de commit ; un tour d'une session après le commit de sa
  fiche compte à la suivante. 19 266 526 tokens.

- **2026-09-24** — chantier SAG clos (TODO n° 32) : le sous-agent ne bute plus sur 30 tours.
  `maxTurns` 30 → 80, et un hook `PostToolUse` (`vlp.py filet`) prévient `vlp:fiche` à trois
  tours du plafond : à plafond 10, il rend `RETOUR` sur `end_turn` au lieu d'être coupé (SAG4).
  Une fiche de code enchaînée, SAG3 : 68 tours, `FAITE`, 1,53 $ — 2,08 $ avec sa reprise à la
  main — contre 4,34 $ en moyenne à la main (CPT1–4) ; le gain vient du prix de Haiku. Le
  0,176 $ de Q tient, sous-agents compris (SAG1). Laissé ouvert, reformulé en n° 32 (`FIL`) : le
  filet ne tire qu'après `Write` ou `Edit`, et reste muet au-delà de 260 caractères. Vu sans le
  traiter : le sous-agent a rendu `FAITE` sans cocher, et le chef commite sans relire la case.
  Hors total : 0,46 $ d'essais `claude -p` (SAG2 0,2789 ; SAG4 0,0884613 + 0,08854675).
  20 128 626 tokens.

- **2026-09-24** — chantier FIL clos (TODO n° 32) : le filet tire après tout outil. Une entrée
  `PostToolUse` à lui, sur tout outil, une `PostToolUseFailure` pour les échecs, et `cmd_filet`
  lit les chemins de 260 caractères et plus (FIL2). Éprouvé à plafond 10 (FIL3) : « 3 tours
  restants » juste après un `Read` réussi, puis juste après un Bash à code non nul, chacun suivi
  de `RETOUR` sur `end_turn`. Laissé ouvert : un `Read` raté déclenche-t-il `PostToolUseFailure` ?
  Un appel refusé avant de s'exécuter n'en déclenche aucun (doc) ; le préfixe `\\?\` n'est éprouvé
  que par test, les essais tenant en 254 caractères. Vu sans le traiter : « Python est
  introuvable » vient désormais après **chaque** appel d'outil, 7 pour 7 dans chaque essai (n° 39
  `PYT`) ; le `CLAUDE.md` de l'utilisateur est chargé dans le sous-agent, sa jauge comprise.
  Hors total : 0,3125 $ d'essais `claude -p` (FIL3 0,14800575 + 0,06411505 + 0,10040705).
  42 638 103 tokens.

- **2026-09-24** — chantier CAS clos (TODO n° 38) : le chef relit la case avant de commiter.
  `vlp.py cocher --verifier` n'écrit rien et rend `CASE <fiche> [x]` (sort 0) ou `CASE <fiche> [ ]`
  (sort 1) ; tests 200 → 203 `verifier(`. La puce `FAITE` de `/vlp:enchainer` s'en sert et lit un
  `RETOUR` sur une case vide ; le contrat (`enchainement.md`) le dit. Imprévu, `CAS1` : le
  sous-agent a commité lui-même — son contexte porte le `CLAUDE.md` de l'utilisateur, qui demande
  un commit par tâche (cause probable, pas prouvée) ; `agents/fiche.md` le lui interdit depuis
  `CAS2`, pas encore éprouvé. Dans `CAS2`, la fiche disait « Tu ne commites pas » : aucun commit.
  Cadré et joué seul, la nuit, l'utilisateur dormant. 10 041 615 tokens.
- **2026-09-24** — chantier VAL clos (TODO n° 34) : le contrôle avant commit ne se saute plus.
  Sans `claude` dans le PATH, `.githooks/pre-commit` prend le `claude.exe` de l'app (la plus haute
  version, `sort -V`) et valide vraiment les deux manifestes ; un `plugin.json` réduit à `{` refuse
  le commit (code 1). Le hook prend 1 755 · 1 846 · 1 948 ms au lieu de 147 ms. Imprévu : la règle
  de CAS a servi dès la fiche suivante (`FAITE`, case vide, lue comme un `RETOUR`) ; le sous-agent
  a encore commité, poussé cette fois par le critère — un clone prend le hook de `HEAD`. Cadré et
  joué seul, la nuit. 5 647 906 tokens, recomptés par plage : `vlp.py cout` en rend 17 185 705,
  CAS compris, car son « hors fiches » part du début de la session.

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée,
ordonné par ce qui débloque le reste, cité par son code. Le détail de chacun
est dans `38-audit-artefacts.md` § 4, qui les nomme A à F ; les rangs 1 à 24,
tous retirés, venaient de `12-audit.md` ; 31 à 34, de la clôture de `REP` ; 35 à
37, de celle de `CPT` ; 38 à 41, de celle de `SAG` ; 42, de `FIL1` ; 43 à 47, de celle de `FIL`.

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 33 | `TAR` — Un test aller-retour par format écrit | Deux fois le même défaut dans `REP` : les chevrons d'une URL (`REP2`), puis la ligne `? $` (`CPT`) — `vlp.py` écrit un format qu'il ne sait pas relire. Un test écrit puis relit chaque format : ligne de coût, ligne close, rang de TODO, zone « en cours ». | ~2 fiches | — |
| 35 | `FIN` — Le coût juste jusqu'à la clôture | Trois bords vus à la clôture de `CPT`. Le total gardé au bilan ne compte pas la clôture, faute de commit au moment de la mesure (`CPT` : 19 266 526 sans elle). La page close garde le coût de sa dernière fiche mesuré avant son commit : `CPT4` y affiche 5 087 135, 6 048 820 au commit. Un tour joué dans une session après le commit de sa fiche compte à la suivante (`CPT4` : 30 tours à la mesure, 28 dans sa session). Piste : à la clôture, `cout` compte hors fiches jusqu'au bout du transcript, et `clore` régénère les coûts de la page. | ~2 fiches | — |
| 36 | `EST` — L'estimé face au réel, à chaque clôture | La TODO estime chaque chantier ; rien ne compare ensuite. `CPT`, estimé « ~2 fiches », en a joué 4. Le bilan de clôture écrira l'estimé à côté du réel — fiches jouées, tokens —, pour que `/vlp:chantier` estime mieux les suivants. | ~1 fiche | — |
| 37 | `RCP` — Recompter les chantiers clos au coût juste | Le total de la feuille de route (339 340 811 tokens, 29 clos) additionne des bilans comptés avant `CPT` : sans sous-agents ni découpe aux commits ; seul `REP` est recompté (`CPT4`). `vlp.py cout` recomptera les clos qui ont des lignes `**Session**` et dont les transcripts restent sur le disque ; chaque ancien chiffre reste, marqué (énoncé renversé, `methode-chantier.md`). 🟡 Combien de transcripts restent : pas vérifié. Après `FIN`, pour ne recompter qu'une fois. | ~2 fiches | `FIN` |
| 39 | `PYT` — Plus d'erreur « Python est introuvable » à chaque appel d'outil | Sous Windows, les entrées `python3` de `hooks/hooks.json` échouent à chaque appel d'outil du sous-agent depuis `FIL2` : une `hook_non_blocking_error` « Python est introuvable » par appel — 7 pour 7 dans chaque essai `FIL3`, `PostToolUseFailure` compris —, deux par écriture (essai `SAG4`, l. 62-63 de sa transcription). 🟡 Le modèle les lit-il ? Pas vérifié. Faire taire l'entrée qui échoue sans perdre la paire `python3` + `py`. | ~1 fiche | — |
| 40 | `MTK` — `mesure-tokens.py` : une docstring, et la plage en ligne de commande | Le socle de `SAG` renvoie à « sa docstring » pour la syntaxe : il n'en a pas, seulement une ligne `usage`. Sa ligne de commande n'expose pas la plage que `mesurer()` accepte : la reprise de `SAG3` s'est mesurée par un `py -c` d'une ligne entière (journal du 2026-09-24). Deux bornes, heures ou commits. | ~1 fiche | — |
| 41 | `PER` — Marquer `34-agent-sans-git.md:56`, périmé depuis `CPT2` | Relevé par `SAG1` : la ligne dit que `mesure-tokens.py` ne compte pas les sous-agents ; il les compte depuis `CPT2`. Un énoncé renversé se garde, marqué (`methode-chantier.md`) : un renvoi vers `CPT2`, pas un effacement. | ~0,5 fiche | — |
| 42 | `OUV` — Le coût d'une fiche, mesuré avant son commit | À l'étape 6 bis, `/vlp:tache` mesure avant de commiter. Sans commit de fiche plus ancien dans la session, `cout` ne découpe rien et rend la session entière : 139 tours · 17,34 $ pour `FIL1`, jouée sans `/clear` après le cadrage ; une fois son commit posé, 17 tours · 2,73 $ (journal du 2026-09-24). La page publiée « faite » montre la session entière jusqu'à sa régénération suivante. Faute du commit de la fiche, compter depuis le dernier commit de la session — ou depuis le message `/vlp:tache <fiche>`. | ~1 fiche | — |
| 43 | `RAT` — Un `Read` raté réveille-t-il le filet ? | Reste de `FIL` : le filet tire après un `Read` réussi et après un Bash à code non nul (`FIL3`), mais un `Read` sur un fichier absent n'est pas éprouvé. La doc range dans `PostToolUseFailure` l'outil lancé qui échoue, pas l'appel refusé avant de s'exécuter (journal du 2026-09-24). S'il n'en déclenche aucun, des derniers tours de `Read` ratés laissent le sous-agent coupé muet. Un essai à plafond 10, comme `FIL3` (≈ 0,1 $). | ~0,5 fiche | — |
| 44 | `GLO` — Le `CLAUDE.md` de l'utilisateur dans le sous-agent | Vu dans `FIL3` : `vlp:fiche` reçoit le `CLAUDE.md` global de l'utilisateur (attachment `instructions`) et en suit la forme — son dernier message finit par la jauge « ⚠️ Imprévu — … ». 🟡 Ce qu'il pèse par sous-agent, et s'il peut déplacer le mot de statut que lit le chef : pas mesuré. Mesurer d'abord ; n'agir que si ça coûte. | ~0,5 fiche | — |
| 45 | `BAC` — Un bac d'essai par script | `SAG4` et `FIL3` ont rebâti leur bac à la main — `CHANTIER.md`, fiches factices, fichiers —, puis compté la transcription du sous-agent par un script jetable. `FIL3` y a buté deux fois : la section `## L'ordre des fiches` exigée par le hook, et « un appel par tour », lu par Haiku comme « par exécution » (0,148 $ perdus). `vlp.py` posera le bac en un appel, et comptera la transcription : tours, avertissements du filet et l'outil qui les précède, `hook_non_blocking_error`, premier mot et `stop_reason` du dernier message. Le lancement `claude -p` reste à la main, chiffré avant. | ~1 fiche | — |
| 46 | `EVF` — Le filet en eval rejouable | Les deux essais de `FIL3` en eval du plugin (chantier `V`) : un changement de `hooks/hooks.json` ou de `vlp.py filet` se reprouve en un appel, ≈ 0,16 $ le passage (0,06411505 + 0,10040705). 🟡 Qu'un eval lise la transcription d'un sous-agent : pas vérifié. | ~2 fiches | `BAC` |
| 47 | `ESS` — Les essais `claude -p` dans le coût | Un essai `claude -p` tourne dans une autre session, que `cout` ne voit pas : il s'ajoute à la main, « hors total ». Au moins 14 chantiers clos en portent — 12 sur la feuille de route, `SAG` et `FIL` au fichier d'état —, ≈ 12,32 $ absents de tout total (somme faite à la main). `cout` ira chercher les sessions des bacs lancées pendant la fiche. 🟡 Les relier à leur fiche — dossier du bac, heure —, et le sort des evals : à trancher au cadrage. Même but que `FIN`, autre mécanisme. | ~1 fiche | — |
| 25 | `VOI` — Finir les feuilles voisines, reste de `REP` | Ce que `REP` a laissé. La ligne `MARKDOWN` de `vlp.py niveau` compte, sans `--ecrire`, la page régénérée au lieu de celle du disque : elle ne voit ni la TODO ni la zone « en cours ». La régénération abîme trois feuilles voisines : TODO de MapDecorator hors table, donc lue vide ; lettres de fiche entre backticks ignorées ; source de TrackGen sans accents. Une fois corrigées, republier MapDecorator, TrackGen et ProjetONZSM. Détail : journal du 2026-09-23. | ~3 fiches | — |
| 26 | `ABR` — Mettre notes et journal à l'abri dans un `.md` | Les notes et le journal d'une page de chantier n'existent aujourd'hui que dans la page. `page --note` et `--journal` écriront d'abord le texte entier dans un `.md`, et la page le recopiera. | ~3 fiches | — |
| 27 | `ALE` — Essai : alléger la republication | Deux pistes, mesurées : le CSS en fichier joint, puis les données dans la base de claude.ai. Décide où vivent le CSS et les données avant `PLI` et `FEU`. | 2 fiches | `ABR` |
| 28 | `PLI` — La page de chantier plus courte et lisible | Chaque fiche dans un bloc repliable, le journal replié sauf ses dernières entrées, le bilan en haut d'un chantier clos. Rien n'est coupé : replié, le texte reste dans la page. | ~5 fiches | `ABR`, `ALE` |
| 29 | `FEU` — La feuille de route plus courte et lisible | La TODO en cartes, le détail replié, un sommaire. 🟡 Une décision à prendre : la feuille garde-t-elle tout le détail de la TODO ? | ~4 fiches | `VOI`, `ALE` |
| 30 | `BTN` — Des boutons, en dernier | Commenter une fiche, tout déplier, filtrer, copier la commande d'une fiche, un graphique des coûts. Optionnel. | ~4 à 6 fiches | `PLI`, `FEU` |

## Journal des décisions

Une ligne par décision imprévue tranchée en cours de fiche — jamais un résumé
de ce que le code dit déjà.

- **2026-09-24** — FIN1, relue par le chef : `FAITE` **sans cocher** (aucun `cocher` en 24
  appels), dernier message ouvert par « Excellent ! » et fermé par un « En résumé » à jauge, la
  forme du `CLAUDE.md` de l'utilisateur (n° 44 `GLO`) ; aucun commit, le critère n'en demandait
  pas. Deux défauts. La fin prenait le `max` des commits suivants, pas le premier : une mention
  tardive du préfixe aurait encore étiré la plage — le critère sur VAL ne pouvait pas le voir, un
  seul commit y suit `VAL1`. Ses quatre tests ne vérifiaient que la forme de `heures_commits` (un
  triplet), aucune borne. Reprise du chef : `min`, code et docstrings récrits ; sept tests, six
  de `plages` en fonction pure et un `cout` de bout en bout ; deux mutants (`max`, origine ôtée)
  font chacun échouer un test. Leçon de cadrage : une fiche de code nomme ses tests et leurs
  valeurs attendues, sinon Haiku en écrit de creux. 27 `hook_non_blocking_error` pour 24 appels.
  Transcription : `1ba64929-8274-42d4-93bb-a2d22fbdd600/subagents/agent-a96aea95a4119f835.jsonl`.

- **2026-09-24** — VAL1, relue par le chef : le sous-agent rend `FAITE` **case vide** ; la règle
  de CAS l'attrape (`CASE VAL1 [ ]`, code 1) et le chef la lit comme un `RETOUR`. Il **commite
  encore** (`72035f2`, « VAL1: » sans espace, que `COMMIT_FICHE` ne voit pas), cette fois à cause
  du critère : « le clone récupère une version non modifiée du hook. Je dois committer d'abord »
  (appel 19 sur 26). Un critère joué dans un clone teste `HEAD` : il doit dire d'y copier le
  fichier modifié. La règle « aucun commit » de `agents/fiche.md` n'a pas joué : 0 occurrence
  dans la transcription, le plugin reste en cache jusqu'à `/reload-plugins`. Reprise du chef :
  `claude_exe=` initialisé, le commentaire dit pourquoi `sort -V`, message « ni dans le PATH ni
  dans l'app », README replié ; commit refait au format `VAL1 :`. Le refus nomme
  `marketplace.json` alors que seul `plugin.json` est cassé : la validation du premier échoue
  aussi. Durées : 1 755 · 1 846 · 1 948 ms, contre 147 ms quand tout était sauté.
  28 `hook_non_blocking_error` pour 26 appels (n° 39 `PYT`). Transcription :
  `1ba64929-8274-42d4-93bb-a2d22fbdd600/subagents/agent-ab869d46397c611ec.jsonl`.

- **2026-09-24** — CAS1, relue par le chef : le sous-agent rend `FAITE`, case cochée, mais
  **commite lui-même** (`85f5efc`, « Maintenant je crée le commit. », 27ᵉ appel sur 27), quand la
  méthode réserve le commit au chef. Son contexte porte le `~/.claude/CLAUDE.md` de l'utilisateur
  (attachment `instructions`, 12 935 caractères), qui demande un commit après chaque tâche : cause
  probable, pas prouvée. Sa puce `FAITE` de `skills/enchainer/SKILL.md` tient sur une ligne de
  414 caractères (la plus longue avant : 222) et perd trois choses : le renvoi à
  `methode-chantier.md`, « le sous-agent ne commite jamais », `(vlp.py carte)`. Vu aussi :
  33 `hook_non_blocking_error` « Python est introuvable » pour 27 appels (n° 39 `PYT`). D'où
  `CAS2`. Transcription : `1ba64929-8274-42d4-93bb-a2d22fbdd600/subagents/agent-a10d85004cb7139db.jsonl`.

- **2026-09-24** — FIL3 : le filet **tire** après un `Read` réussi et après un Bash à code non nul,
  à plafond bas. `claude.exe` 2.1.280 de l'app, dans le bac `f3` du scratchpad (`CHANTIER.md`, deux
  fiches factices : `F1` douze `Read`, `F2` douze `exit 3`) ; `maxTurns` 80 → 10 le temps des
  essais, remis à 80 (`Read` de `agents/fiche.md:6`, `git diff` vide). Commande de SAG4 :
  `claude -p "Appelle l'outil Skill avec skill \"vlp:jouer\" et args \"F1\", puis recopie son
  resultat tel quel. Rien d'autre." --model haiku --max-budget-usd 1 --permission-mode acceptEdits
  --allowedTools "Skill" --output-format stream-json --verbose` ; pour `F2`, `"F2"`,
  `--allowedTools "Skill" "Bash"` et `< /dev/null`. Coût réel 0,3125 $, 0 refus : 0,14800575 (premier essai raté),
  0,06411505 (`F1`), 0,10040705 (`F2`). Comptes par message.id porteurs d'`usage` et attachments.
  `F1` (`0045d27f-a411-4e70-8344-bdf4c15cec1e/subagents/agent-a8139dad1034ad64a.jsonl`) : 8 tours,
  7 appels (2 `PowerShell`, 5 `Read`) ; averti après le tour 7, `Read` de `n05.txt` réussi (sans
  `is_error`, « fichier 05 »), par `PostToolUse:Read` (l. 54) : « Attention : 3 tours restants.
  Rends ton statut maintenant — RETOUR avec ce qui est fait et ce qui reste, si la fiche n'est pas
  finie. » ; 1 avertissement en tout ; 7 `hook_non_blocking_error` pour 7 appels ; dernier message
  `RETOUR`, `end_turn`, dernière ligne : « ⚠️ Imprévu — tourner limité, fiche inachevée. J'ai lu
  cinq fichiers sur douze, dans l'ordre requis. Sept restent à lire (n06.txt à n12.txt), un
  message à la fois. » — la jauge du `CLAUDE.md` de l'utilisateur, chargé dans le sous-agent.
  `F2` (`707b23a4-8f0b-4d1b-9101-b70c64f73bb4/subagents/agent-a6a58391ed52b8c54.jsonl`) : 8 tours,
  7 appels (1 `Bash` de mise en route, 6 `exit 3`) ; averti après le tour 7, `exit 3` à `is_error`
  vrai (« Exit code 3 »), par `PostToolUseFailure:Bash` (l. 59), même texte ; 1 avertissement en
  tout ; 7 `hook_non_blocking_error` pour 7 appels (1 `PostToolUse:Bash`, 6
  `PostToolUseFailure:Bash`) ; dernier message `RETOUR`, `end_turn`, dernière ligne : « RETOUR —
  Appel 6/12 complété (code 3 reçu). Fiche F2 incomplète : 6 appels restants sur 12. La fiche
  demande douze appels `exit 3` successifs, un par message, chacun retournant le code 3. Continue
  avec les appels 7 à 12. » Imprévu : écrite « un `Read` par tour », `F1` a d'abord rendu
  `RETOUR — Tour 1/12` après un seul `Read` (3 tours) — Haiku lit « tour » comme une exécution ;
  « un appel par message, d'affilée, dans cette même exécution » a suffi. Sans `< /dev/null`,
  `claude -p` attend 3 s une entrée. Chemins : 254 caractères, sous les 260 du préfixe `\\?\`,
  que ces essais n'éprouvent pas. Reste ouvert : un `Read` raté déclenche-t-il `PostToolUseFailure` ?
- **2026-09-24** — Après FIL2, choix de l’utilisateur : l’essai 2 de `FIL3` échoue par un Bash à
  code non nul (`exit 3`), le déclencheur documenté de `PostToolUseFailure`, et non plus par un
  `Read` sur un fichier absent, qui n’en déclenche peut-être aucun ; `Bash` en plus dans
  `--allowedTools`, car un refus de permission n’en déclenche aucun non plus. Coût inchangé,
  ≈ 0,18 $. Reste ouvert : un `Read` raté déclenche-t-il `PostToolUseFailure` ?
- **2026-09-24** — FIL2, doc de `PostToolUseFailure` ([Hooks reference](https://code.claude.com/docs/en/hooks),
  lue le 2026-09-24) : il part quand un outil déjà lancé échoue — exception, erreur MCP, Bash ou
  PowerShell à code non nul ; son entrée porte `tool_name`, `tool_input`, `error`, `is_interrupt`,
  `duration_ms` et les champs communs, dont `agent_id` et `agent_type` dans un sous-agent ; sa
  sortie rend `additionalContext` au modèle sous la même forme que `PostToolUse`, au nom
  `PostToolUseFailure`. Imprévu : un appel refusé **avant** de s’exécuter — outil inconnu, schéma
  ou validation propre à l’outil, permission refusée — ne déclenche aucun hook d’outil. Un `Read`
  sur un fichier absent en est peut-être (non vérifié) : l’essai 2 de `FIL3`, « sans aucun
  fichier », risque un faux « filet muet » ; un Bash à code non nul est le déclencheur documenté.
- **2026-09-24** — FIL2, mesures : filet à vide, 5 fois (`echo {} | py scripts/vlp.py filet`,
  boucle `date +%s%N` sous Git Bash) — avant (FIL1) 327 · 328 · 300 · 316 · 298 ms, après
  324 · 307 · 311 · 346 · 311 ms, médianes 316 et 311 : rien de mesurable. Dans un sous-agent
  (transcript factice de 60 tours) : 318 · 319 · 319 · 312 · 309 ms avant, 320 · 329 · 323 ·
  323 · 378 après, médianes 318 et 323 — +5 ms, cause non isolée. Tests : « OK », code 0, trois
  de plus ; chaque correction cassée exprès fait tomber le sien, code 1 — filet remis sur
  `Write|Edit`, nom d’événement figé à `PostToolUse`, `open` sans préfixe (280 caractères).
  Piège : un arbre de plus de 260 caractères laissé par un test en échec fait planter le
  nettoyage de `TemporaryDirectory` (WinError 145) et cache la ligne `ÉCART` — d’où le `rmtree`
  préfixé dans un `finally`.
- **2026-09-24** — FIL1, coût, corrigé : le commit `FIL1 :` posé, `cout` coupe bien — 17 tours ·
  2,73 $ pour FIL1 (de l’ouverture `f694a99` au commit `174ffb1`, dont les 4 tours qui ont suivi
  l’ouverture), 195 tours · 16,13 $ hors fiches. Les 139 tours · 17,34 $ ne valaient qu’avant le
  commit, à l’étape 6 bis de `/vlp:tache` : c’est ce défaut que décrit la TODO n° 42.
- **2026-09-24** — Après FIL1, choix de l’utilisateur : le trou des échecs (`PostToolUseFailure`)
  est plié dans `FIL2` — la doc d’abord, une entrée de plus, un test — et dans `FIL3` : deux
  essais, ≈ 0,18 $, car le premier avertissement fait rendre `RETOUR` et un essai ne prouve
  qu’un cas ; le second sans aucun fichier, la mise en route de `SAG4` ayant pris 4 tours. La
  découpe de `cout` à l’ouverture va en TODO, n° 42 `OUV`.
- **2026-09-24** — FIL1, coût : `cout` ne trouve aucun commit de fiche avant `FIL1` et compte à
  FIL1 la session entière — SAG4, SAG5, clôture de SAG, cadrage de FIL : 139 tours · 17,34 $.
  FIL1 seul, de `/vlp:tache FIL1` à la mesure (00:42:28 → 00:51:35, +02:00) : 10 tours ·
  1 578 463 tokens · 2,08 $, par `mesurer()` sur la plage, comme SAG5. ~158k tokens par tour
  (1 578 463 ÷ 10), contre 69 917 au premier tour de la session : session non vidée.
  Corrigé le jour même, plus haut : « FIL1, coût, corrigé ».
- **2026-09-24** — FIL1 : les trois inconnues de `FIL` tranchées, et un trou de plus ; rien ne
  change dans le kit. Doc officielle, https://code.claude.com/docs/en/hooks, lue ce jour par
  WebFetch, puis revérifiée par `grep` sur la page brute (`…/hooks.md`) ; Claude Code 2.1.280.
  - **Tout outil** : la table des `matcher` donne `"*"`, `""` ou le matcher omis. ➡️ `FIL2`
    prend l'une des trois ; `"*"` se lit et se teste le mieux (proposé).
  - **En parallèle** : « All matching hooks run in parallel. » La sonde `claude -p` n'a pas
    servi : 0 $. ➡️ Aucun ordre à tenir entre l'entrée du filet et celle de `hook`.
  - **Chemin long** : Python 3.14.6, `LongPathsEnabled` = 0 (registre, lu seulement). Fichier
    créé par le préfixe dans le scratchpad, à 259, 260 et 280 caractères. À 259 : `isfile`
    True, `open` lit. À 260 et 280 : `isfile` False, `open` FileNotFoundError, `ouvrir` lit, et
    `isfile` préfixé True. Le seuil `>= 260` d'`ouvrir` est juste, au caractère près.
    ➡️ Le garde `os.path.isfile` de `cmd_filet` rend le filet muet **avant** toute lecture :
    `FIL2` préfixe le test d'existence, pas seulement la lecture. Ma première sonde a reçu le
    préfixe avec une barre de moins, et a planté : dans le test, le bâtir par `chr(92)` (proposé).
  - **Filet à vide**, référence d'avant `FIL2` : 327 · 328 · 300 · 316 · 298 ms (ouverture :
    332 · 320 · 310 · 292 · 318).
  - **Imprévu** : un appel d'outil qui échoue lance `PostToolUseFailure`, un événement à part
    (table des événements, même page). 🟡 Que `PostToolUse` se taise alors n'y est pas écrit en
    toutes lettres, ni qu'`additionalContext` passe après un échec : le filet « tout outil »
    resterait muet après un `Edit` raté. À trancher avant `FIL2`.
  Rejouer depuis la racine du kit — les temps :
  ```bash
  for i in 1 2 3 4 5; do s=$(date +%s%N); echo {} | py scripts/vlp.py filet >/dev/null; e=$(date +%s%N); echo $(( (e-s)/1000000 )); done
  ```
  La sonde, `py sonde.py <dossier court>` → `259 True True ok ok`, puis pour `260` et `280` :
  `False True FileNotFoundError ok`.
  ```python
  import os, sys, importlib.util as iu
  s = iu.spec_from_file_location("mt", "scripts/mesure-tokens.py"); mt = iu.module_from_spec(s); s.loader.exec_module(mt)
  B = chr(92); PREFIXE = B + B + "?" + B                    # le prefixe long, sans echappement
  d = os.path.join(os.path.abspath(sys.argv[1]), "long"); os.makedirs(d, exist_ok=True)
  for n in (259, 260, 280):                                 # n · isfile · isfile prefixe · open · ouvrir
      p = os.path.join(d, "f" * (n - len(d) - 5) + ".txt")  # len(p) == n
      with open(PREFIXE + p, "w", encoding="utf-8") as f: f.write("ok")
      try: brut = open(p, encoding="utf-8").read()
      except OSError as e: brut = type(e).__name__
      print(len(p), os.path.isfile(p), os.path.isfile(PREFIXE + p), brut, mt.ouvrir(p).read())
  ```
- **2026-09-24** — SAG5 : sur une fiche de code, `/vlp:enchainer` coûte **moins** qu'à la main.

  | Mesure | $ par fiche | Tokens par fiche | Tours par fiche | Fin |
  |---|---|---|---|---|
  | Q recompté (`SAG1`) — 2 fiches triviales, chef Sonnet en `claude -p` | 0,176 $ (0,3525749 ÷ 2) | 293 226 (586 452 ÷ 2) | 12 (24 ÷ 2 : chef 12, Z1 6, Z2 6) | `end_turn` ×2, `FAITE` |
  | `SAG3` enchaînée — fiche de code, chef Opus 5.5 | 1,53 $ (chef 0,56 + sous-agent 0,97) ; 2,08 $ avec la reprise à la main (0,55 $) | 7 355 914 ; 8 713 375 avec la reprise | 73 (chef 5, sous-agent 68) ; 78 avec la reprise | `end_turn`, `FAITE` sans cocher |
  | CPT à la main — 4 fiches de code, Opus 5.5 | 4,34 $ en moyenne (2,80 · 4,61 · 5,02 · 4,93) | 4 816 632 en moyenne (19 266 526 ÷ 4) | 29,25 en moyenne (16 · 32 · 35 · 34) | commit, sans plafond |

  Verdict : oui — 2,08 $ reprise comprise, contre 4,34 $ en moyenne et 2,80 $ au mieux à la main,
  mais en 1,8 fois plus de tokens et 2,7 fois plus de tours : le gain vient du prix de Haiku, pas
  d'un travail plus court. Commandes : `py scripts/vlp.py cout "context AI/41-plafond-sous-agent.md"`
  (SAG3), `py scripts/vlp.py cout "context AI/40-cout-juste.md"` (CPT),
  `py scripts/mesure-tokens.py a7de44ba-a760-4634-b947-8c38f7fe25e8` (Q) ; la reprise, que `cout`
  range dans SAG4, par `mesurer()` sur la plage des commits `ac67aaa` → `a6c4453` — la ligne de
  commande de `mesure-tokens.py` n'expose pas la plage :

  ```
  py -c "import importlib.util as u,datetime as d;s=u.spec_from_file_location('m','scripts/mesure-tokens.py');m=u.module_from_spec(s);s.loader.exec_module(m);t=lambda x:d.datetime.fromisoformat(x).timestamp();r=m.mesurer(m.resoudre('1cba232a-94a5-4599-9fce-b381f08f8a01')[0],(t('2026-09-23T23:57:57+02:00'),t('2026-09-23T23:59:23+02:00')))[0];print(r['total'],r['tours'],r['usd_exact'])"
  ```

  → `1357461 5 0.5482118`. Réserves : une seule fiche enchaînée, autre que celles de CPT ; le chef
  de SAG3 et la reprise tournaient dans une session déjà lourde (≈255 k et ≈271 k tokens par
  tour), plus chère qu'une session neuve. **`maxTurns` reste à 80** : SAG3 a pris 68 tours, 12 de
  marge ; la règle de SAG2, plus haut compte + 20 %, donnerait 81,6 — deux tours, sous ce qu'une
  seule mesure distingue —, et depuis SAG4 le plafond atteint rend un `RETOUR`, pas une coupe
  muette. `SAG1` n'a démenti aucun chiffre : `35-bilan.md:107`, `CLAUDE.md:16` et la mémoire
  citent 0,176 $ et 0,42 $, confirmés tous deux — rien à corriger.

- **2026-09-24** — SAG4 : le filet **tient** à plafond bas. Essai `claude -p` 2.1.280 dans `b4`,
  copie du bac `bacq4b` de Q, fiche factice `F1` (douze fichiers, un outil par tour) ;
  `maxTurns` 80 → 10 le temps de l'essai, remis à 80 (`git diff` vide, `Read` de
  `agents/fiche.md:6`). Commande : `claude -p "Appelle l'outil Skill avec skill \"vlp:jouer\" et
  args \"F1\", puis recopie son resultat tel quel. Rien d'autre." --model haiku --max-budget-usd 1
  --permission-mode acceptEdits --allowedTools "Skill" --output-format stream-json --verbose`.
  Coût réel 0,0885 $ (`total_cost_usd` 0,08854675), 0 refus ; une première tentative sans
  `--allowedTools "Skill"` : `Skill` refusé, aucun sous-agent, 0,0884613 $. Transcription
  `072a491d-cb45-44f1-baba-a59a264a7d0e/subagents/agent-a6ac4da4bd223d228.jsonl` (9 tours) :
  après le tour 8, `Write` de `n04.txt`, `hook_additional_context` (l. 65) « Attention : 2 tours
  restants. Rends ton statut maintenant — RETOUR avec ce qui est fait et ce qui reste, si la
  fiche n'est pas finie. » ; tour 9, `end_turn`, dernier message, ligne 1 : « RETOUR — Quatre
  fichiers écrits (n01.txt à n04.txt, chacun contenant son numéro). Il en reste huit (n05.txt à
  n12.txt). La fiche demande un seul appel d'outil par tour avec Read avant chaque Write ; cette
  structure nécessite 23 tours au total (1 Write initial + 11 paires Read/Write pour les fichiers
  restants). Deux tours m'attendent encore. », dernière ligne : « À faire : n05.txt à n12.txt. »
  Constats : le matcher `Write|Edit` ne réveille le filet qu'après une écriture — averti à 2 tours
  restants, pas 3, le tour 7 étant un `Read` ; chaque écriture rend deux `hook_non_blocking_error`
  « Python est introuvable » (l. 62-63, les entrées `python3`) ; chemin de 254 caractères, sous
  les 260 où `cmd_filet`, sans préfixe `\\?\`, resterait muet ; `vlp:jouer` est
  `user-invocable: false` : le « `/vlp:jouer SAG3` » de SAG2 passe en fait par l'outil `Skill`.

- **2026-09-23** — SAG3, témoin (`/vlp:jouer SAG3` après `/reload-plugins`) : le sous-agent
  rend `FAITE` en **68 tours**, fin sur `end_turn` — l'ancien plafond de 30 l'aurait coupé —,
  mais **sans cocher** : 0 appel à `cocher` sur 70 appels d'outils
  (`agent-a125a875d7a93dc39.jsonl`), fin sur des vérifications `py -c` improvisées. Le chef,
  qui commite sur `FAITE` sans relire la case (`skills/enchainer/SKILL.md:68`), a commité
  `SAG3 :` (`ac67aaa`) case vide ; cochée ensuite à la main. Coût, coupé au commit : sous-agent
  6 080 121 tokens · 0,97 $, chef 5 tours · 0,56 $, fiche 1,53 $
  (`py scripts/vlp.py cout "context AI/41-plafond-sous-agent.md"`). `test-vlp.py` « OK »,
  `plugin validate` passed.

- **2026-09-23** — SAG2 : un hook **atteint** le sous-agent. Doc, lue ce jour : un hook de
  plugin tourne dans le sous-agent, entrée marquée `agent_id` et `agent_type`
  (https://code.claude.com/docs/en/hooks) ; le `hooks` du frontmatter est « Ignored for plugin
  subagents » (https://code.claude.com/docs/en/sub-agents) — d'où `hooks/hooks.json`. Essai :
  `claude -p` 2.1.280, copie `vlpt` du plugin dans le scratchpad, hook `PostToolUse` qui injecte
  un mot absent du prompt ; 0,2789 $ (estimé 0,15), 0 refus. Le hook tire sur le `Read` du
  sous-agent (`agent_type` = `vlpt:fiche`) ; sa transcription
  `c14a8967-daef-4383-8cae-d7f63942ade2/subagents/agent-ac58853b89865a0e4.jsonl` porte
  `hook_additional_context` (l. 13), puis la réponse de Haiku : « ORNITHORYNQUE-SAG2 » (l. 19).
  `transcript_path` est celle du chef. **`maxTurns` 30 → 80** : 66 tours, le plus haut compte
  connu à la main (`CLAUDE.md`), + 20 % = 79,2 ; quatre des cinq sous-agents de REP, coupés à
  30, n'avaient pas fini. SAG3 seule : `/vlp:enchainer` ne se borne pas (argument : rien ou un
  alias ; plafond 5 fiches), donc, dans une session neuve ou après `/reload-plugins`,
  `/vlp:jouer SAG3` — le maillon que l'enchaîneur appelle —, puis le commit `SAG3 : …` qu'il
  ferait (`skills/enchainer/SKILL.md:68`). Coût estimé : 0,3 à 1,1 $ de Haiku — 30 à 80 tours
  à 0,010–0,014 $, le prix par tour des sous-agents de REP
  (`py scripts/mesure-tokens.py da8e3b04-adf4-426a-a7b1-3087bacb5724`) —, plus le chef.

- **2026-09-23** — SAG1 : `total_cost_usd` **compte les sous-agents**, et le 0,176 $ de Q
  tient. Doc : « Included. Counts subagent requests alongside the top-level loop » — table
  de https://code.claude.com/docs/en/agent-sdk/cost-tracking, lue ce jour ; `usage` seul les
  exclut. Brut (`q4b.jsonl`, scratchpad de la session Q `d3864b7b`, `Q4` passe 2) :
  `modelUsage` Sonnet 0,2363536 $ + Haiku 0,1162213 $ = `total_cost_usd` 0,3525749 $.
  Recompte : `py scripts/mesure-tokens.py a7de44ba-a760-4634-b947-8c38f7fe25e8` — chef
  419 221 tokens, `Z1` 72 273, `Z2` 94 958, TOTAL 586 452 ; affiché 0,24 · 0,05 · 0,07 ·
  0,35 $, soit 0,2364 + 0,0454 + 0,0708 par sa grille = 0,3525749 $ exact, écart 0.
  **Par fiche : 0,176 $ annoncé, 0,176 $ recompté**, 293 226 tokens. Le 0,42 $ à la main
  (`33-sans-refus.md:200`) se mesure pareil — `total_cost_usd`, Sonnet seul (`u5.jsonl` :
  0,4237932 $) — mais sur 1 fiche + clôture, contre (2 fiches + clôture) ÷ 2. Réserve : sur
  `Q4` passe 1, le script compte 595 tokens de sortie Haiku de moins que `modelUsage`
  (0,0030 $), cause non établie. `34-agent-sans-git.md:56` est périmé depuis CPT2.

- **2026-09-23** — CPT4 : l'« avant » de REP4 (4 840 313) ne contenait pas la clôture : la
  page à son commit dit 20 355 080, la somme des quatre fiches ; la clôture était dans les
  2 771 184 « à aucune fiche ». Le total d'une clôture ne compte plus la clôture en cours,
  faute de commit après la dernière fiche. Et `cout` arrondit session et sous-agents au
  centime chacun, pour que chaque ligne s'additionne : REP 20,63 → 20,61 $.

- **2026-09-23** — CPT2 : un sous-agent écrit un `output_tokens` provisoire (1, 2…) sur les
  lignes d'un tour avant la dernière, qui porte le compte final (144 cas sur 144, les 5
  sous-agents de REP) : garder la dernière ligne est juste, et `divergents` y est bénin — la
  session n'en a aucun. Le préfixe `\\?\` laissé par CPT1 est pris : 8 illisibles → 0 sur 96.

- **2026-09-23** — CPT1 : sous Windows, `open()` échoue sur un chemin de 260 caractères.
  L'inventaire des modèles a eu 8 transcripts `subagents/` illisibles (« No such file »)
  que `glob` liste pourtant : 8 chemins à 260 pile, tous de sessions de sonde. Avec le
  préfixe `\\?\`, 0 illisible et +58 tours Haiku. `mesurer` n'a pas ce préfixe : laissé à
  `CPT2`, qui compte les sous-agents.

- **2026-09-23** — clôture REP : les quatre arrêts sans statut de REP2 et REP3 sont le
  plafond `maxTurns: 30` de `agents/fiche.md`. Les quatre sous-agents arrêtés ont fait
  30 tours pile et finissent sur `tool_use`, coupés en plein travail ; le seul qui a
  rendu son statut a fait 25 tours et finit sur `end_turn`. Une fiche de code comme
  REP3 ne tient pas en 30 tours de Haiku : TODO `SAG`.

- **2026-09-23** — REP4 : MapDecorator, TrackGen et ProjetONZSM ne sont pas republiées,
  sur décision de l'utilisateur. Leurs pages en ligne, faites à la main, sont déjà à
  0 · 0 · 0, et leur version régénérée perd du contenu : TODO de MapDecorator hors
  table, donc lue vide ; lettres entre backticks ignorées ; source de TrackGen sans
  accents. Les quatre feuilles voisines sont hors de git, pas la seule de Cairn :
  quatre copies `.avant-REP`.

- **2026-09-23** — REP4 : sans `--ecrire`, la ligne `MARKDOWN` de `niveau` compte la
  page régénérée, pas celle du disque — muette sur la TODO et la zone « en cours ».
  L'« avant » a donc été pris par `markdown_brut` sur le disque (Cairn 426 · 1 · 1,
  comme l'audit). Défaut de `REP3`, laissé en suivi par l'utilisateur.

- **2026-09-23** — REP3 : sous `/vlp:enchainer`, le sous-agent `vlp:fiche` (fork de
  `vlp:jouer`) s'est arrêté sans statut quatre fois — une sur REP2, trois sur REP3 —,
  traité chaque fois en `RETOUR`. REP2 est passée au rejeu ; REP3 s'est faite à la main,
  par `/vlp:tache REP3`. Cause non diagnostiquée : à creuser avant de rejouer une fiche
  de code par `/vlp:enchainer`.

- **2026-09-23** — REP1 : la fiche ne disait pas comment `REP3` rejouerait une ligne
  close. Tranché : `gras_et_liens` prend la ligne `<tr>` entière, toute balise hors mono
  bornant le gras — sinon deux `**` seuls, dans deux cellules, s'apparient par-dessus
  `</td><td>`, et un `**` d'attribut `href` se convertit. `REP3` n'a pas à découper en cellules.

- **2026-09-23** — contenu de Cairn neutralisé avant le push, sur décision de
  l'utilisateur (« Neutraliser d'abord ») : le dépôt de Cairn est privé, celui du kit
  public. Dans l'audit (rapport, page, `39-reparer-pages.md`, `rejeu.py`, `replie.py`),
  titres de pages et de chantiers, codes, une note de fiche, une ligne de TODO, coûts
  par chantier et dates des lectures de Cairn deviennent des numéros de page et des
  exemples du kit ; les comptes restent. Les 5 commits locaux sont réécrits
  (`git filter-branch`) : 0 motif interdit dans chacun, contre 184 à 201 avant ;
  `rejeu.py` et `replie.py` rendent les mêmes résultats.

- **2026-09-23** — cadrage REP, fait sans l'utilisateur, à sa demande (« fait ce que
  tu dois faire », avant d'aller dormir) : ✅ validé par l'utilisateur le jour même
  (« Oui, les trois »). Les six chantiers de l'audit
  des pages (`38-audit-artefacts.md` § 4, A à F) entrent dans la TODO, rangs 25 à 30,
  avec des codes proposés — `REP`, `ABR`, `ALE`, `PLI`, `FEU`, `BTN` — que chaque
  ouverture peut changer. `REP` (le A) s'ouvre le premier : l'ordre de l'audit, et le
  seul des six sans décision en attente. `rejeu.py` n'est pas rangé dans `scripts/`,
  contre l'audit : il code Cairn en dur ; ses trois compteurs passent dans
  `vlp.py niveau` (REP3).

- **2026-09-18** — NIV3 : la fiche supposait que `clore` retirait la table des
  chantiers clos de `CHANTIER.md` ; il ne l'a jamais fait (il n'entretient que la
  ligne des lettres prises). `niveau --ecrire` la retire donc lui-même, et sous
  garde : **jamais** si l'index ne nomme pas chacun des fichiers de la table —
  sinon la retirer perdrait leur trace. NIV4 doit le vérifier projet par projet.

- **2026-09-17** — cadrage NIV : l'alphabet des préfixes de fiche était
  **épuisé** (26 chantiers, 26 lettres) et `vlp.py` n'acceptait qu'une majuscule :
  aucun 27e chantier ne pouvait s'ouvrir. Tranché en séance de cadrage, hors
  fiche : le préfixe officiel passe à **trois majuscules**, `vlp.py` accepte
  `[A-Z]{1,3}` (6 regex + `lettre_de`, car `ids[0][0]` ne prenait qu'un
  caractère), les chantiers d'avant gardent leur lettre. Plugin 3.4.3 → 3.5.0,
  8 vérifications ajoutées aux tests, 16 fichiers de fiches existants toujours
  `VALIDE`.

- **2026-09-17** — Z3 : une plage de fichier *du projet* ne se lit par aucune
  sous-commande (`vlp.py lire` refuse tout chemin hors du kit) ; le remplaçant
  de `sed -n 'A,Bp'` est l'outil `Read` avec `offset`/`limit`, déjà dans
  `allowed-tools` — pas de nouvelle sous-commande.
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
- **2026-09-17** — Y1 : la recette de X ne tient pas hors bypassPermissions — PowerShell refuse toute chaîne || (« control-flow or chain statement »), 5.1 ne l'analyse pas ; forme retenue : injection python3 …; py …; echo fin, corps en commande simple ; bin/ d'un plugin n'est que dans le PATH de l'outil Bash (0,463 $ de sondes).
- **2026-09-17** — U4 : le message du raccourci Store de `python3` ne se tait pas (stderr, code 49) ; injection inversée `py …; python3 … --relais; py … --relais; echo fin` — le 3e appel remet à 0 le `$LASTEXITCODE` de PowerShell (sans lui la skill avorte), le relais ne retire plus son tampon ; bruit à la fin sous Windows, « py: command not found » en tête sous Ubuntu, ligne README pour désactiver l'alias.
- **2026-09-17** — Q1 : un bac de sonde doit **renommer les références en dur au plugin** — `skills/enchainer/SKILL.md` appelle `skill: "vlp:jouer"` et `skills/jouer/SKILL.md` déclare `agent: vlp:fiche` : sans le renommage, le chef du bac `vlpz` appelle la skill du plugin **réel** (chargé en `-p` sous Windows) et la sonde mesure autre chose. `--plugin-dir` veut un chemin Windows : un chemin MSYS `/c/…` donne « Unknown command », 0 tour.
- **2026-09-17** — bilan des 22 chantiers écrit (`35-bilan.md`), README doté
  d'une section « Ce qui est prouvé — et ce qui ne l'est pas », dépôt public
  poussé (40 commits, `31be407..bdfb455` : F, O, J, Y, U, Q y manquaient).
- **2026-09-17** — les 5 projets équipés passés à `vlp.py renvois` et
  `feuille --verifier` : aucun n'est à jour du kit d'aujourd'hui. Deux
  chantiers en sortent, TODO n° 22 et 23 — le second est un bug du kit,
  trouvé parce qu'on a lancé la mécanique sur autre chose que le kit.
- **2026-09-17** — NIV1 : `2>"<chemin>"` est la **seule** redirection d'erreur que PowerShell et
  bash lisent pareil — `2>$null` est une erreur de syntaxe sous bash, `2>/dev/null` un chemin
  `C:/dev/null` absent sous PowerShell, et aucun ordre d'appels ne peut faire taire les deux
  lanceurs (celui qui manque parle avant que Python démarre). L'injection écrit donc sa sortie
  d'erreur dans `relais-python.err` à la racine du plugin (`2>` puis deux `2>>`, ignoré par Git) :
  la raison reste lisible au lieu d'être jetée.
