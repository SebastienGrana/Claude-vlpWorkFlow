> **QUAND LIRE** : on joue une fiche `T*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache T<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier T — Compter les tours, pondérer le coût

**À quoi il sert.** `mesure-tokens.py` additionne chaque ligne `assistant` du
transcript, or un tour d'API s'y écrit sur plusieurs lignes qui répètent le même
`usage` : les totaux publiés comptent ×1,9 et personne ne compte les tours. Le
chantier corrige le compte, rend tours, appels, contexte et coût pondéré, et
écrit la ligne `**Session**` sans deviner.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 5 fiches, `T1` à jouer.

## Le socle commun

**Le transcript** : `~/.claude/projects/<slug du projet>/<id>.jsonl`, une ligne
JSON par événement. Vérifié le 2026-09-17 sur ce projet :

- seules les lignes `type: "assistant"` portent `message.usage`
  (`scripts/mesure-tokens.py:29`) ;
- **un tour = un `message.id`** ; un tour s'écrit sur 1 à 3 lignes `assistant`
  (une par bloc de contenu), chacune avec le **même** `usage`. Mesuré : C1 =
  59 lignes pour 31 ids, M4 = 122 pour 66 ; `requestId` compte pareil ;
- clés de `usage` : `input_tokens`, `output_tokens`,
  `cache_creation_input_tokens`, `cache_read_input_tokens`, et le sous-objet
  `cache_creation.ephemeral_5m_input_tokens` / `.ephemeral_1h_input_tokens`
  (somme = `cache_creation_input_tokens` ; peut manquer sur un vieux
  transcript) ; `message.model` nomme le modèle ;
- un appel d'outil = un bloc `{"type":"tool_use","name":…}` dans
  `message.content` (une liste).

**L'id de session** : `$CLAUDE_CODE_SESSION_ID` — vérifié, vaut le nom du jsonl
courant. `$CLAUDE_SESSION_ID` n'existe pas : l'audit se trompait de nom.

**L'interpréteur** : `python3` est un faux ami sur Windows (stub du Store :
`command -v` le trouve, il ne tourne pas). La seule ligne à mettre dans une
commande, avant tout appel au script :
`PY=$(for p in python3 python; do "$p" -c "" 2>/dev/null && { echo "$p"; break; }; done)`

**Le script** : `scripts/mesure-tokens.py` — `mesurer(chemin)` (l.7) rend un
dict, `main(argv)` (l.48) imprime une table TSV, une ligne par fichier, `TOTAL`
si plusieurs. Python 3 sans dépendance, zéro appel modèle. Ses colonnes à la fin
du chantier, dans cet ordre :
`fichier tours appels ctx_1er ctx_dernier input output cache_creation cache_1h cache_read total equiv usd invalides`
Les cinq anciennes (`input output cache_creation cache_read total`) gardent leur
nom : `cloture.md` et `tache.md` les affichent. `ctx` d'un tour = input +
cache_creation + cache_read. `total` = les quatre comptes, une fois par tour.

**Le test** : `scripts/test-mesure-tokens.py`, sans fixture sur disque — il
écrit un jsonl synthétique dans un dossier temporaire, appelle `mesurer`,
compare. `"$PY" scripts/test-mesure-tokens.py` imprime `OK` et sort 0, ou le
premier écart et sort 1.

**Les lignes `**Session**` existantes** (4, deux formats) :
`context AI/10-mesure.md:105` (`~/…`), `:133` (`C:\…`),
`context AI/11-conso.md:60` et `:98` (`C:\…`). Après T4, une nouvelle ligne
porte l'id seul.

**Où s'affiche le coût** : `commands/tache.md:260-273` (« Coût de la fiche »),
`cloture.md:38-42` (bilan), convention d'affichage
`templates/artefact-chantier.html:8-12`. Rien n'y change dans ce chantier, sauf
l'appel du script et la ligne Session (T4).

**Ce qu'on ne fait pas** : afficher `equiv` ou `usd` sur les pages (chantier R
ou S) ; donner une ligne Session aux fiches jouées par `/vlp:enchainer`
(chantier N) ; recalculer les pages de chantier M et C (archives — une ligne
datée au journal le dit) ; écrire un poids ou un prix de mémoire (T3 les lit
sur la grille).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `T1` | Dédoublonner par tour, et tester | rien |
| `T2` | Compter les appels d'outils, résoudre les chemins | `T1` |
| `T3` | Pondérer le coût : équivalents et dollars | `T1` |
| `T4` | Écrire la ligne Session par la variable | `T2` |
| `T5` | Rejouer les mesures de M et C | `T1`, `T2`, `T3` |

Rien n'est parallélisable : T1, T2, T3 touchent le même script, dans cet ordre ;
T4 change les commandes qui l'appellent ; T5 vient en dernier.

---

<!-- FICHE:T1 -->
## T1 [x] — Dédoublonner par tour, et tester

**Session** : C:\Users\znorr\.claude\projects\C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow\0239e4db-1265-485d-ab3c-bb5097b2ecb8.jsonl
**Dépend de** : rien.
**Fichiers** : scripts/mesure-tokens.py, scripts/test-mesure-tokens.py (à créer)
— et rien d'autre.

**Prompt**
Dans `mesurer`, regroupe les lignes `assistant` par `message.id` : un id = un
tour. Garde l'usage de la **dernière** ligne de chaque id, et compte les ids
dont les usages divergent d'une ligne à l'autre (`divergents`, sur stderr s'il
est > 0 — le socle dit qu'ils sont identiques, vérifie-le au lieu de le croire).
Les quatre comptes et `total` se somment une fois par tour.
Ajoute `tours` (ids distincts), `ctx_1er` et `ctx_dernier` (contexte du premier
et du dernier tour, dans l'ordre du fichier) et `cache_1h` (somme de
`cache_creation.ephemeral_1h_input_tokens`, 0 si absent). Colonnes dans l'ordre
du socle ; `appels`, `equiv`, `usd` n'existent pas encore — ne les ajoute pas.
Écris `scripts/test-mesure-tokens.py` : un jsonl synthétique de 3 tours dont un
sur 3 lignes, une ligne sans usage, une ligne invalide, un `cache_creation`
sans sous-objet ; une assertion par colonne.

**Critère de fin**
`"$PY" scripts/test-mesure-tokens.py` imprime `OK` ; le script sur la session
de `context AI/11-conso.md:60` (C1) rend `tours = 31`, `divergents = 0`, et un
`total` inférieur à 6 406 759 (l'ancien compte). Affiche la table.
<!-- /FICHE -->

---

<!-- FICHE:T2 -->
## T2 [x] — Compter les appels d'outils, résoudre les chemins

**Session** : C:\Users\znorr\.claude\projects\C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow\0239e4db-1265-485d-ab3c-bb5097b2ecb8.jsonl
**Dépend de** : `T1`.
**Fichiers** : scripts/mesure-tokens.py, scripts/test-mesure-tokens.py — et
rien d'autre.

**Prompt**
Compte les blocs `tool_use` de `message.content` par `name`, une fois par
ligne (un bloc n'apparaît que sur une ligne — vérifie-le sur un vrai transcript
avant de sommer). Colonne `appels` = total ; après la table, une ligne par
fichier `<fichier>\tappels\tBash=12 Edit=3 …`, triée par nombre décroissant.
Résous l'argument avant d'ouvrir : `~` → home ; un chemin Windows (`C:\…`,
`C:/…`) tel quel ; un **id seul** (ni séparateur ni `.jsonl`) → le premier
`~/.claude/projects/*/<id>.jsonl` trouvé par glob, erreur nommée si aucun. La
colonne `fichier` garde le nom de base du jsonl.
Étends le test : deux `tool_use` de noms différents sur un tour, et la
résolution d'un id (glob sur un dossier temporaire, `HOME` redirigé).

**Critère de fin**
`"$PY" scripts/test-mesure-tokens.py` → `OK` ; le script appelé avec le seul id
de la ligne `context AI/10-mesure.md:105`, puis avec la ligne `:133` telle
quelle, rend deux lignes de table et une ligne par outil, `appels` > 0.
Affiche-les.
<!-- /FICHE -->

---

<!-- FICHE:T3 -->
## T3 [x] — Pondérer le coût : équivalents et dollars

**Session** : C:\Users\znorr\.claude\projects\C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow\0239e4db-1265-485d-ab3c-bb5097b2ecb8.jsonl
**Dépend de** : `T1`.
**Fichiers** : scripts/mesure-tokens.py, scripts/test-mesure-tokens.py — et
rien d'autre.

**Prompt**
Charge la skill `claude-api` et lis-y la grille : prix d'entrée, de sortie, de
cache lu, de cache écrit 5 min et 1 h, pour chaque modèle que les transcripts
nomment (`grep -oh '"model":"[^"]*"' ~/.claude/projects/*/*.jsonl | sort -u`).
**Rien de mémoire** : chaque nombre du script vient de la grille, date de
lecture en commentaire, dans une seule table.
Deux colonnes : `equiv` = tokens équivalents entrée = input ×1 + cache lu ×
(prix cache lu / prix entrée) + cache 5 min × (idem) + cache 1 h × (idem) +
output × (prix sortie / prix entrée) ; `usd` = la même somme en dollars au prix
du modèle de chaque tour, arrondi au cent. Cache 5 min = `cache_creation` −
`cache_1h`. Modèle absent de la table → `usd` vaut `?` et une ligne sur stderr
le nomme ; `equiv` se calcule quand même si les ratios sont les mêmes pour
tous les modèles de la table — dis-le dans le script, sinon `?` aussi.
Étends le test : un tour dont les quatre comptes valent 1 000, modèle connu,
`equiv` et `usd` attendus calculés dans le test depuis la même table.

**Critère de fin**
`"$PY" scripts/test-mesure-tokens.py` → `OK` ; sur la session de
`context AI/11-conso.md:60`, la table montre `equiv` et `usd` à côté des
comptes bruts, et `equiv` < `total`. Affiche la table et la table de ratios.
<!-- /FICHE -->

---

<!-- FICHE:T4 -->
## T4 [x] — Écrire la ligne Session par la variable

**Session** : 0239e4db-1265-485d-ab3c-bb5097b2ecb8
**Dépend de** : `T2`.
**Fichiers** : commands/tache.md (paragraphe « Coût de la fiche », l.260-273),
cloture.md (l.38-42), CONVENTION-FICHIERS.md (seulement si `grep -n Session`
y trouve la convention) — et rien d'autre.

**Prompt**
Dans `tache.md`, remplace la devinette (« repéré dans un chemin déjà exposé…
scratchpad ») par : `**Session** : <id>`, l'id lu par
`echo "$CLAUDE_CODE_SESSION_ID"` dans le même appel Bash que le script ; si la
variable est vide, pas de ligne, et une phrase qui le dit. Le script reçoit
l'id tel quel (T2 le résout). Les lignes `**Session**` anciennes se passent
telles quelles : rien à convertir.
Dans `tache.md` et `cloture.md`, l'appel devient
`"$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/mesure-tokens.py" …`, précédé de la ligne
portable du socle — une fois, pas deux. Rien d'autre : l'affichage (« les deux
tables brutes ») reste, les nouvelles colonnes s'affichent d'elles-mêmes. Ne
recopie ni nombre ni règle : unité, colonnes et convention vivent ailleurs.

**Critère de fin**
`sed -n '/Coût de la fiche/,/^## 6 bis/p' commands/tache.md | grep -c scratchpad`
rend 0 ; `grep -c CLAUDE_CODE_SESSION_ID commands/tache.md` rend 1 ; et dans
cette session même, `echo "$CLAUDE_CODE_SESSION_ID"` non vide puis le script
sur cet id rendent une table. Affiche les trois sorties.
<!-- /FICHE -->

---

<!-- FICHE:T5 -->
## T5 [x] — Rejouer les mesures de M et C

**Session** : 0239e4db-1265-485d-ab3c-bb5097b2ecb8
**Dépend de** : `T1`, `T2`, `T3`.
**Fichiers** : context AI/08-etat.md (bilans M l.85-88 et C l.104-107, journal),
context AI/12-audit.md (table l.13-44 et la phrase « 51 à 128 tours »),
CLAUDE.md (la parenthèse « mesuré : une fiche = 51–128 tours »), la feuille de
route (URL dans CHANTIER.md : `Artifact` read, puis publish), context
AI/10-mesure.md et 11-conso.md (lecture seule, lignes `**Session**`) — et rien
d'autre.

**Prompt**
Lance le script sur les quatre lignes `**Session**` de M et C, puis sur les
neuf sessions de la table de l'audit (leur id y est tronqué à 8 caractères :
glob `~/.claude/projects/*/<id8>*.jsonl`).
Dans `08-etat.md`, remplace les totaux des deux bilans (M « total 13 030 459 »,
C « total 15 389 496 ») par les nouveaux comptes, et ajoute une ligne datée au
journal : l'ancien script comptait chaque ligne `assistant`, donc ×1,9 ; les
pages de chantier M et C gardent les anciens chiffres, archives. Dans
`12-audit.md`, réécris la table avec les colonnes du script et remplace
« 51 à 128 tours » par la plage mesurée ; même plage dans `CLAUDE.md`.
Dans la feuille de route : colonne Tokens des lignes M et C et le total cumulé,
au format de `templates/artefact-chantier.html:8-12` (E reste « non
mesurable »). Republie avec la même url, sans favicon, label `M et C recomptés`.

**Critère de fin**
La table du script sur les quatre sessions M et C est affichée en entier ;
`grep -n '13 030 459\|15 389 496\|51 à 128\|51–128' "context AI/08-etat.md" "context AI/12-audit.md" CLAUDE.md`
ne rend que la ligne datée du journal ; la feuille de route republiée montre
les nouveaux totaux.
<!-- /FICHE -->
