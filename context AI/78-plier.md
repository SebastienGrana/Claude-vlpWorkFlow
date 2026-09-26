> **QUAND LIRE** : on joue une fiche `PLI*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache PLI<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier PLI — La page de chantier plus courte et lisible

**À quoi il sert.** La page d'un chantier se lit mal quand elle grandit : toutes
les fiches et tout le journal dépliés. Elle se replie — rien n'est coupé — et son
CSS part dans un `vlp.css` joint, que la relecture ne recharge plus (`ALE`).

**Estimé.** 5 fiches · ≈20 $ — ≈3,99 $/fiche sur 65 clos (le 2026-09-27).

**Fait.** Rien. Ouvert le 2026-09-27, cadré en 7 fiches, `PLI1` à jouer.

**Session** : 566269ee-41a6-4c46-a3ce-85d9f2e86a8b

## Le socle commun

**Décidé au cadrage (questionnaire, 2026-09-27).**
- Frontière : les deux gabarits, `vlp.py`, les commandes, et la feuille de route
  **du kit** republiée. Les pages des quatre projets équipés migrent à leur
  prochaine régénération, sans fiche ici.
- `vlp.css` : une source, `templates/vlp.css` du kit ; `vlp.py page` et
  `vlp.py feuille` la **recopient à chaque appel** dans `<contexte>/artefacts/vlp.css`
  (`files` n'accepte qu'une source sous le dossier du projet).
- Chaque publication d'une page passe `files: {"vlp.css": "<contexte>/artefacts/vlp.css"}`,
  **même une republication** : `read` ne rend pas le fichier joint, donc aucun coût
  de relecture (`77-alleger.md`, « Mesures »).
- Repli : une fiche `encours` ou `bloquee` est ouverte, les autres repliées ; le
  journal montre ses **3** dernières entrées, le reste replié ; un chantier clos
  a son bilan **en haut**.
- Mesure : hauteur en écrans d'ordinateur (864 px de haut, 1536 de large) et écart
  de contexte d'un `Artifact read` (`mesure-tokens.py --plage`), avant et après,
  sur la même page : `context AI/artefacts/51-relecture.html` (8 fiches, 7 entrées
  de journal, close).

**Invariant.** Replié, le texte reste dans le HTML : `vlp.py comparer` sur la page
régénérée ne dit **aucune ligne perdue**. La règle vit dans `38-audit-artefacts.md`
(« plus court, jamais au prix d'une information que Claude relit »).

| Symbole | Où | Rôle |
|---|---|---|
| `regenerer` | `scripts/vlp.py:2182` | réécrit les zones d'une page existante |
| `LI_FICHE` | `scripts/vlp.py:1789` | motif d'une fiche dans la page, lu par `comparer` et d'autres |
| `abri_de_page` | `scripts/vlp.py:2340` | relit journal et notes d'une page (amorce `ABR`) |
| `page_du_fichier` | `scripts/vlp.py:2378` | `<dossier>/artefacts/<nom>.html` |
| `feuille`, `page_feuille` | `scripts/vlp.py:2642`, `:2709` | la feuille de route |
| CSS `details.clos` injecté | `scripts/vlp.py:2949-2976` | seul CSS écrit par le script |
| `cmd_clore` (bilan) | `scripts/vlp.py:3325`, `:3415-3437` | rend la `ZONE:bilan` visible |
| `<style>` des gabarits | `templates/artefact-chantier.html:14-62`, `templates/artefact-feuille-de-route.html:11-63` | à sortir |
| CSS déjà extrait | `context AI/artefacts/essai-ale/vlp.css` (47 lignes, page de chantier) | point de départ |
| mesure en écrans | `context AI/38-audit-artefacts.md` § 4, `context AI/38-audit-scripts/replie.py` | montage : charset, viewport, marge nulle |

**Tests.** Dans `scripts/test-vlp.py`, chaque test bâtit son projet dans un
dossier temporaire ; chaque critère de code nomme son mutant. `pyright` sur les
`.py` touchés, zéro erreur.

**Hors chantier.** La base `db` (`BDD`), la feuille en cartes (`FEU`), les boutons
(`BTN`), la republication des pages des projets équipés.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `PLI1` | Mesurer la page avant | rien |
| `PLI2` | Poser `vlp.css` dans le kit | rien |
| `PLI3` | Migrer les pages existantes vers `vlp.css` | `PLI2` |
| `PLI4` | Joindre `vlp.css` à chaque publication | `PLI2` |
| `PLI5` | Replier les fiches | `PLI3` |
| `PLI6` | Replier le journal, bilan en haut | `PLI5` |
| `PLI7` | Mesurer après, republier la feuille | `PLI1`, `PLI4`, `PLI6` |

`PLI1` et `PLI2` sont indépendantes. Jouer `PLI4` **avant** `PLI3` : sinon la page
de ce chantier, régénérée sans `<style>`, se republie sans `vlp.css` joint.

---

<!-- FICHE:PLI1 -->
## PLI1 [x] — Mesurer la page avant

**Session** : 30b330e2-4593-4cb3-8abc-4a109ec7890d
**Dépend de** : rien.
**Fichiers** : `context AI/artefacts/51-relecture.html`, `context AI/38-audit-artefacts.md` (§ 4, le montage), `scripts/mesure-tokens.py`, `context AI/78-plier.md` — et rien d'autre.

**Prompt**
Mesure la page `51-relecture.html` telle qu'elle est, avant tout changement.

1. **Écrans.** Enveloppe une copie comme au § 4 de `38-audit-artefacts.md`
   (charset, viewport, marge nulle), dans le scratchpad. Ouvre-la dans le
   navigateur intégré à 1536 × 864, lis `document.documentElement.scrollHeight`,
   divise par 864.
2. **Tokens.** Publie-la en artefact **jetable** (sans `url`), puis, dans un tour
   à part, lis l'heure (`date`), puis `Artifact read` sur son URL, puis relis
   l'heure. `py scripts/mesure-tokens.py --plage <début> <fin> <session>` : l'écart
   `ctx_dernier − ctx_1er`. Garde l'URL jetable : `PLI7` la republie.

Écris une section `## Mesures` en fin de ce fichier : une table (mesure, commande,
comptes bruts), l'URL jetable, l'id de session.

