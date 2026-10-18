"""La décision d'`ouverture` (`noyau/hooks.py`), sans Git (REF47) : `heure_d_ajout` reçoit le code et le texte de
`git log --diff-filter=A --format=%at`."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import hooks

SANS = "aucun commit n'ajoute ce fichier : l'ouverture n'est pas commitée"


def test_heure_d_ajout_le_plus_ancien():
    assert hooks.heure_d_ajout(0, "300\n200\n100\n") == (100, None)


def test_heure_d_ajout_sans_commit_ou_en_echec():
    assert hooks.heure_d_ajout(0, "") == (None, SANS)
    assert hooks.heure_d_ajout(128, "100\n") == (None, SANS)
