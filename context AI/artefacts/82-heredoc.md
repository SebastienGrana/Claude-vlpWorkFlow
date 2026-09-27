# ECRIT_GIT ne lit pas le texte d'un heredoc — notes et journal
## Résultat
Un sous-agent peut écrire les mots git commit dans un fichier par cat ou tee sans que le gardien le renvoie ; un heredoc qui s'exécute reste refusé.
## Notes
- ECH1 : ecrit_git : corps d'un heredoc reçu par cat/tee tu, hors $(…) et sans | derrière ; 9 cas + 2 ; mutants (rien retiré ; sans gardes $( et |) : ÉCART ; corpus sous-agents 19 → 14, chef 1157 → 1149 ; test-vlp OK ; pyright 0 errors
## Journal
## Bilan
- Livré : ecrit_git : le corps d'un heredoc reçu par cat ou tee n'est plus lu par le gardien ni par contrat ; un heredoc qui s'exécute (py, | bash, $(…)) reste refusé
- Surpris : Une chaîne citée porte un vrai git reset (ssh '…') : couper les chaînes, piste de la TODO, aurait laissé passer une vraie écriture
- Estimé : estimé 0,5 fiches ≈2,12 $ · cadré 1 · joué 1 fiches ≈3,03 $
