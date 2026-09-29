# Un essai rechargé voit le code du worktree — notes et journal
## Résultat
Dans un worktree du kit en avance sur main, la carte dit PLUGIN_RETARD= : combien de commits de code manquent au plugin chargé, et la commande pour avancer main avant un /reload-plugins.
## Notes
- ESR1 : retard_plugin et sa ligne dans la carte, consigne dans tache et check, test sur un vrai worktree et mutant ; ne dépend de rien
## Journal
## Bilan
- Livré : la carte dit PLUGIN_RETARD= (n commits de code, commande merge --ff-only) quand le plugin chargé n'a pas le code du worktree du kit ; tache et check la disent
- Surpris : le plugin chargé ne peut pas voir son propre retard avant que main n'ait ce code : la première alerte viendra après la fusion
- Estimé : estimé 1 fiches ≈3,02 $ · cadré 1 · joué 1 fiches 1,41 $
