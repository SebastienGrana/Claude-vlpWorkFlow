"""`noyau/nuit.py` : le fichier des nuits, `trier`, `plan`, `chef page`, les joints d'une page, le sommaire — migré de
l'ancienne suite maison (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import datetime
import io
import json
import os
import pathlib
import re
import subprocess
import tempfile

from aides import SCRIPTS, appel, ecrire, ligne_close, lire, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"


FICHES = """# Chantier Z

**Ouvert.** le 2026-10-08.

## Le socle commun

## Z1 [x] — faite
---
## Z2 [ ] — à faire
## Z10 [ ] — après
"""


def valide(texte):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "v.md")
        ecrire(f, texte)
        code, s = appel(["valider", f])
        return code, s.replace(f, "F")


def carte_sous(depart, session=None, nuit=False, argv=None, **options):
    """Rendre la carte de `depart` sous `CLAUDE_CODE_SESSION_ID=session` (absent si `None`) et `VLP_NUIT=1` si `nuit` :
    par `main(argv)` si `argv`, sinon par `carte(**options)` ; l'environnement remis sans ces deux variables."""
    os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    if session is not None:
        os.environ["CLAUDE_CODE_SESSION_ID"] = session
    if nuit:
        os.environ["VLP_NUIT"] = "1"
    s = io.StringIO()
    try:
        if argv:
            for un in argv:
                mod.main(un, s)
        else:
            mod.carte(depart, s, **options)
    finally:
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
        os.environ.pop("VLP_NUIT", None)
    return s.getvalue()


GABARIT_VLPCSS = os.path.join(ICI, "..", "templates", "vlp.css")


def test_sommaire(tmp_path):
    """FEU4 : sommaire et `id` des trois sections, posés une seule fois sur une feuille sans eux."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as ts:
        ecrire(os.path.join(ts, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(ts, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
        gabarit = pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8")
        sans = re.sub(r' id="(?:encours|todo|clos)"', "", gabarit.replace("\n" + mod.SOMMAIRE, ""))
        fdr = os.path.join(ts, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, sans)
        code, s = appel(["feuille", ts, "--date", "2026-09-27"])
        html = pathlib.Path(fdr).read_text(encoding="utf-8")
        noms = ("encours", "todo", "clos")
        assert code == 0
        assert "sommaire" not in sans
        assert 'id="' not in sans
        assert html.count('class="sommaire"') == 1
        assert html.count("<nav") == 1
        assert html.count('<a href="#') == 3
        assert all(html.count('href="#%s"' % n) == 1 and html.count('id="%s"' % n) == 1 for n in noms)
        assert (html.index("</header>") < html.index("<nav") < html.index('id="encours"')
                 < html.index('id="todo"') < html.index('id="clos"'))
        code, s = appel(["feuille", ts, "--date", "2026-09-28"])
        assert code == 0
        assert "inchangée" in s


FICHES_PLI2 = """# Chantier PLI2

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
x
<!-- /FICHE -->
"""


def gabarit_rapport():
    """Le texte du vrai gabarit `templates/rapport-choix.html`, que `chef page` remplit."""
    return mod.lire(os.path.join(ICI, "..", "templates", "rapport-choix.html"))


def option_page(valeur, **plus):
    """Une option de question de `chef page` : `valeur`, son libellé capitalisé, un effet ; `plus` s'y ajoute."""
    return dict({"valeur": valeur, "libelle": valeur.capitalize(), "effet": "ça change"}, **plus)


def base_page(**plus):
    """Le JSON ordinaire de `chef page` : une carte de décision, deux questions ; `plus` remplace des champs de tête."""
    d = {"projet": "Demo", "sujet": "essai", "titre": "Rapport d'essai", "date": "2026-10-01", "jauge": "Imprévu",
         "puces": ["Un **point** clé"],
         "decisions": {"cartes": [{"titre": "Ordre par défaut", "portee": "matin", "niveau": "faible",
                                   "probleme": "deux côtés ajoutent", "choix": "à la fin", "ecarte": "en tête",
                                   "prix": "ordre figé", "defaire": "une ligne"}]},
         "choix": [{"titre": "Quelle suite ?", "options": [option_page("oui"), option_page("non")]},
                   {"titre": "Quel plafond ?", "puces": ["le contexte"],
                    "options": [option_page("bas"), option_page("moyen", recommande=True), option_page("haut")]}]}
    d.update(plus)
    return d


def base_modifiee(f):
    """Une copie profonde de `base_page()`, passée à `f` qui la modifie en place ; rend la copie."""
    d = json.loads(json.dumps(base_page()))
    f(d)
    return d


def faire_page(dossier, d, nom, copie=None):
    """`(code, sortie, chemin)` de `cmd_chef_page` : `d` un dict (mis en JSON) ou un texte tel quel ; `nom` un fichier
    de `dossier`, ou un chemin absolu ; `copie` le gabarit, le vrai par défaut."""
    chemin = os.path.join(dossier, nom)
    s = io.StringIO()
    code = mod.cmd_chef_page(d if isinstance(d, str) else json.dumps(d, ensure_ascii=False), chemin, s,
                             gabarit_rapport() if copie is None else copie)
    return code, s.getvalue(), chemin


def octets_de(chemin):
    """Les octets de `chemin` ; `b""` s'il n'existe pas."""
    if not os.path.exists(chemin):
        return b""
    with open(chemin, "rb") as f:
        return f.read()


def test_chef_page(tmp_path):
    """chef page (chantier NUI, NUI17) : la page à cartes remplie par script, sur une copie lue du vrai gabarit —
    (a) la page du cas ordinaire."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        code, s, pa = faire_page(tcp, base_page(), "a.html")
        a = octets_de(pa)
        page = a.decode("utf-8")
        assert code == 0
        assert re.fullmatch(r"PAGE SAINE \d+ blocs\nCARTES D1 Q1 Q2\n", s) is not None
        comptes = (page.count('name="Q2"'), page.count("(recommandé)"), page.count('class="jauge moyen"'))
        assert (comptes == (3, 1, 1)), ("chef page (a) : name=\"Q2\" 3 fois, « (recommandé) » 1 fois, class=\"jauge moyen\" 1 fois") + "\n" + str(str(comptes))
        code2, s2 = appel(["vigile", pa])
        assert code2 == 0
        assert s2 == s.split("\n")[0] + "\n"
        assert 'data-cle="Demo-2026-10-01-essai"' in page
        assert "<title>Demo — Rapport d'essai</title>" in page
        comptes = (page.count("<h2>Tes réponses</h2>"), page.count("<script>"), page.count("<!--"))
        assert (comptes == (1, 1, 0)), ("chef page (a) : « Tes réponses » et <script> 1 fois, aucun commentaire") + "\n" + str(str(comptes))
        restes = [x for x in ("Le fil", "&lt;Projet&gt;", "<dépôt>") if x in page]
        assert (restes == []), ("chef page (a) : ni « Le fil », ni &lt;Projet&gt;, ni <dépôt>") + "\n" + str(str(restes))
        assert a != b""
        assert b"\r" not in a
        assert a.endswith(b"\n")
        defaut = [p for p in (("name=\"D1\"", 2), ("name=\"Q1\"", 2)) if page.count(p[0]) != p[1]]
        assert (defaut == []), ("chef page (a) : D1 et Q1 portent leurs deux boutons") + "\n" + str(str(defaut))
        assert ("<li>Un <strong>point</strong> clé</li>" in page), ("chef page (a) : les puces d'en-tête passent par cellule_md") + "\n" + str(page[page.find("<header"):][:300])


def test_chef_page_echappe(tmp_path):
    """chef page (b) : un texte échappé, une valeur sûre dans son attribut."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        d = base_page(projet="P & Q", titre="T < U")
        d["choix"][0]["titre"] = "a < b & **c**"
        d["choix"][0]["options"].append(option_page('a"b'))
        code, _s, pb = faire_page(tcp, d, "b.html")
        b = octets_de(pb).decode("utf-8")
        assert code == 0
        assert "<h3>🟡 Q1 · a &lt; b &amp; <strong>c</strong></h3>" in b
        assert "<title>P &amp; Q — T &lt; U</title>" in b
        assert 'data-cle="P &amp; Q-2026-10-01-essai"' in b
        assert 'value="a&quot;b"' in b


