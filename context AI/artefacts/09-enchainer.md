# Enchaîner les fiches — notes et journal
## Résultat
Une nouvelle commande /vlp:enchainer joue les fiches non cochées du chantier courant l'une après l'autre, chacune dans un sous-agent neuf. Elle s'arrête dès qu'un retour humain est nécessaire, pose un questionnaire, puis reprend seule avec la réponse.
## Notes
- E1 : grep -c FICHE:S → 0 + 0 + 4 = 4 ; grep (visuel) → 1 ligne, 09-sable.md:59, dans S2.
- E2 : grep -c 'https://' sur 09-enchainer.md → 4 ; ligne frontmatter répond « Oui », URL à l'appui.
- E3 : Table Mesures remplie (lignes 58-64) → 0 « à mesurer (E3) », 1 « à mesurer » (E7).
- E4 : enchainement.md, argument enchaine, marque « (visuel) » · dépend de E3
- E5 : /vlp:enchainer bac à sable : plan « je joue S2, arrêt prévu à S2 (visuel) », joue S2, s'arrête sur RETOUR (b.txt écrit) — S3/S4 non joués.
- E6 : Bac à sable : questionnaire posé à S2, « oui » → case cochée, reprise ; S3 bloqué (2 tentatives, ls: cannot access), S4 jamais lancé (dépend de S3) — 143,5k tokens pour S2+S3.
- E7 : Non faite. Sous-agent vlp:fiche : S1 12 965, S2 13 163, S3 15 830 tokens — mais le chef coûte ~70k de socle et ~12 appels par fiche.
- E8 : Non faite : la commande est retirée du kit, il n'y a rien à publier.
## Journal
- 2026-09-10 : E1 : /vlp:init publie une feuille de route, E1 l'interdisait ; la fiche l'a emporté, le bac à sable n'a aucune page (à retenir pour E7).
- 2026-09-10 : E3 : allowed-tools du frontmatter ne contraint pas l'exécution rejouée via Skill dans un sous-agent (une commande Bash hors liste passe sans refus) — contredit la doc lue en E2 ; à retenir pour E4-E6.
- 2026-09-10 : E6 : run complet mesuré à 143,5k tokens pour S2+S3 seuls ; l'utilisateur juge cette consommation inacceptable — coût central à traiter en E7, pas seulement à mesurer.
- 2026-09-10 : E7 : sous-agents à ~13k par fiche, mais le chef (socle de session ~70k, ~12 appels par fiche) rend l'enchaînement plus cher que le jeu manuel ; chantier abandonné et clos.
## Bilan
- Livré : la marque (visuel) des critères de fin, et une mesure fiable du coût. Retirés du kit : /vlp:enchainer, l'agent fiche, le contrat de retour et le mode enchaine. E7 et E8 ne sont pas faites.
- Surprise : le coût ne vient pas des sous-agents (~9k au départ) mais du chef, une session principale qui part de ~70k tokens et relit ce socle à chaque appel. subagent_tokens mesure le dernier tour, pas un cumul.
