"""`vlp.py lire` (REF55) : un fichier du kit s'imprime ; un chemin qui sort du kit, par `..` ou sur un autre
disque, sort 1 par sa GARDE — jamais un traceback (`os.path.commonpath` lève entre deux lecteurs)."""
import os

import pytest

from aides import appel, lire, mod


def test_un_fichier_du_kit_s_imprime():
    code, s = appel(["lire", "cloture.md"])
    assert code == 0 and s.startswith(lire(os.path.join(mod.KIT, "cloture.md"))[:200])


def test_remonter_par_deux_points_est_hors_du_kit():
    assert appel(["lire", "../hors.md"]) == (1, "GARDE: hors du kit : ../hors.md\n")


@pytest.mark.skipif(os.name != "nt", reason="seul Windows a des lecteurs")
def test_un_autre_disque_est_hors_du_kit():
    autre = "Y:" if os.path.splitdrive(mod.KIT)[0].upper() == "Z:" else "Z:"
    assert appel(["lire", autre + "/hors.md"]) == (1, "GARDE: hors du kit : %s/hors.md\n" % autre)
