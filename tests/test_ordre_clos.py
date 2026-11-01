"""`noyau/ordre.py` : `clore` marque le chantier clos dans la source d'enchaînement (REF35, défaut `E16`).

À la clôture de `GAI`, `clore` a sorti `GARDE: pas ISO (kit)` : `ISO` avait quitté la TODO, et sa ligne de la source ne
portait pas `✅`. Ces tests gardent l'écriture de `✅ clos le <date>` par `clore` lui-même.
"""
import os
import pathlib
import re
import tempfile

from aides import SCRIPTS, appel, ecrire, lire, mod

OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


def gabarit(nom):
    """Le texte du gabarit `nom` du kit (`templates/`)."""
    return pathlib.Path(os.path.join(SCRIPTS, "..", "templates", nom)).read_text(encoding="utf-8")


SOURCE = """## Les projets

| Clé | Dossier |
|---|---|
| k | `.` |
| p | `p` |

## La cible

| Projet | Codes |
|---|---|
| k | `U` |
| p | `U` |

## Le chemin conseillé

| Pas | Projet | Nom | Coût |
|---|---|---|---|
| `U` | k | | note du kit |
| `U` | p | u | juste après `K1` |
"""


def clore_avec_source(t, source_texte):
    """Clore le chantier `U` du projet `<t>/p`, la source d'enchaînement `<t>/kit/ctx/ordre.md` valant
    `source_texte` ; rend (code, sortie, texte de la source après)."""
    kit, projet = os.path.join(t, "kit"), os.path.join(t, "p")
    ecrire(os.path.join(kit, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n"
           "- **artefact enchaînement** : https://claude.ai/artifact/essai\n")
    ecrire(os.path.join(kit, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
           "|---|---|---|---|---|\n| 1 | `U` — homonyme du kit | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
    source = os.path.join(kit, "ctx", "ordre.md")
    ecrire(source, source_texte)
    ecrire(os.path.join(projet, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
           "Lettres de fiche déjà prises : A (test).\n")
    ecrire(os.path.join(projet, "ctx", "08-etat.md"), "# État\n")
    ecrire(os.path.join(projet, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
    ecrire(os.path.join(projet, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
    ecrire(os.path.join(projet, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
    avant = mod.etat.SOURCE_ORDRE
    try:
        mod.etat.SOURCE_ORDRE = source
        code, s = appel(["clore", projet, "--livre", "fini", "--date", "2026-10-13"])
    finally:
        mod.etat.SOURCE_ORDRE = avant
    return code, s, lire(source)


def test_clore_marque_ordre(tmp_path):
    """REF35 : `clore` écrit `✅ clos le <date>` dans la source, sur la ligne du chantier qu'il clôt — le pas du projet
    clos, pas celui d'un autre projet au même code —, avant de refaire la page : aucune `GARDE: pas`."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        code, s, apres = clore_avec_source(t, SOURCE)
    assert code == 0, ("REF35 : clore sort 0") + "\n" + s
    assert "| `U` | p | u | ✅ clos le 2026-10-13 |\n" in apres, ("REF35 : clore marque ✅ clos le <date> la ligne du "
                                                                  "projet clos") + "\n" + apres
    assert "| `U` | k | | note du kit |\n" in apres, ("REF35 : la ligne d'un autre projet au même code reste") + "\n" + apres
    assert "GARDE: pas" not in s, ("REF35 : aucune GARDE: pas") + "\n" + s
    assert "ORDRE marqué U ✅ clos le 2026-10-13" in s, ("REF35 : la ligne ORDRE marqué dit l'écriture") + "\n" + s
    assert "ORDRE envoyer" in s, ("REF35 : la page d'enchaînement refaite") + "\n" + s


def test_clore_ordre_deja_clos(tmp_path):
    """REF35 : une ligne déjà `✅` reste telle quelle — ni réécrite, ni ligne `ORDRE marqué`."""
    deja = SOURCE.replace("juste après `K1`", "✅ clos le 2026-10-01")
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        code, s, apres = clore_avec_source(t, deja)
    assert code == 0, ("REF35 : déjà ✅, clore sort 0") + "\n" + s
    assert apres == deja, ("REF35 : déjà ✅, la source intacte") + "\n" + apres
    assert "ORDRE marqué" not in s, ("REF35 : déjà ✅, pas de ligne ORDRE marqué") + "\n" + s


LIGNES = ["## Le chemin conseillé", "", "| Pas | Projet | Nom | Coût |", "|---|---|---|---|",
          "| `REF` | kit | | juste après `ISO` (2026-10-16) |", "| `ISO` | kit | x | ✅ clos le 2026-10-17 |",
          "| `C2` | md | |"]


def test_marquer_clos_ordre():
    """REF35 : `marquer_clos_ordre` en mémoire — la cellule « Coût » du pas `code` des projets `cles` devient
    `✅ clos le <date>`, les autres lignes intactes ; une cellule manquante est ajoutée."""
    neuves = mod.marquer_clos_ordre(LIGNES, {"kit"}, "REF", "2026-11-01") or []
    assert neuves[4:5] == ["| `REF` | kit | | ✅ clos le 2026-11-01 |"], ("REF35 : la ligne du pas marquée") + "\n" + str(neuves)
    assert neuves[:4] + neuves[5:] == LIGNES[:4] + LIGNES[5:], ("REF35 : seule la ligne du pas change") + "\n" + str(neuves)
    courte = mod.marquer_clos_ordre(LIGNES, {"md"}, "C2", "2026-11-01") or []
    assert courte[6:7] == ["| `C2` | md | | ✅ clos le 2026-11-01 |"], ("REF35 : une cellule manquante est ajoutée") + "\n" + str(courte)


def test_marquer_clos_ordre_rien():
    """REF35 : `marquer_clos_ordre` rend `None` — rien à écrire — pour un pas déjà `✅`, d'un autre projet, ou absent."""
    assert mod.marquer_clos_ordre(LIGNES, {"kit"}, "ISO", "2026-11-01") is None, "REF35 : déjà ✅ : None"
    assert mod.marquer_clos_ordre(LIGNES, {"autre"}, "REF", "2026-11-01") is None, "REF35 : autre projet : None"
    assert mod.marquer_clos_ordre(LIGNES, {"kit"}, "ABS", "2026-11-01") is None, "REF35 : pas absent : None"
