# vlp (Claude-vlpWorkflow) — à lire en premier, en entier, et seul

Le kit « vlp » : un plugin Claude Code qui porte la méthode des chantiers et des
fiches. Il ne contient que des commandes en markdown, des gabarits et de la
doctrine — aucun code applicatif. Dépôt public :
https://github.com/SebastienGrana/Claude-vlpWorkFlow — cloné et utilisé en groupe.

## Où on en est — en cinq lignes

- Prouvé : le kit est un plugin (v3.0.0, « degré 3 »), chargé en place par un lien
  dans `~/.claude/skills/vlp` ; quatre commandes `/vlp:init`, `/vlp:chantier`,
  `/vlp:tache`, `/vlp:check`.
- Équipés : Cairn-VlpLib, MapDecorator, ProjetONZSM, TrackGen — et ce kit lui-même.
- Clos le 2026-09-10, abandonné : enchaîner les fiches — le chef coûtait plus que
  les fiches jouées à la main.
- Clos le 2026-09-11 : mesurer les tokens consommés (chantier M) — script
  `scripts/mesure-tokens.py`, coût affiché en fin de fiche et à la clôture.
- Détail daté dans `context AI/08-etat.md`.

## Quatre règles non négociables

1. **Annoncer le plan en une ou deux phrases avant d'agir**, et poser un
   questionnaire au moindre choix ouvert.
2. **Mesurer avant de corriger**, et afficher les comptes bruts à côté du
   verdict — un instrument muet rend son propre échec indiagnosticable.
3. **Une règle vit à un seul endroit** : une commande renvoie à `cloture.md` ou à
   `methode-chantier.md`, elle ne les recopie pas.
4. **Rien de propre à une machine dans `commands/` ni `templates/`** : le dépôt
   est cloné par d'autres ; un chemin passe par `${CLAUDE_PLUGIN_ROOT}`. Seule
   exception, assumée : `scripts/` à la racine du kit, réservé à l'outil de
   mesure de tokens — zéro appel modèle, seulement du parsing local de
   transcripts JSONL. Décidé le 2026-09-10, après l'abandon du chantier E
   faute d'instrument pour chiffrer son propre coût. Ce n'est pas un
   relâchement général : `commands/` et `templates/` restent interdits au code
   applicatif.

Prose en français, texte des commandes en français.

## Routage — ouvrir ceci, et rien d'autre

Cette table remplace la lecture de `00-INDEX.md`. Si la tâche n'y figure pas,
et seulement dans ce cas, ouvrir l'index.

| La tâche | Ouvrir |
|---|---|
| modifier une commande | `commands/<nom>.md` — celle-là seule |
| changer une règle de méthode | `methode-chantier.md`, ou `cloture.md` pour la clôture |
| savoir où vit quoi dans un projet équipé | `CONVENTION-FICHIERS.md` |
| toucher aux pages publiées | `ARTEFACTS.md`, puis le gabarit dans `templates/` |
| ouvrir un chantier, ou le découper en fiches | **lancer `/vlp:chantier`** |
| jouer une fiche `<X>*` | `context AI/<NN>-<chantier>.md` — chantier **ouvert** |
| relire le chantier E (enchaîner les fiches) | `context AI/09-enchainer.md` — chantier **clos**, abandonné |
| relire le chantier M (mesurer les tokens) | `context AI/10-mesure.md` — chantier **clos** |
| reprendre après une longue interruption | `context AI/08-etat.md` |

## Économie de contexte

La fenêtre sature par **densité de contexte**, pas par volume horaire. Donc,
dans cet ordre :

- **Un fichier de contexte ne s'ouvre que si la table ci-dessus le nomme.** Le
  voisin d'un fichier utile n'est pas utile ; il n'est que du volume.
- **Ne jamais lire le dossier de contexte en entier**, ni le README.
- **Une tâche, une session.** `/clear` entre deux tâches : une session laissée
  ouverte relit tout son passé à chaque tour.
- **Explorer et lire avec un modèle léger**, garder le lourd pour ce qui décide.
- Grep ciblé plutôt que lecture de fichier entier, dans les commandes comme ici.
