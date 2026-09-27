# ECRIT_GIT ne lit pas le texte d'un heredoc — notes et journal
## Résultat
Un sous-agent peut écrire les mots git commit dans un fichier par cat ou tee sans que le gardien le renvoie ; un heredoc qui s'exécute reste refusé.
## Notes
- ECH1 : ecrit_git(commande) : le corps d'un heredoc reçu par cat ou tee est une donnée ; lire_contrat et le gardien l'appellent. Dépend de rien.
## Journal
## Bilan
