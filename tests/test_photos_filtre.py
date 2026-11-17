"""Un lancement filtré qui laisse des photos de côté reste vert ; la suite entière garde le rouge d'une photo orpheline
(ROU2).

syrupy sort 1 dès qu'une photo ne sert pas : `vlp.py rapide <motif>` sortait rouge alors que ses tests passaient
(« 59 snapshots unused », vu à `ALG2`).
"""
import os
import shutil
import subprocess
import sys

TESTS = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(TESTS), "scripts")

# Un test paramétré, comme `test_photo` du kit : sous un filtre, syrupy ne compte « unused » que les photos dont le
# nom répond à un test lancé (`syrupy/report.py`, `unused`) — deux fonctions séparées ne reproduisent pas la panne.
DEUX_PHOTOS = '''
import pytest

@pytest.mark.parametrize("nom", [1, 2])
def test_photo(nom, snapshot):
    assert nom == snapshot
'''

UNE_PHOTO = DEUX_PHOTOS.replace("[1, 2]", "[1]")
# `--seul` lit aussi le texte du test : le motif « [1] » n'est que dans le nom `test_photo[1]`, pas dans `[1, 2]`.
MOTIF_UN = "[1]"


def pytest_dans(dossier, *args):
    """Lancer pytest dans `dossier` en sous-processus, avec les aides du kit importables et sans relance sous
    `coverage` (`VLP_COUVERTURE=1`) ; rendre (code de sortie, sortie entière décodée en UTF-8, remplacement compris)."""
    env = {k: v for k, v in os.environ.items() if k not in ("VLP_TOUS_ECARTS", "VLP_PONT")}
    env.update(VLP_COUVERTURE="1", PYTHONIOENCODING="utf-8", PYTHONPATH=os.pathsep.join([TESTS, SCRIPTS]))
    fini = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "--rootdir", str(dossier), *args],
                          cwd=dossier, env=env, capture_output=True, timeout=300)
    return fini.returncode, (fini.stdout + fini.stderr).decode("utf-8", errors="replace")


def batir_projet(tmp_path):
    """Bâtir dans `tmp_path` un projet de deux tests à photo, avec une copie de `conftest.py`, `testpaths` sur son
    dossier, et leurs deux photos écrites par syrupy (`--snapshot-update`, fichier nommé : pas la suite entière) ;
    rendre le dossier. Les photos manquent : AssertionError avec la sortie."""
    shutil.copy(os.path.join(TESTS, "conftest.py"), tmp_path / "conftest.py")
    (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = .\n", encoding="utf-8")
    (tmp_path / "test_photos.py").write_text(DEUX_PHOTOS, encoding="utf-8")
    code, sortie = pytest_dans(tmp_path, "--snapshot-update", "test_photos.py")
    assert code == 0, "photos non écrites (code %d) :\n%s" % (code, sortie)
    assert (tmp_path / "__snapshots__" / "test_photos.ambr").exists(), "photos absentes :\n" + sortie
    return tmp_path


def test_un_lancement_filtre_qui_laisse_une_photo_reste_vert(tmp_path):
    projet = batir_projet(tmp_path)
    code, sortie = pytest_dans(projet, "--seul", MOTIF_UN)
    assert "1 deselected" in sortie, "le filtre ne laisse pas une photo de côté :\n" + sortie
    assert code == 0, "lancement filtré rouge (code %d) :\n%s" % (code, sortie)


def test_la_suite_entiere_garde_le_rouge_d_une_photo_orpheline(tmp_path):
    projet = batir_projet(tmp_path)
    (projet / "test_photos.py").write_text(UNE_PHOTO, encoding="utf-8")
    code, sortie = pytest_dans(projet)
    assert code == 1, "suite entière à photo orpheline : code %d, attendu 1 :\n%s" % (code, sortie)
