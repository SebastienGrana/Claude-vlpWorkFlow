> **QUAND LIRE** : on joue une fiche `M*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache M<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier M — mesurer les tokens consommés

**CLOS** le 2026-09-11. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**À quoi il sert.** Le kit n'a aucun instrument de coût : le chantier E a dû
mesurer à la main pour se clore (voir `08-etat.md`). Ce chantier ajoute un
script qui somme les tokens d'`usage` par session, à partir des transcripts
JSONL, et l'affiche à deux moments : fin de fiche, fin de chantier.

**Fait.** Rien. Ouvert le 2026-09-10, cadré en 4 fiches, `M1` à jouer.

## Le socle commun

- **Dossier des transcripts d'une session** :
  `~/.claude/projects/<projet-slugifié>/<session-id>.jsonl`, où
  `<projet-slugifié>` est le chemin absolu du projet avec `/`, `\` et `:`
  remplacés par `-` (observé pour ce projet :
  `C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow`).
- **Champ à sommer** : `usage` (input_tokens, output_tokens,
  cache_creation_input_tokens, cache_read_input_tokens) — à confirmer sur un
  vrai fichier JSONL en M2, ne pas deviner son emplacement exact dans le JSON.
- **Script** : `scripts/mesure-tokens.py` — seule exception de la règle 4 de
  `CLAUDE.md` (posée en M1). Prend un ou plusieurs chemins JSONL, affiche une
  table texte brute (une ligne par fichier + un total), zéro appel modèle.
- **Convention d'id de session dans une fiche** : une ligne `**Session** :
  <chemin du jsonl>` sous le titre de la fiche jouée, écrite par `tache.md` à
  son étape 6 — même emplacement que le bloc « Tentatives ». C'est elle que
  `cloture.md` relit pour le cumul du chantier.
- **Ce qu'on ne fait pas ici** : pas d'estimation a priori (prédire le coût
  avant de jouer) — c'est un autre problème, hors chantier, cf. instruction
  d'ouverture.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `M1` | Ajouter l'exception à la règle 4 de CLAUDE.md | rien |
| `M2` | Écrire scripts/mesure-tokens.py | `M1` |
| `M3` | tache.md : afficher le coût en fin de fiche | `M2` |
| `M4` | cloture.md : total du chantier + proposition commit/push | `M2`, `M3` |

Aucune parallélisation utile : chaque fiche a besoin de la précédente pour
être testée en vrai (M2 a besoin de M1 posée, M3 a besoin du script qui
existe, M4 a besoin de la convention `**Session**` que M3 introduit).

---

<!-- FICHE:M1 -->
## M1 [x] — Ajouter l'exception à la règle 4 de CLAUDE.md

**Dépend de** : rien.
**Fichiers** : CLAUDE.md.

**Prompt**
Reformule la règle 4 (« Rien de propre à une machine dans `commands/` ni
`templates/` ») pour y ajouter une exception explicite et assumée : un
dossier `scripts/` à la racine du kit est permis — seule exception à la
doctrine « aucun code applicatif » — réservé à l'outil de mesure de tokens
(zéro appel modèle, uniquement du parsing local de transcripts JSONL). Dis
pourquoi (mesurer le coût réel, décision du 2026-09-10, cf. l'abandon du
chantier E faute d'instrument) et où (`scripts/`). N'édite rien d'autre dans
le fichier.

**Critère de fin**
`grep -n "scripts/" CLAUDE.md` rend au moins une ligne dans la règle 4, et la
règle dit explicitement que c'est une exception, pas un relâchement général.
<!-- /FICHE -->

---

<!-- FICHE:M2 -->
## M2 [x] — Écrire scripts/mesure-tokens.py

**Dépend de** : `M1`.
**Fichiers** : scripts/mesure-tokens.py (nouveau).

**Prompt**
Avant d'écrire le parseur, ouvre un vrai fichier JSONL de cette session
(dossier du socle commun) et vérifie où vit `usage` dans les lignes qui
comptent — ne devine pas le nom des champs.

Script Python 3, sans dépendance externe. Prend en argument un ou plusieurs
chemins de fichiers JSONL. Pour chacun : lit ligne à ligne, parse le JSON,
ignore silencieusement une ligne invalide mais compte combien ont été
ignorées, additionne les champs d'`usage` trouvés. Affiche une table texte
brute au terminal : une ligne par fichier (nom court du fichier, les quatre
comptes, un total), puis une ligne `TOTAL` si plusieurs fichiers sont passés.
Code de sortie non nul si aucun fichier n'a pu être lu.

**Critère de fin**
`python scripts/mesure-tokens.py <un jsonl réel de cette session>` affiche une
table avec des comptes non nuls — comptes bruts, aucun arrondi qui masque le
détail.
<!-- /FICHE -->

---

<!-- FICHE:M3 -->
## M3 [x] — tache.md : afficher le coût en fin de fiche

**Session** : ~/.claude/projects/C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow/c49b72aa-2742-43b5-a9e2-d293736ee715.jsonl
**Dépend de** : `M2`.
**Fichiers** : commands/tache.md (étape 6, juste après la case cochée).

**Prompt**
À la fin de l'étape 6 de `tache.md` (une fois la fiche cochée) : d'abord,
détermine comment la session courante connaît son propre fichier JSONL — ne
devine pas, vérifie (l'id de session peut être visible dans un chemin déjà
exposé à la session, par exemple le dossier scratchpad ; confirme avant
d'écrire l'étape). Écris la ligne `**Session** : <chemin du jsonl>` sous le
titre de la fiche qui vient d'être cochée — même emplacement que le bloc
« Tentatives » (juste sous le titre, avant « Dépend de »). Puis appelle
`scripts/mesure-tokens.py` sur ce seul fichier (coût de la fiche), puis sur
tous les fichiers listés par les lignes `**Session**` déjà présentes dans le
fichier de fiches, fiche courante comprise (cumul du chantier). Affiche les
deux tables brutes avant de rendre la main.

**Critère de fin**
Jouer une fiche de test (ou relire M2 elle-même comme cas réel) fait
apparaître deux tables — coût de la fiche, cumul du chantier — comptes bruts,
avant que la main soit rendue.
<!-- /FICHE -->

---

<!-- FICHE:M4 -->
## M4 [x] — cloture.md : total du chantier + proposition commit/push

**Session** : C:\Users\znorr\.claude\projects\C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow\dd7e5a7f-b756-4575-a2dd-f0f6cf8621ac.jsonl
**Dépend de** : `M2`, `M3`.
**Fichiers** : cloture.md (étape 3 « Le fichier d'état », et après l'étape 5
« Pour finir »).

**Prompt**
À l'étape 3 de `cloture.md`, avant d'écrire la ligne de bilan : lis toutes les
lignes `**Session**` du fichier de fiches qu'on clôture, appelle
`scripts/mesure-tokens.py` sur l'ensemble, verse le total brut dans la ligne
de bilan datée (comptes bruts, pas d'estimation, pas d'arrondi).

Ajoute ensuite une section après « Pour finir » : une fois les cinq écritures
faites, propose (questionnaire, jamais automatique — geste irréversible) un
`git commit` (message résumant le chantier clos) puis un `git push`. Refuse
d'agir sans confirmation explicite à chaque fois, même si l'utilisateur a déjà
confirmé pour un chantier précédent.

**Critère de fin**
Clôturer un chantier (test ou réel) fait apparaître le total brut dans le
fichier d'état, et affiche une demande de confirmation avant tout commit ou
push — jamais l'un ou l'autre sans réponse.
<!-- /FICHE -->

---

**Les marqueurs `<!-- FICHE:… -->` / `<!-- /FICHE -->` ne sont pas décoratifs.**
`/vlp:tache` extrait une fiche entre eux, d'un seul `sed`.
