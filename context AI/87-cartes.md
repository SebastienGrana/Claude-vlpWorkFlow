> **QUAND LIRE** : on joue une fiche `FEU*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache FEU<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier FEU — La feuille de route plus courte et lisible

**À quoi il sert.** La TODO de la feuille de route est un tableau où chaque rang déroule tout son
texte : 14,05 écrans d'ordinateur pour Cairn (maquette du 2026-09-23). En cartes, l'étiquette
visible et le détail replié, plus un sommaire : 3,84 écrans visés, rien de retiré.

**Estimé.** 4 fiches · ≈17 $ — ≈4,13 $/fiche sur 74 clos (le 2026-09-27).

**CLOS** le 2026-09-27. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** FEU1..FEU8 (2026-09-27) : Feuilles du kit et de Cairn en cartes (TODO repliee, sommaire, detail des chantiers possibles) ; Cairn 3,15 ecrans fermee (etait 13,79) ; TODO ne defile plus a 375x812 ; page_vs_source rangs=entiers=16 — estimé 4 fiches ≈17 $ (taux plat) · cadré 8 · joué 8 fiches 26,77 $.

**Session** : bc14fab5-1e0d-472c-908e-b6dfeefa2dfd

## Le socle commun

**Décidé au cadrage (page à cartes, 2026-09-27).**
- Carte fermée = **étiquette seule** : rang, cellule « Chantier » (badge « en cours » compris),
  coût, dépendance. « Ce qu'il apporte », entier, dans le détail replié (Q1).
- Sommaire : **trois liens** en haut de la feuille, vers les sections d'`id` `encours`, `todo`,
  `clos` (Q4). Pas de script.
- Republiées ici : la feuille **du kit** et celle de **Cairn**. MapDecorator, ProjetONZSM, TrackGen
  passent en cartes à leur prochain `vlp.py feuille`, sans fiche (Q2) : d'ici là, `niveau` y dit
  1 écart « feuille », attendu.
- `page_vs_source.py` et `rejeu.py` lisent les cartes (Q3).

**La forme cartes.** La zone TODO devient une liste, délimitée par `<ol class="todo">\n` et
`        </ol>` ; **une ligne par carte** :
`<li class="carte-todo"><details><summary><span class="rang mono">N</span><span class="titre">…badge…</span><span class="meta mono">coût · dépend de : …</span></summary><div class="detail">…</div></details></li>`.
Liste vide : `<li class="rien">Rien en attente.</li>`. Chaque texte passe par `cellule_md`,
comme dans le tableau.

**Invariants.**
- Replié, pas retiré : chaque cellule de la TODO du fichier d'état est dans la page, texte
  identique (rapport de nuit, Q8).
- Une feuille d'avant, TODO en tableau, se lit encore et se convertit ; badge « en cours » gardé.
- ⚠️ Aucune lecture de la TODO ne déborde : `zone()` cherche son délimiteur **sans borne** après le
  marqueur. Sur une page en cartes, il trouverait le `<tbody>` de `ZONE:clos`, et `feuille()` y
  écrirait la TODO. Borne : le prochain `<!-- ZONE:`.
- Une carte n'a jamais `class="fiche"` : `LI_FICHE` la lirait comme une fiche. Même allure par
  sélecteurs partagés dans `vlp.css`, sans recopier les règles.
- `vlp.css` : une source, `templates/vlp.css`, que `feuille` recopie dans `<contexte>/artefacts/` ;
  toute publication passe `files: {"vlp.css": "<contexte>/artefacts/vlp.css"}`.
- Cairn est privé : ici, des comptes et des numéros, jamais un extrait de sa TODO.
- Autre projet : `git check-ignore` avant de réécrire sa feuille ; `Artifact read` de la version
  en ligne, puis `vlp.py comparer` en ligne → locale, jamais contre le disque.

| Symbole | Où (2026-09-27, à regrepper) | Rôle |
|---|---|---|
| `zone` | `scripts/vlp.py:2858` | (début, fin) entre deux délimiteurs après `ZONE:nom`, sans borne |
| `todo_du_fichier` | `scripts/vlp.py:2839` | les rangs de la TODO du fichier d'état |
| `feuille` | `scripts/vlp.py:2870` ; zone `:2893`, badge relu `:2895` | régénère encours, TODO, lettres |
| `compte_todo`, `RESUME_TODO` | `scripts/vlp.py:2917-2937` | le décompte au-dessus de la TODO |
| `BADGE_COURS`, `LI_FICHE` | `scripts/vlp.py:2742`, `:1904` | badge « en cours » ; motif d'une fiche |
| `markdown_brut` | `scripts/vlp.py:3511` | lit todo, encours, clos |
| garde de `cmd_clore` | `scripts/vlp.py:3931` | la zone TODO doit exister avant d'écrire |
| `migrer_feuille` | `scripts/vlp.py:3289`, appelée `:3627` | migre les clos d'une feuille d'avant |
| `comparer`, `BLOC` | `scripts/vlp.py:3339` | texte visible, découpé au `tr`, `li`, `div`, `p` |
| gabarit | `templates/artefact-feuille-de-route.html:33-54` | la section TODO |
| tests de la feuille | `scripts/test-vlp.py:1010-1040`, `:2360-2376` | rendu de la TODO ; `VOI1` |
| outils d'audit | `context AI/38-audit-scripts/page_vs_source.py:96`, `rejeu.py:42` | même lecture, sans borne |
| mesure en écrans | `context AI/78-plier.md`, `## Mesures` | enveloppe, `py -m http.server`, 1536 × 864 |

