#!/usr/bin/env python3
"""Teste boucle.py avec le faux `claude` de `scripts/faux-claude.py` : aucun appel modèle.

Le faux joue un rôle par prompt (découper, jouer, clore, relire) et rend les lignes
`stream-json` de NUI1 ; ses pilotes `VLP_FAUX_*` sont dans sa docstring. Ce fichier
teste boucle.py avec lui, puis le faux lui-même, rôle par rôle et pilote par pilote.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import importlib.util
import io
import json
import os
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

FAUX_CLAUDE = os.path.join(ICI, "faux-claude.py")
_spec = importlib.util.spec_from_file_location("faux_claude", FAUX_CLAUDE)
assert _spec and _spec.loader
_faux: Any = importlib.util.module_from_spec(_spec)  # `FICHE` y vit : un seul gabarit de fiche
_spec.loader.exec_module(_faux)
FICHE = _faux.FICHE


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
    return FAUX_CLAUDE


def boucle(t, faux, plafond, rate="", options=()):
    env = dict(os.environ, VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_RATE=rate,
               PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ICI, "boucle.py"), t, "--plafond", str(plafond),
                        "--claude", faux, "--traces", t] + list(options), env=env, capture_output=True, text=True, encoding="utf-8")
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
    verifier("git add et git commit autorisés, --amend et --no-verify interdits, rien d'autre",
             "--allowedTools,Bash(git add:*),Bash(git commit:*),PowerShell(git add:*),"
             "PowerShell(git commit:*),--disallowedTools,Bash(git commit --amend:*)," in s
             and "PowerShell(git commit --no-verify:*)" in s and "push" not in s, s)
    verifier("TOTAL additionne tours et coût", "TOTAL 2 fiches · 6 tours · 0.0200 $" in s, s)
    verifier("sans --effort, aucun effort transmis", "--effort" not in s, s)

with tempfile.TemporaryDirectory() as t:
    code, s, cases = boucle(t, projet(t), 1, options=["--effort", "low"])
    verifier("--effort low transmis tel quel à claude", code == 0 and "--effort,low" in s, s)

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


# --- le faux lui-même : un rôle par prompt, un pilote par variable (NUI2) -------------

def faux(args, cwd, **env):
    base = {k: v for k, v in os.environ.items() if not k.startswith("VLP_FAUX_")}
    base.update(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), PYTHONIOENCODING="utf-8")
    base.update(env)
    r = subprocess.run([sys.executable, FAUX_CLAUDE] + args, cwd=cwd, env=base, capture_output=True,
                       text=True, encoding="utf-8")
    return r.returncode, [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")], r.stderr


def lire(chemin):
    with open(chemin, encoding="utf-8") as h:
        return h.read()


def verdict_de(lignes):
    return next((str(x.get("result")) for x in lignes if x["type"] == "result"), "")


# Le premier test qui passe par la ligne `return 2  # prompt inconnu` du faux : un mutant qui la change tombe ici.
r = subprocess.run([sys.executable, FAUX_CLAUDE, "-p", "bonjour"], capture_output=True, text=True, encoding="utf-8")
verifier("faux : prompt inconnu → code 2",
         r.returncode == 2 and len(r.stderr.strip().splitlines()) == 1 and r.stdout == "", (r.returncode, r.stdout, r.stderr))

with tempfile.TemporaryDirectory() as t:
    projet(t)
    carte, fiches, nouveau =(os.path.join(t, n) for n in ("CHANTIER.md", "fiches.md", "T.md"))
    avant = lire(fiches)
    code, _, e = faux(["-p", "/vlp:chantier T"], t)
    verifier("faux découper : T.md à deux fiches, courant de CHANTIER.md remplacé, fiches.md intact",
             code == 0 and os.path.isfile(nouveau) and "## T1 [ ]" in lire(nouveau) and "## T2 [ ]" in lire(nouveau)
             and lire(nouveau).count("<!-- FICHE:") == 2
             and "**fichier de fiches courant** : T.md (T1..T2)" in lire(carte) and lire(fiches) == avant, e)
    code, _, e = faux(["-p", "/vlp:tache T1"], t)
    verifier("faux jouer coche dans le fichier courant",
             code == 0 and "## T1 [x]" in lire(nouveau) and "## T2 [ ]" in lire(nouveau) and lire(fiches) == avant, e)
    code, _, e = faux(["-p", "/vlp:tache T2"], t, VLP_FAUX_RATE="T2")
    verifier("faux jouer : VLP_FAUX_RATE laisse la case", code == 0 and "## T2 [ ]" in lire(nouveau), e)
    code, _, e = faux(["-p", "/vlp:tache T1"], t)
    verifier("faux jouer : cocher non nul → sa sortie sur stderr, code 2", code == 2 and "déjà cochée" in e, e)
    with open(carte, "a", encoding="utf-8", newline="") as h:
        h.write("- **artefact du chantier** : https://exemple.invalid/x\n")
    code, _, e = faux(["-p", "/vlp:tache"], t)
    verifier("faux clore : courant et artefact passent à aucun",
             code == 0 and "**fichier de fiches courant** : aucun" in lire(carte)
             and "**artefact du chantier** : aucun" in lire(carte), lire(carte) + e)

with tempfile.TemporaryDirectory() as t:
    relire = ["--agent", "vlp:relecture", "--model", "claude-opus-5-5"]
    code, l, e = faux(["-p", "F1 --sha abc123"] + relire, t)
    verifier("faux relire : ACCEPTÉE par défaut, outils de relecture dans init",
             code == 0 and verdict_de(l).startswith("ACCEPTÉE — ") and l[0]["tools"] == ["Read", "Edit", "Bash", "PowerShell"], l)
    code, l, e = faux(["-p", "F1"] + relire, t, VLP_FAUX_REFUSE="F1:fiche")
    verifier("faux relire : VLP_FAUX_REFUSE fiche → REFUSÉE — fiche : puis RÉÉCRITURE",
             verdict_de(l).startswith("REFUSÉE — fiche : ") and "\nRÉÉCRITURE : " in verdict_de(l), l)
    code, l, e = faux(["-p", "F1"] + relire, t, VLP_FAUX_REFUSE="F1:copie")
    verifier("faux relire : VLP_FAUX_REFUSE copie → REFUSÉE — copie : sans RÉÉCRITURE",
             verdict_de(l).startswith("REFUSÉE — copie : ") and "RÉÉCRITURE" not in verdict_de(l), l)
    code, l, e = faux(["-p", "F2"] + relire, t, VLP_FAUX_REFUSE="F1:fiche")
    verifier("faux relire : une autre fiche reste ACCEPTÉE", verdict_de(l).startswith("ACCEPTÉE — "), l)
    code, l, e = faux(["-p", "F1 --sha"] + relire, t)
    verifier("faux relire : prompt mal formé → code 2", code == 2 and l == [], (code, l, e))

with tempfile.TemporaryDirectory() as t:
    projet(t)
    jouer =["-p", "/vlp:tache F9"]
    sid = "11111111-2222-3333-4444-555555555555"
    code, l, e = faux(jouer + ["--session-id", sid], t, VLP_FAUX_RATE="F9")
    verifier("faux : init et result portent l'id de --session-id",
             code == 0 and l[0]["subtype"] == "init" and l[0]["session_id"] == sid and l[-1]["session_id"] == sid
             and l[-1]["num_turns"] == 3 and l[-1]["total_cost_usd"] == 0.01, l)
    code, l, e = faux(jouer + ["--model", "claude-opus-5-5"], t, VLP_FAUX_LIMITE="claude-opus", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_LIMITE rend la limite au modèle qui commence par le préfixe",
             code == 1 and l[-1]["is_error"] is True and l[-1]["result"].startswith("You've hit your session limit"), l)
    code, l, e = faux(jouer + ["--model", "claude-sonnet-5-5"], t, VLP_FAUX_LIMITE="claude-opus", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_LIMITE laisse passer un autre modèle", code == 0 and l[-1]["is_error"] is False, l)
    code, l, e = faux(jouer + ["--model", "claude-inexistant-9", "--fallback-model", "claude-opus-5,claude-sonnet-5-5"],
                      t, VLP_FAUX_REPLI="1", VLP_FAUX_RATE="F9")
    vus = [x["message"]["model"] for x in l if x["type"] == "assistant"]
    verifier("faux : VLP_FAUX_REPLI → message.model et modelUsage au premier repli, ligne model_fallback",
             code == 0 and vus == ["claude-opus-5"] and list(l[-1]["modelUsage"]) == ["claude-opus-5"]
             and any(x.get("subtype") == "model_fallback" for x in l), l)
    debut = time.time()
    faux(jouer, t, VLP_FAUX_DORT="0.4", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_DORT dort avant de répondre", time.time() - debut >= 0.4, time.time() - debut)
    code, l, e = faux(jouer, t, VLP_FAUX_ERREUR="coupure", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_ERREUR=coupure → init puis rien, ni result, code 1",
             code == 1 and [x["type"] for x in l] == ["system"], (code, l))
    code, l, e = faux(jouer, t, VLP_FAUX_ERREUR="api", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_ERREUR=api → message <synthetic>, result is_error vrai, code 1",
             code == 1 and l[1]["message"]["model"] == "<synthetic>" and l[-1]["is_error"] is True
             and l[-1]["terminal_reason"] == "api_error" and l[-1]["total_cost_usd"] == 0, (code, l))
    for forme, sous in (("tours", "error_max_turns"), ("budget", "error_max_budget_usd")):
        code, l, e = faux(jouer, t, VLP_FAUX_ERREUR=forme, VLP_FAUX_RATE="F9")
        verifier("faux : VLP_FAUX_ERREUR=%s → %s, is_error vrai, sans clé result, code 1" % (forme, sous),
                 code == 1 and l[-1]["subtype"] == sous and l[-1]["is_error"] is True and "result" not in l[-1], (code, l))
    code, l, e = faux(jouer, t, VLP_FAUX_ERREUR="zzz", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_ERREUR inconnue → code 2", code == 2 and "zzz" in e, (code, e))

print("OK")
