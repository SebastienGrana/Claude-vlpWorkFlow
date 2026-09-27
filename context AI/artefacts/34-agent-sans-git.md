# /vlp:enchainer sans Git — notes et journal
## Lien
https://claude.ai/artifact/4QHw2nEwQfRzYdxhXsKjRH
## Résultat
Dans un bac PowerShell sans .git ni outil Bash, /vlp:enchainer joue deux fiches, les coche et rend FAITE — refus avant/apres affiches cote a cote.
## Notes
- Q1 : 4 tours, 0,1357 $, 7 appels ; 3 refus (Read hors projet, tous du sous-agent), shell absent = 0 tentative ; statut RETOUR ; 0 fiche cochee sur 2 ; carte du sous-agent non journalisee
- Q2 : agents/fiche.md : cat 1 -> 0, PowerShell 0 -> 1, grep -n 1 -> 0 ; lire/cocher/valider --plan a la place ; test-vlp.py OK, renvois 45 nommes 0 absents, plugin validate passed
- Q3 : commandes bannies en tete de ligne 0 sur 11 fichiers (ls 2 -> 0) ; allowed-tools 55 -> 36 entrees (19 mortes retirees), depareillees 11 -> 0 ; test-vlp.py OK, renvois 0 absents, plugin validate passed
- Q4 : meme bac, plugin repare : refus 3 -> 0, 2 fiches cochees sur 2, FAITE x2, sortie.txt et sortie2.txt ecrits ; 12 tours, 0,3526 $ ; evals hook 1/1 et Ubuntu 4/4
- Q5 : enchaine 0,176 $/fiche (0,3526 $ / 2, bac) contre 0,42 $/fiche a la main (U5, meme bac) : 2,4x moins cher sur fiches scriptables ; en session reelle le chef part de ~78k non comptes, et un RETOUR annule le gain ; README, plugin 3.4.2, TODO 21 retiree (TODO vide)
## Journal
- 2026-09-17 : Q1 : un bac de sonde doit renommer les references en dur au plugin (skill: vlp:jouer, agent: vlp:fiche), sinon le chef appelle le plugin reel ; --plugin-dir veut un chemin Windows
- 2026-09-17 : Q4 : l'etape 5 de enchainer disait d'appliquer cloture.md sans donner la commande — 3 refus ; elle porte maintenant vlp.py lire cloture.md, comme tache etape 7
## Bilan
- Livré : /vlp:enchainer tourne sans Git : PowerShell donné au sous-agent vlp:fiche, kit lu par vlp.py lire, coche par cocher, ls remplacés par lignes, allowed-tools 55 → 36 entrées ; bac PowerShell sans .git ni Bash : refus 3 → 0, deux fiches jouées et cochées, chantier du bac clos ; evals Windows 1/1, Ubuntu 4/4 ; plugin 3.4.2
- Surpris : le nom du plugin est en dur dans enchainer et jouer : un bac renommé appelle la skill du plugin réel et mesure autre chose ; et l'étape 5 d'enchainer demandait d'appliquer cloture.md sans donner la commande pour le lire
