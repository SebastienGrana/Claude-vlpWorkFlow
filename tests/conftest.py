"""L'isolation de chaque test (REF4, D3) : rien de la machine ne se lit ni ne s'écrit.

- `isoler` (autouse) : `HOME` **et** `USERPROFILE` (Windows ne lit que celui-ci) sur un dossier du test, une
  config Git globale vide, celle du système ignorée, un auteur Git fixe, `TZ` et `LANG` fixés ; ni la session
  qui lance la suite (`CLAUDE_CODE_SESSION_ID`), ni les variables de la nuit (`VARIABLES_NUIT`, ENV1).
- `depot_modele` (session) : un dépôt Git vide, créé une fois ; `depot` en donne une copie à chaque test.
"""
import os
import shutil
import subprocess

import pytest
from aides import mod

AUTEUR = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


@pytest.fixture(autouse=True)
def isoler(tmp_path, monkeypatch):
    """Poser, pour ce test seul, un dossier personnel et une config Git à lui ; rendre le dossier personnel."""
    maison = tmp_path / "maison"
    maison.mkdir()
    gitconfig = tmp_path / "gitconfig"
    gitconfig.write_text("", encoding="utf-8")
    for nom in ("HOME", "USERPROFILE"):
        monkeypatch.setenv(nom, str(maison))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(gitconfig))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for nom, valeur in AUTEUR.items():
        monkeypatch.setenv(nom, valeur)
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LANG", "C.UTF-8")
    for nom in ("CLAUDE_CODE_SESSION_ID", "GIT_AUTHOR_DATE", "GIT_COMMITTER_DATE", *mod.carnet.VARIABLES_NUIT):
        monkeypatch.delenv(nom, raising=False)
    return maison


@pytest.fixture(scope="session")
def depot_modele(tmp_path_factory):
    """Un dépôt Git vide, branche `main`, créé une fois pour toute la session — sous une config à lui : la
    fixture de session passe avant `isoler`."""
    if shutil.which("git") is None:
        pytest.skip("git absent : le dépôt modèle ne se bâtit pas")
    racine = tmp_path_factory.mktemp("modele")
    gitconfig = racine / "gitconfig"
    gitconfig.write_text("", encoding="utf-8")
    depot = racine / "depot"
    depot.mkdir()
    env = dict(os.environ, GIT_CONFIG_GLOBAL=str(gitconfig), GIT_CONFIG_NOSYSTEM="1", **AUTEUR)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=depot, env=env, check=True, capture_output=True)
    return depot


@pytest.fixture
def depots(tmp_path, depot_modele):
    """Une fabrique : `depots("nom")` rend une copie neuve du dépôt modèle sous le dossier du test
    (`shutil.copytree`) — aucun `git init` de plus."""
    def copier(nom):
        copie = tmp_path / nom
        shutil.copytree(depot_modele, copie)
        return copie
    return copier


@pytest.fixture
def init_git(depot_modele):
    """`init_git(d)` fait de `d` un dépôt Git vide sur `main` — le `.git` du dépôt modèle copié dedans, `d` créé au
    besoin, son contenu gardé ; la place d'un `git init` dans un test migré (REF58)."""
    def poser(d):
        shutil.copytree(os.path.join(depot_modele, ".git"), os.path.join(d, ".git"))
    return poser


@pytest.fixture
def depot(depots):
    """Une copie du dépôt modèle, à ce test seul."""
    return depots("depot")


# --- La suite entière, sans l'ancienne suite maison (REF59, choix Q1 : A et Q2 : A de l'utilisateur) -------------------------
# Ce que l'ancienne suite maison faisait autour de ses tests : `--seul <motif>` (VIT10), une ligne `ÉCART: <libellé>`
# par test rouge puis `OK` ou `FIN: <n> écart(s)` en dernière ligne (ce que lit `vlp.py mutant`), la suite verte que
# `cocher` exige (VIT11), la relance sous `coverage` (REF8). Sous `pytest-xdist`, le contrôleur seul en a la charge.


def pytest_addoption(parser):
    parser.addoption("--seul", default=None, metavar="MOTIF",
                     help="ne jouer que les tests dont le nom ou le texte (aides du module comprises) porte MOTIF, "
                          "sans tenir compte de la casse ; aucun : sort 1 (VIT10)")


