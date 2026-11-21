"""`noyau/niveau.py` : `niveau` et ses écarts, l'attente de publication, la comparaison des pages, `AILLEURS=` — la
décision sans Git (REF47) puis les commandes, migré de l'ancienne suite maison (REF51). Chaque `assert` garde le
libellé d'origine de son `verifier` en tête de son message (REF5), puis le diagnostic.
"""
import datetime
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
    CARTE_MATIN,
    CARTE_NIV3,
    CHANTIER,
    ETAT_MATIN,
    ETAT_NIV,
    FICHES,
    GABARIT_FEUILLE,
    GABARIT_VLPCSS,
    INDEX_NIV3,
    JOUR_MATIN,
    OUVERT,
    SCRIPTS,
    appel,
    ecrire,
    ligne_close,
    lire,
    mod,
)
from noyau import niveau

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

def test_source_ignore():
    assert niveau.source_ignore(".gitignore:3:context AI/\tcontext AI/a.md\n") == ".gitignore:3"   # le fichier et sa ligne : « ignoré par .gitignore:3 »
    assert niveau.source_ignore("C:/x/.git/info/exclude:1:*.md\tz.md") == "C:/x/.git/info/exclude:1"
    assert niveau.source_ignore("") == "?"


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


def rendu(depart):
    s = io.StringIO()
    mod.carte(depart, s)
    return s.getvalue()


def test_niveau_git(tmp_path, init_git):
    """NUI36 : l'étape `git` de `niveau` — ignoré avec sa ligne de `.gitignore`, non ajouté, ligne « kit » à chemin
    de machine, tout suivi sans écart, hors Git sans écart ; `--ecrire` ne corrige rien."""
    def git(d, *args):
        subprocess.run(["git"] + list(args), cwd=d, capture_output=True, check=True)

    def ecarts_git(d, ecrire=False):
        s = io.StringIO()
        mod.cmd_niveau(mod.argparse.Namespace(projet=d, date="2026-10-08", ecrire=ecrire), s)
        return [l for l in s.getvalue().split("\n") if l.startswith(("ÉCART: git:", "CORRIGÉ: git:"))]

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p = os.path.join(t, "p")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pn", "ctx/") + "- **kit** : le plugin vlp\n")
        ecrire(os.path.join(p, "CLAUDE.md"), "# p\n")
        ecrire(os.path.join(p, "ctx", "08-etat.md"), "# état\n")
        ecrire(os.path.join(p, "ctx", "00-INDEX.md"), "# Index\n")
        assert (ecarts_git(p) == []), ("niveau git : hors Git, aucun écart") + "\n" + str(ecarts_git(p))
        init_git(p)
        git(p, "add", "-A")
        assert (ecarts_git(p) == []), ("niveau git : tout suivi, aucun écart") + "\n" + str(ecarts_git(p))
        git(p, "rm", "-q", "--cached", "CHANTIER.md")
        ecrire(os.path.join(p, ".gitignore"), "# rien\nCHANTIER.md\n")
        ecrire(os.path.join(p, "ctx", "09-neuf.md"), "# neuf\n")
        e = ecarts_git(p)
        assert len(e) == 2
        assert e[0].startswith("ÉCART: git: CHANTIER.md — ignoré par .gitignore:2")
        assert e[1].startswith("ÉCART: git: ctx/09-neuf.md — non ajouté")
        assert (ecarts_git(p, ecrire=True) == e), ("niveau git : --ecrire ne corrige rien") + "\n" + str(ecarts_git(p, True))
        carte = mod.lire(os.path.join(p, "CHANTIER.md"))
        ecrire(os.path.join(p, "CHANTIER.md"), carte + "- **contexte dans Git** : non — dépôt public\n")
        s = io.StringIO()
        mod.ecarts_git(p, s)
        ecrire(os.path.join(p, "CHANTIER.md"), carte)
        assert ("EXPRÈS: git: 1 chemin(s) ignoré(s) exprès — CHANTIER.md, « contexte dans Git » : non — dépôt public ; "
                 "aucun écart compté\n" in s.getvalue())
        assert "ignoré par" not in s.getvalue()
        assert "ÉCART: git: ctx/09-neuf.md — non ajouté" in s.getvalue()
        ecrire(os.path.join(p, ".gitignore"), "# rien\n")
        git(p, "add", "-A")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pn", "ctx/") + "- **kit** : D:/Projets/kit, lié dans"
               " ~/.claude/skills/vlp\n")
        e = ecarts_git(p)
        assert len(e) == 1
        assert "la ligne « kit » porte un chemin de machine" in e[0]


