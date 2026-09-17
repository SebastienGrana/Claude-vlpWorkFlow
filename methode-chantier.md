> **QUAND LIRE** : on ouvre un nouveau chantier, on découpe un chantier en
> fiches, on se demande comment une fiche est faite, ou où vit quoi dans un
> projet équipé. Pas besoin de ce fichier pour *exécuter* une fiche :
> `/vlp:tache` est autoportante.

# Mener un chantier — la méthode qui économise le contexte

Un **chantier** est un lot de travail qui ne tient pas dans une séance. Mené
d'un seul tenant, il coûte cher pour une raison mécanique : une session relit
tout son passé à chaque tour, donc la fin d'un long chantier se paye au prix de
son début. La parade : **un chantier s'écrit une fois en fiches, puis chaque
fiche s'exécute dans sa propre session.**

## Deux règles qui valent partout

Elles sont écrites ici, et nulle part ailleurs : le reste du kit y renvoie.

- **Une règle vit à un seul endroit — un nombre aussi.** Ailleurs, on pointe ;
  on ne recopie jamais. Une doctrine recopiée existe en plusieurs exemplaires,
  et une correction n'en atteint aucun : c'est ainsi que le kit a divergé sur
  six copies sans qu'aucune alarme ne sonne. Un seuil vit dans
  `scripts/vlp.py`, qui avertit quand il est dépassé ; la doc dit « le seuil de
  `vlp.py` » et n'écrit pas le chiffre.
- **Les comptes bruts s'affichent à côté du verdict.** « OK », « plus court »,
  « moins cher » ne se croient pas seuls : on montre les nombres qui les
  fondent, avant et après. Un instrument muet rend son propre échec
  indiagnosticable.

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
derrière elle tout le contexte de la première. `/vlp:enchainer` tient la même
règle autrement — chaque fiche dans un sous-agent neuf, jusqu'au premier arrêt
— mais son chef relit tout son contexte à chaque appel : mesuré, l'ensemble
coûte plus cher en tokens que les fiches jouées à la main.

**3. Clôture.** Elle est décrite dans `cloture.md` à la racine du kit, que
`/vlp:tache`, `/vlp:enchainer` et `/vlp:chantier` lisent au moment de clore :
cinq écritures — l'en-tête **CLOS**, les quatre lignes de `CHANTIER.md`, le
bilan daté dans le fichier d'état, le routage de `CLAUDE.md`, et les deux pages
republiées. Un fichier de fiches clos ne se rejoue pas : il ne sert plus qu'à
relire un socle d'API quand une fiche l'y renvoie.

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

## Où vit quoi — les six familles, et rien d'autre

| Fichier | À la racine ? | Qui le lit | Longueur visée |
|---|---|---|---|
| `CLAUDE.md` | oui | **toute** session, en entier, en premier | 60 lignes |
| `CHANTIER.md` | oui | `/vlp:chantier`, `/vlp:tache` et `/vlp:enchainer`, en entier | 30 lignes |
| `<contexte>/00-INDEX.md` | non | seulement quand le routage de `CLAUDE.md` ne répond pas | 40 lignes |
| le **fichier d'état** | non | reprise à froid, choix du prochain chantier | libre |
| les **fichiers de fiches**, un par chantier | non | `/vlp:tache` et `/vlp:enchainer`, **par plages**, jamais en entier | libre |
| `<contexte>/artefacts/*.html` | non | publié pour l'utilisateur ; relu par `/vlp:tache` à chaque fiche, par `/vlp:enchainer` une fois par lancement | le seuil de `vlp.py` |

Le dossier de contexte s'appelle `context AI/` par défaut. Son nom importe peu ;
ce qui compte est qu'il soit **un seul dossier**, à plat, numéroté.

**Les numéros ne sont pas la convention — les libellés le sont.** L'état
s'appelle `08-etat.md` dans un projet et `10-etat.md` dans un autre. Ce qui ne
varie pas, ce sont les libellés en gras de `CHANTIER.md` — « **fichier
d'état** », « **méthode** », « **fichier de fiches courant** » — que les
commandes lisent tels quels : elles lisent la ligne, et la ligne dit le nom.

**Le moteur est dans le kit, les données sont dans le projet.** Ne descendent
jamais dans un projet : `skills/`, `agents/`, `hooks/`, `scripts/`, cette
méthode, `cloture.md`, `enchainement.md` et les gabarits de `templates/` —
instanciés, pas recopiés. Un projet équipé avant cette règle garde sa copie de
la méthode — sa ligne « méthode » la nomme ; on cesse seulement d'en fabriquer.

**Cinq règles de rangement :**

