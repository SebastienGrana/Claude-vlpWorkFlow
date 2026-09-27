# Le kit sans Git Bash — notes et journal
## Lien
https://claude.ai/artifact/UWhqsTpQNUmwnztwz85auy
## Résultat
Une session -p avec l'outil PowerShell seul : le hook rend VALIDE sans erreur, et le prérequis des commandes est écrit, cité de la doc.
## Notes
- G1 : Tableau 5 mécanismes, sourcés doc + 3 sondes -p (0,115 $) : sans Git Bash, hook sh → exit 1 muet, injection → skill en échec ; forme exec python …/vlp.py hook → VALIDE 1 fiches.
- G2 : Prérequis Git for Windows écrit dans README (doc citée, erreur mesurée) ; hook inchangé (VALIDE 1 fiches) ; tests OK 59 assertions, renvois 0 absent, validate 1 avertissement voulu ; TODO n° 16 ouverte.
## Journal
- 2026-09-17 : 2026-09-17 — G1 : un poste Windows sans Git ne se simule pas par l'environnement (PATH sans Git, CLAUDE_CODE_GIT_BASH_PATH faux : l'outil Bash reste) ; on le simule par shell: powershell sur le hook ou la skill. Sans Git Bash, sh casse hook (exit 1, muet) et injection (skill en échec) ; la forme exec python …/vlp.py hook passe.
## Bilan
- Livré : la preuve, par la doc et 3 sondes -p, que sans Git Bash le hook sh rend exit 1 sans rien dire, et qu'une skill à !`sh …` échoue avant tout tour. Git for Windows est désormais écrit requis dans le README.
- Surpris : un poste sans Git ne se simule pas par l'environnement, parce que Claude Code retrouve Git Bash hors PATH. Il se simule par shell: powershell. Aucun hook ne se réserve à un OS : le kit sans sh part en TODO n° 16.
