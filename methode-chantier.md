> **QUAND LIRE** : on ouvre un nouveau chantier, on découpe un chantier en
> fiches, on se demande comment une fiche est faite, ou où vit quoi dans un
> projet équipé — ou on écrit du code, une commande ou de la doctrine du kit.
> Pas besoin de ce fichier pour *exécuter* une fiche : `/vlp:tache` est autoportante.

# Mener un chantier — la méthode qui économise le contexte

Un **chantier** est un lot de travail qui ne tient pas dans une séance. Mené
d'un seul tenant, il coûte cher pour une raison mécanique : une session relit
tout son passé à chaque tour, donc la fin d'un long chantier se paye au prix de
son début. La parade : **un chantier s'écrit une fois en fiches, puis chaque
fiche s'exécute dans sa propre session.**

**Sommaire** : Les règles qui valent partout · Les trois temps · Git — un commit par
fiche, un push par chantier · Où vit quoi · Le fichier de fiches · Anatomie d'une fiche ·
Les deux formes de critère de fin · Ce que `/vlp:tache` garantit · Coder dans le kit.

## Les règles qui valent partout

Elles sont écrites ici, et nulle part ailleurs : le reste du kit y renvoie. Le récit
mesuré qui a fait naître une règle — sa preuve — vit dans `lecons-mesure.md`, sous son
titre (`MET6`, 2026-10-07).

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
  publie une cause qu'on n'a pas mesurée. ⚠️ Le piège n'est pas l'erreur de
  calcul, c'est la **mauvaise quantité comparée**, qu'aucune relecture de
  chiffres n'attrape. Écrire, dans la ligne même : « ce compte compare X à Y ».
  Trois cas du même piège :
  - **Une conclusion recopiée d'une table à l'autre se dégrade en silence.** Un
    chiffre faux détonne, on le recoupe ; un **énoncé** faux, non — il a la bonne
    forme, et rien dans le texte ne dit qu'il compare autre chose que ce qu'il
    annonce. La parade tient en deux gestes : chaque ligne nomme ses quantités,
    jamais deux nombres nus (la règle ci-dessus) ; et un **script re-dérive** le
    verdict depuis les nombres écrits, avant publication. Un verdict qu'aucune machine ne recalcule
    n'est qu'une phrase.
  - **Un instrument qui montre peut réfuter ce que la mesure confortait.** Une
    sonde qui rend un taux dit quelle chose est douteuse, jamais pourquoi, et un
    taux se lit trop facilement comme un taux d'échec. Une vue par cas — une page,
    un dessin, un rendu — fait apparaître ce qu'aucune colonne ne portait : qu'une
    partie de l'écart n'est pas un défaut de l'instrument mais la description
    exacte de la réalité. **Le meilleur résultat d'un chantier de vue peut être
    négatif** : « aucune règle n'est fausse ». Ce n'est pas un chantier raté,
    c'est une hypothèse coûteuse écartée pour de bon.
  - **Prouver qu'un ancien chiffre a disparu demande la liste de ses valeurs, pas
    le motif qui les a trouvées.** Un motif trouve tous les nombres, anciens et
    nouveaux, et ne dit pas lesquels devaient partir. La fiche qui inventorie les
    chiffres à republier écrit donc aussi la **liste des anciennes valeurs**, dans
    chaque format où les pages les écrivent (`1,234.5`, `1 234,5`) ; la fiche qui
    republie la passe au grep et nomme chaque ligne qui reste — historique datée,
    ou faux positif.
- **Une hypothèse vraie sur un cas se revérifie sur tous.** Un cas qui colle au
  token près ne dit rien des autres. Avant de corriger sur la foi d'un cas, la
  même mesure passe sur tout le lot, et les trois comptes (en entier, en partie,
  pas du tout) s'écrivent.
  - **Un filtre qui se trompe se change sur le vrai corpus, règles candidates côte
    à côte.** La règle intuitive n'est pas la bonne. La règle devient un
    paramètre, chaque candidate se mesure, l'utilisateur retient ; l'ancienne
    reste rejouable (`--regle tout`), et les chiffres qu'elle a produits restent,
    marqués.
