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
    verifier("extraire : fiche scriptable, pas d'ARRÊT", "ARRÊT" not in s, s)
    ecrire(f, AVEC.replace("**Prompt**\n", "**Critère de fin** (visuel)\n"))
    code, s = appel(["extraire", f, "Y1"])
    verifier("extraire : fiche (visuel), ARRÊT avant le compte", code == 0
             and s.endswith("<!-- /FICHE -->\n" + mod.ARRET + "\n--- fiche, lignes : 9\n"), s)
    ecrire(f, AVEC)
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
    nulle = os.path.join(t, "nulle-part")
    r1 = appel(["carte", nulle, "--python", "py"])
    r2 = appel(["carte", nulle, "--python", "python3", "--relais"])
    r3 = appel(["carte", nulle, "--python", "py", "--relais"])
    r4 = appel(["carte", os.path.join(t, "ailleurs"), "--python", "python3", "--relais"])
    verifier("carte --python : ligne vide, PYTHON=, deux relais muets (U4), relais seul",
             (r1, r2, r3, r4) == ((0, "\nPYTHON=py\nAUCUN_PROJET\n"), (0, ""), (0, ""), (0, "\nPYTHON=python3\nAUCUN_PROJET\n")), (r1, r2, r3, r4))

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
    verifier("renvois : tout présent, poids sous seuil", appel(["renvois", t]) == (0, "POIDS CLAUDE.md 14/80 · CHANTIER.md 2/50 · index 9/80\n"
             "RENVOIS 3 nommés · 0 absents\n"), appel(["renvois", t]))
    ecrire(os.path.join(t, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n" + "x\n" * 49)
    code, s = appel(["renvois", t])
    verifier("renvois : poids au-delà, avertit sans changer la sortie", code == 0 and s.startswith(
        "AVERTISSEMENT: CHANTIER.md 51 lignes > 50\nPOIDS CLAUDE.md 14/80 · CHANTIER.md 51/50 · index 9/80\n"), s)
    os.remove(os.path.join(t, "CLAUDE.md"))
    code, s = appel(["renvois", t])
    verifier("renvois : CLAUDE.md absent dans les poids", code == 0 and "POIDS CLAUDE.md absent/80 · CHANTIER.md 51/50" in s, s)
    ecrire(os.path.join(t, "CLAUDE.md"),
           "# P\n\n| hors routage | `perdu.md` |\n\n## Routage — ouvrir ceci\n\n| La tâche | Ouvrir |\n|---|---|\n"
           "| lire `vlp.py` | `ctx/01-a.md` |\n| lancer | **`/vlp:chantier`** |\n\n## Économie\n\n| x | `loin.md` |\n")
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `99-mort.md` | jamais |\n")
    code, s = appel(["renvois", t])
    verifier("renvois : absent, sort 1", code == 1 and s.startswith("ABSENT: ctx/00-INDEX.md:3: 99-mort.md\n")
             and s.endswith("index 3/80\nRENVOIS 2 nommés · 1 absents\n"), s)
    os.remove(os.path.join(t, "CHANTIER.md"))
    verifier("renvois : pas équipé", appel(["renvois", t])[0] == 1, appel(["renvois", t]))

with tempfile.TemporaryDirectory() as t:
    carte_ = ("# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
              "- **fichier de fiches courant** : %s\n- **artefact du chantier** : %s\n\n"
              "Lettres de fiche déjà prises : E (Un), M (Deux `x`). Un nouveau chantier en choisit une autre.\n")
    ecrire(os.path.join(t, "CHANTIER.md"), carte_ % ("aucun", "aucun"))
    ecrire(os.path.join(t, "ctx", "08-etat.md"),
           "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
           "| 3 | Le `sh` | a \\|\\| b <c> | 2 fiches | — |\n| 4 | Quatre | rien | 1 fiche | 3 |\n\n## Journal\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [x] — a\n## Q2 [ ] — b\n")
    fdr = os.path.join(t, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(fdr, open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read())
    lire = lambda c: open(c, encoding="utf-8").read()
    code, s = appel(["feuille", t, "--date", "2026-01-02"])
    html = lire(fdr)
    verifier("feuille : fermé, réécrite", code == 0 and "FEUILLE todo 2 · encours non · lettres 2 · réécrite" in s
             and "Aucun chantier ouvert" in html and '<span class="mono">E, M</span>' in html
             and '<span class="mono">2026-01-02</span>' in html, s + html)
    verifier("feuille : TODO rendue", '<td>Le <span class="mono">sh</span></td><td>a || b &lt;c&gt;</td>' in html
             and "&lt;U, R&gt;" not in html and 'data-etat="cours"' not in html.split("ZONE:todo")[1], html)
    code, s = appel(["feuille", t, "--date", "2026-03-04"])
    verifier("feuille : idempotente, date gardée", code == 0 and "inchangée" in s and "2026-01-02" in lire(fdr), s)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_ % ("ctx/30-q.md (Q1..Q2)", "https://exemple/q"))
    code, s = appel(["feuille", t, "--verifier"])
    verifier("feuille : --verifier voit l'écart sans écrire", code == 1 and "écart" in s and "Aucun chantier" in lire(fdr), s)
    code, s = appel(["feuille", t, "--todo", "4", "--date", "2026-03-04"])
    html = lire(fdr)
    verifier("feuille : ouvert, badge, lettre", code == 0 and "encours oui · lettres 3" in s
             and 'Un titre <span class="badge" data-etat="cours">' in html and '<span class="mono">Q1–Q2</span>' in html
             and 'href="https://exemple/q"' in html and "E, M, Q" in html
             and '<td class="mono">4</td><td>Quatre <span class="badge" data-etat="cours">' in html, s + html)
    code, s = appel(["feuille", t])
    verifier("feuille : badge gardé sans --todo", code == 0 and "inchangée" in s, s)
    verifier("feuille : --verifier identique", appel(["feuille", t, "--verifier"])[0] == 0, appel(["feuille", t, "--verifier"]))
    code, s = appel(["feuille", t, "--todo", "9"])
    verifier("feuille : --todo absent, garde", code == 1 and s.startswith("GARDE:"), s)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_ % ("aucun", "aucun"))
    code, s = appel(["feuille", t])
    html = lire(fdr)
    verifier("feuille : refermé, badge ôté", code == 0 and "Aucun chantier ouvert" in html
             and 'data-etat="cours"' not in html.split("ZONE:encours")[1] and "E, M</span>" in html, s)

    ecrire(os.path.join(t, "CHANTIER.md"), carte_ % ("ctx/30-q.md (Q1..Q2)", "https://exemple/q")
           + "\n| Fichier de fiches | Fiches | Clos le | Artefact |\n|---|---|---|---|\n| ctx/10-e.md | E1..E2 | 2026-01-01 | u |\n\nFin.\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un `titre`\n\n**À quoi il sert.** x\n\n**Fait.** Rien.\n\n## Q1 [x] — a\n## Q2 [ ] — b\n")
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
    ecrire(page_q, open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read()
           .replace("<!-- ZONE:blocage — publiée quand /tache s'arrête après deux tentatives ; retirée dès que la fiche repasse -->\n  <section hidden>",
                    "<!-- ZONE:blocage — publiée quand /tache s'arrête après deux tentatives ; retirée dès que la fiche repasse -->\n  <section>"))
    verifier("clore : gabarit, blocage visible avant", page_q and "<!-- ZONE:blocage" in lire(page_q) and lire(page_q).count("<section hidden>") == 1, lire(page_q))
    code, s = appel(["clore", t, "--livre", "Livré `a` <b>", "--tokens", "1500", "--abandon", "Q2 abandonnée", "--date", "2026-05-06", "--surpris", "x < y", "--resume", "b `c`."])
    carte_lue, fiches_lues, html = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "30-q.md")), lire(fdr)
    verifier("clore : routage, index, bilan, résumé comptés", "· routage 1 · index 1 · bilan 1 · résumé 1 —" in s and "GARDE" not in s, s)
    verifier("clore : résumé, une ligne par clos", "- Clos le 2026-05-06 : a (chantier E).\n- Clos le 2026-05-06 : b `c` (chantier Q).\n\n## Routage" in lire(os.path.join(t, "CLAUDE.md")), lire(os.path.join(t, "CLAUDE.md")))
    cl, g = ["## Où on en est", "", "- Clos le 2026-01-01 : a (chantier E).", "", "## Règles"], []
    verifier("résumé : ligne ajoutée après la dernière", mod.resume_claude(cl, "Q", "b", "2026-02-02", g)
             and cl[3] == "- Clos le 2026-02-02 : b (chantier Q)." and cl[2].endswith("E).") and not g, cl)
    cl2 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."]
    verifier("résumé : suffixe (chantier Q) déjà dans le texte, pas doublé", mod.resume_claude(cl2, "Q", "b (chantier Q).", "2026-01-01", g)
             and cl2[-1] == "- Clos le 2026-01-01 : b (chantier Q).", cl2)
    verifier("résumé : déjà là, rien", not mod.resume_claude(cl, "Q", "b", "2026-02-02", g) and len(cl) == 6, cl)
    cl3 = ["## Où on en est", "- Prouvé : x.", "  puis vieux (chantier A) ;"] + ["- Clos le 2026-01-0%d : c%d (chantier %s)." % (i, i, "BCDEF"[i - 1]) for i in range(1, 6)] + ["", "## R"]
    verifier("résumé : garde les CLOS_GARDES derniers, le plus ancien sorti", mod.resume_claude(cl3, "G", "g", "2026-01-09", g)
             and mod.CLOS_GARDES == 5 and not any("(chantier B)" in l for l in cl3) and cl3[:3] == ["## Où on en est", "- Prouvé : x.", "  puis vieux (chantier A) ;"]
             and sum(1 for l in cl3 if l.startswith("- Clos le")) == 5 and cl3[-3] == "- Clos le 2026-01-09 : g (chantier G).", cl3)
    verifier("résumé : section absente, garde", not mod.resume_claude(["# x"], "Q", "b", "d", g) and g and "Où on en est" in g[0], g)
    verifier("clore : Fait. remplacé", "**Fait.** Q1..Q2 (2026-05-06) : Livré `a` <b>.\n" in fiches_lues and "**Fait.** Rien." not in fiches_lues, fiches_lues)
    verifier("clore : index clos", "| `30-q.md` | on relit le socle du chantier Q — **clos** « Un (vrai) titre », `Q1..Q2` |\n" == lire(os.path.join(t, "ctx", "00-INDEX.md")).split("---|\n")[1], lire(os.path.join(t, "ctx", "00-INDEX.md")))
    verifier("clore : routage ouvert retiré, une ligne vers l'index", "|---|---|\n| relire un chantier clos | `ctx/00-INDEX.md` — sa ligne y nomme le fichier de fiches |\n| relire le chantier E" in lire(os.path.join(t, "CLAUDE.md"))
             and "chantier Q" not in lire(os.path.join(t, "CLAUDE.md")).split("## Routage")[1], lire(os.path.join(t, "CLAUDE.md")))
    pq = lire(page_q)
    verifier("clore : ZONE:bilan visible, blocage caché", "<section>\n    <h2>Chantier clos le 2026-05-06</h2>\n    <div class=\"bilan\">\n      <p>Livré : Livré `a` &lt;b&gt;</p>\n      <p>Surpris : x &lt; y</p>\n    </div>\n  </section>" in pq
             and pq.split("<!-- ZONE:blocage")[1].split("-->\n")[1].startswith("  <section hidden>") and pq.count("<section hidden>") == 1, pq)
    verifier("clore : bilan", code == 0 and "CLOS Q Q1..Q2 (Q2 abandonnée) · total 3 812" in s and "encours non" in s, s)
    verifier("clore : fichier de fiches", "**CLOS** le 2026-05-06. Ne se rejoue pas" in fiches_lues
             and fiches_lues.index("**CLOS**") < fiches_lues.index("**Fait.**") and "Abandonnées : Q2 abandonnée." in fiches_lues, fiches_lues)
    verifier("clore : CHANTIER.md", "**fichier de fiches courant** : aucun" in carte_lue and "**artefact du chantier** : aucun" in carte_lue
             and "| ctx/10-e.md | E1..E2 | 2026-01-01 | u |\n\nFin." in carte_lue and "| ctx/30-q.md |" not in carte_lue
             and "M (Deux `x`), Q (Un `titre`). Un nouveau chantier" in carte_lue, carte_lue)
    clos = html.split("<!-- ZONE:clos")[1]
    verifier("clore : feuille de route", '<a href="https://exemple/q">Un <span class="mono">titre</span></a>' in clos
             and '<td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>' in clos and "≈1,5k (1 500)" in clos
             and "Livré <span class=\"mono\">a</span> &lt;b&gt;" in clos and clos.index("Q1–Q2") < clos.index("2 312")
             and "<strong>≈3,8k (3 812)</strong>" in clos and "Aucun chantier ouvert" in html and "E, M, Q</span>" in html, clos)
    verifier("clore : estimation en dollars au pied de table",
             '<strong>≈3,8k (3 812)</strong></td><td class="mono">≈0,00 $</td>' in clos, clos)
    verifier("clore : résumé du bloc repliable des clos",
             '<span class="resume-clos">2 chantiers clos · ≈3,8k (3 812) tokens · ≈0,00 $</span>' in clos, clos)
    verifier("clore : la table des clos reste dans un details repliable",
             '<details class="clos">' in clos and "</details>" in clos, clos)
    code, s = appel(["clore", t, "--livre", "x"])
    verifier("clore : second appel refusé", code == 1 and s.startswith("GARDE: aucun chantier ouvert")
             and lire(os.path.join(t, "CHANTIER.md")) == carte_lue, s)

