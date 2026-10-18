"""`vlp.py carte` (noyau/carte.py) : la carte d'un projet, sa TODO, sa méthode, son plafond, la ligne `GIT=`,
l'injection des skills, l'avertissement d'une session déjà notée, la marque d'enchaînement et le ménage des
tampons — migré de l'ancienne suite maison (REF50). Chaque `assert` garde le libellé d'origine de son `verifier` en
tête de son message (REF5), puis le diagnostic ; `conftest.py` isole l'environnement et la config Git.
"""
import glob
import hashlib
import io
import os
import re
import shutil
import subprocess
import tempfile
import time

from aides import RACINE, ecrire, mod

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


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


def rendu(depart):
    s = io.StringIO()
    mod.carte(depart, s)
    return s.getvalue()


def test_carte_projet(tmp_path):
    """Contrôler `carte` sur un projet : remontée au projet, chemin avec espace, titres numérotés, prochaine fiche."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p = os.path.join(t, "proj")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES)
        sous = os.path.join(p, "src", "a")
        os.makedirs(sous)
        ecrire(os.path.join(p, "src", "chantier.md"), "une commande, pas la carte\n")

        s = rendu(sous)
        assert ("PROJET=%s\n" % p in s), ("remonte au projet") + "\n" + str(s)
        assert ("- **alias** : pz" in s), ("carte entière") + "\n" + str(s)
        assert ("--- fiches : context AI/20-z.md (10 lignes, 3 titres) ---" in s), ("chemin avec espace et plage") + "\n" + str(s)
        assert ("7:## Z1 [x] — faite\n9:## Z2 [ ] — à faire\n10:## Z10 [ ] — après\n" in s), ("titres numérotés") + "\n" + str(s)
        assert (s.endswith("PROCHAINE=Z2\n")), ("prochaine dans l'ordre du fichier") + "\n" + str(s)
        # REF28 : sans effort au socle, le défaut lu dans la méthode du kit (`medium`, copie que ce test compare à
        # sa source) ; avec, celui du socle — jamais au-delà de « L'ordre des fiches ».
        assert ("\nEFFORT=medium (défaut de methode-chantier.md)\nPROCHAINE=" in s), ("effort : défaut de la méthode") + "\n" + str(s)
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES.replace(
            "## Le socle commun\n", "## Le socle commun\n\n- la fiche en Opus, effort `high`.\n\n"
            "## L'ordre des fiches\n\n- effort `low` hors du socle\n"))
        s = rendu(p)
        assert ("\nEFFORT=high (socle du chantier)\nPROCHAINE=" in s), ("effort : celui du socle") + "\n" + str(s)
        m = os.path.join(t, "methode-chantier.md")
        ecrire(m, "- **L'effort se règle selon la tâche** — plus bas\n  pour le mécanique. Une fiche, de code, en Opus"
               " :\n  `xhigh` ; `max` en recours.\n- autre puce : `low`\n")
        assert (mod.effort_defaut(m) == "xhigh"), ("effort : défaut sur deux lignes") + "\n" + str(mod.effort_defaut(m))
        assert (mod.ligne_effort([], os.path.join(t, "absente.md")).startswith(
            "EFFORT=absent")), ("effort : règle absente") + "\n" + str(mod.ligne_effort([], os.path.join(t, "absente.md")))

        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES.replace("[ ]", "[x]"))
        s = rendu(p)
        assert (s.endswith("PROCHAINE=aucune\n")), ("tout coché") + "\n" + str(s)

        ecrire(os.path.join(p, "context AI", "20-z.md"), "# Chantier Z\n\n%s\n### Z1 reformulé\n" % OUVERT)
        s = rendu(p)
        assert ("GARDE: aucun titre" in s and "PROCHAINE" not in s), ("garde grep muet") + "\n" + str(s)

        # Sans marque, aucun chantier : l'ancienne ligne « fichier de fiches courant » ne nomme plus rien (NUI31).
        ecrire(os.path.join(p, "context AI", "20-z.md"), FICHES.replace(OUVERT, "Fermé."))
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/") + "- **fichier de fiches courant** :"
               " context AI/20-z.md (Z1..Z10)\n")
        s = rendu(p)
        assert ("--- fichier de fiches courant : aucun ---\n" in s and "TODO=absente (pas de ligne « chantiers possibles »)" in s), ("aucun courant") + "\n" + str(s)

        w = os.path.join(t, "ws")
        ecrire(os.path.join(w, "b", "CHANTIER.md"), CHANTIER % ("bb", "context AI/"))
        ecrire(os.path.join(w, "a", "CHANTIER.md"), CHANTIER % ("aa", "context AI/"))
        ecrire(os.path.join(w, "c", "chantier.md"), "une commande\n")
        s = rendu(w)
        assert (s == "VOISIN=%s alias=aa\nGIT=hors Git\nVOISIN=%s alias=bb\nGIT=hors Git\n"
                 % (os.path.join(w, "a"), os.path.join(w, "b"))), ("voisins triés avec alias, et leur GIT=") + "\n" + str(s)

        vide = os.path.join(t, "vide")
        os.makedirs(vide)
        s = rendu(vide)
        assert (s == "AUCUN_PROJET\n"), ("aucun projet") + "\n" + str(s)


def test_carte_git(tmp_path, depot_modele):
    """NUI35 : la ligne `GIT=` de la carte — tout suivi, un fichier ignoré, un fichier non ajouté, un dossier nommé
    par lui-même, hors Git ; jamais pour le relecteur."""
    def git(d, *args):
        subprocess.run(["git"] + list(args), cwd=d, capture_output=True, check=True)

    def lignes_git(d, relecteur=False):
        s = io.StringIO()
        mod.carte(d, s, relecteur)
        return [l for l in s.getvalue().split("\n") if l.startswith("GIT=")]

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        p = os.path.join(t, "p")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pg", "ctx/"))
        assert (lignes_git(p) == ["GIT=hors Git"]), ("git : hors Git") + "\n" + str(lignes_git(p))
        ecrire(os.path.join(p, "CLAUDE.md"), "# p\n")
        ecrire(os.path.join(p, "ctx", "08-etat.md"), "# état\n")
        ecrire(os.path.join(p, "ctx", "artefacts", "page.html"), "<p>\n")
        shutil.copytree(os.path.join(depot_modele, ".git"), os.path.join(p, ".git"))   # le dépôt modèle, pas un git init
        assert (lignes_git(p) == ["GIT=non ajouté CHANTIER.md, CLAUDE.md, ctx/"]), ("git : dossier entier non ajouté") + "\n" + str(lignes_git(p))
        git(p, "add", "-A")
        assert (lignes_git(p) == ["GIT=suivi"]), ("git : tout suivi") + "\n" + str(lignes_git(p))
        assert (lignes_git(p, relecteur=True) == []), ("git : rien pour le relecteur") + "\n" + str(lignes_git(p, True))
        ecrire(os.path.join(p, "ctx", "09-neuf.md"), "# neuf\n")
        assert (lignes_git(p) == ["GIT=non ajouté ctx/09-neuf.md"]), ("git : un fichier non ajouté") + "\n" + str(lignes_git(p))
        git(p, "rm", "-q", "--cached", "CHANTIER.md")
        ecrire(os.path.join(p, ".gitignore"), "CHANTIER.md\n")
        assert (lignes_git(p) == ["GIT=ignoré CHANTIER.md", "GIT=non ajouté ctx/09-neuf.md"]), ("git : un fichier ignoré, l'autre non ajouté") + "\n" + str(lignes_git(p))
        git(p, "rm", "-q", "--cached", "ctx/08-etat.md")
        ecrire(os.path.join(p, ".gitignore"), "CHANTIER.md\nctx/*\n!ctx/artefacts/\n__pycache__/\n")
        ecrire(os.path.join(p, "ctx", "__pycache__", "x.pyc"), "x")
        assert (lignes_git(p) == ["GIT=ignoré CHANTIER.md, ctx/*"]), ("git : les fichiers directs d'un dossier en ctx/*, sans __pycache__") + "\n" + str(lignes_git(p))


def test_carte_relecteur(tmp_path):
    """REL2 : `carte --relecteur` tait les titres de fiches et `PROCHAINE=` ; sans l'option, rien ne change."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as bac:
        pr = os.path.join(bac, "pr")
        ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/"))
        ecrire(os.path.join(pr, "context AI", "20-z.md"),
               ouvert("# Chantier ZZZ\n\n## ZZZ1 [ ] — à relire\n---\n## ZZZ2 [x] — piège\n"))
        s = rendu(pr)
        assert (s.endswith("--- fiches : context AI/20-z.md (7 lignes, 2 titres) ---\n"
                            "5:## ZZZ1 [ ] — à relire\n7:## ZZZ2 [x] — piège\nEFFORT=medium (défaut de "
                            "methode-chantier.md)\nPROCHAINE=ZZZ1\n")), ("carte sans --relecteur : titres et PROCHAINE inchangés") + "\n" + str(s)
        r = io.StringIO()
        mod.carte(pr, r, relecteur=True)
        r = r.getvalue()
        assert ("piège" not in r and "PROCHAINE=" not in r and "PROJET=%s\n" % pr in r), ("carte --relecteur : ni titre ni PROCHAINE=, mais PROJET=") + "\n" + str(r)
        assert ("ZZZ2" not in r and "COURANT=context AI/20-z.md\n" in r), ("carte --relecteur : ni l'étendue des fiches (dette REL), mais le chemin") + "\n" + str(r)
        sans_git = "".join(l for l in s.splitlines(True) if not l.startswith("GIT="))   # NUI35 : pas pour le relecteur
        assert (sans_git.startswith(r) and "- **alias** : pr" in r and "GIT=" in s and "GIT=" not in r), ("carte --relecteur : le reste à l'octet près, sans GIT=") + "\n" + str(r)
        j = io.StringIO()
        mod.carte_injectee(pr, "py", False, j, relecteur=True)
        j = j.getvalue()
        assert (j.startswith("\nPYTHON=py\n") and "piège" not in j and "PROCHAINE=" not in j), ("carte --python --relecteur : l'option passe l'injection") + "\n" + str(j)


