#!/usr/bin/env python3
"""Teste vlp.py sans fixture sur disque.

Construit des projets dans un dossier temporaire, appelle les sous-commandes, compare.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
`--seul <motif>` (ou `VLP_SEUL`) : ne joue que les groupes dont le nom ou le texte porte le motif (VIT10).
"""
import datetime
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
        carte = mod.lire(os.path.join(p, "CHANTIER.md"))
        ecrire(os.path.join(p, "CHANTIER.md"), carte + "- **contexte dans Git** : non — dépôt public\n")
        s = io.StringIO()
        mod.ecarts_git(p, s)
        ecrire(os.path.join(p, "CHANTIER.md"), carte)
        verifier("NWT (c) niveau git : l'ignoré déclaré exprès (« contexte dans Git » : non) se dit en une ligne EXPRÈS, "
                 "sans écart ; le non ajouté reste un écart",
                 "EXPRÈS: git: 1 chemin(s) ignoré(s) exprès — CHANTIER.md, « contexte dans Git » : non — dépôt public ; "
                 "aucun écart compté\n" in s.getvalue() and "ignoré par" not in s.getvalue()
                 and "ÉCART: git: ctx/09-neuf.md — non ajouté" in s.getvalue(), s.getvalue())
        ecrire(os.path.join(p, ".gitignore"), "# rien\n")
        git(p, "add", "-A")
        ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pn", "ctx/") + "- **kit** : D:/Projets/kit, lié dans"
               " ~/.claude/skills/vlp\n")
        e = ecarts_git(p)
        verifier("niveau git : la ligne « kit » à chemin de machine",
                 len(e) == 1 and "la ligne « kit » porte un chemin de machine" in e[0], e)


groupe(tester_niveau_git)


def appel(argv):
    s = io.StringIO()
    code = mod.main(argv, s)
    return code, s.getvalue()


def valide(texte):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "v.md")
        ecrire(f, texte)
        code, s = appel(["valider", f])
        return code, s.replace(f, "F")


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


# total_clos : relire aussi les lignes closes sous 1 000, qui n'ont pas de parenthèses.
def ligne_close(c):
    """Une ligne close au format de cmd_clore, avec plage Q1–Q2, date 2026-05-06, et coût c."""
    return f'          <tr>\n            <td>Test <span class="badge" data-etat="clos">clos</span></td>\n            <td class="mono">Q1–Q2</td><td class="mono">2026-05-06</td>\n            <td class="mono">{c}</td>\n            <td>Test</td>\n          </tr>\n'


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


# --- hook : le PostToolUse du plugin -----------------------------------------

def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


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
                verifier("REF29 : clore sans couts.svg dit LIRE sans lui",
                         "\nLIRE vlp.css vlp.js\n" in s
                         and not os.path.exists(os.path.join(te, "ctx", "artefacts", "couts.svg")), s)
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


def tester_clore_reperes_et_routage():
    """Dette SCH (Cairn, 2026-10-14) : une rangée de TODO dont le code suit des repères (🔴📅) se trouve, un code
    cité plus loin dans la ligne non ; une ligne « relire un chantier clos — … » prolongée compte comme présente."""
    todo = ["| # | Chantier | a | b | c |", "|---|---|---|---|---|", "| 1 | 🔴📅 `SCH` — x | a | b | — |",
            "| 2 | 🟡💤 ⏸️ `HD` — y | voir `REG` | b | — |", "| 3 | `REG` — z | a | b | — |"]
    verifier("dette SCH : rangée trouvée derrière ses repères, code cité ailleurs ignoré — mutant : `\\s*` au lieu de `[^|`]*`",
             mod.rangee_todo(todo, "SCH") == (0, 2, "1") and mod.rangee_todo(todo, "HD") == (0, 3, "2")
             and mod.rangee_todo(todo, "REG") == (0, 4, "3") and mod.rangee_todo(todo, "SC") == (0, None, None),
             [mod.rangee_todo(todo, c) for c in ("SCH", "HD", "REG", "SC")])
    cl = ["| T | O |", "|---|---|", "| relire un chantier clos — filet de tests | `ctx/00-INDEX-archive.md` |"]
    verifier("dette SCH : ligne « relire un chantier clos — … » reconnue, « closes » non — mutant : startswith(ROUTAGE_CLOS)",
             mod.rang_routage_clos(cl) == 2 and mod.rang_routage_clos(["| relire un chantier clos | x |"]) == 0
             and mod.rang_routage_clos(["| relire un chantier closes | x |"]) is None, mod.rang_routage_clos(cl))
    vieux = ["| T | O |", "| relire le chantier E (e) | x |"]
    verifier("dette SCH : sans « relire un chantier clos », le repli « relire le chantier » ; sans repli, None",
             mod.rang_routage_clos(vieux, "| relire le chantier") == 1 and mod.rang_routage_clos(vieux) is None
             and mod.rang_routage_clos(cl, "| relire le chantier") == 2, vieux)


groupe(tester_clore_reperes_et_routage)


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
        res = appel(["oter", to, "BBB", "--raison", "fait cette nuit", "--date", "2026-10-12", "--fait"])
        lu, carte_ = open(chemin, encoding="utf-8").read(), open(os.path.join(to, "CHANTIER.md"), encoding="utf-8").read()
        prises = mod.lettres_prises(carte_.split("\n"))
        verifier("oter --fait : la lettre est prise, ce qui l'attend n'est plus bloqué — mutant : sans l'ajout aux lettres",
                 res[0] == 0 and res[1].rstrip().endswith("· lettre prise")
                 and "U (test), BBB (b, sans fiche). Un nouveau chantier" in carte_
                 and not mod.est_bloque("`BBB`", prises, []), (res, carte_))
        verifier("oter --fait : « fait sans fiche » dans la provenance et au journal",
                 "4, `BBB`, fait sans fiche le 2026-10-12 : fait cette nuit.\n" in lu
                 and "## 2026-10-12 — `BBB` fait sans fiche, retiré de la TODO (n° 4)\n" in lu, lu)


groupe(tester_oter)


