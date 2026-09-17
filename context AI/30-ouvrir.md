> **QUAND LIRE** : on joue une fiche `O*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache O<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier O — Ouvrir et clore par script

**À quoi il sert.** Après le chantier F, l'ouverture et la clôture gardent des écritures mécaniques à la main :
ligne d'index, routage et « Où on en est » de `CLAUDE.md`, lignes de `CHANTIER.md`, « Fait. », `ZONE:bilan`. Un script les écrit.

**Où on en est.** Ouvert le 2026-09-17, aucune fiche jouée.

## Le socle commun

| Nom | Où | Ce que c'est |
|---|---|---|
| index | `context AI/00-INDEX.md` | ligne `` \| `NN-nom.md` \| on relit le socle du chantier L — **clos** « titre », `L1..Ln` \| `` (ouvert : « on joue une fiche `L*` ») |
| routage | `CLAUDE.md`, table « Routage » | ligne `` \| relire le chantier L (titre) \| `context AI/NN-nom.md` — chantier **clos** \| ``, la plus récente en tête des chantiers |
| « Où on en est » | `CLAUDE.md`, section `## Où on en est` | chaîne `Clos le <date> : … (chantier L) ;` puis `  puis … (chantier L) ;`, la dernière finie par `.` |
| `CHANTIER.md` | racine | « **fichier de fiches courant** » (`context AI/NN-nom.md (L1..Ln)`), « **artefact du chantier** », table des clos |
| fichier de fiches | `context AI/NN-nom.md` | sous le titre : `**CLOS** le …` (écrit par `clore`), puis `**Fait.** L1..Ln (<date>) : …` ; `**Où on en est.**` à l'ouverture |
| page du chantier | `context AI/artefacts/NN-nom.html` | `<!-- ZONE:bilan … -->` : `<section hidden>`, `<h2>`, `<p>Livré : …</p>`, `<p>Surpris : …</p>` |
| sous-commande | `scripts/vlp.py` : docstring, `add_parser` dans `main`, une `cmd_*` ; `champ`, `plage`, `lettres_prises`, `cmd_clore` | bilan en une ligne, comptes bruts ; relancée, ne change rien ; `GARDE:` et sort 1 sur refus |
| tests | `scripts/test-vlp.py` | `sh scripts/vlp` n'est pas requis : `python scripts/test-vlp.py` → `OK` ; 73 assertions avant (`grep -cE "^\s*(assert\|verifie\|check)"`) |
| essai réel | scratchpad | `cp -r CHANTIER.md CLAUDE.md "context AI"` dans un bac, script lancé sur le bac, `grep` du résultat, `vlp.py valider` sur le fichier de fiches du bac |

Invariants : le script n'écrit que des fichiers locaux — **publier reste un appel `Artifact`** ; le texte de jugement
(livré, surpris, résumé) arrive en argument, le script ne l'invente pas. Scripts CRLF : Edit passe ; script Python par Write, `PYTHONUTF8=1`.

Dehors : la ligne de bilan et la TODO du fichier d'état (jugement), la section « Où on en est » du fichier d'état,
l'allègement de `CLAUDE.md` (autre chantier), la publication.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `O1` | Mesurer les écritures encore à la main | rien |
| `O2` | Écrire `vlp.py ouvrir` | `O1` |
| `O3` | Étendre `vlp.py clore` : routage, index, « Fait. », `ZONE:bilan` | `O1` |
| `O4` | `vlp.py clore` écrit « Où on en est » de `CLAUDE.md` | `O3` |
| `O5` | Brancher dans `/vlp:chantier` et `cloture.md`, mesurer l'après | `O2`, `O4` |

O2 et O3 sont indépendantes ; O5 vient en dernier.

---

<!-- FICHE:O1 -->
## O1 [x] — Mesurer les écritures encore à la main

**Dépend de** : rien.
**Fichiers** : `context AI/29-feuille.md` et `context AI/28-sans-sh.md` (lignes `**Session**`, par `sh scripts/vlp sessions`), leurs transcripts sous `~/.claude/projects/`.

