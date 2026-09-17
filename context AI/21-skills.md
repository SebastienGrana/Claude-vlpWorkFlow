> **QUAND LIRE** : on joue une fiche `K*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache K<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier K — Migrer `commands/` → `skills/`

**À quoi il sert.** Les cinq commandes du kit vivent en `commands/*.md`, forme que la doc
des plugins garde pour l'existant (« Use `skills/` for new plugins ») ; K les passe en
`skills/<nom>/SKILL.md`, un dossier par commande avec ses références (TODO n° 8).

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 3 fiches, `K1` à jouer.

## Le socle commun

**Résultat visible.** `commands/` n'existe plus ; `skills/` porte `init`, `chantier`,
`tache`, `enchainer`, `check` ; la suite d'evals Windows passe 3/3 ; `claude plugin
validate .` sans avertissement nouveau ; `vlp.py renvois .` à 0 absent.

**L'existant, mesuré au cadrage** (`wc -l`) :

| Fichier | Lignes | Lu par |
|---|---|---|
| `commands/chantier.md` | 273 | `/vlp:chantier` |
| `commands/check.md` | 130 | `/vlp:check` |
| `commands/enchainer.md` | 145 | `/vlp:enchainer` |
| `commands/init.md` | 181 | `/vlp:init` |
| `commands/tache.md` | 151 | `/vlp:tache` |
| `references/tache-{blocage,contraintes,page}.md` | 35, 8, 30 | `tache.md:63,107`, `enchainer.md:127,133`, `agents/fiche.md:18` |

Le kit est la racine du plugin (`.claude-plugin/plugin.json`, v3.1.0), chargé par le
lien `~/.claude/skills/vlp`. Le frontmatter garde `description`, `argument-hint`,
`allowed-tools` ; le corps garde `$ARGUMENTS`, `` !`…` `` et `${CLAUDE_PLUGIN_ROOT}` —
qu'ils marchent dans un `SKILL.md` de plugin est **l'inconnue de K1**, à prouver par un
run, pas à supposer. Doc : https://code.claude.com/docs/en/skills et
https://code.claude.com/docs/en/plugins-reference.

**Prouver sans `/reload-plugins`** : un run d'eval recharge le plugin à neuf. `claude`
n'est pas dans le PATH : `"$APPDATA/Claude/claude-code/2.1.271/claude.exe"`. La commande
de la suite Windows est écrite une fois, dans `context AI/18-evals.md` (« Lancer —
toujours ainsi ») ; une seule eval = un seul `--tag`. Coût, tours et score :
`aggregate-result.json` sous `evals/results/`. Plafond : `--max-cost-usd 1.5` par lancement.

**Renvois à repérer** — avant/après par
`grep -rn "commands/\|references/" --include=*.md --include=*.json --include=*.py . | grep -v "context AI/\|archive/\|exemples/\|\.git/"`
(17 lignes au cadrage). Les mentions de `~/.claude/commands/` (copie simple hors plugin,
`chantier.md:161`, `init.md:50`, `check.md:95,107`) décrivent un repli et **restent**.

**Dehors.** `context: fork` + `agent: vlp:fiche` (chantier N, TODO n° 9) ; les cas
`tache` et `chantier` (tag `wsl2`, TODO n° 11) ; les projets équipés (rien n'y vit de
`commands/`) ; `archive/` et `exemples/`, archives. `disable-model-invocation` se
**mesure** en K1 et ne se pose que s'il laisse passer l'appel par l'outil `Skill`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `K1` | Migrer `check` en skill pilote, mesurer `disable-model-invocation` | rien |
| `K2` | Migrer les quatre autres commandes et `references/` | `K1` |
| `K3` | Mettre les renvois de la doc à jour | `K2` |

Rien n'est parallélisable : K1 prouve la forme que K2 recopie, K3 décrit ce que K2 a posé.

---

<!-- FICHE:K1 -->
## K1 [ ] — Migrer `check` en skill pilote, mesurer `disable-model-invocation`

**Dépend de** : rien.
**Fichiers** : `commands/check.md` → `skills/check/SKILL.md`, `evals/check/`, `context AI/08-etat.md` (journal).

**Prompt**
Déplace `commands/check.md` par `git mv` vers `skills/check/SKILL.md`, contenu inchangé
sauf ce que la doc des skills exige (lis-la d'abord). Lance l'eval `check` seule : elle
dit si la skill se charge, si `` !`…` `` et `${CLAUDE_PLUGIN_ROOT}` y sont substitués
(regarde la trace avec `--keep-temp` si le score n'est pas 1). Puis ajoute
`disable-model-invocation: true` au frontmatter et rejoue la même eval : garde-le si le
score reste 1 et que le grader `runs-vlp-check-command` passe, retire-le sinon — le
verdict vaut pour les quatre autres en K2. Lance `claude plugin validate .`.
Écris une ligne de journal : substitutions constatées, les deux scores, tours et coût,
le choix sur `disable-model-invocation`.

**Critère de fin**
`ls commands/check.md skills/check/SKILL.md` : le premier absent, le second présent ;
l'eval `check` finale score 1 (tours et `costUsd` affichés) ; `validate` : même nombre
d'avertissements qu'avant (1 sur `plugin.json`, voulu).
<!-- /FICHE -->

---

<!-- FICHE:K2 -->
## K2 [ ] — Migrer les quatre autres commandes et `references/`

**Dépend de** : `K1`.
**Fichiers** : `commands/{init,chantier,tache,enchainer}.md`, `references/*.md`, `agents/fiche.md`, `evals/init/case.yaml`, `context AI/08-etat.md` (journal).

**Prompt**
Même forme que `skills/check/SKILL.md` (K1, `disable-model-invocation` selon son
verdict) : `git mv` chaque commande vers `skills/<nom>/SKILL.md`. Les trois
`references/tache-*.md` vont par `git mv` dans `skills/tache/references/` — un seul
exemplaire ; `skills/tache/SKILL.md`, `skills/enchainer/SKILL.md` et `agents/fiche.md`
y pointent par `${CLAUDE_PLUGIN_ROOT}/skills/tache/references/` (ou `<kit>/…` dans
l'agent, comme aujourd'hui). `commands/` et `references/` disparaissent. Lance les tests
`python scripts/test-vlp.py`, `validate`, puis la suite d'evals Windows (3 cas). Si
`init` échoue **seulement** par `max_turns` (25 pris sur 25 au chantier I), passe
`max_turns` à 30 dans `evals/init/case.yaml`, rejoue ce cas seul, et dis-le au journal.

**Critère de fin**
`ls commands references` : absents ; `ls skills` : 5 dossiers ;
`grep -rn "references/" skills agents` : toutes les lignes nomment `skills/tache/references/` ;
tests `OK` ; suite Windows 3/3 score 1 (tours et `costUsd` par cas).
<!-- /FICHE -->

---

<!-- FICHE:K3 -->
## K3 [ ] — Mettre les renvois de la doc à jour

**Dépend de** : `K2`.
**Fichiers** : `CLAUDE.md`, `methode-chantier.md`, `README.md`, `scripts/vlp.py` (commentaire), `.claude-plugin/plugin.json`, `context AI/00-INDEX.md`.

**Prompt**
Relance le grep des renvois du socle et corrige chaque ligne vivante : routage de
`CLAUDE.md` (« modifier une commande » → `skills/<nom>/SKILL.md`), règle 4 (`commands/`
→ `skills/`), `methode-chantier.md` (« Ne descendent jamais »), l'arborescence du
`README.md`, le commentaire de `vlp.py` (`carte`), l'index s'il en parle. Ne touche ni
aux replis `~/.claude/commands/`, ni à `archive/`, `exemples/`, ni aux fichiers de
fiches clos. Passe `plugin.json` en 3.2.0 (structure changée, commandes identiques).
Puis `vlp.py renvois .` et `validate`.

**Critère de fin**
Le grep des renvois : lignes avant → après, et chaque ligne restante est un repli
`~/.claude/commands/` ou une donnée de test ; `vlp.py renvois .` : 0 absent (nommés
affichés) ; `validate` : 1 avertissement, le voulu.
<!-- /FICHE -->
