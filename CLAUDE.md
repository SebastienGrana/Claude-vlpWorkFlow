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
- Clos le 2026-09-24 : le filet prévient le sous-agent après tout outil, échecs (PostToolUseFailure) et chemins longs compris ; « 3 tours restants » prouvé à plafond 10 après un Read et après un Bash à code non nul (chantier FIL).
- Clos le 2026-09-24 : le chef relit la case avant de commiter : cocher --verifier, RETOUR sur une case vide ; le sous-agent ne commite plus, écrit dans fiche.md, pas encore éprouvé (chantier CAS).
- Clos le 2026-09-24 : le contrôle avant commit ne se saute plus : sans claude dans le PATH, le hook prend le claude.exe de l'app et refuse un manifeste cassé ; 1,8 s par commit au lieu de 147 ms (chantier VAL).
- Clos le 2026-09-24 : chaque chantier ne compte que le sien, même quand une session en enchaîne plusieurs ; la première fiche se mesure avant son commit, et clore régénère les coûts de la page (chantier FIN).
- Clos le 2026-09-24 : ce que vlp.py écrit, il le relit : coût négatif, ligne close sous 1 000, lettres prises et résumé passent par leur lecteur dans un test ; 11 mutants (chantier TAR).

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
| jouer une fiche du chantier PLA (la plage des fiches suit le fichier) | `context AI/47-plage-suit.md` — chantier **ouvert**, par `/vlp:tache PLA<n>` |
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
