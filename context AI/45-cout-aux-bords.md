> **QUAND LIRE** : on joue une fiche `FIN*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache FIN<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier FIN — Le coût juste, aux deux bords du chantier

**À quoi il sert.** `vlp.py cout` coupe une session aux commits de fiche. Mais « hors fiches »
part du début de la session, et s'arrête au dernier commit de fiche : dans une session qui
enchaîne plusieurs chantiers, le deuxième compte le premier ; et la clôture n'est comptée
qu'après son propre commit, jamais au bilan. Les deux bords seront bornés au chantier, la
première fiche se mesurera avant son commit (n° 42 `OUV`), et `clore` régénérera les coûts de
la page.

**Fait.** Rien. Ouvert le 2026-09-24, cadré en 3 fiches, `FIN1` à jouer.

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `heures_commits` | `scripts/vlp.py:934` | depuis `FIN1` : `({id: heure}, [heures des commits qui nomment le préfixe], [heures des autres])`, heures d'auteur ; `None` sans Git, sans dépôt ou sans commit de fiche, et sa raison dans `pourquoi` |
| `plages` | `scripts/vlp.py:972` | `([(id, (début, fin))], [plages hors fiches])` ; depuis `FIN1` : la première fiche part du dernier commit antérieur qui nomme le préfixe, à défaut de l'origine (le dernier des autres avant ce début) ; hors fiches : de l'origine à ce début, et du dernier commit de fiche au premier suivant qui nomme le préfixe, sinon jusqu'au bout |
| `parts_aux_commits` | `scripts/vlp.py:1002` | mesure chaque plage dans chaque session et ses sous-agents ; `None` sans transcript mesurable |
| `regenerer` | `scripts/vlp.py:1159` | régénère fiches, coûts, avancement et date d'une page ; lève `ValueError` si une zone manque |
| le bilan de page de `clore` | `scripts/vlp.py:1958` à `1976` | pose `ZONE:bilan`, cache `ZONE:blocage` ; ne touche pas aux coûts |
| la docstring du module | `scripts/vlp.py:51` à `56` (`page`), `114` à `130` (`clore`) | ce que `page` et `clore` promettent |
| les tests de découpe | `scripts/test-vlp.py:427` à `553` | dépôt `avec` : tours aux heures `T0` + 50, 200, 250, 400, 700, 1000 ; commits à 100 « Chantier Q ouvert », 300 `Q1`, 600 `Q2`, 800 « Chantier Q clos », 900 « Autre » ; dépôt `multi` et tests « plages : … » de `FIN1` à la fin |
| les tests de `clore` | `scripts/test-vlp.py:657` à `757` | projet bâti à la main, page tirée du gabarit `artefact-chantier.html` (fiches `&lt;R1&gt;` à `&lt;R3&gt;`) |

**Mesuré à l'ouverture, le 2026-09-24.** Toute la nuit tient dans une session (`1ba64929…`).
- `vlp.py cout` sur `43-case-relue.md` (CAS) : TOTAL 11 729 608 · 94 tours. Son bilan en dit
  10 041 615, mesuré avant son commit de clôture : l'écart, 1 687 993, est la clôture.
- Sur `44-pre-commit.md` (VAL) : `VAL1` 3 368 752 · 40 tours ; hors fiches 15 285 294 · 115 tours ;
  TOTAL 18 654 046 · 155 tours — CAS compris.
- Attendu pour VAL, mesuré par plage : hors fiches 3 555 686 · 21 tours, soit le cadrage (de
  `9fe9b7e` à `a56c19f`) 2 087 345 · 7 et la clôture (de `c5123af` à `cd6325a`) 1 468 341 · 14 ;
  TOTAL 6 924 438 · 61 tours.
- Des sujets nomment un préfixe avant son ouverture : `4ef74e7` (FIN, EST, RCP), `bf058b0`
  (PYT, MTK, PER), `8463f13` (PYT).

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dort ; à revoir au réveil).
- FIN est élargi : au bord de début, vu cette nuit, et à `OUV` (n° 42), qui touche la même
  fonction.
- Début : le dernier commit qui ne nomme pas le préfixe, avant le début de la première fiche.
  Un sujet qui nomme le préfixe juste avant l'ouverture (une dette versée dans la TODO) y fait
  entrer le travail d'avant lui : accepté, c'est borné à ce commit.
- Fin : le premier commit qui nomme le préfixe après le dernier commit de fiche — la clôture ;
  sans lui, le bout du transcript. Une mention plus tardive (un recompte) ne l'étire plus.
- Le troisième bord de la TODO (un tour joué après le commit de sa fiche compte à la suivante)
  reste tel quel : couper au commit est la seule règle qui tienne pour `/vlp:tache` comme pour
  `/vlp:enchainer` ; 2 tours mesurés sur `CPT4`.

**Ce qu'on ne fait pas.** Recompter les chantiers clos (n° 37 `RCP`). Réécrire les bilans déjà
posés : ils restent, les pages se régénèrent. Le troisième bord. Le cadrage joué dans une
session sans ligne `**Session**` : il n'est mesuré nulle part, autre chantier.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `FIN1` | Borner « hors fiches » au chantier : l'origine, la clôture | rien |
| `FIN2` | Mesurer la première fiche avant son commit | `FIN1` |
| `FIN3` | `clore` régénère les coûts de la page | `FIN1` |

`FIN1` puis `FIN2` touchent les mêmes fonctions : en série. `FIN3` pourrait passer avant `FIN2`.

---

<!-- FICHE:FIN1 -->
## FIN1 [x] — Borner « hors fiches » au chantier : l'origine, la clôture

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`heures_commits`, `plages`), `scripts/test-vlp.py` — et rien
d'autre.

**Prompt**
1. `heures_commits` rend aussi les heures des commits qui ne nomment pas le préfixe, triées :
   `(commits, prefixe, autres)`. Sa docstring le dit. Le test « heures_commits : heure
   d'auteur… » (`scripts/test-vlp.py:459`) attend alors `autres` = `[T0 + 900]`.
2. Dans `plages`, trois changements, et sa docstring les dit :
   - **l'origine** : le plus récent de `autres` avant le début de la première fiche (`debut`),
     ou avant le commit de la première fiche si `debut` vaut `-INFINI` ; à défaut, `-INFINI`.
     La première fiche part de `debut`, ou de l'origine si `debut` vaut `-INFINI` ;
   - hors fiches avant : de l'origine au début de la première fiche, au lieu de `-INFINI` ;
   - hors fiches après : du dernier commit de fiche au premier de `prefixe` qui le suit ; à
     défaut, jusqu'au bout (`INFINI`). Le cas des fiches à session sans commit ne change pas.
3. Des tests, dans un second dépôt à part, sur le moule du dépôt `avec` (lignes 448 à 457),
   avec son propre transcript :
   - un commit « Chantier P clos » avant « Chantier Q ouvert » : un tour avant lui ne compte
     nulle part ; un tour entre les deux compte hors fiches ;
   - sans commit de clôture : un tour après le dernier commit de fiche compte hors fiches ;
   - un commit qui nomme le préfixe après la clôture (« RCP1 : recompte Q ») : un tour entre
     la clôture et lui ne compte pas ;
   - sans commit qui nomme le préfixe avant la première fiche : elle part de l'origine.
   Les tests de découpe existants (lignes 459 à 499) passent sans qu'un de leurs chiffres change.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`. `py scripts/vlp.py cout "context AI/44-pre-commit.md"` rend
