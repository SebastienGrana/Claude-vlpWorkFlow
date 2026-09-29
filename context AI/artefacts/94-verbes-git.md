# Le gardien ne voit que trois verbes Git — notes et journal
## Résultat
Le gardien et contrat bloquent tout appel Git d'un sous-agent qui n'est pas une lecture (diff, status, log, show, rev-parse, ls-files, blame, grep) : git checkout et git stash ne passent plus.
## Notes
- VRB1 : ECRIT_GIT en liste blanche, git en position de commande, tests et deux mutants, rejeu sur 145 sous-agents ; ne dépend de rien
## Journal
## Bilan
