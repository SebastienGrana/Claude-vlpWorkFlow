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

## Les règles qui valent partout

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
- **Une ligne de mesure nomme les quantités qu'elle compare.** Un compte juste
  ne prouve rien s'il ne dit pas de quoi il est le compte, et c'est ainsi qu'on
  publie une cause qu'on n'a pas mesurée. Mesuré : un chantier a conclu « la
  cause dominante est l'autosave périmée » à partir de « 35 autosaves seules /
  10 ghosts » — un compte de **quels fichiers existent sur le disque**, c'est-
  à-dire un fait sur l'**outillage**. Les deux nombres étaient exacts ; le pont
  entre eux n'existait pas. Rejoué en croisant la vraie variable, la source
  **ne triait pas** (19 / 7, la proportion du corpus) et la cause était
  ailleurs. ⚠️ Le piège n'est pas l'erreur de calcul — il n'y en avait pas —
  c'est la **mauvaise quantité comparée**, qu'aucune relecture de chiffres
  n'attrape. Écrire, dans la ligne même : *ce compte compare X à Y*.
- **Une hypothèse vraie sur un cas se revérifie sur tous.** Un cas qui colle au token près
  ne dit rien des autres. Mesuré (chantier `APC`) : « l'écart est fait des tours d'après
  `clore` » tenait au token près pour `ESD` ; sur les 19 clos à expliquer, il tenait en entier
  pour 5, en partie pour 14. Avant de corriger sur la foi d'un cas, la même mesure passe sur
  tout le lot, et les trois comptes (en entier, en partie, pas du tout) s'écrivent.
- **Un énoncé renversé se garde, marqué.** On ne remplace pas un chiffre publié
  en silence : le paragraphe périmé reste, avec un renvoi vers ce qui le
  renverse et **par quoi**. Quelqu'un qui grep tombe sur l'ancien texte avant
  le nouveau ; sans marqueur il le lit comme vrai.
- **Un résultat inchangé ne prouve pas qu'on a mesuré la même chose.** Un
  chiffre qui ne bouge pas rassure, et c'est exactement pour cela qu'il faut
  regarder derrière lui. Trois cas, tous trois rencontrés le même jour sur un
  seul chantier : un **seuil** revalidé à l'identique alors que ce qu'il
  découpe avait changé de 7 % ; un chiffre publié qui bouge de 0,2 point parce
  que **deux correctifs le montaient pendant qu'un troisième le descendait** ;
  et une case qui perd 10 % sans qu'**aucune règle** n'ait changé, seulement
  parce qu'on a cessé de compter deux fois la même donnée. Le remède est
  toujours le même : une table **avant / après par cause**, en comptes bruts,
  jamais un verdict net unique. Un chantier qui joue plusieurs correctifs
  d'un coup doit pouvoir dire lequel explique quoi — sinon il a corrigé sans
  savoir quoi.
- **Un arrondi n'est pas une tolérance.** Grouper des mesures par une clé
  arrondie coupe à une frontière **arbitraire** : deux valeurs voisines tombent
  de part et d'autre, deux valeurs éloignées tombent ensemble. Mesuré : une
  carte s'est retrouvée seule dans son groupe pour **3 cm**, quand ses cinq
  sœurs portaient le même décalage à un flottement physique près. Quand ce
  qu'on groupe est une **quantité continue**, la clé est une **distance sous
  tolérance**, pas un arrondi — et la tolérance se justifie par ce qui fait
  flotter la mesure, jamais par le chiffre rond le plus proche.
- **Une norme n'est pas un vecteur, et deux quantités voisines ne sont pas la
  même.** Résumer un vecteur par sa longueur perd sa direction, donc fait
  coïncider ce qui n'a rien à voir : une mesure a innocenté une carte à tort
  parce qu'elle partageait la **norme** de ses voisines, avec **10,9 m**
  d'écart sur une composante. Avant de conclure d'une coïncidence de nombres,
  vérifier qu'on compare bien la même **grandeur**, et la comparer **entière**.
  Le corollaire vaut aussi à l'écriture : deux quantités voisines — la distance
  à une ligne entière, et la distance à son début — portent des noms distincts,
  sinon un lecteur les échange sans le voir.
