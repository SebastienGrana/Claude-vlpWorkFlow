#!/usr/bin/env python3
"""MET3 → MET4 : rejouer 3 fiches de code et 1 de conception à `medium`, `high` et `xhigh` (Opus 5.5), un essai à
la fois, et juger chacun. Rebâti sur `vit25.py` (VIT25, série 2), reconstitué du transcript de sa session (`17d950aa`) :
mêmes étapes, même juge.

    met4-juge.py --kit DOSSIER --essais-dir DOSSIER --conception VIT12|REG2 [--essais VIT23:high,…] --borne USD
    met4-juge.py --kit DOSSIER --essais-dir DOSSIER --a-blanc [--essais VIT23:high,…]
    met4-juge.py --kit DOSSIER --essais-dir DOSSIER --a-blanc <fiche>:<branche d'un essai déjà joué>

`--kit` : le dépôt du kit dont on lance vlp.py et boucle.py ; `--essais-dir` : où poser les worktrees d'essai. Les
deux sont exigés : aucun chemin de machine dans le dépôt (EFF2). Le relais les reçoit par `MET4_KIT`.

Par fiche, une fois : la branche de préparation, posée sur le commit d'avant la fiche, plus CHANTIER.md (artefact
« aucun », vérification « le critère de fin ») — celle de VIT25 (`vit25/prep-<fiche>`) si elle existe, sinon
`met4/prep-<fiche>`.
Par essai : `claude auth status` ; un worktree neuf sous `ESSAIS` ; le post-it du chantier (sans lui la carte dit
COURANT=aucun) ; la carte relue (PROCHAINE=<fiche>, sinon arrêt) ; l'essai déclaré par `vlp.py essai`, pour que
`cout` le compte (MET2) ; puis `boucle.py --plafond 1 --model claude-opus-5-5 --effort <niveau> --budget <plafond>`,
la consigne « premier plan » passée par `claude-relais.py` (`--append-system-prompt`).
Le juge : commits, suite entière du worktree, pyright sur les .py touchés, `sante --cliquet`, compte de « verifier( »,
relecteur (rôle relire de boucle.py, --sha HEAD), coût (essai + relecteur).
Une ligne JSON par essai dans met4-resultats.jsonl ; un essai déjà noté ne se rejoue pas.
Arrêt : une limite d'usage, une GARDE, ou la borne en $ (essais + relecteurs) atteinte.

`--a-blanc` seul : la liste des essais qui seraient joués (nom, plafond, commit d'avant, worktree, déjà noté),
sans rien lancer — ni modèle, ni git, ni CLI.
`--a-blanc <fiche>:<branche>` : aucun appel modèle. Tout le chemin d'un essai (connexion, préparation, worktree, post-it, carte, `essai`
présent dans le kit), puis, à la place de la session, les commits d'un essai déjà joué (`git merge --ff-only`), et
le juge sans relecteur. Le worktree et sa branche sont retirés à la fin.
"""
import argparse
import datetime
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from typing import NoReturn

KIT = ""  # --kit, exigé
ESSAIS = ""  # --essais-dir, exigé
ICI = os.path.dirname(os.path.abspath(__file__))
RESULTATS = os.path.join(ICI, "met4-resultats.jsonl")
RELAIS = os.path.join(ICI, "claude-relais.py")
MODELE = "claude-opus-5-5"
VIT, REG = "context AI/102-vitesse.md", "context AI/93-reglages-enchainer.md"
# fiche → (commit d'avant la fiche, plafond $ de l'essai, fichier de fiches). Plafonds : ceux de VIT25 (≈ 2 fois le
# réel à Max) ; 6 $ pour la conception, ≈ 2 fois l'essai `xhigh` le plus cher de la série 2 (VIT20, 3,31 $).
FICHES = {"VIT23": ("0f0edd6", "6", VIT), "VIT20": ("ee0ca8f", "8", VIT), "VIT19": ("2edc69b", "34", VIT),
          "VIT12": ("df288a5", "6", VIT), "REG2": ("196560f", "6", REG)}