- **Un énoncé renversé se garde, marqué.** On ne remplace pas un chiffre publié
  en silence : le paragraphe périmé reste, avec un renvoi vers ce qui le
  renverse et **par quoi**. Quelqu'un qui grep tombe sur l'ancien texte avant
  le nouveau ; sans marqueur il le lit comme vrai.
- Leçon partie dans `lecons-mesure.md` : « Un résultat inchangé ne prouve pas… ».
- Leçon partie dans `lecons-mesure.md` : « Un arrondi n'est pas une tolérance ».
- Leçon partie dans `lecons-mesure.md` : « Une norme n'est pas un vecteur… ».
- **Un commentaire périmé coûte plus cher qu'un chiffre périmé.** Un chiffre
  faux se remarque — il détonne, on le recoupe. Un commentaire faux oriente, et
  il oriente en silence : il décrit un code qui n'existe plus, et le lecteur
  suivant part chercher le coupable là où on le lui montre. Quand une relecture
  change une règle, le commentaire qui la décrit fait partie de la règle : il se
  corrige dans le même geste, ou il devient un piège daté.
- **Un seuil calé sur une distribution qui ne pouvait pas répondre reste
  arbitraire, même quand il tombe juste.** Avant de lire un histogramme pour
  choisir une borne, vérifier que la population mesurée peut contenir des
  valeurs des deux côtés de cette borne : la raison écrite est ce que la session
  suivante relira.
- **Un chantier se cite par son code, jamais par son rang** — décision de
  l'utilisateur, prise sur un compte. Un rang bouge à chaque re-tri, et chaque
  re-tri rend faux tous les renvois qui le citent. Donner à chaque chantier un
  code court et stable (`POR`, `LIG`, `GBX`), garder le `#` pour le seul tri, et
  écrire la correspondance ancien rang → code une fois, en tête du fichier qui
  les décrit.
- **Une fiche se paie jusqu'à ce qu'elle soit faite — sa reprise comprise.** Un
  statut `FAITE` n'est pas une fiche faite : une case restée vide, et le travail
  continue hors de la fiche. Une reprise se mesure sur la plage de ses propres
  commits, et s'ajoute à la fiche qu'elle termine.
- **Un essai part d'un bac, ou se déclare.** `vlp.py cout` ne voit un essai `claude -p`
  que lancé d'un bac du scratchpad de la session. Lancé ailleurs — une copie du kit, un
  worktree jetable —, il se déclare au lancement : `vlp.py essai "<dossier de
  ~/.claude/projects/>"`, glob permis (`MET2`, 2026-10-07).
- **Une définition d'agent se charge au démarrage de la session — pas à la
  volée.** Mesurer l'effet d'un changement dans `agents/*.md` sur une session
  déjà ouverte mesure l'ancienne définition. Avant de mesurer la forme d'un
  sous-agent après un changement d'agent : relancer l'app, ou au moins vérifier
  que la session parente a démarré après le commit. Un **script de hook**, lui,
  est relu à chaque appel.
- **Un fait qui dit comment écrire un fichier se revérifie au moment d'écrire —
  même marqué « mesuré ».** Fins de ligne, encodage, séparateur : une commande les
  tranche en une seconde. Un fait réfuté se corrige **là où il sera relu**, pas
  seulement dans le bilan qui le réfute.
