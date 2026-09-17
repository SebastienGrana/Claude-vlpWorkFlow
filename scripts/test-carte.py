#!/usr/bin/env python3
"""Teste carte.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle `carte`, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import importlib.util
import io
import os
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("carte", os.path.join(ICI, "carte.py"))
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

print("OK")
