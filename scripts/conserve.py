"""Aucune règle ne se perd quand on découpe ou range une doc (REF16, `Q6` de la note `122`).

`vlp.py conserve <avant>… --apres <après>…` : chaque ligne de texte des fichiers d'avant — hors titres (`#`), lignes
vides et séparateurs (`---`, `***`, `___`, une clôture de bloc, une ligne de tableau sans lettre ; un `#` dans un
bloc de code est du texte) — doit se retrouver, espaces de
bord ôtés, comme ligne d'un des fichiers d'après. `CONSERVE <n> lignes lues · <p> perdue(s)`, puis une ligne
`PERDUE <fichier>:<ligne> <texte>` par perte ; sort 1 s'il y en a une. Un fichier illisible : `GARDE:`, sort 1.

Aiguillé avant le cœur, comme `retraits.py` : bibliothèque standard seule, rien d'importé du kit.
"""
import argparse
import re
import sys

SEPARATEUR = re.compile(r"^(#.*|-{3,}|\*{3,}|_{3,}|`{3,}.*|[|:\s-]*)$")


def texte(ligne):
    """La ligne sans ses espaces de bord, ou None si elle ne porte pas de texte (titre, vide, séparateur)."""
    nue = ligne.strip()
    return None if SEPARATEUR.match(nue) else nue


def textes(lignes):
    """[texte ou None] de chaque ligne (`texte`) ; dans un bloc ```, une ligne `#…` est un commentaire de code, pas un
    titre : elle compte (REF22). Un bloc ouvert sans clôture court jusqu'à la fin de la liste."""
    dedans, rendu = False, []
    for ligne in lignes:
        nue = ligne.strip()
        rendu.append(nue if dedans and nue.startswith("#") else texte(ligne))
        dedans ^= nue.startswith("```")
    return rendu


def perdues(avant, apres):
    """[(numéro, texte)] des lignes de texte de `avant` (liste de lignes) absentes de `apres` (liste de lignes)."""
    vues = set(textes(apres))
    return [(i, t) for i, t in enumerate(textes(avant), 1) if t is not None and t not in vues]


def lignes(chemin):
    """Les lignes d'un fichier, en UTF-8."""
    with open(chemin, encoding="utf-8") as f:
        return f.read().splitlines()


def principal(argv, sortie=None):
    """`vlp.py conserve <avant>… --apres <après>…` : ce que dit la docstring du module."""
    p = argparse.ArgumentParser(prog="vlp.py conserve", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("avant", nargs="+")
    p.add_argument("--apres", nargs="+", required=True)
    a = p.parse_args(argv)
    sortie = sortie or sys.stdout
    try:
        apres = [l for c in a.apres for l in lignes(c)]
        avant = {c: lignes(c) for c in a.avant}
    except OSError as e:
        sortie.write("GARDE: conserve — fichier illisible : %s\n" % e)
        return 1
    lues = sum(1 for ls in avant.values() for t in textes(ls) if t is not None)
    pertes = [(c, i, t) for c, ls in avant.items() for i, t in perdues(ls, apres)]
    sortie.write("CONSERVE %d lignes lues · %d perdue(s)\n" % (lues, len(pertes)))
    for c, i, t in pertes:
        sortie.write("PERDUE %s:%d %s\n" % (c, i, t))
    return 1 if pertes else 0
