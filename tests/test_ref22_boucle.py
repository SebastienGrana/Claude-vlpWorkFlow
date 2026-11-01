"""REF22, l'angle des bugs : six défauts de la boucle de nuit et de `mesure-tokens.py`, rejoués puis corrigés.

Chaque test rejoue un défaut relevé par REF22 — arbre de processus laissé vivant au délai (vérification de nuit, session
de jeu), coût d'une session coupée sans ses sous-agents, carte gardée lue comme « aucune fiche », arbre sale embarqué par
la branche suivante d'une reprise, sha en chiffres lu comme une date. Aucun ne lit la machine : `conftest.py` isole `~`
et Git ; aucun ne lance le vrai `claude`.
"""
import argparse
import datetime
import importlib.util
import os
import subprocess
import sys
import time

import aides_boucle
import boucle_noyau.session as session
import carnet
import faux_claude
from aides import SCRIPTS
from aides_boucle import aides_du_canal, bmod, carnet_de

_spec = importlib.util.spec_from_file_location("mesure_tokens_ref22", os.path.join(SCRIPTS, "mesure-tokens.py"))
assert _spec and _spec.loader
mt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mt)

SID = "00000000-0000-4000-8000-0000000ref22"


def test_ref22_verifier_nuit_tue_l_arbre_au_delai(monkeypatch, tmp_path):
    """REF22 (1) : la commande de nuit lance (par le shell) un petit-enfant qui écrit après 2,5 s, puis dort ; au délai
    d'une seconde, l'arbre entier est tué — le rendu ne l'attend pas, et il n'écrit jamais."""
    monkeypatch.setattr(session, "TIMEOUT_S", 1)
    marque = tmp_path / "marque.txt"
    commande = '"%s" -c "import time; time.sleep(2.5); open(r\'%s\', \'w\').write(\'x\'); time.sleep(1.5)"' % (
        sys.executable, marque)
    t0 = time.time()
    raison = session.verifier_nuit(commande, str(tmp_path))
    duree = time.time() - t0
    time.sleep(max(0.0, 4 - (time.time() - t0)))
    assert (raison, duree < 2.5, marque.exists()) == ("dépasse le délai de 1 s", True, False), \
        "REF22 verifier_nuit : rendu %r après %.1f s (attendu le délai en moins de 2,5 s), petit-enfant vivant : %s" % (
            raison, duree, marque.exists())


FAUX_QUI_ESSAIME = """import os, subprocess, sys, time
subprocess.Popen([sys.executable, "-c", "import sys, time; time.sleep(2.5); open(sys.argv[1], 'w').write('x')",
                  os.environ["REF22_MARQUE"]], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL)
time.sleep(30)
"""


def test_ref22_jouer_tue_les_enfants_de_claude_au_delai(monkeypatch, tmp_path):
    """REF22 (2) : un faux `claude` lance un enfant qui écrit après 2,5 s, puis dort ; au délai d'une seconde, `jouer`
    tue l'arbre — l'enfant n'écrit jamais."""
    t = str(tmp_path / "projet")
    os.makedirs(t)
    aides_boucle.depot(t)
    faux = tmp_path / "faux_essaime.py"
    faux.write_text(FAUX_QUI_ESSAIME, encoding="utf-8")
    marque = tmp_path / "marque.txt"
    monkeypatch.setenv("REF22_MARQUE", str(marque))
    monkeypatch.setitem(session.ROLES["jouer"], "timeout", 1)
    a = argparse.Namespace(nuit=True, canal="A", chantier="X", carnet=carnet_de(t), permission_mode="auto",
                           model=None, effort=None, budget=None)
    t0 = time.time()
    s = bmod.jouer(str(faux), "F1", t, a, str(tmp_path / "trace.jsonl"))
    time.sleep(max(0.0, 4 - (time.time() - t0)))
    assert (s["issue"], marque.exists()) == ("timeout", False), \
        "REF22 jouer : issue %s, l'enfant de claude a écrit après le délai : %s" % (s["issue"], marque.exists())


def test_ref22_mesure_kit_compte_les_sous_agents(monkeypatch, tmp_path):
    """REF22 (3) : une session coupée qui a un sous-agent, au même coût qu'elle : `mesure_kit` compte les deux, comme
    `mesure_session_kit` du rapport."""
    monkeypatch.chdir(tmp_path)
    faux_claude.transcription(SID, "claude-opus-5-5")
    principal, _ = mt.resoudre(SID)
    assert principal
    seul, _ = mt.mesurer(principal)
    assert seul is not None, "REF22 mesure_kit : transcription du faux illisible"
    sous = os.path.join(os.path.splitext(principal)[0], "subagents", "agent-a.jsonl")
    os.makedirs(os.path.dirname(sous))
    with open(principal, encoding="utf-8") as h, open(sous, "w", encoding="utf-8", newline="") as s:
        s.write(h.read())
    usd, tours, garde = session.mesure_kit(SID)
    attendu = float(2 * seul["usd_exact"])
    assert (usd, tours, garde) == (attendu, 2 * seul["tours"], None), \
        "REF22 mesure_kit : (%r, %r, %r), attendu (%r, %d, None) — le sous-agent compte" % (
            usd, tours, garde, attendu, 2 * seul["tours"])