**Prompt**
Dans les transcripts des chantiers F et X (des sessions complètes : cadrage, fiches, clôture), compte par un script
Python du scratchpad les appels d'outil et les tours (par `message.id`) dont l'entrée nomme : `00-INDEX.md`,
`CLAUDE.md`, `CHANTIER.md`, la ligne `**Fait.**`, `ZONE:bilan` ou la page du chantier (hors appels `Artifact`).
Sépare ouverture et clôture (repère : le commit « ouvert » et le premier appel à `cloture.md`), et compte à part
les refus et les reprises. Note au passage le format exact des lignes écrites, s'il diffère du socle.

**Critère de fin**
Une table de comptes bruts (fichier × F/X × ouverture/clôture : appels, tours, refus) écrite dans ce bloc,
sous « Mesuré », avec le total des tours de chaque session.

**Mesuré** (2026-09-17, script du scratchpad sur les `.jsonl` ; phases : ouverture ≤ commit « ouvert », clôture > dernier commit « faite ») —
appels et tours dont l'entrée nomme la cible (lectures comprises ; un appel à plusieurs cibles compte une fois au total ; page du chantier hors total, déjà scriptée) :

| Session | tours | ouverture : index / CLAUDE.md / CHANTIER.md / Fait. | total ouverture | clôture : index / CLAUDE.md / CHANTIER.md / Fait. / bilan | total clôture | refus |
|---|---|---|---|---|---|---|
| F `52dde2c9` | 64 | 4 / 3 / 3 / 1 | 7 appels, 7 tours | 0 / 1 / 3 / 1 / 1 | 5 appels, 5 tours | 0 |
| X `fd4ebe27` | 77 | 4 / 2 / 2 / 1 | 5 appels, 5 tours | 2 / 2 / 2 / 1 / 1 | 4 appels, 3 tours | 0 |
| O (cette session, ouverture) | 20 | 3 / 3 / 3 / 1 | 8 appels, 7 tours | — | — | 0 |

Soit 10 à 12 tours à la main par chantier (F 12 sur 64, X 8 sur 77). Formats réels (git `be749a8`, `5b01fd9`) : routage ouvert
`| jouer une fiche du chantier L (<titre>) | `<fichier>` — chantier **ouvert**, par `/vlp:tache L<n>` |`, clos `| relire le chantier L (<titre>) | `<fichier>` — chantier **clos** |` ;
index ouvert « on joue une fiche `L*` — chantier **ouvert** « Titre », `L1..Ln` » ; `**Fait.** Rien. Ouvert le <date>…` (X, F) ou `**Où on en est.** …` (O).
<!-- /FICHE -->

---

<!-- FICHE:O2 -->
## O2 [x] — Écrire `vlp.py ouvrir`

