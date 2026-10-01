> **QUAND LIRE** : on joue une fiche `NUI*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache NUI<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier NUI — Le chef de nuit

**À quoi il sert.** Le kit n'enchaîne qu'un chantier à la fois, et chacun attend l'utilisateur pour se cadrer et se clore.
`/vlp:chef` cadre le soir, joue plusieurs chantiers la nuit sur deux canaux sans humain, fusionne et rend un rapport le matin.

**Estimé.** 6 fiches · ≈18 $ — ≈2,98 $/fiche sur 88 clos (le 2026-10-01).

**Fait.** Rien. Ouvert le 2026-10-01, cadré en 20 fiches, `NUI1` à jouer.

**Session** : d0a75cf6-8b7d-417c-9775-44ffe5decb84

## Le socle commun

**Les décisions** vivent dans la TODO n° 72 (`context AI/08-etat.md:381` : PAR5 Q1-Q11, cadrage du
2026-09-29 Q1-Q8, deuxième tour) : on y renvoie, on ne les recopie pas. Celles qui font plusieurs fiches :
- **Deux canaux**, A et B ; même canal si dépendance ou fichier commun. **Un canal = un worktree**
  `.claude/worktrees/nuit-<date>-<A|B>`, créé depuis `main` par la ligne de lancement (`NUI9`) ; jamais
  un worktree par chantier. **Une branche par chantier** : `nuit/<date>-<A|B>-<code>`, créée dans ce
  worktree par boucle.py depuis le dernier chantier réussi du canal (`main` au départ).
- **Mis de côté** (chantier bloqué) : laissé ouvert dans sa branche, travail commité `WIP …` par le lanceur
  (sujet hors `COMMIT_FICHE`), canal reparti d'une branche neuve, dépendants sautés. Le matin, la branche est
  listée, jamais fusionnée ; l'utilisateur choisit : reprendre à la main, abandonner, rejouer la nuit suivante.
- **Modèles par rôle**, ID épinglé : chef, découper, clore, relire `claude-opus-5-5`, repli
  `--fallback-model claude-opus-5,claude-sonnet-5-5` ; relance (refus `copie`, une fois) `claude-opus-5-5`
  effort medium, même repli ; jouer `claude-sonnet-5-5` effort low. Fable jamais la nuit.
- **Borne double** : en $ et en nombre de chantiers, pot commun aux deux canaux, relue avant
  chaque session ; atteinte, la fiche en cours se finit et le chantier reste ouvert.
- **Relire avant le commit** : la session de fiche ne commite pas ; boucle.py relit l'instantané, commite sur ACCEPTÉE.

**Les noms retenus** (nouveaux — aucune sous-commande `vlp.py` de ce nom n'existe) :
- `boucle.py --nuit` : un canal, chantier par chantier ; `--reprendre` ; pose `VLP_NUIT=1`, et
  `carte` imprime alors `NUIT=1`. Rôles : `découper` (`/vlp:chantier <code>`), `jouer`
  (`/vlp:tache <fiche>`), `relire`, `relance`, `clore`. Relectures : `vlp-relecture-<canal>-*`.
  `--permission-prompts none` : CLI ≥ 2.1.259 selon le cadrage, non vérifié ici (`NUI1` l'essaie).
- Plafonds par rôle (`--max-turns`, `--max-budget-usd`, timeout) : valeurs fixées et justifiées par mesure dans `NUI4`,
  puis boucle.py ; relire lit `maxTurns` d'agents/relecture.md (`lire_max_turns`, vlp.py:1617). Verrou, `CARNET_MIN`, `LECONS_MAX` : `NUI3`, `NUI11`.
- `scripts/carnet.py` : le carnet `<git-common-dir>/vlp-nuit/<date>.jsonl`, hors Git et hors worktrees,
  une ligne JSON par session. Clés : `nuit canal chantier role fiche modele_demande modeles_vus tours_cli
  usd_cli duree_s issue refus_n cause reecriture garde plugin_retard session` ; le matin ajoute
  `usd_kit tours_kit` (mesure-tokens.py) ; on ne compare que `_kit` à `_kit`. `issue` : pas partie,
  ratée, jouée, plafond, limite, timeout, coupure. Une ligne `STOP` arrête les deux canaux.
- `scripts/faux-claude.py` : le faux `claude` des tests, un rôle par prompt, piloté par l'environnement.
- `nuit.md` (racine du kit) : la conduite de nuit ; les commandes y renvoient en une ligne.
- `<contexte>/NN-nuits.md` : fichier projet numéroté, déclaré à l'index (ligne `index` de CHANTIER.md,
  lue par `champ(carte_, "index")`, vlp.py:4897) — plan du soir, table des nuits, `## Leçons`.
  Libellé optionnel de `CHANTIER.md` : `- **vérification de nuit** : <commande>`.
- `vlp.py trier`, `nuits noter [--sorte]`, `nuits lecon`, `plan`, `matin`, `chef page --questions <json>` (autre que `page`) ; `/vlp:chef` : `skills/chef/SKILL.md`.

| Symbole | Fichier:ligne | Ce qu'il rend |
|---|---|---|
| `cmd_ouvrir` | vlp.py:5134 | `GARDE: un chantier est déjà ouvert` (5153) — d'où une branche par chantier |
| `cmd_clore` | vlp.py:4850 | CHANTIER.md (courant, artefact → aucun ; lettre), index, CLAUDE.md (routage ; fenêtre `CLOS_GARDES`, 1362), archive ; la feuille en dernier, en échec `GARDE:` après écritures (5058) |
| `todo_du_fichier` | vlp.py:3223 | `[(n, chantier, apporte, coût, dépend)]` ; ligne ≠ 5 cellules : `ValueError` |
| `carte` | vlp.py:714 | `PROJET=`, CHANTIER.md, `ATTENTE=`, `PLUGIN_RETARD=` (739), `PROCHAINE=` (764) |
| `cmd_relecture` · `instantane` | vlp.py:1240 · 1201 | sans `--sha`, l'arbre en commit de parent `HEAD`, ni `HEAD` ni l'index bougés |
| `retirer_relectures` · `RELECTURE` | vlp.py:1189 · 1143 | retire TOUS les `vlp-relecture-*` du dépôt ; appelée 1250, 1256, 1278, 1289 |
| `cmd_cocher` · `refuser` | vlp.py:1055 · 1104 | `CASE <fiche> [x]`, `TÊTE <sha>` (`--verifier`) ; `REFUSÉ <fiche> · refus <n>` ; `Erreur :` remplacé, jamais doublé (1134) : boucle.py garde le motif d'avant |
| `SESSION` · `sessions_de` | vlp.py:422 · 833 | `**Session** : <id>`, une par ligne, lues par `cout` (898) ; `cocher` l'ajoute depuis `CLAUDE_CODE_SESSION_ID` (1097) |
| `COMMIT_FICHE` · `heures_commits` | vlp.py:2342 · 2346 | sujet `<fiche> :` · heure du plus ancien commit de chaque fiche |
| `STATUTS` · `VERDICTS` | vlp.py:1659 · 1850 | `FAITE RETOUR BLOQUÉE` · `ACCEPTÉE REFUSÉE` |
| `lire_attente` · `ecrire_attente` · `lire_publie` | vlp.py:4386 · 4399 · 2112 | `en-attente` `[(page, url, heure)]`, retiré vide · `publie` (2104) `{(page, nom): sha256}` ; ni l'un ni l'autre suivi dans le kit, `.gitattributes` sans `merge=union` : `NUI16` ajoute la ligne, ne la garde pas |
| `cmd_claude` · `cmd_bac` | vlp.py:5354 · 5363 | `CLAUDE <chemin>` · un bac d'essai et ses commandes `claude -p` |
| `cmd_mutant` | vlp.py:5569 | `mutant <fichier> <avant> <après> [--test "<cmd>"]` → `MUTANT ATTRAPÉ <n>`, fichier rendu |
| `cmd_vigile` · `cmd_valider` | vlp.py:4328 · 1447 | `PAGE SAINE` ou `GARDE:` · avertit au-delà de `SEUIL_FICHE`, `SEUIL_SOCLE` (1356-1357) |
| `cmd_gardien` | vlp.py:2027 | muet hors `agent_type` fiche ou relecture (2039-2044) : une session `-p` sans `--agent` n'est pas gardée (`NUI1` l'essaie) |
| `HERITEES` · `AUTORISES` · `INTERDITS` | boucle.py:48 · 51 · 53 | variables ôtées à la fille · `git add`, `git commit` permis · `--amend`, `--no-verify`, `-n` refusés |
| `lire_carte` · `jouer` | boucle.py:72 · 88 | `(racine, fichier, prochaine)` · une session `-p` sans timeout (102), `result` lu (111-114) |
| `resoudre` · `message.model` | mesure-tokens.py:94 · 293 | id de session → son `.jsonl` · le modèle de chaque message |

**Invariants** — une fiche qui en casse un est refusée :
- Sans `--nuit`, boucle.py ne change pas (REG : `context AI/93-reglages-enchainer.md:30-31`).
- La nuit n'écrit aucun fichier suivi hors du travail des chantiers ; ses notes vont au carnet.
- Ni push ni question la nuit ; ce qui attend un humain va au matin (`nuit.md`).
- Aucun sous-agent n'écrit dans Git. La nuit commitent boucle.py (découpage — `/vlp:chantier` ne commite
  pas —, fiche ACCEPTÉE, `WIP`) et la session `clore` (cloture.md:72, `AUTORISES` gardés) ; `jouer`, `relire`, `découper` jamais.
- Un test bâtit son projet, son dépôt et son carnet dans un dossier temporaire.
- Python 3 sans dépendance, pyright à zéro erreur sur les fichiers touchés ; `vlp.py` en LF, `test-vlp.py`
  en CRLF : l'outil Edit. `${CLAUDE_PLUGIN_ROOT}` : commandes et hooks.json seuls. CLAUDE.md est au seuil
  (`SEUIL_CLAUDE`, vlp.py:1359) : une ligne ajoutée en remplace une.
- Le plugin chargé suit `main`, pas le worktree ; `/reload-plugins` est un geste de l'utilisateur.

**Une fiche de code NUI** nomme son test et son mutant : `vlp.py mutant <fichier> <avant> <après>`
(défaut test-vlp.py ; `--test "py -3 scripts/test-boucle.py"` pour boucle.py). Dès `NUI2`,
test-vlp.py lance test-boucle.py. Une fiche de prose : un grep qui compte, et un micro-essai sur bac.

**Dehors** : BDD ; push la nuit ; sessions cloud, `--bg` ; agent teams ; plusieurs projets par nuit ; effort
par fiche ; Fable la nuit ; ratio nuit/jour sur l'estimé ; leçon écrite par la nuit dans methode-chantier.md ;
timeout adaptatif ; « mêmes fichiers » par `git merge-tree` ; vérification de nuit exigée des autres projets ;
eval du tri avant trois nuits ; `claude -w`. Écartés au cadrage, ou en attente des chiffres de plusieurs nuits.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `NUI1` | Relever les formes réelles d'une session -p | rien |
| `NUI2` | Faire un faux claude par rôle | `NUI1` |
| `NUI3` | Tenir le carnet et la borne double | `NUI2` |
| `NUI4` | Donner à chaque rôle ses plafonds | `NUI3` |
| `NUI5` | Relire avant le commit | `NUI4` |
| `NUI6` | Relancer plus fort, ou arrêter tôt | `NUI5` |
| `NUI7` | Enchaîner les chantiers d'un canal | `NUI6`, `NUI12` |
| `NUI8` | Reprendre une nuit coupée | `NUI7` |
| `NUI9` | Lancer les deux canaux d'une ligne | `NUI7` |
| `NUI10` | Trier les chantiers prêts | rien |
| `NUI11` | Tenir le fichier des nuits | `NUI3`, `NUI10` |
| `NUI12` | Écrire le plan de nuit | `NUI11` |
| `NUI13` | Écrire la conduite de nuit | `NUI12` |
| `NUI14` | Renvoyer les commandes à nuit.md | `NUI13` |
| `NUI15` | Fusionner le matin : CHANTIER.md et la feuille | rien |
| `NUI16` | Fusionner le matin : 08-etat.md et les listes | `NUI15` |
| `NUI17` | Remplir une page à cartes par script | rien |
| `NUI18` | Écrire /vlp:chef, le soir | `NUI9`, `NUI11`, `NUI12`, `NUI13`, `NUI17` |
| `NUI19` | Écrire /vlp:chef, le matin | `NUI13`, `NUI15`, `NUI16`, `NUI18` |
| `NUI20` | Jouer une nuit réelle | toutes (`NUI1` à `NUI19`) |

Deux voies se jouent en parallèle — boucle.py (`NUI1` → `NUI9`, en chaîne) et vlp.py avec sa prose (`NUI10` → `NUI17` ; `NUI15` et `NUI17` partent de rien) — et se rejoignent à `NUI11` (il lit les carnets par carnet.py, `NUI3`), à `NUI7` (il lit le plan de `NUI12`), puis à `NUI18`-`NUI19`. `NUI12` ne touche que vlp.py (`plan` écrit le plan, `carte` imprime `NUIT=1` quand `VLP_NUIT=1` est posé) : poser `VLP_NUIT=1` et lire le plan dans boucle.py reviennent à `NUI7`. Fiches à cheval, jamais en même temps qu'une fiche de l'autre voie : `NUI2` (test-vlp.py lance test-boucle.py, comme le test de `NUI10`), `NUI3`, `NUI5` et `NUI6` (vlp.py : `nuits noter`, relectures par canal, `cocher --session`, la constante de `refuser`). `NUI20` attend tout.

---

<!-- FICHE:NUI1 -->
## NUI1 [x] — Relever les formes réelles d'une session -p

**Session** : d4efca2e-77f5-426f-a1e1-e528bce64e4b
**Dépend de** : rien.
**Fichiers** : `context AI/08-etat.md` (seul fichier écrit) ; lus : `scripts/vlp.py` (`cmd_bac`, `BAC_FICHIER`, `cmd_claude`, `cmd_kit_essai`, `cmd_gardien`, `REFUS_GIT`, `cmd_vigile_hook`, `defauts_page`), `scripts/boucle.py` (`jouer`, `HERITEES`, `AUTORISES`), `scripts/mesure-tokens.py` (`resoudre`), `hooks/hooks.json` (`PreToolUse`), `agents/relecture.md`, `.githooks/pre-commit`, `scripts/test-vlp.py` (3211-3215), `methode-chantier.md` (l. 220) — et rien d'autre.

**Prompt**
boucle.py (`NUI2` à `NUI8`) va lire des sorties de `claude -p` que personne n'a vues : tu les vois en vrai,
avant qu'un faux claude les imite. Aucun code ici. Pose un bac dans un dossier vide du scratchpad (`vlp.py bac`),
trouve la CLI (`vlp.py claude`), note `claude --version`. Chaque session : `-p`, `--output-format stream-json
--verbose`, un `--max-budget-usd` bas, sans les variables de `HERITEES` (boucle.py:48), trace au scratchpad.
**Avant de lancer**, annonce la somme de ces plafonds et attends l'accord de l'utilisateur : fiche de `/vlp:tache`,
jamais d'`enchainer` ni de la nuit.
1. `--model claude-opus-5 --session-id <uuid>` : répond-il ? l'uuid revient-il dans `system/init` ?
2. `--model` inexistant, avec puis sans le `--fallback-model` du socle (deux sessions) : repli visible où
   (`system/api_retry`, `message.model` lu comme mesure-tokens.py:293, clés de `modelUsage`) ? forme d'une session qui ne part pas ?
