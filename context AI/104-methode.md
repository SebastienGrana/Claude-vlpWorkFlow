> **QUAND LIRE** : on joue une fiche `MET*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache MET<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier MET — La méthode du kit refaite, puis la TODO re-cadrée

**Ouvert.** le 2026-10-07.

**À quoi il sert.** Coder plus vite et mieux (le but de VIT) : une méthode rangée et complétée
par ce qui est publié, des commandes alignées sur elle, une TODO relue avec elle.

**Fait.** Rien. Ouvert le 2026-10-07, cadré en 10 fiches, `MET1` à jouer.

**Session** : ac0e817e-9962-4425-9cbb-c9dd8f5577b2

## Le socle commun

**Tranché au cadrage** (page à cartes https://claude.ai/artifact/FYzibZkWbfRUdaGMp9MA9A, 2026-10-07) :
méthode **rangée puis complétée** (Q1) ; commandes **alignées** sur elle, options ajoutées si
besoin (Q2) ; recherche sur **trois sujets**, 2 recherches chacun (Q3) ; ruff **trié ici**, sans
corriger le code (Q4) ; TODO **relue et reclassée**, texte des lignes gardé (Q5) ; essais hors bac :
**une règle et du code** (Q6) ; effort : **le billet lu, puis 3 fiches de code et 1 de conception**,
à `medium` et `xhigh` (Q7). Dehors (D1) : le refactoring (`REF`, re-cadré seulement), corriger
les remarques de ruff, la reprise de `NUI`, repeindre les vieilles pages (`CTR`), la consigne
« premier plan » des sessions `-p` (`ARP`).

| Quoi | Où | Ce qu'on en sait (2026-10-07) |
|---|---|---|
| la méthode | `methode-chantier.md` | 452 lignes ; « Les règles qui valent partout » : 21 règles, ~200 lignes |
| les commandes | `skills/*/SKILL.md` (8) | 1 162 lignes ; agents : `agents/fiche.md`, `agents/relecture.md` |
| la doctrine voisine | `cloture.md`, `nuit.md`, `enchainement.md` | lues par les commandes au moment voulu |
| la TODO | `context AI/08-etat.md`, « La TODO ordonnée » | 17 lignes ouvertes, 35 987 caractères |
| le journal | `context AI/08-etat.md`, entrées `## <date> — <code> — <sujet>` | l'effort : « VIT25 — l'effort » ; ruff : l'entrée `VIT15` du 2026-10-04 |
| la page à cartes | `templates/rapport-choix.html` du kit | lire son commentaire de tête, remplir, publier |
| le compteur d'essais | `essais_de` (`scripts/vlp_coeur.py`), test `tester_essais_de` (`scripts/test-vlp.py`) | ne voit que `~/.claude/projects/*-<session>-scratchpad-*/*.jsonl` |

**Une page à cartes, puis le journal.** Une fiche marquée `(visuel)` publie sa page, s'arrête,
et reprend sur les réponses collées. Les réponses s'écrivent dans `context AI/08-etat.md`, entrée
`## <date> — MET<n> — <sujet>`, avec le lien de la page : `MET7` et les suivantes y renvoient par
ce titre. Chaque option porte son ➕ et son ➖ ; l'existant porte nom, version, licence, lien, date.

