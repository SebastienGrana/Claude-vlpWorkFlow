# Index du contexte vlp

**`CLAUDE.md`, à la racine, est le fichier d'entrée** : il porte l'identité du
projet, l'état en cinq lignes, les règles, et une table « tâche → fichier » qui
suffit dans presque tous les cas. Cet index-ci ne sert que lorsque la tâche n'y
figure pas.

Un fichier = un sujet. **Ne charger que ce que la tâche demande.**
Chaque fichier s'ouvre sur une ligne « QUAND LIRE » : elle seule décide. Si
elle ne décrit pas la tâche en cours, le fichier n'est pas à ouvrir, même s'il
a l'air proche.

## Stable — ce qui ne bouge presque plus

| Fichier | Lire quand |
|---|---|
| `08-etat.md` | on reprend après une interruption, ou on choisit quoi faire ensuite |
| `12-audit.md` | on choisit le prochain chantier du kit, ou on cherche la preuve d'un bug ou d'une mesure de l'audit du 2026-09-17 |
| `38-audit-artefacts.md` | on choisit un chantier sur les pages publiées (six proposés, A à F), ou on cherche la preuve d'un défaut de page relevé le 2026-09-22 ; ses scripts sont dans `38-audit-scripts/`, sa page dans `artefacts/` |
| `39-reparer-pages.md` | on relit le socle du chantier REP — **clos** « Réparer les pages publiées », `REP1..REP4` |
| `40-cout-juste.md` | on relit le socle du chantier CPT — **clos** « Un coût juste, fiche par fiche et sous-agents compris », `CPT1..CPT4` |
| `41-plafond-sous-agent.md` | on relit le socle du chantier SAG — **clos** « Le sous-agent ne bute plus sur 30 tours », `SAG1..SAG5` |
| `42-filet-tout-outil.md` | on relit le socle du chantier FIL — **clos** « Le filet tire après tout outil », `FIL1..FIL3` |
| `43-case-relue.md` | on relit le socle du chantier CAS — **clos** « Le chef relit la case avant de commiter », `CAS1..CAS2` |
| `44-pre-commit.md` | on relit le socle du chantier VAL — **clos** « Le contrôle avant commit ne se saute plus », `VAL1..VAL1` |
| `45-cout-aux-bords.md` | on relit le socle du chantier FIN — **clos** « Le coût juste, aux deux bords du chantier », `FIN1..FIN3` |
| `46-aller-retour.md` | on relit le socle du chantier TAR — **clos** « Ce que vlp.py écrit, il le relit », `TAR1..TAR3` |
| `47-plage-suit.md` | on relit le socle du chantier PLA — **clos** « La plage des fiches suit le fichier », `PLA1..PLA2` |
| `48-mesure-plage.md` | on relit le socle du chantier MTK — **clos** « mesure-tokens.py se lit et se borne en ligne de commande », `MTK1..MTK2` |
| `49-cadrage-compte.md` | on relit le socle du chantier CAD — **clos** « Le cadrage compte dans le coût du chantier », `CAD1..CAD1` |
| `50-zero-muet.md` | on relit le socle du chantier ZER — **clos** « Un vieux chantier ne se recompte plus à zéro », `ZER1..ZER1` |
| `51-relecture.md` | on relit le socle du chantier REV — **clos** « Relire chaque fiche avant son commit », `REV1..REV4` |
| `52-contrat-sortie.md` | on relit le socle du chantier CON — **clos** « Le contrat du sous-agent, vérifié à sa sortie », `CON1..CON5` |
| `53-claude-global.md` | on relit le socle du chantier GLO — **clos** « Le CLAUDE.md de l'utilisateur dans le sous-agent », `GLO1..GLO3` |
| `54-gardien-renvoie.md` | on relit le socle du chantier GAR — **clos** « Le gardien renvoie pour de vrai », `GAR1..GAR3` |
| `55-un-chiffre.md` | on relit le socle du chantier UNI — **clos** « Un seul chiffre par clôture », `UNI1..UNI2` |
| `56-hook-une-fois.md` | on relit le socle du chantier PYT — **clos** « Un hook n'agit qu'une fois », `PYT1..PYT2` |
| `57-gardien-relecteur.md` | on relit le socle du chantier RLG — **clos** « Le gardien derrière le relecteur », `RLG1..RLG1` |
| `58-forme-sous-agent.md` | on relit le socle du chantier FOR — **clos** « La forme du sous-agent, pour de vrai », `FOR1..FOR3` |
| `59-juger-fin.md` | on relit le socle du chantier JUG — **clos** « Le gardien ne juge que la fin du message », `JUG1..JUG3` |
| `35-bilan.md` | on doit expliquer le kit — d'où il vient, ce qu'il sait faire aujourd'hui, ce qu'il ne promet pas ; les 22 chantiers chiffrés |
| `36-gardes.md` | on relit le socle du chantier Z — **clos** « Une GARDE au lieu d'un traceback », `Z1..Z4` |
| `37-niveau.md` | on relit le socle du chantier NIV — **clos** « Remettre les projets équipés à niveau », `NIV1..NIV4` |
| *(racine du kit)* `methode-chantier.md` | on ouvre un chantier, ou on le découpe en fiches — ici le projet **est** le kit, la méthode est donc à la racine |

