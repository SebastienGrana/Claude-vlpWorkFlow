#!/usr/bin/env python3
"""Teste vlp.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle les sous-commandes, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
`--seul <motif>` (ou `VLP_SEUL`) : ne joue que les groupes dont le nom ou le texte porte le motif (VIT10).
"""
import datetime
import glob
import hashlib
import importlib.util
import inspect
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
spec = importlib.util.spec_from_file_location("vlp_coeur", os.path.join(ICI, "vlp_coeur.py"))   # le code de vlp.py (VIT5)
assert spec and spec.loader
mod: Any = importlib.util.module_from_spec(spec)  # ses attributs, GIT compris, se lisent et se changent
spec.loader.exec_module(mod)

# Les tests rejouent des entrées identiques : le tampon de hook serait créé une fois,
# et les rejoues se tairaient. `TAMPON_HOOKS = None` : toujours vrai (FIL3, PYT1).
mod.TAMPON_HOOKS = None

# `ouvrir` et `cocher` notent CLAUDE_CODE_SESSION_ID : un test le fixe lui-même, jamais celui de la
# session qui lance la suite (chantier CAD).
os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
# Une fiche jouée la nuit lance la suite sous les variables de la nuit : `carte` imprimerait `NUIT=1` partout,
# `plan ecrire` refuserait, `VLP_CANAL` passerait au faux `claude`. Un test les fixe lui-même (NUI12, ENV1).
for _nom in mod.carnet.VARIABLES_NUIT:
    os.environ.pop(_nom, None)

# Le chantier ouvert se dit par sa marque, sous le titre du fichier de fiches du dossier `contexte` (NUI31).
CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"
OUVERT = "**Ouvert.** le 2026-10-08."
FICHES = """# Chantier Z

**Ouvert.** le 2026-10-08.

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


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


def rendu(depart):
    s = io.StringIO()
    mod.carte(depart, s)
    return s.getvalue()


ECARTS = []     # avec VLP_TOUS_ECARTS=1 (`vlp.py mutant`), un écart n'arrête pas la suite (chantier MUT)


CONTROLES = []  # les libellés des contrôles joués : leur nombre sous `--seul` (VIT10)


def verifier(nom, cond, sortie):
    """Contrôler `cond` : faux, imprimer l'écart et sortir 1 — ou le garder sous `VLP_TOUS_ECARTS=1`."""
    CONTROLES.append(nom)
    if not cond:
        print("ÉCART:", nom)
        print(sortie)
        if os.environ.get("VLP_TOUS_ECARTS") != "1":
            sys.exit(1)
        ECARTS.append(nom)


def motif_seul(argv, env):
    """Rendre le motif de `--seul <motif>`, sinon celui de `VLP_SEUL`, sinon "" (tout se joue) ; `--seul` sans motif :
    `None` (VIT10)."""
    if "--seul" in argv:
        i = argv.index("--seul")
        return argv[i + 1] if i + 1 < len(argv) and argv[i + 1] else None
    return env.get("VLP_SEUL", "")


def seul_demande():
    """Lire le motif de `--seul` pour cette suite ; `--seul` sans motif : sortir 2."""
    motif = motif_seul(sys.argv[1:], os.environ)
    if motif is None:
        print("GARDE: --seul sans motif")
        sys.exit(2)
    return motif


SEUL = seul_demande()
JOUES = []      # les groupes joués, sous `--seul` (VIT10)


def porte_motif(f, motif):
    """Dire si le nom ou le texte du groupe `f` (ses libellés) porte `motif`, sans tenir compte de la casse — son
    texte, et celui des fonctions du module qu'il nomme, sur un niveau : un libellé écrit dans `matin_t`, que
    `tester_matin` appelle, retient `tester_matin` (dette RTD)."""
    source = inspect.getsource(f)
    aides = [inspect.getsource(g) for nom, g in globals().items()
             if inspect.isfunction(g) and g is not f and re.search(r"\b%s\b" % re.escape(nom), source)]
    return motif.lower() in (f.__name__ + " " + source + "".join(aides)).lower()


def groupe(f):
    """Jouer le groupe de contrôles `f` — sous `--seul`, seulement s'il porte le motif (VIT10)."""
    if SEUL and not porte_motif(f, SEUL):
        return
    JOUES.append(f.__name__)
    f()


def lancer_boucle():
    """Lancer `test-boucle.py` sans l'attendre (VIT7) : rendre `(processus, stdout, stderr)`, ses deux sorties dans
    des fichiers temporaires — un tube plein bloquerait l'enfant. Un arrêt de la suite avant la récolte (un écart sans
    `VLP_TOUS_ECARTS`) le tue à la sortie (`arreter_boucle`, par `atexit`)."""
    import atexit
    sorties = [tempfile.TemporaryFile("w+", encoding="utf-8", errors="replace") for _ in range(2)]
    p = subprocess.Popen([sys.executable, os.path.join(ICI, "test-boucle.py")], stdout=sorties[0], stderr=sorties[1],
                         env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    atexit.register(arreter_boucle, p)
    return p, sorties[0], sorties[1]


def arreter_boucle(p):
    """Tuer `test-boucle.py` s'il tourne encore : son arbre sous Windows (`tuer_arbre`), lui seul ailleurs — il reste
    dans le groupe de la suite, que `vlp.py mutant` tue en entier."""
    if p.poll() is not None:
        return
    if sys.platform == "win32":
        mod.tuer_arbre(p)
    else:
        p.kill()
    p.wait()


def boucle_du_debut():
    """Lancer `test-boucle.py` dès le début, récolté par `tester_boucle` en fin de suite : ses ~180 s courent pendant
    le reste (VIT7). `VLP_BOUCLE_SERIE=1` ou `--seul` : rien lancé ici (`None`) ; `tester_boucle`, s'il se joue, le
    joue en série, comme avant."""
    return None if os.environ.get("VLP_BOUCLE_SERIE") == "1" or SEUL else lancer_boucle()


BOUCLE = boucle_du_debut()
# Le code que cette suite joue, pris au départ : une suite verte l'écrit à la fin, et `cocher` exige de le retrouver (VIT11).
EMPREINTE_DEPART = mod.empreinte_kit(mod.KIT)


def noter_si_verte():
    """Noter `EMPREINTE_DEPART` comme celle de la dernière suite entière verte — jamais sous `vlp.py mutant`
    (`VLP_TOUS_ECARTS=1`), qui joue une copie mutée (VIT11), ni sous `--seul`, qui n'en joue qu'une part (VIT10)."""
    if os.environ.get("VLP_TOUS_ECARTS") != "1" and not SEUL:
        mod.noter_suite_verte(mod.KIT, EMPREINTE_DEPART)


def tester_carte_projet():
    """Contrôler `carte` sur un projet : remontée au projet, chemin avec espace, titres numérotés, prochaine fiche."""
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "proj")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
        sous = os.path.join(p, "src", "a")
        os.makedirs(sous)
        ecrire(os.path.join(p, "src", "chantier.md"), "une commande, pas la carte\n")

        s = rendu(sous)
        verifier("remonte au projet", "PROJET=%s\n" % p in s, s)
        verifier("carte entière", "- **alias** : pz" in s, s)
        verifier("chemin avec espace et plage", "--- fiches : context AI/20-z.md (10 lignes, 3 titres) ---" in s, s)
        verifier("titres numérotés", "7:## Z1 [x] — faite\n9:## Z2 [ ] — à faire\n10:## Z10 [ ] — après\n" in s, s)
        verifier("prochaine dans l'ordre du fichier", s.endswith("PROCHAINE=Z2\n"), s)

        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES.replace("[ ]", "[x]"))
        s = rendu(p)
        verifier("tout coché", s.endswith("PROCHAINE=aucune\n"), s)

        ecrire(os.path.join(p, "context AI", "20-z.md"), "# Chantier Z\n\n%s\n### Z1 reformulé\n" % OUVERT)
        s = rendu(p)
        verifier("garde grep muet", "GARDE: aucun titre" in s and "PROCHAINE" not in s, s)

        # Sans marque, aucun chantier : l'ancienne ligne « fichier de fiches courant » ne nomme plus rien (NUI31).
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES.replace(OUVERT, "Fermé."))
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/") + "- **fichier de fiches courant** :"
               " context AI/20-z.md (Z1..Z10)\n")
        s = rendu(p)
        verifier("aucun courant", "--- fichier de fiches courant : aucun ---\n" in s and "TODO=absente (pas de ligne « chantiers possibles »)" in s, s)

        w = os.path.join(t, "ws")
        ecrire(os.path.join(w, "b", "CHANTIER.md"), CHANTIER % ("bb", "context AI/"))
        ecrire(os.path.join(w, "a", "CHANTIER.md"), CHANTIER % ("aa", "context AI/"))
        ecrire(os.path.join(w, "c", "chantier.md"), "une commande\n")
        s = rendu(w)
        verifier("voisins triés avec alias, et leur GIT=",
                 s == "VOISIN=%s alias=aa\nGIT=hors Git\nVOISIN=%s alias=bb\nGIT=hors Git\n"
                 % (os.path.join(w, "a"), os.path.join(w, "b")), s)

        vide = os.path.join(t, "vide")
        os.makedirs(vide)
        s = rendu(vide)
        verifier("aucun projet", s == "AUCUN_PROJET\n", s)


groupe(tester_carte_projet)


def tester_carte_git():
    """NUI35 : la ligne `GIT=` de la carte — tout suivi, un fichier ignoré, un fichier non ajouté, un dossier nommé
    par lui-même, hors Git ; jamais pour le relecteur."""
    def git(d, *args):
        subprocess.run(["git"] + list(args), cwd=d, capture_output=True, check=True)

    def lignes_git(d, relecteur=False):
        s = io.StringIO()
        mod.carte(d, s, relecteur)
        return [l for l in s.getvalue().split("\n") if l.startswith("GIT=")]

    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "p")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pg", "ctx/"))
        verifier("git : hors Git", lignes_git(p) == ["GIT=hors Git"], lignes_git(p))
        ecrire(os.path.join(p, "CLAUDE.md"), "# p\n")
        ecrire(os.path.join(p, "ctx", "08-etat.md"), "# état\n")
        ecrire(os.path.join(p, "ctx", "artefacts", "page.html"), "<p>\n")
        git(p, "init", "-q")
        verifier("git : dossier entier non ajouté",
                 lignes_git(p) == ["GIT=non ajouté CHANTIER.md, CLAUDE.md, ctx/"], lignes_git(p))
        git(p, "add", "-A")
        verifier("git : tout suivi", lignes_git(p) == ["GIT=suivi"], lignes_git(p))
        verifier("git : rien pour le relecteur", lignes_git(p, relecteur=True) == [], lignes_git(p, True))
        ecrire(os.path.join(p, "ctx", "09-neuf.md"), "# neuf\n")
        verifier("git : un fichier non ajouté", lignes_git(p) == ["GIT=non ajouté ctx/09-neuf.md"], lignes_git(p))
        git(p, "rm", "-q", "--cached", "CHANTIER.md")
        ecrire(os.path.join(p, ".gitignore"), "CHANTIER.md\n")
        verifier("git : un fichier ignoré, l'autre non ajouté",
                 lignes_git(p) == ["GIT=ignoré CHANTIER.md", "GIT=non ajouté ctx/09-neuf.md"], lignes_git(p))
        git(p, "rm", "-q", "--cached", "ctx/08-etat.md")
        ecrire(os.path.join(p, ".gitignore"), "CHANTIER.md\nctx/*\n!ctx/artefacts/\n__pycache__/\n")
        ecrire(os.path.join(p, "ctx", "__pycache__", "x.pyc"), "x")
        verifier("git : les fichiers directs d'un dossier en ctx/*, sans __pycache__",
                 lignes_git(p) == ["GIT=ignoré CHANTIER.md, ctx/*"], lignes_git(p))


groupe(tester_carte_git)


def tester_niveau_git():
    """NUI36 : l'étape `git` de `niveau` — ignoré avec sa ligne de `.gitignore`, non ajouté, ligne « kit » à chemin
    de machine, tout suivi sans écart, hors Git sans écart ; `--ecrire` ne corrige rien."""
    def git(d, *args):
        subprocess.run(["git"] + list(args), cwd=d, capture_output=True, check=True)

    def ecarts_git(d, ecrire=False):
        s = io.StringIO()
        mod.cmd_niveau(mod.argparse.Namespace(projet=d, date="2026-10-08", ecrire=ecrire), s)
        return [l for l in s.getvalue().split("\n") if l.startswith(("ÉCART: git:", "CORRIGÉ: git:"))]

    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "p")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pn", "ctx/") + "- **kit** : le plugin vlp\n")
        ecrire(os.path.join(p, "CLAUDE.md"), "# p\n")
        ecrire(os.path.join(p, "ctx", "08-etat.md"), "# état\n")
        ecrire(os.path.join(p, "ctx", "00-INDEX.md"), "# Index\n")
        verifier("niveau git : hors Git, aucun écart", ecarts_git(p) == [], ecarts_git(p))
        git(p, "init", "-q")
        git(p, "add", "-A")
        verifier("niveau git : tout suivi, aucun écart", ecarts_git(p) == [], ecarts_git(p))
        git(p, "rm", "-q", "--cached", "CHANTIER.md")
        ecrire(os.path.join(p, ".gitignore"), "# rien\nCHANTIER.md\n")
        ecrire(os.path.join(p, "ctx", "09-neuf.md"), "# neuf\n")
        e = ecarts_git(p)
        verifier("niveau git : ignoré par sa ligne, et non ajouté",
                 len(e) == 2 and e[0].startswith("ÉCART: git: CHANTIER.md — ignoré par .gitignore:2")
                 and e[1].startswith("ÉCART: git: ctx/09-neuf.md — non ajouté"), e)
        verifier("niveau git : --ecrire ne corrige rien", ecarts_git(p, ecrire=True) == e, ecarts_git(p, True))
        ecrire(os.path.join(p, ".gitignore"), "# rien\n")
        git(p, "add", "-A")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pn", "ctx/") + "- **kit** : D:/Projets/kit, lié dans"
               " ~/.claude/skills/vlp\n")
        e = ecarts_git(p)
        verifier("niveau git : la ligne « kit » à chemin de machine",
                 len(e) == 1 and "la ligne « kit » porte un chemin de machine" in e[0], e)


groupe(tester_niveau_git)


def test_carte_relecteur():
    """REL2 : `carte --relecteur` tait les titres de fiches et `PROCHAINE=` ; sans l'option, rien ne change."""
    with tempfile.TemporaryDirectory() as bac:
        pr = os.path.join(bac, "pr")
        ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/"))
        ecrire(os.path.join(pr, "context AI", "20-z.md"),
               ouvert("# Chantier ZZZ\n\n## ZZZ1 [ ] — à relire\n---\n## ZZZ2 [x] — piège\n"))
        s = rendu(pr)
        verifier("carte sans --relecteur : titres et PROCHAINE inchangés",
                 s.endswith("--- fiches : context AI/20-z.md (7 lignes, 2 titres) ---\n"
                            "5:## ZZZ1 [ ] — à relire\n7:## ZZZ2 [x] — piège\nPROCHAINE=ZZZ1\n"), s)
        r = io.StringIO()
        mod.carte(pr, r, relecteur=True)
        r = r.getvalue()
        verifier("carte --relecteur : ni titre ni PROCHAINE=, mais PROJET=",
                 "piège" not in r and "PROCHAINE=" not in r and "PROJET=%s\n" % pr in r, r)
        verifier("carte --relecteur : ni l'étendue des fiches (dette REL), mais le chemin",
                 "ZZZ2" not in r and "COURANT=context AI/20-z.md\n" in r, r)
        sans_git = "".join(l for l in s.splitlines(True) if not l.startswith("GIT="))   # NUI35 : pas pour le relecteur
        verifier("carte --relecteur : le reste à l'octet près, sans GIT=",
                 sans_git.startswith(r) and "- **alias** : pr" in r and "GIT=" in s and "GIT=" not in r, r)
        j = io.StringIO()
        mod.carte_injectee(pr, "py", False, j, relecteur=True)
        j = j.getvalue()
        verifier("carte --python --relecteur : l'option passe l'injection",
                 j.startswith("\nPYTHON=py\n") and "piège" not in j and "PROCHAINE=" not in j, j)


def test_carte_todo():
    """LEC2 : la TODO des chantiers possibles, quand aucun chantier n'est ouvert."""
    with tempfile.TemporaryDirectory() as t:
        pr = os.path.join(t, "pr")
        def chantier(possibles):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n"
                   "- **chantiers possibles** : %s\n- **contexte** : ctx/\n" % possibles)
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

        chantier("`a.md`")
        ecrire(os.path.join(pr, "ctx", "fiches.md"), "# Chantier Z\n\n%s\n\n## Z1 [ ] — Fiche\n" % OUVERT)
        s = rendu(pr)
        verifier("carte TODO : chantier ouvert, aucun bloc", "--- TODO :" not in s and "TODO=absente" not in s, s)


def test_carte_methode():
    """LEC3 : le format des fiches de la ligne **méthode**, quand aucun chantier n'est ouvert."""
    kit = mod.KIT
    with tempfile.TemporaryDirectory() as t:
        pr, faux_kit = os.path.join(t, "pr"), os.path.join(t, "kit")
        def chantier(methode):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n"
                   + ("- **méthode** : %s\n" % methode if methode else ""))
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

def tester_extraire_socle():
    """Contrôler `extraire`, `socle` et `carte` sur un fichier de fiches : marqueurs, CRLF, fichier absent (chantier U)."""
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
        r1 = appel(["carte", nulle, "--python", "py -3"])
        r2 = appel(["carte", nulle, "--python", "python3", "--relais"])
        r3 = appel(["carte", nulle, "--python", "py -3", "--relais"])
        r4 = appel(["carte", os.path.join(t, "ailleurs"), "--python", "python3", "--relais"])
        verifier("carte --python : ligne vide, PYTHON=, deux relais muets (U4), relais seul",
                 (r1, r2, r3, r4) == ((0, "\nPYTHON=py -3\nAUCUN_PROJET\n"), (0, ""), (0, ""), (0, "\nPYTHON=python3\nAUCUN_PROJET\n")), (r1, r2, r3, r4))


groupe(tester_extraire_socle)

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


def tester_valider():
    """Contrôler `valider` : un fichier sain, ses écarts, les avertissements de longueur et de socle."""
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


groupe(tester_valider)

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


def tester_arrondi():
    """Contrôler l'arrondi d'un compte de tokens."""
    verifier("arrondi", [mod.arrondi(n) for n in (999, 1000, 999949, 999950, 1505630)] == ["999", "≈1,0k (1 000)", "≈999,9k (999 949)", "≈1,0M (999 950)", "≈1,5M (1 505 630)"],
             [mod.arrondi(n) for n in (999, 1000, 999949, 999950, 1505630)])


groupe(tester_arrondi)

from decimal import Decimal

# Tout ce que ligne_cout écrit, triplet le relit : total sous et au-dessus de 1 000, prix chiffré, « ? », et négatifs.
def tester_triplet():
    """Contrôler que `triplet` relit ce que `ligne_cout` écrit, et le brut seul."""
    allers = [(t, tours, u) for t in (0, 7, 999, 1000, 999999, 1000000, 123456789, -5, -1500) for tours in (0, 1, 42) for u in (None, Decimal("0"), Decimal("1.83"), Decimal("-0.05"))]
    verifier("triplet relit ligne_cout", all(mod.triplet(mod.ligne_cout(*a)) == a for a in allers),
             [(a, mod.ligne_cout(*a), mod.triplet(mod.ligne_cout(*a)) == a) for a in allers if mod.triplet(mod.ligne_cout(*a)) != a])
    # Le brut entre parenthèses suffit, sans l'arrondi devant : une page d'un autre format se relit.
    verifier("triplet : le brut entre parenthèses suffit", mod.triplet("(5 284 442) · 42 tours · 1,83 $") == (5284442, 42, Decimal("1.83")),
             mod.triplet("(5 284 442) · 42 tours · 1,83 $"))


groupe(tester_triplet)

# total_clos : relire aussi les lignes closes sous 1 000, qui n'ont pas de parenthèses.
def ligne_close(c):
    """Une ligne close au format de cmd_clore, avec plage Q1–Q2, date 2026-05-06, et coût c."""
    return f'          <tr>\n            <td>Test <span class="badge" data-etat="clos">clos</span></td>\n            <td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>\n            <td class="mono">{c}</td>\n            <td>Test</td>\n          </tr>\n'

def tester_total_clos():
    """Contrôler `total_clos` et `couts` sur des lignes closes, dont un « ? $ » d'une ancienne page."""
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


groupe(tester_total_clos)

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

def tester_page_creer():
    """Contrôler `page --creer`, `page --verifier` et une page absente."""
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


groupe(tester_page_creer)

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

def tester_heures_commits():
    """Contrôler la découpe aux commits : `heures_commits`, puis `page`, `cout` et `recompter` coupés."""
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
                     h == ({"Q1": T0 + 300, "Q2": T0 + 600}, [T0 + 100, T0 + 300, T0 + 600, T0 + 800], [T0 + 900], []), h)
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
                     h == ({}, [T0 + 100, T0 + 1100], [T0 + 60, T0 + 1050], []), h)
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


groupe(tester_heures_commits)


def tester_commit_au_titre():
    """PRP4 : une fiche à deux commits `<id> :` va jusqu'à celui qui porte son titre — `NUI20`,
    coupée à son commit d'étape, perdait sa séance (2 tours au lieu de 35)."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le commit au titre n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        d, sq = os.path.join(t, "q"), os.path.join(t, "s.jsonl")
        transcript(sq, 6, [T0 + x for x in (50, 200, 250, 400, 700, 1000)])
        os.makedirs(os.path.join(t, "s", "subagents"))
        transcript(os.path.join(t, "s", "subagents", "agent-a1.jsonl"), 2, [T0 + 450, T0 + 460])
        ecrire(os.path.join(d, "q.md"), QFICHES % (sq, sq))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=d, env=env, check=True, capture_output=True)
        for x, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (350, "Q2 : l'avant, relevé"),
                         (380, "Autre : un chantier voisin au milieu"), (600, "Q2 : Brancher"),
                         (800, "Chantier Q clos : fini"), (950, "Q1 : correctif d'après")):
            date = "%d +0000" % (T0 + x)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=d, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        q = os.path.join(d, "q.md")
        h = mod.heures_commits(q, ["Q1", "Q2"], titres={"Q1": "Créer", "Q2": "Brancher"})
        verifier("PRP4 commit au titre : Q2 au sien, pas à l'étape ; Q1 pas étiré par son correctif",
                 h is not None and h[0] == {"Q1": T0 + 300, "Q2": T0 + 600}, h)
        h = mod.heures_commits(q, ["Q1", "Q2"])
        verifier("PRP4 commit au titre : sans titres, le plus ancien, comme avant",
                 h is not None and h[0] == {"Q1": T0 + 300, "Q2": T0 + 350}, h)
        code, s = appel(["cout", q])
        verifier("PRP4 commit au titre : cout donne à Q2 sa séance, sous-agent compris, total inchangé", code == 0
                 and "\nQ1 · ≈200,0k (200 000) · 2 tours · 1,00 $" in s
                 and "\nQ2 · ≈300,0k (300 000) · 3 tours · 1,50 $" in s
                 and "TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s, s)


groupe(tester_commit_au_titre)

# FIN1 : les bornes de `plages`, en fonction pure — heures (commits de fiche, qui nomment, autres).
def tester_plages():
    """Contrôler les bornes de `plages`, en fonction pure (chantier FIN)."""
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


groupe(tester_plages)


def tester_plages_preparation():
    """Contrôler qu'un commit `<PRÉFIXE> :` entre deux fiches coupe la suivante (chantier PRP)."""
    P2, G = [("Q1", "a", True, ["s"]), ("Q2", "b", True, ["s"])], []
    h = ({"Q1": 300, "Q2": 600}, [100, 300, 450, 600, 800], [30, 900], [450])
    r = mod.plages(P2, h, G)
    verifier("plages_preparation : la fiche 2 part du commit `<PRÉFIXE> :`, le morceau d'avant hors fiches",
             r == ([("Q1", (100, 300)), ("Q2", (450, 600))], [(30, 100), (300, 450), (600, 800)]) and not G, (r, G))
    longueur = lambda p: sum(b - a for _, (a, b) in p[0]) + sum(b - a for a, b in p[1])
    verifier("plages_preparation : le total ne bouge pas",
             longueur(r) == longueur(mod.plages(P2, h[:3], G)), (r, mod.plages(P2, h[:3], G)))


groupe(tester_plages_preparation)


# --- hook : le PostToolUse du plugin -----------------------------------------

def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


def tester_hook_fiches():
    """Contrôler le hook d'écriture sur un fichier de fiches : JSON illisible, .md ordinaire, fiches valides ou non."""
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


groupe(tester_hook_fiches)

def tester_etat():
    """Contrôler `etat` : dossier absent, puis le fichier d'état trouvé."""
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


groupe(tester_etat)

def tester_renvois():
    """Contrôler `renvois` : renvois présents ou absents, poids sous ou sur le seuil."""
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


groupe(tester_renvois)


def tester_renvois_garde():
    """TAB2 : une ligne d'index qui n'a pas le nombre de cellules de son en-tête arrête `renvois`."""
    with tempfile.TemporaryDirectory() as d:
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(d, "ctx", "01-a.md"), "a\n")
        tete = "| Fichier | a | b | c | d |\n|---|---|---|---|---|\n| `01-a.md` | x \\| y | b | c | d |\n"
        ecrire(os.path.join(d, "ctx", "00-INDEX.md"), tete)
        verifier("TAB2 : renvois, table saine et \\| gardé", appel(["renvois", d]) == (0, "POIDS CLAUDE.md absent/80 · CHANTIER.md 2/50 · index 3/80\n"
                 "RENVOIS 1 nommés · 0 absents\n"), appel(["renvois", d]))
        for ligne, n in (("| `01-a.md` | a | b | c |\n", 4), ("| `01-a.md` | a | b | c | d | e |\n", 6)):
            ecrire(os.path.join(d, "ctx", "00-INDEX.md"), tete + ligne)
            verifier("TAB2 : renvois, %d cellules au lieu de 5 → GARDE, sort 1" % n, appel(["renvois", d]) == (
                1, "GARDE: ctx/00-INDEX.md, ligne 4 : %d cellules au lieu de 5 — une barre verticale dans une "
                "cellule s'écrit \\|\n" % n), appel(["renvois", d]))


