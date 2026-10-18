"""`vlp.py lire` : un fichier du kit s'imprime tel quel, `${CLAUDE_PLUGIN_ROOT}` remplacé par la racine du kit en barres
obliques (REF27) ; un chemin qui sort du kit, par `..` ou sur un autre disque (REF55), sort 1 par sa GARDE — jamais un
traceback (`os.path.commonpath` lève entre deux lecteurs). Migré de `tester_lire_kit` (l'ancienne suite maison, REF8)."""
import os

import pytest
from aides import appel, lire, mod


def attendu_et_source():
    source = lire(os.path.join(mod.etat.KIT, "cloture.md"))
    racine = os.path.realpath(mod.etat.KIT).replace("\\", "/")
    attendu = source.replace("${CLAUDE_PLUGIN_ROOT}", racine)
    return (attendu if attendu.endswith("\n") else attendu + "\n"), source, racine


def test_un_fichier_du_kit_tel_quel():
    attendu, _, _ = attendu_et_source()
    r = appel(["lire", "cloture.md"])
    assert r == (0, attendu), "lire : un fichier du kit, tel quel" + " · %r" % (r[1][:200],)


def test_la_racine_du_kit_remplace_la_variable():
    _, source, racine = attendu_et_source()
    s = appel(["lire", "cloture.md"])[1]
    assert source.count("${CLAUDE_PLUGIN_ROOT}") > 0 and "CLAUDE_PLUGIN_ROOT" not in s \
        and '"%s/scripts/vlp.py"' % racine in s, \
        "lire : ${CLAUDE_PLUGIN_ROOT} remplacé par la racine du kit (%d dans la source)" \
        % source.count("${CLAUDE_PLUGIN_ROOT}") + " · %r" % (s[:300],)


def test_hors_du_kit_et_absent_sortent_1():
    attendu, _, _ = attendu_et_source()
    code, s = appel(["lire", "cloture.md", "../hors.md", "absent.md", "cloture.md"])
    assert code == 1 and s == attendu + "GARDE: hors du kit : ../hors.md\nABSENT absent.md\n" + attendu, \
        "lire : hors du kit et absent sortent 1, le reste imprimé" + " · %r" % (s[-200:],)


@pytest.mark.skipif(os.name != "nt", reason="seul Windows a des lecteurs")
def test_un_autre_disque_est_hors_du_kit():
    autre = "Y:" if os.path.splitdrive(mod.etat.KIT)[0].upper() == "Z:" else "Z:"
    assert appel(["lire", autre + "/hors.md"]) == (1, "GARDE: hors du kit : %s/hors.md\n" % autre)