**Règles à tenir** (`methode-chantier.md`, « Les règles qui valent partout ») : une règle à un
seul endroit, un nombre aussi ; ne pas réinventer la roue ; la TODO ne grossit pas sans deux oui
(retirer ou fondre une ligne n'en demande pas). Le kit garde **zéro paquet à l'exécution** ; un
outil d'atelier (tests, contrôles) est permis s'il est optionnel et a un repli (2026-10-05).
Recherche web : la section « Recherche web » du `CLAUDE.md` de l'utilisateur.

**Effort** (règle de l'effort) : `MET2` est une fiche de code, `xhigh` ; les autres se
conçoivent. Le dire avant de jouer, l'utilisateur le règle.

**Commit** : `MET<n> : <titre>`, un par fiche ; un `.py` touché passe `pyright` (0 erreur).
Le plugin chargé suit `main` : une commande modifiée ici ne se voit qu'après la fusion.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `MET1` | Chercher ce qui existe, et le présenter | rien |
| `MET2` | Compter les essais lancés hors d'un bac | rien |
| `MET3` | Préparer le test d'effort | `MET2` |
| `MET4` | Jouer le test d'effort | `MET3` |
| `MET5` | Trier les familles de ruff | rien |
| `MET6` | Trier les 21 règles | rien |
| `MET7` | Compléter la méthode | `MET1`, `MET2`, `MET4`, `MET5`, `MET6` |
| `MET8` | Aligner les commandes (1/2) | `MET7` |
| `MET9` | Aligner les commandes (2/2) | `MET7` |
| `MET10` | Relire et reclasser la TODO | `MET7` |

`MET1`, `MET2`, `MET5`, `MET6` ne dépendent de rien ; (b) passe avant (a) : `MET2` avant `MET3`.
Une fiche à la fois : `MET4` lance des sessions `claude -p` longues, sur 8 Go de mémoire.

---

<!-- FICHE:MET1 -->
## MET1 [x] — Chercher ce qui existe, et le présenter

**Session** : 240bd893-1e58-426c-bd93-728f652a2820
**Dépend de** : rien.
**Fichiers** : la page à cartes (scratchpad, depuis `templates/rapport-choix.html`), `context AI/08-etat.md` (une entrée au journal) — et rien d'autre.

**Prompt**
Cherche ce qui est publié sur trois sujets, **2 recherches chacun, 6 au plus**, 2 pages lues
en entier au plus : (1) travailler avec un agent de code — la doc officielle d'Anthropic
(Claude Code) d'abord ; (2) ranger le code Python d'un outil en ligne de commande (modules,
taille des fichiers, nommage) ; (3) les design patterns qui servent un outil comme le kit
(sous-commandes, scripts testés, doc lue par un LLM). La doc officielle tranche seule ; sinon
deux sources indépendantes, dites telles ; la récurrence n'est pas un argument.
Rends une page à cartes : une carte par pratique trouvée, son lien, sa date, son rang (doc
officielle, blog, forum), à côté de l'option « le faire nous-mêmes » ; trois choix par carte :
l'adopter, l'adapter, l'écarter. Ce que le kit fait déjà se dit (« déjà là : … »).
Publie, arrête-toi, puis écris les réponses au journal.

**Critère de fin** (visuel)
La page est publiée, l'utilisateur a collé ses réponses, et l'entrée `MET1 — ce qui existe`
du journal les porte toutes, avec la ligne de coût : « N recherches, M pages lues ».
<!-- /FICHE -->

---

<!-- FICHE:MET2 -->
## MET2 [x] — Compter les essais lancés hors d'un bac

**Session** : 240bd893-1e58-426c-bd93-728f652a2820
**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py` (`essais_de` et ses deux appelants : `grep -n "essais_de("`), `scripts/test-vlp.py` (`tester_essais_de`), `methode-chantier.md` (la règle), `context AI/08-etat.md` (le recompte de VIT) — et rien d'autre.

**Prompt**
Effort `xhigh`. `essais_de` ne trouve un essai que si son dossier de transcripts porte l'id
de la session et `scratchpad`. Les essais de `VIT25` ont tourné dans des copies du kit :
23 dossiers `~/.claude/projects/D--ProgPerso-vlp-vit25-*`, sans id de session (compté le
2026-10-07) ; ils manquent au total de `VIT`.
Écris d'abord, en trois lignes, les moyens de relier un essai à sa session (un nom de copie
qui porte l'id, un registre écrit au lancement, autre) ; prends le plus simple qui tient sans
réseau ni dépendance, et dis pourquoi. Code-le, et écris la règle « un essai part d'un bac,
ou se déclare » dans la méthode, à un seul endroit.
Puis recompte `VIT` avec ses 23 dossiers : l'ancien total reste au journal, marqué, avec un
renvoi vers le nouveau et par quoi (règle « un énoncé renversé se garde »).

**Critère de fin**
Un cas de `tester_essais_de`, dans un `HOME` temporaire, trouve un essai hors bac relié par le
moyen choisi, et pas un essai d'une autre session ; `vlp.py mutant … --attendu "<début du
libellé>"` le fait tomber quand le nouveau chemin est retiré. Suite `OK`, `pyright` 0 sur les
fichiers touchés. Le total de `VIT` avant → après, en $ et en tours, au journal.
<!-- /FICHE -->

---

<!-- FICHE:MET3 -->
## MET3 [x] — Préparer le test d'effort

**Session** : 240bd893-1e58-426c-bd93-728f652a2820
**Dépend de** : `MET2`.
**Fichiers** : `context AI/08-etat.md` (entrée « VIT25 — l'effort »), `scripts/boucle.py`, une page à cartes — et rien d'autre.

**Prompt**
Lis d'abord le billet officiel « Spending your effort » (`claude.dev/blog/spending-your-effort/`,
une page) : s'il chiffre la qualité par niveau, dis ce qui reste à mesurer.
Le plan reprend celui de `VIT25` (série 2) : VIT23, VIT20, VIT19 rejouées à `medium` et
`xhigh`, chacune dans un worktree jetable posé sur le commit d'avant la fiche (`0f0edd6`,
`ee0ca8f`, `2edc69b`), une session `boucle.py --plafond 1 --model claude-opus-5-5 --effort
<niveau>`, la consigne « premier plan » passée par `--append-system-prompt`, un essai à la
fois, `claude auth status` avant chacun. Le juge de `VIT25` (`vit25.py`) vivait dans un
scratchpad disparu : rebâtis-le dans le tien (suite, pyright, `sante --cliquet`, relecteur,
coût), et lance les essais pour que `MET2` les compte.
Choisis la **fiche de conception** : une fiche de doctrine d'un chantier clos, au critère
jugeable par script ou relecteur ; propose deux candidates.
Montre l'estimé (≈ 20,55 $ la passe de `VIT25`, plus la conception, chiffrée) sur une page à
cartes : candidate retenue, borne en $, go.

**Critère de fin** (visuel)
L'utilisateur a choisi la candidate et dit go sur l'estimé ; le juge tourne à blanc sur un
worktree (sortie collée au journal, entrée `MET3 — le test d'effort préparé`).
<!-- /FICHE -->

---

<!-- FICHE:MET4 -->
## MET4 [x] — Jouer le test d'effort

**Session** : 240bd893-1e58-426c-bd93-728f652a2820
**Dépend de** : `MET3`.
**Fichiers** : le juge et les worktrees de `MET3`, `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Joue les 8 essais préparés par `MET3` (4 fiches × `medium`, `xhigh`), un à la fois, sous la
borne en $ qu'il a fixée ; une session qui meurt en attendant arrête la série. Rends au
journal le tableau de `VIT25` (tours, $, durée, réflexion, suite, pyright, cliquet, mutants,
relecteur), par fiche puis par niveau, avec les limites dites (un essai par case).
Vérifie par `vlp.py cout` que les essais sont comptés (le chemin de `MET2`). Termine par une
recommandation pour la règle de l'effort, à trancher par l'utilisateur dans `MET7`.
Retire les worktrees, garde les branches.

**Critère de fin**
Le journal porte l'entrée `MET4 — xhigh contre medium` : 8 lignes de tableau, le total des
essais en $ et le même total vu par `vlp.py cout` — les deux s'écrivent côte à côte.
<!-- /FICHE -->

---

<!-- FICHE:MET5 -->
## MET5 [x] — Trier les familles de ruff

**Session** : 240bd893-1e58-426c-bd93-728f652a2820
**Dépend de** : rien.
**Fichiers** : `context AI/08-etat.md` (l'entrée `VIT15` du 2026-10-04), un réglage de ruff à la racine (`ruff.toml` ou `pyproject.toml`, à proposer), une page à cartes — et rien d'autre.

**Prompt**
Ruff est un outil d'atelier : optionnel, avec repli. Relis le compte de `VIT15` (1 069 remarques
sur `vlp.py` et `test-vlp.py`, dont 838 `UP031`) et refais-le sur `scripts/*.py` d'aujourd'hui,
par famille de règles (`ruff check --statistics`).
Une carte par famille qui sort : ce qu'elle demande, en clair, son compte, et trois choix —
l'adopter, la régler, l'écarter —, avec ton avis. Publie, arrête-toi.
Sur les réponses : écris le réglage, et les réponses au journal (`MET5 — ruff trié`).
Ne corrige **aucune** remarque dans le code : c'est le travail de `REF`.

**Critère de fin** (visuel)
L'utilisateur a répondu ; `ruff check scripts/` lit le réglage, et le nombre de remarques
avant → après réglage s'écrit au journal ; `git diff --stat -- scripts/` est vide.
<!-- /FICHE -->

---

<!-- FICHE:MET6 -->
## MET6 [x] — Trier les 21 règles

**Session** : 240bd893-1e58-426c-bd93-728f652a2820
**Dépend de** : rien.
**Fichiers** : `methode-chantier.md`, un fichier de leçons à la racine du kit (nom à proposer), une page à cartes — et rien d'autre.

**Prompt**
« Les règles qui valent partout » compte 21 règles. Certaines servent tout chantier ; d'autres
sont des leçons de mesure nées dans les projets (arrondi, norme d'un vecteur, seuil sur une
distribution). Une carte par règle : son titre en gras, ce qu'elle dit en clair, et trois
choix — **reste** (raccourcie si possible), **part** dans le fichier de leçons, **se fond** dans
une autre qu'on nomme —, avec ton avis. Publie, arrête-toi.
Sur les réponses : range. Une règle qui part garde un renvoi d'une ligne dans la méthode ; une
règle fondue garde son exemple mesuré. Rien ne se perd. Le fichier de leçons s'ouvre sur sa
ligne « QUAND LIRE » ; `CLAUDE.md` et `00-INDEX.md` le déclarent s'il est lu par une session.

**Critère de fin** (visuel)
L'utilisateur a répondu ; chaque titre de règle en gras se retrouve par `grep` à sa nouvelle
place : restées + parties + fondues = 21 ; `methode-chantier.md` avant → après en lignes, au
journal (`MET6 — les règles triées`).
<!-- /FICHE -->

---

<!-- FICHE:MET7 -->
## MET7 [x] — Compléter la méthode

**Session** : 35091dff-73df-4438-8d1f-fc8332923ae8
**Dépend de** : `MET1`, `MET2`, `MET4`, `MET5`, `MET6`.
**Fichiers** : `methode-chantier.md`, `context AI/08-etat.md` (entrées `MET1` à `MET6`) — et rien d'autre.

**Prompt**
Écris dans `methode-chantier.md` une section « Coder dans le kit » : ce que `MET1` a fait
adopter ou adapter (rangement, nommage, patterns), avec sa source ; la règle de style de
`MET5`, qui renvoie au réglage de ruff sans recopier ses règles. Mets à jour la règle de
l'effort avec le résultat de `MET4` — la recommandation, puis ce que l'utilisateur tranche
(une question, posée avant d'écrire). Vérifie que la règle des essais de `MET2` n'existe
qu'à un endroit.
Court : un renvoi vaut mieux qu'une copie ; un chiffre vit à un seul endroit.

**Critère de fin**
`grep -c` des titres de la nouvelle section → 1 dans le kit ; `vlp.py rapide` puis la suite
`OK` ; `methode-chantier.md` avant → après en lignes, au journal (`MET7 — la méthode complétée`).
<!-- /FICHE -->

---

<!-- FICHE:MET8 -->
## MET8 [x] — Aligner les commandes (1/2)

**Session** : 35091dff-73df-4438-8d1f-fc8332923ae8
**Dépend de** : `MET7`.
**Fichiers** : `skills/chantier/SKILL.md`, `skills/tache/SKILL.md`, `skills/enchainer/SKILL.md`, `skills/jouer/SKILL.md`, `skills/relire/SKILL.md`, `agents/fiche.md`, `agents/relecture.md`, `methode-chantier.md` (lecture) — et rien d'autre.

**Prompt**
Relis chaque fichier contre la méthode de `MET7` et cherche deux choses : ce qui la
**contredit**, et ce qui la **recopie** au lieu d'y renvoyer. Corrige les deux ; une option
de commande s'ajoute si la méthode en a besoin (accord de l'utilisateur au cadrage), et le
dit dans sa docstring ou son en-tête. Pas de réécriture de forme : ce qui marche reste.
Les tests verrouillent certains textes (les copies de l'injection de la carte, `hooks.json`) :
un test qui tombe se lit avant d'être changé.

**Critère de fin**
Une table au journal (`MET8 — commandes alignées 1/2`) : par fichier, contradictions et copies
trouvées → corrigées, en comptes bruts ; suite `OK`. Le vrai rejeu d'une commande vient après
la fusion dans `main` (le plugin chargé suit `main`).
<!-- /FICHE -->

---

<!-- FICHE:MET9 -->
## MET9 [x] — Aligner les commandes (2/2)

**Session** : 35091dff-73df-4438-8d1f-fc8332923ae8
**Dépend de** : `MET7`.
**Fichiers** : `skills/init/SKILL.md`, `skills/check/SKILL.md`, `skills/chef/SKILL.md`, `cloture.md`, `nuit.md`, `enchainement.md`, `methode-chantier.md` (lecture) — et rien d'autre.

**Prompt**
Même travail que `MET8`, sur ces six fichiers : ce qui contredit la méthode de `MET7`, ce qui
la recopie au lieu d'y renvoyer, corrigé ; une option ajoutée si la méthode en a besoin. Pas
de réécriture de forme. `nuit.md` et `chef` servent la reprise de `NUI` : ne change pas leur
mécanique, seulement leur accord avec la méthode.

**Critère de fin**
Une table au journal (`MET9 — commandes alignées 2/2`) : par fichier, contradictions et copies
trouvées → corrigées, en comptes bruts ; suite `OK`.
<!-- /FICHE -->

---

<!-- FICHE:MET10 -->
## MET10 [x] — Relire et reclasser la TODO

**Session** : 35091dff-73df-4438-8d1f-fc8332923ae8
**Dépend de** : `MET7`.
**Fichiers** : `context AI/08-etat.md` (« La TODO ordonnée »), une page à cartes, la feuille de route (`vlp.py feuille`) — et rien d'autre.

**Prompt**
Relis chacune des lignes ouvertes de la TODO avec la méthode de `MET7`. Une carte par ligne :
ce qu'elle apporte en clair, son coût ré-estimé (les estimations sous-estiment : `EST` 1 → 3,
`CPT` 2 → 4), et quatre choix — **garder**, **fondre** dans une autre qu'on nomme,
**abandonner**, **re-cadrer** (pour `REF`, n° 96, attendu) —, plus un rang proposé.
Format `gros` du gabarit (`data-format="gros"`). Publie, arrête-toi.
Sur les réponses : reclasse, écris les estimés, fonds ou retire — à l'outil `Edit`, jamais par
un script improvisé (un tel script a déjà vidé `08-etat.md`, ligne `OTE`) ; le texte des
lignes gardées ne change pas ; pas de « | » dans une cellule. Une ligne neuve demande les deux
oui. Régénère la feuille, republie-la.

**Critère de fin** (visuel)
L'utilisateur a répondu ; la carte lit la TODO sans `GARDE:` ; lignes ouvertes avant → après,
et gardées / fondues / abandonnées, au journal (`MET10 — la TODO relue`).
<!-- /FICHE -->
