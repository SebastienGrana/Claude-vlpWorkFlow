"""Les décisions de `noyau/matin.py` qui ne lancent pas `git` (REF49 ; `methode-chantier.md`, « Coder dans le kit » :
la décision se teste sans Git). Le branchement sur de vrais dépôts reste gardé par `tests/test_matin.py`."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import matin


def test_pointes_du_texte():
    texte = "refs/heads/nuit/2026-10-18-A 1792300000\nrefs/heads/nuit/2026-10-18-B pas-un-nombre\n\n"
    assert matin.pointes_du_texte(texte) == [("nuit/2026-10-18-A", 1792300000)]


def test_choisir_nuit_la_seule():
    etats = [("nuit/2026-10-17-A", "deja"), ("nuit/2026-10-18-A", "fusion"), ("nuit/2026-10-18-B", "fusion")]
    assert matin.choisir_nuit(etats) == ("2026-10-18", "NUIT 2026-10-18 — la seule à ranger : 2 branche(s)\n")


def test_choisir_nuit_plusieurs_ou_aucune():
    deux = [("nuit/2026-10-18-A", "fusion"), ("nuit/2026-10-17-A", "fusion")]
    assert matin.choisir_nuit(deux) == (
        None, "GARDE: plusieurs nuits à ranger : 2026-10-17 (1), 2026-10-18 (1) — rien fusionné ; donne la date\n")
    assert matin.choisir_nuit([("nuit/2026-10-18-A", "cote")]) == (
        None, "GARDE: aucune nuit à ranger (1 branche(s) nuit/* déjà fusionnée(s) ou de côté) — rien fusionné\n")
