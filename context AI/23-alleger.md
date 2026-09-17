> **QUAND LIRE** : on joue une fiche `L*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache L<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier L — `/vlp:enchainer` : alléger le chef

**À quoi il sert.** Mesuré sur MapDecorator : le chef fait 15 tours (2,07 $) pour une seule fiche déléguée.
On lui donne la page en un appel, on lui interdit d'agir après un arrêt, et on le fait tourner sur un modèle léger.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 3 fiches, `L1` à jouer.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17) :

| Fichier | Ce qu'il porte |
|---|---|
| `skills/enchainer/SKILL.md` | le chef : carte, `valider` + grep (étape 2), un `Skill` `vlp:jouer` par fiche (3), arrêt (3 bis), bilan + page par `cat tache-page.md` (4), clôture (5) |
| `skills/jouer/SKILL.md` | `context: fork`, `agent: vlp:fiche`, `background: false`, `user-invocable: false` |
| `agents/fiche.md` | `model: haiku`, `effort: low`, `maxTurns: 25` |
| `skills/tache/references/tache-page.md` | la page : `vlp.py page` + `--note`, `read` puis publication avec `url` — partagée avec `/vlp:tache` |

**Avant, mesuré** (journal de `context AI/08-etat.md`, 2026-09-17, MapDecorator, session interactive Opus) :
chef **15 tours**, 14 appels (Bash 9, Artifact 2, AskUserQuestion 2, Skill 1), 2,07 $ ; dont ≈ 6 tours de
page (`cat tache-page.md`, `page --help`, `ls` du HTML, `page`, `read`, publier) et ≈ 5 tours d'action après
un `RETOUR` ; P1, écrite dans la session, vérifiée et cochée par le chef. Sous-agent Haiku 22 tours / 25, 0,13 $.

**Invariants.** Une règle vit à un seul endroit : `tache-page.md` reste la référence de `/vlp:tache` ;
enchainer peut y renvoyer pour le détail mais donne sa commande complète. `(visuel)` et le contrat
`enchainement.md` ne changent pas. Pas de `disable-model-invocation` (écarté en K1).

**Outils de preuve** : `vlp.py valider`, `vlp.py renvois` (0 absent), `claude plugin validate .`
(1 avertissement voulu), evals Windows **toujours ainsi** : `claude plugin eval . --tag check --tag init
--tag hook --runs 1 --ablation none --no-publish --scaffold --allow-tools Write Edit --trust-plugin
--max-cost-usd 1.5 -j 3` ; tours et coût dans `aggregate-result.json`. `claude` hors PATH :
`%APPDATA%/Claude/claude-code/<version>/claude.exe`.

**La sonde** (L3) : bac à sable dans le scratchpad, `claude.exe -p … --output-format json --permission-mode
acceptEdits --add-dir <kit> --max-budget-usd 0.5` ; transcripts copiés par `cp` avant `mesure-tokens.py`
(chemins > 260 caractères). **Plafond : 1,5 $ et trois lancements** pour L3.

**Dehors** : le coût de `/vlp:tache` ; WSL2 (TODO n° 11) ; le contenu du sous-agent `vlp:fiche` hors `maxTurns`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `L1` | Donner la page au chef en un appel | rien |
| `L2` | Questionner sans agir, et régler modèle et `maxTurns` | rien |
| `L3` | Mesurer le chef après, et livrer | `L1`, `L2` |

L1 et L2 touchent deux étapes distinctes du même fichier : jouables dans n'importe quel ordre, pas en parallèle.

---

<!-- FICHE:L1 -->
## L1 [ ] — Donner la page au chef en un appel

**Dépend de** : rien.
**Fichiers** : `skills/enchainer/SKILL.md` (étape 4), `skills/tache/references/tache-page.md`, `scripts/vlp.py` (aide de `page`).

**Prompt**
Réécris l'étape 4 de `skills/enchainer/SKILL.md` pour que le chef régénère la page sans rien lire
d'autre : la commande `vlp.py page "<fichier de fiches courant>" "<page>" --note <fiche> "<critère>"`
complète, avec le chemin de la page tiré de ce que la carte donne déjà (le fichier de fiches courant
→ `artefacts/<même nom>.html`), puis `Artifact` `read` sur l'`url` de « artefact du chantier » et
publication avec `file_path` et `url`, `label` des fiches jouées. Supprime le `cat` de `tache-page.md`
(garde celui de `tache-blocage.md`, cas rare). Si la page dérivée n'existe pas, `vlp.py page` le dit :
une ligne, et continue. Ne recopie pas les règles de `tache-page.md` au-delà de la commande : renvoie-y
par son nom pour le cas d'une `GARDE:`.

**Critère de fin**
`grep -c "tache-page.md" skills/enchainer/SKILL.md` → 0 appel `cat` restant (compte avant → après) ;
`grep -c "vlp.py\" page" skills/enchainer/SKILL.md` ≥ 1 ; `wc -l` avant → après ; `vlp.py renvois` 0 absent.
<!-- /FICHE -->

---

<!-- FICHE:L2 -->
## L2 [ ] — Questionner sans agir, et régler modèle et `maxTurns`

**Dépend de** : rien.
**Fichiers** : `skills/enchainer/SKILL.md` (étapes 3 et 3 bis), `agents/fiche.md`, doc des skills (frontmatter `model`).

**Prompt**
Étape 3 bis : après un `RETOUR`, le chef pose **une** question et, selon la réponse, coche ou non —
aucun autre outil (ni lecture, ni copie, ni vérification, ni correction). Étape 3 : une fiche déjà
cochée n'est ni rejouée ni vérifiée. Vérifie dans la doc des skills (https://code.claude.com/docs/en/skills)
que `model:` est un champ de frontmatter ; si oui, pose `model: sonnet` sur `skills/enchainer/SKILL.md`,
sinon écris-le au journal et n'invente rien. `maxTurns` de `agents/fiche.md` : 22 mesurés pour 25 —
monte-le à 30 et dis pourquoi au journal. Chaque ajout se paye à chaque lancement : court.

**Critère de fin**
`grep -n "^model:" skills/enchainer/SKILL.md` (ou la ligne de journal qui dit pourquoi pas) ;
`grep -n "maxTurns" agents/fiche.md` → 30 ; la phrase « aucun autre outil » trouvée à l'étape 3 bis ;
`wc -l` avant → après ; `claude plugin validate .` → 1 avertissement voulu.
<!-- /FICHE -->

---

<!-- FICHE:L3 -->
## L3 [ ] — Mesurer le chef après, et livrer

**Dépend de** : `L1`, `L2`.
**Fichiers** : bac à sable du scratchpad, `.claude-plugin/plugin.json`, `context AI/08-etat.md` (journal, TODO n° 12).

**Prompt**
Monte le bac à sable de la sonde : un `CHANTIER.md` avec « artefact du chantier » factice, deux fiches,
la première scriptable (`FAITE`), la seconde `(visuel)` (`RETOUR`). Sonde d'abord si `Artifact` existe
en `-p` ; sinon, dis-le et compte les tours hors publication. Lance le chef en `--model opus` pour voir
si `model: sonnet` de L2 bascule (modèle lu message par message dans le transcript). Mesure le chef et
le sous-agent par `mesure-tokens.py`. Passe le plugin en 3.3.1, lance les evals Windows, écris au journal
une ligne avant → après, et mets la TODO n° 12 à jour (soldée ou restante).

**Critère de fin**
Tours du chef avant (15) → après, appels par outil, modèle constaté du chef, $ ; 2 statuts rendus
(`FAITE`, `RETOUR`) ; evals 3/3 avec tours bruts ; `grep '"version"' .claude-plugin/plugin.json` → 3.3.1.
<!-- /FICHE -->
