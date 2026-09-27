# Evals du plugin — notes et journal
## Lien
https://claude.ai/artifact/HuzF1uSZeEvW89uUaoGS5e
## Résultat
claude plugin eval passe 5 cas sur un bac à sable (init, chantier, tache, check, hook), graders gratuits seuls ; validate rend 0 avertissement et tourne avant chaque commit
## Notes
- V1 : Cas check : score 1, 26 tours, 0,24 $ (après 3 runs ratés à 0,24 $ au total) ; fixtures par scaffold_script.
- V2 : Bloquée : tache et chantier exigent Bash, refusé sous Windows (pas de sandbox). Cas écrits, tag wsl2 ; TODO n° 11.
- V3 : init : score 1, 19 tours, 0,39 $, 0 Artifact ; hook : score 1, 2 tours, 0,10 $, INVALIDE prouvé dans la trace.
- V4 : validate marketplace 1 → 0 avertissement ; pre-commit refuse un plugin.json cassé ; suite Windows 3/3, 39 tours, 0,93 $.
## Journal
- 2026-09-17 : V2 bloquée sous Windows : les cas qui exigent Bash se jouent sous WSL2 (TODO n° 11) ; V4 ne l'attend plus.
## Bilan
- Livré : trois tests automatiques qui passent sous Windows — check, init, hook (3 runs, 39 tours, 0,93 $) — et un contrôle avant commit qui refuse un manifeste cassé ; validate sans avertissement sur le marketplace.
- V2 abandonnée, non faite : tache et chantier exigent Bash, que Claude Code refuse sous Windows faute de sandbox. Leurs cas sont écrits ; ils se joueront sous WSL2 (TODO n° 11).
- Surprise : le sous-agent limité à 8 tours ne tient pas une fiche d'essais — relancé 4 fois pour V1, il a écrasé deux fichiers du kit (restaurés). Coût : ≈19,3M (19 316 675) tokens, 12,80 $, plus 2,25 $ de runs d'eval.
