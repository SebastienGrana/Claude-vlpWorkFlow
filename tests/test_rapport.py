"""`noyau/rapport.py` : `symboles`, `mutant`, `rapide`, `sante` et son cliquet, la base refaite à la fusion, les tailles
— migré de `scripts/test-vlp.py` (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son
message (REF5), puis le diagnostic.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import pytest
from aides import SCRIPTS, appel, ecrire, lire, mod
from noyau import rapport

ICI = SCRIPTS     # le dossier de scripts/test-vlp.py, d'où ces tests viennent

def test_py_du_statut():
    texte = " M scripts/a.py\0?? tests/neuf.py\0R  b.py\0ancien.py\0 M notes.md\0"
    assert rapport.py_du_statut(texte) == ["scripts/a.py", "tests/neuf.py", "b.py"]
    assert rapport.py_du_statut("") == []


def test_symboles(tmp_path):
    """`vlp.py symboles` sur un fichier à trois fonctions (VIT9) : chacune `nom début-fin`, dans l'ordre du fichier,
    la fonction imbriquée et la méthode tues ; avec des noms, leurs seules lignes, `ABSENT` pour l'inconnu, sort 1."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        chemin = os.path.join(t, "trois.py")
        ecrire(chemin, "import os\n\n\ndef un():\n    return os.sep\n\n\ndef deux():\n    def dedans():\n"
                       "        return 2\n    return dedans()\n\n\nclass Trois:\n    def m(self):\n        return 3\n")
        o = io.StringIO()
        code = mod.main(["symboles", chemin], o)
        assert (code == 0 and o.getvalue() == "un 4-5\ndeux 8-11\nTrois 14-16\n"), ("VIT9 : symboles, une ligne `nom début-fin` par fonction ou classe de premier niveau") + "\n" + str(o.getvalue())
        o = io.StringIO()
        code = mod.main(["symboles", chemin, "Trois", "rien", "un"], o)
        assert (code == 1 and o.getvalue() == "Trois 14-16\nABSENT rien\nun 4-5\n"), ("VIT9 : symboles avec des noms, leurs seules lignes, ABSENT pour l'inconnu, sort 1") + "\n" + str(o.getvalue())
        angel = os.path.join(t, "deco.as")
        ecrire(angel, "class Deco {\n    void Poser() { int x = 1; }\n}\n")
        o = io.StringIO()
        try:
            code = mod.main(["symboles", angel], o)
        except SyntaxError as e:    # l'ancien comportement : le traceback, rendu en écart
            code = "traceback %s" % e
        assert (code == 1 and o.getvalue().startswith("GARDE: %s ne se lit pas en Python" % angel)
                 and o.getvalue().count("\n") == 1), ("SYM : symboles sur un fichier non Python, une GARDE: et sort 1, jamais un traceback") + "\n" + str(o.getvalue())


def test_mutant(tmp_path):
    """MUT1 : casser, tester, lister les écarts, rendre à l'octet — CRLF, @fichier, gardes."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tm:
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
        assert (attrape[0] == 0 and "MUTANT ATTRAPÉ 2 écart(s)" in attrape[1] and attrape[1].count("ÉCART:") == 2
                 and "RENDU " in attrape[1] and attrape[2]
                 and vivant[0] == 1 and "MUTANT VIVANT" in vivant[1] and vivant[2]
                 and absent[0] == 1 and "trouvé 0 fois" in absent[1] and absent[2]
                 and double[0] == 1 and "trouvé 3 fois" in double[1] and double[2]
                 and plante[0] == 1 and "ne se lancent pas" in plante[1] and rendu_plante), ("MUT1 : mutant — attrapé (2 écarts, @fichier sur CRLF), vivant, absent, double, tests qui ne "
                 "se lancent pas ; fichier rendu à l'octet chaque fois — mutant : restauration retirée") + "\n" + str((attrape, vivant, absent, double, plante, rendu_plante))


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


def test_mutant_attendu(tmp_path):
    """VIT2 : le mutant joue une copie, le vrai fichier inchangé pendant et après ; `--attendu` tue l'arbre dès son
    écart, VIVANT s'il ne tombe pas ; une suite arrêtée en erreur après un autre écart est PLANTÉ, `--tous` aussi."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tm, tempfile.TemporaryDirectory(dir=tmp_path) as hors:
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
        assert (attrape[0] == 0 and "MUTANT ATTRAPÉ 2 écart(s) · arrêté sur « attendu »\n" in attrape[1]
                 and attrape[2] < 20 and not os.path.exists(petit) and vu_pendant == empreinte and attrape[3]
                 and "RENDU %s\n" % empreinte in attrape[1] and "COPIE restée" not in attrape[1]), ("VIT2 : --attendu juste → MUTANT ATTRAPÉ, l'arbre tué dès l'écart (pas 30 s, petit-fils compris) ; "
                 "vrai fichier inchangé pendant (sha1) et après — mutants : muter le vrai fichier, tuer le seul fils") + "\n" + str((attrape, vu_pendant, os.path.exists(petit)))
        vivant = mutant("x = 4", "--attendu", "jamais")
        assert (vivant[0] == 1 and vivant[1].startswith("ÉCART: autre\nMUTANT VIVANT pour jamais\n") and vivant[3]), ("VIT2 : --attendu d'un test qui ne tombe pas → MUTANT VIVANT pour …, sort 1, avec les écarts vus") + "\n" + str(vivant)
        milieu = mutant("x = 4", "--attendu", "utr")
        assert (milieu[0] == 1 and milieu[1].startswith(
                     "ÉCART: autre\nMUTANT VIVANT pour utr\n"
                     "ATTENDU AU MILIEU · « utr » est dans « autre » : --attendu \"autr\"\n") and milieu[3]), ("REF31 : --attendu au milieu d'un écart (cas d'ENA) → VIVANT, puis la ligne ATTENDU AU MILIEU qui "
                 "donne le début du libellé à recopier — mutant : la ligne retirée") + "\n" + str(milieu)
        plante = mutant("x = 3", "--attendu", "attendu")
        plante_tous = mutant("x = 3")
        assert (all(p[0] == 1 and "MUTANT PLANTÉ · tests sortis 1 sans finir, après 1 écart(s)" in p[1]
                     and "ATTRAPÉ" not in p[1] and p[3] for p in (plante, plante_tous))), ("VIT2 : la suite arrêtée en erreur après un autre écart → MUTANT PLANTÉ, sort 1, avec --attendu comme "
                 "sans — mutant : ATTRAPÉ dès qu'un écart est vu") + "\n" + str((plante, plante_tous))