with tempfile.TemporaryDirectory() as t:
    lire = lambda c: open(c, encoding="utf-8").read()
    carte_o = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : %s\n- **artefact du chantier** : %s\n")
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n| `05-d.md` | vieux |\n\nFin.\n")
    ecrire(os.path.join(t, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n| relire le chantier E (e) | `ctx/10-e.md` — chantier **clos** |\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
    carte_lue, index_lu, claude_lu = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "00-INDEX.md")), lire(os.path.join(t, "CLAUDE.md"))
    verifier("ouvrir : bilan", code == 0 and s == "OUVERT Q Q1..Q2 · index +1 · routage +1 · artefact aucun — %s\n" % t, s)
    verifier("ouvrir : CHANTIER.md", "**fichier de fiches courant** : ctx/30-q.md (Q1..Q2)\n- **artefact du chantier** : aucun\n" in carte_lue, carte_lue)
    verifier("ouvrir : index, après le plus grand numéro", "| `10-e.md` | on relit |\n| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q2` |\n| `05-d.md`" in index_lu, index_lu)
    verifier("ouvrir : routage, avant « relire un chantier clos »", "**clos** |\n| jouer une fiche du chantier Q (un `titre`) | `ctx/30-q.md` — chantier **ouvert**, par `/vlp:tache Q<n>` |\n| relire" in claude_lu, claude_lu)
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`", "--artefact", "https://exemple/q"])
    verifier("ouvrir : relance, artefact seul", code == 0 and "index +0 · routage +0 · artefact https://exemple/q" in s
             and lire(os.path.join(t, "CLAUDE.md")) == claude_lu and lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_lu
             and "**artefact du chantier** : https://exemple/q" in lire(os.path.join(t, "CHANTIER.md")), s)
    avant = lire(os.path.join(t, "CHANTIER.md"))
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
    verifier("ouvrir : relance sans artefact, rien ne change", code == 0 and lire(os.path.join(t, "CHANTIER.md")) == avant, s)
    ecrire(os.path.join(t, "ctx", "31-r.md"), "# Chantier R — r\n\n## R1 [ ] — a\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
    verifier("ouvrir : autre chantier ouvert, refus", code == 1 and s.startswith("GARDE: un chantier est déjà ouvert")
             and lire(os.path.join(t, "CHANTIER.md")) == avant, s)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    os.remove(os.path.join(t, "CLAUDE.md"))
    code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
    verifier("ouvrir : CLAUDE.md absent, garde, le reste écrit", code == 0 and "GARDE: CLAUDE.md introuvable" in s
             and "routage +0" in s and "index +1" in s and "ctx/31-r.md (R1..R1)" in lire(os.path.join(t, "CHANTIER.md")), s)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    ecrire(os.path.join(t, "ctx", "32-s.md"), "# Chantier S — s\n\n**CLOS** le 2026-01-01. Ne se rejoue pas.\n\n## S1 [x] — a\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/32-s.md", "--titre", "s"])
    verifier("ouvrir : fichier CLOS, refus sans écrire", code == 1 and s.startswith("GARDE: ctx/32-s.md porte **CLOS**")
             and "aucun" in lire(os.path.join(t, "CHANTIER.md")), s)

with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "y.md")
    ecrire(f, SANS)
    verifier("cout : aucune session", appel(["cout", f]) == (0, "SESSIONS 0 — pas de total\n"), appel(["cout", f]))
    ecrire(f, AVEC)
    for s_ in ("aaa", "bbb", "ccc"):
        os.makedirs(os.path.join(t, ".claude", "projects", "p"), exist_ok=True)
        transcript(os.path.join(t, ".claude", "projects", "p", s_ + ".jsonl"), 2)
    garde_env = dict(os.environ)
    os.environ.update(HOME=t, USERPROFILE=t, CLAUDE_CODE_SESSION_ID="ccc")
    try:
        code, s = appel(["cout", f])
        verifier("cout : toutes les sessions du fichier, un total", code == 0 and "aaa.jsonl\t" in s and "bbb.jsonl\t" in s
                 and "ccc.jsonl\t" not in s and s.count("TOTAL\t") == 1, s)
        code, s = appel(["cout", f, "--session"])
        verifier("cout --session : la session seule, puis le cumul", code == 0 and s.startswith("SESSION=ccc\nfichier\t")
                 and s.split("TOTAL\t")[0].count("ccc.jsonl\t") == 3 and s.count("TOTAL\t") == 1, s)
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        verifier("cout --session : id vide, rien mesuré", appel(["cout", f, "--session"]) == (0, "SESSION=\n"), appel(["cout", f, "--session"]))
    finally:
        os.environ.clear()
        os.environ.update(garde_env)
    code, s = appel(["valider", f, "--plan"])
    verifier("valider --plan : titres de fiche, grep -n", s.endswith("\n12:## Y1 [x] — faite\n24:## Y2 [ ] — à faire\n")
             and "pas un titre" not in s, s)
    code, s = appel(["lignes", f, t, os.path.join(t, "absent.md"), os.path.join(t, "*.md")])
    verifier("lignes : fichier, dossier, absent, motif", code == 0 and s == "%d %s\nDOSSIER %s\nABSENT %s\n%d %s\nSEUILS page %d · fiche %d · socle %d\n"
             % (len(mod.lignes_de(f)), f, t, os.path.join(t, "absent.md"), len(mod.lignes_de(f)), f, mod.SEUIL_PAGE, mod.SEUIL_FICHE, mod.SEUIL_SOCLE), s)
    d = os.path.join(t, "projet")
    for n in ("b", "A", ".cache"):
        os.makedirs(os.path.join(d, n))
    ecrire(os.path.join(d, "CLAUDE.md"), "# C\n")
    verifier("equiper : dossier, sous-dossiers, CLAUDE.md, carte, état",
             appel(["equiper", d]) == (0, "DOSSIER=%s\nA/\nb/\nCLAUDE.md\nAUCUN_PROJET\nETAT=01-etat.md\n" % os.path.abspath(d)),
             appel(["equiper", d]))

# --- chantier U : lire, cocher, page déduite ----------------------------------

attendu = mod.lire(os.path.join(mod.KIT, "cloture.md"))
attendu = attendu if attendu.endswith("\n") else attendu + "\n"
verifier("lire : un fichier du kit, tel quel", appel(["lire", "cloture.md"]) == (0, attendu), appel(["lire", "cloture.md"])[1][:200])
code, s = appel(["lire", "cloture.md", "../hors.md", "absent.md", "cloture.md"])
verifier("lire : hors du kit et absent sortent 1, le reste imprimé", code == 1
         and s == attendu + "GARDE: hors du kit : ../hors.md\nABSENT absent.md\n" + attendu, s[-200:])

COCHE = """## L'ordre des fiches

<!-- FICHE:U1 -->
## U1 [ ] — Première
**Tentatives** (2026-01-01) — non résolu.
1. essai un
2. essai deux
Erreur : boum
**Dépend de** : rien.
**Prompt**
<!-- /FICHE -->
<!-- FICHE:U2 -->
## U2 [ ] — Seconde
**Dépend de** : `U1`.
<!-- /FICHE -->
"""

with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "ctx", "05-u.md")
    ecrire(f, COCHE)
    garde_env = dict(os.environ)
    try:
        os.environ["CLAUDE_CODE_SESSION_ID"] = "abc"
        code, s = appel(["cocher", f, "U1", "--resolu", "lire par vlp.py", "--date", "2026-01-02"])
        verifier("cocher : coche, Tentatives réduit, Session avant Dépend de", code == 0 and s == "COCHÉ U1 · Session abc\n"
                 and lire(f) == COCHE.replace("## U1 [ ]", "## U1 [x]").replace(
                     "**Tentatives** (2026-01-01) — non résolu.\n1. essai un\n2. essai deux\nErreur : boum\n",
                     "**Tentatives** (2026-01-02) — résolu par : lire par vlp.py\n**Session** : abc\n"), s + lire(f))
        avant = lire(f)
        code, s = appel(["cocher", f, "U1"])
        verifier("cocher : déjà cochée, refus sans écrire", code == 1 and s == "GARDE: U1 déjà cochée — rien écrit\n"
                 and lire(f) == avant, s)
        verifier("cocher : fiche introuvable", appel(["cocher", f, "U9"]) == (1, "GARDE: fiche introuvable : U9\n"), appel(["cocher", f, "U9"]))
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        code, s = appel(["cocher", f, "U2"])
        verifier("cocher : id vide, pas de ligne Session", code == 0 and s == "COCHÉ U2 · Session absente\n"
                 and lire(f) == avant.replace("## U2 [ ]", "## U2 [x]"), s + lire(f))
    finally:
        os.environ.clear()
        os.environ.update(garde_env)

    ecrire(f, PAGE % (" ", "", " ", ""))
    page = os.path.join(t, "ctx", "artefacts", "05-u.html")
    code, s = appel(["page", f, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R", "--date", "2026-01-02"])
    verifier("page sans chemin : artefacts/<même nom>.html, dossier créé", code == 0 and os.path.isfile(page)
             and s.startswith("PAGE %s · 3 fiches" % page), s)
    code, s = appel(["page", f, "--verifier"])
    verifier("page --verifier sans chemin : la même page", code == 0 and s.startswith("À JOUR 3 fiches"), s)

# --- Z2 : un chemin de CHANTIER.md ne fait plus tomber une sous-commande ---
# Un cas par ligne « plante » de la table de Z1, plus le point de lecture unique.
GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")
ETAT_Z = ("# État\n\n## TODO\n\n| n° | Chantier | Apport | Coût | Décidé |\n|---|---|---|---|---|\n"
          "| 1 | un truc | utile | bas | 2026-01-02 |\n")
CARTE_Z = ("# Chantier courant\n\n- **alias** : z\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **fichier de fiches courant** : %s\n"
           "- **artefact du chantier** : aucun\n")

with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "proj")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z % "ctx/absent.md (Z1..Z2)")
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
    os.makedirs(os.path.join(proj, "ctx", "artefacts"))
    shutil.copy(GABARIT_FEUILLE, os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"))
    manque = "GARDE: fichier de fiches introuvable : ctx/absent.md\n"

    code, s = appel(["carte", proj])
    verifier("Z2 carte : fiches courant absent, GARDE et 1", code == 1 and manque in s, s)
    code, s = appel(["feuille", proj])
    verifier("Z2 feuille : fiches courant absent, GARDE et 1 (plantait)",
             code == 1 and s == "GARDE: fichier de fiches courant introuvable : ctx/absent.md\n", s)
    code, s = appel(["clore", proj, "--livre", "rien"])
    verifier("Z2 clore : fiches courant absent, GARDE et 1 (plantait)", code == 1 and s == manque, s)
    code, s = appel(["ouvrir", proj, "--fiches", "ctx/absent.md", "--titre", "T"])
    verifier("Z2 ouvrir : fiches absent, GARDE et 1", code == 1 and s == manque, s)

    absent = os.path.join(proj, "ctx", "absent.md")
    for sous in (["extraire", absent, "Z1"], ["socle", absent], ["cocher", absent, "Z1"],
                 ["cout", absent], ["page", absent]):
        code, s = appel(sous)
        verifier("Z2 %s : chemin absent, GARDE du point unique et 1" % sous[0],
                 code == 1 and s == "GARDE: fichier introuvable : %s\n" % absent, s)

    try:
        mod.lignes_du_projet(proj, "ctx/absent.md", "fichier de fiches")
        verifier("Z2 point unique : lève Absent", False, "rien levé")
    except mod.Absent as e:
        verifier("Z2 point unique : Absent est une ValueError, les gardes locales la voient",
                 isinstance(e, ValueError) and str(e) == "fichier de fiches introuvable : ctx/absent.md", str(e))


# Préfixe à trois lettres : le format officiel depuis le chantier RNV.
CHANTIER_3 = """# Chantier courant

- **alias** : p3
- **contexte** : ctx
- **fichier de fiches courant** : ctx/30-rnv.md (RNV1..RNV2)

Lettres de fiche déjà prises : Z (Zed), RNV (Remise à niveau). Un nouveau chantier en choisit une autre.
"""

FICHES_3 = """# Chantier RNV

## Le socle commun

rien

## L'ordre des fiches

RNV1 puis RNV2

<!-- FICHE:RNV1 -->
## RNV1 [ ] — première
**Dépend de** : rien
**Critère de fin** : rien
<!-- /FICHE -->

---

<!-- FICHE:RNV2 -->
## RNV2 [ ] — seconde
**Dépend de** : RNV1
**Critère de fin** : rien
<!-- /FICHE -->
"""

with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "p3")
    fiches3 = os.path.join(proj, "ctx", "30-rnv.md")
    ecrire(os.path.join(proj, "CHANTIER.md"), CHANTIER_3)
    ecrire(fiches3, FICHES_3)

    s3 = rendu(proj)
    verifier("3 lettres : titres lus par la carte", "## RNV1 [ ] — première" in s3, s3)
    verifier("3 lettres : PROCHAINE", s3.rstrip().endswith("PROCHAINE=RNV1"), s3)

    code, s3 = appel(["valider", fiches3])
    verifier("3 lettres : marqueurs valides", code == 0 and "VALIDE 2 fiches" in s3, s3)

    code, s3 = appel(["extraire", fiches3, "RNV2"])
    verifier("3 lettres : extraire", code == 0 and "## RNV2 [ ] — seconde" in s3, s3)

    code, s3 = appel(["cocher", fiches3, "RNV1"])
    verifier("3 lettres : cocher", code == 0 and "COCHÉ RNV1" in s3, s3)

    lettres3 = mod.lettres_prises(CHANTIER_3.splitlines())
    verifier("3 lettres : lettres prises, une et trois lettres mêlées",
             lettres3 == ["Z", "RNV"], repr(lettres3))

    verifier("3 lettres : lettre_de isole le préfixe",
             (mod.lettre_de("RNV12"), mod.lettre_de("Z3")) == ("RNV", "Z"),
             repr((mod.lettre_de("RNV12"), mod.lettre_de("Z3"))))

    verifier("3 lettres : une entrée de clos est reconnue",
             bool(mod.ENTREE_CLOS.match("- Clos le 2026-09-17 : un titre (chantier RNV).")), "non")

# NIV1 — la ligne d'injection ne laisse entrer aucun message de lanceur dans la carte.
RACINE = os.path.dirname(ICI)
lignes_injection = []
for skill in ("chantier", "tache"):
    texte = io.open(os.path.join(RACINE, "skills", skill, "SKILL.md"), encoding="utf-8").read()
    lignes_injection.append([l for l in texte.splitlines() if l.startswith("!`") and "vlp.py" in l])

