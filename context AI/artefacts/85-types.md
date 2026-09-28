# pyright sans erreur, gardé au commit — notes et journal
## Résultat
Un commit qui indexe un .py passe par pyright ; en erreur, il est refusé ; pyright absent, le hook le dit et laisse passer.
## Notes
- TYP1 : pyrightconfig.json (include scripts, mode standard) ; bloc pyright du pre-commit avant claude, seulement si un .py est indexé ; tester_hook_pyright, faux pyright : .md seul code 0, .py code 1 « pyright en erreur », sans pyright code 0 « introuvable » ; mutants condition .py retirée et code de sortie ignoré : ÉCART ; pyright racine 0 errors, 6 fichiers ; test-vlp OK, 0 SAUTÉ
## Journal
## Bilan
- Livré : pyrightconfig.json (scripts, mode standard) et un bloc pyright dans .githooks/pre-commit : un commit qui indexe un .py en erreur est refusé ; pyright absent, le hook le dit et laisse passer
- Surpris : Le faux pyright sans extension est trouvé par le sh de Git sous Windows : il se dit exécutable par son #! ; 38-audit-scripts porte 12 erreurs d'avant, laissé dehors
- Estimé : estimé 1 fiches ≈4,16 $ (taux plat) · cadré 1 · joué 1 fiches 1,64 $
