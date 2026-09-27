# Un hook n'agit qu'une fois — notes et journal
## Lien
https://claude.ai/artifact/2R2w8zMfCKbEhkU8Gm9bdG
## Résultat
La paire python3 + py reste, mais un hook n'agit qu'une fois : un seul renvoi, un seul VALIDE par écriture.
## Notes
- PYT1 : premier_lancement : tampon exclusif par empreinte de l'entrée
- PYT2 : compté en vrai dans la session : 2 VALIDE avant, 1 après — dépend de PYT1
## Journal
## Bilan
- Livré : un hook n'agit qu'une fois : python3 et py partent tous deux, le premier qui crée le tampon agit, l'autre se tait ; 2 VALIDE par écriture avant, 1 après
- Surpris : filet et hook reçoivent la même entrée sur une écriture : sans le nom de sous-commande dans l'empreinte, hook se serait tu derrière filet