def test_carte_todo(tmp_path):
    """LEC2 : la TODO des chantiers possibles, quand aucun chantier n'est ouvert."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr = os.path.join(t, "pr")
        def chantier(possibles):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n"
                   "- **chantiers possibles** : %s\n- **contexte** : ctx/\n" % possibles)
        todo = lambda n: "## TODO %s\n\nTexte%s.\n## Suite\n\nFin.\n" % (n, n)

        ecrire(os.path.join(pr, "08-etat.md"), "# État\n\n## TODO première\n\nLigne 1.\nLigne 2.\n"
               "## TODO deuxième\n\nLigne TODO2.\n## Autre\n\nAprès.\n## Quatre\n\nFin.\n")
        chantier("`08-etat.md`")
        s = rendu(pr)
        assert ("--- TODO : 08-etat.md (lignes 3–6) ---\n## TODO première\n\nLigne 1.\nLigne 2.\n" in s
                 and "## TODO deuxième" not in s), ("carte TODO : premier titre TODO seul, texte jusqu'avant le titre suivant") + "\n" + str(s)

        ecrire(os.path.join(pr, "sans.md"), "# X\n\n## Un\n\nTexte.\n## Deux\n")
        chantier("`sans.md`")
        s = rendu(pr)
        assert ("TODO=absente sans.md\n" in s), ("carte TODO : sans titre TODO") + "\n" + str(s)

        ecrire(os.path.join(pr, "a.md"), todo("A"))
        ecrire(os.path.join(pr, "b.md"), todo("B"))
        chantier("`a.md`, puis `b.md`")
        s = rendu(pr)
        assert ("--- TODO : a.md (lignes 1–3) ---\n## TODO A\n\nTexteA.\n--- TODO : b.md (lignes 1–3) ---" in s), ("carte TODO : deux chemins entre backticks, dans l'ordre") + "\n" + str(s)

        chantier("`a.md` (section TODO)")
        s = rendu(pr)
        assert (s.count("--- TODO :") == 1 and "--- TODO : a.md " in s), ("carte TODO : prose entre parenthèses") + "\n" + str(s)

        chantier("`absent.md`, puis `b.md`")
        s = rendu(pr)
        assert ("GARDE: fichier introuvable : absent.md\n--- TODO : b.md " in s), ("carte TODO : absent → GARDE, le suivant quand même") + "\n" + str(s)

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
            assert (vus == attendus and "GARDE" not in s), ("carte TODO : le disque tranche — %s" % possibles) + "\n" + str(s)

        chantier("`a.md`")
        ecrire(os.path.join(pr, "ctx", "fiches.md"), "# Chantier Z\n\n%s\n\n## Z1 [ ] — Fiche\n" % OUVERT)
        s = rendu(pr)
        assert ("--- TODO :" not in s and "TODO=absente" not in s), ("carte TODO : chantier ouvert, aucun bloc") + "\n" + str(s)


def test_carte_plafond(tmp_path):
    """REF2 : sans chantier ouvert, la carte injectée reste sous `PLAFOND_CARTE`, sa TODO condensée ; un rang cassé,
    une `GARDE:` et la TODO entière ; au-delà du plafond, une `GARDE:` en première ligne, la carte entière ensuite."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr = os.path.join(t, "pr")
        def chantier(prose=""):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n- **chantiers possibles** : `08-etat.md`\n"
                   "- **contexte** : ctx/\n%s" % prose)
        def etat(rangs):
            ecrire(os.path.join(pr, "08-etat.md"), "# État\n\n## La TODO\n\nProse de tête.\n\n| # | Chantier | Ce qu'il "
                   "apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n%s\nProse de fin.\n## Suite\n\nFin.\n" % rangs)
        def injectee():
            s = io.StringIO()
            mod.carte_injectee(pr, "py -3", False, s)
            return s.getvalue()
        apporte = "Ce que le chantier apporte, aussi long qu'une vraie ligne de TODO. " * 12
        chantier()
        etat("".join("| %d | `C%02d` — Le chantier %d | %s | **V2 · score 15 (3 × 5)** · 1 fiche | — |\n"
                     % (n, n, n, apporte) for n in range(1, 61)))
        s = injectee()
        assert (len(s) <= mod.PLAFOND_CARTE and "GARDE" not in s), ("carte sous PLAFOND_CARTE : TODO de 60 lignes, %d caractères" % len(s)) + "\n" + str(s[:2000])
        assert ("--- TODO : 08-etat.md (lignes 3–" in s and "| # | Chantier | Coût estimé | Dépend de |\n" in s
                 and "9:| 1 | `C01` — Le chantier 1 | **V2 · score 15 (3 × 5)** · 1 fiche | — |\n" in s
                 and "68:| 60 | `C60` — " in s and "Ce que le chantier apporte" not in s and "Prose de" not in s), ("carte sous PLAFOND_CARTE : rangs numérotés, sans « Ce qu'il apporte » ni la prose") + "\n" + str(s[:2000])

        etat("| 1 | `C01` — Cassé | apporte | coût |\n")
        s = rendu(pr)
        assert ("GARDE: 08-etat.md : ligne 1 de la TODO : 4 cellules" in s and "Prose de tête.\n" in s), ("carte sous PLAFOND_CARTE : rang cassé → GARDE, TODO entière") + "\n" + str(s)

        chantier("\n%s\nDernière ligne de CHANTIER.md.\n" % ("Une prose de CHANTIER.md bien trop longue. " * 700))
        s = injectee()
        assert (s.startswith("GARDE: carte de %d caractères" % (len(s) - len(s.split("\n", 1)[0]) - 1))
                 and "\nPYTHON=py -3\n" in s and "Dernière ligne de CHANTIER.md.\n" in s), ("carte au-delà de PLAFOND_CARTE : GARDE en première ligne, carte entière") + "\n" + str(s[:500])


