# Ce que vlp.py écrit, il le relit — notes et journal
## Lien
https://claude.ai/artifact/FpW5mgUnZbqmCmvreVM5ig
## Résultat
Chaque format que vlp.py écrit passe par son lecteur dans un test : un coût négatif garde son signe, une ligne close sous 1 000 tokens se recompte, une lettre se lit hors d'un titre ou sans titre, un résumé tient sur une ligne.
## Notes
- TAR1 : COUT et triplet relisent le signe ; arrondi passe au million dès 999 950 ; ne dépend de rien.
- TAR2 : total_clos relit un coût nu sous 1 000, clore perd son rattrapage ; ne dépend de rien.
- TAR3 : lettres_prises lit entrée par entrée, resume_claude écrit sur une ligne ; ne dépend de rien.
## Journal
## Bilan
- Livré : Ce que vlp.py écrit, il le relit : un coût négatif garde son signe, une ligne close sous 1 000 tokens se recompte, une lettre se lit hors d'un titre ou sans titre, un résumé tient sur une ligne
- Surpris : Les trois sous-agents ont écrit leurs tests d'abord, comme la fiche le demandait, mais ont débordé ou relâché le code ; onze mutants prouvent les reprises.
