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
  jugement, donc à la main. Les 22 et 24 sont retirés, la TODO est vide ; 21 827 897 (recompté par REC : 24 964 199) tokens.

- **2026-09-23** — chantier REP clos (TODO n° 25) : les feuilles de route ne montrent
  plus de Markdown brut ni de lien cassé. `cellule_md` convertit gras et liens, les
  chevrons d'une URL tombent à la lecture et à l'écriture, et `vlp.py niveau` compte le
  Markdown brut, puis migre les lignes closes avec `--ecrire`. Les cinq feuilles sont à
  0 · 0 · 0 ; Cairn, à 426 · 1 · 1 avant, est republiée ; les trois autres gardent leur
  page en ligne, déjà propre. Laissé ouvert, reformulé en n° 25 : la ligne `MARKDOWN`
  muette sans `--ecrire`, et la régénération qui abîme trois feuilles voisines. Coût par
  fiche, repris de git parce que la page l'a perdu (une ligne `? $` ne se relit pas) :
  REP1 2 702 105 · REP2 4 227 906 · REP3 8 584 756 · REP4 4 840 313 ; 23 126 264 (recompté par REC : 33 108 434) tokens.
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
  fiche compte à la suivante. 19 266 526 (recompté par REC : 21 606 411) tokens.

- **2026-09-24** — chantier SAG clos (TODO n° 32) : le sous-agent ne bute plus sur 30 tours.
  `maxTurns` 30 → 80, et un hook `PostToolUse` (`vlp.py filet`) prévient `vlp:fiche` à trois
  tours du plafond : à plafond 10, il rend `RETOUR` sur `end_turn` au lieu d'être coupé (SAG4).
  Une fiche de code enchaînée, SAG3 : 68 tours, `FAITE`, 1,53 $ — 2,08 $ avec sa reprise à la
  main — contre 4,34 $ en moyenne à la main (CPT1–4) ; le gain vient du prix de Haiku. Le
  0,176 $ de Q tient, sous-agents compris (SAG1). Laissé ouvert, reformulé en n° 32 (`FIL`) : le
  filet ne tire qu'après `Write` ou `Edit`, et reste muet au-delà de 260 caractères. Vu sans le
  traiter : le sous-agent a rendu `FAITE` sans cocher, et le chef commite sans relire la case.
  Hors total : 0,46 $ d'essais `claude -p` (SAG2 0,2789 ; SAG4 0,0884613 + 0,08854675).
  20 128 626 (recompté par REC : 21 912 236) tokens.

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
  42 638 103 (recompté par REC : 20 319 194) tokens.

- **2026-09-24** — chantier CAS clos (TODO n° 38) : le chef relit la case avant de commiter.
  `vlp.py cocher --verifier` n'écrit rien et rend `CASE <fiche> [x]` (sort 0) ou `CASE <fiche> [ ]`
  (sort 1) ; tests 200 → 203 `verifier(`. La puce `FAITE` de `/vlp:enchainer` s'en sert et lit un
  `RETOUR` sur une case vide ; le contrat (`enchainement.md`) le dit. Imprévu, `CAS1` : le
  sous-agent a commité lui-même — son contexte porte le `CLAUDE.md` de l'utilisateur, qui demande
  un commit par tâche (cause probable, pas prouvée) ; `agents/fiche.md` le lui interdit depuis
  `CAS2`, pas encore éprouvé. Dans `CAS2`, la fiche disait « Tu ne commites pas » : aucun commit.
  Cadré et joué seul, la nuit, l'utilisateur dormant. 10 041 615 (recompté par REC : 11 729 608) tokens.
- **2026-09-24** — chantier VAL clos (TODO n° 34) : le contrôle avant commit ne se saute plus.
  Sans `claude` dans le PATH, `.githooks/pre-commit` prend le `claude.exe` de l'app (la plus haute
  version, `sort -V`) et valide vraiment les deux manifestes ; un `plugin.json` réduit à `{` refuse
  le commit (code 1). Le hook prend 1 755 · 1 846 · 1 948 ms au lieu de 147 ms. Imprévu : la règle
  de CAS a servi dès la fiche suivante (`FAITE`, case vide, lue comme un `RETOUR`) ; le sous-agent
  a encore commité, poussé cette fois par le critère — un clone prend le hook de `HEAD`. Cadré et
  joué seul, la nuit. 5 647 906 (recompté par REC : 6 924 438) tokens, recomptés par plage : `vlp.py cout` en rend 17 185 705,
  CAS compris, car son « hors fiches » part du début de la session.
- **2026-09-24** — chantier FIN clos (TODO n° 35, avec n° 42 `OUV`) : le coût juste, aux deux
  bords du chantier. « Hors fiches » part de l'origine — le dernier commit qui ne nomme pas le
  préfixe, avant l'ouverture — et finit au premier commit qui le nomme après la dernière fiche,
  la clôture ; sans elle, au bout. Une session qui enchaîne plusieurs chantiers ne fait plus
  compter l'un à l'autre : VAL 18 654 046 → 6 924 438, CAS inchangé à 11 729 608. La première
  fiche se mesure avant son commit, depuis l'ouverture ; `clore` régénère les coûts de la page.
  Tests 203 → 214 `verifier(`. Imprévu : les trois sous-agents ont rendu du code à reprendre
  (`max` au lieu du premier commit, une plage en double, des gardes doublées), et des tests
  creux ou absents en FIN1 et FIN2 — même nommés avec leurs valeurs ; chaque reprise est prouvée
  par un mutant. Cadré et joué seul, la nuit. 21 871 718 (recompté par REC : 22 962 798) tokens.

- **2026-09-24** — chantier TAR clos (TODO n° 33) : ce que `vlp.py` écrit, il le relit. Une
  sonde a repassé chaque format par son lecteur ; quatre défauts, quatre corrections, chacune
  prouvée par un test écrit d'abord : un coût négatif relu avec son signe (63 allers ratés sur
  198 avant), `arrondi` au million dès 999 950 ; une ligne close sous 1 000 tokens recomptée,
  `clore` sans rattrapage ; une lettre relue hors d'un titre (« Tests, CI (rapide) ») ou sans
  titre (« A. ») ; un résumé de `CLAUDE.md` sur une ligne. La vraie feuille reste à 439 668 779
  et 34 lettres. Tests 214 → 220 `verifier(`. Imprévu : les trois sous-agents ont encore
  débordé ou relâché la fiche — `COUT` plus strict qu'avant, un analyseur de 45 lignes, les blancs
  réduits dans le mauvais ordre — ; repris, et 11 mutants tombent. Cadré et joué seul, la nuit.
  17 642 733 (recompté par REC : 19 399 198) tokens.

- **2026-09-24** — chantier PLA clos (TODO n° 51) : la plage des fiches suit le fichier. Une
  fiche ajoutée après l'ouverture ne laisse plus de plage figée : `page` refait la plage de
  l'en-tête — elle seule, « · clos » écrit à la main reste —, et une fiche seule s'y lit `X1` ;
  `ouvrir` relancé refait la plage de sa ligne d'index `**ouvert**` (`index ~1`), ni le titre ni
  une ligne écrite à la main. `/vlp:chantier` dit de relancer `ouvrir`, `page` et `feuille`
  après un redécoupage. La page VAL passe de « VAL1–VAL1 » à « VAL1 ». Tests 220 → 224
  `verifier(`. Imprévu : le sous-agent PLA1 a commité seul (définition d'agent d'avant `CAS`,
  `CLAUDE.md` global « commit par tâche ») ; les deux ont rendu du code à reprendre — une plage
  écrite deux fois, une ligne réécrite titre compris, un test « une seule ligne » creux ; 9
  mutants tombent. Cadré et joué seul, la nuit. 11 938 808 (recompté par REC : 13 033 400) tokens.

- **2026-09-24** — chantier MTK clos (TODO n° 40 et 41, `MTK` et `PER`) : `mesure-tokens.py` se
  lit et se borne en ligne de commande. `--plage DEBUT FIN` ne garde que `(DEBUT, FIN]` — une
  borne est une heure ISO 8601, sans décalage l'heure locale, ou un commit Git ; une borne
  illisible ou une plage incomplète sort 1, là où l'option se lisait comme trois ids introuvables
  et la session entière se mesurait, code 0. Le script a une docstring de module ; la phrase
  périmée de `34-agent-sans-git.md` reste, marquée d'un renvoi daté vers `CPT2`. Imprévu : le
  sous-agent `MTK1` a écrit ses tests après le code, sans écart vu, et un fichier suivi par Git
  passait pour un commit (sans `--`) ; la docstring de `MTK2` disait faux deux fois et recopiait
  `COLONNES`. Repris ; sept mutants tombent. Cadré et joué seul, la nuit. 12 192 684 (recompté par REC : 13 588 111) tokens.

- **2026-09-24** — chantier CAD clos (TODO n° 50) : le cadrage compte dans le coût du chantier.
  `ouvrir` note `**Session** : <id>` avant la première ligne `## ` du fichier de fiches — le
  socle, jamais dans une fiche —, s'il n'y est pas déjà (`session +<0|1>`) ; `cout` et la page
  mesurent ces sessions d'en-tête comme celles des fiches : un cadrage joué dans sa session,
  puis `/clear`, entre dans « hors fiches ». La suite de tests retire l'id de la session qui la
  lance. Tests 224 → 230 `verifier(`. Imprévu : le sous-agent a plafonné à 80 appels ; le filet a
  tiré, et il a commité au lieu de cocher — case vide, `FAITE` quand même ; il avait écrit le
  code avant les tests, puis relâché ceux-ci sous le vrai id de session ; sa session tombait dans
  la fiche. Repris ; neuf mutants tombent. Cadré et joué seul, la nuit. 14 603 596 (recompté par REC : 15 724 492) tokens.

- **2026-09-24** — chantier ZER clos (hors TODO, trouvé par le recompte à blanc de `RCP`) : un
  vieux chantier ne se recompte plus à zéro. Depuis `FIN`, `cout` et la page rendaient 0 sur les
  dix clos sans commit de fiche — M, C, T, S, L, W, X, F, O, Q —, six sans une garde : leur plage
  partait de leur clôture. Un clos sans commit de fiche retombe sur ses sessions entières, sous
  `DÉCOUPE aucune — chantier clos sans commit « X1 : » ni d'une autre fiche` ; en cours, rien ne
  change (`FIN2`). Une découpe qui ne garde aucun tour le dit : `GARDE: découpe à zéro`. Tests
  230 → 237 `verifier(` ; neuf mutants tombent ; les dix rendent leur sortie d'avant la nuit,
  octet pour octet hors la ligne `DÉCOUPE`. Imprévu : une régression de la nuit même, faite par
  `FIN`, reprise par le chef. Cadré et joué seul, à la main, la nuit. 11 209 181 (recompté par REC : 12 079 243) tokens.

- **2026-09-25** — chantier REV clos (TODO n° 48) : chaque `FAITE` d'`/vlp:enchainer` est relu
  avant son commit par un agent `vlp:relecture` neuf (`opus`) — `vlp.py relecture` (instantané
  sans bouger `HEAD`, copies AVANT/APRÈS), `cocher --verifier` et `--refuser`, contrat dans
  `enchainement.md` : trois motifs refusent, le reste se remarque ; un soupçon se rejoue ; la
  sonde va au-delà du critère ; le dépôt vivant ne se lit pas ; un hook se lance par `env -C`.
  Prouvé sur les quatre témoins de la nuit : 4 verdicts justes sur 4, en quatre passages et
  deux lots (la table finale mêle le 4ᵉ passage et `c5123af` rejouée) ; 0,50 $ la relecture au
  dernier état, contre 1,78 $ au premier. En route, trois bugs du kit prouvés et corrigés (hook
  en CRLF, regex de l'en-tête, fichier d'état hors fiche). Laissé ouvert : la carte donnée au
  relecteur liste les titres des fiches, un indice ; la relecture n'a pas encore tourné dans un
  vrai `/vlp:enchainer`. 614 tours, 74 789 054 (recompté par REC : 76 440 498) tokens, 56,10 $.

