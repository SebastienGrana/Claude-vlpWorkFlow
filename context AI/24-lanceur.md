> **QUAND LIRE** : on joue une fiche `P*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache P<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier P — Un lanceur Python sans accolade

**À quoi il sert.** En `-p`, le motif `PY=$(for p in python3 python; …)` est refusé (« Contains brace with quote
character ») et coûte des tours. Un seul lanceur `scripts/vlp` choisit le Python ; toutes les commandes l'appellent.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 3 fiches, `P1` à jouer.

## Le socle commun

**Ce qui existe** (compté au cadrage, le 2026-09-17) :

| Où | Forme | Nombre |
|---|---|---|
| `skills/{tache,enchainer}/SKILL.md` | `PY=$(for p in python3 python; …)` | 2 + 2 |
| `skills/{chantier,check,init,jouer}/SKILL.md`, `cloture.md`, `hooks/hooks.json` | même motif | 1 chacun (6) |
| `skills/{chantier,tache,enchainer,jouer}/SKILL.md` | `` !`python3 … carte 2>/dev/null \|\| python … carte` `` | 4 |
| `skills/{chantier,tache}/SKILL.md` | `python "…/vlp.py" carte "<dossier>"` en prose | 2 |
| `allowed-tools` des six skills | `Bash(python3:*), Bash(python:*)` | 6 |

Sur la machine : `python3` = faux raccourci du Store (WindowsApps, exit 49), `python` et `py` = 3.14.6.

**Le nom retenu** : `scripts/vlp`, script `sh` sans dépendance, qui essaie `python3`, `python`, `py` (dans cet
ordre, chacun testé par `-c ""`), puis `exec` le premier sur `vlp.py` avec tous les arguments ; aucun → message
sur stderr, exit 127. Appel : `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" <sous-commande> …`. La détection vit là, seule.

**Invariants.** Un script ne s'exécute qu'une fois (pas de `||` qui relance sur échec du script). Le code de sortie
de `vlp.py` traverse le lanceur (`exec`). Pas de `disable-model-invocation`. `mesure-tokens.py` hors lanceur.

**Outils de preuve** : `vlp.py valider`, `vlp.py renvois` (0 absent), `claude.exe plugin validate .` puis
`validate .claude-plugin/plugin.json` (1 avertissement voulu), evals Windows : `claude.exe plugin eval . --tag check
--tag init --tag hook --runs 1 --ablation none --no-publish --scaffold --allow-tools Write Edit --trust-plugin
--max-cost-usd 1.5 -j 3`. `claude.exe` : `%APPDATA%/Claude/claude-code/2.1.271/`.

**La sonde** : bac à sable du scratchpad (git init, `CHANTIER.md`, fichier de fiches, page par `page --creer`),
`claude.exe -p … --output-format stream-json --verbose --permission-mode acceptEdits --add-dir <kit>
--max-budget-usd 0.5` ; transcripts copiés par `cp` avant `mesure-tokens.py`. **Plafond du chantier : 2 $ de sondes.**

**Avant, mesuré en L3** (journal de `08-etat.md`) : le motif refusé coûte 1 tour au chef, 2 à 3 tours par
sous-agent, qui retombe sur `python3` (exit 49).

**Dehors** : WSL2 (TODO n° 11) ; `mesure-tokens.py` ; le contenu des fiches jouées par le sous-agent.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `P1` | Sonder les formes, écrire le lanceur | rien |
| `P2` | Remplacer partout | `P1` |
| `P3` | Prouver de bout en bout, et livrer | `P2` |

Strictement en série : P2 applique la forme que P1 a prouvée, P3 mesure ce que P2 a posé.

---

<!-- FICHE:P1 -->
## P1 [x] — Sonder les formes, écrire le lanceur

