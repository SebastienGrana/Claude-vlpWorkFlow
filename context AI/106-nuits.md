# Les nuits — le plan du soir, la table des nuits, les leçons

QUAND LIRE : on prépare une nuit (plan du soir) ou on relit les nuits passées (table, leçons) ; `vlp.py trier` imprime les leçons.

| nuit | canal | chantier | jouées/acceptées/refusées | $ |
|---|---|---|---|---|
| 2026-10-08 | A | TAB | 2/1/1 | 5,26 |
| 2026-10-08 | B | APR | 1/0/0 | 2,13 |
| 2026-10-08 | B | BRA | 1/1/0 | 3,54 |
| 2026-10-09 | A | RTO | 1/1/0 | 3,94 |
| 2026-10-09 | B | CTR | 1/1/0 | 3,83 |
| 2026-10-09 | A | PRP | 4/4/0 | 11,09 |
| 2026-10-09 | A | EFF | 3/2/0 | 5,12 |

## Nuit 2026-10-08

Borne : 60 $ · 3 chantiers
Canal A · rang 1 · code TAB · préfixe TAB
Canal B · rang 1 · code APR · préfixe APR
Canal B · rang 2 · code BRA · préfixe BRA

### TAB
- canal A, seul : il touche scripts/vlp.py et scripts/test-vlp.py, qu'aucun chantier de B ne touche (Q1 : trois)
- estimé : 26 à 39 $, la cellule de la TODO ré-estimée à MET10 ; 4 fiches à 3,95 $ font ≈ 16 $ au taux du jour, non mesuré (Q3)
- découpage : TAB1 relever les lecteurs de tables de vlp.py qui tronquent ou jettent une ligne sans rien dire (relevé seul, au journal) ; TAB2 leur donner la garde de la TODO, une GARDE: au lieu d'une coupe muette, test et mutant — rien si TAB1 n'en trouve aucun, la fiche le note ; TAB3 clore lit la TODO avant sa première écriture (ex-CLV), test et mutant ; TAB4 vlp.py oter <projet> <code> --raison T [--date D] : retire la rangée de la TODO, sa phrase de provenance et date une ligne au journal, tout calculé avant d'écrire, .tmp puis os.replace, refuse un code absent, ouvert ou clos (GARDE:, sort 1), test et mutant (Q3 : quatre-fiches)

### APR
- canal B, premier : le tri ne le lie à TAB que par methode-chantier.md, où sa ligne n'écrit rien (Q1 : trois)
- estimé : 1 fiche, 4 à 12 $ (3,95 $ au taux du jour, × 1 à × 3), non mesuré (Q4)
- découpage : APR1 borner context AI/99-jnt1-mesure.py par date, le rejouer sur les seules sessions d'après la clôture de JNT (2026-09-29), écrire au journal les comptes avant / après et ce que JNT2 et JNT3 ont rapporté (Q4 : une-fiche)

### BRA
- canal B, second : il touche skills/chef/SKILL.md et le tri, rien de ce que TAB écrit hors de vlp.py ; même canal qu'APR pour ne pas ouvrir un troisième canal (Q1 : trois)
- estimé : 1 fiche, 4 à 12 $, non mesuré (Q5)
- découpage : BRA1 vlp.py trier refuse de trier hors de main, une GARDE: avant le tri, testée avec son mutant ; la section 0 de /vlp:chef renvoie à cette garde, et la vérification de branche de sa section 4 n'est plus recopiée (Q5 : script)

## Nuit 2026-10-09

Borne : 65 $ · 4 chantiers
Canal A · rang 1 · code RTO · préfixe RTO
Canal A · rang 2 · code PRP · préfixe PRP
Canal A · rang 3 · code EFF · préfixe EFF
Canal B · rang 1 · code CTR · préfixe CTR

### RTO
- canal A, premier : il touche scripts/vlp_coeur.py (clore) et cloture.md ; le plus petit des trois, et la clôture de PRP s'en sert la même nuit (Q1 : a-et-b)
- estimé : 1 fiche, 7,4 à 11 $, la cellule de la TODO ; ≈ 4 $ au taux du jour (3,99 $), non mesuré (Q3)
- découpage : RTO1 clore, qui lit déjà la TODO avant sa première écriture (TAB3), ôte la rangée de son code dans la même passe ; la phrase de provenance au-dessus de la table dit « <n>, `<code>`, clos le D. » ; pas d'entrée au journal en plus, la ligne d'archive de clore dit déjà la clôture ; le temps 1 de cloture.md renvoie au script ; test et mutant (Q3 : une-fiche)