## Chantiers — un fichier de fiches par chantier

| Fichier | Lire quand |
|---|---|
| `09-enchainer.md` | on joue une fiche `E*` — chantier **clos**, abandonné, « Enchaîner les fiches » ; commande remise telle quelle le 2026-09-17 |
| `10-mesure.md` | on joue une fiche `M*` — chantier **clos** « Mesurer les tokens », `M1..M4` |
| `11-conso.md` | on joue une fiche `C*` — chantier **clos** « Afficher la conso sur toutes les pages », `C1..C2` |
| `13-tours.md` | on joue une fiche `T*` — chantier **clos** « Compter les tours, pondérer le coût », `T1..T5` |
| `14-bugs.md` | on joue une fiche `B*` — chantier **clos** « Corriger les bugs de l'audit », `B1..B3` |
| `15-reduire.md` | on joue une fiche `R*` — chantier **clos** « Réduire les tours de `/vlp:tache` », `R1..R4` |
| `16-script.md` | on joue une fiche `S*` — chantier **clos** « Un script `vlp.py` pour la mécanique », `S1..S5` |
| `17-hooks.md` | on joue une fiche `H*` — chantier **clos** « Hooks du kit », `H1..H4` |
| `18-evals.md` | on joue une fiche `V*` — chantier **clos** « Evals du plugin », `V1..V4` |
| `19-doctrine.md` | on joue une fiche `D*` — chantier **clos** « Fusionner la doctrine », `D1..D6` |
| `22-fork.md` | on relit le socle du chantier N — **clos** « `/vlp:enchainer` : réparer ou retirer », `N1..N3` |
| `23-alleger.md` | on relit le socle du chantier L — **clos** « `/vlp:enchainer` : alléger le chef », `L1..L3` |
| `24-lanceur.md` | on relit le socle du chantier P — **clos** « Un lanceur Python sans accolade », `P1..P3` |
| `26-gitbash.md` | on relit le socle du chantier G — **clos** « Le kit sans Git Bash », `G1..G2` |
| `27-wsl.md` | on relit le socle du chantier W — **clos** « Evals sous WSL2 », `W1..W2` |
| `28-sans-sh.md` | on relit le socle du chantier X — **clos** « Le kit sans sh », `X1..X3` |
| `29-feuille.md` | on relit le socle du chantier F — **clos** « La feuille de route par script », `F1..F4` |
| `30-ouvrir.md` | on relit le socle du chantier O — **clos** « Ouvrir et clore par script », `O1..O5` |
| `31-jauge.md` | on relit le socle du chantier J — **clos** « Des fichiers de tête qui ne grossissent plus », `J1..J4` |
| `32-sans-git.md` | on relit le socle du chantier Y — **clos** « Le kit entier sans sh », `Y1..Y5` |
| `33-sans-refus.md` | on relit le socle du chantier U — **clos** « /vlp:tache sans refus sous PowerShell », `U1..U5` |
| `34-agent-sans-git.md` | on relit le socle du chantier Q — **clos** « /vlp:enchainer sans Git », `Q1..Q5` |
| `25-arret.md` | on relit le socle du chantier A — **clos** « Une fiche visuelle arrête `/vlp:enchainer` », `A1..A2` |
| `21-skills.md` | on relit le socle du chantier K — **clos** « Migrer commands/ → skills/ », `K1..K3` |
| `20-init.md` | on joue une fiche `I*` — chantier **clos** « Un projet neuf qui ne ment pas », `I1..I3` |

## Le kit lui-même — à la racine, hors de ce dossier

Ces fichiers ne se lisent pas en série : chacun répond à une question précise.

| Fichier | Lire quand |
|---|---|
| `skills/<nom>/SKILL.md` | on modifie cette commande-là |
| `agents/fiche.md`, `enchainement.md` | on touche au sous-agent de `/vlp:enchainer`, ou à son contrat de retour |
| `scripts/mesure-tokens.py` | on touche à la mesure des tokens |
| `scripts/vlp.py` | on touche à la mécanique des commandes — carte, extraction, validation, page, hook ; ses sous-commandes sont dans sa docstring |
| `skills/tache/references/` | on touche au blocage, à la page de chantier ou aux trois contraintes d'une fiche |
| `cloture.md` | on touche aux cinq écritures d'une clôture |
| `ARTEFACTS.md` | on touche aux pages publiées : nommage, URL, budget |
| `README.md` | on change la mise en place, ou la présentation du kit |
