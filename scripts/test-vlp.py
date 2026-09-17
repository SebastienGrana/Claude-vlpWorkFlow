#!/usr/bin/env python3
"""Teste vlp.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle les sous-commandes, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile

for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("vlp", os.path.join(ICI, "vlp.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **fichier de fiches courant** : %s\n"
FICHES = """# Chantier Z

## Le socle commun

## Z1 [x] — faite
---
## Z2 [ ] — à faire
## Z10 [ ] — après
"""


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte)


def rendu(depart):
    s = io.StringIO()
    mod.carte(depart, s)
    return s.getvalue()


def verifier(nom, cond, sortie):
    if not cond:
        print("ÉCART:", nom)
        print(sortie)
        sys.exit(1)


with tempfile.TemporaryDirectory() as t:
    p = os.path.join(t, "proj")
    ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/20-z.md (Z1..Z10)"))
    ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
    sous = os.path.join(p, "src", "a")
    os.makedirs(sous)
    ecrire(os.path.join(p, "src", "chantier.md"), "une commande, pas la carte\n")

    s = rendu(sous)
    verifier("remonte au projet", "PROJET=%s\n" % p in s, s)
    verifier("carte entière", "- **alias** : pz" in s, s)
    verifier("chemin avec espace et plage", "--- fiches : context AI/20-z.md (8 lignes, 3 titres) ---" in s, s)
    verifier("titres numérotés", "5:## Z1 [x] — faite\n7:## Z2 [ ] — à faire\n8:## Z10 [ ] — après\n" in s, s)
    verifier("prochaine dans l'ordre du fichier", s.endswith("PROCHAINE=Z2\n"), s)

    ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES.replace("[ ]", "[x]"))
    s = rendu(p)
    verifier("tout coché", s.endswith("PROCHAINE=aucune\n"), s)

    ecrire(os.path.join(p, "context AI", "20-z.md"), "# titres\n### Z1 reformulé\n")
    s = rendu(p)
    verifier("garde grep muet", "GARDE: aucun titre" in s and "PROCHAINE" not in s, s)

    ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "aucun"))
    s = rendu(p)
    verifier("aucun courant", s.endswith("--- fichier de fiches courant : aucun ---\n"), s)

    ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/99-absent.md"))
    s = rendu(p)
    verifier("fichier absent", "GARDE: fichier de fiches introuvable : context AI/99-absent.md" in s, s)

    w = os.path.join(t, "ws")
    ecrire(os.path.join(w, "b", "CHANTIER.md"), CHANTIER % ("bb", "aucun"))
    ecrire(os.path.join(w, "a", "CHANTIER.md"), CHANTIER % ("aa", "aucun"))
    ecrire(os.path.join(w, "c", "chantier.md"), "une commande\n")
    s = rendu(w)
    verifier("voisins triés avec alias",
             s == "VOISIN=%s alias=aa\nVOISIN=%s alias=bb\n" % (os.path.join(w, "a"), os.path.join(w, "b")), s)

    vide = os.path.join(t, "vide")
    os.makedirs(vide)
    s = rendu(vide)
    verifier("aucun projet", s == "AUCUN_PROJET\n", s)


def appel(argv):
    s = io.StringIO()
    code = mod.main(argv, s)
    return code, s.getvalue()


AVEC = """# Chantier Y

## Le socle commun

Socle, ligne 1.

## L'ordre des fiches

---

<!-- FICHE:Y1 -->
## Y1 [x] — faite
**Session** : aaa
**Prompt**
```
---
## pas un titre
```
<!-- /FICHE -->

---

