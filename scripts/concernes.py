"""Les tests concernés par des fonctions (REF13, choix `Q3` de la note `122`) : des consignes TDD seules ont augmenté les
régressions ; la liste des tests concernés par le changement les a réduites (TDAD, preprint 2026).

- La mesure : la suite entière, sous `coverage` (`couverture.py`), avec `dynamic_context = "test_function"`
  (`pyproject.toml`) — chaque ligne mesurée porte le nom du test qui l'a exécutée.
- La lecture : `vlp.py concernes <fonction>…` trouve chaque fonction dans `scripts/` par `ast`, puis lit dans
  `.couverture/donnees` (une base SQLite, lue par `sqlite3`) les tests passés par ses lignes. La carte de
  `/vlp:tache` en imprime une ligne pour la prochaine fiche (`ligne_carte`).

Aiguillé avant le cœur, comme `couverture.py` : bibliothèque standard seule, aucun paquet à l'exécution.

`concernes <fonction>… [--racine R]` — les tests qui exécutent ces fonctions (REF13 ; `concernes.py`, aiguillé
avant le cœur) : chaque fonction trouvée sous `<racine>/scripts/` par `ast`, ses lignes lues dans la mesure par test
de la dernière suite entière (`.couverture/donnees`, `dynamic_context = "test_function"`). Imprime `ABSENTE <nom>`
par fonction introuvable, `CONCERNES <n> test(s) pour <noms>`, puis un test par ligne ; sans mesure, ou sans
contexte par test : `GARDE:`, sort 1. La carte en tire `CONCERNES <fiche>=…` pour la prochaine fiche.
"""
import argparse
import ast
import glob
import os
import re
import sqlite3
import sys
from contextlib import closing

DONNEES = os.path.join(".couverture", "donnees")   # le fichier de mesure de `couverture.chemins`
NOMME = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")   # un nom entre accents graves, dans le texte d'une fiche
MONTRES = 12   # tests montrés sur la ligne de la carte ; le reste se compte


def fonctions(racine, noms):
    """{nom: [(chemin relatif, première ligne, dernière ligne)]} des fonctions `noms` définies sous `racine/scripts/` ;
    une fonction absente n'a pas d'entrée, un fichier illisible est sauté."""
    voulus, trouvees = set(noms), {}
    for chemin in sorted(glob.glob(os.path.join(racine, "scripts", "**", "*.py"), recursive=True)):
        try:
            with open(chemin, encoding="utf-8") as f:
                arbre = ast.parse(f.read())
        except (OSError, SyntaxError, ValueError):
            continue
        rel = os.path.relpath(chemin, racine).replace(os.sep, "/")
        for n in ast.walk(arbre):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in voulus:
                trouvees.setdefault(n.name, []).append((rel, n.lineno, n.end_lineno or n.lineno))
    return trouvees


def lignes_de_numbits(numbits):
    """Les numéros de ligne d'un champ `numbits` de coverage : le bit `i % 8` de l'octet `i // 8` dit la ligne `i`."""
    return {i * 8 + j for i, octet in enumerate(numbits) for j in range(8) if octet & (1 << j)}


def contextes(base, rel, debut, fin):
    """Les contextes (noms de tests) de la base `base` passés par les lignes `debut`–`fin` du fichier dont le chemin
    mesuré finit par `rel` ; le contexte vide (hors d'un test) n'en est pas un."""
    vus = set()
    for id_, chemin in base.execute("SELECT id, path FROM file"):
        if not chemin.replace("\\", "/").endswith("/" + rel):
            continue
        vus.update(ctx for (ctx,) in base.execute(
            "SELECT DISTINCT context.context FROM arc JOIN context ON arc.context_id = context.id WHERE file_id = ? "
            "AND (fromno BETWEEN ? AND ? OR tono BETWEEN ? AND ?)", (id_, debut, fin, debut, fin)))
        for ctx, bits in base.execute("SELECT context.context, numbits FROM line_bits JOIN context "
                                      "ON line_bits.context_id = context.id WHERE file_id = ?", (id_,)):
            if any(debut <= n <= fin for n in lignes_de_numbits(bits)):
                vus.add(ctx)
    vus.discard("")
    return vus


def ouvrir(racine):
    """La base de mesure de `racine` en lecture seule, ou None si elle manque."""
    chemin = os.path.join(racine, DONNEES)
    if not os.path.isfile(chemin):
        return None
    return sqlite3.connect("file:%s?mode=ro" % chemin.replace("\\", "/"), uri=True)


def par_test(base):
    """Vrai si la mesure porte des contextes par test (`dynamic_context`), pas le seul contexte vide."""
    return base.execute("SELECT COUNT(*) FROM context WHERE context != ''").fetchone()[0] > 0


def concernes(racine, noms, base=None, trouvees=None):
    """(tests triés, fonctions absentes) : les tests passés par au moins une des fonctions `noms` ; `trouvees`, leurs
    lieux déjà lus par `fonctions`."""
    base = base or ouvrir(racine)
    trouvees, tests = trouvees if trouvees is not None else fonctions(racine, noms), set()
    if base is not None:
        for lieux in trouvees.values():
            for rel, debut, fin in lieux:
                tests |= contextes(base, rel, debut, fin)
    return sorted(tests), [n for n in noms if n not in trouvees]


def ligne_carte(racine, fiche, texte):
    """La ligne `CONCERNES <fiche>=…` de la carte : les tests passés par les fonctions que le texte de la fiche nomme
    entre accents graves ; None sans mesure par test ou sans fonction nommée."""
    base = ouvrir(racine)
    if base is None:
        return None
    with closing(base):
        noms = list(dict.fromkeys(NOMME.findall(texte)))
        lieux = fonctions(racine, noms)
        if not lieux or not par_test(base):
            return None
        tests, _ = concernes(racine, list(lieux), base, lieux)
    reste = " … et %d autres" % (len(tests) - MONTRES) if len(tests) > MONTRES else ""
    return "CONCERNES %s=%d test(s) pour %s : %s%s" % (fiche, len(tests), ", ".join(n for n in noms if n in lieux),
                                                     ", ".join(tests[:MONTRES]) or "aucun", reste)


def principal(argv, sortie=None):
    """`vlp.py concernes <fonction>… [--racine R]` : les tests qui exécutent ces fonctions, lus dans la dernière mesure
    de la suite entière ; la racine du kit par défaut."""
    p = argparse.ArgumentParser(prog="vlp.py concernes", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("noms", nargs="+")
    p.add_argument("--racine", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = p.parse_args(argv)
    sortie = sortie or sys.stdout
    racine = os.path.abspath(a.racine)
    base = ouvrir(racine)
    if base is None:
        sortie.write("GARDE: concernes — pas de mesure sous %s : lancer la suite entière, "
                     "uv run --frozen pytest -n 4 (REF13)\n" % racine)
        return 1
    with closing(base):
        if not par_test(base):
            sortie.write("GARDE: concernes — la mesure n'a aucun contexte par test : dynamic_context absent de "
                         "[tool.coverage.run] ? (REF13)\n")
            return 1
        tests, absentes = concernes(racine, a.noms, base)
    sortie.write("".join("ABSENTE %s\n" % n for n in absentes))
    sortie.write("CONCERNES %d test(s) pour %s\n" % (len(tests), ", ".join(n for n in a.noms if n not in absentes)))
    sortie.write("".join("  %s\n" % t for t in tests))
    return 0