verifier("NIV1 : une ligne d'injection par skill, les deux identiques",
         [len(x) for x in lignes_injection] == [1, 1] and lignes_injection[0] == lignes_injection[1],
         repr(lignes_injection))

injection = lignes_injection[0][0]
verifier("NIV1 : chaque appel de lanceur detourne sa sortie d'erreur",
         injection.count('/scripts/vlp.py" carte') == 3
         == injection.count('"${CLAUDE_PLUGIN_ROOT}/relais-python.err"')
         and injection.count('2>"') == 1 and injection.count('2>>"') == 2, injection)

verifier("NIV1 : aucune syntaxe propre a un seul shell",
         "$null" not in injection and "/dev/null" not in injection, injection)

s_niv1 = io.StringIO()
mod.carte_injectee(os.path.join(RACINE, "scripts"), "py", False, s_niv1)
lu = s_niv1.getvalue()
verifier("NIV1 : la carte ne dit que PYTHON= et le projet",
         lu.splitlines()[:2] == ["", "PYTHON=py"] and "introuvable" not in lu and "not found" not in lu
         and "PROJET=" in lu, lu[:200])

# --- NIV2 : `niveau` dit en quoi un projet équipé a dérivé du kit -------------

ETAT_NIV = ("# État\n\n"
            "Le plugin pose `${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py` — prose, pas un chemin lu.\n\n"
            "## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
            "|---|---|---|---|---|\n| 1 | un truc | utile | bas | — |\n")