CODE = ("VIT23", "VIT20", "VIT19")
NIVEAUX = ("medium", "high", "xhigh")
PY = ["py", "-3"]


def heure():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dire(texte):
    print("[%s] %s" % (heure(), texte), flush=True)


def lancer(cmd, cwd=None, timeout=None):
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1"), timeout=timeout)
    return r.returncode, r.stdout + r.stderr, round(time.time() - t0, 1)


def git(args, cwd):
    return lancer(["git"] + args, cwd=cwd)


def garde(texte) -> NoReturn:
    dire("GARDE: " + texte)
    raise SystemExit(1)


def vlp(args, cwd):
    return lancer(PY + [KIT + "/scripts/vlp.py"] + args, cwd=cwd)


def claude_du_kit():
    _, sortie, _ = vlp(["claude"], KIT)
    morceaux = sortie.strip().split(" ", 1)
    if len(morceaux) != 2 or not morceaux[0].startswith("CLAUDE"):
        garde("vlp.py claude ne rend pas de chemin : %r" % sortie.strip()[-300:])
    return morceaux[1]


def preparer(fiche):
    """La branche de préparation : celle de VIT25 si elle existe, sinon met4/prep-<fiche> ; rend son sha."""
    for branche in ("vit25/prep-" + fiche, "met4/prep-" + fiche):
        code, out, _ = git(["rev-parse", "--verify", "-q", branche], KIT)
        if code == 0:
            dire("PRÉPARATION %s : %s (%s)" % (fiche, branche, out.strip()[:7]))
            return out.strip()
    branche, dossier = "met4/prep-" + fiche, ESSAIS + "/prep-" + fiche
    code, out, _ = git(["worktree", "add", "-b", branche, dossier, FICHES[fiche][0]], KIT)
    if code:
        garde("worktree de préparation %s : %s" % (fiche, out))
    chemin = dossier + "/CHANTIER.md"
    with open(chemin, encoding="utf-8", newline="") as f:
        texte = f.read()
    nl = "\r\n" if "\r\n" in texte else "\n"
    lignes, sortie, i, vus = texte.split(nl), [], 0, 0
    while i < len(lignes):
        ligne = lignes[i]
        if ligne.startswith("- **artefact du chantier** :"):
            sortie.append("- **artefact du chantier** : aucun")
            vus += 1
        elif ligne.startswith("- **vérification** :"):
            sortie.append("- **vérification** : le critère de fin")
            vus += 1
            while i + 1 < len(lignes) and lignes[i + 1].startswith("  "):
                i += 1
        else:
            sortie.append(ligne)
        i += 1
    if vus != 2:
        garde("CHANTIER.md de %s : %d lignes changées sur 2" % (fiche, vus))
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(nl.join(sortie))
    git(["add", "CHANTIER.md"], dossier)
    code, out, _ = git(["commit", "-m", "MET4 : préparation de l'essai %s — artefact aucun, vérification au critère "
                        "de fin (comme VIT25)" % fiche], dossier)
    if code:
        garde("commit de préparation %s : %s" % (fiche, out))
    git(["worktree", "remove", dossier], KIT)
    sha = git(["rev-parse", branche], KIT)[1].strip()
    dire("PRÉPARÉ %s : %s sur %s" % (fiche, sha[:7], FICHES[fiche][0]))
    return sha


def connecte():
    """`claude auth status` dit-il `"loggedIn": true` ? Le 2026-10-06, le premier essai de VIT25 est mort en 10 s :
    « OAuth session expired and could not be refreshed », `loggedIn: false`."""
    _, statut, _ = lancer([claude_du_kit(), "auth", "status"], cwd=KIT)
    return '"loggedIn": true' in statut


