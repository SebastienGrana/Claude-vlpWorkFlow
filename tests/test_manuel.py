"""REF36 : une aide par sous-commande de `vlp.py`, tirée de `scripts/noyau/manuel.py` — la ligne de `vlp.py --help`,
le détail de `vlp.py <sous-commande> --help` —, et la docstring de `vlp.py` qui n'en recopie que les lignes.
"""
import ast
import io
import os
import re
from contextlib import redirect_stderr, redirect_stdout

import concernes
import conserve
import couverture
import pytest
import retraits
from aides import SCRIPTS, mod
from noyau import manuel

AIGUILLEES = {"couverture": couverture, "concernes": concernes, "conserve": conserve, "retraits": retraits}


def aide(lancer, argv):
    """Le texte que `lancer(argv)` imprime avant de sortir 0 — un `--help` d'argparse."""
    sortie = io.StringIO()
    with pytest.raises(SystemExit) as fin, redirect_stdout(sortie), redirect_stderr(io.StringIO()):
        lancer(argv)
    assert fin.value.code == 0, (argv, sortie.getvalue())
    return sortie.getvalue()


def plat(texte):
    """Le texte, blancs réduits à une espace : argparse recoupe les lignes à la largeur du terminal."""
    return " ".join(texte.split())


def sous_commandes():
    """Les sous-commandes que déclare `main`, lues dans l'usage de `vlp.py -h`."""
    liste = re.search(r"\{([^}]+)\}", aide(lambda argv: mod.main(argv, io.StringIO()), ["-h"]))
    assert liste
    return liste.group(1).split(",")


def lignes_docstring():
    """`{nom: ligne}` des puces `` - `nom` — ligne `` de la docstring de `vlp.py`, lue par `ast` sans l'importer."""
    with open(os.path.join(SCRIPTS, "vlp.py"), encoding="utf-8") as f:
        doc = ast.get_docstring(ast.parse(f.read()), clean=False) or ""
    return dict(re.findall(r"^- `([a-z-]+)` — (.+)$", doc, re.M))


def test_chaque_sous_commande_a_son_detail():
    """`vlp.py <sous-commande> --help` rend le détail de `manuel.AIDES`, pour chacune des sous-commandes de `main`,
    et `AIDES` n'en nomme pas d'autre."""
    noms = sous_commandes()
    assert sorted(manuel.AIDES) == sorted(noms), "manuel : une entrée par sous-commande de main, ni plus ni moins"
    for nom in noms:
        ligne, detail = manuel.AIDES[nom]
        assert ligne.strip(), nom
        assert detail.strip(), nom
        texte = aide(lambda argv: mod.main(argv, io.StringIO()), [nom, "--help"])
        assert detail.strip().splitlines()[0] in texte, (nom, texte)


def test_l_aide_generale_liste_chaque_sous_commande_avec_sa_ligne():
    """`vlp.py --help` porte, pour chaque sous-commande — les aiguillées avant le cœur comprises —, son nom suivi de
    sa ligne."""
    texte = plat(aide(lambda argv: mod.main(argv, io.StringIO()), ["--help"]))
    for nom, ligne in {**{n: l for n, (l, _d) in manuel.AIDES.items()}, **manuel.AIGUILLEES}.items():
        assert "%s %s" % (nom, plat(ligne)) in texte, nom


def test_la_docstring_recopie_les_lignes_et_rien_d_autre():
    """La docstring de `vlp.py` : une puce par sous-commande, sa ligne mot pour mot celle de `--help`."""
    attendu = {**{n: l for n, (l, _d) in manuel.AIDES.items()}, **manuel.AIGUILLEES}
    assert lignes_docstring() == attendu


def test_les_aiguillees_ont_leur_detail_dans_leur_module():
    """Les sous-commandes que `vlp.py` aiguille avant le cœur : celles de `manuel.AIGUILLEES`, et leur `--help` rend
    la docstring de leur module."""
    with open(os.path.join(SCRIPTS, "vlp.py"), encoding="utf-8") as f:
        aiguillees = re.findall(r'sys\.argv\[1:2\] == \["([a-z-]+)"\]', f.read())
    assert sorted(aiguillees) == sorted(manuel.AIGUILLEES) == sorted(AIGUILLEES)
    for nom, module in AIGUILLEES.items():
        texte = aide(module.principal, ["--help"])
        assert (module.__doc__ or "").splitlines()[0] in texte, (nom, texte)
