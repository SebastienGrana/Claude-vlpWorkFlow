"""Les aides communes de la suite pytest (REF4) : le code de `vlp.py` chargé par chemin, comme
l'ancienne suite maison le charge, et les petits bâtisseurs que les tests migrés partagent.

Le chargement se fait une fois par processus ; un test qui change l'état du module (`mod.etat.GIT`…) passe par
`monkeypatch.setattr`, qui le remet à la fin du test.
"""
import datetime
import importlib.util
import inspect
import io
import json
import os
import re
import subprocess
from typing import Any

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RACINE, "scripts")


def charger_coeur():
    """Charger `scripts/vlp_coeur.py` par son chemin (`spec_from_file_location`), puis le régler comme
    l'ancienne suite maison le règle : tampon des hooks coupé, page d'enchaînement du vrai kit jamais refaite."""
    spec = importlib.util.spec_from_file_location("vlp_coeur", os.path.join(SCRIPTS, "vlp_coeur.py"))
    assert spec and spec.loader
    module: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.etat.TAMPON_HOOKS = None
    module.etat.SOURCE_ORDRE = None
    return module


mod: Any = charger_coeur()


def porte_motif(fonction, motif, nom=None):
    """Dire si le test `fonction` porte `motif`, sans tenir compte de la casse : dans son nom (`nom`, l'id d'un test
    paramétré compris), son texte, ou celui des fonctions de son module qu'il nomme — un libellé écrit dans une aide
    retient le test qui l'appelle (VIT10, l'option `--seul` de `conftest.py`, REF59)."""
    try:
        source = inspect.getsource(fonction)
    except (OSError, TypeError):
        source = ""
    module = inspect.getmodule(fonction)
    aides = [inspect.getsource(g) for n, g in sorted(vars(module).items()) if inspect.isfunction(g)
             and g is not fonction and re.search(r"\b%s\b" % re.escape(n), source)] if module else []
    return motif.lower() in ((nom or fonction.__name__) + " " + source + "".join(aides)).lower()


def appel(argv):
    """Lancer `vlp.py <argv>` dans ce processus : rendre (code de sortie, sortie)."""
    s = io.StringIO()
    code = mod.main(argv, s)
    return code, s.getvalue()


def lire(chemin):
    """Lire un fichier comme le kit le lit."""
    return mod.lire(chemin)


def ecrire(chemin, texte):
    """Écrire `texte` tel quel, dossiers créés."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte)


def transcript(chemin, tours, heures=None):
    """Un jsonl de `tours` tours, 100 000 tokens d'entrée chacun, sur claude-opus-5 (5 $ le million) ;
    `heures` : celle de chaque tour, en secondes UTC — sans elles, aucun `timestamp`."""
    with open(chemin, "w", encoding="utf-8") as f:
        for n in range(tours):
            ligne: dict[str, Any] = {"type": "assistant", "requestId": "r%d" % n, "message": {
                "id": "m%d" % n, "model": "claude-opus-5", "content": [],
                "usage": {"input_tokens": 100000, "output_tokens": 0,
                          "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}}
            if heures:
                ligne["timestamp"] = datetime.datetime.fromtimestamp(
                    heures[n], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            f.write(json.dumps(ligne) + "\n")


def commits(depot, sujets, t0):
    """Poser des commits vides dans `depot` : `sujets` est une liste de (secondes après `t0`, message), la date
    d'auteur et de commiteur fixée à cette heure."""
    for d, sujet in sujets:
        date = "%d +0000" % (t0 + d)
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=depot, check=True,
                       capture_output=True, env=dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))


def ligne_close(c):
    """Une ligne close au format de cmd_clore, avec plage Q1–Q2, date 2026-05-06, et coût c."""
    return ('          <tr>\n            <td>Test <span class="badge" data-etat="clos">clos</span></td>\n'
            '            <td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>\n'
            '            <td class="mono">%s</td>\n            <td>Test</td>\n          </tr>\n' % c)
