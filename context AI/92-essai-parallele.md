> **QUAND LIRE** : on joue une fiche `PAR*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache PAR<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier PAR — Deux chantiers en parallèle : l'essai mesuré

**À quoi il sert.** Le kit suppose un seul chantier à la fois (entrée 58 de `08-etat.md`).
Avant de coder le parallèle, ce chantier mesure un essai réel — deux chantiers du kit en
même temps, dont LOC, chacun dans son worktree — et dit, chiffres à l'appui, si le temps
gagné passe 20 %.

**Fait.** Rien. Ouvert le 2026-09-28, cadré en 4 fiches, `PAR1` à jouer.

**Session** : 1282cde7-5a36-4b45-a08f-53f8ddddea98

## Le socle commun

Tranché au cadrage (2026-09-28, trois questionnaires) ; décisions D1–D6 du matin : entrée 58.

- **Ce chantier mesure, il ne code pas le parallèle.** D2–D5 (réserver, verrou, clôture
  à tour de rôle) ne se codent que si le verdict de `PAR3` passe le seuil. Seule `PAR1`
  touche du code.
- **L'essai** : un chantier du kit dans ce worktree + **LOC** dans le sien (choisi le
  2026-09-28 à la place de MapDecorator, sans mesure : `PAR2`), joués en même temps dans
  deux sessions — geste de l'utilisateur, entre `PAR2` et `PAR3`. Deux sessions au plus.
- **Ce worktree** : LOC y est mis de côté — « fichier de fiches courant » passé à `aucun`
  avant `ouvrir`, qui refuse un second chantier (`scripts/vlp.py:4652`). La copie de LOC,
  dans son worktree, ne bouge pas.
- **La feuille de route en ligne** ne se republie pas d'ici : une fois, après la fusion
  dans `main`. Seule la page de PAR se publie.

**La mesure, fixée avant l'essai** — elle ne change pas en voyant les chiffres :

- **Temps actif** d'un ensemble de transcriptions : leurs lignes horodatées, sous-agents
  compris, sur une seule ligne de temps ; la somme des écarts entre deux lignes voisines,
  sauf ceux de **plus de 30 min** (une pause). 30 min : choix de Claude, dit comme tel ;
  une seule constante, dans `mesure-tokens.py`.
- **Attente** : la part du temps actif où la session attend l'utilisateur — de la ligne
  qui précède un message tapé par lui jusqu'à ce message (un `tool_result` n'en est pas un).
- **Par fiche** : temps actif des sessions d'un fichier de fiches (cadrage compris, comme
  `vlp.py cout`), entre son commit « ouvert » et son commit « clos », ÷ fiches jouées.
- **Série estimée** = Σ (fiches jouées pendant l'essai × min/fiche de son projet).
  **Réel** = temps actif des deux sessions sur une ligne de temps commune.
- **Gain** = 1 − réel ÷ série. **Retenu à partir de 20 %**, si le $/fiche (`vlp.py cout`)
  ne monte pas face à la référence.
- **Référence** : TYP, CHK, FEU, BTN, TAU (`context AI/85-types.md` à `89-un-seul-prix.md`) ;
  les deux côtés de l'essai sont du kit. MapDecorator : **N = 0**, moyenne sans objet — son
  `context AI/` est ignoré par Git (`.gitignore:4`, aucun commit « ouvert »), 0 ligne `**Session**`.

Mesuré par `PAR2` (2026-09-28), cadrage compris — la plage de `vlp.py cout` :

| Chantier | Fiches | Actif (min) | Attente (min) | min/fiche | $/fiche |
|---|---|---|---|---|---|
| TYP | 1 | 8 | 0 | 8,0 | 1,64 |
| CHK | 2 | 9 | 0 | 4,5 | 1,11 |
| FEU | 8 | 112 | 5 | 14,0 | 3,35 |
| BTN | 7 | 205 | 22 | 29,3 | 6,24 |
| TAU | 4 | 76 | 1 | 19,0 | 5,01 |
| **kit** (Σ ÷ Σ fiches) | **22** | **410** | **28** | **18,6** | **4,29** |

Sans cadrage (« ouvert » → « clos ») : 368 min, 24 d'attente, **16,7 min/fiche**. La série de
`PAR3` prend celle qui ressemble à l'essai — chantiers déjà cadrés (LOC l'est) : 16,7 ; sinon
18,6. Choix de Claude, dit comme tel : 18,6 face à un essai sans cadrage gonflerait le gain.

Commandes, depuis la racine du kit (`<X>` le chantier, `<f>` son fichier) : sessions
`py scripts/vlp.py sessions "<f>"` ; fiches `grep -cE "^## <X>[0-9]+ \[x\]" "<f>"` ; actif
`py scripts/mesure-tokens.py --actif --plage <origine> <clos> <sessions…>`, ligne `actif TOTAL`
— `<clos>` : `git log -1 --format=%H --grep="^Chantier <X> clos"` ; `<origine>` : le dernier
commit sans `<X>` avant « Chantier `<X>` ouvert » (`plages`, `scripts/vlp.py:2241`), ou
« ouvert » sans cadrage ; $ `py scripts/vlp.py cout "<f>"`, ligne `TOTAL`.

| Nom | Où | Ce qu'il fait |
|---|---|---|
| `resoudre` | `scripts/mesure-tokens.py:82` | id de session → transcription |
| `sous_agents` | `scripts/mesure-tokens.py:103` | les transcriptions de ses sous-agents |
| `heure` | `scripts/mesure-tokens.py:126` | l'heure d'une ligne, secondes UTC ; None sans `timestamp` |
| `mesurer` | `scripts/mesure-tokens.py:208` | une ligne de colonnes, `--plage` comprise |
| `borne`, `main`, `USAGE` | `scripts/mesure-tokens.py:342`, `:362`, `:359` | bornes ISO ou commit ; options |
| `ecrire`, `iso`, `verifier` | `scripts/test-mesure-tokens.py:177`, `:140`, `:183` | le patron des tests |
| `sessions_entete` | `scripts/vlp.py:775` | les sessions notées en tête d'un fichier de fiches |
| `cout` | `scripts/vlp.py` (docstring `:37`) | le coût, découpé par fiche |

Invariants :

- Une heure écrite vient de l'horloge (`date`) ou d'un commit, jamais estimée ; `--plage`
  lit une borne ISO sans décalage comme l'heure locale : `date`, jamais `date -u`.
- Du Python touché passe `pyright` (compte brut) ; une fiche de code nomme son test et son
  mutant (`methode-chantier.md`, « Anatomie d'une fiche »).
- MapDecorator est lu, jamais écrit.

**Dehors** : le code du parallèle (D2–D5), agent teams (D6, écartés), toute écriture dans
`scripts/vlp.py` ou `scripts/test-vlp.py`, la republication de la feuille de route.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `PAR1` | Compter le temps actif par script | rien |
| `PAR2` | Poser la référence en série | `PAR1` |
| `PAR3` | Mesurer l'essai et rendre le verdict | `PAR2`, l'essai |
| `PAR4` | Prédire la fusion des branches | rien |
| `PAR5` | Revoir avec l'utilisateur l'IHM de `nuit` | rien |

`PAR1` → `PAR2` → essai (geste de l'utilisateur) → `PAR3` ; `PAR4` indépendante, plus
parlante jouée en dernier. `PAR5`, ajoutée le 2026-09-28 à la demande de l'utilisateur,
est une conversation indépendante, plus parlante après `PAR3` : son verdict donne les
chiffres des réglages par défaut.

---

<!-- FICHE:PAR1 -->
## PAR1 [x] — Compter le temps actif par script

**Session** : a0161a66-d517-4617-8abe-c793f1ca1df0
**Dépend de** : rien.
**Fichiers** : `scripts/mesure-tokens.py`, `scripts/test-mesure-tokens.py` — et rien d'autre.

**Prompt**
Ajoute à `mesure-tokens.py` l'option `--actif` : le temps actif et l'attente du socle,
sans rien changer à la sortie par défaut. Chaque fichier donné et ses sous-agents
(`sous_agents`) forment une ligne de temps ; `--plage` s'applique comme pour les tours.
Après les lignes habituelles, imprime :
- par fichier : `actif\t<fichier>\t<min actives>\t<min d'attente>\t<pauses retirées>` ;
- au-delà d'un fichier, `actif\tTOTAL\t…` sur la ligne de temps commune (une minute où
  deux sessions travaillent compte une fois) — c'est le **réel** de l'essai.