def test_carte_methode(tmp_path):
    """LEC3 : le format des fiches de la ligne **méthode**, quand aucun chantier n'est ouvert."""
    kit = mod.etat.KIT
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr, faux_kit = os.path.join(t, "pr"), os.path.join(t, "kit")
        def chantier(methode):
            ecrire(os.path.join(pr, "CHANTIER.md"), "# C\n\n- **alias** : pr\n"
                   + ("- **méthode** : %s\n" % methode if methode else ""))
        trois = ("# M\n## Avant\nx\n## Le fichier de fiches\na\n## Anatomie d'une fiche\nb\n"
                 "## Les deux formes de critère de fin\nc\n## Après\nd\n")

        ecrire(os.path.join(pr, "m.md"), trois)
        chantier("m.md")
        s = rendu(pr)
        assert ("--- méthode : m.md (lignes 4–9) ---\n## Le fichier de fiches\na\n## Anatomie d'une fiche\nb\n"
                 "## Les deux formes de critère de fin\nc\n" in s and "## Après" not in s), ("carte méthode : trois sections, le titre qui suit exclu") + "\n" + str(s)

        ecrire(os.path.join(pr, "sans.md"), "# M\n## Le fichier de fiches\na\n## Anatomie d'une fiche\nb\n")
        chantier("sans.md")
        s = rendu(pr)
        assert ("METHODE=absente sans.md\n" in s and "--- méthode" not in s), ("carte méthode : titre de fin manquant") + "\n" + str(s)

        ecrire(os.path.join(faux_kit, "methode-chantier.md"), trois)
        mod.etat.KIT = faux_kit
        try:
            chantier("methode-chantier.md, à la racine du kit")
            s = rendu(pr)
            assert ("--- méthode : methode-chantier.md (lignes 4–9) ---\n" in s), ("carte méthode : absente du projet, trouvée sous le kit") + "\n" + str(s)
            chantier("nulle-part.md")
            s = rendu(pr)
            assert ("GARDE: fichier introuvable : nulle-part.md\n" in s and "--- méthode" not in s), ("carte méthode : introuvable des deux côtés") + "\n" + str(s)
        finally:
            mod.etat.KIT = kit

        chantier(None)
        s = rendu(pr)
        assert ("METHODE=absente (pas de ligne « méthode »)\n" in s), ("carte méthode : pas de ligne") + "\n" + str(s)


