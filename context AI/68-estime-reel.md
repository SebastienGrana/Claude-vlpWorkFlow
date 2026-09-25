> **QUAND LIRE** : on joue une fiche `EST*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache EST<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier EST — L'estimé face au réel, à chaque clôture

**À quoi il sert.** La TODO estime chaque chantier en fiches, et rien ne compare
ensuite (`CPT`, estimé « ~2 fiches », en a joué 4). `ouvrir` notera l'estimé —
fiches et $ —, `clore` l'écrira à côté du réel, sans que personne le recopie.

**Estimé.** 1 fiches · ≈3,91 $ — ≈3,91 $/fiche sur 55 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 3 fiches, `EST1` à jouer.

**Session** : 75f1eda3-6e28-4b15-ac57-920dcc7f7125

**Session** : f09814fe-9212-4e08-b35d-79e1fa2f3be1

## Le socle commun

Décidé au cadrage (2026-09-26) : on compare **fiches et $** ; c'est **le script**
qui écrit ; le $ estimé est **calculé** (moyenne des clos × fiches estimées) ;
les chantiers déjà clos restent **dehors**.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `cmd_ouvrir` | `scripts/vlp.py:3184` | écrit `CHANTIER.md`, l'index, le routage ; options l. 3356 |
| `cmd_clore` | `scripts/vlp.py:2995` | ligne `**Fait.**`, `ZONE:bilan`, ligne `CLOS …` ; options l. 3347 |
| `total_mesure` | `cmd_clore`, étape « 1 ter » | total tokens du chantier, mesuré sur la page |
| `estimation_usd(n)` | `scripts/vlp.py:1699` | `≈X $` au taux `USD_PAR_MTOKENS` (l. 1696) |
| `lignes_clos(corps)` | `scripts/vlp.py:2507` | les lignes de `ZONE:clos` de la feuille de route |
| `page_feuille(projet)` | `scripts/vlp.py` | le chemin de la feuille de route |
| `TITRE` | `scripts/vlp.py:263` | le motif d'un titre de fiche `## X1 [ ] — …` |
| `appel`, `verifier` | `scripts/test-vlp.py:242`, `:64` | lancer une sous-commande, tester sa sortie |

- **La ligne d'estimé**, dans le fichier de fiches, seule sur sa ligne, juste
  avant `**Fait.**` : `**Estimé.** <N> fiches · ≈<X> $ — <Y> $/fiche sur <K> clos (le <date>).`
  Nombres décimaux à virgule (`0,5`), comme `estimation_usd`.
- **La moyenne** : sur les lignes de `ZONE:clos` dont le total est mesuré
  (`(<n> tokens)` entre parenthèses) ; fiches d'une ligne = `n − 1 + 1` de sa
  plage `X1–Xn`, une seule fiche pour `ZER1`. Mesuré le 2026-09-26 : 56 lignes
  closes. ⚠️ Limite connue : `REV1–REV4` sous-compte `REV` (TODO n° 57, `PLG`).
- **Le réel à la clôture** : fiches cadrées = titres `TITRE` ; fiches jouées =
  titres `[x]` ; $ = `estimation_usd(total_mesure)`.
- Un test bâtit son projet dans un dossier temporaire, jamais le vrai dépôt.
  Tout `.py` touché passe `pyright scripts/` à 0 erreur, compte brut au rendu.

Hors chantier : une colonne « estimé » sur la feuille de route (son gabarit),
`/vlp:check`, et le rattrapage des chantiers déjà clos.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `EST1` | Noter l'estimé à l'ouverture | rien |
| `EST2` | Écrire l'estimé à côté du réel à la clôture | `EST1` |
| `EST3` | Faire passer l'estimé par `/vlp:chantier` | `EST1` |

`EST2` et `EST3` sont indépendantes l'une de l'autre, pas de `EST1`.

---

<!-- FICHE:EST1 -->
## EST1 [x] — Noter l'estimé à l'ouverture

