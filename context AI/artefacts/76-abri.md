# Mettre notes et journal à l'abri dans un .md — notes et journal
## Résultat
Résultat, notes, journal et bilan d'un chantier vivent dans un .md à côté de sa page ; la page les recopie, et les pages de Cairn ont leur .md.
## Notes
- ABR1 : abri : notes 2 · journal 3 · bilan 1, & relu, page identique, DÉJÀ au 2e ; mutant sans unescape tombe ; verifier 380 → 387, OK ; pyright 0 errors ; mesure : 0/221 notes et 4/88 journal balisés (65 pages)
- ABR2 : creer/note/journal ecrits d'abord dans le .md ; page effacee reprend x/y depuis le .md ; note retiree du .md -> disparait de la page (mutant capte) ; ancienne page sans .md garde ses notes ; verifier 387 -> 396, OK ; pyright 0 errors
- ABR3 : bilan (Livre/Surpris/Estime) recopie dans la ZONE:bilan depuis le .md, ecrit apres resolution de l'estime (jamais le marqueur) ; test de clore verifie le .md sans \x00 ; mutant (ecriture prematuree) capte ; verifier 396 -> 397, OK ; pyright 0 errors
- ABR4 : ARTEFACTS.md : 4 lignes ajoutees (5 avec la ligne vide), grep les montre, renvois 0 absents
- ABR5 : 23 pages Cairn (hors feuille-de-route), 23 .md crees (abri), git status Cairn : 0 .html modifie, seuls les .md nouveaux ; commit 1eb321a dans Cairn, sans pousser
## Journal
## Bilan
