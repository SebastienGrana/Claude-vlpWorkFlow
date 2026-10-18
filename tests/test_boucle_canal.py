"""La boucle de nuit, seconde moitié (REF52, ex-`scripts/` à tiret) : le canal, l'héritage d'un chantier marqué,
la reprise, le lanceur, `vlp` dans le processus, le premier plan, les traces, minuit. Les aides : `aides_boucle.py`."""
import contextlib
import glob
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any

import carnet
import aides_boucle
import faux_claude
from aides import SCRIPTS
from aides_boucle import (ENV_GIT, FAUX_CLAUDE, FICHE, JOUR, SONNET, _PASSES, aides_du_canal, bmod, boucle, carnet_de,
                          cases_de, depot, faux, git, journal_de, lire, nuit, pilote, projet, verifier)


def test_canal():
    """NUI7 : un canal enchaîne les chantiers de son plan, chacun sur sa branche, et met de côté ce qui bloque."""
    aides = aides_du_canal()
    DATE, ecrire_f, depot_canal, carnet_du, canal, br = (aides[k] for k in ("DATE", "ecrire_f", "depot_canal", "carnet_du",
                                                                           "canal", "br"))
    sha, sujet, ancetre, branches, roles, gardes = (aides[k] for k in ("sha", "sujet", "ancetre", "branches", "roles",
                                                                       "gardes"))
    ecrits = [0]

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI7 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI7 " + nom, cond, sortie)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "BBB", "CCC"))
        code, s, lignes = canal(t, hors)
        brs = [br(c) for c in ("AAA", "BBB", "CCC")]
        sujets = git(t, "log", "--format=%s", brs[2]).splitlines()
        clore = [d for d in lignes if d["role"] == "clore"]
        lues = [bool(re.search(r"\*\*Session\*\*[^\n]*%s[^\n]*\(clore\)" % d["session"],
                               git(t, "show", "%s:ctx/%s.md" % (b, d["chantier"])))) for d, b in zip(clore, brs)]
        envs = journal_de(os.path.join(hors, "env.jsonl"))
        neuf("(a) trois chantiers réussis : trois branches à la --date, chacune ancêtre de la suivante, trois sessions "
             "clore dont la ligne `**Session** … (clore)` est commitée, trois commits « ouvert (nuit) », VLP_NUIT=1 "
             "et VLP_CANAL=A vus par les 18 sessions du faux, plugin_retard = la carte (aucune ligne : null)",
             code == 0 and "ARRÊT plan terminé — 3 clos, 0 de côté, 0 sautés" in s and branches(t) == brs
             and len({sha(t, b) for b in brs}) == 3 and ancetre(t, brs[0], brs[1]) and ancetre(t, brs[1], brs[2])
             and [d["chantier"] for d in clore] == ["AAA", "BBB", "CCC"] and all(lues)
             and sum(bool(re.fullmatch(r"Chantier (AAA|BBB|CCC) ouvert \(nuit\) : 2 fiches", x)) for x in sujets) == 3
             and len(envs) == 18 and all(e["VLP_NUIT"] == "1" and e["VLP_CANAL"] == "A" for e in envs)
             and all(d["plugin_retard"] is None for d in lignes), (s, lignes, lues, envs))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "BBB", "CCC"))
        depart = sha(t, "HEAD")
        code, s, lignes = canal(t, hors, VLP_FAUX_REFUSE="AAA1:fiche")
        saute = [d for d in lignes if d["chantier"] == "BBB"]
        neuf("(b) AAA1 refusée (cause fiche) : WIP sur sa branche, BBB qui en dépend sauté sans session, CCC part de la "
             "base et non du WIP, chaque étape au carnet",
             code == 0 and "ARRÊT plan terminé — 1 clos, 1 de côté, 1 sautés" in s
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : AAA1 refusée à la relecture")
             and "SAUTÉ BBB — dépend de AAA" in s and branches(t) == [br("AAA"), br("CCC")]
             and len(saute) == 1 and saute[0]["role"] is None and saute[0]["issue"] == "pas partie"
             and saute[0]["garde"] == "saute:AAA"
             and git(t, "merge-base", br("AAA"), br("CCC")).strip() == depart
             and not ancetre(t, br("AAA"), br("CCC"))
             and roles(lignes, "AAA") == ["découper", "jouer", "relire"]
             and [g.split(":")[0] for g in gardes(lignes, "AAA")] == ["cause-fiche", "mis-de-cote"]
             and roles(lignes, "CCC") == ["découper", "jouer", "relire", "jouer", "relire", "clore"]
             and gardes(lignes, "CCC") == [], (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"))
        code, s, lignes = canal(t, hors, VLP_FAUX_CLOT="AAA1")
        hors_role = [d for d in lignes if d["garde"] == "cloture-hors-role"]
        neuf("(c) une session de jeu qui clôt le chantier (AAA1) : carnet cloture-hors-role, WIP sur sa branche, pas de "
             "session clore, CCC joué ensuite",
             code == 0 and len(hors_role) == 1 and hors_role[0]["chantier"] == "AAA" and hors_role[0]["fiche"] == "AAA1"
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : AAA1 a clos le chantier") and "CLORE AAA" not in s
             and "clore" not in roles(lignes, "AAA") and "CLOS CCC" in s
             and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"), couts=("~0,5 fiche", "~2 fiches", "1 fiche"))
        code, s, lignes = canal(t, hors)
        neuf("(d) AAA à ~0,5 fiche, le faux en écrit 2 : mis de côté sans jouer ni commit « ouvert », CCC joué",
             code == 0 and "plus de 2 × 0.5" in s and "JOUE AAA" not in s and roles(lignes, "AAA") == ["découper"]
             and not any(x.startswith("Chantier AAA ouvert") for x in git(t, "log", "--all", "--format=%s").splitlines())
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : 2 fiches : plus de 2 × 0.5")
             and "CLOS CCC" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"))
        depart = sha(t, "HEAD")
        code, s, lignes = canal(t, hors, VLP_FAUX_VIDE="AAA")
        neuf("(d) découpage vide : mis de côté sans WIP (arbre propre), la branche reste à la base, CCC joué",
             code == 0 and "le découpage n'a ouvert aucun chantier" in s and sha(t, br("AAA")) == depart
             and not any(x.startswith("WIP") for x in git(t, "log", "--all", "--format=%s").splitlines())
             and roles(lignes, "AAA") == ["découper"] and "CLOS CCC" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "BBB", "CCC"))
        hooks = os.path.join(hors, "hooks")
        ecrire_f(os.path.join(hooks, "pre-commit"),
                 "#!/bin/sh\nif git diff --cached --name-only | grep -qx CASSE; then exit 1; fi\nexit 0\n")
        os.chmod(os.path.join(hooks, "pre-commit"), 0o755)
        git(t, "config", "core.hooksPath", hooks.replace("\\", "/"))
        code, s, lignes = canal(t, hors, VLP_FAUX_REFUSE="AAA1:fiche", VLP_FAUX_CASSE="AAA1")
        neuf("(e) cas b sous un pre-commit qui refuse CASSE : ARRÊT, HEAD et arbre intacts, carnet wip-refuse, "
             "ni BBB sauté ni CCC joué",
             code == 1 and "ARRÊT AAA : commit WIP refusé" in s and sujet(t, "HEAD") == "Chantier AAA ouvert (nuit) : 2 fiches"
             and os.path.exists(os.path.join(t, "CASSE")) and git(t, "status", "--porcelain").strip() != ""
             and gardes(lignes, "AAA")[-1] == "wip-refuse" and "SAUTÉ" not in s and "CHANTIER CCC" not in s
             and branches(t) == [br("AAA")], (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"), borne_chantiers=1)
        code, s, lignes = canal(t, hors)
        neuf("(f) la borne du plan est celle de la nuit : un chantier de borne 1, puis ARRÊT borne atteinte, sort 0",
             code == 0 and "borne 5.0 $ · 1 chantiers" in s and "CLOS AAA" in s and "CHANTIER CCC" not in s
             and "ARRÊT borne atteinte" in s and roles(lignes, "CCC") == [], (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"))
        chemin = os.path.join(t, "ctx", "08-etat.md")
        ecrire_f(chemin, lire(chemin).replace("| 3 | `CCC` — c | x | ~2 fiches | — |", "| 3 | `CCC` — c | x | ~2 fiches | — | en trop |"))
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", "TODO cassée")
        code, s, lignes = canal(t, hors)
        neuf("(g) une barre verticale dans la TODO (ValueError) : chaque chantier mis de côté, aucune session, arbre propre",
             code == 0 and s.count("TODO illisible") == 2 and "JOUE" not in s and "DÉCOUPER" not in s
             and not any(carnet.est_session(d) for d in lignes) and git(t, "status", "--porcelain").strip() == ""
             and "ARRÊT plan terminé — 0 clos, 2 de côté, 0 sautés" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        code, s = nuit(t, "--canal", "A", "--date", DATE)
        neuf("(h) un chantier déjà ouvert au départ : ARRÊT, rien joué, sort 1",
             code == 1 and "ARRÊT un chantier est déjà ouvert au départ (fiches.md)" in s and "JOUE" not in s
             and cases_de(t) == "...", s)
        code, s = nuit(t, "--canal", "A", "--date", "2026-13-45")
        neuf("(h) --date qui n'est pas une date : refusée (code 2)", code == 2 and "AAAA-MM-JJ attendu" in s, s)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, None)
        code, s, lignes = canal(t, hors)
        neuf("(i) sans plan à la date : ARRÊT plan illisible, sort 1, aucune session",
             code == 1 and "ARRÊT plan illisible — GARDE: pas de fichier des nuits" in s
             and not any(carnet.est_session(d) for d in lignes), (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA",))
        vrai = bmod.vlp

        def avec_retard(argv, dossier):
            """La carte du dépôt de test n'a pas de PLUGIN_RETARD (il compare au kit, pas au dépôt) : on la lui prête."""
            rendu, texte = vrai(argv, dossier)
            fin = "PLUGIN_RETARD=8 commit(s) de code du plugin absents du plugin chargé\n" if argv[0] == "carte" else ""
            return rendu, texte + fin

        sortie = io.StringIO()
        bmod.vlp = avec_retard
        try:
            with pilote(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), VLP_FAUX_CLORE="commit", PYTHONIOENCODING="utf-8",
                        **ENV_GIT), contextlib.redirect_stdout(sortie):
                code = bmod.main([t, "--claude", FAUX_CLAUDE, "--traces", hors, "--nuit", "--canal", "A", "--date", DATE])
        finally:
            bmod.vlp = vrai
        lignes = [d for d in carnet_du(t) if carnet.est_session(d)]   # NUI8 : notes `depart` et `base` hors tri
        neuf("(j) la carte dit PLUGIN_RETARD=8 : les six lignes de session du carnet portent plugin_retard 8",
             code == 0 and "plan terminé — 1 clos" in sortie.getvalue() and len(lignes) == 6
             and all(d["plugin_retard"] == 8 for d in lignes), (sortie.getvalue(), lignes))

    sys.stderr.write("NUI7 : %d cas neufs passés / %d écrits\n" % (ecrits[0], ecrits[0]))


def test_sans_nuit():
    """NUI7 (a), partie à elle : la seule qui attend les variables de la nuit absentes ; `tests/test_suites_voisines.py` la lance seule,
    sous ces variables, pour que leur retrait en tête se voie (ENV1)."""
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        journal = os.path.join(hors, "sans-nuit.jsonl")
        with pilote(VLP_FAUX_ENV=journal):
            code, s, cases = boucle(t, FAUX_CLAUDE, 1)
        envs = journal_de(journal)
        verifier("NUI7 (a) sans --nuit : VLP_NUIT absent de l'environnement du faux", code == 0 and len(envs) == 1
                 and envs[0]["VLP_NUIT"] is None and envs[0]["VLP_CANAL"] is None, (s, envs))


def test_herite():
    """NUI25 : un canal part d'un worktree détaché sur main, comme le lanceur — main y porte un chantier marqué, que
    le canal hérite sans le jouer ; et une carte gardée (plusieurs ouverts) n'est jamais lue « aucun »."""
    aides = aides_du_canal()
    DATE, ecrire_f, depot_canal, canal, br, sujet = (aides[k] for k in ("DATE", "ecrire_f", "depot_canal", "canal", "br",
                                                                         "sujet"))
    ecrits = [0]

    def neuf(nom, cond, sortie):
        ecrits[0] += 1
        verifier("NUI25 " + nom, cond, sortie)

    def marque(code, fiches=()):
        """Un fichier de fiches ouvert comme par `vlp.py ouvrir` : titre `# Chantier `, marque, fiches."""
        return ("# Chantier %s — hérité\n\n**Ouvert.** le 2026-09-30.\n\n## Le socle commun\n\nRien.\n\n"
                "## L'ordre des fiches\n\n%s.\n\n---\n\n" % (code, ", ".join(fiches))
                + "".join(FICHE % (f, f, f, "") for f in fiches))

    def main_herite(t, hors, d):
        """Le dépôt du canal, main portant le chantier HHH ouvert (sa marque), puis le worktree
        détaché du canal dans `d` : son chemin."""
        depot_canal(t, hors, ("AAA",))
        ecrire_f(os.path.join(t, "ctx", "100-x.md"), marque("HHH", ("HHH1", "HHH2")))
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", "HHH ouvert sur main")
        wt = os.path.join(d, "canal")
        git(t, "worktree", "add", "-q", "--detach", wt, "HEAD")
        return wt

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as d:
        wt = main_herite(t, hors, d)
        code, s, lignes = canal(wt, hors)
        herite = git(wt, "show", "%s:ctx/100-x.md" % br("AAA"))
        neuf("(a) main porte HHH ouvert : le canal découpe et clôt AAA, son commit d'ouverture dit AAA, HHH ni joué ni "
             "touché",
             code == 0 and "CLOS AAA" in s and "ARRÊT plan terminé — 1 clos, 0 de côté, 0 sautés" in s
             and "Chantier AAA ouvert (nuit) : 2 fiches" in git(wt, "log", "--format=%s", br("AAA")).splitlines()
             and "HHH" not in s and not any(str(d_.get("fiche") or "").startswith("HHH") for d_ in lignes)
             and "**Ouvert.**" in herite and "**CLOS**" not in herite and "## HHH1 [ ]" in herite, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as d:
        wt = main_herite(t, hors, d)
        code, s, lignes = canal(wt, hors, VLP_FAUX_VIDE="AAA")
        neuf("(b) main porte HHH ouvert, le découpage n'ouvre rien : mis de côté, HHH jamais pris pour le découpage",
             code == 0 and "le découpage n'a ouvert aucun chantier" in s and "HHH" not in s and "JOUE" not in s
             and not any(x.startswith("Chantier AAA ouvert") for x in git(wt, "log", "--all", "--format=%s").splitlines()),
             (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as d:
        wt = main_herite(t, hors, d)
        for nom, code_ in (("200-a.md", "AA2"), ("201-b.md", "BB2")):
            ecrire_f(os.path.join(wt, "ctx", nom), marque(code_))
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "deux ouverts dans le canal")
        code, s, _ = canal(wt, hors)
        neuf("(c) deux chantiers ouverts par le worktree du canal : la GARDE de la carte, sort 1, rien découpé",
             code == 1 and "GARDE: plusieurs chantiers ouverts : ctx/200-a.md, ctx/201-b.md" in s
             and "DÉCOUPER" not in s and "JOUE" not in s, s)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA",))
        vrai = bmod.vlp
        fichier = os.path.join(t, "ctx", "AAA.md")

        def garde_apres_clore(argv, dossier):
            """Une fois AAA marqué CLOS, la carte garde comme si un second chantier restait ouvert."""
            rendu, texte = vrai(argv, dossier)
            if argv[0] == "carte" and os.path.isfile(fichier) and "**CLOS**" in lire(fichier):
                return 1, texte.split("COURANT=")[0] + "GARDE: plusieurs chantiers ouverts : ctx/AAA.md, ctx/ZZZ.md\n"
            return rendu, texte

        sortie = io.StringIO()
        bmod.vlp = garde_apres_clore
        try:
            with pilote(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), VLP_FAUX_CLORE="commit", PYTHONIOENCODING="utf-8",
                        **ENV_GIT), contextlib.redirect_stdout(sortie):
                code = bmod.main([t, "--claude", FAUX_CLAUDE, "--traces", hors, "--nuit", "--canal", "A", "--date", DATE])
        finally:
            bmod.vlp = vrai
        s = sortie.getvalue()
        neuf("(d) la carte garde après la clôture : AAA mis de côté pour carte gardée, jamais compté clos",
             code == 0 and "MIS DE CÔTÉ AAA — carte gardée — GARDE: plusieurs chantiers ouverts" in s
             and "CLOS AAA —" not in s and "ARRÊT plan terminé — 0 clos, 1 de côté, 0 sautés" in s, s)

    sys.stderr.write("NUI25 : %d cas neufs passés / %d écrits\n" % (ecrits[0], ecrits[0]))


# --- reprendre une nuit coupée (NUI8) ---------------------------------------------------------------------
# Chaque cas pose son projet, son dépôt, son carnet et son `~` (HOME, USERPROFILE) dans des dossiers jetés.

def test_reprise():
    aides = aides_du_canal()
    DATE, canal, depot_canal, carnet_du = aides["DATE"], aides["canal"], aides["depot_canal"], aides["carnet_du"]
    br, sha, sujet, branches, roles = aides["br"], aides["sha"], aides["sujet"], aides["branches"], aides["roles"]
    ecrire_f, ancetre = aides["ecrire_f"], aides["ancetre"]
    ecrits, sautes = [0], [0]
    plafonds = bmod.plafonds()
    SID = "00000000-0000-4000-8000-00000000000a"

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI8 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI8 " + nom, cond, sortie)

    def mesure_cli(h, sid):
        """`mesure-tokens.py <id>` lancé par le test sous le `~` de `h` : (tours, usd) de sa ligne."""
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "mesure-tokens.py"), sid], capture_output=True, text=True,
                           encoding="utf-8", env=dict(os.environ, HOME=h, USERPROFILE=h, PYTHONIOENCODING="utf-8"))
        tete, valeurs = (r.stdout.splitlines() + ["", ""])[:2]
        d = dict(zip(tete.split("\t"), valeurs.split("\t")))
        return int(d.get("tours") or -1), float(d.get("usd") or -1)

    def session_de(lignes, role, fiche=None):
        """La première ligne de session du rôle (et de la fiche), ou None."""
        return next((d for d in lignes if carnet.est_session(d) and d["role"] == role
                     and (fiche is None or d["fiche"] == fiche)), None)

    def reprendre(t, hors, h, *options, **env):
        """boucle.py --nuit --canal A --reprendre --carnet <celui de DATE> dans `t` : (code, sortie, lignes du carnet)."""
        env.setdefault("VLP_FAUX_CLORE", "commit")
        chemin = carnet.du_jour(t, DATE)
        assert chemin
        code, s = nuit(t, "--canal", "A", "--reprendre", "--carnet", chemin, *options, traces=hors, HOME=h, USERPROFILE=h, **env)
        return code, s, carnet_du(t)

    # (a) un jeu coupé : mesuré dans sa transcription, chantier de côté, la fiche suivante pas jouée -----------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        depart = sha(t, "HEAD")
        code, s, lignes = canal(t, hors, VLP_FAUX_COUPE="AAA1", HOME=h, USERPROFILE=h)
        j = session_de(lignes, "jouer", "AAA1")
        tours, usd = mesure_cli(h, j["session"]) if j else (None, None)
        neuf("(a) --nuit, AAA1 en COUPE : issue coupure, usd_cli null, usd_kit et tours_kit égaux à mesure-tokens.py (tours 2), "
             "pot = usd_kit, chantier mis de côté (WIP), AAA2 pas jouée, CCC joué",
             code == 0 and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s and j is not None
             and j["issue"] == "coupure" and j["usd_cli"] is None and j["tours_cli"] is None
             and tours == 2 and j["tours_kit"] == tours and j["usd_kit"] == usd and carnet.pot([j], plafonds) == usd
             and roles(lignes, "AAA") == ["découper", "jouer"] and "JOUE AAA2" not in s and "MIS DE CÔTÉ AAA" in s
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : AAA1 : session de jeu coupée")
             and "CLOS CCC" in s, (s, lignes, tours, usd))
        departs = [(i, d) for i, d in enumerate(lignes) if (d["note"] or "").startswith("depart ")]
        neuf("(a) chaque session a, avant sa ligne, une note `depart <rôle>` au même id, hors `est_session` (role null), "
             "et la note `base` du canal porte HEAD de départ",
             len(departs) == sum(carnet.est_session(d) for d in lignes) and all(d["role"] is None for _, d in departs)
             and all(any(x["note"] == "depart %s" % d["role"] and x["session"] == d["session"] for x in lignes[:i])
                     for i, d in enumerate(lignes) if carnet.est_session(d))
             and [d["note"] for d in lignes if (d["note"] or "").startswith("base ")] == ["base " + depart], (lignes, depart))

    # (b) la même coupure sans transcription : la garde le dit, le pot compte le plafond du rôle -------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        code, s, lignes = canal(t, hors, "--borne-usd", "4.5", VLP_FAUX_COUPE="AAA1", VLP_FAUX_SANS_TRANSCRIPTION="1",
                                HOME=h, USERPROFILE=h)
        j = session_de(lignes, "jouer", "AAA1")
        neuf("(b) COUPE sans transcription : garde « transcription introuvable », usd_kit et tours_kit null (pas 0), "
             "pot = le --max-budget-usd du rôle jouer — et la borne de 4.5 $ tient CCC à l'écart",
             code == 0 and j is not None and j["issue"] == "coupure" and j["usd_kit"] is None and j["tours_kit"] is None
             and j["usd_cli"] is None and "transcription introuvable" in str(j["garde"])
             and carnet.pot([j], plafonds) == bmod.ROLES["jouer"]["usd"]
             and "ARRÊT borne atteinte — pot 5.0100 $ ≥ borne 4.5000 $" in s and "CHANTIER CCC" not in s, (s, lignes))

    # (c) le code de sortie ne décide pas de l'issue ---------------------------------------------------------------
    issues = []
    for sortie in ("143", "1"):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
            depot_canal(t, hors, ("AAA",))
            code, s, lignes = canal(t, hors, VLP_FAUX_COUPE="AAA1=" + sortie, HOME=h, USERPROFILE=h)
            j = session_de(lignes, "jouer", "AAA1")
            issues.append((code, j["issue"] if j else None, j["usd_cli"] if j else 0))
    neuf("(c) COUPE sortie 143, puis sortie 1 : la même issue `coupure` les deux fois", issues == [(0, "coupure", None)] * 2, issues)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as h:
        projet(t)
        sid = "11111111-2222-3333-4444-555555555555"
        def transcriptions():
            return glob.glob(os.path.join(glob.escape(h), ".claude", "projects", "*", sid + ".jsonl"))

        code, l, e = faux(["-p", "/vlp:tache F9", "--session-id", sid, "--model", SONNET], t, VLP_FAUX_COUPE="F9=143",
                          VLP_FAUX_RATE="F9", HOME=h, USERPROFILE=h)
        ecrites = [json.loads(x) for f in transcriptions() for x in lire(f).splitlines()]
        neuf("(c) faux, COUPE=F9=143 : sort 143, init puis rien (aucun result), transcription de deux lignes assistant à "
             "message.id distincts, message.model celui de --model, usage à la forme d'un vrai transcript",
             code == 143 and [x["type"] for x in l] == ["system"] and len(ecrites) == 2
             and len({x["message"]["id"] for x in ecrites}) == 2 and all(x["message"]["model"] == SONNET for x in ecrites)
             and all(set(x["message"]["usage"]) >= {"input_tokens", "output_tokens", "cache_creation_input_tokens",
                                                    "cache_read_input_tokens", "cache_creation"} for x in ecrites), (code, l, e, ecrites))
        for f in transcriptions():
            os.remove(f)
        code, l, e = faux(["-p", "/vlp:tache F9", "--session-id", sid], t, VLP_FAUX_COUPE="F9", VLP_FAUX_RATE="F9",
                          VLP_FAUX_SANS_TRANSCRIPTION="1", HOME=h, USERPROFILE=h)
        neuf("(c) faux, COUPE=F9 : sort 1 par défaut ; SANS_TRANSCRIPTION n'écrit rien ; une autre fiche n'est pas coupée",
             code == 1 and not transcriptions()
             and faux(["-p", "/vlp:tache F9"], t, VLP_FAUX_COUPE="F8", VLP_FAUX_RATE="F9", HOME=h, USERPROFILE=h)[0] == 0,
             (code, l, e))

    # (d) un depart sans fin, la branche créée, l'arbre sale : --reprendre -------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        chemin = carnet.du_jour(t, DATE)
        assert chemin
        depart = sha(t, "HEAD")
        carnet.noter(chemin, "A", "base " + depart)
        carnet.ajouter(chemin, nuit=DATE, canal="A", chantier="AAA", fiche="AAA1", note="depart jouer", session=SID)
        git(t, "switch", "-q", "-c", br("AAA"))
        ecrire_f(os.path.join(t, "sale.txt"), "travail non commité\n")
        with pilote(HOME=h, USERPROFILE=h):
            faux_claude.transcription(SID, SONNET)
        tours, usd = mesure_cli(h, SID)
        code, s, lignes = reprendre(t, hors, h)
        coupures = [d for d in lignes if d["issue"] == "coupure"]
        neuf("(d) un depart sans fin, branche créée, arbre sale → --reprendre : une ligne coupure (coût relu dans la "
             "transcription), commit WIP du travail non commité, le chantier suivant joué",
             code == 0 and "REPRISE canal A · 1 sessions coupées · en cours : AAA" in s and len(coupures) == 1
             and coupures[0]["session"] == SID and coupures[0]["role"] == "jouer" and coupures[0]["fiche"] == "AAA1"
             and coupures[0]["chantier"] == "AAA" and coupures[0]["usd_cli"] is None and coupures[0]["tours_kit"] == tours == 2
             and coupures[0]["usd_kit"] == usd and "reprise : session sans fin" in str(coupures[0]["garde"])
             and "MIS DE CÔTÉ AAA — une session a été coupée" in s and "JOUE AAA" not in s
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : une session a été coupée")
             and "sale.txt" in git(t, "show", "--name-only", "--format=", br("AAA"))
             and branches(t) == [br("AAA"), br("CCC")] and git(t, "merge-base", br("AAA"), br("CCC")).strip() == depart
             and roles(lignes, "CCC") == ["découper", "jouer", "relire", "jouer", "relire", "clore"]
             and "CLOS CCC" in s and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s, (s, lignes))
        avant = (lire(chemin), branches(t), sha(t, "HEAD"))
        code, s, lignes = reprendre(t, hors, h)
        neuf("(d) 2e --reprendre : carnet, branches nuit/* et HEAD identiques avant et après, aucune ligne JOUE, rien à reprendre",
             code == 0 and (lire(chemin), branches(t), sha(t, "HEAD")) == avant and "JOUE" not in s
             and "REPRISE canal A · 0 sessions coupées · en cours : aucun" in s
             and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s, (s, avant))

    # (d) un chantier découpé, arrêté entre deux fiches, l'arbre propre : il reprend dans sa branche -----------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        code1, s1, l1 = canal(t, hors, "--plafond", "1", HOME=h, USERPROFILE=h)
        pointe = sha(t, br("AAA"))
        code, s, lignes = reprendre(t, hors, h)
        neuf("(d) chantier découpé, une fiche jouée et commitée, aucune coupure : --reprendre le reprend dans sa branche, "
             "sans repasser par découper (une seule session découper pour AAA), la branche jamais recréée, puis CCC",
             code1 == 0 and "plafond de 1 fiches" in s1 and roles(l1, "AAA") == ["découper", "jouer", "relire"]
             and code == 0 and "REPRISE canal A · 0 sessions coupées · en cours : AAA" in s and "REPRISE AAA" in s
             and roles(lignes, "AAA") == ["découper", "jouer", "relire", "jouer", "relire", "clore"]
             and "CLOS AAA" in s and "CLOS CCC" in s and "DÉCOUPER AAA" not in s
             and branches(t) == [br("AAA"), br("CCC")] and ancetre(t, pointe, br("AAA"))
             and "ARRÊT plan terminé — 2 clos, 0 de côté, 0 sautés" in s, (s1, s, lignes))

    # (g) une relecture coupée, une clôture coupée : le chantier se met de côté ---------------------------------------
    for coupe, genre in (("relire:AAA1", "la relecture a été coupée"), ("clore", "la clôture a été coupée")):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
            depot_canal(t, hors, ("AAA",))
            code, s, lignes = canal(t, hors, VLP_FAUX_COUPE=coupe, HOME=h, USERPROFILE=h)
            role = coupe.split(":")[0]
            j = session_de(lignes, role)
            tours, usd = mesure_cli(h, j["session"]) if j else (None, None)
            neuf("(g) %s en COUPE : issue coupure, usd_kit lu dans la transcription, aucun refus ni relance, chantier "
                 "mis de côté (« %s »)" % (coupe, genre),
                 code == 0 and j is not None and j["issue"] == "coupure" and j["usd_cli"] is None and j["usd_kit"] == usd
                 and j["tours_kit"] == tours == 2 and j["refus_n"] is None and "RELANCE" not in s and genre in s
                 and "MIS DE CÔTÉ AAA" in s and "ARRÊT plan terminé — 0 clos, 1 de côté, 0 sautés" in s, (s, lignes))

    # (e) sans --nuit, rien de la reprise ni de l'éveil ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, cases = boucle(t, FAUX_CLAUDE, 1, options=["--reprendre"])
        neuf("(e) sans --nuit : --reprendre refusé (code 2), aucune ligne ÉVEIL, rien joué",
             code == 2 and "exigent --nuit" in s and "ÉVEIL" not in s and cases == "...", s)
        code, s, cases = boucle(t, FAUX_CLAUDE, 1)
        neuf("(e) sans --nuit, une fiche jouée : aucune ligne ÉVEIL, aucun carnet de nuit",
             code == 0 and cases == "x.." and "ÉVEIL" not in s and not os.path.exists(os.path.join(t, ".git", "vlp-nuit")), s)
        chemin = os.path.join(hors, DATE + ".jsonl")
        refus = [nuit(t, "--canal", "A", "--reprendre"),
                 nuit(t, "--canal", "A", "--reprendre", "--carnet", chemin, "--chantier", "X"),
                 nuit(t, "--canal", "A", "--reprendre", "--carnet", chemin, "--date", DATE),
                 nuit(t, "--canal", "A", "--reprendre", "--carnet", os.path.join(hors, "carnet.jsonl"))]
        neuf("(e) --nuit --reprendre sans --carnet, avec --chantier, avec --date, ou sur un carnet dont le nom n'est pas une "
             "date : refusé (code 2), rien écrit — la date vient du nom du carnet, jamais de l'horloge",
             [c for c, _ in refus] == [2] * 4 and "exige --carnet" in refus[0][1] and "exige --carnet" in refus[1][1]
             and "exige --carnet" in refus[2][1] and "AAAA-MM-JJ attendu" in refus[3][1] and not os.path.exists(chemin), refus)

    # (h) le worktree du canal absent -----------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as nu:
        chemin = os.path.join(hors, DATE + ".jsonl")
        absent = nuit(os.path.join(nu, "absent"), "--canal", "A", "--reprendre", "--carnet", chemin)
        sans_git = nuit(nu, "--canal", "A", "--reprendre", "--carnet", chemin)
        neuf("(h) dossier du canal absent, ou sans Git : GARDE:, sort 1, ni claude lancé ni carnet écrit",
             absent[0] == 1 and absent[1].startswith("GARDE:") and sans_git[0] == 1 and sans_git[1].startswith("GARDE:")
             and "CLAUDE=" not in absent[1] + sans_git[1] and not os.path.exists(chemin), (absent, sans_git))

    # (i) le pot, ligne à ligne, et le coût d'une session coupée sans transcription lisible --------------------------------
    neuf("(i) carnet.cout_de : usd_cli, à défaut usd_kit, à défaut le plafond du rôle, sinon 0 ; un 0.0 est un coût",
         carnet.cout_de({"role": "jouer", "usd_cli": 1.5, "usd_kit": 9}, {"jouer": 5}) == 1.5
         and carnet.cout_de({"role": "jouer", "usd_cli": None, "usd_kit": 0.45}, {"jouer": 5}) == 0.45
         and carnet.cout_de({"role": "jouer", "usd_cli": None, "usd_kit": None}, {"jouer": 5}) == 5
         and carnet.cout_de({"role": "jouer", "usd_cli": 0.0, "usd_kit": None}, {"jouer": 5}) == 0.0
         and carnet.cout_de({"role": "jouer", "usd_cli": None, "usd_kit": None}) == 0
         and carnet.pot([{"role": "jouer", "usd_cli": None, "usd_kit": None, "note": None, "stop": None},
                         {"role": "jouer", "usd_cli": 1, "note": "hors pot", "stop": None}], {"jouer": 5}) == 5
         and set(plafonds) == {"découper", "jouer", "relire", "relance", "clore"}
         and all(plafonds[r] == bmod.ROLES[r]["usd"] for r in bmod.ROLES), plafonds)
    with tempfile.TemporaryDirectory() as h:
        with pilote(HOME=h, USERPROFILE=h):
            faux_claude.transcription(SID, "claude-inconnu-9")
            hors_grille = bmod.mesure_kit(SID)
            introuvable = bmod.mesure_kit("sans-transcription")
        neuf("(i) mesure_kit : un modèle hors grille rend (None, tours, garde) — jamais 0 ; une session sans transcription "
             "rend (None, None, garde)",
             hors_grille[0] is None and hors_grille[1] == 2 and "modèle hors grille (claude-inconnu-9)" in hors_grille[2]
             and introuvable[:2] == (None, None) and "transcription introuvable" in introuvable[2], (hors_grille, introuvable))

    # (f) l'éveil de la machine : win32 seulement ------------------------------------------------------------------------
    if sys.platform == "win32":
        with tempfile.TemporaryDirectory() as t:
            depot(t)
            code, s = nuit(t, "--canal", "A", "--chantier", "X", "--plafond", "1")
            neuf("(f) win32, --nuit : l'appel réel à SetThreadExecutionState rend un état — ÉVEIL tenu",
                 code == 0 and "ÉVEIL tenu" in s and "ÉVEIL non tenu" not in s, s)
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
            depot(t)
            vrai, appels = bmod.appel_eveil, []
            bmod.appel_eveil = lambda drapeaux: appels.append(drapeaux) or 0
            sortie = io.StringIO()
            try:
                with pilote(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), PYTHONIOENCODING="utf-8", **ENV_GIT), \
                        contextlib.redirect_stdout(sortie):
                    code = bmod.main([t, "--claude", FAUX_CLAUDE, "--traces", hors, "--nuit", "--canal", "A",
                                      "--chantier", "X", "--plafond", "1", "--date", JOUR])
            finally:
                bmod.appel_eveil = vrai
            notes = [d["note"] for d in carnet.lire(carnet_de(t)) if (d["note"] or "").startswith("ÉVEIL")]
            neuf("(f) retour 0 : ÉVEIL non tenu et une note ; ES_CONTINUOUS | ES_SYSTEM_REQUIRED au départ (0x80000001), "
                 "ES_CONTINUOUS à la fin (0x80000000) — les valeurs de la doc Microsoft",
                 code == 0 and "ÉVEIL non tenu" in sortie.getvalue() and "ÉVEIL tenu" not in sortie.getvalue()
                 and len(notes) == 1 and appels == [0x80000001, 0x80000000]
                 and bmod.ES_CONTINUOUS == 0x80000000 and bmod.ES_SYSTEM_REQUIRED == 0x00000001, (sortie.getvalue(), notes, appels))
    else:
        sautes[0] += 2
        sys.stderr.write("SAUTÉ (plateforme) : (f) ÉVEIL tenu et non tenu — sys.platform vaut %s, pas win32\n" % sys.platform)

    sys.stderr.write("NUI8 : %d cas neufs passés / %d écrits · %d cas d'avant passés · %d cas sautés (plateforme)\n"
                     % (ecrits[0], ecrits[0], _PASSES[0] - ecrits[0], sautes[0]))


# --- lancer les deux canaux d'une nuit (NUI9) -------------------------------------------------------------
# Chaque cas bâtit projet, dépôt sur `main`, dépôt nu `origin` (poussé une fois), carnet et `~` dans des dossiers jetés.

def test_lanceur():
    aides = aides_du_canal()
    DATE, depot_canal, carnet_du = aides["DATE"], aides["depot_canal"], aides["carnet_du"]
    br, sha, branches, ecrire_f = aides["br"], aides["sha"], aides["branches"], aides["ecrire_f"]
    ecrits = [0]
    SOIR = "RIEN FUSIONNÉ, RIEN POUSSÉ — /vlp:chef le matin"

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI9 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI9 " + nom, cond, sortie)

    def projet_lanceur(t, hors, o):
        """Le dépôt de `depot_canal` avec un plan à deux chantiers en A (AAA, BBB) et un en B (CCC), sur `main`, et un
        dépôt nu `origin` poussé une fois."""
        depot_canal(t, hors, ("AAA", "BBB"), codes_b=("CCC",))
        git(t, "branch", "-M", "main")
        subprocess.run(["git", "init", "-q", "--bare", o], check=True, capture_output=True)
        git(t, "remote", "add", "origin", o)
        git(t, "push", "-q", "origin", "main")

    def lance(t, *options, claude: Any = FAUX_CLAUDE, base=None, **env):
        """boucle.py --nuit --lancer --date DATE dans `t` : (code, sortie). Sans --traces : celles des canaux vont au carnet."""
        env_ = dict(base) if base is not None else {k: v for k, v in os.environ.items()
                                                    if k not in (carnet.ENV_CARNET, carnet.ENV_CANAL)}
        env_.update(ENV_GIT)
        env_.update(VLP_FAUX_VLP=os.path.join(SCRIPTS, "vlp.py"), VLP_FAUX_CLORE="commit", PYTHONIOENCODING="utf-8")
        env_.update(env)
        argv = [sys.executable, os.path.join(SCRIPTS, "boucle.py"), t, "--nuit", "--lancer", "--date", DATE]
        r = subprocess.run(argv + (["--claude", claude] if claude else []) + list(options), env=env_,
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout + r.stderr

    def chemin_carnet(t):
        chemin = carnet.du_jour(t, DATE)
        assert chemin
        return chemin

    def octets(chemin):
        with open(chemin, "rb") as h:
            return h.read()

    def worktrees(t):
        return git(t, "worktree", "list").splitlines()

    def exclu(t):
        """Le texte de `info/exclude` du dépôt, ou ''."""
        chemin = os.path.join(t, ".git", "info", "exclude")
        return octets(chemin).decode("utf-8", "replace") if os.path.isfile(chemin) else ""

    def rien_cree(t):
        """Aucun worktree, aucun dossier `.claude/worktrees`, rien dans le dossier du carnet, `info/exclude` sans la ligne."""
        return (len(worktrees(t)) == 1 and not os.path.exists(os.path.join(t, ".claude", "worktrees"))
                and not glob.glob(os.path.join(os.path.dirname(chemin_carnet(t)), "*")) and ".claude/worktrees" not in exclu(t))

    # (a) la nuit lancée : deux canaux en parallèle, rien fusionné, rien poussé ---------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o:
        projet_lanceur(t, hors, o)
        avant = (sha(t, "main"), git(t, "ls-remote", "origin"))
        code, s = lance(t, VLP_FAUX_DORT="1")
        lignes = s.splitlines()

        def rang(debut):
            return next((i for i, l in enumerate(lignes) if l.startswith(debut)), -1)
        dep_a, dep_b, fin_a, fin_b, ligne_b = (rang(x) for x in ("DÉPART A · pid ", "DÉPART B · pid ", "FIN A · code ", "FIN B · code ", "[B] "))
        neuf("(a) --lancer, A : AAA et BBB, B : CCC, VLP_FAUX_DORT=1 : DÉPART A et DÉPART B avant toute ligne FIN ; des lignes "
             "[B] et FIN B avant FIN A, des lignes [A] après FIN B ; FIN code 0 des deux, dernière ligne « RIEN FUSIONNÉ, RIEN "
             "POUSSÉ », sort 0",
             code == 0 and min(dep_a, dep_b, fin_a, fin_b, ligne_b) >= 0 and max(dep_a, dep_b) < min(fin_a, fin_b)
             and ligne_b < fin_b < fin_a and any(l.startswith("[A] ") for l in lignes[fin_b:])
             and lignes[fin_a].startswith("FIN A · code 0") and lignes[fin_b].startswith("FIN B · code 0") and lignes[-1] == SOIR, s)
        carnets = glob.glob(os.path.join(os.path.dirname(chemin_carnet(t)), "*.jsonl"))
        ligs = carnet_du(t)
        liste = "\n".join(worktrees(t))
        neuf("(a) git worktree list porte nuit-<date>-A et -B ; un seul carnet, des lignes des canaux A et B (A : AAA et BBB, "
             "B : CCC) ; les trois chantiers ont leur branche ; sha de main et ls-remote origin identiques ; git status "
             "--porcelain vide ; .gitignore absent, la ligne .claude/worktrees/ dans info/exclude",
             len(worktrees(t)) == 3 and "nuit-%s-A" % DATE in liste and "nuit-%s-B" % DATE in liste and len(carnets) == 1
             and {(d["canal"], d["chantier"]) for d in ligs if carnet.est_session(d)} == {("A", "AAA"), ("A", "BBB"), ("B", "CCC")}
             and sorted(branches(t)) == [br("AAA"), br("BBB"), "nuit/%s-B-CCC" % DATE]
             and (sha(t, "main"), git(t, "ls-remote", "origin")) == avant and git(t, "status", "--porcelain").strip() == ""
             and not os.path.exists(os.path.join(t, ".gitignore")) and ".claude/worktrees/" in exclu(t).splitlines(),
             (liste, carnets, branches(t), git(t, "status", "--porcelain"), exclu(t)))
        dossier_carnet = os.path.dirname(chemin_carnet(t))
        neuf("(a) les traces des deux canaux vont dans le dossier du carnet (hors Git), une par canal, non vides",
             all(os.listdir(os.path.join(dossier_carnet, "traces-%s-%s" % (DATE, c))) for c in "AB"), os.listdir(dossier_carnet))

        # (b) relancé à la même date : un worktree de nuit existe déjà ; sans eux, ce sont les branches -----------------
        avant_b = (octets(chemin_carnet(t)), worktrees(t), branches(t))
        code, s = lance(t)
        neuf("(b) relancé à la même date : GARDE sur le worktree existant, sort 1, aucun DÉPART, aucun worktree de plus, "
             "carnet et branches inchangés",
             code == 1 and "GARDE: un worktree de nuit existe déjà" in s and "DÉPART" not in s
             and (octets(chemin_carnet(t)), worktrees(t), branches(t)) == avant_b, s)
        for ligne in worktrees(t)[1:]:
            git(t, "worktree", "remove", "--force", ligne.split()[0])
        code, s = lance(t)
        neuf("(b) les worktrees retirés, les branches restent : GARDE sur la branche existante, sort 1, aucun worktree",
             code == 1 and "GARDE: une branche de cette nuit existe déjà" in s and "DÉPART" not in s and len(worktrees(t)) == 1
             and octets(chemin_carnet(t)) == avant_b[0], s)

    # (c) les gardes du projet : aucun worktree, aucun carnet, rien d'écrit avant la dernière ---------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o:
        projet_lanceur(t, hors, o)
        ecrire_f(os.path.join(t, "ctx", "100-x.md"), "# x modifié, pas commité\n")
        code, s = lance(t)
        neuf("(c) un fichier non commité : GARDE sur l'arbre, sort 1, rien créé",
             code == 1 and s.splitlines()[-1].startswith("GARDE: l'arbre n'est pas propre") and rien_cree(t), s)
        git(t, "checkout", "-q", "--", ".")
        git(t, "switch", "-q", "-c", "autre")
        code, s = lance(t)
        neuf("(c) pas sur main : GARDE sur la branche, sort 1, rien créé",
             code == 1 and "GARDE: la branche courante est autre, pas main" in s and rien_cree(t), s)
        git(t, "switch", "-q", "main")
        code, s = lance(t, "--date", "2026-10-02")
        neuf("(c) pas de plan à la date : GARDE sur le plan, sort 1, rien créé",
             code == 1 and "GARDE: pas de plan utilisable à la date 2026-10-02" in s and rien_cree(t), s)
        nuits = os.path.relpath(glob.glob(os.path.join(t, "ctx", "*-nuits.md"))[0], t).replace("\\", "/")
        ecrire_f(os.path.join(t, ".gitignore"), "ctx/*-nuits.md\n")
        git(t, "rm", "-q", "--cached", nuits)
        git(t, "add", ".gitignore")
        git(t, "commit", "-q", "-m", "le fichier des nuits ignoré")
        code, s = lance(t)
        neuf("(c) fichier des nuits ignoré (.gitignore) : GARDE sur le fichier, sort 1, rien créé",
             code == 1 and "GARDE: le fichier des nuits (%s) est ignoré par Git" % nuits in s and rien_cree(t)
             and git(t, "status", "--porcelain").strip() == "", s)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o:
        projet_lanceur(t, hors, o)
        ecrire_f(os.path.join(t, ".gitignore"), ".claude/worktrees/\n")
        git(t, "add", ".gitignore")
        git(t, "commit", "-q", "-m", "worktrees ignorés")
        avant_exclu = exclu(t)
        code, s = lance(t)
        neuf("(c) .claude/worktrees/ déjà ignoré (.gitignore) : la nuit part, info/exclude n'est pas touché, sort 0",
             code == 0 and "FIN A · code 0" in s and "FIN B · code 0" in s and exclu(t) == avant_exclu
             and git(t, "status", "--porcelain").strip() == "", s)

    # (d) claude introuvable : la GARDE d'avant tout le reste ------------------------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o, \
            tempfile.TemporaryDirectory() as vide:
        projet_lanceur(t, hors, o)
        reduit = {k: v for k, v in os.environ.items() if k not in ("VLP_CLAUDE", carnet.ENV_CARNET, carnet.ENV_CANAL)}
        reduit.update(PATH=os.path.dirname(sys.executable), LOCALAPPDATA=vide, APPDATA=vide)
        code, s = lance(t, claude=None, base=reduit)
        neuf("(d) claude introuvable (VLP_CLAUDE ôtée, PATH réduit à Python, LOCALAPPDATA et APPDATA vides) : GARDE: claude "
             "introuvable, sort 1, aucun worktree",
             code == 1 and s.startswith("GARDE: claude introuvable") and rien_cree(t), s)

    # (e) les options : ce qu'argparse refuse -------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as t:
        def argparse_refuse(*options):
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "boucle.py"), t, *options], capture_output=True, text=True,
                               encoding="utf-8")
            return r.returncode, r.stdout + r.stderr
        code, s = argparse_refuse()
        neuf("(e) sans --lancer ni --nuit, --plafond absent : refusé par argparse (code 2)",
             code == 2 and "--plafond est exigé sans --nuit" in s, s)
        code, s = argparse_refuse("--lancer", "--plafond", "1")
        neuf("(e) --lancer sans --nuit : refusé par argparse (code 2)", code == 2 and "exigent --nuit" in s, s)
        code, s = argparse_refuse("--nuit", "--lancer", "--canal", "A")
        neuf("(e) --nuit --lancer --canal : refusé par argparse (code 2), le lanceur ouvre les deux canaux lui-même",
             code == 2 and "--lancer ouvre les deux canaux" in s, s)

    sys.stderr.write("NUI9 : %d cas neufs passés / %d écrits\n" % (ecrits[0], ecrits[0]))


# --- `vlp` appelé dans le processus rend ce que rendait le sous-processus (VIT6) -----

def test_vlp_dans_processus():
    """Comparer `bmod.vlp` à un vrai `vlp.py` lancé en sous-processus : même code, même sortie, sur une carte et sur
    une ligne de commande fausse (sortie 2) ; le dossier courant et l'environnement ne fuient pas après l'appel."""
    with tempfile.TemporaryDirectory() as t:
        projet(t)
        ici, env = os.getcwd(), dict(os.environ)
        rendus, attendus = [], []
        for argv in (["carte", t], ["sous-commande-inconnue"]):
            rendus.append(bmod.vlp(argv, t))
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "vlp.py")] + argv, cwd=t, capture_output=True,
                               text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            attendus.append((r.returncode, r.stdout))
        verifier("vlp dans le processus : même code et même sortie qu'un sous-processus, rien ne fuit",
                 rendus == attendus and attendus[1][0] == 2 and "PROCHAINE=F1" in attendus[0][1]
                 and os.getcwd() == ici and dict(os.environ) == env,
                 "rendu %r\nattendu %r" % (rendus, attendus))


