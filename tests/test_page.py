"""`noyau/page.py` : la page d'un chantier, ses plages, ses arrondis, les fiches lançables. Deux étages : la décision de
`heures_commits` sans Git (REF46), sur le texte de `git log` ; puis les commandes, migrées de l'ancienne suite maison
(REF58), chaque `assert` migré au libellé d'origine de son `verifier` (REF5).
"""
import io
import os
import re
import tempfile
from decimal import Decimal

from aides import RACINE, appel, ecrire, lire, mod, transcript
from noyau import page

LOG = "\n".join([   # le plus récent d'abord, comme `git log`
    "500 Fusion : W2",
    "400 W2 : La suivante",
    "300 W1 : Une fiche",
    "250 W1 : case cochée",
    "200 Chantier W ouvert",
    "100 Autre chose",
])


def test_le_commit_au_titre_et_l_etape_d_avant():
    pourquoi = []
    r = page.heures_du_log(LOG, ["W1", "W2"], pourquoi, titres={"W1": "Une fiche", "W2": "La suivante"})
    # 250 (`W1 : case cochée`) est une étape d'avant le commit au titre : hors des bornes ; `Fusion : W2` va aux autres.
    assert r == ({"W1": 300, "W2": 400}, [200, 300, 400], [100, 500], [])
    assert pourquoi == []


def test_sans_commit_de_fiche_un_chantier_en_cours():
    assert page.heures_du_log("200 Chantier W ouvert\n100 Autre", ["W1"], []) == ({}, [200], [100], [])


def test_sans_commit_qui_nomme_le_prefixe():
    pourquoi = []
    assert page.heures_du_log("100 Autre chose", ["W1"], pourquoi) is None
    assert pourquoi == ["aucun commit qui nomme W"]


def test_un_chantier_clos_sans_commit_de_fiche():
    pourquoi = []
    assert page.heures_du_log("200 Chantier W ouvert", ["W1"], pourquoi, clos=True) is None
    assert pourquoi == ["chantier clos sans commit « W1 : » ni d'une autre fiche"]


def test_arrondi():
    """Contrôler l'arrondi d'un compte de tokens."""
    assert ([mod.arrondi(n) for n in (999, 1000, 999949, 999950, 1505630)] == ["999", "≈1,0k (1 000)", "≈999,9k (999 949)", "≈1,0M (999 950)", "≈1,5M (1 505 630)"]), ("arrondi") + "\n" + str([mod.arrondi(n) for n in (999, 1000, 999949, 999950, 1505630)])


def test_triplet():
    """Contrôler que `triplet` relit ce que `ligne_cout` écrit, et le brut seul."""
    allers = [(t, tours, u) for t in (0, 7, 999, 1000, 999999, 1000000, 123456789, -5, -1500) for tours in (0, 1, 42) for u in (None, Decimal("0"), Decimal("1.83"), Decimal("-0.05"))]
    assert (all(mod.triplet(mod.ligne_cout(*a)) == a for a in allers)), ("triplet relit ligne_cout") + "\n" + str([(a, mod.ligne_cout(*a), mod.triplet(mod.ligne_cout(*a)) == a) for a in allers if mod.triplet(mod.ligne_cout(*a)) != a])
    # Le brut entre parenthèses suffit, sans l'arrondi devant : une page d'un autre format se relit.
    assert (mod.triplet("(5 284 442) · 42 tours · 1,83 $") == (5284442, 42, Decimal("1.83"))), ("triplet : le brut entre parenthèses suffit") + "\n" + str(mod.triplet("(5 284 442) · 42 tours · 1,83 $"))


PAGE = """# Chantier P

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [%s] — Créer `a.py`
%s**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P2 -->
## P2 [%s] — Brancher
%s**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P3 -->
## P3 [ ] — Finir
**Critère de fin**
<!-- /FICHE -->
"""