- **Un commentaire périmé coûte plus cher qu'un chiffre périmé.** Un chiffre
  faux se remarque — il détonne, on le recoupe. Un commentaire faux *oriente*,
  et il oriente en silence : il décrit un code qui n'existe plus, et le lecteur
  suivant part chercher le coupable là où on le lui montre. Mesuré : sur un même
  chantier, **quatre angles d'analyse indépendants ont accusé le même innocent
  le même jour**, tous les quatre conduits par deux commentaires périmés —
  alors qu'une **troisième ligne du même fichier** énonçait déjà le fait juste.
  Quand une relecture change une règle, le commentaire qui la décrit fait partie
  de la règle : il se corrige dans le même geste, ou il devient un piège daté.
- **Un seuil calé sur une distribution qui ne pouvait pas répondre reste
  arbitraire, même quand il tombe juste.** Avant de lire un histogramme pour
  choisir une borne, vérifier que la population mesurée peut *contenir* des
  valeurs des deux côtés de cette borne. Mesuré : une largeur de bande a été
  choisie sur la distribution des écarts manqués, alors que par construction
  cette distribution ne pouvait contenir **aucune** valeur sous le seuil
  envisagé. Le chiffre retenu est resté le bon, mais pour une autre raison que
  celle écrite — et la raison écrite est ce que la session suivante relira.
- **Un instrument qui *montre* peut réfuter ce que la mesure *confortait*.**
  Une sonde qui rend un taux dit *quelle* chose est douteuse, jamais *pourquoi*,
  et un taux se lit trop facilement comme un taux d'échec. Une vue par cas —
  une page, un dessin, un rendu — fait apparaître ce qu'aucune colonne ne
  portait : qu'une partie de l'écart n'est pas un défaut de l'instrument mais la
  description exacte de la réalité. **Le meilleur résultat d'un chantier de vue
  peut être négatif** : *aucune règle n'est fausse*. Ce n'est pas un chantier
  raté, c'est une hypothèse coûteuse écartée pour de bon.
- **Un chantier se cite par son code, jamais par son rang** — décision de
  l'utilisateur, prise sur un compte. Un rang bouge à chaque re-tri, et chaque
  re-tri rend faux tous les renvois qui le citent : un tri a rendu faux
  **21 renvois vivants dans cinq fichiers** d'un coup, et l'audit revenait à
  chaque fois. Donner à chaque chantier un code court et stable (`POR`, `LIG`,
  `GBX`), garder le `#` pour le seul tri, et écrire la correspondance
  ancien rang → code une fois, en tête du fichier qui les décrit.
- **Une conclusion recopiée d'une table à l'autre se dégrade en silence.** Un
  chiffre faux détonne, on le recoupe ; un **énoncé** faux, non — il a la bonne
  forme, et rien dans le texte ne dit qu'il compare autre chose que ce qu'il
  annonce. Mesuré : une table de douze énoncés republiée sans être rejouée
  écrivait **deux fois la même quantité** dans ses deux premières lignes,
  testait **un autre énoncé que le sien** dans deux autres, portait les chiffres
  d'après dans sa colonne d'avant, et annonçait en prose **quatre**
  renversements quand sa propre table en cochait **cinq** — dont un qui, rejoué,
  **tenait**. Quatre défauts, aucune alarme, et la conclusion fausse a servi de
  socle au chantier suivant. La parade tient en deux gestes : **chaque ligne
  nomme les quantités qu'elle compare**, jamais deux nombres nus ; et un
  **script re-dérive** le verdict depuis les nombres écrits, avant publication.
  Un verdict qu'aucune machine ne recalcule n'est qu'une phrase.
- **Une fiche se paie jusqu'à ce qu'elle soit faite — sa reprise comprise.** Un
  statut `FAITE` n'est pas une fiche faite : une case restée vide, et le travail
  continue hors de la fiche. Mesuré : une fiche enchaînée a coûté 1,53 $ à son
  commit ; sa reprise à la main — cocher, journal, page — 0,55 $ de plus, que
  `vlp.py cout`, qui coupe aux commits de fiche, rangeait dans la fiche
  **suivante**. Le vrai prix, 2,08 $, n'était écrit nulle part, et la suivante
  paraissait plus chère qu'elle n'était. Une reprise se mesure sur la plage de
  ses propres commits, et s'ajoute à la fiche qu'elle termine.
