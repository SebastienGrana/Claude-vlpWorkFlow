# vlp (Claude-vlpWorkflow) — à lire en premier, en entier, et seul

Le kit « vlp » : un plugin Claude Code qui porte la méthode des chantiers et des
fiches. Il ne contient que des commandes en markdown, des gabarits et de la
doctrine — aucun code applicatif. Dépôt public :
https://github.com/SebastienGrana/Claude-vlpWorkFlow — cloné et utilisé en groupe.

## Où on en est — en cinq lignes

- Prouvé : le kit est un plugin (« degré 3 », version dans `.claude-plugin/plugin.json`),
  chargé en place par un lien dans `~/.claude/skills/vlp` ; cinq commandes `/vlp:init`,
  `/vlp:chantier`, `/vlp:tache`, `/vlp:enchainer`, `/vlp:check`, et l'agent `vlp:fiche`.
- Équipés : Cairn-VlpLib, MapDecorator, ProjetONZSM, TrackGen — et ce kit lui-même.
- Chaque chantier clos a sa ligne dans `context AI/00-INDEX.md`, son détail daté dans
  `context AI/08-etat.md` ; ici, les derniers seulement (`vlp.py clore` les tient).
- Clos le 2026-09-24 : mesure-tokens.py se borne en ligne de commande : --plage DEBUT FIN, heures ISO ou commits, une borne illisible sort 1 ; une docstring ; 7 mutants, et MTK1 a écrit ses tests après le code (chantier MTK).
- Clos le 2026-09-24 : un cadrage joué dans sa propre session compte : ouvrir note sa session en tête, cout et la page la mesurent hors fiches ; 9 mutants, et le sous-agent a commité au 80e appel, case vide (chantier CAD).
- Clos le 2026-09-24 : un vieux chantier ne se recompte plus à zéro : sans commit de fiche, vlp.py cout et la page retombent sur ses sessions entières et le disent ; les dix touchés retrouvent leur sortie d'avant la nuit (chantier ZER).
- Clos le 2026-09-25 : chaque FAITE d'/vlp:enchainer est relu avant son commit par un relecteur neuf : trois motifs refusent, un soupçon se rejoue, la sonde va au-delà du critère ; 4 verdicts justes sur 4 sur les témoins de la nuit, 0,50 $ la relecture (chantier REV).
- Clos le 2026-09-25 : un sous-agent vlp:fiche ne commite plus : vlp.py gardien refuse git sur PreToolUse et renvoie sur SubagentStop un statut absent ou une case vide ; HEAD 60ef683 intact sur le témoin, 6,83 $ (chantier CON).

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
   `skills/`, `templates/` ni `scripts/` : un chemin passe par
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
| modifier une commande | `skills/<nom>/SKILL.md` — celle-là seule |
| modifier le sous-agent ou le contrat de `/vlp:enchainer` | `skills/jouer/SKILL.md`, `agents/fiche.md`, ou `enchainement.md` |
| changer une règle de méthode | `methode-chantier.md`, ou `cloture.md` pour la clôture |
| savoir où vit quoi dans un projet équipé | `methode-chantier.md`, section « Où vit quoi » |
| toucher aux pages publiées | `ARTEFACTS.md`, puis le gabarit dans `templates/` |
| ouvrir un chantier, ou le découper en fiches | **lancer `/vlp:chantier`** |
| jouer une fiche du chantier GLO (le CLAUDE.md de l'utilisateur dans le sous-agent) | `context AI/53-claude-global.md` — chantier **ouvert**, par `/vlp:tache GLO<n>` |
| relire un chantier clos | `context AI/00-INDEX.md` — sa ligne y nomme le fichier de fiches |
| reprendre après une longue interruption | `context AI/08-etat.md` |
| choisir le prochain chantier du kit, ou retrouver la preuve d'un bug relevé le 2026-09-17 | `context AI/12-audit.md` |
| expliquer le kit, ou citer un gain chiffré | `context AI/35-bilan.md` |

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