CARTE_SALE = """# Chantier courant

- **alias** : sale
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **méthode** : ${CLAUDE_PLUGIN_ROOT}/methode-chantier.md
- **fichier de fiches courant** : aucun

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le |
|---|---|---|
| ctx/10-a.md | A1..A2 | 2026-01-01 |
"""
INDEX_SALE = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
              "| `99-fantome.md` | jamais, il n'existe pas |\n"
              "| *(hors dossier)* `${CLAUDE_PLUGIN_ROOT}/methode-chantier.md` | la méthode |\n")

with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "sale")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_SALE)
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_SALE)
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)

    code, s = appel(["niveau", proj])
    cat = [l.split(":")[1].strip() for l in s.splitlines() if l.startswith("ÉCART:")]
    verifier("NIV2 : les cinq catégories d'écart, sauf `page` (aucun courant)",
             code == 1 and cat == ["renvois", "feuille", "variable", "variable", "clos"], s)
    verifier("NIV2 : le renvoi absent est nommé avec sa source et sa ligne",
             "ÉCART: renvois: ctx/00-INDEX.md:5: 99-fantome.md — nommé, introuvable\n" in s, s)
    verifier("NIV2 : la feuille de route absente est un écart",
             "ÉCART: feuille: feuille de route introuvable :" in s, s)
    verifier("NIV2 : la variable est lue en champ et en cellule, jamais en prose",
             "ÉCART: variable: CHANTIER.md:7 cite ${CLAUDE_PLUGIN_ROOT}" in s
             and "08-etat.md:3" not in s, s)
    verifier("NIV2 : la table des clos est repérée à son titre",
             "ÉCART: clos: CHANTIER.md:10 —" in s, s)
    verifier("NIV2 : le poids sort brut, et le bilan compte les deux genres",
             "POIDS CLAUDE.md absent/80 · CHANTIER.md 14/50 · index 6/80\n" in s
             and s.rstrip().endswith("NIVEAU 5 écarts · 0 avertissements — %s" % proj), s)

