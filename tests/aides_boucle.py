"""Les aides des tests de la boucle de nuit (`test_boucle.py`, `test_boucle_canal.py`) : `boucle.py` lancé avec le
faux `claude` de `tests/faux_claude.py`, aucun appel modèle (REF52, ex-`scripts/` à tiret).

Le faux joue un rôle par prompt (découper, jouer, clore, relire) et rend les lignes `stream-json` de NUI1 ; ses
pilotes `VLP_FAUX_*` sont dans sa docstring. `verifier` porte le libellé de chaque cas en tête de son message d'échec ;
`conftest.py` isole chaque test (`~`, Git, variables de la nuit — ENV1, NUI8).
"""
import argparse
import contextlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Any

import carnet
import faux_claude
from aides import SCRIPTS, mod

FAUX_CLAUDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faux_claude.py")
FICHE = faux_claude.FICHE   # un seul gabarit de fiche


def projet(t, visuel=None, tentatives=None):
    corps = "# Chantier F — fiches\n\n**Ouvert.** le 2026-10-08.\n\n## Le socle commun\n\nRien.\n\n## L'ordre des fiches\n\nF1, F2, F3.\n\n---\n\n"
    for f in ("F1", "F2", "F3"):
        bloc = FICHE % (f, f, f, " (visuel)" if f == visuel else "")
        if f == tentatives:
            bloc = bloc.replace("**Prompt**", "**Tentatives** (2026-09-26) — non résolu.\n1. RETOUR.\n\n**Prompt**")
        corps += bloc
    with open(os.path.join(t, "fiches.md"), "w", encoding="utf-8", newline="") as h:
        h.write(corps)
    with open(os.path.join(t, "CHANTIER.md"), "w", encoding="utf-8", newline="") as h:
        h.write("# Chantier courant\n\n- **contexte** : .\n")      # fiches.md, ouvert par sa marque (NUI31)
    return FAUX_CLAUDE


def boucle(t, faux, plafond, rate="", options=(), **pilotes):
    env = dict(os.environ, VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), VLP_FAUX_RATE=rate,
               PYTHONIOENCODING="utf-8", **pilotes)
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "boucle.py"), t, "--plafond", str(plafond),
                        "--claude", faux, "--traces", t] + list(options), env=env, capture_output=True, text=True, encoding="utf-8")
    with open(os.path.join(t, "fiches.md"), encoding="utf-8") as h:
        texte = h.read()
    cases = "".join("x" if ("## %s [x]" % f) in texte else "." for f in ("F1", "F2", "F3"))
    return r.returncode, r.stdout + r.stderr, cases


_PASSES = [0]   # cas passés : `verifier` sort au premier écart, donc ceux qui l'ont passé sont ceux qui sont écrits —
                # ceux de ce processus : une partie lancée à part (VIT22) ne compte que les siens


def verifier(nom, cond, sortie):
    """Le libellé `nom` en tête du message d'échec, que `conftest.py` reprend dans sa ligne `ÉCART:` ; la sortie
    après. Un cas passé se compte (`_PASSES`)."""
    assert cond, "%s\n%s" % (nom, sortie)
    _PASSES[0] += 1


# --- le faux lui-même : un rôle par prompt, un pilote par variable (NUI2) -------------

