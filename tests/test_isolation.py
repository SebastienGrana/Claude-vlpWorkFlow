"""L'isolation de `conftest.py` (REF4, D3), prouvée : le dossier personnel que le kit lit est celui du test."""
import os
import subprocess


def test_le_dossier_personnel_est_celui_du_test(isoler):
    """`os.path.expanduser("~")` — ce que `essais_de` et ses voisins lisent — vaut le dossier du test : sous
    Windows il suit `USERPROFILE`, ailleurs `HOME`."""
    assert os.path.normcase(os.path.expanduser("~")) == os.path.normcase(str(isoler)), \
        "isolation : le dossier personnel lu est celui du test"


def test_git_ne_lit_que_la_config_du_test(depot):
    """Ni la config globale de la machine ni celle du système : `git config --list --show-origin` ne nomme que le
    dépôt du test, ou rien."""
    sortie = subprocess.run(["git", "config", "--list", "--show-origin"], cwd=depot, capture_output=True,
                            encoding="utf-8", check=True).stdout
    origines = {l.split("\t", 1)[0] for l in sortie.splitlines() if l}
    assert all(o.startswith("file:.git/") for o in origines), "isolation : Git ne lit que la config du test"
