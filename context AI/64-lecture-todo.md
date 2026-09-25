> **QUAND LIRE** : on joue une fiche `LEC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache LEC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier LEC — `/vlp:chantier` ne lit plus l'état en entier

**À quoi il sert.** L'étape 1 de `/vlp:chantier` lit en entier le fichier d'état (2 137 lignes)
et la méthode (376), quand choisir et cadrer n'en demandent que la TODO et le format des fiches.
La carte les imprimera, avant le premier tour ; la commande ne lira plus le reste.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 5 fiches, `LEC1` à jouer.

**Session** : 44909b3f-749f-48b6-b44b-9fdfb6a43588

## Le socle commun

**Mesuré au cadrage (2026-09-25).** `context AI/08-etat.md` : 2 137 lignes, dont la TODO
356–391 (36) et le journal 393–2137. `methode-chantier.md` : 376 lignes, dont le format des
fiches 288–361 (74) — « Le fichier de fiches », « Anatomie d'une fiche », « Les deux formes de
critère de fin ». Ce compte compare des lignes, pas des tokens : le coût vient de `LEC1`.

**Décidé au cadrage, par l'utilisateur.**

1. La carte imprime TODO et format **seulement quand aucun chantier n'est ouvert** (branche « aucun »).
2. TODO : **toute la section**, du premier titre `## ` qui contient « TODO » jusqu'au `## ` suivant,
   exclu — pour chaque fichier que nomme la ligne **chantiers possibles**.