groupe(tester_renvois_garde)


def tester_barre_finale():
    """TAB2 : une ligne de table sans barre finale rend GARDE, au lieu de perdre sa dernière cellule."""
    with tempfile.TemporaryDirectory() as d:
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier |\n|---|\n")
        # (libellé, en-tête, lignes, numéro de la ligne fautive) ; le routage commence ligne 3
        cas = (("ligne", "| La tâche | Ouvrir |", "| a | `01-a.md` |\n| b | `02-b.md`", 6),
               ("en-tête", "| La tâche | Ouvrir", "| a | `01-a.md` | x\n| b | `02-b.md` | y |", 3))
        for libelle, tete, corps, n in cas:
            ecrire(os.path.join(d, "CLAUDE.md"), "## Routage\n\n%s\n|---|---|\n%s\n" % (tete, corps))
            verifier("TAB2 : une ligne sans barre finale rend GARDE, sort 1 (%s)" % libelle,
                     appel(["renvois", d]) == (1, "GARDE: CLAUDE.md, ligne %d : pas de barre finale — une ligne "
                                                  "de table se ferme par |\n" % n), appel(["renvois", d]))
    entete = ["| # | Chantier | Apporte | Coût | Dépend |", "|---|---|---|---|---|"]
    try:
        mod.todo_du_fichier(entete + ["| 1 | A | b | c | d"])
        dit = "aucune erreur"
    except ValueError as e:
        dit = str(e)
    verifier("TAB2 : une ligne sans barre finale lève, dans la TODO aussi",
             dit.startswith("ligne 1 de la TODO : pas de barre finale"), dit)


groupe(tester_barre_finale)


