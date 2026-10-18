"""La découpe aux commits, migrée de `tester_heures_commits` (l'ancienne suite maison, REF4) : `heures_commits`, puis
`page`, `cout` et `recompter` coupés. Un test par comportement ; chaque `assert` porte en message le libellé de la
vérification d'origine, mot pour mot — 29 en tout, comme les 29 `verifier` du groupe (REF5 les compare).

Q1 et Q2 partagent une session horodatée, un sous-agent part pendant Q2. Commits : Q ouvert +100, Q1 +300,
Q2 +600, Q clos +800, puis un qui ne nomme pas le préfixe. Tours : +50 (cadrage) et +700 (clôture) hors fiches ;
+200 et +250 à Q1 ; +400 et le sous-agent (+450, 2 tours) à Q2 ; +1000, après le dernier commit du chantier, ne
compte pas.
"""
import os

import pytest

from aides import appel, commits, ecrire, ligne_close, lire, mod, transcript

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
DECOUPE_TETE = ("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, "
                "un sous-agent compte à la fiche que nomme son prompt, sinon à son départ\n")
SUJETS_Q = [(100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
            (800, "Chantier Q clos : fini"), (900, "Autre : QA et Q12x ne nomment pas le préfixe")]
ATTENDU = (DECOUPE_TETE +
           "Q1 · ≈200,0k (200 000) · 2 tours · 1,00 $ = session ≈200,0k (200 000) · 2 tours · 1,00 $ + 0 sous-agent\n"
           "Q2 · ≈300,0k (300 000) · 3 tours · 1,50 $ = session ≈100,0k (100 000) · 1 tours · 0,50 $"
           " + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $\n"
           "hors fiches · ≈200,0k (200 000) · 2 tours · 1,00 $ = session ≈200,0k (200 000) · 2 tours · 1,00 $"
           " + 0 sous-agent\n"
           "TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours · 3,50 $ = session ≈500,0k (500 000)"
           " · 5 tours · 2,50 $ + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $\n")


def clos_(texte):
    """Le fichier de fiches `texte`, marqué clos sous son titre."""
    return texte.replace("# Chantier Q\n", "# Chantier Q\n\n**CLOS** le 2026-01-06.\n", 1)


@pytest.fixture
def q(tmp_path):
    """La session `sq` (6 tours horodatés) et son sous-agent ; `sans`, le même fichier de fiches hors Git."""
    t = str(tmp_path)
    sq = os.path.join(t, "s.jsonl")
    transcript(sq, 6, [T0 + d for d in (50, 200, 250, 400, 700, 1000)])
    os.makedirs(os.path.join(t, "s", "subagents"))
    transcript(os.path.join(t, "s", "subagents", "agent-a1.jsonl"), 2, [T0 + 450, T0 + 460])
    sans = os.path.join(t, "sans")
    ecrire(os.path.join(sans, "q.md"), QFICHES % (sq, sq))
    return {"t": t, "sq": sq, "sans": sans}


@pytest.fixture
def avec(q, depot):
    """Le chantier Q dans un dépôt : ses cinq commits datés."""
    d = str(depot)
    commits(d, SUJETS_Q, T0)
    ecrire(os.path.join(d, "q.md"), QFICHES % (q["sq"], q["sq"]))
    return d


@pytest.fixture
def ouv_texte(q):
    """Q1 cochée, Q2 pas encore, Q2 sans session : le fichier de FIN2 et de ZER1."""
    return (QFICHES % (q["sq"], "")).replace("## Q2 [x]", "## Q2 [ ]").replace("**Session** : \n", "")


def test_sans_depot(q):
    pourquoi = []
    h = mod.heures_commits(os.path.join(q["sans"], "q.md"), ["Q1", "Q2"], pourquoi)
    assert h is None and len(pourquoi) == 1 and pourquoi[0].startswith(
        ("git log en échec : ", "git ne se lance pas : ")), "heures_commits : sans .git, rien, et pourquoi"


def test_sans_git(q, monkeypatch):
    monkeypatch.setattr(mod.etat, "GIT", "git-absent-vlp")
    pourquoi = []
    h = mod.heures_commits(os.path.join(q["sans"], "q.md"), ["Q1", "Q2"], pourquoi)
    assert h is None and pourquoi[0].startswith("git ne se lance pas : "), \
        "heures_commits : sans git, rien — jamais un traceback"


def test_heures_d_auteur(avec):
    h = mod.heures_commits(os.path.join(avec, "q.md"), ["Q1", "Q2"])
    assert h == ({"Q1": T0 + 300, "Q2": T0 + 600}, [T0 + 100, T0 + 300, T0 + 600, T0 + 800], [T0 + 900], []), \
        "heures_commits : heure d'auteur, commits qui nomment le préfixe"


def test_aucun_commit_de_fiche(avec):
    pourquoi = []
    h = mod.heures_commits(os.path.join(avec, "q.md"), ["Z1"], pourquoi)
    assert h is None and pourquoi == ["aucun commit qui nomme Z"], "heures_commits : aucun commit de fiche, et pourquoi"


def test_page_coupee(q, avec):
    page = os.path.join(avec, "artefacts", "q.html")
    code, s = appel(["page", os.path.join(avec, "q.md"), page, "--creer", "--projet", "P", "--titre", "T",
                     "--resultat", "R", "--date", "2026-01-05"])
    html = lire(page) if os.path.exists(page) else ""
    assert (code == 0
            and '<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>' in html
            and '<span class="cout mono">≈300,0k (300 000) · 3 tours · 1,50 $</span>' in html
            and '<p class="mono cout-hors">Hors fiches : ≈200,0k (200 000) · 2 tours · 1,00 $</p>' in html
            and '<p class="mono cout-total">Coût du chantier : ≈700,0k (700 000) · 7 tours · 3,50 $</p>' in html
            and "Hors fiches : &lt;" not in html
            and ", dont hors fiches ≈200,0k (200 000) · 2 tours · 1,00 $" in s), \
        "page coupée aux commits : sous-agent compris, hors fiches à part, total = somme"
    avant = lire(page)
    appel(["page", os.path.join(avec, "q.md"), page, "--date", "2026-01-05"])
    assert lire(page) == avant, "page coupée : régénérer deux fois ne change rien"
    # Sans .git, la même page retombe sur l'ancienne logique : Q1 garde son coût affiché, Q2 prend la session
    # moins Q1 et la part à aucune fiche ; ni sous-agent, ni ligne hors fiches.
    ancienne = os.path.join(q["sans"], "artefacts", "q.html")
    ecrire(ancienne, avant)
    code, s = appel(["page", os.path.join(q["sans"], "q.md"), ancienne, "--date", "2026-01-05"])
    html = lire(ancienne)
    assert (code == 0
            and html.count('<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>') == 2
            and '<p class="mono cout-hors">' not in html
            and "Coût du chantier : ≈600,0k (600 000) · 6 tours · 3,00 $" in html), \
        "page sans .git : l'ancienne logique, sur l'ancienne page"


def test_cout_coupe(q, avec, monkeypatch):
    fiches = os.path.join(avec, "q.md")
    code, s = appel(["cout", fiches])
    assert code == 0 and s == ATTENDU, "cout coupé aux commits : une ligne par fiche, hors fiches, TOTAL"
    assert [mod.triplet(l)[:2] for l in s.splitlines()[1:]] == [(200000, 2), (300000, 3), (200000, 2), (700000, 7)], \
        "cout : triplet relit la somme de chaque ligne, celle de la page"
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", q["sq"])
    code, s = appel(["cout", fiches, "--session"])
    assert (code == 0 and s.startswith("SESSION=%s\nfichier\t" % q["sq"]) and "\nagent-a1.jsonl\t" in s
            and s.endswith("\n" + ATTENDU)), "cout --session : la table de la session, puis la découpe"
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID")
    code, s = appel(["cout", os.path.join(q["sans"], "q.md")])
    assert (code == 0 and s.startswith("DÉCOUPE aucune — git log en échec : ") and "\ns.jsonl\t" in s
            and "\nagent-a1.jsonl\t" in s and "\nTOTAL\t" in s), "cout sans .git : la table d'avant, sous la raison"


def test_cout_clos_avec_commits(q, avec):
    ecrire(os.path.join(avec, "qk.md"), clos_(QFICHES % (q["sq"], q["sq"])))
    code, s = appel(["cout", os.path.join(avec, "qk.md")])
    assert code == 0 and s == ATTENDU, "cout : clos avec commits de fiche, la découpe"


def test_cout_borne_par_le_bas(q, depots):
    """FIN1 : dans une session qui enchaîne plusieurs chantiers, « Chantier P clos » (60) borne Q par le bas — le
    tour de 50 ne compte nulle part ; sans clôture, hors fiches va au bout."""
    multi = str(depots("multi"))
    commits(multi, [(60, "Chantier P clos : fini"), (100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"),
                    (600, "Q2 : Brancher")], T0)
    ecrire(os.path.join(multi, "q.md"), QFICHES % (q["sq"], q["sq"]))
    code, s = appel(["cout", os.path.join(multi, "q.md")])
    assert (code == 0 and "\nhors fiches · ≈200,0k (200 000) · 2 tours · 1,00 $ = session" in s
            and "\nTOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours · 3,50 $ = " in s), \
        "cout : P clos borne Q par le bas, sans clôture hors fiches va au bout"


def test_cout_premiere_fiche(depots, ouv_texte):
    """FIN2 : Q1 cochée, mesurée avant son commit — seule l'ouverture nomme Q. Elle part de l'ouverture (100), pas
    du début de la session : le tour de 50 ne compte pas."""
    ouv = str(depots("ouv"))
    commits(ouv, [(60, "Chantier P clos : fini"), (100, "Chantier Q ouvert : cadré")], T0)
    ecrire(os.path.join(ouv, "q.md"), ouv_texte)
    code, s = appel(["cout", os.path.join(ouv, "q.md")])
    assert (code == 0 and "\nQ1 · ≈700,0k (700 000) · 7 tours · 3,50 $ = " in s
            and "\nTOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s), \
        "cout : la première fiche avant son commit"


def test_clos_sans_commit_de_fiche(q, depots, ouv_texte):
    """ZER1 : un chantier clos sans commit de fiche — sa dernière mention est sa clôture, et la plage qui en part
    ne voit aucun tour ; son travail commité sous d'autres messages (1050), hors fiches non plus. Il retombe sur
    les sessions entières, et le dit ; sans ligne **CLOS**, la découpe reste, et une garde dit qu'elle ne garde
    rien."""
    clq = str(depots("clq"))
    commits(clq, [(60, "Chantier P clos : fini"), (100, "Chantier Q ouvert : cadré"),
                  (1050, "Autre : le travail, sans nommer le préfixe"), (1100, "Chantier Q clos : fini")], T0)
    ecrire(os.path.join(clq, "q.md"), ouv_texte)
    ecrire(os.path.join(clq, "qz.md"), clos_(ouv_texte))
    code, s = appel(["cout", os.path.join(clq, "qz.md")])
    assert (code == 0 and s.startswith("DÉCOUPE aucune — chantier clos sans commit « Q1 : » ni d'une autre fiche : "
                                       "sessions entières, sous-agents compris\n")
            and "\nTOTAL\t8\t0\t-\t-\t800000\t0\t0\t0\t0\t800000\t800000\t4.00\t0\n" in s), \
        "cout : clos sans commit de fiche, les sessions entières, et pourquoi"
    code, s = appel(["page", os.path.join(clq, "qz.md"), os.path.join(clq, "artefacts", "qz.html"), "--creer",
                     "--projet", "P", "--titre", "T", "--resultat", "R", "--date", "2026-01-05"])
    html = lire(os.path.join(clq, "artefacts", "qz.html")) if code == 0 else ""
    assert (code == 0 and '<p class="mono cout-hors">' not in html
            and "Coût du chantier : ≈600,0k (600 000) · 6 tours · 3,00 $" in html), \
        "page : clos sans commit de fiche, les sessions entières, sans hors fiches"
    pourquoi = []
    h = mod.heures_commits(os.path.join(clq, "qz.md"), ["Q1", "Q2"], pourquoi, clos=True)
    assert h is None and pourquoi == ["chantier clos sans commit « Q1 : » ni d'une autre fiche"], \
        "heures_commits : clos sans commit de fiche, le repli et pourquoi"
    h = mod.heures_commits(os.path.join(clq, "q.md"), ["Q1", "Q2"])
    assert h == ({}, [T0 + 100, T0 + 1100], [T0 + 60, T0 + 1050], []), \
        "heures_commits : en cours sans commit de fiche, la découpe"
    code, s = appel(["cout", os.path.join(clq, "q.md")])
    assert (code == 0 and s.startswith("GARDE: découpe à zéro — aucun tour de 2 transcripts ne tombe dans une plage\n"
                                       "DÉCOUPE aux commits de fiche")
            and "\nTOTAL (fiches + hors fiches) · 0 · 0 tours · 0,00 $ = " in s), "cout : une découpe à zéro le dit"
    c2 = os.path.join(q["t"], "c2.jsonl")
    transcript(c2, 1, [T0 + 1080])
    ecrire(os.path.join(clq, "q2.md"), lire(os.path.join(clq, "q.md")).replace(
        "## Le socle commun", "**Session** : %s\n\n## Le socle commun" % c2, 1))
    code, s = appel(["cout", os.path.join(clq, "q2.md")])
    assert code == 0 and "GARDE" not in s and "\nhors fiches · ≈100,0k (100 000) · 1 tours · 0,50 $ = " in s, \
        "cout : fiches à zéro, un tour hors fiches — pas de garde"


def test_session_du_cadrage(q, avec):
    """CAD1 : le cadrage joué dans une autre session, notée en tête du fichier — deux tours avant l'ouverture, un
    après la clôture : les deux premiers comptent, hors fiches."""
    sc = os.path.join(q["t"], "c.jsonl")
    transcript(sc, 3, [T0 + d for d in (20, 40, 1000)])
    qc = os.path.join(avec, "qc.md")
    ecrire(qc, (QFICHES % (q["sq"], q["sq"])).replace("## Le socle commun", "**Session** : %s\n\n## Le socle commun" % sc))
    code, s = appel(["cout", qc])
    assert code == 0 and s.splitlines() == ATTENDU.splitlines()[:3] + [
        "hors fiches · ≈400,0k (400 000) · 4 tours · 2,00 $ = session ≈400,0k (400 000) · 4 tours · 2,00 $ + 0 sous-agent",
        "TOTAL (fiches + hors fiches) · ≈900,0k (900 000) · 9 tours · 4,50 $ = session ≈700,0k (700 000) · 7 tours · 3,50 $"
        " + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $"], "cout : la session du cadrage, en tête, compte hors fiches"
    code, s = appel(["page", qc, os.path.join(avec, "artefacts", "qc.html"), "--creer", "--projet", "P", "--titre", "T",
                     "--resultat", "R", "--date", "2026-01-05"])
    html = lire(os.path.join(avec, "artefacts", "qc.html")) if code == 0 else ""
    assert (code == 0
            and '<p class="mono cout-hors">Hors fiches : ≈400,0k (400 000) · 4 tours · 2,00 $</p>' in html
            and '<p class="mono cout-total">Coût du chantier : ≈900,0k (900 000) · 9 tours · 4,50 $</p>' in html), \
        "page : la session du cadrage, en tête, compte hors fiches"


SEULE = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
         "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n%s**Critère de fin**\n<!-- /FICHE -->\n")


@pytest.fixture
def rc(q, depots):
    """REC1 : un projet dont l'index nomme quatre clos — Q se coupe aux commits ; M partage sa session sans commit
    qui le nomme, N n'a pas de session, P une transcription absente, K n'est pas à l'index."""
    d = str(depots("rc"))
    commits(d, SUJETS_Q, T0)
    ecrire(os.path.join(d, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
           "| `q.md` | chantier **clos** « Q », `Q1..Q2` |\n| `m.md` | chantier **clos** « M », `M1..M1` |\n"
           "| `n.md` | chantier **clos** « N », `N1..N1` |\n| `p.md` | chantier **clos** « P », `P1..P1` |\n")
    ecrire(os.path.join(d, "ctx", "q.md"), clos_(QFICHES % (q["sq"], q["sq"])))
    ecrire(os.path.join(d, "ctx", "m.md"), SEULE % ("M", "M", "M", "**Session** : %s\n" % q["sq"]))
    ecrire(os.path.join(d, "ctx", "n.md"), SEULE % ("N", "N", "N", ""))
    ecrire(os.path.join(d, "ctx", "p.md"), SEULE % ("P", "P", "P", "**Session** : rec1-transcription-absente\n"))
    ecrire(os.path.join(d, "ctx", "artefacts", "feuille-de-route.html"),
           '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
           + "".join(ligne_close(c).replace("Q1–Q2", pl) for pl, c in (
               ("Q1–Q2", mod.arrondi(650000)), ("M1", mod.arrondi(300000)), ("N1", mod.arrondi(999)),
               ("P1", mod.arrondi(2000)), ("K1–K3", mod.arrondi(1500)), ("E1–E8", "non mesurable")))
           + "        </tbody>\n      </table>\n")
    return d


def disque(racine):
    """Tous les fichiers sous `racine`, hors `.git`, et leur texte."""
    return {os.path.relpath(os.path.join(r, n), racine): lire(os.path.join(r, n))
            for r, _, ns in os.walk(racine) if ".git" not in r.split(os.sep) for n in ns}


def test_recompter_lit_sans_ecrire(rc):
    avant = disque(rc)
    code, s = appel(["recompter", rc])
    assert code == 0 and s.splitlines() == [
        "Q inscrit 650 000 · recompté 700 000 · écart +50 000 · découpe · partagée avec M",
        "M inscrit 300 000 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (aucun commit qui nomme M)"
        " · partagée avec Q",
        "N inscrit 999 · recompté gardé · écart +0 · gardé — sans session",
        "P inscrit 2 000 · recompté gardé · écart +0 · gardé — transcription absente (rec1-transcription-absente)",
        "K inscrit 1 500 · recompté gardé · écart +0 · gardé — fichier introuvable",
        "E inscrit 0 · recompté gardé · écart +0 · gardé — fichier introuvable",
        "RECOMPTE 6 clos · 1 recomptés · 5 gardés · inscrit 954 499 · recompté 1 004 499 · écart +50 000"], \
        ("recompter : un clos découpé, des gardés à écart 0, la somme avec les gardés — mutants :"
         " un gardé compté dans l'écart, la somme sans les gardés")
    code2, s2 = appel(["cout", os.path.join(rc, "ctx", "q.md")])
    assert code2 == 0 and "\nTOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s2, \
        "recompter : le recompté de Q est le TOTAL de cout"
    assert disque(rc) == avant, "recompter n'écrit rien"


def test_recompter_ecrire(rc, tmp_path):
    """REC3 : --ecrire marque les six lignes en tête de cellule, resomme pied et résumé, puis ne change plus rien."""
    fr = os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(fr, lire(fr).replace("      <table>\n", '      <summary><span class="resume-clos">vieux</span></summary>\n'
                                "      <table>\n", 1).replace("      </table>\n",
           '        <tfoot>\n          <tr><td colspan="3">Total cumulé</td><td class="mono"><strong>vieux'
           '</strong></td><td class="mono">vieux</td></tr>\n        </tfoot>\n      </table>\n', 1))
    code, s = appel(["recompter", rc, "--ecrire"])
    feuille_ = lire(fr)
    corps_ = feuille_[:feuille_.find("<tfoot>")]
    assert (code == 0 and mod.total_clos(corps_) == 1004499
            and s.splitlines()[-2:] == [
                "RECOMPTE 6 clos · 1 recomptés · 5 gardés · inscrit 954 499 · recompté 1 004 499 · écart +50 000",
                "ÉCRIT 6 cellules · total 954 499 → 1 004 499"]
            and '<td class="mono">recompté (REC), était 650 000 · ≈700,0k (700 000)</td>' in feuille_
            and '<td class="mono">non recompté — sans session · (999)</td>' in feuille_
            and '<td class="mono">non recompté — fichier introuvable · non mesurable</td>' in feuille_), \
        ("recompter --ecrire : total_clos égale le recompté — mutants : la marque posée en parenthèses,"
         " la marque dans une balise")
    assert ("<strong>%s</strong></td><td class=\"mono\"></td>" % mod.arrondi(1004499) in feuille_
            and '<span class="resume-clos">%s</span>' % mod.resume_clos(6, 1004499) in feuille_), \
        ("recompter --ecrire : pied et résumé resommés, sans $ (aucune ligne au prix mesuré) — mutant :"
         " le pied non resommé")
    code, s = appel(["recompter", rc, "--ecrire"])
    assert (code == 0 and lire(fr) == feuille_
            and s.splitlines()[-1] == "ÉCRIT 0 cellules · total 1 004 499 → 1 004 499"
            and "Q inscrit 700 000 · recompté 700 000 · écart +0 · découpe · partagée avec M" in s), \
        "recompter --ecrire relancé : rien ne change"
    sans_chantier = tmp_path / "sans-chantier"
    sans_chantier.mkdir()
    code, s = appel(["recompter", str(sans_chantier)])
    assert code == 1 and s.startswith("GARDE: pas de CHANTIER.md"), "recompter : pas de CHANTIER.md, une garde"
