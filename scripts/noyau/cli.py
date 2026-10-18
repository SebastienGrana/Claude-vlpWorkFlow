"""La ligne de commande de `vlp.py` : les sous-parseurs, `main`, et chaque sous-commande vers sa fonction (REF49 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import argparse
import os
import sys
from collections.abc import Callable
from typing import Any

import carnet

from noyau import etat
from noyau.commun import (Absent, chemin_garde, cmd_archiver, lire, une_fois)
from noyau.fiches import (cmd_cocher, cmd_commiter, cmd_extraire, cmd_lire, cmd_socle, cmd_valider)
from noyau.carte import (cmd_carte)
from noyau.sessions import (cmd_compteur, cmd_cout, cmd_essai, cmd_sessions)
from noyau.page import (cmd_joints, cmd_lancables)
from noyau.notes import (cmd_abri, cmd_etat, cmd_page, cmd_renvois, page_du_fichier)
from noyau.feuille import (cmd_archive)
from noyau.clos import (
    cmd_lien,
    cmd_liens,
    cmd_prix,
    cmd_recompter,
    cmd_recompter_clos,
    cmd_repeindre,
    cmd_vigile,
    cmd_vigile_hook,
)
from noyau.relecture import (cmd_equiper, cmd_lignes, cmd_relecture)
from noyau.hooks import (REGLE, REGLES, cmd_contrat, cmd_filet, cmd_forme, cmd_gardien, cmd_hook)
from noyau.niveau import (cmd_attente, cmd_attente_hook, cmd_comparer, cmd_niveau)
from noyau.bac import (
    cmd_bac,
    cmd_claude,
    cmd_kit_essai,
    cmd_nuits_noter,
    cmd_servir,
    cmd_transcription,
)
from noyau.nuit import (CANAUX, GABARIT_CHOIX, cmd_chef_page, cmd_feuille, cmd_plan, cmd_trier)
from noyau.clore import (cmd_clore, cmd_oter, cmd_ouverts, cmd_postit)
from noyau.ouvrir import (cmd_ouvrir, cmd_pause, nombre_fiches)
from noyau.matin import (cmd_fusionner, cmd_matin)
from noyau.rapport import (
    cmd_apercu,
    cmd_mutant,
    cmd_nuits_lecon,
    cmd_rapide,
    cmd_sante,
    cmd_symboles,
)
from noyau.ordre import (cmd_ordre)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). `RENVOIS`,
# `lire_arguments`, `page_gardee` et `fichier_garde`, posés par REF49 à la place de la chaîne de tests sur `a.cmd`, se lisent ici seulement.
__all__ = [
    "options_outils", "options_clore", "options_marques", "options_fusionner", "options_etat", "options_carte",
    "options_mesure", "options_mutant", "options_sante", "main", "PAR_ARGUMENTS", "repartir",
]


def options_outils(sous):
    """Déclarer les lignes de commande des outils : `bac`, `claude`, `kit-essai`, `symboles`, `rapide`, `lancables`,
    `commiter`, `ordre`."""
    la = sous.add_parser("lancables")
    la.add_argument("fichier")
    la.add_argument("--max", type=int, default=2)
    la.add_argument("--tourne", nargs="*", default=[])
    cm = sous.add_parser("commiter")
    cm.add_argument("fichier")
    cm.add_argument("fiche")
    bc = sous.add_parser("bac")
    bc.add_argument("dossier")
    sous.add_parser("claude")
    ke = sous.add_parser("kit-essai")
    ke.add_argument("dossier")
    ke.add_argument("--max-turns", type=int, required=True)
    ke.add_argument("--kit")
    sy = sous.add_parser("symboles")
    sy.add_argument("fichier")
    sy.add_argument("noms", nargs="*")
    od = sous.add_parser("ordre")
    od.add_argument("--json", action="store_true")
    od.add_argument("--db", action="store_true")
    od.add_argument("--source")
    ra = sous.add_parser("rapide")
    ra.add_argument("motif")
    ra.add_argument("--racine")


def options_clore(sous):
    """Déclarer la ligne de commande de `clore` et d'`oter`, les deux qui ôtent un chantier de la TODO (TAB4)."""
    cl = sous.add_parser("clore")
    cl.add_argument("projet")
    cl.add_argument("--livre", required=True)
    cl.add_argument("--tokens", type=int)
    cl.add_argument("--abandon")
    cl.add_argument("--fait")
    cl.add_argument("--surpris")
    cl.add_argument("--resume")
    cl.add_argument("--date")
    ot = sous.add_parser("oter")
    ot.add_argument("projet")
    ot.add_argument("code")
    ot.add_argument("--raison", required=True)
    ot.add_argument("--date")
    ot.add_argument("--fait", action="store_true")


