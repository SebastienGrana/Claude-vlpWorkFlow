> **QUAND LIRE** : on joue une fiche `G*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache G<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier G — Le kit sans Git Bash

**À quoi il sert.** Le hook et toutes les commandes lancent `sh …/scripts/vlp` ; sous PowerShell seul, `sh` est
introuvable. On établit par la doc et une sonde quel shell Claude Code emploie, puis on rend le hook sûr ou on écrit le prérequis.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 2 fiches, `G1` à jouer.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17) :

| Où | Ce qui s'y joue |
|---|---|
| `hooks/hooks.json` | `PostToolUse` `Write\|Edit` → `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" hook` |
| `scripts/vlp` | lanceur `#!/bin/sh` : premier de `python3`, `python`, `py` qui passe `-c ""`, puis `vlp.py` ou `mesure-tokens.py` |
| `skills/*/SKILL.md` | `allowed-tools: Bash(sh:*)` ; `!`sh …/scripts/vlp carte`` injecté dans `chantier`, `tache`, `enchainer`, `jouer` |
| `README.md` ligne ~64 | « Sur Windows (PowerShell, sans droits administrateur) » — la mise en place |

**Mesuré au cadrage, sous PowerShell** (`Get-Command`) : `sh` absent ; `bash` = `C:\Windows\system32\bash.exe`,
c'est-à-dire **WSL**, jamais un remplaçant de `sh` ; `python` et `py` répondent, `python3` est le raccourci du Store ;
le PATH n'a que `Git/cmd` et `Git/mingw64/bin` ; `CLAUDE_CODE_GIT_BASH_PATH` vide. Pourtant le hook tourne dans
cette session : Claude Code trouve Git Bash sans le PATH — à prouver, pas à supposer.

**Frontière** (tranchée au cadrage) : seul le **hook** peut changer de lanceur ; les commandes gardent `sh` et le
prérequis s'écrit pour elles. Hors chantier : les evals WSL2 (TODO n° 11), l'eval `init`.

**Arrêt voulu** : si l'outil PowerShell ne s'active pas en `-p`, ou si la sonde dépasse son budget, la fiche rend
la main à l'utilisateur — pas de repli sur la doc seule.

**Outils de preuve** : `sh scripts/vlp valider`, `sh scripts/vlp renvois .` (0 absent), `python scripts/test-vlp.py`,
`claude.exe plugin validate .` puis `validate .claude-plugin/plugin.json` (1 avertissement voulu), evals Windows :
`claude.exe plugin eval . --tag check --tag init --tag hook --runs 1 --ablation none --no-publish --scaffold
--allow-tools Write Edit --trust-plugin --max-cost-usd 1.5 -j 3`. `claude.exe` : `%APPDATA%/Claude/claude-code/2.1.271/`.
Sonde : bac à sable dans le scratchpad, `claude.exe -p … --output-format stream-json --verbose --add-dir <kit>
--max-budget-usd 0.5`, en arrière-plan ; lue par un script Python lancé avec `PYTHONUTF8=1`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `G1` | Établir quel shell lance hook, injection et outil | rien |
| `G2` | Corriger le hook ou écrire le prérequis | `G1` |

Rien n'est parallélisable : G2 choisit sa branche sur le tableau de G1.

---

<!-- FICHE:G1 -->
## G1 [x] — Établir quel shell lance hook, injection et outil

**Tentatives** (2026-09-17) — résolu par : simuler par la config (`shell: powershell` sur le hook et la skill) ; retirer Git du PATH ou fausser `CLAUDE_CODE_GIT_BASH_PATH` laisse l'outil Bash (Claude Code retrouve Git Bash).

**Dépend de** : rien.
**Fichiers** : `context AI/26-gitbash.md` (le tableau, sous cette fiche) — et rien d'autre dans le kit.

