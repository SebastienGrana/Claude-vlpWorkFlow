"""Un test retiré ou affaibli, rendu visible au commit (REF11, note `122` : le piège nommé par Kent Beck, et la carte
système de Claude 3.7 — un test supprimé, mis en `skip`, ou une assertion retirée pour que tout passe).

- Les comptes : sur l'**ensemble** des fichiers de test (`tests/**.py`, `scripts/test-*.py`), par `ast` — les tests
  (`def test…`), les appels à `verifier`, les `assert`, et les `skip`/`xfail`. Une découpe déplace un test d'un fichier
  à l'autre sans rien retirer : seule la somme compte.
- Le jugement : `vlp.py retraits <message>`, appelé par `.githooks/commit-msg` — le seul hook qui voit le message.
  `HEAD` contre l'index : une baisse des tests, `verifier` ou `assert`, une hausse des `skip`, refusent le commit, sauf
  une ligne `Test retiré : <raison>` dans le message (hors commentaires `#`).

Aiguillé avant le cœur, comme `couverture.py` : bibliothèque standard seule, rien d'importé du kit.

`retraits <fichier du message> [--racine R]` — un test retiré ou affaibli au commit (REF11 ; `retraits.py`, aiguillé
avant le cœur ; lancé par `.githooks/commit-msg`, la racine du dépôt par défaut) : compte par `ast`, sur l'ensemble
des fichiers de test de `HEAD` et de l'index, les tests, `verifier`, `assert` et `skip`/`xfail`. Imprime
`RETRAITS tests a → b · …`, `ILLISIBLE <fichier>` par test qui ne se lit pas, puis `— passe` (sort 0) ou, sur une
baisse ou plus de `skip` sans ligne `Test retiré : <raison>` dans le message, `— commit refusé` (sort 1). Sans
`HEAD` : `RETRAITS premier commit …` (sort 0) ; message illisible : `GARDE:`, sort 1.
"""
import argparse
import ast
import os
import re
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAISON = re.compile(r"^Test retiré : \S", re.MULTILINE)
SKIPS = frozenset({"skip", "skipif", "xfail", "importorskip", "skipTest"})
BAISSES = ("tests", "verifier", "assert")   # un compte qui ne doit pas baisser ; `skip`, lui, ne doit pas monter


def est_test(chemin):
    """Vrai si `chemin` (relatif à la racine, barres obliques) est un fichier de test Python."""
    return chemin.endswith(".py") and (chemin.startswith("tests/") or (
        os.path.dirname(chemin) == "scripts" and os.path.basename(chemin).startswith("test-")))


def compter(texte):
    """Les comptes d'un fichier de test (`tests`, `verifier`, `assert`, `skip`), ou None s'il ne se lit pas."""
    try:
        arbre = ast.parse(texte)
    except (SyntaxError, ValueError):
        return None
    n = dict.fromkeys((*BAISSES, "skip"), 0)
    for noeud in ast.walk(arbre):
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)) and noeud.name.startswith("test"):
            n["tests"] += 1
        elif isinstance(noeud, ast.Assert):
            n["assert"] += 1
        elif isinstance(noeud, ast.Call) and nom_de(noeud.func) == "verifier":
            n["verifier"] += 1
        elif nom_de(noeud) in SKIPS:
            n["skip"] += 1
    return n


def nom_de(noeud):
    """Le nom que porte un nœud `Name` ou `Attribute` (`pytest.mark.skip` → `skip`), sinon None."""
    if isinstance(noeud, ast.Name):
        return noeud.id
    return noeud.attr if isinstance(noeud, ast.Attribute) else None


def ecarts(avant, apres):
    """Les écarts qui affaiblissent la suite, `<compte> <avant> → <après>` : une baisse de `BAISSES`, une hausse des
    `skip`."""
    return ["%s %d → %d" % (c, avant[c], apres[c]) for c in (*BAISSES, "skip")
            if (apres[c] > avant[c] if c == "skip" else apres[c] < avant[c])]


def raison(message):
    """Vrai si le message porte une ligne `Test retiré : <raison>` non vide, hors des lignes de commentaire."""
    return bool(RAISON.search("\n".join(l for l in message.splitlines() if not l.startswith("#"))))


