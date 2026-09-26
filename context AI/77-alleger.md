> **QUAND LIRE** : on joue une fiche `ALE*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ALE<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ALE — Essai : alléger la republication

**À quoi il sert.** Republier une page oblige à la relire, CSS compris (37 % des
caractères). On essaie deux pistes, on les mesure, on écrit une décision pour chacune.

**Estimé.** 2 fiches · ≈7,98 $ — ≈3,99 $/fiche sur 64 clos (le 2026-09-26).

**CLOS** le 2026-09-26. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** ALE1..ALE3 (2026-09-26) : CSS des pages en vlp.css joint adopte (-43 % par relecture, 5760 -> 3286) ; base db en attente d'un essai hors mode auto (630, mais rien en local ni par lien public) — estimé 2 fiches ≈7,98 $ · cadré 3 · joué 3 fiches ≈12 $.

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
  ligne suivante, par `ALE1` : **URL de la page jetable** : https://claude.ai/artifact/UHPu5YwRDT9Dcsgkj9t9mG
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
## ALE1 [x] — Essayer le CSS en fichier joint

**Session** : e2536015-4263-47cd-ba7e-6c0cf89df306
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
## ALE2 [x] — Essayer les données en base

**Session** : dfb6bb11-4da6-4dd5-b257-a4e52d9f7286
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
## ALE3 [x] — Écrire les deux décisions

**Session** : dfb6bb11-4da6-4dd5-b257-a4e52d9f7286
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

## Mesures

Une republication = `Artifact read` + une ligne de journal + `Artifact` publish,
même session (`e2536015-4263-47cd-ba7e-6c0cf89df306`), 2026-09-26. Le tour de
lecture est le premier de la plage ; `ctx_dernier − ctx_1er` ≈ ce que la page lue
a ajouté au contexte.

| Essai (ALE1) | Commande | tours | ctx_1er | ctx_dernier | écart | total |
|---|---|---|---|---|---|---|
| témoin, CSS dans la page | `py scripts/mesure-tokens.py --plage 2026-09-26T23:24:57 2026-09-26T23:25:10 e2536015-4263-47cd-ba7e-6c0cf89df306` | 2 | 85885 | 91645 | 5760 | 178395 |
| CSS joint (`vlp.css`) | `py scripts/mesure-tokens.py --plage 2026-09-26T23:26:00 2026-09-26T23:26:09 e2536015-4263-47cd-ba7e-6c0cf89df306` | 2 | 98252 | 101538 | 3286 | 200403 |

- **Écart** : 5760 → 3286, soit −2474 tokens par lecture (−43 %). Le `total`
  monte (178395 → 200403) parce que le contexte de départ est plus gros
  (85885 → 98252) : il suit la longueur de la session, pas la page.
- **Le CSS joint est-il relu : non.** La sortie de `read` porte
  `[This version has 2 published files, this page included; …]` puis
  `<link rel="stylesheet" href="vlp.css">` à la place du `<style>` — aucune
  règle CSS dans le texte rendu. `list` `scope: "files"` : `index.html` 6524
  octets, `vlp.css` 4584 octets.
- **Republier sans `files`** garde `vlp.css` (version 4 : toujours 2 fichiers).
- **Borne de plage** : l'heure lue dans le même message que le `read` tombe
  après le tour qui la lance ; la borne témoin a été reculée à 23:24:57, heure
  du tour de lecture relevée dans le `.jsonl`. L'essai 2 lit l'heure dans un
  tour à part, avant le `read`.
- **Affichage stylé : oui.** Constaté par l'utilisateur le 2026-09-26 (fond
  crème, cartes) ; le navigateur intégré de Claude n'est pas connecté à claude.ai.

**ALE2 — base `db`.** `db` existe pour ce compte (liste des capacités de la skill
`artifact-capabilities`, contrat 0.2.60). Variante : `essai-ale/page-db.html`,
publiée avec `capabilities: {db: {}}` et `vlp.css` joint :
https://claude.ai/artifact/KyNAVstNmYp1Afr7YbJago — le journal vient de la
collection `journal` (champs `ordre`, `date`, `texte`), amorcée par un `batch` de
2 documents hors mesure. Session `dfb6bb11-4da6-4dd5-b257-a4e52d9f7286`. Une
modification = écrire `j3.json` + `ArtifactData set` depuis ce fichier, **sans
lire la page**.

| Essai (ALE2) | Commande | tours | ctx_1er | ctx_dernier | écart | total |
|---|---|---|---|---|---|---|
| base (`ArtifactData set`) | `py scripts/mesure-tokens.py --plage 2026-09-26T23:31:54 2026-09-26T23:32:04 dfb6bb11-4da6-4dd5-b257-a4e52d9f7286` | 2 | 112122 | 112752 | 630 | 225363 |

- **Écart** : 630, contre 5760 (témoin) et 3286 (CSS joint). Le `total` suit
  encore le contexte de départ (112122), pas l'écriture.
- **1. Accord demandé à l'utilisateur : non constaté.** L'utilisateur ne sait pas
  (questionnaire, 2026-09-26) ; la session tournait en mode auto, qui a pu valider
  seul. 🟡 Reste ouvert : à trancher par un essai hors mode auto.
- **2. Fichier local dans le navigateur intégré : non.** Il affiche « Base
  indisponible dans cette vue : journal non affiché. » (`claude` absent hors claude.ai).
- **3. Page en fenêtre privée : écran de connexion.** Constaté par l'utilisateur
  le 2026-09-26. Une page qui déclare `db` est réservée à l'organisation
  (`db.d.ts` : « cannot be shared publicly ») : pas de visiteur par lien public.

**ALE3 — décisions (questionnaire, 2026-09-26).** C1 (CSS joint) **adoptée** ;
C2 (base `db`) **en attente** d'un essai hors mode auto — l'utilisateur : le
groupe n'est pas un frein, seul compte son usage. Écrites dans `ARTEFACTS.md`,
« Où vivent le CSS et les données ». Page jetable
`UHPu5YwRDT9Dcsgkj9t9mG` **supprimée** avec son accord ; la variante base
`KyNAVstNmYp1Afr7YbJago` et `essai-ale/page-db.html` + `vlp.css` **gardés** pour
cet essai (choix « Pas encore ») ; `page.html` et `j3.json` retirés.