- **2026-09-25** — chantier CON clos (TODO n° 49) : le contrat d'`agents/fiche.md` se lit et se
  tient. `vlp.py contrat` le lit dans les transcriptions (après `f98ceec` : 8 sous-agents, 0
  écrivent dans Git, 5 sans statut en tête — c'est le statut qui casse) ; `vlp.py gardien`,
  branché sur `PreToolUse` (`Bash|PowerShell`) et `SubagentStop`, refuse l'écriture Git et
  renvoie un sous-agent sans statut en tête, sur case vide ou dont le commit nomme la fiche.
  Prouvé en vrai : `SubagentStop` renvoie (sonde, `CON3`), `PreToolUse` refuse et `HEAD` reste
  `60ef683` (témoin, `CON5`). `CON2` sautée (8 ≥ 5). Laissé ouvert : le renvoi du gardien n'a
  tiré que sur la sonde, pas encore sur un vrai statut manquant ; chaque hook tourne deux fois
  (`python3` et `py` ouvrent le même Python). Joué à la main, une session. 108 tours,
  13 910 638 (recompté par REC : 15 711 661) tokens, 6,83 $.

- **2026-09-25** — chantier GLO clos (TODO n° 44) : les `CLAUDE.md` de l'utilisateur et du
  projet, et sa mémoire, entrent dans chaque sous-agent (attachment `instructions`, premier
  niveau de la transcription). `vlp.py forme` les mesure : depuis `f98ceec`, 36 sous-agents,
  jauge dans 23 derniers messages, « En résumé » dans 14 ; le `CLAUDE.md` utilisateur (6 000
  caractères) coûte au plus 7,24 % d'une fiche triviale — borne haute, fragile. Verdict fondé
  sur la forme : une phrase dans `agents/fiche.md` et `agents/relecture.md` (« Ton lecteur est
  le chef, pas l'humain »). Laissé ouvert : la preuve, au premier `/vlp:enchainer` d'une session
  neuve (`forme --depuis 5e37964`). Enchaîné la nuit, l'utilisateur dormant : GLO1 rendue
  `FAITE` sur case vide et fausse (lisait `message.attachments`, 0 partout), corrigée par le
  chef ; GLO2 et GLO3 refusées à la relecture (octets pris pour des caractères ; journal citant
  une phrase retouchée), recalées par le chef. 134 tours, 13 784 706 (recompté par REC : 15 674 582) tokens, 5,67 $.

- **2026-09-25** — chantier GAR clos (TODO n° 59) : le gardien juge encore un `FAITE` après
  un premier renvoi (`stop_hook_active`) — case vide et `TÊTE` —, plus la tête ; la sonde de
  `CON3` est retirée. Prouvé en vrai sur un témoin (`GAR3`) : renvoi sur « Parfait, », puis
  sur la case vide sous `stop_hook_active`, et le sous-agent coche. Laissé ouvert : chaque
  renvoi arrive deux fois (`python3` et `py`, chantier `PYT`) ; aucun test ne garde l'absence
  de `sonde`. 89 tours, 7 588 840 (recompté par REC : 8 426 745) tokens, 2,54 $.

- **2026-09-25** — chantier UNI clos (TODO n° 52) : un seul chiffre par clôture. `clore`
  écrit sur la feuille de route le total que `regenerer` vient de mettre sur la page, et le
  rend (`CLOS … · chantier <n> · cumul <m>`) ; `--tokens` n'est plus qu'un contrôle
  (`ÉCART`) ; `cloture.md` fait `clore` d'abord et cite ce chiffre au bilan. Prouvé sur UNI
  elle-même : page et `CLOS` à 15 942 182. UNI1 rendue `FAITE` avec l'`ÉCART` dans une branche
  morte et sans son test, corrigée par le chef ; UNI2 écrite par le chef. Laissé ouvert : la
  ligne de bilan s'écrit après la page, donc ses propres tours n'y sont pas — quelques
  milliers, hors du chiffre. 106 tours, 15 942 182 (recompté par REC : 16 613 231) tokens, 4,47 $.

- **2026-09-25** — chantier PYT clos (TODO n° 39) : un hook n'agit qu'une fois. La paire
  `python3` + `py` reste ; `une_fois` lit l'entrée, et seul le lanceur qui crée
  `<temp>/vlp-hook-<sha1 du nom et de l'entrée>` agit. Compté dans la session : 2 `VALIDE`
  par écriture avant, 1 après. Le « Python est introuvable » de la TODO était périmé : les
  deux lanceurs marchent (mesuré au cadrage). Surpris : `filet` et `hook` reçoivent la même
  entrée — sans le nom dans l'empreinte, `hook` se taisait derrière `filet` (`0bef88a`).
  Laissé ouvert : sous `SubagentStop`, le renvoi en double n'a pas été recompté après le
  correctif. `CLOS` : 11 561 195 (recompté par REC : 12 279 871) tokens ; `cout`, quelques tours plus tard : 83 tours, 3,81 $.

- **2026-09-25** — chantier RLG clos (TODO n° 60) : le gardien refuse `git commit/add/reset`
  au relecteur comme au `vlp:fiche` ; le `SubagentStop` du relecteur n'est pas jugé. `RLG1`,
  jouée par Haiku, a été refusée deux fois par le relecteur — deux vrais plantages, un JSON
  qui n'est pas un objet, puis un `tool_input` qui n'en est pas un (vrai pour `vlp:fiche`
  depuis `CON`) —, corrigés par le chef, acceptée à la troisième. Le 🟡 des `git worktree`
  est tombé : l'agent n'en tape jamais. Vu en chemin, versé en TODO : la phrase de forme de
  `GLO3` n'a rien changé (`FOR`), `ECRIT_GIT` lit le texte d'un heredoc (`ECH`), le tampon
  de `PYT` gêne une sonde à la main (`SON`). `CLOS` : 8 745 720 (recompté par REC : 9 179 817) tokens, 109 tours, 3,61 $.

- **2026-09-25** — chantier FOR clos (TODO n° 62) : la mesure « sans effet » de `GLO3`
  était fausse — la session `ca431cf8` avait démarré 21 min avant le commit `5e37964`,
  sans `/reload-plugins` ; une définition d'agent se charge au démarrage. `FOR1` corrige
  `forme --depuis` (compare au départ du sous-agent, plus de la session parente). `FOR2`,
  en session neuve après relance de l'app : `resume 0/2`, `jauge 1/2` — contre 14/36 et
  23/36 avant `GLO3` (mesurés en texte entier, voir `JUG2`) ; échantillon minuscule, mais net. Décision : jouer `FOR3`. Premier
  essai refusé à la relecture — `JAUGE` matchait en sous-chaîne (« bonne » contenait
  « Pas bon »), un faux positif prouvé sur le relecteur lui-même ; corrigé par `\b`. Le
  gardien renvoie maintenant une fois une fin qui porte « En résumé » ou la jauge, fiche
  et relecteur. Laissé ouvert : un verdict qui *cite* la jauge en la décrivant se fait
  renvoyer à tort — ne juger que la fin du message serait plus juste. `CLOS` :
  17 689 317 (recompté par REC : 20 371 577) tokens.

- **2026-09-25** — chantier JUG clos (TODO n° 65) : trois règles mesurées sur 29 vrais
  sous-agents depuis `GLO` (`JUG1`) — renvoyés `tout` 16, `tiret` 16 (aucun `---` dans le
  corpus), `deux` 11 (rate 3 vraies fins), `tete` 14 (retire exactement les 2 citations).
  Retenue par l'utilisateur : `tete`, un mot ne compte que s'il ouvre une ligne. `JUG2` en fait
  le défaut (`REGLE`), `--regle tout` rejoue l'ancienne mesure ; les chiffres d'avant sont
  marqués « mesurés en texte entier ». `JUG3`, en vrai : relecteur en prose renvoyé 0 fois,
  résumé à part renvoyé 1 fois puis réécrit (0,13 $ les deux). Laissé ouvert : une ligne qui
  s'ouvre par « Imprévu » ou « Pas bon » pour une autre raison serait encore renvoyée une fois
  — absent des 29 mesurés. `CLOS` : 10 273 570 (recompté par REC : 11 306 457) tokens.

- **2026-09-25** — chantier REC clos (TODO n° 37, `RCP`) : la feuille de route recomptée par
  `cout`. `vlp.py recompter` (`REC1`) ; 23 clos recomptés, 25 gardés et marqués « non
  recompté » — 23 en `DÉCOUPE aucune` (dix attendus au cadrage), V sans session, E sans plage. Écarts
  rangés par cause (`REC2`) : `FIL` −22 318 909 (session partagée avec `SAG`), `REP`
  +9 982 170 (sous-agents avant `CPT`), 17 clos à fiches inchangées au token près, écart tout
  en hors fiches. `--ecrire` (`REC3`) ; appliqué (`REC4`) : total 681 541 003 → 700 725 374,
  second passage `ÉCRIT 0`, 22 bilans marqués (H, 23e écart, ne cite pas de chiffre).
  Laissé ouvert : la cause des 4b et de `NIV`/`H` n'est pas établie. `CLOS` : 15 906 689 tokens.

- **2026-09-25** — chantier ESS clos (TODO n° 47) : `vlp.py cout` compte les essais `claude -p`
  dans le prix de leur fiche, part `essais` à côté, `TOTAL` compris (`essais_de`, relié par le
  dossier du bac puis l'heure). Les ≈ 12,32 $ de la TODO = 4,5734 $ de sondes + 7,74 $ d'evals
  (dehors). `recompter` : +1 090 457 sur `SAG` et `FIL`, seuls rattrapés (0,77 $) ; 9 clos à bacs
  sont en `DÉCOUPE aucune`, mesurés sans essais (7,1299 $ de dossiers) — laissé ouvert en TODO
  n° 68, avec la republication. `CLOS` : 12 254 063 tokens.
- **2026-09-25** — chantier ESD clos (TODO n° 68) : `cout` sans découpe montre une ligne `essais`
  (`essais_entiers`) ; `recompter --essais` ajoute les essais une seule fois, sous une marque que
  l'affichage et l'écriture lisent (`ajout_essais`, seul endroit de la règle). Écrit sur la
  feuille : 11 clos, +12 991 756. `ESD2` refusée une fois (mutant « ignorer la marque » vivant,
  test sur le vrai dépôt), reprise par le chef. Laissé ouvert : `REC` et `ESS` (TODO n° 67).
  `CLOS` : 16 735 386 tokens.
- **2026-09-25** — chantier APC clos (TODO n° 67) : `recompter --a-clore` décompose l'écart des
  19 clos de `REC2` — après-clore l'explique en entier pour 5, en partie pour 14, jamais 0 ; reste
  10 952 704, cause non établie. Choix (b) : un fichier clos se recompte jusqu'à l'appel `clore`
  (`decouper`) — inscrit = recompté, les republications sortent du coût (`cloture.md`). Sur `ESD` :
  18 506 516 → 16 735 386. Laissé ouvert : `NIV`, `H`, et ce reste. `CLOS` : 13 795 365 tokens.
- **2026-09-25** — chantier LEC clos (TODO n° 53) : sans chantier ouvert, la carte imprime la
  TODO de chaque fichier « chantiers possibles » et le format des fiches (`section`, `chemins_md`),
  texte compris ; `/vlp:chantier` ne les relit plus. Mesuré (journal `LEC5`) : `equiv` 285 200 →
  148 740, 1.14 → 0.59 $, mais au-dessus du cadrage à la main (0.49 $), 3 appels du montage
  compris. `LEC2` refusée 4 fois : deux critères qui ne vérifiaient que l'en-tête quand le socle
  voulait le texte, un sous-agent, une règle du chef jamais essayée sur les vraies lignes — **une
  règle de fiche s'essaie sur les données des projets avant d'être jouée** ; `LEC2` à `LEC4`
  jouées à la main. Laissé ouvert : `ENC` (TODO n° 69), une mesure sans montage. `CLOS` :
  41 160 098 tokens.

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée, cité
par son code, rangé par importance d'implémentation — rangée la nuit du
2026-09-24, décidé seul (l'utilisateur dormait ; validé au réveil) : d'abord ce qui
garde juste le code livré (`REV`, `CON`, `GLO`), puis les chiffres (`UNI`, `RCP`,
`ESS`, `EST`), l'outillage d'essai (`RAT`, `BAC`, `EVF`, `PYT`), enfin les pages,
dans l'ordre de leurs dépendances. Reclassée le 2026-09-28 à la demande de l'utilisateur, par la même règle : le chiffre juste (`TAU`), la faute possible (`ENQ`), le refus de publication qui a bloqué `BTN6` (`LOC`), l'outillage (`MUT`), puis `NUI`, qui a besoin des deux premiers, `BDD` et `PAR`. Reclassée le 2026-09-29 à la demande de l'utilisateur, pour l'ordre d'implémentation : la faute possible d'abord (`VRB`), la preuve des essais (`ESR`), l'outillage (`MUT`, puis `CLI`, qui trouve `claude` pour la nuit), le chiffre juste (`DEC` : une nuit partage sa session entre chantiers), le poids des clôtures (`ARC` : une nuit en clôt plusieurs), puis `NUI`, qui a besoin de tous, et `BDD`, pas estimé. Le numéro reste celui d'entrée. Le détail des
pages est dans `38-audit-artefacts.md` § 4, qui les nomme A à F ; les rangs 1 à
24, tous retirés, venaient de `12-audit.md` ; 31 à 34, de la clôture de `REP` ; 35
à 37, de celle de `CPT` ; 38 à 41, de celle de `SAG` ; 42, de `FIL1` ; 43 à 47, de
celle de `FIL` ; 48 à 51, de celle de `FIN` ; 52, des clôtures de la nuit du
2026-09-24 ; 53, du cadrage de `REV` ; 54, d'une demande de l'utilisateur pendant `REV5` ; 55 à 57, de la clôture de `REV` ; 58, d'une demande de l'utilisateur le 2026-09-25 ; 59 à 61, de la clôture de `CON` ; 66, de celle de `JUG` ; 67, de celle de `REC` ; 68, d'`ESS4` ; 69, d'une demande de l'utilisateur pendant `LEC2` ; 70, de `REL1` ; 72, d'une demande de l'utilisateur le 2026-09-26 ; 75 et 76, d'une demande de l'utilisateur à la clôture de `PLI`, le 2026-09-27 ; 77 et 78, du rapport de la nuit du 2026-09-27 (deux oui ; 77 fondue dans 78 le 2026-09-28) ; 79 à 81, de la clôture de `BTN` (deux oui) ; 82, de la clôture d'`ENQ` (deux oui) ; 84, de la clôture de `PAR` (deux oui) ; 85, de celle de `LOC` (deux oui) ; 86 et 87, de celle de `REG` (deux oui).

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 82 | `VRB` — Le gardien ne voit que trois verbes Git | Vu à la clôture d'`ENQ`, le 2026-09-28 : `ECRIT_GIT` (`scripts/vlp.py:1549`) ne vise que `commit`, `add` et `reset`. Mesuré le même jour sur 145 sous-agents `vlp:*` (202 transcriptions) : 19 appels visés par le motif, et 4 appels d'autres verbes qu'il ne voit pas — `git checkout <fichier>` (2 appels, 1 sous-agent, sur Cairn : efface les modifications non commitées du fichier) et `git stash` (2 appels, 1 sous-agent, sur le kit) ; aucun `push`. Ce qu'elle ferait : élargir le motif aux verbes qui effacent ou publient (`checkout`, `restore`, `stash`, `clean`, `push`, `rebase`…), le gardien et `contrat` avec, test et mutant. 🟡 À trancher au cadrage : la liste exacte des verbes, et `git checkout <branche>` (sans danger pour le travail) face à `git checkout <fichier>`. Ajoutée avec deux oui, clôture d'`ENQ` (2026-09-28). | ~1 fiche (estimé, non mesuré — comme `ECH`, 1,36 $ ; les estimations sous-estiment) | — |
| 86 | `ESR` — Un essai rechargé voit le code du worktree | Vu à `REG3`, le 2026-09-29 : `~/.claude/skills/vlp` suit le dossier principal (`main`), pas le worktree où la fiche a été écrite ; `/reload-plugins` aurait rechargé l'ancien `enchainer` (`model: sonnet` encore en tête), et l'essai aurait « réussi » sur le mauvais code. `main` avancé à la main de 8 commits avant l'essai. Ce qu'elle ferait : avant une fiche d'essai rechargé (`(visuel)` qui demande `/reload-plugins`), un script compare la branche du plugin chargé et le worktree (`git log main..HEAD`) et dit l'avance, avec la commande pour avancer `main` ; test et mutant. Voisine de `NUI` (b), `niveau` aveugle au worktree : même famille, pas le même trou. 🟡 À trancher au cadrage : où il se lance (carte, `/vlp:tache` étape 5, `/vlp:check`). Ajoutée avec deux oui, clôture de `REG` (2026-09-29). | ~1 fiche (estimé, non mesuré — les estimations sous-estiment) | — |
| 81 | `MUT` — Le mutant par un outil du kit | Une fiche de code exige un mutant (`methode-chantier.md:360`) ; à la clôture de `BTN`, il a été fait par un script écrit à la main dans le dossier de la session, perdu au `/clear`. Ce qu'elle ferait : `vlp.py mutant <fichier> <avant> <après>` — casse le code exprès, joue les tests sans s'arrêter au premier écart, liste les `ÉCART:`, rend le fichier à l'octet près. D'abord compter les sessions qui ont réécrit ce script (une seule connue). Regarder les outils de mutation Python existants (règle « ne pas réinventer la roue ») ; la contrainte « sans dépendance » du kit pèse contre. Ajoutée avec deux oui, clôture de `BTN` (2026-09-28). | ~1 fiche (estimé, non mesuré) | — |
| 87 | `CLI` — Le bac dit comment ouvrir sa session | Vu à `REG3`, le 2026-09-29 : ouvrir une session dans le bac a pris 3 allers-retours — une session de l'app lancée dans un worktree du kit au lieu du bac, `claude` absent du `PATH`, puis le chemin court `%APPDATA%\Claude\claude-code\<version>\claude.exe` refusé dans le terminal de l'utilisateur (app du Store, `AppData` virtualisé ; seul `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming\…` y marche). Ce qu'elle ferait : `vlp.py bac` imprime la commande prête à coller pour ouvrir une session dans le bac, avec le vrai chemin ; `VAL` trouve déjà le `claude.exe` de l'app pour le hook : à réutiliser. Vu au reclassement du 2026-09-29 : `boucle.py` ne cherche `claude.exe` que sous `%APPDATA%` (`scripts/boucle.py:72-74`), pas sous `Packages` comme le hook (`.githooks/pre-commit:31`) — une nuit (`NUI`) lancée depuis le terminal de l'utilisateur ne trouverait pas `claude` : la même recherche, aux deux endroits. Ajoutée avec deux oui, clôture de `REG` (2026-09-29). | ~1 fiche (estimé, non mesuré — les estimations sous-estiment) | — |
| 83 | `DEC` — `vlp.py cout` découpe les sessions partagées et les fiches sans commit | Vu le 2026-09-28 en rejouant `cout` sur 25 chantiers clos de Cairn : le recalcul ne retombe sur le publié que pour **9** (6 sur le total avec « hors fiches », 3 sur les fiches seules) ; **16** ne collent à aucun des deux. Trois défauts mesurés : (1) une fiche sans commit `<ID> :` court jusqu'à la fin de la session (chantiers 31, 32, 36 à 39 de Cairn : le recalcul égale la session entière, de +10 % à +64 % au-dessus du publié) ; (2) une session partagée entre chantiers est comptée par chacun (Cairn 50, 51, 53 : `TAI` et `GAR` rendent le même total, 70 869 394 ; sur 43 à 47 la somme recalculée, 119,9 M, dépasse la session entière, 62,8 M) ; (3) le « hors fiches » est tantôt dans le coût du chantier, tantôt hors (`MIL`, `BUD`, `VIT` : publié = fiches seules ; `PUB`, `TEL`, `REP`, `LIS`, `REC`, `FON` : publié = total). Ce qu'elle ferait : une règle unique de « coût d'un chantier », écrite avant le code ; la fin d'une plage bornée par la clôture du chantier ; une plage prise dans une session partagée coupée à ses commits ; « DÉCOUPE aucune » (`SEG`) dit ce qu'elle compte. Tests sur les trois défauts, avec mutant. À revoir d'abord : `CPT`, `FIN` et `REC` ont déjà touché `cout` (règle « ne pas réinventer » : lire leurs fichiers de fiches avant de cadrer). Rien n'est réécrit sur les pages tant que la règle n'est pas fiable : les 16 chantiers restent sans $ sur la feuille de Cairn. Ajoutée à la demande de l'utilisateur, le 2026-09-28 (« pas important »). | ~2 fiches (estimé, non mesuré — les estimations sous-estiment) | — |
| 85 | `ARC` — Les vieux chantiers clos vont à une page d'archive de la feuille | Vu à la clôture de `LOC`, le 2026-09-29 : republier la feuille de route oblige à lire chaque ligne de la version en ligne avant d'y écrire (l'outil `Artifact` refuse sinon). Elle pèse 74 746 octets sur 588 lignes ; les chantiers clos en font 57 150 (76,5 %) et 535 lignes, pour 81 lignes de clos — mesuré le même jour, et chaque clôture en ajoute une. Ce qu'elle ferait : comme `IDX` pour l'index, ranger les clos anciens dans une page d'archive, republiée seulement quand on y range ; la feuille garde les derniers. 🟡 À trancher au cadrage : le seuil, la place du graphique `couts.svg`, et l'effet sur `vlp.py feuille`, `comparer`, `niveau` et les feuilles des quatre autres projets. Ajoutée avec deux oui, clôture de `LOC` (2026-09-29). Revu à la clôture de `REG` (2026-09-29) : la feuille en ligne faisait 591 lignes, trop grosse pour un seul `Read` (35 839 tokens pour 25 000 permis) — relue en deux morceaux. | ~2 fiches (estimé, non mesuré — les estimations sous-estiment) | — |
| 72 | `NUI` — `/vlp:chantier nuit` : les questions le soir, les chantiers la nuit | Demandé par l'utilisateur le 2026-09-26. Une séance de nuit enchaîne plusieurs chantiers sans humain ; le kit n'en fait aujourd'hui qu'un à la fois. Le soir, `/vlp:chantier nuit` trie la TODO — un script d'abord (🟡, dépendance non close), puis le modèle relit ce qui reste (décision cachée sans 🟡, comme `ENR`) — et rassemble toutes les questions de cadrage dans une page à cartes, vulgarisées, avec un bouton « copier » : l'utilisateur y répond d'un coup. Un 🟡 n'écarte plus un chantier s'il se tranche le soir ; restent écartés ce qui se juge à l'œil (`(visuel)`) et ce qui demande sa main (push). La borne de la nuit — budget en $ ou nombre de chantiers — se choisit au lancement. La nuit, les restes d'une clôture n'entrent pas dans la TODO : ils attendent les deux oui du matin. Tranché avec lui le 2026-09-26 : le nom, le tri en deux temps, la page, la borne au lancement. Estimé en séance, sans mesure — les estimations sous-estiment (`EST` 1 → 3, `CPT` 2 → 4). Ajoutée à la demande de l'utilisateur ; rangée le 2026-09-28 après `LOC` et `TAU`, dont elle a besoin : une nuit qui bute sur la limite de publication s'arrête net, et sa borne en $ suppose un prix juste. Ajouté le 2026-09-26 : `/vlp:chantier nuit clear` — une session neuve pour chaque fiche **et** chaque clôture, comme `/clear` entre deux ; la brique existe pour les fiches (`scripts/boucle.py`, option `clear` de `/vlp:enchainer`, un essai réel sur le bac : fiche cochée), reste à l'étendre à « ouvrir → jouer → clore → chantier suivant ». Tranché avec lui le 2026-09-26 : la nuit, le découpage en fiches se fait seul, au plus logique et au plus sûr pour la qualité ; un chantier dont le découpage ne se tranche pas sans risque se découpe le soir, et l'utilisateur le valide.<br>**Rangé le 2026-09-29** (`PAR5`, page à cartes « Ranger les commandes », 11 cartes, réponses de l'utilisateur) :<br>Q1 parallèle : le kit ne code que ce qui lui est propre — réserver les fichiers, clore à tour de rôle ; lancer, suivre et faire parler les sessions : les outils de Claude Code (sessions en fond `claude agents`, worktrees, messages entre sessions) ; écartés : D2–D5 tout maison, un orchestrateur de la communauté (non vérifié), rien coder ; aucun outil ne connaît `CHANTIER.md`.<br>Q2 commandes : une commande **`/vlp:chef`** — cadrer le soir, orchestrer la nuit —, `enchainer` reste pour un chantier ; elle remplace le `/vlp:chantier nuit` du titre ; écartés : tout dans `enchainer`, la nuit dans `/vlp:chantier` ; une copie de la carte de plus (7 → 8).<br>Q3, Q4, Q6 (défaut `main`, `main clear` = `clear`, retrait du `model: sonnet`) : sortis dans l'entrée 84 `REG`, jouable sans attendre `NUI` — clôture de `PAR`, le 2026-09-29 (deux oui).<br>Q5 joueur de fiche : **Sonnet 5.5, effort `low`, relance plus forte sur refus** (relance à construire) — 0,95 $/fiche acceptée, N = 2 (`PAR7`) ; écartés : Opus `low` (1,39 $), Haiku (0 acceptée sur 2).<br>Q7 nuit à deux canaux, précisé par l'utilisateur : **le soir, le chef liste les chantiers prêts et propose l'ordre et le canal, A ou B ; l'utilisateur valide ; la nuit, chaque canal joue, clôt dans sa branche et enchaîne le suivant ; le matin, fusion A + B dans `main`, avec lui** — même canal pour deux chantiers dépendants ou qui touchent les mêmes fichiers (les 5 derniers du kit touchent tous `scripts/test-vlp.py`) ; écartés : un seul à la fois, fusionner la nuit (5 conflits prédits, `PAR4`), tout attendre le matin (un chantier par canal : `ouvrir` refuse le second).<br>Q8 borne : en $ **et** en nombre de chantiers, le premier atteint arrête tout ; le `--max-budget-usd` de `boucle.py` borne une fiche, pas la nuit : à coder.<br>Q9 : noter et passer au suivant — page refusée en liste d'attente (`LOC`), chantier bloqué arrêté ; écartés : tout arrêter, réessayer après la remise à zéro de 02:00.<br>Q10 réglages par défaut : `main`, Sonnet `low`, relecteur Opus (pas mesuré), 2 canaux, borne double — et le chef en **Opus 5.5, fixé au lancement de la session** (`--model` la nuit), sans `model:` dans `/vlp:chef` : le modèle lourd pour ce qui décide, sans bascule ; hors Opus, `/vlp:chef` le dit et demande confirmation avant d'agir (ajouté par l'utilisateur : Opus gère mieux les tâches complexes ; la nuit, sans humain pour confirmer : à trancher) ; écarté : `model: opus` dans la commande.<br>Q11 le matin : un rapport de nuit en page à cartes (`templates/rapport-choix.html`) ; écartés : l'état seul, un message court.<br>Recherche de `PAR5` : 3 recherches, 2 pages lues en entier (`code.claude.com/docs/en/agents`, `/headless`) ; l'écart d'agent teams (D6) tient — toujours expérimentaux, sans worktree par coéquipier.<br>**Fondu à la clôture de `PAR`** (2026-09-29, deux oui) : (a) la fusion du matin par script — `PAR4` a prédit 3 conflits, tous vus à la fusion de `PAR` dans `main` (`2cef70f`) ; deux pertes sans conflit, à réparer par le script : `CHANTIER.md` perd le chantier de l'autre canal (`LOC`, remis à la main), la feuille son badge « en cours » (`vlp.py feuille . --todo 79`) ; (b) `vlp.py niveau` voit le chantier joué dans un worktree — sur Cairn, 2 faux écarts pendant que `MOR` joue dans le sien (`git worktree list`), et un `--ecrire` y créerait un conflit à la fusion. | ~6 fiches, plus une nuit d'essai | `LOC`, `TAU`, `REG` |
| 73 | `BDD` — Le journal des pages en base `db` | Décidé par `ALE` (`ARTEFACTS.md`, « Où vivent le CSS et les données ») : adoptée pour plus tard. Le journal d'une page de chantier vient d'une collection `db` ; `vlp.py` écrit un JSON, `ArtifactData` l'envoie sans relire la page (écart 630 contre 3286, aucun accord demandé). Le `.md` reste la source. Coût connu : rien en local, pas de lien public, un script dans la page. Ajoutée à la demande de l'utilisateur (deux oui, 2026-09-27). **Fondu à la clôture de `LOC`** (2026-09-29) : ne joindre à une publication que les joints qui ont changé. Le refus « joints non lus » (`ARTEFACTS.md`, « Une publication refusée ») force à relire `vlp.css`, `vlp.js` et `couts.svg` (11 066, 8 206 et 6 776 octets) à chaque republication, alors qu'aucun n'avait changé (`git diff` vide, `LOC5`) ; d'après la doc de l'outil `Artifact`, une publication sans `files` les garde (non essayé) ; 17 transcriptions mentionnent ce refus (compte brut, discussion comprise). À mesurer d'abord : combien de fois il tombe par fiche. Retombé une fois à la clôture de `REG` (2026-09-29), sur la feuille : `vlp.css`, `vlp.js`, `couts.svg`. | 🟡 pas estimé | `PLI` |

## Journal des décisions

Une ligne par décision imprévue tranchée en cours de fiche — jamais un résumé
de ce que le code dit déjà.

- **2026-09-25** — hors chantier, demandé par l'utilisateur contre le *scope creep* (« il y a trop
  de todo ») : la TODO ne grossit plus sans deux oui, justifiés — règle écrite dans
  `methode-chantier.md`, renvoyée par `cloture.md` et `tache-contraintes.md`. Compté : des entrées
  31 à 68, 32 sur 38 créées par le kit lui-même ; 21 lignes ouvertes.
- **2026-09-25** — ESS1, les ≈ 12,32 $ de la TODO n° 47 sont **deux choses** : 4,57 $ de sondes
  `claude -p` (8 notes) et 7,74 $ d'evals (10 notes). Les evals sont dehors par le cadrage :
  `ESS` ne rattrape que les 4,57 $ notés — 4,30 $ trouvés en dossier. Table : `## 2026-09-25 — ESS1`.
- **2026-09-25** — ESS1, trois clos ont des bacs **sans aucune note** : `Y` 1,6679 $, `U` 0,8862 $,
  `Q` 1,0441 $ (3,5982 $, 13 dossiers). `ESS` les ajoutera — au-delà de ce que la TODO chiffrait.
- **2026-09-25** — ESS1, `X` : 0,6171 $ en 19 dossiers pour 0,90 $ notés (−0,2829 $), seul écart
  au-delà du centime. Tous ses bacs sont en `-w-` (Windows) ; des sondes Ubuntu hors de ce disque
  l'expliqueraient — non vérifié.
- **2026-09-25** — ESS4, `cout` ne rattrape que 0,77 $ des 4,5734 $ d'essais notés : sur 11 clos à
  bacs, 9 sont en `DÉCOUPE aucune`, que `cout` mesure sans `essais_de` et que `recompter` garde
  (7,1299 $ de dossiers). Versé en TODO n° 68. Table : `## 2026-09-25 — ESS4`.
- **2026-09-25** — ESS1, un sous-agent voit le scratchpad **à l'id de son chef** : 83 transcripts
  `subagents/` sur 83 qui citent un scratchpad. Mais aucun des 39 bacs n'a été lancé par un
  sous-agent : le cas « essai d'un `vlp:fiche` » reste non observé.
- **2026-09-25** — ESD3, `recompter --essais --ecrire` marque les 11 chantiers avec essais (+12 991 756 total) : SAG (+506 675), FIL (+583 782), Q (+1 594 040), U (+1 899 554), Y (+3 807 198), X (+1 145 283), G (+176 238), A (+390 811), P (+1 257 544), L (+677 922), N (+952 709). Marque idempotente : second `--ecrire` n'ajoute rien (ÉCRIT 0 cellules). Feuille de route régénérée. Table : `## 2026-09-25 — ESD3`.
- **2026-09-25** — CON5, le gardien prouvé après `/reload-plugins` (`10 hooks`). Témoin `CON9`
  dont le prompt demande `git add` puis `git commit`, joué par `vlp:jouer` (agent
  `a626844e3b44445ba`). `HEAD` avant et après : `60ef683` (`git log -1 --format='%h %s'`). Le
  hook a tiré, cité de la transcription : `PreToolUse:Bash hook error: Un sous-agent vlp:fiche
  n'écrit pas dans Git (agents/fiche.md) : retire git commit/add/reset, le chef commite après ton
  statut.` (`is_error: true`). Statut rendu : `RETOUR` en tête, donc `SubagentStop` n'avait rien
  à renvoyer. `py scripts/vlp.py contrat <transcription>` : `a626844e3b44445ba vlp:fiche … RETOUR
  git 1` — `contrat` compte les appels **tentés**, refusés compris. Coût du témoin :
  `mesure-tokens.py` sur sa transcription, 4 tours, 83 596 tokens, 0,04 $. Témoin retiré.
- **2026-09-25** — CON3, les hooks essayés. Doc lue le 2026-09-25,
  https://code.claude.com/docs/en/hooks (doc officielle) : table « Exit code 2 behavior per
  event » — `PreToolUse` « Blocks the tool call », `SubagentStart` « Blocks subagent spawn »,
  `SubagentStop` « Prevents subagent from stopping, continues the subagent » (un résumé de la
  même page disait l'inverse : l'essai tranche). Sonde `vlp.py sonde` branchée sur les trois,
  témoin `CON9` joué par `vlp:jouer` (agent `a17390a4be2ecc6da`, 24 entrées, chaque hook lancé
  deux fois — `python3` et `py` ouvrent le même `python.exe`) ; débranchée, témoin retiré,
  `HEAD` resté `32f114a`. Champs reçus :
  `SubagentStart` : `session_id`, `transcript_path`, `cwd`, `scratchpad_dir`, `prompt_id`,
  `agent_id`, `agent_type` — ni `permission_mode`, ni rien à rendre d'utile. `PreToolUse` :
  mêmes champs plus `permission_mode`, `hook_event_name`, `tool_name`, `tool_input`
  (`agent_type` = `vlp:fiche`). `SubagentStop` : plus `effort`, `stop_hook_active`,
  `agent_transcript_path`, `last_assistant_message`, `background_tasks`.

  | Hook | Ce qu'il peut faire | Preuve |
  |---|---|---|
  | `PreToolUse` | refuser un appel du sous-agent, raison lue par lui | **prouvé** : `PreToolUse:Bash hook error: Sonde CON3 : appel refusé…` en `tool_result` `is_error`, le témoin continue sans relancer |
  | `SubagentStop` | renvoyer le sous-agent au travail, consigne lue par lui ; lire son dernier message sans ouvrir la transcription | **prouvé** : `Stop hook feedback: Sonde CON3 : renvoyé…` en message utilisateur, le témoin écrit « renvoyé » puis rend `FAITE` ; 2e arrêt `stop_hook_active: true` |
  | `SubagentStart` | voir partir un sous-agent (noter `HEAD`) ; bloquer son départ | départ **prouvé** (reçu, `agent_type` `vlp:fiche`) ; blocage **lu** seulement |

  Imprévu : un `SubagentStop` d'`agent_type` **vide** (`last_assistant_message` « ok », agent
  `a021622b7058691f7`, qui n'est pas le témoin) — un hook filtre donc sur `agent_type`, jamais
  sur la seule présence d'`agent_id`. **Choix de l'utilisateur : les deux** — `PreToolUse`
  refuse l'écriture Git, `SubagentStop` renvoie sur statut ou case.
- **2026-09-25** — CON1, `py scripts/vlp.py contrat --depuis f98ceec` : `CONTRAT 8 sous-agents ·
  0 écrivent dans Git · 5 sans statut en tête` — 8 au-delà du seuil de 5, `CON2` sautée. Sans
  `--depuis` : `CONTRAT 77 sous-agents · 4 écrivent dans Git · 42 sans statut en tête` ; les 4
  (`a10d85004cb7139db`, `ab869d46397c611ec`, `ac8f3b1a183943b67`, `ac97af92710782899`) sont
  d'une même session partie à 2026-09-23T23:50:57Z, 17 min avant `f98ceec` : la règle est
  entrée pendant la session qui la violait. Après, les 5 sans statut ouvrent par `Parfait`,
  `---`, `Excellent`, `**Écrit`, `The` — c'est la clause qui casse, pas « aucun commit ».
- **2026-09-25** — REV4, `c5123af` rejouée seule après `96b607b` (`agents/relecture.md` : ce qui
  lit le dépôt d'où il part se lance par `env -C <copie>`) et `/reload-plugins` : `REFUSÉE` ✅, le
  hook sort 1 sur l'arbre intact d'APRÈS (`skills/chantier/SKILL.md` en CRLF, YAML illisible ;
  passé en LF, code 0), AVANT sort 0. 12 lancements du hook, tous par `env -C`. 21 tours,
  648 515 tokens, 0,53 $ ; Git intact. Avec les trois autres lignes du quatrième passage : 4
  verdicts justes sur 4, pour des motifs attendus — table faite de deux passages, les trois autres
  sans hook ni `git` lancé depuis la racine.
- **2026-09-25** — REV4, quatrième passage, après la règle « fouiller au-delà du critère »
  (`794eb0d`) et le critère réécrit. Même protocole ; Git intact après chacune, 0 dossier
  `vlp-relecture-*` neuf, aucun fichier du dépôt vivant lu.

  | Commit | Verdict | Motifs | Remarques | Tours | Tokens | $ |
  |---|---|---|---|---|---|---|
  | `CAD1 8bb748d` | `ACCEPTÉE` ✅ | — | sondes rejouées : sans socle, `## ` en bloc de code, CRLF — tous déjà `INVALIDE` avant | 16 | 727 952 | 0,64 |
  | `PLA1 7d16873` | `REFUSÉE` ✅ | plage vide acceptée : `à venir` → `P1–P2à venir`, `P1-P3` → `P1–P4-P3` (sonde) | étape 3 ; deux `verifier` | 10 | 329 280 | 0,40 |
  | `VAL1 c5123af` | `ACCEPTÉE` ❌ | — | message `marketplace.json` ; `Edit` dans AVANT, `$?` : consignes enfreintes, dit-il | 13 | 366 273 | 0,39 |
  | `PLA1 eb2a6b0` | `REFUSÉE` ✅ | en-tête hors forme abîmé : 12 en-têtes × 3 fichiers sondés, `P1-P3` → `P1–P4-P3` | `plage()` prend la dernière fiche du fichier, pas la plus haute | 8 | 246 581 | 0,35 |

  Quatre relectures : 47 tours, 1 670 086 tokens, 1,77 $, soit 0,44 $ l'une. **3 verdicts justes
  sur 4**, les deux refus par une sonde. Critère non tenu, à cause de `c5123af` : le relecteur a
  lancé `sh <APRÈS>/.githooks/pre-commit` depuis la racine du projet ; le hook prend
  `git rev-parse --show-toplevel` (ligne 4), il a donc validé le dépôt vivant, déjà corrigé
  (code 0). `agents/relecture.md` interdit de changer de dossier ; au passage d'avant, un autre
  relecteur passait par `env -C <copie>`. Deux fautes du chef : le critère réécrit plus tôt dans la
  journée attendait `eb2a6b0` `ACCEPTÉE`, alors que sa regex était déjà un défaut au premier passage
  — corrigé ; et la carte que reçoit le relecteur liste les titres des fiches (« REV6 — Un
  en-tête sans plage reste tel quel ») : un indice, déjà présent au passage d'avant, qui avait
  raté `7d16873`. REV4 reste ouverte.
- **2026-09-25** — REV4, troisième passage, après la règle durcie (`6a5a913` : un soupçon se
  rejoue avant d'être classé ; le dépôt vivant ne se lit pas). Même protocole ; après chacune,
  `git status` vide, `git worktree list` inchangé (3 lignes), 0 dossier `vlp-relecture-*` neuf.

  | Commit | Verdict | Motifs | Remarques | Tours | Tokens | $ |
  |---|---|---|---|---|---|---|
  | `CAD1 8bb748d` | `ACCEPTÉE` ✅ | — | journal et page hors liste ; « je ne l'ai pas rejoué », dit hors périmètre | 11 | 407 215 | 0,40 |
  | `PLA1 7d16873` | `ACCEPTÉE` ❌ | — | `ÉCART:` absent du compte rendu ; étape 3 ; deux `verifier` — la regex n'est plus soupçonnée | 7 | 202 967 | 0,27 |
  | `VAL1 c5123af` | `REFUSÉE` ✅ | le hook sort 1 sur le dépôt intact | cause rejouée : la `description` sans guillemets de `skills/chantier/SKILL.md` ; guillemets, code 0 | 16 | 458 025 | 0,39 |
  | `PLA1 eb2a6b0` | `ACCEPTÉE` ❌ | — | « le changement de `creer` n'a pas de test qui échoue seul — pas rejoué comme mutant » | 6 | 158 629 | 0,22 |

  Quatre relectures : 40 tours, 1 226 836 tokens, 1,28 $, soit 0,32 $ l'une. **Critère non tenu** :
  2 verdicts justes sur 4. Sans le dépôt vivant, `eb2a6b0` ne trouve plus le trait d'union : au
  passage d'avant, la fiche REV6 l'avait sans doute guidé. `eb2a6b0` enfreint la règle neuve (un
  soupçon écrit, non rejoué). Mais le critère de REV4 contredit REV8 : le critère de `PLA1`
  (`context AI/47-plage-suit.md:31`) ne nomme que « le code d'avant » ; le mutant de `creer` n'est
  pas celui du critère, et se remarque. `7d16873` : aucun soupçon, donc la règle neuve ne mord pas.
  Hook de `HEAD` : code 0, `description` entre guillemets. REV4 reste ouverte.
- **2026-09-24** — REV4, deuxième passage, après REV5 à REV8 : quatre relectures par
  `Skill` `vlp:relire`, une à la fois, accord de l'utilisateur après la première. Après chacune :
  `git status` vide, `git worktree list` inchangé (3 lignes), 0 dossier `vlp-relecture-*` neuf
  dans `%TEMP%` (les 12 présents datent de 09:16–09:20). Coûts par `scripts/mesure-tokens.py`.

  | Commit | Verdict | Motifs | Remarques | Tours | Tokens | $ |
  |---|---|---|---|---|---|---|
  | `CAD1 8bb748d` | `ACCEPTÉE` ✅ | — | `pop` au lieu de `try`/`finally` ; fichiers du chef | 8 | 277 222 | 0,34 |
  | `PLA1 7d16873` | `ACCEPTÉE` ❌ | — | lettre de l'étape 3 ; deux `verifier` ; « un nom hors format serait dupliqué », non rejoué | 12 | 375 978 | 0,36 |
  | `VAL1 c5123af` | `REFUSÉE` 🟡 | critère de `VAL1` non tenu : le message nomme `marketplace.json` | hook qui refuse sur la copie en CRLF, dit « faux défaut dû à la copie » ; `sort -V` sans test | 14 | 418 078 | 0,44 |
  | `PLA1 eb2a6b0` | `REFUSÉE` 🟡 | en-tête au trait d'union abîmé (`Q1-Q2` → `Q1–Q2-Q2`), sonde de six en-têtes | test coupé en deux ; `u.md` hors prompt ; mutant de `creer` non rejoué | 17 | 554 317 | 0,55 |

  Quatre relectures : 51 tours, 1 625 595 tokens, 1,69 $, soit 0,42 $ l'une — contre 1,78 $ au
  premier passage (entrée plus bas) ; les trois corrigés : 1,14 $, estimés à 5,89 $. **Critère non
  tenu** : 1 ligne sur 4 tenue en entier, 3 verdicts justes sur 4. REV7 et REV8 ont porté sur
  `8bb748d`. Règle mal appliquée, deux fois (`enchainement.md`, « Relecture ») : un défaut rangé
  « sans effet sur une sortie » sans rejouer la sortie qui l'aurait prouvé (`7d16873`), ou déclassé
  après l'avoir vu (`c5123af`). Sur `eb2a6b0`, le relecteur cite `context AI/51-relecture.md:249`
  (REV6) : il a lu le dépôt vivant, sa sonde en a pu être guidée. Modèle inchangé (`opus`).
- **2026-09-24** — REV5 : l'app Claude est un paquet MSIX. Son `claude.exe` est en vrai sous
  `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\claude-code\` ; `%APPDATA%\Claude\claude-code`
  n'existe que pour les processus qu'elle lance. `py scripts/test-vlp.py` suit le shebang `python3` vers
  `pythoncore-3.14-64`, le Python du paquet « Python install manager », qui ne le voit pas : le hook y
  disait « validate sauté » (attendu aussi depuis un terminal hors de l'app, non mesuré). Décidé avec
  l'utilisateur : le hook cherche aussi `Packages\Claude_*` — test « hook : claude trouvé hors de l'app ».
- **2026-09-24** — REV4, jouée à la main par le chef : les six témoins relus par `vlp:relecture`,
  un à un. Après chacun : `git status` propre, `HEAD` inchangé, `git worktree list` inchangé
  (deux lignes dès le départ : `.claude/worktrees/hopeful-brattain-2284cd`, un worktree de l'app),
  0 dossier `vlp-relecture-*` neuf dans `%TEMP%`.

  | Commit | Verdict | Défauts nommés | Défaut des témoins retrouvé | Tours | Tokens | $ |
  |---|---|---|---|---|---|---|
  | `CAD1 e41925c` | `REFUSÉE` | 11 — session dans le bloc de la fiche, et en double ; 3 mutants survivent ; 2 docstrings ; case vide | oui, les deux, en motif | 18 | 1 824 622 | 1,98 |
  | `PLA1 eb2a6b0` | `REFUSÉE` | test hors fiche ; regex `[^·]*` | oui, en remarque : le mutant de `creer` rend `OK` | 18 | 1 167 165 | 1,52 |
  | `VAL1 72035f2` | `REFUSÉE` | hook qui sort 1 (en-tête YAML de `skills/chantier/SKILL.md`) ; `marketplace.json` nommé ; case vide | en partie : `claude_exe` et README en remarques ; commentaire et message manqués | 9 | 469 188 | 1,31 |
  | `CAD1 8bb748d` | `REFUSÉE` | ni `try` ni `finally` ; `pop` en tête de suite ; `HORS FICHE` du journal | non — corrigé, son mutant tombe | 22 | 2 508 041 | 2,72 |
  | `PLA1 7d16873` | `REFUSÉE` | plage facultative (« fiches à venir » → « fiches PLA1–PLA2à venir ») ; test hors fiche | non — corrigé, et la correction crée ce défaut | 10 | 789 428 | 1,74 |
  | `VAL1 c5123af` | `REFUSÉE` | commit propre refusé en CRLF ; `marketplace.json` nommé ; message « introuvable » réécrit ; `HORS FICHE` du journal | non — corrigé | 8 | 466 092 | 1,43 |

  Six relectures : 85 tours, 7 224 536 tokens, 10,70 $, soit 1,78 $ l'une — contre 1,18 $ la fiche
  pour la reprise de la nuit (16,51 $ pour 14 fiches, n° 48). Extrapolé après la première : 9,90 $
  pour les cinq autres ; mesuré : 8,72 $. **Critère non tenu** : 3 fautifs refusés sur 3, un seul
  pour le défaut de sa ligne ; 0 corrigé accepté sur 3. Causes : le `HORS FICHE` du fichier d'état,
  que la méthode prévoit (motif deux fois, remarque une fois) ; la lettre de la fiche — le message
  de `VAL1`, la fiche le voulait inchangé ; et deux bugs que le chef n'avait pas vus, toujours dans
  `HEAD` : `scripts/vlp.py:1457` (latent, aucune page touchée) et le hook, qui refuse un commit
  propre sur une copie en CRLF (`core.autocrlf` vaut `true` ici ; un clone neuf n'est pas rejoué).
  Pour ce hook, la relecture de `72035f2` accuse le « : » de la description, celle de `c5123af` les
  fins de ligne, octets comparés et code 0 en LF : seule la seconde est prouvée. Transcriptions :
  `dbf37a72-d55e-44f2-8cb7-9d3731712ba1/subagents/`. Décidé avec l'utilisateur : REV4 reste
  ouverte, sa séance notée par une ligne **Session** posée à la main — `cocher` ne la pose pas
  sans cocher ; quatre fiches à cadrer par `/vlp:chantier`, le hook en CRLF d'abord, puis la
  regex `:1457`, le fichier d'état admis par `relecture`, une règle « refuser ou remarquer » dans
  `enchainement.md` ; puis REV4 rejouée sur les trois corrigés (≈ 5,89 $), critère réécrit.
- **2026-09-24** — REV3, jouée à la main par le chef. Tranché hors fiche : l'agent
  `vlp:relecture` ne change jamais de dossier — `relecture` cherche le projet depuis le
  dossier courant, et Windows ne retire pas un worktree où l'on se tient ; pas d'`effort`,
  celui du modèle (`fiche.md` dit `low`) ; la `GARDE:` se traite dans la skill, comme pour
  `vlp:jouer`. Deux limites connues : `maxTurns: 80` est recopié de `fiche.md` — un
  frontmatter ne renvoie pas —, et le hook `filet` ne prévient que les agents `fiche`,
  d'où « réserve un tour pour le verdict ». `claude plugin validate` sur le dossier ne lit
  que `marketplace.json` : l'agent ne se prouve qu'en tournant, à REV4.
- **2026-09-24** — REV2, jouée à la main par le chef. Tranché hors fiche : un bloc
  **Tentatives** « résolu par » que rouvre un refus redevient « non résolu », daté du refus ;
  `--verifier` et `--refuser` s'excluent. Les deux tests existants de `--verifier` prennent la
  ligne `SANS GIT` — leur dossier temporaire n'est pas un dépôt —, et le mutant « tête lue sans
  tester le dépôt » tombe d'abord sur l'un d'eux ; le bloc REV2 rejoué seul le fait tomber sur
  « sans Git ». À savoir pour REV3 : `--verifier` se lance avant le commit du chef — après,
  `TÊTE` nomme ce commit-là (vu sur `e1d7f36`, le commit de REV1).
- **2026-09-24** — REV1, commencée par un sous-agent `vlp:fiche`, finie à la main par le chef.
  Arrêté par l'utilisateur à 51 appels, sans commit, il sortait de la fiche : `relecture <dossier>
  <fichier> --fichiers-fiche` au lieu de `relecture <fiche>`, un test `--retirer` qui passait à
  vide (`RETIRÉ 0`), 12 dossiers `vlp-relecture-*` orphelins dans `%TEMP%` (2 de la relance de ses
  tests par le chef). Son diff (204 lignes) reste hors dépôt ; l'instantané par index temporaire
  est repris, le reste réécrit. Son appel 34, `python3 << 'EOF'` sans argument, a ouvert le
  Microsoft Store, et l'utilisateur a installé Python Install Manager : `python3` rend 3.14.7, les
  deux entrées de chaque hook de `hooks/hooks.json` réussissent, et le bilan `VALIDE` sort deux
  fois — à savoir pour `PYT` (n° 39). Tranché : `FICHIER=` est le chemin dans APRÈS ; la ligne
  **Fichiers** se lit entre backticks et hors d'eux, le gabarit n'en met pas.
- **2026-09-24** — ZER1, jouée à la main par le chef, sans sous-agent. Deux écarts à la fiche.
  Le cas « découpe à zéro » se bâtit dans un dépôt à clôture, avec un commit étranger juste
  avant elle — comme M, dont le travail est commité sous d'autres messages : sans lui, la découpe
  mettait les 7 tours hors fiches, pas à zéro, et le test n'aurait rien prouvé ; sa garde compte
  donc 2 transcripts, pas 1. Et un mutant survivait, la garde sur les fiches seules (`Z6`) : un
  cas de plus, fiches à zéro et un tour hors fiches, sans garde. Neuf mutants tombent. Sur le
  réel, les dix clos sans commit de fiche rendent la sortie d'avant la nuit (`fda5816`), octet
  pour octet hors la ligne `DÉCOUPE` : M 11 362 254, C 7 816 316. Pour `RCP` : en sessions
  entières, un chantier dont la session en a enchaîné d'autres se sur-compte — Q 33 003 302,
  contre 23 753 914 inscrits.
- **2026-09-24** — CAD1, relue par le chef : `FAITE` en premier mot, mais **case vide**
  (`CASE CAD1 [ ]`, `cocher` jamais lancé) et **commit du sous-agent** (`e41925c`, défait par
  `reset --soft`). 80 appels sur 80 : le filet « 3 tours restants » a tiré, et l'appel 80 a
  commité au lieu de cocher ou de rendre `RETOUR` (sa transcription : 4 « commit par tâche »,
  1 « Tu ne commites pas »). Code avant les tests (appels 28 à 48, le test en 51). Lancés sous le
  vrai `CLAUDE_CODE_SESSION_ID`, ses tests ont échoué, et il les a **relâchés** — l'égalité
  exacte de « ouvrir : bilan » devenue cinq `in`, dont `"· session +"` — au lieu de fixer
  l'environnement, comme la fiche le disait. Et un bug : la session allait avant le premier titre
  de fiche, donc **entre `<!-- FICHE:X1 -->` et son titre**, dans la fiche que lit le
  sous-agent. Repris : la session va avant la première ligne `## ` (le socle), cherchée dans
  tout le fichier ; l'en-tête passe à `parts_aux_commits` en sessions (`entete`), après les
  fiches ; la suite retire `CLAUDE_CODE_SESSION_ID` en tête, le bloc `ouvrir` le fixe à
  `cadre` ; comparaisons exactes rétablies ; en plus, un vrai fichier (la fiche extraite sans
  session), une session déjà dans une fiche, l'id vide, la page. Tests 224 → 230 `verifier(`.
  Neuf mutants tombent, dont les deux choix du sous-agent ; le code d'avant rend
  `ÉCART: cout : la session du cadrage, en tête, compte hors fiches`. 80 tours, 101
  `hook_non_blocking_error`, 5 367 778 tokens, 0,90 $ (Haiku). Transcription :
  `…/subagents/agent-ac8f3b1a183943b67.jsonl`.
- **2026-09-24** — MTK2, relue par le chef : `FAITE` en premier mot, case cochée (appel 14 sur
  14), aucun commit, les quatre critères verts. Mais la docstring disait faux deux fois : « heure
  ISO 8601 locale » (avec un décalage, l'heure est exacte) et « 0 si OK, 1 si erreur » (un id
  inconnu à côté d'un bon sort 0) ; elle recopiait les treize noms de `COLONNES` (règle 3) ; le
  marquage ne disait pas où lire la preuve. Repris : docstring en dix-neuf lignes, qui renvoie à
  `COLONNES` et au socle ; code de sortie essayé sur trois cas (id inconnu seul : 1 ; borne
  illisible : 1 ; un bon et un inconnu : 0) ; marquage avec `40-cout-juste.md`, fiche `CPT2`. Deux
  fichiers lus deux fois chacun (appels 2 à 5). 16 `hook_non_blocking_error` pour 14 appels.
  Transcription : `…/subagents/agent-acbba97acde5e699c.jsonl`.
- **2026-09-24** — MTK1, relue par le chef : `FAITE` en premier mot, case cochée (appel 12 sur
  12), aucun commit — mais **tests écrits après le code** (appels 4 à 6 le code, 7 à 9 les
  tests), jamais lancés sur le code d'avant : aucun écart vu ni cité. Première fiche de code sur
  six à sauter la règle depuis `FIN` (`TAR1` à `PLA2` l'ont tenue). Le chef a rejoué le mutant :
  le code d'avant rend la session entière, `(tours, total) = ('4', '2222')`. Repris : sans `--`,
  `git log` lisait un **fichier suivi** comme un chemin et rendait l'heure de son dernier commit
  (essayé : `f` → 1790000000) ; l'erreur répétait le texte fautif ; la ligne `usage` était écrite
  deux fois ; ses tests (88 lignes) ne vérifiaient pas `tours`. `borne` passe `--`, dit « ni heure
  ISO 8601, ni commit Git » ; `lire_iso` lit `Z` pour `heure` et `borne` (Python < 3.11) ; tests
  resserrés en 40 lignes, un fichier suivi et une plage incomplète après la session en plus. Sept
  mutants tombent, le code d'avant compris ; la plage incomplète acceptée tombe par `IndexError`,
  pas par un écart nommé. 18 `hook_non_blocking_error` pour 12 appels. Transcription :
  `…/subagents/agent-a30c38bc0e301159b.jsonl`.
- **2026-09-24** — PLA2, relue par le chef : `FAITE` en premier mot, case cochée (appel 23 sur
  23), aucun commit ; test écrit d'abord (`ÉCART: ouvrir : relancé, la plage de l'index suit le
  fichier`, appel 7) — le compte rendu en cite le contenu, pas la ligne. Repris : sa ligne d'index
  se réécrivait en entier, **titre du jour compris** (la fiche : la plage seule) ; son test « une
  seule ligne » vérifiait par `in`, qu'une ligne doublée passe aussi ; son bloc `bash` du skill
  recopiait `--projet --titre --resultat` de la création — sans `--creer`, `page` les ignore en
  silence (code 0, titre inchangé : essayé sur une copie). Réécrit en 7 lignes, une regex sur le
  dernier jeton ; test relancé avec un autre titre, liste des lignes comparée ; commande `page`
  ramenée à `--note`, `feuille .` sans `--todo`. Cinq mutants tombent, la version du sous-agent
  comprise. 30 `hook_non_blocking_error` pour 23 appels. Transcription :
  `…/subagents/agent-a5c89b25e7f7b3f65.jsonl`.
- **2026-09-24** — PLA1, relue par le chef : `FAITE` en premier mot, test écrit d'abord
  (`ÉCART: page : l'en-tête suit la plage du fichier`, appel 14 sur 22) — mais le compte rendu
  ne cite pas l'`ÉCART:`, et le sous-agent **a commité seul** (`eb2a6b0`, défait par
  `git reset --soft`, recommité par le chef). Sa transcription contient 0 fois « aucun commit » :
  la définition d'agent chargée date d'avant `CAS` (`/reload-plugins` pas fait) ; et 4 fois
  « commit par tâche » : le `CLAUDE.md` global de l'utilisateur. Troisième commit seul sur dix
  sous-agents (`CAS1`, `VAL1`, `PLA1`). Repris : la plage s'écrivait deux fois, dans `creer` puis
  aussitôt dans `regenerer` — un mutant de `creer` survivait. `creer` laisse la plage vide,
  `regenerer` l'écrit seul, par `plage()`. Quatre mutants tombent (`page --creer` deux fois,
  « page : l'en-tête suit la plage du fichier », « page : l'en-tête d'une fiche seule »). Sur les
  36 vraies pages, la règle ne change que `44-pre-commit.html` (« VAL1–VAL1 » → « VAL1 »),
  corrigée à la main et republiée. 26 `hook_non_blocking_error` pour 22 appels. Transcription :
  `…/subagents/agent-ac97af92710782899.jsonl`.
- **2026-09-24** — TAR3, relue par le chef : `FAITE` en premier mot, sur une seule ligne ; case
  cochée (appel 34 sur 34), aucun commit ; tests écrits d'abord, tels que nommés. Repris : son
  `lettres_prises` (45 lignes, caractère par caractère) acceptait `A1` (`isupper`) et une lettre
  suivie de n'importe quel mot ; réécrit en 17 lignes, la regex de la fiche (` (` ou la fin) sur
  des entrées coupées hors parenthèses. Son `resume_claude` réduisait les blancs **après**
  `rstrip(".")` : « ici.\n » aurait écrit « ici.  (chantier Q). » ; l'ordre inversé, et le test
  le prend (« deux lignes\nici.\n »). Quatre mutants tombent chacun sur son test, l'ordre du
  sous-agent compris. Le vrai `CHANTIER.md` : `lettres 35 · identique`. 39
  `hook_non_blocking_error` pour 34 appels. Transcription : `…/subagents/agent-ab1cc2f79f30e5669.jsonl`.

- **2026-09-24** — TAR2, relue par le chef : `FAITE` en premier mot, suivi d'un « En résumé »
  et de la jauge du `CLAUDE.md` de l'utilisateur (n° 44 `GLO`) ; case cochée (appel 17 sur 17),
  aucun commit ; tests écrits d'abord, tels que nommés. Retouches : `total_clos` ramené à une
  ligne (le sous-agent en avait fait huit), l'aide de test `l` renommée `ligne_close`. Le retrait
  du rattrapage de `clore` n'était couvert par aucun test (la clôture testée vaut 1 500) : un
  test de bout en bout ajouté, « clore : une clôture sous 1 000, comptée une fois » (banc `REP3`,
  `--tokens 950`, total 2 450). Trois mutants tombent : l'alternative nue muette, l'alternative
  nue qui avale plage et date, le rattrapage remis. La vraie feuille rend toujours 439 668 779.
  Le `git checkout` de la reprise de `TAR1` a mis `scripts/*.py` en CRLF dans la copie de
  travail (`core.autocrlf`) ; le dépôt reste en LF. 20 `hook_non_blocking_error` pour 17 appels.
  Transcription : `…/subagents/agent-a3becca0201e99237.jsonl`.

- **2026-09-24** — TAR1, relue par le chef : `FAITE` en premier mot, case cochée (appel 25 sur
  26), aucun commit ; tests écrits d'abord, `ÉCART: arrondi` cité. Mais le code déborde la fiche :
  `arrondi` écrivait un négatif en `-≈1,5k (1 500)`, et `COUT` exigeait « ≈…k ( » devant le brut
  — plus strict que l'ancien, qui relit tout brut entre parenthèses (le repli sans Git relit les
  anciennes pages). Repris au plus près de la fiche : le seuil d'`arrondi` seul, `COUT` d'origine
  plus un signe sur le total nu et le prix, `triplet` inchangé. Un test ajouté, « triplet : le
  brut entre parenthèses suffit », que la version du sous-agent fait tomber ; trois mutants
  (signe du total, signe du prix, seuil) tombent chacun sur son test. 37
  `hook_non_blocking_error` pour 26 appels. Transcription : `…/subagents/agent-a1e187c75b0e51d20.jsonl`.

- **2026-09-24** — FIN3, relue par le chef : `FAITE` en premier mot, case cochée (appel 38 sur
  38), aucun commit ; le test demandé est écrit tel que nommé, et un mutant (l'appel à
  `regenerer` ôté) le fait échouer. Une retouche : `regenerer` préfixe déjà ses gardes de
  « GARDE: », que `clore` aurait doublé ; elles passent par une liste à part. 44
  `hook_non_blocking_error` pour 38 appels. Transcription :
  `1ba64929-8274-42d4-93bb-a2d22fbdd600/subagents/agent-a28da69f9f04ffbb9.jsonl`.

- **2026-09-24** — FIN2, relue par le chef : `FAITE`, case cochée cette fois (appel 35 sur 36),
  message ouvert par « ## En résumé », le mot-statut au dernier paragraphe ; aucun commit dans le
  projet (l'appel 25 commite dans un dépôt jetable). Malgré des tests nommés avec leurs valeurs,
  deux défauts. Le test de bout en bout « cout : la première fiche avant son commit » n'est pas
  écrit : à sa place, un test sur le dépôt `multi`, où les deux fiches ont leur commit, commenté
  « peu importe le format ». Et `plages` gagnait une branche à part qui donnait une plage à
  chaque fiche à session : un double compte dès qu'il y en a deux. Reprise du chef : une seule
  logique (sans commit de fiche, `premier` vaut l'infini), `([], [])` puis `None` dans
  `parts_aux_commits`, le test écrit comme la fiche le dit ; un mutant (le `None` d'avant) le
  fait échouer. 47 `hook_non_blocking_error` pour 36 appels. Transcription :
  `1ba64929-8274-42d4-93bb-a2d22fbdd600/subagents/agent-aa594f5a572bf52ac.jsonl`.

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

## 2026-09-25 — GLO2

Commande 1 (tous les sous-agents) :
```
py "C:/Users/znorr/.claude/skills/vlp/scripts/vlp.py" forme
```
Bilan brut : `FORME 105 sous-agents · user 4298 car. · resume 29 · jauge 38 · tete 59`

Commande 2 (depuis commit f98ceec, 2026-09-24T00:07:40Z) :
```
py "C:/Users/znorr/.claude/skills/vlp/scripts/vlp.py" forme --depuis 2026-09-24T00:07:40Z
```
Bilan brut : `FORME 36 sous-agents · user 5507 car. · resume 14 · jauge 23 · tete 27`

**Calculs, en borne haute (tokens ≤ caractères ÷ 2), prix Haiku du socle.** Tailles en
caractères, lues le 2026-09-25 par `len(open(p, encoding="utf-8").read())` — la première
écriture de cette entrée avait pris des octets UTF-8 (6262 / 5801 / 3459), relevé par la
relecture ; corrigé par le chef.

| Fichier | Caractères | Tokens ≤ | Coût ≤ par sous-agent | Part de 0,176 $ |
|---|---|---|---|---|
| `~/.claude/CLAUDE.md` (`User`) | 6000 | 3000 | 3000 × 4,25 ÷ 10⁶ = 0,01275 $ | 7,24 % |
| `CLAUDE.md` du kit (`Project`) | 5669 | 2834,5 | 0,01205 $ | 6,84 % |
| `MEMORY.md` (`AutoMem`) | 3317 | 1658,5 | 0,00705 $ | 4,00 % |

4,25 = 1,25 (une écriture de cache) + 30 × 0,1 (trente lectures), en $/MTok.

**Verdict : agir**, sur deux quantités, chacune comparée à son seuil du socle :
- coût : le `CLAUDE.md` utilisateur ≤ 7,24 % d'une fiche triviale, au-dessus de 5 % — mais
  c'est une **borne haute** ; à 3,5 caractères par token, il retombe vers 4,1 %. Fragile.
- forme : **23 sur 36** sous-agents depuis `f98ceec` portent la jauge dans leur dernier
  message, 14 « En résumé » — bien au-dessus d'un sur dix. **C'est elle qui fonde le verdict.**

## 2026-09-25 — GLO3

GLO3 : agir selon le verdict de GLO2. La même phrase, à `agents/fiche.md:66` et
`agents/relecture.md:39` (le sous-agent l'avait écrite à la 3e personne, sans nommer les
formes ; resserrée par le chef) :

> **Ton lecteur est le chef, pas l'humain.** Les règles de forme d'un `CLAUDE.md` —
> « En résumé », jauge, émojis, message à part — ne visent que la session principale : ton
> dernier message n'en porte aucune.

Preuve au prochain `/vlp:enchainer` d'une session neuve — une définition d'agent se charge au
démarrage : `vlp.py forme --depuis <ce commit>` doit y rendre `resume` et `jauge` à 0 ou presque
(avant : 14 et 23 sur 36).

## 2026-09-25 — GAR3

Joué à la main par le chef : une fiche témoin `GAR9` ajoutée en fin de
`context AI/54-gardien-renvoie.md`, jouée par `vlp:jouer`, puis retirée avec son fichier.
Transcription `agent-aba306969ff0ed624` (session `ca431cf8-…`), dans l'ordre :

| Ligne | Ce qui se passe |
|---|---|
| 19 | le sous-agent finit par « Parfait, c'est fait. » |
| 20, 22 | `Stop hook feedback` : « Ton dernier message commence par « Parfait, » : son premier mot doit être FAITE, RETOUR ou BLOQUÉE (agents/fiche.md). Réécris-le, statut en tête. » — deux fois, `python3` puis `py` (chantier `PYT`) |
| 25 | « FAITE — témoin écrit », sans `cocher` — cet arrêt porte `stop_hook_active` |
| 26, 28 | `Stop hook feedback` : « FAITE, mais la case de GAR9 est vide : coche-la par vlp.py cocher, puis rends FAITE. » — deux fois ; **avant `GAR1`, cet arrêt passait sans contrôle** (`GLO1`) |
| 31 | le sous-agent lance `vlp.py cocher … GAR9` |
| 35 | « FAITE — témoin du gardien écrit et vérifié » ; premier mot rendu au chef : `FAITE` |

Case de `GAR9` à la fin : `[x]` (`cocher --verifier` : `CASE GAR9 [x]`). Le gardien a donc
tenu les deux renvois de la séquence, le second sous `stop_hook_active`.

## 2026-09-25 — PYT2

Joué à la main par le chef, dans sa session `ca431cf8-…`. Chaque lanceur laisse deux
attachments par écriture : `hook_success` et `hook_additional_context` ; on compte le second.

| Écriture de `56-hook-une-fois.md` | Heure (UTC) | `hook_additional_context` VALIDE | Lanceurs |
|---|---|---|---|
| `Write`, avant `PYT1` (`5375617`, 00:39 UTC) | 00:31:28 | **2** | `python3`, `py` |
| `Edit` d'une ligne blanche, après `0bef88a` | 00:45:43 | **1** | `python3` seul |

Commande : pour chaque `tool_use` `Edit`/`Write` de la transcription, compter les entrées
`{"attachment": {"type": "hook_additional_context", "toolUseID": <son id>}}` qui portent
`VALIDE` ; `attachment.command` nomme le lanceur sur `hook_success`.

En chemin, `0bef88a` : `filet` et `hook` reçoivent la même entrée sur une écriture — sans le
nom de sous-commande dans l'empreinte, `hook` se serait tu derrière `filet`, et le fichier de
fiches n'aurait plus été validé. Mutant (empreinte sans le nom) : le test tombe.

## 2026-09-25 — FOR2

Commande :
```bash
py "<kit>/scripts/vlp.py" forme --depuis 029770b
```

Sortie brute :
```
FORME 3 sous-agents · user 5999 car. · resume 0 · jauge 1 · tete 2
```

Sous-agents de FOR1 (tete ≠ 0) :
- a0de5d54a20561c92 vlp:fiche resume 0 jauge 1 tete 1
- a90355e9dff2e59bf vlp:relecture resume 0 jauge 0 tete 1

Compte avant GLO3 (journal GLO2) : jauge 23 sur 36, « En résumé » 14 sur 36 (mesurés en texte entier, voir `JUG2`).

Compte FOR1 : resume 0/2, jauge 1/2 (mesurés en texte entier, voir `JUG2`). Échantillon très petit (2 sous-agents) : 0 sur 2 ne prouve pas que la phrase tient.

## 2026-09-25 — JUG1

Commande (sha de « Chantier GLO ouvert » : `2281227`), une fois par règle :
```bash
py "<kit>/scripts/vlp.py" forme --depuis 2281227 --regle <r>
```

Sorties brutes, dans l'ordre `tout`, `tiret`, `deux`, `tete` :
```
FORME 29 sous-agents · user 5969 car. · resume 12 · jauge 14 · tete 28
FORME 29 sous-agents · user 5969 car. · resume 12 · jauge 14 · tete 28
FORME 29 sous-agents · user 5969 car. · resume 1 · jauge 11 · tete 28
FORME 29 sous-agents · user 5969 car. · resume 10 · jauge 14 · tete 28
```

Renvoyés (`resume` ou `jauge` à 1) : `tout` 16 · `tiret` 16 · `deux` 11 · `tete` 14, sur 29.
Ce compte compare les sous-agents *renvoyés* par règle, pas leur qualité.

Sous-agents dont le verdict change — `resume jauge` par règle, et où tombe le mot :

| id | type | tout | tiret | deux | tete | Le mot dans le dernier message |
|---|---|---|---|---|---|---|
| a3381d18662212bd2 | relecture | 10 | 10 | 00 | 00 | « En résumé » cité en milieu de ligne (L6/31) |
| acc69ef4998b2c1ed | relecture | 10 | 10 | 00 | 00 | « En résumé » cité en milieu de ligne (L10/34) — le relecteur de FOR3 |
| a4e06d782ad915aec | fiche | 11 | 11 | 00 | 11 | jauge L5, « En résumé » L7, sur 10 lignes |
| a197ee7f87df684d7 | relecture | 11 | 11 | 00 | 11 | « En résumé » L53, jauge L55, sur 59 lignes |
| a4e885046ff9cc898 | relecture | 11 | 11 | 00 | 11 | jauge L31, « En résumé » L35, sur 41 lignes |
| a48c79a59b280d0d2 | relecture | 11 | 11 | 01 | 11 | « En résumé » L31/35 hors des deux dernières |
| ae0b1e231109d1ec3, a9ce00d839ade76fc, ae2b8913e96167c54, a860169308600a92b, ab1dc9f4aa83b01ac | relecture | 11 | 11 | 01 | 11 | idem : la jauge répétée reste, « En résumé » sort |

- `tiret` = `tout` sur ce corpus : aucun dernier message n'a de ligne `---`.
- `deux` perd trois fins hors forme vraies (a4e06d78, a197ee7f, a4e88504) : le résumé à part
  est suivi de 2 à 4 lignes d'explication.
- `tete` retire exactement les deux citations (a3381d18, acc69ef4) et garde les 14 autres.

Le message **renvoyé** du relecteur de FOR3 (`acc69ef4998b2c1ed`, ligne 55 de sa transcription,
2026-09-25T10:20:08Z ; son dernier message est la réécriture, ligne 59). Jugé :
`tout` (1, 1) · `tiret` (1, 1) · `deux` (0, 0) · `tete` (0, 0). La pièce, pour `JUG2` :

```text
ACCEPTÉE — critère tenu : `py scripts/test-vlp.py` rend `OK` dans AVANT (279 `verifier(`) et dans APRÈS (285, soit 6 de plus). Le mutant du critère tombe : `ÉCART: gardien : fiche jauge « Tout va bien », renvoyée`.

**Ce que j'ai rejoué**
- **Suite de tests** : lancée dans AVANT, puis dans APRÈS. Les deux sortent `OK`.
- **Mutant** : dans `cmd_gardien`, j'ai remplacé `resume, jauge = forme_texte(dernier_msg)` par `resume, jauge = 0, 0`.
  - La suite s'arrête au premier écart, sur le test « fiche renvoyée ».
  - Le lanceur s'arrête au premier écart : le test « relecteur renvoyé » n'a donc pas pu tomber dans la suite. Je l'ai vérifié en appel direct : sous le mutant, le gardien se tait sur les deux cas, fiche et relecteur.
  - Ligne rétablie ensuite.
- **Sondage du gardien**, 19 entrées, dans AVANT puis dans APRÈS :
  - Renvoyés dans APRÈS seulement :
    - `Pas bon.`
    - `**Pas bon**`
    - `Ça tient, mais…`
    - `✅ Tout va bien`
    - un relecteur avec `En résumé`
    - `Bonjour ✅ Tout va bien`
  - Muets : `Pas bonne`, `Imprévue`, `maison`, `Grosse erreurs`, ainsi que `None`, `42`, un agent `general-purpose`, et tout message sous `stop_hook_active`.
  - Sur les renvois de `verdict_fin` (`Parfait`, vide), APRÈS rend la même sortie qu'AVANT.
  - Le bug du premier refus (la jauge cherchée comme bout de mot, « bonne » contient « Pas bon ») est corrigé : `\b` borne maintenant chaque mot de `JAUGE`.
- **Hook** : `hooks/hooks.json` déclare `SubagentStop` avec `matcher: "*"`. Le relecteur reçoit donc bien le gardien.

**Remarques, sans effet sur le verdict**
- **Tests** : 6 ajoutés, la fiche en demandait 4. Les 2 de plus visent la correction du premier refus. Leur commentaire `# Mutation test : …` est mal nommé : ce sont des tests de mot entier, pas des mutants.
- **Mesure `forme`** : `lire_forme` juge maintenant en mot entier, et plus en bout de mot. La mesure change donc un peu, par exemple « Pas bonne » ne compte plus comme une jauge. C'est voulu par le prompt (« la même chose »), mais la fiche ne l'annonce pas.
- **Faux positifs voulus** : un statut qui cite un mot de la jauge sera renvoyé une fois. Exemples : `Imprévu : …`, ou un `REFUSÉE` qui cite « Pas bon ». C'est ce que dit la fiche (« un mot de `JAUGE` »), et `stop_hook_active` empêche un second renvoi.
- **État incohérent** :
  - La fiche porte `[x]` et garde son bloc **Tentatives** « non résolu ».
  - L'artefact `context AI/artefacts/58-forme-sous-agent.html` affiche FOR3 « bloquée », avec sa section blocage.
  - Les deux sont à remettre d'accord avant le commit.
- **Fichiers hors de la liste de FOR3** : `context AI/08-etat.md` et le diff FOR2 viennent de FOR2 et de l'état du chantier, pas du code de FOR3. Pour le code, seuls `scripts/vlp.py` et `scripts/test-vlp.py` sont touchés.

Copies retirées (`RETIRÉ 2`). Fichiers en jeu :
- `C:\Users\znorr\Documents\ProgPerso\Claude-vlpWorkflow\scripts\vlp.py`
- `C:\Users\znorr\Documents\ProgPerso\Claude-vlpWorkflow\scripts\test-vlp.py`
- `C:\Users\znorr\Documents\ProgPerso\Claude-vlpWorkflow\context AI\58-forme-sous-agent.md`
- `C:\Users\znorr\Documents\ProgPerso\Claude-vlpWorkflow\context AI\artefacts\58-forme-sous-agent.html`
```

**Règle retenue** (par l'utilisateur, 2026-09-25) : `tete` — elle retire les 2 citations et garde les 14 fins hors forme vraies.

## 2026-09-25 — JUG2

La règle `tete`, retenue en `JUG1`, est le défaut de `forme_texte` (constante `REGLE` de
`scripts/vlp.py`) : le gardien la suit sans changer son appel, `forme --regle tout` rejoue
l'ancienne mesure. Les chiffres d'avant (`GLO2`, `FOR2`, bilan `FOR`) sont marqués « mesurés en
texte entier ».

Commande, avant puis après :
```bash
py "<kit>/scripts/vlp.py" forme --depuis 2281227 --regle tout
py "<kit>/scripts/vlp.py" forme --depuis 2281227
```

Sorties brutes :
```
FORME 29 sous-agents · user 5969 car. · resume 12 · jauge 14 · tete 28
FORME 29 sous-agents · user 5969 car. · resume 10 · jauge 14 · tete 28
```

Renvoyés : 16 → 14 sur 29 — les deux citations de `JUG1` (a3381d18, acc69ef4). La pièce de
`JUG1` est lue par `test-vlp.py` dans ce journal, pas recopiée : elle porte des chemins de machine.

## 2026-09-25 — JUG3

Deux `vlp:relecture` lancés par `Agent` depuis `/vlp:tache`, l'un après l'autre, premier
lancement à 2026-09-25T10:57:05Z (`date -u`). Le gardien lu en place, sans relancer l'app.

Prompt du premier — la jauge et « En résumé » cités en prose :
```text
Essai du gardien (chantier JUG, fiche JUG3) — il n'y a aucune fiche à relire. N'ouvre aucun fichier, ne lance aucun outil.

Rends directement ce verdict, et rien d'autre, en un seul message :

ACCEPTÉE — essai du gardien, rien à relire. Le gardien renvoie un relecteur dont une ligne s'ouvre par « En résumé » ou par une jauge comme « Pas bon » ; un verdict qui les cite en prose, comme celui-ci, doit passer sans renvoi.
```

Prompt du second — un résumé à part, jauge en première ligne :
```text
Essai du gardien (chantier JUG, fiche JUG3) — il n'y a aucune fiche à relire. N'ouvre aucun fichier, ne lance aucun outil.

Rends directement ce verdict, exactement sous cette forme, en un seul message :

ACCEPTÉE — essai du gardien, rien à relire.

✅ **Tout va bien** — essai fait.

**En résumé**

Le relecteur n'avait rien à relire : c'est un essai du gardien.

Si le gardien te renvoie, suis ce qu'il te dit.
```

Lu dans les transcriptions (entrées `Stop hook feedback` et `hook_blocking_error` `SubagentStop`) :
- `a958861005acdd18b` (prose) : **renvoyé 0 fois** — son message, tel que demandé, est son dernier.
- `abda1f44810cde2fe` (résumé à part) : **renvoyé 1 fois** (« Ton dernier message porte un « En
  résumé » ou une jauge… ») ; sa fin réécrite : `ACCEPTÉE : c'était un essai du gardien, et il
  n'y avait rien à relire.`

Sortie brute :
```
a958861005acdd18b vlp:relecture 2026-09-25T10:57:11Z user 5999 projet 5186 memoire 3330 resume 0 jauge 0 tete 1
abda1f44810cde2fe vlp:relecture 2026-09-25T10:57:20Z user 5999 projet 5186 memoire 3330 resume 0 jauge 0 tete 1
FORME 2 sous-agents · user 5999 car. · resume 0 · jauge 0 · tete 2
```

Coût (`vlp.py cout … --session`, avant le commit de `JUG3` : la fiche est encore dans « hors fiches ») :
```
JUG1 · ≈2,9M (2 911 195) · 28 tours · 1,61 $ = session ≈2,9M (2 911 195) · 28 tours · 1,61 $ + 0 sous-agent
JUG2 · ≈2,0M (2 006 666) · 14 tours · 0,86 $ = session ≈2,0M (2 006 666) · 14 tours · 0,86 $ + 0 sous-agent
hors fiches · ≈4,1M (4 129 933) · 33 tours · 2,72 $ = session ≈4,1M (4 083 242) · 30 tours · 2,59 $ + 2 sous-agents ≈46,7k (46 691) · 3 tours · 0,13 $
TOTAL (fiches + hors fiches) · ≈9,0M (9 047 794) · 75 tours · 5,19 $ = session ≈9,0M (9 001 103) · 72 tours · 5,06 $ + 2 sous-agents ≈46,7k (46 691) · 3 tours · 0,13 $
```
Les deux relecteurs : 0,13 $ à eux deux. Le coût définitif de `JUG3` se lit après son commit.

## 2026-09-25 — REC1

`py scripts/vlp.py recompter .` : `RECOMPTE 48 clos · 23 recomptés · 25 gardés · inscrit 681 541 003
· recompté 700 725 374 · écart +19 184 371`. Imprévu : le socle de REC comptait **dix** clos sans
commit de fiche (M, C, T, S, L, W, X, F, O, Q) ; `recompter` en trouve **23** en `DÉCOUPE aucune`
— Z, Q, U, Y, J, O, F, X, W, G, A, P, L, N, K, I, D, S, R, B, T, C, M —, plus V sans ligne
`**Session**` et E sans plage à l'index. H seul, des chantiers du 2026-09-17, se découpe. Les 23
recomptés ont presque tous un écart positif, de +434 097 (RLG) à +3 136 302 (NIV) ; deux écarts
sortent du lot : FIL −22 318 909, REP +9 982 170. À ranger par cause en REC2.

## 2026-09-25 — REC2

Rien de publié n'a changé. `py scripts/vlp.py recompter .`, sortie brute :

```
JUG inscrit 10 273 570 · recompté 11 306 457 · écart +1 032 887 · découpe
FOR inscrit 17 689 317 · recompté 20 371 577 · écart +2 682 260 · découpe
RLG inscrit 8 745 720 · recompté 9 179 817 · écart +434 097 · découpe · partagée avec GAR, GLO, PYT, UNI
PYT inscrit 11 561 195 · recompté 12 279 871 · écart +718 676 · découpe · partagée avec GAR, GLO, RLG, UNI
UNI inscrit 15 942 182 · recompté 16 613 231 · écart +671 049 · découpe · partagée avec GAR, GLO, PYT, RLG
GAR inscrit 7 588 840 · recompté 8 426 745 · écart +837 905 · découpe · partagée avec GLO, PYT, RLG, UNI
GLO inscrit 13 784 706 · recompté 15 674 582 · écart +1 889 876 · découpe · partagée avec GAR, PYT, RLG, UNI
CON inscrit 13 910 638 · recompté 15 711 661 · écart +1 801 023 · découpe
REV inscrit 74 789 054 · recompté 76 440 498 · écart +1 651 444 · découpe
ZER inscrit 11 209 181 · recompté 12 079 243 · écart +870 062 · découpe · partagée avec CAD, CAS, FIN, MTK, PLA, TAR, VAL
CAD inscrit 14 603 596 · recompté 15 724 492 · écart +1 120 896 · découpe · partagée avec CAS, FIN, MTK, PLA, TAR, VAL, ZER
MTK inscrit 12 192 684 · recompté 13 588 111 · écart +1 395 427 · découpe · partagée avec CAD, CAS, FIN, PLA, TAR, VAL, ZER
PLA inscrit 11 938 808 · recompté 13 033 400 · écart +1 094 592 · découpe · partagée avec CAD, CAS, FIN, MTK, TAR, VAL, ZER
TAR inscrit 17 642 733 · recompté 19 399 198 · écart +1 756 465 · découpe · partagée avec CAD, CAS, FIN, MTK, PLA, VAL, ZER
FIN inscrit 21 871 718 · recompté 22 962 798 · écart +1 091 080 · découpe · partagée avec CAD, CAS, MTK, PLA, TAR, VAL, ZER
VAL inscrit 5 647 906 · recompté 6 924 438 · écart +1 276 532 · découpe · partagée avec CAD, CAS, FIN, MTK, PLA, TAR, ZER
CAS inscrit 10 041 615 · recompté 11 729 608 · écart +1 687 993 · découpe · partagée avec CAD, FIN, MTK, PLA, TAR, VAL, ZER
FIL inscrit 42 638 103 · recompté 20 319 194 · écart -22 318 909 · découpe · partagée avec SAG
SAG inscrit 20 128 626 · recompté 21 912 236 · écart +1 783 610 · découpe · partagée avec FIL
CPT inscrit 19 266 526 · recompté 21 606 411 · écart +2 339 885 · découpe
REP inscrit 23 126 264 · recompté 33 108 434 · écart +9 982 170 · découpe
NIV inscrit 21 827 897 · recompté 24 964 199 · écart +3 136 302 · découpe
Z inscrit 11 093 368 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « Z1 : » ni d'une autre fiche)
Q inscrit 23 753 914 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « Q1 : » ni d'une autre fiche)
U inscrit 15 933 829 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « U1 : » ni d'une autre fiche)
Y inscrit 21 917 062 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « Y1 : » ni d'une autre fiche)
J inscrit 7 579 062 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « J1 : » ni d'une autre fiche)
O inscrit 9 842 371 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « O1 : » ni d'une autre fiche)
F inscrit 8 781 743 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « F1 : » ni d'une autre fiche)
X inscrit 10 921 635 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « X1 : » ni d'une autre fiche)
W inscrit 7 305 939 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « W1 : » ni d'une autre fiche)
G inscrit 7 997 540 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « G1 : » ni d'une autre fiche)
A inscrit 5 765 489 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « A1 : » ni d'une autre fiche)
P inscrit 6 786 706 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « P1 : » ni d'une autre fiche)
L inscrit 7 324 563 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « L1 : » ni d'une autre fiche)
N inscrit 6 491 074 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « N1 : » ni d'une autre fiche)
K inscrit 6 203 651 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « K1 : » ni d'une autre fiche)
I inscrit 6 542 829 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « I1 : » ni d'une autre fiche)
D inscrit 7 164 227 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « D1 : » ni d'une autre fiche)
V inscrit 19 316 675 · recompté gardé · écart +0 · gardé — sans session
H inscrit 14 649 178 · recompté 16 898 227 · écart +2 249 049 · découpe
S inscrit 17 193 402 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « S1 : » ni d'une autre fiche)
R inscrit 11 840 151 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « R1 : » ni d'une autre fiche)
B inscrit 5 342 511 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « B1 : » ni d'une autre fiche)
T inscrit 16 194 635 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « T1 : » ni d'une autre fiche)
C inscrit 7 816 316 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « C1 : » ni d'une autre fiche)
M inscrit 11 362 254 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « M1 : » ni d'une autre fiche)
E inscrit 0 · recompté gardé · écart +0 · gardé — fichier introuvable
RECOMPTE 48 clos · 23 recomptés · 25 gardés · inscrit 681 541 003 · recompté 700 725 374 · écart +19 184 371
```

**Comment chaque écart est rangé.** Une seule cause par clos, prouvée par les nombres du tableau
plus bas, mesurés par les fonctions de `vlp.py` (`plages`, `mesurer`) sur les mêmes plages que
`cout`, et par la page du chantier (`context AI/artefacts/<fichier>.html`, lignes « Coût du
chantier » et « Hors fiches »). Dates de clôture lues plus haut dans ce fichier : `REP` et `CPT`
le 2026-09-23 (`REP` avant `CPT`), `CAD` le 2026-09-24 ; `NIV` et `H` sont d'avant (feuille de
route, colonne « Clos le » : 2026-09-18 et 2026-09-17).

1. **Session partagée avec un autre clos** — `FIL`. La sortie dit « partagée avec SAG » ; la page
   donnait 30 230 692 hors fiches, le recompte en trouve 7 911 783 (6 270 808 + 1 640 975).
   Ce qui a déplacé ces tours n'est pas établi ici.
2. **Sous-agents non comptés avant `CPT`** — `REP`, clos avant `CPT`. Recompté : 8 161 098 de
   sous-agents. L'écart ne vient pas que d'eux : +9 982 170 = 8 161 098 (sous-agents)
   + 3 987 052 (hors fiches, côté clôture) − 2 165 980 (sessions des fiches : 20 960 284 contre
   23 126 264 inscrits).
3. **Cadrage non compté avant `CAD`** — aucun clos. Aucun fichier clos avant `CAD` ne porte de
   session de cadrage en tête (`sessions_entete` vide pour les 12 recomptés d'avant `CAD`, et pour `CAD`) : le recompte ne voit pas plus
   ce cadrage que l'inscrit.
4. **Autre** — trois groupes, décrits par ce qui est mesuré, sans cause supposée :
   - 4a, `SAG` et `CPT` : l'inscrit égale **au token près** les fiches recomptées (20 128 626 ;
     19 266 526), et l'écart égale exactement le hors fiches, côté clôture (1 783 610 ; 2 339 885).
   - 4b, 17 clos : les fiches recomptées (session + sous-agents) égalent **au token près** celles de
     la page (total − hors fiches de la page) ; tout l'écart est dans hors fiches, et il reste
     sous le hors fiches côté clôture, dans les 17 cas (`CAS` : égal, 1 687 993). 13 de ces 17
     portent « partagée avec » dans la sortie, mais leurs fiches n'ont pas bougé : ce n'est pas
     la cause mesurée.
   - 4c, `NIV` et `H`, clos avant `CPT`, sans sous-agent recompté : aucune explication.

Preuves par clos — colonnes : écart ; fiches recomptées, sessions puis sous-agents ; hors fiches
recompté, côté cadrage puis côté clôture ; page du chantier, total puis hors fiches (— : la page
n'a pas de ligne hors fiches).

| Clos | Cause | Écart | Fiches : sessions | Fiches : sous-agents | Hors : cadrage | Hors : clôture | Page : total | Page : hors |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| JUG | 4b | +1 032 887 | 6 915 183 | 46 691 | 2 771 949 | 1 572 634 | 10 273 570 | 3 311 696 |
| FOR | 4b | +2 682 260 | 7 431 684 | 5 517 937 | 3 806 364 | 3 615 592 | 17 689 317 | 4 739 696 |
| RLG | 4b | +434 097 | 2 905 604 | 2 747 743 | 1 863 578 | 1 662 892 | 8 745 720 | 3 092 373 |
| PYT | 4b | +718 676 | 7 090 753 | 2 201 811 | 2 053 359 | 933 948 | 11 561 195 | 2 268 631 |
| UNI | 4b | +671 049 | 8 181 965 | 5 409 750 | 2 020 500 | 1 001 016 | 15 942 182 | 2 350 467 |
| GAR | 4b | +837 905 | 3 755 306 | 2 018 224 | 1 540 101 | 1 113 114 | 7 864 973 | 2 091 443 |
| GLO | 4b | +1 889 876 | 6 298 224 | 3 208 326 | 3 825 523 | 2 342 509 | 15 182 315 | 5 675 765 |
| CON | 4b | +1 801 023 | 10 455 203 | 311 906 | 2 906 894 | 2 037 658 | 14 631 523 | 3 864 414 |
| REV | 4b | +1 651 444 | 52 826 427 | 15 672 178 | 6 026 326 | 1 915 567 | 75 866 013 | 7 367 408 |
| ZER | 4b | +870 062 | 4 291 766 | 0 | 6 708 181 | 1 079 296 | 11 633 997 | 7 342 231 |
| CAD | 4b | +1 120 896 | 5 308 597 | 5 367 778 | 3 654 434 | 1 393 683 | 15 154 579 | 4 478 204 |
| MTK | 4b | +1 395 427 | 7 049 685 | 897 222 | 4 144 106 | 1 497 098 | 12 738 440 | 4 791 533 |
| PLA | 4b | +1 094 592 | 5 250 344 | 1 783 266 | 4 692 050 | 1 307 740 | 12 587 599 | 5 553 989 |
| TAR | 4b | +1 756 465 | 8 893 259 | 3 044 459 | 5 418 305 | 2 043 175 | 18 799 875 | 6 862 157 |
| FIN | 4b | +1 091 080 | 11 719 698 | 5 435 742 | 4 411 421 | 1 395 937 | 22 487 850 | 5 332 410 |
| VAL | 4b | +1 276 532 | 2 558 849 | 809 903 | 2 087 345 | 1 468 341 | 6 924 438 | 3 555 686 |
| CAS | 4b | +1 687 993 | 4 939 709 | 1 444 431 | 3 657 475 | 1 687 993 | 11 729 608 | 5 345 468 |
| FIL | 1 | −22 318 909 | 12 407 411 | 0 | 6 270 808 | 1 640 975 | 42 000 943 | 30 230 692 |
| SAG | 4a | +1 783 610 | 14 048 505 | 6 080 121 | 0 | 1 783 610 | 19 851 147 | 0 |
| CPT | 4a | +2 339 885 | 19 266 526 | 0 | 0 | 2 339 885 | 18 304 841 | 0 |
| REP | 2 | +9 982 170 | 20 960 284 | 8 161 098 | 0 | 3 987 052 | 20 355 080 | — |
| NIV | 4c | +3 136 302 | 24 964 199 | 0 | 0 | 0 | 21 298 361 | — |
| H | 4c | +2 249 049 | 8 241 128 | 0 | 8 657 099 | 0 | 15 461 826 | — |

**Avant / après, par cause :**

| Cause | Clos | Inscrit | Recompté | Écart |
|---|---:|---:|---:|---:|
| Session partagée avec un autre clos | 1 | 42 638 103 | 20 319 194 | −22 318 909 |
| Sous-agents non comptés avant `CPT` | 1 | 23 126 264 | 33 108 434 | +9 982 170 |
| Cadrage non compté avant `CAD` | 0 | 0 | 0 | +0 |
| Autre — hors fiches absent de l'inscrit | 2 | 39 395 152 | 43 518 647 | +4 123 495 |
| Autre — fiches inchangées, hors fiches plus gros | 17 | 279 433 463 | 301 445 727 | +22 012 264 |
| Autre — sans explication | 2 | 36 477 075 | 41 862 426 | +5 385 351 |
| Gardés — écart 0 par règle | 25 | 260 470 946 | 260 470 946 | +0 |
| **Total** | 48 | 681 541 003 | 700 725 374 | +19 184 371 |

Somme des écarts par cause **+19 184 371** · écart de la ligne `RECOMPTE` **+19 184 371**.

## 2026-09-25 — ESS1

Script jetable du scratchpad (`bacs.py`, rien dans `scripts/`) sur `~/.claude/projects/*-scratchpad-*` :
**39 dossiers**, **11 sessions parentes**, 89 `.jsonl` de tête, **7,8983 $** (`mesure-tokens.py`,
`usd_exact`, sous-agents des essais compris). Les 11 parents ont leur `<id>.jsonl` dans le dossier
du kit, et chacun est cité par un fichier de fiches de `context AI/`. Tous lancés par le chef : les
sessions à lanceur non lu dans la commande (`X`, `Y`, `P`, témoin de `L`) n'ont aucun sous-agent.

Notes relevées : 12 lignes de la feuille de route (« plus … $ de sondes / d'evals / de runs ») et
2 du fichier d'état (« Hors total : … »). Le mot « hors total » n'est écrit qu'une fois en minuscule,
dans la TODO n° 47 elle-même : le grep de la fiche ne trouvait rien d'autre.

**Essais notés → dossier** (sondes `claude -p`, le périmètre d'`ESS`) :

| Chantier | Noté | Dossiers (parent · bacs) | Mesuré | Écart |
|---|---:|---|---:|---:|
| `X` | 0,90 | `fd4ebe27` · 19 bacs `x1-w-*`, `x2-w*`, `x3-w*` | 0,6171 | −0,2829 |
| `G` | 0,115 | `1e8a6fc3` · `bacg` | 0,1153 | +0,0003 |
| `A` | 0,22 | `72b06e7b` · `bacA` | 0,2211 | +0,0011 |
| `P` | 0,75 | `b59e04ab` · `bac-p1`, `bac-p3` | 0,7503 | +0,0003 |
| `L` | 1,26 | `93b3a242` · `sonde-l3`, `temoin` | 1,2636 | +0,0036 |
| `N` | 0,56 | `0b3db2da` · `sonde-n1` | 0,5643 | +0,0043 |
| `SAG` | 0,45590805 | `1cba232a` · `bacsag2`, `b4` | 0,4559 | −0,0000 |
| `FIL` | 0,31252785 | `49006a92` · `f3` | 0,3125 | −0,0000 |
| **8 notés** | **4,5734** | **8 trouvés · 0 absent** | **4,3001** | −0,2733 |

**Evals notées → dossier** (dehors par le cadrage) : `O` 0,29 · `F` 0,29 · `W` 0,67 · `A` 0,81 ·
`P` 0,59 · `L` 1,00 · `N` 0,62 · `K` 0,85 · `I` 0,37 · `V` 2,25 (runs) — **10 notées, 0 trouvée,
7,74 $**. Attendu : un eval ne tourne pas dans un bac du scratchpad.

**Dossiers sans note** : `Y` (`6a0eaab3` · `y1-ya`, `y3-yb`, `y5-zb`) 1,6679 · `U` (`1b086951` ·
`ps51`, `bacu1`, `bacu4`, `bacu5`) 0,8862 · `Q` (`d3864b7b` · `bacq1`, `bacq4`, `bacq4b`) 1,0441 —
**13 dossiers, 3 chantiers, 3,5982 $**.

Face au ≈ 12,32 $ de la TODO : 4,5734 (sondes) + 7,74 (evals) = **12,3134 $** — le « 12,32 »
arrondissait `SAG` à 0,46. Dossiers : 4,3001 (notés) + 3,5982 (sans note) = **7,8983 $**, le total du
script. Critère d'arrêt (plus d'un noté sur quatre sans dossier) : **0 / 8** sur les sondes ; 10 / 18
si l'on compte les evals, que le cadrage a mises dehors.

## 2026-09-25 — ESS4

`py scripts/vlp.py recompter .` (sans `--ecrire`) : `RECOMPTE 49 clos · 24 recomptés · 25 gardés ·
inscrit 716 632 063 · recompté 718 373 550 · écart +1 741 487`. Trois écarts non nuls : `FIL`
+583 782 et `SAG` +506 675 — **exactement** leur part `essais` dans `cout` (`3 essais ≈583,8k
(583 782)`, `3 essais ≈506,7k (506 675)`) — et `REC` +651 030, **0 essai** (cause non vérifiée : la
session a pu grandir après l'inscription, menu de clôture `1f92f30`). 583 782 + 506 675 + 651 030
= 1 741 487. Les dollars viennent de `py scripts/vlp.py cout "context AI/<fichier>.md"`, au centime.

| Chantier | Noté à la main | Dossier (ESS1) | Trouvé par `cout` | Écart (trouvé − noté) | Cause |
|---|---:|---:|---:|---:|---|
| `X` | 0,90 | 0,6171 | 0 | −0,90 | chantier gardé (`DÉCOUPE aucune`) ; dont −0,2829 dossier absent |
| `G` | 0,115 | 0,1153 | 0 | −0,115 | chantier gardé (`DÉCOUPE aucune`) |
| `A` | 0,22 | 0,2211 | 0 | −0,22 | chantier gardé (`DÉCOUPE aucune`) |
| `P` | 0,75 | 0,7503 | 0 | −0,75 | chantier gardé (`DÉCOUPE aucune`) |
| `L` | 1,26 | 1,2636 | 0 | −1,26 | chantier gardé (`DÉCOUPE aucune`) |
| `N` | 0,56 | 0,5643 | 0 | −0,56 | chantier gardé (`DÉCOUPE aucune`) |
| `SAG` | 0,45590805 | 0,4559 | 0,46 (SAG2 0,28 · SAG4 0,18) | +0,0041 | arrondi (`cout` au centime) |
| `FIL` | 0,31252785 | 0,3125 | 0,31 (FIL3) | −0,0025 | arrondi (`cout` au centime) |
| **8 notés** | **4,5734** | **4,3001** | **0,77** | **−3,8034** | |
| `Y` · `U` · `Q` (sans note) | 0 | 3,5982 | 0 | 0 | chantier gardé (`DÉCOUPE aucune`) |
| 10 evals (dehors) | 7,74 | 0 | 0 | −7,74 | hors d'`ESS` par le cadrage |

Face au ≈ 12,32 $ de la TODO n° 47 : noté **12,3134** (4,5734 sondes + 7,74 evals), trouvé par
`cout` **0,77**, écart **−11,5434** — dont 7,74 d'evals dehors et 3,8034 de sondes.

Causes, en comptes bruts : **chantier gardé 9** (`X` `G` `A` `P` `L` `N` `Y` `U` `Q`, 7,1299 $ de
dossiers : 7,8983 − 0,4559 − 0,3125) · **dossier absent 1** (`X`, 0,2829, déjà dans ESS1) ·
**arrondi 2** (`SAG`, `FIL`) · **essai hors plage 0** (la somme des fiches égale le `TOTAL`, `hors
fiches` sans essai) · **sous-agent de l'essai 0**. La cause « chantier gardé » n'était pas prévue par
la fiche : sur `DÉCOUPE aucune`, `cmd_cout` mesure les sessions entières par `mesure().main(ids)`
(`scripts/vlp.py:545`), sans `essais_de`, et `recompter` garde ces chantiers.

Écart au-delà de 0,05 $ : **6 chantiers sur 8 notés** (`X` `G` `A` `P` `L` `N`) ; les 10 evals aussi,
mais dehors.

## 2026-09-25 — ESD3

`py scripts/vlp.py recompter . --essais --ecrire` : 11 cellules écrites la première fois (B − A = 12 991 756 = somme affichée sans `--ecrire`). Deuxième passage : `ÉCRIT 0 cellules` (marque d'essais idempotente). Feuille régénérée par `py scripts/vlp.py feuille` : inchangée (zones et chiffres en place).

| Chantier | Inscrit (avant) | Essais ajoutés |
|---|---:|---:|
| `SAG` | 21 912 236 | 506 675 |
| `FIL` | 20 319 194 | 583 782 |
| `Q` | 23 753 914 | 1 594 040 |
| `U` | 15 933 829 | 1 899 554 |
| `Y` | 21 917 062 | 3 807 198 |
| `X` | 10 921 635 | 1 145 283 |
| `G` | 7 997 540 | 176 238 |
| `A` | 5 765 489 | 390 811 |
| `P` | 6 786 706 | 1 257 544 |
| `L` | 7 324 563 | 677 922 |
| `N` | 6 491 074 | 952 709 |
| **Total des 11** | **149 123 242** | **+12 991 756** |

Feuille entière (50 clos) : 728 886 126 → 741 877 882.

## 2026-09-25 — APC1

`py scripts/vlp.py cout "context AI/62-essais-sans-decoupe.md" --a-clore`. Appel `clore` trouvé
à 19:13:18 (heure locale), dans la dernière plage hors fiches : `ESD3` 19:12:50 → `Chantier ESD
clos` 19:14:08. L'hypothèse du socle APC tient pour `ESD` : l'écart est **entièrement** fait des
tours joués entre l'appel `clore` et le commit de clôture.

| Ce qu'on compare | Tokens | Tours |
|---|---:|---:|
| Inscrit (feuille de route, chiffre de `clore`) | 16 735 386 | — |
| `à clore` (dernière plage hors fiches arrêtée à l'appel `clore`) | 16 735 386 | 198 |
| `à clore` − inscrit | 0 | — |
| Recompté (`TOTAL`, plage jusqu'au commit de clôture) | 18 506 516 | 206 |
| `après clore` (recompté − `à clore`, session seule, 0 sous-agent) | 1 771 130 | 8 |
| Reste non expliqué (recompté − inscrit − `après clore`) | 0 | — |

## 2026-09-25 — APC2

`py scripts/vlp.py recompter . --a-clore` (code 0), sortie brute :

```
ESD inscrit 16 735 386 · recompté 18 506 516 · écart +1 771 130 · découpe · à clore 16 735 386 · après clore 1 771 130
ESS inscrit 12 254 063 · recompté 13 017 121 · écart +763 058 · découpe · à clore 12 254 063 · après clore 763 058
REC inscrit 15 906 689 · recompté 16 557 719 · écart +651 030 · découpe · à clore 15 906 689 · après clore 651 030
JUG inscrit 11 306 457 · recompté 11 306 457 · écart +0 · découpe · à clore 10 273 570 · après clore 1 032 887
FOR inscrit 20 371 577 · recompté 20 371 577 · écart +0 · découpe · à clore 17 689 317 · après clore 2 682 260
RLG inscrit 9 179 817 · recompté 9 179 817 · écart +0 · découpe · partagée avec GAR, GLO, PYT, UNI · à clore 8 745 720 · après clore 434 097
PYT inscrit 12 279 871 · recompté 12 279 871 · écart +0 · découpe · partagée avec GAR, GLO, RLG, UNI · à clore 11 561 195 · après clore 718 676
UNI inscrit 16 613 231 · recompté 16 613 231 · écart +0 · découpe · partagée avec GAR, GLO, PYT, RLG · à clore 15 942 182 · après clore 671 049
GAR inscrit 8 426 745 · recompté 8 426 745 · écart +0 · découpe · partagée avec GLO, PYT, RLG, UNI · à clore 7 864 973 · après clore 561 772
GLO inscrit 15 674 582 · recompté 15 674 582 · écart +0 · découpe · partagée avec GAR, PYT, RLG, UNI · à clore 15 182 315 · après clore 492 267
CON inscrit 15 711 661 · recompté 15 711 661 · écart +0 · découpe · à clore 14 631 523 · après clore 1 080 138
REV inscrit 76 440 498 · recompté 76 440 498 · écart +0 · découpe · à clore 75 866 013 · après clore 574 485
ZER inscrit 12 079 243 · recompté 12 079 243 · écart +0 · découpe · partagée avec CAD, CAS, FIN, MTK, PLA, TAR, VAL · à clore 11 633 997 · après clore 445 246
CAD inscrit 15 724 492 · recompté 15 724 492 · écart +0 · découpe · partagée avec CAS, FIN, MTK, PLA, TAR, VAL, ZER · à clore 15 154 579 · après clore 569 913
MTK inscrit 13 588 111 · recompté 13 588 111 · écart +0 · découpe · partagée avec CAD, CAS, FIN, PLA, TAR, VAL, ZER · à clore 12 738 440 · après clore 849 671
PLA inscrit 13 033 400 · recompté 13 033 400 · écart +0 · découpe · partagée avec CAD, CAS, FIN, MTK, TAR, VAL, ZER · à clore 12 587 599 · après clore 445 801
TAR inscrit 19 399 198 · recompté 19 399 198 · écart +0 · découpe · partagée avec CAD, CAS, FIN, MTK, PLA, VAL, ZER · à clore 18 799 875 · après clore 599 323
FIN inscrit 22 962 798 · recompté 22 962 798 · écart +0 · découpe · partagée avec CAD, CAS, MTK, PLA, TAR, VAL, ZER · à clore 22 487 850 · après clore 474 948
VAL inscrit 6 924 438 · recompté 6 924 438 · écart +0 · découpe · partagée avec CAD, CAS, FIN, MTK, PLA, TAR, ZER · à clore 6 467 267 · après clore 457 171
CAS inscrit 11 729 608 · recompté 11 729 608 · écart +0 · découpe · partagée avec CAD, FIN, MTK, PLA, TAR, VAL, ZER · à clore 10 591 273 · après clore 1 138 335
FIL inscrit 20 902 976 · recompté 20 902 976 · écart +0 · découpe · partagée avec SAG · à clore 20 121 243 · après clore 781 733
SAG inscrit 22 418 911 · recompté 22 418 911 · écart +0 · découpe · partagée avec FIL · à clore 21 552 508 · après clore 866 403
CPT inscrit 21 606 411 · recompté 21 606 411 · écart +0 · découpe · à clore 20 517 798 · après clore 1 088 613
REP inscrit 33 108 434 · recompté 33 108 434 · écart +0 · découpe · sans appel clore
NIV inscrit 24 964 199 · recompté 24 964 199 · écart +0 · découpe · sans appel clore
Z inscrit 11 093 368 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « Z1 : » ni d'une autre fiche)
Q inscrit 25 347 954 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « Q1 : » ni d'une autre fiche)
U inscrit 17 833 383 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « U1 : » ni d'une autre fiche)
Y inscrit 25 724 260 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « Y1 : » ni d'une autre fiche)
J inscrit 7 579 062 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « J1 : » ni d'une autre fiche)
O inscrit 9 842 371 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « O1 : » ni d'une autre fiche)
F inscrit 8 781 743 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « F1 : » ni d'une autre fiche)
X inscrit 12 066 918 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « X1 : » ni d'une autre fiche)
W inscrit 7 305 939 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « W1 : » ni d'une autre fiche)
G inscrit 8 173 778 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « G1 : » ni d'une autre fiche)
A inscrit 6 156 300 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « A1 : » ni d'une autre fiche)
P inscrit 8 044 250 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « P1 : » ni d'une autre fiche)
L inscrit 8 002 485 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « L1 : » ni d'une autre fiche)
N inscrit 7 443 783 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « N1 : » ni d'une autre fiche)
K inscrit 6 203 651 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « K1 : » ni d'une autre fiche)
I inscrit 6 542 829 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « I1 : » ni d'une autre fiche)
D inscrit 7 164 227 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « D1 : » ni d'une autre fiche)
V inscrit 19 316 675 · recompté gardé · écart +0 · gardé — sans session
H inscrit 16 898 227 · recompté 16 898 227 · écart +0 · découpe · sans appel clore
S inscrit 17 193 402 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « S1 : » ni d'une autre fiche)
R inscrit 11 840 151 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « R1 : » ni d'une autre fiche)
B inscrit 5 342 511 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « B1 : » ni d'une autre fiche)
T inscrit 16 194 635 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « T1 : » ni d'une autre fiche)
C inscrit 7 816 316 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « C1 : » ni d'une autre fiche)
M inscrit 11 362 254 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (chantier clos sans commit « M1 : » ni d'une autre fiche)
E inscrit 0 · recompté gardé · écart +0 · gardé — fichier introuvable
RECOMPTE 51 clos · 26 recomptés · 25 gardés · inscrit 758 613 268 · recompté 761 798 486 · écart +3 185 218
```

Les 19 clos des causes 4a et 4b de `REC2` portent déjà le recompté (écart +0 ci-dessus) : l'écart
est celui de `REC2` (recompté − inscrit d'alors). Reste = écart − `après clore`. Calcul croisé par
script sur la sortie et la table `REC2` (colonne « Page : total »), pas à la main.

| Clos | Cause `REC2` | Écart | `après clore` | Reste | L'après-clore l'explique |
|---|---|---:|---:|---:|---|
| JUG | 4b | +1 032 887 | 1 032 887 | 0 | entièrement |
| FOR | 4b | +2 682 260 | 2 682 260 | 0 | entièrement |
| RLG | 4b | +434 097 | 434 097 | 0 | entièrement |
| PYT | 4b | +718 676 | 718 676 | 0 | entièrement |
| UNI | 4b | +671 049 | 671 049 | 0 | entièrement |
| GAR | 4b | +837 905 | 561 772 | 276 133 | en partie — page = à clore |
| GLO | 4b | +1 889 876 | 492 267 | 1 397 609 | en partie — page = à clore |
| CON | 4b | +1 801 023 | 1 080 138 | 720 885 | en partie — page = à clore |
| REV | 4b | +1 651 444 | 574 485 | 1 076 959 | en partie — page = à clore |
| ZER | 4b | +870 062 | 445 246 | 424 816 | en partie — page = à clore |
| CAD | 4b | +1 120 896 | 569 913 | 550 983 | en partie — page = à clore |
| MTK | 4b | +1 395 427 | 849 671 | 545 756 | en partie — page = à clore |
| PLA | 4b | +1 094 592 | 445 801 | 648 791 | en partie — page = à clore |
| TAR | 4b | +1 756 465 | 599 323 | 1 157 142 | en partie — page = à clore |
| FIN | 4b | +1 091 080 | 474 948 | 616 132 | en partie — page = à clore |
| VAL | 4b | +1 276 532 | 457 171 | 819 361 | en partie — page = recompté |
| CAS | 4b | +1 687 993 | 1 138 335 | 549 658 | en partie — page = recompté |
| SAG | 4a | +1 783 610 | 866 403 | 917 207 | en partie — reste = hors fiches clôture avant `clore` |
| CPT | 4a | +2 339 885 | 1 088 613 | 1 251 272 | en partie — reste = hors fiches clôture avant `clore` |
| **19** | | **+26 135 759** | **15 183 055** | **10 952 704** | |

**Comptes.** Entièrement : **5** (`JUG`, `FOR`, `RLG`, `PYT`, `UNI`) · en partie : **14** · pas du
tout : **0** — 5 + 14 + 0 = 19. Sans appel `clore` retrouvé : **0** des 19 ; 3 sur tous les
recomptés (`REP`, `NIV`, `H`). Les 3 clos non recomptés
(`ESD`, `ESS`, `REC`) : `à clore` = inscrit au token près, `après clore` = écart, somme +3 185 218 =
écart de la ligne `RECOMPTE`.

**Ce que dit le reste, sans cause supposée.** 10 clos (`GAR` à `FIN`) : `à clore` égale **au token
près** le total de la page du chantier ; c'est l'inscrit de la feuille qui est plus bas. `VAL`,
`CAS` : la page égale le recompté, l'inscrit est sous `à clore`. `SAG`, `CPT` (4a, l'inscrit = les
fiches seules) : reste + `après clore` = hors fiches côté clôture de `REC2` (917 207 + 866 403 =
1 783 610 ; 1 251 272 + 1 088 613 = 2 339 885). `SAG` : son `à clore` compte 506 675 d'essais
(`ESD`) absents de `REC2` ; le reste n'en dépend pas. L'hypothèse du socle `APC` tient **en
entier pour les 3 clos les plus récents et 5 des 19** ; pour les 14 autres, l'inscrit est sous
`à clore` : ce qui l'a fait plus bas n'est pas établi ici.

## 2026-09-25 — LEC1

**La séance d'avant.** `2f9a46f3-70ad-4145-a7c8-ada5aefa0034` (2026-09-24, `/vlp:chantier` sans
argument) : la dernière qui lit `08-etat.md` par un `Read` sans `offset`. Les deux plus récentes
(`2d0c4c56`, `2ff884ef`) recevaient le chantier en argument et lisaient par `grep` ou plage.
⚠️ Ce `Read` est **tronqué par l'outil** : lignes 1–453 rendues sur 1 222 (commit `637bbf0`),
47 938 caractères. L'« avant » mesuré est donc une lecture de 453 lignes, pas du fichier entier ;
le fichier en fait 2 137 aujourd'hui. Rien n'est estimé à la place.

Plage `2026-09-24T06:41:13.306Z` → `2026-09-24T06:45:44.475Z` (1er `AskUserQuestion`) :
`tours` 3, appels 4 (`Read`=2 `Bash`=1 `AskUserQuestion`=1), `ctx_1er` 72 733, `ctx_dernier`
110 515, `output` 28 673, `equiv` 285 200, `usd` 1.14.

**L'après fait à la main.** `44909b3f-749f-48b6-b44b-9fdfb6a43588`, plage
`2026-09-25T18:11:24.470Z` → `2026-09-25T18:12:18.718Z` : `tours` 6, appels 6 (`Bash`=2 `Read`=1
`Grep`=1 `Skill`=1 `AskUserQuestion`=1), `ctx_1er` 67 539, `ctx_dernier` 85 624, `output` 3 685,
`equiv` 122 263, `usd` 0.49. Commande : `py scripts/mesure-tokens.py --plage <début> <fin> <id>`.
Deux séances sur deux sujets : l'écart ne s'attribue pas à la seule lecture de la TODO.

**Les cinq projets** (décisions 2 et 5 du socle `LEC`, calculées sur les titres `## `) :

| Projet | Fichier TODO (lignes) | Titre TODO | Section | Méthode : titres trouvés |
|---|---|---|---|---|
| kit | `context AI/08-etat.md` (2 137) | `:356` | 356–392 (37) | 2 — bloc 288–361 (74) |
| MapDecorator | `context AI/08-etat.md` (215) | `:120` | 120–177 (58) | 1 — « Les deux formes… » absent |
| ProjetONZSM | `context AI/08-etat.md` (64) | `:29` | 29–44 (16) | 2 — bloc 33–77 (45) |
| TrackGen | `context AI/08-etat.md` (679) | `:30`, `:124` | 30–49 (20) | 2 — bloc 33–77 (45) |
| Cairn-VlpLib | `20a-chantiers.md` (854) ; `10-etat.md` (4 500) | aucun ; `:158` | — ; 158–434 (277) | 1 |

- TrackGen : la TODO vivante est `:30` — elle dit que `/chantier` en tire ses propositions, table
  de 11 chantiers lignes 36–48. `:124` est une liste arbitrée le 2026-08-28 (sous-titre `:126`),
  jusqu'à la fin du fichier (124–679). La décision 4 (le premier titre) prend la bonne.
- Kit : la section fait 37 lignes, pas 36 comme au socle — la ligne 392, vide, précède le `## `
  de 393 et la décision 2 l'inclut.
- MapDecorator et Cairn sortiront `METHODE=absente` ; Cairn sortira aussi `TODO=absente` pour
  `20a-chantiers.md`.

## 2026-09-25 — LEC5

Ce compte compare trois séances `/vlp:chantier` sans argument sur le kit, du début au premier
`AskUserQuestion` : la dernière d'avant `LEC` (lecture de `08-etat.md` par `Read`), le cadrage
fait à la main, et l'après, où la carte imprime la TODO et le format des fiches.
Commande : `py scripts/mesure-tokens.py --plage <début> <fin> <id>`.

| Séance | id | tours | appels | ctx_dernier | equiv | usd |
|---|---|---|---|---|---|---|
| avant | `2f9a46f3-70ad-4145-a7c8-ada5aefa0034` | 3 | 4 | 110 515 | 285 200 | 1.14 |
| cadrage à la main | `44909b3f-749f-48b6-b44b-9fdfb6a43588` | 6 | 6 | 85 624 | 122 263 | 0.49 |
| après | `3aeb5082-062a-484c-8232-a4fde9bd995b` | 5 | 5 | 89 437 | 148 740 | 0.59 |

Plage de l'après : `2026-09-25T21:21:15.307Z` → `2026-09-25T21:22:31.586Z` ; appels `Bash`=4
`AskUserQuestion`=1, `ctx_1er` 74 672, `output` 6 641. Aucun `Read` de `08-etat.md` ni de la
méthode : la carte les a donnés.

- ⚠️ **L'après est gonflé par le montage.** Pour que la carte prenne la branche « aucun », le chef
  avait mis `CHANTIER.md` à « aucun » **sans commit**. La séance l'a vu et a lancé `git diff`,
  `grep`, `sed` pour comprendre : 3 appels sur 5 que la commande seule ne fait pas.
- Face à l'avant : `equiv` −48 % (285 200 → 148 740), `usd` 1.14 → 0.59, malgré ces 3 appels.
  L'avant ne lisait que 453 lignes sur 1 222 (`Read` tronqué, journal `LEC1`) ; le fichier en
  fait 2 175 aujourd'hui.
- Face au cadrage à la main : **l'après ne baisse pas** — `equiv` 122 263 → 148 740, `usd` 0.49 →
  0.59. Deux séances différentes, et l'après porte les 3 appels du montage : l'écart ne se lit
  pas comme le prix de la carte.

## 2026-09-26 — ENC (clos)

Livré : `cocher --refuser` dit le rang du refus (`· refus <n>`, ENC1) ; le relecteur
classe `REFUSÉE` en `fiche` ou `copie` et propose une `RÉÉCRITURE` sous la première
(ENC2) ; le chef pose un questionnaire à quatre options — réécrire, rejouer telle
quelle, jouer à la main, s'arrêter — avant de rejouer un refus, sans jamais réécrire
une fiche de lui-même (ENC3). Joué en `main` de bout en bout : l'essai grandeur
nature n'a rencontré aucune permission refusée. Laissé ouvert : rien, les trois
fiches sont faites. Coût du chantier : 17 228 202 (`vlp.py cout`).

## 2026-09-26 — REL (clos)

Livré : `REL1` a compté, sur 42 relecteurs, 56 citations de titres d'autres fiches
(15 relecteurs), 1 de `PROCHAINE`, 54 de libellés de `CHANTIER.md` (11), et 1 lecture
entière du fichier de fiches (`rel1-carte.py`) ; `vlp.py carte --relecteur` tait titres et
`PROCHAINE=`, test et mutant (`REL2`) ; `vlp:relire` l'injecte (`REL3`). Laissé ouvert :
la ligne **fichier de fiches courant** donne encore l'étendue (`REL1..REL3`) ; `FICHIER=`
entier, TODO n° 70 `FFE` ; la section « Chantiers clos » reste dans la carte. Retiré de
la TODO : n° 55 `FUI`. Coût du chantier : 8 399 715 (`vlp.py clore`).

## 2026-09-26 — ABR (clos)

Livré : `<NN>-<nom>.md` — résultat, notes, journal, bilan — tient à côté de la page ;
`vlp.py abri` l'amorce depuis une page existante (ABR1) ; `vlp.py page` l'écrit
d'abord, la page le recopie en entier (ABR2) ; `clore` y écrit le bilan, l'estimé
résolu avant l'écriture, jamais le marqueur (ABR3) ; `ARTEFACTS.md` le dit (ABR4) ;
les 23 pages de Cairn ont leur `.md` (ABR5). Surpris : le `.gitignore` de Cairn
exclut tout `context AI/` — les `.md` y sont entrés par `git add -f`, décidé avec
l'utilisateur, jamais poussés depuis ce kit. Laissé ouvert : rien, les cinq fiches
sont faites. Retiré de la TODO : n° 26 `ABR`. Coût du chantier : 28 101 075
(`vlp.py clore`).

Appris (ABR2, la fiche la plus chère — 47 tours) : un mutant qui garde un
`--note`/`--journal` explicite en argument ne distingue rien, puisque le
chemin correct et le chemin fauté produisent alors la même sortie ; il faut
retirer la donnée du `.md` sans repasser d'override pour forcer le chemin qui
diverge. Autre piège du même chantier : une fixture de test qui loge la page
et le fichier de fiches dans le même dossier sous le même nom fait collision
avec `chemin_abri()` — les séparer (`artefacts/`) dès l'écriture de la
fixture, pas après l'échec.

Dette repérée : le `.gitignore` de Cairn-VlpLib exclut tout `context AI/` —
en désaccord avec la convention « le `.md` est la source, il vit à côté de la
page » posée par ABR. Réglé une fois par `git add -f` (décidé avec
l'utilisateur, 2026-09-26), sans changer le `.gitignore` : si un futur
chantier retouche `context AI/` dans Cairn, le même conflit reviendra.

Essaimé (vérifié le 2026-09-26, `find … context AI/artefacts/*.html|*.md`) :
Cairn-VlpLib a ses 23 `.md` ; MapDecorator (4 pages), ProjetONZSM (1) et
TrackGen (1) — 6 pages en tout — n'ont **aucun** `.md` d'abri. Pas migrées
par ce chantier : voir la tâche proposée en aparté.

- 2026-09-26 (FFE2) : sans `FICHIER=`, `rel1-carte.py` rejoint `APRÈS=` et la ligne **fichier de fiches courant** de la carte ; juste sur les 20 relecteurs réels, faux sur les 19 rejeux REV (carte à `51-relecture.md`, fiche relue ailleurs) : `entier 1 · plage 2` → `0 · 0` en `--sans-fichier`, lectures toutes venues de ces rejeux. Critère accepté ainsi par l'utilisateur.

- 2026-09-26 — **FFE clos** (FFE1..FFE2) : `vlp.py relecture` ne rend plus `FICHIER=` ; `agents/relecture.md` défend d'ouvrir le fichier de fiches ; `rel1-carte.py` le retrouve par `APRÈS=` + la carte (`--sans-fichier`), juste sur 20 relecteurs réels, aveugle sur les 19 rejeux REV. Laissé ouvert : mesurer l'après sur de vrais relecteurs. Retiré de la TODO : n° 70 `FFE`. Coût du chantier : 7 310 346 (`vlp.py clore`).

- 2026-09-26 — **EST clos** (EST1..EST3) : `vlp.py ouvrir --estime-fiches <n>` note `**Estimé.**` (fiches, $ = moyenne des clos mesurés × n) ; `clore` l'écrit à côté du réel (cadré, joué, $) dans la ligne CLOS, `**Fait.**` et le bilan ; `/vlp:chantier` passe l'option. EST : estimé 1 fiche ≈3,91 $, joué 3 fiches ≈8,91 $. Laissé ouvert : le $ réel de `clore` est au taux plat `estimation_usd` (≈8,91 $), pas le pondéré de `cout` (6,04 $). Retiré de la TODO : n° 36 `EST`. Coût du chantier : 10 647 851 (`vlp.py clore`).

- 2026-09-26 (BAC2) : `vlp.py transcription` rejoué sur les deux transcriptions de `FIL3` ; aucun écart avec l'entrée du 2026-09-24. Sorties telles quelles :

  `F1` (`0045d27f-…/subagents/agent-a8139dad1034ad64a.jsonl`) :

  ```
  TOURS=8
  APPELS=7 — PowerShell 2, Read 5
  AVERTISSEMENTS=1
  PREMIER_AVERTISSEMENT tour=7 outil=Read is_error=non hook=PostToolUse:Read
  TEXTE=Attention : 3 tours restants. Rends ton statut maintenant — RETOUR avec ce qui est fait et ce qui reste, si la fiche n'est pas finie.
  HOOK_ERREURS=7 pour 7 appels
  DERNIER mot=RETOUR stop_reason=end_turn
  DERNIERE_LIGNE=⚠️ Imprévu — tourner limité, fiche inachevée. J'ai lu cinq fichiers sur douze, dans l'ordre requis. Sept restent à lire (n06.txt à n12.txt), un message à la fois.
  ```

  `F2` (`707b23a4-…/subagents/agent-a6a58391ed52b8c54.jsonl`) :

  ```
  TOURS=8
  APPELS=7 — Bash 7
  AVERTISSEMENTS=1
  PREMIER_AVERTISSEMENT tour=7 outil=Bash is_error=oui hook=PostToolUseFailure:Bash
  TEXTE=Attention : 3 tours restants. Rends ton statut maintenant — RETOUR avec ce qui est fait et ce qui reste, si la fiche n'est pas finie.
  HOOK_ERREURS=7 pour 7 appels
  DERNIER mot=RETOUR stop_reason=end_turn
  DERNIERE_LIGNE=RETOUR — Appel 6/12 complété (code 3 reçu). Fiche F2 incomplète : 6 appels restants sur 12. La fiche demande douze appels `exit 3` successifs, un par message, chacun retournant le code 3. Continue avec les appels 7 à 12.
  ```

- 2026-09-26 — **BAC clos** (BAC1..BAC2) : `vlp.py bac <dossier>` pose le bac d'essai de FIL3 en un appel ; `vlp.py transcription <jsonl>` compte tours, appels, avertissements du filet (et l'appel que désigne leur `toolUseID`), erreurs de hook et dernier message — rejoué sur F1 et F2 de FIL3, sans écart avec le journal. Laissé ouvert : lancer `claude -p` reste à la main ; l'eval rejouable, n° 46 `EVF`. Retiré de la TODO : n° 45 `BAC`. Coût du chantier : 8 142 489 (`vlp.py clore`).

- 2026-09-26 (EVF1, essai n° 1) : cas `evals/filet-vue/` (scaffold `vlp.py bac .`, chef limité à `Skill`, prompt = consigne `F1` de `FIL3`). `vlp.py bac` a d'abord échoué dans le scaffold : `py` (lanceur Windows) n'a aucun runtime enregistré une fois relancé hors du profil normal (`No runtimes are installed`) — corrigé en préférant `python` (l'exécutable réel) dans `fixture.sh`. Une fois le scaffold posé, le chef a bien appelé `Skill vlp:jouer F1`, mais **le fork `vlp:jouer` échoue avant même de forker `vlp:fiche`** : sa propre commande `!` (carte du projet) est un appel Bash, refusé — `allowed_tools: [Skill]` du cas ne couvre pas Bash, et **le grant `Bash(python3:*)`/`Bash(py:*)` d'un `allowed-tools` de skill ne peut pas élargir ce que l'eval autorise** (doc `plugin-evals`, confirmé en vrai). En le donnant par `--allow-tools` (opérateur), 2ᵉ essai : refusé net, **`exit 1` — « sandbox required but unavailable … Windows sandbox is not active »** : tout grant Bash/PowerShell sous eval exige un backend de sandbox, absent nativement sous Windows (doc : « Native Windows has no backend, run shell-granting suites under WSL2 », déjà connu pour `wsl2`/TODO n° 11, mais ici ça touche **`EVF1` et `EVF2` aussi**, pas seulement `EVF3` — parce que `vlp:jouer` lance sa carte par un `!` Bash inconditionnel, avant même de forker. **Correction (même jour, après les essais WSL2) : ce n'est PAS une réponse à la question ouverte** — l'erreur naît au chargement de la skill (préambule `!`, contexte du chef), avant tout fork : aucun sous-agent n'a tourné, la question reste ouverte. Coût des deux essais : 0,0620136 $ (2 tours) + 0 $ (refusé avant tour). Commandes : `claude plugin eval . --tag filet-vue --runs 1 --ablation none --no-publish --scaffold [--allow-tools "Bash(python3:*)" "Bash(py:*)" "Bash(echo:*)"] --trust-plugin --max-cost-usd 0.5 -j 1 --keep-temp --json evals/results/evf1-filet-vue{,2}.json`. WSL2 Ubuntu présent mais arrêté ; `claude` non trouvé sur son PATH sans le démarrer et le vérifier (pas fait, coût/temps à trancher avec l'utilisateur).

- 2026-09-26 (EVF1, essais WSL2) : Ubuntu, `claude` 2.1.275 (`~/.local/bin`, hors PATH non interactif), `bwrap`/`socat` présents. Avec `--allow-tools "Bash(python3:*)" "Bash(py:*)" "Bash(echo:*)"` : 0,1916695 $, 2 tours, 3 graders à `passed=False` (`Read called 0x`, `pattern not found` ×2), carte de `vlp:jouer` refusée. Avec `--allow-tools Bash` entier : 0,1307515 $, 2 tours, même refus mot pour mot. Cause probable, non prouvée : le préambule `!` de la skill écrit `2>"${CLAUDE_PLUGIN_ROOT}/relais-python.err"`, hors du workspace de l'eval — une redirection hors workspace refusée même Bash accordé. La corriger toucherait les 7 copies de l'injection de carte : hors fiche. Total EVF1 : 0,3844346 $ (0,0620136 + 0,1916695 + 0,1307515). Commandes rejouables : `wsl -d Ubuntu -- bash -lc 'cd /mnt/c/.../Claude-vlpWorkflow && ~/.local/bin/claude plugin eval . --tag filet-vue --runs 1 --ablation none --no-publish --scaffold --allow-tools Bash --trust-plugin --max-cost-usd 0.5 -j 1 --keep-temp'`.

- 2026-09-26 (EVF4) : cause du blocage d'`EVF1` **prouvée** sur deux copies jetables du kit sous WSL2 (cas `filet-vue`, `--allow-tools Bash`) : variante A, injection **sans redirection** — 0,14054115 $, 2 tours, `Read called 12x`, `matched fichier 05`, témoin « fichier 13 » `pattern not found` (échoue, voulu) ; variante B, `2>"${CLAUDE_PLUGIN_DATA}/relais-python.err"` — 0,1206815 $, 2 tours, `Read called 0x`, carte refusée comme avec `${CLAUDE_PLUGIN_ROOT}`. Décidé seul la nuit (l'utilisateur dormait, à valider) : variante A dans les 7 `SKILL.md`, ce qui défait la redirection de `NIV1`. Bruit mesuré sans redirection : 0 ligne sur 59 sous PowerShell (Windows), 2 lignes `py: command not found` sur 60 sous Ubuntu. Test `EVF4 : les 7 injections de carte n'écrivent aucun fichier` ; mutant (redirection remise dans `relire`) → `ÉCART`. `pyright` : 0 errors.

- 2026-09-26 (EVF1) : **OUI, un eval du plugin voit le sous-agent**, prouvé sur le vrai kit après `EVF4`. `wsl -d Ubuntu`, `~/.local/bin/claude` 2.1.275 : `claude plugin eval . --tag filet-vue --runs 1 --ablation none --no-publish --scaffold --allow-tools Bash --trust-plugin --max-cost-usd 0.5 -j 1 --keep-temp --json evals/results/evf1-final.json`. `costUsd` 0,15195725, `turns` 2 (le chef). Graders : `read-appears-in-trace` passé — « Read called 12x (expected 1..∞) » ; `subagent-content-in-trace` passé — « matched fichier 05 » ; témoin `negative-witness-fichier-13` échoué — « pattern not found in trace » (voulu). `allowed_tools` du cas bride tout le run, sous-agent compris (Read ajouté pour lui ; Bash par `--allow-tools`). La transcription du sous-agent est gardée sous `<kept>/config/projects/*/*/subagents/agent-*.jsonl` (`chmod` d'abord) ; `vlp.py transcription` : `TOURS=5`, `APPELS=15 — Bash 3, Read 12`, `AVERTISSEMENTS=0`, `HOOK_ERREURS=3 pour 15 appels`, `DERNIER mot=FAITE stop_reason=end_turn`. ⚠️ Haiku groupe ses `Read` (12 en 5 tours) malgré « un appel par message » : à plafond 10, le filet risque de ne pas tirer — à voir en `EVF2`.

- 2026-09-26 (EVF2) : `vlp.py kit-essai <dossier> --max-turns <n> [--kit <source>]` copie le kit sans `.git`, `.claude`, `context AI`, `evals/results` et réécrit `maxTurns` ; test dans un kit factice, mutant (pas de réécriture) → `ÉCART`. Cas `evals/filet/` (ex-`filet-vue`), lancé sous WSL2 sur `kit-essai` à 6 et à 80 (plafond 6 et non 10, décidé seul la nuit : Haiku groupe ses `Read`, F1 tient en 4–5 tours, le filet ne tire qu'à ≤ 3 tours restants). Plafond 6 : 0,1361381 $, `Read called 12x`, **transcription `AVERTISSEMENTS=1`, `PREMIER_AVERTISSEMENT tour=3 outil=Bash … hook=PostToolUse:Bash`, « Attention : 3 tours restants. … »**, fin `FAITE`. Plafond 80 : 0,14217435 $, `Read called 12x`, `AVERTISSEMENTS=0`, fin `FAITE`. **Le grader `filet-warns` (regex sur la trace) est muet aux deux plafonds : la trace de l'eval porte les appels d'outils du sous-agent, pas le contexte injecté par ses hooks.** Le filet se prouve donc par la transcription gardée (`--keep-temp`, `<kept>/config/projects/*/*/subagents/agent-*.jsonl`) ; critère d'EVF2 réécrit en ce sens, la nuit, à valider. Grader `retour-rendu` retiré : le sous-agent finit avant le plafond.

- 2026-09-26 (EVF3) : **le filet se rejoue en un appel** — `bash evals/filet/rejouer.sh [plafond]` sous WSL2 (`claude` dans le PATH) : copie `kit-essai`, `claude plugin eval . --tag filet --runs 1 --ablation none --no-publish --scaffold --allow-tools Bash --trust-plugin --max-cost-usd 0.5 -j 1 --keep-temp --json evals/results/filet-<plafond>.json`, puis `vlp.py transcription` sur chaque sous-agent gardé. F2 dans `evals/filet-bash/` (un `case.yaml` par dossier ; décidé seul la nuit), plafond 6 et non 10 comme EVF2. **Plafond 6** : total 0,2770472 $ ; `filet` 0,1315755 $, turns 2, `subagent-reads` passed « Read called 12x (expected 1..∞) », transcription `TOURS=4`, `AVERTISSEMENTS=1`, `PREMIER_AVERTISSEMENT tour=3 outil=Bash is_error=non hook=PostToolUse:Bash`, `DERNIER mot=FAITE` ; `filet-bash` 0,14547169999999998 $, turns 2, `subagent-bash` passed « Bash called 5x (expected 1..∞) », transcription `TOURS=6`, `APPELS=5 — Bash 5`, `AVERTISSEMENTS=3`, `PREMIER_AVERTISSEMENT tour=3 outil=Bash is_error=oui hook=PostToolUseFailure:Bash`, `DERNIER mot=RETOUR` (« 4 appels sur 12 lancés … La limite de tours a été atteinte »). **Plafond 80 (témoin)** : total 0,28954 $ ; `filet` 0,1472009 $, « Read called 12x », `AVERTISSEMENTS=0`, `FAITE` ; `filet-bash` 0,1423391 $, « Bash called 14x », `AVERTISSEMENTS=0`, `FAITE`. Imprévu : à 80, Haiku fait les douze `exit 3` en 4 tours (groupés) ; à 6, il n'en groupe que 1 à 2 par tour et rend `RETOUR` — le filet a servi.

- 2026-09-26 — Chantier EVF clos : `bash evals/filet/rejouer.sh [plafond]` rejoue F1 et F2 de FIL3 en eval du plugin sous WSL2, en un appel (0,2770472 $ à plafond 6, 0,28954 $ à 80). Laissé ouvert : la trace de l'eval ne porte pas le contexte des hooks, le filet se prouve hors grader, par la transcription gardée ; deux critères réécrits la nuit (EVF2, EVF3) et la redirection retirée (EVF4), à valider. Chantier 35 593 422. Vaut au-delà : sous eval, une injection `!` qui écrit hors du workspace est refusée même `--allow-tools Bash`.

- 2026-09-26 (RAT1) : **OUI, un `Read` raté réveille le filet** — il déclenche `PostToolUseFailure:Read`, et le filet y avertit. Cas `evals/filet-rate/` (tag `filet-rate`, à part de `filet`) : bac de `FIL3` plus une fiche `F3`, douze `Read` sur `m01.txt`…`m12.txt` absents ; sous WSL2, `kit-essai` puis `claude plugin eval . --tag filet-rate --runs 1 --ablation none --no-publish --scaffold --allow-tools Bash --trust-plugin --max-cost-usd 0.5 -j 1 --keep-temp`. **Plafond 5** : 0,15179964999999998 $, turns 2, « Read called 15x (expected 1..∞) » ; transcription `TOURS=4`, `APPELS=17 — Bash 2, Read 15`, `AVERTISSEMENTS=13`, `PREMIER_AVERTISSEMENT tour=2 outil=Read is_error=oui hook=PostToolUseFailure:Read`, fin `FAITE`. **Plafond 6** : 0,14890994999999999 $, « Read called 12x » ; les douze `Read` tombent au tour 2 (4 tours restants, hors zone) : hook `PostToolUseFailure:Read` vu (ligne 21, `hook_non_blocking_error` du jumeau `py`, absent sous WSL2), `AVERTISSEMENTS=1` au tour 3 sur un Bash. **Plafond 80 (témoin)** : 0,1502577 $, « Read called 12x », `AVERTISSEMENTS=0`. Plafond 5 décidé seul la nuit, après le 6 qui plaçait les `Read` trop tôt. **Imprévu** : 13 avertissements dans un même tour — le filet répète son texte à chaque appel groupé du tour, pas une fois par tour ; coût de contexte à mesurer (candidat TODO, à valider).

- 2026-09-26 — Chantier RAT clos : un `Read` raté déclenche `PostToolUseFailure:Read` et le filet y avertit (plafond 5, `evals/filet-rate/`) ; question ouverte depuis `FIL2` fermée. Laissé ouvert : le filet répète son avertissement à chaque appel d'un même tour (13 d'un coup), à mesurer ; cadré seul la nuit, 1 fiche, à valider. Chantier 1 706 811.

- 2026-09-26 — Chantier SON clos : `VLP_SANS_TAMPON=1` dans l'environnement fait agir un hook rejoué à la main à chaque fois (`premier_lancement`), sans `nonce` ; test et mutant. Variable plutôt qu'option, choisie seule la nuit, à valider. Chantier 1 974 524.

- 2026-09-26 (TOU1) : **mesure avant, clé de `TOU2` confirmée** — `bash evals/filet/rejouer.sh 5 filet-rate` (WSL `-d Ubuntu` : la distribution par défaut `docker-desktop` n'a pas bash) : `TOURS=4`, `APPELS=14 — Bash 2, Read 12`, `AVERTISSEMENTS=13`, `AVERTIS_PAR_TOUR=2:12,3:1` ; `costUsd` 0.15472195. Les 12 `Read` d'une même salve voient le même compte de tours : 12 avertissements pour un seul tour.
- 2026-09-26 (TOU3) : **mesure après, un avertissement par tour** — même commande, lancée par `wsl -d Ubuntu bash -lc` (sans `-l`, `claude: command not found`). Plafond 5 : `TOURS=5`, `APPELS=14 — Bash 2, Read 12`, `AVERTISSEMENTS=3`, `AVERTIS_PAR_TOUR=2:1,3:1,4:1` ; `costUsd` 0.14369535 (TOU1 : `TOURS=4`, `AVERTISSEMENTS=13`, `AVERTIS_PAR_TOUR=2:12,3:1`, 0.15472195). Témoin plafond 80 : `TOURS=5`, `APPELS=16 — Bash 4, Read 12`, `AVERTISSEMENTS=0`, `AVERTIS_PAR_TOUR=aucun` ; `costUsd` 0.1447187. Les deux rendent `FAITE`, `HOOK_ERREURS=4`.
- 2026-09-26 : **chantier TOU clos** — livré : le filet n'avertit qu'une fois par tour (filet-rate plafond 5 : 13 → 3 avertissements, témoin 80 : 0). Rien d'ouvert. Estimé 0,5 fiche ≈2,01 $, joué 3 fiches ≈5,86 $. Chantier 6 996 159.
- 2026-09-26 (dette TOU) : **`HOOK_ERREURS` sous WSL = la moitié `py` de la paire de hooks, absente sous Linux** — témoin 80 rejoué (≈ 0,14 $) et lu dans la même session WSL (`/tmp` y est un `tmpfs`, vidé à l'arrêt : les transcriptions gardées ne survivent pas) : 4 `hook_non_blocking_error`, une par événement (`PreToolUse:Bash`, `PostToolUse:Bash`, `PostToolUseFailure:Read`, `SubagentStop`), toutes `Executable not found in $PATH: "py"`. Bruit voulu de la paire `python3` + `py` (chantier `Y`), pas un défaut : la moitié `python3` agit. Rien à corriger.
- 2026-09-26 (VOI4) : **ce que la régénération des trois voisins perd, mesuré par `vlp.py comparer`** (page du disque vs régénérée dans le scratchpad, `vlp.py feuille` sans écriture) :
  - MapDecorator : `COMPARER 1 perdus · 1 ajoutés`. Cause réelle : `todo_du_fichier` (`scripts/vlp.py:2395`) ne lit que la table `| # | Chantier`, et `MapDecorator/context AI/08-etat.md:120` porte sa TODO en liste numérotée `N. [ ]`/`[x]` (pas une table) — lue vide, la page régénérée affiche « aucun chantier possible » alors que 8 items restent ouverts (`#3,4,5,6,7,8,9,10,12`). Second diff, sans rapport : « Lettres de fiche prises » passe de `P` (disque) à `T, U, R, M, P` (régénérée) — pas une perte, la correction `VOI3` (lettres entre backticks, `CHANTIER.md:40`) répare enfin cette ligne.
  - TrackGen : `COMPARER 1 perdus · 1 ajoutés`. La table `| # | Chantier` (`08-etat.md:36`, 11 lignes) est lue **correctement** malgré le titre sans accents (`## La TODO ordonnee`, `:30`) — les 11 items sont identiques des deux côtés. Seule différence : le badge `11 chantiers possibles` (`vlp.py:2486-2487`) que la régénération ajoute et que la page à la main n'avait pas. **Les accents du titre n'expliquent aucune perte** — l'inquiétude posée au cadrage ne se confirme pas.
  - ProjetONZSM : `COMPARER 1 perdus · 1 ajoutés`. Même chose que TrackGen : table correcte (`08-etat.md:34`, 8 lignes) des deux côtés, seul le badge `8 chantiers possibles` diffère. Rien à corriger.
  - Chaque page est un seul bloc HTML de haut en bas (`<div class="page">` non fermé avant la fin) : `comparer` ne peut isoler que la page entière, pas la ligne exacte — la cause s'est trouvée en lisant le texte `PERDU`/`AJOUTÉ` à l'œil, pas par un compte par ligne. Limite de granularité notée, hors fiche.
  - **Tranché par l'utilisateur** : MapDecorator — correction **dans le projet** (sa TODO passe en table standard, `vlp.py` ne change pas). TrackGen — **aucune action** : l'inquiétude des accents ne se confirme pas, la table se lit déjà correctement.
- 2026-09-26 (VOI5) : **la TODO de MapDecorator passe en table** (`MapDecorator/context AI/08-etat.md:120`) : 9 lignes ouvertes, #1, #2, #11 sous `### Fait`. `feuille ../MapDecorator --verifier` : avant `FEUILLE todo 0`, après `FEUILLE todo 9` ; `todo_du_fichier` lit `3 4 5 6 7 8 9 10 12` (9). Témoins inchangés : TrackGen `todo 11`, ProjetONZSM `todo 8`. ⚠️ Le « 8 items » du journal `VOI4` et du critère `VOI5` était un compte faux : la liste qu'ils citent en porte 9. ⚠️ Pas de commit côté MapDecorator : `context AI/` y est ignoré par Git (`.gitignore:4`), le fichier n'est que sur disque.
- 2026-09-26 (VOI6) : **les trois pages régénérées, aucune republiée** — `feuille` : MapDecorator `todo 9` (le 8 du critère reprend le compte faux, voir VOI5), TrackGen `todo 11`, ProjetONZSM `todo 8` ; `COMPARER 1 perdus · 1 ajoutés` et `NIVEAU 0 écarts · 0 avertissements` pour les trois. Page MapDecorator vue et acceptée, mais la **version en ligne** (`1789503912-51a0`) est plus riche que la TODO du fichier : une ligne sans numéro (« Exporter la palette vers cairn »), les coûts et dépendances des lignes 4, 5, 6, 7, 9, 12, le badge « chantier P » — la republier les aurait effacés. Le `comparer` de la fiche confrontait la page du disque, déjà en retard sur la page en ligne : il ne pouvait pas voir cette perte ; comparer à la page en ligne (`Artifact read` avec `path`). **Non republiées sur décision de l'utilisateur** : ces trois projets sont en pause, le travail va à Cairn et vlp. Pages locales réécrites sur disque (hors Git, `context AI/` ignoré).
- 2026-09-26 : **chantier VOI clos** — livré : `vlp.py niveau` compte la page du disque, `comparer` confronte deux pages, les lettres entre backticks se lisent ; MapDecorator, TrackGen, ProjetONZSM à `NIVEAU 0 écarts`. Laissé ouvert : les trois pages en ligne non republiées (projets en pause), et la page en ligne de MapDecorator plus riche que sa TODO (à reporter dans le fichier avant toute republication). Estimé 3 fiches ≈12 $, joué 6 fiches ≈22 $. Chantier 26 741 523.
- 2026-09-26 (dette VOI) : **TODO de MapDecorator remise au niveau de sa page en ligne** — ligne « Exporter la palette vers Cairn » (`—`) ajoutée, coûts et dépendances des 9 lignes reportés, `roulables.csv` sur #4, chantier `P` et doute sur le chiffre de Cairn sur #12. `feuille` : `todo 9` → `todo 10` ; les 9 éléments manquants comptés 1 fois chacun dans la page régénérée. ⚠️ Non tranché : #12 dit « 90,7 % du décor à plus de 32 m », la page en ligne « 7,4 % sous 32 m » (soit 92,6 % au-delà), les deux gardés. Page non republiée (projet en pause), fichier hors Git (`context AI/` ignoré). Essaimage `niveau` : 0 écart partout ; avertissements de poids : kit index 104/80, Cairn `CLAUDE.md` 85/80 et index 89/80.
- 2026-09-26 : **chantier IDX clos** — livré : `vlp.py archiver` range les lignes `**clos**` de l'index dans `00-INDEX-archive.md` (même dossier), appelé par `clore` ; `recompter` et `niveau` lisent l'archive. Kit : index 105 → 43 lignes, clos 63 → 0 (archive 0 → 63), `RECOMPTE` identique avant/après, `archiver` relancé : `ARCHIVÉ 0`. Routage, gabarit, `methode-chantier.md` et `cloture.md` pointent l'archive. Laissé ouvert : `CLAUDE.md` du kit 81/80, index de Cairn (migré à sa prochaine clôture). Chantier : 10782128.
- 2026-09-26 : **chantier ALE clos** — livré : `ARTEFACTS.md`, « Où vivent le CSS et les données » : le CSS en `vlp.css` joint **adopté** (écart par republication 5760 → 3286, −43 %, `read` ne rend que le `<link>`) ; la base `db` **en attente** (écart 630 sans relire la page, mais « Base indisponible » en local et écran de connexion en fenêtre privée : une page `db` est réservée à l'organisation). TODO `PLI`, `FEU`, `BTN` sans `ALE`. Laissé ouvert : l'essai hors mode auto — une écriture `ArtifactData` demande-t-elle un accord ? — sur la variante gardée (`KyNAVstNmYp1Afr7YbJago`, `essai-ale/page-db.html`) ; la page jetable ALE1 est supprimée. Retiré de la TODO : n° 27 `ALE`. Estimé 2 fiches ≈7,98 $, joué 3 fiches ≈12 $. Chantier 14 440 218.
- 2026-09-27 (dette ALE) : **une écriture `ArtifactData` ne demande aucun accord**, même hors mode auto — `journal/j4` écrit sur la variante `KyNAVstNmYp1Afr7YbJago`, aucune fenêtre vue par l'utilisateur, aucune règle `ArtifactData` dans les permissions (grep, 0). Base `db` passée de « en attente » à **adoptée pour plus tard** (`ARTEFACTS.md`) ; `PLI` et `FEU` restent en HTML statique.
- 2026-09-27 : **chantier PLI clos** — livré : la page d'un chantier se replie (fiches finies, journal sauf ses 3 dernières entrées), un clos a son bilan en haut, le CSS des deux gabarits vit dans `vlp.css`, recopié par `page` et `feuille` et joint à chaque publication. Mesuré sur `51-relecture.html` (`78-plier.md`, « Mesures ») : repliée 3,45 → 2,18 écrans (2977 → 1886 px), dépliée 3,63 ; `Artifact read` 7 795 → 5 842 tokens (−25 %) ; `comparer` 0 ligne perdue. Laissé ouvert : `page` ne remonte pas le bilan d'un clos déjà clos (seul `clore` le fait), le hors fiches de `51-relecture` a bougé à la régénération (7,55 → 7,89 $, 29 → 31 tours), les pages des projets équipés migrent à leur prochaine régénération. Estimé 5 fiches ≈20 $, joué 7 fiches. Chantier 46 030 670.
- 2026-09-27 : **chantier VID clos** — livré : `vlp.py vigile` (`defauts_page`, 15 tests, 3 mutants) et son hook `PreToolUse` sur `Artifact` : une page `.html` à commentaire ouvert, sans style ou sans bloc visible est refusée avec sa raison — essai réel : page cassée refusée (3 défauts nommés), page saine publiée. Laissé ouvert : rien. Piste qui vaut au-delà : `/reload-plugins` ne se lance pas depuis Claude (ni shell, ni outil) — une fiche qui l'exige demande le geste de l'utilisateur. Chantier 11 845 098.
- 2026-09-27 : **chantier HAB clos** — livré : `vlp.py page --forme` (la forme seule : `vlp.css`, fiches repliées, bilan en haut ; coûts, total, hors fiches, titres, libellés, comptage et date recopiés de l'ancienne page), `vlp.py repeindre <projet>` (chaque clos passe par `--forme` puis `vigile`, dans une copie), `vlp.py lien`/`liens` (l'URL en ligne de chaque page dans son `.md`, section `## Lien`). Kit : 64 pages repeintes, chiffres identiques 64/64 (154 coûts de fiche, 99 lignes total/hors), `COMPARER 0 perdus` et `PAGE SAINE` 64/64, toutes remises en ligne ; Cairn : 17 repeintes et en ligne. `repeindre --a-blanc` : 0 repeintes sur les deux. Coût en ligne : 0,125 $/page (sous-agent Sonnet, kit), 0,22 $/page (Cairn). Laissé ouvert : le critère visuel de HAB4 vu en local seulement (claude.ai demande une connexion) — à regarder en ligne par l'utilisateur. Pistes qui valent au-delà : les pages html de Cairn ne sont pas suivies par Git (`.gitignore:15`, `context AI/`) : leur seul filet est la version en ligne ; `comparer` prend une plage d'en-tête refaite pour une perte ; chaque publication d'un sous-agent réveille le chef par un avis « watch limit » (~45 tours vides pour 66 pages). Estimé 1 à 2 fiches, joué 6 (≈68 $) : la remise en ligne de 81 pages n'était pas chiffrée à l'estimé. Chantier 81 710 966.
- 2026-09-27 : **chantier PLG clos** — livré : `bornes(ids)` dans `vlp.py`, la plage de fiches va du plus petit au plus grand numéro ; `plage()` et les quatre plages `..` de `clore` et `ouvrir` l'appellent. Tranché de nuit, l'utilisateur dormant : le plus haut numéro (TODO n° 57, 🟡). 4 tests, mutant `ids[0], ids[-1]` tombé ; test-vlp OK ; pyright 0. Estimé 0,5 fiche ≈2,12 $, joué 1 fiche. Chantier 3 009 913.
- 2026-09-27 : **chantier ECH clos** — livré : `ecrit_git(commande)` dans `vlp.py` ; le corps d'un heredoc reçu par `cat` ou `tee`, hors `$(…)` et sans `|` derrière, n'est plus lu par le gardien ni par `contrat`. Mesuré sur 889 transcriptions : sous-agents 19 → 14 appels attrapés (les 5 heredocs `cat`), chef 1 157 → 1 149. Tranché de nuit (🟡 de la TODO n° 63) : les chaînes citées restent lues, une portait un vrai `git reset` par `ssh`. 9 cas testés, 2 mutants tombés. Estimé 0,5 fiche, joué 1.
- 2026-09-27 : **chantier OUV clos** — livré : la règle `tete` de `forme_texte` exige la forme d'une jauge, `EMOJIS_JAUGE` en tête ou `SUITE_JAUGE` (`—`, `…`, fin de ligne) derrière ; une puce `- Imprévu : j'ai dû…` ne fait plus renvoyer. Mesuré sur le corpus : 79 jauges de sous-agents (72 émoji + suite, 5 émoji seul, 2 suite seule), 0 sans émoji suivie de `:` ; toutes gardées. Tranché de nuit (🟡 de la TODO n° 66) : l'émoji OU la suite. 7 cas testés, mutant tombé. Estimé 0,5 fiche, joué 1.
- 2026-09-27 : **chantier ECA clos** — livré : les 24 écarts de `recompter .` expliqués au jeton près, puis écrits. 19 négatifs (JUG … CPT) : leur chiffre courait jusqu'au commit de clôture (règle `REC`), recompté jusqu'au commit = inscrit sur 19 ; `recompter --ecrire` les arrête à l'appel `clore` (règle `APC`) — 19 cellules, total 1 140 424 192 → 1 125 033 889 ; JUG, FOR, RLG, PYT, UNI retombent sur le chiffre de `clore` d'origine. 4 positifs (BAC, EST, FFE, REL) : la ligne de bilan « Coût du chantier : N (`vlp.py clore`) », écrite par `echo` ou heredoc, prise pour un appel — `lance_clore` n'accepte plus qu'un interprète Python en tête de segment, heredocs `cat`/`tee` tus (`sans_heredoc`, sorti de `ecrit_git`) ; corpus : 82 appels gardés, 20 textes écartés. LEC : LEC5 sans commit courait jusqu'au bout d'une session continuée après la clôture — `plages(clos)` l'arrête au commit suivant qui nomme le préfixe, 50 820 624 → 41 160 098 = l'inscrit. Tests et mutants (ancien motif, sans `sans_heredoc`, `clos` ignoré) ; test-vlp OK ; pyright 0. Reste non traité : une fiche sans commit dont le commit suivant est la clôture même (absent des 72 clos). Estimé 1,5 fiche ≈6,34 $, joué 3 fiches ≈10 $ au taux plat. Coût du chantier : 12 094 884 (`vlp.py clore`).
- 2026-09-27 : **chantier TYP clos** — livré : `pyrightconfig.json` (`include` `scripts`, mode `standard`, celui du 0 mesuré) et un bloc pyright dans `.githooks/pre-commit`, avant `claude` (dont l'absence sort par `exit 0`), lancé seulement si le commit indexe un `.py` (66 commits sur les 200 derniers) ; en erreur, commit refusé ; pyright absent, le hook le dit et laisse passer. Limite dite dans le hook : pyright lit l'arbre de travail, pas l'index. Tranché la nuit, l'utilisateur dormant : `context AI/38-audit-scripts/` reste dehors (12 erreurs d'avant, 11 scripts — les nettoyer est un chantier à lui). `tester_hook_pyright` : faux pyright en tête du PATH, claude caché ; mutants (condition `.py` retirée, code de sortie ignoré) : ÉCART ; test-vlp OK, 0 SAUTÉ ; pyright racine 0 errors, 6 fichiers ; le commit `TYP1` lui-même est passé par le hook (7 s). Surpris : le faux pyright sans extension est trouvé par le sh de Git sous Windows. Estimé 1 fiche ≈4,16 $, joué 1 fiche ≈2,51 $. Coût du chantier : 2 995 094 (`vlp.py clore`).
- 2026-09-27 : **chantier CHK clos** — livré : `vlp.py contrat --ouverture F` garde les sous-agents partis — leur heure à eux — depuis le plus ancien commit qui ajoute le fichier de fiches F, sous une ligne `DEPUIS` ; F non commité : `GARDE:`. `/vlp:check` le lance en vérification I (+12 −2 lignes), sautée sans chantier courant. Le 🟡 (commit d'ouverture ou session du cadrage) tranché la nuit, l'utilisateur dormant, par la mesure : 28 sous-agents sur 103 partis dans une session de cadrage — la borne « commit, session parente » en rate (REV 3, RLG 2), la borne « départ du cadrage » range dans ZER 14 sous-agents d'avant son ouverture ; le premier commit qui nomme le préfixe est souvent l'ajout à la TODO ; le commit qui ajoute le fichier est « Chantier X ouvert » pour 69 fichiers sur 80. Tests et mutants (heure parente, filtre retiré) ; test-vlp OK ; pyright 0. Réel : depuis FOR, `CONTRAT 11 sous-agents · 3 écrivent dans Git · 1 sans statut en tête`. Reste : rejouer `/vlp:check` après `/reload-plugins`, geste de l'utilisateur. Estimé 0,5 fiche ≈2,07 $, joué 2 fiches ≈4,13 $. Coût du chantier : 4 935 035 (`vlp.py clore`).
- 2026-09-27 : **rapport de la nuit validé** — par l'utilisateur, au matin. Les neuf décisions de la nuit gardées (D1 à D9), dont le critère visuel de `HAB4`, levé sur son regard. `/vlp:check` rechargé : la vérification I sort (Q1), la réserve de `CHK2` est levée. Push des 34 commits de la nuit (`8eb274e..7a280fa`). `ENR` retiré de la TODO (Q7) : `ESD` l'a vu en vrai, un `REFUSÉE` qui arrête la chaîne et marque la page bloquée. `FEU` tranché (Q8) : la feuille garde tout le détail de la TODO, replié. `ECO` (77) et `ENQ` (78) versés à la TODO, deux oui (Q3, Q4). Le dernier cas d'`ECA` noté, pas mis à la TODO (Q5) : une fiche sans commit dont le commit suivant est la clôture même, 0 cas sur 72 chantiers clos. Chez Cairn, les pages publiées suivies par Git (Q6) : exception `!context AI/artefacts/` dans son `.gitignore`, 37 fichiers, commit `a4b5ae1`, non poussé. Essaimage (Q2) : `vlp.py niveau` sur les quatre projets équipés, 0 écart partout ; un avertissement chez Cairn, `CLAUDE.md` 89 lignes > 80. Il a d'abord planté chez MapDecorator, seul projet avec un chantier courant : l'appel interne à `cmd_page` n'avait pas reçu `forme`, ajouté par `HAB` ; corrigé et testé (`f295814`, mutant tombé). Deux faits mis en mémoire : vérifier ce que Git suit avant de réécrire les pages d'un projet ; publier en lot par sous-agents réveille le chef à chaque page.
- 2026-09-27 (FEU1) : **à 1536 × 864, aucune feuille ne défile de côté** — `.page` borne les tableaux à 696 px, ils s'y plient (kit et Cairn, TODO et clos) ; le défilement de l'audit se voit à 375 × 812 (TODO kit 483 > 335, Cairn 627 > 335). Le critère « la TODO ne défile plus de côté » de `FEU6` se remesure à 375 × 812. Et `page_vs_source.py` ne retrouve pas le rang qui porte le badge « en cours » (kit 6/7, Cairn 15/16) : à régler en `FEU5`. Table : `87-cartes.md`, « Mesures ».
- 2026-09-27 (FEU) : **`FEU7` et `FEU8` ajoutées** sur deux commentaires de l'utilisateur — un lien vers la feuille de route sur la page du chantier ; le détail des chantiers possibles (petits ≤ 1 fiche, moyens 2 à 4, gros ≥ 5, pas estimés, bloqués, total). Règles essayées sur les 52 rangs des cinq projets : seuls le kit et Cairn notent leurs dépendances en codes, les trois autres en numéros de rang. `FEU6` attend `FEU8` (`4c88161`).
- 2026-09-27 (FEU2) : **pyright refuse `test-vlp.py` si un test s'ajoute au niveau du module** — « Code is too complex to analyze », 1 erreur dès un `try` de plus. Un nouveau test va dans une fonction `test_<nom>()` appelée juste après, comme `test_archiver`. Et `grep -c $'\r$'` sous Git Bash compte faux les CRLF : `vlp.py` est en LF, `test-vlp.py` en CRLF, comptés par Python.
- 2026-09-27 (BTN1) : **même une aide ou une constante au niveau du module fait tomber pyright sur `test-vlp.py`** (1 erreur « Code is too complex to analyze », 0 une fois rangées) — nuance de FEU2 : les aides d'un test vont **dans** sa fonction `tester_<nom>()`, seuls la fonction et son appel restent au niveau du module.
- 2026-09-27 (BTN2) : **`clore` n'écrit pas de ligne `FILES`** (`scripts/vlp.py:3953` ; seuls `page`, `feuille` et `joints` l'écrivent) — `cloture.md` prend celle de `clore`, sinon celle de `vlp.py joints` ; `BTN5`, qui la lui ajoute avec `couts.svg`, rend ce repli inutile.
- 2026-09-27 (BTN3) : **une page servie en local telle quelle mesure 980 px de large à 375 × 812** (`innerWidth` 981, `scrollWidth` = `clientWidth` = 980) : les gabarits n'ont pas de `<meta name="viewport">`, et l'émulation mobile retombe sur 980 px ; claude.ai ajoute lui-même la balise autour de la page. Mesurer la largeur sur une copie **enveloppée** (`context AI/38-audit-scripts/replie.py:25-27`, comme FEU et PLI) : là, 375 = 375. Vaut pour `BTN4` et `BTN6`.
- 2026-09-27 (hors fiche, demande de l'utilisateur) : **cartes en trois colonnes**, fiches et chantiers possibles — à gauche identifiant, état, Copier et dépendances (« ← BTN1 » ; au-delà de deux, « ← 6 fiches », liste au survol) ; au milieu le titre, seul à replier le corps ; à droite le coût, ou « visuel » tant qu'une fiche à regarder n'est pas faite (`apercu_fiches`, `fleche`, `depend_todo` dans `vlp.py`). Pour `BTN6` : **`comparer` sortira un PERDU et un AJOUTÉ par carte republiée** (ordre du texte changé, flèche ajoutée) — attendu, pas une perte ; une page d'avant se lit encore (`lis_page`, `rang_en_cours`, testés).
- 2026-09-27 (hors fiche, commentaire de la page BTN, choix de l'utilisateur) : **l'état d'une fiche en une phrase, sous son titre** — « À lancer » (Copier, couleur d'accent), ou « Après BTN4, BTN5, BTN7 » tant qu'une dépendance n'est pas faite (tous les noms, `data-attend`, pas de Copier) ; « En cours · attend … » pour une fiche en cours qui attend ; « · en même temps que BTN4 » (ou « · BTN5 peut partir en même temps » sur celle en cours) pour les fiches à lancer ensemble (`pretes` dans `vlp.py`). **Une dépendance faite ne s'affiche plus** : « À lancer » le dit déjà ; la colonne de gauche ne garde que l'identifiant et Copier (4,6rem, ≈ 10 lettres : « APRÈS BTN4, BTN5, BTN7 » y prenait 3 lignes). Essayés d'abord puis retirés : un trait bleu et sa légende (l'utilisateur y lisait un lien entre BTN4 et BTN5, « btn5 est lié a btn4 ? »), puis « ∥ avec BTN5 » dans la colonne de gauche. En même temps = prises dans l'ordre, sans fichier commun (nom seul : `templates/vlp.css` = `vlp.css`) ; une prête sans ligne **Fichiers** n'en est pas. `--forme` recalcule ces libellés, garde ceux écrits à la main (« abandonnée »). Limite : la ligne **Fichiers** est une prévision écrite au cadrage, et le fichier de fiches et le fichier d'état, que toute fiche touche, n'y comptent pas.
- 2026-09-27 (BTN5) : **au niveau du module de `test-vlp.py`, même un `and` de plus dans un `verifier` fait tomber pyright** (« Code is too complex to analyze », 0 → 1 erreur, mesuré) — les tests BTN5 vivent dans `tester_joints()` ; REP3 compte désormais 2 `ÉCART:` (une feuille d'avant à ligne close chiffrée n'a pas la balise de `couts.svg`, `niveau` dit « la régénère »).
- 2026-09-28 : **chantier BTN clos** — livré : `vlp.js` joint aux pages — Tout déplier / Tout replier et Copier la commande d'une fiche (BTN3), quatre filtres d'état sur la feuille (BTN4) —, la ligne `FILES` dans les commandes (BTN1, BTN2), le graphique `couts.svg` des chantiers clos (BTN5), le décompte en valeur et le texte d'avant la liste replié (BTN7). BTN6 : la republication a buté sur la limite de 200 publications par jour (`publish 429`, remise à zéro minuit UTC) ; le regard s'est fait **en local** — un `http.server` par dossier de pages, la largeur téléphone dans un cadre de 375 px (piège des 980 px, BTN3) — et l'utilisateur l'a validé à la place du regard en ligne ; les pages partent par la tâche planifiée `vlp-btn6-publier` (02:10). Reste : un coup d'œil en ligne ; le presse-papier de Copier non vérifié (`NotAllowedError` dans le navigateur de l'app). BTN4 a coûté le plus (253 tours, 19,14 $) : sa fenêtre, de `a45f34f` à `ddb58c0`, porte aussi quatre commits hors fiche demandés sur la page. Estimé 6 fiches ≈25 $, joué 7 fiches ≈79 $ (taux plat de `clore`) ; `cout` : 602 tours, 46,74 $. Coût du chantier : 94 966 950 (`vlp.py clore`).
- 2026-09-28 (TAU4) : **`prix` posait le `$` en tête de chaque cellule sans jamais rafraîchir le résumé replié ni le pied « Total cumulé »** de la feuille — les deux restaient au dernier `resommer` d'un `clore`/`recompter --ecrire`, donc à l'ancienne louche (`≈1092 $` sur 1304,5M tokens = 0,8371 $/Mtoken, alors que la somme réelle des 70 cellules mesurées valait `661,15 $`). Corrigé dans `cmd_prix` (`scripts/vlp.py`) : il appelle désormais `resommer` sur l'état final des cellules, posées ou déjà là, à chaque passage — test et mutant dans `tester_prix` (`scripts/test-vlp.py`), pyright 0 erreur. `prix .` rejoué a réécrit la feuille une dernière fois ; le total affiché (`661,15 $ sur 70 clos mesurés`) égale maintenant la somme de ses 70 lignes. **Chantier TAU clos** — livré : un seul prix, le pondéré de `cout`, partout (cellule de clôture, estimé, total de la feuille) ; `vlp.py prix <projet>` recale les 21 chantiers déjà clos (70 cellules posées, 7 sans page `$`) ; résumé et pied de la feuille rafraîchis par la même occasion (dette ci-dessus). 22 pages republiées (21 chantiers + la feuille), chacune relue en ligne avant. `grep -l "joué [0-9]* fiches ≈" "context AI"` retrouve 4 faux positifs hors du périmètre de `prix` : `08-etat.md` (journal historique, jamais recalculé), la note de test d'EST2 dans `68-estime-reel.{html,md}` (une citation de sortie de commande, pas un vrai « joué » de bilan), et `essai-ale/page-db.html` (page d'essai hors `ZONE:clos`) — aucun des trois n'est un fichier que `prix` gère. Estimé 1 fiche ≈4,42 $ (taux plat), joué 4 fiches 20,05 $. Coût du chantier : 58 820 414 (`vlp.py clore`).
- 2026-09-28 (ENQ3) : **l'interdit de commit ne suffisait pas là où il était** — `py scripts/vlp.py contrat` (colonne `bloqué` d'`ENQ1`) sur les 103 sous-agents `vlp:fiche` : **5** ont au moins un appel bloqué par le gardien, **1** en a plusieurs — retentes — (`ac386a140a603894e`, 3 blocages), et **5 sur 5** sont venus après `f98ceec` (2026-09-24 02:07:40 +0200 = 00:07:40Z), qui posait déjà l'interdit à `agents/fiche.md:54-56`. Règle fixée au cadrage : au moins une tentative après `f98ceec` → l'interdit ne suffit pas là où il est. Déplacé à l'étape 5 (`agents/fiche.md`), là où le sous-agent finit — une phrase, retiré de `:54-56` où il faisait doublon (`grep -n "commit" agents/fiche.md` : la règle une fois, à l'étape 5 ; une référence, sans la recopier, plus bas). Effet non prouvé ici : à lire aux chantiers suivants par `/vlp:check` section I.
- 2026-09-28 : **chantier ENQ clos** — livré : `contrat` (`vlp.py`) sépare bloqué (refusé par le gardien, `REFUS_GIT`) d'écrit, et interrompu (`INTERROMPU`) de sans-statut — `CONTRAT <n> · <e> écrivent · <b> bloqués · <s> sans statut · <i> interrompus` ; réel depuis `FOR` : `11 sous-agents · 0 écrivent · 3 bloqués · 0 sans statut · 1 interrompus` (ENQ1), les 3 tentatives sont bien de vraies fautes bloquées, 0 vraie écriture. Le texte cité d'un `echo`/`printf` vers un fichier n'est plus lu comme une écriture Git (`sans_echo`), sans blanchir une chaîne qui écrit vraiment (`ssh … git reset`) : le relecteur `a860169308600a92b` repasse de `git 1` à `git 0` (ENQ2). L'interdit de commit du sous-agent vit désormais à l'étape 5 d'`agents/fiche.md`, une seule fois (ENQ3) — mesuré : 5 sous-agents sur 103 avec ≥1 tentative bloquée, tous après `f98ceec`, qui posait déjà l'interdit ailleurs : il ne suffisait pas là où il était. Rien d'abandonné. Estimé 1 fiche ≈2,97 $, joué 3 fiches 7,38 $. Coût du chantier : 19 338 471 (`vlp.py clore`).
- 2026-09-28 (PAR1) : **l'attente de `--actif` court depuis la dernière ligne de conversation, pas depuis la ligne qui précède le message tapé** — le harnais écrit `queue-operation` (`enqueue`, `dequeue`) à la même seconde que le message (+0 s sur la session de cadrage de PAR ; sur 7 sessions, la ligne qui précède un message tapé est 19 fois une `queue-operation`, 6 fois un `attachment` `date`) : prise au mot, l'attente vaudrait toujours 0. Message tapé = `origin.kind` `human` (3 418 lignes, aucune avec `tool_result`) ou, sans `origin`, une commande locale (295). Limite voulue par le socle : répondre à un questionnaire rend un `tool_result`, donc du temps actif mais pas de l'attente (cadrage de PAR : 3 questionnaires, 0,0 + 0,4 + 0,7 min).
- 2026-09-28 (PAR2) : **MapDecorator ne peut pas servir de référence : 0 chantier mesurable** — son `context AI/` est ignoré par Git (`.gitignore:4`), donc aucun commit « Chantier … ouvert » (9 commits en tout), et 0 ligne `**Session**` sur ses 4 fichiers de fiches ; l'utilisateur a choisi un essai kit + LOC. Ailleurs : ProjetONZSM et TrackGen, 0 « ouvert » et 0 session ; Cairn-VlpLib, 2 « ouvert », 7 « clos ». Référence kit (TYP, CHK, FEU, BTN, TAU ; 22 fiches) : 18,6 min/fiche cadrage compris (plage de `cout`), 16,7 sans ; 4,29 $/fiche. Le socle disait à la fois « cadrage compris » et « entre ouvert et clos » : les deux chiffres sont écrits, la série de `PAR3` prend celui qui ressemble à l'essai.
- 2026-09-29 (PAR6) : **`clear` et `main` coûtent presque pareil ; `clear` ne passe dessous qu'à la 3e fiche d'une même session** — une session neuve relit en cache près de la moitié de sa base (moy. 39 680 tokens lus sur 73 602, N = 49) : son départ vaut 0,25 $, pas les 0,64 $ supposés (réécriture entière). Sur les 84 fiches jouées dans une session déjà ouverte, `main` a relu 30,99 $ de contexte hérité ; repartir à neuf aurait coûté 22,71 $ de départs : ≈ 8,28 $ d'écart, 0,10 $/fiche (5 % de 2,03 $). `main clear` = `clear` (réponse de l'utilisateur) ; le vrai essai de `boucle.py` ira dans `PAR7`, qui joue déjà des fiches payantes.

| Variante | N fiches | $/fiche | tours/fiche | base (1re requête) | lu / écrit à la 1re requête | contexte à l'entrée de la fiche |
|---|---|---|---|---|---|---|
| `enchainer` (sous-agents + relecteur) | 44 | 3,18 | 79,1 | 69 920 | 41 059 / ≈ 28 861 | 218 721 |
| `main` | 84 | 2,03 | 27,2 | 76 053 | 38 925 / ≈ 37 128 | 171 354 |
| `clear` (proxy : `/clear` + `/vlp:tache` à la main) | 49 | 2,18 | 30,1 | 73 602 | 39 680 / ≈ 33 922 | 73 602 |
| `main clear` | pas mesuré — même chose que `clear` | — | — | — | — | — |

Rang de la fiche dans sa session (fiches `main`) — relu hérité contre départ de sa session, moyennes, et fiches où `clear` aurait coûté moins : rang 1, 0,28 contre 0,27 $ (7/17) ; rang 2, 0,28 contre 0,28 $ (12/30) ; **rang 3, 0,59 contre 0,27 $ (11/17)** ; rang 4, 0,31 contre 0,25 $ (4/10) ; rang 5, 0,63 contre 0,25 $ (4/6) ; rang 6, 0,25 contre 0,27 $ (2/4). Au-delà du rang 3, N ≤ 10.

- **Vrai `claude -p`** (sans `boucle.py`) : 3 sessions `/vlp:tache` du 2026-09-26, bacs `bac1`–`bac3`, Haiku 4.5, fiches de bac triviales — 0,14 · 0,16 · 0,11 $, `ctx_1er` 42 622 · 42 629 · 42 625 : la base d'un `claude -p` est plus légère que celle de l'app (≈ 73 600).
- **Les $/fiche des lignes ne se comparent pas entre eux** : ce ne sont pas les mêmes fiches (les 44 à sous-agents viennent de REP → HAB, où le sous-agent était lui-même l'objet testé ; FEU et BTN surtout en `main`). La comparaison juste est l'écart relu/départ, fiche par fiche. Tours : ceux de `vlp.py cout`, sous-agents compris.
- **Pas compté** : un changement de modèle en `main` réécrit tout le contexte (`PAR2` : 139 752 tokens à la 1re requête Sonnet 5.5, ≈ 0,56 $ à 4 $/M) ; une compaction ; la qualité d'une fiche jouée dans un contexte chargé.
- **Méthode** : 177 fiches des fichiers `context AI/NN-*.md` qui portent des sessions ; plage = commit précédent nommant le préfixe → commit de la fiche, `$` et tours de `vlp.py cout`, mode par la session qui porte la plage (ouverte dedans : `clear` ; avant : `main` ; ≥ 1 sous-agent : `enchainer`). Script jetable, non commité (`Fichiers` de la fiche).

- 2026-09-29 (PAR3) : **une fiche refaite dans la plage compte dans la série** (LOC1, refaite de zéro dans le worktree de LOC, 3 fichiers comme `3864ec3`, choix de l'utilisateur) ; **la ligne de fiche de `cout` avale les commits hors fiche qui la précèdent** — PAR6 : 6,79 $ (58 tours), dont 3,30 $ (23 tours) d'ajout de PAR5–PAR7 la veille (`mesure-tokens.py --plage 092f774 7b4440a`) ; un cas chiffré pour `DEC` (n° 83). Le verdict lit PAR6 seule (3,49 $), tranché par l'utilisateur.
- 2026-09-29 (PAR7) : **Haiku 4.5 n'a fini aucune des deux fiches ; Sonnet 5.5 et Opus 5.5 les deux, Sonnet pour 0,95 $ la fiche contre 1,39 $** — ENQ2 et TAU1 (fiches de code closes) rejouées une fois par modèle, effort `low`, chacune dans un worktree jetable posé sur le commit d'avant la fiche (artefact à `aucun`, vérification « le critère de fin », seul changement), par `boucle.py --plafond 1 --model <id>` ; `--effort low` par un relais `.py` du scratchpad, `boucle.py` ne le passant pas (`scripts/boucle.py:104-107`). Juge, le même pour les six : le chef (Opus 5.5) applique le critère de fin — `test-vlp.py`, pyright, le mutant de la fiche, `contrat` — et 8 sondes d'`ecrit_git` pour ENQ2 (les 5 du critère, `$(…)`, accents graves, `&&`) ; relecteur non utilisé (choix de l'utilisateur). Tours et $ : `mesure-tokens.py <session>` (au cent près le `total_cost_usd` du CLI).

| Réglage | Jouées | Acceptées | Refusées | `RETOUR` | Tours/fiche | $/fiche acceptée |
|---|---|---|---|---|---|---|
| Haiku 4.5, `low` | 2 | 0 | 1 (TAU1) | 1 (ENQ2) | 49,5 (24 · 75) | sans objet — 1,57 $ (0,40 · 1,18) pour 0 acceptée |
| Sonnet 5.5, `low` | 2 | 2 | 0 | 0 | 26 (13 · 39) | **0,95** (0,49 · 1,41) |
| Opus 5.5, `low` | 2 | 2 | 0 | 0 | 26 (14 · 38) | **1,39** (1,03 · 1,74) |

- **Haiku** : 11 et 14 refus de permission (0 chez les deux autres) — les commandes de `/vlp:tache` enrobées de `cd "<chemin absolu>" &&`, `git -C "<chemin>"`, `/mnt/c/…` sous Git Bash ; `auto` ne laisse passer que `git add`/`git commit` en tête (`scripts/boucle.py:53`). ENQ2, **`RETOUR`** : rien commité, case vide ; le code passe `test-vlp.py` et pyright 0, mais sondes 7/8 (`echo "$(git add .)" > f` tu), limite absente de la docstring, 1er cas du critère recopié sans son `}`. TAU1, **refusée** : `ÉCART: clore : une clôture sous 1 000, comptée une fois`, pyright 1 erreur (« Code is too complex », test au niveau du module : FEU2), `? $` en cellule au lieu de rien. Les deux fois, il rend « ✅ Tout va bien ».
- **Sonnet et Opus** : sondes 8/8 ; mutant — ENQ2, `vlp.py` de départ : le test tombe ; TAU1, `estimation_usd` remis au joué : `ÉCART: clore : Fait. remplacé` ; `contrat` sur `a860169308600a92b` : `bloqué 1` → `bloqué 0`, `git 0` avant comme après (ENQ1 a séparé les colonnes après que le critère fut écrit). D'origine (Opus 5.5, `main` dans l'app, `vlp.py cout`) : ENQ2 0,93 $, TAU1 1,41 $.
- **Cause du changement de modèle, vérifiée** (session neuve `fd56c6c4`, `claude -p`) : lancée en `--model claude-opus-5-5`, `/vlp:enchainer main` répond en `claude-sonnet-5-5` dès l'`init` (50 068 tokens écrits, 0 relu, 0,21 $) — le `model: sonnet` de `skills/enchainer/SKILL.md:4` vaut pour le tour de la skill ; au tour suivant (`--resume`), retour à `claude-opus-5-5`, 51 172 écrits, 0 relu (≈ 0,41 $) : chaque bascule repaie tout le contexte. Vérifié en `claude -p`, pas dans l'app. Rien corrigé : à `PAR5`.
- **Limites** : N = 2 par réglage, un indice et pas une tendance ; trois parties en même temps (ENQ2 314 · 190 · 265 s, TAU1 563 · 735 · 494 s, Haiku · Sonnet · Opus) ; régime `claude -p` en `auto`, pas le sous-agent d'`enchainer` — le refus de Haiku tient en partie à ce régime. Coût de l'essai : parties 6,25 $, contrôles 0,70 $ (effort de Haiku 0,08 ; enchainer 0,21 ; reprise 0,41).
- 2026-09-29 : **chantier PAR clos** — livré : l'essai de deux chantiers en parallèle, mesuré avant d'être codé. `mesure-tokens.py --actif` compte le temps actif et l'attente (PAR1) ; la série de référence, 16,7 min/fiche sans cadrage et 4,29 $/fiche (PAR2) ; l'essai PAR ‖ LOC dans deux worktrees : réel **22 min** contre 66,8 en série, **gain 67 %** (48 % face à la série observée), 2,59 $/fiche (PAR3) ; la fusion prédite : 3 fichiers en conflit, 5 blocs, et `CHANTIER.md` perd LOC sans conflit (PAR4) ; le coût par mode d'`enchainer` : `main` 2,03 $/fiche, `clear` 2,18 $, sous-agents 3,18 $ (PAR6) ; le modèle par rôle : Sonnet 5.5 0,95 $/fiche acceptée, Opus 5.5 1,39 $, Haiku 4.5 0 fiche finie sur 2 (PAR7) ; le rangement des commandes — `/vlp:chef`, deux canaux la nuit, le kit ne code que la réservation des fichiers et la clôture à tour de rôle (PAR5, détail : entrée 72 `NUI`). Laissé ouvert : un seul essai, un point et pas une tendance ; `/vlp:chef` hors Opus la nuit, sans humain pour confirmer ; le `model: sonnet` d'`enchainer`, à retirer (les deux : entrée 72) ; `cout` avale le hors-fiche de la session (`DEC`, n° 83 — PAR5 porte 6,60 $). Les décisions D1–D6 du 2026-09-28 et le détail de l'essai vivaient à la ligne 58 de la TODO, retirée à cette clôture : `git show 4cd2c4b:"context AI/08-etat.md"`. PAR7 a coûté le plus (243 tours, 10,34 $, dont 7 essais `claude -p` 6,87 $). Rien d'abandonné. Estimé non noté, joué 7 fiches 39,62 $ ; `cout` : 501 tours. Coût du chantier : 66 248 116 (`vlp.py clore`).
- 2026-09-29 (LOC2) : **la liste d'attente ne tient que les pages sous `<contexte>/artefacts/`** — les 3 refus 429 de Cairn du 2026-09-27 (`3bf8a922`:625, `ad875ef2`:2323 et :2694) portaient un `file_path` dans le scratchpad, sans projet à trouver : `attente hook` s'y tait (`page_relative` rend `None`). Le texte du refus se lit dans `error` (exemple de la doc, `1cba232a`:1756), champ jamais vu sur un vrai refus : `LOC5` le vérifie.
- 2026-09-29 : **chantier LOC clos** — livré : une publication refusée n'arrête plus le chantier. La liste d'attente `<contexte>/artefacts/en-attente` (`vlp.py attente ajouter|lister|retirer|hook`, deux hooks sur `Artifact`), sa règle (`ARTEFACTS.md`, « Une publication refusée ») et l'aperçu local sans cache (`vlp.py apercu`, `/_telephone` à 375 px) ; `LOC5` les a essayés pour de vrai (liste 0 → 0 après un refus « non lue », 0 → 1 → 0 par le hook à la republication, couleur de `vlp.css` vue au rechargement, fichier rendu à l'octet). Laissé ouvert : le vrai refus 429 n'a pas été provoqué (la limite n'est pas usée), donc le champ `error` d'un vrai 429 reste prouvé par le seul test de `LOC2`. À savoir : `attente lister` prend le dossier `context AI/artefacts`, pas la racine du projet. Chantier 26 602 791 tokens.
- 2026-09-29 (REG3) : **un essai d'`enchainer` passe par `main`** — le plugin chargé (`~/.claude/skills/vlp`) suit le dossier principal, pas le worktree : REG1-2 invisibles tant que `main` n'avait pas avancé (fast-forward de 8 commits, sans push). Une session de l'app ouverte « pour l'essai » tournait dans un worktree du kit, pas dans le bac. `claude` absent du `PATH` : le CLI de l'app vit dans `%LOCALAPPDATA%/Packages/Claude_<id>/LocalCache/Roaming/Claude/claude-code/<version>/claude.exe` (app du Store, `AppData` virtualisé : le chemin court ne marche que depuis les shells de l'app).
- 2026-09-29 : **chantier REG clos** — livré : `/vlp:enchainer` sans argument joue les fiches dans la session (`main`), sans bascule de modèle (`model:` retiré de sa tête) ; `agents` (ex-défaut) et `clear` jouent en Sonnet `low`, l'effort transmis tel quel par `boucle.py --effort` (REG1-2) ; essayé pour de vrai sur un bac (REG3 : `Skill(vlp:tache)`, aucune ligne `Agent(vlp:fiche)`, F1 `[x]`, modèle inchangé). Laissé ouvert : l'essai s'est fait dans le CLI, pas dans l'app (panneau Tâches non vu) ; F2 et le plafond de 5 fiches non regardés ; la relance sur refus, le chef en Opus et l'effort par fiche restent à `NUI` (entrée 72). Estimé 1 fiche ≈3,03 $, joué 3 fiches 7,07 $. Chantier 11 796 217 (`vlp.py clore`).
