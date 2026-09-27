# Hooks du kit — notes et journal
## Lien
https://claude.ai/artifact/MTMEspegQa2HCZxww8Tqfq
## Résultat
Un fichier de fiches cassé est refusé dès son écriture par un hook PostToolUse du plugin, prouvé après /reload-plugins ; l'appel valider prescrit dans /vlp:chantier disparaît ; SessionStart gardé seulement si les chiffres le justifient.
## Notes
- H1 : Hooks chargés après /reload-plugins : python et py parlent (exit 2, racine substituée), python3 et la forme args muets ; « republie » 2 → 0 ; check A–G passent ; init rejoué sur un bac à sable, publication neutralisée.
- H2 : test-vlp.py OK (5 cas hook) ; 16-script.md → JSON VALIDE 5 fiches, exit 0 ; 11-conso.md → écart ligne 88 sur stderr, exit 2 ; méthode et commands/chantier.md muets ; 0,19–0,21 s par appel.
- H3 : Après /reload-plugins (1 hook) : Write intact → VALIDE en contexte ; Edit sans <!-- /FICHE --> → écart ligne 15, INVALIDE ; coche de H3 → VALIDE 4 fiches · socle 51 lignes. valider dans un bloc de chantier.md 1 → 0 ; identique|marqueur 16 → 15.
- H4 : SessionStart écarté : avec, ctx_1er 60 609 (2 tours, 122 861 tokens) ; sans, 58 635 (1 tour, 58 936) — +1 974 tokens par tour dans toute session, sans retirer d'injection (carte périmée en cours de session).
## Journal
- 2026-09-17 : H1 : le kit lié dans skills/ charge ses hooks ; forme retenue : la boucle PY des commandes (python3 muet sous Windows, forme args non déclenchée).
- 2026-09-17 : H2 : un fichier de fiches se reconnaît hors bloc de code — la méthode, chantier.md et le gabarit en montrent sans en être.
- 2026-09-17 : H3 : hook branché et prouvé en vrai ; les écritures par Bash (sed -i, heredoc) lui échappent.
- 2026-09-17 : H4 : SessionStart écarté aux chiffres — +1 974 tokens par tour, et la carte change en cours de session.
## Bilan
- Livré : vlp.py hook (testé) et hooks/hooks.json — un hook PostToolUse qui valide un fichier de fiches à chaque Write ou Edit : sain, la ligne VALIDE en contexte ; cassé, l'écart et la consigne, aussitôt. Prouvé en vrai après /reload-plugins. /vlp:chantier n'appelle plus valider dans un bloc ; tache-page.md lit avant de publier ; check et init rejoués.
- Surpris : le kit lié dans skills/ charge bien ses hooks, mais python3 y échoue muet sous Windows et la forme args ne se déclenche pas. SessionStart écarté : +1 974 tokens par tour dans toute session, pour une carte périmée dès qu'une fiche est cochée.
- Laissé ouvert : les écritures par Bash échappent au hook ; Windows sans Git Bash non testé. Total mesuré à la clôture : 14 649 178 tokens · 87 tours · 11,02 $.