**Critère de fin**
`grep -c "^## Mesures" "context AI/78-plier.md"` rend 1 ; la table porte la
hauteur en écrans (hauteur brute en px à côté) et l'écart en tokens (`ctx_1er`,
`ctx_dernier` à côté), chacun avec sa commande rejouable.
<!-- /FICHE -->

---

<!-- FICHE:PLI2 -->
## PLI2 [x] — Poser `vlp.css` dans le kit

**Session** : 30b330e2-4593-4cb3-8abc-4a109ec7890d
**Dépend de** : rien.
**Fichiers** : `templates/artefact-chantier.html`, `templates/artefact-feuille-de-route.html`, `context AI/artefacts/essai-ale/vlp.css`, `scripts/vlp.py` (`cmd_page`, `cmd_feuille`, `creer`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Crée `templates/vlp.css` : le CSS des deux gabarits réuni, sans doublon (les
variables `:root` et le mode sombre ne s'écrivent qu'une fois ; pars de
`essai-ale/vlp.css`). Dans chaque gabarit, remplace le bloc `<style>…</style>`
par `<link rel="stylesheet" href="vlp.css">` ; garde le `<link>` des polices et
le commentaire de tête. Le commentaire « Compact volontairement » part avec le
CSS, dans `vlp.css`.

Puis, dans `vlp.py`, `page` et `feuille` recopient `templates/vlp.css` du kit
dans le dossier `artefacts/` de la page, **à chaque appel**, et le disent en une
ligne de sortie (`CSS <chemin>`). Le kit se trouve comme pour les gabarits.

**Critère de fin**
Un test `tester_vlp_css_recopie` : dans un projet temporaire, `page --creer`
puis `feuille` laissent `artefacts/vlp.css` identique octet pour octet à
`templates/vlp.css` ; modifier la copie puis relancer `page` la remet à
l'identique. Mutant : ne copier qu'à `--creer` → le test tombe. `grep -c "<style" templates/artefact-*.html` rend 0 pour les deux. Tests et pyright : comptes bruts.
<!-- /FICHE -->

---

<!-- FICHE:PLI3 -->
## PLI3 [x] — Migrer les pages existantes vers `vlp.css`

**Session** : 30b330e2-4593-4cb3-8abc-4a109ec7890d
**Dépend de** : `PLI2`.
**Fichiers** : `scripts/vlp.py` (`regenerer`, `feuille`, CSS `details.clos` injecté), `templates/vlp.css`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Une page déjà publiée garde son en-tête à la régénération : son `<style>` y
resterait. Quand `page` ou `feuille` régénère une page qui porte un bloc
`<style>…</style>`, remplace-le par le `<link>` de `vlp.css` — une fois, et
jamais deux `<link>`.

Le CSS que `vlp.py` injecte pour `details.clos` et `.resume-clos` passe dans
`templates/vlp.css` ; le script n'écrit plus aucune règle CSS.

**Critère de fin**
Un test `tester_style_migre` : une page à `<style>` (copie du vieux gabarit,
bâtie dans le test) régénérée par `page` n'a plus de `<style>`, a exactement un
`<link rel="stylesheet" href="vlp.css">`, et `comparer` ne dit aucune ligne de
texte perdue ; régénérée deux fois, toujours un seul `<link>`. Mutant : ajouter
le `<link>` sans retirer le `<style>` → le test tombe. `grep -c "details.clos {" scripts/vlp.py` rend 0. Tests et pyright : comptes bruts.
<!-- /FICHE -->

---

<!-- FICHE:PLI4 -->
## PLI4 [x] — Joindre `vlp.css` à chaque publication

**Session** : 30b330e2-4593-4cb3-8abc-4a109ec7890d
**Dépend de** : `PLI2`.
**Fichiers** : `ARTEFACTS.md` (« Où vivent le CSS et les données »), `skills/chantier/SKILL.md`, `skills/init/SKILL.md`, `skills/enchainer/SKILL.md`, `skills/tache/SKILL.md`, `cloture.md` — et rien d'autre.

**Prompt**
La règle vit dans `ARTEFACTS.md`, section « Où vivent le CSS et les données » :
chaque publication d'une page passe `files` avec `vlp.css`, republication
comprise, et pourquoi (socle). Écris-la là, une fois.

Puis, dans chaque endroit qui publie une page (`grep -n "file_path\|Publie\|republi"`
sur les fichiers ci-dessus), ajoute le paramètre `files` à côté de `file_path`,
en une courte mention qui pointe `ARTEFACTS.md` — pas la raison recopiée.

**Critère de fin**
Pour chaque fichier ci-dessus, `grep -c "vlp.css"` rend au moins 1 là où il
publie ; le compte de lignes publiantes et le compte de mentions `vlp.css`
s'affichent côte à côte, par fichier. `py scripts/vlp.py renvois .` ne signale
aucune règle recopiée. `.githooks/pre-commit` passe.
<!-- /FICHE -->

---

<!-- FICHE:PLI5 -->
## PLI5 [x] — Replier les fiches

**Session** : 30b330e2-4593-4cb3-8abc-4a109ec7890d
**Dépend de** : `PLI3`.
**Fichiers** : `scripts/vlp.py` (`regenerer`, `LI_FICHE` et ses lecteurs, `abri_de_page`), `templates/artefact-chantier.html` (`ZONE:fiches`), `templates/vlp.css`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Chaque fiche de la `ZONE:fiches` devient un bloc repliable : son en-tête (id,
titre, état) toujours visible, sa note et son coût dans le corps. Ouvert si
`data-etat` vaut `encours` ou `bloquee`, replié sinon (socle). Garde `data-etat`
et les classes que lisent la barre d'avancement et le CSS.

`LI_FICHE` et tout ce qui lit une fiche dans la page (`grep -n "LI_FICHE\|class=\"fiche\""`)
lisent l'ancienne forme **et** la nouvelle : les pages des projets équipés ne
sont pas encore régénérées. Le gabarit montre la nouvelle forme.

**Critère de fin**
Un test `tester_fiches_repliees` : une page de 3 fiches (faite, encours, à faire)
régénérée a 3 blocs, un seul ouvert, celui en cours ; `comparer` contre
l'ancienne forme ne dit aucune ligne de texte perdue ; une page à l'ancienne
forme se lit encore (mêmes fiches). Mutant : tout ouvrir → le test tombe ; lire
la seule nouvelle forme → le test tombe. Tests et pyright : comptes bruts.
<!-- /FICHE -->

---

<!-- FICHE:PLI6 -->
## PLI6 [ ] — Replier le journal, bilan en haut

**Dépend de** : `PLI5`.
**Fichiers** : `scripts/vlp.py` (`regenerer`, `cmd_clore`, `abri_de_page`), `templates/artefact-chantier.html` (`ZONE:journal`, `ZONE:bilan`), `templates/vlp.css`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans la `ZONE:journal`, les **3** dernières entrées restent visibles ; les
plus anciennes vont dans un bloc replié à la suite, qui dit combien il en
cache. Trois entrées ou moins : pas de bloc. `abri_de_page` relit les entrées
des deux endroits, dans l'ordre.

Quand le chantier est clos (`ZONE:bilan` visible), la section du bilan se place
juste sous l'en-tête, avant les fiches. Garde le marqueur `ZONE:bilan` avec elle.

**Critère de fin**
Un test `tester_journal_replie` : 7 entrées → 3 visibles, 4 dans le bloc
replié, `abri_de_page` en rend 7 dans l'ordre ; 2 entrées → aucun bloc. Un test
`tester_bilan_en_haut` : après `clore`, `ZONE:bilan` précède `ZONE:fiches` dans
la page. Mutants : garder tout visible → le premier tombe ; laisser le bilan en
bas → le second tombe. Tests et pyright : comptes bruts.
<!-- /FICHE -->

---

<!-- FICHE:PLI7 -->
## PLI7 [ ] — Mesurer après, republier la feuille

**Dépend de** : `PLI1`, `PLI4`, `PLI6`.
**Fichiers** : `context AI/78-plier.md` (section `## Mesures`), `context AI/artefacts/51-relecture.html`, `context AI/artefacts/feuille-de-route.html`, `CHANTIER.md` (URL de la feuille) — et rien d'autre.

**Prompt**
Régénère `51-relecture.html` par `vlp.py page`, puis `vlp.py comparer` : aucune
ligne de texte perdue. Refais les deux mesures de `PLI1`, même montage : écrans
repliée (état par défaut) et tout déplié ; tokens, en republiant **l'URL
jetable** de `PLI1` avec `files` (`vlp.css`), puis `read` dans un tour à part.
Ajoute les lignes « après » à la table `## Mesures`.

Puis `vlp.py feuille .`, `read` de la feuille du kit (URL dans `CHANTIER.md`),
republication avec `files`. Demande à l'utilisateur la suppression de l'artefact
jetable.

**Critère de fin** (visuel)
La table `## Mesures` porte avant et après, comptes bruts et commandes ;
`comparer` : 0 ligne perdue. L'utilisateur constate sur claude.ai la feuille de
route du kit et la page jetable stylées (fond crème, cartes), fiches repliées.
<!-- /FICHE -->

## Mesures

Page mesurée : `context AI/artefacts/51-relecture.html` (15 535 octets, 8 fiches,
7 entrées de journal, close). Mesuré le 2026-09-27 par `PLI1`.

| Mesure | Quand | Commande | Comptes bruts | Résultat |
|---|---|---|---|---|
| Hauteur, écrans d'ordinateur | avant | `py envelopper.py "context AI/artefacts/51-relecture.html" pli1-avant.html` (enveloppe de `38-audit-scripts/replie.py:25-27`), servi par `py -m http.server 8765`, navigateur intégré à 1536 × 864, `await document.fonts.ready; document.documentElement.scrollHeight / 864` | `scrollHeight` = 2977 px, `innerHeight` = 864, `innerWidth` = 1536 | **3,45 écrans** |
| Coût d'un `Artifact read` | avant | `date` (22:25:02Z), `Artifact read` dans un tour à part, `date` (22:25:09Z), puis `py scripts/mesure-tokens.py --plage 2026-09-26T22:25:02Z 2026-09-26T22:25:09Z 30b330e2-4593-4cb3-8abc-4a109ec7890d` | `ctx_1er` = 92 462, `ctx_dernier` = 100 257, 2 tours (Artifact=1, PowerShell=1) | **7 795 tokens** |

- URL jetable (à republier par `PLI7`, puis à supprimer) :
  https://claude.ai/artifact/VVNW7buXnTtffssZmd3knk
- Session : `30b330e2-4593-4cb3-8abc-4a109ec7890d`.
- ⚠️ Montage : la fiche renvoyait au « § 4 » de `38-audit-artefacts.md` ; l'enveloppe
  est dans `38-audit-scripts/replie.py:25-27` (§ 1 la cite). Un fichier hors du
  projet ne s'ouvre qu'en instantané figé dans le navigateur intégré : d'où le
  petit serveur local, à refaire tel quel en `PLI7`.
- ⚠️ L'écart contient aussi l'enveloppe que la plateforme ajoute à la lecture
  (en-tête `[Artifact …]`, `<head>` de claude.ai) : même biais avant et après.
