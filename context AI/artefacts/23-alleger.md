# /vlp:enchainer : alléger le chef — notes et journal
## Lien
https://claude.ai/artifact/Y4gMbrQmjNSpxCsDKiTxrq
## Résultat
Tours du chef mesurés avant (15) → après, sur une fiche FAITE et une RETOUR ; page en un appel, chef en Sonnet
## Notes
- L1 : Étape 4 d'enchainer : cat tache-page.md 1 → 0, commande vlp.py page 0 → 1, SKILL.md 105 → 110 lignes, renvois 46 nommés · 0 absent
- L2 : model: sonnet posé (doc : override pour le reste du tour) ; maxTurns 25 → 30 ; « Aucun autre outil » à l'étape 3 bis ; enchainer 110 → 114 lignes, fiche.md 38 → 38 ; validate : passe
- L3 : Chef 15 → 9 tours (7 + 2 à la reprise), 14 → 7 appels, 2,07 $ → 0,78 $ ; chef en claude-sonnet-5 malgré --model opus (témoin : opus) ; FAITE + RETOUR ; evals 3/3 (19, 2, 23 tours) ; version 3.3.1
## Journal
- 2026-09-17 : L2 : model: sonnet sur le chef (vaut pour tout le tour), maxTurns de vlp:fiche 25 → 30 (22 tours mesurés)
- 2026-09-17 : L3 : model: sonnet bascule le chef, mais une réponse en texte le rend à Opus ; motif PY=$(for …) refusé en -p (TODO n° 13)
## Bilan
- Livré : la page en un appel, aucune action du chef après un RETOUR, model: sonnet sur le chef, maxTurns 25 → 30 ; plugin 3.3.1, evals Windows 3/3. Chef 15 → 9 tours, 14 → 7 appels, 2,07 $ → 0,78 $ (sonde headless).
- Surpris : une réponse en texte rend le chef à Opus (nouveau prompt) ; le motif PY=$(for …) est refusé en -p (TODO n° 13). Total brut : 52 tours, 7 324 563 tokens, 6,06 $, plus 1,26 $ de sondes et 1,00 $ d'evals.
