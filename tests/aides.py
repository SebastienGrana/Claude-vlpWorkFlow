"""Les aides communes de la suite pytest (REF4) : le code de `vlp.py` chargé par chemin, comme
l'ancienne suite maison le charge, et les petits bâtisseurs que les tests migrés partagent.

Le chargement se fait une fois par processus ; un test qui change l'état du module (`mod.etat.GIT`…) passe par
`monkeypatch.setattr`, qui le remet à la fin du test.
"""
import datetime
import importlib.util
import inspect
import io
import json
import os
import re
import subprocess
from typing import Any

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RACINE, "scripts")


def charger_coeur():
    """Charger `scripts/vlp_coeur.py` par son chemin (`spec_from_file_location`), puis le régler comme
    l'ancienne suite maison le règle : tampon des hooks coupé, page d'enchaînement du vrai kit jamais refaite."""
    spec = importlib.util.spec_from_file_location("vlp_coeur", os.path.join(SCRIPTS, "vlp_coeur.py"))
    assert spec
    assert spec.loader
    module: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.etat.TAMPON_HOOKS = None
    module.etat.SOURCE_ORDRE = None
    return module


mod: Any = charger_coeur()


def porte_motif(fonction, motif, nom=None):
    """Dire si le test `fonction` porte `motif`, sans tenir compte de la casse : dans son nom (`nom`, l'id d'un test
    paramétré compris), son texte, ou celui des fonctions de son module qu'il nomme — un libellé écrit dans une aide
    retient le test qui l'appelle (VIT10, l'option `--seul` de `conftest.py`, REF59)."""
    try:
        source = inspect.getsource(fonction)
    except (OSError, TypeError):
        source = ""
    module = inspect.getmodule(fonction)
    aides = [inspect.getsource(g) for n, g in sorted(vars(module).items()) if inspect.isfunction(g)
             and g is not fonction and re.search(r"\b%s\b" % re.escape(n), source)] if module else []
    return motif.lower() in ((nom or fonction.__name__) + " " + source + "".join(aides)).lower()


def appel(argv):
    """Lancer `vlp.py <argv>` dans ce processus : rendre (code de sortie, sortie)."""
    s = io.StringIO()
    code = mod.main(argv, s)
    return code, s.getvalue()


def lire(chemin):
    """Lire un fichier comme le kit le lit."""
    return mod.lire(chemin)


def ecrire(chemin, texte):
    """Écrire `texte` tel quel, dossiers créés."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte)


def lire_texte(chemin):
    """Le texte UTF-8 de `chemin` ; `FileNotFoundError` s'il n'existe pas."""
    with open(chemin, encoding="utf-8") as f:
        return f.read()


def transcript(chemin, tours, heures=None):
    """Un jsonl de `tours` tours, 100 000 tokens d'entrée chacun, sur claude-opus-5 (5 $ le million) ;
    `heures` : celle de chaque tour, en secondes UTC — sans elles, aucun `timestamp`."""
    with open(chemin, "w", encoding="utf-8") as f:
        for n in range(tours):
            ligne: dict[str, Any] = {"type": "assistant", "requestId": "r%d" % n, "message": {
                "id": "m%d" % n, "model": "claude-opus-5", "content": [],
                "usage": {"input_tokens": 100000, "output_tokens": 0,
                          "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}}
            if heures:
                ligne["timestamp"] = datetime.datetime.fromtimestamp(
                    heures[n], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            f.write(json.dumps(ligne) + "\n")


def commits(depot, sujets, t0):
    """Poser des commits vides dans `depot` : `sujets` est une liste de (secondes après `t0`, message), la date
    d'auteur et de commiteur fixée à cette heure."""
    for d, sujet in sujets:
        date = "%d +0000" % (t0 + d)
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=depot, check=True,
                       capture_output=True, env=dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))


def ligne_close(c):
    """Une ligne close au format de cmd_clore, avec plage Q1–Q2, date 2026-05-06, et coût c."""
    return ('          <tr>\n            <td>Test <span class="badge" data-etat="clos">clos</span></td>\n'
            '            <td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>\n'
            '            <td class="mono">%s</td>\n            <td>Test</td>\n          </tr>\n' % c)


# Les constantes que plusieurs fichiers de tests posaient à l'identique (dette RUF, 2026-11-21).