### PRP
- canal A, second : il touche scripts/vlp_coeur.py (cout, recompter) comme RTO ; avant EFF, qui compte ses essais par vlp.py cout (Q1 : a-et-b)
- estimé : 4 fiches, 15 à 22 $, la cellule de la TODO avec la recopie fondue à la clôture de MET ; ≈ 16 $ au taux du jour, non mesuré (Q4)
- découpage : PRP1 relevé sans code, au journal : ce qu'ont tranché CPT, FIN, UNI, TAU et CAD sur la découpe, la cause de NUI20 à 2 tours · 0,16 $ (séance de 20:15 à 23:49 coupée par 7 commits d'autres chantiers) et celle de l'écart de TAB (5,26 $ au carnet, 11,71 $ à clore) ; PRP2 cout coupe aussi aux commits `<PRÉFIXE> :`, versés au « hors fiches », le total du chantier inchangé, test et mutant — si PRP1 montre qu'une décision passée l'interdit, la fiche le note et s'arrête ; PRP3 recompter --ecrire borné à un seul clos, qui récrit ses quatre copies (la ligne « Fait. » du fichier de fiches, la ZONE:bilan de sa page, l'abri .md, la ligne d'archive), test et mutant, l'outil seul : aucun vrai clos récrit cette nuit ; PRP4 corriger la cause de NUI20 ou de TAB si PRP1 la trouve dans le code, sinon la fiche le note et s'arrête (Q4 : quatre-fiches)

### EFF
- canal A, troisième : après PRP, qui change vlp.py cout, par lequel EFF compte ses essais (Q1 : a-et-b)
- estimé : 2 fiches la nuit, ≈ 8 $ au taux du jour, 7,4 à 11 $ (× 2 à × 3), non mesuré ; les essais en high (≈ 10 $, ≈ 1 h 45, estimés depuis MET4) se font de jour, hors de la borne (Q5)
- découpage : EFF1 trouver les 2 essais de VIT25 que cout ne compte pas (53 sur 55, ligne cout de VIT25), corriger si la cause est dans le code, test ; EFF2 mettre le juge de MET4 à l'abri dans le dépôt — met4-juge.py, ses résultats met4-resultats.jsonl et met4-tableau.py, dans le dossier scratchpad/met4 de la session 240bd893 (à trouver sous le dossier temporaire de claude par son id) — sans aucun chemin local (KIT et ESSAIS passés en arguments), lui apprendre le niveau high, essai --a-blanc sans appel modèle ; EFF3 (visuel) jouer les 4 fiches de MET4 en high aux mêmes mesures, écrire le tableau medium / high / xhigh au journal et la règle de l'effort dans methode-chantier.md — fiche de jour, avec l'utilisateur : une session de fiche de nuit est coupée à 60 min (boucle.py, TIMEOUT_S) et plafonnée à 5 $, et ses sessions filles hériteraient VLP_NUIT=1 et le carnet ; la nuit s'arrête sur elle et met EFF de côté (Q5 : prep-nuit)

### CTR
- canal B, seul : il touche scripts/vlp_coeur.py (les deux couleurs, ligne 4543) et scripts/test-vlp.py comme le canal A, loin des lignes de A (clore, cout, recompter) ; risque de conflit au matin sur test-vlp.py accepté (Q1 : a-et-b)
- estimé : 1 fiche, ≈ 4 $ au taux du jour, 4 à 12 $ (× 1 à × 3), non mesuré ; la cellule de la TODO, 11 à 17 $, comptait aussi la repeinte des vieilles pages (Q6)
- découpage : CTR1 les deux couleurs de scripts/vlp_coeur.py (COUTS_BARRE, COUTS_TEXTE ; la TODO cite la ligne 4300, elle est à 4543 le 2026-10-09) prises dans vlp.css : --cours pour les barres, --doux pour le texte, valeurs relues dans vlp.css ; contrastes recalculés par script (formule WCAG) sur --surface et --ground et notés au journal ; tests ; feuille de route et archive refaites, mises en attente pour le matin (la nuit ne publie pas) ; la repeinte des ≈ 88 vieilles pages de clos aux joints d'aujourd'hui n'est pas faite : une note --sorte reste pour le matin (Q6 : une-fiche)

## Leçons

Forme d'une leçon, écrite ici seul : `- <date> · N=<n> · <une cause, pas un constat> · <nombres nommés> · nuits <dates> · sessions <ids>`. N sous `LECON_INDICE` (`vlp.py`) : « indice ». Retirée, elle reste, suffixée `— retirée le <date> par <chantier ou nuit>`. Tenue deux nuits, proposée au matin, deux oui de l'utilisateur : elle monte. La colonne `$` est la somme des `usd_kit` du carnet.

- 2026-10-08 · N=4 · test-vlp.py hérite des VLP_NUIT, VLP_CARNET et VLP_CANAL de la session de nuit et sort rouge, ce qui bloque la case · 2 ÉCART par fiche, 4 fiches sur 4, 1 mise de côté (APR1) · nuits 2026-10-08 · sessions 3f47d6b9, 23bf8e86, 7905aed8, d07d8dca
- 2026-10-08 · N=4 · une session claude -p de nuit n'a pas l'outil Artifact, donc aucune page ne part en ligne · 3 pages de chantier, feuille de route et archive en attente · nuits 2026-10-08 · sessions d0a38db6, 3e7acc3d, a829c7ca, 2d385b79
- 2026-10-08 · N=1 · la fiche prescrivait la coupe d'une ligne de table sans le cas d'une ligne sans barre finale · 1 refus cause fiche, TAB2 mise de côté · nuits 2026-10-08 · sessions fa25bc3b
