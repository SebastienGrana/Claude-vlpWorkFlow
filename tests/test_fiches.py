"""Les décisions de `noyau/fiches.py` qui ne lancent pas `git` (REF45 ; `methode-chantier.md`, « Coder dans le kit » :
la décision se teste sans Git) — chacune reçoit le texte qu'un `git` aurait rendu. Le branchement sur un vrai dépôt
reste gardé par les groupes `cocher` et `commiter` de `scripts/test-vlp.py`."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import fiches

FICHES = ["# Fiches", "",
          "## W1 [ ] — Une fiche", "", "**Fichiers** : `src/a.py`, `docs/`, `src/*.txt`.", "",
          "## W2 [ ] — La suivante", "", "**Fichiers** : `src/b.py`."]


def test_tete_de_fiche_nomme_le_commit_du_sous_agent():
    assert fiches.tete_de_fiche("W1", "abc123 W1 : Une fiche\n") == "TÊTE abc123 W1 : Une fiche\n"


def test_tete_de_fiche_laisse_un_autre_commit():
    assert fiches.tete_de_fiche("W1", "abc123 W12 : une autre") is None
    assert fiches.tete_de_fiche("W1", "abc123 Fusion : W1") is None
    assert fiches.tete_de_fiche("W1", "") is None   # git log muet : rien à dire


def test_chemins_du_statut_suivis_non_suivis_et_renommes():
    texte = " M src/a.py\0?? docs/neuf.md\0R  nouveau.py\0ancien.py\0A  un nom à espace.txt\0"
    assert fiches.chemins_du_statut(texte) == ["src/a.py", "docs/neuf.md", "nouveau.py", "un nom à espace.txt"]


def test_chemins_du_statut_vide():
    assert fiches.chemins_du_statut("") == []


def test_partage_commit_ses_fichiers_et_les_communs():
    avant = ["src/a.py", "src/b.py", "docs/guide.md", "src/notes.txt", "autre.py"]
    apres = avant + ["fiches.md"]
    ajout, hors = fiches.partage_commit(FICHES, "W1", {"fiches.md"}, avant, apres)
    assert ajout == ["src/a.py", "docs/guide.md", "src/notes.txt", "fiches.md"]
    assert hors == ["src/b.py", "autre.py"]   # le fichier d'une autre fiche, et un inconnu
