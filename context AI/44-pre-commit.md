> **QUAND LIRE** : on joue une fiche `VAL*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache VAL<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier VAL — Le contrôle avant commit ne se saute plus

**À quoi il sert.** À chaque commit, `.githooks/pre-commit` dit « claude introuvable dans le
PATH, validate sauté » : `claude` n'est pas dans le PATH de ce poste, seul le `claude.exe` de
l'app existe. Le hook le cherchera, et validera vraiment les manifestes.

**Fait.** Rien. Ouvert le 2026-09-24, cadré en 1 fiche, `VAL1` à jouer.

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| le hook | `.githooks/pre-commit` | `sh` POSIX, lancé par Git ; `command -v claude`, sinon « introuvable », sort 0 ; puis `claude plugin validate` sur `marketplace.json` et `plugin.json` ; un échec : la sortie, « `<manifeste>` invalide, commit refusé. », sort 1 |
| l'exécutable de l'app | `"$APPDATA"/Claude/claude-code/<version>/claude.exe` | ici `2.1.275` et `2.1.280` ; les evals le cherchent déjà ainsi (`34-agent-sans-git.md:55`) |
| l'activation | `README.md:65` | `git config core.hooksPath .githooks`, une fois par clone ; posé dans ce clone |

**Mesuré à l'ouverture, le 2026-09-24.** Hook actuel : 147 ms, « validate sauté », code 0.
Les deux `plugin validate` par l'exécutable de l'app : 1 569 · 1 566 · 1 569 ms. `sort -V` existe
dans le `sh` de Git (GNU coreutils 8.32).

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dort ; à revoir au réveil).
- Seul le chemin Windows de l'app est cherché : c'est le seul vérifié sur une machine.
- Plusieurs versions : la plus haute, par `sort -V` — un tri alphabétique mettrait `2.1.99`
  après `2.1.280`.

**Ce qu'on ne fait pas.** Le chemin de l'app sous macOS ou Linux : aucun poste pour le vérifier.
Toucher aux evals.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `VAL1` | Chercher le `claude.exe` de l'app quand `claude` manque | rien |

Une seule fiche : rien à paralléliser.

---

<!-- FICHE:VAL1 -->
## VAL1 [x] — Chercher le `claude.exe` de l'app quand `claude` manque

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `.githooks/pre-commit`, `README.md` (lignes 65–66) — et rien d'autre.

**Prompt**
Cette fiche porte sur Git : `sh` et `git` sont là, et ses vérifications se lancent dans
l'outil `Bash`.
1. Dans `.githooks/pre-commit`, quand `command -v claude` échoue : prends la plus haute
   version de `"$APPDATA"/Claude/claude-code/*/claude.exe` (`ls -d`, erreurs tues,
   `sort -V`, `tail -1`). Trouvé : les deux `plugin validate` passent par lui. Rien : le
   message « introuvable » actuel, sort 0. Reste en `sh` POSIX, commentaires en français.
2. Dans `README.md`, lignes 65–66 : une phrase — sans `claude` dans le PATH, le hook prend
   le `claude.exe` de l'app Claude sous Windows.
Tu ne commites pas : le chef le fera.

**Critère de fin**
Quatre sorties lues : `sh .githooks/pre-commit` dans le dépôt ne dit rien et sort 0 ; dans un
clone temporaire (`git clone -q`, dossier donné par `py -c` et `tempfile.mkdtemp()`), avec
`.claude-plugin/plugin.json` réduit à `{`, `git -C <clone> -c core.hooksPath=.githooks commit
-qam casse` sort 1 en disant « plugin.json invalide, commit refusé. » ; `APPDATA` vers un
dossier vide, le hook dit « introuvable » et sort 0 ; sa durée, trois fois, contre 147 ms avant.
<!-- /FICHE -->
