> **QUAND LIRE** : on joue une fiche `ENC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ENC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ENC — `/vlp:enchainer` rejoue une fiche floue

**À quoi il sert.** Après un `REFUSÉE`, rien ne demande si la faute est dans la fiche ou
chez le sous-agent : `LEC2`, 4 refus, 6,96 $ (TODO 69). Le relecteur dira la cause, le chef
la montrera dans un questionnaire, et proposera `main` au 2ᵉ refus.

**CLOS** le 2026-09-26. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** ENC1..ENC3 (2026-09-26) : cocher --refuser dit le rang du refus (ENC1) ; le relecteur classe REFUSÉE en fiche ou copie et propose une RÉÉCRITURE (ENC2) ; le chef pose un questionnaire à 4 options avant de rejouer un refus (ENC3).

**Session** : 584acc32-1973-4176-ab5c-7f2ebade2388

## Le socle commun

Image : le correcteur rend « refusé » ; on demande enfin si c'est l'énoncé ou l'élève.

**Décidé au cadrage (2026-09-25, par l'utilisateur).**

1. Le relecteur classe son refus, `fiche` ou `copie` ; le chef le reprend dans un
   questionnaire ; l'utilisateur tranche.
2. Jouer à la main (`vlp:tache`, comme `main`) est proposé à partir du **2ᵉ refus** de la
   même fiche.
3. Le chef ne réécrit **jamais** une fiche de lui-même : le texte vient de la ligne
   `RÉÉCRITURE` du relecteur, l'utilisateur le valide, puis le chef l'applique.
4. La procédure du chef après un refus vit dans `skills/enchainer/references/refus.md`,
   lue par `vlp.py lire` sur un `REFUSÉE` seulement : sans refus, elle ne coûte rien.
5. Un bloc **Tentatives** dont toutes les lignes numérotées sont `FAITE refusée à la
   relecture.` n'arrête plus le rejeu : ni l'étape 0 du chef, ni le sous-agent. Celui-ci
   lit la ligne `Erreur :` comme ce qu'il ne doit pas refaire.
6. ENC se joue par `/vlp:enchainer main` : c'est l'essai grandeur nature de `main`. Une
   permission refusée y rend `RETOUR` — c'est une mesure de l'essai, pas un échec.

**Noms retenus, à recopier tels quels.**

- `REFUSÉE — fiche : <motifs>` et `REFUSÉE — copie : <motifs>` (verdict du relecteur)
- `RÉÉCRITURE : <phrase de la fiche> → <ce qu'elle devient>` (sous un verdict `fiche`)
- `REFUSÉ <fiche> · refus <n>` (sortie de `cocher --refuser`)

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `refuser()` | `scripts/vlp.py:839` | écrit le bloc, numérote `N. FAITE refusée à la relecture.`, remplace `Erreur :` ; sortie `:869` |
| docstring de `cocher` | `scripts/vlp.py:63-74` | décrit `--refuser` et sa sortie |
| test `cocher --refuser` | `scripts/test-vlp.py:1527-1553` | attend aujourd'hui `REFUSÉ VAL1\n` deux fois |
| `VERDICTS` | `scripts/vlp.py:1422`, lu `:1493` | le gardien ne juge que le premier mot : `REFUSÉE — fiche` passe |
| arrêts imprévus | `enchainement.md:20-22` | un bloc Tentatives rend `RETOUR` |
| relecture | `enchainement.md:24-51` | les verdicts, les trois motifs de refus |
| étape 0, `REFUSÉE` | `skills/enchainer/SKILL.md:63-66`, `:84-86` | ce que le chef fait d'un bloc, d'un refus |
| reprise d'un bloc | `skills/tache/SKILL.md:74-76` | le modèle : ne pas rejouer ce que le bloc liste |
| fichier lu à la demande | `skills/tache/references/tache-blocage.md` | le modèle de `refus.md` |

