# Les réglages d'enchainer tranchés par PAR5 — notes et journal
## Résultat
/vlp:enchainer sans argument joue les fiches dans la session (main), sans bascule de modèle ; le joueur des modes agents et clear est Sonnet, effort low.
## Notes
- REG1 : boucle.py transmet --effort à claude -p, sans défaut ; test et mutant. Ne dépend de rien.
- REG2 : enchainer part en main, agents pour les sous-agents, clear en Sonnet low ; le sous-agent joueur passe de Haiku à Sonnet. Dépend de REG1.
- REG3 : Essai réel sur un bac, par l'utilisateur après /reload-plugins : la fiche est jouée dans la session. Dépend de REG2.
## Journal
## Bilan
