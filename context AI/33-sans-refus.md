> **QUAND LIRE** : on joue une fiche `U*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache U<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier U — `/vlp:tache` sans refus sous PowerShell

**À quoi il sert.** Sans Git, une fiche passe mais paie des refus de permission (`cat` hors du projet, `$env:…`,
nom de page deviné) et la carte s'ouvre sur le message du raccourci Store. Le kit doit tourner sous PowerShell sans un refus.

**CLOS** le 2026-09-17. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** U1..U5 (2026-09-17) : refus mesurés (9) et 5.1 non forçable, lire/cocher/page déduite dans vlp.py, corps sans cat ni $env et sans attente, carte py d'abord avec relais prouvé, preuve refus 9 → 1 et evals.

## Le socle commun

**Ce qui provoque un refus** (lu au cadrage, le 2026-09-17 — lignes approximatives) :

| Où | Ce qui s'y joue |
|---|---|
| `skills/tache/SKILL.md` 62, 106, 144 · `chantier` 87 · `enchainer` 108 | `cat "${CLAUDE_PLUGIN_ROOT}/…"` : 6 `cat` d'un fichier du kit, hors du projet → refus, repli `Read` |
| `skills/tache/SKILL.md` 118-122 | coche + `**Session** : <id>` par `Edit`, l'id « étant `$CLAUDE_CODE_SESSION_ID` » → le modèle tente `$env:…` |
| `skills/tache/SKILL.md` 131 · `chantier` (5 bis) | `page "<fiches>" "<contexte>/artefacts/<NN>-<chantier>.html"` : chemin tapé par le modèle, deviné → `GARDE:` |
| `scripts/vlp.py` ~312 · ~798 · ~1377 | `cout --session` écrit déjà `SESSION=<id>` ; `cmd_page` ; le parseur de `page` |
| `allowed-tools` de `tache` | `PowerShell(cat:*)`, `Bash(cat:*)`, `PowerShell(ls:*)`, `Bash(ls:*)` en plus des Python |
| injection des 6 skills | `python3 …carte --python python3; py …carte --python py --relais; echo fin` — sous Windows, `python3` = raccourci du Store : son message (accents cassés) précède `PYTHON=` |

Compter avant et après : `grep -c 'cat "' skills/*/SKILL.md` (6 au cadrage).

**Frontière** (tranchée au cadrage) : dedans, les corps de `tache`, `chantier`, `enchainer`, `vlp.py`, la carte
injectée, PowerShell 5.1 sondé, le relais sur un poste où `python3` et `py` répondent tous deux. Dehors : macOS
(aucune machine) ; `agents/fiche.md` (outil `Bash` seul : `/vlp:enchainer` sans Git n'est pas couvert, à noter en TODO) ;
`.githooks/`, `evals/*/fixture.sh`. Git Bash et Ubuntu doivent continuer de marcher. Recherche web permise
(doc Claude Code : `curl` la page `code.claude.com/docs/en/<page>.md` dans le scratchpad, puis `Grep`).

**Le bac de sonde** (méthode validée en Y5, `context AI/32-sans-git.md`, bloc Mesuré de Y5) : script Python du scratchpad
qui copie le plugin dans `plugz/` (`name` → `vlpz` dans `plugin.json`, `shell: powershell` ajouté avant `allowed-tools`
de chaque skill) et écrit un bac **sans `.git`** : `CHANTIER.md` (URL d'artefact fictive, « Lettres de fiche déjà prises »),
`context AI/01-z.md` (fiche `Z1` : écrire un fichier), sa page `context AI/artefacts/01-z.html` (`page --creer`).
Lancement : `MSYS_NO_PATHCONV=1 "$C" -p "/vlpz:tache Z1" --plugin-dir "$(pwd -W)/plugz" --tools PowerShell Skill Read Edit
Write --permission-mode acceptEdits --model sonnet --max-budget-usd 1.2 --output-format stream-json --verbose` (jamais
`bypassPermissions` : il cache les refus). Refus = `permission_denials` de la dernière ligne ; coût = `total_cost_usd` ;
texte injecté = transcript du bac (`~/.claude/projects/*<bac>*/<id>.jsonl`). Garder le script : U5 le rejoue.
**Plafond 2 $ de sondes par fiche**, au-delà arrêt.

**Outils de preuve** : `python scripts/vlp.py valider <fichier>`, `python scripts/test-vlp.py` (« OK », 100 assertions
avant U), `python scripts/vlp.py renvois .`, `"$C" plugin validate .` (1 avertissement voulu), `C=$(ls -d
"$APPDATA"/Claude/claude-code/*/claude.exe | tail -1)` ; evals : pièges du prompt de chantier (Windows `hook`, Ubuntu `wsl2`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `U1` | Mesurer les refus avant | rien |
| `U2` | Faire absorber lectures, coche et nom de page par `vlp.py` | `U1` |
| `U3` | Réécrire les corps des skills sans `cat` ni `$…` | `U2` |
| `U4` | Nettoyer la carte et prouver le relais à deux Python | `U1` |
| `U5` | Prouver sans refus, sous PowerShell 7 et 5.1 | `U3`, `U4` |

U4 ne touche que l'injection : elle peut se jouer avant U2 ; U5 rejoue la sonde de U1 à l'identique.

---

<!-- FICHE:U1 -->
## U1 [x] — Mesurer les refus avant

**Dépend de** : rien.
**Fichiers** : `context AI/32-sans-git.md` (bloc Mesuré de Y5, lecture seule) — et rien d'autre ; aucun fichier du kit modifié.

**Prompt**
Écris le script du bac (voir le socle) et lance la sonde `/vlpz:tache Z1` sous PowerShell 7. Relève, bruts : tours,
`total_cost_usd`, fiche cochée ou non, et chaque `permission_denials` (outil + début de commande), classé par cause
(`cat` hors projet, `$env:`, nom de page, autre). Lis dans le transcript le texte injecté : la carte commence-t-elle
par le message du Store ? Puis cherche comment faire jouer à Claude Code `powershell.exe` 5.1 plutôt que `pwsh` 7
(doc `code.claude.com/docs/en/*.md`, recherche web) : réglage, variable, ou « impossible » avec la source.
Écris un bloc **Mesuré** sous cette fiche : la table des refus, la méthode 5.1, le chemin du script du bac.

**Critère de fin**
Bloc Mesuré présent : `permission_denials` = <n> classés par cause (somme = n), tours et coût affichés, fiche du bac
cochée ou non (`grep -c '\[x\]'`), méthode 5.1 trouvée ou source qui dit non ; `git status --short` n'a que ce fichier.

**Mesuré** (2026-09-17) — bac `scratchpad/bacu1` (script `scratchpad/bac.py <nom>`, lecture `PYTHONUTF8=1 py lire.py
<sortie.jsonl> <nom>`), Sonnet, pwsh 7.6.6. **Deux prompts** : `/vlpz:tache Z1` s'arrête à l'étape 6 (« Confirmes-tu ? »),
puis `--resume <id> -p "Confirmé, continue."`. Prompt 1 : 7 tours, 0,123 $, 6 appels, **1 refus** (`cat` de
`tache-contraintes.md` hors projet → 2 `Read`). Prompt 2 : 10 tours, 0,129 $, 9 appels, **8 refus** : 5 `$env:CLAUDE_CODE_SESSION_ID`
(dont `[Environment]::…` et un `dangerouslyDisableSandbox`), 3 `py …vlp.py` (`cout` ×2, `socle`) — **les `allowed-tools` d'une
skill ne valent plus après la confirmation** (nouveau prompt) : `cout` et `page` refusés, page non régénérée. Total **9 refus**
(cat 1 · $env 5 · allowed-tools perdus 3 · nom de page 0, `page` jamais atteinte) ; fiche du bac cochée (`[x]` = 1),
Session absente. Carte injectée : « Python est introuvable ; ex�cutez… » avant `PYTHON=py`. Au montage, `page --creer`
échoue si `artefacts/` n'existe pas (FileNotFoundError). **PowerShell 5.1 non forçable** : doc `tools-reference.md`
(« auto-detects `pwsh.exe` … fallback to `powershell.exe` ») ; binaire 2.1.271 : chemins en dur, « PATH is never
consulted » ; sondes Haiku `CLAUDE_CODE_TEST_NO_PWSH=1` et `ProgramFiles` faussé → 7.6.6 (0,02 $ chacune). Seule voie :
un poste sans pwsh 7 (geste de l'utilisateur). Sondes : 0,25 $ Sonnet + 0,14 $ Haiku.
<!-- /FICHE -->

---

<!-- FICHE:U2 -->
## U2 [x] — Faire absorber lectures, coche et nom de page par `vlp.py`

**Dépend de** : `U1`.
**Fichiers** : `scripts/vlp.py` (docstring, `cmd_page`, parseur), `scripts/test-vlp.py`.

**Prompt**
Trois sous-commandes ou options, chacune testée, docstring à jour :
- `lire <chemin relatif au kit>…` : imprime des fichiers du kit (la racine = dossier parent de `scripts/`) ; refuse
  un chemin qui sort du kit ; remplace les 6 `cat` du socle.
- `page <fiches>` sans second argument : la page se déduit, `<dossier des fiches>/artefacts/<même nom>.html` ; avec
  le second argument, comportement inchangé.
- `cocher <fiches> <fiche> [--resolu "…"]` : `[ ]` → `[x]` sur le titre, `**Session** : <id>` avant « Dépend de »
  (id lu dans l'environnement, absent → pas de ligne, dit), bloc Tentatives réduit à la ligne « résolu par » si
  `--resolu` ; écrit `COCHÉ <fiche> · Session <id|absente>`. Déjà cochée : refus, code non nul.
Garde les ajouts de tests dans le style existant ; calcule les attendus, ne les tape pas.

**Critère de fin**
`python scripts/test-vlp.py` → « OK » avec <n> assertions (> 100, compte par `grep -cE`) ; sur une copie du bac de U1,
`lire`, `page` sans sortie et `cocher` relancés deux fois rendent la sortie attendue puis le refus ; `valider` VALIDE.
<!-- /FICHE -->

---

<!-- FICHE:U3 -->
## U3 [x] — Réécrire les corps des skills sans `cat` ni `$…`

**Dépend de** : `U2`.
**Fichiers** : `skills/tache/SKILL.md`, `skills/chantier/SKILL.md`, `skills/enchainer/SKILL.md`, `cloture.md` (s'il
nomme le coche ou la page).

**Prompt**
Remplace les 6 `cat "${CLAUDE_PLUGIN_ROOT}/…"` par `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" lire …` (un seul
appel pour plusieurs fichiers). Étape 6 de `tache` : la coche et la Session passent par `cocher` (plus d'`Edit`, plus
de `$CLAUDE_CODE_SESSION_ID` dans le texte) ; `page` sans chemin de sortie dans `tache` et `chantier`. Retire de
`allowed-tools` ce qui ne sert plus (`cat`, `ls` si plus aucun appel). Une commande simple par ligne, `;` entre deux,
jamais `||`, `&&`, `$…`, tuyau. Aucun ajout de prose au-delà du remplacement. Relis `tache-page.md` et
`tache-blocage.md` : s'ils nomment `cat` ou le coche par `Edit`, aligne-les. Décidé après U1 (les `allowed-tools`
tombent au prompt suivant) : un critère scriptable ne fait plus attendre de confirmation — coche, coût et page dans le
même prompt ; seul un critère visuel attend le retour de l'utilisateur.

**Critère de fin**
`grep -c 'cat "' skills/*/SKILL.md cloture.md` → 0 partout (6 avant) ; `grep -c 'CLAUDE_CODE_SESSION_ID' skills/*/SKILL.md`
→ 0 ; `renvois .` 0 absent ; `test-vlp.py` OK ; `"$C" plugin validate .` OK ; lignes de `tache` avant/après affichées.
<!-- /FICHE -->

---

<!-- FICHE:U4 -->
## U4 [x] — Nettoyer la carte et prouver le relais à deux Python

**Dépend de** : `U1`.
**Fichiers** : `skills/*/SKILL.md` (ligne d'injection des 6), `scripts/vlp.py` (`carte`, `--relais`), `scripts/test-vlp.py`.

**Prompt**
La carte injectée sous Windows commence par le message du raccourci Store de `python3`. Cherche une forme qui le
taise sans casser Ubuntu (où seul `python3` existe) ni Git Bash, et sans `2>`, `||`, `&&` : ordre des deux appels,
argument de `carte`, ou autre (recherche web permise sur le raccourci et `$LASTEXITCODE`). Sonde chaque forme candidate
en injection d'une skill de bac (`--model haiku --max-budget-usd 0.3`) sous PowerShell, Git Bash et Ubuntu, avant d'écrire.
Puis le relais : un dossier de shim `python3.cmd` → vrai Python, mis en tête du PATH du lancement, pour un poste où
`python3` et `py` répondent tous deux ; lis dans le transcript combien de cartes sont injectées.
Applique la forme retenue aux 6 skills en un script (compte chaque motif avant de remplacer). Si rien ne marche :
garde l'injection, dis pourquoi dans un bloc Mesuré, et arrête-toi pour demander.

**Critère de fin**
Texte injecté lu dans les transcripts : PowerShell, Git Bash, Ubuntu → `PYTHON=` en tête, 0 ligne « Python est
introuvable » ; avec le shim → 1 seule ligne `PYTHON=` ; `grep -c` de la nouvelle injection = 6 ; `test-vlp.py` OK.

**Mesuré** (2026-09-17) — le message du Store sort sur **stderr** (code 49), capturé par l'injection ; rien ne le tait
sans `2>` (recherche web : seule parade, désactiver l'alias dans Windows). Aucun ordre ne donne 0 bruit partout :
**décidé avec l'utilisateur** : ordre inversé + une ligne README. Tentative 1 `py …; python3 … --relais; echo fin` :
Git Bash OK, Ubuntu OK, **PowerShell avorte** (« Shell command failed » : `$LASTEXITCODE` = 49, `echo` n'est pas natif).
Tentative 2 : `py …; python3 … --relais; py … --relais; echo fin` et le relais **ne retire plus** le tampon (sinon le
3e appel réécrit la carte). Sondes Haiku, bac `scratchpad/bacu4` (skills `sondeps|sondebash|sondeubu`, `injecte.py`) :
PowerShell et Git Bash → `PYTHON=` en tête, 1 message Store à la fin, OK ; Ubuntu → « py: command not found » ×2 (1 en
tête), 1 `PYTHON=`, OK ; shim venv `python3.exe` en tête du PATH (format `/c/…` : un `C:/` dans PATH Git Bash est coupé
au `:`) → 1 seule carte, 0 message, OK. Injection ×6, tests OK. Sondes : 0,046 $ + 0,063 $.
<!-- /FICHE -->

---

<!-- FICHE:U5 -->
## U5 [x] — Prouver sans refus, sous PowerShell 7 et 5.1

**Session** : 1b086951-ecc7-4072-8bdd-86bf3948ebee
**Dépend de** : `U3`, `U4`.
**Fichiers** : `README.md` (prérequis, ce qui est sondé), `.claude-plugin/plugin.json` (version), `context AI/08-etat.md` (TODO n° 20).

**Prompt**
Rejoue le script du bac de U1 tel quel (recopie seulement le plugin modifié) sous PowerShell 7, puis sous 5.1 par la
méthode trouvée en U1 (ou dis qu'elle n'existe pas). Relève les mêmes comptes qu'en U1, côte à côte. Rejoue les evals :
Windows `hook`, Ubuntu `wsl2` (4 cas). Plugin 3.4.1. README : PowerShell 5.1 sondé ou non, macOS non sondé ; pas de prose
en plus. TODO n° 20 : retirée ; ajoute l'entrée « `/vlp:enchainer` sans Git » si U1 à U4 l'ont confirmée.

**Critère de fin**
Table avant/après : `permission_denials` U1 → U5 (cible 0 sous pwsh 7), tours, coût, fiche du bac cochée
(`grep -c '\[x\]'` = 1) et page régénérée sans `GARDE:` ; 5.1 : mêmes comptes ou « non sondable » sourcé ; evals
réussis/total par cas ; `validate` OK ; `renvois .` 0 absent.

**Mesuré** (2026-09-17) — même bac (`bac.py bacu5`), Sonnet, pwsh 7.6.6, **un seul prompt** (plus d'attente de
confirmation). Avant (U1) → après : refus **9 → 1** ; partie fiche (lecture, écriture, `cocher` + `cout` + `page` en un
appel) : **0 refus**, 5 tours, 0,19 $ ; Session **absente → écrite** (`COCHÉ Z1 · Session f52d…`) ; page **non
régénérée → « 1 faite »**, 0 `GARDE:` de `page`. Le refus restant vient de la clôture du bac (`Test-Path` sur
`plugz/scripts/mesure-tokens.py`, hors projet, improvisé). Run entier : 18 tours, 0,42 $ (clôture comprise ; U1 : 17
tours, 0,25 $ sans page ni clôture). Carte : `PYTHON=py` en tête. **5.1 non sondable** ici (U1). Evals : Windows `hook`
1/1 (0,05 $) ; Ubuntu `chantier` 1/1, `check` 1/1, `init` 1/1, `tache` 1/1 (1,50 $, 163 s). Plugin 3.4.1 ; TODO n° 20
retirée, n° 21 ajoutée (`/vlp:enchainer` sans Git : l'agent n'a que `Bash`).
<!-- /FICHE -->
