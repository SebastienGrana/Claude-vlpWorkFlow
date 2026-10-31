"""REF14 : `relecture` liste d'office, sous les yeux du relecteur, tout test modifié, supprimé, mis en `skip` ou affaibli
— les comptes de `retraits.py` (REF11), fichier par fichier, puis leur somme. La décision d'abord, sur le texte qu'un
`git diff --name-status` aurait rendu ; puis un vrai dépôt, pour le branchement dans `cmd_relecture`.
"""
import os
import shutil
import subprocess
import tempfile

import pytest
from aides import appel, ecrire
from noyau import relecture

CHANTIER = "# Chantier courant\n\n- **alias** : px\n- **contexte** : .\n"


def test_tests_touches_liste_chaque_test_change():
    """Une découpe qui déplace un test ne se signale pas : seule la somme dit le retrait."""
    avant = {"tests/test_a.py": "def test_x():\n    assert 1\n    assert 2\n",
             "tests/test_b.py": "def test_y():\n    assert 1\n",
             "tests/test_c.py": "def test_z():\n    assert 1\n",
             "tests/test_d.py": "def test_w():\n    assert 1\n"}
    apres = {"tests/test_a.py": "import pytest\n@pytest.mark.skip\ndef test_x():\n    assert 1\n",
             "tests/test_e.py": "def test_z():\n    assert 1\n",
             "tests/test_d.py": "def test_w(:\n",
             "tests/test_n.py": "def test_n():\n    assert 1\n"}
    etat = "M\ttests/test_a.py\nD\ttests/test_b.py\nR100\ttests/test_c.py\ttests/test_e.py\nM\ttests/test_d.py\n" \
           "A\ttests/test_n.py\nM\tscripts/vlp.py\n"
    lignes = relecture.tests_touches(etat, avant.get, apres.get)
    assert lignes == ["TEST MODIFIÉ tests/test_a.py — assert 2 → 1, skip 0 → 1",
                      "TEST SUPPRIMÉ tests/test_b.py — tests 1 → 0, assert 1 → 0",
                      "TEST RENOMMÉ tests/test_c.py → tests/test_e.py",
                      "TEST MODIFIÉ tests/test_d.py — illisible",
                      "TEST AJOUTÉ tests/test_n.py",
                      "RETRAITS tests 4 → 3, assert 5 → 3, skip 0 → 1"], lignes
    assert relecture.tests_touches("M\tscripts/vlp.py\n", avant.get, apres.get) == [], "aucun test touché : rien"
    assert relecture.tests_touches("M\ttests/test_a.py\n", avant.get, avant.get) == [
        "TEST MODIFIÉ tests/test_a.py", "RETRAITS rien de retiré ni d'affaibli"]


def test_relecture_liste_un_test_affaibli(tmp_path, init_git):
    """`relecture` imprime la ligne `TEST` d'un test affaibli, puis `RETRAITS`, avant le diff."""
    if not shutil.which("git"):
        pytest.skip("git absent — relecture n'est pas testée")
    env = dict(os.environ, GIT_CONFIG_GLOBAL=str(tmp_path / "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    ecrire(env["GIT_CONFIG_GLOBAL"], "")
    depot = str(tmp_path / "r")
    ecrire(os.path.join(depot, "CHANTIER.md"), CHANTIER)
    ecrire(os.path.join(depot, "f.md"), "# Chantier X\n\n**Ouvert.** le 2026-10-31.\n\n## Le socle commun\n\nSocle X.\n\n"
                                        "## L'ordre des fiches\n\n---\n\n<!-- FICHE:X1 -->\n## X1 [ ] — relire\n\n"
                                        "**Fichiers** : `tests/test_a.py`.\n<!-- /FICHE -->\n")
    ecrire(os.path.join(depot, "tests", "test_a.py"), "def test_a():\n    assert 1\n    assert 2\n")
    init_git(depot)
    for args in (["add", "-A"], ["commit", "-q", "-m", "init"]):
        subprocess.run(["git", *args], cwd=depot, env=env, check=True, capture_output=True)
    ecrire(os.path.join(depot, "tests", "test_a.py"), "def test_a():\n    assert 1\n")
    ici, tmp = os.getcwd(), tempfile.tempdir
    tempfile.tempdir = str(tmp_path)
    os.chdir(depot)
    try:
        code, s = appel(["relecture", "X1"])
        assert code == 0 and "TEST MODIFIÉ tests/test_a.py — assert 2 → 1\nRETRAITS assert 2 → 1\ndiff --git" in s, s
    finally:
        appel(["relecture", "--retirer"])
        os.chdir(ici)
        tempfile.tempdir = tmp


def test_le_relecteur_rapporte_tout_en_fable():
    """REF14 (`Q4`, `Q10`, choix `B`) : le relecteur en Fable, chaque défaut avec sa gravité et sa confiance, le refus
    sur un bloquant sûr seul, les lignes `TEST` d'office, la sortie rouge exigée — dans l'agent et dans le contrat."""
    kit = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def lu(chemin):
        with open(os.path.join(kit, chemin), encoding="utf-8") as f:
            return f.read()
    agent, contrat = lu("agents/relecture.md"), lu("enchainement.md")
    assert "\nmodel: fable\n" in agent.split("\n---\n")[0] + "\n", "agents/relecture.md : model: fable"
    manque = [m for m in ("bloquant", "à corriger", "remarque", "sûr", "probable", "douteux", "`bloquant · sûr`",
                          "`TEST`", "sortie rouge") if m not in contrat]
    assert not manque, "enchainement.md, « Relecture » : %s" % manque
    assert all(m in agent for m in ("`TEST`", "gravité", "confiance")), "agents/relecture.md renvoie au contrat"
