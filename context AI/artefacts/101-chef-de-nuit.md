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
- NUI13 : nuit.md : lire code 0, ne coûte rien 1, 29 citations, 0 ID/plafond/08-etat ; nuit.md +1 ligne dans 5 fichiers, CLAUDE.md 80 lignes ; test-vlp OK, mutant CODE_PLUGIN ATTRAPÉ 1 écart, pyright 0 erreur
- NUI14 : 3 renvois, 1 ligne chacun (tache 1 0, cloture 1 0, chantier 2 0), nuit.md 24 24, 30 citations avant et après, 0 écart relu ; test-vlp OK, main a725aba sans PLUGIN_RETARD ; essai claude -p : FICHE F1 CASE [x] 16 tours 0.4623 $ 68 s, lire nuit.md 1, git commit 0, cloture.md 0, rev-list 1, PROCHAINE=aucune
- NUI15 : test-vlp.py rend OK (732 verifier, 9 pour NUI15 : cas a à h et gardes) ; mutants lettres gardées (1 écart) et todo None (3 écarts) attrapés ; pyright 0 error sur vlp.py et test-vlp.py
- NUI16 : test-vlp.py OK, 743 verifier (+11), 3 mutants attrapés (4, 1, 1 écarts), pyright 0 ; essai D2 : 3 cas sur 4 égaux, empreintes différentes ≠ → publie par la clé, aucune ligne merge=union
- NUI17 : test-vlp.py OK, 784 verifier (743 + 41 neufs), mutants M1 M2 M3 attrapés sur (c) (d) (b), chef page ARTEFACTS.md 1 (0 avant), pyright 0 erreur sur vlp.py et test-vlp.py
- NUI18 : test OK 784 verifier en 502 s, pyright 0 erreur, mutant attrapé (NIV1 et EVF4, 2 écarts), essai réel 0,216118 $ en 1 tour, 0 tool_use, 0 refus, bac 14/14 identique
- NUI19 : test-vlp.py OK (794 verifier, 8 min 18 s), pyright 0 erreur ; mutants sous-agents non sommés, usd_exact None compté 0, ligne de table à chaque rejeu : trois ATTRAPÉS ; SKILL.md +2/+1/+1/+1 et nuit.md +1 constatés
- NUI20 : une vraie nuit sur le kit, mesurée — dépend de toutes
- NUI21 : test-vlp OK (code 0) ; mutant Pause ATTRAPÉ (1 écart) ; ouverts . → OUVERTS=0 ; sans CHANTIER.md / --rev inconnu → GARDE code 1 ; pyright 0 errors
- NUI22 : test-vlp OK (0 ÉCART) ; mutant règle 2 ATTRAPÉ (1 écart, cas a) ; fichier_courant( 8 → 2 lignes (définition + appel unique dans courant_de, la fiche disait 1 à tort) ; pyright 0 errors
- NUI23 : test-vlp OK (0 ÉCART, 6 anciens tests remis au modèle de la marque par sans_chantier) ; mutant artefact toujours repris ATTRAPÉ (1 écart) ; pyright 0 errors ; migré = fichier titré marqué seulement
- NUI24 : test-vlp OK (0 ÉCART) ; mutant « pointe WIP non lue » ATTRAPÉ ; « mis de côté : » dans boucle.py 3 → 0 ; pyright 0
- NUI25 : test-boucle OK (NUI25 4/4 : hérité ni joué ni touché, découpage vide, GARDE au départ, GARDE après clore) ; test-vlp OK 0 ÉCART ; mutant 952 ligne brute ATTRAPÉ ; pyright 0 ; faux-claude.py touché hors liste (fichier dans le contexte)
- NUI26 : test-vlp OK (0 écart, 19:32→19:41) ; mutant exception CLOS → MUTANT ATTRAPÉ 1 écart (NUI26 a) ; pyright 0 ; « main » en dur : vlp.py 2 → 1 (cmd_matin, choix A), boucle.py 2 (cause_de_refus, lanceur, choix A), label merge-file → HEAD
- NUI27 : suite OK (0 écart, 9 min), mutant attrapé par NUI27 (a) seul ; pyright 0
- NUI28 : test-vlp OK (309 s, 0 ÉCART), 2 contrôles NUI28 ; MUTANT ATTRAPÉ 2 écart(s) ; carte du kit 86 → 86 lignes ; pyright 0 errors (3 fichiers) ; coût gonflé par VIT/MET/ARP, à recouper avant clore
- NUI29 : grep « ligne fichier de fiches courant » 1 → 0 ; COURANT= 0 → 14 ; bac : worktree COURANT=aucun + AILLEURS=F, /vlp:chantier ESS cadre ; test-vlp OK
- NUI30 : les projets équipés reçoivent leurs marques, Cairn HD en pause ; après NUI23
- NUI31 : la vieille ligne de CHANTIER.md disparaît ; après NUI29, NUI30
- NUI32 : NUI20 remise au nouveau modèle ; après NUI21 à NUI31
## Journal
- 2026-10-01 : Essai NUI14 sous NUIT=1 : une session claude -p sur une fiche triviale, 16 tours, 0,4623 $, 68 s (un appel lire nuit.md, 0 git commit, 0 cloture.md) ; boucle.py ne crée pas le dossier de --traces.
- 2026-10-01 : NUI16 : essai D2, publie en union égal à la clé dans 3 cas sur 4 (empreintes différentes : deux lignes contre clé retirée) → publie par la clé, pas de merge=union au .gitattributes
## Bilan