1. **Un fichier = un sujet.** Le voisin d'un fichier utile n'est pas utile ; il
   n'est que du volume. Un fichier qui répond à deux questions se scinde. Les
   artefacts y font exception : ce sont des **vues**, pas du contexte, et une
   session ne s'en sert jamais pour se renseigner.
2. **Chaque fichier s'ouvre sur une ligne « QUAND LIRE »**, qui décrit la
   *tâche* justifiant l'ouverture, pas le contenu.
3. **`CLAUDE.md` porte une table de routage « tâche → fichier ».** Elle remplace
   la lecture de l'index dans presque tous les cas ; l'index n'est que le filet.
4. **Ce qui s'ouvre se déclare le jour même** : numéro, ligne d'index, ligne de
   routage. Un index qui ment coûte plus cher que le fichier lui-même.
5. **Rien de ce qui ne sert pas** : pas de résumé de ce que le code dit déjà
   (une table `fichier:ligne` vaut mieux qu'une paraphrase), pas d'historique
   narratif — le journal prend une ligne par décision *imprévue*, datée ; le
   reste est dans git.

**Numérotation.** Un nombre à deux chiffres, attribué dans l'ordre de création,
jamais renuméroté : les journaux et les vieux commits citent les numéros. `00`
est l'index ; les suffixes `20a`, `20b` éclatent un fichier trop gros sans
toucher aux voisins. Le **préfixe de fiche** d'un chantier — `R`, `N`, `U`… —
est indépendant du numéro et ne se réemploie jamais : `CHANTIER.md` garde les
lettres prises. `/vlp:chantier` en propose une, l'utilisateur tranche ; le seul
refus possible est « déjà prise », en disant par quel chantier.

**Ce qui ne part pas dans git.** Le dossier de contexte — artefacts compris —,
`CLAUDE.md` et `CHANTIER.md` décrivent une manière de travailler, pas le
produit ; beaucoup de projets les gardent hors du dépôt. Le choix se prend
**une fois**, et `.gitignore` nomme alors les trois, pas deux sur trois.

## Le fichier de fiches

Un chantier = un fichier du dossier de contexte, numéroté comme les autres et
déclaré le jour même : l'index, le routage de `CLAUDE.md`, et les lignes
« fichier de fiches courant » et « artefact du chantier » de `CHANTIER.md`.

Il s'ouvre sur trois choses, et rien de plus :

- **L'état du chantier** en deux lignes : à quoi il sert, ce qui est fait.
- **Le socle commun** : les API, invariants et noms que *toutes* les fiches
  utilisent, dans une section délimitée que `/vlp:tache` extrait d'un appel. Ce
  qui est ici n'est pas répété dans les fiches ; au-delà du seuil de `vlp.py`,
  `valider` avertit.
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
**en silence** — et une extraction vide ressemble à une fiche vide. C'est pourquoi
le hook du plugin (`hooks/hooks.json`) valide un fichier de fiches à chaque
écriture par `Write` ou `Edit`, et rend l'écart aussitôt.

## Anatomie d'une fiche

Une fiche tient en **~20 lignes** ; au-delà du seuil de `vlp.py`, c'est deux
fiches, et `valider` avertit. Le squelette complet est dans
`<kit>/templates/context AI/fichier-de-fiches.md`.

Quatre exigences, apprises en cassant :

1. **Tout fichier à ouvrir est nommé dans la fiche.** Une fiche qui laisse
   chercher fait ouvrir trois fichiers au hasard — plus cher que le chantier.
2. **Aucun libellé ni chiffre inventé** : les libellés viennent de la plage de
   maquette citée ; tant qu'une mesure n'existe pas, la fiche demande la
   mesure, elle n'annonce pas son résultat.
3. **Un critère de fin observable**, sinon la fiche ne peut pas être cochée. Il
   affiche ses comptes bruts (voir « Deux règles qui valent partout »).
4. **Les fiches sont indépendantes autant que possible** ; les dépendances
   réelles sont écrites, pas devinées.

## Les deux formes de critère de fin

Elles ne se transportent pas d'un projet à l'autre.

- **Scriptable** — la session lance la commande et lit sa sortie. On ne demande
  pas à l'utilisateur ce que le code calcule déjà.
- **Visuel** — seul l'utilisateur voit le résultat (un jeu, une interface non
  pilotable). La fiche s'arrête et lui rend la main ; la session ne lit le log
  qu'**après** son retour, sinon elle lit l'ancienne version. Son titre porte
  alors la marque `**Critère de fin** (visuel)`, qu'un grep retrouve sans
  lire la fiche — c'est là que `/vlp:enchainer` s'arrête pour poser la question.

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
