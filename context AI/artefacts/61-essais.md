# Les essais claude -p dans le coût — notes et journal
## Lien
https://claude.ai/artifact/AhWBb31gZnFz1zEHvuGhrQ
## Résultat
vlp.py cout compte les essais claude -p dans le prix de leur fiche, avec une part essais à côté ; les 14 clos recomptés face aux ≈ 12,32 $ notés à la main
## Notes
- ESS1 : 8 sondes notées, 8 trouvées, 0 absente (4,5734 $ notés, 4,3001 $ mesurés) ; 10 evals notées, 0 dossier (7,74 $, dehors) ; 13 dossiers sans note (Y, U, Q : 3,5982 $) ; 39 dossiers = 7,8983 $
- ESS2 : test-vlp.py OK (verifier( 297 → 300) : A 2 chemins, B 1, inconnue 0 ; mutant sans -scratchpad- : ÉCART, l'intrus pris ; pyright 0 errors avant et après ; vrai disque : SAG 3, X 26
- ESS3 : test-vlp.py OK (verifier( 300 → 301) : Q1 = session + 1 essai (sous-agent compris), hors fiches = 1 essai, TOTAL = 2 essais ; mutant sans sorte 2 : ÉCART ; pyright 0 errors ; cout REC avant/après identique (REC sans essai)
- ESS4 : noté 12,3134 $ (4,5734 sondes + 7,74 evals) · trouvé par cout 0,77 $ (SAG 0,46 · FIL 0,31) · écart −11,5434 $ · 6 chantiers sur 8 au-delà de 0,05 $ · causes : chantier gardé 9, dossier absent 1, arrondi 2, hors plage 0, sous-agent 0
## Journal
- 2026-09-25 : ESS1 : les 12,32 $ de la TODO = 4,57 $ de sondes + 7,74 $ d'evals (dehors) ; Y, U, Q ont 3,60 $ de bacs jamais notés
- 2026-09-25 : ESS4, cout ne rattrape que 0,77 $ des 4,5734 $ d'essais notés : 9 clos sur 11 sont en DÉCOUPE aucune, mesurés sans essais_de (7,1299 $ de dossiers). TODO n° 68.
## Bilan
- Livré : vlp.py cout compte les essais claude -p dans le prix de leur fiche (part essais, TOTAL compris) ; recompter rend +1 090 457 sur SAG et FIL
- Surpris : 9 clos sur 11 à bacs sont en DÉCOUPE aucune, que cout mesure sans essais : 0,77 $ rattrapés sur 4,5734 $ notés (TODO n° 68)
