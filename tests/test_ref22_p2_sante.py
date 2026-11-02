"""REF22, passe 2 de l'angle des bugs : `sante`, `concernes`, `retraits`, `conserve`, `noyau/bac`.

- `sante <fichier relatif> --racine <projet>` : le fichier se résolvait depuis le dossier courant, pas la racine.
- Un BOM UTF-8 (Bloc-notes, `Out-File`) : Python lance le fichier, `ast.parse` du texte lu en `utf-8` le refuse.
- `concernes.ouvrir` : un `#` dans le chemin coupait l'URI `file:` de sqlite.
- `sante.tailles_de` : `splitlines()` coupe aussi sur `\\f`, U+2028… — une autre façon de compter que `mesurer_fichier`.
- `conserve` : `***` et `___` passaient pour du texte, un commentaire `#` d'un bloc de code pour un titre.
- `noyau/bac.version_claude` : `2.1.99-beta` lu `2.1.0`, classé sous `2.1.98`."""
import io
import os
import sqlite3
import subprocess
from contextlib import closing

import concernes
import conserve
import noyau.bac
import retraits
import sante
from aides import appel, ecrire

BOM = "﻿"
CODE = 'def f():\n    """Un."""\n    return 1\n'
TEST = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n"


# --- 1. Un fichier relatif se lit depuis `--racine` ------------------------------------------------------------------


def test_ref22_p2_sante_fichier_relatif_depuis_la_racine(tmp_path, monkeypatch):
    """REF22 : `sante scripts/a.py --cliquet --racine projet`, lancé d'un autre dossier qui a son `scripts/a.py`,
    mesure le fichier du projet, pas celui du dossier courant."""
    projet, autre = str(tmp_path / "projet"), str(tmp_path / "autre")
    ecrire(os.path.join(projet, "scripts", "a.py"), CODE)
    ecrire(os.path.join(autre, "scripts", "a.py"), "def f(a, b, c, d, e, g):\n    return a\n")
    assert appel(["sante", "--base", "--sans-ruff", "--racine", projet])[0] == 0, "REF22 : la base posée"
    monkeypatch.chdir(autre)
    code, s = appel(["sante", os.path.join("scripts", "a.py"), "--cliquet", "--sans-ruff", "--racine", projet])
    assert (code, s.endswith("CLIQUET TENU\n")) == (0, True), "REF22 : le fichier relatif, lu sous --racine\n" + s


# --- 2. Un BOM UTF-8 ---------------------------------------------------------------------------------------------------


def test_ref22_p2_concernes_lit_un_bom(tmp_path):
    """REF22 : `concernes.fonctions` trouve la fonction d'un fichier ouvert par un BOM."""
    ecrire(str(tmp_path / "scripts" / "a.py"), BOM + CODE)
    assert concernes.fonctions(str(tmp_path), ["f"]) == {"f": [("scripts/a.py", 1, 3)]}, "REF22 : concernes, le BOM"


def test_ref22_p2_sante_lit_un_bom(tmp_path):
    """REF22 : `sante` mesure un fichier ouvert par un BOM, sans `GARDE:`, et sa taille ne change pas."""
    r = str(tmp_path)
    ecrire(os.path.join(r, "scripts", "a.py"), BOM + CODE)
    code, s = appel(["sante", "--sans-ruff", "--racine", r])
    assert (code, "GARDE" in s) == (0, False), "REF22 : sante, le BOM\n" + s
    assert sante.tailles_de(r) == {"scripts/a.py": 3}, "REF22 : tailles_de, le BOM"


def test_ref22_p2_retraits_lit_un_bom(depot):
    """REF22 : un fichier de test ré-enregistré avec un BOM garde ses comptes à l'index — pas `tests 2 → 0`."""
    def git(*args):
        subprocess.run(["git", "-C", str(depot), *args], capture_output=True, check=True)

    ecrire(str(depot / "tests" / "test_a.py"), TEST)
    git("add", "-A")
    git("commit", "-q", "-m", "a")
    ecrire(str(depot / "tests" / "test_a.py"), BOM + TEST)
    git("add", "-A")
    avant, apres = retraits.textes(str(depot), "HEAD"), retraits.textes(str(depot), "")
    assert retraits.compter(apres["tests/test_a.py"]) == retraits.compter(avant["tests/test_a.py"]), (
        "REF22 : retraits, le BOM à l'index")