**Dépend de** : rien.
**Fichiers** : `scripts/vlp` (neuf), `scripts/test-vlp.py` (un test du lanceur),
`hooks/hooks.json`, `context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
Écris `scripts/vlp` comme dit le socle, sans accolade dans ce qu'une commande tapera. Teste-le :
`sh scripts/vlp valider "context AI/24-lanceur.md"` rend `VALIDE` et exit 0 ; une fiche cassée rend exit ≠ 0 ;
`PATH` réduit sans Python → exit 127 et message.
Puis mesure, dans un bac à sable, trois cas en `-p` (un lancement court chacun, `Réponds par la sortie`) :
(a) l'ancien motif, (b) `sh "<kit>/scripts/vlp" carte`, avec `--allowedTools "Bash(sh:*)"` puis sans ; note
refus ou passage, tours, coût. En session interactive (celle-ci) : lance l'ancien motif par l'outil Bash et note
s'il passe, demande permission, ou est refusé.
Pour PowerShell sans Git Bash : lance le hook (`hooks/hooks.json`, forme `sh`) sous `pwsh -c` en substituant le
chemin, et note ce qui arrive (`sh` introuvable ?). Ne change pas `hooks.json` ici.
Écris une ligne au journal de `08-etat.md` avec les comptes bruts.

**Critère de fin**
`sh scripts/vlp valider "context AI/24-lanceur.md"; echo $?` → `VALIDE 3 fiches …` puis `0` ; le journal porte
les trois mesures `-p` (refus/passage, tours, $), la mesure interactive et la mesure PowerShell.
<!-- /FICHE -->

---

<!-- FICHE:P2 -->
## P2 [x] — Remplacer partout

**Dépend de** : `P1`.
**Fichiers** : `skills/{tache,enchainer,chantier,check,init,jouer}/SKILL.md`, `cloture.md`, `hooks/hooks.json`,
`.claude-plugin/plugin.json` — et rien d'autre.

**Prompt**
Remplace les formes du socle par l'appel au lanceur, dans la forme que P1 a prouvée (journal de `08-etat.md`) :
les 12 motifs `PY=$(…)` (un `"$PY" X` devient `sh "…/scripts/vlp" X`), les 4 injections de carte, les 2 renvois
en prose. Dans `skills/jouer`, `<kit>` reste `<kit>`. Ajuste `allowed-tools` (`Bash(sh:*)` ; retire
`python3`/`python` si plus rien ne les appelle). Aucune autre retouche de prose.
Écris par un script Python du scratchpad qui compte chaque motif avant de remplacer (CRLF), puis relance
`vlp.py renvois`. Passe le plugin en 3.3.2. `/reload-plugins` est un geste utilisateur : ne le demande pas,
P3 le prouvera en `-p`.

**Critère de fin**
`grep -rc "for p in python3\|python3 \"" skills cloture.md hooks` → 0 partout ; `grep -rc "scripts/vlp\"" skills
cloture.md hooks` → comptes bruts affichés (≥ 18) ; `vlp.py renvois` 0 absent ; `claude.exe plugin validate .` passe
(1 avertissement voulu).
<!-- /FICHE -->

---

<!-- FICHE:P3 -->
## P3 [x] — Prouver de bout en bout, et livrer

**Session** : b59e04ab-d2e0-4f45-bbf7-669a63809773
**Dépend de** : `P2`.
**Fichiers** : le bac à sable du scratchpad, `context AI/08-etat.md` (journal, TODO n° 13) — et rien d'autre.

**Prompt**
Rejoue en `-p` sur un bac à sable neuf (deux fiches triviales) `/vlp:enchainer`, comme la sonde de L3, et
compte : refus « brace », exit 49, tours du chef, tours de chaque sous-agent (`subagents/agent-*.jsonl`), $.
Compare aux chiffres de L3 (chef 9 tours / 7 appels, sous-agents 9 et 6). Si un refus subsiste, trouve la
ligne et corrige-la (retour à P2 pour ce seul point).
Lance les evals (socle) en arrière-plan pendant la sonde. Écris au journal les comptes bruts avant/après et
retire la TODO n° 13 de la table.

**Critère de fin**
Transcripts de la sonde : `grep -c "Contains brace"` → 0, `grep -c "exit code 49\|Exit code 49"` → 0 ;
`aggregate-result.json` → 3/3 passés ; tours chef/sous-agents et $ au journal, à côté de ceux de L3.
<!-- /FICHE -->
