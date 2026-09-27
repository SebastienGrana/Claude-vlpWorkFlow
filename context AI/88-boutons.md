> **QUAND LIRE** : on joue une fiche `BTN*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache BTN<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier BTN — Des boutons sur les pages

**À quoi il sert.** Les pages du kit sont des affiches : on lit, on ne touche à rien. BTN y pose
quatre choses : tout déplier, copier la commande d'une fiche, filtrer la feuille par état, un
graphique du coût des chantiers clos — sans alourdir la page relue à chaque fiche.

**Estimé.** 6 fiches · ≈25 $ — ≈4,22 $/fiche sur 75 clos (le 2026-09-27).

**CLOS** le 2026-09-28. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** BTN1..BTN7 (2026-09-28) : vlp.js joint aux pages (tout déplier, copier la commande d'une fiche, quatre filtres d'état), graphique couts.svg des chantiers clos, décompte en valeur et texte d'avant la liste replié, ligne FILES dans les commandes — estimé 6 fiches ≈25 $ · cadré 7 · joué 7 fiches ≈79 $.

**Session** : 6ac208bd-c52d-458e-830f-a96141a6b0f7

## Le socle commun

**Décidé au cadrage (deux pages à cartes, 2026-09-27).**
- Dedans : **tout déplier** (les deux pages), **copier la commande** `/vlp:tache <ID>` (page du
  chantier), **filtrer par état** (feuille : à faire, en cours, clos), **graphique** (feuille).
- Ajouté le 2026-09-27 (A1, sur un commentaire) : le **décompte** des chantiers possibles mis en
  valeur, et le texte d'avant la liste **replié** (`BTN7`).
- Le code des boutons dans un fichier joint **`vlp.js`**, comme `vlp.css` (D1). Le graphique dans
  un fichier joint **`couts.svg`**, écrit par `vlp.py` (D2, D3), **en tokens**, pas en dollars (D4).
- `<meta charset="utf-8">` en **première ligne** des deux gabarits (D5).
- `vlp.py` dit quoi joindre : une ligne **`FILES`** (D6), qui remplace les 7 « `files: vlp.css` »
  recopiés dans les commandes.
- Republiées en fin de chantier : la feuille **du kit**, celle de **Cairn**, la page de BTN (Q6).

**Établi par l'essai du 2026-09-27** (page jetable publiée, puis supprimée).
- Sur claude.ai, un `<script src="vlp.js">` joint **tourne**, un `<img src="….svg">` joint
  **s'affiche** (capture de l'utilisateur).
- `Artifact read` ne rend que les balises, **jamais les fichiers joints**.
- En local, `file://` rend une image figée : aucun joint ne charge. Il faut un serveur :
  `py -m http.server <port> --directory <dossier>`, déclaré dans `.claude/launch.json`, ouvert par
  `preview_start`. Sans `charset`, le navigateur lit la page en `windows-1252` (mesuré).
- ⚠️ Le sous-agent `vlp:fiche` **n'a pas de navigateur** : les fiches dont le critère se voit
  dans le navigateur sont **(visuel)**. On les joue par `/vlp:tache`, dans la session principale.

**Invariants.**
- **Aucun code de bouton dans le HTML** : `vlp.js` fabrique ses boutons au chargement, à partir des
  crochets déjà posés (table ci-dessous). La page ne gagne que ses balises `<meta>`, `<script>`,
  `<img>`, relues à chaque fiche (`ARTEFACTS.md`, « Le budget de contexte »).
- Les styles dans `vlp.css` seul (`ALE`) : `vlp.js` pose des classes, jamais d'attribut `style`.
- Copier : `navigator.clipboard.writeText` dans le gestionnaire du clic ; en cas de rejet,
  sélectionner le texte et dire « Sélectionné : fais Ctrl+C » (comme `templates/rapport-choix.html`).
- Masquer : `el.hidden`, jamais `style.display`. Clavier : un vrai `<button type="button">`.
- À 375 × 812, aucun défilement latéral (`scrollWidth` ≤ `clientWidth`), comme depuis FEU.
- Une source par joint : `templates/vlp.css`, `templates/vlp.js` ; `vlp.py` les recopie dans
  `<contexte>/artefacts/` à chaque `page` et `feuille`.
- Cairn est privé : ici, des comptes et des numéros, jamais un extrait de ses pages.