def test_page_creer(tmp_path):
    """Contrôler `page --creer`, `page --verifier` et une page absente."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        fiches = os.path.join(t, "p.md")
        page = os.path.join(t, "artefacts", "p.html")  # comme en vrai : le .md de l'abri (même dossier que la
        # page) ne collisionne pas avec le fichier de fiches, dans le dossier parent (chantier ABR)
        sa, sb = os.path.join(t, "a.jsonl"), os.path.join(t, "b.jsonl")
        transcript(sa, 2)
        transcript(sb, 1)

        ecrire(fiches, PAGE % (" ", "", " ", ""))
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "Le <titre>",
                         "--resultat", "Fini quand.", "--note", "P1", "Produit a.py", "--date", "2026-01-02"])
        html = lire(page) if os.path.exists(page) else ""
        assert (code == 0 and "<title>Proj — Le &lt;titre&gt;</title>" in html
                 and "Proj · fiches P1–P3" in html and "<p>Fini quand.</p>" in html
                 and '<span data-etat="encours"></span><span></span><span></span>' in html
                 and "3 fiches · 0 faite · en cours : P1" in html and '<span class="note">Produit a.py</span>' in html
                 and "&lt;" not in html.split("<ul class=\"journal\">")[1].split("</ul>")[0]
                 and '<p class="mono cout-total">' not in html and '<p class="mono cout-hors">' not in html
                 and "Mis à jour le <span class=\"mono\">2026-01-02</span>" in html
                 and "lignes · total non mesuré" in s), ("page --creer") + "\n" + str(s + html)
        # Dette CLI : `--projet .` écrivait « . » en tête de page ; un dossier donne son alias, sinon son nom
        with tempfile.TemporaryDirectory(dir=tmp_path) as tnom:
            dnom = os.path.join(tnom, "mon-projet")
            os.makedirs(dnom)
            assert (mod.nom_du_projet(dnom) == "mon-projet"), ("page --creer : un dossier sans CHANTIER.md donne son nom") + "\n" + str(mod.nom_du_projet(dnom))
            ecrire(os.path.join(dnom, "CHANTIER.md"), "# C\n\n- **alias** : mp\n")
            assert (mod.nom_du_projet(dnom) == "mp"), ("page --creer : un dossier équipé donne son alias") + "\n" + str(mod.nom_du_projet(dnom))
            assert (mod.nom_du_projet("Proj " + tnom) == "Proj " + tnom), ("page --creer : un nom reste un nom") + "\n" + ""
            pnom = os.path.join(tnom, "p.html")
            appel(["page", fiches, pnom, "--creer", "--projet", dnom, "--titre", "T", "--resultat", "R"])
            assert ('<div class="eyebrow">mp · fiches'
                     in lire(pnom) and "<title>mp — T</title>" in lire(pnom)), ("page --creer : --projet <dossier> écrit l'alias en tête") + "\n" + str(lire(pnom)[:400])
        code, s = appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R"])
        assert (code == 1 and "existe déjà" in s), ("page --creer n'écrase pas") + "\n" + str(s)

        ecrire(fiches, PAGE % ("x", "**Session** : %s\n" % sa, " ", ""))
        code, s = appel(["page", fiches, page, "--verifier"])
        assert (code == 1 and "ÉCART: P1 : page encours, fichier faite" in s
                 and "EN RETARD 3 fiches · 3 écarts" in s), ("page --verifier : en retard") + "\n" + str(s)
        code, s = appel(["page", fiches, page, "--note", "P1", "a.py : <3 tests>", "--journal", "P1 : tranché.", "--date", "2026-01-03"])
        html = lire(page)
        assert (code == 0
                 and '<li class="fiche" data-etat="faite">' in html and "a.py : &lt;3 tests&gt;" in html
                 and '<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>' in html
                 and '<p class="mono cout-total">Coût du chantier : ≈200,0k (200 000) · 2 tours · 1,00 $</p>' in html
                 and '<time datetime="2026-01-03">2026-01-03</time><span>P1 : tranché.</span>' in html
                 and "3 fiches · 1 faite · en cours : P2" in html), ("page : fiche faite, coût, note échappée, journal") + "\n" + str(s + html)
        code, s = appel(["page", fiches, page, "--verifier"])
        assert (code == 0 and s == "À JOUR 3 fiches · 0 écarts (états et avancement seulement)\n"), ("page --verifier : à jour") + "\n" + str(s)
        avant = lire(page)
        appel(["page", fiches, page, "--date", "2026-01-03"])
        assert (lire(page) == avant), ("page : régénérer deux fois ne change rien") + "\n" + str(lire(page))

        # P2 partage la session de P1 : P1 garde son coût affiché, P2 prend le reste ; b s'ajoute au total.
        # L'ancien total compte 1 tour de cadrage (100 000) qu'aucune fiche ne porte : il reste hors de P2.
        ecrire(page, lire(page).replace("Coût du chantier : ≈200,0k (200 000) · 2 tours · 1,00 $",
                                        "Coût du chantier : ≈300,0k (300 000) · 3 tours · 1,50 $"))
        transcript(sa, 4)
        ecrire(fiches, PAGE % ("x", "**Session** : %s\n" % sa, "x", "**Session** : %s\n**Session** : %s\n" % (sa, sb)))
        code, s = appel(["page", fiches, page, "--date", "2026-01-04"])
        html = lire(page)
        assert (code == 0
                 and '<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>' in html
                 and '<span class="cout mono">≈100,0k (100 000) · 1 tours · 0,50 $</span>' in html
                 and "Coût du chantier : ≈500,0k (500 000) · 5 tours · 2,50 $" in html
                 and "3 fiches · 2 faites · en cours : P3" in html), ("page : session partagée, le reste à la dernière") + "\n" + str(s + html)
        avant = lire(page)
        appel(["page", fiches, page, "--date", "2026-01-04"])
        assert (lire(page) == avant), ("page : session partagée, régénérer deux fois ne change rien") + "\n" + str(lire(page))

        # Blocage : bloquée reste bloquée tant que non cochée ; le bloc se masque quand elle l'est.
        html = lire(page).replace('<li class="fiche" data-etat="encours">', '<li class="fiche" data-etat="bloquee">')
        html = html.replace("<section hidden>\n    <h2>Arrêt sur blocage</h2>", "<section>\n    <h2>Arrêt sur blocage</h2>")
        html = html.replace('<div class="blocage">\n      <p></p>', '<div class="blocage">\n      <p>P3 — deux essais.</p>')
        ecrire(page, html)
        appel(["page", fiches, page])
        html = lire(page)
        assert ('<li class="fiche" data-etat="bloquee">' in html and "bloquée : P3" in html
                 and "<section>\n    <h2>Arrêt sur blocage</h2>" in html), ("page : bloquée gardée") + "\n" + str(html)
        ecrire(fiches, lire(fiches).replace("## P3 [ ]", "## P3 [x]"))
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0 and "<section hidden>\n    <h2>Arrêt sur blocage</h2>" in html
                 and "3 fiches · 3 faites</p>" in html and 'data-etat="bloquee"' not in html.split('<div class="page">')[1]), ("page : blocage masqué une fois cochée") + "\n" + str(s + html.split("<div class=\"page\">")[1])

        # L'en-tête suit la plage du fichier : quand on ajoute P4, la plage devient P1–P4, mais ce qui suit reste.
        ecrire(page, lire(page).replace('Proj · fiches P1–P3</div>', 'Proj · fiches P1–P3 · clos</div>'))
        ecrire(fiches, lire(fiches) + '\n<!-- FICHE:P4 -->\n## P4 [ ] — Ajoutée\n**Critère de fin**\n<!-- /FICHE -->\n')
        code, s = appel(["page", fiches, page])
        html = lire(page)
        assert (code == 0 and 'Proj · fiches P1–P4 · clos</div>' in html), ("page : l'en-tête suit la plage du fichier") + "\n" + str(s + html)

        u_fiches = os.path.join(t, "u.md")
        u_page = os.path.join(t, "artefacts", "u.html")
        ecrire(u_fiches, "# Chantier U\n\n## Le socle commun\n\n## L'ordre des fiches\n\n<!-- FICHE:U1 -->\n## U1 [ ] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        code, s = appel(["page", u_fiches, u_page, "--creer", "--projet", "Proj", "--titre", "U", "--resultat", "R."])
        u_html = lire(u_page) if os.path.exists(u_page) else ""
        assert (code == 0 and "Proj · fiches U1</div>" in u_html), ("page : l'en-tête d'une fiche seule") + "\n" + str(s + u_html)

        # Un en-tête sans plage reconnue reste tel quel : ni texte libre, ni parenthèses, ni trait d'union (REV6).
        for entete in ("fiches à venir", "fiches (X1–X2)", "fiches X1-X2"):
            ecrire(u_page, u_html.replace("Proj · fiches U1</div>", "Proj · %s</div>" % entete))
            code, s = appel(["page", u_fiches, u_page])
            html = lire(u_page)
            assert (code == 0 and "Proj · %s</div>" % entete in html), ("page : un en-tête sans plage reste tel quel (%s)" % entete) + "\n" + str(s + html)
        ecrire(u_page, u_html)

        code, s = appel(["page", fiches, os.path.join(t, "absente.html")])
        assert (code == 1 and "--creer" in s), ("page absente sans --creer") + "\n" + str(s)


def test_plages():
    """Contrôler les bornes de `plages`, en fonction pure (chantier FIN)."""
    P2, G = [("Q1", "a", True, ["s"]), ("Q2", "b", True, ["s"])], []
    bornes = lambda h, f=P2: mod.plages(f, h, G)
    assert (bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800], [30, 900]))
             == ([("Q1", (100, 300)), ("Q2", (300, 600))], [(30, 100), (600, 800)])), ("plages : l'origine, le chantier d'avant, borne hors fiches") + "\n" + str(bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800], [30, 900])))
    assert (bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600], [30]))[1] == [(30, 100), (600, mod.INFINI)]), ("plages : sans clôture, hors fiches va au bout") + "\n" + str(bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600], [30])))
    assert (bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800, 950], [30, 900]))[1] == [(30, 100), (600, 800)]), ("plages : une mention après la clôture n'étire rien") + "\n" + str(bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800, 950], [30, 900])))
    assert (bornes(({"Q1": 300, "Q2": 600}, [300, 600, 800], [30, 200]))
             == ([("Q1", (200, 300)), ("Q2", (300, 600))], [(600, 800)])), ("plages : sans commit qui nomme avant, la première fiche part de l'origine") + "\n" + str(bornes(({"Q1": 300, "Q2": 600}, [300, 600, 800], [30, 200])))
    assert (bornes(({"Q1": 300}, [20, 100, 300, 800], [10]), P2[:1])[1] == [(10, 100), (300, 800)]), ("plages : une mention juste avant l'ouverture y fait entrer son travail") + "\n" + str(bornes(({"Q1": 300}, [20, 100, 300, 800], [10]), P2[:1]))
    assert (bornes(({"Q1": 300}, [100, 300], [30])) == ([("Q1", (100, 300)), ("Q2", (300, mod.INFINI))], [(30, 100)])
             and not G), ("plages : fiche à session sans commit, au bout, rien après") + "\n" + str((bornes(({"Q1": 300}, [100, 300], [30])), G))

    # FIN2 : sans commit de fiche, la première fiche part du dernier commit qui nomme le préfixe
    COCHEE, VIDE = [("Q1", "a", True, ["s"]), ("Q2", "b", False, [])], [("Q1", "a", False, [])]
    assert (bornes(({}, [100], [30, 900]), COCHEE) == ([("Q1", (100, mod.INFINI))], [(30, 100)]) and not G), ("plages : sans commit de fiche, la fiche cochée part de l'ouverture") + "\n" + str((bornes(({}, [100], [30, 900]), COCHEE), G))
    assert (bornes(({}, [100], [30]), VIDE) == ([], []) and not G), ("plages : sans commit de fiche ni session, rien") + "\n" + str((bornes(({}, [100], [30]), VIDE), G))


def test_plages_preparation():
    """Contrôler qu'un commit `<PRÉFIXE> :` entre deux fiches coupe la suivante (chantier PRP)."""
    P2, G = [("Q1", "a", True, ["s"]), ("Q2", "b", True, ["s"])], []
    h = ({"Q1": 300, "Q2": 600}, [100, 300, 450, 600, 800], [30, 900], [450])
    r = mod.plages(P2, h, G)
    assert (r == ([("Q1", (100, 300)), ("Q2", (450, 600))], [(30, 100), (300, 450), (600, 800)]) and not G), ("plages_preparation : la fiche 2 part du commit `<PRÉFIXE> :`, le morceau d'avant hors fiches") + "\n" + str((r, G))
    longueur = lambda p: sum(b - a for _, (a, b) in p[0]) + sum(b - a for a, b in p[1])
    assert (longueur(r) == longueur(mod.plages(P2, h[:3], G))), ("plages_preparation : le total ne bouge pas") + "\n" + str((r, mod.plages(P2, h[:3], G)))