`VAL1` 3 368 752 · 40 tours, hors fiches 3 555 686 · 21 tours, TOTAL 6 924 438 · 61 tours ;
`py scripts/vlp.py cout "context AI/43-case-relue.md"` rend un TOTAL inchangé, 11 729 608 · 94 tours.
<!-- /FICHE -->

<!-- FICHE:FIN2 -->
## FIN2 [x] — Mesurer la première fiche avant son commit

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : `FIN1`.
**Fichiers** : `scripts/vlp.py` (`heures_commits`, `plages`, docstring du module lignes 51 à
56), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Le cas : `/vlp:tache` mesure une fiche après l'avoir cochée, avant son commit. Pour la première
fiche d'un chantier, aucun commit de fiche n'existe : `heures_commits` rend `None` et `cout` rend
la session entière (`FIL1` : 139 tours à la mesure, 17 une fois commitée).
1. `heures_commits` : sans commit de fiche mais avec un commit qui nomme le préfixe, rends
   `({}, prefixe, autres)`. `None` seulement si aucun commit ne nomme le préfixe, et la raison
   dans `pourquoi` le dit.
2. `plages` : sans commit de fiche, le début est le plus récent de `prefixe`, l'origine se
   calcule comme dans `FIN1`, et la fiche à session sans commit va de ce début au bout. Sans
   commit de fiche ni fiche à session, rien ne plante : `parts_aux_commits` rend `None`, et
   `cout` retombe sur les sessions entières, comme aujourd'hui.
