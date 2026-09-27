# Afficher la conso sur toutes les pages — notes et journal
## Lien
https://claude.ai/code/artifact/b72f8b89-f4c3-4cb1-aa35-344efd08ea23
## Résultat
Chaque fiche de l'artefact de chantier montre son coût en tokens, et un total apparaît en bas de chaque liste — celle des fiches d'un chantier, et celle des chantiers clos de la feuille de route. Pas de cumul entre projets équipés.
## Notes
- C1 : Marqueurs ZONE inchangés, deux gabarits sous 250 lignes, un seul appel à mesure-tokens.py dans tache.md, compte brut visible à côté de l'arrondi.
- C2 : Feuille de route : colonne Tokens, total de M reporté, E « non mesurable », total cumulé. Page de M : son coût dans le bilan.
## Journal
## Bilan
- Le coût en tokens est affiché sur toutes les pages : par fiche et en total sur la page d'un chantier, en colonne Tokens avec un total cumulé dans la table des clos de la feuille de route — toujours avec le compte brut à côté de l'arrondi. M reporté après coup ; E « non mesurable ».
- Ce qui a surpris : le coût relevé en fin de fiche n'est qu'un instantané. La session de C1 a continué de consommer ensuite (≈4,4M affichés à la fiche, ≈6,4M à la clôture) ; les coûts ci-dessus sont remesurés sur les sessions entières. Et C2, sans aucun fichier local à modifier, a coûté plus que C1 — et n'avait pas reporté sa republication dans la copie locale de la feuille de route, rattrapée à la clôture.
