> **QUAND LIRE** : on joue une fiche `I*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache I<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier I — Un projet neuf qui ne ment pas

**À quoi il sert.** `/vlp:init` pose un projet dont l'index et le routage nomment des
fichiers absents, et fige `08-etat.md` ; ce chantier le rend vrai, et le prouve par script.

**Fait.** Rien. Ouvert le 2026-09-17 (TODO n° 10, audit point 8), cadré en 3 fiches, `I1` à jouer.

## Le socle commun

**Ce qui existe et se réutilise** (lancer par `PYTHONUTF8=1 python scripts/vlp.py …`) :

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `main` | `scripts/vlp.py`, fin du fichier | les sous-parseurs ; une sous-commande = un `add_parser` + une branche |
| docstring | `scripts/vlp.py`, en tête | la liste des sous-commandes — toute nouvelle s'y déclare |
| `lire`, `lignes_de` | `scripts/vlp.py` | texte sans CRLF |
| `ecrire`, `appel`, `verifier` | `scripts/test-vlp.py` | projets en dossier temporaire ; `OK` et sortie 0 |
| lignes `**contexte**`, `**index**`, `**fichier d'état**` | `CHANTIER.md` d'un projet | les chemins, relatifs à sa racine |
| cas `init` | `evals/init/case.yaml` | graders `file_exists` et `tool_used` ; Bash refusé sous Windows |

**Les deux sous-commandes du chantier** — noms retenus, sorties à respecter :

- `vlp.py etat <contexte>` → une ligne `ETAT=<NN>-etat.md` : le `*-etat.md` déjà présent,
  sinon le premier nombre à deux chiffres libre après le plus grand (`01` si vide). Sort 0.
- `vlp.py renvois <projet>` → une ligne `ABSENT: <source>:<ligne>: <nom>` par renvoi mort,
  puis `RENVOIS <n> nommés · <n> absents`. Sort 1 s'il y a un absent.
  Lit les noms entre accents graves dans les tables de l'index et dans la table de
  routage de `CLAUDE.md` ; un nom existe s'il existe contre le dossier de contexte ou
  contre la racine. Ignorés : un nom à `<…>`, une ligne dont la 1re cellule commence par
  `*(` (hors dossier), un nom sans `.` (commande, dossier).

**Invariants.** Pas de chiffre recopié : les commandes appellent le script, elles ne
décrivent pas son algorithme. `08-etat.md` reste un exemple légitime dans
`methode-chantier.md` et dans les `fixture.sh` des evals : on n'y touche pas.

**Dehors.** Les projets équipés (Cairn, MapDecorator, ProjetONZSM, TrackGen) ne sont
pas retouchés ; `/vlp:chantier` étape 5 garde son `ls` pour numéroter.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `I1` | Nommer le fichier d'état par script | rien |
| `I2` | Lister les renvois morts, dans `/vlp:check` | rien |
| `I3` | Prouver sur l'eval `init` | `I1`, `I2` |

I1 et I2 sont indépendantes ; I3 les rejoue ensemble sur un projet réellement posé.

---

<!-- FICHE:I1 -->
## I1 [ ] — Nommer le fichier d'état par script

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `commands/init.md`,
`templates/CLAUDE.md`, `templates/CHANTIER.md`, `templates/context AI/00-INDEX.md`,
`templates/artefact-feuille-de-route.html` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `etat` décrite au socle, déclarée dans la docstring, et ses
tests dans `test-vlp.py` : dossier vide → `01-etat.md` ; `03-a.md` et `07-b.md` →
`08-etat.md` ; `10-etat.md` présent → `10-etat.md` ; dossier absent → `01-etat.md`.
Dans `commands/init.md` étape 3, le fichier d'état prend le nom que rend
`vlp.py etat "<contexte>"` — un appel groupé avec l'étape 0 si possible, sans ajouter de
tour ; sans Bash, la règle se dit en une ligne (« le premier numéro libre ») sans
chiffre. Dans les gabarits, `08-etat.md` devient `<NN>-etat.md`, et `init.md` dit de
remplacer `<NN>` comme les autres `<…>`.

**Critère de fin**
`python scripts/test-vlp.py` rend `OK` ; `grep -rc "08-etat" templates commands` somme
à 0 (7 avant) ; `vlp.py etat "context AI"` rend `ETAT=08-etat.md` sur ce kit.
<!-- /FICHE -->

---

<!-- FICHE:I2 -->
## I2 [ ] — Lister les renvois morts, dans `/vlp:check`

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `commands/check.md`,
`commands/init.md`, `context AI/00-INDEX.md` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `renvois` décrite au socle, déclarée dans la docstring, et ses
tests : un index qui nomme un fichier absent → `ABSENT` et sortie 1 ; un nom à `<…>`, une
ligne `*(hors dossier)` et `commands/` sont ignorés ; tout présent → `0 absents`, sortie 0.
Dans `commands/check.md`, ajoute une vérification `H — Les renvois mènent quelque part`
qui l'appelle en un bloc, et mets à jour le compte des vérifications et « de `A` à `G` ».
Dans `commands/init.md` étape 3 ter, retire la liste recopiée des outils de
`/vlp:tache` (`sed`, `awk`… : faux depuis le chantier S) — renvoie au frontmatter
`allowed-tools` de `commands/tache.md`. Lance `renvois` sur ce kit et corrige son
`00-INDEX.md` jusqu'à 0 absent (au moins `scripts/carte.py`, retiré en S) ; profites-en
pour y passer `19-doctrine.md` à **clos**.

**Critère de fin**
`python scripts/test-vlp.py` rend `OK` ; `vlp.py renvois .` sur ce kit rend `0 absents`
(compte avant/après affiché) ; `grep -c "awk" commands/init.md` rend 0 (1 avant).
<!-- /FICHE -->

---

<!-- FICHE:I3 -->
## I3 [ ] — Prouver sur l'eval `init`

**Dépend de** : `I1`, `I2`.
**Fichiers** : `evals/init/case.yaml` — et rien d'autre.

**Prompt**
Le grader `*/08-etat.md` devient `*/*-etat.md`. Lance le cas seul, avec `--keep-temp`
(`claude` absent du PATH : `%APPDATA%/Claude/claude-code/<version>/claude.exe` ; drapeaux
`--trust-plugin --allow-tools Write Edit`, comme en V3). Puis lance toi-même
`vlp.py renvois` et `vlp.py etat` sur le dossier gardé. Si `renvois` trouve un absent,
c'est un gabarit qui ment : corrige-le (fichier de `templates/`, hors liste — dis-le) et
rejoue une fois. Plafond : 0,80 $ pour les lancements de la fiche.

**Critère de fin**
Le rapport de l'eval donne score 1 (tours et $ affichés) ; sur le dossier gardé,
`vlp.py renvois` rend `0 absents` avec le nombre de renvois nommés, et le fichier d'état
posé porte le nom que rend `vlp.py etat`.
<!-- /FICHE -->