**Tests.** Dans `scripts/test-vlp.py`, chaque test bâtit son projet dans un dossier temporaire
(`vlp.py` chargé par son chemin, `test-vlp.py:28`) ; chaque critère de code nomme son mutant.
`pyright` : zéro erreur sur les `.py` touchés — un fichier qui en porte déjà : jamais une de plus.

**Hors chantier.** La table des clos (reste un tableau) ; la typographie (celle de `vlp.css`) ;
les boutons (`BTN`) ; la base `db` (`BDD`) ; les trois petites feuilles (Q2).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `FEU1` | Mesurer les feuilles avant | rien |
| `FEU2` | Lire la zone TODO sans déborder | rien |
| `FEU3` | Écrire la TODO en cartes | `FEU2` |
| `FEU4` | Poser le sommaire | `FEU3` |
| `FEU5` | Faire lire les cartes aux outils de l'audit | `FEU3` |
| `FEU7` | Un lien vers la feuille de route sur la page du chantier | rien |
| `FEU8` | Le détail des chantiers possibles | rien |
| `FEU6` | Régénérer, mesurer après, republier | `FEU1`, `FEU4`, `FEU5`, `FEU8` |

`FEU1` et `FEU2` sont indépendantes, `FEU4` et `FEU5` aussi. `FEU2` avant toute carte : sans
elle, la première feuille en cartes verrait sa TODO écrite dans la table des clos. `FEU7` et
`FEU8`, ajoutées le 2026-09-27 sur deux commentaires de l'utilisateur, passent avant `FEU6` :
elle republie la feuille une seule fois, décompte compris.

---

<!-- FICHE:FEU1 -->
## FEU1 [x] — Mesurer les feuilles avant

**Session** : bc14fab5-1e0d-472c-908e-b6dfeefa2dfd
**Dépend de** : rien.
**Fichiers** : `context AI/87-cartes.md` (section `## Mesures`), `context AI/78-plier.md` (`## Mesures`, le montage), `context AI/38-audit-scripts/page_vs_source.py`, `scripts/mesure-tokens.py`, `CHANTIER.md` et `../Cairn-VlpLib/CHANTIER.md` (URL des feuilles) — et rien d'autre.

**Prompt**
Mesure la feuille du kit et celle de Cairn **telles qu'elles sont en ligne**, avant tout code.

