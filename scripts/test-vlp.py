#!/usr/bin/env python3
"""Teste vlp.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle les sous-commandes, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
`--seul <motif>` (ou `VLP_SEUL`) : ne joue que les groupes dont le nom ou le texte porte le motif (VIT10).
"""
import importlib.util
import inspect
import io
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
mod.etat.TAMPON_HOOKS = None
# `clore` refait les données de la page d'enchaînement du vrai kit : un test de clôture ne le fait pas, sauf celui
# qui le vérifie, sur un kit à lui (ORD5).
mod.etat.SOURCE_ORDRE = None

# `ouvrir` et `cocher` notent CLAUDE_CODE_SESSION_ID : un test le fixe lui-même, jamais celui de la
# session qui lance la suite (chantier CAD).
os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
# Une fiche jouée la nuit lance la suite sous les variables de la nuit : `carte` imprimerait `NUIT=1` partout,
# `plan ecrire` refuserait, `VLP_CANAL` passerait au faux `claude`. Un test les fixe lui-même (NUI12, ENV1).
for _nom in mod.carnet.VARIABLES_NUIT:
    os.environ.pop(_nom, None)


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte)


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
import couverture  # REF8 : lancée seule, la suite se relance sous `coverage`, avant la boucle et le pont
MESURE = couverture.mesurer(mod.etat.KIT, os.path.abspath(__file__), sys.argv[1:], mod.empreinte_kit(mod.etat.KIT)) if couverture.a_mesurer(SEUL) else None
if MESURE is not None:
    sys.exit(MESURE)


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


def lancer_boucle(argv=None, env=None):
    """Lancer `test-boucle.py` — ou `argv`, depuis la racine du kit : le pont pytest (REF19) — sans l'attendre (VIT7) :
    rendre `(processus, stdout, stderr)`, ses deux sorties dans des fichiers temporaires — un tube plein bloquerait
    l'enfant. Un arrêt de la suite avant la récolte le tue à la sortie (`arreter_boucle`, par `atexit`)."""
    import atexit
    sorties = [tempfile.TemporaryFile("w+", encoding="utf-8", errors="replace") for _ in range(2)]
    p = subprocess.Popen(argv or [sys.executable, os.path.join(ICI, "test-boucle.py")], stdout=sorties[0], stderr=sorties[1],
                         cwd=os.path.join(ICI, "..") if argv else None, env=dict(os.environ, PYTHONIOENCODING="utf-8", **(env or {})))
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
PONT_ARGV = [shutil.which("uv") or "uv", "run", "--frozen", "pytest", "-q", "-n", "4"]  # REF19 : 40,9 s contre 66,6 en série
PONT = None if os.environ.get("VLP_PONT") == "1" or SEUL else lancer_boucle(PONT_ARGV, {"VLP_PONT": "1"})  # REF19
# Le code que cette suite joue, pris au départ : une suite verte l'écrit à la fin, et `cocher` exige de le retrouver (VIT11).
EMPREINTE_DEPART = mod.empreinte_kit(mod.etat.KIT)


def noter_si_verte():
    """Noter `EMPREINTE_DEPART` comme celle de la dernière suite entière verte — jamais sous `vlp.py mutant`
    (`VLP_TOUS_ECARTS=1`), qui joue une copie mutée (VIT11), ni sous `--seul`, qui n'en joue qu'une part (VIT10)."""
    if os.environ.get("VLP_TOUS_ECARTS") != "1" and not SEUL:
        mod.noter_suite_verte(mod.etat.KIT, EMPREINTE_DEPART)


def appel(argv):
    s = io.StringIO()
    code = mod.main(argv, s)
    return code, s.getvalue()




def tester_pont_pytest():
    """REF4 : le pont vers la suite `pytest` de `tests/`, par l'atelier (`uv run --frozen pytest`, syrupy n'est que là),
    en parallèle (`PONT_ARGV`), qui sort 0 ; uv ou pytest manque : un écart, jamais un saut silencieux. Lancé dès le
    début de la suite (`PONT`, REF19) et récolté ici, en fin ; sous `--seul`, lancé et attendu ici. Pas sous
    `VLP_PONT=1` : une suite lancée depuis pytest le relancerait sans fin (REF7, vu le 2026-10-18)."""
    if os.environ.get("VLP_PONT") == "1":
        print("SAUTÉ: pont pytest — déjà dans une suite lancée par le pont (VLP_PONT=1)")
        return
    try:
        p, sortie, erreur = PONT or lancer_boucle(PONT_ARGV, {"VLP_PONT": "1"})
        code = p.wait(timeout=600)
        sortie.seek(0)
        erreur.seek(0)
        texte = (sortie.read() + erreur.read()).strip()
    except (OSError, subprocess.SubprocessError) as e:
        code, texte = None, "uv run pytest ne se lance pas : %s" % e
    verifier("REF4 pont : uv run --frozen pytest -q sur tests/ sort 0 (l'atelier : uv sync)", code == 0,
             "\n".join(texte.splitlines()[-40:]))


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


def tester_ref5_parite():
    """REF5 : `vlp.py parite` relie chaque `verifier` d'un groupe de `scripts/test-vlp.py` à l'`assert` de `tests/`
    qui porte son libellé en message — `MIGRÉ`, `PARTIEL … — manque :`, `RESTE`, puis le total. Un libellé formaté
    (`"… %d" % n`) se compare par son gabarit ; une fonction d'aide compte au groupe qui l'appelle."""
    with tempfile.TemporaryDirectory() as r:
        ecrire(os.path.join(r, "scripts", "test-vlp.py"),
               "def aide_c():\n    verifier(\"c1\", True, '')\n\n\n"
               "def tester_a():\n    verifier(\"a1\", True, '')\n    verifier(\"a2 : %d fiches\" % 3, True, '')\n\n\n"
               "def tester_b():\n    verifier(\"b1\", True, '')\n    verifier(\"b2\", True, '')\n\n\n"
               "def tester_c():\n    aide_c()\n\n\n"
               "groupe(tester_a)\ngroupe(tester_b)\ngroupe(tester_c)\n")
        ecrire(os.path.join(r, "tests", "test_ab.py"),
               "def test_a():\n    assert True, \"a1\" + \"\\n\" + str(0)\n    assert True, \"a2 : %d fiches\" % 3\n\n\n"
               "def test_b():\n    assert True, (\"b\"\n                  \"1\")\n")
        code, s = appel(["parite", "--racine", r])
    verifier("REF5 : parite rend MIGRÉ, PARTIEL — manque : <nom>, RESTE (aide comprise), puis le total",
             code == 0 and s == "MIGRÉ tester_a 2/2\nPARTIEL tester_b 1/2 — manque : b2\nRESTE tester_c 0/1\n"
             "PARITE 3 groupes · migrés 1 · partiels 1 · restent 1 · vérifications 3/5\n", s)


groupe(tester_ref5_parite)


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
             porte_motif(tester_mesure_tokens, "une voisine de celle-ci")
             and not porte_motif(tester_ref5_parite, "une voisine de celle-ci"),
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


groupe(tester_seul)


groupe(tester_boucle_nuit)
groupe(tester_pont_pytest)    # récolte le pont lancé au début (REF19)
groupe(tester_boucle)    # en dernier : les trois quarts de la suite, un écart d'ailleurs tombe avant lui (VIT2)

if ECARTS:
    print("FIN: %d écart(s)" % len(ECARTS))     # la suite est allée au bout : `vlp.py mutant` ne la dit pas PLANTÉ
    sys.exit(1)
noter_si_verte()
bilan_seul()
print("OK")
