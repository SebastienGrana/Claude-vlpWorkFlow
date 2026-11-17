"""PEN1 : `pas_ordre` prend la rangée de TODO dont le code **est** celui du pas (`codes_todo` : le premier texte
entre accents graves de la cellule Chantier), pas une rangée qui le **cite** — vu sur Cairn à la clôture de `CLR`
(2026-10-14), où un titre « en retard de `MEN` et `CLR` » passait pour la rangée de `MEN`."""
from aides import mod

O = mod.noyau.ordre

CITE = ("1", "`AAA` — en retard de `BBB`", "touche x", "~2 fiches", "—")
VRAIE = ("2", "`BBB` — Le vrai chantier", "touche y", "~1 fiche", "—")


def test_pen1_pas_ordre_prend_la_rangee_du_code_pas_celle_qui_le_cite():
    """PEN1 : la rangée `AAA` cite `BBB` dans son titre, la rangée `BBB` existe → le pas `BBB` est la rangée n° 2,
    origine `todo`, sans garde (avant : deux rangées le portaient, une `GARDE:`)."""
    pas, origine, garde = O.pas_ordre("BBB", "kit", [CITE, VRAIE], "nom de la source", "~3 fiches")
    assert garde is None
    assert origine == "todo"
    assert pas["numero"] == "2"


def test_pen1_pas_ordre_retombe_sur_la_source_sans_sa_rangee():
    """PEN1 : sans rangée `BBB`, le pas retombe sur la source (origine `source`, nom et coût de la source), pas sur
    la rangée `AAA` qui le cite."""
    pas, origine, garde = O.pas_ordre("BBB", "kit", [CITE], "nom de la source", "~3 fiches")
    assert garde is None
    assert origine == "source"
    assert pas["numero"] is None
    assert pas["nom"] == "nom de la source"