def git(racine, *args, entree=None):
    """(code, sortie en octets) d'une commande `git` dans `racine`."""
    r = subprocess.run(["git", *args], cwd=racine, input=entree, capture_output=True, check=False)
    return r.returncode, r.stdout


def textes(racine, rev):
    """Les fichiers de test de `rev` (`HEAD`, ou `""` pour l'index) : {chemin: texte}, lus d'un seul `cat-file` ; `{}`
    sans fichier de test. Un nom non ASCII se lit tel quel (`core.quotepath=false`, REF22) : cité, il ne finissait
    plus par `.py` et ses tests ne comptaient pas. Un BOM UTF-8 en tête est ôté : `ast.parse` le refuse, et le
    fichier ré-enregistré passait pour vidé de ses tests (REF22)."""
    code, liste = git(racine, "-c", "core.quotepath=false",
                      *(["ls-tree", "-r", "--name-only", rev] if rev else ["ls-files", "--cached"]))
    chemins = [c for c in liste.decode("utf-8", "replace").splitlines() if est_test(c)] if code == 0 else []
    if not chemins:
        return {}
    _, sortie = git(racine, "cat-file", "--batch",
                    entree="".join("%s:%s\n" % (rev, c) for c in chemins).encode("utf-8"))
    lus, i = {}, 0
    for c in chemins:
        fin = sortie.index(b"\n", i)
        tete = sortie[i:fin].split()
        i = fin + 1
        if len(tete) == 3 and tete[1] == b"blob":
            taille = int(tete[2])
            lus[c] = sortie[i:i + taille].decode("utf-8", "replace").lstrip("﻿")   # un BOM : REF22
            i += taille + 1
    return lus


def total(lus):
    """(comptes sommés, fichiers illisibles) d'un {chemin: texte}."""
    somme, illisibles = dict.fromkeys((*BAISSES, "skip"), 0), []
    for c, texte in sorted(lus.items()):
        n = compter(texte)
        if n is None:
            illisibles.append(c)
            continue
        for k in somme:
            somme[k] += n[k]
    return somme, illisibles


def juger(racine, message, sortie):
    """Juger l'index de `racine` contre `HEAD`, au vu de `message` : 0 si rien ne s'affaiblit ou si le message le
    justifie, 1 sinon. Sans `HEAD` (premier commit), rien à comparer."""
    if git(racine, "rev-parse", "--verify", "-q", "HEAD")[0]:
        sortie.write("RETRAITS premier commit, rien à comparer\n")
        return 0
    (avant, _), (apres, illisibles) = total(textes(racine, "HEAD")), total(textes(racine, ""))
    sortie.write("RETRAITS %s\n" % " · ".join("%s %d → %d" % (c, avant[c], apres[c]) for c in avant))
    for c in illisibles:
        sortie.write("ILLISIBLE %s : ses tests ne se comptent pas\n" % c)
    trop = ecarts(avant, apres)
    if not trop:
        sortie.write("RETRAITS rien de retiré ni d'affaibli — passe\n")
        return 0
    if raison(message):
        sortie.write("RETRAITS %s — passe, le message dit pourquoi\n" % ", ".join(trop))
        return 0
    sortie.write("RETRAITS %s — commit refusé : un test retiré ou affaibli s'explique dans le message, par une "
                 "ligne « Test retiré : <raison> » (REF11)\n" % ", ".join(trop))
    return 1


def principal(argv, sortie=None):
    """`vlp.py retraits <fichier du message> [--racine R]` : le hook `commit-msg`, la racine du dépôt par défaut."""
    p = argparse.ArgumentParser(prog="vlp.py retraits", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("message")
    p.add_argument("--racine", default=".")
    a = p.parse_args(argv)
    sortie = sortie or sys.stdout
    try:
        with open(a.message, encoding="utf-8", errors="replace") as f:
            message = f.read()
    except OSError as e:
        sortie.write("GARDE: retraits — message illisible : %s\n" % e)
        return 1
    return juger(os.path.abspath(a.racine), message, sortie)