def test_ena3_lancables(tmp_path):
    """ENA3 : `lancables` — les fiches prêtes, `--max` au plus, coupées avant la première `(visuel)`, qui ne part que
    seule ; deux qui se croisent partent, en `INDICE:` (ISO3), le fichier de fiches ôté (toutes le cochent)."""
    def fiche(ident, fichiers, visuel=False):
        """Une fiche minimale : ses `fichiers` sur la ligne **Fichiers**, son critère `(visuel)` ou non."""
        return ("<!-- FICHE:%s -->\n## %s [ ] — %s\n\n**Dépend de** : rien.\n**Fichiers** : %s.\n\n**Critère de fin**%s\n"
                "Rien.\n<!-- /FICHE -->\n" % (ident, ident, ident, fichiers, " (visuel)" if visuel else ""))
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        chemin = os.path.join(t, "fiches.md")
        corps = ("# Essai\n\n## Le socle commun\n\nRien.\n\n## L'ordre des fiches\n\nT1 à T4.\n\n---\n"
                 + fiche("T1", "`a.py`, `ctx/fiches.md`") + fiche("T2", "`a.py`, `b.py`")
                 + fiche("T3", "`c.py`, `ctx/fiches.md`") + fiche("T4", "`d.py`", visuel=True))
        ecrire(chemin, corps)
        vus = [appel(["lancables", chemin] + o)[1].splitlines() for o in ([], ["--max", "3"], ["--max", "1"])]
        assert (vus == [["LANCABLES T1 T2", "INDICE: T1 T2 a.py"], ["LANCABLES T1 T2 T3", "INDICE: T1 T2 a.py"],
                         ["LANCABLES T1"]]), ("ENA3 : T2 croise T1 et part quand même, en INDICE: (ISO3) ; fiches.md n'est pas commun ; coupé à 2, 3 "
                 "ou 1 avant T4 (visuel)") + "\n" + str(repr(vus))
        suite = []
        for cochees in (("T1", "T3"), ("T1", "T2", "T3"), ("T1", "T2", "T3", "T4")):
            texte = corps
            for c in cochees:
                texte = texte.replace("## %s [ ]" % c, "## %s [x]" % c)
            ecrire(chemin, texte)
            suite.append(appel(["lancables", chemin, "--max", "3"])[1].strip())
        assert (suite == ["LANCABLES T2", "LANCABLES T4", "LANCABLES aucune"]), ("ENA3 : T2 seule avant la (visuel), puis T4 seule, puis aucune") + "\n" + str(repr(suite))
        code, sortie = appel(["lancables", os.path.join(t, "absent.md")])
        assert (code == 1 and sortie.startswith("GARDE:")), ("ENA3 : fichier absent → GARDE:, sort 1") + "\n" + str(sortie)