def faux(args, cwd, **env):
    base = {k: v for k, v in os.environ.items() if not k.startswith("VLP_FAUX_")}
    base.update(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), PYTHONIOENCODING="utf-8")
    base.update(env)
    r = subprocess.run([sys.executable, FAUX_CLAUDE] + args, cwd=cwd, env=base, capture_output=True,
                       text=True, encoding="utf-8")
    return r.returncode, [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")], r.stderr


def lire(chemin):
    with open(chemin, encoding="utf-8") as h:
        return h.read()


def verdict_de(lignes):
    return next((str(x.get("result")) for x in lignes if x["type"] == "result"), "")


# --- le carnet de nuit et la borne double (NUI3) --------------------------------------

# Git sans le poste (NUI5) : config globale et système neutralisées, une identité d'essai — comme `tests/conftest.py`.
_GIT_TMP = tempfile.TemporaryDirectory()
with open(os.path.join(_GIT_TMP.name, "gitconfig"), "w", encoding="utf-8") as _h:
    _h.write("")
ENV_GIT = dict(GIT_CONFIG_GLOBAL=os.path.join(_GIT_TMP.name, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def git(t, *args):
    r = subprocess.run(["git"] + list(args), cwd=t, env=dict(os.environ, **ENV_GIT), check=True,
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def depot(t):
    """`git init` dans `t`, le projet de test, puis un commit initial : le carnet vit dans son `.git`,
    et la boucle de nuit commite sur ACCEPTÉE."""
    subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
    faux_ = projet(t)
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "init")
    return faux_


# La date des nuits sans --date, lue une fois : une suite qui passe minuit cherchait le carnet du lendemain, la boucle
# ayant écrit celui de la veille (NUI4 (e) rouge le 2026-10-16 à 00:03). `nuit()` la passe donc à boucle.py.
JOUR = time.strftime("%Y-%m-%d")


def carnet_de(t):
    chemin = carnet.du_jour(t, JOUR)
    assert chemin, "pas de carnet : %s n'est pas un dépôt Git" % t
    return chemin


def cases_de(t):
    texte = lire(os.path.join(t, "fiches.md"))
    return "".join("x" if ("## %s [x]" % f) in texte else "." for f in ("F1", "F2", "F3"))


def nuit(t, *options, rate="", claude=FAUX_CLAUDE, traces=None, **env):
    """boucle.py --nuit dans `t` : (code, sortie). VLP_CARNET et VLP_CANAL d'ici ne passent pas. Les traces
    vont hors du dépôt (`traces`, sinon un dossier jeté) : la boucle commite tout ce qu'elle y trouverait. Sans
    --date ni --reprendre (qui la refuse), la date `JOUR`, celle de `carnet_de`."""
    if "--date" not in options and "--reprendre" not in options:
        options += ("--date", JOUR)
    base = {k: v for k, v in os.environ.items() if k not in (carnet.ENV_CARNET, carnet.ENV_CANAL)}
    base.update(ENV_GIT)
    base.update(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), VLP_FAUX_RATE=rate, PYTHONIOENCODING="utf-8")
    base.update(env)
    with tempfile.TemporaryDirectory() as jete:
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "boucle.py"), t, "--claude", claude, "--traces",
                            traces or jete, "--nuit"] + list(options), env=base, capture_output=True, text=True,
                           encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


# --- les plafonds de chaque rôle, l'issue de chaque session, la limite d'usage (NUI4) -----

_spec_b = importlib.util.spec_from_file_location("boucle", os.path.join(SCRIPTS, "boucle.py"))
assert _spec_b and _spec_b.loader
bmod: Any = importlib.util.module_from_spec(_spec_b)   # `jouer()` y est appelé tel quel, un rôle à la fois
_spec_b.loader.exec_module(bmod)
kit = mod   # le code de vlp.py : source indépendante des `maxTurns` attendus
OPUS, SONNET, REPLI = "claude-opus-5-5", "claude-sonnet-5-5", "claude-opus-5,claude-sonnet-5-5"


def tours_de(agent):
    return kit.lire_max_turns(os.path.join(SCRIPTS, os.pardir, "agents", agent))


@contextlib.contextmanager
def pilote(**pilotes):
    """Pose des variables d'environnement le temps d'un bloc : `jouer()` les passe au faux."""
    avant = {k: os.environ.get(k) for k in pilotes}
    os.environ.update(pilotes)
    try:
        yield
    finally:
        for k, v in avant.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def drapeau(argv, nom):
    return argv[argv.index(nom) + 1] if nom in argv else None


def lancer(t, role="relire", controle=None, fiche="F1", **pilotes):
    """`jouer()` du module chargé, sous --nuit, dans le dépôt de test `t` : (rendu, lignes de session, arguments)."""
    journal = os.path.join(t, "argv.jsonl")
    ns = argparse.Namespace(nuit=True, canal="A", chantier="X", carnet=carnet_de(t), permission_mode="auto",
                            model=None, effort=None, budget=None)
    with pilote(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), VLP_FAUX_ARGV=journal, **pilotes):
        s = bmod.jouer(FAUX_CLAUDE, fiche, t, ns, os.path.join(t, "%s.jsonl" % role), role=role, controle=controle)
    sessions = [d for d in carnet.lire(carnet_de(t)) if carnet.est_session(d)]
    argvs = [json.loads(ligne) for ligne in lire(journal).splitlines()] if os.path.exists(journal) else []
    return s, sessions, argvs


# --- relire avant le commit (NUI5) : dépôt avec un commit initial, traces et journaux hors du dépôt -----

def journal_de(chemin):
    return [json.loads(l) for l in lire(chemin).splitlines()] if os.path.exists(chemin) else []


def autorises(argv):
    """Les `--allowedTools` d'une ligne de commande : ce qui suit le drapeau, jusqu'au drapeau suivant."""
    if "--allowedTools" not in argv:
        return []
    suite = argv[argv.index("--allowedTools") + 1:]
    return suite[:next((i for i, x in enumerate(suite) if x.startswith("--")), len(suite))]


# --- enchaîner les chantiers d'un canal (NUI7) -----------------------------------------------------------

# La date des nuits de NUI7 — et de NUI25, NUI8 et NUI9, qui reprennent les aides d'un canal.
DATE_CANAL = "2026-10-01"


