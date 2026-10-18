"""`noyau/nuit.py` : le fichier des nuits, `trier`, `plan`, `chef page`, les joints d'une page, le sommaire — migré de
`scripts/test-vlp.py` (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import datetime
import io
import json
import os
import re
import subprocess
import tempfile

from aides import SCRIPTS, appel, ecrire, ligne_close, lire, mod

ICI = SCRIPTS     # le dossier de scripts/test-vlp.py, d'où ces tests viennent

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
        gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read()
        sans = re.sub(r' id="(?:encours|todo|clos)"', "", gabarit.replace("\n" + mod.SOMMAIRE, ""))
        fdr = os.path.join(ts, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, sans)
        code, s = appel(["feuille", ts, "--date", "2026-09-27"])
        html = io.open(fdr, encoding="utf-8").read()
        noms = ("encours", "todo", "clos")
        assert (code == 0 and "sommaire" not in sans and 'id="' not in sans
                 and html.count('class="sommaire"') == 1 and html.count("<nav") == 1
                 and html.count('<a href="#') == 3
                 and all(html.count('href="#%s"' % n) == 1 and html.count('id="%s"' % n) == 1 for n in noms)
                 and html.index("</header>") < html.index("<nav") < html.index('id="encours"')
                 < html.index('id="todo"') < html.index('id="clos"')), ("FEU4 : un sommaire sous l'en-tête, trois liens, chaque cible id une fois") + "\n" + str((s, html[:1500]))
        code, s = appel(["feuille", ts, "--date", "2026-09-28"])
        assert (code == 0 and "inchangée" in s), ("FEU4 : 2e appel inchangée") + "\n" + str(s)


FICHES_PLI2 = """# Chantier PLI2

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
x
<!-- /FICHE -->
"""


def test_chef_page(tmp_path):
    """chef page (chantier NUI, NUI17) : la page à cartes remplie par script, sur une copie lue du vrai gabarit."""
    gabarit = mod.lire(os.path.join(ICI, "..", "templates", "rapport-choix.html"))

    def option(valeur, **plus):
        return dict({"valeur": valeur, "libelle": valeur.capitalize(), "effet": "ça change"}, **plus)

    def base(**plus):
        d = {"projet": "Demo", "sujet": "essai", "titre": "Rapport d'essai", "date": "2026-10-01", "jauge": "Imprévu",
             "puces": ["Un **point** clé"],
             "decisions": {"cartes": [{"titre": "Ordre par défaut", "portee": "matin", "niveau": "faible",
                                       "probleme": "deux côtés ajoutent", "choix": "à la fin", "ecarte": "en tête",
                                       "prix": "ordre figé", "defaire": "une ligne"}]},
             "choix": [{"titre": "Quelle suite ?", "options": [option("oui"), option("non")]},
                       {"titre": "Quel plafond ?", "puces": ["le contexte"],
                        "options": [option("bas"), option("moyen", recommande=True), option("haut")]}]}
        d.update(plus)
        return d

    def modifiee(f):
        d = json.loads(json.dumps(base()))
        f(d)
        return d

    with tempfile.TemporaryDirectory(dir=tmp_path) as tcp:
        def faire(d, nom, copie=gabarit):
            """`(code, sortie, chemin)` : `nom` est un fichier du dossier temporaire, ou un chemin absolu."""
            chemin = os.path.join(tcp, nom)
            s = io.StringIO()
            code = mod.cmd_chef_page(d if isinstance(d, str) else json.dumps(d, ensure_ascii=False), chemin, s, copie)
            return code, s.getvalue(), chemin

        def octets_de(chemin):
            if not os.path.exists(chemin):
                return b""
            with open(chemin, "rb") as f:
                return f.read()

        # (a) la page du cas ordinaire
        code, s, pa = faire(base(), "a.html")
        a = octets_de(pa)
        page = a.decode("utf-8")
        assert (code == 0 and re.fullmatch(r"PAGE SAINE \d+ blocs\nCARTES D1 Q1 Q2\n", s) is not None), ("chef page (a) : jauge Imprévu, une décision, Q1 à deux options, Q2 à trois — sort 0, CARTES D1 Q1 Q2") + "\n" + str(s)
        comptes = (page.count('name="Q2"'), page.count("(recommandé)"), page.count('class="jauge moyen"'))
        assert (comptes == (3, 1, 1)), ("chef page (a) : name=\"Q2\" 3 fois, « (recommandé) » 1 fois, class=\"jauge moyen\" 1 fois") + "\n" + str(str(comptes))
        code2, s2 = appel(["vigile", pa])
        assert (code2 == 0 and s2 == s.split("\n")[0] + "\n"), ("chef page (a) : vigile sur le fichier, PAGE SAINE du même compte de blocs") + "\n" + str(s2)
        assert ('data-cle="Demo-2026-10-01-essai"' in page and "<title>Demo — Rapport d'essai</title>" in page), ("chef page (a) : data-cle <projet>-<date>-<sujet> et <title> <projet> — <titre>") + "\n" + str(page[:200])
        comptes = (page.count("<h2>Tes réponses</h2>"), page.count("<script>"), page.count("<!--"))
        assert (comptes == (1, 1, 0)), ("chef page (a) : « Tes réponses » et <script> 1 fois, aucun commentaire") + "\n" + str(str(comptes))
        restes = [x for x in ("Le fil", "&lt;Projet&gt;", "<dépôt>") if x in page]
        assert (restes == []), ("chef page (a) : ni « Le fil », ni &lt;Projet&gt;, ni <dépôt>") + "\n" + str(str(restes))
        assert (a != b"" and b"\r" not in a and a.endswith(b"\n")), ("chef page (a) : UTF-8, fins \\n, jamais \\r") + "\n" + str(repr(a[-40:]))
        defaut = [p for p in (("name=\"D1\"", 2), ("name=\"Q1\"", 2)) if page.count(p[0]) != p[1]]
        assert (defaut == []), ("chef page (a) : D1 et Q1 portent leurs deux boutons") + "\n" + str(str(defaut))
        assert ("<li>Un <strong>point</strong> clé</li>" in page), ("chef page (a) : les puces d'en-tête passent par cellule_md") + "\n" + str(page[page.find("<header"):][:300])

        # (b) un texte échappé, une valeur sûre dans son attribut
        d = base(projet="P & Q", titre="T < U")
        d["choix"][0]["titre"] = "a < b & **c**"
        d["choix"][0]["options"].append(option('a"b'))
        code, s, pb = faire(d, "b.html")
        b = octets_de(pb).decode("utf-8")
        assert (code == 0 and "<h3>🟡 Q1 · a &lt; b &amp; <strong>c</strong></h3>" in b), ("chef page (b) : le titre de Q1 `a < b & **c**` échappé, gras rendu dans son <h3> — mutant : cellule_md ôté "
                 "du titre de question") + "\n" + str(s + b[b.find("<h3>🟡 Q1"):][:120])
        assert ("<title>P &amp; Q — T &lt; U</title>" in b and 'data-cle="P &amp; Q-2026-10-01-essai"' in b
                 and 'value="a&quot;b"' in b), ("chef page (b) : <title>, data-cle et value passent par esc seul, le guillemet d'une valeur devient &quot;") + "\n" + str(b[:200])

        # (c) un commentaire de tête qui cite des balises : la page ne change pas d'un octet
        citee = gabarit.replace("<!--\n", '<!--\n  Cite <div class="page" data-cle="x"> et <script> ici.\n', 1)
        assert (citee != gabarit and -1 < citee.find("<script>") < citee.find("-->")
                 and -1 < citee.find('<div class="page"') < citee.find("-->")), ("chef page (c) : prémisse, la copie cite ces balises dans son commentaire, avant les vraies") + "\n" + str(citee[:300])
        code, s, pc = faire(base(), "c.html", citee)
        assert (code == 0 and a != b"" and octets_de(pc) == a), ("chef page (c) : balise citée dans le commentaire de tête — sort 0, page identique à l'octet à celle de (a) "
                 "— mutant : morceaux cherchés dans le gabarit brut") + "\n" + str(s)

        # (d) une page sans style ne part pas
        sans_tete = re.sub(r"<link\b[^>]*>|<style\b.*?</style>", "", gabarit, flags=re.S | re.I)
        assert ("<style" not in sans_tete.lower() and "<link" not in sans_tete.lower()), ("chef page (d) : prémisse, la copie n'a ni <style> ni <link>") + "\n" + str(sans_tete[:200])
        code, s, pd = faire(base(), "d.html", sans_tete)
        assert (code == 1 and not os.path.exists(pd)
                 and s == 'GARDE: %s — aucun style (ni balise style, ni link rel="stylesheet")\n' % pd), ("chef page (d) : copie sans style ni link → GARDE aucun style, fichier absent, sort 1 — mutant : résultat "
                 "de defauts_page ignoré") + "\n" + str(s)

        # (e) ce qui ne se remplit pas : une GARDE chacun, rien d'écrit
        sans_carte = {k: v for k, v in base().items() if k not in ("decisions", "choix")}
        sans_effet = modifiee(lambda x: x["choix"][1]["options"][2].pop("effet"))
        for k, (nom, entree, attendu) in enumerate((
                ("aucune carte", sans_carte, "GARDE: aucune carte : ni « decisions », ni « choix »\n"),
                ("jauge Super", base(jauge="Super"),
                 "GARDE: jauge : « Super » n'est pas un de %s\n" % " · ".join(mod.JAUGE)),
                ("option sans effet", sans_effet,
                 "GARDE: choix[1].options[2] : « effet » manque, ou n'est pas un texte non vide\n"))):
            code, s, pe = faire(entree, "e%d.html" % k)
            assert (code == 1 and s == attendu and not os.path.exists(pe)), ("chef page (e) %s : GARDE, rien écrit, sort 1" % nom) + "\n" + str(s)

        # les autres GARDE, chacune seule : JSON, champs, gabarit, écriture
        occupe = os.path.join(tcp, "occupe")
        ecrire(occupe, "un fichier, pas un dossier\n")
        sans_script = gabarit.replace("<script>", "<scrip>")
        sans_reponses = gabarit.replace("<h2>Tes réponses</h2>", "<h2>Autre</h2>")
        autres = (
            ("JSON illisible", "pas du json", gabarit, "GARDE: JSON illisible"),
            ("JSON qui n'est pas un objet", "[1]", gabarit, "GARDE: le JSON n'est pas un objet\n"),
            ("@fichier absent", "@" + os.path.join(tcp, "absent.json"), gabarit, "GARDE: questions illisibles"),
            ("titre absent", modifiee(lambda x: x.pop("titre")), gabarit,
             "GARDE: racine : « titre » manque, ou n'est pas un texte non vide\n"),
            ("date invalide", base(date="demain"), gabarit, "GARDE: racine : « date » vaut AAAA-MM-JJ\n"),
            ("puces qui ne sont pas des textes", base(puces=[1]), gabarit,
             "GARDE: racine : « puces » doit être une liste de textes\n"),
            ("niveau inconnu", modifiee(lambda x: x["decisions"]["cartes"][0].update(niveau="fort")), gabarit,
             "GARDE: decisions.cartes[0] : « niveau » vaut faible ou moyen\n"),
            ("champ de carte absent", modifiee(lambda x: x["decisions"]["cartes"][0].pop("prix")), gabarit,
             "GARDE: decisions.cartes[0] : « prix » manque, ou n'est pas un texte non vide\n"),
            ("question à une option", base(choix=[{"titre": "Une ?", "options": [option("a")]}]), gabarit,
             "GARDE: choix[0] : 1 option(s), il en faut au moins deux\n"),
            ("valeur doublée", modifiee(lambda x: x["choix"][1]["options"][0].update(valeur="moyen")), gabarit,
             "GARDE: choix[1].options[1] : la valeur « moyen » est déjà prise\n"),
            ("deux recommandées", modifiee(lambda x: x["choix"][1]["options"][2].update(recommande=True)), gabarit,
             "GARDE: choix[1] : deux options recommandées\n"),
            ("recommande qui n'est pas un booléen",
             modifiee(lambda x: x["choix"][1]["options"][0].update(recommande="oui")), gabarit,
             "GARDE: choix[1].options[0] : « recommande » vaut true ou false\n"),
            ("genre de mal inconnu", base(mal=[{"genre": "grave", "titre": "x", "texte": "y"}]), gabarit,
             "GARDE: mal[0] : « genre » vaut erreur ou alerte\n"),
            ("gabarit sans <script>", base(), sans_script, "GARDE: gabarit : le <script> est introuvable\n"),
            ("gabarit sans « Tes réponses »", base(), sans_reponses,
             "GARDE: gabarit : la section « Tes réponses » est introuvable\n"))
        for k, (nom, entree, copie, attendu) in enumerate(autres):
            code, s, po = faire(entree, "g%d.html" % k, copie)
            assert (code == 1 and s.startswith(attendu) and s.count("GARDE:") == 1 and not os.path.exists(po)), ("chef page GARDE %s : une ligne, rien écrit, sort 1" % nom) + "\n" + str(s)
        code, s, po = faire(base(), os.path.join("occupe", "p.html"))
        assert (code == 1 and s.startswith("GARDE: %s — écriture impossible" % po) and s.count("GARDE:") == 1), ("chef page GARDE écriture impossible : le dossier de sortie est un fichier") + "\n" + str(s)

        # toutes les sections, dans l'ordre du gabarit, et les cinq mots de la jauge
        complet = base(jauge="Pas bon", plage="NUI1 à NUI3", pied="Fin du **rapport**.",
                       chiffres={"cases": [{"valeur": "3", "legende": "fiches"}, {"valeur": "1,2 $", "legende": "coût"}],
                                 "sources": ["`vlp.py cout`"]},
                       fait=[{"ref": "NUI1", "code": "abc1234", "titre": "Relever", "livre": "un fichier", "cout": "0,5 $"}],
                       mal=[{"genre": "erreur", "titre": "Un défaut", "texte": "à revoir"},
                            {"genre": "alerte", "titre": "Un doute", "texte": "à suivre"}],
                       fil=[{"heure": "19:22", "code": "NUI1", "texte": "fait"}])
        complet["decisions"]["intro"] = "Trois choix pris."
        code, s, pf = faire(complet, "complet.html")
        f = octets_de(pf).decode("utf-8")
        assert (code == 0 and s.endswith("CARTES D1 Q1 Q2\n")), ("chef page complet : sort 0, CARTES D1 Q1 Q2") + "\n" + str(s)
        titres = ["Les chiffres", "Ce qui a été fait", "Les décisions prises seul", "Les choix à trancher",
                  "Ce qui a mal tourné", "Le fil", "Tes réponses"]
        places = [f.find("<h2>%s" % t) for t in titres]
        assert (-1 not in places and places == sorted(places)), ("chef page complet : sept sections, dans l'ordre du gabarit") + "\n" + str(str(places))
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
        assert (code == 0 and s.startswith("PAGE SAINE")), ("chef page complet : vigile sur le fichier, PAGE SAINE") + "\n" + str(s)

        # la commande : le vrai gabarit sous KIT, le JSON par @fichier, la date du jour par défaut
        jq = os.path.join(tcp, "q.json")
        ecrire(jq, json.dumps(base(), ensure_ascii=False))
        sortie = os.path.join(tcp, "cmd.html")
        code, s = appel(["chef", "page", "--questions", "@" + jq, "--sortie", sortie])
        assert (code == 0 and s.endswith("CARTES D1 Q1 Q2\n") and a != b"" and octets_de(sortie) == a), ("chef page par la commande : sort 0, page identique à l'octet à celle de (a)") + "\n" + str(s)
        sans_date = {k: v for k, v in base().items() if k != "date"}
        code, s, pj = faire(sans_date, "jour.html")
        m = re.search(r'data-cle="Demo-(\d{4}-\d\d-\d\d)-essai"', octets_de(pj).decode("utf-8"))
        assert (code == 0 and m is not None and datetime.date.fromisoformat(m.group(1)) <= datetime.date.today()), ("chef page : sans date, le jour — AAAA-MM-JJ lu dans data-cle") + "\n" + str(s)


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
        assert (code == 0 and all("PRÊT %s" % c in lignes for c in ("AAA", "BBB", "CCC", "JJJ", "III"))), ("NUI10 : trier sort 0, PRÊT pour AAA, BBB, CCC (dépend d'un code prêt), JJJ (dépend d'un rang prêt), III") + "\n" + str(s)
        assert ("FICHIERS AAA scripts/vlp.py" in lignes and "FICHIERS BBB vlp.py" in lignes
                 and "FICHIERS HHH dossier x/m.py" in lignes), ("NUI10 : FICHIERS — `vlp.py archive` donne vlp.py, un chemin à espace reste entier") + "\n" + str(s)
        assert (len(canal) == 3 and canal[0].startswith("CANAL 1 : AAA, BBB, CCC, JJJ — ")
                 and "fichier vlp.py : AAA, BBB" in canal[0] and "CCC dépend de AAA" in canal[0]), ("NUI10 : un CANAL groupe AAA, BBB, CCC, JJJ et nomme vlp.py et la dépendance — mutant : chemin entier") + "\n" + str(canal)
        assert ("CANAL 2 : HHH — inconnu → à la page" in canal and "CANAL 3 : III — inconnu → à la page" in canal), ("NUI10 : une prête sans lien — inconnu → à la page") + "\n" + str(canal)
        assert (any(l.startswith("ÉCARTÉE DDD") for l in lignes)
                 and "MARQUES DDD 5 : 🟡 1 · à trancher 1 · non mesuré 1 · %s 1 · push 1" % mod.MARQUE_VISUELLE in lignes), ("NUI10 : DDD porte les cinq marques, la visuelle en cellule 3 — ÉCARTÉE, MARQUES à 5 — mutant : cellule 3 retirée") + "\n" + str(s)
        assert (any(l.startswith("ÉCARTÉE FFF") for l in lignes) and any(l.startswith("ÉCARTÉE GGG") for l in lignes)), ("NUI10 : push en cellule 4 écarte FFF ; dépendance absente écarte GGG") + "\n" + str(s)
        assert (any(l.startswith("SOIR HHH") for l in lignes) and not any(l.startswith("SOIR III") for l in lignes)), ("NUI10 : SOIR pour HHH (~6 fiches), pas pour III (~½ fiche)") + "\n" + str(s)
        assert (io.open(etat, encoding="utf-8").read() == "# État\n\n" + entete + lignes_todo + "\n## Journal\n"), ("NUI10 : trier n'écrit rien — le fichier d'état reste tel quel") + "\n" + ""
        ecrire(etat, "# État\n\n" + entete + "| 1 | `AAA` — a | `sed x | sha256sum` | 2 fiches | — |\n\n## Journal\n")
        code, s = appel(["trier", tp])
        assert (code == 1 and s.startswith("GARDE: ligne 1 de la TODO")), ("NUI10 : une barre non échappée — GARDE, sort 1") + "\n" + str(s)


def test_trier_branche(tmp_path):
    """BRA1 : dans Git, `trier` ne trie que sur `main` ; ailleurs, une seule ligne `GARDE:`, sort 1."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n")
        ecrire(os.path.join(tb, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `AAA` — a | x | 1 fiche | — |\n\n## Journal\n")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tb, capture_output=True)
        code_main, s_main = appel(["trier", tb])
        subprocess.run(["git", "switch", "-q", "-c", "nuit/x"], cwd=tb, capture_output=True)
        code, s = appel(["trier", tb])
        assert (code_main == 0 and code == 1 and len(s.splitlines()) == 1 and s.startswith("GARDE: trier hors de main")), ("BRA1 : trier sort 0 sur main, 1 sur nuit/x — une seule ligne, GARDE: trier hors de main") + "\n" + str("%s\n%s" % (s_main, s))


def test_fichier_nuits(tmp_path):
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    carte = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **artefact du chantier** : aucun\n\n"
             "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
    indice = ("# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
              "| `100-x.md` | un chantier |\n\nFin.\n")
    rang = ('          <tr>\n            <td>x</td>\n            <td class="mono">%s</td><td class="mono">2026-01-01</td>\n'
            '            <td class="mono">%s</td>\n            <td>y</td>\n          </tr>\n')
    lecon = "- 2026-09-26 · N=%d · %s · jouées 3 sur 5 · nuits 2026-09-25 · sessions s1"
    env = os.environ.get("CLAUDE_CODE_SESSION_ID")
    os.environ["CLAUDE_CODE_SESSION_ID"] = ""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tp, check=True, capture_output=True)
        ecrire(os.path.join(tp, "CHANTIER.md"), carte)
        ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), indice)
        ecrire(os.path.join(tp, "ctx", "08-etat.md"), "# État\n\n" + entete + "| 1 | `AAA` — a | x | 1 fiche | — |\n\n## Journal\n")
        ecrire(os.path.join(tp, "ctx", "100-x.md"), "# x\n")
        lire_idx = lambda: io.open(os.path.join(tp, "ctx", "00-INDEX.md"), encoding="utf-8").read()
        # (a) création : le numéro suivant le plus grand, la ligne sous le plus grand numéro lu en entier
        _, s0 = appel(["trier", tp])
        chemin = mod.fichier_nuits(tp, True)
        idx = lire_idx().splitlines()
        avant = lire_idx()
        assert (chemin == os.path.join(tp, "ctx", "101-nuits.md") and os.path.isfile(chemin)
                 and idx[idx.index("| `100-x.md` | un chantier |") + 1].startswith("| `101-nuits.md` |")
                 and "**clos**" not in avant and "**ouvert**" not in avant and "NUITS absent" in s0), ("NUI11 (a) : 00, 08, 100 → 101-nuits.md, sa ligne d'index juste sous celle de 100 ; trier sans fichier le dit") + "\n" + str((chemin, idx, s0))
        assert (mod.fichier_nuits(tp, True) == chemin and lire_idx() == avant
                 and appel(["archiver", tp])[1].startswith("ARCHIVÉ 0 ") and lire_idx() == avant), ("NUI11 (a) : relancé, même chemin, index inchangé ; archiver ne la déplace pas") + "\n" + str(lire_idx())
        # (b) écrire, retirer, indice, plafond, forme
        ligne_t = "| 2026-09-25 | A | NUI | 3/2/1 | 4,50 |"
        premiere, seconde = mod.nuits_ecrire(chemin, ligne_t), mod.nuits_ecrire(chemin, ligne_t)
        l2 = lecon % (2, "cause un")
        mod.nuits_ecrire(chemin, l2)
        mod.nuits_ecrire(chemin, l2)
        lu = io.open(chemin, encoding="utf-8").read()
        assert (premiere is True and seconde is False and lu.count(ligne_t) == 1 and lu.count(l2) == 1
                 and lu.index(ligne_t) < lu.index("## Leçons") < lu.index(l2)), ("NUI11 (b) : nuits_ecrire deux fois → une ligne de table, une leçon") + "\n" + str(lu)
        code, s = appel(["trier", tp])
        assert (code == 0 and "--- Leçons : ctx/101-nuits.md (lignes " in s and l2 + " — indice" in s.splitlines()), ("NUI11 (b) : N=2 → la leçon porte « indice », sous --- Leçons ---, sort 0") + "\n" + str(s)
        retiree = mod.nuits_retirer(chemin, l2, "2026-09-27", "NUI12")
        encore = mod.nuits_retirer(chemin, l2, "2026-09-27", "NUI12")
        code, s = appel(["trier", tp])
        assert (retiree is True and encore is False
                 and l2 + " — retirée le 2026-09-27 par NUI12" in s.splitlines() and " — indice" not in s and code == 0), ("NUI11 (b) : nuits_retirer → suffixe, leçon gardée, plus d'indice, rien la seconde fois") + "\n" + str(s)
        for k in range(12):
            mod.nuits_ecrire(chemin, lecon % (3, "cause %d" % k))
        code, s = appel(["trier", tp])
        assert (code == 0 and "GARDE" not in s), ("NUI11 (b) : 12 vivantes + 1 retirée → pas de GARDE — mutant : retirées comptées vivantes") + "\n" + str(s)
        mod.nuits_ecrire(chemin, lecon % (3, "cause 12"))
        code, s = appel(["trier", tp])
        assert (code == 1 and "GARDE: 13 leçons vivantes" in s and "TRI 1 rangs" in s), ("NUI11 (b) : 13 vivantes → GARDE:, tri imprimé, sort 1") + "\n" + str(s)
        ecrire(chemin, io.open(chemin, encoding="utf-8").read().replace(lecon % (3, "cause 12") + "\n", "- pas une forme\n"))
        code, s = appel(["trier", tp])
        assert (code == 1 and "GARDE: leçon hors forme" in s and "- pas une forme" in s and "TRI 1 rangs" in s), ("NUI11 (b) : une leçon hors forme → GARDE: qui la cite, tri imprimé, sort 1") + "\n" + str(s)
        ecrire(chemin, io.open(chemin, encoding="utf-8").read().replace("- pas une forme\n", ""))
        # (d) une ligne de table à 6 cellules
        try:
            mod.nuits_du_fichier(mod.NUITS_TETE[:6] + ["| a | b | c | d | e | f |"] + mod.NUITS_TETE[6:])
            dit = "aucune erreur"
        except ValueError as e:
            dit = str(e)
        assert ("ligne 7 de la table des nuits : 6 cellules au lieu de 5" in dit), ("NUI11 (d) : une ligne de table à 6 cellules lève une ValueError qui la nomme") + "\n" + str(dit)
        # (c) TAUX nuit : carnets du dépôt, médiane des fiches acceptées
        c1, c2 = mod.carnet.du_jour(tp, "2026-09-25"), mod.carnet.du_jour(tp, "2026-09-26")

        def fiche(c, nuit, code, lignes, refus=None):
            for role, usd_kit, usd_cli in lignes:
                mod.carnet.ajouter(c, nuit=nuit, canal="A", chantier="NUI", role=role, fiche=code, usd_kit=usd_kit,
                                   usd_cli=usd_cli, refus_n=refus if role == "relire" else None)

        fiche(c1, "2026-09-25", "N1", [("jouer", 0.5, 99), ("relire", 0.5, 99)])
        fiche(c1, "2026-09-25", "N2", [("jouer", 0.5, 99), ("relire", 1.5, 99)])
        fiche(c2, "2026-09-26", "N3", [("jouer", 0.5, 99), ("relance", 1.0, 99), ("relire", 1.5, 99)])
        fiche(c2, "2026-09-26", "N4", [("jouer", 0.5, 99), ("relire", 3.5, 99)])
        code, s = appel(["trier", tp])
        assert ("TAUX nuit indice — 4 fiches acceptées" in s.splitlines()), ("NUI11 (c) : 4 fiches acceptées → indice, sans chiffre — mutant : CARNET_MIN = 0") + "\n" + str(s)
        fiche(c2, "2026-09-26", "N5", [("jouer", 0.5, 99), ("relire", 9.5, 99)])
        fiche(c2, "2026-09-26", "R1", [("jouer", 100, 99), ("relire", 50, 99)], refus=1)
        fiche(c2, "2026-09-26", "R1", [("relance", 40, 99), ("relire", 50, 99)], refus=2)
        mod.carnet.ajouter(c1, nuit="2026-09-25", canal="A", chantier="NUI", role="relance", fiche="N1", usd_kit=None, usd_cli=99)
        code, s = appel(["trier", tp])
        assert ("TAUX nuit médiane 3 $/fiche sur 5 fiches acceptées · sans usd_kit 1" in s.splitlines()), ("NUI11 (c) : 5 fiches (1, 2, 3, 4, 10), une refusée deux fois hors compte, une ligne sans usd_kit"
                 " → médiane 3 — mutant : usd_kit lu en usd_cli") + "\n" + str(s)
        # TAUX jour : le prix par fiche de l'estimé d'`ouvrir`, sur la même feuille
        ecrire(os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)")
               + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)") + rang % ("D1–D2", "≈2,0M (2 000 000)")
               + rang % ("E1–E8", "non recompté — fichier introuvable · non mesurable") + "</tbody>\n")
        _, s = appel(["trier", tp])
        ecrire(os.path.join(tp, "ctx", "30-q.md"), "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n")
        appel(["ouvrir", tp, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        estime = re.search(r"— (≈[\d,]+ \$/fiche sur \d+ clos) \(le", io.open(os.path.join(tp, "ctx", "30-q.md"), encoding="utf-8").read())
        assert (estime is not None and estime.group(1) == "≈1,00 $/fiche sur 3 clos"
                 and "TAUX jour " + estime.group(1) in s.splitlines()), ("NUI11 (c) : TAUX jour = le prix par fiche de l'estimé d'ouvrir sur la même feuille (≈1,00 $/fiche sur 3 clos)") + "\n" + str((s, estime))
    if env is None:
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    else:
        os.environ["CLAUDE_CODE_SESSION_ID"] = env


def test_plan(tmp_path):
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    carte = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **artefact du chantier** : aucun\n\n"
             "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")
    indice = ("# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
              "| `100-x.md` | un chantier |\n\nFin.\n")
    todo = ("# État\n\n" + entete + "| 1 | `AAA` — a | x | 1 fiche | — |\n| 2 | `BBB` — b | x | 1 fiche | — |\n"
            "| 3 | `CCC` — c | x | 1 fiche | — |\n\n## Journal\n")
    env = os.environ.get("VLP_NUIT")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"), carte)
        ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), indice)
        ecrire(os.path.join(tp, "ctx", "08-etat.md"), todo)
        ecrire(os.path.join(tp, "ctx", "100-x.md"), "# x\n")
        nuits, index = os.path.join(tp, "ctx", "101-nuits.md"), os.path.join(tp, "ctx", "00-INDEX.md")

        def octets():
            with open(index, "rb") as fi:
                return (open(nuits, "rb").read() if os.path.isfile(nuits) else None), fi.read()

        def texte():
            with open(nuits, "rb") as fn:
                return fn.read().decode("utf-8")

        def plan(nom, **corps):
            chemin = os.path.join(tp, nom + ".json")
            ecrire(chemin, json.dumps(corps))
            return chemin

        def ch(code, prefixe, *reponses):
            return {"code": code, "prefixe": prefixe, "reponses": list(reponses)}

        def ecrire_plan(f, date):
            return appel(["plan", "ecrire", tp, "--json", f, "--date", date])

        def lire_plan(*options):
            return appel(["plan", "lire", tp, *options])

        # (0) sans fichier des nuits : lire refuse ; ecrire le crée, sa ligne d'index comprise
        code, s = lire_plan("--date", "2026-09-25")
        assert (code == 1 and s.startswith("GARDE: pas de fichier des nuits") and not os.path.isfile(nuits)), ("NUI12 (0) : plan lire sans fichier des nuits → GARDE:, sort 1") + "\n" + str(s)
        code, s = ecrire_plan(plan("passee", borne_usd=3, borne_chantiers=1, A=[ch("AAA", "AAA", "ancienne")]), "2026-09-25")
        assert (code == 0 and s.startswith("PLAN ctx/101-nuits.md · 2026-09-25 · 1 chantiers") and os.path.isfile(nuits)
                 and "| `101-nuits.md` |" in octets()[1].decode("utf-8")), ("NUI12 (0) : plan ecrire crée 101-nuits.md et sa ligne d'index, sort 0") + "\n" + str(s)
        mod.nuits_ecrire(nuits, "| 2026-09-24 | A | NUI | 3/2/1 | 4,50 |")
        mod.nuits_ecrire(nuits, "- 2026-09-24 · N=3 · cause un · jouées 3 sur 5 · nuits 2026-09-24 · sessions s1")
        # (a) A = deux chantiers, B = un : lire par canal, dans l'ordre, aussi sous VLP_NUIT=1
        code, s = ecrire_plan(plan("soir", borne_usd=12.5, borne_chantiers=3,
                                   A=[ch("AAA", "AAA", "r1a", "r1b é"), ch("BBB", "BBB", "r2")], B=[ch("CCC", "CCC", "r3")]),
                              "2026-09-30")
        os.environ["VLP_NUIT"] = "1"
        code_a, s_a = lire_plan("--date", "2026-09-30", "--canal", "A")
        code_b, s_b = lire_plan("--date", "2026-09-30", "--canal", "B")
        code_c, s_c = lire_plan("--date", "2026-09-30", "--canal", "A", "--chantier", "BBB")
        del os.environ["VLP_NUIT"]
        lignes_a = [l for l in s_a.splitlines() if l.startswith("CHANTIER ")]
        assert (code == 0 and code_a == 0 and s_a.startswith("BORNE 12.5 $ · 3 chantiers\n")
                 and lignes_a == ["CHANTIER AAA · canal A · rang 1 · préfixe AAA", "CHANTIER BBB · canal A · rang 2 · préfixe BBB"]), ("NUI12 (a) : lire --canal A sous VLP_NUIT=1 → sort 0, la borne, 2 chantiers dans l'ordre") + "\n" + str(s_a)
        assert (code_b == 0 and [l for l in s_b.splitlines() if l.startswith("CHANTIER ")]
                 == ["CHANTIER CCC · canal B · rang 1 · préfixe CCC"]), ("NUI12 (a) : lire --canal B → son seul chantier") + "\n" + str(s_b)
        assert (code_c == 0 and "- r2" in s_c.splitlines() and "r1a" not in s_c and "### AAA" not in s_c), ("NUI12 (a) : lire --chantier BBB → ses réponses, aucune de AAA") + "\n" + str(s_c)
        assert ("- r1b é" in lire_plan("--date", "2026-09-30", "--chantier", "AAA")[1].splitlines()), ("NUI12 (a) : la réponse en é revient telle quelle, en puce") + "\n" + ""
        code, s = lire_plan("--date", "2026-09-29")
        assert (code == 1 and s.startswith("GARDE: pas de plan à la date 2026-09-29")
                 and lire_plan()[0] == 1), ("NUI12 (a) : une date sans plan → GARDE:, sort 1; sans --date → GARDE:") + "\n" + str(s)
        avant = texte()
        assert (avant.count("## Nuit 2026-09-25") == 1 and avant.index("## Nuit 2026-09-25")
                 < avant.index("## Nuit 2026-09-30") < avant.index("## Leçons")), ("NUI12 (a) : la nuit passée reste, la nouvelle se pose avant ## Leçons") + "\n" + str(avant)
        # (b) réécrit à la même date : une seule section, le reste octet pour octet
        code, s = ecrire_plan(plan("soir2", borne_usd=7, borne_chantiers=2, A=[ch("AAA", "AAA", "neuf")]), "2026-09-30")
        apres = texte()
        assert (code == 0 and apres.count("## Nuit 2026-09-30") == 1 and "- neuf" in apres and "r1a" not in apres
                 and apres.index("## Nuit 2026-09-30") < apres.index("## Leçons")), ("NUI12 (b) : même date → une seule `## Nuit`, remplacée, avant ## Leçons — mutant : autres sections perdues") + "\n" + str(apres)
        assert (apres[:apres.index("## Nuit 2026-09-30")] == avant[:avant.index("## Nuit 2026-09-30")]
                 and apres[apres.index("## Leçons"):] == avant[avant.index("## Leçons"):]), ("NUI12 (b) : la nuit passée, la table et ## Leçons identiques octet pour octet") + "\n" + str(apres)
        # (c) neuf refus : GARDE:, sort 1, ni le fichier des nuits ni l'index ne bougent
        refus = [
            ("code absent de la TODO", plan("r1", borne_usd=1, borne_chantiers=1, A=[ch("ZZZ", "ZZZ")])),
            ("préfixe NUIT (quatre lettres)", plan("r2", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "NUIT")])),
            ("préfixe déjà pris (E)", plan("r3", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "E")])),
            ("préfixe donné deux fois", plan("r4", borne_usd=1, borne_chantiers=2, A=[ch("AAA", "XXX")], B=[ch("BBB", "XXX")])),
            ("chantier dans deux canaux", plan("r5", borne_usd=1, borne_chantiers=2, A=[ch("AAA", "XXX")], B=[ch("AAA", "YYY")])),
            ("canal C", plan("r6", borne_usd=1, borne_chantiers=1, C=[ch("AAA", "XXX")])),
            ("JSON sans borne", plan("r7", A=[ch("AAA", "XXX")])),
            ("réponse à saut de ligne", plan("r8", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "XXX", "a\nb")])),
        ]
        for nom, f in refus:
            fichier_avant = octets()
            code, s = ecrire_plan(f, "2026-10-01")
            assert (code == 1 and s.startswith("GARDE: ") and octets() == fichier_avant), ("NUI12 (c) : %s → GARDE:, sort 1, rien d'écrit — mutant : contrôle des lettres prises retiré" % nom) + "\n" + str(s)
        valide = plan("r9", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "XXX")])
        fichier_avant = octets()
        os.environ["VLP_NUIT"] = "1"
        code, s = ecrire_plan(valide, "2026-10-01")
        del os.environ["VLP_NUIT"]
        assert (code == 1 and s.startswith("GARDE: VLP_NUIT=1") and octets() == fichier_avant), ("NUI12 (c) : VLP_NUIT=1 → plan ecrire refuse (GARDE:, sort 1, rien d'écrit)") + "\n" + str(s)
        code, s = ecrire_plan(valide, "2026-10-01")
        assert (code == 0), ("NUI12 (c) : le même plan, sans VLP_NUIT → écrit (le refus venait bien de la variable)") + "\n" + str(s)
        # (d) carte : NUIT=1 une fois, dans le bloc d'avant les fiches ; rien sinon
        projet = os.path.join(tp, "proj")
        ecrire(os.path.join(projet, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
        ecrire(os.path.join(projet, "context AI", "20-z.md"), FICHES)

        def carte_sous(valeur, relecteur=False):
            if valeur is None:
                os.environ.pop("VLP_NUIT", None)
            else:
                os.environ["VLP_NUIT"] = valeur
            sortie = io.StringIO()
            mod.carte(projet, sortie, relecteur)
            os.environ.pop("VLP_NUIT", None)
            return sortie.getvalue().splitlines()

        nuit = carte_sous("1")
        assert (nuit.count("NUIT=1") == 1 and nuit.index("--- CHANTIER.md ---") < nuit.index("NUIT=1")
                 < next(k for k, l in enumerate(nuit) if l.startswith("--- fiches :"))), ("NUI12 (d) : carte sous VLP_NUIT=1 → NUIT=1 une fois, après --- CHANTIER.md --- et avant --- fiches : — mutant : ligne jamais écrite") + "\n" + str(nuit)
        assert (not any(l.startswith("NUIT=") for l in carte_sous("1", True) + carte_sous("0") + carte_sous(None))), ("NUI12 (d) : --relecteur, VLP_NUIT=0 et variable absente → aucune ligne NUIT=") + "\n" + ""
    if env is not None:
        os.environ["VLP_NUIT"] = env


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


def test_joints(tmp_path):
    """Les aides vivent ici, pas au niveau du module : celui-ci est déjà au seuil de
    complexité de pyright (« Code is too complex to analyze », mesuré sur BTN1)."""
    META_BTN1 = '<meta charset="utf-8">'
    SCRIPT_BTN1 = '<script src="vlp.js"></script>'

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
                        and io.open(c, "rb").read() == io.open(os.path.join(ICI, "..", "templates", n), "rb").read()
                        for n, c in files.items()))

    def balises_une_fois(html):
        """(b) : le charset une fois, en première ligne ; le script une fois, en dernière."""
        lignes = html.rstrip("\n").split("\n")
        return (html.count(META_BTN1) == 1 and html.count(SCRIPT_BTN1) == 1
                and lignes[0] == META_BTN1 and lignes[-1] == SCRIPT_BTN1)

    def sans_balises(html):
        return html.replace(META_BTN1 + "\n", "").replace(SCRIPT_BTN1 + "\n", "")

    def projet_btn1(tab):
        """Un projet équipé minimal, sa feuille posée depuis le gabarit (comme PLI2)."""
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
        return proj, fdr

    # (c) d'abord : une page d'avant, sans charset ni script, les reçoit une fois ; une seconde
    # régénération n'en ajoute pas — page du chantier, puis feuille de route.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        ecrire(fiches, FICHES_PLI2)
        appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        ecrire(page, sans_balises(lire(page)))
        assert ("<meta charset" not in lire(page) and "vlp.js" not in lire(page)), ("BTN1 : (c) la page d'avant n'a ni charset ni script") + "\n" + str(lire(page)[:300])
        code, s = appel(["page", fiches, page])
        assert (code == 0 and balises_une_fois(lire(page))), ("BTN1 : (c) page d'avant régénérée — charset et script reçus une fois chacun") + "\n" + str(s + lire(page)[:300])
        code, s = appel(["page", fiches, page])
        assert (code == 0 and balises_une_fois(lire(page))), ("BTN1 : (c) régénérée deux fois, rien de plus — mutant : la balise posée sans vérifier sa présence") + "\n" + str(lire(page)[:300] + lire(page)[-300:])
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn1(tab)
        ecrire(fdr, sans_balises(lire(fdr)))
        code, s = appel(["feuille", proj])
        assert (code == 0 and balises_une_fois(lire(fdr))), ("BTN1 : (c) feuille d'avant régénérée — charset et script reçus une fois chacun") + "\n" + str(s + lire(fdr)[:300])
        code, s = appel(["feuille", proj])
        assert (code == 0 and balises_une_fois(lire(fdr))), ("BTN1 : (c) feuille régénérée deux fois, rien de plus") + "\n" + str(lire(fdr)[:300] + lire(fdr)[-300:])
    # Un charset cité dans un commentaire n'est pas un charset posé.
    cite = mod.migrer_joints("<!-- %s -->\n<p>x</p>\n" % META_BTN1)
    assert (cite.startswith(META_BTN1 + "\n") and cite.count(META_BTN1) == 2), ("BTN1 : (c) charset cité en commentaire — le vrai est posé quand même") + "\n" + str(cite)

    # (a) et (b) : `page --creer`, puis `page` sans --creer ; vlp.js modifié à la main entre deux.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        art = os.path.join(tab, "artefacts")
        page = os.path.join(art, "p.html")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert (code == 0 and joints_recopies(s, art) and "CSS %s\n" % os.path.join(art, "vlp.css") in s), ("BTN1 : (a) page --creer recopie vlp.css et vlp.js à l'octet, FILES les nomme"
                 " — mutant : vlp.js retiré de recopier_joints") + "\n" + str(s)
        assert (balises_une_fois(lire(page))), ("BTN1 : (b) page --creer — charset et script une fois chacun") + "\n" + str(lire(page)[:300])
        with open(os.path.join(art, "vlp.js"), "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        assert (code == 0 and joints_recopies(s, art)), ("BTN1 : (a) page (régénération) remet vlp.js à l'octet, FILES les nomme") + "\n" + str(s)
        assert (balises_une_fois(lire(page))), ("BTN1 : (b) page régénérée — charset et script une fois chacun") + "\n" + str(lire(page)[:300])
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn1(tab)
        art = os.path.dirname(fdr)
        code, s = appel(["feuille", proj])
        assert (code == 0 and joints_recopies(s, art) and "CSS %s\n" % os.path.join(art, "vlp.css") in s), ("BTN1 : (a) feuille recopie vlp.css et vlp.js à l'octet, FILES les nomme") + "\n" + str(s)
        assert (balises_une_fois(lire(fdr))), ("BTN1 : (b) feuille régénérée — charset et script une fois chacun") + "\n" + str(lire(fdr)[:300])

    # `joints <dossier>` : les deux copies, et la ligne FILES seule ; un dossier absent est gardé.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        code, s = appel(["joints", tab])
        assert (code == 0 and joints_recopies(s, tab) and len(s.splitlines()) == 1), ("BTN1 : joints recopie les deux joints et n'écrit que la ligne FILES") + "\n" + str(s)
        code, s = appel(["joints", os.path.join(tab, "absent")])
        assert (code == 1 and s.startswith("GARDE: dossier introuvable")), ("BTN1 : joints sur un dossier absent — GARDE, sort 1") + "\n" + str(s)

    # Les deux gabarits : charset en première ligne, script en dernière, une fois chacun.
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = io.open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
        assert (balises_une_fois(gabarit)), ("BTN1 : (b) gabarit %s — charset et script une fois chacun" % nom) + "\n" + str(gabarit[:300])
        # Dette BTN : /vlp:init publie la feuille remplie à la main, sans `feuille` — un lien local vers
        # autre chose qu'un joint y reste sans fichier (l'image couts.svg y restait, cassée).
        locaux = set(re.findall(r'(?:src|href)="(?!https?:|#|&lt;)([^"]+)"', gabarit))
        assert (locaux <= set(mod.JOINTS)), ("Dette BTN : gabarit %s — ne lie en local que les joints — mutant : image couts.svg remise"
                 % nom) + "\n" + str(str(sorted(locaux)))

    # --- BTN5 : le coût des chantiers clos en image, `couts.svg` et sa balise — imbriqué ici : le
    # module est au seuil de complexité de pyright (BTN1), et couts.svg est un joint de plus.
    IMG = '<img src="couts.svg"'

    def projet_btn5(tab, rangs):
        """Un projet équipé minimal, sa feuille posée depuis le gabarit, `rangs` en tête de ZONE:clos."""
        proj = os.path.join(tab, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               ""
               "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"),
               "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                          encoding="utf-8").read()
        i = gabarit.index("<tbody>\n", gabarit.index("<!-- ZONE:clos")) + len("<tbody>\n")
        ecrire(fdr, gabarit[:i] + "".join(rangs) + gabarit[i:])
        return proj, fdr

    def rang(nom, cout):
        return ligne_close(cout).replace("<td>Test ", "<td>%s " % nom)

    def barres(chemin):
        """[(x, hauteur)] des barres de `couts.svg`, de gauche à droite ; [] sans fichier."""
        if not os.path.isfile(chemin):
            return []
        return sorted((float(x), float(h)) for x, h in re.findall(
            r'<rect class="barre" x="([\d.]+)" y="[\d.]+" width="[\d.]+" height="([\d.]+)"', lire(chemin)))

    # Quatre lignes closes, la plus récente en haut : D 4 000, C sans coût, B 2 000, A 1 000.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang("D", mod.arrondi(4000)), rang("C", "non mesuré"),
                                      rang("B", mod.arrondi(2000)), rang("A", mod.arrondi(1000))])
        svg = os.path.join(os.path.dirname(fdr), "couts.svg")
        code, s = appel(["feuille", proj])
        b = barres(svg)
        h = [x[1] for x in b]
        assert (code == 0 and len(b) == 3), ("BTN5 : 4 lignes closes, une sans coût — couts.svg a 3 barres") + "\n" + str(s + str(b))
        r = sorted(h)
        assert (abs(2 * r[0] - r[1]) <= 1 and abs(4 * r[0] - r[2]) <= 1), ("BTN5 : hauteurs dans le rapport 1 : 2 : 4, à 1 px près — mutant : hauteur constante") + "\n" + str(str(b))
        assert (b[-1][1] == max(h) and b[0][1] == min(h)), ("BTN5 : la plus récente (la plus chère) à droite, la plus ancienne à gauche"
                 " — mutant : ordre non retourné") + "\n" + str(str(b))
        dessin = lire(svg)
        formes = re.findall(r"<(?:rect|text)\b[^>]*>", dessin)
        assert ("%s tokens</text>" % mod.arrondi(4000) in dessin and formes
                 and all('fill="#' in f for f in formes)), ("BTN5 : le maximum en haut à gauche (arrondi + « tokens »), chaque forme a son fill") + "\n" + str(dessin)
        files = files_de(s) or {}
        assert ("couts.svg" in files and "\\" not in files["couts.svg"]
                 and os.path.samefile(files["couts.svg"], svg)), ("BTN5 : FILES nomme couts.svg, à côté de la feuille") + "\n" + str(s)
        assert ("\nLIRE vlp.css vlp.js couts.svg\n" in s), ("REF29 : feuille dit LIRE avec couts.svg joint — mutant : ligne LIRE retirée") + "\n" + str(s)
        html = lire(fdr)
        alt = re.search(r'<img src="couts\.svg" alt="([^"]*)"', html)
        assert (html.count(IMG) == 1 and html.index(IMG) < html.index('<details class="clos">')
                 and alt is not None and "3 barres" in alt.group(1) and alt.group(1).endswith("le plus cher : D")), ("BTN5 : la balise <img> une fois, avant details.clos ; alt : 3 barres, D le plus cher") + "\n" + str(html[-3000:])
        donnees = re.search(r'<img src="couts\.svg"[^>]* data-couts="([^"]*)">', html)
        donnees = json.loads(mod.html.unescape(donnees.group(1))) if donnees else {}
        assert (donnees == {"couleur": mod.COUTS_BARRE, "barres": [[n, t, mod.arrondi(t)] for n, t in
                             (("A", 1000), ("B", 2000), ("D", 4000))]}), ("Graphique : data-couts porte la couleur et les barres [chantier, tokens, arrondi],"
                 " de la plus ancienne à la plus récente — mutant : attribut retiré") + "\n" + str(str(donnees))
        # CTR1 : l'image recopie `--cours` et `--doux` de vlp.css, lisibles à 4,5:1 sur les deux fonds.
        css, rapports = contrastes_couts(mod.COUTS_BARRE, mod.COUTS_TEXTE)
        assert (mod.COUTS_BARRE == css.get("--cours") and mod.COUTS_TEXTE == css.get("--doux")
                 and min(rapports) >= 4.5), ("Graphique : couleurs de couts.svg = --cours et --doux de vlp.css, contraste ≥ 4,5"
                 " sur --surface et --ground — mutant : ancienne couleur des barres") + "\n" + str("rapports %s · css %s" % (
                     " ".join("%.2f" % r for r in rapports), css))
        print("  CTR1 contrastes (barre/surface, barre/ground, texte/surface, texte/ground) : %s"
              % " ".join("%.2f" % r for r in rapports))
        ecrire(fdr, mod.BALISE_COUTS.sub("", html))
        appel(["feuille", proj])
        assert (lire(fdr).count(IMG) == 1), ("BTN5 : une feuille d'avant, sans balise, la reçoit à sa régénération") + "\n" + str(lire(fdr)[-3000:])
        appel(["feuille", proj])
        assert (lire(fdr).count(IMG) == 1 and lire(svg) == dessin), ("BTN5 : régénérée encore, toujours une balise, même dessin") + "\n" + str(lire(fdr)[-3000:])

    # Sans coût (les lignes d'exemple du gabarit seules) : ni fichier — un ancien est retiré —, ni balise.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang("C", "non mesuré")])
        svg = os.path.join(os.path.dirname(fdr), "couts.svg")
        ecrire(svg, "<svg/>")
        code, s = appel(["feuille", proj])
        assert (code == 0 and not os.path.exists(svg) and IMG not in lire(fdr)
                 and "couts.svg" not in (files_de(s) or {})), ("BTN5 : une feuille sans coût n'a ni couts.svg, ni balise, ni entrée FILES") + "\n" + str(s + lire(fdr)[-2000:])
        assert ("\nLIRE vlp.css vlp.js\n" in s), ("REF29 : feuille sans couts.svg dit LIRE sans lui") + "\n" + str(s)

    # Des coûts mesurés, tous à 0 (dette BTN) : rien à dessiner, et pas de division par un maximum nul.
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang("B", mod.arrondi(0)), rang("A", mod.arrondi(0))])
        code, s = appel(["feuille", proj])
        assert (code == 0 and not os.path.exists(os.path.join(os.path.dirname(fdr), "couts.svg"))
                 and IMG not in lire(fdr)), ("Dette BTN : coûts clos tous à 0 — feuille passe, sans couts.svg ni balise"
                 " — mutant : garde de couts_clos retirée") + "\n" + str(s)
