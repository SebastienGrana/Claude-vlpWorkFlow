"""PEN2 : sans `--todo`, `feuille` pose le badge « en cours » sur la rangée dont le **code** (`codes_todo`) est celui du
chantier ouvert (`lettre_de` de sa première fiche), pas sur le **numéro** relu dans la page : la TODO de Cairn
numérote par rang, et une renumérotation faisait passer le badge sur un autre chantier."""
import os

from aides import appel, ecrire, lire, mod
from test_fusion import (CARTE_MATIN, GABARIT_FEUILLE, commit_matin, depot_matin, git_matin, ouvert_ligne)

TETE = "# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"


def badges(page):
    """(rang qui porte le badge, nombre de badges) dans la `ZONE:todo` de la feuille `page` ; `(None, 0)` sans badge."""
    html = lire(page)
    d, f, forme = mod.zone_todo(html)
    return mod.rang_en_cours(html[d:f], forme), html[d:f].count(mod.BADGE_COURS)


def test_pen2_feuille_sans_todo_suit_le_code_pas_le_numero(tmp_path):
    """PEN2 : `QQQ` ouvert, badge posé au rang 3 ; la TODO renumérotée met `QQQ` au n° 2 et `RRR` au n° 3 →
    `feuille` sans `--todo` pose le badge sur le rang 2, une seule fois (avant : sur le 3, le numéro relu)."""
    d = str(tmp_path / "p")
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n")
    ecrire(os.path.join(d, "ctx", "30-qqq.md"), ouvert_ligne("# Chantier QQQ — Q\n\n## QQQ1 [ ] — a\n## QQQ2 [ ] — b\n"))
    etat = os.path.join(d, "ctx", "08-etat.md")
    page = os.path.join(d, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(page, lire(GABARIT_FEUILLE))
    ecrire(etat, TETE + "| 2 | `PPP` — p | a | 1 fiche | — |\n| 3 | `QQQ` — q | b | 2 fiches | — |\n\n## Journal\n")
    code, s = appel(["feuille", d, "--todo", "3", "--date", "2026-11-18"])
    assert code == 0, s
    assert badges(page) == ("3", 1), s
    ecrire(etat, TETE + "| 2 | `QQQ` — q | b | 2 fiches | — |\n| 3 | `RRR` — r | c | 1 fiche | — |\n\n## Journal\n")
    code, s = appel(["feuille", d, "--date", "2026-11-18"])
    assert code == 0, s
    assert badges(page) == ("2", 1), s


def test_pen2_fusion_qui_renumerote_garde_le_badge_sur_le_code(tmp_path, init_git):
    """PEN2 : `main` à `LOC` ouvert, badge au n° 79 ; une branche renumérote la TODO (`PAR` au 79, `LOC` au 80) →
    après `fusionner`, le badge est sur le 80, la rangée de `LOC` (avant : le 79 relu avant la fusion, `PAR`).
    Sans Git, `init_git` saute le test (`conftest.py`)."""
    d = str(tmp_path / "f")
    depot_matin(init_git, d)
    page = os.path.join(d, "ctx", "artefacts", "feuille-de-route.html")
    assert badges(page) == ("79", 1)
    git_matin(d, "switch", "-q", "-c", "renum", "main")
    ecrire(os.path.join(d, "ctx", "08-etat.md"),
           TETE + "| 79 | `PAR` — deux chantiers | b | 3 fiches | — |\n| 80 | `LOC` — publier | a | 2 fiches | — |\n\n"
           "## Journal\n")
    commit_matin(d, "LOC1 : renuméroter", 1)
    git_matin(d, "switch", "-q", "main")
    code, s = appel(["fusionner", d, "renum"])
    assert code == 0, s
    assert s == "FUSIONNÉE renum\n", s
    assert badges(page) == ("80", 1), s
