# Le chef de nuit — notes et journal
## Résultat
/vlp:chef cadre le soir, deux canaux jouent les chantiers la nuit sans humain, puis fusion et rapport le matin
## Notes
- NUI1 : grep -c titre NUI1 : 0 avant, 1 après ; table : 12 lignes +| (9 sessions, validate, en-tête, filet) ; 24 formes JSON (+{"type") ; znorr 0 ; Users 0 ; git status : 08-etat.md seul ; coût des 9 essais 0.9962 $ pour 2.46 $ annoncés
- NUI2 : test-boucle OK (31 vérifications : 10 d'avant + 21 nouvelles ; 23,4 s avant, 21,9 s après) ; test-vlp OK (35,5 s avant, 54,5 s après) ; grep FAUX = : 0 ; mutant boucle.py : ÉCART --effort low transmis tel quel à claude, MUTANT ATTRAPÉ 2 ; mutant faux-claude.py : ÉCART faux : prompt inconnu → code 2, MUTANT ATTRAPÉ 1 ; pyright 0 errors
- NUI3 : test-boucle OK (63 s contre 21,9 s avant ; cas a à f, 2×50 écritures = 100 lignes en 1,2 s) ; test-vlp OK (106 s contre 54,5 s avant) ; mutant pot filtré : ÉCART NUI3 (b) pot des lignes B ≥ borne, MUTANT ATTRAPÉ 1 ; mutant verrou sans garde : ÉCART NUI3 (e) verrou vieilli de 60 s, MUTANT ATTRAPÉ 1 ; mutant w au lieu de a : MUTANT ATTRAPÉ 3 (dont nuits noter) ; pyright 0 errors sur les 5 .py
- NUI4 : test-boucle.py OK, 46 → 68 cas ; mutants garde --nuit et timeout→coupure ATTRAPÉS ; test-vlp.py OK ; pyright 0 erreur sur boucle.py, test-boucle.py, faux-claude.py
- NUI5 : test-vlp.py OK (canaux, cocher --session) ; test-boucle.py OK (6 cas nuit neufs) ; 3 mutants ATTRAPÉS (préfixe du canal, AUTORISES, commit sur REFUSÉE) ; grep statuts 0, VERDICTS 5 ; pyright 0 erreur sur 5 fichiers
- NUI6 : test-boucle.py OK, 9 cas neufs passés / 9 écrits ; 3 mutants attrapés (cas b, e, d) ; test-vlp.py OK ; pyright 0 errors
- NUI7 : test-boucle.py OK, 103 appels à verifier contre 90 avant (13 cas neufs a à j, 1 cas d'avant dont la prémisse change) ; mutants base de branche HEAD et garde clôture hors rôle sans mise de côté : MUTANT ATTRAPÉ 1 écart chacun ; test-vlp.py OK 559 s ; pyright 0 errors sur boucle.py, test-boucle.py, faux-claude.py
- NUI8 : test-boucle OK : 19 cas neufs passés / 19 écrits, 103 cas d'avant passés, 0 sauté (6 min 9 s) ; test-vlp OK ; 3 mutants ATTRAPÉS (mesure sautée, depart sans fin, pot sans usd_kit) ; pyright 0 errors sur les 4 .py ; ÉVEIL tenu lu sous win32
- NUI9 : test-boucle OK : 14 cas neufs passés / 14 écrits (a-e), 8 min 0 s ; test-vlp OK ; 2 mutants ATTRAPÉS (canal A attendu avant le Popen de B, garde d'arbre propre retirée) ; pyright 0 errors sur boucle.py et test-boucle.py ; non prouvés : Ctrl+C, canal sans chantier
- NUI10 : test-vlp.py OK (tester_trier neuf) · 4 mutants MUTANT ATTRAPÉ · trier . sur le kit : sort 0, 8 rangs, 5 PRÊT, 3 ÉCARTÉE, CANAL CAR+TAB+CLV par vlp.py, APR FICHIERS 99-jnt1-mesure.py sans SOIR · pyright 0 errors
- NUI11 : test-vlp.py OK (tester_fichier_nuits neuf, cas a à d) · 3 mutants MUTANT ATTRAPÉ (CARNET_MIN = 0, retirées vivantes, usd_kit lu usd_cli) · grep -c nuits.md 0 → 1, sept familles 1 · pyright 0 errors sur vlp.py et test-vlp.py
- NUI12 : test-vlp.py OK (cas plan 0, a, b, c×9, d) ; 3 mutants MUTANT ATTRAPÉ (NUIT=1 jamais écrite → (d), sections perdues → (b), lettres prises retirées → (c)) ; pyright 0 errors, 0 warnings, 0 informations
- NUI13 : nuit.md : ce que la nuit fait à la place de l'humain — dépend de NUI12
- NUI14 : les commandes renvoient à nuit.md, essai sur bac — dépend de NUI13
- NUI15 : vlp.py matin : fusion, CHANTIER.md et feuille réparés — ne dépend de rien
- NUI16 : fusion par clé de l'état, des listes et d'en-attente — dépend de NUI15
- NUI17 : une page à cartes remplie par script — ne dépend de rien
- NUI18 : /vlp:chef, le soir — dépend de NUI9, NUI11, NUI12, NUI13, NUI17
- NUI19 : /vlp:chef, le matin — dépend de NUI13, NUI15, NUI16, NUI18
- NUI20 : une vraie nuit sur le kit, mesurée — dépend de toutes
## Journal
## Bilan
