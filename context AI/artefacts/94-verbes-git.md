# Le gardien ne voit que trois verbes Git — notes et journal
## Résultat
Le gardien et contrat bloquent tout appel Git d'un sous-agent qui n'est pas une lecture (diff, status, log, show, rev-parse, ls-files, blame, grep) : git checkout et git stash ne passent plus.
## Notes
- VRB1 : ECRIT_GIT en liste blanche, git en position de commande, tests et deux mutants, rejeu sur 145 sous-agents ; ne dépend de rien
## Journal
## Bilan
- Livré : le gardien et contrat refusent tout appel Git d'un sous-agent hors des 8 verbes de lecture (liste blanche), git lu en position de commande ; checkout et stash ne passent plus
- Surpris : un seul faux positif sur 1539 appels rejoués : echo "git dans …" (le guillemet fait lire git comme une commande)
- Estimé : estimé 1 fiches ≈3,02 $ · cadré 1 · joué 1 fiches 1,18 $
