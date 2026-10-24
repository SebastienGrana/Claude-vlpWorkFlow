"""REF53 : la photo de `boucle.py` (syrupy, REF6), prise avant sa découpe, pour qu'une différence de comportement
crie : `--plafond 0` sur le projet des tests de la boucle, et `--help`, qui photographie ses arguments.

Chaque photo garde le code de sortie, la sortie (erreur comprise) et le fichier de fiches, les dossiers remplacés.
"""
import os
import subprocess
import sys
import tempfile

import pytest

from aides import SCRIPTS
from aides_boucle import boucle, projet


def propre(texte, t):
    """`texte` sans ce qui change d'un lancement à l'autre : le dossier du projet, celui du kit."""
    return texte.replace(t, "<PROJET>").replace(os.path.dirname(SCRIPTS), "<KIT>")


def test_photo_plafond_0(snapshot):
    """`boucle.py --plafond 0` : rien de joué, l'arrêt et le total dits, aucune case cochée."""
    with tempfile.TemporaryDirectory() as t:
        code, sortie, cases = boucle(t, projet(t), 0)
        with open(os.path.join(t, "fiches.md"), encoding="utf-8") as h:
            fiches = h.read()
        assert propre("code %d · cases %s\n%s--- fiches.md ---\n%s" % (code, cases, sortie, fiches), t) == snapshot


@pytest.mark.parametrize("argv", [["--help"]], ids=["help"])
def test_photo_aide(argv, snapshot):
    """`boucle.py --help` : la liste de ses arguments, à largeur fixe."""
    env = dict(os.environ, COLUMNS="100", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "boucle.py")] + argv, env=env, capture_output=True,
                       text=True, encoding="utf-8")
    assert propre("code %d\n%s%s" % (r.returncode, r.stdout, r.stderr), "\0") == snapshot
