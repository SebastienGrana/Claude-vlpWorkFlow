# Contrat de retour — fiche enchaînée

Lu par `/vlp:enchainer`, l'agent `vlp:fiche` que lance la skill `vlp:jouer`, et
l'agent `vlp:relecture` que lance la skill `vlp:relire`.

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

**Arrêts imprévus** (rendent `RETOUR`) : décision que la fiche ne tranche pas,
dépendance non cochée, permission refusée, fiche portant déjà un bloc
Tentatives, compte rendu sans statut (plafond de tours atteint).

## Relecture

Un `FAITE` dont la case et la tête passent `cocher --verifier` est relu avant son
commit par un agent `vlp:relecture` neuf. Son compte rendu commence par l'un de deux
verdicts, rien devant, le détail sur la même ligne :

```
ACCEPTÉE — <ce qui a été rejoué, comptes bruts>
REFUSÉE — <les motifs, une ligne>
```

Aucun verdict vaut `REFUSÉE`. Trois motifs refusent, et eux seuls : le critère de fin
non tenu ; un bug qu'une sortie prouve — du code, ou une doc qu'une commande rejouée
contredit ; un mutant du critère qui survit. La ligne `REFUSÉE` porte les motifs seuls.

Le reste se remarque, sous la ligne du verdict, sans le changer : la lettre de la
fiche, un `HORS FICHE`, le style, un écart sans effet sur une sortie.

Un soupçon se tranche par une sortie, jamais au jugé : rejoue-le dans AVANT et APRÈS
avant de le classer. Une remarque au conditionnel (« serait », « pourrait ») est un
soupçon non rejoué. Un défaut que la copie montre compte, même si un clone neuf ferait
autrement. Ne lis que la sortie de `relecture`, AVANT, APRÈS et ce contrat : le dépôt
vivant raconte la suite, et fausse le jugement.
