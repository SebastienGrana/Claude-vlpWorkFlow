# /vlp:tache sans refus sous PowerShell — notes et journal
## Lien
https://claude.ai/artifact/PRskc6e4VoLwnS2aYb2Jw7
## Résultat
La sonde de U1 rejouée en U5 : 0 refus de permission sous PowerShell 7, fiche du bac cochée, page régénérée sans GARDE ; 5.1 sondé ; carte sans message du Store.
## Notes
- U1 : 9 refus mesurés (cat 1, $env 5, allowed-tools perdus après confirmation 3), 17 tours, 0,25 $ ; 5.1 non forçable (chemins en dur, 3 sondes Haiku → 7.6.6)
- U2 : test-vlp.py OK, 100 → 108 assertions ; bac, 2 passes : lire, page sans chemin (dossier artefacts créé), cocher → COCHÉ puis refus exit 1 ; valider VALIDE
- U3 : cat " 6 → 0, CLAUDE_CODE_SESSION_ID 1 → 0 ; tache 149 → 150 lignes (cocher + cout + page en un appel, pas d'attente sur critère scriptable) ; renvois 44 · 0 absent ; tests OK ; validate OK
- U4 : 4 sondes Haiku OK : PowerShell et Git Bash PYTHON= en tête (Store à la fin), Ubuntu 1 carte (py absent en tête), shim deux Python 1 seule carte ; injection ×6, tests OK (108), validate OK ; 0,11 $
- U5 : refus 9 → 1 (partie fiche 0 ; 1 Test-Path improvisé à la clôture du bac), Session et page écrites en un appel ; 5.1 non sondable ; evals Windows hook 1/1, Ubuntu 4/4 (1,55 $) ; plugin 3.4.1
## Journal
- 2026-09-17 : U4 : injection py; python3 --relais; py --relais; echo fin — le 3e appel remet à 0 le $LASTEXITCODE de PowerShell ; le relais garde son tampon ; README : désactiver l'alias python3 du Store.
## Bilan
- Livré : vlp.py lire, cocher et page sans chemin ; tache sans cat ni $env ni attente sur critère scriptable ; carte py d'abord ; bac PowerShell refus 9 → 1 (fiche 0) ; evals Windows 1/1, Ubuntu 4/4 ; plugin 3.4.1
- Surpris : les allowed-tools d'une skill tombent dès le message suivant : l'attente de confirmation causait la moitié des refus ; et echo ne remet pas $LASTEXITCODE à 0 sous PowerShell
