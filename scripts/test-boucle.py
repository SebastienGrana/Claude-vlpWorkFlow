#!/usr/bin/env python3
"""Teste boucle.py avec un faux `claude` : aucun appel modèle.

Le faux coche la fiche que nomme `/vlp:tache <fiche>`, sauf celles de
`VLP_FAUX_RATE`, et rend une ligne `result` comme `--output-format stream-json`.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import io
import os
import subprocess
import sys
import tempfile

for _flux in (sys.stdout, sys.stderr):
    try:
        if isinstance(_flux, io.TextIOWrapper):
            _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))

FAUX = r'''import json, os, subprocess, sys
fiche = sys.argv[sys.argv.index("-p") + 1].split()[-1]
if fiche not in os.environ.get("VLP_FAUX_RATE", "").split(","):
    subprocess.run([sys.executable, os.environ["VLP_FAUX_VLP"], "cocher", "fiches.md", fiche],
                   stdout=subprocess.DEVNULL)
print(json.dumps({"type": "result", "num_turns": 3, "total_cost_usd": 0.01,
                  "result": "joué " + fiche + " · " + ",".join(sys.argv[1:])}))
'''

FICHE = """<!-- FICHE:%s -->
## %s [ ] — fiche %s

**Prompt**
Rien.

**Critère de fin**%s
Rien.
<!-- /FICHE -->

---

"""


def projet(t, visuel=None, tentatives=None):
    corps = "# Fiches\n\n## Le socle commun\n\nRien.\n\n## L'ordre des fiches\n\nF1, F2, F3.\n\n---\n\n"
    for f in ("F1", "F2", "F3"):
        bloc = FICHE % (f, f, f, " (visuel)" if f == visuel else "")
        if f == tentatives:
            bloc = bloc.replace("**Prompt**", "**Tentatives** (2026-09-26) — non résolu.\n1. RETOUR.\n\n**Prompt**")
        corps += bloc
    with open(os.path.join(t, "fiches.md"), "w", encoding="utf-8", newline="") as h:
        h.write(corps)
    with open(os.path.join(t, "CHANTIER.md"), "w", encoding="utf-8", newline="") as h:
        h.write("# Chantier courant\n\n- **fichier de fiches courant** : fiches.md (F1..F3)\n")
    faux = os.path.join(t, "faux_claude.py")
    with open(faux, "w", encoding="utf-8") as h:
        h.write(FAUX)
    return faux


def boucle(t, faux, plafond, rate=""):
    env = dict(os.environ, VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_RATE=rate,
               PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ICI, "boucle.py"), t, "--plafond", str(plafond),
                        "--claude", faux], env=env, capture_output=True, text=True, encoding="utf-8")
    with open(os.path.join(t, "fiches.md"), encoding="utf-8") as h:
        texte = h.read()
    cases = "".join("x" if ("## %s [x]" % f) in texte else "." for f in ("F1", "F2", "F3"))
    return r.returncode, r.stdout + r.stderr, cases


def verifier(nom, cond, sortie):
    if not cond:
        print("ÉCART:", nom)
        print(sortie)
        sys.exit(1)


with tempfile.TemporaryDirectory() as t:
    code, s, cases = boucle(t, projet(t), 2)
    verifier("plafond 2 : F1 et F2 jouées, F3 non, sort 0",
             code == 0 and cases == "xx." and "ARRÊT plafond de 2 fiches" in s, s + cases)
    verifier("le prompt est /vlp:tache <fiche> et le mode auto par défaut",
             "joué F1 · -p,/vlp:tache F1," in s and "--permission-mode,auto" in s, s)
    verifier("TOTAL additionne tours et coût", "TOTAL 2 fiches · 6 tours · 0.0200 $" in s, s)

with tempfile.TemporaryDirectory() as t:
    code, s, cases = boucle(t, projet(t), 5)
    verifier("tout joué : arrêt « aucune », sort 0",
             code == 0 and cases == "xxx" and "ARRÊT aucune fiche à jouer" in s, s + cases)

with tempfile.TemporaryDirectory() as t:
    code, s, cases = boucle(t, projet(t), 5, rate="F2")
    verifier("F2 non cochée : arrêt, F3 non jouée, sort 1",
             code == 1 and cases == "x.." and "ARRÊT F2 non cochée" in s and "JOUE F3" not in s, s + cases)

with tempfile.TemporaryDirectory() as t:
    code, s, cases = boucle(t, projet(t, visuel="F2"), 5, rate="F2")
    verifier("F2 (visuel) : jouée, puis arrêt prévu, sort 0",
             code == 0 and cases == "x.." and "ARRÊT F2 est (visuel)" in s and "JOUE F3" not in s, s + cases)

with tempfile.TemporaryDirectory() as t:
    code, s, cases = boucle(t, projet(t, tentatives="F1"), 5)
    verifier("F1 à bloc Tentatives : rien joué, sort 1",
             code == 1 and cases == "..." and "JOUE" not in s and "Tentatives" in s, s + cases)

print("OK")
