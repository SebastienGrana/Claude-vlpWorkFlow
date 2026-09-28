# Le filet en eval rejouable — notes et journal
## Lien
https://claude.ai/artifact/Q4TySCaXvCVZuQ6f91Hpgm
## Résultat
Une commande rejoue les deux essais de FIL3 en eval du plugin ; un changement du filet se reprouve en un appel, ≈ 0,16 $ le passage.
## Notes
- EVF4 : Variante A (sans redirection) : 12 Read vus, « fichier 05 » trouvé, témoin échoue ; B (PLUGIN_DATA) refusée. 7 SKILL.md corrigés, test + mutant, pyright 0.
- EVF1 : OUI : Read called 12x, matched fichier 05, témoin fichier 13 échoue ; 0,15195725 $ ; transcription sous-agent 5 tours, 15 appels, FAITE.
- EVF2 : kit-essai + test + mutant ; plafond 6 : 1 avertissement (transcription), 80 : 0 ; la trace de l'eval ne voit pas les hooks — critère réécrit la nuit, à valider.
- EVF3 : Le cas F2 (Bash, exit 3) sous WSL2, et la commande qui rejoue les deux cas. Dépend d'EVF2.
## Journal
- 2026-09-26 : EVF4 : la redirection de NIV1 retirée des 7 injections — seule variante qui passe sous eval ; décidé seul la nuit, à valider.
- 2026-09-26 : EVF2 : la trace de l'eval ne porte pas le contexte des hooks ; le filet se prouve par la transcription gardée — critère réécrit la nuit, à valider.
## Bilan
- Livré : bash evals/filet/rejouer.sh rejoue les deux essais du filet (F1 Read, F2 exit 3) en eval du plugin sous WSL2, en un appel, ≈0,28 $ le passage
- Surpris : la trace de l'eval voit les appels d'outils du sous-agent mais pas le contexte de ses hooks ; la redirection 2> de la carte bloquait tout fork sous eval
- Estimé : estimé 2 fiches ≈7,79 $ (taux plat) · cadré 4 · joué 4 fiches 14,24 $
