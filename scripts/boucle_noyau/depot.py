"""Ce que la boucle fait dans Git et sur le disque : commit, branche, worktrees, flux, traces (REF53).

Sorti de `boucle.py`, qui le ré-exporte.
"""
import os
import tempfile

from boucle_noyau.session import kit, ligne_carnet

__all__ = ["commiter", "git_revert", "tete_de", "arbre_propre", "brancher", "mettre_de_cote", "cause_de_refus",
    "exclure_worktrees", "ecrire_ligne", "suivre", "dossier_de_traces"
]


def commiter(racine, sujet, fichier=None):
    """(ok, erreur) : `git add -A` puis `git commit -m <sujet>` ; avec `fichier`, ce fichier seul."""
    git = kit().git_texte
    code, err = git(["add", "--", fichier] if fichier else ["add", "-A"], racine)
    if code == 0:
        code, err = git(["commit", "-q", "-m", sujet] + (["--", fichier] if fichier else []), racine)
    return code == 0, err


def git_revert(racine):
    """None si `git revert --no-edit HEAD` passe, sinon sa première ligne d'erreur."""
    code, err = kit().git_texte(["revert", "--no-edit", "HEAD"], racine)
    return None if code == 0 else err


def tete_de(racine):
    """Le sha de `HEAD` dans `racine`, ou None."""
    code, sha = kit().git_texte(["rev-parse", "HEAD"], racine)
    return sha.strip() if code == 0 else None


def arbre_propre(racine):
    """Vrai si `git status --porcelain` ne rend rien ; None si Git ne répond pas."""
    code, s = kit().git_texte(["status", "--porcelain"], racine)
    return None if code != 0 else not s.strip()


def brancher(racine, branche, base):
    """None si `git switch -c <branche> <base>` passe, sinon sa première ligne d'erreur."""
    code, err = kit().git_texte(["switch", "-q", "-c", branche, base], racine)
    return None if code == 0 else err


def mettre_de_cote(racine, a, code, raison):
    """Met le chantier `code` de côté — seul endroit où la boucle le fait : une ligne `mis-de-cote:<raison>` au
    carnet ; arbre propre, rien de plus ; sinon `git add -A` et le commit WIP (`WIP_SUJET` de vlp.py), hors
    `COMMIT_FICHE`. Rend None, ou la raison d'arrêt du canal : commit refusé par un hook (ligne `wip-refuse`, arbre tel
    quel — jamais `--no-verify`) ou Git muet."""
    raison = " ".join(raison.split())[:200]
    ligne_carnet(a, garde="mis-de-cote:%s" % raison)
    propre = arbre_propre(racine)
    if propre is None:
        return "%s : git status impossible" % code
    if propre:
        return None
    ok, err = commiter(racine, kit().WIP_SUJET % (code, raison))
    if ok:
        return None
    ligne_carnet(a, garde="wip-refuse")
    return "%s : commit WIP refusé — %s" % (code, err)


