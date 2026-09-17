> **QUAND LIRE** : on joue une fiche `F*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache F<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier F — La feuille de route par script

**À quoi il sert.** La feuille de route et la clôture de `CHANTIER.md` se retouchent à la main à chaque
ouverture et clôture (badge, lettres, TODO, ligne des clos, total) : du déterministe en prose. Un script les écrit.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 4 fiches, `F1` à jouer.

## Le socle commun

| Nom | Où | Ce que c'est |
|---|---|---|
| feuille de route | `context AI/artefacts/feuille-de-route.html` (copie locale) ; gabarit `templates/artefact-feuille-de-route.html` | zones `ZONE:encours`, `ZONE:todo`, `ZONE:clos` (`tbody` + `tfoot` « Total cumulé »), `footer` « Lettres de fiche prises » et « Mis à jour le » |
| `CHANTIER.md` | racine | lignes en gras « **fichier de fiches courant** », « **artefact du chantier** », « **contexte** », « **fichier d'état** » ; table « Chantiers clos » ; ligne « Lettres de fiche déjà prises » |
| TODO | fichier d'état, table `\| # \| Chantier \| Ce qu'il apporte \| Coût estimé \| Dépend de \|` | la vérité ; la page n'en est que le miroir |
| `esc`, `milliers`, `arrondi` | `scripts/vlp.py` | échappement HTML ; « 11 362 254 » ; « ≈11,4M » — format Tokens : `≈<arrondi> (<milliers>)` |
| sous-commande | `scripts/vlp.py` : docstring, `add_parser` dans `main`, une `cmd_*` | ligne bilan en sortie, comptes bruts ; `--verifier` n'écrit rien, sort 1 si écart |
| tests | `scripts/test-vlp.py` (`verifier`, `appel`, bacs en dossier temporaire) | `python scripts/test-vlp.py` → `OK` ; 59 assertions avant ce chantier (`grep -cE "^\s*(assert\|verifie\|check)"`) |
| lanceur | `sh scripts/vlp <sous-commande>` ; dans une skill `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" …` | jamais `PY=$(for …)` ni `{ …; }` |

Invariants : le fichier fait foi, la page se régénère ; un script relancé ne change rien (idempotent) ; il
n'écrit que des fichiers locaux — **publier reste un appel `Artifact`** (lire l'url, puis republier).

Dehors : la page du chantier et sa `ZONE:bilan` (à la main), la ligne de bilan du fichier d'état, le routage
de `CLAUDE.md`, la publication. Scripts CRLF : l'outil Edit passe ; écrire un script Python par Write, `PYTHONUTF8=1`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `F1` | Mesurer ce que coûtent la feuille de route et la clôture à la main | rien |
| `F2` | Écrire `vlp.py feuille` | rien |
| `F3` | Écrire `vlp.py clore` | `F2` |
| `F4` | Brancher les deux scripts dans `/vlp:chantier` et `cloture.md` | `F2`, `F3` |

F1 et F2 sont indépendantes ; F3 réutilise la régénération de F2 ; F4 vient en dernier.

---

<!-- FICHE:F1 -->
## F1 [ ] — Mesurer ce que coûtent la feuille de route et la clôture à la main

**Dépend de** : rien.
**Fichiers** : `~/.claude/projects/C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow/fd4ebe27-5975-4250-89c7-13c5e861cc33.jsonl` (chantier X), `…/20b6f6d2-b753-45d0-9f79-4e0e0aa0deed.jsonl` (chantier W), ce fichier de fiches.

**Prompt**
Écris dans le scratchpad un script Python (Write, `PYTHONUTF8=1`) qui lit ces deux transcripts et compte,
par session, les appels d'outil `tool_use` qui touchent :
- la feuille de route : `Artifact` dont l'`url` ou le `file_path` vise `ff1fc060` ou `feuille-de-route`,
  et `Edit`/`Write`/`Bash` dont l'entrée nomme `feuille-de-route` ;
- la clôture de `CHANTIER.md` : `Edit`/`Write`/`Bash` dont l'entrée nomme `CHANTIER.md`.
Compte aussi les tours (messages assistant distincts par `message.id`) qui portent au moins un de ces appels,
et les publications refusées (`tool_result` en erreur qui suit un `Artifact`).
Verse les comptes bruts dans une ligne `**Mesuré**` sous le titre de F1 : ce sont l'« avant » que F4 comparera.

**Critère de fin**
Le script affiche, pour X et W : appels feuille, appels `CHANTIER.md`, tours concernés, refus ; la ligne
`**Mesuré**` les reprend, et `sh scripts/vlp valider "context AI/29-feuille.md"` rend `VALIDE`.
<!-- /FICHE -->

---

<!-- FICHE:F2 -->
## F2 [ ] — Écrire `vlp.py feuille`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `context AI/artefacts/feuille-de-route.html`, `context AI/08-etat.md` (sa TODO seule).

