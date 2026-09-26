> **QUAND LIRE** : on joue une fiche `VOI*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache VOI<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier VOI — Finir les feuilles voisines, reste de REP

**À quoi il sert.** `vlp.py niveau` montre 1 écart `feuille` sur MapDecorator, TrackGen et ProjetONZSM :
leur feuille régénérée perd du contenu, et la ligne `MARKDOWN` compte la mauvaise page. Le chantier
répare la régénération, puis republie les trois pages (TODO n° 25, journal du 2026-09-23).

**Estimé.** 3 fiches · ≈12 $ — ≈4,00 $/fiche sur 61 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 6 fiches, `VOI1` à jouer.

**Session** : 382d47f9-b6fa-494b-8bb1-40222f22a6d9

**Session** : e216f2f1-2f4f-49a6-a0ab-65533791a028

## Le socle commun

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `cmd_niveau` | `scripts/vlp.py:2870` | écarts d'un projet équipé ; la ligne `md = markdown_brut(converti if a.ecrire else neuf)` (`:2907`) compte la page **régénérée** sans `--ecrire` |
| `markdown_brut` | `scripts/vlp.py:2786` | `(** bruts, liens Markdown, liens cassés)` d'un HTML |
| `feuille` | `scripts/vlp.py:2426` | régénère encours, TODO et lettres depuis `CHANTIER.md` et le fichier d'état |
| `lettres_prises` | `scripts/vlp.py:2331` | lettres de la ligne « Lettres de fiche déjà prises » ; regex `\s*([A-Z]{1,3})(?: \(\|\.?\s*$)` : une lettre entre backticks tombe |
| `todo_du_fichier` | `scripts/vlp.py:2395` | lit la seule table `\| # \| Chantier` du fichier d'état |
| tests `niveau` | `scripts/test-vlp.py`, sections `NIV2`, `NIV3`, `REP3` (`:1854`, `:1953`, `:2148`) | modèles à suivre : projet bâti dans un `tempfile` |

**Les trois voisins** — dossiers frères du kit (`../<Projet>`), hors du dépôt du kit :

| Projet | Page locale | Ce qui casse (journal du 2026-09-23) | URL en ligne (`CHANTIER.md`) |
|---|---|---|---|
| MapDecorator | `context AI/artefacts/feuille-de-route.html` | TODO en section `## TODO` (`08-etat.md:120`), pas en table → lue vide ; lettres `` `T`, `U`, `R`, `M` `` (`CHANTIER.md:40`) | `…/201dbba3-4082-4d15-83d9-96d3ffafd44b` |
| TrackGen | idem | titres sans accents (`## La TODO ordonnee`) — cause exacte à mesurer | `…/04f79dca-d66d-40dc-83f3-35fad5cc102b` |
| ProjetONZSM | idem | rien de nommé : à mesurer | `…/0ec5a72c-7c34-4bb6-82c4-a15bb632edd2` |

Chaque page a sa copie `feuille-de-route.html.avant-REP` à côté. Les pages en ligne, faites à la
main, sont la référence : la régénération ne doit rien leur retirer.

**Décidé au cadrage** (2026-09-26, avec l'utilisateur) :

- Fin du chantier : régénération sans perte, `niveau` à 0 écart `feuille`, trois pages republiées.
- Les accents de TrackGen et la TODO de MapDecorator : **mesurer d'abord** (`VOI4`), puis
  l'utilisateur tranche entre corriger le projet ou le script.
- Avant republication : `vlp.py comparer` d'abord, puis l'utilisateur regarde la page.
- Rien n'est écrit dans un projet voisin avant la décision de `VOI4`.

**Hors chantier** : le gabarit de la feuille (`FEU`), la page de Cairn (déjà republiée par `REP`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `VOI1` | Compter la page du disque sans `--ecrire` | rien |
| `VOI2` | Comparer deux feuilles par script | rien |
| `VOI3` | Lire les lettres de fiche entre backticks | rien |
| `VOI4` | Mesurer ce que chaque voisin perd, et faire trancher | `VOI2` |
| `VOI5` | Passer la TODO de MapDecorator en table | `VOI4` |
| `VOI6` | Régénérer, faire regarder, republier les trois pages | `VOI1`, `VOI3`, `VOI5` |

`VOI1`, `VOI2` et `VOI3` sont indépendantes. `VOI5` réécrite après `VOI4` (2026-09-26).

---

<!-- FICHE:VOI1 -->
## VOI1 [x] — Compter la page du disque sans `--ecrire`

**Tentatives** (2026-09-26) — résolu par : compter html si la page existe, neuf si absente ; NIV3 attend 5 écarts (choix utilisateur)

**Session** : 8cef44d4-8634-4856-a1fc-f0559f6a0b36
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_niveau`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Sans `--ecrire`, la ligne `MARKDOWN` de `cmd_niveau` doit compter la page **du disque** (`html`),
celle que l'utilisateur voit, et non la page régénérée (`neuf`). Avec `--ecrire`, rien ne change :
elle compte `converti`, la page qui sera écrite. Un disque sans page (feuille absente) reste
« non mesuré » ou compte le gabarit, comme aujourd'hui.

Ajoute un test dans la section `REP3` de `scripts/test-vlp.py` : un projet bâti dans un
`tempfile` dont la page du disque porte un `**x**` brut que la régénération ferait tomber.
Sans `--ecrire`, `MARKDOWN` doit en compter 1. Attention aux `with tempfile` voisins : ne
réemploie pas leur variable.

**Critère de fin**
`py scripts/test-vlp.py` passe (compte brut de tests avant/après) ; le mutant « remettre `neuf`
dans la branche sans `--ecrire` » fait tomber le nouveau test. `pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:VOI2 -->
## VOI2 [x] — Comparer deux feuilles par script

**Session** : 75214987-1d49-4d93-8532-3920557c9c7b
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (nouvelle sous-commande `comparer`, docstring du module), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute `vlp.py comparer <ancienne.html> <neuve.html>`. Il extrait le **texte visible** de chaque
page (balises, `<script>` et `<style>` retirés, entités décodées, blancs réduits), par
ligne de tableau ou par bloc, et écrit :
- une ligne `PERDU: <texte>` par texte présent dans l'ancienne et absent de la neuve ;
- une ligne `AJOUTÉ: <texte>` pour l'inverse ;
- en dernier, `COMPARER <p> perdus · <a> ajoutés`.
Code de sortie 0, même avec des pertes : c'est une mesure, pas une garde. Un fichier absent :
`GARDE:` et code 1. Python standard seul (`html.parser`). Documente la sous-commande dans la
docstring du module.

**Critère de fin**
Test dans `scripts/test-vlp.py` : deux pages bâties dans un `tempfile`, l'une perd une ligne de
TODO et prend une date. Attendu : `COMPARER 1 perdus · 1 ajoutés`, et la ligne `PERDU:` porte le
texte de la TODO. Mutant « ne jamais écrire `PERDU` » : le test tombe. `pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:VOI3 -->
## VOI3 [x] — Lire les lettres de fiche entre backticks

**Session** : 75214987-1d49-4d93-8532-3920557c9c7b
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`lettres_prises`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
`lettres_prises` doit accepter une lettre écrite entre backticks, comme chez MapDecorator :
`` Lettres de fiche déjà prises : `T`, `U`, `R`, `M`. `` → `["T", "U", "R", "M"]`. Les formes
déjà lues restent lues : `X (titre)`, `X` seule, un titre à virgule qui n'en ajoute pas (tests
`TAR`). « aucune » ne rend toujours rien. Essaie la regex sur les vraies lignes des quatre
`CHANTIER.md` (le kit, `../MapDecorator`, `../TrackGen`, `../ProjetONZSM`) avant d'écrire le test,
et donne les listes obtenues.

**Critère de fin**
Test nouveau : la ligne de MapDecorator ci-dessus rend 4 lettres. Les tests `TAR` passent
toujours (compte brut avant/après). Mutant « retirer la tolérance des backticks » : le nouveau
test tombe. `pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:VOI4 -->
## VOI4 [x] — Mesurer ce que chaque voisin perd, et faire trancher

**Session** : 75214987-1d49-4d93-8532-3920557c9c7b
**Dépend de** : `VOI2`.
**Fichiers** : les trois `context AI/artefacts/feuille-de-route.html` des voisins (lus, jamais écrits), `../TrackGen/context AI/08-etat.md` et `../MapDecorator/context AI/08-etat.md` (lus), `context AI/08-etat.md` du kit (journal) — et rien d'autre.

**Prompt**
Pour chaque voisin, régénère la feuille **dans le scratchpad** (jamais sur la page du projet) et
lance `vlp.py comparer <page du disque> <page régénérée>`. Pour chaque `PERDU:`, trouve la cause :
la fonction de `vlp.py` qui ne lit pas, et la ligne du projet qu'elle rate. Pour TrackGen, dis
précisément quel titre ou libellé sans accents fait tomber quoi.

Écris une entrée datée au journal de `context AI/08-etat.md` : par projet, les comptes
`COMPARER` bruts et la cause de chaque perte. Puis présente à l'utilisateur, pour MapDecorator
(TODO hors table) et pour TrackGen (accents), les deux corrections possibles — dans le projet, ou
dans `vlp.py` — avec ce que chacune change, et arrête-toi.

**Critère de fin** (visuel)
Le journal porte les trois comptes `COMPARER` et une cause par perte ; l'utilisateur a tranché,
projet ou script, pour MapDecorator et pour TrackGen, et sa réponse est notée au journal.
<!-- /FICHE -->

---

<!-- FICHE:VOI5 -->
## VOI5 [x] — Passer la TODO de MapDecorator en table

**Session** : 83db81cd-9578-4477-8067-1e1ad7cef7a5
**Dépend de** : `VOI4` (tranché : correction dans le projet ; `vlp.py` ne change pas ; TrackGen et ProjetONZSM, aucune action).
**Fichiers** : `../MapDecorator/context AI/08-etat.md` (section `## TODO`, `:120`) — seul fichier voisin écrit ; `context AI/08-etat.md` du kit (journal) — et rien d'autre.

**Prompt**
La TODO de MapDecorator est une liste `N. [ ]`/`[x]` ; `todo_du_fichier` ne lit que la table
`| # | Chantier`, d'où `FEUILLE todo 0`. Réécris la section en table au format de TrackGen
(`../TrackGen/context AI/08-etat.md:36`) : `| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |`.

- Une ligne par item **ouvert** : #3, 4, 5, 6, 7, 8, 9, 10, 12 — numéros gardés, jamais renumérotés.
- `Chantier` : le titre en gras de l'item ; `Ce qu'il apporte` : le reste de son texte sur une ligne, renvoi `→ fichier` compris, sans rien couper.
- `Coût estimé` et `Dépend de` : `—` (rien n'est inventé). Un `|` dans le texte s'échappe `\|`.
- Les items faits #1, #2, #11 : liste sous la table, sous un titre `Fait`, texte intact.

Rien d'autre ne bouge dans ce fichier. MapDecorator a des modifications en cours sur d'autres
fichiers : commite **ce seul fichier** dans son dépôt (`git add "context AI/08-etat.md"`), jamais `-a`.
Écris au journal du kit les comptes avant et après.

**Vérification**
- `py scripts/vlp.py feuille ../MapDecorator --verifier` avant (mesuré au cadrage : `FEUILLE todo 0`) et après.
- `py -c` qui importe `scripts/vlp.py` et imprime les numéros de `todo_du_fichier` sur le fichier réécrit.
- `feuille --verifier` sur `../TrackGen` et `../ProjetONZSM` : témoins, rien n'y est écrit.

**Critère de fin**
`FEUILLE todo 8` sur MapDecorator ; numéros lus `3 4 5 6 7 8 9 10 12`, 8 exactement ; les titres
de #1, #2, #11 présents sous `Fait` (`grep -c` = 1 chacun) ; témoins inchangés, `todo 11` et
`todo 8`. `COMPARER 1 perdus · 1 ajoutés` est accepté : la page est un seul bloc de texte
(journal `VOI4`), `comparer` ne peut pas descendre à la ligne.
<!-- /FICHE -->

---

<!-- FICHE:VOI6 -->
## VOI6 [ ] — Régénérer, faire regarder, republier les trois pages

**Dépend de** : `VOI1`, `VOI3`, `VOI5`.
**Fichiers** : les trois `CHANTIER.md` et `context AI/artefacts/feuille-de-route.html` des voisins, `context AI/08-etat.md` du kit — et rien d'autre.

**Prompt**
Pour chaque voisin : copie la page du disque dans le scratchpad, `vlp.py feuille ../<Projet>`,
puis `vlp.py comparer` entre cette copie et la page écrite, puis `vlp.py niveau ../<Projet>`. Donne les trois sorties brutes.
Montre ensuite chaque page à l'utilisateur, une à la fois, et attends son accord.

Sur accord seulement : `Artifact` `action: "read"` sur l'URL de `CHANTIER.md`, puis republie le
fichier local avec cette `url`, `label` `VOI6 republiée`. Une page refusée n'est pas publiée : dis
pourquoi au journal. Termine par une entrée au journal : les comptes avant (`NIVEAU 1 écarts`) et
après, par projet.

**Critère de fin** (visuel)
Pour les trois voisins : `FEUILLE todo` à 8, 11 et 8 (MapDecorator, TrackGen, ProjetONZSM),
`NIVEAU 0 écarts`, l'utilisateur a vu la page et dit oui, et la republication a répondu sans
erreur. `COMPARER 1 perdus · 1 ajoutés` est accepté : la page est un seul bloc (journal `VOI4`).
<!-- /FICHE -->
