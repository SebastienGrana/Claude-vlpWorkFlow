<!-- Les numéros d'étape sont ceux de /vlp:tache. Lu par /vlp:tache (étape 5, après deux tentatives), /vlp:enchainer et l'agent vlp:fiche. -->

# Bloquée après deux tentatives

À la troisième tentative, avant de rendre la main, **écris ce que tu as tenté dans la
fiche elle-même** — pas seulement sur l'artefact. C'est le seul endroit que la
session suivante lira *avant* d'écrire : l'artefact, elle ne l'ouvre qu'à
l'étape 6 bis, une fois le travail refait. Sans ça, elle rejoue tes deux
tentatives à l'identique.

Ajoute donc, dans le fichier de fiches, **juste sous le titre de la fiche** et
avant sa ligne « Dépend de » :

```
**Tentatives** (<date>) — non résolu.
1. <ce que tu as essayé, une ligne>
2. <ce que tu as essayé, une ligne>
Erreur : <la ligne d'erreur qui compte, pas la trace entière>
```

Trois à cinq lignes, pas plus : ce bloc est relu à chaque reprise de la fiche,
il se paye autant de fois. Une deuxième session bloquée **complète** ce bloc,
elle n'en ouvre pas un second.

Puis **marque le blocage sur l'artefact** — c'est le moment où l'on a le plus
besoin de le voir. Suis la régénération de `tache-page.md` (grep, lire, réécrire,
republier), avec : la fiche passée en
`data-etat="bloquee"` dans `ZONE:fiches` et dans `ZONE:avancement`, la section
`ZONE:blocage` rendue visible — retire son `hidden` — portant les deux lignes
de ce que tu as tenté et l'erreur brute, telle quelle, dans le `pre`.
`label` : `<fiche> bloquée`. Ne coche pas la fiche, n'écris rien dans le
fichier d'état.

Cette section se retire — `hidden` remis — dès que la fiche repasse, lors de la
mise à jour de l'étape 6.

## Un blocage arrête une fiche, pas le chantier

Avant de rendre la main, dis quelle **fiche suivante reste jouable** — celle
dont la ligne « Dépend de » ne cite pas la fiche bloquée — et propose-la. Sans
ça, un blocage isolé gèle tout le chantier.

Les essais de cette fiche ne sont **pas commités** : la fiche n'a pas été
cochée. S'ils ne servent à rien, propose de les jeter (`git checkout -- .`)
plutôt que de les laisser polluer la fiche suivante ; s'ils gardent une piste,
laisse-les et dis-le.

**L'agent `vlp:fiche` ne touche pas à git** : ni commit, ni `revert`, ni
`checkout`. Il *dit* ce qu'il propose, et rend `BLOQUÉE` — c'est le chef, ou
l'utilisateur, qui exécute. Un geste git dans un sous-agent détruit du travail
que personne n'a vu.
