# Une session claude -p ne meurt plus en attendant l'arrière-plan — notes et journal
## Résultat
Une vraie session claude -p va au bout d'une fiche qui lance une commande longue ; la carte ne crie plus « /clear d'abord » sous /vlp:enchainer ; les fichiers vlp-carte-* ne s'entassent plus.
## Notes
- ARP1 : test-boucle.py OK (premier_plan 4,5 s, suite 188 s), test-vlp.py OK (168 s), mutant ARP1 ATTRAPÉ 1 écart, pyright 0 erreur sur 2 fichiers ; --append-system-prompt présent dans claude 2.1.293
- ARP2 : boucle.py : F1 cochée, ARRÊT plafond de 1 fiches, 6 tours, 240 s ; trace : PowerShell sleep 200 avec timeout 400000, sans run_in_background, résultat FINI ; essai 0,59 $ (estimé 1,5 à 2 $). Prouve « pas morte », pas « grâce à la consigne » : une session, sans témoin
- ARP3 : La carte se tait quand /vlp:enchainer joue, grâce à une marque posée par sa carte.
- ARP4 : Le ménage des fichiers vlp-carte-* et des marques d'ARP3 ; dépend d'ARP3.
## Journal
## Bilan
