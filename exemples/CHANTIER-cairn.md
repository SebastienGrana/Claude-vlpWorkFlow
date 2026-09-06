# Chantier courant — cairn

> Exemple rempli, tiré du projet réel (library Python de lecture GBX).
> Vérification **scriptable** : la session lance la commande et lit sa sortie.
> Figé sur un chantier **ouvert**, pour montrer la ligne « fichier de fiches
> courant » remplie ; dans le projet réel elle vaut « aucun » depuis la clôture.

- **alias** : cairn
- **kit** : ~/Claude-vlpWorkflow
- **contexte** : context AI/
- **méthode** : context AI/21-methode-chantier.md
- **chantiers possibles** : context AI/20a-chantiers.md, puis context AI/10-etat.md
- **fichier d'état** : context AI/10-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : context AI/22-filet-non-regression.md (fiches `N1`..`N7`)
- **artefact feuille de route** : https://claude.ai/public/artifacts/<id>
- **artefact du chantier** : https://claude.ai/public/artifacts/<id>
- **livraison** : aucune
- **vérification** : lancer soi-même la commande du critère de fin de la fiche,
  et lire sa sortie — comptes bruts compris.

## Contraintes d'écriture

- Prose en français, code et commentaires de code en anglais.
- **Aucun chemin absolu dans le code** : `paths.py` résout à l'appel.
- La library lit, elle **n'écrit jamais** dans un fichier de jeu.
- Une mesure affiche ses **comptes bruts** à côté de son verdict.
- Aucune API n'est appelée de mémoire : elle se vérifie d'abord.

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| — | — | — | — |