def essai_dans_le_kit():
    """Le kit chargé a-t-il `vlp.py essai` (MET2) ? Un motif refusé rend sa GARDE sans rien écrire."""
    _, out, _ = vlp(["essai", "../sonde"], KIT)
    return "GARDE: essai non déclaré" in out


def declarer(nom):
    """Le dossier de transcripts de l'essai, et celui des bacs qu'il ouvrirait, déclarés pour la session qui lance.
    Leurs noms dérivent du chemin, chaque caractère hors [A-Za-z0-9] changé en « - », comme le fait claude."""
    projet = re.sub(r"[^A-Za-z0-9]", "-", ESSAIS + "/" + nom)
    bacs = re.sub(r"[^A-Za-z0-9]", "-", os.path.join(tempfile.gettempdir(), "claude")) + "-" + projet + "-*"
    for motif in (projet, bacs):
        code, out, _ = vlp(["essai", motif], KIT)
        if code:
            garde("essai %s non déclaré — %s" % (nom, out.strip()))
        dire("  " + out.strip())


def worktree(nom, prep, fiche):
    """Le worktree de l'essai, son post-it, et la carte qui doit dire PROCHAINE=<fiche>."""
    dossier = ESSAIS + "/" + nom
    code, out, _ = git(["worktree", "add", "-b", "met4/" + nom, dossier, prep], KIT)
    if code:
        garde("worktree %s : %s" % (nom, out))
    p = git(["rev-parse", "--git-path", "vlp-chantier"], dossier)[1].strip()
    p = p if os.path.isabs(p) else os.path.join(dossier, p)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(FICHES[fiche][2] + "\n")
    _, carte, _ = vlp(["carte", "--python", "py -3"], dossier)
    m = re.search(r"^PROCHAINE=(\S+)", carte, re.M)
    if not m or m.group(1) != fiche:
        garde("carte de %s : PROCHAINE=%s, attendu %s\n%s" % (nom, m.group(1) if m else "?", fiche, carte[-800:]))
    dire("  carte de %s : PROCHAINE=%s" % (nom, fiche))
    return dossier


def relecteur(fiche, dossier, traces):
    """Le rôle relire de boucle.py (vlp:relecture, Opus 5.5, --sha HEAD), par le relais ; rend verdict, $, tours."""
    sys.path.insert(0, KIT + "/scripts")
    import boucle  # pyright: ignore[reportMissingImports]  # chargé du kit à l'exécution, hors du dossier du script
    a = argparse.Namespace(nuit=True, permission_mode="auto")
    cmd = boucle.commande(RELAIS, "relire", fiche, a, boucle.OPUS, str(uuid.uuid4()), suite=" --sha HEAD")
    env = {k: v for k, v in os.environ.items() if k not in boucle.HERITEES}
    trace = os.path.join(traces, "relire.jsonl")
    t0 = time.time()
    with open(trace, "w", encoding="utf-8") as f:
        try:
            subprocess.run(cmd, cwd=dossier, env=env, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT,
                           timeout=3600)
        except subprocess.TimeoutExpired:
            dire("  relecteur : délai de 3600 s dépassé")
    s = boucle.lire_trace(trace)
    r = s["result"] or {}
    texte = str(r.get("result") or "")
    verdict = next((ligne.split()[0] for ligne in texte.splitlines()
                    if ligne.startswith(("ACCEPTÉE", "REFUSÉE"))), "aucun")
    return {"verdict": verdict, "usd": r.get("total_cost_usd") or 0.0, "tours": r.get("num_turns"),
            "s": round(time.time() - t0), "premiere": texte.strip().splitlines()[0] if texte.strip() else "",
            "texte": texte, "session": s["session"]}