def options_marques(sous):
    """Déclarer la ligne de commande de `ouverts` et de `pause`, les lecteur et poseur des marques (NUI21, NUI30), et
    de `postit`, le poseur du post-it d'un worktree (ISO8)."""
    ou = sous.add_parser("ouverts")
    ou.add_argument("projet")
    ou.add_argument("--rev")
    po = sous.add_parser("postit")
    po.add_argument("dossier")
    po.add_argument("fichier")
    pa = sous.add_parser("pause")
    pa.add_argument("fichier")
    pa.add_argument("raison")
    pa.add_argument("--date")


def options_fusionner(sous):
    """Déclarer la ligne de commande de `fusionner` : la fusion du jour (NUI26), ou, avec `--worktree`, la branche
    d'une fiche (ISO4)."""
    fu = sous.add_parser("fusionner")
    fu.add_argument("projet")
    fu.add_argument("branche")
    fu.add_argument("--worktree")


def options_etat(sous):
    """Déclarer la ligne de commande de `etat` : le nom du fichier d'état, ou, avec `--texte`, un texte ajouté à sa
    fin (ISO5)."""
    et = sous.add_parser("etat")
    et.add_argument("contexte")
    et.add_argument("--texte")


def options_carte(sous):
    """Déclarer la ligne de commande de `carte`."""
    c = sous.add_parser("carte")
    c.add_argument("dossier", nargs="?", default=None)
    c.add_argument("--python")
    c.add_argument("--relais", action="store_true")
    c.add_argument("--relecteur", action="store_true")
    c.add_argument("--session-neuve", action="store_true")
    c.add_argument("--enchaine", action="store_true")


def options_mesure(sous):
    """Déclarer les lignes de commande de `cout`, de `compteur` et d'`essai`."""
    es = sous.add_parser("essai")
    es.add_argument("motif")
    es.add_argument("--session")
    co = sous.add_parser("cout")
    co.add_argument("fichier")
    co.add_argument("--session", action="store_true")
    co.add_argument("--a-clore", action="store_true")
    cm = sous.add_parser("compteur")
    cm.add_argument("fichier")
    cm.add_argument("fiches", nargs="*")
    cm.add_argument("--recoupe", action="store_true")


def options_mutant(sous):
    """Déclarer la ligne de commande de `mutant`."""
    mu = sous.add_parser("mutant")
    mu.add_argument("cible")
    mu.add_argument("avant")
    mu.add_argument("apres")
    mu.add_argument("--test")
    quoi = mu.add_mutually_exclusive_group()
    quoi.add_argument("--attendu")
    quoi.add_argument("--tous", action="store_true")


def options_sante(sous):
    """Déclarer la ligne de commande de `sante` : `--base` ou `--cliquet`, `--forcer` et `--si-base` avec `--base`
    seulement."""
    sa = sous.add_parser("sante")
    sa.add_argument("fichiers", nargs="*")
    quoi = sa.add_mutually_exclusive_group()
    quoi.add_argument("--base", action="store_true")
    quoi.add_argument("--cliquet", action="store_true")
    sa.add_argument("--forcer", metavar="RAISON")
    sa.add_argument("--si-base", action="store_true")
    sa.add_argument("--racine")
    sa.add_argument("--sans-ruff", action="store_true")


