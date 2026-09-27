# Une GARDE au lieu d'un traceback — notes et journal
## Lien
https://claude.ai/artifact/QQxmj1U8isNTaJKAfMxLyP
## Résultat
Aucun chemin venu de CHANTIER.md ne peut plus faire tomber une sous-commande de vlp.py : elle rend GARDE: et sort 1.
## Notes
- Z1 : 18 couples mesurés, 11 gardent déjà, 7 plantent — table remplie dans le socle
- Z2 : py scripts/test-vlp.py imprime OK et sort 0 ; cas 108 → 115 sites (119 assertions) ; table de Z1 rejouée sur les mêmes bacs : tracebacks 2 → 0, feuille et clore du cas 1 rendent GARDE et 1
- Z3 : grep -rn "sed \|awk " skills/ : 1 avant, 0 apres ; reste 1 mention de sed, en interdiction (skills/tache/SKILL.md:81) ; test-vlp.py OK
- Z4 : Avant : carte/feuille GARDE + code 1, renvois code 1 ; apres : carte PROCHAINE=P6f code 0, FEUILLE todo 0 · encours oui · lettres 1 · reecrite code 0, renvois 2 ABSENT preexistants code 1 — aucun traceback dans les deux jeux.
## Journal
- 2026-09-17 : Z3 : une plage de fichier du projet ne se lit par aucune sous-commande (vlp.py lire refuse hors du kit) ; le remplacant de sed -n 'A,Bp' est l'outil Read avec offset/limit, deja dans allowed-tools.
## Bilan
- Livré : Toute lecture d'un chemin venu de CHANTIER.md rend une GARDE: en clair et sort 1, au lieu d'un traceback — prouvé sur Cairn-VlpLib
- Surpris : carte gardait deja mais sortait 0 : une garde muette pour l'appelant, aussi indiagnosticable que le traceback voisin