def test_premier_plan():
    """ARP1 : toute session, sans `--nuit` comme sous `--nuit`, reçoit `--append-system-prompt PREMIER_PLAN`."""
    def consignes(journal):
        """Pour chaque lancement du journal : le texte qui suit `--append-system-prompt`, ou None."""
        return [a[a.index("--append-system-prompt") + 1] if "--append-system-prompt" in a[:-1] else None
                for a in journal_de(journal)]

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        journal = os.path.join(hors, "argv.jsonl")
        code, s, cases = boucle(t, projet(t), 1, VLP_FAUX_ARGV=journal)
        simple = consignes(journal)
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        journal = os.path.join(hors, "argv.jsonl")
        code_n, s_n = nuit(t, "--canal", "A", "--chantier", "X", traces=hors, VLP_FAUX_ARGV=journal)
        de_nuit = consignes(journal)
    verifier("ARP1 : la session sans --nuit (1) et toutes celles de --nuit (jouer et relire) reçoivent "
             "--append-system-prompt suivi de PREMIER_PLAN — mutant : l'option retirée de `commun`",
             code == 0 and simple == [bmod.PREMIER_PLAN] and code_n == 0 and len(de_nuit) >= 2
             and all(c == bmod.PREMIER_PLAN for c in de_nuit), (simple, de_nuit, s, s_n))