JUGE_HORS_KIT = """import sys
t = open(sys.argv[1], encoding="utf-8").read()
if "x = 9" in t:
    raise ValueError("juge cassé")
print("OK X -- lu" if "x = 1" in t else "KO X -- lu")
sys.exit(0 if "x = 1" in t else 1)
"""


def test_mutant_juge(tmp_path):
    """ISO : un juge hors kit (`--test`) qui n'imprime ni `ÉCART:` ni `FIN:` est jugé à son code de sortie —
    ATTRAPÉ s'il sort 1 et dit `--attendu`, VIVANT s'il sort 0 ou ne le dit pas, PLANTÉ sur une erreur Python."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tm:
        f, juge = os.path.join(tm, "f.py"), os.path.join(tm, "juge.py")
        ecrire(f, "x = 1\ny = 1\n")
        ecrire(juge, JUGE_HORS_KIT)
        test = '"%s" "%s" "%s"' % (sys.executable, juge, f)

        def mutant(avant, apres, *options):
            o = io.StringIO()
            return mod.main(["mutant", f, avant, apres, "--test", test, *options], o), o.getvalue()
        vus = {"attrapé": mutant("x = 1", "x = 2", "--attendu", "KO X"), "nu": mutant("x = 1", "x = 2"),
               "vivant": mutant("y = 1", "y = 2", "--attendu", "KO X"),
               "muet": mutant("x = 1", "x = 2", "--attendu", "jamais"),
               "planté": mutant("x = 1", "x = 9", "--attendu", "KO X")}
        assert (vus["attrapé"][0] == 0 and "MUTANT ATTRAPÉ · juge hors kit sorti 1 — « KO X -- lu »" in vus["attrapé"][1]
                 and vus["nu"][0] == 0 and "MUTANT ATTRAPÉ · juge hors kit sorti 1" in vus["nu"][1]
                 and vus["vivant"][0] == 1 and "MUTANT VIVANT pour KO X · juge hors kit sorti 0" in vus["vivant"][1]
                 and vus["muet"][0] == 1 and "MUTANT VIVANT pour jamais · juge hors kit sorti 1 sans le dire"
                 in vus["muet"][1]
                 and vus["planté"][0] == 1 and "MUTANT PLANTÉ · juge hors kit sorti 1" in vus["planté"][1]
                 and "ValueError" in vus["planté"][1]), ("ISO : mutant d'un juge hors kit — sorti 1 en disant --attendu → ATTRAPÉ ; sorti 0, ou sans le "
                 "dire → VIVANT ; erreur Python → PLANTÉ — mutant : juge hors kit dit PLANTÉ") + "\n" + str(vus)


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


def test_mutant_vise(tmp_path):
    """VIT21 : `--attendu` sans `--test` ne joue d'abord que les groupes qui portent son libellé (`--seul`) ; attrapé
    là, une ligne `VISÉ` le dit ; aucun groupe, ou pas cet écart : la suite entière tranche, dite ; `--test` garde le
    dernier mot."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tm:
        kit, journal = os.path.join(tm, "kit"), os.path.join(tm, "journal.txt")
        f = os.path.join(kit, "f.py")
        ecrire(f, "a = 1\nb = 2\nc = 3\n")
        ecrire(os.path.join(kit, "scripts", "test-vlp.py"), SUITE_VISEE.replace("@JOURNAL@", repr(journal)))

        def mutant(avant, apres, attendu, *options):
            """Jouer le mutant `avant` → `apres` sur le faux kit ; rendre (code, sortie, motifs des lancements)."""
            ecrire(journal, "")
            o = io.StringIO()
            garde, mod.etat.KIT = mod.etat.KIT, kit
            try:
                code = mod.main(["mutant", f, avant, apres, "--attendu", attendu, *options], o)
            finally:
                mod.etat.KIT = garde
            with open(journal, encoding="utf-8") as j:
                return code, o.getvalue(), j.read().split("\n")[:-1]
        vise = mutant("a = 1", "a = 9", "porte a")
        assert (vise[0] == 0 and vise[1].startswith("VISÉ --seul « porte a »\nÉCART: porte a\n"
                                                     "MUTANT ATTRAPÉ 1 écart(s) · arrêté sur « porte a »\n")
                 and vise[2] == ["porte a"]), ("VIT21 : --attendu sans --test → ses seuls groupes (--seul), MUTANT ATTRAPÉ dit VISÉ, sans suite "
                 "entière — mutant : --seul jamais ajouté") + "\n" + str(vise)
        sans = mutant("c = 3", "c = 9", "hors c")
        assert (sans[0] == 0 and sans[1].startswith("SUITE ENTIÈRE · aucun groupe ne porte « hors c »\nÉCART: hors c\n"
                                                     "MUTANT ATTRAPÉ 1 écart(s) · arrêté sur « hors c »\n")
                 and sans[2] == ["hors c", ""]), ("VIT21 : un --attendu qu'aucun groupe ne porte → la GARDE de --seul n'est pas un écart : suite "
                 "entière, dite, qui l'attrape — mutant : pas de repli") + "\n" + str(sans)
        autre = mutant("b = 2", "b = 9", "porte a")
        assert (autre[0] == 1 and autre[1].startswith("SUITE ENTIÈRE · « porte a » n'est pas tombé dans ses groupes\n"
                                                       "ÉCART: voisin b\nMUTANT VIVANT pour porte a\n")
                 and "ATTRAPÉ" not in autre[1] and autre[2] == ["porte a", ""]), ("VIT21 : un groupe qui ne porte pas le contrôle ne rend jamais ATTRAPÉ — suite entière, dite, "
                 "MUTANT VIVANT pour …, sort 1") + "\n" + str(autre)
        test = '"%s" "%s"' % (sys.executable, os.path.join(kit, "scripts", "test-vlp.py"))
        dernier = mutant("a = 1", "a = 9", "porte a", "--test", test)
        assert (dernier[0] == 0 and dernier[1].startswith("ÉCART: porte a\nMUTANT ATTRAPÉ 1 écart(s)")
                 and dernier[2] == [""]), ("VIT21 : --test donné garde le dernier mot — sa seule commande, ni VISÉ ni SUITE ENTIÈRE") + "\n" + str(dernier)