def test_ena5_ensemble(tmp_path):
    """ENA5 : `lancables --tourne` réserve les fichiers des lancées et retient ce qui dépend d'une cochée encore en
    relecture ; `releve` lit les motifs d'une ligne **Fichiers** ; le chef commite par `commiter`, jamais
    `git add -A`, et ne propose plus `agents ensemble [N]` (ENA8 : le code reste, pour le chantier `ISO`)."""
    vus = [mod.releve(c, n) for c, n in (
        ("skills/a/SKILL.md", "skills/*/SKILL.md"), ("skills/b/SKILL.md", "skills/{a,b}/SKILL.md"),
        ("skills/c/SKILL.md", "skills/{a,b}/SKILL.md"), ("src/y/z.py", "src/"), ("srcx/w.py", "src"),
        ("a.py", "*"), ("a.py", "a.py"))]
    assert (vus == [True, True, False, True, False, False, True]), ("ENA5 : releve — *, {a,b}, dossier, un * d'italique ne prend rien") + "\n" + str(repr(vus))
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        chemin = os.path.join(t, "fiches.md")
        ecrire(os.path.join(t, "CHANTIER.md"), "x\n")
        for dossier in ("scripts", "doc", "src"):
            os.mkdir(os.path.join(t, dossier))
        ecrire(chemin, "# Essai\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [%s] — %s\n\n**Dépend de** : %s.\n**Fichiers** : %s.\n\n**Critère de fin**\n"
            "Rien.\n<!-- /FICHE -->\n" % (i, i, c, i, d, f) for i, c, d, f in (
                ("T1", "x", "rien", "`a.py`"), ("T2", " ", "rien", "`a.py`, `b.py`"), ("T3", " ", "rien", "`c.py`"),
                ("T5", " ", "`T1`", "`e.py`"))))
        vus = [appel(["lancables", chemin] + o)[1].replace(chemin, "F").splitlines() for o in (
            ["--max", "3", "--tourne", "T1"], ["--max", "3"], ["--max", "2", "--tourne", "T2"], ["--tourne", "T9"])]
        # Relecteurs d'ENA5 : `scripts/*.py`, puis `scripts/`, partaient avec `scripts/vlp.py` (noms seuls comparés).
        ecrire(chemin, "# Essai\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [ ] — %s\n\n**Dépend de** : rien.\n**Fichiers** : `%s`.\n\n**Critère de fin**\n"
            "Rien.\n<!-- /FICHE -->\n" % (i, i, i, f) for i, f in (
                ("P1", "scripts/*.py"), ("P2", "scripts/vlp.py"), ("P3", "doc/*.md"), ("P4", "src/"), ("P5", "src/a.py"))))
        vus += [appel(["lancables", chemin] + o)[1].splitlines() for o in (["--max", "5"], ["--max", "5", "--tourne", "P4"])]
    assert (vus == [["LANCABLES T2 T3", "INDICE: T1 T2 a.py"], ["LANCABLES T2 T3 T5"], ["LANCABLES T3"],
                     ["GARDE: --tourne T9 : aucune fiche de ce nom dans F, ignorée", "LANCABLES T2 T3"],
                     ["LANCABLES P1 P2 P3 P4 P5", "INDICE: P1 P2 scripts/*.py", "INDICE: P4 P5 src/"],
                     ["LANCABLES P1 P2 P3 P5", "INDICE: P4 P5 src/", "INDICE: P1 P2 scripts/*.py"]]), ("ENA5 : T1 en relecture retient T5, T2 part à côté en INDICE: (ISO3) ; T2 compte dans --max ; une lancée "
             "inconnue : GARDE:, le reste sort ; un motif ou un dossier croise ce qu'il prend") + "\n" + str(repr(vus))
    # Toutes les façons d'écrire scripts/vlp.py, deux à deux : la famille entière, pas les deux exemples des relecteurs.
    meme = ["scripts/vlp.py", "vlp.py", "scripts/", "scripts/*.py", "scripts/{vlp,x}.py", "*.py", "scripts/*",
            "scripts/v*.py", "*/vlp.py"]
    manque = [(x, y) for x in meme for y in meme if not mod.croisent({x}, {y})]
    assert (manque == [] and not mod.croisent({"scripts/"}, {"doc/a.md"}) and not mod.croisent({"vlp.py"}, {"a.md"})), ("ENA5 : croisent voit les 81 paires d'un même fichier, et sépare scripts/ de doc/a.md") + "\n" + str(repr(manque))
    # 3e relecteur d'ENA5 : le filtre d'apercu_fiches jetait `.gitignore`, `skills`, `*.py`. Les formes relevées sur les
    # 421 lignes **Fichiers** du kit, par `lancables` — chaque paire vise un même fichier ; les libres, non.
    racine = {"skills": True, "scripts": True, "context ai": True, "seul": True, ".gitignore": False,
              ".gitattributes": False}

    def deux(x, y):
        """Vrai si `lancables` ne signale pas en `INDICE:` (ISO3) deux fiches aux lignes **Fichiers** `x` et `y` —
        chacune un fichier à elle en tête, ancré dans `seul/` que rien d'autre ne nomme : un nom seul (`A1.md`)
        croiserait tout dossier, et cacherait un nom perdu."""
        lignes = ("# E\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [ ] — %s\n\n**Dépend de** : rien.\n**Fichiers** : `seul/%s.txt`, %s.\n\n"
            "**Critère de fin**\nRien.\n<!-- /FICHE -->\n" % (i, i, i, i, f) for i, f in (("A1", x), ("B1", y)))).split("\n")
        return mod.indices(mod.apercu_lancables(lignes, "f.md", racine), ["A1", "B1"]) == []
    formes = [("`.gitignore`, `a.py`", "`.gitignore`, `b.py`"), ("`skills`, `doc/a.md`", "`skills/a/SKILL.md`"),
              ("skills", "`skills/tache/SKILL.md`"), ("`*.py`, `doc/b.md`", "`scripts/vlp.py`"),
              ("`scripts/`", "`scripts/vlp.py`"), ("`scripts\\vlp.py`", "`scripts/vlp.py`"),
              ("`./scripts/vlp.py`", "`scripts/vlp.py`"), ("`Scripts/vlp.py`", "`scripts/vlp.py`"),
              ("`CLAUDE.md`", "CLAUDE.md"), ("`skills/{a,b}/SKILL.md`", "`skills/b/SKILL.md`"),
              ("`vlp.css`", "`templates/vlp.css`"), ("`.gitattributes`", "`.gitattributes`, `a.md`"),
              ("`.editorconfig`, `a.py`", "`.editorconfig`, `b.py`"),
              ("`vlp.py:513`", "`scripts/vlp.py`"), ("`scripts/vlp.py:10-20`", "`scripts/vlp.py`"),
              ("`vlp.py niveau`", "`scripts/vlp.py`"), ("`git show main:CHANTIER.md`", "`CHANTIER.md`"),
              ("context AI/08-etat.md", "`context AI/08-etat.md`"), ("context AI/08-etat.md", "`context AI/*.md`"),
              ("`grep -n x context AI/08-etat.md`", "`context AI/08-etat.md`"),
              # 4e relecteur : un chemin partiel — son premier nom n'est pas à la racine — contre le chemin entier.
              ("`references/tache-page.md`", "`skills/tache/references/tache-page.md`"),
              ("`tache/SKILL.md`", "`skills/tache/SKILL.md`"), ("`references/*.md`", "`skills/`"),
              ("`references/tache-page.md`", "`skills/tache/references/`"), ("`references/`", "`skills/a/references/b.md`"),
              ("`skills/tache/SKILL.md`", "`skills/tache/skill.md`")]
    libres = [("`carte`, `a.py`", "`cmd_niveau`, `b.py`"), ("`skills/tache/SKILL.md`", "`skills/chantier/SKILL.md`"),
              ("`scripts/vlp.py`", "`doc/a.md`"), ("`scripts/vlp.py:10`", "`scripts/boucle.py`"),
              ("`references/a.md`", "`skills/tache/references/b.md`"), ("`skills/`", "`scripts/vlp.py`"),
              ("`./scripts/`", "`skills/a.md`")]
    rates = [f for f in formes if deux(*f)] + [f for f in libres if not deux(*f)]
    with tempfile.TemporaryDirectory(dir=tmp_path) as projet:
        ecrire(os.path.join(projet, "CHANTIER.md"), "x\n")
        os.mkdir(os.path.join(projet, "skills"))
        os.mkdir(os.path.join(projet, "doc"))
        fiches = os.path.join(projet, "context AI", "f.md")
        ecrire(fiches, "# E\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [ ] — %s\n\n**Dépend de** : rien.\n**Fichiers** : %s.\n\n**Critère de fin**\n"
            "Rien.\n<!-- /FICHE -->\n" % (i, i, i, f) for i, f in (
                ("Q1", "skills"), ("Q2", "`skills/a/SKILL.md`"), ("Q3", "`carte`, `doc/c.py`"))))
        cli = appel(["lancables", fiches, "--max", "3"])[1].splitlines()
        rates += [] if cli[:1] == ["LANCABLES Q1 Q2 Q3"] and [l[:14] for l in cli[1:]] == ["INDICE: Q1 Q2 "] else [cli]
    assert (rates == []), ("ENA5 : l'INDICE: de lancables lit les formes réelles (liste d'invités, racine du projet), et tait les "
             "libres (ISO3)") + "\n" + str(repr(rates))
    chef = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    plat = " ".join(chef.split())
    assert ('vlp.py" commiter "' in plat and "git add -A" not in plat and "agents ensemble" not in plat), ("ENA8 : le chef commite par commiter, jamais git add -A, et ne propose plus agents ensemble — lancables "
             "revient avec ISO6") + "\n" + "skills/enchainer/SKILL.md"


