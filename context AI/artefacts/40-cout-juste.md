# Un coût juste, fiche par fiche et sous-agents compris — notes et journal
## Lien
https://claude.ai/artifact/FpVtjMX2wqNboLrfCbvxGk
## Résultat
vlp.py cout rend, pour chaque fiche de REP, un coût coupé aux heures des commits, sous-agents compris, plus une ligne « hors fiches » ; une ligne « ? $ » ne fait plus perdre de coût, et Opus 5.5 a son prix.
## Notes
- CPT1 : --grille : 8 modèles, claude-opus-5-5 compris (4 · 20 · 0.20 · 5 · 8) ; REP da8e3b04 : usd ? → 20.96, plus de « modèle absent » ; test-vlp OK, verifier 177 → 179 ; test-mesure-tokens OK, cas 4 → 5
- CPT2 : da8e3b04 : session + 5 agent-*.jsonl + TOTAL 37 490 931 ; 5 sous-agents 8 161 098 tokens (= socle) ; test-mesure-tokens OK, cas 5 → 11, blocs 1 → 3 ; test-vlp OK ; sous-agents illisibles 8 → 0 sur 96
- CPT3 : test-vlp.py OK, verifications 179 -> 185 ; REP sur copie : 3 211 466 + 4 539 690 + 16 480 389 + 4 889 837 + hors fiches 6 875 079 = total 35 996 461 tokens · 306 tours · 20,63 $, egal a la mesure seule de la session et de ses 5 sous-agents
- CPT4 : cout REP : 4 lignes de fiche, 1 hors fiches, 1 TOTAL ; REP2 2 sous-agents, REP3 3, somme 8 161 098 (= CPT2) ; TOTAL 35 996 461 tokens · 306 tours · 20,61 $ ; table avant / après : 6 lignes qui s'additionnent, colonne plage Σ 0 ; test-vlp OK, test-mesure-tokens OK
## Journal
- 2026-09-23 : CPT1 : sous Windows, open() échoue sur un chemin de 260 caractères. 8 transcripts subagents/ de sessions de sonde, listés par glob, illisibles ; avec le préfixe \\?\ : 0 illisible, +58 tours Haiku. Le préfixe manque à mesurer : laissé à CPT2, qui compte les sous-agents.
- 2026-09-23 : CPT2 : un sous-agent écrit un output_tokens provisoire (1, 2…) sur les lignes d'un tour avant la dernière, qui porte le compte final (144 cas sur 144, les 5 sous-agents de REP) : garder la dernière ligne est juste, et divergents y est bénin — la session n'en a aucun. Le préfixe \\?\ laissé par CPT1 est pris : 8 illisibles → 0 sur 96.
- 2026-09-23 : CPT4 : l'« avant » de REP4 (4 840 313) ne contenait pas la clôture : la page à son commit dit 20 355 080, la somme des quatre fiches ; la clôture était dans les 2 771 184 « à aucune fiche ». Le total d'une clôture ne compte plus la clôture en cours, faute de commit après la dernière fiche. Et cout arrondit session et sous-agents au centime chacun, pour que chaque ligne s'additionne : REP 20,63 → 20,61 $.
## Bilan
- Livré : vlp.py cout et la page coupent chaque session aux commits de fiche, sous-agents compris, avec une ligne hors fiches ; Opus 5.5 a son prix, une ligne ? $ se relit
- Surpris : l'« avant » de REP4 ne contenait pas la clôture, déjà « à aucune fiche » ; et le total d'une clôture ne compte plus la clôture en cours, faute de commit
