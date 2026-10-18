"""La relecture d'une fiche, et `git_texte`, le lanceur de `git` du cœur (REF47 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import glob
import io
import os
import re

import carnet

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (lignes_de)
from noyau.fiches import (SEUIL_FICHE, SEUIL_SOCLE, cmd_extraire, cmd_socle, extraire_lignes)
from noyau.carte import (carte, equipe, trouver)
from noyau.page import (SEUIL_PAGE)
from noyau.notes import (nom_etat)
from noyau.feuille import (champ)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF47 — `meme_depot_ailleurs`, `chemins_a_suivre`, `relectures_de` — se lisent ici seulement.
__all__ = [
    "RELECTURE", "git_texte", "CODE_PLUGIN", "retard_plugin", "regrouper_dossiers", "etat_git", "ligne_git",
    "suivi_en_retard", "prefixe_relecture", "retirer_relectures", "instantane", "texte_fichiers", "noms_fichiers",
    "entrees", "invites", "ancre", "noms_ecrits", "nomme", "cmd_relecture", "cmd_lignes", "PLAN", "cmd_equiper",
]


# --- relecture ---------------------------------------------------------------

RELECTURE = "vlp-relecture-"    # le préfixe des worktrees de relecture : `--retirer` ne retire qu'eux


def git_texte(args, cwd, env=None):
    """(code, texte) de `git <args>` dans `cwd` : la sortie si le code vaut 0, sinon la première ligne
    d'erreur. Git qui ne se lance pas : (None, raison) — jamais un traceback."""
    import subprocess
    try:
        r = subprocess.run([etat.GIT, "-c", "core.quotepath=false"] + args, cwd=cwd, env=env, capture_output=True,
                           encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "git ne se lance pas : %s" % e
    if r.returncode:
        return r.returncode, ((r.stderr or "").strip().splitlines() or ["code %d" % r.returncode])[0]
    return 0, r.stdout


# Le code du plugin : ce qu'un `/reload-plugins` recharge, ou que les commandes lisent (chantier ESR).
CODE_PLUGIN = ("skills", "agents", "hooks", "scripts", "templates", ".claude-plugin", "methode-chantier.md",
               "cloture.md", "enchainement.md", "ARTEFACTS.md", "nuit.md")


def retard_plugin(racine, kit=None):
    """`(n, principal, branche)` : `n` commits de `racine` qui touchent `CODE_PLUGIN` et manquent au
    `HEAD` du kit chargé (`kit`, défaut `KIT`, résolu en `principal`) — un worktree du kit en avance
    sur le dossier que suit `~/.claude/skills/vlp` (chantier ESR). `branche` : celle de `racine`, ou
    son sha court si `HEAD` est détaché. `None` : autre dépôt, même dossier, retard nul, git muet."""
    principal = os.path.realpath(kit or etat.KIT)
    sorties = [git_texte(["rev-parse", "--path-format=absolute", "--git-common-dir", "--show-toplevel"], d)
               for d in (principal, racine)]
    if any(code != 0 for code, _ in sorties) or not meme_depot_ailleurs(sorties[0][1], sorties[1][1]):
        return None
    code, tete = git_texte(["rev-parse", "HEAD"], principal)
    code2, n = git_texte(["rev-list", "--count", "%s..HEAD" % tete.strip(), "--"] + list(CODE_PLUGIN), racine)
    if code != 0 or code2 != 0 or not n.strip().isdigit() or int(n) == 0:
        return None
    _, branche = git_texte(["rev-parse", "--abbrev-ref", "HEAD"], racine)
    if branche.strip() == "HEAD":
        _, branche = git_texte(["rev-parse", "--short", "HEAD"], racine)
    return int(n), principal, branche.strip()


def meme_depot_ailleurs(kit, racine):
    """Vrai si deux sorties de `git rev-parse --path-format=absolute --git-common-dir --show-toplevel` — le kit, puis
    `racine` — disent un même dépôt vu de deux dossiers (un worktree du kit). Ne lance rien (REF47)."""
    lieux = []
    for t in (kit, racine):
        if len(t.split()) < 2:
            return False
        lieux.append([os.path.normcase(os.path.realpath(x)) for x in t.strip().split("\n")[:2]])
    return lieux[0][0] == lieux[1][0] and lieux[0][1] != lieux[1][1]


def regrouper_dossiers(racine, chemins):
    """`chemins` (relatifs à `racine`, en barres obliques), où un dossier dont tous les fichiers sur disque sont
    dans la liste se nomme par lui-même (`ctx/`), pas fichier par fichier, et ses seuls fichiers directs par `ctx/*`
    (ses sous-dossiers restent nommés) ; la racine ne se regroupe jamais. Rend `[(nom, exemple)]` : `exemple`, un
    chemin de la liste sous ce nom, de préférence un fichier — ce que `git check-ignore` interroge (NUI36)."""
    par_dossier = {}
    for c in chemins:
        par_dossier.setdefault(c.rstrip("/").rpartition("/")[0], []).append(c)
    rendus = []
    for d, liste in sorted(par_dossier.items()):
        noms = {c.rstrip("/").rpartition("/")[2] for c in liste}
        try:
            sur_disque = set(os.listdir(os.path.join(racine, d))) if d else None
        except OSError:
            sur_disque = None
        exemple = sorted(liste, key=lambda c: (c.endswith("/"), c))[0]
        if sur_disque is None:
            rendus += [(c, c) for c in sorted(liste)]
        elif sur_disque == noms:
            rendus.append((d + "/", exemple))
        elif {n for n in sur_disque if os.path.isfile(os.path.join(racine, d, n))} <= noms:
            rendus += [(d + "/*", exemple)] + [(c, c) for c in sorted(liste) if c.endswith("/")]
        else:
            rendus += [(c, c) for c in sorted(liste)]
    return rendus


def etat_git(racine):
    """L'état Git de ce que la méthode veut suivi (`methode-chantier.md`, « Ce qui part dans Git ») : `CHANTIER.md`,
    `CLAUDE.md`, le dossier de la ligne **contexte**. `None` hors d'un dépôt Git (ou Git muet) ; sinon
    `{"ignoré": [(nom, exemple)], "non ajouté": [...]}` (`regrouper_dossiers`), vides quand tout est suivi (NUI35,
    partagé avec `niveau`)."""
    code, _ = git_texte(["rev-parse", "--show-toplevel"], racine)
    if code != 0:
        return None
    contexte = champ(lignes_de(os.path.join(racine, "CHANTIER.md")), "contexte", "context AI/")
    cibles = ["CHANTIER.md", "CLAUDE.md", contexte.rstrip("/") + "/"]
    etat = {}
    for nom, options in (("ignoré", ["--ignored"]), ("non ajouté", [])):
        code, t = git_texte(["ls-files", "--others", "--exclude-standard", "--directory"] + options + ["--"] + cibles,
                            racine)
        etat[nom] = regrouper_dossiers(racine, chemins_a_suivre(t) if code == 0 else [])
    return etat


def chemins_a_suivre(texte):
    """Les chemins d'une sortie de `git ls-files --others --directory`, sans le cache de Python : il n'est jamais du
    contexte, il reste ignoré sans écart. Ne lance rien (REF47)."""
    return [l for l in texte.split("\n") if l and not l.endswith("__pycache__/")]


def ligne_git(racine):
    """Les lignes `GIT=` de la carte : `GIT=suivi`, `GIT=hors Git`, ou `GIT=ignoré …` et/ou `GIT=non ajouté …`."""
    etat = etat_git(racine)
    if etat is None:
        return ["GIT=hors Git"]
    lignes = ["GIT=%s %s" % (nom, ", ".join(n for n, _ in liste)) for nom, liste in etat.items() if liste]
    principale, retard = suivi_en_retard(racine)
    if retard:
        lignes.append("GIT=en retard sur %s : %s suivi(s) là-bas, pas ici — worktree né avant ; y fusionner %s"
                      % (principale, ", ".join(retard), principale))
    return lignes or ["GIT=suivi"]


def suivi_en_retard(racine):
    """`(branche principale, [cibles])` : `CHANTIER.md` et `CLAUDE.md` que la branche principale suit et que `HEAD`
    ne suit pas — un worktree né avant que Git suive le contexte (Cairn, `FAM`, panne `N2` d'`AVL4`, NWT) ; sa carte
    lit alors un vieux `CHANTIER.md`. Sur la branche principale, ou hors Git : `[]`."""
    principale = coeur.branche_principale(racine)
    code, nom = git_texte(["rev-parse", "--abbrev-ref", "HEAD"], racine)
    if not principale or code != 0 or nom.strip() == principale:
        return principale, []

    def suivi(rev, cible):
        """Vrai si `rev` suit `cible`."""
        code, s = git_texte(["ls-tree", "--name-only", rev, "--", cible], racine)
        return code == 0 and bool(s.strip())
    return principale, [c for c in ("CHANTIER.md", "CLAUDE.md") if suivi(principale, c) and not suivi("HEAD", c)]


def prefixe_relecture(fiche=None):
    """`vlp-relecture-`, ou `vlp-relecture-<canal>-` quand `VLP_CANAL` est posé (chantier NUI) : deux
    canaux de nuit relisent dans le même dépôt, chacun ne retire que ses worktrees. Avec `fiche`, suivi de
    `<fiche>-` : deux relecteurs lancés ensemble (chantier ISO) ne retirent chacun que les copies de sa fiche."""
    canal = re.sub(r"[^\w.]", "_", os.environ.get(carnet.ENV_CANAL, "").strip())
    propre = re.sub(r"[^\w.]", "_", fiche.strip()) if fiche else ""
    return RELECTURE + (canal + "-" if canal else "") + (propre + "-" if propre else "")


def retirer_relectures(racine, fiche=None):
    """Retire les worktrees `vlp-relecture-*` du dépôt — ceux du canal seul si `VLP_CANAL` est posé, ceux
    de `fiche` seule si elle est donnée —, puis `prune` : le nombre retiré."""
    code, liste = git_texte(["worktree", "list", "--porcelain"], racine)
    n = 0
    for chemin in relectures_de(liste, prefixe_relecture(fiche)) if code == 0 else []:
        n += git_texte(["worktree", "remove", "--force", chemin], racine)[0] == 0
    git_texte(["worktree", "prune"], racine)
    return n


def relectures_de(liste, prefixe):
    """Les worktrees d'une sortie de `git worktree list --porcelain` dont le dossier commence par `prefixe`. Ne lance
    rien (REF47)."""
    chemins = [l[len("worktree "):] for l in liste.splitlines() if l.startswith("worktree ")]
    return [c for c in chemins if os.path.basename(c.rstrip("/\\")).startswith(prefixe)]


def instantane(racine):
    """(code, sha) : l'arbre de travail — suivis et non suivis, selon `.gitignore` — en commit de
    parent `HEAD`, par un index temporaire : ni `HEAD` ni l'index réel ne bougent."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="vlp-index-") as d:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(d, "index"))
        for args in (["read-tree", "HEAD"], ["add", "-A"], ["write-tree"]):
            code, arbre = git_texte(args, racine, env)
            if code != 0:
                return code, arbre
    # Une identité à lui : l'instantané ne dépend pas de la configuration du poste.
    env = dict(os.environ, GIT_AUTHOR_NAME="vlp", GIT_AUTHOR_EMAIL="vlp@relecture",
               GIT_COMMITTER_NAME="vlp", GIT_COMMITTER_EMAIL="vlp@relecture")
    return git_texte(["commit-tree", arbre.strip(), "-p", "HEAD", "-m", "vlp relecture : instantané"], racine, env)


def texte_fichiers(fiche):
    """Le texte de la ligne **Fichiers** d'une fiche, libellé ôté, jusqu'à la ligne vide ou au champ suivant ;
    "" sans elle."""
    k = next((i for i, l in enumerate(fiche) if l.startswith("**Fichiers**")), None)
    if k is None:
        return ""
    para = [fiche[k][len("**Fichiers**"):]]
    for l in fiche[k + 1:]:
        if not l.strip() or l.startswith(("**", "<!--")):
            break
        para.append(l)
    return " ".join(para)


def noms_fichiers(fiche):
    """Ce que nomme la ligne **Fichiers** d'une fiche (`texte_fichiers`) :
    chaque `…` entre backticks, et chaque mot hors d'eux — le gabarit n'en met pas."""
    texte = texte_fichiers(fiche)
    return (set(re.findall(r"`([^`]+)`", texte))
            | set(re.split(r"[\s,;:()]+", re.sub(r"`[^`]*`", " ", texte)))) - {""}


def entrees(dossier):
    """{nom en minuscules : vrai si dossier} des entrées de `dossier` — la racine d'un projet, pour `invites`."""
    try:
        return {e.lower(): os.path.isdir(os.path.join(dossier, e)) for e in os.listdir(dossier)}
    except OSError:
        return {}


def invites(fiche, racine):
    """La liste d'invités de la ligne **Fichiers** d'une fiche, pour `lancables` (ENA5 ; jugée sur l'historique Git et
    sur l'arbre par `context AI/119-ena5-juge.py`) : ses noms écrits (`noms_ecrits`), chacun lu par `ancre`."""
    return {ancre(n, racine) for n in noms_ecrits(fiche, racine)}


def ancre(nom, racine):
    """`nom` tel que `croisent` le compare. Un chemin dont le premier nom n'est pas une entrée de `racine` est partiel
    (`references/tache-page.md`, `ai/08-etat.md` coupé d'un chemin à espace) : il vaut son nom seul, que `croisent`
    fait croiser tout dossier et tout chemin de même nom ; un dossier partiel vaut `*`, qui croise tout."""
    if "/" in nom and nom.split("/", 1)[0] not in racine:
        return "*" if nom.endswith("/") else nom.rsplit("/", 1)[-1]
    return nom


def noms_ecrits(fiche, racine):
    """Les noms de la ligne **Fichiers** d'une fiche, normalisés — `\\` en `/`, `./`, guillemets et ponctuation de fin
    ôtés, minuscules. N'entre que chemin (un `/`), motif, nom à extension (`.gitignore` compris) ou entrée de
    `racine` (`entrees`) : `skills` → `skills/`, pas `carte`. Entre backticks, le tout, et chaque mot s'ils sont
    plusieurs, coupés aux blancs et aux `:` (`vlp.py niveau`, `vlp.py:513`) ; hors d'eux, chaque mot. Un nom de trop
    ne coûte qu'un départ ensemble ; un nom manqué, un conflit."""
    texte = texte_fichiers(fiche)

    def propre(n):
        """Le nom normalisé."""
        n = n.strip().strip("\"'").rstrip(".,;").replace("\\", "/").lower()
        return n[2:] if n.startswith("./") else n
    candidats = []
    for brut in re.findall(r"`([^`]+)`", texte):
        mots = [m for m in re.split(r"[\s:\"']+", brut) if m]
        candidats += [propre(brut)] + (list(map(propre, mots)) if len(mots) > 1 else [])
    candidats += map(propre, re.split(r"[\s,;:()]+", re.sub(r"`[^`]*`", " ", texte)))
    rendu = set()
    for n in candidats:
        if n.strip("/") and ("/" in n or re.search(r"[*?[{]", n)
                             or re.fullmatch(r"\.[\w-]+(?:\.[\w-]+)*|[\w-]+(?:\.[\w-]+)+", n)):
            rendu.add(n)
        elif n in racine:
            rendu.add(n + "/" if racine[n] else n)
    return rendu


def nomme(chemin, noms):
    """Vrai si `chemin` (relatif au dépôt, en `/`) est nommé : égal, fin de chemin après un `/`
    (`vlp.py` pour `scripts/vlp.py`), ou sous un dossier nommé (`templates/`)."""
    return any(chemin == n or chemin.endswith("/" + n) or (n.endswith("/") and "/" + n in "/" + chemin)
               for n in noms)


def cmd_relecture(a, sortie):
    """La relecture d'une fiche (chantier REV) : ce qu'en dit la docstring du module."""
    import tempfile
    projet = trouver(os.getcwd())
    code, racine = git_texte(["rev-parse", "--show-toplevel"], projet or os.getcwd())
    if code != 0:
        sortie.write("GARDE: pas de dépôt Git — %s\n" % racine)
        return 1
    racine = racine.strip()
    if a.retirer:
        sortie.write("RETIRÉ %d\n" % retirer_relectures(racine, a.fiche))
        return 0
    if not a.fiche or projet is None:
        sortie.write("GARDE: %s\n" % ("relecture <fiche> [--sha S], ou relecture --retirer" if not a.fiche
                                      else "pas de CHANTIER.md au-dessus de %s" % os.getcwd()))
        return 1
    retirer_relectures(racine, a.fiche)
    if a.sha:
        code, sha = git_texte(["rev-parse", "--verify", "--quiet", a.sha + "^{commit}"], racine)
        pourquoi = "commit inconnu : %s" % a.sha
    else:
        code, sha = instantane(racine)
        pourquoi = "instantané impossible — %s" % sha
    if code != 0:
        sortie.write("GARDE: %s\n" % pourquoi)
        return 1
    sha = sha.strip()
    code, parent = git_texte(["rev-parse", "--verify", "--quiet", sha + "^"], racine)
    if code != 0:
        sortie.write("GARDE: commit sans parent : %s\n" % sha[:12])
        return 1
    parent = parent.strip()
    dossiers = []
    for nom, rev in (("apres", sha), ("avant", parent)):
        d = tempfile.mkdtemp(prefix=prefixe_relecture(a.fiche) + nom + "-")
        code, err = git_texte(["worktree", "add", "--detach", d, rev], racine)
        dossiers.append(d)
        if code != 0:
            retirer_relectures(racine, a.fiche)
            sortie.write("GARDE: worktree %s impossible — %s\n" % (nom, err))
            return 1
    # Le fichier de fiches que nomme CHANTIER.md dans APRÈS, au même endroit du dépôt que le projet.
    code, prefixe = git_texte(["rev-parse", "--show-prefix"], projet)
    prefixe = prefixe.strip() if code == 0 else ""
    apres_projet = os.path.normpath(os.path.join(dossiers[0], prefixe))
    # Le chantier du dossier qui relit, pas celui de la copie : APRÈS est un worktree détaché, que la règle des
    # branches de `courant_de` verrait toujours hériter de la principale (chantier NUI22).
    courant = coeur.courant_de(projet) if equipe(apres_projet) else None
    fichier = os.path.normpath(os.path.join(apres_projet, courant)) if courant else ""
    fiche, _ = extraire_lignes(lignes_de(fichier) if os.path.isfile(fichier) else [], a.fiche)
    if not fiche:
        retirer_relectures(racine, a.fiche)
        sortie.write("GARDE: fiche %s absente du fichier de fiches courant d'APRÈS : %s\n" % (a.fiche, courant or "aucun"))
        return 1
    # Pas de `FICHIER=` : le fichier entier porte la suite du chantier (FFE, REL1 : 1 lecture sur 42).
    sortie.write("APRÈS=%s\nAVANT=%s\n" % (dossiers[0], dossiers[1]))
    cmd_socle(fichier, sortie)
    cmd_extraire(fichier, a.fiche, sortie)
    code, etat = git_texte(["diff", "--name-status", "--no-color", parent, sha], racine)
    sortie.write(etat if code == 0 else "GARDE: git diff --name-status en échec — %s\n" % etat)
    fiches_rel, noms = prefixe + (courant or "").replace("\\", "/"), noms_fichiers(fiche)
    # Le fichier d'état : toute fiche peut écrire à son journal (REV7).
    etat_val = champ(lignes_de(os.path.join(apres_projet, "CHANTIER.md")), "fichier d'état", "aucun")
    exclus = {fiches_rel} | (set() if etat_val.startswith("aucun") else {prefixe + etat_val.replace("\\", "/")})
    for ligne in etat.splitlines() if code == 0 else []:
        chemin = ligne.split("\t")[-1]
        if chemin not in exclus and "/artefacts/" not in "/" + chemin and not nomme(chemin, noms):
            sortie.write("HORS FICHE %s\n" % chemin)
    code, diff = git_texte(["diff", "--no-color", "--no-ext-diff", parent, sha], racine)
    sortie.write(diff if code == 0 else "GARDE: git diff en échec — %s\n" % diff)
    return 0


def cmd_lignes(chemins, sortie):
    """`wc -l` et `ls` sans shell : une ligne par chemin (motif `*` et `~` compris)."""
    for motif in chemins:
        trouves = sorted(glob.glob(os.path.expanduser(motif))) or [os.path.expanduser(motif)]
        for c in trouves:
            if os.path.isdir(c):
                reel = os.path.realpath(c)
                sortie.write("DOSSIER %s%s\n" % (c, "" if os.path.normcase(reel) == os.path.normcase(os.path.abspath(c)) else " → " + reel))
            elif os.path.isfile(c):
                sortie.write("%d %s\n" % (len(lignes_de(c)), c))
            else:
                sortie.write("ABSENT %s\n" % motif)
    sortie.write("SEUILS page %d · fiche %d · socle %d\n" % (SEUIL_PAGE, SEUIL_FICHE, SEUIL_SOCLE))
    return 0


PLAN = re.compile(r"^## [A-Z]{1,3}[0-9]|^\*\*(Dépend de|Tentatives|Critère de fin)\*\*")


def cmd_equiper(dossier, contexte, sortie):
    """Ce que `/vlp:init` regarde avant d'équiper, sans `pwd`, `ls`, `head` ni `grep` ; un dossier absent, une
    `GARDE:`, sort 1 (chantier ISO)."""
    d = os.path.abspath(dossier)
    if not os.path.isdir(d):
        sortie.write("GARDE: dossier absent : %s — rien lu\n" % d)
        return 1
    sortie.write("DOSSIER=%s\n" % d)
    sous = sorted((n for n in os.listdir(d) if not n.startswith(".") and os.path.isdir(os.path.join(d, n))), key=str.lower)
    for n in sous[:20]:
        sortie.write("%s/\n" % n)
    if "CLAUDE.md" in os.listdir(d):
        sortie.write("CLAUDE.md\n")
    c = io.StringIO()
    carte(d, c)
    for l in c.getvalue().splitlines():
        if re.match(r"^(PROJET|VOISIN)=|^AUCUN_PROJET", l):
            sortie.write(l + "\n")
    sortie.write("ETAT=%s\n" % nom_etat(os.path.join(d, contexte)))
    return 0