def test_mutant_worktree(tmp_path):
    """MUW1 : une cible dans un worktree du kit rangé sous le dépôt principal (`KIT`) joue les tests du worktree,
    pas ceux de `KIT`, et une ligne `TESTS` le nomme."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tm:
        principal = os.path.join(tm, "principal")
        interieur = os.path.join(principal, ".claude", "worktrees", "w")
        for k, suite in ((principal, "print('OK')\n"),
                         (interieur, SUITE_VISEE.replace("@JOURNAL@", repr(os.path.join(tm, "journal.txt"))))):
            ecrire(os.path.join(k, ".claude-plugin", "plugin.json"), "{}\n")
            ecrire(os.path.join(k, "scripts", "test-vlp.py"), suite)
        f = os.path.join(interieur, "f.py")
        ecrire(f, "a = 1\nb = 2\nc = 3\n")
        o = io.StringIO()
        garde, mod.etat.KIT = mod.etat.KIT, principal
        try:
            code = mod.main(["mutant", f, "a = 1", "a = 9", "--attendu", "porte a"], o)
        finally:
            mod.etat.KIT = garde
        assert (code == 0 and "MUTANT ATTRAPÉ" in o.getvalue() and "TESTS %s\n" % interieur in o.getvalue()
                 and mod.kit_de(f) == interieur), ("MUW1 : cible d'un worktree sous KIT → ses tests à lui, MUTANT ATTRAPÉ et ligne TESTS du worktree — "
                 "mutant : copie_mutee reprise sur KIT") + "\n" + str((code, o.getvalue()))


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


def test_rapide(tmp_path):
    """VIT23 : `vlp.py rapide` joue les groupes de la fiche (`--seul`), pyright sur les `.py` touchés et le cliquet ;
    un écart semé dans le groupe d'une fiche → rouge, sans suite entière ; un contrôle sauté dit sa raison."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
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
        assert (propre == ("pyright", None, "aucun .py touché")), ("VIT23 : arbre propre → pyright sauté, « aucun .py touché » — mutant : pyright lancé sur rien") + "\n" + str(propre)

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
        assert (touches == ["f.py", "sous dossier/neuf.py"]), ("VIT23 : les .py touchés — modifié, et neuf sous un dossier à espace —, ni .txt ni .py intact") + "\n" + str(touches)
        vert = rapide("porte")
        assert (vert[0] == 0 and vert[2] == ["porte"] and vert[1] == (
                     "RAPIDE groupes « porte » : vert · N s · OK\n"
                     "RAPIDE pyright 2 fichier(s) : vert · N s · 0 errors, 0 warnings, 0 informations\n"
                     "RAPIDE cliquet : vert · N s · CLIQUET TENU\n"
                     "RAPIDE VERT · N s — la suite entière reste à jouer : cocher l'exige\n")), ("VIT23 : tout passe → trois lignes vertes, RAPIDE VERT, sort 0 ; seul --seul lancé, jamais la suite "
                 "entière") + "\n" + str(vert)
        ecrire(os.path.join(kit, "f.py"), "a = 9\nb = 2\nc = 3\nd = 4\n")
        seme = rapide("porte")
        assert (seme[0] == 1 and seme[2] == ["porte"] and seme[1].startswith(
                     "RAPIDE groupes « porte » : rouge · N s · code 1\n  ÉCART: porte a\n  FIN: 1 écart(s)\n")
                 and seme[1].endswith("RAPIDE ROUGE · N s — corrige avant de lancer la suite entière\n")), ("VIT23 : un écart semé dans le groupe de la fiche → rouge, ses lignes, RAPIDE ROUGE, sort 1, sans "
                 "lancer la suite entière — mutant : un rouge parmi des verts ne compte pas") + "\n" + str(seme)
        ecrire(os.path.join(kit, "f.py"), "a = 1\nb = 2\nc = 3\nd = 4\n")
        ecrire(os.path.join(kit, "sous dossier", "neuf.py"), "erreur = 5\n")
        ecrire(os.path.join(kit, "rompu"), "")
        types = rapide("porte")
        assert (types[0] == 1 and "RAPIDE pyright 2 fichier(s) : rouge · N s · code 1\n" in types[1]
                 and "neuf.py:1:1 - error: faux\n  1 errors, 0 warnings, 0 informations\n" in types[1]
                 and "RAPIDE cliquet : rouge · N s · code 1\n  EMPIRE f.py:1 g · complexité 3 → 11, seuil 10\n"
                     "  CLIQUET ROMPU\n" in types[1]), ("VIT23 : pyright en erreur et cliquet rompu → chacun rouge, avec ses lignes") + "\n" + str(types)
        os.remove(os.path.join(kit, "rompu"))
        sautes = rapide("rien", None)
        assert (sautes[0] == 0 and sautes[2] == ["rien"] and sautes[1] == (
                     "RAPIDE groupes « rien » : sauté · N s · aucun groupe ne porte ce motif\n"
                     "RAPIDE pyright : sauté · pyright introuvable\n"
                     "RAPIDE cliquet : vert · N s · CLIQUET TENU\n"
                     "RAPIDE VERT · N s — la suite entière reste à jouer : cocher l'exige\n")), ("VIT23 : aucun groupe ne porte le motif, pyright absent → sautés, chacun sa raison, VERT") + "\n" + str(sautes)
        o = io.StringIO()
        absent = mod.ecrire_rapide("x", None, mod.jouer_rapide([os.path.join(tr, "absent.exe")], kit), o)
        hors = io.StringIO()
        assert (absent and "RAPIDE x : rouge · " in o.getvalue() and "  ne se lance pas : " in o.getvalue()
                 and mod.main(["rapide", "porte", "--racine", tr], hors) == 1
                 and hors.getvalue().startswith("GARDE: ") and "pas de scripts/test-vlp.py" in hors.getvalue()), ("VIT23 : une commande qui ne se lance pas → rouge, dite ; hors du kit → GARDE, sort 1") + "\n" + str((o.getvalue(), hors.getvalue()))


