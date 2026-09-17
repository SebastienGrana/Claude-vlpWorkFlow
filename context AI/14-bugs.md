> **QUAND LIRE** : on joue une fiche `B*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache B<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier B — Corriger les bugs de l'audit

**À quoi il sert.** L'audit du 2026-09-17 (`12-audit.md`) a relevé des bugs qui
font mentir le kit : un grep muet, des arguments substitués avant lecture, des
gabarits qui promettent des fichiers absents. Le chantier les corrige un par un.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 3 fiches, `B1` à jouer.

## Le socle commun

Périmètre : bugs **1, 2, 3, 5, 6, 7, 8, 10, 11** de `12-audit.md` (le 3 ajouté
au cadrage, il n'était rangé nulle part). Le 4 est déjà corrigé.

| Bug | Où il est, mesuré au cadrage | Fiche |
|---|---|---|
| 1 | `commands/check.md:65` grep `Lettres prises` ; libellé réel `Lettres de fiche déjà prises` | B2 |
| 2 | `$1`/`$2` : `chantier.md` 38, 55-56 ; `tache.md` 59, 82-83 ; `init.md` 16 ; `enchainer.md` 26 — 0 `$ARGUMENTS` | B1 |
| 3 | `${CLAUDE_PLUGIN_ROOT}` littéral : `CHANTIER.md:12`, `templates/CHANTIER.md:12`, `templates/context AI/00-INDEX.md:20` ; écrit par `init.md:107` | B2 |
| 5 | `context AI/artefacts/00-route.html`, référencée nulle part | B3 |
| 6 | `<title>` : gabarit `templates/artefact-chantier.html:1` = `<Chantier> — <Projet>` ; `09-enchainer.html` = `Claude-vlpWorkflow — …` ; `10-mesure.html` = `Mesurer les tokens — vlp` | B2, B3 |
| 7 | `**Session**` en chemin de machine : `10-mesure.md` (2), `11-conso.md` (2), `13-tours.md` (3) | B3 |
| 8 | fantômes : `templates/CLAUDE.md` 31-32 (`18-code`, `02-architecture`), `templates/context AI/00-INDEX.md` 17-18 (`01-projet`, `02-architecture`) | B2 |
| 10 | `README.md:50-52` « tenus à jour à chaque fiche » contre `ARTEFACTS.md:24` | B3 |
| 11 | pas de `.gitignore` ; `scripts/__pycache__/` dans `git status` | B3 |

Invariants :

- Convention de titre : `<Projet> — <Nom du chantier>` (`commands/chantier.md`,
  étape 5 bis). Ici le projet s'appelle `vlp`.
- `$ARGUMENTS` sur une ligne à lui ; la prose dit « le premier argument », « le
  second », jamais `$1` ni `$2` (contrainte de `CHANTIER.md`).
- `${CLAUDE_PLUGIN_ROOT}` n'est substitué que dans le texte d'une commande :
  un fichier de données (`CHANTIER.md`, index) nomme le fichier du kit en clair.
- `scripts/mesure-tokens.py` accepte un id de session seul (chantier T) : une
  ligne `**Session** : <id>` se mesure comme un chemin.
- Chaque correctif se prouve par le grep du tableau : compte avant, compte après.

**Hors chantier** : le bug 9 `(visuel)` (TODO n° 4), le numéro d'état figé de
`init.md:82` (TODO n° 10), les `CHANTIER.md` des autres projets équipés (autres
dépôts). Les fragilités 12 à 18 ont leurs chantiers.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `B1` | Remplacer `$1` et `$2` par `$ARGUMENTS` | rien |
| `B2` | Rendre justes les libellés et les gabarits | rien |
| `B3` | Nettoyer le dépôt | rien |

Les trois sont indépendantes ; l'ordre ne sert qu'à commiter proprement.

---

<!-- FICHE:B1 -->
## B1 [x] — Remplacer `$1` et `$2` par `$ARGUMENTS`

**Session** : 7bb64701-bdad-4be9-8287-3ede11e93e49

**Dépend de** : rien.
**Fichiers** : commands/chantier.md, commands/tache.md, commands/init.md,
commands/enchainer.md — et rien d'autre.

**Prompt**
Dans chacune des quatre commandes, ajoute juste après le frontmatter un court
bloc « Arguments reçus : » suivi de `$ARGUMENTS` seul sur sa ligne. Puis
réécris chaque passage qui nomme `$1` ou `$2` (lignes du socle) pour dire « le
premier argument », « le second argument », « tous les arguments ». Garde le
sens exact : alias d'un projet voisin, puis fiche ou nom de chantier. Ne
touche à rien d'autre dans ces fichiers.

**Critère de fin**
`grep -n '\$[12]\b' commands/*.md agents/*.md` rend 0 ligne (8 avant) et
`grep -c '^\$ARGUMENTS$' commands/{chantier,tache,init,enchainer}.md` rend 1
pour chacun (0 avant). Le rejeu réel d'une commande avec arguments reste un
geste de l'utilisateur : noter dans le journal ce qui reste à rejouer.
<!-- /FICHE -->

---

<!-- FICHE:B2 -->
## B2 [ ] — Rendre justes les libellés et les gabarits

**Dépend de** : rien.
**Fichiers** : commands/check.md, commands/chantier.md, commands/init.md,
CHANTIER.md, templates/CHANTIER.md, templates/CLAUDE.md,
templates/context AI/00-INDEX.md, templates/artefact-chantier.html — et rien d'autre.

**Prompt**
Bug 1 : dans `check.md`, étape D, cherche `Lettres de fiche déjà prises`.
Bug 3 : la ligne « **méthode** » des deux `CHANTIER.md` et la ligne de l'index
gabarit nomment `methode-chantier.md` « à la racine du kit », sans variable ;
`chantier.md` étape 1 nomme lui-même `${CLAUDE_PLUGIN_ROOT}/methode-chantier.md`
(texte de commande, donc substitué) ; `init.md` écrit la nouvelle valeur au
lieu de la variable.
Bug 6 : le `<title>` du gabarit de chantier devient `<Projet> — <Chantier>`.
Bug 8 : retire des gabarits `CLAUDE.md` et `00-INDEX.md` les lignes qui
nomment `01-projet.md`, `02-architecture.md`, `18-code.md`.

**Critère de fin**
Rendent 1 ligne chacun (0 avant) : `grep -c 'Lettres de fiche déjà prises' commands/check.md`.
Rendent 0 (compte avant entre parenthèses) :
`grep -rn 'CLAUDE_PLUGIN_ROOT' CHANTIER.md templates/` (3),
`grep -rn '01-projet\|02-architecture\|18-code' templates/` (4),
`grep -c 'Chantier&gt; — &lt;Projet' templates/artefact-chantier.html` (1).
Et le grep de `check.md` D, exécuté tel qu'écrit, trouve la ligne de `CHANTIER.md`.
<!-- /FICHE -->

---

<!-- FICHE:B3 -->
## B3 [ ] — Nettoyer le dépôt

**Dépend de** : rien.
**Fichiers** : .gitignore (nouveau), context AI/artefacts/00-route.html,
context AI/artefacts/09-enchainer.html, context AI/artefacts/10-mesure.html,
context AI/10-mesure.md, context AI/11-conso.md, context AI/13-tours.md,
README.md — et rien d'autre.

**Prompt**
Bug 11 : `.gitignore` avec `__pycache__/`.
Bug 5 : `git rm` de `00-route.html`.
Bug 6 : `<title>` de `09-enchainer.html` → `vlp — Enchaîner les fiches`, de
`10-mesure.html` → `vlp — Mesurer les tokens` ; republie chacune à son URL
(table des clos de `CHANTIER.md`), après l'avoir relue.
Bug 7 : dans les trois fichiers de fiches clos, chaque ligne `**Session**` en
chemin se réduit à l'id de session (le nom du `.jsonl` sans extension). Mesure
M et C avec `mesure-tokens.py` **avant** la retouche, puis après.
Bug 10 : `README.md` dit qu'une seule page suit les fiches, et renvoie à
`ARTEFACTS.md` au lieu de recopier la règle.

**Critère de fin**
`git status --short` ne montre plus `scripts/__pycache__/` ;
`grep -rn '00-route' --include=*.md --include=*.html .` hors `12-audit.md` et ce fichier : 0 ;
`grep -rn '^\*\*Session\*\* : .*[/\\]' "context AI/"` : 0 (7 avant) ;
totaux de `mesure-tokens.py` sur M et C identiques avant/après (M 11 362 254,
C 7 816 316) ; `grep -h '<title>' "context AI/artefacts/"*.html` : tous en `vlp — …`.
<!-- /FICHE -->