def main(argv, sortie=None, entree=None, erreur=None):
    """Lire la ligne de commande, puis lancer la sous-commande demandée."""
    sortie = sortie or sys.stdout
    p = argparse.ArgumentParser(prog="vlp.py", description="La mécanique du kit vlp.")
    sous = p.add_subparsers(dest="cmd", required=True)
    options_carte(sous)
    e = sous.add_parser("extraire")
    e.add_argument("fichier")
    e.add_argument("fiche")
    s = sous.add_parser("socle")
    s.add_argument("fichier")
    se = sous.add_parser("sessions")
    se.add_argument("fichier")
    options_mesure(sous)
    li = sous.add_parser("lignes")
    li.add_argument("chemins", nargs="+")
    eq = sous.add_parser("equiper")
    eq.add_argument("dossier")
    eq.add_argument("--contexte", default="context AI")
    v = sous.add_parser("valider")
    v.add_argument("fichiers", nargs="+")
    v.add_argument("--plan", action="store_true")
    pg = sous.add_parser("page")
    pg.add_argument("fichier")
    pg.add_argument("page", nargs="?")
    pg.add_argument("--note", nargs=2, action="append", metavar=("FICHE", "TEXTE"))
    pg.add_argument("--journal", action="append")
    pg.add_argument("--creer", action="store_true")
    pg.add_argument("--projet")
    pg.add_argument("--titre")
    pg.add_argument("--resultat")
    pg.add_argument("--verifier", action="store_true")
    pg.add_argument("--forme", action="store_true")
    pg.add_argument("--date")
    sous.add_parser("hook")
    sous.add_parser("filet")
    options_etat(sous)
    rv = sous.add_parser("renvois")
    rv.add_argument("projet")
    nv = sous.add_parser("niveau")
    nv.add_argument("projet")
    nv.add_argument("--ecrire", action="store_true")
    nv.add_argument("--date")
    cp = sous.add_parser("comparer")
    cp.add_argument("ancienne")
    cp.add_argument("neuve")
    sous.add_parser("trier").add_argument("projet")
    fe = sous.add_parser("feuille")
    fe.add_argument("projet")
    fe.add_argument("--todo")
    fe.add_argument("--verifier", action="store_true")
    fe.add_argument("--date")
    options_clore(sous)
    sous.add_parser("archiver").add_argument("projet")
    ar = sous.add_parser("archive")
    ar.add_argument("projet")
    ar.add_argument("--url")
    sous.add_parser("abri").add_argument("pages", nargs="+")
    ou =sous.add_parser("ouvrir")
    ou.add_argument("projet")
    ou.add_argument("--fiches", required=True)
    ou.add_argument("--titre", required=True)
    ou.add_argument("--artefact")
    ou.add_argument("--estime-fiches", type=nombre_fiches)
    lr = sous.add_parser("lire")
    lr.add_argument("chemins", nargs="+")
    co2 = sous.add_parser("cocher")
    co2.add_argument("fichier")
    co2.add_argument("fiche")
    co2.add_argument("--resolu")
    co2.add_argument("--date")
    cv = co2.add_mutually_exclusive_group()
    cv.add_argument("--verifier", action="store_true")
    cv.add_argument("--refuser")
    cv.add_argument("--session")
    co2.add_argument("--role")
    rl = sous.add_parser("relecture")
    rl.add_argument("fiche", nargs="?")
    rl.add_argument("--sha")
    rl.add_argument("--retirer", action="store_true")
    ct = sous.add_parser("contrat")
    ct.add_argument("transcriptions", nargs="*")
    ct.add_argument("--depuis")
    ct.add_argument("--ouverture")
    fm = sous.add_parser("forme")
    fm.add_argument("transcriptions", nargs="*")
    fm.add_argument("--depuis")
    fm.add_argument("--regle", choices=REGLES, default=REGLE)
    sous.add_parser("gardien")
    vg = sous.add_parser("vigile")
    vg.add_argument("fichier", nargs="?", default=None)
    options_marques(sous)
    at = sous.add_parser("attente")
    ats = at.add_subparsers(dest="op", required=True)
    at_aj = ats.add_parser("ajouter")
    at_aj.add_argument("page")
    at_aj.add_argument("--url")
    at_aj.add_argument("--projet")
    ats.add_parser("lister").add_argument("dossier")
    at_re = ats.add_parser("retirer")
    at_re.add_argument("page")
    at_re.add_argument("--projet")
    ats.add_parser("hook")
    rp = sous.add_parser("repeindre")
    rp.add_argument("projet")
    rp.add_argument("--a-blanc", action="store_true")
    ln = sous.add_parser("lien")
    ln.add_argument("page")
    ln.add_argument("url")
    lns = sous.add_parser("liens")
    lns.add_argument("projet")
    rc =sous.add_parser("recompter")
    rc.add_argument("projet")
    for o in ("--ecrire", "--essais", "--a-clore"):
        rc.add_argument(o, action="store_true")
    rc.add_argument("--clos")
    px = sous.add_parser("prix")
    px.add_argument("projet")
    px.add_argument("--a-blanc", action="store_true")
    options_outils(sous)
    sous.add_parser("joints").add_argument("dossier")
    sv = sous.add_parser("servir")
    sv.add_argument("dossier")
    sv.add_argument("port", type=int)
    ap = sous.add_parser("apercu")
    ap.add_argument("projet")
    ap.add_argument("--port", type=int)
    options_mutant(sous)
    nu = sous.add_parser("nuits")
    nu.add_argument("verbe", choices=["noter", "lecon"])
    nu.add_argument("texte")
    nu.add_argument("--canal")
    nu.add_argument("--stop", action="store_true")
    nu.add_argument("--sorte", choices=carnet.SORTES)
    nu.add_argument("--projet", default=".")
    pl = sous.add_parser("plan")
    pl.add_argument("verbe", choices=["ecrire", "lire"])
    pl.add_argument("projet")
    pl.add_argument("--json")
    pl.add_argument("--date")
    pl.add_argument("--canal", choices=CANAUX)
    pl.add_argument("--chantier")
    options_fusionner(sous)
    ma = sous.add_parser("matin")
    ma.add_argument("projet")
    ma.add_argument("date", nargs="?")
    ma.add_argument("--rapport")
    ch = sous.add_parser("chef")
    ch.add_argument("verbe", choices=["page"])
    ch.add_argument("--questions", required=True)
    ch.add_argument("--sortie", required=True)
    tr = sous.add_parser("transcription")
    tr.add_argument("jsonl")
    options_sante(sous)
    a = lire_arguments(p, sous, argv)
    try:
        return repartir(a, sortie, entree, erreur)
    except Absent as e:
        sortie.write("GARDE: %s\n" % e)
        return 1