**Prompt**
Lis la doc Claude Code (WebFetch, pages « setup » Windows, « hooks », « settings » et l'outil PowerShell) et
réponds, citation courte à l'appui : Git Bash est-il obligatoire sous Windows ? par quel shell passent un hook
`type: command`, une injection `!`…`` d'une skill, l'outil Bash et l'outil PowerShell ? comment active-t-on
l'outil PowerShell seul (variable, réglage) ?
Puis sonde : bac à sable (git init, `CHANTIER.md` minimal, `ctx/`), session `-p` avec l'outil PowerShell seul
et le plugin chargé, qui écrit un fichier de fiches par `Write` et lance `/vlp:check`. Relève dans le stream-json :
la sortie du hook (`VALIDE` ou erreur), la carte injectée, le shell de chaque appel.
Écris sous cette fiche un tableau « mécanisme → shell utilisé → `sh` trouvé oui/non → source (doc ou sonde) ».
Outil PowerShell impossible à activer en `-p`, ou budget dépassé : arrête-toi et rends la main.

**Critère de fin**
Le tableau couvre 4 mécanismes (hook, injection, outil Bash, outil PowerShell), chacun avec sa source ; la sortie
brute du hook de la sonde et son coût (`sh scripts/vlp mesure <id>`) y sont recopiés.

**Constaté** (doc code.claude.com, `setup`, `hooks`, `skills` ; sondes `-p` 2.1.271, Git retiré du PATH) :

| Mécanisme | Shell sans Git Bash | `sh` trouvé | Source |
|---|---|---|---|
| hook `type: command`, forme shell | PowerShell — « or to "powershell" on Windows when Git Bash isn't installed » | non : `exit_code 1`, « sh n'est pas reconnu », **muet** pour le modèle | doc + sonde 3 (`shell: powershell`) |
| hook, forme exec (`command` + `args`) | aucun — exécutable lancé direct | sans objet : `python …/vlp.py hook` → `VALIDE 1 fiches` | doc + sonde 3 |
| injection `!`…`` | outil Bash s'il existe, sinon PowerShell | non : skill en échec avant tout tour, 0 $ | doc + sonde 2 (`shell: powershell`) |
| outil Bash | absent — « Git for Windows … optional » | — | doc `setup` |
| outil PowerShell | l'outil shell — « Claude Code uses PowerShell as the shell tool instead » | non (PATH sans Git) | doc + `Get-Command` |

`--disallowedTools Bash` ne bascule pas l'injection : « Permission to use Bash has been denied » (sonde 1). Sondes : 0,069 + 0,015 + 0 + 0 + 0,031 = 0,115 $.
<!-- /FICHE -->

---

<!-- FICHE:G2 -->
## G2 [x] — Corriger le hook ou écrire le prérequis

**Session** : 1e8a6fc3-8dc9-4781-8113-2575a81d15bb
**Dépend de** : `G1`.
**Fichiers** : `hooks/hooks.json`, `README.md`, `INSTALLATION.md`, `.claude-plugin/plugin.json` (version),
`scripts/test-vlp.py` si le hook change — et rien d'autre.

**Prompt**
Lis le tableau de G1. Deux branches :
- le hook échoue sans `sh` : fais-le tourner partout sans toucher aux skills (lanceur que PowerShell et Git Bash
  trouvent tous deux, sans `bash` — c'est WSL — ni `python3` — c'est le Store) ; plugin 3.3.4 ;
- le hook passe déjà (Git Bash imposé par Claude Code) : ne change aucun code.
Dans les deux cas, écris en une ligne dans `README.md` et `INSTALLATION.md` ce qu'exigent les commandes (Git Bash,
outil Bash), avec la citation de doc de G1. Une décision que le tableau ne tranche pas : rends la main.

**Critère de fin**
La sonde de G1 rejouée montre le hook `VALIDE <n> fiches` sans erreur ; `python scripts/test-vlp.py` passe (comptes
bruts), `claude.exe plugin validate` propre (1 avertissement voulu), evals 3/3 ; si le hook a changé, `sh scripts/vlp
renvois .` rend 0 absent.

**Constaté** : branche « documenter », tranchée par l'utilisateur — sans Git Bash les skills échouent de toute
façon (G1), aucun hook ne se réserve à un OS, `python` seul casse macOS/Linux ; le « tout compatible » part en TODO
n° 16. `INSTALLATION.md` n'existe plus : prérequis dans `README.md` seul. Hook du plugin inchangé, `VALIDE 1 fiches`
dans la sonde 3 ; `test-vlp.py` OK (59 assertions) ; `renvois` 52 nommés · 0 absent ; `validate` passé, 1 avertissement
voulu. Evals non rejouées : aucun fichier chargé par le plugin n'a changé.
<!-- /FICHE -->