def cause_de_refus(racine, date):
    """La cause pour laquelle la nuit `date` ne se lance pas depuis `racine`, ou None (NUI9). Rien ne s'écrit : Git est
    lu (`branch`, `status`, `check-ignore`, `worktree list`), dans l'ordre — branche `main`, arbre propre (un plan non
    commité manquerait aux worktrees), fichier des nuits non ignoré (ignoré, il n'est dans aucun worktree), aucun
    worktree ni branche de cette nuit (une nuit lancée se reprend par `--reprendre`)."""
    k = kit()
    code, courante = k.git_texte(["branch", "--show-current"], racine)
    if code != 0:
        return "git branch impossible — %s" % courante
    if courante.strip() != "main":
        return "la branche courante est %s, pas main : les canaux partent de main" % (courante.strip() or "aucune (HEAD détachée)")
    propre = arbre_propre(racine)
    if propre is None:
        return "git status impossible"
    if not propre:
        return "l'arbre n'est pas propre (git status --porcelain) : un plan non commité manquerait aux worktrees"
    try:
        nuits = k.fichier_nuits(racine)
    except ValueError as e:
        return str(e)
    if nuits:
        code, err = k.git_texte(["check-ignore", "-q", nuits], racine)
        if code == 0:
            return ("le fichier des nuits (%s) est ignoré par Git : il n'est dans aucun worktree"
                    % os.path.relpath(nuits, racine).replace("\\", "/"))
        if code != 1:
            return "git check-ignore impossible — %s" % err
    code, liste = k.git_texte(["worktree", "list", "--porcelain"], racine)
    if code != 0:
        return "git worktree list impossible — %s" % liste
    deja = [l[len("worktree "):] for l in liste.splitlines()
            if l.startswith("worktree ") and l.replace("\\", "/").rsplit("/", 1)[-1].startswith("nuit-%s-" % date)]
    if deja:
        return "un worktree de nuit existe déjà (%s) — une nuit lancée se reprend par --reprendre" % deja[0]
    code, branches = k.git_texte(["branch", "--list", "nuit/%s-*" % date], racine)
    if code != 0:
        return "git branch --list impossible — %s" % branches
    if branches.strip():
        return ("une branche de cette nuit existe déjà (%s) — une nuit lancée se reprend par --reprendre"
                % branches.strip().splitlines()[0].lstrip("*+ "))
    return None


def exclure_worktrees(racine, date):
    """None, ou la raison de l'échec. `.claude/worktrees/` non ignoré (`check-ignore` sur le worktree du canal A) : sa
    ligne entre dans `info/exclude` du dépôt commun (`rev-parse --git-common-dir`) — jamais `.gitignore` ni un fichier
    suivi —, sans quoi le worktree d'un canal salirait le `git status` de `main`."""
    k = kit()
    code, err = k.git_texte(["check-ignore", "-q", ".claude/worktrees/nuit-%s-A" % date], racine)
    if code == 0:
        return None
    if code != 1:
        return "git check-ignore impossible — %s" % err
    code, commun = k.git_texte(["rev-parse", "--path-format=absolute", "--git-common-dir"], racine)
    if code != 0:
        return "git rev-parse impossible — %s" % commun
    exclure = os.path.join(commun.strip(), "info", "exclude")
    try:
        os.makedirs(os.path.dirname(exclure), exist_ok=True)
        existant = ""
        if os.path.isfile(exclure):
            with open(exclure, encoding="utf-8", errors="replace") as h:
                existant = h.read()
        with open(exclure, "a", encoding="utf-8", newline="") as h:
            h.write(("\n" if existant and not existant.endswith("\n") else "") + ".claude/worktrees/\n")
    except OSError as e:
        return "info/exclude non écrit — %s" % e
    return None


def ecrire_ligne(verrou, texte):
    """Une ligne à la fois sur la sortie commune : les fils des deux canaux n'entremêlent pas les leurs."""
    with verrou:
        print(texte, flush=True)


def suivre(canal, proc, verrou):
    """Le fil d'un canal (NUI9) : chaque ligne de sa fille, préfixée `[canal] `, puis `FIN <canal> · code <n>` dès qu'elle sort."""
    assert proc.stdout
    for ligne in proc.stdout:
        ecrire_ligne(verrou, "[%s] %s" % (canal, ligne.rstrip("\r\n")))
    ecrire_ligne(verrou, "FIN %s · code %d" % (canal, proc.wait()))


def dossier_de_traces(traces):
    """Rendre le dossier des traces : `traces`, créé s'il manque, comme celui du lanceur de nuit ; sinon un dossier
    temporaire neuf `vlp-boucle-*`. Impossible à créer (un fichier à sa place, un droit) : une GARDE, puis sortie 1
    — avant toute session, rien de joué (dette ARP : un dossier absent rendait un traceback)."""
    try:
        traces = traces or tempfile.mkdtemp(prefix="vlp-boucle-")
        os.makedirs(traces, exist_ok=True)
    except OSError as e:
        print("GARDE: dossier de traces impossible à créer — %s" % e)
        raise SystemExit(1) from e
    return traces
