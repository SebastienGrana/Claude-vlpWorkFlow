# vlp (Claude-vlpWorkflow) — à lire en premier, en entier, et seul

Le kit « vlp » : un plugin Claude Code qui porte la méthode des chantiers et des
fiches. Il ne contient que des commandes en markdown, des gabarits et de la
doctrine — aucun code applicatif. Dépôt public :
https://github.com/SebastienGrana/Claude-vlpWorkFlow — cloné et utilisé en groupe.

## Où on en est — en cinq lignes

- Prouvé : le kit est un plugin (v3.1.0, « degré 3 »), chargé en place par un lien
  dans `~/.claude/skills/vlp` ; cinq commandes `/vlp:init`, `/vlp:chantier`,
  `/vlp:tache`, `/vlp:enchainer`, `/vlp:check`, et l'agent `vlp:fiche`.
- Équipés : Cairn-VlpLib, MapDecorator, ProjetONZSM, TrackGen — et ce kit lui-même.
- Clos le 2026-09-10, abandonné : enchaîner les fiches — le chef coûtait plus que
  les fiches jouées à la main. Remis tel quel le 2026-09-17, coût non corrigé.
- Clos le 2026-09-11 : mesurer les tokens consommés (chantier M) — script
  `scripts/mesure-tokens.py`, coût affiché en fin de fiche et à la clôture.
  Clos le 2026-09-17 : ce coût affiché sur toutes les pages (chantier C), puis
  compté par tour et pondéré en dollars (chantier T).
- Audité le 2026-09-17 : dix chantiers possibles dans la TODO de
  `context AI/08-etat.md`, preuves et détail dans `context AI/12-audit.md`.
  Clos le 2026-09-17 : ses bugs corrigés (chantier B), puis `/vlp:tache`
  allégée — carte injectée, 14 → 9 appels prescrits (chantier R) ; puis la
  mécanique dans `scripts/vlp.py`, `sed`/`awk` 11 → 1, 9 → 5 appels (chantier S) ;
  puis un hook `PostToolUse` valide les fichiers de fiches à l'écriture (chantier H) ;
  puis `claude plugin eval` : 3 cas sous Windows, `validate` avant commit (chantier V) ;
  puis la doctrine en trois docs, chaque seuil dans `vlp.py` (chantier D).

## Quatre règles non négociables

1. **Annoncer le plan en une ou deux phrases avant d'agir**, et poser un
   questionnaire au moindre choix ouvert.
2. **Mesurer avant de corriger — en tours et en coût pondéré, pas en lignes**,
   et afficher les comptes bruts à côté du verdict. Un gain sans mesure
   avant/après n'est pas un gain ; un instrument muet rend son propre échec
   indiagnosticable.
3. **Une règle vit à un seul endroit — un nombre aussi** (250, 80, 5…) : une
   commande renvoie à `cloture.md` ou à `methode-chantier.md`, elle ne les
   recopie pas ; ailleurs, on pointe.
4. **Le déterministe est un script, le jugement est de la prose.** Extraire,
   valider, régénérer, mesurer vivent dans `scripts/` — Python 3 sans
   dépendance, zéro appel modèle, testé : `vlp.py` porte la mécanique (ses
   sous-commandes sont dans sa docstring), `mesure-tokens.py` le coût — et une
   commande les appelle en un tour, elle ne décrit pas leur algorithme. Rien de propre à une machine dans
   `commands/`, `templates/` ni `scripts/` : un chemin passe par
   `${CLAUDE_PLUGIN_ROOT}`, **dans le texte des commandes et `hooks/hooks.json`
   seulement** — la
   variable n'existe ni dans le shell ni dans un fichier de données. Exception
   ouverte le 2026-09-10 pour le seul `mesure-tokens.py`, étendue à toute la
   mécanique le 2026-09-17 (audit, `context AI/12-audit.md`).

Prose en français, texte des commandes en français.

## Routage — ouvrir ceci, et rien d'autre

Cette table remplace la lecture de `00-INDEX.md`. Si la tâche n'y figure pas,
et seulement dans ce cas, ouvrir l'index.

| La tâche | Ouvrir |
|---|---|
| modifier une commande | `commands/<nom>.md` — celle-là seule |
| modifier le sous-agent ou le contrat de `/vlp:enchainer` | `agents/fiche.md`, ou `enchainement.md` |
| changer une règle de méthode | `methode-chantier.md`, ou `cloture.md` pour la clôture |
| savoir où vit quoi dans un projet équipé | `methode-chantier.md`, section « Où vit quoi » |
| toucher aux pages publiées | `ARTEFACTS.md`, puis le gabarit dans `templates/` |
| ouvrir un chantier, ou le découper en fiches | **lancer `/vlp:chantier`** |
| relire le chantier D (fusionner la doctrine) | `context AI/19-doctrine.md` — chantier **clos** |
| relire le chantier V (evals du plugin) | `context AI/18-evals.md` — chantier **clos**, V2 abandonnée (TODO n° 11) |
| relire le chantier H (hooks du kit) | `context AI/17-hooks.md` — chantier **clos** |
| relire le chantier S (un script `vlp.py` pour la mécanique) | `context AI/16-script.md` — chantier **clos** |
| relire le chantier R (réduire les tours de `/vlp:tache`) | `context AI/15-reduire.md` — chantier **clos** |
| relire le chantier B (corriger les bugs de l'audit) | `context AI/14-bugs.md` — chantier **clos** |
| relire le chantier T (compter les tours) | `context AI/13-tours.md` — chantier **clos** |
| relire le chantier E (enchaîner les fiches) | `context AI/09-enchainer.md` — chantier **clos**, abandonné puis remis tel quel |
| relire le chantier M (mesurer les tokens) | `context AI/10-mesure.md` — chantier **clos** |
| relire le chantier C (afficher la conso) | `context AI/11-conso.md` — chantier **clos** |
| reprendre après une longue interruption | `context AI/08-etat.md` |
| choisir le prochain chantier du kit, ou retrouver la preuve d'un bug relevé le 2026-09-17 | `context AI/12-audit.md` |

## Économie de contexte

La fenêtre sature par **densité de contexte**, pas par volume horaire. Donc,
dans cet ordre :

- **Un fichier de contexte ne s'ouvre que si la table ci-dessus le nomme.** Le
  voisin d'un fichier utile n'est pas utile ; il n'est que du volume.
- **Ne jamais lire le dossier de contexte en entier**, ni le README.
- **Une tâche, une session.** `/clear` entre deux tâches : une session laissée
  ouverte relit tout son passé à chaque tour.
- **Le coût est dans les tours, pas dans les lignes** (mesuré : une fiche =
  28–66 tours, la commande = 8 % du premier tour). Grouper les lectures en un
  appel, injecter la carte avant le premier tour, ne jamais retaper ce qu'un
  script régénère.
- **Explorer et lire avec un modèle léger**, garder le lourd pour ce qui décide.
- Grep ciblé plutôt que lecture de fichier entier, dans les commandes comme ici.
