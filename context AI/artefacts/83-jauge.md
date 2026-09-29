# Une ligne qui s'ouvre par un mot de jauge, sans être une jauge — notes et journal
## Lien
https://claude.ai/artifact/HdCA6Er5uSgx2ztdUVGyPb
## Résultat
Une puce comme « - Imprévu : j'ai dû… » ne fait plus renvoyer un sous-agent ; une vraie jauge (émoji, ou le mot suivi de —, … ou fin de ligne) le fait toujours.
## Notes
- OUV1 : EMOJIS_JAUGE ou SUITE_JAUGE exigés par la règle tete ; 7 cas gardien (puce « - Imprévu : » muette) ; mutant forme ignorée : ÉCART ; rejeu mesure_ouv.py 79/79 jauges gardées, 199 sous-agents 70 → 70 lignes ; test-vlp OK ; pyright 0 errors
## Journal
## Bilan
- Livré : La règle tete exige la forme d'une jauge : émoji de jauge en tête, ou le mot suivi de —, … ou fin de ligne ; une puce « - Imprévu : » ne fait plus renvoyer
- Surpris : Le faux positif redouté n'est jamais arrivé : 0 ligne sans émoji suivie de « : » sur 79 jauges de sous-agents
- Estimé : estimé 0,5 fiches ≈2,12 $ (taux plat) · cadré 1 · joué 1 fiches 1,17 $
