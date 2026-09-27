# Le contrat du sous-agent, vérifié à sa sortie — notes et journal
## Lien
https://claude.ai/artifact/S67CbUwD7JjgTfbDbR4e1t
## Résultat
Un sous-agent vlp:fiche qui tente de commiter est arrêté par un hook, prouvé sur un témoin — ou, faute de hook possible, la règle chargée est mesurée et le chiffre le dit.
## Notes
- CON1 : test-vlp.py : OK ; mutant sans git -C → ÉCART « témoin sale » (git 1 au lieu de 2). contrat --depuis f98ceec : 8 sous-agents · 0 écrivent dans Git · 5 sans statut en tête
- CON2 : sautée : 8 sous-agents (CON1, contrat --depuis f98ceec ; seuil 5) — aucun témoin joué
- CON3 : PreToolUse refuse (prouvé), SubagentStop renvoie (prouvé, stop_hook_active au 2e arrêt), SubagentStart reçu ; sonde débranchée, HEAD 32f114a inchangé — choix : les deux
- CON4 : test-vlp.py : OK (9 tests gardien + hooks.json) ; mutant agent_type inversé → ÉCART « gardien : sous-agent vlp:relecture laissé passer » ; pyright 0 errors
- CON5 : HEAD 60ef683 avant et après le témoin qui devait commiter ; PreToolUse:Bash hook error « Un sous-agent vlp:fiche n'écrit pas dans Git » dans sa transcription ; statut RETOUR ; 4 tours, 0,04 $
## Journal
- 2026-09-25 : CON1 : après f98ceec, 8 sous-agents vlp:fiche, 0 écrivent dans Git, 5 sans statut en tête — la clause qui casse est le statut, pas le commit ; les 4 qui commitent partent 17 min avant f98ceec. CON2 sautée (8 > 5).
- 2026-09-25 : CON3 : SubagentStop peut renvoyer le sous-agent (prouvé, contre un résumé de la doc) ; un SubagentStop arrive avec agent_type vide — filtrer sur agent_type. Choix : PreToolUse + SubagentStop.
## Bilan
- Livré : vlp.py contrat lit le contrat du sous-agent ; vlp.py gardien le tient — PreToolUse refuse l'écriture Git, SubagentStop renvoie sans statut en tête, prouvés en vrai
- Surpris : Après la règle, aucun sous-agent n'a commité : c'est le statut en tête qui casse (5 sur 8) ; et SubagentStop peut renvoyer, contre un résumé de la doc
