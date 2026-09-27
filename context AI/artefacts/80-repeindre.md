# Repeindre une page sans recompter — notes et journal
## Résultat
Les 90 pages de chantiers clos (kit et Cairn) au format PLI, chiffres de coût inchangés, remises en ligne par lots ; les pages sans lien listées.
## Notes
- HAB1 : Test tester_forme : après --forme, total 11 262 523, hors 5 000 et coûts 1 111 / 2 222 identiques ; vlp.css lié, fiches repliées, bilan en haut, vigile PAGE SAINE ; --creer refusé ; mutant --forme ignoré → le test du total tombe ; pyright 0 erreur.
- HAB2 : Test tester_repeindre : 3 clos (2 anciens, 1 au format) → 2 repeintes · 0 avec lien · 2 sans lien · 0 refusées · 1 déjà ; relancé 0 repeintes ; --a-blanc 0 octet changé ; mutant sans filtre → tombe ; parcours commun clos_du_projet avec recompter. À blanc : kit 64 repeintes, 3 déjà, 1 sans page ; Cairn 17, 2 déjà. pyright 0.
- HAB3 : Test tester_liens : lien écrit/relit l'URL, reste du .md intact, URL inattendue refusée, liens pose A et signale un DOUBLON ; mutant texte_abri sans la section → tombe ; pyright 0. Réel : liens kit 67 écrits · 1 sans page ; Cairn 19 écrits (17 suivis par Git, 2 ignorés). repeindre --a-blanc : kit 64 avec lien · 0 sans lien · 3 déjà · 1 sans page ; Cairn 17 avec lien · 0 sans lien · 2 déjà. 0 doublon, Artifact list inutile.
- HAB4 : repeindre . : 64 repeintes · 64 avec lien · 0 sans lien · 0 refusées · 3 déjà · 1 sans page ; chiffres identiques 64/64 (154 coûts de fiche, 99 lignes total/hors), COMPARER 0 perdus 64/64, PAGE SAINE 64/64. Lot en ligne : 15 publiées, 0 arrêtée, 0 refusée (2 à la main, 13 par un sous-agent Sonnet) ; coût du lot 104 tours · ≈1,7M (1 681 848) · 4,60 $, soit 0,31 $/page ; sous-agent seul 56 tours · 2,13 $ = 0,16 $/page. Vu à l'œil : en local seulement (bilan en haut, fiches repliées, libellé abandonnée gardé) ; en ligne, écran de connexion : à regarder par l'utilisateur. Lots suivants : 13 pages par sous-agent.
- HAB5 : Les lots suivants du kit, taille fixée par HAB4.
- HAB6 : Cairn repeint et remis en ligne, rien de son contenu dans le kit ; dépend de HAB4.
## Journal
- 2026-09-27 : HAB4 : --forme garde aussi titres, libellés d'état, ligne de comptage et date de l'ancienne page ; sans cela, 64/64 pages perdaient leur date et 4 du texte (18-evals V2 abandonnée → en cours, 10-mesure, 11-conso, 14-bugs).
- 2026-09-27 : HAB4 : critère visuel non vu en ligne (la page claude.ai demande une connexion, jamais faite par Claude) ; vu en local, fiche cochée avec cette réserve, la nuit, pour ne pas bloquer HAB5 et HAB6 ; le format est celui des pages PLI déjà vues en ligne.
- 2026-09-27 : HAB4 : le lot passe par un sous-agent Sonnet (0,16 $/page, contexte principal épargné) ; lots suivants de 13 pages.
## Bilan
