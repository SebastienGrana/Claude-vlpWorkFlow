"""`noyau/ordre.py` : la page d'enchaînement entre projets, son classement, sa base, sa clôture, sa jonction — migré de
l'ancienne suite maison (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

from aides import SCRIPTS, appel, ecrire, lire, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


ORDRE_SOURCE = """# L'ordre

## Les projets

| Clé | Dossier |
|---|---|
| k | `.` |
| a | `autre` |
| x | `absent` |

## La cible

| Projet | Codes |
|---|---|
| a | `A1` |

## Le chemin conseillé

| Pas | Projet | Nom | Coût |
|---|---|---|---|
| `K9` | k | fait avant | ✅ fait le 2026-10-01 |
| `K1` | k | | une note |
| `A1` | a | | |
| `A2` | a | une fiche | 1 fiche |
| `X1` | x | | |

## Les niveaux forcés

| Pas | Niveau | Pourquoi |
|---|---|---|
| `K9` | conseillé | fait |
| `A2` | à la marge | sans phase |
"""


def test_ordre(tmp_path, init_git):
    """ORD1 : `vlp.py ordre --json` sur deux projets bâtis à côté l'un de l'autre (le kit `.` et `autre`) et un
    absent : les pas lus en TODO ou pris de la source, les totaux du JSON ; un pas sans coût nulle part, une GARDE ;
    le dossier écrit, ignoré par Git dans le vrai kit."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        kit, autre = os.path.join(t, "kit"), os.path.join(t, "autre")
        for racine, todo in ((kit, "| 1 | `K1` — le premier | apporte | **V1 · score 15 (5 × 3)** · 2 à 3 fiches | — |"),
                             (autre, "| 7 | Le pont (`A1`) | apporte | **V2 · score 9 (3 × 3)** · 4 fiches | `K1` |")):
            ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(racine, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                                                           "|---|---|---|---|---|\n%s\n" % todo)
        source = os.path.join(kit, "ctx", "ordre.md")
        ecrire(source, ORDRE_SOURCE)
        code, s = appel(["ordre", "--json", "--source", source])
        donnees = json.load(open(os.path.join(kit, "ctx", "ordre", "donnees.json"), encoding="utf-8"))
        ecrire(source, ORDRE_SOURCE.replace("| 1 fiche |", "| |"))
        sans = appel(["ordre", "--json", "--source", source])
    assert (code == 0 and s.startswith("GARDE: projet x absent : absent n'est pas un dossier équipé")
             and "ORDRE 5 pas · 2 trouvés en TODO · 2 pris de la source\n" in s), ("ORD1 : ordre --json compte les pas, ceux lus en TODO, ceux pris de la source ; le projet absent dit") + "\n" + str(s)
    a1 = [p for p in donnees["pas"] if p["code"] == "A1"]
    assert (a1 == [{"projet": "a", "code": "A1", "numero": "7", "nom": "Le pont", "phase": "V2", "score": 9,
                     "bas": 4.0, "haut": 4.0, "fait": False, "note": "", "depend": "`K1`", "niveau": "obligatoire",
                     "vague": 1}]), ("ORD1 : un pas lu en TODO garde son nom, sa phase, son score, ses fiches et sa dépendance brute") + "\n" + str(a1)
    assert (donnees["totaux"] == {"pas": 4, "bas": 7.0, "haut": 8.0, "faits": ["K9"], "non_chiffres": [],
                                   "par_projet": {"k": {"pas": 2, "bas": 2.0, "haut": 3.0},
                                                  "a": {"pas": 2, "bas": 5.0, "haut": 5.0}},
                                   "par_niveau": {"obligatoire": {"pas": 2, "bas": 6.0, "haut": 7.0},
                                                  "conseillé": {"pas": 1, "bas": 0, "haut": 0},
                                                  "à la marge": {"pas": 1, "bas": 1.0, "haut": 1.0}}}
             and donnees["cible"] == {"a": ["A1"]} and donnees["projets_absents"] == ["x"]), ("ORD1 : les totaux du JSON — fiches bas et haut des pas chiffrés, faits, par projet") + "\n" + str(donnees)
    assert (sans[0] == 1 and "GARDE: pas A2 (a) : ni dans la TODO, ni un coût en fiches dans la source\n" in sans[1]), ("ORD1 : un pas ni en TODO ni chiffré par la source, une GARDE qui le nomme, sort 1") + "\n" + str(sans)
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:     # un dépôt neuf, le .gitignore du kit : vrai aussi dans une copie
        shutil.copy(os.path.join(mod.etat.KIT, ".gitignore"), t)
        init_git(t)
        ignore = subprocess.run(["git", "check-ignore", "context AI/ordre/donnees.json"], cwd=t,
                                capture_output=True, text=True)
    assert (ignore.returncode == 0), ("ORD1 : ce que le script écrit est ignoré par le .gitignore du kit") + "\n" + str(ignore)