def tester_todo_sans_code():
    """Dette FIN (Fil-Rouge, 2026-10-14) : une TODO sans codes (`| 10 | Finitions … |`) — `clore` trouve la rangée par
    le titre du chantier, `oter` par son numéro ; un routage sans « relire un chantier clos » ni « relire le
    chantier », mais des lignes **clos** : `ouvrir` y pose sa ligne, que `clore` retrouve."""
    gabarit = lambda nom: open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
    lire = lambda c: open(c, encoding="utf-8").read()
    todo = ["| # | Chantier | a | b | c |", "|---|---|---|---|---|", "| 10 | Finitions de l'API : erreurs et Swagger | a | b | — |",
            "| 11 | Réparer le banc | a | b | — |", "| 12 | Réparer le banc | a | b | — |"]
    verifier("dette FIN : rangée par numéro, ou par titre (apostrophe courbe, casse) s'il est seul ; deux pareils, aucune "
             "— mutant : sans le repli du titre",
             mod.rangee_todo(todo, "11") == (0, 3, "11") and mod.rangee_todo(todo, "1") == (0, None, None)
             and mod.rangee_todo(todo, "FIN", "finitions de l’API :  erreurs et Swagger") == (0, 2, "10")
             and mod.rangee_todo(todo, "BAN", "Réparer le banc") == (0, None, None)
             and mod.rangee_todo(todo, "FIN") == (0, None, None),
             [mod.rangee_todo(todo, "11"), mod.rangee_todo(todo, "FIN", "finitions de l’API :  erreurs et Swagger")])
    etat = ("# État\n\nProvenance : 10, de x ; 11, de y.\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
            "|---|---|---|---|---|\n| 10 | Finitions de l'API : erreurs et Swagger | a | 1 | `DRO` |\n"
            "| 11 | Réparer le banc | a | 1 | rien |\n| 12 | Seed | a | 1 | 10..11 |\n\n## Journal des décisions\n\n## 2026-10-01 — x\n")
    with tempfile.TemporaryDirectory() as tf:
        ancien = os.environ.get("CLAUDE_CODE_SESSION_ID")
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        carte_f = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
                   "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : DRO (droits).\n")
        ecrire(os.path.join(tf, "CHANTIER.md"), carte_f)
        ecrire(os.path.join(tf, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `12-dro.md` | on relit |\n")
        routage = ("| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n"
                   "| relire une fiche `DRO1` à `DRO2` | `ctx/12-dro.md` — chantier **clos** le 2026-10-13 |\n| reprendre | y |\n")
        ecrire(os.path.join(tf, "CLAUDE.md"), routage)
        chemin = os.path.join(tf, "ctx", "08-etat.md")
        ecrire(chemin, etat)
        ecrire(os.path.join(tf, "ctx", "13-fin.md"), "# Chantier FIN — Finitions de l'API : erreurs et Swagger\n\n"
               "**Fait.** Rien.\n\n## FIN1 [x] — a\n")
        ecrire(os.path.join(tf, "ctx", "artefacts", "13-fin.html"), gabarit("artefact-chantier.html"))
        ecrire(os.path.join(tf, "ctx", "artefacts", "feuille-de-route.html"), gabarit("artefact-feuille-de-route.html"))
        code, s = appel(["ouvrir", tf, "--fiches", "ctx/13-fin.md", "--titre", "Finitions de l'API : erreurs et Swagger"])
        verifier("dette FIN : ouvrir pose sa ligne avant la première ligne **clos** — mutant : sans ce repli",
                 code == 0 and "routage +1" in s and "GARDE" not in s and "| modifier | x |\n| jouer une fiche du chantier FIN "
                 "(finitions de l'API : erreurs et Swagger) | `ctx/13-fin.md` — chantier **ouvert**, par `/vlp:tache FIN<n>` |\n"
                 "| relire une fiche `DRO1`" in lire(os.path.join(tf, "CLAUDE.md")), (s, lire(os.path.join(tf, "CLAUDE.md"))))
        for code_, quoi in (("10", "ouvert, trouvé par son titre"), ("99", "absent")):
            res = appel(["oter", tf, code_, "--raison", "r", "--date", "2026-10-14"])
            verifier("dette FIN : oter refuse un numéro %s — GARDE, fichier inchangé" % quoi,
                     res[0] == 1 and res[1].startswith("GARDE: ") and lire(chemin) == etat, res)
        res = appel(["oter", tf, "11", "--raison", "fait à la main", "--date", "2026-10-14", "--fait"])
        lu = lire(chemin)
        verifier("dette FIN : oter par numéro ôte la rangée, marque provenance et journal, ne prend aucune lettre "
                 "— mutant : sans la branche du numéro",
                 res[0] == 0 and "| 11 |" not in lu and "| 10 |" in lu and "| 12 |" in lu
                 and "11, « Réparer le banc », fait sans fiche le 2026-10-14 : fait à la main.\n" in lu
                 and "## 2026-10-14 — « Réparer le banc » fait sans fiche, retiré de la TODO (n° 11)\n" in lu
                 and lire(os.path.join(tf, "CHANTIER.md")) == carte_f and "lettre prise" not in res[1], (res, lu))
        code, s = appel(["clore", tf, "--livre", "fini", "--date", "2026-10-14"])
        lu, claude_lu = lire(chemin), lire(os.path.join(tf, "CLAUDE.md"))
        verifier("dette FIN : clore trouve la rangée par le titre du chantier, et la ligne de routage posée par ouvrir",
                 code == 0 and "TODO `FIN` ôtée · n° 10\n" in s and "| 10 |" not in lu and "| 12 | Seed" in lu
                 and "10, `FIN`, clos le 2026-10-14." in lu and "routage 1" in s and "jouer une fiche" not in claude_lu
                 and "ligne « jouer une fiche" not in s, (s, lu, claude_lu))
        if ancien is None:
            del os.environ["CLAUDE_CODE_SESSION_ID"]
        else:
            os.environ["CLAUDE_CODE_SESSION_ID"] = ancien


groupe(tester_todo_sans_code)


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
                 '</details><span class="meta"><span class="seg">2 fiches</span></span></li>' in html
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
        verifier("REF29 : clore, coût mesuré, dit LIRE avec couts.svg",
                 "\nLIRE vlp.css vlp.js couts.svg\n" in s and os.path.exists(os.path.join(os.path.dirname(fdr), "couts.svg")), s)
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
            regenerer_vrai = mod.noyau.page.regenerer
            mod.noyau.page.regenerer = lambda *x, p=prix: (lambda r: r[:3] + ((2_000_000, 3, p), r[4]))(regenerer_vrai(*x))
            try:
                code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
            finally:
                mod.noyau.page.regenerer = regenerer_vrai
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


# --- chantier ESS : les essais d'une session, par le dossier de leur bac -------


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


# --- Z2 : le projet d'essai de son groupe, migré (REF50, tests/test_fiches.py) ; les groupes qui suivent le gardent ---
GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


# NIV1 — la ligne d'injection ne laisse entrer aucun message de lanceur dans la carte.
RACINE = os.path.dirname(ICI)


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


def tester_ena2_arriere_plan():
    """ENA2 : la fiche et son relecteur partent par l'outil `Agent` en arrière-plan — la skill forkée
    attendait la fin même en `background: true` (bac `ENA2`, 2026-10-12), la conversation restait prise
    tout le temps de la fiche (≈ 45 min le 2026-10-03, `ENA1`) ; le chef lit le statut à la notification
    de fin, pas dans ce que l'appel rend tout de suite."""
    chef = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    plat = " ".join(chef.split())
    verifier("ENA2 : fiche et relecteur lancés par Agent, en arrière-plan",
             'subagent_type: "vlp:fiche"' in plat and 'subagent_type: "vlp:relecture"' in plat
             and plat.count("run_in_background: true") == 2, "skills/enchainer/SKILL.md")
    verifier("ENA2 : le prompt de la fiche se lit par FICHE_A_JOUER (id suivi d'une espace, pas d'un point)",
             "Fiche à jouer : <fiche> " in plat, "skills/enchainer/SKILL.md")
    verifier("ENA2 : le chef lit le Result à la notification de fin",
             "**notification de fin**" in chef, "absent de skills/enchainer/SKILL.md")


groupe(tester_ena2_arriere_plan)


def tester_gai1_rejeu():
    """GAI1 : le rejeu après `CONFLIT` sort du plafond et de `--tourne` — il repart aussitôt ; seul un 2ᵉ `CONFLIT`
    de la même fiche attend que plus rien ne tourne (les deux causes d'`ISO7`, tranchées le 2026-10-17)."""
    plat = " ".join(io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read().split())
    verifier("GAI1 : le plafond compte chaque fiche une fois, le rejeu après CONFLIT hors plafond",
             "plafond compte chaque fiche une fois, plus chaque rejeu après `REFUSÉE` ; un rejeu après `CONFLIT`, non"
             in plat and "chaque départ, rejeu compris" not in plat, "skills/enchainer/SKILL.md")
    verifier("GAI1 : CONFLIT sort de --tourne et repart aussitôt ; le 2ᵉ attend",
             "`CONFLIT` : la fiche sort de `--tourne` et repart aussitôt" in plat
             and "à son 2ᵉ `CONFLIT`, elle y reste" in plat, "skills/enchainer/SKILL.md")


groupe(tester_gai1_rejeu)


def tester_ena4_commiter():
    """ENA4 : `commiter` — coche la fiche et ne commite que ses fichiers changés et le fichier de fiches ; un changé
    hors de sa ligne **Fichiers** se dit `HORS:` et reste hors du commit (jamais `git add -A`)."""
    with tempfile.TemporaryDirectory() as t:
        d = os.path.join(t, "d")
        os.makedirs(os.path.join(d, "ctx"))
        fiches = os.path.join(d, "ctx", "fiches.md")
        ecrire(fiches, "# Essai\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [ ] — Toucher %s\n\n**Dépend de** : rien.\n**Fichiers** : `src/%s`%s.\n\n"
            "**Critère de fin**\nRien.\n<!-- /FICHE -->\n" % (f, f, n, n, p) for f, n, p in (
                ("C1", "a.py", " (la ligne « **b** » seule)"), ("C2", "b.py", ""))))
        for n in ("src/a.py", "src/b.py", "scripts/sante-base.json"):
            os.makedirs(os.path.dirname(os.path.join(d, n)), exist_ok=True)
            ecrire(os.path.join(d, n), "x = 1\n")
        vieux = dict(os.environ)
        os.environ.update(GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t",
                          GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        try:
            ecrire(os.environ["GIT_CONFIG_GLOBAL"], "")
            for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "départ"]):
                subprocess.run(["git"] + args, cwd=d, check=True, capture_output=True)
            for n in ("src/a.py", "src/b.py", "scripts/sante-base.json"):
                ecrire(os.path.join(d, n), "x = 2\n")
            code, sortie = appel(["commiter", fiches, "C1"])
            montre = subprocess.run(["git", "show", "--name-only", "--format=%s", "HEAD"], cwd=d, capture_output=True,
                                    encoding="utf-8").stdout.split()
            reste = subprocess.run(["git", "status", "--porcelain"], cwd=d, capture_output=True, encoding="utf-8").stdout
            # Puis le même dépôt devient le kit (`est_kit`) : C2 y prend la base du cliquet, commun.
            marques = (".claude-plugin/plugin.json", "scripts/test-vlp.py")
            for n in marques:
                os.makedirs(os.path.dirname(os.path.join(d, n)), exist_ok=True)
                ecrire(os.path.join(d, n), "{}\n")
            for args in (["add", "--"] + list(marques), ["commit", "-q", "-m", "kit"]):
                subprocess.run(["git"] + args, cwd=d, check=True, capture_output=True)
            mod.noter_suite_verte(d, mod.empreinte_kit(d))  # cocher dans le kit exige la suite verte (VIT11)
            kit = appel(["commiter", fiches, "C2"])
            montre_kit = subprocess.run(["git", "show", "--name-only", "--format=%s", "HEAD"], cwd=d,
                                        capture_output=True, encoding="utf-8").stdout.split()
        finally:
            os.environ.clear()
            os.environ.update(vieux)
        verifier("ENA4 : commiter C1 ne prend que src/a.py et le fichier de fiches, coché",
                 code == 0 and "src/a.py" in montre and "ctx/fiches.md" in montre and "src/b.py" not in montre
                 and "## C1 [x]" in io.open(fiches, encoding="utf-8").read(), repr((code, sortie, montre)))
        verifier("ENA4 : src/b.py dit HORS: et reste à commiter — le « **b** » de la prose n'est pas un motif (ENA5)",
                 "src/b.py" in sortie.partition("HORS:")[2] and "M src/b.py" in reste, repr((sortie, reste)))
        verifier("ENA4 : hors du kit, scripts/sante-base.json n'est pas un commun — HORS:, laissé hors du commit",
                 "scripts/sante-base.json" not in montre and "scripts/sante-base.json" in sortie.partition("HORS:")[2]
                 and "M scripts/sante-base.json" in reste, repr((sortie, montre, reste)))
        verifier("ENA4 : dans le kit, scripts/sante-base.json est un commun — commité avec src/b.py",
                 "scripts/sante-base.json" in montre_kit and "src/b.py" in montre_kit, repr((kit, montre_kit)))