JOUR_MATIN = "2026-10-01"


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


def noms_worktrees(d):
    """Les noms de dossier des worktrees du dépôt de `d`, le principal en tête (ISO4)."""
    return [os.path.basename(l[len("worktree "):].rstrip("/")) for l in git_matin(d, "worktree", "list", "--porcelain")
            .splitlines() if l.startswith("worktree ")]


def test_ref40_base_refaite(tmp_path):
    """REF40 : un `CONFLIT` sur `scripts/sante-base.json` seul — deux fiches ont réécrit le relevé du cliquet — se
    règle par le relevé refait sur le code fusionné : `FUSIONNÉ` et `BASE REFAITE`, la base égale à celle d'un
    `sante --base` neuf ; une fonction qui empire (base relâchée par `--forcer` dans la fiche) : `CONFLIT` comme avant."""
    if not shutil.which("git"):
        pytest.skip("git absent — la base refaite à la fusion n'est pas testée")
        return
    def fonction(nom, params=""):
        return "def %s(%s):\n    \"\"\"%s.\"\"\"\n    return 1\n\n\n" % (nom, params, nom)

    def base(d):
        return lire(os.path.join(d, "scripts", "sante-base.json")).replace("\r\n", "\n")

    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wa, wb = (os.path.join(tr, n) for n in ("d", "wt-a", "wt-b"))
        os.makedirs(d)
        git_matin(d, "init", "-q", "-b", "main")
        fiches = os.path.join(d, "ctx", "f.md")
        ecrire(fiches, "# F\n\n## W1 [ ] — a\n\n## W2 [ ] — b\n")
        for nom, f in (("a", "f"), ("b", "g"), ("c", "h")):
            ecrire(os.path.join(d, "scripts", nom + ".py"), fonction(f))
        appel(["sante", "--base", "--racine", d])
        commit_matin(d, "départ", 1)
        for nom, w in (("a", wa), ("b", wb)):
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
        # La base est triée par (fichier, fonction) : a.py:f2 (W1) et a2.py:g2 (main) s'insèrent au même endroit,
        # b2.py:k (main) juste avant c.py:h, que W2 change — chaque fusion bute sur la base seule.
        ecrire(os.path.join(wa, "scripts", "a.py"), fonction("f") + fonction("f2"))
        appel(["sante", "--base", "--racine", wa])
        commit_matin(wa, "W1 : a", 2)
        ecrire(os.path.join(wb, "scripts", "c.py"), fonction("h", "a, b, c, d, e, f"))   # 6 arguments, seuil 5
        appel(["sante", "--base", "--racine", wb, "--forcer", "essai"])
        commit_matin(wb, "W2 : b", 3)
        ecrire(os.path.join(d, "scripts", "a2.py"), fonction("g2"))
        ecrire(os.path.join(d, "scripts", "b2.py"), fonction("k"))
        appel(["sante", "--base", "--racine", d])
        commit_matin(d, "main ajoute g2 et k", 4)
        fus = appel(["fusionner", fiches, "W1", "--worktree", wa])
        fusionnee = (base(d), git_matin(d, "status", "--porcelain"), noms_worktrees(d),
                     git_matin(d, "log", "-1", "--format=%s").strip())
        appel(["sante", "--base", "--racine", d])
        neuve = base(d)
        conf = appel(["fusionner", fiches, "W2", "--worktree", wb])
        apres_conf = (git_matin(d, "status", "--porcelain"), code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD"),
                      base(d) == neuve)
    assert (fus[0] == 0 and fus[1].startswith("FUSIONNÉ W1 ") and "\nBASE REFAITE scripts/sante-base.json" in fus[1]
             and fusionnee[1:] == ("", ["d", "wt-b"], "Fusion : W1")), ("REF40 : conflit sur sante-base.json seul → FUSIONNÉ W1 et BASE REFAITE, sort 0, arbre propre, "
             "worktree retiré, commit « Fusion : W1 »") + "\n" + str((fus, fusionnee[1:]))
    assert (fusionnee[0] == neuve and '"f2"' in neuve and '"g2"' in neuve), ("REF40 : la base fusionnée égale celle d'un sante --base neuf, f2 et g2 comprises") + "\n" + str((fusionnee[0], neuve))
    assert (conf[0] == 1 and conf[1].endswith("CONFLIT W2 scripts/sante-base.json\n") and apres_conf == ("", 1, True)), ("REF40 : une fonction qui empire sur le code fusionné → CONFLIT W2 scripts/sante-base.json, sort 1, "
             "arbre propre, pas de MERGE_HEAD, base de main intacte") + "\n" + str((conf, apres_conf))


