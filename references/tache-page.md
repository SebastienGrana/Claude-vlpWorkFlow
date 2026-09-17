<!-- Lu par /vlp:tache (étape 1) et /vlp:enchainer (étape 4). -->

# Régénérer l'artefact du chantier

La page dérive du fichier de fiches, jamais l'inverse : c'est
`scripts/vlp.py page` qui la réécrit — états, avancement, comptage, coûts des
lignes `**Session**`, date. Tu ne retouches pas son HTML à la main. Son URL est
dans la ligne « **artefact du chantier** » de `CHANTIER.md`.

Ce qui reste de ton jugement tient en deux options :

- `--note <fiche> "<texte>"` : le **critère de fin constaté**, une ligne,
  comptes bruts compris ;
- `--journal "<texte>"` : seulement si la fiche a tranché quelque chose
  d'imprévu — la **même ligne** que celle ajoutée au fichier d'état.

Lis sa sortie. Une `GARDE:` : une session non mesurée, ou une page au-delà du
seuil — dis-le en une ligne. Une sortie non nulle : la page n'est pas écrite,
dis-le et continue, le fichier de fiches est à jour.

Puis publie, si la session n'a ni publié ni lu cette page : d'abord `Artifact`
`action: "read"` sur l'`url` — sans lecture, la publication est refusée, et
refusée encore au second essai. Si la version lue dit quelque chose que la page
locale ne dit pas, reporte-le par `--note` ou `--journal` et régénère. Enfin
`Artifact` avec le `file_path` local **et** l'`url` — sans `url`, tu crées un
doublon. Pas de `favicon`, pas de nouveau titre, `label` : `<fiche> faite`.
Échec : une ligne, et continue.

**Ne touche pas à la feuille de route** : elle ne bouge qu'à l'ouverture et à la
clôture d'un chantier.