<!-- FICHE:Y2 -->
## Y2 [ ] — à faire
**Session** : bbb
**Session** : aaa
<!-- /FICHE -->
"""

SANS = "## Z1 [ ] — ancien\nlong\n---\n## Z2 [ ] — dernier\nfin\n"

with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "y.md")
    ecrire(f, AVEC)
    code, s = appel(["extraire", f, "Y1"])
    verifier("extraire : marqueurs, --- dans un bloc de code", code == 0 and s.startswith("<!-- FICHE:Y1 -->\n## Y1")
             and "## pas un titre\n```\n<!-- /FICHE -->\n--- fiche, lignes : 9\n" in s and "GARDE" not in s, s)
    code, s = appel(["extraire", f, "Y9"])
    verifier("extraire : fiche absente", code == 1 and "GARDE: fiche introuvable : Y9" in s, s)
    code, s = appel(["socle", f])
    verifier("socle : du titre à l'ordre exclu", code == 0 and s == "## Le socle commun\n\nSocle, ligne 1.\n\n--- socle, lignes : 4\n", s)
    code, s = appel(["sessions", f])
    verifier("sessions : dédoublonnées, dans l'ordre", code == 0 and s == "aaa\nbbb\n", s)

    ecrire(f, AVEC.replace("<!-- /FICHE -->\n\n---\n\n<!-- FICHE:Y2", "\n---\n\n<!-- FICHE:Y2"))
    code, s = appel(["extraire", f, "Y1"])
    verifier("extraire : fermant absent, arrêt au marqueur suivant", code == 0 and s.startswith("GARDE: marqueur fermant absent")
             and "Y2" not in s and s.endswith("```\n\n---\n\n--- fiche, lignes : 11\n"), s)

    ecrire(f, SANS)
    code, s = appel(["extraire", f, "Z1"])
    verifier("extraire : repli sans marqueurs", code == 0 and "GARDE: pas de marqueurs" in s
             and s.endswith("## Z1 [ ] — ancien\nlong\n---\n--- fiche, lignes : 3\n"), s)
    code, s = appel(["extraire", f, "Z2"])
    verifier("extraire : repli jusqu'à la fin", s.endswith("fin\n--- fiche, lignes : 2\n"), s)
    code, s = appel(["socle", f])
    verifier("socle : absent", code == 1 and s == "--- socle, lignes : 0\n", s)
    code, s = appel(["sessions", f])
    verifier("sessions : aucune", code == 0 and s == "", s)

    ecrire(f, AVEC.replace("\n", "\r\n"))
    code, s = appel(["socle", f])
    verifier("CRLF toléré", code == 0 and "\r" not in s and s.endswith("--- socle, lignes : 4\n"), s)
    code, s = appel(["extraire", os.path.join(t, "absent.md"), "Y1"])
    verifier("fichier absent", code == 1 and "GARDE: fichier introuvable" in s, s)

    code, s = appel(["carte", os.path.join(t, "nulle-part")])
    verifier("carte par main, sortie 0", code == 0 and s == "AUCUN_PROJET\n", s)

SAIN = """# Chantier V

## Le socle commun

Un socle.

## L'ordre des fiches

---

<!-- FICHE:V1 -->
## V1 [ ] — scriptable
On parle de `(visuel)` entre accents graves : ce n'est pas le marqueur.
Un code en ligne `**Critère de
fin**` coupé, puis l'arrêt (`(visuel)`) : pas le marqueur.
**Critère de fin**
Une commande.
<!-- /FICHE -->

---

