> **QUAND LIRE** : on joue une fiche `H*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache H<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier H — Hooks du kit

**À quoi il sert.** Le kit a 0 hook : la validation d'un fichier de fiches est un
appel prescrit à la main, et une coche écrite par `/vlp:tache` n'est jamais validée.
Le chantier met `vlp.py valider` dans un hook `PostToolUse` du plugin (TODO n° 5).

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 4 fiches, `H1` à jouer.

## Le socle commun

**Résultat visible.** Écrire un fichier de fiches cassé (marqueur manquant, titre
reformulé) est refusé tout de suite par un hook `PostToolUse` du plugin — exit 2,
écarts lisibles par le modèle —, prouvé en vrai après `/reload-plugins` ; l'appel
`valider` prescrit à l'étape 6 de `commands/chantier.md` disparaît. `SessionStart`
n'est gardé que si les chiffres le justifient (H4).

**Noms retenus** (ne pas renommer) : `hooks/hooks.json` à la racine du kit ;
`vlp.py hook`, sous-commande qui lit sur stdin le JSON du hook et prend
`tool_input.file_path`. Un fichier de fiches se reconnaît **à son contenu**
(`<!-- FICHE:` ou `## Le socle commun`), jamais à son nom.

**Contrat des hooks — à vérifier en H1, pas à supposer.** Doc :
https://code.claude.com/docs/en/hooks et
https://code.claude.com/docs/en/plugins-reference (`hooks/hooks.json`,
`${CLAUDE_PLUGIN_ROOT}`). Attendu : `PostToolUse`, matcher `Write|Edit`, exit 2 →
stderr rendu au modèle (l'outil a déjà écrit : le message dit de corriger) ;
`hookSpecificOutput.additionalContext` pour une ligne rendue sans bloquer.
Inconnues : un kit chargé par un **lien dans `~/.claude/skills/vlp`** lit-il ses
hooks ? Sous Windows, quel shell lance la commande, et quelle forme de Python
répond (`python3` y est un faux raccourci, R3) ? Le repli `python3 … || python …`
relance le script en double sur une sortie non nulle (S5) : interdit pour `hook`.

**Invariants.** Ceux de `vlp.py` (socle de `16-script.md`) : Python 3 sans
dépendance, zéro appel modèle, UTF-8, testé par `scripts/test-vlp.py`. Un hook
valide est **muet ou d'une ligne** : ce qu'il dit est relu à chaque tour suivant.
`${CLAUDE_PLUGIN_ROOT}` dans `hooks/hooks.json` étend la règle 4 de `CLAUDE.md` —
à écrire (H3). Écart connu : `11-conso.md:88` (`(visuel)` de C1, archive) — le hook
le signalera si on édite ce fichier ; laissé tel quel.

**Mesure « avant »** (2026-09-17, cadrage, `mesure-tokens.py`) :

| Session | Tours | Appels | ctx_1er | Total | $ |
|---|---|---|---|---|---|
| S5 seule (`079e6e4d`, une fiche) | 42 | 64 | 58 839 | 5 191 619 | 4,70 |
| cadrage S + S1..S4 (`f5582775`) | 75 | 84 | 58 797 | 13 738 641 | 12,37 |
| cadrage R + R1..R4 (`588d8fcf`) | 80 | 92 | 58 632 | 13 103 584 | 10,68 |

Appels `vlp.py valider` prescrits : `chantier` 1, `check` 1, `enchainer` 1,
`tache` 0 (coche et `**Session**` écrites sans validation). Lignes citant
`identique` ou `marqueur` (`grep -c`) : `chantier` 4, `check` 3, méthode 3,
gabarit de fiches 2, `enchainer` 1, `init` 1, `tache` 1, `tache-blocage` 1 = 16.
Carte injectée par `` !`…` `` : `chantier`, `tache`, `enchainer` ; `CHANTIER.md`
fait 3 573 octets.

**Dehors.** Evals (TODO 6), fusion de la doctrine (7), migration `skills/` (8),
`/vlp:init` (10) ; `PreToolUse` ; les écritures par Bash (`sed -i`, `>`), que
`Write|Edit` ne voit pas. `check` et `enchainer` gardent leur `valider` : ils
contrôlent sans écrire, aucun hook ne les déclenche.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `H1` | Sonder le chargement des hooks, solder les restes de S | rien |
| `H2` | Écrire `vlp.py hook` | rien |
| `H3` | Brancher le hook et alléger les commandes | `H1`, `H2` |
| `H4` | Décider `SessionStart` aux chiffres | `H3` |

H1 et H2 sont parallélisables ; H3 et H4 non.

---

<!-- FICHE:H1 -->
## H1 [x] — Sonder le chargement des hooks, solder les restes de S

**Session** : c6648728-7227-4c69-ba9a-24c6670987bd
**Dépend de** : rien.
**Fichiers** : `hooks/hooks.json` (nouveau), `references/tache-page.md`,
`context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
Lis les deux pages de doc du socle (format d'un `hooks/hooks.json` de plugin).
Pose un hook-sonde `PostToolUse`, matcher `Write|Edit`, qui écrit sur stderr
`SONDE vlp <forme>` et sort 2 — une entrée par forme candidate (`python3`,
`python`, `py`), chacune un one-liner `-c` qui cite aussi `${CLAUDE_PLUGIN_ROOT}`
reçu en argument, pour prouver sa substitution. Rends la main : l'utilisateur fait `/reload-plugins`. Puis écris un
fichier dans le scratchpad et relève quelles sondes parlent. Vide ensuite
`hooks/hooks.json` (`{"hooks": {}}`) : H3 y mettra le vrai.
Restes de S : dans `references/tache-page.md`, la publication fait `Artifact`
`read` sur l'URL puis publie — plus de « republie » sans lecture (journal S5).
Rejoue `/vlp:check` sur ce projet et note sa sortie ; `/vlp:init` se rejoue
dans un dossier vide du scratchpad, ouvert par l'utilisateur. Une ligne de
journal : chargement oui/non, forme retenue, écarts de `check` et `init`.

**Critère de fin** (visuel)
Après `/reload-plugins`, une écriture fait parler au moins une sonde (nom de la
forme cité) — ou aucune, et la fiche s'arrête pour décider ; `grep -c republie
references/tache-page.md` avant → après ; `check` et `init` rejoués, écarts listés.
<!-- /FICHE -->

---

<!-- FICHE:H2 -->
## H2 [ ] — Écrire `vlp.py hook`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `hook` à `vlp.py`. Elle lit le JSON sur stdin et prend
`tool_input.file_path`. Sort 0 **muette** si : JSON illisible, chemin absent,
fichier inexistant, pas `.md`, ou contenu sans `<!-- FICHE:` ni
`## Le socle commun`. Sinon, réutilise la fonction de `valider` (pas de
sous-processus) : écart → les lignes `fichier:ligne: message` et le bilan sur
stderr, puis `Corrige ce fichier de fiches avant de continuer.`, sort 2 ;
valide → sur stdout le JSON `hookSpecificOutput` (`hookEventName`
`PostToolUse`, `additionalContext` = la seule ligne de bilan), sort 0. Chemin
relatif résolu contre `cwd` du JSON s'il existe. Mets la docstring à jour.
Dans `test-vlp.py`, cinq cas, fichiers temporaires seulement : JSON illisible,
`.md` ordinaire, fichier de fiches valide, marqueur fermant manquant, titre
reformulé.

