"""Défaut d'ALG3, réparé le 2026-11-08 (choix B de l'utilisateur) : dans le kit, `clore` écrit `CHANTIER.md` et
`CLAUDE.md` après la suite de clôture, et rendait périmé le rapport de couverture qu'il venait d'exiger — le
`pre-push` refusait, une seconde suite (650 s) était due. `clore` re-note l'empreinte après ses propres écritures,
seulement si le rapport était à jour juste avant ; une retouche à la main le rend toujours périmé."""
import io
import os
import subprocess
import tempfile

import couverture
import noyau.clore
from aides import ecrire, mod


def kit(d):
    """Faire de `d` un faux kit (plugin et suite) dans un dépôt Git, avec `CHANTIER.md` et `CLAUDE.md` ; rend `d`."""
    for chemin, texte in ((".claude-plugin/plugin.json", "{}"), ("tests/conftest.py", ""), ("CHANTIER.md", "carte\n"),
                          ("CLAUDE.md", "routage\n"), ("scripts/x.py", "x = 1\n")):
        ecrire(os.path.join(d, *chemin.split("/")), texte)
    subprocess.run(["git", "init", "-q"], cwd=d, check=True, capture_output=True)
    return d


def noter_rapport(d, empreinte):
    """Poser un rapport de couverture mesuré sur `empreinte`, et la suite verte sur la même."""
    _, rapport, note = couverture.chemins(d)
    ecrire(rapport, "<coverage/>\n")
    ecrire(note, empreinte + "\n")
    mod.noter_suite_verte(d, empreinte)


def ecritures_de_clore(d):
    """Ce que `clore` écrit hors de `context AI/` : `CHANTIER.md` et `CLAUDE.md`."""
    ecrire(os.path.join(d, "CHANTIER.md"), "carte, chantier clos\n")
    ecrire(os.path.join(d, "CLAUDE.md"), "routage, clos le 2026-11-08\n")


def test_un_rapport_a_jour_le_reste_apres_clore():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        avant = mod.empreinte_kit(d)
        noter_rapport(d, avant)
        ecritures_de_clore(d)
        assert not couverture.rapport_a_jour(d, mod.empreinte_kit(d)), "témoin : les écritures de clore le périment"
        noyau.clore.renoter_apres_clore(d, avant)
        assert couverture.rapport_a_jour(d, mod.empreinte_kit(d)), "clore : un rapport à jour avant le reste après"
        assert mod.suite_manquante(os.path.join(d, "CHANTIER.md")) is None, "clore : la suite verte suit aussi"


def test_sans_avant_clore_lit_l_empreinte_du_rapport_et_le_dit():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        noter_rapport(d, mod.empreinte_kit(d))
        ecritures_de_clore(d)
        sortie = io.StringIO()
        noyau.clore.renoter_apres_clore(d, sortie=sortie)
        assert couverture.rapport_a_jour(d, mod.empreinte_kit(d)), "clore sans avant : l'empreinte notée sert d'avant"
        assert "COUVERTURE re-notée" in sortie.getvalue(), "clore : la re-note se dit sur la sortie"


def test_un_rapport_perime_avant_clore_n_est_pas_renote():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        avant = mod.empreinte_kit(d)
        noter_rapport(d, "une autre empreinte")
        ecritures_de_clore(d)
        noyau.clore.renoter_apres_clore(d, avant)
        assert not couverture.rapport_a_jour(d, mod.empreinte_kit(d)), "clore : un rapport périmé avant le reste"


def test_une_retouche_a_la_main_apres_clore_perime_le_rapport():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        avant = mod.empreinte_kit(d)
        noter_rapport(d, avant)
        ecritures_de_clore(d)
        noyau.clore.renoter_apres_clore(d, avant)
        ecrire(os.path.join(d, "CHANTIER.md"), "carte, chantier clos, puis retouchée à la main\n")
        assert not couverture.rapport_a_jour(d, mod.empreinte_kit(d)), "une retouche à la main périme le rapport"


def test_hors_du_kit_rien_n_est_renote():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        os.remove(os.path.join(d, ".claude-plugin", "plugin.json"))
        avant = mod.empreinte_kit(d)
        noter_rapport(d, avant)
        ecritures_de_clore(d)
        noyau.clore.renoter_apres_clore(d, avant)
        assert not couverture.rapport_a_jour(d, mod.empreinte_kit(d)), "hors du kit, clore ne touche à aucune note"
