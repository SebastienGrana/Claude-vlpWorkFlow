> **QUAND LIRE** : on joue une fiche `<X>*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache <X><n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier <X> — <titre du chantier>

**À quoi il sert.** <Deux lignes : le problème, et ce que le chantier change.
Pas d'historique, pas de justification longue.>

**Fait.** <Rien. Ouvert le <date>, cadré en <n> fiches, `<X>1` à jouer.>

## Le socle commun

<Ce que **toutes** les fiches utilisent, et qu'aucune ne répète : les API
vérifiées avec leur fichier et leur ligne, les invariants, les noms retenus,
les conventions de clé, ce qui existe déjà et se réutilise sans le recréer.
C'est la seule plage que `/vlp:tache` relit à chaque fiche : rien d'inutile ici,
mais rien d'utile ailleurs non plus.>

<Une table « symbole → fichier:ligne → ce qu'il rend » vaut mieux qu'un
paragraphe : une fiche y renvoie en un mot.>

<Dis aussi ce qu'on **ne** fait **pas** dans ce chantier, et pourquoi.>

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `<X>1` | <titre à l'infinitif> | rien |
| `<X>2` | <titre à l'infinitif> | `<X>1` |
| `<X>3` | <titre à l'infinitif> | `<X>1` |

<Une ligne en clair sur ce qui est parallélisable et ce qui ne l'est pas.>

---

<!-- FICHE:<X>1 -->
## <X>1 [ ] — <titre court à l'infinitif>

<Un bloc `**Tentatives** (<date>)` peut apparaître ici, sous le titre : c'est
`/vlp:tache` qui l'écrit quand elle abandonne après deux essais, et qui le relit à
la reprise pour ne pas les rejouer. Il ne se met pas à la main.>

**Dépend de** : rien.
**Fichiers** : <chemin/a.ext>, <chemin/b.ext> — et rien d'autre.
**Maquette** : <sed -n '120,148p' mockups/src/body.html>   (si des libellés existent)

**Prompt**
<Ce qu'il faut écrire, en clair, à la deuxième personne. Nomme les fonctions,
pas les lignes. Une fiche décrit une intention, pas un diff. ~20 lignes : si
elle en fait 50, c'est deux fiches.>

**Critère de fin**
<Ce qu'on doit voir pour dire que c'est fait. Une phrase. Soit une commande et
ce que sa sortie doit montrer — comptes bruts à côté du verdict — soit ce que
l'utilisateur doit constater à l'écran quand lui seul peut le faire.>
<!-- /FICHE -->

---

<!-- FICHE:<X>2 -->
## <X>2 [ ] — <titre court à l'infinitif>

**Dépend de** : `<X>1`.
**Fichiers** : <…>

**Prompt**
<…>

**Critère de fin**
<…>
<!-- /FICHE -->

---

**Les marqueurs `<!-- FICHE:… -->` / `<!-- /FICHE -->` ne sont pas décoratifs.**
`/vlp:tache` extrait une fiche entre eux, d'un seul `sed`. Sans eux, elle retombe
sur un motif de titres, qui rate en silence dès qu'un titre est reformulé — et
une extraction vide ressemble à une fiche vide. Le nom du marqueur ouvrant est
exactement celui de la fiche : `<!-- FICHE:D3 -->` pour `## D3 [ ] — …`.