# Les sous-commandes qui ne demandent que leurs options et la sortie : `repartir` les lance d'une ligne.
PAR_ARGUMENTS = {
    "ouvrir": cmd_ouvrir, "clore": cmd_clore, "oter": cmd_oter, "archiver": cmd_archiver, "trier": cmd_trier, "feuille": cmd_feuille,
    "niveau": cmd_niveau, "comparer": cmd_comparer, "relecture": cmd_relecture, "contrat": cmd_contrat,
    "forme": cmd_forme, "ouverts": cmd_ouverts, "postit": cmd_postit, "pause": cmd_pause, "plan": cmd_plan, "matin": cmd_matin, "fusionner": cmd_fusionner,
    "sante": cmd_sante, "symboles": cmd_symboles, "compteur": cmd_compteur, "carte": cmd_carte,
    "rapide": cmd_rapide, "essai": cmd_essai, "lancables": cmd_lancables,
    "commiter": cmd_commiter, "ordre": cmd_ordre, "etat": cmd_etat,
}


def lire_arguments(p, sous, argv):
    """Poser sur chaque sous-commande sa fonction — `set_defaults(func=…)`, prise dans `RENVOIS` (REF49) —, puis lire
    `argv`."""
    for nom, sous_parseur in sous.choices.items():
        sous_parseur.set_defaults(func=RENVOIS[nom])
    return p.parse_args(argv)


def repartir(a, sortie, entree, erreur):
    """Le dispatch : la fonction que `set_defaults(func=…)` a posée sur la sous-commande (`RENVOIS`, REF49). Une
    `Absent` levée ici est gardée par `main`, et nulle part ailleurs : un chemin de `CHANTIER.md` ne fait plus tomber
    le script."""
    return a.func(a, sortie, entree, erreur)


def page_gardee(a, sortie):
    """`page` : son fichier de fiches gardé (`chemin_garde`), sa page par défaut tirée du fichier, puis `cmd_page`."""
    chemin_garde(a.fichier)
    if a.page is None:
        a.page = page_du_fichier(a.fichier)
    return cmd_page(a, sortie)


