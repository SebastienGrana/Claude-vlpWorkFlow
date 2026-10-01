#!/usr/bin/env python3
"""Teste boucle.py avec le faux `claude` de `scripts/faux-claude.py` : aucun appel modèle.

Le faux joue un rôle par prompt (découper, jouer, clore, relire) et rend les lignes
`stream-json` de NUI1 ; ses pilotes `VLP_FAUX_*` sont dans sa docstring. Ce fichier
teste boucle.py avec lui, puis le faux lui-même, rôle par rôle et pilote par pilote.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import argparse
import contextlib
import glob
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any

import carnet

for _flux in (sys.stdout, sys.stderr):
    try:
        if isinstance(_flux, io.TextIOWrapper):
            _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))

# Le `~` du poste ne sert à personne ici (NUI8) : une transcription lue ou écrite sous `~/.claude/projects` va dans un
# dossier jeté, pour tous les cas — ceux d'avant comme ceux de la reprise (qui posent le leur, un par cas).
_HOME = tempfile.TemporaryDirectory()
os.environ["HOME"] = os.environ["USERPROFILE"] = _HOME.name

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


_PASSES = [0]   # cas passés : `verifier` sort au premier écart, donc ceux qui l'ont passé sont ceux qui sont écrits


def verifier(nom, cond, sortie):
    if not cond:
        print("ÉCART:", nom)
        print(sortie)
        sys.exit(1)
    _PASSES[0] += 1


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
    for genre, debut_texte in (("opus", "You've hit your Opus limit"), ("semaine", "You've hit your weekly limit")):
        code, l, e = faux(jouer + ["--model", "claude-opus-5-5"], t, VLP_FAUX_LIMITE="claude-opus",
                          VLP_FAUX_GENRE=genre, VLP_FAUX_RATE="F9")
        verifier("faux : VLP_FAUX_GENRE=%s → le texte de la limite de ce genre" % genre,
                 code == 1 and l[-1]["result"].startswith(debut_texte), l)
    code, l, e = faux(jouer + ["--model", "claude-opus-5-5"], t, VLP_FAUX_LIMITE="claude-opus",
                      VLP_FAUX_GENRE="zzz", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_GENRE inconnu → code 2", code == 2 and "zzz" in e, (code, e))
    code, l, e = faux(jouer, t, VLP_FAUX_DENIALS="2", VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_DENIALS=2 → permission_denials de 2 entrées, is_error faux",
             code == 0 and len(l[-1]["permission_denials"]) == 2 and l[-1]["is_error"] is False, l)
    journal = os.path.join(t, "argv.jsonl")
    faux(jouer + ["--model", "claude-sonnet-5-5"], t, VLP_FAUX_ARGV=journal, VLP_FAUX_RATE="F9")
    verifier("faux : VLP_FAUX_ARGV ajoute une ligne JSON des arguments reçus",
             json.loads(lire(journal).splitlines()[-1]) == jouer + ["--model", "claude-sonnet-5-5"], lire(journal))
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


# --- le carnet de nuit et la borne double (NUI3) --------------------------------------

# Git sans le poste (NUI5) : config globale et système neutralisées, une identité d'essai — comme test-vlp.py.
_GIT_TMP = tempfile.TemporaryDirectory()
with open(os.path.join(_GIT_TMP.name, "gitconfig"), "w", encoding="utf-8") as _h:
    _h.write("")
ENV_GIT = dict(GIT_CONFIG_GLOBAL=os.path.join(_GIT_TMP.name, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def git(t, *args):
    r = subprocess.run(["git"] + list(args), cwd=t, env=dict(os.environ, **ENV_GIT), check=True,
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def depot(t):
    """`git init` dans `t`, le projet de test, puis un commit initial : le carnet vit dans son `.git`,
    et la boucle de nuit commite sur ACCEPTÉE."""
    subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
    faux_ = projet(t)
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "init")
    return faux_


def carnet_de(t):
    chemin = carnet.du_jour(t)
    assert chemin, "pas de carnet : %s n'est pas un dépôt Git" % t
    return chemin


def cases_de(t):
    texte = lire(os.path.join(t, "fiches.md"))
    return "".join("x" if ("## %s [x]" % f) in texte else "." for f in ("F1", "F2", "F3"))


def nuit(t, *options, rate="", claude=FAUX_CLAUDE, traces=None, **env):
    """boucle.py --nuit dans `t` : (code, sortie). VLP_CARNET et VLP_CANAL d'ici ne passent pas. Les traces
    vont hors du dépôt (`traces`, sinon un dossier jeté) : la boucle commite tout ce qu'elle y trouverait."""
    base = {k: v for k, v in os.environ.items() if k not in (carnet.ENV_CARNET, carnet.ENV_CANAL)}
    base.update(ENV_GIT)
    base.update(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_RATE=rate, PYTHONIOENCODING="utf-8")
    base.update(env)
    with tempfile.TemporaryDirectory() as jete:
        r = subprocess.run([sys.executable, os.path.join(ICI, "boucle.py"), t, "--claude", claude, "--traces",
                            traces or jete, "--nuit"] + list(options), env=base, capture_output=True, text=True,
                           encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def tester_nuit():
    canal_a = ("--canal", "A", "--chantier", "X")
    with tempfile.TemporaryDirectory() as t:
        depot(t)
        code, s = nuit(t, *canal_a)
        tout = [d for d in carnet.lire(carnet_de(t)) if carnet.est_session(d)]   # les notes `depart` (NUI8) sont hors tri
        lignes = [d for d in tout if d["role"] == "jouer"]
        verifier("NUI3 (a) --nuit, 3 fiches : 3 lignes `jouer` (et 3 `relire`, NUI5) aux clés de CLES, canal A, "
                 "usd_cli du faux, usd_kit et tours_kit à null, session lue dans init",
                 code == 0 and cases_de(t) == "xxx" and "ARRÊT aucune fiche à jouer" in s and len(lignes) == 3
                 and [d["role"] for d in tout] == ["jouer", "relire"] * 3
                 and all(set(d) == set(carnet.CLES) for d in lignes)
                 and [d["fiche"] for d in lignes] == ["F1", "F2", "F3"]
                 and all(d["canal"] == "A" and d["chantier"] == "X" and d["role"] == "jouer" and d["usd_cli"] == 0.01
                         and d["tours_cli"] == 3 and d["usd_kit"] is None and d["tours_kit"] is None
                         and d["nuit"] == carnet.nuit_de(carnet_de(t)) and isinstance(d["duree_s"], int)
                         and len(d["session"] or "") == 36 for d in lignes), (s, lignes))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        chemin = carnet_de(t)
        carnet.ajouter(chemin, canal="B", chantier="Y", role="jouer", fiche="Z1", usd_cli=1.0)
        code, s = nuit(t, *canal_a, "--borne-usd", "1.0")
        verifier("NUI3 (b) pot des lignes B ≥ borne : rien joué, ARRÊT borne atteinte, sort 0",
                 code == 0 and "JOUE" not in s and cases_de(t) == "..." and "ARRÊT borne atteinte — pot 1.0000 $" in s, s)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        chemin = carnet_de(t)
        carnet.ajouter(chemin, canal="B", chantier="Y", role="jouer", fiche="Z1", usd_cli=0.01)
        carnet.ajouter(chemin, canal="B", chantier="Y", role="jouer", fiche="Z2", usd_cli=9.0, note="hors pot")
        code, s = nuit(t, *canal_a, "--borne-usd", "0.015")
        verifier("NUI3 (b) pot à moins d'une session de la borne : une fiche jouée, puis ARRÊT borne atteinte ; "
                 "une `note` à role posé reste hors pot",
                 code == 0 and s.count("JOUE ") == 1 and cases_de(t) == "x.." and "ARRÊT borne atteinte" in s, s)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        chemin = carnet_de(t)
        for ch in ("Y", "Z"):
            carnet.ajouter(chemin, canal="B", chantier=ch, role="jouer", fiche=ch + "1", usd_cli=0.0)
        code, s = nuit(t, *canal_a, "--borne-chantiers", "2")
        verifier("NUI3 (c) 2 chantiers au carnet, --borne-chantiers 2, chantier neuf : rien joué",
                 code == 0 and "JOUE" not in s and "ARRÊT borne atteinte — 2 chantiers ≥ borne 2" in s, s)
        code, s = nuit(t, "--canal", "A", "--chantier", "Y", "--borne-chantiers", "2")
        verifier("NUI3 (c) le chantier déjà au carnet, lui, part", code == 0 and cases_de(t) == "xxx", s)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        carnet.stop(carnet_de(t), "B", "raison de B")
        code, s = nuit(t, *canal_a)
        verifier("NUI3 (d) stop() de B : le canal A rend ARRÊT STOP, rien joué, sort 1",
                 code == 1 and "ARRÊT STOP — raison de B" in s and "JOUE" not in s and cases_de(t) == "...", s)

    with tempfile.TemporaryDirectory() as t:
        c = os.path.join(t, "e.jsonl")
        verrou = c + ".verrou"
        with open(verrou, "w", encoding="utf-8") as h:
            h.write("4242")
        vieux = time.time() - 60
        os.utime(verrou, (vieux, vieux))
        carnet.ajouter(c, canal="A", note="n1")
        lignes = carnet.lire(c)
        verifier("NUI3 (e) verrou vieilli de 60 s : cassé, une ligne garde nomme le PID et l'âge, puis la ligne ; "
                 "verrou retiré",
                 len(lignes) == 2 and "PID 4242" in str(lignes[0]["garde"]) and "âge 6" in str(lignes[0]["garde"])
                 and lignes[1]["note"] == "n1" and not os.path.exists(verrou), lignes)

        c = os.path.join(t, "e2.jsonl")
        verrou = c + ".verrou"
        with open(verrou, "w", encoding="utf-8") as h:
            h.write("4242")
        threading.Timer(0.3, os.remove, [verrou]).start()
        debut = time.time()
        carnet.ajouter(c, canal="A", note="n2")
        lignes = carnet.lire(c)
        verifier("NUI3 (e) verrou jeune retiré pendant l'attente : ligne écrite après l'attente, sans garde",
                 len(lignes) == 1 and lignes[0]["garde"] is None and time.time() - debut >= 0.25, (lignes, time.time() - debut))

        c = os.path.join(t, "e3.jsonl")
        code_script = ("import sys; sys.path.insert(0, %r); import carnet\n"
                       "for i in range(50): carnet.ajouter(sys.argv[1], canal=sys.argv[2], note=str(i))\n" % ICI)
        procs = [subprocess.Popen([sys.executable, "-c", code_script, c, canal]) for canal in "AB"]
        codes = [p.wait() for p in procs]
        brutes = lire(c).splitlines()
        valides = [d for d in (json.loads(b) for b in brutes) if isinstance(d, dict)]
        verifier("NUI3 (e) 2 processus × 50 écritures : 100 lignes JSON valides, 50 par canal, aucune garde",
                 codes == [0, 0] and len(brutes) == 100 and len(valides) == 100
                 and sum(d["canal"] == "A" for d in valides) == 50 and all(d["garde"] is None for d in valides), (codes, len(brutes)))

        c = os.path.join(t, "e4.jsonl")
        with open(c, "w", encoding="utf-8", newline="") as h:
            h.write('{"nuit": "coupée')
        carnet.ajouter(c, canal="A", note="après la coupure")
        lignes = carnet.lire(c)
        verifier("NUI3 : la ligne coupée en pleine écriture est sautée, la suivante reste lisible",
                 len(lignes) == 1 and lignes[0]["note"] == "après la coupure", lignes)
        avant = lire(c)
        try:
            carnet.ajouter(c, canal="A", inconnue="x")
            refuse = False
        except ValueError:
            refuse = True
        verifier("NUI3 : une clé inconnue est refusée, rien d'écrit, pas de verrou resté",
                 refuse and lire(c) == avant and not os.path.exists(c + ".verrou"), lire(c))

    with tempfile.TemporaryDirectory() as t:
        stub = os.path.join(t, "rec.py")
        with open(stub, "w", encoding="utf-8", newline="") as h:
            h.write("import json, os, sys\n"
                    "d = os.path.dirname(os.path.abspath(__file__))\n"
                    "json.dump({k: os.environ.get(k) for k in ('VLP_CARNET', 'VLP_CANAL')}, "
                    "open(os.path.join(d, 'env.json'), 'w'))\n"
                    "print(json.dumps({'type': 'system', 'subtype': 'init', 'session_id': 's-1'}))\n"
                    "print(json.dumps({'type': 'assistant', 'message': {'model': 'm'}}))\n"
                    "print(json.dumps({'type': 'result', 'num_turns': 1, 'total_cost_usd': 0.5, 'result': 'x'}))\n")
        depot(t)
        chemin = carnet_de(t)
        code, s = nuit(t, "--canal", "A", "--chantier", "X", "--plafond", "1", claude=stub)
        env = json.loads(lire(os.path.join(t, "env.json")))
        lignes = [d for d in carnet.lire(chemin) if carnet.est_session(d)]
        verifier("NUI3 : la fille reçoit VLP_CARNET et VLP_CANAL ; la ligne porte tours, coût et session du result/init, "
                 "même case non cochée",
                 env == {"VLP_CARNET": chemin, "VLP_CANAL": "A"} and len(lignes) == 1 and lignes[0]["session"] == "s-1"
                 and lignes[0]["usd_cli"] == 0.5 and lignes[0]["tours_cli"] == 1, (env, lignes, s))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        code, s, cases = boucle(t, FAUX_CLAUDE, 3)
        verifier("NUI3 (f) sans --nuit : rien joué de plus, aucun vlp-nuit dans .git",
                 code == 0 and cases == "xxx" and not os.path.exists(os.path.join(t, ".git", "vlp-nuit")), s)
        code, s, cases = boucle(t, FAUX_CLAUDE, 1, options=["--canal", "A"])
        verifier("NUI3 : --canal sans --nuit est refusé (code 2)", code == 2 and "exigent --nuit" in s, s)
        code, s = nuit(t, "--chantier", "X")
        verifier("NUI3 : --nuit sans --canal est refusé (code 2)", code == 2 and "--nuit exige" in s, s)
        r = subprocess.run([sys.executable, os.path.join(ICI, "boucle.py"), t, "--claude", FAUX_CLAUDE],
                           capture_output=True, text=True, encoding="utf-8")
        verifier("NUI3 : sans --nuit, --plafond reste exigé (code 2)",
                 r.returncode == 2 and "--plafond est exigé" in r.stderr, r.stderr)


tester_nuit()


# --- les plafonds de chaque rôle, l'issue de chaque session, la limite d'usage (NUI4) -----

_spec_b = importlib.util.spec_from_file_location("boucle", os.path.join(ICI, "boucle.py"))
assert _spec_b and _spec_b.loader
bmod: Any = importlib.util.module_from_spec(_spec_b)   # `jouer()` y est appelé tel quel, un rôle à la fois
_spec_b.loader.exec_module(bmod)
_spec_k = importlib.util.spec_from_file_location("vlp", os.path.join(ICI, "vlp.py"))
assert _spec_k and _spec_k.loader
kit: Any = importlib.util.module_from_spec(_spec_k)    # source indépendante des `maxTurns` attendus
_spec_k.loader.exec_module(kit)
OPUS, SONNET, REPLI = "claude-opus-5-5", "claude-sonnet-5-5", "claude-opus-5,claude-sonnet-5-5"


def tours_de(agent):
    return kit.lire_max_turns(os.path.join(ICI, os.pardir, "agents", agent))


@contextlib.contextmanager
def pilote(**pilotes):
    """Pose des variables d'environnement le temps d'un bloc : `jouer()` les passe au faux."""
    avant = {k: os.environ.get(k) for k in pilotes}
    os.environ.update(pilotes)
    try:
        yield
    finally:
        for k, v in avant.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def drapeau(argv, nom):
    return argv[argv.index(nom) + 1] if nom in argv else None


def lancer(t, role="relire", controle=None, fiche="F1", **pilotes):
    """`jouer()` du module chargé, sous --nuit, dans le dépôt de test `t` : (rendu, lignes de session, arguments)."""
    journal = os.path.join(t, "argv.jsonl")
    ns = argparse.Namespace(nuit=True, canal="A", chantier="X", carnet=carnet_de(t), permission_mode="auto",
                            model=None, effort=None, budget=None)
    with pilote(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_ARGV=journal, **pilotes):
        s = bmod.jouer(FAUX_CLAUDE, fiche, t, ns, os.path.join(t, "%s.jsonl" % role), role=role, controle=controle)
    sessions = [d for d in carnet.lire(carnet_de(t)) if carnet.est_session(d)]
    argvs = [json.loads(ligne) for ligne in lire(journal).splitlines()] if os.path.exists(journal) else []
    return s, sessions, argvs


def tester_plafonds():
    canal_a = ("--canal", "A", "--chantier", "X")
    bmod.BASCULE["jusqu"] = 0.0

    with tempfile.TemporaryDirectory() as t:
        projet(t)
        code, s, cases = boucle(t, FAUX_CLAUDE, 1)
        verifier("NUI4 (a) sans --nuit : ni --max-turns, ni --session-id, ni --permission-prompts, ni --fallback-model, "
                 "ni --max-budget-usd",
                 code == 0 and "joué F1 · -p," in s and not any(
                     o in s for o in ("--max-turns", "--session-id", "--permission-prompts", "--fallback-model",
                                      "--max-budget-usd")), s)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        code, s = nuit(t, *canal_a, "--plafond", "1")
        ligne = next(d for d in carnet.lire(carnet_de(t)) if carnet.est_session(d))
        verifier("NUI4 (b) --nuit, jouer : modèle, effort, plafonds, permission-prompts, --session-id = clé session "
                 "du carnet, sans repli",
                 code == 0 and all(x in s for x in (
                     "--model,claude-sonnet-5-5", "--effort,low", "--max-budget-usd,5", "--permission-prompts,none",
                     "--max-turns,%d" % tours_de("fiche.md"), "--session-id,%s" % ligne["session"]))
                 and "--fallback-model" not in s, s)
        verifier("NUI4 : la ligne du carnet porte modele_demande, modeles_vus et issue",
                 ligne["modele_demande"] == SONNET and ligne["modeles_vus"] == [SONNET] and ligne["issue"] == "jouée", ligne)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        ordre = (("relire", "F1"), ("jouer", "F1"), ("relance", "F2"), ("clore", "F1"), ("découper", "T"))
        argvs: list[Any] = []
        for role, fiche in ordre:
            _, _, argvs = lancer(t, role, fiche=fiche)
        vus = {role: (drapeau(a, "-p"), drapeau(a, "--model"), drapeau(a, "--fallback-model"), drapeau(a, "--effort"),
                      int(drapeau(a, "--max-turns") or 0),drapeau(a, "--max-budget-usd"), drapeau(a, "--agent"),
                      "--allowedTools" in a) for (role, _), a in zip(ordre, argvs)}
        attendu = {"relire": ("F1", OPUS, REPLI, None, tours_de("relecture.md"), "3", "vlp:relecture", False),
                   "jouer": ("/vlp:tache F1", SONNET, None, "low", tours_de("fiche.md"), "5", None, False),   # NUI5
                   "relance": ("/vlp:tache F2", OPUS, REPLI, "medium", tours_de("fiche.md"), "5", None, True),
                   "clore": ("/vlp:tache", OPUS, REPLI, None, 60, "5", None, True),
                   "découper": ("/vlp:chantier T", OPUS, REPLI, None, 150, "20", None, False)}
        verifier("NUI4 (b)(c) les cinq rôles par jouer() : prompt, modèle, repli, effort, tours (relire : maxTurns de "
                 "relecture.md), $, agent, --allowedTools",
                 vus == attendu, (vus, attendu))
        verifier("NUI4 : une session --nuit = un --session-id neuf et --permission-prompts none ; relire et découper "
                 "sans git qui écrit, jouer sans --amend",
                 len({drapeau(a, "--session-id") for a in argvs}) == 5
                 and all(drapeau(a, "--permission-prompts") == "none" for a in argvs)
                 and all("Bash(git commit:*)" in argvs[i] and "Bash(git add:*)" in argvs[i] for i in (0, 4))
                 and "Bash(git commit --amend:*)" in argvs[1], argvs)
        verifier("NUI4 : max_tours rend l'entier de la table ou le maxTurns du fichier d'agent",
                 bmod.max_tours("découper") == 150 and bmod.max_tours("relire") == tours_de("relecture.md")
                 and bmod.max_tours("jouer") == tours_de("fiche.md"), None)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        bmod.ROLES["relire"]["timeout"] = 2
        try:
            debut = time.time()
            s, sessions, _ = lancer(t, VLP_FAUX_DORT="60")
        finally:
            bmod.ROLES["relire"]["timeout"] = bmod.TIMEOUT_S
        verifier("NUI4 (d) DORT 60 s au-delà d'un timeout de 2 s (ROLES[rôle][\"timeout\"]) : issue timeout, rendu en "
                 "moins de 30 s (processus tué), ni tours ni coût au carnet, pas de stop",
                 s["issue"] == "timeout" and time.time() - debut < 30 and [x["issue"] for x in sessions] == ["timeout"]
                 and sessions[0]["tours_cli"] is None and sessions[0]["usd_cli"] is None and s["stop"] is None, (s, sessions))

    for nom, pilotes, attendue in (("coupure", {"VLP_FAUX_ERREUR": "coupure"}, "coupure"),
                                   ("max_turns", {"VLP_FAUX_ERREUR": "tours"}, "plafond"),
                                   ("max_budget", {"VLP_FAUX_ERREUR": "budget"}, "plafond")):
        with tempfile.TemporaryDirectory() as t:
            depot(t)
            s, sessions, _ = lancer(t, **pilotes)
            verifier("NUI4 (e) %s → %s au carnet, aucune ligne stop" % (nom, attendue),
                     s["issue"] == attendue and [x["issue"] for x in sessions] == [attendue]
                     and carnet.stop_de(carnet.lire(carnet_de(t))) is None, (s, sessions))
            if nom == "coupure":
                verifier("NUI4 (e) coupure : tours_cli et usd_cli à null, pas 0", sessions[0]["tours_cli"] is None
                         and sessions[0]["usd_cli"] is None, sessions)

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        with pilote(VLP_FAUX_ERREUR="api"):
            code, s = nuit(t, *canal_a)
        lignes = carnet.lire(carnet_de(t))
        verifier("NUI4 (e) erreur api → pas partie, ligne stop au carnet, ARRÊT STOP, sort 1, rien coché",
                 code == 1 and "ARRÊT STOP — session pas partie" in s and cases_de(t) == "..."
                 and [d["issue"] for d in lignes if carnet.est_session(d)] == ["pas partie"]
                 and (carnet.stop_de(lignes) or "").startswith("session pas partie"), (s, lignes))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        with pilote(VLP_FAUX_DENIALS="2"):
            code, s = nuit(t, *canal_a)
        lignes = carnet.lire(carnet_de(t))
        sessions = [d for d in lignes if carnet.est_session(d)]
        verifier("NUI4 (e) refus de permission et case cochée → jouée sans stop, leur nombre dans garde, 3 fiches "
                 "(3 jeux et 3 relectures, NUI5)",
                 code == 0 and cases_de(t) == "xxx" and [d["issue"] for d in sessions] == ["jouée"] * 6
                 and all(d["garde"] == "permission_denials : 2" for d in sessions) and carnet.stop_de(lignes) is None,
                 (s, lignes))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        s, sessions, _ = lancer(t, controle=lambda: False)
        verifier("NUI4 (e) contrôle du rôle échoué → ratée, sans stop",
                 s["issue"] == "ratée" and s["ok"] is False and [x["issue"] for x in sessions] == ["ratée"]
                 and s["stop"] is None, (s, sessions))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        s, sessions, argvs = lancer(t, VLP_FAUX_LIMITE="claude-opus", VLP_FAUX_GENRE="opus")
        bascule = bmod.BASCULE["jusqu"]
        notes = [d["note"] for d in carnet.lire(carnet_de(t)) if d.get("note") and not d["note"].startswith("depart ")]
        verifier("NUI4 (f) limite opus sur relire : bascule au carnet, session relancée en claude-sonnet-5-5 sans repli, "
                 "issues limite puis jouée, sans stop",
                 s["issue"] == "jouée" and s["stop"] is None and [x["issue"] for x in sessions] == ["limite", "jouée"]
                 and [x["modele_demande"] for x in sessions] == [OPUS, SONNET]
                 and [drapeau(a, "--model") for a in argvs] == [OPUS, SONNET]
                 and drapeau(argvs[1], "--fallback-model") is None
                 and len(notes) == 1 and "bascule Opus → claude-sonnet-5-5" in notes[0]
                 and carnet.stop_de(carnet.lire(carnet_de(t))) is None
                 and time.time() < bascule <= time.time() + 90000, (s, sessions, notes, bascule))
        s, sessions, argvs = lancer(t, VLP_FAUX_LIMITE="claude-opus", VLP_FAUX_GENRE="opus")
        verifier("NUI4 (f) la session Opus suivante part en claude-sonnet-5-5 d'emblée : une session de plus, "
                 "pas de nouvelle limite ni de nouvelle note",
                 [x["issue"] for x in sessions] == ["limite", "jouée", "jouée"]
                 and [drapeau(a, "--model") for a in argvs] == [OPUS, SONNET, SONNET]
                 and len([d for d in carnet.lire(carnet_de(t)) if d.get("note") and not d["note"].startswith("depart ")]) == 1,
                 (sessions, argvs))

    for genre in ("semaine", "session"):
        with tempfile.TemporaryDirectory() as t:
            depot(t)
            bmod.BASCULE["jusqu"] = 0.0
            s, sessions, argvs = lancer(t, VLP_FAUX_LIMITE="claude-opus", VLP_FAUX_GENRE=genre)
            verifier("NUI4 (f) limite %s : issue limite, ligne stop au carnet, ni bascule ni relance" % genre,
                     s["issue"] == "limite" and str(s["stop"]).startswith("limite ")
                     and [x["issue"] for x in sessions] == ["limite"] and len(argvs) == 1
                     and bmod.BASCULE["jusqu"] == 0.0
                     and (carnet.stop_de(carnet.lire(carnet_de(t))) or "").startswith("limite "), (s, sessions))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        with pilote(VLP_FAUX_LIMITE="claude-sonnet"):
            code, s = nuit(t, *canal_a)
        verifier("NUI4 : une limite en boucle --nuit → ARRÊT STOP — limite session, sort 1, rien coché",
                 code == 1 and "ARRÊT STOP — limite session" in s and cases_de(t) == "...", s)

    maintenant = time.time()
    lu = bmod.reset_de("You've hit your Opus limit · resets 3:45pm")
    minuit = time.localtime(bmod.reset_de("You've hit your Opus limit · resets 12:00am"))
    verifier("NUI4 : reset_de lit « resets 3:45pm » (prochain 15:45 local) et « 12:00am » (minuit) ; illisible → fin de nuit",
             maintenant < lu <= maintenant + 90000 and time.localtime(lu)[3:5] == (15, 45)
             and minuit[3:5] == (0, 0) and bmod.reset_de("You've hit your Opus limit") == float("inf"), (lu, minuit))
    bmod.BASCULE["jusqu"] = time.time() + 100
    pendant = (bmod.modele_de("relire"), bmod.modele_de("jouer"))
    bmod.BASCULE["jusqu"] = time.time() - 1
    apres = bmod.modele_de("relire")
    bmod.BASCULE["jusqu"] = 0.0
    verifier("NUI4 : pendant la bascule un rôle Opus passe en Sonnet (jouer y reste), après le reset il revient en Opus",
             pendant == (SONNET, SONNET) and apres == OPUS, (pendant, apres))


tester_plafonds()


# --- relire avant le commit (NUI5) : dépôt avec un commit initial, traces et journaux hors du dépôt -----

def journal_de(chemin):
    return [json.loads(l) for l in lire(chemin).splitlines()] if os.path.exists(chemin) else []


def autorises(argv):
    """Les `--allowedTools` d'une ligne de commande : ce qui suit le drapeau, jusqu'au drapeau suivant."""
    if "--allowedTools" not in argv:
        return []
    suite = argv[argv.index("--allowedTools") + 1:]
    return suite[:next((i for i, x in enumerate(suite) if x.startswith("--")), len(suite))]


def tester_relecture():
    canal_a = ("--canal", "A", "--chantier", "X")

    def nuit_de_test(t, hors, *options, **env):
        argv, envj = os.path.join(hors, "argv.jsonl"), os.path.join(hors, "env.jsonl")
        code, s = nuit(t, *canal_a, *options, traces=hors, VLP_FAUX_ARGV=argv, VLP_FAUX_ENV=envj, **env)
        return code, s, journal_de(argv), journal_de(envj)

    def sessions_de(t):
        return [l for l in lire(os.path.join(t, "fiches.md")).splitlines() if l.startswith("**Session** : ")]

    def sujet(t):
        return git(t, "log", "-1", "--format=%s").strip()

    def nombre(t):
        return git(t, "rev-list", "--count", "HEAD").strip()

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs, envs = nuit_de_test(t, hors, "--plafond", "1")
        jeu, lecture = argvs[0], argvs[1]
        verifier("NUI5 nuit : jouer sans git — ni `git add` ni `git commit` dans ses --allowedTools, `--amend` "
                 "toujours interdit",
                 code == 0 and drapeau(jeu, "-p") == "/vlp:tache F1"
                 and not any("git add" in x or "git commit:" in x for x in autorises(jeu))
                 and "Bash(git commit --amend:*)" in jeu, (s, jeu))
        verifier("NUI5 nuit : canal — le faux du rôle relire voit VLP_CANAL de la boucle",
                 [e["VLP_CANAL"] for e in envs if e["role"] == "relire"] == ["A"]
                 and drapeau(lecture, "--agent") == "vlp:relecture" and drapeau(lecture, "-p") == "F1", (envs, lecture))
        verifier("NUI5 nuit : ACCEPTÉE commite — `F1 : fiche F1`, arbre propre, la seule fiches.md, deux lignes "
                 "Session (jouer, puis relire suffixé)",
                 sujet(t) == "F1 : fiche F1" and nombre(t) == "2" and git(t, "status", "--porcelain") == ""
                 and git(t, "show", "--name-only", "--format=", "HEAD").split() == ["fiches.md"]
                 and sessions_de(t) == ["**Session** : %s" % drapeau(jeu, "--session-id"),
                                        "**Session** : %s (relire)" % drapeau(lecture, "--session-id")],
                 (s, sujet(t), sessions_de(t)))
        ligne = [d for d in carnet.lire(carnet_de(t)) if d["role"] == "relire"]
        verifier("NUI5 : la ligne relire du carnet, session du relecteur, le coût du relecteur au TOTAL",
                 len(ligne) == 1 and ligne[0]["session"] == drapeau(lecture, "--session-id") and ligne[0]["issue"] == "jouée"
                 and "TOTAL 1 fiches · 6 tours · 0.0200 $" in s, (ligne, s))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        # cause `fiche` : `copie` relance depuis NUI6, et la boucle ne s'arrête plus au premier refus
        code, s, argvs, envs = nuit_de_test(t, hors, VLP_FAUX_REFUSE="F1:fiche")
        fiches = lire(os.path.join(t, "fiches.md"))
        ligne = [d for d in carnet.lire(carnet_de(t)) if d["role"] == "relire"]
        verifier("NUI5 nuit : REFUSÉE — aucun commit neuf, bloc Tentatives sous F1, ARRÊT, code 1, refus_n et cause au carnet",
                 code == 1 and nombre(t) == "1" and "## F1 [ ]" in fiches
                 and fiches.index("## F1 [ ]") < fiches.index("**Tentatives**") < fiches.index("## F2")
                 and "Erreur : REFUSÉE — fiche : motif factice" in fiches
                 and "ARRÊT F1 refusée à la relecture — refus 1, cause fiche" in s and "JOUE F2" not in s
                 and len(ligne) == 1 and ligne[0]["refus_n"] == 1 and ligne[0]["cause"] == "fiche", (s, ligne))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        crochet = os.path.join(t, ".git", "hooks", "pre-commit")
        with open(crochet, "w", encoding="utf-8", newline="\n") as h:
            h.write("#!/bin/sh\necho refusé par le crochet\nexit 1\n")
        os.chmod(crochet, 0o755)
        code, s, argvs, envs = nuit_de_test(t, hors)
        ligne = [d for d in carnet.lire(carnet_de(t)) if d["role"] == "relire"]
        verifier("NUI5 nuit : pre-commit refuse — ARRÊT, code 1, aucun commit, garde au carnet, F2 pas jouée",
                 code == 1 and "ARRÊT F1 : commit refusé" in s and nombre(t) == "1" and "JOUE F2" not in s
                 and len(ligne) == 1 and "commit refusé" in str(ligne[0]["garde"]), (s, ligne))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs, envs = nuit_de_test(t, hors, "--plafond", "1", VLP_FAUX_COMMIT="F1", VLP_FAUX_REFUSE="F1:fiche")
        fiches = lire(os.path.join(t, "fiches.md"))
        ligne = [d for d in carnet.lire(carnet_de(t)) if d["role"] == "relire"]
        verifier("NUI5 nuit : TÊTE refusée — le prompt de relire porte --sha HEAD, `git revert` d'abord, puis le bloc "
                 "Tentatives ; ARRÊT, code 1, garde TÊTE au carnet",
                 code == 1 and drapeau(argvs[1], "-p") == "F1 --sha HEAD" and sujet(t) == 'Revert "F1 : fiche F1"'
                 and nombre(t) == "3" and "## F1 [ ]" in fiches and "**Tentatives**" in fiches
                 and len(ligne) == 1 and "TÊTE" in str(ligne[0]["garde"]) and ligne[0]["refus_n"] == 1, (s, sujet(t), ligne))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs, envs = nuit_de_test(t, hors, "--plafond", "1", VLP_FAUX_COMMIT="F1")
        verifier("NUI5 nuit : TÊTE acceptée — la ligne Session du relecteur seule, sujet `F1 : session de relecture`",
                 code == 0 and drapeau(argvs[1], "-p") == "F1 --sha HEAD" and sujet(t) == "F1 : session de relecture"
                 and nombre(t) == "3" and git(t, "show", "--name-only", "--format=", "HEAD").split() == ["fiches.md"]
                 and git(t, "status", "--porcelain") == "" and len(sessions_de(t)) == 2
                 and sessions_de(t)[1] == "**Session** : %s (relire)" % drapeau(argvs[1], "--session-id"), (s, sujet(t)))


tester_relecture()


# --- relancer plus fort sur refus, ou arrêter tôt (NUI6) -------------------------------------------------

def tester_relance():
    canal_a = ("--canal", "A", "--chantier", "X")
    ecrits = [0]

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI6 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI6 " + nom, cond, sortie)

    def nuit_relance(t, hors, *options, etat=False, **env):
        argv = os.path.join(hors, "argv.jsonl")
        if etat:
            env["VLP_FAUX_ETAT"] = os.path.join(hors, "etat.json")
        code, s = nuit(t, *canal_a, *options, traces=hors, VLP_FAUX_ARGV=argv, **env)
        return code, s, journal_de(argv)

    def relances(argvs):
        """Les lancements du rôle relance : l'ID et l'effort de `ROLES["relance"]` (le faux ne les distingue
        du rôle jouer que par là)."""
        r = bmod.ROLES["relance"]
        return [x for x in argvs if drapeau(x, "--model") == r["modele"] and drapeau(x, "--effort") == r["effort"]]

    def lignes_carnet(t, **cles):
        return [d for d in carnet.lire(carnet_de(t)) if all(d.get(k) == v for k, v in cles.items())]

    def arret_de(t):
        """La ligne du carnet d'un arrêt : sans `role`, une `garde`."""
        return [d for d in carnet.lire(carnet_de(t)) if d["role"] is None and d["garde"]]

    def sujets(t):
        return git(t, "log", "--format=%s").split("\n")

    def avec_bloc(t, bloc):
        """Pose un bloc Tentatives sous F1 (le premier `**Prompt**`), commité : l'arbre reste propre."""
        chemin = os.path.join(t, "fiches.md")
        with open(chemin, encoding="utf-8", newline="") as h:
            texte = h.read()
        with open(chemin, "w", encoding="utf-8", newline="") as h:
            h.write(texte.replace("**Prompt**", bloc + "\n\n**Prompt**", 1))
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", "bloc")

    def avec_verification(t, hors, script):
        """CHANTIER.md porte le libellé, la commande lance `script` (écrit dans `hors`) par ce Python."""
        chemin = os.path.join(hors, "verif.py")
        with open(chemin, "w", encoding="utf-8", newline="") as h:
            h.write(script)
        with open(os.path.join(t, "CHANTIER.md"), "a", encoding="utf-8", newline="") as h:
            h.write('- **vérification de nuit** : "%s" "%s"\n' % (sys.executable, chemin))
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", "libellé")

    refus_seuls = ("**Tentatives** (2026-09-26) — non résolu.\n1. FAITE refusée à la relecture.\n"
                   "Erreur : REFUSÉE — copie : motif factice")

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs = nuit_relance(t, hors, "--plafond", "1", etat=True, VLP_FAUX_REFUSE="F1:copie")
        relance = relances(argvs)
        ligne = lignes_carnet(t, role="relance")
        neuf("(a) F1 refusée copie puis acceptée : une session relance (ID et effort du rôle), F1 commitée, "
             "une ligne relance au carnet, refus_n 1, cause copie",
             code == 0 and len(relance) == 1 and sujets(t)[0] == "F1 : fiche F1" and cases_de(t) == "x.."
             and len(ligne) == 1 and ligne[0]["refus_n"] == 1 and ligne[0]["cause"] == "copie"
             and ligne[0]["fiche"] == "F1", (s, relance, ligne))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs = nuit_relance(t, hors, VLP_FAUX_REFUSE="F1:fiche")
        arret = arret_de(t)
        neuf("(b) F1 refusée fiche avec RÉÉCRITURE : aucune relance, aucun commit `F1 :`, reecriture au carnet, "
             "ARRÊT cause-fiche",
             code == 1 and not relances(argvs) and not any(x.startswith("F1 :") for x in sujets(t))
             and "ARRÊT F1 refusée à la relecture — refus 1, cause fiche — garde cause-fiche" in s
             and len(arret) == 1 and arret[0]["garde"] == "cause-fiche" and arret[0]["cause"] == "fiche"
             and arret[0]["reecriture"] == "RÉÉCRITURE : phrase de la fiche → phrase corrigée"
             and arret[0]["refus_n"] == 1, (s, arret))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs = nuit_relance(t, hors, VLP_FAUX_REFUSE="F1:aucun")
        arret = arret_de(t)
        neuf("(b) F1 sans verdict : aucune relance, ARRÊT sans-cause, cause aucune au carnet",
             code == 1 and not relances(argvs) and "RELIT F1 · aucun verdict" in s and "garde sans-cause" in s
             and len(arret) == 1 and arret[0]["garde"] == "sans-cause" and arret[0]["cause"] == "aucune", (s, arret))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs = nuit_relance(t, hors, etat=True, VLP_FAUX_REFUSE="F1:copie,copie")
        fiches = lire(os.path.join(t, "fiches.md"))
        refus = [d["refus_n"] for d in lignes_carnet(t, role="relire")]
        arret = arret_de(t)
        neuf("(c) F1 refusée copie deux fois, motifs différents : une seule relance (qui a coché --resolu), cocher "
             "rend refus 1 au 2e refus, et pourtant refus-max ; F2 pas jouée",
             code == 1 and len(relances(argvs)) == 1 and refus == [1, 1] and "1. FAITE refusée" in fiches
             and "2. FAITE refusée" not in fiches and "motif factice 2" in fiches and "garde refus-max" in s
             and "JOUE F2" not in s and cases_de(t) == "..." and len(arret) == 1 and arret[0]["garde"] == "refus-max"
             and arret[0]["refus_n"] == 2, (s, refus, arret))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        avec_bloc(t, refus_seuls)
        code, s, argvs = nuit_relance(t, hors, VLP_FAUX_REFUSE="F1:copie")
        arret = arret_de(t)
        neuf("(d) F1 à bloc de refus seuls dont Erreur : égale le nouveau motif, bloc remplacé par --resolu : "
             "meme-erreur, pas de relance",
             code == 1 and "JOUE F1" in s and not relances(argvs) and "garde meme-erreur" in s
             and len(arret) == 1 and arret[0]["garde"] == "meme-erreur", (s, arret))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        avec_bloc(t, refus_seuls.replace("\nErreur :", "\n2. RETOUR.\nErreur :"))
        code, s, argvs = nuit_relance(t, hors)
        neuf("(d) un bloc qui n'est pas fait de refus seuls arrête encore, rien joué",
             code == 1 and "porte un bloc Tentatives" in s and "JOUE" not in s and not argvs, (s, argvs))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        avec_verification(t, hors, "import sys\nsys.exit(1)\n")
        code, s, argvs = nuit_relance(t, hors)
        arret = arret_de(t)
        neuf("(e) vérification qui sort 1 : ARRÊT verification avant F1, aucune ligne JOUE",
             code == 1 and "garde verification" in s and "JOUE" not in s and not argvs and cases_de(t) == "..."
             and len(arret) == 1 and arret[0]["garde"] == "verification", (s, arret))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        # passe tant que le dépôt n'a qu'un commit, échoue dès qu'F1 est commitée
        avec_verification(t, hors, "import subprocess, sys\n"
                          "n = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], capture_output=True, text=True)\n"
                          "sys.exit(1 if int(n.stdout) > 2 else 0)\n")
        code, s, argvs = nuit_relance(t, hors)
        neuf("(e) vérification qui réussit avant F1 et échoue après son commit : arrêt après F1, F2 pas jouée",
             code == 1 and "VERIF avant F1 · sort 0" in s and "garde verification" in s and "après son commit" in s
             and cases_de(t) == "x.." and "JOUE F2" not in s and sujets(t)[0] == "F1 : fiche F1", (s, cases_de(t)))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, argvs = nuit_relance(t, hors, "--plafond", "1")
        neuf("(e) libellé absent : F1 jouée, ni ligne VERIF ni garde",
             code == 0 and cases_de(t) == "x.." and "VERIF" not in s and "verification" not in s
             and not arret_de(t), (s, arret_de(t)))

    sys.stderr.write("NUI6 : %d cas neufs passés / %d écrits\n" % (ecrits[0], ecrits[0]))


tester_relance()


# --- enchaîner les chantiers d'un canal (NUI7) -----------------------------------------------------------

def tester_canal():
    DATE = "2026-10-01"
    ecrits = [0]

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI7 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI7 " + nom, cond, sortie)

    def ecrire_f(chemin, texte):
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8", newline="") as h:
            h.write(texte)

    def depot_canal(t, hors, codes, couts=("~2 fiches",) * 3, borne_chantiers=3, codes_b=()):
        """Un dépôt Git équipé, tout commité : CHANTIER.md sans chantier ouvert, la TODO (AAA, BBB qui dépend de AAA,
        CCC) et, si `codes`, le plan du soir `DATE` du canal A — et du canal B pour `codes_b`, NUI9 — écrit par
        `vlp.py plan ecrire`. `hors` : plan et hooks."""
        entete = "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
        subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
        ecrire_f(os.path.join(t, "CHANTIER.md"),
                 "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **fichier d'état** : ctx/08-etat.md\n"
                 "- **fichier de fiches courant** : aucun\n- **artefact du chantier** : aucun\n\n"
                 "Lettres de fiche déjà prises : E (Un), KKK (Clos). Un nouveau chantier en choisit une autre.\n")
        ecrire_f(os.path.join(t, "ctx", "00-INDEX.md"),
                 "# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `00-INDEX.md` | l'index |\n| `08-etat.md` | l'état |\n"
                 "| `100-x.md` | un chantier |\n\nFin.\n")
        ecrire_f(os.path.join(t, "ctx", "08-etat.md"),
                 "# État\n\n" + entete + "| 1 | `AAA` — a | x | %s | — |\n| 2 | `BBB` — b | x | %s | `AAA` |\n"
                 "| 3 | `CCC` — c | x | %s | — |\n\n## Journal\n" % couts)
        ecrire_f(os.path.join(t, "ctx", "100-x.md"), "# x\n")
        if codes:
            plan = {"borne_usd": 5, "borne_chantiers": borne_chantiers,
                    "A": [{"code": c, "prefixe": c, "reponses": []} for c in codes]}
            if codes_b:
                plan["B"] = [{"code": c, "prefixe": c, "reponses": []} for c in codes_b]
            ecrire_f(os.path.join(hors, "plan.json"), json.dumps(plan))
            r = subprocess.run([sys.executable, os.path.join(ICI, "vlp.py"), "plan", "ecrire", t, "--json",
                                os.path.join(hors, "plan.json"), "--date", DATE], capture_output=True, text=True,
                               encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            assert r.returncode == 0, r.stdout + r.stderr
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", "plan")

    def carnet_du(t):
        chemin = carnet.du_jour(t, DATE)
        assert chemin, "pas de carnet : %s n'est pas un dépôt Git" % t
        return carnet.lire(chemin)

    def canal(t, hors, *options, **env):
        """boucle.py --nuit --canal A --date DATE dans `t` : (code, sortie, lignes du carnet de DATE). Le faux clôt
        par un commit, comme `cloture.md:72` ; ce qu'il a vu de l'environnement va dans `hors/env.jsonl`."""
        env.setdefault("VLP_FAUX_CLORE", "commit")
        env.setdefault("VLP_FAUX_ENV", os.path.join(hors, "env.jsonl"))
        code, s = nuit(t, "--canal", "A", "--date", DATE, *options, traces=hors, **env)
        return code, s, carnet_du(t)

    def br(code):
        return "nuit/%s-A-%s" % (DATE, code)

    def sha(t, ref):
        return git(t, "rev-parse", ref).strip()

    def sujet(t, ref):
        return git(t, "log", "-1", "--format=%s", ref).strip()

    def ancetre(t, x, y):
        return subprocess.run(["git", "merge-base", "--is-ancestor", x, y], cwd=t, env=dict(os.environ, **ENV_GIT),
                              capture_output=True).returncode == 0

    def branches(t):
        return git(t, "branch", "--list", "nuit/*", "--format=%(refname:short)").split()

    def roles(lignes, code):
        """Les rôles des sessions du chantier `code`, dans l'ordre du carnet."""
        return [d["role"] for d in lignes if d["chantier"] == code and carnet.est_session(d)]

    def gardes(lignes, code):
        """Les gardes des lignes du chantier `code` qui ne sont pas des sessions (sans `role`)."""
        return [d["garde"] for d in lignes if d["chantier"] == code and d["role"] is None and d["note"] is None]

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "BBB", "CCC"))
        code, s, lignes = canal(t, hors)
        brs = [br(c) for c in ("AAA", "BBB", "CCC")]
        sujets = git(t, "log", "--format=%s", brs[2]).splitlines()
        clore = [d for d in lignes if d["role"] == "clore"]
        lues = [bool(re.search(r"\*\*Session\*\*[^\n]*%s[^\n]*\(clore\)" % d["session"],
                               git(t, "show", "%s:%s.md" % (b, d["chantier"])))) for d, b in zip(clore, brs)]
        envs = journal_de(os.path.join(hors, "env.jsonl"))
        neuf("(a) trois chantiers réussis : trois branches à la --date, chacune ancêtre de la suivante, trois sessions "
             "clore dont la ligne `**Session** … (clore)` est commitée, trois commits « ouvert (nuit) », VLP_NUIT=1 "
             "et VLP_CANAL=A vus par les 18 sessions du faux, plugin_retard = la carte (aucune ligne : null)",
             code == 0 and "ARRÊT plan terminé — 3 clos, 0 de côté, 0 sautés" in s and branches(t) == brs
             and len({sha(t, b) for b in brs}) == 3 and ancetre(t, brs[0], brs[1]) and ancetre(t, brs[1], brs[2])
             and [d["chantier"] for d in clore] == ["AAA", "BBB", "CCC"] and all(lues)
             and sum(bool(re.fullmatch(r"Chantier (AAA|BBB|CCC) ouvert \(nuit\) : 2 fiches", x)) for x in sujets) == 3
             and len(envs) == 18 and all(e["VLP_NUIT"] == "1" and e["VLP_CANAL"] == "A" for e in envs)
             and all(d["plugin_retard"] is None for d in lignes), (s, lignes, lues, envs))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        journal = os.path.join(hors, "sans-nuit.jsonl")
        with pilote(VLP_FAUX_ENV=journal):
            code, s, cases = boucle(t, FAUX_CLAUDE, 1)
        envs = journal_de(journal)
        neuf("(a) sans --nuit : VLP_NUIT absent de l'environnement du faux", code == 0 and len(envs) == 1
             and envs[0]["VLP_NUIT"] is None and envs[0]["VLP_CANAL"] is None, (s, envs))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "BBB", "CCC"))
        depart = sha(t, "HEAD")
        code, s, lignes = canal(t, hors, VLP_FAUX_REFUSE="AAA1:fiche")
        saute = [d for d in lignes if d["chantier"] == "BBB"]
        neuf("(b) AAA1 refusée (cause fiche) : WIP sur sa branche, BBB qui en dépend sauté sans session, CCC part de la "
             "base et non du WIP, chaque étape au carnet",
             code == 0 and "ARRÊT plan terminé — 1 clos, 1 de côté, 1 sautés" in s
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : AAA1 refusée à la relecture")
             and "SAUTÉ BBB — dépend de AAA" in s and branches(t) == [br("AAA"), br("CCC")]
             and len(saute) == 1 and saute[0]["role"] is None and saute[0]["issue"] == "pas partie"
             and saute[0]["garde"] == "saute:AAA"
             and git(t, "merge-base", br("AAA"), br("CCC")).strip() == depart
             and not ancetre(t, br("AAA"), br("CCC"))
             and roles(lignes, "AAA") == ["découper", "jouer", "relire"]
             and [g.split(":")[0] for g in gardes(lignes, "AAA")] == ["cause-fiche", "mis-de-cote"]
             and roles(lignes, "CCC") == ["découper", "jouer", "relire", "jouer", "relire", "clore"]
             and gardes(lignes, "CCC") == [], (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"))
        code, s, lignes = canal(t, hors, VLP_FAUX_CLOT="AAA1")
        hors_role = [d for d in lignes if d["garde"] == "cloture-hors-role"]
        neuf("(c) une session de jeu qui clôt le chantier (AAA1) : carnet cloture-hors-role, WIP sur sa branche, pas de "
             "session clore, CCC joué ensuite",
             code == 0 and len(hors_role) == 1 and hors_role[0]["chantier"] == "AAA" and hors_role[0]["fiche"] == "AAA1"
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : AAA1 a clos le chantier") and "CLORE AAA" not in s
             and "clore" not in roles(lignes, "AAA") and "CLOS CCC" in s
             and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"), couts=("~0,5 fiche", "~2 fiches", "1 fiche"))
        code, s, lignes = canal(t, hors)
        neuf("(d) AAA à ~0,5 fiche, le faux en écrit 2 : mis de côté sans jouer ni commit « ouvert », CCC joué",
             code == 0 and "plus de 2 × 0.5" in s and "JOUE AAA" not in s and roles(lignes, "AAA") == ["découper"]
             and not any(x.startswith("Chantier AAA ouvert") for x in git(t, "log", "--all", "--format=%s").splitlines())
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : 2 fiches : plus de 2 × 0.5")
             and "CLOS CCC" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"))
        depart = sha(t, "HEAD")
        code, s, lignes = canal(t, hors, VLP_FAUX_VIDE="AAA")
        neuf("(d) découpage vide : mis de côté sans WIP (arbre propre), la branche reste à la base, CCC joué",
             code == 0 and "le découpage n'a ouvert aucun chantier" in s and sha(t, br("AAA")) == depart
             and not any(x.startswith("WIP") for x in git(t, "log", "--all", "--format=%s").splitlines())
             and roles(lignes, "AAA") == ["découper"] and "CLOS CCC" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "BBB", "CCC"))
        hooks = os.path.join(hors, "hooks")
        ecrire_f(os.path.join(hooks, "pre-commit"),
                 "#!/bin/sh\nif git diff --cached --name-only | grep -qx CASSE; then exit 1; fi\nexit 0\n")
        os.chmod(os.path.join(hooks, "pre-commit"), 0o755)
        git(t, "config", "core.hooksPath", hooks.replace("\\", "/"))
        code, s, lignes = canal(t, hors, VLP_FAUX_REFUSE="AAA1:fiche", VLP_FAUX_CASSE="AAA1")
        neuf("(e) cas b sous un pre-commit qui refuse CASSE : ARRÊT, HEAD et arbre intacts, carnet wip-refuse, "
             "ni BBB sauté ni CCC joué",
             code == 1 and "ARRÊT AAA : commit WIP refusé" in s and sujet(t, "HEAD") == "Chantier AAA ouvert (nuit) : 2 fiches"
             and os.path.exists(os.path.join(t, "CASSE")) and git(t, "status", "--porcelain").strip() != ""
             and gardes(lignes, "AAA")[-1] == "wip-refuse" and "SAUTÉ" not in s and "CHANTIER CCC" not in s
             and branches(t) == [br("AAA")], (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"), borne_chantiers=1)
        code, s, lignes = canal(t, hors)
        neuf("(f) la borne du plan est celle de la nuit : un chantier de borne 1, puis ARRÊT borne atteinte, sort 0",
             code == 0 and "borne 5.0 $ · 1 chantiers" in s and "CLOS AAA" in s and "CHANTIER CCC" not in s
             and "ARRÊT borne atteinte" in s and roles(lignes, "CCC") == [], (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA", "CCC"))
        chemin = os.path.join(t, "ctx", "08-etat.md")
        ecrire_f(chemin, lire(chemin).replace("| 3 | `CCC` — c | x | ~2 fiches | — |", "| 3 | `CCC` — c | x | ~2 fiches | — | en trop |"))
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", "TODO cassée")
        code, s, lignes = canal(t, hors)
        neuf("(g) une barre verticale dans la TODO (ValueError) : chaque chantier mis de côté, aucune session, arbre propre",
             code == 0 and s.count("TODO illisible") == 2 and "JOUE" not in s and "DÉCOUPER" not in s
             and not any(carnet.est_session(d) for d in lignes) and git(t, "status", "--porcelain").strip() == ""
             and "ARRÊT plan terminé — 0 clos, 2 de côté, 0 sautés" in s, (s, lignes))

    with tempfile.TemporaryDirectory() as t:
        depot(t)
        code, s = nuit(t, "--canal", "A", "--date", DATE)
        neuf("(h) un chantier déjà ouvert au départ : ARRÊT, rien joué, sort 1",
             code == 1 and "ARRÊT un chantier est déjà ouvert au départ (fiches.md)" in s and "JOUE" not in s
             and cases_de(t) == "...", s)
        code, s = nuit(t, "--canal", "A", "--date", "2026-13-45")
        neuf("(h) --date qui n'est pas une date : refusée (code 2)", code == 2 and "AAAA-MM-JJ attendu" in s, s)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, None)
        code, s, lignes = canal(t, hors)
        neuf("(i) sans plan à la date : ARRÊT plan illisible, sort 1, aucune session",
             code == 1 and "ARRÊT plan illisible — GARDE: pas de fichier des nuits" in s
             and not any(carnet.est_session(d) for d in lignes), (s, lignes))

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot_canal(t, hors, ("AAA",))
        vrai = bmod.vlp

        def avec_retard(argv, dossier):
            """La carte du dépôt de test n'a pas de PLUGIN_RETARD (il compare au kit, pas au dépôt) : on la lui prête."""
            rendu, texte = vrai(argv, dossier)
            fin = "PLUGIN_RETARD=8 commit(s) de code du plugin absents du plugin chargé\n" if argv[0] == "carte" else ""
            return rendu, texte + fin

        sortie = io.StringIO()
        bmod.vlp = avec_retard
        try:
            with pilote(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_CLORE="commit", PYTHONIOENCODING="utf-8",
                        **ENV_GIT), contextlib.redirect_stdout(sortie):
                code = bmod.main([t, "--claude", FAUX_CLAUDE, "--traces", hors, "--nuit", "--canal", "A", "--date", DATE])
        finally:
            bmod.vlp = vrai
        lignes = [d for d in carnet_du(t) if carnet.est_session(d)]   # NUI8 : notes `depart` et `base` hors tri
        neuf("(j) la carte dit PLUGIN_RETARD=8 : les six lignes de session du carnet portent plugin_retard 8",
             code == 0 and "plan terminé — 1 clos" in sortie.getvalue() and len(lignes) == 6
             and all(d["plugin_retard"] == 8 for d in lignes), (sortie.getvalue(), lignes))

    sys.stderr.write("NUI7 : %d cas neufs passés / %d écrits\n" % (ecrits[0], ecrits[0]))
    return dict(DATE=DATE, ecrire_f=ecrire_f, depot_canal=depot_canal, carnet_du=carnet_du, canal=canal, br=br, sha=sha,
                sujet=sujet, ancetre=ancetre, branches=branches, roles=roles)


aides_canal = tester_canal()


# --- reprendre une nuit coupée (NUI8) ---------------------------------------------------------------------
# Chaque cas pose son projet, son dépôt, son carnet et son `~` (HOME, USERPROFILE) dans des dossiers jetés.

def tester_reprise(aides):
    DATE, canal, depot_canal, carnet_du = aides["DATE"], aides["canal"], aides["depot_canal"], aides["carnet_du"]
    br, sha, sujet, branches, roles = aides["br"], aides["sha"], aides["sujet"], aides["branches"], aides["roles"]
    ecrire_f, ancetre = aides["ecrire_f"], aides["ancetre"]
    ecrits, sautes = [0], [0]
    plafonds = bmod.plafonds()
    SID = "00000000-0000-4000-8000-00000000000a"

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI8 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI8 " + nom, cond, sortie)

    def mesure_cli(h, sid):
        """`mesure-tokens.py <id>` lancé par le test sous le `~` de `h` : (tours, usd) de sa ligne."""
        r = subprocess.run([sys.executable, os.path.join(ICI, "mesure-tokens.py"), sid], capture_output=True, text=True,
                           encoding="utf-8", env=dict(os.environ, HOME=h, USERPROFILE=h, PYTHONIOENCODING="utf-8"))
        tete, valeurs = (r.stdout.splitlines() + ["", ""])[:2]
        d = dict(zip(tete.split("\t"), valeurs.split("\t")))
        return int(d.get("tours") or -1), float(d.get("usd") or -1)

    def session_de(lignes, role, fiche=None):
        """La première ligne de session du rôle (et de la fiche), ou None."""
        return next((d for d in lignes if carnet.est_session(d) and d["role"] == role
                     and (fiche is None or d["fiche"] == fiche)), None)

    def reprendre(t, hors, h, *options, **env):
        """boucle.py --nuit --canal A --reprendre --carnet <celui de DATE> dans `t` : (code, sortie, lignes du carnet)."""
        env.setdefault("VLP_FAUX_CLORE", "commit")
        chemin = carnet.du_jour(t, DATE)
        assert chemin
        code, s = nuit(t, "--canal", "A", "--reprendre", "--carnet", chemin, *options, traces=hors, HOME=h, USERPROFILE=h, **env)
        return code, s, carnet_du(t)

    # (a) un jeu coupé : mesuré dans sa transcription, chantier de côté, la fiche suivante pas jouée -----------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        depart = sha(t, "HEAD")
        code, s, lignes = canal(t, hors, VLP_FAUX_COUPE="AAA1", HOME=h, USERPROFILE=h)
        j = session_de(lignes, "jouer", "AAA1")
        tours, usd = mesure_cli(h, j["session"]) if j else (None, None)
        neuf("(a) --nuit, AAA1 en COUPE : issue coupure, usd_cli null, usd_kit et tours_kit égaux à mesure-tokens.py (tours 2), "
             "pot = usd_kit, chantier mis de côté (WIP), AAA2 pas jouée, CCC joué",
             code == 0 and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s and j is not None
             and j["issue"] == "coupure" and j["usd_cli"] is None and j["tours_cli"] is None
             and tours == 2 and j["tours_kit"] == tours and j["usd_kit"] == usd and carnet.pot([j], plafonds) == usd
             and roles(lignes, "AAA") == ["découper", "jouer"] and "JOUE AAA2" not in s and "MIS DE CÔTÉ AAA" in s
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : AAA1 : session de jeu coupée")
             and "CLOS CCC" in s, (s, lignes, tours, usd))
        departs = [(i, d) for i, d in enumerate(lignes) if (d["note"] or "").startswith("depart ")]
        neuf("(a) chaque session a, avant sa ligne, une note `depart <rôle>` au même id, hors `est_session` (role null), "
             "et la note `base` du canal porte HEAD de départ",
             len(departs) == sum(carnet.est_session(d) for d in lignes) and all(d["role"] is None for _, d in departs)
             and all(any(x["note"] == "depart %s" % d["role"] and x["session"] == d["session"] for x in lignes[:i])
                     for i, d in enumerate(lignes) if carnet.est_session(d))
             and [d["note"] for d in lignes if (d["note"] or "").startswith("base ")] == ["base " + depart], (lignes, depart))

    # (b) la même coupure sans transcription : la garde le dit, le pot compte le plafond du rôle -------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        code, s, lignes = canal(t, hors, "--borne-usd", "4.5", VLP_FAUX_COUPE="AAA1", VLP_FAUX_SANS_TRANSCRIPTION="1",
                                HOME=h, USERPROFILE=h)
        j = session_de(lignes, "jouer", "AAA1")
        neuf("(b) COUPE sans transcription : garde « transcription introuvable », usd_kit et tours_kit null (pas 0), "
             "pot = le --max-budget-usd du rôle jouer — et la borne de 4.5 $ tient CCC à l'écart",
             code == 0 and j is not None and j["issue"] == "coupure" and j["usd_kit"] is None and j["tours_kit"] is None
             and j["usd_cli"] is None and "transcription introuvable" in str(j["garde"])
             and carnet.pot([j], plafonds) == bmod.ROLES["jouer"]["usd"]
             and "ARRÊT borne atteinte — pot 5.0100 $ ≥ borne 4.5000 $" in s and "CHANTIER CCC" not in s, (s, lignes))

    # (c) le code de sortie ne décide pas de l'issue ---------------------------------------------------------------
    issues = []
    for sortie in ("143", "1"):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
            depot_canal(t, hors, ("AAA",))
            code, s, lignes = canal(t, hors, VLP_FAUX_COUPE="AAA1=" + sortie, HOME=h, USERPROFILE=h)
            j = session_de(lignes, "jouer", "AAA1")
            issues.append((code, j["issue"] if j else None, j["usd_cli"] if j else 0))
    neuf("(c) COUPE sortie 143, puis sortie 1 : la même issue `coupure` les deux fois", issues == [(0, "coupure", None)] * 2, issues)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as h:
        projet(t)
        sid = "11111111-2222-3333-4444-555555555555"
        def transcriptions():
            return glob.glob(os.path.join(glob.escape(h), ".claude", "projects", "*", sid + ".jsonl"))

        code, l, e = faux(["-p", "/vlp:tache F9", "--session-id", sid, "--model", SONNET], t, VLP_FAUX_COUPE="F9=143",
                          VLP_FAUX_RATE="F9", HOME=h, USERPROFILE=h)
        ecrites = [json.loads(x) for f in transcriptions() for x in lire(f).splitlines()]
        neuf("(c) faux, COUPE=F9=143 : sort 143, init puis rien (aucun result), transcription de deux lignes assistant à "
             "message.id distincts, message.model celui de --model, usage à la forme d'un vrai transcript",
             code == 143 and [x["type"] for x in l] == ["system"] and len(ecrites) == 2
             and len({x["message"]["id"] for x in ecrites}) == 2 and all(x["message"]["model"] == SONNET for x in ecrites)
             and all(set(x["message"]["usage"]) >= {"input_tokens", "output_tokens", "cache_creation_input_tokens",
                                                    "cache_read_input_tokens", "cache_creation"} for x in ecrites), (code, l, e, ecrites))
        for f in transcriptions():
            os.remove(f)
        code, l, e = faux(["-p", "/vlp:tache F9", "--session-id", sid], t, VLP_FAUX_COUPE="F9", VLP_FAUX_RATE="F9",
                          VLP_FAUX_SANS_TRANSCRIPTION="1", HOME=h, USERPROFILE=h)
        neuf("(c) faux, COUPE=F9 : sort 1 par défaut ; SANS_TRANSCRIPTION n'écrit rien ; une autre fiche n'est pas coupée",
             code == 1 and not transcriptions()
             and faux(["-p", "/vlp:tache F9"], t, VLP_FAUX_COUPE="F8", VLP_FAUX_RATE="F9", HOME=h, USERPROFILE=h)[0] == 0,
             (code, l, e))

    # (d) un depart sans fin, la branche créée, l'arbre sale : --reprendre -------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        chemin = carnet.du_jour(t, DATE)
        assert chemin
        depart = sha(t, "HEAD")
        carnet.noter(chemin, "A", "base " + depart)
        carnet.ajouter(chemin, nuit=DATE, canal="A", chantier="AAA", fiche="AAA1", note="depart jouer", session=SID)
        git(t, "switch", "-q", "-c", br("AAA"))
        ecrire_f(os.path.join(t, "sale.txt"), "travail non commité\n")
        with pilote(HOME=h, USERPROFILE=h):
            _faux.transcription(SID, SONNET)
        tours, usd = mesure_cli(h, SID)
        code, s, lignes = reprendre(t, hors, h)
        coupures = [d for d in lignes if d["issue"] == "coupure"]
        neuf("(d) un depart sans fin, branche créée, arbre sale → --reprendre : une ligne coupure (coût relu dans la "
             "transcription), commit WIP du travail non commité, le chantier suivant joué",
             code == 0 and "REPRISE canal A · 1 sessions coupées · en cours : AAA" in s and len(coupures) == 1
             and coupures[0]["session"] == SID and coupures[0]["role"] == "jouer" and coupures[0]["fiche"] == "AAA1"
             and coupures[0]["chantier"] == "AAA" and coupures[0]["usd_cli"] is None and coupures[0]["tours_kit"] == tours == 2
             and coupures[0]["usd_kit"] == usd and "reprise : session sans fin" in str(coupures[0]["garde"])
             and "MIS DE CÔTÉ AAA — une session a été coupée" in s and "JOUE AAA" not in s
             and sujet(t, br("AAA")).startswith("WIP AAA mis de côté : une session a été coupée")
             and "sale.txt" in git(t, "show", "--name-only", "--format=", br("AAA"))
             and branches(t) == [br("AAA"), br("CCC")] and git(t, "merge-base", br("AAA"), br("CCC")).strip() == depart
             and roles(lignes, "CCC") == ["découper", "jouer", "relire", "jouer", "relire", "clore"]
             and "CLOS CCC" in s and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s, (s, lignes))
        avant = (lire(chemin), branches(t), sha(t, "HEAD"))
        code, s, lignes = reprendre(t, hors, h)
        neuf("(d) 2e --reprendre : carnet, branches nuit/* et HEAD identiques avant et après, aucune ligne JOUE, rien à reprendre",
             code == 0 and (lire(chemin), branches(t), sha(t, "HEAD")) == avant and "JOUE" not in s
             and "REPRISE canal A · 0 sessions coupées · en cours : aucun" in s
             and "ARRÊT plan terminé — 1 clos, 1 de côté, 0 sautés" in s, (s, avant))

    # (d) un chantier découpé, arrêté entre deux fiches, l'arbre propre : il reprend dans sa branche -----------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
        depot_canal(t, hors, ("AAA", "CCC"))
        code1, s1, l1 = canal(t, hors, "--plafond", "1", HOME=h, USERPROFILE=h)
        pointe = sha(t, br("AAA"))
        code, s, lignes = reprendre(t, hors, h)
        neuf("(d) chantier découpé, une fiche jouée et commitée, aucune coupure : --reprendre le reprend dans sa branche, "
             "sans repasser par découper (une seule session découper pour AAA), la branche jamais recréée, puis CCC",
             code1 == 0 and "plafond de 1 fiches" in s1 and roles(l1, "AAA") == ["découper", "jouer", "relire"]
             and code == 0 and "REPRISE canal A · 0 sessions coupées · en cours : AAA" in s and "REPRISE AAA" in s
             and roles(lignes, "AAA") == ["découper", "jouer", "relire", "jouer", "relire", "clore"]
             and "CLOS AAA" in s and "CLOS CCC" in s and "DÉCOUPER AAA" not in s
             and branches(t) == [br("AAA"), br("CCC")] and ancetre(t, pointe, br("AAA"))
             and "ARRÊT plan terminé — 2 clos, 0 de côté, 0 sautés" in s, (s1, s, lignes))

    # (g) une relecture coupée, une clôture coupée : le chantier se met de côté ---------------------------------------
    for coupe, genre in (("relire:AAA1", "la relecture a été coupée"), ("clore", "la clôture a été coupée")):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as h:
            depot_canal(t, hors, ("AAA",))
            code, s, lignes = canal(t, hors, VLP_FAUX_COUPE=coupe, HOME=h, USERPROFILE=h)
            role = coupe.split(":")[0]
            j = session_de(lignes, role)
            tours, usd = mesure_cli(h, j["session"]) if j else (None, None)
            neuf("(g) %s en COUPE : issue coupure, usd_kit lu dans la transcription, aucun refus ni relance, chantier "
                 "mis de côté (« %s »)" % (coupe, genre),
                 code == 0 and j is not None and j["issue"] == "coupure" and j["usd_cli"] is None and j["usd_kit"] == usd
                 and j["tours_kit"] == tours == 2 and j["refus_n"] is None and "RELANCE" not in s and genre in s
                 and "MIS DE CÔTÉ AAA" in s and "ARRÊT plan terminé — 0 clos, 1 de côté, 0 sautés" in s, (s, lignes))

    # (e) sans --nuit, rien de la reprise ni de l'éveil ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
        depot(t)
        code, s, cases = boucle(t, FAUX_CLAUDE, 1, options=["--reprendre"])
        neuf("(e) sans --nuit : --reprendre refusé (code 2), aucune ligne ÉVEIL, rien joué",
             code == 2 and "exigent --nuit" in s and "ÉVEIL" not in s and cases == "...", s)
        code, s, cases = boucle(t, FAUX_CLAUDE, 1)
        neuf("(e) sans --nuit, une fiche jouée : aucune ligne ÉVEIL, aucun carnet de nuit",
             code == 0 and cases == "x.." and "ÉVEIL" not in s and not os.path.exists(os.path.join(t, ".git", "vlp-nuit")), s)
        chemin = os.path.join(hors, DATE + ".jsonl")
        refus = [nuit(t, "--canal", "A", "--reprendre"),
                 nuit(t, "--canal", "A", "--reprendre", "--carnet", chemin, "--chantier", "X"),
                 nuit(t, "--canal", "A", "--reprendre", "--carnet", chemin, "--date", DATE),
                 nuit(t, "--canal", "A", "--reprendre", "--carnet", os.path.join(hors, "carnet.jsonl"))]
        neuf("(e) --nuit --reprendre sans --carnet, avec --chantier, avec --date, ou sur un carnet dont le nom n'est pas une "
             "date : refusé (code 2), rien écrit — la date vient du nom du carnet, jamais de l'horloge",
             [c for c, _ in refus] == [2] * 4 and "exige --carnet" in refus[0][1] and "exige --carnet" in refus[1][1]
             and "exige --carnet" in refus[2][1] and "AAAA-MM-JJ attendu" in refus[3][1] and not os.path.exists(chemin), refus)

    # (h) le worktree du canal absent -----------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as nu:
        chemin = os.path.join(hors, DATE + ".jsonl")
        absent = nuit(os.path.join(nu, "absent"), "--canal", "A", "--reprendre", "--carnet", chemin)
        sans_git = nuit(nu, "--canal", "A", "--reprendre", "--carnet", chemin)
        neuf("(h) dossier du canal absent, ou sans Git : GARDE:, sort 1, ni claude lancé ni carnet écrit",
             absent[0] == 1 and absent[1].startswith("GARDE:") and sans_git[0] == 1 and sans_git[1].startswith("GARDE:")
             and "CLAUDE=" not in absent[1] + sans_git[1] and not os.path.exists(chemin), (absent, sans_git))

    # (i) le pot, ligne à ligne, et le coût d'une session coupée sans transcription lisible --------------------------------
    neuf("(i) carnet.cout_de : usd_cli, à défaut usd_kit, à défaut le plafond du rôle, sinon 0 ; un 0.0 est un coût",
         carnet.cout_de({"role": "jouer", "usd_cli": 1.5, "usd_kit": 9}, {"jouer": 5}) == 1.5
         and carnet.cout_de({"role": "jouer", "usd_cli": None, "usd_kit": 0.45}, {"jouer": 5}) == 0.45
         and carnet.cout_de({"role": "jouer", "usd_cli": None, "usd_kit": None}, {"jouer": 5}) == 5
         and carnet.cout_de({"role": "jouer", "usd_cli": 0.0, "usd_kit": None}, {"jouer": 5}) == 0.0
         and carnet.cout_de({"role": "jouer", "usd_cli": None, "usd_kit": None}) == 0
         and carnet.pot([{"role": "jouer", "usd_cli": None, "usd_kit": None, "note": None, "stop": None},
                         {"role": "jouer", "usd_cli": 1, "note": "hors pot", "stop": None}], {"jouer": 5}) == 5
         and set(plafonds) == {"découper", "jouer", "relire", "relance", "clore"}
         and all(plafonds[r] == bmod.ROLES[r]["usd"] for r in bmod.ROLES), plafonds)
    with tempfile.TemporaryDirectory() as h:
        with pilote(HOME=h, USERPROFILE=h):
            _faux.transcription(SID, "claude-inconnu-9")
            hors_grille = bmod.mesure_kit(SID)
            introuvable = bmod.mesure_kit("sans-transcription")
        neuf("(i) mesure_kit : un modèle hors grille rend (None, tours, garde) — jamais 0 ; une session sans transcription "
             "rend (None, None, garde)",
             hors_grille[0] is None and hors_grille[1] == 2 and "modèle hors grille (claude-inconnu-9)" in hors_grille[2]
             and introuvable[:2] == (None, None) and "transcription introuvable" in introuvable[2], (hors_grille, introuvable))

    # (f) l'éveil de la machine : win32 seulement ------------------------------------------------------------------------
    if sys.platform == "win32":
        with tempfile.TemporaryDirectory() as t:
            depot(t)
            code, s = nuit(t, "--canal", "A", "--chantier", "X", "--plafond", "1")
            neuf("(f) win32, --nuit : l'appel réel à SetThreadExecutionState rend un état — ÉVEIL tenu",
                 code == 0 and "ÉVEIL tenu" in s and "ÉVEIL non tenu" not in s, s)
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors:
            depot(t)
            vrai, appels = bmod.appel_eveil, []
            bmod.appel_eveil = lambda drapeaux: appels.append(drapeaux) or 0
            sortie = io.StringIO()
            try:
                with pilote(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), PYTHONIOENCODING="utf-8", **ENV_GIT), \
                        contextlib.redirect_stdout(sortie):
                    code = bmod.main([t, "--claude", FAUX_CLAUDE, "--traces", hors, "--nuit", "--canal", "A",
                                      "--chantier", "X", "--plafond", "1"])
            finally:
                bmod.appel_eveil = vrai
            notes = [d["note"] for d in carnet.lire(carnet_de(t)) if (d["note"] or "").startswith("ÉVEIL")]
            neuf("(f) retour 0 : ÉVEIL non tenu et une note ; ES_CONTINUOUS | ES_SYSTEM_REQUIRED au départ (0x80000001), "
                 "ES_CONTINUOUS à la fin (0x80000000) — les valeurs de la doc Microsoft",
                 code == 0 and "ÉVEIL non tenu" in sortie.getvalue() and "ÉVEIL tenu" not in sortie.getvalue()
                 and len(notes) == 1 and appels == [0x80000001, 0x80000000]
                 and bmod.ES_CONTINUOUS == 0x80000000 and bmod.ES_SYSTEM_REQUIRED == 0x00000001, (sortie.getvalue(), notes, appels))
    else:
        sautes[0] += 2
        sys.stderr.write("SAUTÉ (plateforme) : (f) ÉVEIL tenu et non tenu — sys.platform vaut %s, pas win32\n" % sys.platform)

    sys.stderr.write("NUI8 : %d cas neufs passés / %d écrits · %d cas d'avant passés · %d cas sautés (plateforme)\n"
                     % (ecrits[0], ecrits[0], _PASSES[0] - ecrits[0], sautes[0]))


tester_reprise(aides_canal)


# --- lancer les deux canaux d'une nuit (NUI9) -------------------------------------------------------------
# Chaque cas bâtit projet, dépôt sur `main`, dépôt nu `origin` (poussé une fois), carnet et `~` dans des dossiers jetés.

def tester_lanceur(aides):
    DATE, depot_canal, carnet_du = aides["DATE"], aides["depot_canal"], aides["carnet_du"]
    br, sha, branches, ecrire_f = aides["br"], aides["sha"], aides["branches"], aides["ecrire_f"]
    ecrits = [0]
    SOIR = "RIEN FUSIONNÉ, RIEN POUSSÉ — /vlp:chef le matin"

    def neuf(nom, cond, sortie):
        """Un cas neuf de NUI9 : `verifier` sort au premier écart, donc ceux qui passent = ceux qui sont écrits."""
        ecrits[0] += 1
        verifier("NUI9 " + nom, cond, sortie)

    def projet_lanceur(t, hors, o):
        """Le dépôt de `depot_canal` avec un plan à deux chantiers en A (AAA, BBB) et un en B (CCC), sur `main`, et un
        dépôt nu `origin` poussé une fois."""
        depot_canal(t, hors, ("AAA", "BBB"), codes_b=("CCC",))
        git(t, "branch", "-M", "main")
        subprocess.run(["git", "init", "-q", "--bare", o], check=True, capture_output=True)
        git(t, "remote", "add", "origin", o)
        git(t, "push", "-q", "origin", "main")

    def lance(t, *options, claude: Any = FAUX_CLAUDE, base=None, **env):
        """boucle.py --nuit --lancer --date DATE dans `t` : (code, sortie). Sans --traces : celles des canaux vont au carnet."""
        env_ = dict(base) if base is not None else {k: v for k, v in os.environ.items()
                                                    if k not in (carnet.ENV_CARNET, carnet.ENV_CANAL)}
        env_.update(ENV_GIT)
        env_.update(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_CLORE="commit", PYTHONIOENCODING="utf-8")
        env_.update(env)
        argv = [sys.executable, os.path.join(ICI, "boucle.py"), t, "--nuit", "--lancer", "--date", DATE]
        r = subprocess.run(argv + (["--claude", claude] if claude else []) + list(options), env=env_,
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout + r.stderr

    def chemin_carnet(t):
        chemin = carnet.du_jour(t, DATE)
        assert chemin
        return chemin

    def octets(chemin):
        with open(chemin, "rb") as h:
            return h.read()

    def worktrees(t):
        return git(t, "worktree", "list").splitlines()

    def exclu(t):
        """Le texte de `info/exclude` du dépôt, ou ''."""
        chemin = os.path.join(t, ".git", "info", "exclude")
        return octets(chemin).decode("utf-8", "replace") if os.path.isfile(chemin) else ""

    def rien_cree(t):
        """Aucun worktree, aucun dossier `.claude/worktrees`, rien dans le dossier du carnet, `info/exclude` sans la ligne."""
        return (len(worktrees(t)) == 1 and not os.path.exists(os.path.join(t, ".claude", "worktrees"))
                and not glob.glob(os.path.join(os.path.dirname(chemin_carnet(t)), "*")) and ".claude/worktrees" not in exclu(t))

    # (a) la nuit lancée : deux canaux en parallèle, rien fusionné, rien poussé ---------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o:
        projet_lanceur(t, hors, o)
        avant = (sha(t, "main"), git(t, "ls-remote", "origin"))
        code, s = lance(t, VLP_FAUX_DORT="1")
        lignes = s.splitlines()

        def rang(debut):
            return next((i for i, l in enumerate(lignes) if l.startswith(debut)), -1)
        dep_a, dep_b, fin_a, fin_b, ligne_b = (rang(x) for x in ("DÉPART A · pid ", "DÉPART B · pid ", "FIN A · code ", "FIN B · code ", "[B] "))
        neuf("(a) --lancer, A : AAA et BBB, B : CCC, VLP_FAUX_DORT=1 : DÉPART A et DÉPART B avant toute ligne FIN ; des lignes "
             "[B] et FIN B avant FIN A, des lignes [A] après FIN B ; FIN code 0 des deux, dernière ligne « RIEN FUSIONNÉ, RIEN "
             "POUSSÉ », sort 0",
             code == 0 and min(dep_a, dep_b, fin_a, fin_b, ligne_b) >= 0 and max(dep_a, dep_b) < min(fin_a, fin_b)
             and ligne_b < fin_b < fin_a and any(l.startswith("[A] ") for l in lignes[fin_b:])
             and lignes[fin_a].startswith("FIN A · code 0") and lignes[fin_b].startswith("FIN B · code 0") and lignes[-1] == SOIR, s)
        carnets = glob.glob(os.path.join(os.path.dirname(chemin_carnet(t)), "*.jsonl"))
        ligs = carnet_du(t)
        liste = "\n".join(worktrees(t))
        neuf("(a) git worktree list porte nuit-<date>-A et -B ; un seul carnet, des lignes des canaux A et B (A : AAA et BBB, "
             "B : CCC) ; les trois chantiers ont leur branche ; sha de main et ls-remote origin identiques ; git status "
             "--porcelain vide ; .gitignore absent, la ligne .claude/worktrees/ dans info/exclude",
             len(worktrees(t)) == 3 and "nuit-%s-A" % DATE in liste and "nuit-%s-B" % DATE in liste and len(carnets) == 1
             and {(d["canal"], d["chantier"]) for d in ligs if carnet.est_session(d)} == {("A", "AAA"), ("A", "BBB"), ("B", "CCC")}
             and sorted(branches(t)) == [br("AAA"), br("BBB"), "nuit/%s-B-CCC" % DATE]
             and (sha(t, "main"), git(t, "ls-remote", "origin")) == avant and git(t, "status", "--porcelain").strip() == ""
             and not os.path.exists(os.path.join(t, ".gitignore")) and ".claude/worktrees/" in exclu(t).splitlines(),
             (liste, carnets, branches(t), git(t, "status", "--porcelain"), exclu(t)))
        dossier_carnet = os.path.dirname(chemin_carnet(t))
        neuf("(a) les traces des deux canaux vont dans le dossier du carnet (hors Git), une par canal, non vides",
             all(os.listdir(os.path.join(dossier_carnet, "traces-%s-%s" % (DATE, c))) for c in "AB"), os.listdir(dossier_carnet))

        # (b) relancé à la même date : un worktree de nuit existe déjà ; sans eux, ce sont les branches -----------------
        avant_b = (octets(chemin_carnet(t)), worktrees(t), branches(t))
        code, s = lance(t)
        neuf("(b) relancé à la même date : GARDE sur le worktree existant, sort 1, aucun DÉPART, aucun worktree de plus, "
             "carnet et branches inchangés",
             code == 1 and "GARDE: un worktree de nuit existe déjà" in s and "DÉPART" not in s
             and (octets(chemin_carnet(t)), worktrees(t), branches(t)) == avant_b, s)
        for ligne in worktrees(t)[1:]:
            git(t, "worktree", "remove", "--force", ligne.split()[0])
        code, s = lance(t)
        neuf("(b) les worktrees retirés, les branches restent : GARDE sur la branche existante, sort 1, aucun worktree",
             code == 1 and "GARDE: une branche de cette nuit existe déjà" in s and "DÉPART" not in s and len(worktrees(t)) == 1
             and octets(chemin_carnet(t)) == avant_b[0], s)

    # (c) les gardes du projet : aucun worktree, aucun carnet, rien d'écrit avant la dernière ---------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o:
        projet_lanceur(t, hors, o)
        ecrire_f(os.path.join(t, "ctx", "100-x.md"), "# x modifié, pas commité\n")
        code, s = lance(t)
        neuf("(c) un fichier non commité : GARDE sur l'arbre, sort 1, rien créé",
             code == 1 and s.splitlines()[-1].startswith("GARDE: l'arbre n'est pas propre") and rien_cree(t), s)
        git(t, "checkout", "-q", "--", ".")
        git(t, "switch", "-q", "-c", "autre")
        code, s = lance(t)
        neuf("(c) pas sur main : GARDE sur la branche, sort 1, rien créé",
             code == 1 and "GARDE: la branche courante est autre, pas main" in s and rien_cree(t), s)
        git(t, "switch", "-q", "main")
        code, s = lance(t, "--date", "2026-10-02")
        neuf("(c) pas de plan à la date : GARDE sur le plan, sort 1, rien créé",
             code == 1 and "GARDE: pas de plan utilisable à la date 2026-10-02" in s and rien_cree(t), s)
        nuits = os.path.relpath(glob.glob(os.path.join(t, "ctx", "*-nuits.md"))[0], t).replace("\\", "/")
        ecrire_f(os.path.join(t, ".gitignore"), "ctx/*-nuits.md\n")
        git(t, "rm", "-q", "--cached", nuits)
        git(t, "add", ".gitignore")
        git(t, "commit", "-q", "-m", "le fichier des nuits ignoré")
        code, s = lance(t)
        neuf("(c) fichier des nuits ignoré (.gitignore) : GARDE sur le fichier, sort 1, rien créé",
             code == 1 and "GARDE: le fichier des nuits (%s) est ignoré par Git" % nuits in s and rien_cree(t)
             and git(t, "status", "--porcelain").strip() == "", s)

    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o:
        projet_lanceur(t, hors, o)
        ecrire_f(os.path.join(t, ".gitignore"), ".claude/worktrees/\n")
        git(t, "add", ".gitignore")
        git(t, "commit", "-q", "-m", "worktrees ignorés")
        avant_exclu = exclu(t)
        code, s = lance(t)
        neuf("(c) .claude/worktrees/ déjà ignoré (.gitignore) : la nuit part, info/exclude n'est pas touché, sort 0",
             code == 0 and "FIN A · code 0" in s and "FIN B · code 0" in s and exclu(t) == avant_exclu
             and git(t, "status", "--porcelain").strip() == "", s)

    # (d) claude introuvable : la GARDE d'avant tout le reste ------------------------------------------------------------
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as hors, tempfile.TemporaryDirectory() as o, \
            tempfile.TemporaryDirectory() as vide:
        projet_lanceur(t, hors, o)
        reduit = {k: v for k, v in os.environ.items() if k not in ("VLP_CLAUDE", carnet.ENV_CARNET, carnet.ENV_CANAL)}
        reduit.update(PATH=os.path.dirname(sys.executable), LOCALAPPDATA=vide, APPDATA=vide)
        code, s = lance(t, claude=None, base=reduit)
        neuf("(d) claude introuvable (VLP_CLAUDE ôtée, PATH réduit à Python, LOCALAPPDATA et APPDATA vides) : GARDE: claude "
             "introuvable, sort 1, aucun worktree",
             code == 1 and s.startswith("GARDE: claude introuvable") and rien_cree(t), s)

    # (e) les options : ce qu'argparse refuse -------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as t:
        def argparse_refuse(*options):
            r = subprocess.run([sys.executable, os.path.join(ICI, "boucle.py"), t, *options], capture_output=True, text=True,
                               encoding="utf-8")
            return r.returncode, r.stdout + r.stderr
        code, s = argparse_refuse()
        neuf("(e) sans --lancer ni --nuit, --plafond absent : refusé par argparse (code 2)",
             code == 2 and "--plafond est exigé sans --nuit" in s, s)
        code, s = argparse_refuse("--lancer", "--plafond", "1")
        neuf("(e) --lancer sans --nuit : refusé par argparse (code 2)", code == 2 and "exigent --nuit" in s, s)
        code, s = argparse_refuse("--nuit", "--lancer", "--canal", "A")
        neuf("(e) --nuit --lancer --canal : refusé par argparse (code 2), le lanceur ouvre les deux canaux lui-même",
             code == 2 and "--lancer ouvre les deux canaux" in s, s)

    sys.stderr.write("NUI9 : %d cas neufs passés / %d écrits\n" % (ecrits[0], ecrits[0]))


tester_lanceur(aides_canal)

print("OK")
