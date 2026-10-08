# Une session claude -p ne meurt plus en attendant l'arrière-plan — notes et journal
## Résultat
Une vraie session claude -p va au bout d'une fiche qui lance une commande longue ; la carte ne crie plus « /clear d'abord » sous /vlp:enchainer ; les fichiers vlp-carte-* ne s'entassent plus.
## Notes
- ARP1 : test-boucle.py OK (premier_plan 4,5 s, suite 188 s), test-vlp.py OK (168 s), mutant ARP1 ATTRAPÉ 1 écart, pyright 0 erreur sur 2 fichiers ; --append-system-prompt présent dans claude 2.1.293
- ARP2 : boucle.py : F1 cochée, ARRÊT plafond de 1 fiches, 6 tours, 240 s ; trace : PowerShell sleep 200 avec timeout 400000, sans run_in_background, résultat FINI ; essai 0,59 $ (estimé 1,5 à 2 $). Prouve « pas morte », pas « grâce à la consigne » : une session, sans témoin
- ARP3 : test-vlp.py OK (145 s) : ARP3 9 contrôles, VIT20 + NIV1 + ARP3 27, NIV1 6 ; mutant ARP3 ATTRAPÉ 1 écart ; pyright 0 erreur sur 3 fichiers ; tester_niv1_injection ne compare pas enchainer, rien à y admettre
- ARP4 : test-vlp.py OK (145 s), ARP4 2 contrôles ; mutant ARP4 ATTRAPÉ 1 écart ; pyright 0 erreur sur 3 fichiers ; vlp-carte-* : 1 202 au début de la fiche (1 185 le 2026-10-07), 3 après la suite (elle appelle carte_injectee sur le vrai dossier), 1 après une carte ; vlp-enchaine-* : 0 → 0
## Journal
## Bilan
- Livré : toute session de boucle.py reçoit la consigne « premier plan » (une vraie session -p va au bout d'une attente de 200 s), la carte se tait sous /vlp:enchainer par une marque de session, et les tampons vlp-carte-* s'effacent (1 202 → 1)
- Surpris : la suite de tests fait déjà le ménage du vrai dossier temporaire (elle appelle carte_injectee) ; boucle.py --traces plante sur un dossier absent ; l'essai réel a coûté 0,59 $ pour 1,5 à 2 $ estimés
- Estimé : estimé 2,5 fiches ≈9,93 $ · cadré 4 · joué 4 fiches 10,09 $
