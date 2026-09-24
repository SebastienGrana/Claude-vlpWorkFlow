# Contrat de retour — fiche enchaînée

Lu par `/vlp:enchainer` et l'agent `vlp:fiche`, que la skill `vlp:jouer` lance.

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
