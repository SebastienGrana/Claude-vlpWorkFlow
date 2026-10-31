"""REF15 (Q1 A, 2026-10-31) : `PT018`, l'assertion composée, devient le 6e compte du cliquet, et `tests/` est
mesuré. Le compte ne tient que pour un test ; ailleurs, aucun seuil. Le compte `ast` suit ruff 0.16.10, sondé :
un `and` en tête, message ou non, ou `not (… or …)` ; une fonction imbriquée compte pour elle."""
import json
import os

import sante

TEXTE = ("def test_a():\n    assert a and b\n    assert (a and b), 'm'\n    assert not (a or b)\n    assert a or b\n"
         "    assert not (a and b)\n    assert x\n    def inner():\n        assert c and d\n    if x:\n"
         "        assert e and f\n")


def poser(racine, relatif, texte):
    chemin = os.path.join(racine, *relatif.split("/"))
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)
    return chemin


def test_le_compte_ast_suit_la_sonde_de_ruff(tmp_path):
    fonctions, _ = sante.mesurer_fichier(str(tmp_path), poser(str(tmp_path), "tests/test_x.py", TEXTE))
    comptes = {f["fonction"]: f["ast"][sante.COMPTES.index("assertions composées")] for f in fonctions}
    assert comptes == {"test_a": 4, "test_a.inner": 1}, comptes


def test_un_fichier_de_tests_est_un_test(tmp_path):
    vus = {}
    for relatif in ("tests/test_x.py", "tests/aides.py", "scripts/test-y.py", "scripts/z.py"):
        fonctions, _ = sante.mesurer_fichier(str(tmp_path), poser(str(tmp_path), relatif, "def f():\n    return 1\n"))
        vus[relatif] = fonctions[0]["test"]
    assert vus == {"tests/test_x.py": True, "tests/aides.py": True, "scripts/test-y.py": True, "scripts/z.py": False}


def test_le_seuil_ne_tient_que_pour_un_test():
    i = sante.COMPTES.index("assertions composées")
    assert (sante.seuils_de({"test": True})[i], sante.seuils_de({"test": False})[i]) == (0, None)
    assert sante.seuils_de({"test": True})[sante.COMPTES.index("instructions")] is None, "VIT Q4, Q2 A : gardé"


def test_le_cliquet_mesure_tests(tmp_path):
    a = poser(str(tmp_path), "scripts/a.py", "def f():\n    return 1\n")
    t = poser(str(tmp_path), "tests/test_t.py", "def test_t():\n    assert 1\n")
    assert sante.chemins_de(str(tmp_path), None) == sorted([a, t])


def test_ruff_compte_chaque_pt018_de_la_fonction(tmp_path):
    chemin = poser(str(tmp_path), "tests/test_x.py", TEXTE)
    fonctions, nombre = sante.mesurer_fichier(str(tmp_path), chemin)
    for f in fonctions:
        f["ruff"] = [0] * len(sante.REGLES)
    diags = [{"filename": chemin, "code": "PT018", "message": "Assertion should be broken down into multiple parts",
              "location": {"row": r}} for r in (2, 3, 4, 9, 11)]
    sante.lire_ruff(json.dumps(diags), {sante.cle(chemin): sante.carte_lignes(fonctions, nombre)})
    i = sante.REGLES.index("PT018")
    assert {f["fonction"]: f["ruff"][i] for f in fonctions} == {"test_a": 4, "test_a.inner": 1}


def test_une_base_a_cinq_comptes_ne_casse_rien():
    f = {"fichier": "tests/test_x.py", "fonction": "test_a", "ligne": 1, "empreinte": "e", "doc": False,
         "test": True, "ast": [1, 0, 0, 3, 0, 2]}
    b = {"fichier": "tests/test_x.py", "fonction": "test_a", "empreinte": "e", "ast": [1, 0, 0, 3, 0]}
    assert sante.ecarts_de(f, b, "ast") == [], "un compte absent de la base vaut le compte du jour"
    neuve = "SEUIL tests/test_x.py:1 test_a · assertions composées 2, seuil 0 (neuve)\n"
    assert sante.ecarts_de(f, None, "ast") == [neuve]