def controleur(config):
    """Vrai hors d'un processus de `pytest-xdist` : le contrôleur, ou une session sans `-n`."""
    return not hasattr(config, "workerinput")


def suite_entiere(config):
    """Vrai si cette session joue toute la suite, sur le vrai code : aucun chemin nommé, ni `--seul`, ni `-k`, ni
    `-m`, ni le mutant (`VLP_TOUS_ECARTS=1`, une copie mutée)."""
    return (config.args_source == pytest.Config.ArgsSource.TESTPATHS and not config.getoption("seul")
            and not config.getoption("keyword") and not config.getoption("markexpr")
            and os.environ.get("VLP_TOUS_ECARTS") != "1")


def pytest_configure(config):
    """La suite entière se relance sous `coverage` (`couverture.mesurer`), puis sort de son code : la mesure réunit
    les processus de `-n` (REF8, vérifié le 2026-10-18 : même couverture en série et sous `-n 4`). Déjà mesurée, ou
    sans `uv` : elle tourne telle quelle, et note son empreinte de départ pour la suite verte (VIT11)."""
    config.vlp_ecarts = []
    config.vlp_aucun = False
    if not (controleur(config) and suite_entiere(config)):
        return
    import couverture
    if couverture.a_mesurer(False):
        code = couverture.mesurer(mod.etat.KIT, "-m", ["pytest", *config.invocation_params.args],
                                  mod.empreinte_kit(mod.etat.KIT))
        if code is not None:
            pytest.exit("suite jouée sous coverage, ci-dessus", returncode=code)
    config.vlp_empreinte = mod.empreinte_kit(mod.etat.KIT)


def pytest_collection_modifyitems(config, items):
    """`--seul` : ne garder que les tests qui portent le motif (`aides.porte_motif`) ; aucun ne le porte : le dire, et
    la session sortira 1 — un motif mal tapé ne passe pas pour une suite verte (VIT10)."""
    motif = config.getoption("seul")
    if not motif:
        return
    from aides import porte_motif
    gardes = [i for i in items if porte_motif(getattr(i, "function", None) or (lambda: None), motif, i.name)]
    config.hook.pytest_deselected(items=[i for i in items if i not in gardes])
    items[:] = gardes
    if not gardes:
        config.vlp_aucun = True
        print("GARDE: aucun groupe ne porte « %s »" % motif)


def pytest_runtest_logreport(report):
    """Un test rouge : une ligne `ÉCART: <libellé>`, la première de son message d'erreur — le libellé que porte son
    `assert` (REF5) — sitôt connu, pour que `vlp.py mutant --attendu` s'arrête dessus."""
    if report.failed:
        crash = getattr(report.longrepr, "reprcrash", None)
        message = (getattr(crash, "message", "") or str(report.longrepr)).split("\n")[0]
        libelle = message.split(": ", 1)[1] if message.startswith("AssertionError: ") else message
        ECARTS.append(libelle)
        print("\nÉCART: %s — %s" % (libelle, report.nodeid), flush=True)


ECARTS = []     # les écarts de la session du contrôleur, dans l'ordre


def pytest_sessionfinish(session, exitstatus):
    """Sur le contrôleur : `--seul` sans test → sort 1 ; la suite entière verte → son empreinte de départ notée,
    celle que `cocher` retrouve (VIT11)."""
    config = session.config
    if not controleur(config):
        return
    if config.vlp_aucun:
        session.exitstatus = 1
    elif exitstatus == 0 and suite_entiere(config) and hasattr(config, "vlp_empreinte"):
        mod.noter_suite_verte(mod.etat.KIT, config.vlp_empreinte)
    config.vlp_fin = session.exitstatus


def pytest_unconfigure(config):
    """La dernière ligne de la sortie, après le résumé de pytest : `OK` si tout est vert, `FIN: <n> écart(s)` si des
    tests sont rouges — la suite est allée au bout (`vlp.py mutant` ne la dit pas PLANTÉ) ; rien sinon."""
    fin = getattr(config, "vlp_fin", None)
    if not controleur(config) or fin is None:
        return
    if fin == 0:
        print("OK")
    elif fin == 1 and ECARTS:
        print("FIN: %d écart(s)" % len(ECARTS))
