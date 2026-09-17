> **QUAND LIRE** : on joue une fiche `Y*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache Y<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier Y — Le kit entier sans `sh`

**À quoi il sert.** Sans Git Bash, le hook se tait, les skills à `!`sh …`` échouent avant tout tour, et le corps
appelle `sh`, `grep`, `wc`, `tr`, `xargs`. Le kit doit tourner de bout en bout sans Git, et le README cesser de l'exiger.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 5 fiches, `Y1` à jouer.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17 — les lignes sont approximatives) :

| Où | Ce qui s'y joue |
|---|---|
| `hooks/hooks.json` | `PostToolUse` `Write\|Edit`, forme shell : `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" hook` |
| `skills/{chantier:18,enchainer:25,jouer:20,tache:17}/SKILL.md` | l'injection `!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" carte`` |
| corps : `chantier` 47, 221, 239 · `check` 44, 55, 115 · `enchainer` 41, 96 · `init` 23 · `tache` 39, 62, 132, 133 · `cloture.md` 22, 35 | les appels `sh …/scripts/vlp` ; bash seul en plus : `tache` 62 (`F="…"`), 132 (`[ -n "$S" ] &&`, `tr`), `cloture.md` 22 (`tr \| xargs -0`), `enchainer` 41 (`grep`), `init` 23 (`ls -d */ \| head`) |
| `allowed-tools` des 6 skills | `Bash(sh:*)` partout, plus `grep`, `cat`, `wc`, `head`, `tail`, `sed`… selon la skill |
| `scripts/vlp` | lanceur `sh` : premier de `python3`, `python`, `py` qui répond à `-c ""` ; `mesure` → `mesure-tokens.py` |
| `README.md` ~l. 44 | « Prérequis : Python 3 et un `sh` » — Git for Windows requis |

Compter avant d'écrire : `grep -rn 'sh "${CLAUDE_PLUGIN_ROOT}' skills cloture.md hooks | wc -l`.

**Recette mesurée par X** (`context AI/28-sans-sh.md`) : hook forme exec (`command` + `args`, shell ignoré), paire
`python3` + `py` = une erreur non bloquante de chaque côté, muette ; injection `py … || python3 …` propre sous pwsh 7,
Git Bash et Ubuntu ; `python3 … || python …` colle le message du Store devant `PROJET=` ; si la dernière commande
d'une injection échoue, la skill échoue à 0 tour ; `shell: powershell` = pwsh 7 même ôté du PATH ; `powershell.exe`
5.1 refuse `||`. Non sondé : `allowed-tools` hors `bypassPermissions`, 5.1 en injection, Python du Store seul.

**Frontière** (tranchée au cadrage) : dedans, le hook, les injections, le corps des 6 skills et `cloture.md`,
PowerShell 5.1, Python du Store seul, le sort de `scripts/vlp` (tranché en Y1). Dehors : macOS (aucune machine) ; le
bug `Artifact action "comments"` (traité dans une autre session) ; `.githooks/` et `evals/*/fixture.sh` (outils du
mainteneur, qui a Git). Git Bash doit continuer de marcher : chaque forme retenue passe sous Git Bash ET sans.

**Simuler et prouver** : sans Git = `shell: powershell` dans le frontmatter d'une skill de bac
(`.claude/skills/<nom>/SKILL.md`, `-p "/<nom>"`) ou d'un hook (`.claude/settings.json` du bac) — l'environnement ne
simule rien ; Ubuntu = `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -l /mnt/c/…/sonde.sh 2>&1 | tr -d '\0'` ;
preuve d'un hook : `--include-hook-events` → `hook_response` ; d'une injection : le transcript du bac. Sondes en
`--model haiku --max-budget-usd 0.3`, coût = `total_cost_usd` ; **plafond 1 $ de sondes par fiche**, au-delà arrêt.

