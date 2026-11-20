"""Un test rouge dont le message porte « → » se compte sous `pytest -n`, même sur une console cp1252 (ROU1).

La ligne `ÉCART:` de `conftest.py` levait `UnicodeEncodeError` : pytest finissait en `INTERNALERROR` et le rouge
se perdait (« 1 failed, 3 passed » pour 5 tests, vu à `ALG1` et `ALG5`).
"""
import os
import shutil
import subprocess
import sys

TESTS = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(TESTS), "scripts")

CINQ_TESTS = '''
def test_un():
    assert True

def test_deux():
    assert True

def test_trois():
    assert True

def test_quatre():
    assert True

def test_rouge():
    assert 1 == 2, "attendu 1 → reçu 2"
'''


def jouer_cinq_tests(tmp_path):
    """Bâtir dans `tmp_path` un projet de 5 tests (1 rouge à « → ») avec une copie de `conftest.py`, le jouer sous
    `pytest -n 2` en sous-processus, console en cp1252 ; rendre la sortie entière (stdout puis stderr), décodée en
    cp1252 avec remplacement — un octet hors de cp1252 n'arrête pas la lecture."""
    shutil.copy(os.path.join(TESTS, "conftest.py"), tmp_path / "conftest.py")
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / "test_cinq.py").write_text(CINQ_TESTS, encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "VLP_TOUS_ECARTS")}
    env["PYTHONIOENCODING"] = "cp1252"
    env["PYTHONPATH"] = os.pathsep.join([TESTS, SCRIPTS])
    fini = subprocess.run([sys.executable, "-m", "pytest", "-n", "2", "-p", "no:cacheprovider",
                           "--rootdir", str(tmp_path), "test_cinq.py"],
                          cwd=tmp_path, env=env, capture_output=True, timeout=300, check=False)
    return (fini.stdout + fini.stderr).decode("cp1252", errors="replace")


def test_un_rouge_a_fleche_se_compte_sous_n(tmp_path):
    sortie = jouer_cinq_tests(tmp_path)
    assert "INTERNALERROR" not in sortie, "pytest plante sur la ligne ÉCART :\n" + sortie
    assert "1 failed, 4 passed" in sortie, "le résumé ne compte pas les 5 tests :\n" + sortie
    ecarts = [ligne for ligne in sortie.splitlines() if ligne.startswith("ÉCART: ")]
    assert len(ecarts) == 1, "attendu une ligne ÉCART, vu %d :\n%s" % (len(ecarts), sortie)
    assert ecarts[0].endswith(" — test_cinq.py::test_rouge"), "la ligne ÉCART perd sa forme : " + ecarts[0]
