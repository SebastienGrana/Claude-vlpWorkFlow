> **QUAND LIRE** : on joue une fiche `J*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache J<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier J — Des fichiers de tête qui ne grossissent plus

**À quoi il sert.** `CLAUDE.md` (117 lignes, visé 60), `CHANTIER.md` (71, visé 30) et l'index (60, visé 40) grossissent
à chaque `vlp.py clore`. Des seuils dans `vlp.py`, une clôture qui compacte, et le kit remis sous seuil.

**Où on en est.** Ouvert le 2026-09-17, cadré en 4 fiches, `J1` à jouer.

## Le socle commun

| Nom | Où | Ce que c'est |
|---|---|---|
| seuils existants | `scripts/vlp.py` : `SEUIL_FICHE`, `SEUIL_SOCLE` (~l. 263), `SEUIL_PAGE` (~l. 420) | un seuil vit là et nulle part ailleurs ; la doc dit « le seuil de `vlp.py` » |
| `renvois` | `vlp.py` `cmd_renvois` (~l. 754), appelée par `/vlp:check` (étape H) | `RENVOIS <n> nommés · <n> absents`, sort 1 si absent |
| `ouvrir` | `vlp.py` `cmd_ouvrir` (~l. 1132) | routage inséré **avant la première** ligne `\| relire le chantier` de `CLAUDE.md` ; index après le plus grand numéro |
| `clore` | `vlp.py` `cmd_clore` (~l. 950), `resume_claude` (~l. 930) | routage ouvert → « relire le chantier L » ; chaîne `Clos le … ;` / `  puis … (chantier L).` dans « Où on en est » ; ligne ajoutée à la table `\| Fichier de fiches \|` de `CHANTIER.md` ; lettre ajoutée à « Lettres de fiche déjà prises » |
| lettres | `vlp.py` `lettres_prises` (~l. 801), lue par `feuille` | motif `X (Titre)` entre « Lettres de fiche déjà prises » et « Un nouveau chantier » : **ne change pas** |
| « longueur visée » | `methode-chantier.md`, table « Où vit quoi » | écrit 60 / 30 / 40 en dur : à remplacer par « le seuil de `vlp.py` » |
| gabarits | `templates/CLAUDE.md`, `templates/CHANTIER.md`, `templates/context AI/00-INDEX.md` | ce que `/vlp:init` pose dans un projet neuf |
| tests | `scripts/test-vlp.py` | `python scripts/test-vlp.py` → `OK` ; 92 assertions avant (`grep -cE "^\s*(assert\|verifie\|check)"`) |
| essai réel | scratchpad | `cp -r CHANTIER.md CLAUDE.md "context AI"` dans un bac, script lancé sur le bac, `wc -l` avant/après, `diff`, relance + `diff -r` vide |

**Frontière retenue au cadrage.** L'index garde tout l'historique des clos (c'est le filet). `CLAUDE.md` ne garde, pour les
clos, qu'**une** ligne de routage « relire un chantier clos → `context AI/00-INDEX.md` » ; « Où on en est » garde les derniers
clos seulement (nombre = constante de `vlp.py`). `CHANTIER.md` perd sa table des clos : la ligne des lettres reste,
les URL des pages closes restent sur la feuille de route. Le fichier d'état et git gardent le reste.

Invariants : relancé, un script ne change rien ; comptes bruts dans chaque sortie ; `GARDE:` sur refus.
Scripts CRLF : Edit passe ; script Python par Write, `PYTHONUTF8=1`. Une écriture par script échappe au hook : relancer `valider`.

Dehors : le fichier d'état (libre), les skills autres que `init` et `check`, `/vlp:chantier` (autre chantier), la TODO n° 16.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `J1` | Mesurer la croissance des trois fichiers | rien |
| `J2` | Poser les seuils dans `vlp.py`, avertis par `renvois` | `J1` |
| `J3` | `ouvrir` et `clore` compactent au lieu d'empiler | `J2` |
| `J4` | Remettre le kit sous seuil, doc et gabarits | `J3` |

Aucune n'est parallélisable : chacune fixe ce que la suivante écrit.

---

<!-- FICHE:J1 -->
## J1 [ ] — Mesurer la croissance des trois fichiers

**Dépend de** : rien.
**Fichiers** : `CLAUDE.md`, `CHANTIER.md`, `context AI/00-INDEX.md` (par `git show <commit>:<fichier>`), `git log --grep="clos :"`.

**Prompt**
Pour chacun des 8 derniers commits « Chantier … clos », compte les lignes et les octets des trois fichiers
(`git show <c>:<f> | wc -lc`), et la part de chaque section (« Où on en est », « Routage », table des clos, lignes de
l'index « **clos** »). Déduis la croissance par chantier. Estime ce qu'ils pèsent en tokens (octets / 3,5, dis-le) et
en coût sur une session de 67 tours (O) au prix de lecture en cache — l'estimation se dit estimation.
Propose les trois seuils et le nombre de clos gardés dans « Où on en est », à partir de ces comptes.

**Critère de fin**
Un bloc « **Mesuré** » sous cette fiche : table commit × fichier (lignes, octets), croissance par chantier, estimation
de coût, et les seuils retenus avec leur raison.
<!-- /FICHE -->

---

<!-- FICHE:J2 -->
## J2 [ ] — Poser les seuils dans `vlp.py`, avertis par `renvois`

**Dépend de** : `J1`.
**Fichiers** : `scripts/vlp.py` (seuils, `cmd_renvois`, docstring), `scripts/test-vlp.py`, `skills/check/SKILL.md` (étape H).

**Prompt**
Ajoute près des autres seuils `SEUIL_CLAUDE`, `SEUIL_CHANTIER`, `SEUIL_INDEX` et le nombre de clos gardés, aux valeurs
du bloc « Mesuré » de J1. `renvois` écrit en plus une ligne `POIDS CLAUDE.md <n>/<seuil> · CHANTIER.md <n>/<seuil> ·
index <n>/<seuil>` et un `AVERTISSEMENT:` par fichier au-delà — son code de sortie ne change pas (un poids n'est pas
un renvoi mort). Docstring à jour ; tests : sous seuil, au-delà, fichier absent. Dans `/vlp:check` étape H, une phrase
au plus pour dire que `POIDS` avertit.

**Critère de fin**
`python scripts/test-vlp.py` → `OK`, assertions 92 → n affichées ; `sh scripts/vlp renvois .` sur le kit montre la
ligne `POIDS` avec les trois comptes bruts (au-delà : 3 avertissements attendus avant J4).
<!-- /FICHE -->

---

<!-- FICHE:J3 -->
## J3 [ ] — `ouvrir` et `clore` compactent au lieu d'empiler

**Dépend de** : `J2`.
**Fichiers** : `scripts/vlp.py` (`cmd_ouvrir`, `cmd_clore`, `resume_claude`, docstring), `scripts/test-vlp.py`.

**Prompt**
Selon la frontière du socle : `clore` **retire** la ligne « jouer une fiche du chantier L » du routage (plus de
« relire le chantier L ») ; `resume_claude` ne garde que les derniers clos (constante de J2), le plus ancien sorti ;
`clore` n'ajoute plus de ligne à la table des clos de `CHANTIER.md` — table absente acceptée, plus de `GARDE:` ; la
lettre et l'index restent écrits. `ouvrir` insère le routage avant la ligne « relire un chantier clos », sinon avant
la première « relire le chantier » (projets pas encore compactés). Tests mis à jour : vérifie l'attendu d'un test
qui échoue avant d'accuser le script.
Essai réel sur une copie du projet dans le scratchpad : `ouvrir` puis `clore` d'un faux chantier, `wc -l` des trois
fichiers avant et après, relance + `diff -r`.

**Critère de fin**
`OK`, assertions affichées ; sur la copie compactée à la main : `CLAUDE.md` et `CHANTIER.md` ont le même `wc -l` avant
`ouvrir` et après `clore` (index +1), `diff -r` de la relance vide, `vlp.py valider` sur le fichier de fiches du bac `VALIDE`.
<!-- /FICHE -->

---

<!-- FICHE:J4 -->
## J4 [ ] — Remettre le kit sous seuil, doc et gabarits

**Dépend de** : `J3`.
**Fichiers** : `CLAUDE.md`, `CHANTIER.md`, `context AI/00-INDEX.md`, `methode-chantier.md` (« Où vit quoi »),
`templates/CLAUDE.md`, `templates/CHANTIER.md`, `skills/init/SKILL.md` (l. ~131), `cloture.md` (étape 2), `.claude-plugin/plugin.json`.

**Prompt**
Compacte les trois fichiers du kit selon la frontière du socle (routage des clos → une ligne vers l'index ; « Où on en
est » aux derniers clos ; table des clos de `CHANTIER.md` retirée) ; l'index garde ses lignes. Dans la méthode, la colonne
« Longueur visée » dit « le seuil de `vlp.py` ». Gabarits et `/vlp:init` sans table des clos ; `cloture.md` ne parle
plus d'« ajouter la ligne des clos » de `CHANTIER.md`. Plugin 3.3.6.
`claude.exe plugin validate .`, `sh scripts/vlp renvois .`, `sh scripts/vlp feuille . --verifier` ; eval `chantier`
sous WSL2 seulement si `skills/chantier/` a changé (sinon dis pourquoi elle n'est pas rejouée).

**Critère de fin**
`POIDS` sans avertissement pour `CLAUDE.md` et `CHANTIER.md` (comptes avant/après affichés), `RENVOIS … 0 absent`,
validate OK (1 avertissement voulu), feuille `identique`.
<!-- /FICHE -->
