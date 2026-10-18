"""Le cliquet voit le code sorti de `vlp_coeur.py` (REF46) : `scripts/noyau/` compte pour les fonctions et pour les
tailles. Avant, `scripts/*.py` seul : les fonctions déplacées par REF45 n'étaient plus gardées."""
import os

import sante


def poser(racine, relatif, texte="def f():\n    return 1\n"):
    chemin = os.path.join(racine, *relatif.split("/"))
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)
    return chemin


def test_les_fonctions_d_un_sous_dossier_de_scripts(tmp_path):
    haut = poser(str(tmp_path), "scripts/a.py")
    bas = poser(str(tmp_path), "scripts/noyau/b.py")
    assert sante.chemins_de(str(tmp_path), None) == sorted([haut, bas])


def test_la_taille_d_un_sous_dossier_de_scripts(tmp_path):
    poser(str(tmp_path), "scripts/a.py")
    poser(str(tmp_path), "scripts/noyau/b.py", "x = 1\n" * 3)
    poser(str(tmp_path), "tests/t.py")
    assert sante.tailles_de(str(tmp_path)) == {"scripts/a.py": 2, "scripts/noyau/b.py": 3, "tests/t.py": 2}