def test_niveau_git_sauf(tmp_path, init_git):
    """Q24 (2026-10-25) : `- **contexte dans Git** : oui — sauf `<chemin>` (pourquoi)` déclare un ignoré exprès,
    chemin par chemin : une ligne `EXPRÈS: git:` pour lui, sans écart ; un ignoré qu'elle ne nomme pas reste un écart."""
    def git(d, *args):
        subprocess.run(["git"] + list(args), cwd=d, capture_output=True, check=True)

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p = os.path.join(t, "p")
        carte = CHANTIER % ("pn", "ctx/") + "- **kit** : le plugin vlp\n"
        ecrire(os.path.join(p, "CLAUDE.md"), "# p\n")
        ecrire(os.path.join(p, "ctx", "08-etat.md"), "# état\n")
        ecrire(os.path.join(p, "ctx", "00-INDEX.md"), "# Index\n")
        ecrire(os.path.join(p, "ctx", "ordre", "page.html"), "<p>régénérée</p>\n")
        ecrire(os.path.join(p, "ctx", "note.md"), "# note\n")
        ecrire(os.path.join(p, ".gitignore"), "ctx/ordre/\nctx/note.md\n")
        ecrire(os.path.join(p, "CHANTIER.md"), carte + "- **contexte dans Git** : oui — sauf `ctx/ordre/` (régénéré)\n")
        init_git(p)
        git(p, "add", "-A")
        s = io.StringIO()
        mod.ecarts_git(p, s)
        lignes = [l for l in s.getvalue().split("\n") if l.startswith(("ÉCART: git:", "EXPRÈS: git:"))]
        assert sorted(lignes) == ["EXPRÈS: git: ctx/ordre/ — CHANTIER.md, « contexte dans Git » : sauf ; aucun écart compté",
                          "ÉCART: git: ctx/note.md — ignoré par .gitignore:2 — à retirer à la main, puis ajouter"], (
            "Q24 niveau git : le chemin déclaré « sauf » est exprès, l'autre reste un écart") + "\n" + str(lignes)


def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


def test_niv2_ecarts(tmp_path):
    """Contrôler `niveau` : les catégories d'écart d'un projet en retard (NIV2)."""
    CARTE_SALE = """# Chantier courant

- **alias** : sale
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **méthode** : ${CLAUDE_PLUGIN_ROOT}/methode-chantier.md

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le |
|---|---|---|
| ctx/10-a.md | A1..A2 | 2026-01-01 |
"""
    INDEX_SALE = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
                  "| `99-fantome.md` | jamais, il n'existe pas |\n"
                  "| *(hors dossier)* `${CLAUDE_PLUGIN_ROOT}/methode-chantier.md` | la méthode |\n")

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "sale")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_SALE)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_SALE)
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)

        code, s = appel(["niveau", proj])
        cat = [l.split(":")[1].strip() for l in s.splitlines() if l.startswith("ÉCART:")]
        assert code == 1
        assert cat == ["renvois", "feuille", "variable", "variable", "clos"]
        assert ("ÉCART: renvois: ctx/00-INDEX.md:5: 99-fantome.md — nommé, introuvable\n" in s), ("NIV2 : le renvoi absent est nommé avec sa source et sa ligne") + "\n" + str(s)
        assert ("ÉCART: feuille: feuille de route introuvable :" in s), ("NIV2 : la feuille de route absente est un écart") + "\n" + str(s)
        assert "ÉCART: variable: CHANTIER.md:7 cite ${CLAUDE_PLUGIN_ROOT}" in s
        assert "08-etat.md:3" not in s
        assert ("ÉCART: clos: CHANTIER.md:9 —" in s), ("NIV2 : la table des clos est repérée à son titre") + "\n" + str(s)
        assert "POIDS CLAUDE.md absent/100 · CHANTIER.md 13/50 · index 6/80\n" in s
        assert s.rstrip().endswith("NIVEAU 5 écarts · 0 avertissements — %s" % proj)


CARTE_NETTE = """# Chantier courant

- **alias** : net
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **méthode** : methode-chantier.md, copie d'avant la règle

## Chantiers clos — dans l'index, pas ici
"""


INDEX_NET = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
             "| `08-etat.md` | on reprend |\n")


