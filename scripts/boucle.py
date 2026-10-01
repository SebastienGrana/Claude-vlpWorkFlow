#!/usr/bin/env python3
"""La boucle de `/vlp:enchainer clear` : une session `claude -p` neuve par fiche.

Chaque fiche est jouée comme après un `/clear` suivi de `/vlp:tache <fiche>` : un
processus `claude` neuf, sans rien de la fiche d'avant, dans le dossier du projet.
Seul script du kit qui appelle un modèle ; `vlp.py` reste sans appel modèle.

    boucle.py [dossier] --plafond N [--claude C] [--model M] [--effort E]
              [--permission-mode P] [--budget USD] [--traces DOSSIER]
              [--nuit --canal C --chantier X [--borne-usd USD] [--borne-chantiers N] [--carnet CHEMIN]]

Avant chaque fiche : `vlp.py carte` donne `PROCHAINE=` ; `aucune` arrête. Une fiche
à bloc **Tentatives** arrête sans être jouée. Une fiche `(visuel)` (ligne `ARRÊT:`
d'`extraire`) est jouée, puis arrête : `vlp:tache` la livre sans la cocher. Après
chaque fiche, `vlp.py cocher --verifier` : case vide, hors `(visuel)`, arrête.

Imprime `CLAUDE=`, `PROJET=`, puis par fiche `JOUE <fiche> — trace <jsonl>`,
`FICHE <fiche> · CASE [x|  ] · tours <n> · <coût> $ · <s> s` et le texte rendu
par la session, indenté ; enfin `ARRÊT <raison>` et `TOTAL <n> fiches · <tours>
tours · <coût> $ · <s> s`. Sort 0 sur un arrêt prévu (plafond, aucune, visuel),
1 sinon.

`claude` : `--claude`, sinon celui de `vlp.py claude` — la même recherche que `vlp.py bac`
(`VLP_CLAUDE`, le PATH, puis le CLI de l'app sous `Packages`, puis sous `%APPDATA%`).
Un `--claude` en `.py` se lance par ce Python : c'est le faux `claude` des tests.
Permissions : `--permission-mode`, `auto` par défaut — personne ne répond en `-p` —,
plus `git add` et `git commit` (`AUTORISES`), sauf `--amend` et `--no-verify` en tête.
Traces : `--traces`, sinon un dossier temporaire neuf `vlp-boucle-*`, gardé.

`--nuit` (chantier NUI) tient le carnet de `carnet.py` et ouvre `--canal`, `--chantier` (exigés),
`--borne-usd`, `--borne-chantiers` et `--carnet` (absolu ; défaut : celui du jour, fixé au lancement) ;
`--plafond` y devient facultatif, exigé sans `--nuit`. Sans `--nuit` rien de tout cela ne s'applique
et aucun carnet n'est touché. Avant chaque session — jamais pendant —, la boucle relit le carnet :
un `stop` de n'importe quel canal rend `ARRÊT STOP — <raison>` (sort 1) ; la borne atteinte rend
`ARRÊT borne atteinte — <$ ou chantiers>` (sort 0), chantier ouvert. Une session déjà partie va
au bout : la borne se dépasse d'une session par canal au plus. Après chaque session, une ligne du
carnet (nuit, canal, chantier, role, fiche, modele_demande, modeles_vus, tours_cli, usd_cli, duree_s,
issue, garde, session) ; la session fille reçoit `VLP_CARNET` et `VLP_CANAL`.

Sous `--nuit`, chaque session prend ses réglages dans `ROLES`, en tête du fichier : les cinq rôles
(découper, jouer, relire, relance, clore) — prompt, modèle, repli, effort, outils, `--max-turns`,
`--max-budget-usd`, timeout —, la source de chaque plafond en commentaire. Sans `--nuit`, `jouer()` bâtit
la commande d'avant (REG). `main()` joue le rôle jouer, puis relire (NUI5) ; `jouer(…, role=…)` joue les autres,
test-boucle.py le charge comme module, et pour un test `ROLES[<rôle>]["timeout"]` se remplace sur ce module.
Toute session `--nuit` : un `--session-id` neuf, `--permission-prompts none`, le timeout à `subprocess.run`.
Issue de chaque session, dans la ligne du carnet : `timeout`, `coupure` (aucune ligne `result`), `plafond`
(`subtype` `error_max_*`), `limite` (texte du `result`), `pas partie` (`is_error`, ou aucun message
`assistant`), `ratée` (le contrôle du rôle a échoué), `jouée`. `pas partie` et `limite` écrivent une ligne
`stop` : la boucle rend `ARRÊT STOP`, sort 1. Limite « Opus » : les rôles Opus passent à `claude-sonnet-5-5`
jusqu'au reset lu dans le message (illisible : fin de la nuit), une note au carnet, la session relancée une
fois (`BASCULE`) ; « session » ou « weekly » : `stop`. Les `permission_denials` ne classent pas : leur nombre
va au carnet (`garde`).

Relire avant le commit (NUI5, sous `--nuit` seulement) : le rôle jouer n'a ni `git add` ni `git commit`
(`AUTORISES` ne lui va plus ; `INTERDITS` reste). Après sa session, `cocher --verifier` : case cochée sans
`TÊTE`, la session du rôle relire (`relecture <fiche>`, sans `--sha`) ; son premier mot est lu contre
`VERDICTS` de vlp.py, aucun verdict valant `REFUSÉE`. ACCEPTÉE : `cocher --session <relire> --role relire`,
puis `git add -A` et `git commit -m "<fiche> : <titre>"` ; un commit refusé (pre-commit) arrête, sortie 1.
REFUSÉE : `cocher --refuser "<1re ligne du result>"` puis `cocher --session`, l'arbre laissé tel quel ;
`ARRÊT`, sortie 1 ; `relire()` rend à la relance `refus_n`, `cause` (le mot entre le verdict et ` :`,
`aucun-verdict` sans verdict) et `erreur_avant` (la ligne `Erreur :` d'avant). `TÊTE` (la session de jeu a
commité malgré tout) : la relecture part avec ` --sha HEAD` ; REFUSÉE : `git revert --no-edit HEAD` d'abord,
puis les deux `cocher` ; ACCEPTÉE : `cocher --session`, puis un commit de cette ligne seule, sujet
`<fiche> : session de relecture`. La ligne `relire` du carnet porte `refus_n`, `cause` et `garde` (commit
refusé, `TÊTE`) ; le coût du relecteur entre au `TOTAL`.
"""
import argparse
import functools
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any

