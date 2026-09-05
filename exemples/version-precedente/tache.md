---
description: Exécute une fiche du chantier courant d'un projet (md | cairn)
argument-hint: md [U1]
allowed-tools: Bash(cd:*), Bash(sed:*), Bash(grep:*), Bash(tail:*), Bash(./deploy.sh), Bash(ls:*), Bash(python:*), Read, Edit, Write
---

Exécute une fiche du chantier courant du projet **$1**. Si **$2** est donné,
c'est cette fiche-là ; sinon c'est la première fiche non cochée du fichier de
fiches courant, que l'étape 0 bis détermine. Dans toute la suite, « la fiche
retenue » désigne celle des deux qui s'applique.

Suis ces étapes dans l'ordre, sans en sauter ni en ajouter.

## La règle qui prime sur tout : n'ouvre que ce qui est nommé

Cette session a un budget de contexte serré, et **cette commande est
autoportante** : tout ce dont tu as besoin est ici. **N'ouvre aucun fichier que
les étapes ci-dessous ne nomment pas**, et ne lis jamais un fichier en entier
quand une plage suffit. En particulier : pas de `CLAUDE.md`, pas de
`00-INDEX.md`, pas de `09-chantiers.md` / `21-methode-chantier.md` (ils disent
comment *écrire* une fiche, pas comment l'exécuter), et **jamais un fichier de
fiches en entier** — il fait des centaines de lignes, la fiche en fait 20. Pas
d'agent, pas de recherche large : tout est déjà localisé.

## 0. La table des projets — se placer, et savoir où est le chantier

| `$1` | Dossier | Fichier de fiches courant | Livraison | Vérification |
|---|---|---|---|---|
| `md` | `C:/Users/<utilisateur>/Documents/ProgPerso/MapDecorator` | aucun — chantier `R` clos le 2026-09-05, relancer `/chantier md` | `./deploy.sh` | l'utilisateur recharge dans le jeu, puis tu lis le log |
| `cairn` | `C:/Users/<utilisateur>/Documents/ProgPerso/Cairn-VlpLib` | aucun — chantier `N` clos le 2026-09-04, relancer `/chantier cairn` | aucune | tu lances la commande du critère de fin et tu lis sa sortie |

Si `$1` est vide, **demande lequel des deux** avant d'aller plus loin, et
n'ouvre rien tant que tu n'as pas la réponse : la table change, et deviner le
projet ferait jouer une fiche de l'autre.

Si `$1` n'est pas dans cette table, ou si son chantier courant est « aucun »,
arrête-toi et dis-le : c'est `/chantier` qu'il faut lancer d'abord, pas
`/tache`.

Côté `md`, `mockups/TACHES-UI.md` (fiches `T*`) et `context AI/15-annulation.md`
(fiches `U*`) sont **clos** : ils ne se rejouent pas ; ils ne servent plus qu'à
relire le socle d'API à l'étape 4.

Commence par te placer dans le dossier de la table, quel que soit le dossier
d'où la session a été ouverte :

```bash
cd "<dossier de la table>" && pwd
```

Si ce dossier n'existe pas, arrête-toi et dis-le.

## 0 bis. Si `$2` est vide : trouver la première fiche non cochée

Saute cette étape si `$2` est renseigné : la fiche retenue est `$2`.

Sinon, liste les titres de fiches du fichier de fiches courant — les titres
seuls, jamais le fichier entier :

```bash
grep -n '^## [A-Z][0-9]' "<fichier de fiches courant>"
```

La fiche retenue est **la première ligne de cette sortie qui ne porte pas
`[x]`** — la première dans l'ordre du fichier, pas le plus petit numéro :
l'ordre des fiches est celui des dépendances, et `R10` trierait avant `R2`.

Si toutes portent `[x]`, arrête-toi et dis-le : le chantier est fini, il reste
à le marquer **clos** en tête de son fichier et à vider sa ligne dans la table
de l'étape 0.

Annonce ensuite la fiche retenue **en une ligne, avant de l'exécuter** —
identifiant et titre, tels qu'ils apparaissent. Tu n'attends pas de réponse,
mais une case mal cochée doit se voir tout de suite, pas à la fin.

## 1. Lire la fiche, et elle seule

```bash
sed -n '/^## <fiche retenue> /,/^---$/p' "<fichier de fiches courant>"
```

Si la fiche ne s'y trouve pas, arrête-toi et dis-le — n'en cherche pas une
autre ailleurs.

Si elle porte déjà `[x]`, arrête-toi et dis-le. Si elle dépend d'une autre
fiche non cochée, dis-le et demande s'il faut continuer quand même.

## 2. Lire ce que la fiche cite en plage

Une ligne « maquette : `sed -n 'A,Bp' …` » ou « corpus : … » est à exécuter
telle quelle. **Les libellés d'interface viennent de là et de nulle part
ailleurs** — ne les invente pas, ne les traduis pas, ne les reformule pas.

Si la fiche ne donne pas de plage, saute cette étape.

## 3. Lire les fichiers de code que la fiche nomme

Ceux de la ligne « **Fichiers** », rien d'autre. S'ils sont longs, lis la zone
concernée plutôt que le fichier entier.

## 4. Écrire

Lis d'abord le socle commun du fichier de fiches — une seule fois, cette plage
et rien de plus :

```bash
sed -n '/^## Le socle/,/^## L.ordre des fiches/p' "<fichier de fiches courant>"
```

Puis applique le bloc « Prompt » de la fiche.

Contraintes communes aux deux projets, non négociables :

- Libellés et commentaires de code **en anglais**, prose en français.
- **Aucun chiffre inventé** : tant qu'une mesure n'existe pas, zéro, ou un
  contrôle grisé — jamais un chiffre d'exemple de maquette.
- Une API dont tu n'es pas sûr se vérifie, jamais de mémoire.

Contraintes propres à `md` :

- On édite `files/`, **jamais** `Openplanet4/Plugins/MapDecorator/`.
- Un contrôle grisé **affiche toujours sa raison**.
- Les blocs d'une carte s'énumèrent par `pluginMap.Map.Blocks`, **jamais**
  `pluginMap.Blocks`, qui fait crasher le jeu.
- Vérification d'API par grep dans
  `C:/Users/<utilisateur>/Openplanet4/OpenplanetCore.json`. Le socle déjà vérifié est
  dans `sed -n '/^## Le socle commun/,/^## L.état/p' mockups/TACHES-UI.md` —
  ne le regrepe pas.

Contraintes propres à `cairn` :

- **Aucun chemin absolu dans le code** : `paths.py` résout à l'appel.
- La library lit, elle **n'écrit jamais** dans un fichier de jeu.
- Une mesure affiche ses **comptes bruts** à côté de son verdict.

## 5. Livrer, puis vérifier

**Si `$1` vaut `md`** : lance `./deploy.sh`, puis **arrête-toi** sur une seule
ligne — demande de recharger le plugin dans le jeu (F3 → Reload), et de
répondre quoi que ce soit pour continuer. Ne lis pas le log avant ce retour :
il ne porterait encore que l'ancienne version. Au retour :

```bash
tail -n 120 "C:/Users/<utilisateur>/Openplanet4/Openplanet.log" | grep -iE "MapDecorator|ERROR|WARN"
```

**Si `$1` vaut `cairn`** : lance toi-même la commande du critère de fin. Rien à
déployer, personne à attendre.

Dans les deux cas c'est **toi** qui lis la sortie, pas l'utilisateur — ne lui
demande pas ce qu'elle affiche. Si elle porte une erreur, corrige et reprends
l'étape 5. **Deux tentatives au maximum** : à la troisième, arrête-toi, montre
l'erreur brute et dis ce que tu as essayé.

## 6. Clore

Quand ça passe, écris trois choses et rien de plus :

1. Le **critère de fin** de la fiche, recopié — côté `md` c'est ce que
   l'utilisateur doit regarder à l'écran, et lui seul peut le faire ; côté
   `cairn`, c'est la sortie que tu viens de lire, comptes bruts compris.
2. Ce que tu as changé, en deux ou trois lignes.
3. Ce qui t'a surpris, s'il y a lieu — une API qui ne se comporte pas comme
   annoncé, une décision que la fiche ne tranchait pas.

Une fois qu'il confirme, coche la fiche (`## <fiche retenue> [x] — …` dans le
fichier de fiches courant), et ajoute une ligne au fichier d'état du projet
(`context AI/08-etat.md` pour `md`, `context AI/10-etat.md` pour `cairn`)
**seulement** si la tâche a tranché quelque chose d'imprévu.

Si c'était la dernière fiche non cochée, dis-le : le chantier est fini, il
reste à le marquer **clos** en tête de son fichier et à vider sa ligne dans la
table de l'étape 0.

Puis rappelle-lui de faire `/clear` avant la fiche suivante.