def test_niv2_a_niveau(tmp_path):
    """Contrôler `niveau` sur un projet à niveau, et un chemin introuvable (NIV2)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "net")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
        ecrire(os.path.join(proj, "methode-chantier.md"), "la copie locale, tolérée\n")
        os.makedirs(os.path.join(proj, "ctx", "artefacts"))
        shutil.copy(GABARIT_FEUILLE, os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"))
        appel(["feuille", proj])

        code, s = appel(["niveau", proj])
        assert code == 0
        assert "ÉCART:" not in s
        assert s.rstrip().endswith("NIVEAU 0 écarts · 0 avertissements — %s" % proj)
        assert ("methode-chantier" not in s), ("NIV2 : une copie locale de methode-chantier.md n'est pas un écart") + "\n" + str(s)

        ecrire(os.path.join(proj, "CLAUDE.md"), "x\n" * (mod.SEUIL_CLAUDE + 1))
        code, s = appel(["niveau", proj])
        assert code == 0
        assert ("AVERTISSEMENT: poids: CLAUDE.md %d lignes > %d\n"
                 % (mod.SEUIL_CLAUDE + 1, mod.SEUIL_CLAUDE) in s)
        assert "NIVEAU 0 écarts · 1 avertissements" in s

        ecrire(os.path.join(proj, "CLAUDE.md"), "x\n" * 93)
        code, s = appel(["niveau", proj])
        assert code == 0
        assert "AVERTISSEMENT:" not in s
        assert "POIDS CLAUDE.md 93/100 ·" in s
        assert "NIVEAU 0 écarts · 0 avertissements" in s

        code, s = appel(["niveau", os.path.join(t, "pas-un-projet")])
        assert code == 1
        assert s.startswith("GARDE: pas de CHANTIER.md dans ")

    # `niveau` lit les chemins du projet par le point unique : il hérite des GARDE.
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "garde")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE.replace("ctx/00-INDEX.md", "ctx/absent.md"))
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
        code, s = appel(["niveau", proj])
        assert code == 1
        assert "GARDE: index introuvable : ctx/absent.md\n" in s


def niveau_courant():
    with tempfile.TemporaryDirectory() as tc:
        pc = os.path.join(tc, "courant")
        ecrire(os.path.join(pc, "CHANTIER.md"), CARTE_NETTE.replace(
            "courant** : aucun", "courant** : ctx/20-z.md"))
        ecrire(os.path.join(pc, "ctx", "00-INDEX.md"), INDEX_NET)
        ecrire(os.path.join(pc, "ctx", "08-etat.md"), ETAT_NIV)
        ecrire(os.path.join(pc, "ctx", "20-z.md"), FICHES)
        try:
            return appel(["niveau", pc])
        except AttributeError as e:
            return None, "traceback : %s" % e


def test_hab_niveau():
    """Contrôler `niveau` avec un chantier courant (chantier HAB)."""
    code, s = niveau_courant()
    assert code is not None
    assert "\nNIVEAU " in s


def feuille_ancienne():
    css = "".join(l for l in pathlib.Path(GABARIT_VLPCSS).read_text(encoding="utf-8").splitlines(True)
                  if not l.lstrip().startswith(("details.clos", ".resume-clos")))
    gabarit = pathlib.Path(GABARIT_FEUILLE).read_text(encoding="utf-8")
    gabarit = gabarit.replace('<link rel="stylesheet" href="vlp.css">', "<style>\n%s</style>" % css)
    lignes = gabarit.splitlines(True)
    return "".join(l for l in lignes
                   if not l.lstrip().startswith(("<details class=\"clos\">",
                                                 "<summary><span class=\"resume-clos\">", "</details>")))


def bac_niv3(t, feuille=True, index=INDEX_NIV3):
    proj = os.path.join(t, "niv3")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NIV3)
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), index)
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
    ecrire(os.path.join(proj, "ctx", "10-a.md"), "# Chantier A\n")
    if feuille:
        ecrire(os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"), feuille_ancienne())
    return proj


def compte(s, prefixe):
    return len([l for l in s.splitlines() if l.startswith(prefixe)])


def test_niv3(tmp_path):
    """Contrôler `niveau --ecrire` : avant, après, et ce qui n'est pas écrit (NIV3)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = bac_niv3(t)
        code, avant = appel(["niveau", proj])
        n = compte(avant, "ÉCART:")
        # VOI1 : la page du disque, un gabarit jamais régénéré, porte un lien cassé — le cinquième
        assert code == 1
        assert n == 5
        assert "ÉCART: renvois: " in avant
        assert "ÉCART: feuille: le bloc repliable" in avant
        assert "ÉCART: clos: " in avant
        assert "ÉCART: feuille: Markdown brut ou lien cassé" in avant

        code, pendant = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        m = compte(pendant, "CORRIGÉ:")
        assert code == 1
        assert m == 3
        assert compte(pendant, "ÉCART:") == 1
        assert "CORRIGÉ: feuille: bloc repliable des chantiers clos posé\n" in pendant
        assert "CORRIGÉ: feuille: régénérée\n" in pendant
        assert "CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:8" in pendant
        assert pendant.rstrip().endswith("NIVEAU 3 corrigés · 1 à la main — %s" % proj)

        code, apres = appel(["niveau", proj])
        # la régénération corrige deux écarts d'un coup : la page, et le lien cassé qu'elle portait
        assert code == 1
        assert compte(apres, "ÉCART:") == n - m - 1
        assert "ÉCART: renvois: " in apres

        carte_niv3 = pathlib.Path(os.path.join(proj, "CHANTIER.md")).read_text(encoding="utf-8")
        assert "| ctx/10-a.md |" not in carte_niv3
        assert "## Chantiers clos — dans l'index, pas ici" in carte_niv3
        assert "Lettres de fiche déjà prises : A." in carte_niv3

        html_niv3 = pathlib.Path(os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")).read_text(encoding="utf-8")
        assert '<details class="clos">' in html_niv3
        assert '<span class="resume-clos">' in html_niv3
        assert html_niv3.count('href="vlp.css"') == 1
        assert "<style>" not in html_niv3
        assert ('\n          <tr>\n' in html_niv3), ("NIV3 : les lignes de ZONE:clos gardent les dix espaces que `clore` repère") + "\n" + "indentation changée"
        assert '<span class="titre">un truc</span>' in html_niv3
        assert "2026-09-18" in html_niv3

        code, encore = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        assert ("NIVEAU 0 corrigés · 1 à la main" in encore), ("NIV3 : rejoué, il ne corrige plus rien — les corrections sont idempotentes") + "\n" + str(encore)


def test_niv3_feuille_absente(tmp_path):
    """NIV3 : la feuille absente — posée depuis le gabarit, puis régénérée."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = bac_niv3(t, feuille=False)
        page = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        _code, s = appel(["niveau", proj])
        assert not os.path.exists(page)
        assert "ÉCART: feuille: feuille de route introuvable :" in s
        _code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        assert os.path.isfile(page)
        assert "CORRIGÉ: feuille: posée depuis le gabarit" in s
        assert '<span class="titre">un truc</span>' in pathlib.Path(page).read_text(encoding="utf-8")


def test_niv3_index_incomplet(tmp_path):
    """NIV3 : l'index ne nomme pas un fichier de la table — la retirer le perdrait."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = bac_niv3(t, index="# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
                               "| `08-etat.md` | on reprend |\n")
        _code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        assert "ÉCART: clos: " in s
        assert "CORRIGÉ: clos: " not in s
        assert "| ctx/10-a.md |" in pathlib.Path(os.path.join(proj, "CHANTIER.md")).read_text(encoding="utf-8")