- **La TODO ne grossit pas sans deux oui de l'utilisateur** — décision de
  l'utilisateur, le 2026-09-25, contre le *scope creep*. Chaque chantier laisse
  des restes ; versés tels quels, ils ouvrent du travail que personne n'a choisi.
  D'où :
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
- **Ne pas réinventer la roue — ni un outil, ni un chiffre** — décision de
  l'utilisateur, le 2026-09-28 pour l'outil, le 2026-09-29 pour le chiffre. Avant
  de coder, chercher si l'outil existe déjà (bibliothèque, module standard) ;
  avant de calculer ou de payer un essai, chercher si l'information est publiée
  (un prix, un banc de modèles, une limite d'API) : la doc officielle d'abord,
  puis la communauté. On ne code ou ne mesure que ce qu'aucune source ne donne —
  le propre du projet : son coût par fiche, ses tours, ses fichiers. Le web dit
  le général, la mesure dit le nôtre ; un chiffre du fournisseur que personne n'a
  refait se dit tel. Une contrainte du projet prime, et se dit : les scripts du
  kit restent sans dépendance.
- **L'effort se règle selon la tâche, et se dit avant** — décision de
  l'utilisateur, le 2026-10-04. Plus bas pour le mécanique (lancer un script,
  publier, commiter, mesurer), plus haut pour ce qui se conçoit ou se débogue.
  Une fiche, de code ou de conception, en Opus 5.5 : `medium` ; `xhigh` en recours,
  pour rejouer une fiche refusée ou bloquée — décision du 2026-10-07, après `MET4`
  (même qualité mesurée, `xhigh` nettement plus cher ; `context AI/08-etat.md`, entrée
  « MET4 — xhigh contre medium »). Elle remplace « `xhigh` pour une fiche de code »,
  décidé le même jour après `VIT25`. `high` mesuré le 2026-10-09 sur les mêmes 4
  fiches (`EFF3`) : même qualité aux trois niveaux, `high` +59 % de $ sur `medium`,
  −11 % sous `xhigh`. Aucune fiche du jeu n'était refusée ni bloquée : la mesure ne
  dit pas si `high` suffit au recours (entrée « EFF3 — high contre medium et xhigh »).
  Tout changement s'annonce d'abord par un petit message : le modèle et
  l'effort, avant → après, et pourquoi (« Opus 5.5 · effort high → medium : la
  suite est mécanique »). Le niveau en cours se lit, il ne se suppose pas
  (`get_session` sur `self`, dans l'app de bureau) : l'utilisateur le change à
  tout moment. Sa propre session, Claude ne la change pas — l'outil de l'app
  refuse (« a session must not silently re-price its own turns ») : il dit le
  niveau voulu, l'utilisateur le règle. Une session qu'il lance
  (`boucle.py --effort`, `set_session_effort` sur une autre session), il en
  règle l'effort lui-même, annoncé de la même façon.

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
**Sans fiche** : une modification qui se dit en une phrase se fait directement, sans
chantier ni fiche (source dans « Coder dans le kit »).

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

**Une fiche sans rien à commiter pose un commit vide** —
`git commit --allow-empty -m "<PRÉFIXE><n> : <titre>"` : c'est la borne où
`vlp.py cout` coupe. Décision de l'utilisateur, 2026-09-27, à la clôture de
`SEG` (cairn) : tout y était hors git, aucun commit ne nommait `SEG`, et `cout`
a rendu `DÉCOUPE aucune` — des sessions entières, dont une session parallèle,
**18 147 448** tokens contre **11 262 523** pour le chantier seul (`clore`).

**Un push à la clôture seulement, et jamais sans confirmation** : il publie, et
ne se reprend pas. `cloture.md` le porte.

**Une branche de chantier fusionnée dans `main` : relire `CHANTIER.md` et la feuille** —
Git ne voit pas ces pertes-là. Vu deux fois : prédit par `PAR4`, puis à la fusion de `PAR`
(`2cef70f`, 2026-09-29) : sans conflit, `CHANTIER.md` a perdu le chantier resté ouvert de
l'autre côté (`LOC`), et la feuille régénérée son badge « en cours » — `vlp.py feuille .
--todo <rang>` le rend. Les conflits, eux, se prédisent :
`git merge-tree --write-tree --name-only <branche> main`.

Le sous-agent de `/vlp:enchainer` ne commite pas — il n'a ni le contexte ni le
droit : c'est le chef qui commite, après chaque `FAITE` accepté à la relecture
(`enchainement.md`, « Relecture »).

## Où vit quoi — les sept familles, et rien d'autre

| Fichier | À la racine ? | Qui le lit | Longueur visée |
|---|---|---|---|
| `CLAUDE.md` | oui | **toute** session, en entier, en premier | le seuil de `vlp.py` |
| `CHANTIER.md` | oui | `/vlp:chantier`, `/vlp:tache` et `/vlp:enchainer`, en entier | le seuil de `vlp.py` |
| `<contexte>/00-INDEX.md`, et son archive `00-INDEX-archive.md` à côté | non | l'index : quand le routage de `CLAUDE.md` ne répond pas ; l'archive : pour relire un chantier clos, dont `vlp.py clore` y déplace la ligne (`vlp.py archiver`) | l'index : le seuil de `vlp.py` ; l'archive : libre |
| le **fichier d'état** | non | reprise à froid ; le choix du prochain chantier n'en lit que la TODO, par la carte | libre |
| les **fichiers de fiches**, un par chantier | non | `/vlp:tache` et `/vlp:enchainer`, **par plages**, jamais en entier | libre |
| `<contexte>/artefacts/*.html` | non | publié pour l'utilisateur ; relu par `/vlp:tache` à chaque fiche, par `/vlp:enchainer` une fois par lancement | le seuil de `vlp.py` |
| `<contexte>/NN-nuits.md`, un seul, créé par `vlp.py` à la première nuit | non | le plan du soir, la table des nuits et les leçons ; `vlp.py trier` imprime les leçons ; la ligne d'index le déclare | libre |

Le dossier de contexte s'appelle `context AI/` par défaut. Son nom importe peu ;
ce qui compte est qu'il soit **un seul dossier**, à plat, numéroté.

**Les numéros ne sont pas la convention — les libellés le sont.** L'état
s'appelle `08-etat.md` dans un projet et `10-etat.md` dans un autre. Ce qui ne
varie pas, ce sont les libellés en gras de `CHANTIER.md` — « **fichier
d'état** », « **méthode** », « **artefact du chantier** » — que les
commandes lisent tels quels : elles lisent la ligne, et la ligne dit le nom.
Le chantier en cours, lui, ne se lit pas : il se calcule (« Le chantier ouvert »).

**Le moteur est dans le kit, les données sont dans le projet.** Ne descendent
jamais dans un projet : `skills/`, `agents/`, `hooks/`, `scripts/`, cette
méthode, `cloture.md`, `enchainement.md`, `nuit.md` et les gabarits de `templates/` —
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

**Numérotation.** Un nombre à deux chiffres au moins — `100` suit `99` (chantier `PIP`) —, attribué dans l'ordre de création,
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

**Ce qui part dans Git.** `CHANTIER.md`, `CLAUDE.md`, les `.md` du dossier de
contexte et ses artefacts sont **suivis** : un worktree ne reçoit que les
fichiers suivis, et la mécanique en vit — un commit par fiche, la marque
d'ouverture lue dans un commit, les canaux de nuit, la fusion du matin.
Restent hors Git ce qui est propre à une machine : les tampons (post-it
`vlp-chantier`, marques `vlp-*`) et `.claude/launch.json`. Aucun de ces
fichiers ne porte de chemin de machine. Un dépôt public se trie fichier par
fichier avant d'y verser le contexte. Tranché le 2026-10-08 (`NUI34`).

## Le fichier de fiches

Un chantier = un fichier du dossier de contexte, numéroté comme les autres et
déclaré le jour même : l'index, le routage de `CLAUDE.md`, la ligne
« artefact du chantier » de `CHANTIER.md`, et sa marque d'ouverture.

**Le chantier ouvert — où vit l'état.** Les commandes renvoient ici.

- **La marque**, une ligne du fichier de fiches : `**Ouvert.** le <date>.` ;
  `**CLOS** le …` à la clôture ; `**Pause.** le <date> — <raison>` s'il est mis
  de côté. Ouvert = la première, sans aucune des deux autres.
- **Le chantier du dossier se calcule** : `vlp.py carte` l'imprime en
  `COURANT=` (`courant_de`, seul lecteur) ; « le fichier de fiches courant »
  d'une commande, c'est cette valeur. D'abord le **post-it** du dossier
  (`git rev-parse --git-path vlp-chantier`, propre au worktree, hors Git),
  sinon le seul ouvert — hors de la branche principale, le seul ajouté
  sur cette branche. Deux ouverts : une `GARDE:`.
- **Un chantier seulement hérité** de la branche principale n'est pas celui
  du dossier : `COURANT=aucun`, on peut en cadrer un autre ici.
- **Les autres worktrees** : une ligne `AILLEURS=<code> <dossier>` par
  chantier ; ce code se joue là-bas, il ne se rouvre pas ici.
- **La fusion du jour** : `vlp.py fusionner <projet> <branche>` ; une branche
  qui ajoute un chantier encore ouvert ne se fusionne pas.

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
   Du code se cite par son **nom** — fonction, classe, constante —, jamais par
   sa ligne : le code bouge, la ligne ment (7 renvois sur 7 périmés dans NUI,
   `VIT9`) ; `vlp.py symboles <fichier> <nom>` rend sa ligne du jour.
2. **Aucun libellé ni chiffre inventé** : les libellés viennent de la plage de
   maquette citée ; tant qu'une mesure n'existe pas, la fiche demande la
   mesure, elle n'annonce pas son résultat.
3. **Un critère de fin observable**, sinon la fiche ne peut pas être cochée. Il
   affiche ses comptes bruts (voir « Les règles qui valent partout »). Pour du
   code, il nomme le test, l'appel, la valeur attendue, et **le mutant** — le
   code cassé exprès que ce test doit faire tomber : « les tests passent » ne
   prouve rien, un test creux passe aussi (`FIN1`, puis `FIN2` alors que son
   test était nommé avec ses valeurs, 2026-09-24). Le mutant se joue par
   `vlp.py mutant … --attendu "<début du libellé du test>"` : il mute une copie du kit, jamais le vrai
   fichier, et s'arrête dès que ce test tombe (`VIT2`) ; `--tous` les liste tous (`MUT1`). Un critère joué dans un
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

Un critère vérifie ce que le socle décide, pas un signe qui en tient lieu (un
en-tête n'est pas le texte qu'il annonce). Une règle qui lit les fichiers des
projets s'essaie sur leurs vraies lignes avant d'être écrite dans une fiche
(`LEC2`, quatre refus, journal du 2026-09-25).

## Ce que `/vlp:tache` garantit, et qu'il ne faut pas défaire

`/vlp:tache` est **autoportante** : elle n'ouvre que ce qu'elle nomme, jamais
`CLAUDE.md`, jamais l'index, jamais un fichier de fiches en entier. Elle lit la
sortie **elle-même** au lieu de la demander, s'arrête à deux tentatives, et
finit par le critère de fin recopié. Jouée par un humain, elle vulgarise la
fiche avec son contexte avant d'écrire — la règle vit à son étape 1 ; sous
`/vlp:enchainer`, non.

Quand elle s'arrête ainsi, elle écrit un bloc « **Tentatives** » **dans la
fiche**, sous son titre. C'est ce qui rend la reprise utile : la session
suivante le lit à l'étape 1, avant d'écrire, et cherche autre chose au lieu de
rejouer les mêmes deux essais. Le bloc se solde à la fiche cochée.

`CHANTIER.md`, à la racine, est la seule chose à mettre à jour quand un
chantier s'ouvre ou se clôt. Un fichier qui ment envoie la session dans un
chantier clos.

## Coder dans le kit

Ce que le kit prend aux pratiques publiées, et comment il l'adapte — tranché par
l'utilisateur au chantier `MET` (`context AI/08-etat.md`, entrée « MET1 — ce qui existe »,
2026-10-07). Deux docs officielles, citées par leurs sections : **Best practices**
(https://code.claude.com/docs/en/best-practices) et **Skill authoring**
(https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

**Déjà dans la méthode** — la source, à côté de la règle :

| La règle du kit | Où | Source |
|---|---|---|
| un critère de fin observable | « Anatomie d'une fiche », exigence 3 | Best practices, « Give Claude a way to verify its work » |
| une modification qui se dit en une phrase se fait sans fiche | « Les trois temps » | Best practices, « Explore first, then plan, then code » |
| cadrer en fiches, jouer chaque fiche en session neuve | « Les trois temps » | Best practices, « Let Claude interview you » |
| deux tentatives, puis arrêt et bloc « Tentatives » | « Ce que `/vlp:tache` garantit » | Best practices, « Course-correct early and often » |
| le déterministe en script | `CLAUDE.md` du kit, règle 4 | Skill authoring, « Provide utility scripts » |

**Le code Python des scripts :**

- **Le style est celui de ruff**, réglé par `pyproject.toml` à la racine du kit : chaque
  écart au défaut y porte sa raison (`MET5`). Le code d'avant n'est pas corrigé : `REF`.
  ⚠️ Le cliquet de `sante.py` lance ruff `--isolated` : il ne voit pas ce réglage.
- **`pyproject.toml` ne règle que les outils d'atelier**, jamais un paquet à installer : le
  kit garde zéro paquet à l'exécution (`MET1`, Q10).
- **Un fichier Python de plus de 1 000 lignes ne grossit plus ; un nouveau reste en
  dessous** — le défaut de Pylint, `max-module-lines` (message C0302, « too-many-lines »).
  Aucun script ne le garde encore ; la découpe des gros fichiers : `REF`.
- **Un fichier nouveau se nomme en minuscules, mots liés par un tiret bas** (PEP 8,
  « Package and Module Names ») ; les noms à tiret déjà là restent, leur renommage : `REF`.
- **Une sous-commande porte sa fonction**, branchée par `set_defaults(func=…)` (argparse,
  « Subcommands ») ; l'aiguillage par `if` de `vlp_coeur.py` se convertit à `REF`.
- **Un seuil nouveau porte sa raison**, écrite à côté de lui (Skill authoring, « Solve,
  don't defer »).
- **Retoucher une fonction déjà au-dessus d'un seuil du cliquet** : la docstring que
  `sante.py` exige alors compte elle-même une instruction pour ruff. Sortir le travail dans
  une fonction neuve, documentée, et gagner une instruction dans l'ancienne (dette `ARP`,
  `main` de `boucle.py` : 100 → 104, puis 101, puis 100, 2026-10-08).
- **Un lecteur refuse ce qu'il ne sait pas lire, et une commande vérifie tout avant sa
  première écriture** : une `GARDE:` qui sort 1 et dit « rien écrit », jamais une ligne lue
  à moitié ni un fichier écrit sur deux (`TAB`, 2026-10-09 : une table coupée en silence,
  `clore` qui écrivait avant de lire la TODO).

**La prose que Claude lit** — commandes, agents, doctrine, `CLAUDE.md` :

- **Court, et une seule façon par défaut** (Skill authoring, « Concise is key », « Avoid
  offering too many options »). Le crible, phrase par phrase : Claude le sait-il déjà ? La
  retirer lui ferait-elle faire une erreur ? Sinon, elle part. Une seconde façon ne s'écrit
  que pour un cas nommé où la première échoue.
- **Chaque ligne de `CLAUDE.md` passe ce crible** (Best practices, « Write an effective
  CLAUDE.md ») ; « Où on en est » reste, `vlp.py clore` le tient.
- **Un mot d'insistance — « IMPORTANT », des capitales — se réserve à une règle que Claude a
  ignorée deux fois** (même section) ; le gras qui aide à lire reste.
- **Une chose, un seul nom**, dans tout le kit (Skill authoring, « Use consistent
  terminology »).
- **Rien qui se périme** : une règle garde sa date entre parenthèses, son récit va au journal
  ou à `lecons-mesure.md` (Skill authoring, « Avoid time-sensitive information »).
- **Une doctrine de plus de 100 lignes s'ouvre sur un sommaire**, tenu à la main (Skill
  authoring, « Progressive disclosure patterns »).
- **Une commande nouvelle s'écrit après ses essais** : trois scénarios d'abord, puis un essai
  par modèle prévu pour la jouer (Skill authoring, « Build evaluations first », « Test with
  all models you plan to use »).
