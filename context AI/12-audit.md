> **QUAND LIRE** : on choisit le prochain chantier du kit, ou on cherche la
> preuve d'un bug ou d'une mesure de l'audit du 2026-09-17. Pas besoin de ce
> fichier pour jouer une fiche : chaque chantier aura le sien.

# Audit du kit — 2026-09-17

Fait en une session, sur tout le kit (commandes, agent, doctrine, gabarits,
script, chantiers clos), avec 19 transcripts mesurés, la doc officielle et les
pratiques qui reviennent partout sur le web. La liste ordonnée des chantiers
qui en sort est la **TODO de `08-etat.md`** ; ce fichier garde les preuves et
le détail de ce que chaque chantier vise.

## Les mesures brutes

Recompté le 2026-09-17 par `scripts/mesure-tokens.py` (chantier T) — un
tour = un `message.id` ; contexte d'un tour = input + cache_creation +
cache_read ; `equiv` et `usd` pondérés sur la grille de prix. La première
version de cette table comptait les lignes `assistant` : ×1,7 à ×4,6.

| Session | Commande | tours | appels | ctx_1er | ctx_dernier | input | output | cache_creation | cache_1h | cache_read | total | equiv | usd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ba2e8409 | `/vlp:tache` | 29 | 22 | 82 562 | 135 729 | 58 | 21 401 | 74 805 | 74 805 | 3 078 226 | 3 174 490 | 564 496 | 1.13 |
| ca51f6e9 | `/vlp:tache` (C1) | 31 | 32 | 82 823 | 130 801 | 62 | 17 171 | 74 353 | 26 375 | 3 326 286 | 3 417 872 | 531 268 | 1.06 |
| c49b72aa | `/vlp:tache` (M3) | 34 | 31 | 82 497 | 129 446 | 68 | 10 219 | 71 477 | 71 477 | 3 517 106 | 3 598 870 | 545 828 | 1.09 |
| a70a363d | `/vlp:tache` | 40 | 40 | 81 903 | 127 541 | 80 | 21 177 | 75 962 | 75 962 | 4 128 698 | 4 225 917 | 670 759 | 1.34 |
| dd7e5a7f | `/vlp:tache` (M4) | 66 | 63 | 82 830 | 152 347 | 132 | 35 388 | 194 394 | 194 394 | 7 533 470 | 7 763 384 | 1 319 207 | 2.64 |
| c6c476f5 | `/vlp:tache` (E7) | 28 | 82 | 70 016 | 121 708 | 690 | 66 396 | 376 245 | 94 040 | 2 718 975 | 3 162 306 | 1 145 404 | 5.73 |
| be0a1961 | `/vlp:chantier` | 45 | 43 | 80 901 | 166 647 | 90 | 36 263 | 110 199 | 104 577 | 5 452 566 | 5 599 118 | 942 843 | 1.89 |
| 37331eef | `/vlp:enchainer` (chef seul) | 6 | 6 | 77 917 | 84 656 | 12 | 1 073 | 27 528 | 20 789 | 459 026 | 487 639 | 101 281 | 0.20 |
| c65ff31d | *(aucune commande vlp)* | 5 | 0 | 75 190 | 81 883 | 10 | 8 528 | 27 205 | 27 205 | 368 174 | 403 917 | 133 877 | 0.27 |

Ce que ça dit :

- socle de session **sans** commande vlp : 75 113–76 788 (4 sessions) ; avec
  `/vlp:tache` au 1er tour : 81 903–83 021 → commande + `CHANTIER.md`
  ≈ 6–7 k tokens, **~8 % du 1er tour** ;
- une fiche = **28 à 66 tours**, 22 à 82 appels d'outils ; `Bash` 11–32,
  `Edit` 3–34, `Artifact` 2–6 par fiche (les six `/vlp:tache`) ;
- coût ≈ contexte × tours : **le kit optimise les lignes, la facture est
  dans les tours** — un tour de plus à 120 k pèse 100 fois un socle de
  80 lignes ;
- `scripts/mesure-tokens.py` compte `cache_read` au même poids qu'un token
  frais ; la facturation, non (fraction du prix — à vérifier sur la grille).
  Les 7,8 M du chantier C sont surtout du cache relu. Pondéré depuis le
  chantier T : colonnes `equiv` et `usd`.

## Bugs — ça casse ou ça ment aujourd'hui

1. **`/vlp:check` D ne trouve jamais sa ligne** — `commands/check.md:65`
   cherche `Lettres prises` ; le libellé réel est `Lettres de fiche déjà
   prises` (`templates/CHANTIER.md:41`, `CHANTIER.md:45`). Mesuré : grep vide
   sur les deux.
2. **`$1` / `$2` sont substitués avant lecture** — session c6c476f5, texte
   reçu : « Ce que valent `cible` et `15k`. Si `cible` est l'alias… ». Sans
   argument, `$1` reste littéral. Correctif : une ligne `Arguments :
   $ARGUMENTS`, et une prose qui dit « le premier argument ». Fichiers :
   `chantier.md` (3 occurrences), `tache.md` (3), `init.md` (1),
   `enchainer.md` (1).
