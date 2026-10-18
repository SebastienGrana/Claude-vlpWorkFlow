"""Les décisions de `noyau/relecture.py` qui ne lancent pas `git` (REF47 ; `methode-chantier.md`, « Coder dans le
kit » : la décision se teste sans Git) — chacune reçoit le texte qu'un `git` aurait rendu."""
import os

import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import relecture


def test_relectures_de_garde_le_prefixe():
    liste = "\n".join(["worktree /d/kit", "HEAD abc", "", "worktree /t/vlp-relecture-W1-x", "detached", "",
                       "worktree /t/vlp-relecture-W2-y", "", "worktree /t/autre"])
    assert relecture.relectures_de(liste, "vlp-relecture-W1-") == ["/t/vlp-relecture-W1-x"]
    assert relecture.relectures_de(liste, "vlp-relecture-") == ["/t/vlp-relecture-W1-x", "/t/vlp-relecture-W2-y"]
    assert relecture.relectures_de("", "vlp-relecture-") == []


def test_chemins_a_suivre_sans_le_cache_de_python():
    assert relecture.chemins_a_suivre("ctx/a.md\nctx/__pycache__/\n\nCLAUDE.md\n") == ["ctx/a.md", "CLAUDE.md"]


def test_meme_depot_ailleurs(tmp_path):
    commun, kit, arbre = (os.path.join(str(tmp_path), n) for n in ("depot/.git", "depot", "arbre"))
    assert relecture.meme_depot_ailleurs("%s\n%s\n" % (commun, kit), "%s\n%s\n" % (commun, arbre))
    assert not relecture.meme_depot_ailleurs("%s\n%s\n" % (commun, kit), "%s\n%s\n" % (commun, kit))   # même dossier
    assert not relecture.meme_depot_ailleurs("%s\n%s\n" % (commun, kit), "%s/autre/.git\n%s\n" % (tmp_path, arbre))
    assert not relecture.meme_depot_ailleurs("", "%s\n%s\n" % (commun, arbre))   # git muet
