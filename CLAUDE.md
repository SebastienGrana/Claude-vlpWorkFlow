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
- Clos le 2026-09-25 : les essais des 9 clos sans découpe, SAG et FIL entrent dans leur chiffre : +12 991 756 sur la feuille de route (chantier ESD).
- Clos le 2026-09-25 : la recompte s'arrête à l'appel clore : inscrit = recompté ; les republications sortent du coût (chantier APC).
- Clos le 2026-09-25 : la carte imprime la TODO et le format des fiches ; /vlp:chantier ne relit plus l'état en entier : 0,59 $ contre 1,14 $ avant (chantier LEC).
- Clos le 2026-09-26 : Clos le 2026-09-26 : /vlp:enchainer distingue refus de fiche et de copie, propose réécriture, rejeu, main ou arrêt (chantier ENC).
- Clos le 2026-09-26 : le relecteur ne voit plus la suite : carte --relecteur sans titres ni PROCHAINE= (chantier REL).

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
| jouer une fiche du chantier FFE (le relecteur ne lit plus le fichier de fiches entier) | `context AI/67-relecteur-sans-fichier.md` — chantier **ouvert**, par `/vlp:tache FFE<n>` |
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
