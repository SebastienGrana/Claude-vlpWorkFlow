> **QUAND LIRE** : on joue une fiche `X*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache X<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier X — Le kit sans `sh` : sonder puis trancher

**À quoi il sert.** Sans Git Bash, le hook `sh` se tait et les skills à `!`sh …`` échouent (G1). On mesure, sous
Windows et sous Ubuntu, s'il existe un lancement de Python sans `sh` qui passe partout ; puis on l'applique ou on renonce.

**CLOS** le 2026-09-17. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** X1, X2, X3 (2026-09-17) : hook et carte sans `sh` sondés sous Windows et Ubuntu ; X3 tranchée « renoncer » — rien d'appliqué, recette dans la TODO n° 16.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17) :

| Où | Ce qui s'y joue |
|---|---|
| `hooks/hooks.json` | `PostToolUse` `Write\|Edit`, forme shell : `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" hook` |
| `skills/{chantier,enchainer,jouer,tache}/SKILL.md` | une injection chacune : `!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" carte`` |
| `scripts/vlp` | lanceur `sh` : premier de `python3`, `python`, `py` qui répond à `-c ""` |
| `context AI/26-gitbash.md`, fiche G1 | le tableau « mécanisme → shell sans Git Bash » : hook forme shell → PowerShell, `exit_code 1`, muet ; forme exec (`command` + `args`) → sans shell, `python …/vlp.py hook` passe ; injection → skill en échec avant tout tour, 0 $ |

**Frontière** (tranchée au cadrage) : dedans, le hook et les 4 injections de carte. Dehors : les 17 appels `sh` du
corps des skills et de `cloture.md`, les `Bash(sh:*)` des allowed-tools, `scripts/vlp` lui-même.

**Contraintes connues** (G2, doc) : aucun champ `os`/`platform` de hook ; PowerShell 5.1 ignore `||` (pwsh 7 l'a) ;
sous Windows `python3` est souvent le raccourci du Store ; `python` peut manquer sous macOS/Linux ; sous PowerShell
`bash` est WSL, jamais un remplaçant de `sh`. Un résultat non mesuré ne s'écrit pas : la fiche note « non sondé ».

**Simuler et prouver** :
- Windows sans Git : `shell: powershell` sur un hook (`.claude/settings.json` d'un bac à sable du scratchpad) ou dans
  le frontmatter d'une skill de bac (`.claude/skills/<nom>/SKILL.md`, lancée par `-p "/<nom>"`) ;
- Ubuntu : le même bac lancé par `wsl.exe -d Ubuntu -- bash -lc '…' | tr -d '\0'` (`claude` 2.1.274, `python3`) ;
- preuve d'un hook : `claude -p … --output-format stream-json --verbose --include-hook-events` → `hook_response`
  (`stdout`, `stderr`, `exit_code`) ; preuve d'une injection : le texte de la carte dans le premier message, ou l'échec ;
- sondes en `--model haiku --max-budget-usd 0.3` ; coût = `total_cost_usd` de la dernière ligne. Plafond : 1 $ de
  sondes par fiche ; au-delà, la fiche s'arrête.

**Outils de preuve** : `sh scripts/vlp valider <fichier>`, `python scripts/test-vlp.py` (« OK »), `sh scripts/vlp
renvois .`, `claude.exe plugin validate .` (1 avertissement voulu) — `claude.exe` sous `%APPDATA%/Claude/claude-code/<version>/`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `X1` | Sonder le hook sans `sh` | rien |
| `X2` | Sonder la carte injectée sans `sh` | `X1` |
| `X3` | Appliquer ou renoncer | `X1`, `X2` |

X2 reprend les candidats de X1 ; X3 ne tranche que sur leurs deux tableaux.

---

<!-- FICHE:X1 -->
## X1 [x] — Sonder le hook sans `sh`

**Dépend de** : rien.
**Fichiers** : `context AI/28-sans-sh.md` (le tableau, sous cette fiche) ; un bac à sable dans le scratchpad — rien
d'autre dans le kit.

**Prompt**
Relève dans la doc des hooks (code.claude.com, `hooks` : forme exec, `shell`, code de sortie non bloquant) les formes
utiles, puis sonde au moins ces candidats pour un hook `PostToolUse` qui lance `vlp.py hook` sur un fichier de fiches
écrit par `Write` : forme exec `python3`, `python`, `py` ; forme shell `python "<kit>/scripts/vlp.py" hook` ; deux
hooks exec côte à côte (`python3` et `py`), dont l'un échoue sans bruit. Chacun sous Windows `shell: powershell` et
sous Ubuntu. Note aussi ce que voit le modèle quand un des deux hooks échoue, et si `VALIDE` sort deux fois.

**Critère de fin**
Sous cette fiche, un tableau candidat × système (Windows PowerShell, Ubuntu) → `exit_code`, `stdout` brut
(`VALIDE <n> fiches` ou erreur), source (doc ou sonde) ; au moins 5 candidats, chacun sur les 2 systèmes ; coût
total des sondes recopié.

**Constaté** (2026-09-17, `claude -p --model haiku --include-hook-events`, Windows 2.1.271, Ubuntu 2.1.274) — présents :
Windows `python` (3.14), `py`, `python3` = raccourci du Store, pwsh 7.6.6 ; Ubuntu `python3` seul. Doc `hooks` : exec
« resolves `command` as an executable on `PATH` », `${CLAUDE_PLUGIN_ROOT}` substitué dans `args`, `shell` ignoré.

| Candidat | Windows (`shell: powershell` pour la forme shell) | Ubuntu | Source |
|---|---|---|---|
| exec `python3` | `exit_code 49`, stderr « Python est introuvable ; exécutez sans arguments… Store » | `0`, `VALIDE 1 fiches` | sonde |
| exec `python` | `0`, `VALIDE 1 fiches` | `1`, « Executable not found in $PATH: "python" » | sonde |
| exec `py` | `0`, `VALIDE 1 fiches` | `1`, « Executable not found in $PATH: "py" » | sonde |
| shell `python "<kit>/scripts/vlp.py" hook` | `0`, `VALIDE 1 fiches` | `127`, « /bin/sh: 1: python: not found » | sonde |
| paire exec `python3` + `py` | `49` (python3) puis `0` `VALIDE` (py) | `1` (py) puis `0` `VALIDE` (python3) | sonde |

Aucun candidat seul ne passe les 2 systèmes ; la paire `python3` + `py` passe les deux, une erreur non bloquante de
chaque côté. Ce que voit le modèle : un hook en échec seul → « AUCUN » (muet) ; la paire → `VALIDE` une fois. Double
`VALIDE` si `python3` et `py` sont vrais tous deux (Windows avec Python du Store) : non sondé, ni macOS. Sous Windows
chaque sonde a une réponse `0 VALIDE` de plus : le hook `sh` du plugin vlp, chargé en `-p` (Git Bash présent).
Sondes : 10 × 2 tours, 0,313 $.
<!-- /FICHE -->

---

<!-- FICHE:X2 -->
## X2 [x] — Sonder la carte injectée sans `sh`

**Dépend de** : `X1`.
**Fichiers** : `context AI/28-sans-sh.md` (le tableau, sous cette fiche) ; un bac à sable dans le scratchpad — rien
d'autre dans le kit.

**Prompt**
Lis le tableau de X1. Dans une skill de bac, sonde une injection `!`…`` qui lance `vlp.py carte` sans `sh` : les
candidats de X1 qui passaient, plus `python3 … carte; python … carte` (deux commandes, une en échec) et `python3 …
carte || python … carte`. Chacun sous Windows `shell: powershell` (dis si c'est pwsh 7 ou powershell.exe 5.1) et sous
Ubuntu. Mesure surtout si une injection dont une commande échoue (code non nul, stderr) fait échouer la skill.

**Critère de fin**
Sous cette fiche, un tableau candidat × système → skill lancée oui/non, carte présente (`PROJET=` lu dans le premier
message) oui/non, message d'erreur brut ; au moins 4 candidats, chacun sur les 2 systèmes ; coût total recopié.

**Constaté** (2026-09-17, skill de bac `-p "/sonde" --model haiku --permission-mode bypassPermissions`, texte
injecté relu dans le transcript) — Windows `shell: powershell` = **pwsh 7.6.6**, même pwsh ôté du PATH (`w51`) ;
Ubuntu = `/bin/bash`. Hors Claude : `powershell.exe` 5.1 refuse `||` (« Le jeton « || » n'est pas un séparateur
d'instruction valide », exit 1) ; une injection sous 5.1 : non sondé.

| Candidat | Windows (pwsh 7) | Ubuntu | Source |
|---|---|---|---|
| `python3 … carte` | skill non lancée, 0 tour, « Shell command failed … Python est introuvable … Store » | lancée, `PROJET=` oui | sonde |
| `python … carte` | lancée, `PROJET=` oui | non lancée, « /bin/bash: line 1: python: command not found » | sonde |
| `py … carte` | lancée, `PROJET=` oui | non lancée, « py: command not found » | sonde |
| `python3 … carte; python … carte` | lancée, `PROJET=` **collé** derrière le message du Store (pas en début de ligne) | non lancée, « Shell command failed » (le 2e échoue, la carte était sortie) | sonde |
| `python3 … carte \|\| python … carte` | lancée, `PROJET=` oui, précédé du message du Store (même pwsh ôté du PATH) | lancée, `PROJET=` oui | sonde |
| deux injections `python3` puis `py` | non lancée, « Shell command failed » (python3) | non lancée, « py: command not found » | sonde |

Une injection dont la **dernière** commande sort en erreur fait échouer la skill avant tout tour (0 $) ; seul `||`
passe les 2 systèmes, avec le message du Store dans la carte sous Windows. Sondes : 13 + 10 relancées ; la
1re série Windows invalide (Git Bash a converti `"/sonde"` en `C:/Program Files/Git/sonde` : `MSYS_NO_PATHCONV=1`) ;
coût 0,266 $ + 0,178 $ = 0,443 $.
<!-- /FICHE -->

---

<!-- FICHE:X3 -->
## X3 [x] — Appliquer ou renoncer

**Session** : fd4ebe27-5975-4250-89c7-13c5e861cc33
**Dépend de** : `X1`, `X2`.
**Fichiers** : `hooks/hooks.json`, les 4 `skills/*/SKILL.md` du socle (ligne d'injection seule),
`.claude-plugin/plugin.json` (version), `scripts/test-vlp.py` si le hook change, `README.md` (prérequis),
`context AI/08-etat.md` (ligne n° 16 de la TODO) — et rien d'autre.

**Prompt**
Lis les tableaux de X1 et X2. Un candidat passe sur les 2 systèmes pour un mécanisme : applique-le à ce mécanisme
seulement, plugin 3.3.4, et écris dans `README.md` ce qui marche désormais sans Git Bash. Aucun ne passe : ne change
aucun code, écris la raison mesurée dans la ligne n° 16 (reformulée, ou retirée si rien ne reste à essayer). Un choix
que les tableaux ne tranchent pas (deux candidats, un compromis de tours) : rends la main.

**Critère de fin**
Branche « appliquer » : la sonde gagnante rejouée avec le plugin réel sous les 2 systèmes (sorties brutes) ;
`test-vlp.py` OK (nombre d'assertions) ; `validate` propre (1 avertissement voulu) ; `renvois .` 0 absent ; evals
`hook` sous Windows et `tache`, `chantier` sous Ubuntu passées. Branche « renoncer » : la ligne n° 16 citée, `git diff
--stat` sans fichier du plugin.

**Sonde complémentaire** (2026-09-17, décidée par l'utilisateur avant de trancher X3 ; même bac que X2, texte injecté
relu dans le transcript) — l'ordre inversé, sous 3 shells :

| Candidat | Windows pwsh 7 | Windows Git Bash (sans `shell`) | Ubuntu |
|---|---|---|---|
| `python … carte \|\| python3 … carte` | lancée, `PROJET=` en 1re ligne, sans message | lancée, `PROJET=` en 1re ligne, sans message | lancée, `PROJET=` oui, « /bin/bash: line 1: python: command not found » à part |
| `py … carte \|\| python3 … carte` | lancée, `PROJET=` en 1re ligne, sans message | lancée, `PROJET=` oui, sans message | lancée, `PROJET=` oui, « py: command not found » à part |

6 sondes, 0,141 $. Non sondé : un Windows sans `py` ni `python` réel (Python du Store seul), PowerShell 5.1, macOS.

**Constaté** : branche « renoncer », tranchée par l'utilisateur — appliquer n'apporte rien de visible (tous les postes qui font tourner le kit ont `sh` ; sans Git, les 17 appels `sh` du corps échouent encore), et coûte le bruit du hook double, des allowed-tools non sondés et une version poussée au groupe. Ligne n° 16 de `08-etat.md` reformulée avec la recette ; `git diff --stat` : `08-etat.md`, `28-sans-sh.md`, aucun fichier du plugin. Sondes du chantier : 0,313 + 0,443 + 0,141 = 0,897 $.
<!-- /FICHE -->