def test_niv1_injection():
    """Contrôler la ligne d'injection de chaque skill (NIV1, EVF4)."""
    lignes_injection = []
    for skill in ("chantier", "tache", "chef"):
        texte = io.open(os.path.join(RACINE, "skills", skill, "SKILL.md"), encoding="utf-8").read()
        lignes_injection.append([l for l in texte.splitlines() if l.startswith("!`") and "vlp.py" in l])

    sans_option = [[l.replace(" --session-neuve", "") for l in x] for x in lignes_injection]
    assert ([len(x) for x in lignes_injection] == [1, 1, 1]
             and sans_option[0] == sans_option[1] == sans_option[2]), ("NIV1 : une ligne d'injection par skill, les trois identiques (au --session-neuve de tache près, VIT20)") + "\n" + str(repr(lignes_injection))

    injection = lignes_injection[0][0]
    # EVF4 : plus aucune redirection — `2>"${CLAUDE_PLUGIN_ROOT}/…"` écrivait hors du workspace, refusé sous
    # eval même Bash accordé (variante A, seule à laisser forker vlp:jouer). Le prix : `py: command not found`
    # entre dans la carte là où `py` manque (2 lignes sur 60 sous Ubuntu, 0 sous Windows, mesuré le 2026-09-26).
    assert (injection.count('/scripts/vlp.py" carte') == 3 and ">" not in injection), ("EVF4 : trois appels de lanceur, aucune redirection") + "\n" + str(injection)

    assert ("$null" not in injection and "/dev/null" not in injection), ("NIV1 : aucune syntaxe propre a un seul shell") + "\n" + str(injection)

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
    assert (injections == len(skills_glob) > 0 and ecrit_fichier == []), ("EVF4 : une injection de carte par SKILL.md du glob, aucune n'écrit de fichier") + "\n" + str("%d injections pour %d SKILL.md, fautives : %r" % (injections, len(skills_glob), ecrit_fichier))

    # VIT24 : `py` seul relit le `#!` de vlp.py et relance un python3 (+54 ms) ; le relais python3 ne change pas.
    textes = [io.open(c, encoding="utf-8").read() for c in skills_glob]
    py3 = sum(t.count('py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python "py -3"') for t in textes)
    nus = sum(t.count('py "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte') for t in textes)
    relais = sum(t.count('python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" carte --python python3 --relais') for t in textes)
    assert (py3 == 2 * len(skills_glob) and nus == 0 and relais == len(skills_glob)), ("VIT24 : chaque injection lance la carte par py -3 et dit PYTHON=py -3 (deux appels sur trois), aucun py "
             "nu ; le relais python3 reste") + "\n" + str((py3, nus, relais, len(skills_glob)))

    s_niv1 = io.StringIO()
    mod.carte_injectee(os.path.join(RACINE, "scripts"), "py -3", False, s_niv1)
    lu_n = s_niv1.getvalue()
    # L'en-tête seul : la carte recopie ensuite CHANTIER.md et, sans chantier courant, la TODO du kit, dont une
    # ligne (n° 101, EXE) cite « claude.exe introuvable » — une donnée du projet, pas un message de lanceur.
    entete_n = lu_n.split("\n--- ")[0]
    assert (lu_n.splitlines()[:2] == ["", "PYTHON=py -3"] and "introuvable" not in entete_n
             and "not found" not in entete_n and "PROJET=" in entete_n), ("NIV1 : la carte ne dit que PYTHON= et le projet") + "\n" + str(entete_n[:200])


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


