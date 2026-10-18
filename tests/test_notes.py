"""`noyau/notes.py` : l'abri des notes et du journal, l'état, les renvois, la forme des pages et leurs liens — migré de
l'ancienne suite maison (REF58). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest
from aides import SCRIPTS, appel, ecrire, ligne_close, lire, mod, transcript

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"


OUVERT = "**Ouvert.** le 2026-10-08."


FICHES = """# Chantier Z

**Ouvert.** le 2026-10-08.

## Le socle commun

## Z1 [x] — faite
---
## Z2 [ ] — à faire
## Z10 [ ] — après
"""


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


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


def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


def test_etat(tmp_path):
    """Contrôler `etat` : dossier absent, puis le fichier d'état trouvé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        c = os.path.join(t, "ctx")
        assert (appel(["etat", c]) == (0, "ETAT=01-etat.md\n")), ("etat : dossier absent") + "\n" + str(appel(["etat", c]))
        os.makedirs(c)
        assert (appel(["etat", c]) == (0, "ETAT=01-etat.md\n")), ("etat : dossier vide") + "\n" + str(appel(["etat", c]))
        ecrire(os.path.join(c, "03-a.md"), "a\n")
        ecrire(os.path.join(c, "07-b.md"), "b\n")
        assert (appel(["etat", c]) == (0, "ETAT=08-etat.md\n")), ("etat : à la suite du plus grand") + "\n" + str(appel(["etat", c]))
        ecrire(os.path.join(c, "10-etat.md"), "état\n")
        assert (appel(["etat", c]) == (0, "ETAT=10-etat.md\n")), ("etat : déjà présent") + "\n" + str(appel(["etat", c]))


def test_renvois(tmp_path):
    """Contrôler `renvois` : renvois présents ou absents, poids sous ou sur le seuil."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        ecrire(os.path.join(t, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(t, "ctx", "01-a.md"), "a\n")
        ecrire(os.path.join(t, "outils", "b.py"), "b\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"),
               "# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `01-a.md` | on lit `z.md` |\n"
               "| `<NN>-x.md` | gabarit |\n| *(hors dossier)* `m.md` | ailleurs |\n"
               "| `commands/<nom>.md`, `outils/b.py` | code |\n| `references/` | dossier |\n")
        ecrire(os.path.join(t, "CLAUDE.md"),
               "# P\n\n| hors routage | `perdu.md` |\n\n## Routage — ouvrir ceci\n\n| La tâche | Ouvrir |\n|---|---|\n"
               "| lire `vlp.py` | `ctx/01-a.md` |\n| lancer | **`/vlp:chantier`** |\n\n## Économie\n\n| x | `loin.md` |\n")
        assert (appel(["renvois", t]) == (0, "POIDS CLAUDE.md 14/80 · CHANTIER.md 2/50 · index 9/80\n"
                 "RENVOIS 3 nommés · 0 absents\n")), ("renvois : tout présent, poids sous seuil") + "\n" + str(appel(["renvois", t]))
        ecrire(os.path.join(t, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n" + "x\n" * 49)
        code, s = appel(["renvois", t])
        assert (code == 0 and s.startswith(
            "AVERTISSEMENT: CHANTIER.md 51 lignes > 50\nPOIDS CLAUDE.md 14/80 · CHANTIER.md 51/50 · index 9/80\n")), ("renvois : poids au-delà, avertit sans changer la sortie") + "\n" + str(s)
        os.remove(os.path.join(t, "CLAUDE.md"))
        code, s = appel(["renvois", t])
        assert (code == 0 and "POIDS CLAUDE.md absent/80 · CHANTIER.md 51/50" in s), ("renvois : CLAUDE.md absent dans les poids") + "\n" + str(s)
        ecrire(os.path.join(t, "CLAUDE.md"),
               "# P\n\n| hors routage | `perdu.md` |\n\n## Routage — ouvrir ceci\n\n| La tâche | Ouvrir |\n|---|---|\n"
               "| lire `vlp.py` | `ctx/01-a.md` |\n| lancer | **`/vlp:chantier`** |\n\n## Économie\n\n| x | `loin.md` |\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `99-mort.md` | jamais |\n")
        code, s = appel(["renvois", t])
        assert (code == 1 and s.startswith("ABSENT: ctx/00-INDEX.md:3: 99-mort.md\n")
                 and s.endswith("index 3/80\nRENVOIS 2 nommés · 1 absents\n")), ("renvois : absent, sort 1") + "\n" + str(s)
        os.remove(os.path.join(t, "CHANTIER.md"))
        assert (appel(["renvois", t])[0] == 1), ("renvois : pas équipé") + "\n" + str(appel(["renvois", t]))


def test_renvois_garde(tmp_path):
    """TAB2 : une ligne d'index qui n'a pas le nombre de cellules de son en-tête arrête `renvois`."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as d:
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(d, "ctx", "01-a.md"), "a\n")
        tete = "| Fichier | a | b | c | d |\n|---|---|---|---|---|\n| `01-a.md` | x \\| y | b | c | d |\n"
        ecrire(os.path.join(d, "ctx", "00-INDEX.md"), tete)
        assert (appel(["renvois", d]) == (0, "POIDS CLAUDE.md absent/80 · CHANTIER.md 2/50 · index 3/80\n"
                 "RENVOIS 1 nommés · 0 absents\n")), ("TAB2 : renvois, table saine et \\| gardé") + "\n" + str(appel(["renvois", d]))
        for ligne, n in (("| `01-a.md` | a | b | c |\n", 4), ("| `01-a.md` | a | b | c | d | e |\n", 6)):
            ecrire(os.path.join(d, "ctx", "00-INDEX.md"), tete + ligne)
            assert (appel(["renvois", d]) == (
                1, "GARDE: ctx/00-INDEX.md, ligne 4 : %d cellules au lieu de 5 — une barre verticale dans une "
                "cellule s'écrit \\|\n" % n)), ("TAB2 : renvois, %d cellules au lieu de 5 → GARDE, sort 1" % n) + "\n" + str(appel(["renvois", d]))


