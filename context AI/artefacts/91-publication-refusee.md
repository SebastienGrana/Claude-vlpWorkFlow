# Une publication refusée n'arrête plus le chantier — notes et journal
## Lien
https://claude.ai/artifact/KF3UyEHa475AaJ317E6LFm
## Résultat
Une page refusée par la limite du jour attend dans une liste et part plus tard, sans bloquer ni case ni clôture ; on la relit en local, sans cache, en largeur téléphone.
## Notes
- LOC1 : 4 résultats Artifact en 429 sur 223 occurrences brutes hors session (269 avec) ; événement PostToolUseFailure, champ error ; cause du blocage : prompt et critère (visuel) de BTN6 ; VALIDE
- LOC2 : suite OK (exit 0) ; 5 mutants tombent, témoin OK ; pyright 0 erreur ; hook essayé en sous-processus : proposition 02:00 / 02:10 une fois
- LOC3 : titre 1 (ARTEFACTS.md:92) ; renvois grep -o : ARTEFACTS 1, cloture 1, chantier 2, tache 1, tache-page 1, init 1 ; phrase d'échec restante seulement hors refus (liste au compte rendu) ; renvois : 0 nouvel avertissement (CLAUDE.md 81/80 déjà là, non touché) ; test-vlp.py : OK code 0
- LOC4 : suite OK (grep -c 'verifier(' : 576 → 593, +17 contrôles), pyright 0 erreur avant et après, 3 mutants tombent (en-tête no-store retiré, check-ignore ignoré, remplacer = ajouter), git ls-files .claude/ = 0 ligne, servir lancé pour de vrai : 200, Cache-Control: no-store, cadre 375 px
- LOC5 : Liste 0 → 0 après refus « non lue » (et « joints non lus »), 0 → 1 → 0 par le hook seul à la republication (v8) ; aperçu /_telephone à 375 px, --ground #f6efdf → #ff9ecf visible au rechargement, vlp.css rendu (sha 60bbbfc4…, 11 066 octets, git diff --stat vide) ; vrai 429 non essayé (test de LOC2 seul) ; vu par l'utilisateur
## Journal
- 2026-09-29 : LOC2 : la liste ne tient que les pages sous artefacts/ ; les pages Cairn du scratchpad (3 refus du 2026-09-27) n'y entrent pas, le hook se tait ; le champ error est à vérifier en vrai par LOC5
## Bilan
- Livré : la liste d'attente des pages refusées (attente ajouter/lister/retirer/hook, hooks sur Artifact), sa règle dans ARTEFACTS.md et l'aperçu local sans cache (apercu, /_telephone à 375 px), essayés pour de vrai
- Surpris : attente lister prend le dossier context AI/artefacts et non la racine ; un second refus (joints non lus) est venu sans toucher la liste ; le vrai 429 n'a pas été essayé
- Estimé : estimé 1 fiches ≈2,97 $ · cadré 5 · joué 5 fiches 11,74 $