3. **`${CLAUDE_PLUGIN_ROOT}` n'existe pas dans le shell** — mesuré vide dans
   `Bash`. Substitué dans le texte des commandes seulement. Littéral dans
   `CHANTIER.md` (ligne « méthode ») et `templates/context AI/00-INDEX.md:20` :
   ça marche parce que le modèle devine le chemin vu ailleurs.
4. **TODO du kit vide** — `08-etat.md`, table sans ligne ; la feuille de
   route disait « Aucun chantier proposé ». Corrigé par cet audit.
5. **Page orpheline** — `context AI/artefacts/00-route.html` (124 lignes),
   référencée nulle part : doublon d'avant la convention de nommage.
6. **Trois formats de titre** dans le dépôt qui a écrit la convention
   `<Projet> — <Chantier>` : `Claude-vlpWorkflow — Enchaîner les fiches`,
   `Mesurer les tokens — vlp`, `vlp — Afficher la conso…`.
7. **Deux formats de chemin dans `**Session**`** — `10-mesure.md:105`
   (`~/.claude/…`) et `:133` (`C:\Users\…`). Aucun script robuste ne peut les
   lire ; les chemins de la machine partent sur GitHub.
8. **Gabarits qui promettent des fichiers que `/vlp:init` ne crée pas** —
   `01-projet.md`, `02-architecture.md` (`templates/context AI/00-INDEX.md:
   17-18`), `18-code.md` (`templates/CLAUDE.md`, routage). L'index d'un projet
   neuf ment dès le premier jour (contraire à CONVENTION règle 4). Et
   `init.md:82` fige `08-etat.md` alors que « les numéros ne sont pas la
   convention ».
9. **Marqueur `(visuel)` fragile** — `/vlp:enchainer` le cherche sur la ligne
   `**Critère de fin**` ; dans C1 il est au milieu d'un paragraphe
   (`11-conso.md:606`) : l'enchaînement ne s'y serait pas arrêté.
10. **README se contredit** — « deux pages… tenues à jour à chaque fiche »
    vs `ARTEFACTS.md` « une seule des deux vit au rythme des fiches ».
11. **Pas de `.gitignore`** ; `scripts/__pycache__/` traîne dans `git status`.

## Fragilités de conception

12. **Découpage inter-commandes à la regex sur de la prose** —
    `enchainer.md:22,122,128` et `agents/fiche.md:16` font des `sed`/`awk` sur
    `tache.md` (`/^## 0\. /,/^## 1\. /`, `/^Trois contraintes/`, `/^Ajoute
    donc/`). Mesuré : 78, 76, 10, 6, 13 lignes rendues aujourd'hui ; casse
    en silence à la première reformulation — déjà arrivé (décalage de 7
    lignes, `08-etat.md` 2026-09-17).
13. **`allowed-tools` n'est pas une clôture** — doc : outils « utilisables
    sans permission pendant ce tour ». `tache.md:25` écrit « `Bash` n'est
    ouvert que pour lire » ; E3 a mesuré le contraire, la phrase est restée.
14. **Règles dupliquées** (hors contexte/exemples/archive) : « 250 lignes »
    dans 6 fichiers, « comptes bruts » 10, « six copies » 5, « un seul
    endroit / une seule fois » 7. README, INSTALLATION, CONVENTION, ARTEFACTS
    et méthode racontent la même histoire cinq fois.
15. **La page de chantier, « vue dérivée jamais retouchée à la main », est
    retapée par le modèle** — 130 lignes de HTML à chaque fiche, à 120 k de
    contexte, 2 à 8 appels `Artifact`. Une vue dérivée se calcule.
16. **Le kit ne se teste pas** — ni `claude plugin validate`, ni eval.
    `claude plugin eval` (v2.1.269+) compare avec/sans plugin ; graders
    `regex`, `tool_used`, `tool_order`, `file_exists` gratuits.