1. **Lecture.** Un tour à part par feuille : `date`, `Artifact read` sur son URL, `date` ; puis
   `py scripts/mesure-tokens.py --plage <début> <fin> <session>` : l'écart `ctx_dernier − ctx_1er`.
   Garde le fichier sauvé : c'est aussi la base de `comparer` en `FEU6`.
2. **Écrans.** Même montage que `PLI1` (`78-plier.md`, `## Mesures`), `vlp.css` à côté :
   `await document.fonts.ready`, `scrollHeight / 864`, à 1536 × 864.
3. **Défilement de côté.** Même page : `scrollWidth > innerWidth` pour la page, puis pour chaque
   `.tableau`, `scrollWidth > clientWidth` — dis lequel défile, TODO ou clos.
4. **Rien de perdu, départ.** `py "context AI/38-audit-scripts/page_vs_source.py" ../Cairn-VlpLib "context AI"` :
   la ligne `feuille · TODO : rangs … · toutes cellules entières ailleurs …`.

Écris `## Mesures` en fin de ce fichier : une table (mesure, feuille, commande, comptes bruts,
résultat), le nombre de rangs de chaque feuille, l'id de session. Cairn : des comptes seulement.

**Critère de fin**
`grep -c "^## Mesures" "context AI/87-cartes.md"` rend 1 ; pour chaque feuille, la table porte les
écrans (px bruts à côté), le défilement de côté par tableau, l'écart en tokens (`ctx_1er`,
`ctx_dernier` à côté) ; pour Cairn, la ligne de `page_vs_source.py` ; chaque ligne a sa commande.
<!-- /FICHE -->

---

<!-- FICHE:FEU2 -->
## FEU2 [x] — Lire la zone TODO sans déborder