Minutes arrondies à l'entier. Le seuil de 30 min est une constante nommée, citée dans la
docstring. Une ligne sans heure ne compte pas et se dit sur stderr, comme `sans heure`.
Mets à jour la docstring (usage, sortie) et `USAGE`.
Tests dans `test-mesure-tokens.py`, transcriptions écrites par `ecrire` avec `iso` :
un écart de 30 min exactement est gardé, un de 31 retiré ; l'attente compte l'écart
jusqu'à un message tapé, pas jusqu'à un `tool_result` ; deux sessions qui se chevauchent
donnent un `TOTAL` plus petit que leur somme ; un sous-agent de 40 min sans ligne du
parent n'est pas une pause.

**Critère de fin**
`py scripts/test-mesure-tokens.py` passe ; les mutants « `>` devient `>=` sur le seuil » et
« sous-agents hors de la ligne de temps » font chacun tomber un test nommé ;
`pyright scripts/mesure-tokens.py scripts/test-mesure-tokens.py` : `0 errors` ;
`mesure-tokens.py --actif <session de cadrage de PAR>` imprime une ligne `actif`, recopiée.
<!-- /FICHE -->

---

<!-- FICHE:PAR2 -->
## PAR2 [x] — Poser la référence en série

**Session** : a0161a66-d517-4617-8abe-c793f1ca1df0
**Dépend de** : `PAR1`.
**Fichiers** : les fichiers de fiches de la référence et les transcriptions (lecture
seule), `context AI/92-essai-parallele.md` (la ligne « Mesuré par PAR2 » du socle) — et
rien d'autre.