def test_chef_page_commentaire_cite(tmp_path):
    """chef page (c) : un commentaire de tête qui cite des balises — la page ne change pas d'un octet."""
    gabarit = gabarit_rapport()
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        a = octets_de(faire_page(tcp, base_page(), "a.html")[2])
        citee = gabarit.replace("<!--\n", '<!--\n  Cite <div class="page" data-cle="x"> et <script> ici.\n', 1)
        assert citee != gabarit
        assert -1 < citee.find("<script>") < citee.find("-->")
        assert -1 < citee.find('<div class="page"') < citee.find("-->")
        code, _s, pc = faire_page(tcp, base_page(), "c.html", citee)
        assert code == 0
        assert a != b""
        assert octets_de(pc) == a


def test_chef_page_sans_style(tmp_path):
    """chef page (d) : une page sans style ne part pas."""
    gabarit = gabarit_rapport()
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        sans_tete = re.sub(r"<link\b[^>]*>|<style\b.*?</style>", "", gabarit, flags=re.S | re.I)
        assert "<style" not in sans_tete.lower()
        assert "<link" not in sans_tete.lower()
        code, s, pd = faire_page(tcp, base_page(), "d.html", sans_tete)
        assert code == 1
        assert not os.path.exists(pd)
        assert s == 'GARDE: %s — aucun style (ni balise style, ni link rel="stylesheet")\n' % pd


def test_chef_page_non_remplie(tmp_path):
    """chef page (e) : ce qui ne se remplit pas — une GARDE chacun, rien d'écrit."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        sans_carte = {k: v for k, v in base_page().items() if k not in ("decisions", "choix")}
        sans_effet = base_modifiee(lambda x: x["choix"][1]["options"][2].pop("effet"))
        for k, (nom, entree, attendu) in enumerate((
                ("aucune carte", sans_carte, "GARDE: aucune carte : ni « decisions », ni « choix »\n"),
                ("jauge Super", base_page(jauge="Super"),
                 "GARDE: jauge : « Super » n'est pas un de %s\n" % " · ".join(mod.JAUGE)),
                ("option sans effet", sans_effet,
                 "GARDE: choix[1].options[2] : « effet » manque, ou n'est pas un texte non vide\n"))):
            code, s, pe = faire_page(tcp, entree, "e%d.html" % k)
            assert code == 1
            assert s == attendu
            assert not os.path.exists(pe)


def test_chef_page_autres_gardes(tmp_path):
    """chef page : les autres GARDE, chacune seule — JSON, champs, gabarit, écriture."""
    gabarit = gabarit_rapport()
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        occupe = os.path.join(tcp, "occupe")
        ecrire(occupe, "un fichier, pas un dossier\n")
        sans_script = gabarit.replace("<script>", "<scrip>")
        sans_reponses = gabarit.replace("<h2>Tes réponses</h2>", "<h2>Autre</h2>")
        autres = (
            ("JSON illisible", "pas du json", gabarit, "GARDE: JSON illisible"),
            ("JSON qui n'est pas un objet", "[1]", gabarit, "GARDE: le JSON n'est pas un objet\n"),
            ("@fichier absent", "@" + os.path.join(tcp, "absent.json"), gabarit, "GARDE: questions illisibles"),
            ("titre absent", base_modifiee(lambda x: x.pop("titre")), gabarit,
             "GARDE: racine : « titre » manque, ou n'est pas un texte non vide\n"),
            ("date invalide", base_page(date="demain"), gabarit, "GARDE: racine : « date » vaut AAAA-MM-JJ\n"),
            ("puces qui ne sont pas des textes", base_page(puces=[1]), gabarit,
             "GARDE: racine : « puces » doit être une liste de textes\n"),
            ("niveau inconnu", base_modifiee(lambda x: x["decisions"]["cartes"][0].update(niveau="fort")), gabarit,
             "GARDE: decisions.cartes[0] : « niveau » vaut faible ou moyen\n"),
            ("champ de carte absent", base_modifiee(lambda x: x["decisions"]["cartes"][0].pop("prix")), gabarit,
             "GARDE: decisions.cartes[0] : « prix » manque, ou n'est pas un texte non vide\n"),
            ("question à une option", base_page(choix=[{"titre": "Une ?", "options": [option_page("a")]}]), gabarit,
             "GARDE: choix[0] : 1 option(s), il en faut au moins deux\n"),
            ("valeur doublée", base_modifiee(lambda x: x["choix"][1]["options"][0].update(valeur="moyen")), gabarit,
             "GARDE: choix[1].options[1] : la valeur « moyen » est déjà prise\n"),
            ("deux recommandées", base_modifiee(lambda x: x["choix"][1]["options"][2].update(recommande=True)), gabarit,
             "GARDE: choix[1] : deux options recommandées\n"),
            ("recommande qui n'est pas un booléen",
             base_modifiee(lambda x: x["choix"][1]["options"][0].update(recommande="oui")), gabarit,
             "GARDE: choix[1].options[0] : « recommande » vaut true ou false\n"),
            ("genre de mal inconnu", base_page(mal=[{"genre": "grave", "titre": "x", "texte": "y"}]), gabarit,
             "GARDE: mal[0] : « genre » vaut erreur ou alerte\n"),
            ("gabarit sans <script>", base_page(), sans_script, "GARDE: gabarit : le <script> est introuvable\n"),
            ("gabarit sans « Tes réponses »", base_page(), sans_reponses,
             "GARDE: gabarit : la section « Tes réponses » est introuvable\n"))
        for k, (nom, entree, copie, attendu) in enumerate(autres):
            code, s, po = faire_page(tcp, entree, "g%d.html" % k, copie)
            assert code == 1
            assert s.startswith(attendu)
            assert s.count("GARDE:") == 1
            assert not os.path.exists(po)
        code, s, po = faire_page(tcp, base_page(), os.path.join("occupe", "p.html"))
        assert code == 1
        assert s.startswith("GARDE: %s — écriture impossible" % po)
        assert s.count("GARDE:") == 1


def test_chef_page_complet(tmp_path):
    """chef page : toutes les sections, dans l'ordre du gabarit, et les cinq mots de la jauge."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        complet = base_page(jauge="Pas bon", plage="NUI1 à NUI3", pied="Fin du **rapport**.",
                            chiffres={"cases": [{"valeur": "3", "legende": "fiches"}, {"valeur": "1,2 $", "legende": "coût"}],
                                      "sources": ["`vlp.py cout`"]},
                            fait=[{"ref": "NUI1", "code": "abc1234", "titre": "Relever", "livre": "un fichier", "cout": "0,5 $"}],
                            mal=[{"genre": "erreur", "titre": "Un défaut", "texte": "à revoir"},
                                 {"genre": "alerte", "titre": "Un doute", "texte": "à suivre"}],
                            fil=[{"heure": "19:22", "code": "NUI1", "texte": "fait"}])
        complet["decisions"]["intro"] = "Trois choix pris."
        code, s, pf = faire_page(tcp, complet, "complet.html")
        f = octets_de(pf).decode("utf-8")
        assert code == 0
        assert s.endswith("CARTES D1 Q1 Q2\n")
        titres = ["Les chiffres", "Ce qui a été fait", "Les décisions prises seul", "Les choix à trancher",
                  "Ce qui a mal tourné", "Le fil", "Tes réponses"]
        places = [f.find("<h2>%s" % t) for t in titres]
        assert -1 not in places
        assert places == sorted(places)
        manques = [x for x in ('class="jauge ko">❌ Pas bon</span>', "Demo · 2026-10-01 · NUI1 à NUI3",
                               '<div class="chiffre"><b>1,2 $</b><span>coût</span></div>', '<span class="mono">vlp.py cout</span>',
                               "<td class=\"n\">NUI1</td>", "Trois choix pris.", '<div class="erreur">', "🔥 Un défaut",
                               '<div class="alerte">', "⚠️ Un doute", "<time>19:22</time>", "Fin du <strong>rapport</strong>.")
                   if x not in f]
        assert (manques == []), ("chef page complet : jauge ko, plage, chiffres, tableau, intro, mal, fil et pied") + "\n" + str(str(manques))
        mots = [mod.html_jauge(m) for m in mod.JAUGE]
        attendus = ['<span class="jauge">✅ Tout va bien</span>', '<span class="jauge">🟢 Ça tient, mais…</span>',
                    '<span class="jauge moyen">⚠️ Imprévu</span>', '<span class="jauge ko">❌ Pas bon</span>',
                    '<span class="jauge ko">🔥 Grosse erreur</span>']
        assert (mots == attendus), ("chef page : les cinq mots de JAUGE, leur émoji et leur classe") + "\n" + str(str(mots))
        code, s = appel(["vigile", pf])
        assert code == 0
        assert s.startswith("PAGE SAINE")


