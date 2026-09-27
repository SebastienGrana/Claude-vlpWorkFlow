# Un lanceur Python sans accolade — notes et journal
## Lien
https://claude.ai/artifact/UdhUqFegfkke1gimdbSELv
## Résultat
Plus aucun PY=$(for …) dans le moteur : un lanceur scripts/vlp unique, une sonde -p sans refus « brace » ni exit 49, evals 3/3
## Notes
- P1 : scripts/vlp posé, test-vlp OK (+3 cas) ; -p : ancien motif refusé (brace, 0,20 $), sh + Bash(sh:*) passe (0,05 $), sans allowlist → approval ; interactif : passe ; PowerShell : sh introuvable, ancien motif ParserError
- P2 : anciens motifs 18 → 0 ; 25 appels sh …/scripts/vlp (mesure inclus) ; Bash(sh:*) ×6 ; renvois 0 absent ; validate OK (1 avertissement voulu) ; plugin 3.3.2
- P3 : sonde enchainer -p : brace 0, exit 49 0, python3 0 ; chef 14 tours / 19 appels (dont 15 de clôture), sous-agents 8 et 6 tours (L3 : 9/7, 9 et 6) ; evals 3/3 (0,59 $)
## Journal
## Bilan
- Livré : le lanceur scripts/vlp (sh, sans accolade), 18 lancements remplacés par 25 appels sh …/scripts/vlp, allowed-tools Bash(sh:*) ; plugin 3.3.2, evals Windows 3/3 (0,59 $). En -p : ancien motif refusé, lanceur passant, sonde /vlp:enchainer sans refus « brace » ni exit 49.
- Surpris : tache et cloture lançaient aussi mesure-tokens.py et un second bloc à accolades ; sous PowerShell sans Git Bash, sh est introuvable ; le sous-agent rend FAITE sur une fiche (visuel) (TODO n° 14). Total brut : 49 tours, 6 786 706 tokens, 5,98 $, plus 0,75 $ de sondes et 0,59 $ d'evals.
