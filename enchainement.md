# Contrat de retour — fiche enchaînée

Lu par `/vlp:enchainer`, et par les agents `vlp:fiche` et `vlp:relecture` qu'il lance
par l'outil `Agent` (seuls les evals du filet, `evals/filet*/`, appellent encore la skill `vlp:jouer` ;
aucun n'appelle `vlp:relire`).

L'agent `vlp:fiche` rend un compte rendu dont le **premier mot** est l'un des
trois statuts suivants — rien devant, et le détail sur la même ligne.

- `FAITE` — critère de fin constaté, avec ses comptes bruts (voir `methode-chantier.md`) ; case cochée.
  Jamais sur une fiche `(visuel)`, ni case vide : le chef l'y lit comme un `RETOUR`.
- `RETOUR` — ce qu'elle attend d'un humain et pourquoi ; case non cochée.
- `BLOQUÉE` — deux tentatives épuisées, erreur brute ; bloc Tentatives écrit.

La première ligne, telle quelle, sans un mot devant — ni « Parfait », ni titre :

```
FAITE — <critère constaté, comptes bruts>
```

**Fichier d'état, en worktree.** Lancée dans un worktree, une fiche donne son dossier — le `PROJET=`
de sa carte — sur une ligne `DOSSIER: <chemin>` sous la ligne de statut, quel qu'il soit : le chef
y relit, commite et fusionne. Si elle doit écrire le fichier d'état (`CHANTIER.md`, ligne
**fichier d'état**), elle n'y touche pas : elle met ce texte dans son compte rendu, sous la ligne
de statut, entre une ligne `ÉTAT:` et une ligne `/ÉTAT`. Le chef l'y ajoute après la fusion de sa branche.

```
FAITE — <critère constaté, comptes bruts>
DOSSIER: <chemin du worktree>
ÉTAT:
<le texte à ajouter au fichier d'état>
/ÉTAT
```

**Arrêts imprévus** (rendent `RETOUR`) : décision que la fiche ne tranche pas,
dépendance non cochée, permission refusée, fiche portant déjà un bloc Tentatives
— sauf si toutes ses lignes numérotées sont `FAITE refusée à la relecture.`,
l'agent lisant alors `Erreur :` comme ce qu'il ne doit pas refaire —, compte
rendu sans statut (plafond de tours atteint).

## Relecture

Un `FAITE` dont la case et la tête passent `cocher --verifier` est relu avant son
commit par un agent `vlp:relecture` neuf. Son compte rendu commence par l'un de deux
verdicts, rien devant, le détail sur la même ligne :

```
ACCEPTÉE — <ce qui a été rejoué, comptes bruts>
REFUSÉE — fiche : <motifs>
REFUSÉE — copie : <motifs>
```

Aucun verdict vaut `REFUSÉE`. Trois motifs refusent, et eux seuls : le critère de fin
non tenu ; un bug qu'une sortie prouve — du code, ou une doc qu'une commande rejouée
contredit ; un mutant du critère qui survit. `REFUSÉE` porte sa cause avant les
motifs, `fiche` ou `copie`. `fiche` : la faute reviendrait avec tout exécutant qui
suit la fiche à la lettre — critère qui vérifie un signe au lieu de ce que le socle
décide, fiche et socle qui se contredisent, règle inapplicable sur les vraies lignes,
fichier utile non nommé ; sous ce verdict, une ligne `RÉÉCRITURE : <phrase de la
fiche> → <ce qu'elle devient>` — le relecteur n'écrit jamais dans la fiche, seulement
cette ligne. `copie` : la fiche le disait clairement, le sous-agent ne l'a pas fait.

Le reste se remarque, sous la ligne du verdict, sans le changer : la lettre de la
fiche, un `HORS FICHE`, un écart sans effet sur une sortie. Le style ne se signale pas.

Un soupçon se tranche par une sortie, jamais au jugé : rejoue-le dans AVANT et APRÈS
avant de le classer. Une remarque au conditionnel (« serait », « pourrait ») est un
soupçon non rejoué. Un défaut que la copie montre compte, même si un clone neuf ferait
autrement. Ne lis que la sortie de `relecture`, AVANT, APRÈS et ce contrat : le dépôt
vivant raconte la suite, et fausse le jugement.

Fouille au-delà du critère : chaque motif, regex ou condition que le diff change se
sonde, dans AVANT et APRÈS, sur des entrées que les tests n'essaient pas — vide,
forme voisine, autre séparateur, texte libre. Une entrée qui sortait bien dans AVANT
et sort mal dans APRÈS est un bug prouvé.
