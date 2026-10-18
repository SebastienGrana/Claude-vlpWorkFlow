"""La couverture des lignes changées (REF8, décision D7 de la note `122`).

- La mesure : `scripts/test-vlp.py`, lancé seul, se relance sous `coverage` (`a_mesurer`, `mesurer`) ; vert, les
  mesures de chaque processus sont réunies en `.couverture/coverage.xml`, avec l'empreinte du code joué (VIT11).
- Le jugement : `vlp.py couverture`, appelé par `.githooks/pre-commit`, fait lire à `diff-cover` les lignes changées
  indexées ; sous `SEUIL` %, ou sans rapport pour ce code, le commit est refusé. Aucun seuil global.

Outils d'atelier, lancés par `uv run`, jamais importés. La décision (`verdict`) reçoit le rapport de `diff-cover`
et ne lance rien : elle se teste en mémoire (`methode-chantier.md`, « Coder dans le kit »).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

SEUIL = 90   # % des lignes changées couvertes : Google, « Code Coverage Best Practices » (2020) ; aucun seuil global
DOSSIER = ".couverture"   # sous la racine du kit, ignoré par Git et par l'empreinte (`KIT_EXCLUS`)
SANS_MESURE = ("VLP_COUVERTURE", "VLP_TOUS_ECARTS", "VLP_PONT")
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def chemins(racine):
    """(données, rapport, empreinte) de la mesure sous `racine`."""
    d = os.path.join(racine, DOSSIER)
    return os.path.join(d, "donnees"), os.path.join(d, "coverage.xml"), os.path.join(d, "empreinte")


def a_mesurer(seul, env=None):
    """Vrai si la suite doit se relancer sous `coverage` : ni sous `--seul` (une part de la suite), ni déjà mesurée
    (`VLP_COUVERTURE=1`), ni sous le mutant (`VLP_TOUS_ECARTS=1`, une copie mutée), ni lancée par le pont
    (`VLP_PONT=1`)."""
    env = os.environ if env is None else env
    return not seul and all(env.get(v) != "1" for v in SANS_MESURE)


def mesurer(racine, script, argv, empreinte, lanceur=None):
    """Relancer `script` sous `coverage`, puis, vert, réunir les mesures en `coverage.xml` et noter `empreinte` à côté.
    `lanceur` : la commande de coverage, `uv run --frozen coverage` d'office. Rendre le code de sortie — ou None sans
    uv : la suite tourne alors sans mesure, et le dit."""
    if lanceur is None:
        uv = shutil.which("uv")
        if not uv:
            print("COUVERTURE non mesurée : uv introuvable (uv sync) — un commit de .py sera refusé (REF8)")
            return None
        lanceur = [uv, "run", "--frozen", "coverage"]
    donnees, rapport, note = chemins(racine)
    os.makedirs(os.path.dirname(donnees), exist_ok=True)
    for vieux in (rapport, note):
        if os.path.exists(vieux):
            os.remove(vieux)
    env = dict(os.environ, VLP_COUVERTURE="1", COVERAGE_FILE=donnees)

    def coverage(*args):
        """Lancer `coverage <args>` dans `racine`, sous `env` ; rendre son code de sortie."""
        return subprocess.run([*lanceur, *args], cwd=racine, env=env).returncode

    coverage("erase")
    code = coverage("run", script, *argv)
    if code != 0:
        return code
    if coverage("combine", "-q") or coverage("xml", "-q", "-o", rapport):
        print("ÉCART: couverture — coverage combine ou xml a échoué, pas de rapport (REF8)")
        return 1
    with open(note, "w", encoding="utf-8") as f:
        f.write(empreinte + "\n")
    print("COUVERTURE mesurée : %s/coverage.xml" % DOSSIER)
    return 0


def verdict(rapport, seuil=SEUIL):
    """(code, lignes) depuis le rapport JSON de `diff-cover` : les fichiers aux lignes changées non couvertes, puis
    le bilan ; sous `seuil` %, refusé (1). Aucune ligne changée mesurable : rien à couvrir (0)."""
    total = rapport.get("total_num_lines", 0)
    if not total:
        return 0, ["COUVERTURE rien à couvrir : aucune ligne changée mesurée\n"]
    lignes = ["NON COUVERT %s : %s\n" % (c, ", ".join(str(n) for n in s["violation_lines"]))
              for c, s in sorted(rapport.get("src_stats", {}).items()) if s.get("violation_lines")]
    taux = rapport.get("total_percent_covered", 0)
    passe = taux >= seuil
    lignes.append("COUVERTURE %s %% des %d lignes changées, seuil %d %% — %s\n"
                  % (taux, total, seuil, "passe" if passe else "commit refusé"))
    return (0 if passe else 1), lignes


def py_indexes(racine):
    """Les `.py` indexés pour le commit (ajoutés, copiés, modifiés, renommés), ou None si Git échoue."""
    r = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], cwd=racine,
                       capture_output=True, encoding="utf-8", errors="replace")
    return None if r.returncode else [n for n in r.stdout.splitlines() if n.endswith(".py")]


def rapport_a_jour(racine, empreinte):
    """Vrai si le rapport existe et a été mesuré sur le code `empreinte`."""
    _, rapport, note = chemins(racine)
    try:
        with open(note, encoding="utf-8") as f:
            notee = f.read().strip()
    except OSError:
        return False
    return os.path.isfile(rapport) and notee == empreinte


def empreinte_du_kit(racine):
    """L'empreinte de VIT11 (`vlp_coeur.empreinte_kit`), le cœur importé ici seulement : un commit sans `.py` ne
    le charge pas."""
    import vlp_coeur
    return vlp_coeur.empreinte_kit(racine)


def juger(racine, sortie, seuil=SEUIL, empreinte_de=empreinte_du_kit):
    """Juger le commit indexé dans `racine` : rien à couvrir sans `.py`, `GARDE:` sans rapport mesuré sur le code
    d'aujourd'hui (`empreinte_de`), sinon le verdict de `diff-cover` sur les seules lignes indexées."""
    py = py_indexes(racine)
    if py is None:
        sortie.write("GARDE: couverture — git diff --cached a échoué dans %s\n" % racine)
        return 1
    if not py:
        sortie.write("COUVERTURE rien à couvrir : aucun .py dans le commit\n")
        return 0
    if not rapport_a_jour(racine, empreinte_de(racine)):
        sortie.write("GARDE: couverture — pas de rapport mesuré sur ce code : lancer la suite entière, "
                     "py -3 scripts/test-vlp.py, puis commiter (REF8)\n")
        return 1
    outil = shutil.which("diff-cover")
    if not outil:
        sortie.write("GARDE: couverture — diff-cover introuvable : uv sync, puis uv run (REF8)\n")
        return 1
    with tempfile.TemporaryDirectory() as t:
        json_ = os.path.join(t, "diff.json")
        r = subprocess.run([outil, chemins(racine)[1], "--compare-branch=HEAD", "--ignore-unstaged",
                            "--format", "json:" + json_], cwd=racine, capture_output=True, encoding="utf-8",
                           errors="replace")
        if r.returncode or not os.path.isfile(json_):
            sortie.write("GARDE: couverture — diff-cover sorti %d : %s\n"
                         % (r.returncode, ((r.stderr or r.stdout).strip().splitlines() or [""])[-1]))
            return 1
        with open(json_, encoding="utf-8") as f:
            code, lignes = verdict(json.load(f), seuil)
    sortie.write("".join(lignes))
    return code


def principal(argv, sortie=None):
    """`vlp.py couverture [--racine R]` : juger le commit indexé de `R`, le kit par défaut (le hook de commit)."""
    p = argparse.ArgumentParser(prog="vlp.py couverture")
    p.add_argument("--racine", default=KIT)
    return juger(os.path.abspath(p.parse_args(argv).racine), sortie or sys.stdout)