**Session** : bc14fab5-1e0d-472c-908e-b6dfeefa2dfd
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris `zone_todo(html)` : `(début, fin, forme)` du contenu de `ZONE:todo`, forme `"tableau"`
(entre `<tbody>\n` et `        </tbody>`, l'ancienne) ou `"cartes"` (délimiteurs du socle). La
recherche s'arrête au prochain `<!-- ZONE:` : un délimiteur trouvé au-delà ne compte pas ;
aucune des deux formes dans la zone → `ValueError`, jamais la zone suivante.

Fais-y passer toutes les lectures de la TODO : `feuille` (bornes, et le badge « en cours »
relu dans les deux formes — une carte le porte dans son `summary`), `markdown_brut`, la garde de
`cmd_clore`, le test `VOI1`. `feuille` écrit encore des lignes de tableau : les cartes, c'est
`FEU3`. Une docstring courte ; la ligne de `zone_todo` dans la docstring du module si elle liste
les fonctions.

**Critère de fin**
Nouveau test dans `test-vlp.py`, pages bâties en mémoire : une feuille en cartes (une carte, badge
compris) suivie d'une `ZONE:clos` à `<tbody>` → forme `"cartes"`, `fin` avant `<!-- ZONE:clos`,
badge relu sur le bon rang ; la même en tableau → mêmes bornes que `zone(html, "todo", …)` ;
une zone sans aucune des deux formes → `ValueError`. Mutant : la borne retirée et `"tableau"`
essayé d'abord → le cas « cartes » rend le `<tbody>` des clos, le test tombe. Tous les tests verts ;
`pyright` 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:FEU3 -->
## FEU3 [x] — Écrire la TODO en cartes

**Session** : bc14fab5-1e0d-472c-908e-b6dfeefa2dfd
**Dépend de** : `FEU2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `templates/artefact-feuille-de-route.html`, `templates/vlp.css` — et rien d'autre.

**Prompt**
`feuille` écrit la zone TODO en cartes, forme du socle, une ligne par carte : étiquette = rang,
cellule « Chantier » (+ `BADGE_COURS`), coût, dépendance ; « Ce qu'il apporte » dans le détail.
Une feuille en forme `"tableau"` se convertit : tout le bloc `<div class="tableau">` de la zone
laisse place à la liste, badge gardé. Le décompte `resume-todo` reste juste au-dessus.

Le gabarit passe en cartes (une carte d'exemple, à `&lt;…&gt;` comme le reste). Dans
`templates/vlp.css`, les cartes prennent l'allure d'une `.fiche` repliée (fond, bordure,
flèche ▸ / ▾) en ajoutant `.carte-todo` aux sélecteurs existants ; `.meta` en petit, doux.
Dans la docstring de `feuille`, « au-dessus du tableau » devient « au-dessus des cartes ».

**Critère de fin**
Nouveau test dans `test-vlp.py` : une feuille d'avant en tableau, badge « en cours » sur un rang,
bâtie dans un dossier temporaire. Après `feuille` : plus de `<table>` dans la zone TODO ; n cartes
pour n rangs ; chaque cellule, passée par `cellule_md`, présente telle quelle ; badge sur la bonne
carte ; 2e appel `inchangée` ; `vlp.py vigile` sur la page : `PAGE SAINE`. Mutant : le détail
omis → le test tombe. Les tests de `test-vlp.py:1010-1040` passés à la forme cartes ; tous verts ;
`pyright` 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:FEU4 -->
## FEU4 [x] — Poser le sommaire

**Session** : bc14fab5-1e0d-472c-908e-b6dfeefa2dfd
**Dépend de** : `FEU3`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `templates/artefact-feuille-de-route.html`, `templates/vlp.css` — et rien d'autre.

**Prompt**
Sous l'en-tête de la feuille, un sommaire de trois liens : « Chantier en cours », « Chantiers
possibles », « Chantiers clos », vers `#encours`, `#todo`, `#clos` — ces `id` posés sur leurs
trois sections. Pas de script. Dans le gabarit ; et `feuille` pose sommaire et `id` sur une
feuille qui ne les a pas, **une seule fois**. Une règle courte dans `vlp.css`, dans la famille
de `h2` et de `.eyebrow`.

**Critère de fin**
Nouveau test dans `test-vlp.py` : une feuille sans sommaire, bâtie dans un dossier temporaire →
après `feuille`, un seul sommaire, trois liens, chaque cible `id` présente une fois dans la page ;
2e appel `inchangée`. Mutant : la garde « déjà posé » retirée → deux sommaires, le test tombe.
Tous verts ; `pyright` 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:FEU5 -->
## FEU5 [x] — Faire lire les cartes aux outils de l'audit

**Session** : bc14fab5-1e0d-472c-908e-b6dfeefa2dfd
**Dépend de** : `FEU3`.
**Fichiers** : `context AI/38-audit-scripts/page_vs_source.py`, `context AI/38-audit-scripts/rejeu.py`, `scripts/vlp.py` (`zone_todo`, lu seulement), `context AI/87-cartes.md` (`## Mesures`, la ligne de départ de `FEU1`) — et rien d'autre.

**Prompt**
Les deux lisent la TODO par `ZONE:todo.*?<tbody>(.*?)</tbody>` : sur une feuille en cartes, ce
motif attrape la table des clos, sans erreur. Qu'ils prennent les bornes de `zone_todo` — `vlp.py`
chargé par son chemin, depuis le dossier du script, comme `test-vlp.py:28` —, pas un motif
recopié. Un rang = une ligne de tableau ou une carte ; ses cellules = rang, chantier, apporte,
coût, dépendance, lues dans les deux formes. Dans `rejeu.py`, les compteurs `todo_*` comptent
les cartes ; leurs noms ne changent pas.

Compte les erreurs `pyright` des deux fichiers **avant** d'y toucher.

**Critère de fin**
`page_vs_source.py ../Cairn-VlpLib "context AI"` sur la feuille en tableau d'aujourd'hui rend la
même ligne `feuille · TODO` que `FEU1` ; sur une copie en cartes (scratchpad, `vlp.py feuille`
sur une copie du projet), mêmes rangs, tous entiers. `rejeu.py` tourne sur les deux formes, sans
trace d'erreur. Mutant : la borne de `zone_todo` contournée → sur la copie en cartes, les rangs
changent. `pyright` : pas une erreur de plus, compte avant / après donné.
<!-- /FICHE -->

---

<!-- FICHE:FEU7 -->
## FEU7 [x] — Un lien vers la feuille de route sur la page du chantier

**Session** : 206644ce-75ee-40a0-a175-e09afdfe7b7c
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`regenerer` `:2338`, son motif de l'eyebrow `:2444`, `trouver` `:526`, `champ` `:2752`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Demandé par l'utilisateur en commentaire sur la page de ce chantier, le 2026-09-27, posé sur
l'eyebrow : « ajoute ici un lien vers la feuille de route ». `regenerer` lit la ligne
`**artefact feuille de route**` du `CHANTIER.md` du projet (`trouver`, en remontant depuis le
fichier de fiches) et finit l'eyebrow par ` · <a href="<url>">la feuille de route</a>` — le motif
de `:2444` tolère déjà un ` · ` après la plage. Libellé calqué sur « la page du chantier » de
l'encours (`feuille`, `:2885`). Un seul lien : régénérer n'en ajoute pas un second, une URL
changée remplace l'ancienne ; ligne absente ou « aucun » : pas de lien, et celui d'avant se retire.

**Critère de fin**
Nouveau test dans `test-vlp.py`, projet temporaire : `CHANTIER.md` avec une URL → après deux
`vlp.py page`, l'eyebrow porte exactement un `<a href="<url>">la feuille de route</a>`, plage
intacte ; URL changée → la nouvelle seule ; « aucun » → aucun lien. Mutant : la garde d'unicité
retirée → deux liens après deux passages, le test tombe. Tous les tests verts ; `pyright` 0 erreur.
`grep -c "la feuille de route</a>" "context AI/artefacts/87-cartes.html"` rend 1 après `vlp.py page`.
<!-- /FICHE -->

---

<!-- FICHE:FEU8 -->
## FEU8 [x] — Le détail des chantiers possibles

**Session** : 206644ce-75ee-40a0-a175-e09afdfe7b7c
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`resume_todo` et `compte_todo` `:2920-2935`, leur appel dans `feuille` `:2905`, `lettres_prises` `:2768`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Demandé par l'utilisateur en commentaire sur la feuille du kit, sur « 7 chantiers possibles » ;
seuils et parts tranchés avec lui le 2026-09-27. La ligne du décompte devient, parts à zéro omises,
singulier sous 2 : `7 chantiers possibles · 2 petits, 1 moyen, 2 gros, 2 pas estimés · 1 bloqué · ≈17 fiches estimées`.
- **Taille** : les nombres de « Coût estimé » avant le premier mot « fiche », borne haute
  (`~4 à 6` → 6, `2-3` → 3, `~0,5` → 0,5). Petit ≤ 1, moyen ≤ 4, gros au-delà ; aucun nombre
  avant « fiche » (`à cadrer`, `🟡 pas estimé`, `—`) : pas estimé.
- **Bloqué** : « Dépend de » nomme un code entre backticks absent des lettres prises de
  `CHANTIER.md` — **sans** celle du chantier en cours, que `feuille` ajoute (`:2889`) —, ou un
  numéro égal au rang d'une ligne encore dans la TODO (`3`, `1..9`).
- **Total** : la somme des bornes hautes, virgule française.
Essayé le 2026-09-27 sur les 52 rangs des cinq projets : kit et Cairn notent leurs dépendances en
codes, les trois autres en numéros de rang.

**Critère de fin**
Nouveau test dans `test-vlp.py`, fichier d'état en mémoire : coûts `~0,5 fiche`, `~4 à 6 fiches`,
`2-3 fiches`, `à cadrer` ; dépendances `` `AAA` `` (prise), `` `ZZZ` ``, le numéro d'un rang
présent, `—` → `4 chantiers possibles · 1 petit, 1 moyen, 1 gros, 1 pas estimé · 2 bloqués · ≈9,5 fiches estimées`.
Mutant : borne basse au lieu de haute → `~4 à 6` passe moyen, le test tombe. Tous les tests verts ;
`pyright` 0 erreur. `vlp.py feuille` sur une copie du kit (scratchpad) rend la ligne ci-dessus à 7 rangs.
<!-- /FICHE -->

---

<!-- FICHE:FEU6 -->
## FEU6 [x] — Régénérer, mesurer après, republier

**Session** : 206644ce-75ee-40a0-a175-e09afdfe7b7c
**Dépend de** : `FEU1`, `FEU4`, `FEU5`, `FEU8`.
**Fichiers** : `context AI/87-cartes.md` (`## Mesures`), `context AI/artefacts/feuille-de-route.html`, `../Cairn-VlpLib/context AI/artefacts/feuille-de-route.html`, `CHANTIER.md` et `../Cairn-VlpLib/CHANTIER.md` (URL), `context AI/38-audit-scripts/page_vs_source.py`, `context AI/38-audit-scripts/rejeu.py` — et rien d'autre.

**Prompt**
Pour la feuille du kit, puis celle de Cairn : `git check-ignore` ; `Artifact read` de la version en
ligne ; `vlp.py feuille <projet>` ; `vlp.py comparer <en ligne> <locale>` — chaque `PERDU:` d'une
ancienne ligne de tableau se retrouve dans les `AJOUTÉ:` de sa carte (étiquette et détail) : donne
les comptes (perdus, ajoutés, justifiés). Puis `page_vs_source.py` sur Cairn (rangs = rangs de sa
TODO, tous entiers) et `rejeu.py`.

Refais les mesures de `FEU1`, même montage : écrans cartes fermées et tout déplié, défilement de
côté ; republie chaque feuille à son URL avec `files` (`vlp.css`), puis la lecture en tokens,
dans un tour à part. Ajoute les lignes « après » à `## Mesures`. Chez Cairn, si Git suit la
feuille : un commit dans son dépôt, jamais de push.

**Critère de fin** (visuel)
`## Mesures` porte avant et après, comptes bruts et commandes ; Cairn cartes fermées ≤ 5 écrans ;
la TODO ne défile plus de côté ; `page_vs_source.py` : rangs = entiers = rangs de la TODO de Cairn.
L'utilisateur voit en ligne les deux feuilles : cartes fermées, sommaire en haut.
<!-- /FICHE -->

## Mesures

Mesuré par `FEU1` le 2026-09-27, session `bc14fab5-1e0d-472c-908e-b6dfeefa2dfd`, sur les
versions **en ligne** : kit `1790510770-a339` (TODO en tableau, **7 rangs**), Cairn
`1790510183-4a9a` (TODO en tableau, **16 rangs**). Fichiers sauvés, base de `comparer` en `FEU6` :
`tool-results/artifact-ff1fc060-1790510770-a339.html` et `tool-results/artifact-71823ec4-1790510183-4a9a.html`.

| Mesure | Feuille | Quand | Commande | Comptes bruts | Résultat |
|---|---|---|---|---|---|
| Coût d'un `Artifact read` | kit | avant | `date` (12:07:03Z), `Artifact read` dans un tour à part, `date` (12:07:11Z), `py scripts/mesure-tokens.py --plage 2026-09-27T12:07:03Z 2026-09-27T12:07:11Z bc14fab5-1e0d-472c-908e-b6dfeefa2dfd` | `ctx_1er` = 155 048, `ctx_dernier` = 178 322, 2 tours (Artifact=1, Bash=1) | **23 274 tokens** |
| Coût d'un `Artifact read` | Cairn | avant | `date` (12:07:14Z), `Artifact read`, `date` (12:07:22Z), `py scripts/mesure-tokens.py --plage 2026-09-27T12:07:14Z 2026-09-27T12:07:22Z bc14fab5-…` | `ctx_1er` = 178 694, `ctx_dernier` = 201 072, 2 tours (Artifact=1, Bash=1) | **22 378 tokens** |
| Hauteur, écrans d'ordinateur | kit | avant, replié (défaut) | fichier sauvé copié en `scratchpad/feu1/kit/index.html` (l'enveloppe de la plateforme y est déjà), `vlp.css` du kit à côté, `py -m http.server 8765`, navigateur intégré à 1536 × 864, `await document.fonts.ready; document.documentElement.scrollHeight / 864` | `scrollHeight` = 2931 px, `innerHeight` = 864, `innerWidth` = 1536, 1 `details` fermé, `vlp.css` chargé, fond `rgb(246, 239, 223)` ; tableau TODO haut de 2125 px | **3,39 écrans** |
| Hauteur, écrans d'ordinateur | kit | avant, tout déplié | même page, `details.open = true` | `scrollHeight` = 14 775 px (75 rangs clos) | **17,10 écrans** |
| Hauteur, écrans d'ordinateur | Cairn | avant, replié (défaut) | même montage, `scratchpad/feu1/cairn/index.html`, `vlp.css` de Cairn (identique au kit, `cmp`) | `scrollHeight` = 11 913 px, 1 `details` fermé, `vlp.css` chargé ; tableau TODO haut de 10 519 px | **13,79 écrans** |
| Hauteur, écrans d'ordinateur | Cairn | avant, tout déplié | même page, `details.open = true` | `scrollHeight` = 15 977 px (29 rangs clos) | **18,49 écrans** |
| Défilement de côté, 1536 × 864 | kit | avant | même page : `scrollWidth > innerWidth`, puis chaque `.tableau` : `scrollWidth > clientWidth` (clos déplié) | page 1521 ≤ 1536 ; TODO 696 = 696 ; clos 696 = 696 | **aucun** |
| Défilement de côté, 1536 × 864 | Cairn | avant | idem | page 1521 ≤ 1536 ; TODO 696 = 696 ; clos 696 = 696 | **aucun** |
| Défilement de côté, 375 × 812 | kit | avant | idem, `resize_window` preset `mobile` | page 375 = 375 ; TODO 483 > 335 ; clos 545 > 335 | **TODO et clos** défilent |
| Défilement de côté, 375 × 812 | Cairn | avant | idem | page 375 = 375 ; TODO 627 > 335 ; clos 488 > 335 | **TODO et clos** défilent |
| Rien de perdu, départ | Cairn | avant | `py "context AI/38-audit-scripts/page_vs_source.py" ../Cairn-VlpLib "context AI"` | `feuille · TODO : rangs 16 · toutes cellules entières ailleurs 15` | 1 rang manquant : le rang 1 |
| Rien de perdu, départ | kit | avant | `py "context AI/38-audit-scripts/page_vs_source.py" . "context AI"` | `feuille · TODO : rangs 7 · toutes cellules entières ailleurs 6` | 1 rang manquant : le rang 29 |
| Coût d'un `Artifact read` | Cairn | après | `date` (15:31:50), `Artifact read` sur `https://claude.ai/artifact/F1xfVYG1FtfRGy2Qs1krX8` dans un tour à part, `date` (15:32:01), `py scripts/mesure-tokens.py --plage 2026-09-27T15:31:50 2026-09-27T15:32:01 206644ce-75ee-40a0-a175-e09afdfe7b7c` | `ctx_1er` = 126 048, `ctx_dernier` = 148 248, 2 tours (Artifact=1, Bash=1) | **22 200 tokens** |
| Hauteur, écrans d'ordinateur | kit | après, replié (défaut) | feuille republiée relue (`tool-results/artifact-ff1fc060-1790515321-d915.html`), copiée en `scratchpad/feu6/apres/kit/index.html`, `vlp.css` à côté, `py -m http.server 8791` (`.claude/launch.json` « feu6-apres »), même script que `FEU1` à 1536 × 864 | `scrollHeight` = 1425 px | **1,65 écrans** |
| Hauteur, écrans d'ordinateur | kit | après, tout déplié | même page, `details.open = true` | `scrollHeight` = 14 586 px | **16,88 écrans** |
| Hauteur, écrans d'ordinateur | Cairn | après, replié (défaut) | même montage, `scratchpad/feu6/apres/cairn/index.html` (`tool-results/artifact-71823ec4-1790515529-fdc8.html`) | `scrollHeight` = 2724 px | **3,15 écrans** |
| Hauteur, écrans d'ordinateur | Cairn | après, tout déplié | même page | `scrollHeight` = 12 703 px | **14,70 écrans** |
| Défilement de côté, 375 × 812 | kit | après | `resize_window` preset `mobile`, `body` et `#todo` : `scrollWidth` vs `clientWidth` | `body` 375 = 375 ; `#todo` 335 = 335 | **aucun** |
| Défilement de côté, 375 × 812 | Cairn | après | idem | `body` 375 = 375 ; `#todo` 335 = 335 | **aucun** |
| Rien de perdu, départ | Cairn | après | `py "context AI/38-audit-scripts/page_vs_source.py" ../Cairn-VlpLib "context AI"` | `feuille · TODO : rangs 16 · toutes cellules entières ailleurs 16` | **16 = 16**, aucun rang manquant |