3. `--model claude-opus-5-5` (l'ID épinglé, seul, sans `--agent`), le `--fallback-model` du socle, `--permission-prompts
   none`, un prompt qui exige une question avant d'écrire : la liste à virgule est-elle acceptée telle quelle (`init`, ou
   erreur au départ) ? quel modèle dans `init` ? `AskUserQuestion` dans ses outils ? question en texte ? `permission_denials` ?
4. Une page d'une ligne écrite par toi, avec une balise `<style>` et un texte visible, passée par `vlp.py vigile`
   (`PAGE SAINE`) avant le lancement, puis publiée par `Artifact` (`--allowedTools Artifact`) : lien dans le `result`,
   refus de la CLI, ou `deny` du kit (`cmd_vigile_hook`, vlp.py:4343 — issue à part) ? Une publication, pas plus (limite du jour).
5. Un 2e bac en dépôt Git (`git init` par toi) ; `--agent vlp:relecture`, l'ID du rôle relire (socle), `--allowedTools
   "Bash(git commit:*)"` (la forme d'`AUTORISES`, boucle.py:51) : quel modèle dans `init` — l'ID demandé, ou le `model: opus`
   d'agents/relecture.md:4 ? Demande `git commit --allow-empty`. Trois issues : `deny` du gardien (`REFUS_GIT`, vlp.py:1664,
   dans le `tool_result` : il voit `relecture`, vlp.py:2039-2044) ; refus de permission sans `REFUS_GIT` (gardien non
   atteint) ; appel exécuté, même en échec Git (gardien muet). Aucun appel : « non observé ».
6. `--max-turns 2`, puis 7. `--max-budget-usd 0.01` : le texte du prompt de `F1` (`BAC_FICHIER` : douze `Read`
   d'affilée), lancé direct avec `--allowedTools Read`, pas la commande `Skill` du bac : code de sortie, `subtype`,
   `is_error`, `total_cost_usd`.
8. La même session tuée en cours, comme le ferait `subprocess.run(timeout=…)` sous win32 : code, dernière ligne, `result`
   présent ? `mesure-tokens.py <session_id>` (`resoudre`, mesure-tokens.py:94) rend-il son coût ? Le 143 de la doc
   headless ne s'écrit que s'il est vu.
9. `claude plugin validate`, sur les deux manifestes comme `.githooks/pre-commit` puis sur le dossier, dans une copie
   `vlp.py kit-essai <dossier> --max-turns 1` dont une `skills/*/SKILL.md` est cassée exprès : l'erreur est-elle vue ?
   Vérifie la note `08-etat.md:558-559` ; test-vlp.py:3211-3215 ne casse que `plugin.json`, jamais une `SKILL.md`.
Tu ne provoques pas de limite d'usage (`NUI2` l'imite d'après la doc, marquée non observée), ne fixes aucun plafond de rôle (`NUI4`), n'écris pas le faux claude (`NUI2`), n'écris Git que dans le bac.
Consigne dans le fichier d'état, où la méthode range une mesure (methode-chantier.md:220), en section `## <date du jour> — NUI1`, forme de `08-etat.md:1525` — pas une puce du journal des décisions.

**Critère de fin**
`grep -c "^## .* — NUI1\b" "context AI/08-etat.md"` : 0 avant, 1 après. La section porte une table : 9 sessions `-p`,
une ligne chacune (options, code de sortie, `subtype`/`is_error` ou « aucun result », modèles vus, `total_cost_usd`,
verdict oui / non / non observé — jamais « déduit »), plus une ligne pour `validate` (commande, code de sortie, sortie
brute réduite) ; la somme des coûts des 9 à côté du plafond annoncé ; puis une ligne JSON réduite par forme distincte,
seule source de `NUI2` : toutes les clés, à tous les niveaux, chaque valeur remplacée par son type (number, string,
list, object), sauf `type`, `subtype`, `is_error` et les noms de modèles ; ni texte de message ni chemin, `<bac>` à sa place.
Comptes sur `git diff -U0 -- "context AI/08-etat.md" | grep "^+"` : lignes ouvertes par `+|` 12 ; par `+{"type"` une
par forme, 1 au moins ; `znorr` 0 ; `Users` 0. `git status --short` ne montre que ce fichier.
<!-- /FICHE -->

---

<!-- FICHE:NUI2 -->
## NUI2 [x] — Faire un faux claude par rôle

**Session** : d4efca2e-77f5-426f-a1e1-e528bce64e4b
**Dépend de** : `NUI1`.
**Fichiers** : `scripts/faux-claude.py` (nouveau), `scripts/test-boucle.py`, `scripts/test-vlp.py` ; lus : `context AI/08-etat.md` (entrée `(NUI1)`, ses lignes JSON réduites), `scripts/boucle.py` (`jouer`, `lire_carte`), `scripts/vlp.py` (`cmd_ouvrir`, `cmd_cocher`), `enchainement.md`, `skills/tache/SKILL.md` (l. 50-53), la page https://code.claude.com/docs/en/errors (doc officielle) — et rien d'autre.

**Prompt**
Les fiches `NUI3` à `NUI9` testent boucle.py au faux claude ; celui d'aujourd'hui (`FAUX`, test-boucle.py:23-30)
coche `fiches.md` en dur, sortie jetée (l.26-27), et n'émet qu'un `result` : découpage, repli, refus, limite y
passent à vide. Sors-le dans `scripts/faux-claude.py` (main sous `if __name__`), lancé tel quel par `--claude`
(boucle.py:90) ; `FICHE` (test-boucle.py:32-44) y déménage, chargé par `importlib` comme test-vlp.py:29-32.
- Rôles (noms : socle). Découper, `/vlp:chantier <code>` : écrit `<code>.md` à deux fiches `FICHE` et remplace
  la ligne `**fichier de fiches courant**` de CHANTIER.md (motif de `cmd_ouvrir`, vlp.py:5162) — jamais
  `vlp.py ouvrir` ni `clore`, qui exigent index et options. Jouer, `/vlp:tache <fiche>` : lit le courant de
  CHANTIER.md du cwd comme `lire_carte` (boucle.py:81-84), y coche par `vlp.py cocher`, sauf `VLP_FAUX_RATE`
  (gardé) ; `cocher` non nul : sa sortie sur stderr, code 2. La relance est ce rôle, seul `--model` change.
  Clore, `/vlp:tache` sans fiche (skills/tache/SKILL.md:50-53) : courant et artefact passent à `aucun`.
  Relire, `--agent vlp:relecture` dans argv (comme `NUI1` l'a lancé) : la fiche est le premier mot du prompt
  (`<fiche> [--sha <sha>]`), verdict à la forme d'enchainement.md:33-35. Prompt inconnu : une ligne sur
  stderr, rien sur stdout, code 2 — jamais « joué » en silence.
- Pilotes : `VLP_FAUX_REFUSE=<fiche>:<cause>` (relire refuse cette fiche ; `fiche` avec sa ligne `RÉÉCRITURE`,
  enchainement.md:44) ; `VLP_FAUX_LIMITE=<préfixe>` (une session dont `--model` y commence rend la limite) ;
  `VLP_FAUX_REPLI=1` (`message.model` = premier de `--fallback-model`) ; `VLP_FAUX_DORT=<s>` ;
  `VLP_FAUX_ERREUR=<forme>`, une valeur par forme d'échec relevée par `NUI1` (au moins : coupure après
  `system/init` sans `result` ; erreur d'API avant le premier tour).
- Sortie : les formes de `NUI1`, réduites — `system/init` (l'id de `--session-id` s'il est passé), une ligne
  `assistant` avec `message.model`, `result` avec `num_turns`, `total_cost_usd`, `modelUsage`. Garde 3 tours,
  0,01 $ et `joué <fiche> · <arguments>` : les 10 tests d'aujourd'hui les lisent (test-boucle.py:84-117).
- Limite (que `NUI1` ne provoque pas) : son texte pris à la page d'erreurs nommée plus haut, sur une ligne
  `# forme déduite, <lien> (lu le <date>)` ; ce qu'elle ne fixe pas (`subtype`, code) : `is_error` vrai,
  code 1, marqués de même. Ni `NUI1` ni la page ne donnent le texte : RETOUR.
- test-boucle.py : les 10 tests inchangés (`projet()` n'écrit plus le faux), plus un test direct du faux par
  rôle et par pilote, en dossier temporaire, dont « jouer coche dans le fichier courant » (découper `T` puis
  jouer `T1` : `## T1 [x]` dans `T.md`, `fiches.md` intact) et « faux : prompt inconnu → code 2 »
  (`[sys.executable, faux, "-p", "bonjour"]` : code 2, une ligne sur stderr, stdout vide). test-vlp.py, juste
  avant `tester_mutant()` (l.5448) : un `verifier` qui lance test-boucle.py par `sys.executable`, exige `OK`,
  et passe stdout + stderr en `sortie` pour que son `ÉCART:` remonte dans `vlp.py mutant` (vlp.py:5610).
Tu ne touches pas boucle.py (rôles, plafonds, carnet : `NUI3`, `NUI4`) ; le faux n'appelle jamais Git.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` → `OK`, tests d'avant (10) et nouveaux comptés ; `py -3 scripts/test-vlp.py`
   → `OK` ; durées brutes des deux, avant et après, mesurées par toi. `grep -c "^FAUX = " scripts/test-boucle.py` → 0 (1 avant).
2. Mutant sans `--test`, preuve que test-vlp.py lance test-boucle.py : `py -3 scripts/vlp.py mutant
   scripts/boucle.py 'cmd += ["--effort", a.effort]' 'pass'` → `MUTANT ATTRAPÉ`, avec dans sa sortie la
   ligne `ÉCART: --effort low transmis tel quel à claude`.
3. `py -3 scripts/vlp.py mutant scripts/faux-claude.py <avant> <après> --test "py -3 scripts/test-boucle.py"`,
   `<après>` faisant sortir 0 un prompt inconnu → `MUTANT ATTRAPÉ`, « faux : prompt inconnu → code 2 »
   tombé ; les deux chaînes exactes recopiées au rapport.
4. pyright : 0 erreur sur les trois fichiers touchés, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:NUI3 -->
## NUI3 [x] — Tenir le carnet et la borne double

**Session** : d4efca2e-77f5-426f-a1e1-e528bce64e4b
**Dépend de** : `NUI2`.
**Fichiers** : `scripts/carnet.py` (neuf), `scripts/boucle.py`, `scripts/vlp.py`, `scripts/test-boucle.py`,
`scripts/test-vlp.py`, `scripts/faux-claude.py` (lu, pas modifié) — et rien d'autre.

**Prompt**
Crée `scripts/carnet.py`, sans dépendance ni appel modèle ; vlp.py et boucle.py le chargent par `import carnet`.
- Chemin : `--git-common-dir` absolu (l'appel de `retard_plugin`, vlp.py:1173), puis `vlp-nuit/<date>.jsonl`.
- `CLES` : les 17 du socle, `usd_kit`, `tours_kit`, `note`, `stop` ; clé inconnue refusée, absente écrite `null` ;
  à la lecture, une ligne illisible (processus tué en pleine écriture) est sautée.
- Ajout sous verrou `<carnet>.verrou` qui porte le PID, créé en `O_CREAT|O_EXCL` (`tampon_neuf`, vlp.py:473).
  Verrou tenu : attendre un pas court, réessayer ; plus vieux que 30 s (une constante, seul endroit du nombre ;
  âge = date du fichier) : cassé, et une ligne `garde` le dit (PID, âge).
- `stop(carnet, canal, raison)` écrit la ligne `stop` : l'écrivain de `NUI4` et de l'utilisateur.
- `est_session(ligne)` : `role` posé, `note` et `stop` nuls — seul tri des lignes de session (pot, `NUI8`, `NUI11`, `NUI19`).
- Pot : somme des `usd_cli` des lignes `est_session`, des deux canaux ; un chantier compte dès sa première ligne.
  Borne atteinte : pot ≥ borne $, ou chantier absent du carnet qui veut partir et compte ≥ borne de chantiers.

Dans `boucle.py`, sous `--nuit` seul (sans lui rien ne change : invariant du socle) : `--canal`, `--chantier`,
`--borne-usd`, `--borne-chantiers`, `--carnet` (absolu ; défaut celui du jour, fixé au lancement : une nuit
passe minuit) ; `--plafond` (`required=True` dans `main`) devient facultatif sous `--nuit`, exigé sans lui. Avant chaque session, jamais pendant, relis le carnet : `stop` d'un canal quelconque →
`ARRÊT STOP — <raison>`, sort 1 ; borne → `ARRÊT borne atteinte — <$ ou chantiers>`, sort 0, chantier ouvert.
Après chaque session, une ligne : nuit, canal, chantier, role `jouer`, fiche, tours_cli, usd_cli, duree_s,
`session` (`session_id` de la ligne `system`/`init`, forme relevée par `NUI1`). La fille reçoit `VLP_CARNET`
et `VLP_CANAL` (de carnet.py). Docstrings à jour ; boucle.py : la borne se dépasse d'une session par canal au plus.
`vlp.py nuits noter "<texte>" [--canal C] [--stop]` : une ligne `note`, ou `stop` par `stop()`, au carnet de
`VLP_CARNET`, sinon celui du jour ; imprime `NOTÉ <chemin>` ; sans dépôt Git ni `VLP_CARNET` : `GARDE:`, sort 1.
Tu ne fais pas : issue ni modèles (`NUI4`), coût d'une session sans `result` (`NUI8`), `VLP_NUIT` ni plan
(`NUI7`, `NUI12`), reste du pot en `--max-budget-usd` (il couperait la fiche) ; ni fichier suivi, ni hook.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` rend `OK` ; chaque cas bâtit un dépôt `git init` et son carnet en dossier
   temporaire : (a) `--nuit`, 3 fiches → 3 lignes, clés = `CLES` (`usd_kit`, `tours_kit` à `null`), canal A,
   `usd_cli` du faux ; (b) lignes B pré-écrites, pot ≥ borne → rien joué, `ARRÊT borne atteinte`, sort 0 ;
   pot à moins d'une session de la borne → une fiche jouée, puis cet arrêt ; une `note` à `role` posé hors pot ; (c) 2 chantiers au carnet,
   `--borne-chantiers 2`, chantier neuf → rien joué ; (d) `stop()` pour B → le canal A rend `ARRÊT STOP`,
   sort 1 ; (e) verrou vieilli de 60 s (`os.utime`) → ligne écrite et une `garde` qui nomme le PID ; verrou
   jeune retiré par le test pendant l'attente → ligne écrite, sans `garde` ; 2 processus × 50 écritures →
   100 lignes JSON valides ; (f) sans `--nuit` : aucun `vlp-nuit`.
2. `py -3 scripts/test-vlp.py` rend `OK` (il lance test-boucle.py), dont : `nuits noter` deux fois → deux lignes
   `note` ; `--stop` → une ligne `stop` (clé `stop` = la raison, `canal`) ; `VLP_CARNET` posé → écrit là ;
   sans dépôt ni `VLP_CARNET` → `GARDE:`, sort 1.
3. Trois mutants `py -3 scripts/vlp.py mutant <fichier> <avant> <après> [--test "<cmd>"]` (avant : une seule
   occurrence), chacun `MUTANT ATTRAPÉ`, commandes exactes au compte rendu : pot filtré sur le canal courant,
   `--test "py -3 scripts/test-boucle.py"` → (b) tombe ; verrou cassé sans sa ligne `garde`, même `--test`
   → (e) tombe ; ajout de carnet.py en `"w"` au lieu de `"a"`, test par défaut → les deux notes tombent.
4. pyright : 0 erreur sur les cinq `.py` touchés, compte brut au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:NUI4 -->
## NUI4 [x] — Donner à chaque rôle ses plafonds

**Session** : 7d26b8c1-34e3-43be-bef5-0d9610438714
**Dépend de** : `NUI3`.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py`, `scripts/faux-claude.py`, `scripts/carnet.py` (lu), `scripts/vlp.py` (lu : `lire_max_turns`), `scripts/test-vlp.py` (lu), `agents/fiche.md` (lu), `agents/relecture.md` (lu), la mesure de `NUI1` (fichier nommé dans sa fiche, lu) — et rien d'autre.

**Prompt**
Sous `--nuit` (posé par `NUI3` ; absent, pose-le ici), chaque session prend ses réglages dans une table unique en tête
de `boucle.py` : les cinq rôles du socle, avec prompt, modèle, repli et effort (socle, « Modèles par rôle » : pointés,
pas recopiés), outils, `--max-turns`, `--max-budget-usd`, timeout. Sans `--nuit`, `jouer()` bâtit la commande d'aujourd'hui
(REG, `context AI/93-reglages-enchainer.md:31`). Sous `--nuit`, `main()` ne joue encore que le rôle jouer : les autres
lignes se prouvent par `jouer()` appelé depuis test-boucle.py, module chargé comme `scripts/test-vlp.py:3440-3443`.
Plafonds, la source de chacun en commentaire dans la table, telle quelle :
- tours : jouer et relance, `lire_max_turns` d'`agents/fiche.md` ; relire, d'`agents/relecture.md` (`boucle.py` charge
  `vlp.py` comme module, `scripts/test-vlp.py:29`) — jamais recopiés ; découper 150, clore 60 : non mesurés.
- $ : jouer et relance 5 (≈ 2,9 × 1,74 $, max de PAR7 en `-p`, `context AI/08-etat.md:2370-2371` ; Opus medium jamais
  mesuré) ; relire 3, clore 5 : non mesurés ; découper 20 (≈ 3 × 6,60 $ de PAR5, plafond haut : ce 6,60 $ compte du
  hors-fiche, `08-etat.md:2377`).
- timeout 60 min pour tous : 4,9 × 735 s (TAU1, `08-etat.md:2376`), 2 × 29,3 min/fiche (BTN, `context AI/92-essai-parallele.md:87`).
Prompts : jouer et relance `/vlp:tache <fiche>`, découper `/vlp:chantier <code>`, relire selon l'essai `--agent` de `NUI1`,
clore fixé par `NUI7`. Outils : jouer, relance et clore (`cloture.md:72`) gardent `AUTORISES` et `INTERDITS` (`NUI5`
retire le premier à jouer) ; découper et relire, aucun Git qui écrit. Toute session `--nuit` : un `--session-id` neuf
(`uuid`), `--permission-prompts none` (absent ou sans effet selon `NUI1` : RETOUR sans coder), le timeout à `subprocess.run`.
Une fonction classe l'issue (valeurs du socle), dans cet ordre : timeout ; coupure (aucune ligne `result`) ; plafond
(formes de `NUI1`) ; `limite`, d'usage (ci-dessous) ; pas partie (`is_error`, ou aucun message `assistant`) → ligne `STOP` ;
ratée (contrôle du rôle échoué — jouer : case vide à `cocher --verifier`) ; jouée. Les `permission_denials` ne classent
pas : leur nombre va au carnet (`garde`). Chaque session écrit sa ligne par `scripts/carnet.py` (clés du socle ;
`modeles_vus` = les `message.model` et les clés de `modelUsage`).
Limite d'usage, lue dans le texte du `result` : forme prise de la doc (https://code.claude.com/docs/en/errors, lien et date
de lecture en commentaire, « non vérifiée sur le vrai CLI : `NUI20` la confirme »). « Opus limit » : rôles Opus en
`claude-sonnet-5-5` jusqu'au reset lu dans le message (illisible : fin de nuit), bascule au carnet, session relancée une
fois ; « session limit » ou « weekly limit » : `STOP`. Au faux claude, une variable choisit le genre de limite (`opus`,
`session`, `semaine`) à côté de `VLP_FAUX_LIMITE`, un pilote rend `permission_denials` non vide ; noms en docstring.
Pas ici : relecture et commit (`NUI5`), relance sur refus (`NUI6`), enchaînement (`NUI7`).

**Critère de fin**
1. `py -3 scripts/test-boucle.py` : `OK`, cas comptés avant/après, dont : (a) sans `--nuit`, ni `--max-turns`, ni
   `--session-id`, ni `--permission-prompts`, ni `--fallback-model`, tests d'avant intacts ; (b) `--nuit`, jouer :
   `--model,claude-sonnet-5-5`, `--effort,low`, `--max-budget-usd,5`, `--permission-prompts,none`, `--max-turns` =
   `lire_max_turns` d'`agents/fiche.md`, `--session-id` = clé `session` du carnet ; (c) relire, par `jouer()` du module
   chargé : `--max-turns` = `lire_max_turns` d'`agents/relecture.md` ; (d) `DORT` au-delà d'un timeout de test (variable
   nommée en docstring) → `timeout`, processus tué ; (e) sans `result` → `coupure`, forme plafond → `plafond`, `erreur` →
   `pas partie` et `STOP`, refus de permission et case cochée → `jouée` sans `STOP` ; (f) limite `opus` sur relire →
   bascule au carnet, relance, session Opus suivante en `claude-sonnet-5-5` ; limite `semaine` → `STOP`, sans bascule.
2. Mutants, `py -3 scripts/vlp.py mutant scripts/boucle.py <avant> <après> --test "py -3 scripts/test-boucle.py"` :
   la garde `--nuit` de la table retirée → un cas sans `--nuit` tombe (`test-boucle.py:93` ou (a)) ; l'issue timeout
   rendue `coupure` → (d) tombe.
3. `py -3 scripts/test-vlp.py` : `OK` ; pyright 0 erreur sur `scripts/boucle.py`, `scripts/test-boucle.py`, `scripts/faux-claude.py`.
<!-- /FICHE -->

---

<!-- FICHE:NUI5 -->
## NUI5 [x] — Relire avant le commit

**Session** : 7d26b8c1-34e3-43be-bef5-0d9610438714
**Dépend de** : `NUI4`.
**Fichiers** : `scripts/boucle.py`, `scripts/vlp.py`, `scripts/test-boucle.py`, `scripts/test-vlp.py`, `scripts/faux-claude.py` ; lus seulement : `scripts/carnet.py`, `agents/relecture.md`, `enchainement.md` — et rien d'autre.

**Prompt**
La nuit, la fiche est relue sur l'arbre non commité, et boucle.py la commite sur ACCEPTÉE (socle, « Relire avant le commit »). Ordre de jeu : la partie vlp.py et son cas de test-vlp.py d'abord, puis boucle.py — un arrêt en cours de session laisse un état testé.
Dans vlp.py :
- Relectures par canal : `VLP_CANAL`, posé par `NUI3` (nom en constante de carnet.py, chargé comme `nuits noter` le charge). Posé, `cmd_relecture` nomme ses worktrees `vlp-relecture-<canal>-…`, et `retirer_relectures` (vlp.py:1189) ne retire que ce préfixe, à ses quatre appels, `--retirer` compris : l'étape 5 d'agents/relecture.md le lance sans argument. Absent, rien ne change.
- `cocher <fichier> <fiche> --session <uuid> --role <rôle>` (exclusif de `--verifier` et `--refuser`) : ajoute `**Session** : <uuid> (<rôle>)`, fiche cochée ou non, jamais doublée ; `--role clore` l'écrit dans l'en-tête, avant le premier titre, comme `ouvrir` (vlp.py:5222-5227) — quand l'écrire : `NUI7`. `SESSION` (vlp.py:422) ne rend plus que l'id, sans suffixe : `sessions_de`, `sessions_entete` et `cout` le lisent.
Dans boucle.py, sous `--nuit` seulement (invariant du socle) :
- `jouer` : le rôle `jouer` ne reçoit plus `AUTORISES` (boucle.py:49-51) ; `INTERDITS` reste.
- Après la session, `cocher --verifier` (boucle.py:163). `CASE [x]` sans `TÊTE` : la session du rôle `relire` (table de `NUI4`), dont la commande `relecture <fiche>` part sans `--sha` (`instantane`, vlp.py:1201). Premier mot de son `result` lu contre `VERDICTS`, importé de vlp.py : plus aucune de ces chaînes recopiée. `STATUTS` n'est pas importé : aucun rôle n'est classé ici par son statut (`NUI4` classe jouer par la case). Aucun verdict vaut `REFUSÉE` (enchainement.md:38).
- `ACCEPTÉE` : `cocher --session <uuid du relire> --role relire`, puis `git add -A` et `git commit -m "<fiche> : <titre>"` (sujet de `COMMIT_FICHE`, vlp.py:2342 ; titre lu par `extraire`). Commit refusé (pre-commit, code non nul) → `ARRÊT`, code 1.
- `REFUSÉE` : la ligne `Erreur :` d'avant lue par `extraire`, puis `cocher --refuser "<première ligne du result>"` et `cocher --session` ; arbre laissé tel quel ; `ARRÊT`, code 1. Tu rends à `NUI6` : `refus_n` lu sur `REFUSÉ <fiche> · refus <n>` (vlp.py:1137) ; `cause` = le mot entre `REFUSÉE — ` et ` :` (enchainement.md:34-35), `aucun-verdict` sans verdict ; la ligne `Erreur :` d'avant. La relance est `NUI6`.
- `TÊTE` (la session a commité malgré tout) : relecture `--sha HEAD`. `REFUSÉE` : `git revert --no-edit HEAD` d'abord, puis les deux `cocher` (un `cocher` avant laisserait le fichier de fiches modifié et ferait échouer le revert). `ACCEPTÉE` : `cocher --session`, puis boucle.py commite cette ligne seule, sujet `<fiche> : session de relecture`.
- Chaque issue au carnet par `scripts/carnet.py` (`NUI3`) : la ligne du rôle `relire`, `refus_n` et `cause` sur un refus, `garde` sur un commit refusé ou une `TÊTE`. Le coût du relecteur entre au `TOTAL`.
- Docstrings de `cocher`, `relecture` et de boucle.py à jour.
`faux-claude.py`, rôle `jouer` : pose `CLAUDE_CODE_SESSION_ID` = son `--session-id` autour de `vlp.py cocher` (le vrai claude le pose à ses commandes ; `cocher` le lit, vlp.py:1094) ; un réglage d'environnement de plus où il commite sa fiche — sa docstring perd « n'appelle jamais Git ».
Pas ici : la prose de `/vlp:tache` (`NUI14`), la relance (`NUI6`), agents/relecture.md.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK`, avec « relecture : canaux » : `relecture X1` sous A puis sous B, les worktrees d'A restent ; `--retirer` sous B → `RETIRÉ 2`, ceux d'A toujours là ; `cocher --session` deux fois → une ligne ; `--role clore` → `sessions_entete` voit l'id ; `sessions` rend l'id sans suffixe.
2. `py -3 scripts/test-boucle.py` → `OK`. Les cas sans `--nuit` passent inchangés. Cas `--nuit` : dépôt temporaire avec un commit initial, identité et config globale neutralisées comme test-vlp.py:3099-3121, traces dans un second dossier temporaire hors du dépôt :
   - « nuit : jouer sans git » : ni `git add` ni `git commit` dans les `--allowedTools` du rôle `jouer` ;
   - « nuit : canal » : le faux du rôle `relire` voit `VLP_CANAL` égal au canal de la boucle ;
   - « nuit : ACCEPTÉE commite » : `git log -1 --format=%s` = `F1 : fiche F1`, arbre propre, `git show --name-only --format= HEAD` = les seuls fichiers de la fiche (fiches.md et ce que le faux écrit) ; F1 porte deux lignes `**Session**` : le `--session-id` de jouer, puis celui de relire suffixé `(relire)` ;
   - « nuit : REFUSÉE » : aucun commit neuf, bloc `**Tentatives**` sous F1, `ARRÊT`, code 1 ; au carnet, la ligne `relire` porte `refus_n` 1 et la `cause` du faux ;
   - « nuit : pre-commit refuse » (hook `.git/hooks/pre-commit` du dépôt temporaire qui sort 1) : `ARRÊT`, code 1, `garde` au carnet ;
   - « nuit : TÊTE » : le prompt du rôle `relire` porte `--sha` ; sur `REFUSÉE`, dernier sujet `Revert "F1 : fiche F1"` et bloc `**Tentatives**` sous F1.
3. Mutants, fichier rendu à l'octet, chaînes exactes au compte rendu :
   - `py -3 scripts/vlp.py mutant scripts/vlp.py <préfixe du canal dans retirer_relectures> <RELECTURE seul>` → « relecture : canaux » tombe ;
   - `py -3 scripts/vlp.py mutant scripts/boucle.py <AUTORISES retiré sous --nuit> <AUTORISES gardé> --test "py -3 scripts/test-boucle.py"` → « nuit : jouer sans git » tombe ;
   - même commande, `<avant>` la condition du commit sur `ACCEPTÉE`, `<après>` la même vraie aussi sur `REFUSÉE` → « nuit : REFUSÉE » tombe.
4. `grep -cE "['\"](ACCEPTÉE|REFUSÉE|FAITE|RETOUR|BLOQUÉE)" scripts/boucle.py` → `0` (0 aujourd'hui aussi), et `grep -c "VERDICTS" scripts/boucle.py` → au moins 1.
5. pyright : 0 erreur sur les cinq fichiers modifiés, compte brut écrit.
<!-- /FICHE -->

---

<!-- FICHE:NUI6 -->
## NUI6 [x] — Relancer plus fort sur refus, ou arrêter tôt

**Session** : 7d26b8c1-34e3-43be-bef5-0d9610438714
**Dépend de** : `NUI5`.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py`, `scripts/faux-claude.py`, `scripts/vlp.py` (une constante hissée, rien d'autre) ; lus seulement : `scripts/carnet.py`, `skills/tache/SKILL.md` (l. 136-137), `enchainement.md` (l. 21-23 et 38-46) — et rien d'autre.

**Prompt**
Sous `--nuit` seulement (invariant du socle : sans `--nuit`, boucle.py ne change pas), tu apprends à boucle.py quoi faire d'un refus, et quand arrêter un chantier sans humain. Décisions : TODO n° 72 (Q2 du 2e tour) ; ID et effort de la relance : socle, « Modèles par rôle ».
- Avant tout code, ouvre la table des rôles de `NUI4` : pas de ligne `relance` → `RETOUR` en nommant `NUI4` ; n'invente pas cette ligne.
- vlp.py : la chaîne `FAITE refusée à la relecture.`, locale à `refuser` (vlp.py:1112), devient une constante de module près de `VERDICTS` (vlp.py:1850) ; `refuser` s'en sert, boucle.py l'importe. Pas de copie de la chaîne dans boucle.py.
- Le compte et le motif ne se relisent pas dans le fichier de fiches après une session : la relance joue `/vlp:tache`, qui coche avec `--resolu` une fiche à bloc Tentatives (SKILL.md:136-137), et `cocher --resolu` remplace tout le bloc (vlp.py:1092) ; `refus <n>` retomberait à 1, la ligne `Erreur :` aurait disparu. boucle.py tient donc lui-même, par fiche : n refus et dernier motif. Départ lu par `extraire` avant la première session de la fiche : n = lignes numérotées égales à la constante, motif = la ligne `Erreur :` du bloc.
- `REFUSÉE` rendu par la relecture de `NUI5` (aucun verdict vaut `REFUSÉE`, enchainement.md:38) : n augmente ; `cocher <fichier> <fiche> --refuser "<motif>"` reste appelé, pour la trace seulement ; cause lue sur la ligne du verdict, `fiche` ou `copie` (enchainement.md:41-46).
- Gardes, dans cet ordre : motif égal au dernier motif tenu → `meme-erreur` (le carnet dit alors que la relance n'a rien changé) ; n ≥ la constante de boucle.py (2, là seulement) → `refus-max` ; cause `fiche` → `cause-fiche`, la ligne `RÉÉCRITURE :` du verdict au carnet (clé `reecriture`) ; aucun verdict → `sans-cause`, `cause` vaut `aucune` au carnet ; cause `copie` → une session du rôle `relance` sur l'arbre tel quel (rien de commité, aucun revert), puis la même chaîne que `NUI5`.
- Un bloc Tentatives fait de refus seuls (lignes numérotées toutes égales à la constante) n'arrête plus la boucle (enchainement.md:21-23) ; tout autre bloc arrête, comme boucle.py:153-155.
- Vérification de nuit : la valeur du libellé de CHANTIER.md (socle, « noms retenus »), lue par `champ` (vlp.py:3136) importé de vlp.py ; lancée par le shell dans la racine du projet, avant la première fiche jouée du chantier et après le commit de chaque `ACCEPTÉE`, bornée par le timeout de `NUI4` ; code ≠ 0 → garde `verification` ; libellé absent → rien, ni GARDE ni ligne.
- Chaque arrêt : une ligne `ARRÊT` qui nomme la fiche et sa garde, sortie 1, et une ligne au carnet (`garde`, `refus_n`, `cause`, `reecriture`) par `scripts/carnet.py`.
- faux-claude.py, rôles `jouer` et `relance` : fiche à bloc Tentatives → `cocher --resolu`, comme SKILL.md:136, pour que le test suive le chemin réel.
Tu ne fais pas : la mise de côté (commit WIP, branche neuve, dépendants sautés : `NUI7`), `nuit.md` (`NUI13`), la table des rôles (`NUI4`). Docstring de boucle.py à jour.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` rend `OK` avec ces cas neufs, sous `--nuit` (faux claude, projet, dépôt et carnet en dossier temporaire) :
   a. F1 refusée `copie` puis acceptée → une session `relance` dont les arguments portent l'ID et l'effort du rôle `relance` ; F1 commitée ; au carnet, une ligne `role` relance, `refus_n` 1, `cause` copie.
   b. F1 refusée `fiche` avec une ligne `RÉÉCRITURE :` → aucune relance, aucun commit `F1 :`, `reecriture` = cette ligne, `ARRÊT … cause-fiche` ; F1 sans verdict → aucune relance, `ARRÊT … sans-cause`, `cause` aucune.
   c. F1 refusée `copie` deux fois, à motifs différents → exactement une relance (qui a coché `--resolu`), `cocher` rend `refus 1` au 2e refus, et pourtant `ARRÊT … refus-max` ; F2 pas jouée.
   d. F1 portant un bloc de refus seuls dont `Erreur :` égale le motif du nouveau refus, bloc remplacé par `--resolu` pendant la session → `ARRÊT … meme-erreur`, pas de relance.
   e. Vérification qui sort 1 → `ARRÊT … verification` avant F1, aucune ligne `JOUE` ; qui réussit avant F1 et échoue après son commit → arrêt après F1, F2 pas jouée ; libellé absent → F1 jouée.
   Les cas d'avant passent tels quels, dont « F1 à bloc Tentatives : rien joué, sort 1 » (test-boucle.py:116, sans `--nuit`). Compte brut : cas neufs passés / écrits.
2. Trois mutants, chacun `MUTANT ATTRAPÉ` par `py -3 scripts/vlp.py mutant scripts/boucle.py <avant> <après> --test "py -3 scripts/test-boucle.py"` : la condition de relance qui accepte aussi la cause `fiche` (cas b tombe) ; le code retour de la vérification ignoré (cas e tombe) ; le test « même Erreur » retiré (cas d tombe).
3. `py -3 scripts/test-vlp.py` : `OK` (il lance test-boucle.py depuis `NUI2` ; le cas de `refuser`, test-vlp.py:1879, inchangé) ; pyright : 0 erreur sur les fichiers touchés, compte brut écrit.
<!-- /FICHE -->

---

<!-- FICHE:NUI7 -->
## NUI7 [x] — Enchaîner les chantiers d'un canal

**Session** : 763247fd-fd16-4c79-beca-2714a79f98ad
**Dépend de** : `NUI6`, `NUI12`.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py`, `scripts/faux-claude.py` ; lus : `scripts/carnet.py`, `scripts/vlp.py` (`todo_du_fichier`, `borne_haute_cout`, `est_bloque`, `rapport`, `plan lire`), `skills/chantier/SKILL.md` (étape 6), `cloture.md` (commit de clôture), `.githooks/pre-commit` — et rien d'autre.

**Prompt**
boucle.py joue un chantier ouvert et sort sur `aucune` sans clore (boucle.py:149-151). Sous `--nuit` sans
`--chantier`, fais-en la boucle d'un canal ; sans `--nuit`, ou avec `--chantier` (`NUI3`-`NUI6`), rien ne change.
- `--date` (défaut : celle du lancement, lue une fois) nomme branches, plan et carnet par défaut ; plan lu par
  `vlp.py plan lire` (`NUI12`, sa syntaxe y vit), jamais à la main ; `VLP_NUIT=1` posé pour les filles.
- Par chantier, dans l'ordre : borne et `STOP` relus (`NUI3`), atteints → le canal s'arrête ; branche
  `nuit/<date>-<canal>-<code>` depuis le dernier réussi (socle, « Deux canaux ») ; `découper` ; `jouer` avec
  `NUI5`-`NUI6` ; sur `PROCHAINE=aucune`, `clore`, qui commite (cloture.md:72) — avant de le lancer, `cocher
  --session <uuid> --role clore` (`NUI5`), l'uuid de son `--session-id` : la ligne entre au commit, son coût
  compte. Réussi : `lire_carte` (boucle.py:72) rend un fichier `None`, arbre propre ; sa pointe est la base du
  suivant. `lire_carte` lit aussi `PLUGIN_RETARD=` : sa valeur (ou `null`) va à `plugin_retard` des lignes.
- Mis de côté si : après `découper`, fichier `None` ; ou `vlp.py valider` rend un écart, un avertissement, ou
  plus de fiches (`rapport`, vlp.py:1469) que 2 × la borne haute de sa ligne TODO (`todo_du_fichier`
  vlp.py:3223, `borne_haute_cout` 3426 ; `None` : `valider` seul juge ; `ValueError` : mis de côté) ; après
  `jouer` ou `relance`, fichier `None` (garde « clôture hors rôle ») ; un arrêt de chantier de `NUI6`, sa
  ligne `ARRÊT` imprimée telle quelle. Sinon boucle.py commite le découpage (`/vlp:chantier` ne commite pas) :
  `Chantier <code> ouvert (nuit) : <n> fiches`, hors `COMMIT_FICHE`.
- Une seule fonction de mise de côté (socle, « Mis de côté ») : `git status --porcelain` vide → pas de commit ;
  sinon `git add -A`, commit `WIP <code> mis de côté : <raison>`. Tout commit de boucle.py refusé par un hook
  → `ARRÊT` du canal, arbre tel quel, jamais `--no-verify` ; limite connue : le pre-commit du kit lance pyright
  (.githooks/pre-commit:8-13), une fiche de code cassée y arrête le canal. Le suivant part du dernier réussi ;
  un chantier dont « Dépend de » (TODO, cellule 5) nomme un code mis de côté ou sauté (motif de `est_bloque`,
  vlp.py:3436) est sauté, sans session.
- Carnet par `carnet.py`, clés du socle : `garde` = `mis-de-cote:<raison>`, `saute:<code>`, `cloture-hors-role`,
  `wip-refuse` ; sauté : `issue` `pas partie` ; la branche se déduit de `nuit canal chantier`.
Tu ne fusionnes rien, ne crées aucun worktree (`NUI9`), ne touches ni vlp.py ni la prose (`NUI13`, `NUI14`). Pilotes absents de `NUI2` (`clore` qui commite, fiche qui clôt, découpage vide, `VLP_NUIT` recopié) : faux-claude.py.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` → `OK`, cas d'avant inchangés (compte brut avant/après) ; chaque cas neuf
   bâtit dépôt Git, plan et carnet en dossier temporaire :
   a. trois chantiers réussis : 3 branches à la `--date`, chacune ancêtre de la suivante (`git merge-base
      --is-ancestor`), 3 sessions `clore`, chacune sa ligne `**Session** … (clore)` commitée, 3 commits `Chantier
      … ouvert (nuit)`, `VLP_NUIT=1` vu par le faux (absent sans `--nuit`), `plugin_retard` = la carte ;
   b. `VLP_FAUX_REFUSE=<1re fiche du 1er>:fiche` : `WIP` sur sa branche, le 2e (qui en dépend) sauté sans
      session, le 3e part de la base et non du `WIP`, chaque étape au carnet ;
   c. une fiche qui clôt → carnet `cloture-hors-role`, `WIP` sur sa branche, pas de `clore` ;
   d. TODO à `~0,5 fiche`, le faux en écrit 2 → mis de côté sans `jouer` ; découpage vide → sans `WIP`, suivant joué ;
   e. cas b sous un pre-commit (`core.hooksPath`) qui sort 1 si la fiche refusée a indexé `CASSE` → `ARRÊT`,
      arbre intact, carnet `wip-refuse`.
2. Mutants `py -3 scripts/vlp.py mutant scripts/boucle.py <avant> <après> --test "py -3 scripts/test-boucle.py"`
   → `MUTANT ATTRAPÉ`, chaînes au rapport : base de branche → `HEAD` (b tombe) ; mise de côté de la garde
   « clôture hors rôle » retirée (c tombe).
3. `py -3 scripts/test-vlp.py` → `OK`, durée brute ; pyright : 0 erreur sur les trois fichiers touchés, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:NUI8 -->
## NUI8 [x] — Reprendre une nuit coupée

**Session** : 28c4a1ca-ce9e-4c0a-9a6e-a5edbd860a0c
**Dépend de** : `NUI7`.
**Fichiers** : `scripts/boucle.py`, `scripts/carnet.py`, `scripts/test-boucle.py`, `scripts/faux-claude.py` ; lus seulement :
`scripts/mesure-tokens.py` (`GRILLE` l.66, `resoudre` l.94, `mesurer` l.220), `scripts/vlp.py` (`mesure` l.2171) — et rien d'autre.

**Prompt**
Une nuit se coupe : session tuée (timeout de `NUI4`), terminal fermé, veille, redémarrage. Tu fais que rien ne s'y perde,
sous `--nuit` seulement (invariant du socle). Mise de côté, branche du chantier : fonctions de `NUI7`, appelées, pas refaites.
1. Session sans ligne `result` (issues `timeout`, `coupure` de `NUI4`) : l'issue tient à l'absence de `result`, jamais au
   code de sortie (143 sous POSIX, 1 sous win32 par `TerminateProcess` : la forme relevée par `NUI1` fait foi). Son id est
   celui de `--session-id` ; boucle.py la mesure par `mesure()`, `resoudre(<id>)`, `mesurer` : `usd_kit`, `tours_kit` sur
   sa ligne, `usd_cli`, `tours_cli` à `null`, jamais 0. Transcription introuvable : `garde` le dit. Puis mise de côté.
2. Le pot de carnet.py somme, sur les lignes `est_session` (`NUI3`), `usd_cli`, à défaut `usd_kit`, à défaut le
   `--max-budget-usd` du rôle, passé par boucle.py depuis la table de `NUI4` — le nombre n'est pas recopié.
3. Avant chaque session, une `note` (`NUI3`) `depart` : canal, chantier, rôle, fiche, session — hors `est_session`, donc
   hors pot et hors mesure. Un `depart` sans ligne `est_session` au même id est une session coupée.
4. `--reprendre` (avec `--nuit`, `--canal`, `--carnet` ; la date vient du nom du carnet, jamais de l'horloge), dans l'ordre :
   (a) chaque `depart` sans fin reçoit sa ligne `coupure`, coût relu comme en 1 ; (b) le chantier en cours du canal (plan
   de `NUI12`, ni clos ni mis de côté au carnet) : session coupée ou arbre sale → mis de côté, jamais commité en fiche ;
   sinon il reprend dans sa branche `nuit/…` (jamais recréée), sans repasser par `découper` s'il est découpé ; (c) la
   boucle de `NUI7` continue. Worktree du canal absent : `GARDE:`, sort 1.
5. Éveil, sous `sys.platform == "win32"` seulement : `SetThreadExecutionState` par `ctypes`, `ES_CONTINUOUS |
   ES_SYSTEM_REQUIRED` au départ, `ES_CONTINUOUS` à la fin ; constantes nommées, valeurs et lien daté de la doc Microsoft
   en commentaire. Retour 0 : `ÉVEIL non tenu` et une `note` ; sinon `ÉVEIL tenu`.
Faux claude, mode `COUPE` (variables dans sa docstring, code de sortie compris) : `system/init`, une transcription
`~/.claude/projects/<x>/<id>.jsonl` de deux lignes `assistant` à `message.id` distincts, `message.model` dans `GRILLE`,
`message.usage` à la forme relevée par `NUI1` ; aucune ligne `result`.
Tu ne fais pas : relancer une session coupée, `NUI9`, `nuit.md` (`NUI13`), détecter un canal encore vivant (une reprise
suit un terminal fermé : la docstring le dit), l'essai `powercfg /requests` (droits d'administrateur : il revient à
`NUI20`). Docstrings de boucle.py et carnet.py à jour.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` rend `OK` ; chaque cas bâtit projet, dépôt `git init`, carnet et `~` (`HOME`,
   `USERPROFILE`) dans un dossier temporaire, avec les quatre variables d'identité Git de test-vlp.py:654 :
   a. `--nuit`, F1 en `COUPE` → issue `coupure`, `usd_cli` null, `usd_kit` et `tours_kit` égaux à ce que rend
      `mesure-tokens.py <id>` lancé par le test (tours 2), pot = `usd_kit` ; chantier mis de côté, F2 pas jouée.
   b. `COUPE` sans transcription → `garde` qui le dit ; pot = `--max-budget-usd` du rôle jouer.
   c. `COUPE` sortie 143, puis sortie 1 → même issue `coupure` les deux fois.
   d. un `depart` sans fin, branche créée, arbre sale → `--reprendre` : une ligne `coupure`, commit `WIP`, chantier suivant
      joué ; 2e `--reprendre` : carnet et `git branch --list "nuit/*"` identiques avant et après, aucune ligne `JOUE`.
   e. sans `--nuit` : `--reprendre` refusé (sort ≠ 0), aucune ligne `ÉVEIL` ; cas d'avant verts sous ce `~` déplacé.
   f. win32, `--nuit` → `ÉVEIL tenu` ; hors win32, `SAUTÉ (plateforme)`, compté à part.
   Comptes bruts : cas neufs passés / écrits, cas d'avant passés, cas sautés.
2. Trois mutants `MUTANT ATTRAPÉ` par `py -3 scripts/vlp.py mutant <fichier> <avant> <après> --test "py -3
   scripts/test-boucle.py"` : mesure sautée sans `result` (boucle.py) → (a) tombe ; `depart` fermé sans chercher sa fin
   (boucle.py) → (d) tombe ; pot sans `usd_kit` (carnet.py) → (a) tombe. Les trois commandes au compte rendu.
3. `py -3 scripts/test-vlp.py` : `OK` ; pyright : 0 erreur sur les quatre `.py` touchés, compte brut écrit.
<!-- /FICHE -->

---

<!-- FICHE:NUI9 -->
## NUI9 [x] — Lancer les deux canaux d'une ligne

**Session** : 28c4a1ca-ce9e-4c0a-9a6e-a5edbd860a0c
**Dépend de** : `NUI7`.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py` ; lus seulement : `scripts/carnet.py`, `scripts/faux-claude.py`, `scripts/vlp.py` (`cmd_relecture`, `plan lire` de `NUI12`, la fonction de `NUI11` qui trouve le fichier des nuits) — et rien d'autre.

**Prompt**
Tu donnes à l'utilisateur la ligne unique qu'il tape le soir dans un terminal (TODO n° 72, Q6 du cadrage) : `py -3 <kit>/scripts/boucle.py --nuit --lancer <projet>`. `--lancer` est le lanceur ; `--nuit` sans lui reste un canal (`NUI7`). `--plafond`, facultatif sous `--nuit` depuis `NUI3`, l'est aussi sous `--lancer` : la borne double du socle le remplace ; sans eux, il reste exigé. Canal, worktree, branches : socle, « Le socle commun ». Le lanceur, dans cet ordre, sans rien créer avant la dernière garde :
- trouve `claude` une fois par `trouver_claude` de boucle.py (qui lit `vlp.py claude`) ; introuvable → la GARDE dont le texte commence par `GARDE: claude introuvable`, sort 1 ; trouvé → passé en `--claude` aux deux canaux ;
- vérifie le projet : branche courante `main` ; arbre propre (`git status --porcelain` vide : un plan de `NUI12` non commité manquerait aux worktrees) ; fichier des nuits non ignoré (`git check-ignore` sur le chemin que rend la fonction de `NUI11` : ignoré, comme le contexte de Cairn, il n'est dans aucun worktree) ; aucun worktree (`worktree list`) ni branche (`branch --list "nuit/<date>-*"`) de nuit à la date ; un plan à la date (`vlp.py plan lire <projet> --date <d>`, `NUI12`). Sinon `GARDE:` qui nomme la cause, sort 1. Une nuit déjà lancée se reprend par `--reprendre` (`NUI8`), pas ici ;
- si `.claude/worktrees/` n'est pas ignoré (`git check-ignore`), l'ajoute à `info/exclude` du dépôt commun (`rev-parse --git-common-dir`), sinon le worktree d'un canal salit `git status` de `main` ; jamais `.gitignore` ni un fichier suivi ;
- crée les deux worktrees détachés sur `main` (`git worktree add --detach`, comme `cmd_relecture` de vlp.py) ; les branches par chantier restent à boucle.py de canal (`NUI7`) ;
- fixe la date une fois, puis lance deux processus `boucle.py --nuit --canal A|B <worktree>` (`subprocess.Popen`, `sys.executable -u`), sans attendre l'un avant l'autre, avec le même `--carnet`, le même `--claude`, et la ligne de borne de `plan lire`, lue une seule fois, en `--borne-usd` et `--borne-chantiers` (`NUI3`) ; une autre option qu'exigent `NUI3`, `NUI7` ou `NUI8` et que tu ne trouves pas : dis-le au compte rendu, ne l'invente pas ; traces de chaque canal par `--traces`, dans le dossier du carnet (hors Git) ;
- imprime `DÉPART <canal> · pid <n> · <worktree>` pour chacun, puis chaque ligne des deux filles préfixée `[A] ` ou `[B] ` dans ce seul terminal (un fil de lecture par fille, stdlib, UTF-8) ; `FIN <canal> · code <n>` dès que cette fille sort, par son fil ; quand les deux sont sorties, `RIEN FUSIONNÉ, RIEN POUSSÉ — /vlp:chef le matin` ; sort 0 si les deux sortent 0, 1 sinon ;
- Ctrl+C : `terminate()` aux deux filles, sort 1 ; la reprise est à `NUI8`.
Seules commandes Git du lanceur : `branch --show-current` et `branch --list`, `status`, `check-ignore`, `rev-parse`, `worktree add` et `list`. Ni merge, ni push, ni commit, ni checkout (invariants du socle). Docstring de boucle.py à jour : la ligne de lancement, et qu'un projet dont le fichier des nuits est ignoré par Git ne se lance pas.
Tu ne fais pas : le plan (`NUI12`), la boucle d'un canal (`NUI7`), la reprise et le maintien éveillé (`NUI8`), la fusion (`NUI15`), la ligne écrite par `/vlp:chef` (`NUI18`) ; aucun hook, aucune ligne de CLAUDE.md.

**Critère de fin**
1. `py -3 scripts/test-boucle.py` rend `OK`. Chaque cas bâtit en dossier temporaire un dépôt `git init` sur `main`, un dépôt nu `origin` poussé une fois par le test, le projet et le plan commité du bout en bout de `NUI7`, et passe le faux claude par `--claude` :
   a. `--lancer`, plan à deux chantiers en A et un en B, `VLP_FAUX_DORT=1` (`NUI2`) → `DÉPART A` et `DÉPART B` avant toute ligne `FIN` ; des lignes `[B] ` et `FIN B` avant `FIN A` ; `git worktree list` porte les deux `nuit-<date>-A` et `-B` ; un seul carnet, avec des lignes canal A et canal B ; sha de `main` et `git ls-remote origin` identiques avant et après ; `git status --porcelain` du projet vide ; sort 0.
   b. relancé à la même date → `GARDE:`, aucun worktree de plus, carnet inchangé.
   c. un fichier non commité → `GARDE:`, aucun worktree ; fichier des nuits ignoré (`.gitignore` du dépôt temporaire) → `GARDE:`, aucun worktree ; pas de plan à la date → `GARDE:`, aucun worktree.
   d. `claude` introuvable (`VLP_CLAUDE` ôtée, `PATH` réduit au dossier de Python, `LOCALAPPDATA` et `APPDATA` vers un dossier vide) → la GARDE `GARDE: claude introuvable`, aucun worktree.
   e. sans `--lancer` ni `--nuit`, `--plafond` absent → refusé par argparse (sort 2) ; les cas d'avant passent tels quels.
   Compte brut au compte rendu : cas neufs passés / écrits.
2. Deux mutants, chacun `MUTANT ATTRAPÉ` par `py -3 scripts/vlp.py mutant scripts/boucle.py <avant> <après> --test "py -3 scripts/test-boucle.py"` : le canal A attendu (`wait`) avant le `Popen` de B → (a) tombe ; la garde d'arbre propre retirée → (c) tombe. Les deux commandes exactes au compte rendu.
3. `py -3 scripts/test-vlp.py` : `OK` ; pyright : 0 erreur sur les fichiers touchés, compte brut écrit.
<!-- /FICHE -->

---

<!-- FICHE:NUI10 -->
## NUI10 [x] — Trier les chantiers prêts

**Session** : 763247fd-fd16-4c79-beca-2714a79f98ad
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` ; lu : `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Ajoute à `vlp.py` la sous-commande `trier <projet>` : le tri du soir par script, « un script d'abord »
(TODO n° 72, socle). Lecture seule, zéro appel modèle. Lis la TODO comme `feuille` (vlp.py:3367) :
`champ(…, "fichier d'état")`, `lignes_du_projet`, `todo_du_fichier` (3223) ; les codes clos par
`lettres_prises` (3152). Une `ValueError` → `GARDE:`, sort 1, comme `cmd_feuille` (3652-3654). Le code d'une
ligne : le premier code entre backticks de sa cellule 2, sinon son rang. Par rang, dans l'ordre :
- `PRÊT <code>`, ou `ÉCARTÉE <code> — <raison>` : la marque visuelle ou `push` en cellule 3-4, ou une
  dépendance non close selon `est_bloque` (3436). Une PRÊTE du même soir compte comme close — son code
  rejoint les clos, son rang sort des rangs présents — et on recommence jusqu'à ce que plus rien ne bouge.
- `FICHIERS <code> <chemins>` : dans chaque backtick des cellules 3-4, les mots (`shlex.split`, guillemets
  retirés ; repli `split`) qui finissent en `.py .md .html .json .css .js` — `vlp.py archive` donne `vlp.py`.
- `MARQUES <code> <total> : 🟡 <n> · à trancher <n> · non mesuré <n> · <marque visuelle> <n> · push <n>` :
  sous-chaînes comptées en cellules 3-4, sans chercher le sens ; liste fermée, constante unique relue par
  l'ÉCARTÉE. La marque visuelle (le mot visuel entre parenthèses) devient sa propre constante, dont se servent
  `CRITERE_VISUEL` (1352) et `valider_lignes` (1438) ; `ARRET` (1353) reste du texte affiché.
- `SOIR <code> — <raison>`, PRÊTE à découper le soir : `borne_haute_cout` (3426) au-delà du seuil « gros » de
  `decompte_todo` (3451), constante lue par les deux ; `None` ; « à cadrer » en cellule 3-4. `½` s'y lit 0,5.
- Enfin, par groupe de PRÊTES liées : `CANAL <k> : <codes> — <raisons>` ; lien par dépendance d'abord, sinon
  par un fichier commun comparé sur son nom (`vlp.py` = `scripts/vlp.py`) ; une PRÊTE sans lien :
  `inconnu → à la page`. Le script groupe ; A ou B se choisit à la page du soir (`NUI18`).
Docstrings à jour : la liste des sous-commandes (près de `feuille`, vlp.py:166), `borne_haute_cout`. Tu ne fais
pas : TAUX, Leçons, `CARNET_MIN`, `LECONS_MAX` (`NUI11`), le plan (`NUI12`), la page (`NUI17`, `NUI18`). Avec `½`,
le décompte de la feuille du kit bouge : `feuille . --verifier` dit écart jusqu'à la clôture de NUI (`cmd_clore`
écrit la feuille, vlp.py:5056) — attendu ; ne la régénère pas, dis-le au compte rendu.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` rend `OK`, dont `tester_trier` (neuf, patron `tester_barre_todo`, test-vlp.py:4823 :
   CHANTIER.md et TODO en dossier temporaire, `appel(["trier", tp])`) : `AAA` cite `scripts/vlp.py` → `PRÊT` ;
   `BBB` cite `vlp.py archive`, dépend d'un clos → `PRÊT`, `FICHIERS BBB vlp.py` ; `CCC` dépend de `AAA`, `JJJ`
   du rang de `AAA` (numéro nu) → `PRÊT` ; une ligne `CANAL` groupe `AAA, BBB, CCC, JJJ`, nomme `vlp.py` et la
   dépendance ; `DDD` porte les cinq marques (la visuelle en cellule 3) → `ÉCARTÉE`,
   `MARQUES DDD 5 : 🟡 1 · à trancher 1 · non mesuré 1 · <marque visuelle> 1 · push 1` ; `FFF`, `push` en
   cellule 4 → `ÉCARTÉE` ; `GGG` dépend de `ZZZ` absent → `ÉCARTÉE` ; `HHH` `~6 fiches`, cite `py "dossier x/m.py"`
   → `SOIR`, `FICHIERS HHH dossier x/m.py`, `inconnu → à la page` ; `III` `~½ fiche` → sans `SOIR` ; une barre
   non échappée → `GARDE:`, sort 1. Le cas FEU8 de `borne_haute_cout` (test-vlp.py:4750) gagne `~½ fiche` → 0,5.
2. Quatre mutants `py -3 scripts/vlp.py mutant scripts/vlp.py "<avant>" "<après>"` (défaut test-vlp.py), chacun
   `MUTANT ATTRAPÉ`, commande exacte au compte rendu : cellule 3 retirée du compte des marques → `MARQUES DDD`
   tombe ; codes prêts non comptés clos → `CCC` tombe ; rang prêt gardé présent → `JJJ` tombe ; fichiers comparés
   sur le chemin entier → le `CANAL` tombe.
3. `py -3 scripts/vlp.py trier .` sur le kit : sort 0, un `PRÊT` ou `ÉCARTÉE` par rang de la TODO (comptes bruts
   au compte rendu) ; si `TAB`, `CLV` et `CAR` y sont : même `CANAL`, par `vlp.py` ; `APR` : `FICHIERS APR
   context AI/99-jnt1-mesure.py`, sans `SOIR`.
4. pyright : 0 erreur sur `scripts/vlp.py` et `scripts/test-vlp.py`, compte brut au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:NUI11 -->
## NUI11 [x] — Tenir le fichier des nuits

**Session** : 763247fd-fd16-4c79-beca-2714a79f98ad
**Dépend de** : `NUI3`, `NUI10`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `methode-chantier.md`, `scripts/carnet.py` (lu)
— et rien d'autre.

**Prompt**
Tu donnes au projet le fichier des nuits du socle : création, forme, écriture, lecture ; `trier` (`NUI10`) en imprime
les Leçons et le TAUX. Tout dans `scripts/vlp.py`, sans dépendance (`statistics.median`), aucune sous-commande neuve.
- `fichier_nuits(projet, creer=False)` : le `*-nuits.md` du `contexte`, lu comme `page_feuille` (vlp.py:3504) ;
  deux → `ValueError`. Absent et `creer` : premier numéro libre (methode-chantier.md, « Numérotation »), écrit
  depuis `NUITS_TETE`, ligne d'index sous le plus grand numéro lu en entier (`numero_ligne`, vlp.py:545, n'en lit
  que deux chiffres), sans `**clos**` (`archiver` la déplacerait, vlp.py:556) ni `**ouvert**`. Relancé : rien.
- `NUITS_TETE`, comme `ARCHIVE_TETE` (vlp.py:539) : QUAND LIRE ; la table `| nuit | canal | chantier |
  jouées/acceptées/refusées | $ |` ($ : somme des `usd_kit`) ; `## Leçons` et la forme d'une leçon, écrite là
  seul (`NUI19` y renvoie) : `- <date> · N=<n> · <une cause, pas un constat> · <nombres nommés> · nuits <dates>
  · sessions <ids>` ; N sous `LECON_INDICE` : « indice » ; retirée, elle reste, suffixée `— retirée le <date>
  par <chantier ou nuit>` (methode-chantier.md:44) ; tenue deux nuits, proposée au matin, deux oui : elle monte.
- `nuits_du_fichier(lignes)` : ≠ 5 cellules ou hors forme → `ValueError` nommée (`todo_du_fichier`, vlp.py:3223).
- `nuits_ecrire(chemin, ligne)` (ligne de table ou leçon, à sa section) et `nuits_retirer(chemin, lecon, date,
  par)` (le suffixe) vérifient par `nuits_du_fichier` avant d'écrire ; déjà là → rien. `NUI19` les appelle.
- `trier` imprime `## Leçons` par `imprimer_section` (vlp.py:659), `indice` accolé aux vivantes sous
  `LECON_INDICE` ; plus de `LECONS_MAX` vivantes, ou un `ValueError` de lecture → `GARDE:` qui le nomme, tri
  imprimé, sort 1. Puis, sans ratio ni estimé corrigé (Dehors du socle) : `TAUX jour <X> $/fiche sur <K>
  clos` — la division de `cmd_ouvrir` (vlp.py:5248) sur `moyenne_clos` (vlp.py:5097), sortie en une fonction
  qu'`ouvrir` appelle aussi ; `TAUX nuit médiane <Y> $/fiche sur <n> fiches acceptées` — une fiche = (nuit,
  chantier, fiche), somme des `usd_kit` de ses lignes `est_session` (`NUI3`), sur tous les carnets lus par carnet.py
  (chargé comme `mesure()`, vlp.py:2171) ; acceptée : une ligne `relire` à `refus_n` nul (`NUI5` ne l'écrit que
  sur un refus). Sous `CARNET_MIN` : `TAUX nuit indice — <n> fiches acceptées`, sans chiffre. Ligne sans
  `usd_kit` : comptée à part, `sans usd_kit <m>` ; jamais `usd_cli`.
Constantes, seul endroit des nombres : `LECON_INDICE` 3, `LECONS_MAX` 12, `CARNET_MIN` 5. methode-chantier.md,
« Où vit quoi » : une ligne pour `<contexte>/NN-nuits.md`, titre à sept familles. Pas ici : `NUI12`, `NUI19`.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` rend `OK`, dont, projet, dépôt `git init` et carnet en dossier temporaire :
   (a) contexte à `00`, `08`, `100` → `fichier_nuits(p, True)` rend `101-nuits.md`, index sous `100` ; relancé :
   même chemin, index inchangé ; `archiver` ne la déplace pas ; (b) `nuits_ecrire` deux fois → une ligne ;
   `nuits_retirer` → suffixe, leçon gardée ; N=2 → `indice` ; 12 vivantes + 1 retirée → pas de `GARDE` ;
   13 vivantes → `GARDE:`, sort 1 ; leçon hors forme → `GARDE:` qui la cite ; (c) TAUX jour = l'estimé par fiche
   d'`ouvrir` sur la même feuille ; 4 fiches acceptées → `indice` ; 5 fiches, chacune une ligne `jouer` et une
   `relire` (l'une aussi `relance`), sommes `usd_kit` 1, 2, 3, 4, 10, parts `jouer` d'une autre médiane,
   `usd_cli` tous autres → `médiane 3` ; une fiche refusée deux fois hors compte ; une ligne sans `usd_kit` →
   `sans usd_kit 1` ; (d) une ligne de table à 6 cellules → `ValueError`.
2. Trois mutants `MUTANT ATTRAPÉ`, défaut test-vlp.py, commandes exactes au compte rendu :
   `py -3 scripts/vlp.py mutant scripts/vlp.py "CARNET_MIN = 5" "CARNET_MIN = 0"` → (c) « 4 → indice » tombe ;
   retirées comptées vivantes → (b) « 12 + 1 » tombe ; `usd_kit` lu en `usd_cli` → (c) médiane tombe.
3. `grep -c "nuits.md" methode-chantier.md` : 0 avant, 1 après ; `grep -c "sept familles" methode-chantier.md` : 1.
4. pyright : 0 erreur sur `scripts/vlp.py` et `scripts/test-vlp.py`, compte brut au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:NUI12 -->
## NUI12 [x] — Écrire le plan de nuit

**Session** : 763247fd-fd16-4c79-beca-2714a79f98ad
**Dépend de** : `NUI11`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Le soir, les réponses de l'utilisateur deviennent un plan que la nuit relit sans rien lui demander. Écris-le par script, dans le fichier des nuits du socle, trouvé par `fichier_nuits` (`NUI11`), pas un second chemin : `plan ecrire` l'appelle avec `creer=True` (le premier soir, il n'existe pas), `plan lire` sans.
- `vlp.py plan ecrire <projet> --json <fichier> [--date AAAA-MM-JJ]` (défaut : la date du jour, lue) : le JSON
  porte la borne double du socle, puis par canal `A`, `B` la liste ordonnée des chantiers : code de la TODO,
  préfixe des fiches, réponses de cadrage (lignes libres). Il écrit la section `## Nuit <date>`, après la
  table des nuits et avant `## Leçons` : une ligne par chantier (canal, rang, code, préfixe), puis un
  `### <code>` par chantier, chaque réponse en puce `- ` (jamais un titre). Même date : la section est
  remplacée ; les autres nuits, la table et `## Leçons` restent octet pour octet.
- Tout se vérifie avant la première écriture, et un refus n'écrit rien (`GARDE:`, sort 1) : code absent de la
  TODO (`todo_du_fichier` du socle, sur le `fichier d'état` lu par `champ`, vlp.py:3136 ; le code se lit comme
  le lit `trier`, `NUI10`) ; préfixe que `PREFIXE` (vlp.py:419) ne reconnaît pas en entier (`fullmatch`, pas
  `match` : `NUIT` passerait), déjà pris (`lettres_prises`, vlp.py:3152) ou donné deux fois — deux canaux
  ouvrent chacun leur chantier sans se voir ; un chantier dans deux canaux ; canal autre que A ou B ; borne
  nulle ou absente ; une réponse à saut de ligne ; `VLP_NUIT=1` posé (refus de `ecrire` seul : la nuit
  n'écrit aucun fichier suivi ; `lire` reste permis, boucle.py le lance sous `VLP_NUIT=1`).
- `vlp.py plan lire <projet> --date <d> [--canal A|B] [--chantier <code>]` : une ligne pour la borne, puis
  une ligne par chantier du canal, dans l'ordre ; avec `--chantier`, son seul `### <code>`, par
  `imprimer_section` (vlp.py:659). Pas de fichier des nuits, ou pas de plan à cette date → `GARDE:`, sort 1.
  `--date` obligatoire : une nuit passe minuit, boucle.py passera celle du lancement.
- `carte` du socle : `VLP_NUIT` valant `1` → une ligne `NUIT=1`, dans le bloc `if not relecteur` qui suit
  `--- CHANTIER.md ---` (avec les `ATTENTE=`), donc avant `--- fiches :` ou `--- fichier de fiches courant`.
  Toute autre valeur, absente, ou `--relecteur` : rien.
- `test-vlp.py` ôte `VLP_NUIT` de l'environnement en tête, comme `CLAUDE_CODE_SESSION_ID` : une fiche jouée la nuit lance la suite sous `VLP_NUIT=1`. Docstring de vlp.py : `plan`, et `NUIT=1` dans `carte`.
Tu ne fais pas : poser `VLP_NUIT` ni lire le plan dans boucle.py (`NUI7`) ; la prose de `/vlp:chantier` et `/vlp:tache` qui lit le plan (`NUI14`) ; le commit du plan dans `main` avant le lancement (`NUI18`) ; la borne tenue (`NUI3`) ; le tri (`NUI10`) ; aucune ligne de CLAUDE.md, aucun commit par vlp.py.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` rend `OK`, dont un cas `plan` en dossier temporaire (projet, TODO de 3 codes,
   fichier des nuits d'une nuit passée) : (0) sans fichier des nuits, `plan ecrire` le crée (ligne d'index
   comprise), `plan lire` avant lui → `GARDE:` ; (a) A = deux chantiers, B = un → `lire --canal A` : 2 lignes, dans
   l'ordre, aussi sous `VLP_NUIT=1` (sort 0) ; `--chantier` du 2e : ses réponses, aucune du 1er ; (b) réécrit à
   la même date → une seule `## Nuit <date>`, avant `## Leçons` ; la nuit passée, la table et `## Leçons`
   identiques octet pour octet ; (c) neuf refus (code absent, préfixe `NUIT`, préfixe pris, préfixe en double,
   chantier dans deux canaux, canal C, JSON sans borne, réponse à saut de ligne, `VLP_NUIT=1`) → `GARDE:`,
   sort 1, fichier identique octet pour octet ; (d) `carte` d'un projet à fichier de fiches courant (constantes
   `CHANTIER`, `FICHES` de test-vlp.py) sous `VLP_NUIT=1` → `NUIT=1` une fois, après `--- CHANTIER.md ---` et
   avant `--- fiches :` ; avec `--relecteur`, sous `VLP_NUIT=0` et sans la variable → aucune ligne `NUIT=`.
2. Trois mutants joués par `py -3 scripts/vlp.py mutant scripts/vlp.py <avant> <après>` (défaut
   test-vlp.py), chacun `MUTANT ATTRAPÉ` : la ligne `NUIT=1` jamais écrite → (d) tombe ; les sections des
   autres dates perdues à la réécriture → (b) tombe ; le contrôle des lettres prises retiré → (c) tombe.
   Les trois commandes exactes au compte rendu.
3. pyright : 0 erreur sur `scripts/vlp.py` et `scripts/test-vlp.py`, compte brut au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:NUI13 -->
## NUI13 [x] — Écrire la conduite de nuit

**Session** : 28c4a1ca-ce9e-4c0a-9a6e-a5edbd860a0c
**Dépend de** : `NUI12`.
**Fichiers** : `nuit.md` (neuf, racine du kit), `methode-chantier.md`, `skills/init/SKILL.md`, `CLAUDE.md`, `context AI/00-INDEX.md`, `README.md`, `scripts/vlp.py`, `scripts/test-vlp.py` ; lus aux seules lignes citées : `skills/tache/SKILL.md`, `skills/tache/references/tache-blocage.md`, `skills/chantier/SKILL.md`, `skills/enchainer/SKILL.md`, `skills/enchainer/references/refus.md`, `cloture.md`, `ARTEFACTS.md` — et rien d'autre.

**Prompt**
Aucune commande ne sait qu'elle tourne sans humain ; depuis `NUI12`, la carte imprime `NUIT=1`. Écris `nuit.md`,
racine du kit comme `cloture.md` : le seul endroit qui dit, pour chaque attente d'un humain, ce que la nuit fait
à la place. Les renvois des commandes sont `NUI14` : ne touche ni `skills/` (hors init) ni `cloture.md`.
- En-tête (modèles cloture.md:1-4, refus.md:1-2) : `QUAND LIRE` (la carte imprime `NUIT=1`), qui le lit
  (`/vlp:tache`, `/vlp:chantier`, la session `clore`), « sans `NUIT=1`, ce fichier ne coûte rien ».
- Une table `Où | Ce qui attend l'humain | La nuit, à la place`, une ligne par citation, `fichier:ligne` en tête :
  tache/SKILL.md 29-30, 40, 42, 43, 45-47, 58, 67-68, 73-74, 76-78, 100-101, 104-106, 123, 144-147, 154-165 ;
  tache-blocage.md 43-46 ; ARTEFACTS.md 101-103 ; cloture.md 16-18, 39-40, 79-106, 108-113 ; chantier/SKILL.md
  40-42, 83-86, 133-145, 149-151, 154-161, 180-181, 280-281, 283-285 ; enchainer/SKILL.md:112-117 et
  refus.md:15-22 ensemble, une ligne (`/vlp:enchainer` ne tourne pas la nuit).
- À la place, jamais une question : `PROJET=` est le worktree du canal (aucun choix de projet), commentaires
  non lus ; `ATTENTE=` et `PLUGIN_RETARD=` notés au compte rendu, pas agis (ni republication, ni merge, ni
  tâche planifiée) ; la session de fiche coche à 6 bis, ne commite pas, ne clôt pas — le lanceur commite et
  lance `clore` (socle, « Invariants ») ; tout arrêt (`GARDE:`, fichier à « aucun », dépendance, Tentatives,
  troisième tentative, permission, geste, critère à l'œil, chantier ouvert, gabarits, avertissement de
  `valider`) : une ligne, la main rendue, ni `git checkout` ni écriture à la main — le lanceur met de côté
  (socle, « Mis de côté ») ; `/vlp:chantier` lit réponses et préfixe dans le plan (`NUI12`), suit sa réponse
  `découpage :` s'il y en a une (validée le soir, `NUI18`), sinon découpe seul, au plus sûr ; son arrêt final
  est le signal du lanceur ; le menu de clôture n'est pas posé, ses quatre cases vont au matin par `vlp.py
  nuits noter` (`NUI3` ; la sorte : `NUI19`), 3 (`niveau`, faux écarts en worktree) et 4 (dette « tout de suite ») comprises ; ce
  qui demande deux oui (methode-chantier.md:166-184) : au matin ; `git push` jamais, le matin par une
  question à lui seul.
- Pointe, ne recopie pas : ID de modèle, plafonds, clés du carnet (`boucle.py`, `carnet.py`) ; ni la TODO 72, dont la ligne sort à la clôture (cloture.md:16) : `nuit.md` porte la règle, une fois.
- Déclare-le le jour même (methode-chantier.md:310-311) : listes methode-chantier.md:294-298 et init:99-103,
  table du kit de `00-INDEX.md` (33-42), arbre du README (169-172) ; routage : CLAUDE.md:56 (« règle de
  méthode ») le nomme, aucune ligne de plus ; `CODE_PLUGIN` (vlp.py:1161-1162) le compte : lu dans le plugin
  chargé, son retard doit se voir.

**Critère de fin**
1. `py -3 scripts/vlp.py lire nuit.md` → code 0, 1re ligne `> **QUAND LIRE**` ; `grep -c "ne coûte rien"
   nuit.md` → 1 ; `grep -cE '^\| .*\.md:[0-9]' nuit.md` → 29, une par citation de la liste (une citation
   ajoutée monte ce compte d'autant, dite au rapport) ; `grep -cE "claude-(opus|sonnet|fable)|--max-|08-etat"
   nuit.md` → 0.
2. `grep -c "nuit\.md"` → une ligne de plus qu'avant la fiche (0 au 2026-10-01) dans methode-chantier.md,
   skills/init/SKILL.md, CLAUDE.md, `context AI/00-INDEX.md`, README.md ; `py -3 scripts/vlp.py lignes
   CLAUDE.md` → `80 CLAUDE.md`. Comptes bruts au rapport.
3. `py -3 scripts/test-vlp.py` → `OK`, avec un `verifier` neuf dans `tester_retard_plugin` : après `mod.carte`
   (test-vlp.py:5397), `commit(wt, "nuit.md", …)` puis `mod.retard_plugin(wt, kit=kit)` → `(2, …, "fiche")`
   (scripts/x.py et nuit.md ; context AI/n.md non compté). Mutant, `nuit.md` en fin de `CODE_PLUGIN` :
   `py -3 scripts/vlp.py mutant scripts/vlp.py '"ARTEFACTS.md", "nuit.md")' '"ARTEFACTS.md")'` →
   `MUTANT ATTRAPÉ <n> écart(s)`, ce `verifier` tombé ; chaînes exactes au rapport. pyright : 0 erreur sur
   vlp.py et test-vlp.py, compte brut. Pas de bac : rien ne lit `nuit.md` avant `NUI14`, qui l'essaie.
<!-- /FICHE -->

---

<!-- FICHE:NUI14 -->
## NUI14 [x] — Renvoyer les commandes à nuit.md

**Session** : 28c4a1ca-ce9e-4c0a-9a6e-a5edbd860a0c
**Dépend de** : `NUI13`.
**Fichiers** : `skills/tache/SKILL.md`, `skills/chantier/SKILL.md`, `cloture.md`, `nuit.md` (ses numéros de ligne seuls) ; lus seulement : `skills/enchainer/references/refus.md` (l. 1-2), `scripts/boucle.py` (docstring) ; dans le bac, `fiches.md` et la trace `F1.jsonl` — et rien d'autre.

**Prompt**
La nuit, les commandes ne savent pas qu'aucun humain ne répond. `carte` imprime `NUIT=1` (`NUI12`) et `nuit.md` dit quoi faire (`NUI13`). Relie l'un à l'autre : une ligne par fichier, qui pointe vers nuit.md sans en rien recopier (CLAUDE.md du kit, règle 3).
- Lis d'abord `nuit.md`. Il doit dire : pour `/vlp:tache <fiche>`, pas de commit, arrêt après 6 bis, pas d'étape 7 ; que seul le rôle `clore` (`/vlp:tache` sans fiche) applique cloture.md ; pour `/vlp:chantier`, lire le plan, n'interroger personne ; pour la clôture, ce que deviennent le menu, les deux oui et le push. Un point manque : arrête-toi et dis lequel, comme un blocage (étape 5, tache-blocage.md) ; `NUI13` le complète, pas toi.
- La ligne : `NUIT=1` → lis `nuit.md` par `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire nuit.md` ; il prime sur les étapes qui suivent.
- `skills/tache/SKILL.md`, étape 0 : une puce juste après `PROJET=` (l. 34-36). Raison : `ATTENTE=` et `PLUGIN_RETARD=` (l. 42-43) changent de sens la nuit.
- `skills/chantier/SKILL.md`, étape 0 : un paragraphe à lui, avec sa ligne vide, juste avant `ATTENTE=` (l. 46), donc avant l'étape 0 ter et ses questions. Pas un 5e point de la liste l. 36-44 : on s'y arrête au premier cas qui s'applique.
- `cloture.md` : une ligne dans l'encadré QUAND LIRE (l. 1-4).
- `refus.md` : aucune ligne. Seul `/vlp:enchainer` le lit (refus.md:1-2) ; la nuit, boucle.py tranche les refus (`NUI6`).
Les lignes ajoutées ne contiennent ni `commit`, ni `push`, ni `6 bis`. Elles décalent les citations `fichier:ligne` que nuit.md fait de ces trois fichiers : avance chaque numéro situé après ton insertion (+1, +2 pour chantier), et rien d'autre dans nuit.md. Tu ne touches ni à boucle.py, ni à vlp.py.
Le micro-essai se joue sur le plugin de `main`, que le plugin chargé suit (socle) : annonce-le dès le début.
- Commite les renvois sous un sujet qui nomme la fiche sans commencer par `NUI14 :` (`Renvois à nuit.md, avant l'essai de NUI14`) : `heures_commits` (vlp.py:2346) garde le plus ancien commit `NUI14 :`, et le coût de l'essai tomberait hors de la fiche. Le commit de 6 bis reste le seul `NUI14 :`.
- `py -3 scripts/vlp.py carte .` dans le kit : une ligne `PLUGIN_RETARD=` (fiche jouée en worktree) → donne sa commande, attends le oui ; pas de ligne → rien à demander. Pas de `/reload-plugins` : `claude -p` est un processus neuf (boucle.py:4-5).
Bac :
- `py -3 scripts/vlp.py bac <ton scratchpad>/nui14-bac` ; dans son `fiches.md`, retire « rien à commiter » du socle (Edit) : sinon « aucun commit » ne prouverait rien.
- Dans le bac : `py -3 <kit>/scripts/vlp.py cocher fiches.md F2` (F1 devient la dernière : sans nuit.md, l'étape 7 clôturerait), puis `git init` et un commit `base`.
- Puis `$env:VLP_NUIT='1'; py -3 scripts/boucle.py <bac> --plafond 1 --model claude-sonnet-5-5 --effort low --budget 1 --traces <ton scratchpad>/nui14-traces`.
`$env:` et `git` sortent des `allowed-tools` (aucune commande du kit ne porte `$env:`, chantier U) : dis-le en une ligne et demande l'autorisation (SKILL.md l. 26-30). Sans `--nuit`, boucle.py autorise `git commit` (`AUTORISES`, boucle.py:51) : seule la prose doit l'empêcher.

**Critère de fin**
1. Les renvois, sur le commit des renvois (`<sha>`) :
   - `grep -c "nuit.md"` : 1 dans `skills/tache/SKILL.md`, 1 dans `skills/chantier/SKILL.md`, 1 dans `cloture.md` (0 dans chacun avant) ;
   - `git show --numstat --format= <sha>` : `1 0` pour tache et cloture.md, `2 0` pour chantier, nuit.md à autant d'ajouts que de retraits, refus.md absent ;
   - aucune ligne ajoutée aux trois commandes ne contient `commit`, `push` ni `6 bis` ;
   - `grep -oE '\.md:[0-9]+' nuit.md | wc -l` : même compte avant et après ; chaque citation décalée relue sur sa ligne ;
   - `py -3 scripts/test-vlp.py` → `OK`.
2. Avant l'essai : `$env:VLP_NUIT='1'; py -3 scripts/vlp.py carte <bac>` imprime `NUIT=1` ; la carte du kit n'a pas de ligne `PLUGIN_RETARD=`.
3. L'essai (1 $ au plus, plafonné par `--budget 1`) :
   - boucle.py imprime `FICHE F1 · CASE [x]`, puis `ARRÊT plafond de 1 fiches` ;
   - `git -C <bac> rev-list --count HEAD` → 1 : aucun commit ;
   - la carte du bac garde `fiches.md` comme fichier courant, avec `PROCHAINE=aucune` : aucune clôture ;
   - dans `F1.jsonl`, les `tool_use` lus en JSON (pas un grep du fichier entier : le texte injecté de la commande peut citer `cloture.md`) : au moins un appel `lire nuit.md`, 0 `git commit`, 0 `cloture.md`.
   Au rapport : ces comptes bruts, plus le coût et les tours de la ligne `FICHE`.
<!-- /FICHE -->

---

<!-- FICHE:NUI15 -->
## NUI15 [x] — Fusionner le matin : CHANTIER.md et la feuille

**Session** : 28c4a1ca-ce9e-4c0a-9a6e-a5edbd860a0c
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` ; lus : `templates/CHANTIER.md`, `templates/artefact-feuille-de-route.html`,
`templates/artefact-archive-clos.html`, `methode-chantier.md` (l. 263-268) — et rien d'autre.

**Prompt**
Écris `vlp.py matin <projet> <date>` : il fusionne dans `main` les branches de la nuit `<date>` (nom, carnet,
sort d'un mis de côté : le socle) et répare ce que Git perd sans conflit (methode-chantier.md:263-268).
- Git par `git_texte` (vlp.py:1146). Gardes (`GARDE:`, sort 1, rien fusionné) : non équipé (`equipe`), HEAD hors `main`, arbre sale.
- Branches `refs/heads/nuit/<date>-*`. Pointe dont CHANTIER.md (`git show`) a un courant (`fichier_courant`,
  vlp.py:622) → `DE CÔTÉ <branche> — <courant>`, jamais fusionnée ; déjà ancêtre de `main` → `DÉJÀ <branche>`.
- Ordre du carnet (Q1) : `json.loads` ligne à ligne, sans importer carnet.py ; rang de la 1re ligne de chaque
  `canal` + `chantier`. Carnet absent : heure de la pointe, puis nom, et `ORDRE pointes — carnet absent`.
- Avant chaque fusion, retiens de `main` : `fichier de fiches courant`, `artefact du chantier` (`champ`, vlp.py:3136),
  les lettres (découpage de `lettres_prises`, vlp.py:3152 : factorise-le), `rang_en_cours` (vlp.py:3283) de la feuille.
- `git merge --no-ff --no-commit <branche>`, puis CHANTIER.md, en conflit ou non : les deux libellés de `main` ;
  les lettres de `main`, puis celles de la branche qui y manquent, une fois chacune.
- Autre conflit (code, 08-etat.md, archive…), ou feuille en conflit sans archive (`page_clos`, vlp.py:3515,
  rend la feuille) → `ARRÊT <branche> — conflit : <fichiers>`, sort 1 : fusion en cours, CHANTIER.md réparé et
  ajouté, suivantes non touchées ; la ligne donne la commande `feuille --todo <rang>` à lancer après résolution.
- Sinon : la feuille de `main` si en conflit, puis le chemin de `cmd_feuille` (vlp.py:3641), `todo` = le rang
  retenu ; `feuille()` ne refait pas `ZONE:archive` : avec une archive, `rafraichir_couts` (vlp.py:3526) le repose.
  Sa `GARDE:` → ARRÊT. Puis `git add -A` (joints, `couts.svg` ; l'arbre était propre), commit `Matin <date> :
  <branche>` (hors `COMMIT_FICHE`, vlp.py:2342) ; refusé (pre-commit) → `ARRÊT <branche> — commit refusé : <1re
  ligne>`, même sortie. `FUSIONNÉE <branche>` ; en fin : `MATIN <n> fusionnée(s) · <m> de côté`. Docstring à jour.

Tu ne fais pas : 08-etat.md, CLAUDE.md, l'index, archive-clos, `en-attente`, `.gitattributes` (`NUI16`), push, carnet.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` rend `OK`, dont une section `NUI15` : dépôt `git init -b main` en dossier
   temporaire, config Git isolée comme test-vlp.py:3019-3022, `GIT_COMMITTER_DATE` fixé à chaque commit.
   (a) `2cef70f` rejoué : base à courant `LOC`, un artefact, lettres `…ENQ`, badge au rang 79, une archive ;
   `nuit/<date>-A-PAR` clôt PAR (courant et artefact `aucun`, lettres `…ENQ, PAR`, ligne close à l'archive).
   Après `matin` : courant et artefact de LOC, `PAR` une fois, `rang_en_cours` = `79`, `ZONE:archive` compte
   la ligne de PAR, aucun `<<<<<<<`, HEAD à deux parents, `git status --porcelain` vide.
   (b) A et B, une lettre chacune sur la même ligne, feuille changée des deux côtés : les deux lettres gardées ;
   carnet où B précède A, pointe de B plus récente → B d'abord (`git log --first-parent main`).
   (c) Sans carnet, une pointe à courant ≠ `aucun` (commit `WIP`) : `ORDRE pointes`, `DE CÔTÉ`, hors de `main`.
   (d) Un `.py` changé des deux côtés : `ARRÊT` qui le nomme et donne `feuille --todo`, sort 1, `MERGE_HEAD`
   présent, la suivante pas fusionnée ; résolu, commité, relancé → `DÉJÀ`. (e) Hook `exit 1` par `core.hooksPath` :
   `ARRÊT … commit refusé`. (f) Dépôt nu en `origin` : sa `main` n'a pas bougé. (g) HEAD hors `main`, puis arbre
   sale : `GARDE:`, rien fusionné.
2. Deux mutants, chacun `MUTANT ATTRAPÉ` par `py -3 scripts/vlp.py mutant scripts/vlp.py <avant> <après>`
   (défaut test-vlp.py) : la ligne des lettres de la branche gardée telle quelle → (b) tombe (lettre de A absente) ;
   `todo` laissé à `None` → (a) tombe (badge perdu). Les deux commandes exactes au compte rendu.
3. pyright : 0 erreur sur vlp.py et test-vlp.py, compte brut au compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:NUI16 -->
## NUI16 [ ] — Fusionner le matin : 08-etat.md et les listes

**Dépend de** : `NUI15`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `.gitattributes` (une ligne, seulement si l'essai la garde),
`context AI/08-etat.md` (journal : le verdict de l'essai) — et rien d'autre.

**Prompt**
`matin` (`NUI15`) arrête sur tout conflit hors `CHANTIER.md` et feuille. Fusionne ici, par clé, les fichiers que
les deux canaux réécrivent : en 2cef70f, Git lève un conflit sur la TODO (suppression contre ajout voisin), et
`merge=union` y ressuscite la ligne 58 close. Ces chemins sortent de la liste d'ARRÊT de `NUI15` — fichier d'état,
`CLAUDE.md`, index et archive, `archive-clos.html`, `couts.svg`, `en-attente`, `publie` sans union ; ailleurs, un
conflit reste un ARRÊT. Après `git merge --no-ff --no-commit`, avant l'étape feuille de `NUI15`, recalcule-les
depuis base (`git merge-base`), avant et branche, lues par `git show <rev>:<chemin>`, jamais dans l'arbre marqué ;
écris, `git add` (`git rm` si vide). Absent des trois (non suivi, comme `publie` et `en-attente` dans le kit) :
ni écrit ni retiré ; le faire suivre n'est pas ici. Une fonction à 3 voies par clé (retiré d'un côté, intact de
l'autre = retiré ; changé d'un côté = ce changement ; ajouté = gardé ; changé des deux, ou retiré contre
changé = `GARDE:`, arrêt, sauf `en-attente`), pour :
- le fichier d'état (`champ(carte, "fichier d'état")`, jamais en dur), découpé par `section` (vlp.py:429) : TODO,
  clé `| n |` (`todo_du_fichier`, socle) ; « Journal des décisions » jusqu'à la fin, en union, ajouts de l'avant
  puis de la branche ; le reste par `git merge-file -p`, un conflit → arrêt.
- `CLAUDE.md` : lignes `ENTREE_CLOS` (vlp.py:4820) des deux côtés, coupées aux `CLOS_GARDES` dernières par la
  coupe de `resume_claude` (4827), sortie en fonction commune ; le reste par `git merge-file -p`.
- l'index et son archive (`chemin_archive`, 525) : clé la ligne ; archive retriée par `numero_ligne` (545).
- `archive-clos.html` (`page_clos`, 3515) : clé la ligne close (`lignes_clos`, 3701), la branche en tête ; pied
  et résumé par `resommer` (4186). Pas `rafraichir_couts` : il réécrit la feuille ; `couts.svg` en conflit prend
  la branche, l'étape feuille de `NUI15` le refait depuis l'archive (`couts_du_projet`, 3520).
- `en-attente` : clé la page ; changée des deux côtés → l'heure la plus récente, en fin comme
  `ajouter_attente` ; vide → retiré, comme `ecrire_attente`.
Essai de `publie` (D2) : dépôt temporaire, `publie merge=union`, deux branches écrites par `noter_publie` — clés
disjointes ; même clé, même empreinte ; empreintes différentes ; absent de la base. Compare cas par cas
`lire_publie` après `git merge` à la fusion par clé (désaccord → clé retirée, imprimée). Égal partout : la
ligne entre dans `.gitattributes` ; sinon, `publie` passe par la clé. Tu ne fais pas : `CHANTIER.md`, la
feuille (`NUI15`) ; `/vlp:chef` (`NUI19`) ; aucun push ; aucun `.py` ni `.html` en `merge=union`.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK` ; chaque cas : dépôt `git init` temporaire, base, branches A et B, `matin` :
   a. TODO (2cef70f) : base `| 58 |`, `| 82 |` ; A retire 58, B ajoute 83 → 58 absente, 82 et 83 là,
      `MERGE_HEAD` absent, HEAD à deux parents ; 82 changée en A et en B → `GARDE:`, sortie ≠ 0, aucun commit ;
   b. journal (5d7fc42) : A et B ajoutent un bloc en fin → les deux, A puis B, zéro `<<<<<<<` ;
   c. `CLAUDE.md` à `CLOS_GARDES` lignes « Clos le », A et B en closent un chacun → `CLOS_GARDES`, les 2 neuves ;
   d. archive de l'index : les deux lignes neuves, triées ; `archive-clos.html` : les deux, pied = `total_clos` ;
   e. `en-attente` : P retirée par A, intacte en B → absente ; Q changée des deux côtés → la plus récente ;
      vide → absent ; non suivi, présent dans l'arbre de `main` → intact ;
   f. `publie` : les quatre cas de l'essai ; l'état choisi verrouillé (ligne et union = script, ou pas de ligne).
2. Trois mutants `py -3 scripts/vlp.py mutant scripts/vlp.py <avant> <après>` (défaut test-vlp.py), `<avant>`
   dans le code neuf de `matin`, hors coupe commune, chacun `MUTANT ATTRAPÉ` : retiré d'un côté gardé → a ;
   coupe non appelée → c ; retrait d'`en-attente` ignoré → e. Rapport : chaîne exacte, ligne `ÉCART:` imprimée.
3. Verdict de l'essai cas par cas (lignes de `publie`, clés en désaccord) au rapport et au journal ; pyright 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:NUI17 -->
## NUI17 [ ] — Remplir une page à cartes par script

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `ARTEFACTS.md` (l. 19-23), `templates/rapport-choix.html` (lu, pas modifié) — et rien d'autre.

**Prompt**
`templates/rapport-choix.html` se remplit à la main : aucun script ne le cite, et une écriture à la main a déjà
publié une page vide (balise trouvée dans le commentaire ; commentaire corrigé en `3aecd04`). Ajoute
`vlp.py chef page --questions <json|@chemin> --sortie <page.html>` : le modèle choisit le contenu, le script
écrit la page — celle du soir (`NUI18`) comme le rapport du matin (`NUI19`). Zéro appel modèle.
- Entrée par `lire_arg` (vlp.py:5561). La forme du JSON et ses `GARDE:` vivent dans la docstring de `chef page`,
  seul endroit : `projet`, `sujet`, `titre`, `date` (défaut : le jour, lu), `jauge` facultative, puces d'en-tête,
  puis une clé par section du gabarit, dans son ordre ; une carte porte les champs de sa carte dans le gabarit,
  une option sa valeur, son libellé, ce qu'elle change, `recommande`.
- Jauge : un mot de `JAUGE` (vlp.py:1851), son émoji d'`EMOJIS_JAUGE`, la classe `moyen` ou `ko` du gabarit
  (l. 59-60, 111) selon son rang.
- La fonction prend le texte du gabarit en paramètre : la commande lui passe le vrai (chemin sous `KIT`, comme
  `GABARIT_FEUILLE`, vlp.py:3680), le test une copie. Elle n'en garde que la tête (`<title>` refait :
  `<projet> — <titre>` ; lien des polices, `<style>`), la section « Tes réponses » et le `<script>`, cherchés
  hors commentaires (`COMMENTAIRE`, vlp.py:4303) ; le commentaire de tête (l. 2-24) n'est pas recopié. Le reste,
  elle le bâtit ; une section sans clé est absente entière.
- Les `name` (D1… puis Q1…, dans l'ordre de la page) sont posés par le script, jamais par le JSON ; `data-cle`
  = `<projet>-<date>-<sujet>`. `<title>`, `data-cle` et `value` passent par `esc` (vlp.py:2184) seul, tout autre
  texte par `cellule_md` (vlp.py:3218) : échappé, gras et code rendus.
- `GARDE:`, rien écrit, sort 1 : JSON illisible, aucune carte, jauge hors `JAUGE`, question à moins de deux
  options, option sans effet, valeur doublée, deux recommandées ; morceau du gabarit introuvable ;
  `defauts_page` (vlp.py:4308) non vide sur la page bâtie, une ligne par défaut au format de `vigile`.
  Sinon : UTF-8, fins `\n`, imprime `PAGE SAINE <n> blocs` puis `CARTES D1 Q1…`, sort 0.
Ajoute l'entrée à la docstring de vlp.py près de `vigile` (vlp.py:296), et une phrase à ARTEFACTS.md:19-23 qui
y renvoie. Tu ne fais pas : `/vlp:chef` ni le choix des questions (`NUI18`), le rapport tiré du carnet
(`NUI19`), la publication ; le gabarit ne change pas et reste remplissable à la main.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` rend `OK`, dont un bloc neuf après les cas de `vigile` (test-vlp.py:4377-4394),
   dans son propre dossier temporaire (pas `tvg`), sur une copie lue du vrai gabarit :
   (a) jauge « Imprévu », une décision, Q1 à deux options, Q2 à trois dont une recommandée → sort 0,
   `CARTES D1 Q1 Q2` ; `name="Q2"` 3 fois, « (recommandé) » 1 fois, `class="jauge moyen"` 1 fois ; `vigile` sur
   le fichier → `PAGE SAINE` ; `data-cle` attendu ; `<h2>Tes réponses</h2>` et `<script>` 1 fois chacun ;
   `<!--` 0 fois ; ni « Le fil », ni `&lt;Projet&gt;`, ni `<dépôt>` ;
   (b) le titre de Q1 `a < b & **c**` → `a &lt; b &amp; <strong>c</strong>` dans son `<h3>` ;
   (c) balise citée : copie dont le commentaire de tête cite `<div class="page"` et `<script>`, même JSON
   qu'en (a) → sort 0, page identique à l'octet à celle de (a) ;
   (d) page vide : copie sans `<style>` ni `<link>` → `GARDE:` « aucun style », fichier absent, sort 1 ;
   (e) aucune carte, jauge « Super », option sans effet → `GARDE:` chacun, rien écrit.
2. Trois mutants, chacun `MUTANT ATTRAPÉ` par `py -3 scripts/vlp.py mutant scripts/vlp.py <avant> <après>`
   (défaut test-vlp.py) : morceaux cherchés dans le gabarit brut → (c) tombe ; résultat de `defauts_page`
   ignoré → (d) tombe ; `cellule_md` ôté du titre de question → (b) tombe. Commandes exactes au compte rendu.
3. `grep -c "chef page" ARTEFACTS.md` → 1 (0 avant) ; pyright : 0 erreur sur vlp.py et test-vlp.py, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:NUI18 -->
## NUI18 [ ] — Écrire /vlp:chef, le soir

**Dépend de** : `NUI9`, `NUI11`, `NUI12`, `NUI13`, `NUI17`.
**Fichiers** : `skills/chef/SKILL.md` (nouveau), `nuit.md` (une ligne de sa table), `scripts/test-vlp.py` (NIV1
2128-2137, EVF4 2149-2161), `CLAUDE.md` (11-12), `README.md` (5, 86-88) ; lus : `skills/chantier/SKILL.md`
(1-5, 18, 133-162), les docstrings de `scripts/vlp.py` (`trier`, `plan`, `chef page`) et de `scripts/boucle.py`
(lancement), `context AI/08-etat.md` (ligne 381 seule), `context AI/33-sans-refus.md` (35-41) — et rien d'autre.

**Prompt**
Écris la partie soir de `/vlp:chef` (TODO 72 : PAR5 Q2, Q7, Q8, Q10 ; Q6 du cadrage) : elle juge, les scripts
écrivent (`NUI9`-`NUI12`, `NUI17`) ; le matin est `NUI19`. Un appel ou un champ absent : RETOUR, n'invente pas.
- Frontmatter comme `chantier` (son socle `Bash`/`PowerShell`, plus `git`, `Read`, `Write`, `Artifact`), sans `model:`.
- L'injection de `skills/chantier/SKILL.md:18` à l'identique (8e copie) ; `NUIT=1` : une ligne de renvoi à
  `nuit.md`, où tu ajoutes « `/vlp:chef` ne se joue pas la nuit ». Hors Opus 5.5 : dis-le, demande ; sans oui, arrête.
- `vlp.py trier` (`NUI10`, `NUI11`), puis le jugement : dépendance implicite (l'un change ce que l'autre appelle ou
  mesure) → même canal ; chaque marque → carte ou « écarté : <raison> » ; un taux « indice » ne multiplie rien ;
  une `GARDE:` de `trier` se dit, ne se contourne pas.
- Ligne SOIR (TODO 72 : « se découpe le soir ») : carte « découpage validé ce soir » — tu proposes les fiches (titres,
  ordre), il valide ; une réponse `découpage :` du plan, que la nuit suit (`nuit.md`) — ou « écarter cette nuit ». Rien
  n'est ouvert sur `main` : un chantier ouvert y passerait aux deux canaux (`GARDE` de `cmd_ouvrir`, vlp.py:5153).
- Questions, réponses, page : au dossier du carnet (socle ; `git rev-parse --path-format=absolute --git-common-dir`).
  Page par `vlp.py chef page` (`NUI17`), publiée par `Artifact` telle qu'elle sort : par chantier prêt, questions
  de l'étape 3 de `/vlp:chantier` et préfixe de son étape 4 ; ordre et canal à valider (Q7) ; borne en $ et en
  chantiers (Q8) ; une leçon de `trier` dans le pourquoi de la carte qu'elle touche.
- Réponses → `vlp.py plan` (`NUI12`) : canal et estimé retenus, chacun sa raison. Avant : `git branch --show-current`
  ≠ `main`, ou fichier des nuits ignoré (`git check-ignore`) → dis-le, arrête-toi, aucun checkout. Après : `git add`
  de ce fichier, et de l'index le soir où `plan` l'a créé, commit au sujet hors `COMMIT_FICHE` ; puis la ligne de lancement de la docstring de
  boucle.py (`NUI9`), jamais composée à la main : l'utilisateur la lance.
`test-vlp.py` : EVF4 compte les SKILL.md du glob (le 7 en dur part, commentaire et libellé compris) ; NIV1 lit aussi
`chef` (trois lignes identiques). `CLAUDE.md:11-12` et `README.md` (5, 86-88) : six commandes, `/vlp:chef` nommé.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK`, comptes bruts et durée ; EVF4 : 8 injections pour 8 SKILL.md ; NIV1 :
   trois lignes. pyright sur `scripts/test-vlp.py` : 0 erreur, compte brut.
2. `py -3 scripts/vlp.py mutant skills/chef/SKILL.md @<avant> @<après>` (fichiers du scratchpad : `` !`py `` →
   `` `py ``) → `MUTANT ATTRAPÉ`, ÉCART sur EVF4 (que l'ancien `injections == 7` laissait passer) et sur NIV1.
   Chaînes exactes au rapport.
3. `grep -c '^model:' skills/chef/SKILL.md` → 0 ; `grep -o '/scripts/vlp.py" carte' skills/chef/SKILL.md | wc -l`
   → 3 ; `grep -c 'nuit.md' skills/chef/SKILL.md` → 1 ; `grep -c 'git branch --show-current'
   skills/chef/SKILL.md` → 1 ; `grep -c 'vlp:chef' nuit.md CLAUDE.md README.md` → ≥ 1 chacun ; `wc -l CLAUDE.md` → 80.
4. Micro-essai (≈ 0,1-1 $) : bac sans `.git`, kit copié en `vlpz` comme `33-sans-refus.md:35-41` (`vlp.py bac`) ;
   `claude -p "/vlpz:chef" --model claude-sonnet-5-5 --max-budget-usd 1 --output-format stream-json --verbose` :
   la carte (`PYTHON=`) au transcript, le `result` dit « pas Opus » et demande ; blocs `tool_use` du stream : 0 ;
   `permission_denials` : [] ; liste du bac identique avant et après ; `total_cost_usd` et `num_turns` bruts.
<!-- /FICHE -->

---

<!-- FICHE:NUI19 -->
## NUI19 [ ] — Écrire /vlp:chef, le matin

**Dépend de** : `NUI13`, `NUI15`, `NUI16`, `NUI18`.
**Fichiers** : `skills/chef/SKILL.md`, `scripts/vlp.py`, `scripts/carnet.py`, `scripts/test-vlp.py`, `nuit.md` ; lus :
`scripts/mesure-tokens.py` (`resoudre` :94, `sous_agents` :115, `mesurer` :220), `cloture.md:98-115`,
`methode-chantier.md:166-184`, `ARTEFACTS.md` (« Une publication refusée ») — et rien d'autre.

**Prompt**
Le soir (`NUI18`) et la fusion (`NUI15`-`NUI16`) existent. Le script d'abord : `matin --rapport <json>`, sans fusion ni commit, rejouable :
1. Carnet de la nuit (`carnet.py`) : chaque ligne `est_session` (`NUI3`) sans `usd_kit` reçoit `usd_kit`, `tours_kit` :
   `resoudre`, `mesurer` sur la session et ses `sous_agents`, `usd_exact` et `tours` sommés comme vlp.py:2470 (un `None`
   rend `None`), arrondis une fois (`quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`, vlp.py:2472). Introuvable, illisible ou `usd_exact` `None` → aucune clé `_kit`, une
   ligne `KIT ? <session> — <raison>`, jamais 0. Réécriture sous le verrou de `NUI3`, le même, pas un second ; `CLES`
   y gagne `sorte` (et `usd_kit`, `tours_kit` s'ils manquent).
2. Fichier des nuits (`fichier_nuits(p, creer=True)`, `NUI11`) : une ligne de table par (nuit, canal, chantier)
   absente, tirée du carnet. `nuits lecon "<ligne>"` ajoute une leçon sous `## Leçons` ; hors forme (`NUI11`) : `GARDE:`.
3. Le JSON au format de `chef page --questions` (`NUI17`) : une carte de rapport par chantier (issues, relances,
   `modeles_vus`, `plugin_retard`, `_kit` sommés, jamais `_cli`) ; une par mis de côté — la détection `DE CÔTÉ` de
   `NUI15` sortie en une fonction que `matin` et `--rapport` appellent, croisée au carnet (`cause`, dépendants sautés :
   `NUI7`), désaccord → `ÉCART` — aux trois réponses du socle (« Mis de côté ») ; une par note selon sa `sorte` :
   `reste`, les trois réponses du premier oui ; `case3`, `case4`, faire ou laisser ; sans sorte : `NOTE SANS SORTE`.
   `nuits noter` prend `--sorte reste|case3|case4` ; une ligne de nuit.md, où `NUI13` renvoie restes et cases au
   matin, dit à `clore` de la passer.
Puis la section « Le matin » de skills/chef/SKILL.md, entrée par l'argument `matin`, un appel par geste :
1. `matin` avec l'utilisateur ; conflit de code : la main à lui, arrêt (`NUI15`). `ATTENTE=` → ARTEFACTS.md ;
   `PLUGIN_RETARD=` → `/reload-plugins`, son geste. Puis `matin --rapport`, 1 à 3 leçons ajoutées au JSON (tirées des
   `cause` et `reecriture`, forme de `NUI11`), `chef page --questions`, page publiée (refus : ARTEFACTS.md).
2. Réponses collées : leçon gardée → `nuits lecon` ; tenue deux nuits → proposée pour methode-chantier.md (deux oui) ;
   reste versé : le second oui, ligne relue avant son commit ; case 3 ou 4 : faite selon cloture.md ; reprendre : la
   branche nommée, rien d'autre ; abandonner ou rejouer (la nuit repart de `main`, `NUI7`) : `git branch -D <branche>`
   donné, jamais lancé ; rejouer garde la ligne TODO, que le tri du soir reprend (`NUI10`).
3. Le commit du matin ; puis `git push`, une question à lui seul, jamais une carte ; « Pour finir ».
Tu ne fais pas : la fusion, le remplisseur, le soir, le reste de nuit.md ; aucun push.

**Critère de fin**
1. `py -3 scripts/test-vlp.py` → `OK`, comptes bruts. Un cas en dossier temporaire (dépôt `git init`, carnet, home comme
   test-vlp.py:1533) : sessions à sous-agent, sans transcript, à sous-agent hors `GRILLE` ; un mis de côté ; notes `reste`, `case3`, sans sorte :
   a. `usd_kit`, `tours_kit` = somme de `mesurer` sur les deux transcripts, calculée par le test ;
   b. `--rapport` rejoué : carnet et fichier des nuits identiques à l'octet, une ligne de table par chantier, verrou
      absent, `git rev-list --count HEAD` inchangé ;
   c. sans transcript, et hors `GRILLE` : aucune clé `_kit`, une ligne `KIT ?` chacune ;
   d. JSON : mis de côté et `reste` à trois réponses, `case3` à deux, `NOTE SANS SORTE`, pas de `push` ; `nuits lecon` hors forme → `GARDE:`.
2. Trois mutants `py -3 scripts/vlp.py mutant scripts/vlp.py <avant> <après>` → `MUTANT ATTRAPÉ` : sous-agents non
   sommés (a tombe) ; `usd_exact` `None` compté 0 (c) ; ligne de table ajoutée à chaque rejeu (b). Chaînes au rapport.
3. Comptes bruts avant → après : skills/chef/SKILL.md `grep -c 'vlp.py" matin'` +2, `"chef page --questions"` +1,
   `"git push"` +1, `"git branch -D"` +1 ; nuit.md `grep -c -- "--sorte"` +1. Pas de micro-essai en `-p`
   (`AskUserQuestion` absent, 08-etat.md:1436) : la preuve d'usage est `NUI20`.
4. pyright : 0 erreur sur les `.py` touchés, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:NUI20 -->
## NUI20 [ ] — Jouer une nuit réelle

**Dépend de** : `NUI1`, `NUI2`, `NUI3`, `NUI4`, `NUI5`, `NUI6`, `NUI7`, `NUI8`, `NUI9`, `NUI10`, `NUI11`, `NUI12`, `NUI13`, `NUI14`, `NUI15`, `NUI16`, `NUI17`, `NUI18`, `NUI19`.
**Fichiers** : lus — `nuit.md` ; `CHANTIER.md` de `main` (`git show main:CHANTIER.md`) ; `context AI/08-etat.md`, lignes 381 (« Q7 essai réel ») et 384 à 386 (`APR`, `TAB`, `CLV`) ; le carnet et le fichier des nuits (socle, « Les noms retenus ») ; le fichier de fiches de chaque chantier de la nuit (`git show <branche>:<fichier>`) ; appelés : `scripts/vlp.py` (`carte`, `vigile`), `scripts/mesure-tokens.py`, `scripts/test-vlp.py` ; écrit — une entrée `## <date> — NUI20` au journal de `context AI/08-etat.md`, et rien d'autre.

**Prompt**
L'essai qui prouve le chantier : une vraie nuit sur le kit, au plan de Q7 (TODO n° 72, ligne 381) — `TAB` puis `CLV`
sur A, `APR` sur B, sa borne double (socle). Tu ne lances ni la nuit ni `claude` : ces gestes sont à l'utilisateur.
- Avant, arrête-toi au premier écart (RETOUR, l'écart nommé) :
  a. chaque fiche `NUI1` à `NUI19` a son commit `<fiche> :` (`COMMIT_FICHE`, vlp.py:2342) dans `main` ;
  b. `main` sans chantier ouvert (`fichier de fiches courant : aucun`) : la nuit part de `main` et `ouvrir` refuse un
     second chantier (vlp.py:5151-5154). La fusion `--ff-only` qui avance `main` (vlp.py:739-741) y amène `NUI` ouvert :
     l'utilisateur remet `aucun` par un commit à lui sur `main`, avant la nuit ; tu relèves son sha, tu ne l'écris pas ;
  c. `vlp.py carte` dans le worktree de `NUI` sans ligne `PLUGIN_RETARD=` ; le `/reload-plugins` : l'utilisateur le confirme ;
  d. `py -3 scripts/test-vlp.py` sur `main` → `OK`, durée lue par `time` (Bash) : le script n'en imprime aucune ;
  e. relevés : `git worktree list`, `git rev-parse main origin/main`, `git status --porcelain` de `main`, la cellule
     « Coût estimé » des trois lignes TODO.
- Puis rends la main : l'utilisateur ouvre sur `main` une session au modèle du chef (TODO n° 72, Q10), joue `/vlp:chef`
  le soir, tape la ligne de lancement (`NUI9`), et revient après le `/vlp:chef` du matin. Tu ne lis rien de la nuit avant.
- Au retour, compte ; carnet et fichier des nuits restent aux scripts :
  - par chantier : sa branche, son issue (clos, mis de côté et sa raison, sauté, pas parti), fiches découpées /
    acceptées (commits `COMMIT_FICHE` de la branche) / refusées, relances (rôle `relance` au carnet), son `**Estimé.**`
    (`ESTIME`, vlp.py:4823), posé seulement par `ouvrir --estime-fiches` : absent, noté, écart sur la cellule TODO seule ;
  - la nuit : `usd_kit`, `tours_kit` sommés (socle, carnet), durée, lignes par `issue`, replis, `plugin_retard`
    (attendu sur A après `TAB` : noté, pas agi) ; à part, les sessions du soir et du matin, par `mesure-tokens.py <id>`.
- Une `GARDE:` de `clore` compte comme mis de côté : la nuit, `clore` est celui de `main`, dette `CLV` comprise.
Tu ne corriges rien de ce que la nuit révèle : chaque défaut, avec sa session et sa ligne de carnet, va à l'entrée du
journal avec la table des comptes ; la suite se décide à la clôture de `NUI`. Jamais de push : la question est à `/vlp:chef`.

**Critère de fin** (visuel)
1. Avant : a à e passés, bruts dans l'entrée (19 commits, sha du commit `aucun`, `PLUGIN_RETARD=` absent, reload
   confirmé, durée du test, sha de `main` et `origin/main`).
2. L'utilisateur a vu la fusion et la page du rapport (`vlp.py vigile <page>` → `PAGE SAINE`), et le dit.
3. Chacun des trois chantiers a une branche et une issue ; un clos a sa ligne `role` `clore` au carnet et sa branche
   fusionnée dans `main` ; `CLV` part de la pointe de `TAB` si `TAB` est clos (`git merge-base --is-ancestor`), sinon de
   `main` ; un mis de côté est listé, pas fusionné ; aucun quatrième chantier.
4. Pot final dans la borne, ou dépassement dit session par session ; `origin/main` au sha relevé ; `git log <sha
   relevé>..main` : les fusions et les réparations de `vlp.py matin` (`NUI15`, `NUI16`) seules, listées.
5. L'entrée du journal porte la table des comptes bruts (coût, tours, fiches acceptées, relances, mis de côté) à côté
   de l'estimé relevé avant (cellules TODO ; lignes `**Estimé.**` trouvées, 0 à 3), écart en $ et en %, sur le même
   instrument ou dit ; une nuit : un indice, pas une règle.
<!-- /FICHE -->
