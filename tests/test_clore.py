"""`noyau/clore.py` : `clore`, la TODO qu'il retire, ses repères, le chantier courant, le post-it, les blobs — la
décision sans Git (REF48) puis les commandes, migré de l'ancienne suite maison (REF51). Chaque `assert` garde le
libellé d'origine de son `verifier` en tête de son message (REF5), puis le diagnostic.
"""
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

import pytest
from aides import (
    RACINE,
    SCRIPTS,
    appel,
    ecrire,
    ligne_close,
    lire,
    lire_texte,
    mod,
    transcript,
)
from noyau import clore

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

def test_blocs_worktrees_principal_en_tete():
    texte = "\n".join(["worktree /d/kit", "HEAD abc", "branch refs/heads/main", "",
                       "worktree /t/arbre", "HEAD def", "detached", ""])
    assert clore.blocs_worktrees(texte) == [("/d/kit", "main"), ("/t/arbre", None)]
    assert clore.blocs_worktrees("") == []


def test_textes_du_lot_blob_absent_et_arbre():
    sortie = (b"abc blob 10\nun\r\ndeux\r\n\n"    # un blob : 10 octets, puis son LF
              b"HEAD:x missing\n"                  # absent : rien à sauter
              b"def tree 3\nxyz\n")                # pas un blob
    assert clore.textes_du_lot(sortie, 3) == ["un\ndeux\n", None, None]


def test_prefixes_joues():
    assert clore.prefixes_joues("REF45 : un\nFusion : W2\nW2 : deux\nREF46 : trois\nautre\n") == ["REF", "W"]
    assert clore.prefixes_joues("") == []


OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


OUVERT_LIGNE = mod.OUVERT_LIGNE   # la seconde valeur d'`OUVERT` dans l'ancienne suite maison, lue par les groupes de sa fin


def ouvert_ligne(texte):
    """`ouvert`, tel que les groupes de la fin de l'ancienne suite maison l'appelaient : le gabarit `OUVERT_LIGNE` inséré
    brut, `%s` compris."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT_LIGNE, texte, count=1, flags=re.M)


QFICHES = """# Chantier Q

## Le socle commun

## L'ordre des fiches

