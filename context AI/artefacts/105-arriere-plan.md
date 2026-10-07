# Une session claude -p ne meurt plus en attendant l'arrière-plan — notes et journal
## Résultat
Une vraie session claude -p va au bout d'une fiche qui lance une commande longue ; la carte ne crie plus « /clear d'abord » sous /vlp:enchainer ; les fichiers vlp-carte-* ne s'entassent plus.
## Notes
- ARP1 : La consigne « premier plan » donnée à toute session -p, dans boucle.py seul ; testée au faux claude.
- ARP2 : Un essai réel, payant : une vraie session -p sur une fiche à commande longue ; dépend d'ARP1.
- ARP3 : La carte se tait quand /vlp:enchainer joue, grâce à une marque posée par sa carte.
- ARP4 : Le ménage des fichiers vlp-carte-* et des marques d'ARP3 ; dépend d'ARP3.
## Journal
## Bilan
