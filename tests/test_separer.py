"""RUF1 : `vlp.py separer` sépare les assertions composées (`PT018`) — une assertion par part, sans message, dans
l'ordre (le socle de `context AI/130-ruf.md`). Chaque cas bâtit un fichier dans un dossier temporaire et compare le
texte rendu à l'attendu exact."""
import io
import os

import separer
from aides import ecrire


def jouer(tmp_path, texte, *options, nom="test_x.py"):
    """Écrire `texte` dans `<tmp>/<nom>`, jouer `separer` dessus : (code, sortie, texte du fichier après)."""
    chemin = os.path.join(str(tmp_path), nom)
    ecrire(chemin, texte)
    sortie = io.StringIO()
    code = separer.principal([chemin, *options], sortie)
    with open(chemin, encoding="utf-8", newline="") as f:
        return code, sortie.getvalue().replace(str(tmp_path).replace("\\", "/"), "<T>"), f.read()


def rendu(tmp_path, texte):
    """Le texte de `texte` réécrit par `separer --ecrire` (RUF1), le code de sortie à 0."""
    code, _sortie, apres = jouer(tmp_path, texte, "--ecrire")
    assert code == 0
    return apres


def test_deux_parts(tmp_path):
    """RUF1 : `assert a and b` devient deux assertions, à la même indentation."""
    assert rendu(tmp_path, "def test_a():\n    assert a and b\n") == "def test_a():\n    assert a\n    assert b\n"


def test_trois_parts_avec_message(tmp_path):
    """RUF1 : trois parts, dans l'ordre ; le message est retiré (choix du cadrage)."""
    avant = "def test_a():\n    assert x == 1 and y in z and f(w), \"le message\"\n"
    apres = "def test_a():\n    assert x == 1\n    assert y in z\n    assert f(w)\n"
    assert rendu(tmp_path, avant) == apres


def test_imbriquees(tmp_path):
    """RUF1 : un `and` entre parenthèses se sépare aussi, et un `not (… or …)` dans un `and`."""
    avant = "def test_a():\n    assert a and (b and c)\n    assert d and not (e or f)\n"
    apres = ("def test_a():\n    assert a\n    assert b\n    assert c\n"
             "    assert d\n    assert not e\n    assert not f\n")
    assert rendu(tmp_path, avant) == apres


def test_not_or(tmp_path):
    """RUF1 : `not (a or b)` devient `not a`, `not b` ; une part qui est un `and` garde ses parenthèses sous le
    `not`, et un `not` sous le `not` s'annule."""
    avant = "def test_a():\n    assert not (a == 1 or b and c or not d)\n"
    apres = "def test_a():\n    assert not a == 1\n    assert not (b and c)\n    assert d\n"
    assert rendu(tmp_path, avant) == apres


def test_multilignes(tmp_path):
    """RUF1 : une assertion sur plusieurs lignes ; une part qui tient sur plusieurs lignes va entre parenthèses."""
    avant = ("def test_a():\n"
             "    assert (x == 1\n"
             "            and y), (\n"
             "        \"un message long\")\n"
             "    assert a and (\n"
             "        b\n"
             "        or c)\n")
    apres = ("def test_a():\n"
             "    assert x == 1\n"
             "    assert y\n"
             "    assert a\n"
             "    assert (b\n"
             "        or c)\n")
    assert rendu(tmp_path, avant) == apres


def test_dans_une_classe_et_un_bloc(tmp_path):
    """RUF1 : l'indentation suit l'assertion, dans une méthode, un `with` ou un `for`."""
    avant = "class TestA:\n    def test_a(self):\n        for i in r:\n            assert i and not i.x\n"
    apres = "class TestA:\n    def test_a(self):\n        for i in r:\n            assert i\n            assert not i.x\n"
    assert rendu(tmp_path, avant) == apres


def test_commentaire_en_fin_reste(tmp_path):
    """RUF1 : un commentaire après l'assertion reste, sur la dernière part."""
    avant = "def test_a():\n    assert a and b  # noqa: E501\n"
    assert rendu(tmp_path, avant) == "def test_a():\n    assert a\n    assert b  # noqa: E501\n"


