"""ALG3 (dette de la clôture d'ALG) : `vlp.py couverture --depuis <rev>`, le jugement de la couverture du chantier à
sa clôture — rien à couvrir, `diff-cover` introuvable ou en échec, puis le branchement réel (git, coverage et
diff-cover vrais) sous le réglage `[tool.coverage.run]` du kit, comme `test_couverture.py` pour le commit indexé."""
import io
import os
import re
import shutil
import sys

import couverture
import pytest
from aides import RACINE, ecrire, lire
from test_couverture import APPEL, CODE, git, mesurer_ici


def depart(depot):
    """Poser dans `depot` le réglage coverage du kit, `scripts/x.py` et son appel, en un commit « départ »."""
    reglage = re.search(r"^\[tool\.coverage\.run\]\n(?:(?!\[).*\n)*", lire(os.path.join(RACINE, "pyproject.toml")), re.M)
    assert reglage, "pas de [tool.coverage.run] dans le pyproject.toml du kit"
    ecrire(str(depot / "pyproject.toml"), reglage.group(0))
    ecrire(str(depot / "scripts" / "x.py"), CODE)
    ecrire(str(depot / "appel.py"), APPEL)
    ecrire(str(depot / ".gitignore"), ".couverture/\n.coverage*\n")
    git(depot, "add", "-A")
    git(depot, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "départ")


def juger(depot, rev="HEAD~1"):
    """`couverture.juger_depuis(depot, rev)`, l'empreinte fixée à « E » : rend (code, sortie)."""
    sortie = io.StringIO()
    return couverture.juger_depuis(str(depot), rev, sortie, empreinte_de=lambda _: "E"), sortie.getvalue()


@pytest.mark.skipif(shutil.which("git") is None, reason="git absent : couverture --depuis n'est pas testé")
def test_depuis_rien_a_couvrir_puis_sans_diff_cover_puis_en_echec(depot, monkeypatch):
    depart(depot)
    ecrire(str(depot / "note.md"), "rien\n")
    git(depot, "add", "-A")
    git(depot, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "note")
    assert juger(depot)[1].startswith("COUVERTURE rien à couvrir"), "couverture --depuis : sans .py, rien à couvrir"
    ecrire(str(depot / "scripts" / "x.py"), CODE + "\n\ndef triple(n):\n    return 3 * n\n")
    git(depot, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "triple")
    monkeypatch.setattr(couverture, "rapport_a_jour", lambda _r, _e: True)
    for outil, debut in ((None, "GARDE: couverture — diff-cover introuvable"),
                         (sys.executable, "GARDE: couverture — diff-cover sorti ")):
        monkeypatch.setattr(couverture.shutil, "which", lambda _, o=outil: o)
        code, s = juger(depot)
        assert code == 1, "couverture --depuis : une GARDE\n" + s
        assert s.startswith(debut), "couverture --depuis : la bonne GARDE\n" + s


@pytest.mark.skipif(shutil.which("git") is None or shutil.which("diff-cover") is None,
                    reason="git ou diff-cover absent : le branchement n'est pas testé")
def test_depuis_refuse_une_ligne_non_couverte_puis_passe_couvert(depot):
    depart(depot)
    ecrire(str(depot / "scripts" / "x.py"), CODE + "\n\ndef triple(n):\n    return 3 * n\n")
    git(depot, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "triple")
    assert mesurer_ici(depot) == 0, "la mesure tourne"
    code, s = juger(depot)
    assert code == 1, "couverture --depuis : une ligne nue refuse la clôture\n" + s
    assert "NON COUVERT scripts/x.py : 6\n" in s, "couverture --depuis : la ligne nommée\n" + s
    assert s.endswith("— clôture refusée\n"), "couverture --depuis : le mot de la clôture\n" + s
    ecrire(str(depot / "appel.py"), APPEL + "assert x.triple(2) == 6\n")
    assert mesurer_ici(depot) == 0, "la mesure tourne"
    code, s = juger(depot)
    assert code == 0, "couverture --depuis : couvert, la clôture passe\n" + s
    assert s.endswith("— passe\n"), "couverture --depuis : passe\n" + s
