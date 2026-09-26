#!/usr/bin/env python3
"""La boucle de `/vlp:enchainer clear` : une session `claude -p` neuve par fiche.

Chaque fiche est jouée comme après un `/clear` suivi de `/vlp:tache <fiche>` : un
processus `claude` neuf, sans rien de la fiche d'avant, dans le dossier du projet.
Seul script du kit qui appelle un modèle ; `vlp.py` reste sans appel modèle.

    boucle.py [dossier] --plafond N [--claude C] [--model M] [--permission-mode P]
              [--budget USD]

Avant chaque fiche : `vlp.py carte` donne `PROCHAINE=` ; `aucune` arrête. Une fiche
à bloc **Tentatives** arrête sans être jouée. Une fiche `(visuel)` (ligne `ARRÊT:`
d'`extraire`) est jouée, puis arrête : `vlp:tache` la livre sans la cocher. Après
chaque fiche, `vlp.py cocher --verifier` : case vide, hors `(visuel)`, arrête.

Imprime `CLAUDE=`, `PROJET=`, puis par fiche `JOUE <fiche> — trace <jsonl>`,
`FICHE <fiche> · CASE [x|  ] · tours <n> · <coût> $ · <s> s` et le texte rendu
par la session, indenté ; enfin `ARRÊT <raison>` et `TOTAL <n> fiches · <tours>
tours · <coût> $ · <s> s`. Sort 0 sur un arrêt prévu (plafond, aucune, visuel),
1 sinon.

`claude` : `--claude`, sinon `VLP_CLAUDE`, sinon le PATH, sinon le plus récent
`%APPDATA%/Claude/claude-code/*/claude.exe` (le CLI de l'app de bureau Windows).
Un `--claude` en `.py` se lance par ce Python : c'est le faux `claude` des tests.
Permissions : `--permission-mode`, `auto` par défaut — personne ne répond en `-p`.
"""
import argparse
import glob
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

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


def vlp(argv, dossier):
    """Code et sortie de `vlp.py <argv>`, lancé dans `dossier`."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, VLP] + argv, cwd=dossier, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def trouver_claude(choix):
    if choix or os.environ.get("VLP_CLAUDE"):
        return choix or os.environ["VLP_CLAUDE"]
    sur_path = shutil.which("claude")
    if sur_path:
        return sur_path
    appdata = os.environ.get("APPDATA", "")
    trouves = glob.glob(os.path.join(appdata, "Claude", "claude-code", "*", "claude.exe")) if appdata else []

    def version(p):
        nom = os.path.basename(os.path.dirname(p))
        return [int(x) if x.isdigit() else 0 for x in nom.split(".")]
    return max(trouves, key=version) if trouves else None


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
            "--permission-mode", a.permission_mode]
    if a.model:
        cmd += ["--model", a.model]
    if a.budget:
        cmd += ["--max-budget-usd", a.budget]
    env = {k: v for k, v in os.environ.items() if k not in HERITEES}
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


def main(argv):
    p = argparse.ArgumentParser(description="Une session claude -p neuve par fiche.")
    p.add_argument("dossier", nargs="?", default=".")
    p.add_argument("--plafond", type=int, required=True)
    p.add_argument("--claude")
    p.add_argument("--model")
    p.add_argument("--permission-mode", default="auto")
    p.add_argument("--budget")
    a = p.parse_args(argv)

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
    traces = tempfile.mkdtemp(prefix="vlp-boucle-")
    jouees, total_tours, total_cout, t_debut = 0, 0, 0.0, time.time()
    code, raison = 0, "plafond de %d fiches" % a.plafond

    while jouees < a.plafond:
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
