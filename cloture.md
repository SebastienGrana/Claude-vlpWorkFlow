> **QUAND LIRE** : la dernière fiche d'un chantier vient d'être cochée, ou on
> décide de clore un chantier tel quel sans jouer les fiches restantes.
> Lu par `/vlp:tache` (étape 7), par `/vlp:enchainer` (étape 5) et par
> `/vlp:chantier` (étape 0 ter), qui l'appliquent sans la réécrire.

# Clore un chantier — les cinq écritures, dans cet ordre

Une clôture qui s'arrête au milieu laisse un projet qui ment. Si l'une des cinq
échoue, **dis laquelle et où tu t'es arrêté** : la reprise saura quoi finir.

Des fiches restent non cochées (clôture décidée, pas atteinte) : elles sont
**abandonnées**, pas faites — ne les coche pas, et dis lesquelles et pourquoi.

## 1. Le fichier d'état

Avant d'écrire la ligne de bilan, si `${CLAUDE_PLUGIN_ROOT}/scripts/mesure-tokens.py`
existe et que le fichier de fiches qu'on clôture porte des lignes
`**Session**` : appelle le script sur toutes, et garde le total brut, sans
arrondi (règle des comptes bruts : `methode-chantier.md`). Sinon, pas de total.

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" sessions "<fichier de fiches>" | tr -d '\r' | tr '\n' '\0' | xargs -0 sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" mesure
```

Une ligne de bilan, datée : ce que le chantier a livré, ce qu'il a laissé
ouvert, et ce total. Pas un récit — le détail est dans git et dans le fichier de fiches.
Retire la ligne du chantier de la TODO, ou reformule-la s'il en reste.

Une piste qui a échoué pour une raison qui **vaut au-delà de ce chantier** va
ici aussi : c'est le seul endroit que la prochaine session lira.

## 2. Le fichier de fiches, `CHANTIER.md` et la feuille de route locale — un appel

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" clore . --livre "<ce qu'il a livré, une ligne>" --tokens <total brut de l'étape 1> --abandon "<fiches abandonnées et pourquoi>"
```

Sans total, pas de `--tokens` ; sans abandon, pas de `--abandon`. Le script
pose `**CLOS**`, remet les deux lignes de `CHANTIER.md` à `aucun`, ajoute la
ligne des clos avec l'URL et la lettre, puis écrit la feuille de route locale
(ligne des clos, total cumulé, chantier en cours, TODO de l'étape 1). Lis les
lignes `FEUILLE` et `CLOS` ; une `GARDE:` dit ce qui n'est pas écrit.

## 3. `CLAUDE.md`

La ligne de routage du chantier dit désormais **clos**. Un routage qui envoie
vers un chantier clos coûte une session entière.

## 4. L'artefact du chantier

Lire, réécrire, republier :

- `Artifact`, `action: "read"`, son `url` (la lecture est imposée : sans elle
  la republication est refusée) ;
- `ZONE:bilan` rendue visible — retire son `hidden` — avec la date, ce que le
  chantier a livré, ce qui a surpris ;
- `ZONE:blocage` remise en `hidden` ;
- les fiches abandonnées, s'il y en a, laissées **non faites** et dites comme
  telles ;
- republication : `file_path` local **et** `url`, pas de `favicon`,
  `label` : `clos`.

## 5. La feuille de route

Déjà écrite à l'étape 2 : `action: "read"` sur son `url` (« **artefact feuille
de route** » de `CHANTIER.md`), puis republication du fichier local avec cette `url`,
`label` : `<chantier> clos`.

Si une publication échoue, dis-le en une ligne et continue : les écritures
locales sont ce qui compte, les pages se rattrapent.

## Pour finir

Donne les deux liens, et dis la suite : `/clear`, puis `/vlp:chantier` pour ouvrir
le suivant.

## Commit et push — jamais sans confirmation

Une fois les cinq écritures faites, propose un `git commit` (message résumant
le chantier clos) puis un `git push` — deux gestes irréversibles, deux
questionnaires séparés. Ne commit ni ne push sans confirmation explicite à
chaque fois, même si l'utilisateur a déjà confirmé pour un chantier
précédent : une clôture ne vaut que pour elle-même.
