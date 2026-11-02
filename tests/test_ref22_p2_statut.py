"""REF22, passe 2, l'angle des bugs : `noyau/fiches.py` (`chemins_du_statut`), `noyau/rapport.py` (`py_du_statut`)
et `noyau/notes.py` (`nom_etat`) — un renommage dans l'arbre de travail (` R`), un contexte numéroté à trois chiffres.
"""
import os

from aides import ecrire
from noyau import fiches, notes, rapport


def test_ref22_chemins_du_statut_saute_l_ancien_nom_d_un_renommage_en_colonne_y():
    """REF22 : un renommage vu dans l'arbre de travail (` R`, après `git add -N`) saute l'ancien nom qui le suit,
    comme `R ` : il n'est pas lu, tronqué de trois caractères, pour un chemin changé."""
    assert fiches.chemins_du_statut(" R nouveau.md\0ancien nom.md\0") == ["nouveau.md"]
    assert fiches.chemins_du_statut(" C copie.md\0source.md\0 M a.md\0") == ["copie.md", "a.md"]


def test_ref22_py_du_statut_saute_l_ancien_nom_d_un_renommage_en_colonne_y():
    """REF22 : `py_du_statut` saute l'ancien nom d'un renommage ` R` : `a.py` n'est pas rendu `y`."""
    assert rapport.py_du_statut(" R b.py\0a.py\0") == ["b.py"]


def test_ref22_nom_etat_lit_un_numero_a_trois_chiffres(tmp_path):
    """REF22 : un contexte numéroté à trois chiffres compte — l'état `100-etat.md` est trouvé, et le numéro libre
    suit `125`, au lieu de `01-etat.md` ou `09-etat.md` ; le format `%02d` reste pour les petits numéros."""
    un, deux, petit = (str(tmp_path / n) for n in ("un", "deux", "petit"))
    for d, noms in ((un, ("100-etat.md", "101-truc.md")), (deux, ("08-vieux.md", "125-ref.md")),
                    (petit, ("07-a.md",))):
        for n in noms:
            ecrire(os.path.join(d, n), "x\n")
    assert (notes.nom_etat(un), notes.nom_etat(deux), notes.nom_etat(petit)) == (
        "100-etat.md", "126-etat.md", "08-etat.md")
