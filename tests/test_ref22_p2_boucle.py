"""REF22, l'angle des bugs, passe 2 : cinq défauts de `boucle.py` et de `carnet.py`, rejoués puis corrigés.

Un carnet dont une raison porte U+2028, une fiche qui cite le bloc **Tentatives** sans en porter un, des filles du
lanceur arrêtées sans leurs sessions `claude`, une borne de plan à virgule, un dossier absent. Aucun ne lit la machine
(`tmp_path`) ; aucun ne lance le vrai `claude`.
"""
import argparse
import contextlib
import io

import carnet
from aides_boucle import bmod


def test_ref22_p2_carnet_lit_une_raison_a_u2028(tmp_path):
    """REF22 : une raison qui porte U+2028 ou U+0085 reste une seule ligne du carnet — `lire` rend les trois lignes
    écrites, `stop_de` la raison, `pot` 1,75."""
    c = str(tmp_path / "2026-11-02.jsonl")
    carnet.ajouter(c, nuit="2026-11-02", canal="A", chantier="X", role="jouer", fiche="X1", usd_cli=1.25,
                   issue="jouée", session="s1")
    carnet.stop(c, "A", "limite opus   ligne 2")
    carnet.ajouter(c, nuit="2026-11-02", canal="A", chantier="X", role="relire", fiche="X1", usd_cli=0.5,
                   issue="jouée", session="s2", garde="motif \u0085 ici")
    lignes = carnet.lire(c)
    vu = (len(lignes), carnet.stop_de(lignes) is not None, carnet.pot(lignes))
    assert vu == (3, True, 1.75), "REF22 carnet.lire : %r lignes lues, stop vu, pot — attendu (3, True, 1.75)" % (vu,)


class _Joue(Exception):
    """La fiche est jouée : `jouer` remplacé lève ceci."""


def test_ref22_p2_tentatives_cite_en_milieu_de_ligne(monkeypatch, tmp_path):
    """REF22 : une fiche qui cite « **Tentatives** » au milieu d'une ligne ne porte aucun bloc (`tentatives()` ne lit
    qu'un début de ligne) : elle est jouée, la boucle ne s'arrête pas sur « porte un bloc Tentatives »."""
    extrait = ("## F1 [ ] — titre\n\nLe bloc **Tentatives** se lit en tête de ligne.\n\n"
               "**Critère de fin** : x\n")
    monkeypatch.setattr(bmod, "lire_carte", lambda racine: (racine, "fiches.md", "F1", None))
    monkeypatch.setattr(bmod, "vlp", lambda argv, dossier: (0, extrait))

    def jouer(*_x, **_k):
        raise _Joue

    monkeypatch.setattr(bmod, "jouer", jouer)
    a = argparse.Namespace(plafond=1, nuit=False, plugin_retard=None)
    etat = {"jouees": 0, "tours": 0, "cout": 0.0, "verifiee": False}
    try:
        rendu = bmod.fiches_du_chantier("claude", a, str(tmp_path), "fiches.md", str(tmp_path), None, etat)
    except _Joue:
        rendu = "jouée"
    assert rendu == "jouée", "REF22 fiches_du_chantier : %r — attendu la fiche jouée" % (rendu,)


class _FauxKit:
    """Note les processus dont l'arbre est tué."""

    def __init__(self):
        self.tues = []

    def tuer_arbre(self, p):
        """Note `p`, ne rend rien."""
        self.tues.append(p.nom)


class _FausseFille:
    """Une fille `boucle.py` : `wait` se note ; ni `terminate` ni `kill` — l'arbre se tue par le kit."""

    def __init__(self, nom, attendues):
        self.nom, self.attendues = nom, attendues

    def wait(self, timeout=None):
        """Note l'attente, rend 1."""
        self.attendues.append(self.nom)
        return 1


def test_ref22_p2_ctrl_c_tue_l_arbre_des_filles():
    """REF22 : au Ctrl+C du lanceur, chaque fille est arrêtée par `tuer_arbre` du kit (ses sessions `claude` avec
    elle), puis attendue — jamais un `terminate()` qui laisse vivre les petits-enfants."""
    k, attendues = _FauxKit(), []
    filles = [_FausseFille("A", attendues), _FausseFille("B", attendues)]
    try:
        bmod.arreter_filles(filles, k)
        erreur = None
    except AttributeError as e:
        erreur = str(e)
    assert (erreur, k.tues, attendues) == (None, ["A", "B"], ["A", "B"]), \
        "REF22 arreter_filles : erreur %r, arbres tués %r, filles attendues %r" % (erreur, k.tues, attendues)


def test_ref22_p2_lire_plan_borne_a_virgule(monkeypatch):
    """REF22 : « BORNE 12,5 $ » (plan édité à la main) : `lire_plan` rend `(None, "borne illisible : 12,5")`, jamais
    un `ValueError` en traceback."""
    monkeypatch.setattr(bmod, "vlp", lambda argv, dossier: (
        0, "BORNE 12,5 $ · 2 chantiers\nCHANTIER REF · canal A · rang 1 · préfixe REF\n"))
    try:
        rendu = bmod.lire_plan("/x", argparse.Namespace(date="2026-11-02", canal="A"))
    except ValueError as e:
        rendu = "ValueError : %s" % e
    assert rendu == (None, "borne illisible : 12,5"), "REF22 lire_plan : %r" % (rendu,)


def test_ref22_p2_dossier_absent_est_une_garde(tmp_path):
    """REF22 : `boucle.py <dossier absent> --plafond 1` sort 1 sur une `GARDE: dossier introuvable`, jamais un
    `FileNotFoundError` en traceback."""
    absent = str(tmp_path / "absent")
    sortie = io.StringIO()
    try:
        with contextlib.redirect_stdout(sortie):
            code = bmod.main([absent, "--plafond", "1", "--claude", str(tmp_path / "faux.py")])
    except OSError as e:
        code = "%s : %s" % (type(e).__name__, e)
    assert (code, "GARDE: dossier introuvable : %s" % absent in sortie.getvalue()) == (1, True), \
        "REF22 main : %r\n%s" % (code, sortie.getvalue())
