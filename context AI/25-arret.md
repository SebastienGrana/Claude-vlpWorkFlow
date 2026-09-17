> **QUAND LIRE** : on joue une fiche `A*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache A<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier A — Une fiche visuelle arrête `/vlp:enchainer`

**À quoi il sert.** Mesuré en P3 : le sous-agent `vlp:fiche` a rendu `FAITE` sur une fiche `(visuel)`, et le chef a
continué jusqu'à la clôture (TODO n° 14). Deux verrous : le chef traite toute `(visuel)` en `RETOUR`, et le script
marque la fiche extraite.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 2 fiches, `A1` à jouer.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17) :

| Où | Ce qui s'y joue |
|---|---|
| `scripts/vlp.py` `extraire_lignes`, `cmd_extraire` | rend la fiche entre marqueurs, puis `--- fiche, lignes : N` |
| `scripts/vlp.py` `CRITERE_VISUEL` | `^\*\*Critère de fin\*\* \(visuel\)` — la marque, reconnue par `valider` |
| `skills/jouer/SKILL.md` | injecte la carte ; le sous-agent lance `socle` puis `extraire` ; une ligne `GARDE:` → `RETOUR` |
| `agents/fiche.md` étape 3 | « Critère `(visuel)` ou geste humain : rends `RETOUR` » — ignoré par Haiku en P3 |
| `skills/enchainer/SKILL.md` étape 2 | la série s'arrête à la première `(visuel)`, incluse — le chef la connaît |
| `skills/enchainer/SKILL.md` étape 3.2 | `FAITE` → fiche suivante, puis carte ; `PROCHAINE=aucune` → clôture |
| `enchainement.md` | le contrat `FAITE` / `RETOUR` / `BLOQUÉE`, qui fait foi |

**Le verrou retenu.** (1) `vlp.py extraire` ajoute, sur une fiche `(visuel)`, une ligne commençant par `ARRÊT:` — pas
`GARDE:`, que `vlp:jouer` traite en `RETOUR` avant tout travail. La fiche se joue, puis s'arrête sans cocher.
(2) Le chef : une fiche `(visuel)` vaut `RETOUR` quel que soit le statut rendu ; case cochée par le sous-agent →
remise à `[ ]` avant la question. Il ne clôt jamais sur une `(visuel)` sans réponse.

**Avant, mesuré en P3** (journal de `08-etat.md`) : Z2 `(visuel)` rendue `FAITE` ; chef 14 tours, 19 appels dont
15 pour une clôture, 0,38 $ ; sous-agents 8 et 6 tours ; sonde entière 0,45 $.

**Outils de preuve** : `sh scripts/vlp valider`, `sh scripts/vlp renvois` (0 absent), `python scripts/test-vlp.py`,
`claude.exe plugin validate .` puis `validate .claude-plugin/plugin.json` (1 avertissement voulu), evals Windows :
`claude.exe plugin eval . --tag check --tag init --tag hook --runs 1 --ablation none --no-publish --scaffold
--allow-tools Write Edit --trust-plugin --max-cost-usd 1.5 -j 3`. `claude.exe` : `%APPDATA%/Claude/claude-code/2.1.271/`.

**La sonde** : bac à sable du scratchpad (git init, `CHANTIER.md`, fichier de fiches Z1 scriptable + Z2 `(visuel)`,
page par `page --creer`), `claude.exe -p "/vlp:enchainer" --output-format stream-json --verbose --permission-mode
acceptEdits --add-dir <kit> --allowedTools Skill "Bash(sh:*)" --max-budget-usd 0.5` ; transcripts copiés par `cp`
avant `sh scripts/vlp mesure`. **Plafond du chantier : 1 $ de sondes.**

**Dehors** : `/vlp:tache` (l'humain y est présent) ; WSL2 (TODO n° 11) ; la publication de la page dans la sonde.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `A1` | Poser les deux verrous | rien |
| `A2` | Prouver l'arrêt en `-p`, et livrer | `A1` |

En série : A2 mesure ce que A1 a posé.

---

<!-- FICHE:A1 -->
## A1 [ ] — Poser les deux verrous

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `skills/enchainer/SKILL.md`, `agents/fiche.md`,
`enchainement.md`, `.claude-plugin/plugin.json` — et rien d'autre.

**Prompt**
Compte d'abord, et note : `grep -c "visuel" agents/fiche.md enchainement.md skills/enchainer/SKILL.md`.
Dans `vlp.py`, `cmd_extraire` : si une ligne de la fiche extraite répond à `CRITERE_VISUEL`, écris après la fiche,
avant `--- fiche, lignes`, une ligne `ARRÊT: critère de fin (visuel) — livre, puis rends RETOUR sans cocher`. Rien
sur une fiche scriptable. Deux tests dans `test-vlp.py` (avec, sans). Mets la docstring à jour d'une ligne.
`agents/fiche.md` : la règle devient une phrase à part, en tête des étapes : une ligne `ARRÊT:` → jamais `FAITE`.
`enchainement.md` : une ligne — `FAITE` sur une fiche `(visuel)` vaut `RETOUR`.
`skills/enchainer/SKILL.md` étape 3.2 : sur la fiche `(visuel)` de l'étape 2, tout statut est un `RETOUR` ; si la
case est cochée, remets-la à `[ ]` (une ligne), puis étape 3 bis. Court : chaque mot se paye à chaque lancement.
Plugin 3.3.3.

**Critère de fin**
`python scripts/test-vlp.py` → `OK` (comptes de cas avant/après) ; `sh scripts/vlp extraire "context AI/24-lanceur.md" P3`
sans `ARRÊT:`, et sur une fiche `(visuel)` de test avec ; le `grep -c "visuel"` avant/après affiché ;
`sh scripts/vlp renvois` 0 absent ; `claude.exe plugin validate .` passe (1 avertissement voulu).
<!-- /FICHE -->

---

<!-- FICHE:A2 -->
## A2 [ ] — Prouver l'arrêt en `-p`, et livrer

**Dépend de** : `A1`.
**Fichiers** : le bac à sable du scratchpad, `context AI/08-etat.md` (journal, TODO n° 14) — et rien d'autre.

**Prompt**
Rejoue la sonde du socle (Z1 scriptable, Z2 `(visuel)`), comme en P3. Compte dans les transcripts : statut rendu
par chaque sous-agent (`subagents/agent-*.jsonl`), présence d'une ligne `ARRÊT:` dans celui de Z2, case de Z2 dans
le fichier de fiches du bac après la sonde, appels de clôture du chef (écritures de `CHANTIER.md`, en-tête
`**CLOS**`), tours et $ du chef et des sous-agents. Compare à P3 (socle). Si le chef clôt encore, trouve la ligne
qui l'y mène et corrige-la (retour à A1 pour ce seul point), une seconde sonde au plus.
Lance les evals en arrière-plan pendant la sonde. Écris au journal les comptes bruts avant/après et retire la
TODO n° 14 de la table.

**Critère de fin**
Bac après sonde : `grep -c "^## Z2 \[ \]"` → 1 ; `grep -c "CLOS"` sur son fichier de fiches → 0 ; transcript du chef :
question posée sur Z2 ; tours chef/sous-agents et $ au journal à côté de ceux de P3 ; `aggregate-result.json` → 3/3.
<!-- /FICHE -->
