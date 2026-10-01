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

print("OK")