def test_traces():
    """Dette ARP : un `--traces` absent se crée, la fiche se joue ; un `--traces` qui est un fichier rend une GARDE."""
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        absent = os.path.join(hors, "pas", "encore")
        code, s, cases = boucle(t, projet(t), 1, options=("--traces", absent))
        cree = os.path.isdir(absent) and os.listdir(absent) != []
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        fichier = os.path.join(hors, "un-fichier")
        open(fichier, "w").close()
        code_f, s_f, cases_f = boucle(t, projet(t), 1, options=("--traces", fichier))
    verifier("dette ARP : --traces absent créé, F1 cochée, trace écrite ; --traces sur un fichier : GARDE, sort 1, "
             "rien de joué — mutant : le makedirs retiré", code == 0 and cases == "x.." and cree
             and code_f == 1 and "GARDE: dossier de traces" in s_f and cases_f == "...", (s, s_f))


def test_minuit():
    """Une suite qui passe minuit : `JOUR` posé à une autre date que l'horloge, comme après minuit. La boucle lancée
    par `nuit()` sans --date écrit le carnet de `JOUR`, celui que `carnet_de` relit."""
    vrai = aides_boucle.JOUR
    aides_boucle.JOUR = "2099-01-01"
    try:
        with tempfile.TemporaryDirectory() as t:
            depot(t)
            with pilote(VLP_FAUX_ERREUR="api"):
                code, s = nuit(t, "--canal", "A", "--chantier", "X")
            chemin = carnet_de(t)
            lignes = carnet.lire(chemin)
    finally:
        aides_boucle.JOUR = vrai
    verifier("minuit : sans --date, nuit() passe JOUR à boucle.py, et carnet_de relit ce carnet-là, l'horloge "
             "fût-elle à un autre jour — mutant : le --date de nuit() retiré",
             code == 1 and os.path.basename(chemin) == "2099-01-01.jsonl"
             and [d["issue"] for d in lignes if carnet.est_session(d)] == ["pas partie"], (s, chemin, lignes))
