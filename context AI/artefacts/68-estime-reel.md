# L'estimé face au réel, à chaque clôture — notes et journal
## Lien
https://claude.ai/artifact/Fre8eWqQkrmvQFanE5z3jr
## Résultat
À la clôture, vlp.py clore écrit seul l'estimé (fiches et $) à côté du réel, dans la ligne CLOS, la ligne Fait. et le bilan de la page.
## Notes
- EST1 : test-vlp.py : OK, 0 échec ; test EST1 (A1–A3 3 000 000 + B1 1 000 000 → ≈1,67 $ pour 2 fiches), mutant « une fiche par ligne » tombe ; 2e appel : estimé gardé, 1 ligne ; pyright scripts/ : 0 errors
- EST2 : test-vlp.py : OK, 0 échec ; CLOS « estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ≈? $ », même texte page et Fait ; sans ligne : estimé non noté ; mutant cadrées=jouées : ÉCART clore : Fait. remplacé ; pyright scripts/ : 0 errors
- EST3 : grep --estime-fiches SKILL.md = 1 ; grep **Estimé.** 1 fiches = 1 ; ouvrir rend « estimé 1 fiches ≈3,91 $ » ; VALIDE 3 fiches, 0 écarts
## Journal
## Bilan
- Livré : vlp.py ouvrir note l'estimé (fiches et $, moyenne des clos), clore l'écrit à côté du réel ; /vlp:chantier passe --estime-fiches
- Surpris : EST, estimé à 1 fiche, en a joué 3 : la TODO estime encore au doigt mouillé
- Estimé : estimé 1 fiches ≈3,91 $ · cadré 3 · joué 3 fiches ≈8,91 $
