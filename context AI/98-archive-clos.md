> **QUAND LIRE** : on joue une fiche `ARC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ARC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ARC — Les chantiers clos vont à une page d'archive

**À quoi il sert.** Republier la feuille de route oblige à relire sa version en ligne ; les clos
en font l'essentiel et grossissent à chaque clôture. Ils partent dans un artefact d'archive,
publié par la liste d'attente ; la feuille garde l'en-tête, la TODO, le graphique et un lien.

**Estimé.** 2 fiches · ≈6,00 $ — ≈3,00 $/fiche sur 85 clos (le 2026-09-29).

**Fait.** Rien. Ouvert le 2026-09-29, cadré en 2 fiches, `ARC1` à jouer.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

**Mesuré au cadrage (2026-09-29)**, feuille du kit : **76 901 octets, 615 lignes, 87 clos** ; la
`ZONE:clos` en fait **60 107** (78,2 %). Autres feuilles : Cairn 65 960 octets (35 `<tr>`),
MapDecorator 9 501, ProjetONZSM 5 767, TrackGen 7 347. La zone est lue ou écrite à ~10 endroits
de `scripts/vlp.py` (`page_feuille` puis `zone(html, "clos", …)` : `couts_clos`, `clos_du_projet`,
`recompter`, `prix`, `gras_et_liens`, `niveau`, `clore`, le prix moyen d'`ouvrir`…).

**Tranché au cadrage (l'utilisateur)** :
- l'archive est **un artefact à part** : `<contexte>/artefacts/archive-clos.html`, son URL dans le
  champ `**artefact archive**` de `CHANTIER.md` ;
- **tous** les clos y vont — la feuille n'en liste plus aucun ;
- `clore` ajoute sa ligne à l'archive et la met **en liste d'attente** (`attente`, chantier `LOC`) :
  elle part une fois, en fin de séance ; elle peut avoir quelques clos de retard ;
- le graphique `couts.svg` **reste sur la feuille**, dessiné sur tous les clos de l'archive.

**Invariant** : un projet sans `archive-clos.html` se lit et s'écrit comme aujourd'hui, sur sa
feuille — rien ne change chez lui tant qu'`archive` n'y est pas lancé.

**Dehors** : lancer `archive` sur les quatre autres projets (chacun le fera à son rythme) ;
toucher aux pages de chantier ; ranger par date ou par seuil.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ARC1` | Lire et écrire les clos par `page_clos` | rien |
| `ARC2` | `vlp.py archive` déplace les clos, `clore` tient l'archive | `ARC1` |

---

<!-- FICHE:ARC1 -->
## ARC1 [ ] — Lire et écrire les clos par `page_clos`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `scripts/vlp.py`, `page_clos(projet)` : `<contexte>/artefacts/archive-clos.html` s'il
existe, sinon `page_feuille(projet)`. Tout ce qui lit ou écrit les lignes de `ZONE:clos` passe
par elle (lignes, pied « Total cumulé », prix, marques de recompte, liens) ; ce qui écrit
l'en-tête, la TODO, `encours` ou le graphique reste sur la feuille. `couts.svg` se dessine
sur les lignes de `page_clos`, et s'écrit à côté de la feuille. Un commentaire au-dessus de
`page_clos` dit la règle ; la docstring de tête, une phrase.

**Critère de fin**
1. Tests dans `scripts/test-vlp.py`, sur un projet temporaire dont la feuille n'a **aucune** ligne
   close et dont `archive-clos.html` en a deux : `clore` ajoute sa ligne en tête de l'archive
   (feuille sans ligne close) ; `recompter`, `prix --a-blanc` et le prix moyen d'`ouvrir
   --estime-fiches` lisent l'archive ; `couts.svg` a deux barres. Sans archive : les tests
   d'avant passent tels quels.
2. Mutant joué par `vlp.py mutant` : `page_clos` qui rend toujours la feuille → un test tombe.
3. `py scripts/test-vlp.py` : `OK` ; pyright 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:ARC2 -->
## ARC2 [ ] — `vlp.py archive` déplace les clos, `clore` tient l'archive

**Dépend de** : `ARC1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `templates/artefact-archive-clos.html`,
`cloture.md`, `ARTEFACTS.md`, `CHANTIER.md`, `context AI/artefacts/` — et rien d'autre.

**Prompt**
Un gabarit `templates/artefact-archive-clos.html` : titre, lien vers la feuille, la `ZONE:clos`
et son pied, `vlp.css`/`vlp.js` comme la feuille. `vlp.py archive <projet> [--url URL]` crée
l'archive depuis le gabarit, y déplace **toutes** les lignes closes et le pied de la feuille, et
laisse sur la feuille un bloc `ZONE:archive` : « <n> chantiers clos · <total cumulé> — dans
l'archive » avec le lien (`--url`, sinon le champ `**artefact archive**`), et le graphique ;
`--url` écrit aussi le champ. Relancé : rien ne bouge. `ARCHIVE <n> lignes · feuille <octets
avant> → <après>`. `clore`, archive présente : refait ce bloc et fait `attente ajouter` pour
l'archive (URL connue). `cloture.md` et `ARTEFACTS.md` : une phrase chacun, sans recopier.

**Critère de fin**
1. Tests : `archive` déplace deux lignes et le pied, bloc écrit, relancé sans changement ;
   `clore` ensuite refait le bloc (n + 1) et met l'archive en attente. Mutant par `vlp.py mutant`.
2. Réel, sur le kit : `archive .` — les comptes bruts `ARCHIVE`, la feuille sous **20 000**
   octets ; l'archive publiée (première URL), puis `archive . --url <URL>`.
3. `py scripts/test-vlp.py` : `OK` ; pyright 0 erreur.
<!-- /FICHE -->
