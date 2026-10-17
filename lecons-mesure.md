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
un essai hors bac · une définition d'agent · une option de Claude Code · un fait qui dit comment écrire · la TODO et ses deux oui ·
ne pas réinventer la roue · l'effort selon la tâche · le chemin du code changé ·
l'estimé qui se double · le commit vide · le code cité par son nom · le mutant.

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
- Un fait tiré d'un refus, d'un relecteur ou d'une page **se rejoue avant de s'écrire** —
  Mesuré (`ENA8`, 2026-10-13) : la docstring de `lancables` recopiait la formule du 5e
  refus d'`ENA5` ; rejouée par le relecteur, elle était fausse (refus 1, `2a3f2fc`) ; la
  2e tentative a rejoué 10 cas et dit le trou vrai (`77f75b8`, acceptée).

### Un nombre qu'un script relit vit sur sa ligne à lui

Mesuré (`ENA7`, 2026-10-13) : le compte de refus, posé en fin de la tête du bloc
**Tentatives**, à côté du motif libre du relecteur. Un motif contenant « non résolu »
laissait la tête soldée sur une fiche rouverte ; une sonde de la même famille : « · refus 2 »
dans un `--resolu` faisait lire `refus 3`. Remède : une ligne à elle,
`Refus soldés : <n> · dernier : <motif>`, et la tête lue à sa place (`0811c7a`, 3 mutants
attrapés).

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

### Un essai part d'un bac, ou se déclare

Mesuré à `ESH` (2026-10-12), sur 1 278 transcripts : 148 portent la marque `turnOrigin`
« sdk », tous des `claude -p`. Le champ `entrypoint` ne dit pas qui a lancé : 100 de ces
148, lancés depuis l'app, y portent `claude-desktop`, comme une séance humaine. Un seul
essai hors bac n'était compté nulle part : `PAR`, le 2026-09-29, 1 tour · 0,08 $.

Le filtre qui semblait évident a été mesuré avant d'être écrit : écarter les séances
ouvertes par `/vlp:tache`, pour taire celles d'`enchainer clear`. Il aurait caché
**36 essais réels** hors bac (`MET4`, `VIT25`), pour **0** séance de boucle hors nuit
trouvée. Le faux signal reste possible, et se lit dans la docstring d'`essais_hors_bac`.

### Une définition d'agent se charge au démarrage de la session — pas à la volée

Mesuré : une phrase ajoutée à `agents/fiche.md` (chantier `GLO`) a été jugée « sans
effet » sur une session qui avait démarré 21 minutes **avant** le commit, sans
`/reload-plugins` (chantier `FOR`). Rejouée après relance de l'app, la même phrase
changeait nettement la mesure. Un script de hook, lui, est relu à chaque appel : le
gardien changé a jugé en vrai sans relance (chantier `JUG`).

### Une option de Claude Code se mesure dans un bac avant qu'on bâtisse dessus — sa doc ne suffit pas

Mesuré (`ENA2`, 2026-10-12, Claude Code 2.1.296) : la doc des skills, lue mot pour mot le
jour même, disait `background: true` « running it in the background » ; dans le bac, la
`Skill` `vlp:jouer` a attendu la fin de la fiche (55 s) et rendu son résultat dans le même
appel, aucune des 4 exceptions écrites ne s'appliquant. L'outil `Agent` en
`run_in_background: true`, lui, a rendu la main en 1 s (`08-etat.md`, journal du
2026-10-12). Chercher la doc d'abord (« Ne pas réinventer la roue », plus bas), puis
l'essayer sur le cas du kit avant d'y poser une commande.

### Un fait qui dit comment écrire un fichier, ou ce que rend un autre projet, se revérifie au moment de s'en servir — même marqué « mesuré »

Mesuré sur cairn : le socle de deux chantiers de suite (`PUB`, puis `REP`) disait
trois pages en CRLF, le second avec leurs comptes de lignes et « mesuré le
2026-09-27 » ; `git ls-files --eol` les disait LF, dans l'index et sur le disque. `PUB` l'avait
écrit dans son bilan, et le cadrage suivant ne l'a pas vu : il relit son socle, pas
les bilans.

Mesuré sur MapDecorator, à l'audit `AMD` du kit (2026-10-11) : le socle du chantier `P`,
« mesuré le 2026-09-15 », citait `summary.json` de cairn — sa taille, ses comptes, deux de
ses champs. Le fichier avait été refait le 2026-09-30 : ces 5 faits étaient tous périmés,
les deux champs avaient disparu, et `P2`, écrite pour les lire, n'en aurait rien tiré ; elle
ne compilait pas non plus, pour d'autres raisons, dans son code (`21-audit-amd.md` de
MapDecorator, faits 3 à 7 et section `P2`).

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

