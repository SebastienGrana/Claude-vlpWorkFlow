"""Lancer une session `claude -p` de la boucle : rôles, modèles, ligne de commande, trace (REF53).

Sorti de `boucle.py`, qui le ré-exporte et en garde la doc. `BASCULE` et `ROLES` sont des dictionnaires changés
en place — par la boucle comme par les tests — : leur objet est le même dans `boucle.py` et ici.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import uuid
from typing import Any

import carnet

__all__ = ["ICI", "VLP_COEUR", "HERITEES", "AUTORISES", "INTERDITS", "NON_GIT", "PREMIER_PLAN", "OPUS", "SONNET",
    "REPLI_OPUS", "TIMEOUT_S", "REFUS_MAX", "COUPEES", "ROLES", "LIMITE_RE", "RESET_RE", "FIN", "BASCULE", "kit",
    "max_tours", "modele_de", "reset_de", "ligne_carnet", "plafonds", "mesure_kit", "commande", "lire_trace",
    "classer", "jouer", "verifier_nuit", "session_de"
]

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # scripts/boucle_noyau/ → scripts/
VLP_COEUR = os.path.join(ICI, "vlp_coeur.py")    # le code de vlp.py, chargé comme module par `kit()` (VIT5)
# Variables de la session qui lance la boucle : la session fille a les siennes.
HERITEES = ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID")
# En `auto`, `vlp.py` passe déjà ; `git add` et `git commit` sont refusés (essai du bac,
# 2026-09-26). Seuls ces deux-là s'ajoutent : ni push, ni reset, ni checkout, ni clean.
AUTORISES = [outil + "(git %s:*)" % c for outil in ("Bash", "PowerShell") for c in ("add", "commit")]
# Réécrire le commit d'avant, ou sauter le hook : refusés, écrits en tête de commande.
INTERDITS = [outil + "(git commit %s:*)" % o for outil in ("Bash", "PowerShell")
             for o in ("--amend", "--no-verify", "-n")]
# Découper et relire n'écrivent jamais dans Git : `git add` et `git commit` leur restent refusés.
NON_GIT = [outil + "(git %s:*)" % c for outil in ("Bash", "PowerShell") for c in ("add", "commit")]
# Ajoutée au prompt système de toute session (ARP1). 600 000 ms : le timeout le plus long qu'accepte l'outil Bash.
PREMIER_PLAN = ("Session non interactive (claude -p) : rendre la main la termine. Lance chaque commande au premier "
                "plan, jamais en arrière-plan (pas de run_in_background), avec un timeout jusqu'à 600000 ms. "
                "N'attends aucune notification : rien ne te réveillera.")

OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
REPLI_OPUS = "claude-opus-5,claude-sonnet-5-5"   # socle de NUI, « Modèles par rôle » : pointé, pas décidé ici
# 60 min pour tous les rôles : 4,9 × 735 s (TAU1, `context AI/08-etat.md:2378`) et 2 × 29,3 min/fiche
# (BTN, `context AI/92-essai-parallele.md:87`).
TIMEOUT_S = 60 * 60
REFUS_MAX = 2   # refus d'une même fiche au bout desquels la nuit s'arrête (`refus-max`) — seul endroit du nombre
COUPEES = ("timeout", "coupure")   # issues d'une session sans ligne `result` (NUI4, NUI8) : son travail n'est pas à croire

# Les réglages d'une session `--nuit`, un rôle par entrée. `tours` : un entier (non mesuré), ou le fichier
# d'agent dont `lire_max_turns` de vlp.py lit `maxTurns` — jamais recopié. `git` : le rôle commite-t-il.
ROLES = {
    "découper": {
        "prompt": "/vlp:chantier {fiche}", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": None, "git": False,
        "tours": 150,   # non mesuré
        "usd": 20,      # ≈ 3 × 6,60 $ (PAR5, `context AI/08-etat.md:2379`) : plafond haut, ce 6,60 $ compte du hors-fiche
        "timeout": TIMEOUT_S},
    "jouer": {
        "prompt": "/vlp:tache {fiche}", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": "medium", "git": True,
        "tours": "agents/fiche.md",
        "usd": 5,       # ≈ 3,1 × 1,59 $, la fiche la plus chère en medium (entrée « MET4 — xhigh contre medium »)
        "timeout": TIMEOUT_S},
    "relire": {
        # d'après l'essai `--agent` de NUI1 (`context AI/08-etat.md`, section NUI1, essai 5) : le modèle
        # est l'ID demandé, pas le `model: opus` de l'agent ; NUI5 ajoute ` --sha HEAD` au prompt (`suite`)
        "prompt": "{fiche}", "agent": "vlp:relecture", "modele": OPUS, "repli": REPLI_OPUS,
        "effort": None, "git": False,
        "tours": "agents/relecture.md",
        "usd": 3,       # non mesuré
        "timeout": TIMEOUT_S},
    "relance": {
        "prompt": "/vlp:tache {fiche}", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": "xhigh", "git": True,
        "tours": "agents/fiche.md",
        "usd": 8,       # ≈ 2,7 × 2,93 $, la fiche la plus chère en xhigh (entrée « MET4 — xhigh contre medium »)
        "timeout": TIMEOUT_S},
    "clore": {
        # sans fiche, `/vlp:tache` voit `PROCHAINE=aucune` et applique sa clôture (`skills/tache/SKILL.md`, étapes 0 et 7)
        "prompt": "/vlp:tache", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": None, "git": True,   # `cloture.md:72` : la session commite la clôture
        "tours": 60,    # non mesuré
        "usd": 5,       # non mesuré
        "timeout": TIMEOUT_S},
}

# Limite d'usage : forme prise de la doc, https://code.claude.com/docs/en/errors (lue le 2026-10-01 par
# WebFetch, qui résume la page) : « You've hit your session limit · resets 3:45pm », « … weekly limit ·
# resets Mon 12:00am », « … Opus limit · resets 3:45pm » (« Sonnet limit » existe aussi : `stop`).
# Non vérifiée sur le vrai CLI : NUI20 la confirme.
LIMITE_RE = re.compile(r"\s*You've hit your (\w+) limit", re.I)
RESET_RE = re.compile(r"resets\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)\b", re.I)
FIN = float("inf")   # « fin de la nuit » : un reset illisible
BASCULE = {"jusqu": 0.0}   # instant jusqu'où les rôles Opus tournent en SONNET
_KIT: list[Any] = []   # vlp.py chargé comme module, une fois (comme `tests/aides.py` le charge)


def kit():
    """Charger une fois le code de vlp.py (`vlp_coeur.py`) comme module : `VERDICTS`, `git_texte`, `lire_max_turns`."""
    if not _KIT:
        spec = importlib.util.spec_from_file_location("vlp_coeur", VLP_COEUR)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _KIT.append(mod)
    return _KIT[0]


def max_tours(role):
    """`--max-turns` du rôle : l'entier de la table, ou le `maxTurns` de son fichier d'agent."""
    t = ROLES[role]["tours"]
    if isinstance(t, int):
        return t
    n = kit().lire_max_turns(os.path.join(ICI, os.pardir, t))
    if n is None:
        raise ValueError("maxTurns illisible dans %s" % t)
    return n


def modele_de(role):
    """Le modèle du rôle : celui de la table, sauf un rôle Opus pendant une bascule."""
    m = ROLES[role]["modele"]
    return SONNET if m == OPUS and time.time() < BASCULE["jusqu"] else m


def reset_de(texte):
    """L'instant du prochain reset lu dans `texte` (heure locale), ou `FIN` s'il est illisible."""
    m = RESET_RE.search(texte)
    if not m:
        return FIN
    heure = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
    maintenant = time.time()
    an, mois, jour = time.localtime(maintenant)[:3]
    minute = int(m.group(2) or 0)
    cible = time.mktime((an, mois, jour, heure, minute, 0, 0, 0, -1))
    # Demain, même heure : `mktime` sur le jour suivant, pas `+ 86400` — un changement d'heure le décale d'une heure.
    return cible if cible > maintenant else time.mktime((an, mois, jour + 1, heure, minute, 0, 0, 0, -1))


def ligne_carnet(a, **champs):
    """Une ligne du carnet de la nuit : nuit, canal, chantier et `plugin_retard` (celui de la dernière carte lue)
    sont communs à toutes celles de la boucle ; `champs` : le reste."""
    carnet.ajouter(a.carnet, nuit=carnet.nuit_de(a.carnet), canal=a.canal, chantier=a.chantier,
                   plugin_retard=getattr(a, "plugin_retard", None), **champs)


def plafonds():
    """`{rôle: $}` : le `--max-budget-usd` de chaque rôle de `ROLES`, que le pot du carnet compte pour une session
    sans coût mesuré (NUI8) — jamais recopié."""
    return {role: r["usd"] for role, r in ROLES.items()}


def mesure_kit(session):
    """`(usd_kit, tours_kit, garde)` d'une session sans ligne `result`, mesurés dans sa transcription par
    `mesure-tokens.py` (`resoudre` de l'id, puis `mesurer`) : le `usd_exact` en flottant, les tours de la grille.
    Transcription introuvable ou illisible, modèle hors grille : `(None, None, garde)` — jamais 0 —, et le pot
    du carnet compte alors le plafond du rôle."""
    m = kit().mesure()
    chemin, err = m.resoudre(session)
    if chemin is None:
        return None, None, "transcription introuvable pour la session %s — coût non mesuré, le pot compte le plafond du rôle" % session
    r, err = m.mesurer(chemin)
    if r is None:
        return None, None, "transcription illisible (%s) — coût non mesuré, le pot compte le plafond du rôle" % err
    if r["usd_exact"] is None:
        return None, r["tours"], "modèle hors grille (%s) — coût non mesuré, le pot compte le plafond du rôle" % ", ".join(r["inconnus"])
    return float(r["usd_exact"]), r["tours"], None


def commande(claude, role, fiche, a, modele, session, suite=""):
    """La ligne de commande d'une session. Sans `--nuit` : celle d'avant les rôles (REG).
    `suite` : ce qui s'ajoute au prompt du rôle (` --sha HEAD` pour relire)."""
    cmd = [sys.executable, claude] if claude.endswith(".py") else [claude]
    commun = ["--output-format", "stream-json", "--verbose", "--permission-mode", a.permission_mode,
              "--append-system-prompt", PREMIER_PLAN]
    if not a.nuit:  # sans --nuit : la commande d'aujourd'hui, la table ne sert pas
        cmd += ["-p", "/vlp:tache %s" % fiche] + commun
        cmd += ["--allowedTools"] + AUTORISES + ["--disallowedTools"] + INTERDITS
        if a.model:
            cmd += ["--model", a.model]
        if a.effort:
            cmd += ["--effort", a.effort]
        if a.budget:
            cmd += ["--max-budget-usd", a.budget]
        return cmd
    r = ROLES[role]
    cmd += ["-p", r["prompt"].format(fiche=fiche) + suite] + commun
    if r["agent"]:
        cmd += ["--agent", r["agent"]]
    if r["git"]:
        if role != "jouer":     # NUI5 : la boucle commite, après la relecture ; `jouer` n'a ni `git add` ni `git commit`
            cmd += ["--allowedTools"] + AUTORISES
        cmd += ["--disallowedTools"] + INTERDITS
    else:
        cmd += ["--disallowedTools"] + NON_GIT
    cmd += ["--model", modele]
    if r["repli"] and modele == r["modele"]:
        cmd += ["--fallback-model", r["repli"]]
    if r["effort"]:
        cmd += ["--effort", r["effort"]]
    return cmd + ["--max-turns", str(max_tours(role)), "--max-budget-usd", str(r["usd"]),
                  "--session-id", session, "--permission-prompts", "none"]


def lire_trace(trace):
    """Ce que dit la trace : `result`, modèles vus, un message `assistant`, id de session."""
    s: dict[str, Any] = {"result": None, "modeles": [], "assistant": False, "session": None}

    def voir(m):
        if isinstance(m, str) and m not in s["modeles"]:
            s["modeles"].append(m)

    with open(trace, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            try:
                d = json.loads(ligne)
            except ValueError:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("type") == "system" and d.get("subtype") == "init" and s["session"] is None:
                s["session"] = d.get("session_id")
            elif d.get("type") == "assistant":
                s["assistant"] = True
                message = d.get("message")
                voir(message.get("model") if isinstance(message, dict) else None)
            elif d.get("type") == "result":
                s["result"] = d
                usage = d.get("modelUsage")
                for m in usage if isinstance(usage, dict) else ():
                    voir(m)
    return s


def classer(s, ok):
    """L'issue d'une session, dans cet ordre : timeout, coupure, plafond, limite, pas partie, ratée, jouée."""
    r = s["result"]
    if s["timeout"]:
        return "timeout"
    if r is None:
        return "coupure"
    if str(r.get("subtype") or "").startswith("error_max_"):
        return "plafond"
    if LIMITE_RE.match(str(r.get("result") or "")):
        return "limite"
    if r.get("is_error") or not s["assistant"]:
        return "pas partie"
    return "jouée" if ok else "ratée"


def jouer(claude, fiche, racine, a, trace, role="jouer", controle=None, suite="", apres=None, session=None):
    """Joue une session neuve du rôle `role` (sans `--nuit` : toujours le rôle jouer).

    `controle()` dit si le contrôle du rôle passe (jouer : la case est cochée) ; sans, il passe.
    `session` : l'id de son `--session-id`, quand l'appelant l'a déjà écrit (clore) — la première session seule,
    une relance après la limite Opus en prend un neuf.
    `suite` s'ajoute au prompt. `apres(texte, issue, session)` : une fois par session venue au bout — ni
    limite ni pas partie —, avant sa ligne du carnet ; il rend les clés de plus de cette ligne (`refus_n`,
    `cause`, `garde`). Rend un dict : `tours` et `cout` (cumulés si une limite Opus relance), `texte`,
    `issue`, `ok` (rendu de `controle`), `stop` (la raison écrite au carnet, ou None), `session` (celle
    de la dernière), `coupee` (sous `--nuit`, session sans ligne `result` : `apres` n'est pas appelé, la ligne du
    carnet porte `usd_kit` et `tours_kit`). Sous `--nuit`, une note `depart` avant chaque session, une ligne du carnet après.
    """
    env = {k: v for k, v in os.environ.items() if k not in HERITEES}
    if a.nuit:
        env[carnet.ENV_CARNET], env[carnet.ENV_CANAL], env["VLP_NUIT"] = a.carnet, a.canal, "1"
    tours, cout, rejoue = 0, 0.0, False
    while True:
        modele = modele_de(role) if a.nuit else a.model
        demande = session if session and not rejoue else str(uuid.uuid4())
        cmd = commande(claude, role, fiche, a, modele, demande, suite)
        delai = ROLES[role]["timeout"] if a.nuit else None
        if a.nuit:   # avant la session, jamais pendant : sans ligne de session au même id, elle a été coupée (NUI8)
            ligne_carnet(a, fiche=fiche, note="depart %s" % role, session=demande)
        fini, t0 = True, time.time()
        with open(trace, "w", encoding="utf-8") as f:
            try:
                subprocess.run(cmd, cwd=racine, env=env, stdin=subprocess.DEVNULL, stdout=f,
                               stderr=subprocess.STDOUT, timeout=delai)
            except subprocess.TimeoutExpired:
                fini = False
        s = lire_trace(trace)
        s["timeout"] = not fini
        r = s["result"] or {}
        texte = str(r.get("result") or "") if s["result"] else "(aucune ligne result dans la trace)"
        ok = controle() if controle else True
        issue = classer(s, ok)
        tours, cout = tours + (r.get("num_turns") or 0), cout + (r.get("total_cost_usd") or 0.0)
        duree = int(time.time() - t0)
        coupee = a.nuit and issue in COUPEES   # sans ligne `result` : son travail n'est pas à croire (NUI8)
        if a.nuit:
            refus = len(r.get("permission_denials") or [])
            usd_kit, tours_kit, garde_kit = mesure_kit(demande) if coupee else (None, None, None)
            plus = apres(texte, issue, s["session"] or demande) \
                if apres and issue not in ("limite", "pas partie") + COUPEES else {}
            gardes = ["permission_denials : %d" % refus if refus else None, plus.get("garde"), garde_kit]
            ligne_carnet(a, role=role, fiche=fiche, modele_demande=modele, modeles_vus=s["modeles"],
                         tours_cli=r.get("num_turns") if s["result"] else None,
                         usd_cli=r.get("total_cost_usd") if s["result"] else None,
                         usd_kit=usd_kit, tours_kit=tours_kit,
                         duree_s=duree, issue=issue, garde=" ; ".join(g for g in gardes if g) or None,
                         session=s["session"] or demande, **{k: v for k, v in plus.items() if k != "garde"})
        stop = None
        if a.nuit and issue == "limite":
            m = LIMITE_RE.match(texte)
            genre = m.group(1).lower() if m else ""
            if genre == "opus" and not rejoue and ROLES[role]["modele"] == OPUS:
                BASCULE["jusqu"] = reset_de(texte)
                quand = "la fin de la nuit" if BASCULE["jusqu"] == FIN else time.strftime("%H:%M", time.localtime(BASCULE["jusqu"]))
                carnet.noter(a.carnet, a.canal, "bascule Opus → %s jusqu'à %s : %s" % (SONNET, quand, texte))
                rejoue, trace = True, os.path.splitext(trace)[0] + "-2.jsonl"
                continue
            stop = "limite %s — %s" % (genre, texte)
        elif a.nuit and issue == "pas partie":
            stop = "session pas partie — %s" % texte.split("\n")[0]
        if stop:
            carnet.stop(a.carnet, a.canal, stop)
        return {"tours": tours, "cout": cout, "texte": texte, "issue": issue, "ok": ok, "stop": stop,
                "session": s["session"] or demande, "coupee": coupee}


def verifier_nuit(commande, racine):
    """None si la vérification de nuit passe (code 0), sinon la raison, lue par le shell dans `racine`
    et bornée par `TIMEOUT_S`."""
    try:
        r = subprocess.run(commande, cwd=racine, shell=True, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "dépasse le délai de %d s" % TIMEOUT_S
    if r.returncode:
        return "sort %d" % r.returncode
    return None


def session_de(claude, a, racine, traces, etat, role, code, fiche, controle, session=None):
    """Une session d'un rôle hors fiche (découper, clore) : sa trace, ses lignes imprimées, les compteurs de `etat`."""
    trace = os.path.join(traces, "%s-%s.jsonl" % (code, role))
    print("%s %s — trace %s" % (role.upper(), code, trace), flush=True)
    t0 = time.time()
    s = jouer(claude, fiche, racine, a, trace, role=role, controle=controle, session=session)
    etat["tours"] += s["tours"]
    etat["cout"] += s["cout"]
    print("%s %s · tours %d · %.4f $ · %d s" % (role.upper(), code, s["tours"], s["cout"], int(time.time() - t0)))
    for ligne in s["texte"].strip().split("\n"):
        print("    " + ligne)
    print(flush=True)
    return s
