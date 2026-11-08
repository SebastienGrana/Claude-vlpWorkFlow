"""ALG5 : la page se régénère à la clôture, plus à chaque fiche ; elle lit les lignes `**Constaté**` que `vlp.py fin`
écrit dans les fiches (ALG4), comme les notes de `--note`. Chaque test bâtit ses fichiers dans un dossier temporaire."""
import os
import tempfile

from aides import appel, ecrire, lire

FICHES = """# Chantier P

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [x] — Créer `a.py`
**Constaté** : test_a vert, 3 lignes
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P2 -->
## P2 [x] — Brancher
**Constaté** : branché, vu dans la sortie
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P3 -->
## P3 [ ] — Finir
**Critère de fin**
<!-- /FICHE -->
"""


def test_la_page_lit_les_lignes_constate():
    with tempfile.TemporaryDirectory() as t:
        fiches = os.path.join(t, "p.md")
        page = os.path.join(t, "artefacts", "p.html")
        ecrire(fiches, FICHES)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R",
                         "--note", "P2", "la note donnée"])
        html = lire(page) if os.path.exists(page) else ""
        assert code == 0, "page : créée\n" + s
        assert '<span class="note">test_a vert, 3 lignes</span>' in html, "page : la ligne Constaté devient la note"
        assert '<span class="note">la note donnée</span>' in html, "page : une note donnée passe avant Constaté"


def test_niveau_dit_la_page_en_retard_sans_la_compter():
    """Un chantier ouvert : sa page en retard se dit `RETARD: page:`, non comptée ; une page introuvable reste un écart."""
    import io

    import noyau.niveau
    s = io.StringIO()
    n = noyau.niveau.compter_page(["ÉCART: P1 faite dans le fichier, pas sur la page", "GARDE: page introuvable : x"], s)
    assert n == 1, "niveau : seule la page introuvable compte\n" + s.getvalue()
    assert "RETARD: page: P1 faite" in s.getvalue(), "niveau : le retard se dit\n" + s.getvalue()
    assert "ÉCART: page: page introuvable" in s.getvalue(), "niveau : l'introuvable reste un écart\n" + s.getvalue()
