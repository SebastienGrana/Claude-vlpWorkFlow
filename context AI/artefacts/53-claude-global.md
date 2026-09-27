# Le CLAUDE.md de l'utilisateur dans le sous-agent — notes et journal
## Lien
https://claude.ai/artifact/DNU51GksM3KyNWwZNMcZXt
## Résultat
Le poids du CLAUDE.md utilisateur dans un sous-agent est chiffré, et sa forme (résumé, jauge) comptée ; on agit seulement si ça coûte.
## Notes
- GLO1 : vlp.py forme : poids des instructions et forme du dernier message, par transcription
- GLO2 : la mesure sur tous les sous-agents, et le verdict au seuil de 5 % — dépend de GLO1
- GLO3 : une phrase dans les deux agents, ou « rien à faire » — dépend de GLO2
## Journal
## Bilan
- Livré : vlp.py forme mesure les CLAUDE.md et la forme de chaque sous-agent ; une phrase dans les deux agents : ton lecteur est le chef, pas l'humain
- Surpris : GLO1 a rendu FAITE sur case vide après un vrai renvoi du gardien : stop_hook_active laisse passer le second arrêt