- ⚠️ **Le défilement de côté ne se voit pas à 1536 × 864** : `.page` borne les tableaux à 696 px et
  ils s'y plient. Il se voit à 375 × 812, sur les deux tableaux. Le critère de `FEU6` (« la TODO ne
  défile plus de côté ») se remesure donc **à 375 × 812** ; la table des clos, hors chantier,
  continuera d'y défiler.
- ⚠️ **Le rang manquant de `page_vs_source.py` est celui qui porte le badge « en cours »**, sur les
  deux feuilles (cellule « Chantier », index 1) : « en cours » n'est dans aucune source. Tant qu'un
  chantier est ouvert, « rangs = entiers » (critère de `FEU6`) ne tient pas sans retirer le badge
  avant de comparer — à régler en `FEU5`, qui fait lire les cartes à cet outil.
  Commande : `scratchpad/pvs_rang.py`, tête de `page_vs_source.py` (l. 1-52) plus une boucle par rang.
- ⚠️ Chez Cairn, `ZONE:todo` porte un **préambule** (paragraphes et listes) **avant** le tableau :
  la conversion de `FEU3` ne remplace que le tableau, jamais ce préambule.
- La TODO fait **88 %** de la hauteur repliée de Cairn (10 519 / 11 913 px) et 73 % de celle du kit
  (2125 / 2931 px).
