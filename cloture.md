> **QUAND LIRE** : la dernière fiche d'un chantier vient d'être cochée, ou on
> décide de clore un chantier tel quel sans jouer les fiches restantes.
> Lu par `/vlp:tache` (étape 7), par `/vlp:enchainer` (étape 5) et par
> `/vlp:chantier` (étape 0 ter), qui l'appliquent sans la réécrire.

# Clore un chantier — les quatre temps, dans cet ordre

Une clôture qui s'arrête au milieu laisse un projet qui ment. Si l'un des quatre
échoue, **dis laquelle et où tu t'es arrêté** : la reprise saura quoi finir.

Des fiches restent non cochées (clôture décidée, pas atteinte) : elles sont
**abandonnées**, pas faites — ne les coche pas, et dis lesquelles et pourquoi.

## 1. La TODO

Au fichier d'état, retire la ligne du chantier de la TODO, ou reformule-la s'il en
reste : la feuille de route que l'étape 2 écrit la relit.

## 2. Tout ce qui se déduit — un appel

```bash
<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" clore . --livre "<ce qu'il a livré, une ligne>" --abandon "<fiches abandonnées et pourquoi>" --surpris "<ce qui a surpris, une ligne>" --resume "<ce qu'il a livré, en quelques mots>"
```

`<python>` : la valeur de `PYTHON=` dans la carte de la commande qui clôt. Sans
abandon, pas de `--abandon`. Le script
pose `**CLOS**` et `**Fait.**` dans le fichier de fiches ; remet les deux lignes
de `CHANTIER.md` à `aucun` ; passe à « clos » la ligne de l'index, retire celle
du routage de `CLAUDE.md`, et ajoute `--resume` à sa section « Où on en est »,
qui ne garde que les derniers clos ; rend visible la `ZONE:bilan` de la page du
chantier et en régénère les coûts ; puis écrit la feuille de route locale (ligne
des clos, total cumulé, chantier en cours, TODO de l'étape 1). Le total du
chantier — fiches, hors fiches et sous-agents — est celui qu'il vient d'écrire sur
la page : la ligne `CLOS … · chantier <n>` le donne, le même partout. Lis les lignes
`FEUILLE` et `CLOS` ; une `GARDE:` dit ce qui n'est pas écrit — écris-le alors à
la main.

Puis, au fichier d'état, une ligne de bilan datée : ce que le chantier a livré, ce
qu'il a laissé ouvert, et ce `<n>` tel quel, sans arrondi (règle des comptes bruts :
`methode-chantier.md`). Pas un récit — le détail est dans git et dans le fichier de
fiches. Une piste qui a échoué pour une raison qui **vaut au-delà de ce chantier** va
ici aussi : c'est le seul endroit que la prochaine session lira.

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

Puis, en une ligne : **quelle fiche a coûté le plus cher**, et pourquoi — `cout`
les donne, une ligne par fiche :
`<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" cout "<fichier de fiches>"`.

## Ce que le chantier laisse — un menu, rien d'obligatoire

Un **questionnaire à cases multiples**, jamais une liste à taper : une case par
choix, une ligne d'explication chacune. N'exécute que ce qui est coché —
plusieurs à la fois se font, aucun aussi.

1. **Brainstorm** — des idées de chantiers pour ce projet. **Lis d'abord en
   entier la liste des chantiers possibles**, la TODO du fichier d'état, avant
   de chercher : une idée qui en recoupe une ligne le dit, et la nomme. Ce qui
   est retenu va dans cette TODO, et nulle part ailleurs : c'est là que
   `/vlp:chantier` ira les chercher. Les idées se présentent **vulgarisées**,
   avant le choix : une image simple du kit d'abord (une salle d'examen, un
   surveillant…), puis pour chacune, une ligne par point — le problème, le
   risque, ce qu'elle ferait, son coût —, le jargon après ; enfin un avis.
2. **Ce qui a été appris** — ce chantier a-t-il tranché quelque chose qui vaut
   au-delà de lui ? Une règle de méthode va dans `methode-chantier.md` ; une
   façon de travailler propre à l'utilisateur va **en mémoire**, un fait par
   fiche. C'est ainsi que le kit apprend au fur et à mesure, au lieu de
   réapprendre la même chose à chaque chantier.
3. **Essaimer** — remettre les autres projets équipés à niveau :
   `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" niveau <projet>`.
4. **La dette repérée** — ce qu'on a vu passer sans le traiter. Petite (une
   fiche ou moins) : elle se corrige **tout de suite**, une tâche par dette —
   test et mutant s'il y a du code —, dans un commit à elle
   (`Dette <chantier> : …`), avant la question du push. Plus grosse : elle se
   présente comme un chantier, et l'utilisateur tranche sur le moment — ouvert
   tout de suite, ou versé dans la TODO. Ce qui n'est écrit nulle part est perdu
   au `/clear`.

Le menu compte quatre cases, pas cinq : **le push n'y est pas**, ni le prompt du
chantier suivant, qui n'est pas facultatif (« Pour finir »). Il se demande
**après**, dans une question à lui seul — `git push`, jamais sans confirmation
explicite, même si l'utilisateur a confirmé pour un chantier précédent. Une
case cochée au milieu de trois autres n'est pas une confirmation : un push
publie, et ne se reprend pas.

## Pour finir

Le **dernier message** de la clôture, après le push et toute question — le dernier
texte du tour, **sans aucun appel d'outil après lui** : l'app replie le texte écrit
entre deux appels, et il n'est pas vu (constaté le 2026-09-25). Dans cet ordre :

1. le **prompt du chantier suivant**, toujours, même si rien n'est coché, dans un
   bloc de code `text` : le sujet, ce que celui-ci vient de livrer, et les seuls
   fichiers à ouvrir — jamais avant une question, où il n'est pas vu ;
2. les deux liens ;
3. la suite : `/clear`, puis coller le prompt.