AVEC = """# Chantier Y

## Le socle commun

Socle, ligne 1.

## L'ordre des fiches

---

<!-- FICHE:Y1 -->
## Y1 [x] — faite
**Session** : aaa
**Prompt**
```
---
## pas un titre
```
<!-- /FICHE -->

---

<!-- FICHE:Y2 -->
## Y2 [ ] — à faire
**Session** : bbb
**Session** : aaa
<!-- /FICHE -->
"""

CARTE_MATIN = ("# Chantier courant\n\n- **alias** : mt\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact feuille de route** : https://claude.ai/artifact/FEU\n"
               "- **artefact du chantier** : https://claude.ai/artifact/LOC\n- **artefact archive** : aucune\n\n"
               "Lettres de fiche déjà prises : E (Enchaîner), ENQ (Les écritures Git). "
               "Un nouveau chantier en choisit un autre.\n")

CARTE_NIV3 = """# Chantier courant

- **alias** : niv3
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le |
|---|---|---|
| ctx/10-a.md | `A1`..`A2` | 2026-01-01 |

Lettres de fiche déjà prises : A. Un nouveau chantier en choisit une autre.
"""

CARTE_Z = ("# Chantier courant\n\n- **alias** : z\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n")

CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"

CODE = "def double(n):\n    return 2 * n\n"

DECOUPE_TETE = ("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, "
                "un sous-agent compte à la fiche que nomme son prompt, sinon à son départ\n")

ETAT_MATIN = ("# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
              "| 79 | `LOC` — publier | a | 2 fiches | — |\n| 80 | `PAR` — deux chantiers | b | 3 fiches | — |\n\n"
              "## Journal\n")

ETAT_NIV = ("# État\n\n"
            "Le plugin pose `${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py` — prose, pas un chemin lu.\n\n"
            "## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
            "|---|---|---|---|---|\n| 1 | un truc | utile | bas | — |\n")

ETAT_Z = ("# État\n\n## TODO\n\n| n° | Chantier | Apport | Coût | Décidé |\n|---|---|---|---|---|\n"
          "| 1 | un truc | utile | bas | 2026-01-02 |\n")

FICHES = """# Chantier Z

**Ouvert.** le 2026-10-08.

## Le socle commun

## Z1 [x] — faite
---
## Z2 [ ] — à faire
## Z10 [ ] — après
"""

FICHES_PLI2 = """# Chantier PLI2

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
x
<!-- /FICHE -->
"""

FICHES_PLI5 = """# Chantier PLI5

## Le socle commun

## L'ordre des fiches

<!-- FICHE:Q1 -->
## Q1 [x] — Faite
**Critère de fin**
x
<!-- /FICHE -->

<!-- FICHE:Q2 -->
## Q2 [ ] — En cours
**Critère de fin**
x
<!-- /FICHE -->

<!-- FICHE:Q3 -->
## Q3 [ ] — À faire
**Critère de fin**
x
<!-- /FICHE -->
"""

GABARIT_FEUILLE = os.path.join(SCRIPTS, "..", "templates", "artefact-feuille-de-route.html")

GABARIT_VLPCSS = os.path.join(SCRIPTS, "..", "templates", "vlp.css")

INDEX_NIV3 = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
              "| `10-a.md` | on relit le chantier A |\n"
              "| `99-fantome.md` | jamais, il n'existe pas |\n")

JOUR_MATIN = "2026-10-01"

OUVERT = "**Ouvert.** le 2026-10-08."

OUVERT_DU_JOUR = mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat()

OUVERT_LIGNE = mod.OUVERT_LIGNE   # la seconde valeur d'`OUVERT` dans l'ancienne suite maison, lue par les groupes de sa fin

PAGE = """# Chantier P

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [%s] — Créer `a.py`
%s**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P2 -->
## P2 [%s] — Brancher
%s**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P3 -->
## P3 [ ] — Finir
**Critère de fin**
<!-- /FICHE -->
"""

QFICHES = """# Chantier Q

## Le socle commun

## L'ordre des fiches

<!-- FICHE:Q1 -->
## Q1 [x] — Créer
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:Q2 -->
## Q2 [x] — Brancher
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
"""

SANS = "## Z1 [ ] — ancien\nlong\n---\n## Z2 [ ] — dernier\nfin\n"

T0 = 1790000000
