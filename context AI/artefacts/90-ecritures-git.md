# Les écritures Git des sous-agents, tranchées — notes et journal
## Lien
https://claude.ai/artifact/SMDkZ5pSLFekzj6QPPVDrU
## Résultat
contrat dit 0 écrivent · 3 bloqués · 1 interrompu depuis FOR, au lieu de 3 écrivent ; le gardien ne bloque plus un echo vers un fichier ; l'interdit de commit est là où le sous-agent finit.
## Notes
- ENQ1 : test-vlp.py OK, pyright 0 erreur ; contrat --ouverture 58-forme-sous-agent.md → 11 sous-agents · 0 écrivent · 3 bloqués · 0 sans statut · 1 interrompus ; corpus entier : 103 sous-agents · 5 écrivent · 5 bloqués · 45 sans statut · 1 interrompus (avant : 10 écrivent · 46 sans statut)
- ENQ2 : 4 cas ajoutés à ECH1 + test dédié, test-vlp.py OK, pyright 0 erreur ; contrat sur a860169308600a92b : git 1 → git 0 ; corpus vlp:fiche inchangé (5 écrivent · 5 bloqués · 45 sans statut · 1 interrompus)
- ENQ3 : 08-etat.md : 5 sous-agents avec ≥1 bloqué, 1 avec plusieurs, 5/5 après f98ceec ; interdit déplacé à l'étape 5 de agents/fiche.md, une seule fois (grep) ; test-vlp.py OK
## Journal
## Bilan
- Livré : contrat sépare bloqué/écrit et interrompu/sans-statut (REFUS_GIT, INTERROMPU) ; le texte cité d'un echo/printf vers un fichier n'est plus lu comme une écriture Git (sans_echo) ; l'interdit de commit du sous-agent déplacé à l'étape 5 d'agents/fiche.md, une seule fois
- Surpris : les 3 vraies fautes de FOR sont toutes des tentatives refusées (0 écriture réelle), et le sans-statut restant était un interrompu, pas une faute
- Estimé : estimé 1 fiches ≈2,97 $ · cadré 3 · joué 3 fiches 7,38 $
