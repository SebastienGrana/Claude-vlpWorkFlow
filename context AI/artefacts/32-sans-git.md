# Le kit entier sans sh — notes et journal
## Lien
https://claude.ai/artifact/4Ds6mG8JcZWVtgrKVs6YXE
## Résultat
Le kit tourne de bout en bout sans Git Bash (hook, carte, corps des skills, clôture), prouvé par une sonde /vlp:tache simulée sans Git et les evals ; le README n'exige plus Git.
## Notes
- Y1 : 22 sondes Haiku (Windows pwsh 7 et Git Bash, Ubuntu) + contrôles locaux 5.1 : || refusé par PowerShell, python3 …; py …; echo fin lancée partout, corps en commande simple passe (0 refus) ; bin/ inutile sans Git ; 0,463 $ ; scripts/vlp : retirer
- Y2 : vlp.py cout [--session], valider --plan, equiper : 4 passages Unix remplacés ; diff vide sur 10/3/17 lignes, init 1 écart voulu (DOSSIER= natif) ; tests 96 → 102 OK
- Y3 : hook = paire exec python3 + py, 4 injections python3 …; py … --relais; echo fin ; sondes Git Bash, PowerShell, Ubuntu : hook VALIDE (l'autre Python exit 49 / 1), PYTHON= et PROJET= en tête ; tests 103 OK, validate OK ; 0,127 $
- Y4 : appels sh 15 → 0, tuyaux 3 → 0, validate OK, tests 103 → 104 OK ; vlp.py lignes ajouté
- Y5 : 0 appel sh, fiche du bac cochée 5/5 (Haiku ×4, Sonnet ×1) ; evals Windows hook 1/1, Ubuntu 4/4 ; scripts/vlp retiré ; 0 renvoi absent ; plugin 3.4.0
## Journal
- 2026-09-17 : Y1 : la recette de X ne tient pas hors bypassPermissions — PowerShell refuse toute chaîne || (« control-flow or chain statement »), 5.1 ne l'analyse pas ; forme retenue : injection python3 …; py …; echo fin, corps en commande simple ; bin/ d'un plugin n'est que dans le PATH de l'outil Bash (0,463 $ de sondes).
## Bilan
- Livré : le kit tourne sans Git : hook en paire exec python3 + py, carte injectée sans sh, corps des skills en <python> "…/vlp.py", scripts/vlp retiré ; bac PowerShell 0 appel sh, evals Windows 1/1 et Ubuntu 4/4 ; plugin 3.4.0
- Surpris : PowerShell refuse toute chaîne || même permise, et un run d'eval Windows n'accorde aucun shell : les sondes en bypassPermissions de X mentaient