def test_niv3_sans_carte(tmp_path):
    """NIV3 : rien n'est écrit tant qu'un calcul peut échouer — un projet sans CHANTIER.md."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        code, s = appel(["niveau", os.path.join(t, "rien"), "--ecrire"])
        assert code == 1
        assert s.startswith("GARDE: pas de CHANTIER.md dans ")
        assert not os.listdir(t)


VIEILLE = ('          <tr>\n            <td><a href="&lt;https://v&gt;">Un <span class="mono">**c**</span></a>'
           ' <span class="badge" data-etat="clos">clos</span></td>\n'
           '            <td class="mono">A1–A2</td><td class="mono">2026-01-01</td>\n'
           '            <td class="mono">≈1,5k (1 500)</td>\n'
           '            <td>Livré **x** et [t](https://u)</td>\n          </tr>\n')


def visible(h):
    return re.sub(r"<[^>]+>", "", h)


def rangs_clos(page):
    html = pathlib.Path(page).read_text(encoding="utf-8")
    d, f = mod.zone(html, "clos", "<tbody>\n", "        </tbody>")
    return mod.lignes_clos(html[d:f])


def test_rep3_compteurs(tmp_path):
    """Contrôler les trois compteurs d'une feuille, puis `clore` (REP3)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "rep3")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
        page = mod.page_feuille(proj)  # le chemin tel que `niveau` l'affiche
        os.makedirs(os.path.dirname(page))
        shutil.copy(GABARIT_FEUILLE, page)
        appel(["feuille", proj, "--date", "2026-09-18"])

        code, s = appel(["niveau", proj, "--date", "2026-09-18"])
        assert code == 0
        assert "ÉCART:" not in s
        assert "MARKDOWN 0 ** · 0 liens Markdown · 0 liens cassés — %s\n" % page in s

        html = pathlib.Path(page).read_text(encoding="utf-8")
        d, _f = mod.zone(html, "clos", "<tbody>\n", "        </tbody>")
        ecrire(page, html[:d] + VIEILLE + html[d:])
        code, s = appel(["niveau", proj, "--date", "2026-09-18"])
        # Le second écart (BTN5) : la ligne close a un coût, la feuille n'a pas encore la balise de couts.svg.
        assert code == 1
        assert compte(s, "ÉCART:") == 2
        assert "MARKDOWN 2 ** · 1 liens Markdown · 1 liens cassés — %s\n" % page in s
        assert ("ÉCART: feuille: Markdown brut ou lien cassé — « vlp.py niveau --ecrire »"
                     " convertit les lignes closes\n" in s)

        code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        apres = pathlib.Path(page).read_text(encoding="utf-8")
        assert code == 0
        assert "CORRIGÉ: feuille: 1 lignes closes converties\n" in s
        assert "MARKDOWN 0 ** · 0 liens Markdown · 0 liens cassés — %s\n" % page in s
        assert '<a href="&lt;URL de son artefact&gt;">' in apres

        ligne = rangs_clos(page)[0]
        assert visible(ligne) == visible(VIEILLE).replace("**x**", "x").replace("[t](https://u)", "t")
        assert '<a href="https://v">' in ligne
        assert '<a href="https://u">t</a>' in ligne
        assert "<strong>x</strong>" in ligne
        assert '<span class="mono">**c**</span>' in ligne
        assert ligne.startswith("          <tr>\n")

        code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        assert pathlib.Path(page).read_text(encoding="utf-8") == apres
        assert "CORRIGÉ: feuille:" not in s

        carte = pathlib.Path(os.path.join(proj, "CHANTIER.md")).read_text(encoding="utf-8")
        ecrire(os.path.join(proj, "CHANTIER.md"), carte.replace(
            "- **méthode** :", "- **artefact du chantier** : https://exemple/w\n- **méthode** :")
            + "\nLettres de fiche déjà prises : A. Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "40-w.md"), ouvert("# Chantier W — Un titre\n\n## W1 [x] — a\n"))
        code, s = appel(["clore", proj, "--livre", "y", "--tokens", "950", "--date", "2026-09-19"])
        assert code == 0
        assert "· chantier 950 · cumul 2 450 ·" in s
        rangs = rangs_clos(page)
        assert len(rangs) == 2
        assert "2026-09-19" in rangs[0]
        assert rangs[1] == ligne


def test_voi1_markdown(tmp_path):
    """Contrôler que sans `--ecrire`, MARKDOWN compte la page du disque (VOI1)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tv:
        projv = os.path.join(tv, "voi1")
        ecrire(os.path.join(projv, "CHANTIER.md"), CARTE_NETTE)
        ecrire(os.path.join(projv, "ctx", "00-INDEX.md"), INDEX_NET)
        ecrire(os.path.join(projv, "ctx", "08-etat.md"), ETAT_NIV)
        pagev = mod.page_feuille(projv)
        os.makedirs(os.path.dirname(pagev))
        shutil.copy(GABARIT_FEUILLE, pagev)
        appel(["feuille", projv, "--date", "2026-09-18"])
        htmlv = pathlib.Path(pagev).read_text(encoding="utf-8")
        d, _f, _ = mod.zone_todo(htmlv)
        ecrire(pagev, htmlv[:d] + "          <tr><td>**x**</td></tr>\n" + htmlv[d:])
        _code, s = appel(["niveau", projv, "--date", "2026-09-18"])
        assert ("MARKDOWN 2 ** · 0 liens Markdown · 0 liens cassés — %s\n" % pagev in s), ("VOI1 : sans --ecrire, le ** brut de la page du disque se compte, même si la régénération le fait tomber") + "\n" + str(s)  # un **x** = deux **


def test_rep3_sans_etat(tmp_path):
    """Contrôler une feuille qui ne se régénère pas, sans fichier d'état (REP3)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "rep3b")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE.replace("- **fichier d'état** : ctx/08-etat.md\n", ""))
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
        code, s = appel(["niveau", proj])
        assert code == 1
        assert "MARKDOWN non mesuré, la feuille ne se régénère pas — " in s
        assert "ÉCART: feuille: fichier d'état introuvable : aucun\n" in s


ANCIENNE_CMP = ("<html><body><table><tbody>\n"
                "<tr><td>ligne A</td></tr>\n"
                "<tr><td>TODO : un truc</td></tr>\n"
                "</tbody></table></body></html>\n")


NEUVE_CMP = ("<html><body><table><tbody>\n"
             "<tr><td>ligne A</td></tr>\n"
             "<tr><td>2026-09-26</td></tr>\n"
             "</tbody></table></body></html>\n")


def test_voi2_comparer(tmp_path):
    """Contrôler `comparer` : une ligne perdue, une ajoutée (VOI2)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tc:
        anc = os.path.join(tc, "ancienne.html")
        neu = os.path.join(tc, "neuve.html")
        ecrire(anc, ANCIENNE_CMP)
        ecrire(neu, NEUVE_CMP)
        code, s = appel(["comparer", anc, neu])
        assert code == 0
        assert "PERDU: TODO : un truc\n" in s
        assert "AJOUTÉ: 2026-09-26\n" in s
        assert s.rstrip().endswith("COMPARER 1 perdus · 1 ajoutés")
        code, s = appel(["comparer", anc, os.path.join(tc, "absente.html")])
        assert code == 1
        assert s.startswith("GARDE:")


def test_page_enveloppee(tmp_path):
    """Dans une fonction : au niveau du module, pyright jugeait le fichier trop complexe."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tenv:
        a = os.path.join(tenv, "ancienne.html")
        n = os.path.join(tenv, "neuve.html")
        for chemin, page in ((a, ANCIENNE_CMP), (n, NEUVE_CMP)):
            ecrire(chemin, page.replace("<body>", "<body><div class=\"page\"><h2>Titre</h2>")
                   .replace("</body>", "</div></body>"))
        c, sortie = appel(["comparer", a, n])
        assert c == 0
        assert "PERDU: TODO : un truc\n" in sortie
        assert "AJOUTÉ: 2026-09-26\n" in sortie
        assert sortie.rstrip().endswith("COMPARER 1 perdus · 1 ajoutés")


def test_plage_refaite(tmp_path):
    """Dette HAB : une plage d'en-tête refaite n'est ni perdue ni ajoutée."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tpl:
        a = os.path.join(tpl, "ancienne.html")
        n = os.path.join(tpl, "neuve.html")
        for chemin, fin in ((a, "P7"), (n, "P8")):
            ecrire(chemin, ANCIENNE_CMP.replace("<body>", "<body><div>kit · fiches P1–%s</div>" % fin))
        c, sortie = appel(["comparer", a, n])
        assert c == 0
        assert "PERDU:" not in sortie
        assert "AJOUTÉ:" not in sortie
        assert "PLAGE: kit · fiches P1–P7 → kit · fiches P1–P8\n" in sortie
        assert sortie.rstrip().endswith("COMPARER 0 perdus · 0 ajoutés · 1 plages refaites")
        ecrire(n, ANCIENNE_CMP.replace("<body>", "<body><div>autre · fiches P1–P8</div>"))
        c, sortie = appel(["comparer", a, n])
        assert "PERDU: kit · fiches P1–P7\n" in sortie
        assert "PLAGE:" not in sortie
        assert sortie.rstrip().endswith("COMPARER 1 perdus · 1 ajoutés")
        for chemin, fin in ((a, "P7"), (n, "P8")):
            ecrire(chemin, ANCIENNE_CMP.replace("<body>", "<body><div>Fiches P1–%s — la page</div>" % fin))
        c, sortie = appel(["comparer", a, n])
        assert "PLAGE: Fiches P1–P7 — la page → Fiches P1–P8 — la page\n" in sortie
        assert "PERDU:" not in sortie


SOIR_ATTENTE = datetime.datetime(2026, 9, 28, 20, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
URL_ATTENTE = "https://claude.ai/artifact/AAA"
REFUS_ATTENTE = "publish 429: daily publish limit for your plan reached (200) — resets at UTC midnight"


def hook_attente(d, maintenant=SOIR_ATTENTE):
    """`(code, sortie)` de `cmd_attente_hook` sur l'entrée JSON `d`, à l'heure `maintenant`."""
    o = io.StringIO()
    code = mod.cmd_attente_hook(io.StringIO(json.dumps(d)), o, maintenant)
    return code, o.getvalue()


def projet_attente(t, nom):
    """Un projet équipé `<t>/<nom>` ; rend `(projet, son dossier artefacts)`."""
    p = os.path.join(t, nom)
    ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
    ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
    return p, os.path.join(p, "context AI", "artefacts")


def test_attente(tmp_path):
    """attente (chantier LOC2) : la liste des pages refusées par la limite du jour — ajouter, lister, retirer."""
    url = URL_ATTENTE
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p, art = projet_attente(t, "proj")
        liste, page = os.path.join(art, "en-attente"), os.path.join(art, "88-boutons.html")
        assert ("ATTENTE=" not in rendu(p)), ("attente : carte sans liste, pas de ligne ATTENTE=") + "\n" + str(rendu(p))
        code, s = appel(["attente", "ajouter", "88-boutons.html", "--projet", p])
        assert ((code, s) == (0, "ATTENTE 1\n")), ("attente ajouter : ATTENTE 1") + "\n" + str(s)
        code, s = appel(["attente", "ajouter", "88-boutons.html", "--url", url, "--projet", p])
        lignes = mod.lignes_de(liste)
        assert (code, s) == (0, "ATTENTE 1\n")
        assert len(lignes) == 1
        assert lignes[0].split("\t")[:2] == ["88-boutons.html", url]
        assert len(lignes[0].split("\t")) == 3
        assert (not os.path.exists(liste + ".tmp")), ("attente : aucun .tmp laissé") + "\n" + str(str(os.listdir(art)))
        code, s = appel(["attente", "lister", art])
        assert ((code, s) == (0, "ATTENTE=88-boutons.html %s\nATTENTE 1\n" % url)), ("attente lister") + "\n" + str(s)
        code, s2 = appel(["attente", "lister", p])
        assert ((code, s2) == (0, s)), ("attente lister la racine du projet : la même liste, pas un ATTENTE 0 muet — mutant : la racine lue comme un dossier artefacts") + "\n" + str(s2)
        c = rendu(p)
        assert (0 <= c.find("ATTENTE=88-boutons.html %s\n" % url) < c.find("--- fiches :")), ("attente : la carte montre ATTENTE= avant le fichier de fiches courant") + "\n" + str(c)
        s = io.StringIO()
        mod.carte(p, s, True)
        assert ("ATTENTE=" not in s.getvalue()), ("attente : la carte du relecteur n'a pas de ligne ATTENTE=") + "\n" + str(s.getvalue())
        code, s = appel(["attente", "ajouter", "../hors.html", "--projet", p])
        assert code == 1
        assert s.startswith("GARDE:")
        code, s = appel(["attente", "retirer", page, "--projet", p])
        assert (code, s) == (0, "ATTENTE 0\n")
        assert not os.path.exists(liste)


@pytest.fixture
def tampon_hooks():
    """Un vrai dossier de tampons, comme TOU2 — le tampon du jour fait la différence ; l'ancien remis après."""
    ancien_tampon = mod.etat.TAMPON_HOOKS
    mod.etat.TAMPON_HOOKS = tempfile.mkdtemp()
    try:
        yield
    finally:
        shutil.rmtree(mod.etat.TAMPON_HOOKS, ignore_errors=True)
        mod.etat.TAMPON_HOOKS = ancien_tampon


def test_attente_hook(tmp_path, tampon_hooks):
    """attente hook : un refus de la limite du jour s'ajoute à la liste et se propose une fois par jour et par
    projet ; les autres échecs ne font rien ; une publication réussie retire la page."""
    soir, url = SOIR_ATTENTE, URL_ATTENTE
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p, art = projet_attente(t, "proj")
        page, autre = os.path.join(art, "88-boutons.html"), os.path.join(art, "91-x.html")
        echec = {"hook_event_name": "PostToolUseFailure", "tool_name": "Artifact", "cwd": p,
                 "tool_input": {"file_path": page, "url": url}, "error": REFUS_ATTENTE}
        code, s = hook_attente(echec)
        assert code == 0
        assert mod.lire_attente(art)[0][:2] == ("88-boutons.html", url)
        sortie = json.loads(s)["hookSpecificOutput"] if s else {}
        assert sortie.get("hookEventName") == "PostToolUseFailure"
        assert "88-boutons.html" in sortie.get("additionalContext", "")
        assert "à 02:00 locale" in sortie["additionalContext"]
        assert "à 02:10 qui" in sortie["additionalContext"]
        code, s = hook_attente(dict(echec, tool_input={"file_path": autre}))
        assert s == ""
        assert [e[0] for e in mod.lire_attente(art)] == ["88-boutons.html", "91-x.html"]
        assert mod.lire_attente(art)[1][1] == "aucune"
        code, s = hook_attente(echec, soir + datetime.timedelta(days=1))
        assert ('"additionalContext"' in s), ("attente hook : le lendemain (jour UTC), la proposition revient") + "\n" + str(s)
        p2, art2 = projet_attente(t, "proj2")
        code, s = hook_attente(dict(echec, cwd=p2, tool_input={"file_path": os.path.join(art2, "88-boutons.html")}))
        assert ('"additionalContext"' in s), ("attente hook : un autre projet, sa propre proposition") + "\n" + str(s)
        avant = mod.lire_attente(art)
        for nom, d in (
                ("page non lue", dict(echec, error="Nothing was published or removed: this publish touches files"
                                                   " whose published content is not what you last saw")),
                ("refus du vigile", dict(echec, error="PreToolUse:Artifact hook error: Page cassée, publication"
                                                      " refusée (vlp.py vigile) — x.html : aucun style")),
                ("vigile avant l'appel", dict(echec, hook_event_name="PreToolUse")),
                ("autre outil", dict(echec, tool_name="Write")),
                ("asset", dict(echec, tool_input={"file_path": page, "asset": True})),
                ("page hors projet", dict(echec, tool_input={"file_path": os.path.join(t, "ailleurs", "x.html")}))):
            code, s = hook_attente(d, soir + datetime.timedelta(days=2))
            assert code == 0
            assert s == ""
            assert mod.lire_attente(art) == avant
        code, s = hook_attente(dict(echec, hook_event_name="PostToolUse", tool_input={"file_path": page}))
        assert code == 0
        assert s == ""
        assert [e[0] for e in mod.lire_attente(art)] == ["91-x.html"]
        code, s = hook_attente(dict(echec, hook_event_name="PostToolUse", tool_input={"file_path": page}))
        assert code == 0
        assert s == ""
        assert [e[0] for e in mod.lire_attente(art)] == ["91-x.html"]
        o = io.StringIO()
        code = mod.main(["attente", "hook"], o, io.StringIO("pas du json"))
        assert ((code, o.getvalue()) == (0, "")), ("attente hook : entrée illisible, muet, code 0") + "\n" + str(o.getvalue())


def test_attente_remise_a_zero():
    """attente : remise à zéro 02:00 et tâche 02:10 pour 2026-09-28 20:00 UTC+2."""
    zero, tache = mod.remise_a_zero(SOIR_ATTENTE)
    assert ((zero.strftime("%Y-%m-%d %H:%M"), tache.strftime("%H:%M")) == ("2026-09-29 02:00", "02:10")), ("attente : remise à zéro 02:00 et tâche 02:10 pour 2026-09-28 20:00 UTC+2") + "\n" + str(str(zero))


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
    ecrire(os.path.join(d, "ctx", "40-loc.md"), ouvert("# Chantier LOC — Publier\n\n## LOC1 [ ] — a\n"))
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


def test_attentes_de_nuit(tmp_path):
    """NPB1 (a) : `clore` sous `VLP_NUIT=1` met en attente la page du chantier et la feuille ; sans, ni l'une ni l'autre."""
    vus = {}
    garde = os.environ.pop("VLP_NUIT", None)
    try:
        for nuit in (True, False):
            with tempfile.TemporaryDirectory(dir=tmp_path) as te:
                ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                       "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : https://claude.ai/artifact/c\n"
                       "- **artefact feuille de route** : https://claude.ai/artifact/f\n\n"
                       "Lettres de fiche déjà prises : U (test).\n")
                ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé "
                       "| Dépend de |\n|---|---|---|---|---|\n| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
                ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
                for page, gabarit in (("50-u.html", "artefact-chantier.html"),
                                      ("feuille-de-route.html", "artefact-feuille-de-route.html")):
                    ecrire(os.path.join(te, "ctx", "artefacts", page),
                           pathlib.Path(os.path.join(ICI, "..", "templates", gabarit)).read_text(encoding="utf-8"))
                if nuit:
                    os.environ["VLP_NUIT"] = "1"
                try:
                    code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
                finally:
                    os.environ.pop("VLP_NUIT", None)
                vus[nuit] = (code, s, [[p, u] for p, u, _ in mod.lire_attente(os.path.join(te, "ctx", "artefacts"))])
    finally:
        if garde is not None:
            os.environ["VLP_NUIT"] = garde
    assert vus[True][0] == 0
    assert (vus[True][2] == [["50-u.html", "https://claude.ai/artifact/c"],
                                                     ["feuille-de-route.html", "https://claude.ai/artifact/f"]])
    assert "ATTENTE 50-u.html — https://claude.ai/artifact/c\n" in vus[True][1]
    assert vus[False][0] == 0
    assert vus[False][2] == []


