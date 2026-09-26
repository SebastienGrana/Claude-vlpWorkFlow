> **QUAND LIRE** : on joue une fiche `ALE*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ALE<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ALE — Essai : alléger la republication

**À quoi il sert.** Republier une page oblige à la relire, CSS compris (37 % des
caractères). On essaie deux pistes, on les mesure, on écrit une décision pour chacune.

**Estimé.** 2 fiches · ≈7,98 $ — ≈3,99 $/fiche sur 64 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 3 fiches, `ALE1` à jouer.

**Session** : 88a2fc75-310a-48ac-8cb9-d5c13ef2956b

## Le socle commun

- **Le plan d'essai** : `context AI/38-audit-artefacts.md`, § 4 « C — Essai »
  (lignes 445–495) — pistes C1 (CSS joint) et C2 (base `db`), ce qu'il reste à prouver.
- **Le point de départ** : une lecture seule de page coûte **5 379 tokens**
  (médiane, n = 91, même fichier § 2.5). Ce chiffre vient de Cairn ; les fiches
  mesurent leur propre témoin, elles ne le réutilisent pas.
- **Republier = lire d'abord, puis publier** : `ARTEFACTS.md`, « Republier : lire d'abord ».
- **La page jetable** : une copie de `context AI/artefacts/76-abri.html`, dans
  `context AI/artefacts/essai-ale/` (sous le dossier de travail : l'outil refuse
  une source hors de lui). Jamais une page en ligne du kit. Son URL s'écrit ici,
  ligne suivante, par `ALE1` : **URL de la page jetable** : aucune.
- **La même modification à chaque essai** : ajouter une entrée de journal d'une
  ligne dans la page. Rien d'autre ne change entre deux mesures.
- **La mesure** : l'heure lue par `date` juste avant la lecture et juste après la
  publication, puis `py scripts/mesure-tokens.py --plage <avant> <après> <id de session>`.
  On retient `ctx_dernier − ctx_1er` et `total`, recopiés bruts avec la commande.
- **Jouées à la main** : `/vlp:tache` seulement. Le sous-agent `vlp:fiche` n'a
  pas l'outil `Artifact` ; `/vlp:enchainer` ne sert pas ici.

**Hors du chantier** : déplacer le CSS des gabarits dans `vlp.css` (c'est à `PLI`
et `FEU`, une seule migration) ; toucher une page réelle ; changer `vlp.py`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ALE1` | Essayer le CSS en fichier joint | rien |
| `ALE2` | Essayer les données en base | `ALE1` |
| `ALE3` | Écrire les deux décisions | `ALE1`, `ALE2` |

Rien n'est parallélisable : `ALE2` reprend la page jetable d'`ALE1`.

---

<!-- FICHE:ALE1 -->
## ALE1 [ ] — Essayer le CSS en fichier joint

**Dépend de** : rien.
**Fichiers** : `context AI/artefacts/76-abri.html` (lu, copié), `context AI/artefacts/essai-ale/`, `ARTEFACTS.md` (la section « Republier : lire d'abord »), ce fichier (la ligne d'URL du socle).

**Prompt**
Copie `76-abri.html` dans `essai-ale/page.html` et publie-la (nouvel artefact,
titre « Essai ALE »). Écris son URL dans le socle. Puis deux essais, dans cette séance :

1. **Témoin** — CSS dans la page : lis la page (`Artifact read`), fais la
   modification du socle, republie. Mesure.
2. **CSS joint** — sors le `<style>` dans `essai-ale/vlp.css`, relie-le par
   `<link rel="stylesheet" href="vlp.css">`, publie avec `files`. Puis refais
   exactement l'essai 1 : lis, modifie, republie. Mesure.

Note aussi ce que rend `Artifact read` sur la page à fichier joint : le CSS
y est-il, oui ou non ? La page s'affiche-t-elle toujours avec son style ? Écris
les deux mesures, et ce constat, dans une section `## Mesures` en fin de ce fichier.

**Critère de fin**
La section `## Mesures` porte deux lignes — témoin et CSS joint — chacune avec
sa commande `mesure-tokens.py`, ses `ctx_1er`, `ctx_dernier` et `total` bruts,
plus une ligne « le CSS joint est-il relu : oui/non », avec l'extrait de la sortie de `read` qui le prouve.
<!-- /FICHE -->

---

<!-- FICHE:ALE2 -->
## ALE2 [ ] — Essayer les données en base

**Dépend de** : `ALE1`.
**Fichiers** : `context AI/artefacts/essai-ale/`, ce fichier (socle et `## Mesures`).

**Prompt**
Charge d'abord la skill `artifact-capabilities` : dis si `db` existe pour ce
compte. S'il n'existe pas, écris-le dans `## Mesures` et arrête la fiche là.

Sinon, fais de la page jetable une variante : le journal vient d'une
collection `journal` de la base, lue par un court script ; publie-la avec la
capacité `db`. Puis la même modification que le socle, mais **sans relire la page** :
une écriture `ArtifactData` depuis un fichier JSON local. Mesure-la comme le socle le dit.

Relève trois points :
1. l'écriture a-t-elle demandé un accord à l'utilisateur ? — demande-lui ;
2. le fichier local, ouvert dans le navigateur intégré, affiche-t-il le journal ?
3. la page, ouverte par l'utilisateur dans une fenêtre privée, affiche-t-elle le journal ?

Écris la mesure et les trois réponses dans `## Mesures`.

**Critère de fin** (visuel)
`## Mesures` porte la ligne « base » avec sa commande et ses comptes bruts, et
les trois réponses. L'utilisateur confirme les points 1 et 3, que lui seul voit.
<!-- /FICHE -->

---

<!-- FICHE:ALE3 -->
## ALE3 [ ] — Écrire les deux décisions

**Dépend de** : `ALE1`, `ALE2`.
**Fichiers** : ce fichier (`## Mesures`), `ARTEFACTS.md`, `context AI/08-etat.md` (entrées n° 28, 29 et 30 de la TODO).

**Prompt**
Dans `ARTEFACTS.md`, écris une section courte « Où vivent le CSS et les
données » : une décision par piste — adoptée ou non —, le chiffre qui la
fonde (renvoi à `## Mesures` de ce fichier, sans recopier le tableau), et ce
que `PLI` et `FEU` en font.

Dans la TODO, mets à jour les lignes `PLI`, `FEU` et `BTN` : retire `ALE` des
dépendances, et dis en une phrase ce qui change pour elles.

Enfin, demande à l'utilisateur l'accord de supprimer la page jetable
(`Artifact` `action: "delete"`). Avec son oui seulement, supprime-la, puis
le dossier `essai-ale/`.

**Critère de fin**
`grep -c "Où vivent le CSS et les données" ARTEFACTS.md` rend 1 ;
`grep -E "^\| (28|29|30) \|" "context AI/08-etat.md"` montre trois lignes
dont la dernière colonne ne nomme plus `ALE` ; la page jetable est supprimée,
ou le refus de l'utilisateur est noté dans `## Mesures`.
<!-- /FICHE -->