def cliquet_avant(dossier, prep):
    """`sante --cliquet` contre la base d'avant la fiche, pas contre celle que la session vient d'écrire : `/vlp:tache`
    réécrit `scripts/sante-base.json` à son étape 6 bis, et le juge de VIT25 comparait donc le code à sa propre base
    (les 4 essais vérifiés le 2026-10-07 l'avaient réécrite). La base de la préparation est remise le temps du
    contrôle, puis celle du commit revient."""
    base = "scripts/sante-base.json"
    code, texte, _ = git(["show", prep + ":" + base], dossier)
    if code:
        return {"code": None, "sortie": ["sans base à la préparation : cliquet non mesuré"]}
    with open(os.path.join(dossier, base), "w", encoding="utf-8", newline="") as f:
        f.write(texte)
    try:
        code, out, _ = vlp(["sante", "--cliquet", "--racine", dossier], dossier)
    finally:
        git(["checkout", "HEAD", "--", base], dossier)
    return {"code": code, "sortie": out.strip().splitlines()[-3:]}


def juger(fiche, dossier, prep, traces, relire=True):
    j = {}
    j["commits"] = git(["log", "--format=%h %s", prep + "..HEAD"], dossier)[1].strip().splitlines()
    j["sale"] = git(["status", "--porcelain"], dossier)[1].strip().splitlines()
    dire("  juge : suite entière du worktree")
    code, out, duree = lancer(PY + [dossier + "/scripts/test-vlp.py"], cwd=dossier, timeout=1800)
    lignes = [ligne for ligne in out.strip().splitlines() if ligne.strip()]
    j["suite"] = {"code": code, "ok": code == 0 and bool(lignes) and lignes[-1].strip() == "OK",
                  "derniere": lignes[-1] if lignes else "", "s": duree,
                  "ecarts": [ligne for ligne in lignes if "ÉCART" in ligne][:10]}
    touches = [f for f in git(["diff", "--name-only", prep, "HEAD"], dossier)[1].splitlines() if f.endswith(".py")]
    j["py_touches"] = touches
    if touches:
        _, out, _ = lancer(["pyright"] + touches, cwd=dossier, timeout=900)
        m = re.search(r"(\d+) errors?", out)
        j["pyright"] = int(m.group(1)) if m else "illisible : " + out.strip()[-200:]
    else:
        j["pyright"] = "aucun .py touché"
    j["cliquet"] = cliquet_avant(dossier, prep)
    avant = git(["show", prep + ":scripts/test-vlp.py"], dossier)[1]
    with open(dossier + "/scripts/test-vlp.py", encoding="utf-8") as f:
        apres = f.read()
    j["verifier"] = [avant.count("verifier("), apres.count("verifier(")]
    if relire:
        dire("  juge : relecteur")
        j["relecteur"] = relecteur(fiche, dossier, traces)
    return j