def noms_ailleurs(dossier):
    """Les `(code, nom du dossier)`, triés, des lignes `AILLEURS=` de la carte de `dossier` (NUI28)."""
    s = appel(["carte", dossier])[1]
    return sorted((l.split()[0][len("AILLEURS="):], os.path.basename(l.split(None, 1)[1].rstrip("/")))
                  for l in s.splitlines() if l.startswith("AILLEURS="))


def test_ailleurs_meme_chantier(tmp_path, init_git):
    """NUI28 (b) à (d) : au même chantier qu'ici, un autre worktree n'est nommé (`AILLEURS=`, `niveau`) que s'il a
    joué une fiche de ce code qu'ici n'a pas — un hérité se tait des deux côtés (ISO2, TODO 140)."""
    if not shutil.which("git"):
        pytest.skip("git absent — AILLEURS= au même chantier n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wl = os.path.join(tr, "n"), os.path.join(tr, "wt-l")
        depot_matin(init_git, d)
        _, seul = appel(["niveau", d])
        git_matin(d, "worktree", "add", "-q", "-b", "l", wl, "main")
        ecrire(mod.postit(wl), "ctx/40-loc.md\n")      # le worktree joue LOC : son post-it le nomme (NUI31)
        ecrire(os.path.join(wl, "b.txt"), "b\n")
        commit_matin(wl, "LOC1 : a", 2)                 # et une fiche de LOC que main n'a pas (ISO2)
        _, avec = appel(["niveau", d])
        _, dans = appel(["niveau", wl])
    assert "ÉCART: page:" in seul
    assert "AILLEURS:" not in seul
    assert "AILLEURS: page: LOC joue dans " in avec
    assert "wt-l" in avec
    assert "ÉCART: page:" not in avec
    assert "AILLEURS:" not in dans

    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wh = os.path.join(tr, "h"), os.path.join(tr, "wt-h")
        depot_matin(init_git, d)
        git_matin(d, "worktree", "add", "-q", "-b", "h", wh, "main")
        ecrire(mod.postit(wh), "ctx/40-loc.md\n")      # LOC hérité de main, nommé par le post-it : le même des deux côtés
        herite = [noms_ailleurs(w) for w in (d, wh)]
        ecrire(os.path.join(wh, "b.txt"), "b\n")
        commit_matin(wh, "LOC1 : a", 2)                 # une fiche de LOC jouée dans le worktree, pas dans main
        joue = [noms_ailleurs(w) for w in (d, wh)]
    assert (herite == [[], []]), ("NUI28 (c) ISO2 : même chantier hérité, aucun commit de fiche d'un côté ni de l'autre → ni main ni le "
             "worktree ne nomment l'autre (TODO 140) — mutant : toujours nommer") + "\n" + str(herite)
    assert (joue == [[("LOC", "wt-h")], []]), ("NUI28 (d) ISO2 : même code, une fiche LOC jouée dans le worktree → main le nomme, le worktree ne nomme "
             "pas main — mutant : toujours nommer") + "\n" + str(joue)
