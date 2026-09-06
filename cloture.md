> **QUAND LIRE** : la dernière fiche d'un chantier vient d'être cochée, ou on
> décide de clore un chantier tel quel sans jouer les fiches restantes.
> Lu par `/vlp:tache` (étape 7) et par `/vlp:chantier` (étape 0 ter). C'est la **seule**
> description de la clôture : les deux commandes l'appliquent, aucune ne la
> réécrit de son côté.

# Clore un chantier — les cinq écritures, dans cet ordre

Une clôture qui s'arrête au milieu laisse un projet qui ment. Si l'une des cinq
échoue, **dis laquelle et où tu t'es arrêté** : la reprise saura quoi finir.

## 1. Le fichier de fiches

En tête du fichier, sous le titre, la ligne :

```
**CLOS** le <date>. Ne se rejoue pas — ne sert plus qu'à relire son socle.
```

Si des fiches restent non cochées (clôture décidée, pas atteinte), ajoute
en une ligne **lesquelles et pourquoi on les abandonne**. Une fiche abandonnée
n'est pas une fiche faite : ne la coche pas.

## 2. `CHANTIER.md`

Quatre lignes, à la racine du projet :

- « **fichier de fiches courant** » repasse à `aucun` ;
- « **artefact du chantier** » repasse à `aucun` ;
- la ligne du chantier entre dans la table **Chantiers clos** : fichier, plage
  de fiches, date, et **l'URL de son artefact** dans la colonne « Artefact » —
  sans elle, la page est perdue ;
- « **Lettres de fiche déjà prises** » reçoit la lettre du chantier. Elle ne se
  réemploiera jamais, même clos.

## 3. Le fichier d'état

Une ligne de bilan, datée : ce que le chantier a livré, et ce qu'il a laissé
ouvert. Pas un récit — le détail est dans git et dans le fichier de fiches.

Une piste qui a échoué pour une raison qui **vaut au-delà de ce chantier** va
ici aussi : c'est le seul endroit que la prochaine session lira.

## 4. `CLAUDE.md`

La ligne de routage du chantier dit désormais **clos**. Un routage qui envoie
vers un chantier clos coûte une session entière.

## 5. Les deux pages

D'abord **l'artefact du chantier** — lire, réécrire, republier :

- `Artifact`, `action: "read"`, son `url` (la lecture est imposée : sans elle
  la republication est refusée) ;
- `ZONE:bilan` rendue visible — retire son `hidden` — avec la date, ce que le
  chantier a livré, ce qui a surpris ;
- `ZONE:blocage` remise en `hidden` ;
- les fiches abandonnées, s'il y en a, laissées **non faites** et dites comme
  telles ;
- republication : `file_path` local **et** `url`, pas de `favicon`,
  `label` : `clos`.

Puis la **feuille de route**, même séquence, son `url` est dans
`CHANTIER.md` :

- `ZONE:encours` remis à « aucun chantier ouvert » ;
- une ligne en tête de `ZONE:clos`, avec le lien vers l'artefact du chantier ;
- la ligne correspondante retirée de `ZONE:todo` ;
- la TODO reportée depuis le **fichier d'état** si elle a bougé — c'est le
  fichier qui fait foi, la page n'en est que le miroir ;
- `label` : `<chantier> clos`.

Si une publication échoue, dis-le en une ligne et continue : les quatre
écritures locales sont ce qui compte, les pages se rattrapent.

## Pour finir

Donne les deux liens, et dis la suite : `/clear`, puis `/vlp:chantier` pour ouvrir
le suivant.
