> **QUAND LIRE** : on cherche la preuve d'une règle de `methode-chantier.md` — le
> récit mesuré qui l'a fait naître —, ou on groupe, compare ou résume des grandeurs
> mesurées (les trois leçons parties de la méthode). Pas besoin de ce fichier pour
> appliquer une règle : la méthode suffit.

# Les leçons de mesure

Les règles vivent dans `methode-chantier.md`, « Les règles qui valent partout ». Ici,
deux choses, rangées par `MET6` le 2026-10-07 : trois leçons parties de la méthode,
et le récit mesuré des règles restées, sous leur titre et dans leur ordre.

**Sommaire** : Trois leçons parties de la méthode · Les récits des règles restées —
une ligne de mesure · une hypothèse vraie sur un cas · un commentaire périmé · un
seuil arbitraire · un chantier cité par son code · une fiche payée jusqu'au bout ·
une définition d'agent · un fait qui dit comment écrire · la TODO et ses deux oui ·
ne pas réinventer la roue.

## Trois leçons parties de la méthode

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

## Les récits des règles restées

### Une ligne de mesure nomme les quantités qu'elle compare

Mesuré : un chantier a conclu « la cause dominante est l'autosave périmée » à partir
de « 35 autosaves seules / 10 ghosts » — un compte de **quels fichiers existent sur le
disque**, c'est-à-dire un fait sur l'**outillage**. Les deux nombres étaient exacts ;
le pont entre eux n'existait pas. Rejoué en croisant la vraie variable, la source **ne
triait pas** (19 / 7, la proportion du corpus) et la cause était ailleurs. Il n'y
avait aucune erreur de calcul : c'était la mauvaise quantité comparée.

Fondues dans cette règle par `MET6` :

- « Une conclusion recopiée d'une table à l'autre se dégrade en silence » — Mesuré :
  une table de douze énoncés republiée sans être rejouée écrivait **deux fois la même
  quantité** dans ses deux premières lignes, testait **un autre énoncé que le sien**
  dans deux autres, portait les chiffres d'après dans sa colonne d'avant, et annonçait
  en prose **quatre** renversements quand sa propre table en cochait **cinq** — dont
  un qui, rejoué, **tenait**. Quatre défauts, aucune alarme, et la conclusion fausse a
  servi de socle au chantier suivant.
- « Un instrument qui montre peut réfuter ce que la mesure confortait » — pas de récit
  chiffré : son texte entier est resté dans la méthode.
- « Prouver qu'un ancien chiffre a disparu demande la liste de ses valeurs, pas le
  motif qui les a trouvées » — Mesuré sur cairn (`REP`) : le critère de la dernière
  fiche citait « la liste de `REP1` », que `REP1` n'avait pas écrite — elle avait
  grepé un motif. Refaite depuis la table de `REP3` : **86** valeurs, **33** lignes
  touchées, **25** historiques datées, **8** faux positifs (une valeur courte prise
  dans un autre nombre, `139` dans `117 139`).

### Une hypothèse vraie sur un cas se revérifie sur tous

Mesuré (chantier `APC`) : « l'écart est fait des tours d'après `clore` » tenait au
token près pour `ESD` ; sur les 19 clos à expliquer, il tenait en entier pour 5, en
partie pour 14.

Fondues dans cette règle par `MET6` :

- « Un filtre qui se trompe se change sur le vrai corpus, règles candidates côte à
  côte » — Mesuré (chantier `JUG`) sur 29 vrais sous-agents : « après le dernier `---` »
  ne changeait rien — aucun message n'en portait — et « les deux dernières lignes »
  laissait passer 3 vraies fautes ; seule « le mot ouvre une ligne » retirait les 2
  faux renvois sans rien rater.
- Une suite qui tombe sous plusieurs causes se rejoue **une cause à la fois** — Mesuré
  (chantier `ENV`, 2026-10-09) : sous les trois variables de la nuit, 2 `ÉCART` ; sous
  chacune seule, 0, 0 et 2 — `VLP_CANAL` seule, quand le libellé de l'écart nommait
  `VLP_NUIT absent`. Le libellé d'un contrôle dit ce qu'il vérifie d'abord, pas ce qui
  le fait tomber.

### Un commentaire périmé coûte plus cher qu'un chiffre périmé

Mesuré : sur un même chantier, **quatre angles d'analyse indépendants ont accusé le
même innocent le même jour**, tous les quatre conduits par deux commentaires périmés —
alors qu'une **troisième ligne du même fichier** énonçait déjà le fait juste.

### Un seuil calé sur une distribution qui ne pouvait pas répondre reste arbitraire, même quand il tombe juste

Mesuré : une largeur de bande a été choisie sur la distribution des écarts manqués,
alors que par construction cette distribution ne pouvait contenir **aucune** valeur
sous le seuil envisagé. Le chiffre retenu est resté le bon, mais pour une autre raison
que celle écrite.

### Un chantier se cite par son code, jamais par son rang

Le compte : un tri a rendu faux **21 renvois vivants dans cinq fichiers** d'un coup,
et l'audit revenait à chaque fois.

### Une fiche se paie jusqu'à ce qu'elle soit faite — sa reprise comprise

Mesuré : une fiche enchaînée a coûté 1,53 $ à son commit ; sa reprise à la main —
cocher, journal, page — 0,55 $ de plus, que `vlp.py cout`, qui coupe aux commits de
fiche, rangeait dans la fiche **suivante**. Le vrai prix, 2,08 $, n'était écrit nulle
part, et la suivante paraissait plus chère qu'elle n'était.

### Une définition d'agent se charge au démarrage de la session — pas à la volée

Mesuré : une phrase ajoutée à `agents/fiche.md` (chantier `GLO`) a été jugée « sans
effet » sur une session qui avait démarré 21 minutes **avant** le commit, sans
`/reload-plugins` (chantier `FOR`). Rejouée après relance de l'app, la même phrase
changeait nettement la mesure. Un script de hook, lui, est relu à chaque appel : le
gardien changé a jugé en vrai sans relance (chantier `JUG`).

### Un fait qui dit comment écrire un fichier se revérifie au moment d'écrire — même marqué « mesuré »

Mesuré sur cairn : le socle de deux chantiers de suite (`PUB`, puis `REP`) disait
trois pages en CRLF, le second avec leurs comptes de lignes et « mesuré le
2026-09-27 » ; `git ls-files --eol` les disait LF, dans l'index et sur le disque. `PUB` l'avait
écrit dans son bilan, et le cadrage suivant ne l'a pas vu : il relit son socle, pas
les bilans.

### La TODO ne grossit pas sans deux oui de l'utilisateur

Mesuré le 2026-09-25 dans `context AI/08-etat.md` : des entrées 31 à 68, soit 38, le
kit en a créé 32 de lui-même (clôtures, cadrages, une fiche), 2 sont nées d'une
demande de l'utilisateur, 4 sans origine notée ; 21 lignes restent ouvertes.

### Ne pas réinventer la roue — ni un outil, ni un chiffre

Mesuré : le graphique des coûts des pages, dessiné à la main, passé à Chart.js ;
`PAR7`, 10,13 $ pour comparer trois modèles sur deux fiches, quand le guide de coût de
la skill `claude-api` écartait déjà Haiku 4.5 des longues boucles d'agent et donnait
la méthode (tout en effort bas, relancer les échecs plus haut) — restait seulement le
coût par fiche dans le kit.