def test_ref9_tailles(tmp_path):
    """REF9 : le cliquet garde la taille des fichiers `.py` de `scripts/` et de `tests/` — au-dessus de
    `SEUIL_LIGNES`, la taille de base est le plafond, qui descend quand le fichier maigrit ; un fichier neuf, ou de
    1 000 lignes ou moins, ne passe pas le seuil."""
    seuil = mod_sante().SEUIL_LIGNES
    lignes = lambda n: "".join("x%d = %d\n" % (i, i) for i in range(n))
    with tempfile.TemporaryDirectory(dir=tmp_path) as tc:
        def lancer(fichiers, *options):
            """Écrire `fichiers` (`{chemin: lignes}`, None efface), puis lancer `sante --sans-ruff`."""
            for nom, n in fichiers.items():
                if n is None:
                    os.remove(os.path.join(tc, nom))
                else:
                    ecrire(os.path.join(tc, nom), lignes(n))
            return appel(["sante", "--racine", tc, "--sans-ruff"] + list(options))

        pose = lancer({"scripts/gros.py": 1200, "scripts/petit.py": 10}, "--base")
        tenu = lancer({}, "--cliquet")
        grossi = lancer({"scripts/gros.py": 1201}, "--cliquet")
        neuf = lancer({"scripts/gros.py": 1200, "scripts/neuf.py": seuil + 1}, "--cliquet")
        test_neuf = lancer({"scripts/neuf.py": None, "tests/test_gros.py": seuil + 1}, "--cliquet")
        maigri = lancer({"tests/test_gros.py": None, "scripts/gros.py": 1100}, "--base")
        regrossi = lancer({"scripts/gros.py": 1150}, "--cliquet")
        refuse = lancer({}, "--base")
    assert (pose[0] == 0 and tenu[0] == 0 and "TAILLES au-dessus de %d lignes, taille/plafond : scripts/gros.py "
             "1200/1200\n" % seuil in tenu[1] and tenu[1].endswith("CLIQUET TENU\n")), ("REF9 : la base pose les tailles ; le même code → TENU, et la ligne des gros fichiers, taille/plafond") + "\n" + str((pose, tenu))
    assert (grossi[0] == 1 and "TAILLE scripts/gros.py · 1201 lignes, plafond 1200 (base)\n" in grossi[1]), ("REF9 : une ligne ajoutée à un gros fichier → TAILLE …, plafond 1200 (base), ROMPU") + "\n" + str(grossi)
    assert (neuf[0] == 1 and "TAILLE scripts/neuf.py · %d lignes, plafond %d (seuil)\n" % (seuil + 1, seuil) in neuf[1]
             and test_neuf[0] == 1 and "TAILLE tests/test_gros.py · %d lignes" % (seuil + 1) in test_neuf[1]), ("REF9 : un fichier neuf de 1 001 lignes, dans scripts/ ou tests/ → TAILLE …, plafond 1000 (seuil), ROMPU") + "\n" + str((neuf, test_neuf))
    assert (maigri[0] == 0 and regrossi[0] == 1 and "TAILLE scripts/gros.py · 1150 lignes, plafond 1100 (base)\n"
             in regrossi[1] and refuse[0] == 1 and "GARDE: la base ne se relâche pas" in refuse[1]), ("REF9 : un gros fichier qui maigrit (1100) fait baisser sa base : 1150 → ROMPU, plafond 1100, et --base "
             "refuse de relâcher") + "\n" + str((maigri, regrossi, refuse))


