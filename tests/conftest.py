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
def depot(depots):
    """Une copie du dépôt modèle, à ce test seul."""
    return depots("depot")