**Dépend de** : `O1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `skills/chantier/SKILL.md` (étapes 5 bis et 6, pour le format).

**Prompt**
Ajoute `ouvrir <projet> --fiches <context AI/NN-nom.md> --titre "<titre>" [--artefact <url>]`. Plage et lettre se
lisent dans le fichier de fiches (titres `## L1 [ ] —`). Elle écrit, dans l'ordre :
1. `CHANTIER.md` : « fichier de fiches courant » = `<fichier> (L1..Ln)`, « artefact du chantier » = l'url ou `aucun` ;
2. l'index : la ligne au format du socle (« on joue une fiche `L*` »), après la dernière ligne de fichier ;
3. le routage de `CLAUDE.md` : la ligne ouverte au format mesuré en O1, en tête des lignes « relire le chantier ».
Refuse si un chantier est déjà courant (sauf même fichier : alors met seulement l'artefact à jour — relance sans effet).
Bilan : `OUVERT <lettre> <plage> · index +<n> · routage +<n> — <projet>`. Docstring et tests (refus, relance idempotente).

**Critère de fin**
`python scripts/test-vlp.py` rend `OK`, assertions 73 → N affichées ; sur un bac copié, `ouvrir` puis `grep -c` des trois
écritures = 1 chacune, un second appel laisse `diff -r` vide.
<!-- /FICHE -->

---

<!-- FICHE:O3 -->
## O3 [x] — Étendre `vlp.py clore` : routage, index, « Fait. », `ZONE:bilan`

**Dépend de** : `O1`.
**Fichiers** : `scripts/vlp.py` (`cmd_clore`), `scripts/test-vlp.py`, `cloture.md` (étapes 3 et 4), `templates/artefact-chantier.html` (`ZONE:bilan`).

**Prompt**
Ajoute à `clore` : `--fait "<texte>"`, `--surpris "<texte>"`. En plus de ce qu'elle fait :
1. la ligne `**Fait.** L1..Ln (<date>) : <fait>` (défaut : `--livre`), qui remplace `**Fait.** …` ou `**Où on en est.** …` s'il existe ;
2. l'index et le routage : la ligne ouverte passe au format clos mesuré en O1 (titre du routage gardé) ;
3. la page du chantier (`<contexte>/artefacts/<NN-nom>.html`, même `NN-nom` que le fichier) : `ZONE:bilan` sans `hidden`,
   `<h2>Chantier clos le <date></h2>`, `Livré : <livre>`, `Surpris : <surpris>` (échappés par `esc`) ; `ZONE:blocage` en `hidden`.
Une ligne absente (index, routage, page) : `GARDE:` nommée, le reste s'écrit quand même. Bilan : la ligne `CLOS` gagne ` · routage · index · bilan`.

**Critère de fin**
`python scripts/test-vlp.py` rend `OK`, assertions en hausse sur O2 (comptes affichés) ; bac copié : `clore` lancé,
`grep -c "chantier \*\*clos\*\*"` monte de 1 dans `CLAUDE.md` et l'index, `grep -c "<section hidden" ` baisse de 1 dans la page.
<!-- /FICHE -->

---

<!-- FICHE:O4 -->
## O4 [ ] — `vlp.py clore` écrit « Où on en est » de `CLAUDE.md`

**Dépend de** : `O3`.
**Fichiers** : `scripts/vlp.py` (`cmd_clore`), `scripts/test-vlp.py`, `CLAUDE.md` (section « Où on en est », pour le format).

**Prompt**
Ajoute `--resume "<texte>"` à `clore`. Dans la section `## Où on en est` de `CLAUDE.md` :
si la dernière chaîne commence par `Clos le <même date>`, remplace le `.` final de sa dernière ligne par ` ;` et ajoute
`  puis <texte> (chantier L).` ; sinon ajoute `  Clos le <date> : <texte> (chantier L).` à la fin de la section.
Sans `--resume`, rien ; section absente : `GARDE:`. Relancée (même lettre déjà présente) : rien. Bilan : ` · résumé`.

**Critère de fin**
`python scripts/test-vlp.py` rend `OK`, assertions en hausse sur O3 (comptes affichés) ; bac copié : `grep -c "(chantier <L>)"`
passe de 0 à 1 dans `CLAUDE.md`, et un cas de date différente est testé.
<!-- /FICHE -->

---

<!-- FICHE:O5 -->
## O5 [ ] — Brancher dans `/vlp:chantier` et `cloture.md`, mesurer l'après

**Dépend de** : `O2`, `O4`.
**Fichiers** : `skills/chantier/SKILL.md` (étapes 5 bis et 6), `cloture.md` (étapes 2 à 4), `ARTEFACTS.md`, `.claude-plugin/plugin.json`.

**Prompt**
Dans `/vlp:chantier`, les écritures 1 à 4 de l'étape 6 deviennent un appel `sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" ouvrir …`,
placé avant `feuille`. Dans `cloture.md`, l'étape 2 prend `--fait`, `--surpris`, `--resume` ; l'étape 3 disparaît (écrite par
le script) ; l'étape 4 ne garde que lire et republier. Pointe `ARTEFACTS.md` vers le script. Plugin 3.3.5.
`claude.exe plugin validate .`, `sh scripts/vlp renvois .`, eval `chantier` sous WSL2 (socle : pièges du prompt).

**Critère de fin**
validate OK (1 avertissement voulu), `RENVOIS … 0 absent`, eval chantier 3/3 (tours et coût affichés) ; puis, à la clôture
de ce chantier, les appels à la main comptés comme en O1 sur cette session, affichés à côté des comptes O1.
<!-- /FICHE -->
