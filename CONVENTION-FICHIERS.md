# La gestion des fichiers — où vit quoi, et qui a le droit de l'ouvrir

La méthode des chantiers ne tient que si les fichiers autour d'elle tiennent.
Voici la convention complète, indépendante du langage et du projet.

## Les six familles, et rien d'autre

| Fichier | À la racine ? | Qui le lit | Longueur visée |
|---|---|---|---|
| `CLAUDE.md` | oui | **toute** session, en entier, en premier | 60 lignes |
| `CHANTIER.md` | oui | `/chantier` et `/tache`, en entier | 30 lignes |
| `<contexte>/00-INDEX.md` | non | seulement quand le routage de `CLAUDE.md` ne répond pas | 40 lignes |
| `<contexte>/08-etat.md` | non | reprise à froid, choix du prochain chantier | libre |
| `<contexte>/09-chantiers.md` | non | `/chantier` seulement — jamais `/tache` | 90 lignes |
| `<contexte>/<NN>-<chantier>.md` | non | `/tache`, **par plages**, jamais en entier | libre |
| `<contexte>/artefacts/*.html` | non | publié pour l'utilisateur ; relu par `/tache` à chaque fiche | 250 lignes |

Le dossier de contexte s'appelle `context AI/` par défaut. Son nom importe peu ;
ce qui compte est qu'il soit **un seul dossier**, à plat, numéroté.

## Les cinq règles

**1. Un fichier = un sujet.** Le voisin d'un fichier utile n'est pas utile ; il
n'est que du volume. Un fichier qui répond à deux questions se scinde.

**2. Chaque fichier s'ouvre sur une ligne « QUAND LIRE ».** Elle décrit la
*tâche* qui justifie l'ouverture, pas le contenu. Si elle ne décrit pas la
tâche en cours, le fichier n'est pas à ouvrir, même s'il a l'air proche.

**3. `CLAUDE.md` porte une table de routage « tâche → fichier ».** Elle remplace
la lecture de l'index dans presque tous les cas. L'index n'est que le filet.

**4. Ce qui s'ouvre se déclare le jour même.** Un nouveau fichier de contexte
prend, dans la même session : son numéro, sa ligne d'index, sa ligne de
routage. Un index qui ment coûte plus cher que le fichier lui-même.

**5. Un fichier de fiches clos ne se rejoue pas.** Il est marqué **clos** en
tête, sort de `CHANTIER.md` vers la table des clos, et ne sert plus qu'à relire
un socle d'API quand une fiche l'y renvoie.

Les artefacts font exception à « un fichier = un sujet » : ils ne sont pas du
contexte, ce sont des **vues**. Rien ne s'y trouve qui ne soit ailleurs, et une
session ne s'en sert jamais pour se renseigner — `ARTEFACTS.md` dit le reste.

## Numérotation

Un nombre à deux chiffres, attribué **dans l'ordre de création**, jamais
renuméroté : les journaux extérieurs et les vieux commits citent les numéros.
`00` est l'index. Les suffixes de lettre (`20a`, `20b`) servent à éclater un
fichier devenu trop gros sans toucher aux numéros voisins.

Les fichiers de chantier prennent un numéro comme les autres. Leur **préfixe de
fiche** — la lettre `R`, `N`, `U`… — est indépendant du numéro et ne se réemploie
jamais, même après clôture : `CHANTIER.md` garde la liste des lettres prises.
`/chantier` en **propose** une à l'étape 4, avec les lettres déjà prises ; c'est
l'utilisateur qui tranche, et une lettre dictée l'emporte. Le seul refus possible
est « déjà prise », et il doit dire par quel chantier.

## Ce qui ne va nulle part

- **Pas de résumé de ce que le code dit déjà.** Une table de symboles avec
  `fichier:ligne` vaut mieux qu'une paraphrase, et se vérifie.
- **Pas d'historique narratif.** Le journal des décisions prend une ligne par
  décision *imprévue*, datée. Le reste est dans git.
- **Pas de chiffre non mesuré.** Tant que la mesure n'existe pas, on écrit la
  mesure à faire, pas son résultat attendu.

## Le cycle de vie d'un chantier, vu depuis les fichiers

1. `/chantier` lit `<contexte>/09-chantiers.md` puis le fichier d'état.
2. Il écrit `<contexte>/<NN>-<chantier>.md`, publie
   `<contexte>/artefacts/<NN>-<chantier>.html`, et **quatre lignes** ailleurs :
   l'index, le routage de `CLAUDE.md`, « fichier de fiches courant » et
   « artefact du chantier » dans `CHANTIER.md`.
3. `/tache` ne touche qu'au fichier de fiches (une case cochée), à l'artefact
   du chantier (la même case, et la fiche suivante marquée en cours) et, si une
   décision imprévue est tombée, au fichier d'état (une ligne).
4. À la dernière case cochée : « clos » en tête du fichier de fiches, sa ligne
   passe dans la table des clos de `CHANTIER.md` avec l'URL de son artefact, le
   routage le dit, l'état reçoit sa ligne de bilan, l'artefact du chantier
   reçoit le sien, et la feuille de route repasse à « aucun chantier ouvert ».

## Ce qui ne part pas dans git

Le dossier de contexte — artefacts compris —, `CLAUDE.md` et `CHANTIER.md`
décrivent une manière de travailler, pas le produit. Beaucoup de projets préfèrent les garder hors du
dépôt. C'est un choix par projet — mais il se prend **une fois**, et
`.gitignore` doit alors les nommer tous les trois, pas deux sur trois.
