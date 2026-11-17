"""FIG4 : `vlp.py valider` avertit dès le cadrage d'une fiche qui nomme un test existant sans ligne **Tests** — `figer`
la bloquerait en pleine fiche (deux fois à ROU, sur `tests/conftest.py`). Un test « existant » l'est comme pour
`figer` (FIG1) : présent dans `HEAD` ; sans Git, présent sur le disque.
"""
import io
import os
import subprocess

from aides import ecrire, mod

FICHE = """<!-- FICHE:%s -->
## %s [ ] — fiche %s

**Dépend de** : rien.
**Fichiers** : %s — et rien d'autre.
%s
**Prompt**
Fais-la.

**Critère de fin**
Fait.
<!-- /FICHE -->

"""
DECLARE = "**Tests** : modifiés — le conftest change de règle\n"


def fiches(*fiches_):
    """Un fichier de fiches : le socle, puis chaque (code, fichiers, ligne Tests)."""
    return ("# Chantier F — fiches\n\n## Le socle commun\n\nRien.\n\n## L'ordre des fiches\n\nDans l'ordre.\n\n"
            + "".join(FICHE % (c, c, c, f, t) for c, f, t in fiches_))


def projet(racine, avec_git, init_git):
    """Un projet équipé, `tests/conftest.py` existant (commité si `avec_git`), et `tests/test_ecrit.py` sur le disque
    seulement — écrit par une fiche, pas commité."""
    ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : .\n")
    ecrire(os.path.join(racine, "tests", "conftest.py"), "X = 1\n")
    if avec_git:
        init_git(racine)
        for args in (["add", "-A"], ["commit", "-q", "-m", "init"]):
            subprocess.run(["git", "-C", racine, *args], check=True, capture_output=True)
    ecrire(os.path.join(racine, "tests", "test_ecrit.py"), "def test_e():\n    pass\n")


def avertissements(chemin):
    """Les codes de fiche et chemins de test des avertissements « test existant » de `vlp.py valider <chemin>`, dans
    l'ordre : [(code, chemin)]."""
    o = io.StringIO()
    mod.main(["valider", chemin], o, io.StringIO(), io.StringIO())
    return [(l.split("fiche ", 1)[1].split(" ", 1)[0], l.split(" : ")[2].split(" ", 1)[0])
            for l in o.getvalue().splitlines() if "est un test existant" in l]


def test_valider_test_existant_sans_permission(tmp_path, init_git):
    """FIG4 : une fiche qui nomme `tests/conftest.py`, commité, sans ligne **Tests** → un avertissement qui nomme la
    fiche et le chemin ; la même avec la ligne → rien ; un test inexistant, ou écrit sur le disque sans être commité →
    rien."""
    racine = str(tmp_path / "p")
    projet(racine, True, init_git)
    chemin = os.path.join(racine, "fiches.md")
    ecrire(chemin, fiches(("F1", "tests/conftest.py, scripts/x.py", ""), ("F2", "`tests/conftest.py`", DECLARE),
                          ("F3", "un test neuf `tests/test_neuf.py`", ""), ("F4", "tests/test_ecrit.py", "")))
    assert avertissements(chemin) == [("F1", "tests/conftest.py")], (
        "valider : un test existant sans ligne **Tests**, un avertissement qui nomme fiche et chemin")


def test_valider_test_existant_sans_git(tmp_path, init_git):
    """FIG4 : sans Git, « existant » se lit sur le disque — le test écrit, lui aussi, avertit."""
    racine = str(tmp_path / "p")
    projet(racine, False, init_git)
    chemin = os.path.join(racine, "fiches.md")
    ecrire(chemin, fiches(("F1", "tests/conftest.py", ""), ("F3", "`tests/test_neuf.py`", ""),
                          ("F4", "tests/test_ecrit.py", "")))
    assert avertissements(chemin) == [("F1", "tests/conftest.py"), ("F4", "tests/test_ecrit.py")], (
        "valider : sans Git, tout test sur le disque est existant")
