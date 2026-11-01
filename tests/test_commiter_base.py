"""`commiter` dans le kit et la base partagée du cliquet (`scripts/sante-base.json`) : deux fiches qui la changent
chacune (REF33, défaut `E12`). Le commit de l'une ne doit porter que sa part de la base — les lignes de ses fichiers —,
pas celle de l'autre, qui reste sur le disque pour le commit suivant.
"""
import json
import os
import subprocess

from aides import appel, ecrire, mod

BASE = "scripts/sante-base.json"


def base(entrees, tailles):
    """Une base au format de `sante.ecrire_base` : la tête sur une ligne, une fonction par ligne, triées."""
    tete = json.dumps({"format": 1, "ruff": "0", "forcee": [], "fichiers": tailles}, ensure_ascii=False)[:-1]
    lignes = [json.dumps({"fichier": f, "fonction": n, "empreinte": e, "ast": [1, 1, 1, 1, 1, 0], "doc": True})
              for f, n, e in sorted(entrees)]
    return tete + ', "fonctions": [\n' + ",\n".join(lignes) + "\n]}\n"


def git(d, *args):
    """`git <args>` dans `d` : sa sortie."""
    return subprocess.run(["git", *args], cwd=d, capture_output=True, encoding="utf-8", check=True).stdout


def test_commiter_ne_prend_que_sa_part_de_la_base(tmp_path, init_git, monkeypatch):
    d = str(tmp_path / "d")
    for cle, val in (("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig")), ("GIT_CONFIG_NOSYSTEM", "1"),
                     ("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"), ("GIT_COMMITTER_NAME", "t"),
                     ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(cle, val)
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    ecrire(str(tmp_path / "gitconfig"), "")
    fiches = os.path.join(d, "ctx", "fiches.md")
    ecrire(fiches, "# Essai\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
        "<!-- FICHE:%s -->\n## %s [ ] — Toucher %s\n\n**Dépend de** : rien.\n**Fichiers** : `scripts/%s`.\n\n"
        "**Critère de fin**\nRien.\n<!-- /FICHE -->\n" % (f, f, n, n) for f, n in (("C1", "a.py"), ("C2", "b.py"))))
    for n in ("scripts/a.py", "scripts/b.py", ".claude-plugin/plugin.json", "tests/conftest.py"):
        ecrire(os.path.join(d, n), "x = 1\n")
    depart = base([("scripts/a.py", "fa", "a0"), ("scripts/b.py", "fb", "b0")], {"scripts/a.py": 1, "scripts/b.py": 1})
    ecrire(os.path.join(d, BASE), depart)
    init_git(d)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "départ")
    # Les deux fiches ont joué dans le même dossier, aucune n'est commitée : chacune a changé son fichier et sa ligne.
    ecrire(os.path.join(d, "scripts/a.py"), "x = 2\n")
    ecrire(os.path.join(d, "scripts/b.py"), "x = 2\ny = 2\n")
    tout = base([("scripts/a.py", "fa", "a1"), ("scripts/b.py", "fb", "b1")], {"scripts/a.py": 1, "scripts/b.py": 2})
    ecrire(os.path.join(d, BASE), tout)
    mod.noter_suite_verte(d, mod.empreinte_kit(d))      # cocher dans le kit exige la suite verte (VIT11)
    code, sortie = appel(["commiter", fiches, "C1"])
    assert code == 0, sortie
    assert git(d, "show", "HEAD:" + BASE) == base([("scripts/a.py", "fa", "a1"), ("scripts/b.py", "fb", "b0")],
                                                  {"scripts/a.py": 1, "scripts/b.py": 1})
    with open(os.path.join(d, BASE), encoding="utf-8", newline="") as f:
        assert f.read() == tout      # le disque garde la base entière : la part de C2 attend son commit
