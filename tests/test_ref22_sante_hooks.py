"""REF22, l'angle des bugs : les hooks de commit et leurs juges (`couverture`, `retraits`, `sante`, `concernes`).

- Un nom non ASCII, cité par Git (`core.quotepath`, vrai d'office) : `"scripts/caf\\303\\251.py"` ne finit pas par `.py`.
- Un chemin de machine sous la forme de Git Bash, ou à quatre barres : le hook le laissait passer.
- `sante <fichiers> --base` : la base réécrite avec ces seuls fichiers, les autres effacés.
- Un `.py` indexé en partie : le rapport, mesuré sur l'arbre de travail, ne colle plus aux lignes de l'index.
- `concernes` : la ligne du `def`, jouée à l'import, attribuait la fonction au test qui importe le module.

Les chemins de machine se bâtissent par morceaux : écrits d'un bloc, ils feraient refuser le commit de ce fichier."""
import io
import os
import re
import shutil
import subprocess
import sys

import concernes
import couverture
import coverage
import pytest
import retraits
from aides import RACINE, appel, ecrire, lire

CAFE = "café"   # un nom non ASCII : Git le cite d'office


def git_ici(d, *args):
    """Lancer `git <args>` dans `d` (la config de la machine écartée par `isoler`) ; rendre (code, sortie)."""
    r = subprocess.run(["git", "-C", str(d), *args], capture_output=True, encoding="utf-8", errors="replace",
                       check=False)
    return r.returncode, r.stdout + r.stderr


# --- 1. Les noms non ASCII -------------------------------------------------------------------------------------------


def test_ref22_py_indexes_voit_un_nom_non_ascii(depot):
    ecrire(str(depot / "scripts" / (CAFE + ".py")), "x = 1\n")
    git_ici(depot, "add", "-A")
    assert couverture.py_indexes(str(depot)) == ["scripts/%s.py" % CAFE], "REF22 : py_indexes, un nom non ASCII"


def test_ref22_retraits_compte_un_test_non_ascii(depot):
    ecrire(str(depot / "tests" / ("test_%s.py" % CAFE)), "def test_a():\n    assert 1\n")
    git_ici(depot, "add", "-A")
    assert list(retraits.textes(str(depot), "")) == ["tests/test_%s.py" % CAFE], "REF22 : retraits, l'index"
    git_ici(depot, "commit", "-q", "-m", "a")
    assert list(retraits.textes(str(depot), "HEAD")) == ["tests/test_%s.py" % CAFE], "REF22 : retraits, HEAD"


def hook_isole(init_git, t):
    """Un dépôt neuf sous `t`, le `pre-commit` du kit branché, `scripts/` copié hors suivi (le hook y lance
    `vlp.py claude`) ; rendre (dépôt, PATH sans pyright, uv ni claude, `git(chemins, *args)`) — APPDATA et
    LOCALAPPDATA vides : ni l'app ni son claude ne se trouvent."""
    depot = os.path.join(t, "depot")
    for nom in (".githooks", "scripts"):
        shutil.copytree(os.path.join(RACINE, nom), os.path.join(depot, nom))
    sans = [d for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and not any(shutil.which(n, path=d) for n in ("pyright", "uv", "claude"))]
    base = dict(os.environ, APPDATA="", LOCALAPPDATA="")

    def git(chemins, *args):
        r = subprocess.run(["git", *args], cwd=depot, env=dict(base, PATH=os.pathsep.join(chemins)),
                           capture_output=True, encoding="utf-8", errors="replace", check=False)
        return r.returncode, r.stdout + r.stderr

    init_git(depot)
    git(sans, "config", "core.hooksPath", ".githooks")
    ecrire(os.path.join(depot, ".git", "info", "exclude"), "scripts/\n")
    return depot, sans, git


@pytest.mark.skipif(shutil.which("git") is None, reason="git absent : le hook n'est pas testé")
def test_ref22_pre_commit_voit_un_py_non_ascii(tmp_path, init_git):
    depot, sans, git = hook_isole(init_git, str(tmp_path))
    rouge = str(tmp_path / "rouge")
    ecrire(os.path.join(rouge, "uv"), '#!/bin/sh\necho "faux uv $* : sortie 1"\nexit 1\n')
    os.chmod(os.path.join(rouge, "uv"), 0o755)
    ecrire(os.path.join(depot, CAFE + ".py"), "x = 1\n")
    git(sans, "add", CAFE + ".py")
    code, s = git([rouge, *sans], "commit", "-q", "-m", "py")
    assert (code, "faux uv run --frozen pyright : sortie 1" in s) == (1, True), (
        "REF22 : pre-commit, un .py au nom non ASCII réveille pyright\n" + s)