def test_vit20_session_neuve(tmp_path):
    """Contrôler `carte --session-neuve` : l'avertissement d'une session déjà notée, et rien d'autre (VIT20)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as bac:
        pr = os.path.join(bac, "pr")
        ecrire(os.path.join(pr, "CHANTIER.md"), CHANTIER % ("pr", "context AI/"))
        ecrire(os.path.join(pr, "context AI", "20-z.md"), FICHES_VIT20)
        avant = carte_sous(pr)
        assert (avant.endswith("PROCHAINE=ZZZ3\n")), ("VIT20 : la carte d'avant, sans id ni option, finit sur PROCHAINE=") + "\n" + str(avant)
        s = carte_sous(pr, "joue-1", neuve=True)
        assert (s == avant + AVERTI_VIT20 % "ZZZ1, ZZZ2"), ("VIT20 : id sur deux fiches cochées → la carte d'avant, puis AVERTISSEMENT: qui les nomme") + "\n" + str(s)
        s = carte_sous(pr, "cadre-1", neuve=True)
        assert (s == avant + AVERTI_VIT20 % "cadrage"), ("VIT20 : id sur la ligne du cadrage → AVERTISSEMENT: qui le nomme") + "\n" + str(s)
        s = carte_sous(pr, "nuit-1", neuve=True)
        assert (s == avant + AVERTI_VIT20 % "ZZZ1"), ("VIT20 : id d'une ligne à rôle « (relecture) » → l'id seul compte") + "\n" + str(s)
        for sid in (None, "", "   ", "inconnue"):
            s = carte_sous(pr, sid, neuve=True)
            assert (s == avant), ("VIT20 : id %r → la carte d'avant, au caractère près" % (sid,)) + "\n" + str(s)
        s = carte_sous(pr, "joue-1")
        assert (s == avant), ("VIT20 : sans --session-neuve (/vlp:jouer, /vlp:enchainer, /vlp:chantier) → la carte d'avant") + "\n" + str(s)
        s = carte_sous(pr, "cadre-1", nuit=True, neuve=True)
        assert (s == carte_sous(pr, nuit=True) and "NUIT=1\n" in s), ("VIT20 : VLP_NUIT=1 (la nuit note l'id de clore avant sa session) → la carte de nuit d'avant") + "\n" + str(s)
        injection = [["carte", pr, "--python", "py -3", "--session-neuve"],
                     ["carte", pr, "--python", "python3", "--relais", "--session-neuve"]]
        s = carte_sous(pr, "joue-1", argv=injection)
        assert (s == "\nPYTHON=py -3\n" + avant + AVERTI_VIT20 % "ZZZ1, ZZZ2"), ("VIT20 : l'injection par main → PYTHON=py -3, la carte, l'AVERTISSEMENT: une fois ; le relais se tait") + "\n" + str(s)

    porteurs = sorted(os.path.basename(os.path.dirname(c)) for c in glob.glob(os.path.join(RACINE, "skills", "*", "SKILL.md"))
                      if "--session-neuve" in io.open(c, encoding="utf-8").read())
    tache = io.open(os.path.join(RACINE, "skills", "tache", "SKILL.md"), encoding="utf-8").read()
    ligne = next((l for l in tache.splitlines() if l.startswith("!`") and "vlp.py" in l), "")
    assert (porteurs == ["tache"] and ligne.count("--session-neuve") == 3), ("VIT20 : --session-neuve sur les trois appels de l'injection de /vlp:tache, dans aucune autre skill") + "\n" + str((porteurs, ligne))


def test_arp3_marque(tmp_path):
    """Contrôler `carte --enchaine` : la marque de la session fait taire l'AVERTISSEMENT: de VIT20, celle d'une autre
    session non (ARP3). Chaque cas dans son propre dossier temporaire, qui sert aussi de `tempfile.tempdir`."""
    enchainer = [["--python", "py -3", "--enchaine"], ["--python", "python3", "--relais", "--enchaine"],
                 ["--python", "py -3", "--relais", "--enchaine"]]

    def cas(session_marque, session_tache, appels):
        """Le projet de VIT20 dans un dossier neuf : `appels` (options de `carte`, l'injection d'enchainer) sous
        `session_marque`, puis la carte de /vlp:tache sous `session_tache`. Rendre (sa sortie, les marques posées)."""
        ancien = tempfile.tempdir
        with tempfile.TemporaryDirectory(dir=tmp_path) as bac:
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
    assert (marques == ["vlp-enchaine-joue-1"] and "AVERTISSEMENT:" not in s and s.endswith("PROCHAINE=ZZZ3\n")), ("ARP3 : l'injection d'enchainer pose la marque de sa session, la carte de tache s'y tait") + "\n" + str((marques, s))
    s, marques = cas("autre-1", "joue-1", enchainer)
    assert (marques == ["vlp-enchaine-autre-1"] and s.endswith(AVERTI_VIT20 % "ZZZ1, ZZZ2")), ("ARP3 : la marque d'une autre session → l'AVERTISSEMENT: sort encore") + "\n" + str((marques, s))
    s, marques = cas("joue-1", "joue-1", enchainer[1:])
    assert (marques == ["vlp-enchaine-joue-1"] and "AVERTISSEMENT:" not in s), ("ARP3 : les appels relais seuls posent la marque (sous Ubuntu, le premier appel échoue)") + "\n" + str((marques, s))
    for sid in (None, "", "../joue-1", "a/b", "joue 1"):
        s, marques = cas(sid, "joue-1", enchainer)
        assert (marques == [] and s.endswith(AVERTI_VIT20 % "ZZZ1, ZZZ2")), ("ARP3 : id %r → aucune marque, l'AVERTISSEMENT: sort" % (sid,)) + "\n" + str((marques, s))

    porteurs = sorted(os.path.basename(os.path.dirname(c)) for c in glob.glob(os.path.join(RACINE, "skills", "*", "SKILL.md"))
                      if "--enchaine" in io.open(c, encoding="utf-8").read())
    texte = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    ligne = next((l for l in texte.splitlines() if l.startswith("!`") and "vlp.py" in l), "")
    assert (porteurs == ["enchainer"] and ligne.count("--enchaine") == 3), ("ARP3 : --enchaine sur les trois appels de l'injection de /vlp:enchainer, dans aucune autre skill") + "\n" + str((porteurs, ligne))


def test_arp4_menage(tmp_path):
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
    with tempfile.TemporaryDirectory(dir=tmp_path) as bac:
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
        assert (reste == attendu), ("ARP4 : carte_injectee efface vlp-carte- de plus de 30 s et vlp-enchaine- de plus de 4 jours, garde "
                 "les récents, les autres préfixes et son propre tampon ; un dossier au préfixe ne bloque pas la suite "
                 "— mutant : l'âge des marques réduit à celui de vlp-carte-") + "\n" + str((reste, attendu))

    with tempfile.TemporaryDirectory(dir=tmp_path) as bac:
        vieillir(bac, [("vlp-filet-0dossier", 120), ("vlp-hook-vieux", 120), ("vlp-filet-vieux", 120),
                       ("vlp-hook-frais", 10), ("vlp-carte-vieux", 120)])
        neuf = mod.vlp_hook.tampon_neuf("vlp-hook-neuf", bac)
        reste = restants(bac)
        attendu = sorted(["vlp-filet-0dossier", "vlp-hook-frais", "vlp-carte-vieux", "vlp-hook-neuf"])
        assert (neuf is True and reste == attendu), ("ARP4 : tampon_neuf efface vlp-hook- et vlp-filet- de plus de 60 s, garde le reste, crée le sien") + "\n" + str((neuf, reste, attendu))
