# Contrat de retour — fiche enchaînée

Lu par `/vlp:enchainer` et l'agent `vlp:fiche`.

L'agent `vlp:fiche` rend un compte rendu dont le **premier mot** est l'un des
trois statuts suivants, et rien d'autre à la première ligne.

- `FAITE` — critère de fin constaté, avec ses comptes bruts (voir `methode-chantier.md`) ; case cochée.
- `RETOUR` — ce qu'elle attend d'un humain et pourquoi ; case non cochée.
- `BLOQUÉE` — deux tentatives épuisées, erreur brute ; bloc Tentatives écrit.

**Arrêts imprévus** (rendent `RETOUR`) : décision que la fiche ne tranche pas,
dépendance non cochée, permission refusée, fiche portant déjà un bloc
Tentatives.