def test_chef_page_commande(tmp_path):
    """chef page, la commande : le vrai gabarit sous KIT, le JSON par @fichier, la date du jour par défaut."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        a = octets_de(faire_page(tcp, base_page(), "a.html")[2])
        jq = os.path.join(tcp, "q.json")
        ecrire(jq, json.dumps(base_page(), ensure_ascii=False))
        sortie = os.path.join(tcp, "cmd.html")
        code, s = appel(["chef", "page", "--questions", "@" + jq, "--sortie", sortie])
        assert code == 0
        assert s.endswith("CARTES D1 Q1 Q2\n")
        assert a != b""
        assert octets_de(sortie) == a
        sans_date = {k: v for k, v in base_page().items() if k != "date"}
        code, s, pj = faire_page(tcp, sans_date, "jour.html")
        m = re.search(r'data-cle="Demo-(\d{4}-\d\d-\d\d)-essai"', octets_de(pj).decode("utf-8"))
        assert code == 0
        assert m is not None
        assert datetime.date.fromisoformat(m.group(1)) <= datetime.date.today()


def test_trier(tmp_path):
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    lignes_todo = ("| 1 | `AAA` — a | cite `scripts/vlp.py` | 2 fiches | — |\n"
                   "| 2 | `BBB` — b | cite `vlp.py archive` | 1 fiche | `KKK` |\n"
                   "| 3 | `CCC` — c | x | 1 fiche | `AAA` |\n"
                   "| 4 | `DDD` — d | 🟡 à trancher, non mesuré, %s | 1 fiche, push | — |\n"
                   "| 5 | `FFF` — f | x | 1 fiche, push | — |\n"
                   "| 6 | `GGG` — g | x | 1 fiche | `ZZZ` |\n"
                   "| 7 | `HHH` — h | cite `py \"dossier x/m.py\"` | ~6 fiches | — |\n"
                   "| 8 | `III` — i | x | ~½ fiche | — |\n"
                   "| 9 | `JJJ` — j | x | 1 fiche | 1 |\n" % mod.MARQUE_VISUELLE)
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")
        etat = os.path.join(tp, "ctx", "08-etat.md")
        ecrire(etat, "# État\n\n" + entete + lignes_todo + "\n## Journal\n")
        code, s = appel(["trier", tp])
        lignes = s.splitlines()
        canal = [l for l in lignes if l.startswith("CANAL ")]
        assert code == 0
        assert all("PRÊT %s" % c in lignes for c in ("AAA", "BBB", "CCC", "JJJ", "III"))
        assert "FICHIERS AAA scripts/vlp.py" in lignes
        assert "FICHIERS BBB vlp.py" in lignes
        assert "FICHIERS HHH dossier x/m.py" in lignes
        assert len(canal) == 3
        assert canal[0].startswith("CANAL 1 : AAA, BBB, CCC, JJJ — ")
        assert "fichier vlp.py : AAA, BBB" in canal[0]
        assert "CCC dépend de AAA" in canal[0]
        assert "CANAL 2 : HHH — inconnu → à la page" in canal
        assert "CANAL 3 : III — inconnu → à la page" in canal
        assert any(l.startswith("ÉCARTÉE DDD") for l in lignes)
        assert "MARQUES DDD 5 : 🟡 1 · à trancher 1 · non mesuré 1 · %s 1 · push 1" % mod.MARQUE_VISUELLE in lignes
        assert any(l.startswith("ÉCARTÉE FFF") for l in lignes)
        assert any(l.startswith("ÉCARTÉE GGG") for l in lignes)
        assert any(l.startswith("SOIR HHH") for l in lignes)
        assert not any(l.startswith("SOIR III") for l in lignes)
        assert (pathlib.Path(etat).read_text(encoding="utf-8") == "# État\n\n" + entete + lignes_todo + "\n## Journal\n"), ("NUI10 : trier n'écrit rien — le fichier d'état reste tel quel") + "\n" + ""
        ecrire(etat, "# État\n\n" + entete + "| 1 | `AAA` — a | `sed x | sha256sum` | 2 fiches | — |\n\n## Journal\n")
        code, s = appel(["trier", tp])
        assert code == 1
        assert s.startswith("GARDE: ligne 1 de la TODO")


def test_trier_branche(tmp_path, init_git):
    """BRA1 : dans Git, `trier` ne trie que sur `main` ; ailleurs, une seule ligne `GARDE:`, sort 1."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n")
        ecrire(os.path.join(tb, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `AAA` — a | x | 1 fiche | — |\n\n## Journal\n")
        init_git(tb)
        code_main, _s_main = appel(["trier", tb])
        subprocess.run(["git", "switch", "-q", "-c", "nuit/x"], cwd=tb, capture_output=True, check=False)
        code, s = appel(["trier", tb])
        assert code_main == 0
        assert code == 1
        assert len(s.splitlines()) == 1
        assert s.startswith("GARDE: trier hors de main")


ENTETE_TODO = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"

LECON_NUITS = "- 2026-09-26 · N=%d · %s · jouées 3 sur 5 · nuits 2026-09-25 · sessions s1"


def projet_nuits(tp, init_git):
    """Un dépôt Git à une ligne de TODO et un index dont `100-x.md` est le plus grand numéro, sans fichier des nuits ;
    rend la fonction qui relit l'index."""
    carte = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **artefact du chantier** : aucun\n\n"
             "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
    indice = ("# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
              "| `100-x.md` | un chantier |\n\nFin.\n")
    init_git(tp)
    ecrire(os.path.join(tp, "CHANTIER.md"), carte)
    ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), indice)
    ecrire(os.path.join(tp, "ctx", "08-etat.md"), "# État\n\n" + ENTETE_TODO + "| 1 | `AAA` — a | x | 1 fiche | — |\n\n## Journal\n")
    ecrire(os.path.join(tp, "ctx", "100-x.md"), "# x\n")
    return lambda: pathlib.Path(os.path.join(tp, "ctx", "00-INDEX.md")).read_text(encoding="utf-8")


