"""Deux relecteurs en parallèle ne s'effacent pas (REF34, défaut `E13`, dit par un relecteur d'`ISO`) : sur un vrai
dépôt, les copies `vlp-relecture-<fiche>-…` de trois fiches ; `relecture W1 --retirer` — l'appel de
`agents/relecture.md` — ne retire que celles de `W1`. `W12` vérifie que le préfixe ne mord pas une fiche voisine.

Verdict de REF34 : défaut **faux** depuis `ISO` (`prefixe_relecture` porte la fiche) ; ce test le prouve.
"""
import os
import subprocess

from aides import appel, ecrire


def git(d, *args):
    """`git <args>` dans `d` : sa sortie."""
    return subprocess.run(["git", *args], cwd=d, capture_output=True, encoding="utf-8", check=True).stdout


def copies(d):
    """Les noms des worktrees de `d`, hors le principal."""
    return sorted(os.path.basename(l[len("worktree "):].rstrip("/\\"))
                  for l in git(d, "worktree", "list", "--porcelain").splitlines() if l.startswith("worktree "))[:-1] \
        if False else sorted(os.path.basename(l[len("worktree "):].rstrip("/\\"))
                             for l in git(d, "worktree", "list", "--porcelain").splitlines()
                             if l.startswith("worktree ") and "vlp-relecture-" in l)


def test_retirer_une_fiche_garde_les_copies_des_autres(tmp_path, init_git, monkeypatch):
    for cle, val in (("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig")), ("GIT_CONFIG_NOSYSTEM", "1"),
                     ("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"), ("GIT_COMMITTER_NAME", "t"),
                     ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(cle, val)
    monkeypatch.delenv("VLP_CANAL", raising=False)
    ecrire(str(tmp_path / "gitconfig"), "")
    d = str(tmp_path / "d")
    ecrire(os.path.join(d, "a.txt"), "a\n")
    init_git(d)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "départ")
    for fiche in ("W1", "W12", "W2"):
        for cote in ("apres", "avant"):
            git(d, "worktree", "add", "--detach", str(tmp_path / ("vlp-relecture-%s-%s-x" % (fiche, cote))), "HEAD")
    monkeypatch.chdir(d)
    assert appel(["relecture", "W1", "--retirer"]) == (0, "RETIRÉ 2\n")
    assert copies(d) == ["vlp-relecture-W12-apres-x", "vlp-relecture-W12-avant-x",
                         "vlp-relecture-W2-apres-x", "vlp-relecture-W2-avant-x"]
