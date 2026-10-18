"""La décision de `heures_commits` (`noyau/page.py`), sans Git (REF46 ; `methode-chantier.md`, « Coder dans le kit ») :
`heures_du_log` reçoit le texte de `git log --format="%at %s"`. Le branchement sur un vrai dépôt reste gardé par
`tests/test_heures_commits.py`."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import page

LOG = "\n".join([   # le plus récent d'abord, comme `git log`
    "500 Fusion : W2",
    "400 W2 : La suivante",
    "300 W1 : Une fiche",
    "250 W1 : case cochée",
    "200 Chantier W ouvert",
    "100 Autre chose",
])


def test_le_commit_au_titre_et_l_etape_d_avant():
    pourquoi = []
    r = page.heures_du_log(LOG, ["W1", "W2"], pourquoi, titres={"W1": "Une fiche", "W2": "La suivante"})
    # 250 (`W1 : case cochée`) est une étape d'avant le commit au titre : hors des bornes ; `Fusion : W2` va aux autres.
    assert r == ({"W1": 300, "W2": 400}, [200, 300, 400], [100, 500], [])
    assert pourquoi == []


def test_sans_commit_de_fiche_un_chantier_en_cours():
    assert page.heures_du_log("200 Chantier W ouvert\n100 Autre", ["W1"], []) == ({}, [200], [100], [])


def test_sans_commit_qui_nomme_le_prefixe():
    pourquoi = []
    assert page.heures_du_log("100 Autre chose", ["W1"], pourquoi) is None
    assert pourquoi == ["aucun commit qui nomme W"]


def test_un_chantier_clos_sans_commit_de_fiche():
    pourquoi = []
    assert page.heures_du_log("200 Chantier W ouvert", ["W1"], pourquoi, clos=True) is None
    assert pourquoi == ["chantier clos sans commit « W1 : » ni d'une autre fiche"]