groupe(tester_ena4_commiter)


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
        regenerer_vrai = mod.noyau.page.regenerer
        mod.noyau.page.regenerer = lambda *x: (lambda r: r[:3] + ((4321, 3, None), r[4]))(regenerer_vrai(*x))
        try:
            code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "950", "--date", "2026-09-25"])
        finally:
            mod.noyau.page.regenerer = regenerer_vrai
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
        angel = os.path.join(t, "deco.as")
        ecrire(angel, "class Deco {\n    void Poser() { int x = 1; }\n}\n")
        o = io.StringIO()
        try:
            code = mod.main(["symboles", angel], o)
        except SyntaxError as e:    # l'ancien comportement : le traceback, rendu en écart
            code = "traceback %s" % e
        verifier("SYM : symboles sur un fichier non Python, une GARDE: et sort 1, jamais un traceback",
                 code == 1 and o.getvalue().startswith("GARDE: %s ne se lit pas en Python" % angel)
                 and o.getvalue().count("\n") == 1, o.getvalue())


groupe(tester_symboles)


ORDRE_SOURCE = """# L'ordre

## Les projets

| Clé | Dossier |
|---|---|
| k | `.` |
| a | `autre` |
| x | `absent` |

## La cible

| Projet | Codes |
|---|---|
| a | `A1` |

## Le chemin conseillé

| Pas | Projet | Nom | Coût |
|---|---|---|---|
| `K9` | k | fait avant | ✅ fait le 2026-10-01 |
| `K1` | k | | une note |
| `A1` | a | | |
| `A2` | a | une fiche | 1 fiche |
| `X1` | x | | |

## Les niveaux forcés

| Pas | Niveau | Pourquoi |
|---|---|---|
| `K9` | conseillé | fait |
| `A2` | à la marge | sans phase |
"""


def tester_ordre():
    """ORD1 : `vlp.py ordre --json` sur deux projets bâtis à côté l'un de l'autre (le kit `.` et `autre`) et un
    absent : les pas lus en TODO ou pris de la source, les totaux du JSON ; un pas sans coût nulle part, une GARDE ;
    le dossier écrit, ignoré par Git dans le vrai kit."""
    with tempfile.TemporaryDirectory() as t:
        kit, autre = os.path.join(t, "kit"), os.path.join(t, "autre")
        for racine, todo in ((kit, "| 1 | `K1` — le premier | apporte | **V1 · score 15 (5 × 3)** · 2 à 3 fiches | — |"),
                             (autre, "| 7 | Le pont (`A1`) | apporte | **V2 · score 9 (3 × 3)** · 4 fiches | `K1` |")):
            ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(racine, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                                                           "|---|---|---|---|---|\n%s\n" % todo)
        source = os.path.join(kit, "ctx", "ordre.md")
        ecrire(source, ORDRE_SOURCE)
        code, s = appel(["ordre", "--json", "--source", source])
        donnees = json.load(open(os.path.join(kit, "ctx", "ordre", "donnees.json"), encoding="utf-8"))
        ecrire(source, ORDRE_SOURCE.replace("| 1 fiche |", "| |"))
        sans = appel(["ordre", "--json", "--source", source])
    verifier("ORD1 : ordre --json compte les pas, ceux lus en TODO, ceux pris de la source ; le projet absent dit",
             code == 0 and s.startswith("GARDE: projet x absent : absent n'est pas un dossier équipé")
             and "ORDRE 5 pas · 2 trouvés en TODO · 2 pris de la source\n" in s, s)
    a1 = [p for p in donnees["pas"] if p["code"] == "A1"]
    verifier("ORD1 : un pas lu en TODO garde son nom, sa phase, son score, ses fiches et sa dépendance brute",
             a1 == [{"projet": "a", "code": "A1", "numero": "7", "nom": "Le pont", "phase": "V2", "score": 9,
                     "bas": 4.0, "haut": 4.0, "fait": False, "note": "", "depend": "`K1`", "niveau": "obligatoire",
                     "vague": 1}], a1)
    verifier("ORD1 : les totaux du JSON — fiches bas et haut des pas chiffrés, faits, par projet",
             donnees["totaux"] == {"pas": 4, "bas": 7.0, "haut": 8.0, "faits": ["K9"], "non_chiffres": [],
                                   "par_projet": {"k": {"pas": 2, "bas": 2.0, "haut": 3.0},
                                                  "a": {"pas": 2, "bas": 5.0, "haut": 5.0}},
                                   "par_niveau": {"obligatoire": {"pas": 2, "bas": 6.0, "haut": 7.0},
                                                  "conseillé": {"pas": 1, "bas": 0, "haut": 0},
                                                  "à la marge": {"pas": 1, "bas": 1.0, "haut": 1.0}}}
             and donnees["cible"] == {"a": ["A1"]} and donnees["projets_absents"] == ["x"], donnees)
    verifier("ORD1 : un pas ni en TODO ni chiffré par la source, une GARDE qui le nomme, sort 1",
             sans[0] == 1 and "GARDE: pas A2 (a) : ni dans la TODO, ni un coût en fiches dans la source\n" in sans[1],
             sans)
    with tempfile.TemporaryDirectory() as t:     # un dépôt neuf, le .gitignore du kit : vrai aussi dans une copie
        shutil.copy(os.path.join(mod.etat.KIT, ".gitignore"), t)
        subprocess.run(["git", "init", "-q", t], capture_output=True)
        ignore = subprocess.run(["git", "check-ignore", "context AI/ordre/donnees.json"], cwd=t,
                                capture_output=True, text=True)
    verifier("ORD1 : ce que le script écrit est ignoré par le .gitignore du kit", ignore.returncode == 0, ignore)


groupe(tester_ordre)


CLASSE_SOURCE = """# L'ordre

## Les projets

| Clé | Dossier |
|---|---|
| p | `.` |

## La cible

| Projet | Codes |
|---|---|
| p | `P3` |

## Le chemin conseillé

| Pas | Projet | Nom | Coût |
|---|---|---|---|
| `P1` | p | | |
| `P2` | p | | |
| `P3` | p | | |
| `P4` | p | | |
| `P5` | p | | |
| `P6` | p | six | 1 fiche |

## Les dépendances ajoutées

| Pas | Dépend de | Pourquoi |
|---|---|---|
| `P2` | `P6` | le test |
"""


