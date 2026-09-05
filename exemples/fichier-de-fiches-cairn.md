> **Extrait réel** du chantier « filet de non-régression » de cairn
> (`Cairn-VlpLib/context AI/22-filet-non-regression.md`). Le socle est abrégé
> ici ; la fiche `N1` est recopiée telle quelle, pour montrer la densité visée.

---

> **QUAND LIRE** : on joue une fiche `N*` du filet de non-régression, ou on se
> demande où en est ce chantier. `/tache cairn N<n>` n'en lit que le socle
> commun et sa fiche — jamais ce fichier en entier.

# Chantier N — le filet de non-régression

**À quoi il sert.** Le dépôt a 29 modules, 4 615 lignes et zéro test. Ce
chantier pose un banc `pytest` sur les vérités **connues par ailleurs** — pas
sur des chiffres de corpus, qui bougent à chaque relance — puis s'en sert pour
corriger `geometry.fit()`, la seule régression connue.

**Fait.** Rien. Ouvert le 2026-09-04, cadré en 7 fiches, `N1` à jouer.

## Le socle commun

Ce que toutes les fiches utilisent. Rien à relire ailleurs pour ça.

**Où vont les tests.** Un dossier `tests/` à la racine. Le dépôt **n'est pas un
package** : les modules s'importent par leur nom nu (`import mapdata`), et un
fichier qui importe un voisin ouvre par `sys.path.insert(0, <racine>)` puis
`import layout`. `tests/conftest.py` fait la même chose, une fois, pour tous
les tests — aucun fichier de test ne recopie cet en-tête.

**Les symboles cités par les fiches**, tous vérifiés le 2026-09-04 :

| Symbole | Fichier | Ce qu'il rend |
|---|---|---|
| `mapdata.read(path, with_items=True)` | `gbx/mapdata.py:157` | une carte : blocs, drapeaux, items, métadonnées |
| `replay.STEP_MAX` | `gbx/replay.py:60` | `32.0` — lu dans les données, pas choisi |
| `geometry.fit(raw, seen)` | `analysis/geometry.py:221` | choisit le rectangle : c'est lui qu'on corrige |

<... la table réelle en compte seize, plus les deux marqueurs pytest et la
liste de ce qu'on ne teste pas ...>

**Ce qu'on ne teste pas, et pourquoi.** Aucun chiffre de corpus : les 9,3 %,
les 305 472 lignes bougent à chaque relance et un test qui les fige transforme
une mesure en dogme.

**Toute sortie affiche ses comptes bruts à côté du verdict.** Un instrument
muet rend son propre échec indiagnosticable.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `N1` | Poser le banc pytest et prouver les imports | rien |
| `N2` | Les tables pures, sans aucun fichier | `N1` |
| `N3` | Le conteneur, sur une carte témoin | `N1` |
| `N4` | Le ghost et la cellule de départ | `N1` |
| `N5` | Le banc de `fit()`, GTCurve2 en échec attendu | `N1`, `N3` |
| `N6` | Corriger l'objectif de `fit()` | `N5` |
| `N7` | Mesurer la couverture et écrire ce qui reste | `N1`–`N6` |

`N2`, `N3` et `N4` sont indépendantes entre elles : leur ordre est libre.

---

## N1 [x] — Poser le banc pytest et prouver les imports

**Dépend de** : rien.
**Fichiers** : créer `tests/conftest.py`, `tests/test_imports.py`,
`pytest.ini`, `requirements-dev.txt` — et rien d'autre. Lire `layout.py` pour
copier l'en-tête `sys.path`.
**Corpus** : aucun.

**Prompt**
Pose l'infrastructure de test, et rien de plus. `pytest.ini` déclare les deux
marqueurs du socle (`needs_corpus`, `needs_corpus_pkl`) pour qu'ils ne lèvent
pas d'avertissement. `requirements-dev.txt` contient `pytest` et `coverage`,
seules dépendances de développement du dépôt.

`tests/conftest.py` met la racine sur `sys.path` puis `import layout`, comme
tout module du dépôt, et définit deux fixtures qui sautent le test quand la
ressource manque : l'une vérifie que `paths.py` résout un dossier de cartes
existant, l'autre que `corpus.pkl` est là. Le message de skip dit **laquelle**
manque et comment l'obtenir.

`tests/test_imports.py` importe chacun des modules de `gbx/`, `measure/`,
`build/`, `analysis/` et de la racine par son nom nu, et échoue en nommant le
module fautif. C'est ce contrôle-là — pas une relecture — qui avait rattrapé le
dépôt cassé après le rangement. N'importe pas `probes/` : ce sont des
instruments, pas des modules.

**Critère de fin**
`python -m pytest -q` sort en 0, et le compte de tests est affiché. Puis
`python -m pytest tests/test_imports.py -v` liste chaque module importé, un par
ligne : le nombre de lignes doit valoir le nombre de fichiers `.py` des quatre
dossiers plus les deux de la racine — affiche les deux nombres côte à côte.

---