- **Une définition d'agent se charge au démarrage de la session — pas à la
  volée.** Mesurer l'effet d'un changement dans `agents/*.md` sur une session
  déjà ouverte mesure l'ancienne définition. Mesuré : une phrase ajoutée à
  `agents/fiche.md` (chantier `GLO`) a été jugée « sans effet » sur une session
  qui avait démarré 21 minutes **avant** le commit, sans `/reload-plugins`
  (chantier `FOR`). Rejouée après relance de l'app, la même phrase changeait
  nettement la mesure. Avant de mesurer la forme d'un sous-agent après un
  changement d'agent : relancer l'app, ou au moins vérifier que la session
  parente a démarré après le commit. Un **script de hook**, lui, est relu à chaque
  appel : le gardien changé a jugé en vrai sans relance (chantier `JUG`).
- **Un filtre qui se trompe se change sur le vrai corpus, règles candidates côte à
  côte.** La règle intuitive n'est pas la bonne. Mesuré (chantier `JUG`) sur 29 vrais
  sous-agents : « après le dernier `---` » ne changeait rien — aucun message n'en
  portait — et « les deux dernières lignes » laissait passer 3 vraies fautes ; seule
  « le mot ouvre une ligne » retirait les 2 faux renvois sans rien rater. La règle
  devient un paramètre, chaque candidate se mesure, l'utilisateur retient ; l'ancienne
  reste rejouable (`--regle tout`), et les chiffres qu'elle a produits restent, marqués.
- **La TODO ne grossit pas sans deux oui de l'utilisateur** — décision de
  l'utilisateur, le 2026-09-25, contre le *scope creep*. Chaque chantier laisse
  des restes ; versés tels quels, ils ouvrent du travail que personne n'a choisi.
  Mesuré le 2026-09-25 dans `context AI/08-etat.md` : des entrées 31 à 68, soit
  38, le kit en a créé 32 de lui-même (clôtures, cadrages, une fiche), 2 sont
  nées d'une demande de l'utilisateur, 4 sans origine notée ; 21 lignes restent
  ouvertes. D'où :
  - **Ce qu'on repère en passant ne se fait pas, et ne s'écrit pas seul dans la
    TODO.** Une fiche le signale dans son compte rendu, sans plus.
  - **Premier oui — l'idée.** Une question à elle seule, précédée de sa
    justification : **pourquoi elle fait grossir le périmètre** (quel travail
    neuf elle ouvre, que le chantier ne promettait pas), son coût estimé, la TODO
    avant → après en lignes ouvertes. Trois réponses : verser, fondre dans une
    entrée existante qu'on nomme, abandonner — abandonner est une réponse normale.
  - **Deuxième oui — la ligne écrite.** Relue par l'utilisateur, puis confirmée
    avant son commit : une ligne écrite dit souvent plus que l'idée acceptée.
  - Une case cochée dans un menu n'est pas un oui, pas plus que pour le push
    (`cloture.md`). Retirer une entrée ou en fondre deux ne fait pas grossir la
    TODO : cette règle ne s'y applique pas.

## Les trois temps