# --- 2. Les chemins de machine : Git Bash, quatre barres ------------------------------------------------------------


@pytest.mark.skipif(shutil.which("git") is None, reason="git absent : le hook n'est pas testé")
def test_ref22_pre_commit_refuse_git_bash_et_quatre_barres(tmp_path, init_git):
    depot, sans, git = hook_isole(init_git, str(tmp_path))
    quatre = "\\" * 4
    vus = []
    for forme in ("/c/" + "Users/bob/x", "cd /d/" + "users/bob", "C:" + quatre + "Users" + quatre + "bob",
                  "https://exemple.org/a/users/bob", "src/a/users/bob"):
        ecrire(os.path.join(depot, "b.md"), "voir `%s`\n" % forme)
        git(sans, "add", "b.md")
        code, s = git(sans, "commit", "-q", "-m", "chemin")
        vus.append((forme, code == 1 and "pre-commit : chemin de machine dans une ligne ajoutée" in s))
    assert [refus for _, refus in vus] == [True, True, True, False, False], (
        "REF22 : pre-commit, Git Bash et quatre barres refusés, une URL et un chemin relatif passent\n" + str(vus))


# --- 3. `sante <fichiers> --base` ------------------------------------------------------------------------------------


def test_ref22_sante_base_avec_fichiers_refuse(tmp_path):
    r = str(tmp_path / "r")
    ecrire(os.path.join(r, "scripts", "a.py"), 'def f():\n    """Un."""\n    return 1\n')
    ecrire(os.path.join(r, "scripts", "b.py"), "def g():\n    return 2\n")
    assert appel(["sante", "--base", "--sans-ruff", "--racine", r])[0] == 0, "REF22 : sante --base, la base posée"
    chemin = os.path.join(r, "scripts", "sante-base.json")
    avant = lire(chemin)
    code, s = appel(["sante", os.path.join(r, "scripts", "a.py"), "--base", "--sans-ruff", "--racine", r])
    assert (code, s.startswith("GARDE: --base"), lire(chemin) == avant) == (1, True, True), (
        "REF22 : sante <fichiers> --base refuse, la base intacte\n" + s)
    assert appel(["sante", "--cliquet", "--sans-ruff", "--racine", r])[1].endswith("CLIQUET TENU\n"), (
        "REF22 : le cliquet tient toujours")


# --- 4. Un `.py` indexé en partie ------------------------------------------------------------------------------------


CODE = "def double(n):\n    return 2 * n\n"
APPEL = "import sys\nsys.path.insert(0, 'scripts')\nimport x\nassert x.double(2) == 4\nassert x.triple(2) == 6\n"


@pytest.mark.skipif(shutil.which("git") is None or shutil.which("diff-cover") is None,
                    reason="git ou diff-cover absent : le branchement n'est pas testé")
def test_ref22_couverture_refuse_un_py_indexe_en_partie(depot):
    reglage = re.search(r"^\[tool\.coverage\.run\]\n(?:(?!\[).*\n)*", lire(os.path.join(RACINE, "pyproject.toml")), re.M)
    assert reglage, "REF22 : pas de [tool.coverage.run] dans le pyproject.toml du kit"
    ecrire(str(depot / "pyproject.toml"), reglage.group(0))
    ecrire(str(depot / "scripts" / "x.py"), CODE)
    ecrire(str(depot / "appel.py"), APPEL)
    ecrire(str(depot / ".gitignore"), ".couverture/\n.coverage*\n")
    git_ici(depot, "add", "-A")
    git_ici(depot, "commit", "-q", "-m", "départ")
    ecrire(str(depot / "scripts" / "x.py"), CODE + "\n\ndef triple(n):\n    return 3 * n\n")
    git_ici(depot, "add", "scripts/x.py")
    ecrire(str(depot / "scripts" / "x.py"), "# a\n# b\n# c\n# d\n" + CODE + "\n\ndef triple(n):\n    return 3 * n\n")
    lanceur = [sys.executable, "-m", "coverage"]
    assert couverture.mesurer(str(depot), "appel.py", [], "E", lanceur=lanceur) == 0, "REF22 : la mesure"
    sortie = io.StringIO()
    code = couverture.juger(str(depot), sortie, empreinte_de=lambda _: "E")
    assert (code, sortie.getvalue()) == (1, "GARDE: couverture — indexé en partie : scripts/x.py ; le rapport, "
                                            "mesuré sur l'arbre de travail, ne colle pas à l'index : indexer tout le "
                                            "fichier, ou git stash --keep-index puis la suite (REF22)\n"), (
        "REF22 : couverture, un .py indexé en partie refusé\n" + sortie.getvalue())