def test_commentaire_dedans_garde(tmp_path):
    """RUF1 : un commentaire dans une assertion multiligne se perdrait : fichier intact, `GARDE:`, sort 1."""
    avant = "def test_a():\n    assert (a  # pourquoi a\n            and b)\n    assert c and d\n"
    code, sortie, apres = jouer(tmp_path, avant, "--ecrire")
    assert code == 1
    assert apres == avant
    assert sortie == ("GARDE: <T>/test_x.py — un commentaire dans l'assertion de la ligne 2 se perdrait : "
                      "laissé intact\nTOTAL 0 fichiers · 0 assertions → 0 · écrits\n")


def test_deux_instructions_sur_la_ligne_garde(tmp_path):
    """RUF1 : une assertion qui partage sa ligne (`if x: assert …`, `…; assert …`) ne se sépare pas : `GARDE:`."""
    for avant in ("def test_a():\n    if x: assert a and b\n", "def test_a():\n    y = 1; assert a and b\n",
                  "def test_a():\n    assert a and b; y = 1\n"):
        code, sortie, apres = jouer(tmp_path, avant, "--ecrire")
        assert code == 1
        assert apres == avant
        assert "partage sa ligne" in sortie


def test_fin_de_ligne_crlf_gardee(tmp_path):
    """RUF1 : un fichier en CRLF le reste ; le reste du fichier ne bouge pas."""
    avant = "def test_a():\r\n    assert a and b\r\n    assert c\r\n"
    assert rendu(tmp_path, avant) == "def test_a():\r\n    assert a\r\n    assert b\r\n    assert c\r\n"


def test_sans_ecrire_compte_et_n_ecrit_rien(tmp_path):
    """RUF1 : sans `--ecrire`, une ligne par fichier touché et le total ; aucun fichier écrit."""
    ecrire(str(tmp_path / "d" / "test_b.py"), "def test_b():\n    assert c\n")
    ecrire(str(tmp_path / "d" / "sous" / "test_c.py"), "def test_c():\n    assert a and b and c\n    assert d and e\n")
    avant = "def test_a():\n    assert a and b\n"
    ecrire(str(tmp_path / "d" / "test_a.py"), avant)
    sortie = io.StringIO()
    code = separer.principal([str(tmp_path / "d")], sortie)
    assert code == 0
    with open(str(tmp_path / "d" / "test_a.py"), encoding="utf-8") as f:
        assert f.read() == avant
    racine = str(tmp_path / "d").replace("\\", "/")
    assert sortie.getvalue().replace(racine, "<D>") == (
        "SEPARER <D>/sous/test_c.py · 2 assertions → 5\n"
        "SEPARER <D>/test_a.py · 1 assertions → 2\n"
        "TOTAL 2 fichiers · 3 assertions → 7 · rien d'écrit (--ecrire pour réécrire)\n")


def test_avec_ecrire_le_total_dit_ecrits(tmp_path):
    """RUF1 : avec `--ecrire`, la même ligne par fichier, et le total dit `écrits`."""
    code, sortie, _apres = jouer(tmp_path, "def test_a():\n    assert a and b\n", "--ecrire")
    assert code == 0
    assert sortie == "SEPARER <T>/test_x.py · 1 assertions → 2\nTOTAL 1 fichiers · 1 assertions → 2 · écrits\n"


def test_fichier_illisible_garde(tmp_path):
    """RUF1 : un fichier qui ne se lit pas par `ast` : `GARDE:`, intact, sort 1."""
    code, sortie, apres = jouer(tmp_path, "def test_(:\n", "--ecrire")
    assert code == 1
    assert apres == "def test_(:\n"
    assert sortie.startswith("GARDE: <T>/test_x.py — ne se lit pas par ast")


def test_rien_a_separer(tmp_path):
    """RUF1 : un fichier sans assertion composée n'est ni nommé ni réécrit."""
    code, sortie, apres = jouer(tmp_path, "def test_a():\n    assert a or b\n    assert not (a and b)\n", "--ecrire")
    assert code == 0
    assert apres == "def test_a():\n    assert a or b\n    assert not (a and b)\n"
    assert sortie == "TOTAL 0 fichiers · 0 assertions → 0 · écrits\n"