- L'écart en tokens contient aussi l'enveloppe de la plateforme (en-tête `[Artifact …]`, `<head>` de
  claude.ai) : même biais avant et après, comme en `PLI1`.
- **`FEU6` ne mesure qu'une seule lecture « après »** (Cairn), pas les deux comme `FEU1` : sa propre
  ligne de Prompt dit « la lecture en tokens », au singulier. Le premier essai (`13:28:13`–`13:30:53`)
  a été fait en heure **UTC** (`date -u`) : `mesure-tokens.py` lit une heure sans décalage comme
  l'**heure locale** (sa docstring) et a rendu 0 tour, 0 appel — écart de 2 h avec l'heure système.
  Refait en heure locale : `15:31:50`–`15:32:01`.
- Les 2 appels de la mesure « après » sont l'`Artifact read` visé **et** le `Bash` qui a pris
  l'horodatage de fin (`15:32:01`, borne haute incluse) : le coût du `Bash` seul est négligeable
  à côté de celui de la lecture, mais le compte brut le montre, sans le cacher.
- Toutes les valeurs « après » viennent des feuilles **republiées et relues en ligne** : kit
  `https://claude.ai/artifact/YWDny8kjubq9DhdP5rbPxA` (version 164), Cairn
  `https://claude.ai/artifact/F1xfVYG1FtfRGy2Qs1krX8` (version 76) — mêmes URL qu'avant, contenu
  regénéré par `FEU2`–`FEU5`, `FEU7`, `FEU8`.
