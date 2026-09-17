> **QUAND LIRE** : on joue une fiche `D*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache D<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier D — Fusionner la doctrine

**À quoi il sert.** Cinq fichiers de doc racontent la même histoire, et les
seuils (250, 80, 50) sont recopiés jusque dans les commandes. Le chantier ramène
la doc à trois fichiers et loge chaque nombre dans `scripts/vlp.py`, seul.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 6 fiches, `D1` à jouer.

## Le socle commun

**Cible — trois docs à la racine, pas un de plus :**

| Reste | Absorbe | Disparaît |
|---|---|---|
| `README.md` | `INSTALLATION.md`, `TLDR README.txt` | ces deux-là |
| `methode-chantier.md` (nom **gardé**) | `CONVENTION-FICHIERS.md` | celui-là |
| `ARTEFACTS.md` | — (allégé) | — |

`cloture.md` et `enchainement.md` restent : lus par les commandes, ils sont
seulement nettoyés de leurs doublons.

**Un nombre vit dans `scripts/vlp.py`.** `SEUIL_PAGE = 250` (l. ~364),
`SEUIL_FICHE = 50` (l. ~213) existent ; le seuil du socle (80) n'existe nulle
part en code. `valider` rend `VALIDE|INVALIDE <n> fiches · socle <n> lignes ·
<n> écarts · <n> avertissements` ; `page` rend `PAGE … · N lignes` et une
`GARDE:` au-delà. La doc et les commandes disent « le seuil de `vlp.py` » et
lisent l'avertissement ou la `GARDE:` — elles n'écrivent plus le chiffre.
Tests : `python scripts/test-vlp.py`.

**Une règle vit dans `methode-chantier.md`** (« comptes bruts à côté du
verdict », « un seul endroit ») ; ailleurs, on pointe.

**Mesuré au cadrage (2026-09-17)** — fichiers contenant, dans README,
INSTALLATION, CONVENTION, ARTEFACTS, méthode, cloture, enchainement,
`commands/`, `agents/`, `templates/`, `scripts/`, `hooks/` :

| Motif | Fichiers | Lesquels |
|---|---|---|
| `250` | 6 | CONVENTION, ARTEFACTS, chantier.md, check.md, artefact-chantier.html, vlp.py |
| `80 lignes` | 2 | chantier.md, check.md |
| `comptes bruts` | 9 | README, méthode, cloture, enchainement, check, enchainer, tache, templates/CLAUDE.md, gabarit de fiches |
| `six copies` | 1 | CONVENTION |
| `un seul endroit\|une seule fois` | 5 | CONVENTION, méthode, enchainer, init, tache |

Lignes : README 162, INSTALLATION 163, CONVENTION 121, ARTEFACTS 148,
méthode 127 (721), + TLDR 73. Citent un doc à renommer ou supprimer :
INSTALLATION et CONVENTION → `CLAUDE.md` seul ; README → `templates/CLAUDE.md`,
`CLAUDE.md` ; ARTEFACTS → `vlp.py`. `methode-chantier.md` est cité par trois
commandes, `vlp.py`, trois fixtures d'eval et `templates/CHANTIER.md` : son nom
ne change pas.

**Hors chantier** : `context AI/`, `archive/`, `exemples/` ; renommer
`methode-chantier.md` ; les quatre projets équipés ; la migration vers
`skills/` (TODO n° 8). Après modification : `/reload-plugins`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `D1` | Loger les seuils dans le script | rien |
| `D2` | Fondre CONVENTION-FICHIERS dans la méthode | `D1` |
| `D3` | Fondre INSTALLATION et le TLDR dans le README | rien |
| `D4` | Nettoyer ARTEFACTS, cloture et enchainement | `D1`, `D2` |
| `D5` | Nettoyer les commandes et les gabarits | `D1`, `D2` |
| `D6` | Compter, puis rejouer les evals | `D3`, `D4`, `D5` |

`D3` se joue quand on veut ; `D4` et `D5` sont indépendantes l'une de l'autre.

---

<!-- FICHE:D1 -->
## D1 [x] — Loger les seuils dans le script

**Dépend de** : rien.
**Fichiers** : scripts/vlp.py, scripts/test-vlp.py — et rien d'autre.

**Prompt**
Fais de `vlp.py` la seule source des trois seuils. Ajoute `SEUIL_SOCLE = 80`
à côté de `SEUIL_FICHE`, et fais rendre à `valider` un **avertissement** (pas
un écart) quand le socle le dépasse, sur le modèle de celui de la fiche trop
longue. Retourne le commentaire de `SEUIL_PAGE` : c'est le script qui fait foi,
la doc y renvoie ; le message de `GARDE:` de `page` ne cite plus ARTEFACTS.md.
Mets à jour la docstring (sous-commande `valider`). Ajoute les tests : un socle
de 81 lignes avertit, un de 80 non ; ajuste ceux dont le message a changé.

**Critère de fin**
`python scripts/test-vlp.py` passe en entier — nombre de tests avant/après
affiché ; `grep -n "ARTEFACTS" scripts/vlp.py` ne rend plus le seuil.
<!-- /FICHE -->

---

<!-- FICHE:D2 -->
## D2 [x] — Fondre CONVENTION-FICHIERS dans la méthode

**Dépend de** : `D1`.
**Fichiers** : methode-chantier.md, CONVENTION-FICHIERS.md (supprimé), CLAUDE.md, context AI/00-INDEX.md.

**Prompt**
Porte dans `methode-chantier.md` ce que CONVENTION-FICHIERS dit et que la
méthode ne dit pas encore : les six familles, ce qui reste dans le kit, les
règles, la numérotation, ce qui ne part pas dans git. Ce qui répète la méthode
(les trois temps, le cycle de vie) ne se recopie pas. Les seuils ne sont plus
écrits : « le seuil de `vlp.py` ». La méthode devient l'unique lieu des règles
« comptes bruts » et « un seul endroit ». Supprime CONVENTION-FICHIERS.md, puis
corrige ses renvois : la ligne de routage de `CLAUDE.md` et l'index. Garde la
ligne « **QUAND LIRE** » en tête et le nom du fichier.

**Critère de fin**
`grep -rn "CONVENTION-FICHIERS" --exclude-dir="context AI" --exclude-dir=archive --exclude-dir=exemples .`
ne rend rien ; `wc -l methode-chantier.md` affiché, à comparer à 127 + 121.
<!-- /FICHE -->

---

<!-- FICHE:D3 -->
## D3 [x] — Fondre INSTALLATION et le TLDR dans le README

**Dépend de** : rien.
**Fichiers** : README.md, INSTALLATION.md (supprimé), TLDR README.txt (supprimé), CLAUDE.md, templates/CLAUDE.md.

**Prompt**
Fais du README le seul point d'entrée de qui clone le dépôt. Il garde le
problème, les trois temps en quelques lignes, puis l'installation : le chemin
court par lien, ce que `/vlp:init` demande, vérifier que ça marche, quand le
kit change, le workspace. Le chemin manuel se résume ou disparaît. Ce que le
README racontait de la méthode (anatomie d'une fiche, préfixe, pages) devient un
renvoi d'une ligne à `methode-chantier.md` ou `ARTEFACTS.md`. Le TLDR n'apporte
rien que le haut du README ne dise : supprime-le. Corrige les renvois vers les
fichiers supprimés.

**Critère de fin**
`grep -rn "INSTALLATION\|TLDR" --exclude-dir="context AI" --exclude-dir=archive --exclude-dir=exemples --exclude-dir=.git .`
ne rend rien ; `wc -l README.md` affiché, à comparer à 162 + 163 + 73.
<!-- /FICHE -->

---

<!-- FICHE:D4 -->
## D4 [x] — Nettoyer ARTEFACTS, cloture et enchainement

**Dépend de** : `D1`, `D2`.
**Fichiers** : ARTEFACTS.md, cloture.md, enchainement.md.

**Prompt**
Retire de ces trois fichiers ce qui est dit ailleurs : l'histoire de la méthode,
les règles déjà dans `methode-chantier.md`, et les seuils — `ARTEFACTS.md` dit
« le seuil de `vlp.py` » au lieu de 250, et son « budget de contexte » pointe.
Ne touche ni aux titres de section que les commandes citent, ni aux étapes
numérotées de `cloture.md` : cherche d'abord qui les cite
(`grep -rn "cloture.md\|ARTEFACTS" commands agents scripts`). Chaque fichier
garde ce qui lui est propre.

**Critère de fin**
`grep -n "250\|comptes bruts\|un seul endroit" ARTEFACTS.md cloture.md enchainement.md`
ne rend que des renvois, cités un par un ; `wc -l` des trois affiché avant/après.
<!-- /FICHE -->

---

<!-- FICHE:D5 -->
## D5 [ ] — Nettoyer les commandes et les gabarits

**Dépend de** : `D1`, `D2`.
**Fichiers** : commands/*.md, templates/artefact-chantier.html, templates/CLAUDE.md, templates/context AI/fichier-de-fiches.md.

**Prompt**
Les commandes cessent d'écrire les seuils : `chantier.md` (étape 6) et
`check.md` (repères) lisent l'avertissement de `valider` et la `GARDE:` de
`page` au lieu de comparer à 80 et 250. Retire le commentaire « ~250 lignes »
du gabarit HTML. Là où une commande répète une règle de la méthode (« comptes
bruts », « un seul endroit »), garde l'ordre d'agir en quelques mots et retire
la justification. Tout ajout se paye à chaque exécution : le texte ne doit que
raccourcir. Ne touche pas aux étapes, titres ni marqueurs que `vlp.py` lit.

**Critère de fin**
`grep -rn "250\|80 lignes" commands templates` ne rend rien ;
`wc -l commands/*.md` affiché avant/après, chaque total inférieur ou égal.
<!-- /FICHE -->

---

<!-- FICHE:D6 -->
## D6 [ ] — Compter, puis rejouer les evals

**Dépend de** : `D3`, `D4`, `D5`.
**Fichiers** : aucun à modifier, sauf correction d'un écart trouvé.

**Prompt**
Rejoue la mesure du socle (mêmes motifs, même périmètre, sans les fichiers
supprimés) et pose la table avant/après. Attendu : trois docs `.md` de doctrine
à la racine plus `cloture.md` et `enchainement.md` ; `250` et `80` dans
`scripts/` seul ; « comptes bruts » et « un seul endroit » définis dans la
méthode seule — tout autre fichier qui les porte est justifié en une ligne ou
corrigé. Lance `claude plugin validate`, puis la suite d'evals Windows avec la
commande de `context AI/18-evals.md` (« Lancer — toujours ainsi »), et relève
`costUsd` et `turns` de `aggregate-result.json`.

**Critère de fin**
La table des comptes bruts avant/après ; `validate` propre ; suite d'evals 3/3,
avec coût et tours affichés à côté de la référence V4 (3 runs, 39 tours, 0,93 $).
<!-- /FICHE -->