def test_fichier_nuits(tmp_path, init_git, monkeypatch):
    """(a) création : le numéro suivant le plus grand, la ligne sous le plus grand numéro lu en entier."""
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        lire_idx = projet_nuits(tp, init_git)
        _, s0 = appel(["trier", tp])
        chemin = mod.fichier_nuits(tp, True)
        idx = lire_idx().splitlines()
        avant = lire_idx()
        assert chemin == os.path.join(tp, "ctx", "101-nuits.md")
        assert os.path.isfile(chemin)
        assert idx[idx.index("| `100-x.md` | un chantier |") + 1].startswith("| `101-nuits.md` |")
        assert "**clos**" not in avant
        assert "**ouvert**" not in avant
        assert "NUITS absent" in s0
        assert mod.fichier_nuits(tp, True) == chemin
        assert lire_idx() == avant
        assert appel(["archiver", tp])[1].startswith("ARCHIVÉ 0 ")
        assert lire_idx() == avant


def test_fichier_nuits_lecons(tmp_path, init_git, monkeypatch):
    """(b) écrire, retirer, indice, plafond, forme des leçons du fichier des nuits."""
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
    lecon = LECON_NUITS
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        projet_nuits(tp, init_git)
        chemin = mod.fichier_nuits(tp, True)
        ligne_t = "| 2026-09-25 | A | NUI | 3/2/1 | 4,50 |"
        premiere, seconde = mod.nuits_ecrire(chemin, ligne_t), mod.nuits_ecrire(chemin, ligne_t)
        l2 = lecon % (2, "cause un")
        mod.nuits_ecrire(chemin, l2)
        mod.nuits_ecrire(chemin, l2)
        lu = pathlib.Path(chemin).read_text(encoding="utf-8")
        assert premiere is True
        assert seconde is False
        assert lu.count(ligne_t) == 1
        assert lu.count(l2) == 1
        assert lu.index(ligne_t) < lu.index("## Leçons") < lu.index(l2)
        code, s = appel(["trier", tp])
        assert code == 0
        assert "--- Leçons : ctx/101-nuits.md (lignes " in s
        assert l2 + " — indice" in s.splitlines()
        retiree = mod.nuits_retirer(chemin, l2, "2026-09-27", "NUI12")
        encore = mod.nuits_retirer(chemin, l2, "2026-09-27", "NUI12")
        code, s = appel(["trier", tp])
        assert retiree is True
        assert encore is False
        assert l2 + " — retirée le 2026-09-27 par NUI12" in s.splitlines()
        assert " — indice" not in s
        assert code == 0
        for k in range(12):
            mod.nuits_ecrire(chemin, lecon % (3, "cause %d" % k))
        code, s = appel(["trier", tp])
        assert code == 0
        assert "GARDE" not in s
        mod.nuits_ecrire(chemin, lecon % (3, "cause 12"))
        code, s = appel(["trier", tp])
        assert code == 1
        assert "GARDE: 13 leçons vivantes" in s
        assert "TRI 1 rangs" in s
        ecrire(chemin, pathlib.Path(chemin).read_text(encoding="utf-8").replace(lecon % (3, "cause 12") + "\n", "- pas une forme\n"))
        code, s = appel(["trier", tp])
        assert code == 1
        assert "GARDE: leçon hors forme" in s
        assert "- pas une forme" in s
        assert "TRI 1 rangs" in s


def test_nuits_table_six_cellules():
    """(d) une ligne de table à 6 cellules lève une ValueError qui la nomme."""
    try:
        mod.nuits_du_fichier(mod.NUITS_TETE[:6] + ["| a | b | c | d | e | f |"] + mod.NUITS_TETE[6:])
        dit = "aucune erreur"
    except ValueError as e:
        dit = str(e)
    assert ("ligne 7 de la table des nuits : 6 cellules au lieu de 5" in dit), ("NUI11 (d) : une ligne de table à 6 cellules lève une ValueError qui la nomme") + "\n" + str(dit)


def fiche_carnet(c, nuit, code, lignes, refus=None):
    """Ajouter au carnet `c` une fiche `code` du chantier NUI : une ligne par `(role, usd_kit, usd_cli)` de `lignes`,
    `refus` posé sur la ligne `relire` seule."""
    for role, usd_kit, usd_cli in lignes:
        mod.carnet.ajouter(c, nuit=nuit, canal="A", chantier="NUI", role=role, fiche=code, usd_kit=usd_kit,
                           usd_cli=usd_cli, refus_n=refus if role == "relire" else None)


