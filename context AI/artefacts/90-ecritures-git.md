# Les écritures Git des sous-agents, tranchées — notes et journal
## Résultat
contrat dit 0 écrivent · 3 bloqués · 1 interrompu depuis FOR, au lieu de 3 écrivent ; le gardien ne bloque plus un echo vers un fichier ; l'interdit de commit est là où le sous-agent finit.
## Notes
- ENQ1 : contrat sépare bloqué / écrit et interrompu / sans statut — dépend de rien
- ENQ2 : un echo ou printf vers un fichier n'est plus lu comme une écriture Git — dépend d'ENQ1
- ENQ3 : mesure les tentatives bloquées, puis met l'interdit à l'étape 5 d'agents/fiche.md — dépend d'ENQ1
## Journal
## Bilan