def essai(fiche, niveau, prep):
    nom = "%s-%s" % (fiche, niveau)
    if not connecte():
        garde("le CLI claude n'est pas connecté (claude auth status : loggedIn false) — rien de lancé")
    dossier = worktree(nom, prep, fiche)
    declarer(nom)
    traces = os.path.join(ICI, "traces", nom)
    os.makedirs(traces, exist_ok=True)
    debut = heure()
    dire("JOUE %s (plafond %s $)" % (nom, FICHES[fiche][1]))
    code, sortie, duree = lancer(PY + [KIT + "/scripts/boucle.py", dossier, "--plafond", "1", "--model", MODELE,
                                       "--effort", niveau, "--budget", FICHES[fiche][1], "--traces", traces,
                                       "--claude", RELAIS], cwd=dossier)
    with open(os.path.join(traces, "boucle.txt"), "w", encoding="utf-8") as f:
        f.write(sortie)
    resume = [ligne for ligne in sortie.splitlines() if ligne.startswith(("FICHE", "ARRÊT", "TOTAL", "GARDE"))]
    for ligne in resume:
        dire("  " + ligne)
    m = re.search(r"^TOTAL .*?· ([\d.,]+) \$", sortie, re.M)
    usd = float(m.group(1).replace(",", ".")) if m else 0.0
    r = {"fiche": fiche, "niveau": niveau, "debut": debut, "boucle_code": code, "boucle_s": duree,
         "boucle": resume, "usd_essai": usd}
    if "You've hit your" in sortie:
        r["limite"] = True
        return r
    if "Failed to authenticate" in sortie:
        garde("connexion perdue pendant %s : %s — worktree et branche à retirer avant de rejouer" % (nom, resume))
    attente = re.search(r"arrière-plan|en fond|notification|prévenu|j'attends|je reprends", sortie, re.I)
    if "CASE [ ]" in sortie and attente:
        garde("%s : la session a rendu la main en attendant (« %s ») — la consigne du relais ne suffit pas"
              % (nom, attente.group(0)))
    r.update(juger(fiche, dossier, prep, traces))
    r["fin"] = heure()
    rel = r["relecteur"]
    dire("  JUGÉ %s : suite %s · pyright %s · cliquet %s · verifier( %s→%s · relecteur %s (%.2f $) · essai %.2f $"
         % (nom, "OK" if r["suite"]["ok"] else "ROUGE", r["pyright"], r["cliquet"]["code"], r["verifier"][0],
            r["verifier"][1], rel["verdict"], rel["usd"], usd))
    return r


def a_blanc(fiche, branche):
    """Le chemin d'un essai sans appel modèle : les commits de `branche` jouent le rôle de la session."""
    if fiche not in FICHES:
        garde("fiche %s inconnue (%s)" % (fiche, ", ".join(FICHES)))
    dire("À BLANC %s, commits de %s à la place de la session — aucun appel modèle" % (fiche, branche))
    dire("  connexion du CLI : %s" % ("oui" if connecte() else "NON — un vrai essai s'arrêterait ici"))
    if not essai_dans_le_kit():
        garde("le kit %s n'a pas `vlp.py essai` (MET2) : les essais ne seraient pas comptés — avancer main" % KIT)
    dire("  vlp.py essai : présent dans le kit")
    prep = preparer(fiche)
    nom = "%s-blanc" % fiche
    dossier = worktree(nom, prep, fiche)
    try:
        code, out, _ = git(["merge", "--ff-only", branche], dossier)
        if code:
            garde("merge --ff-only %s : %s" % (branche, out.strip()))
        j = juger(fiche, dossier, prep, None, relire=False)
        dire("  commits : %d — %s" % (len(j["commits"]), " | ".join(j["commits"])))
        dire("  arbre sale : %d ligne(s)" % len(j["sale"]))
        dire("  suite : %s (%s s) — dernière ligne « %s »" % ("OK" if j["suite"]["ok"] else "ROUGE", j["suite"]["s"],
                                                               j["suite"]["derniere"]))
        dire("  pyright : %s — %s" % (j["pyright"], ", ".join(j["py_touches"]) or "-"))
        dire("  cliquet : code %s — %s" % (j["cliquet"]["code"], " / ".join(j["cliquet"]["sortie"])))
        dire("  verifier( : %s → %s" % tuple(j["verifier"]))
        dire("  relecteur : sauté à blanc (appel modèle)")
    finally:
        git(["worktree", "remove", "--force", dossier], KIT)
        git(["branch", "-D", "met4/" + nom], KIT)
        dire("  worktree %s et branche met4/%s retirés" % (nom, nom))


def lister(liste):
    """`--a-blanc` sans valeur : ce qui serait joué, lu dans les constantes et le jsonl seulement."""
    vus, total = faits()
    dire("À BLANC, liste seule — aucun appel modèle, ni git, ni CLI · kit %s · essais sous %s" % (KIT, ESSAIS))
    for fiche, niveau in liste:
        nom = "%s-%s" % (fiche, niveau)
        dire("  ESSAI %s · effort %s · plafond %s $ · avant %s · worktree %s/%s · %s" % (
            nom, niveau, FICHES[fiche][1], FICHES[fiche][0], ESSAIS, nom,
            "déjà noté" if (fiche, niveau) in vus else "à jouer"))
    dire("FIN %d essai(s) listé(s) · %.2f $ déjà notés (essais + relecteurs)" % (len(liste), total))


