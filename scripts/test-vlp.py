#!/usr/bin/env python3
"""Teste vlp.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle les sous-commandes, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import datetime
import glob
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

for _flux in (sys.stdout, sys.stderr):
    try:
        if isinstance(_flux, io.TextIOWrapper):
            _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("vlp", os.path.join(ICI, "vlp.py"))
assert spec and spec.loader
mod: Any = importlib.util.module_from_spec(spec)  # ses attributs, GIT compris, se lisent et se changent
spec.loader.exec_module(mod)

# Les tests rejouent des entrées identiques : le tampon de hook serait créé une fois,
# et les rejoues se tairaient. `TAMPON_HOOKS = None` : toujours vrai (FIL3, PYT1).
mod.TAMPON_HOOKS = None

# `ouvrir` et `cocher` notent CLAUDE_CODE_SESSION_ID : un test le fixe lui-même, jamais celui de la
# session qui lance la suite (chantier CAD).
os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
# Une fiche jouée la nuit lance la suite sous `VLP_NUIT=1` : `carte` imprimerait `NUIT=1` partout et
# `plan ecrire` refuserait. Un test le fixe lui-même (NUI12).
os.environ.pop("VLP_NUIT", None)

CHANTIER ="# Chantier courant\n\n- **alias** : %s\n- **fichier de fiches courant** : %s\n"
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


ECARTS = []     # avec VLP_TOUS_ECARTS=1 (`vlp.py mutant`), un écart n'arrête pas la suite (chantier MUT)


def verifier(nom, cond, sortie):
    if not cond:
        print("ÉCART:", nom)
        print(sortie)
        if os.environ.get("VLP_TOUS_ECARTS") != "1":
            sys.exit(1)
        ECARTS.append(nom)


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
    verifier("aucun courant", "--- fichier de fiches courant : aucun ---\n" in s and "TODO=absente (pas de ligne « chantiers possibles »)" in s, s)

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


def test_carte_relecteur():
    """REL2 : `carte --relecteur` tait les titres de fiches et `PROCHAINE=` ; sans l'option, rien ne change."""
    with tempfile.TemporaryDirectory() as bac:
        pr = os.path.join(bac, "pr")
        ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/20-z.md (ZZZ1..ZZZ2)"))
        ecrire(os.path.join(pr, "context AI", "20-z.md"),
               "# Chantier ZZZ\n\n## ZZZ1 [ ] — à relire\n---\n## ZZZ2 [x] — piège\n")
        s = rendu(pr)
        verifier("carte sans --relecteur : titres et PROCHAINE inchangés",
                 s.endswith("--- fiches : context AI/20-z.md (5 lignes, 2 titres) ---\n"
                            "3:## ZZZ1 [ ] — à relire\n5:## ZZZ2 [x] — piège\nPROCHAINE=ZZZ1\n"), s)
        r = io.StringIO()
        mod.carte(pr, r, relecteur=True)
        r = r.getvalue()
        verifier("carte --relecteur : ni titre ni PROCHAINE=, mais PROJET=",
                 "piège" not in r and "PROCHAINE=" not in r and "PROJET=%s\n" % pr in r, r)
        verifier("carte --relecteur : ni l'étendue des fiches (dette REL), mais le chemin",
                 "ZZZ2" not in r and "- **fichier de fiches courant** : context AI/20-z.md\n" in r, r)
        verifier("carte --relecteur : le reste à l'octet près",
                 s.replace(" (ZZZ1..ZZZ2)", "").startswith(r) and "- **alias** : pr" in r, r)
        j = io.StringIO()
        mod.carte_injectee(pr, "py", False, j, relecteur=True)
        j = j.getvalue()
        verifier("carte --python --relecteur : l'option passe l'injection",
                 j.startswith("\nPYTHON=py\n") and "piège" not in j and "PROCHAINE=" not in j, j)


def test_carte_todo():
    """LEC2 : la TODO des chantiers possibles, quand aucun chantier n'est ouvert."""
    with tempfile.TemporaryDirectory() as t:
        pr = os.path.join(t, "pr")
        def chantier(possibles, courant="aucun"):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n"
                   "- **chantiers possibles** : %s\n- **fichier de fiches courant** : %s\n" % (possibles, courant))
        todo = lambda n: "## TODO %s\n\nTexte%s.\n## Suite\n\nFin.\n" % (n, n)

        ecrire(os.path.join(pr, "08-etat.md"), "# État\n\n## TODO première\n\nLigne 1.\nLigne 2.\n"
               "## TODO deuxième\n\nLigne TODO2.\n## Autre\n\nAprès.\n## Quatre\n\nFin.\n")
        chantier("`08-etat.md`")
        s = rendu(pr)
        verifier("carte TODO : premier titre TODO seul, texte jusqu'avant le titre suivant",
                 "--- TODO : 08-etat.md (lignes 3–6) ---\n## TODO première\n\nLigne 1.\nLigne 2.\n" in s
                 and "## TODO deuxième" not in s, s)

        ecrire(os.path.join(pr, "sans.md"), "# X\n\n## Un\n\nTexte.\n## Deux\n")
        chantier("`sans.md`")
        s = rendu(pr)
        verifier("carte TODO : sans titre TODO", "TODO=absente sans.md\n" in s, s)

        ecrire(os.path.join(pr, "a.md"), todo("A"))
        ecrire(os.path.join(pr, "b.md"), todo("B"))
        chantier("`a.md`, puis `b.md`")
        s = rendu(pr)
        verifier("carte TODO : deux chemins entre backticks, dans l'ordre",
                 "--- TODO : a.md (lignes 1–3) ---\n## TODO A\n\nTexteA.\n--- TODO : b.md (lignes 1–3) ---" in s, s)

        chantier("`a.md` (section TODO)")
        s = rendu(pr)
        verifier("carte TODO : prose entre parenthèses", s.count("--- TODO :") == 1 and "--- TODO : a.md " in s, s)

        chantier("`absent.md`, puis `b.md`")
        s = rendu(pr)
        verifier("carte TODO : absent → GARDE, le suivant quand même",
                 "GARDE: fichier introuvable : absent.md\n--- TODO : b.md " in s, s)

        ecrire(os.path.join(pr, "context AI", "a.md"), todo("CA"))
        ecrire(os.path.join(pr, "context AI", "b.md"), todo("CB"))
        ecrire(os.path.join(pr, "context AI", "état.md"), todo("E"))
        for possibles, attendus in (
                ("context AI/a.md, puis context AI/b.md", ["context AI/a.md", "context AI/b.md"]),
                ("voir context AI/a.md.", ["context AI/a.md"]),
                ("`a.md` ; context AI/b.md", ["a.md", "context AI/b.md"]),
                ("context AI/état.md", ["context AI/état.md"])):
            chantier(possibles)
            s = rendu(pr)
            vus = re.findall(r"^--- TODO : (.+) \(lignes", s, re.M)
            verifier("carte TODO : le disque tranche — %s" % possibles, vus == attendus and "GARDE" not in s, s)

        chantier("`a.md`", "fiches.md")
        ecrire(os.path.join(pr, "fiches.md"), "## Z1 [ ] — Fiche\n")
        s = rendu(pr)
        verifier("carte TODO : chantier ouvert, aucun bloc", "--- TODO :" not in s and "TODO=absente" not in s, s)


def test_carte_methode():
    """LEC3 : le format des fiches de la ligne **méthode**, quand aucun chantier n'est ouvert."""
    kit = mod.KIT
    with tempfile.TemporaryDirectory() as t:
        pr, faux_kit = os.path.join(t, "pr"), os.path.join(t, "kit")
        def chantier(methode):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n"
                   "- **fichier de fiches courant** : aucun\n" + ("- **méthode** : %s\n" % methode if methode else ""))
        trois = ("# M\n## Avant\nx\n## Le fichier de fiches\na\n## Anatomie d'une fiche\nb\n"
                 "## Les deux formes de critère de fin\nc\n## Après\nd\n")

        ecrire(os.path.join(pr, "m.md"), trois)
        chantier("m.md")
        s = rendu(pr)
        verifier("carte méthode : trois sections, le titre qui suit exclu",
                 "--- méthode : m.md (lignes 4–9) ---\n## Le fichier de fiches\na\n## Anatomie d'une fiche\nb\n"
                 "## Les deux formes de critère de fin\nc\n" in s and "## Après" not in s, s)

        ecrire(os.path.join(pr, "sans.md"), "# M\n## Le fichier de fiches\na\n## Anatomie d'une fiche\nb\n")
        chantier("sans.md")
        s = rendu(pr)
        verifier("carte méthode : titre de fin manquant", "METHODE=absente sans.md\n" in s and "--- méthode" not in s, s)

        ecrire(os.path.join(faux_kit, "methode-chantier.md"), trois)
        mod.KIT = faux_kit
        try:
            chantier("methode-chantier.md, à la racine du kit")
            s = rendu(pr)
            verifier("carte méthode : absente du projet, trouvée sous le kit",
                     "--- méthode : methode-chantier.md (lignes 4–9) ---\n" in s, s)
            chantier("nulle-part.md")
            s = rendu(pr)
            verifier("carte méthode : introuvable des deux côtés",
                     "GARDE: fichier introuvable : nulle-part.md\n" in s and "--- méthode" not in s, s)
        finally:
            mod.KIT = kit

        chantier(None)
        s = rendu(pr)
        verifier("carte méthode : pas de ligne", "METHODE=absente (pas de ligne « méthode »)\n" in s, s)


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

import datetime
import json

lire = mod.lire


def transcript(chemin, tours, heures=None):
    """Un jsonl de `tours` tours, 100 000 tokens d'entrée chacun, sur claude-opus-5 (5 $ le million) ;
    `heures` : celle de chaque tour, en secondes UTC — sans elles, aucun `timestamp`."""
    with open(chemin, "w", encoding="utf-8") as f:
        for n in range(tours):
            ligne = {"type": "assistant", "requestId": "r%d" % n, "message": {
                "id": "m%d" % n, "model": "claude-opus-5", "content": [],
                "usage": {"input_tokens": 100000, "output_tokens": 0,
                          "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}}
            if heures:
                ligne["timestamp"] = datetime.datetime.fromtimestamp(
                    heures[n], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            f.write(json.dumps(ligne) + "\n")


verifier("arrondi", [mod.arrondi(n) for n in (999, 1000, 999949, 999950, 1505630)] == ["999", "≈1,0k (1 000)", "≈999,9k (999 949)", "≈1,0M (999 950)", "≈1,5M (1 505 630)"],
         [mod.arrondi(n) for n in (999, 1000, 999949, 999950, 1505630)])

from decimal import Decimal

# Tout ce que ligne_cout écrit, triplet le relit : total sous et au-dessus de 1 000, prix chiffré, « ? », et négatifs.
allers = [(t, tours, u) for t in (0, 7, 999, 1000, 999999, 1000000, 123456789, -5, -1500) for tours in (0, 1, 42) for u in (None, Decimal("0"), Decimal("1.83"), Decimal("-0.05"))]
verifier("triplet relit ligne_cout", all(mod.triplet(mod.ligne_cout(*a)) == a for a in allers),
         [(a, mod.ligne_cout(*a), mod.triplet(mod.ligne_cout(*a)) == a) for a in allers if mod.triplet(mod.ligne_cout(*a)) != a])
# Le brut entre parenthèses suffit, sans l'arrondi devant : une page d'un autre format se relit.
verifier("triplet : le brut entre parenthèses suffit", mod.triplet("(5 284 442) · 42 tours · 1,83 $") == (5284442, 42, Decimal("1.83")),
         mod.triplet("(5 284 442) · 42 tours · 1,83 $"))

# total_clos : relire aussi les lignes closes sous 1 000, qui n'ont pas de parenthèses.
def ligne_close(c):
    """Une ligne close au format de cmd_clore, avec plage Q1–Q2, date 2026-05-06, et coût c."""
    return f'          <tr>\n            <td>Test <span class="badge" data-etat="clos">clos</span></td>\n            <td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>\n            <td class="mono">{c}</td>\n            <td>Test</td>\n          </tr>\n'

verifier("total_clos : une ligne close sous 1 000",
         mod.total_clos(ligne_close(mod.arrondi(950))) == 950 and
         mod.total_clos(ligne_close(mod.arrondi(1500)) + ligne_close(mod.arrondi(950))) == 2450,
         (mod.total_clos(ligne_close(mod.arrondi(950))),
          mod.total_clos(ligne_close(mod.arrondi(1500)) + ligne_close(mod.arrondi(950)))))

verifier("total_clos : ni plage, ni date, ni pied",
         mod.total_clos(ligne_close("non mesuré")) == 0 and
         mod.total_clos('<td class="mono"><strong>≈3,8k (3 812)</strong></td><td class="mono">≈0,00 $</td>') == 0,
         (mod.total_clos(ligne_close("non mesuré")),
          mod.total_clos('<td class="mono"><strong>≈3,8k (3 812)</strong></td><td class="mono">≈0,00 $</td>')))

# Un « ? $ » de l'ancienne page traverse les soustractions de couts : P1 garde son coût
# affiché, P2 prend le reste, en « ? » puisque la part de P1 en dollars est inconnue.
with tempfile.TemporaryDirectory() as t:
    s = os.path.join(t, "s.jsonl")
    transcript(s, 3)
    gardes = []
    cout, total, hors = mod.couts([("P1", "a", True, [s]), ("P2", "b", True, [s])],
                                  {"P1": ("faite", None, "≈100,0k (100 000) · 1 tours · ? $")},
                                  "Coût du chantier : ≈100,0k (100 000) · 1 tours · ? $", gardes)
    verifier("couts : « ? $ » relu sans planter",
             cout == {"P1": "≈100,0k (100 000) · 1 tours · ? $", "P2": "≈200,0k (200 000) · 2 tours · ? $"}
             and total == (300000, 3, Decimal("1.5")) and hors is None and not gardes, (cout, total, hors, gardes))

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
    page = os.path.join(t, "artefacts", "p.html")  # comme en vrai : le .md de l'abri (même dossier que la
    # page) ne collisionne pas avec le fichier de fiches, dans le dossier parent (chantier ABR)
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
             and '<p class="mono cout-total">' not in html and '<p class="mono cout-hors">' not in html
             and "Mis à jour le <span class=\"mono\">2026-01-02</span>" in html
             and "lignes · total non mesuré" in s, s + html)
    # Dette CLI : `--projet .` écrivait « . » en tête de page ; un dossier donne son alias, sinon son nom
    with tempfile.TemporaryDirectory() as tnom:
        dnom = os.path.join(tnom, "mon-projet")
        os.makedirs(dnom)
        verifier("page --creer : un dossier sans CHANTIER.md donne son nom", mod.nom_du_projet(dnom) == "mon-projet",
                 mod.nom_du_projet(dnom))
        ecrire(os.path.join(dnom, "CHANTIER.md"), "# C\n\n- **alias** : mp\n")
        verifier("page --creer : un dossier équipé donne son alias", mod.nom_du_projet(dnom) == "mp",
                 mod.nom_du_projet(dnom))
        verifier("page --creer : un nom reste un nom", mod.nom_du_projet("Proj " + tnom) == "Proj " + tnom, "")
        pnom = os.path.join(tnom, "p.html")
        appel(["page", fiches, pnom, "--creer", "--projet", dnom, "--titre", "T", "--resultat", "R"])
        verifier("page --creer : --projet <dossier> écrit l'alias en tête", '<div class="eyebrow">mp · fiches'
                 in lire(pnom) and "<title>mp — T</title>" in lire(pnom), lire(pnom)[:400])
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

    # L'en-tête suit la plage du fichier : quand on ajoute P4, la plage devient P1–P4, mais ce qui suit reste.
    ecrire(page, lire(page).replace('Proj · fiches P1–P3</div>', 'Proj · fiches P1–P3 · clos</div>'))
    ecrire(fiches, lire(fiches) + '\n<!-- FICHE:P4 -->\n## P4 [ ] — Ajoutée\n**Critère de fin**\n<!-- /FICHE -->\n')
    code, s = appel(["page", fiches, page])
    html = lire(page)
    verifier("page : l'en-tête suit la plage du fichier", code == 0 and 'Proj · fiches P1–P4 · clos</div>' in html, s + html)

    u_fiches = os.path.join(t, "u.md")
    u_page = os.path.join(t, "artefacts", "u.html")
    ecrire(u_fiches, "# Chantier U\n\n## Le socle commun\n\n## L'ordre des fiches\n\n<!-- FICHE:U1 -->\n## U1 [ ] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
    code, s = appel(["page", u_fiches, u_page, "--creer", "--projet", "Proj", "--titre", "U", "--resultat", "R."])
    u_html = lire(u_page) if os.path.exists(u_page) else ""
    verifier("page : l'en-tête d'une fiche seule", code == 0 and "Proj · fiches U1</div>" in u_html, s + u_html)

    # Un en-tête sans plage reconnue reste tel quel : ni texte libre, ni parenthèses, ni trait d'union (REV6).
    for entete in ("fiches à venir", "fiches (X1–X2)", "fiches X1-X2"):
        ecrire(u_page, u_html.replace("Proj · fiches U1</div>", "Proj · %s</div>" % entete))
        code, s = appel(["page", u_fiches, u_page])
        html = lire(u_page)
        verifier("page : un en-tête sans plage reste tel quel (%s)" % entete,
                 code == 0 and "Proj · %s</div>" % entete in html, s + html)
    ecrire(u_page, u_html)

    code, s = appel(["page", fiches, os.path.join(t, "absente.html")])
    verifier("page absente sans --creer", code == 1 and "--creer" in s, s)

# Découpe aux commits : Q1 et Q2 partagent une session horodatée, un sous-agent part pendant Q2.
# Commits : Q ouvert +100, Q1 +300, Q2 +600, Q clos +800, puis un qui ne nomme pas le préfixe.
# Tours : +50 (cadrage) et +700 (clôture) hors fiches ; +200 et +250 à Q1 ; +400 et le
# sous-agent (+450, 2 tours) à Q2 ; +1000, après le dernier commit du chantier, ne compte pas.
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

with tempfile.TemporaryDirectory() as t:
    avec, sans = os.path.join(t, "avec"), os.path.join(t, "sans")
    sq = os.path.join(t, "s.jsonl")
    transcript(sq, 6, [T0 + d for d in (50, 200, 250, 400, 700, 1000)])
    os.makedirs(os.path.join(t, "s", "subagents"))
    transcript(os.path.join(t, "s", "subagents", "agent-a1.jsonl"), 2, [T0 + 450, T0 + 460])
    for d in (avec, sans):
        ecrire(os.path.join(d, "q.md"), QFICHES % (sq, sq))
    pourquoi = []
    h = mod.heures_commits(os.path.join(sans, "q.md"), ["Q1", "Q2"], pourquoi)
    verifier("heures_commits : sans .git, rien, et pourquoi", h is None and len(pourquoi) == 1
             and pourquoi[0].startswith(("git log en échec : ", "git ne se lance pas : ")), (h, pourquoi))
    mod.GIT = "git-absent-vlp"
    pourquoi = []
    h = mod.heures_commits(os.path.join(sans, "q.md"), ["Q1", "Q2"], pourquoi)
    mod.GIT = "git"
    verifier("heures_commits : sans git, rien — jamais un traceback", h is None
             and pourquoi[0].startswith("git ne se lance pas : "), (h, pourquoi))
    if not shutil.which("git"):
        print("SAUTÉ: git absent — la découpe aux commits n'est pas testée")
    else:
        # Un dépôt à part : ni la config globale (signature, hooks) ni celle du système.
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=avec, env=env, check=True, capture_output=True)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                         (800, "Chantier Q clos : fini"), (900, "Autre : QA et Q12x ne nomment pas le préfixe")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=avec, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        h = mod.heures_commits(os.path.join(avec, "q.md"), ["Q1", "Q2"])
        verifier("heures_commits : heure d'auteur, commits qui nomment le préfixe",
                 h == ({"Q1": T0 + 300, "Q2": T0 + 600}, [T0 + 100, T0 + 300, T0 + 600, T0 + 800], [T0 + 900]), h)
        page = os.path.join(avec, "artefacts", "q.html")
        code, s = appel(["page", os.path.join(avec, "q.md"), page, "--creer", "--projet", "P", "--titre", "T",
                         "--resultat", "R", "--date", "2026-01-05"])
        html = lire(page) if os.path.exists(page) else ""
        verifier("page coupée aux commits : sous-agent compris, hors fiches à part, total = somme", code == 0
                 and '<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>' in html
                 and '<span class="cout mono">≈300,0k (300 000) · 3 tours · 1,50 $</span>' in html
                 and '<p class="mono cout-hors">Hors fiches : ≈200,0k (200 000) · 2 tours · 1,00 $</p>' in html
                 and '<p class="mono cout-total">Coût du chantier : ≈700,0k (700 000) · 7 tours · 3,50 $</p>' in html
                 and "Hors fiches : &lt;" not in html
                 and ", dont hors fiches ≈200,0k (200 000) · 2 tours · 1,00 $" in s, s + html)
        avant = lire(page)
        appel(["page", os.path.join(avec, "q.md"), page, "--date", "2026-01-05"])
        verifier("page coupée : régénérer deux fois ne change rien", lire(page) == avant, lire(page))
        # Sans .git, la même page retombe sur l'ancienne logique : Q1 garde son coût affiché, Q2 prend
        # la session moins Q1 et la part à aucune fiche ; ni sous-agent, ni ligne hors fiches.
        ecrire(os.path.join(sans, "artefacts", "q.html"), avant)
        code, s = appel(["page", os.path.join(sans, "q.md"), os.path.join(sans, "artefacts", "q.html"), "--date", "2026-01-05"])
        html = lire(os.path.join(sans, "artefacts", "q.html"))
        verifier("page sans .git : l'ancienne logique, sur l'ancienne page", code == 0
                 and html.count('<span class="cout mono">≈200,0k (200 000) · 2 tours · 1,00 $</span>') == 2
                 and '<p class="mono cout-hors">' not in html
                 and "Coût du chantier : ≈600,0k (600 000) · 6 tours · 3,00 $" in html, s + html)
        pourquoi = []
        h = mod.heures_commits(os.path.join(avec, "q.md"), ["Z1"], pourquoi)
        verifier("heures_commits : aucun commit de fiche, et pourquoi", h is None
                 and pourquoi == ["aucun commit qui nomme Z"], (h, pourquoi))
        # cout : la découpe de la page, en détail — la somme d'abord, puis session + sous-agents.
        q = os.path.join(avec, "q.md")
        code, s = appel(["cout", q])
        attendu = ("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, un sous-agent compte à son départ\n"
                   "Q1 · ≈200,0k (200 000) · 2 tours · 1,00 $ = session ≈200,0k (200 000) · 2 tours · 1,00 $ + 0 sous-agent\n"
                   "Q2 · ≈300,0k (300 000) · 3 tours · 1,50 $ = session ≈100,0k (100 000) · 1 tours · 0,50 $"
                   " + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $\n"
                   "hors fiches · ≈200,0k (200 000) · 2 tours · 1,00 $ = session ≈200,0k (200 000) · 2 tours · 1,00 $"
                   " + 0 sous-agent\n"
                   "TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours · 3,50 $ = session ≈500,0k (500 000)"
                   " · 5 tours · 2,50 $ + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $\n")
        verifier("cout coupé aux commits : une ligne par fiche, hors fiches, TOTAL", code == 0 and s == attendu, s)
        verifier("cout : triplet relit la somme de chaque ligne, celle de la page",
                 [mod.triplet(l)[:2] for l in s.splitlines()[1:]] == [(200000, 2), (300000, 3), (200000, 2), (700000, 7)], s)
        garde_env = dict(os.environ)
        os.environ["CLAUDE_CODE_SESSION_ID"] = sq
        try:
            code, s = appel(["cout", q, "--session"])
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        verifier("cout --session : la table de la session, puis la découpe", code == 0
                 and s.startswith("SESSION=%s\nfichier\t" % sq) and "\nagent-a1.jsonl\t" in s
                 and s.endswith("\n" + attendu), s)
        code, s = appel(["cout", os.path.join(sans, "q.md")])
        verifier("cout sans .git : la table d'avant, sous la raison", code == 0
                 and s.startswith("DÉCOUPE aucune — git log en échec : ") and "\ns.jsonl\t" in s
                 and "\nagent-a1.jsonl\t" in s and "\nTOTAL\t" in s, s)
        # FIN1 : dans une session qui enchaîne plusieurs chantiers, « Chantier P clos » (60) borne
        # Q par le bas — le tour de 50 ne compte nulle part ; sans clôture, hors fiches va au bout.
        multi = os.path.join(t, "multi")
        os.makedirs(multi)
        subprocess.run(["git", "init", "-q"], cwd=multi, env=env, check=True, capture_output=True)
        for d, sujet in ((60, "Chantier P clos : fini"), (100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"),
                         (600, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=multi, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        ecrire(os.path.join(multi, "q.md"), QFICHES % (sq, sq))
        code, s = appel(["cout", os.path.join(multi, "q.md")])
        verifier("cout : P clos borne Q par le bas, sans clôture hors fiches va au bout", code == 0
                 and "\nhors fiches · ≈200,0k (200 000) · 2 tours · 1,00 $ = session" in s
                 and "\nTOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours · 3,50 $ = " in s, s)
        # FIN2 : Q1 cochée, mesurée avant son commit — seule l'ouverture nomme Q. Elle part de
        # l'ouverture (100), pas du début de la session : le tour de 50 ne compte pas.
        ouv = os.path.join(t, "ouv")
        os.makedirs(ouv)
        subprocess.run(["git", "init", "-q"], cwd=ouv, env=env, check=True, capture_output=True)
        for d, sujet in ((60, "Chantier P clos : fini"), (100, "Chantier Q ouvert : cadré")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=ouv, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        ecrire(os.path.join(ouv, "q.md"), (QFICHES % (sq, "")).replace("## Q2 [x]", "## Q2 [ ]")
               .replace("**Session** : \n", ""))
        code, s = appel(["cout", os.path.join(ouv, "q.md")])
        verifier("cout : la première fiche avant son commit", code == 0
                 and "\nQ1 · ≈700,0k (700 000) · 7 tours · 3,50 $ = " in s
                 and "\nTOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s, s)
        # ZER1 : un chantier clos sans commit de fiche — sa dernière mention est sa clôture, et la
        # plage qui en part ne voit aucun tour ; son travail commité sous d'autres messages (1050),
        # hors fiches non plus. Il retombe sur les sessions entières, et le dit ; sans ligne **CLOS**,
        # la découpe reste, et une garde dit qu'elle ne garde rien.
        clq = os.path.join(t, "clq")
        os.makedirs(clq)
        subprocess.run(["git", "init", "-q"], cwd=clq, env=env, check=True, capture_output=True)
        for d, sujet in ((60, "Chantier P clos : fini"), (100, "Chantier Q ouvert : cadré"),
                         (1050, "Autre : le travail, sans nommer le préfixe"), (1100, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=clq, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        ecrire(os.path.join(clq, "q.md"), lire(os.path.join(ouv, "q.md")))
        clos_ = lambda texte: texte.replace("# Chantier Q\n", "# Chantier Q\n\n**CLOS** le 2026-01-06.\n", 1)
        ecrire(os.path.join(clq, "qz.md"), clos_(lire(os.path.join(ouv, "q.md"))))
        code, s = appel(["cout", os.path.join(clq, "qz.md")])
        verifier("cout : clos sans commit de fiche, les sessions entières, et pourquoi", code == 0
                 and s.startswith("DÉCOUPE aucune — chantier clos sans commit « Q1 : » ni d'une autre fiche : "
                                  "sessions entières, sous-agents compris\n")
                 and "\nTOTAL\t8\t0\t-\t-\t800000\t0\t0\t0\t0\t800000\t800000\t4.00\t0\n" in s, s)
        code, s = appel(["page", os.path.join(clq, "qz.md"), os.path.join(clq, "artefacts", "qz.html"), "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R", "--date", "2026-01-05"])
        html = lire(os.path.join(clq, "artefacts", "qz.html")) if code == 0 else ""
        verifier("page : clos sans commit de fiche, les sessions entières, sans hors fiches", code == 0
                 and '<p class="mono cout-hors">' not in html
                 and "Coût du chantier : ≈600,0k (600 000) · 6 tours · 3,00 $" in html, s + html)
        pourquoi = []
        h = mod.heures_commits(os.path.join(clq, "qz.md"), ["Q1", "Q2"], pourquoi, clos=True)
        verifier("heures_commits : clos sans commit de fiche, le repli et pourquoi", h is None
                 and pourquoi == ["chantier clos sans commit « Q1 : » ni d'une autre fiche"], (h, pourquoi))
        h = mod.heures_commits(os.path.join(clq, "q.md"), ["Q1", "Q2"])
        verifier("heures_commits : en cours sans commit de fiche, la découpe",
                 h == ({}, [T0 + 100, T0 + 1100], [T0 + 60, T0 + 1050]), h)
        code, s = appel(["cout", os.path.join(clq, "q.md")])
        verifier("cout : une découpe à zéro le dit", code == 0 and s.startswith(
            "GARDE: découpe à zéro — aucun tour de 2 transcripts ne tombe dans une plage\n"
            "DÉCOUPE aux commits de fiche") and "\nTOTAL (fiches + hors fiches) · 0 · 0 tours · 0,00 $ = " in s, s)
        c2 = os.path.join(t, "c2.jsonl")
        transcript(c2, 1, [T0 + 1080])
        ecrire(os.path.join(clq, "q2.md"), lire(os.path.join(clq, "q.md")).replace(
            "## Le socle commun", "**Session** : %s\n\n## Le socle commun" % c2, 1))
        code, s = appel(["cout", os.path.join(clq, "q2.md")])
        verifier("cout : fiches à zéro, un tour hors fiches — pas de garde", code == 0 and "GARDE" not in s
                 and "\nhors fiches · ≈100,0k (100 000) · 1 tours · 0,50 $ = " in s, s)
        ecrire(os.path.join(avec, "qk.md"), clos_(QFICHES % (sq, sq)))
        code, s = appel(["cout", os.path.join(avec, "qk.md")])
        verifier("cout : clos avec commits de fiche, la découpe", code == 0 and s == attendu, s)
        # CAD1 : le cadrage joué dans une autre session, notée en tête du fichier — deux tours avant
        # l'ouverture, un après la clôture : les deux premiers comptent, hors fiches.
        sc = os.path.join(t, "c.jsonl")
        transcript(sc, 3, [T0 + d for d in (20, 40, 1000)])
        qc = os.path.join(avec, "qc.md")
        ecrire(qc, (QFICHES % (sq, sq)).replace("## Le socle commun", "**Session** : %s\n\n## Le socle commun" % sc))
        code, s = appel(["cout", qc])
        verifier("cout : la session du cadrage, en tête, compte hors fiches", code == 0 and s.splitlines() == attendu.splitlines()[:3] + [
            "hors fiches · ≈400,0k (400 000) · 4 tours · 2,00 $ = session ≈400,0k (400 000) · 4 tours · 2,00 $ + 0 sous-agent",
            "TOTAL (fiches + hors fiches) · ≈900,0k (900 000) · 9 tours · 4,50 $ = session ≈700,0k (700 000) · 7 tours · 3,50 $"
            " + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $"], s)
        code, s = appel(["page", qc, os.path.join(avec, "artefacts", "qc.html"), "--creer", "--projet", "P", "--titre", "T",
                         "--resultat", "R", "--date", "2026-01-05"])
        html = lire(os.path.join(avec, "artefacts", "qc.html")) if code == 0 else ""
        verifier("page : la session du cadrage, en tête, compte hors fiches", code == 0
                 and '<p class="mono cout-hors">Hors fiches : ≈400,0k (400 000) · 4 tours · 2,00 $</p>' in html
                 and '<p class="mono cout-total">Coût du chantier : ≈900,0k (900 000) · 9 tours · 4,50 $</p>' in html, s + html)
        # REC1 : recompter lit la feuille, l'index et les fichiers clos, et n'écrit rien. Q se coupe
        # aux commits (le TOTAL de cout, 700 000) ; M partage sa session sans commit qui le nomme,
        # N n'a pas de session, P une transcription absente, K n'est pas à l'index : gardés, écart 0.
        rc = os.path.join(t, "rc")
        os.makedirs(rc)
        subprocess.run(["git", "init", "-q"], cwd=rc, env=env, check=True, capture_output=True)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                         (800, "Chantier Q clos : fini"), (900, "Autre : QA et Q12x ne nomment pas le préfixe")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=rc, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                 "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n%s**Critère de fin**\n<!-- /FICHE -->\n")
        ecrire(os.path.join(rc, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(rc, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `q.md` | chantier **clos** « Q », `Q1..Q2` |\n| `m.md` | chantier **clos** « M », `M1..M1` |\n"
               "| `n.md` | chantier **clos** « N », `N1..N1` |\n| `p.md` | chantier **clos** « P », `P1..P1` |\n")
        ecrire(os.path.join(rc, "ctx", "q.md"), clos_(QFICHES % (sq, sq)))
        ecrire(os.path.join(rc, "ctx", "m.md"), seule % ("M", "M", "M", "**Session** : %s\n" % sq))
        ecrire(os.path.join(rc, "ctx", "n.md"), seule % ("N", "N", "N", ""))
        ecrire(os.path.join(rc, "ctx", "p.md"), seule % ("P", "P", "P", "**Session** : rec1-transcription-absente\n"))
        ecrire(os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html"),
               '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
               + "".join(ligne_close(c).replace("Q1–Q2", pl) for pl, c in (
                   ("Q1–Q2", mod.arrondi(650000)), ("M1", mod.arrondi(300000)), ("N1", mod.arrondi(999)),
                   ("P1", mod.arrondi(2000)), ("K1–K3", mod.arrondi(1500)), ("E1–E8", "non mesurable")))
               + "        </tbody>\n      </table>\n")
        disque = lambda: {os.path.relpath(os.path.join(r, n), rc): lire(os.path.join(r, n))
                          for r, _, ns in os.walk(rc) if ".git" not in r.split(os.sep) for n in ns}
        avant = disque()
        code, s = appel(["recompter", rc])
        verifier("recompter : un clos découpé, des gardés à écart 0, la somme avec les gardés — mutants :"
                 " un gardé compté dans l'écart, la somme sans les gardés", code == 0 and s.splitlines() == [
                     "Q inscrit 650 000 · recompté 700 000 · écart +50 000 · découpe · partagée avec M",
                     "M inscrit 300 000 · recompté gardé · écart +0 · gardé — DÉCOUPE aucune (aucun commit qui nomme M)"
                     " · partagée avec Q",
                     "N inscrit 999 · recompté gardé · écart +0 · gardé — sans session",
                     "P inscrit 2 000 · recompté gardé · écart +0 · gardé — transcription absente (rec1-transcription-absente)",
                     "K inscrit 1 500 · recompté gardé · écart +0 · gardé — fichier introuvable",
                     "E inscrit 0 · recompté gardé · écart +0 · gardé — fichier introuvable",
                     "RECOMPTE 6 clos · 1 recomptés · 5 gardés · inscrit 954 499 · recompté 1 004 499 · écart +50 000"], s)
        code2, s2 = appel(["cout", os.path.join(rc, "ctx", "q.md")])
        verifier("recompter : le recompté de Q est le TOTAL de cout", code2 == 0
                 and "\nTOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s2, s2)
        verifier("recompter n'écrit rien", disque() == avant, sorted(disque()))
        # REC3 : --ecrire marque les six lignes en tête de cellule, resomme pied et résumé, puis ne
        # change plus rien.
        fr = os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fr, lire(fr).replace("      <table>\n", '      <summary><span class="resume-clos">vieux</span></summary>\n'
                                    "      <table>\n", 1).replace("      </table>\n",
               '        <tfoot>\n          <tr><td colspan="3">Total cumulé</td><td class="mono"><strong>vieux'
               '</strong></td><td class="mono">vieux</td></tr>\n        </tfoot>\n      </table>\n', 1))
        code, s = appel(["recompter", rc, "--ecrire"])
        feuille_ = lire(fr)
        corps_ = feuille_[:feuille_.find("<tfoot>")]
        verifier("recompter --ecrire : total_clos égale le recompté — mutants : la marque posée en parenthèses,"
                 " la marque dans une balise", code == 0 and mod.total_clos(corps_) == 1004499
                 and s.splitlines()[-2:] == [
                     "RECOMPTE 6 clos · 1 recomptés · 5 gardés · inscrit 954 499 · recompté 1 004 499 · écart +50 000",
                     "ÉCRIT 6 cellules · total 954 499 → 1 004 499"]
                 and '<td class="mono">recompté (REC), était 650 000 · ≈700,0k (700 000)</td>' in feuille_
                 and '<td class="mono">non recompté — sans session · (999)</td>' in feuille_
                 and '<td class="mono">non recompté — fichier introuvable · non mesurable</td>' in feuille_, s + feuille_)
        verifier("recompter --ecrire : pied et résumé resommés, sans $ (aucune ligne au prix mesuré) — mutant :"
                 " le pied non resommé", "<strong>%s</strong></td><td class=\"mono\"></td>" % mod.arrondi(1004499)
                 in feuille_ and '<span class="resume-clos">%s</span>' % mod.resume_clos(6, 1004499) in feuille_, feuille_)
        code, s = appel(["recompter", rc, "--ecrire"])
        verifier("recompter --ecrire relancé : rien ne change", code == 0 and lire(fr) == feuille_
                 and s.splitlines()[-1] == "ÉCRIT 0 cellules · total 1 004 499 → 1 004 499"
                 and "Q inscrit 700 000 · recompté 700 000 · écart +0 · découpe · partagée avec M" in s, s)
        code, s = appel(["recompter", os.path.join(t, "clq")])
        verifier("recompter : pas de CHANTIER.md, une garde", code == 1 and s.startswith("GARDE: pas de CHANTIER.md"), s)

# FIN1 : les bornes de `plages`, en fonction pure — heures (commits de fiche, qui nomment, autres).
P2, G = [("Q1", "a", True, ["s"]), ("Q2", "b", True, ["s"])], []
bornes = lambda h, f=P2: mod.plages(f, h, G)
verifier("plages : l'origine, le chantier d'avant, borne hors fiches",
         bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800], [30, 900]))
         == ([("Q1", (100, 300)), ("Q2", (300, 600))], [(30, 100), (600, 800)]), bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800], [30, 900])))
verifier("plages : sans clôture, hors fiches va au bout",
         bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600], [30]))[1] == [(30, 100), (600, mod.INFINI)],
         bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600], [30])))
verifier("plages : une mention après la clôture n'étire rien",
         bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800, 950], [30, 900]))[1] == [(30, 100), (600, 800)],
         bornes(({"Q1": 300, "Q2": 600}, [100, 300, 600, 800, 950], [30, 900])))
verifier("plages : sans commit qui nomme avant, la première fiche part de l'origine",
         bornes(({"Q1": 300, "Q2": 600}, [300, 600, 800], [30, 200]))
         == ([("Q1", (200, 300)), ("Q2", (300, 600))], [(600, 800)]), bornes(({"Q1": 300, "Q2": 600}, [300, 600, 800], [30, 200])))
verifier("plages : une mention juste avant l'ouverture y fait entrer son travail",
         bornes(({"Q1": 300}, [20, 100, 300, 800], [10]), P2[:1])[1] == [(10, 100), (300, 800)],
         bornes(({"Q1": 300}, [20, 100, 300, 800], [10]), P2[:1]))
verifier("plages : fiche à session sans commit, au bout, rien après",
         bornes(({"Q1": 300}, [100, 300], [30])) == ([("Q1", (100, 300)), ("Q2", (300, mod.INFINI))], [(30, 100)])
         and not G, (bornes(({"Q1": 300}, [100, 300], [30])), G))

# FIN2 : sans commit de fiche, la première fiche part du dernier commit qui nomme le préfixe
COCHEE, VIDE = [("Q1", "a", True, ["s"]), ("Q2", "b", False, [])], [("Q1", "a", False, [])]
verifier("plages : sans commit de fiche, la fiche cochée part de l'ouverture",
         bornes(({}, [100], [30, 900]), COCHEE) == ([("Q1", (100, mod.INFINI))], [(30, 100)]) and not G,
         (bornes(({}, [100], [30, 900]), COCHEE), G))
verifier("plages : sans commit de fiche ni session, rien",
         bornes(({}, [100], [30]), VIDE) == ([], []) and not G, (bornes(({}, [100], [30]), VIDE), G))


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

# REP1 : le gras et les liens Markdown d'une cellule — jamais dans du code cité.
gras_liens, cellule = mod.gras_et_liens, mod.cellule_md
s = gras_liens("un **mot** fort")
verifier("gras_et_liens : un gras", s == "un <strong>mot</strong> fort", s)
s = gras_liens("**a** puis **b**")
verifier("gras_et_liens : deux gras dans une cellule", s == "<strong>a</strong> puis <strong>b</strong>", s)
s = gras_liens("note **importante")
verifier("gras_et_liens : un ** sans paire, inchangé", s == "note **importante", s)
s = cellule("**le `sh` seul**")
verifier("gras_et_liens : un gras qui contient du code", s == '<strong>le <span class="mono">sh</span> seul</strong>', s)
s = cellule("`**x**` puis `**` et z**")
verifier("gras_et_liens : un ** dans du code, inchangé, jamais apparié au-dehors",
         s == '<span class="mono">**x**</span> puis <span class="mono">**</span> et z**', s)
s = cellule("voir [la doc](https://exemple/a?b=1&c=2)")
verifier("gras_et_liens : un lien https, l'URL échappée dans le href",
         s == 'voir <a href="https://exemple/a?b=1&amp;c=2">la doc</a>', s)
s = gras_liens("[x](javascript:alert(1))")
verifier("gras_et_liens : un lien javascript:, inchangé", s == "[x](javascript:alert(1))", s)
s = cellule("`[t](https://u)`")
verifier("gras_et_liens : un lien dans du code, inchangé", s == '<span class="mono">[t](https://u)</span>', s)
s = cellule("**voir [la doc](https://u) et `x`** puis **y")
verifier("gras_et_liens : deux passes = une, un gras englobe lien et code", gras_liens(s) == s
         and s == '<strong>voir <a href="https://u">la doc</a> et <span class="mono">x</span></strong> puis **y', s)
s = gras_liens("[A](https://w/A_(b))")
verifier("gras_et_liens : des parenthèses équilibrées dans l'URL", s == '<a href="https://w/A_(b)">A</a>', s)
s = gras_liens('[t](https://u"x)')
verifier("gras_et_liens : un guillemet dans l'URL, inchangé", s == '[t](https://u"x)', s)
s = gras_liens('<td>**a</td><td>b**</td><a href="https://x/**y">t**</a>')
verifier("gras_et_liens : une autre balise borne le gras, ses attributs intacts",
         s == '<td>**a</td><td>b**</td><a href="https://x/**y">t**</a>', s)

def tester_bilan_md_clore(page_q):
    """Dans une fonction : au niveau du module, pyright jugeait le fichier trop complexe (ABR3)."""
    bilan_md = mod.lire_abri(mod.chemin_abri(page_q))["bilan"]
    verifier("clore : bilan écrit dans le .md, estimé résolu — mutant : écrire avant de remplacer ESTIME_A_ECRIRE",
             bilan_md == ["Livré : Livré `a` <b>", "Surpris : x < y",
                          "Estimé : estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $"]
             and "\x00" not in "\n".join(bilan_md), bilan_md)


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
    verifier("feuille : TODO rendue", '<span class="gauche"><span class="rang mono">3</span></span><details><summary>'
             '<span class="titre">Le <span class="mono">sh</span></span></summary><div class="detail">a || b &lt;c&gt;</div>'
             '</details><span class="meta mono">2 fiches</span></li>' in html
             and "&lt;U, R&gt;" not in html and 'data-etat="cours"' not in html.split("ZONE:todo")[1], html)
    avant_todo = html.split("<!-- ZONE:todo")[0].split("Les chantiers possibles")[1]
    verifier("feuille : décompte au-dessus de la TODO, détaillé (FEU8)", avant_todo.count("resume-todo") == 1
             and "><strong>2 chantiers possibles</strong> · 1 petit, 1 moyen · 1 bloqué · ≈3 fiches estimées</p>" in avant_todo
             and "&lt;n&gt; chantiers possibles" not in html, html)
    code, s = appel(["feuille", t, "--date", "2026-03-04"])
    verifier("feuille : idempotente, date gardée", code == 0 and "inchangée" in s and "2026-01-02" in lire(fdr), s)
    ecrire(fdr, mod.RESUME_TODO.sub("", lire(fdr)))
    code, s = appel(["feuille", t, "--date", "2026-01-02"])
    verifier("feuille : décompte posé sur une feuille d'avant", code == 0 and lire(fdr).count("resume-todo") == 1
             and ("><strong>2 chantiers possibles</strong> · 1 petit, 1 moyen · 1 bloqué · ≈3 fiches estimées</p>\n    <!-- ZONE:todo"
                  in lire(fdr)), s + lire(fdr))
    verifier("feuille : décompte au singulier et vide",
             mod.resume_todo(1) == "1 chantier possible" and mod.resume_todo(0) == "aucun chantier possible", "")
    ecrire(os.path.join(t, "CHANTIER.md"), carte_ % ("ctx/30-q.md (Q1..Q2)", "https://exemple/q"))
    code, s = appel(["feuille", t, "--verifier"])
    verifier("feuille : --verifier voit l'écart sans écrire", code == 1 and "écart" in s and "Aucun chantier" in lire(fdr), s)
    code, s = appel(["feuille", t, "--todo", "4", "--date", "2026-03-04"])
    html = lire(fdr)
    verifier("feuille : ouvert, badge, lettre", code == 0 and "encours oui · lettres 3" in s
             and 'Un titre <span class="badge" data-etat="cours">' in html and '<span class="mono">Q1–Q2</span>' in html
             and 'href="https://exemple/q"' in html and "E, M, Q" in html
             and ('<span class="rang mono">4</span>' + mod.BADGE_COURS + '<span class="dep mono">← 3</span></span>'
                  '<details><summary><span class="titre">Quatre</span></summary>') in html, s + html)
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
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un `titre`\n\n**À quoi il sert.** x\n\n**Estimé.** 2 fiches · ≈0,40 $ — ≈0,20 $/fiche sur 3 clos (le 2026-05-01).\n\n**Fait.** Rien.\n\n## Q1 [x] — a\n## Q2 [ ] — b\n")
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
    verifier("clore : routage, index, bilan, résumé comptés", "· routage 1 · index 1 · archivé 1 · bilan 1 · résumé 1 ·" in s and "GARDE" not in s, s)
    verifier("clore : résumé, une ligne par clos", "- Clos le 2026-05-06 : a (chantier E).\n- Clos le 2026-05-06 : b `c` (chantier Q).\n\n## Routage" in lire(os.path.join(t, "CLAUDE.md")), lire(os.path.join(t, "CLAUDE.md")))
    cl, gr = ["## Où on en est", "", "- Clos le 2026-01-01 : a (chantier E).", "", "## Règles"], []
    verifier("résumé : ligne ajoutée après la dernière", mod.resume_claude(cl, "Q", "b", "2026-02-02", gr)
             and cl[3] == "- Clos le 2026-02-02 : b (chantier Q)." and cl[2].endswith("E).") and not gr, cl)
    cl2 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."]
    verifier("résumé : suffixe (chantier Q) déjà dans le texte, pas doublé", mod.resume_claude(cl2, "Q", "b (chantier Q).", "2026-01-01", gr)
             and cl2[-1] == "- Clos le 2026-01-01 : b (chantier Q).", cl2)
    cl5 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."]
    verifier("résumé : préfixe Clos le déjà dans le texte, pas doublé", mod.resume_claude(cl5, "Q", "Clos le 2026-09-27 : b.", "2026-09-27", gr)
             and cl5[-1] == "- Clos le 2026-09-27 : b (chantier Q).", cl5)
    verifier("résumé : déjà là, rien", not mod.resume_claude(cl, "Q", "b", "2026-02-02", gr) and len(cl) == 6, cl)
    cl3 = ["## Où on en est", "- Prouvé : x.", "  puis vieux (chantier A) ;"] + ["- Clos le 2026-01-0%d : c%d (chantier %s)." % (i, i, "BCDEF"[i - 1]) for i in range(1, 6)] + ["", "## R"]
    verifier("résumé : garde les CLOS_GARDES derniers, le plus ancien sorti", mod.resume_claude(cl3, "G", "g", "2026-01-09", gr)
             and mod.CLOS_GARDES == 5 and not any("(chantier B)" in l for l in cl3) and cl3[:3] == ["## Où on en est", "- Prouvé : x.", "  puis vieux (chantier A) ;"]
             and sum(1 for l in cl3 if l.startswith("- Clos le")) == 5 and cl3[-3] == "- Clos le 2026-01-09 : g (chantier G).", cl3)
    verifier("résumé : section absente, garde", not mod.resume_claude(["# x"], "Q", "b", "d", gr) and gr and "Où on en est" in gr[0], gr)
    cl4, g4 = ["## Où on en est", "- Clos le 2026-01-01 : a (chantier E)."], []
    verifier("résumé : sur une ligne, relu par ENTREE_CLOS",
             mod.resume_claude(cl4, "Q", "deux lignes\nici.\n", "2026-09-24", g4)
             and cl4[-1] == "- Clos le 2026-09-24 : deux lignes ici (chantier Q)."
             and bool(mod.ENTREE_CLOS.match(cl4[-1])) and not g4, repr(cl4[-1]))
    verifier("clore : Fait. remplacé", "**Fait.** Q1..Q2 (2026-05-06) : Livré `a` <b> — estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $.\n" in fiches_lues and "**Fait.** Rien." not in fiches_lues, fiches_lues)
    ligne_q = "| `30-q.md` | on relit le socle du chantier Q — **clos** « Un (vrai) titre », `Q1..Q2` |\n"
    verifier("clore : index clos, passé à l'archive — mutant : clore n'appelle pas archiver",
             lire(os.path.join(t, "ctx", "00-INDEX.md")).split("---|\n")[1].startswith("| `00-INDEX-archive.md` |") and "**clos**" not in lire(os.path.join(t, "ctx", "00-INDEX.md"))
             and lire(os.path.join(t, "ctx", "00-INDEX-archive.md")).split("---|\n")[1] == ligne_q, lire(os.path.join(t, "ctx", "00-INDEX.md")))
    verifier("clore : routage ouvert retiré, une ligne vers l'index", "|---|---|\n| relire un chantier clos | `ctx/00-INDEX-archive.md` — sa ligne y nomme le fichier de fiches |\n| relire le chantier E" in lire(os.path.join(t, "CLAUDE.md"))
             and "chantier Q" not in lire(os.path.join(t, "CLAUDE.md")).split("## Routage")[1], lire(os.path.join(t, "CLAUDE.md")))
    pq = lire(page_q)
    verifier("clore : ZONE:bilan visible, blocage caché", "<section>\n    <h2>Chantier clos le 2026-05-06</h2>\n    <div class=\"bilan\">\n      <p>Livré : Livré `a` &lt;b&gt;</p>\n      <p>Surpris : x &lt; y</p>\n      <p>Estimé : estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $</p>\n    </div>\n  </section>" in pq
             and pq.split("<!-- ZONE:blocage")[1].split("-->\n")[1].startswith("  <section hidden>") and pq.count("<section hidden>") == 1, pq)
    verifier("clore : la page régénérée, fiches du fichier", '<span class="id">Q1</span>' in pq and '<span class="id">Q2</span>' in pq
             and '<span class="id">&lt;R' not in pq and '<p class="mono cout-total">' not in pq, pq)
    tester_bilan_md_clore(page_q)
    verifier("clore : bilan", code == 0 and "CLOS Q Q1..Q2 (Q2 abandonnée) · chantier 1 500 · cumul 3 812 · routage 1 · index 1 · archivé 1 · bilan 1 · résumé 1 · estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $ — " in s and "encours non" in s, s)
    verifier("clore : fichier de fiches", "**CLOS** le 2026-05-06. Ne se rejoue pas" in fiches_lues
             and fiches_lues.index("**CLOS**") < fiches_lues.index("**Fait.**") and "Abandonnées : Q2 abandonnée." in fiches_lues, fiches_lues)
    verifier("clore : CHANTIER.md", "**fichier de fiches courant** : aucun" in carte_lue and "**artefact du chantier** : aucun" in carte_lue
             and "| ctx/10-e.md | E1..E2 | 2026-01-01 | u |\n\nFin." in carte_lue and "| ctx/30-q.md |" not in carte_lue
             and "M (Deux `x`), Q (Un `titre`). Un nouveau chantier" in carte_lue, carte_lue)
    clos = html.split("<!-- ZONE:clos")[1]
    verifier("clore : feuille de route", '<a href="https://exemple/q">Un <span class="mono">titre</span></a>' in clos
             and '<td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>' in clos and "≈1,5k (1 500)" in clos
             and "Livré <span class=\"mono\">a</span> &lt;b&gt;" in clos and clos.index("Q1–Q2") < clos.index("2 312", clos.index("<tbody>"))
             and "<strong>≈3,8k (3 812)</strong>" in clos and "Aucun chantier ouvert" in html and "E, M, Q</span>" in html, clos)
    verifier("clore : pied de table sans $ — aucune ligne n'a de prix mesuré (chantier TAU)",
             '<strong>≈3,8k (3 812)</strong></td><td class="mono"></td>' in clos, clos)
    verifier("clore : résumé du bloc repliable des clos, coût non mesuré",
             '<span class="resume-clos">2 chantiers clos · ≈3,8k (3 812) tokens · coût non mesuré</span>' in clos, clos)
    verifier("clore : la table des clos reste dans un details repliable",
             '<details class="clos">' in clos and "</details>" in clos, clos)
    code, s = appel(["clore", t, "--livre", "x"])
    verifier("clore : second appel refusé", code == 1 and s.startswith("GARDE: aucun chantier ouvert")
             and lire(os.path.join(t, "CHANTIER.md")) == carte_lue, s)

# archiver : les lignes clos quittent l'index pour l'archive, telles quelles (chantier IDX)
def test_archiver():
    with tempfile.TemporaryDirectory() as ta:
        def lu(c):
            with open(c, encoding="utf-8", newline="") as fh:
                return fh.read()
        def pose(c, x):
            os.makedirs(os.path.dirname(c), exist_ok=True)
            with open(c, "w", encoding="utf-8", newline="") as fh:
                fh.write(x)
        pose(os.path.join(ta, "CHANTIER.md"), "# C\n\n- **index** : ctx/00-INDEX.md\n")
        clos_a = "| `41-b.md` | on relit le socle du chantier B — **clos** « Bé  (deux blancs) », `B1..B2` |"
        clos_b = "| `39-a.md` | on relit le socle du chantier A — **clos** « A », `A1..A3` |"
        ouvert = "| `42-c.md` | on joue une fiche `C*` — chantier **ouvert** « C », `C1..C2` |"
        pose(os.path.join(ta, "ctx", "00-INDEX.md"), "# I\n\n| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | on reprend |\n%s\n%s\n%s\n" % (clos_a, clos_b, ouvert))
        code, s = appel(["archiver", ta])
        idx_a, arch_a = lu(os.path.join(ta, "ctx", "00-INDEX.md")), lu(os.path.join(ta, "ctx", "00-INDEX-archive.md"))
        verifier("archiver : 2 clos déplacés, l'ouvert reste", code == 0 and s.startswith("ARCHIVÉ 2 · index 7 lignes · archive 8 lignes")
                 and ouvert in idx_a and "**clos**" not in idx_a and idx_a.count("| `00-INDEX-archive.md` |") == 1, s + idx_a)
        verifier("archiver : lignes identiques à l'octet, triées par numéro — mutant : réécrire la ligne",
                 arch_a.endswith("|---|---|\n%s\n%s\n" % (clos_b, clos_a)) and arch_a.startswith("# ") and "QUAND LIRE" in arch_a, arch_a)
        code, s = appel(["archiver", ta])
        verifier("archiver : relancé, rien ne change — mutant : renvoi posé deux fois",
                 code == 0 and s.startswith("ARCHIVÉ 0 ·") and lu(os.path.join(ta, "ctx", "00-INDEX.md")) == idx_a
                 and lu(os.path.join(ta, "ctx", "00-INDEX-archive.md")) == arch_a, s)
        pose(os.path.join(ta, "CHANTIER.md"), "# C\n")
        code, s = appel(["archiver", ta])
        verifier("archiver : pas de champ index, garde", code == 1 and s.startswith("GARDE:"), s)


test_archiver()

with tempfile.TemporaryDirectory() as t:
    lire = lambda c: open(c, encoding="utf-8").read()
    os.environ["CLAUDE_CODE_SESSION_ID"] = "cadre"     # la session du cadrage, que `ouvrir` note
    carte_o = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : %s\n- **artefact du chantier** : %s\n")
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n| `05-d.md` | vieux |\n\nFin.\n")
    ecrire(os.path.join(t, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n| relire le chantier E (e) | `ctx/10-e.md` — chantier **clos** |\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
    carte_lue, index_lu, claude_lu = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "00-INDEX.md")), lire(os.path.join(t, "CLAUDE.md"))
    verifier("ouvrir : bilan", code == 0 and s == "OUVERT Q Q1..Q2 · index +1 · routage +1 · session +1 · artefact aucun — %s\n" % t, s)
    verifier("ouvrir : la session du cadrage, avant la première ligne ##", lire(os.path.join(t, "ctx", "30-q.md"))
             == "# Chantier Q — Un titre\n\n**Session** : cadre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n", lire(os.path.join(t, "ctx", "30-q.md")))
    verifier("ouvrir : CHANTIER.md", "**fichier de fiches courant** : ctx/30-q.md (Q1..Q2)\n- **artefact du chantier** : aucun\n" in carte_lue, carte_lue)
    verifier("ouvrir : index, après le plus grand numéro", "| `10-e.md` | on relit |\n| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q2` |\n| `05-d.md`" in index_lu, index_lu)
    verifier("ouvrir : routage, avant « relire un chantier clos »", "**clos** |\n| jouer une fiche du chantier Q (un `titre`) | `ctx/30-q.md` — chantier **ouvert**, par `/vlp:tache Q<n>` |\n| relire" in claude_lu, claude_lu)
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`", "--artefact", "https://exemple/q"])
    verifier("ouvrir : relance, artefact seul", code == 0 and "index +0 · routage +0 · session +0 · artefact https://exemple/q" in s
             and lire(os.path.join(t, "ctx", "30-q.md")).count("**Session**") == 1
             and lire(os.path.join(t, "CLAUDE.md")) == claude_lu and lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_lu
             and "**artefact du chantier** : https://exemple/q" in lire(os.path.join(t, "CHANTIER.md")), s)
    avant = lire(os.path.join(t, "CHANTIER.md"))
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
    verifier("ouvrir : relance sans artefact, rien ne change", code == 0 and lire(os.path.join(t, "CHANTIER.md")) == avant, s)
    ecrire(os.path.join(t, "ctx", "31-r.md"), "# Chantier R — r\n\n## R1 [ ] — a\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
    verifier("ouvrir : autre chantier ouvert, refus", code == 1 and s.startswith("GARDE: un chantier est déjà ouvert")
             and lire(os.path.join(t, "CHANTIER.md")) == avant, s)
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n## Q3 [ ] — c\n")
    # Relancé avec un autre titre : seule la plage suit, sur la même et unique ligne.
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un autre titre"])
    index_q = [l for l in lire(os.path.join(t, "ctx", "00-INDEX.md")).split("\n") if l.startswith("| `30-q.md` |")]
    verifier("ouvrir : relancé, la plage de l'index suit le fichier", code == 0 and "OUVERT Q Q1..Q3 · index ~1 · routage +0 · session +1" in s
             and index_q == ["| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q3` |"]
             and "ctx/30-q.md (Q1..Q3)" in lire(os.path.join(t, "CHANTIER.md")), s + repr(index_q))
    index_main = lire(os.path.join(t, "ctx", "00-INDEX.md")).replace("chantier **ouvert** « Un `titre` », `Q1..Q3`", "à la main `Q1..Q2`")
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), index_main)
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
    verifier("ouvrir : relancé, une ligne d'index écrite à la main reste", code == 0 and "index +0" in s
             and lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_main, s)
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
    # Un vrai fichier : la session va avant `## Le socle commun`, jamais entre le marqueur d'une
    # fiche et son titre — la fiche extraite n'en porte pas. Déjà sur une ligne `**Session**`, même
    # d'une fiche, elle n'est pas redoublée ; un id vide ne note rien.
    vrai = ("# Chantier T — t\n\nÀ quoi il sert.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
            "<!-- FICHE:T1 -->\n## T1 [ ] — a\n<!-- /FICHE -->\n")
    for nom, texte in (("33-t.md", vrai), ("34-u.md", "# Chantier U — u\n\n## U1 [x] — a\n**Session** : cadre\n"),
                       ("35-v.md", "# Chantier V — v\n\n## V1 [ ] — a\n")):
        ecrire(os.path.join(t, "ctx", nom), texte)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    code, s = appel(["ouvrir", t, "--fiches", "ctx/33-t.md", "--titre", "t"])
    lu_o = lire(os.path.join(t, "ctx", "33-t.md"))
    verifier("ouvrir : un vrai fichier, la session avant le socle, hors de toute fiche", code == 0 and "· session +1 ·" in s
             and lu_o == vrai.replace("## Le socle commun", "**Session** : cadre\n\n## Le socle commun")
             and "**Session**" not in appel(["extraire", os.path.join(t, "ctx", "33-t.md"), "T1"])[1], s + lu_o)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    code, s = appel(["ouvrir", t, "--fiches", "ctx/34-u.md", "--titre", "u"])
    verifier("ouvrir : session déjà sur une ligne d'une fiche, pas redoublée", code == 0 and "· session +0 ·" in s
             and lire(os.path.join(t, "ctx", "34-u.md")).count("**Session**") == 1, s)
    ecrire(os.path.join(t, "CHANTIER.md"), carte_o % ("aucun", "aucun"))
    os.environ["CLAUDE_CODE_SESSION_ID"] = ""
    code, s = appel(["ouvrir", t, "--fiches", "ctx/35-v.md", "--titre", "v"])
    verifier("ouvrir : id vide, rien de noté", code == 0 and "· session +0 ·" in s
             and lire(os.path.join(t, "ctx", "35-v.md")) == "# Chantier V — v\n\n## V1 [ ] — a\n", s)
    os.environ.pop("CLAUDE_CODE_SESSION_ID", None)

def test_estime():
    with tempfile.TemporaryDirectory() as te:
        # `ouvrir --estime-fiches` (chantier EST) : A1–A3 à 3,00 $ et B1 à 1,00 $ (4 fiches, 4,00 $)
        # font 1,00 $/fiche — le prix mesuré des lignes, pas les tokens (chantier TAU). D1–D2, mesurée
        # en tokens mais sans `$`, ne compte ni dans la somme ni dans les fiches de la moyenne — mutant :
        # la compter comme 0 $ ferait 4,00 $ sur 6 fiches, ≈0,67 $/fiche au lieu de ≈1,00 $/fiche. La
        # ligne non mesurable (E) ne compte pas non plus.
        lire = lambda c: open(c, encoding="utf-8").read()
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        rang = ('          <tr>\n            <td>x</td>\n            <td class="mono">%s</td><td class="mono">2026-01-01</td>\n'
                '            <td class="mono">%s</td>\n            <td>y</td>\n          </tr>\n')
        carte_e = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n")
        fiches_e = "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n"
        ecrire(os.path.join(te, "CHANTIER.md"), carte_e)
        ecrire(os.path.join(te, "ctx", "30-q.md"), fiches_e)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        verifier("EST1 : sans feuille, GARDE, le reste écrit", code == 0 and "GARDE: feuille de route introuvable" in s
                 and "estimé" not in s.split("\n")[-2] and "**Estimé.**" not in lire(os.path.join(te, "ctx", "30-q.md"))
                 and "ctx/30-q.md (Q1..Q1)" in lire(os.path.join(te, "CHANTIER.md")), s)
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)")
               + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)") + rang % ("D1–D2", "≈2,0M (2 000 000)")
               + rang % ("E1–E8", "non recompté — fichier introuvable · non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        lu_e = lire(os.path.join(te, "ctx", "30-q.md"))
        verifier("EST1 : l'estimé avant **Fait.**, fiches lues sur la plage — mutant : D1–D2 comptée dans la moyenne $",
                 code == 0 and "· estimé 2 fiches ≈2,00 $ — " in s
                 and "\n**Estimé.** 2 fiches · ≈2,00 $ — ≈1,00 $/fiche sur 3 clos (le " in lu_e
                 and lu_e.index("**Estimé.**") < lu_e.index("**Fait.**"), s + lu_e)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "0,5"])
        verifier("EST1 : second appel, estimé gardé, une seule ligne", code == 0 and "· estimé gardé — " in s
                 and lire(os.path.join(te, "ctx", "30-q.md")).count("**Estimé.**") == 1, s)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q"])
        verifier("EST1 : sans l'option, rien ne change", code == 0 and "estimé" not in s
                 and lire(os.path.join(te, "ctx", "30-q.md")) == lu_e, s)
        verifier("EST1 : 0,5 et 0.5 acceptés", mod.nombre_fiches("0,5") == mod.nombre_fiches("0.5") == 0.5
                 and mod.decimal_fr(0.5) == "0,5" and mod.decimal_fr(2.0) == "2", "")
        ecrire(os.path.join(te, "CHANTIER.md"), carte_e)
        ecrire(os.path.join(te, "ctx", "31-r.md"), "# Chantier R — r\n\n**Fait.** Rien.\n\n## R1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("E1–E8", "non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/31-r.md", "--titre", "r", "--estime-fiches", "1"])
        verifier("EST1 : aucun clos mesuré, GARDE, le reste écrit", code == 0 and "GARDE: aucun chantier clos mesuré" in s
                 and "ctx/31-r.md (R1..R1)" in lire(os.path.join(te, "CHANTIER.md")), s)
        # TAU2 : des clos mesurés en tokens, mais aucun au prix `$` — GARDE dédiée, pas d'estimé en $.
        ecrire(os.path.join(te, "CHANTIER.md"), carte_e)
        ecrire(os.path.join(te, "ctx", "32-s.md"), "# Chantier S — s\n\n**Fait.** Rien.\n\n## S1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("D1–D2", "≈2,0M (2 000 000)") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/32-s.md", "--titre", "s", "--estime-fiches", "1"])
        verifier("TAU2 : mesuré en tokens, aucun au prix $ — GARDE dédiée, le reste écrit", code == 0
                 and "GARDE: aucun chantier clos au prix mesuré sur la feuille de route — pas d'estimé" in s
                 and "**Estimé.**" not in lire(os.path.join(te, "ctx", "32-s.md"))
                 and "ctx/32-s.md (S1..S1)" in lire(os.path.join(te, "CHANTIER.md")), s)
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    # TAU2 : le total de la feuille (`resume_clos`, `resommer`) sur trois clos, deux avec `$` et un
    # sans — mutant : compter la ligne sans `$` comme 0 $ fausse la somme comme la moyenne.
    corps_mixte = (rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)") + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)")
                   + rang % ("D1–D2", "≈2,0M (2 000 000)"))
    from decimal import Decimal
    verifier("TAU2 : prix_clos — deux lignes sur trois portent un $, la troisième ignorée",
             mod.prix_clos(corps_mixte) == (Decimal("4.00"), 2), mod.prix_clos(corps_mixte))
    verifier("TAU2 : resume_clos — « sur 2 clos mesurés »",
             mod.resume_clos(3, 6_000_000, Decimal("4.00"), 2)
             == "3 chantiers clos · ≈6,0M (6 000 000) tokens · 4,00 $ sur 2 clos mesurés", mod.resume_clos(3, 6_000_000, Decimal("4.00"), 2))
    gabarit_pied = ('<table><tbody>%s</tbody><tfoot><tr><td colspan="3">Total cumulé</td>'
                    '<td class="mono"><strong>x</strong></td><td class="mono">y</td></tr></tfoot></table>'
                    '<span class="resume-clos">z</span>' % corps_mixte)
    resomme = mod.resommer(gabarit_pied, 3, 6_000_000, *mod.prix_clos(corps_mixte))
    verifier("TAU2 : resommer — pied « 4,00 $ sur 2 clos mesurés », toutes mesurées → sans le « sur »",
             '<strong>≈6,0M (6 000 000)</strong></td><td class="mono">4,00 $ sur 2 clos mesurés</td>' in resomme
             and '<span class="resume-clos">3 chantiers clos · ≈6,0M (6 000 000) tokens · 4,00 $ sur 2 clos mesurés</span>' in resomme, resomme)
    corps_toutes = rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)") + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)")
    verifier("TAU2 : texte_cout_clos — toutes mesurées, sans « sur »",
             mod.texte_cout_clos(*mod.prix_clos(corps_toutes), 2) == "4,00 $", mod.texte_cout_clos(*mod.prix_clos(corps_toutes), 2))
    verifier("TAU2 : texte_cout_clos — aucune mesurée, vide",
             mod.texte_cout_clos(None, 0, 1) == "", mod.texte_cout_clos(None, 0, 1))
    # `clore` sans ligne **Estimé.** (chantier ouvert avant EST) : « estimé non noté », sans GARDE
    # d'estimé ; le réel en dollars est le prix mesuré de la page, `? $` sans lui (chantiers EST, TAU).
    with tempfile.TemporaryDirectory() as te:
        ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : ctx/50-u.md (U1..U2)\n- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(te, "ctx", "50-u.md"), "# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n## U2 [x] — b\n")
        code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
        verifier("EST2 : sans **Estimé.**, estimé non noté, réel ≈? $", code == 0
                 and " · estimé non noté · cadré 2 · joué 2 fiches ? $ — " in s and "stim" not in s.split("CLOS ")[0]
                 and "**Fait.** U1..U2 (2026-09-26) : fini — estimé non noté · cadré 2 · joué 2 fiches ? $.\n"
                 in open(os.path.join(te, "ctx", "50-u.md"), encoding="utf-8").read(), s)
    # Le prix mesuré (le pondéré de la page, ici 12,34 $ pour 2 M tokens — la louche en dirait
    # ≈1,67 $) : au joué, et en tête de la cellule Tokens de la feuille ; inconnu, `? $` et une
    # cellule sans `$` (chantier TAU). Mutant : remettre `estimation_usd` au joué — le test tombe.
    for prix, joue, cellule in ((Decimal("12.34"), "12,34 $", "12,34 $ · ≈2,0M (2 000 000)"),
                                (None, "? $", "≈2,0M (2 000 000)")):
        with tempfile.TemporaryDirectory() as te:
            ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n"
                   "- **fichier de fiches courant** : ctx/50-u.md (U1..U1)\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : U (test).\n")
            ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
                   "|---|---|---|---|---|\n| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
            ecrire(os.path.join(te, "ctx", "50-u.md"), "# Chantier U — u\n\n**Estimé.** 3 fiches · ≈9,00 $ — ≈3,00 $/fiche sur 2 clos (le 2026-09-01).\n\n**Fait.** Rien.\n\n## U1 [x] — a\n")
            ecrire(os.path.join(te, "ctx", "artefacts", "50-u.html"),
                   open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read())
            fdr = os.path.join(te, "ctx", "artefacts", "feuille-de-route.html")
            ecrire(fdr, open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read())
            regenerer_vrai = mod.regenerer
            mod.regenerer = lambda *x, p=prix: (lambda r: r[:3] + ((2_000_000, 3, p), r[4]))(regenerer_vrai(*x))
            try:
                code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
            finally:
                mod.regenerer = regenerer_vrai
            texte = "estimé 3 fiches ≈9,00 $ · cadré 1 · joué 1 fiches " + joue
            lu = lambda c: open(c, encoding="utf-8").read()
            feuille = lu(fdr)
            verifier("TAU1 : joué au prix mesuré (%s) — CLOS, page, .md, **Fait.**" % joue, code == 0
                     and " · " + texte + " — " in s
                     and "<p>Estimé : " + texte + "</p>" in lu(os.path.join(te, "ctx", "artefacts", "50-u.html"))
                     and "Estimé : " + texte + "\n" in lu(os.path.join(te, "ctx", "artefacts", "50-u.md"))
                     and "**Fait.** U1..U1 (2026-09-26) : fini — " + texte + ".\n" in lu(os.path.join(te, "ctx", "50-u.md")), s)
            attendu = (2_000_000, 1, 1, prix, 1 if prix is not None else 0)
            verifier("TAU1 : cellule Tokens « %s », brut relu par couts_clos et moyenne_clos" % cellule,
                     '<td class="mono">' + cellule + "</td>" in "".join(mod.lignes_clos(feuille))
                     and mod.couts_clos(feuille) == [("u", 2_000_000)] and mod.moyenne_clos(feuille) == attendu
                     and (prix is not None or "$ · ≈2,0M" not in feuille),
                     "%r %r %s" % (mod.couts_clos(feuille), mod.moyenne_clos(feuille), mod.lignes_clos(feuille)))


test_estime()


def tester_prix():
    """prix (chantier TAU3) : le `$` de la page de chaque clos posé en tête de sa cellule Tokens,
    le vieux joué à la louche recalé dessus, le vieil estimé marqué `(taux plat)` — sur un projet
    à deux clos, X mesuré en $, Y jamais mesuré."""
    with tempfile.TemporaryDirectory() as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n"
               "- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `x.md` | chantier **clos** « X », `X1..X1` |\n"
               "| `y.md` | chantier **clos** « Y », `Y1..Y1` |\n")
        seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n**Fait.** %s1..%s1 (2026-01-06) : fini —"
                 " estimé 1 fiches ≈%s $ · cadré 1 · joué 1 fiches %s.\n\n## Le socle commun\n\n"
                 "## L'ordre des fiches\n\n<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        ecrire(os.path.join(tp, "ctx", "x.md"), seule % ("X", "X", "X", "25", "≈25 $", "X", "X"))
        ecrire(os.path.join(tp, "ctx", "y.md"), seule % ("Y", "Y", "Y", "10", "? $", "Y", "Y"))
        ecrire(os.path.join(tp, "ctx", "artefacts", "x.html"),
               '<p class="mono cout-total">Coût du chantier : ≈50,0k (50 000) · 5 tours · 12,34 $</p>\n'
               '<div class="bilan"><p>Estimé : estimé 1 fiches ≈25 $ · cadré 1 · joué 1 fiches ≈25 $</p></div>\n')
        ecrire(os.path.join(tp, "ctx", "artefacts", "y.html"),
               '<p class="mono cout-total">Coût du chantier : ≈20,0k (20 000) · 3 tours · ? $</p>\n')
        ecrire(os.path.join(tp, "ctx", "artefacts", "x.md"),
               "# X — notes et journal\n\n## Résultat\nFini\n\n## Notes\n\n## Journal\n\n## Bilan\n"
               "- Estimé : estimé 1 fiches ≈25 $ · cadré 1 · joué 1 fiches ≈25 $\n")
        fdr = os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, '    <!-- ZONE:clos — test -->\n'
               '    <details class="clos">\n      <summary><span class="resume-clos">vieux</span></summary>\n'
               '      <table>\n        <tbody>\n'
               + ligne_close(mod.arrondi(50000)).replace("Q1–Q2", "X1")
               + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1")
               + '        </tbody>\n        <tfoot>\n          <tr><td colspan="3">Total cumulé</td>'
                 '<td class="mono"><strong>vieux</strong></td><td class="mono">vieux</td></tr>\n        </tfoot>\n'
               '      </table>\n    </details>\n')
        disque = lambda: {os.path.relpath(os.path.join(r, n), tp): lire(os.path.join(r, n))
                          for r, _, ns in os.walk(tp) for n in ns}
        avant = disque()
        code, s = appel(["prix", tp, "--a-blanc"])
        ligne = "PRIX 1 posés · 0 déjà · 1 sans prix · 1 joués recalés · 1 estimés marqués · à blanc, rien d'écrit"
        ok = code == 0 and s.splitlines()[-1] == ligne
        ok = ok and "ÉCRIT" not in s
        ok = ok and disque() == avant
        verifier("TAU3 : --a-blanc annonce sans rien écrire", ok, s)
        code, s = appel(["prix", tp])
        ligne = "PRIX 1 posés · 0 déjà · 1 sans prix · 1 joués recalés · 1 estimés marqués"
        ok = code == 0 and s.splitlines()[-1] == ligne
        verifier("TAU3 : premier passage — 1 posé (X, en $), 1 sans prix (Y, ? $) — mutant : marquer"
                 " (taux plat) sans regarder s'il y est déjà", ok, s)
        feuille = lire(fdr)
        ok = '<td class="mono">12,34 $ · ≈50,0k (50 000)</td>' in feuille
        ok = ok and '<td class="mono">≈20,0k (20 000)</td>' in feuille
        verifier("TAU3 : prix posé en tête de la cellule Tokens de X, Y intacte", ok, feuille)
        verifier("TAU4 : pied et résumé de la feuille resommés au premier passage (X mesuré, Y non) —"
                 " mutant : le résumé et le pied non resommés, restés « vieux »",
                 '<strong>%s</strong></td><td class="mono">12,34 $ sur 1 clos mesurés</td>' % mod.arrondi(70000) in feuille
                 and '<span class="resume-clos">%s</span>' % mod.resume_clos(2, 70000, __import__("decimal").Decimal("12.34"), 1)
                 in feuille, feuille)
        recale = "estimé 1 fiches ≈25 $ (taux plat) · cadré 1 · joué 1 fiches 12,34 $"
        x_md = lire(os.path.join(tp, "ctx", "x.md"))
        verifier("TAU3 : joué de X recalé sur le prix mesuré, estimé marqué (taux plat), fichier de fiches",
                 recale + "." in x_md, x_md)
        x_page = lire(os.path.join(tp, "ctx", "artefacts", "x.html"))
        ok = recale in x_page
        ok = ok and "50 000) · 5 tours · 12,34 $</p>" in x_page
        verifier("TAU3 : la page de X recalée pareil, le cout-total intact", ok, x_page)
        x_abri = lire(os.path.join(tp, "ctx", "artefacts", "x.md"))
        verifier("TAU3 : le .md d'abri de X recalé pareil", recale in x_abri, x_abri)
        y_md = lire(os.path.join(tp, "ctx", "y.md"))
        verifier("TAU3 : Y sans prix mesuré — rien recalé, rien marqué",
                 "estimé 1 fiches ≈10 $ · cadré 1 · joué 1 fiches ? $" in y_md, y_md)
        apres = disque()
        code, s = appel(["prix", tp])
        ligne = "PRIX 0 posés · 1 déjà · 1 sans prix · 0 joués recalés · 0 estimés marqués"
        ok = code == 0 and s.splitlines()[-1] == ligne
        ok = ok and "ÉCRIT" not in s
        ok = ok and disque() == apres
        verifier("TAU3 : relancé, plus rien à écrire — fichiers identiques à l'octet", ok, s)
        code, s = appel(["prix", os.path.join(tp, "ctx")])
        verifier("TAU3 : pas de CHANTIER.md, une GARDE", code == 1 and s.startswith("GARDE: pas de CHANTIER.md"), s)


tester_prix()


def tester_cout_session():
    """cout --session, valider --plan, lignes, equiper — regroupés dans une fonction : un test de
    plus au niveau du module fait tomber pyright (« Code is too complex to analyze », chantier TAU3)."""
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
                     and "ccc.jsonl\t" not in s and s.count("TOTAL\t") == 1 and s.startswith("DÉCOUPE aucune — "), s)
            code, s = appel(["cout", f, "--session"])
            verifier("cout --session : la session seule, puis le cumul", code == 0 and s.startswith("SESSION=ccc\nfichier\t")
                     and s.split("TOTAL\t")[0].count("ccc.jsonl\t") == 3 and s.count("TOTAL\t") == 1
                     and s.count("\nDÉCOUPE aucune — ") == 1, s)
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


tester_cout_session()


# --- chantier ESS : les essais d'une session, par le dossier de leur bac -------

with tempfile.TemporaryDirectory() as t:
    pr = os.path.join(t, ".claude", "projects")
    for bac in ("C--tmp-sa-aaaa-1-scratchpad-b1", "C--tmp-sa-aaaa-1-scratchpad-b2", "C--tmp-sa-bbbb-2-scratchpad-b1",
                "C--tmp-sa-aaaa-1-intrus"):     # le dernier n'est pas un bac : pas de `-scratchpad-`
        ecrire(os.path.join(pr, bac, "e.jsonl"), "{}\n")
    garde_env = dict(os.environ)
    os.environ.update(HOME=t, USERPROFILE=t)
    try:
        a, b, z = mod.essais_de("aaaa-1"), mod.essais_de("bbbb-2"), mod.essais_de("zzzz-9")
    finally:
        os.environ.clear()
        os.environ.update(garde_env)
    verifier("essais_de : les deux bacs de A, triés, sans l'intrus",
             a == [os.path.join(pr, "C--tmp-sa-aaaa-1-scratchpad-b1", "e.jsonl"),
                   os.path.join(pr, "C--tmp-sa-aaaa-1-scratchpad-b2", "e.jsonl")], a)
    verifier("essais_de : le bac de B seul", len(b) == 1 and "bbbb-2-scratchpad-b1" in b[0], b)
    verifier("essais_de : session inconnue, liste vide", z == [], z)

# cout : un essai dans la plage de Q1 (et son sous-agent) compte à Q1, l'autre hors fiches.
with tempfile.TemporaryDirectory() as t:
    pr, dep = os.path.join(t, ".claude", "projects"), os.path.join(t, "depot")
    os.makedirs(os.path.join(pr, "p"))
    transcript(os.path.join(pr, "p", "sss.jsonl"), 2, [T0 + 200, T0 + 400])
    for bac, h_ in (("b1", 250), ("b2", 700)):
        os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-" + bac))
        transcript(os.path.join(pr, "C--x-sss-scratchpad-" + bac, "e.jsonl"), 1, [T0 + h_])
    os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents"))
    transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents", "agent-a1.jsonl"), 1, [T0 + 260])
    ecrire(os.path.join(dep, "q.md"), QFICHES % ("sss", "sss"))
    if not shutil.which("git"):
        print("SAUTÉ: git absent — les essais dans la découpe ne sont pas testés")
    else:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=dep, env=env, check=True, capture_output=True)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            code, s = appel(["cout", os.path.join(dep, "q.md")])
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        cent, deux, trois = "≈100,0k (100 000) · 1 tours · 0,50 $", "≈200,0k (200 000) · 2 tours · 1,00 $", "≈300,0k (300 000) · 3 tours · 1,50 $"
        attendu = ("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, un sous-agent compte à son départ\n"
                   "Q1 · %s = session %s + 0 sous-agent + 1 essai %s\n" % (trois, cent, deux)
                   + "Q2 · %s = session %s + 0 sous-agent\n" % (cent, cent)
                   + "hors fiches · %s = session 0 · 0 tours · 0,00 $ + 0 sous-agent + 1 essai %s\n" % (cent, cent)
                   + "TOTAL (fiches + hors fiches) · ≈500,0k (500 000) · 5 tours · 2,50 $ = session %s"
                     " + 0 sous-agent + 2 essais %s\n" % (deux, trois))
        verifier("cout : l'essai de la plage à Q1, sous-agent compris ; l'autre hors fiches ; TOTAL les deux",
                 code == 0 and s == attendu, s)

# APC1 : cout --a-clore. Q1 (200), Q2 (400), l'appel clore (700), un tour après lui (800), le commit
# de clôture (900), un clore rejoué après lui (1000), hors plage : à clore = 3 tours, après = 1.
with tempfile.TemporaryDirectory() as t:
    pr, dep = os.path.join(t, ".claude", "projects"), os.path.join(t, "depot")
    os.makedirs(os.path.join(pr, "p"))
    for s_, heures_ in (("sss", [T0 + 200, T0 + 400, T0 + 700, T0 + 800, T0 + 1000]), ("ttt", [T0 + 200, T0 + 400, T0 + 700])):
        chemin_ = os.path.join(pr, "p", s_ + ".jsonl")
        transcript(chemin_, len(heures_), heures_)
        if s_ == "sss":
            lignes_ = [json.loads(l) for l in lire(chemin_).splitlines()]
            for k in (2, 4):
                lignes_[k]["message"]["content"] = [{"type": "tool_use", "id": "t%d" % k, "name": "Bash", "input": {
                    "command": 'py "C:/k/scripts/vlp.py" clore . --livre x'}}]
            lignes_[3]["message"]["content"] = [{"type": "tool_use", "id": "t3", "name": "Bash",
                                                 "input": {"command": 'grep -n "clore" scripts/vlp.py'}}]
            ecrire(chemin_, "".join(json.dumps(l) + "\n" for l in lignes_))
    ecrire(os.path.join(dep, "q.md"), QFICHES % ("sss", "sss"))
    ecrire(os.path.join(dep, "r.md"), QFICHES % ("ttt", "ttt"))
    if not shutil.which("git"):
        print("SAUTÉ: git absent — cout --a-clore n'est pas testé")
    else:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=dep, env=env, check=True, capture_output=True)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                         (900, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        # APC2 : recompter --a-clore, un projet par fichier (q.md et r.md portent le même préfixe Q),
        # inscrit 250 000 : ni le recompté (400 000) ni l'à-clore (300 000).
        for p_, f_ in (("pq", "q.md"), ("pr", "r.md")):
            ecrire(os.path.join(dep, p_, "CHANTIER.md"), "# C\n\n- **contexte** : ./\n- **index** : 00-INDEX.md\n")
            ecrire(os.path.join(dep, p_, "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
                   "| `../%s` | chantier **clos** « Q », `Q1..Q2` |\n" % f_)
            ecrire(os.path.join(dep, p_, "artefacts", "feuille-de-route.html"),
                   "    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n"
                   + ligne_close(mod.arrondi(250000)) + "        </tbody>\n      </table>\n")
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            (code, s), (code2, s2) = (appel(["cout", os.path.join(dep, "q.md"), "--a-clore"]),
                                      appel(["cout", os.path.join(dep, "r.md"), "--a-clore"]))
            (code3, s3), (code4, s4), (code5, s5) = (appel(["recompter", os.path.join(dep, "pq"), "--a-clore"]),
                                                     appel(["recompter", os.path.join(dep, "pr"), "--a-clore"]),
                                                     appel(["recompter", os.path.join(dep, "pq")]))
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        lignes_ = s.splitlines()
        verifier("cout --a-clore : TOTAL 4 tours, à clore 3, après clore 1 — le clore hors plage et le grep ignorés",
                 code == 0 and len(lignes_) == 7 and lignes_[4].startswith("TOTAL ")
                 and mod.triplet(lignes_[4])[:2] == (400000, 4)
                 and lignes_[5].startswith("à clore · ") and mod.triplet(lignes_[5])[:2] == (300000, 3)
                 and lignes_[6].startswith("après clore · ") and mod.triplet(lignes_[6])[:3] == (100000, 1, Decimal("0.50")), s)
        verifier("cout --a-clore : sans appel clore, une GARDE et pas de ligne", code2 == 0
                 and s2.splitlines()[-1] == "GARDE: aucun appel « vlp.py clore » dans la dernière plage hors fiches"
                 " — pas de ligne à clore" and "à clore ·" not in s2, s2)
        verifier("recompter --a-clore : à clore 300 000, après clore = recompté − à clore — mutant :"
                 " après clore = recompté − inscrit", code3 == 0 and s3.splitlines()[0] ==
                 "Q inscrit 250 000 · recompté 400 000 · écart +150 000 · découpe · à clore 300 000 · après clore 100 000", s3)
        verifier("recompter --a-clore : sans appel clore, la ligne le dit", code4 == 0 and s4.splitlines()[0] ==
                 "Q inscrit 250 000 · recompté 300 000 · écart +50 000 · découpe · sans appel clore", s4)
        verifier("recompter sans --a-clore : la ligne d'avant APC2", code5 == 0 and s5.splitlines()[0] ==
                 "Q inscrit 250 000 · recompté 400 000 · écart +150 000 · découpe", s5)

# APC3 : un vrai `clore` — Q1 (200), Q2 (400), l'appel clore (700) —, puis un tour après lui (800) et
# le commit de clôture (900) : le chiffre inscrit égale le TOTAL de cout, le recompté.
def tester_apc3():
    """APC3, et la dette PLI : page d'un clos s'arrête à clore, comme cout."""
    with tempfile.TemporaryDirectory() as t:
        proj, s3 = os.path.join(t, "apc3"), os.path.join(t, "s3.jsonl")
        transcript(s3, 3, [T0 + 200, T0 + 400, T0 + 700])
        lignes_ = [json.loads(l) for l in lire(s3).splitlines()]
        lignes_[2]["message"]["content"] = [{"type": "tool_use", "id": "t2", "name": "Bash",
                                             "input": {"command": 'py "C:/k/scripts/vlp.py" clore . --livre x'}}]
        ecrire(s3, "".join(json.dumps(l) + "\n" for l in lignes_))
        ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : ctx/q.md (Q1..Q2)\n- **artefact du chantier** : https://u\n\n"
               "Lettres de fiche déjà prises : Q (test).\n")
        ecrire(os.path.join(proj, "ctx", "q.md"), QFICHES % (s3, s3))
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `q.md` | on joue `Q*` — **ouvert** |\n")
        ecrire(os.path.join(proj, "CLAUDE.md"), "| T | O |\n|---|---|\n| jouer Q | `ctx/q.md` **ouvert** |\n")
        ecrire(os.path.join(proj, "ctx", "artefacts", "q.html"),
               open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read())
        if not shutil.which("git"):
            print("SAUTÉ: git absent — clore = recompte n'est pas testé")
        else:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            subprocess.run(["git", "init", "-q"], cwd=proj, env=env, check=True, capture_output=True)

            def commit_(d, sujet):
                date = "%d +0000" % (T0 + d)
                subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=proj, check=True,
                               capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
            for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
                commit_(d, sujet)
            code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "1", "--date", "2026-09-25"])
            with open(s3, "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(lignes_[0], requestId="r9", timestamp=datetime.datetime.fromtimestamp(
                    T0 + 800, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    message=dict(lignes_[0]["message"], id="m9"))) + "\n")
            commit_(900, "Chantier Q clos : fini")
            code2, s2 = appel(["cout", os.path.join(proj, "ctx", "q.md")])
            verifier("APC3 : inscrit par clore = recompté, 300 000 · 3 tours ; le tour d'après clore n'y est pas"
                     " — mutant : decouper sans heure_clore (recompté 400 000)", code == 0 and code2 == 0
                     and "chantier 300 000" in s and "**CLOS**" in lire(os.path.join(proj, "ctx", "q.md"))
                     and "\nTOTAL (fiches + hors fiches) · ≈300,0k (300 000) · 3 tours" in s2, s + s2)
            code3, s3_ = appel(["page", os.path.join(proj, "ctx", "q.md"), os.path.join(proj, "ctx", "artefacts", "q.html")])
            verifier("dette PLI : page d'un clos = cout, 300 000 · 3 tours — mutant : page sans heure_clore"
                     " (400 000 · 4 tours)", code3 == 0 and "Coût du chantier : ≈300,0k (300 000) · 3 tours"
                     in lire(os.path.join(proj, "ctx", "artefacts", "q.html")), s3_)


tester_apc3()

# ESD1 : sans découpe (pas de .git), les essais des sessions entières en une ligne à part, sous
# les tables ; une session sans essai n'en a pas.
with tempfile.TemporaryDirectory() as t:
    pr, dep = os.path.join(t, ".claude", "projects"), os.path.join(t, "depot")
    os.makedirs(os.path.join(pr, "p"))
    for s_ in ("sss", "ttt"):
        transcript(os.path.join(pr, "p", s_ + ".jsonl"), 2, [T0 + 200, T0 + 400])
    for bac in ("b1", "b2"):
        os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-" + bac))
        transcript(os.path.join(pr, "C--x-sss-scratchpad-" + bac, "e.jsonl"), 1, [T0 + 250])
    os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents"))
    transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents", "agent-a1.jsonl"), 1, [T0 + 260])
    ecrire(os.path.join(dep, "avec.md"), QFICHES % ("sss", "sss"))
    ecrire(os.path.join(dep, "sans.md"), QFICHES % ("ttt", "ttt"))
    garde_env = dict(os.environ)
    os.environ.update(HOME=t, USERPROFILE=t)
    try:
        (code, s), (code2, s2) = appel(["cout", os.path.join(dep, "avec.md")]), appel(["cout", os.path.join(dep, "sans.md")])
    finally:
        os.environ.clear()
        os.environ.update(garde_env)
    verifier("cout sans découpe : une ligne essais, 2 essais sous-agent compris, après les tables",
             code == 0 and s.startswith("DÉCOUPE aucune — ") and "\nsss.jsonl\t2\t" in s
             and s.endswith("\nessais · ≈300,0k (300 000) · 3 tours · 1,50 $ = session 0 · 0 tours · 0,00 $"
                            " + 0 sous-agent + 2 essais ≈300,0k (300 000) · 3 tours · 1,50 $\n"), s)
    verifier("cout sans découpe, sans essai : pas de ligne essais", code2 == 0
             and s2.startswith("DÉCOUPE aucune — ") and "essai" not in s2 and s2.endswith("\n"), s2)

# ESD2 : recompter --essais, sur un projet sans .git — M (session sss, 1 essai + son sous-agent) est
# gardé DÉCOUPE aucune et reçoit ses essais ; N (session ttt, sans essai) ne change pas. Un second
# passage ne change plus rien : la marque est lue avant l'ajout, à l'affichage comme à l'écriture.
with tempfile.TemporaryDirectory() as t:
    pr, rc = os.path.join(t, ".claude", "projects"), os.path.join(t, "rc")
    os.makedirs(os.path.join(pr, "p"))
    for s_ in ("sss", "ttt"):
        transcript(os.path.join(pr, "p", s_ + ".jsonl"), 1, [T0 + 200])
    os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents"))
    transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e.jsonl"), 1, [T0 + 250])
    transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents", "agent-a1.jsonl"), 1, [T0 + 260])
    seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
             "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Session** : %s\n**Critère de fin**\n<!-- /FICHE -->\n")
    ecrire(os.path.join(rc, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
    ecrire(os.path.join(rc, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
           "| `m.md` | chantier **clos** « M », `M1..M1` |\n| `n.md` | chantier **clos** « N », `N1..N1` |\n")
    ecrire(os.path.join(rc, "ctx", "m.md"), seule % ("M", "M", "M", "sss"))
    ecrire(os.path.join(rc, "ctx", "n.md"), seule % ("N", "N", "N", "ttt"))
    fr = os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(fr, '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
           + "".join(ligne_close(c).replace("Q1–Q2", pl) for pl, c in (("M1", mod.arrondi(300000)), ("N1", mod.arrondi(2000))))
           + "        </tbody>\n      </table>\n")
    garde_env = dict(os.environ)
    os.environ.update(HOME=t, USERPROFILE=t)
    try:
        initial = lire(fr)
        simule = appel(["recompter", rc, "--essais"])
        avant = lire(fr)
        un = appel(["recompter", rc, "--essais", "--ecrire"])
        feuille_ = lire(fr)
        deux = appel(["recompter", rc, "--essais", "--ecrire"])
        resimule = appel(["recompter", rc, "--essais"])
    finally:
        os.environ.clear()
        os.environ.update(garde_env)
    l_ = simule[1].splitlines()
    verifier("recompter --essais : le gardé DÉCOUPE aucune reçoit ses essais, sous-agent compris ; l'autre +0 ;"
             " rien d'écrit", simule[0] == 0 and len(l_) == 3 and avant == initial
             and l_[0].startswith("M inscrit 300 000 · essais 200 000 · ajout +200 000 · gardé — DÉCOUPE aucune (")
             and l_[1].startswith("N inscrit 2 000 · essais 0 · ajout +0 · gardé — DÉCOUPE aucune (")
             and l_[2] == "ESSAIS 2 clos · 1 reçoivent · inscrit 302 000 · avec essais 502 000 · ajout +200 000", simule[1])
    verifier("recompter --essais --ecrire : le chiffre + l'essai, la marque en tête, BRUT le relit",
             un[0] == 0 and un[1].splitlines()[-1] == "ÉCRIT 1 cellules · total 302 000 → 502 000"
             and '<td class="mono">essais (ESD) +200 000 · ≈500,0k (500 000)</td>' in feuille_
             and '<td class="mono">≈2,0k (2 000)</td>' in feuille_ and mod.total_clos(feuille_) == 502000, un[1] + feuille_)
    verifier("recompter --essais --ecrire, second passage : cellule identique — mutant : ignorer la marque",
             deux[0] == 0 and lire(fr) == feuille_ and deux[1].splitlines()[-1] == "ÉCRIT 0 cellules · total 502 000 → 502 000",
             deux[1] + lire(fr))
    verifier("recompter --essais après écriture : la simulation dit +0, déjà ajoutés",
             resimule[0] == 0 and resimule[1].splitlines()[0].startswith("M inscrit 500 000 · essais 200 000 · ajout +0 · ")
             and resimule[1].splitlines()[0].endswith(" · déjà ajoutés (ESD)")
             and resimule[1].splitlines()[-1].endswith(" · 0 reçoivent · inscrit 502 000 · avec essais 502 000 · ajout +0"),
             resimule[1])
    # La règle du découpé, en fonction pure : les essais sans passer le recompté.
    verifier("ajout_essais : découpé borné par l'écart ; autre gardé, rien ; marque, rien",
             [mod.ajout_essais("x", 100, 150, "découpe", 80), mod.ajout_essais("x", 100, 300, "découpe", 80),
              mod.ajout_essais("x", 100, 90, "découpe", 80), mod.ajout_essais("x", 100, None, "gardé — sans session", 80),
              mod.ajout_essais(mod.MARQUE_ESSAIS + "+5 · (105)", 105, None, "gardé — DÉCOUPE aucune (r)", 5)]
             == [50, 80, 0, 0, 0], "")
    # Dette d'ESD : un `recompter --ecrire` sur une cellule marquée ESD garde la marque en tête.
    marques = [mod.marquer("essais (ESD) +200 000 · recompté (REC), était 650 000 · ≈850,0k (850 000)", 850000, 900000, "découpe"),
               mod.marquer("essais (ESD) +50 000 · ≈700,0k (700 000)", 700000, 750000, "découpe")]
    verifier("marquer : la marque ESD reste en tête — mutant : la marque ESD perdue", marques == [
        "essais (ESD) +200 000 · recompté (REC), était 650 000 · ≈900,0k (900 000)",
        "essais (ESD) +50 000 · recompté (REC), était 700 000 · ≈750,0k (750 000)"], marques)

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

def tester_cocher_session(f):
    # cocher --session --role (chantier NUI) : la session d'un rôle de la nuit, avec son suffixe.
    garde_env = dict(os.environ)
    ecrire(f, "# Chantier\n\n## Le socle commun\n\nSocle.\n\n<!-- FICHE:U1 -->\n## U1 [ ] — Première\n"
              "**Dépend de** : `U0`.\n<!-- /FICHE -->\n")
    try:
        os.environ["CLAUDE_CODE_SESSION_ID"] = "xyz"
        code, s = appel(["cocher", f, "U1", "--session", "abc", "--role", "relire"])
        une = lire(f)
        code2, s2 = appel(["cocher", f, "U1", "--session", "abc", "--role", "relire"])
        verifier("cocher --session : une ligne, la fiche reste ouverte, jamais doublée",
                 code == 0 and s == "NOTÉ U1 · **Session** : abc (relire)\n" and "## U1 [ ]" in une
                 and une.count("**Session** : abc (relire)\n**Dépend de**") == 1
                 and (code2, s2) == (0, "DÉJÀ U1 · **Session** : abc (relire)\n") and lire(f) == une, s + s2 + lire(f))
        appel(["cocher", f, "U1"])
        code, s = appel(["cocher", f, "U1", "--session", "cl1", "--role", "clore"])
        texte = lire(f)
        verifier("cocher --session --role clore : l'en-tête, avant le premier titre, vu de sessions_entete",
                 code == 0 and texte.index("**Session** : cl1 (clore)\n") < texte.index("## Le socle commun")
                 and mod.sessions_entete(mod.lignes_de(f)) == ["cl1"]
                 and "## U1 [x]" in texte and "**Session** : abc (relire)\n**Session** : xyz\n**Dépend de**" in texte,
                 s + texte)
        verifier("cocher --session : sessions rend l'id sans suffixe, dédoublonné",
                 appel(["sessions", f]) == (0, "cl1\nabc\nxyz\n"), appel(["sessions", f]))
        avant3 = lire(f)
        verifier("cocher --session sans --role : GARDE, rien écrit",
                 appel(["cocher", f, "U1", "--session", "abc"]) == (1, "GARDE: --session <uuid> --role <rôle>, sans espace ni parenthèse\n")
                 and lire(f) == avant3, lire(f))
    finally:
        os.environ.clear()
        os.environ.update(garde_env)


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
        verifier("cocher --verifier : cochée", appel(["cocher", f, "U1", "--verifier"]) == (0, "CASE U1 [x]\nSANS GIT\n"), appel(["cocher", f, "U1", "--verifier"]))
        avant2 = lire(f)
        verifier("cocher --verifier : non cochée, pas d'écriture", appel(["cocher", f, "U2", "--verifier"]) == (1, "CASE U2 [ ]\nSANS GIT\n") and lire(f) == avant2, appel(["cocher", f, "U2", "--verifier"]))
        verifier("cocher --verifier : fiche introuvable", appel(["cocher", f, "U9", "--verifier"]) == (1, "GARDE: fiche introuvable : U9\n"), appel(["cocher", f, "U9", "--verifier"]))
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        code, s = appel(["cocher", f, "U2"])
        verifier("cocher : id vide, pas de ligne Session", code == 0 and s == "COCHÉ U2 · Session absente\n"
                 and lire(f) == avant.replace("## U2 [ ]", "## U2 [x]"), s + lire(f))
    finally:
        os.environ.clear()
        os.environ.update(garde_env)

    tester_cocher_session(f)

    ecrire(f, PAGE % (" ", "", " ", ""))
    page = os.path.join(t, "ctx", "artefacts", "05-u.html")
    code, s = appel(["page", f, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R", "--date", "2026-01-02"])
    verifier("page sans chemin : artefacts/<même nom>.html, dossier créé", code == 0 and os.path.isfile(page)
             and s.startswith("PAGE %s · 3 fiches" % page), s)
    code, s = appel(["page", f, "--verifier"])
    verifier("page --verifier sans chemin : la même page", code == 0 and s.startswith("À JOUR 3 fiches"), s)

# cocher --verifier et --refuser (chantier REV) : la tête du dépôt, puis le refus du relecteur.
REFUS = """<!-- FICHE:VAL1 -->
## VAL1 [x] — Valider

**Dépend de** : rien.
<!-- /FICHE -->
<!-- FICHE:VAL10 -->
## VAL10 [x] — Dixième
**Dépend de** : `VAL1`.
<!-- /FICHE -->
"""

with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "ctx", "06-v.md")
    ecrire(f, REFUS)
    verifier("cocher --verifier : sans Git", appel(["cocher", f, "VAL1", "--verifier"]) == (0, "CASE VAL1 [x]\nSANS GIT\n"),
             appel(["cocher", f, "VAL1", "--verifier"]))
    code, s = appel(["cocher", f, "VAL1", "--refuser", "motif un", "--date", "2026-01-03"])
    premier = lire(f)
    code2, s2 = appel(["cocher", f, "VAL1", "--refuser", "motif deux", "--date", "2026-01-04"])
    bloc = "**Tentatives** (2026-01-03) — non résolu.\n1. FAITE refusée à la relecture.\n"
    un = REFUS.replace("## VAL1 [x] — Valider\n\n", "## VAL1 [ ] — Valider\n\n" + bloc + "Erreur : motif un\n\n")
    deux = un.replace(bloc + "Erreur : motif un\n", bloc + "2. FAITE refusée à la relecture.\nErreur : motif deux\n")
    verifier("cocher --refuser", (code, s, code2, s2) == (0, "REFUSÉ VAL1 · refus 1\n", 0, "REFUSÉ VAL1 · refus 2\n")
             and premier == un and lire(f) == deux and lire(f).count("**Tentatives**") == 1
             and lire(f).count("Erreur :") == 1
             and appel(["cocher", f, "VAL9", "--refuser", "m"]) == (1, "GARDE: fiche introuvable : VAL9\n"),
             premier + "\n---\n" + lire(f))
    if not shutil.which("git"):
        print("SAUTÉ: git absent — la tête de cocher --verifier n'est pas testée")
    else:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        ecrire(f, REFUS)
        subprocess.run(["git", "init", "-q"], cwd=t, env=env, check=True, capture_output=True)
        vus = []
        for sujet in ("VAL1: x", "VAL1 : x", "VAL10 : y"):
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=t, env=env, check=True,
                           capture_output=True)
            # Lu comme vlp.py le lit, config du poste comprise : même longueur d'abréviation.
            sha = subprocess.run(["git", "log", "-1", "--format=%h"], cwd=t, capture_output=True,
                                 encoding="utf-8").stdout.strip()
            vus.append((appel(["cocher", f, "VAL1", "--verifier"]), sha))
        verifier("cocher --verifier : un commit du sous-agent",
                 [v for v, _ in vus] == [(1, "CASE VAL1 [x]\nTÊTE %s VAL1: x\n" % vus[0][1]),
                                        (1, "CASE VAL1 [x]\nTÊTE %s VAL1 : x\n" % vus[1][1]),
                                        (0, "CASE VAL1 [x]\n")], vus)

# refus dans un bloc déjà existant mais dont l'unique tentative n'est PAS un refus de
# relecture (une piste écrite à la main, ou une BLOQUÉE) : le rang repart à 1, pas à 2 —
# distingue de « <n> = toutes les lignes numérotées ».
REFUS_PISTE = """<!-- FICHE:VAL2 -->
## VAL2 [x] — Deuxième

**Tentatives** (2026-01-05) — non résolu.
1. <une piste>
Erreur : blocage initial
**Dépend de** : rien.
<!-- /FICHE -->
"""
with tempfile.TemporaryDirectory() as t:
    f2 = os.path.join(t, "ctx", "07-v2.md")
    ecrire(f2, REFUS_PISTE)
    code3, s3 = appel(["cocher", f2, "VAL2", "--refuser", "motif trois", "--date", "2026-01-06"])
    attendu2 = REFUS_PISTE.replace("## VAL2 [x]", "## VAL2 [ ]").replace(
        "1. <une piste>\nErreur : blocage initial\n",
        "1. <une piste>\n2. FAITE refusée à la relecture.\nErreur : motif trois\n")
    verifier("cocher --refuser : bloc existant sans refus de relecture, rang repart à 1",
             (code3, s3) == (0, "REFUSÉ VAL2 · refus 1\n") and lire(f2) == attendu2, s3 + lire(f2))

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


# ARC1 : l'archive des clos, quand elle existe, reçoit et donne les lignes closes ; la feuille garde le graphique
def test_page_clos():
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z % "ctx/30-a.md (A1..A1)"
               + "\nLettres de fiche déjà prises : A (Arc). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `x.md` | chantier **clos** « X », `X1..X1` |\n| `y.md` | chantier **clos** « Y », `Y1..Y1` |\n"
               "| `30-a.md` | chantier **ouvert** « A », `A1..A1` |\n")
        ecrire(os.path.join(proj, "ctx", "30-a.md"), "# Chantier A\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
               "## L'ordre des fiches\n\n<!-- FICHE:A1 -->\n## A1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        gabarit = lire(GABARIT_FEUILLE)
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, gabarit)
        d, f = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
        deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
                + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
        archive = os.path.join(proj, "ctx", "artefacts", mod.ARCHIVE_CLOS)
        ecrire(archive, gabarit[:d] + deux + gabarit[f:])
        verifier("ARC1 : page_clos rend l'archive", os.path.normpath(mod.page_clos(proj)) == os.path.normpath(archive),
                 mod.page_clos(proj))
        code, s = appel(["recompter", proj])
        verifier("ARC1 : recompter lit les deux clos de l'archive", code == 0 and "RECOMPTE 2 clos" in s, s)
        code, s = appel(["prix", proj, "--a-blanc"])
        verifier("ARC1 : prix lit l'archive", code == 0 and "2 sans prix" in s, s)
        code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "1000"])
        lignes_a, lignes_f = mod.lignes_clos(lire(archive)), mod.lignes_clos(lire(fdr))
        verifier("ARC1 : clore ajoute sa ligne en tête de l'archive, la feuille n'en a aucune",
                 code == 0 and len(lignes_a) == 3 and "A1" in lignes_a[0] and not lignes_f, s)
        svg = os.path.join(proj, "ctx", "artefacts", mod.COUTS_SVG)
        barres = lire(svg).count('class="barre"') if os.path.isfile(svg) else 0
        verifier("ARC1 : couts.svg à côté de la feuille, trois barres lues dans l'archive",
                 barres == 3 and 'data-couts=' in lire(fdr), "%d barres\n%s" % (barres, s))
        ecrire(os.path.join(proj, "ctx", "31-b.md"), "# Chantier B\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
               "## L'ordre des fiches\n\n<!-- FICHE:B1 -->\n## B1 [ ] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        code, s = appel(["ouvrir", proj, "--fiches", "ctx/31-b.md", "--titre", "b", "--estime-fiches", "1"])
        verifier("ARC1 : le prix moyen d'ouvrir se lit dans l'archive", "estimé 1 fiches ≈12 $" in s, s)


test_page_clos()


def test_archive():
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z % "ctx/30-a.md (A1..A1)"
               + "\nLettres de fiche déjà prises : A (Arc). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `30-a.md` | chantier **ouvert** « A », `A1..A1` |\n")
        ecrire(os.path.join(proj, "ctx", "30-a.md"), "# Chantier A\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
               "## L'ordre des fiches\n\n<!-- FICHE:A1 -->\n## A1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        gabarit = lire(GABARIT_FEUILLE)
        d, f = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
        deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
                + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, mod.resommer(gabarit[:d] + deux + gabarit[f:], 2, 70000))
        archive = os.path.join(proj, "ctx", "artefacts", mod.ARCHIVE_CLOS)
        code, s = appel(["archive", proj])
        a_html, f_html = lire(archive) if os.path.isfile(archive) else "", lire(fdr)
        verifier("ARC2 : archive déplace les deux lignes et le pied",
                 code == 0 and "ARCHIVE 2 déplacées" in s and len(mod.lignes_clos(a_html)) == 2
                 and "Total cumulé" in a_html and "Total cumulé" not in f_html and "<!-- ZONE:clos" not in f_html, s)
        verifier("ARC2 : la feuille garde le bloc d'archive, son résumé et le graphique",
                 "<!-- ZONE:archive" in f_html and "2 chantiers clos" in f_html and "pas encore publiée" in f_html
                 and "data-couts=" in f_html and "&lt;md&gt;" not in a_html, f_html[-1500:])
        code, s = appel(["archive", proj])
        verifier("ARC2 : relancé, rien ne bouge",
                 code == 0 and "ARCHIVE 0 déplacées" in s and lire(fdr) == f_html and lire(archive) == a_html, s)
        code, s = appel(["archive", proj, "--url", "https://claude.ai/artifact/ARCH"])
        verifier("ARC2 : --url écrit le champ et le lien",
                 code == 0 and "- **artefact archive** : https://claude.ai/artifact/ARCH" in lire(os.path.join(proj, "CHANTIER.md"))
                 and 'href="https://claude.ai/artifact/ARCH"' in lire(fdr), s)
        code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "1000"])
        attente = os.path.join(proj, "ctx", "artefacts", "en-attente")
        verifier("ARC2 : clore refait le bloc (3 clos) et met l'archive en attente",
                 code == 0 and "3 chantiers clos" in lire(fdr) and "data-couts=" in lire(fdr) and len(mod.lignes_clos(lire(archive))) == 3
                 and os.path.isfile(attente) and mod.ARCHIVE_CLOS + "\thttps://claude.ai/artifact/ARCH" in lire(attente), s)
        code, s = appel(["archive", proj])
        verifier("ARC2 : après clore, archive ne bouge plus rien", code == 0 and "ARCHIVE 0 déplacées" in s, s)


test_archive()


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

    prises = [mod.lettres_prises(["Lettres de fiche déjà prises : %s Un nouveau chantier en choisit une autre." % e])
              for e in ("E (Un), Q (Tests, CI (rapide)).", "A.", "aucune.")]
    verifier("lettres prises : titre à virgule, lettre sans titre", prises == [["E", "Q"], ["A"], []], repr(prises))

    verifier("3 lettres : lettre_de isole le préfixe",
             (mod.lettre_de("RNV12"), mod.lettre_de("Z3")) == ("RNV", "Z"),
             repr((mod.lettre_de("RNV12"), mod.lettre_de("Z3"))))

    verifier("3 lettres : une entrée de clos est reconnue",
             bool(mod.ENTREE_CLOS.match("- Clos le 2026-09-17 : un titre (chantier RNV).")), "non")

# NIV1 — la ligne d'injection ne laisse entrer aucun message de lanceur dans la carte.
RACINE = os.path.dirname(ICI)
lignes_injection = []
for skill in ("chantier", "tache", "chef"):
    texte = io.open(os.path.join(RACINE, "skills", skill, "SKILL.md"), encoding="utf-8").read()
    lignes_injection.append([l for l in texte.splitlines() if l.startswith("!`") and "vlp.py" in l])

verifier("NIV1 : une ligne d'injection par skill, les trois identiques",
         [len(x) for x in lignes_injection] == [1, 1, 1]
         and lignes_injection[0] == lignes_injection[1] == lignes_injection[2],
         repr(lignes_injection))

injection = lignes_injection[0][0]
# EVF4 : plus aucune redirection — `2>"${CLAUDE_PLUGIN_ROOT}/…"` écrivait hors du workspace, refusé sous
# eval même Bash accordé (variante A, seule à laisser forker vlp:jouer). Le prix : `py: command not found`
# entre dans la carte là où `py` manque (2 lignes sur 60 sous Ubuntu, 0 sous Windows, mesuré le 2026-09-26).
verifier("EVF4 : trois appels de lanceur, aucune redirection",
         injection.count('/scripts/vlp.py" carte') == 3 and ">" not in injection, injection)

verifier("NIV1 : aucune syntaxe propre a un seul shell",
         "$null" not in injection and "/dev/null" not in injection, injection)

# Dette REL, puis EVF4 : toute injection de carte (une par SKILL.md du glob) — trois appels, et aucune écriture de fichier.
skills_glob = sorted(glob.glob(os.path.join(RACINE, "skills", "*", "SKILL.md")))
ecrit_fichier = []
injections = 0
for chemin_skill in skills_glob:
    for bout in io.open(chemin_skill, encoding="utf-8").read().split("!`")[1:]:
        bout = bout.split("`")[0]
        appels = bout.count('/scripts/vlp.py" carte')
        if appels:
            injections += 1
            if appels != 3 or ">" in bout:
                ecrit_fichier.append(os.path.basename(os.path.dirname(chemin_skill)))
verifier("EVF4 : une injection de carte par SKILL.md du glob, aucune n'écrit de fichier",
         injections == len(skills_glob) > 0 and ecrit_fichier == [],
         "%d injections pour %d SKILL.md, fautives : %r" % (injections, len(skills_glob), ecrit_fichier))

s_niv1 = io.StringIO()
mod.carte_injectee(os.path.join(RACINE, "scripts"), "py", False, s_niv1)
lu_n = s_niv1.getvalue()
verifier("NIV1 : la carte ne dit que PYTHON= et le projet",
         lu_n.splitlines()[:2] == ["", "PYTHON=py"] and "introuvable" not in lu_n and "not found" not in lu_n
         and "PROJET=" in lu_n, lu_n[:200])

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

# Un chantier courant fait passer `niveau` par `cmd_page` : son appel interne
# oubliait `forme`, ajouté par HAB — traceback chez MapDecorator, le 2026-09-27.
# Dans une fonction : un embranchement de plus au niveau du module, et pyright
# rend « Code is too complex to analyze » sur tout le fichier.
def niveau_courant():
    with tempfile.TemporaryDirectory() as tc:
        pc = os.path.join(tc, "courant")
        ecrire(os.path.join(pc, "CHANTIER.md"), CARTE_NETTE.replace(
            "courant** : aucun", "courant** : ctx/20-z.md"))
        ecrire(os.path.join(pc, "ctx", "00-INDEX.md"), INDEX_NET)
        ecrire(os.path.join(pc, "ctx", "08-etat.md"), ETAT_NIV)
        ecrire(os.path.join(pc, "ctx", "20-z.md"), FICHES)
        try:
            return appel(["niveau", pc])
        except AttributeError as e:
            return None, "traceback : %s" % e

code, s = niveau_courant()
verifier("HAB : `niveau` avec un chantier courant rend son bilan, pas un traceback",
         code is not None and "\nNIVEAU " in s, s)

# --- NIV3 : `niveau --ecrire` corrige les écarts mécaniques, et eux seuls ----

# Une feuille de route d'avant le 2026-09-17 : le CSS inline (comme avant le
# chantier PLI, pas de <link href="vlp.css">), sans le bloc repliable ni ses
# règles CSS — le reste à l'identique, marqueurs et indentation compris.
GABARIT_VLPCSS = os.path.join(ICI, "..", "templates", "vlp.css")


def feuille_ancienne():
    css = "".join(l for l in io.open(GABARIT_VLPCSS, encoding="utf-8").read().splitlines(True)
                  if not l.lstrip().startswith(("details.clos", ".resume-clos")))
    gabarit = io.open(GABARIT_FEUILLE, encoding="utf-8").read()
    gabarit = gabarit.replace('<link rel="stylesheet" href="vlp.css">', "<style>\n%s</style>" % css)
    lignes = gabarit.splitlines(True)
    return "".join(l for l in lignes
                   if not l.lstrip().startswith(("<details class=\"clos\">",
                                                 "<summary><span class=\"resume-clos\">", "</details>")))


CARTE_NIV3 = """# Chantier courant

- **alias** : niv3
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **fichier de fiches courant** : aucun

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le |
|---|---|---|
| ctx/10-a.md | `A1`..`A2` | 2026-01-01 |

Lettres de fiche déjà prises : A. Un nouveau chantier en choisit une autre.
"""
INDEX_NIV3 = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
              "| `10-a.md` | on relit le chantier A |\n"
              "| `99-fantome.md` | jamais, il n'existe pas |\n")


def bac_niv3(t, feuille=True, index=INDEX_NIV3):
    proj = os.path.join(t, "niv3")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NIV3)
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), index)
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
    ecrire(os.path.join(proj, "ctx", "10-a.md"), "# Chantier A\n")
    if feuille:
        ecrire(os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"), feuille_ancienne())
    return proj


def compte(s, prefixe):
    return len([l for l in s.splitlines() if l.startswith(prefixe)])


with tempfile.TemporaryDirectory() as t:
    proj = bac_niv3(t)
    code, avant = appel(["niveau", proj])
    n = compte(avant, "ÉCART:")
    # VOI1 : la page du disque, un gabarit jamais régénéré, porte un lien cassé — le cinquième
    verifier("NIV3 avant : cinq écarts, dont le renvoi absent que rien ne sait corriger",
             code == 1 and n == 5 and "ÉCART: renvois: " in avant
             and "ÉCART: feuille: le bloc repliable" in avant and "ÉCART: clos: " in avant
             and "ÉCART: feuille: Markdown brut ou lien cassé" in avant,
             avant)

    code, pendant = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
    m = compte(pendant, "CORRIGÉ:")
    verifier("NIV3 : trois corrigés, le renvoi absent reste à la main",
             code == 1 and m == 3 and compte(pendant, "ÉCART:") == 1
             and "CORRIGÉ: feuille: bloc repliable des chantiers clos posé\n" in pendant
             and "CORRIGÉ: feuille: régénérée\n" in pendant
             and "CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:9" in pendant
             and pendant.rstrip().endswith("NIVEAU 3 corrigés · 1 à la main — %s" % proj), pendant)

    code, apres = appel(["niveau", proj])
    # la régénération corrige deux écarts d'un coup : la page, et le lien cassé qu'elle portait
    verifier("NIV3 après : %d écarts, %d corrigés, %d restants — le compte se ferme"
             % (n, m, n - m - 1),
             code == 1 and compte(apres, "ÉCART:") == n - m - 1 and "ÉCART: renvois: " in apres, apres)

    carte_niv3 = io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read()
    verifier("NIV3 : la table est partie, le titre et la phrase du gabarit la remplacent,"
             " les lettres prises restent",
             "| ctx/10-a.md |" not in carte_niv3 and "## Chantiers clos — dans l'index, pas ici" in carte_niv3
             and "Lettres de fiche déjà prises : A." in carte_niv3, carte_niv3)

    html_niv3 = io.open(os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"),
                        encoding="utf-8").read()
    verifier("NIV3 : le bloc repliable et son résumé sont posés, le style migré vers vlp.css (PLI3)",
             '<details class="clos">' in html_niv3 and '<span class="resume-clos">' in html_niv3
             and html_niv3.count('href="vlp.css"') == 1 and "<style>" not in html_niv3, html_niv3[:200])
    verifier("NIV3 : les lignes de ZONE:clos gardent les dix espaces que `clore` repère",
             '\n          <tr>\n' in html_niv3, "indentation changée")
    verifier("NIV3 : la feuille est aussi régénérée — la TODO du fichier d'état y passe",
             '<span class="titre">un truc</span>' in html_niv3 and "2026-09-18" in html_niv3, html_niv3[-600:])

    code, encore = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
    verifier("NIV3 : rejoué, il ne corrige plus rien — les corrections sont idempotentes",
             "NIVEAU 0 corrigés · 1 à la main" in encore, encore)

# La feuille absente : posée depuis le gabarit, puis régénérée.
with tempfile.TemporaryDirectory() as t:
    proj = bac_niv3(t, feuille=False)
    page = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
    code, s = appel(["niveau", proj])
    verifier("NIV3 : sans --ecrire, rien n'est posé", not os.path.exists(page)
             and "ÉCART: feuille: feuille de route introuvable :" in s, s)
    code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
    verifier("NIV3 : la feuille absente est posée depuis le gabarit puis régénérée",
             os.path.isfile(page) and "CORRIGÉ: feuille: posée depuis le gabarit" in s
             and '<span class="titre">un truc</span>' in io.open(page, encoding="utf-8").read(), s)

# L'index ne nomme pas un fichier de la table : la retirer le perdrait.
with tempfile.TemporaryDirectory() as t:
    proj = bac_niv3(t, index="# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
                           "| `08-etat.md` | on reprend |\n")
    code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
    verifier("NIV3 : une table dont l'index ne nomme pas les fichiers reste à la main",
             "ÉCART: clos: " in s and "CORRIGÉ: clos: " not in s
             and "| ctx/10-a.md |" in io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read(), s)

# Rien n'est écrit tant qu'un calcul peut échouer : un projet sans CHANTIER.md.
with tempfile.TemporaryDirectory() as t:
    code, s = appel(["niveau", os.path.join(t, "rien"), "--ecrire"])
    verifier("NIV3 : sans CHANTIER.md, --ecrire s'arrête sur une GARDE et n'écrit rien",
             code == 1 and s.startswith("GARDE: pas de CHANTIER.md dans ") and not os.listdir(t), s)

# IDX1 : la ligne clos a quitté l'index pour l'archive — les trois lecteurs de l'index la voient encore.
def idx1():
    verifier("IDX1 : l'archive se dérive de l'index, dans son dossier",
             mod.chemin_archive("ctx/00-INDEX.md") == "ctx/00-INDEX-archive.md"
             and mod.chemin_archive("00-INDEX.md") == "00-INDEX-archive.md", mod.chemin_archive("ctx/00-INDEX.md"))
    with tempfile.TemporaryDirectory() as t:
        rc = os.path.join(t, "rc")
        ecrire(os.path.join(rc, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(rc, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | on reprend |\n")
        ecrire(os.path.join(rc, "ctx", "00-INDEX-archive.md"),
               "| Fichier | Lire quand |\n|---|---|\n| `n.md` | chantier **clos** « N », `N1..N1` |\n")
        ecrire(os.path.join(rc, "ctx", "n.md"), "# Chantier N\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n"
               "<!-- FICHE:N1 -->\n## N1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        ecrire(os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html"),
               '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
               + ligne_close(mod.arrondi(999)).replace("Q1–Q2", "N1") + "        </tbody>\n      </table>\n")
        code, s = appel(["recompter", rc])
        verifier("IDX1 : recompter trouve le fichier par l'archive — mutant : ne lire que l'index",
                 code == 0 and s.splitlines()[0] == "N inscrit 999 · recompté gardé · écart +0 · gardé — sans session", s)

    with tempfile.TemporaryDirectory() as t:
        proj = bac_niv3(t, index="# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n| `08-etat.md` | on reprend |\n")
        ecrire(os.path.join(proj, "ctx", "00-INDEX-archive.md"),
               "| Fichier | Lire quand |\n|---|---|\n| `10-a.md` | chantier **clos** « A », `A1..A2` |\n")
        code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        verifier("IDX1 : niveau retire la table des clos que l'archive nomme — mutant : ne lire que l'index",
                 "CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:9" in s
                 and "| ctx/10-a.md |" not in io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read(), s)

    with tempfile.TemporaryDirectory() as t:
        ecrire(os.path.join(t, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(t, "ctx", "01-a.md"), "a\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `01-a.md` | on lit |\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX-archive.md"),
               "| Fichier | Lire quand |\n|---|---|\n| `20-mort.md` | chantier **clos** « M », `M1..M1` |\n")
        code, s = appel(["renvois", t])
        verifier("IDX1 : renvois lit l'archive, sans poids — mutant : archive non lue",
                 code == 1 and s == "ABSENT: ctx/00-INDEX-archive.md:3: 20-mort.md\n"
                 "POIDS CLAUDE.md absent/80 · CHANTIER.md 2/50 · index 3/80\nRENVOIS 2 nommés · 1 absents\n", s)


idx1()

# REP2 : retirer les chevrons d'une URL
with tempfile.TemporaryDirectory() as t:
    # Test 1 : champ retire les chevrons d'une URL entre chevrons
    carte_avec_chevrons = """# Chantier REP2
- **artefact du chantier** : <https://example.com/path>
"""
    carte_sans_chevrons = """# Chantier REP2
- **artefact du chantier** : https://example.com/path
"""
    carte_autre_chevrons = """# Chantier REP2
- **artefact du chantier** : <contexte>
"""

    lignes = carte_avec_chevrons.strip().split('\n')
    val = mod.champ(lignes, "artefact du chantier")
    verifier("REP2 : champ retire les chevrons d'une URL https",
             val == "https://example.com/path", "got: " + str(val))

    lignes = carte_sans_chevrons.strip().split('\n')
    val = mod.champ(lignes, "artefact du chantier")
    verifier("REP2 : champ retourne une URL sans chevrons inchangée",
             val == "https://example.com/path", "got: " + str(val))

    lignes = carte_autre_chevrons.strip().split('\n')
    val = mod.champ(lignes, "artefact du chantier")
    verifier("REP2 : champ retourne <contexte> inchangé",
             val == "<contexte>", "got: " + str(val))

    # Test 2 : ouvrir --artefact retire les chevrons
    proj = os.path.join(t, "proj-rep2")
    ecrire(os.path.join(proj, "CHANTIER.md"),
           """# Chantier courant
- **alias** : rep
- **fichier de fiches courant** : fiches.md
- **artefact du chantier** : aucun
""")
    ecrire(os.path.join(proj, "fiches.md"), """# Chantier REP2

## Le socle

---

## REP2 [ ] — à faire
""")
    ecrire(os.path.join(proj, "CLAUDE.md"), """| relire un chantier clos | exemple |
""")
    ecrire(os.path.join(proj, "context AI", "00-index.md"), "| `a` | b |\n")

    code, s = appel(["ouvrir", proj, "--fiches", "fiches.md", "--titre", "REP2", "--artefact", "<https://example.com/artifact>"])
    carte = io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read()
    verifier("REP2 : ouvrir retire les chevrons de --artefact",
             "- **artefact du chantier** : https://example.com/artifact" in carte, carte)

    # Test 3 : cmd_ouvrir avec URL sans chevrons
    proj2 = os.path.join(t, "proj-rep2b")
    ecrire(os.path.join(proj2, "CHANTIER.md"),
           """# Chantier courant
- **alias** : rep
- **fichier de fiches courant** : fiches.md
- **artefact du chantier** : aucun
""")
    ecrire(os.path.join(proj2, "fiches.md"), """# Chantier REP2

## Le socle

---

## REP2b [ ] — à faire
""")
    ecrire(os.path.join(proj2, "CLAUDE.md"), """| relire un chantier clos | exemple |
""")
    ecrire(os.path.join(proj2, "context AI", "00-index.md"), "| `a` | b |\n")

    code, s = appel(["ouvrir", proj2, "--fiches", "fiches.md", "--titre", "REP2b", "--artefact", "https://example.com/artifact"])
    carte2 = io.open(os.path.join(proj2, "CHANTIER.md"), encoding="utf-8").read()
    verifier("REP2 : ouvrir accepte une URL sans chevrons",
             "- **artefact du chantier** : https://example.com/artifact" in carte2, carte2)

# --- REP3 : `niveau` compte le Markdown brut et migre `ZONE:clos` -------------

# Une ligne close d'avant REP1 : gras et lien restés bruts, URL entre chevrons,
# et un `**` dans du code cité, qui ne se compte ni ne se convertit.
VIEILLE = ('          <tr>\n            <td><a href="&lt;https://v&gt;">Un <span class="mono">**c**</span></a>'
           ' <span class="badge" data-etat="clos">clos</span></td>\n'
           '            <td class="mono">A1–A2</td><td class="mono">2026-01-01</td>\n'
           '            <td class="mono">≈1,5k (1 500)</td>\n'
           '            <td>Livré **x** et [t](https://u)</td>\n          </tr>\n')


def visible(h):
    return re.sub(r"<[^>]+>", "", h)


def rangs_clos(page):
    html = io.open(page, encoding="utf-8").read()
    d, f = mod.zone(html, "clos", "<tbody>\n", "        </tbody>")
    return mod.lignes_clos(html[d:f])


with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "rep3")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE)
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
    page = mod.page_feuille(proj)  # le chemin tel que `niveau` l'affiche
    os.makedirs(os.path.dirname(page))
    shutil.copy(GABARIT_FEUILLE, page)
    appel(["feuille", proj, "--date", "2026-09-18"])

    code, s = appel(["niveau", proj, "--date", "2026-09-18"])
    verifier("REP3 : une feuille propre sort ses trois compteurs, à zéro, sans écart",
             code == 0 and "ÉCART:" not in s
             and "MARKDOWN 0 ** · 0 liens Markdown · 0 liens cassés — %s\n" % page in s, s)

    html = io.open(page, encoding="utf-8").read()
    d, f = mod.zone(html, "clos", "<tbody>\n", "        </tbody>")
    ecrire(page, html[:d] + VIEILLE + html[d:])
    code, s = appel(["niveau", proj, "--date", "2026-09-18"])
    # Le second écart (BTN5) : la ligne close a un coût, la feuille n'a pas encore la balise de couts.svg.
    verifier("REP3 : la ligne close brute se compte hors code cité, fait un écart, et nomme --ecrire",
             code == 1 and compte(s, "ÉCART:") == 2
             and "MARKDOWN 2 ** · 1 liens Markdown · 1 liens cassés — %s\n" % page in s
             and "ÉCART: feuille: Markdown brut ou lien cassé — « vlp.py niveau --ecrire »"
                 " convertit les lignes closes\n" in s, s)

    code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
    apres = io.open(page, encoding="utf-8").read()
    verifier("REP3 : --ecrire convertit la ligne close en place, et les compteurs tombent à zéro",
             code == 0 and "CORRIGÉ: feuille: 1 lignes closes converties\n" in s
             and "MARKDOWN 0 ** · 0 liens Markdown · 0 liens cassés — %s\n" % page in s
             and '<a href="&lt;URL de son artefact&gt;">' in apres, s)

    ligne = rangs_clos(page)[0]
    verifier("REP3 : aucun texte visible perdu, chaque URL dans un href, le code cité et les dix espaces intacts",
             visible(ligne) == visible(VIEILLE).replace("**x**", "x").replace("[t](https://u)", "t")
             and '<a href="https://v">' in ligne and '<a href="https://u">t</a>' in ligne
             and "<strong>x</strong>" in ligne and '<span class="mono">**c**</span>' in ligne
             and ligne.startswith("          <tr>\n"), ligne)

    code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
    verifier("REP3 : rejoué, --ecrire ne change plus rien — deux passes = une",
             io.open(page, encoding="utf-8").read() == apres and "CORRIGÉ: feuille:" not in s, s)

    carte = io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read()
    ecrire(os.path.join(proj, "CHANTIER.md"), carte.replace(
        "- **fichier de fiches courant** : aucun",
        "- **fichier de fiches courant** : ctx/40-w.md (W1..W1)\n"
        "- **artefact du chantier** : https://exemple/w")
        + "\nLettres de fiche déjà prises : A. Un nouveau chantier en choisit une autre.\n")
    ecrire(os.path.join(proj, "ctx", "40-w.md"), "# Chantier W — Un titre\n\n## W1 [x] — a\n")
    code, s = appel(["clore", proj, "--livre", "y", "--tokens", "950", "--date", "2026-09-19"])
    verifier("clore : une clôture sous 1 000, comptée une fois", code == 0 and "· chantier 950 · cumul 2 450 ·" in s, s)
    rangs = rangs_clos(page)
    verifier("REP3 : clore pose sa ligne au-dessus de la ligne convertie, sans la défaire",
             len(rangs) == 2 and "2026-09-19" in rangs[0] and rangs[1] == ligne, s)

# VOI1 : sans --ecrire, MARKDOWN compte la page du disque, pas la régénérée
with tempfile.TemporaryDirectory() as tv:
    projv = os.path.join(tv, "voi1")
    ecrire(os.path.join(projv, "CHANTIER.md"), CARTE_NETTE)
    ecrire(os.path.join(projv, "ctx", "00-INDEX.md"), INDEX_NET)
    ecrire(os.path.join(projv, "ctx", "08-etat.md"), ETAT_NIV)
    pagev = mod.page_feuille(projv)
    os.makedirs(os.path.dirname(pagev))
    shutil.copy(GABARIT_FEUILLE, pagev)
    appel(["feuille", projv, "--date", "2026-09-18"])
    htmlv = io.open(pagev, encoding="utf-8").read()
    d, f, _ = mod.zone_todo(htmlv)
    ecrire(pagev, htmlv[:d] + "          <tr><td>**x**</td></tr>\n" + htmlv[d:])
    code, s = appel(["niveau", projv, "--date", "2026-09-18"])
    verifier("VOI1 : sans --ecrire, le ** brut de la page du disque se compte, même si la régénération le fait tomber",
             "MARKDOWN 2 ** · 0 liens Markdown · 0 liens cassés — %s\n" % pagev in s, s)  # un **x** = deux **

# FEU2 : zone_todo s'arrête à la zone suivante — sur une feuille en cartes, jamais le <tbody> des clos
def test_zone_todo():
    CLOS_FEU2 = ('  <section>\n    <!-- ZONE:clos — les chantiers clos -->\n    <table><tbody>\n'
                 '          <tr><td>un clos</td></tr>\n        </tbody></table>\n  </section>\n')
    cartes_feu2 = ('  <section>\n    <!-- ZONE:todo — les chantiers possibles -->\n    <ol class="todo">\n'
                   '          <li class="carte-todo"><details><summary><span class="rang mono">29</span><span class="titre">'
                   '<span class="mono">FEU</span> — a</span><span class="meta mono">~4 fiches</span></summary>'
                   '<div class="detail">x</div></details></li>\n'
                   '          <li class="carte-todo"><details><summary><span class="rang mono">30</span><span class="titre">'
                   '<span class="mono">BTN</span> — b' + mod.BADGE_COURS + '</span><span class="meta mono">~5 fiches</span>'
                   '</summary><div class="detail">y</div></details></li>\n'
                   '        </ol>\n  </section>\n') + CLOS_FEU2
    d2, f2, forme2 = mod.zone_todo(cartes_feu2)
    verifier("FEU2 : cartes → forme cartes, fin avant ZONE:clos, badge relu sur le rang 30",
             forme2 == "cartes" and f2 < cartes_feu2.index("<!-- ZONE:clos") and cartes_feu2[d2:f2].count("carte-todo") == 2
             and mod.rang_en_cours(cartes_feu2[d2:f2], forme2) == "30",
             (d2, f2, forme2, cartes_feu2[d2:f2]))
    tableau_feu2 = ('  <section>\n    <!-- ZONE:todo — les chantiers possibles -->\n    <table><tbody>\n'
                    '          <tr><td class="mono">29</td><td><span class="mono">FEU</span> — a</td><td>x</td></tr>\n'
                    '          <tr><td class="mono">30</td><td><span class="mono">BTN</span> — b' + mod.BADGE_COURS
                    + '</td><td>y</td></tr>\n        </tbody></table>\n  </section>\n') + CLOS_FEU2
    d2, f2, forme2 = mod.zone_todo(tableau_feu2)
    verifier("FEU2 : tableau → forme tableau, mêmes bornes que zone(), badge relu sur le rang 30",
             forme2 == "tableau" and (d2, f2) == mod.zone(tableau_feu2, "todo", "<tbody>\n", "        </tbody>")
             and mod.rang_en_cours(tableau_feu2[d2:f2], forme2) == "30",
             (d2, f2, forme2))
    vide_feu2 = '  <section>\n    <!-- ZONE:todo — les chantiers possibles -->\n    <p>rien</p>\n  </section>\n' + CLOS_FEU2
    try:
        mod.zone_todo(vide_feu2)
        erreur_feu2 = None
    except ValueError as e:
        erreur_feu2 = str(e)
    verifier("FEU2 : ni tableau ni cartes dans la zone → ValueError, jamais le <tbody> des clos",
             erreur_feu2 is not None and "ZONE:todo" in erreur_feu2, erreur_feu2)

test_zone_todo()


def test_feuille_en_cartes():
    """FEU3 : une feuille d'avant, TODO en tableau et badge sur un rang, passe en cartes."""
    with tempfile.TemporaryDirectory() as tc:
        ecrire(os.path.join(tc, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : ctx/30-q.md (Q1..Q2)\n- **artefact du chantier** : https://exemple/q\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(tc, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Le `sh` | a \\|\\| b <c> | 2 fiches | — |\n| 4 | **Quatre** | rien | 1 fiche | 3 |\n"
               "| 7 | Sept | [un lien](https://x/y) | à cadrer | `E` |\n\n## Journal\n")
        ecrire(os.path.join(tc, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [x] — a\n## Q2 [ ] — b\n")
        gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read()
        d, f, _ = mod.zone_todo(gabarit)
        debut, fin = gabarit.rindex('<ol class="todo">', 0, d), f + len("        </ol>")
        tableau = ('<p>Un préambule gardé.</p>\n    <div class="tableau">\n      <table>\n        <thead>\n'
                   '          <tr><th>#</th><th>Chantier</th></tr>\n        </thead>\n        <tbody>\n'
                   '          <tr><td class="mono">3</td><td>vieux</td></tr>\n'
                   '          <tr><td class="mono">4</td><td>vieux' + mod.BADGE_COURS + '</td></tr>\n'
                   '        </tbody>\n      </table>\n    </div>')
        fdr = os.path.join(tc, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, gabarit[:debut] + tableau + gabarit[fin:])
        code, s = appel(["feuille", tc, "--date", "2026-09-27"])
        html = io.open(fdr, encoding="utf-8").read()
        d, f, forme = mod.zone_todo(html)
        zone_t = html[html.index("<!-- ZONE:todo"):html.index("<!-- ZONE:clos")]
        rangs = mod.todo_du_fichier(mod.lignes_de(os.path.join(tc, "ctx", "08-etat.md")))
        # « Dépend de » (5e cellule) passe en flèche à gauche de la carte (gabarit en colonnes).
        absentes = ([c for r in rangs for c in r[:4] if mod.cellule_md(c) not in html[d:f]]
                    + [r[4] for r in rangs if mod.depend_todo(r[4]) not in html[d:f]])
        verifier("FEU3 : tableau → cartes, une par rang, chaque cellule telle quelle (« Dépend de » en flèche),"
                 " badge sur la carte 4, préambule gardé",
                 code == 0 and forme == "cartes" and "<table" not in zone_t and "<tr" not in zone_t
                 and html[d:f].count('<li class="carte-todo">') == len(rangs) == 3 and not absentes
                 and html[d:f].count(mod.BADGE_COURS) == 1 and mod.rang_en_cours(html[d:f], forme) == "4"
                 and "<p>Un préambule gardé.</p>" in zone_t and zone_t.count("resume-todo") == 0,
                 (s, absentes, zone_t))
        code, s = appel(["feuille", tc, "--date", "2026-09-28"])
        verifier("FEU3 : 2e appel inchangée", code == 0 and "inchangée" in s, s)
        code, s = appel(["vigile", fdr])
        verifier("FEU3 : vigile sur la page en cartes", code == 0 and s.startswith("PAGE SAINE"), s)


test_feuille_en_cartes()


def test_sommaire():
    """FEU4 : sommaire et `id` des trois sections, posés une seule fois sur une feuille sans eux."""
    with tempfile.TemporaryDirectory() as ts:
        ecrire(os.path.join(ts, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : aucun\n\n"
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
        verifier("FEU4 : un sommaire sous l'en-tête, trois liens, chaque cible id une fois",
                 code == 0 and "sommaire" not in sans and 'id="' not in sans
                 and html.count('class="sommaire"') == 1 and html.count("<nav") == 1
                 and html.count('<a href="#') == 3
                 and all(html.count('href="#%s"' % n) == 1 and html.count('id="%s"' % n) == 1 for n in noms)
                 and html.index("</header>") < html.index("<nav") < html.index('id="encours"')
                 < html.index('id="todo"') < html.index('id="clos"'),
                 (s, html[:1500]))
        code, s = appel(["feuille", ts, "--date", "2026-09-28"])
        verifier("FEU4 : 2e appel inchangée", code == 0 and "inchangée" in s, s)


test_sommaire()

# UNI1 : clore utilise le total mesuré ; sans mesure, retombe sur --tokens
with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "uni")
    os.makedirs(proj)
    ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier de fiches courant** : ctx/50-u.md (U1..U1)\n- **artefact du chantier** : https://u\n\nLettres de fiche déjà prises : U (test).\n")
    ecrire(os.path.join(proj, "ctx", "50-u.md"), "# Chantier U — test\n\n## U1 [x] — a\n")
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `50-u.md` | on joue `U*` |\n")
    ecrire(os.path.join(proj, "CLAUDE.md"), "| T | O |\n|---|---|\n| jouer U | `ctx/50-u.md` **ouvert** |\n| relire un clos | `ctx/00-INDEX.md` |\n")
    page_u = os.path.join(proj, "ctx", "artefacts", "50-u.html")
    ecrire(page_u, open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read())
    code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "950", "--date", "2026-09-25"])
    verifier("UNI1 : sans mesure, --tokens utilisé, pas d'ÉCART", code == 0 and "chantier 950" in s and "ÉCART" not in s, s)

# UNI1 : mesuré, le total de la page gagne sur un --tokens faux, et le dit
with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "uni2")
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
    ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n- **index** : ctx/00-INDEX.md\n- **fichier de fiches courant** : ctx/50-u.md (U1..U1)\n- **artefact du chantier** : https://u\n\nLettres de fiche déjà prises : U (test).\n")
    ecrire(os.path.join(proj, "ctx", "50-u.md"), "# Chantier U — test\n\n## U1 [x] — a\n")
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| F | L |\n|---|---|\n| `50-u.md` | on joue `U*` |\n")
    ecrire(os.path.join(proj, "CLAUDE.md"), "| T | O |\n|---|---|\n| jouer U | `ctx/50-u.md` **ouvert** |\n| relire un clos | `ctx/00-INDEX.md` |\n")
    ecrire(os.path.join(proj, "ctx", "artefacts", "50-u.html"),
           open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read())
    feuille_u = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(feuille_u, open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read())
    regenerer_vrai = mod.regenerer
    mod.regenerer = lambda *x: (lambda r: r[:3] + ((4321, 3, None), r[4]))(regenerer_vrai(*x))
    try:
        code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "950", "--date", "2026-09-25"])
    finally:
        mod.regenerer = regenerer_vrai
    fu = open(feuille_u, encoding="utf-8").read()
    verifier("UNI1 : --tokens faux, ÉCART et le mesuré écrit sur la feuille", code == 0
             and "ÉCART tokens 950 donné · 4 321 mesuré — le mesuré fait foi" in s and "· chantier 4 321 ·" in s
             and "(4 321)" in fu and ">950<" not in fu, s + fu[-800:])

# Une feuille qui ne se régénère pas : les compteurs ne sont pas mesurés, et le disent.
with tempfile.TemporaryDirectory() as t:
    proj = os.path.join(t, "rep3b")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE.replace("- **fichier d'état** : ctx/08-etat.md\n", ""))
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
    code, s = appel(["niveau", proj])
    verifier("REP3 : sans fichier d'état, la ligne MARKDOWN dit « non mesuré »",
             code == 1 and "MARKDOWN non mesuré, la feuille ne se régénère pas — " in s
             and "ÉCART: feuille: fichier d'état introuvable : aucun\n" in s, s)



# Simplifier les tests filet
with tempfile.TemporaryDirectory() as t:
    def filet_test(json_obj):
        """Appelle vlp.py filet avec l'entrée JSON."""
        o, e = io.StringIO(), io.StringIO()
        code = mod.main(["filet"], o, io.StringIO(json.dumps(json_obj)), e)
        return code, o.getvalue(), e.getvalue()

    def creer_trans(chemin, tours):
        """Crée un transcript factice."""
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            for n in range(tours):
                d = {"message": {"id": f"m{n}", "usage": {"input_tokens": 100, "output_tokens": 50}}}
                f.write(json.dumps(d) + "\n")

    # Pas d'agent_id
    code, o, e = filet_test({"agent_type": "vlp:fiche"})
    verifier("filet : pas agent_id, muet", (code, o, e) == (0, "", ""), o + e)

    # agent_type ne contient pas 'fiche'
    code, o, e = filet_test({"agent_type": "autre", "agent_id": "a1"})
    verifier("filet : agent_type sans 'fiche', muet", (code, o, e) == (0, "", ""), o + e)

    # Transcript absent
    t_fwd = t.replace(os.sep, '/')
    code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/chef.jsonl"})
    verifier("filet : transcript absent, muet", (code, o, e) == (0, "", ""), o + e)

    # 77 tours / 80 max = 3 restants → avertissement
    sub_path = os.path.join(t, "s", "subagents", "agent-a1.jsonl")
    creer_trans(sub_path, 77)
    code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
    verifier("filet : 3 tours restants, avertissement",
             code == 0 and '"additionalContext": "Attention : 3 tours restants' in o, o + e)

    # 76 tours = 4 restants → muet
    creer_trans(sub_path, 76)
    code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
    verifier("filet : 4 tours restants, muet", code == 0 and o == "", o + e)

    # 78 tours = 2 restants → avertissement
    creer_trans(sub_path, 78)
    code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
    verifier("filet : 2 tours restants, avertissement",
             code == 0 and '"additionalContext": "Attention : 2 tours restants' in o, o + e)

    # Après un échec (PostToolUseFailure) : même avertissement, au nom de l'événement reçu
    creer_trans(sub_path, 77)
    code, o, e = filet_test({"hook_event_name": "PostToolUseFailure", "agent_type": "vlp:fiche",
                             "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
    verifier("filet : après un échec, avertissement au nom de PostToolUseFailure",
             code == 0 and '"hookEventName": "PostToolUseFailure"' in o
             and '"additionalContext": "Attention : 3 tours restants' in o, o + e)

    # TOU2 : une fois par tour — tampon `vlp-filet-<agent_id>-<tours>` dans un TAMPON_HOOKS neuf
    ancien_tampon = mod.TAMPON_HOOKS
    mod.TAMPON_HOOKS = tempfile.mkdtemp()
    try:
        def salve(*ids):
            """Un appel par id d'outil (entrées différentes) ; rend le nombre de sorties non vides."""
            return sum(bool(filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "tool_use_id": i,
                                        "transcript_path": t_fwd + "/s.jsonl"})[1]) for i in ids)
        creer_trans(sub_path, 77)
        verifier("TOU2 : deux appels du même tour, une seule sortie", salve("u1", "u2") == 1, "")
        creer_trans(sub_path, 78)
        verifier("TOU2 : un tour de plus, le filet avertit de nouveau", salve("u3") == 1, "")
        creer_trans(sub_path, 77)
        os.environ["VLP_SANS_TAMPON"] = "1"
        try:
            n = salve("u4", "u5")
        finally:
            del os.environ["VLP_SANS_TAMPON"]
        verifier("TOU2 : VLP_SANS_TAMPON, deux sorties", n == 2, str(n))
    finally:
        shutil.rmtree(mod.TAMPON_HOOKS, ignore_errors=True)
        mod.TAMPON_HOOKS = ancien_tampon

    # Un vrai chemin de plus de 260 caractères, bâti comme dans FIL1 : sans le préfixe,
    # isfile et open y disent absent un transcript présent ; le filet doit avertir quand même
    if os.name != "nt":
        print("SAUTÉ: hors Windows — le chemin long du filet n'est pas testé (le préfixe est propre à Windows)")
    else:
        prefixe = chr(92) * 2 + "?" + chr(92)    # le préfixe des chemins longs, bâti sans échappement
        long_base = os.path.join(os.path.abspath(t), "l" * (254 - len(os.path.abspath(t))))
        long_sub = os.path.join(long_base, "subagents", "agent-a1.jsonl")
        os.makedirs(prefixe + os.path.dirname(long_sub))
        with open(prefixe + long_sub, "w", encoding="utf-8") as f:
            for n in range(77):
                f.write(json.dumps({"message": {"id": f"m{n}", "usage": {"input_tokens": 1}}}) + "\n")
        try:
            code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1",
                                     "transcript_path": long_base.replace(os.sep, "/") + ".jsonl"})
            verifier(f"filet : transcript à {len(long_sub)} caractères, avertissement",
                     len(long_sub) > 260 and '"additionalContext": "Attention : 3 tours restants' in o, o + e)
        finally:    # même après un écart : sans le préfixe, le nettoyage du dossier temporaire échouerait
            shutil.rmtree(prefixe + long_base)


# contrat (chantier CON) : deux sous-agents fabriqués, un propre et un qui commite par `git -C`
with tempfile.TemporaryDirectory() as t:
    def agent(id_, texte, commandes, type_="vlp:fiche"):
        chemin = os.path.join(t, "p", "sess", "subagents", f"agent-{id_}.jsonl")
        lignes = [{"message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": outil, "input": {"command": c}}]}} for outil, c in commandes]
        lignes.append({"message": {"role": "assistant", "content": [{"type": "text", "text": texte}]}})
        ecrire(chemin, "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in lignes))
        ecrire(chemin[:-len(".jsonl")] + ".meta.json", json.dumps({"agentType": type_}))
        return chemin

    ecrire(os.path.join(t, "p", "sess.jsonl"), json.dumps({"timestamp": "2026-09-24T10:00:00Z"}) + "\n")
    propre = agent("propre", "FAITE — X1 cochée.", [("Bash", 'py vlp.py cocher "f.md" X1'),
                                                     ("PowerShell", "git status; git log -1")])
    sale = agent("sale", "✅ X1 faite", [("Bash", 'git -C "C:/a b/proj" commit -m "X1 : fin"'),
                                        ("PowerShell", "git add -A"), ("Bash", "echo git")])
    code, s = appel(["contrat", propre, sale])
    verifier("contrat : témoin propre, aucun appel qui écrit dans Git",
             "propre vlp:fiche 2026-09-24T10:00:00Z FAITE git 0 bloqué 0\n" in s, s)
    verifier("contrat : témoin sale, git -C … commit et git add comptés, sans tool_result : écrits",
             "sale vlp:fiche 2026-09-24T10:00:00Z ✅ git 2 bloqué 0\n" in s, s)
    verifier("contrat : bilan", code == 0 and s.endswith(
        "CONTRAT 2 sous-agents · 1 écrivent dans Git · 0 bloqués par le gardien · "
        "1 sans statut en tête · 0 interrompus\n"), s)
    code, s = appel(["contrat", propre, "--depuis", "2026-09-24T10:00:01+00:00"])
    verifier("contrat : --depuis écarte une session partie avant",
             code == 0 and s == "CONTRAT 0 sous-agents · 0 écrivent dans Git · 0 bloqués par le gardien · "
             "0 sans statut en tête · 0 interrompus\n", s)
    code, s = appel(["contrat", "--depuis", "pas-une-borne-zz"])
    verifier("contrat : borne illisible, GARDE", code == 1 and s.startswith("GARDE: --depuis pas-une-borne-zz"), s)


# ENQ1 : un appel refusé par le gardien compte en bloqué, pas en écrit ; un interrompu pas en sans-statut
with tempfile.TemporaryDirectory() as t:
    def ligne_agent(id_, blocs):
        chemin = os.path.join(t, "p2", "sess", "subagents", f"agent-{id_}.jsonl")
        ecrire(chemin, "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in blocs))
        ecrire(chemin[:-len(".jsonl")] + ".meta.json", json.dumps({"agentType": "vlp:fiche"}))
        return chemin

    ecrire(os.path.join(t, "p2", "sess.jsonl"), json.dumps({"timestamp": "2026-09-24T10:00:00Z"}) + "\n")
    refusee = ligne_agent("refusee", [
        {"message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "tu1", "name": "Bash", "input": {"command": "git add -A"}}]}},
        {"message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tu1", "content": mod.REFUS_GIT}]}},
        {"message": {"role": "assistant", "content": [{"type": "text", "text": "RETOUR — bloquée par le gardien."}]}}])
    ecrit = ligne_agent("ecrit", [
        {"message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "tu2", "name": "Bash", "input": {"command": "git add -A"}}]}},
        {"message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tu2", "content": "add 'f.md'"}]}},
        {"message": {"role": "assistant", "content": [{"type": "text", "text": "FAITE — X1 cochée."}]}}])
    avant = ligne_agent("avant", [
        {"message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "tu3", "name": "Bash", "input": {"command": "git commit -m x"}}]}},
        {"message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tu3", "content": mod.REFUS_GIT_AVANT}]}},
        {"message": {"role": "assistant", "content": [{"type": "text", "text": "RETOUR — bloquée."}]}}])
    interrompue = ligne_agent("interrompue", [
        {"message": {"role": "assistant", "content": [{"type": "text", "text": "Je lance le dernier essai…"}]}},
        {"message": {"role": "user", "content": "[Request interrupted by user]"}}])
    code, s = appel(["contrat", refusee, ecrit, avant, interrompue])
    verifier("ENQ1 : bilan — refusé compté en bloqué (phrase d'avant VRB comprise), interrompu pas en "
             "sans-statut — mutant : compter un refus comme une écriture, ou oublier REFUS_GIT_AVANT, le fait tomber",
             code == 0 and s.endswith("CONTRAT 4 sous-agents · 1 écrivent dans Git · 2 bloqués par le gardien · "
                                       "0 sans statut en tête · 1 interrompus\n"), s)
    verifier("ENQ1 : la ligne du refusé porte git 0 bloqué 1",
             "refusee vlp:fiche 2026-09-24T10:00:00Z RETOUR git 0 bloqué 1\n" in s, s)
    verifier("ENQ1 : la ligne de l'interrompu porte (interrompu)",
             "interrompue vlp:fiche 2026-09-24T10:00:00Z (interrompu) git 0 bloqué 0\n" in s, s)



# gardien (chantier CON4) : PreToolUse refuse l'écriture Git, SubagentStop renvoie sur statut ou case
with tempfile.TemporaryDirectory() as t:
    def gardien(d):
        o = io.StringIO()
        code = mod.main(["gardien"], o, io.StringIO(d if isinstance(d, str) else json.dumps(d)))
        return code, o.getvalue()

    fiche = {"agent_id": "a1", "agent_type": "vlp:fiche"}
    relecture = {"agent_id": "a2", "agent_type": "vlp:relecture"}
    commit = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
              "tool_input": {"command": 'git -C "C:/a b" commit -m "X1 : fin"'}}
    code, s = gardien(dict(commit, **relecture))
    verifier("gardien : sous-agent vlp:relecture git commit refusé", code == 0 and '"permissionDecision": "deny"' in s and "vlp:relecture" in s, s)
    code, s = gardien(dict(fiche, **commit))
    verifier("gardien : git -C … commit refusé pour vlp:fiche", code == 0 and '"permissionDecision": "deny"' in s and "vlp:fiche" in s, s)
    code, s = gardien(dict(relecture, hook_event_name="PreToolUse", tool_name="Bash",
                           tool_input={"command": "git diff HEAD~1"}))
    verifier("gardien : relecteur git diff laissé passer", (code, s) == (0, ""), s)
    code, s = gardien(dict(fiche, hook_event_name="PreToolUse", tool_name="PowerShell",
                           tool_input={"command": "git status; git log -1"}))
    verifier("gardien : fiche git status laissé passer", (code, s) == (0, ""), s)
    verifier("gardien : entrée illisible, muet", gardien("pas du json") == (0, ""), "")
    verifier("gardien : JSON qui n'est pas un objet, muet",
             gardien('[43, "sonde"]') == (0, "") and gardien('"x"') == (0, ""), "")
    verifier("gardien : tool_input ou agent_type qui ne sont pas ce qu'on attend, muet", all(
        gardien(dict(agent, hook_event_name="PreToolUse", tool_name="Bash", tool_input=ti)) == (0, "")
        for agent in (fiche, relecture) for ti in ("git commit", ["git commit"], 7)) and gardien(dict(
            commit, agent_id="a3", agent_type=["vlp:relecture"])) == (0, ""), "")

    proj = os.path.join(t, "proj")
    ecrire(os.path.join(proj, "CHANTIER.md"), CHANTIER % ("px", "f.md (X1..X1)"))
    ecrire(os.path.join(proj, "f.md"), "# X\n\n<!-- FICHE:X1 -->\n## X1 [ ] — une\n<!-- /FICHE -->\n")
    trans = os.path.join(t, "agent-a1.jsonl")
    ecrire(trans, json.dumps({"message": {"role": "user", "content": "Fiche à jouer :\n\nX1\n\nKit : k"}},
                             ensure_ascii=False) + "\n")
    fin = dict(fiche, hook_event_name="SubagentStop", stop_hook_active=False, cwd=proj,
               agent_transcript_path=trans)
    code, s = gardien(dict(fin, last_assistant_message="Parfait, la fiche est faite."))
    verifier("gardien : statut absent, renvoyé", '"decision": "block"' in s and "« Parfait, »" in s, s)
    code, s = gardien(dict(fin, last_assistant_message="Parfait.", stop_hook_active=True))
    verifier("gardien : déjà renvoyé une fois, laissé", (code, s) == (0, ""), s)
    code, s = gardien(dict(fin, last_assistant_message="FAITE — X1.", stop_hook_active=True))
    verifier("gardien : FAITE sur case vide sous stop_hook_active, renvoyé", '"decision": "block"' in s and "case de X1 est vide" in s, s)
    code, s = gardien(dict(fin, last_assistant_message="FAITE — X1."))
    verifier("gardien : FAITE sur case vide, renvoyé", '"decision": "block"' in s and "case de X1 est vide" in s, s)
    ecrire(os.path.join(proj, "f.md"), "# X\n\n<!-- FICHE:X1 -->\n## X1 [x] — une\n<!-- /FICHE -->\n")
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le gardien sur HEAD n'est pas testé")
    else:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "départ"]):
            subprocess.run(["git"] + args, cwd=proj, env=env, check=True, capture_output=True)
        code, s = gardien(dict(fin, last_assistant_message="FAITE — X1."))
        verifier("gardien : FAITE sur case cochée, sans commit de fiche, laissé", (code, s) == (0, ""), s)
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "X1 : une"], cwd=proj, env=env, check=True)
        code, s = gardien(dict(fin, last_assistant_message="FAITE — X1."))
        verifier("gardien : HEAD nomme la fiche, renvoyé", '"decision": "block"' in s and "tu as commité" in s, s)
    fin_relecture = dict(relecture, hook_event_name="SubagentStop", stop_hook_active=False, cwd=proj,
                         agent_transcript_path=trans)
    code, s = gardien(dict(fin_relecture, last_assistant_message="ACCEPTÉE — tout va bien"))
    verifier("gardien : relecteur ACCEPTÉE muet", (code, s) == (0, ""), s)
    code, s = gardien(dict(fin_relecture, last_assistant_message="REFUSÉE — erreur"))
    verifier("gardien : relecteur REFUSÉE muet", (code, s) == (0, ""), s)
    code, s = gardien(dict(fin, last_assistant_message="RETOUR — x\n\n---\n✅ Tout va bien"))
    verifier("gardien : fiche jauge « Tout va bien », renvoyée", '"decision": "block"' in s and "« En résumé » ou une jauge" in s, s)
    code, s = gardien(dict(fin, last_assistant_message="RETOUR — x\n\n---\n✅ Tout va bien", stop_hook_active=True))
    verifier("gardien : fiche jauge sous stop_hook_active, muet", (code, s) == (0, ""), s)
    code, s = gardien(dict(fin_relecture, last_assistant_message="ACCEPTÉE — ok\nEn résumé : y"))
    verifier("gardien : relecteur « En résumé », renvoyé", '"decision": "block"' in s and "« En résumé » ou une jauge" in s, s)
    code, s = gardien(dict(fin_relecture, last_assistant_message="ACCEPTÉE — ok"))
    verifier("gardien : relecteur sans « En résumé » ni jauge, muet", (code, s) == (0, ""), s)
    # JUG2 : la pièce de JUG1 se lit au journal, jamais recopiée ici (elle porte des chemins de machine)
    with open(os.path.join(RACINE, "context AI", "08-etat.md"), encoding="utf-8") as f:
        piece = re.search(r"La pièce, pour `JUG2` :\n\n```text\n(.*?)\n```", f.read(), re.S)
    piece = piece.group(1) if piece else ""
    code, s = gardien(dict(fin_relecture, last_assistant_message=piece))
    verifier("gardien : relecteur de FOR3 qui cite la jauge en prose (JUG1), muet",
             piece.startswith("ACCEPTÉE") and "« Tout va bien »" in piece and (code, s) == (0, ""), s or piece[:80])
    code, s = gardien(dict(fin_relecture, last_assistant_message=(
        "ACCEPTÉE — ok\n\n✅ **Tout va bien** — relu\n\n**En résumé**\n\nLa fiche tient.")))
    verifier("gardien : relecteur ACCEPTÉE puis résumé à part, renvoyé",
             '"decision": "block"' in s and "« En résumé » ou une jauge" in s, s)
    # Mutation test : les tests « renvoyé » reposent sur forme_texte (chantier FOR3)
    code, s = gardien(dict(fin, last_assistant_message="RETOUR — Pas bonne action"))
    verifier("gardien : fiche « Pas bonne » (pas jauge), muet — substring bug", (code, s) == (0, ""), s)
    code, s = gardien(dict(fin, last_assistant_message="RETOUR — Grosse bonne nouvelle"))
    verifier("gardien : fiche « Grosse bonne » (pas jauge), muet — substring bug", (code, s) == (0, ""), s)


# hooks.json : le filet sur tout outil, après un succès et après un échec ; hook sur les écritures
with open(os.path.join(RACINE, "hooks", "hooks.json"), encoding="utf-8") as f:
    crochets = json.load(f)["hooks"]


def paire(groupe, *sous):
    """Les deux commandes d'un groupe : python3 puis py, sur `vlp.py <sous>`."""
    return [(h.get("type"), h.get("command"), h.get("args")) for h in groupe.get("hooks", [])] == [
        ("command", c, ["${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py", *sous]) for c in ("python3", "py")]


succes, echec = crochets.get("PostToolUse", []), crochets.get("PostToolUseFailure", [])
verifier("hooks.json : filet sur tout outil après un succès et après un échec, hook sur Write|Edit",
         len(succes) == 3 and len(echec) == 2
         and any(g.get("matcher") == "*" and paire(g, "filet") for g in succes)
         and any(g.get("matcher") == "Write|Edit" and paire(g, "hook") for g in succes)
         and echec[0].get("matcher") == "*" and paire(echec[0], "filet"),
         json.dumps(crochets, ensure_ascii=False))
verifier("hooks.json : attente sur Artifact après un succès et après un échec (chantier LOC)",
         any(g.get("matcher") == "Artifact" and paire(g, "attente", "hook") for g in succes)
         and echec[1].get("matcher") == "Artifact" and paire(echec[1], "attente", "hook"),
         json.dumps(crochets, ensure_ascii=False))
avant, arret = crochets.get("PreToolUse", []), crochets.get("SubagentStop", [])
verifier("hooks.json : gardien avant Bash|PowerShell et à l'arrêt d'un sous-agent",
         len(avant) == 2 and avant[0].get("matcher") == "Bash|PowerShell" and paire(avant[0], "gardien")
         and len(arret) == 1 and arret[0].get("matcher") == "*" and paire(arret[0], "gardien"),
         json.dumps(crochets, ensure_ascii=False))
verifier("hooks.json : vigile avant Artifact (chantier VID)",
         avant[1].get("matcher") == "Artifact" and paire(avant[1], "vigile"),
         json.dumps(crochets, ensure_ascii=False))


def tester_canaux(g):
    # Deux canaux de nuit (chantier NUI) : chacun ne retire que ses worktrees.
    for canal in ("A", "B"):
        os.environ["VLP_CANAL"] = canal
        appel(["relecture", "X1"])
    noms = [os.path.basename(l.split(" ")[0].rstrip("/\\")) for l in g("worktree", "list").splitlines()[1:]]
    os.environ["VLP_CANAL"] = "B"
    retire_b = appel(["relecture", "--retirer"])
    reste_a = [os.path.basename(l.split(" ")[0].rstrip("/\\")) for l in g("worktree", "list").splitlines()[1:]]
    del os.environ["VLP_CANAL"]
    verifier("relecture : canaux — chacun ne retire que ses worktrees",
             len(noms) == 4 and sum(n.startswith("vlp-relecture-A-") for n in noms) == 2
             and sum(n.startswith("vlp-relecture-B-") for n in noms) == 2 and retire_b == (0, "RETIRÉ 2\n")
             and len(reste_a) == 2 and all(n.startswith("vlp-relecture-A-") for n in reste_a),
             "%s %s %s" % (noms, retire_b, reste_a))
    verifier("relecture : sans canal, --retirer retire tout", appel(["relecture", "--retirer"]) == (0, "RETIRÉ 2\n")
             and len(g("worktree", "list").splitlines()) == 1, g("worktree", "list"))


# relecture (chantier REV) : un dépôt à part, et ses worktrees dans le dossier temporaire du test
# (`tempfile.tempdir`) — un test qui échoue n'en laisse aucun dans celui du système.
if not shutil.which("git"):
    print("SAUTÉ: git absent — relecture n'est pas testée")
else:
    with tempfile.TemporaryDirectory() as t:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        depot = os.path.join(t, "r")

        def g(*args):
            return subprocess.run(["git"] + list(args), cwd=depot, env=env, check=True, capture_output=True,
                                  encoding="utf-8").stdout

        def lu(*chemin):
            c = os.path.join(*chemin)
            return mod.lire(c) if os.path.isfile(c) else None

        FICHE_X = ("# Chantier X\n\n## Le socle commun\n\nSocle X.\n\n## L'ordre des fiches\n\n---\n\n"
                   "<!-- FICHE:X1 -->\n## X1 %s — relire\n\n**Fichiers** : `a.py` — et rien d'autre.\n\n"
                   "**Prompt**\nb.py n'est pas nommé.\n<!-- /FICHE -->\n")
        ecrire(os.path.join(depot, "CHANTIER.md"), CHANTIER % ("px", "f.md (X1..X1)") + "- **fichier d'état** : ctx d/etat.md\n")
        ecrire(os.path.join(depot, "f.md"), FICHE_X % "[ ]")
        ecrire(os.path.join(depot, "a.py"), "a\n")
        ecrire(os.path.join(depot, "ctx d", "etat.md"), "journal\n")
        g("init", "-q")
        g("add", "-A")
        g("commit", "-q", "-m", "init")
        # Une fiche finie, pas encore commitée : a.py changé, b.py nouveau, la case cochée.
        ecrire(os.path.join(depot, "a.py"), "a2\n")
        ecrire(os.path.join(depot, "b.py"), "b\n")
        ecrire(os.path.join(depot, "f.md"), FICHE_X % "[x]")
        ecrire(os.path.join(depot, "ctx d", "etat.md"), "journal\nune décision\n")  # le journal, jamais hors fiche (REV7)
        tete, etat = g("rev-parse", "HEAD"), g("status", "--porcelain")
        ici, tmp = os.getcwd(), tempfile.tempdir
        tempfile.tempdir = t
        os.chdir(depot)
        try:
            code, s = appel(["relecture", "X1"])
            vu = dict(l.split("=", 1) for l in s.splitlines() if l.startswith(("APRÈS=", "AVANT=")))
            apres, avant = vu.get("APRÈS", "?"), vu.get("AVANT", "?")
            verifier("relecture : l'instantané prend l'arbre sans bouger HEAD", code == 0
                     and g("rev-parse", "HEAD") == tete and g("status", "--porcelain") == etat
                     and lu(apres, "a.py") == "a2\n" and lu(apres, "b.py") == "b\n"
                     and lu(avant, "a.py") == "a\n" and lu(avant, "b.py") is None, s + g("status", "--porcelain"))
            reperes = [s.find(r) for r in ("APRÈS=", "AVANT=", "Socle X.", "--- socle, lignes : ", "## X1 [x] — relire",
                                           "--- fiche, lignes : ", "M\ta.py", "HORS FICHE", "diff --git")]
            verifier("relecture : un fichier hors fiche",
                     [l for l in s.splitlines() if l.startswith("HORS FICHE")] == ["HORS FICHE b.py"]
                     and -1 not in reperes and reperes == sorted(reperes)
                     and "\nFICHIER=" not in "\n" + s, s)  # FFE
            code, s = appel(["relecture", "--retirer"])
            verifier("relecture : --retirer", code == 0 and s == "RETIRÉ 2\n"
                     and len(g("worktree", "list").splitlines()) == 1, s + g("worktree", "list"))
            g("add", "-A")
            g("commit", "-q", "-m", "X1 : relire")
            appel(["relecture", "X1", "--sha", "HEAD"])
            code, s = appel(["relecture", "X1", "--sha", "HEAD"])
            liste = g("worktree", "list")
            verifier("relecture --sha : le commit contre son parent, ceux de l'appel d'avant retirés", code == 0
                     and "M\ta.py\nA\tb.py\nM\tctx d/etat.md\nM\tf.md\nHORS FICHE b.py\ndiff --git" in s
                     and len(liste.splitlines()) == 3 and appel(["relecture", "--retirer"]) == (0, "RETIRÉ 2\n"),
                     s + liste)
            tester_canaux(g)
            gardes = [appel(["relecture", "X9"]), appel(["relecture", "X1", "--sha", "0badc0de"])]
            mod.GIT = "git-absent-vlp"
            gardes.append(appel(["relecture", "X1"]))
            mod.GIT = "git"
            verifier("relecture : fiche absente, commit inconnu, sans Git — GARDE, sort 1, aucun worktree",
                     all(c == 1 and s.startswith("GARDE: ") for c, s in gardes)
                     and len(g("worktree", "list").splitlines()) == 1, gardes)
        finally:
            mod.GIT = "git"
            tempfile.tempdir = tmp
            os.chdir(ici)


# pre-commit (chantier REV) : lancé par `git commit`, dans un dépôt où le plugin est copié, ses .md en CRLF —
# comme une copie de `relecture` quand core.autocrlf vaut true.
if not shutil.which("git"):
    print("SAUTÉ: git absent — le hook pre-commit n'est pas testé")
else:
    with tempfile.TemporaryDirectory() as t:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        depot = os.path.join(t, "plugin")
        for nom in (".claude-plugin", ".githooks", "agents", "hooks", "skills"):
            shutil.copytree(os.path.join(RACINE, nom), os.path.join(depot, nom))
        shutil.copy(os.path.join(RACINE, ".gitattributes"), depot)
        for dossier, _, noms in os.walk(depot):
            for nom in (n for n in noms if n.endswith(".md")):
                with open(os.path.join(dossier, nom), "rb") as f:
                    octets = f.read().replace(b"\r\n", b"\n")
                with open(os.path.join(dossier, nom), "wb") as f:
                    f.write(octets.replace(b"\n", b"\r\n"))

        def git(*args):
            r = subprocess.run(["git"] + list(args), cwd=depot, env=env, capture_output=True, encoding="utf-8",
                               errors="replace")
            return r.returncode, r.stdout + r.stderr

        git("init", "-q")
        git("config", "core.hooksPath", ".githooks")
        git("add", "-A")
        code, s = git("commit", "-q", "-m", "copie")
        # L'app Claude en MSIX : son claude.exe n'est dans %APPDATA% que pour les processus qu'elle lance.
        paquet = os.environ.get("LOCALAPPDATA") and glob.glob(os.path.join(
            os.environ["LOCALAPPDATA"], "Packages", "Claude_*", "LocalCache", "Roaming", "Claude", "claude-code", "*",
            "claude.exe"))
        if not paquet:
            print("SAUTÉ: pas de claude.exe sous Packages\\Claude_* — la recherche hors de l'app n'est pas testée")
        else:
            verifier("hook : claude trouvé hors de l'app", "validate sauté" not in s, s)
        if "validate sauté" in s:
            print("SAUTÉ: claude introuvable — le hook pre-commit n'est pas testé")
        else:
            verifier("hook : une copie en CRLF passe", code == 0, s)
            ecrire(os.path.join(depot, ".claude-plugin", "plugin.json"), "{")
            git("add", "-A")
            code, s = git("commit", "-q", "-m", "casse")
            verifier("hook : plugin.json cassé est nommé", code == 1
                     and "pre-commit : .claude-plugin/plugin.json invalide" in s and "marketplace.json" not in s, s)
        code, s = git("check-attr", "eol", "--", "skills/chantier/SKILL.md")
        verifier(".gitattributes : les .md en LF", s == "skills/chantier/SKILL.md: eol: lf\n", s)
        # JNT2 : les joints publiés en LF dans tout clone — un worktree en CRLF changeait leurs octets
        code, s = git("check-attr", "eol", "--", "templates/vlp.css", "templates/vlp.js", "a/couts.svg")
        verifier(".gitattributes : les joints (.css, .js, .svg) en LF", s == "templates/vlp.css: eol: lf\n"
                 "templates/vlp.js: eol: lf\na/couts.svg: eol: lf\n", s)

# GLO1 : forme et poids dans les transcriptions
with tempfile.TemporaryDirectory() as t:
    sa = os.path.join(t, "sa.jsonl")
    sb = os.path.join(t, "sb.jsonl")
    # Transcription 1 : User de 100 caractères + "FAITE — … En résumé … Tout va bien"
    with open(sa, "w", encoding="utf-8") as f:
        # le format réel : une entrée de premier niveau, pas un champ de `message`
        f.write(json.dumps({"type": "attachment", "attachment": {
            "type": "instructions", "files": [{
                "type": "User", "path": "user.md", "content": "x" * 100
            }]
        }}) + "\n")
        f.write(json.dumps({"type": "assistant", "requestId": "r2", "message": {
            "role": "assistant", "content": [{
                "type": "text", "text": "FAITE — début En résumé détails Tout va bien fin"
            }]
        }}) + "\n")
    # Transcription 2 : sans attachements + "Parfait"
    with open(sb, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "assistant", "requestId": "r1", "message": {
            "role": "assistant", "content": [{
                "type": "text", "text": "Parfait"
            }]
        }}) + "\n")
    # Créer les .meta.json
    meta_a = sa[:-len(".jsonl")] + ".meta.json"
    meta_b = sb[:-len(".jsonl")] + ".meta.json"
    ecrire(meta_a, json.dumps({"agentType": "vlp:fiche"}))
    ecrire(meta_b, json.dumps({"agentType": "vlp:relecture"}))
    # Créer la structure de répertoires pour que le motif glob trouve les fichiers
    proj_dir = os.path.join(t, "projects", "test", "test", "subagents")
    os.makedirs(proj_dir)
    shutil.move(sa, os.path.join(proj_dir, "agent-id1.jsonl"))
    shutil.move(sb, os.path.join(proj_dir, "agent-id2.jsonl"))
    shutil.move(meta_a, os.path.join(proj_dir, "agent-id1.meta.json"))
    shutil.move(meta_b, os.path.join(proj_dir, "agent-id2.meta.json"))
    sa = os.path.join(proj_dir, "agent-id1.jsonl")
    sb = os.path.join(proj_dir, "agent-id2.jsonl")
    # Appel direct (pas par glob)
    code, s = appel(["forme", "--regle", "tout", sa, sb])     # le texte entier : la mesure d'avant JUG2
    lignes = s.strip().split("\n")
    verifier("forme : deux transcriptions, bilan attendu", code == 0
             and len(lignes) == 3  # deux lignes de données + une ligne de bilan
             and lignes[2].startswith("FORME 2 sous-agents · user 50 car. · resume 1 · jauge 1 · tete 1"),
             s)

# GLO1 (JUG1) : forme_texte ne juge que la partie du texte que dit sa règle
cite = "FAITE — la fiche cite « En résumé » et « Pas bon » en milieu de phrase."
verifier("forme_texte tete : une citation en milieu de phrase ne compte pas",
         mod.forme_texte(cite, "tete") == (0, 0), mod.forme_texte(cite, "tete"))
a_part = "✅ **Tout va bien** — fait\n\n**En résumé**\n\nLa fiche est faite."
verifier("forme_texte tete : le résumé à part, jauge en tête",
         mod.forme_texte(a_part, "tete") == (1, 1), mod.forme_texte(a_part, "tete"))
verifier("forme_texte tiret : seul l'après-dernier --- est jugé",
         mod.forme_texte("x\n---\n✅ Tout va bien", "tiret") == (0, 1),
         mod.forme_texte("x\n---\n✅ Tout va bien", "tiret"))

# GLO1 (FOR1) : forme --depuis filtre sur le départ de la transcription, pas de la session
with tempfile.TemporaryDirectory() as t:
    # Créer la structure de répertoires pour que le motif glob trouve les fichiers
    proj_dir = os.path.join(t, "projects", "test", "test", "subagents")
    os.makedirs(proj_dir)
    # Transcription de sous-agent avec timestamp 2026-09-25T12:00:00Z
    sc = os.path.join(proj_dir, "agent-for1.jsonl")
    with open(sc, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "attachment", "timestamp": "2026-09-25T12:00:00Z", "attachment": {
            "type": "instructions", "files": [{
                "type": "User", "path": "user.md", "content": "test"
            }]
        }}) + "\n")
        f.write(json.dumps({"type": "assistant", "requestId": "r1", "message": {
            "role": "assistant", "content": [{
                "type": "text", "text": "FAITE — test En résumé test Tout va bien"
            }]
        }}) + "\n")
    # Créer le .meta.json
    meta_c = sc[:-len(".jsonl")] + ".meta.json"
    ecrire(meta_c, json.dumps({"agentType": "vlp:fiche"}))
    # Parent session avec timestamp 2026-09-25T08:00:00Z (antérieur à --depuis 10:00:00Z)
    parent_session = os.path.join(t, "session.jsonl")
    with open(parent_session, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "session", "timestamp": "2026-09-25T08:00:00Z"}) + "\n")
    # Appel avec --depuis après le timestamp du sous-agent mais avant celui de la parent session
    code, s = appel(["forme", "--depuis", "2026-09-25T10:00:00Z", sc])
    verifier("forme --depuis filtre sur le départ du sous-agent", code == 0
             and "FORME 1 sous-agents" in s,
             s)

# Test de carte avec TODO
test_carte_relecteur()
test_carte_todo()
test_carte_methode()

# PYT1 : premier lancement des hooks — restaurer TAMPON_HOOKS pour ce test
def gardien_test(texte):
    """Appelle vlp.py gardien avec l'entrée JSON."""
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["gardien"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()

def test_premier_lancement():
    # Sauvegarder et restaurer TAMPON_HOOKS pour ce test
    ancien_tampon = mod.TAMPON_HOOKS
    mod.TAMPON_HOOKS = tempfile.mkdtemp()     # neuf : un tampon d'un run d'avant ferait taire le 1er appel

    try:
        # Entrée PreToolUse qui essaie de commiter
        entree_commit = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git commit -m 'test'"},
            "agent_type": "vlp:fiche"
        })

        # Entrée différente (PowerShell au lieu de Bash)
        entree_commit_ps = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {"command": "git commit -m 'test ps'"},
            "agent_type": "vlp:fiche"
        })

        # Premier appel : doit refuser (écrit en JSON)
        code1, out1, err1 = gardien_test(entree_commit)
        verifier("gardien : premier lancement, refuse le git commit",
                 code1 == 0 and "permissionDecision" in out1 and "deny" in out1 and err1 == "",
                 out1 + err1)

        # Deuxième appel avec la même entrée : doit être muet (retourne 0 sans rien écrire)
        code2, out2, err2 = gardien_test(entree_commit)
        verifier("gardien : deuxième lancement de la même entrée, muet",
                 code2 == 0 and out2 == "" and err2 == "",
                 "out=%s err=%s" % (out2, err2))

        # Troisième appel avec une entrée différente : doit refuser (écrit en JSON)
        code3, out3, err3 = gardien_test(entree_commit_ps)
        verifier("gardien : entrée différente, refuse le git commit",
                 code3 == 0 and "permissionDecision" in out3 and "deny" in out3 and err3 == "",
                 out3 + err3)
        # PYT2 : sur une écriture, `filet` et `hook` reçoivent la même entrée — chacun agit une fois
        verifier("premier_lancement : même entrée, deux sous-commandes, chacune une fois",
                 mod.premier_lancement("{}", "cmd_filet") and mod.premier_lancement("{}", "cmd_hook")
                 and not mod.premier_lancement("{}", "cmd_hook"), "")
        # SON : VLP_SANS_TAMPON saute le tampon — la même entrée rejouée agit à chaque fois
        os.environ["VLP_SANS_TAMPON"] = "1"
        try:
            rejeux = [gardien_test(entree_commit)[1] for _ in range(2)]
        finally:
            del os.environ["VLP_SANS_TAMPON"]
        verifier("SON : VLP_SANS_TAMPON, la même entrée rejouée deux fois refuse deux fois",
                 all("deny" in r for r in rejeux), repr(rejeux))
        verifier("SON : sans VLP_SANS_TAMPON, le tampon reprend (muet)",
                 gardien_test(entree_commit)[1] == "", "")
    finally:
        # Restaurer TAMPON_HOOKS à None pour les tests suivants
        shutil.rmtree(mod.TAMPON_HOOKS, ignore_errors=True)
        mod.TAMPON_HOOKS = ancien_tampon


test_premier_lancement()

# BAC1 : `bac` pose le bac d'essai de FIL3, dans un dossier temporaire à lui
def test_bac():
    with tempfile.TemporaryDirectory() as tbac:
        dbac = os.path.join(tbac, "bac")
        code, s = appel(["bac", dbac])
        verifier("bac : sort 0 et annonce le dossier", code == 0 and s.startswith("BAC %s\n" % dbac), s)
        verifier("bac : deux commandes claude -p", s.count("claude -p") == 2, s)
        fbac = os.path.join(dbac, mod.BAC_FICHES)
        code, sv = appel(["valider", fbac])
        verifier("bac : le fichier de fiches se valide", code == 0, sv)
        for ident in ("F1", "F2"):
            code, se_ = appel(["extraire", fbac, ident])
            verifier("bac : extraire %s non vide" % ident, code == 0 and ("## %s [ ]" % ident) in se_, se_)
        ns = [n for n in os.listdir(dbac) if re.match(r"^n\d\d\.txt$", n)]
        verifier("bac : douze fichiers n*.txt", len(ns) == 12, " ".join(sorted(ns)))
        with open(fbac, encoding="utf-8") as f:
            texte_bac = f.read()
        verifier("bac : « un appel par message » deux fois", texte_bac.count("un appel par message") == 2, texte_bac)
        verifier("bac : jamais « par tour »", "par tour" not in texte_bac, texte_bac)
        code, s2 = appel(["bac", dbac])
        verifier("bac : un 2e appel rend une GARDE", code == 1 and s2.startswith("GARDE:"), s2)
        # Dette REG : `clore` refusait le bac, faute de la ligne des lettres (REG3, 2026-09-29)
        for ident in ("F1", "F2"):
            appel(["cocher", fbac, ident])
        code, s3 = appel(["clore", dbac, "--livre", "x", "--resume", "x"])
        verifier("bac : clore passe, les deux fiches jouées", code == 0 and "CLOS F F1..F2" in s3, s3)


test_bac()


# CLI1 : `claude` trouve le CLI de l'app, Packages d'abord ; `bac` et `boucle.py` s'en servent
def test_claude():
    noms = ("VLP_CLAUDE", "PATH", "LOCALAPPDATA", "APPDATA")
    avant = {n: os.environ.get(n) for n in noms}
    with tempfile.TemporaryDirectory() as tcl:
        def faux(*parties):
            p = os.path.join(tcl, *parties, "claude.exe")
            os.makedirs(os.path.dirname(p))
            ecrire(p, "")
            return p
        paquet = ("loc", "Packages", "Claude_x1", "LocalCache", "Roaming", "Claude", "claude-code")
        faux(*paquet, "2.1.9")
        p10 = faux(*paquet, "2.1.10")
        a99 = faux("app", "Claude", "claude-code", "2.1.99")
        try:
            os.environ.pop("VLP_CLAUDE", None)
            os.environ["PATH"] = os.path.join(tcl, "vide")
            os.environ["APPDATA"] = os.path.join(tcl, "app")
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "loc")
            code, s = appel(["claude"])
            verifier("claude : Packages avant APPDATA, 2.1.10 avant 2.1.9", code == 0 and s == "CLAUDE %s\n" % p10, s)
            dbac = os.path.join(tcl, "bac")
            code, s = appel(["bac", dbac])
            verifier("claude : bac imprime la ligne SESSION", code == 0 and s.endswith(
                'SESSION Set-Location "%s"; & "%s"\n' % (os.path.abspath(dbac), p10)), s)
            spec = importlib.util.spec_from_file_location("boucle", os.path.join(ICI, "boucle.py"))
            assert spec and spec.loader
            boucle = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(boucle)
            verifier("claude : boucle.py rend le même chemin", boucle.trouver_claude(None) == p10,
                     str(boucle.trouver_claude(None)))
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "vide")
            code, s = appel(["claude"])
            verifier("claude : sans Packages, APPDATA", code == 0 and s == "CLAUDE %s\n" % a99, s)
            os.environ["VLP_CLAUDE"] = "mon-claude"
            code, s = appel(["claude"])
            verifier("claude : VLP_CLAUDE gagne sur tout", code == 0 and s == "CLAUDE mon-claude\n", s)
            os.environ.pop("VLP_CLAUDE")
            os.environ["APPDATA"] = os.path.join(tcl, "vide")
            code, s = appel(["claude"])
            verifier("claude : rien trouvé → GARDE, sort 1", code == 1 and s.startswith("GARDE:"), s)
            code, s = appel(["bac", os.path.join(tcl, "bac2")])
            verifier("claude : bac sans claude sort 0, GARDE puis SESSION claude", code == 0
                     and 'GARDE: claude.exe introuvable' in s and s.endswith('; & "claude"\n'), s)
        finally:
            for n, v in avant.items():
                if v is None:
                    os.environ.pop(n, None)
                else:
                    os.environ[n] = v


test_claude()


# EVF2 : `kit-essai` copie un kit factice à plafond bas, dans un dossier temporaire à lui
def test_kit_essai():
    with tempfile.TemporaryDirectory() as tke:
        src = os.path.join(tke, "kit")
        for sous_dossier in ("agents", "scripts", ".git", "context AI", os.path.join("evals", "results"),
                             os.path.join("evals", "cas")):
            os.makedirs(os.path.join(src, sous_dossier))
        fiche_src = os.path.join(src, "agents", "fiche.md")
        with open(fiche_src, "w", encoding="utf-8") as f:
            f.write("---\nname: fiche\nmaxTurns: 80\ntools: Read\n---\n\nCorps.\n")
        for rel in ("scripts/x.py", ".git/HEAD", "context AI/08-etat.md", "evals/results/r.json", "evals/cas/case.yaml"):
            with open(os.path.join(src, rel), "w", encoding="utf-8") as f:
                f.write("x\n")
        dke = os.path.join(tke, "copie")
        code, s = appel(["kit-essai", dke, "--max-turns", "6", "--kit", src])
        verifier("kit-essai : sort 0 et annonce 80 → 6", code == 0 and s == "KIT %s · maxTurns 80 → 6\n" % dke, s)
        verifier("kit-essai : maxTurns 6 dans la copie", mod.lire_max_turns(os.path.join(dke, "agents", "fiche.md")) == 6,
                 repr(mod.lire_max_turns(os.path.join(dke, "agents", "fiche.md"))))
        verifier("kit-essai : maxTurns inchangé dans le kit", mod.lire_max_turns(fiche_src) == 80, "")
        presents = [rel for rel in ("scripts/x.py", "evals/cas/case.yaml") if os.path.exists(os.path.join(dke, rel))]
        absents = [rel for rel in (".git", "context AI", "evals/results") if not os.path.exists(os.path.join(dke, rel))]
        verifier("kit-essai : copie le kit, sans .git, context AI ni evals/results",
                 len(presents) == 2 and len(absents) == 3, "%r %r" % (presents, absents))
        code, s2 = appel(["kit-essai", dke, "--max-turns", "6", "--kit", src])
        verifier("kit-essai : un 2e appel rend une GARDE", code == 1 and s2.startswith("GARDE:"), s2)


test_kit_essai()


# BAC2 : `transcription` compte une transcription de sous-agent factice, dans un dossier à lui
def test_transcription():
    u = {"input_tokens": 1}
    lignes = [
        {"type": "user", "message": {"role": "user", "content": "fiche"}},
        # tour 1 sur trois lignes assistant, deux appels : Bash en erreur, puis Read réussi
        {"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": None,
                                          "content": [{"type": "thinking", "thinking": "…"}]}},
        {"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": None,
                                          "content": [{"type": "tool_use", "id": "tA", "name": "Bash", "input": {}}]}},
        {"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": "tool_use",
                                          "content": [{"type": "tool_use", "id": "tB", "name": "Read", "input": {}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tA", "is_error": True, "content": "Exit code 3"}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tB", "content": "fichier 01"}]}},
        {"type": "attachment", "attachment": {"type": "hook_non_blocking_error",
                                              "hookName": "PostToolUseFailure:Bash", "toolUseID": "tA"}},
        {"type": "attachment", "attachment": {"type": "hook_non_blocking_error",
                                              "hookName": "PostToolUse:Read", "toolUseID": "tB"}},
        {"type": "attachment", "attachment": {"type": "hook_additional_context", "hookName": "PostToolUseFailure:Bash",
                                              "toolUseID": "tA", "content": ["Attention : 1 tour restant."]}},
        {"type": "assistant", "message": {"id": "m2", "usage": u, "stop_reason": "end_turn",
                                          "content": [{"type": "text", "text": "RETOUR — fait 1/2\n\nIl reste un appel.\n"}]}},
    ]
    with tempfile.TemporaryDirectory() as ttr:
        jsonl = os.path.join(ttr, "agent.jsonl")
        with open(jsonl, "w", encoding="utf-8") as f:
            for ligne in lignes:
                f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
        code, s = appel(["transcription", jsonl])
        attendu = ("TOURS=2\n"
                   "APPELS=2 — Bash 1, Read 1\n"
                   "AVERTISSEMENTS=1\n"
                   "AVERTIS_PAR_TOUR=1:1\n"
                   "PREMIER_AVERTISSEMENT tour=1 outil=Bash is_error=oui hook=PostToolUseFailure:Bash\n"
                   "TEXTE=Attention : 1 tour restant.\n"
                   "HOOK_ERREURS=2 pour 2 appels\n"
                   "DERNIER mot=RETOUR stop_reason=end_turn\n"
                   "DERNIERE_LIGNE=Il reste un appel.\n")
        verifier("transcription : la sortie du socle, tours par message.id, is_error par toolUseID",
                 code == 0 and s == attendu, s)
        sans = os.path.join(ttr, "sans.jsonl")
        with open(sans, "w", encoding="utf-8") as f:
            f.write(json.dumps(lignes[-1]) + "\n")
        code, s = appel(["transcription", sans])
        verifier("transcription : sans avertissement, « aucun » et pas de TEXTE=",
                 code == 0 and "PREMIER_AVERTISSEMENT aucun\n" in s and "TEXTE=" not in s
                 and "AVERTIS_PAR_TOUR=aucun\n" in s, s)
        # TOU1 : 3 avertissements au tour 2 (une salve de trois Read), 1 au tour 3
        salve = [{"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": "tool_use",
                                                   "content": [{"type": "tool_use", "id": "s0", "name": "Read"}]}}]
        salve += [{"type": "assistant", "message": {"id": "m2", "usage": u, "stop_reason": "tool_use",
                                                    "content": [{"type": "tool_use", "id": i, "name": "Read"}]}}
                  for i in ("s1", "s2", "s3")]
        salve.append({"type": "assistant", "message": {"id": "m3", "usage": u, "stop_reason": "tool_use",
                                                       "content": [{"type": "tool_use", "id": "s4", "name": "Read"}]}})
        salve += [{"type": "attachment", "attachment": {"type": "hook_additional_context", "hookName": "PostToolUse:Read",
                                                        "toolUseID": i, "content": "Attention"}}
                  for i in ("s1", "s2", "s3", "s4")]
        par_tour = os.path.join(ttr, "par-tour.jsonl")
        with open(par_tour, "w", encoding="utf-8") as f:
            for ligne in salve:
                f.write(json.dumps(ligne) + "\n")
        code, s = appel(["transcription", par_tour])
        verifier("transcription : AVERTIS_PAR_TOUR range chaque avertissement au tour de son appel",
                 code == 0 and "AVERTISSEMENTS=4\nAVERTIS_PAR_TOUR=2:3,3:1\n" in s, s)
        code, s = appel(["transcription", os.path.join(ttr, "absent.jsonl")])
        verifier("transcription : illisible rend une GARDE", code == 1 and s.startswith("GARDE:"), s)


test_transcription()

# --- VOI2 : `comparer` dit ce qu'une régénération de page a perdu ou ajouté ---

ANCIENNE_CMP = ("<html><body><table><tbody>\n"
                "<tr><td>ligne A</td></tr>\n"
                "<tr><td>TODO : un truc</td></tr>\n"
                "</tbody></table></body></html>\n")
NEUVE_CMP = ("<html><body><table><tbody>\n"
             "<tr><td>ligne A</td></tr>\n"
             "<tr><td>2026-09-26</td></tr>\n"
             "</tbody></table></body></html>\n")

with tempfile.TemporaryDirectory() as tc:
    anc = os.path.join(tc, "ancienne.html")
    neu = os.path.join(tc, "neuve.html")
    ecrire(anc, ANCIENNE_CMP)
    ecrire(neu, NEUVE_CMP)
    code, s = appel(["comparer", anc, neu])
    verifier("VOI2 : une ligne perdue, une ajoutée, code 0 — une mesure, pas une garde",
             code == 0 and "PERDU: TODO : un truc\n" in s and "AJOUTÉ: 2026-09-26\n" in s
             and s.rstrip().endswith("COMPARER 1 perdus · 1 ajoutés"), s)
    code, s = appel(["comparer", anc, os.path.join(tc, "absente.html")])
    verifier("VOI2 : fichier absent — GARDE, code 1", code == 1 and s.startswith("GARDE:"), s)

# --- Dette IDX : une page enveloppée dans un `div` se compare ligne à ligne ---

def tester_page_enveloppee():
    """Dans une fonction : au niveau du module, pyright jugeait le fichier trop complexe."""
    with tempfile.TemporaryDirectory() as tenv:
        a = os.path.join(tenv, "ancienne.html")
        n = os.path.join(tenv, "neuve.html")
        for chemin, page in ((a, ANCIENNE_CMP), (n, NEUVE_CMP)):
            ecrire(chemin, page.replace("<body>", "<body><div class=\"page\"><h2>Titre</h2>")
                   .replace("</body>", "</div></body>"))
        c, sortie = appel(["comparer", a, n])
        verifier("Dette IDX : page dans un div — mutant : seul le bloc extérieur compte",
                 c == 0 and "PERDU: TODO : un truc\n" in sortie and "AJOUTÉ: 2026-09-26\n" in sortie
                 and sortie.rstrip().endswith("COMPARER 1 perdus · 1 ajoutés"), sortie)


tester_page_enveloppee()


def tester_plage_refaite():
    """Dette HAB : une plage d'en-tête refaite n'est ni perdue ni ajoutée."""
    with tempfile.TemporaryDirectory() as tpl:
        a = os.path.join(tpl, "ancienne.html")
        n = os.path.join(tpl, "neuve.html")
        for chemin, fin in ((a, "P7"), (n, "P8")):
            ecrire(chemin, ANCIENNE_CMP.replace("<body>", "<body><div>kit · fiches P1–%s</div>" % fin))
        c, sortie = appel(["comparer", a, n])
        verifier("Dette HAB : plage refaite — PLAGE, 0 perdu (mutant : sans appariement)",
                 c == 0 and "PERDU:" not in sortie and "AJOUTÉ:" not in sortie
                 and "PLAGE: kit · fiches P1–P7 → kit · fiches P1–P8\n" in sortie
                 and sortie.rstrip().endswith("COMPARER 0 perdus · 0 ajoutés · 1 plages refaites"), sortie)
        ecrire(n, ANCIENNE_CMP.replace("<body>", "<body><div>autre · fiches P1–P8</div>"))
        c, sortie = appel(["comparer", a, n])
        verifier("Dette HAB : texte changé autour de la plage — reste PERDU et AJOUTÉ",
                 "PERDU: kit · fiches P1–P7\n" in sortie and "PLAGE:" not in sortie
                 and sortie.rstrip().endswith("COMPARER 1 perdus · 1 ajoutés"), sortie)
        for chemin, fin in ((a, "P7"), (n, "P8")):
            ecrire(chemin, ANCIENNE_CMP.replace("<body>", "<body><div>Fiches P1–%s — la page</div>" % fin))
        c, sortie = appel(["comparer", a, n])
        verifier("Dette BTN : « Fiches » avec majuscule, plage refaite — PLAGE (mutant : minuscule seule)",
                 "PLAGE: Fiches P1–P7 — la page → Fiches P1–P8 — la page\n" in sortie
                 and "PERDU:" not in sortie, sortie)


tester_plage_refaite()


def tester_bornes():
    """PLG1 : une plage va du plus petit au plus grand numéro, pas de la première à la
    dernière fiche du fichier."""
    verifier("PLG1 : plage par numéro — mutant : bornes rend ids[0], ids[-1]",
             mod.plage(["REV1", "REV2", "REV3", "REV5", "REV8", "REV4"]) == "REV1–REV8",
             mod.plage(["REV1", "REV2", "REV3", "REV5", "REV8", "REV4"]))
    verifier("PLG1 : numéro entier, X10 après X9", mod.plage(["X10", "X9"]) == "X9–X10", mod.plage(["X10", "X9"]))
    verifier("PLG1 : une fiche seule, son id", mod.plage(["U1"]) == "U1", mod.plage(["U1"]))
    with tempfile.TemporaryDirectory() as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n")
        ecrire(os.path.join(tb, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n")
        ecrire(os.path.join(tb, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
        ecrire(os.path.join(tb, "ctx", "30-q.md"), "# Chantier Q — q\n\n## Q2 [ ] — b\n## Q1 [ ] — a\n")
        c, sortie = appel(["ouvrir", tb, "--fiches", "ctx/30-q.md", "--titre", "q"])
        carte = open(os.path.join(tb, "CHANTIER.md"), encoding="utf-8").read()
        verifier("PLG1 : ouvrir sur Q2 puis Q1 écrit Q1..Q2", c == 0 and "OUVERT Q Q1..Q2 " in sortie
                 and "ctx/30-q.md (Q1..Q2)" in carte, sortie + carte)


tester_bornes()


def tester_heredoc():
    """ECH1 : le corps d'un heredoc reçu par cat ou tee est une donnée ; le reste est lu.
    ENQ2 : pareil pour le texte cité d'un echo/printf envoyé dans un fichier."""
    def refuse(commande):
        o = io.StringIO()
        mod.main(["gardien"], o, io.StringIO(json.dumps({
            "agent_id": "a1", "agent_type": "vlp:fiche", "hook_event_name": "PreToolUse",
            "tool_name": "Bash", "tool_input": {"command": commande}})))
        return '"permissionDecision": "deny"' in o.getvalue()
    cas = [("cat > f <<'EOF'\ngit commit\nEOF", False),
           ("tee f <<EOF\ngit add x\nEOF", False),
           ("PYTHONUTF8=1 cat >> \"a b.md\" <<-\"FIN\"\n\tgit reset\n\tFIN\necho ok", False),
           ("py - <<'EOF'\nimport os; os.system('git commit -m x')\nEOF", True),
           ("cat <<'EOF' | bash\ngit commit\nEOF", True),
           ("bash -c \"$(cat <<'EOF'\ngit commit\nEOF\n)\"", True),
           ("cat > f <<'EOF'\nx\nEOF\ngit commit -m y", True),
           ("cat > f <<'EOF'\ngit commit", True),
           ("ssh h 'git reset --hard'", True),
           # ENQ2 : echo/printf tu vers un fichier, refusé si pipé ou si git suit ailleurs
           ('echo \'{"command":"git add ."}\' > f', False),
           ("printf '%s' 'git commit' >> f", False),
           ('echo "git add ." | sh', True),
           ("echo x > f; git add f", True),
           # dette VRB : echo à l'écran muet, "$(…)" lu, pipe ou && lu
           ('echo "git dans APRÈS: $?"; sh x', False), ('echo "git stash"', False),
           ('echo "$(git stash)"', True), ('echo "$(git stash)" > f', True),
           ('echo "a" && git stash', True), ('printf "git push\\n" | sh', True)]
    faux = [(c, attendu) for c, attendu in cas if refuse(c) != attendu]
    verifier("ECH1/ENQ2 : heredoc de cat/tee et echo/printf vers un fichier muets, le reste refusé "
             "(%d cas) — mutant : rien retiré" % len(cas), not faux, repr(faux))
    verifier("ECH1 : lire_contrat ne compte pas le heredoc de cat",
             mod.ecrit_git("cat > f <<'EOF'\ngit commit\nEOF") is False
             and mod.ecrit_git("git -C x commit -m y") is True, "")
    verifier("ENQ2 : lire_contrat ne compte pas le texte cité d'un echo/printf vers un fichier — "
             "mutant : retirer sans_echo fait tomber les deux « faux »",
             mod.ecrit_git('echo \'{"command":"git add ."}\' > f') is False
             and mod.ecrit_git("printf '%s' 'git commit' >> f") is False
             and mod.ecrit_git('echo "git add ." | sh') is True
             and mod.ecrit_git("ssh h 'git reset --hard'") is True, "")
    ecrit = ["git checkout f.py", "git checkout main", "git switch x", "git stash", "git -C x stash",
             "git restore f", "git clean -fd", "git push", "git rebase main", "git merge x",
             "cd x && git stash", "& git.exe push", "PYTHONUTF8=1 git commit -m x", "git --bare add x",
             '"C:/Program Files/Git/cmd/git.exe" push', "x=$(git stash)"]
    lit = ["git diff --cached", "git status", "git --no-pager log -1", "git show HEAD:f",
           "git rev-parse --show-toplevel", "git ls-files", "git -C x log", "grep -c git f",
           "ls .git", "echo git", "cd /c/git && ls", "git", "gitk --all", "py x.py # git stash"]
    faux = ([c for c in ecrit if not mod.ecrit_git(c)] + [c for c in lit if mod.ecrit_git(c)]
            + [c for c in ecrit + lit if refuse(c) != mod.ecrit_git(c)])
    verifier("VRB1 : liste blanche — %d écritures refusées, %d lectures ou non-appels passent, "
             "gardien et contrat d'accord — mutants : `stash` dans LECTURE_GIT, ancrage retiré"
             % (len(ecrit), len(lit)), not faux, repr(faux))


tester_heredoc()


def tester_forme_jauge():
    """OUV1 : une ligne n'est une jauge que si elle en a la forme — émoji en tête, ou le mot
    suivi de —, … ou de la fin de ligne."""
    def renvoye(message):
        o = io.StringIO()
        mod.main(["gardien"], o, io.StringIO(json.dumps({
            "agent_id": "a2", "agent_type": "vlp:relecture", "hook_event_name": "SubagentStop",
            "last_assistant_message": message})))
        return '"decision": "block"' in o.getvalue()
    cas = [("REFUSÉE\n- Imprévu : j'ai dû relancer", False),
           ("ACCEPTÉE\nPas bonne idée de relancer", False),
           ("ACCEPTÉE\n⚠️ **Imprévu** : x", True),
           ("ACCEPTÉE\nÇa tient, mais…", True),
           ("ACCEPTÉE\nPas bon — y", True),
           ("ACCEPTÉE\n**Tout va bien.**", True),
           ("ACCEPTÉE\nGrosse erreur", True)]
    faux = [(m, attendu) for m, attendu in cas if renvoye(m) != attendu]
    verifier("OUV1 : puce « Imprévu : » muette, vraies jauges renvoyées (%d cas) — mutant : forme ignorée"
             % len(cas), not faux, repr(faux))


tester_forme_jauge()


def tester_lance_clore():
    """ECA1 : un appel `clore` est une commande lancée ; la ligne de bilan qui le cite n'en est pas un."""
    cas = [('py scripts/vlp.py clore . --livre x', True),
           ('cd "C:/k" && py "C:/k/scripts/vlp.py" clore .', True),
           ('export A=b; py scripts/vlp.py clore .', True),
           ("cat > f.py <<'EOF'\nprint(1)\nEOF\npy scripts/vlp.py clore .", True),
           ('$o = py "$kit/scripts/vlp.py" clore .', True),
           ('python3 -X utf8 scripts/vlp.py clore .', True),
           ('"C:/Program Files/Python/python.exe" "C:/Mes documents/kit/scripts/vlp.py" clore .', True),
           ('echo "- Coût du chantier : 8 (\\`vlp.py clore\\`)." >> "context AI/08-etat.md"', False),
           ("cat >> etat.md <<'EOF'\n- Coût du chantier : 8 (`vlp.py clore`).\nEOF", False),
           ('git commit -q -m "O3 faite : vlp.py clore écrit le bilan"', False),
           ('py scripts/vlp.py page . --resultat "À la clôture, vlp.py clore écrit l\'estimé"', False),
           ("cat > t.ps1 <<'EOF'\npy scripts/vlp.py clore .\nEOF", False),
           ('grep -n "clore" scripts/vlp.py', False)]
    faux = [(c, attendu) for c, attendu in cas if mod.lance_clore(c) != attendu]
    verifier("ECA1 : lance_clore, %d cas — mutant : l'ancien motif (le texte cité compte)" % len(cas),
             not faux, repr(faux))


tester_lance_clore()


def tester_clos_sans_commit():
    """ECA2 : un clos dont Q2 n'a pas de commit « Q2 : » — son travail est dans « Journal : … Q2 ».
    Tours à 200 (Q1), 400 et 500 (Q2), l'appel clore à 700, puis 800, 1000, 1100 : la session a
    continué après la clôture (900). Q2 s'arrête au journal (600), hors fiches à l'appel clore."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — ECA2 n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        dep, sq = os.path.join(t, "depot"), os.path.join(t, "s.jsonl")
        transcript(sq, 7, [T0 + d for d in (200, 400, 500, 700, 800, 1000, 1100)])
        lignes_ = [json.loads(l) for l in lire(sq).splitlines()]
        lignes_[3]["message"]["content"] = [{"type": "tool_use", "id": "t3", "name": "Bash",
                                             "input": {"command": "py scripts/vlp.py clore . --livre x"}}]
        ecrire(sq, "".join(json.dumps(l) + "\n" for l in lignes_))
        ecrire(os.path.join(dep, "q.md"), (QFICHES % (sq, sq)).replace("# Chantier Q\n",
                                                                         "# Chantier Q\n\n**CLOS** le 2026-05-06.\n", 1))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=dep, env=env, check=True, capture_output=True)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"),
                         (600, "Journal : la mesure de Q2"), (900, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        code, s = appel(["cout", os.path.join(dep, "q.md")])
        lignes_ = s.splitlines()
        q2 = [l for l in lignes_ if l.startswith("Q2 · ")]
        total = [l for l in lignes_ if l.startswith("TOTAL ")]
        verifier("ECA2 : clos, Q2 sans commit — Q2 2 tours, TOTAL 400 000 · 4 tours — mutant : clos ignoré"
                 " (TOTAL 700 000 · 7 tours)", code == 0 and len(q2) == 1 and mod.triplet(q2[0])[:2] == (200000, 2)
                 and len(total) == 1 and mod.triplet(total[0])[:2] == (400000, 4), s)


tester_clos_sans_commit()

# --- VOI3 : `lettres_prises` tolère une lettre entre backticks (MapDecorator) -

LIGNE_MAPDECORATOR = "Lettres de fiche déjà prises : `T`, `U`, `R`, `M`. Un nouveau chantier en choisit"
verifier("VOI3 : lettres entre backticks (ligne réelle de MapDecorator)",
         mod.lettres_prises([LIGNE_MAPDECORATOR]) == ["T", "U", "R", "M"],
         repr(mod.lettres_prises([LIGNE_MAPDECORATOR])))

# --- ABR1 : le .md d'une page, amorcé depuis la page sans la toucher ----------

PAGE_ABR = """<title>kit — Abri</title>
    <h1>Abri &amp; journal</h1>
    <p>Notes &lt;à l'abri&gt;</p>
    <ul class="fiches">
      <li class="fiche" data-etat="faite">
        <span class="id">ABR1</span><span class="titre">Un</span>
        <span class="etat">faite</span>
        <span class="note">test 3/3 &amp; pyright 0</span>
      </li>
      <li class="fiche">
        <span class="id">ABR2</span><span class="titre">Deux</span>
        <span class="etat">à faire</span>
        <span class="note">dépend de ABR1</span>
      </li>
    </ul>
    <ul class="journal">
      <li><time datetime="2026-09-25">2026-09-25</time><span>Pierre &amp; Paul</span></li>
      <li><time>2026-09-26</time><span>E3 : <span class="mono">allowed-tools</span> muet</span></li>
      <li><time datetime="2026-09-26">2026-09-26</time><span>sur
        deux lignes</span></li>
    </ul>
  <section>
    <h2>Chantier clos le 2026-09-26</h2>
    <div class="bilan">
      <p>Livré : un <code>.md</code> &amp; une page</p>
    </div>
  </section>
"""


def tester_abri():
    with tempfile.TemporaryDirectory() as tab:
        page = os.path.join(tab, "artefacts", "76-abri.html")
        ecrire(page, PAGE_ABR)
        md = os.path.join(tab, "artefacts", "76-abri.md")
        verifier("ABR1 : chemin du .md à côté de la page", mod.chemin_abri(page) == md, mod.chemin_abri(page))
        code, s = appel(["abri", page])
        verifier("ABR1 : abri — 2 notes, 3 lignes de journal, un bilan",
                 code == 0 and s == "ABRI %s · résultat 1 · notes 2 · journal 3 · bilan 1\n" % md, s)
        parts = mod.lire_abri(md)
        verifier("ABR1 : .md relu, texte désechappé — mutant : ne pas désechapper",
                 parts["titre"] == "Abri & journal" and parts["resultat"] == "Notes <à l'abri>"
                 and parts["notes"] == {"ABR1": "test 3/3 & pyright 0", "ABR2": "dépend de ABR1"}
                 and parts["journal"] == [("2026-09-25", "Pierre & Paul"), ("2026-09-26", "E3 : allowed-tools muet"),
                                          ("2026-09-26", "sur deux lignes")]
                 and parts["bilan"] == ["Livré : un .md & une page"], repr(parts))
        with open(page, "rb") as f:
            verifier("ABR1 : la page identique octet pour octet", f.read() == PAGE_ABR.encode("utf-8"), "page modifiée")
        mod.ecrire_abri(md, parts)
        verifier("ABR1 : écrire puis relire redonne les mêmes parts", mod.lire_abri(md) == parts, lire(md))
        code, s = appel(["abri", page])
        verifier("ABR1 : second abri — DÉJÀ, .md non réécrit", code == 0 and s == "DÉJÀ %s\n" % md, s)
        code, s = appel(["abri", os.path.join(tab, "absente.html")])
        verifier("ABR1 : page absente — GARDE, code 1", code == 1 and s.startswith("GARDE:"), s)


tester_abri()

# --- ABR2 : `page` écrit d'abord dans le .md, puis le recopie en entier -------

FICHES_ABR2 = """# Chantier ABR

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
<!-- /FICHE -->
"""


def tester_abr2():
    with tempfile.TemporaryDirectory() as tab:
        fiches = os.path.join(tab, "abr.md")
        page = os.path.join(tab, "artefacts", "abr.html")
        md = mod.chemin_abri(page)
        ecrire(fiches, FICHES_ABR2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        verifier("ABR2 : --creer amorce le .md", code == 0 and os.path.exists(md), s)
        code, s = appel(["page", fiches, page, "--note", "P1", "x", "--journal", "y", "--date", "2026-09-26"])
        verifier("ABR2 : page — note et journal écrits d'abord dans le .md", code == 0
                 and mod.lire_abri(md)["notes"] == {"P1": "x"}
                 and mod.lire_abri(md)["journal"] == [("2026-09-26", "y")], s + lire(md))
        html_avant = lire(page)
        os.remove(page)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        verifier("ABR2 : la page effacée reprend x et y depuis le .md — mutant : lire l'ancienne page",
                 code == 0 and '<span class="note">x</span>' in html
                 and '<time datetime="2026-09-26">2026-09-26</time><span>y</span>' in html
                 and "<p>R0</p>" in html, s + html)
        verifier("ABR2 : le .md n'a pas bougé au second --creer — mutant : --creer réécrit le .md",
                 mod.lire_abri(md)["notes"] == {"P1": "x"} and mod.lire_abri(md)["journal"] == [("2026-09-26", "y")],
                 lire(md))

        # Une page ancienne, sans .md : elle garde ses notes (pas de perte à l'amorçage).
        ancienne = os.path.join(tab, "artefacts", "anc.html")
        ecrire(ancienne, html_avant)
        fiches_anc = os.path.join(tab, "anc.md")
        ecrire(fiches_anc, FICHES_ABR2)
        verifier("ABR2 : pas de .md avant ce test", not os.path.exists(mod.chemin_abri(ancienne)), "")
        code, s = appel(["page", fiches_anc, ancienne, "--date", "2026-09-27"])
        html = lire(ancienne)
        verifier("ABR2 : page ancienne sans .md — garde ses notes", code == 0
                 and '<span class="note">x</span>' in html
                 and '<span>y</span>' in html, s + html)
        verifier("ABR2 : l'amorçage a posé le .md de l'ancienne page",
                 os.path.exists(mod.chemin_abri(ancienne)) and mod.lire_abri(mod.chemin_abri(ancienne))["notes"] == {"P1": "x"},
                 lire(mod.chemin_abri(ancienne)))
        # Le .md prime désormais sur l'ancienne page : une note différente dans le .md l'emporte
        # — mutant : lire la note dans l'ancienne page (`anciens`) au lieu du .md.
        code, s = appel(["page", fiches_anc, ancienne, "--note", "P1", "z", "--date", "2026-09-27"])
        html = lire(ancienne)
        verifier("ABR2 : le .md l'emporte sur l'ancienne note de la page — mutant : lire l'ancienne page",
                 code == 0 and '<span class="note">z</span>' in html and '<span class="note">x</span>' not in html,
                 s + html)
        # Une note retirée du .md disparaît de la page — mutant : retomber sur l'ancienne page (`anciens`),
        # qui la garde encore. C'est le seul cas où le mutant se distingue d'une note passée par --note.
        md_anc = mod.chemin_abri(ancienne)
        parts_anc = mod.lire_abri(md_anc)
        del parts_anc["notes"]["P1"]
        mod.ecrire_abri(md_anc, parts_anc)
        code, s = appel(["page", fiches_anc, ancienne, "--date", "2026-09-28"])
        html = lire(ancienne)
        verifier("ABR2 : note retirée du .md — absente de la page — mutant : retombe sur l'ancienne page",
                 code == 0 and '<span class="note">' not in html.split("<ul class=\"journal\">")[0].split('id">P1')[1].split("</li>")[0],
                 s + html)


tester_abr2()


# --- PLI1 (fiche PLI2) : `page` et `feuille` recopient `templates/vlp.css` ----

FICHES_PLI2 = """# Chantier PLI2

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — Un
**Critère de fin**
x
<!-- /FICHE -->
"""


def tester_vlp_css_recopie():
    source = io.open(os.path.join(ICI, "..", "templates", "vlp.css"), "rb").read()

    # `page --creer`, puis `page` sans --creer (régénération) : les deux recopient.
    with tempfile.TemporaryDirectory() as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        css = os.path.join(tab, "artefacts", "vlp.css")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        verifier("PLI2 : page --creer recopie vlp.css, le dit en sortie",
                 code == 0 and os.path.isfile(css) and io.open(css, "rb").read() == source
                 and "CSS %s\n" % css in s, s)
        with open(css, "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        verifier("PLI2 : page (régénération, sans --creer) remet vlp.css à l'identique"
                 " — mutant : ne copier qu'à --creer",
                 code == 0 and io.open(css, "rb").read() == source, s)

    # `feuille`, sur un projet équipé, recopie aussi.
    with tempfile.TemporaryDirectory() as tab:
        proj = os.path.join(tab, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : aucun\n"
               "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"),
               "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        css = os.path.join(proj, "ctx", "artefacts", "vlp.css")
        code, s = appel(["feuille", proj])
        verifier("PLI2 : feuille recopie vlp.css, le dit en sortie",
                 code == 0 and os.path.isfile(css) and io.open(css, "rb").read() == source
                 and "CSS %s\n" % css in s, s)

    # Les deux gabarits ne portent plus de <style> inline (chantier PLI, fiche PLI2).
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = io.open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
        verifier("PLI2 : %s sans <style> — %d" % (nom, gabarit.count("<style")),
                 gabarit.count("<style") == 0 and 'href="vlp.css"' in gabarit, gabarit[:400])


tester_vlp_css_recopie()


# --- PLI3 : une page à <style> inline est migrée vers <link href="vlp.css"> ---

def avec_style_inline(html):
    """Une page déjà régénérée (donc liée à vlp.css), avec son <style> d'avant PLI3
    remis en place — comme une page publiée avant ce chantier, jamais régénérée depuis."""
    css = io.open(os.path.join(ICI, "..", "templates", "vlp.css"), encoding="utf-8").read()
    return html.replace('<link rel="stylesheet" href="vlp.css">', "<style>\n%s</style>" % css, 1)


def tester_style_migre():
    with tempfile.TemporaryDirectory() as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        ancienne = os.path.join(tab, "avant.html")
        ecrire(fiches, FICHES_PLI2)
        appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        # Une page déjà correcte, mais encore au CSS inline (avant PLI3) — le seul écart voulu.
        ecrire(page, avec_style_inline(lire(page)))
        ecrire(ancienne, lire(page))
        code, s = appel(["page", fiches, page])
        html = lire(page)
        verifier("PLI3 : régénérée, la page n'a plus de <style>, un seul <link> vers vlp.css"
                 " — mutant : ajouter le <link> sans retirer le <style>",
                 code == 0 and "<style>" not in html and html.count('href="vlp.css"') == 1, html[:400])
        code, s = appel(["comparer", ancienne, page])
        verifier("PLI3 : comparer ne dit aucune ligne de texte perdue",
                 code == 0 and "PERDU:" not in s and s.rstrip().startswith("COMPARER 0 perdus"), s)
        code, s = appel(["page", fiches, page])
        verifier("PLI3 : régénérée deux fois, toujours un seul <link>",
                 code == 0 and lire(page).count('href="vlp.css"') == 1, lire(page)[:400])


tester_style_migre()


# --- PLI5 : chaque fiche repliée, ouverte si en cours ; l'ancienne forme se lit encore ---

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


def tester_fiches_repliees():
    with tempfile.TemporaryDirectory() as tfr:
        fiches = os.path.join(tfr, "q.md")
        page = os.path.join(tfr, "artefacts", "q.html")
        ancienne = os.path.join(tfr, "avant.html")
        ecrire(fiches, FICHES_PLI5)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0",
                         "--note", "Q1", "n1", "--note", "Q2", "n2", "--note", "Q3", "n3"])
        html = lire(page)
        ul = re.search(r'<ul class="fiches">.*?</ul>', html, re.S)
        zone = ul.group(0) if ul else ""
        verifier("PLI5 : 3 fiches, 3 blocs repliables, un seul ouvert — celui en cours"
                 " — mutant : tout ouvrir",
                 code == 0 and zone.count("<details") == 3 and zone.count("<details open>") == 1
                 and '<details open><summary><span class="titre">En cours</span><span class="etat">En cours</span></summary>'
                 in zone, s + zone)
        ecrire(ancienne, forme_ancienne(html))
        verifier("PLI5 : la forme ancienne du test n'a plus de bloc repliable",
                 "<details" not in lire(ancienne) and lire(ancienne).count('<li class="fiche"') == 3, lire(ancienne))
        code, s = appel(["comparer", ancienne, page])
        verifier("PLI5 : comparer contre l'ancienne forme ne dit aucune ligne de texte perdue",
                 code == 0 and "PERDU:" not in s and s.rstrip().startswith("COMPARER 0 perdus"), s)
        vues_neuves, vues_anciennes = mod.lis_page(html), mod.lis_page(lire(ancienne))
        verifier("PLI5 : une page à l'ancienne forme se lit encore, mêmes fiches"
                 " — mutant : ne lire que la nouvelle forme",
                 len(vues_neuves) == 3 and vues_anciennes == vues_neuves
                 and vues_anciennes["Q2"][0] == "encours", "%r\n%r" % (vues_neuves, vues_anciennes))


tester_fiches_repliees()


# --- Gabarit en colonnes (2026-09-27) : dépendances à gauche, coût ou « visuel » à droite ---

def tester_carte_en_colonnes():
    fiches_md = ("# Chantier Q\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                 "<!-- FICHE:Q1 -->\n## Q1 [x] — Faite\n**Dépend de** : rien.\n**Critère de fin** (visuel)\nx\n"
                 "<!-- /FICHE -->\n\n"
                 "<!-- FICHE:Q2 -->\n## Q2 [ ] — Visuelle\n**Dépend de** : `Q1`.\n**Critère de fin** (visuel)\nx\n"
                 "<!-- /FICHE -->\n\n"
                 "<!-- FICHE:Q3 -->\n## Q3 [ ] — Trois dépendances\n**Dépend de** : `Q1`,\n`Q2` et `PLI3`.\n"
                 "**Critère de fin**\nx\n<!-- /FICHE -->\n")
    c1 = "≈1,1k (1 111) · 1 tours · 0,01 $"
    with tempfile.TemporaryDirectory() as tcc:
        fiches = os.path.join(tcc, "q.md")
        page = os.path.join(tcc, "artefacts", "q.html")
        ecrire(fiches, fiches_md)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0",
                         "--note", "Q2", "n2"])
        html = lire(page)
        li = {m.group(1): m.group(0)
              for m in re.finditer(r'<li class="fiche".*?<span class="id">(\w+)</span>.*?</li>', html, re.S)}
        verifier("colonnes : à gauche l'identifiant seul, l'état en une phrase sous le titre",
                 code == 0 and '<span class="gauche"><span class="id">Q2</span></span>' in li.get("Q2", "")
                 and '<summary><span class="titre">Visuelle</span><span class="etat">En cours</span></summary>'
                 in li.get("Q2", ""), s + html)
        verifier("colonnes : une dépendance faite ne s'affiche plus, sur aucune fiche (Q2 dépend de Q1, faite)",
                 "Q1" in li and all('class="dep' not in c for c in li.values()), "%r" % li)
        verifier("colonnes : une dépendance sur la ligne suivante se lit — Q3 « Après Q2 »",
                 '<span class="etat">Après Q2</span>' in li.get("Q3", "") and " data-attend" in li.get("Q3", ""),
                 li.get("Q3", ""))
        verifier("colonnes : « visuel » à droite d'une fiche à regarder et non faite, seulement"
                 " — mutant : la fiche faite l'a aussi",
                 mod.VISUEL in li.get("Q2", "") and mod.VISUEL not in li.get("Q1", "")
                 and mod.VISUEL not in li.get("Q3", ""), "%r" % li)
        verifier("colonnes : le titre et l'état dans le summary, la note dans le corps, « visuel » après",
                 ('<details open><summary><span class="titre">Visuelle</span><span class="etat">En cours</span></summary>\n'
                  '        <span class="note">n2</span></details>\n        ' + mod.VISUEL + '</li>') in li.get("Q2", ""),
                 li.get("Q2", ""))
        # Le coût d'une page d'avant passe à droite : `--forme` le relit, puis le pose après le corps.
        q1 = '<span class="titre">Faite</span><span class="etat">Faite</span></summary></details>'
        ecrire(page, html.replace(q1 + '</li>', q1 + '\n        <span class="cout mono">%s</span></li>' % c1))
        code, s = appel(["page", fiches, page, "--forme"])
        apres = lire(page)
        verifier("colonnes : --forme garde le coût, à droite, et le relit — mutant : coût gardé dans le corps",
                 code == 0 and (q1 + '\n        <span class="cout mono">%s</span></li>' % c1) in apres
                 and mod.lis_page(apres)["Q1"][2] == c1, s + apres)
    pli5 = ('      <li class="fiche" data-etat="encours"><details open>\n'
            '        <summary><span class="id">Q2</span><span class="titre">Visuelle</span>\n'
            '        <span class="etat">en cours</span></summary>\n'
            '        <span class="note">n2</span>\n'
            '        <span class="cout mono">%s</span>\n'
            '      </details></li>\n' % c1)
    verifier("colonnes : une fiche de la forme PLI5, en ligne partout, se lit encore",
             mod.lis_page(pli5) == {"Q2": ("encours", "n2", c1)}, "%r" % mod.lis_page(pli5))
    neuve = ('<li class="carte-todo"><span class="gauche"><span class="rang mono">7</span></span><details><summary>'
             '<span class="titre">a</span></summary></details></li>\n<li class="carte-todo"><span class="gauche">'
             '<span class="rang mono">8</span>' + mod.BADGE_COURS + '</span><details><summary><span class="titre">b'
             '</span></summary></details></li>\n')
    ancienne = ('<li class="carte-todo"><details><summary><span class="rang mono">5</span><span class="titre">a'
                + mod.BADGE_COURS + '</span><span class="meta mono">1 fiche · dépend de : —</span></summary></details></li>\n')
    verifier("colonnes : le badge « en cours » se lit à gauche d'une carte, et dans le titre d'une carte d'avant"
             " — mutant : exiger le titre juste après le rang",
             mod.rang_en_cours(neuve, "cartes") == "8" and mod.rang_en_cours(ancienne, "cartes") == "5",
             "%r %r" % (mod.rang_en_cours(neuve, "cartes"), mod.rang_en_cours(ancienne, "cartes")))
    verifier("colonnes : dépendances d'un chantier possible — code, rang, rien, et plus de deux codes",
             mod.depend_todo("`PLI`") == '<span class="dep mono">← PLI</span>'
             and mod.depend_todo("3") == '<span class="dep mono">← 3</span>' and mod.depend_todo("—") == ""
             and mod.depend_todo("`A`, `B`, `C`") == '<span class="dep mono" title="A, B, C">← 3 chantiers</span>',
             "%r" % [mod.depend_todo(d) for d in ("`PLI`", "3", "—", "`A`, `B`, `C`")])


tester_carte_en_colonnes()


# Fiches prêtes, et à lancer en même temps (commentaires de la page BTN, choix de l'utilisateur) : l'état
# en une phrase sous le titre — « À lancer », ou « Après A, B » et `data-attend` ; les prêtes sans fichier
# commun ajoutent « en même temps que … ».
def tester_pretes_et_paralleles():
    def fiche(ident, case, dep, fichiers):
        return ("<!-- FICHE:%s -->\n## %s [%s] — Fiche %s\n**Dépend de** : %s\n%s**Critère de fin**\nx\n"
                "<!-- /FICHE -->\n\n" % (ident, ident, case, ident, dep, "**Fichiers** : %s\n" % fichiers if fichiers else ""))
    def fichier_md(faites):
        return ("# Chantier R\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                + fiche("R1", "x", "rien.", "`a.py`")
                + fiche("R2", "x" if "R2" in faites else " ", "`R1`.", "`scripts/a.py`, `b.css`")
                + fiche("R3", "x" if "R3" in faites else " ", "`R1`.", "`c.js` (nouveau) — et rien d'autre.")
                + fiche("R4", "x" if "R4" in faites else " ", "rien.", "`templates/b.css` (`.x > y` `:12`), `compte_todo`")
                + fiche("R5", " ", "`R2`, `R3`,\n`R4` et `PLI9`.", "`d.md`")
                + fiche("R6", " ", "`R1`.", "")
                + fiche("R7", "x" if "R7" in faites else " ", "`R3`.", "`e.md`"))
    def cartes(html):
        return {m.group(1): m.group(0)
                for m in re.finditer(r'<li class="fiche".*?<span class="id">(\w+)</span>.*?</li>', html, re.S)}
    def tete(attributs, ident):
        return '<li class="fiche"%s><span class="gauche"><span class="id">%s</span></span>' % (attributs, ident)
    def dit(li, ident, texte):
        return ('<span class="etat">%s</span>' % texte) in li.get(ident, "")
    def libelle(html, ident, texte):
        return re.sub(r'(<span class="id">%s</span>.*?<span class="etat">)[^<]*' % ident,
                      lambda m: m.group(1) + texte, html, count=1, flags=re.S)
    with tempfile.TemporaryDirectory() as tpp:
        fiches = os.path.join(tpp, "r.md")
        page = os.path.join(tpp, "artefacts", "r.html")
        ecrire(fiches, fichier_md(()))
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        li = cartes(html)
        verifier("prêtes : une fiche qui attend dit « Après » et tous les noms pas faits de ce fichier"
                 " — mutant : attente ignorée",
                 code == 0 and li.get("R5", "").startswith(tete(" data-attend", "R5")) and dit(li, "R5", "Après R2, R3, R4")
                 and li.get("R7", "").startswith(tete(" data-attend", "R7")) and dit(li, "R7", "Après R3"), s + html)
        verifier("prêtes : une fiche qui se lance dit « À lancer », sans ses dépendances faites ; en cours, son état",
                 dit(li, "R4", "À lancer") and dit(li, "R6", "À lancer") and all('class="dep' not in c for c in li.values())
                 and li.get("R2", "").startswith(tete(' data-etat="encours"', "R2"))
                 and dit(li, "R2", "En cours · R3 peut partir en même temps"), "%r" % li)
        verifier("en même temps : sur les prêtes sans fichier commun (même nommé autrement), pas sur celle sans"
                 " ligne Fichiers — mutants : fichiers communs ignorés, prête sans Fichiers comptée",
                 dit(li, "R3", "À lancer · en même temps que R2")
                 and all("même temps" not in li.get(i, "même temps") for i in ("R1", "R4", "R5", "R6", "R7")), "%r" % li)
        verifier("prêtes : la page se relit — lis_page lit l'état malgré data-attend",
                 mod.lis_page(html).get("R2", ("?",))[0] == "encours" and mod.lis_page(html).get("R5", ("?",))[0] is None,
                 "%r" % mod.lis_page(html))
        code, s = appel(["page", fiches, page])
        code2, s2 = appel(["page", fiches, page, "--forme"])
        verifier("prêtes : régénérer, puis repeindre, ne change rien",
                 code == 0 and code2 == 0 and lire(page) == html, s + s2 + lire(page))
        # Une page d'avant : « à faire » (avant BTN), « à lancer » et « après » en minuscules (v12 de la page
        # BTN), une phrase périmée, et un libellé écrit à la main.
        vieille = html
        for ident, texte in (("R6", "abandonnée"), ("R4", "à lancer"), ("R3", "À lancer · en même temps que R9"),
                             ("R5", "à faire"), ("R7", "après R3")):
            vieille = libelle(vieille, ident, texte)
        ecrire(page, vieille)
        code, s = appel(["page", fiches, page, "--forme"])
        li = cartes(lire(page))
        verifier("prêtes : --forme recalcule les libellés qu'il a écrits, dans toutes leurs formes, garde « abandonnée »"
                 " — mutants : tout libellé gardé, casse, phrase entière comparée",
                 code == 0 and dit(li, "R3", "À lancer · en même temps que R2") and dit(li, "R4", "À lancer")
                 and dit(li, "R5", "Après R2, R3, R4") and dit(li, "R7", "Après R3") and dit(li, "R6", "abandonnée"),
                 s + lire(page))
        ecrire(fiches, fichier_md(("R2", "R3")))
        appel(["page", fiches, page])
        li = cartes(lire(page))
        verifier("en même temps : suit les cases — R2 et R3 faites, R4 en cours, R4 et R7 ensemble, R5 après R4",
                 dit(li, "R4", "En cours · R7 peut partir en même temps") and dit(li, "R7", "À lancer · en même temps que R4")
                 and dit(li, "R5", "Après R4"), "%r" % li)
        ecrire(fiches, fichier_md(("R2", "R3", "R4", "R7")))
        appel(["page", fiches, page])
        verifier("en même temps : une seule prête avec des fichiers — aucun « en même temps »",
                 all("même temps" not in c for c in cartes(lire(page)).values()), lire(page))
        # En cours, mais une dépendance plus bas n'est pas faite : l'état reste, puis « attend ».
        ecrire(fiches, "# Chantier S\n\n" + fiche("S1", " ", "`S2`, `S3`, `S4`.", "`f.md`")
               + "".join(fiche(i, " ", "rien.", "`g.md`") for i in ("S2", "S3", "S4")))
        code, s = appel(["page", fiches, os.path.join(tpp, "artefacts", "s.html"), "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        li = cartes(lire(os.path.join(tpp, "artefacts", "s.html")))
        verifier("prêtes : en cours et en attente — « En cours · attend » et tous les noms, data-attend",
                 code == 0 and li.get("S1", "").startswith(tete(' data-etat="encours" data-attend', "S1"))
                 and dit(li, "S1", "En cours · attend S2, S3, S4"), s + "%r" % li)


tester_pretes_et_paralleles()


# --- PLI6 : le journal replié au-delà de 3 entrées ; le bilan sous l'en-tête à la clôture ---

def tester_journal_replie():
    for n, visibles, repliees in ((7, 3, 4), (2, 2, 0)):
        with tempfile.TemporaryDirectory() as tjr:
            fiches = os.path.join(tjr, "q.md")
            page = os.path.join(tjr, "artefacts", "q.html")
            ecrire(fiches, FICHES_PLI5)
            argv = ["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"]
            for k in range(1, n + 1):
                argv += ["--journal", "j%d" % k]
            code, s = appel(argv)
            html = lire(page)
            ancien = re.search(r'<details class="journal-ancien">.*?</details>', html, re.S)
            premier = re.search(r'<ul class="journal">(.*?)</ul>', html, re.S)
            vus = premier.group(1).count("<li>") if premier else -1
            caches = ancien.group(0).count("<li>") if ancien else 0
            textes = [t for _, t in mod.abri_de_page(html)["journal"]]
            verifier("PLI6 : %d entrées → %d visibles, %d repliées, abri les relit dans l'ordre"
                     " — mutant : garder tout visible" % (n, visibles, repliees),
                     code == 0 and vus == visibles and caches == repliees and bool(ancien) == bool(repliees)
                     and textes == ["j%d" % k for k in range(1, n + 1)]
                     and (not ancien or "%d entrées plus anciennes" % repliees in ancien.group(0)),
                     "%s\nvus=%d caches=%d %r\n%s" % (s, vus, caches, textes, html[html.find("Journal"):][:900]))


tester_journal_replie()


def tester_bilan_en_haut():
    gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read()
    # une page d'avant PLI6 : le bilan en bas, juste avant le pied de page
    i = gabarit.index("  <!-- ZONE:bilan")
    fin = gabarit.index("  </section>\n", i) + len("  </section>\n\n")
    bloc = gabarit[i:fin]
    ancienne = (gabarit[:i] + gabarit[fin:]).replace("  <footer>", bloc + "  <footer>", 1)
    with tempfile.TemporaryDirectory() as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : ctx/50-u.md (U1..U1)\n- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(tb, "ctx", "50-u.md"), "# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n")
        page = os.path.join(tb, "ctx", "artefacts", "50-u.html")
        ecrire(page, ancienne)
        verifier("PLI6 : la page de départ a son bilan en bas",
                 ancienne.index("ZONE:bilan") > ancienne.index("ZONE:fiches"), "")
        code, s = appel(["clore", tb, "--livre", "fini", "--date", "2026-09-27"])
        html = lire(page)
        verifier("PLI6 : après clore, ZONE:bilan précède ZONE:fiches, visible, une seule fois"
                 " — mutant : laisser le bilan en bas",
                 code == 0 and html.count("ZONE:bilan") == 1
                 and html.index("ZONE:bilan") < html.index("ZONE:fiches")
                 and "<section>\n    <h2>Chantier clos le 2026-09-27</h2>" in html, s + html[:1500])
        # un clos d'avant PLI6 : bilan visible, mais en bas — `page` le remonte aussi (dette PLI)
        j = html.index("  <!-- ZONE:bilan")
        fin_b = html.index("  </section>\n", j) + len("  </section>\n")
        clos_bas = (html[:j] + html[fin_b:]).replace("  <footer>", html[j:fin_b] + "\n  <footer>", 1)
        ecrire(page, clos_bas)
        code, s = appel(["page", os.path.join(tb, "ctx", "50-u.md"), page])
        html = lire(page)
        verifier("dette PLI : page remonte le bilan d'un clos resté en bas, une seule fois"
                 " — mutant : ne le remonter qu'à clore",
                 code == 0 and clos_bas.index("ZONE:bilan") > clos_bas.index("ZONE:fiches")
                 and html.count("ZONE:bilan") == 1 and html.index("ZONE:bilan") < html.index("ZONE:fiches"),
                 s + html[:1500])
    with tempfile.TemporaryDirectory() as tbo:
        # témoin : une page ouverte à l'ancienne forme (bilan caché, en bas) n'est pas touchée
        ouverte = os.path.join(tbo, "artefacts", "q.html")
        fiches_o = os.path.join(tbo, "q.md")
        ecrire(fiches_o, FICHES_PLI5)
        ecrire(ouverte, ancienne)
        code, s = appel(["page", fiches_o, ouverte])
        html = lire(ouverte)
        verifier("dette PLI : un chantier ouvert garde son bilan caché là où il est"
                 " — mutant : toujours remonter le bilan",
                 code == 0 and html.index("ZONE:bilan") > html.index("ZONE:fiches")
                 and "<section hidden>\n    <h2>Chantier clos le" in html, s + html[-1500:])


tester_bilan_en_haut()


def tester_vigile():
    """vigile (chantier VID1) : une page cassée ne part pas — commentaire ouvert, aucun style, aucun bloc."""
    def hook(d):
        o = io.StringIO()
        code = mod.main(["vigile"], o, io.StringIO(d if isinstance(d, str) else json.dumps(d)))
        return code, o.getvalue()

    with tempfile.TemporaryDirectory() as tvg:
        saine = os.path.join(tvg, "saine.html")
        ecrire(saine, "<!-- tête fermée -->\n<html><head><style>p{}</style></head>"
                      "<body><h1>Titre</h1><p>Un texte.</p></body></html>\n")
        cairn = os.path.join(tvg, "cairn.html")
        ecrire(cairn, "<!-- Gabarit : remplis les <…>\n<html><head><style>p{}</style></head>"
                      "<body><h1>Titre</h1><p>Un texte.</p></body></html>\n")
        sans_style = os.path.join(tvg, "sans-style.html")
        ecrire(sans_style, "<html><body><p>Un texte.</p></body></html>\n")
        sans_bloc = os.path.join(tvg, "sans-bloc.html")
        ecrire(sans_bloc, "<html><head><style>p{}</style></head><body><script>x()</script></body></html>\n")
        lien = os.path.join(tvg, "lien.html")
        ecrire(lien, '<html><head><link rel="stylesheet" href="vlp.css"></head><body><p>Un texte.</p></body></html>\n')

        code, s = appel(["vigile", saine])
        verifier("vigile : page saine, PAGE SAINE 2 blocs", (code, s) == (0, "PAGE SAINE 2 blocs\n"), s)
        code, s = appel(["vigile", cairn])
        verifier("vigile : page Cairn, commentaire ouvert ligne 1 — mutant : ne plus le chercher",
                 code == 1 and "GARDE: %s — commentaire ouvert ligne 1" % cairn in s, s)
        verifier("vigile : page Cairn, style et texte cachés dans le commentaire comptent pour rien",
                 "aucun style" in s and "aucun bloc de texte visible" in s and s.count("GARDE:") == 3, s)
        code, s = appel(["vigile", sans_style])
        verifier("vigile : page sans style, GARDE — mutant : l'accepter",
                 code == 1 and s == "GARDE: %s — aucun style (ni balise style, ni link rel=\"stylesheet\")\n"
                 % sans_style, s)
        code, s = appel(["vigile", sans_bloc])
        verifier("vigile : page sans bloc, GARDE — mutant : accepter zéro bloc",
                 code == 1 and s == "GARDE: %s — aucun bloc de texte visible\n" % sans_bloc, s)
        code, s = appel(["vigile", lien])
        verifier("vigile : page stylée par un seul link, saine", (code, s) == (0, "PAGE SAINE 1 blocs\n"), s)
        code, s = appel(["vigile", os.path.join(tvg, "absente.html")])
        verifier("vigile : fichier absent, GARDE introuvable", code == 1 and s.startswith("GARDE: introuvable"), s)

        pub = {"hook_event_name": "PreToolUse", "tool_name": "Artifact"}
        code, s = hook(dict(pub, tool_input={"file_path": cairn}))
        verifier("vigile : hook, page Cairn refusée, raison nomme fichier et défauts",
                 code == 0 and '"permissionDecision": "deny"' in s and json.dumps(cairn)[1:-1] in s
                 and "commentaire ouvert" in s and "aucun style" in s and "aucun bloc" in s, s)
        code, s = hook(dict(pub, tool_input={"file_path": "sans-style.html"}, cwd=tvg))
        verifier("vigile : hook, chemin relatif au cwd refusé", '"permissionDecision": "deny"' in s, s)
        verifier("vigile : hook, page saine, muet", hook(dict(pub, tool_input={"file_path": saine})) == (0, ""), "")
        verifier("vigile : hook, asset vrai, muet",
                 hook(dict(pub, tool_input={"file_path": cairn, "asset": True})) == (0, ""), "")
        verifier("vigile : hook, un Bash, muet", hook({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                                       "tool_input": {"command": "cat %s" % cairn}}) == (0, ""), "")
        md = os.path.join(tvg, "page.md")
        ecrire(md, "<!-- ouvert\n")
        verifier("vigile : hook, un .md, muet", hook(dict(pub, tool_input={"file_path": md})) == (0, ""), "")
        verifier("vigile : hook, JSON illisible, muet",
                 hook("pas du json") == (0, "") and hook('[1, "x"]') == (0, ""), "")
        verifier("vigile : hook, fichier illisible, muet",
                 hook(dict(pub, tool_input={"file_path": os.path.join(tvg, "absente.html")})) == (0, ""), "")


tester_vigile()


def tester_chef_page():
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

    with tempfile.TemporaryDirectory() as tcp:
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
        verifier("chef page (a) : jauge Imprévu, une décision, Q1 à deux options, Q2 à trois — sort 0, CARTES D1 Q1 Q2",
                 code == 0 and re.fullmatch(r"PAGE SAINE \d+ blocs\nCARTES D1 Q1 Q2\n", s) is not None, s)
        comptes = (page.count('name="Q2"'), page.count("(recommandé)"), page.count('class="jauge moyen"'))
        verifier("chef page (a) : name=\"Q2\" 3 fois, « (recommandé) » 1 fois, class=\"jauge moyen\" 1 fois",
                 comptes == (3, 1, 1), str(comptes))
        code2, s2 = appel(["vigile", pa])
        verifier("chef page (a) : vigile sur le fichier, PAGE SAINE du même compte de blocs",
                 code2 == 0 and s2 == s.split("\n")[0] + "\n", s2)
        verifier("chef page (a) : data-cle <projet>-<date>-<sujet> et <title> <projet> — <titre>",
                 'data-cle="Demo-2026-10-01-essai"' in page and "<title>Demo — Rapport d'essai</title>" in page, page[:200])
        comptes = (page.count("<h2>Tes réponses</h2>"), page.count("<script>"), page.count("<!--"))
        verifier("chef page (a) : « Tes réponses » et <script> 1 fois, aucun commentaire", comptes == (1, 1, 0), str(comptes))
        restes = [x for x in ("Le fil", "&lt;Projet&gt;", "<dépôt>") if x in page]
        verifier("chef page (a) : ni « Le fil », ni &lt;Projet&gt;, ni <dépôt>", restes == [], str(restes))
        verifier("chef page (a) : UTF-8, fins \\n, jamais \\r", a != b"" and b"\r" not in a and a.endswith(b"\n"), repr(a[-40:]))
        defaut = [p for p in (("name=\"D1\"", 2), ("name=\"Q1\"", 2)) if page.count(p[0]) != p[1]]
        verifier("chef page (a) : D1 et Q1 portent leurs deux boutons", defaut == [], str(defaut))
        verifier("chef page (a) : les puces d'en-tête passent par cellule_md",
                 "<li>Un <strong>point</strong> clé</li>" in page, page[page.find("<header"):][:300])

        # (b) un texte échappé, une valeur sûre dans son attribut
        d = base(projet="P & Q", titre="T < U")
        d["choix"][0]["titre"] = "a < b & **c**"
        d["choix"][0]["options"].append(option('a"b'))
        code, s, pb = faire(d, "b.html")
        b = octets_de(pb).decode("utf-8")
        verifier("chef page (b) : le titre de Q1 `a < b & **c**` échappé, gras rendu dans son <h3> — mutant : cellule_md ôté "
                 "du titre de question",
                 code == 0 and "<h3>🟡 Q1 · a &lt; b &amp; <strong>c</strong></h3>" in b, s + b[b.find("<h3>🟡 Q1"):][:120])
        verifier("chef page (b) : <title>, data-cle et value passent par esc seul, le guillemet d'une valeur devient &quot;",
                 "<title>P &amp; Q — T &lt; U</title>" in b and 'data-cle="P &amp; Q-2026-10-01-essai"' in b
                 and 'value="a&quot;b"' in b, b[:200])

        # (c) un commentaire de tête qui cite des balises : la page ne change pas d'un octet
        citee = gabarit.replace("<!--\n", '<!--\n  Cite <div class="page" data-cle="x"> et <script> ici.\n', 1)
        verifier("chef page (c) : prémisse, la copie cite ces balises dans son commentaire, avant les vraies",
                 citee != gabarit and -1 < citee.find("<script>") < citee.find("-->")
                 and -1 < citee.find('<div class="page"') < citee.find("-->"), citee[:300])
        code, s, pc = faire(base(), "c.html", citee)
        verifier("chef page (c) : balise citée dans le commentaire de tête — sort 0, page identique à l'octet à celle de (a) "
                 "— mutant : morceaux cherchés dans le gabarit brut",
                 code == 0 and a != b"" and octets_de(pc) == a, s)

        # (d) une page sans style ne part pas
        sans_tete = re.sub(r"<link\b[^>]*>|<style\b.*?</style>", "", gabarit, flags=re.S | re.I)
        verifier("chef page (d) : prémisse, la copie n'a ni <style> ni <link>",
                 "<style" not in sans_tete.lower() and "<link" not in sans_tete.lower(), sans_tete[:200])
        code, s, pd = faire(base(), "d.html", sans_tete)
        verifier("chef page (d) : copie sans style ni link → GARDE aucun style, fichier absent, sort 1 — mutant : résultat "
                 "de defauts_page ignoré",
                 code == 1 and not os.path.exists(pd)
                 and s == 'GARDE: %s — aucun style (ni balise style, ni link rel="stylesheet")\n' % pd, s)

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
            verifier("chef page (e) %s : GARDE, rien écrit, sort 1" % nom,
                     code == 1 and s == attendu and not os.path.exists(pe), s)

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
            verifier("chef page GARDE %s : une ligne, rien écrit, sort 1" % nom,
                     code == 1 and s.startswith(attendu) and s.count("GARDE:") == 1 and not os.path.exists(po), s)
        code, s, po = faire(base(), os.path.join("occupe", "p.html"))
        verifier("chef page GARDE écriture impossible : le dossier de sortie est un fichier",
                 code == 1 and s.startswith("GARDE: %s — écriture impossible" % po) and s.count("GARDE:") == 1, s)

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
        verifier("chef page complet : sort 0, CARTES D1 Q1 Q2", code == 0 and s.endswith("CARTES D1 Q1 Q2\n"), s)
        titres = ["Les chiffres", "Ce qui a été fait", "Les décisions prises seul", "Les choix à trancher",
                  "Ce qui a mal tourné", "Le fil", "Tes réponses"]
        places = [f.find("<h2>%s" % t) for t in titres]
        verifier("chef page complet : sept sections, dans l'ordre du gabarit", -1 not in places and places == sorted(places),
                 str(places))
        manques = [x for x in ('class="jauge ko">❌ Pas bon</span>', "Demo · 2026-10-01 · NUI1 à NUI3",
                               '<div class="chiffre"><b>1,2 $</b><span>coût</span></div>', '<span class="mono">vlp.py cout</span>',
                               "<td class=\"n\">NUI1</td>", "Trois choix pris.", '<div class="erreur">', "🔥 Un défaut",
                               '<div class="alerte">', "⚠️ Un doute", "<time>19:22</time>", "Fin du <strong>rapport</strong>.")
                   if x not in f]
        verifier("chef page complet : jauge ko, plage, chiffres, tableau, intro, mal, fil et pied", manques == [], str(manques))
        mots = [mod.html_jauge(m) for m in mod.JAUGE]
        attendus = ['<span class="jauge">✅ Tout va bien</span>', '<span class="jauge">🟢 Ça tient, mais…</span>',
                    '<span class="jauge moyen">⚠️ Imprévu</span>', '<span class="jauge ko">❌ Pas bon</span>',
                    '<span class="jauge ko">🔥 Grosse erreur</span>']
        verifier("chef page : les cinq mots de JAUGE, leur émoji et leur classe", mots == attendus, str(mots))
        code, s = appel(["vigile", pf])
        verifier("chef page complet : vigile sur le fichier, PAGE SAINE", code == 0 and s.startswith("PAGE SAINE"), s)

        # la commande : le vrai gabarit sous KIT, le JSON par @fichier, la date du jour par défaut
        jq = os.path.join(tcp, "q.json")
        ecrire(jq, json.dumps(base(), ensure_ascii=False))
        sortie = os.path.join(tcp, "cmd.html")
        code, s = appel(["chef", "page", "--questions", "@" + jq, "--sortie", sortie])
        verifier("chef page par la commande : sort 0, page identique à l'octet à celle de (a)",
                 code == 0 and s.endswith("CARTES D1 Q1 Q2\n") and a != b"" and octets_de(sortie) == a, s)
        sans_date = {k: v for k, v in base().items() if k != "date"}
        code, s, pj = faire(sans_date, "jour.html")
        m = re.search(r'data-cle="Demo-(\d{4}-\d\d-\d\d)-essai"', octets_de(pj).decode("utf-8"))
        verifier("chef page : sans date, le jour — AAAA-MM-JJ lu dans data-cle",
                 code == 0 and m is not None and datetime.date.fromisoformat(m.group(1)) <= datetime.date.today(), s)


tester_chef_page()

def tester_forme():
    """page --forme (chantier HAB1) : la forme d'une page ancienne refaite, ses chiffres gardés,
    même dans un dépôt dont les commits de fiche feraient changer le coût."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — page --forme n'est pas testée")
        return
    with tempfile.TemporaryDirectory() as tfo:
        sq = os.path.join(tfo, "s.jsonl")
        transcript(sq, 6, [T0 + d for d in (50, 200, 250, 400, 700, 1000)])
        fiches = os.path.join(tfo, "q.md")
        ecrire(fiches, QFICHES % (sq, sq))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(tfo, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=tfo, env=env, check=True, capture_output=True)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=tfo, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        page = os.path.join(tfo, "artefacts", "q.html")
        code, s = appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R",
                         "--date", "2026-01-05"])
        verifier("HAB1 : la page de départ se crée", code == 0, s)
        # L'ancien format : style dans la page, fiches à plat, bilan visible en bas, chiffres d'une autre mesure.
        html = avec_style_inline(lire(page))
        for balise in ("<details open>", "<details>", "</details>", "<summary>", "</summary>"):
            html = html.replace(balise, "")
        html = re.sub(r'<span class="cout mono">.*?</span>', "", html)
        # Écrits à la main sur les vieilles pages (18-evals, 11-conso du kit) : un libellé, un comptage.
        html = re.sub(r'(<span class="id">Q2</span>.*?<span class="etat">)Faite(</span>)', r"\1abandonnée\2", html, count=1, flags=re.S)
        html = re.sub(r'(<p class="mono" style="margin-top:.5rem">).*?(</p>)', r"\g<1>2 fiches · Q2 abandonnée · clos\2", html, count=1)
        c1, c2 = "≈1,1k (1 111) · 1 tours · 0,01 $", "≈2,2k (2 222) · 2 tours · 0,02 $"
        for q, c in (("Q1", c1), ("Q2", c2)):
            html = re.sub(r'(<span class="id">%s</span>.*?)(\s*</li>)' % q,
                          lambda m: m.group(1) + '\n        <span class="cout mono">%s</span>' % c + m.group(2),
                          html, count=1, flags=re.S)
        total = "Coût du chantier : ≈11,3M (11 262 523) · 42 tours · 3,40 $"
        hors = "Hors fiches : ≈5,0k (5 000) · 1 tours · 0,05 $"
        html = re.sub(r'<p class="mono cout-total">.*?</p>', '<p class="mono cout-total">%s</p>' % total, html, flags=re.S)
        html = re.sub(r'<p class="mono cout-hors">.*?</p>', '<p class="mono cout-hors">%s</p>' % hors, html, flags=re.S)
        i = html.index("  <!-- ZONE:bilan")
        fin = html.index("  </section>\n", i) + len("  </section>\n\n")
        bloc = html[i:fin].replace("<section hidden>", "<section>", 1).replace("<p></p>", "<p>Fini.</p>", 1)
        html = (html[:i] + html[fin:]).replace("  <footer>", bloc + "  <footer>", 1)
        verifier("HAB1 : la page de départ est à l'ancien format",
                 "<style>" in html and "<details" not in html and total in html
                 and html.index("ZONE:bilan") > html.index("ZONE:fiches"), html[:600])
        ecrire(page, html)
        code, s = appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        apres = lire(page)
        lu = mod.lis_page(apres)
        verifier("HAB1 : --forme garde le total 11 262 523 et le hors fiches — mutant : --forme ignoré",
                 code == 0 and apres.count(total) == 1 and apres.count(hors) == 1
                 and "total ≈11,3M (11 262 523) · 42 tours · 3,40 $" in s, s + apres)
        verifier("HAB1 : --forme garde les deux coûts de fiche (%s ; %s)" % (c1, c2),
                 lu["Q1"][2] == c1 and lu["Q2"][2] == c2, lu)
        verifier("HAB1 : --forme lie vlp.css, replie les fiches, remonte le bilan",
                 "<style>" not in apres and apres.count('href="vlp.css"') == 1 and apres.count("<details") >= 2
                 and apres.index("ZONE:bilan") < apres.index("ZONE:fiches") and "<p>Fini.</p>" in apres, apres[:1500])
        verifier("HAB1 : --forme garde libellé, comptage et date écrits sur l'ancienne page"
                 " — mutant : reprendre la date du jour",
                 "<span class=\"etat\">abandonnée</span>" in apres and "2 fiches · Q2 abandonnée · clos" in apres
                 and 'Mis à jour le <span class="mono">2026-01-05</span>' in apres, apres)
        ecrire(os.path.join(tfo, "avant.html"), html)
        code, s = appel(["comparer", os.path.join(tfo, "avant.html"), page])
        verifier("HAB1 : comparer, 0 ligne de texte perdue", code == 0 and s.rstrip().startswith("COMPARER 0 perdus"), s)
        code, s = appel(["vigile", page])
        verifier("HAB1 : la page repeinte, vigile PAGE SAINE", code == 0 and s.startswith("PAGE SAINE"), s)
        avant = lire(page)
        code, s = appel(["page", fiches, page, "--forme", "--date", "2026-01-06"])
        verifier("HAB1 : --forme deux fois ne change rien", code == 0 and lire(page) == avant, s)
        code, s = appel(["page", fiches, os.path.join(tfo, "neuve.html"), "--forme", "--creer", "--projet", "P",
                         "--titre", "T", "--resultat", "R"])
        verifier("HAB1 : --forme refuse --creer par une GARDE",
                 code == 1 and s.startswith("GARDE: --forme ne va pas avec --creer")
                 and not os.path.exists(os.path.join(tfo, "neuve.html")), s)
        # Témoin : sans --forme, la même page recompte — la preuve que le dépôt ferait changer le total.
        code, s = appel(["page", fiches, page, "--date", "2026-01-06"])
        verifier("HAB1 : sans --forme, le total change (témoin)", code == 0 and total not in lire(page), s)


tester_forme()


def projet_clos(dossier, liens=()):
    """Un projet à trois clos A, B, C : A et B à l'ancien format, C déjà lié à vlp.css ; `liens` :
    (plage, url) de lignes de ZONE:clos à lien, en plus d'une ligne sans lien par clos."""
    seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
             "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
    ecrire(os.path.join(dossier, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
    ecrire(os.path.join(dossier, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
           + "".join("| `%s.md` | chantier **clos** « %s », `%s1..%s1` |\n" % (x.lower(), x, x, x) for x in "ABC"))
    for x in "ABC":
        fiches = os.path.join(dossier, "ctx", "%s.md" % x.lower())
        page = os.path.join(dossier, "ctx", "artefacts", "%s.html" % x.lower())
        ecrire(fiches, seule % (x, x, x))
        appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", x, "--resultat", "R"])
        if x != "C":
            ecrire(page, avec_style_inline(lire(page)))
    rangs = [ligne_close(mod.arrondi(1500)).replace("Q1–Q2", "%s1" % x) for x in "ABC" if "%s1" % x not in dict(liens)]
    rangs += [ligne_close(mod.arrondi(1500)).replace("Q1–Q2", pl).replace("<td>Test ", '<td><a href="%s">Test</a> ' % u)
              for pl, u in liens]
    ecrire(os.path.join(dossier, "ctx", "artefacts", "feuille-de-route.html"),
           '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n' + "".join(rangs)
           + "        </tbody>\n      </table>\n")


def tester_repeindre():
    """repeindre (chantier HAB2) : les pages closes d'un projet, repeintes par page --forme."""
    with tempfile.TemporaryDirectory() as trp:
        projet_clos(trp)
        disque = lambda: {os.path.relpath(os.path.join(r, n), trp): lire(os.path.join(r, n))
                          for r, _, ns in os.walk(trp) for n in ns}
        avant = disque()
        code, s = appel(["repeindre", trp, "--a-blanc"])
        verifier("HAB2 : --a-blanc annonce 2 repeintes et ne change aucun octet",
                 code == 0 and "2 repeintes · 0 avec lien · 2 sans lien · 0 refusées · 1 déjà" in s
                 and disque() == avant, s)
        code, s = appel(["repeindre", trp])
        pages = [lire(os.path.join(trp, "ctx", "artefacts", "%s.html" % x)) for x in "ab"]
        verifier("HAB2 : repeindre, 2 repeintes · 0 avec lien · 2 sans lien · 0 refusées, 1 déjà"
                 " — mutant : ne pas filtrer les pages déjà au format",
                 code == 0 and s.splitlines()[-1] == "REPEINDRE 2 repeintes · 0 avec lien · 2 sans lien"
                 " · 0 refusées · 1 déjà · 0 sans page" and s.count("REPEINTE ") == 2
                 and all("<style>" not in p and 'href="vlp.css"' in p for p in pages), s)
        code, s = appel(["repeindre", trp])
        verifier("HAB2 : relancé, 0 repeintes, 3 déjà", code == 0 and "0 repeintes" in s and "3 déjà" in s, s)
        code, s = appel(["repeindre", os.path.join(trp, "ctx")])
        verifier("HAB2 : pas de CHANTIER.md, une GARDE", code == 1 and s.startswith("GARDE: pas de CHANTIER.md"), s)


tester_repeindre()


def tester_liens():
    """lien et liens (chantier HAB3) : l'URL en ligne d'une page, dans la section `## Lien` de son .md."""
    ua, ub, ub2 = ("https://claude.ai/artifact/%s" % k for k in ("aaa", "bbb", "bbb2"))
    with tempfile.TemporaryDirectory() as tli:
        projet_clos(tli, [("A1", ua), ("B1", ub), ("B1", ub2)])
        art = os.path.join(tli, "ctx", "artefacts")
        md_c = os.path.join(art, "c.md")
        avant = mod.lire_abri(md_c)
        code, s = appel(["lien", os.path.join(art, "c.html"), "https://claude.ai/artifact/ccc"])
        apres = mod.lire_abri(md_c)
        verifier("HAB3 : lien écrit l'URL, lire_abri la relit, le reste intact"
                 " — mutant : texte_abri oublie la section",
                 code == 0 and s.startswith("LIEN écrit") and apres["lien"] == "https://claude.ai/artifact/ccc"
                 and dict(apres, lien="") == avant and "## Lien\nhttps://claude.ai/artifact/ccc\n" in lire(md_c), (s, apres, avant))
        code, s = appel(["lien", os.path.join(art, "c.html"), "https://claude.ai/artifact/ccc"])
        verifier("HAB3 : lien relancé, déjà", code == 0 and s.startswith("LIEN déjà"), s)
        code, s = appel(["lien", os.path.join(art, "c.html"), "pas-une-url"])
        verifier("HAB3 : lien refuse une URL inattendue", code == 1 and s.startswith("GARDE: lien inattendu"), s)
        code, s = appel(["liens", tli])
        verifier("HAB3 : liens pose A, signale B en doublon, C sans lien dans la feuille",
                 code == 0 and s.splitlines()[-1] == "LIENS 1 écrits · 0 déjà · 1 doublons · 1 sans lien · 0 sans page"
                 and "DOUBLON %s · %s · %s" % (os.path.join(art, "b.html"), ub, ub2) in s
                 and mod.lire_abri(os.path.join(art, "a.md"))["lien"] == ua
                 and mod.lire_abri(os.path.join(art, "b.md"))["lien"] == "", s)
        code, s = appel(["repeindre", tli, "--a-blanc"])
        verifier("HAB3 : repeindre lit le lien du .md", code == 0
                 and "REPEINTE %s · lien %s" % (os.path.join(art, "a.html"), ua) in s
                 and "2 repeintes · 1 avec lien · 1 sans lien" in s, s)


tester_liens()


def tester_hook_pyright():
    # TYP1 : le hook lance pyright quand un .py est indexé. claude caché (APPDATA, LOCALAPPDATA vides, PATH
    # sans lui), le vrai pyright aussi : un faux, en tête du PATH, sort 1.
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le bloc pyright du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        depot = os.path.join(t, "depot")
        shutil.copytree(os.path.join(RACINE, ".githooks"), os.path.join(depot, ".githooks"))
        faux = os.path.join(t, "faux")
        os.mkdir(faux)
        ecrire(os.path.join(faux, "pyright"), '#!/bin/sh\necho "faux pyright : 1 error"\nexit 1\n')
        os.chmod(os.path.join(faux, "pyright"), 0o755)
        sans = [d for d in os.environ.get("PATH", "").split(os.pathsep)
                if d and not shutil.which("pyright", path=d) and not shutil.which("claude", path=d)]
        base = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                    GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                    APPDATA="", LOCALAPPDATA="")
        ecrire(base["GIT_CONFIG_GLOBAL"], "")

        def git(chemins, *args):
            r = subprocess.run(["git"] + list(args), cwd=depot, env=dict(base, PATH=os.pathsep.join(chemins)),
                               capture_output=True, encoding="utf-8", errors="replace")
            return r.returncode, r.stdout + r.stderr

        git(sans, "init", "-q")
        git(sans, "config", "core.hooksPath", ".githooks")
        ecrire(os.path.join(depot, "a.md"), "a\n")
        git(sans, "add", "a.md")
        code, s = git([faux] + sans, "commit", "-q", "-m", "md")
        verifier("hook pyright : un .md seul passe", code == 0 and "pyright" not in s, s)
        ecrire(os.path.join(depot, "a.py"), "x = 1\n")
        git(sans, "add", "a.py")
        code, s = git([faux] + sans, "commit", "-q", "-m", "py")
        verifier("hook pyright : un .py en erreur est refusé", code == 1 and "faux pyright : 1 error" in s
                 and "pre-commit : pyright en erreur, commit refusé." in s, s)
        code, s = git(sans, "commit", "-q", "-m", "py")
        verifier("hook pyright : sans pyright, le .py passe en le disant", code == 0
                 and "pre-commit : pyright introuvable, vérification de types sautée." in s, s)


tester_hook_pyright()


def tester_contrat_ouverture():
    # CHK1 : --ouverture garde les sous-agents partis depuis l'ajout du fichier de fiches — leur heure à
    # eux : la session parente, partie avant, ne les écarte pas.
    if not shutil.which("git"):
        print("SAUTÉ: git absent — contrat --ouverture n'est pas testé")
        return

    def iso(s):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(T0 + s))

    with tempfile.TemporaryDirectory() as t:
        depot = os.path.join(t, "depot")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")

        def git(quand, *args):
            date = "@%d +0000" % (T0 + quand)
            subprocess.run(["git"] + list(args), cwd=depot, capture_output=True, check=True,
                           env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))

        ecrire(os.path.join(depot, "a.md"), "a\n")
        git(0, "init", "-q")
        git(0, "add", "a.md")
        git(0, "commit", "-q", "-m", "TODO : Q ajouté")
        q = os.path.join(depot, "q.md")
        ecrire(q, "# Chantier Q\n")
        git(1000, "add", "q.md")
        git(1000, "commit", "-q", "-m", "Chantier Q ouvert")
        ecrire(os.path.join(t, "p", "sess.jsonl"), json.dumps({"timestamp": iso(200)}) + "\n")

        def agent(id_, quand):
            chemin = os.path.join(t, "p", "sess", "subagents", "agent-%s.jsonl" % id_)
            ecrire(chemin, json.dumps({"timestamp": iso(quand), "message": {"role": "assistant", "content": [
                {"type": "text", "text": "FAITE — Q1 cochée."}]}}, ensure_ascii=False) + "\n")
            ecrire(chemin[:-len(".jsonl")] + ".meta.json", json.dumps({"agentType": "vlp:fiche"}))
            return chemin

        avant, apres = agent("avant", 500), agent("apres", 1500)
        code, s = appel(["contrat", avant, apres, "--ouverture", q])
        verifier("CHK1 : --ouverture garde le sous-agent parti après, session parente partie avant", code == 0
                 and s == "DEPUIS %s · ouverture de %s\napres vlp:fiche %s FAITE git 0 bloqué 0\n"
                 "CONTRAT 1 sous-agents · 0 écrivent dans Git · 0 bloqués par le gardien · "
                 "0 sans statut en tête · 0 interrompus\n" % (iso(1000), q, iso(200)), s)
        r = os.path.join(depot, "r.md")
        ecrire(r, "r\n")
        code, s = appel(["contrat", avant, "--ouverture", r])
        verifier("CHK1 : fichier jamais commité, GARDE", code == 1 and s == "GARDE: --ouverture %s : aucun commit "
                 "n'ajoute ce fichier : l'ouverture n'est pas commitée\n" % r, s)


tester_contrat_ouverture()


# --- FEU7 : l'eyebrow de la page du chantier finit par un lien vers la feuille de route ---

FICHES_FEU7 = """# Chantier FEU7

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [ ] — a
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P2 -->
## P2 [ ] — b
**Critère de fin**
<!-- /FICHE -->
"""


def tester_lien_feuille_de_route():
    with tempfile.TemporaryDirectory() as tab:
        proj = os.path.join(tab, "proj")
        fiches = os.path.join(proj, "p.md")
        page = os.path.join(proj, "artefacts", "p.html")
        carte = os.path.join(proj, "CHANTIER.md")
        ecrire(fiches, FICHES_FEU7)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/route\n")
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        html = lire(page)
        verifier("FEU7 : eyebrow, un lien vers la feuille de route", code == 0
                 and 'Proj · fiches P1–P2 · <a href="https://exemple/route">la feuille de route</a></div>' in html
                 and html.count("la feuille de route</a>") == 1, html)
        code, s = appel(["page", fiches, page])
        html = lire(page)
        verifier("FEU7 : régénérée deux fois, toujours un seul lien — mutant : garde d'unicité retirée",
                 code == 0 and html.count("la feuille de route</a>") == 1
                 and 'Proj · fiches P1–P2 · <a href="https://exemple/route">la feuille de route</a></div>' in html, html)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/autre\n")
        code, s = appel(["page", fiches, page])
        html = lire(page)
        verifier("FEU7 : URL changée, la nouvelle seule", code == 0
                 and 'Proj · fiches P1–P2 · <a href="https://exemple/autre">la feuille de route</a></div>' in html
                 and "exemple/route" not in html and html.count("la feuille de route</a>") == 1, html)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : aucun\n")
        code, s = appel(["page", fiches, page])
        html = lire(page)
        verifier("FEU7 : « aucun », le lien se retire", code == 0
                 and "la feuille de route" not in html and "Proj · fiches P1–P2</div>" in html, html)
        ecrire(carte, "# C\n\n- **artefact feuille de route** : https://exemple/route\n")
        ecrire(fiches, lire(fiches) + '\n<!-- FICHE:P3 -->\n## P3 [ ] — c\n**Critère de fin**\n<!-- /FICHE -->\n')
        code, s = appel(["page", fiches, page])
        html = lire(page)
        verifier("FEU7 : la plage reste intacte à côté du lien", code == 0
                 and 'Proj · fiches P1–P3 · <a href="https://exemple/route">la feuille de route</a></div>' in html, html)


tester_lien_feuille_de_route()


# --- FEU8 : le décompte au-dessus de la TODO détaille tailles, bloqués, total estimé ---

def tester_decompte_todo():
    gabarit = lire(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"))
    verifier("Dette BTN : le gabarit porte le décompte en valeur, sans style= (mutant : ancienne forme)",
             [l.strip() for l in gabarit.splitlines() if "resume-todo" in l]
             == ['<p class="resume-todo"><strong>&lt;n&gt; chantiers possibles</strong></p>'], "")
    verifier("FEU8 : borne_haute_cout — borne haute, ou None sans nombre avant « fiche »",
             mod.borne_haute_cout("~0,5 fiche") == 0.5 and mod.borne_haute_cout("~4 à 6 fiches") == 6.0
             and mod.borne_haute_cout("2-3 fiches") == 3.0 and mod.borne_haute_cout("à cadrer") is None
             and mod.borne_haute_cout("~½ fiche") == 0.5 and mod.borne_haute_cout("1½ fiche") == 1.5
             and mod.borne_haute_cout("🟡 pas estimé") is None and mod.borne_haute_cout("—") is None,
             (mod.borne_haute_cout("~0,5 fiche"), mod.borne_haute_cout("~4 à 6 fiches")))
    verifier("FEU8 : est_bloque — code absent, numéro ou plage d'un rang présent, tiret non bloquant",
             mod.est_bloque("`AAA`", ["AAA"], {"1", "2"}) is False
             and mod.est_bloque("`ZZZ`", ["AAA"], {"1", "2"}) is True
             and mod.est_bloque("3", ["AAA"], {"1", "3"}) is True
             and mod.est_bloque("1..9", ["AAA"], {"5"}) is True
             and mod.est_bloque("—", ["AAA"], {"1"}) is False, "")
    # Fichier d'état en mémoire, comme demandé par le critère de fin de FEU8 : 4 rangs, un de
    # chaque taille et un pas estimé ; deux bloqués (code `ZZZ` absent, numéro 1 encore présent).
    lignes = ["| # | Chantier | Apporte | Coût | Dépend |", "|---|---|---|---|---|",
              "| 1 | A | x | ~0,5 fiche | `AAA` |",
              "| 2 | B | x | ~4 à 6 fiches | `ZZZ` |",
              "| 3 | C | x | 2-3 fiches | 1 |",
              "| 4 | D | x | à cadrer | — |"]
    rangs = mod.todo_du_fichier(lignes)
    verifier("FEU8 : todo_du_fichier lit les 4 rangs", len(rangs) == 4, rangs)
    ligne = mod.resume_todo(len(rangs), *mod.decompte_todo(rangs, ["AAA"]))
    verifier("FEU8 : décompte de la TODO — tailles, bloqués, total estimé — mutant : borne basse au lieu de haute",
             ligne == "4 chantiers possibles · 1 petit, 1 moyen, 1 gros, 1 pas estimé · 2 bloqués · ≈9,5 fiches estimées",
             ligne)
    # BTN7 : le décompte en valeur, le texte d'avant la liste replié. Ici et non au niveau du
    # module, déjà au seuil de pyright (BTN1, BTN5).
    with tempfile.TemporaryDirectory() as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(tb, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Trois | a | 2 fiches | — |\n| 4 | Quatre | b | 1 fiche | 3 |\n\n## Journal\n")
        fdr = os.path.join(tb, "ctx", "artefacts", "feuille-de-route.html")
        lire_fdr = lambda: io.open(fdr, encoding="utf-8").read()
        # Le gabarit porte le décompte d'avant (`mono`, `style=`) : deux `feuille` n'en laissent qu'un.
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        appel(["feuille", tb, "--date", "2026-09-27"])
        code, s = appel(["feuille", tb, "--date", "2026-09-27"])
        sans = lire_fdr()
        decomptes = [l for l in sans.splitlines() if "resume-todo" in l]
        css = io.open(os.path.join(tb, "ctx", "artefacts", "vlp.css"), encoding="utf-8").read()
        verifier("BTN7 : décompte en <strong>, sans style=, un seul après deux feuille sur la forme d'avant,"
                 " .resume-todo dans vlp.css — mutant : RESUME_TODO sans l'ancienne forme",
                 code == 0 and decomptes == ['    <p class="resume-todo"><strong>2 chantiers possibles</strong>'
                                             ' · 1 petit, 1 moyen · 1 bloqué · ≈3 fiches estimées</p>']
                 and ".resume-todo {" in css and ".resume-todo strong" in css, (s, decomptes))
        verifier("BTN7 : sans préambule, aucun details.lecture", 'class="lecture"' not in sans, "")
        i = sans.index('<ol class="todo">')
        ancienne = sans[:i] + "<p>Lire ainsi.</p>\n    <ul>\n      <li>un</li>\n    </ul>\n    " + sans[i:]
        vieille = os.path.join(tb, "ancienne.html")
        ecrire(vieille, ancienne)
        ecrire(fdr, ancienne)
        code, s = appel(["feuille", tb, "--date", "2026-09-27"])
        neuve = lire_fdr()
        code2, s2 = appel(["feuille", tb, "--date", "2026-09-27"])
        _, sc = appel(["comparer", vieille, fdr])
        verifier("BTN7 : préambule replié une fois dans un details.lecture fermé, texte intact, 2e feuille"
                 " inchangée — mutant : details posé sans vérifier qu'il y est",
                 code == 0 and code2 == 0 and neuve.count('<details class="lecture">') == 1
                 and neuve == lire_fdr() and "inchangée" in s2 and "COMPARER 0 perdus" in sc
                 and ('<details class="lecture"><summary>Comment lire cette liste</summary>\n    <p>Lire ainsi.</p>\n'
                      '    <ul>\n      <li>un</li>\n    </ul>\n    </details>\n    <ol class="todo">') in neuve,
                 (s, s2, sc))


tester_decompte_todo()


# --- PIP1 : une ligne de TODO mal découpée rend une GARDE, plus un décompte faux ---

def tester_barre_todo():
    entete = ["| # | Chantier | Apporte | Coût | Dépend |", "|---|---|---|---|---|"]
    rangs = mod.todo_du_fichier(entete + ["| 1 | A | `sed x \\| sha256sum` | 2 fiches | — |"])
    verifier("PIP1 : une barre échappée dans du code reste un caractère — 5 cellules, rendue sans \\",
             rangs == [["1", "A", "`sed x \\| sha256sum`", "2 fiches", "—"]]
             and mod.cellule_md(rangs[0][2]) == '<span class="mono">sed x | sha256sum</span>', rangs)
    for ligne, n in (("| 2 | B | `sed x | sha256sum` | 2 fiches | — |", 6), ("| 3 | C | x | — |", 4)):
        try:
            mod.todo_du_fichier(entete + [ligne])
            dit = "aucune erreur"
        except ValueError as e:
            dit = str(e)
        verifier("PIP1 : une ligne à %d cellules lève une ValueError qui la nomme — mutant : >= 5" % n,
                 dit.startswith("ligne %s de la TODO : %d cellules au lieu de 5" % (ligne[2], n)), dit)
    with tempfile.TemporaryDirectory() as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        etat = os.path.join(tp, "ctx", "08-etat.md")
        ecrire(etat, "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
                     "| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
        fdr = os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        code, s = appel(["feuille", tp, "--date", "2026-09-29"])
        avant = io.open(fdr, encoding="utf-8").read()
        verifier("PIP1 : une TODO saine passe", code == 0 and "GARDE" not in s, s)
        ecrire(etat, "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
                     "| 3 | Trois | `sed | sha256sum` | 2 fiches | — |\n\n## Journal\n")
        code, s = appel(["feuille", tp, "--date", "2026-09-29"])
        verifier("PIP1 : feuille rend GARDE avec le numéro, sort 1, la page ne bouge pas",
                 code == 1 and "GARDE: ligne 3 de la TODO : 6 cellules" in s
                 and io.open(fdr, encoding="utf-8").read() == avant, s)
        _, s = appel(["niveau", tp, "--date", "2026-09-29"])
        verifier("PIP1 : niveau compte la ligne comme un écart de la feuille",
                 "ÉCART: feuille: ligne 3 de la TODO : 6 cellules" in s, s)


tester_barre_todo()


# --- NUI10 : le tri du soir par script, lecture seule ---

def tester_trier():
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
    with tempfile.TemporaryDirectory() as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")
        etat = os.path.join(tp, "ctx", "08-etat.md")
        ecrire(etat, "# État\n\n" + entete + lignes_todo + "\n## Journal\n")
        code, s = appel(["trier", tp])
        lignes = s.splitlines()
        canal = [l for l in lignes if l.startswith("CANAL ")]
        verifier("NUI10 : trier sort 0, PRÊT pour AAA, BBB, CCC (dépend d'un code prêt), JJJ (dépend d'un rang prêt), III",
                 code == 0 and all("PRÊT %s" % c in lignes for c in ("AAA", "BBB", "CCC", "JJJ", "III")), s)
        verifier("NUI10 : FICHIERS — `vlp.py archive` donne vlp.py, un chemin à espace reste entier",
                 "FICHIERS AAA scripts/vlp.py" in lignes and "FICHIERS BBB vlp.py" in lignes
                 and "FICHIERS HHH dossier x/m.py" in lignes, s)
        verifier("NUI10 : un CANAL groupe AAA, BBB, CCC, JJJ et nomme vlp.py et la dépendance — mutant : chemin entier",
                 len(canal) == 3 and canal[0].startswith("CANAL 1 : AAA, BBB, CCC, JJJ — ")
                 and "fichier vlp.py : AAA, BBB" in canal[0] and "CCC dépend de AAA" in canal[0], canal)
        verifier("NUI10 : une prête sans lien — inconnu → à la page",
                 "CANAL 2 : HHH — inconnu → à la page" in canal and "CANAL 3 : III — inconnu → à la page" in canal, canal)
        verifier("NUI10 : DDD porte les cinq marques, la visuelle en cellule 3 — ÉCARTÉE, MARQUES à 5 — mutant : cellule 3 retirée",
                 any(l.startswith("ÉCARTÉE DDD") for l in lignes)
                 and "MARQUES DDD 5 : 🟡 1 · à trancher 1 · non mesuré 1 · %s 1 · push 1" % mod.MARQUE_VISUELLE in lignes, s)
        verifier("NUI10 : push en cellule 4 écarte FFF ; dépendance absente écarte GGG",
                 any(l.startswith("ÉCARTÉE FFF") for l in lignes) and any(l.startswith("ÉCARTÉE GGG") for l in lignes), s)
        verifier("NUI10 : SOIR pour HHH (~6 fiches), pas pour III (~½ fiche)",
                 any(l.startswith("SOIR HHH") for l in lignes) and not any(l.startswith("SOIR III") for l in lignes), s)
        verifier("NUI10 : trier n'écrit rien — le fichier d'état reste tel quel",
                 io.open(etat, encoding="utf-8").read() == "# État\n\n" + entete + lignes_todo + "\n## Journal\n", "")
        ecrire(etat, "# État\n\n" + entete + "| 1 | `AAA` — a | `sed x | sha256sum` | 2 fiches | — |\n\n## Journal\n")
        code, s = appel(["trier", tp])
        verifier("NUI10 : une barre non échappée — GARDE, sort 1", code == 1 and s.startswith("GARDE: ligne 1 de la TODO"), s)


tester_trier()


# --- NUI11 : le fichier des nuits, ses leçons et le TAUX imprimés par trier ---

def tester_fichier_nuits():
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    carte = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n\n"
             "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
    indice = ("# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
              "| `100-x.md` | un chantier |\n\nFin.\n")
    rang = ('          <tr>\n            <td>x</td>\n            <td class="mono">%s</td><td class="mono">2026-01-01</td>\n'
            '            <td class="mono">%s</td>\n            <td>y</td>\n          </tr>\n')
    lecon = "- 2026-09-26 · N=%d · %s · jouées 3 sur 5 · nuits 2026-09-25 · sessions s1"
    env = os.environ.get("CLAUDE_CODE_SESSION_ID")
    os.environ["CLAUDE_CODE_SESSION_ID"] = ""
    with tempfile.TemporaryDirectory() as tp:
        subprocess.run(["git", "init", "-q"], cwd=tp, check=True, capture_output=True)
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
        verifier("NUI11 (a) : 00, 08, 100 → 101-nuits.md, sa ligne d'index juste sous celle de 100 ; trier sans fichier le dit",
                 chemin == os.path.join(tp, "ctx", "101-nuits.md") and os.path.isfile(chemin)
                 and idx[idx.index("| `100-x.md` | un chantier |") + 1].startswith("| `101-nuits.md` |")
                 and "**clos**" not in avant and "**ouvert**" not in avant and "NUITS absent" in s0, (chemin, idx, s0))
        verifier("NUI11 (a) : relancé, même chemin, index inchangé ; archiver ne la déplace pas",
                 mod.fichier_nuits(tp, True) == chemin and lire_idx() == avant
                 and appel(["archiver", tp])[1].startswith("ARCHIVÉ 0 ") and lire_idx() == avant, lire_idx())
        # (b) écrire, retirer, indice, plafond, forme
        ligne_t = "| 2026-09-25 | A | NUI | 3/2/1 | 4,50 |"
        premiere, seconde = mod.nuits_ecrire(chemin, ligne_t), mod.nuits_ecrire(chemin, ligne_t)
        l2 = lecon % (2, "cause un")
        mod.nuits_ecrire(chemin, l2)
        mod.nuits_ecrire(chemin, l2)
        lu = io.open(chemin, encoding="utf-8").read()
        verifier("NUI11 (b) : nuits_ecrire deux fois → une ligne de table, une leçon",
                 premiere is True and seconde is False and lu.count(ligne_t) == 1 and lu.count(l2) == 1
                 and lu.index(ligne_t) < lu.index("## Leçons") < lu.index(l2), lu)
        code, s = appel(["trier", tp])
        verifier("NUI11 (b) : N=2 → la leçon porte « indice », sous --- Leçons ---, sort 0",
                 code == 0 and "--- Leçons : ctx/101-nuits.md (lignes " in s and l2 + " — indice" in s.splitlines(), s)
        retiree = mod.nuits_retirer(chemin, l2, "2026-09-27", "NUI12")
        encore = mod.nuits_retirer(chemin, l2, "2026-09-27", "NUI12")
        code, s = appel(["trier", tp])
        verifier("NUI11 (b) : nuits_retirer → suffixe, leçon gardée, plus d'indice, rien la seconde fois",
                 retiree is True and encore is False
                 and l2 + " — retirée le 2026-09-27 par NUI12" in s.splitlines() and " — indice" not in s and code == 0, s)
        for k in range(12):
            mod.nuits_ecrire(chemin, lecon % (3, "cause %d" % k))
        code, s = appel(["trier", tp])
        verifier("NUI11 (b) : 12 vivantes + 1 retirée → pas de GARDE — mutant : retirées comptées vivantes",
                 code == 0 and "GARDE" not in s, s)
        mod.nuits_ecrire(chemin, lecon % (3, "cause 12"))
        code, s = appel(["trier", tp])
        verifier("NUI11 (b) : 13 vivantes → GARDE:, tri imprimé, sort 1",
                 code == 1 and "GARDE: 13 leçons vivantes" in s and "TRI 1 rangs" in s, s)
        ecrire(chemin, io.open(chemin, encoding="utf-8").read().replace(lecon % (3, "cause 12") + "\n", "- pas une forme\n"))
        code, s = appel(["trier", tp])
        verifier("NUI11 (b) : une leçon hors forme → GARDE: qui la cite, tri imprimé, sort 1",
                 code == 1 and "GARDE: leçon hors forme" in s and "- pas une forme" in s and "TRI 1 rangs" in s, s)
        ecrire(chemin, io.open(chemin, encoding="utf-8").read().replace("- pas une forme\n", ""))
        # (d) une ligne de table à 6 cellules
        try:
            mod.nuits_du_fichier(mod.NUITS_TETE[:6] + ["| a | b | c | d | e | f |"] + mod.NUITS_TETE[6:])
            dit = "aucune erreur"
        except ValueError as e:
            dit = str(e)
        verifier("NUI11 (d) : une ligne de table à 6 cellules lève une ValueError qui la nomme",
                 "ligne 7 de la table des nuits : 6 cellules au lieu de 5" in dit, dit)
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
        verifier("NUI11 (c) : 4 fiches acceptées → indice, sans chiffre — mutant : CARNET_MIN = 0",
                 "TAUX nuit indice — 4 fiches acceptées" in s.splitlines(), s)
        fiche(c2, "2026-09-26", "N5", [("jouer", 0.5, 99), ("relire", 9.5, 99)])
        fiche(c2, "2026-09-26", "R1", [("jouer", 100, 99), ("relire", 50, 99)], refus=1)
        fiche(c2, "2026-09-26", "R1", [("relance", 40, 99), ("relire", 50, 99)], refus=2)
        mod.carnet.ajouter(c1, nuit="2026-09-25", canal="A", chantier="NUI", role="relance", fiche="N1", usd_kit=None, usd_cli=99)
        code, s = appel(["trier", tp])
        verifier("NUI11 (c) : 5 fiches (1, 2, 3, 4, 10), une refusée deux fois hors compte, une ligne sans usd_kit"
                 " → médiane 3 — mutant : usd_kit lu en usd_cli",
                 "TAUX nuit médiane 3 $/fiche sur 5 fiches acceptées · sans usd_kit 1" in s.splitlines(), s)
        # TAUX jour : le prix par fiche de l'estimé d'`ouvrir`, sur la même feuille
        ecrire(os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)")
               + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)") + rang % ("D1–D2", "≈2,0M (2 000 000)")
               + rang % ("E1–E8", "non recompté — fichier introuvable · non mesurable") + "</tbody>\n")
        _, s = appel(["trier", tp])
        ecrire(os.path.join(tp, "ctx", "30-q.md"), "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n")
        appel(["ouvrir", tp, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        estime = re.search(r"— (≈[\d,]+ \$/fiche sur \d+ clos) \(le", io.open(os.path.join(tp, "ctx", "30-q.md"), encoding="utf-8").read())
        verifier("NUI11 (c) : TAUX jour = le prix par fiche de l'estimé d'ouvrir sur la même feuille (≈1,00 $/fiche sur 3 clos)",
                 estime is not None and estime.group(1) == "≈1,00 $/fiche sur 3 clos"
                 and "TAUX jour " + estime.group(1) in s.splitlines(), (s, estime))
    if env is None:
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    else:
        os.environ["CLAUDE_CODE_SESSION_ID"] = env


tester_fichier_nuits()


# --- NUI12 : le plan du soir, écrit dans le fichier des nuits, relu par la nuit ---

def tester_plan():
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    carte = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n\n"
             "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")
    indice = ("# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
              "| `100-x.md` | un chantier |\n\nFin.\n")
    todo = ("# État\n\n" + entete + "| 1 | `AAA` — a | x | 1 fiche | — |\n| 2 | `BBB` — b | x | 1 fiche | — |\n"
            "| 3 | `CCC` — c | x | 1 fiche | — |\n\n## Journal\n")
    env = os.environ.get("VLP_NUIT")
    with tempfile.TemporaryDirectory() as tp:
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
        verifier("NUI12 (0) : plan lire sans fichier des nuits → GARDE:, sort 1",
                 code == 1 and s.startswith("GARDE: pas de fichier des nuits") and not os.path.isfile(nuits), s)
        code, s = ecrire_plan(plan("passee", borne_usd=3, borne_chantiers=1, A=[ch("AAA", "AAA", "ancienne")]), "2026-09-25")
        verifier("NUI12 (0) : plan ecrire crée 101-nuits.md et sa ligne d'index, sort 0",
                 code == 0 and s.startswith("PLAN ctx/101-nuits.md · 2026-09-25 · 1 chantiers") and os.path.isfile(nuits)
                 and "| `101-nuits.md` |" in octets()[1].decode("utf-8"), s)
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
        verifier("NUI12 (a) : lire --canal A sous VLP_NUIT=1 → sort 0, la borne, 2 chantiers dans l'ordre",
                 code == 0 and code_a == 0 and s_a.startswith("BORNE 12.5 $ · 3 chantiers\n")
                 and lignes_a == ["CHANTIER AAA · canal A · rang 1 · préfixe AAA", "CHANTIER BBB · canal A · rang 2 · préfixe BBB"], s_a)
        verifier("NUI12 (a) : lire --canal B → son seul chantier",
                 code_b == 0 and [l for l in s_b.splitlines() if l.startswith("CHANTIER ")]
                 == ["CHANTIER CCC · canal B · rang 1 · préfixe CCC"], s_b)
        verifier("NUI12 (a) : lire --chantier BBB → ses réponses, aucune de AAA",
                 code_c == 0 and "- r2" in s_c.splitlines() and "r1a" not in s_c and "### AAA" not in s_c, s_c)
        verifier("NUI12 (a) : la réponse en é revient telle quelle, en puce",
                 "- r1b é" in lire_plan("--date", "2026-09-30", "--chantier", "AAA")[1].splitlines(), "")
        code, s = lire_plan("--date", "2026-09-29")
        verifier("NUI12 (a) : une date sans plan → GARDE:, sort 1; sans --date → GARDE:",
                 code == 1 and s.startswith("GARDE: pas de plan à la date 2026-09-29")
                 and lire_plan()[0] == 1, s)
        avant = texte()
        verifier("NUI12 (a) : la nuit passée reste, la nouvelle se pose avant ## Leçons",
                 avant.count("## Nuit 2026-09-25") == 1 and avant.index("## Nuit 2026-09-25")
                 < avant.index("## Nuit 2026-09-30") < avant.index("## Leçons"), avant)
        # (b) réécrit à la même date : une seule section, le reste octet pour octet
        code, s = ecrire_plan(plan("soir2", borne_usd=7, borne_chantiers=2, A=[ch("AAA", "AAA", "neuf")]), "2026-09-30")
        apres = texte()
        verifier("NUI12 (b) : même date → une seule `## Nuit`, remplacée, avant ## Leçons — mutant : autres sections perdues",
                 code == 0 and apres.count("## Nuit 2026-09-30") == 1 and "- neuf" in apres and "r1a" not in apres
                 and apres.index("## Nuit 2026-09-30") < apres.index("## Leçons"), apres)
        verifier("NUI12 (b) : la nuit passée, la table et ## Leçons identiques octet pour octet",
                 apres[:apres.index("## Nuit 2026-09-30")] == avant[:avant.index("## Nuit 2026-09-30")]
                 and apres[apres.index("## Leçons"):] == avant[avant.index("## Leçons"):], apres)
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
            verifier("NUI12 (c) : %s → GARDE:, sort 1, rien d'écrit — mutant : contrôle des lettres prises retiré" % nom,
                     code == 1 and s.startswith("GARDE: ") and octets() == fichier_avant, s)
        valide = plan("r9", borne_usd=1, borne_chantiers=1, A=[ch("AAA", "XXX")])
        fichier_avant = octets()
        os.environ["VLP_NUIT"] = "1"
        code, s = ecrire_plan(valide, "2026-10-01")
        del os.environ["VLP_NUIT"]
        verifier("NUI12 (c) : VLP_NUIT=1 → plan ecrire refuse (GARDE:, sort 1, rien d'écrit)",
                 code == 1 and s.startswith("GARDE: VLP_NUIT=1") and octets() == fichier_avant, s)
        code, s = ecrire_plan(valide, "2026-10-01")
        verifier("NUI12 (c) : le même plan, sans VLP_NUIT → écrit (le refus venait bien de la variable)", code == 0, s)
        # (d) carte : NUIT=1 une fois, dans le bloc d'avant les fiches ; rien sinon
        projet = os.path.join(tp, "proj")
        ecrire(os.path.join(projet, "CHANTIER.md"), CHANTIER % ("pz", "context AI/20-z.md (Z1..Z10)"))
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
        verifier("NUI12 (d) : carte sous VLP_NUIT=1 → NUIT=1 une fois, après --- CHANTIER.md --- et avant --- fiches : — mutant : ligne jamais écrite",
                 nuit.count("NUIT=1") == 1 and nuit.index("--- CHANTIER.md ---") < nuit.index("NUIT=1")
                 < next(k for k, l in enumerate(nuit) if l.startswith("--- fiches :")), nuit)
        verifier("NUI12 (d) : --relecteur, VLP_NUIT=0 et variable absente → aucune ligne NUIT=",
                 not any(l.startswith("NUIT=") for l in carte_sous("1", True) + carte_sous("0") + carte_sous(None)), "")
    if env is not None:
        os.environ["VLP_NUIT"] = env


tester_plan()


# --- BTN1: `vlp.js` joint aux pages, la ligne FILES ; charset et script posés une fois ---

def tester_joints():
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
               "- **fichier de fiches courant** : aucun\n"
               "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"),
               "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        return proj, fdr

    # (c) d'abord : une page d'avant, sans charset ni script, les reçoit une fois ; une seconde
    # régénération n'en ajoute pas — page du chantier, puis feuille de route.
    with tempfile.TemporaryDirectory() as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        ecrire(fiches, FICHES_PLI2)
        appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        ecrire(page, sans_balises(lire(page)))
        verifier("BTN1 : (c) la page d'avant n'a ni charset ni script",
                 "<meta charset" not in lire(page) and "vlp.js" not in lire(page), lire(page)[:300])
        code, s = appel(["page", fiches, page])
        verifier("BTN1 : (c) page d'avant régénérée — charset et script reçus une fois chacun",
                 code == 0 and balises_une_fois(lire(page)), s + lire(page)[:300])
        code, s = appel(["page", fiches, page])
        verifier("BTN1 : (c) régénérée deux fois, rien de plus — mutant : la balise posée sans vérifier sa présence",
                 code == 0 and balises_une_fois(lire(page)), lire(page)[:300] + lire(page)[-300:])
    with tempfile.TemporaryDirectory() as tab:
        proj, fdr = projet_btn1(tab)
        ecrire(fdr, sans_balises(lire(fdr)))
        code, s = appel(["feuille", proj])
        verifier("BTN1 : (c) feuille d'avant régénérée — charset et script reçus une fois chacun",
                 code == 0 and balises_une_fois(lire(fdr)), s + lire(fdr)[:300])
        code, s = appel(["feuille", proj])
        verifier("BTN1 : (c) feuille régénérée deux fois, rien de plus",
                 code == 0 and balises_une_fois(lire(fdr)), lire(fdr)[:300] + lire(fdr)[-300:])
    # Un charset cité dans un commentaire n'est pas un charset posé.
    cite = mod.migrer_joints("<!-- %s -->\n<p>x</p>\n" % META_BTN1)
    verifier("BTN1 : (c) charset cité en commentaire — le vrai est posé quand même",
             cite.startswith(META_BTN1 + "\n") and cite.count(META_BTN1) == 2, cite)

    # (a) et (b) : `page --creer`, puis `page` sans --creer ; vlp.js modifié à la main entre deux.
    with tempfile.TemporaryDirectory() as tab:
        fiches = os.path.join(tab, "p.md")
        art = os.path.join(tab, "artefacts")
        page = os.path.join(art, "p.html")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        verifier("BTN1 : (a) page --creer recopie vlp.css et vlp.js à l'octet, FILES les nomme"
                 " — mutant : vlp.js retiré de recopier_joints",
                 code == 0 and joints_recopies(s, art) and "CSS %s\n" % os.path.join(art, "vlp.css") in s, s)
        verifier("BTN1 : (b) page --creer — charset et script une fois chacun",
                 balises_une_fois(lire(page)), lire(page)[:300])
        with open(os.path.join(art, "vlp.js"), "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        verifier("BTN1 : (a) page (régénération) remet vlp.js à l'octet, FILES les nomme",
                 code == 0 and joints_recopies(s, art), s)
        verifier("BTN1 : (b) page régénérée — charset et script une fois chacun",
                 balises_une_fois(lire(page)), lire(page)[:300])
    with tempfile.TemporaryDirectory() as tab:
        proj, fdr = projet_btn1(tab)
        art = os.path.dirname(fdr)
        code, s = appel(["feuille", proj])
        verifier("BTN1 : (a) feuille recopie vlp.css et vlp.js à l'octet, FILES les nomme",
                 code == 0 and joints_recopies(s, art) and "CSS %s\n" % os.path.join(art, "vlp.css") in s, s)
        verifier("BTN1 : (b) feuille régénérée — charset et script une fois chacun",
                 balises_une_fois(lire(fdr)), lire(fdr)[:300])

    # `joints <dossier>` : les deux copies, et la ligne FILES seule ; un dossier absent est gardé.
    with tempfile.TemporaryDirectory() as tab:
        code, s = appel(["joints", tab])
        verifier("BTN1 : joints recopie les deux joints et n'écrit que la ligne FILES",
                 code == 0 and joints_recopies(s, tab) and len(s.splitlines()) == 1, s)
        code, s = appel(["joints", os.path.join(tab, "absent")])
        verifier("BTN1 : joints sur un dossier absent — GARDE, sort 1",
                 code == 1 and s.startswith("GARDE: dossier introuvable"), s)

    # Les deux gabarits : charset en première ligne, script en dernière, une fois chacun.
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = io.open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
        verifier("BTN1 : (b) gabarit %s — charset et script une fois chacun" % nom,
                 balises_une_fois(gabarit), gabarit[:300])
        # Dette BTN : /vlp:init publie la feuille remplie à la main, sans `feuille` — un lien local vers
        # autre chose qu'un joint y reste sans fichier (l'image couts.svg y restait, cassée).
        locaux = set(re.findall(r'(?:src|href)="(?!https?:|#|&lt;)([^"]+)"', gabarit))
        verifier("Dette BTN : gabarit %s — ne lie en local que les joints — mutant : image couts.svg remise"
                 % nom, locaux <= set(mod.JOINTS), str(sorted(locaux)))

    # --- BTN5 : le coût des chantiers clos en image, `couts.svg` et sa balise — imbriqué ici : le
    # module est au seuil de complexité de pyright (BTN1), et couts.svg est un joint de plus.
    IMG = '<img src="couts.svg"'

    def projet_btn5(tab, rangs):
        """Un projet équipé minimal, sa feuille posée depuis le gabarit, `rangs` en tête de ZONE:clos."""
        proj = os.path.join(tab, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **fichier de fiches courant** : aucun\n"
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
    with tempfile.TemporaryDirectory() as tab:
        proj, fdr = projet_btn5(tab, [rang("D", mod.arrondi(4000)), rang("C", "non mesuré"),
                                      rang("B", mod.arrondi(2000)), rang("A", mod.arrondi(1000))])
        svg = os.path.join(os.path.dirname(fdr), "couts.svg")
        code, s = appel(["feuille", proj])
        b = barres(svg)
        h = [x[1] for x in b]
        verifier("BTN5 : 4 lignes closes, une sans coût — couts.svg a 3 barres",
                 code == 0 and len(b) == 3, s + str(b))
        r = sorted(h)
        verifier("BTN5 : hauteurs dans le rapport 1 : 2 : 4, à 1 px près — mutant : hauteur constante",
                 abs(2 * r[0] - r[1]) <= 1 and abs(4 * r[0] - r[2]) <= 1, str(b))
        verifier("BTN5 : la plus récente (la plus chère) à droite, la plus ancienne à gauche"
                 " — mutant : ordre non retourné", b[-1][1] == max(h) and b[0][1] == min(h), str(b))
        dessin = lire(svg)
        formes = re.findall(r"<(?:rect|text)\b[^>]*>", dessin)
        verifier("BTN5 : le maximum en haut à gauche (arrondi + « tokens »), chaque forme a son fill",
                 "%s tokens</text>" % mod.arrondi(4000) in dessin and formes
                 and all('fill="#' in f for f in formes), dessin)
        files = files_de(s) or {}
        verifier("BTN5 : FILES nomme couts.svg, à côté de la feuille",
                 "couts.svg" in files and "\\" not in files["couts.svg"]
                 and os.path.samefile(files["couts.svg"], svg), s)
        html = lire(fdr)
        alt = re.search(r'<img src="couts\.svg" alt="([^"]*)"', html)
        verifier("BTN5 : la balise <img> une fois, avant details.clos ; alt : 3 barres, D le plus cher",
                 html.count(IMG) == 1 and html.index(IMG) < html.index('<details class="clos">')
                 and alt is not None and "3 barres" in alt.group(1) and alt.group(1).endswith("le plus cher : D"),
                 html[-3000:])
        donnees = re.search(r'<img src="couts\.svg"[^>]* data-couts="([^"]*)">', html)
        donnees = json.loads(mod.html.unescape(donnees.group(1))) if donnees else {}
        verifier("Graphique : data-couts porte la couleur et les barres [chantier, tokens, arrondi],"
                 " de la plus ancienne à la plus récente — mutant : attribut retiré",
                 donnees == {"couleur": mod.COUTS_BARRE, "barres": [[n, t, mod.arrondi(t)] for n, t in
                             (("A", 1000), ("B", 2000), ("D", 4000))]}, str(donnees))
        ecrire(fdr, mod.BALISE_COUTS.sub("", html))
        appel(["feuille", proj])
        verifier("BTN5 : une feuille d'avant, sans balise, la reçoit à sa régénération",
                 lire(fdr).count(IMG) == 1, lire(fdr)[-3000:])
        appel(["feuille", proj])
        verifier("BTN5 : régénérée encore, toujours une balise, même dessin",
                 lire(fdr).count(IMG) == 1 and lire(svg) == dessin, lire(fdr)[-3000:])

    # Sans coût (les lignes d'exemple du gabarit seules) : ni fichier — un ancien est retiré —, ni balise.
    with tempfile.TemporaryDirectory() as tab:
        proj, fdr = projet_btn5(tab, [rang("C", "non mesuré")])
        svg = os.path.join(os.path.dirname(fdr), "couts.svg")
        ecrire(svg, "<svg/>")
        code, s = appel(["feuille", proj])
        verifier("BTN5 : une feuille sans coût n'a ni couts.svg, ni balise, ni entrée FILES",
                 code == 0 and not os.path.exists(svg) and IMG not in lire(fdr)
                 and "couts.svg" not in (files_de(s) or {}), s + lire(fdr)[-2000:])

    # Des coûts mesurés, tous à 0 (dette BTN) : rien à dessiner, et pas de division par un maximum nul.
    with tempfile.TemporaryDirectory() as tab:
        proj, fdr = projet_btn5(tab, [rang("B", mod.arrondi(0)), rang("A", mod.arrondi(0))])
        code, s = appel(["feuille", proj])
        verifier("Dette BTN : coûts clos tous à 0 — feuille passe, sans couts.svg ni balise"
                 " — mutant : garde de couts_clos retirée",
                 code == 0 and not os.path.exists(os.path.join(os.path.dirname(fdr), "couts.svg"))
                 and IMG not in lire(fdr), s)


tester_joints()


def tester_attente():
    """attente (chantier LOC2) : la liste des pages refusées par la limite du jour, et son hook."""
    soir = datetime.datetime(2026, 9, 28, 20, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
    url, url2 = "https://claude.ai/artifact/AAA", "https://claude.ai/artifact/BBB"
    refus = "publish 429: daily publish limit for your plan reached (200) — resets at UTC midnight"

    def hook(d, maintenant=soir):
        o = io.StringIO()
        code = mod.cmd_attente_hook(io.StringIO(json.dumps(d)), o, maintenant)
        return code, o.getvalue()

    def projet(t, nom):
        p = os.path.join(t, nom)
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/20-z.md (Z1..Z10)"))
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
        return p, os.path.join(p, "context AI", "artefacts")

    with tempfile.TemporaryDirectory() as t:
        p, art = projet(t, "proj")
        liste, page, autre = os.path.join(art, "en-attente"), os.path.join(art, "88-boutons.html"), os.path.join(art, "91-x.html")
        verifier("attente : carte sans liste, pas de ligne ATTENTE=", "ATTENTE=" not in rendu(p), rendu(p))
        code, s = appel(["attente", "ajouter", "88-boutons.html", "--projet", p])
        verifier("attente ajouter : ATTENTE 1", (code, s) == (0, "ATTENTE 1\n"), s)
        code, s = appel(["attente", "ajouter", "88-boutons.html", "--url", url, "--projet", p])
        lignes = mod.lignes_de(liste)
        verifier("attente ajouter deux fois la même page : 1 ligne, la seconde url — mutant : ajouter sans remplacer",
                 (code, s) == (0, "ATTENTE 1\n") and len(lignes) == 1 and lignes[0].split("\t")[:2] == ["88-boutons.html", url]
                 and len(lignes[0].split("\t")) == 3, str(lignes))
        verifier("attente : aucun .tmp laissé", not os.path.exists(liste + ".tmp"), str(os.listdir(art)))
        code, s = appel(["attente", "lister", art])
        verifier("attente lister", (code, s) == (0, "ATTENTE=88-boutons.html %s\nATTENTE 1\n" % url), s)
        code, s2 = appel(["attente", "lister", p])
        verifier("attente lister la racine du projet : la même liste, pas un ATTENTE 0 muet — mutant : la racine lue comme un dossier artefacts",
                 (code, s2) == (0, s), s2)
        c = rendu(p)
        verifier("attente : la carte montre ATTENTE= avant le fichier de fiches courant",
                 0 <= c.find("ATTENTE=88-boutons.html %s\n" % url) < c.find("--- fiches :"), c)
        s = io.StringIO()
        mod.carte(p, s, True)
        verifier("attente : la carte du relecteur n'a pas de ligne ATTENTE=", "ATTENTE=" not in s.getvalue(), s.getvalue())
        code, s = appel(["attente", "ajouter", "../hors.html", "--projet", p])
        verifier("attente ajouter : une page hors des artefacts, GARDE", code == 1 and s.startswith("GARDE:"), s)
        code, s = appel(["attente", "retirer", page, "--projet", p])
        verifier("attente retirer la dernière (chemin absolu) : ATTENTE 0, fichier absent — mutant : laisser un fichier vide",
                 (code, s) == (0, "ATTENTE 0\n") and not os.path.exists(liste), s)

        # Le hook : un vrai dossier de tampons, comme TOU2 — le tampon du jour fait la différence
        ancien_tampon = mod.TAMPON_HOOKS
        mod.TAMPON_HOOKS = tempfile.mkdtemp()
        try:
            echec = {"hook_event_name": "PostToolUseFailure", "tool_name": "Artifact", "cwd": p,
                     "tool_input": {"file_path": page, "url": url}, "error": refus}
            code, s = hook(echec)
            verifier("attente hook : un 429 ajoute la page avec son url",
                     code == 0 and mod.lire_attente(art)[0][:2] == ("88-boutons.html", url), str(mod.lire_attente(art)))
            sortie = json.loads(s)["hookSpecificOutput"] if s else {}
            verifier("attente hook : 1er appel du jour, proposition à 02:00 / 02:10 (maintenant = 2026-09-28 20:00 UTC+2)",
                     sortie.get("hookEventName") == "PostToolUseFailure" and "88-boutons.html" in sortie.get("additionalContext", "")
                     and "à 02:00 locale" in sortie["additionalContext"] and "à 02:10 qui" in sortie["additionalContext"], s)
            code, s = hook(dict(echec, tool_input={"file_path": autre}))
            verifier("attente hook : 2e appel du jour, page ajoutée, pas de proposition — mutant : sans tampon_neuf",
                     s == "" and [e[0] for e in mod.lire_attente(art)] == ["88-boutons.html", "91-x.html"]
                     and mod.lire_attente(art)[1][1] == "aucune", s + str(mod.lire_attente(art)))
            code, s = hook(echec, soir + datetime.timedelta(days=1))
            verifier("attente hook : le lendemain (jour UTC), la proposition revient", '"additionalContext"' in s, s)
            p2, art2 = projet(t, "proj2")
            code, s = hook(dict(echec, cwd=p2, tool_input={"file_path": os.path.join(art2, "88-boutons.html")}))
            verifier("attente hook : un autre projet, sa propre proposition", '"additionalContext"' in s, s)
            avant = mod.lire_attente(art)
            for nom, d in (
                    ("page non lue", dict(echec, error="Nothing was published or removed: this publish touches files"
                                                       " whose published content is not what you last saw")),
                    ("refus du vigile", dict(echec, error="PreToolUse:Artifact hook error: Page cassée, publication"
                                                          " refusée (vlp.py vigile) — x.html : aucun style")),
                    ("vigile avant l'appel", dict(echec, hook_event_name="PreToolUse")),
                    ("autre outil", dict(echec, tool_name="Write")),
                    ("asset", dict(echec, tool_input={"file_path": page, "asset": True})),
                    ("page hors projet", dict(echec, tool_input={"file_path": os.path.join(t, "ailleurs", "x.html")}))):
                code, s = hook(d, soir + datetime.timedelta(days=2))
                verifier("attente hook : %s, rien — code 0, silence, liste inchangée" % nom,
                         code == 0 and s == "" and mod.lire_attente(art) == avant, s)
            code, s = hook(dict(echec, hook_event_name="PostToolUse", tool_input={"file_path": page}))
            verifier("attente hook : une publication réussie retire la page listée, en silence",
                     code == 0 and s == "" and [e[0] for e in mod.lire_attente(art)] == ["91-x.html"], s)
            code, s = hook(dict(echec, hook_event_name="PostToolUse", tool_input={"file_path": page}))
            verifier("attente hook : un succès d'une page absente de la liste, rien",
                     code == 0 and s == "" and [e[0] for e in mod.lire_attente(art)] == ["91-x.html"], s)
            o = io.StringIO()
            code = mod.main(["attente", "hook"], o, io.StringIO("pas du json"))
            verifier("attente hook : entrée illisible, muet, code 0", (code, o.getvalue()) == (0, ""), o.getvalue())
        finally:
            shutil.rmtree(mod.TAMPON_HOOKS, ignore_errors=True)
            mod.TAMPON_HOOKS = ancien_tampon

    zero, tache = mod.remise_a_zero(soir)
    verifier("attente : remise à zéro 02:00 et tâche 02:10 pour 2026-09-28 20:00 UTC+2",
             (zero.strftime("%Y-%m-%d %H:%M"), tache.strftime("%H:%M")) == ("2026-09-29 02:00", "02:10"), str(zero))


tester_attente()


def tester_publie():
    """publie (chantier JNT3) : la ligne FILES ne nomme que les joints changés depuis la
    dernière publication réussie de la page, notée par `attente hook`."""
    def files_de(s):
        for l in s.splitlines():
            if l.startswith("FILES "):
                return json.loads(l[len("FILES "):])
        return None

    def hook(d):
        return mod.cmd_attente_hook(io.StringIO(json.dumps(d)), io.StringIO())

    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "proj")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/20-z.md (Z1..Z10)"))
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
        art = os.path.join(p, "context AI", "artefacts")
        fiches, page, notes = os.path.join(t, "p.md"), os.path.join(art, "p.html"), os.path.join(art, "publie")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        files = files_de(s) or {}
        verifier("JNT3 : page jamais notée — FILES nomme les 2 joints", code == 0 and sorted(files) == ["vlp.css", "vlp.js"], s)
        # vlp.js en `{from}` relatif au dossier courant : les deux formes du paramètre `files`
        passe = {"vlp.css": files.get("vlp.css"), "vlp.js": {"from": os.path.relpath(files.get("vlp.js", t), p)}}
        succes = {"hook_event_name": "PostToolUse", "tool_name": "Artifact", "cwd": p,
                  "tool_input": {"file_path": page, "url": "https://claude.ai/artifact/AAA", "files": passe}}
        hook(dict(succes, hook_event_name="PostToolUseFailure", error="Nothing was published or removed"))
        verifier("JNT3 : une publication refusée ne note rien", not os.path.exists(notes), str(os.listdir(art)))
        hook(succes)
        lignes = mod.lignes_de(notes) if os.path.exists(notes) else []
        verifier("JNT3 : publication réussie — publie a 2 lignes, page p.html, chemin et {from}",
                 [l.split("\t")[:2] for l in lignes] == [["p.html", "vlp.css"], ["p.html", "vlp.js"]], str(lignes))
        code, s = appel(["page", fiches, page])
        verifier("JNT3 : rien de changé — FILES {} — mutant : ligne_files qui ignore la note", files_de(s) == {}, s)
        ecrire(notes, "".join(l.replace("\tvlp.css\t", "\tvlp.css\t0") + "\n" if "\tvlp.css\t" in l else l + "\n"
                              for l in lignes))
        code, s = appel(["page", fiches, page])
        verifier("JNT3 : vlp.css changé depuis la note — FILES ne nomme que lui", sorted(files_de(s) or {"x": 0}) == ["vlp.css"], s)
        hook(dict(succes, tool_input={"file_path": page, "files": {"vlp.css": files.get("vlp.css")}}))
        code, s = appel(["page", fiches, page])
        verifier("JNT3 : republié avec vlp.css seul — vlp.js garde sa note, FILES {}",
                 files_de(s) == {} and len(mod.lignes_de(notes)) == 2, s + lire(notes))


tester_publie()


def tester_apercu():
    """servir et apercu (chantier LOC4) : un serveur sans cache, et une seule entrée dans launch.json."""
    import contextlib
    import threading
    import urllib.error
    import urllib.request

    voisine = ('{"name": "gabarits", "runtimeExecutable": "py",\n'
               '      "runtimeArgs": ["-c", "print(1)"],   "port": 8792}')
    launch = '{\n  "version": "0.0.1",\n  "configurations": [\n    %s\n  ]\n}' % voisine
    with tempfile.TemporaryDirectory() as t:
        # Ni la config globale ni les exclusions de l'utilisateur ne masquent le `.gitignore` du test.
        anciens = {k: os.environ.get(k) for k in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "XDG_CONFIG_HOME")}
        os.environ.update(GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                          XDG_CONFIG_HOME=os.path.join(t, "xdg"))
        ecrire(os.environ["GIT_CONFIG_GLOBAL"], "")
        try:
            p = os.path.join(t, "proj")
            ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "aucun"))
            lancement = os.path.join(p, ".claude", "launch.json")
            lu = lambda: open(lancement, encoding="utf-8", newline="").read()
            entrees = lambda: [e for e in json.loads(lu())["configurations"] if e["name"].startswith("apercu-")]
            git_ok = bool(shutil.which("git"))
            if git_ok:
                subprocess.run(["git", "init", "-q"], cwd=p, check=True, capture_output=True)

            code, s = appel(["apercu", p])
            verifier("apercu : sans launch.json, le crée avec l'entrée et le premier port, sort 0",
                     code == 0 and s.startswith("APERCU écrit apercu-proj · port 8790 · ")
                     and [e["port"] for e in entrees()] == [8790], s)
            ecrire(lancement, launch)
            avant_voisine = lu().split(voisine)
            code, s = appel(["apercu", p])
            e = entrees()
            verifier("apercu : ajoute l'entrée après la voisine, port 8790 (8792 est pris ailleurs)",
                     code == 0 and s.startswith("APERCU écrit apercu-proj · port 8790") and len(e) == 1
                     and e[0]["runtimeArgs"][1:] == ["servir", os.path.join(p, "context AI", "artefacts").replace("\\", "/"),
                                                     "8790"], s)
            une_fois = lu()
            code, s = appel(["apercu", p])
            verifier("apercu : deux fois → une seule entrée apercu-, fichier identique, la voisine intacte à l'octet"
                     " — mutant : ajouter sans chercher l'entrée existante",
                     code == 0 and s.startswith("APERCU déjà apercu-proj") and lu() == une_fois
                     and len(entrees()) == 1 and lu().split(voisine)[0] == avant_voisine[0]
                     and voisine in lu(), s)
            code, s = appel(["apercu", p, "--port", "8801"])
            verifier("apercu : --port remplace l'entrée (toujours une seule), la voisine intacte",
                     code == 0 and "remplacé apercu-proj · port 8801" in s and [x["port"] for x in entrees()] == [8801]
                     and voisine in lu(), s)
            code, s = appel(["apercu", p])
            verifier("apercu : sans --port, garde le port de l'entrée déjà là",
                     code == 0 and "déjà apercu-proj · port 8801" in s, s)
            ecrire(lancement, '{"version": "0.0.1", "configurations": []}\r\n')
            code, s = appel(["apercu", p])
            verifier("apercu : tableau vide → une entrée, fin de ligne CRLF gardée",
                     code == 0 and len(entrees()) == 1 and "\r\n" in lu() and "\n" not in lu().replace("\r\n", ""), lu())
            for nom, contenu in (("illisible", "{pas du json"), ("sans tableau", '{"version": "0.0.1"}'),
                                 ("deux entrées", '{"configurations": [{"name": "apercu-proj"}, {"name": "apercu-proj"}]}')):
                ecrire(lancement, contenu)
                code, s = appel(["apercu", p])
                verifier("apercu : launch.json %s → GARDE:, sort 1, rien d'écrit" % nom,
                         code == 1 and s.startswith("GARDE:") and lu() == contenu, s)
            code, s = appel(["apercu", os.path.join(t, "nulle-part")])
            verifier("apercu : pas de projet équipé → GARDE:, sort 1", code == 1 and s.startswith("GARDE: pas de projet"), s)
            if not git_ok:
                print("SAUTÉ: git absent — la GARDE du .gitignore n'est pas testée")
            else:
                os.remove(lancement)
                code, s = appel(["apercu", p])
                verifier("apercu : sans .gitignore → écrit quand même, et une GARDE: le dit, sort 0"
                         " — mutant : ne pas consulter git check-ignore",
                         code == 0 and len(entrees()) == 1 and s.splitlines()[-1].startswith("GARDE: .claude/launch.json"), s)
                ecrire(os.path.join(p, ".gitignore"), ".claude/launch.json\n")
                code, s = appel(["apercu", p])
                verifier("apercu : .gitignore couvre le fichier → pas de GARDE:",
                         code == 0 and s.startswith("APERCU déjà") and "GARDE" not in s, s)

            # servir : un vrai serveur, sur un port libre choisi par le système (port 0).
            art = os.path.join(t, "art")
            ecrire(os.path.join(art, "a.html"), "<p>é</p>")
            ecrire(os.path.join(art, "vlp.js"), "var x = 'é';")
            ecrire(os.path.join(art, "sous", "b.svg"), "<svg/>")
            serveur = mod.faire_serveur(art, 0)
            fil = threading.Thread(target=serveur.serve_forever, daemon=True)
            fil.start()
            base = "http://127.0.0.1:%d" % serveur.server_port

            def prendre(chemin):
                try:
                    with urllib.request.urlopen(base + chemin) as r:
                        return r.status, r.headers, r.read().decode("utf-8")
                except urllib.error.HTTPError as err:
                    return err.code, err.headers, ""
            try:
                with contextlib.redirect_stderr(io.StringIO()):     # le journal des requêtes
                    statut, tetes, corps = prendre("/a.html")
                    verifier("servir : Cache-Control: no-store et html en UTF-8 — mutant : l'en-tête retiré",
                             statut == 200 and tetes["Cache-Control"] == "no-store"
                             and tetes["Content-Type"] == "text/html; charset=utf-8" and corps == "<p>é</p>", (statut, tetes))
                    verifier("servir : .js et .svg (sous-dossier) en UTF-8, sans cache",
                             prendre("/vlp.js")[1]["Content-Type"] == "text/javascript; charset=utf-8"
                             and prendre("/sous/b.svg")[1]["Content-Type"] == "image/svg+xml; charset=utf-8"
                             and prendre("/vlp.js")[1]["Cache-Control"] == "no-store", "types")
                    statut, tetes, corps = prendre("/_telephone?page=sous/b.svg")
                    verifier("servir : /_telephone rend la page dans un cadre de 375 px, sans cache",
                             statut == 200 and 'src="/sous/b.svg"' in corps and "width:375px" in corps
                             and tetes["Cache-Control"] == "no-store", corps)
                    for mauvais in ("", "?page=../secret", "?page=/etc/passwd", "?page=<script>", "?page=a.html%22onload%3D1"):
                        verifier("servir : /_telephone%s → 400, jamais de cadre" % mauvais,
                                 prendre("/_telephone" + mauvais)[0] == 400, mauvais)
                    verifier("servir : page absente → 404 sans cache",
                             prendre("/nulle.html")[0] == 404, "404")
            finally:
                serveur.shutdown()
                serveur.server_close()
            code, s = appel(["servir", os.path.join(t, "absent"), "8800"])
            verifier("servir : dossier absent → GARDE:, sort 1", code == 1 and s.startswith("GARDE: dossier introuvable"), s)
            code, s = appel(["servir", art, "99999"])
            verifier("servir : port impossible → GARDE:, sort 1", code == 1 and s.startswith("GARDE: port 99999"), s)
        finally:
            for k, v in anciens.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


tester_apercu()


def tester_retard_plugin():
    """ESR1 : un worktree du kit en avance de code sur le kit chargé — la carte le dit."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — retard_plugin n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(tr, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        kit, wt, autre = (os.path.join(tr, x) for x in ("kit", "wt", "autre"))

        def git(d, *args):
            subprocess.run(["git"] + list(args), cwd=d, env=env, check=True, capture_output=True)

        def commit(d, chemin, texte):
            ecrire(os.path.join(d, chemin), texte)
            git(d, "add", "-A")
            git(d, "commit", "-q", "-m", chemin)
        for d in (kit, autre):
            os.makedirs(d)
            git(d, "init", "-q", "-b", "main")
            commit(d, "CHANTIER.md", "# C\n\n- **fichier de fiches courant** : aucun\n")
        git(kit, "worktree", "add", "-q", "-b", "fiche", wt)
        commit(wt, "scripts/x.py", "x = 1\n")
        r1 = mod.retard_plugin(wt, kit=kit)
        commit(wt, "context AI/n.md", "note\n")
        r2 = mod.retard_plugin(wt, kit=kit)
        muets = (mod.retard_plugin(kit, kit=kit), mod.retard_plugin(autre, kit=kit))
        garde, mod.KIT = mod.KIT, kit
        try:
            o = io.StringIO()
            mod.carte(wt, o)
        finally:
            mod.KIT = garde
        lignes = [l for l in o.getvalue().split("\n") if l.startswith("PLUGIN_RETARD=")]
        verifier("ESR1 : retard du plugin — 1 commit de scripts/ compté, context AI/ non, muet sur le kit "
                 "et un autre dépôt, une ligne dans la carte — mutant : chemins retirés du rev-list",
                 r1 is not None and r1[0] == 1 and r1[2] == "fiche" and r2 is not None and r2[0] == 1
                 and muets == (None, None) and len(lignes) == 1 and lignes[0].startswith("PLUGIN_RETARD=1 ")
                 and lignes[0].endswith("merge --ff-only fiche"), (r1, r2, muets, lignes))
        commit(wt, "nuit.md", "nuit\n")
        r3 = mod.retard_plugin(wt, kit=kit)
        verifier("NUI13 : nuit.md compte dans le code du plugin — scripts/x.py et nuit.md font 2, context AI/n.md "
                 "reste hors compte — mutant : nuit.md retiré de CODE_PLUGIN",
                 r3 is not None and r3[0] == 2 and r3[2] == "fiche", r3)


tester_retard_plugin()


def tester_mutant():
    """MUT1 : casser, tester, lister les écarts, rendre à l'octet — CRLF, @fichier, gardes."""
    with tempfile.TemporaryDirectory() as tm:
        f, essai, apres = (os.path.join(tm, x) for x in ("f.py", "essai.py", "apres.txt"))
        source = "a = 1\r\nb = 2\r\nc = 3\r\n"
        ecrire(f, source)
        ecrire(essai, "import sys\nt = open(sys.argv[1], encoding='utf-8').read()\n"
                      "n = 0\nfor v in ('a = 1', 'b = 2'):\n    if v not in t:\n        print('ÉCART:', v); n += 1\n"
                      "sys.exit(1 if n else 0)\n")
        test = '"%s" "%s" "%s"' % (sys.executable, essai, f)

        def mutant(avant, apres_, test_=test):
            o = io.StringIO()
            code = mod.main(["mutant", f, avant, apres_, "--test", test_] if isinstance(test_, str)
                            else ["mutant", f, avant, apres_], o)
            with open(f, "rb") as g:
                return code, o.getvalue(), g.read() == source.encode()
        ecrire(apres, "a = 9\nb = 9")
        attrape = mutant("a = 1\nb = 2", "@" + apres)
        vivant = mutant("c = 3", "c = 4")
        absent = mutant("z = 0", "z = 1")
        double = mutant(" = ", "=")
        o = io.StringIO()
        plante = (mod.cmd_mutant(f, "c = 3", "c = 4", [os.path.join(tm, "absent.exe")], o), o.getvalue())
        with open(f, "rb") as g:
            rendu_plante = g.read() == source.encode()
        verifier("MUT1 : mutant — attrapé (2 écarts, @fichier sur CRLF), vivant, absent, double, tests qui ne "
                 "se lancent pas ; fichier rendu à l'octet chaque fois — mutant : restauration retirée",
                 attrape[0] == 0 and "MUTANT ATTRAPÉ 2 écart(s)" in attrape[1] and attrape[1].count("ÉCART:") == 2
                 and "RENDU " in attrape[1] and attrape[2]
                 and vivant[0] == 1 and "MUTANT VIVANT" in vivant[1] and vivant[2]
                 and absent[0] == 1 and "trouvé 0 fois" in absent[1] and absent[2]
                 and double[0] == 1 and "trouvé 3 fois" in double[1] and double[2]
                 and plante[0] == 1 and "ne se lancent pas" in plante[1] and rendu_plante,
                 (attrape, vivant, absent, double, plante, rendu_plante))


tester_mutant()


def tester_boucle():
    """NUI2 : test-boucle.py joue boucle.py et faux-claude.py ; lancé d'ici, un mutant de l'un ou de l'autre
    tombe aussi sous `vlp.py mutant` sans --test. Sa sortie passe en entier : son `ÉCART:` y remonte."""
    r = subprocess.run([sys.executable, os.path.join(ICI, "test-boucle.py")], capture_output=True,
                       encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    verifier("boucle : test-boucle.py (boucle.py et son faux claude) sort OK",
             r.returncode == 0 and r.stdout.strip() == "OK", (r.stdout or "") + (r.stderr or ""))


tester_boucle()


def tester_nuits():
    """NUI3 : `vlp.py nuits noter` écrit une `note`, ou le `stop`, au carnet de `VLP_CARNET`, sinon au
    carnet du jour du dépôt ; sans l'un ni l'autre : GARDE, sort 1."""
    env = {k: os.environ.pop(k, None) for k in ("VLP_CARNET", "VLP_CANAL")}
    try:
        with tempfile.TemporaryDirectory() as t:
            c = os.path.join(t, "nuit.jsonl")
            os.environ["VLP_CARNET"] = c
            sortie = [io.StringIO() for _ in range(3)]
            codes = [mod.main(["nuits", "noter", "première", "--canal", "A"], sortie[0]),
                     mod.main(["nuits", "noter", "deuxième"], sortie[1])]
            os.environ["VLP_CANAL"] = "B"
            codes.append(mod.main(["nuits", "noter", "arrêtez", "--stop"], sortie[2]))
            lignes = mod.carnet.lire(c)
            verifier("nuits noter : deux notes puis un stop au carnet de VLP_CARNET, NOTÉ <chemin>, canal de "
                     "--canal puis de VLP_CANAL",
                     codes == [0, 0, 0] and [d["note"] for d in lignes] == ["première", "deuxième", None]
                     and [d["stop"] for d in lignes] == [None, None, "arrêtez"]
                     and [d["canal"] for d in lignes] == ["A", None, "B"]
                     and all(s.getvalue() == "NOTÉ %s\n" % c for s in sortie)
                     and all(d["nuit"] == "nuit" and d["role"] is None for d in lignes), (codes, lignes))
            del os.environ["VLP_CARNET"], os.environ["VLP_CANAL"]
            o = io.StringIO()
            code = mod.cmd_nuits_noter("sans dépôt", None, False, o, dossier=t)
            verifier("nuits noter : sans dépôt Git ni VLP_CARNET → GARDE:, sort 1, rien d'écrit",
                     code == 1 and o.getvalue().startswith("GARDE:") and os.listdir(t) == ["nuit.jsonl"], (code, o.getvalue()))
            subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
            o = io.StringIO()
            code = mod.cmd_nuits_noter("du jour", "A", False, o, dossier=t)
            jour = mod.carnet.du_jour(t)
            verifier("nuits noter : sans VLP_CARNET, le carnet du jour du dépôt (.git/vlp-nuit/<date>.jsonl)",
                     code == 0 and jour and o.getvalue() == "NOTÉ %s\n" % jour and os.path.join(".git", "vlp-nuit") in jour
                     and [d["note"] for d in mod.carnet.lire(jour)] == ["du jour"], (code, o.getvalue(), jour))
    finally:
        for k, v in env.items():
            if v is not None:
                os.environ[k] = v


tester_nuits()


# --- NUI15 : `vlp.py matin`, la fusion de la nuit dans main -------------------------------------
JOUR_MATIN = "2026-10-01"
CARTE_MATIN = ("# Chantier courant\n\n- **alias** : mt\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n- **fichier de fiches courant** : ctx/40-loc.md (LOC1..LOC1)\n"
               "- **artefact feuille de route** : https://claude.ai/artifact/FEU\n"
               "- **artefact du chantier** : https://claude.ai/artifact/LOC\n- **artefact archive** : aucune\n\n"
               "Lettres de fiche déjà prises : E (Enchaîner), ENQ (Les écritures Git). "
               "Un nouveau chantier en choisit un autre.\n")
ETAT_MATIN = ("# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
              "| 79 | `LOC` — publier | a | 2 fiches | — |\n| 80 | `PAR` — deux chantiers | b | 3 fiches | — |\n\n"
              "## Journal\n")
HOOK_REFUSE = "#!/bin/sh\necho 'hook : refusé' >&2\nexit 1\n"
ORDRE_ABSENT = "ORDRE pointes — carnet absent\n"     # la 1re ligne de `matin` quand aucun carnet ne dit l'ordre


def git_matin(d, *args):
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("git %s : %s" % (" ".join(args), r.stderr))
    return r.stdout


def code_git(d, *args):
    return subprocess.run(["git"] + list(args), cwd=d, capture_output=True).returncode


def commit_matin(d, message, heure):
    """Un commit à `heure` (0 à 23) du jour de la nuit : la date de l'auteur et du commiteur est fixée."""
    os.environ["GIT_AUTHOR_DATE"] = os.environ["GIT_COMMITTER_DATE"] = "%sT%02d:00:00+00:00" % (JOUR_MATIN, heure)
    git_matin(d, "add", "-A")
    git_matin(d, "commit", "-q", "-m", message)


def depot_matin(d, archive=True, etat=ETAT_MATIN):
    """Le dépôt de 2cef70f : `main` à courant LOC et son artefact, des lettres jusqu'à ENQ, une archive de deux clos
    (`archive` faux : ils restent sur la feuille), la feuille au rang 79 — un seul commit, à l'heure 0."""
    os.makedirs(d)
    git_matin(d, "init", "-q", "-b", "main")
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
    ecrire(os.path.join(d, "ctx", "08-etat.md"), etat)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n")
    ecrire(os.path.join(d, "ctx", "40-loc.md"), "# Chantier LOC — Publier\n\n## LOC1 [ ] — a\n")
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 2\nc = 3\n")
    gabarit = lire(GABARIT_FEUILLE)
    debut, fin = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
    deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
            + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
    ecrire(os.path.join(d, "ctx", "artefacts", "feuille-de-route.html"),
           mod.resommer(gabarit[:debut] + deux + gabarit[fin:], 2, 70000))
    if archive:
        appel(["archive", d, "--url", "https://claude.ai/artifact/ARCH"])
    appel(["feuille", d, "--todo", "79", "--date", "2026-09-30"])
    commit_matin(d, "base", 0)


def branche_matin(d, canal, code, lettre, heure, clos=True, x=None, ligne=None, retire=None, modifs=None):
    """`nuit/<jour>-<canal>-<code>`, un commit à `heure` depuis `main` : `clos`, le chantier est clos (courant et
    artefact à `aucun`) et la feuille refaite sans badge ; `lettre`, sa lettre ajoutée à la liste ; `x`, le nouveau
    `scripts/x.py` ; `ligne`, la plage d'une ligne close de plus à l'archive ; `retire`, le rang ôté de la TODO ;
    `modifs(d)`, d'autres retouches, avant la feuille."""
    nom = "nuit/%s-%s-%s" % (JOUR_MATIN, canal, code)
    git_matin(d, "switch", "-q", "-c", nom, "main")
    chemin = os.path.join(d, "CHANTIER.md")
    carte_ = lire(chemin)
    if clos:
        carte_ = re.sub(r"(\*\*(?:fichier de fiches courant|artefact du chantier)\*\* : ).*", r"\g<1>aucun", carte_)
    if lettre:
        carte_ = carte_.replace(". Un nouveau chantier", ", %s (Chantier %s). Un nouveau chantier" % (lettre, code))
    ecrire(chemin, carte_)
    if retire:
        etat = os.path.join(d, "ctx", "08-etat.md")
        ecrire(etat, "".join(l for l in lire(etat).splitlines(True) if not l.startswith("| %s |" % retire)))
    if ligne:
        archive = os.path.join(d, "ctx", "artefacts", mod.ARCHIVE_CLOS)
        html = lire(archive)
        debut, _ = mod.zone(html, "clos", "<tbody>\n", "        </tbody>")
        ecrire(archive, html[:debut] + ligne_close(mod.arrondi(1000)).replace("Q1–Q2", ligne) + html[debut:])
    if x:
        ecrire(os.path.join(d, "scripts", "x.py"), x)
    if modifs:
        modifs(d)
    appel(["feuille", d, "--date", JOUR_MATIN])
    commit_matin(d, ("%s1 : %s" % (code, code)) if clos else "WIP %s" % code, heure)
    git_matin(d, "switch", "-q", "main")
    return nom


def etat_matin(d):
    """Ce que `matin` a laissé dans `d` : (lignes de CHANTIER.md, feuille, rang « en cours », zone d'archive)."""
    carte_ = mod.lignes_de(os.path.join(d, "CHANTIER.md"))
    html = lire(os.path.join(d, "ctx", "artefacts", "feuille-de-route.html"))
    debut, fin, forme = mod.zone_todo(html)
    return (carte_, html, mod.rang_en_cours(html[debut:fin], forme),
            html[html.index("<!-- ZONE:archive"):html.index("<!-- /ZONE:archive")])


def matin_a(tr):
    """(a) 2cef70f rejoué, avec un `origin` nu (f) : la clôture de PAR rend à main son chantier ouvert, son rang, ses lettres."""
    d, origine = os.path.join(tr, "a"), os.path.join(tr, "origine.git")
    depot_matin(d)
    git_matin(tr, "init", "-q", "--bare", "-b", "main", origine)
    git_matin(d, "remote", "add", "origin", origine)
    git_matin(d, "push", "-q", "origin", "main")
    pousse = git_matin(origine, "rev-parse", "main").strip()
    nom = branche_matin(d, "A", "PAR", "PAR", 1, ligne="PAR1–PAR3", retire="80")
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_, html, rang, archive = etat_matin(d)
    lettres = mod.lettres_prises(carte_)
    parents = git_matin(d, "rev-list", "--parents", "-n", "1", "HEAD").split()
    verifier("NUI15 (a) 2cef70f rejoué : courant et artefact de LOC rendus, PAR une fois après ENQ, rang 79, archive à "
             "3 clos, aucun conflit, HEAD à deux parents, arbre propre — mutants : lettres de la branche gardées, "
             "todo laissé à None",
             code == 0 and s == ORDRE_ABSENT + "FUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % nom
             and mod.champ(carte_, "fichier de fiches courant") == "ctx/40-loc.md (LOC1..LOC1)"
             and mod.champ(carte_, "artefact du chantier") == "https://claude.ai/artifact/LOC"
             and lettres == ["E", "ENQ", "PAR"] and rang == "79" and "3 chantiers clos" in archive
             and "<<<<<<<" not in "\n".join(carte_) + html and "Aucun chantier ouvert" not in html
             and len(parents) == 3 and not git_matin(d, "status", "--porcelain")
             and git_matin(d, "log", "-1", "--format=%s").strip() == "Matin %s : %s" % (JOUR_MATIN, nom)
             and "| 80 |" not in lire(os.path.join(d, "ctx", "08-etat.md")), (code, s, carte_, rang, archive[:300]))
    verifier("NUI15 (f) un dépôt nu en origin : sa main n'a pas bougé, matin ne pousse rien",
             git_matin(origine, "rev-parse", "main").strip() == pousse != git_matin(d, "rev-parse", "main").strip(),
             (pousse, git_matin(d, "rev-parse", "main")))


def matin_b(tr):
    """(b) A et B ajoutent chacun une lettre sur la même ligne, la feuille change des deux côtés : les deux lettres
    restent ; le carnet met B avant A, bien que la pointe de B soit la plus récente."""
    d = os.path.join(tr, "b")
    depot_matin(d)
    a, b = branche_matin(d, "A", "AAA", "AAA", 1), branche_matin(d, "B", "BBB", "BBB", 2)
    carnet_ = mod.carnet.du_jour(d, JOUR_MATIN)
    os.makedirs(os.path.dirname(carnet_), exist_ok=True)
    for canal, code in (("B", "BBB"), ("A", "AAA")):
        mod.carnet.ecrire(carnet_, mod.carnet.ligne({"nuit": JOUR_MATIN, "canal": canal, "chantier": code, "role": "fiche"}))
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_, html, rang, _ = etat_matin(d)
    sujets = git_matin(d, "log", "--first-parent", "--format=%s", "main").splitlines()
    verifier("NUI15 (b) deux nuits, une lettre chacune sur la même ligne, la feuille changée des deux côtés : les deux "
             "lettres gardées, le badge au rang 79, B avant A comme au carnet (pointe de B plus récente) — mutant : "
             "lettres de la branche gardées",
             code == 0 and "ORDRE" not in s and s.endswith("MATIN 2 fusionnée(s) · 0 de côté\n")
             and mod.lettres_prises(carte_) == ["E", "ENQ", "BBB", "AAA"] and rang == "79"
             and 'Lettres de fiche prises : <span class="mono">E, ENQ, BBB, AAA, LOC</span>' in html
             and [x for x in reversed(sujets) if x.startswith("Matin")]
             == ["Matin %s : %s" % (JOUR_MATIN, b), "Matin %s : %s" % (JOUR_MATIN, a)],
             (code, s, mod.lettres_prises(carte_), rang, sujets))


def matin_c(tr):
    """(c) sans carnet : l'heure de la pointe ; une pointe à chantier ouvert (commit WIP) reste de côté."""
    d = os.path.join(tr, "c")
    depot_matin(d)
    wip = branche_matin(d, "A", "WIP", None, 1, clos=False, x="a = 1\nb = 2\nc = 30\n")
    ok = branche_matin(d, "B", "OKK", "OKK", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI15 (c) sans carnet : ORDRE pointes, la pointe WIP DE CÔTÉ avant la suivante fusionnée, hors de main",
             code == 0 and s == (ORDRE_ABSENT + "DE CÔTÉ %s — ctx/40-loc.md\nFUSIONNÉE %s\n"
                                 "MATIN 1 fusionnée(s) · 1 de côté\n" % (wip, ok))
             and code_git(d, "merge-base", "--is-ancestor", wip, "main") == 1, (code, s))


def matin_d(tr):
    """(d) un `.py` changé des deux côtés : ARRÊT qui le nomme, fusion en cours, la suivante intacte ; résolu, relancé."""
    d = os.path.join(tr, "d")
    depot_matin(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, x="a = 1\nb = 20\nc = 3\n")
    b = branche_matin(d, "B", "BBB", "BBB", 2)
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 22\nc = 3\n")
    commit_matin(d, "main avance", 3)
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_ = lire(os.path.join(d, "CHANTIER.md"))
    verifier("NUI15 (d) un .py changé des deux côtés : ARRÊT qui le nomme et donne feuille --todo 79, sort 1, MERGE_HEAD "
             "là, CHANTIER.md réparé sans marque, la suivante pas fusionnée",
             code == 1 and s.startswith(ORDRE_ABSENT + "ARRÊT %s — conflit : scripts/x.py — après résolution : " % a)
             and s.endswith(' feuille "%s" --todo 79\n' % d)
             and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
             and code_git(d, "merge-base", "--is-ancestor", b, "main") == 1
             and "- **fichier de fiches courant** : ctx/40-loc.md (LOC1..LOC1)" in carte_ and "<<<<<<<" not in carte_,
             (code, s))
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 22\nc = 3\n")
    appel(["feuille", d, "--todo", "79", "--date", JOUR_MATIN])
    commit_matin(d, "résolu", 4)
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI15 (d) résolu, commité, relancé : DÉJÀ pour la branche résolue, la suivante fusionnée",
             code == 0 and s == ORDRE_ABSENT + "DÉJÀ %s\nFUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % (a, b),
             (code, s))


def matin_e(tr):
    """(e) un hook qui refuse (`core.hooksPath`) : ARRÊT, la fusion reste en cours."""
    d, hooks = os.path.join(tr, "e"), os.path.join(tr, "hooks-e")
    depot_matin(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    for h in ("pre-commit", "pre-merge-commit"):
        ecrire(os.path.join(hooks, h), HOOK_REFUSE)
        os.chmod(os.path.join(hooks, h), 0o755)
    git_matin(d, "config", "core.hooksPath", hooks.replace("\\", "/"))
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI15 (e) hook exit 1 par core.hooksPath : ARRÊT … commit refusé, la 1re ligne du hook, fusion en cours",
             code == 1 and s == ORDRE_ABSENT + "ARRÊT %s — commit refusé : hook : refusé\n" % nom
             and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0, (code, s))


def matin_h(tr):
    """(h) sans archive, les clos vivent sur la feuille : une feuille en conflit ne se reprend pas de main, ARRÊT."""
    d = os.path.join(tr, "h")
    depot_matin(d, archive=False)
    a, b = branche_matin(d, "A", "AAA", "AAA", 1), branche_matin(d, "B", "BBB", "BBB", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI15 (h) sans archive, feuille changée des deux côtés : la 1re fusionnée, ARRÊT sur la feuille pour la "
             "2e, fusion en cours",
             code == 1 and s.startswith(ORDRE_ABSENT + "FUSIONNÉE %s\nARRÊT %s — conflit : ctx/artefacts/feuille-de-route.html"
                                        " — après résolution : " % (a, b)) and s.endswith(" --todo 79\n")
             and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0, (code, s))


def matin_g(tr):
    """(g) les gardes : date, aucune branche, HEAD hors main, pas la racine, arbre sale, non équipé, CHANTIER.md sans
    libellés — chaque fois rien fusionné."""
    d, mini, vide = os.path.join(tr, "g"), os.path.join(tr, "mini"), os.path.join(tr, "vide")
    depot_matin(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    os.makedirs(vide)
    os.makedirs(mini)
    git_matin(mini, "init", "-q", "-b", "main")
    ecrire(os.path.join(mini, "CHANTIER.md"), "# C\n\n- **alias** : m\n")
    commit_matin(mini, "mini", 5)
    sorties = [appel(["matin", vide, JOUR_MATIN]), appel(["matin", d, "hier"]), appel(["matin", d, "2026-01-01"]),
               appel(["matin", mini, JOUR_MATIN])]
    git_matin(d, "switch", "-q", "-c", "autre")
    sorties.append(appel(["matin", d, JOUR_MATIN]))
    git_matin(d, "switch", "-q", "main")
    ecrire(os.path.join(d, "sous", "CHANTIER.md"), "# C\n")
    sorties.append(appel(["matin", os.path.join(d, "sous"), JOUR_MATIN]))
    shutil.rmtree(os.path.join(d, "sous"))
    ecrire(os.path.join(d, "scripts", "x.py"), "sale\n")
    sorties.append(appel(["matin", d, JOUR_MATIN]))
    attendu = ("GARDE: pas de CHANTIER.md dans", "GARDE: AAAA-MM-JJ attendu : hier", "GARDE: aucune branche nuit/2026-01-01-*",
               "GARDE: CHANTIER.md de main sans ses deux libellés", "GARDE: HEAD est sur autre, pas sur main",
               "n'est pas la racine d'un dépôt Git", "GARDE: arbre pas propre (1 chemin(s))")
    verifier("NUI15 (g) sept gardes : non équipé, date illisible, aucune branche, CHANTIER.md sans libellés, HEAD hors "
             "main, pas la racine, arbre sale — sort 1, « rien fusionné », aucune fusion commencée",
             all(c == 1 and a in s and "GARDE:" in s for (c, s), a in zip(sorties, attendu))
             and code_git(d, "merge-base", "--is-ancestor", nom, "main") == 1
             and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") != 0, sorties)


# --- NUI16 : `matin` fusionne par clé les fichiers que les deux canaux réécrivent ---------------
ETAT = "ctx/08-etat.md"
ETAT_NUI16 = ("# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
              "| 58 | `OLD` — ancien | o | 1 fiche | — |\n| 79 | `LOC` — publier | a | 2 fiches | — |\n"
              "| 80 | `PAR` — deux chantiers | b | 3 fiches | — |\n| 82 | `ENQ` — écritures | c | 2 fiches | — |\n\n"
              "## Journal des décisions\n\n## 2026-09-30 — base\nune ligne de base\n")
RANGEE_82 = "| 82 | `ENQ` — écritures | c | 2 fiches | — |\n"
CLAUDE_NUI16 = ("# Projet\n\n## Où on en est — en cinq lignes\n\n- Prouvé : le kit tient.\n"
                + "".join("- Clos le 2026-09-2%d : fait %s (chantier CC%s).\n" % (n, c, c)
                        for n, c in enumerate("ABCDEFGH"[:mod.CLOS_GARDES]))
                + "\n## Règles\n\n1. une règle.\n")
INDEX_NUI16 = ("# Index\n\n## Stable\n\n| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | l'état |\n"
               "| `00-INDEX-archive.md` | on relit un chantier clos |\n\n## Chantiers\n\n| Fichier | Lire quand |\n|---|---|\n"
               "| `40-loc.md` | on joue LOC — chantier **ouvert** |\n| `41-aaa.md` | on joue AAA — chantier **ouvert** |\n"
               "| `42-bbb.md` | on joue BBB — chantier **ouvert** |\n")
ARCHIVE_NUI16 = ("# Archive\n\n| Fichier | Lire quand |\n|---|---|\n| `50-z.md` | chantier **clos** Z |\n"
                 "| `10-x.md` | chantier **clos** X |\n")      # désordonnée exprès : seul le tri la remet en ordre
ATTENTE = "ctx/artefacts/en-attente"
PUBLIE_MATIN = "ctx/artefacts/publie"


def depot_nui16(d, fichiers=None, archive=True):
    """`depot_matin` sur l'état à quatre rangées et son journal, puis `fichiers` (`{chemin: texte}`) en un 2e commit."""
    depot_matin(d, archive=archive, etat=ETAT_NUI16)
    for chemin, texte in (fichiers or {}).items():
        ecrire(os.path.join(d, chemin), texte)
    if fichiers:
        commit_matin(d, "fichiers", 0)


def retoucher(chemin, f):
    """Une retouche pour `branche_matin(modifs=…)` : réécrit `chemin` (relatif au dépôt) par `f(texte)`."""
    def faire(d):
        complet = os.path.join(d, chemin)
        ecrire(complet, f(lire(complet)))
    return faire


def resumee(lettre, texte):
    """Ce que `clore --resume` fait de CLAUDE.md : `resume_claude`, qui coupe aux `CLOS_GARDES` dernières."""
    def faire(t):
        cl = t.split("\n")[:-1]
        mod.resume_claude(cl, lettre, texte, JOUR_MATIN, [])
        return "\n".join(cl) + "\n"
    return faire


def rangees(texte, motif=r"`(\d\d)-"):
    return re.findall(motif, "\n".join(l for l in texte.splitlines() if l.startswith("|")))


def matin_n_a(tr):
    """(a) 2cef70f : A retire la rangée 58 de la TODO, B en ajoute une 83 ; puis la 82 changée des deux côtés."""
    d = os.path.join(tr, "na")
    depot_nui16(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, retire="58")
    b = branche_matin(d, "B", "BBB", "BBB", 2,
                      modifs=retoucher(ETAT, lambda t: t.replace(RANGEE_82, RANGEE_82 + "| 83 | `NEW` — neuf | d | 1 fiche | — |\n")))
    code, s = appel(["matin", d, JOUR_MATIN])
    etat = lire(os.path.join(d, ETAT))
    parents = git_matin(d, "rev-list", "--parents", "-n", "1", "HEAD").split()
    verifier("NUI16 (a) 2cef70f : A retire la 58, B ajoute la 83 → 58 absente, 79, 80, 82, 83 là dans l'ordre, aucune marque, "
             "MERGE_HEAD absent, HEAD à deux parents — mutant : retiré d'un côté gardé",
             code == 0 and s == ORDRE_ABSENT + "FUSIONNÉE %s\nFUSIONNÉE %s\nMATIN 2 fusionnée(s) · 0 de côté\n" % (a, b)
             and re.findall(r"^\| (\d+) \|", etat, re.M) == ["79", "80", "82", "83"] and "<<<<<<<" not in etat
             and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") != 0 and len(parents) == 3,
             (code, s, etat))
    d = os.path.join(tr, "nb")
    depot_nui16(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ETAT, lambda t: t.replace("| c |", "| cA |")))
    b = branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ETAT, lambda t: t.replace("| c |", "| cB |")))
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI16 (a) la 82 changée en A et en B : GARDE: qui la nomme, sort 1, la fusion de B reste en cours, aucun commit "
             "pour B",
             code == 1 and "GARDE: ctx/08-etat.md : TODO : la rangée n° 82 est changée des deux côtés" in s
             and "FUSIONNÉE %s\n" % a in s and "ARRÊT %s — conflit : ctx/08-etat.md" % b in s
             and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
             and git_matin(d, "log", "-1", "--format=%s").strip() == "Matin %s : %s" % (JOUR_MATIN, a), (code, s))


def matin_n_b(tr):
    """(b) 5d7fc42 : A et B ajoutent un bloc au journal, en fin de fichier."""
    d = os.path.join(tr, "nj")
    depot_nui16(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ETAT, lambda t: t + "## 2026-10-01 — AAA\nbloc de A\n"))
    b = branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ETAT, lambda t: t + "## 2026-10-01 — BBB\nbloc de B\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    etat = lire(os.path.join(d, ETAT))
    verifier("NUI16 (b) 5d7fc42 : le journal de A puis celui de B, après le journal de la base, aucune marque, la TODO intacte",
             code == 0 and s.endswith("MATIN 2 fusionnée(s) · 0 de côté\n") and "<<<<<<<" not in etat
             and etat.index("une ligne de base") < etat.index("bloc de A") < etat.index("bloc de B")
             and etat.count("## 2026-10-01 — AAA") == etat.count("## 2026-10-01 — BBB") == 1
             and re.findall(r"^\| (\d+) \|", etat, re.M) == ["58", "79", "80", "82"], (code, s, etat))


def matin_n_c(tr):
    """(c) CLAUDE.md à `CLOS_GARDES` lignes « Clos le » : A et B en closent un chacun ; le reste de chacun change aussi."""
    d = os.path.join(tr, "nk")
    depot_nui16(d, {"CLAUDE.md": CLAUDE_NUI16})
    a = branche_matin(d, "A", "AAA", "AAA", 1,
                      modifs=retoucher("CLAUDE.md", lambda t: resumee("AAA", "fait A")(t).replace("le kit tient.", "le kit tient, A.")))
    b = branche_matin(d, "B", "BBB", "BBB", 2,
                      modifs=retoucher("CLAUDE.md", lambda t: resumee("BBB", "fait B")(t).replace("1. une règle.", "1. une règle, B.")))
    code, s = appel(["matin", d, JOUR_MATIN])
    claude = lire(os.path.join(d, "CLAUDE.md"))
    clos = [l for l in claude.splitlines() if mod.ENTREE_CLOS.match(l)]
    verifier("NUI16 (c) CLAUDE.md : CLOS_GARDES lignes « Clos le », les deux neuves dont A avant B, les plus anciennes coupées, "
             "le reste de A et de B gardé, aucune marque — mutant : coupe non appelée",
             code == 0 and len(clos) == mod.CLOS_GARDES and clos[-2].endswith("(chantier AAA).") and clos[-1].endswith("(chantier BBB).")
             and "(chantier CCB)" not in claude and "(chantier CCC)" in claude and "le kit tient, A." in claude and "1. une règle, B." in claude
             and "<<<<<<<" not in claude, (code, s, claude))


def matin_n_d(tr):
    """(d) l'index, son archive (désordonnée) et `archive-clos.html` : A et B clôturent chacun un chantier."""
    d = os.path.join(tr, "ni")
    depot_nui16(d, {"ctx/00-INDEX.md": INDEX_NUI16, "ctx/00-INDEX-archive.md": ARCHIVE_NUI16})

    def clot(retire, ouvre, apres, rangee):
        def faire(d):
            retoucher("ctx/00-INDEX.md", lambda t: t.replace(retire, "") + ouvre)(d)
            retoucher("ctx/00-INDEX-archive.md", lambda t: t.replace(apres, apres + rangee))(d)
        return faire
    branche_matin(d, "A", "AAA", "AAA", 1, ligne="AAA1–AAA2", modifs=clot(
        "| `41-aaa.md` | on joue AAA — chantier **ouvert** |\n", "| `43-ccc.md` | on joue CCC — chantier **ouvert** |\n",
        "| `50-z.md` | chantier **clos** Z |\n", "| `41-aaa.md` | chantier **clos** AAA |\n"))
    branche_matin(d, "B", "BBB", "BBB", 2, ligne="BBB1", modifs=clot(
        "| `42-bbb.md` | on joue BBB — chantier **ouvert** |\n", "| `44-ddd.md` | on joue DDD — chantier **ouvert** |\n",
        "| `10-x.md` | chantier **clos** X |\n", "| `20-bbb.md` | chantier **clos** BBB |\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    index, archive = lire(os.path.join(d, "ctx", "00-INDEX.md")), lire(os.path.join(d, "ctx", "00-INDEX-archive.md"))
    clos = lire(os.path.join(d, "ctx", "artefacts", mod.ARCHIVE_CLOS))
    debut, fin = mod.zone(clos, "clos", "<tbody>\n", "        </tbody>")
    corps = clos[debut:fin]
    places = [corps.find(m) for m in ("BBB1", "AAA1–AAA2", "X1", "Y1")]
    pied = re.search(r'Total cumulé</td><td class="mono"><strong>(.*?)</strong>', clos)
    verifier("NUI16 (d) index : 41 et 42 retirées, 43 et 44 ajoutées une fois, A avant B, le reste intact ; archive : "
             "10, 20, 41, 50 triées",
             code == 0 and rangees(index) == ["08", "00", "40", "43", "44"] and "<<<<<<<" not in index + archive
             and rangees(archive) == ["10", "20", "41", "50"], (code, s, index, archive))
    verifier("NUI16 (d) archive-clos.html : 4 lignes, celle de B en tête puis celle de A puis celles de la base ; le pied est "
             "`total_clos` de ces 4 lignes, le résumé en compte 4",
             len(mod.lignes_clos(corps)) == 4 and -1 not in places and places == sorted(places)
             and pied is not None and pied.group(1) == mod.arrondi(mod.total_clos(corps)) and mod.total_clos(corps) == 72000
             and "4 chantiers clos" in clos and "<<<<<<<" not in clos, (code, s, corps, pied))


def matin_n_e(tr):
    """(e) `en-attente` : retirée par A et intacte en B ; changée des deux côtés ; vide ; non suivie."""
    def heure(h):
        return "2026-10-01T%02d:00+02:00" % h

    def attente(*entrees):
        return "".join("%s\turl%s\t%s\n" % (p, p, h) for p, h in entrees)
    d = os.path.join(tr, "ne1")
    depot_nui16(d, {ATTENTE: attente(("P", heure(8)), ("Q", heure(8)))})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ATTENTE, lambda t: attente(("Q", heure(11)))))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ATTENTE, lambda t: attente(("P", heure(8)), ("Q", heure(10)))))
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI16 (e) en-attente : P retirée par A et intacte en B → absente ; Q changée des deux côtés → l'heure la plus "
             "récente, celle de A bien que B soit fusionnée après",
             code == 0 and lire(os.path.join(d, ATTENTE)) == attente(("Q", heure(11))), (code, s))
    d = os.path.join(tr, "ne2")
    depot_nui16(d, {ATTENTE: attente(("P", heure(8)), ("Q", heure(8)))})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ATTENTE, lambda t: attente(("Q", heure(8)))))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ATTENTE, lambda t: attente(("P", heure(8)))))
    code, s = appel(["matin", d, JOUR_MATIN])
    suivis = git_matin(d, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    verifier("NUI16 (e) en-attente : P retirée par A, Q par B → vide → le fichier est retiré, de l'arbre et de l'index — "
             "mutant : retrait ignoré",
             code == 0 and not os.path.exists(os.path.join(d, ATTENTE)) and ATTENTE not in suivis
             and not git_matin(d, "status", "--porcelain"), (code, s, suivis))
    d = os.path.join(tr, "ne3")
    depot_nui16(d)
    ecrire(os.path.join(d, ".git", "info", "exclude"), "en-attente\n")
    ecrire(os.path.join(d, ATTENTE), attente(("P", heure(9))))
    branche_matin(d, "A", "AAA", "AAA", 1)
    branche_matin(d, "B", "BBB", "BBB", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI16 (e) en-attente non suivie, présente dans l'arbre de main : ni écrite ni retirée",
             code == 0 and lire(os.path.join(d, ATTENTE)) == attente(("P", heure(9))), (code, s))


def publie_essai(tr, nom, base, ea, eb):
    """L'essai D2 : un dépôt à `publie merge=union`, deux branches écrites par `noter_publie` ; `(ce que Git en fait lu par
    lire_publie, ce que fusion_publie en fait, ses lignes imprimées)`."""
    d = os.path.join(tr, "pub-" + nom)
    art = os.path.join(d, "art")
    os.makedirs(art)
    git_matin(d, "init", "-q", "-b", "main")
    ecrire(os.path.join(d, ".gitattributes"), "publie merge=union\n")
    ecrire(os.path.join(d, "x"), "x\n")
    if base:
        mod.noter_publie(art, "P", base)
    commit_matin(d, "base", 0)
    for branche, e in (("A", ea), ("B", eb)):
        git_matin(d, "switch", "-q", "-c", branche, "main")
        os.makedirs(art, exist_ok=True)
        mod.noter_publie(art, "P", e)
        commit_matin(d, branche, 1)
        git_matin(d, "switch", "-q", "main")
    git_matin(d, "merge", "-q", "--no-ff", "-m", "A", "A")
    textes = [mod.lire_rev(d, rev, "art/publie") for rev in (git_matin(d, "merge-base", "HEAD", "B").strip(), "HEAD", "B")]
    infos = []
    par_cle = mod.notes_publie(mod.fusion_publie(d, "B", textes, [], infos).split("\n"))
    code_git(d, "merge", "-q", "--no-edit", "B")
    return mod.lire_publie(art), par_cle, infos


def matin_n_f(tr):
    """(f) `publie` : l'essai D2 en quatre cas, l'état choisi verrouillé, puis `matin` de bout en bout."""
    h = {n: n * 64 for n in "123"}
    cas = (("disjointes", {"a": h["1"]}, {"b": h["2"]}, {"c": h["3"]}),
           ("meme", {"a": h["1"]}, {"b": h["2"]}, {"b": h["2"]}),
           ("differentes", {"a": h["1"]}, {"a": h["2"]}, {"a": h["3"]}),
           ("sans-base", None, {"a": h["1"], "k": h["2"]}, {"c": h["3"], "k": h["2"]}))
    mesures = [publie_essai(tr, nom, base, ea, eb) for nom, base, ea, eb in cas]
    gitattributes = lire(os.path.join(ICI, "..", ".gitattributes"))
    verifier("NUI16 (f) essai D2, 4 cas : `merge=union` donne comme la clé pour des clés disjointes, une même clé de même "
             "empreinte et un fichier absent de la base, et non pour des empreintes différentes (deux lignes, la dernière lue ; "
             "la clé dit : retirée) — d'où la fusion par clé, et aucune ligne `merge=union` au .gitattributes du kit",
             [u == c for u, c, _ in mesures] == [True, True, False, True] and "merge=union" not in gitattributes
             and mesures[2][1] == {} and list(mesures[2][0].values()) == [h["3"]]
             and [len(i) for _, _, i in mesures] == [0, 0, 1, 0] and mesures[2][2][0].startswith("PUBLIE P a — "),
             [(u, c, i) for u, c, i in mesures])
    d = os.path.join(tr, "np")
    css, js = "feuille-de-route.html\tvlp.css\t", "feuille-de-route.html\tvlp.js\t"
    depot_nui16(d, {PUBLIE_MATIN: css + h["1"] + "\n" + js + h["1"] + "\n"})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(PUBLIE_MATIN, lambda t: css + h["2"] + "\n" + js + h["1"] + "\n"))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(PUBLIE_MATIN, lambda t: css + h["3"] + "\n" + js + h["2"] + "\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NUI16 (f) matin : vlp.css aux empreintes différentes → clé retirée et dite (`PUBLIE …`), vlp.js changée d'un seul "
             "côté → la valeur de B",
             code == 0 and "PUBLIE feuille-de-route.html vlp.css — empreintes différentes des deux côtés, clé retirée" in s
             and lire(os.path.join(d, PUBLIE_MATIN)) == js + h["2"] + "\n", (code, s))


def matin_r(tr):
    """NUI19 : `matin --rapport` — le carnet complété (sous-agents sommés, jamais 0), une ligne par chantier au fichier des
    nuits, le JSON de `chef page` ; rejoué, rien ne change. Un dépôt, un carnet de neuf lignes, un `HOME` à transcripts."""
    from decimal import ROUND_HALF_UP
    d, h = os.path.join(tr, "r"), os.path.join(tr, "home-r")
    depot_matin(d)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n| `40-loc.md` | x |\n")
    commit_matin(d, "index", 0)
    branche_matin(d, "A", "AAA", "AAA", 1)
    branche_matin(d, "B", "PAR", None, 2, clos=False, x="a = 1\nb = 2\nc = 30\n")
    c = mod.carnet.du_jour(d, JOUR_MATIN)
    assert c
    pr = os.path.join(h, ".claude", "projects", "p")
    chemins = {n: os.path.join(pr, n + ".jsonl") for n in ("s-aaa-1", "s-aaa-r", "s-par-1", "s-par-r")}
    sous = {n: os.path.join(pr, n, "subagents", "agent-a1.jsonl") for n in ("s-aaa-1", "s-par-1")}
    for p in sous.values():
        os.makedirs(os.path.dirname(p))
    transcript(chemins["s-aaa-1"], 2)
    transcript(sous["s-aaa-1"], 1)
    transcript(chemins["s-aaa-r"], 1)
    transcript(chemins["s-par-1"], 1)
    transcript(chemins["s-par-r"], 1)
    with open(sous["s-par-1"], "w", encoding="utf-8") as f:     # un sous-agent d'un modèle hors GRILLE
        f.write(json.dumps({"type": "assistant", "requestId": "r0", "message": {
            "id": "m0", "model": "claude-inconnu-9", "content": [], "usage": {
                "input_tokens": 1000, "output_tokens": 0, "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0}}}) + "\n")

    def somme(*transcripts):
        usd, tours = Decimal(0), 0
        for p in transcripts:
            r = mod.mesure().mesurer(p)[0]
            usd, tours = usd + r["usd_exact"], tours + r["tours"]
        return float(usd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), tours

    def octets(chemin):
        with open(chemin, "rb") as f:
            return f.read()

    def ligne_c(**champs):
        mod.carnet.ajouter(c, nuit=JOUR_MATIN, **champs)

    sauve = {k: os.environ.get(k) for k in ("HOME", "USERPROFILE", "VLP_CARNET", "VLP_CANAL")}
    os.environ.update(HOME=h, USERPROFILE=h, VLP_CARNET=c)
    os.environ.pop("VLP_CANAL", None)
    try:
        ligne_c(canal="A", chantier="AAA", fiche="AAA1", note="depart jouer", session="s-aaa-1", plugin_retard=4)
        ligne_c(canal="A", chantier="AAA", role="jouer", fiche="AAA1", issue="jouée", modeles_vus=["claude-sonnet-5-5"],
                usd_cli=7.77, tours_cli=9, session="s-aaa-1", plugin_retard=4)
        ligne_c(canal="A", chantier="AAA", role="relire", fiche="AAA1", issue="jouée", session="s-aaa-r")
        ligne_c(canal="A", chantier="AAA", role="clore", issue="jouée", session="s-aaa-c")
        ligne_c(canal="B", chantier="PAR", role="jouer", fiche="PAR1", issue="jouée", session="s-par-1")
        ligne_c(canal="B", chantier="PAR", role="relire", fiche="PAR1", issue="jouée", refus_n=1, cause="la cause du refus",
                reecriture="RÉÉCRITURE : refaire le test", session="s-par-r")
        ligne_c(canal="B", chantier="PAR", garde="mis-de-cote:test cassé")
        ligne_c(canal="B", chantier="DEP", issue="pas partie", garde="saute:PAR")
        ligne_c(canal="B", chantier="ZZZ", garde="mis-de-cote:sans branche")
        mod.carnet.noter(c, "A", "base abc123")
        codes = [appel(["nuits", "noter", "verser ceci", "--canal", "A", "--sorte", "reste"])[0],
                 appel(["nuits", "noter", "faire niveau", "--canal", "B", "--sorte", "case3"])[0],
                 appel(["nuits", "noter", "oubli de sorte", "--canal", "A"])[0]]
        code_stop, s_stop = appel(["nuits", "noter", "x", "--stop", "--sorte", "reste"])
        sortes = [(x["note"], x["sorte"]) for x in mod.carnet.lire(c) if x["note"] and not x["note"].startswith(("depart", "base"))]
        verifier("NUI19 (sorte) nuits noter --sorte : reste, case3 et sans sorte au carnet ; --sorte avec --stop → GARDE:, rien d'écrit",
                 codes == [0, 0, 0] and sortes == [("verser ceci", "reste"), ("faire niveau", "case3"), ("oubli de sorte", None)]
                 and code_stop == 1 and s_stop.startswith("GARDE: --sorte") and len(mod.carnet.lire(c)) == 13, (codes, sortes, s_stop))
        code, s = appel(["matin", d, JOUR_MATIN])
        verifier("NUI19 (r) matin d'abord : la branche close fusionnée, PAR de côté",
                 code == 0 and s.endswith("MATIN 1 fusionnée(s) · 1 de côté\n"), (code, s))
        avant = git_matin(d, "rev-list", "--count", "HEAD")
        rapport = os.path.join(tr, "rapport-r.json")
        code1, s1 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
        carnet1, json1 = octets(c), octets(rapport)
        nuits = mod.fichier_nuits(d)
        assert nuits
        nuits1 = octets(nuits)
        code2, s2 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
        lignes = mod.carnet.lire(c)
        par_session = {x["session"]: x for x in lignes if mod.carnet.est_session(x)}
        u_a, t_a = somme(chemins["s-aaa-1"], sous["s-aaa-1"])
        u_r, t_r = somme(chemins["s-aaa-r"])
        u_p, t_p = somme(chemins["s-par-r"])
        verifier("NUI19 (a) usd_kit et tours_kit = la somme de mesurer sur la session et son sous-agent, au centime ; usd_cli gardé — "
                 "mutant : sous-agents non sommés",
                 code1 == 0 and (par_session["s-aaa-1"]["usd_kit"], par_session["s-aaa-1"]["tours_kit"]) == (u_a, t_a)
                 and (par_session["s-aaa-r"]["usd_kit"], par_session["s-aaa-r"]["tours_kit"]) == (u_r, t_r)
                 and (par_session["s-par-r"]["usd_kit"], par_session["s-par-r"]["tours_kit"]) == (u_p, t_p)
                 and par_session["s-aaa-1"]["usd_cli"] == 7.77 and t_a == 3 and s1.startswith("KIT ? "), (par_session, s1))
        verifier("NUI19 (c) sans transcript, et sous-agent hors GRILLE : aucune clé _kit, une ligne KIT ? chacune, jamais 0 — "
                 "mutant : usd_exact None compté 0",
                 all(par_session[n]["usd_kit"] is None and par_session[n]["tours_kit"] is None for n in ("s-aaa-c", "s-par-1"))
                 and "KIT ? s-aaa-c — transcription introuvable\n" in s1
                 and "KIT ? s-par-1 — modèle hors grille (claude-inconnu-9)\n" in s1 and s1.count("KIT ? ") == 2, (par_session, s1))
        table = [l for l in octets(nuits).decode("utf-8").splitlines() if l.startswith("| " + JOUR_MATIN)]
        euros = lambda v: ("%.2f" % v).replace(".", ",")
        verifier("NUI19 (b) --rapport rejoué : carnet, fichier des nuits et JSON identiques à l'octet, une ligne de table par chantier "
                 "(4), aucune ajoutée au rejeu, verrou absent, HEAD inchangé",
                 code2 == 0 and carnet1 == octets(c) and nuits1 == octets(nuits) and json1 == octets(rapport)
                 and len(table) == 4 and "NUITS ctx/41-nuits.md · 4 ligne(s) ajoutée(s)\n" in s1
                 and "NUITS ctx/41-nuits.md · 0 ligne(s) ajoutée(s)\n" in s2
                 and "| %s | A | AAA | 1/1/0 | ≥ %s |" % (JOUR_MATIN, euros(u_a + u_r)) in table
                 and "| %s | B | PAR | 1/0/1 | ≥ %s |" % (JOUR_MATIN, euros(u_p)) in table
                 and not os.path.exists(c + ".verrou") and git_matin(d, "rev-list", "--count", "HEAD") == avant, (code2, table, s1, s2))
        donnees = json.loads(json1.decode("utf-8"))
        choix = donnees.get("choix", [])
        titres = [q["titre"] for q in choix]
        cote =next((q for q in choix if q["titre"].startswith("Mis de côté : PAR")), {})
        reste = next((q for q in choix if q["titre"].startswith("Reste à verser")), {})
        case3 = next((q for q in choix if q["titre"].startswith("Case 3")), {})
        sans = [m for m in donnees.get("mal", []) if m["titre"] == "NOTE SANS SORTE"]
        verifier("NUI19 (d) JSON : le mis de côté et le reste à trois réponses, la case 3 à deux, NOTE SANS SORTE une fois (les notes "
                 "de la boucle n'y sont pas), l'ÉCART de ZZZ dit, jamais un _cli ni un push",
                 [len(q.get("options", [])) for q in (cote, reste, case3)] == [3, 3, 2]
                 and [o["valeur"] for o in cote["options"]] == ["reprendre", "abandonner", "rejouer"]
                 and [o["valeur"] for o in reste["options"]] == ["verser", "fondre", "abandonner"]
                 and len(sans) == 1 and "oubli de sorte" in sans[0]["texte"]
                 and "NOTE SANS SORTE A — oubli de sorte\n" in s1
                 and "ÉCART B-ZZZ — le carnet le met de côté, Git non" in s1 and s1.count("ÉCART ") == 1
                 and any("Chantiers sautés à cause de lui : DEP" in p for p in cote["puces"])
                 and any("la cause du refus" in p for p in cote["puces"]) and any("`git branch -D nuit/" in o["effet"] for o in cote["options"])
                 and "7,77" not in json1.decode("utf-8") and "7.77" not in json1.decode("utf-8")
                 and "push" not in json1.decode("utf-8").lower() and len(titres) == 4
                 and [t.startswith("Mis de côté : ") for t in titres].count(True) == 2 and any("ZZZ" in t for t in titres),
                 (titres, cote, reste, case3, sans, s1))
        html = os.path.join(tr, "rapport-r.html")
        code, s = appel(["chef", "page", "--questions", "@" + rapport, "--sortie", html])
        verifier("NUI19 (d) le JSON passe `chef page` : PAGE SAINE, les cartes Q1 à Q4", code == 0 and s.startswith("PAGE SAINE ")
                 and s.endswith("CARTES Q1 Q2 Q3 Q4\n"), (code, s))
        code_h, s_h = appel(["nuits", "lecon", "hors forme", "--projet", d])
        lecon = "- %s · N=1 · cause un · jouées 3 sur 5 · nuits %s · sessions s-aaa-1" % (JOUR_MATIN, JOUR_MATIN)
        code_l, s_l = appel(["nuits", "lecon", lecon, "--projet", d])
        code_m, s_m = appel(["nuits", "lecon", lecon, "--projet", d])
        textes = octets(nuits).decode("utf-8").splitlines()
        verifier("NUI19 (d) nuits lecon : hors forme → GARDE:, sort 1, rien d'écrit ; une leçon sous `## Leçons`, rejouée → déjà là",
                 code_h == 1 and s_h.startswith("GARDE: leçon hors forme") and code_l == 0 and s_l == "LEÇON ctx/41-nuits.md · ajoutée\n"
                 and code_m == 0 and s_m == "LEÇON ctx/41-nuits.md · déjà là\n" and textes.count(lecon) == 1
                 and textes.index("## Leçons") < textes.index(lecon), (code_h, s_h, s_l, s_m))
        transcript(os.path.join(pr, "s-aaa-c.jsonl"), 1)     # la transcription qui manquait paraît : le chiffre de A/AAA changerait
        code3, s3 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
        table3 = [l for l in octets(nuits).decode("utf-8").splitlines() if l.startswith("| " + JOUR_MATIN)]
        mesuree = next(x for x in mod.carnet.lire(c) if x["session"] == "s-aaa-c")
        verifier("NUI19 (b) une ligne de table déjà là n'est pas refaite quand son chiffre aurait changé : toujours 4 lignes, "
                 "A/AAA inchangée, la session enfin mesurée au carnet — mutant : une ligne de table à chaque rejeu",
                 code3 == 0 and mesuree["usd_kit"] is not None and table3 == table
                 and "NUITS ctx/41-nuits.md · 0 ligne(s) ajoutée(s)\n" in s3 and "KIT ? s-aaa-c" not in s3, (code3, table, table3, s3))
        code_a, s_a = appel(["matin", d, "2026-10-02", "--rapport", rapport])
        verifier("NUI19 (r) --rapport sans carnet à cette date → GARDE:, sort 1",
                 code_a == 1 and s_a.startswith("GARDE: carnet de la nuit 2026-10-02 absent ou vide"), (code_a, s_a))
    finally:
        for k, v in sauve.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def tester_matin():
    """NUI15 : `vlp.py matin <projet> <date>` fusionne dans main les branches de la nuit et répare ce que Git perd sans
    conflit (methode-chantier.md:263-268). Un dépôt temporaire par cas, la config Git isolée, la date de chaque commit
    fixée ; l'environnement est rendu ensuite."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — matin n'est pas testé")
        return
    noms = ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME",
            "GIT_COMMITTER_EMAIL", "GIT_AUTHOR_DATE", "GIT_COMMITTER_DATE")
    gardes = {k: os.environ.get(k) for k in noms}
    try:
        with tempfile.TemporaryDirectory() as tr:
            ecrire(os.path.join(tr, "gitconfig"), "")
            os.environ.update(GIT_CONFIG_GLOBAL=os.path.join(tr, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                              GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                              GIT_COMMITTER_EMAIL="t@t")
            for cas in (matin_a, matin_b, matin_c, matin_d, matin_e, matin_h, matin_g,
                        matin_n_a, matin_n_b, matin_n_c, matin_n_d, matin_n_e, matin_n_f, matin_r):
                cas(tr)
    finally:
        for k, v in gardes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


tester_matin()

if ECARTS:
    sys.exit(1)
print("OK")