CARTE_NETTE = """# Chantier courant

- **alias** : net
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **méthode** : methode-chantier.md, copie d'avant la règle
- **fichier de fiches courant** : aucun

## Chantiers clos — dans l'index, pas ici
"""
INDEX_NET = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
             "| `08-etat.md` | on reprend |\n")

with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "net")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE)
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
    ecrire(os.path.join(proj, "methode-chantier.md"), "la copie locale, tolérée\n")
    os.makedirs(os.path.join(proj, "ctx", "artefacts"))
    shutil.copy(GABARIT_FEUILLE, os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"))
    appel(["feuille", proj])

    code, s = appel(["niveau", proj])
    verifier("NIV2 : un projet à niveau ne sort aucun écart, et 0",
             code == 0 and "ÉCART:" not in s
             and s.rstrip().endswith("NIVEAU 0 écarts · 0 avertissements — %s" % proj), s)
    verifier("NIV2 : une copie locale de methode-chantier.md n'est pas un écart",
             "methode-chantier" not in s, s)

    ecrire(os.path.join(proj, "CLAUDE.md"), "x\n" * (mod.SEUIL_CLAUDE + 1))
    code, s = appel(["niveau", proj])
    verifier("NIV2 : un fichier de tête trop lourd avertit, il ne fait pas un écart",
             code == 0 and "AVERTISSEMENT: poids: CLAUDE.md %d lignes > %d\n"
             % (mod.SEUIL_CLAUDE + 1, mod.SEUIL_CLAUDE) in s
             and "NIVEAU 0 écarts · 1 avertissements" in s, s)

    code, s = appel(["niveau", os.path.join(t, "pas-un-projet")])
    verifier("NIV2 : sans CHANTIER.md, une GARDE et 1",
             code == 1 and s.startswith("GARDE: pas de CHANTIER.md dans "), s)

# `niveau` lit les chemins du projet par le point unique : il hérite des GARDE.
with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "garde")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE.replace("ctx/00-INDEX.md", "ctx/absent.md"))
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
    code, s = appel(["niveau", proj])
    verifier("NIV2 : un chemin de CHANTIER.md introuvable rend une GARDE, pas un traceback",
             code == 1 and "GARDE: index introuvable : ctx/absent.md\n" in s, s)

print("OK")