**Session** : 90bf84ae-82bc-4221-92ea-2a25673b4dbf
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute à `ouvrir` l'option `--estime-fiches N` (décimal, `0,5` ou `0.5`
acceptés). Donnée, `ouvrir` calcule la moyenne $/fiche sur la feuille de
route (règle du socle), puis écrit la ligne `**Estimé.**` du socle dans le
fichier de fiches, juste avant `**Fait.**`. Déjà présente : ne la réécris pas,
dis-le. Pas de feuille, ou aucun clos mesuré : `GARDE:` qui le dit, le reste
de `ouvrir` s'écrit quand même. Sans l'option : rien ne change.
La ligne de sortie `OUVERT …` gagne ` · estimé <N> fiches ≈<X> $`, ou
` · estimé gardé` si la ligne existait.
Docstring de `vlp.py` à jour, dans le paragraphe de `ouvrir`.

**Critère de fin**
`py scripts/test-vlp.py` : 0 échec, compte brut. Un nouveau test, sur une
feuille factice à deux clos mesurés (`A1–A3` 3 000 000 tokens, `B1` 1 000 000),
attend `1 000 000` tokens par fiche, donc pour `--estime-fiches 2` la ligne
`**Estimé.** 2 fiches · ≈1,67 $ — ≈0,84 $/fiche sur 2 clos` avant `**Fait.**`.
Mutant : compter une fiche par ligne close au lieu de lire la plage — le test
tombe. Un second appel : `estimé gardé`, une seule ligne `**Estimé.**`.
`pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:EST2 -->
## EST2 [x] — Écrire l'estimé à côté du réel à la clôture

**Session** : f86e52fa-fbd8-4e04-848e-240a52ae8542
**Dépend de** : `EST1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_clore`, relis la ligne `**Estimé.**` du fichier de fiches et
compose : `estimé <N> fiches ≈<X> $ · cadré <C> · joué <J> fiches ≈<Y> $`
(réel : règle du socle). Écris-le à trois endroits : la ligne de sortie
`CLOS …`, juste avant ` — <projet>` ; la ligne `**Fait.**` du fichier de
fiches, en fin de phrase ; un `<p>Estimé : …</p>` dans la `ZONE:bilan`
de la page, après « Surpris ». Sans ligne `**Estimé.**` (chantier ouvert
avant `EST`) : `estimé non noté · cadré <C> · joué <J> fiches ≈<Y> $`,
sans `GARDE`. Total non mesuré : `≈? $` pour le réel.
Docstring de `vlp.py` à jour, dans le paragraphe de `clore`.

**Critère de fin**
`py scripts/test-vlp.py` : 0 échec, compte brut. Le test de `clore` existant
(`scripts/test-vlp.py`, « clore : bilan ») gagne une ligne `**Estimé.**` et
attend dans `CLOS` `estimé 2 fiches ≈… $ · cadré 2 · joué 1 fiches` (Q2
abandonnée), valeurs recopiées de sa sortie, et le même texte dans la page et
dans `**Fait.**`. Un second projet sans la ligne attend `estimé non noté`.
Mutant : compter les fiches cadrées comme jouées — le test tombe.
`pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:EST3 -->
## EST3 [x] — Faire passer l'estimé par /vlp:chantier

**Session** : f09814fe-9212-4e08-b35d-79e1fa2f3be1
**Dépend de** : `EST1`.
**Fichiers** : `skills/chantier/SKILL.md`, `context AI/68-estime-reel.md`
(ce fichier) — et rien d'autre.

**Prompt**
À l'étape 6 de `skills/chantier/SKILL.md`, la commande `ouvrir` gagne
`--estime-fiches <n>`, et une ligne de prose : `<n>` est le nombre recopié
de la colonne « Coût estimé » de la ligne TODO du chantier ; pas estimé, ou
chantier hors TODO : l'option s'omet. Rien d'autre dans la commande — le
calcul est au script. Puis lance, sur ce kit même,
`py scripts/vlp.py ouvrir . --fiches "context AI/68-estime-reel.md" --titre "L'estimé face au réel, à chaque clôture" --estime-fiches 1`
(la TODO estimait `EST` à « ~1 fiche ») : `EST` se clôt avec sa propre comparaison.

**Critère de fin**
`grep -c -- "--estime-fiches" skills/chantier/SKILL.md` vaut 1 (compte brut).
`grep -c "^\*\*Estimé\.\*\* 1 fiches" "context AI/68-estime-reel.md"` vaut 1,
et la sortie de `ouvrir` contient ` · estimé 1 fiches ≈`.
`py scripts/vlp.py valider "context AI/68-estime-reel.md"` : `VALIDE 3 fiches`.
<!-- /FICHE -->
