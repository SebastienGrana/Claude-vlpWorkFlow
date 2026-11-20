"""Sépare les assertions composées (`PT018` de ruff) : une assertion par part, sans message, dans l'ordre (RUF1).

- Ce qui se sépare : un `assert` dont le test est un `and`, ou `not (… or …)` — le prédicat `composee` de
  `sante.py`, le seul. `assert a and b and c, msg` devient `assert a`, `assert b`, `assert c` ; un `and` entre
  parenthèses se sépare aussi ; `assert not (a or b)` devient `assert not a`, `assert not b` (un `not` sous le
  `not` s'annule). Le message est retiré : pytest affiche les valeurs comparées (choix du cadrage de RUF).
- Chaque part garde son texte source (`ast.get_source_segment`), entre parenthèses si elle tient sur plusieurs lignes
  ou ne tiendrait pas seule (`:=`, `yield`) ; sous un `not`, entre parenthèses aussi si c'est un `and`, un `or`, un
  `… if … else …` ou un `lambda`. Un commentaire après l'assertion reste, sur la dernière part.
- Ce qui ne se sépare pas, le fichier entier laissé intact et signalé `GARDE:` : un commentaire dans l'assertion (il
  se perdrait), une assertion qui partage sa ligne avec une autre instruction, un fichier qui ne se lit pas par `ast`,
  ou un texte réécrit qui ne se relit pas avec le bon nombre d'`assert`.

Aiguillé avant le cœur, comme `retraits.py` : bibliothèque standard seule, et le prédicat de `sante.py`.

`separer <chemin…> [--ecrire]` — sépare les assertions composées des fichiers `.py` nommés ou sous les dossiers
nommés (RUF1). Imprime `SEPARER <fichier> · <n> assertions → <m>` par fichier touché, `GARDE: <fichier> — <raison> :
laissé intact` par fichier refusé, puis `TOTAL <k> fichiers · <n> assertions → <m>` et `· rien d'écrit` ou, sous
`--ecrire`, `· écrits` : les fichiers sont alors réécrits, fins de ligne gardées. Sort 1 s'il y a une `GARDE:`,
0 sinon.
"""
import argparse
import ast
import io
import os
import sys
import tokenize

import sante

BOM = "﻿"
PARENS_SEULE = (ast.NamedExpr, ast.Yield, ast.YieldFrom, ast.Await)         # `assert x := 1` ne se lit pas
PARENS_SOUS_NOT = (ast.BoolOp, ast.IfExp, ast.Lambda, ast.NamedExpr, ast.Yield, ast.YieldFrom)


class Garde(Exception):
    """Un fichier qui ne se sépare pas sans risque ; le message dit pourquoi."""


def parts(e):
    """Les parts d'un test d'assertion : une liste de `(nœud, nié)`, dans l'ordre. Un `and` se déplie, `not (… or …)`
    se déplie en parts niées ; tout autre nœud est une part à lui seul."""
    if isinstance(e, ast.BoolOp) and isinstance(e.op, ast.And):
        return [p for v in e.values for p in parts(v)]
    if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.Not) and isinstance(e.operand, ast.BoolOp) \
            and isinstance(e.operand.op, ast.Or):
        return [p for v in e.operand.values for p in parts_niees(v)]
    return [(e, False)]


def parts_niees(e):
    """Les parts de `not e` : un `or` se déplie, un `not` s'annule (`not not a` → les parts de `a`), tout autre nœud
    est une part niée."""
    if isinstance(e, ast.BoolOp) and isinstance(e.op, ast.Or):
        return [p for v in e.values for p in parts_niees(v)]
    if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.Not):
        return parts(e.operand)
    return [(e, True)]


def texte_part(source, noeud, nie):
    """Le texte d'une part, `not` compris s'il est nié, prêt à suivre `assert `."""
    segment = ast.get_source_segment(source, noeud)
    if segment is None:
        raise Garde("une part sans texte source à la ligne %d" % noeud.lineno)
    plusieurs = "\n" in segment or "\r" in segment
    if nie:
        return "not (%s)" % segment if plusieurs or isinstance(noeud, PARENS_SOUS_NOT) else "not " + segment
    return "(%s)" % segment if plusieurs or isinstance(noeud, PARENS_SEULE) else segment


def colonne(ligne, octets):
    """La colonne en caractères d'un décalage `ast` en octets UTF-8 dans `ligne`."""
    return len(ligne.encode("utf-8")[:octets].decode("utf-8", "replace"))


def commentaires(source):
    """Les commentaires de `source` : une liste de `(ligne, colonne en caractères)`."""
    try:
        return [j.start for j in tokenize.generate_tokens(io.StringIO(source).readline) if j.type == tokenize.COMMENT]
    except (tokenize.TokenError, SyntaxError) as e:
        raise Garde("ne se tokenise pas : %s" % e) from e