def tester_ordre_classement():
    """ORD2 : un graphe de 6 pas — une chaîne P3 → P2 (par son numéro de ligne) → P1, P2 → P6 ajoutée par la source,
    une branche conseillée P4, un `V2` — classé et mis en vagues ; puis un cycle, et une dépendance illisible."""
    def classer(dep1, dep5):
        with tempfile.TemporaryDirectory() as t:
            lignes = [(1, "V1", dep1), (2, "V1", "`P1`"), (3, "V1", "2"), (4, "V1", "`P1`"), (5, "V2", dep5)]
            ecrire(os.path.join(t, "p", "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(t, "p", "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                   "|---|---|---|---|---|\n" + "".join("| %d | `P%d` — pas | a | **%s · score 9 (3 × 3)** · 1 fiche | %s |\n"
                                                       % (n, n, phase, dep) for n, phase, dep in lignes))
            ecrire(os.path.join(t, "p", "ctx", "ordre.md"), CLASSE_SOURCE)
            code, s = appel(["ordre", "--json", "--source", os.path.join(t, "p", "ctx", "ordre.md")])
            chemin = os.path.join(t, "p", "ctx", "ordre", "donnees.json")
            return code, s, json.load(open(chemin, encoding="utf-8")) if os.path.isfile(chemin) else None
    code, s, donnees = classer("—", "—")
    niveaux = donnees and {p["code"]: p["niveau"] for p in donnees["pas"]}
    verifier("ORD2 : obligatoire de proche en proche depuis la cible, conseillé en V1, à la marge en V2",
             code == 0 and niveaux == {"P1": "obligatoire", "P2": "obligatoire", "P3": "obligatoire", "P4": "conseillé",
                                       "P5": "à la marge", "P6": "obligatoire"}, (s, niveaux))
    verifier("ORD2 : les vagues du tri, dans l'ordre du chemin, et le compte des dépendances",
             donnees is not None and donnees["vagues"] == [["P1", "P5", "P6"], ["P2", "P4"], ["P3"]]
             and "CLASSEMENT 4 obligatoires · 1 conseillés · 1 à la marge · 3 vagues · dépendances : 3 lues en TODO, "
                 "1 écrites par la source, 0 hors du chemin\n" in s, (s, donnees and donnees["vagues"]))
    cycle = classer("`P3`", "—")
    verifier("ORD2 : un cycle, une GARDE qui le nomme, rien d'écrit, sort 1",
             cycle[0] == 1 and cycle[1].startswith("GARDE: cycle de dépendances : ") and cycle[2] is None, cycle[:2])
    illisible = classer("—", "plus tard")
    verifier("ORD2 : une dépendance illisible, une GARDE qui nomme le pas, sort 1",
             illisible[0] == 1 and "GARDE: pas P5 : dépendance illisible « plus tard »\n" in illisible[1], illisible[:2])


groupe(tester_ordre_classement)


def donnees_de_page(html_):
    """Le bloc JSON d'une page d'ordre, relu ; `{}` sans bloc."""
    m = re.search(r'<script type="application/json" id="donnees">(.*?)</script>', html_, re.S)
    return json.loads(m.group(1)) if m else {}


def tester_ordre_page():
    """ORD3 : `vlp.py ordre` sans `--json` écrit la page d'un projet temporaire — le JSON embarqué égal au fichier de
    données, chaque pas et chaque total, aucune balise de gabarit restante, un `</script>` de TODO échappé, ses joints
    et la ligne `FILES` ; un gabarit à deux balises, une GARDE ; Chart.js à la même URL que `vlp.js`."""
    source_page = ORDRE_SOURCE.replace("| Clé | Dossier |\n|---|---|\n| k | `.` |\n| a | `autre` |",
                                       "| Clé | Dossier | Nom |\n|---|---|---|\n| k | `.` | Le kit |\n| a | `autre` | |") \
        + "\n## Le jugement\n\n- `A1` d'abord, puis\n  le reste.\n\n## Les décisions\n\n- **K1** avant tout.\n"
    with tempfile.TemporaryDirectory() as t:
        kit, autre = os.path.join(t, "kit"), os.path.join(t, "autre")
        for racine, todo in ((kit, "| 1 | `K1` — le premier </script> | apporte | **V1 · score 15 (5 × 3)** · 2 à 3 fiches | — |"),
                             (autre, "| 7 | Le pont (`A1`) | apporte | **V2 · score 9 (3 × 3)** · 4 fiches | `K1` |")):
            ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(racine, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                                                           "|---|---|---|---|---|\n%s\n" % todo)
        source = os.path.join(kit, "ctx", "ordre.md")
        ecrire(source, source_page)
        code, s = appel(["ordre", "--source", source])
        dossier = os.path.join(kit, "ctx", "ordre")
        donnees = json.load(open(os.path.join(dossier, "donnees.json"), encoding="utf-8"))
        page = lire(os.path.join(dossier, "ordre.html")) if os.path.isfile(os.path.join(dossier, "ordre.html")) else ""
        joints = sorted(n for n in os.listdir(dossier) if n.startswith("vlp."))
        double = os.path.join(t, "double.html")
        ecrire(double, "<données><données>")
        avant, mod.etat.GABARIT_ORDRE = mod.etat.GABARIT_ORDRE, double
        try:
            garde = appel(["ordre", "--source", source])
        finally:
            mod.etat.GABARIT_ORDRE = avant
    embarque = donnees_de_page(page)
    verifier("ORD3 : ordre sans --json écrit la page et ses joints, puis la ligne FILES",
             code == 0 and "\nPAGE " in s and "\nFILES {" in s and '"vlp.css"' in s and joints == ["vlp.css", "vlp.js"],
             (s, joints))
    verifier("ORD3 : la page porte les données entières — chaque pas, dans l'ordre, et chaque total",
             embarque == donnees and [p["code"] for p in embarque["pas"]] == ["K9", "K1", "A1", "A2"]
             and embarque["totaux"]["par_niveau"]["obligatoire"] == {"pas": 2, "bas": 6.0, "haut": 7.0}
             and [p["nom"] for p in embarque["projets"]] == ["Le kit", "a"], embarque)
    verifier("ORD3 : la prose de la source en texte, puce continuée comprise, et la piste du projet de la source",
             embarque and embarque["prose"]["Le jugement"] == ["`A1` d'abord, puis le reste."]
             and embarque["prose"]["Les décisions"] == ["**K1** avant tout."]
             and [x["code"] for x in embarque["piste"]] == ["K1"], embarque and embarque["prose"])
    restes = re.findall(r"<[^\x00-\x7f]|<…", page)
    verifier("ORD3 : aucune balise de gabarit restante, un </script> de TODO échappé, la page saine, la balise viewport",
             page and not restes and page.count("</script>") == lire(mod.etat.GABARIT_ORDRE).count("</script>")
             and mod.defauts_page(page) == [] and '<meta name="viewport"' in page, restes)
    verifier("ORD3 : un gabarit à deux balises, une GARDE qui le dit, sort 1",
             garde[0] == 1 and "la balise <données> y est 2 fois, attendu 1" in garde[1], garde)
    url = re.compile(r"https://cdn\.jsdelivr\.net/npm/chart\.js@[^\"']+")
    verifier("ORD3 : Chart.js chargé à la même URL que vlp.js",
             url.findall(lire(mod.etat.GABARIT_ORDRE)) == url.findall(lire(os.path.join(mod.etat.KIT, "templates", "vlp.js")))
             and len(url.findall(lire(mod.etat.GABARIT_ORDRE))) == 1, url.findall(lire(mod.etat.GABARIT_ORDRE)))


groupe(tester_ordre_page)


CLES_ORDRE_DB = ["source", "date", "projets", "cible", "projets_absents", "pas", "vagues", "dependances", "totaux",
                 "prose", "piste", "taux"]


def tester_ordre_db():
    """ORD4 : `vlp.py ordre --db` écrit le document de la base — un objet JSON compact, chaque clé que la page lit, sa
    taille dite face à la limite d'un document `db`, et pas de page ; passé un dixième, un AVERTISSEMENT ; passé la
    limite, une GARDE, rien d'écrit."""
    with tempfile.TemporaryDirectory() as t:
        ecrire(os.path.join(t, "p", "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
        ecrire(os.path.join(t, "p", "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `P1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
        source = os.path.join(t, "p", "ctx", "ordre.md")
        ecrire(source, "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| p | `.` |\n\n## La cible\n\n| Projet | Codes |\n"
               "|---|---|\n| p | `P1` |\n\n## Le chemin conseillé\n\n| Pas | Projet | Nom | Coût |\n|---|---|---|---|\n"
               "| `P1` | p | | |\n\n## Le jugement\n\n- `P1` d'abord.\n")
        code, s = appel(["ordre", "--db", "--source", source])
        chemin = os.path.join(t, "p", "ctx", "ordre", "donnees.json")
        brut = open(chemin, encoding="utf-8").read()
        page = os.path.isfile(os.path.join(t, "p", "ctx", "ordre", "ordre.html"))
        avant = mod.etat.LIMITE_DOC_DB
        try:
            mod.etat.LIMITE_DOC_DB = len(brut.encode("utf-8")) * 5
            dixieme = appel(["ordre", "--db", "--source", source])
            mod.etat.LIMITE_DOC_DB = 100
            os.remove(chemin)
            trop = appel(["ordre", "--db", "--source", source])
        finally:
            mod.etat.LIMITE_DOC_DB = avant
        reecrit = os.path.isfile(chemin)
    doc = json.loads(brut)
    taille = len(brut.rstrip("\n").encode("utf-8"))
    verifier("ORD4 : ordre --db écrit un objet JSON compact, chaque clé que la page lit, sans page",
             code == 0 and isinstance(doc, dict) and list(doc) == CLES_ORDRE_DB and "\n " not in brut and not page,
             (s, list(doc)))
    verifier("ORD4 : la ligne DB dit la taille en octets face à la limite d'un document db (256 KiB)",
             mod.etat.LIMITE_DOC_DB == 262144 and "DB ordre/donnees %d octets · limite 262144 · " % taille in s
             and "AVERTISSEMENT" not in s, s)
    verifier("ORD4 : passé un dixième de la limite, un AVERTISSEMENT ; passé la limite, une GARDE, rien d'écrit",
             dixieme[0] == 0 and "AVERTISSEMENT: ordre/donnees passe le dixième" in dixieme[1]
             and trop[0] == 1 and "au-delà de la limite d'un document db (100)" in trop[1] and not reecrit,
             (dixieme, trop))


groupe(tester_ordre_db)


def tester_ordre_clore():
    """ORD5 : `clore` d'un projet, quel qu'il soit, refait les données de la page d'enchaînement du kit et dit quoi
    envoyer où (ligne `ORDRE`) ; sans source, une GARDE, et la clôture finit."""
    gabarit = lambda nom: open(os.path.join(ICI, "..", "templates", nom), encoding="utf-8").read()
    sorties = []
    for avec_source in (True, False):
        with tempfile.TemporaryDirectory() as tk:
            kit, projet = os.path.join(tk, "kit"), os.path.join(tk, "p")
            ecrire(os.path.join(kit, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n"
                   "- **artefact enchaînement** : https://claude.ai/artifact/essai\n")
            ecrire(os.path.join(kit, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                   "|---|---|---|---|---|\n| 1 | `K1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
            source = os.path.join(kit, "ctx", "ordre.md")
            if avec_source:
                ecrire(source, "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| k | `.` |\n\n## La cible\n\n"
                       "| Projet | Codes |\n|---|---|\n| k | `K1` |\n\n## Le chemin conseillé\n\n| Pas | Projet | Nom | "
                       "Coût |\n|---|---|---|---|\n| `K1` | k | | |\n")
            ecrire(os.path.join(projet, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : A (test).\n")
            ecrire(os.path.join(projet, "ctx", "08-etat.md"), "# État\n")
            ecrire(os.path.join(projet, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(projet, "ctx", "artefacts", "50-u.html"), gabarit("artefact-chantier.html"))
            ecrire(os.path.join(projet, "ctx", "artefacts", "feuille-de-route.html"),
                   gabarit("artefact-feuille-de-route.html"))
            avant = mod.etat.SOURCE_ORDRE
            try:
                mod.etat.SOURCE_ORDRE = source
                code, s = appel(["clore", projet, "--livre", "fini", "--date", "2026-10-13"])
            finally:
                mod.etat.SOURCE_ORDRE = avant
            donnees = os.path.join(kit, "ctx", "ordre", "donnees.json")
            sorties.append((code, s, os.path.isfile(donnees) and json.load(open(donnees, encoding="utf-8")),
                            os.path.realpath(donnees), os.path.realpath(source)))
    (code, s, doc, donnees, _), (code_sans, s_sans, doc_sans, _, source_sans) = sorties
    verifier("ORD5 : clore d'un autre projet refait les données du kit et dit quoi envoyer où",
             code == 0 and "CLOS U " in s and "ORDRE envoyer %s → https://claude.ai/artifact/essai\n" % donnees in s
             and isinstance(doc, dict) and [p["code"] for p in doc["pas"]] == ["K1"], (code, s))
    verifier("ORD5 : sans source, une GARDE qui le dit, pas de ligne ORDRE, et la clôture finit",
             code_sans == 0 and "CLOS U " in s_sans and "ORDRE envoyer" not in s_sans and doc_sans is False
             and "GARDE: ordre : source introuvable (%s)" % source_sans in s_sans, (code_sans, s_sans))


groupe(tester_ordre_clore)


def tester_clore_pages_aucun():
    """ISO : un projet dont `CHANTIER.md` dit ses trois pages « aucun » se clôt sans ligne `ORDRE` vers la page
    d'enchaînement du kit, ni `GARDE:` de page absente ; une ligne `SANS PAGE` le dit."""
    with tempfile.TemporaryDirectory() as tk:
        kit, projet = os.path.join(tk, "kit"), os.path.join(tk, "p")
        ecrire(os.path.join(kit, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n"
               "- **artefact enchaînement** : https://claude.ai/artifact/essai\n")
        ecrire(os.path.join(kit, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
               "|---|---|---|---|---|\n| 1 | `K1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |\n")
        source = os.path.join(kit, "ctx", "ordre.md")
        ecrire(source, "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| k | `.` |\n\n## La cible\n\n"
               "| Projet | Codes |\n|---|---|\n| k | `K1` |\n\n## Le chemin conseillé\n\n| Pas | Projet | Nom | "
               "Coût |\n|---|---|---|---|\n| `K1` | k | | |\n")
        ecrire(os.path.join(projet, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n- **artefact feuille de route** : aucun\n"
               "- **artefact du chantier** : aucun\n- **artefact enchaînement** : aucun\n\n"
               "Lettres de fiche déjà prises : A (test).\n")
        ecrire(os.path.join(projet, "ctx", "08-etat.md"), "# État\n")
        ecrire(os.path.join(projet, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
        avant = mod.etat.SOURCE_ORDRE
        try:
            mod.etat.SOURCE_ORDRE = source
            code, s = appel(["clore", projet, "--livre", "fini", "--date", "2026-10-17"])
        finally:
            mod.etat.SOURCE_ORDRE = avant
        donnees = os.path.join(kit, "ctx", "ordre", "donnees.json")
        verifier("ISO : clore d'un projet aux pages « aucun » — ni ORDRE vers le kit, ni GARDE de page absente, "
                 "une ligne SANS PAGE — clore : enchaînement « aucun » ignoré",
                 code == 0 and "CLOS U " in s and "ORDRE envoyer" not in s and not os.path.exists(donnees)
                 and "page du chantier introuvable" not in s and "feuille de route introuvable" not in s
                 and "SANS PAGE la page du chantier, la feuille de route — CHANTIER.md dit « aucun »\n" in s, (code, s))


groupe(tester_clore_pages_aucun)


def lien_dossier(cible, lien):
    """Un lien vers le dossier `cible` : une jonction sous Windows (`mklink /J`, sans droit d'administrateur), comme
    `~/.claude/skills/vlp` ; un lien symbolique ailleurs."""
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", lien, cible], capture_output=True, check=True)
    else:
        os.symlink(cible, lien)


def tester_ordre_jonction():
    """Dette ORD : lancé par le plugin, le kit est vu par une jonction ; `ordre` cherche les projets voisins à côté du
    vrai kit, pas à côté du lien."""
    with tempfile.TemporaryDirectory() as tj:
        kit, autre, lien = os.path.join(tj, "vrai", "kit"), os.path.join(tj, "vrai", "autre"), os.path.join(tj, "lien")
        for racine, todo in ((kit, "| 1 | `K1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |"),
                             (autre, "| 2 | `A1` — pas | a | **V1 · score 9 (3 × 3)** · 1 fiche | — |")):
            ecrire(os.path.join(racine, "CHANTIER.md"), "# Chantier\n\n- **chantiers possibles** : `ctx/etat.md`\n")
            ecrire(os.path.join(racine, "ctx", "etat.md"), "## TODO\n\n| # | Chantier | Apporte | Coût | Dépend de |\n"
                   "|---|---|---|---|---|\n%s\n" % todo)
        ecrire(os.path.join(kit, "ctx", "ordre.md"), "## Les projets\n\n| Clé | Dossier |\n|---|---|\n| k | `.` |\n"
               "| a | `autre` |\n\n## La cible\n\n| Projet | Codes |\n|---|---|\n| a | `A1` |\n\n## Le chemin conseillé\n\n"
               "| Pas | Projet | Nom | Coût |\n|---|---|---|---|\n| `K1` | k | | |\n| `A1` | a | | |\n")
        lien_dossier(kit, lien)
        code, s = appel(["ordre", "--json", "--source", os.path.join(lien, "ctx", "ordre.md")])
        os.rmdir(lien) if os.name == "nt" else os.remove(lien)   # la jonction seule, jamais ce qu'elle vise
    verifier("Dette ORD : la source lue par une jonction trouve le projet voisin du vrai kit",
             code == 0 and "GARDE" not in s and "ORDRE 2 pas · 2 trouvés en TODO" in s, (code, s))


groupe(tester_ordre_jonction)


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


# --- VOI3 : `lettres_prises` tolère une lettre entre backticks (MapDecorator) -


# --- ABR1 : le .md d'une page, amorcé depuis la page sans la toucher ----------


# --- ABR2 : `page` écrit d'abord dans le .md, puis le recopie en entier -------


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


# --- PLI3 : une page à <style> inline est migrée vers <link href="vlp.css"> ---


# --- PLI5 : chaque fiche repliée, ouverte si en cours ; l'ancienne forme se lit encore ---


# --- Gabarit en colonnes (2026-09-27) : dépendances à gauche, coût ou « visuel » à droite ---


# --- PLI6 : le journal replié au-delà de 3 entrées ; le bilan sous l'en-tête à la clôture ---


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


def hook_isole(t):
    """Rendre un dépôt neuf sous `t`, le hook du kit branché et `scripts/` copié hors suivi (le hook y lance
    `vlp.py claude`, VIT19), le PATH sans pyright, uv ni claude, et `git(chemins, *args, **env)` : claude caché,
    APPDATA et LOCALAPPDATA vides sauf `env`."""
    depot = os.path.join(t, "depot")
    for nom in (".githooks", "scripts"):
        shutil.copytree(os.path.join(RACINE, nom), os.path.join(depot, nom))
    sans = [d for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and not any(shutil.which(n, path=d) for n in ("pyright", "uv", "claude"))]
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
    # TYP1, REF3 : le hook lance `uv run --frozen pyright` quand un .py est indexé. claude, uv et pyright cachés
    # (`hook_isole`) ; un faux uv en tête du PATH — un script sh, que le hook lance, quand uv ne saurait pas lancer
    # un faux pyright sous Windows — rend le verdict de pyright.
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le bloc pyright du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        depot, sans, git = hook_isole(t)
        def faux_uv(nom, code):
            d = os.path.join(t, nom)
            ecrire(os.path.join(d, "uv"), '#!/bin/sh\necho "faux uv $* : sortie %d"\nexit %d\n' % (code, code))
            os.chmod(os.path.join(d, "uv"), 0o755)
            return d
        rouge, vert = faux_uv("rouge", 1), faux_uv("vert", 0)
        ecrire(os.path.join(depot, "a.md"), "a\n")
        git(sans, "add", "a.md")
        code, s = git([rouge] + sans, "commit", "-q", "-m", "md")
        verifier("hook pyright : un .md seul passe", code == 0 and "pyright" not in s, s)
        ecrire(os.path.join(depot, "a.py"), "x = 1\n")
        git(sans, "add", "a.py")
        code, s = git([rouge] + sans, "commit", "-q", "-m", "py")
        verifier("hook pyright : un .py en erreur est refusé", code == 1 and "faux uv run --frozen pyright : sortie 1" in s
                 and "pre-commit : pyright en erreur ou absent de l'atelier (uv sync), commit refusé." in s, s)
        code, s = git(sans, "commit", "-q", "-m", "py")
        verifier("hook pyright : sans uv, le .py est refusé en le disant (E27)", code == 1
                 and "pre-commit : uv introuvable, pyright non lancé, commit refusé" in s, s)
        code, s = git([vert] + sans, "commit", "-q", "-m", "py")
        verifier("hook pyright : pyright vert sous uv, le .py passe", code == 0
                 and "faux uv run --frozen pyright : sortie 0" not in s, s)


groupe(tester_hook_pyright)


def tester_hook_chemin():
    # CHM : le hook refuse une ligne ajoutée qui porte un chemin de machine, sous ses trois formes ; `~` passe, et une
    # ligne ancienne, gardée telle quelle, ne bloque rien. Les chemins se bâtissent par morceaux : écrits d'un bloc
    # dans ce fichier, ils feraient refuser son propre commit.
    if not shutil.which("git"):
        print("SAUTÉ: git absent — le bloc des chemins du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as t:
        depot, sans, git = hook_isole(t)
        ecrire(os.path.join(depot, "a.md"), "le kit : ~/.claude/skills/vlp\n")
        git(sans, "add", "a.md")
        code, s = git(sans, "commit", "-q", "-m", "tilde")
        verifier("CHM : hook, un chemin en ~ passe", code == 0 and "chemin de machine" not in s, s)
        refus = []
        for forme in ("C:" + "/Users/bob/x", "C:" + "\\Users\\bob\\x", "/mnt/c/" + "Users/bob/x", "C-" + "-Users-bob-Documents"):
            ecrire(os.path.join(depot, "b.md"), "voir `%s`\n" % forme)
            git(sans, "add", "b.md")
            code, s = git(sans, "commit", "-q", "-m", "chemin")
            refus.append(code == 1 and "pre-commit : chemin de machine dans une ligne ajoutée" in s)
        verifier("CHM : hook, les trois formes de chemin de machine refusées (4 cas)", refus == [True] * 4, refus)


groupe(tester_hook_chemin)


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


# --- FEU7 : l'eyebrow de la page du chantier finit par un lien vers la feuille de route ---


# --- FEU8 : le décompte au-dessus de la TODO détaille tailles, bloqués, total estimé ---


# --- PIP1 : une ligne de TODO mal découpée rend une GARDE, plus un décompte faux ---


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


def contrastes_couts(barre, texte):
    """CTR1 : les variables de la ligne `:root` de vlp.css, et les rapports WCAG (luminance
    relative) de `barre` puis `texte`, chacune sur `--surface` puis `--ground`."""
    racine_css = next(l for l in lire(GABARIT_VLPCSS).splitlines() if l.startswith(":root"))
    css = dict(re.findall(r"(--[\w-]+):(#[0-9a-f]{6})", racine_css))

    def luminance(c):
        v = [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        v = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v]
        return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]

    def contraste(a, b):
        la, lb = sorted((luminance(a), luminance(b)), reverse=True)
        return (la + .05) / (lb + .05)
    return css, [contraste(c, css.get(f, "#000000")) for c in (barre, texte) for f in ("--surface", "--ground")]


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
        verifier("REF29 : feuille dit LIRE avec couts.svg joint — mutant : ligne LIRE retirée",
                 "\nLIRE vlp.css vlp.js couts.svg\n" in s, s)
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
        # CTR1 : l'image recopie `--cours` et `--doux` de vlp.css, lisibles à 4,5:1 sur les deux fonds.
        css, rapports = contrastes_couts(mod.COUTS_BARRE, mod.COUTS_TEXTE)
        verifier("Graphique : couleurs de couts.svg = --cours et --doux de vlp.css, contraste ≥ 4,5"
                 " sur --surface et --ground — mutant : ancienne couleur des barres",
                 mod.COUTS_BARRE == css.get("--cours") and mod.COUTS_TEXTE == css.get("--doux")
                 and min(rapports) >= 4.5, "rapports %s · css %s" % (
                     " ".join("%.2f" % r for r in rapports), css))
        print("  CTR1 contrastes (barre/surface, barre/ground, texte/surface, texte/ground) : %s"
              % " ".join("%.2f" % r for r in rapports))
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
        verifier("REF29 : feuille sans couts.svg dit LIRE sans lui", "\nLIRE vlp.css vlp.js\n" in s, s)

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
        ancien_tampon = mod.etat.TAMPON_HOOKS
        mod.etat.TAMPON_HOOKS = tempfile.mkdtemp()
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
            shutil.rmtree(mod.etat.TAMPON_HOOKS, ignore_errors=True)
            mod.etat.TAMPON_HOOKS = ancien_tampon

    zero, tache = mod.remise_a_zero(soir)
    verifier("attente : remise à zéro 02:00 et tâche 02:10 pour 2026-09-28 20:00 UTC+2",
             (zero.strftime("%Y-%m-%d %H:%M"), tache.strftime("%H:%M")) == ("2026-09-29 02:00", "02:10"), str(zero))


groupe(tester_attente)


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
        milieu = mutant("x = 4", "--attendu", "utr")
        verifier("REF31 : --attendu au milieu d'un écart (cas d'ENA) → VIVANT, puis la ligne ATTENDU AU MILIEU qui "
                 "donne le début du libellé à recopier — mutant : la ligne retirée",
                 milieu[0] == 1 and milieu[1].startswith(
                     "ÉCART: autre\nMUTANT VIVANT pour utr\n"
                     "ATTENDU AU MILIEU · « utr » est dans « autre » : --attendu \"autr\"\n") and milieu[3],
                 milieu)
        plante = mutant("x = 3", "--attendu", "attendu")
        plante_tous = mutant("x = 3")
        verifier("VIT2 : la suite arrêtée en erreur après un autre écart → MUTANT PLANTÉ, sort 1, avec --attendu comme "
                 "sans — mutant : ATTRAPÉ dès qu'un écart est vu",
                 all(p[0] == 1 and "MUTANT PLANTÉ · tests sortis 1 sans finir, après 1 écart(s)" in p[1]
                     and "ATTRAPÉ" not in p[1] and p[3] for p in (plante, plante_tous)), (plante, plante_tous))


groupe(tester_mutant_attendu)

# Un juge hors kit, comme le `verif.py` du projet jetable d'ISO7 : `OK`/`KO` en tête de ligne, ni `ÉCART:` ni `FIN:`.
JUGE_HORS_KIT = """import sys
t = open(sys.argv[1], encoding="utf-8").read()
if "x = 9" in t:
    raise ValueError("juge cassé")
print("OK X -- lu" if "x = 1" in t else "KO X -- lu")
sys.exit(0 if "x = 1" in t else 1)
"""


def tester_mutant_juge():
    """ISO : un juge hors kit (`--test`) qui n'imprime ni `ÉCART:` ni `FIN:` est jugé à son code de sortie —
    ATTRAPÉ s'il sort 1 et dit `--attendu`, VIVANT s'il sort 0 ou ne le dit pas, PLANTÉ sur une erreur Python."""
    with tempfile.TemporaryDirectory() as tm:
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
        verifier("ISO : mutant d'un juge hors kit — sorti 1 en disant --attendu → ATTRAPÉ ; sorti 0, ou sans le "
                 "dire → VIVANT ; erreur Python → PLANTÉ — mutant : juge hors kit dit PLANTÉ",
                 vus["attrapé"][0] == 0 and "MUTANT ATTRAPÉ · juge hors kit sorti 1 — « KO X -- lu »" in vus["attrapé"][1]
                 and vus["nu"][0] == 0 and "MUTANT ATTRAPÉ · juge hors kit sorti 1" in vus["nu"][1]
                 and vus["vivant"][0] == 1 and "MUTANT VIVANT pour KO X · juge hors kit sorti 0" in vus["vivant"][1]
                 and vus["muet"][0] == 1 and "MUTANT VIVANT pour jamais · juge hors kit sorti 1 sans le dire"
                 in vus["muet"][1]
                 and vus["planté"][0] == 1 and "MUTANT PLANTÉ · juge hors kit sorti 1" in vus["planté"][1]
                 and "ValueError" in vus["planté"][1], vus)


groupe(tester_mutant_juge)

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
            garde, mod.etat.KIT = mod.etat.KIT, kit
            try:
                code = mod.main(["mutant", f, avant, apres, "--attendu", attendu, *options], o)
            finally:
                mod.etat.KIT = garde
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
        garde, mod.etat.KIT = mod.etat.KIT, principal
        try:
            code = mod.main(["mutant", f, "a = 1", "a = 9", "--attendu", "porte a"], o)
        finally:
            mod.etat.KIT = garde
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


# --- NUI16 : `matin` fusionne par clé les fichiers que les deux canaux réécrivent ---------------


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


def tester_postit():
    """ISO8 : `postit` pose le post-it d'un worktree pour son sous-agent isolé — `carte` y lit alors le chantier."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — postit n'est pas testé")
        return
    signe = ("-c", "user.name=t", "-c", "user.email=t@t")
    with tempfile.TemporaryDirectory() as tr:
        d, wt, hors = os.path.join(tr, "cd"), os.path.join(tr, "wt"), os.path.join(tr, "hors")
        ecrire(os.path.join(d, "CHANTIER.md"), "- **alias** : cd\n- **contexte** : ctx/\n")
        ecrire(os.path.join(d, "ctx", "a.md"), "# Chantier A — x\n\n%s\n\n## A1 [ ] — f\n" % (OUVERT % "2026-10-17"))
        ecrire(os.path.join(d, "ctx", "c.md"), "# Chantier C — x\n\n%s\n\n%s\n\n## C1 [x] — f\n"
               % (OUVERT % "2026-10-01", mod.CLOS_LIGNE % "2026-10-02"))
        ecrire(os.path.join(hors, "CHANTIER.md"), "- **contexte** : ctx/\n")
        git_matin(d, "init", "-q", "-b", "main")
        git_matin(d, "add", "-A")
        git_matin(d, *signe, "commit", "-q", "-m", "base")
        git_matin(d, "worktree", "add", "-q", "-b", "wt", wt)
        p = mod.postit(wt)
        clos = appel(["postit", wt, "ctx/c.md"])
        clos_rien = not os.path.exists(p)
        sans_git = appel(["postit", hors, "ctx/a.md"])
        avant = next(l for l in appel(["carte", wt])[1].split("\n") if l.startswith("COURANT="))
        pose = appel(["postit", wt, "ctx\\a.md"])
        apres = next(l for l in appel(["carte", wt])[1].split("\n") if l.startswith("COURANT="))
        lu = mod.lire(p) if os.path.exists(p) else None
        git_matin(d, "worktree", "remove", "--force", wt)
    chef = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    trois = chef[chef.find("## 3. Jouer chaque fiche"):chef.find("## 3 bis.")]
    verifier("ISO8 : postit écrit le post-it du worktree, carte y lit COURANT=ctx/a.md — mutant : postit qui n'écrit rien",
             avant == "COURANT=aucun" and pose == (0, "POSTIT ctx/a.md — %s\n" % wt) and lu == "ctx/a.md\n"
             and apres == "COURANT=ctx/a.md", repr((avant, pose, lu, apres)))
    verifier("ISO8 : postit refuse un fichier non ouvert et un dossier hors Git — GARDE:, sort 1, rien d'écrit",
             clos[0] == 1 and clos[1].startswith("GARDE: ctx/c.md n'est pas un chantier ouvert") and clos_rien
             and sans_git[0] == 1 and sans_git[1].startswith("GARDE: %s hors Git" % hors), repr((clos, clos_rien, sans_git)))
    verifier("ISO8 : le prompt du sous-agent ne lui fait plus écrire le post-it — l'étape 3 sans (Write), avec postit",
             "(Write)" not in trois and "scripts/vlp.py\" postit " in trois, trois[:200])


groupe(tester_postit)


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


def noms_worktrees(d):
    """Les noms de dossier des worktrees du dépôt de `d`, le principal en tête (ISO4)."""
    return [os.path.basename(l[len("worktree "):].rstrip("/")) for l in git_matin(d, "worktree", "list", "--porcelain")
            .splitlines() if l.startswith("worktree ")]


def tester_iso4_fusionner_fiche():
    """ISO4 : `fusionner <fichier> <fiche> --worktree <dossier>` sur un dépôt et deux worktrees — sans conflit,
    `FUSIONNÉ`, le fichier dans main, plus de worktree ni de branche ; même ligne changée des deux côtés, `CONFLIT`,
    sort 1, `git status` propre ; un dossier hors des worktrees, ou sans commit de la fiche : `GARDE:`, rien touché."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — fusionner --worktree n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        d, wa, wc = (os.path.join(tr, n) for n in ("d", "wt-a", "wt-c"))
        os.makedirs(d)
        git_matin(d, "init", "-q", "-b", "main")
        fiches = os.path.join(d, "ctx", "f.md")
        ecrire(fiches, "# F\n\n## W1 [ ] — a\n\n## W2 [ ] — c\n")
        ecrire(os.path.join(d, "a.txt"), "1\n2\n3\n")
        commit_matin(d, "départ", 1)
        for nom, w in (("a", wa), ("c", wc)):
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
        gardes = [appel(["fusionner", fiches, "W1", "--worktree", w]) for w in (wa, tr)]   # W1 pas encore commitée
        intact = noms_worktrees(d) == ["d", "wt-a", "wt-c"] and git_matin(d, "status", "--porcelain") == ""
        ecrire(os.path.join(wa, "b.txt"), "b\n")
        commit_matin(wa, "W1 : a", 2)
        ecrire(os.path.join(wc, "a.txt"), "1\nc\n3\n")
        commit_matin(wc, "W2 : c", 3)
        ecrire(os.path.join(d, "a.txt"), "1\nm\n3\n")
        commit_matin(d, "main change la ligne 2", 4)
        fus = appel(["fusionner", fiches, "W1", "--worktree", wa])
        apres_fus = (os.path.isfile(os.path.join(d, "b.txt")), noms_worktrees(d))
        conf = appel(["fusionner", fiches, "W2", "--worktree", wc])
        apres_conf = (git_matin(d, "status", "--porcelain"), code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD"),
                      lire(os.path.join(d, "a.txt")).replace("\r\n", "\n"), noms_worktrees(d),
                      git_matin(d, "branch", "--format=%(refname:short)").split())
    verifier("ISO4 : sans conflit → FUSIONNÉ W1 <sha>, sort 0, b.txt dans main, le worktree wt-a retiré",
             fus[0] == 0 and re.fullmatch(r"FUSIONNÉ W1 [0-9a-f]{7,}\n", fus[1]) is not None
             and apres_fus == (True, ["d", "wt-c"]), (fus, apres_fus))
    verifier("ISO4 : même ligne changée des deux côtés → CONFLIT W2 a.txt, sort 1, git status propre, pas de "
             "MERGE_HEAD, la ligne de main gardée, plus de worktree ni de branche a ou c — mutant : pas d'abort",
             conf == (1, "CONFLIT W2 a.txt\n") and apres_conf == ("", 1, "1\nm\n3\n", ["d"], ["main"]),
             (conf, apres_conf))
    verifier("ISO4 : sans commit « W1 : » dans le worktree, ou un dossier hors des worktrees → GARDE:, sort 1, rien "
             "touché",
             [c for c, _ in gardes] == [1, 1] and gardes[0][1].startswith("GARDE: aucun commit « W1 : »")
             and "n'est pas un autre worktree" in gardes[1][1] and intact, (gardes, intact))


groupe(tester_iso4_fusionner_fiche)


def tester_ref40_base_refaite():
    """REF40 : un `CONFLIT` sur `scripts/sante-base.json` seul — deux fiches ont réécrit le relevé du cliquet — se
    règle par le relevé refait sur le code fusionné : `FUSIONNÉ` et `BASE REFAITE`, la base égale à celle d'un
    `sante --base` neuf ; une fonction qui empire (base relâchée par `--forcer` dans la fiche) : `CONFLIT` comme avant."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — la base refaite à la fusion n'est pas testée")
        return
    def fonction(nom, params=""):
        return "def %s(%s):\n    \"\"\"%s.\"\"\"\n    return 1\n\n\n" % (nom, params, nom)

    def base(d):
        return lire(os.path.join(d, "scripts", "sante-base.json")).replace("\r\n", "\n")

    with tempfile.TemporaryDirectory() as tr:
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
    verifier("REF40 : conflit sur sante-base.json seul → FUSIONNÉ W1 et BASE REFAITE, sort 0, arbre propre, "
             "worktree retiré, commit « Fusion : W1 »",
             fus[0] == 0 and fus[1].startswith("FUSIONNÉ W1 ") and "\nBASE REFAITE scripts/sante-base.json" in fus[1]
             and fusionnee[1:] == ("", ["d", "wt-b"], "Fusion : W1"), (fus, fusionnee[1:]))
    verifier("REF40 : la base fusionnée égale celle d'un sante --base neuf, f2 et g2 comprises",
             fusionnee[0] == neuve and '"f2"' in neuve and '"g2"' in neuve, (fusionnee[0], neuve))
    verifier("REF40 : une fonction qui empire sur le code fusionné → CONFLIT W2 scripts/sante-base.json, sort 1, "
             "arbre propre, pas de MERGE_HEAD, base de main intacte",
             conf[0] == 1 and conf[1].endswith("CONFLIT W2 scripts/sante-base.json\n") and apres_conf == ("", 1, True),
             (conf, apres_conf))


groupe(tester_ref40_base_refaite)


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


def tester_ref9_tailles():
    """REF9 : le cliquet garde la taille des fichiers `.py` de `scripts/` et de `tests/` — au-dessus de
    `SEUIL_LIGNES`, la taille de base est le plafond, qui descend quand le fichier maigrit ; un fichier neuf, ou de
    1 000 lignes ou moins, ne passe pas le seuil."""
    seuil = mod_sante().SEUIL_LIGNES
    lignes = lambda n: "".join("x%d = %d\n" % (i, i) for i in range(n))
    with tempfile.TemporaryDirectory() as tc:
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
    verifier("REF9 : la base pose les tailles ; le même code → TENU, et la ligne des gros fichiers, taille/plafond",
             pose[0] == 0 and tenu[0] == 0 and "TAILLES au-dessus de %d lignes, taille/plafond : scripts/gros.py "
             "1200/1200\n" % seuil in tenu[1] and tenu[1].endswith("CLIQUET TENU\n"), (pose, tenu))
    verifier("REF9 : une ligne ajoutée à un gros fichier → TAILLE …, plafond 1200 (base), ROMPU",
             grossi[0] == 1 and "TAILLE scripts/gros.py · 1201 lignes, plafond 1200 (base)\n" in grossi[1], grossi)
    verifier("REF9 : un fichier neuf de 1 001 lignes, dans scripts/ ou tests/ → TAILLE …, plafond 1000 (seuil), ROMPU",
             neuf[0] == 1 and "TAILLE scripts/neuf.py · %d lignes, plafond %d (seuil)\n" % (seuil + 1, seuil) in neuf[1]
             and test_neuf[0] == 1 and "TAILLE tests/test_gros.py · %d lignes" % (seuil + 1) in test_neuf[1],
             (neuf, test_neuf))
    verifier("REF9 : un gros fichier qui maigrit (1100) fait baisser sa base : 1150 → ROMPU, plafond 1100, et --base "
             "refuse de relâcher",
             maigri[0] == 0 and regrossi[0] == 1 and "TAILLE scripts/gros.py · 1150 lignes, plafond 1100 (base)\n"
             in regrossi[1] and refuse[0] == 1 and "GARDE: la base ne se relâche pas" in refuse[1],
             (maigri, regrossi, refuse))


def mod_sante():
    """Le module `sante`, chargé comme `cmd_sante` le charge (REF9)."""
    import sante
    return sante


groupe(tester_ref9_tailles)


def tester_iso6_parallele():
    """ISO6 : `/vlp:enchainer agents` lance en parallèle d'office — chaque fiche en worktree au rythme de `lancables`,
    puis `commiter` là-bas, `fusionner` ici, `etat` du bloc `ÉTAT:`, `CONFLIT` rejoué en fin ; `file`, le mode sans
    argument et `clear` restent ; le contrat dit `DOSSIER:` et `ÉTAT:`."""
    chef = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    contrat = io.open(os.path.join(RACINE, "enchainement.md"), encoding="utf-8").read()
    indice = next((l for l in chef.splitlines() if l.startswith("argument-hint:")), "")
    debut, fin = chef.find("## 3. Jouer chaque fiche"), chef.find("## 3 bis.")
    trois = " ".join(chef[debut:fin].split()) if 0 <= debut < fin else ""
    attendus = ['isolation: "worktree"', 'lancables "<fichier de fiches courant>" --max <largeur> --tourne', "INDICE:",
                "DOSSIER:", 'fusionner "<fichier de fiches courant>" <fiche> --worktree "<dossier>"',
                'etat "<fichier d\'état>" --texte', "CONFLIT", 'postit "<dossier>" "<fichier de fiches courant>"']
    plat = " ".join(chef.split())
    verifier("ISO6 : l'étape 3 lance en worktree par lancables, fusionne, écrit l'état et rejoue un CONFLIT",
             [a for a in attendus if a not in trois] == [], [a for a in attendus if a not in trois])
    verifier("ISO6 : argument-hint dit la largeur et file ; main, clear et le plafond de 5 restent",
             "agents [<largeur>]" in indice and "agents file" in indice and "`agents file`" in plat
             and "**Sans argument (ou `main`) : aucun sous-agent.**" in plat and 'boucle.py" . --plafond' in plat
             and "Plafond : **5 fiches**" in plat, indice)
    verifier("ISO6 : le contrat porte DOSSIER:, ÉTAT: et /ÉTAT",
             all(m in contrat for m in ("DOSSIER: <chemin", "\nÉTAT:\n", "\n/ÉTAT\n")), "enchainement.md")


groupe(tester_iso6_parallele)


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


def noms_ailleurs(dossier):
    """Les `(code, nom du dossier)`, triés, des lignes `AILLEURS=` de la carte de `dossier` (NUI28)."""
    s = appel(["carte", dossier])[1]
    return sorted((l.split()[0][len("AILLEURS="):], os.path.basename(l.split(None, 1)[1].rstrip("/")))
                  for l in s.splitlines() if l.startswith("AILLEURS="))


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
        vus = {nom: noms_ailleurs(w) for nom, w in dossiers.items()}
    attendu ={"m": [("WZA", "wt-a"), ("WZB", "wt-b")], "a": [("MAA", "m"), ("WZB", "wt-b")],
               "b": [("MAA", "m"), ("WZA", "wt-a")], "c": [("MAA", "m"), ("WZA", "wt-a"), ("WZB", "wt-b")]}
    verifier("NUI28 (a) main + deux worktrees à chantier + un sans : la carte de chacun nomme les autres chantiers, "
             "jamais le sien ; le worktree sans chantier n'est nommé par personne — mutant : le sien non filtré",
             vus == attendu, vus)

    with tempfile.TemporaryDirectory() as tr:
        d, wl = os.path.join(tr, "n"), os.path.join(tr, "wt-l")
        depot_matin(d)
        git_matin(d, "worktree", "add", "-q", "-b", "l", wl, "main")
        ecrire(os.path.join(wl, "b.txt"), "b\n")
        commit_matin(wl, "LOC1 : a", 2)          # ni post-it ni marque à lui : ses commits disent ce qu'il joue
        ecrire(os.path.join(wl, "c.txt"), "c\n")
        commit_matin(wl, "ZZZ1 : vieux", 3)      # un vieux commit jamais fusionné, d'un chantier ouvert nulle part
        _, joue = appel(["niveau", d])
        carte = [l for l in appel(["carte", d])[1].splitlines() if l.startswith("AILLEURS=")]
    verifier("NWT (a) un worktree sans marque ni post-it : ses commits « LOC1 : » disent qu'il joue LOC, ouvert dans le "
             "principal → AILLEURS ; « ZZZ1 : », ouvert nulle part, ne compte pas",
             "AILLEURS: page: LOC joue dans " in joue and "ÉCART: page:" not in joue and len(carte) == 1
             and carte[0].startswith("AILLEURS=LOC ") and carte[0].rstrip("/").endswith("wt-l"), (joue, carte))

    with tempfile.TemporaryDirectory() as tr:
        d, wv = os.path.join(tr, "v"), os.path.join(tr, "wt-v")
        os.makedirs(d)
        git_matin(d, "init", "-q", "-b", "main")
        ecrire(os.path.join(d, "a.txt"), "a\n")
        commit_matin(d, "avant le suivi", 1)
        git_matin(d, "worktree", "add", "-q", "-b", "v", wv, "main")
        ecrire(os.path.join(wv, "CHANTIER.md"), CARTE_MATIN)      # sa vieille copie locale, jamais suivie
        ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
        ecrire(os.path.join(d, "CLAUDE.md"), "# v\n")
        commit_matin(d, "contexte suivi", 2)
        retard, principal_ = mod.ligne_git(wv), mod.ligne_git(d)
    verifier("NWT (b) un worktree né avant que main suive CHANTIER.md et CLAUDE.md : la carte le dit et propose de "
             "fusionner main ; main lui-même, non",
             "GIT=en retard sur main : CHANTIER.md, CLAUDE.md suivi(s) là-bas, pas ici — worktree né avant ; y fusionner "
             "main" in retard and not any("retard" in l for l in principal_), (retard, principal_))


groupe(tester_ailleurs)


def tester_ailleurs_meme_chantier():
    """NUI28 (b) à (d) : au même chantier qu'ici, un autre worktree n'est nommé (`AILLEURS=`, `niveau`) que s'il a
    joué une fiche de ce code qu'ici n'a pas — un hérité se tait des deux côtés (ISO2, TODO 140)."""
    if not shutil.which("git"):
        print("SAUTÉ: git absent — AILLEURS= au même chantier n'est pas testé")
        return
    with tempfile.TemporaryDirectory() as tr:
        d, wl = os.path.join(tr, "n"), os.path.join(tr, "wt-l")
        depot_matin(d)
        _, seul = appel(["niveau", d])
        git_matin(d, "worktree", "add", "-q", "-b", "l", wl, "main")
        ecrire(mod.postit(wl), "ctx/40-loc.md\n")      # le worktree joue LOC : son post-it le nomme (NUI31)
        ecrire(os.path.join(wl, "b.txt"), "b\n")
        commit_matin(wl, "LOC1 : a", 2)                 # et une fiche de LOC que main n'a pas (ISO2)
        _, avec = appel(["niveau", d])
        _, dans = appel(["niveau", wl])
    verifier("NUI28 (b) niveau : LOC joué dans un worktree → « AILLEURS: page: LOC joue dans … », aucun ÉCART: page "
             "dans le principal ; sans worktree, ou lancé dans le worktree, la page se compte",
             "ÉCART: page:" in seul and "AILLEURS:" not in seul
             and "AILLEURS: page: LOC joue dans " in avec and "wt-l" in avec and "ÉCART: page:" not in avec
             and "AILLEURS:" not in dans,
             (seul, avec, dans))

    with tempfile.TemporaryDirectory() as tr:
        d, wh = os.path.join(tr, "h"), os.path.join(tr, "wt-h")
        depot_matin(d)
        git_matin(d, "worktree", "add", "-q", "-b", "h", wh, "main")
        ecrire(mod.postit(wh), "ctx/40-loc.md\n")      # LOC hérité de main, nommé par le post-it : le même des deux côtés
        herite = [noms_ailleurs(w) for w in (d, wh)]
        ecrire(os.path.join(wh, "b.txt"), "b\n")
        commit_matin(wh, "LOC1 : a", 2)                 # une fiche de LOC jouée dans le worktree, pas dans main
        joue = [noms_ailleurs(w) for w in (d, wh)]
    verifier("NUI28 (c) ISO2 : même chantier hérité, aucun commit de fiche d'un côté ni de l'autre → ni main ni le "
             "worktree ne nomment l'autre (TODO 140) — mutant : toujours nommer",
             herite == [[], []], herite)
    verifier("NUI28 (d) ISO2 : même code, une fiche LOC jouée dans le worktree → main le nomme, le worktree ne nomme "
             "pas main — mutant : toujours nommer",
             joue == [[("LOC", "wt-h")], []], joue)


groupe(tester_ailleurs_meme_chantier)


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


def tester_sante_reglages():
    """REF3 (D5) : la commande ruff de `sante` lit `pyproject.toml` — sans `--isolated`. Un faux ruff rend ses
    arguments, que `lancer_ruff` reçoit comme sa sortie."""
    import sante
    sortie = sante.lancer_ruff([sys.executable, "-c", "import json, sys; print(json.dumps(sys.argv[1:]))"], ["x.py"])
    args = json.loads(sortie)
    verifier("sante : la commande ruff lit pyproject.toml, sans --isolated",
             "--isolated" not in args and args[:1] == ["check"] and args[-1] == "x.py", sortie)


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
             porte_motif(tester_iso4_fusionner_fiche, "le principal en tête") and not porte_motif(tester_mutant, "le principal en tête"),
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
groupe(tester_sante_reglages)
groupe(tester_sante_cliquet)
groupe(tester_sante_si_base)
groupe(tester_sante_kit)
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