def fichier_garde(lancer):
    """`lancer(a, sortie)` derrière `chemin_garde(a.fichier)` : les sous-commandes qui lisent un fichier de fiches."""
    def garde(a, sortie, _entree, _erreur):
        """`chemin_garde`, puis `lancer`."""
        chemin_garde(a.fichier)
        return lancer(a, sortie)
    return garde


# Chaque sous-commande vers sa fonction `(a, sortie, entree, erreur)` ; `main` la pose par `set_defaults(func=…)`.
RENVOIS: dict[str, Callable[..., Any]] = {nom: (lambda f: lambda a, s, _e, _er: f(a, s))(f) for nom, f in PAR_ARGUMENTS.items()}
RENVOIS.update({
    "lire": lambda a, s, _e, _er: cmd_lire(a.chemins, s),
    "archive": lambda a, s, _e, _er: cmd_archive(a.projet, a.url, s),
    "abri": lambda a, s, _e, _er: cmd_abri(a.pages, s),
    "renvois": lambda a, s, _e, _er: cmd_renvois(a.projet, s),
    "hook": lambda _a, s, e, er: une_fois(e, cmd_hook, s, er or sys.stderr),
    "filet": lambda _a, s, e, er: une_fois(e, cmd_filet, s, er or sys.stderr),
    "page": lambda a, s, _e, _er: page_gardee(a, s),
    "valider": lambda a, s, _e, _er: cmd_valider(a.fichiers, s, a.plan),
    "equiper": lambda a, s, _e, _er: cmd_equiper(a.dossier, a.contexte, s),
    "lignes": lambda a, s, _e, _er: cmd_lignes(a.chemins, s),
    "gardien": lambda _a, s, e, _er: une_fois(e, cmd_gardien, s),
    "vigile": lambda a, s, e, _er: cmd_vigile(a.fichier, s) if a.fichier else une_fois(e, cmd_vigile_hook, s),
    "attente": lambda a, s, e, _er: une_fois(e, cmd_attente_hook, s) if a.op == "hook" else cmd_attente(a, s),
    "repeindre": lambda a, s, _e, _er: cmd_repeindre(a.projet, s, a.a_blanc),
    "lien": lambda a, s, _e, _er: cmd_lien(a.page, a.url, s),
    "liens": lambda a, s, _e, _er: cmd_liens(a.projet, s),
    "recompter": lambda a, s, _e, _er: (cmd_recompter_clos(a.projet, s, a.ecrire, a.clos) if a.clos
                                         else cmd_recompter(a.projet, s, a.ecrire, a.essais, a.a_clore)),
    "prix": lambda a, s, _e, _er: cmd_prix(a.projet, s, a.a_blanc),
    "bac": lambda a, s, _e, _er: cmd_bac(a.dossier, s),
    "claude": lambda _a, s, _e, _er: cmd_claude(s),
    "kit-essai": lambda a, s, _e, _er: cmd_kit_essai(a.dossier, a.max_turns, a.kit, s),
    "servir": lambda a, s, _e, _er: cmd_servir(a.dossier, a.port, s),
    "apercu": lambda a, s, _e, _er: cmd_apercu(a.projet, s, a.port),
    "mutant": lambda a, s, _e, _er: cmd_mutant(a, s),
    "nuits": lambda a, s, _e, _er: (cmd_nuits_lecon(a.texte, a.projet, s) if a.verbe == "lecon"
                                     else cmd_nuits_noter(a.texte, a.canal, a.stop, s, sorte=a.sorte)),
    "chef": lambda a, s, _e, _er: cmd_chef_page(a.questions, a.sortie, s, lire(os.path.join(etat.KIT, GABARIT_CHOIX))),
    "joints": lambda a, s, _e, _er: cmd_joints(a.dossier, s),
    "transcription": lambda a, s, _e, _er: cmd_transcription(a.jsonl, s),
    "extraire": fichier_garde(lambda a, s: cmd_extraire(a.fichier, a.fiche, s)),
    "cocher": fichier_garde(cmd_cocher),
    "socle": fichier_garde(lambda a, s: cmd_socle(a.fichier, s)),
    "cout": fichier_garde(lambda a, s: cmd_cout(a.fichier, a.session, s, a.a_clore)),
    "sessions": fichier_garde(lambda a, s: cmd_sessions(a.fichier, s)),
})
