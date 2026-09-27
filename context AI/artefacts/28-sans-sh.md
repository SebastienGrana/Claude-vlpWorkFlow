# Le kit sans sh — notes et journal
## Lien
https://claude.ai/artifact/3kr8HUKbmuFbt7QQ3awLcg
## Résultat
Deux tableaux mesurés (hook, carte injectée) sous Windows PowerShell et Ubuntu, puis le candidat appliqué — ou le n° 16 reformulé avec sa raison
## Notes
- X1 : 5 candidats × 2 systèmes : aucun seul ne passe ; paire exec python3 + py passe les deux (Win 49 puis 0 VALIDE, Ubuntu 1 puis 0 VALIDE) ; 10 sondes, 0,313 $
- X2 : 6 candidats × 2 systèmes : seul python3 … || python … lance la skill partout (Windows pwsh 7.6.6, message du Store dans la carte ; 5.1 refuse ||) ; une dernière commande en erreur fait échouer la skill à 0 tour ; 23 sondes, 0,443 $
- X3 : Renoncé (choix de l'utilisateur) : ordre inversé sondé, py … || python3 … propre sous pwsh 7, Git Bash et Ubuntu (6 sondes, 0,141 $) ; rien d'appliqué, recette dans la TODO n° 16 ; git diff sans fichier du plugin
## Journal
## Bilan
- Sondé, puis renoncé. Sans sh, aucun nom de Python n'est commun à Windows et Ubuntu : le hook ne passe partout qu'en paire exec python3 + py (une erreur non bloquante de chaque côté), la carte injectée qu'en py … || python3 … (propre sous pwsh 7, Git Bash et Ubuntu).
- Rien d'appliqué : tous les postes qui font tourner le kit ont déjà sh, et sans Git les 17 appels sh du corps des skills échoueraient encore. La recette est dans la TODO n° 16.
- Surprises : python3 … || python … colle le message du Store devant PROJET= ; une injection dont la dernière commande échoue fait échouer la skill à 0 tour ; Git Bash réécrit -p "/sonde" en chemin Windows. 68 tours, 10 921 635 tokens, 8,96 $, plus 0,90 $ de sondes.