def remplacement(source, lignes, noeud, comms):
    """Les lignes qui remplacent l'assertion `noeud` (fins de ligne comprises) ; `Garde` si elle partage sa ligne ou
    porte un commentaire en son sein."""
    premiere, derniere = lignes[noeud.lineno - 1], lignes[noeud.end_lineno - 1]
    debut = colonne(premiere, noeud.col_offset)
    fin = colonne(derniere, noeud.end_col_offset)
    retrait = premiere[:debut]
    corps = derniere.rstrip("\r\n")
    reste = corps[fin:]
    if retrait.strip() or (reste.strip() and not reste.lstrip().startswith("#")):
        raise Garde("l'assertion de la ligne %d partage sa ligne avec une autre instruction" % noeud.lineno)
    for ligne, col in comms:
        if noeud.lineno <= ligne <= noeud.end_lineno and not (ligne == noeud.end_lineno and col >= fin):
            raise Garde("un commentaire dans l'assertion de la ligne %d se perdrait" % noeud.lineno)
    eol = derniere[len(corps):]                  # vide sur une dernière ligne sans fin : elle le reste
    textes = [retrait + "assert " + texte_part(source, n, nie) for n, nie in parts(noeud.test)]
    textes[-1] += reste.rstrip() if reste.strip() else ""
    return [t + (eol or "\n") for t in textes[:-1]] + [textes[-1] + eol]


def separer(texte):
    """`(texte réécrit, n assertions composées, m assertions qui les remplacent)` ; le texte tel quel si `n` vaut 0.
    `Garde` si le fichier ne se lit pas, ou si une assertion ne se sépare pas sans risque : rien n'est alors rendu."""
    bom = BOM if texte.startswith(BOM) else ""
    source = texte[len(bom):]
    try:
        arbre = ast.parse(source)
    except (SyntaxError, ValueError) as e:
        raise Garde("ne se lit pas par ast : %s" % e) from e
    composees = sorted((s for s in ast.walk(arbre) if isinstance(s, ast.Assert) and sante.composee(s)),
                       key=lambda s: s.lineno, reverse=True)
    if not composees:
        return texte, 0, 0
    lignes = io.StringIO(source, newline="").readlines()    # coupé comme `ast` : \n, \r\n, \r — ni \f ni
    comms = commentaires(source)
    m = 0
    for noeud in composees:                      # du bas vers le haut : les numéros de ligne d'au-dessus tiennent
        nouvelles = remplacement(source, lignes, noeud, comms)
        lignes[noeud.lineno - 1:noeud.end_lineno] = nouvelles
        m += len(nouvelles)
    rendu = "".join(lignes)
    relu(source, rendu, len(composees), m)
    return bom + rendu, len(composees), m


def relu(avant, apres, n, m):
    """Vérifier que `apres` se relit par `ast` et porte exactement `m - n` assertions de plus qu'`avant` ; `Garde`
    sinon."""
    try:
        arbre = ast.parse(apres)
    except (SyntaxError, ValueError) as e:
        raise Garde("le texte réécrit ne se relit pas par ast : %s" % e) from e
    attendu = nb_assert(ast.parse(avant)) - n + m
    if nb_assert(arbre) != attendu:
        raise Garde("le texte réécrit porte %d assertions, %d attendues" % (nb_assert(arbre), attendu))


def nb_assert(arbre):
    """Le nombre d'instructions `assert` d'un arbre `ast`, fonctions imbriquées comprises."""
    return sum(isinstance(s, ast.Assert) for s in ast.walk(arbre))


def fichiers(chemins):
    """Les fichiers `.py` nommés, ou sous les dossiers nommés (sans `__pycache__`), triés, en barres obliques."""
    vus = []
    for c in chemins:
        if os.path.isdir(c):
            for dossier, sous, noms in os.walk(c):
                sous[:] = sorted(s for s in sous if s != "__pycache__")
                vus.extend(os.path.join(dossier, n) for n in sorted(noms) if n.endswith(".py"))
        else:
            vus.append(c)
    return sorted({v.replace("\\", "/") for v in vus})


def traiter(chemin, ecrire, sortie):
    """Séparer un fichier, et l'écrire sous `ecrire` : `(n, m)`, ou None sur une `GARDE:` (imprimée)."""
    try:
        with open(chemin, encoding="utf-8", newline="") as f:
            texte = f.read()
        rendu, n, m = separer(texte)
    except (OSError, UnicodeDecodeError, Garde) as e:
        sortie.write("GARDE: %s — %s : laissé intact\n" % (chemin, e))
        return None
    if n:
        sortie.write("SEPARER %s · %d assertions → %d\n" % (chemin, n, m))
        if ecrire:
            with open(chemin, "w", encoding="utf-8", newline="") as f:
                f.write(rendu)
    return n, m


def principal(argv, sortie=None):
    """`vlp.py separer <chemin…> [--ecrire]` : 0, ou 1 s'il y a eu une `GARDE:`."""
    p = argparse.ArgumentParser(prog="vlp.py separer", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("chemins", nargs="+")
    p.add_argument("--ecrire", action="store_true")
    a = p.parse_args(argv)
    sortie = sortie or sys.stdout
    k = n = m = 0
    gardes = 0
    for chemin in fichiers(a.chemins):
        r = traiter(chemin, a.ecrire, sortie)
        if r is None:
            gardes += 1
        elif r[0]:
            k, n, m = k + 1, n + r[0], m + r[1]
    sortie.write("TOTAL %d fichiers · %d assertions → %d · %s\n"
                 % (k, n, m, "écrits" if a.ecrire else "rien d'écrit (--ecrire pour réécrire)"))
    return 1 if gardes else 0