3. Aucun titre TODO : une ligne `TODO=absente <fichier>` ; la commande lit alors ce fichier.
4. Deux titres TODO dans un fichier : le premier seul.
5. Méthode : de `## Le fichier de fiches` jusqu'au `## ` qui suit `## Les deux formes de critère
   de fin`, exclu. Un des deux titres manque : `METHODE=absente <fichier>`.
6. Preuve : une vraie séance `/vlp:chantier`, avant et après, par `mesure-tokens.py`.

**Sortie de la carte, noms retenus** (LEC4 les cite, rien d'autre ne les invente) :
`--- TODO : <chemin> (lignes A–B) ---`, `TODO=absente <chemin>`,
`--- méthode : <chemin> (lignes A–B) ---`, `METHODE=absente <chemin>`. Chemins tels que
`CHANTIER.md` les écrit.

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `carte` | `scripts/vlp.py:365` | la carte ; la branche « aucun » est à `:381–383` — c'est là qu'on ajoute |
| `COURANT`, `ALIAS` | `scripts/vlp.py:250–251` | modèle des motifs pour les lignes **chantiers possibles** et **méthode** |
| `Absent`, `chemin_garde` | `scripts/vlp.py:299`, `:305` | lecture gardée ; `carte` écrit `GARDE:` et ne lève pas (`:388`) |
| `KIT` | `scripts/vlp.py:654` | racine du kit, repli pour la méthode |
| `todo_du_fichier` | `scripts/vlp.py:2238` | lit la **table** seule, pour `feuille` — pas pour la carte (décision 2) |
| tests | `scripts/test-vlp.py` (`carte` appelée `:60`) | `py scripts/test-vlp.py` |
| mesure | `scripts/mesure-tokens.py:6` | `mesure-tokens.py [--plage DEBUT FIN] <fichier.jsonl \| id>` |

**Les projets équipés, vus au cadrage** (`CHANTIER.md` de chacun) :

| Projet | chantiers possibles | méthode | titre TODO |
|---|---|---|---|
| kit | `context AI/08-etat.md` | `methode-chantier.md` (prose : « à la racine du kit ») | `:356` |
| MapDecorator | `context AI/08-etat.md` | `context AI/09-chantiers.md` | `:120`, hors table |
| ProjetONZSM | `context AI/08-etat.md` | `context AI/09-chantiers.md` | `:29` |
| TrackGen | `context AI/08-etat.md` | `context AI/09-chantiers.md` | `:30` et `:124` |
| Cairn-VlpLib | `20a-chantiers.md`, puis `10-etat.md` | `context AI/21-methode-chantier.md` | aucun (854 l.) ; `:158` (4 500 l.) |

⚠️ Cairn est privé : ni extrait ni titre dans ce dépôt, des comptes et des numéros seulement.

**Ce qu'on ne fait pas.** Sortir le journal dans son propre fichier (écarté au cadrage) ; toucher
l'étape 0 ter, `feuille`, `todo_du_fichier` ou `/vlp:tache` ; alléger le reste de la méthode.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `LEC1` | Mesurer l'avant | rien |
| `LEC2` | Faire imprimer la TODO par la carte | rien |
| `LEC3` | Faire imprimer le format des fiches par la carte | `LEC2` |
| `LEC4` | Brancher `/vlp:chantier` sur la carte | `LEC2`, `LEC3` |
| `LEC5` | Mesurer l'après | `LEC1`, `LEC4` |

`LEC1` et `LEC2` sont indépendantes ; `LEC3` réemploie la fonction de section de `LEC2`.

---

<!-- FICHE:LEC1 -->
## LEC1 [x] — Mesurer l'avant

**Session** : 819d1b08-9d1c-421c-b547-43124bc57994
**Dépend de** : rien.
**Fichiers** : `~/.claude/projects/C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow/*.jsonl`,
`scripts/mesure-tokens.py`, le `CHANTIER.md` et les fichiers du tableau « projets équipés » du
socle (par `grep -n "^## "` seulement), `context AI/08-etat.md` (journal, en fin) — et rien d'autre.

**Prompt**
1. Dans les transcriptions, trouve la dernière séance `/vlp:chantier` du kit qui a lu
   `08-etat.md` en entier (un `Read` sans `offset`, ou plusieurs qui le couvrent). Note son id.
2. Mesure-la de son début au premier appel `AskUserQuestion` :
   `py scripts/mesure-tokens.py --plage <début> <heure du 1er AskUserQuestion> <id>`.
3. Même mesure sur la séance de ce cadrage, `44909b3f-749f-48b6-b44b-9fdfb6a43588`, qui n'a lu que
   la TODO sur consigne de l'utilisateur : un « après » fait à la main.
4. Pour les cinq projets : ligne et longueur de la section TODO selon la décision 2 ; les deux titres
   de méthode de la décision 5 présents ou non. TrackGen : lequel de `:30` et `:124` porte la TODO
   vivante, lignes à l'appui.
5. Écris tout au journal du fichier d'état, sous `## <date> — LEC1`, la date lue par `date`.

**Critère de fin**
Le journal porte l'id de la séance d'avant et ses comptes bruts (`tours`, `ctx_dernier`, `equiv`,
`usd`) sur la plage nommée ; les mêmes pour `44909b3f` ; une table des cinq projets (fichier, ligne
du titre TODO, lignes de la section, titres de méthode trouvés 0–2). Aucune séance d'avant : le
dire, et proposer d'en jouer une — ne rien estimer à sa place.
<!-- /FICHE -->

---

<!-- FICHE:LEC2 -->
## LEC2 [ ] — Faire imprimer la TODO par la carte

**Session** : e41e8069-96d6-419d-8454-665a2f96394b
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris une fonction pure `section(lignes, debut, fin)` → `(a, b)` numéros de ligne 1-basés, ou
`None` : `debut` et `fin` sont des prédicats sur un titre `## `, la section va du premier titre
qui vérifie `debut` jusqu'avant le premier titre `## ` qui **suit** celui qui vérifie `fin` (fin
de fichier s'il n'y en a pas). `None` si aucun titre ne vérifie `debut`, ou aucun après lui ne
vérifie `fin` — `LEC3` en a besoin pour `METHODE=absente`. Un `## ` dans un bloc ```` ``` ```` n'est
pas un titre. `LEC3` la réemploie ; la TODO l'appelle avec `fin` = le titre de début lui-même.
Dans la branche « aucun » de `carte`, après sa ligne `--- fichier de fiches courant : aucun ---`,
lis la ligne **chantiers possibles** (motif à la manière de `COURANT`) et **cherches-y** chaque
chemin en `.md` — backticks ôtés, prose autour ignorée : `` `a.md`, puis `b.md` `` en donne deux,
`context AI/08-etat.md (section TODO)` en donne un ; ne découpe pas sur des séparateurs. Pour
chacun, imprime la sortie du socle (décisions 2 à 4) : l'en-tête `--- TODO : <chemin> (lignes
A–B) ---` **suivi du texte des lignes A à B**, tel quel — c'est lui que `/vlp:chantier` lira à la
place du fichier ; ou `TODO=absente <chemin>`. Fichier introuvable : `GARDE: <chemin>` par
`Absent`, sans lever, et on passe au suivant. Ligne absente : `TODO=absente (pas de ligne
« chantiers possibles »)`. Rien sur la méthode : c'est `LEC3`. Mets à jour l'entrée `carte` de
la docstring de `vlp.py`.

**Critère de fin**
`py scripts/test-vlp.py` passe, dont une fonction `test_carte_todo` bâtie dans un dossier
temporaire, avec ces cas, chacun son `verifier` :
- un fichier à **trois** titres après la TODO et **deux** titres TODO → le premier seul, lignes
  A–B exactes, **et** la dernière ligne du texte de la section présente dans la sortie, la
  première ligne du titre suivant absente ;
- un fichier sans titre TODO → `TODO=absente <chemin>` ;
- une ligne `` `a.md`, puis `b.md` `` → deux blocs, dans l'ordre ;
- un chemin suivi de prose entre parenthèses → un bloc ;
- un fichier nommé mais absent → `GARDE:` et le bloc du suivant quand même ;
- un chantier ouvert → aucun bloc.

Mutant : `section` qui s'arrête au **dernier** `## ` au lieu du suivant — `test-vlp.py` échoue ;
donne la sortie. `py scripts/vlp.py carte` sur une copie du kit dont le fichier de fiches courant
vaut « aucun » imprime `--- TODO : context AI/08-etat.md (lignes A–B) ---` puis B−A+1 lignes, A–B
égales au `grep -n "^## "` du fichier. `pyright scripts/vlp.py scripts/test-vlp.py` : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:LEC3 -->
## LEC3 [ ] — Faire imprimer le format des fiches par la carte

**Dépend de** : `LEC2` (la fonction `section`).
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans la même branche, après les blocs TODO, lis la ligne **méthode** et tires-en le premier
chemin `*.md`. Cherche-le dans le projet, sinon sous `KIT` : la ligne du kit est de la prose
(« `methode-chantier.md`, à la racine du kit »). Imprime la sortie retenue au socle
(décision 5), par `section`. Fichier introuvable dans les deux : `GARDE:`, sans lever.
Complète l'entrée `carte` de la docstring.

**Critère de fin**
`py scripts/test-vlp.py` passe, dont un `test_carte_methode` en dossier temporaire : les trois
sections → lignes exactes, le `## ` qui suit exclu ; `## Les deux formes de critère de fin`
manquant → `METHODE=absente` ; chemin absent du projet, trouvé sous un faux `KIT`. Mutant : fin
au `## ` qui suit le **premier** titre — le premier cas tombe. `py scripts/vlp.py carte` sur le
kit imprime `--- méthode : … (lignes 288–361) ---` si la méthode n'a pas bougé, sinon les lignes
du `grep -n "^## " methode-chantier.md`. `pyright` sur les deux fichiers : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:LEC4 -->
## LEC4 [ ] — Brancher `/vlp:chantier` sur la carte

**Dépend de** : `LEC2`, `LEC3`.
**Fichiers** : `skills/chantier/SKILL.md` (étapes 0 et 1 seulement), `methode-chantier.md`
(la ligne « fichier d'état » de « Où vit quoi ») — et rien d'autre.

**Prompt**
L'étape 1 ne fait plus lire la méthode ni les chantiers possibles en entier : la carte les donne,
sous les noms retenus au socle. Une ligne `TODO=absente` ou `METHODE=absente` : lire ce
fichier-là en entier, comme avant. Le reste de la méthode se pointe, il ne se lit pas d'office.
Ne recopie pas les titres de section : ils vivent dans `vlp.py` (règle 3 de `CLAUDE.md`). Court :
tout ajout se paie à chaque exécution. Ne touche pas à l'étape 0 ter. Dans « Où vit quoi », dis que
le choix du prochain chantier lit la TODO par la carte.

**Critère de fin**
`py scripts/vlp.py lignes skills/chantier/SKILL.md` : 278 avant, le compte après écrit à côté,
sans hausse. `grep -c "en entier"` dans l'étape 1 : 0. `TODO=absente` et `METHODE=absente` y
apparaissent une fois chacun. `.githooks/pre-commit` passe sans `--no-verify`.
<!-- /FICHE -->

---

<!-- FICHE:LEC5 -->
## LEC5 [ ] — Mesurer l'après

**Dépend de** : `LEC1`, `LEC4`.
**Fichiers** : `scripts/mesure-tokens.py`, `context AI/08-etat.md` (journal `LEC1`, puis en fin) —
et rien d'autre.

**Prompt**
Rends la main d'abord : l'utilisateur relance l'app (ou `/reload-plugins`), ouvre une session
neuve, lance `/vlp:chantier` sans argument, s'arrête au premier questionnaire, et te donne l'id
de cette session. Après son retour seulement, mesure-la sur la même plage que `LEC1` (début →
premier `AskUserQuestion`). Écris sous `## <date> — LEC5` une table avant / cadrage à la main /
après, colonnes `tours`, `ctx_dernier`, `equiv`, `usd`, et la ligne qui dit ce qu'elle compare.

**Critère de fin** (visuel)
La table porte trois lignes aux comptes bruts, lues sur les trois ids nommés, et la phrase
« ce compte compare … à … ». L'après ne baisse pas : le dire, sans chercher d'excuse.
<!-- /FICHE -->
