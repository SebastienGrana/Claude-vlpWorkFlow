"""Dette de FIG (ABP) : une fiche cochée sans rien livrer — sa ligne « **Constaté** : abandonnée » — s'affiche
« Abandonnée » sur la page du chantier, pas « Faite » (FIG3, 2026-11-17). La couleur viendra du `vlp.css` de CON3."""
from aides import mod

P = mod.noyau.page
LIGNES = ["## A1 [x] — une", "", "**Constaté** : abandonnée, rien écrit — A0 a réparé au centre", "",
          "## A2 [x] — deux", "", "**Constaté** : 3 passed", "", "## A3 [ ] — trois", "", "**Dépend de** : `A1`."]


def test_page_fiche_abandonnee():
    """La ligne « **Constaté** : abandonnée » d'une fiche cochée donne l'état `abandonnee` ; une autre note, `faite`."""
    abandon = P.abandonnees(LIGNES)
    assert abandon == {"A1"}, "page : seule A1 porte « Constaté : abandonnée »"
    assert P.etats(P.fiches_du_fichier(LIGNES), {}, abandon) == {"A1": "abandonnee", "A2": "faite", "A3": "encours"}, (
        "page : une fiche cochée et abandonnée n'est pas faite")
