> **QUAND LIRE** : on joue une fiche `ABR*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ABR<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ABR — Mettre notes et journal à l'abri dans un `.md`

**À quoi il sert.** Le résultat, les notes, le journal et le bilan d'un chantier
n'existent que dans sa page HTML : la recréer ou la raccourcir (`PLI`) les perd.
Ils vivront d'abord dans un `.md` à côté de la page, et la page le recopiera.

**Estimé.** 3 fiches · ≈12 $ — ≈3,97 $/fiche sur 63 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 5 fiches, `ABR1` à jouer.

**Session** : 7c039d58-69d1-4e4f-838e-de0e34a55f40

## Le socle commun

**Le fichier.** `<dossier>/artefacts/<NN>-<nom>.md`, à côté de `<NN>-<nom>.html` :
même nom, extension `.md`. Une fonction le calcule depuis la page ; tout le monde
l'appelle, personne ne recolle le chemin.

**Le format** — quatre sections, dans cet ordre, titres recopiés tels quels :

```
# <titre du chantier> — notes et journal
## Résultat
<une ligne>
## Notes
- <ID> : <texte>
## Journal
- <AAAA-MM-JJ> : <texte>
## Bilan
- Livré : <texte>
- Surpris : <texte>
- Estimé : <texte>
```

- Texte **brut** dans le `.md` ; la page l'échappe à la copie (`esc`).
- Une entrée tient sur une ligne : un saut de ligne dans un texte devient une espace.
- **Le `.md` prime.** S'il existe, la page recopie les quatre sections en entier ;
  sinon, on l'amorce d'abord depuis la page, puis on écrit.
- L'amorçage ne perd rien : ce qui est dans la page passe dans le `.md`.

**Ce qui existe déjà** (`scripts/vlp.py`) :

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `esc` | `:1808` | échappe `& < >` |
| `lis_page` | `:1854` | `{id: (état, note html, coût)}` |
| `creer` | `:2158` | page neuve depuis le gabarit, `--resultat` compris |
| `regenerer` | `:2178` | notes (`:2194`), journal (`:2226`) écrits dans la page |
| `cmd_page` | `:2271` | lit, régénère, écrit la page |
| `zone` | `:2505` | bornes d'une `ZONE:` de la page |
| bilan de `clore` | `:3290`–`:3315` | écrit `Livré`, `Surpris`, `Estimé` (`ESTIME_A_ECRIRE`, `:3176`) |
| gabarit | `templates/artefact-chantier.html` | zones `journal` (`:115`), `bilan` (`:122`) |

**Tests.** `scripts/test-vlp.py`, chacun dans son dossier temporaire ; lancer
`py scripts/test-vlp.py`. Chaque fiche de code nomme son test **et** son mutant.
`pyright` sur les fichiers touchés : 0 erreur, compte brut dans le rendu.

**Dehors.** Replier ou raccourcir la page (`PLI`), le CSS et la base claude.ai
(`ALE`), les projets voisins autres que Cairn. Rien n'est republié par les fiches
de code. Cairn est privé : aucun extrait de son contenu dans ce dépôt, des comptes seulement.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ABR1` | Écrire le `.md` et l'amorcer depuis une page | rien |
| `ABR2` | Faire écrire `page` dans le `.md` d'abord | `ABR1` |
| `ABR3` | Faire écrire le bilan de `clore` dans le `.md` | `ABR1` |
| `ABR4` | Dire dans la doctrine que le `.md` est la source | `ABR2`, `ABR3` |
| `ABR5` | Mettre les pages de Cairn à l'abri | `ABR2`, `ABR3` |

`ABR2` et `ABR3` sont indépendantes l'une de l'autre ; `ABR4` et `ABR5` aussi.

---

<!-- FICHE:ABR1 -->
## ABR1 [x] — Écrire le `.md` et l'amorcer depuis une page

**Session** : 72de750c-600b-43d1-b5e7-94c21b471768
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris dans `vlp.py` trois fonctions, au format du socle : le chemin du `.md`
d'une page ; lire un `.md` en `{résultat, notes, journal, bilan}` ; l'écrire.
Puis l'amorçage : tirer ces quatre parts d'une page HTML existante (texte
désechappé, `html.unescape`). Avant de choisir quoi faire d'une balise restée
dans une note, **mesure** : combien de notes et de lignes de journal contiennent
`<` dans `context AI/artefacts/*.html` — donne la commande et le compte.
Ajoute la sous-commande `abri <page.html>…` : crée le `.md` d'une page qui n'en
a pas, **sans toucher la page** ; un `.md` déjà là n'est pas réécrit. Sortie :
`ABRI <md> · résultat <0|1> · notes <n> · journal <n> · bilan <0|1>`, ou
`DÉJÀ <md>`. Une ligne dans la docstring, avec les autres sous-commandes.