@pytest.mark.skipif(shutil.which("git") is None or shutil.which("diff-cover") is None,
                    reason="git ou diff-cover absent : le branchement n'est pas testé")
def test_ref22_couverture_juge_un_py_non_ascii(depot):
    reglage = re.search(r"^\[tool\.coverage\.run\]\n(?:(?!\[).*\n)*", lire(os.path.join(RACINE, "pyproject.toml")), re.M)
    assert reglage, "REF22 : pas de [tool.coverage.run] dans le pyproject.toml du kit"
    ecrire(str(depot / "pyproject.toml"), reglage.group(0))
    ecrire(str(depot / "scripts" / (CAFE + ".py")), CODE)
    ecrire(str(depot / "appel.py"), "import sys\nsys.path.insert(0, 'scripts')\nimport %s\n" % CAFE)
    ecrire(str(depot / ".gitignore"), ".couverture/\n.coverage*\n")
    git_ici(depot, "add", "-A")
    git_ici(depot, "commit", "-q", "-m", "départ")
    ecrire(str(depot / "scripts" / (CAFE + ".py")), CODE + "\n\ndef triple(n):\n    return 3 * n\n")
    git_ici(depot, "add", "-A")
    lanceur = [sys.executable, "-m", "coverage"]
    assert couverture.mesurer(str(depot), "appel.py", [], "E", lanceur=lanceur) == 0, "REF22 : la mesure"
    sortie = io.StringIO()
    code = couverture.juger(str(depot), sortie, empreinte_de=lambda _: "E")
    assert (code, "NON COUVERT scripts/%s.py : 6\n" % CAFE in sortie.getvalue()) == (1, True), (
        "REF22 : couverture, la ligne non couverte d'un .py non ASCII se voit\n" + sortie.getvalue())


def test_ref22_verdict_de_l_index_sans_git_est_une_garde(tmp_path):
    code, lignes = couverture.verdict_de_l_index(str(tmp_path), ["scripts/x.py"], {"total_num_lines": 0})
    assert (code, lignes[0].startswith("GARDE: couverture — git diff a échoué")) == (1, True), (
        "REF22 : verdict_de_l_index, Git en échec : une GARDE, pas un verdict\n" + str(lignes))


def test_ref22_env_sans_citation_s_ajoute_aux_paires_posees():
    env = couverture.env_sans_citation({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "a.b", "GIT_CONFIG_VALUE_0": "c"})
    assert env == {"GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "a.b", "GIT_CONFIG_VALUE_0": "c",
                   "GIT_CONFIG_KEY_1": "core.quotepath", "GIT_CONFIG_VALUE_1": "false"}, (
        "REF22 : env_sans_citation, la paire après celles déjà posées")


# --- 6. `concernes` : la ligne du `def` ------------------------------------------------------------------------------


MODULE = "def f():\n    return 1\n\n\ndef g():\n    return 2\n\n\ndef h(): return 3\n"


@pytest.mark.parametrize("arcs", [True, False])
def test_ref22_concernes_ignore_la_ligne_du_def(tmp_path, arcs):
    t = str(tmp_path / "p")
    m = os.path.join(t, "scripts", "m.py")
    ecrire(m, MODULE)
    os.makedirs(os.path.join(t, ".couverture"))
    d = coverage.CoverageData(basename=os.path.join(t, ".couverture", "donnees"))
    for contexte, lignes in (("test_m.test_f", [2]), ("test_m.test_g", [1, 5, 6]), ("test_m.test_h", [9])):
        d.set_context(contexte)
        if arcs:
            d.add_arcs({m: [(-1, n) for n in lignes] + [(n, -1) for n in lignes]})
        else:
            d.add_lines({m: lignes})
    d.write()
    assert concernes.concernes(t, ["f"]) == (["test_m.test_f"], []), (
        "REF22 : concernes, le test qui importe le module (ligne du def) ne passe pas par f (%s)" % arcs)
    assert concernes.concernes(t, ["g", "h"]) == (["test_m.test_g", "test_m.test_h"], []), (
        "REF22 : concernes, g garde son test, h (sur une ligne) le sien (%s)" % arcs)