def mod_sante():
    """Le module `sante`, chargé comme `cmd_sante` le charge (REF9)."""
    import sante
    return sante


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


def test_sante_comptes(tmp_path):
    """VIT15 : par `ast`, les cinq comptes des sondes égalent ceux de ruff ; les docstrings sont vues ; l'empreinte ne
    voit pas les fins de ligne ; un nom en double devient `nom#2`."""
    import sante
    with tempfile.TemporaryDirectory(dir=tmp_path) as ts:
        ecrire(os.path.join(ts, "sondes.py"), SONDES)
        ecrire(os.path.join(ts, "crlf.py"), SONDES.replace("\n", "\r\n"))
        ecrire(os.path.join(ts, "double.py"), "def f():\n    pass\n\n\ndef f():\n    return 1\n")
        fonctions = sante.mesurer_fichier(ts, os.path.join(ts, "sondes.py"))[0]
        crlf = sante.mesurer_fichier(ts, os.path.join(ts, "crlf.py"))[0]
        double = [f["fonction"] for f in sante.mesurer_fichier(ts, os.path.join(ts, "double.py"))[0]]
    comptes = {f["fonction"]: f["ast"] for f in fonctions}
    assert (comptes == {n: c for n, c in SONDES_ATTENDU.items() if not n.startswith("f_match")}
             and [f["fonction"] for f in fonctions if f["doc"]] == ["f_externe", "f_instr"]
             and [f["empreinte"] for f in crlf] == [f["empreinte"] for f in fonctions] and double == ["f", "f#2"]), ("VIT15 (a) les cinq comptes ast des sondes égalent ceux de ruff 0.16.10 — elif et else-if, boucles et leur "
             "else, try complet, imbrication, fonction et classe imbriquées, arguments muets et de méthode, instructions "
             "à la Pylint ; docstrings vues ; même empreinte en CRLF ; un nom en double → f#2") + "\n" + str((comptes, double))
    if sys.version_info < (3, 10):
        pytest.skip("Python < 3.10 — les sondes de `match` ne sont pas testées")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as ts:
        ecrire(os.path.join(ts, "choix.py"), SONDES_MATCH)
        choix = {f["fonction"]: f["ast"] for f in sante.mesurer_fichier(ts, os.path.join(ts, "choix.py"))[0]}
    assert (choix == {n: c for n, c in SONDES_ATTENDU.items() if n.startswith("f_match")}), ("VIT15 (a bis) match : une branche par case, le dernier gratuit en complexité s'il attrape tout, pas "
             "d'imbrication à lui") + "\n" + str(choix)


def test_sante_ruff(tmp_path):
    """VIT15 : le chemin ruff, sans dépendre de ruff — sa sortie JSON enregistrée se lit, ruff en échec laisse `ast`
    seul ; et ruff réel, s'il est installé, s'accorde à `ast`."""
    import sante
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
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
    assert (lus == {n: SONDES_ATTENDU[n] for n in ("f_externe", "f_externe.interne", "f_chaine", "f_chaine.g")}), ("VIT15 (b) la sortie JSON de ruff, enregistrée : un diagnostic va à la fonction la plus intérieure de sa "
             "ligne, le plus grand des deux PLR1702 de la ligne 89 gagne ; un autre code, un autre fichier ne comptent pas") + "\n" + str(lus)
    assert (version is None and echec.getvalue() == "RUFF ÉCHEC ruff sort 3 — comptes estimés (ast)\n"
             and len(apres) == 15 and all(f["ruff"] is None for f in apres)), ("VIT15 (c) ruff qui sort 3 → `RUFF ÉCHEC ruff sort 3`, puis les comptes ast seuls") + "\n" + str(echec.getvalue())
    if commande is None:
        pytest.skip("ruff absent — son chemin réel n'est pas testé")
        return
    assert (code == 0 and s.startswith("SANTE ruff %s · " % reel) and "AST=RUFF 15/15 fonctions\n" in s), ("VIT15 (c bis) ruff réel %s sur les sondes : ses comptes égalent ceux d'ast, 15/15" % reel) + "\n" + str(s)


def test_sante_reglages():
    """REF3 (D5) : la commande ruff de `sante` lit `pyproject.toml` — sans `--isolated`. Un faux ruff rend ses
    arguments, que `lancer_ruff` reçoit comme sa sortie."""
    import sante
    sortie = sante.lancer_ruff([sys.executable, "-c", "import json, sys; print(json.dumps(sys.argv[1:]))"], ["x.py"])
    args = json.loads(sortie)
    assert ("--isolated" not in args and args[:1] == ["check"] and args[-1] == "x.py"), ("sante : la commande ruff lit pyproject.toml, sans --isolated") + "\n" + str(sortie)