| Crochet lu par `vlp.js` | Où il naît |
|---|---|
| `li.fiche[data-etat]`, `span.id` | page du chantier, `templates/artefact-chantier.html:45-60` |
| `nav.sommaire`, `#encours`, `#todo`, `#clos` | feuille, `templates/artefact-feuille-de-route.html:21-43` |
| `li.carte-todo`, `.badge[data-etat="cours"]` | `feuille`, `scripts/vlp.py:2992` ; `BADGE_COURS` `:2755` |
| `details.clos`, lignes `.badge[data-etat="clos"]` | gabarit `:48` ; `cmd_clore`, `scripts/vlp.py:4075` |

| Symbole (2026-09-27, à regrepper) | Où | Rôle |
|---|---|---|
| `recopier_vlp_css`, `GABARIT_VLPCSS` | `scripts/vlp.py:1890`, `:1887` | copie `vlp.css` ; appelée `:2660`, `:3117`, `:3300` |
| `migrer_style`, `STYLE_INLINE` | `scripts/vlp.py:2301-2311` | pose le `<link>` sur une page d'avant |
| `cmd_page` · `feuille` · `cmd_feuille` | `scripts/vlp.py:2609` · `:2959` · `:3098` | régénèrent les deux pages |
| `page_feuille(` | `:3234`, `:3371`, `:3779`, `:4060`, `:4262` | chaque lecteur ou écrivain de la feuille |
| `lignes_clos`, `BRUT`, `total_clos` | `scripts/vlp.py:3131-3146` | les lignes de `ZONE:clos`, leur coût brut |
| `arrondi` | `scripts/vlp.py:1949` | la convention de coût (`≈2,3k (2 312)`) |
| tests PLI2, PLI3 | `scripts/test-vlp.py:3545-3635` | `vlp.css` recopié, ligne `CSS` ; migration |

**Tests.** Dans `scripts/test-vlp.py`, chaque test bâtit son projet dans un dossier temporaire
(`vlp.py` chargé par son chemin, `test-vlp.py:28`) ; chaque critère de code nomme son mutant.
`pyright` : zéro erreur sur les `.py` touchés — un fichier qui en porte déjà : jamais une de plus.