**Critère de fin**
`python scripts/test-vlp.py` → `OK` ; sur ce projet,
`echo '{"tool_input":{"file_path":"context AI/16-script.md"}}' | python scripts/vlp.py hook; echo $?`
→ une ligne JSON `VALIDE 5 fiches`, 0 ; même appel sur `context AI/11-conso.md`
→ l'écart de la ligne 88 sur stderr, 2 ; temps d'un appel affiché (`time`).
<!-- /FICHE -->

---

<!-- FICHE:H3 -->
## H3 [ ] — Brancher le hook et alléger les commandes

**Dépend de** : `H1`, `H2`.
**Fichiers** : `hooks/hooks.json`, `commands/chantier.md`, `methode-chantier.md`,
`CLAUDE.md` (règle 4 seulement), `context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
`hooks/hooks.json` : `PostToolUse`, matcher `Write|Edit`, commande `vlp.py hook`
dans la forme retenue par H1 (journal), sans repli qui double l'appel.
`commands/chantier.md` : l'étape 6 ne lance plus `valider` — le bilan est déjà
rendu par le hook à l'écriture de l'étape 5 ; garde `wc -l` s'il sert au coût
annoncé. Allège les consignes « à l'identique » / marqueurs que le hook fait
respecter : l'explication vit une fois (méthode ou gabarit), `chantier.md`
pointe. Règle 4 de `CLAUDE.md` : `${CLAUDE_PLUGIN_ROOT}` vaut aussi dans
`hooks/hooks.json`. Rends la main pour `/reload-plugins`, puis écris dans le
scratchpad une copie de `16-script.md` sans un `<!-- /FICHE -->`, puis une copie
intacte. Une ligne de journal : appels prescrits et lignes comptées avant/après.

**Critère de fin** (visuel)
La copie cassée fait remonter l'écart du hook (exit 2) ; la copie intacte rend la
ligne `VALIDE` ; `grep -c "valider" commands/chantier.md` 1 → 0 ; lignes
`identique|marqueur` 16 → N (même `grep -c` que le socle).
<!-- /FICHE -->

---

<!-- FICHE:H4 -->
## H4 [ ] — Décider `SessionStart` aux chiffres

**Dépend de** : `H3`.
**Fichiers** : `hooks/hooks.json`, `context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
Ajoute à `hooks/hooks.json` un `SessionStart` qui lance `vlp.py carte` (forme de
H1). Rends la main : l'utilisateur fait `/reload-plugins`, ouvre une session
neuve sur ce projet et y tape un seul mot, puis une autre sans le hook (ou la
sienne d'avant) ; il donne les deux ids. Mesure-les avec `mesure-tokens.py`
(`ctx_1er`, octets ajoutés). Vérifie aussi si la carte revient après `/clear`
(source `clear`). Garde le hook **seulement** s'il permet de retirer une
injection `` !`…` `` d'une commande sans perdre une carte fraîche ; sinon retire-le
et écris « écarté », chiffres à l'appui. Une ligne de journal : la décision et ses
comptes bruts.

**Critère de fin** (visuel)
`ctx_1er` avec et sans le hook, affichés côte à côte ; `hooks/hooks.json` garde ou
retire `SessionStart` selon la règle ci-dessus ; la ligne de journal le dit.
<!-- /FICHE -->