def test_fichier_nuits_taux(tmp_path, init_git, monkeypatch):
    """(c) TAUX nuit : carnets du dépôt, médiane des fiches acceptées ; TAUX jour : le prix par fiche de l'estimé
    d'`ouvrir`, sur la même feuille."""
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
    rang = ('          <tr>\n            <td>x</td>\n            <td class="mono">%s</td><td class="mono">2026-01-01</td>\n'
            '            <td class="mono">%s</td>\n            <td>y</td>\n          </tr>\n')
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        projet_nuits(tp, init_git)
        mod.fichier_nuits(tp, True)
        c1, c2 = mod.carnet.du_jour(tp, "2026-09-25"), mod.carnet.du_jour(tp, "2026-09-26")
        fiche_carnet(c1, "2026-09-25", "N1", [("jouer", 0.5, 99), ("relire", 0.5, 99)])
        fiche_carnet(c1, "2026-09-25", "N2", [("jouer", 0.5, 99), ("relire", 1.5, 99)])
        fiche_carnet(c2, "2026-09-26", "N3", [("jouer", 0.5, 99), ("relance", 1.0, 99), ("relire", 1.5, 99)])
        fiche_carnet(c2, "2026-09-26", "N4", [("jouer", 0.5, 99), ("relire", 3.5, 99)])
        _code, s = appel(["trier", tp])
        assert ("TAUX nuit indice — 4 fiches acceptées" in s.splitlines()), ("NUI11 (c) : 4 fiches acceptées → indice, sans chiffre — mutant : CARNET_MIN = 0") + "\n" + str(s)
        fiche_carnet(c2, "2026-09-26", "N5", [("jouer", 0.5, 99), ("relire", 9.5, 99)])
        fiche_carnet(c2, "2026-09-26", "R1", [("jouer", 100, 99), ("relire", 50, 99)], refus=1)
        fiche_carnet(c2, "2026-09-26", "R1", [("relance", 40, 99), ("relire", 50, 99)], refus=2)
        mod.carnet.ajouter(c1, nuit="2026-09-25", canal="A", chantier="NUI", role="relance", fiche="N1", usd_kit=None, usd_cli=99)
        _code, s = appel(["trier", tp])
        assert ("TAUX nuit médiane 3 $/fiche sur 5 fiches acceptées · sans usd_kit 1" in s.splitlines()), ("NUI11 (c) : 5 fiches (1, 2, 3, 4, 10), une refusée deux fois hors compte, une ligne sans usd_kit"
                 " → médiane 3 — mutant : usd_kit lu en usd_cli") + "\n" + str(s)
        ecrire(os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)")
               + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)") + rang % ("D1–D2", "≈2,0M (2 000 000)")
               + rang % ("E1–E8", "non recompté — fichier introuvable · non mesurable") + "</tbody>\n")
        _, s = appel(["trier", tp])
        ecrire(os.path.join(tp, "ctx", "30-q.md"), "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n")
        appel(["ouvrir", tp, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        estime = re.search(r"— (≈[\d,]+ \$/fiche sur \d+ clos) \(le", pathlib.Path(os.path.join(tp, "ctx", "30-q.md")).read_text(encoding="utf-8"))
        assert estime is not None
        assert estime.group(1) == "≈1,00 $/fiche sur 3 clos"
        assert "TAUX jour " + estime.group(1) in s.splitlines()


CARTE_PLAN = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
              "- **artefact du chantier** : aucun\n\n"
              "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")


def projet_plan(tp):
    """Un projet à trois lignes de TODO (AAA, BBB, CCC), sans fichier des nuits ; rend `(nuits, index)`, leurs chemins."""
    indice = ("# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
              "| `100-x.md` | un chantier |\n\nFin.\n")
    todo = ("# État\n\n" + ENTETE_TODO + "| 1 | `AAA` — a | x | 1 fiche | — |\n| 2 | `BBB` — b | x | 1 fiche | — |\n"
            "| 3 | `CCC` — c | x | 1 fiche | — |\n\n## Journal\n")
    ecrire(os.path.join(tp, "CHANTIER.md"), CARTE_PLAN)
    ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), indice)
    ecrire(os.path.join(tp, "ctx", "08-etat.md"), todo)
    ecrire(os.path.join(tp, "ctx", "100-x.md"), "# x\n")
    return os.path.join(tp, "ctx", "101-nuits.md"), os.path.join(tp, "ctx", "00-INDEX.md")


def octets_plan(nuits, index):
    """`(octets du fichier des nuits ou None s'il manque, octets de l'index)`."""
    with open(index, "rb") as fi:
        return (pathlib.Path(nuits).read_bytes() if os.path.isfile(nuits) else None), fi.read()


def texte_nuits(nuits):
    """Le texte du fichier des nuits, lu en octets puis décodé (les fins de ligne gardées)."""
    with open(nuits, "rb") as fn:
        return fn.read().decode("utf-8")


def json_plan(tp, nom, **corps):
    """Écrire `corps` en JSON dans `<tp>/<nom>.json` ; rend son chemin."""
    chemin = os.path.join(tp, nom + ".json")
    ecrire(chemin, json.dumps(corps))
    return chemin


def ch(code, prefixe, *reponses):
    """Un chantier d'un canal du plan : son code, son préfixe, ses réponses."""
    return {"code": code, "prefixe": prefixe, "reponses": list(reponses)}


def ecrire_plan(tp, f, date):
    """`(code, sortie)` de `plan ecrire` du JSON `f` à `date`."""
    return appel(["plan", "ecrire", tp, "--json", f, "--date", date])


def lire_plan(tp, *options):
    """`(code, sortie)` de `plan lire` avec `options`."""
    return appel(["plan", "lire", tp, *options])


def plans_du_soir(tp, nuits):
    """Le plan passé du 2026-09-25, une ligne de table et une leçon, puis le plan du soir 2026-09-30 (A = AAA et BBB,
    B = CCC) ; rend la sortie de ce dernier `plan ecrire`."""
    ecrire_plan(tp, json_plan(tp, "passee", borne_usd=3, borne_chantiers=1, A=[ch("AAA", "AAA", "ancienne")]), "2026-09-25")
    mod.nuits_ecrire(nuits, "| 2026-09-24 | A | NUI | 3/2/1 | 4,50 |")
    mod.nuits_ecrire(nuits, "- 2026-09-24 · N=3 · cause un · jouées 3 sur 5 · nuits 2026-09-24 · sessions s1")
    return ecrire_plan(tp, json_plan(tp, "soir", borne_usd=12.5, borne_chantiers=3,
                                     A=[ch("AAA", "AAA", "r1a", "r1b é"), ch("BBB", "BBB", "r2")], B=[ch("CCC", "CCC", "r3")]),
                       "2026-09-30")


