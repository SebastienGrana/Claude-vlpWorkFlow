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
code, s = appel(["valider", "absent-1.md", "absent-2.md"])
verifier("valider : un bilan par fichier", code == 1 and s.count("INVALIDE 0 fiches") == 2, s)

print("OK")