def test_barre_finale(tmp_path):
    """TAB2 : une ligne de table sans barre finale rend GARDE, au lieu de perdre sa dernière cellule."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as d:
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier |\n|---|\n")
        # (libellé, en-tête, lignes, numéro de la ligne fautive) ; le routage commence ligne 3
        cas = (("ligne", "| La tâche | Ouvrir |", "| a | `01-a.md` |\n| b | `02-b.md`", 6),
               ("en-tête", "| La tâche | Ouvrir", "| a | `01-a.md` | x\n| b | `02-b.md` | y |", 3))
        for libelle, tete, corps, n in cas:
            ecrire(os.path.join(d, "CLAUDE.md"), "## Routage\n\n%s\n|---|---|\n%s\n" % (tete, corps))
            assert (appel(["renvois", d]) == (1, "GARDE: CLAUDE.md, ligne %d : pas de barre finale — une ligne "
                                                  "de table se ferme par |\n" % n)), ("TAB2 : une ligne sans barre finale rend GARDE, sort 1 (%s)" % libelle) + "\n" + str(appel(["renvois", d]))
    entete = ["| # | Chantier | Apporte | Coût | Dépend |", "|---|---|---|---|---|"]
    try:
        mod.todo_du_fichier(entete + ["| 1 | A | b | c | d"])
        dit = "aucune erreur"
    except ValueError as e:
        dit = str(e)
    assert (dit.startswith("ligne 1 de la TODO : pas de barre finale")), ("TAB2 : une ligne sans barre finale lève, dans la TODO aussi") + "\n" + str(dit)


PAGE_ABR = """<title>kit — Abri</title>
    <h1>Abri &amp; journal</h1>
    <p>Notes &lt;à l'abri&gt;</p>
    <ul class="fiches">
      <li class="fiche" data-etat="faite">
        <span class="id">ABR1</span><span class="titre">Un</span>
        <span class="etat">faite</span>
        <span class="note">test 3/3 &amp; pyright 0</span>
      </li>
      <li class="fiche">
        <span class="id">ABR2</span><span class="titre">Deux</span>
        <span class="etat">à faire</span>
        <span class="note">dépend de ABR1</span>
      </li>
    </ul>
    <ul class="journal">
      <li><time datetime="2026-09-25">2026-09-25</time><span>Pierre &amp; Paul</span></li>
      <li><time>2026-09-26</time><span>E3 : <span class="mono">allowed-tools</span> muet</span></li>
      <li><time datetime="2026-09-26">2026-09-26</time><span>sur
        deux lignes</span></li>
    </ul>
  <section>
    <h2>Chantier clos le 2026-09-26</h2>
    <div class="bilan">
      <p>Livré : un <code>.md</code> &amp; une page</p>
    </div>
  </section>