**1. Cadrage — une session qui ne code pas.** C'est par là qu'une séance
commence. `/vlp:chantier` tout court **propose les chantiers possibles** (tirés du
fichier d'état) avec un avis sur lequel faire en premier ; `/vlp:chantier <nom>`
saute la proposition et cadre directement. Ensuite, dans les deux cas :
questionnaire sur le résultat visible, la frontière et les inconnues,
proposition du découpage, écriture du fichier de fiches, mise à jour de
`CHANTIER.md`, et la main rendue. Le coût du cadrage est payé **une fois** ; il
ne se repaye pas à chaque fiche.
Avant de promettre un chiffre de la TODO, le cadrage vérifie que les cas visés
passent par le code qu'on va changer : `ESS` visait 11 clos, 9 étaient en
`DÉCOUPE aucune`, hors du chemin modifié (journal `ESS4` du fichier d'état).

**2. Exécution — une fiche, une session.** `/vlp:tache X1`, puis `/clear`, puis
`/vlp:tache X2`. Jamais deux fiches dans la même session : la seconde traînerait
derrière elle tout le contexte de la première. `/vlp:enchainer` tient la même
règle autrement — chaque fiche dans un sous-agent neuf, jusqu'au premier arrêt,
par la skill forkée `vlp:jouer` : le chef ne lit ni socle ni fiche, un appel par
fiche (mesures au journal du fichier d'état du kit, chantier N).

**3. Clôture.** Elle est décrite dans `cloture.md` à la racine du kit, que
`/vlp:tache`, `/vlp:enchainer` et `/vlp:chantier` lisent au moment de clore :
le bilan daté dans le fichier d'état, puis `vlp.py clore` pour tout ce qui s'en
déduit (`CLOS`, `CHANTIER.md`, index, `CLAUDE.md`, pages locales), et les deux
pages republiées. Un fichier de fiches clos ne se rejoue pas : il ne sert plus qu'à
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

## Git — un commit par fiche, un push par chantier

**Une fiche cochée, un commit**, aussitôt et **sans demander** : message
`<PRÉFIXE><n> : <titre de la fiche>`. Un commit local se défait ; un commit par
fiche rend chaque pas annulable seul, et une fiche qui a mal tourné se reprend
par un `git revert` au lieu d'une reconstitution à la main.

**Un push à la clôture seulement, et jamais sans confirmation** : il publie, et
ne se reprend pas. `cloture.md` le porte.

Le sous-agent de `/vlp:enchainer` ne commite pas — il n'a ni le contexte ni le
droit : c'est le chef qui commite, après chaque `FAITE` accepté à la relecture
(`enchainement.md`, « Relecture »).

## Où vit quoi — les six familles, et rien d'autre

| Fichier | À la racine ? | Qui le lit | Longueur visée |
|---|---|---|---|
| `CLAUDE.md` | oui | **toute** session, en entier, en premier | le seuil de `vlp.py` |
| `CHANTIER.md` | oui | `/vlp:chantier`, `/vlp:tache` et `/vlp:enchainer`, en entier | le seuil de `vlp.py` |
| `<contexte>/00-INDEX.md` | non | seulement quand le routage de `CLAUDE.md` ne répond pas | le seuil de `vlp.py` |
| le **fichier d'état** | non | reprise à froid ; le choix du prochain chantier n'en lit que la TODO, par la carte | libre |
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
toucher aux voisins. Le **préfixe de fiche** d'un chantier — `RNV`, `PRJ`, `CAR`… —
est indépendant du numéro et ne se réemploie jamais : `CHANTIER.md` garde les
préfixes pris. `/vlp:chantier` en propose un, l'utilisateur tranche ; le seul
refus possible est « déjà pris », en disant par quel chantier.

**Trois lettres, depuis le 2026-09-17.** Un préfixe s'écrit en trois majuscules
— une abréviation du sujet, pas la suivante de l'alphabet. Les chantiers d'avant
gardent leur lettre unique et restent lisibles : `vlp.py` accepte une à trois
majuscules. L'alphabet à une lettre avait été épuisé au 26e chantier, et aucun
27e n'aurait pu s'ouvrir.

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
   affiche ses comptes bruts (voir « Les règles qui valent partout »). Pour du
   code, il nomme le test, l'appel, la valeur attendue, et **le mutant** — le
   code cassé exprès que ce test doit faire tomber : « les tests passent » ne
   prouve rien, un test creux passe aussi (`FIN1`, puis `FIN2` alors que son
   test était nommé avec ses valeurs, 2026-09-24). Un critère joué dans un
   clone y copie d'abord le fichier modifié : un clone part du dernier commit,
   et sans la copie le sous-agent commite pour l'y faire entrer (`VAL1`). Un
   critère qui prouve un juge — relecteur, eval — écrit son attendu selon les
   règles de ce juge, et le juge ne voit rien qui raconte la suite : un attendu
   contraire à la règle, ou un juge qui a lu la réponse, ne prouvent rien (`REV4`).
   Un test bâtit son propre projet dans un dossier temporaire : lire le vrai
   dépôt ou les transcripts de la machine le fait casser dès qu'une fiche
   suivante écrit, et échouer chez un autre membre du groupe (`ESD2`, refusée à
   la relecture pour ça).
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