<!-- FICHE:V2 -->
## V2 [ ] — visuelle
**Critère de fin** (visuel)
L'utilisateur regarde.
<!-- /FICHE -->
"""


def valide(texte):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "v.md")
        ecrire(f, texte)
        code, s = appel(["valider", f])
        return code, s.replace(f, "F")


code, s = valide(SAIN)
verifier("valider : sain", code == 0 and s == "VALIDE 2 fiches · socle 4 lignes · 0 écarts · 0 avertissements — F\n", s)

CAS = [
    ("fermant absent", SAIN.replace("L'utilisateur regarde.\n<!-- /FICHE -->", "L'utilisateur regarde."),
     "F:22: marqueur ouvrant sans fermant : <!-- FICHE:V2 -->"),
    ("imbriqué", SAIN.replace("Une commande.\n<!-- /FICHE -->", "Une commande."),
     "F:21: marqueur imbriqué : <!-- FICHE:V1 --> ouvert ligne 11 sans fermant"),
    ("fermant orphelin", SAIN + "<!-- /FICHE -->\n", "F:27: marqueur fermant sans ouvrant"),
    ("marqueur ≠ titre", SAIN.replace("<!-- FICHE:V2 -->", "<!-- FICHE:V9 -->"), "F:23: marqueur V9 ≠ titre V2"),
    ("titre sans marqueurs", SAIN + "\n---\n\n## V3 [ ] — nue\n**Critère de fin**\n", "F:30: titre sans marqueurs : V3"),
    ("double", SAIN.replace("## V2 [ ] — visuelle", "## V1 [ ] — visuelle").replace("FICHE:V2", "FICHE:V1"),
     "F:23: identifiant en double : V1 (déjà ligne 12)"),
    ("socle absent", SAIN.replace("## Le socle commun", "## Socle"), "F:1: section absente : ## Le socle commun"),
    ("ordre en double", SAIN + "\n## L'ordre des fiches\n", "F:28: section en double : ## L'ordre des fiches (déjà ligne 7)"),
    ("section après une fiche", SAIN.replace("## L'ordre des fiches\n", "").replace("L'utilisateur regarde.\n", "L'utilisateur regarde.\n## L'ordre des fiches\n"),
     "F:25: section après la première fiche : ## L'ordre des fiches"),
    ("sans critère", SAIN.replace("**Critère de fin**\nUne commande.", "Une commande."), "F:11: fiche V1 sans ligne **Critère de fin**"),
    ("visuel hors ligne (point 9)", SAIN.replace("**Critère de fin** (visuel)", "Voici le **Critère de fin** (visuel)"),
     "F:24: fiche V2 : (visuel) hors de la ligne"),
]
for nom, texte, attendu in CAS:
    code, s = valide(texte)
    verifier("valider : " + nom, code == 1 and attendu in s and s.splitlines()[-1].startswith("INVALIDE"), s)

code, s = valide(SAIN.replace("Une commande.\n", "Une commande.\n" + "x\n" * 60))
verifier("valider : avertissement de longueur, pas écart", code == 0
         and "F:11: avertissement : fiche V1 : 68 lignes, au-delà du seuil" in s and "0 écarts · 1 avertissements" in s, s)
code, s = valide(SAIN.replace("Un socle.\n", "Un socle.\n" + "x\n" * 77))
verifier("valider : socle de 81 lignes avertit", code == 0
         and "F:3: avertissement : socle : 81 lignes, au-delà du seuil" in s and "1 avertissements" in s, s)
code, s = valide(SAIN.replace("Un socle.\n", "Un socle.\n" + "x\n" * 76))
verifier("valider : socle de 80 lignes n'avertit pas", code == 0
         and "socle : 80 lignes" not in s and "0 avertissements" in s, s)
code, s = appel(["valider", "absent-1.md", "absent-2.md"])
verifier("valider : un bilan par fichier", code == 1 and s.count("INVALIDE 0 fiches") == 2, s)

import json

lire = mod.lire


def transcript(chemin, tours):
    """Un jsonl de `tours` tours, 100 000 tokens d'entrée chacun, sur claude-opus-5 (5 $ le million)."""
    with open(chemin, "w", encoding="utf-8") as f:
        for n in range(tours):
            f.write(json.dumps({"type": "assistant", "requestId": "r%d" % n, "message": {
                "id": "m%d" % n, "model": "claude-opus-5", "content": [],
                "usage": {"input_tokens": 100000, "output_tokens": 0,
                          "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}}) + "\n")


verifier("arrondi", [mod.arrondi(n) for n in (999, 1000, 1505630)] == ["999", "≈1,0k (1 000)", "≈1,5M (1 505 630)"],
         [mod.arrondi(n) for n in (999, 1000, 1505630)])

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

with tempfile.TemporaryDirectory() as t:
    fiches = os.path.join(t, "p.md")
    page = os.path.join(t, "p.html")
    sa, sb = os.path.join(t, "a.jsonl"), os.path.join(t, "b.jsonl")
    transcript(sa, 2)
    transcript(sb, 1)

    ecrire(fiches, PAGE % (" ", "", " ", ""))
    code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "Le <titre>",
                     "--resultat", "Fini quand.", "--note", "P1", "Produit a.py", "--date", "2026-01-02"])
    html = lire(page) if os.path.exists(page) else ""
    verifier("page --creer", code == 0 and "<title>Proj — Le &lt;titre&gt;</title>" in html
             and "Proj · fiches P1–P3" in html and "<p>Fini quand.</p>" in html
             and '<span data-etat="encours"></span><span></span><span></span>' in html
             and "3 fiches · 0 faite · en cours : P1" in html and '<span class="note">Produit a.py</span>' in html
             and "&lt;" not in html.split("<ul class=\"journal\">")[1].split("</ul>")[0]
             and '<p class="mono cout-total">' not in html and "Mis à jour le <span class=\"mono\">2026-01-02</span>" in html
             and "lignes · total non mesuré" in s, s + html)
    code, s = appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R"])
    verifier("page --creer n'écrase pas", code == 1 and "existe déjà" in s, s)

    ecrire(fiches, PAGE % ("x", "**Session** : %s\n" % sa, " ", ""))
    code, s = appel(["page", fiches, page, "--verifier"])
    verifier("page --verifier : en retard", code == 1 and "ÉCART: P1 : page encours, fichier faite" in s
             and "EN RETARD 3 fiches · 3 écarts" in s, s)
    code, s = appel(["page", fiches, page, "--note", "P1", "a.py : <3 tests>", "--journal", "P1 : tranché.", "--date", "2026-01-03"])
    html = lire(page)
    verifier("page : fiche faite, coût, note échappée, journal", code == 0
             and '<li class="fiche" data-etat="faite">' in html and "a.py : &lt;3 tests&gt;" in html
             and '<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>' in html
             and '<p class="mono cout-total">Coût du chantier : ≈200,0k (200 000) · 2 tours · 1,00 $</p>' in html
             and '<time datetime="2026-01-03">2026-01-03</time><span>P1 : tranché.</span>' in html
             and "3 fiches · 1 faite · en cours : P2" in html, s + html)
    code, s = appel(["page", fiches, page, "--verifier"])
    verifier("page --verifier : à jour", code == 0 and s == "À JOUR 3 fiches · 0 écarts (états et avancement seulement)\n", s)
    avant = lire(page)
    appel(["page", fiches, page, "--date", "2026-01-03"])
    verifier("page : régénérer deux fois ne change rien", lire(page) == avant, lire(page))

    # P2 partage la session de P1 : P1 garde son coût affiché, P2 prend le reste ; b s'ajoute au total.
    # L'ancien total compte 1 tour de cadrage (100 000) qu'aucune fiche ne porte : il reste hors de P2.
    ecrire(page, lire(page).replace("Coût du chantier : ≈200,0k (200 000) · 2 tours · 1,00 $",
                                    "Coût du chantier : ≈300,0k (300 000) · 3 tours · 1,50 $"))
    transcript(sa, 4)
    ecrire(fiches, PAGE % ("x", "**Session** : %s\n" % sa, "x", "**Session** : %s\n**Session** : %s\n" % (sa, sb)))
    code, s = appel(["page", fiches, page, "--date", "2026-01-04"])
    html = lire(page)
    verifier("page : session partagée, le reste à la dernière", code == 0
             and '<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>' in html
             and '<span class="cout mono">≈100,0k (100 000) · 1 tours · 0,50 $</span>' in html
             and "Coût du chantier : ≈500,0k (500 000) · 5 tours · 2,50 $" in html
             and "3 fiches · 2 faites · en cours : P3" in html, s + html)
    avant = lire(page)
    appel(["page", fiches, page, "--date", "2026-01-04"])
    verifier("page : session partagée, régénérer deux fois ne change rien", lire(page) == avant, lire(page))

    # Blocage : bloquée reste bloquée tant que non cochée ; le bloc se masque quand elle l'est.
    html = lire(page).replace('<li class="fiche" data-etat="encours">', '<li class="fiche" data-etat="bloquee">')
    html = html.replace("<section hidden>\n    <h2>Arrêt sur blocage</h2>", "<section>\n    <h2>Arrêt sur blocage</h2>")
    html = html.replace('<div class="blocage">\n      <p></p>', '<div class="blocage">\n      <p>P3 — deux essais.</p>')
    ecrire(page, html)
    appel(["page", fiches, page])
    html = lire(page)
    verifier("page : bloquée gardée", '<li class="fiche" data-etat="bloquee">' in html and "bloquée : P3" in html
             and "<section>\n    <h2>Arrêt sur blocage</h2>" in html, html)
    ecrire(fiches, lire(fiches).replace("## P3 [ ]", "## P3 [x]"))
    code, s = appel(["page", fiches, page])
    html = lire(page)
    verifier("page : blocage masqué une fois cochée", code == 0 and "<section hidden>\n    <h2>Arrêt sur blocage</h2>" in html
             and "3 fiches · 3 faites</p>" in html and 'data-etat="bloquee"' not in html.split('<div class="page">')[1], s + html.split("<div class=\"page\">")[1])

    code, s = appel(["page", fiches, os.path.join(t, "absente.html")])
    verifier("page absente sans --creer", code == 1 and "--creer" in s, s)


# --- hook : le PostToolUse du plugin -----------------------------------------

def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


with tempfile.TemporaryDirectory() as t:
    def json_de(nom):
        return '{"tool_input": {"file_path": "%s"}, "cwd": "%s"}' % (nom, t.replace("\\", "/"))

    code, o, e = hook("pas du json")
    verifier("hook : JSON illisible, muet", (code, o, e) == (0, "", ""), o + e)
    ecrire(os.path.join(t, "notes.md"), "# Notes\n\n```\n<!-- FICHE:D1 -->\n## Le socle commun\n```\n")
    code, o, e = hook(json_de("notes.md"))
    verifier("hook : .md ordinaire (marqueur en bloc de code), muet", (code, o, e) == (0, "", ""), o + e)
    ecrire(os.path.join(t, "y.md"), AVEC.replace("\n**Prompt**\n```\n---\n## pas un titre\n```", "\n**Critère de fin**")
           .replace("**Session** : bbb", "**Critère de fin**"))
    code, o, e = hook(json_de("y.md"))
    verifier("hook : fiches valides, bilan en JSON, sort 0", code == 0 and e == ""
             and '"additionalContext": "VALIDE 2 fiches' in o and '"hookEventName": "PostToolUse"' in o, o + e)
    ecrire(os.path.join(t, "y.md"), lire(os.path.join(t, "y.md")).replace("<!-- /FICHE -->\n\n---", "\n---", 1))
    code, o, e = hook(json_de("y.md"))
    verifier("hook : fermant manquant, sort 2 sur stderr", code == 2 and o == "" and "marqueur" in e
             and "INVALIDE" in e and e.endswith("Corrige ce fichier de fiches avant de continuer.\n"), o + e)
    ecrire(os.path.join(t, "y.md"), AVEC.replace("## Le socle commun", "## Socle"))
    code, o, e = hook(json_de("y.md"))
    verifier("hook : titre de section reformulé, sort 2", code == 2 and "section absente : ## Le socle commun" in e, o + e)

with tempfile.TemporaryDirectory() as t:
    c = os.path.join(t, "ctx")
    verifier("etat : dossier absent", appel(["etat", c]) == (0, "ETAT=01-etat.md\n"), appel(["etat", c]))
    os.makedirs(c)
    verifier("etat : dossier vide", appel(["etat", c]) == (0, "ETAT=01-etat.md\n"), appel(["etat", c]))
    ecrire(os.path.join(c, "03-a.md"), "a\n")
    ecrire(os.path.join(c, "07-b.md"), "b\n")
    verifier("etat : à la suite du plus grand", appel(["etat", c]) == (0, "ETAT=08-etat.md\n"), appel(["etat", c]))
    ecrire(os.path.join(c, "10-etat.md"), "état\n")
    verifier("etat : déjà présent", appel(["etat", c]) == (0, "ETAT=10-etat.md\n"), appel(["etat", c]))

with tempfile.TemporaryDirectory() as t:
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
    verifier("renvois : tout présent", appel(["renvois", t]) == (0, "RENVOIS 3 nommés · 0 absents\n"), appel(["renvois", t]))
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `99-mort.md` | jamais |\n")
    code, s = appel(["renvois", t])
    verifier("renvois : absent, sort 1", code == 1 and s == "ABSENT: ctx/00-INDEX.md:3: 99-mort.md\nRENVOIS 2 nommés · 1 absents\n", s)
    os.remove(os.path.join(t, "CHANTIER.md"))
    verifier("renvois : pas équipé", appel(["renvois", t])[0] == 1, appel(["renvois", t]))

SH = shutil.which("sh")
if SH is None:
    print("lanceur : sh absent du PATH, tests du lanceur sautés")
else:
    def lancer(argv, env=None):
        r = subprocess.run([SH, os.path.join(ICI, "vlp")] + argv, capture_output=True, env=env,
                           encoding="utf-8", errors="replace")
        return r.returncode, r.stdout.replace("\r", ""), r.stderr
    with tempfile.TemporaryDirectory() as t:
        r = lancer(["etat", os.path.join(t, "ctx")])
        verifier("lanceur : relaie la sous-commande, sort 0", r[:2] == (0, "ETAT=01-etat.md\n"), r)
        r = lancer(["renvois", t])
        verifier("lanceur : relaie le code de sortie", r[0] == 1, r)
        r = lancer(["mesure"])
        verifier("lanceur : mesure lance mesure-tokens.py", r[0] == 1 and "usage: mesure-tokens.py" in r[1] + r[2], r)
        r = lancer(["etat", t], env=dict(os.environ, PATH=t))
        verifier("lanceur : aucun Python, sort 127", r[0] == 127 and "aucun Python" in r[2], r)

print("OK")
