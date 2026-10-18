"""Clore un chantier : feuille de route, archive, index, coût (REF48 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import os
import re
import sys

from noyau import etat
from noyau.facade import coeur
import noyau.page   # `noyau.page.<nom>` : un test remplace ce nom là
import noyau.relecture   # `noyau.relecture.<nom>` : un test remplace ce nom là
from noyau.commun import (Absent, TITRE, archiver, chemin_archive, lignes_de, lignes_du_projet, lire)
from noyau.fiches import (CLOS_GARDES, VLP_PY)
from noyau.carte import (equipe)
from noyau.page import (
    COMMIT_FICHE,
    arrondi,
    bilan_en_haut,
    dollars,
    esc,
    ligne_files,
    ligne_lire,
    milliers,
    recopier_joints,
    total_sans_page,
)
from noyau.notes import (abri_de_page, chemin_abri, lire_abri, texte_abri)
from noyau.feuille import (
    LETTRES,
    bornes,
    cellule_md,
    champ,
    couts_du_projet,
    feuille,
    fin_lettres,
    lettre_de,
    lettres_prises,
    page_clos,
    page_feuille,
    plage,
    poser_bloc_archive,
    todo_du_fichier,
    zone,
    zone_todo,
)
from noyau.clos import (ecrire_couts, lignes_clos, prix_clos, resommer, total_clos)
from noyau.niveau import (attentes_de_nuit, noter_attentes)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF48 — `textes_du_lot`, `blocs_worktrees`, `prefixes_joues` — se lisent ici seulement.
__all__ = [
    "CLOS_LIGNE", "OUVERT_LIGNE", "PAUSE_LIGNE", "MARQUE_OUVERT", "MARQUE_CLOS", "MARQUE_PAUSE", "ENTREE_CLOS",
    "ROUTAGE_CLOS", "rang_routage_clos", "rang_routage_ouvrir", "ESTIME", "ESTIME_A_ECRIRE", "clos_a_couper",
    "resume_claude", "ouverts", "migre", "poser_marque", "date_ouverture", "textes_contexte", "blobs_git",
    "principal", "worktrees", "autres_worktrees", "ouverts_ailleurs", "chantiers_ailleurs", "code_et_tete",
    "code_du_fichier", "codes_joues", "ecrire_ailleurs", "courant_a_compter", "branche_principale", "postit",
    "courant_de", "courant_ou_rien", "cmd_ouverts", "cmd_postit", "rangee_todo", "oter_rangee", "ecrire_par_tmp",
    "todo_de_clore", "refus_d_oter", "cmd_oter", "refus_de_clore", "cmd_clore",
]


# --- clore -------------------------------------------------------------------

CLOS_LIGNE = "**CLOS** le %s. Ne se rejoue pas — ne sert plus qu'à relire son socle."
OUVERT_LIGNE = "**Ouvert.** le %s."
PAUSE_LIGNE = "**Pause.** le %s — %s"
# Les motifs de lecture des trois marques : le début de ligne, comme `**CLOS**` (chantier NUI21).
MARQUE_OUVERT, MARQUE_CLOS, MARQUE_PAUSE = "**Ouvert.**", "**CLOS**", "**Pause.**"
ENTREE_CLOS = re.compile(r"^- Clos le \S+ : .* \(chantier [A-Z]{1,3}\)\.$")
ROUTAGE_CLOS = "| relire un chantier clos |"


def rang_routage_clos(lignes, repli=None):
    """L'indice de la ligne « relire un chantier clos » du routage ; à défaut, de la première qui commence par
    `repli` ; sinon None. Sa cellule peut se prolonger (`| relire un chantier clos — filet de tests… |`,
    Cairn) : ratée, la clôture de SCH en a posé une seconde (2026-10-14)."""
    debut = ROUTAGE_CLOS[:-2]
    rang = next((k for k, l in enumerate(lignes) if l.startswith(debut) and l[len(debut):][:1] in (" ", "|")), None)
    if rang is None and repli:
        rang = next((k for k, l in enumerate(lignes) if l.startswith(repli)), None)
    return rang


def rang_routage_ouvrir(lignes):
    """Où `ouvrir` pose sa ligne : « relire un chantier clos », sinon le premier « relire le chantier », sinon la
    première ligne de table **clos** (`| relire une fiche `C1` à `C5` | … **clos** … |`, Fil-Rouge : ratée, FIN y a
    eu sa ligne écrite à la main, que `clore` n'a pas retrouvée, 2026-10-14) ; sinon None."""
    rang = rang_routage_clos(lignes, "| relire le chantier")
    if rang is None:
        rang = next((k for k, l in enumerate(lignes) if l.startswith("| ") and "**clos**" in l), None)
    return rang
# La ligne que `ouvrir --estime-fiches` pose : N fiches et leur coût, relus par `clore` (chantier EST).
ESTIME = re.compile(r"^\*\*Estimé\.\*\* (\S+) fiches · (≈\S+ \$)")
ESTIME_A_ECRIRE = "\x00estimé\x00"   # posé dans la ZONE:bilan, remplacé une fois le total mesuré connu


def clos_a_couper(entrees):
    """Les plus anciennes des `entrees` (lignes « Clos le », ou leurs rangs, de la plus ancienne à la plus récente)
    qui dépassent les `CLOS_GARDES` gardées : la coupe de `resume_claude` et de `matin` (chantier NUI)."""
    return entrees[:max(0, len(entrees) - CLOS_GARDES)]


def resume_claude(cl, lettre, texte, date, gardes):
    """Ajoute `- Clos le <date> : T (chantier L).` à la section « Où on en est » de `CLAUDE.md`,
    en place, puis n'en garde que les CLOS_GARDES dernières de cette forme. Vrai si une ligne
    est écrite ; déjà là : rien."""
    debut = next((k for k, l in enumerate(cl) if l.startswith("## Où on en est")), None)
    if debut is None:
        gardes.append("section « Où on en est » absente de CLAUDE.md")
        return False
    fin = next((k for k in range(debut + 1, len(cl)) if cl[k].startswith("## ")), len(cl))
    if any("(chantier %s)" % lettre in l for l in cl[debut:fin]):
        return False
    dernier = max(k for k in range(debut, fin) if cl[k].strip())
    # Une ligne, blancs réduits : `ENTREE_CLOS` la relit, et l'élagage la trouve (chantier TAR).
    texte = re.sub(r"\s*\(chantier %s\)$" % re.escape(lettre), "", " ".join(texte.split()).rstrip("."))
    # Le préfixe aussi, s'il est déjà là : `--resume "Clos le … : T"` le doublait (chantier TYP).
    texte = re.sub(r"^Clos le \S+ : ", "", texte)
    cl.insert(dernier + 1, "- Clos le %s : %s (chantier %s)." % (date, texte, lettre))
    entrees = [k for k in range(debut, fin + 1) if ENTREE_CLOS.match(cl[k])]
    for k in reversed(clos_a_couper(entrees)):
        del cl[k]
    return True


def ouverts(racine, rev=None):
    """Les fichiers `.md` du dossier de contexte (ligne `contexte` de CHANTIER.md) ouverts : un titre `# Chantier `,
    la marque d'ouverture, ni `**CLOS**` ni `**Pause.**` ; triés par nom, chemins relatifs à `racine`. Avec `rev`,
    lus dans ce commit par Git, jamais dans l'arbre de travail. Sans marque, jamais ouvert (chantier NUI21)."""
    return [f for f, lignes in textes_contexte(racine, rev)
            if any(l.startswith("# Chantier ") for l in lignes)
            and any(l.startswith(MARQUE_OUVERT) for l in lignes)
            and not any(l.startswith((MARQUE_CLOS, MARQUE_PAUSE)) for l in lignes)]


def migre(racine, rev=None):
    """Vrai si un fichier titré `# Chantier ` du contexte porte la marque d'ouverture — la règle de `ouverts`, sinon
    une marque posée hors titre ferait un projet « migré » sans aucun chantier visible (NUI23). Faux : `courant_de`
    lit encore l'ancienne ligne de CHANTIER.md, et `niveau --ecrire` pose la marque (NUI30)."""
    return any(any(l.startswith("# Chantier ") for l in lignes) and any(l.startswith(MARQUE_OUVERT) for l in lignes)
               for _, lignes in textes_contexte(racine, rev))


def poser_marque(lignes, marque):
    """Insère `marque`, précédée d'une ligne vide, sous le titre `# Chantier ` de `lignes`, en place ; faux sans
    titre — `ouverts` ne verrait pas une marque posée ailleurs. Le seul poseur : `ouvrir`, `niveau`, `pause`."""
    k = next((k for k, l in enumerate(lignes) if l.startswith("# Chantier ")), None)
    if k is None:
        return False
    lignes[k + 1:k + 1] = ["", marque]
    return True


def date_ouverture(racine, code):
    """`AAAA-MM-JJ` du plus ancien commit « Chantier <code> ouvert » ou « <code> : chantier ouvert », ou None (hors
    Git, aucun tel commit) : la date de la marque que `niveau --ecrire` pose (NUI30)."""
    motif = "^(chantier %s ouvert|%s : chantier ouvert)" % (re.escape(code), re.escape(code))
    code_git, texte = noyau.relecture.git_texte(["log", "--format=%as", "-i", "-E", "--grep=" + motif], racine)
    dates = texte.split() if code_git == 0 else []
    return dates[-1] if dates else None


def textes_contexte(racine, rev=None):
    """[(chemin relatif à `racine`, lignes)] des `.md` du dossier de contexte, triés par nom : l'arbre de travail,
    ou le commit `rev` lu par Git. Sans ligne `contexte` : [] ; à `.`, les chemins sans préfixe. Le lecteur commun de
    `ouverts` et `courant_de`."""
    carte_ = os.path.join(racine, "CHANTIER.md")
    # Un worktree où CHANTIER.md n'est pas suivi n'en a pas (Cairn) : aucun texte, jamais un traceback (NUI30).
    dossier = champ(lignes_de(carte_), "contexte") if os.path.isfile(carte_) else None
    if not dossier:
        return []
    dossier = dossier.strip("`").rstrip("/")
    rel = "%s/%%s" % dossier if dossier != "." else "%s"
    if rev is None:
        base = os.path.join(racine, dossier)
        noms = sorted(n for n in os.listdir(base) if n.endswith(".md")) if os.path.isdir(base) else []
        return [(rel % n, lignes_de(os.path.join(base, n))) for n in noms]
    code, sortie_git = noyau.relecture.git_texte(["ls-tree", "--name-only", rev, "./%s/" % dossier], racine)
    noms = sorted(os.path.basename(l) for l in (sortie_git.splitlines() if code == 0 else []) if l.endswith(".md"))
    specs = ["%s:./%s/%s" % (rev, dossier, n) for n in noms]
    textes = []
    for n, spec, t in zip(noms, specs, blobs_git(specs, racine)):
        if t is None:       # pas un blob lisible d'un coup : `git show`, comme avant VIT3
            code, t = noyau.relecture.git_texte(["show", spec], racine)
            t = t if code == 0 else None
        textes.append((rel % n, t.split("\n") if t is not None else []))
    return textes


def blobs_git(specs, cwd):
    """Lire les objets `specs` (`<rev>:<chemin>`) en un seul `git cat-file --batch` (VIT3) ; rendre, pour chacun, son
    texte tel que `git_texte` le lit de `git show` — UTF-8, `\\r\\n` et `\\r` en `\\n` —, ou None : absent, pas un blob,
    ou Git en échec."""
    import subprocess
    try:
        r = subprocess.run([etat.GIT, "-c", "core.quotepath=false", "cat-file", "--batch"], cwd=cwd, capture_output=True,
                           input="".join(s + "\n" for s in specs).encode("utf-8"), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return [None] * len(specs)
    return [None] * len(specs) if r.returncode else textes_du_lot(r.stdout, len(specs))


def textes_du_lot(sortie, n):
    """Les `n` textes d'une sortie de `git cat-file --batch` (des octets), comme `blobs_git` les rend : UTF-8, fins de
    ligne en `\\n`, None pour un objet absent ou qui n'est pas un blob. Ne lance rien (REF48)."""
    pos, textes = 0, []
    for _ in range(n):
        fin = sortie.find(b"\n", pos)
        tete = sortie[pos:fin].split() if fin >= 0 else []
        pos = fin + 1
        if len(tete) != 3 or not tete[2].isdigit():     # `<spec> missing`, ou `ambiguous` : pas de contenu à sauter
            textes.append(None)
            continue
        taille = int(tete[2])
        contenu, pos = sortie[pos:pos + taille], pos + taille + 1     # le contenu, puis son LF
        textes.append(contenu.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
                      if tete[1] == b"blob" else None)
    return textes


def principal(racine):
    """`(dossier, branche)` du premier bloc de `git worktree list --porcelain` — le dossier principal —, chacun None
    s'il manque (hors Git ; branche : tête détachée). `clore` y lit d'où lancer `fusionner` (NUI26)."""
    blocs = worktrees(racine)
    return blocs[0] if blocs else (None, None)


def worktrees(racine):
    """`[(dossier, branche)]` des blocs de `git worktree list --porcelain`, le principal en tête ; branche None sur une
    tête détachée ; [] hors Git. Lu par `principal` et `ouverts_ailleurs` (NUI27)."""
    code, s = noyau.relecture.git_texte(["worktree", "list", "--porcelain"], racine)
    return blocs_worktrees(s) if code == 0 else []


def blocs_worktrees(texte):
    """`[(dossier, branche)]` d'une sortie de `git worktree list --porcelain`, dans son ordre ; branche None sur une
    tête détachée. Ne lance rien (REF48)."""
    blocs, dossier, branche = [], None, None
    for l in texte.split("\n") + [""]:
        if not l.strip():
            if dossier:
                blocs.append((dossier, branche))
            dossier = branche = None
        elif l.startswith("worktree "):
            dossier = l[len("worktree "):].strip()
        elif l.startswith("branch refs/heads/"):
            branche = l[len("branch refs/heads/"):].strip()
    return blocs


def autres_worktrees(racine):
    """Les dossiers des autres worktrees du dépôt de `racine`, ceux qui existent encore, jamais le sien."""
    ici = os.path.normcase(os.path.realpath(racine))
    return [dossier for dossier, _ in worktrees(racine)
            if os.path.isdir(dossier) and os.path.normcase(os.path.realpath(dossier)) != ici]


def ouverts_ailleurs(racine):
    """`[(dossier, fichier)]` des chantiers ouverts dans les autres worktrees du dépôt de `racine`, lus dans leur arbre
    de travail par `ouverts` ; un dossier disparu n'en a aucun. `ouvrir` y refuse un code déjà pris (NUI27)."""
    return [(dossier, f) for dossier in autres_worktrees(racine) for f in ouverts(dossier)]


def chantiers_ailleurs(racine):
    """`[(code, dossier)]` : le chantier que `courant_de` donne à chaque autre worktree, post-it compris ; un dossier
    sans chantier, ou à plusieurs ouverts (`Absent`), n'en a aucun. `carte` les imprime en `AILLEURS=`, `niveau` n'y
    compte pas d'écart de page (NUI28). Sans chantier à lui, un worktree nomme ceux de ses commits de fiche ouverts
    dans le principal (`codes_joues`, NWT). Au même chantier que `racine`, il ne se nomme que s'il a un commit de
    fiche de ce code que `racine` n'a pas (`codes_joues` contre son `HEAD`) : un hérité se tait, chaque côté
    renvoyait à l'autre (ISO2, TODO 140) ; une fiche jouée là-bas se dit."""
    rendu, (dossier_p, principale), (mien, tete) = [], principal(racine), code_et_tete(racine)
    ouverts_p = {code_du_fichier(dossier_p, f) for f in ouverts(dossier_p)} if dossier_p else set()
    for dossier in autres_worktrees(racine):
        try:
            f = courant_de(dossier)
        except Absent:
            continue
        code = code_du_fichier(dossier, f) if f else None
        joues = [code] if code else [c for c in codes_joues(dossier, principale) if c in ouverts_p]
        rendu += [(c, dossier) for c in joues if c != mien or c in codes_joues(dossier, tete)]
    return rendu


def code_et_tete(racine):
    """`(code, sha)` de `racine` : le code de son chantier courant (`courant_ou_rien`, None sans lui) et son `HEAD`
    (None hors Git) — ce contre quoi `chantiers_ailleurs` juge un autre worktree au même chantier (ISO2)."""
    f = courant_ou_rien(racine)
    code, tete = noyau.relecture.git_texte(["rev-parse", "HEAD"], racine)
    return (code_du_fichier(racine, f) if f else None), (tete.strip() if code == 0 else None)


def code_du_fichier(dossier, f):
    """Le préfixe de la première fiche d'un fichier de fiches (`FAM` pour `## FAM1 …`), ou None sans fiche."""
    ids = [l.split()[1] for l in lignes_de(os.path.join(dossier, f)) if TITRE.match(l)]
    return lettre_de(ids[0]) if ids else None


def codes_joues(dossier, principale):
    """Les préfixes, triés, des commits de fiche `<id> : …` (`COMMIT_FICHE`) de la branche de `dossier` absents de
    `principale` — une branche, ou le `HEAD` d'un autre worktree (ISO2) ; [] sans elle. Un worktree né avant que Git suive le contexte n'a pas la marque d'ouverture, que
    `niveau --ecrire` a posée dans le principal : ses commits disent quel chantier il joue (Cairn, `FAM`, NWT) ; un
    vieux commit jamais fusionné aussi — `chantiers_ailleurs` ne garde que les ouverts du principal."""
    if not principale:
        return []
    code, s = noyau.relecture.git_texte(["log", "--format=%s", principale + "..HEAD"], dossier)
    return prefixes_joues(s) if code == 0 else []


def prefixes_joues(texte):
    """Les préfixes, triés, des sujets de commit de fiche (`<id> : …`, `COMMIT_FICHE`) d'une sortie de
    `git log --format=%s`. Ne lance rien (REF48)."""
    trouves = (COMMIT_FICHE.match(l) for l in texte.splitlines())
    return sorted({lettre_de(t.group(1)) for t in trouves if t})


def ecrire_ailleurs(racine, sortie):
    """Les lignes `AILLEURS=<code> <dossier>` de `carte`, une par chantier de `chantiers_ailleurs` (NUI28)."""
    for code, dossier in chantiers_ailleurs(racine):
        sortie.write("AILLEURS=%s %s\n" % (code, dossier))


def courant_a_compter(projet, sortie):
    """Le chantier courant dont `niveau` compte la page, ou None. Joué dans un autre worktree que le principal (Cairn,
    MOR, 2026-09-29), sa page vit là-bas : `AILLEURS: page: …`, rien de compté (NUI28). Le principal n'en est pas un :
    tout worktree hérite de lui son chantier."""
    courant = courant_de(projet)
    ids = [l.split()[1] for l in lignes_de(os.path.join(projet, courant)) if TITRE.match(l)] if courant else []
    racine_p = os.path.normcase(os.path.realpath(principal(projet)[0] or projet))
    joue = next((dossier for code, dossier in chantiers_ailleurs(projet) if ids and code == lettre_de(ids[0])
                 and os.path.normcase(os.path.realpath(dossier)) != racine_p), None)
    if joue:
        sortie.write("AILLEURS: page: %s joue dans %s — non comptée\n" % (lettre_de(ids[0]), joue))
        return None
    return courant


def branche_principale(racine):
    """La branche du dossier principal (`principal`), ou None (hors Git, tête détachée)."""
    return principal(racine)[1]


def postit(racine):
    """Le chemin du post-it local du dossier — `git rev-parse --git-path vlp-chantier`, propre à chaque worktree,
    jamais suivi ni fusionné —, ou None hors Git (chantier NUI22)."""
    code, p = noyau.relecture.git_texte(["rev-parse", "--git-path", "vlp-chantier"], racine)
    return os.path.join(racine, p.strip()) if code == 0 and p.strip() else None


def courant_de(racine, rev=None):
    """Le fichier de fiches du chantier courant de `racine` (relatif à elle), ou None : le **seul** lecteur
    (chantier NUI22). Dans l'ordre : 1. le post-it du dossier, s'il nomme un ouvert (arbre de travail seul) ;
    2. hors de la branche principale, le seul ouvert ajouté depuis la merge-base avec elle — un hérité n'est pas
    le chantier du dossier ; 3. sinon le seul ouvert. Deux ou plus : `Absent`, que `main` rend en `GARDE:`. Aucune
    marque : None — l'ancienne ligne de CHANTIER.md n'est plus lue (NUI31). Avec `rev`, tout se lit dans ce commit."""
    liste = ouverts(racine, rev)
    p = postit(racine) if rev is None else None
    if p and os.path.isfile(p):
        nomme = lire(p).strip()
        if nomme in liste:
            return nomme
    tete = rev or "HEAD"
    principale = branche_principale(racine)
    code, nom = noyau.relecture.git_texte(["rev-parse", "--abbrev-ref", tete], racine)
    if principale and code == 0 and nom.strip() != principale:
        code, base = noyau.relecture.git_texte(["merge-base", tete, principale], racine)
        if code == 0:
            herites = set(ouverts(racine, base.strip()))
            liste = [f for f in liste if f not in herites]
    if len(liste) > 1:
        raise Absent("plusieurs chantiers ouverts : %s" % ", ".join(liste))
    return liste[0] if liste else None


def courant_ou_rien(racine):
    """`courant_de(racine)`, ou None quand plusieurs chantiers y sont ouverts (`Absent`)."""
    try:
        return courant_de(racine)
    except Absent:
        return None


def cmd_ouverts(a, sortie):
    """`ouverts <projet> [--rev <révision>]` : une ligne `OUVERT <fichier>` par chantier ouvert du projet (`ouverts`), sinon
    `OUVERTS=0` ; sans `CHANTIER.md` ou révision inconnue : `GARDE:`, sort 1."""
    if not equipe(a.projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % a.projet)
        return 1
    if a.rev is not None and noyau.relecture.git_texte(["rev-parse", "--verify", "-q", a.rev + "^{commit}"], a.projet)[0] != 0:
        sortie.write("GARDE: révision inconnue : %s\n" % a.rev)
        return 1
    liste = ouverts(a.projet, a.rev)
    sortie.write("".join("OUVERT %s\n" % f for f in liste) if liste else "OUVERTS=0\n")
    return 0


def cmd_postit(a, sortie):
    """`postit <dossier> <fichier>` : `<fichier>` dans le post-it du dossier, écrit comme `ouvrir` le fait. Le chef le
    pose pour un sous-agent isolé en worktree, qui ne peut pas écrire dans le `.git` du dossier principal (ISO7, ISO8).
    Hors Git, ou `<fichier>` qui n'est pas un ouvert du dossier : `GARDE:`, sort 1, rien d'écrit."""
    fichier = a.fichier.replace("\\", "/")
    p = postit(a.dossier) if os.path.isdir(a.dossier) else None
    if not p:
        sortie.write("GARDE: %s hors Git ou introuvable — pas de post-it, rien d'écrit\n" % a.dossier)
        return 1
    liste = ouverts(a.dossier)
    if fichier not in liste:
        sortie.write("GARDE: %s n'est pas un chantier ouvert de %s (ouverts : %s) — rien d'écrit\n"
                     % (fichier, a.dossier, ", ".join(liste) or "aucun"))
        return 1
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(fichier + "\n")
    sortie.write("POSTIT %s — %s\n" % (fichier, a.dossier))
    return 0


def rangee_todo(lignes, code, titre=None):
    """(indice de l'en-tête `| # | Chantier`, indice de la rangée dont `` `code` `` est le premier code de la 2e
    cellule, son numéro) ; sans en-tête ou sans rangée, None à leur place (TAB4). Des repères peuvent le
    précéder (`| 1 | 🔴📅 `SCH` — …`, Cairn) : ratés, la clôture de SCH a gardé sa rangée (2026-10-14).
    `code` tout en chiffres : la rangée de ce numéro ; sinon, à défaut de code, la seule dont la 2e cellule est
    `titre` — une TODO sans codes (`| 10 | Finitions de l'API : erreurs et Swagger |`, Fil-Rouge) : ratée, la
    clôture de FIN l'a gardée (2026-10-14)."""
    tete = next((k for k, l in enumerate(lignes) if l.startswith("| # | Chantier")), None)
    if tete is None:
        return None, None, None
    pareil = lambda t: " ".join(t.replace("’", "'").split()).casefold()
    motif = r"^\|\s*(%s)\s*\|" % code if code.isdigit() else r"^\|\s*(\d+)\s*\|[^|`]*`%s`" % re.escape(code)
    par_titre = []
    for k in range(tete + 1, len(lignes)):
        if not lignes[k].startswith("|"):
            break
        m = re.match(motif, lignes[k])
        if m:
            return tete, k, m.group(1)
        m = re.match(r"^\|\s*(\d+)\s*\|([^|]*)\|", lignes[k])
        if titre and m and pareil(m.group(2)) == pareil(titre):
            par_titre.append((k, m.group(1)))
    return (tete,) + par_titre[0] if len(par_titre) == 1 else (tete, None, None)


def oter_rangee(lignes, tete, k, ajout):
    """Ôter la rangée `k` de la TODO et ajouter `ajout` à la phrase de provenance, la dernière ligne non vide
    au-dessus de l'en-tête `tete` — commun à `oter` et à `clore` (RTO1)."""
    p = tete - 1
    while p > 0 and not lignes[p].strip():
        p -= 1
    lignes[p] += ajout
    del lignes[k]


def ecrire_par_tmp(ecritures):
    """Écrire chaque `(chemin, contenu)` dans `chemin.tmp`, puis `os.replace` — commun à `oter` et à `clore`."""
    for chemin, contenu in ecritures:
        with open(chemin + ".tmp", "w", encoding="utf-8", newline="") as fh:
            fh.write(contenu)
        os.replace(chemin + ".tmp", chemin)


def todo_de_clore(chemin, code, titre, date, ecritures):
    """La TODO du fichier d'état `chemin` à la clôture de `code` : sa rangée ôtée et ` <n>, `<code>`, clos le
    <date>.` à la provenance, sans entrée au journal — la ligne d'archive dit la clôture ; ajoutée à `ecritures`.
    Rend la ligne à imprimer ; un code absent de la TODO (chantier hors TODO) n'écrit rien et n'est pas une GARDE
    (RTO1). Une TODO sans codes : la rangée au `titre` du chantier (`rangee_todo`)."""
    lignes = lignes_de(chemin) if os.path.isfile(chemin) else []
    tete, k, numero = rangee_todo(lignes, code, titre)
    if tete is None or k is None:
        return "TODO `%s` absente — rien ôté" % code
    oter_rangee(lignes, tete, k, " %s, `%s`, clos le %s." % (numero, code, date))
    ecritures.append((chemin, "\n".join(lignes) + "\n"))
    return "TODO `%s` ôtée · n° %s" % (code, numero)


def refus_d_oter(projet, carte_, code, lignes):
    """Le refus de `oter`, calculé avant toute écriture, ou None : TODO illisible, code absent de la TODO,
    chantier clos (« Lettres de fiche déjà prises ») ou ouvert (`courant_de`) — sa rangée, par code ou par titre
    (`rangee_todo`) —, journal absent (TAB4)."""
    try:
        todo_du_fichier(lignes)
    except ValueError as e:
        return "%s — rien écrit" % e
    k = rangee_todo(lignes, code)[1]
    if k is None:
        return "`%s` absent de la TODO — rien écrit" % code
    if code in lettres_prises(carte_):
        return "`%s` est un chantier clos (« %s ») — rien écrit" % (code, LETTRES)
    courant = courant_de(projet)
    fiches_ = lignes_du_projet(projet, courant, "fichier de fiches") if courant else []
    ids = [l.split()[1] for l in fiches_ if TITRE.match(l)]
    titre = next((re.sub(r"^# Chantier \S+ — ", "", l) for l in fiches_ if l.startswith("# ")), None)
    if ids and rangee_todo(lignes, lettre_de(ids[0]), titre)[1] == k:
        return "`%s` est le chantier ouvert (%s) — rien écrit" % (code, courant)
    if "## Journal des décisions" not in lignes:
        return "pas de « ## Journal des décisions » — rien écrit"
    return None


def cmd_oter(a, sortie):
    """Retirer la rangée `a.code` de la TODO : rangée ôtée, numéro marqué retiré dans la phrase de provenance,
    entrée datée au journal ; tout calculé avant d'écrire, puis `.tmp` et `os.replace` (TAB4)."""
    projet, date = a.projet, a.date or __import__("datetime").date.today().isoformat()
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    etat = champ(carte_, "fichier d'état")
    chemin = os.path.join(projet, etat) if etat else None
    if not chemin or not os.path.isfile(chemin):
        sortie.write("GARDE: fichier d'état introuvable : %s — rien écrit\n" % etat)
        return 1
    lignes = lignes_de(chemin)
    garde = refus_d_oter(projet, carte_, a.code, lignes)
    if garde:
        sortie.write("GARDE: %s\n" % garde)
        return 1
    tete, k, numero = rangee_todo(lignes, a.code)
    assert tete is not None and k is not None   # `refus_d_oter` a trouvé la rangée
    raison = a.raison.strip().rstrip(".")
    ecritures, quoi, prise = [], "retiré", ""
    # Un numéro (TODO sans codes, Fil-Rouge) : la rangée se nomme par son titre, et n'a pas de lettre à prendre.
    nomme = "« %s »" % lignes[k].split("|")[2].strip() if a.code.isdigit() else "`%s`" % a.code
    if a.fait and a.code.isdigit():
        quoi = "fait sans fiche"
    elif a.fait:    # fait sans fiche : sa lettre est prise, ceux qui l'attendent ne sont plus bloqués
        texte = "\n".join(carte_) + "\n"
        j = texte.find(LETTRES)
        if j < 0:
            sortie.write("GARDE: ligne « %s » absente de CHANTIER.md — rien écrit\n" % LETTRES)
            return 1
        m = re.match(r"^\|\s*\d+\s*\|\s*`[^`]+`\s*—\s*(.*?)\s*\|", lignes[k])
        fin = fin_lettres(texte, j)
        texte = texte[:fin] + ", %s (%s, sans fiche)" % (a.code, m.group(1) if m else a.code) + texte[fin:]
        ecritures.append((os.path.join(projet, "CHANTIER.md"), texte))
        quoi, prise = "fait sans fiche", " · lettre prise"
    oter_rangee(lignes, tete, k, " %s, %s, %s le %s : %s." % (numero, nomme, quoi, date, raison))
    while lignes and not lignes[-1].strip():
        lignes.pop()
    lignes += ["", "## %s — %s %s, retiré de la TODO (n° %s)" % (date, nomme, quoi, numero) if a.fait
               else "## %s — %s retiré de la TODO (n° %s)" % (date, nomme, numero), "", "- **Raison** : %s." % raison]
    ecrire_par_tmp([(chemin, "\n".join(lignes) + "\n")] + ecritures)
    sortie.write("OTÉ %s · n° %s · provenance marquée · journal %s — %s%s\n" % (nomme, numero, date, etat, prise))
    return 0


def refus_de_clore(projet, carte_, courant, fiches_, ids):
    """Le refus de `clore`, calculé avant toute écriture, ou None : aucune fiche, déjà **CLOS**, ou une TODO
    du fichier d'état que `todo_du_fichier` refuse — la feuille la relirait après les écritures (TAB3)."""
    if not ids:
        return "aucune fiche dans %s" % courant
    if any(l.startswith("**CLOS**") for l in fiches_):
        return "%s porte déjà **CLOS**" % courant
    etat = champ(carte_, "fichier d'état")
    if etat and os.path.isfile(os.path.join(projet, etat)):
        try:
            todo_du_fichier(lignes_de(os.path.join(projet, etat)))
        except ValueError as e:
            return "%s — rien écrit" % e
    return None


def cmd_clore(a, sortie):
    """Clore le chantier courant de `a.projet` : les écritures mécaniques de `cloture.md`, décrites à `clore` dans la
    docstring de `vlp.py`."""
    projet, date = a.projet, a.date or __import__("datetime").date.today().isoformat()
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    chemin_carte = os.path.join(projet, "CHANTIER.md")
    carte_ = lignes_de(chemin_carte)
    courant = courant_de(projet)
    if not courant:
        sortie.write("GARDE: aucun chantier ouvert — rien à clore\n")
        return 1
    chemin_fiches = os.path.join(projet, courant)
    fiches_ = lignes_du_projet(projet, courant, "fichier de fiches")
    ids = [l.split()[1] for l in fiches_ if TITRE.match(l)]
    garde = refus_de_clore(projet, carte_, courant, fiches_, ids)
    if garde:
        sortie.write("GARDE: %s\n" % garde)
        return 1
    lettre = lettre_de(ids[0])
    titre = next((re.sub(r"^# Chantier \S+ — ", "", l) for l in fiches_ if l.startswith("# ")), courant)
    url = champ(carte_, "artefact du chantier", "aucun")
    fait = "%s..%s" % bornes(ids) + (" (%s)" % a.abandon if a.abandon else "")
    # L'estimé de l'ouverture, relu ici pour être écrit à côté du réel (chantier EST).
    estime = next((m for m in map(ESTIME.match, fiches_) if m), None)
    joue = sum(1 for l in fiches_ if TITRE.match(l) and l.split()[2] == "[x]")

    # 1. le fichier de fiches
    entete = [CLOS_LIGNE % date] + (["", "Abandonnées : %s." % a.abandon.rstrip(".")] if a.abandon else []) + [""]
    ligne_fait = "**Fait.** %s..%s (%s) : %s" % (bornes(ids) + (date, (a.fait or a.livre).rstrip(".")))  + "."
    i = next((k for k, l in enumerate(fiches_) if l.startswith(("**Fait.**", "**Où on en est.**"))), None)
    if i is None:
        i = next(k for k, l in enumerate(fiches_) if l.startswith("# ")) + 2
        fiches_[i:i] = entete + [ligne_fait, ""]
    else:
        fin_para = i
        while fin_para + 1 < len(fiches_) and fiches_[fin_para + 1].strip():
            fin_para += 1
        fiches_[i:fin_para + 1] = entete + [ligne_fait]
    k_fait = i + len(entete)
    gardes, ecritures, faits = [], [], {"routage": 0, "index": 0, "archivé": 0, "bilan": 0}
    nom = os.path.basename(courant)
    total_mesure = None     # le total que `regenerer` écrit sur la page, en 1 ter (chantier UNI)

    # 1 bis. l'index et le routage de CLAUDE.md passent à « clos »
    index = champ(carte_, "index")
    chemin_index = os.path.join(projet, index) if index else None
    if not chemin_index or not os.path.isfile(chemin_index):
        gardes.append("index introuvable : %s" % index)
    else:
        idx = lignes_de(chemin_index)
        avant = list(idx)
        k = next((k for k, l in enumerate(idx) if l.startswith("| `%s` |" % nom) and "**ouvert**" in l), None)
        if k is None:
            gardes.append("ligne ouverte de %s absente de l'index" % nom)
        else:
            m = re.search(r"« (.*) »", idx[k])
            idx[k] = "| `%s` | on relit le socle du chantier %s — **clos** « %s », `%s..%s` |" % (
                (nom, lettre, m.group(1) if m else titre) + bornes(ids))
            faits["index"] = 1
        # les lignes clos quittent l'index pour l'archive (chantier IDX)
        chemin_arch = os.path.join(projet, chemin_archive(index))
        arch = lignes_de(chemin_arch) if os.path.isfile(chemin_arch) else None
        idx, narch, faits["archivé"] = archiver(idx, arch, os.path.basename(chemin_arch))
        if idx != avant:
            ecritures.append((chemin_index, "\n".join(idx) + "\n"))
        if narch is not None and narch != arch:
            ecritures.append((chemin_arch, "\n".join(narch) + "\n"))
    chemin_claude = os.path.join(projet, "CLAUDE.md")
    if not os.path.isfile(chemin_claude):
        gardes.append("CLAUDE.md introuvable")
    else:
        cl = lignes_de(chemin_claude)
        k = next((k for k, l in enumerate(cl) if l.startswith("| jouer une fiche du chantier %s (" % lettre)
                  and "`%s`" % courant in l), None)
        if k is None:
            gardes.append("ligne « jouer une fiche du chantier %s » absente de CLAUDE.md" % lettre)
        else:
            del cl[k]
            if rang_routage_clos(cl) is None:
                cl.insert(k, "%s `%s` — sa ligne y nomme le fichier de fiches |" % (ROUTAGE_CLOS, chemin_archive(index or "00-INDEX.md")))
            faits["routage"] = 1
        if a.resume:
            if resume_claude(cl, lettre, a.resume, date, gardes):
                faits["résumé"] = 1
        if faits["routage"] or faits.get("résumé"):
            ecritures.append((chemin_claude, "\n".join(cl) + "\n"))

    # 1 ter. la ZONE:bilan de la page du chantier, recopiée depuis le .md (chantier ABR)
    chemin_page = os.path.join(projet, os.path.dirname(courant), "artefacts", nom[:-3] + ".html")
    md_page = parts_page = None
    if not os.path.isfile(chemin_page):
        total_mesure = total_sans_page(carte_, chemin_page, chemin_fiches, gardes)
    else:
        pg = lire(chemin_page)
        try:
            d, f = zone(pg, "bilan", "\n", "  </section>")
            db, fb = zone(pg, "blocage", "\n", "  </section>")
        except ValueError as e:
            gardes.append("page du chantier : %s" % e)
        else:
            md_page = chemin_abri(chemin_page)
            parts_page = lire_abri(md_page) if os.path.exists(md_page) else abri_de_page(pg)
            # Le bilan final n'est écrit dans le .md qu'une fois l'estimé connu (1 quater) — jamais
            # avec le marqueur `ESTIME_A_ECRIRE` (mutant : l'écrire ici le laisserait dans le .md).
            parts_page["bilan"] = ["Livré : %s" % a.livre] + (["Surpris : %s" % a.surpris] if a.surpris else []) \
                + ["Estimé : %s" % ESTIME_A_ECRIRE]
            corps = ('  <section>\n    <h2>Chantier clos le %s</h2>\n    <div class="bilan">\n' % date
                     + "".join("      <p>%s</p>\n" % esc(t) for t in parts_page["bilan"]) + "    </div>\n")
            bloc = pg[db:fb]
            bloc = re.sub(r"^  <section>", "  <section hidden>", bloc, count=1)
            pg = pg[:db] + bloc + pg[fb:d] + corps + pg[f:] if db < d else pg[:d] + corps + pg[f:db] + bloc + pg[fb:]
            pg = bilan_en_haut(pg)
            couts_page = []    # les gardes de regenerer portent déjà « GARDE: »
            try:
                pg, _, _, total_mesure, _ = noyau.page.regenerer(pg, chemin_fiches, parts_page, date, couts_page)
            except ValueError as e:
                couts_page.append("page du chantier : coûts non régénérés — %s" % e)
            gardes.extend(re.sub(r"^GARDE: ", "", g) for g in couts_page)
            ecritures.append((chemin_page, pg))
            faits["bilan"] = 1

    # 1 quater. l'estimé à côté du réel : page, `.md`, `**Fait.**`, ligne CLOS (chantier EST)
    # Le prix mesuré, le pondéré de la page (chantier TAU ; plus la louche à tant par million).
    prix = total_mesure[2] if total_mesure and total_mesure[0] else None
    reel = "cadré %d · joué %d fiches %s" % (len(ids), joue, dollars(prix))
    texte_estime = ("estimé %s fiches %s" % estime.groups() if estime else "estimé non noté") + " · " + reel
    fiches_[k_fait] = ligne_fait[:-1] + " — " + texte_estime + "."
    ecritures = [(c, t.replace(ESTIME_A_ECRIRE, esc(texte_estime), 1) if c == chemin_page else t) for c, t in ecritures]
    if md_page is not None and parts_page is not None:
        parts_page["bilan"][-1] = "Estimé : %s" % texte_estime
        ecritures.append((md_page, texte_abri(parts_page)))

    # 1 quinquies. la rangée du chantier quitte la TODO, écrite avec le reste, avant la feuille qui la relit (RTO1)
    todo_dit = todo_de_clore(os.path.join(projet, champ(carte_, "fichier d'état") or ""), lettre, titre, date, ecritures)

    # 2. CHANTIER.md
    for k, l in enumerate(carte_):
        m = re.match(r"^(\s*-\s*\*\*artefact du chantier\*\*\s*:\s*)", l)
        if m:
            carte_[k] = m.group(1) + "aucun"
    texte = "\n".join(carte_) + "\n"
    j = texte.find(LETTRES)
    if j < 0:
        sortie.write("GARDE: ligne « Lettres de fiche déjà prises » absente de CHANTIER.md\n")
        return 1
    if lettre not in lettres_prises(carte_):
        k = fin_lettres(texte, j)
        texte = texte[:k] + ", %s (%s)" % (lettre, titre) + texte[k:]

    # 3. la feuille de route
    page = page_feuille(projet)
    html = lire(page) if os.path.isfile(page) else None
    archive = page_clos(projet)     # la ligne close va à l'archive si elle existe (chantier ARC)
    clos_html = html if archive == page else lire(archive)
    total = None
    # Un seul chiffre (chantier UNI) : le total de la page, sinon --tokens ; --tokens différent
    # du mesuré n'est qu'un contrôle, qui le dit.
    total_chantier = total_mesure[0] if total_mesure and total_mesure[0] else a.tokens
    ecart = bool(total_mesure and total_mesure[0]) and a.tokens is not None and a.tokens != total_chantier
    if html is not None and clos_html is not None:
        try:
            d, f = zone(clos_html, "clos", "<tbody>\n", "        </tbody>")
        except ValueError as e:
            sortie.write("GARDE: %s\n" % e)
            return 1
        anciens = lignes_clos(clos_html[d:f])
        lien = cellule_md(titre) if url.lower().startswith("aucun") else '<a href="%s">%s</a>' % (esc(url), cellule_md(titre))
        ligne = ('          <tr>\n            <td>%s <span class="badge" data-etat="clos">clos</span></td>\n'
                 '            <td class="mono">%s</td><td class="mono">%s</td>\n'
                 '            <td class="mono">%s</td>\n            <td>%s</td>\n          </tr>\n'
                 % (lien, plage(ids), date, "non mesuré" if total_chantier is None
                    else ("" if prix is None else dollars(prix) + " · ") + arrondi(total_chantier),
                    cellule_md(a.livre)))
        corps = ligne + "".join(anciens)
        clos_html = clos_html[:d] + corps + clos_html[f:]
        total = total_clos(corps)
        usd_corps, n_usd_corps = prix_clos(corps)
        clos_html = resommer(clos_html, len(anciens) + 1, total, usd_corps, n_usd_corps)
        html = clos_html if archive == page else html
        etat = champ(carte_, "fichier d'état")
        try:
            zone_todo(html)
            zone(html, "encours", "\n", "  </section>")
            if not etat or not os.path.isfile(os.path.join(projet, etat)):
                raise ValueError("fichier d'état introuvable : %s" % etat)
        except ValueError as e:
            sortie.write("GARDE: %s — rien d'écrit\n" % e)
            return 1

    with open(chemin_fiches, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(fiches_) + "\n")
    with open(chemin_carte, "w", encoding="utf-8", newline="") as fh:
        fh.write(texte)
    # Le post-it du dossier ne nomme plus un chantier clos (NUI23) ; celui d'un autre chantier reste.
    p = postit(projet)
    if p and os.path.isfile(p) and lire(p).strip() == courant:
        os.remove(p)
    ecrire_par_tmp(ecritures + ([(archive, clos_html)] if html is not None and archive != page and clos_html is not None
                                else []))
    coeur.ordre_de_clore(todo_dit, sortie, carte_)
    coeur.dire_sans_page(carte_, [(chemin_page, "artefact du chantier", "la page du chantier"),
                            (page, "artefact feuille de route", "la feuille de route")], sortie, gardes)
    if html is None:
        sortie.write("".join("GARDE: %s\n" % g for g in coeur.garde_page(
            carte_, "artefact feuille de route", "feuille de route introuvable : %s — CHANTIER.md et fiches écrits" % page)))
    else:
        try:
            html, bilan = feuille(projet, html, None, date)
        except ValueError as e:
            sortie.write("GARDE: %s — CHANTIER.md et fiches écrits, feuille non écrite\n" % e)
            return 1
        attentes_de_nuit(projet, [(chemin_page, url), (page, champ(carte_, "artefact feuille de route", "aucune"))],
                         sortie)
        if archive != page and clos_html is not None:
            # l'archive se publie en fin de séance, par la liste d'attente (chantier ARC)
            url_archive = champ(lignes_de(chemin_carte), "artefact archive", "aucune")
            html = poser_bloc_archive(html, clos_html, url_archive)
            if url_archive.lower().startswith("aucun"):
                sortie.write("GARDE: archive sans URL — publier %s, puis « vlp.py archive %s --url <URL> »\n"
                             % (archive, projet))
            else:
                noter_attentes(projet, [(archive, url_archive)], sortie)
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(html)
        joints = recopier_joints(os.path.dirname(os.path.abspath(page)))
        joints.update(ecrire_couts(page, html, couts_du_projet(projet, html)))
        sortie.write(ligne_files(joints) + ligne_lire(joints))
        sortie.write(bilan + " · réécrite — %s\n" % page)
    if ecart:
        sortie.write("ÉCART tokens %s donné · %s mesuré — le mesuré fait foi\n"
                     % (milliers(a.tokens), milliers(total_chantier)))
    champ_chantier = "non mesuré" if total_chantier is None else milliers(total_chantier)
    sortie.write("CLOS %s %s · chantier %s · cumul %s · routage %d · index %d · archivé %d · bilan %d%s · %s — %s\n" % (
        lettre, fait, champ_chantier, "non mesuré" if total is None else milliers(total), faits["routage"], faits["index"],
        faits["archivé"], faits["bilan"],
        " · résumé %d" % faits.get("résumé", 0) if a.resume else "", texte_estime, projet))
    # Clos dans un worktree hors de la principale : la ligne qui le fusionne, à lancer depuis elle (NUI26). La nuit
    # ne la lit pas : `matin` fusionne ses branches.
    dossier_principal, principale = principal(projet)
    code, ici = noyau.relecture.git_texte(["symbolic-ref", "--short", "-q", "HEAD"], projet)
    if os.environ.get("VLP_NUIT") != "1" and dossier_principal and principale and code == 0 \
            and ici.strip() != principale:
        sortie.write('FUSIONNER depuis %s : "%s" "%s" fusionner "%s" %s\n' % (
            dossier_principal, sys.executable, VLP_PY, dossier_principal, ici.strip()))
    return 0