def tester_clore_todo():
    """TAB3 : `clore` lit la TODO avant sa première écriture — cassée, il n'écrit rien."""
    gabarit = lambda nom: open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()

    def empreinte(racine):
        return {os.path.join(r, f): hashlib.sha256(open(os.path.join(r, f), "rb").read()).hexdigest()
                for r, _, fs in os.walk(racine) for f in fs}

    for saine in (False, True):
        with tempfile.TemporaryDirectory() as te:
            ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : U (test).\n")
            rang = "| 3 | Trois | a | 2 fiches | — |" if saine else "| 3 | Trois | a | b | 2 fiches | — |"
            ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé "
                   "| Dépend de |\n|---|---|---|---|---|\n%s\n\n## Journal\n" % rang)
            ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(te, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
            ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
            avant = empreinte(te)
            code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-10-09"])
            if saine:
                verifier("TAB3 : clore sur une TODO saine passe", code == 0 and "CLOS U " in s, s)
            else:
                verifier("TAB3 : clore sur une TODO cassée rend GARDE, sort 1, rien écrit",
                         code == 1 and s.startswith("GARDE: ligne 3 de la TODO : 6 cellules au lieu de 5")
                         and "rien écrit" in s and empreinte(te) == avant, (code, s))


groupe(tester_clore_todo)


def tester_clore_ote_todo():
    """RTO1 : `clore` ôte la rangée du chantier de la TODO et marque la provenance, sans toucher au journal ;
    un code absent de la TODO n'écrit rien au fichier d'état, et ce n'est pas une GARDE."""
    gabarit = lambda nom: open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
    journal = "## Journal des décisions\n\n## 2026-10-01 — x\n"
    for present in (True, False):
        with tempfile.TemporaryDirectory() as tr:
            ecrire(os.path.join(tr, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : A (test).\n")
            rangs = ("| 3 | `U` — u | a | 2 fiches | — |\n" if present else "") + "| 4 | `AAA` — a | a | 1 | — |\n"
            etat = ("# État\n\nProvenance : 3, de x ; 4, de y.\n\n| # | Chantier | Ce qu'il apporte | Coût estimé "
                    "| Dépend de |\n|---|---|---|---|---|\n%s\n%s" % (rangs, journal))
            chemin = os.path.join(tr, "ctx", "08-etat.md")
            ecrire(chemin, etat)
            ecrire(os.path.join(tr, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(tr, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
            ecrire(os.path.join(tr, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
            code, s = appel(["clore", tr, "--livre", "fini", "--date", "2026-10-09"])
            lu = open(chemin, encoding="utf-8").read()
            if present:
                verifier("RTO1 : clore ôte la rangée U, garde l'autre, marque la provenance, journal inchangé",
                         code == 0 and "| 3 | `U`" not in lu and "| 4 | `AAA`" in lu
                         and "Provenance : 3, de x ; 4, de y. 3, `U`, clos le 2026-10-09.\n" in lu
                         and lu.endswith(journal) and "TODO `U` ôtée · n° 3\n" in s and "CLOS U " in s, (code, s, lu))
            else:
                verifier("RTO1 : clore sur un code absent de la TODO — rien ôté, fichier d'état inchangé, pas de GARDE",
                         code == 0 and "TODO `U` absente — rien ôté\n" in s and lu == etat and "CLOS U " in s, (code, s, lu))


groupe(tester_clore_ote_todo)


def tester_oter():
    """TAB4 : `vlp.py oter` retire une rangée de la TODO, marque son numéro, l'écrit au journal ; refuse un code
    absent, ouvert ou clos sans rien écrire."""
    etat = ("# État\n\n## La TODO\n\nProvenance : 3, de x ; 4, de y.\n\n"
            "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
            "| 3 | `AAA` — a | x | 1 | — |\n| 4 | `BBB` — b | x | 1 | — |\n| 5 | `U` — u | x | 1 | — |\n"
            "| 6 | `OUV` — o | x | 1 | — |\n\n## Journal des décisions\n\n## 2026-10-01 — x\n")
    with tempfile.TemporaryDirectory() as to:
        ecrire(os.path.join(to, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n\n"
               "Lettres de fiche déjà prises : U (test). Un nouveau chantier en choisit un autre.\n")
        ecrire(os.path.join(to, "ctx", "50-ouv.md"), ouvert("# Chantier OUV — o\n\n## OUV1 [ ] — a\n"))
        chemin = os.path.join(to, "ctx", "08-etat.md")
        ecrire(chemin, etat)
        for code, quoi in (("ZZZ", "absent"), ("OUV", "ouvert"), ("U", "clos")):
            res = appel(["oter", to, code, "--raison", "r", "--date", "2026-10-09"])
            verifier("TAB4 : oter refuse un code %s — GARDE, sort 1, fichier inchangé" % quoi,
                     res[0] == 1 and res[1].startswith("GARDE: ") and "rien écrit" in res[1]
                     and open(chemin, encoding="utf-8").read() == etat, res)
        res = appel(["oter", to, "AAA", "--raison", "fait ailleurs", "--date", "2026-10-09"])
        lu = open(chemin, encoding="utf-8").read()
        verifier("TAB4 : oter ôte la rangée, et elle seule", res[0] == 0 and "| 3 | `AAA`" not in lu
                 and "| 4 | `BBB`" in lu and len(mod.todo_du_fichier(lu.split("\n"))) == 3, (res, lu))
        verifier("TAB4 : oter marque le numéro retiré dans la phrase de provenance",
                 "Provenance : 3, de x ; 4, de y. 3, `AAA`, retiré le 2026-10-09 : fait ailleurs.\n" in lu, lu)
        verifier("TAB4 : oter écrit une entrée datée au journal",
                 lu.endswith("## 2026-10-01 — x\n\n## 2026-10-09 — `AAA` retiré de la TODO (n° 3)\n\n"
                             "- **Raison** : fait ailleurs.\n"), lu)


groupe(tester_oter)

# REP1 : le gras et les liens Markdown d'une cellule — jamais dans du code cité.
def tester_gras_et_liens():
    """Contrôler `gras_et_liens` et `cellule` : le gras et les liens Markdown d'une cellule (chantier REP)."""
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


groupe(tester_gras_et_liens)

def tester_bilan_md_clore(page_q):
    """Dans une fonction : au niveau du module, pyright jugeait le fichier trop complexe (ABR3)."""
    bilan_md = mod.lire_abri(mod.chemin_abri(page_q))["bilan"]
    verifier("clore : bilan écrit dans le .md, estimé résolu — mutant : écrire avant de remplacer ESTIME_A_ECRIRE",
             bilan_md == ["Livré : Livré `a` <b>", "Surpris : x < y",
                          "Estimé : estimé 2 fiches ≈0,40 $ · cadré 2 · joué 1 fiches ? $"]
             and "\x00" not in "\n".join(bilan_md), bilan_md)


def tester_feuille_clore():
    """Contrôler `feuille` et `clore` : feuille fermée, réécrite, résumé (chantier FEU)."""
    with tempfile.TemporaryDirectory() as t:
        carte_ = ("# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
                  "- **artefact du chantier** : %s\n\n"
                  "Lettres de fiche déjà prises : E (Un), M (Deux `x`). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "aucun")
        ecrire(os.path.join(t, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Le `sh` | a \\|\\| b <c> | 2 fiches | — |\n| 4 | Quatre | rien | 1 fiche | 3 |\n\n## Journal\n")
        q_ferme = "# Chantier Q — Un titre\n\n## Q1 [x] — a\n## Q2 [ ] — b\n"
        ecrire(os.path.join(t, "ctx", "30-q.md"), q_ferme)
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
        ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "https://exemple/q")
        ecrire(os.path.join(t, "ctx", "30-q.md"), ouvert(q_ferme))
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
        ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "aucun")
        ecrire(os.path.join(t, "ctx", "30-q.md"), q_ferme)
        code, s = appel(["feuille", t])
        html = lire(fdr)
        verifier("feuille : refermé, badge ôté", code == 0 and "Aucun chantier ouvert" in html
                 and 'data-etat="cours"' not in html.split("ZONE:encours")[1] and "E, M</span>" in html, s)

        ecrire(os.path.join(t, "CHANTIER.md"), carte_ % "https://exemple/q"
               + "\n| Fichier de fiches | Fiches | Clos le | Artefact |\n|---|---|---|---|\n| ctx/10-e.md | E1..E2 | 2026-01-01 | u |\n\nFin.\n")
        ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un `titre`\n\n" + OUVERT + "\n\n**À quoi il sert.** x\n\n**Estimé.** 2 fiches · ≈0,40 $ — ≈0,20 $/fiche sur 3 clos (le 2026-05-01).\n\n**Fait.** Rien.\n\n## Q1 [x] — a\n## Q2 [ ] — b\n")
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
        verifier("clore : CHANTIER.md", "**artefact du chantier** : aucun" in carte_lue
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


groupe(tester_feuille_clore)

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


groupe(test_archiver)


def sans_chantier(racine, carte):
    """Plus aucun chantier ouvert dans `racine` : CHANTIER.md réécrit avec `carte`, et la marque d'ouverture que
    `ouvrir` a posée retirée des fiches — la ligne seule à « aucun » ne ferme plus rien (NUI23)."""
    ecrire(os.path.join(racine, "CHANTIER.md"), carte)
    ctx = os.path.join(racine, "ctx")
    for nom in os.listdir(ctx):
        chemin = os.path.join(ctx, nom)
        if nom.endswith(".md") and os.path.isfile(chemin):
            texte = mod.lire(chemin)
            ecrire(chemin, re.sub(r"\n\n\*\*Ouvert\.\*\* le [^\n]*", "", texte))


OUVERT_DU_JOUR = mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat()

def tester_ouvrir():
    """Contrôler `ouvrir` : bilan, fichier de fiches posé, ligne de l'état."""
    with tempfile.TemporaryDirectory() as t:
        lire = lambda c: open(c, encoding="utf-8").read()
        os.environ["CLAUDE_CODE_SESSION_ID"] = "cadre"     # la session du cadrage, que `ouvrir` note
        carte_o = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **artefact du chantier** : %s\n")
        ecrire(os.path.join(t, "CHANTIER.md"), carte_o % "aucun")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n| `05-d.md` | vieux |\n\nFin.\n")
        ecrire(os.path.join(t, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n| relire le chantier E (e) | `ctx/10-e.md` — chantier **clos** |\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
        ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        carte_lue, index_lu, claude_lu = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "00-INDEX.md")), lire(os.path.join(t, "CLAUDE.md"))
        verifier("ouvrir : bilan", code == 0 and s == "OUVERT Q Q1..Q2 · index +1 · routage +1 · session +1 · artefact aucun — %s\n" % t, s)
        verifier("ouvrir : la session du cadrage, avant la première ligne ##", lire(os.path.join(t, "ctx", "30-q.md"))
                 == "# Chantier Q — Un titre\n\n%s\n\n**Session** : cadre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n"
                 % (mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat()), lire(os.path.join(t, "ctx", "30-q.md")))
        verifier("ouvrir : CHANTIER.md, l'artefact seul — plus de ligne du fichier courant (NUI31)",
                 "fichier de fiches" not in carte_lue and "- **artefact du chantier** : aucun\n" in carte_lue
                 and mod.courant_de(t) == "ctx/30-q.md", carte_lue)
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
                 and mod.courant_de(t) == "ctx/30-q.md", s + repr(index_q))
        index_main = lire(os.path.join(t, "ctx", "00-INDEX.md")).replace("chantier **ouvert** « Un `titre` », `Q1..Q3`", "à la main `Q1..Q2`")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), index_main)
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        verifier("ouvrir : relancé, une ligne d'index écrite à la main reste", code == 0 and "index +0" in s
                 and lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_main, s)
        sans_chantier(t, carte_o % "aucun")
        os.remove(os.path.join(t, "CLAUDE.md"))
        code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
        verifier("ouvrir : CLAUDE.md absent, garde, le reste écrit", code == 0 and "GARDE: CLAUDE.md introuvable" in s
                 and "routage +0" in s and "index +1" in s and mod.courant_de(t) == "ctx/31-r.md", s)
        sans_chantier(t, carte_o % "aucun")
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
        sans_chantier(t, carte_o % "aucun")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/33-t.md", "--titre", "t"])
        lu_o = lire(os.path.join(t, "ctx", "33-t.md"))
        verifier("ouvrir : un vrai fichier, la session avant le socle, hors de toute fiche", code == 0 and "· session +1 ·" in s
                 and lu_o == vrai.replace("## Le socle commun", "**Session** : cadre\n\n## Le socle commun")
                                 .replace("# Chantier T — t\n\n", "# Chantier T — t\n\n%s\n\n" % OUVERT_DU_JOUR)
                 and "**Session**" not in appel(["extraire", os.path.join(t, "ctx", "33-t.md"), "T1"])[1], s + lu_o)
        sans_chantier(t, carte_o % "aucun")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/34-u.md", "--titre", "u"])
        verifier("ouvrir : session déjà sur une ligne d'une fiche, pas redoublée", code == 0 and "· session +0 ·" in s
                 and lire(os.path.join(t, "ctx", "34-u.md")).count("**Session**") == 1, s)
        sans_chantier(t, carte_o % "aucun")
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        code, s = appel(["ouvrir", t, "--fiches", "ctx/35-v.md", "--titre", "v"])
        verifier("ouvrir : id vide, rien de noté", code == 0 and "· session +0 ·" in s
                 and lire(os.path.join(t, "ctx", "35-v.md")) == "# Chantier V — v\n\n%s\n\n## V1 [ ] — a\n" % OUVERT_DU_JOUR, s)
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)


groupe(tester_ouvrir)

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
                   "- **artefact du chantier** : aucun\n")
        fiches_e = "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n"
        ecrire(os.path.join(te, "CHANTIER.md"), carte_e)
        ecrire(os.path.join(te, "ctx", "30-q.md"), fiches_e)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        verifier("EST1 : sans feuille, GARDE, le reste écrit", code == 0 and "GARDE: feuille de route introuvable" in s
                 and "estimé" not in s.split("\n")[-2] and "**Estimé.**" not in lire(os.path.join(te, "ctx", "30-q.md"))
                 and mod.courant_de(te) == "ctx/30-q.md", s)
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
        sans_chantier(te, carte_e)
        ecrire(os.path.join(te, "ctx", "31-r.md"), "# Chantier R — r\n\n**Fait.** Rien.\n\n## R1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("E1–E8", "non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/31-r.md", "--titre", "r", "--estime-fiches", "1"])
        verifier("EST1 : aucun clos mesuré, GARDE, le reste écrit", code == 0 and "GARDE: aucun chantier clos mesuré" in s
                 and mod.courant_de(te) == "ctx/31-r.md", s)
        # TAU2 : des clos mesurés en tokens, mais aucun au prix `$` — GARDE dédiée, pas d'estimé en $.
        sans_chantier(te, carte_e)
        ecrire(os.path.join(te, "ctx", "32-s.md"), "# Chantier S — s\n\n**Fait.** Rien.\n\n## S1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("D1–D2", "≈2,0M (2 000 000)") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/32-s.md", "--titre", "s", "--estime-fiches", "1"])
        verifier("TAU2 : mesuré en tokens, aucun au prix $ — GARDE dédiée, le reste écrit", code == 0
                 and "GARDE: aucun chantier clos au prix mesuré sur la feuille de route — pas d'estimé" in s
                 and "**Estimé.**" not in lire(os.path.join(te, "ctx", "32-s.md"))
                 and mod.courant_de(te) == "ctx/32-s.md", s)
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
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n## U2 [x] — b\n"))
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
                   "- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : U (test).\n")
            ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
                   "|---|---|---|---|---|\n| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
            ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Estimé.** 3 fiches · ≈9,00 $ — ≈3,00 $/fiche sur 2 clos (le 2026-09-01).\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
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


groupe(test_estime)


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


groupe(tester_prix)


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


groupe(tester_cout_session)


# --- chantier ESS : les essais d'une session, par le dossier de leur bac -------

def tester_essais_de():
    """Contrôler `essais_de` : les bacs d'un projet, triés."""
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
        # MET2 : un essai hors bac (une copie du kit) se déclare au registre, par `vlp.py essai`.
        for copie in ("D--x-vlp-essai-v1", "D--x-vlp-essai-v2", "D--x-vlp-autre-w1"):
            ecrire(os.path.join(pr, copie, "e.jsonl"), "{}\n")
        o, refus = io.StringIO(), io.StringIO()
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            codes = (mod.main(["essai", "D--x-vlp-essai-*", "--session", "aaaa-1"], o),
                     mod.main(["essai", "D--x-vlp-essai-*", "--session", "aaaa-1"], o),
                     mod.main(["essai", "D--x-vlp-autre-w1", "--session", "bbbb-2"], o),
                     mod.main(["essai", "../x", "--session", "aaaa-1"], refus))
            a2, b2 = mod.essais_de("aaaa-1"), mod.essais_de("bbbb-2")
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        with open(os.path.join(t, ".claude", "vlp-essais.txt"), encoding="utf-8") as f:
            registre = f.read().splitlines()
        verifier("essai : un essai hors bac déclaré pour A est à A, pas à B",
                 codes == (0, 0, 0, 1)
                 and a2 == sorted(a + [os.path.join(pr, "D--x-vlp-essai-v1", "e.jsonl"),
                                       os.path.join(pr, "D--x-vlp-essai-v2", "e.jsonl")])
                 and b2 == sorted(b + [os.path.join(pr, "D--x-vlp-autre-w1", "e.jsonl")])
                 and "ESSAI aaaa-1 D--x-vlp-essai-* · 2 dossier(s) · 2 transcript(s)" in o.getvalue(),
                 (codes, a2, b2, o.getvalue()))
        verifier("essai : déclaré une fois, un motif qui sort du dossier refusé",
                 registre == ["aaaa-1 D--x-vlp-essai-*", "bbbb-2 D--x-vlp-autre-w1"]
                 and refus.getvalue().startswith("GARDE: essai non déclaré"), (registre, refus.getvalue()))


groupe(tester_essais_de)

# cout : un essai dans la plage de Q1 (et son sous-agent) compte à Q1, l'autre hors fiches.
def tester_cout_essai_plage():
    """Contrôler `cout` : un essai dans la plage d'une fiche compte, sous-agent compris."""
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


groupe(tester_cout_essai_plage)

# APC1 : cout --a-clore. Q1 (200), Q2 (400), l'appel clore (700), un tour après lui (800), le commit
# de clôture (900), un clore rejoué après lui (1000), hors plage : à clore = 3 tours, après = 1.
def tester_cout_a_clore():
    """Contrôler `cout --a-clore` et `recompter --a-clore` (chantier APC)."""
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


groupe(tester_cout_a_clore)

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
               "- **artefact du chantier** : https://u\n\n"
               "Lettres de fiche déjà prises : Q (test).\n")
        ecrire(os.path.join(proj, "ctx", "q.md"), ouvert(QFICHES % (s3, s3)))
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


groupe(tester_apc3)

# ESD1 : sans découpe (pas de .git), les essais des sessions entières en une ligne à part, sous
# les tables ; une session sans essai n'en a pas.
def tester_cout_sans_decoupe():
    """Contrôler `cout` sans découpe : la ligne des essais, avec et sans essai (chantier ESD)."""
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


groupe(tester_cout_sans_decoupe)

# ESD2 : recompter --essais, sur un projet sans .git — M (session sss, 1 essai + son sous-agent) est
# gardé DÉCOUPE aucune et reçoit ses essais ; N (session ttt, sans essai) ne change pas. Un second
# passage ne change plus rien : la marque est lue avant l'ajout, à l'affichage comme à l'écriture.
def tester_recompter_essais():
    """Contrôler `recompter --essais`, avec et sans `--ecrire` (chantier ESD)."""
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


groupe(tester_recompter_essais)


def tester_recompter_un_clos():
    """`recompter --clos A --ecrire` (PRP3) : les quatre copies du coût de A écrites, B intact —
    `recompte` simulé (90 000 tokens, 7,50 $), la découpe a ses propres tests."""
    from decimal import Decimal
    with tempfile.TemporaryDirectory() as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `a.md` | chantier **clos** « A », `A1..A1` |\n| `b.md` | chantier **clos** « B », `B1..B1` |\n")
        joue = "estimé 1 fiches ≈25 $ · cadré 1 · joué 1 fiches 12,34 $"
        for x in ("A", "B"):
            ecrire(os.path.join(tp, "ctx", x.lower() + ".md"),
                   "# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n**Fait.** %s1..%s1 (2026-01-06) : fini — %s.\n\n"
                   "## Le socle commun\n\n<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n"
                   % (x, x, x, joue, x, x))
            ecrire(os.path.join(tp, "ctx", "artefacts", x.lower() + ".html"),
                   '<p class="mono cout-total">Coût : 12,34 $</p>\n  <!-- ZONE:bilan -->\n  <section>\n'
                   '    <div class="bilan">\n      <p>Estimé : %s</p>\n    </div>\n  </section>\n' % joue)
            ecrire(os.path.join(tp, "ctx", "artefacts", x.lower() + ".md"),
                   "# %s — notes et journal\n## Résultat\nFini\n## Notes\n## Journal\n## Bilan\n- Estimé : %s\n" % (x, joue))
        fdr = os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
               + "".join(ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", pl) for pl in ("A1", "B1"))
               + "        </tbody>\n      </table>\n")
        b = [os.path.join(tp, "ctx", n) for n in ("b.md", os.path.join("artefacts", "b.html"), os.path.join("artefacts", "b.md"))]
        avant_b = [lire(c) for c in b]
        vrai = mod.recompte
        mod.recompte = lambda chemin: (90000, "découpe", 0, Decimal("7.50"))
        try:
            absent = appel(["recompter", tp, "--clos", "Z", "--ecrire"])
            initiale = lire(fdr)
            un = appel(["recompter", tp, "--clos", "A", "--ecrire"])
            copies_a = [lire(os.path.join(tp, "ctx", n)) for n in
                        ("a.md", os.path.join("artefacts", "a.html"), os.path.join("artefacts", "a.md"))]
            feuille_ = lire(fdr)
            deux = appel(["recompter", tp, "--clos", "A", "--ecrire"])
        finally:
            mod.recompte = vrai
        verifier("PRP3 : --clos absent de ZONE:clos, une GARDE, rien d'écrit",
                 absent[0] == 1 and absent[1].startswith("GARDE: clos Z absent")
                 and initiale.count("12,34 $ · %s" % mod.arrondi(50000)) == 2, absent[1])
        neuf = "joué 1 fiches 7,50 $"
        verifier("PRP3 : recompter --clos A --ecrire — 4 copies écrites pour A (archive, **Fait.**, ZONE:bilan, abri)"
                 " — mutant : sauter l'écriture de la ZONE:bilan",
                 un[0] == 0 and un[1].splitlines()[-1] == "COPIES 4 écrites · 0 inchangées · 0 introuvables"
                 and un[1].splitlines()[0].startswith("A inscrit 50 000 · recompté 90 000")
                 and '<td class="mono">7,50 $ · recompté (REC), était 50 000 · %s</td>' % mod.arrondi(90000) in feuille_
                 and all(neuf in c for c in copies_a), un[1] + "\n".join(copies_a) + feuille_)
        verifier("PRP3 : B n'a pas bougé — 0 copie changée (fiches, page, abri, cellule d'archive)",
                 [lire(c) for c in b] == avant_b
                 and '<td class="mono">B1</td>' in feuille_
                 and feuille_.count('<td class="mono">12,34 $ · %s</td>' % mod.arrondi(50000)) == 1, feuille_)
        verifier("PRP3 : relancé, les quatre copies inchangées",
                 deux[0] == 0 and deux[1].splitlines()[-1] == "COPIES 0 écrites · 4 inchangées · 0 introuvables"
                 and lire(fdr) == feuille_, deux[1])


groupe(tester_recompter_un_clos)

# --- chantier U : lire, cocher, page déduite ----------------------------------

def tester_lire_kit():
    """Contrôler `lire` : un fichier du kit tel quel, hors du kit et absent."""
    attendu = mod.lire(os.path.join(mod.KIT, "cloture.md"))
    attendu = attendu if attendu.endswith("\n") else attendu + "\n"
    verifier("lire : un fichier du kit, tel quel", appel(["lire", "cloture.md"]) == (0, attendu), appel(["lire", "cloture.md"])[1][:200])
    code, s = appel(["lire", "cloture.md", "../hors.md", "absent.md", "cloture.md"])
    verifier("lire : hors du kit et absent sortent 1, le reste imprimé", code == 1
             and s == attendu + "GARDE: hors du kit : ../hors.md\nABSENT absent.md\n" + attendu, s[-200:])


groupe(tester_lire_kit)

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


def tester_cocher():
    """Contrôler `cocher` : la coche, les Tentatives réduites, la Session ; `page` sans chemin."""
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


groupe(tester_cocher)

# cocher --verifier et --refuser (chantier REV) : la tête du dépôt, puis le refus du relecteur.
def tester_cocher_refuser():
    """Contrôler `cocher --verifier` et `cocher --refuser` (chantier REV)."""
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


groupe(tester_cocher_refuser)

# --- Z2 : un chemin de CHANTIER.md ne fait plus tomber une sous-commande ---
# Un cas par ligne « plante » de la table de Z1, plus le point de lecture unique.
GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")
ETAT_Z = ("# État\n\n## TODO\n\n| n° | Chantier | Apport | Coût | Décidé |\n|---|---|---|---|---|\n"
          "| 1 | un truc | utile | bas | 2026-01-02 |\n")
CARTE_Z = ("# Chantier courant\n\n- **alias** : z\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n")

def tester_z2_chemin():
    """Contrôler qu'un chemin de CHANTIER.md ne fait plus tomber une commande (Z2)."""
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z)
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        os.makedirs(os.path.join(proj, "ctx", "artefacts"))
        shutil.copy(GABARIT_FEUILLE, os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"))
        manque = "GARDE: fichier de fiches introuvable : ctx/absent.md\n"

        # Un fichier courant absent ne se nomme plus : seule la marque ouvre, sur un fichier qui existe (NUI31).
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


groupe(tester_z2_chemin)


# ARC1 : l'archive des clos, quand elle existe, reçoit et donne les lignes closes ; la feuille garde le graphique
def test_page_clos():
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z
               + "\nLettres de fiche déjà prises : A (Arc). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `x.md` | chantier **clos** « X », `X1..X1` |\n| `y.md` | chantier **clos** « Y », `Y1..Y1` |\n"
               "| `30-a.md` | chantier **ouvert** « A », `A1..A1` |\n")
        ecrire(os.path.join(proj, "ctx", "30-a.md"), "# Chantier A\n\n" + OUVERT + "\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
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


groupe(test_page_clos)


def test_archive():
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z
               + "\nLettres de fiche déjà prises : A (Arc). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `30-a.md` | chantier **ouvert** « A », `A1..A1` |\n")
        ecrire(os.path.join(proj, "ctx", "30-a.md"), "# Chantier A\n\n" + OUVERT + "\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
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


groupe(test_archive)


# Préfixe à trois lettres : le format officiel depuis le chantier RNV.
def tester_trois_lettres():
    """Contrôler le préfixe à trois lettres : titres lus par la carte, lettres prises."""
    CHANTIER_3 = """# Chantier courant

- **alias** : p3
- **contexte** : ctx

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
        ecrire(fiches3, ouvert(FICHES_3))

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


groupe(tester_trois_lettres)

# NIV1 — la ligne d'injection ne laisse entrer aucun message de lanceur dans la carte.
RACINE = os.path.dirname(ICI)
def tester_niv1_injection():
    """Contrôler la ligne d'injection de chaque skill (NIV1, EVF4)."""
    lignes_injection = []
    for skill in ("chantier", "tache", "chef"):
        texte = io.open(os.path.join(RACINE, "skills", skill, "SKILL.md"), encoding="utf-8").read()
        lignes_injection.append([l for l in texte.splitlines() if l.startswith("!`") and "vlp.py" in l])

    sans_option = [[l.replace(" --session-neuve", "") for l in x] for x in lignes_injection]
    verifier("NIV1 : une ligne d'injection par skill, les trois identiques (au --session-neuve de tache près, VIT20)",
             [len(x) for x in lignes_injection] == [1, 1, 1]
             and sans_option[0] == sans_option[1] == sans_option[2],
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

    # VIT24 : `py` seul relit le `#!` de vlp.py et relance un python3 (+54 ms) ; le relais python3 ne change pas.
    textes = [io.open(c, encoding="utf-8").read() for c in skills_glob]
    py3 = sum(t.count('py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python "py -3"') for t in textes)
    nus = sum(t.count('py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte') for t in textes)
    relais = sum(t.count('python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais') for t in textes)
    verifier("VIT24 : chaque injection lance la carte par py -3 et dit PYTHON=py -3 (deux appels sur trois), aucun py "
             "nu ; le relais python3 reste", py3 == 2 * len(skills_glob) and nus == 0 and relais == len(skills_glob),
             (py3, nus, relais, len(skills_glob)))

    s_niv1 = io.StringIO()
    mod.carte_injectee(os.path.join(RACINE, "scripts"), "py -3", False, s_niv1)
    lu_n = s_niv1.getvalue()
    # L'en-tête seul : la carte recopie ensuite CHANTIER.md et, sans chantier courant, la TODO du kit, dont une
    # ligne (n° 101, EXE) cite « claude.exe introuvable » — une donnée du projet, pas un message de lanceur.
    entete_n = lu_n.split("\n--- ")[0]
    verifier("NIV1 : la carte ne dit que PYTHON= et le projet",
             lu_n.splitlines()[:2] == ["", "PYTHON=py -3"] and "introuvable" not in entete_n
             and "not found" not in entete_n and "PROJET=" in entete_n, entete_n[:200])


groupe(tester_niv1_injection)


# VIT20 — une fiche, une session neuve : la carte de /vlp:tache avertit d'une session déjà notée.
FICHES_VIT20 = ("# Chantier ZZZ\n\n**Ouvert.** le 2026-10-08.\n\n**Session** : cadre-1\n\n## Le socle commun\n\n"
                "## ZZZ1 [x] — faite\n**Session** : joue-1\n**Session** : nuit-1 (relecture)\n**Dépend de** : rien.\n---\n"
                "## ZZZ2 [x] — aussi\n**Session** : joue-1\n---\n## ZZZ3 [ ] — à faire\n")
AVERTI_VIT20 = ("AVERTISSEMENT: session déjà notée dans ce fichier de fiches (%s) — /clear d'abord : une fiche, "
                "une session neuve\n")


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


def tester_vit20_session_neuve():
    """Contrôler `carte --session-neuve` : l'avertissement d'une session déjà notée, et rien d'autre (VIT20)."""
    with tempfile.TemporaryDirectory() as bac:
        pr = os.path.join(bac, "pr")
        ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/"))
        ecrire(os.path.join(pr, "context AI", "20-z.md"), FICHES_VIT20)
        avant = carte_sous(pr)
        verifier("VIT20 : la carte d'avant, sans id ni option, finit sur PROCHAINE=", avant.endswith("PROCHAINE=ZZZ3\n"), avant)
        s = carte_sous(pr, "joue-1", neuve=True)
        verifier("VIT20 : id sur deux fiches cochées → la carte d'avant, puis AVERTISSEMENT: qui les nomme",
                 s == avant + AVERTI_VIT20 % "ZZZ1, ZZZ2", s)
        s = carte_sous(pr, "cadre-1", neuve=True)
        verifier("VIT20 : id sur la ligne du cadrage → AVERTISSEMENT: qui le nomme", s == avant + AVERTI_VIT20 % "cadrage", s)
        s = carte_sous(pr, "nuit-1", neuve=True)
        verifier("VIT20 : id d'une ligne à rôle « (relecture) » → l'id seul compte", s == avant + AVERTI_VIT20 % "ZZZ1", s)
        for sid in (None, "", "   ", "inconnue"):
            s = carte_sous(pr, sid, neuve=True)
            verifier("VIT20 : id %r → la carte d'avant, au caractère près" % (sid,), s == avant, s)
        s = carte_sous(pr, "joue-1")
        verifier("VIT20 : sans --session-neuve (/vlp:jouer, /vlp:enchainer, /vlp:chantier) → la carte d'avant", s == avant, s)
        s = carte_sous(pr, "cadre-1", nuit=True, neuve=True)
        verifier("VIT20 : VLP_NUIT=1 (la nuit note l'id de clore avant sa session) → la carte de nuit d'avant",
                 s == carte_sous(pr, nuit=True) and "NUIT=1\n" in s, s)
        injection = [["carte", pr, "--python", "py -3", "--session-neuve"],
                     ["carte", pr, "--python", "python3", "--relais", "--session-neuve"]]
        s = carte_sous(pr, "joue-1", argv=injection)
        verifier("VIT20 : l'injection par main → PYTHON=py -3, la carte, l'AVERTISSEMENT: une fois ; le relais se tait",
                 s == "\nPYTHON=py -3\n" + avant + AVERTI_VIT20 % "ZZZ1, ZZZ2", s)

    porteurs = sorted(os.path.basename(os.path.dirname(c)) for c in glob.glob(os.path.join(RACINE, "skills", "*", "SKILL.md"))
                      if "--session-neuve" in io.open(c, encoding="utf-8").read())
    tache = io.open(os.path.join(RACINE, "skills", "tache", "SKILL.md"), encoding="utf-8").read()
    ligne = next((l for l in tache.splitlines() if l.startswith("!`") and "vlp.py" in l), "")
    verifier("VIT20 : --session-neuve sur les trois appels de l'injection de /vlp:tache, dans aucune autre skill",
             porteurs == ["tache"] and ligne.count("--session-neuve") == 3, (porteurs, ligne))


groupe(tester_vit20_session_neuve)


def tester_arp3_marque():
    """Contrôler `carte --enchaine` : la marque de la session fait taire l'AVERTISSEMENT: de VIT20, celle d'une autre
    session non (ARP3). Chaque cas dans son propre dossier temporaire, qui sert aussi de `tempfile.tempdir`."""
    enchainer = [["--python", "py -3", "--enchaine"], ["--python", "python3", "--relais", "--enchaine"],
                 ["--python", "py -3", "--relais", "--enchaine"]]

    def cas(session_marque, session_tache, appels):
        """Le projet de VIT20 dans un dossier neuf : `appels` (options de `carte`, l'injection d'enchainer) sous
        `session_marque`, puis la carte de /vlp:tache sous `session_tache`. Rendre (sa sortie, les marques posées)."""
        ancien = tempfile.tempdir
        with tempfile.TemporaryDirectory() as bac:
            pr = os.path.join(bac, "pr")
            ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/"))
            ecrire(os.path.join(pr, "context AI", "20-z.md"), FICHES_VIT20)
            tempfile.tempdir = bac
            try:
                carte_sous(pr, session_marque, argv=[["carte", pr] + x for x in appels])
                s = carte_sous(pr, session_tache, argv=[["carte", pr, "--python", "py -3", "--session-neuve"]])
                marques = sorted(os.path.basename(m) for m in glob.glob(os.path.join(bac, "vlp-enchaine-*")))
            finally:
                tempfile.tempdir = ancien
        return s, marques

    s, marques = cas("joue-1", "joue-1", enchainer)
    verifier("ARP3 : l'injection d'enchainer pose la marque de sa session, la carte de tache s'y tait",
             marques == ["vlp-enchaine-joue-1"] and "AVERTISSEMENT:" not in s and s.endswith("PROCHAINE=ZZZ3\n"),
             (marques, s))
    s, marques = cas("autre-1", "joue-1", enchainer)
    verifier("ARP3 : la marque d'une autre session → l'AVERTISSEMENT: sort encore",
             marques == ["vlp-enchaine-autre-1"] and s.endswith(AVERTI_VIT20 % "ZZZ1, ZZZ2"), (marques, s))
    s, marques = cas("joue-1", "joue-1", enchainer[1:])
    verifier("ARP3 : les appels relais seuls posent la marque (sous Ubuntu, le premier appel échoue)",
             marques == ["vlp-enchaine-joue-1"] and "AVERTISSEMENT:" not in s, (marques, s))
    for sid in (None, "", "../joue-1", "a/b", "joue 1"):
        s, marques = cas(sid, "joue-1", enchainer)
        verifier("ARP3 : id %r → aucune marque, l'AVERTISSEMENT: sort" % (sid,),
                 marques == [] and s.endswith(AVERTI_VIT20 % "ZZZ1, ZZZ2"), (marques, s))

    porteurs = sorted(os.path.basename(os.path.dirname(c)) for c in glob.glob(os.path.join(RACINE, "skills", "*", "SKILL.md"))
                      if "--enchaine" in io.open(c, encoding="utf-8").read())
    texte = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    ligne = next((l for l in texte.splitlines() if l.startswith("!`") and "vlp.py" in l), "")
    verifier("ARP3 : --enchaine sur les trois appels de l'injection de /vlp:enchainer, dans aucune autre skill",
             porteurs == ["enchainer"] and ligne.count("--enchaine") == 3, (porteurs, ligne))


groupe(tester_arp3_marque)


def tester_arp4_menage():
    """Contrôler le ménage des tampons (ARP4) sur ses deux chemins réels, chacun dans son dossier temporaire :
    `carte_injectee` (`vlp-carte-` à RELAIS_SECONDES, `vlp-enchaine-` à MARQUE_SECONDES) et `tampon_neuf`
    (`vlp-hook-` et `vlp-filet-` à 60 s). Un fichier vieilli par `os.utime` ; un dossier au préfixe ne bloque rien."""
    jour = 24 * 3600

    def vieillir(dossier, ages):
        """Créer dans `dossier` un fichier par paire (nom, âge en secondes), daté de cet âge. `0dossier` : un dossier."""
        for nom, age in ages:
            chemin = os.path.join(dossier, nom)
            if "0dossier" in nom:
                os.mkdir(chemin)
            else:
                open(chemin, "w").close()
            os.utime(chemin, (time.time() - age, time.time() - age))

    def restants(dossier):
        return sorted(n for n in os.listdir(dossier) if n != "pr")

    ancien = tempfile.tempdir
    with tempfile.TemporaryDirectory() as bac:
        pr = os.path.join(bac, "pr")
        ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/"))
        ecrire(os.path.join(pr, "context AI", "20-z.md"), FICHES_VIT20)
        vieillir(bac, [("vlp-carte-0dossier", 120), ("vlp-carte-vieux", 120), ("vlp-carte-frais", 5),
                       ("vlp-enchaine-vieille", 5 * jour), ("vlp-enchaine-recente", 2 * jour),
                       ("vlp-hook-vieux", 120), ("autre-vieux", 10 * jour)])
        tempfile.tempdir = bac
        try:
            mod.carte_injectee(pr, "py -3", False, io.StringIO())
        finally:
            tempfile.tempdir = ancien
        cle = hashlib.sha1(os.path.abspath(pr).encode("utf-8")).hexdigest()[:16]
        reste = restants(bac)
        attendu = sorted(["vlp-carte-0dossier", "vlp-carte-frais", "vlp-enchaine-recente", "vlp-hook-vieux",
                          "autre-vieux", "vlp-carte-" + cle])
        verifier("ARP4 : carte_injectee efface vlp-carte- de plus de 30 s et vlp-enchaine- de plus de 4 jours, garde "
                 "les récents, les autres préfixes et son propre tampon ; un dossier au préfixe ne bloque pas la suite "
                 "— mutant : l'âge des marques réduit à celui de vlp-carte-", reste == attendu, (reste, attendu))

    with tempfile.TemporaryDirectory() as bac:
        vieillir(bac, [("vlp-filet-0dossier", 120), ("vlp-hook-vieux", 120), ("vlp-filet-vieux", 120),
                       ("vlp-hook-frais", 10), ("vlp-carte-vieux", 120)])
        neuf = mod.vlp_hook.tampon_neuf("vlp-hook-neuf", bac)
        reste = restants(bac)
        attendu = sorted(["vlp-filet-0dossier", "vlp-hook-frais", "vlp-carte-vieux", "vlp-hook-neuf"])
        verifier("ARP4 : tampon_neuf efface vlp-hook- et vlp-filet- de plus de 60 s, garde le reste, crée le sien",
                 neuf is True and reste == attendu, (neuf, reste, attendu))


groupe(tester_arp4_menage)

# --- NIV2 : `niveau` dit en quoi un projet équipé a dérivé du kit -------------

ETAT_NIV = ("# État\n\n"
            "Le plugin pose `${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py` — prose, pas un chemin lu.\n\n"
            "## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
            "|---|---|---|---|---|\n| 1 | un truc | utile | bas | — |\n")
def tester_niv2_ecarts():
    """Contrôler `niveau` : les catégories d'écart d'un projet en retard (NIV2)."""
    CARTE_SALE = """# Chantier courant

- **alias** : sale
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **méthode** : ${CLAUDE_PLUGIN_ROOT}/methode-chantier.md

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
                 "ÉCART: clos: CHANTIER.md:9 —" in s, s)
        verifier("NIV2 : le poids sort brut, et le bilan compte les deux genres",
                 "POIDS CLAUDE.md absent/80 · CHANTIER.md 13/50 · index 6/80\n" in s
                 and s.rstrip().endswith("NIVEAU 5 écarts · 0 avertissements — %s" % proj), s)


groupe(tester_niv2_ecarts)

CARTE_NETTE = """# Chantier courant

- **alias** : net
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md
- **méthode** : methode-chantier.md, copie d'avant la règle

## Chantiers clos — dans l'index, pas ici
"""
INDEX_NET = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
             "| `08-etat.md` | on reprend |\n")

def tester_niv2_a_niveau():
    """Contrôler `niveau` sur un projet à niveau, et un chemin introuvable (NIV2)."""
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


groupe(tester_niv2_a_niveau)

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

def tester_hab_niveau():
    """Contrôler `niveau` avec un chantier courant (chantier HAB)."""
    code, s = niveau_courant()
    verifier("HAB : `niveau` avec un chantier courant rend son bilan, pas un traceback",
             code is not None and "\nNIVEAU " in s, s)


groupe(tester_hab_niveau)

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


def tester_niv3():
    """Contrôler `niveau --ecrire` : avant, après, et ce qui n'est pas écrit (NIV3)."""
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
                 and "CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:8" in pendant
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


groupe(tester_niv3)

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
                 "CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:8" in s
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


groupe(idx1)

# REP2 : retirer les chevrons d'une URL
def tester_rep2_chevrons():
    """Contrôler le retrait des chevrons d'une URL (REP2)."""
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


groupe(tester_rep2_chevrons)

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


def tester_rep3_compteurs():
    """Contrôler les trois compteurs d'une feuille, puis `clore` (REP3)."""
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
            "- **méthode** :", "- **artefact du chantier** : https://exemple/w\n- **méthode** :")
            + "\nLettres de fiche déjà prises : A. Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "40-w.md"), ouvert("# Chantier W — Un titre\n\n## W1 [x] — a\n"))
        code, s = appel(["clore", proj, "--livre", "y", "--tokens", "950", "--date", "2026-09-19"])
        verifier("clore : une clôture sous 1 000, comptée une fois", code == 0 and "· chantier 950 · cumul 2 450 ·" in s, s)
        rangs = rangs_clos(page)
        verifier("REP3 : clore pose sa ligne au-dessus de la ligne convertie, sans la défaire",
                 len(rangs) == 2 and "2026-09-19" in rangs[0] and rangs[1] == ligne, s)


groupe(tester_rep3_compteurs)

# VOI1 : sans --ecrire, MARKDOWN compte la page du disque, pas la régénérée
def tester_voi1_markdown():
    """Contrôler que sans `--ecrire`, MARKDOWN compte la page du disque (VOI1)."""
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


groupe(tester_voi1_markdown)

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

groupe(test_zone_todo)


def test_feuille_en_cartes():
    """FEU3 : une feuille d'avant, TODO en tableau et badge sur un rang, passe en cartes."""
    with tempfile.TemporaryDirectory() as tc:
        ecrire(os.path.join(tc, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact du chantier** : https://exemple/q\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(tc, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Le `sh` | a \\|\\| b <c> | 2 fiches | — |\n| 4 | **Quatre** | rien | 1 fiche | 3 |\n"
               "| 7 | Sept | [un lien](https://x/y) | à cadrer | `E` |\n\n## Journal\n")
        ecrire(os.path.join(tc, "ctx", "30-q.md"), ouvert("# Chantier Q — Un titre\n\n## Q1 [x] — a\n## Q2 [ ] — b\n"))
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


groupe(test_feuille_en_cartes)


def test_sommaire():
    """FEU4 : sommaire et `id` des trois sections, posés une seule fois sur une feuille sans eux."""
    with tempfile.TemporaryDirectory() as ts:
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


groupe(test_sommaire)

# UNI1 : clore utilise le total mesuré ; sans mesure, retombe sur --tokens
def tester_uni1_total():
    """Contrôler que `clore` utilise le total mesuré, et `--tokens` sans mesure (UNI1)."""
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "uni")
        os.makedirs(proj)
        ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : https://u\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "50-u.md"), ouvert("# Chantier U — test\n\n## U1 [x] — a\n"))
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
        ecrire(os.path.join(proj, "CHANTIER.md"), "# Chantier\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : https://u\n\nLettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(proj, "ctx", "50-u.md"), ouvert("# Chantier U — test\n\n## U1 [x] — a\n"))
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


groupe(tester_uni1_total)

# Une feuille qui ne se régénère pas : les compteurs ne sont pas mesurés, et le disent.
def tester_rep3_sans_etat():
    """Contrôler une feuille qui ne se régénère pas, sans fichier d'état (REP3)."""
    with tempfile.TemporaryDirectory() as t:
        proj = os.path.join(t, "rep3b")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NETTE.replace("- **fichier d'état** : ctx/08-etat.md\n", ""))
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), INDEX_NET)
        code, s = appel(["niveau", proj])
        verifier("REP3 : sans fichier d'état, la ligne MARKDOWN dit « non mesuré »",
                 code == 1 and "MARKDOWN non mesuré, la feuille ne se régénère pas — " in s
                 and "ÉCART: feuille: fichier d'état introuvable : aucun\n" in s, s)


groupe(tester_rep3_sans_etat)



# Simplifier les tests filet
def tester_filet():
    """Contrôler le filet : sous-agent ou non, un avertissement par tour (chantier TOU)."""
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


groupe(tester_filet)


# contrat (chantier CON) : deux sous-agents fabriqués, un propre et un qui commite par `git -C`
def tester_contrat():
    """Contrôler `contrat` : témoins propre et sale, bilan, bornes ; un refusé compté en bloqué (ENQ1)."""
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


groupe(tester_contrat)



# gardien (chantier CON4) : PreToolUse refuse l'écriture Git, SubagentStop renvoie sur statut ou case
def tester_gardien():
    """Contrôler le gardien : ce qu'il refuse et laisse passer, entrées illisibles."""
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
        ecrire(os.path.join(proj, "CHANTIER.md"), CHANTIER % ("px", "."))
        ecrire(os.path.join(proj, "f.md"), "# Chantier X\n\n**Ouvert.** le 2026-10-08.\n\n<!-- FICHE:X1 -->\n## X1 [ ] — une\n<!-- /FICHE -->\n")
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
        ecrire(os.path.join(proj, "f.md"), "# Chantier X\n\n**Ouvert.** le 2026-10-08.\n\n<!-- FICHE:X1 -->\n## X1 [x] — une\n<!-- /FICHE -->\n")
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


groupe(tester_gardien)


# hooks.json : le filet sur tout outil, après un succès et après un échec ; hook sur les écritures
with open(os.path.join(RACINE, "hooks", "hooks.json"), encoding="utf-8") as f:
    crochets = json.load(f)["hooks"]


def paire(groupe, *sous):
    """Les deux commandes d'un groupe : python3 puis `py -3` (sans `-3`, `py` lit le `#!` et relance le
    `python3` du PATH, +77 ms, VIT8), sur `vlp.py <sous>`."""
    return [(h.get("type"), h.get("command"), h.get("args")) for h in groupe.get("hooks", [])] == [
        ("command", c, [*option, "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py", *sous])
        for c, option in (("python3", []), ("py", ["-3"]))]


def tester_hooks_json():
    """Contrôler hooks.json : filet, hook d'écriture, attente, gardien et vigile."""
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


groupe(tester_hooks_json)


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
def tester_relecture():
    """Contrôler `relecture` dans un dépôt à part : instantané, `--sha`, canaux (chantier REV)."""
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

            FICHE_X = ("# Chantier X\n\n**Ouvert.** le 2026-10-08.\n\n## Le socle commun\n\nSocle X.\n\n## L'ordre des fiches\n\n---\n\n"
                       "<!-- FICHE:X1 -->\n## X1 %s — relire\n\n**Fichiers** : `a.py` — et rien d'autre.\n\n"
                       "**Prompt**\nb.py n'est pas nommé.\n<!-- /FICHE -->\n")
            ecrire(os.path.join(depot, "CHANTIER.md"), CHANTIER % ("px", ".") + "- **fichier d'état** : ctx d/etat.md\n")
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


groupe(tester_relecture)


# pre-commit (chantier REV) : lancé par `git commit`, dans un dépôt où le plugin est copié, ses .md en CRLF —
# comme une copie de `relecture` quand core.autocrlf vaut true.
def tester_pre_commit():
    """Contrôler le pre-commit, lancé par `git commit` dans un dépôt à part (chantier REV)."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le hook pre-commit n'est pas testé")
    else:
        with tempfile.TemporaryDirectory() as t:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            depot = os.path.join(t, "plugin")
            for nom in (".claude-plugin", ".githooks", "agents", "hooks", "scripts", "skills"):
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
            # Le hook lance `scripts/vlp.py claude` (VIT19) ; hors suivi, ses .py ne réveillent pas pyright.
            ecrire(os.path.join(depot, ".git", "info", "exclude"), "scripts/\n")
            git("add", "-A")
            code, s = git("commit", "-q", "-m", "copie")
            # Le claude que le hook trouve, ce test le demande au même `vlp.py claude`, sans recopier où l'app le range.
            _, trouve = appel(["claude"])
            if not trouve.startswith("CLAUDE "):
                print("SAUTÉ: %s — le hook pre-commit n'est pas testé" % trouve.strip())
            else:
                verifier("hook : claude trouvé, validate lancé", "validate sauté" not in s, s)
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


groupe(tester_pre_commit)

# GLO1 : forme et poids dans les transcriptions
def tester_forme_transcriptions():
    """Contrôler `forme` sur deux transcriptions (GLO1)."""
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


groupe(tester_forme_transcriptions)

# GLO1 (JUG1) : forme_texte ne juge que la partie du texte que dit sa règle
def tester_forme_texte():
    """Contrôler que `forme_texte` ne juge que la fin du texte (JUG1)."""
    cite = "FAITE — la fiche cite « En résumé » et « Pas bon » en milieu de phrase."
    verifier("forme_texte tete : une citation en milieu de phrase ne compte pas",
             mod.forme_texte(cite, "tete") == (0, 0), mod.forme_texte(cite, "tete"))
    a_part = "✅ **Tout va bien** — fait\n\n**En résumé**\n\nLa fiche est faite."
    verifier("forme_texte tete : le résumé à part, jauge en tête",
             mod.forme_texte(a_part, "tete") == (1, 1), mod.forme_texte(a_part, "tete"))
    verifier("forme_texte tiret : seul l'après-dernier --- est jugé",
             mod.forme_texte("x\n---\n✅ Tout va bien", "tiret") == (0, 1),
             mod.forme_texte("x\n---\n✅ Tout va bien", "tiret"))


groupe(tester_forme_texte)

# GLO1 (FOR1) : forme --depuis filtre sur le départ de la transcription, pas de la session
def tester_forme_depuis():
    """Contrôler que `forme --depuis` filtre sur le départ du sous-agent (FOR1)."""
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


groupe(tester_forme_depuis)

# Test de carte avec TODO
groupe(test_carte_relecteur)
groupe(test_carte_todo)
groupe(test_carte_methode)

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


groupe(test_premier_lancement)


def tester_lanceur_trie():
    """Lancer deux fois le vrai `vlp.py gardien` sur la même entrée, comme `python3` et `py` le font (VIT8) : le
    premier refuse le commit, le second sort 0, muet, sans importer `vlp_coeur` (`-X importtime`). `TMPDIR` neuf :
    le tampon y vit seul."""
    entree = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "agent_type": "vlp:fiche",
                         "tool_input": {"command": "git commit -m 'VIT8 %f'" % time.time()}})
    with tempfile.TemporaryDirectory() as t:
        env = dict(os.environ, TMPDIR=t, PYTHONIOENCODING="utf-8")
        env.pop("VLP_SANS_TAMPON", None)
        r = [subprocess.run([sys.executable, "-X", "importtime", os.path.join(ICI, "vlp.py"), "gardien"], input=entree,
                            capture_output=True, text=True, encoding="utf-8", env=env) for _ in range(2)]
    verifier("VIT8 : deux lanceurs, même entrée — le 1er refuse, le 2e sort muet sans charger le cœur",
             [x.returncode for x in r] == [0, 0] and "deny" in r[0].stdout and "vlp_coeur" in r[0].stderr
             and r[1].stdout == "" and "vlp_coeur" not in r[1].stderr,
             "\n".join("code %d\n%s\n%s" % (x.returncode, x.stdout, x.stderr[-600:]) for x in r))


groupe(tester_lanceur_trie)


def tester_symboles():
    """`vlp.py symboles` sur un fichier à trois fonctions (VIT9) : chacune `nom début-fin`, dans l'ordre du fichier,
    la fonction imbriquée et la méthode tues ; avec des noms, leurs seules lignes, `ABSENT` pour l'inconnu, sort 1."""
    with tempfile.TemporaryDirectory() as t:
        chemin = os.path.join(t, "trois.py")
        ecrire(chemin, "import os\n\n\ndef un():\n    return os.sep\n\n\ndef deux():\n    def dedans():\n"
                       "        return 2\n    return dedans()\n\n\nclass Trois:\n    def m(self):\n        return 3\n")
        o = io.StringIO()
        code = mod.main(["symboles", chemin], o)
        verifier("VIT9 : symboles, une ligne `nom début-fin` par fonction ou classe de premier niveau",
                 code == 0 and o.getvalue() == "un 4-5\ndeux 8-11\nTrois 14-16\n", o.getvalue())
        o = io.StringIO()
        code = mod.main(["symboles", chemin, "Trois", "rien", "un"], o)
        verifier("VIT9 : symboles avec des noms, leurs seules lignes, ABSENT pour l'inconnu, sort 1",
                 code == 1 and o.getvalue() == "Trois 14-16\nABSENT rien\nun 4-5\n", o.getvalue())


groupe(tester_symboles)


def tester_suite_verte():
    """`cocher` dans le kit exige la suite entière verte sur le code du jour (VIT11) : refus sans empreinte, accord
    après `noter_suite_verte`, refus après un script touché — pas après `sante-base.json` ni `context AI/` ; un projet
    équipé, sans plugin, coche sans suite."""
    def cocher(fichier, fiche):
        """Cocher `fiche` par `main` ; rendre (code, sortie)."""
        o = io.StringIO()
        return mod.main(["cocher", fichier, fiche], o), o.getvalue()

    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
        for chemin, texte in ((".claude-plugin/plugin.json", "{}"), ("scripts/test-vlp.py", "print('OK')\n"),
                              ("scripts/sante-base.json", "[]\n")):
            ecrire(os.path.join(t, chemin), texte)
        fiches = os.path.join(t, "context AI", "f.md")
        ecrire(fiches, "# Z\n\n## Z1 [ ] — a\n\n## Z2 [ ] — b\n\n## Z3 [ ] — c\n")
        sans = cocher(fiches, "Z1")
        mod.noter_suite_verte(t, mod.empreinte_kit(t))
        apres = cocher(fiches, "Z1")
        ecrire(os.path.join(t, "scripts", "sante-base.json"), "[1]\n")
        hors = cocher(fiches, "Z2")
        ecrire(os.path.join(t, "scripts", "x.py"), "x = 1\n")
        touche = cocher(fiches, "Z3")
        verifier("VIT11 : cocher dans le kit — refus sans suite verte, accord après, refus après un script touché",
                 sans[0] == 1 and "GARDE: Z1 non cochée" in sans[1] and apres[0] == 0 and hors[0] == 0
                 and touche[0] == 1 and "GARDE: Z3 non cochée" in touche[1]
                 and lire(fiches).count("[x]") == 2, repr((sans, apres, hors, touche)))
        os.remove(os.path.join(t, ".claude-plugin", "plugin.json"))
        equipe = cocher(fiches, "Z3")
        verifier("VIT11 : un projet équipé (sans plugin) coche sans suite verte", equipe[0] == 0, repr(equipe))


groupe(tester_suite_verte)

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


groupe(test_bac)


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
            verifier("claude : rien trouvé → GARDE, sort 1", code == 1 and s.startswith("GARDE: claude.exe introuvable"),
                     s)
            code, s = appel(["bac", os.path.join(tcl, "bac2")])
            verifier("claude : bac sans claude sort 0, GARDE puis SESSION claude", code == 0
                     and 'GARDE: claude.exe introuvable' in s and s.endswith('; & "claude"\n'), s)
            # VIT19 : l'app range claude.exe un dossier plus bas, sous une empreinte ; la version reste au-dessus
            faux("loc2", *paquet[1:], "2.1.99")
            p288 = faux("loc2", *paquet[1:], "2.1.288", "36aa8c97bf86")
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "loc2")
            code, s = appel(["claude"])
            verifier("claude : à la seconde profondeur, 2.1.288 avant 2.1.99", code == 0 and s == "CLAUDE %s\n" % p288, s)
            sans_exe = os.path.join(tcl, "app2", "Claude", "claude-code")
            os.makedirs(os.path.join(sans_exe, "2.1.288", "36aa8c97bf86"))
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "vide")
            os.environ["APPDATA"] = os.path.join(tcl, "app2")
            code, s = appel(["claude"])
            verifier("claude : l'app sans claude.exe → sa GARDE, le dossier nommé, sort 1", code == 1
                     and s.startswith("GARDE: claude.exe absent de l'app") and sans_exe in s, s)
        finally:
            for n, v in avant.items():
                if v is None:
                    os.environ.pop(n, None)
                else:
                    os.environ[n] = v


