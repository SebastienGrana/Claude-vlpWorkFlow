"""Ce qui reste des suites voisines, migrées vers pytest par REF52 (`test_boucle.py`, `test_boucle_canal.py`,
`test_mesure_tokens.py`) : la boucle sous les variables de la nuit (ENV1), puis l'option `--seul` de `conftest.py`
(VIT10, choix Q2 : A)."""
import os
import subprocess
import sys
import tempfile
import time

from aides import RACINE, mod, porte_motif


def test_boucle_nuit():
    """ENV1 : une fiche de nuit lance la suite sous ses variables ; `isoler` (`conftest.py`) les retire à chaque test.
    Ce test les pose au seul test de la boucle qui les attend absentes, pour que leur retrait se voie."""
    debut = time.perf_counter()
    code, texte = lancer_pytest("tests/test_boucle_canal.py::test_sans_nuit", VLP_NUIT="1", VLP_CANAL="B",
                                VLP_CARNET=os.path.join(tempfile.gettempdir(), "carnet-env1.jsonl"))
    assert code == 0 and "1 passed" in texte and "ÉCART" not in texte, (
        "ENV1 : test_sans_nuit, sous les trois variables de la nuit, passe sans ÉCART "
        "— mutant : le retrait des variables de la nuit dans `isoler` neutralisé") + "\n" + str(
        (time.perf_counter() - debut, texte))


def _temoin_nom():
    """Un témoin, retenu par son nom."""


def _temoin_aide():
    """Un témoin qui appelle une aide du module."""
    _aide_du_temoin()


def _aide_du_temoin():
    """Le libellé « une aide Vit10-Témoin » vit ici."""


def test_porte_motif():
    """VIT10 : le nom, le texte, ou celui d'une aide nommée, sans casse ; ni l'un ni l'autre, écarté."""
    assert porte_motif(_temoin_nom, "TEMOIN_NOM"), "seul : le nom porte le motif, sans casse — mutant : casse comptée"
    assert porte_motif(_temoin_nom, "retenu PAR son nom"), "seul : le texte porte le motif, sans casse"
    assert not porte_motif(_temoin_nom, "autre-motif"), "seul : ni le nom ni le texte, écarté"
    assert porte_motif(_temoin_aide, "vit10-témoin") and not porte_motif(_temoin_nom, "vit10-témoin"), \
        "seul : le texte d'une aide du module que le test appelle porte le motif — mutant : aides ignorées"
    assert porte_motif(_temoin_nom, "cas-b", "test_x[cas-b]"), "seul : l'id d'un test paramétré compte comme son nom"


def lancer_pytest(*args, **env):
    """Lancer pytest sur ce kit avec `args`, sous les variables `env` en plus ; rendre (code de sortie, sortie)."""
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", *args], cwd=RACINE, capture_output=True,
                       encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8", **env))
    return r.returncode, r.stdout + r.stderr


def test_seul_ne_joue_que_ses_tests():
    """`--seul` garde les seuls tests qui portent le motif, et la session finit sur `OK`."""
    code, s = lancer_pytest("tests/test_commun.py", "--seul", "LEC :")
    assert code == 0 and "1 passed" in s and "deselected" in s and s.strip().endswith("OK"), \
        "seul : pytest ne joue que le test qui porte le motif, puis OK" + "\n" + s


def test_seul_sans_test_sort_1():
    """Un motif que rien ne porte : `GARDE:` et sortie 1 — un motif mal tapé ne passe pas pour une suite verte."""
    code, s = lancer_pytest("tests/test_commun.py", "--seul", "motif-que-rien-ne-porte")
    assert code == 1 and "GARDE: aucun groupe ne porte « motif-que-rien-ne-porte »" in s, \
        "seul : aucun test retenu → GARDE et sortie 1" + "\n" + s


def test_commande_suite():
    """La commande de la suite du kit : pytest par `uv`, dans l'environnement du projet nommé, sur 4 processus ou en
    série — ce que `rapide` et `mutant` lancent (REF59)."""
    entiere, serie = mod.commande_suite("K"), mod.commande_suite("K", parallele=False)
    assert entiere[1:] == ["run", "--frozen", "--project", "K", "pytest", "-q", "-n", "4"], entiere
    assert serie[1:] == ["run", "--frozen", "--project", "K", "pytest", "-q"] and serie[0] == entiere[0], serie


def test_sans_parallele():
    """`sans_parallele` ôte `-n <n>` et lui seul : `--seul` filtre à la collecte, que pytest-xdist fait ailleurs."""
    assert mod.sans_parallele(["uv", "run", "pytest", "-q", "-n", "4", "--seul", "x"]) == [
        "uv", "run", "pytest", "-q", "--seul", "x"]
    assert mod.sans_parallele(["py", "suite.py", "--seul", "-n"]) == ["py", "suite.py", "--seul"]   # -n sans valeur, en fin
    assert mod.sans_parallele(["py", "suite.py"]) == ["py", "suite.py"]