def test_iso3_indice(tmp_path):
    """ISO3 : `lancables` ne retient plus deux fiches qui se croisent — elles partent, chacune dans son worktree, et
    une ligne `INDICE:` le dit ; `--tourne` compte dans la largeur, un id inconnu n'arrête plus tout."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        chemin = os.path.join(t, "fiches.md")
        ecrire(os.path.join(t, "CHANTIER.md"), "x\n")      # un projet, `src` à sa racine : le chemin entier reste
        os.mkdir(os.path.join(t, "src"))
        ecrire(chemin, "# Essai\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [ ] — %s\n\n**Dépend de** : rien.\n**Fichiers** : %s.\n\n**Critère de fin**\n"
            "Rien.\n<!-- /FICHE -->\n" % (i, i, i, f) for i, f in (
                ("I1", "`src/a.py`"), ("I2", "`src/a.py`, `src/b.py`"), ("I3", "`src/c.py`"))))
        vus = [appel(["lancables", chemin] + o) for o in (
            ["--max", "2"], ["--max", "3"], ["--max", "2", "--tourne", "I1"], ["--max", "3", "--tourne", "I9"])]
    vus = [(code, s.replace(chemin, "F").splitlines()) for code, s in vus]
    assert (vus[:2] == [(0, ["LANCABLES I1 I2", "INDICE: I1 I2 src/a.py"]),
                         (0, ["LANCABLES I1 I2 I3", "INDICE: I1 I2 src/a.py"])]), ("ISO3 : trois prêtes dont deux se croisent — --max 2 → les deux et une ligne INDICE: ; --max 3 → les "
             "trois — mutant : exclure les croisées") + "\n" + str(repr(vus[:2]))
    assert (vus[2:] == [(0, ["LANCABLES I2", "INDICE: I1 I2 src/a.py"]),
                         (0, ["GARDE: --tourne I9 : aucune fiche de ce nom dans F, ignorée", "LANCABLES I1 I2 I3",
                              "INDICE: I1 I2 src/a.py"])]), ("ISO3 : --tourne I1 compte dans la largeur, son croisement avec I2 en INDICE: ; un id inconnu → GARDE:, "
             "ignoré, le reste sort, sort 0") + "\n" + str(repr(vus[2:]))


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


def forme_ancienne(html):
    """Les fiches remises à plat, comme avant PLI5 : ni `<details>` ni `<summary>`."""
    return mod.LI_FICHE.sub(lambda m: re.sub(r"</?details(?: open)?>|</?summary>", "", m.group(0)), html)


def test_fiches_repliees(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tfr:
        fiches = os.path.join(tfr, "q.md")
        page = os.path.join(tfr, "artefacts", "q.html")
        ancienne = os.path.join(tfr, "avant.html")
        ecrire(fiches, FICHES_PLI5)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0",
                         "--note", "Q1", "n1", "--note", "Q2", "n2", "--note", "Q3", "n3"])
        html = lire(page)
        ul = re.search(r'<ul class="fiches">.*?</ul>', html, re.S)
        zone = ul.group(0) if ul else ""
        assert (code == 0 and zone.count("<details") == 3 and zone.count("<details open>") == 1
                 and '<details open><summary><span class="titre">En cours</span><span class="etat">En cours</span></summary>'
                 in zone), ("PLI5 : 3 fiches, 3 blocs repliables, un seul ouvert — celui en cours"
                 " — mutant : tout ouvrir") + "\n" + str(s + zone)
        ecrire(ancienne, forme_ancienne(html))
        assert ("<details" not in lire(ancienne) and lire(ancienne).count('<li class="fiche"') == 3), ("PLI5 : la forme ancienne du test n'a plus de bloc repliable") + "\n" + str(lire(ancienne))
        code, s = appel(["comparer", ancienne, page])
        assert (code == 0 and "PERDU:" not in s and s.rstrip().startswith("COMPARER 0 perdus")), ("PLI5 : comparer contre l'ancienne forme ne dit aucune ligne de texte perdue") + "\n" + str(s)
        vues_neuves, vues_anciennes = mod.lis_page(html), mod.lis_page(lire(ancienne))
        assert (len(vues_neuves) == 3 and vues_anciennes == vues_neuves
                 and vues_anciennes["Q2"][0] == "encours"), ("PLI5 : une page à l'ancienne forme se lit encore, mêmes fiches"
                 " — mutant : ne lire que la nouvelle forme") + "\n" + str("%r\n%r" % (vues_neuves, vues_anciennes))