CLASSE_SOURCE = """# L'ordre

## Les projets

| Clé | Dossier |
|---|---|
| p | `.` |

## La cible

| Projet | Codes |
|---|---|
| p | `P3` |

## Le chemin conseillé

| Pas | Projet | Nom | Coût |
|---|---|---|---|
| `P1` | p | | |
| `P2` | p | | |
| `P3` | p | | |
| `P4` | p | | |
| `P5` | p | | |
| `P6` | p | six | 1 fiche |

## Les dépendances ajoutées

| Pas | Dépend de | Pourquoi |
|---|---|---|
| `P2` | `P6` | le test |
"""


def test_ordre_classement(tmp_path):
    """ORD2 : un graphe de 6 pas — une chaîne P3 → P2 (par son numéro de ligne) → P1, P2 → P6 ajoutée par la source,
    une branche conseillée P4, un `V2` — classé et mis en vagues ; puis un cycle, et une dépendance illisible."""
    def classer(dep1, dep5):
        with tempfile.TemporaryDirectory(dir=tmp_path) as t:
            lignes = [(1, "V1", dep1), (2, "V1", "`P1`"), (3, "V1", "2"), (4, "V1", "`P1`"), (5, "V2", dep5)]
            ecrire(os.path.join(t, "p", "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(t, "p", "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                   "|---|---|---|---|---|\n" + "".join("| %d | `P%d` — pas | a | **%s · score 9 (3 × 3)** · 1 fiche | %s |\n"
                                                       % (n, n, phase, dep) for n, phase, dep in lignes))
            ecrire(os.path.join(t, "p", "ctx", "ordre.md"), CLASSE_SOURCE)
            code, s = appel(["ordre", "--json", "--source", os.path.join(t, "p", "ctx", "ordre.md")])
            chemin = os.path.join(t, "p", "ctx", "ordre", "donnees.json")
            return code, s, json.load(open(chemin, encoding="utf-8")) if os.path.isfile(chemin) else None
    code, s, donnees = classer("—", "—")
    niveaux = donnees and {p["code"]: p["niveau"] for p in donnees["pas"]}
    assert (code == 0 and niveaux == {"P1": "obligatoire", "P2": "obligatoire", "P3": "obligatoire", "P4": "conseillé",
                                       "P5": "à la marge", "P6": "obligatoire"}), ("ORD2 : obligatoire de proche en proche depuis la cible, conseillé en V1, à la marge en V2") + "\n" + str((s, niveaux))
    assert (donnees is not None and donnees["vagues"] == [["P1", "P5", "P6"], ["P2", "P4"], ["P3"]]
             and "CLASSEMENT 4 obligatoires · 1 conseillés · 1 à la marge · 3 vagues · dépendances : 3 lues en TODO, "
                 "1 écrites par la source, 0 hors du chemin\n" in s), ("ORD2 : les vagues du tri, dans l'ordre du chemin, et le compte des dépendances") + "\n" + str((s, donnees and donnees["vagues"]))
    cycle = classer("`P3`", "—")
    assert (cycle[0] == 1 and cycle[1].startswith("GARDE: cycle de dépendances : ") and cycle[2] is None), ("ORD2 : un cycle, une GARDE qui le nomme, rien d'écrit, sort 1") + "\n" + str(cycle[:2])
    illisible = classer("—", "plus tard")
    assert (illisible[0] == 1 and "GARDE: pas P5 : dépendance illisible « plus tard »\n" in illisible[1]), ("ORD2 : une dépendance illisible, une GARDE qui nomme le pas, sort 1") + "\n" + str(illisible[:2])


def donnees_de_page(html_):
    """Le bloc JSON d'une page d'ordre, relu ; `{}` sans bloc."""
    m = re.search(r'<script type="application/json" id="donnees">(.*?)</script>', html_, re.S)
    return json.loads(m.group(1)) if m else {}


def test_ordre_page(tmp_path):
    """ORD3 : `vlp.py ordre` sans `--json` écrit la page d'un projet temporaire — le JSON embarqué égal au fichier de
    données, chaque pas et chaque total, aucune balise de gabarit restante, un `</script>` de TODO échappé, ses joints
    et la ligne `FILES` ; un gabarit à deux balises, une GARDE ; Chart.js à la même URL que `vlp.js`."""
    source_page = ORDRE_SOURCE.replace("| Clé | Dossier |\n|---|---|\n| k | `.` |\n| a | `autre` |",
                                       "| Clé | Dossier | Nom |\n|---|---|---|\n| k | `.` | Le kit |\n| a | `autre` | |") \
        + "\n## Le jugement\n\n- `A1` d'abord, puis\n  le reste.\n\n## Les décisions\n\n- **K1** avant tout.\n"
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        kit, autre = os.path.join(t, "kit"), os.path.join(t, "autre")
        for racine, todo in ((kit, "| 1 | `K1` — le premier </script> | apporte | **V1 · score 15 (5 × 3)** · 2 à 3 fiches | — |"),
                             (autre, "| 7 | Le pont (`A1`) | apporte | **V2 · score 9 (3 × 3)** · 4 fiches | `K1` |")):
            ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(racine, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                                                           "|---|---|---|---|---|\n%s\n" % todo)
        source = os.path.join(kit, "ctx", "ordre.md")
        ecrire(source, source_page)
        code, s = appel(["ordre", "--source", source])
        dossier = os.path.join(kit, "ctx", "ordre")
        donnees = json.load(open(os.path.join(dossier, "donnees.json"), encoding="utf-8"))
        page = lire(os.path.join(dossier, "ordre.html")) if os.path.isfile(os.path.join(dossier, "ordre.html")) else ""
        joints = sorted(n for n in os.listdir(dossier) if n.startswith("vlp."))
        double = os.path.join(t, "double.html")
        ecrire(double, "<données><données>")
        avant, mod.etat.GABARIT_ORDRE = mod.etat.GABARIT_ORDRE, double
        try:
            garde = appel(["ordre", "--source", source])
        finally:
            mod.etat.GABARIT_ORDRE = avant
    embarque = donnees_de_page(page)
    assert (code == 0 and "\nPAGE " in s and "\nFILES {" in s and '"vlp.css"' in s and joints == ["vlp.css", "vlp.js"]), ("ORD3 : ordre sans --json écrit la page et ses joints, puis la ligne FILES") + "\n" + str((s, joints))
    assert (embarque == donnees and [p["code"] for p in embarque["pas"]] == ["K9", "K1", "A1", "A2"]
             and embarque["totaux"]["par_niveau"]["obligatoire"] == {"pas": 2, "bas": 6.0, "haut": 7.0}
             and [p["nom"] for p in embarque["projets"]] == ["Le kit", "a"]), ("ORD3 : la page porte les données entières — chaque pas, dans l'ordre, et chaque total") + "\n" + str(embarque)
    assert (embarque and embarque["prose"]["Le jugement"] == ["`A1` d'abord, puis le reste."]
             and embarque["prose"]["Les décisions"] == ["**K1** avant tout."]
             and [x["code"] for x in embarque["piste"]] == ["K1"]), ("ORD3 : la prose de la source en texte, puce continuée comprise, et la piste du projet de la source") + "\n" + str(embarque and embarque["prose"])
    restes = re.findall(r"<[^\x00-\x7f]|<…", page)
    assert (page and not restes and page.count("</script>") == lire(mod.etat.GABARIT_ORDRE).count("</script>")
             and mod.defauts_page(page) == [] and '<meta name="viewport"' in page), ("ORD3 : aucune balise de gabarit restante, un </script> de TODO échappé, la page saine, la balise viewport") + "\n" + str(restes)
    assert (garde[0] == 1 and "la balise <données> y est 2 fois, attendu 1" in garde[1]), ("ORD3 : un gabarit à deux balises, une GARDE qui le dit, sort 1") + "\n" + str(garde)
    url = re.compile(r"https://cdn\.jsdelivr\.net/npm/chart\.js@[^\"']+")
    assert (url.findall(lire(mod.etat.GABARIT_ORDRE)) == url.findall(lire(os.path.join(mod.etat.KIT, "templates", "vlp.js")))
             and len(url.findall(lire(mod.etat.GABARIT_ORDRE))) == 1), ("ORD3 : Chart.js chargé à la même URL que vlp.js") + "\n" + str(url.findall(lire(mod.etat.GABARIT_ORDRE)))


CLES_ORDRE_DB = ["source", "date", "projets", "cible", "projets_absents", "pas", "vagues", "dependances", "totaux",
                 "prose", "piste", "taux"]


def test_ordre_db(tmp_path):
    """ORD4 : `vlp.py ordre --db` écrit le document de la base — un objet JSON compact, chaque clé que la page lit, sa
    taille dite face à la limite d'un document `db`, et pas de page ; passé un dixième, un AVERTISSEMENT ; passé la
    limite, une GARDE, rien d'écrit."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        ecrire(os.path.join(t, "p", "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
        ecrire(os.path.join(t, "p", "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `P1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
        source = os.path.join(t, "p", "ctx", "ordre.md")
        ecrire(source, "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| p | `.` |\n\n## La cible\n\n| Projet | Codes |\n"
               "|---|---|\n| p | `P1` |\n\n## Le chemin conseillé\n\n| Pas | Projet | Nom | Coût |\n|---|---|---|---|\n"
               "| `P1` | p | | |\n\n## Le jugement\n\n- `P1` d'abord.\n")
        code, s = appel(["ordre", "--db", "--source", source])
        chemin = os.path.join(t, "p", "ctx", "ordre", "donnees.json")
        brut = open(chemin, encoding="utf-8").read()
        page = os.path.isfile(os.path.join(t, "p", "ctx", "ordre", "ordre.html"))
        avant = mod.etat.LIMITE_DOC_DB
        try:
            mod.etat.LIMITE_DOC_DB = len(brut.encode("utf-8")) * 5
            dixieme = appel(["ordre", "--db", "--source", source])
            mod.etat.LIMITE_DOC_DB = 100
            os.remove(chemin)
            trop = appel(["ordre", "--db", "--source", source])
        finally:
            mod.etat.LIMITE_DOC_DB = avant
        reecrit = os.path.isfile(chemin)
    doc = json.loads(brut)
    taille = len(brut.rstrip("\n").encode("utf-8"))
    assert (code == 0 and isinstance(doc, dict) and list(doc) == CLES_ORDRE_DB and "\n " not in brut and not page), ("ORD4 : ordre --db écrit un objet JSON compact, chaque clé que la page lit, sans page") + "\n" + str((s, list(doc)))
    assert (mod.etat.LIMITE_DOC_DB == 262144 and "DB ordre/donnees %d octets · limite 262144 · " % taille in s
             and "AVERTISSEMENT" not in s), ("ORD4 : la ligne DB dit la taille en octets face à la limite d'un document db (256 KiB)") + "\n" + str(s)
    assert (dixieme[0] == 0 and "AVERTISSEMENT: ordre/donnees passe le dixième" in dixieme[1]
             and trop[0] == 1 and "au-delà de la limite d'un document db (100)" in trop[1] and not reecrit), ("ORD4 : passé un dixième de la limite, un AVERTISSEMENT ; passé la limite, une GARDE, rien d'écrit") + "\n" + str((dixieme, trop))


def test_ordre_clore(tmp_path):
    """ORD5 : `clore` d'un projet, quel qu'il soit, refait les données de la page d'enchaînement du kit et dit quoi
    envoyer où (ligne `ORDRE`) ; sans source, une GARDE, et la clôture finit."""
    gabarit = lambda nom: open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
    sorties = []
    for avec_source in (True, False):
        with tempfile.TemporaryDirectory(dir=tmp_path) as tk:
            kit, projet = os.path.join(tk, "kit"), os.path.join(tk, "p")
            ecrire(os.path.join(kit, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n"
                   "- **artefact enchaînement** : https://claude.ai/artifact/essai\n")
            ecrire(os.path.join(kit, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                   "|---|---|---|---|---|\n| 1 | `K1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
            source = os.path.join(kit, "ctx", "ordre.md")
            if avec_source:
                ecrire(source, "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| k | `.` |\n\n## La cible\n\n"
                       "| Projet | Codes |\n|---|---|\n| k | `K1` |\n\n## Le chemin conseillé\n\n| Pas | Projet | Nom | "
                       "Coût |\n|---|---|---|---|\n| `K1` | k | | |\n")
            ecrire(os.path.join(projet, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : A (test).\n")
            ecrire(os.path.join(projet, "ctx", "08-etat.md"), "# État\n")
            ecrire(os.path.join(projet, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(projet, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
            ecrire(os.path.join(projet, "ctx", "artefacts", "feuille-de-route.html"),
                   gabarit("artefact-feuille-de-route.html"))
            avant = mod.etat.SOURCE_ORDRE
            try:
                mod.etat.SOURCE_ORDRE = source
                code, s = appel(["clore", projet, "--livre", "fini", "--date", "2026-10-13"])
            finally:
                mod.etat.SOURCE_ORDRE = avant
            donnees = os.path.join(kit, "ctx", "ordre", "donnees.json")
            sorties.append((code, s, os.path.isfile(donnees) and json.load(open(donnees, encoding="utf-8")),
                            os.path.realpath(donnees), os.path.realpath(source)))
    (code, s, doc, donnees, _), (code_sans, s_sans, doc_sans, _, source_sans) = sorties
    assert (code == 0 and "CLOS U " in s and "ORDRE envoyer %s → https://claude.ai/artifact/essai\n" % donnees in s
             and isinstance(doc, dict) and [p["code"] for p in doc["pas"]] == ["K1"]), ("ORD5 : clore d'un autre projet refait les données du kit et dit quoi envoyer où") + "\n" + str((code, s))
    assert (code_sans == 0 and "CLOS U " in s_sans and "ORDRE envoyer" not in s_sans and doc_sans is False
             and "GARDE: ordre : source introuvable (%s)" % source_sans in s_sans), ("ORD5 : sans source, une GARDE qui le dit, pas de ligne ORDRE, et la clôture finit") + "\n" + str((code_sans, s_sans))


def test_clore_pages_aucun(tmp_path):
    """ISO : un projet dont `CHANTIER.md` dit ses trois pages « aucun » se clôt sans ligne `ORDRE` vers la page
    d'enchaînement du kit, ni `GARDE:` de page absente ; une ligne `SANS PAGE` le dit."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tk:
        kit, projet = os.path.join(tk, "kit"), os.path.join(tk, "p")
        ecrire(os.path.join(kit, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n"
               "- **artefact enchaînement** : https://claude.ai/artifact/essai\n")
        ecrire(os.path.join(kit, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `K1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
        source = os.path.join(kit, "ctx", "ordre.md")
        ecrire(source, "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| k | `.` |\n\n## La cible\n\n"
               "| Projet | Codes |\n|---|---|\n| k | `K1` |\n\n## Le chemin conseillé\n\n| Pas | Projet | Nom | "
               "Coût |\n|---|---|---|---|\n| `K1` | k | | |\n")
        ecrire(os.path.join(projet, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n- **artefact feuille de route** : aucun\n"
               "- **artefact du chantier** : aucun\n- **artefact enchaînement** : aucun\n\n"
               "Lettres de fiche déjà prises : A (test).\n")
        ecrire(os.path.join(projet, "ctx", "08-etat.md"), "# État\n")
        ecrire(os.path.join(projet, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
        avant = mod.etat.SOURCE_ORDRE
        try:
            mod.etat.SOURCE_ORDRE = source
            code, s = appel(["clore", projet, "--livre", "fini", "--date", "2026-10-17"])
        finally:
            mod.etat.SOURCE_ORDRE = avant
        donnees = os.path.join(kit, "ctx", "ordre", "donnees.json")
        assert (code == 0 and "CLOS U " in s and "ORDRE envoyer" not in s and not os.path.exists(donnees)
                 and "page du chantier introuvable" not in s and "feuille de route introuvable" not in s
                 and "SANS PAGE la page du chantier, la feuille de route — CHANTIER.md dit « aucun »\n" in s), ("ISO : clore d'un projet aux pages « aucun » — ni ORDRE vers le kit, ni GARDE de page absente, "
                 "une ligne SANS PAGE — clore : enchaînement « aucun » ignoré") + "\n" + str((code, s))


def lien_dossier(cible, lien):
    """Un lien vers le dossier `cible` : une jonction sous Windows (`mklink /J`, sans droit d'administrateur), comme
    `~/.claude/skills/vlp` ; un lien symbolique ailleurs."""
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", lien, cible], capture_output=True, check=True)
    else:
        os.symlink(cible, lien)


def test_ordre_jonction(tmp_path):
    """Dette ORD : lancé par le plugin, le kit est vu par une jonction ; `ordre` cherche les projets voisins à côté du
    vrai kit, pas à côté du lien."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tj:
        kit, autre, lien = os.path.join(tj, "vrai", "kit"), os.path.join(tj, "vrai", "autre"), os.path.join(tj, "lien")
        for racine, todo in ((kit, "| 1 | `K1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |"),
                             (autre, "| 2 | `A1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |")):
            ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(racine, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                   "|---|---|---|---|---|\n%s\n" % todo)
        ecrire(os.path.join(kit, "ctx", "ordre.md"), "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| k | `.` |\n"
               "| a | `autre` |\n\n## La cible\n\n| Projet | Codes |\n|---|---|\n| a | `A1` |\n\n## Le chemin conseillé\n\n"
               "| Pas | Projet | Nom | Coût |\n|---|---|---|---|\n| `K1` | k | | |\n| `A1` | a | | |\n")
        lien_dossier(kit, lien)
        code, s = appel(["ordre", "--json", "--source", os.path.join(lien, "ctx", "ordre.md")])
        os.rmdir(lien) if os.name == "nt" else os.remove(lien)   # la jonction seule, jamais ce qu'elle vise
    assert (code == 0 and "GARDE" not in s and "ORDRE 2 pas · 2 trouvés en TODO" in s), ("Dette ORD : la source lue par une jonction trouve le projet voisin du vrai kit") + "\n" + str((code, s))