**Prompt**
Ajoute la sous-commande `feuille <projet> [--todo N] [--verifier]`. Elle lit `CHANTIER.md` du projet, trouve
le fichier d'état et le contexte par leurs lignes en gras, et réécrit dans `<contexte>/artefacts/feuille-de-route.html` :
- `ZONE:encours` : courant à `aucun` → « Aucun chantier ouvert » ; sinon le titre `# Chantier X — …` du
  fichier de fiches, sa plage (`F1–F4`, lue sur les titres) et le lien vers l'« artefact du chantier » ;
- `ZONE:todo` : une ligne par ligne de la TODO, `` `x` `` rendu en `<span class="mono">`, `\|` rendu `|` ;
  `--todo N` pose `<span class="badge" data-etat="cours">en cours</span>` sur la ligne N ;
- le pied : lettres prises de `CHANTIER.md`, plus la lettre du chantier courant s'il y en a un ; « Mis à jour le » à la date du jour.
Rien d'autre ne bouge (`ZONE:clos` intact). Bilan : `FEUILLE todo <n> · encours <oui|non> · lettres <n> — <page>`.
Docstring, puis tests dans `test-vlp.py` sur un bac temporaire : encours ouvert et fermé, badge, idempotence, `--verifier`.

**Critère de fin**
`python scripts/test-vlp.py` rend `OK` avec plus de 59 assertions (compte `grep -cE` avant/après affiché) ;
`sh scripts/vlp feuille .` puis `sh scripts/vlp feuille . --verifier` sort 0 ; `git diff --stat` sur la page ne touche que ses zones.
<!-- /FICHE -->

---

<!-- FICHE:F3 -->
## F3 [ ] — Écrire `vlp.py clore`

**Dépend de** : `F2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `cloture.md` (sections 1, 2 et 5, pour le format).

**Prompt**
Ajoute `clore <projet> --livre "<texte>" [--tokens N] [--abandon "<fiches et pourquoi>"] [--date AAAA-MM-JJ]`.
Elle fait, dans l'ordre, les écritures mécaniques de `cloture.md` :
1. l'en-tête `**CLOS** le <date>…` sous le titre du fichier de fiches courant (plus la ligne d'abandon) ;
2. `CHANTIER.md` : courant et artefact à `aucun`, une ligne de plus dans la table des clos (fichier, plage `F1..F4`
   avec abandon entre parenthèses, date, URL), la lettre ajoutée aux « Lettres de fiche déjà prises » ;
3. la feuille de route : une ligne en tête de `ZONE:clos` (lien, badge clos, plage, date, Tokens au format du socle
   ou « non mesuré », livré), le « Total cumulé » recalculé en sommant les comptes bruts entre parenthèses,
   puis la régénération de `feuille` (encours remis à aucun).
Refuse (sort 1, `GARDE:`) si le courant vaut déjà `aucun`. Bilan : `CLOS <lettre> <plage> · total <brut> — <projet>`.
Docstring et tests sur un bac temporaire : les quatre lignes, la table, la lettre, le total, le refus au second appel.

**Critère de fin**
`python scripts/test-vlp.py` rend `OK`, assertions en hausse sur F2 (comptes affichés) ; un bac copié de ce
projet dans le scratchpad, `clore` lancé, montre `CHANTIER.md` et la page corrects (`grep` des quatre lignes et du total affichés).
<!-- /FICHE -->

---

<!-- FICHE:F4 -->
## F4 [ ] — Brancher les deux scripts dans `/vlp:chantier` et `cloture.md`

**Dépend de** : `F2`, `F3`.
**Fichiers** : `skills/chantier/SKILL.md` (étape 5 bis), `cloture.md`, `ARTEFACTS.md`, `.claude-plugin/plugin.json`.

**Prompt**
Dans `/vlp:chantier` 5 bis, la retouche à la main de la feuille de route devient un appel
`sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" feuille . --todo <N>`, puis `read` de l'url et republication du fichier local.
Dans `cloture.md`, les sections 1, 2 et la partie feuille de route de 5 deviennent un appel `clore` (avec
`--tokens` pris à l'étape 3), puis la publication ; la page du chantier, le bilan, le routage restent en prose.
Retire de `ARTEFACTS.md` ce qui décrit la retouche à la main, en y pointant le script. Version en 3.3.4.
Court : chaque ligne ajoutée à une skill se paye à chaque appel.

**Critère de fin**
`claude.exe plugin validate .` passe (1 avertissement voulu), `sh scripts/vlp renvois .` rend 0 absent,
`grep -c "ZONE:encours" skills/chantier/SKILL.md cloture.md` rend 0 et 0, l'eval `chantier` rend 3/3 (tours et coût affichés) ;
la clôture de ce chantier se fait par `clore` et compare ses appels à la ligne `**Mesuré**` de F1.
<!-- /FICHE -->