Une sécurité aussi : `ENA5` (2026-10-12) a voulu garantir « jamais deux fiches sur un même
fichier » en lisant les lignes **Fichiers**, sur `apercu_fiches`, dont la doc dit « le repère
prévient, il ne garantit rien » ; `commiter` lisait les chemins entiers — deux règles du même
fichier, en désaccord. 5 refus d'une même famille, ≈ 21 $ pour 4,06 $ estimés ; et même juste,
la lecture ratait 73 paires sur 347. Git voit déjà les conflits : le parallèle est parti à
`ISO`, chaque fiche dans son worktree. Avant de bâtir une garantie sur une fonction, lire ce
qu'elle promet — un indice ou une garantie — et chercher l'outil qui la porte déjà.

### L'effort se règle selon la tâche

Mesuré à `MET4` (2026-10-07) : même qualité, `xhigh` nettement plus cher que `medium`
(`context AI/08-etat.md`, entrée « MET4 — xhigh contre medium ») ; la décision remplace
« `xhigh` pour une fiche de code », prise le même jour après `VIT25`. `high` mesuré le
2026-10-09 sur les mêmes 4 fiches (`EFF3`) : même qualité aux trois niveaux, `high` +59 %
de $ sur `medium`, −11 % sous `xhigh`. Aucune fiche du jeu n'était refusée ni bloquée : la
mesure ne dit pas si `high` suffit au recours (entrée « EFF3 — high contre medium et xhigh »).

### Le cadrage vérifie le chemin du code changé

Mesuré à `ESS` : le chantier visait 11 clos, 9 étaient en `DÉCOUPE aucune`, hors du chemin
modifié (journal `ESS4` du fichier d'état).

### L'estimé du cadrage se double

Mesuré à `AVL2` (2026-10-11), sur les 45 clos qui portent un estimé chiffré : estimé 91
fiches · 348,03 $, joué 167 fiches · 574,89 $ — ×1,84 en fiches, ×1,65 en $ ; l'écart
grandit d'une semaine à l'autre (×1,25, ×1,64, ×1,96 en $). Revu à la clôture d'`AVL`
(2026-10-12), le premier chantier ouvert après la règle mais cadré avant elle : estimé
6 fiches ≈ 24 $, joué 12 fiches · 68,08 $ (ligne `CLOS`) — ×2 en fiches.

Ce qui a le plus coûté, un indice sur trois fiches de deux audits, pas une mesure : une
fiche qui écrit dans plusieurs projets et republie leurs pages — `AVL9` (121 tours ·
13,08 $), `AVL10` (105 tours · 9,90 $), `ACA7` (68 tours · 7,80 $), la plus chère de
chacun.

### Une fiche sans rien à commiter pose un commit vide

Mesuré à la clôture de `SEG` (cairn, 2026-09-27) : tout y était hors git, aucun commit ne
nommait `SEG`, et `cout` a rendu `DÉCOUPE aucune` — des sessions entières, dont une session
parallèle, **18 147 448** tokens contre **11 262 523** pour le chantier seul (`clore`).

### Du code se cite par son nom, jamais par sa ligne

Mesuré à `VIT9` : 7 renvois sur 7 périmés dans `NUI`.

### Un critère de code nomme son mutant

Vu le 2026-09-24 : « les tests passent » ne prouvait rien, un test creux passait aussi —
à `FIN1`, puis à `FIN2` alors que son test était nommé avec ses valeurs.

### Le parallèle se mesure contre la file, sur le même chantier

Mesuré à `ISO7` (2026-10-17) : le même chantier à blanc de 5 fiches, joué à la file puis en
parallèle (2 worktrees). À la file : **10,8 min · 3,24 $**. En parallèle : **17,8 min · 5,12 $**
— **+65 %** de temps, **+58 %** de coût —, et deux fiches ensemble une seule fois (46 s). Le
parallèle marche de bout en bout, sans geste à la main, mais il paie un conflit rejoué, des
relectures en double et un second lancement (le plafond compte le rejeu). Une variante ne
s'emploie que sur un gain mesuré : celle-ci n'en a pas (`context AI/121-iso.md`, « Mesuré à ISO7 »).


### Un témoin doit pouvoir produire l'artefact qu'il contrôle

Mesuré à la relecture de fin du chantier `FAM` (cairn, 2026-10-15). `FAM8` cherchait les
objets en miroir de part et d'autre de la route, et comparait au témoin « un côté décalé de
50 m le long de la course » : écart **2,47 points**, hypothèse tenue. Mais la position le long
de la course était celle du **nœud de route le plus proche** : tous les objets au-delà d'un
bout de route avaient la même, et s'appariaient entre eux. **14 913** paires sur **27 801**
(53,6 %) venaient de là ; le décalage de 50 m cassait cette collision, donc le témoin ne la
reproduisait jamais. Sans ces objets : **1,77 point**, hypothèse renversée. Dix fiches et une
validation à l'œil (en bloc) ne l'avaient pas vu ; un relecteur qui recalculait chaque cas,
puis une seconde vérification de ses chiffres, l'ont trouvé.