def essais_voulus(texte):
    """`VIT23:high,…` en couples (fiche, niveau), chacun connu, sinon une GARDE."""
    liste = []
    for e in texte.split(","):
        fiche, _, niveau = e.strip().partition(":")
        if fiche not in FICHES or niveau not in NIVEAUX:
            garde("essai %r : fiche parmi %s, niveau parmi %s" % (e, ", ".join(FICHES), ", ".join(NIVEAUX)))
        liste.append((fiche, niveau))
    return liste


def faits():
    if not os.path.isfile(RESULTATS):
        return {}, 0.0
    vus, total = {}, 0.0
    with open(RESULTATS, encoding="utf-8") as f:
        for ligne in f:
            d = json.loads(ligne)
            vus[(d["fiche"], d["niveau"])] = d
            total += d.get("usd_essai", 0.0) + (d.get("relecteur") or {}).get("usd", 0.0)
    return vus, total


def main():
    global KIT, ESSAIS
    # la console de Windows est en cp1252 quand la sortie passe par un tube : « → » y plantait (MET3, 2026-10-07)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    p = argparse.ArgumentParser()
    p.add_argument("--conception", choices=("VIT12", "REG2"), help="la fiche de conception, tranchée à MET3")
    p.add_argument("--essais", help="VIT23:high,… ; défaut : les 12, fiche par fiche")
    p.add_argument("--borne", type=float, help="$ cumulés (essais + relecteurs) qui arrêtent ; exigée hors --a-blanc")
    p.add_argument("--kit", required=True, help="le dépôt du kit dont on lance vlp.py et boucle.py")
    p.add_argument("--essais-dir", required=True, help="le dossier où poser les worktrees d'essai")
    p.add_argument("--a-blanc", nargs="?", const="", help="seul : la liste ; <fiche>:<branche d'un essai déjà joué>")
    a = p.parse_args()
    KIT, ESSAIS = a.kit.replace("\\", "/"), a.essais_dir.replace("\\", "/")
    os.environ["MET4_KIT"] = KIT
    if a.a_blanc == "":
        return lister(essais_voulus(a.essais) if a.essais else [(f, n) for f in CODE for n in NIVEAUX])
    if a.a_blanc:
        fiche, branche = a.a_blanc.split(":", 1)
        return a_blanc(fiche, branche)
    if not a.conception or a.borne is None:
        garde("--conception et --borne sont exigées pour jouer : la borne est celle que l'utilisateur a dite")
    if not essai_dans_le_kit():
        garde("le kit %s n'a pas `vlp.py essai` (MET2) : les essais ne seraient pas comptés — avancer main" % KIT)
    liste = essais_voulus(a.essais) if a.essais else [(f, n) for f in CODE + (a.conception,) for n in NIVEAUX]
    os.makedirs(ESSAIS, exist_ok=True)
    for fiche, niveau in liste:
        vus, total = faits()
        if (fiche, niveau) in vus:
            dire("DÉJÀ %s-%s" % (fiche, niveau))
            continue
        if total >= a.borne:
            garde("borne atteinte : %.2f $ ≥ %.2f $" % (total, a.borne))
        r = essai(fiche, niveau, preparer(fiche))
        if r.get("limite"):
            garde("limite d'usage pendant %s-%s : %s" % (fiche, niveau, r["boucle"]))
        with open(RESULTATS, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    vus, total = faits()
    dire("FIN %d essais notés · %.2f $ (essais + relecteurs)" % (len(vus), total))


if __name__ == "__main__":
    main()