**Outils de preuve** : `sh scripts/vlp valider <fichier>`, `python scripts/test-vlp.py` (« OK », 96 assertions
avant Y), `sh scripts/vlp renvois .`, `"$C" plugin validate .` (1 avertissement voulu), `C=$(ls -d
"$APPDATA"/Claude/claude-code/*/claude.exe | tail -1)`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `Y1` | Sonder les trous et choisir la forme d'appel | rien |
| `Y2` | Faire absorber les outils Unix du corps par `vlp.py` | rien |
| `Y3` | Passer le hook et les injections sans `sh` | `Y1` |
| `Y4` | Passer le corps des skills et `cloture.md` sans `sh` | `Y1`, `Y2` |
| `Y5` | Prouver sans Git et documenter | `Y3`, `Y4` |

Y1 et Y2 sont indépendantes ; Y3 et Y4 appliquent la forme choisie en Y1.

---

<!-- FICHE:Y1 -->
## Y1 [ ] — Sonder les trous et choisir la forme d'appel

**Dépend de** : rien.
**Fichiers** : `context AI/28-sans-sh.md` (socle et bloc « Constaté » de X2 seulement), un bac dans le scratchpad ;
écrit un bloc « **Mesuré** » sous cette fiche.

**Prompt**
Sonde ce que X n'a pas sondé, une ligne par cas, et tranche la forme d'appel unique des skills :
1. **PowerShell 5.1** : quel shell Claude Code prend sans pwsh 7 (doc Claude Code, WebFetch avec citation) ; la
   syntaxe des formes candidates sous `powershell.exe -NoProfile -Command` (hors Claude Code : dis-le).
2. **Python du Store seul** : simule `py` absent par un nom inexistant (`pyx … || python3 …`) sous pwsh 7 et Git
   Bash : la sortie garde-t-elle `PROJET=` en début de ligne ?
3. **allowed-tools** hors `bypassPermissions` : une skill de bac en `-p` sans `--permission-mode`, `allowed-tools`
   `Bash(py:*)`, `Bash(python3:*)`, `PowerShell(py:*)` — l'appel passe-t-il sans approbation ?
4. **Le corps sans Bash** : `--disallowedTools Bash` sur le bac — le modèle lance-t-il l'appel par PowerShell ?
Puis tranche `scripts/vlp` : **retirer** si une forme sans `sh` passe dans les cas 1 à 4 et sous Ubuntu, **garder en
repli** sinon. Si aucune forme ne passe partout, arrête-toi et présente le tableau.

**Critère de fin**
Le bloc « Mesuré » sous la fiche : un tableau cas × environnement (Git Bash, pwsh 7, 5.1, Ubuntu) avec la sortie brute
de chaque sonde et son coût, total ≤ 1 $ ; la forme retenue écrite en une ligne ; le sort de `scripts/vlp` écrit.
<!-- /FICHE -->

---

<!-- FICHE:Y2 -->
## Y2 [ ] — Faire absorber les outils Unix du corps par `vlp.py`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (docstring, `cmd_sessions`, parseur), `scripts/test-vlp.py`, `skills/tache/SKILL.md`
(l. ~130-134), `cloture.md` (l. ~20-24), `skills/enchainer/SKILL.md` (l. ~41), `skills/init/SKILL.md` (l. ~23).

**Prompt**
Relis les quatre passages : chacun enchaîne `vlp` avec un outil Unix (`[ -n ] &&`, `tr`, `xargs`, `grep`, `ls -d */
| head`). Pour chacun, choisis : une option ou une sous-commande de `vlp.py` qui rend la même sortie en un appel
(ex. `sessions --mesure` qui mesure elle-même chaque session, sans `xargs`), ou un outil du modèle (`Grep`, `Glob`)
nommé dans la prose. Écris le code et ses tests ; ne touche pas encore aux skills — Y4 les réécrit. Liste dans un
bloc « **Mesuré** » : passage → remplaçant → sortie avant/après identique (diff vide ou écart expliqué).

**Critère de fin**
`python scripts/test-vlp.py` → `OK`, assertions 96 → n affichées ; pour chaque passage, l'ancienne commande et la
nouvelle lancées sur le kit, `diff` des deux sorties vide (ou écart écrit) dans le bloc « Mesuré ».
<!-- /FICHE -->

