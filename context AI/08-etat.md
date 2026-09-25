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

## La TODO ordonnée — les chantiers possibles

C'est d'ici que `/chantier` tire ses propositions. Un chantier par entrée, cité
par son code, rangé par importance d'implémentation — rangée la nuit du
2026-09-24, décidé seul (l'utilisateur dormait ; validé au réveil) : d'abord ce qui
garde juste le code livré (`REV`, `CON`, `GLO`), puis les chiffres (`UNI`, `RCP`,
`ESS`, `EST`), l'outillage d'essai (`RAT`, `BAC`, `EVF`, `PYT`), enfin les pages,
dans l'ordre de leurs dépendances. Le numéro reste celui d'entrée. Le détail des
pages est dans `38-audit-artefacts.md` § 4, qui les nomme A à F ; les rangs 1 à
24, tous retirés, venaient de `12-audit.md` ; 31 à 34, de la clôture de `REP` ; 35
à 37, de celle de `CPT` ; 38 à 41, de celle de `SAG` ; 42, de `FIL1` ; 43 à 47, de
celle de `FIL` ; 48 à 51, de celle de `FIN` ; 52, des clôtures de la nuit du
2026-09-24 ; 53, du cadrage de `REV` ; 54, d'une demande de l'utilisateur pendant `REV5` ; 55 à 57, de la clôture de `REV` ; 58, d'une demande de l'utilisateur le 2026-09-25 ; 59 à 61, de la clôture de `CON` ; 66, de celle de `JUG`.

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 47 | `ESS` — Les essais `claude -p` dans le coût | Un essai `claude -p` tourne dans une autre session, que `cout` ne voit pas : il s'ajoute à la main, « hors total ». Au moins 14 chantiers clos en portent — 12 sur la feuille de route, `SAG` et `FIL` au fichier d'état —, ≈ 12,32 $ absents de tout total (somme faite à la main). `cout` ira chercher les sessions des bacs lancées pendant la fiche. 🟡 Les relier à leur fiche — dossier du bac, heure —, et le sort des evals : à trancher au cadrage. Même but que `FIN`, autre mécanisme. | ~1 fiche | — |
| 36 | `EST` — L'estimé face au réel, à chaque clôture | La TODO estime chaque chantier ; rien ne compare ensuite. `CPT`, estimé « ~2 fiches », en a joué 4. Le bilan de clôture écrira l'estimé à côté du réel — fiches jouées, tokens —, pour que `/vlp:chantier` estime mieux les suivants. | ~1 fiche | — |
| 43 | `RAT` — Un `Read` raté réveille-t-il le filet ? | Reste de `FIL` : le filet tire après un `Read` réussi et après un Bash à code non nul (`FIL3`), mais un `Read` sur un fichier absent n'est pas éprouvé. La doc range dans `PostToolUseFailure` l'outil lancé qui échoue, pas l'appel refusé avant de s'exécuter (journal du 2026-09-24). S'il n'en déclenche aucun, des derniers tours de `Read` ratés laissent le sous-agent coupé muet. Un essai à plafond 10, comme `FIL3` (≈ 0,1 $). | ~0,5 fiche | — |
| 45 | `BAC` — Un bac d'essai par script | `SAG4` et `FIL3` ont rebâti leur bac à la main — `CHANTIER.md`, fiches factices, fichiers —, puis compté la transcription du sous-agent par un script jetable. `FIL3` y a buté deux fois : la section `## L'ordre des fiches` exigée par le hook, et « un appel par tour », lu par Haiku comme « par exécution » (0,148 $ perdus). `vlp.py` posera le bac en un appel, et comptera la transcription : tours, avertissements du filet et l'outil qui les précède, `hook_non_blocking_error`, premier mot et `stop_reason` du dernier message. Le lancement `claude -p` reste à la main, chiffré avant. | ~1 fiche | — |
| 46 | `EVF` — Le filet en eval rejouable | Les deux essais de `FIL3` en eval du plugin (chantier `V`) : un changement de `hooks/hooks.json` ou de `vlp.py filet` se reprouve en un appel, ≈ 0,16 $ le passage (0,06411505 + 0,10040705). 🟡 Qu'un eval lise la transcription d'un sous-agent : pas vérifié. | ~2 fiches | `BAC` |
| 25 | `VOI` — Finir les feuilles voisines, reste de `REP` | Ce que `REP` a laissé. La ligne `MARKDOWN` de `vlp.py niveau` compte, sans `--ecrire`, la page régénérée au lieu de celle du disque : elle ne voit ni la TODO ni la zone « en cours ». La régénération abîme trois feuilles voisines : TODO de MapDecorator hors table, donc lue vide ; lettres de fiche entre backticks ignorées ; source de TrackGen sans accents. Une fois corrigées, republier MapDecorator, TrackGen et ProjetONZSM. Détail : journal du 2026-09-23. | ~3 fiches | — |
| 26 | `ABR` — Mettre notes et journal à l'abri dans un `.md` | Les notes et le journal d'une page de chantier n'existent aujourd'hui que dans la page. `page --note` et `--journal` écriront d'abord le texte entier dans un `.md`, et la page le recopiera. | ~3 fiches | — |
| 27 | `ALE` — Essai : alléger la republication | Deux pistes, mesurées : le CSS en fichier joint, puis les données dans la base de claude.ai. Décide où vivent le CSS et les données avant `PLI` et `FEU`. | 2 fiches | `ABR` |
| 28 | `PLI` — La page de chantier plus courte et lisible | Chaque fiche dans un bloc repliable, le journal replié sauf ses dernières entrées, le bilan en haut d'un chantier clos. Rien n'est coupé : replié, le texte reste dans la page. | ~5 fiches | `ABR`, `ALE` |
| 29 | `FEU` — La feuille de route plus courte et lisible | La TODO en cartes, le détail replié, un sommaire. 🟡 Une décision à prendre : la feuille garde-t-elle tout le détail de la TODO ? | ~4 fiches | `VOI`, `ALE` |
| 30 | `BTN` — Des boutons, en dernier | Commenter une fiche, tout déplier, filtrer, copier la commande d'une fiche, un graphique des coûts. Optionnel. | ~4 à 6 fiches | `PLI`, `FEU` |
| 53 | `LEC` — `/vlp:chantier` ne lit plus l'état en entier | L'étape 1 de `/vlp:chantier` lit « en entier » le fichier que `CHANTIER.md` nomme « chantiers possibles » — ici `context AI/08-etat.md`. Mesuré au cadrage de `REV`, le 2026-09-24, avant l'ajout de cette entrée : 1 223 lignes, 57 260 tokens selon l'outil `Read`, qui n'en rend que 453 lignes d'un coup (plafond de 25 000 tokens) ; relus à chaque tour de la séance (`methode-chantier.md:9`). Pour choisir, la TODO suffit : le journal fait 78 % des lignes (271 à 1 223). 🟡 À trancher au cadrage : lire la seule TODO par script, ou sortir le journal dans son propre fichier (« Un fichier = un sujet », `methode-chantier.md`). Ajoutée à la demande de l'utilisateur ; rang pas encore fixé, d'où la fin de table. | 🟡 pas estimé | — |
| 54 | `TYP` — pyright sans erreur, puis gardé au commit | **Nettoyé le 2026-09-25, hors chantier** (`8acfc79`) : `pyright scripts/` 37 → 0, tests inchangés ; reste la garde au commit. Demandé par l'utilisateur le 2026-09-24, pendant `REV5`. La règle « pyright avant le commit » vit dans `~/.claude/CLAUDE.md` ; pour le kit, décidé avec lui : nettoyer d'abord, puis zéro erreur, gardé par `.githooks/pre-commit`. Mesuré le 2026-09-24, `pyright scripts/` (paquet pip `pyright` 1.1.414, sans configuration) : 37 erreurs, 0 avertissement, 8,6 s — `test-vlp.py` 18, `vlp.py` 13, `mesure-tokens.py` 3, `test-mesure-tokens.py` 3 ; par règle, `reportOptionalMemberAccess` 10, `reportAttributeAccessIssue` 8, `reportPossiblyUnboundVariable` 5, `reportArgumentType` 5, `reportOperatorIssue` 3, `reportAssignmentType` 3, `reportIndexIssue` 2, `reportFunctionMemberAccess` 1. Dans `test-vlp.py`, surtout des noms de module réemployés (`lu`, `g`) et `mod.GIT` posé sur un module chargé par `importlib`. Le kit est cloné en groupe : sans pyright, le hook saute en le disant. Tests d'abord, mutants. 🟡 À trancher au cadrage : `context AI/38-audit-scripts/` (10 fichiers `.py`) dedans ou non ; le mode de pyright, dans un `pyrightconfig.json` ; lancer pyright à chaque commit, ou seulement quand un `.py` est touché (8,6 s par passage). Ajoutée à la demande de l'utilisateur ; rang pas encore fixé, d'où la fin de table. | 🟡 pas estimé | — |
| 55 | `FUI` — Le relecteur ne voit pas la suite | La skill `vlp:relire` donne au relecteur la carte du projet, qui liste les titres des fiches : au quatrième passage de `REV4`, le relecteur de `7d16873` y lisait « REV6 [x] — Un en-tête sans plage reste tel quel », le défaut qu'il devait trouver (transcription `agent-a56a4a45f6ee3c52c`). Au passage d'avant, la même carte ne l'avait pas fait trouver : un indice, pas la réponse. Le relecteur recevra ce dont il juge — fiche, socle, diff — sans les titres ni l'état du chantier. 🟡 Ce que la carte apporte d'autre au relecteur : pas mesuré. | ~1 fiche | — |
| 56 | `ENR` — La relecture dans un vrai `/vlp:enchainer` | `REV3` a branché `vlp:relire` dans `/vlp:enchainer`, mais la relecture n'a tourné qu'appelée à la main par le chef (`REV4`, 4 passages, 0,50 $ la relecture au dernier état). Jamais sur un `FAITE` vivant, ni avec un `REFUSÉE` qui arrête la chaîne et marque la page bloquée. Un chantier de deux ou trois fiches enchaîné, dont une piégée, le prouvera. | ~1 fiche, plus l'essai | `FUI` |
| 57 | `PLG` — La plage de l'en-tête et la dernière fiche | `plage()` prend la première et la dernière fiche **du fichier** : `REV`, rangé REV1…REV3, REV5…REV8, REV4, s'affiche « fiches REV1–REV4 » alors que REV8 existe (vu par le relecteur de `eb2a6b0`, 2026-09-25). Voulu par `PLA` pour la feuille de route. 🟡 À trancher : l'ordre du fichier, ou le plus haut numéro. | ~0,5 fiche | — |
| 58 | `PAR` — Deux chantiers en parallèle, s'ils ne se chevauchent pas | Tout le kit suppose un seul chantier à la fois : `CHANTIER.md` s'intitule « Chantier courant » et ne porte qu'un **fichier de fiches courant** et qu'un **artefact du chantier** (`CHANTIER.md:1`, `:16`, `:18`) ; `/vlp:tache` et `/vlp:enchainer` jouent « une fiche du chantier courant » ; `vlp.py ouvrir` et `clore` écrivent ces lignes uniques. Deux chantiers dont les fichiers touchés sont disjoints pourraient tourner en même temps, dans deux sessions. 🟡 À trancher au cadrage : comment `CHANTIER.md` porte deux chantiers courants sans devenir ambigu (il est lu **en entier** par `/vlp:chantier` et `/vlp:tache`) ; comment une commande sait duquel il s'agit (argument, ou lettre de fiche) ; qui vérifie le non-chevauchement, et sur quoi — les fichiers que les fiches nomment, ou une liste déclarée à l'ouverture ; un seul dépôt ou deux worktrees, et l'ordre des commits ; ce que deviennent la page publiée et le coût, que `cout` coupe aux commits de fiche. Ajoutée à la demande de l'utilisateur ; rang pas encore fixé, d'où la fin de table. | 🟡 pas estimé | — |
| 61 | `CHK` — `/vlp:check` lit le contrat | `vlp.py contrat` (chantier `CON`) ne tourne qu'à la main. `/vlp:check` le lancera `--depuis` l'ouverture du chantier courant et dira, sans rien rejouer, combien de sous-agents, combien ont écrit dans Git, combien sans statut en tête — le bulletin du gardien. 🟡 L'heure d'ouverture : commit `Chantier … ouvert`, ou session du cadrage notée par `ouvrir`. | ~0,5 fiche | — |
| 63 | `ECH` — `ECRIT_GIT` ne lit pas le texte d'un heredoc | Le gardien a refusé à deux relecteurs de `RLG1` (2026-09-25) un heredoc ou un `echo` qui ne faisait qu'écrire les mots `git commit` ou `git add` dans un fichier de sonde. `ECRIT_GIT` cherche le motif dans toute la commande. Vrai aussi pour `vlp:fiche`, depuis `CON`. 🟡 Jusqu'où lire le shell : couper les chaînes citées ne suffit pas pour un heredoc. | ~0,5 fiche | — |
| 64 | `SON` — Rejouer un hook à la main sans le tampon | `une_fois` (chantier `PYT`) fait taire la même entrée rejouée en moins de 60 s, même par une autre copie de `vlp.py` : un relecteur de `RLG1` a dû ajouter un `nonce` pour comparer AVANT et APRÈS. Une variable d'environnement, ou une option, qui saute le tampon hors d'un vrai hook. | ~0,5 fiche | — |
| 66 | `OUV` — Une ligne qui s'ouvre par un mot de jauge, sans être une jauge | Reste de `JUG` : le gardien (règle `tete`) renvoie une ligne qui **commence** par « Imprévu », « Pas bon »… même quand ce n'est pas la jauge — une puce `- Imprévu : j'ai dû…`, un `REFUSÉE` dont une ligne s'ouvre par « Pas bon ». Absent des 29 sous-agents mesurés en `JUG1` ; `stop_hook_active` borne le coût à un renvoi. 🟡 Exiger l'émoji de la jauge devant le mot, ou le mot suivi de `—`/`…`/fin de ligne : à mesurer sur le corpus comme en `JUG1` (`forme --regle`). | ~0,5 fiche | — |

## Journal des décisions

Une ligne par décision imprévue tranchée en cours de fiche — jamais un résumé
de ce que le code dit déjà.

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
