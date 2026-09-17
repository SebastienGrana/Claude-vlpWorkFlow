> **QUAND LIRE** : la dernière fiche d'un chantier vient d'être cochée, ou on
> décide de clore un chantier tel quel sans jouer les fiches restantes.
> Lu par `/vlp:tache` (étape 7), par `/vlp:enchainer` (étape 5) et par
> `/vlp:chantier` (étape 0 ter), qui l'appliquent sans la réécrire.

# Clore un chantier — les quatre temps, dans cet ordre

Une clôture qui s'arrête au milieu laisse un projet qui ment. Si l'un des quatre
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

## 2. Tout ce qui se déduit — un appel

```bash
sh "${CLAUDE_PLUGIN_ROOT}/scripts/vlp" clore . --livre "<ce qu'il a livré, une ligne>" --tokens <total brut de l'étape 1> --abandon "<fiches abandonnées et pourquoi>" --surpris "<ce qui a surpris, une ligne>" --resume "<ce qu'il a livré, en quelques mots>"
```

Sans total, pas de `--tokens` ; sans abandon, pas de `--abandon`. Le script
pose `**CLOS**` et `**Fait.**` dans le fichier de fiches ; remet les deux lignes
de `CHANTIER.md` à `aucun` et ajoute la ligne des clos ; passe à « clos » les
lignes de l'index et du routage de `CLAUDE.md`, et prolonge sa section « Où on
en est » par `--resume` ; rend visible la `ZONE:bilan` de la page du chantier ;
puis écrit la feuille de route locale (ligne des clos, total cumulé, chantier
en cours, TODO de l'étape 1). Lis les lignes `FEUILLE` et `CLOS` ; une `GARDE:`
dit ce qui n'est pas écrit — écris-le alors à la main.

## 3. L'artefact du chantier

Déjà écrit à l'étape 2 : `Artifact`, `action: "read"` sur son `url` (sans
lecture, la republication est refusée), puis republication : `file_path` local
**et** `url`, pas de `favicon`, `label` : `clos`. Des fiches abandonnées y
restent **non faites**.

## 4. La feuille de route

Déjà écrite à l'étape 2 : `action: "read"` sur son `url` (« **artefact feuille
de route** » de `CHANTIER.md`), puis republication du fichier local avec cette `url`,
`label` : `<chantier> clos`.

Si une publication échoue, dis-le en une ligne et continue : les écritures
locales sont ce qui compte, les pages se rattrapent.

## Pour finir

Donne les deux liens, et dis la suite : `/clear`, puis `/vlp:chantier` pour ouvrir
le suivant.

## Commit et push — jamais sans confirmation

Une fois les quatre temps faits, propose un `git commit` (message résumant
le chantier clos) puis un `git push` — deux gestes irréversibles, deux
questionnaires séparés. Ne commit ni ne push sans confirmation explicite à
chaque fois, même si l'utilisateur a déjà confirmé pour un chantier
précédent : une clôture ne vaut que pour elle-même.
