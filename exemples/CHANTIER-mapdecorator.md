# Chantier courant — MapDecorator

> Exemple rempli, tiré du projet réel (plugin Openplanet, ManiaScript).
> Vérification **visuelle** : seul l'utilisateur voit le jeu.
> Figé sur un chantier **ouvert**, pour montrer la ligne « fichier de fiches
> courant » remplie ; dans le projet réel elle vaut « aucun » depuis la clôture.

- **alias** : md
- **contexte** : context AI/
- **méthode** : context AI/09-chantiers.md
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : context AI/18-detection-piste.md (fiches `R1`..`R5`)
- **artefact feuille de route** : https://claude.ai/public/artifacts/<id>
- **artefact du chantier** : https://claude.ai/public/artifacts/<id>
- **livraison** : ./deploy.sh
- **vérification** : l'utilisateur recharge le plugin dans le jeu (F3 → Reload)
  et répond ; ensuite seulement, lire
  `tail -n 120 "C:/Users/<utilisateur>/Openplanet4/Openplanet.log" | grep -iE "MapDecorator|ERROR|WARN"`

## Contraintes d'écriture

- Prose en français, libellés et commentaires de code en anglais.
- On édite `files/`, **jamais** `Openplanet4/Plugins/MapDecorator/`.
- Un contrôle grisé **affiche toujours sa raison**.
- Les blocs d'une carte s'énumèrent par `pluginMap.Map.Blocks`, **jamais**
  `pluginMap.Blocks`, qui fait crasher le jeu.
- Vérification d'API par grep dans
  `C:/Users/<utilisateur>/Openplanet4/OpenplanetCore.json`. Le socle déjà vérifié est
  dans `sed -n '/^## Le socle commun/,/^## L.état/p' mockups/TACHES-UI.md` —
  ne pas le regreper.

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| mockups/TACHES-UI.md | `T*` | avant 2026-09-04 | — (antérieur aux artefacts) |
| context AI/15-annulation.md | `U*` | avant 2026-09-04 | — (antérieur aux artefacts) |