**Prompt**
Pose le rythme habituel de chaque projet, avec les définitions du socle. Pour chaque
chantier de la référence :
- ses sessions : les lignes `**Session**` de son fichier de fiches ;
- sa plage : ses commits « Chantier <X> ouvert » et « Chantier <X> clos »
  (`git log --grep`), lus depuis le dossier de son projet ;
- `mesure-tokens.py --actif --plage <ouvert> <clos> <sessions…>`, ligne `actif TOTAL` ;
- `vlp.py cout <fichier>`, ligne `TOTAL` : son $ ;
- ses fiches jouées : les cases cochées.
Côté MapDecorator, prends ses 5 derniers chantiers clos qui notent des sessions ; moins :
tous, et dis combien. Un chantier sans session notée ou sans commit « ouvert » : écarté,
et dit. Fais-le par une boucle jetable dans le dossier temporaire de la session, jamais
commitée : c'est une mesure, pas un outil.
Remplace la ligne « Mesuré par PAR2 » par une table : chantier · fiches · actif (min) ·
attente (min) · min/fiche · $/fiche ; puis, par projet, la moyenne pondérée
(Σ actif ÷ Σ fiches, Σ $ ÷ Σ fiches).

**Critère de fin**
La table du socle porte 5 lignes kit et N lignes MapDecorator (N dit), les deux moyennes,
et sous elle la forme générique des commandes qui l'ont produite ; `vlp.py valider` sur
ce fichier rend `VALIDE`.
<!-- /FICHE -->

---

<!-- FICHE:PAR3 -->
## PAR3 [ ] — Mesurer l'essai et rendre le verdict

**Dépend de** : `PAR2`, et l'essai (geste de l'utilisateur).
**Fichiers** : les transcriptions et les deux fichiers de fiches de l'essai (lecture
seule), `context AI/92-essai-parallele.md` (**Fait.**), `context AI/08-etat.md`
(entrée 58) — et rien d'autre.

**Prompt**
D'abord, demande à l'utilisateur ce qu'il n'a pas dit : les deux chantiers de l'essai,
et ses heures de début et de fin, lues à l'horloge. Pas d'essai joué : arrête-toi, la
fiche reste non faite.
Puis mesure, avec les définitions du socle, sans en changer une :
- réel : `mesure-tokens.py --actif --plage <début> <fin> <sessions des deux fichiers>`,
  ligne `actif TOTAL` ;
- série : fiches jouées dans la plage (leurs commits, dans chaque projet) × min/fiche de
  son projet, lu dans la table de `PAR2` ;
- gain = 1 − réel ÷ série ; $/fiche de chaque côté (`vlp.py cout`) face à sa moyenne ;
- l'attente de chaque session face à celle de sa référence.
Écris le verdict dans **Fait.** et à la fin de l'entrée 58 de `08-etat.md` : les comptes
bruts, le gain, et la suite — « coder D2–D5 » si gain ≥ 20 % et $/fiche pas monté,
sinon « ne pas coder », et pourquoi. Un seul essai : dis que c'est un point, pas une
tendance.

**Critère de fin**
**Fait.** et l'entrée 58 portent : réel (min), série (min), gain (%), $/fiche des deux
côtés face à leur référence, attente par session, verdict — chaque chiffre avec la
commande qui l'a produit ; `vlp.py valider` sur ce fichier rend `VALIDE`.
<!-- /FICHE -->