---

<!-- FICHE:Y3 -->
## Y3 [ ] — Passer le hook et les injections sans `sh`

**Dépend de** : `Y1`.
**Fichiers** : `hooks/hooks.json`, `skills/{chantier,enchainer,jouer,tache}/SKILL.md` (ligne d'injection et
`allowed-tools` seulement), `scripts/test-vlp.py` si un test lit `hooks.json`.

**Prompt**
Applique la forme retenue en Y1 (bloc « Mesuré ») : le hook en forme exec (paire mesurée par X), les 4 injections
`carte` dans la forme d'appel unique. Rien d'autre dans les skills. Puis sonde, bac du scratchpad, `--model haiku` :
le hook (`--include-hook-events`) et `/vlp:tache` à 0 tour d'action (la carte suffit) sous Git Bash, sous
`shell: powershell`, et sous Ubuntu.

**Critère de fin**
`"$C" plugin validate .` OK (1 avertissement) ; `python scripts/test-vlp.py` → `OK` ; tableau 3 environnements ×
{hook `VALIDE` dans `hook_response.stdout`, `PROJET=` en tête de ligne dans le transcript}, sorties brutes et coût
≤ 1 $ ; `grep -c 'sh "' hooks/hooks.json` = 0.
<!-- /FICHE -->

---

<!-- FICHE:Y4 -->
## Y4 [ ] — Passer le corps des skills et `cloture.md` sans `sh`

**Dépend de** : `Y1`, `Y2`.
**Fichiers** : `skills/{chantier,check,enchainer,init,tache}/SKILL.md`, `cloture.md`, `skills/tache/references/` si
un appel `sh` y vit (`grep -rln 'sh "' skills/tache/references`).

**Prompt**
Compte d'abord les appels (commande du socle). Remplace chaque `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" …` par la
forme retenue en Y1, et chaque tuyau Unix par le remplaçant de Y2. Une commande du corps ne doit plus rien exiger de
bash : pas de variable `F=`, pas de `[ ]`, pas de `|` vers `tr`, `grep`, `head`, `wc`. Mets les `allowed-tools` au
diapason de Y1. Pas de phrase nouvelle hors du strict nécessaire : chaque ligne se paye à chaque exécution.

**Critère de fin**
`grep -rn 'sh "${CLAUDE_PLUGIN_ROOT}' skills cloture.md | wc -l` → n avant, 0 après ; `grep -rnE '\| *(tr|xargs|head|wc|grep)
' skills cloture.md` → 0 ; `"$C" plugin validate .` OK ; `python scripts/test-vlp.py` → `OK`.
<!-- /FICHE -->

---

<!-- FICHE:Y5 -->
## Y5 [ ] — Prouver sans Git et documenter

**Dépend de** : `Y3`, `Y4`.
**Fichiers** : `README.md` (prérequis), `.claude-plugin/plugin.json` (version), `scripts/vlp` (si Y1 a dit
retirer), `context AI/08-etat.md` (TODO n° 16).

**Prompt**
Preuve de bout en bout : dans un bac simulé sans Git (`shell: powershell` + `--disallowedTools Bash`, méthode validée
en Y1), `/vlp:tache` joue une fiche triviale (écrire un fichier) jusqu'à la cocher et régénérer la page ; relève tours,
coût, appels refusés. Rejoue les evals sous Windows (`check`, `init`, `hook`) et Ubuntu (`tache`, `chantier`).
Puis le README : prérequis Python 3 seul, Git Bash facultatif, ce qui reste non sondé (macOS) ; plugin 3.4.0 ;
`scripts/vlp` retiré ou gardé selon Y1, sans renvoi mort.

**Critère de fin**
La sonde de bout en bout coche la fiche du bac (`grep -c '\[x\]'` = 1) avec 0 appel `sh`, coût affiché ; evals :
comptes réussis/total par cas ; `sh scripts/vlp renvois .` (ou sa forme neuve) → 0 absent ; `"$C" plugin validate .` OK.
<!-- /FICHE -->
