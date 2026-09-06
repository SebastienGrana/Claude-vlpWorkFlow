# Claude-vlpWorkflow — mener un gros chantier sans saturer le contexte

Un kit portable — **un seul exemplaire, à côté des projets**, jamais recopié
dedans. Il apporte cinq commandes, les gabarits de fichiers, et la convention
qui les tient ensemble.

Le partage tient en une ligne : **le kit porte le moteur, le projet porte ses
données.** La méthode, la clôture et les gabarits restent ici et servent tous
les projets à la fois ; un projet ne garde que son `CHANTIER.md`, son état, ses
fichiers de fiches et ses pages publiées.

## Le problème qu'il résout

Une session d'assistant **relit tout son passé à chaque tour**. Un lot de
travail mené d'un seul tenant se paye donc de plus en plus cher à mesure qu'il
avance : la dernière heure coûte le prix de toutes les précédentes. Ce n'est
pas un problème de volume horaire, mais de **densité de contexte**.

La parade tient en une phrase :

> **Un chantier s'écrit une fois en fiches, puis chaque fiche s'exécute dans sa
> propre session.**

Le cadrage — comprendre, découper, nommer les fichiers à ouvrir — est payé
**une fois**. Chaque fiche démarre ensuite à froid, avec vingt lignes
d'instructions et trois fichiers nommés, au lieu de traîner tout l'historique.

## Les trois temps

**1. Cadrage.** `/chantier` — une session qui **ne code pas**. Elle propose les
chantiers possibles avec un avis, questionne le résultat visible / la frontière
/ les inconnues, propose le découpage, écrit le fichier de fiches, puis rend la
main.

**2. Exécution.** `/tache R1`, `/clear`, `/tache R2`, `/clear`… Une fiche par
session, jamais deux. La commande est **autoportante** : elle n'ouvre que ce
qu'elle nomme, lit elle-même la sortie de vérification, s'arrête à deux
tentatives, et finit par le critère de fin recopié.

**3. Clôture.** Dernière case cochée, fichier marqué clos, `CHANTIER.md` mis à
jour, une ligne dans l'état. Un chantier clos ne se rejoue pas.

Et en parallèle, sans rien coûter aux sessions : **deux pages publiées**. Une
feuille de route par projet, un artefact par chantier, tenus à jour à chaque
fiche — pour savoir où l'on en est depuis un téléphone, sans ouvrir de session.
Ils ne sont jamais la vérité : les fichiers du projet le restent.

## Ce qu'il y a dans le dossier

```
commands/                  LE MOTEUR — copié une fois dans ~/.claude/commands/
  vlp-init.md              /vlp-init  — équiper un projet, en sept questions
  chantier.md              /chantier  — cadrer un chantier en fiches
  tache.md                 /tache     — exécuter une fiche, une seule
  vlp-sync.md              /vlp-sync  — repousser les commandes depuis le kit
  vlp-check.md             /vlp-check — vérifier un projet, sans rien écrire
methode-chantier.md        LA DOCTRINE — lue depuis le kit, jamais recopiée
cloture.md                 les cinq écritures d'une clôture, décrites une fois
CONVENTION-FICHIERS.md     où vit quoi, et qui a le droit de l'ouvrir
ARTEFACTS.md               les deux pages publiées : nommage, URL, budget
INSTALLATION.md            la mise en place
templates/                 LES GABARITS — instanciés dans un projet
  CHANTIER.md              la carte à la racine du projet : la seule table à tenir
  CLAUDE.md                l'entrée du projet : identité, état, règles, routage
  artefact-feuille-de-route.html  la page publiable du projet : TODO, en cours, clos
  artefact-chantier.html   la page publiable d'un chantier : les fiches et leur état
  context AI/
    fichier-de-fiches.md   le squelette d'un chantier découpé
    00-INDEX.md            l'index du dossier de contexte
    NN-etat.md             l'état daté, la TODO ordonnée, le journal des décisions
exemples/
  CHANTIER-mapdecorator.md vérification visuelle (un jeu : l'utilisateur regarde)
  CHANTIER-cairn.md        vérification scriptable (la session lance et lit)
  fichier-de-fiches-cairn.md  extrait réel : socle, ordre, une fiche entière
```

## Pas de préfixe si le dossier suffit

Un projet équipé porte un `CHANTIER.md` **à sa racine**. Les commandes le
cherchent en remontant depuis le dossier courant, puis d'un cran plus bas :

- session ouverte **dans le projet** → `/tache R3`, rien à préciser ;
- session ouverte **dans un workspace** avec un seul projet équipé → pareil ;
- workspace avec plusieurs projets équipés → elles demandent lequel, ou
  acceptent l'alias : `/tache cairn N2` ;
- aucun `CHANTIER.md` → elles renvoient vers `/vlp-init` au lieu d'improviser.

C'est aussi ce qui remplace la table centrale des versions précédentes : l'état
d'un projet vit **dans le projet**, et rien n'est à tenir à jour ailleurs.

## Les quatre exigences d'une fiche

Apprises en cassant, elles font toute la différence entre une fiche qui tient
en une séance et une qui déborde :

1. **Tout fichier à ouvrir est nommé dans la fiche.** Une fiche qui laisse
   chercher fait ouvrir trois fichiers au hasard — plus cher que le chantier.
2. **Aucun libellé ni chiffre inventé.** Les libellés viennent d'une plage de
   maquette citée ; une mesure qui n'existe pas se demande, elle ne s'annonce
   pas.
3. **Un critère de fin observable**, sinon la fiche ne peut pas être cochée —
   et il affiche ses comptes bruts à côté de son verdict.
4. **Les fiches sont indépendantes autant que possible** ; les dépendances
   réelles sont écrites, pas devinées.

Une fiche tient en **~20 lignes**. Si elle en fait 50, c'est deux fiches.

## Les deux pages publiées

Un projet équipé publie une **feuille de route** — la TODO ordonnée, le
chantier en cours, la table des clos — et, par chantier, une page qui montre
**les fiches et où l'on en est**, jusqu'à son bilan de clôture.

- `/vlp-init` pose et publie la feuille de route ;
- `/chantier` publie l'artefact du chantier qu'il vient de cadrer, et bascule
  la feuille de route sur « en cours » ;
- `/tache` coche la fiche sur la **page du chantier**, marque la suivante, y
  porte les décisions imprévues — et signale un **arrêt sur blocage** quand il
  abandonne après deux tentatives. Il ne touche pas à la feuille de route : sa
  session est la plus serrée des trois, et une seconde page relue à chaque
  fiche y coûterait le prix de la fiche ;
- à la dernière fiche, le chantier passe en « clos » des deux côtés.

Les URL vivent dans `CHANTIER.md` ; elles ne changent jamais. Les fils de
commentaires d'une page sont le canal de retour entre deux sessions :
`/chantier` les lit à la reprise, `/tache` seulement si on le lui demande.
Détail complet dans `ARTEFACTS.md`.

## Par où commencer

`INSTALLATION.md`, puis `/vlp-init` dans le projet. Ensuite `/chantier`.

Et une règle à retenir avant toutes les autres : **on modifie le kit, jamais sa
copie installée.** `/vlp-sync` repousse les commandes ; une retouche faite
directement dans `~/.claude/commands/` sera écrasée sans prévenir, et une copie
du kit posée dans un projet ne sera plus jamais mise à jour. C'est comme ça que
six exemplaires ont divergé de cinq cents lignes.
