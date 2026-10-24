"""Extraire, socle, valider ; cocher, commiter, refuser une fiche (REF45 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import argparse
import fnmatch
import os
import re

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (FERMANT, SESSION, TITRE, lignes_de, lire)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF45 — `tete_de_fiche`, `chemins_du_statut`, `partage_commit` — se lisent ici seulement.
__all__ = [
    "extraire_lignes",
    "socle_lignes",
    "cmd_extraire",
    "cmd_socle",
    "VLP_PY",
    "cmd_lire",
    "cmd_cocher",
    "chemins_changes",
    "releve",
    "croisent",
    "deplie",
    "cmd_commiter",
    "garde_avant_coche",
    "noter_session",
    "REFUS_SOLDES",
    "TETE_OUVERTE",
    "refus_du_bloc",
    "bloc_solde",
    "refuser",
    "OUVRANT",
    "CRITERE",
    "MARQUE_VISUELLE",
    "CRITERE_VISUEL",
    "ARRET",
    "CODE_EN_LIGNE",
    "SEUIL_FICHE",
    "SEUIL_SOCLE",
    "SEUIL_CLAUDE",
    "SEUIL_CHANTIER",
    "SEUIL_INDEX",
    "CLOS_GARDES",
    "valider_lignes",
    "cmd_valider",
    "cmd_valider_seul",
    "rapport",
]


# --- extraire, socle, sessions -----------------------------------------------

def extraire_lignes(lignes, fiche):
    """(lignes de la fiche, garde ou None). Liste vide : fiche absente."""
    ouvrant = "<!-- FICHE:%s -->" % fiche
    debut = next((i for i, l in enumerate(lignes) if l.strip() == ouvrant), None)
    if debut is not None:
        # Un fermant oublié : `sed` avalait la fiche suivante sans rien dire.
        # On s'arrête au prochain marqueur ouvrant, et on le dit.
        fin = next((i for i in range(debut + 1, len(lignes))
                    if lignes[i].strip() == FERMANT or lignes[i].startswith("<!-- FICHE:")), len(lignes))
        if fin == len(lignes) or lignes[fin].strip() != FERMANT:
            return lignes[debut:fin], "GARDE: marqueur fermant absent après %s — fiche lue jusqu'au marqueur suivant ou la fin" % ouvrant
        return lignes[debut:fin + 1], None
    titre = "## %s " % fiche
    debut = next((i for i, l in enumerate(lignes) if l.startswith(titre)), None)
    if debut is None:
        return [], None
    fin = next((i for i in range(debut + 1, len(lignes)) if lignes[i].rstrip() == "---"), len(lignes) - 1)
    return lignes[debut:fin + 1], "GARDE: pas de marqueurs pour %s — repli du titre au premier '---', un '---' dans un bloc de code le coupe" % fiche


def socle_lignes(lignes):
    debut = next((i for i, l in enumerate(lignes) if l.startswith("## Le socle")), None)
    if debut is None:
        return []
    fin = next((i for i in range(debut + 1, len(lignes)) if re.match(r"^## L.*ordre des fiches", lignes[i])), len(lignes))
    return lignes[debut:fin]


def cmd_extraire(chemin, fiche, sortie):
    extrait, garde = extraire_lignes(lignes_de(chemin), fiche)
    if garde:
        sortie.write(garde + "\n")
    if not extrait:
        sortie.write("GARDE: fiche introuvable : %s\n--- fiche, lignes : 0\n" % fiche)
        return 1
    sortie.write("\n".join(extrait) + "\n")
    if any(CRITERE_VISUEL.match(l) for l in extrait):
        # Le sous-agent de /vlp:enchainer a rendu FAITE sur une fiche visuelle (P3) :
        # la consigne vient du script, pas de sa mémoire. Pas GARDE: — vlp:jouer
        # rendrait RETOUR avant tout travail.
        sortie.write(ARRET + "\n")
    sortie.write("--- fiche, lignes : %d\n" % len(extrait))
    return 0


def cmd_socle(chemin, sortie):
    extrait = socle_lignes(lignes_de(chemin))
    if extrait:
        sortie.write("\n".join(extrait) + "\n")
    sortie.write("--- socle, lignes : %d\n" % len(extrait))
    return 0 if extrait else 1


VLP_PY = os.path.join(etat.KIT, "scripts", "vlp.py")   # le lanceur : les commandes qu'on affiche le nomment (VIT5)


def cmd_lire(chemins, sortie):
    """Un `cat` d'un fichier du kit est hors du projet : PowerShell le refuse
    (chantier U). Python, lui, est permis par `allowed-tools`. `${CLAUDE_PLUGIN_ROOT}`, que seules les commandes
    voient remplacé, devient la racine du kit en barres obliques : recopiée, la ligne se lance (REF27)."""
    racine = os.path.realpath(etat.KIT)
    code, disque = 0, os.path.normcase(os.path.splitdrive(racine)[0])  # commonpath lève entre deux disques (REF55)
    for c in chemins:
        vrai = os.path.realpath(os.path.join(racine, c))
        if os.path.normcase(os.path.splitdrive(vrai)[0]) != disque or os.path.commonpath([racine, vrai]) != racine:
            sortie.write("GARDE: hors du kit : %s\n" % c)
            code = 1
        elif not os.path.isfile(vrai):
            sortie.write("ABSENT %s\n" % c)
            code = 1
        else:
            texte = lire(vrai).replace("${CLAUDE_PLUGIN_ROOT}", racine.replace("\\", "/"))
            sortie.write(texte if texte.endswith("\n") else texte + "\n")
    return code


def cmd_cocher(a, sortie):
    """La coche et la ligne Session en une écriture : l'id vient de
    l'environnement, pas d'un `$env:` que PowerShell refuse (chantier U)."""
    lignes = lignes_de(a.fichier)
    titre = "## %s [" % a.fiche
    debut = next((i for i, l in enumerate(lignes) if l.startswith(titre)), None)
    if debut is None:
        sortie.write("GARDE: fiche introuvable : %s\n" % a.fiche)
        return 1
    if a.verifier:
        cocher = lignes[debut].startswith("## %s [x]" % a.fiche)
        sortie.write("CASE %s [%s]\n" % (a.fiche, "x" if cocher else " "))
        # La tête du dépôt (chantier REV) : un dernier commit qui nomme la fiche est celui du
        # sous-agent — `VAL1:` compris, que `COMMIT_FICHE` laisse passer.
        dossier = os.path.dirname(os.path.abspath(a.fichier))
        if noyau.relecture.git_texte(["rev-parse", "--git-dir"], dossier)[0] != 0:
            sortie.write("SANS GIT\n")
            return 0 if cocher else 1
        code, tete = noyau.relecture.git_texte(["log", "-1", "--format=%h %s"], dossier)
        ligne = tete_de_fiche(a.fiche, tete if code == 0 else "")
        if ligne:
            sortie.write(ligne)
            return 1
        return 0 if cocher else 1
    if a.refuser is not None:
        return refuser(a, lignes, debut, sortie)
    if a.session is not None or a.role:
        return noter_session(a, lignes, debut, sortie)
    garde = garde_avant_coche(a, lignes[debut])
    if garde:
        sortie.write(garde)
        return 1
    fin = next((i for i in range(debut + 1, len(lignes))
                if lignes[i].strip() == FERMANT or TITRE.match(lignes[i])), len(lignes))
    lignes[debut] = lignes[debut].replace("[ ]", "[x]", 1)
    if a.resolu:
        t = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Tentatives**")), None)
        if t is not None:
            n = next((i for i in range(t + 1, fin) if not lignes[i].strip() or lignes[i].startswith("**")), fin)
            date = a.date or __import__("datetime").date.today().isoformat()
            avant = len(lignes)
            lignes[t:n] = bloc_solde(lignes[t:n], date, a.resolu)
            fin += len(lignes) - avant
    s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if s and "**Session** : %s" % s not in lignes[debut:fin]:
        dep = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Dépend de**")), debut + 1)
        lignes.insert(dep, "**Session** : %s" % s)
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("COCHÉ %s · Session %s\n" % (a.fiche, s or "absente"))
    return 0


def tete_de_fiche(fiche, tete):
    """La ligne `TÊTE <sha> <sujet>` si `tete` — la sortie de `git log -1 --format="%h %s"` — est un commit qui nomme
    `fiche` (`<fiche> :`, celui d'un sous-agent), sinon None. Ne lance rien (REF45)."""
    sha, _, sujet = tete.strip().partition(" ")
    return "TÊTE %s %s\n" % (sha, sujet) if re.match(r"%s\s*:" % re.escape(fiche), sujet) else None


def chemins_changes(racine):
    """Les chemins que `git status` dit changés sous `racine` (`chemins_du_statut`) ; None hors Git."""
    code, texte = noyau.relecture.git_texte(["status", "--porcelain", "-z", "--untracked-files=all"], racine)
    return chemins_du_statut(texte) if code == 0 else None


def chemins_du_statut(texte):
    """Les chemins d'une sortie de `git status --porcelain -z` — suivis ou non, un par fichier, relatifs à la racine du
    dépôt ; `-z` : ni guillemets ni échappement, l'ancien nom d'un renommage sauté. Ne lance rien (REF45)."""
    rendu, morceaux = [], iter(texte.split("\0"))
    for m in morceaux:
        if len(m) > 3:
            rendu.append(m[3:])
            if m[0] in "RC":
                next(morceaux, None)
    return rendu


def releve(chemin, nom):
    """Vrai si `chemin` (relatif au dépôt, en `/`) relève de `nom`, lu sur une ligne **Fichiers** : égal, sous ce
    dossier, ou pris par son motif — `{a,b}` déplié, puis `*`, `?`, `[…]` par `fnmatch`, où `*` passe aussi les `/`
    (ENA5). Un motif sans lettre (`*` d'un italique) ne prend rien."""
    accolade = re.search(r"\{([^{}]*)\}", nom)
    if accolade:
        return any(releve(chemin, nom[:accolade.start()] + choix + nom[accolade.end():])
                   for choix in accolade.group(1).split(","))
    nom = nom.rstrip("/")
    return chemin == nom or chemin.startswith(nom + "/") or (
        bool(re.search(r"[*?[]", nom)) and bool(re.search(r"\w", nom)) and fnmatch.fnmatchcase(chemin, nom))


def croisent(uns, autres):
    """Vrai si deux ensembles de chemins, tels qu'écrits sur des lignes **Fichiers**, peuvent viser un même fichier
    (ENA5) — dans le doute, oui : `lancables` en fait un `INDICE:` (ISO3). `{a,b}` se déplie. Deux
    chemins à `/` : égaux, l'un sous le dossier de l'autre, ou, s'il y a un motif, leurs parts littérales (avant le
    premier `*?[`) dont l'une commence l'autre. Un nom seul (`vlp.py`) peut vivre dans tout dossier : il croise un
    dossier, et un chemin dont le dernier nom le prend ou qu'il prend (`fnmatch`) ; deux derniers noms à motif aussi."""
    motif = re.compile(r"[*?[]")

    def peut(x, y):
        """Vrai si `x` et `y`, sans accolade, peuvent viser un même fichier."""
        if "/" in x and "/" in y:
            if not motif.search(x) and not motif.search(y):
                return releve(x, y) or releve(y, x)
            px, py = (motif.split(n, 1)[0] for n in (x, y))
            return px.startswith(py) or py.startswith(px)
        if x.endswith("/") or y.endswith("/"):
            return True
        bx, by = x.rsplit("/", 1)[-1], y.rsplit("/", 1)[-1]
        return bool(motif.search(bx) and motif.search(by)) or fnmatch.fnmatchcase(bx, by) or fnmatch.fnmatchcase(by, bx)
    return any(peut(a, b) for x in uns for y in autres for a in deplie(x) for b in deplie(y))


def deplie(nom):
    """Les noms que les accolades de `nom` désignent : `a/{b,c}.py` → `a/b.py`, `a/c.py`."""
    accolade = re.search(r"\{([^{}]*)\}", nom)
    if not accolade:
        return [nom]
    return [n for choix in accolade.group(1).split(",") for n in deplie(nom[:accolade.start()] + choix + nom[accolade.end():])]


def cmd_commiter(a, sortie):
    """Commiter une fiche par ses seuls fichiers (ENA4) : la cocher si sa case est vide (`cmd_cocher`, ses gardes
    comprises), puis ajouter à l'index ses chemins changés — ceux de sa ligne **Fichiers**, un dossier y valant ce qu'il
    contient, un motif ce qu'il prend (`releve`) — et les communs : le fichier de fiches, `scripts/sante-base.json` dans le kit ;
    jamais `git add -A` : en parallèle, il avalerait le travail d'une autre fiche. Un changé hors de sa liste : `HORS:`,
    laissé hors du commit. Limite : un commun porte aussi ce qu'une autre fiche y a écrit — sa case, son bloc
    **Tentatives**, ses empreintes."""
    lignes = lignes_de(a.fichier)
    fiche = next((f for f in coeur.fiches_du_fichier(lignes) if f[0] == a.fiche), None)
    racine = noyau.relecture.git_texte(["rev-parse", "--show-toplevel"], os.path.dirname(os.path.abspath(a.fichier)))
    changes = chemins_changes(racine[1].strip()) if racine[0] == 0 else None
    if fiche is None or changes is None:
        sortie.write("GARDE: commiter veut une fiche du fichier, dans un dépôt Git : %s %s\n" % (a.fichier, a.fiche))
        return 1
    if not fiche[2] and cmd_cocher(argparse.Namespace(fichier=a.fichier, fiche=a.fiche, verifier=False, refuser=None,
                                                      session=None, role=None, resolu=None, date=None), sortie):
        return 1
    racine = racine[1].strip()
    # Communs : chaque fiche coche le fichier de fiches, et, dans le kit seul, réécrit la base du cliquet (`sante --base`).
    communs = {os.path.relpath(os.path.abspath(a.fichier), racine).replace(os.sep, "/")}
    if coeur.est_kit(racine):
        communs.add("scripts/sante-base.json")
    ajout, hors = partage_commit(lignes, a.fiche, communs, changes, chemins_changes(racine) or [])
    if hors:
        sortie.write("HORS: %s — changés hors de la ligne Fichiers de %s, laissés hors du commit\n" % (", ".join(hors), a.fiche))
    # Sans chemin, `git add -A --` ajouterait tout le dépôt : l'ajout se saute.
    etapes = ([["add", "-A", "--"] + ajout] if ajout else []) + [
        ["commit", "--allow-empty", "-q", "-m", "%s : %s" % (a.fiche, fiche[1])]]
    for etape in etapes:
        code, texte = noyau.relecture.git_texte(etape, racine)
        if code != 0:
            sortie.write("GARDE: git %s : %s\n" % (etape[0], texte.strip()))
            return 1
    sortie.write("COMMIT %s : %s · %d fichier(s)\n" % (a.fiche, fiche[1], len(ajout)))
    return 0


def partage_commit(lignes, fiche, communs, avant, apres):
    """(ajout, hors) du commit de `fiche` : `ajout`, les changés d'`apres` (le statut relu après la coche) qui sont
    communs ou relèvent de sa ligne **Fichiers** ; `hors`, les changés d'`avant` (le statut d'avant la coche) laissés
    dehors. Ne lance rien (REF45)."""
    debut = next(i for i, l in enumerate(lignes) if l.startswith("## %s [" % fiche))
    fin = next((i for i in range(debut + 1, len(lignes)) if TITRE.match(lignes[i])), len(lignes))
    # Un motif ne se lit qu'entre backticks : `**kit**` de la prose prendrait tout chemin qui contient « kit » (ENA5).
    cites = set(re.findall(r"`([^`]+)`", coeur.texte_fichiers(lignes[debut:fin])))
    siens = {n for n in coeur.noms_fichiers(lignes[debut:fin]) if n in cites or not re.search(r"[*?[{]", n)}
    ajout = [c for c in apres if c in communs or any(releve(c, n) for n in siens)]
    return ajout, [c for c in avant if c not in ajout]


def garde_avant_coche(a, titre):
    """Rendre la `GARDE:` qui empêche de cocher `a.fiche` — déjà cochée, ou, dans le kit, sans suite entière verte sur
    le code d'aujourd'hui (VIT11) —, ou `None`."""
    if not titre.startswith("## %s [ ]" % a.fiche):
        return "GARDE: %s déjà cochée — rien écrit\n" % a.fiche
    kit = coeur.suite_manquante(a.fichier)
    if kit:
        return ("GARDE: %s non cochée — la suite entière n'a pas tourné verte sur le code d'aujourd'hui : "
                "uv run --frozen pytest -n 4, depuis %s, puis cocher (VIT11)\n" % (a.fiche, kit))
    return None


def noter_session(a, lignes, debut, sortie):
    """`cocher --session <uuid> [--role R]` (chantier NUI) : la session d'un rôle de la nuit — le
    relecteur, le clos — que la boucle, et non la session elle-même, connaît. `**Session** : <uuid>
    (<rôle>)`, fiche cochée ou non, jamais doublée ; après les lignes Session de la fiche, sinon
    avant `**Dépend de**`. `--role clore` : dans l'en-tête, avant le premier `## `, comme `ouvrir`."""
    if not (a.session or "").strip() or not a.role or re.search(r"[()\s]", a.session + a.role):
        sortie.write("GARDE: --session <uuid> --role <rôle>, sans espace ni parenthèse\n")
        return 1
    ligne = "**Session** : %s (%s)" % (a.session, a.role)
    fin = next((i for i in range(debut + 1, len(lignes))
                if lignes[i].strip() == FERMANT or TITRE.match(lignes[i])), len(lignes))
    if a.role == "clore":
        zone = range(0, next((i for i, l in enumerate(lignes) if TITRE.match(l)), len(lignes)))
    else:
        zone = range(debut + 1, fin)
    if any(lignes[i] == ligne for i in zone):
        sortie.write("DÉJÀ %s · %s\n" % (a.fiche, ligne))
        return 0
    if a.role == "clore":
        k = next((k for k, l in enumerate(lignes) if l.startswith("## ")), debut)
        lignes[k:k] = [ligne, ""]
    else:
        vues = [i for i in zone if SESSION.match(lignes[i])]
        dep = next((i for i in zone if lignes[i].startswith("**Dépend de**")), debut + 1)
        lignes.insert(vues[-1] + 1 if vues else dep, ligne)
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("NOTÉ %s · %s\n" % (a.fiche, ligne))
    return 0


# Les refus de relecture soldés d'un bloc Tentatives, sur une ligne à eux sous la tête (ENA7) : aucun texte libre
# (motif, `--resolu`) ne partage une ligne avec un compte, il s'y lirait comme un compte. La tête est ouverte si son
# premier « résolu » est « non résolu » : le texte de `--resolu` ne vient qu'après « résolu par : ».
REFUS_SOLDES = re.compile(r"Refus soldés : ([0-9]+)(?: · dernier : (.*))?$")
TETE_OUVERTE = re.compile(r"\*\*Tentatives\*\*(?:(?!résolu).)*non résolu")


def refus_du_bloc(bloc):
    """Les refus de relecture d'un bloc **Tentatives** (`bloc` : ses lignes, tête comprise), dont le rang survit à
    `--resolu` (ENA7) : `(rang, motif, soldes)` — `soldes`, l'indice dans `bloc` de sa ligne
    `Refus soldés : <p>[ · dernier : <m>]`, ou None ; `rang`, `p` plus les lignes numérotées `ESSAI_REFUSE` ;
    `motif`, la ligne `Erreur :` si la dernière ligne numérotée est un refus (un blocage l'écrase), sinon `m`."""
    soldes = next((i for i in range(1, len(bloc)) if REFUS_SOLDES.match(bloc[i])), None)
    vu = REFUS_SOLDES.match(bloc[soldes]) if soldes else None
    essais = [l.split(". ", 1)[1] for l in bloc[1:] if re.match(r"[0-9]+\. ", l)]
    erreur = next((l[len("Erreur :"):].strip() for l in bloc[1:] if l.startswith("Erreur :")), None)
    motif = erreur if essais and essais[-1] == coeur.ESSAI_REFUSE else None
    return (int(vu.group(1)) if vu else 0) + essais.count(coeur.ESSAI_REFUSE), motif or (vu.group(2) if vu else None), soldes


def bloc_solde(bloc, date, resolu):
    """Ce qui remplace un bloc **Tentatives** à la fiche cochée (`cocher --resolu`) : la tête `résolu par`, puis, s'il
    portait des refus de relecture, leur ligne `Refus soldés : <n> · dernier : <motif>`, que `refuser` relit (ENA7)."""
    rang, motif, _ = refus_du_bloc(bloc)
    soldes = ["Refus soldés : %d" % rang + (" · dernier : %s" % motif if motif else "")] if rang else []
    return ["**Tentatives** (%s) — résolu par : %s" % (date, resolu)] + soldes


def refuser(a, lignes, debut, sortie):
    """Le refus du relecteur (chantier REV) : la case rouverte, et sous le titre le bloc de
    `tache-blocage.md` — déjà là, il gagne la ligne numérotée suivante et son `Erreur :` prend
    le nouveau motif ; il ne se double jamais. Une tête soldée redevient `— non résolu.`, sa ligne
    `Refus soldés` gardée : le rang la compte, et la sortie redit son dernier motif (ENA7)."""
    fin = next((i for i in range(debut + 1, len(lignes))
                if lignes[i].strip() == FERMANT or TITRE.match(lignes[i])), len(lignes))
    lignes[debut] = lignes[debut].replace("[x]", "[ ]", 1)
    date = a.date or __import__("datetime").date.today().isoformat()
    essai, erreur = coeur.ESSAI_REFUSE, "Erreur : %s" % a.refuser
    bloc = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Tentatives**")), None)
    if bloc is None:
        # Sous le titre, après sa ligne vide s'il en a une — comme les blocs écrits à la main.
        k = debut + 2 if debut + 1 < fin and not lignes[debut + 1].strip() else debut + 1
        lignes[k:k] = (["**Tentatives** (%s) — non résolu." % date, "1. " + essai, erreur]
                       + ([""] if k == debut + 2 else []))
        rang, dernier, soldes = 0, None, None
    else:
        n = next((i for i in range(bloc + 1, fin) if not lignes[i].strip() or lignes[i].startswith("**")), fin)
        # Compté avant l'ajout : la ligne Refus soldés, et les tentatives qui étaient déjà un refus de relecture.
        rang, dernier, soldes = refus_du_bloc(lignes[bloc:n])
        if not TETE_OUVERTE.match(lignes[bloc]):
            lignes[bloc] = "**Tentatives** (%s) — non résolu." % date
        numeros = [i for i in range(bloc + 1, n) if re.match(r"[0-9]+\. ", lignes[i])]
        p = numeros[-1] + 1 if numeros else bloc + 1 + (soldes or 0)
        suivant = int(lignes[numeros[-1]].split(".")[0]) + 1 if numeros else rang + 1
        lignes.insert(p, "%d. %s" % (suivant, essai))
        e = next((i for i in range(p + 1, n + 1) if lignes[i].startswith("Erreur :")), None)
        if e is None:
            lignes.insert(p + 1, erreur)
        else:
            lignes[e] = erreur
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("REFUSÉ %s · refus %d%s\n" % (a.fiche, rang + 1,
                                                " · dernier : %s" % dernier if soldes and dernier else ""))
    return 0


# --- valider -----------------------------------------------------------------

OUVRANT = re.compile(r"^<!-- FICHE:(\S+) -->$")
CRITERE = "**Critère de fin**"
# La marque d'un critère à regarder : un seul endroit, lue par la fiche, `valider` et `trier` (NUI10).
MARQUE_VISUELLE = "(visuel)"
CRITERE_VISUEL = re.compile(r"^\*\*Critère de fin\*\* " + re.escape(MARQUE_VISUELLE))
ARRET = "ARRÊT: critère de fin (visuel) — livre, puis rends RETOUR sans cocher"
CODE_EN_LIGNE = re.compile(r"`[^`]*`")
# Les seuils vivent ici ; la doc dit « le seuil de vlp.py » et n'écrit pas le chiffre.
SEUIL_FICHE = 50
SEUIL_SOCLE = 80
# Fichiers de tête, lus à chaque session ou chaque fiche (mesure : chantier J, J1).
# `SEUIL_CLAUDE` : 80 → 100 le 2026-10-24, décision de l'utilisateur (« Le plafond, on va l'augmenter à 100 lignes »).
SEUIL_CLAUDE = 100
SEUIL_CHANTIER = 50
SEUIL_INDEX = 80
CLOS_GARDES = 5  # chantiers clos gardés dans « Où on en est » de CLAUDE.md


def valider_lignes(lignes):
    """(écarts, avertissements, nombre de fiches, lignes du socle) ; un écart
    ou un avertissement est un couple (numéro de ligne, message)."""
    ecarts, avert = [], []
    blocs = []          # (id du marqueur, début, fin) — indices 0
    ouvert = None       # (id, début)
    for i, l in enumerate(lignes):
        s = l.strip()
        m = OUVRANT.match(s)
        if m:
            if ouvert:
                ecarts.append((i + 1, "marqueur imbriqué : <!-- FICHE:%s --> ouvert ligne %d sans fermant"
                               % (ouvert[0], ouvert[1] + 1)))
                blocs.append((ouvert[0], ouvert[1], i - 1))
            ouvert = (m.group(1), i)
        elif s == FERMANT:
            if ouvert:
                blocs.append((ouvert[0], ouvert[1], i))
                ouvert = None
            else:
                ecarts.append((i + 1, "marqueur fermant sans ouvrant"))
    if ouvert:
        ecarts.append((ouvert[1] + 1, "marqueur ouvrant sans fermant : <!-- FICHE:%s -->" % ouvert[0]))
        blocs.append((ouvert[0], ouvert[1], len(lignes) - 1))

    titres = [(i, l.split()[1]) for i, l in enumerate(lignes) if TITRE.match(l)]
    vus, fiches_ = {}, []
    for n, (i, ident) in enumerate(titres):
        if ident in vus:
            ecarts.append((i + 1, "identifiant en double : %s (déjà ligne %d)" % (ident, vus[ident] + 1)))
        vus.setdefault(ident, i)
        bloc = next((b for b in blocs if b[1] < i <= b[2]), None)
        if bloc is None:
            ecarts.append((i + 1, "titre sans marqueurs : %s" % ident))
            suivant = titres[n + 1][0] if n + 1 < len(titres) else len(lignes)
            fin = next((j for j in range(i + 1, suivant) if lignes[j].rstrip() == "---"), suivant) - 1
            fiches_.append((ident, i, fin))
        else:
            if bloc[0] != ident:
                ecarts.append((i + 1, "marqueur %s ≠ titre %s" % (bloc[0], ident)))
            fiches_.append((ident, bloc[1], bloc[2]))

    premiere = min([i for i, _ in titres] + [b[1] for b in blocs] + [len(lignes)])
    socle = socle_lignes(lignes)
    for nom, motif in (("## Le socle commun", r"^## Le socle"), ("## L'ordre des fiches", r"^## L.*ordre des fiches")):
        ou = [i for i, l in enumerate(lignes) if re.match(motif, l)]
        if not ou:
            ecarts.append((1, "section absente : %s" % nom))
        elif len(ou) > 1:
            ecarts.append((ou[1] + 1, "section en double : %s (déjà ligne %d)" % (nom, ou[0] + 1)))
        elif ou[0] > premiere:
            ecarts.append((ou[0] + 1, "section après la première fiche : %s" % nom))

    if socle and len(socle) > SEUIL_SOCLE:
        debut_socle = next((i for i, l in enumerate(lignes) if l.startswith("## Le socle")), 1)
        avert.append((debut_socle + 1, "socle : %d lignes, au-delà du seuil de vlp.py (%d)"
                      % (len(socle), SEUIL_SOCLE)))

    for ident, debut, fin in fiches_:
        corps = lignes[debut:fin + 1]
        if not any(l.startswith(CRITERE) for l in corps):
            ecarts.append((debut + 1, "fiche %s sans ligne %s" % (ident, CRITERE)))
        ouvert_code = False   # un code en ligne peut commencer sur la ligne d'avant
        for j, l in enumerate(corps, debut + 1):
            if not l.strip() or l.lstrip().startswith("```"):
                ouvert_code = False
                continue
            # Une mention entre accents graves parle du marqueur, elle ne le pose pas.
            hors_code = CODE_EN_LIGNE.sub("", ("`" if ouvert_code else "") + l)
            if hors_code.count("`") % 2:
                ouvert_code, hors_code = True, hors_code[:hors_code.index("`")]
            else:
                ouvert_code = False
            if MARQUE_VISUELLE in hors_code and not CRITERE_VISUEL.match(l):
                ecarts.append((j, "fiche %s : %s hors de la ligne « %s %s » — /vlp:enchainer ne s'y arrêtera pas"
                               % (ident, MARQUE_VISUELLE, CRITERE, MARQUE_VISUELLE)))
        if len(corps) > SEUIL_FICHE:
            avert.append((debut + 1, "fiche %s : %d lignes, au-delà du seuil de vlp.py (%d)"
                          % (ident, len(corps), SEUIL_FICHE)))
    return sorted(ecarts), avert, len(vus), len(socle)


def cmd_valider(chemins, sortie, plan=False):
    """`vlp.py valider` : valider chaque fichier de fiches (`cmd_valider_seul`) ; avec `plan`, lister aussi ses titres,
    dépendances, blocs Tentatives et critères de fin (`PLAN`), numéro de ligne en tête."""
    code = cmd_valider_seul(chemins, sortie)
    for chemin in chemins if plan else []:
        for n, l in enumerate(lignes_de(chemin) if os.path.isfile(chemin) else [], 1):
            if coeur.PLAN.match(l):
                sortie.write("%s%d:%s\n" % (chemin + ":" if len(chemins) > 1 else "", n, l))
    return code


def cmd_valider_seul(chemins, sortie):
    code = 0
    for chemin in chemins:
        if not os.path.isfile(chemin):
            sortie.write("%s:0: fichier introuvable\nINVALIDE 0 fiches · socle 0 lignes · 1 écarts · 0 avertissements — %s\n"
                         % (chemin, chemin))
            code = 1
            continue
        if rapport(chemin, lignes_de(chemin), sortie):
            code = 1
    return code


def rapport(chemin, lignes, sortie):
    """Écrit les écarts, les avertissements et le bilan ; rend le nombre d'écarts."""
    ecarts, avert, n, socle = valider_lignes(lignes)
    for ligne, message in ecarts:
        sortie.write("%s:%d: %s\n" % (chemin, ligne, message))
    for ligne, message in avert:
        sortie.write("%s:%d: avertissement : %s\n" % (chemin, ligne, message))
    sortie.write("%s %d fiches · socle %d lignes · %d écarts · %d avertissements — %s\n"
                 % ("INVALIDE" if ecarts else "VALIDE", n, socle, len(ecarts), len(avert), chemin))
    return len(ecarts)


# En fin de fichier : `relecture` importe des noms d'ici, qui doivent exister avant lui (REF47).
import noyau.relecture  # noqa: E402 — `noyau.relecture.git_texte` : un test la remplace là
