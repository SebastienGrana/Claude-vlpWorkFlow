"""REF6 : trois vraies sorties de `vlp.py` — `carte`, `valider --plan`, `cout` — photographiées par syrupy (tests
de caractérisation, D2), dans un projet temporaire. Le chemin du test et la racine du kit sont filtrés (`propre`) :
la photo ne garde que ce qui doit rester stable. Photo dans `__snapshots__/test_photos_essai.ambr` ; un changement
voulu se reprend par `uv run pytest --snapshot-update`. syrupy gardé contre pytest-regtest : l'essai est dans
`context AI/122-qualite-code-tests.md`, section « L'outil de photographie (`REF6`) ».
"""
import os
import re

import pytest

from aides import RACINE, appel, commits, ecrire, transcript

FICHES = """# Chantier Z

**Ouvert.** le 2026-10-08.

## Le socle commun

Un socle.

## L'ordre des fiches

<!-- FICHE:Z1 -->
## Z1 [x] — faite

**Dépend de** : rien.
**Session** : %s
**Critère de fin**
vu.
<!-- /FICHE -->
<!-- FICHE:Z2 -->
## Z2 [ ] — à faire

**Dépend de** : `Z1`.
**Critère de fin** (visuel)
regarder.
<!-- /FICHE -->
"""


@pytest.fixture
def projet(tmp_path, depot, monkeypatch):
    """Un projet équipé dans un dépôt : `CHANTIER.md`, un fichier de fiches à deux fiches, une session de trois
    tours ; le dossier courant y est posé, comme une commande lancée depuis sa racine."""
    session = tmp_path / "s.jsonl"
    transcript(str(session), 3, [1790000000 + d for d in (10, 20, 30)])
    ecrire(str(depot / "CHANTIER.md"), "# Chantier courant\n\n- **alias** : p\n- **contexte** : ctx/\n")
    ecrire(str(depot / "ctx" / "z.md"), FICHES % session)
    commits(str(depot), [(5, "Chantier Z ouvert : cadré")], 1790000000)
    monkeypatch.chdir(depot)
    return depot


def propre(code, sortie, tmp_path):
    """Le code de sortie et la sortie, le dossier du test en `<TMP>` et la racine du kit en `<KIT>`, barres
    obliques — la photo ne dépend ni de la machine ni du lancement."""
    for avant, apres in ((str(tmp_path), "<TMP>"), (RACINE, "<KIT>")):
        sortie = sortie.replace(avant, apres).replace(avant.replace("\\", "/"), apres)
    sortie = re.sub(r"<(TMP|KIT)>[^\s]*", lambda m: m.group(0).replace("\\", "/"), sortie)
    return "code %d\n%s" % (code, sortie)


SORTIES = {
    "carte": lambda: appel(["carte"]),
    "valider": lambda: appel(["valider", os.path.join("ctx", "z.md"), "--plan"]),
    "cout": lambda: appel(["cout", os.path.join("ctx", "z.md")]),
}


@pytest.mark.parametrize("nom", list(SORTIES))
@pytest.mark.usefixtures("projet")
def test_photo(nom, tmp_path, snapshot):
    """La sortie de `nom`, filtrée, égale à sa photo."""
    assert propre(*SORTIES[nom](), tmp_path) == snapshot
