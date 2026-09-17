# Chantier courant — vlp (le kit Claude-vlpWorkflow)

> Fichier lu **en entier** par `/vlp:chantier` et `/vlp:tache`, depuis la racine du
> projet. C'est la seule table à tenir : rien à mettre à jour ailleurs quand un
> chantier s'ouvre ou se clôt. Garde-le court — vingt à trente lignes.
> Les libellés en gras se recopient **à l'identique** : ils sont lus tels quels.

- **alias** : vlp
- **kit** : ce dossier même — le projet est le kit. Chez znorr :
  C:/Users/znorr/Documents/ProgPerso/Claude-vlpWorkflow, lié dans ~/.claude/skills/vlp
- **contexte** : context AI/
- **méthode** : methode-chantier.md, à la racine du kit — il voyage avec le plugin
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : context AI/27-wsl.md (W1..W2)
- **artefact feuille de route** : https://claude.ai/code/artifact/ff1fc060-daca-486f-b4c6-e1f55114c0f7
- **artefact du chantier** : https://claude.ai/artifact/BTzA23mPmYQKAnUvT1Pkpd
- **livraison** : aucune — le plugin est chargé en place ; `/reload-plugins` pour
  que la session en cours voie une modification
- **vérification** : geste de l'utilisateur — rejouer la commande modifiée sur un
  projet équipé, et regarder ce qu'elle fait

## Contraintes d'écriture

Les règles que toute fiche respecte, quel que soit son sujet.

- Une règle vit à un seul endroit — un nombre aussi : on la référence, on ne la
  recopie jamais (le kit a souffert de six copies divergentes).
- Une commande est autoportante : chaque étape nomme ce qu'elle ouvre, et rien
  d'autre. Elle ne découpe jamais une autre commande au `sed` : ce qui est
  partagé vit dans un fichier ou un script commun.
- Le déterministe s'écrit dans `scripts/`, testé, et la commande l'appelle en
  un tour ; la prose ne décrit pas un algorithme.
- Tout ajout dans une commande se paye à chaque exécution : court, ou pas du tout.
- `$ARGUMENTS` sur une ligne à lui ; jamais `$1` ni `$2` dans la prose — ils
  sont substitués avant que le modèle lise.
- Le texte des commandes est en français ; chemins en barres obliques, jamais
  un chemin de machine.

## Chantiers clos — ne se rejouent pas

Ils ne servent plus qu'à relire un socle d'API, si une fiche y renvoie.

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| context AI/09-enchainer.md | E1..E8 (E7, E8 abandonnées) | 2026-09-10 | https://claude.ai/code/artifact/305e604c-23a1-4899-a3ad-37013b45ff4c |
| context AI/10-mesure.md | M1..M4 | 2026-09-11 | https://claude.ai/code/artifact/6736d2af-e88e-4e72-b485-d9dbef1951fa |
| context AI/11-conso.md | C1..C2 | 2026-09-17 | https://claude.ai/code/artifact/b72f8b89-f4c3-4cb1-aa35-344efd08ea23 |
| context AI/13-tours.md | T1..T5 | 2026-09-17 | https://claude.ai/artifact/G7oHVSDZnVJdYXiEPD63CU |
| context AI/14-bugs.md | B1..B3 | 2026-09-17 | https://claude.ai/artifact/NSx145qiALVfwmHc57Yrdq |
| context AI/15-reduire.md | R1..R4 | 2026-09-17 | https://claude.ai/artifact/CWC5awkprtgXwgyyP1CoeC |
| context AI/16-script.md | S1..S5 | 2026-09-17 | https://claude.ai/artifact/MDYKgdDhAKsPJE4cp1TK6u |
| context AI/17-hooks.md | H1..H4 | 2026-09-17 | https://claude.ai/artifact/MTMEspegQa2HCZxww8Tqfq |
| context AI/18-evals.md | V1..V4 (V2 abandonnée) | 2026-09-17 | https://claude.ai/artifact/HuzF1uSZeEvW89uUaoGS5e |
| context AI/19-doctrine.md | D1..D6 | 2026-09-17 | https://claude.ai/artifact/Pnfr1vfuHWiqM4XHuFP8Eh |
| context AI/20-init.md | I1..I3 | 2026-09-17 | https://claude.ai/artifact/8p27CpH1GuMgtE9ECWcwoj |
| context AI/21-skills.md | K1..K3 | 2026-09-17 | https://claude.ai/artifact/SnRg17z3ojPU3jTk9pQpD7 |
| context AI/22-fork.md | N1..N3 | 2026-09-17 | https://claude.ai/artifact/PF7Ud3UWBNAdytYTs1yV7D |
| context AI/23-alleger.md | L1..L3 | 2026-09-17 | https://claude.ai/artifact/Y4gMbrQmjNSpxCsDKiTxrq |
| context AI/24-lanceur.md | P1..P3 | 2026-09-17 | https://claude.ai/artifact/UdhUqFegfkke1gimdbSELv |
| context AI/25-arret.md | A1..A2 | 2026-09-17 | https://claude.ai/artifact/Q3xC4KRxoecmTC9SfRTowB |
| context AI/26-gitbash.md | G1..G2 | 2026-09-17 | https://claude.ai/artifact/UWhqsTpQNUmwnztwz85auy |

Lettres de fiche déjà prises : E (Enchaîner les fiches), M (Mesurer les tokens), C (Afficher la conso), T (Compter les tours), B (Corriger les bugs de l'audit), R (Réduire les tours de `/vlp:tache`), S (Un script `vlp.py` pour la mécanique), H (Hooks du kit), V (Evals du plugin), D (Fusionner la doctrine), I (Un projet neuf qui ne ment pas), K (Migrer `commands/` → `skills/`), N (`/vlp:enchainer` : réparer ou retirer), L (`/vlp:enchainer` : alléger le chef), P (Un lanceur Python sans accolade), A (Une fiche visuelle arrête `/vlp:enchainer`), G (Le kit sans Git Bash), W (Evals sous WSL2). Un nouveau chantier en choisit une autre —
elles ne se réemploient jamais, même après clôture. `/vlp:chantier` la propose,
l'utilisateur tranche ; c'est cette ligne qui rend le refus possible.
