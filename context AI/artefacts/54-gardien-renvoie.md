# Le gardien renvoie pour de vrai — notes et journal
## Lien
https://claude.ai/artifact/QRcCKNW5b4biaNPXBR5H7d
## Résultat
Un FAITE sur case vide est renvoyé même après un premier renvoi, la sonde est retirée, et un témoin le prouve.
## Notes
- GAR1 : cmd_gardien juge encore un FAITE sous stop_hook_active
- GAR2 : vlp.py sonde retiré, code et tests
- GAR3 : un témoin joué à la main : renvoi sur la tête puis sur la case vide — dépend de GAR1
## Journal
## Bilan
- Livré : le gardien juge encore un FAITE après un premier renvoi ; sonde retirée ; prouvé sur un témoin
- Surpris : la faille est apparue en vrai sur GLO1, le soir même : un FAITE sur case vide passait après un renvoi sur la tête
