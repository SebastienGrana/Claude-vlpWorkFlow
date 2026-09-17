> **QUAND LIRE** : on joue une fiche `Q*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache Q<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier Q — `/vlp:enchainer` sans Git

**À quoi il sert.** Depuis le chantier Y (v3.4.0), le kit annonce « Python 3 seul, Git facultatif ». Une commande
sur cinq dément la promesse : le sous-agent `vlp:fiche` n'a que l'outil `Bash` et fait un `cat` hors du projet.

**Ouvert** le 2026-09-17. Aucune fiche jouée.

## Le socle commun

**Ce qui bloque, lu au cadrage le 2026-09-17** (lignes approximatives) :

| Où | Ce qui s'y joue |
|---|---|
| `agents/fiche.md` frontmatter | `tools: Read, Edit, Write, Bash` — sans Git Bash, l'outil `Bash` n'existe pas : le sous-agent ne lance rien |
| `agents/fiche.md` étape 1 | `cat "<kit>/enchainement.md" "<kit>/skills/tache/references/…"` : lecture hors du projet → refus, repli `Read` |
| `agents/fiche.md` étapes 3-5 | vérification scriptable, `grep -n`, coche : tout passe par un shell que l'agent n'a pas |
| `skills/jouer/SKILL.md` | porte la carte « py d'abord » et les `allowed-tools` PowerShell ; le sous-agent forké n'en hérite pas — à vérifier en `Q1` |
| `skills/enchainer/SKILL.md` | chef déjà migré (carte, `<python>`, `vlp.py valider --plan`, `page`, `lire`) — sert de modèle |
| `enchainement.md` | contrat `FAITE` / `RETOUR` / `BLOQUÉE` ; ne parle d'aucun shell |

Comptes de départ : `grep -c 'cat "' agents/fiche.md` = 1 · `grep -c 'PowerShell' agents/fiche.md` = 0.

**Ce qu'un corps de skill ou d'agent s'interdit depuis `U`** : `cat`, `ls`, `$env:…`, `[ ]`, `&&`, `||`, un tuyau vers
`tr`/`grep`/`head`/`wc`/`xargs`, `2>/dev/null`. Une commande simple par ligne, `;` entre deux. Ce que faisait un tuyau
est une sous-commande de `vlp.py` : `lire`, `cocher`, `page`, `cout`, `lignes`, `valider --plan`, `socle`, `extraire`.

**Frontière** (tranchée au cadrage) : dedans, `agents/fiche.md`, `skills/jouer/SKILL.md`, la revue des six
`skills/*/SKILL.md` et des références de `tache` sous l'angle « lancé par un sous-agent », le coût comparé
enchaînement / jeu à la main, `README.md`, la version du plugin, la TODO n° 21. Dehors : macOS, PowerShell 5.1
(non sondable tant que `pwsh` 7 est installé — `U1`), `.githooks/`, la refonte du contrat de retour.

**Le bac de sonde** (méthode validée en `U`, socle de `context AI/33-sans-refus.md`) : scripts `bac.py <nom>`,
`lire.py`, `detail.py` du scratchpad de `U` —
`C:/Users/znorr/AppData/Local/Temp/claude/C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow/1b086951-ecc7-4072-8bdd-86bf3948ebee/scratchpad/`.
Ils se **recopient** avant d'être modifiés. `bac.py` copie le plugin dans `plugz/` (`name` → `vlpz`,
`shell: powershell` avant les `allowed-tools` de chaque skill) et écrit un bac **sans `.git`**. Ici, il lui faut
**deux** fiches triviales, pour qu'un enchaînement ait une suite. Lancement :
`MSYS_NO_PATHCONV=1 "$C" -p "/vlpz:enchainer" --plugin-dir "$(pwd -W)/plugz" --tools PowerShell Skill Read Edit Write
--permission-mode acceptEdits --model sonnet --max-budget-usd 1.2 --output-format stream-json --verbose`. Jamais
`bypassPermissions` : il cache les refus. `--tools` sans `Bash` **est** la simulation du poste sans Git.
Refus = `permission_denials` de la dernière ligne ; coût du lancement entier, sous-agents compris = `total_cost_usd` ;
le texte réellement injecté et le message du sous-agent se lisent dans le transcript du bac
(`~/.claude/projects/*<bac>*/<id>.jsonl`), pas dans le stream-json. **Plafond 2 $ de sondes par fiche.**

**Outils de preuve** : `py scripts/vlp.py valider <fichier>`, `py scripts/test-vlp.py` (« OK », 108 assertions avant
`Q`, s'arrête au premier écart), `py scripts/vlp.py renvois .`, `"$C" plugin validate .` (1 avertissement voulu),
`C=$(ls -d "$APPDATA"/Claude/claude-code/*/claude.exe | tail -1)` ; evals : `hook` sous Windows, `wsl2` sous Ubuntu
(pièges du prompt de chantier). `mesure-tokens.py` ne compte pas les sous-agents : pour eux, seul `total_cost_usd`
du run `-p` fait foi.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `Q1` | Mesurer l'enchaînement sans Git — refus, tours, coût | rien |
| `Q2` | Donner `PowerShell` au sous-agent et lui retirer `cat` | `Q1` |
| `Q3` | Chasser `Bash` et `cat` partout où un sous-agent lit | `Q1` |
| `Q4` | Prouver sans refus dans le même bac | `Q2`, `Q3` |
| `Q5` | Chiffrer enchaîner contre jouer à la main, écrire le verdict | `Q4` |

`Q3` ne dépend que du constat de `Q1` : elle peut se jouer avant `Q2`. `Q4` rejoue la sonde de `Q1` à l'identique.

---

<!-- FICHE:Q1 -->
## Q1 [x] — Mesurer l'enchaînement sans Git — refus, tours, coût

**Dépend de** : rien.
**Fichiers** : `context AI/33-sans-refus.md` (socle seul, lecture) ; les scripts du scratchpad de `U` nommés dans le socle — recopiés, jamais modifiés en place. Aucun fichier du kit touché.

**Prompt**
Recopie `bac.py`, `lire.py`, `detail.py` dans le scratchpad de cette session. Adapte `bac.py` pour que le bac porte
**deux** fiches triviales (`Z1` puis `Z2`, chacune : écrire un fichier), la seconde dépendant de la première, et une
page générée par `page --creer`. Lance la sonde `/vlpz:enchainer` sous PowerShell 7, **sans l'outil `Bash`**.
Relève, bruts : tours et `total_cost_usd` du lancement entier, chaque `permission_denials` (outil + début de commande)
classé par cause (`cat` hors projet, shell absent, `allowed-tools`, autre), le statut rendu par le sous-agent
(`FAITE` / `RETOUR` / `BLOQUÉE` / aucun), et le nombre de fiches cochées dans le bac. Dans le transcript, lis ce que
le sous-agent a reçu : la carte y est-elle, et avec quel `PYTHON=` ? Écris un bloc **Mesuré** sous cette fiche.

**Critère de fin**
Bloc Mesuré présent : `permission_denials` = <n> classés par cause (somme = n), tours et coût affichés, statut rendu
recopié, `grep -c '\[x\]'` du fichier de fiches du bac, présence ou absence de la carte dans le message du sous-agent ;
`git status --short` ne montre que ce fichier.

**Mesuré** (2026-09-17) — bac `scratchpad/bacq1` (`bac.py bacq1`, deux fiches `Z1` puis `Z2`), Sonnet, pwsh 7,
`--tools PowerShell Skill Read Edit Write` — **sans `Bash` : c'est la simulation du poste sans Git**. Lancement :
**4 tours, 0,1357 $, 7 appels**. **3 refus** (`permission_denials`), tous `Read` hors projet, tous du sous-agent :
`plugz/enchainement.md`, `skills/tache/references/tache-contraintes.md`, `…/tache-blocage.md` — c'est le repli
« permission refusée sur le kit : `Read` sur les mêmes fichiers » de l'étape 1 de `agents/fiche.md`. Classement :
lecture hors projet 3 · shell absent 0 (somme 3) — l'outil `Bash` n'étant pas *refusé* mais **absent**, aucune
tentative n'entre dans `permission_denials` : le sous-agent n'a lancé ni `vlp.py socle` ni `extraire`, donc ni socle
ni fiche extraite. Statut rendu : **`RETOUR`** (« Permission refusée sur les fichiers du kit »), le chef a ensuite
posé la question à l'utilisateur. Résultat : `[x]` = **0** sur 2, `sortie.txt` et `sortie2.txt` **absents**, 0 fiche
jouée. **La carte reçue par le sous-agent n'est pas journalisée** : l'exécution forkée n'apparaît dans aucun des 3
transcripts du bac (0 message `isSidechain`, 0 « Fiche à jouer ») — seul son compte rendu remonte au chef.
Deux pièges de sonde, imprévus : ① le nom du plugin est **en dur** (`enchainer` appelle `skill: "vlp:jouer"`,
`jouer` déclare `agent: vlp:fiche`) — sans les renommer dans la copie, le chef du bac appelle la skill du plugin
**réel** (chargé en `-p` sous Windows, sans `shell: powershell`) et la sonde mesure autre chose (1er lancement :
4 appels, 0,1218 $, blocage `Bash` sur l'injection du vrai `vlp:jouer`) ; ② `--plugin-dir` veut un chemin
**Windows** — un chemin MSYS `/c/…` avec `MSYS_NO_PATHCONV=1` donne « Unknown command: /vlpz:enchainer », 0 tour.
Sondes : 3 lancements, **0,26 $** au total.
<!-- /FICHE -->

---

<!-- FICHE:Q2 -->
## Q2 [x] — Donner `PowerShell` au sous-agent et lui retirer `cat`

**Dépend de** : `Q1`.
**Fichiers** : `agents/fiche.md`, `skills/jouer/SKILL.md`, `scripts/test-vlp.py`.

**Prompt**
Dans `agents/fiche.md` : ajoute `PowerShell` à la ligne `tools:` ; remplace le `cat` de l'étape 1 par
`<python> "<kit>/scripts/vlp.py" lire …` sur les mêmes fichiers ; réécris tout corps qui suppose un shell POSIX aux
règles du socle (une commande simple par ligne, `;` entre deux, pas de `&&` ni `||`, pas de tuyau). Dis d'où vient
`<python>` : la carte est dans le message de `vlp:jouer` — si `Q1` a montré qu'elle n'y arrive pas, fais-la porter par
`jouer` de façon explicite. Ne touche pas au contrat de retour. Compte les motifs avant et après.

**Critère de fin**
`grep -c 'cat "' agents/fiche.md` = 0 et `grep -c 'PowerShell' agents/fiche.md` ≥ 1, comptes avant/après affichés ;
`py scripts/test-vlp.py` rend « OK » ; `"$C" plugin validate .` passe (1 avertissement voulu) ;
`py scripts/vlp.py renvois .` sans ligne `0 absent` en défaut.

**Mesuré** (2026-09-17) — `agents/fiche.md`, comptes avant → après : `cat "` **1 → 0**, `PowerShell` **0 → 1**
(la ligne `tools:`), `grep -n` **1 → 0**. Trois gestes : `tools: … Bash, PowerShell` ; l'étape 1 lit le kit par
`<python> "<kit>/scripts/vlp.py" lire enchainement.md skills/tache/references/…` (chemins relatifs au kit, `lire`
les y résout) au lieu du `cat` et de son repli `Read` ; l'étape 5 coche par `vlp.py cocher`, et le repérage d'une
ligne avant `Edit` passe de `grep -n` à `valider --plan`. L'intro dit d'où vient `<python>` (`PYTHON=` de la carte)
et interdit `cat`, `ls`, `&&`, `||`, les tuyaux. `skills/jouer/SKILL.md` porte déjà la carte et `<python>` :
rien à y changer. Preuves : `test-vlp.py` « OK », `renvois .` 45 nommés · 0 absents, `plugin validate .`
« Validation passed ». Doc lue (`code.claude.com/docs/en/sub-agents.md`) : `PowerShell` est un nom d'outil valide
pour un sous-agent, et un **fork reçoit le pool exact de la conversation principale** — un agent de plugin ne peut
en revanche pas porter `permissionMode` (ignoré), ce qui se vérifiera en `Q4`.
<!-- /FICHE -->

---

<!-- FICHE:Q3 -->
## Q3 [ ] — Chasser `Bash` et `cat` partout où un sous-agent lit

**Dépend de** : `Q1`.
**Fichiers** : les six `skills/*/SKILL.md`, `agents/fiche.md`, `enchainement.md`, `skills/tache/references/` (les fichiers que l'agent lit à son étape 1).

**Prompt**
Inventorie toute commande qu'une skill ou l'agent prescrit, et cherche les motifs bannis du socle (`cat`, `ls`,
`$env:`, `[ ]`, `&&`, `||`, tuyau, `2>/dev/null`, `sh`). Pour chacun, dis qui le lancerait et dans quel contexte
(session principale, sous-agent forké). Corrige ce qui est dans la frontière ; note en une ligne ce qui n'y est pas.
Vérifie aussi les `allowed-tools` : un couple `Bash(...)` sans son `PowerShell(...)` est un manque.
Écris la table avant/après sous la fiche.

**Critère de fin**
Table des motifs avec compte avant et après par fichier ; les motifs bannis comptés à 0 dans `agents/` et dans les six
`skills/*/SKILL.md` (sortie de `grep` recopiée) ; chaque `Bash(` des `allowed-tools` a son `PowerShell(` ;
`py scripts/test-vlp.py` rend « OK » ; `py scripts/vlp.py valider` sans écart sur les fichiers touchés.
<!-- /FICHE -->

---

<!-- FICHE:Q4 -->
## Q4 [ ] — Prouver sans refus dans le même bac

**Dépend de** : `Q2`, `Q3`.
**Fichiers** : aucun fichier du kit modifié — sauf correction rendue nécessaire par la sonde.

**Prompt**
Rejoue le bac de `Q1` tel quel, avec le plugin modifié seulement recopié (mêmes fiches, même prompt, mêmes `--tools`
sans `Bash`, même modèle). Relève les mêmes comptes qu'en `Q1` et pose-les côte à côte. Si un refus résiste, dis sa
cause exacte et si elle est dans la frontière ; deux tentatives au plus, puis bloc **Tentatives**. Rejoue les evals
seulement si un fichier chargé par le plugin et couvert par une eval a changé — sinon dis-le et n'en lance aucune.

**Critère de fin**
Table avant/après : `permission_denials` `Q1` → `Q4` (cible 0 hors clôture du bac), tours, `total_cost_usd`, statut
rendu par le sous-agent, `grep -c '\[x\]'` du bac = 2 ; evals rejouées avec réussis/total, ou la phrase qui dit
pourquoi non.
<!-- /FICHE -->

---

<!-- FICHE:Q5 -->
## Q5 [ ] — Chiffrer enchaîner contre jouer à la main, écrire le verdict

**Dépend de** : `Q4`.
**Fichiers** : `README.md` (prérequis, ce qui est sondé), `.claude-plugin/plugin.json` (version), `context AI/08-etat.md` (TODO n° 21).

**Prompt**
Rapporte le coût du lancement de `Q4` (chef + sous-agents, `total_cost_usd`) au coût d'une fiche jouée à la main.
Chaque chiffre porte sa source : le run de `Q4`, la ligne `37331eef` de `context AI/12-audit.md` pour le chef seul,
le repère de clôture du chantier `D` pour les fiches à la main. Dis en deux lignes lequel gagne, et à quelle condition
— sans arrondir en faveur de l'enchaînement. Puis : `README.md`, une ligne sur `/vlp:enchainer` sondé sans Git (ou
non) ; plugin en 3.4.2 ; TODO n° 21 retirée du fichier d'état.

**Critère de fin**
Table à deux lignes — à la main / enchaîné — avec coût par fiche et la source de chaque chiffre ; verdict écrit en
deux lignes ; `grep -c '3.4.2' .claude-plugin/plugin.json` = 1 ; la TODO n° 21 absente de `context AI/08-etat.md` ;
`"$C" plugin validate .` passe.
<!-- /FICHE -->