3. La docstring du module, lignes 51 à 56, dit le repli juste : sans Git, ou sans commit qui
   nomme le préfixe.
4. Ces tests, avec ces noms et ces valeurs, dans `scripts/test-vlp.py` après ceux de `FIN1`
   (« plages : … ») :
   - « plages : sans commit de fiche, la fiche cochée part de l'ouverture » :
     `mod.plages([("Q1", "a", True, ["s"]), ("Q2", "b", False, [])], ({}, [100], [30, 900]), G)`
     rend `([("Q1", (100, mod.INFINI))], [(30, 100)])` ;
   - « plages : sans commit de fiche ni session, rien » :
     `mod.plages([("Q1", "a", False, [])], ({}, [100], [30]), G)` rend `([], [])` ;
   - « cout : la première fiche avant son commit » : un dépôt à part, sur le moule du dépôt
     `multi` de `FIN1`, commits à `T0` + 60 « Chantier P clos : fini » et `T0` + 100 « Chantier
     Q ouvert : cadré » ; le fichier de fiches de `QFICHES`, mais `Q2` décochée et sans ligne
     `**Session**` ; `cout` rend `Q1 · ≈700,0k (700 000) · 7 tours · 3,50 $` et
     `TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours` — le tour de `T0` + 50 ne
     compte pas ;
   - le test « heures_commits : aucun commit de fiche, et pourquoi » attend la raison
     `aucun commit qui nomme Z`.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`. Les deux `cout` du critère de `FIN1` rendent les mêmes
nombres qu'après `FIN1`.
<!-- /FICHE -->

<!-- FICHE:FIN3 -->
## FIN3 [ ] — `clore` régénère les coûts de la page

**Dépend de** : `FIN1`.
**Fichiers** : `scripts/vlp.py` (`cmd_clore`, docstring lignes 114 à 130), `scripts/test-vlp.py`,
`cloture.md` (étape 2) — et rien d'autre.

**Prompt**
Le cas : `/vlp:tache` mesure la dernière fiche avant son commit, et `clore` ne touche pas aux
coûts ; la page close garde donc ce coût d'avant le commit, et ne compte pas la clôture.
1. Dans `cmd_clore`, au bilan de page : une fois `ZONE:bilan` posée dans la page, passe-la par
   `regenerer(page, fichier de fiches, {}, [], date, gardes)` et écris ce qu'elle rend. Une
   `ValueError` : la garde « page du chantier : coûts non régénérés — <erreur> », et la page
   s'écrit avec son seul bilan.
2. La docstring de `clore` (lignes 114 à 130) et l'étape 2 de `cloture.md` le disent, en
   quelques mots : `clore` rend visible la `ZONE:bilan` **et régénère les coûts** de la page.
3. Un test nommé « clore : la page régénérée, fiches du fichier », dans le bloc de `clore`
   juste après « clore : ZONE:bilan visible, blocage caché » : `pq` contient
   `<span class="id">Q1</span>` et `<span class="id">Q2</span>`, et ne contient plus ni
   `&lt;R1&gt;` (une fiche du gabarit) ni `<p class="mono cout-total">`. Les assertions
   existantes du bloc passent sans changer.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`, et le test de l'étape 3 y figure.
<!-- /FICHE -->
