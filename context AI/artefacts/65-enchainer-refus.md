# /vlp:enchainer rejoue une fiche floue — notes et journal
## Lien
https://claude.ai/artifact/JYcQpXPB33miEmCW3tAxg2
## Résultat
Après un refus, le relecteur dit si la faute est dans la fiche ou chez le sous-agent ; le chef le montre dans un questionnaire, et propose de jouer à la main dès le 2e refus. ENC lui-même se joue en main : l'essai grandeur nature.
## Notes
- ENC1 : test-vlp.py : OK, 0 échec ; 2 mutants testés (n=toutes lignes, n=1 fixe) tombent tous les deux ; pyright : 0 errors
- ENC2 : grep -c des 3 chaînes REFUSÉE — fiche :, REFUSÉE — copie :, RÉÉCRITURE : = 1 chacune ; exception FAITE refusée présente ; enchainement.md = 60 lignes (≤60)
- ENC3 : SKILL.md=145 lignes (≤146) ; refus.md=24 lignes (≤30) ; grep refus.md dans SKILL.md=1 ; 4 options + · refus dans refus.md=1 chacune
## Journal
## Bilan
- Livré : cocher --refuser dit le rang du refus (ENC1) ; le relecteur classe REFUSÉE en fiche ou copie et propose une RÉÉCRITURE (ENC2) ; le chef pose un questionnaire à 4 options avant de rejouer un refus (ENC3)
- Surpris : un with imbriqué qui réutilise la variable t d'un test voisin écrase son dossier temporaire avant qu'il serve — piège rencontré en écrivant le test de ENC1
