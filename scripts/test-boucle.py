#!/usr/bin/env python3
"""Teste boucle.py avec le faux `claude` de `scripts/faux-claude.py` : aucun appel modèle.

Le faux joue un rôle par prompt (découper, jouer, clore, relire) et rend les lignes
`stream-json` de NUI1 ; ses pilotes `VLP_FAUX_*` sont dans sa docstring. Ce fichier
teste boucle.py avec lui, puis le faux lui-même, rôle par rôle et pilote par pilote.
Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
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

def depot(t):
    """`git init` dans `t`, puis le projet de test : le carnet vit dans son `.git`."""
    subprocess.run(["git", "init", "-q", t], check=True, capture_output=True)
    return projet(t)


def carnet_de(t):
    chemin = carnet.du_jour(t)
    assert chemin, "pas de carnet : %s n'est pas un dépôt Git" % t
    return chemin


def cases_de(t):
    texte = lire(os.path.join(t, "fiches.md"))
    return "".join("x" if ("## %s [x]" % f) in texte else "." for f in ("F1", "F2", "F3"))


def nuit(t, *options, rate="", claude=FAUX_CLAUDE):
    """boucle.py --nuit dans `t` : (code, sortie). VLP_CARNET et VLP_CANAL d'ici ne passent pas."""
    base = {k: v for k, v in os.environ.items() if k not in (carnet.ENV_CARNET, carnet.ENV_CANAL)}
    base.update(VLP_FAUX_VLP=os.path.join(ICI, "vlp.py"), VLP_FAUX_RATE=rate, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ICI, "boucle.py"), t, "--claude", claude, "--traces", t,
                        "--nuit"] + list(options), env=base, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def tester_nuit():
    canal_a = ("--canal", "A", "--chantier", "X")
    with tempfile.TemporaryDirectory() as t:
        depot(t)
        code, s = nuit(t, *canal_a)
        lignes = carnet.lire(carnet_de(t))
        verifier("NUI3 (a) --nuit, 3 fiches : 3 lignes `jouer` aux clés de CLES, canal A, usd_cli du faux, "
                 "usd_kit et tours_kit à null, session lue dans init",
                 code == 0 and cases_de(t) == "xxx" and "ARRÊT aucune fiche à jouer" in s and len(lignes) == 3
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
        lignes = carnet.lire(chemin)
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
        code, s = nuit(t, "--canal", "A")
        verifier("NUI3 : --nuit sans --chantier est refusé (code 2)", code == 2 and "--nuit exige" in s, s)
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
        ligne = carnet.lire(carnet_de(t))[0]
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
                   "jouer": ("/vlp:tache F1", SONNET, None, "low", tours_de("fiche.md"), "5", None, True),
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
        verifier("NUI4 (e) refus de permission et case cochée → jouée sans stop, leur nombre dans garde, 3 fiches",
                 code == 0 and cases_de(t) == "xxx" and [d["issue"] for d in sessions] == ["jouée"] * 3
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
        notes = [d["note"] for d in carnet.lire(carnet_de(t)) if d.get("note")]
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
                 and len([d for d in carnet.lire(carnet_de(t)) if d.get("note")]) == 1, (sessions, argvs))

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

print("OK")