---

<!-- FICHE:PAR4 -->
## PAR4 [ ] — Prédire la fusion des branches

**Dépend de** : rien.
**Fichiers** : le dépôt Git (lecture seule : aucune fusion, aucun worktree touché),
`context AI/08-etat.md` (entrée 58) — et rien d'autre.

**Prompt**
Prédis ce que donnera la fusion dans `main` de deux branches de chantiers du kit : celle
de ce worktree (PAR) et celle qui porte les commits `LOC*` (`git log --all --grep`).
Sans rien fusionner : `git merge-tree --write-tree --name-only <branche PAR> <branche LOC>`.
Relève :
- les fichiers en conflit, et pour chacun la ligne qui se heurte ;
- les pertes silencieuses, qui fusionnent sans conflit mais mentent après : d'abord la
  ligne « fichier de fiches courant » de `CHANTIER.md`, mise à `aucun` ici alors que LOC
  reste ouvert ; puis l'index, `CLAUDE.md` et la feuille de route ;
- ce que la clôture de chacun réécrira encore : les fichiers communs d'une clôture
  (`git show --stat 2c6a118`, la clôture de TAU).
N'écris qu'un paragraphe, à la fin de l'entrée 58 : « Fusion prédite PAR/LOC (<date>) »,
avec les comptes et la commande. C'est la matière de D5.

**Critère de fin**
L'entrée 58 porte le paragraphe : la commande rejouable, le nombre de fichiers en conflit
(compte brut) et leurs noms, et le cas de `CHANTIER.md` tranché — conflit ou perte
silencieuse ; `git status --short` ne montre que `context AI/08-etat.md`.
<!-- /FICHE -->

---

<!-- FICHE:PAR5 -->
## PAR5 [ ] — Revoir avec l'utilisateur l'IHM de `nuit`

**Dépend de** : rien. Plus parlante après `PAR3` : son verdict et les min/fiche de `PAR2`
donnent les réglages par défaut.
**Fichiers** : `context AI/08-etat.md` (entrée 72 `NUI`, et entrée 58 si `PAR3` est faite),
le gabarit `templates/rapport-choix.html` du kit — et rien d'autre. Aucun code.

**Prompt**
Prépare avec l'utilisateur l'interface de `nuit` comme orchestrateur de chantiers en
parallèle (`NUI` la voit aujourd'hui en série) : commandes, options, réglages par défaut.
Aucune commande du kit ne contient « nuit » à ce jour : tout est à décider.
1. **D'abord, ce que les gens font déjà** — recherche web, selon « Recherche web » et
   « Avant de coder » du `CLAUDE.md` de l'utilisateur (n'en recopie pas les nombres) :
   orchestrer plusieurs sessions Claude Code en parallèle, en worktrees, sans humain, sous une
   borne de budget ; y compris ce que Claude Code fait déjà lui-même. `D6` (agent teams) a été
   écarté au cadrage : si la recherche le remet en cause, dis-le, ne tranche pas. Rends les
   outils trouvés et, à côté, « le coder nous-mêmes » avec son coût.
2. **Puis une page à cartes** (gabarit `rapport-choix.html`), précédée de « Avant de choisir ».
   Une carte par décision, options nommées en mots : la commande — `/vlp:chantier nuit`, ou
   `/vlp:chef nuit`, que l'utilisateur propose (2026-09-28) pour séparer cadrer et orchestrer —
   et ce qu'on tape le soir ; les options (combien en parallèle, la borne de
   la nuit, ce qui est écarté, ce que fait la nuit d'une publication refusée ou d'un chantier
   bloqué) ; les réglages par défaut, chacun avec son chiffre mesuré (`PAR2`, `PAR3`) ou
   « pas mesuré » ; ce qu'on lit le matin. Publie-la en artifact, demande à l'utilisateur d'y
   répondre (bouton Copier), et n'écris rien avant son retour.
3. À son retour, écris les décisions à la fin de l'entrée 72 de `08-etat.md` : une ligne par
   carte — choisi, écarté, pourquoi — puis la ligne de coût de la recherche.

**Critère de fin** (visuel)
L'utilisateur a rendu ses réponses ; l'entrée 72 porte une ligne par carte (compte brut :
cartes, lignes) et la ligne de coût de la recherche ; `vlp.py valider` sur ce fichier rend
`VALIDE` ; `git status --short` ne montre que `context AI/08-etat.md`.
<!-- /FICHE -->
