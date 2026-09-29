# Les réglages d'enchainer tranchés par PAR5 — notes et journal
## Résultat
/vlp:enchainer sans argument joue les fiches dans la session (main), sans bascule de modèle ; le joueur des modes agents et clear est Sonnet, effort low.
## Notes
- REG1 : test-boucle.py : OK (code 0) ; mutant sans --effort dans jouer() : ÉCART « --effort low transmis tel quel à claude », code 1 ; rendu : OK ; pyright 2 fichiers : 0 errors (avant : 0)
- REG2 : model: 0 · model: sonnet 1 · --effort low 1 · Sans main 0 · test-vlp OK · test-boucle OK
- REG3 : Bac bac-reg3, CLI 2.1.284 Sonnet 5.5 : /vlp:enchainer sans argument -> Skill(vlp:tache), F1 jouée dans la session, aucune ligne Agent(vlp:fiche), F1 [x] à 20:14:07 (session 9115c22a), modèle inchangé. Vu dans le terminal, pas dans le panneau Tâches de l'app.
## Journal
- 2026-09-29 : REG3 : le plugin chargé suit le dossier principal, pas le worktree — main avancé de 8 commits (sans push) avant l'essai ; le CLI de l'app vit dans le dossier Packages (AppData virtualisé).
## Bilan
- Livré : /vlp:enchainer sans argument joue les fiches dans la session (main), sans bascule de modèle ; agents et clear jouent en Sonnet low, l'effort transmis par boucle.py ; essayé pour de vrai sur un bac (F1 cochée, aucun sous-agent)
- Surpris : le plugin chargé suit le dossier principal, pas le worktree : l'essai a exigé d'avancer main ; le CLI de l'app n'est pas dans le PATH (app du Store, AppData virtualisé)
- Estimé : estimé 1 fiches ≈3,03 $ · cadré 3 · joué 3 fiches 7,07 $
