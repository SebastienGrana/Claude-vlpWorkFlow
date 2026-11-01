"""`sante --base` dans un worktree en retard sur `main` (REF39, défaut `E22`) : la base du cliquet s'y recalait sur
un état ancien — remise à la main deux fois (`AVL1`, `AVL2`). Il en sort une `GARDE:` qui nomme le retard, rien écrit.
"""
import os
import pathlib
import subprocess

from aides import appel, ecrire

BASE = os.path.join("scripts", "sante-base.json")
F = 'def f(a):\n    """Rendre a."""\n    return a\n'
G = '\n\ndef g(a):\n    """Rendre a."""\n    return a\n'


def git(d, *args):
    """`git <args>` dans `d` : sa sortie."""
    return subprocess.run(["git", *args], cwd=d, capture_output=True, encoding="utf-8", check=True).stdout


def test_sante_base_refuse_un_worktree_en_retard(depot, tmp_path):
    d, wt = str(depot), str(tmp_path / "wt")
    ecrire(os.path.join(d, "scripts", "m.py"), F)
    assert appel(["sante", "--base", "--racine", d, "--sans-ruff"])[0] == 0
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "c1")
    git(d, "worktree", "add", "-q", "-b", "retard", wt)
    ecrire(os.path.join(d, "scripts", "m.py"), F + G)
    git(d, "commit", "-q", "-am", "c2")
    ecrire(os.path.join(wt, "scripts", "n.py"), F.replace("def f", "def h"))     # une écriture changerait la base
    avant = pathlib.Path(wt, BASE).read_bytes()
    en_retard = appel(["sante", "--base", "--si-base", "--racine", wt, "--sans-ruff"])
    reste = pathlib.Path(wt, BASE).read_bytes()
    os.remove(os.path.join(wt, "scripts", "n.py"))
    git(wt, "merge", "-q", "main")
    a_jour = appel(["sante", "--base", "--si-base", "--racine", wt, "--sans-ruff"])
    sur_main = appel(["sante", "--base", "--racine", d, "--sans-ruff"])
    assert en_retard[0] == 1, "REF39 (a) worktree en retard sur main → sort 1" + "\n" + str(en_retard)
    assert en_retard[1].startswith("GARDE: "), "REF39 (b) worktree en retard sur main → GARDE:" + "\n" + str(en_retard)
    assert "1 commit(s) de main" in en_retard[1], "REF39 (c) la GARDE: nomme le retard" + "\n" + str(en_retard)
    assert reste == avant, "REF39 (d) worktree en retard sur main → base inchangée à l'octet"
    assert a_jour == (0, "BASE scripts/sante-base.json · 2 fonctions · sans ruff\n"), (
        "REF39 (e) worktree à jour → base écrite") + "\n" + str(a_jour)
    assert sur_main == (0, "BASE scripts/sante-base.json · 2 fonctions · sans ruff\n"), (
        "REF39 (f) le dossier principal sur main → base écrite") + "\n" + str(sur_main)
