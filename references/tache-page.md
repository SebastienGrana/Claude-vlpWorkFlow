<!-- Les numéros d'étape sont ceux de /vlp:tache. Lu par /vlp:tache (étape 6 bis) et /vlp:enchainer. -->

# Régénérer l'artefact du chantier

L'artefact est ce que l'utilisateur regarde entre deux sessions : une fiche
cochée dans le fichier mais pas sur la page, et la page ment. Fais-le dans la
foulée de la case cochée, jamais « plus tard ».

Son URL est dans la ligne « **artefact du chantier** » de `CHANTIER.md`.

**Le principe : la page dérive du fichier de fiches, jamais l'inverse.** Tu ne
reportes pas une case de tête — tu réécris les zones pour qu'elles disent ce
que le fichier dit, et le fichier vient d'être mis à jour à l'étape 6.

Quatre gestes, dans cet ordre :

1. relis l'état réel des fiches — une commande, quatre lignes de sortie :

   ```bash
   grep -n '^## [A-Z][0-9]' "<fichier de fiches courant>"
   ```

2. `Artifact`, `action: "read"`, cette `url`. **Cette lecture n'est pas
   facultative** : le protocole refuse une republication sur une page que la
   session n'a ni lue ni publiée. Elle sert aussi à récupérer ce qui aurait été
   publié entre-temps.

3. réécris le fichier local `<contexte>/artefacts/<NN>-<chantier>.html`, à
   partir de la version rendue, pour qu'il dise **exactement** ce que la sortie
   du `grep` dit :

   - chaque fiche `[x]` en `data-etat="faite"`, son `etat` en « faite » ;
   - la première non cochée en `data-etat="encours"` ;
   - les suivantes sans `data-etat` ;
   - `ZONE:avancement` : un segment par fiche, les mêmes états ;
   - la `note` de la fiche jouée remplacée par le **critère de fin constaté** —
     une ligne, comptes bruts compris ;
   - `ZONE:blocage` remise en `hidden` si la fiche qui bloquait vient de
     passer ;
   - si la tâche a tranché quelque chose d'imprévu, la **même ligne** que celle
     ajoutée au fichier d'état, datée, dans `ZONE:journal` ;
   - la ligne de comptage de l'en-tête, et la date du pied de page ;
   - si la fiche jouée a une ligne `**Session**` : son coût en `.cout`, sous sa
     `.note`, et le total du chantier en `.cout-total` sous la liste — les deux
     déjà calculés par « Coût de la fiche », étape 6 de `/vlp:tache`, convention
     d'affichage dans `templates/artefact-chantier.html`. Pas un second appel à
     `mesure-tokens.py`.

   En cas de **désaccord** entre la page et le `grep`, c'est le `grep` qui a
   raison : la page est une vue, le fichier est la vérité.

4. republie : `file_path` local **et** `url` — sans `url`, tu crées un doublon.
   Pas de `favicon`, pas de nouveau titre. `label` : `<fiche> faite`.

**Garde de taille**, avant de republier :

```bash
wc -l "<contexte>/artefacts/<NN>-<chantier>.html"
```

Au-delà de **250 lignes**, republie quand même mais **dis-le en une ligne** :
cette page est relue à chaque fiche, son gras se paye autant de fois qu'il
reste de fiches à jouer. Ce qui la gonfle vient presque toujours du fichier de
fiches — prompt, socle, extraits de code — et n'a rien à faire là.

Rien d'autre ne va sur cette page : pas de code, pas le prompt de la fiche, pas
le détail des tentatives. Si la publication échoue, dis-le en une ligne et
continue — le fichier de fiches, lui, est à jour.

**Et c'est tout : ne touche pas à la feuille de route.** Elle ne bouge qu'à
l'ouverture et à la clôture d'un chantier. Sa zone « en cours » ne porte pas de
compteur — elle nomme le chantier et renvoie à sa page, qui est celle que tu
viens de mettre à jour ; il n'y a donc rien à y reporter, et la lire à chaque
fiche coûterait autant que la page du chantier pour une ligne.