17. **Fiches du kit hors norme** — E7 = 46 lignes, C1 = 34 (norme : ~20, à
    50 c'est deux).
18. **`/vlp:enchainer` remis « tel quel »**, coût connu mauvais, vendu
    « commode mais plus cher » à un groupe qui clone.

## Ce que disent les pratiques récurrentes

- **Le plus petit ensemble de tokens à haut signal** (Anthropic). `tache.md`
  fait 377 lignes / 18 ko relues à chaque fiche ; la doc des skills vise
  < 500 lignes **avec** disclosure progressive : corps court, le rare
  (blocage, coût, clôture) en fichiers de référence chargés à la demande.
- **Ne jamais envoyer un LLM faire le travail d'un linter** (HumanLayer). Le
  déterministe va dans un hook ou un script : valider les marqueurs,
  régénérer la page, extraire une fiche. Le kit a 1 script, 0 hook, ~30
  règles « ne fais pas ». Le suivi d'instructions baisse uniformément avec
  leur nombre (~150–200 suivies, le harnais en prend ~50).
- **Just-in-time context** : `` !`cat CHANTIER.md` `` injecte la carte avant
  le 1er tour ; `${CLAUDE_SESSION_ID}` est substitué dans une commande —
  le paragraphe `tache.md:260-271` devient une ligne.
- **Sous-agents quand l'isolation vaut plus que le démarrage** (Anthropic).
  Levier non essayé : `context: fork` + `agent: vlp:fiche` sur la commande
  elle-même — plus de chef qui relit 70 k par appel.
- **Spec-driven : petites tâches, frontières, critère vérifiable.** La fiche
  vlp est en avance là-dessus : marqueurs, dépendances écrites, « aucun
  chiffre inventé », bloc Tentatives.

## Le roast, pour mémoire

- 18 ko pour dire « lis peu ». « 250 lignes » vit à six endroits.
- `/vlp:check` vérifie une ligne qui n'existe pas, muet depuis le 1er jour.
- La TODO du projet qui explique comment tenir une TODO était vide.
- Une fiche fait 20 lignes et jusqu'à 66 tours ; le kit compte les lignes.
- « Aucun code applicatif » — la mécanique est en prose, exécutée par le
  modèle à 1 000 tokens le tour : du code, en plus cher, sans test.
- Le cœur est bon ; c'est le moteur qui est en prose.

## Ce que chaque chantier de la TODO vise — le détail que la table ne dit pas

Lettres proposées (prises : E, M, C) — `/vlp:chantier` tranche.

- **B — Corriger les bugs** : points 1, 2, 5, 6, 7, 8 (index et routage
  seulement), 10, 11 ; convention de chemin pour `**Session**`.
- **T — Compter les tours, pondérer** : `mesure-tokens.py` rend tours,
  appels d'outils par nom, contexte 1er/dernier tour, coût pondéré (cache ≠
  frais) ; `**Session**` écrite via `${CLAUDE_SESSION_ID}` ; résout `~` et
  `C:\`.
- **R — Réduire les tours de `/vlp:tache`** : `` !`cat CHANTIER.md` `` à
  l'étape 0 ; 0 bis + 1 + 4 en un seul appel ; corps ≤ 150 lignes ;
  blocage / coût / clôture en fichiers de référence ; corrige le point 13.
  Gain prouvé par T, avant/après.
- **S — Script `vlp.py`** : `extraire <fiche>`, `socle`, `etat`, `page`
  (régénère le HTML depuis le fichier de fiches), `valider` (marqueurs,
  titres, `(visuel)` sur la bonne ligne). Remplace les points 12, 15, 9.
  Étend l'exception de la règle 4 de `CLAUDE.md` — à assumer.
- **H — Hooks du kit** : `hooks/hooks.json` ; `PostToolUse` (matcher Edit /
  Write) → `vlp.py valider` sur un fichier de fiches, exit 2 + message ;
  `SessionStart` → injecter `CHANTIER.md` si présent. Fin des « recopie à
  l'identique ».
- **V — Evals** : `claude plugin eval init`, 4–5 cas sur un bac à sable
  (`init` équipe, `chantier` propose depuis la TODO, `tache` extrait la
  bonne fiche, `check` voit une incohérence injectée) ; `claude plugin
  validate` avant commit.
- **D — Fusionner la doctrine** : README + INSTALLATION + CONVENTION +
  ARTEFACTS + méthode → 3 fichiers ; chaque nombre vit une fois, les autres
  pointent (point 14).
- **K — Migrer `commands/` → `skills/`** : un dossier par commande avec ses
  références ; `disable-model-invocation: true` ; variante `context: fork`
  + `agent: vlp:fiche`. La doc : « Use `skills/` for new plugins ».
- **N — `/vlp:enchainer` : réparer ou retirer** : chef ≤ 3 tours par fiche
  via la skill forkée, ou suppression ; décidé aux chiffres de T.
- **I — Un projet neuf qui ne ment pas** : `/vlp:init` crée ce que l'index
  et le routage nomment, ou ne les nomme pas ; numéro d'état pris à la
  suite (point 8).

Ordre conseillé : B → T → R → S, puis H et V en parallèle ; D n'importe
quand ; K et N attendent les chiffres.

## Sources

- https://code.claude.com/docs/en/slash-commands — frontmatter, `$ARGUMENTS`,
  `` !`cmd` ``, `context: fork`, « custom commands have been merged into
  skills »
- https://code.claude.com/docs/en/hooks-guide et
  https://code.claude.com/docs/en/hooks — événements, exit 2,
  `additionalContext`
- https://code.claude.com/docs/en/plugins-reference — « Use `skills/` for new
  plugins », `${CLAUDE_PLUGIN_ROOT}`
- https://code.claude.com/docs/en/plugin-evals — v2.1.269+, baseline, graders
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  — < 500 lignes, disclosure progressive, « build evaluations first »
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://claude.com/blog/subagents-in-claude-code
- https://www.humanlayer.dev/blog/writing-a-good-claude-md
- https://addyosmani.com/blog/good-spec/
