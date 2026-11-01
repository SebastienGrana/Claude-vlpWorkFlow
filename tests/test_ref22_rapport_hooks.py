"""REF22 (l'angle des bugs) : quatre défauts rejoués, un test chacun, écrit avant sa correction.

- le juge hors kit d'un mutant : un `unittest` qui attrape le mutant n'est pas un juge planté (`verdict_juge`) ;
- le contrat Git : le motif cité d'un `grep`/`Select-String`/`--grep=` n'est pas un appel Git (`ecrit_git`) ;
- le gel des tests : la racine se cherche depuis le fichier visé, pas depuis `cwd` (`cible_test`) ;
- les nuits : une leçon déjà retirée, passée entière, ne prend pas un second suffixe (`nuits_retirer`).
"""
import io
import os
import sys

from aides import ecrire, lire, mod

H = mod.noyau.hooks
R = mod.noyau.rapport
N = mod.noyau.nuit

JUGE_UNITTEST = '''import sys
import unittest

F = sys.argv[1]


class T(unittest.TestCase):
    def test_x(self):
        ns = {}
        with open(F, encoding="utf-8") as f:
            exec(f.read(), ns)
        self.assertEqual(ns["x"] + 1, 2)


unittest.main(argv=[sys.argv[0]])
'''


def test_ref22_juge_unittest_attrape_n_est_pas_plante(tmp_path):
    """REF22 : un juge `unittest` sorti 1 sur un `assertEqual` raté imprime `Traceback` et `AssertionError:` — il a
    tourné et attrapé le mutant : `ATTRAPÉ`, pas `PLANTÉ`. Un juge qui n'a pas tourné reste `PLANTÉ`."""
    f, juge = str(tmp_path / "f.py"), str(tmp_path / "juge.py")
    ecrire(f, "x = 1\n")
    ecrire(juge, JUGE_UNITTEST)
    o = io.StringIO()
    code = mod.main(["mutant", f, "x = 1", "x = 2", "--test", '"%s" "%s" "%s"' % (sys.executable, juge, f)], o)
    assert (code, "MUTANT ATTRAPÉ · juge hors kit sorti 1" in o.getvalue()) == (0, True), (
        "REF22 : unittest qui attrape le mutant → ATTRAPÉ") + "\n" + o.getvalue()
    assert lire(f) == "x = 1\n", "REF22 : le fichier muté est rendu tel quel"

    pytest_natif = ["Traceback (most recent call last):", "AssertionError: 2 != 3", "1 failed in 0.05s"]
    plante = ["Traceback (most recent call last):", "ModuleNotFoundError: No module named 'x'"]
    erreur_seule = ["Traceback (most recent call last):", "TypeError: bad", "FAILED (errors=1)"]
    vus = [R.verdict_juge(lignes, 1, None)[0].split(" ·")[0] for lignes in (pytest_natif, plante, erreur_seule)]
    assert vus == ["MUTANT ATTRAPÉ", "MUTANT PLANTÉ", "MUTANT PLANTÉ"], (
        "REF22 : pytest --tb=native « 1 failed » → ATTRAPÉ ; une erreur sans test raté reste PLANTÉ") + "\n" + repr(vus)


def test_ref22_motif_cite_d_un_grep_n_ecrit_pas_git():
    """REF22 : le motif cité d'un `grep`, d'un `Select-String` ou d'un `--grep=` est une donnée, pas un appel Git ;
    `ssh h 'git commit'` et `bash -c "git commit"` restent des écritures."""
    lit = ['grep -n "git push" methode-chantier.md', "Select-String -Pattern 'git commit' f.md",
           'git log --grep="git commit"', 'git log --oneline | grep "git add"', "rg 'git reset' scripts",
           'grep -E "git (push|commit)" f', "x | sls 'git push'", "findstr \"git commit\" f.txt"]
    ecrit = ["ssh h 'git commit'", 'bash -c "git commit"', 'grep x f; bash -c "git commit"',
             'grep "a" f | sh -c \'git push\'', 'grep "$(git stash)" f', "git log --grep=x && git push"]
    faux = [c for c in lit if H.ecrit_git(c)] + [c for c in ecrit if not H.ecrit_git(c)]
    assert not faux, "REF22 : motif de grep cité muet, appel cité de ssh/bash lu" + "\n" + repr(faux)


def test_ref22_cible_test_racine_du_fichier_vise(tmp_path):
    """REF22 : depuis le dossier principal, un test d'un worktree (`.claude/worktrees/w/tests/…`) se juge à la
    racine du worktree — le gel des tests ne saute plus."""
    principal = tmp_path / "principal"
    w = principal / ".claude" / "worktrees" / "w"
    ecrire(str(principal / "CHANTIER.md"), "# Chantier courant\n")
    ecrire(str(w / "CHANTIER.md"), "# Chantier courant\n")
    ecrire(str(w / "tests" / "test_a.py"), "def test_a():\n    assert 1 == 1\n")
    change = {"old_string": "1 == 1", "new_string": "2 == 2"}
    absolu = H.cible_test({"tool_input": dict(change, file_path=str(w / "tests" / "test_a.py")),
                           "cwd": str(principal)})
    relatif = H.cible_test({"tool_input": dict(change, file_path=".claude/worktrees/w/tests/test_a.py"),
                            "cwd": str(principal)})
    assert absolu == relatif == (str(w), "tests/test_a.py"), (
        "REF22 : la racine du worktree visé, pas celle de cwd") + "\n" + repr((absolu, relatif))


def test_ref22_nuits_retirer_deja_retiree_entiere(tmp_path):
    """REF22 : une leçon déjà retirée, passée entière (suffixe compris), rend False et le fichier ne bouge pas."""
    lecon = "- 2026-09-26 · N=2 · cause un · jouées 3 sur 5 · nuits 2026-09-25 · sessions s1"
    retiree = lecon + " — retirée le 2026-09-27 par NUI12"
    chemin = str(tmp_path / "101-nuits.md")
    texte = ("# Nuits\n\n| nuit | a | b | c | d |\n|---|---|---|---|---|\n\n## Leçons\n\n%s\n" % retiree)
    ecrire(chemin, texte)
    rendu = N.nuits_retirer(chemin, retiree, "2026-09-28", "REF22")
    court = N.nuits_retirer(chemin, lecon, "2026-09-28", "REF22")
    assert (rendu, court, lire(chemin)) == (False, False, texte), (
        "REF22 : déjà retirée → False, rien écrit") + "\n" + lire(chemin)


def test_ref22_rapide_pyright_voit_l_atelier(tmp_path):
    """REF22 : `rapide` lance pyright avec le Python de `.venv` — sans lui, un test qui importe `pytest` est rouge."""
    sans = R.commande_pyright(str(tmp_path), "pyright")
    python = tmp_path / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / (
        "python.exe" if sys.platform == "win32" else "python")
    ecrire(str(python), "")
    avec = R.commande_pyright(str(tmp_path), "pyright")
    assert (sans, avec, R.commande_pyright(str(tmp_path), None)) == (
        ["pyright"], ["pyright", "--pythonpath", str(python)], None), "REF22 : rapide, pyright voit l'atelier"
