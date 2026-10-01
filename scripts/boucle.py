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
au bout : la borne se dépasse d'une session par canal au plus. Après chaque session, une ligne
`jouer` (nuit, canal, chantier, fiche, tours_cli, usd_cli, duree_s, session) ; la session fille
reçoit `VLP_CARNET` et `VLP_CANAL`.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
import time

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


def jouer(claude, fiche, racine, a, trace):
    """Lance une session neuve sur `/vlp:tache <fiche>`. Rend (tours, coût, texte)."""
    cmd = [sys.executable, claude] if claude.endswith(".py") else [claude]
    cmd += ["-p", "/vlp:tache %s" % fiche, "--output-format", "stream-json", "--verbose",
            "--permission-mode", a.permission_mode,
            "--allowedTools"] + AUTORISES + ["--disallowedTools"] + INTERDITS
    if a.model:
        cmd += ["--model", a.model]
    if a.effort:
        cmd += ["--effort", a.effort]
    if a.budget:
        cmd += ["--max-budget-usd", a.budget]
    env = {k: v for k, v in os.environ.items() if k not in HERITEES}
    if a.nuit:
        env[carnet.ENV_CARNET], env[carnet.ENV_CANAL] = a.carnet, a.canal
    with open(trace, "w", encoding="utf-8") as f:
        subprocess.run(cmd, cwd=racine, env=env, stdin=subprocess.DEVNULL, stdout=f,
                       stderr=subprocess.STDOUT)
    tours, cout, texte = 0, 0.0, "(aucune ligne result dans la trace)"
    with open(trace, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            try:
                d = json.loads(ligne)
            except ValueError:
                continue
            if isinstance(d, dict) and d.get("type") == "result":
                tours = d.get("num_turns") or 0
                cout = d.get("total_cost_usd") or 0.0
                texte = str(d.get("result") or "")
    return tours, cout, texte


def session_de(trace):
    """Le `session_id` de la ligne `system`/`init` de la trace, ou None."""
    with open(trace, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            try:
                d = json.loads(ligne)
            except ValueError:
                continue
            if isinstance(d, dict) and d.get("type") == "system" and d.get("subtype") == "init":
                return d.get("session_id")
    return None


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
        tours, cout, texte = jouer(claude, fiche, racine, a, trace)
        duree = int(time.time() - t0)
        jouees, total_tours, total_cout = jouees + 1, total_tours + tours, total_cout + cout
        if a.nuit:
            carnet.ajouter(a.carnet, nuit=carnet.nuit_de(a.carnet), canal=a.canal, chantier=a.chantier,
                           role="jouer", fiche=fiche, tours_cli=tours, usd_cli=cout, duree_s=duree,
                           session=session_de(trace))
        _, verif = vlp(["cocher", fichier, fiche, "--verifier"], racine)
        cochee = ("CASE %s [x]" % fiche) in verif
        print("FICHE %s · CASE [%s] · tours %d · %.4f $ · %d s"
              % (fiche, "x" if cochee else " ", tours, cout, duree))
        for ligne in texte.strip().split("\n"):
            print("    " + ligne)
        print(flush=True)
        if visuel:
            raison = "%s est (visuel) — à regarder" % fiche
            break
        if not cochee:
            code, raison = 1, "%s non cochée — lire sa trace" % fiche
            break

    print("ARRÊT %s" % raison)
    print("TOTAL %d fiches · %d tours · %.4f $ · %d s"
          % (jouees, total_tours, total_cout, int(time.time() - t_debut)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