def test_plan(tmp_path, monkeypatch):
    """(0) sans fichier des nuits : lire refuse ; ecrire le crée, sa ligne d'index comprise. (a) A = deux chantiers,
    B = un : lire par canal, dans l'ordre, aussi sous VLP_NUIT=1."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        nuits, index = projet_plan(tp)
        code, s = lire_plan(tp, "--date", "2026-09-25")
        assert code == 1
        assert s.startswith("GARDE: pas de fichier des nuits")
        assert not os.path.isfile(nuits)
        code, s = ecrire_plan(tp, json_plan(tp, "passee", borne_usd=3, borne_chantiers=1, A=[ch("AAA", "AAA", "ancienne")]), "2026-09-25")
        assert code == 0
        assert s.startswith("PLAN ctx/101-nuits.md · 2026-09-25 · 1 chantiers")
        assert os.path.isfile(nuits)
        assert "| `101-nuits.md` |" in octets_plan(nuits, index)[1].decode("utf-8")
        code, s = plans_du_soir(tp, nuits)
        monkeypatch.setenv("VLP_NUIT", "1")
        code_a, s_a = lire_plan(tp, "--date", "2026-09-30", "--canal", "A")
        code_b, s_b = lire_plan(tp, "--date", "2026-09-30", "--canal", "B")
        code_c, s_c = lire_plan(tp, "--date", "2026-09-30", "--canal", "A", "--chantier", "BBB")
        monkeypatch.delenv("VLP_NUIT")
        lignes_a = [l for l in s_a.splitlines() if l.startswith("CHANTIER ")]
        assert code == 0
        assert code_a == 0
        assert s_a.startswith("BORNE 12.5 $ · 3 chantiers\n")
        assert lignes_a == ["CHANTIER AAA · canal A · rang 1 · préfixe AAA", "CHANTIER BBB · canal A · rang 2 · préfixe BBB"]
        assert code_b == 0
        assert ([l for l in s_b.splitlines() if l.startswith("CHANTIER ")]
                 == ["CHANTIER CCC · canal B · rang 1 · préfixe CCC"])
        assert code_c == 0
        assert "- r2" in s_c.splitlines()
        assert "r1a" not in s_c
        assert "### AAA" not in s_c
        assert ("- r1b é" in lire_plan(tp, "--date", "2026-09-30", "--chantier", "AAA")[1].splitlines()), ("NUI12 (a) : la réponse en é revient telle quelle, en puce") + "\n" + ""
        code, s = lire_plan(tp, "--date", "2026-09-29")
        assert code == 1
        assert s.startswith("GARDE: pas de plan à la date 2026-09-29")
        assert lire_plan(tp)[0] == 1
        avant = texte_nuits(nuits)
        assert avant.count("## Nuit 2026-09-25") == 1
        assert (avant.index("## Nuit 2026-09-25")
                 < avant.index("## Nuit 2026-09-30") < avant.index("## Leçons"))


def test_plan_reecrit(tmp_path):
    """(b) réécrit à la même date : une seule section, le reste octet pour octet."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        nuits, _index = projet_plan(tp)
        plans_du_soir(tp, nuits)
        avant = texte_nuits(nuits)
        code, _s = ecrire_plan(tp, json_plan(tp, "soir2", borne_usd=7, borne_chantiers=2, A=[ch("AAA", "AAA", "neuf")]), "2026-09-30")
        apres = texte_nuits(nuits)
        assert code == 0
        assert apres.count("## Nuit 2026-09-30") == 1
        assert "- neuf" in apres
        assert "r1a" not in apres
        assert apres.index("## Nuit 2026-09-30") < apres.index("## Leçons")
        assert apres[:apres.index("## Nuit 2026-09-30")] == avant[:avant.index("## Nuit 2026-09-30")]
        assert apres[apres.index("## Leçons"):] == avant[avant.index("## Leçons"):]