"""


def test_abri(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        page = os.path.join(tab, "artefacts", "76-abri.html")
        ecrire(page, PAGE_ABR)
        md = os.path.join(tab, "artefacts", "76-abri.md")
        assert (mod.chemin_abri(page) == md), ("ABR1 : chemin du .md à côté de la page") + "\n" + str(mod.chemin_abri(page))
        code, s = appel(["abri", page])
        assert (code == 0 and s == "ABRI %s · résultat 1 · notes 2 · journal 3 · bilan 1\n" % md), ("ABR1 : abri — 2 notes, 3 lignes de journal, un bilan") + "\n" + str(s)
        parts = mod.lire_abri(md)
        assert (parts["titre"] == "Abri & journal" and parts["resultat"] == "Notes <à l'abri>"
                 and parts["notes"] == {"ABR1": "test 3/3 & pyright 0", "ABR2": "dépend de ABR1"}
                 and parts["journal"] == [("2026-09-25", "Pierre & Paul"), ("2026-09-26", "E3 : allowed-tools muet"),
                                          ("2026-09-26", "sur deux lignes")]
                 and parts["bilan"] == ["Livré : un .md & une page"]), ("ABR1 : .md relu, texte désechappé — mutant : ne pas désechapper") + "\n" + str(repr(parts))
        with open(page, "rb") as f:
            assert (f.read() == PAGE_ABR.encode("utf-8")), ("ABR1 : la page identique octet pour octet") + "\n" + "page modifiée"
        mod.ecrire_abri(md, parts)
        assert (mod.lire_abri(md) == parts), ("ABR1 : écrire puis relire redonne les mêmes parts") + "\n" + str(lire(md))
        code, s = appel(["abri", page])
        assert (code == 0 and s == "DÉJÀ %s\n" % md), ("ABR1 : second abri — DÉJÀ, .md non réécrit") + "\n" + str(s)
        code, s = appel(["abri", os.path.join(tab, "absente.html")])
        assert (code == 1 and s.startswith("GARDE:")), ("ABR1 : page absente — GARDE, code 1") + "\n" + str(s)


FICHES_ABR2 = """# Chantier ABR

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
<!-- /FICHE -->
"""


def test_abr2(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "abr.md")
        page = os.path.join(tab, "artefacts", "abr.html")
        md = mod.chemin_abri(page)
        ecrire(fiches, FICHES_ABR2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert (code == 0 and os.path.exists(md)), ("ABR2 : --creer amorce le .md") + "\n" + str(s)
        code, s = appel(["page", fiches, page, "--note", "P1", "x", "--journal", "y", "--date", "2026-09-26"])
        assert (code == 0
                 and mod.lire_abri(md)["notes"] == {"P1": "x"}
                 and mod.lire_abri(md)["journal"] == [("2026-09-26", "y")]), ("ABR2 : page — note et journal écrits d'abord dans le .md") + "\n" + str(s + lire(md))
        html_avant = lire(page)
        os.remove(page)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        assert (code == 0 and '<span class="note">x</span>' in html
                 and '<time datetime="2026-09-26">2026-09-26</time><span>y</span>' in html
                 and "<p>R0</p>" in html), ("ABR2 : la page effacée reprend x et y depuis le .md — mutant : lire l'ancienne page") + "\n" + str(s + html)
        assert (mod.lire_abri(md)["notes"] == {"P1": "x"} and mod.lire_abri(md)["journal"] == [("2026-09-26", "y")]), ("ABR2 : le .md n'a pas bougé au second --creer — mutant : --creer réécrit le .md") + "\n" + str(lire(md))

        # Une page ancienne, sans .md : elle garde ses notes (pas de perte à l'amorçage).
        ancienne = os.path.join(tab, "artefacts", "anc.html")
        ecrire(ancienne, html_avant)
        fiches_anc = os.path.join(tab, "anc.md")
        ecrire(fiches_anc, FICHES_ABR2)
        assert (not os.path.exists(mod.chemin_abri(ancienne))), ("ABR2 : pas de .md avant ce test") + "\n" + ""
        code, s = appel(["page", fiches_anc, ancienne, "--date", "2026-09-27"])
        html = lire(ancienne)
        assert (code == 0
                 and '<span class="note">x</span>' in html
                 and '<span>y</span>' in html), ("ABR2 : page ancienne sans .md — garde ses notes") + "\n" + str(s + html)
        assert (os.path.exists(mod.chemin_abri(ancienne)) and mod.lire_abri(mod.chemin_abri(ancienne))["notes"] == {"P1": "x"}), ("ABR2 : l'amorçage a posé le .md de l'ancienne page") + "\n" + str(lire(mod.chemin_abri(ancienne)))
        # Le .md prime désormais sur l'ancienne page : une note différente dans le .md l'emporte
        # — mutant : lire la note dans l'ancienne page (`anciens`) au lieu du .md.
        code, s = appel(["page", fiches_anc, ancienne, "--note", "P1", "z", "--date", "2026-09-27"])
        html = lire(ancienne)
        assert (code == 0 and '<span class="note">z</span>' in html and '<span class="note">x</span>' not in html), ("ABR2 : le .md l'emporte sur l'ancienne note de la page — mutant : lire l'ancienne page") + "\n" + str(s + html)
        # Une note retirée du .md disparaît de la page — mutant : retomber sur l'ancienne page (`anciens`),
        # qui la garde encore. C'est le seul cas où le mutant se distingue d'une note passée par --note.
        md_anc = mod.chemin_abri(ancienne)
        parts_anc = mod.lire_abri(md_anc)
        del parts_anc["notes"]["P1"]
        mod.ecrire_abri(md_anc, parts_anc)
        code, s = appel(["page", fiches_anc, ancienne, "--date", "2026-09-28"])
        html = lire(ancienne)
        assert (code == 0 and '<span class="note">' not in html.split("<ul class=\"journal\">")[0].split('id">P1')[1].split("</li>")[0]), ("ABR2 : note retirée du .md — absente de la page — mutant : retombe sur l'ancienne page") + "\n" + str(s + html)


FICHES_PLI2 = """# Chantier PLI2

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
x
<!-- /FICHE -->
"""


def test_vlp_css_recopie(tmp_path):
    source = io.open(os.path.join(ICI, "..", "templates", "vlp.css"), "rb").read()

    # `page --creer`, puis `page` sans --creer (régénération) : les deux recopient.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        css = os.path.join(tab, "artefacts", "vlp.css")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert (code == 0 and os.path.isfile(css) and io.open(css, "rb").read() == source
                 and "CSS %s\n" % css in s), ("PLI2 : page --creer recopie vlp.css, le dit en sortie") + "\n" + str(s)
        with open(css, "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        assert (code == 0 and io.open(css, "rb").read() == source), ("PLI2 : page (régénération, sans --creer) remet vlp.css à l'identique"
                 " — mutant : ne copier qu'à --creer") + "\n" + str(s)

    # `feuille`, sur un projet équipé, recopie aussi.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj = os.path.join(tab, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               ""
               "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"),
               "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        css = os.path.join(proj, "ctx", "artefacts", "vlp.css")
        code, s = appel(["feuille", proj])
        assert (code == 0 and os.path.isfile(css) and io.open(css, "rb").read() == source
                 and "CSS %s\n" % css in s), ("PLI2 : feuille recopie vlp.css, le dit en sortie") + "\n" + str(s)

    # Les deux gabarits ne portent plus de <style> inline (chantier PLI, fiche PLI2).
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = io.open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
        assert (gabarit.count("<style") == 0 and 'href="vlp.css"' in gabarit), ("PLI2 : %s sans <style> — %d" % (nom, gabarit.count("<style"))) + "\n" + str(gabarit[:400])


def avec_style_inline(html):
    """Une page déjà régénérée (donc liée à vlp.css), avec son <style> d'avant PLI3
    remis en place — comme une page publiée avant ce chantier, jamais régénérée depuis."""
    css = io.open(os.path.join(ICI, "..", "templates", "vlp.css"), encoding="utf-8").read()
    return html.replace('<link rel="stylesheet" href="vlp.css">', "<style>\n%s</style>" % css, 1)


def test_style_migre(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        ancienne = os.path.join(tab, "avant.html")
        ecrire(fiches, FICHES_PLI2)
        appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        # Une page déjà correcte, mais encore au CSS inline (avant PLI3) — le seul écart voulu.
        ecrire(page, avec_style_inline(lire(page)))
        ecrire(ancienne, lire(page))
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0 and "<style>" not in html and html.count('href="vlp.css"') == 1), ("PLI3 : régénérée, la page n'a plus de <style>, un seul <link> vers vlp.css"
                 " — mutant : ajouter le <link> sans retirer le <style>") + "\n" + str(html[:400])
        code, s = appel(["comparer", ancienne, page])
        assert (code == 0 and "PERDU:" not in s and s.rstrip().startswith("COMPARER 0 perdus")), ("PLI3 : comparer ne dit aucune ligne de texte perdue") + "\n" + str(s)
        code, s = appel(["page", fiches, page])
        assert (code == 0 and lire(page).count('href="vlp.css"') == 1), ("PLI3 : régénérée deux fois, toujours un seul <link>") + "\n" + str(lire(page)[:400])


FICHES_PLI5 = """# Chantier PLI5

## Le socle commun

## L'ordre des fiches