**Hors chantier.** Commenter une fiche (attend `BDD`, n° 73) ; la base `db` ; les feuilles de
MapDecorator, ProjetONZSM, TrackGen (elles reçoivent les boutons à leur prochain `vlp.py feuille`) ;
la typographie de `vlp.css`, sauf le décompte (`BTN7`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `BTN1` | Joindre `vlp.js` aux pages, et dire quoi joindre | rien |
| `BTN2` | Publier avec la ligne `FILES` dans les commandes | `BTN1` |
| `BTN3` | Tout déplier, et copier la commande d'une fiche | `BTN1` |
| `BTN4` | Filtrer la feuille par état | `BTN1` |
| `BTN5` | Dessiner le coût des chantiers clos | `BTN1` |
| `BTN7` | Le décompte en valeur, le texte d'avant la liste replié | rien |
| `BTN6` | Régénérer, republier, et regarder | toutes |

Après `BTN1`, les fiches 2 à 5 sont indépendantes ; `BTN3` et `BTN4` touchent le même
`templates/vlp.js`, donc jamais en même temps. `BTN3`, `BTN4`, `BTN6` sont **(visuel)**. `BTN7`,
ajoutée le 2026-09-27 sur un commentaire de l'utilisateur, passe avant `BTN6` : elle republie les
feuilles une seule fois, décompte et repli compris.

---

<!-- FICHE:BTN1 -->
## BTN1 [x] — Joindre `vlp.js` aux pages, et dire quoi joindre

**Session** : 9f0ccb7c-90c6-450f-b0a0-274fe4ed398d
**Dépend de** : rien.
**Fichiers** : `templates/vlp.js` (nouveau), `templates/artefact-chantier.html`,
`templates/artefact-feuille-de-route.html`, `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Crée `templates/vlp.js` : un commentaire d'en-tête seul (ce qu'il fait, que `BTN3` et `BTN4` le
remplissent). Généralise `recopier_vlp_css` en `recopier_joints(dossier)` : il recopie
`templates/vlp.css` et `templates/vlp.js`, et rend `{nom publié: chemin}` ; ses trois appels
suivent. Expose-le aussi en sous-commande `vlp.py joints <dossier>`, pour `/vlp:init` qui remplit
sa feuille sans `feuille`.

`page` et `feuille` écrivent, en plus de leur ligne `CSS` (les tests PLI2 la verrouillent), une
ligne `FILES {…}` : le JSON de `recopier_joints`, chemins en barres obliques, prêt à passer tel quel
au paramètre `files` d'`Artifact`. `joints` n'écrit que cette ligne.

Dans les deux gabarits : `<meta charset="utf-8">` en **première ligne**, avant le `<title>` ;
`<script src="vlp.js"></script>` en **dernière ligne**. Une page régénérée qui n'a pas l'une ou
l'autre la reçoit une fois, comme `migrer_style` pose le `<link>`. Vérifie d'abord qu'aucun code
(`vigile`, `page_vs_source`, la recherche du `<title>`) ne suppose le `<title>` en première ligne.
Docstring : `joints`, et la ligne `FILES` de `page` et `feuille`.

**Critère de fin**
Nouveaux tests `BTN1 : …` dans `scripts/test-vlp.py` : (a) `page --creer`, `page` et `feuille`
recopient `vlp.js` à l'octet et écrivent `FILES` avec les clés `vlp.css` et `vlp.js`, chacune vers
un fichier qui existe ; (b) la page rendue porte `<meta charset="utf-8">` et `<script
src="vlp.js"></script>` **une fois** chacun ; (c) une page d'avant, sans eux, les reçoit une fois,
et une seconde régénération n'en ajoute pas. `py scripts/test-vlp.py` passe, compte brut affiché.
Mutants : `vlp.js` retiré de `recopier_joints` → (a) tombe ; la balise posée sans vérifier sa
présence → (c) tombe. `pyright` : 0 erreur sur les fichiers touchés, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:BTN2 -->
## BTN2 [x] — Publier avec la ligne `FILES` dans les commandes

**Session** : df441fa6-79e6-47a6-aa5f-8da3676d8563
**Dépend de** : `BTN1`.
**Fichiers** : `skills/chantier/SKILL.md`, `skills/enchainer/SKILL.md`, `skills/init/SKILL.md`,
`skills/tache/SKILL.md`, `cloture.md`, `ARTEFACTS.md`, `scripts/test-vlp.py` (seulement si un test
verrouille l'un de ces textes) — et rien d'autre.

**Prompt**
Les commandes recopient « `files: vlp.css` » 7 fois : `skills/chantier/SKILL.md:236`, `:255`,
`skills/enchainer/SKILL.md:139`, `skills/init/SKILL.md:141`, `skills/tache/SKILL.md:138`,
`cloture.md:52`, `:59` (le 2026-09-27, à regrepper). Remplace chacune par un renvoi à la ligne
`FILES` que vient de rendre `page` ou `feuille` : « `files` : le JSON de la ligne `FILES` ». Pas
plus long que l'ancien texte : tout ajout se paye à chaque exécution.

`/vlp:init` remplit sa feuille à la main, sans `feuille` : il lance `vlp.py joints
"<contexte>/artefacts"` juste avant de publier, et passe sa ligne `FILES`.

`ARTEFACTS.md`, « Où vivent le CSS et les données » : la règle vit là, une fois — les joints
sont `vlp.css`, `vlp.js`, et `couts.svg` pour la feuille ; chaque publication, même une
republication, passe la ligne `FILES`. Le reste de la section ne bouge pas.

⚠️ Des commandes changent : à la fin, dis à l'utilisateur de faire `/reload-plugins` avant `BTN3`.

**Critère de fin**
`grep -rn 'files: vlp.css' skills/ cloture.md ARTEFACTS.md` → **0** ligne (compte brut) ;
`grep -o 'FILES' <chacun des 6 fichiers> | wc -l` → au moins 1 par fichier, comptes bruts affichés.
`py scripts/test-vlp.py` passe, compte brut affiché.
<!-- /FICHE -->

---

<!-- FICHE:BTN3 -->
## BTN3 [x] — Tout déplier, et copier la commande d'une fiche

**Session** : 0237698c-66e3-4b2e-a320-a0a42d6d2896
**Dépend de** : `BTN1`.
**Fichiers** : `templates/vlp.js`, `templates/vlp.css`, `.claude/launch.json` (serveur local, hors
Git) — et rien d'autre.

**Prompt**
Au chargement, `vlp.js` pose deux choses, seulement si leurs crochets existent (socle) :
- en tête de `.page`, un bouton **« Tout déplier »** si la page a au moins un `details` : il les
  ouvre tous et devient « Tout replier », qui les referme ;
- dans le `summary` de chaque `li.fiche` dont `data-etat` ne vaut pas `faite`, un bouton
  **« Copier »** qui copie `/vlp:tache <ID>` (`ID` = texte de `span.id`). Son clic ne replie pas la
  fiche (`preventDefault`). Il dit « Copié. », ou « Sélectionné : fais Ctrl+C » en cas de rejet.

Styles dans `templates/vlp.css`, par classes ; lisibles en clair et en sombre, focus visible.

Pour voir : `vlp.py page "context AI/88-boutons.md"` et `vlp.py feuille .` recopient les joints
dans `context AI/artefacts/` ; sers ce dossier par une entrée `.claude/launch.json`
(`py -m http.server`), ouvre-le par `preview_start`.

**Critère de fin** (visuel)
Dans le navigateur de l'app, par `javascript_tool`, comptes bruts affichés : `document.characterSet`
= `UTF-8` ; sur la page de BTN et sur la feuille, un clic sur « Tout déplier » → `details[open]` =
`details` ; un second → 0 ouvert. Page de BTN : autant de boutons « Copier » que de fiches non
faites (compte fait sur le fichier de fiches) ; un clic dit « Copié. » ou « Sélectionné… ». À
375 × 812, `scrollWidth` ≤ `clientWidth`. Mutant : la boucle d'ouverture retirée → le compte
d'ouverts ne bouge pas. L'entrée ajoutée à `launch.json` est retirée à la fin.
<!-- /FICHE -->

---

<!-- FICHE:BTN4 -->
## BTN4 [x] — Filtrer la feuille par état

**Session** : 9c178cca-e277-4ad4-b73b-e84a635aecb2
**Dépend de** : `BTN1`.
**Fichiers** : `templates/vlp.js`, `templates/vlp.css`, `.claude/launch.json` (serveur local, hors
Git) — et rien d'autre.

**Prompt**
Sur la feuille seulement (elle a `#todo` et `#clos`), `vlp.js` pose sous `nav.sommaire` quatre
boutons : **Tout**, **À faire**, **En cours**, **Clos**. Un seul est enfoncé (`aria-pressed`), « Tout »
au chargement.
- **À faire** : les `li.carte-todo` sans `.badge[data-etat="cours"]` ; `#encours` et `#clos` masqués.
- **En cours** : `#encours`, et la carte qui porte le badge « en cours » ; le reste masqué.
- **Clos** : `#clos` seul, et son `details.clos` ouvert.
- **Tout** : tout réapparaît, les replis reviennent à leur état d'avant le filtre.
Masquer par `el.hidden`. Styles dans `templates/vlp.css`. Montage pour voir : celui de `BTN3`.

**Critère de fin** (visuel)
Dans le navigateur de l'app, sur la feuille du kit régénérée (`BTN` y est en cours), par
`javascript_tool`, comptes bruts affichés : « À faire » → cartes visibles = cartes − 1, `#clos`
masqué ; « En cours » → 1 carte visible et `#encours` visible ; « Clos » → `#todo` masqué,
`details.clos` ouvert ; « Tout » → toutes les cartes visibles. À 375 × 812, `scrollWidth` ≤
`clientWidth`. Mutant : « À faire » qui ignore le badge → cartes visibles = cartes, il tombe.
L'entrée ajoutée à `launch.json` est retirée à la fin.
<!-- /FICHE -->

---

<!-- FICHE:BTN5 -->
## BTN5 [x] — Dessiner le coût des chantiers clos

**Session** : 9c178cca-e277-4ad4-b73b-e84a635aecb2
**Dépend de** : `BTN1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `templates/artefact-feuille-de-route.html`
— et rien d'autre.

**Prompt**
Une fonction pure `svg_couts(html)` rend le SVG du coût des chantiers clos, ou `None` s'il n'y a
aucun coût : une barre par ligne de `ZONE:clos` qui a un coût brut (`lignes_clos`, `BRUT`) ; du
plus ancien à gauche au plus récent à droite (la table met le plus récent en haut) ; hauteur
proportionnelle aux tokens, la plus haute pleine hauteur ; en haut à gauche, le maximum écrit par
`arrondi` suivi de « tokens ». Couleurs en dur, lisibles sur fond clair et sombre : une image ne
lit pas les variables de la page. Chaque forme a son `fill`.

Toute fonction qui écrit la feuille (`page_feuille(` dans le socle : `cmd_feuille`, `cmd_clore`,
`recompter --ecrire`…) écrit `couts.svg` à côté, et l'ajoute à sa ligne `FILES`. La feuille porte,
dans `#clos`, avant `details.clos`, une balise `<img src="couts.svg" alt="…">` ; son `alt` dit le
nombre de barres et le chantier le plus cher. Sans coût : ni fichier, ni balise. Une feuille
d'avant reçoit la balise à sa régénération, une fois. Le gabarit la montre à sa place.

**Critère de fin**
Nouveaux tests `BTN5 : …` dans `scripts/test-vlp.py`, sur une feuille temporaire à 4 lignes clos
— coûts 1 000, 2 000, 4 000, et une sans coût : `couts.svg` a **3** barres, hauteurs dans le
rapport 1 : 2 : 4 (à 1 px près), la plus récente à droite ; `FILES` nomme `couts.svg` ; la balise
`<img>` est là une fois ; une feuille sans coût n'a ni fichier ni balise. `py scripts/test-vlp.py`
passe, compte brut affiché. Mutants : hauteur constante → le rapport tombe ; ordre non retourné
→ l'ordre tombe. `pyright` : 0 erreur sur les fichiers touchés, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:BTN7 -->
## BTN7 [x] — Le décompte en valeur, le texte d'avant la liste replié

**Session** : 9c178cca-e277-4ad4-b73b-e84a635aecb2
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`compte_todo` `:3124`, `RESUME_TODO` `:3055`, `zone_todo` `:2930`,
`feuille` `:3001`), `templates/vlp.css` (`.journal-ancien > summary` `:64`), `scripts/test-vlp.py`
— et rien d'autre.

**Prompt**
Demandé par l'utilisateur le 2026-09-27 : en commentaire sur la feuille du kit, posé sur le
décompte, « met plus en valeur le chiffre des chantiers possibles » ; puis, sur la feuille de
Cairn, le texte entre le décompte et la liste va contre la page courte (choix A1).

Le décompte : `compte_todo` écrit `<p class="resume-todo"><strong><n> chantiers possibles</strong>
· <le reste></p>` — le `<strong>` prend ce qui précède le premier ` · ` de `resume_todo`, qui ne
change pas (ses tests FEU8 restent). Plus d'attribut `style` : ses trois valeurs d'aujourd'hui
passent dans une règle `.resume-todo` de `vlp.css`, et `.resume-todo strong` écrit le chiffre plus
grand, en `var(--texte)`. `RESUME_TODO` lit l'ancienne forme (`mono`, `style=`) et la nouvelle : une
feuille d'avant est réécrite une fois, jamais doublée.

Le texte d'avant la liste : ce qui, dans `ZONE:todo`, sépare la fin du marqueur du début de la
liste (`zone_todo`) et n'est pas du blanc passe dans un `<details class="lecture">` fermé, résumé
« Comment lire cette liste » — une fois : déjà dans un `details.lecture`, rien ne bouge. Le texte
n'est ni retouché ni retiré. Style du résumé : le sélecteur s'ajoute à la règle de
`.journal-ancien > summary`. Relevé le 2026-09-27 : Cairn 177 mots (3 paragraphes, 6 puces),
MapDecorator 35, ProjetONZSM 12, TrackGen 12, le kit 0 — chacun le reçoit à son prochain `feuille`.

**Critère de fin**
Nouveaux tests `BTN7 : …` dans `scripts/test-vlp.py` : (a) après `feuille`, le décompte est
`<p class="resume-todo"><strong>…</strong> · …</p>`, sans `style=` ; une feuille à l'ancien décompte
n'en a qu'un après deux `feuille` ; `vlp.css` porte `.resume-todo` ; (b) une feuille à préambule le
reçoit dans un seul `details.lecture` fermé, texte intact (`comparer` : 0 perdu), et le 2ᵉ `feuille`
dit « inchangée » ; sans préambule, aucun `details.lecture`. Le test FEU3 (« préambule gardé »,
`:2449`) passe sans retouche. `py scripts/test-vlp.py` passe, compte brut affiché. Mutants : le
`details` posé sans vérifier qu'il y est → (b) tombe ; `RESUME_TODO` sans l'ancienne forme → (a)
tombe. `pyright` : 0 erreur sur les fichiers touchés, compte brut.
<!-- /FICHE -->

---

<!-- FICHE:BTN6 -->
## BTN6 [x] — Régénérer, republier, et regarder

**Session** : 9c178cca-e277-4ad4-b73b-e84a635aecb2
**Dépend de** : `BTN1`, `BTN2`, `BTN3`, `BTN4`, `BTN5`, `BTN7`.
**Fichiers** : `context AI/artefacts/feuille-de-route.html`, `context AI/artefacts/88-boutons.html`,
`context AI/88-boutons.md`, et la feuille de Cairn :
`C:/Users/znorr/Documents/ProgPerso/Cairn-VlpLib/context AI/artefacts/feuille-de-route.html` —
et rien d'autre.

**Prompt**
Avant : les lignes des trois pages (`vlp.py lignes`), puis `Artifact read` de chacune en ligne. Pour
chaque feuille, `vlp.py comparer` de la version **en ligne** vers la locale, jamais contre le disque :
un écart qui n'est pas dû à BTN s'arrête et se dit. Cairn : `git check-ignore` sur sa feuille.

Puis régénère : `vlp.py page "context AI/88-boutons.md"`, `vlp.py feuille .`, `vlp.py feuille
<dossier de Cairn>`. Republie chacune à son URL (`CHANTIER.md` de chaque projet), avec `files` =
la ligne `FILES`, comme `FEU6` (`context AI/87-cartes.md`). Après : les lignes des trois pages, et
un `Artifact read` qui ne rend que les balises des joints. Écris avant, après et l'écart dans
`88-boutons.md`, section « Mesures ». Cairn : un commit dans son dépôt, sans push ; rien de Cairn
dans le kit, sauf des comptes.

**Critère de fin** (visuel)
Comptes bruts avant / après des trois pages dans le compte rendu. Puis l'utilisateur ouvre les
trois pages en ligne, sur ordinateur (1536 × 864) et sur téléphone : « Tout déplier », « Copier »
et les quatre filtres marchent ; le graphique s'affiche sur les deux feuilles ; le décompte
ressort, et le texte d'avant la liste de Cairn est replié ; rien ne défile de côté. Il le dit, et
la fiche se coche.
<!-- /FICHE -->

---

## Mesures

Mesuré le 2026-09-27 par `BTN6`, avant et après `vlp.py page "context AI/88-boutons.md"`,
`vlp.py feuille .`, `vlp.py feuille <dossier de Cairn>`. Cairn : des comptes seulement.

| Page | Lignes avant → après (`vlp.py lignes`) | `comparer` en ligne → locale, avant · après | Marques après |
|---|---|---|---|
| Feuille du kit | 556 → 557 (+1 : balise `couts.svg`) | 7 perdus · 13 ajoutés, les deux fois | `<img>` 1, 75 barres, décompte `<strong>` 1, `style=` 0, `details.lecture` 0 (pas de préambule) |
| Page de BTN | 104 → 104 | — | — |
| Feuille de Cairn | 283 → 286 (+3 : balise `couts.svg`, `details.lecture` ouvert et fermé) | 0 · 0, puis 0 perdus · 1 ajouté (« Comment lire cette liste ») | `<img>` 1, 25 barres, décompte `<strong>` 1, `style=` 0, `details.lecture` 1, fermé |

- Kit, 7 perdus : les mêmes textes recoupés (cartes en colonnes, « dépend de : X » devenu « ← X »,
  coût à part), et `Fiches BTN1–BTN6` → `BTN1–BTN7` — `PLAGE_TEXTE` ne lit que « fiches » en
  minuscule. Aucun écart étranger à BTN.
- Republication : refusée le 2026-09-27 à 20:16 (`publish 429: daily publish limit for your plan
  reached (200) — resets at UTC midnight`). Reportée après 02:00, heure locale ; l'`Artifact read`
  d'après, qui ne doit rendre que les balises des joints, vient avec elle.
