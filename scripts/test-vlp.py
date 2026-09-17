#!/usr/bin/env python3
"""Teste vlp.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle les sous-commandes, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import importlib.util
import io
import os
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

print("OK")
