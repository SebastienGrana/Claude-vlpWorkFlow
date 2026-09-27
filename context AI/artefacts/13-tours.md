# Compter les tours, pondérer le coût — notes et journal
## Lien
https://claude.ai/artifact/G7oHVSDZnVJdYXiEPD63CU
## Résultat
Le script de mesure compte une fois par tour et rend les tours, les appels d'outils, le contexte du premier et du dernier tour, et un coût pondéré en tokens équivalents et en dollars. La ligne Session s'écrit par la variable de session, sans deviner. Les totaux de M et C sont recomptés.
## Notes
- T1 : Test : OK. Session C1 : tours = 31, divergents = 0, total 3417872 (ancien compte 6406759).
- T2 : Test : OK. Session de M par id seul : 34 tours, 31 appels ; par chemin C:\ : 66 tours, 63 appels ; une ligne par outil.
- T3 : Test : OK. C1 (Sonnet 5) : equiv 531268 < total 3417872, usd 1.06 ; ratios sortie 5, cache lu 0,1 (0,025 sur Fable 5.1), écrit 1,25 à 5 min, 2 à 1 h.
- T4 : grep scratchpad dans Coût de la fiche : 0 ; grep CLAUDE_CODE_SESSION_ID : 1 ; SESSION non vide et table rendue. Blocs exécutés tels qu'écrits ; rejeu réel de /vlp:tache à faire.
- T5 : M : 100 tours, total 11362254 ; C : 68 tours, total 7816316 ; grep des anciens chiffres : seule la ligne datée du journal ; feuille de route republiée.
## Journal
- 2026-09-17 : T1 : sans message.id, mesure-tokens.py repère un tour par requestId, puis par sa ligne ; sur la ligne TOTAL, ctx_1er et ctx_dernier valent « - », un contexte ne se somme pas. Mesuré sur C1 : le cache écrit mêle 5 min (47 978) et 1 h (26 375) — T3 ne peut pas tout compter au prix 1 h.
- 2026-09-17 : T2 : un fichier passé plusieurs fois à mesure-tokens.py n'est compté qu'une fois. T2 à T5 jouées d'affilée dans la session de T1 : le coût d'une fiche y est l'écart du compteur de session depuis la fiche précédente.
- 2026-09-17 : T3 : un tour à comptes nuls (<synthetic>) coûte 0 ; un tour fast compte comme modèle inconnu, la grille ne donnant pas le prix de son cache. Ratios non communs (cache lu 0,025 sur Fable 5.1) : modèle inconnu, equiv et usd valent « ? ».
- 2026-09-17 : T4 : le cumul passe l'id de session en tête du flux de xargs -0, qui sous macOS ne lance rien sur une entrée vide. Vérifié en exécutant les blocs tels qu'écrits ; le rejeu réel de /vlp:tache sur un projet équipé reste à faire.
- 2026-09-17 : T5 : M et C recomptés (anciens : M 13 030 459, C 15 389 496, une fiche « 51 à 128 tours »). Nouveaux : M 11 362 254, C 7 816 316, une fiche /vlp:tache = 28 à 66 tours. L'ancien script comptait chaque ligne assistant : ×1,7 à ×2,2, ×4,6 sur E7. Pages de M et C gardées en archives.
## Bilan
- Le script de mesure compte une fois par tour et rend tours, appels d'outils, contexte du premier et du dernier tour, et un coût pondéré en équivalents et en dollars ; il est testé. La ligne Session s'écrit par la variable de session. M et C sont recomptés. Total mesuré à la clôture : ≈16,2M (16 194 635), 16,55 $.
- L'ancien compte gonflait ×1,7 à ×2,2, et ×4,6 quand les appels d'outils partaient en parallèle. Jouées d'affilée, les fiches coûtent de plus en plus par tour : 181 k en T3, 293 k en T5. Reste à rejouer /vlp:tache pour de vrai sur un projet équipé.
