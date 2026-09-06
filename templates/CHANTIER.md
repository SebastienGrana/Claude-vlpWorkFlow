# Chantier courant — <nom du projet>

> Fichier lu **en entier** par `/chantier` et `/tache`, depuis la racine du
> projet. C'est la seule table à tenir : rien à mettre à jour ailleurs quand un
> chantier s'ouvre ou se clôt. Garde-le court — vingt à trente lignes.
> Les libellés en gras se recopient **à l'identique** : ils sont lus tels quels.

- **alias** : <md>
- **kit** : <~/Claude-vlpWorkflow — le dossier du kit, gabarits compris>
- **contexte** : <context AI/>
- **méthode** : <kit>/methode-chantier.md
- **chantiers possibles** : <context AI/08-etat.md>
- **fichier d'état** : <context AI/08-etat.md>
- **index** : <context AI/00-INDEX.md>
- **fichier de fiches courant** : aucun
- **artefact feuille de route** : <https://… — posé par /vlp-init>
- **artefact du chantier** : aucun
- **livraison** : <./deploy.sh — ou : aucune>
- **vérification** : <la commande que la session lance et lit elle-même — ou :
  le geste que seul l'utilisateur peut faire, et ce qu'il doit regarder>

## Contraintes d'écriture

Les règles que toute fiche respecte, quel que soit son sujet. Trois ou quatre,
pas quinze — celles qu'on regrette de ne pas avoir écrites.

- <Prose en français, code et commentaires de code en anglais.>
- <On édite `<dossier>`, jamais `<dossier généré>`.>
- <Aucun chemin absolu dans le code.>
- <Vérification d'API par grep dans `<fichier de référence>`.>

## Chantiers clos — ne se rejouent pas

Ils ne servent plus qu'à relire un socle d'API, si une fiche y renvoie.

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| <context AI/15-annulation.md> | <U1..U6> | <2026-09-04> | <https://…> |

Lettres de fiche déjà prises : <U>. Un nouveau chantier en choisit une autre —
elles ne se réemploient jamais, même après clôture. `/chantier` la propose,
l'utilisateur tranche ; c'est cette ligne qui rend le refus possible.