import carnet

for _flux in (sys.stdout, sys.stderr):
    try:
        if isinstance(_flux, io.TextIOWrapper):
            _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
VLP = os.path.join(ICI, "vlp.py")
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

OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
REPLI_OPUS = "claude-opus-5,claude-sonnet-5-5"   # socle de NUI, « Modèles par rôle » : pointé, pas décidé ici
# 60 min pour tous les rôles : 4,9 × 735 s (TAU1, `context AI/08-etat.md:2378`) et 2 × 29,3 min/fiche
# (BTN, `context AI/92-essai-parallele.md:87`).
TIMEOUT_S = 60 * 60

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
        "prompt": "/vlp:tache {fiche}", "agent": None, "modele": SONNET, "repli": None,
        "effort": "low", "git": True,
        "tours": "agents/fiche.md",
        "usd": 5,       # ≈ 2,9 × 1,74 $ (max de PAR7 en `-p`, `context AI/08-etat.md:2373`)
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
        "effort": "medium", "git": True,
        "tours": "agents/fiche.md",
        "usd": 5,       # comme jouer ; Opus medium jamais mesuré
        "timeout": TIMEOUT_S},
    "clore": {
        "prompt": "/vlp:tache", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,   # prompt : NUI7 le fixe
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
_KIT: list[Any] = []   # vlp.py chargé comme module, une fois (`scripts/test-vlp.py:29`)


def kit():
    """vlp.py chargé comme module, une fois : `VERDICTS`, `git_texte`, `lire_max_turns`."""
    if not _KIT:
        spec = importlib.util.spec_from_file_location("vlp", VLP)
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
    cible = time.mktime((an, mois, jour, heure, int(m.group(2) or 0), 0, 0, 0, -1))
    return cible if cible > maintenant else cible + 86400


def vlp(argv, dossier):
    """Code et sortie de `vlp.py <argv>`, lancé dans `dossier`."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, VLP] + argv, cwd=dossier, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def trouver_claude(choix):
    if choix:
        return choix
    _, s = vlp(["claude"], os.getcwd())
    return s[len("CLAUDE "):].strip() if s.startswith("CLAUDE ") else None


def lire_carte(dossier):
    """(racine, fichier de fiches, prochaine) — None là où la carte ne dit rien."""
    _, s = vlp(["carte", dossier], dossier)
    racine = fichier = prochaine = None
    for ligne in s.split("\n"):
        if ligne.startswith("PROJET="):
            racine = ligne[len("PROJET="):].strip()
        elif ligne.startswith("PROCHAINE="):
            prochaine = ligne[len("PROCHAINE="):].strip()
        elif "**fichier de fiches courant**" in ligne and fichier is None:
            valeur = ligne.split(":", 1)[1].strip()
            valeur = valeur.split(" (")[0].strip().strip("`")
            fichier = None if valeur.lower().startswith("aucun") else valeur
    return racine, fichier, prochaine


def commande(claude, role, fiche, a, modele, session, suite=""):
    """La ligne de commande d'une session. Sans `--nuit` : celle d'avant les rôles (REG).
    `suite` : ce qui s'ajoute au prompt du rôle (` --sha HEAD` pour relire)."""
    cmd = [sys.executable, claude] if claude.endswith(".py") else [claude]
    commun = ["--output-format", "stream-json", "--verbose", "--permission-mode", a.permission_mode]
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


def jouer(claude, fiche, racine, a, trace, role="jouer", controle=None, suite="", apres=None):
    """Joue une session neuve du rôle `role` (sans `--nuit` : toujours le rôle jouer).

    `controle()` dit si le contrôle du rôle passe (jouer : la case est cochée) ; sans, il passe.
    `suite` s'ajoute au prompt. `apres(texte, issue, session)` : une fois par session venue au bout — ni
    limite ni pas partie —, avant sa ligne du carnet ; il rend les clés de plus de cette ligne (`refus_n`,
    `cause`, `garde`). Rend un dict : `tours` et `cout` (cumulés si une limite Opus relance), `texte`,
    `issue`, `ok` (rendu de `controle`), `stop` (la raison écrite au carnet, ou None), `session` (celle
    de la dernière). Sous `--nuit`, une ligne du carnet par session.
    """
    env = {k: v for k, v in os.environ.items() if k not in HERITEES}
    if a.nuit:
        env[carnet.ENV_CARNET], env[carnet.ENV_CANAL] = a.carnet, a.canal
    tours, cout, rejoue = 0, 0.0, False
    while True:
        modele = modele_de(role) if a.nuit else a.model
        demande = str(uuid.uuid4())
        cmd = commande(claude, role, fiche, a, modele, demande, suite)
        delai = ROLES[role]["timeout"] if a.nuit else None
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
        if a.nuit:
            refus = len(r.get("permission_denials") or [])
            plus = apres(texte, issue, s["session"] or demande) if apres and issue not in ("limite", "pas partie") else {}
            gardes = ["permission_denials : %d" % refus if refus else None, plus.get("garde")]
            carnet.ajouter(a.carnet, nuit=carnet.nuit_de(a.carnet), canal=a.canal, chantier=a.chantier,
                           role=role, fiche=fiche, modele_demande=modele, modeles_vus=s["modeles"],
                           tours_cli=r.get("num_turns") if s["result"] else None,
                           usd_cli=r.get("total_cost_usd") if s["result"] else None,
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
                "session": s["session"] or demande}


def etat_case(fichier, fiche, racine):
    """(case cochée, sha de la `TÊTE` ou None) selon `cocher --verifier`."""
    _, verif = vlp(["cocher", fichier, fiche, "--verifier"], racine)
    m = re.search(r"^TÊTE (\S+)", verif, re.M)
    return ("CASE %s [x]" % fiche) in verif, m.group(1) if m else None


def case_cochee(fichier, fiche, racine):
    """Vrai si `cocher --verifier` voit la case de `fiche` cochée."""
    return etat_case(fichier, fiche, racine)[0]


def verdict_de(texte):
    """(verdict, cause) lus dans le `result` de la relecture : le premier mot s'il est dans `VERDICTS`
    (sinon `None` : aucun verdict vaut `REFUSÉE`, `enchainement.md`), et le mot entre `<verdict> — ` et
    ` :` — `aucun-verdict` quand il n'y en a pas de lisible."""
    t = texte.lstrip()
    m = re.match(r"\w+", t)
    mot = m.group(0) if m and m.group(0) in kit().VERDICTS else None
    if mot is None:
        return None, "aucun-verdict"
    c = re.match(re.escape(mot) + r"\s*—\s*(\w+)\s*:", t)
    return mot, c.group(1) if c else "aucun-verdict"


def commiter(racine, sujet, fichier=None):
    """(ok, erreur) : `git add -A` puis `git commit -m <sujet>` ; avec `fichier`, ce fichier seul."""
    git = kit().git_texte
    code, err = git(["add", "--", fichier] if fichier else ["add", "-A"], racine)
    if code == 0:
        code, err = git(["commit", "-q", "-m", sujet] + (["--", fichier] if fichier else []), racine)
    return code == 0, err


def relire(claude, fiche, titre, fichier, racine, a, trace, tete=None):
    """La relecture d'une fiche cochée, sous `--nuit` (chantier NUI) : la session du rôle `relire`, puis
    ce que son verdict commande. `tete` : le sha d'un commit que le jeu a fait lui-même (`--sha HEAD`).
    ACCEPTÉE : la ligne `**Session**` du relecteur, puis le commit (de la fiche ; de cette ligne seule si
    `tete`). REFUSÉE : `git revert` d'abord si `tete`, puis `cocher --refuser` et la ligne `**Session**` ;
    l'arbre reste tel quel. Rend `tours`, `cout`, `stop`, `arret` (la raison d'un arrêt, ou None),
    `verdict`, et pour un refus `refus_n`, `cause`, `erreur_avant` — ce que lira la relance (NUI6)."""
    accepte = kit().VERDICTS[0]
    out: dict[str, Any] = {"verdict": None, "arret": None, "refus_n": None, "cause": None, "erreur_avant": None}

    def suite(texte, issue, session):
        mot, cause = verdict_de(texte)
        out["verdict"], plus = mot, {}
        gardes = ["TÊTE %s : la session de jeu a commité" % tete] if tete else []
        noter = ["cocher", fichier, fiche, "--session", session, "--role", "relire"]
        if mot == accepte:
            code, sortie = vlp(noter, racine)
            if code:
                gardes.append("cocher --session : %s" % sortie.strip())
            ok, err = commiter(racine, "%s : session de relecture" % fiche if tete else "%s : %s" % (fiche, titre),
                               fichier if tete else None)
            if not ok:
                out["arret"] = "%s : commit refusé — %s" % (fiche, err)
                gardes.append(out["arret"])
        else:
            _, ex = vlp(["extraire", fichier, fiche], racine)
            out["erreur_avant"] = next((l for l in ex.splitlines() if l.startswith("Erreur :")), None)
            motif = (texte.strip().splitlines() or [""])[0] or "aucun verdict rendu par le relecteur"
            revert = git_revert(racine) if tete else None
            if revert:
                out["arret"] = "%s : revert impossible — %s" % (fiche, revert)
                gardes.append(out["arret"])
            else:
                _, sortie = vlp(["cocher", fichier, fiche, "--refuser", motif], racine)
                vu = re.search(r"refus (\d+)", sortie)
                out["refus_n"], out["cause"] = int(vu.group(1)) if vu else None, cause
                vlp(noter, racine)
                out["arret"] = "%s refusée à la relecture — refus %s, cause %s" % (fiche, out["refus_n"], cause)
                plus.update(refus_n=out["refus_n"], cause=cause)
        if gardes:
            plus["garde"] = " ; ".join(gardes)
        return plus

    s = jouer(claude, fiche, racine, a, trace, role="relire", suite=" --sha HEAD" if tete else "", apres=suite)
    out.update(tours=s["tours"], cout=s["cout"], stop=s["stop"], texte=s["texte"])
    return out


def git_revert(racine):
    """None si `git revert --no-edit HEAD` passe, sinon sa première ligne d'erreur."""
    code, err = kit().git_texte(["revert", "--no-edit", "HEAD"], racine)
    return None if code == 0 else err


def main(argv):
    p = argparse.ArgumentParser(description="Une session claude -p neuve par fiche.")
    p.add_argument("dossier", nargs="?", default=".")
    p.add_argument("--plafond", type=int)
    p.add_argument("--claude")
    p.add_argument("--model")
    p.add_argument("--effort")
    p.add_argument("--permission-mode", default="auto")
    p.add_argument("--budget")
    p.add_argument("--traces")
    p.add_argument("--nuit", action="store_true")
    p.add_argument("--canal")
    p.add_argument("--chantier")
    p.add_argument("--borne-usd", type=float)
    p.add_argument("--borne-chantiers", type=int)
    p.add_argument("--carnet")
    a = p.parse_args(argv)
    if a.nuit:
        if not a.canal or not a.chantier:
            p.error("--nuit exige --canal et --chantier")
        if a.carnet and not os.path.isabs(a.carnet):
            p.error("--carnet doit être un chemin absolu")
    else:
        if a.plafond is None:
            p.error("--plafond est exigé sans --nuit")
        if a.canal or a.chantier or a.borne_usd is not None or a.borne_chantiers is not None or a.carnet:
            p.error("--canal, --chantier, --borne-usd, --borne-chantiers et --carnet exigent --nuit")

    claude = trouver_claude(a.claude)
    if not claude:
        # Le Python du Store (shebang lu par `py`) voit un AppData virtualisé : ni le
        # dossier ni le `.exe`, même par chemin exact. `py -3` lance le vrai (essai, 2026-09-26).
        print("GARDE: claude introuvable — --claude, VLP_CLAUDE ou le PATH ; sous Windows, "
              "lancer par `py -3` (Python : %s)" % sys.executable)
        return 1
    print("CLAUDE=%s" % claude)
    racine, fichier, _ = lire_carte(os.path.abspath(a.dossier))
    if not racine or not fichier:
        print("ARRÊT aucun projet ou aucun fichier de fiches courant")
        return 1
    print("PROJET=%s · FICHIER=%s" % (racine, fichier))
    if a.nuit:
        a.carnet = a.carnet or carnet.du_jour(racine)
        if not a.carnet:
            print("GARDE: pas de dépôt Git pour le carnet de nuit — --carnet <chemin absolu>")
            return 1
        print("CARNET=%s · CANAL=%s · CHANTIER=%s" % (a.carnet, a.canal, a.chantier))
        try:
            for role in ROLES:
                max_tours(role)
        except ValueError as e:
            print("GARDE: %s" % e)
            return 1
    traces = a.traces or tempfile.mkdtemp(prefix="vlp-boucle-")
    jouees, total_tours, total_cout, t_debut = 0, 0, 0.0, time.time()
    code, raison = 0, "plafond de %d fiches" % a.plafond if a.plafond is not None else "aucun plafond"

    while a.plafond is None or jouees < a.plafond:
        if a.nuit:
            lignes = carnet.lire(a.carnet)
            arret = carnet.stop_de(lignes)
            if arret is not None:
                code, raison = 1, "STOP — %s" % arret
                break
            arret = carnet.borne(lignes, a.chantier, a.borne_usd, a.borne_chantiers)
            if arret is not None:
                raison = "borne atteinte — %s" % arret
                break
        _, _, fiche = lire_carte(racine)
        if not fiche or fiche == "aucune":
            raison = "aucune fiche à jouer"
            break
        _, extrait = vlp(["extraire", fichier, fiche], racine)
        if "**Tentatives**" in extrait:
            code, raison = 1, "%s porte un bloc Tentatives — à lire avant de rejouer" % fiche
            break
        visuel = "ARRÊT:" in extrait
        trace = os.path.join(traces, "%s.jsonl" % fiche)
        print("JOUE %s — trace %s" % (fiche, trace), flush=True)
        t0 = time.time()
        s = jouer(claude, fiche, racine, a, trace, controle=functools.partial(case_cochee, fichier, fiche, racine))
        duree = int(time.time() - t0)
        tours, cout, texte, cochee = s["tours"], s["cout"], s["texte"], s["ok"]
        jouees, total_tours, total_cout = jouees + 1, total_tours + tours, total_cout + cout
        print("FICHE %s · CASE [%s] · tours %d · %.4f $ · %d s"
              % (fiche, "x" if cochee else " ", tours, cout, duree))
        for ligne in texte.strip().split("\n"):
            print("    " + ligne)
        print(flush=True)
        if s["stop"]:
            code, raison = 1, "STOP — %s" % s["stop"]
            break
        if visuel:
            raison = "%s est (visuel) — à regarder" % fiche
            break
        if not cochee:
            code, raison = 1, "%s non cochée — lire sa trace" % fiche
            break
        if a.nuit:
            titre = re.search(r"^## %s \[[ x]\] — (.+?)\s*$" % re.escape(fiche), extrait, re.M)
            tete = etat_case(fichier, fiche, racine)[1]
            r = relire(claude, fiche, titre.group(1) if titre else fiche, fichier, racine, a,
                       os.path.join(traces, "%s-relire.jsonl" % fiche), tete)
            total_tours, total_cout = total_tours + r["tours"], total_cout + r["cout"]
            print("RELIT %s · %s · tours %d · %.4f $" % (fiche, r["verdict"] or "aucun verdict", r["tours"], r["cout"]))
            for ligne in r["texte"].strip().split("\n"):
                print("    " + ligne)
            print(flush=True)
            if r["stop"]:
                code, raison = 1, "STOP — %s" % r["stop"]
                break
            if r["arret"]:
                code, raison = 1, r["arret"]
                break

    print("ARRÊT %s" % raison)
    print("TOTAL %d fiches · %d tours · %.4f $ · %d s"
          % (jouees, total_tours, total_cout, int(time.time() - t_debut)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
