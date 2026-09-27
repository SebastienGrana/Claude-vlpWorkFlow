# L'index ne garde que le vivant — notes et journal
## Lien
https://claude.ai/artifact/8J9f3sDCdc7NVpAFRZEyi5
## Résultat
L'index du kit passe sous 80 lignes ; ses 63 lignes de chantiers clos sont dans 00-INDEX-archive.md, sans perte, et clore y range chaque nouveau clos.
## Notes
- IDX1 : test-vlp.py OK (3 cas neufs + 4 mutants attrapés), pyright scripts/ 0 errors, sorties sans archive inchangées
- IDX2 : test-vlp.py OK (0 écart), archiver : ARCHIVÉ 2 puis 0, clore archivé 1 ; 3/3 mutants attrapés ; pyright 0 errors
- IDX3 : index 105 → 43 lignes ; clos index 63 → 0, archive 0 → 63 ; renvois 0 absents ; RECOMPTE identique (63 clos · écart -5 267 600) ; archiver relancé : ARCHIVÉ 0
## Journal
## Bilan
- Livré : l'index ne garde que le vivant : 63 lignes de clos dans 00-INDEX-archive.md, lue par recompter et niveau, et clore y range chaque nouveau clos (vlp.py archiver)
- Surpris : index 105 → 43 lignes sans une ligne perdue ; un recompter a une fois rendu un fichier vide, non reproduit
- Estimé : estimé non noté · cadré 3 · joué 3 fiches ≈9,03 $
