# Chantier courant — vlp (le kit Claude-vlpWorkflow)

> Fichier lu **en entier** par `/vlp:chantier` et `/vlp:tache`, depuis la racine du
> projet. C'est la seule table à tenir : rien à mettre à jour ailleurs quand un
> chantier s'ouvre ou se clôt. Garde-le court — vingt à trente lignes.
> Les libellés en gras se recopient **à l'identique** : ils sont lus tels quels.

- **alias** : vlp
- **kit** : ce dossier même — le projet est le kit. Chez znorr :
  C:/Users/znorr/Documents/ProgPerso/Claude-vlpWorkflow, lié dans ~/.claude/skills/vlp
- **contexte** : context AI/
- **méthode** : ${CLAUDE_PLUGIN_ROOT}/methode-chantier.md
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : aucun
- **artefact feuille de route** : https://claude.ai/code/artifact/ff1fc060-daca-486f-b4c6-e1f55114c0f7
- **artefact du chantier** : aucun
- **livraison** : aucune — le plugin est chargé en place ; `/reload-plugins` pour
  que la session en cours voie une modification
- **vérification** : geste de l'utilisateur — rejouer la commande modifiée sur un
  projet équipé, et regarder ce qu'elle fait

## Contraintes d'écriture

Les règles que toute fiche respecte, quel que soit son sujet.

- Une règle vit à un seul endroit : on la référence, on ne la recopie jamais
  (le kit a souffert de six copies divergentes).
- Une commande est autoportante : chaque étape nomme ce qu'elle ouvre, et rien
  d'autre.
- Tout ajout dans une commande se paye à chaque exécution : court, ou pas du tout.
- Le texte des commandes est en français.

## Chantiers clos — ne se rejouent pas

Ils ne servent plus qu'à relire un socle d'API, si une fiche y renvoie.

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| context AI/09-enchainer.md | E1..E8 (E7, E8 abandonnées) | 2026-09-10 | https://claude.ai/code/artifact/305e604c-23a1-4899-a3ad-37013b45ff4c |
| context AI/10-mesure.md | M1..M4 | 2026-09-11 | https://claude.ai/code/artifact/6736d2af-e88e-4e72-b485-d9dbef1951fa |

Lettres de fiche déjà prises : E (Enchaîner les fiches), M (Mesurer les tokens). Un nouveau chantier en choisit une autre —
elles ne se réemploient jamais, même après clôture. `/vlp:chantier` la propose,
l'utilisateur tranche ; c'est cette ligne qui rend le refus possible.