def ecrire_f(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as h:
        h.write(texte)


def depot_canal(t, hors, codes, **reglages):
    """Un dépôt Git équipé, tout commité : CHANTIER.md sans chantier ouvert, la TODO (AAA, BBB qui dépend de AAA,
    CCC) et, si `codes`, le plan du soir `DATE_CANAL` du canal A — et du canal B pour `codes_b`, NUI9 — écrit par
    `vlp.py plan ecrire`. `hors` : plan et hooks. `reglages` : `couts` (trois, « ~2 fiches » chacun),
    `borne_chantiers` (3), `codes_b` (aucun) — par nom, hors des seuils de ruff (VIT22)."""
    assert set(reglages) <= {"couts", "borne_chantiers", "codes_b"}, reglages
    couts = reglages.get("couts", ("~2 fiches",) * 3)
    borne_chantiers, codes_b = reglages.get("borne_chantiers", 3), reglages.get("codes_b", ())
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
    ecrire_f(os.path.join(t, "CHANTIER.md"),
             "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **artefact du chantier** : aucun\n\n"
             "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")
    ecrire_f(os.path.join(t, "ctx", "00-INDEX.md"),
             "# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
             "| `100-x.md` | un chantier |\n\nFin.\n")
    ecrire_f(os.path.join(t, "ctx", "08-etat.md"),
             "# État\n\n" + entete + "| 1 | `AAA` — a | x | %s | — |\n| 2 | `BBB` — b | x | %s | `AAA` |\n"
             "| 3 | `CCC` — c | x | %s | — |\n\n## Journal\n" % couts)
    ecrire_f(os.path.join(t, "ctx", "100-x.md"), "# x\n")
    if codes:
        plan = {"borne_usd": 5, "borne_chantiers": borne_chantiers,
                "A": [{"code": c, "prefixe": c, "reponses": []} for c in codes]}
        if codes_b:
            plan["B"] = [{"code": c, "prefixe": c, "reponses": []} for c in codes_b]
        ecrire_f(os.path.join(hors, "plan.json"), json.dumps(plan))
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "vlp.py"), "plan", "ecrire", t, "--json",
                            os.path.join(hors, "plan.json"), "--date", DATE_CANAL], capture_output=True, text=True,
                           encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        assert r.returncode == 0, r.stdout + r.stderr
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "plan")


def carnet_du(t):
    chemin = carnet.du_jour(t, DATE_CANAL)
    assert chemin, "pas de carnet : %s n'est pas un dépôt Git" % t
    return carnet.lire(chemin)


def canal(t, hors, *options, **env):
    """boucle.py --nuit --canal A --date DATE_CANAL dans `t` : (code, sortie, lignes du carnet de DATE_CANAL). Le faux clôt
    par un commit, comme `cloture.md:72` ; ce qu'il a vu de l'environnement va dans `hors/env.jsonl`."""
    env.setdefault("VLP_FAUX_CLORE", "commit")
    env.setdefault("VLP_FAUX_ENV", os.path.join(hors, "env.jsonl"))
    code, s = nuit(t, "--canal", "A", "--date", DATE_CANAL, *options, traces=hors, **env)
    return code, s, carnet_du(t)


def br(code):
    return "nuit/%s-A-%s" % (DATE_CANAL, code)


def sha(t, ref):
    return git(t, "rev-parse", ref).strip()


def sujet(t, ref):
    return git(t, "log", "-1", "--format=%s", ref).strip()


def ancetre(t, x, y):
    return subprocess.run(["git", "merge-base", "--is-ancestor", x, y], cwd=t, env=dict(os.environ, **ENV_GIT),
                          capture_output=True).returncode == 0


def branches(t):
    return git(t, "branch", "--list", "nuit/*", "--format=%(refname:short)").split()


def roles(lignes, code):
    """Les rôles des sessions du chantier `code`, dans l'ordre du carnet."""
    return [d["role"] for d in lignes if d["chantier"] == code and carnet.est_session(d)]


def gardes(lignes, code):
    """Les gardes des lignes du chantier `code` qui ne sont pas des sessions (sans `role`)."""
    return [d["garde"] for d in lignes if d["chantier"] == code and d["role"] is None and d["note"] is None]


def aides_du_canal() -> dict[str, Any]:
    """Rendre les aides des cas d'un canal — dépôt équipé, canal lancé, carnet du jour, branches —, que NUI7, NUI25,
    NUI8 et NUI9 reprennent, sans jouer un seul cas : chaque partie les bâtit dans son processus (VIT22)."""
    return dict(DATE=DATE_CANAL, ecrire_f=ecrire_f, depot_canal=depot_canal, carnet_du=carnet_du, canal=canal,
                br=br, sha=sha, sujet=sujet, ancetre=ancetre, branches=branches, roles=roles, gardes=gardes)
