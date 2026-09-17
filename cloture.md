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
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" cout "<fichier de fiches>"
```

`<python>` : la valeur de `PYTHON=` dans la carte de la commande qui clôt.

Une ligne de bilan, datée : ce que le chantier a livré, ce qu'il a laissé
ouvert, et ce total. Pas un récit — le détail est dans git et dans le fichier de fiches.
Retire la ligne du chantier de la TODO, ou reformule-la s'il en reste.

Une piste qui a échoué pour une raison qui **vaut au-delà de ce chantier** va
ici aussi : c'est le seul endroit que la prochaine session lira.

## 2. Tout ce qui se déduit — un appel

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" clore . --livre "<ce qu'il a livré, une ligne>" --tokens <total brut de l'étape 1> --abandon "<fiches abandonnées et pourquoi>" --surpris "<ce qui a surpris, une ligne>" --resume "<ce qu'il a livré, en quelques mots>"
```

Sans total, pas de `--tokens` ; sans abandon, pas de `--abandon`. Le script
pose `**CLOS**` et `**Fait.**` dans le fichier de fiches ; remet les deux lignes
de `CHANTIER.md` à `aucun` ; passe à « clos » la ligne de l'index, retire celle
du routage de `CLAUDE.md`, et ajoute `--resume` à sa section « Où on en est »,
qui ne garde que les derniers clos ; rend visible la `ZONE:bilan` de la page du chantier ;
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

## Le commit de clôture, et la rétro coût — sans demander

Les écritures des quatre temps se commitent **aussitôt, sans confirmation**
(règle du commit par fiche, `methode-chantier.md`) :

```bash
git add -A; git commit -m "Chantier <X> clos : <ce qu'il a livré, une ligne>"
```

Puis, en une ligne et sans rien relancer : **quelle fiche a coûté le plus
cher**, et pourquoi — les chiffres sont ceux de l'étape 1.

## Ce que le chantier laisse — un menu, rien d'obligatoire

Propose ces six choix, numérotés, et **n'exécute que ce qui est demandé** :
plusieurs à la fois se font, aucun aussi.

1. **Le prompt du chantier suivant** — prêt à coller après un `/clear` : le
   sujet, ce que celui-ci vient de livrer, et les seuls fichiers à ouvrir.
2. **Brainstorm** — des idées de chantiers pour ce projet. Ce qui est retenu va
   dans la **TODO du fichier d'état**, et nulle part ailleurs : c'est là que
   `/vlp:chantier` ira les chercher.
3. **Ce qui a été appris** — ce chantier a-t-il tranché quelque chose qui vaut
   au-delà de lui ? Une règle de méthode va dans `methode-chantier.md` ; une
   façon de travailler propre à l'utilisateur va **en mémoire**, un fait par
   fiche. C'est ainsi que le kit apprend au fur et à mesure, au lieu de
   réapprendre la même chose à chaque chantier.
4. **Essaimer** — remettre les autres projets équipés à niveau :
   `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" niveau <projet>`.
5. **La dette repérée** — verser dans la TODO ce qu'on a vu passer sans le
   traiter : ce qui n'y est pas écrit est perdu au `/clear`.
6. **Le push** — `git push`, **jamais sans confirmation explicite**, même si
   l'utilisateur a confirmé pour un chantier précédent : un push publie, et une
   confirmation ne vaut que pour celui qu'elle nomme.

## Pour finir

Donne les deux liens, et dis la suite : `/clear`, puis `/vlp:chantier` pour ouvrir
le suivant.