def test_ref22_carte_gardee_arrete_en_erreur(tmp_path):
    """REF22 (4) : `COURANT=fiches.md`, puis une `GARDE:` sans `PROCHAINE=` (aucun titre de fiche) : la boucle sort 1
    sur la garde, jamais « aucune fiche à jouer » en sortie 0 ; `lire_carte` lève `CarteGardee`."""
    t = str(tmp_path / "projet")
    os.makedirs(t)
    faux = aides_boucle.projet(t)
    with open(os.path.join(t, "fiches.md"), "w", encoding="utf-8", newline="") as h:
        h.write("# Chantier F — fiches\n\n**Ouvert.** le 2026-10-08.\n\n## Le socle commun\n\nRien.\n")
    code, sortie, _ = aides_boucle.boucle(t, faux, 3)
    try:
        lue = bmod.lire_carte(t)
    except bmod.CarteGardee as e:
        lue = "CarteGardee : %s" % e
    vu = (code, "aucune fiche à jouer" in sortie, "GARDE: aucun titre" in sortie,
          str(lue).startswith("CarteGardee : GARDE: aucun titre"))
    assert vu == (1, False, True, True), \
        "REF22 carte gardée : code %d, lire_carte → %r\n%s" % (code, lue, sortie)


def test_ref22_reprise_arbre_sale_avant_brancher(monkeypatch, tmp_path):
    """REF22 (5) : sous `--reprendre`, AAA est de côté sans son WIP (coupé entre la ligne du carnet et le commit) : l'arbre
    est sale ; CCC ne se branche pas dessus — le canal s'arrête, `un_chantier` n'est pas appelé."""
    aides = aides_du_canal()
    t, hors = str(tmp_path / "depot_canal"), str(tmp_path / "hors")
    os.makedirs(t)
    os.makedirs(hors)
    aides["depot_canal"](t, hors, ["AAA", "CCC"])
    base = aides["sha"](t, "HEAD")
    with open(os.path.join(t, "wip.txt"), "w", encoding="utf-8") as h:
        h.write("le travail d'AAA, jamais commité\n")
    a = argparse.Namespace(carnet=carnet.du_jour(t, aides["DATE"]), canal="A", date=aides["DATE"], plafond=None,
                           borne_usd=5.0, borne_chantiers=3, chantier=None, plugin_retard=None)
    appels = []
    monkeypatch.setattr(bmod, "un_chantier", lambda *x, **k: appels.append(x[5]) or ("clos", 0, None))
    reprise = {"base": base, "faits": {"AAA": "de-cote"}, "en_cours": None, "coupe": False, "coupees": 0}
    etat = {"jouees": 0, "tours": 0, "cout": 0.0, "verifiee": False}
    code, raison = bmod.boucle_canal("claude", a, t, hors, etat, ["AAA", "CCC"], None, None, reprise)
    assert (code, appels, "CCC" in raison, aides["branches"](t)) == (1, [], True, []), \
        "REF22 reprise : code %d, raison %r, chantiers joués %r, branches %r" % (code, raison, appels,
                                                                                aides["branches"](t))


def test_ref22_borne_sha_en_chiffres_est_un_commit(monkeypatch, tmp_path):
    """REF22 (6) : `20251001` nomme un commit (une étiquette ici, un sha abrégé en vrai) : `borne` rend son heure de
    commit, pas le 1er octobre 2025 ; `2025-10-01` reste une date."""
    git = ["git", "-c", "commit.gpgsign=false"]
    subprocess.run(git + ["init", "-q"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "x"], cwd=tmp_path, capture_output=True, check=True,
                   env=dict(os.environ, GIT_AUTHOR_DATE="1700000000 +0000", GIT_COMMITTER_DATE="1700000000 +0000"))
    subprocess.run(git + ["tag", "20251001"], cwd=tmp_path, capture_output=True, check=True)
    monkeypatch.chdir(tmp_path)
    chiffres, date = mt.borne("20251001"), mt.borne("2025-10-01")
    assert (chiffres, date) == ((1700000000, None), (datetime.datetime(2025, 10, 1).timestamp(), None)), \
        "REF22 borne : 20251001 → %r, 2025-10-01 → %r" % (chiffres, date)