# --- 3. L'URI sqlite de `concernes.ouvrir` -----------------------------------------------------------------------------


def test_ref22_p2_concernes_ouvre_un_chemin_a_diese(tmp_path):
    """REF22 : une racine `chantier#3` s'ouvre en lecture seule, sans créer un autre fichier à côté."""
    racine = tmp_path / "d" / "chantier#3"
    os.makedirs(racine / ".couverture")
    with closing(sqlite3.connect(str(racine / concernes.DONNEES))) as c:
        c.execute("CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)")
        c.execute("INSERT INTO context VALUES (1, 'test_x')")
        c.commit()
    base = concernes.ouvrir(str(racine))
    assert base is not None, "REF22 : la base trouvée"
    with closing(base):
        assert concernes.par_test(base), "REF22 : concernes.ouvrir, le # du chemin"
    assert os.listdir(tmp_path / "d") == ["chantier#3"], "REF22 : aucun fichier créé à côté"


# --- 4. Une seule façon de compter les lignes --------------------------------------------------------------------------


def test_ref22_p2_tailles_compte_comme_mesurer_fichier(tmp_path):
    """REF22 : 1 000 lignes dont deux chaînes portent U+2028 et `\\f` font 1 000 lignes, pas 1 002."""
    corps = ["x%d = 1" % i for i in range(998)] + ['s = "a b"', 't = "c\fd"']
    ecrire(str(tmp_path / "scripts" / "gros.py"), "\n".join(corps) + "\n")
    assert sante.tailles_de(str(tmp_path)) == {"scripts/gros.py": 1000}, "REF22 : tailles_de, U+2028 et \\f"


# --- 5. `conserve` : séparateurs et blocs de code ----------------------------------------------------------------------


def test_ref22_p2_conserve_etoiles_et_soulignes_sont_des_separateurs():
    """REF22 : `***` et `___`, séparateurs Markdown, ne sont pas du texte perdu."""
    assert conserve.perdues(["une\n", "***\n", "___\n"], ["une\n"]) == [], "REF22 : conserve, *** et ___"


def test_ref22_p2_conserve_un_commentaire_de_code_compte(tmp_path):
    """REF22 : un commentaire `#` dans un bloc ``` est du texte : sa perte se voit ; le titre hors du bloc, non."""
    avant = ["# Titre\n", "```python\n", "# garde : jamais vide\n", "x = 1\n", "```\n", "# Autre titre\n"]
    apres = ["```python\n", "x = 1\n", "```\n"]
    assert conserve.perdues(avant, apres) == [(3, "# garde : jamais vide")], "REF22 : conserve, le # d'un bloc"
    chemin = str(tmp_path / "avant.md")
    ecrire(chemin, "".join(avant))
    s = io.StringIO()
    assert conserve.principal([chemin, "--apres", chemin], s) == 0
    assert s.getvalue() == "CONSERVE 2 lignes lues · 0 perdue(s)\n", "REF22 : conserve, le compte des lignes lues"


# --- 6. `version_claude` : une version à suffixe ---------------------------------------------------------------------


def test_ref22_p2_version_claude_a_suffixe(tmp_path):
    """REF22 : `2.1.99-beta` passe devant `2.1.98`."""
    dossier = str(tmp_path / "claude-code")
    chemins = [os.path.join(dossier, v, "claude.exe") for v in ("2.1.98", "2.1.99-beta")]
    for c in chemins:
        ecrire(c, "")
    assert max(chemins, key=lambda c: noyau.bac.version_claude(dossier, c)) == chemins[1], (
        "REF22 : version_claude, 2.1.99-beta")