**Hors chantier.** Un refus vrai et piégé : en `main`, aucun relecteur ne tourne — la
clôture l'inscrit à la TODO. Comment le chef de `LEC2` a contourné le bloc (2 refus
inscrits sur 4, `64-lecture-todo.md:112-115`). Les `allowed-tools` de `/vlp:enchainer` :
notés s'ils bloquent l'essai, pas corrigés ici.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ENC1` | Dire le rang du refus | rien |
| `ENC2` | Faire dire au relecteur d'où vient la faute | rien |
| `ENC3` | Faire demander le chef avant de rejouer | `ENC1`, `ENC2` |

`ENC1` et `ENC2` sont indépendantes ; `ENC3` lit leurs deux formats.

---

<!-- FICHE:ENC1 -->
## ENC1 [x] — Dire le rang du refus

**Session** : 78a94c41-8003-4614-be9a-2dc15bc057ee
**Dépend de** : rien.
**Fichiers** : scripts/vlp.py, scripts/test-vlp.py — et rien d'autre.

**Prompt**
Dans `refuser()`, la sortie devient `REFUSÉ <fiche> · refus <n>`. `<n>` compte, dans le
bloc après l'ajout, les seules lignes numérotées `FAITE refusée à la relecture.` — pas
toutes les lignes numérotées : une tentative écrite par un sous-agent `BLOQUÉE` l'est
aussi. Mets à jour la docstring de `cocher` (fin de `:74`).

Dans le test `cocher --refuser`, attends `· refus 1` puis `· refus 2`, et ajoute un cas :
une fiche dont le bloc porte déjà `1. <une piste>` (non refusée), puis `--refuser` →
`· refus 1`. Le test bâtit ses fichiers dans son dossier temporaire, comme ses voisins.

**Critère de fin**
`py scripts/test-vlp.py` : sa ligne de bilan, comptes bruts, zéro échec. Deux mutants,
chacun fait tomber le test : `<n>` = toutes les lignes numérotées (le cas nouveau tombe) ;
`<n>` = 1 (le 2ᵉ appel tombe). `pyright scripts/vlp.py scripts/test-vlp.py` : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:ENC2 -->
## ENC2 [x] — Faire dire au relecteur d'où vient la faute

**Session** : 78a94c41-8003-4614-be9a-2dc15bc057ee
**Dépend de** : rien.
**Fichiers** : enchainement.md — et rien d'autre.

**Prompt**
Dans § Relecture, la ligne `REFUSÉE` porte la cause avant ses motifs, sous les deux
formes du socle. `fiche` : la faute reviendrait avec tout exécutant qui suit la fiche à
la lettre — critère qui vérifie un signe au lieu de ce que le socle décide, fiche et
socle qui se contredisent, règle inapplicable sur les vraies lignes, fichier utile non
nommé. `copie` : la fiche le disait clairement, le sous-agent ne l'a pas fait. Sous un
verdict `fiche`, une ligne `RÉÉCRITURE` au format du socle ; le relecteur n'écrit pas
dans la fiche. Remplace « La ligne `REFUSÉE` porte les motifs seuls » en conséquence.

Dans « Arrêts imprévus », l'exception du socle (décision 5) pour un bloc de refus seuls.

Reste court : le fichier fait 51 lignes, il en fera au plus 60.

**Critère de fin**
`grep -c` de chacune des trois chaînes `REFUSÉE — fiche :`, `REFUSÉE — copie :`,
`RÉÉCRITURE :` dans `enchainement.md` : au moins 1 chacune, comptes bruts ;
`grep -n "FAITE refusée" enchainement.md` montre l'exception ; `py scripts/vlp.py lignes
enchainement.md` ≤ 60.
<!-- /FICHE -->

---

<!-- FICHE:ENC3 -->
## ENC3 [x] — Faire demander le chef avant de rejouer

**Session** : 78a94c41-8003-4614-be9a-2dc15bc057ee
**Dépend de** : `ENC1`, `ENC2`.
**Fichiers** : skills/enchainer/SKILL.md, skills/enchainer/references/refus.md (nouveau).

**Prompt**
Dans `SKILL.md`, étape 3 point 2 : sur `REFUSÉE`, après `cocher --refuser`, le chef lit
`vlp.py lire skills/enchainer/references/refus.md` et le suit, au lieu de traiter le
refus comme un `BLOQUÉE`. Étape 0 : l'exception du socle (décision 5). Deux ou trois
lignes de plus, pas davantage.

`refus.md`, 30 lignes au plus : une section « Avant de choisir » — ce que dit le
relecteur, attribué (cause, motif, ligne `RÉÉCRITURE`), et le rang lu sur `· refus <n>` —,
puis un questionnaire (`AskUserQuestion`) à quatre options :
« Réécrire la fiche » (cause `fiche` seulement : la ligne `RÉÉCRITURE` montrée telle
quelle ; sur un oui, un `Edit` qui l'applique, puis rejeu au point 1) ; « Rejouer telle
quelle » (cause `copie`) ; « Jouer à la main » (`vlp:tache`, recommandée dès `n` ≥ 2) ;
« S'arrêter » (le `BLOQUÉE` d'aujourd'hui, étapes 3 bis et 4). Un rejeu compte dans le
plafond de 5. Le chef ne réécrit rien de lui-même et n'ouvre rien d'autre.

**Critère de fin**
`py scripts/vlp.py lire skills/enchainer/references/refus.md` imprime le fichier ;
`py scripts/vlp.py lignes skills/enchainer/SKILL.md skills/enchainer/references/refus.md`
≤ 146 et ≤ 30 ; `grep -c "refus.md" skills/enchainer/SKILL.md` = 1 ; `grep -c` de chacune
des quatre options et de `· refus` dans `refus.md` ≥ 1, comptes bruts.
<!-- /FICHE -->
