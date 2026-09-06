> **QUAND LIRE** : on ouvre un nouveau chantier, on découpe un chantier en
> fiches, ou on se demande comment une fiche est faite. Pas besoin de ce
> fichier pour *exécuter* une fiche : `/vlp:tache` est autoportante.

# Mener un chantier — la méthode qui économise le contexte

Un **chantier** est un lot de travail qui ne tient pas dans une séance. Mené
d'un seul tenant, il coûte cher pour une raison mécanique : une session relit
tout son passé à chaque tour, donc la fin d'un long chantier se paye au prix de
son début. La parade : **un chantier s'écrit une fois en fiches, puis chaque
fiche s'exécute dans sa propre session.**

## Les trois temps

**1. Cadrage — une session qui ne code pas.** C'est par là qu'une séance
commence. `/vlp:chantier` tout court **propose les chantiers possibles** (tirés du
fichier d'état) avec un avis sur lequel faire en premier ; `/vlp:chantier <nom>`
saute la proposition et cadre directement. Ensuite, dans les deux cas :
questionnaire sur le résultat visible, la frontière et les inconnues,
proposition du découpage, écriture du fichier de fiches, mise à jour de
`CHANTIER.md`, et la main rendue. Le coût du cadrage est payé **une fois** ; il
ne se repaye pas à chaque fiche.

**2. Exécution — une fiche, une session.** `/vlp:tache X1`, puis `/clear`, puis
`/vlp:tache X2`. Jamais deux fiches dans la même session : la seconde traînerait
derrière elle tout le contexte de la première.

**3. Clôture.** Elle est décrite **à un seul endroit**, `cloture.md` à la racine
du kit, que `/vlp:tache` et `/vlp:chantier` lisent au moment de clore : cinq
écritures — l'en-tête **CLOS**, les quatre lignes de `CHANTIER.md`, le bilan
daté dans le fichier d'état, le routage de `CLAUDE.md`, et les deux pages
republiées. Un fichier de fiches clos ne se rejoue pas.

Un chantier peut aussi se clore **inachevé** : les fiches non jouées y sont
dites **abandonnées**, jamais cochées. Mieux vaut un chantier clos honnête
qu'un chantier ouvert que personne ne reprendra.

**Les pages publiées, en marge des trois temps.** Le projet a une **feuille de
route** (la TODO ordonnée, le chantier en cours, les clos) et chaque chantier a
sa **page de fiches**, marquée au fur et à mesure — faite, en cours, bloquée.
Seule la seconde vit au rythme des fiches : la feuille de route ne bouge qu'à
l'ouverture et à la clôture, pour que `/vlp:tache` n'ait qu'une page à relire.
Les commandes les tiennent seules ; leurs URL sont dans `CHANTIER.md`. Ce sont
des **vues dérivées** : la page de chantier n'est pas retouchée à la main, elle
est **régénérée** depuis le fichier de fiches à chaque fiche finie. En cas de
désaccord, **le fichier a raison** — c'est le `grep` des cases cochées qui
tranche, pas la mémoire de la session.

`/vlp:check` vérifie cet accord sans rien écrire, quand on a un doute.

## Le fichier de fiches

Un chantier = un fichier du dossier de contexte, numéroté comme les autres et
déclaré dans l'index et dans la table de `CLAUDE.md` **le jour même**.

Il s'ouvre sur trois choses, et rien de plus :

- **L'état du chantier** en deux lignes : à quoi il sert, ce qui est fait.
- **Le socle commun** : les API, invariants et noms que *toutes* les fiches
  utilisent, dans une section délimitée que `/vlp:tache` lit d'un seul `sed`. Ce
  qui est ici n'est pas répété dans les fiches.
- **L'ordre des fiches** : la liste, et qui dépend de qui.

Puis les fiches, séparées par `---`, **chacune encadrée de ses marqueurs** :

```
<!-- FICHE:D1 -->
## D1 [ ] — <titre>
…
<!-- /FICHE -->
```

Les deux titres `## Le socle commun` et `## L'ordre des fiches` se recopient à
l'identique, et les marqueurs ne s'omettent pas : `/vlp:tache` extrait le socle et
la fiche par eux. Un titre reformulé ou un marqueur manquant casse l'extraction
**en silence** — et une extraction vide ressemble à une fiche vide.

## Anatomie d'une fiche

Une fiche tient en **~20 lignes**. Si elle en fait 50, c'est deux fiches.
Le squelette complet est dans `<kit>/templates/context AI/fichier-de-fiches.md`.

Quatre exigences, apprises en cassant :

1. **Tout fichier à ouvrir est nommé dans la fiche.** Une fiche qui laisse
   chercher fait ouvrir trois fichiers au hasard — plus cher que le chantier.
2. **Aucun libellé ni chiffre inventé** : les libellés viennent de la plage de
   maquette citée ; tant qu'une mesure n'existe pas, la fiche demande la
   mesure, elle n'annonce pas son résultat.
3. **Un critère de fin observable**, sinon la fiche ne peut pas être cochée. Il
   affiche ses comptes bruts : un instrument muet rend son propre échec
   indiagnosticable.
4. **Les fiches sont indépendantes autant que possible** ; les dépendances
   réelles sont écrites, pas devinées.

## Les deux formes de critère de fin

Elles ne se transportent pas d'un projet à l'autre.

- **Scriptable** — la session lance la commande et lit sa sortie. On ne demande
  pas à l'utilisateur ce que le code calcule déjà.
- **Visuel** — seul l'utilisateur voit le résultat (un jeu, une interface non
  pilotable). La fiche s'arrête et lui rend la main ; la session ne lit le log
  qu'**après** son retour, sinon elle lit l'ancienne version.

## Ce que `/vlp:tache` garantit, et qu'il ne faut pas défaire

`/vlp:tache` est **autoportante** : elle n'ouvre que ce qu'elle nomme, jamais
`CLAUDE.md`, jamais l'index, jamais un fichier de fiches en entier. Elle lit la
sortie **elle-même** au lieu de la demander, s'arrête à deux tentatives, et
finit par le critère de fin recopié.

Quand elle s'arrête ainsi, elle écrit un bloc « **Tentatives** » **dans la
fiche**, sous son titre. C'est ce qui rend la reprise utile : la session
suivante le lit à l'étape 1, avant d'écrire, et cherche autre chose au lieu de
rejouer les mêmes deux essais. Le bloc se solde à la fiche cochée.

`CHANTIER.md`, à la racine, est la seule chose à mettre à jour quand un
chantier s'ouvre ou se clôt. Un fichier qui ment envoie la session dans un
chantier clos.