<!-- FICHE:Q1 -->
## Q1 [x] — Faite
**Critère de fin**
x
<!-- /FICHE -->

<!-- FICHE:Q2 -->
## Q2 [ ] — En cours
**Critère de fin**
x
<!-- /FICHE -->

<!-- FICHE:Q3 -->
## Q3 [ ] — À faire
**Critère de fin**
x
<!-- /FICHE -->
"""


def test_pretes_et_paralleles(tmp_path):
    def fiche(ident, case, dep, fichiers):
        return ("<!-- FICHE:%s -->\n## %s [%s] — Fiche %s\n**Dépend de** : %s\n%s**Critère de fin**\nx\n"
                "<!-- /FICHE -->\n\n" % (ident, ident, case, ident, dep, "**Fichiers** : %s\n" % fichiers if fichiers else ""))
    def fichier_md(faites):
        return ("# Chantier R\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                + fiche("R1", "x", "rien.", "`a.py`")
                + fiche("R2", "x" if "R2" in faites else " ", "`R1`.", "`scripts/a.py`, `b.css`")
                + fiche("R3", "x" if "R3" in faites else " ", "`R1`.", "`c.js` (nouveau) — et rien d'autre.")
                + fiche("R4", "x" if "R4" in faites else " ", "rien.", "`templates/b.css` (`.x > y` `:12`), `compte_todo`")
                + fiche("R5", " ", "`R2`, `R3`,\n`R4` et `PLI9`.", "`d.md`")
                + fiche("R6", " ", "`R1`.", "")
                + fiche("R7", "x" if "R7" in faites else " ", "`R3`.", "`e.md`"))
    def cartes(html):
        return {m.group(1): m.group(0)
                for m in re.finditer(r'<li class="fiche".*?<span class="id">(\w+)</span>.*?</li>', html, re.S)}
    def tete(attributs, ident):
        return '<li class="fiche"%s><span class="gauche"><span class="id">%s</span></span>' % (attributs, ident)
    def dit(li, ident, texte):
        return ('<span class="etat">%s</span>' % texte) in li.get(ident, "")
    def libelle(html, ident, texte):
        return re.sub(r'(<span class="id">%s</span>.*?<span class="etat">)[^<]*' % ident,
                      lambda m: m.group(1) + texte, html, count=1, flags=re.S)
    with tempfile.TemporaryDirectory(dir=tmp_path) as tpp:
        fiches = os.path.join(tpp, "r.md")
        page = os.path.join(tpp, "artefacts", "r.html")
        ecrire(fiches, fichier_md(()))
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        li = cartes(html)
        assert (code == 0 and li.get("R5", "").startswith(tete(" data-attend", "R5")) and dit(li, "R5", "Après R2, R3, R4")
                 and li.get("R7", "").startswith(tete(" data-attend", "R7")) and dit(li, "R7", "Après R3")), ("prêtes : une fiche qui attend dit « Après » et tous les noms pas faits de ce fichier"
                 " — mutant : attente ignorée") + "\n" + str(s + html)
        assert (dit(li, "R4", "À lancer") and dit(li, "R6", "À lancer") and all('class="dep' not in c for c in li.values())
                 and li.get("R2", "").startswith(tete(' data-etat="encours"', "R2"))
                 and dit(li, "R2", "En cours · R3 peut partir en même temps")), ("prêtes : une fiche qui se lance dit « À lancer », sans ses dépendances faites ; en cours, son état") + "\n" + str("%r" % li)
        assert (dit(li, "R3", "À lancer · en même temps que R2")
                 and all("même temps" not in li.get(i, "même temps") for i in ("R1", "R4", "R5", "R6", "R7"))), ("en même temps : sur les prêtes sans fichier commun (même nommé autrement), pas sur celle sans"
                 " ligne Fichiers — mutants : fichiers communs ignorés, prête sans Fichiers comptée") + "\n" + str("%r" % li)
        assert (mod.lis_page(html).get("R2", ("?",))[0] == "encours" and mod.lis_page(html).get("R5", ("?",))[0] is None), ("prêtes : la page se relit — lis_page lit l'état malgré data-attend") + "\n" + str("%r" % mod.lis_page(html))
        code, s = appel(["page", fiches, page])
        code2, s2 = appel(["page", fiches, page, "--forme"])
        assert (code == 0 and code2 == 0 and lire(page) == html), ("prêtes : régénérer, puis repeindre, ne change rien") + "\n" + str(s + s2 + lire(page))
        # Une page d'avant : « à faire » (avant BTN), « à lancer » et « après » en minuscules (v12 de la page
        # BTN), une phrase périmée, et un libellé écrit à la main.
        vieille = html
        for ident, texte in (("R6", "abandonnée"), ("R4", "à lancer"), ("R3", "À lancer · en même temps que R9"),
                             ("R5", "à faire"), ("R7", "après R3")):
            vieille = libelle(vieille, ident, texte)
        ecrire(page, vieille)
        code, s = appel(["page", fiches, page, "--forme"])
        li = cartes(lire(page))
        assert (code == 0 and dit(li, "R3", "À lancer · en même temps que R2") and dit(li, "R4", "À lancer")
                 and dit(li, "R5", "Après R2, R3, R4") and dit(li, "R7", "Après R3") and dit(li, "R6", "abandonnée")), ("prêtes : --forme recalcule les libellés qu'il a écrits, dans toutes leurs formes, garde « abandonnée »"
                 " — mutants : tout libellé gardé, casse, phrase entière comparée") + "\n" + str(s + lire(page))
        ecrire(fiches, fichier_md(("R2", "R3")))
        appel(["page", fiches, page])
        li = cartes(lire(page))
        assert (dit(li, "R4", "En cours · R7 peut partir en même temps") and dit(li, "R7", "À lancer · en même temps que R4")
                 and dit(li, "R5", "Après R4")), ("en même temps : suit les cases — R2 et R3 faites, R4 en cours, R4 et R7 ensemble, R5 après R4") + "\n" + str("%r" % li)
        ecrire(fiches, fichier_md(("R2", "R3", "R4", "R7")))
        appel(["page", fiches, page])
        assert (all("même temps" not in c for c in cartes(lire(page)).values())), ("en même temps : une seule prête avec des fichiers — aucun « en même temps »") + "\n" + str(lire(page))
        # En cours, mais une dépendance plus bas n'est pas faite : l'état reste, puis « attend ».
        ecrire(fiches, "# Chantier S\n\n" + fiche("S1", " ", "`S2`, `S3`, `S4`.", "`f.md`")
               + "".join(fiche(i, " ", "rien.", "`g.md`") for i in ("S2", "S3", "S4")))
        code, s = appel(["page", fiches, os.path.join(tpp, "artefacts", "s.html"), "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        li = cartes(lire(os.path.join(tpp, "artefacts", "s.html")))
        assert (code == 0 and li.get("S1", "").startswith(tete(' data-etat="encours" data-attend', "S1"))
                 and dit(li, "S1", "En cours · attend S2, S3, S4")), ("prêtes : en cours et en attente — « En cours · attend » et tous les noms, data-attend") + "\n" + str(s + "%r" % li)
        # Une plage « `P1` à `P4` » (cadrage d'ACA, 2026-10-11) : lue en deux noms, P5 se disait « À lancer »,
        # sans data-attend, alors que P2 et P3, au milieu, ne sont pas faites.
        ecrire(fiches, "# Chantier P\n\n" + "".join(fiche(i, c, "rien.", "`%s.md`" % i) for i, c in
                                                     (("P1", "x"), ("P2", " "), ("P3", " "), ("P4", "x")))
               + fiche("P5", " ", "`P1` à `P4`.", "`p5.md`"))
        code, s = appel(["page", fiches, os.path.join(tpp, "artefacts", "p.html"), "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        li = cartes(lire(os.path.join(tpp, "artefacts", "p.html")))
        assert (code == 0 and li.get("P5", "").startswith(tete(" data-attend", "P5")) and dit(li, "P5", "Après P2, P3")
                 and mod.deplier_plages("`P4` à `P2`") == "`P4` à `P2`"), ("prêtes : une plage « P1 à P4 » attend chaque fiche du milieu pas faite, data-attend — mutant :"
                 " plage lue en deux noms ; des bornes à l'envers restent telles quelles") + "\n" + str(s + "%r" % li)


def test_journal_replie(tmp_path):
    for n, visibles, repliees in ((7, 3, 4), (2, 2, 0)):
        with tempfile.TemporaryDirectory(dir=tmp_path) as tjr:
            fiches = os.path.join(tjr, "q.md")
            page = os.path.join(tjr, "artefacts", "q.html")
            ecrire(fiches, FICHES_PLI5)
            argv = ["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"]
            for k in range(1, n + 1):
                argv += ["--journal", "j%d" % k]
            code, s = appel(argv)
            html = lire(page)
            ancien = re.search(r'<details class="journal-ancien">.*?</details>', html, re.S)
            premier = re.search(r'<ul class="journal">(.*?)</ul>', html, re.S)
            vus = premier.group(1).count("<li>") if premier else -1
            caches = ancien.group(0).count("<li>") if ancien else 0
            textes = [t for _, t in mod.abri_de_page(html)["journal"]]
            assert (code == 0 and vus == visibles and caches == repliees and bool(ancien) == bool(repliees)
                     and textes == ["j%d" % k for k in range(1, n + 1)]
                     and (not ancien or "%d entrées plus anciennes" % repliees in ancien.group(0))), ("PLI6 : %d entrées → %d visibles, %d repliées, abri les relit dans l'ordre"
                     " — mutant : garder tout visible" % (n, visibles, repliees)) + "\n" + str("%s\nvus=%d caches=%d %r\n%s" % (s, vus, caches, textes, html[html.find("Journal"):][:900]))


def test_bilan_en_haut(tmp_path):
    gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read()
    # une page d'avant PLI6 : le bilan en bas, juste avant le pied de page
    i = gabarit.index("  <!-- ZONE:bilan")
    fin = gabarit.index("  </section>\n", i) + len("  </section>\n\n")
    bloc = gabarit[i:fin]
    ancienne = (gabarit[:i] + gabarit[fin:]).replace("  <footer>", bloc + "  <footer>", 1)
    with tempfile.TemporaryDirectory(dir=tmp_path) as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(tb, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
        page = os.path.join(tb, "ctx", "artefacts", "50-u.html")
        ecrire(page, ancienne)
        assert (ancienne.index("ZONE:bilan") > ancienne.index("ZONE:fiches")), ("PLI6 : la page de départ a son bilan en bas") + "\n" + ""
        code, s = appel(["clore", tb, "--livre", "fini", "--date", "2026-09-27"])
        html = lire(page)
        assert (code == 0 and html.count("ZONE:bilan") == 1
                 and html.index("ZONE:bilan") < html.index("ZONE:fiches")
                 and "<section>\n    <h2>Chantier clos le 2026-09-27</h2>" in html), ("PLI6 : après clore, ZONE:bilan précède ZONE:fiches, visible, une seule fois"
                 " — mutant : laisser le bilan en bas") + "\n" + str(s + html[:1500])
        # un clos d'avant PLI6 : bilan visible, mais en bas — `page` le remonte aussi (dette PLI)
        j = html.index("  <!-- ZONE:bilan")
        fin_b = html.index("  </section>\n", j) + len("  </section>\n")
        clos_bas = (html[:j] + html[fin_b:]).replace("  <footer>", html[j:fin_b] + "\n  <footer>", 1)
        ecrire(page, clos_bas)
        code, s = appel(["page", os.path.join(tb, "ctx", "50-u.md"), page])
        html = lire(page)
        assert (code == 0 and clos_bas.index("ZONE:bilan") > clos_bas.index("ZONE:fiches")
                 and html.count("ZONE:bilan") == 1 and html.index("ZONE:bilan") < html.index("ZONE:fiches")), ("dette PLI : page remonte le bilan d'un clos resté en bas, une seule fois"
                 " — mutant : ne le remonter qu'à clore") + "\n" + str(s + html[:1500])
    with tempfile.TemporaryDirectory(dir=tmp_path) as tbo:
        # témoin : une page ouverte à l'ancienne forme (bilan caché, en bas) n'est pas touchée
        ouverte = os.path.join(tbo, "artefacts", "q.html")
        fiches_o = os.path.join(tbo, "q.md")
        ecrire(fiches_o, FICHES_PLI5)
        ecrire(ouverte, ancienne)
        code, s = appel(["page", fiches_o, ouverte])
        html = lire(ouverte)
        assert (code == 0 and html.index("ZONE:bilan") > html.index("ZONE:fiches")
                 and "<section hidden>\n    <h2>Chantier clos le" in html), ("dette PLI : un chantier ouvert garde son bilan caché là où il est"
                 " — mutant : toujours remonter le bilan") + "\n" + str(s + html[-1500:])


def test_forme(tmp_path, init_git):
    """page --forme (chantier HAB1) : la forme d'une page ancienne refaite, ses chiffres gardés,
    même dans un dépôt dont les commits de fiche feraient changer le coût."""
    if not shutil.which("git"):
        pytest.skip("git absent — page --forme n'est pas testée")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tfo:
        sq = os.path.join(tfo, "s.jsonl")
        transcript(sq, 6, [T0 + d for d in (50, 200, 250, 400, 700, 1000)])
        fiches = os.path.join(tfo, "q.md")
        ecrire(fiches, QFICHES % (sq, sq))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(tfo, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        init_git(tfo)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=tfo, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        page = os.path.join(tfo, "artefacts", "q.html")
        code, s = appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R",
                         "--date", "2026-01-05"])
        assert (code == 0), ("HAB1 : la page de départ se crée") + "\n" + str(s)
        # L'ancien format : style dans la page, fiches à plat, bilan visible en bas, chiffres d'une autre mesure.
        html = avec_style_inline(lire(page))
        for balise in ("<details open>", "<details>", "</details>", "<summary>", "</summary>"):
            html = html.replace(balise, "")
        html = re.sub(r'<span class="cout mono">.*?</span>', "", html)
        # Écrits à la main sur les vieilles pages (18-evals, 11-conso du kit) : un libellé, un comptage.
        html = re.sub(r'(<span class="id">Q2</span>.*?<span class="etat">)Faite(</span>)', r"\1abandonnée\2", html, count=1, flags=re.S)
        html = re.sub(r'(<p class="mono" style="margin-top:.5rem">).*?(</p>)', r"\g<1>2 fiches · Q2 abandonnée · clos\2", html, count=1)
        c1, c2 = "≈1,1k (1 111) · 1 tours · 0,01 $", "≈2,2k (2 222) · 2 tours · 0,02 $"
        for q, c in (("Q1", c1), ("Q2", c2)):
            html = re.sub(r'(<span class="id">%s</span>.*?)(\s*</li>)' % q,
                          lambda m: m.group(1) + '\n        <span class="cout mono">%s</span>' % c + m.group(2),
                          html, count=1, flags=re.S)
        total = "Coût du chantier : ≈11,3M (11 262 523) · 42 tours · 3,40 $"
        hors = "Hors fiches : ≈5,0k (5 000) · 1 tours · 0,05 $"
        html = re.sub(r'<p class="mono cout-total">.*?</p>', '<p class="mono cout-total">%s</p>' % total, html, flags=re.S)
        html = re.sub(r'<p class="mono cout-hors">.*?</p>', '<p class="mono cout-hors">%s</p>' % hors, html, flags=re.S)
        i = html.index("  <!-- ZONE:bilan")
        fin = html.index("  </section>\n", i) + len("  </section>\n\n")
        bloc = html[i:fin].replace("<section hidden>", "<section>", 1).replace("<p></p>", "<p>Fini.</p>", 1)
        html = (html[:i] + html[fin:]).replace("  <footer>", bloc + "  <footer>", 1)
        assert ("<style>" in html and "<details" not in html and total in html
                 and html.index("ZONE:bilan") > html.index("ZONE:fiches")), ("HAB1 : la page de départ est à l'ancien format") + "\n" + str(html[:600])
        ecrire(page, html)
        code, s = appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        apres = lire(page)
        lu = mod.lis_page(apres)
        assert (code == 0 and apres.count(total) == 1 and apres.count(hors) == 1
                 and "total ≈11,3M (11 262 523) · 42 tours · 3,40 $" in s), ("HAB1 : --forme garde le total 11 262 523 et le hors fiches — mutant : --forme ignoré") + "\n" + str(s + apres)
        assert (lu["Q1"][2] == c1 and lu["Q2"][2] == c2), ("HAB1 : --forme garde les deux coûts de fiche (%s ; %s)" % (c1, c2)) + "\n" + str(lu)
        assert ("<style>" not in apres and apres.count('href="vlp.css"') == 1 and apres.count("<details") >= 2
                 and apres.index("ZONE:bilan") < apres.index("ZONE:fiches") and "<p>Fini.</p>" in apres), ("HAB1 : --forme lie vlp.css, replie les fiches, remonte le bilan") + "\n" + str(apres[:1500])
        assert ("<span class=\"etat\">abandonnée</span>" in apres and "2 fiches · Q2 abandonnée · clos" in apres
                 and 'Mis à jour le <span class="mono">2026-01-05</span>' in apres), ("HAB1 : --forme garde libellé, comptage et date écrits sur l'ancienne page"
                 " — mutant : reprendre la date du jour") + "\n" + str(apres)
        ecrire(os.path.join(tfo, "avant.html"), html)
        code, s = appel(["comparer", os.path.join(tfo, "avant.html"), page])
        assert (code == 0 and s.rstrip().startswith("COMPARER 0 perdus")), ("HAB1 : comparer, 0 ligne de texte perdue") + "\n" + str(s)
        code, s = appel(["vigile", page])
        assert (code == 0 and s.startswith("PAGE SAINE")), ("HAB1 : la page repeinte, vigile PAGE SAINE") + "\n" + str(s)
        avant = lire(page)
        code, s = appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        assert (code == 0 and lire(page) == avant), ("HAB1 : --forme deux fois ne change rien") + "\n" + str(s)
        code, s = appel(["page", fiches, os.path.join(tfo, "neuve.html"), "--forme", "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        assert (code == 1 and s.startswith("GARDE: --forme ne va pas avec --creer")
                 and not os.path.exists(os.path.join(tfo, "neuve.html"))), ("HAB1 : --forme refuse --creer par une GARDE") + "\n" + str(s)
        # Témoin : sans --forme, la même page recompte — la preuve que le dépôt ferait changer le total.
        code, s = appel(["page", fiches, page, "--date", "2026-01-06"])
        assert (code == 0 and total not in lire(page)), ("HAB1 : sans --forme, le total change (témoin)") + "\n" + str(s)


def projet_clos(dossier, liens=()):
    """Un projet à trois clos A, B, C : A et B à l'ancien format, C déjà lié à vlp.css ; `liens` :
    (plage, url) de lignes de ZONE:clos à lien, en plus d'une ligne sans lien par clos."""
    seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
             "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
    ecrire(os.path.join(dossier, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
    ecrire(os.path.join(dossier, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
           + "".join("| `%s.md` | chantier **clos** « %s », `%s1..%s1` |\n" % (x.lower(), x, x, x) for x in "ABC"))
    for x in "ABC":
        fiches = os.path.join(dossier, "ctx", "%s.md" % x.lower())
        page = os.path.join(dossier, "ctx", "artefacts", "%s.html" % x.lower())
        ecrire(fiches, seule % (x, x, x))
        appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", x, "--resultat", "R"])
        if x != "C":
            ecrire(page, avec_style_inline(lire(page)))
    rangs = [ligne_close(mod.arrondi(1500)).replace("Q1–Q2", "%s1" % x) for x in "ABC" if "%s1" % x not in dict(liens)]
    rangs += [ligne_close(mod.arrondi(1500)).replace("Q1–Q2", pl).replace("<td>Test ", '<td><a href="%s">Test</a> ' % u)
              for pl, u in liens]
    ecrire(os.path.join(dossier, "ctx", "artefacts", "feuille-de-route.html"),
           '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n' + "".join(rangs)
           + "        </tbody>\n      </table>\n")


def test_liens(tmp_path):
    """lien et liens (chantier HAB3) : l'URL en ligne d'une page, dans la section `## Lien` de son .md."""
    ua, ub, ub2 = ("https://claude.ai/artifact/%s" % k for k in ("aaa", "bbb", "bbb2"))
    with tempfile.TemporaryDirectory(dir=tmp_path) as tli:
        projet_clos(tli, [("A1", ua), ("B1", ub), ("B1", ub2)])
        art = os.path.join(tli, "ctx", "artefacts")
        md_c = os.path.join(art, "c.md")
        avant = mod.lire_abri(md_c)
        code, s = appel(["lien", os.path.join(art, "c.html"), "https://claude.ai/artifact/ccc"])
        apres = mod.lire_abri(md_c)
        assert (code == 0 and s.startswith("LIEN écrit") and apres["lien"] == "https://claude.ai/artifact/ccc"
                 and dict(apres, lien="") == avant and "## Lien\nhttps://claude.ai/artifact/ccc\n" in lire(md_c)), ("HAB3 : lien écrit l'URL, lire_abri la relit, le reste intact"
                 " — mutant : texte_abri oublie la section") + "\n" + str((s, apres, avant))
        code, s = appel(["lien", os.path.join(art, "c.html"), "https://claude.ai/artifact/ccc"])
        assert (code == 0 and s.startswith("LIEN déjà")), ("HAB3 : lien relancé, déjà") + "\n" + str(s)
        code, s = appel(["lien", os.path.join(art, "c.html"), "pas-une-url"])
        assert (code == 1 and s.startswith("GARDE: lien inattendu")), ("HAB3 : lien refuse une URL inattendue") + "\n" + str(s)
        code, s = appel(["liens", tli])
        assert (code == 0 and s.splitlines()[-1] == "LIENS 1 écrits · 0 déjà · 1 doublons · 1 sans lien · 0 sans page"
                 and "DOUBLON %s · %s · %s" % (os.path.join(art, "b.html"), ub, ub2) in s
                 and mod.lire_abri(os.path.join(art, "a.md"))["lien"] == ua
                 and mod.lire_abri(os.path.join(art, "b.md"))["lien"] == ""), ("HAB3 : liens pose A, signale B en doublon, C sans lien dans la feuille") + "\n" + str(s)
        code, s = appel(["repeindre", tli, "--a-blanc"])
        assert (code == 0
                 and "REPEINTE %s · lien %s" % (os.path.join(art, "a.html"), ua) in s
                 and "2 repeintes · 1 avec lien · 1 sans lien" in s), ("HAB3 : repeindre lit le lien du .md") + "\n" + str(s)


FICHES_FEU7 = """# Chantier FEU7

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — a
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P2 -->
## P2 [ ] — b
**Critère de fin**
<!-- /FICHE -->
"""


def test_lien_feuille_de_route(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj = os.path.join(tab, "proj")
        fiches = os.path.join(proj, "p.md")
        page = os.path.join(proj, "artefacts", "p.html")
        carte = os.path.join(proj, "CHANTIER.md")
        ecrire(fiches, FICHES_FEU7)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/route\n")
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        assert (code == 0
                 and 'Proj · fiches P1–P2 · <a href="https://exemple/route">la feuille de route</a></div>' in html
                 and html.count("la feuille de route</a>") == 1), ("FEU7 : eyebrow, un lien vers la feuille de route") + "\n" + str(html)
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0 and html.count("la feuille de route</a>") == 1
                 and 'Proj · fiches P1–P2 · <a href="https://exemple/route">la feuille de route</a></div>' in html), ("FEU7 : régénérée deux fois, toujours un seul lien — mutant : garde d'unicité retirée") + "\n" + str(html)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/autre\n")
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0
                 and 'Proj · fiches P1–P2 · <a href="https://exemple/autre">la feuille de route</a></div>' in html
                 and "exemple/route" not in html and html.count("la feuille de route</a>") == 1), ("FEU7 : URL changée, la nouvelle seule") + "\n" + str(html)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : aucun\n")
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0
                 and "la feuille de route" not in html and "Proj · fiches P1–P2</div>" in html), ("FEU7 : « aucun », le lien se retire") + "\n" + str(html)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/route\n")
        ecrire(fiches, lire(fiches) + '\n<!-- FICHE:P3 -->\n## P3 [ ] — c\n**Critère de fin**\n<!-- /FICHE -->\n')
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0
                 and 'Proj · fiches P1–P3 · <a href="https://exemple/route">la feuille de route</a></div>' in html), ("FEU7 : la plage reste intacte à côté du lien") + "\n" + str(html)