def test_sante_cliquet(tmp_path):
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
    with tempfile.TemporaryDirectory(dir=tmp_path) as tc:
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
        assert (sans_base == (1, "GARDE: pas de base scripts/sante-base.json — `vlp.py sante --base` d'abord\n")
                 and posee == (0, "BASE scripts/sante-base.json · 4 fonctions · sans ruff\n")
                 and tenu == (0, tete + bilan % (4, 0, 0, 0) + "\nCLIQUET TENU\n")), ("VIT15 (d) sans base → GARDE:, sort 1 ; --base pose 4 fonctions ; le même code → CLIQUET TENU") + "\n" + str((sans_base, posee, tenu))
        empire = lancer({"m.py": ifs(12, "grosse") + ifs(1, "petite") + muette}, "--cliquet")
        assert (empire == (1, tete + "EMPIRE scripts/m.py:1 grosse · complexité 12 → 13, seuil 10\n"
                            + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n")), ("VIT15 (e) une vieille fonction déjà au-dessus du seuil empire (complexité 12 → 13) → EMPIRE, ROMPU, sort "
                 "1 ; ses branches montent au seuil (12), sans écart — mutant : le plafond relâché d'un cran") + "\n" + str(empire)
        sous_seuil = lancer({"m.py": ifs(11, "grosse") + ifs(9, "petite") + muette}, "--cliquet")
        passe = lancer({"m.py": ifs(11, "grosse") + ifs(10, "petite") + muette}, "--cliquet")
        assert (sous_seuil == (0, tete + bilan % (4, 1, 0, 0) + "\nCLIQUET TENU\n")
                 and passe == (1, tete + "EMPIRE scripts/m.py:28 petite · complexité 2 → 11, seuil 10\n"
                               + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n")), ("VIT15 (f) une vieille fonction sous les seuils grandit jusqu'au seuil (complexité 2 → 10) → TENU ; le "
                 "passer (→ 11) → EMPIRE") + "\n" + str((sous_seuil, passe))
        neuves = lancer({"m.py": m + "\n\n" + ifs(10, "neuve_grosse") + "def neuve(a):\n    return a\n"}, "--cliquet")
        tests = lancer({"m.py": m, "test-m.py": longue(70) + ifs(10, "test_neuf").replace('    """Des if."""\n', "")},
                       "--cliquet")
        assert (neuves == (1, tete + "SEUIL scripts/m.py:39 neuve_grosse · complexité 11, seuil 10 (neuve)\n"
                            "DOCSTRING scripts/m.py:64 neuve · sans docstring (neuve)\n"
                            + bilan % (6, 0, 0, 2) + "\nCLIQUET ROMPU · 2 écart(s)\n")
                 and tests == (1, tete + "SEUIL scripts/test-m.py:75 test_neuf · complexité 11, seuil 10 (neuve)\n"
                               + bilan % (5, 1, 0, 1) + "\nCLIQUET ROMPU · 1 écart(s)\n")), ("VIT15 (g) une fonction neuve au-dessus d'un seuil → SEUIL, une neuve sans docstring → DOCSTRING ; dans un "
                 "test-*.py, ni instructions (70) ni docstring, mais la complexité tient") + "\n" + str((neuves, tests))
        touchee = lancer({"m.py": m.replace(muette, "def muette(a):\n    return a + 1\n"), "test-m.py": longue(60)},
                         "--cliquet")
        renommee = lancer({"m.py": ifs(11, "grosse") + ifs(1, "petite2") + muette}, "--cliquet")
        deplacee = lancer({"m.py": ifs(11, "grosse") + muette, "m2.py": ifs(1, "petite")}, "--cliquet")
        assert (touchee == (1, tete + "DOCSTRING scripts/m.py:35 muette · sans docstring (touchée)\n"
                             + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n")
                 and renommee == deplacee == (0, tete + bilan % (4, 0, 1, 0) + "\nCLIQUET TENU\n")), ("VIT15 (h) une vieille fonction touchée sans docstring → DOCSTRING (intacte, elle passait) ; renommée ou "
                 "déplacée dans un autre fichier, même empreinte → suivie, TENU") + "\n" + str((touchee, renommee, deplacee))
        mieux = lancer({"m.py": ifs(9, "grosse") + ifs(1, "petite") + muette, "m2.py": None}, "--cliquet")
        verrou = lancer({}, "--base")
        rechute = lancer({"m.py": ifs(10, "grosse") + ifs(1, "petite") + muette}, "--cliquet")
        assert (mieux == (0, tete + bilan % (4, 1, 0, 0) + " · améliorées 1 : `vlp.py sante --base` les verrouille\n"
                           "CLIQUET TENU\n") and verrou[0] == 0
                 and rechute == (1, tete + "EMPIRE scripts/m.py:1 grosse · complexité 10 → 11, seuil 10\n"
                                 + bilan % (4, 1, 0, 0) + "\nCLIQUET ROMPU · 1 écart(s)\n")), ("VIT15 (i) une amélioration se dit, --base la verrouille : remonter de 10 à 11, sous l'ancienne base (12), "
                 "→ EMPIRE") + "\n" + str((mieux, verrou, rechute))
        avant = mod.lire(base)
        refus = lancer({}, "--base")
        intacte = mod.lire(base) == avant
        forcee = lancer({}, "--base", "--forcer", "essai")
        trace = json.loads(mod.lire(base))["forcee"]
        assert (refus == (1, "EMPIRE scripts/m.py:1 grosse · complexité 10 → 11, seuil 10\n"
                           + "GARDE: la base ne se relâche pas : 1 écart(s) ci-dessus — corrige, ou "
                           + "`--base --forcer \"<raison>\"`, rien écrit\n")
                 and intacte and forcee == (0, "BASE scripts/sante-base.json · 4 fonctions · sans ruff · relâchée : essai\n")
                 and len(trace) == 1 and trace[0]["raison"] == "essai" and trace[0]["ecarts"] == 1), ("VIT15 (j) --base qui relâcherait → l'écart, GARDE:, sort 1, base intacte ; --forcer écrit, et garde sa "
                 "raison dans la base") + "\n" + str((refus, intacte, forcee, trace))
        seul = lancer({}, "--forcer", "x")
        ecrire(base, "{}")
        illisible = lancer({}, "--cliquet")
        casse = lancer({"m.py": "def (\n"}, "--cliquet")
    assert (seul == (1, "GARDE: --forcer ne va qu'avec --base\n")
             and illisible[0] == 1 and illisible[1].endswith("sante-base.json : base illisible, format 1 attendu\n")
             and casse[0] == 1 and casse[1].startswith("GARDE: ") and "m.py:1 : " in casse[1]), ("VIT15 (k) --forcer sans --base, une base illisible, un fichier qui ne se lit pas → GARDE:, sort 1") + "\n" + str((seul, illisible, casse))


def test_sante_si_base(tmp_path):
    """VIT16 : `--base --si-base`, la ligne de `/vlp:tache` à chaque fiche — sans base, rien d'écrit, même lancé hors du
    kit par `--racine .` ; avec une base, comme `--base` : elle se reprend, ou refuse de se relâcher."""
    import hashlib
    base_kit = os.path.join(ICI, "sante-base.json")
    empreinte_kit = hashlib.sha1(open(base_kit, "rb").read()).hexdigest()
    m = 'def f(a):\n    """Rendre a."""\n    return a\n'
    ici = os.getcwd()
    with tempfile.TemporaryDirectory(dir=tmp_path) as tv:
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
        assert (dehors == sans_scripts == (0, "SANS BASE scripts/sante-base.json · rien écrit\n") and cree == ["m.py"]
                 and hashlib.sha1(open(base_kit, "rb").read()).hexdigest() == empreinte_kit), ("VIT16 (a) --si-base sans base → SANS BASE, sort 0, rien d'écrit — dans un projet sans `scripts/`, et "
                 "hors du kit par `--racine .`, la base du kit identique à l'octet — mutant : --si-base ignoré") + "\n" + str((dehors, sans_scripts, cree))
        posee = appel(["sante", "--base", "--racine", equipe, "--sans-ruff"])
        reprise = appel(["sante", "--base", "--si-base", "--racine", equipe, "--sans-ruff"])
        ecrire(os.path.join(equipe, "scripts", "m.py"), m + "\n\ndef g(a):\n    return a\n")
        refus = appel(["sante", "--base", "--si-base", "--racine", equipe, "--sans-ruff"])
        seul = appel(["sante", "--si-base", "--racine", equipe, "--sans-ruff"])
    assert (posee == reprise == (0, "BASE scripts/sante-base.json · 1 fonctions · sans ruff\n")
             and refus[0] == 1 and "GARDE: la base ne se relâche pas : 1 écart(s)" in refus[1]
             and seul == (1, "GARDE: --si-base ne va qu'avec --base\n")), ("VIT16 (b) avec une base, --si-base fait comme --base : BASE, sort 0 ; une fonction neuve sans docstring → "
             "GARDE:, sort 1 ; --si-base sans --base → GARDE:") + "\n" + str((posee, reprise, refus, seul))


def test_sante_kit():
    """VIT15 : le kit tient son propre cliquet — une fonction qui empire, ou neuve au-dessus d'un seuil ou sans
    docstring, fait tomber la suite. Sauté sous `vlp.py mutant` (`VLP_TOUS_ECARTS=1`) : un mutant touche toujours sa
    fonction, et une docstring qui y manque le dirait « attrapé » sans qu'aucun test ne l'ait vu."""
    if os.environ.get("VLP_TOUS_ECARTS") == "1":
        pytest.skip("sous le mutant, le cliquet du kit ne joue pas")
        return
    code, s = appel(["sante", "--cliquet"])
    assert (code == 0 and s.endswith("CLIQUET TENU\n")), ("VIT15 (l) le kit tient son cliquet : `vlp.py sante --cliquet` → CLIQUET TENU ; sinon, chaque écart y est "
             "nommé — corrige la fonction, `--base --forcer` seulement si le relâchement est voulu") + "\n" + str(s)