<!-- FICHE:Q1 -->
## Q1 [x] — Créer
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:Q2 -->
## Q2 [x] — Brancher
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
"""


T0 = 1790000000


def test_clore_todo(tmp_path):
    """TAB3 : `clore` lit la TODO avant sa première écriture — cassée, il n'écrit rien."""
    gabarit = lambda nom: pathlib.Path(os.path.join(ICI, "..", "templates", nom)).read_text(encoding="utf-8")

    def empreinte(racine):
        return {os.path.join(r, f): hashlib.sha256(pathlib.Path(os.path.join(r, f)).read_bytes()).hexdigest()
                for r, _, fs in os.walk(racine) for f in fs}

    for saine in (False, True):
        with tempfile.TemporaryDirectory(dir=tmp_path) as te:
            ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : U (test).\n")
            rang = "| 3 | Trois | a | 2 fiches | — |" if saine else "| 3 | Trois | a | b | 2 fiches | — |"
            ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé "
                   "| Dépend de |\n|---|---|---|---|---|\n%s\n\n## Journal\n" % rang)
            ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(te, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
            ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
            avant = empreinte(te)
            code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-10-09"])
            if saine:
                assert code == 0
                assert "CLOS U " in s
                assert "\nLIRE vlp.css vlp.js\n" in s
                assert not os.path.exists(os.path.join(te, "ctx", "artefacts", "couts.svg"))
            else:
                assert code == 1
                assert s.startswith("GARDE: ligne 3 de la TODO : 6 cellules au lieu de 5")
                assert "rien écrit" in s
                assert empreinte(te) == avant


def test_clore_ote_todo(tmp_path):
    """RTO1 : `clore` ôte la rangée du chantier de la TODO et marque la provenance, sans toucher au journal ;
    un code absent de la TODO n'écrit rien au fichier d'état, et ce n'est pas une GARDE."""
    gabarit = lambda nom: pathlib.Path(os.path.join(ICI, "..", "templates", nom)).read_text(encoding="utf-8")
    journal = "## Journal des décisions\n\n## 2026-10-01 — x\n"
    for present in (True, False):
        with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
            ecrire(os.path.join(tr, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : A (test).\n")
            rangs = ("| 3 | `U` — u | a | 2 fiches | — |\n" if present else "") + "| 4 | `AAA` — a | a | 1 | — |\n"
            etat = ("# État\n\nProvenance : 3, de x ; 4, de y.\n\n| # | Chantier | Ce qu'il apporte | Coût estimé "
                    "| Dépend de |\n|---|---|---|---|---|\n%s\n%s" % (rangs, journal))
            chemin = os.path.join(tr, "ctx", "08-etat.md")
            ecrire(chemin, etat)
            ecrire(os.path.join(tr, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(tr, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
            ecrire(os.path.join(tr, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
            code, s = appel(["clore", tr, "--livre", "fini", "--date", "2026-10-09"])
            lu = pathlib.Path(chemin).read_text(encoding="utf-8")
            if present:
                assert code == 0
                assert "| 3 | `U`" not in lu
                assert "| 4 | `AAA`" in lu
                assert "Provenance : 3, de x ; 4, de y. 3, `U`, clos le 2026-10-09.\n" in lu
                assert lu.endswith(journal)
                assert "TODO `U` ôtée · n° 3\n" in s
                assert "CLOS U " in s
            else:
                assert code == 0
                assert "TODO `U` absente — rien ôté\n" in s
                assert lu == etat
                assert "CLOS U " in s


def test_clore_reperes_et_routage():
    """Dette SCH (Cairn, 2026-10-14) : une rangée de TODO dont le code suit des repères (🔴📅) se trouve, un code
    cité plus loin dans la ligne non ; une ligne « relire un chantier clos — … » prolongée compte comme présente."""
    todo = ["| # | Chantier | a | b | c |", "|---|---|---|---|---|", "| 1 | 🔴📅 `SCH` — x | a | b | — |",
            "| 2 | 🟡💤 ⏸️ `HD` — y | voir `REG` | b | — |", "| 3 | `REG` — z | a | b | — |"]
    assert mod.rangee_todo(todo, "SCH") == (0, 2, "1")
    assert mod.rangee_todo(todo, "HD") == (0, 3, "2")
    assert mod.rangee_todo(todo, "REG") == (0, 4, "3")
    assert mod.rangee_todo(todo, "SC") == (0, None, None)
    cl = ["| T | O |", "|---|---|", "| relire un chantier clos — filet de tests | `ctx/00-INDEX-archive.md` |"]
    assert mod.rang_routage_clos(cl) == 2
    assert mod.rang_routage_clos(["| relire un chantier clos | x |"]) == 0
    assert mod.rang_routage_clos(["| relire un chantier closes | x |"]) is None
    vieux = ["| T | O |", "| relire le chantier E (e) | x |"]
    assert mod.rang_routage_clos(vieux, "| relire le chantier") == 1
    assert mod.rang_routage_clos(vieux) is None
    assert mod.rang_routage_clos(cl, "| relire le chantier") == 2


def test_oter(tmp_path):
    """TAB4 : `vlp.py oter` retire une rangée de la TODO, marque son numéro, l'écrit au journal ; refuse un code
    absent, ouvert ou clos sans rien écrire."""
    etat = ("# État\n\n## La TODO\n\nProvenance : 3, de x ; 4, de y.\n\n"
            "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
            "| 3 | `AAA` — a | x | 1 | — |\n| 4 | `BBB` — b | x | 1 | — |\n| 5 | `U` — u | x | 1 | — |\n"
            "| 6 | `OUV` — o | x | 1 | — |\n\n## Journal des décisions\n\n## 2026-10-01 — x\n")
    with tempfile.TemporaryDirectory(dir=tmp_path) as to:
        ecrire(os.path.join(to, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n\n"
               "Lettres de fiche déjà prises : U (test). Un nouveau chantier en choisit un autre.\n")
        ecrire(os.path.join(to, "ctx", "50-ouv.md"), ouvert("# Chantier OUV — o\n\n## OUV1 [ ] — a\n"))
        chemin = os.path.join(to, "ctx", "08-etat.md")
        ecrire(chemin, etat)
        for code, quoi in (("ZZZ", "absent"), ("OUV", "ouvert"), ("U", "clos")):
            res = appel(["oter", to, code, "--raison", "r", "--date", "2026-10-09"])
            assert res[0] == 1
            assert res[1].startswith("GARDE: ")
            assert "rien écrit" in res[1]
            assert pathlib.Path(chemin).read_text(encoding="utf-8") == etat
        res = appel(["oter", to, "AAA", "--raison", "fait ailleurs", "--date", "2026-10-09"])
        lu = pathlib.Path(chemin).read_text(encoding="utf-8")
        assert res[0] == 0
        assert "| 3 | `AAA`" not in lu
        assert "| 4 | `BBB`" in lu
        assert len(mod.todo_du_fichier(lu.split("\n"))) == 3
        assert ("Provenance : 3, de x ; 4, de y. 3, `AAA`, retiré le 2026-10-09 : fait ailleurs.\n" in lu), ("TAB4 : oter marque le numéro retiré dans la phrase de provenance") + "\n" + str(lu)
        assert (lu.endswith("## 2026-10-01 — x\n\n## 2026-10-09 — `AAA` retiré de la TODO (n° 3)\n\n"
                             "- **Raison** : fait ailleurs.\n")), ("TAB4 : oter écrit une entrée datée au journal") + "\n" + str(lu)
        res = appel(["oter", to, "BBB", "--raison", "fait cette nuit", "--date", "2026-10-12", "--fait"])
        lu, carte_ = pathlib.Path(chemin).read_text(encoding="utf-8"), pathlib.Path(os.path.join(to, "CHANTIER.md")).read_text(encoding="utf-8")
        prises = mod.lettres_prises(carte_.split("\n"))
        assert res[0] == 0
        assert res[1].rstrip().endswith("· lettre prise")
        assert "U (test), BBB (b, sans fiche). Un nouveau chantier" in carte_
        assert not mod.est_bloque("`BBB`", prises, [])
        assert "4, `BBB`, fait sans fiche le 2026-10-12 : fait cette nuit.\n" in lu
        assert "## 2026-10-12 — `BBB` fait sans fiche, retiré de la TODO (n° 4)\n" in lu


def test_todo_sans_code_rangee():
    """Dette FIN : dans une TODO sans codes, `rangee_todo` trouve une rangée par son numéro exact ou par le titre du
    chantier, à l'apostrophe et aux espaces près ; un titre en double ou un code seul ne trouvent rien."""
    todo = ["| # | Chantier | a | b | c |", "|---|---|---|---|---|", "| 10 | Finitions de l'API : erreurs et Swagger | a | b | — |",
            "| 11 | Réparer le banc | a | b | — |", "| 12 | Réparer le banc | a | b | — |"]
    assert mod.rangee_todo(todo, "11") == (0, 3, "11")
    assert mod.rangee_todo(todo, "1") == (0, None, None)
    assert mod.rangee_todo(todo, "FIN", "finitions de l’API :  erreurs et Swagger") == (0, 2, "10")
    assert mod.rangee_todo(todo, "BAN", "Réparer le banc") == (0, None, None)
    assert mod.rangee_todo(todo, "FIN") == (0, None, None)


def test_todo_sans_code(tmp_path, monkeypatch):
    """Dette FIN (Fil-Rouge, 2026-10-14) : une TODO sans codes (`| 10 | Finitions … |`) — `clore` trouve la rangée par
    le titre du chantier, `oter` par son numéro ; un routage sans « relire un chantier clos » ni « relire le
    chantier », mais des lignes **clos** : `ouvrir` y pose sa ligne, que `clore` retrouve."""
    gabarit = lambda nom: pathlib.Path(os.path.join(ICI, "..", "templates", nom)).read_text(encoding="utf-8")
    lire = lambda c: pathlib.Path(c).read_text(encoding="utf-8")
    etat =("# État\n\nProvenance : 10, de x ; 11, de y.\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
            "|---|---|---|---|---|\n| 10 | Finitions de l'API : erreurs et Swagger | a | 1 | `DRO` |\n"
            "| 11 | Réparer le banc | a | 1 | rien |\n| 12 | Seed | a | 1 | 10..11 |\n\n## Journal des décisions\n\n## 2026-10-01 — x\n")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tf:
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
        carte_f = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
                   "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : DRO (droits).\n")
        ecrire(os.path.join(tf, "CHANTIER.md"), carte_f)
        ecrire(os.path.join(tf, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `12-dro.md` | on relit |\n")
        routage = ("| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n"
                   "| relire une fiche `DRO1` à `DRO2` | `ctx/12-dro.md` — chantier **clos** le 2026-10-13 |\n| reprendre | y |\n")
        ecrire(os.path.join(tf, "CLAUDE.md"), routage)
        chemin = os.path.join(tf, "ctx", "08-etat.md")
        ecrire(chemin, etat)
        ecrire(os.path.join(tf, "ctx", "13-fin.md"), "# Chantier FIN — Finitions de l'API : erreurs et Swagger\n\n"
               "**Fait.** Rien.\n\n## FIN1 [x] — a\n")
        ecrire(os.path.join(tf, "ctx", "artefacts", "13-fin.html"), gabarit("artefact-chantier.html"))
        ecrire(os.path.join(tf, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
        code, s = appel(["ouvrir", tf, "--fiches", "ctx/13-fin.md", "--titre", "Finitions de l'API : erreurs et Swagger"])
        assert code == 0
        assert "routage +1" in s
        assert "GARDE" not in s
        assert ("| modifier | x |\n| jouer une fiche du chantier FIN "
                 "(finitions de l'API : erreurs et Swagger) | `ctx/13-fin.md` — chantier **ouvert**, par `/vlp:tache FIN<n>` |\n"
                 "| relire une fiche `DRO1`" in lire(os.path.join(tf, "CLAUDE.md")))
        for code_, quoi in (("10", "ouvert, trouvé par son titre"), ("99", "absent")):
            res = appel(["oter", tf, code_, "--raison", "r", "--date", "2026-10-14"])
            assert res[0] == 1
            assert res[1].startswith("GARDE: ")
            assert lire(chemin) == etat
        res = appel(["oter", tf, "11", "--raison", "fait à la main", "--date", "2026-10-14", "--fait"])
        lu = lire(chemin)
        assert res[0] == 0
        assert "| 11 |" not in lu
        assert "| 10 |" in lu
        assert "| 12 |" in lu
        assert "11, « Réparer le banc », fait sans fiche le 2026-10-14 : fait à la main.\n" in lu
        assert "## 2026-10-14 — « Réparer le banc » fait sans fiche, retiré de la TODO (n° 11)\n" in lu
        assert lire(os.path.join(tf, "CHANTIER.md")) == carte_f
        assert "lettre prise" not in res[1]
        code, s = appel(["clore", tf, "--livre", "fini", "--date", "2026-10-14"])
        lu, claude_lu = lire(chemin), lire(os.path.join(tf, "CLAUDE.md"))
        assert code == 0
        assert "TODO `FIN` ôtée · n° 10\n" in s
        assert "| 10 |" not in lu
        assert "| 12 | Seed" in lu
        assert "10, `FIN`, clos le 2026-10-14." in lu
        assert "routage 1" in s
        assert "jouer une fiche" not in claude_lu
        assert "ligne « jouer une fiche" not in s


def _tester_bilan_md_clore(page_q):
    """Dans une fonction : au niveau du module, pyright jugeait le fichier trop complexe (ABR3)."""
    bilan_md = mod.lire_abri(mod.chemin_abri(page_q))["bilan"]
    assert (bilan_md == ["Livré : Livré `a` <b>", "Surpris : x < y",
                          "Estimé : estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $"])
    assert "\x00" not in "\n".join(bilan_md)


CARTE_FEUILLE = ("# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
                 "- **artefact du chantier** : %s\n\n"
                 "Lettres de fiche déjà prises : E (Un), M (Deux `x`). Un nouveau chantier en choisit une autre.\n")


Q_FERME = "# Chantier Q — Un titre\n\n## Q1 [x] — a\n## Q2 [ ] — b\n"


def decor_feuille(t):
    """Pose dans `t` une carte sans chantier, une TODO de deux rangs, `ctx/30-q.md` fermé et la feuille de route du
    gabarit ; rend le chemin de la feuille."""
    ecrire(os.path.join(t, "CHANTIER.md"), CARTE_FEUILLE % "aucun")
    ecrire(os.path.join(t, "ctx", "08-etat.md"),
           "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
           "| 3 | Le `sh` | a \\|\\| b <c> | 2 fiches | — |\n| 4 | Quatre | rien | 1 fiche | 3 |\n\n## Journal\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), Q_FERME)
    fdr = os.path.join(t, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(fdr, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8"))
    return fdr


def feuille_fermee(t):
    """Le départ de `test_feuille_clore_encours` : `decor_feuille`, puis les appels de `feuille` de
    `test_feuille_clore` rejoués sans rien vérifier ; rend le chemin de la feuille."""
    fdr = decor_feuille(t)
    appel(["feuille", t, "--date", "2026-01-02"])
    appel(["feuille", t, "--date", "2026-03-04"])
    ecrire(fdr, mod.RESUME_TODO.sub("", lire_texte(fdr)))
    appel(["feuille", t, "--date", "2026-01-02"])
    return fdr


def feuille_rejouee(t):
    """Le départ de `clore_q` : `feuille_fermee`, puis les appels de `feuille` de `test_feuille_clore_encours` rejoués
    sans rien vérifier — la feuille ouverte au rang 4, puis refermée ; rend le chemin de la feuille."""
    fdr = feuille_fermee(t)
    ecrire(os.path.join(t, "CHANTIER.md"), CARTE_FEUILLE % "https://exemple/q")
    ecrire(os.path.join(t, "ctx", "30-q.md"), ouvert(Q_FERME))
    for argv in (["--verifier"], ["--todo", "4", "--date", "2026-03-04"], [], ["--verifier"], ["--todo", "9"]):
        appel(["feuille", t, *argv])
    ecrire(os.path.join(t, "CHANTIER.md"), CARTE_FEUILLE % "aucun")
    ecrire(os.path.join(t, "ctx", "30-q.md"), Q_FERME)
    appel(["feuille", t])
    return fdr


def test_feuille_clore(tmp_path):
    """Contrôler `feuille` sans chantier ouvert : feuille fermée, inchangée relancée, résumé de la TODO remis (FEU)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        fdr = decor_feuille(t)
        code, s = appel(["feuille", t, "--date", "2026-01-02"])
        html = lire(fdr)
        assert code == 0
        assert "FEUILLE todo 2 · encours non · lettres 2 · réécrite" in s
        assert "Aucun chantier ouvert" in html
        assert '<span class="mono">E, M</span>' in html
        assert '<span class="mono">2026-01-02</span>' in html
        assert ('<span class="gauche"><span class="rang mono">3</span></span><details><summary>'
                 '<span class="titre">Le <span class="mono">sh</span></span></summary><div class="detail">a || b &lt;c&gt;</div>'
                 '</details><span class="meta"><span class="seg">2 fiches</span></span></li>' in html)
        assert "&lt;U, R&gt;" not in html
        assert 'data-etat="cours"' not in html.split("ZONE:todo")[1]
        avant_todo = html.split("<!-- ZONE:todo")[0].split("Les chantiers possibles")[1]
        assert avant_todo.count("resume-todo") == 1
        assert "><strong>2 chantiers possibles</strong> · 1 petit, 1 moyen · 1 bloqué · ≈3 fiches estimées</p>" in avant_todo
        assert "&lt;n&gt; chantiers possibles" not in html
        code, s = appel(["feuille", t, "--date", "2026-03-04"])
        assert code == 0
        assert "inchangée" in s
        assert "2026-01-02" in lire(fdr)
        ecrire(fdr, mod.RESUME_TODO.sub("", lire(fdr)))
        code, s = appel(["feuille", t, "--date", "2026-01-02"])
        assert code == 0
        assert lire(fdr).count("resume-todo") == 1
        assert ("><strong>2 chantiers possibles</strong> · 1 petit, 1 moyen · 1 bloqué · ≈3 fiches estimées</p>\n    <!-- ZONE:todo"
                      in lire(fdr))
        assert mod.resume_todo(1) == "1 chantier possible"
        assert mod.resume_todo(0) == "aucun chantier possible"


def test_feuille_clore_encours(tmp_path):
    """Contrôler `feuille` avec un chantier ouvert : `--verifier` voit l'écart, `--todo` marque le rang en cours ;
    refermée sans chantier (FEU)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        fdr = feuille_fermee(t)
        carte_, q_ferme = CARTE_FEUILLE, Q_FERME
        ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "https://exemple/q")
        ecrire(os.path.join(t, "ctx", "30-q.md"), ouvert(q_ferme))
        code, s = appel(["feuille", t, "--verifier"])
        assert code == 1
        assert "écart" in s
        assert "Aucun chantier" in lire(fdr)
        code, s = appel(["feuille", t, "--todo", "4", "--date", "2026-03-04"])
        html = lire(fdr)
        assert code == 0
        assert "encours oui · lettres 3" in s
        assert 'Un titre <span class="badge" data-etat="cours">' in html
        assert '<span class="mono">Q1–Q2</span>' in html
        assert 'href="https://exemple/q"' in html
        assert "E, M, Q" in html
        assert (('<span class="rang mono">4</span>' + mod.BADGE_COURS + '<span class="dep mono">← 3</span></span>'
                      '<details><summary><span class="titre">Quatre</span></summary>') in html)
        code, s = appel(["feuille", t])
        assert code == 0
        assert "inchangée" in s
        assert (appel(["feuille", t, "--verifier"])[0] == 0), ("feuille : --verifier identique") + "\n" + str(appel(["feuille", t, "--verifier"]))
        code, s = appel(["feuille", t, "--todo", "9"])
        assert code == 1
        assert s.startswith("GARDE:")
        ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "aucun")
        ecrire(os.path.join(t, "ctx", "30-q.md"), q_ferme)
        code, s = appel(["feuille", t])
        html = lire(fdr)
        assert code == 0
        assert "Aucun chantier ouvert" in html
        assert 'data-etat="cours"' not in html.split("ZONE:encours")[1]
        assert "E, M</span>" in html


def clore_q(t):
    """Le chantier Q clos par `clore`, sur la feuille de `feuille_rejouee` augmentée d'un clos E, d'un index, d'un
    `CLAUDE.md` et d'une page au blocage visible ; rend (code, sortie, chemin de la feuille, chemin de la page)."""
    lire = lire_texte
    fdr = feuille_rejouee(t)
    carte_ = CARTE_FEUILLE
    ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "https://exemple/q"
           + "\n| Fichier de fiches | Fiches | Clos le | Artefact |\n|---|---|---|---|\n| ctx/10-e.md | E1..E2 | 2026-01-01 | u |\n\nFin.\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un `titre`\n\n" + OUVERT + "\n\n**À quoi il sert.** x\n\n**Estimé.** 2 fiches · ≈0,40 $ — ≈0,20 $/fiche sur 3 clos (le 2026-05-01).\n\n**Fait.** Rien.\n\n## Q1 [x] — a\n## Q2 [ ] — b\n")
    html = lire(fdr)
    for gabarit, vrai in (('&lt;≈2,3k (2 312)&gt;', "≈2,3k (2 312)"), ('&lt;≈15,3k (15 342)&gt;', "?"), ("&lt;une ligne&gt;", "ligne &lt;python&gt;"),
                          ('<a href="&lt;URL de son artefact&gt;">&lt;nom&gt;</a>', '<a href="u">E</a>'), ("&lt;U1..U6&gt;", "E1–E2"),
                          ("&lt;AAAA-MM-JJ&gt;", "2026-01-01")):
        html = html.replace(gabarit, vrai)
    ecrire(fdr, html)
    ecrire(os.path.join(t, "CHANTIER.md"), lire(os.path.join(t, "CHANTIER.md")) + "- **index** : ctx/00-INDEX.md\n")
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un (vrai) titre », `Q1..Q2` |\n")
    ecrire(os.path.join(t, "CLAUDE.md"), "# P\n\n## Où on en est\n\n- Clos le 2026-05-06 : a (chantier E).\n\n## Routage\n\n| T | O |\n|---|---|\n| jouer une fiche du chantier Q (un (vrai) titre) | `ctx/30-q.md` — chantier **ouvert**, par `/vlp:tache Q<n>` |\n| relire le chantier E (e) | `ctx/10-e.md` — chantier **clos** |\n")
    page_q = os.path.join(t, "ctx", "artefacts", "30-q.html")
    ecrire(page_q, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-chantier.html")).read_text(encoding="utf-8")
           .replace("<!-- ZONE:blocage — publiée quand /tache s'arrête après deux tentatives ; retirée dès que la fiche repasse -->\n  <section hidden>",
                    "<!-- ZONE:blocage — publiée quand /tache s'arrête après deux tentatives ; retirée dès que la fiche repasse -->\n  <section>"))
    assert page_q
    assert "<!-- ZONE:blocage" in lire(page_q)
    assert lire(page_q).count("<section hidden>") == 1
    code, s = appel(["clore", t, "--livre", "Livré `a` <b>", "--tokens", "1500", "--abandon", "Q2 abandonnée", "--date", "2026-05-06", "--surpris", "x < y", "--resume", "b `c`."])
    return code, s, fdr, page_q


def test_feuille_clore_clore(tmp_path):
    """Contrôler `clore` : sa sortie, le résumé de `CLAUDE.md`, les fiches, l'index et l'archive, la carte ; relancé
    sans chantier ouvert, une GARDE (FEU)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        code, s, fdr, _page_q = clore_q(t)
        carte_lue, fiches_lues = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "30-q.md"))
        assert "· routage 1 · index 1 · archivé 1 · bilan 1 · résumé 1 ·" in s
        assert "GARDE" not in s
        assert "\nLIRE vlp.css vlp.js couts.svg\n" in s
        assert os.path.exists(os.path.join(os.path.dirname(fdr), "couts.svg"))
        assert ("- Clos le 2026-05-06 : a (chantier E).\n- Clos le 2026-05-06 : b `c` (chantier Q).\n\n## Routage" in lire(os.path.join(t, "CLAUDE.md"))), ("clore : résumé, une ligne par clos") + "\n" + str(lire(os.path.join(t, "CLAUDE.md")))
        assert "**Fait.** Q1..Q2 (2026-05-06) : Livré `a` <b> — estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $.\n" in fiches_lues
        assert "**Fait.** Rien." not in fiches_lues
        ligne_q = "| `30-q.md` | on relit le socle du chantier Q — **clos** « Un (vrai) titre », `Q1..Q2` |\n"
        assert lire(os.path.join(t, "ctx", "00-INDEX.md")).split("---|\n")[1].startswith("| `00-INDEX-archive.md` |")
        assert "**clos**" not in lire(os.path.join(t, "ctx", "00-INDEX.md"))
        assert lire(os.path.join(t, "ctx", "00-INDEX-archive.md")).split("---|\n")[1] == ligne_q
        assert "|---|---|\n| relire un chantier clos | `ctx/00-INDEX-archive.md` — sa ligne y nomme le fichier de fiches |\n| relire le chantier E" in lire(os.path.join(t, "CLAUDE.md"))
        assert "chantier Q" not in lire(os.path.join(t, "CLAUDE.md")).split("## Routage")[1]
        assert code == 0
        assert "CLOS Q Q1..Q2 (Q2 abandonnée) · chantier 1 500 · cumul 3 812 · routage 1 · index 1 · archivé 1 · bilan 1 · résumé 1 · estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $ — " in s
        assert "encours non" in s
        assert "**CLOS** le 2026-05-06. Ne se rejoue pas" in fiches_lues
        assert fiches_lues.index("**CLOS**") < fiches_lues.index("**Fait.**")
        assert "Abandonnées : Q2 abandonnée." in fiches_lues
        assert "**artefact du chantier** : aucun" in carte_lue
        assert "| ctx/10-e.md | E1..E2 | 2026-01-01 | u |\n\nFin." in carte_lue
        assert "| ctx/30-q.md |" not in carte_lue
        assert "M (Deux `x`), Q (Un `titre`). Un nouveau chantier" in carte_lue
        code, s = appel(["clore", t, "--livre", "x"])
        assert code == 1
        assert s.startswith("GARDE: aucun chantier ouvert")
        assert lire(os.path.join(t, "CHANTIER.md")) == carte_lue


def test_feuille_clore_page(tmp_path):
    """Contrôler `clore` : la page du chantier (bilan, blocage replié, fiches) et la zone des clos de la feuille (FEU)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        _code, _s, fdr, page_q = clore_q(t)
        html = lire(fdr)
        pq = lire(page_q)
        assert "<section>\n    <h2>Chantier clos le 2026-05-06</h2>\n    <div class=\"bilan\">\n      <p>Livré : Livré `a` &lt;b&gt;</p>\n      <p>Surpris : x &lt; y</p>\n      <p>Estimé : estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $</p>\n    </div>\n  </section>" in pq
        assert pq.split("<!-- ZONE:blocage")[1].split("-->\n")[1].startswith("  <section hidden>")
        assert pq.count("<section hidden>") == 1
        assert '<span class="id">Q1</span>' in pq
        assert '<span class="id">Q2</span>' in pq
        assert '<span class="id">&lt;R' not in pq
        assert '<p class="mono cout-total">' not in pq
        _tester_bilan_md_clore(page_q)
        clos = html.split("<!-- ZONE:clos")[1]
        assert '<a href="https://exemple/q">Un <span class="mono">titre</span></a>' in clos
        assert '<td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>' in clos
        assert "≈1,5k (1 500)" in clos
        assert "Livré <span class=\"mono\">a</span> &lt;b&gt;" in clos
        assert clos.index("Q1–Q2") < clos.index("2 312", clos.index("<tbody>"))
        assert "<strong>≈3,8k (3 812)</strong>" in clos
        assert "Aucun chantier ouvert" in html
        assert "E, M, Q</span>" in html
        assert ('<strong>≈3,8k (3 812)</strong></td><td class="mono"></td>' in clos), ("clore : pied de table sans $ — aucune ligne n'a de prix mesuré (chantier TAU)") + "\n" + str(clos)
        assert ('<span class="resume-clos">2 chantiers clos · ≈3,8k (3 812) tokens · coût non mesuré</span>' in clos), ("clore : résumé du bloc repliable des clos, coût non mesuré") + "\n" + str(clos)
        assert '<details class="clos">' in clos
        assert "</details>" in clos


def test_resume_claude():
    """`resume_claude` : une ligne « Clos le » par clos sous « Où on en est », cinq gardées au plus, une ligne sur
    plusieurs repliée, une GARDE sans la section (FEU)."""
    cl, gr = ["## Où on en est", "", "- Clos le 2026-01-01 : a (chantier E).", "", "## Règles"], []
    assert mod.resume_claude(cl, "Q", "b", "2026-02-02", gr)
    assert cl[3] == "- Clos le 2026-02-02 : b (chantier Q)."
    assert cl[2].endswith("E).")
    assert not gr
    cl2 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."]
    assert mod.resume_claude(cl2, "Q", "b (chantier Q).", "2026-01-01", gr)
    assert cl2[-1] == "- Clos le 2026-01-01 : b (chantier Q)."
    cl5 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."]
    assert mod.resume_claude(cl5, "Q", "Clos le 2026-09-27 : b.", "2026-09-27", gr)
    assert cl5[-1] == "- Clos le 2026-09-27 : b (chantier Q)."
    assert not mod.resume_claude(cl, "Q", "b", "2026-02-02", gr)
    assert len(cl) == 6
    cl3 = ["## Où on en est", "- Prouvé : x.", "  puis vieux (chantier A) ;"] + ["- Clos le 2026-01-0%d : c%d (chantier %s)." % (i, i, "BCDEF"[i - 1]) for i in range(1, 6)] + ["", "## R"]
    assert mod.resume_claude(cl3, "G", "g", "2026-01-09", gr)
    assert mod.CLOS_GARDES == 5
    assert not any("(chantier B)" in l for l in cl3)
    assert cl3[:3] == ["## Où on en est", "- Prouvé : x.", "  puis vieux (chantier A) ;"]
    assert sum(1 for l in cl3 if l.startswith("- Clos le")) == 5
    assert cl3[-3] == "- Clos le 2026-01-09 : g (chantier G)."
    assert not mod.resume_claude(["# x"], "Q", "b", "d", gr)
    assert gr
    assert "Où on en est" in gr[0]
    cl4, g4 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."], []
    assert mod.resume_claude(cl4, "Q", "deux lignes\nici.\n", "2026-09-24", g4)
    assert cl4[-1] == "- Clos le 2026-09-24 : deux lignes ici (chantier Q)."
    assert bool(mod.ENTREE_CLOS.match(cl4[-1]))
    assert not g4


OUVERT_DU_JOUR = mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat()


def test_apc3(tmp_path, init_git):
    """APC3, et la dette PLI : page d'un clos s'arrête à clore, comme cout."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj, s3 = os.path.join(t, "apc3"), os.path.join(t, "s3.jsonl")
        transcript(s3, 3, [T0 + 200, T0 + 400, T0 + 700])
        lignes_ = [json.loads(l) for l in lire(s3).splitlines()]
        lignes_[2]["message"]["content"] = [{"type": "tool_use", "id": "t2", "name": "Bash",
                                             "input": {"command": 'py "C:/k/scripts/vlp.py" clore . --livre x'}}]
        ecrire(s3, "".join(json.dumps(l) + "\n" for l in lignes_))
        ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : https://u\n\n"
               "Lettres de fiche déjà prises : Q (test).\n")
        ecrire(os.path.join(proj, "ctx", "q.md"), ouvert(QFICHES % (s3, s3)))
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `q.md` | on joue `Q*` — **ouvert** |\n")
        ecrire(os.path.join(proj, "CLAUDE.md"), "| T | O |\n|---|---|\n| jouer Q | `ctx/q.md` **ouvert** |\n")
        ecrire(os.path.join(proj, "ctx", "artefacts", "q.html"),
               pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-chantier.html")).read_text(encoding="utf-8"))
        if not shutil.which("git"):
            pytest.skip("git absent — clore = recompte n'est pas testé")
        else:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            init_git(proj)

            def commit_(d, sujet):
                date = "%d +0000" % (T0 + d)
                subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=proj, check=True,
                               capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
            for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
                commit_(d, sujet)
            code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "1", "--date", "2026-09-25"])
            with open(s3, "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(lignes_[0], requestId="r9", timestamp=datetime.datetime.fromtimestamp(
                    T0 + 800, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    message=dict(lignes_[0]["message"], id="m9"))) + "\n")
            commit_(900, "Chantier Q clos : fini")
            code2, s2 = appel(["cout", os.path.join(proj, "ctx", "q.md")])
            assert code == 0
            assert code2 == 0
            assert "chantier 300 000" in s
            assert "**CLOS**" in lire(os.path.join(proj, "ctx", "q.md"))
            assert "\nTOTAL (fiches + hors fiches) · ≈300,0k (300 000) · 3 tours" in s2
            code3, _ = appel(["page", os.path.join(proj, "ctx", "q.md"), os.path.join(proj, "ctx", "artefacts", "q.html")])
            assert code3 == 0
            assert ("Coût du chantier : ≈300,0k (300 000) · 3 tours"
                     in lire(os.path.join(proj, "ctx", "artefacts", "q.html")))


GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


def test_uni1_total(tmp_path):
    """Contrôler que `clore` utilise le total mesuré, et `--tokens` sans mesure (UNI1)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "uni")
        os.makedirs(proj)
        ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : https://u\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "50-u.md"), ouvert("# Chantier U — test\n\n## U1 [x] — a\n"))
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `50-u.md` | on joue `U*` |\n")
        ecrire(os.path.join(proj, "CLAUDE.md"), "| T | O |\n|---|---|\n| jouer U | `ctx/50-u.md` **ouvert** |\n| relire un clos | `ctx/00-INDEX.md` |\n")
        page_u = os.path.join(proj, "ctx", "artefacts", "50-u.html")
        ecrire(page_u, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-chantier.html")).read_text(encoding="utf-8"))
        code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "950", "--date", "2026-09-25"])
        assert code == 0
        assert "chantier 950" in s
        assert "ÉCART" not in s

    # UNI1 : mesuré, le total de la page gagne sur un --tokens faux, et le dit
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "uni2")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
        ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : https://u\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "50-u.md"), ouvert("# Chantier U — test\n\n## U1 [x] — a\n"))
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `50-u.md` | on joue `U*` |\n")
        ecrire(os.path.join(proj, "CLAUDE.md"), "| T | O |\n|---|---|\n| jouer U | `ctx/50-u.md` **ouvert** |\n| relire un clos | `ctx/00-INDEX.md` |\n")
        ecrire(os.path.join(proj, "ctx", "artefacts", "50-u.html"),
               pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-chantier.html")).read_text(encoding="utf-8"))
        feuille_u = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(feuille_u, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8"))
        regenerer_vrai = mod.noyau.page.regenerer
        def regenerer_faux(*x):
            r = regenerer_vrai(*x)
            return r[:3] + ((4321, 3, None), r[4])
        mod.noyau.page.regenerer = regenerer_faux
        try:
            code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "950", "--date", "2026-09-25"])
        finally:
            mod.noyau.page.regenerer = regenerer_vrai
        fu = pathlib.Path(feuille_u).read_text(encoding="utf-8")
        assert code == 0
        assert "ÉCART tokens 950 donné · 4 321 mesuré — le mesuré fait foi" in s
        assert "· chantier 4 321 ·" in s
        assert "(4 321)" in fu
        assert ">950<" not in fu


JOUR_MATIN = "2026-10-01"


CARTE_MATIN = ("# Chantier courant\n\n- **alias** : mt\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact feuille de route** : https://claude.ai/artifact/FEU\n"
               "- **artefact du chantier** : https://claude.ai/artifact/LOC\n- **artefact archive** : aucune\n\n"
               "Lettres de fiche déjà prises : E (Enchaîner), ENQ (Les écritures Git). "
               "Un nouveau chantier en choisit un autre.\n")


ETAT_MATIN = ("# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
              "| 79 | `LOC` — publier | a | 2 fiches | — |\n| 80 | `PAR` — deux chantiers | b | 3 fiches | — |\n\n"
              "## Journal\n")


def git_matin(d, *args):
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace", check=False)
    if r.returncode:
        raise RuntimeError("git %s : %s" % (" ".join(args), r.stderr))
    return r.stdout


def commit_matin(d, message, heure):
    """Un commit à `heure` (0 à 23) du jour de la nuit : la date de l'auteur et du commiteur est fixée."""
    os.environ["GIT_AUTHOR_DATE"] = os.environ["GIT_COMMITTER_DATE"] = "%sT%02d:00:00+00:00" % (JOUR_MATIN, heure)
    git_matin(d, "add", "-A")
    git_matin(d, "commit", "-q", "-m", message)


def depot_matin(init_git, d, archive=True, etat=ETAT_MATIN):
    """Le dépôt de 2cef70f : `main` à courant LOC et son artefact, des lettres jusqu'à ENQ, une archive de deux clos
    (`archive` faux : ils restent sur la feuille), la feuille au rang 79 — un seul commit, à l'heure 0."""
    os.makedirs(d)
    init_git(d)
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
    ecrire(os.path.join(d, "ctx", "08-etat.md"), etat)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n")
    ecrire(os.path.join(d, "ctx", "40-loc.md"), ouvert_ligne("# Chantier LOC — Publier\n\n## LOC1 [ ] — a\n"))
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 2\nc = 3\n")
    gabarit = lire(GABARIT_FEUILLE)
    debut, fin = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
    deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
            + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
    ecrire(os.path.join(d, "ctx", "artefacts", "feuille-de-route.html"),
           mod.resommer(gabarit[:debut] + deux + gabarit[fin:], 2, 70000))
    if archive:
        appel(["archive", d, "--url", "https://claude.ai/artifact/ARCH"])
    appel(["feuille", d, "--todo", "79", "--date", "2026-09-30"])
    commit_matin(d, "base", 0)


def test_ouverts(tmp_path, init_git):
    """NUI21 : `ouverts` — la marque d'ouverture, sans CLOS ni Pause ; `--rev` lit un commit, pas l'arbre."""
    if not shutil.which("git"):
        pytest.skip("git absent — ouverts n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d = os.path.join(tr, "ou")
        os.makedirs(d)
        ecrire(os.path.join(d, "CHANTIER.md"), "- **alias** : ou\n- **contexte** : ctx/\n")
        for n in ("a", "b", "c"):
            ecrire(os.path.join(d, "ctx", n + ".md"), "# Chantier %s — x\n\n## %s1 [ ] — f\n" % (n.upper(), n.upper()))
        code0, s0 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT_LIGNE % "2026-10-03" + "\n\n## B1 [ ] — f\n")
        code1, s1 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT_LIGNE % "2026-10-03" + "\n" + mod.CLOS_LIGNE % "2026-10-04" + "\n")
        code2, s2 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT_LIGNE % "2026-10-03" + "\n" + mod.PAUSE_LIGNE % ("2026-10-04", "attend") + "\n")
        code3, s3 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT_LIGNE % "2026-10-03" + "\n")
        init_git(d)
        git_matin(d, "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
        git_matin(d, "checkout", "-q", "-b", "autre")
        ecrire(os.path.join(d, "ctx", "c.md"), "# Chantier C — x\n\n" + OUVERT_LIGNE % "2026-10-03" + "\n")
        git_matin(d, "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c ouvert")
        code4, s4 = appel(["ouverts", d, "--rev", "main"])
        code5, s5 = appel(["ouverts", d, "--rev", "autre"])
        code6, s6 = appel(["ouverts", d])
        code7, s7 = appel(["ouverts", d, "--rev", "nexistepas"])
        git_matin(d, "checkout", "-q", "main")
        code8, s8 = appel(["ouverts", os.path.join(tr, "vide")])
    assert (code0, s0) == (0, "OUVERTS=0\n")
    assert s1 == "OUVERT ctx/b.md\n"
    assert s2 == "OUVERTS=0\n"
    assert s3 == "OUVERTS=0\n"
    assert s4 == "OUVERT ctx/b.md\n"
    assert s5 == "OUVERT ctx/b.md\nOUVERT ctx/c.md\n"
    assert s6 == s5
    assert (code1, code2, code3, code4, code5, code6) == (0,) * 6
    assert code7 == 1
    assert s7.startswith("GARDE: révision inconnue")
    assert code8 == 1
    assert s8.startswith("GARDE: pas de CHANTIER.md")


def test_blobs_git(tmp_path, init_git):
    """VIT3 : `textes_contexte` avec `rev` lit en un `git cat-file --batch` ce que l'ancien lecteur — un `git show` par
    fichier — lisait, au caractère près : CRLF, `\\r` seul, accents, fin sans LF, et un dossier en `.md` ; une entrée
    absente ou qui n'est pas un blob ne décale pas la suivante."""
    if not shutil.which("git"):
        pytest.skip("git absent — blobs_git n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d = os.path.join(tr, "bl")
        os.makedirs(os.path.join(d, "ctx", "d.md"))
        for nom, octets in (("CHANTIER.md", b"- **contexte** : ctx/\n"), ("ctx/a.md", b"# Chantier A\r\nligne\r\n"),
                            ("ctx/b é.md", "# Chantier B — été\nfin sans LF".encode()),
                            ("ctx/c.md", b"un\rdeux\n\n"), ("ctx/d.md/x.txt", b"x\n")):
            with open(os.path.join(d, nom), "wb") as f:
                f.write(octets)
        init_git(d)
        git_matin(d, "-c", "core.autocrlf=false", "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")

        def ancien(chemin):
            """L'ancien lecteur : un `git show` par fichier."""
            code, t = mod.git_texte(["show", "HEAD:./" + chemin], d)
            return t.split("\n") if code == 0 else []
        nouveau = mod.textes_contexte(d, "HEAD")
        anciens = [ancien(c) for c, _ in nouveau]
        lus = mod.blobs_git(["HEAD:./ctx/a.md", "HEAD:./ctx/absent.md", "HEAD:./ctx/d.md", "HEAD:./ctx/c.md"], d)
    assert [c for c, _ in nouveau] == ["ctx/a.md", "ctx/b é.md", "ctx/c.md", "ctx/d.md"]
    assert [l for _, l in nouveau] == anciens
    assert nouveau[0][1] == ["# Chantier A", "ligne", ""]
    assert nouveau[1][1] == ["# Chantier B — été", "fin sans LF"]
    assert (lus == ["# Chantier A\nligne\n", None, None, "un\ndeux\n\n"]), ("VIT3 : blobs_git — absent et dossier rendent None, sans décaler l'entrée suivante — mutant : sauter le LF "
             "d'après le contenu") + "\n" + str(lus)


def test_courant_de(tmp_path, init_git):
    """NUI22 : `courant_de`, seul lecteur du chantier du dossier — post-it, branche, principale, ancienne ligne."""
    if not shutil.which("git"):
        pytest.skip("git absent — courant_de n'est pas testé")
        return

    def courant(dossier):
        code, s = appel(["carte", dossier])
        ligne = next((l for l in s.split("\n") if l.startswith(("COURANT=", "GARDE:"))), s)
        return code, ligne

    def chantier(lettre, *marques):
        return "# Chantier %s — x\n\n%s\n\n## %s1 [ ] — f\n" % (lettre, "\n".join(marques), lettre)

    signe = ("-c", "user.name=t", "-c", "user.email=t@t")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wt = os.path.join(tr, "cd"), os.path.join(tr, "wt")
        ecrire(os.path.join(d, "CHANTIER.md"), "- **alias** : cd\n- **contexte** : ctx/\n")
        ecrire(os.path.join(d, "ctx", "a.md"), chantier("A", OUVERT_LIGNE % "2026-10-03"))
        ecrire(os.path.join(d, "ctx", "c.md"), chantier("C", OUVERT_LIGNE % "2026-10-01", mod.CLOS_LIGNE % "2026-10-02"))
        init_git(d)
        git_matin(d, "add", "-A")
        git_matin(d, *signe, "commit", "-q", "-m", "base")
        git_matin(d, "worktree", "add", "-q", "-b", "wt", wt)
        a_wt, a_main = courant(wt), courant(d)
        ecrire(os.path.join(wt, "ctx", "b.md"), chantier("B", OUVERT_LIGNE % "2026-10-03"))
        b_wt, b_main = courant(wt), courant(d)
        git_matin(wt, "add", "-A")
        git_matin(wt, *signe, "commit", "-q", "-m", "b ouvert")
        b_rev = mod.de_cote(d, "wt")
        postit = mod.postit(d)
        ecrire(postit, "ctx/c.md\n")
        c_clos = courant(d)
        ecrire(os.path.join(d, "ctx", "e.md"), chantier("E", OUVERT_LIGNE % "2026-10-03"))
        os.remove(postit)
        c_deux = courant(d)
        ecrire(postit, "ctx/e.md\n")
        c_postit = courant(d)
        git_matin(d, "worktree", "remove", "--force", wt)
        v = os.path.join(tr, "vieux")
        ecrire(os.path.join(v, "CHANTIER.md"),
               "- **contexte** : ctx/\n")
        ecrire(os.path.join(v, "ctx", "x.md"), ouvert_ligne("# Chantier X — x\n\n## X1 [ ] — f\n"))
        d_vieux = courant(v)
    assert a_wt == (0, "COURANT=aucun")
    assert a_main == (0, "COURANT=ctx/a.md")
    assert b_wt == (0, "COURANT=ctx/b.md")
    assert b_main == (0, "COURANT=ctx/a.md")
    assert b_rev == "ctx/b.md"
    assert c_clos == (0, "COURANT=ctx/a.md")
    assert c_deux[0] == 1
    assert c_deux[1] == "GARDE: plusieurs chantiers ouverts : ctx/a.md, ctx/e.md"
    assert c_postit == (0, "COURANT=ctx/e.md")
    assert d_vieux == (0, "COURANT=ctx/x.md")


def test_postit(tmp_path, init_git):
    """ISO8 : `postit` pose le post-it d'un worktree pour son sous-agent isolé — `carte` y lit alors le chantier."""
    if not shutil.which("git"):
        pytest.skip("git absent — postit n'est pas testé")
        return
    signe = ("-c", "user.name=t", "-c", "user.email=t@t")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wt, hors = os.path.join(tr, "cd"), os.path.join(tr, "wt"), os.path.join(tr, "hors")
        ecrire(os.path.join(d, "CHANTIER.md"), "- **alias** : cd\n- **contexte** : ctx/\n")
        ecrire(os.path.join(d, "ctx", "a.md"), "# Chantier A — x\n\n%s\n\n## A1 [ ] — f\n" % (OUVERT_LIGNE % "2026-10-17"))
        ecrire(os.path.join(d, "ctx", "c.md"), "# Chantier C — x\n\n%s\n\n%s\n\n## C1 [x] — f\n"
               % (OUVERT_LIGNE % "2026-10-01", mod.CLOS_LIGNE % "2026-10-02"))
        ecrire(os.path.join(hors, "CHANTIER.md"), "- **contexte** : ctx/\n")
        init_git(d)
        git_matin(d, "add", "-A")
        git_matin(d, *signe, "commit", "-q", "-m", "base")
        git_matin(d, "worktree", "add", "-q", "-b", "wt", wt)
        p = mod.postit(wt)
        clos = appel(["postit", wt, "ctx/c.md"])
        clos_rien = not os.path.exists(p)
        sans_git = appel(["postit", hors, "ctx/a.md"])
        avant = next(l for l in appel(["carte", wt])[1].split("\n") if l.startswith("COURANT="))
        pose = appel(["postit", wt, "ctx\\a.md"])
        apres = next(l for l in appel(["carte", wt])[1].split("\n") if l.startswith("COURANT="))
        lu = mod.lire(p) if os.path.exists(p) else None
        git_matin(d, "worktree", "remove", "--force", wt)
    chef = pathlib.Path(os.path.join(RACINE, "skills", "enchainer", "SKILL.md")).read_text(encoding="utf-8")
    trois = chef[chef.find("## 3. Jouer chaque fiche"):chef.find("## 3 bis.")]
    assert avant == "COURANT=aucun"
    assert pose == (0, "POSTIT ctx/a.md — %s\n" % wt)
    assert lu == "ctx/a.md\n"
    assert apres == "COURANT=ctx/a.md"
    assert clos[0] == 1
    assert clos[1].startswith("GARDE: ctx/c.md n'est pas un chantier ouvert")
    assert clos_rien
    assert sans_git[0] == 1
    assert sans_git[1].startswith("GARDE: %s hors Git" % hors)
    assert "(Write)" not in trois
    assert "scripts/vlp.py\" postit " in trois


def noms_ailleurs(dossier):
    """Les `(code, nom du dossier)`, triés, des lignes `AILLEURS=` de la carte de `dossier` (NUI28)."""
    s = appel(["carte", dossier])[1]
    return sorted((l.split()[0][len("AILLEURS="):], os.path.basename(l.split(None, 1)[1].rstrip("/")))
                  for l in s.splitlines() if l.startswith("AILLEURS="))


def test_ailleurs(tmp_path, init_git):
    """NUI28 : `carte` nomme le chantier de chaque autre worktree (`AILLEURS=`), jamais le sien, ni un worktree sans
    chantier ; `niveau` ne compte pas d'écart de page à un chantier qui joue dans un autre worktree que le principal."""
    if not shutil.which("git"):
        pytest.skip("git absent — AILLEURS= n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d = os.path.join(tr, "m")
        depot_matin(init_git, d)
        loc = os.path.join(d, "ctx", "40-loc.md")      # main libre : LOC sans sa marque, l'artefact à aucun
        ecrire(loc, lire(loc).replace("\n%s\n" % OUVERT_LIGNE, ""))
        carte = os.path.join(d, "CHANTIER.md")
        ecrire(carte, re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(carte)))
        ecrire(os.path.join(d, "ctx", "80-maa.md"), "# Chantier MAA — Main\n\n%s\n\n## MAA1 [ ] — a\n" % OUVERT_DU_JOUR)
        commit_matin(d, "MAA ouvert", 3)
        dossiers = {"m": d}
        for nom, code in (("a", "WZA"), ("b", "WZB"), ("c", None)):
            w = dossiers[nom] = os.path.join(tr, "wt-" + nom)
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
            if code:
                ecrire(os.path.join(w, "ctx", "81-%s.md" % nom), "# Chantier %s — %s\n\n%s\n\n## %s1 [ ] — a\n"
                       % (code, nom, OUVERT_DU_JOUR, code))
        vus = {nom: noms_ailleurs(w) for nom, w in dossiers.items()}
    attendu ={"m": [("WZA", "wt-a"), ("WZB", "wt-b")], "a": [("MAA", "m"), ("WZB", "wt-b")],
               "b": [("MAA", "m"), ("WZA", "wt-a")], "c": [("MAA", "m"), ("WZA", "wt-a"), ("WZB", "wt-b")]}
    assert (vus == attendu), ("NUI28 (a) main + deux worktrees à chantier + un sans : la carte de chacun nomme les autres chantiers, "
             "jamais le sien ; le worktree sans chantier n'est nommé par personne — mutant : le sien non filtré") + "\n" + str(vus)

    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wl = os.path.join(tr, "n"), os.path.join(tr, "wt-l")
        depot_matin(init_git, d)
        git_matin(d, "worktree", "add", "-q", "-b", "l", wl, "main")
        ecrire(os.path.join(wl, "b.txt"), "b\n")
        commit_matin(wl, "LOC1 : a", 2)          # ni post-it ni marque à lui : ses commits disent ce qu'il joue
        ecrire(os.path.join(wl, "c.txt"), "c\n")
        commit_matin(wl, "ZZZ1 : vieux", 3)      # un vieux commit jamais fusionné, d'un chantier ouvert nulle part
        _, joue = appel(["niveau", d])
        carte = [l for l in appel(["carte", d])[1].splitlines() if l.startswith("AILLEURS=")]
    assert "AILLEURS: page: LOC joue dans " in joue
    assert "ÉCART: page:" not in joue
    assert len(carte) == 1
    assert carte[0].startswith("AILLEURS=LOC ")
    assert carte[0].rstrip("/").endswith("wt-l")

    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wv = os.path.join(tr, "v"), os.path.join(tr, "wt-v")
        os.makedirs(d)
        init_git(d)
        ecrire(os.path.join(d, "a.txt"), "a\n")
        commit_matin(d, "avant le suivi", 1)
        git_matin(d, "worktree", "add", "-q", "-b", "v", wv, "main")
        ecrire(os.path.join(wv, "CHANTIER.md"), CARTE_MATIN)      # sa vieille copie locale, jamais suivie
        ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
        ecrire(os.path.join(d, "CLAUDE.md"), "# v\n")
        commit_matin(d, "contexte suivi", 2)
        retard, principal_ = mod.ligne_git(wv), mod.ligne_git(d)
    assert ("GIT=en retard sur main : CHANTIER.md, CLAUDE.md suivi(s) là-bas, pas ici — worktree né avant ; y fusionner "
             "main" in retard)
    assert not any("retard" in l for l in principal_)