def test_publie(tmp_path):
    """publie (chantier JNT3) : la ligne FILES ne nomme que les joints changés depuis la
    dernière publication réussie de la page, notée par `attente hook`."""
    def files_de(s):
        for l in s.splitlines():
            if l.startswith("FILES "):
                return json.loads(l[len("FILES "):])
        return None

    def hook(d):
        return mod.cmd_attente_hook(io.StringIO(json.dumps(d)), io.StringIO())

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p = os.path.join(t, "proj")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
        art = os.path.join(p, "context AI", "artefacts")
        fiches, page, notes = os.path.join(t, "p.md"), os.path.join(art, "p.html"), os.path.join(art, "publie")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        files = files_de(s) or {}
        assert (code == 0 and sorted(files) == ["vlp.css", "vlp.js"]), ("JNT3 : page jamais notée — FILES nomme les 2 joints") + "\n" + str(s)
        # vlp.js en `{from}` relatif au dossier courant : les deux formes du paramètre `files`
        passe = {"vlp.css": files.get("vlp.css"), "vlp.js": {"from": os.path.relpath(files.get("vlp.js", t), p)}}
        succes = {"hook_event_name": "PostToolUse", "tool_name": "Artifact", "cwd": p,
                  "tool_input": {"file_path": page, "url": "https://claude.ai/artifact/AAA", "files": passe}}
        hook(dict(succes, hook_event_name="PostToolUseFailure", error="Nothing was published or removed"))
        assert (not os.path.exists(notes)), ("JNT3 : une publication refusée ne note rien") + "\n" + str(str(os.listdir(art)))
        hook(succes)
        lignes = mod.lignes_de(notes) if os.path.exists(notes) else []
        assert ([l.split("\t")[:2] for l in lignes] == [["p.html", "vlp.css"], ["p.html", "vlp.js"]]), ("JNT3 : publication réussie — publie a 2 lignes, page p.html, chemin et {from}") + "\n" + str(str(lignes))
        code, s = appel(["page", fiches, page])
        assert (files_de(s) == {}), ("JNT3 : rien de changé — FILES {} — mutant : ligne_files qui ignore la note") + "\n" + str(s)
        ecrire(notes, "".join(l.replace("\tvlp.css\t", "\tvlp.css\t0") + "\n" if "\tvlp.css\t" in l else l + "\n"
                              for l in lignes))
        code, s = appel(["page", fiches, page])
        assert (sorted(files_de(s) or {"x": 0}) == ["vlp.css"]), ("JNT3 : vlp.css changé depuis la note — FILES ne nomme que lui") + "\n" + str(s)
        hook(dict(succes, tool_input={"file_path": page, "files": {"vlp.css": files.get("vlp.css")}}))
        code, s = appel(["page", fiches, page])
        assert (files_de(s) == {} and len(mod.lignes_de(notes)) == 2), ("JNT3 : republié avec vlp.css seul — vlp.js garde sa note, FILES {}") + "\n" + str(s + lire(notes))


