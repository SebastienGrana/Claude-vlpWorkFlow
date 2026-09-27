# Le gardien ne juge que la fin du message — notes et journal
## Lien
https://claude.ai/artifact/4PsfU81wC6KeJk3Sj7kdkW
## Résultat
Un verdict qui cite la jauge ou « En résumé » en prose n'est plus renvoyé ; une vraie fin hors contrat l'est toujours — prouvé sur un vrai sous-agent.
## Notes
- JUG1 : test-vlp.py OK, verifier( 284 → 287 ; mutant tete=tout tombe au 1er test ; FORME renvoyés tout 16 · tiret 16 · deux 11 · tete 14 sur 29 ; règle retenue : tete
- JUG2 : test-vlp.py OK, verifier( 287 → 289 ; mutant REGLE=tout : le relecteur de FOR3 tombe ; FORME tout resume 12 jauge 14 → tete resume 10 jauge 14, renvoyés 16 → 14 sur 29
- JUG3 : relecteur en prose : renvoyé 0 fois ; relecteur à résumé à part : renvoyé 1 fois puis fin réécrite ; FORME 2 sous-agents · resume 0 · jauge 0 · tete 2 ; 0,13 $ les deux
## Journal
- 2026-09-25 : JUG1 : sur 29 sous-agents, tete retire les 2 citations et garde les 14 fins hors forme ; tiret = tout (aucun ---), deux rate 3 vraies fins ; règle retenue : tete
## Bilan
- Livré : le gardien ne renvoie plus une citation : un mot de jauge ou « En résumé » ne compte que s'il ouvre une ligne (règle tete, mesurée sur 29 sous-agents, essayée sur deux vrais relecteurs)
- Surpris : tiret = tout sur le corpus (aucun dernier message n'a de ---) ; deux lignes aurait laissé passer 3 vraies fins hors forme
