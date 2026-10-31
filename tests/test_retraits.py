"""REF11 : un test retiré ou affaibli se voit au commit (`vlp.py retraits`, lancé par `.githooks/commit-msg`). Les
comptes se testent en mémoire ; le jugement, sur un dépôt temporaire, puis le hook branché pour de vrai."""
import io
import os
import shutil
import subprocess
import sys

import retraits
from aides import RACINE, ecrire

DEUX = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n    verifier('b', True)\n"


def test_compter():
    """Les comptes d'un fichier : tests, `verifier`, `assert`, et `skip`/`xfail` sous toutes leurs formes."""
    assert retraits.compter(DEUX) == {"tests": 2, "verifier": 1, "assert": 2, "skip": 0}, "retraits : les comptes"
    skips = ("import pytest\n@pytest.mark.skip\ndef test_a():\n    pytest.skip('x')\n\n\n"
             "@pytest.mark.xfail\ndef test_b():\n    pytest.importorskip('y')\n")
    assert (retraits.compter(skips) or {}).get("skip") == 4, "retraits : skip, xfail et importorskip comptent"
    assert retraits.compter("def test_(:\n") is None, "retraits : un fichier illisible n'a pas de compte"


def test_ecarts_et_raison():
    """Une baisse des tests, `verifier` ou `assert`, une hausse des `skip` : un écart chacune ; la raison se lit hors
    des commentaires du message."""
    avant = {"tests": 2, "verifier": 1, "assert": 2, "skip": 0}
    assert retraits.ecarts(avant, avant) == [], "retraits : rien de changé, rien à dire"
    assert retraits.ecarts(avant, dict(avant, **{"tests": 3, "assert": 9})) == [], "retraits : une hausse des tests passe"
    assert retraits.ecarts(avant, dict(avant, tests=1, skip=1)) == ["tests 2 → 1", "skip 0 → 1"], (
        "retraits : un test en moins, un skip en plus")
    assert retraits.raison("REF11 : x\n\nTest retiré : doublon de test_b\n"), "retraits : la ligne de raison"
    assert not retraits.raison("REF11 : x\n# Test retiré : doublon\n"), "retraits : un commentaire ne compte pas"
    assert not retraits.raison("Test retiré : \n"), "retraits : une raison vide ne compte pas"


def depot(tmp_path, init_git):
    """Un dépôt : `tests/test_a.py` à deux tests, commité ; rend (dossier, git)."""
    d = str(tmp_path / "d")
    ecrire(os.path.join(d, "tests", "test_a.py"), DEUX)
    init_git(d)

    def git(*args):
        r = subprocess.run(["git", "-C", d, *args], capture_output=True, encoding="utf-8", errors="replace",
                           check=False)
        return r.returncode, r.stdout + r.stderr
    git("add", "-A")
    git("commit", "-q", "-m", "init")
    return d, git


def juger(d, message):
    """`retraits.juger` sur l'index de `d` : rend (code, sortie)."""
    s = io.StringIO()
    return retraits.juger(d, message, s), s.getvalue()


def test_juger(tmp_path, init_git):
    """Le jugement de l'index contre `HEAD` : un test retiré, un `skip` ajouté → refusé ; avec la raison → accepté ;
    un test déplacé d'un fichier à l'autre → accepté."""
    d, git = depot(tmp_path, init_git)
    a = os.path.join(d, "tests", "test_a.py")
    ecrire(a, "def test_a():\n    assert 1\n")
    git("add", "-A")
    code, s = juger(d, "x\n")
    assert code == 1 and "tests 2 → 1" in s and "Test retiré : <raison>" in s, (
        "retraits : un test retiré, commit refusé\n" + s)
    assert juger(d, "x\n\nTest retiré : doublon\n")[0] == 0, "retraits : avec la raison, accepté"

    ecrire(os.path.join(d, "tests", "test_b.py"), "def test_b():\n    assert 2\n    verifier('b', True)\n")
    git("add", "-A")
    code, s = juger(d, "x\n")
    assert code == 0, "retraits : un test déplacé d'un fichier à l'autre, accepté\n" + s

    ecrire(a, "import pytest\n" + DEUX.replace("def test_a", "@pytest.mark.skip\ndef test_a"))
    git("rm", "-q", "--cached", "tests/test_b.py")
    git("add", "tests/test_a.py")
    code, s = juger(d, "x\n")
    assert code == 1 and "skip 0 → 1" in s, "retraits : un skip ajouté, commit refusé\n" + s


def test_juger_sans_head(tmp_path, init_git):
    """Le premier commit d'un dépôt : rien à comparer, accepté."""
    d = str(tmp_path / "neuf")
    ecrire(os.path.join(d, "tests", "test_a.py"), DEUX)
    init_git(d)
    code, s = juger(d, "x\n")
    assert code == 0 and "premier commit" in s, "retraits : sans HEAD, rien à comparer\n" + s


def test_hook_commit_msg(tmp_path, init_git):
    """Le hook branché : `git commit` refuse un test retiré, et l'accepte avec la ligne de raison."""
    d, git = depot(tmp_path, init_git)
    shutil.copytree(os.path.join(RACINE, "scripts"), os.path.join(d, "scripts"))
    os.makedirs(os.path.join(d, ".githooks"))
    shutil.copy(os.path.join(RACINE, ".githooks", "commit-msg"), os.path.join(d, ".githooks", "commit-msg"))
    ecrire(os.path.join(d, ".git", "info", "exclude"), "scripts/\n.githooks/\n")
    git("config", "core.hooksPath", ".githooks")
    ecrire(os.path.join(d, "tests", "test_a.py"), "def test_a():\n    assert 1\n")
    git("add", "-A")
    code, s = git("commit", "-q", "-m", "retire b")
    assert code != 0 and "tests 2 → 1" in s, "retraits : le hook commit-msg refuse un test retiré\n" + s
    code, s = git("commit", "-q", "-m", "retire b", "-m", "Test retiré : doublon de test_a")
    assert code == 0, "retraits : le hook accepte la ligne de raison\n" + s


def test_principal(tmp_path, init_git):
    """`vlp.py retraits` lancé par son aiguillage : un message lu ; un test illisible se dit ; un dépôt sans test passe ;
    un message absent rend une `GARDE:`."""
    d, git = depot(tmp_path, init_git)
    msg = str(tmp_path / "msg.txt")
    ecrire(msg, "x\n")
    ecrire(os.path.join(d, "tests", "test_c.py"), "def test_c(:\n")
    git("add", "-A")
    r = subprocess.run([sys.executable, os.path.join(RACINE, "scripts", "vlp.py"), "retraits", msg, "--racine", d],
                       capture_output=True, encoding="utf-8", errors="replace", check=False)
    assert r.returncode == 0 and "ILLISIBLE tests/test_c.py" in r.stdout, (
        "retraits : un test illisible se dit, sans rien retirer\n" + r.stdout + r.stderr)
    vide = str(tmp_path / "vide")
    ecrire(os.path.join(vide, "a.md"), "a\n")
    init_git(vide)
    subprocess.run(["git", "-C", vide, "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", vide, "commit", "-q", "-m", "a"], check=True, capture_output=True)
    s = io.StringIO()
    assert retraits.principal([msg, "--racine", vide], s) == 0 and "passe" in s.getvalue(), (
        "retraits : un dépôt sans test passe\n" + s.getvalue())
    s = io.StringIO()
    assert retraits.principal([str(tmp_path / "absent.txt")], s) == 1 and s.getvalue().startswith("GARDE:"), (
        "retraits : un message illisible rend une GARDE\n" + s.getvalue())