**Critère de fin**
Un test bâtit une page à 2 notes, 3 lignes de journal (dont une avec `&amp;`),
un bilan ; `abri` rend `notes 2 · journal 3 · bilan 1`, le `.md` relu redonne le
texte avec `&`, la page est identique octet pour octet ; un second `abri` rend
`DÉJÀ`. Mutant : ne pas désechapper — le test tombe. `py scripts/test-vlp.py` :
compte brut avant/après ; `pyright scripts/vlp.py scripts/test-vlp.py` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:ABR2 -->
## ABR2 [x] — Faire écrire `page` dans le `.md` d'abord

**Session** : 72de750c-600b-43d1-b5e7-94c21b471768
**Dépend de** : `ABR1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_page` : si le `.md` manque, amorce-le depuis la page (ou, à `--creer`,
depuis `--resultat`). Puis écris dans le `.md` : `--note` remplace la note de sa
fiche, `--journal` ajoute une ligne datée (`--date`). Enfin `regenerer` prend
**résultat, notes et journal dans le `.md`** et les recopie en entier dans la
page : la note d'une fiche ne vient plus de l'ancienne page. `--verifier`
n'écrit rien, ni page ni `.md`. La ligne `PAGE …` ne change pas.

**Critère de fin**
Un test : `--creer` puis `--note P1 x` et `--journal y` → le `.md` porte `x` et
`y` ; on **efface la page** et on relance `--creer` puis `page` sans option → la
page reprend `x` et `y` depuis le `.md`. Un second test sur une page sans `.md`
(ancienne) : elle garde ses notes. Mutant : lire la note dans l'ancienne page au
lieu du `.md` — le premier test tombe. Tests et pyright comptés comme en `ABR1`.
<!-- /FICHE -->

---

<!-- FICHE:ABR3 -->
## ABR3 [x] — Faire écrire le bilan de `clore` dans le `.md`

**Session** : 72de750c-600b-43d1-b5e7-94c21b471768
**Dépend de** : `ABR1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `clore`, bloc « 1 ter » : écris `Livré`, `Surpris` et `Estimé` dans la
section `## Bilan` du `.md` (amorcé s'il manque), puis fais recopier la
`ZONE:bilan` de la page depuis le `.md`. `Estimé` passe par `ESTIME_A_ECRIRE`
avant d'être connu : le `.md` doit finir avec la valeur réelle, jamais le
marqueur. Un `clore --verifier` n'écrit pas le `.md`. La ligne `CLOS …` ne
change pas.

**Critère de fin**
Un test de clôture sur un projet temporaire : le `.md` porte `Livré`, `Surpris`
et un `Estimé` sans `\x00` ; la `ZONE:bilan` de la page dit les mêmes trois
textes. Mutant : écrire le `.md` avant de remplacer `ESTIME_A_ECRIRE` — le test
tombe. Tests et pyright comptés comme en `ABR1`.
<!-- /FICHE -->

---

<!-- FICHE:ABR4 -->
## ABR4 [x] — Dire dans la doctrine que le `.md` est la source

**Session** : 72de750c-600b-43d1-b5e7-94c21b471768
**Dépend de** : `ABR2`, `ABR3`.
**Fichiers** : `ARTEFACTS.md` — et rien d'autre.

**Prompt**
Dans `ARTEFACTS.md`, là où il dit qu'on ne retouche pas la page à la main
(section qui cite `vlp.py page`) : ajoute en deux ou trois lignes que résultat,
notes, journal et bilan vivent d'abord dans `<NN>-<nom>.md`, à côté de la page,
et que la page les recopie ; qu'une correction se fait dans le `.md`, puis
`vlp.py page`. Nomme `vlp.py abri` pour une page qui n'a pas encore son `.md`.
Ne recopie ni le format ni un nombre : renvoie à la docstring de `vlp.py`.

**Critère de fin**
`grep -n "abri\|\.md" ARTEFACTS.md` montre les nouvelles lignes ;
`py scripts/vlp.py renvois .` rend `0 absents` ; diff de `ARTEFACTS.md` ≤ 5 lignes ajoutées.
<!-- /FICHE -->

---

<!-- FICHE:ABR5 -->
## ABR5 [x] — Mettre les pages de Cairn à l'abri

**Session** : 72de750c-600b-43d1-b5e7-94c21b471768
**Dépend de** : `ABR2`, `ABR3`.
**Fichiers** : `../Cairn-VlpLib/context AI/artefacts/*.html` (lus, pas modifiés)
— et rien d'autre.

**Prompt**
Compte les pages de Cairn (`*.html` hors `feuille-de-route.html`) et leurs `.md`.
Lance `vlp.py abri` sur toutes les pages qui n'en ont pas. Vérifie que **aucune
page ne change** (`git -C ../Cairn-VlpLib status --short`). Commite les `.md`
dans le dépôt de Cairn, sans pousser. Ici, dans le kit, n'écris que les comptes.

**Critère de fin**
Sortie de `abri` : une ligne `ABRI` par page sans `.md` ; `git status` de Cairn :
seulement des `.md` nouveaux, 0 `.html` modifié ; compte brut pages / `.md`
avant et après, égal à la fin.
<!-- /FICHE -->
