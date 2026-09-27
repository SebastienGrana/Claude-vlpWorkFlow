# Le contrôle avant commit ne se saute plus — notes et journal
## Lien
https://claude.ai/artifact/9UtnkEizPx5Td2M6tgVo9n
## Résultat
Sans claude dans le PATH, .githooks/pre-commit prend le claude.exe de l'app et valide vraiment les manifestes ; un manifeste cassé refuse le commit.
## Notes
- VAL1 : Le hook cherche le claude.exe de l'app (plus haute version), README d'une phrase ; ne dépend de rien.
## Journal
## Bilan
- Livré : Sans claude dans le PATH, le hook avant commit prend le claude.exe de l'app et valide vraiment les manifestes ; un manifeste cassé refuse le commit
- Surpris : La règle de CAS a servi dès la fiche suivante : FAITE sur une case vide, lue comme un RETOUR. Le sous-agent a encore commité, poussé cette fois par le critère : un clone prend le hook de HEAD.
