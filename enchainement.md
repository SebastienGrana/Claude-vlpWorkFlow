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
REFUSÉE — <les défauts, une ligne>
```

Aucun verdict vaut `REFUSÉE`. Un défaut : ce que la fiche ne demande pas ; un test
qui ne tombe pas sur le mutant du critère ; un bug ; une doc qui dit faux ; une sortie
qui change entre AVANT et APRÈS sans que la fiche l'explique ; un `HORS FICHE` que la
fiche ne justifie pas.
