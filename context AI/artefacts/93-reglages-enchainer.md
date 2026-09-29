# Les réglages d'enchainer tranchés par PAR5 — notes et journal
## Résultat
/vlp:enchainer sans argument joue les fiches dans la session (main), sans bascule de modèle ; le joueur des modes agents et clear est Sonnet, effort low.
## Notes
- REG1 : test-boucle.py : OK (code 0) ; mutant sans --effort dans jouer() : ÉCART « --effort low transmis tel quel à claude », code 1 ; rendu : OK ; pyright 2 fichiers : 0 errors (avant : 0)
- REG2 : enchainer part en main, agents pour les sous-agents, clear en Sonnet low ; le sous-agent joueur passe de Haiku à Sonnet. Dépend de REG1.
- REG3 : Essai réel sur un bac, par l'utilisateur après /reload-plugins : la fiche est jouée dans la session. Dépend de REG2.
## Journal
## Bilan
