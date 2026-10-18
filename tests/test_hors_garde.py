"""REF41 : un worktree retiré par `fusionner` qui garde des chemins hors commit (un `HORS:` laissé par `commiter`) :
leur diff, non suivis compris, va dans un correctif sous le dossier Git, et `GARDÉ <n> chemin(s) : <correctif>` le
dit — migré de `tester_ref41_hors_garde` (l'ancienne suite maison, REF56). REF56 : le correctif est écrit par Git en
octets, un fichier CRLF ou latin-1 y garde ses octets ; un correctif que `git apply --check` rejette est `PERDU`.
"""
import os
import re
import shutil
import subprocess

import pytest
from aides import appel, ecrire, mod

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git absent : le correctif gardé n'est pas testé")


def git(d, *args):
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("git %s : %s" % (" ".join(args), r.stderr))
    return r.stdout


def code_git(d, *args):
    return subprocess.run(["git"] + list(args), cwd=d, capture_output=True).returncode


def commit(d, message):
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", message)


def deposer(tmp_path, departs):
    """Un dépôt `d` (fins de ligne telles quelles, `core.autocrlf=false`), une fiche W1, les fichiers `departs`
    (chemin → octets) commités, puis un worktree `wt-a` où W1 est commitée : rend (d, wa, fichier de fiches)."""
    d, wa = str(tmp_path / "d"), str(tmp_path / "wt-a")
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "core.autocrlf", "false")
    fiches = os.path.join(d, "ctx", "f.md")
    ecrire(fiches, "# F\n\n## W1 [ ] — a\n")
    for nom, octets in departs.items():
        with open(os.path.join(d, nom), "wb") as f:
            f.write(octets)
    commit(d, "départ")
    git(d, "worktree", "add", "-q", "-b", "a", wa, "main")
    ecrire(os.path.join(wa, "b.txt"), "b\n")
    commit(wa, "W1 : a")
    return d, wa, fiches


def garde(s):
    """(nombre de chemins, correctif) de la ligne `GARDÉ`, ou (None, "")."""
    m = re.search(r"^GARDÉ (\d+) chemin\(s\) : (.+)$", s, re.M)
    return (m.group(1), m.group(2)) if m else (None, "")


def test_ref41_hors_commit_garde(tmp_path):
    d, wa, fiches = deposer(tmp_path, {"doc.txt": b"un\n"})
    ecrire(os.path.join(wa, "doc.txt"), "un\ndeux\n")          # suivi, hors commit
    ecrire(os.path.join(wa, "neuf.txt"), "neuf\n")             # non suivi
    code, s = appel(["fusionner", fiches, "W1", "--worktree", wa])
    n, correctif = garde(s)
    existe = bool(correctif) and os.path.isfile(correctif)
    sous_git = existe and os.path.normcase(os.path.realpath(correctif)).startswith(
        os.path.normcase(os.path.realpath(os.path.join(d, ".git"))) + os.sep)
    check = code_git(d, "apply", "--check", correctif) if existe else None
    intact = git(d, "status", "--porcelain")
    assert code == 0 and n == "2" and sous_git and "PERDU" not in s and check == 0 and intact == "", (
        "REF41 : chemins hors commit → GARDÉ 2 chemin(s) : <correctif sous .git>, sort 0, pas de PERDU, "
        "git apply --check passe sur main fusionnée, arbre propre" + " · %r" % ((code, s, correctif, sous_git, check, intact),))


def test_ref56_crlf_et_latin1_gardent_leurs_octets(tmp_path):
    neufs = {"crlf.txt": b"un\r\ndeux\r\ntrois\r\n", "latin.txt": b"caf\xe9 cr\xe8me\n"}
    d, wa, fiches = deposer(tmp_path, {"crlf.txt": b"un\r\ndeux\r\n", "latin.txt": b"caf\xe9\n"})
    for nom, octets in neufs.items():
        with open(os.path.join(wa, nom), "wb") as f:
            f.write(octets)
    code, s = appel(["fusionner", fiches, "W1", "--worktree", wa])
    n, correctif = garde(s)
    check = code_git(d, "apply", "--check", correctif) if correctif else None
    applique = code_git(d, "apply", correctif) if check == 0 else None
    rendus = {nom: open(os.path.join(d, nom), "rb").read() for nom in neufs}
    assert code == 0 and n == "2" and "PERDU" not in s and check == 0 and applique == 0 and rendus == neufs, (
        "REF56 : un CRLF et un latin-1 hors commit → GARDÉ 2, git apply --check passe, octets rendus exacts"
        + " · %r" % ((code, s, check, applique, rendus),))


def test_ref56_correctif_rejete_est_perdu(tmp_path, monkeypatch):
    _, wa, fiches = deposer(tmp_path, {"doc.txt": b"un\n"})
    ecrire(os.path.join(wa, "doc.txt"), "un\ndeux\n")
    vrai = mod.git_texte
    monkeypatch.setattr(mod.noyau.relecture, "git_texte", lambda args, cwd, env=None: (1, "refusé") if args[:2] == ["apply", "--check"]
                        else vrai(args, cwd, env))
    code, s = appel(["fusionner", fiches, "W1", "--worktree", wa])
    m = re.search(r"^PERDU 1 chemin\(s\) non commités du worktree : doc\.txt — correctif rejeté par git apply "
                  r"--check : (.+)$", s, re.M)
    assert m and os.path.isfile(m.group(1)) and "GARDÉ" not in s, (
        "REF56 : un correctif que git apply --check rejette → PERDU, avec son chemin" + " · %r" % ((code, s),))