def test_iso5_etat_texte(tmp_path):
    """ISO5 : `etat <fichier d'état> --texte <fichier>` ajoute le texte à la fin, une ligne vide avant, CRLF gardé ;
    un texte vide, un texte ou un fichier d'état absent : `GARDE:`, sort 1, rien d'écrit."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        etat, crlf, texte, vide = (os.path.join(tr, n) for n in ("08-etat.md", "crlf.md", "t.txt", "v.txt"))
        ecrire(etat, "# État\n\n- a\n")
        ecrire(texte, "\n- ISO9 : b\n  suite\n\n")
        ecrire(vide, "  \n\n")
        with open(crlf, "wb") as f:
            f.write(b"- a\r\n\r\n\r\n")
        ajout = appel(["etat", etat, "--texte", texte])
        ajout_crlf = appel(["etat", crlf, "--texte", texte])
        gardes = [appel(["etat", etat, "--texte", vide]), appel(["etat", etat, "--texte", os.path.join(tr, "non.txt")]),
                  appel(["etat", os.path.join(tr, "non.md"), "--texte", texte])]
        apres = lire(etat)
        with open(crlf, "rb") as f:
            octets = f.read()
        cree = os.path.exists(os.path.join(tr, "non.md"))
    assert (ajout == (0, "ÉTAT ajouté 2 ligne(s) à %s\n" % etat) and apres == "# État\n\n- a\n\n- ISO9 : b\n  suite\n"), ("ISO5 : etat --texte → ÉTAT ajouté 2 ligne(s), le texte à la fin, une ligne vide avant") + "\n" + str((ajout, apres))
    assert (ajout_crlf[0] == 0 and octets == b"- a\r\n\r\n- ISO9 : b\r\n  suite\r\n"), ("ISO5 : un fichier d'état en CRLF le reste, une seule ligne vide avant le texte") + "\n" + str((ajout_crlf, octets))
    assert ([c for c, _ in gardes] == [1, 1, 1] and gardes[0][1].startswith("GARDE: texte vide")
             and gardes[1][1].startswith("GARDE: texte absent") and gardes[2][1].startswith("GARDE: fichier d'état absent")
             and apres.endswith("  suite\n") and not cree), ("ISO5 : texte vide, texte absent, fichier d'état absent → GARDE:, sort 1, rien d'écrit — mutant : pas de "
             "garde du vide") + "\n" + str((gardes, apres, cree))
