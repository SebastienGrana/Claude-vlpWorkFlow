"""`noyau/notes.py` : l'abri des notes et du journal, l'état, les renvois, la forme des pages et leurs liens — migré de
l'ancienne suite maison (REF58). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic — sauf ceux que `RUF2` a séparés, sans message : pytest montre les valeurs comparées.
"""
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

import pytest
from aides import (
    CHANTIER,
    FICHES,
    FICHES_PLI2,
    FICHES_PLI5,
    OUVERT,
    QFICHES,
    SCRIPTS,
    T0,
    appel,
    ecrire,
    ligne_close,
    lire,
    mod,
    transcript,
)

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


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
        assert (appel(["renvois", t]) == (0, ("POIDS CLAUDE.md 14/100 · CHANTIER.md 2/50 · index 9/80\n"
                 "RENVOIS 3 nommés · 0 absents\n"))), ("renvois : tout présent, poids sous seuil") + "\n" + str(appel(["renvois", t]))
        ecrire(os.path.join(t, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n" + "x\n" * 49)
        code, s = appel(["renvois", t])
        assert code == 0
        assert (s.startswith(
            "AVERTISSEMENT: CHANTIER.md 51 lignes > 50\nPOIDS CLAUDE.md 14/100 · CHANTIER.md 51/50 · index 9/80\n"))
        os.remove(os.path.join(t, "CLAUDE.md"))
        code, s = appel(["renvois", t])
        assert code == 0
        assert "POIDS CLAUDE.md absent/100 · CHANTIER.md 51/50" in s
        ecrire(os.path.join(t, "CLAUDE.md"),
               "# P\n\n| hors routage | `perdu.md` |\n\n## Routage — ouvrir ceci\n\n| La tâche | Ouvrir |\n|---|---|\n"
               "| lire `vlp.py` | `ctx/01-a.md` |\n| lancer | **`/vlp:chantier`** |\n\n## Économie\n\n| x | `loin.md` |\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `99-mort.md` | jamais |\n")
        code, s = appel(["renvois", t])
        assert code == 1
        assert s.startswith("ABSENT: ctx/00-INDEX.md:3: 99-mort.md\n")
        assert s.endswith("index 3/80\nRENVOIS 2 nommés · 1 absents\n")
        os.remove(os.path.join(t, "CHANTIER.md"))
        assert (appel(["renvois", t])[0] == 1), ("renvois : pas équipé") + "\n" + str(appel(["renvois", t]))


def test_renvois_garde(tmp_path):
    """TAB2 : une ligne d'index qui n'a pas le nombre de cellules de son en-tête arrête `renvois`."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as d:
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(d, "ctx", "01-a.md"), "a\n")
        tete = "| Fichier | a | b | c | d |\n|---|---|---|---|---|\n| `01-a.md` | x \\| y | b | c | d |\n"
        ecrire(os.path.join(d, "ctx", "00-INDEX.md"), tete)
        assert (appel(["renvois", d]) == (0, ("POIDS CLAUDE.md absent/100 · CHANTIER.md 2/50 · index 3/80\n"
                 "RENVOIS 1 nommés · 0 absents\n"))), ("TAB2 : renvois, table saine et \\| gardé") + "\n" + str(appel(["renvois", d]))
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
        assert code == 0
        assert s == "ABRI %s · résultat 1 · notes 2 · journal 3 · bilan 1\n" % md
        parts = mod.lire_abri(md)
        assert parts["titre"] == "Abri & journal"
        assert parts["resultat"] == "Notes <à l'abri>"
        assert parts["notes"] == {"ABR1": "test 3/3 & pyright 0", "ABR2": "dépend de ABR1"}
        assert (parts["journal"] == [("2026-09-25", "Pierre & Paul"), ("2026-09-26", "E3 : allowed-tools muet"),
                                          ("2026-09-26", "sur deux lignes")])
        assert parts["bilan"] == ["Livré : un .md & une page"]
        with open(page, "rb") as f:
            assert (f.read() == PAGE_ABR.encode("utf-8")), ("ABR1 : la page identique octet pour octet") + "\n" + "page modifiée"
        mod.ecrire_abri(md, parts)
        assert (mod.lire_abri(md) == parts), ("ABR1 : écrire puis relire redonne les mêmes parts") + "\n" + str(lire(md))
        code, s = appel(["abri", page])
        assert code == 0
        assert s == "DÉJÀ %s\n" % md
        code, s = appel(["abri", os.path.join(tab, "absente.html")])
        assert code == 1
        assert s.startswith("GARDE:")


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
        code, _ = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert code == 0
        assert os.path.exists(md)
        code, _ = appel(["page", fiches, page, "--note", "P1", "x", "--journal", "y", "--date", "2026-09-26"])
        assert code == 0
        assert mod.lire_abri(md)["notes"] == {"P1": "x"}
        assert mod.lire_abri(md)["journal"] == [("2026-09-26", "y")]
        html_avant = lire(page)
        os.remove(page)
        code, _ = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        assert code == 0
        assert '<span class="note">x</span>' in html
        assert '<time datetime="2026-09-26">2026-09-26</time><span>y</span>' in html
        assert "<p>R0</p>" in html
        assert mod.lire_abri(md)["notes"] == {"P1": "x"}
        assert mod.lire_abri(md)["journal"] == [("2026-09-26", "y")]

        # Une page ancienne, sans .md : elle garde ses notes (pas de perte à l'amorçage).
        ancienne = os.path.join(tab, "artefacts", "anc.html")
        ecrire(ancienne, html_avant)
        fiches_anc = os.path.join(tab, "anc.md")
        ecrire(fiches_anc, FICHES_ABR2)
        assert (not os.path.exists(mod.chemin_abri(ancienne))), ("ABR2 : pas de .md avant ce test") + "\n" + ""
        code, _ = appel(["page", fiches_anc, ancienne, "--date", "2026-09-27"])
        html = lire(ancienne)
        assert code == 0
        assert '<span class="note">x</span>' in html
        assert '<span>y</span>' in html
        assert os.path.exists(mod.chemin_abri(ancienne))
        assert mod.lire_abri(mod.chemin_abri(ancienne))["notes"] == {"P1": "x"}
        # Le .md prime désormais sur l'ancienne page : une note différente dans le .md l'emporte
        # — mutant : lire la note dans l'ancienne page (`anciens`) au lieu du .md.
        code, _ = appel(["page", fiches_anc, ancienne, "--note", "P1", "z", "--date", "2026-09-27"])
        html = lire(ancienne)
        assert code == 0
        assert '<span class="note">z</span>' in html
        assert '<span class="note">x</span>' not in html
        # Une note retirée du .md disparaît de la page — mutant : retomber sur l'ancienne page (`anciens`),
        # qui la garde encore. C'est le seul cas où le mutant se distingue d'une note passée par --note.
        md_anc = mod.chemin_abri(ancienne)
        parts_anc = mod.lire_abri(md_anc)
        del parts_anc["notes"]["P1"]
        mod.ecrire_abri(md_anc, parts_anc)
        code, _s = appel(["page", fiches_anc, ancienne, "--date", "2026-09-28"])
        html = lire(ancienne)
        assert code == 0
        assert '<span class="note">' not in html.split("<ul class=\"journal\">")[0].split('id">P1')[1].split("</li>")[0]


def test_vlp_css_recopie(tmp_path):
    source = pathlib.Path(os.path.join(ICI, "..", "templates", "vlp.css")).read_bytes()

    # `page --creer`, puis `page` sans --creer (régénération) : les deux recopient.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        css = os.path.join(tab, "artefacts", "vlp.css")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert code == 0
        assert os.path.isfile(css)
        assert pathlib.Path(css).read_bytes() == source
        assert "CSS %s\n" % css in s
        with open(css, "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        assert code == 0
        assert pathlib.Path(css).read_bytes() == source

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
        ecrire(fdr, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8"))
        css = os.path.join(proj, "ctx", "artefacts", "vlp.css")
        code, s = appel(["feuille", proj])
        assert code == 0
        assert os.path.isfile(css)
        assert pathlib.Path(css).read_bytes() == source
        assert "CSS %s\n" % css in s

    # Les deux gabarits ne portent plus de <style> inline (chantier PLI, fiche PLI2).
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = pathlib.Path(os.path.join(ICI, "..", "templates", nom)).read_text(encoding="utf-8")
        assert gabarit.count("<style") == 0
        assert 'href="vlp.css"' in gabarit


def avec_style_inline(html):
    """Une page déjà régénérée (donc liée à vlp.css), avec son <style> d'avant PLI3
    remis en place — comme une page publiée avant ce chantier, jamais régénérée depuis."""
    css = pathlib.Path(os.path.join(ICI, "..", "templates", "vlp.css")).read_text(encoding="utf-8")
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
        assert code == 0
        assert "<style>" not in html
        assert html.count('href="vlp.css"') == 1
        code, s = appel(["comparer", ancienne, page])
        assert code == 0
        assert "PERDU:" not in s
        assert s.rstrip().startswith("COMPARER 0 perdus")
        code, s = appel(["page", fiches, page])
        assert code == 0
        assert lire(page).count('href="vlp.css"') == 1


def fiche_r(ident, case, dep, fichiers):
    """Une fiche `ident` à la case `case`, qui dépend de `dep`, avec sa ligne **Fichiers** si `fichiers` n'est pas vide."""
    return ("<!-- FICHE:%s -->\n## %s [%s] — Fiche %s\n**Dépend de** : %s\n%s**Critère de fin**\nx\n"
            "<!-- /FICHE -->\n\n" % (ident, ident, case, ident, dep, "**Fichiers** : %s\n" % fichiers if fichiers else ""))


def fichier_r(faites):
    """Le chantier R à sept fiches : R1 faite, et celles de `faites` parmi R2, R3, R4, R7."""
    return ("# Chantier R\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
            + fiche_r("R1", "x", "rien.", "`a.py`")
            + fiche_r("R2", "x" if "R2" in faites else " ", "`R1`.", "`scripts/a.py`, `b.css`")
            + fiche_r("R3", "x" if "R3" in faites else " ", "`R1`.", "`c.js` (nouveau) — et rien d'autre.")
            + fiche_r("R4", "x" if "R4" in faites else " ", "rien.", "`templates/b.css` (`.x > y` `:12`), `compte_todo`")
            + fiche_r("R5", " ", "`R2`, `R3`,\n`R4` et `PLI9`.", "`d.md`")
            + fiche_r("R6", " ", "`R1`.", "")
            + fiche_r("R7", "x" if "R7" in faites else " ", "`R3`.", "`e.md`"))


def cartes_r(html):
    """{identifiant: <li> de sa carte} des fiches d'une page."""
    return {m.group(1): m.group(0)
            for m in re.finditer(r'<li class="fiche".*?<span class="id">(\w+)</span>.*?</li>', html, re.S)}


def tete_r(attributs, ident):
    """Le début attendu de la carte `ident`, avec ses `attributs`."""
    return '<li class="fiche"%s><span class="gauche"><span class="id">%s</span></span>' % (attributs, ident)


def dit_r(li, ident, texte):
    """Vrai si la carte `ident` de `li` porte l'état `texte` ; faux si la carte manque."""
    return ('<span class="etat">%s</span>' % texte) in li.get(ident, "")


def libelle_r(html, ident, texte):
    """`html` où l'état de la carte `ident` est remplacé par `texte`, à la main."""
    return re.sub(r'(<span class="id">%s</span>.*?<span class="etat">)[^<]*' % ident,
                  lambda m: m.group(1) + texte, html, count=1, flags=re.S)


def page_r(tpp):
    """Le chantier R écrit, sa page créée ; rend `(fiches, page, code de page --creer)`."""
    fiches = os.path.join(tpp, "r.md")
    page = os.path.join(tpp, "artefacts", "r.html")
    ecrire(fiches, fichier_r(()))
    code, _ = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
    return fiches, page, code


def test_pretes_et_paralleles(tmp_path):
    """Les fiches prêtes, celles qui attendent, et celles qui peuvent partir en même temps ; la page refaite est stable."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tpp:
        fiches, page, code = page_r(tpp)
        html = lire(page)
        li = cartes_r(html)
        assert code == 0
        assert li.get("R5", "").startswith(tete_r(" data-attend", "R5"))
        assert dit_r(li, "R5", "Après R2, R3, R4")
        assert li.get("R7", "").startswith(tete_r(" data-attend", "R7"))
        assert dit_r(li, "R7", "Après R3")
        assert dit_r(li, "R4", "À lancer")
        assert dit_r(li, "R6", "À lancer")
        assert all('class="dep' not in c for c in li.values())
        assert li.get("R2", "").startswith(tete_r(' data-etat="encours"', "R2"))
        assert dit_r(li, "R2", "En cours · R3 peut partir en même temps")
        assert dit_r(li, "R3", "À lancer · en même temps que R2")
        assert all("même temps" not in li.get(i, "même temps") for i in ("R1", "R4", "R5", "R6", "R7"))
        assert mod.lis_page(html).get("R2", ("?",))[0] == "encours"
        assert mod.lis_page(html).get("R5", ("?",))[0] is None
        code, _ = appel(["page", fiches, page])
        code2, _s2 = appel(["page", fiches, page, "--forme"])
        assert code == 0
        assert code2 == 0
        assert lire(page) == html


def test_pretes_page_d_avant(tmp_path):
    """Une page d'avant : « à faire » (avant BTN), « à lancer » et « après » en minuscules (v12 de la page BTN), une
    phrase périmée, et un libellé écrit à la main ; puis les fiches faites avancent « en même temps »."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tpp:
        fiches, page, _code = page_r(tpp)
        vieille = lire(page)
        for ident, texte in (("R6", "abandonnée"), ("R4", "à lancer"), ("R3", "À lancer · en même temps que R9"),
                             ("R5", "à faire"), ("R7", "après R3")):
            vieille = libelle_r(vieille, ident, texte)
        ecrire(page, vieille)
        code, _ = appel(["page", fiches, page, "--forme"])
        li = cartes_r(lire(page))
        assert code == 0
        assert dit_r(li, "R3", "À lancer · en même temps que R2")
        assert dit_r(li, "R4", "À lancer")
        assert dit_r(li, "R5", "Après R2, R3, R4")
        assert dit_r(li, "R7", "Après R3")
        assert dit_r(li, "R6", "abandonnée")
        ecrire(fiches, fichier_r(("R2", "R3")))
        appel(["page", fiches, page])
        li = cartes_r(lire(page))
        assert dit_r(li, "R4", "En cours · R7 peut partir en même temps")
        assert dit_r(li, "R7", "À lancer · en même temps que R4")
        assert dit_r(li, "R5", "Après R4")
        ecrire(fiches, fichier_r(("R2", "R3", "R4", "R7")))
        appel(["page", fiches, page])
        assert (all("même temps" not in c for c in cartes_r(lire(page)).values())), ("en même temps : une seule prête avec des fichiers — aucun « en même temps »") + "\n" + str(lire(page))


def test_pretes_attend_et_plage(tmp_path):
    """En cours, mais une dépendance plus bas n'est pas faite : l'état reste, puis « attend » ; une plage « `P1` à
    `P4` » se déplie."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tpp:
        fiches = os.path.join(tpp, "r.md")
        ecrire(fiches, "# Chantier S\n\n" + fiche_r("S1", " ", "`S2`, `S3`, `S4`.", "`f.md`")
               + "".join(fiche_r(i, " ", "rien.", "`g.md`") for i in ("S2", "S3", "S4")))
        code, _ = appel(["page", fiches, os.path.join(tpp, "artefacts", "s.html"), "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        li = cartes_r(lire(os.path.join(tpp, "artefacts", "s.html")))
        assert code == 0
        assert li.get("S1", "").startswith(tete_r(' data-etat="encours" data-attend', "S1"))
        assert dit_r(li, "S1", "En cours · attend S2, S3, S4")
        # Une plage « `P1` à `P4` » (cadrage d'ACA, 2026-10-11) : lue en deux noms, P5 se disait « À lancer »,
        # sans data-attend, alors que P2 et P3, au milieu, ne sont pas faites.
        ecrire(fiches, "# Chantier P\n\n" + "".join(fiche_r(i, c, "rien.", "`%s.md`" % i) for i, c in
                                                     (("P1", "x"), ("P2", " "), ("P3", " "), ("P4", "x")))
               + fiche_r("P5", " ", "`P1` à `P4`.", "`p5.md`"))
        code, _s = appel(["page", fiches, os.path.join(tpp, "artefacts", "p.html"), "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        li = cartes_r(lire(os.path.join(tpp, "artefacts", "p.html")))
        assert code == 0
        assert li.get("P5", "").startswith(tete_r(" data-attend", "P5"))
        assert dit_r(li, "P5", "Après P2, P3")
        assert mod.deplier_plages("`P4` à `P2`") == "`P4` à `P2`"


def test_journal_replie(tmp_path):
    for n, visibles, repliees in ((7, 3, 4), (2, 2, 0)):
        with tempfile.TemporaryDirectory(dir=tmp_path) as tjr:
            fiches = os.path.join(tjr, "q.md")
            page = os.path.join(tjr, "artefacts", "q.html")
            ecrire(fiches, FICHES_PLI5)
            argv = ["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"]
            for k in range(1, n + 1):
                argv += ["--journal", "j%d" % k]
            code, _s = appel(argv)
            html = lire(page)
            ancien = re.search(r'<details class="journal-ancien">.*?</details>', html, re.S)
            premier = re.search(r'<ul class="journal">(.*?)</ul>', html, re.S)
            vus = premier.group(1).count("<li>") if premier else -1
            caches = ancien.group(0).count("<li>") if ancien else 0
            textes = [t for _, t in mod.abri_de_page(html)["journal"]]
            assert code == 0
            assert vus == visibles
            assert caches == repliees
            assert bool(ancien) == bool(repliees)
            assert textes == ["j%d" % k for k in range(1, n + 1)]
            assert not ancien or "%d entrées plus anciennes" % repliees in ancien.group(0)


def test_bilan_en_haut(tmp_path):
    gabarit = pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-chantier.html")).read_text(encoding="utf-8")
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
        code, _ = appel(["clore", tb, "--livre", "fini", "--date", "2026-09-27"])
        html = lire(page)
        assert code == 0
        assert html.count("ZONE:bilan") == 1
        assert html.index("ZONE:bilan") < html.index("ZONE:fiches")
        assert "<section>\n    <h2>Chantier clos le 2026-09-27</h2>" in html
        # un clos d'avant PLI6 : bilan visible, mais en bas — `page` le remonte aussi (dette PLI)
        j = html.index("  <!-- ZONE:bilan")
        fin_b = html.index("  </section>\n", j) + len("  </section>\n")
        clos_bas = (html[:j] + html[fin_b:]).replace("  <footer>", html[j:fin_b] + "\n  <footer>", 1)
        ecrire(page, clos_bas)
        code, _ = appel(["page", os.path.join(tb, "ctx", "50-u.md"), page])
        html = lire(page)
        assert code == 0
        assert clos_bas.index("ZONE:bilan") > clos_bas.index("ZONE:fiches")
        assert html.count("ZONE:bilan") == 1
        assert html.index("ZONE:bilan") < html.index("ZONE:fiches")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tbo:
        # témoin : une page ouverte à l'ancienne forme (bilan caché, en bas) n'est pas touchée
        ouverte = os.path.join(tbo, "artefacts", "q.html")
        fiches_o = os.path.join(tbo, "q.md")
        ecrire(fiches_o, FICHES_PLI5)
        ecrire(ouverte, ancienne)
        code, _s = appel(["page", fiches_o, ouverte])
        html = lire(ouverte)
        assert code == 0
        assert html.index("ZONE:bilan") > html.index("ZONE:fiches")
        assert "<section hidden>\n    <h2>Chantier clos le" in html


FORME_C1, FORME_C2 = "≈1,1k (1 111) · 1 tours · 0,01 $", "≈2,2k (2 222) · 2 tours · 0,02 $"
FORME_TOTAL = "Coût du chantier : ≈11,3M (11 262 523) · 42 tours · 3,40 $"
FORME_HORS = "Hors fiches : ≈5,0k (5 000) · 1 tours · 0,05 $"


def depot_forme(tfo, init_git):
    """Un dépôt à trois commits de fiche et une transcription, la page du chantier Q créée ; rend `(fiches, page)`."""
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
    return fiches, page


def ancien_format(html):
    """`html` à l'ancien format : style dans la page, fiches à plat, bilan visible en bas, chiffres d'une autre mesure
    (FORME_C1, FORME_C2, FORME_TOTAL, FORME_HORS), un libellé et un comptage écrits à la main."""
    html = avec_style_inline(html)
    for balise in ("<details open>", "<details>", "</details>", "<summary>", "</summary>"):
        html = html.replace(balise, "")
    html = re.sub(r'<span class="cout mono">.*?</span>', "", html)
    # Écrits à la main sur les vieilles pages (18-evals, 11-conso du kit) : un libellé, un comptage.
    html = re.sub(r'(<span class="id">Q2</span>.*?<span class="etat">)Faite(</span>)', r"\1abandonnée\2", html, count=1, flags=re.S)
    html = re.sub(r'(<p class="mono" style="margin-top:.5rem">).*?(</p>)', r"\g<1>2 fiches · Q2 abandonnée · clos\2", html, count=1)
    for q, c in (("Q1", FORME_C1), ("Q2", FORME_C2)):
        html = re.sub(r'(<span class="id">%s</span>.*?)(\s*</li>)' % q,
                      lambda m, c=c: m.group(1) + '\n        <span class="cout mono">%s</span>' % c + m.group(2),
                      html, count=1, flags=re.S)
    html = re.sub(r'<p class="mono cout-total">.*?</p>', '<p class="mono cout-total">%s</p>' % FORME_TOTAL, html, flags=re.S)
    html = re.sub(r'<p class="mono cout-hors">.*?</p>', '<p class="mono cout-hors">%s</p>' % FORME_HORS, html, flags=re.S)
    i = html.index("  <!-- ZONE:bilan")
    fin = html.index("  </section>\n", i) + len("  </section>\n\n")
    bloc = html[i:fin].replace("<section hidden>", "<section>", 1).replace("<p></p>", "<p>Fini.</p>", 1)
    return (html[:i] + html[fin:]).replace("  <footer>", bloc + "  <footer>", 1)


def page_ancienne(tfo, init_git):
    """La page du chantier Q remise à l'ancien format sur le disque ; rend `(fiches, page, html ancien)`."""
    if not shutil.which("git"):
        pytest.skip("git absent — page --forme n'est pas testée")
    fiches, page = depot_forme(tfo, init_git)
    html = ancien_format(lire(page))
    assert "<style>" in html
    assert "<details" not in html
    assert FORME_TOTAL in html
    assert html.index("ZONE:bilan") > html.index("ZONE:fiches")
    ecrire(page, html)
    return fiches, page, html


def test_forme(tmp_path, init_git):
    """page --forme (chantier HAB1) : la forme d'une page ancienne refaite, ses chiffres gardés,
    même dans un dépôt dont les commits de fiche feraient changer le coût."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tfo:
        fiches, page, html = page_ancienne(tfo, init_git)
        code, s = appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        apres = lire(page)
        lu = mod.lis_page(apres)
        assert code == 0
        assert apres.count(FORME_TOTAL) == 1
        assert apres.count(FORME_HORS) == 1
        assert "total ≈11,3M (11 262 523) · 42 tours · 3,40 $" in s
        assert lu["Q1"][2] == FORME_C1
        assert lu["Q2"][2] == FORME_C2
        assert "<style>" not in apres
        assert apres.count('href="vlp.css"') == 1
        assert apres.count("<details") >= 2
        assert apres.index("ZONE:bilan") < apres.index("ZONE:fiches")
        assert "<p>Fini.</p>" in apres
        assert "<span class=\"etat\">abandonnée</span>" in apres
        assert "2 fiches · Q2 abandonnée · clos" in apres
        assert 'Mis à jour le <span class="mono">2026-01-05</span>' in apres
        ecrire(os.path.join(tfo, "avant.html"), html)
        code, s = appel(["comparer", os.path.join(tfo, "avant.html"), page])
        assert code == 0
        assert s.rstrip().startswith("COMPARER 0 perdus")
        code, s = appel(["vigile", page])
        assert code == 0
        assert s.startswith("PAGE SAINE")


def test_forme_rejouee(tmp_path, init_git):
    """page --forme rejouée : rien ne bouge ; avec --creer : refusée ; sans --forme, la même page recompte — la preuve
    que le dépôt ferait changer le total."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tfo:
        fiches, page, _html = page_ancienne(tfo, init_git)
        appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        avant = lire(page)
        code, s = appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        assert code == 0
        assert lire(page) == avant
        code, s = appel(["page", fiches, os.path.join(tfo, "neuve.html"), "--forme", "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        assert code == 1
        assert s.startswith("GARDE: --forme ne va pas avec --creer")
        assert not os.path.exists(os.path.join(tfo, "neuve.html"))
        code, s = appel(["page", fiches, page, "--date", "2026-01-06"])
        assert code == 0
        assert FORME_TOTAL not in lire(page)


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
        assert code == 0
        assert s.startswith("LIEN écrit")
        assert apres["lien"] == "https://claude.ai/artifact/ccc"
        assert dict(apres, lien="") == avant
        assert "## Lien\nhttps://claude.ai/artifact/ccc\n" in lire(md_c)
        code, s = appel(["lien", os.path.join(art, "c.html"), "https://claude.ai/artifact/ccc"])
        assert code == 0
        assert s.startswith("LIEN déjà")
        code, s = appel(["lien", os.path.join(art, "c.html"), "pas-une-url"])
        assert code == 1
        assert s.startswith("GARDE: lien inattendu")
        code, s = appel(["liens", tli])
        assert code == 0
        assert s.splitlines()[-1] == "LIENS 1 écrits · 0 déjà · 1 doublons · 1 sans lien · 0 sans page"
        assert "DOUBLON %s · %s · %s" % (os.path.join(art, "b.html"), ub, ub2) in s
        assert mod.lire_abri(os.path.join(art, "a.md"))["lien"] == ua
        assert mod.lire_abri(os.path.join(art, "b.md"))["lien"] == ""
        code, s = appel(["repeindre", tli, "--a-blanc"])
        assert code == 0
        assert "REPEINTE %s · lien %s" % (os.path.join(art, "a.html"), ua) in s
        assert "2 repeintes · 1 avec lien · 1 sans lien" in s


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
        code, _s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        assert code == 0
        assert 'Proj · fiches P1–P2 · <a href="https://exemple/route">la feuille de route</a></div>' in html
        assert html.count("la feuille de route</a>") == 1
        code, _s = appel(["page", fiches, page])
        html = lire(page)
        assert code == 0
        assert html.count("la feuille de route</a>") == 1
        assert 'Proj · fiches P1–P2 · <a href="https://exemple/route">la feuille de route</a></div>' in html
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/autre\n")
        code, _s = appel(["page", fiches, page])
        html = lire(page)
        assert code == 0
        assert 'Proj · fiches P1–P2 · <a href="https://exemple/autre">la feuille de route</a></div>' in html
        assert "exemple/route" not in html
        assert html.count("la feuille de route</a>") == 1
        ecrire(carte, "# C\n\n- **artefact feuille de route** : aucun\n")
        code, _s = appel(["page", fiches, page])
        html = lire(page)
        assert code == 0
        assert "la feuille de route" not in html
        assert "Proj · fiches P1–P2</div>" in html
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/route\n")
        ecrire(fiches, lire(fiches) + '\n<!-- FICHE:P3 -->\n## P3 [ ] — c\n**Critère de fin**\n<!-- /FICHE -->\n')
        code, _s = appel(["page", fiches, page])
        html = lire(page)
        assert code == 0
        assert 'Proj · fiches P1–P3 · <a href="https://exemple/route">la feuille de route</a></div>' in html


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
        assert code == 0
        assert sorted(files) == ["vlp.css", "vlp.js"]
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
        assert files_de(s) == {}
        assert len(mod.lignes_de(notes)) == 2


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
    assert ajout == (0, "ÉTAT ajouté 2 ligne(s) à %s\n" % etat)
    assert apres == "# État\n\n- a\n\n- ISO9 : b\n  suite\n"
    assert ajout_crlf[0] == 0
    assert octets == b"- a\r\n\r\n- ISO9 : b\r\n  suite\r\n"
    assert [c for c, _ in gardes] == [1, 1, 1]
    assert gardes[0][1].startswith("GARDE: texte vide")
    assert gardes[1][1].startswith("GARDE: texte absent")
    assert gardes[2][1].startswith("GARDE: fichier d'état absent")
    assert apres.endswith("  suite\n")
    assert not cree
