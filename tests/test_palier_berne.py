"""Un petit projet au `conftest.py` copié ne note plus la suite verte du kit dont il importe les aides (FIG2).

Vu le 2026-11-17 à 12:58 : un petit projet lancé en sous-processus, vert en « suite entière », écrivait
`vlp-suite-verte` du vrai kit (`noter_suite_verte(mod.etat.KIT)`) ; `palier_manquant` rendait alors None sur un code
qu'aucune vraie suite n'avait joué — le palier sauté de ROU2. Le kit visé est bâti ici, dans un dossier temporaire.
"""
import os
import shutil
import subprocess
import sys

from aides import mod
from noyau.palier import palier_manquant

TESTS = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(TESTS)

UN_TEST = "def test_vert():\n    assert True\n"


def batir_kit(dossier, init_git):
    """Bâtir dans `dossier` un kit visé : `scripts/` du kit, ses `tests/aides.py` et `tests/conftest.py`, sa marque
    `.claude-plugin/plugin.json`, en dépôt Git sans commit ; rendre le dossier."""
    shutil.copytree(os.path.join(KIT, "scripts"), dossier / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (dossier / "tests").mkdir()
    for nom in ("aides.py", "conftest.py"):
        shutil.copy(os.path.join(TESTS, nom), dossier / "tests" / nom)
    (dossier / ".claude-plugin").mkdir()
    (dossier / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
    init_git(dossier)
    return dossier


def jouer_petit_projet(projet, kit):
    """Lancer en sous-processus, en suite entière, un petit projet d'un test vert au `conftest.py` copié du kit `kit`,
    ses aides importables, **sans** `GIT_DIR` ; rendre (code de sortie, sortie entière)."""
    projet.mkdir()
    shutil.copy(kit / "tests" / "conftest.py", projet / "conftest.py")
    (projet / "pytest.ini").write_text("[pytest]\ntestpaths = .\n", encoding="utf-8")
    (projet / "test_un.py").write_text(UN_TEST, encoding="utf-8")
    env = {k: v for k, v in os.environ.items()
           if k not in ("VLP_TOUS_ECARTS", "VLP_PONT", "GIT_DIR") and not k.startswith("PYTEST_XDIST_")}
    env.update(VLP_COUVERTURE="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=os.pathsep.join([str(kit / "tests"), str(kit / "scripts")]))
    fini = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "--rootdir", str(projet)],
                          cwd=projet, env=env, capture_output=True, timeout=300, check=False)
    return fini.returncode, (fini.stdout + fini.stderr).decode("utf-8", errors="replace")


def lire_suite_verte(kit):
    """Le texte de `vlp-suite-verte` du kit `kit`, ou None s'il n'existe pas."""
    chemin = mod.chemin_suite_verte(str(kit))
    try:
        with open(chemin or "", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def test_un_petit_projet_ne_note_pas_la_suite_verte_du_kit(tmp_path, init_git):
    kit = batir_kit(tmp_path / "kit", init_git)
    mod.noter_suite_verte(str(kit), mod.empreinte_kit(str(kit)))   # la dernière vraie suite entière
    neuf = kit / "scripts" / "neuf.py"
    neuf.write_text("X = 1\n", encoding="utf-8")                    # le code change depuis
    avant = lire_suite_verte(kit)
    assert avant, "la dernière vraie suite du kit visé n'est pas notée"
    assert palier_manquant(str(neuf)), "le kit visé ne réclame pas son palier avant le petit projet"
    code, sortie = jouer_petit_projet(tmp_path / "projet", kit)
    assert code == 0, "petit projet rouge (code %d) :\n%s" % (code, sortie)
    apres, manque = lire_suite_verte(kit), palier_manquant(str(neuf))
    detail = "(%r → %r), palier_manquant : %r\n%s" % (avant, apres, manque, sortie)
    assert apres == avant, "la suite verte du kit visé écrite par un petit projet " + detail
    assert manque is not None, "palier_manquant à None après un petit projet " + detail
