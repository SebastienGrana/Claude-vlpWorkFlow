"""REF13 : les tests concernés par des fonctions, lus dans la couverture par test (`dynamic_context = "test_function"`,
choix `Q3` de la note `122`, TDAD). La mesure se bâtit par l'API de coverage, dans un projet temporaire ; la lecture,
elle, n'utilise que `sqlite3` (aucun paquet à l'exécution)."""
import io
import os

import concernes
import coverage
from aides import ecrire

MODULE = "def f():\n    return 1\n\n\ndef g():\n    return 2\n"


def projet(tmp_path, arcs=True):
    """Un projet : `scripts/m.py` (`f` lignes 1–2, `g` lignes 5–6) et une mesure où `test_m.test_f` passe par `f`,
    `test_m.test_g` par `g`, et le contexte vide par les deux (l'import). Rend sa racine."""
    t = str(tmp_path / "p")
    m = os.path.join(t, "scripts", "m.py")
    ecrire(m, MODULE)
    os.makedirs(os.path.join(t, ".couverture"))
    d = coverage.CoverageData(basename=os.path.join(t, ".couverture", "donnees"))
    for contexte, lignes in (("", [1, 5]), ("test_m.test_f", [2]), ("test_m.test_g", [6])):
        d.set_context(contexte)
        if arcs:
            d.add_arcs({m: [(-1, n) for n in lignes] + [(n, -1) for n in lignes]})
        else:
            d.add_lines({m: lignes})
    d.write()
    return t


def test_fonctions(tmp_path):
    """Où vit une fonction : chemin relatif, première et dernière ligne ; une fonction absente n'a rien."""
    t = projet(tmp_path)
    assert concernes.fonctions(t, ["f", "g", "h"]) == {"f": [("scripts/m.py", 1, 2)], "g": [("scripts/m.py", 5, 6)]}, (
        "concernes : les fonctions et leurs lignes")


def test_concernes_arcs_et_lignes(tmp_path):
    """Les tests qui passent par une fonction : par les arcs (branches mesurées) comme par les lignes ; le contexte
    vide (hors d'un test) ne compte pas."""
    for arcs in (True, False):
        t = projet(tmp_path / str(arcs), arcs)
        assert concernes.concernes(t, ["f"]) == (["test_m.test_f"], []), "concernes : f → test_f seul (%s)" % arcs
        assert concernes.concernes(t, ["f", "g", "h"]) == (["test_m.test_f", "test_m.test_g"], ["h"]), (
            "concernes : f et g, h absente (%s)" % arcs)


def test_principal(tmp_path):
    """La sous-commande : la liste et son compte ; sans mesure, ou sans contexte par test, une `GARDE:`."""
    t = projet(tmp_path)
    s = io.StringIO()
    assert concernes.principal(["f", "h", "--racine", t], s) == 0, s.getvalue()
    assert s.getvalue() == "ABSENTE h\nCONCERNES 1 test(s) pour f\n  test_m.test_f\n", s.getvalue()
    s = io.StringIO()
    assert concernes.principal(["f", "--racine", str(tmp_path)], s) == 1 and s.getvalue().startswith(
        "GARDE: concernes — pas de mesure"), s.getvalue()
    sans = str(tmp_path / "sans")
    ecrire(os.path.join(sans, "scripts", "m.py"), MODULE)
    os.makedirs(os.path.join(sans, ".couverture"))
    d = coverage.CoverageData(basename=os.path.join(sans, ".couverture", "donnees"))
    d.add_lines({os.path.join(sans, "scripts", "m.py"): [1, 2]})
    d.write()
    s = io.StringIO()
    assert concernes.principal(["f", "--racine", sans], s) == 1 and "contexte par test" in s.getvalue(), s.getvalue()


def test_ligne_carte(tmp_path):
    """La ligne de la carte : les fonctions que la fiche nomme entre accents graves, leurs tests ; rien sans mesure."""
    t = projet(tmp_path)
    fiche = "## X1 [ ] — titre\n**Fichiers** : `scripts/m.py` (`f`, `inconnue`).\n"
    assert concernes.ligne_carte(t, "X1", fiche) == "CONCERNES X1=1 test(s) pour f : test_m.test_f", (
        concernes.ligne_carte(t, "X1", fiche))
    assert concernes.ligne_carte(t, "X1", "rien de nommé") is None, "concernes : rien de nommé, pas de ligne"
    assert concernes.ligne_carte(str(tmp_path), "X1", fiche) is None, "concernes : sans mesure, pas de ligne"
