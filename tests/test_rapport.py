"""La décision de `py_touches` (`noyau/rapport.py`), sans Git (REF49) : `py_du_statut` lit `git status -z`."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import rapport


def test_py_du_statut():
    texte = " M scripts/a.py\0?? tests/neuf.py\0R  b.py\0ancien.py\0 M notes.md\0"
    assert rapport.py_du_statut(texte) == ["scripts/a.py", "tests/neuf.py", "b.py"]
    assert rapport.py_du_statut("") == []
