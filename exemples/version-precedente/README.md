# La version précédente — table centrale, préfixe obligatoire

Ces deux fichiers sont les commandes telles qu'elles tournaient jusqu'au
2026-09-05, avant la migration vers `CHANTIER.md`. Elles portaient la table
« projet → dossier → fichier de fiches courant » **dans `tache.md` lui-même**,
et exigeaient l'alias du projet en premier argument (`/tache md R3`).

Gardées ici pour deux raisons : revenir en arrière si la détection par
`CHANTIER.md` décevait, et montrer à quoi ressemblait une table remplie.

Ce qui a changé :

| | Avant | Après |
|---|---|---|
| Où vit l'état d'un projet | table dans `~/.claude/commands/tache.md` | `CHANTIER.md` à la racine du projet |
| Alias de projet | obligatoire | seulement si le dossier courant est ambigu |
| Contraintes d'écriture | codées en dur dans `tache.md`, un bloc par projet | section de `CHANTIER.md` |
| Ajouter un projet | éditer les deux commandes | `/vlp-init` dans le projet |