groupe(test_claude)


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


groupe(test_kit_essai)


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


groupe(test_transcription)

# --- VOI2 : `comparer` dit ce qu'une régénération de page a perdu ou ajouté ---

ANCIENNE_CMP = ("<html><body><table><tbody>\n"
                "<tr><td>ligne A</td></tr>\n"
                "<tr><td>TODO : un truc</td></tr>\n"
                "</tbody></table></body></html>\n")
NEUVE_CMP = ("<html><body><table><tbody>\n"
             "<tr><td>ligne A</td></tr>\n"
             "<tr><td>2026-09-26</td></tr>\n"
             "</tbody></table></body></html>\n")

def tester_voi2_comparer():
    """Contrôler `comparer` : une ligne perdue, une ajoutée (VOI2)."""
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


groupe(tester_voi2_comparer)

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


groupe(tester_page_enveloppee)


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


groupe(tester_plage_refaite)


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
               "- **artefact du chantier** : aucun\n")
        ecrire(os.path.join(tb, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n")
        ecrire(os.path.join(tb, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
        ecrire(os.path.join(tb, "ctx", "30-q.md"), "# Chantier Q — q\n\n## Q2 [ ] — b\n## Q1 [ ] — a\n")
        c, sortie = appel(["ouvrir", tb, "--fiches", "ctx/30-q.md", "--titre", "q"])
        carte = open(os.path.join(tb, "CHANTIER.md"), encoding="utf-8").read()
        verifier("PLG1 : ouvrir sur Q2 puis Q1 écrit Q1..Q2", c == 0 and "OUVERT Q Q1..Q2 " in sortie
                 and mod.courant_de(tb) == "ctx/30-q.md", sortie + carte)


groupe(tester_bornes)


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


groupe(tester_heredoc)


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


groupe(tester_forme_jauge)


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


groupe(tester_lance_clore)


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


groupe(tester_clos_sans_commit)

# --- VOI3 : `lettres_prises` tolère une lettre entre backticks (MapDecorator) -

def tester_voi3_lettres():
    """Contrôler les lettres entre backticks d'une ligne réelle (VOI3)."""
    LIGNE_MAPDECORATOR = "Lettres de fiche déjà prises : `T`, `U`, `R`, `M`. Un nouveau chantier en choisit"
    verifier("VOI3 : lettres entre backticks (ligne réelle de MapDecorator)",
             mod.lettres_prises([LIGNE_MAPDECORATOR]) == ["T", "U", "R", "M"],
             repr(mod.lettres_prises([LIGNE_MAPDECORATOR])))


groupe(tester_voi3_lettres)

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


groupe(tester_abri)

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


groupe(tester_abr2)


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
               ""
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


groupe(tester_vlp_css_recopie)


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


groupe(tester_style_migre)


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


groupe(tester_fiches_repliees)


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


groupe(tester_carte_en_colonnes)


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


groupe(tester_pretes_et_paralleles)


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


groupe(tester_journal_replie)


def tester_bilan_en_haut():
    gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read()
    # une page d'avant PLI6 : le bilan en bas, juste avant le pied de page
    i = gabarit.index("  <!-- ZONE:bilan")
    fin = gabarit.index("  </section>\n", i) + len("  </section>\n\n")
    bloc = gabarit[i:fin]
    ancienne = (gabarit[:i] + gabarit[fin:]).replace("  <footer>", bloc + "  <footer>", 1)
    with tempfile.TemporaryDirectory() as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(tb, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
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


groupe(tester_bilan_en_haut)


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


groupe(tester_vigile)


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


groupe(tester_chef_page)


def tester_lecteur_copie():
    """LEC : le lecteur à voix haute vit en deux copies — vlp.js et vlp.css pour les pages du kit, le gabarit des
    rapports pour les siens ; entre leurs repères LECTEUR, les deux restent pareilles à l'octet (2026-10-06). Les
    nombres insécables aussi, entre leurs repères INSECABLE (2026-10-07)."""
    def entre(nom, debut, fin):
        t = mod.lire(os.path.join(ICI, "..", "templates", nom))
        i = t.find(debut)
        j = t.find(fin, i) if i >= 0 else -1
        return t[i:j + len(fin)] if j >= 0 else None

    rapport = "rapport-choix.html"
    for genre, nom, debut, fin in (("script du lecteur", "vlp.js", "// LECTEUR — début", "// LECTEUR — fin"),
                                   ("style du lecteur", "vlp.css", "/* LECTEUR — début", "/* LECTEUR — fin */"),
                                   ("script des nombres insécables", "vlp.js", "// INSECABLE — début",
                                    "// INSECABLE — fin")):
        kit, copie = entre(nom, debut, fin), entre(rapport, debut, fin)
        verifier("LEC : le %s, dans %s et %s, pareil à l'octet" % (genre, nom, rapport),
                 kit is not None and kit == copie, "%s : %s ; %s : %s" % (
                     nom, "absent" if kit is None else "%d car." % len(kit),
                     rapport, "absent" if copie is None else "%d car." % len(copie)))


groupe(tester_lecteur_copie)


def tester_chef_page_explique():
    """chef page, `explique` (2026-10-06) : l'Explique-moi en option — `data-explique` sur la page et `CAPACITES sample`
    en sortie avec `true`, rien sans, `GARDE:` pour un autre genre."""
    gabarit = mod.lire(os.path.join(ICI, "..", "templates", "rapport-choix.html"))
    d = {"projet": "Demo", "sujet": "essai", "titre": "Rapport d'essai", "date": "2026-10-01",
         "choix": [{"titre": "Quelle suite ?", "options": [{"valeur": "oui", "libelle": "Oui", "effet": "on suit"},
                                                           {"valeur": "non", "libelle": "Non", "effet": "on arrête"}]}]}
    div = '<div class="page" data-cle="Demo-2026-10-01-essai"%s>'
    with tempfile.TemporaryDirectory() as tex:
        rendus = []
        for nom, explique in (("avec", True), ("sans", None), ("oui", "oui")):
            q = dict(d, explique=explique) if explique is not None else d
            chemin = os.path.join(tex, nom + ".html")
            s = io.StringIO()
            code = mod.cmd_chef_page(json.dumps(q, ensure_ascii=False), chemin, s, gabarit)
            page = mod.lire(chemin) if os.path.exists(chemin) else ""
            rendus.append((code, s.getvalue(), page))
    (c1, s1, p1), (c2, s2, p2), (c3, s3, p3) = rendus
    verifier("chef page explique=true : data-explique sur la page, CAPACITES sample après CARTES",
             c1 == 0 and s1.endswith("CARTES Q1\nCAPACITES sample\n") and div % " data-explique" in p1, s1)
    verifier("chef page sans explique : ni data-explique sur la page, ni CAPACITES",
             c2 == 0 and "CAPACITES" not in s2 and div % "" in p2, s2)
    verifier("chef page explique=\"oui\" : GARDE, sort 1, rien d'écrit",
             c3 == 1 and s3 == "GARDE: racine : « explique » vaut true ou false\n" and p3 == "", s3)


groupe(tester_chef_page_explique)

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


groupe(tester_forme)


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


groupe(tester_repeindre)


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


groupe(tester_liens)


def hook_isole(t):
    """Rendre un dépôt neuf sous `t`, le hook du kit branché et `scripts/` copié hors suivi (le hook y lance
    `vlp.py claude`, VIT19), le PATH sans pyright ni claude, et `git(chemins, *args, **env)` : claude caché,
    APPDATA et LOCALAPPDATA vides sauf `env`."""
    depot = os.path.join(t, "depot")
    for nom in (".githooks", "scripts"):
        shutil.copytree(os.path.join(RACINE, nom), os.path.join(depot, nom))
    sans = [d for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and not shutil.which("pyright", path=d) and not shutil.which("claude", path=d)]
    base = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                APPDATA="", LOCALAPPDATA="")
    ecrire(base["GIT_CONFIG_GLOBAL"], "")

    def git(chemins, *args, **env):
        r = subprocess.run(["git"] + list(args), cwd=depot, env=dict(base, PATH=os.pathsep.join(chemins), **env),
                           capture_output=True, encoding="utf-8", errors="replace")
        return r.returncode, r.stdout + r.stderr

    git(sans, "init", "-q")
    git(sans, "config", "core.hooksPath", ".githooks")
    ecrire(os.path.join(depot, ".git", "info", "exclude"), "scripts/\n")
    return depot, sans, git


def tester_hook_pyright():
    # TYP1 : le hook lance pyright quand un .py est indexé. claude caché (`hook_isole`), le vrai pyright aussi :
    # un faux, en tête du PATH, sort 1.
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le bloc pyright du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        depot, sans, git = hook_isole(t)
        faux = os.path.join(t, "faux")
        os.mkdir(faux)
        ecrire(os.path.join(faux, "pyright"), '#!/bin/sh\necho "faux pyright : 1 error"\nexit 1\n')
        os.chmod(os.path.join(faux, "pyright"), 0o755)
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


groupe(tester_hook_pyright)


def tester_hook_claude():
    # VIT19 : le hook demande claude à `vlp.py claude`. L'app là sans son claude.exe refuse le commit, en le
    # disant ; ni app ni claude, il passe averti. claude trouvé, validate lancé : `tester_pre_commit`.
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le bloc claude du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        depot, sans, git = hook_isole(t)
        app = os.path.join(t, "loc", "Packages", "Claude_x1", "LocalCache", "Roaming", "Claude", "claude-code")
        os.makedirs(os.path.join(app, "2.1.288", "36aa8c97bf86"))
        ecrire(os.path.join(depot, "a.md"), "a\n")
        git(sans, "add", "a.md")
        code, s = git(sans, "commit", "-q", "-m", "md", LOCALAPPDATA=os.path.join(t, "loc"))
        verifier("hook claude : l'app sans claude.exe refuse le commit, en le disant", code == 1
                 and "GARDE: claude.exe absent de l'app" in s and app in s
                 and "pre-commit : l'app Claude est là sans claude.exe trouvé, validate impossible, commit refusé." in s, s)
        code, s = git(sans, "commit", "-q", "-m", "md")
        verifier("hook claude : ni app ni claude, le commit passe averti", code == 0
                 and "pre-commit : claude introuvable, ni dans le PATH ni dans l'app, validate sauté." in s, s)


groupe(tester_hook_claude)


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


groupe(tester_contrat_ouverture)


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


groupe(tester_lien_feuille_de_route)


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
    # les cellules « Coût » de la TODO du 2026-10-08, recopiées telles quelles (NUI38)
    cellules = {
        "~6 fiches, plus une nuit d'essai · ré-estimé à `MET10` (restent `NUI28` à `NUI32` et `NUI20`, `CLR` compris : "
        "7 fiches) : 14 à 21 fiches, 52 à 77 $, plus la nuit d'essai (borne 20 $)": 21.0,
        "~2 fiches de lecture et de mesure, sans code, plus un essai de Remote Build `(visuel)` : jeu ouvert, geste de "
        "l'utilisateur (estimé, non mesuré — les estimations sous-estiment) · ré-estimé à `MET10` : 4 à 6 fiches, 15 à 22 $": 6.0,
        "5 fiches, dont 2 qui demandent une réponse de l'utilisateur (REF2, REF5) et 1 de code (REF3, le script de mesure) "
        "· ré-estimé à `MET10`, re-cadré en 3 fiches : 6 à 9 fiches, 22 à 33 $ ; le refactoring, chiffré par son bilan": 9.0,
        "~1 fiche (estimé, non mesuré — les estimations sous-estiment) · ré-estimé à `MET10`, `CLV` et `OTE` compris : "
        "3,5 fiches → 7 à 10,5, 26 à 39 $": 10.5,
        "~1½ fiche (estimé, non mesuré ; ~½ avant la fonte) · ré-estimé à `MET10` : 3 à 4,5 fiches, 11 à 17 $": 4.5,
        "~1 fiche (estimé, non mesuré) · ré-estimé à `MET10` : 2 à 3 fiches, 7,4 à 11 $ · avec la recopie (clôture de "
        "`MET`) : 4 à 6 fiches, 15 à 22 $": 6.0,
        "≈ 10 $ d'essais et ≈ 1 h 45, estimés depuis `MET4`, non mesurés ; plus le juge, ~1 fiche → 2 à 3 fiches, 7,4 à "
        "11 $ · avec les 2 essais (clôture de `MET`) : +½ fiche → 2,5 à 3,5 fiches, 9 à 13 $": 3.5,
        "~5 fiches · ≈15 $ au taux du 2026-09-29 (3,03 $/fiche sur 80 clos ; estimé, non mesuré — les estimations "
        "sous-estiment : chantiers de pages joués `LOC` 5 fiches 11,74 $, `PLI` 7 fiches 17,96 $, `BTN` 7 fiches 47,08 $) "
        "· re-cadré à `MET10`, l'étape (1) seule : 1 à 1,5 fiche, 3,7 à 5,5 $ ; le reste, sur sa mesure": 1.5,
        "~1 fiche, sans code (estimé, non mesuré) · re-cadré à `MET10` : sans fiche, une séance courte, non chiffrée": None,
    }
    lues = {c: mod.borne_haute_cout(c) for c in cellules}
    verifier("NUI38 : borne_haute_cout — la dernière estimation fait foi (segment ` · `, puis `→`), ni somme ni durée, "
             "« sans fiche » → None",
             lues == cellules, [(c[:40], lues[c], v) for c, v in cellules.items() if lues[c] != v])
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
               "- **artefact du chantier** : aucun\n\n"
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


groupe(tester_decompte_todo)


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
               "- **artefact du chantier** : aucun\n\n"
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


groupe(tester_barre_todo)


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
               "- **artefact du chantier** : aucun\n\n"
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


groupe(tester_trier)


def tester_trier_branche():
    """BRA1 : dans Git, `trier` ne trie que sur `main` ; ailleurs, une seule ligne `GARDE:`, sort 1."""
    with tempfile.TemporaryDirectory() as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n")
        ecrire(os.path.join(tb, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `AAA` — a | x | 1 fiche | — |\n\n## Journal\n")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tb, capture_output=True)
        code_main, s_main = appel(["trier", tb])
        subprocess.run(["git", "switch", "-q", "-c", "nuit/x"], cwd=tb, capture_output=True)
        code, s = appel(["trier", tb])
        verifier("BRA1 : trier sort 0 sur main, 1 sur nuit/x — une seule ligne, GARDE: trier hors de main",
                 code_main == 0 and code == 1 and len(s.splitlines()) == 1 and s.startswith("GARDE: trier hors de main"),
                 "%s\n%s" % (s_main, s))


groupe(tester_trier_branche)


# --- NUI11 : le fichier des nuits, ses leçons et le TAUX imprimés par trier ---

def tester_fichier_nuits():
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
    with tempfile.TemporaryDirectory() as tp:
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


groupe(tester_fichier_nuits)


# --- NUI12 : le plan du soir, écrit dans le fichier des nuits, relu par la nuit ---

def tester_plan():
    entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
    carte = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
             "- **artefact du chantier** : aucun\n\n"
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
        verifier("NUI12 (d) : carte sous VLP_NUIT=1 → NUIT=1 une fois, après --- CHANTIER.md --- et avant --- fiches : — mutant : ligne jamais écrite",
                 nuit.count("NUIT=1") == 1 and nuit.index("--- CHANTIER.md ---") < nuit.index("NUIT=1")
                 < next(k for k, l in enumerate(nuit) if l.startswith("--- fiches :")), nuit)
        verifier("NUI12 (d) : --relecteur, VLP_NUIT=0 et variable absente → aucune ligne NUIT=",
                 not any(l.startswith("NUIT=") for l in carte_sous("1", True) + carte_sous("0") + carte_sous(None)), "")
    if env is not None:
        os.environ["VLP_NUIT"] = env


groupe(tester_plan)


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


groupe(tester_joints)


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
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
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


groupe(tester_attente)


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
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
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


groupe(tester_publie)


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
            ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
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


groupe(tester_apercu)


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
            commit(d, "CHANTIER.md", "# C\n\n")
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


groupe(tester_retard_plugin)


def tester_mutant():
    """MUT1 : casser, tester, lister les écarts, rendre à l'octet — CRLF, @fichier, gardes."""
    with tempfile.TemporaryDirectory() as tm:
        f, essai, apres = (os.path.join(tm, x) for x in ("f.py", "essai.py", "apres.txt"))
        source = "a = 1\r\nb = 2\r\nc = 3\r\n"
        ecrire(f, source)
        ecrire(essai, "import sys\nt = open(sys.argv[1], encoding='utf-8').read()\n"
                      "n = 0\nfor v in ('a = 1', 'b = 2'):\n    if v not in t:\n        print('ÉCART:', v); n += 1\n"
                      "print('FIN: %d' % n if n else 'OK')\nsys.exit(1 if n else 0)\n")
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
        plante = (mod.cmd_mutant(mod.argparse.Namespace(cible=f, avant="c = 3", apres="c = 4", attendu=None,
                                                        test=[os.path.join(tm, "absent.exe")]), o), o.getvalue())
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


groupe(tester_mutant)

# La suite factice de VIT2 : la copie de f, le fichier qui nomme le vrai f, et deux fichiers hors de la copie —
# l'empreinte du vrai f vue pendant la suite, et la trace d'un petit-fils qui survivrait 2 s.
SUITE_MUTANT = """import hashlib, subprocess, sys, time
t = open(sys.argv[1], encoding="utf-8").read()
vrai = open(sys.argv[2], encoding="utf-8").read().strip()
open(sys.argv[3], "w").write(hashlib.sha1(open(vrai, "rb").read()).hexdigest()[:12])
if "x = 2" in t:
    subprocess.Popen([sys.executable, "-c", "import sys, time; time.sleep(2); open(sys.argv[1], 'w').write('vivant')",
                      sys.argv[4]])
    print("ÉCART: autre")
    print("ÉCART: attendu ici")
    time.sleep(30)
    print("FIN: 2 écart(s)")
    sys.exit(1)
print("ÉCART: autre")
if "x = 3" in t:
    sys.exit(1)
print("FIN: 1 écart(s)")
sys.exit(1)
"""


def tester_mutant_attendu():
    """VIT2 : le mutant joue une copie, le vrai fichier inchangé pendant et après ; `--attendu` tue l'arbre dès son
    écart, VIVANT s'il ne tombe pas ; une suite arrêtée en erreur après un autre écart est PLANTÉ, `--tous` aussi."""
    with tempfile.TemporaryDirectory() as tm, tempfile.TemporaryDirectory() as hors:
        f, suite = os.path.join(tm, "f.py"), os.path.join(tm, "suite.py")
        reel, pendant, petit = (os.path.join(hors, x) for x in ("reel.txt", "pendant.txt", "petit.txt"))
        ecrire(f, "x = 1\n")
        ecrire(reel, f)
        ecrire(suite, SUITE_MUTANT)
        test = '"%s" "%s" "%s" "%s" "%s" "%s"' % (sys.executable, suite, f, reel, pendant, petit)
        empreinte = mod.hashlib.sha1(b"x = 1\n").hexdigest()[:12]

        def mutant(apres, *options):
            """Jouer le mutant `x = 1` → `apres` ; rendre (code, sortie, secondes, vrai fichier inchangé)."""
            o, debut = io.StringIO(), time.perf_counter()
            code = mod.main(["mutant", f, "x = 1", apres, "--test", test, *options], o)
            with open(f, "rb") as g:
                return code, o.getvalue(), time.perf_counter() - debut, g.read() == b"x = 1\n"
        attrape = mutant("x = 2", "--attendu", "attendu")
        with open(pendant, encoding="utf-8") as g:
            vu_pendant = g.read()
        time.sleep(2.5)     # le petit-fils, s'il vit encore, a écrit sa trace
        verifier("VIT2 : --attendu juste → MUTANT ATTRAPÉ, l'arbre tué dès l'écart (pas 30 s, petit-fils compris) ; "
                 "vrai fichier inchangé pendant (sha1) et après — mutants : muter le vrai fichier, tuer le seul fils",
                 attrape[0] == 0 and "MUTANT ATTRAPÉ 2 écart(s) · arrêté sur « attendu »\n" in attrape[1]
                 and attrape[2] < 20 and not os.path.exists(petit) and vu_pendant == empreinte and attrape[3]
                 and "RENDU %s\n" % empreinte in attrape[1] and "COPIE restée" not in attrape[1],
                 (attrape, vu_pendant, os.path.exists(petit)))
        vivant = mutant("x = 4", "--attendu", "jamais")
        verifier("VIT2 : --attendu d'un test qui ne tombe pas → MUTANT VIVANT pour …, sort 1, avec les écarts vus",
                 vivant[0] == 1 and vivant[1].startswith("ÉCART: autre\nMUTANT VIVANT pour jamais\n") and vivant[3],
                 vivant)
        plante = mutant("x = 3", "--attendu", "attendu")
        plante_tous = mutant("x = 3")
        verifier("VIT2 : la suite arrêtée en erreur après un autre écart → MUTANT PLANTÉ, sort 1, avec --attendu comme "
                 "sans — mutant : ATTRAPÉ dès qu'un écart est vu",
                 all(p[0] == 1 and "MUTANT PLANTÉ · tests sortis 1 sans finir, après 1 écart(s)" in p[1]
                     and "ATTRAPÉ" not in p[1] and p[3] for p in (plante, plante_tous)), (plante, plante_tous))


groupe(tester_mutant_attendu)

# La suite factice de VIT21, posée en `scripts/test-vlp.py` d'un faux kit : deux groupes, et un contrôle hors de
# tout groupe, comme ceux de test-boucle.py ; `--seul` filtre les groupes sur leur texte, comme `porte_motif`, et
# chaque lancement note son motif dans le journal.
SUITE_VISEE = """import sys
t = open("f.py", encoding="utf-8").read()
motif = sys.argv[sys.argv.index("--seul") + 1] if "--seul" in sys.argv else ""
open(@JOURNAL@, "a", encoding="utf-8").write(motif + "\\n")
groupes = {"g_porte": [("porte a", "a = 1")], "g_voisin": [("voisin b", "b = 2")]}
controles = [c for nom, cs in groupes.items() for c in cs if motif.lower() in (nom + " " + repr(cs)).lower()]
if not motif:
    controles.append(("hors c", "c = 3"))
elif not controles:
    print("SEUL " + motif + " : 0 groupe(s), 0 contrôle(s) — ")
    print("GARDE: aucun groupe ne porte « " + motif + " »")
    sys.exit(1)
ecarts = [nom for nom, v in controles if v not in t]
for nom in ecarts:
    print("ÉCART:", nom)
print("FIN: %d écart(s)" % len(ecarts) if ecarts else "OK")
sys.exit(1 if ecarts else 0)
"""


def tester_mutant_vise():
    """VIT21 : `--attendu` sans `--test` ne joue d'abord que les groupes qui portent son libellé (`--seul`) ; attrapé
    là, une ligne `VISÉ` le dit ; aucun groupe, ou pas cet écart : la suite entière tranche, dite ; `--test` garde le
    dernier mot."""
    with tempfile.TemporaryDirectory() as tm:
        kit, journal = os.path.join(tm, "kit"), os.path.join(tm, "journal.txt")
        f = os.path.join(kit, "f.py")
        ecrire(f, "a = 1\nb = 2\nc = 3\n")
        ecrire(os.path.join(kit, "scripts", "test-vlp.py"), SUITE_VISEE.replace("@JOURNAL@", repr(journal)))

        def mutant(avant, apres, attendu, *options):
            """Jouer le mutant `avant` → `apres` sur le faux kit ; rendre (code, sortie, motifs des lancements)."""
            ecrire(journal, "")
            o = io.StringIO()
            garde, mod.KIT = mod.KIT, kit
            try:
                code = mod.main(["mutant", f, avant, apres, "--attendu", attendu, *options], o)
            finally:
                mod.KIT = garde
            with open(journal, encoding="utf-8") as j:
                return code, o.getvalue(), j.read().split("\n")[:-1]
        vise = mutant("a = 1", "a = 9", "porte a")
        verifier("VIT21 : --attendu sans --test → ses seuls groupes (--seul), MUTANT ATTRAPÉ dit VISÉ, sans suite "
                 "entière — mutant : --seul jamais ajouté",
                 vise[0] == 0 and vise[1].startswith("VISÉ --seul « porte a »\nÉCART: porte a\n"
                                                     "MUTANT ATTRAPÉ 1 écart(s) · arrêté sur « porte a »\n")
                 and vise[2] == ["porte a"], vise)
        sans = mutant("c = 3", "c = 9", "hors c")
        verifier("VIT21 : un --attendu qu'aucun groupe ne porte → la GARDE de --seul n'est pas un écart : suite "
                 "entière, dite, qui l'attrape — mutant : pas de repli",
                 sans[0] == 0 and sans[1].startswith("SUITE ENTIÈRE · aucun groupe ne porte « hors c »\nÉCART: hors c\n"
                                                     "MUTANT ATTRAPÉ 1 écart(s) · arrêté sur « hors c »\n")
                 and sans[2] == ["hors c", ""], sans)
        autre = mutant("b = 2", "b = 9", "porte a")
        verifier("VIT21 : un groupe qui ne porte pas le contrôle ne rend jamais ATTRAPÉ — suite entière, dite, "
                 "MUTANT VIVANT pour …, sort 1",
                 autre[0] == 1 and autre[1].startswith("SUITE ENTIÈRE · « porte a » n'est pas tombé dans ses groupes\n"
                                                       "ÉCART: voisin b\nMUTANT VIVANT pour porte a\n")
                 and "ATTRAPÉ" not in autre[1] and autre[2] == ["porte a", ""], autre)
        test = '"%s" "%s"' % (sys.executable, os.path.join(kit, "scripts", "test-vlp.py"))
        dernier = mutant("a = 1", "a = 9", "porte a", "--test", test)
        verifier("VIT21 : --test donné garde le dernier mot — sa seule commande, ni VISÉ ni SUITE ENTIÈRE",
                 dernier[0] == 0 and dernier[1].startswith("ÉCART: porte a\nMUTANT ATTRAPÉ 1 écart(s)")
                 and dernier[2] == [""], dernier)


groupe(tester_mutant_vise)


def tester_mutant_worktree():
    """MUW1 : une cible dans un worktree du kit rangé sous le dépôt principal (`KIT`) joue les tests du worktree,
    pas ceux de `KIT`, et une ligne `TESTS` le nomme."""
    with tempfile.TemporaryDirectory() as tm:
        principal = os.path.join(tm, "principal")
        interieur = os.path.join(principal, ".claude", "worktrees", "w")
        for k, suite in ((principal, "print('OK')\n"),
                         (interieur, SUITE_VISEE.replace("@JOURNAL@", repr(os.path.join(tm, "journal.txt"))))):
            ecrire(os.path.join(k, ".claude-plugin", "plugin.json"), "{}\n")
            ecrire(os.path.join(k, "scripts", "test-vlp.py"), suite)
        f = os.path.join(interieur, "f.py")
        ecrire(f, "a = 1\nb = 2\nc = 3\n")
        o = io.StringIO()
        garde, mod.KIT = mod.KIT, principal
        try:
            code = mod.main(["mutant", f, "a = 1", "a = 9", "--attendu", "porte a"], o)
        finally:
            mod.KIT = garde
        verifier("MUW1 : cible d'un worktree sous KIT → ses tests à lui, MUTANT ATTRAPÉ et ligne TESTS du worktree — "
                 "mutant : copie_mutee reprise sur KIT",
                 code == 0 and "MUTANT ATTRAPÉ" in o.getvalue() and "TESTS %s\n" % interieur in o.getvalue()
                 and mod.kit_de(f) == interieur, (code, o.getvalue()))


groupe(tester_mutant_worktree)

# Le faux cliquet et le faux pyright de VIT23 : le cliquet rompt si un fichier `rompu` est à la racine ; pyright
# compte une erreur par fichier qui porte le mot `erreur`.
CLIQUET_FAUX = """import os, sys
if os.path.exists("rompu"):
    print("EMPIRE f.py:1 g · complexité 3 → 11, seuil 10")
    print("CLIQUET ROMPU")
    sys.exit(1)
print("CLIQUET 1 fonctions · vieilles 1, dont touchées 0, renommées ou déplacées 0 · neuves 0")
print("CLIQUET TENU")
"""
PYRIGHT_FAUX = """import sys
fautifs = [f for f in sys.argv[1:] if "erreur" in open(f, encoding="utf-8").read()]
for f in fautifs:
    print("  %s:1:1 - error: faux" % f)
print("%d errors, 0 warnings, 0 informations " % len(fautifs))
sys.exit(1 if fautifs else 0)
"""


def tester_rapide():
    """VIT23 : `vlp.py rapide` joue les groupes de la fiche (`--seul`), pyright sur les `.py` touchés et le cliquet ;
    un écart semé dans le groupe d'une fiche → rouge, sans suite entière ; un contrôle sauté dit sa raison."""
    with tempfile.TemporaryDirectory() as tr:
        kit, journal = os.path.join(tr, "kit"), os.path.join(tr, "journal.txt")
        pyright = [sys.executable, os.path.join(tr, "pyright.py")]
        ecrire(pyright[1], PYRIGHT_FAUX)
        ecrire(os.path.join(kit, "f.py"), "a = 1\nb = 2\nc = 3\n")
        ecrire(os.path.join(kit, "scripts", "test-vlp.py"), SUITE_VISEE.replace("@JOURNAL@", repr(journal)))
        ecrire(os.path.join(kit, "scripts", "vlp.py"), CLIQUET_FAUX)
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "0"]):
            subprocess.run(["git"] + args, cwd=kit, capture_output=True, check=True)
        propre = mod.controles_rapides(kit, "porte", pyright)[1]
        verifier("VIT23 : arbre propre → pyright sauté, « aucun .py touché » — mutant : pyright lancé sur rien",
                 propre == ("pyright", None, "aucun .py touché"), propre)

        def rapide(motif, outil=pyright):
            """Jouer `rapide` sur le faux kit ; rendre (code, sortie aux durées masquées, motifs lancés)."""
            ecrire(journal, "")
            o = io.StringIO()
            code = mod.controle_rapide(kit, motif, outil, o)
            with open(journal, encoding="utf-8") as j:
                return code, re.sub(r"\d+\.\d s", "N s", o.getvalue()), j.read().split("\n")[:-1]
        ecrire(os.path.join(kit, "f.py"), "a = 1\nb = 2\nc = 3\nd = 4\n")
        ecrire(os.path.join(kit, "sous dossier", "neuf.py"), "e = 5\n")
        ecrire(os.path.join(kit, "note.txt"), "x\n")
        touches = [t.replace(os.sep, "/").rsplit("/kit/", 1)[-1] for t in mod.py_touches(kit)]
        verifier("VIT23 : les .py touchés — modifié, et neuf sous un dossier à espace —, ni .txt ni .py intact",
                 touches == ["f.py", "sous dossier/neuf.py"], touches)
        vert = rapide("porte")
        verifier("VIT23 : tout passe → trois lignes vertes, RAPIDE VERT, sort 0 ; seul --seul lancé, jamais la suite "
                 "entière", vert[0] == 0 and vert[2] == ["porte"] and vert[1] == (
                     "RAPIDE groupes « porte » : vert · N s · OK\n"
                     "RAPIDE pyright 2 fichier(s) : vert · N s · 0 errors, 0 warnings, 0 informations\n"
                     "RAPIDE cliquet : vert · N s · CLIQUET TENU\n"
                     "RAPIDE VERT · N s — la suite entière reste à jouer : cocher l'exige\n"), vert)
        ecrire(os.path.join(kit, "f.py"), "a = 9\nb = 2\nc = 3\nd = 4\n")
        seme = rapide("porte")
        verifier("VIT23 : un écart semé dans le groupe de la fiche → rouge, ses lignes, RAPIDE ROUGE, sort 1, sans "
                 "lancer la suite entière — mutant : un rouge parmi des verts ne compte pas",
                 seme[0] == 1 and seme[2] == ["porte"] and seme[1].startswith(
                     "RAPIDE groupes « porte » : rouge · N s · code 1\n  ÉCART: porte a\n  FIN: 1 écart(s)\n")
                 and seme[1].endswith("RAPIDE ROUGE · N s — corrige avant de lancer la suite entière\n"), seme)
        ecrire(os.path.join(kit, "f.py"), "a = 1\nb = 2\nc = 3\nd = 4\n")
        ecrire(os.path.join(kit, "sous dossier", "neuf.py"), "erreur = 5\n")
        ecrire(os.path.join(kit, "rompu"), "")
        types = rapide("porte")
        verifier("VIT23 : pyright en erreur et cliquet rompu → chacun rouge, avec ses lignes",
                 types[0] == 1 and "RAPIDE pyright 2 fichier(s) : rouge · N s · code 1\n" in types[1]
                 and "neuf.py:1:1 - error: faux\n  1 errors, 0 warnings, 0 informations\n" in types[1]
                 and "RAPIDE cliquet : rouge · N s · code 1\n  EMPIRE f.py:1 g · complexité 3 → 11, seuil 10\n"
                     "  CLIQUET ROMPU\n" in types[1], types)
        os.remove(os.path.join(kit, "rompu"))
        sautes = rapide("rien", None)
        verifier("VIT23 : aucun groupe ne porte le motif, pyright absent → sautés, chacun sa raison, VERT",
                 sautes[0] == 0 and sautes[2] == ["rien"] and sautes[1] == (
                     "RAPIDE groupes « rien » : sauté · N s · aucun groupe ne porte ce motif\n"
                     "RAPIDE pyright : sauté · pyright introuvable\n"
                     "RAPIDE cliquet : vert · N s · CLIQUET TENU\n"
                     "RAPIDE VERT · N s — la suite entière reste à jouer : cocher l'exige\n"), sautes)
        o = io.StringIO()
        absent = mod.ecrire_rapide("x", None, mod.jouer_rapide([os.path.join(tr, "absent.exe")], kit), o)
        hors = io.StringIO()
        verifier("VIT23 : une commande qui ne se lance pas → rouge, dite ; hors du kit → GARDE, sort 1",
                 absent and "RAPIDE x : rouge · " in o.getvalue() and "  ne se lance pas : " in o.getvalue()
                 and mod.main(["rapide", "porte", "--racine", tr], hors) == 1
                 and hors.getvalue().startswith("GARDE: ") and "pas de scripts/test-vlp.py" in hors.getvalue(),
                 (o.getvalue(), hors.getvalue()))


groupe(tester_rapide)


def tester_boucle():
    """NUI2 : test-boucle.py joue boucle.py et faux-claude.py ; lancé d'ici, un mutant de l'un ou de l'autre
    tombe aussi sous `vlp.py mutant` sans --test. Sa sortie passe en entier : son `ÉCART:` y remonte. Récolter le
    lancement du début de suite (`BOUCLE`, VIT7), ou, sous `VLP_BOUCLE_SERIE=1`, le lancer ici et l'attendre."""
    p, sortie, erreur = BOUCLE or lancer_boucle()
    code = p.wait()
    sortie.seek(0)
    erreur.seek(0)
    texte, err = sortie.read(), erreur.read()
    verifier("boucle : test-boucle.py (boucle.py et son faux claude) sort OK",
             code == 0 and texte.strip() == "OK", texte + err)


def tester_boucle_nuit():
    """ENV1 : cette suite retire les variables de la nuit avant de lancer `test-boucle.py`, qui ne les voit donc
    jamais ; ce test les lui pose, sur sa seule partie qui les attend absentes, pour que son propre retrait se voie."""
    debut = time.perf_counter()
    r = subprocess.run([sys.executable, os.path.join(ICI, "test-boucle.py"), "--parties", "sans_nuit"],
                       capture_output=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8", VLP_NUIT="1", VLP_CANAL="B",
                                VLP_CARNET=os.path.join(tempfile.gettempdir(), "carnet-env1.jsonl")))
    verifier("ENV1 : test-boucle.py --parties sans_nuit, sous les trois variables de la nuit, sort 0 sans ÉCART "
             "— mutant : le retrait en tête de test-boucle.py neutralisé",
             r.returncode == 0 and "ÉCART" not in r.stdout, (time.perf_counter() - debut, r.stdout + r.stderr))


def suite_voisine(chemin):
    """Jouer jusqu'au bout la suite de tests `chemin`, une voisine de celle-ci ; rendre (verte, sa sortie) — verte :
    elle sort 0 et dit `OK` en dernière ligne (VIT24)."""
    r = subprocess.run([sys.executable, chemin], capture_output=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return r.returncode == 0 and r.stdout.strip().endswith("OK"), r.stdout + r.stderr


def tester_mesure_tokens():
    """VIT24 : la suite joue `test-mesure-tokens.py`, que rien ne lançait ; une voisine qui échoue — sort 1, même en
    disant `OK`, ou sort 0 sans le dire — la rend rouge."""
    with tempfile.TemporaryDirectory() as tm:
        rate, muette = os.path.join(tm, "test-rate.py"), os.path.join(tm, "test-muette.py")
        ecrire(rate, 'print("ÉCART: semé")\nprint("OK")\nraise SystemExit(1)\n')
        ecrire(muette, 'print("FIN: 1 écart(s)")\n')
        rouges = [suite_voisine(rate), suite_voisine(muette)]
    verifier("VIT24 : une voisine qui sort 1, ou qui sort 0 sans OK, n'est pas verte — mutant : le code de sortie "
             "ignoré", [r[0] for r in rouges] == [False, False] and "ÉCART: semé" in rouges[0][1], rouges)
    verte, texte = suite_voisine(os.path.join(ICI, "test-mesure-tokens.py"))
    verifier("mesure-tokens : test-mesure-tokens.py sort OK", verte, texte)


groupe(tester_mesure_tokens)


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


groupe(tester_nuits)


# --- NUI15 : `vlp.py matin`, la fusion de la nuit dans main -------------------------------------
JOUR_MATIN = "2026-10-01"
CARTE_MATIN = ("# Chantier courant\n\n- **alias** : mt\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n"
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
    ecrire(os.path.join(d, "ctx", "40-loc.md"), ouvert("# Chantier LOC — Publier\n\n## LOC1 [ ] — a\n"))
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
    """`nuit/<jour>-<canal>-<code>`, un commit à `heure` depuis `main` : `clos`, le chantier est clos (l'artefact à
    `aucun`), sinon ouvert sur la branche, `ctx/41-<code>.md` à sa marque — l'hérité de main ne compte pas (NUI31) et la feuille refaite sans badge ; `lettre`, sa lettre ajoutée à la liste ; `x`, le nouveau
    `scripts/x.py` ; `ligne`, la plage d'une ligne close de plus à l'archive ; `retire`, le rang ôté de la TODO ;
    `modifs(d)`, d'autres retouches, avant la feuille."""
    nom = "nuit/%s-%s-%s" % (JOUR_MATIN, canal, code)
    git_matin(d, "switch", "-q", "-c", nom, "main")
    chemin = os.path.join(d, "CHANTIER.md")
    carte_ = lire(chemin)
    if clos:
        carte_ = re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", carte_)
    else:
        ecrire(os.path.join(d, "ctx", "41-%s.md" % code.lower()), ouvert("# Chantier %s — c\n\n## %s1 [ ] — a\n"
                                                                          % (code, code)))
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
             and mod.courant_de(d) == "ctx/40-loc.md"
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
             code == 0 and s == (ORDRE_ABSENT + "DE CÔTÉ %s — ctx/41-wip.md\nFUSIONNÉE %s\n"
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
             and "- **artefact du chantier** : https://claude.ai/artifact/LOC" in carte_ and "<<<<<<<" not in carte_,
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
               "GARDE: CHANTIER.md de main sans sa ligne « artefact du chantier »", "GARDE: HEAD est sur autre, pas sur main",
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


def matin_s(tr):
    """(s) `matin` sans date : la seule nuit à ranger est prise et dite ; plusieurs nuits, ou aucune (tout fusionné, ou
    de côté), ne fusionnent rien ; `--rapport` veut la date."""
    d, wip_d, rapport = os.path.join(tr, "s"), os.path.join(tr, "swip"), os.path.join(tr, "s-rapport.json")
    depot_matin(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    ancienne = "nuit/2026-09-30-A-OLD"
    git_matin(d, "branch", ancienne, nom)
    code2, s2 = appel(["matin", d])
    intacte = code_git(d, "merge-base", "--is-ancestor", nom, "main") == 1
    code_r, s_r = appel(["matin", d, "--rapport", rapport])
    git_matin(d, "branch", "-D", ancienne)
    code1, s1 = appel(["matin", d])
    code0, s0 = appel(["matin", d])
    depot_matin(wip_d)
    wip = branche_matin(wip_d, "A", "WIP", None, 1, clos=False, x="a = 1\nb = 2\nc = 30\n")
    codew, sw = appel(["matin", wip_d])
    aucune = "GARDE: aucune nuit à ranger (1 branche(s) nuit/* déjà fusionnée(s) ou de côté) — rien fusionné\n"
    verifier("NUI15 (s) matin sans date : deux nuits → GARDE qui les liste (la plus ancienne d'abord), rien fusionné ; "
             "--rapport sans date → GARDE ; la seule nuit → NUIT <date> puis la fusion ; plus rien à ranger, ou une "
             "branche de côté seule → GARDE aucune nuit, sort 1 — mutants : « plusieurs » prend la première, une "
             "branche de côté compte comme à ranger",
             code2 == 1 and s2 == "GARDE: plusieurs nuits à ranger : 2026-09-30 (1), 2026-10-01 (1) — rien fusionné ; "
             "donne la date\n" and intacte
             and code_r == 1 and s_r.startswith("GARDE: --rapport veut la date de la nuit") and not os.path.exists(rapport)
             and code1 == 0 and s1 == ("NUIT 2026-10-01 — la seule à ranger : 1 branche(s)\n" + ORDRE_ABSENT
                                       + "FUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % nom)
             and code_git(d, "merge-base", "--is-ancestor", nom, "main") == 0
             and code0 == 1 and s0 == aucune and codew == 1 and sw == aucune
             and code_git(wip_d, "merge-base", "--is-ancestor", wip, "main") == 1,
             (code2, s2, intacte, code_r, s_r, code1, s1, code0, s0, codew, sw))


def matin_t(tr):
    """(t) une fusion qui touche `scripts/` : `PLUGIN_RETARD=1` avant `MATIN` quand le projet est le kit chargé (`KIT`),
    rien pour un autre projet (RTD1)."""
    sorties = []
    for nom, est_kit in (("t-kit", True), ("t-autre", False)):
        d = os.path.join(tr, nom)
        depot_matin(d)
        branche = branche_matin(d, "A", "RTD", "RTD", 1, x="a = 1\nb = 2\nc = 31\n")
        garde, mod.KIT = mod.KIT, (d if est_kit else tr)
        try:
            sorties.append(appel(["matin", d, JOUR_MATIN]) + (branche,))
        finally:
            mod.KIT = garde
    (code_k, s_k, b_k), (code_a, s_a, _) = sorties
    retard = "PLUGIN_RETARD=1 commit(s) de code du plugin fusionné(s) — la session ouverte ne les voit qu'après /reload-plugins\n"
    verifier("RTD1 (t) matin dit PLUGIN_RETARD= quand ses fusions touchent le code du kit chargé, rien pour un autre "
             "projet — mutant : la condition « projet est KIT » forcée à faux",
             code_k == 0 and s_k.endswith(retard + "MATIN 1 fusionnée(s) · 0 de côté\n") and "FUSIONNÉE %s" % b_k in s_k
             and code_a == 0 and "PLUGIN_RETARD" not in s_a, sorties)


def matin_u(tr):
    """(u) une branche qui laisse une page en attente : `matin` imprime son `ATTENTE=` avant `MATIN` (NPB1)."""
    d = os.path.join(tr, "u")
    depot_matin(d)
    attente = "50-x.html\thttps://claude.ai/artifact/x\t2026-10-01T01:00+02:00\n"
    branche_matin(d, "A", "NPB", "NPB", 1, modifs=lambda r: ecrire(os.path.join(r, "ctx", "artefacts", "en-attente"),
                                                                    attente))
    code, s = appel(["matin", d, JOUR_MATIN])
    verifier("NPB1 (b) matin imprime l'ATTENTE= qu'une branche de la nuit a laissée, avant MATIN — mutant : "
             "l'appel à dire_attentes retiré",
             code == 0 and s.endswith("ATTENTE=50-x.html https://claude.ai/artifact/x\nMATIN 1 fusionnée(s) · 0 de côté\n"),
             (code, s))


def tester_attentes_de_nuit():
    """NPB1 (a) : `clore` sous `VLP_NUIT=1` met en attente la page du chantier et la feuille ; sans, ni l'une ni l'autre."""
    vus = {}
    garde = os.environ.pop("VLP_NUIT", None)
    try:
        for nuit in (True, False):
            with tempfile.TemporaryDirectory() as te:
                ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                       "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : https://claude.ai/artifact/c\n"
                       "- **artefact feuille de route** : https://claude.ai/artifact/f\n\n"
                       "Lettres de fiche déjà prises : U (test).\n")
                ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé "
                       "| Dépend de |\n|---|---|---|---|---|\n| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
                ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
                for page, gabarit in (("50-u.html", "artefact-chantier.html"),
                                      ("feuille-de-route.html", "artefact-feuille-de-route.html")):
                    ecrire(os.path.join(te, "ctx", "artefacts", page),
                           open(os.path.join(ICI, "..", "templates", gabarit), encoding="utf-8").read())
                if nuit:
                    os.environ["VLP_NUIT"] = "1"
                try:
                    code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
                finally:
                    os.environ.pop("VLP_NUIT", None)
                vus[nuit] = (code, s, [[p, u] for p, u, _ in mod.lire_attente(os.path.join(te, "ctx", "artefacts"))])
    finally:
        if garde is not None:
            os.environ["VLP_NUIT"] = garde
    verifier("NPB1 (a) clore sous VLP_NUIT=1 met en attente la page du chantier et la feuille, et le dit ; sans la "
             "nuit, rien — mutant : la garde VLP_NUIT forcée à faux",
             vus[True][0] == 0 and vus[True][2] == [["50-u.html", "https://claude.ai/artifact/c"],
                                                     ["feuille-de-route.html", "https://claude.ai/artifact/f"]]
             and "ATTENTE 50-u.html — https://claude.ai/artifact/c\n" in vus[True][1]
             and vus[False][0] == 0 and vus[False][2] == [], vus)


groupe(tester_attentes_de_nuit)


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
                        matin_n_a, matin_n_b, matin_n_c, matin_n_d, matin_n_e, matin_n_f, matin_r, matin_s, matin_t, matin_u):
                cas(tr)
    finally:
        for k, v in gardes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


groupe(tester_matin)


def tester_ouverts():
    """NUI21 : `ouverts` — la marque d'ouverture, sans CLOS ni Pause ; `--rev` lit un commit, pas l'arbre."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — ouverts n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        d = os.path.join(tr, "ou")
        os.makedirs(d)
        ecrire(os.path.join(d, "CHANTIER.md"), "- **alias** : ou\n- **contexte** : ctx/\n")
        for n in ("a", "b", "c"):
            ecrire(os.path.join(d, "ctx", n + ".md"), "# Chantier %s — x\n\n## %s1 [ ] — f\n" % (n.upper(), n.upper()))
        code0, s0 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT % "2026-10-03" + "\n\n## B1 [ ] — f\n")
        code1, s1 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT % "2026-10-03" + "\n" + mod.CLOS_LIGNE % "2026-10-04" + "\n")
        code2, s2 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT % "2026-10-03" + "\n" + mod.PAUSE_LIGNE % ("2026-10-04", "attend") + "\n")
        code3, s3 = appel(["ouverts", d])
        ecrire(os.path.join(d, "ctx", "b.md"), "# Chantier B — x\n\n" + OUVERT % "2026-10-03" + "\n")
        git_matin(d, "init", "-q", "-b", "main")
        git_matin(d, "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
        git_matin(d, "checkout", "-q", "-b", "autre")
        ecrire(os.path.join(d, "ctx", "c.md"), "# Chantier C — x\n\n" + OUVERT % "2026-10-03" + "\n")
        git_matin(d, "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c ouvert")
        code4, s4 = appel(["ouverts", d, "--rev", "main"])
        code5, s5 = appel(["ouverts", d, "--rev", "autre"])
        code6, s6 = appel(["ouverts", d])
        code7, s7 = appel(["ouverts", d, "--rev", "nexistepas"])
        git_matin(d, "checkout", "-q", "main")
        code8, s8 = appel(["ouverts", os.path.join(tr, "vide")])
    verifier("NUI21 ouverts : sans marque → OUVERTS=0 ; marqué → 1 ; + CLOS → 0 ; + Pause → 0 ; --rev lit le commit, "
             "un fichier marqué sur l'autre branche est absent de main — mutants : la Pause ouvre, --rev lit l'arbre",
             (code0, s0) == (0, "OUVERTS=0\n") and s1 == "OUVERT ctx/b.md\n" and s2 == "OUVERTS=0\n"
             and s3 == "OUVERTS=0\n" and s4 == "OUVERT ctx/b.md\n"
             and s5 == "OUVERT ctx/b.md\nOUVERT ctx/c.md\n" and s6 == s5
             and (code1, code2, code3, code4, code5, code6) == (0,) * 6,
             "\n".join((s0, s1, s2, s3, s4, s5, s6)))
    verifier("NUI21 ouverts : un dossier sans CHANTIER.md, un --rev inconnu → GARDE et code 1, jamais un traceback",
             code7 == 1 and s7.startswith("GARDE: révision inconnue")
             and code8 == 1 and s8.startswith("GARDE: pas de CHANTIER.md"), s7 + s8)


OUVERT = mod.OUVERT_LIGNE
groupe(tester_ouverts)


def tester_blobs_git():
    """VIT3 : `textes_contexte` avec `rev` lit en un `git cat-file --batch` ce que l'ancien lecteur — un `git show` par
    fichier — lisait, au caractère près : CRLF, `\\r` seul, accents, fin sans LF, et un dossier en `.md` ; une entrée
    absente ou qui n'est pas un blob ne décale pas la suivante."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — blobs_git n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        d = os.path.join(tr, "bl")
        os.makedirs(os.path.join(d, "ctx", "d.md"))
        for nom, octets in (("CHANTIER.md", b"- **contexte** : ctx/\n"), ("ctx/a.md", b"# Chantier A\r\nligne\r\n"),
                            ("ctx/b é.md", "# Chantier B — été\nfin sans LF".encode("utf-8")),
                            ("ctx/c.md", b"un\rdeux\n\n"), ("ctx/d.md/x.txt", b"x\n")):
            with open(os.path.join(d, nom), "wb") as f:
                f.write(octets)
        git_matin(d, "init", "-q")
        git_matin(d, "-c", "core.autocrlf=false", "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")

        def ancien(chemin):
            """L'ancien lecteur : un `git show` par fichier."""
            code, t = mod.git_texte(["show", "HEAD:./" + chemin], d)
            return t.split("\n") if code == 0 else []
        nouveau = mod.textes_contexte(d, "HEAD")
        anciens = [ancien(c) for c, _ in nouveau]
        lus = mod.blobs_git(["HEAD:./ctx/a.md", "HEAD:./ctx/absent.md", "HEAD:./ctx/d.md", "HEAD:./ctx/c.md"], d)
    verifier("VIT3 : textes_contexte --rev égale l'ancien lecteur sur 3 fichiers et un dossier en .md (CRLF, \\r, accents, "
             "fin sans LF)", [c for c, _ in nouveau] == ["ctx/a.md", "ctx/b é.md", "ctx/c.md", "ctx/d.md"]
             and [l for _, l in nouveau] == anciens and nouveau[0][1] == ["# Chantier A", "ligne", ""]
             and nouveau[1][1] == ["# Chantier B — été", "fin sans LF"], (nouveau, anciens))
    verifier("VIT3 : blobs_git — absent et dossier rendent None, sans décaler l'entrée suivante — mutant : sauter le LF "
             "d'après le contenu", lus == ["# Chantier A\nligne\n", None, None, "un\ndeux\n\n"], lus)


groupe(tester_blobs_git)


def tester_courant_de():
    """NUI22 : `courant_de`, seul lecteur du chantier du dossier — post-it, branche, principale, ancienne ligne."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — courant_de n'est pas testé")
        return

    def courant(dossier):
        code, s = appel(["carte", dossier])
        ligne = next((l for l in s.split("\n") if l.startswith(("COURANT=", "GARDE:"))), s)
        return code, ligne

    def chantier(lettre, *marques):
        return "# Chantier %s — x\n\n%s\n\n## %s1 [ ] — f\n" % (lettre, "\n".join(marques), lettre)

    signe = ("-c", "user.name=t", "-c", "user.email=t@t")
    with tempfile.TemporaryDirectory() as tr:
        d, wt = os.path.join(tr, "cd"), os.path.join(tr, "wt")
        ecrire(os.path.join(d, "CHANTIER.md"), "- **alias** : cd\n- **contexte** : ctx/\n")
        ecrire(os.path.join(d, "ctx", "a.md"), chantier("A", OUVERT % "2026-10-03"))
        ecrire(os.path.join(d, "ctx", "c.md"), chantier("C", OUVERT % "2026-10-01", mod.CLOS_LIGNE % "2026-10-02"))
        git_matin(d, "init", "-q", "-b", "main")
        git_matin(d, "add", "-A")
        git_matin(d, *signe, "commit", "-q", "-m", "base")
        git_matin(d, "worktree", "add", "-q", "-b", "wt", wt)
        a_wt, a_main = courant(wt), courant(d)
        ecrire(os.path.join(wt, "ctx", "b.md"), chantier("B", OUVERT % "2026-10-03"))
        b_wt, b_main = courant(wt), courant(d)
        git_matin(wt, "add", "-A")
        git_matin(wt, *signe, "commit", "-q", "-m", "b ouvert")
        b_rev = mod.de_cote(d, "wt")
        postit = mod.postit(d)
        ecrire(postit, "ctx/c.md\n")
        c_clos = courant(d)
        ecrire(os.path.join(d, "ctx", "e.md"), chantier("E", OUVERT % "2026-10-03"))
        os.remove(postit)
        c_deux = courant(d)
        ecrire(postit, "ctx/e.md\n")
        c_postit = courant(d)
        git_matin(d, "worktree", "remove", "--force", wt)
        v = os.path.join(tr, "vieux")
        ecrire(os.path.join(v, "CHANTIER.md"),
               "- **contexte** : ctx/\n")
        ecrire(os.path.join(v, "ctx", "x.md"), ouvert("# Chantier X — x\n\n## X1 [ ] — f\n"))
        d_vieux = courant(v)
    verifier("NUI22 (a, b) courant_de : un worktree n'hérite pas du chantier de main, il voit le sien ; main inchangé ; "
             "de_cote lit la branche — mutant : la règle 2 garde les hérités",
             a_wt == (0, "COURANT=aucun") and a_main == (0, "COURANT=ctx/a.md")
             and b_wt == (0, "COURANT=ctx/b.md") and b_main == (0, "COURANT=ctx/a.md") and b_rev == "ctx/b.md",
             repr((a_wt, a_main, b_wt, b_main, b_rev)))
    verifier("NUI22 (c, d) courant_de : post-it sur un clos ignoré, sur un ouvert suivi ; deux ouverts sans post-it → "
             "GARDE ; projet sans marque → l'ancienne ligne de CHANTIER.md",
             c_clos == (0, "COURANT=ctx/a.md") and c_deux[0] == 1
             and c_deux[1] == "GARDE: plusieurs chantiers ouverts : ctx/a.md, ctx/e.md"
             and c_postit == (0, "COURANT=ctx/e.md") and d_vieux == (0, "COURANT=ctx/x.md"),
             repr((c_clos, c_deux, c_postit, d_vieux)))


groupe(tester_courant_de)


def tester_ouvrir_marque():
    """NUI23 : `ouvrir` pose la marque et le post-it ; un worktree ouvre le sien sans la page de main ; `clore`
    efface le post-it ; un 2e chantier dans le même dossier est refusé."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — ouvrir et clore par la marque ne sont pas testés")
        return
    signe = ("-c", "user.name=t", "-c", "user.email=t@t")
    with tempfile.TemporaryDirectory() as tr:
        d, wt = os.path.join(tr, "om"), os.path.join(tr, "wt")
        ecrire(os.path.join(d, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : https://exemple/nui\n\n"
               "Lettres de fiche déjà prises : N (nuit), P (par).\n")
        ecrire(os.path.join(d, "ctx", "50-nui.md"), ouvert("# Chantier N — nuit\n\n" + OUVERT % "2026-10-03" + "\n\n## N1 [ ] — a\n"))
        ecrire(os.path.join(d, "ctx", "51-par.md"), "# Chantier P — par\n\n**Fait.** Rien.\n\n## P1 [x] — a\n")
        git_matin(d, "init", "-q", "-b", "main")
        git_matin(d, "add", "-A")
        git_matin(d, *signe, "commit", "-q", "-m", "base")
        git_matin(d, "worktree", "add", "-q", "-b", "par", wt)
        code1, s1 = appel(["ouvrir", wt, "--fiches", "ctx/51-par.md", "--titre", "Par"])
        code1b, s1b = appel(["ouvrir", wt, "--fiches", "ctx/51-par.md", "--titre", "Par"])
        carte_par = mod.lire(os.path.join(wt, "CHANTIER.md"))
        par = mod.lire(os.path.join(wt, "ctx", "51-par.md"))
        p_wt = mod.postit(wt) or ""
        nomme = mod.lire(p_wt).strip() if os.path.isfile(p_wt) else None
        ouverts_avant = mod.ouverts(wt)
        code2, s2 = appel(["clore", wt, "--livre", "fini", "--date", "2026-10-04"])
        postit_reste = os.path.isfile(p_wt)
        ouverts_apres = mod.ouverts(wt)
        ecrire(os.path.join(d, "ctx", "52-q.md"), "# Chantier Q — q\n\n## Q1 [ ] — a\n")
        code3, s3 = appel(["ouvrir", d, "--fiches", "ctx/52-q.md", "--titre", "Q"])
        git_matin(d, "worktree", "remove", "--force", wt)
    verifier("NUI23 ouvrir : dans un worktree tiré de main où NUI est ouvert, PAR s'ouvre, artefact « aucun », une "
             "seule marque même relancé, post-it écrit — mutant : l'artefact toujours repris",
             (code1, code1b) == (0, 0) and "- **artefact du chantier** : aucun\n" in carte_par
             and par.count("**Ouvert.**") == 1 and nomme == "ctx/51-par.md"
             and ouverts_avant == ["ctx/50-nui.md", "ctx/51-par.md"], s1 + s1b + carte_par + par)
    verifier("NUI23 clore : post-it effacé, PAR hors des ouverts ; ouvrir un 2e chantier dans le dossier → GARDE",
             code2 == 0 and not postit_reste and ouverts_apres == ["ctx/50-nui.md"]
             and code3 == 1 and s3.startswith("GARDE: un chantier est déjà ouvert : ctx/50-nui.md"),
             "\n".join((s2, repr(ouverts_apres), s3)))


groupe(tester_ouvrir_marque)


def tester_nui30_marque():
    """NUI30 : `niveau --ecrire` pose la marque d'un projet à la Cairn (5 fichiers sans CLOS, un courant), datée de son
    commit d'ouverture ; rejoué, rien ; `pause` la pose, `ouvrir` la lève."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — la marque de niveau et la pause ne sont pas testées")
        return

    def courant(dossier):
        return next((l for l in appel(["carte", dossier])[1].split("\n") if l.startswith(("COURANT=", "GARDE:"))), "")

    with tempfile.TemporaryDirectory() as tr:
        d, sans_git, rien = os.path.join(tr, "ca"), os.path.join(tr, "sg"), os.path.join(tr, "rien")
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : ctx/59-f.md (F1..F1)\n- **artefact du chantier** : aucun\n")
        for n, code in (("22-a", "A"), ("23-b", "B"), ("34-h", "H"), ("58-m", "M"), ("59-f", "F")):
            ecrire(os.path.join(d, "ctx", n + ".md"), "# Chantier %s — x\n\n## %s1 [ ] — f\n" % (code, code))
        ecrire(os.path.join(d, "ctx", "21-z.md"), "# Chantier Z — x\n\n" + mod.CLOS_LIGNE % "2026-09-01" + "\n")
        for p_ in (d, sans_git, rien):
            ecrire(os.path.join(p_, "ctx", "00-INDEX.md"), "# Index\n")
        git_matin(d, "init", "-q", "-b", "main")
        git_matin(d, "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--date=2026-09-20T12:00:00",
                  "-m", "Chantier F ouvert : x")
        avant = courant(d)
        _, s0 = appel(["niveau", d])
        _, s1 = appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        apres, ouverts1, f1 = courant(d), appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        carte1 = mod.lire(os.path.join(d, "CHANTIER.md"))
        _, s2 = appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        f2 = mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code3, s3 = appel(["pause", os.path.join(d, "ctx", "34-h.md"), "en pause le soir même", "--date", "2026-09-20"])
        code4, s4 = appel(["pause", os.path.join(d, "ctx", "34-h.md"), "encore"])
        code5, s5 = appel(["pause", os.path.join(d, "ctx", "59-f.md"), "attend"])
        ouverts2, f5 = appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code6, s6 = appel(["ouvrir", d, "--fiches", "ctx/59-f.md", "--titre", "x"])
        ouverts3, f6 = appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code7, s7 = appel(["pause", os.path.join(d, "ctx", "21-z.md"), "x"])
        code8, s8 = appel(["pause", os.path.join(d, "ctx", "absent.md"), "x"])
        h3 = mod.lire(os.path.join(d, "ctx", "34-h.md"))
        ecrire(os.path.join(sans_git, "CHANTIER.md"), "- **contexte** : ctx/\n- **fichier de fiches courant** : ctx/9-s.md\n")
        ecrire(os.path.join(sans_git, "ctx", "9-s.md"), "# Chantier S — x\n\n## S1 [ ] — f\n")
        _, s9 = appel(["niveau", sans_git, "--ecrire", "--date", "2026-10-08"])
        ecrire(os.path.join(rien, "CHANTIER.md"), "- **contexte** : ctx/\n")
        ecrire(os.path.join(rien, "ctx", "9-s.md"), "# Chantier S — x\n\n## S1 [ ] — f\n")
        _, s10 = appel(["niveau", rien, "--ecrire", "--date", "2026-10-08"])
    marque = "**Ouvert.** le 2026-09-20."
    verifier("NUI30 niveau : projet à la Cairn — ÉCART sans --ecrire ; --ecrire pose la marque du commit d'ouverture sous "
             "le titre ; rejoué → rien écrit — mutant : `migre` ignoré, la marque doublée",
             "ÉCART: marque: ctx/59-f.md sans **Ouvert.**" in s0
             and "CORRIGÉ: marque: **Ouvert.** le 2026-09-20 sur ctx/59-f.md — son commit d'ouverture" in s1
             and f1.startswith("# Chantier F — x\n\n" + marque + "\n\n## F1") and ouverts1 == "OUVERT ctx/59-f.md\n"
             and "marque" not in s2 and f2 == f1,
             "\n".join((avant, apres, s0, s1, s2, f1)))
    verifier("NUI31 niveau : la ligne « fichier de fiches courant » n'est plus lue (COURANT=aucun avant la marque) ; "
             "gardée sans --ecrire, retirée après la marque, le reste de CHANTIER.md intact ; rejoué → rien — mutant : "
             "retirée avant que la marque ne soit posée",
             avant == "COURANT=aucun" and apres == "COURANT=ctx/59-f.md"
             and "ÉCART: ligne: CHANTIER.md:3 — « fichier de fiches courant » n'est plus lue (NUI31) — gardée tant que "
                 "la marque d'ouverture manque" in s0
             and "CORRIGÉ: ligne: « fichier de fiches courant » retirée de CHANTIER.md:3" in s1
             and carte1 == "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : aucun\n"
             and "ligne:" not in s2,
             "\n".join((avant, apres, s0, s1, s2, carte1)))
    verifier("NUI30 niveau : sans commit d'ouverture, la date de l'appel, dite, puis la ligne retirée ; sans ligne → rien",
             "CORRIGÉ: marque: **Ouvert.** le 2026-10-08 sur ctx/9-s.md — date de l'appel, aucun commit « Chantier S "
             "ouvert »" in s9 and "CORRIGÉ: ligne:" in s9 and "marque" not in s10 and "ligne:" not in s10, s9 + s10)
    verifier("NUI30 pause : posée sous le titre, le chantier sort des ouverts ; en double, sur un clos, introuvable → GARDE ; "
             "ouvrir la lève — mutant : lever_pause ne rend rien",
             (code3, s3) == (0, "PAUSE %s le 2026-09-20\n" % os.path.join(d, "ctx", "34-h.md").replace("\\", "/"))
             and h3.startswith("# Chantier H — x\n\n**Pause.** le 2026-09-20 — en pause le soir même\n\n## H1")
             and code4 == 1 and "porte déjà **Pause.**" in s4 and code5 == 0 and ouverts2 == "OUVERTS=0\n"
             and "**Pause.**" in f5 and code6 == 0 and " · pause levée" in s6 and "**Pause.**" not in f6
             and f6.startswith("# Chantier F — x\n\n" + marque + "\n\n## F1") and ouverts3 == "OUVERT ctx/59-f.md\n"
             and code7 == 1 and "porte déjà **CLOS**" in s7 and code8 == 1 and s8.startswith("GARDE: fichier de fiches"),
             "\n".join((s3, s4, s5, ouverts2, s6, ouverts3, f6, s7, s8, h3)))


groupe(tester_nui30_marque)


def tester_wip_de_cote():
    """NUI24 : une pointe WIP sans chantier n'est jamais fusionnée ; une branche qui hérite du chantier ouvert de main
    sans en ajouter reste fusionnable."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — la pointe WIP n'est pas testée")
        return
    with tempfile.TemporaryDirectory() as tr:
        d = os.path.join(tr, "w")
        depot_matin(d)
        noms = {}
        for canal, code, sujet in (("A", "WIP", mod.WIP_SUJET % ("WIP", "découpage coupé")), ("B", "HER", "HER1 : her")):
            noms[code] = "nuit/%s-%s-%s" % (JOUR_MATIN, canal, code)
            git_matin(d, "switch", "-q", "-c", noms[code], "main")
            ecrire(os.path.join(d, "scripts", "%s.py" % code.lower()), "x = 1\n")
            commit_matin(d, sujet, 1)
            git_matin(d, "switch", "-q", "main")
        etat_wip, etat_her = mod.etat_branche_nuit(d, noms["WIP"]), mod.etat_branche_nuit(d, noms["HER"])
        code, s = appel(["matin", d, JOUR_MATIN])
        wip_fusionne = code_git(d, "merge-base", "--is-ancestor", noms["WIP"], "main") == 0
    verifier("NUI24 : pointe WIP, chantier aucun → DE CÔTÉ, jamais fusionnée ; héritière de LOC ouvert → fusionnable — "
             "mutant : la pointe WIP n'est plus lue",
             etat_wip == ("cote", "WIP WIP mis de côté : découpage coupé") and etat_her == ("fusion", None)
             and "DE CÔTÉ %s — WIP WIP mis de côté : découpage coupé\n" % noms["WIP"] in s and not wip_fusionne,
             repr((etat_wip, etat_her, wip_fusionne)) + "\n" + s)


groupe(tester_wip_de_cote)


def tester_fusionner():
    """NUI26 : `vlp.py fusionner <projet> <branche>`, la fusion du jour par le chemin de `matin` — un worktree qui clôt
    le chantier de main le libère ; un worktree qui ouvre puis clôt PAR laisse à main le sien ; six refus et `DÉJÀ`."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — fusionner n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        d, wt = os.path.join(tr, "f"), os.path.join(tr, "wt-clot")
        depot_matin(d)
        git_matin(d, "worktree", "add", "-q", "-b", "clot-loc", wt, "main")
        postit = mod.postit(wt)
        assert postit
        ecrire(postit, "ctx/40-loc.md\n")       # le worktree reprend le chantier de main : son post-it le nomme
        etat_wt = os.path.join(wt, "ctx", "08-etat.md")    # la clôture ôte sa ligne de la TODO (cloture.md, étape 1)
        ecrire(etat_wt, "".join(l for l in lire(etat_wt).splitlines(True) if not l.startswith("| 79 |")))
        code_clore, s_clore = appel(["clore", wt, "--livre", "LOC livré", "--date", JOUR_MATIN])
        commit_matin(wt, "Chantier LOC clos", 1)
        code, s = appel(["fusionner", d, "clot-loc"])
        carte_, courant_a = mod.lignes_de(os.path.join(d, "CHANTIER.md")), mod.courant_de(d)
        ecrire(os.path.join(d, "ctx", "50-neo.md"), "# Chantier NEO — Neuf\n\n## NEO1 [ ] — a\n")
        code_ouvrir, s_ouvrir = appel(["ouvrir", d, "--fiches", "ctx/50-neo.md", "--titre", "Neuf"])
        neo = lire(os.path.join(d, "ctx", "50-neo.md"))
    verifier("NUI26 (a) un worktree clôt LOC, le chantier de main : clore dit la ligne FUSIONNER ; fusionner depuis main "
             "→ FUSIONNÉE, commit « Fusion : clot-loc », main à aucun (courant et artefact) ; ouvrir passe ensuite ; "
             "la ligne 79 ôtée de la TODO par la clôture ne fait plus s'arrêter la feuille (dette NUI, 2026-10-08) — "
             "mutant : l'exception **CLOS** retirée",
             code_clore == 0 and ('FUSIONNER depuis %s : ' % d.replace("\\", "/")) in s_clore.replace("\\", "/")
             and ' fusionner "' in s_clore and s_clore.rstrip().endswith(" clot-loc")
             and code == 0 and s == "FUSIONNÉE clot-loc\n"
             and courant_a is None and mod.champ(carte_, "artefact du chantier") == "aucun"
             and code_ouvrir == 0 and "**Ouvert.**" in neo,
             (code_clore, s_clore, code, s, carte_, code_ouvrir, s_ouvrir))

    with tempfile.TemporaryDirectory() as tr:
        d, vide = os.path.join(tr, "g"), os.path.join(tr, "vide")
        depot_matin(d)
        os.makedirs(vide)

        def branche(nom, fichier, corps, carte_aucun):
            """`nom`, depuis main, dans un worktree : `fichier` écrit avec `corps` ; `carte_aucun` : CHANTIER.md à
            `aucun` et la lettre PAR ajoutée, comme `clore` l'écrit."""
            w = os.path.join(tr, "wt-" + nom)
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
            ecrire(os.path.join(w, fichier), corps)
            if carte_aucun:
                chemin = os.path.join(w, "CHANTIER.md")
                c = re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(chemin))
                ecrire(chemin, c.replace(". Un nouveau chantier", ", PAR (Deux chantiers). Un nouveau chantier"))
            commit_matin(w, nom, 2)

        branche("par", "ctx/60-par.md", "# Chantier PAR — Deux\n\n%s\n\n**CLOS** le %s.\n\n## PAR1 [x] — a\n"
                % (OUVERT_DU_JOUR, JOUR_MATIN), True)
        branche("ouvre", "ctx/70-ouv.md", "# Chantier OUV — Ouvert\n\n%s\n\n## OUV1 [ ] — a\n" % OUVERT_DU_JOUR, False)
        refus = [appel(["fusionner", vide, "par"])]
        ecrire(os.path.join(d, "sous", "CHANTIER.md"), "# C\n")
        refus.append(appel(["fusionner", os.path.join(d, "sous"), "par"]))
        shutil.rmtree(os.path.join(d, "sous"))
        git_matin(d, "switch", "-q", "--detach")
        refus.append(appel(["fusionner", d, "par"]))
        git_matin(d, "switch", "-q", "main")
        git_matin(d, "merge", "-q", "--no-ff", "--no-commit", "ouvre")
        refus.append(appel(["fusionner", d, "par"]))
        git_matin(d, "merge", "--abort")
        ecrire(os.path.join(d, "scripts", "x.py"), "sale\n")
        refus.append(appel(["fusionner", d, "par"]))
        git_matin(d, "checkout", "-q", "--", ".")
        refus.append(appel(["fusionner", d, "nulle-part"]))
        refus.append(appel(["fusionner", d, "ouvre"]))
        ouvre_fusionne = code_git(d, "merge-base", "--is-ancestor", "ouvre", "main") == 0
        code, s = appel(["fusionner", d, "par"])
        carte_, courant_c = mod.lignes_de(os.path.join(d, "CHANTIER.md")), mod.courant_de(d)
        sujet = git_matin(d, "log", "-1", "--format=%s").strip()
        deja = appel(["fusionner", d, "par"])
    attendu = ("GARDE: pas de CHANTIER.md dans", "n'est pas la racine d'un dépôt Git", "GARDE: HEAD détachée",
               "GARDE: une fusion est déjà en cours (MERGE_HEAD)", "GARDE: arbre pas propre (1 chemin(s))",
               "GARDE: branche absente : nulle-part", "GARDE: ouvre garde un chantier ouvert (ctx/70-ouv.md) — clos-le")
    verifier("NUI26 (b) six refus, un cas chacun (non équipé, hors racine, HEAD détachée, MERGE_HEAD, arbre sale, branche "
             "absente) et la branche qui garde un chantier ouvert — sort 1, rien fusionné",
             len(refus) == len(attendu) and all(c == 1 and a in r and "rien fusionné" in r for (c, r), a in zip(refus, attendu))
             and not ouvre_fusionne, refus)
    verifier("NUI26 (c) un worktree ouvre puis clôt PAR : fusionner → main garde LOC (courant et artefact), PAR ajouté aux "
             "lettres, commit « Fusion : par » ; rejoué → DÉJÀ par, sort 0",
             code == 0 and s == "FUSIONNÉE par\n" and sujet == "Fusion : par"
             and courant_c == "ctx/40-loc.md"
             and mod.champ(carte_, "artefact du chantier") == "https://claude.ai/artifact/LOC"
             and mod.lettres_prises(carte_) == ["E", "ENQ", "PAR"] and deja == (0, "DÉJÀ par\n"),
             (code, s, sujet, carte_, deja))


groupe(tester_fusionner)


def tester_lettres_doublon():
    """NUI27 : un code pris deux fois n'est plus avalé — à la fusion, même lettre et titres différents → `GARDE:` avant
    toute écriture, même entrée → rien ; `ouvrir` refuse un code déjà ouvert dans un autre worktree, pas le sien hérité."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — les lettres en double ne sont pas testées")
        return
    with tempfile.TemporaryDirectory() as tr:
        d = os.path.join(tr, "l")
        depot_matin(d)

        def lettre(nom, entree):
            """`nom`, depuis main, dans un worktree : `entree` ajoutée à la liste des lettres et CHANTIER.md à `aucun`,
            comme `clore` l'écrit — sinon la branche garde LOC ouvert et `fusionner` la met de côté —, puis commitée."""
            w = os.path.join(tr, "wt-" + nom)
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
            chemin = os.path.join(w, "CHANTIER.md")
            c = re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(chemin))
            ecrire(chemin, c.replace(". Un nouveau chantier", ", %s. Un nouveau chantier" % entree))
            commit_matin(w, nom, 3)

        lettre("pa", "PAR (A)")
        lettre("pb", "PAR (B)")
        lettre("pc", "`PAR` (A)")
        code_a, s_a = appel(["fusionner", d, "pa"])
        tete = git_matin(d, "rev-parse", "HEAD")
        code_b, s_b = appel(["fusionner", d, "pb"])
        propre = git_matin(d, "status", "--porcelain") == "" and git_matin(d, "rev-parse", "HEAD") == tete
        en_cours = code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
        code_c, s_c = appel(["fusionner", d, "pc"])
        lettres = mod.lettres_prises(mod.lignes_de(os.path.join(d, "CHANTIER.md")))
    verifier("NUI27 (a) PAR (A) fusionné, puis PAR (B) → GARDE: le code PAR est pris deux fois, sort 1, rien écrit "
             "(status vide, HEAD immobile, pas de MERGE_HEAD) — mutant : le saut silencieux remis",
             (code_a, s_a) == (0, "FUSIONNÉE pa\n") and code_b == 1
             and s_b.startswith("GARDE: le code PAR est pris deux fois : « A » et « B »") and propre and not en_cours,
             (code_a, s_a, code_b, s_b, propre, en_cours))
    verifier("NUI27 (b) la même entrée des deux côtés, aux backticks près → fusion sans garde, PAR compté une fois",
             (code_c, s_c) == (0, "FUSIONNÉE pc\n") and lettres == ["E", "ENQ", "PAR"], (code_c, s_c, lettres))

    with tempfile.TemporaryDirectory() as tr:
        d, wz, wh = os.path.join(tr, "o"), os.path.join(tr, "wt-zed"), os.path.join(tr, "wt-her")
        depot_matin(d)
        loc = os.path.join(d, "ctx", "40-loc.md")      # main libre : LOC sans sa marque, l'artefact à aucun
        ecrire(loc, lire(loc).replace("\n%s\n" % OUVERT, ""))
        carte = os.path.join(d, "CHANTIER.md")
        ecrire(carte, re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(carte)))
        commit_matin(d, "main libre", 3)
        git_matin(d, "worktree", "add", "-q", "-b", "zed", wz, "main")
        ecrire(os.path.join(wz, "ctx", "80-zed.md"), "# Chantier ZED — Un\n\n%s\n\n## ZED1 [ ] — a\n" % OUVERT_DU_JOUR)
        bis = os.path.join(d, "ctx", "81-zed.md")
        ecrire(bis, "# Chantier ZED — Bis\n\n## ZED1 [ ] — a\n")
        carte_avant = lire(os.path.join(d, "CHANTIER.md"))
        code_z, s_z = appel(["ouvrir", d, "--fiches", "ctx/81-zed.md", "--titre", "Bis"])
        intact = lire(os.path.join(d, "CHANTIER.md")) == carte_avant and "**Ouvert.**" not in lire(bis)
        os.remove(bis)
        ecrire(os.path.join(d, "ctx", "82-her.md"), "# Chantier HER — Hérité\n\n%s\n\n## HER1 [ ] — a\n" % OUVERT_DU_JOUR)
        commit_matin(d, "HER ouvert", 4)
        git_matin(d, "worktree", "add", "-q", "--detach", wh, "main")
        code_h, s_h = appel(["ouvrir", d, "--fiches", "ctx/82-her.md", "--titre", "Hérité"])
    verifier("NUI27 (c) ouvrir ZED quand un autre worktree a ZED ouvert → GARDE: déjà ouvert ailleurs, sort 1, rien écrit ; "
             "le même fichier hérité par un worktree détaché ne bloque pas sa réouverture",
             code_z == 1 and s_z.startswith("GARDE: le code ZED est déjà ouvert ailleurs : ctx/80-zed.md dans ")
             and "wt-zed" in s_z and intact and code_h == 0,
             (code_z, s_z, intact, code_h, s_h))


groupe(tester_lettres_doublon)


def tester_ailleurs():
    """NUI28 : `carte` nomme le chantier de chaque autre worktree (`AILLEURS=`), jamais le sien, ni un worktree sans
    chantier ; `niveau` ne compte pas d'écart de page à un chantier qui joue dans un autre worktree que le principal."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — AILLEURS= n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        d = os.path.join(tr, "m")
        depot_matin(d)
        loc = os.path.join(d, "ctx", "40-loc.md")      # main libre : LOC sans sa marque, l'artefact à aucun
        ecrire(loc, lire(loc).replace("\n%s\n" % OUVERT, ""))
        carte = os.path.join(d, "CHANTIER.md")
        ecrire(carte, re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(carte)))
        ecrire(os.path.join(d, "ctx", "80-maa.md"), "# Chantier MAA — Main\n\n%s\n\n## MAA1 [ ] — a\n" % OUVERT_DU_JOUR)
        commit_matin(d, "MAA ouvert", 3)
        dossiers = {"m": d}
        for nom, code in (("a", "WZA"), ("b", "WZB"), ("c", None)):
            w = dossiers[nom] = os.path.join(tr, "wt-" + nom)
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
            if code:
                ecrire(os.path.join(w, "ctx", "81-%s.md" % nom), "# Chantier %s — %s\n\n%s\n\n## %s1 [ ] — a\n"
                       % (code, nom, OUVERT_DU_JOUR, code))
        vus = {}
        for nom, w in dossiers.items():
            s = appel(["carte", w])[1]
            vus[nom] = sorted((l.split()[0][len("AILLEURS="):], os.path.basename(l.split(None, 1)[1].rstrip("/")))
                              for l in s.splitlines() if l.startswith("AILLEURS="))
    attendu = {"m": [("WZA", "wt-a"), ("WZB", "wt-b")], "a": [("MAA", "m"), ("WZB", "wt-b")],
               "b": [("MAA", "m"), ("WZA", "wt-a")], "c": [("MAA", "m"), ("WZA", "wt-a"), ("WZB", "wt-b")]}
    verifier("NUI28 (a) main + deux worktrees à chantier + un sans : la carte de chacun nomme les autres chantiers, "
             "jamais le sien ; le worktree sans chantier n'est nommé par personne — mutant : le sien non filtré",
             vus == attendu, vus)

    with tempfile.TemporaryDirectory() as tr:
        d, wl = os.path.join(tr, "n"), os.path.join(tr, "wt-l")
        depot_matin(d)
        _, seul = appel(["niveau", d])
        git_matin(d, "worktree", "add", "-q", "-b", "l", wl, "main")
        ecrire(mod.postit(wl), "ctx/40-loc.md\n")      # le worktree joue LOC : son post-it le nomme (NUI31)
        _, avec = appel(["niveau", d])
        _, dans = appel(["niveau", wl])
    verifier("NUI28 (b) niveau : LOC joué dans un worktree → « AILLEURS: page: LOC joue dans … », aucun ÉCART: page "
             "dans le principal ; sans worktree, ou lancé dans le worktree, la page se compte",
             "ÉCART: page:" in seul and "AILLEURS:" not in seul
             and "AILLEURS: page: LOC joue dans " in avec and "wt-l" in avec and "ÉCART: page:" not in avec
             and "AILLEURS:" not in dans,
             (seul, avec, dans))


groupe(tester_ailleurs)


# VIT15 — des sondes, une règle de comptage chacune. SONDES_ATTENDU : leurs comptes par ruff 0.16.10, seuils à zéro et
# `--preview` — complexité, branches, arguments, instructions, imbrication.
SONDES = '''def f_vide():
    pass


def f_if_elif_else(a):
    if a == 1:
        return 1
    elif a == 2:
        return 2
    else:
        return 3


def f_else_if(a):
    if a == 1:
        return 1
    else:
        if a == 2:
            return 2
    return 3


def f_boucles(a):
    for x in a:
        if x:
            break
    else:
        return 0
    while a:
        a = a[1:]
    else:
        pass
    return 1


def f_try_tout(a):
    try:
        a()
    except ValueError:
        return 1
    except KeyError:
        return 2
    else:
        return 3
    finally:
        a()


def f_imbrique(a):
    with open(a) as fichier:
        for ligne in fichier:
            if ligne:
                while ligne:
                    try:
                        ligne = ligne[1:]
                    except IndexError:
                        pass
    return 0


def f_externe(a):
    """Une fonction imbriquée compte dans sa parente."""
    def interne(b):
        if b:
            return 1
        return 0
    if a:
        return interne(a)
    return 0


def f_args(a, _b, *args, c, _, __d, **kwargs):
    return a


class K:
    def m(self, a, b):
        return a

    @staticmethod
    def s(a, b):
        return a

    def autre(this, a):
        return a


def f_chaine(a):
    if a:
        def g(b):
            if b:
                for x in b:
                    if x:
                        return x
            return 0
        return g
    return None


def f_instr(a):
    """return et for : 0 ; global, import, del, raise, += : 1."""
    global ICI
    import os
    x = 1
    x += 1
    del x
    for y in a:
        print(y)
    if a:
        raise ValueError(os.sep)
    return a
'''

SONDES_MATCH = '''def f_match(a):
    match a:
        case 1:
            return 1
        case 2 | 3:
            return 2
        case _:
            return 0


def f_match_garde(a):
    match a:
        case [x] if x:
            if x:
                return 1
        case y:
            return y
'''

SONDES_ATTENDU = {
    "f_vide": [1, 0, 0, 1, 0], "f_if_elif_else": [3, 3, 1, 3, 1], "f_else_if": [3, 3, 1, 3, 2],
    "f_boucles": [4, 5, 1, 5, 2], "f_try_tout": [4, 4, 1, 9, 1], "f_imbrique": [5, 4, 1, 7, 5],
    "f_externe": [4, 1, 1, 4, 1], "f_externe.interne": [2, 1, 1, 1, 1], "f_args": [1, 0, 2, 0, 0],
    "K.m": [1, 0, 2, 0, 0], "K.s": [1, 0, 2, 0, 0], "K.autre": [1, 0, 1, 0, 0], "f_chaine": [6, 1, 1, 4, 4],
    "f_chaine.g": [4, 3, 1, 2, 0], "f_instr": [3, 2, 1, 9, 1],
    "f_match": [3, 3, 1, 4, 0], "f_match_garde": [3, 3, 1, 4, 1],
}

# La sortie JSON de ruff 0.16.10 sur SONDES, réduite aux clés que `sante.lire_ruff` lit et à quatre fonctions : deux
# imbriquées, et deux `PLR1702` sur la ligne 89.
RUFF_ENREGISTRE = [
    ("C901", 61, "`f_externe` is too complex (4 > 0)"),
    ("PLR0913", 61, "Too many arguments in function definition (1 > 0)"),
    ("PLR0912", 61, "Too many branches (1 > 0)"),
    ("PLR0915", 61, "Too many statements (4 > 0)"),
    ("C901", 63, "`interne` is too complex (2 > 0)"),
    ("PLR0913", 63, "Too many arguments in function definition (1 > 0)"),
    ("PLR0912", 63, "Too many branches (1 > 0)"),
    ("PLR0915", 63, "Too many statements (1 > 0)"),
    ("PLR1702", 64, "Too many nested blocks (1 > 0)"),
    ("PLR1702", 67, "Too many nested blocks (1 > 0)"),
    ("C901", 88, "`f_chaine` is too complex (6 > 0)"),
    ("PLR0913", 88, "Too many arguments in function definition (1 > 0)"),
    ("PLR0912", 88, "Too many branches (1 > 0)"),
    ("PLR0915", 88, "Too many statements (4 > 0)"),
    ("PLR1702", 89, "Too many nested blocks (1 > 0)"),
    ("PLR1702", 89, "Too many nested blocks (4 > 0)"),
    ("C901", 90, "`g` is too complex (4 > 0)"),
    ("PLR0913", 90, "Too many arguments in function definition (1 > 0)"),
    ("PLR0912", 90, "Too many branches (3 > 0)"),
    ("PLR0915", 90, "Too many statements (2 > 0)"),
]


def tester_sante_comptes():
    """VIT15 : par `ast`, les cinq comptes des sondes égalent ceux de ruff ; les docstrings sont vues ; l'empreinte ne
    voit pas les fins de ligne ; un nom en double devient `nom#2`."""
    import sante
    with tempfile.TemporaryDirectory() as ts:
        ecrire(os.path.join(ts, "sondes.py"), SONDES)
        ecrire(os.path.join(ts, "crlf.py"), SONDES.replace("\n", "\r\n"))
        ecrire(os.path.join(ts, "double.py"), "def f():\n    pass\n\n\ndef f():\n    return 1\n")
        fonctions = sante.mesurer_fichier(ts, os.path.join(ts, "sondes.py"))[0]
        crlf = sante.mesurer_fichier(ts, os.path.join(ts, "crlf.py"))[0]
        double = [f["fonction"] for f in sante.mesurer_fichier(ts, os.path.join(ts, "double.py"))[0]]
    comptes = {f["fonction"]: f["ast"] for f in fonctions}
    verifier("VIT15 (a) les cinq comptes ast des sondes égalent ceux de ruff 0.16.10 — elif et else-if, boucles et leur "
             "else, try complet, imbrication, fonction et classe imbriquées, arguments muets et de méthode, instructions "
             "à la Pylint ; docstrings vues ; même empreinte en CRLF ; un nom en double → f#2",
             comptes == {n: c for n, c in SONDES_ATTENDU.items() if not n.startswith("f_match")}
             and [f["fonction"] for f in fonctions if f["doc"]] == ["f_externe", "f_instr"]
             and [f["empreinte"] for f in crlf] == [f["empreinte"] for f in fonctions] and double == ["f", "f#2"],
             (comptes, double))
    if sys.version_info < (3, 10):
        print("SAUTÉ: Python < 3.10 — les sondes de `match` ne sont pas testées")
        return
    with tempfile.TemporaryDirectory() as ts:
        ecrire(os.path.join(ts, "choix.py"), SONDES_MATCH)
        choix = {f["fonction"]: f["ast"] for f in sante.mesurer_fichier(ts, os.path.join(ts, "choix.py"))[0]}
    verifier("VIT15 (a bis) match : une branche par case, le dernier gratuit en complexité s'il attrape tout, pas "
             "d'imbrication à lui", choix == {n: c for n, c in SONDES_ATTENDU.items() if n.startswith("f_match")}, choix)


def tester_sante_ruff():
    """VIT15 : le chemin ruff, sans dépendre de ruff — sa sortie JSON enregistrée se lit, ruff en échec laisse `ast`
    seul ; et ruff réel, s'il est installé, s'accorde à `ast`."""
    import sante
    with tempfile.TemporaryDirectory() as tr:
        chemin = os.path.join(tr, "sondes.py")
        ecrire(chemin, SONDES)
        fonctions, nombre = sante.mesurer_fichier(tr, chemin)
        for f in fonctions:
            f["ruff"] = [0] * len(sante.REGLES)
        donnees = [{"code": c, "filename": chemin, "location": {"row": r}, "message": m} for c, r, m in RUFF_ENREGISTRE]
        donnees.append({"code": "E501", "filename": chemin, "location": {"row": 61}, "message": "Line too long (99 > 88)"})
        donnees.append({"code": "C901", "filename": os.path.join(tr, "autre.py"), "location": {"row": 1},
                        "message": "`f_vide` is too complex (9 > 0)"})
        sante.lire_ruff(json.dumps(donnees), {sante.cle(chemin): sante.carte_lignes(fonctions, nombre)})
        echec = io.StringIO()
        apres, version = sante.mesurer(tr, [chemin], ([sys.executable, "-c", "import sys; sys.exit(3)"], "9.9"), echec)
        commande, reel = sante.trouver_ruff()
        code, s = appel(["sante", "--racine", tr, chemin]) if commande else (0, "")
    lus = {f["fonction"]: f["ruff"] for f in fonctions if any(f["ruff"])}
    verifier("VIT15 (b) la sortie JSON de ruff, enregistrée : un diagnostic va à la fonction la plus intérieure de sa "
             "ligne, le plus grand des deux PLR1702 de la ligne 89 gagne ; un autre code, un autre fichier ne comptent pas",
             lus == {n: SONDES_ATTENDU[n] for n in ("f_externe", "f_externe.interne", "f_chaine", "f_chaine.g")}, lus)
    verifier("VIT15 (c) ruff qui sort 3 → `RUFF ÉCHEC ruff sort 3`, puis les comptes ast seuls",
             version is None and echec.getvalue() == "RUFF ÉCHEC ruff sort 3 — comptes estimés (ast)\n"
             and len(apres) == 15 and all(f["ruff"] is None for f in apres), echec.getvalue())
    if commande is None:
        print("SAUTÉ: ruff absent — son chemin réel n'est pas testé")
        return
    verifier("VIT15 (c bis) ruff réel %s sur les sondes : ses comptes égalent ceux d'ast, 15/15" % reel,
             code == 0 and s.startswith("SANTE ruff %s · " % reel) and "AST=RUFF 15/15 fonctions\n" in s, s)


def tester_sante_cliquet():
    """VIT15 : le cliquet sur un faux kit, sans ruff — la base, ce qui empire, ce qui grandit sous le seuil, la fonction
    neuve, la docstring, les tests, le renommage et le déplacement, le verrou d'une amélioration, et la base qui ne se
    relâche que par `--forcer`."""
    def ifs(n, nom):
        """Une fonction documentée à `n` `if` : complexité n + 1, branches n, instructions n + 1."""
        corps = "".join("    if a == %d:\n        return %d\n" % (i, i) for i in range(n))
        return 'def %s(a):\n    """Des if."""\n%s    return a\n\n\n' % (nom, corps)

    def longue(n):
        """Un test sans docstring, de `n` instructions."""
        return "def test_long():\n%s    return 0\n\n\n" % "".join("    x%d = %d\n" % (i, i) for i in range(n))

    muette = "def muette(a):\n    return a\n"
    m = ifs(11, "grosse") + ifs(1, "petite") + muette
    tete = "CLIQUET sur ast, comptes estimés (sans ruff)\n"
    bilan = "CLIQUET %d fonctions · vieilles 4, dont touchées %d, renommées ou déplacées %d · neuves %d"
    with tempfile.TemporaryDirectory() as tc:
        base = os.path.join(tc, "scripts", "sante-base.json")

        def lancer(fichiers, *options):
            """Écrire `fichiers` sous `scripts/` (`{nom: texte}`, None efface), puis lancer `sante --sans-ruff`."""
            for nom, texte in fichiers.items():
                if texte is None:
                    os.remove(os.path.join(tc, "scripts", nom))
                else:
                    ecrire(os.path.join(tc, "scripts", nom), texte)
            return appel(["sante", "--racine", tc, "--sans-ruff"] + list(options))

        sans_base = lancer({"m.py": m, "test-m.py": longue(60)}, "--cliquet")
        posee, tenu = lancer({}, "--base"), lancer({}, "--cliquet")
        verifier("VIT15 (d) sans base → GARDE:, sort 1 ; --base pose 4 fonctions ; le même code → CLIQUET TENU",
                 sans_base == (1, "GARDE: pas de base scripts/sante-base.json — `vlp.py sante --base` d'abord\n")
                 and posee == (0, "BASE scripts/sante-base.json · 4 fonctions · sans ruff\n")
                 and tenu == (0, tete + bilan % (4, 0, 0, 0) + "\nCLIQUET TENU\n"), (sans_base, posee, tenu))
        empire = lancer({"m.py": ifs(12, "grosse") + ifs(1, "petite") + muette}, "--cliquet")
        verifier("VIT15 (e) une vieille fonction déjà au-dessus du seuil empire (complexité 12 → 13) → EMPIRE, ROMPU, sort "
                 "1 ; ses branches montent au seuil (12), sans écart — mutant : le plafond relâché d'un cran",
                 empire == (1, tete + "EMPIRE scripts/m.py:1 grosse · complexité 12 → 13, seuil 10\n"
                            + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n"), empire)
        sous_seuil = lancer({"m.py": ifs(11, "grosse") + ifs(9, "petite") + muette}, "--cliquet")
        passe = lancer({"m.py": ifs(11, "grosse") + ifs(10, "petite") + muette}, "--cliquet")
        verifier("VIT15 (f) une vieille fonction sous les seuils grandit jusqu'au seuil (complexité 2 → 10) → TENU ; le "
                 "passer (→ 11) → EMPIRE",
                 sous_seuil == (0, tete + bilan % (4, 1, 0, 0) + "\nCLIQUET TENU\n")
                 and passe == (1, tete + "EMPIRE scripts/m.py:28 petite · complexité 2 → 11, seuil 10\n"
                               + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n"), (sous_seuil, passe))
        neuves = lancer({"m.py": m + "\n\n" + ifs(10, "neuve_grosse") + "def neuve(a):\n    return a\n"}, "--cliquet")
        tests = lancer({"m.py": m, "test-m.py": longue(70) + ifs(10, "test_neuf").replace('    """Des if."""\n', "")},
                       "--cliquet")
        verifier("VIT15 (g) une fonction neuve au-dessus d'un seuil → SEUIL, une neuve sans docstring → DOCSTRING ; dans un "
                 "test-*.py, ni instructions (70) ni docstring, mais la complexité tient",
                 neuves == (1, tete + "SEUIL scripts/m.py:39 neuve_grosse · complexité 11, seuil 10 (neuve)\n"
                            "DOCSTRING scripts/m.py:64 neuve · sans docstring (neuve)\n"
                            + bilan % (6, 0, 0, 2) + "\nCLIQUET ROMPU · 2 écart(s)\n")
                 and tests == (1, tete + "SEUIL scripts/test-m.py:75 test_neuf · complexité 11, seuil 10 (neuve)\n"
                               + bilan % (5, 1, 0, 1) + "\nCLIQUET ROMPU · 1 écart(s)\n"), (neuves, tests))
        touchee = lancer({"m.py": m.replace(muette, "def muette(a):\n    return a + 1\n"), "test-m.py": longue(60)},
                         "--cliquet")
        renommee = lancer({"m.py": ifs(11, "grosse") + ifs(1, "petite2") + muette}, "--cliquet")
        deplacee = lancer({"m.py": ifs(11, "grosse") + muette, "m2.py": ifs(1, "petite")}, "--cliquet")
        verifier("VIT15 (h) une vieille fonction touchée sans docstring → DOCSTRING (intacte, elle passait) ; renommée ou "
                 "déplacée dans un autre fichier, même empreinte → suivie, TENU",
                 touchee == (1, tete + "DOCSTRING scripts/m.py:35 muette · sans docstring (touchée)\n"
                             + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n")
                 and renommee == deplacee == (0, tete + bilan % (4, 0, 1, 0) + "\nCLIQUET TENU\n"),
                 (touchee, renommee, deplacee))
        mieux = lancer({"m.py": ifs(9, "grosse") + ifs(1, "petite") + muette, "m2.py": None}, "--cliquet")
        verrou = lancer({}, "--base")
        rechute = lancer({"m.py": ifs(10, "grosse") + ifs(1, "petite") + muette}, "--cliquet")
        verifier("VIT15 (i) une amélioration se dit, --base la verrouille : remonter de 10 à 11, sous l'ancienne base (12), "
                 "→ EMPIRE",
                 mieux == (0, tete + bilan % (4, 1, 0, 0) + " · améliorées 1 : `vlp.py sante --base` les verrouille\n"
                           "CLIQUET TENU\n") and verrou[0] == 0
                 and rechute == (1, tete + "EMPIRE scripts/m.py:1 grosse · complexité 10 → 11, seuil 10\n"
                                 + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n"), (mieux, verrou, rechute))
        avant = mod.lire(base)
        refus = lancer({}, "--base")
        intacte = mod.lire(base) == avant
        forcee = lancer({}, "--base", "--forcer", "essai")
        trace = json.loads(mod.lire(base))["forcee"]
        verifier("VIT15 (j) --base qui relâcherait → l'écart, GARDE:, sort 1, base intacte ; --forcer écrit, et garde sa "
                 "raison dans la base",
                 refus == (1, "EMPIRE scripts/m.py:1 grosse · complexité 10 → 11, seuil 10\n"
                           + "GARDE: la base ne se relâche pas : 1 écart(s) ci-dessus — corrige, ou "
                           + "`--base --forcer \"<raison>\"`, rien écrit\n")
                 and intacte and forcee == (0, "BASE scripts/sante-base.json · 4 fonctions · sans ruff · relâchée : essai\n")
                 and len(trace) == 1 and trace[0]["raison"] == "essai" and trace[0]["ecarts"] == 1,
                 (refus, intacte, forcee, trace))
        seul = lancer({}, "--forcer", "x")
        ecrire(base, "{}")
        illisible = lancer({}, "--cliquet")
        casse = lancer({"m.py": "def (\n"}, "--cliquet")
    verifier("VIT15 (k) --forcer sans --base, une base illisible, un fichier qui ne se lit pas → GARDE:, sort 1",
             seul == (1, "GARDE: --forcer ne va qu'avec --base\n")
             and illisible[0] == 1 and illisible[1].endswith("sante-base.json : base illisible, format 1 attendu\n")
             and casse[0] == 1 and casse[1].startswith("GARDE: ") and "m.py:1 : " in casse[1], (seul, illisible, casse))


def tester_sante_si_base():
    """VIT16 : `--base --si-base`, la ligne de `/vlp:tache` à chaque fiche — sans base, rien d'écrit, même lancé hors du
    kit par `--racine .` ; avec une base, comme `--base` : elle se reprend, ou refuse de se relâcher."""
    import hashlib
    base_kit = os.path.join(ICI, "sante-base.json")
    empreinte_kit = hashlib.sha1(open(base_kit, "rb").read()).hexdigest()
    m = 'def f(a):\n    """Rendre a."""\n    return a\n'
    ici = os.getcwd()
    with tempfile.TemporaryDirectory() as tv:
        vide, equipe = os.path.join(tv, "vide"), os.path.join(tv, "equipe")
        os.makedirs(vide)
        ecrire(os.path.join(equipe, "scripts", "m.py"), m)
        try:
            os.chdir(equipe)
            dehors = appel(["sante", "--base", "--si-base", "--racine", "."])
        finally:
            os.chdir(ici)
        sans_scripts = appel(["sante", "--base", "--si-base", "--racine", vide, "--sans-ruff"])
        cree = os.listdir(vide) + os.listdir(os.path.join(equipe, "scripts"))
        verifier("VIT16 (a) --si-base sans base → SANS BASE, sort 0, rien d'écrit — dans un projet sans `scripts/`, et "
                 "hors du kit par `--racine .`, la base du kit identique à l'octet — mutant : --si-base ignoré",
                 dehors == sans_scripts == (0, "SANS BASE scripts/sante-base.json · rien écrit\n") and cree == ["m.py"]
                 and hashlib.sha1(open(base_kit, "rb").read()).hexdigest() == empreinte_kit,
                 (dehors, sans_scripts, cree))
        posee = appel(["sante", "--base", "--racine", equipe, "--sans-ruff"])
        reprise = appel(["sante", "--base", "--si-base", "--racine", equipe, "--sans-ruff"])
        ecrire(os.path.join(equipe, "scripts", "m.py"), m + "\n\ndef g(a):\n    return a\n")
        refus = appel(["sante", "--base", "--si-base", "--racine", equipe, "--sans-ruff"])
        seul = appel(["sante", "--si-base", "--racine", equipe, "--sans-ruff"])
    verifier("VIT16 (b) avec une base, --si-base fait comme --base : BASE, sort 0 ; une fonction neuve sans docstring → "
             "GARDE:, sort 1 ; --si-base sans --base → GARDE:",
             posee == reprise == (0, "BASE scripts/sante-base.json · 1 fonctions · sans ruff\n")
             and refus[0] == 1 and "GARDE: la base ne se relâche pas : 1 écart(s)" in refus[1]
             and seul == (1, "GARDE: --si-base ne va qu'avec --base\n"), (posee, reprise, refus, seul))


def tester_sante_kit():
    """VIT15 : le kit tient son propre cliquet — une fonction qui empire, ou neuve au-dessus d'un seuil ou sans
    docstring, fait tomber la suite. Sauté sous `vlp.py mutant` (`VLP_TOUS_ECARTS=1`) : un mutant touche toujours sa
    fonction, et une docstring qui y manque le dirait « attrapé » sans qu'aucun test ne l'ait vu."""
    if os.environ.get("VLP_TOUS_ECARTS") == "1":
        print("SAUTÉ: sous le mutant, le cliquet du kit ne joue pas")
        return
    code, s = appel(["sante", "--cliquet"])
    verifier("VIT15 (l) le kit tient son cliquet : `vlp.py sante --cliquet` → CLIQUET TENU ; sinon, chaque écart y est "
             "nommé — corrige la fonction, `--base --forcer` seulement si le relâchement est voulu",
             code == 0 and s.endswith("CLIQUET TENU\n"), s)


def tester_seul():
    """Contrôler `--seul` (VIT10) : le motif lu de la ligne de commande, puis de `VLP_SEUL` ; un groupe retenu par
    son nom ou par son texte, sans tenir compte de la casse ; `groupe` ne joue que lui."""
    global SEUL
    verifier("seul : --seul lu avant VLP_SEUL — mutant : VLP_SEUL d'abord",
             motif_seul(["--seul", "ABC1"], {"VLP_SEUL": "X"}) == "ABC1", motif_seul(["--seul", "ABC1"], {"VLP_SEUL": "X"}))
    verifier("seul : VLP_SEUL sans --seul ; ni l'un ni l'autre, tout se joue ; --seul sans motif, None",
             motif_seul([], {"VLP_SEUL": "X"}) == "X" and motif_seul([], {}) == "" and motif_seul(["--seul"], {}) is None
             and motif_seul(["--seul", ""], {}) is None, "")

    appels = []

    def tester_temoin_nom():
        """Un groupe témoin, retenu par son nom."""
        appels.append("nom")

    def temoin_texte():
        """Un groupe témoin, retenu par son texte : « un libellé Vit10-Témoin »."""
        appels.append("texte")
    verifier("seul : le nom porte le motif, sans casse — mutant : casse comptée", porte_motif(tester_temoin_nom, "TEMOIN_NOM"), "")
    verifier("seul : le texte porte le motif, sans casse — mutant : texte ignoré", porte_motif(temoin_texte, "vit10-témoin"), "")
    verifier("seul : ni le nom ni le texte, écarté", not porte_motif(temoin_texte, "autre-motif"), "")
    verifier("seul : le texte d'une aide du module que le groupe appelle porte le motif — mutant : aides ignorées",
             porte_motif(tester_matin, "npb1 (b) matin imprime") and not porte_motif(tester_mutant, "npb1 (b) matin imprime"),
             "")
    garde, joues, SEUL = SEUL, len(JOUES), "temoin_nom"
    try:
        groupe(tester_temoin_nom)
        groupe(temoin_texte)
    finally:
        SEUL = garde
        del JOUES[joues:]
    verifier("seul : groupe ne joue que le groupe qui porte le motif — mutant : filtre ignoré", appels == ["nom"], appels)


def bilan_seul():
    """Sous `--seul`, dire combien de groupes et de contrôles se sont joués ; aucun groupe : sortir 1, pour qu'un motif
    mal tapé ne passe pas pour une suite verte (VIT10)."""
    if not SEUL:
        return
    print("SEUL %s : %d groupe(s), %d contrôle(s) — %s" % (SEUL, len(JOUES), len(CONTROLES), " ".join(JOUES)))
    if not JOUES:
        print("GARDE: aucun groupe ne porte « %s »" % SEUL)
        sys.exit(1)


groupe(tester_sante_comptes)
groupe(tester_sante_ruff)
groupe(tester_sante_cliquet)
groupe(tester_sante_si_base)
groupe(tester_sante_kit)
groupe(tester_seul)


def horodate(d):
    return datetime.datetime.fromtimestamp(T0 + d, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def tour_compteur(d, n, *blocs):
    """Une ligne assistant à T0 + d, son tour n (100 000 tokens d'entrée, 0,50 $), ses blocs."""
    return {"type": "assistant", "timestamp": horodate(d), "requestId": "r%d" % n, "message": {
        "id": "m%d" % n, "model": "claude-opus-5", "content": list(blocs),
        "usage": {"input_tokens": 100000, "output_tokens": 0, "cache_creation_input_tokens": 0,
                  "cache_read_input_tokens": 0}}}


def outil_compteur(ident, nom, **entree):
    return {"type": "tool_use", "id": ident, "name": nom, "input": entree}


def user_compteur(d, contenu, origine=None, **plus):
    ligne = dict({"type": "user", "message": {"role": "user", "content": contenu}}, **plus)
    if d is not None:
        ligne["timestamp"] = horodate(d)
    if origine:
        ligne["origin"] = {"kind": origine}
    return ligne


def sortie_compteur(d, ident, texte):
    return user_compteur(d, [{"type": "tool_result", "tool_use_id": ident, "content": texte}])


def notification_compteur(d, balise, texte):
    return user_compteur(d, "<task-notification>\n%s\n<summary>%s</summary>\n</task-notification>" % (balise, texte),
                         "task-notification")


def lignes_compteur():
    """La transcription faite main de VIT17, en secondes après T0 : chaque écart a sa part en face, et la somme des
    parts se fait à la main — modèle 127, outils 753, attente 80, autre 25 ; une pause (960 → 3000)."""
    sortie_b = '"C:/t/tasks/%s.output"'
    mutant = 'py -3 scripts/vlp.py mutant scripts/a.py "x" "y" --test "py -3 scripts/test-vlp.py --seul z"'
    return [
        {"type": "queue-operation", "operation": "enqueue", "timestamp": horodate(0)},    # hors conversation
        user_compteur(0, "vas-y", "human"),                                                # attente 0
        tour_compteur(10, 1, outil_compteur("u1", "Bash", command="py -3 scripts/test-vlp.py")),   # modèle 10
        sortie_compteur(70, "u1", "SAUTÉ: x\nOK"),                                        # suite 60, verte
        {"type": "attachment", "timestamp": horodate(80)},                                # hors conversation
        tour_compteur(90, 2, outil_compteur("u2", "AskUserQuestion", questions=[])),      # modèle 10 + 10
        sortie_compteur(150, "u2", "Your questions have been answered: oui"),              # attente 60
        tour_compteur(160, 3, outil_compteur("u3", "Bash", command=mutant, run_in_background=True)),   # modèle 10
        sortie_compteur(161, "u3", "Command running in background with ID: b1."),          # mutant 1, b1 noté
        tour_compteur(170, 4, outil_compteur("u7", "Bash", command="until grep -q ATTRAP %s; do sleep 5; done; cat %s"
                                             % (sortie_b % "b1", sortie_b % "b1"))),   # modèle 9
        sortie_compteur(400, "u7", "ÉCART: z\nMUTANT ATTRAPÉ 1 écart(s)"),                 # attend b1 : mutant 230
        notification_compteur(405, "<tool-use-id>u3</tool-use-id>", "fini (exit code 0)"),   # mutant 5, fond
        tour_compteur(410, 5, outil_compteur("u9", "Bash", command="py -3 scripts/test-vlp.py", run_in_background=True)),
        sortie_compteur(411, "u9", "Command running in background with ID: b2."),          # suite 1, sans verdict
        tour_compteur(420, 6, outil_compteur("u8", "Monitor", command='until grep -q "^OK" %s; do sleep 5; done'
                                             % (sortie_b % "b2"))),   # modèle 9
        sortie_compteur(421, "u8", "Monitor started (task m1, expires in 5m)."),           # attend b2 : suite 1
        tour_compteur(430, 7),                                                             # modèle 9
        notification_compteur(700, "<task-id>m1</task-id>", "Monitor event"),             # par m1 : suite 270
        notification_compteur(710, "<tool-use-id>u9</tool-use-id>", "fini (exit code 1)"),   # suite 10, rouge
        tour_compteur(720, 8, outil_compteur("u11", "Bash", command="py -3 scripts/test-vlp.py --seul compteur")),
        sortie_compteur(750, "u11", "ÉCART: w\nFIN: 1 écart(s)"),                          # --seul 30, rouge
        tour_compteur(760, 9, outil_compteur("u4", "Read", file_path="C:/t/x.md")),        # modèle 10
        sortie_compteur(770, "u4", "     1→MUTANT ATTRAPÉ 1 écart(s)\n     2→GARDE: x"),   # reste 10, rien de lu
        tour_compteur(780, 10, outil_compteur("u10", "Bash", command="py -3 scripts/vlp.py cocher f.md X1")),
        sortie_compteur(790, "u10", "GARDE: suite rouge"),                                 # reste 10, GARDE 1
        tour_compteur(800, 11, outil_compteur("u12", "Agent", subagent_type="vlp:relecture")),   # modèle 10
        sortie_compteur(900, "u12", "ACCEPTÉE — ok\nGARDE: q"),                            # reste 100, ACCEPTÉE 1
        user_compteur(910, "consigne", isMeta=True),                                       # autre 10
        user_compteur(920, "[Subagent hand-back] rapport :\n  REFUSÉE — copie", "peer", isMeta=True),   # autre 10
        sortie_compteur(930, "u99", "ÉCART: y"),                                           # appel inconnu : reste 10
        tour_compteur(940, 12, outil_compteur("u5", "Bash", command='git commit -m "Q1 : Créer"')),   # modèle 10
        sortie_compteur(945, "u5", "[main abc] Q1 : Créer"),                               # Git 5
        tour_compteur(950, 13, outil_compteur("u6", "Artifact", action="publish")),        # modèle 5
        sortie_compteur(960, "u6", "publié"),                                              # publication 10
        user_compteur(None, "sans heure"),                                                 # hors du temps
        tour_compteur(3000, 14),                                                           # pause de 2 040 s
        user_compteur(3020, "la suite", "human"),                                          # attente 20
        {"type": "system", "subtype": "stop_hook_summary", "timestamp": horodate(3025)},   # au reste, à la fin
    ]


def ecrire_compteur(chemin, cout_etat=None):
    """Écrire la transcription faite main ; `cout_etat` : une ligne `cost-state` posée après le tour de 760 s."""
    lignes = lignes_compteur()
    if cout_etat is not None:
        lignes.insert(22, dict(cout_etat, type="cost-state"))
    ecrire(chemin, "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes))


TOUT_COMPTEUR = ("actif 16 = modèle 2 + outils 13 + attente 1 + autre 0 · outils : suite 6 (2), --seul 1 (1), "
                 "test-boucle 0 (0), mutant 4 (1), pyright 0 (0), Git 0 (1), publication 0 (1), reste 2 (4) · 14 tours"
                 " · 7,00 $ · garde-fous : suites 1/3, ÉCART 1, MUTANT ATTRAPÉ 1, GARDE 1, relecteur 1 ACCEPTÉE + 1 "
                 "REFUSÉE")


def tester_compteur_lecture():
    """Contrôler la lecture de `compteur` (VIT17) sur la transcription faite main : les parts à la seconde, le temps
    et les appels par sorte d'outil, les garde-fous, ce qui manque, la ligne en minutes."""
    m = mod.mesure()
    with tempfile.TemporaryDirectory() as t:
        chemin = os.path.join(t, "sss.jsonl")
        ecrire_compteur(chemin)
        j, erreur = m.journal(chemin, mod.lire_sortie)
        verifier("compteur : ce qui manque se compte — 1 ligne sans heure, 1 sortie sans appel, 21 user dont 6 à origin",
                 erreur is None and (j.sans_heure, j.sans_appel, j.users, j.origines) == (1, 1, 21, 6),
                 (erreur, j and vars(j).items()))
        mesure_ = mod.compter_plage([(chemin, j)], (-mod.INFINI, mod.INFINI))
    verifier("compteur : un écart va à la ligne qui le ferme — modèle 127, outils 753, attente 80, autre 25, 1 pause",
             (mesure_["parts"], mesure_["pauses"]) == ({"modèle": 127, "outils": 753, "attente": 80, "autre": 25}, 1),
             mesure_)
    verifier("compteur : l'attente d'une tâche de fond va à l'appel qui l'a lancée — boucle, Monitor, notification",
             mesure_["outils"] == {"suite": 342, "--seul": 30, "test-boucle": 0, "mutant": 236, "pyright": 0, "Git": 5,
                                   "publication": 10, "reste": 130} and mesure_["fond"] == 285, mesure_)
    verifier("compteur : un appel par sortie directe — ni la notification, ni l'attente, ni la réponse à une question",
             mesure_["appels"] == {"suite": 2, "--seul": 1, "test-boucle": 0, "mutant": 1, "pyright": 0, "Git": 1,
                                   "publication": 1, "reste": 4}, mesure_["appels"])
    verifier("compteur : les garde-fous lus là où ils disent vrai, les suites jugées sur leur verdict",
             (mesure_["suites"], mesure_["garde_fous"]) == ([3, 1], [1, 1, 1, 1, 1]), mesure_)
    verifier("compteur : la ligne en minutes, chaque total juste à la minute (plus gros restes)",
             mod.ligne_compteur("tout", mesure_, (0, 14, Decimal("7.00"), 1)) == "tout · durée - · " + TOUT_COMPTEUR,
             mod.ligne_compteur("tout", mesure_, (0, 14, Decimal("7.00"), 1)))
    vide = m.Journal(users=3)
    verifier("compteur : manques — une session sans origin, rien de tapé ne se lit, ça se dit",
             mod.manques([("a/s.jsonl", vide)]) == ["AVERTISSEMENT: s.jsonl : 3 ligne(s) user, aucune avec origin — "
                                                    "l'attente tombe au reste"], mod.manques([("a/s.jsonl", vide)]))
    agent = os.path.join("s", "subagents", "agent-a.jsonl")
    evenements = [(T0 + 5, m.MODELE, None), (T0 + 2000, m.MODELE, None)]
    verifier("compteur : un sous-agent tout entier ou pas du tout, à son départ",
             (m.tranche(agent, evenements, (T0, T0 + 10)), m.tranche(agent, evenements, (T0 + 10, T0 + 9000)))
             == (evenements, []), m.tranche(agent, evenements, (T0, T0 + 10)))


def tester_compteur_sortes():
    """Contrôler les sortes d'outil, le verdict d'une suite, l'arrondi qui somme juste et la recoupe sans plage de
    `compteur` (VIT17)."""
    cas = [("Bash", "py -3 scripts/test-vlp.py", "suite"),
           ("Bash", 'cd "D:/x" && py -3 scripts/test-vlp.py --seul compteur', "--seul"),
           ("Bash", "py -3 scripts/test-vlp.py > o.txt; grep -- --seul o.txt", "suite"),
           ("Bash", 'py -3 scripts/vlp.py mutant a.py "x" "y" --test "py -3 scripts/test-vlp.py --seul z"', "mutant"),
           ("PowerShell", '& "C:/Python/python.exe" scripts/test-boucle.py', "test-boucle"),
           ("Bash", "pyright scripts/vlp.py", "pyright"), ("PowerShell", "git -C . log -1", "Git"),
           ("Bash", 'grep -n "test-vlp.py" scripts/x.py', "reste"),
           ("Bash", "cat > f.sh <<'EOF'\npy -3 scripts/test-vlp.py\nEOF", "reste"),
           ("Artifact", "", "publication"), ("Read", "", "reste")]
    rendus = [mod.sorte_outil((nom, {"command": c})) for nom, c, _ in cas]
    verifier("compteur : la sorte d'un appel, à ce qu'il lance en tête d'un segment — ni cité, ni dans un heredoc",
             rendus == [s for _, _, s in cas], list(zip(rendus, [s for _, _, s in cas])))
    verdicts = [mod.verdict_suite(*a) for a in (("SAUTÉ: x\nOK", ""), ("ÉCART: x\nFIN: 1", ""), ("fini\n", ""),
                                                ("(exit code 0)", "fond"), ("(exit code 1)", "fond"), ("tué", "fond"),
                                                ("(exit code 0)", "fond attente"), ("OK", "attente"))]
    verifier("compteur : le verdict d'une suite — OK vert, ÉCART rouge, muet non jugé ; en fond, le code de sortie",
             verdicts == [True, False, None, True, False, None, None, None], verdicts)
    reparties = (mod.minutes_reparties([74, 326, 80, 25]), mod.minutes_reparties([60, 231, 20, 5, 10], 6),
                 mod.minutes_reparties([0, 0]))
    verifier("compteur : les minutes somment leur total — les plus gros restes prennent la minute",
             reparties == ([1, 6, 1, 0], [1, 4, 1, 0, 0], [0, 0]), reparties)
    verifier("compteur : une cost-state sans startTime, ou sans ligne horodatée avant, n'a pas de plage — ça se dit",
             (mod.ligne_recoupe("R", T0, {}, []), mod.ligne_recoupe("R", None, {"startTime": 1}, []))
             == ("R · pas de plage — startTime absent", "R · pas de plage — aucune ligne horodatée avant"),
             mod.ligne_recoupe("R", T0, {}, []))


def tester_compteur_commande():
    """Contrôler `vlp.py compteur` de bout en bout (VIT17) : les plages de `cout`, fiches nommées, `--recoupe`, et la
    `GARDE:` sans découpe."""
    with tempfile.TemporaryDirectory() as t:
        pr, dep = os.path.join(t, ".claude", "projects", "p"), os.path.join(t, "depot")
        ecrire_compteur(os.path.join(pr, "sss.jsonl"), {"startTime": (T0 - 10) * 1000, "totalToolDuration": 300000,
                                                        "totalAPIDuration": 120000})
        ecrire(os.path.join(dep, "q.md"), QFICHES % ("sss", "sss"))
        mod.GIT = "git-absent-vlp"
        try:
            sans_git = appel(["compteur", os.path.join(dep, "q.md")])
        finally:
            mod.GIT = "git"
        verifier("compteur : sans découpe, une GARDE: et 1", sans_git[0] == 1 and sans_git[1].startswith(
            "GARDE: pas de découpe — git ne se lance pas"), sans_git)
        if not shutil.which("git"):
            print("SAUTÉ: git absent — compteur de bout en bout n'est pas testé")
            return
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        subprocess.run(["git", "init", "-q"], cwd=dep, env=env, check=True, capture_output=True)
        for d, sujet in ((-100, "Chantier Q ouvert : cadré"), (943, "Q1 : Créer"), (3010, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            rendus = [appel(["compteur", os.path.join(dep, "q.md")] + plus)
                      for plus in ([], ["Q2"], ["Q9"], ["--recoupe"])]
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
    rien = ("actif 0 = modèle 0 + outils 0 + attente 0 + autre 0 · outils : suite 0 (0), --seul 0 (0), test-boucle 0 "
            "(0), mutant 0 (0), pyright 0 (0), Git 0 (%d), publication 0 (%d), reste 0 (0) · %d tours · %s $ · "
            "garde-fous : suites -, ÉCART -, MUTANT ATTRAPÉ -, GARDE -, relecteur -")
    q2 = "Q2 · durée 34 · " + rien % (1, 1, 2, "1,00")
    lignes = ["AVERTISSEMENT: sss.jsonl : 1 ligne(s) de message sans heure, hors du temps",
              "AVERTISSEMENT: sss.jsonl : 1 sortie(s) sans appel connu, rangée(s) au reste",
              mod.ENTETE_COMPTEUR % 30,
              "Q1 · durée 17 · actif 16 = modèle 2 + outils 12 + attente 1 + autre 1 · outils : suite 6 (2), --seul 0 "
              "(1), test-boucle 0 (0), mutant 4 (1), pyright 0 (0), Git 0 (0), publication 0 (0), reste 2 (4) · 12 "
              "tours · 6,00 $ · garde-fous : suites 1/3, ÉCART 1, MUTANT ATTRAPÉ 1, GARDE 1, relecteur 1 ACCEPTÉE + 1 "
              "REFUSÉE", q2, "hors fiches · durée - · " + rien % (0, 0, 0, "0,00"),
              "TOTAL (fiches + hors fiches) · durée - · " + TOUT_COMPTEUR]
    verifier("compteur : une ligne par fiche aux plages de cout, hors fiches, TOTAL — l'écart à cheval sur un commit "
             "ne compte nulle part", rendus[0] == (0, "\n".join(lignes) + "\n"), rendus[0][1])
    verifier("compteur : les fiches nommées seules, et leur TOTAL", rendus[1] == (0, "\n".join(
        lignes[:3] + [q2, "TOTAL (fiches nommées) · durée 34 · " + rien % (1, 1, 2, "1,00")]) + "\n"), rendus[1][1])
    verifier("compteur : une fiche nommée sans plage se dit, et sort 1", rendus[2][0] == 1
             and "GARDE: fiche sans plage : Q9 — ni commit « Q9 : », ni session\n" in rendus[2][1], rendus[2])
    recoupe = ("RECOUPE sss.jsonl ligne 23 (minutes) · outils 10,1 contre totalToolDuration 5,0 (écart +5,1 ; sans les "
               "4,8 fermées par une notification de fond : +0,4) · modèle 1,5 contre totalAPIDuration 2,0 (écart -0,5) "
               "· durée 12,8 contre totalDuration absent\n")
    verifier("compteur --recoupe : la cost-state face au compteur, du startTime à sa dernière ligne horodatée ; un "
             "champ absent se dit", rendus[3] == (0, "\n".join(lignes) + "\n" + recoupe), rendus[3][1])


groupe(tester_compteur_lecture)
groupe(tester_compteur_sortes)
groupe(tester_compteur_commande)
groupe(tester_boucle_nuit)
groupe(tester_boucle)    # en dernier : les trois quarts de la suite, un écart d'ailleurs tombe avant lui (VIT2)

if ECARTS:
    print("FIN: %d écart(s)" % len(ECARTS))     # la suite est allée au bout : `vlp.py mutant` ne la dit pas PLANTÉ
    sys.exit(1)
noter_si_verte()
bilan_seul()
print("OK")
