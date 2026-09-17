> **QUAND LIRE** : on joue une fiche `W*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache W<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier W — Evals sous WSL2

**CLOS** le 2026-09-17. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**À quoi il sert.** Les cas d'eval `tache` et `chantier` (tag `wsl2`) exigent l'outil Bash, que `claude plugin eval`
refuse sous Windows faute de sandbox (V2). On prépare Ubuntu sous WSL2 et on les joue depuis Linux.

**Fait.** W1 et W2 (2026-09-17) : Ubuntu prêt, `chantier` 3/3 et `tache` 3/3 sous Linux, 0,67 $ d'evals.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17) :

| Où | Ce qui s'y joue |
|---|---|
| `evals/tache/`, `evals/chantier/` | `case.yaml` (tags `[<nom>, wsl2]`, `max_turns` 12, `allowed_tools` avec `Bash`), `prompt.md`, `fixture.sh` (`#!/bin/bash`, bac à sable) |
| `evals/check/`, `init/`, `hook/` | la suite Windows, 3/3 — hors chantier |
| `context AI/18-evals.md`, fiche V2 | l'échec Windows : `sandbox required but unavailable: … the Windows sandbox is not active`, 0,00 $ |
| `wsl.exe -l -v` (cadrage) | une seule distribution : `docker-desktop`, arrêtée, WSL 2 — **pas d'Ubuntu** |

**Frontière** (tranchée au cadrage) : dedans, Ubuntu prêt et les deux cas `wsl2` joués et lus ; une fixture ou un
grader corrigé si le cas casse pour une raison de cas. Dehors : l'eval `init` (reste sous Windows), le kit sans `sh`
(TODO n° 16), toute modification des skills pour faire passer un cas — un échec de skill se note, il ne se corrige
pas ici.

**Gestes réservés à l'utilisateur** : installer la distribution, créer son compte Linux (mot de passe), connecter
Claude Code dans Linux. La session prépare les commandes, ne les tape pas à sa place.

**Lancer depuis Linux** : `claude plugin eval <kit> --tag wsl2 --runs 1 --ablation none --no-publish --scaffold
--allow-tools Read Glob Grep Skill Bash --trust-plugin --max-cost-usd 3 -j 2`, lancé par
`wsl.exe -d Ubuntu -- bash -lc "…"`. `<kit>` vu de Linux : `/mnt/c/Users/znorr/Documents/ProgPerso/Claude-vlpWorkflow`.
Plafond du chantier : **3 $** d'evals en tout ; au-delà, la fiche s'arrête. Coût et tours : `costUsd` et `turns` de
`aggregate-result.json`, sous `evals/results/<date>/` (ignoré par git).

**Outils de preuve Windows** (inchangés) : `sh scripts/vlp valider`, `python scripts/test-vlp.py`,
`claude.exe plugin validate .` (1 avertissement voulu) ; `claude.exe` : `%APPDATA%/Claude/claude-code/2.1.271/`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `W1` | Préparer Ubuntu sous WSL2 | rien |
| `W2` | Jouer les cas `wsl2` sous Linux | `W1` |

Rien n'est parallélisable : W2 exige la distribution de W1.

---

<!-- FICHE:W1 -->
## W1 [x] — Préparer Ubuntu sous WSL2

**Dépend de** : rien.
**Fichiers** : `context AI/27-wsl.md` (le relevé, sous cette fiche) — et rien d'autre dans le kit.

**Prompt**
Écris sous cette fiche, en bloc de code, les commandes que l'utilisateur tape, dans l'ordre : installer la
distribution (`wsl --install -d Ubuntu`), créer son compte au premier lancement, installer Claude Code (méthode
Linux de la doc code.claude.com, `setup`), `bubblewrap` et `socat` (prérequis de la sandbox Linux, doc
`sandboxing`), puis lancer `claude` une fois pour se connecter. Cite en une ligne la doc de chaque prérequis.
Rends la main : ces gestes sont les siens. À son retour, relève par script la version de chaque outil.

**Critère de fin** (visuel)
L'utilisateur dit Ubuntu installé et Claude Code connecté ; puis `wsl.exe -d Ubuntu -- bash -lc "claude --version;
bwrap --version; socat -V | head -1"` rend trois versions, recopiées ici.