def test_plan_refus(tmp_path, monkeypatch):
    """(c) neuf refus : GARDE:, sort 1, ni le fichier des nuits ni l'index ne bougent."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        nuits, index = projet_plan(tp)
        plans_du_soir(tp, nuits)
        refus = [
            ("code absent de la TODO", json_plan(tp, "r1", borne_usd=1, borne_chantiers=1, A=[ch("ZZZ", "ZZZ")])),
            ("préfixe NUIT (quatre lettres)", json_plan(tp, "r2", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "NUIT")])),
            ("préfixe déjà pris (E)", json_plan(tp, "r3", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "E")])),
            ("préfixe donné deux fois", json_plan(tp, "r4", borne_usd=1, borne_chantiers=2, A=[ch("AAA", "XXX")], B=[ch("BBB", "XXX")])),
            ("chantier dans deux canaux", json_plan(tp, "r5", borne_usd=1, borne_chantiers=2, A=[ch("AAA", "XXX")], B=[ch("AAA", "YYY")])),
            ("canal C", json_plan(tp, "r6", borne_usd=1, borne_chantiers=1, C=[ch("AAA", "XXX")])),
            ("JSON sans borne", json_plan(tp, "r7", A=[ch("AAA", "XXX")])),
            ("réponse à saut de ligne", json_plan(tp, "r8", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "XXX", "a\nb")])),
        ]
        for nom, f in refus:
            fichier_avant = octets_plan(nuits, index)
            code, s = ecrire_plan(tp, f, "2026-10-01")
            assert code == 1
            assert s.startswith("GARDE: ")
            assert octets_plan(nuits, index) == fichier_avant
        valide = json_plan(tp, "r9", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "XXX")])
        fichier_avant = octets_plan(nuits, index)
        monkeypatch.setenv("VLP_NUIT", "1")
        code, s = ecrire_plan(tp, valide, "2026-10-01")
        monkeypatch.delenv("VLP_NUIT")
        assert code == 1
        assert s.startswith("GARDE: VLP_NUIT=1")
        assert octets_plan(nuits, index) == fichier_avant
        code, s = ecrire_plan(tp, valide, "2026-10-01")
        assert (code == 0), ("NUI12 (c) : le même plan, sans VLP_NUIT → écrit (le refus venait bien de la variable)") + "\n" + str(s)


def test_plan_carte_nuit(tmp_path, monkeypatch):
    """(d) carte : NUIT=1 une fois, dans le bloc d'avant les fiches ; rien sinon."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        projet = os.path.join(tp, "proj")
        ecrire(os.path.join(projet, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
        ecrire(os.path.join(projet, "context AI", "20-z.md"), FICHES)

        def carte_nuit(valeur, relecteur=False):
            """Les lignes de la carte de `projet` sous `VLP_NUIT=valeur` (absente si `None`), la variable retirée après."""
            if valeur is None:
                monkeypatch.delenv("VLP_NUIT", raising=False)
            else:
                monkeypatch.setenv("VLP_NUIT", valeur)
            sortie = io.StringIO()
            mod.carte(projet, sortie, relecteur)
            monkeypatch.delenv("VLP_NUIT", raising=False)
            return sortie.getvalue().splitlines()

        nuit = carte_nuit("1")
        assert nuit.count("NUIT=1") == 1
        assert (nuit.index("--- CHANTIER.md ---") < nuit.index("NUIT=1")
                 < next(k for k, l in enumerate(nuit) if l.startswith("--- fiches :")))
        assert (not any(l.startswith("NUIT=") for l in carte_nuit("1", True) + carte_nuit("0") + carte_nuit(None))), ("NUI12 (d) : --relecteur, VLP_NUIT=0 et variable absente → aucune ligne NUIT=") + "\n" + ""


def contrastes_couts(barre, texte):
    """CTR1 : les variables de la ligne `:root` de vlp.css, et les rapports WCAG (luminance
    relative) de `barre` puis `texte`, chacune sur `--surface` puis `--ground`."""
    racine_css = next(l for l in lire(GABARIT_VLPCSS).splitlines() if l.startswith(":root"))
    css = dict(re.findall(r"(--[\w-]+):(#[0-9a-f]{6})", racine_css))

    def luminance(c):
        v = [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        v = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v]
        return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]

    def contraste(a, b):
        la, lb = sorted((luminance(a), luminance(b)), reverse=True)
        return (la + .05) / (lb + .05)
    return css, [contraste(c, css.get(f, "#000000")) for c in (barre, texte) for f in ("--surface", "--ground")]


META_BTN1 = '<meta charset="utf-8">'
SCRIPT_BTN1 = '<script src="vlp.js"></script>'
IMG_COUTS = '<img src="couts.svg"'


def files_de(s):
    """Le dict de la ligne `FILES` d'une sortie, ou None."""
    for l in s.splitlines():
        if l.startswith("FILES "):
            return json.loads(l[len("FILES "):])
    return None


def joints_recopies(s, dossier):
    """(a) : FILES a les clés `vlp.css` et `vlp.js`, chacune vers un fichier qui existe, en
    barres obliques, dans `dossier`, identique à l'octet à sa source de `templates/`."""
    files = files_de(s)
    return (files is not None and sorted(files) == ["vlp.css", "vlp.js"]
            and all("\\" not in c and os.path.isfile(c) and os.path.samefile(c, os.path.join(dossier, n))
                    and pathlib.Path(c).read_bytes() == pathlib.Path(os.path.join(ICI, "..", "templates", n)).read_bytes()
                    for n, c in files.items()))


def balises_une_fois(html):
    """(b) : le charset une fois, en première ligne ; le script une fois, en dernière."""
    lignes = html.rstrip("\n").split("\n")
    return (html.count(META_BTN1) == 1 and html.count(SCRIPT_BTN1) == 1
            and lignes[0] == META_BTN1 and lignes[-1] == SCRIPT_BTN1)


def sans_balises(html):
    """`html` sans sa ligne de charset ni sa ligne de script."""
    return html.replace(META_BTN1 + "\n", "").replace(SCRIPT_BTN1 + "\n", "")


def projet_btn1(tab):
    """Un projet équipé minimal, sa feuille posée depuis le gabarit (comme PLI2) ; rend `(projet, feuille)`."""
    proj = os.path.join(tab, "proj")
    ecrire(os.path.join(proj, "CHANTIER.md"),
           "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
           ""
           "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : U (test).\n")
    ecrire(os.path.join(proj, "ctx", "08-etat.md"),
           "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
    fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(fdr, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8"))
    return proj, fdr


def test_joints(tmp_path):
    """(c) d'abord : une page d'avant, sans charset ni script, les reçoit une fois ; une seconde
    régénération n'en ajoute pas — page du chantier, puis feuille de route ; un charset cité dans un commentaire
    n'est pas un charset posé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        ecrire(fiches, FICHES_PLI2)
        appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        ecrire(page, sans_balises(lire(page)))
        assert "<meta charset" not in lire(page)
        assert "vlp.js" not in lire(page)
        code, _s = appel(["page", fiches, page])
        assert code == 0
        assert balises_une_fois(lire(page))
        code, _s = appel(["page", fiches, page])
        assert code == 0
        assert balises_une_fois(lire(page))
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn1(tab)
        ecrire(fdr, sans_balises(lire(fdr)))
        code, _s = appel(["feuille", proj])
        assert code == 0
        assert balises_une_fois(lire(fdr))
        code, _s = appel(["feuille", proj])
        assert code == 0
        assert balises_une_fois(lire(fdr))
    cite = mod.migrer_joints("<!-- %s -->\n<p>x</p>\n" % META_BTN1)
    assert cite.startswith(META_BTN1 + "\n")
    assert cite.count(META_BTN1) == 2


def test_joints_page(tmp_path):
    """(a) et (b) : `page --creer`, puis `page` sans --creer ; vlp.js modifié à la main entre deux ; puis la feuille."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        art = os.path.join(tab, "artefacts")
        page = os.path.join(art, "p.html")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert code == 0
        assert joints_recopies(s, art)
        assert "CSS %s\n" % os.path.join(art, "vlp.css") in s
        assert (balises_une_fois(lire(page))), ("BTN1 : (b) page --creer — charset et script une fois chacun") + "\n" + str(lire(page)[:300])
        with open(os.path.join(art, "vlp.js"), "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        assert code == 0
        assert joints_recopies(s, art)
        assert (balises_une_fois(lire(page))), ("BTN1 : (b) page régénérée — charset et script une fois chacun") + "\n" + str(lire(page)[:300])
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn1(tab)
        art = os.path.dirname(fdr)
        code, s = appel(["feuille", proj])
        assert code == 0
        assert joints_recopies(s, art)
        assert "CSS %s\n" % os.path.join(art, "vlp.css") in s
        assert (balises_une_fois(lire(fdr))), ("BTN1 : (b) feuille régénérée — charset et script une fois chacun") + "\n" + str(lire(fdr)[:300])


def test_joints_commande(tmp_path):
    """`joints <dossier>` : les deux copies, et la ligne FILES seule ; un dossier absent est gardé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        code, s = appel(["joints", tab])
        assert code == 0
        assert joints_recopies(s, tab)
        assert len(s.splitlines()) == 1
        code, s = appel(["joints", os.path.join(tab, "absent")])
        assert code == 1
        assert s.startswith("GARDE: dossier introuvable")


def test_joints_gabarits():
    """Les deux gabarits : charset en première ligne, script en dernière, une fois chacun ; aucun lien local hors joints."""
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = pathlib.Path(os.path.join(ICI, "..", "templates", nom)).read_text(encoding="utf-8")
        assert (balises_une_fois(gabarit)), ("BTN1 : (b) gabarit %s — charset et script une fois chacun" % nom) + "\n" + str(gabarit[:300])
        # Dette BTN : /vlp:init publie la feuille remplie à la main, sans `feuille` — un lien local vers
        # autre chose qu'un joint y reste sans fichier (l'image couts.svg y restait, cassée).
        locaux = set(re.findall(r'(?:src|href)="(?!https?:|#|&lt;)([^"]+)"', gabarit))
        assert (locaux <= set(mod.JOINTS)), ("Dette BTN : gabarit %s — ne lie en local que les joints — mutant : image couts.svg remise"
                 % nom) + "\n" + str(str(sorted(locaux)))


# --- BTN5 : le coût des chantiers clos en image, `couts.svg` et sa balise.

def projet_btn5(tab, rangs):
    """Un projet équipé minimal, sa feuille posée depuis le gabarit, `rangs` en tête de ZONE:clos ; rend
    `(projet, feuille)`."""
    proj, fdr = projet_btn1(tab)
    gabarit = lire(fdr)
    i = gabarit.index("<tbody>\n", gabarit.index("<!-- ZONE:clos")) + len("<tbody>\n")
    ecrire(fdr, gabarit[:i] + "".join(rangs) + gabarit[i:])
    return proj, fdr


def rang_clos(nom, cout):
    """Une ligne de ZONE:clos au nom `nom` et au coût `cout`."""
    return ligne_close(cout).replace("<td>Test ", "<td>%s " % nom)


def barres(chemin):
    """[(x, hauteur)] des barres de `couts.svg`, de gauche à droite ; [] sans fichier."""
    if not os.path.isfile(chemin):
        return []
    return sorted((float(x), float(h)) for x, h in re.findall(
        r'<rect class="barre" x="([\d.]+)" y="[\d.]+" width="[\d.]+" height="([\d.]+)"', lire(chemin)))


def feuille_quatre_clos(tab):
    """Quatre lignes closes, la plus récente en haut : D 4 000, C sans coût, B 2 000, A 1 000 ; rend
    `(projet, feuille, couts.svg, code, sortie)` de la première `feuille`."""
    proj, fdr = projet_btn5(tab, [rang_clos("D", mod.arrondi(4000)), rang_clos("C", "non mesuré"),
                                  rang_clos("B", mod.arrondi(2000)), rang_clos("A", mod.arrondi(1000))])
    svg = os.path.join(os.path.dirname(fdr), "couts.svg")
    code, s = appel(["feuille", proj])
    return proj, fdr, svg, code, s


def test_couts_svg(tmp_path):
    """BTN5 : quatre lignes closes — trois barres à l'échelle, chacune colorée, la ligne FILES et la ligne LIRE."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        _proj, _fdr, svg, code, s = feuille_quatre_clos(tab)
        b = barres(svg)
        h = [x[1] for x in b]
        assert code == 0
        assert len(b) == 3
        r = sorted(h)
        assert abs(2 * r[0] - r[1]) <= 1
        assert abs(4 * r[0] - r[2]) <= 1
        assert b[-1][1] == max(h)
        assert b[0][1] == min(h)
        dessin = lire(svg)
        formes = re.findall(r"<(?:rect|text)\b[^>]*>", dessin)
        assert "%s tokens</text>" % mod.arrondi(4000) in dessin
        assert formes
        assert all('fill="#' in f for f in formes)
        files = files_de(s) or {}
        assert "couts.svg" in files
        assert "\\" not in files["couts.svg"]
        assert os.path.samefile(files["couts.svg"], svg)
        assert ("\nLIRE vlp.css vlp.js couts.svg\n" in s), ("REF29 : feuille dit LIRE avec couts.svg joint — mutant : ligne LIRE retirée") + "\n" + str(s)


def test_couts_svg_balise(tmp_path):
    """BTN5 : la balise de couts.svg, son texte de remplacement et ses données ; les contrastes (CTR1) ; une feuille
    d'avant, sans balise, la reçoit à sa régénération."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr, svg, _code, _s = feuille_quatre_clos(tab)
        dessin = lire(svg)
        html = lire(fdr)
        alt = re.search(r'<img src="couts\.svg" alt="([^"]*)"', html)
        assert html.count(IMG_COUTS) == 1
        assert html.index(IMG_COUTS) < html.index('<details class="clos">')
        assert alt is not None
        assert "3 barres" in alt.group(1)
        assert alt.group(1).endswith("le plus cher : D")
        donnees = re.search(r'<img src="couts\.svg"[^>]* data-couts="([^"]*)">', html)
        donnees = json.loads(mod.html.unescape(donnees.group(1))) if donnees else {}
        assert (donnees == {"couleur": mod.COUTS_BARRE, "barres": [[n, t, mod.arrondi(t)] for n, t in
                             (("A", 1000), ("B", 2000), ("D", 4000))]}), ("Graphique : data-couts porte la couleur et les barres [chantier, tokens, arrondi],"
                 " de la plus ancienne à la plus récente — mutant : attribut retiré") + "\n" + str(str(donnees))
        # CTR1 : l'image recopie `--cours` et `--doux` de vlp.css, lisibles à 4,5:1 sur les deux fonds.
        css, rapports = contrastes_couts(mod.COUTS_BARRE, mod.COUTS_TEXTE)
        assert mod.COUTS_BARRE == css.get("--cours")
        assert mod.COUTS_TEXTE == css.get("--doux")
        assert min(rapports) >= 4.5
        print("  CTR1 contrastes (barre/surface, barre/ground, texte/surface, texte/ground) : %s"
              % " ".join("%.2f" % r for r in rapports))
        ecrire(fdr, mod.BALISE_COUTS.sub("", html))
        appel(["feuille", proj])
        assert (lire(fdr).count(IMG_COUTS) == 1), ("BTN5 : une feuille d'avant, sans balise, la reçoit à sa régénération") + "\n" + str(lire(fdr)[-3000:])
        appel(["feuille", proj])
        assert lire(fdr).count(IMG_COUTS) == 1
        assert lire(svg) == dessin


def test_couts_svg_sans_cout(tmp_path):
    """Sans coût (les lignes d'exemple du gabarit seules) : ni fichier — un ancien est retiré —, ni balise ; des coûts
    mesurés, tous à 0 (dette BTN) : rien à dessiner, et pas de division par un maximum nul."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang_clos("C", "non mesuré")])
        svg = os.path.join(os.path.dirname(fdr), "couts.svg")
        ecrire(svg, "<svg/>")
        code, s = appel(["feuille", proj])
        assert code == 0
        assert not os.path.exists(svg)
        assert IMG_COUTS not in lire(fdr)
        assert "couts.svg" not in (files_de(s) or {})
        assert ("\nLIRE vlp.css vlp.js\n" in s), ("REF29 : feuille sans couts.svg dit LIRE sans lui") + "\n" + str(s)
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang_clos("B", mod.arrondi(0)), rang_clos("A", mod.arrondi(0))])
        code, s = appel(["feuille", proj])
        assert code == 0
        assert not os.path.exists(os.path.join(os.path.dirname(fdr), "couts.svg"))
        assert IMG_COUTS not in lire(fdr)
