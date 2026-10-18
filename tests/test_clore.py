"""Les décisions de `noyau/clore.py` qui ne lancent pas `git` (REF48 ; `methode-chantier.md`, « Coder dans le kit » :
la décision se teste sans Git) — chacune reçoit le texte qu'un `git` aurait rendu."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import clore


def test_blocs_worktrees_principal_en_tete():
    texte = "\n".join(["worktree /d/kit", "HEAD abc", "branch refs/heads/main", "",
                       "worktree /t/arbre", "HEAD def", "detached", ""])
    assert clore.blocs_worktrees(texte) == [("/d/kit", "main"), ("/t/arbre", None)]
    assert clore.blocs_worktrees("") == []


def test_textes_du_lot_blob_absent_et_arbre():
    sortie = (b"abc blob 10\nun\r\ndeux\r\n\n"    # un blob : 10 octets, puis son LF
              b"HEAD:x missing\n"                  # absent : rien à sauter
              b"def tree 3\nxyz\n")                # pas un blob
    assert clore.textes_du_lot(sortie, 3) == ["un\ndeux\n", None, None]


def test_prefixes_joues():
    assert clore.prefixes_joues("REF45 : un\nFusion : W2\nW2 : deux\nREF46 : trois\nautre\n") == ["REF", "W"]
    assert clore.prefixes_joues("") == []
