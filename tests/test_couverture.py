"""REF8 : la couverture des lignes changées. La décision (`verdict`, `a_mesurer`) se teste en mémoire ; un seul dépôt
réel garde le branchement (`juger` : git, coverage et diff-cover vrais), sous le réglage `[tool.coverage.run]` du
kit recopié de `pyproject.toml` (`methode-chantier.md`, « Coder dans le kit »)."""
import io
import os
import re
import shutil
import subprocess
import sys

import couverture
import pytest
from aides import RACINE, ecrire, lire, mod


def rapport(taux, total, violations=None):
    return {"total_percent_covered": taux, "total_num_lines": total,
            "src_stats": {c: {"violation_lines": v} for c, v in (violations or {}).items()}}


def test_verdict_sous_le_seuil_refuse_et_nomme_les_lignes():
    code, lignes = couverture.verdict(rapport(50, 4, {"scripts/x.py": [7, 9], "scripts/y.py": []}))
    assert code == 1 and lignes == [
        "NON COUVERT scripts/x.py : 7, 9\n",
        "COUVERTURE 50 %% des 4 lignes changées, seuil %d %% — commit refusé\n" % couverture.SEUIL], lignes


def test_verdict_au_seuil_passe():
    code, lignes = couverture.verdict(rapport(couverture.SEUIL, 10, {"scripts/x.py": [3]}))
    assert code == 0 and lignes[-1].endswith("— passe\n"), lignes


def test_verdict_sans_ligne_mesuree_n_a_rien_a_couvrir():
    assert couverture.verdict(rapport(100, 0)) == (0, ["COUVERTURE rien à couvrir : aucune ligne changée mesurée\n"])


@pytest.mark.parametrize(("seul", "env", "attendu"), [
    (False, {}, True),
    (True, {}, False),
    (False, {"VLP_COUVERTURE": "1"}, False),
    (False, {"VLP_TOUS_ECARTS": "1"}, False),
    (False, {"VLP_PONT": "1"}, False),
    (False, {"VLP_PONT": "0"}, True),
])
def test_a_mesurer(seul, env, attendu):
    assert couverture.a_mesurer(seul, env) is attendu


def git(d, *args):
    subprocess.run(["git", *args], cwd=d, check=True, capture_output=True)


CODE = "def double(n):\n    return 2 * n\n"
APPEL = "import sys\nsys.path.insert(0, 'scripts')\nimport x\nassert x.double(2) == 4\n"


def mesurer_ici(d):
    """`couverture.mesurer` sur `d`, coverage lancé par ce Python au lieu de `uv` ; rendre son code."""
    return couverture.mesurer(str(d), "appel.py", [], "E", lanceur=[sys.executable, "-m", "coverage"])


@pytest.mark.skipif(shutil.which("git") is None or shutil.which("diff-cover") is None,
                    reason="git ou diff-cover absent : le branchement n'est pas testé")
def test_juger_refuse_sans_rapport_puis_une_ligne_non_couverte_et_passe_couvert(depot):
    reglage = re.search(r"^\[tool\.coverage\.run\]\n(?:(?!\[).*\n)*", lire(os.path.join(RACINE, "pyproject.toml")), re.M)
    assert reglage, "pas de [tool.coverage.run] dans le pyproject.toml du kit"
    ecrire(str(depot / "pyproject.toml"), reglage.group(0))
    ecrire(str(depot / "scripts" / "x.py"), CODE)
    ecrire(str(depot / "appel.py"), APPEL)
    ecrire(str(depot / ".gitignore"), ".couverture/\n.coverage*\n")
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "départ")

    def juger():
        sortie = io.StringIO()
        return couverture.juger(str(depot), sortie, empreinte_de=lambda _: "E"), sortie.getvalue()

    ecrire(str(depot / "note.md"), "rien\n")
    git(depot, "add", "note.md")
    assert juger() == (0, "COUVERTURE rien à couvrir : aucun .py dans le commit\n")

    ecrire(str(depot / "scripts" / "x.py"), CODE + "\n\ndef triple(n):\n    return 3 * n\n")
    git(depot, "add", "scripts/x.py")
    code, s = juger()
    assert code == 1 and s.startswith("GARDE: couverture — pas de rapport mesuré sur ce code"), s

    assert mesurer_ici(depot) == 0 and lire(couverture.chemins(str(depot))[2]) == "E\n"
    code, s = juger()
    assert code == 1 and "NON COUVERT scripts/x.py : 6\n" in s and s.endswith("— commit refusé\n"), s

    ecrire(str(depot / "appel.py"), APPEL + "assert x.triple(2) == 6\n")
    assert mesurer_ici(depot) == 0
    code, s = juger()
    assert code == 0 and "NON COUVERT" not in s and s.endswith("— passe\n"), s


def test_une_suite_rouge_ne_laisse_pas_de_rapport(tmp_path):
    ecrire(str(tmp_path / "appel.py"), "raise SystemExit(3)\n")
    _, rapport, note = couverture.chemins(str(tmp_path))
    ecrire(rapport, "vieux\n")
    ecrire(note, "E\n")
    code = couverture.mesurer(str(tmp_path), "appel.py", [], "E", lanceur=[sys.executable, "-m", "coverage"])
    assert code == 3 and not os.path.exists(rapport) and not os.path.exists(note)


def test_vlp_py_aiguille_couverture_avant_le_coeur(tmp_path):
    r = subprocess.run([sys.executable, os.path.join(RACINE, "scripts", "vlp.py"), "couverture", "--racine",
                        str(tmp_path)], capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 1 and r.stdout.startswith("GARDE: couverture — git diff --cached a échoué"), r


def test_mesurer_sans_uv_ne_mesure_pas_et_le_dit(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(couverture.shutil, "which", lambda _: None)
    assert couverture.mesurer(str(tmp_path), "appel.py", [], "E") is None
    assert capsys.readouterr().out.startswith("COUVERTURE non mesurée : uv introuvable")


def test_mesurer_sans_rapport_quand_combine_echoue(tmp_path, capsys):
    faux = [sys.executable, "-c", "import sys; sys.exit(0 if sys.argv[1] in ('erase', 'run') else 1)"]
    assert couverture.mesurer(str(tmp_path), "appel.py", [], "E", lanceur=faux) == 1
    assert "ÉCART: couverture — coverage combine ou xml a échoué" in capsys.readouterr().out
    assert not os.path.exists(couverture.chemins(str(tmp_path))[2])


def test_juger_sans_diff_cover_puis_diff_cover_en_echec(tmp_path, monkeypatch):
    monkeypatch.setattr(couverture, "py_indexes", lambda _: ["scripts/x.py"])
    monkeypatch.setattr(couverture, "rapport_a_jour", lambda _r, _e: True)
    for outil, debut in ((None, "GARDE: couverture — diff-cover introuvable"),
                         (sys.executable, "GARDE: couverture — diff-cover sorti ")):
        monkeypatch.setattr(couverture.shutil, "which", lambda _, o=outil: o)
        sortie = io.StringIO()
        assert couverture.juger(str(tmp_path), sortie, empreinte_de=lambda _: "E") == 1
        assert sortie.getvalue().startswith(debut), sortie.getvalue()


def test_empreinte_du_kit_est_celle_de_vit11(tmp_path):
    ecrire(str(tmp_path / "a.txt"), "a\n")
    assert couverture.empreinte_du_kit(str(tmp_path)) == mod.empreinte_kit(str(tmp_path))