**Constaté** (2026-09-17, Ubuntu 26.04.1 LTS) : `2.1.274 (Claude Code)` · `bubblewrap 0.11.1` · `socat version 1.8.1.1` ;
`claude auth status` → `"loggedIn": true`, `claude.ai`. AppArmor : clé `sysctl` absente, rien à faire. Piège : `claude: command not
found` dans le terminal ouvert avant l'installation — `exec bash -l`.

**Les gestes** (doc lue le 2026-09-17) — `setup` : « WSL 2 … Sandboxing Supported », « WSL 1 … Not supported » ;
installeur Linux `curl -fsSL https://claude.ai/install.sh | bash`, « You install and launch `claude` inside the WSL
terminal ». `sandboxing` : « On Linux and WSL2, the sandbox relies on two packages » (`bubblewrap`, `socat`) ;
sous Ubuntu 24.04+, AppArmor peut bloquer `bwrap` (`sysctl kernel.apparmor_restrict_unprivileged_userns` = 1).

```
wsl --install -d Ubuntu                       # PowerShell ; au 1er lancement : nom d'utilisateur + mot de passe
sudo apt-get update && sudo apt-get install -y bubblewrap socat    # dans Ubuntu, la suite aussi
curl -fsSL https://claude.ai/install.sh | bash
sysctl kernel.apparmor_restrict_unprivileged_userns                # 1 : profil bwrap de la doc sandboxing
claude                                        # se connecter (navigateur), puis /exit
```
<!-- /FICHE -->

---

<!-- FICHE:W2 -->
## W2 [x] — Jouer les cas `wsl2` sous Linux

**Session** : 20b6f6d2-b753-45d0-9f79-4e0e0aa0deed
**Dépend de** : `W1`.
**Fichiers** : `evals/tache/`, `evals/chantier/`, `context AI/27-wsl.md` (le relevé) — et rien d'autre.

**Prompt**
Lance la suite `wsl2` depuis Linux, avec la commande du socle. Lis `aggregate-result.json` : par cas, graders
passés sur graders, `turns`, `costUsd`. Un cas qui échoue : lis sa trace (`--keep-temp` au rejeu) et classe la
cause — sandbox ou outil absent (environnement), fixture ou grader faux (cas : corrige-le, rejoue une fois),
skill qui se trompe (kit : note-le, ne corrige pas). Écris sous cette fiche un tableau « cas → graders → tours →
coût → cause ». Plafond de 3 $ atteint, ou deux lancements ratés : arrête-toi et rends la main.

**Critère de fin**
Le tableau couvre `tache` et `chantier` avec leurs comptes bruts (graders, tours, coût) lus dans
`aggregate-result.json` ; coût total des lancements ≤ 3 $ ; `python scripts/test-vlp.py` OK et
`claude.exe plugin validate .` propre (1 avertissement voulu) si un cas a changé.

**Constaté** (2026-09-17, `claude plugin eval` 2.1.274 sous Ubuntu, plugin 3.3.3 lu sur `/mnt/c`) :

| Cas | Lancement | Graders | Tours | Coût | Cause |
|---|---|---|---|---|---|
| `chantier` | 1 | 3/3 | 5 | 0,27 $ | — |
| `tache` | 1 | 2/3 (`CITRON-T2` absent) | 4 | 0,20 $ | **cas** : la fixture faisait dépendre T2 de T1 non cochée ; la skill a demandé, comme elle le doit |
| `tache` | 2, fixture corrigée | 3/3 | 4 | 0,20 $ | — |

Evals : 0,47 + 0,20 = **0,67 $** sur 3 $. `test-vlp.py` OK ; `validate` passé, 1 avertissement voulu. Bruit sans effet :
`/bin/bash: …/home/.bashrc: Permission denied` à chaque appel Bash du run (home scellé). Dossiers gardés par
`--keep-temp` : `/tmp/claude-eval-A8kD9X`, `/tmp/claude-eval-cA3EVT` (dans Ubuntu).
<!-- /FICHE -->
