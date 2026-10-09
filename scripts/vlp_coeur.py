#!/usr/bin/env python3
"""Le code de `vlp.py` (VIT5) : `vlp.py` le lance, et son `.pyc` évite de recompiler ce module à chaque
lancement. La doc des sous-commandes vit dans la docstring de `vlp.py`, et nulle part ailleurs.
"""
import argparse
import collections
import datetime
import glob
import hashlib
import html.parser
import io
import json
import os
import re
import shlex
import statistics
import sys
import tempfile
import time
import unicodedata

import carnet
import vlp_hook

TAMPON_HOOKS = vlp_hook.TAMPON

TITRE = re.compile(r"^## [A-Z]{1,3}[0-9]")
TITRE_GENERIQUE = re.compile(r"^##\s+\S")
PREFIXE = re.compile(r"^[A-Z]{1,3}")
COURANT = re.compile(r"^\s*-\s*\*\*fichier de fiches courant\*\*\s*:\s*(.+?)\s*$")
ALIAS = re.compile(r"^\s*-\s*\*\*alias\*\*\s*:\s*(\S+)")
SESSION = re.compile(r"^\*\*Session\*\* : (.+?)(?: \([^()]*\))?\s*$")    # l'id seul : le ` (<rôle>)` de la nuit n'en est pas
FERMANT = "<!-- /FICHE -->"
CHANTIERS_POSSIBLES = re.compile(r"^\s*-\s*\*\*chantiers possibles\*\*\s*:\s*(.+?)\s*$", re.MULTILINE)
METHODE = re.compile(r"^\s*-\s*\*\*méthode\*\*\s*:\s*(.+?)\s*$", re.MULTILINE)
FORMAT_DEBUT, FORMAT_FIN = "## Le fichier de fiches", "## Les deux formes de critère de fin"


def section(lignes, debut, fin):
    """(a, b), lignes 1-basées incluses, ou None : du premier titre `## ` qui
    vérifie `debut` jusqu'avant le premier titre qui suit celui qui vérifie
    `fin` — cherché à partir du titre de début —, ou jusqu'à la fin du fichier.
    None si aucun titre ne vérifie `debut`, ou aucun ensuite `fin`. Un `## `
    dans un bloc ``` n'est pas un titre."""
    titres, en_bloc = [], False
    for i, ligne in enumerate(lignes):
        if ligne.lstrip().startswith("```"):
            en_bloc = not en_bloc
        elif not en_bloc and TITRE_GENERIQUE.match(ligne):
            titres.append(i)
    d = next((k for k, i in enumerate(titres) if debut(lignes[i])), None)
    if d is None:
        return None
    f = next((k for k in range(d, len(titres)) if fin(lignes[titres[k]])), None)
    if f is None:
        return None
    return titres[d] + 1, titres[f + 1] if f + 1 < len(titres) else len(lignes)


def premier_lancement(texte, nom=""):
    """Vrai si ce lancement est le premier à traiter cette entrée de hook : le tampon de `vlp_hook`,
    nommé par `nom` + entrée — le nom, car `filet` et `hook` reçoivent la même entrée (PYT2) —, dans
    `TAMPON_HOOKS` ; ses replis (`None`, `VLP_SANS_TAMPON`, une autre `OSError`) y sont dits."""
    return tampon_neuf(vlp_hook.nom_tampon(texte, nom))


def tampon_neuf(nom):
    """Vrai si `<TAMPON_HOOKS>/<nom>` se crée en exclusif — `vlp_hook.tampon_neuf`, dans le dossier de ce module."""
    return vlp_hook.tampon_neuf(nom, TAMPON_HOOKS)


def une_fois(entree, commande, *args):
    """Lire l'entrée d'un hook une fois : 0, muet, si un autre lanceur l'a déjà traitée ; une entrée
    déjà triée par le lanceur (`vlp_hook.Triee`, VIT8) passe sans re-tri."""
    if isinstance(entree, vlp_hook.Triee):
        return commande(entree, *args)
    texte = (entree or sys.stdin).read()
    return commande(io.StringIO(texte), *args) if premier_lancement(texte, commande.__name__) else 0


def lire(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def lignes_de(chemin):
    lignes = lire(chemin).split("\n")
    if lignes and lignes[-1] == "":
        lignes.pop()
    return lignes


class Absent(ValueError):
    """Un chemin nommé par `CHANTIER.md` ne désigne pas de fichier. Sous-classe
    de `ValueError` : les `except ValueError` qui gardent déjà leur contexte la
    voient ; sinon `main` l'attrape — c'est le seul endroit où la règle vit."""


def chemin_garde(chemin, libelle="fichier", nom=None):
    """Le chemin, ou `Absent` : le point unique où un chemin venu de
    `CHANTIER.md` est vérifié. `nom` : ce qu'on montre quand le relatif parle
    mieux que l'absolu."""
    if not os.path.isfile(chemin):
        raise Absent("%s introuvable : %s" % (libelle, nom or chemin))
    return chemin


def lignes_gardees(chemin, libelle="fichier", nom=None):
    """Les lignes d'un chemin gardé : toute lecture d'un chemin de `CHANTIER.md`
    passe par ici."""
    return lignes_de(chemin_garde(chemin, libelle, nom))


def lignes_du_projet(projet, chemin_relatif, libelle):
    """Les lignes d'un chemin relatif au projet, gardées."""
    return lignes_gardees(os.path.join(projet, chemin_relatif), libelle, chemin_relatif)


def chemin_archive(index):
    """L'archive des lignes clos, dans le dossier de l'index : son chemin ne se
    retape jamais, il se dérive d'ici (chantier IDX)."""
    dossier = os.path.dirname(index)
    return (dossier.rstrip("/\\") + "/" if dossier else "") + "00-INDEX-archive.md"


def lignes_index(projet, index):
    """Les lignes de l'index, puis celles de son archive si elle existe : un
    lecteur de l'index voit aussi les chantiers clos qu'on y a déplacés."""
    archive = os.path.join(projet, chemin_archive(index))
    return lignes_du_projet(projet, index, "index") + (lignes_de(archive) if os.path.isfile(archive) else [])


ARCHIVE_TETE = ["# Archive de l'index — les chantiers clos", "",
                "QUAND LIRE : on relit un chantier clos ; l'index n'en garde qu'une ligne qui renvoie ici.", "",
                "| Fichier | Lire quand |", "|---|---|"]
NUMERO_LIGNE = re.compile(r"^\|\s*`(\d\d)")


def numero_ligne(ligne):
    """Le numéro de fichier d'une ligne de table (2 premiers chiffres) ; sans numéro : après tout."""
    m = NUMERO_LIGNE.match(ligne)
    return int(m.group(1)) if m else 100


def archiver(idx, arch, nom_archive):
    """Déplace chaque ligne de table `**clos**` de l'index `idx` vers l'archive `arch` (None :
    créée avec `ARCHIVE_TETE`), triée par numéro ; pose dans l'index une ligne qui renvoie à
    `nom_archive`, si elle manque. Une ligne se déplace telle quelle, jamais réécrite ; relancée,
    rien ne change. Rend (index, archive ou None, lignes déplacées) (chantier IDX)."""
    clos = [k for k, l in enumerate(idx) if l.startswith("|") and "**clos**" in l]
    renvoi = "| `%s` |" % nom_archive
    a_renvoi = any(l.startswith(renvoi) for l in idx)
    if not clos and (a_renvoi or arch is None):
        return idx, arch, 0
    arch = list(ARCHIVE_TETE) if arch is None else list(arch)
    sep = next((k for k, l in enumerate(arch) if l.startswith("|---")), None)
    if sep is None:
        arch += [""] + ARCHIVE_TETE[-2:]
        sep = len(arch) - 1
    fin = sep + 1
    while fin < len(arch) and arch[fin].startswith("|"):
        fin += 1
    rangees = arch[sep + 1:fin]
    rangees += [idx[k] for k in clos if idx[k] not in rangees]
    arch[sep + 1:fin] = sorted(rangees, key=numero_ligne)
    nouvel = [l for k, l in enumerate(idx) if k not in clos]
    if not a_renvoi:
        rang = clos[0] if clos else max((k + 1 for k, l in enumerate(nouvel) if LIGNE_FICHIER.match(l)), default=len(nouvel))
        nouvel.insert(rang, renvoi + " on relit un chantier clos — chacun y a sa ligne, triée par numéro |")
    return nouvel, arch, len(clos)


def cmd_archiver(a, sortie):
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    index = champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "index")
    if not index:
        sortie.write("GARDE: champ **index** absent de CHANTIER.md\n")
        return 1
    idx = lignes_du_projet(projet, index, "index")
    chemin_arch = os.path.join(projet, chemin_archive(index))
    arch = lignes_de(chemin_arch) if os.path.isfile(chemin_arch) else None
    nidx, narch, n = archiver(idx, arch, os.path.basename(chemin_arch))
    for chemin, avant, apres in ((os.path.join(projet, index), idx, nidx), (chemin_arch, arch, narch)):
        if apres is not None and apres != avant:
            with open(chemin, "w", encoding="utf-8", newline="") as fh:
                fh.write("\n".join(apres) + "\n")
    sortie.write("ARCHIVÉ %d · index %d lignes · archive %d lignes\n" % (n, len(nidx), len(narch or [])))
    return 0


# --- carte -------------------------------------------------------------------

def equipe(d):
    """Vrai si `d` porte `CHANTIER.md` à la casse exacte : sous Windows et
    macOS, `isfile` prendrait un `chantier.md` pour la carte."""
    try:
        return "CHANTIER.md" in os.listdir(d) and os.path.isfile(os.path.join(d, "CHANTIER.md"))
    except OSError:
        return False


def trouver(depart):
    d = os.path.abspath(depart)
    while True:
        if equipe(d):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def fichier_courant(carte_texte):
    """Le fichier que nomme l'ancienne ligne « fichier de fiches courant » de CHANTIER.md, ou None (absente, ou
    « aucun »). Plus aucun lecteur ne la suit (NUI31) : seul `niveau` la lit encore, pour poser la marque d'un projet
    pas migré puis retirer la ligne."""
    for ligne in carte_texte.split("\n"):
        m = COURANT.match(ligne)
        if m:
            valeur = re.sub(r"\s+\([^)]*\)$", "", m.group(1)).strip()
            return None if valeur.lower().startswith("aucun") else valeur
    return None


def chemins_md(texte, racine):
    """Les chemins `.md` d'une ligne de prose, dans l'ordre. Entre
    backticks : le contenu tel quel. Hors backticks, un chemin peut contenir
    une espace (`context AI/`) : pour chaque `.md` non suivi d'une lettre, la
    plus longue fin du texte qui le précède, coupée à une espace, `,`, `;` ou
    une parenthèse, qui existe sous `racine` — le disque tranche ; aucune : la
    plus courte, que la lecture gardée refusera."""
    trouves = []
    for n, morceau in enumerate(re.split(r"(`[^`]*`)", texte)):
        if n % 2:
            if morceau[1:-1].endswith(".md"):
                trouves.append(morceau[1:-1])
            continue
        depart = 0
        for m in re.finditer(r"\.md(?![^\W\d_])", morceau):
            avant = morceau[depart:m.end()]
            depart = m.end()
            coupes = [-1] + [i for i, ch in enumerate(avant) if ch in " ,;()"]
            fins = [avant[i + 1:].strip() for i in coupes]
            fins = [f for f in fins if f and f != ".md"]
            if not fins:
                continue
            bon = next((f for f in fins if os.path.isfile(os.path.join(racine, f))), None)
            trouves.append(bon or fins[-1])
    return trouves


def imprimer_section(sortie, nom, chemin, lignes, plage):
    """L'en-tête `--- <nom> : <chemin> (lignes A–B) ---`, puis le texte."""
    sortie.write("--- %s : %s (lignes %d–%d) ---\n" % (nom, chemin, plage[0], plage[1]))
    sortie.write("".join(l + "\n" for l in lignes[plage[0] - 1:plage[1]]))


def imprimer_todo(texte, racine, sortie):
    """La TODO de chaque fichier que nomme la ligne **chantiers possibles**."""
    possibles = CHANTIERS_POSSIBLES.search(texte)
    if possibles is None:
        sortie.write("TODO=absente (pas de ligne « chantiers possibles »)\n")
        return
    for chemin in chemins_md(possibles.group(1), racine):
        try:
            lignes = lignes_du_projet(racine, chemin, "fichier")
        except Absent as e:
            sortie.write("GARDE: %s\n" % e)
            continue
        plage = section(lignes, lambda t: "TODO" in t, lambda t: "TODO" in t)
        if plage is None:
            sortie.write("TODO=absente %s\n" % chemin)
        else:
            imprimer_section(sortie, "TODO", chemin, lignes, plage)


def imprimer_methode(texte, racine, sortie):
    """Le format des fiches, dans le premier chemin de la ligne **méthode** :
    cherché dans le projet, sinon sous `KIT` (la ligne du kit est de la prose)."""
    methode = METHODE.search(texte)
    chemins = chemins_md(methode.group(1), racine) if methode else []
    if not chemins:
        sortie.write("METHODE=absente (pas de ligne « méthode »)\n")
        return
    chemin = chemins[0]
    lieu = racine if os.path.isfile(os.path.join(racine, chemin)) else KIT
    try:
        lignes = lignes_gardees(os.path.join(lieu, chemin), "fichier", chemin)
    except Absent as e:
        sortie.write("GARDE: %s\n" % e)
        return
    plage = section(lignes, lambda t: t.rstrip() == FORMAT_DEBUT, lambda t: t.rstrip() == FORMAT_FIN)
    if plage is None:
        sortie.write("METHODE=absente %s\n" % chemin)
    else:
        imprimer_section(sortie, "méthode", chemin, lignes, plage)


def fiches(chemin):
    """(nombre de lignes, [(numéro, titre)], prochaine ou None)."""
    lignes = lignes_de(chemin)
    titres = [(i, l) for i, l in enumerate(lignes, 1) if TITRE.match(l)]
    prochaine = next((l.split()[1] for _, l in titres if "[x]" not in l), None)
    return len(lignes), titres, prochaine


def carte(depart, sortie, relecteur=False, neuve=False):
    """Écrire la carte du projet qui contient `depart`, ligne à ligne comme le dit la docstring de `vlp.py` ; `neuve`
    (`--session-neuve`, `/vlp:tache` seule) y ajoute l'avertissement d'`avertir_session` (VIT20)."""
    racine = trouver(depart)
    if racine is None:
        voisins = sorted(os.path.join(v, "CHANTIER.md") for v in glob.glob(os.path.join(os.path.abspath(depart), "*"))
                         if equipe(v))
        for v in voisins:
            m = next((ALIAS.match(l) for l in lire(v).split("\n") if ALIAS.match(l)), None)
            sortie.write("VOISIN=%s alias=%s\n" % (os.path.dirname(v), m.group(1) if m else "?"))
            sortie.write("".join(l + "\n" for l in ligne_git(os.path.dirname(v))))
        if not voisins:
            sortie.write("AUCUN_PROJET\n")
        return 0
    texte = lire(os.path.join(racine, "CHANTIER.md"))
    try:
        courant = courant_de(racine)
    except Absent as e:
        # `cmd_equiper` appelle `carte` en direct : elle garde, elle ne lève pas.
        sortie.write("PROJET=%s\nGARDE: %s\n" % (racine, e))
        return 1
    sortie.write("PROJET=%s\nCOURANT=%s\n--- CHANTIER.md ---\n%s" % (racine, courant or "aucun", texte))
    if not texte.endswith("\n"):
        sortie.write("\n")
    if not relecteur:
        for l in lignes_attente(dossier_artefacts(racine)):
            sortie.write(l + "\n")
        if os.environ.get("VLP_NUIT") == "1":
            sortie.write("NUIT=1\n")
        retard = retard_plugin(racine)
        if retard:
            sortie.write('PLUGIN_RETARD=%d commit(s) de code du plugin absents du plugin chargé — avant un '
                         '/reload-plugins : git -C "%s" merge --ff-only %s\n'
                         % (retard[0], retard[1].replace("\\", "/"), retard[2]))
        ecrire_ailleurs(racine, sortie)
        sortie.write("".join(l + "\n" for l in ligne_git(racine)))
    if courant is None:
        sortie.write("--- fichier de fiches courant : aucun ---\n")
        imprimer_todo(texte, racine, sortie)
        imprimer_methode(texte, racine, sortie)
        return 0
    try:
        n, titres, prochaine = fiches(chemin_garde(os.path.join(racine, courant),
                                                  "fichier de fiches", courant))
    except Absent as e:
        # `cmd_equiper` appelle `carte` en direct : elle garde, elle ne lève pas.
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("--- fiches : %s (%d lignes, %d titres) ---\n" % (courant, n, len(titres)))
    if n and not titres:
        sortie.write("GARDE: aucun titre de fiche au format '## X1' — ne rien conclure\n")
        return 1
    if relecteur:
        # REL1 : 15 relecteurs sur 42 citaient d'autres titres — la suite du chantier, pas un besoin.
        return 0
    for i, l in titres:
        sortie.write("%d:%s\n" % (i, l))
    sortie.write("PROCHAINE=%s\n" % (prochaine or "aucune"))
    avertir_session(os.path.join(racine, courant), neuve, sortie)
    return 0


def places_de_session(lignes, session):
    """Rendre où `session` a une ligne `**Session**` dans le fichier de fiches `lignes`, dans l'ordre et sans doublon :
    `cadrage` avant le premier titre de fiche (`ouvrir`), sinon l'identifiant de la fiche dont le titre précède."""
    places, ici = [], "cadrage"
    for l in lignes:
        m = SESSION.match(l)
        if TITRE.match(l):
            ici = l.split()[1]
        elif m and m.group(1) == session and ici not in places:
            places.append(ici)
    return places


SESSION_SURE = re.compile(r"[0-9A-Za-z-]+\Z")


def marque_enchaine(session):
    """Le chemin de la marque `vlp-enchaine-<session>` dans le dossier temporaire (ARP3), ou None si l'id n'est pas
    fait de chiffres, lettres et tirets : il entre dans un nom de fichier."""
    if not SESSION_SURE.match(session):
        return None
    return os.path.join(tempfile.gettempdir(), "vlp-enchaine-%s" % session)


def poser_marque_enchaine():
    """Poser (ou rafraîchir) la marque de la session de `CLAUDE_CODE_SESSION_ID` — `carte --enchaine`, ARP3. Id vide
    ou hors de `SESSION_SURE` : rien. Une écriture refusée se dit sur stderr, la carte continue."""
    marque = marque_enchaine(os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip())
    if not marque:
        return
    try:
        with open(marque, "w", encoding="utf-8"):
            pass
    except OSError as e:
        sys.stderr.write("vlp: marque %s non posée : %s\n" % (marque, e))


def avertir_session(chemin, neuve, sortie):
    """Écrire `AVERTISSEMENT:` quand `neuve` et que la session de `CLAUDE_CODE_SESSION_ID` est déjà notée dans le
    fichier de fiches `chemin` — au cadrage ou sous une fiche : une fiche, une session neuve (VIT20). Id vide ou
    absent : rien. `VLP_NUIT=1` : rien — la nuit note elle-même l'id de la session `clore` avant de la lancer.
    La marque de cette session (`marque_enchaine`, posée par l'injection de `/vlp:enchainer`) : rien (ARP3)."""
    s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if not neuve or not s or os.environ.get("VLP_NUIT") == "1":
        return
    marque = marque_enchaine(s)
    if marque and os.path.exists(marque):   # ARP3 : /vlp:enchainer joue ses fiches à la suite dans cette session
        return
    places = places_de_session(lignes_de(chemin), s)
    if places:
        sortie.write("AVERTISSEMENT: session déjà notée dans ce fichier de fiches (%s) — /clear d'abord : une fiche, "
                     "une session neuve\n" % ", ".join(places))


RELAIS_SECONDES = 30
MARQUE_SECONDES = 4 * 24 * 3600   # l'âge où une marque `vlp-enchaine-` s'efface : 4 jours (cadrage ARP, réponse de l'utilisateur)


def carte_injectee(depart, python, relais, sortie, **options):
    """Écrire la carte d'une injection ; `options` passent à `carte` (`relecteur`, `neuve`).

    L'injection : `py -3 … --python "py -3"; python3 … --relais; py -3 … --relais; echo fin` (chantier Y, Y1 ; `py -3`
    depuis VIT24 : `py` seul relit le `#!` de `vlp.py` et relance un `python3`, +54 ms ; ordre inversé en U4 : sous Windows le message du raccourci
    Store de `python3` tombe après la carte, sous Ubuntu « py: command not found » avant ; le 3e appel remet
    à 0 le `$LASTEXITCODE` de PowerShell, que `echo` ne touche pas) : une ligne vide d'abord,
    `PYTHON=<nom>` pour le corps de la skill, et rien au relais si le premier lancement a déjà écrit la carte.

    Sans redirection (EVF4) : NIV1 envoyait l'erreur du lanceur absent vers `${CLAUDE_PLUGIN_ROOT}/relais-python.err`,
    une écriture hors du workspace que l'eval refuse même Bash accordé — `vlp:jouer` n'y forkait plus. Le prix :
    `py: command not found` entre dans la carte là où `py` manque (2 lignes sous Ubuntu, 0 sous Windows).

    Le ménage d'abord (ARP4) : `vlp-carte-` de plus de `RELAIS_SECONDES`, `vlp-enchaine-` de plus de
    `MARQUE_SECONDES` — avant d'écrire le tampon de cet appel, qui reste."""
    import hashlib
    import tempfile
    import time
    vlp_hook.menage(tempfile.gettempdir(), (("vlp-carte-", RELAIS_SECONDES), ("vlp-enchaine-", MARQUE_SECONDES)))
    cle = hashlib.sha1(os.path.abspath(depart).encode("utf-8")).hexdigest()[:16]
    tampon = os.path.join(tempfile.gettempdir(), "vlp-carte-%s" % cle)
    if relais:
        # Le tampon reste : le 3e appel de l'injection (`py … --relais`) doit se taire aussi.
        try:
            recent = time.time() - os.path.getmtime(tampon) < RELAIS_SECONDES
        except OSError:
            recent = False
        if recent:
            return 0
    else:
        try:
            with open(tampon, "w", encoding="utf-8") as f:
                f.write(python)
        except OSError:
            pass
    sortie.write("\nPYTHON=%s\n" % python)
    return carte(depart, sortie, **options)


def cmd_carte(a, sortie):
    """Lancer `vlp.py carte` : injectée avec `--python`, nue sinon. `--enchaine` pose la marque à chaque appel, relais
    compris : sous Ubuntu, le premier appel de l'injection échoue."""
    depart = a.dossier or os.getcwd()
    if a.enchaine:
        poser_marque_enchaine()
    if a.python:
        return carte_injectee(depart, a.python, a.relais, sortie, relecteur=a.relecteur, neuve=a.session_neuve)
    return carte(depart, sortie, a.relecteur, a.session_neuve)


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


def sessions_de(lignes):
    vues = []
    for l in lignes:
        m = SESSION.match(l)
        if m and m.group(1) not in vues:
            vues.append(m.group(1))
    return vues


def sessions_entete(lignes):
    """Les sessions de l'en-tête, avant le premier titre de fiche : le cadrage, que `ouvrir`
    note (chantier CAD)."""
    k = next((i for i, l in enumerate(lignes) if TITRE.match(l)), len(lignes))
    return sessions_de(lignes[:k])


def essais_de(session):
    """Les transcripts des essais `claude -p` de `session`, triés : ceux d'un bac de son scratchpad,
    `~/.claude/projects/<projet>-<session>-scratchpad-<bac>/<essai>.jsonl` (ESS1 : 39 dossiers de
    cette forme), et ceux que le registre déclare pour elle (`essais_declares`, MET2). Leurs
    sous-agents n'y sont pas ; [] sans dossier."""
    projets = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    motifs = ["*-" + glob.escape(session) + "-scratchpad-*"] + essais_declares(session)
    return sorted({e for m in motifs for e in glob.glob(os.path.join(projets, m, "*.jsonl"))})


def registre_essais():
    """Le registre des essais lancés hors d'un bac (MET2) : `~/.claude/vlp-essais.txt`, une ligne
    `<session> <motif>` par déclaration (`vlp.py essai`)."""
    return os.path.join(os.path.expanduser("~"), ".claude", "vlp-essais.txt")


def motif_sur(motif):
    """Vrai si `motif` nomme des dossiers de `~/.claude/projects/` sans en sortir : ni séparateur, ni
    `..`, ni blanc — le registre se lit en deux champs (MET2)."""
    return bool(motif) and not re.search(r"[\\/\s]|\.\.", motif)


def essais_declares(session):
    """Les motifs de dossier de `~/.claude/projects/` que le registre déclare pour `session` ;
    [] sans registre. Une ligne qui n'a pas deux champs, ou un motif qui sortirait du dossier,
    ne compte pas (`motif_sur`)."""
    if not os.path.isfile(registre_essais()):
        return []
    with open(registre_essais(), encoding="utf-8") as f:
        paires = [l.split() for l in f]
    return [p[1] for p in paires if len(p) == 2 and p[0] == session and motif_sur(p[1])]


def cmd_essai(a, sortie):
    """Déclarer au registre un essai lancé hors d'un bac, une fois : `ESSAI <session> <motif> ·
    <n> dossier(s) · <m> transcript(s)` — 0 et 0 avant son lancement. La session : `--session`,
    sinon `CLAUDE_CODE_SESSION_ID` ; aucune, ou un motif refusé par `motif_sur` : `GARDE:`,
    rien d'écrit, sort 1 (MET2)."""
    session = a.session or os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not session or len(session.split()) != 1 or not motif_sur(a.motif):
        sortie.write("GARDE: essai non déclaré — session %r, motif %r : il faut une session (--session ou "
                     "CLAUDE_CODE_SESSION_ID) et un nom de dossier de ~/.claude/projects/, sans / ni \\ ni .. "
                     "ni blanc\n" % (session, a.motif))
        return 1
    if a.motif not in essais_declares(session):
        os.makedirs(os.path.dirname(registre_essais()), exist_ok=True)
        with open(registre_essais(), "a", encoding="utf-8", newline="\n") as f:
            f.write("%s %s\n" % (session, a.motif))
    projets = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    sortie.write("ESSAI %s %s · %d dossier(s) · %d transcript(s)\n"
                 % (session, a.motif, len(glob.glob(os.path.join(projets, a.motif))),
                    len(glob.glob(os.path.join(projets, a.motif, "*.jsonl")))))
    return 0


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


def cmd_sessions(chemin, sortie):
    for s in sessions_de(lignes_de(chemin)):
        sortie.write(s + "\n")
    return 0


def cmd_cout(chemin, session, sortie, a_clore=False):
    """Le coût du fichier de fiches, coupé aux commits comme la page : une ligne par fiche
    (`ligne_parts`), puis hors fiches, puis `TOTAL`. Sans heures de commit, les tables
    brutes de `mesure-tokens.py` sur les sessions entières, sous une ligne qui dit pourquoi.
    `--session` met d'abord la table de la session courante, pour `/vlp:tache`. `a_clore` : deux
    lignes après `TOTAL`, `à clore` et `après clore` (chantier APC). Sans `tr` ni
    `xargs` : les commandes du kit tournent aussi sous PowerShell (chantier Y)."""
    import contextlib
    lignes = lignes_de(chemin)
    ids = sessions_de(lignes)
    code = 0
    if session:
        s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
        sortie.write("SESSION=%s\n" % s)
        if not s:
            return 0
        with contextlib.redirect_stdout(sortie):
            code = mesure().main([s]) or 0
        ids = [s] + [i for i in ids if i != s]
    elif not ids:
        sortie.write("SESSIONS 0 — pas de total\n")
        return 0
    decoupe, pourquoi, gardes = decouper(chemin, lignes)
    for g in gardes:
        sortie.write(g + "\n")
    if not decoupe:
        sortie.write("DÉCOUPE aucune — %s : sessions entières, sous-agents compris\n" % pourquoi[0])
        with contextlib.redirect_stdout(sortie):
            code = mesure().main(ids) or code
        gardes, zero = [], (0, 0, 0, 0)
        essais = essais_entiers(ids, gardes)
        for g in gardes:
            sortie.write(g + "\n")
        if essais[1]:
            sortie.write(ligne_parts("essais", zero, zero, essais) + "\n")
        if a_clore:
            sortie.write("GARDE: --a-clore sans découpe — pas de ligne à clore\n")
        return code
    parts, hors = decoupe
    sortie.write("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, "
                 "un sous-agent compte à son départ\n")
    for ident, *r in parts:
        sortie.write(ligne_parts(ident, *r) + "\n")
    sortie.write(ligne_parts("hors fiches", *hors) + "\n")
    sortie.write(ligne_parts("TOTAL (fiches + hors fiches)", *totaux(decoupe)) + "\n")
    if a_clore:
        avant = totaux_a_clore(chemin, lignes)
        if avant is None:
            sortie.write("GARDE: aucun appel « vlp.py clore » dans la dernière plage hors fiches"
                         " — pas de ligne à clore\n")
            return code
        tout = totaux(decoupe)
        sortie.write(ligne_parts("à clore", *avant) + "\n")
        sortie.write(ligne_parts("après clore", *[(a[0] - b[0], a[1] - b[1], moins(a[2], b[2]), a[3] - b[3])
                                                  for a, b in zip(tout, avant)]) + "\n")
    return code


# Un appel qui lance un script Python : en tête d'un segment (début, `;`, `&`, `|`, `(`, fin de ligne), après
# d'éventuels `X=y` ou `$x =`, un interprète Python (`py`, `python`, `python3`, chemin, `.exe` et
# guillemets permis), ses options, puis un chemin qui finit par le script (chantier ECA ; `compteur`, VIT17).
TETE_SEGMENT = r"""(?:^|[;&|(\n])[ \t]*(?:\w+=\S*[ \t]+)*(?:\$\w+[ \t]*=[ \t]*)?"""
INTERPRETE = (r"""(?:"(?:[^"\n]*[/\\])?(?:py|python3?)(?:\.exe)?"|'(?:[^'\n]*[/\\])?(?:py|python3?)(?:\.exe)?'"""
              r"""|(?:[^\s"';&|]*[/\\])?(?:py|python3?)(?:\.exe)?)(?:[ \t]+-(?:[XW][ \t]+)?\S+)*[ \t]+""")


def appel_python(script, suite=""):
    """Compiler le motif d'un appel qui lance `script` — une regex —, puis `suite` : `TETE_SEGMENT`, `INTERPRETE`,
    et un chemin, cité ou nu, qui finit par le script."""
    chemin = r"""(?:"[^"\n]*%s"|'[^'\n]*%s'|[^\s"';&|]*%s)""" % ((script,) * 3)
    return re.compile(TETE_SEGMENT + INTERPRETE + chemin + suite, re.M)


APPEL_CLORE = appel_python(r"vlp\.py", r"[ \t]+clore\b")    # un appel qui lance `clore`


def lance_clore(commande):
    """Vrai si la commande lance `vlp.py clore` (`APPEL_CLORE`), le corps des heredocs qui ne font
    qu'écrire un fichier tu (`sans_heredoc`) : un texte qui cite l'appel — la ligne de bilan qu'un
    `echo` ou un `cat <<EOF` écrit, un `git commit -m`, un `--resultat` — n'en est pas un (chantier ECA)."""
    return bool(APPEL_CLORE.search(sans_heredoc(commande)))


def heure_clore(chemin, lignes):
    """L'heure, en secondes UTC, du dernier `tool_use` dont la commande lance `vlp.py clore`
    (`lance_clore`), dans les sessions du fichier et dans sa dernière plage hors fiches — celle
    que le commit de clôture ferme ; None sans lui. Ce que `clore` a vu en inscrivant son chiffre
    (chantier APC)."""
    fiches_ = fiches_du_fichier(lignes)
    heures = heures_commits(chemin, [f[0] for f in fiches_], [], any(l.startswith("**CLOS**") for l in lignes),
                             {f[0]: f[1] for f in fiches_})
    trous = plages(fiches_, heures, [], clos=True)[1] if heures else []
    if not trous:
        return None
    debut, fin = trous[-1]
    m, vu, sessions = mesure(), None, []
    for groupe in [f[3] for f in fiches_] + [sessions_entete(lignes)]:
        sessions += [s for s in groupe if s not in sessions]
    for s in sessions:
        transcript, erreur = m.resoudre(s)
        if erreur:
            continue
        with m.ouvrir(transcript) as f:
            for ligne in f:
                if "clore" not in ligne:
                    continue
                try:
                    d = json.loads(ligne)
                except ValueError:
                    continue
                contenu = (d.get("message") or {}).get("content") if isinstance(d, dict) else None
                appel = isinstance(contenu, list) and any(
                    isinstance(c, dict) and c.get("type") == "tool_use"
                    and lance_clore(str((c.get("input") or {}).get("command", ""))) for c in contenu)
                t = m.heure(d) if appel else None
                if t is not None and debut < t <= fin:
                    vu = t if vu is None else max(vu, t)
    return vu


def totaux_a_clore(chemin, lignes):
    """Les `totaux` de la découpe dont la dernière plage hors fiches s'arrête à `heure_clore`, ou
    None sans appel `clore` : le calcul de `cout --a-clore` et de `recompter --a-clore`."""
    t = heure_clore(chemin, lignes)
    return None if t is None else totaux(decouper(chemin, lignes, t)[0])


def decouper(chemin, lignes=None, fin=None):
    """(découpe, pourquoi, gardes) d'un fichier de fiches : `parts_aux_commits` sur les heures de
    `heures_commits`, ou None — `pourquoi` dit alors la raison. `cout` l'imprime, `recompter` en
    tire le total (`totaux`) : une découpe, deux lecteurs. `fin` : voir `parts_aux_commits`. Un
    fichier clos s'arrête, sans `fin`, au dernier appel `clore` (`heure_clore`), où `clore` a pris
    son chiffre : ce qui le suit — republications, commit — sort du coût (chantier APC, choix b)."""
    return decoupe_et_heures(chemin, lignes, fin)[:3]


def decoupe_et_heures(chemin, lignes=None, fin=None):
    """Rendre (découpe, pourquoi, gardes, (fiches, heures, fin)) : `decouper`, puis ce qu'elle a lu pour couper — les
    fiches, les heures de commit et la fin du coût —, que `compteur` reprend sans relancer Git (VIT17)."""
    lignes = lignes_de(chemin) if lignes is None else lignes
    fiches_ = fiches_du_fichier(lignes)
    pourquoi, gardes = [], []
    clos = any(l.startswith("**CLOS**") for l in lignes)
    heures = heures_commits(chemin, [f[0] for f in fiches_], pourquoi, clos, {f[0]: f[1] for f in fiches_})
    if fin is None and clos and heures:
        fin = heure_clore(chemin, lignes)
    decoupe = heures and parts_aux_commits(fiches_, heures, gardes, sessions_entete(lignes), fin)
    if not decoupe and heures:
        pourquoi.append("aucune session de fiche mesurée")
    return decoupe or None, pourquoi, gardes, (fiches_, heures, fin)


def totaux(decoupe):
    """(session, sous-agents, essais) d'une découpe, fiches et hors fiches sommées : la ligne
    `TOTAL` de `cout`, dont `plus(*totaux(d))[0]` est le nombre."""
    parts, hors = decoupe
    return tuple(plus(*[p[k + 1] for p in parts], hors[k]) for k in range(3))


# Ce que `compteur` lit d'une sortie d'outil (VIT17). La sorte de son appel : la suite entière, `--seul`,
# `test-boucle`, le mutant, pyright, Git, la publication — l'outil Artifact —, et le reste. Une commande Bash ou
# PowerShell se reconnaît à ce qu'elle lance en tête d'un segment, le corps des heredocs tu (`sans_heredoc`) :
# `mutant` d'abord, son `--test` cite la suite ; un script de mesure qui lance la suite par `subprocess` est du reste.
# Les garde-fous sont des débuts de ligne, chacun lu là seulement où il dit vrai — le même ordre que `GARDE_FOUS` :
# `ÉCART:` dans la sortie d'une suite (ceux d'un mutant sont à lui), `MUTANT ATTRAPÉ` dans celle d'un mutant, `GARDE:`
# dans celle d'un Bash ou d'un PowerShell, le verdict du relecteur au retour d'un `Agent` ou dans le message d'une
# autre session. Une sortie relue — la boucle qui attend une tâche de fond, puis un `Read` du même fichier — compte
# chaque fois.
SORTES_OUTIL = ("suite", "--seul", "test-boucle", "mutant", "pyright", "Git", "publication", "reste")
SUITES = SORTES_OUTIL[:3]
COMMANDES = (("mutant", appel_python(r"vlp\.py", r"[ \t]+mutant\b")), ("suite", appel_python(r"test-vlp\.py")),
             ("test-boucle", appel_python(r"test-boucle\.py")),
             ("pyright", re.compile(TETE_SEGMENT + r"pyright\b", re.M)),
             ("Git", re.compile(TETE_SEGMENT + r"git\b", re.M)))
GARDE_FOUS = ("ÉCART:", "MUTANT ATTRAPÉ", "GARDE:", "ACCEPTÉE", "REFUSÉE")
NUMERO_READ = re.compile(r"^\s*\d+(?:\t|→)")      # le numéro qu'un `Read` met devant chaque ligne
CODE_SORTIE = re.compile(r"\(exit code (\d+)\)")   # dans la notification d'une tâche de fond finie
ENTETE_COMPTEUR = ("COMPTEUR aux commits de fiche, en minutes — une fiche va du commit d'avant au sien ; actif : "
                   "les écarts entre lignes voisines, sessions et sous-agents (sans les essais), sans les pauses de "
                   "plus de %d min, chacun à la part de la ligne qui le ferme ; outils : minutes (appels) ; tours et "
                   "$ : ceux de cout ; suites : vertes sur celles dont la sortie dit le verdict")
TOTAUX_COUT = (("outils", "totalToolDuration"), ("modèle", "totalAPIDuration"), ("durée", "totalDuration"))


def seul_lance(commande, trouve):
    """Vrai si l'appel de la suite trouvé dans la commande porte `--seul` avant la fin de son segment."""
    segment = re.split(r"[\n;&|]", commande[trouve.end():], maxsplit=1)[0]
    return re.search(r"(?<!\S)--seul\b", segment) is not None


def sorte_outil(appel):
    """Rendre la sorte d'un appel (nom, entrée) parmi `SORTES_OUTIL` : l'outil Artifact est la publication ; une
    commande Bash ou PowerShell, ce qu'elle lance (`COMMANDES`) — la suite avec `--seul`, « --seul » ; le reste
    sinon."""
    nom, entree = appel
    if nom == "Artifact":
        return "publication"
    if nom not in ("Bash", "PowerShell"):
        return "reste"
    commande = sans_heredoc(str(entree.get("command", "")))
    for sorte, motif in COMMANDES:
        trouve = motif.search(commande)
        if trouve:
            return "--seul" if sorte == "suite" and seul_lance(commande, trouve) else sorte
    return "reste"


def verdict_suite(texte, lien):
    """Rendre le verdict d'une sortie de suite : vrai si verte, faux si rouge, None s'il ne s'y lit pas — sortie
    écrite ailleurs, ou suite lancée en fond. L'attente d'une tâche de fond n'en dit pas : sa notification le dit, par
    son code de sortie ; au premier plan, un `ÉCART:` ou un `FIN:` la disent rouge, sinon une ligne `OK` verte."""
    if lien == "fond":
        code = CODE_SORTIE.search(texte)
        return None if code is None else code.group(1) == "0"
    if lien:
        return None
    lignes = texte.splitlines()
    if any(l.startswith(("ÉCART:", "FIN:")) for l in lignes):
        return False
    return True if any(l.strip() == "OK" for l in lignes) else None


def garde_fous(texte):
    """Compter les lignes d'une sortie qui s'ouvrent par chaque garde-fou de `GARDE_FOUS`, le numéro de ligne d'un
    `Read` ôté."""
    if not any(g in texte for g in GARDE_FOUS):
        return (0,) * len(GARDE_FOUS)
    debuts = [NUMERO_READ.sub("", l, count=1).lstrip() for l in texte.splitlines()]
    return tuple(sum(d.startswith(g) for d in debuts) for g in GARDE_FOUS)


def lire_sortie(appel, texte, lien):
    """Rendre ce que `compteur` garde d'une sortie, lue au fil du transcript, sans son texte : (sorte d'outil — None
    pour le message d'une autre session —, 1 si elle compte un appel — 0 pour une notification ou l'attente d'une
    tâche de fond (`lien`) —, verdict de suite — None hors suite, ou s'il ne s'y lit pas —, garde-fous, chacun lu là
    où il dit vrai, puis vrai pour une notification : ce qu'elle ferme n'est pas un appel d'outil, mais l'attente de
    la tâche)."""
    sorte, nom = (None, None) if appel is None else (sorte_outil(appel), appel[0])
    releve = nom in (None, "Agent")
    ou = (sorte in SUITES, sorte == "mutant", nom in ("Bash", "PowerShell"), releve, releve)
    vus = tuple(n if lu else 0 for n, lu in zip(garde_fous(texte), ou))
    verte = verdict_suite(texte, lien) if sorte in SUITES else None
    return sorte, int(appel is not None and not lien), verte, vus, lien.startswith("fond")


def mesure_vide():
    """Rendre la mesure d'une plage à zéro : secondes par part, pauses, durée, secondes et appels par sorte d'outil,
    secondes d'outil fermées par une notification, suites [jugées, vertes], garde-fous."""
    return {"parts": dict.fromkeys(mesure().PARTS, 0.0), "pauses": 0, "duree": 0.0,
            "outils": dict.fromkeys(SORTES_OUTIL, 0.0), "appels": dict.fromkeys(SORTES_OUTIL, 0), "fond": 0.0,
            "suites": [0, 0], "garde_fous": [0] * len(GARDE_FOUS)}


def ajouter_mesure(somme, mesure_):
    """Ajouter une mesure à une autre, en place ; la durée reste None dès qu'une manque."""
    for cle in ("parts", "outils", "appels"):
        for k, v in mesure_[cle].items():
            somme[cle][k] += v
    somme["pauses"] += mesure_["pauses"]
    somme["fond"] += mesure_["fond"]
    somme["duree"] = None if somme["duree"] is None or mesure_["duree"] is None else somme["duree"] + mesure_["duree"]
    somme["suites"] = [x + y for x, y in zip(somme["suites"], mesure_["suites"])]
    somme["garde_fous"] = [x + y for x, y in zip(somme["garde_fous"], mesure_["garde_fous"])]


def compter_sorties(rendu, evenements):
    """Ajouter à la mesure `rendu` ce que disent les sorties d'une plage : les appels par sorte d'outil, les suites
    jouées et vertes, les garde-fous."""
    m = mesure()
    for _, part, lu in evenements:
        if lu is None:
            continue
        sorte, appel, verte, vus, _ = lu
        if part == m.OUTILS:
            rendu["appels"][sorte] += appel
        if verte is not None:
            rendu["suites"] = [rendu["suites"][0] + 1, rendu["suites"][1] + verte]
        rendu["garde_fous"] = [x + y for x, y in zip(rendu["garde_fous"], vus)]


def compter_plage(journaux, plage):
    """Rendre la mesure d'une plage (début, fin] : les événements de chaque journal (`tranche`) sur une ligne de temps
    commune, découpés en parts (`parts`) — l'actif de `--actif` sur les mêmes transcripts ; la durée, de borne à borne,
    None si l'une est ouverte ; le temps d'outil par sorte, et sa part fermée par une notification ; puis ce que
    disent les sorties (`compter_sorties`)."""
    m = mesure()
    rendu = mesure_vide()
    evenements = [e for chemin, j in journaux for e in m.tranche(chemin, j.evenements, plage)]
    rendu["parts"], fermes, rendu["pauses"] = m.parts(evenements)
    rendu["duree"] = plage[1] - plage[0] if -INFINI < plage[0] and plage[1] < INFINI else None
    for secondes, part, lu in fermes:
        if part == m.OUTILS:
            rendu["outils"][lu[0] if lu else "reste"] += secondes
            rendu["fond"] += secondes if lu and lu[4] else 0.0
    compter_sorties(rendu, evenements)
    return rendu


def minutes_reparties(secondes, total=None):
    """Rendre les minutes de chaque nombre de secondes, arrondies pour sommer `total` — par défaut l'arrondi de leur
    somme (`minutes`) : chacun prend ses minutes entières, puis les plus gros restes une de plus."""
    total = mesure().minutes(sum(secondes)) if total is None else total
    entieres = [int(s // 60) for s in secondes]
    ordre = sorted(range(len(secondes)), key=lambda i: secondes[i] / 60 - entieres[i], reverse=True)
    for i in ordre[:max(0, total - sum(entieres))]:
        entieres[i] += 1
    return entieres


def texte_garde_fous(mesure_):
    """Écrire les garde-fous d'une mesure : suites vertes sur jugées (`verdict_suite`), puis le compte de chaque
    garde-fou — un tiret pour aucun —, le verdict du relecteur en ACCEPTÉE et REFUSÉE."""
    jouees, vertes = mesure_["suites"]
    ecart, attrape, garde, acceptee, refusee = mesure_["garde_fous"]
    return "suites %s, ÉCART %s, MUTANT ATTRAPÉ %s, GARDE %s, relecteur %s" % (
        "%d/%d" % (vertes, jouees) if jouees else "-", ecart or "-", attrape or "-", garde or "-",
        "%d ACCEPTÉE + %d REFUSÉE" % (acceptee, refusee) if acceptee or refusee else "-")


def ligne_compteur(nom, mesure_, cout):
    """Écrire la ligne de `compteur` d'une plage : durée, actif réparti en parts, outils par sorte, les tours et le
    prix de `cout`, puis les garde-fous ; les minutes de chaque part et de chaque sorte somment leur total à la minute
    (`minutes_reparties`)."""
    m = mesure()
    actif = minutes_reparties([mesure_["parts"][p] for p in m.PARTS])
    outils = minutes_reparties([mesure_["outils"][s] for s in SORTES_OUTIL], actif[m.PARTS.index(m.OUTILS)])
    duree = "-" if mesure_["duree"] is None else "%d" % m.minutes(mesure_["duree"])
    return "%s · durée %s · actif %d = %s · outils : %s · %d tours · %s · garde-fous : %s" % (
        nom, duree, sum(actif), " + ".join("%s %d" % (p, n) for p, n in zip(m.PARTS, actif)),
        ", ".join("%s %d (%d)" % (s, n, mesure_["appels"][s]) for s, n in zip(SORTES_OUTIL, outils)),
        cout[1], dollars(cout[2]), texte_garde_fous(mesure_))


def manques(journaux):
    """Rendre les lignes `AVERTISSEMENT:` de ce qui manque aux transcripts lus — leur format est interne à Claude Code
    et change d'une version à l'autre : un champ absent se dit, jamais en silence. Les lignes de message sans heure,
    hors du temps ; les sorties dont l'appel n'est pas au transcript, rangées au reste ; une session sans `origin`, où
    rien ne se lit tapé : son attente tombe au reste."""
    rendu = []
    for chemin, j in journaux:
        nom = os.path.basename(chemin)
        if j.sans_heure:
            rendu.append("AVERTISSEMENT: %s : %d ligne(s) de message sans heure, hors du temps" % (nom, j.sans_heure))
        if j.sans_appel:
            rendu.append("AVERTISSEMENT: %s : %d sortie(s) sans appel connu, rangée(s) au reste" % (nom, j.sans_appel))
        if j.users and not j.origines:
            rendu.append("AVERTISSEMENT: %s : %d ligne(s) user, aucune avec origin — l'attente tombe au reste"
                         % (nom, j.users))
    return rendu


def lire_journaux(chemins, sortie):
    """Rendre [(chemin, journal)] des transcripts lisibles, chaque sortie lue au fil (`lire_sortie`) ; un illisible se
    dit, puis ce qui manque aux autres (`manques`)."""
    m = mesure()
    rendu = []
    for chemin in chemins:
        j, erreur = m.journal(chemin, lire_sortie)
        if erreur:
            sortie.write("AVERTISSEMENT: transcript non lu : %s — %s\n" % (chemin, erreur))
            continue
        rendu.append((chemin, j))
    for ligne in manques(rendu):
        sortie.write(ligne + "\n")
    return rendu


def dixiemes(secondes, signe=False):
    """Écrire des secondes en minutes à une décimale, à la virgule — signées si `signe` : un écart."""
    return (("%+.1f" if signe else "%.1f") % (secondes / 60)).replace(".", ",")


def ligne_recoupe(tete, avant, etat, siens):
    """Écrire la ligne de recoupe d'une `cost-state` : les outils, le modèle et la durée du compteur, du `startTime` à
    `avant` — la dernière ligne horodatée avant elle —, face à ses totaux, l'écart signé — pour les outils, aussi sans
    ce que ferme une notification : l'attente d'une tâche de fond n'est pas un appel d'outil ; un champ absent se
    dit."""
    m = mesure()
    debut = etat.get("startTime")
    if not isinstance(debut, (int, float)) or avant is None:
        return "%s · pas de plage — %s" % (tete, "aucune ligne horodatée avant" if avant is None else "startTime absent")
    mesure_ = compter_plage(siens, (debut / 1000, avant))
    nous = {"outils": mesure_["parts"][m.OUTILS], "modèle": mesure_["parts"][m.MODELE], "durée": avant - debut / 1000}
    morceaux = []
    for cle, champ in TOTAUX_COUT:
        eux = etat.get(champ)
        if not isinstance(eux, (int, float)):
            morceaux.append("%s %s contre %s absent" % (cle, dixiemes(nous[cle]), champ))
            continue
        ecart = "écart %s" % dixiemes(nous[cle] - eux / 1000, True)
        if cle == "outils":
            ecart += " ; sans les %s fermées par une notification de fond : %s" % (
                dixiemes(mesure_["fond"]), dixiemes(nous[cle] - mesure_["fond"] - eux / 1000, True))
        morceaux.append("%s %s contre %s %s (%s)" % (cle, dixiemes(nous[cle]), champ, dixiemes(eux / 1000), ecart))
    return "%s · %s" % (tete, " · ".join(morceaux))


def recoupe(journaux, chemin, sortie):
    """Écrire une ligne par `cost-state` d'une session (`etats_cout`), recoupée sur sa plage, session et sous-agents
    (`ligne_recoupe`)."""
    m = mesure()
    etats, erreur = m.etats_cout(chemin)
    if erreur:
        sortie.write("AVERTISSEMENT: recoupe : %s — %s\n" % (chemin, erreur))
        return
    agents = set(m.sous_agents(chemin))
    siens = [(c, j) for c, j in journaux if c == chemin or c in agents]
    for n, avant, etat in etats:
        tete = "RECOUPE %s ligne %d (minutes)" % (os.path.basename(chemin), n)
        sortie.write(ligne_recoupe(tete, avant, etat, siens) + "\n")
    if not etats:
        sortie.write("RECOUPE %s · aucune ligne cost-state\n" % os.path.basename(chemin))


def rangs_compteur(nommees, plages_, decoupe, sortie):
    """Rendre [(nom, plages, coût)] des lignes de `compteur` : une par fiche — les seules nommées, si on en nomme —,
    puis hors fiches quand on n'en nomme pas ; une fiche nommée sans plage se dit en `GARDE:`."""
    (par_fiche, trous), (parts_, hors) = plages_, decoupe
    connues = [ident for ident, _ in par_fiche]
    for ident in nommees:
        if ident not in connues:
            sortie.write("GARDE: fiche sans plage : %s — ni commit « %s : », ni session\n" % (ident, ident))
    rangs = [(ident, [plage], plus(*r)) for (ident, plage), (_, *r) in zip(par_fiche, parts_)
             if not nommees or ident in nommees]
    return rangs if nommees else rangs + [("hors fiches", trous, plus(*hors))]


def cmd_compteur(a, sortie):
    """Dire où passe le temps de chaque fiche, coupée aux commits comme `cout` (VIT17) : l'en-tête, une ligne par fiche
    (`ligne_compteur`), hors fiches et `TOTAL` — seulement les fiches nommées, si on en nomme ; `--recoupe` : puis une
    ligne par `cost-state` des sessions (`recoupe`). Sans découpe, une `GARDE:` et 1 ; une fiche nommée sans plage : 1."""
    lignes = lignes_de(chemin_garde(a.fichier))
    decoupe, pourquoi, gardes, (fiches_, heures, fin) = decoupe_et_heures(a.fichier, lignes)
    for g in gardes:
        sortie.write(g + "\n")
    if not decoupe:
        sortie.write("GARDE: pas de découpe — %s\n" % pourquoi[0])
        return 1
    fichiers = transcripts_du_fichier(fiches_, sessions_entete(lignes), [])
    journaux = lire_journaux([c for c, sorte in fichiers if sorte < 2], sortie)
    sortie.write(ENTETE_COMPTEUR % (mesure().PAUSE // 60) + "\n")
    rangs = rangs_compteur(a.fiches, plages_du_cout(fiches_, heures, [], fin), decoupe, sortie)
    total = mesure_vide()
    for nom, bornes, cout in rangs:
        mesure_ = mesure_vide()
        for plage in bornes:
            ajouter_mesure(mesure_, compter_plage(journaux, plage))
        sortie.write(ligne_compteur(nom, mesure_, cout) + "\n")
        ajouter_mesure(total, mesure_)
    nom = "TOTAL (fiches nommées)" if a.fiches else "TOTAL (fiches + hors fiches)"
    sortie.write(ligne_compteur(nom, total, plus(*[r[2] for r in rangs])) + "\n")
    for chemin in [c for c, sorte in fichiers if sorte == 0] if a.recoupe else []:
        recoupe(journaux, chemin, sortie)
    return int(len(rangs) < len(set(a.fiches)))


KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VLP_PY = os.path.join(KIT, "scripts", "vlp.py")   # le lanceur : les commandes qu'on affiche le nomment (VIT5)


def cmd_lire(chemins, sortie):
    """Un `cat` d'un fichier du kit est hors du projet : PowerShell le refuse
    (chantier U). Python, lui, est permis par `allowed-tools`."""
    racine = os.path.realpath(KIT)
    code = 0
    for c in chemins:
        vrai = os.path.realpath(os.path.join(racine, c))
        if os.path.commonpath([racine, vrai]) != racine:
            sortie.write("GARDE: hors du kit : %s\n" % c)
            code = 1
        elif not os.path.isfile(vrai):
            sortie.write("ABSENT %s\n" % c)
            code = 1
        else:
            texte = lire(vrai)
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
        if git_texte(["rev-parse", "--git-dir"], dossier)[0] != 0:
            sortie.write("SANS GIT\n")
            return 0 if cocher else 1
        code, tete = git_texte(["log", "-1", "--format=%h %s"], dossier)
        sha, _, sujet = tete.strip().partition(" ") if code == 0 else ("", "", "")
        if re.match(r"%s\s*:" % re.escape(a.fiche), sujet):
            sortie.write("TÊTE %s %s\n" % (sha, sujet))
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
            lignes[t:n] = ["**Tentatives** (%s) — résolu par : %s" % (date, a.resolu)]
            fin -= n - t - 1
    s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if s and "**Session** : %s" % s not in lignes[debut:fin]:
        dep = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Dépend de**")), debut + 1)
        lignes.insert(dep, "**Session** : %s" % s)
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("COCHÉ %s · Session %s\n" % (a.fiche, s or "absente"))
    return 0


def garde_avant_coche(a, titre):
    """Rendre la `GARDE:` qui empêche de cocher `a.fiche` — déjà cochée, ou, dans le kit, sans suite entière verte sur
    le code d'aujourd'hui (VIT11) —, ou `None`."""
    if not titre.startswith("## %s [ ]" % a.fiche):
        return "GARDE: %s déjà cochée — rien écrit\n" % a.fiche
    kit = suite_manquante(a.fichier)
    if kit:
        return ("GARDE: %s non cochée — la suite entière n'a pas tourné verte sur le code d'aujourd'hui : "
                "py -3 \"%s/scripts/test-vlp.py\", puis cocher (VIT11)\n" % (a.fiche, kit))
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


def refuser(a, lignes, debut, sortie):
    """Le refus du relecteur (chantier REV) : la case rouverte, et sous le titre le bloc de
    `tache-blocage.md` — déjà là, il gagne la ligne numérotée suivante et son `Erreur :` prend
    le nouveau motif ; il ne se double jamais."""
    fin = next((i for i in range(debut + 1, len(lignes))
                if lignes[i].strip() == FERMANT or TITRE.match(lignes[i])), len(lignes))
    lignes[debut] = lignes[debut].replace("[x]", "[ ]", 1)
    date = a.date or __import__("datetime").date.today().isoformat()
    essai, erreur = ESSAI_REFUSE, "Erreur : %s" % a.refuser
    bloc = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Tentatives**")), None)
    if bloc is None:
        # Sous le titre, après sa ligne vide s'il en a une — comme les blocs écrits à la main.
        k = debut + 2 if debut + 1 < fin and not lignes[debut + 1].strip() else debut + 1
        lignes[k:k] = (["**Tentatives** (%s) — non résolu." % date, "1. " + essai, erreur]
                       + ([""] if k == debut + 2 else []))
        n_refus = 1
    else:
        n = next((i for i in range(bloc + 1, fin) if not lignes[i].strip() or lignes[i].startswith("**")), fin)
        if "non résolu" not in lignes[bloc]:
            lignes[bloc] = "**Tentatives** (%s) — non résolu." % date
        numeros = [i for i in range(bloc + 1, n) if re.match(r"[0-9]+\. ", lignes[i])]
        # Compte avant l'ajout : seules les tentatives qui étaient déjà un refus de relecture.
        n_refus = 1 + sum(1 for i in numeros if lignes[i].split(". ", 1)[1] == essai)
        p = numeros[-1] + 1 if numeros else bloc + 1
        suivant = int(lignes[numeros[-1]].split(".")[0]) + 1 if numeros else 1
        lignes.insert(p, "%d. %s" % (suivant, essai))
        e = next((i for i in range(p + 1, n + 1) if lignes[i].startswith("Erreur :")), None)
        if e is None:
            lignes.insert(p + 1, erreur)
        else:
            lignes[e] = erreur
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("REFUSÉ %s · refus %d\n" % (a.fiche, n_refus))
    return 0


# --- relecture ---------------------------------------------------------------

RELECTURE = "vlp-relecture-"    # le préfixe des worktrees de relecture : `--retirer` ne retire qu'eux


def git_texte(args, cwd, env=None):
    """(code, texte) de `git <args>` dans `cwd` : la sortie si le code vaut 0, sinon la première ligne
    d'erreur. Git qui ne se lance pas : (None, raison) — jamais un traceback."""
    import subprocess
    try:
        r = subprocess.run([GIT, "-c", "core.quotepath=false"] + args, cwd=cwd, env=env, capture_output=True,
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
    principal = os.path.realpath(kit or KIT)
    lieux = []
    for d in (principal, racine):
        code, t = git_texte(["rev-parse", "--path-format=absolute", "--git-common-dir", "--show-toplevel"], d)
        if code != 0 or len(t.split()) < 2:
            return None
        lieux.append([os.path.normcase(os.path.realpath(x)) for x in t.strip().split("\n")[:2]])
    if lieux[0][0] != lieux[1][0] or lieux[0][1] == lieux[1][1]:
        return None
    code, tete = git_texte(["rev-parse", "HEAD"], principal)
    code2, n = git_texte(["rev-list", "--count", "%s..HEAD" % tete.strip(), "--"] + list(CODE_PLUGIN), racine)
    if code != 0 or code2 != 0 or not n.strip().isdigit() or int(n) == 0:
        return None
    _, branche = git_texte(["rev-parse", "--abbrev-ref", "HEAD"], racine)
    if branche.strip() == "HEAD":
        _, branche = git_texte(["rev-parse", "--short", "HEAD"], racine)
    return int(n), principal, branche.strip()


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
        # Le cache de Python n'est jamais du contexte : il reste ignoré sans écart.
        chemins = [l for l in t.split("\n") if l and not l.endswith("__pycache__/")] if code == 0 else []
        etat[nom] = regrouper_dossiers(racine, chemins)
    return etat


def ligne_git(racine):
    """Les lignes `GIT=` de la carte : `GIT=suivi`, `GIT=hors Git`, ou `GIT=ignoré …` et/ou `GIT=non ajouté …`."""
    etat = etat_git(racine)
    if etat is None:
        return ["GIT=hors Git"]
    lignes = ["GIT=%s %s" % (nom, ", ".join(n for n, _ in liste)) for nom, liste in etat.items() if liste]
    return lignes or ["GIT=suivi"]


def prefixe_relecture():
    """`vlp-relecture-`, ou `vlp-relecture-<canal>-` quand `VLP_CANAL` est posé (chantier NUI) : deux
    canaux de nuit relisent dans le même dépôt, chacun ne retire que ses worktrees."""
    canal = re.sub(r"[^\w.]", "_", os.environ.get(carnet.ENV_CANAL, "").strip())
    return RELECTURE + (canal + "-" if canal else "")


def retirer_relectures(racine):
    """Retire les worktrees `vlp-relecture-*` du dépôt — ceux du canal seul si `VLP_CANAL` est posé —,
    puis `prune` : le nombre retiré."""
    code, liste = git_texte(["worktree", "list", "--porcelain"], racine)
    n = 0
    for ligne in liste.splitlines() if code == 0 else []:
        chemin = ligne[len("worktree "):] if ligne.startswith("worktree ") else ""
        if os.path.basename(chemin.rstrip("/\\")).startswith(prefixe_relecture()):
            n += git_texte(["worktree", "remove", "--force", chemin], racine)[0] == 0
    git_texte(["worktree", "prune"], racine)
    return n


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


def noms_fichiers(fiche):
    """Ce que nomme la ligne **Fichiers** d'une fiche, jusqu'à la ligne vide ou au champ suivant :
    chaque `…` entre backticks, et chaque mot hors d'eux — le gabarit n'en met pas."""
    k = next((i for i, l in enumerate(fiche) if l.startswith("**Fichiers**")), None)
    if k is None:
        return set()
    para = [fiche[k][len("**Fichiers**"):]]
    for l in fiche[k + 1:]:
        if not l.strip() or l.startswith(("**", "<!--")):
            break
        para.append(l)
    texte = " ".join(para)
    return (set(re.findall(r"`([^`]+)`", texte))
            | set(re.split(r"[\s,;:()]+", re.sub(r"`[^`]*`", " ", texte)))) - {""}


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
        sortie.write("RETIRÉ %d\n" % retirer_relectures(racine))
        return 0
    if not a.fiche or projet is None:
        sortie.write("GARDE: %s\n" % ("relecture <fiche> [--sha S], ou relecture --retirer" if not a.fiche
                                      else "pas de CHANTIER.md au-dessus de %s" % os.getcwd()))
        return 1
    retirer_relectures(racine)
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
        d = tempfile.mkdtemp(prefix=prefixe_relecture() + nom + "-")
        code, err = git_texte(["worktree", "add", "--detach", d, rev], racine)
        dossiers.append(d)
        if code != 0:
            retirer_relectures(racine)
            sortie.write("GARDE: worktree %s impossible — %s\n" % (nom, err))
            return 1
    # Le fichier de fiches que nomme CHANTIER.md dans APRÈS, au même endroit du dépôt que le projet.
    code, prefixe = git_texte(["rev-parse", "--show-prefix"], projet)
    prefixe = prefixe.strip() if code == 0 else ""
    apres_projet = os.path.normpath(os.path.join(dossiers[0], prefixe))
    # Le chantier du dossier qui relit, pas celui de la copie : APRÈS est un worktree détaché, que la règle des
    # branches de `courant_de` verrait toujours hériter de la principale (chantier NUI22).
    courant = courant_de(projet) if equipe(apres_projet) else None
    fichier = os.path.normpath(os.path.join(apres_projet, courant)) if courant else ""
    fiche, _ = extraire_lignes(lignes_de(fichier) if os.path.isfile(fichier) else [], a.fiche)
    if not fiche:
        retirer_relectures(racine)
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
    """Ce que `/vlp:init` regarde avant d'équiper, sans `pwd`, `ls`, `head` ni `grep`."""
    d = os.path.abspath(dossier)
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
SEUIL_CLAUDE = 80
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
    code = cmd_valider_seul(chemins, sortie)
    for chemin in chemins if plan else []:
        for n, l in enumerate(lignes_de(chemin) if os.path.isfile(chemin) else [], 1):
            if PLAN.match(l):
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


# --- hook --------------------------------------------------------------------

MARQUE = re.compile(r"^<!-- FICHE:[A-Z]{1,3}[0-9]+ -->$")


def est_fichier_de_fiches(lignes):
    """Un marqueur de fiche ou le titre du socle, hors bloc de code : la méthode
    et les commandes en montrent dans des blocs, elles ne sont pas des fiches."""
    code = False
    for l in lignes:
        if l.lstrip().startswith("```"):
            code = not code
        elif not code and (MARQUE.match(l.strip()) or l.startswith("## Le socle commun")):
            return True
    return False


def cmd_hook(entree, sortie, erreur):
    try:
        d = json.loads(entree.read())
    except ValueError:
        return 0
    ti = d.get("tool_input") if isinstance(d, dict) else None
    chemin = ti.get("file_path") if isinstance(ti, dict) else None
    if not isinstance(chemin, str) or not chemin.lower().endswith(".md"):
        return 0
    if not os.path.isabs(chemin) and isinstance(d.get("cwd"), str):
        chemin = os.path.join(d["cwd"], chemin)
    if not os.path.isfile(chemin):
        return 0
    lignes = lignes_de(chemin)
    if not est_fichier_de_fiches(lignes):
        return 0
    texte = io.StringIO()
    if rapport(chemin, lignes, texte):
        erreur.write(texte.getvalue() + "Corrige ce fichier de fiches avant de continuer.\n")
        return 2
    bilan = texte.getvalue().strip().splitlines()[-1]
    sortie.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": bilan}},
                            ensure_ascii=False) + "\n")
    return 0


# --- filet -------------------------------------------------------------------

SEUIL_FILET = 3  # Tours restants à partir desquels on avertit le sous-agent


def cmd_filet(entree, sortie, erreur):
    """Avertit quand le sous-agent approche du plafond de tours.

    Lit le JSON du hook sur stdin — `PostToolUse` ou `PostToolUseFailure`, après
    tout outil. Si nous sommes dans un sous-agent (agent_type contient 'fiche'
    et agent_id existe), compte les tours déjà rendus et avertit si
    tours_restants <= SEUIL_FILET, au nom de l'événement reçu.
    Une fois par tour : le tampon `vlp-filet-<agent_id>-<tours>` (`tampon_neuf`) tait les suivants (TOU2).
    """
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0

    # Vérifier que c'est un sous-agent de fiche
    agent_type = d.get("agent_type", "")
    agent_id = d.get("agent_id")
    if "fiche" not in agent_type or not agent_id:
        return 0

    transcript_path = d.get("transcript_path")
    if not isinstance(transcript_path, str):
        return 0

    # Chemin du transcript du sous-agent
    # Sur Windows, les chemins JSON peuvent avoir des barres obliques
    transcript_path_os = transcript_path.replace("/", os.sep)
    base = os.path.splitext(transcript_path_os)[0]
    subagent_path = os.path.join(base, "subagents", f"agent-{agent_id}.jsonl")

    # Compter les tours du sous-agent — None : le transcript ne s'ouvre pas
    tours = comptoir_tours(subagent_path)
    if tours is None:
        return 0

    # Lire maxTurns depuis agents/fiche.md
    # Le chemin est relatif au kit — nous sommes dans scripts/vlp.py
    kit_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fiche_path = os.path.join(kit_root, "agents", "fiche.md")

    max_turns = lire_max_turns(fiche_path)
    if max_turns is None:
        return 0

    tours_restants = max_turns - tours
    if 0 < tours_restants <= SEUIL_FILET and tampon_neuf(f"vlp-filet-{agent_id}-{tours}"):
        tour_mot = "tour" if tours_restants == 1 else "tours"
        message = f"Attention : {tours_restants} {tour_mot} restant{'s' if tours_restants > 1 else ''}. Rends ton statut maintenant — RETOUR avec ce qui est fait et ce qui reste, si la fiche n'est pas finie."
        # Même forme après un succès ou un échec (doc des hooks, lue le 2026-09-24) :
        # seul le nom change, celui de l'événement reçu.
        evenement = d.get("hook_event_name") or "PostToolUse"
        sortie.write(json.dumps(
            {"hookSpecificOutput": {"hookEventName": evenement, "additionalContext": message}},
            ensure_ascii=False
        ) + "\n")

    return 0


def comptoir_tours(chemin):
    """Compte les tours distincts (message.id) dans un transcript de sous-agent ;
    None s'il ne s'ouvre pas. Ouvert par `ouvrir` de mesure-tokens.py : sous
    Windows, dès 260 caractères, isfile et open disent absent un fichier présent (FIL1)."""
    tours = set()
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue
                try:
                    d = json.loads(ligne)
                    message = d.get("message")
                    if isinstance(message, dict):
                        usage = message.get("usage")
                        if isinstance(usage, dict):
                            mid = message.get("id")
                            if mid:
                                tours.add(mid)
                except json.JSONDecodeError:
                    pass
    except UnicodeDecodeError:
        pass
    except OSError:
        return None
    return len(tours)


def lire_max_turns(chemin):
    """Lit maxTurns depuis le frontmatter YAML d'un fichier."""
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            lignes = f.readlines()
    except (OSError, UnicodeDecodeError):
        return None

    # Chercher le frontmatter YAML
    if len(lignes) < 2 or not lignes[0].strip().startswith("---"):
        return None

    for i in range(1, len(lignes)):
        ligne = lignes[i].strip()
        if ligne.startswith("---"):
            break
        if ligne.startswith("maxTurns:"):
            try:
                return int(ligne.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass

    return None


# --- contrat (chantier CON) ----------------------------------------------------

# Les verbes Git qui ne font que lire : tout autre verbe écrit, inconnu compris (chantier VRB).
LECTURE_GIT = frozenset(("diff", "status", "log", "show", "rev-parse", "ls-files", "blame", "grep"))
# Un appel Git : `git` en position de commande — début de ligne, après `;` `&` `|` `(` `)` `{` un
# accent grave, une quote ouvrante (`ssh h 'git …'`) ou au bout d'un chemin (`…/git.exe`), derrière
# d'éventuels `VAR=val`, `sudo`, `if`… —, ses options globales, puis son verbe (`verbe`). Ancré
# pour que `grep -c git f` ne lise pas le verbe `f`.
APPEL_GIT = re.compile(
    r"""(?:^|(?<=[;&|(){`'"/\\]))[ \t]*"""
    r"""(?:(?:\w+=\S*|sudo|env|time|command|nohup|exec|xargs|if|then|else|do|while|until|!)[ \t]+)*"""
    r"""git(?:\.exe)?['"]?(?![\w.-])"""
    r"""(?:[ \t]+(?:-[Cc][ \t]+(?:"[^"]*"|'[^']*'|\S+)|--no-pager|-P|--(?:git-dir|work-tree|namespace)=\S+))*"""
    r"""(?:[ \t]+(?P<verbe>-\S*|[A-Za-z][\w-]*))?""", re.M)
# Un heredoc `<<[-]MOT` (mot nu ou cité) : sa ligne d'ouverture, dont la suite (groupe 3), son
# corps (groupe 4), sa fin.
HEREDOC = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_]\w*)\1([^\n]*)\n(.*?)\n[ \t]*\2[ \t]*$", re.S | re.M)
STATUTS = ("FAITE", "RETOUR", "BLOQUÉE")
# Le cœur du refus du gardien (chantier ENQ) : `cmd_gardien` le met dans sa raison, `lire_contrat`
# le retrouve dans le `tool_result` d'un appel qui écrit dans Git pour le compter en bloqué plutôt
# qu'en écrit — indépendant de l'agent (`vlp:fiche`/`vlp:relecture`) et de la fin de phrase.
# `REFUS_GIT_AVANT`, celui d'avant VRB, se reconnaît encore dans les vieilles transcriptions.
REFUS_GIT = "retire tout appel Git hors lecture (diff, status, log, show…), le chef commite après"
REFUS_GIT_AVANT = "retire git commit/add/reset, le chef commite après"
# Un message utilisateur qui commence ainsi, après le dernier texte de l'assistant, marque le
# sous-agent interrompu plutôt que sans statut en tête (chantier ENQ).
INTERROMPU = "[Request interrupted by user"


def sans_heredoc(commande):
    """La commande, le corps des heredocs qui ne font qu'écrire un fichier tu : reçus par `cat`
    ou `tee`, hors `$(…)` et accents graves, sans `|` derrière — un heredoc reçu par `py`,
    `bash`… s'exécute, il reste lu ; les chaînes citées aussi (`ssh '…'`) (chantiers ECH, ECA)."""
    def taire(m):
        avant = commande[:m.start()]
        mots = [w for w in re.split(r"[;&|(\n`]", avant)[-1].split() if not re.match(r"\w+=", w)]
        recoit = os.path.basename(mots[0].strip("'\"")).lower() if mots else ""
        dans_sous = re.search(r"(?:\$\(|`)[^;&|()\n`]*$", avant)
        if recoit not in ("cat", "tee") or dans_sous or "|" in m.group(3):
            return m.group(0)
        return commande[m.start():m.start(4)] + commande[m.end(4):m.end()]
    return HEREDOC.sub(taire, commande)


ECHO_DONNEE = re.compile(r"""\b(?:echo|printf)\b(?P<args>[^\n;&|`]*?)"""
                         r"""(?:(?P<redir>>{1,2})[ \t]*(?:"[^"]*"|'[^']*'|\S+)|(?=[\n;&]|$))""", re.M)


def sans_echo(commande):
    """La commande, le texte cité d'un `echo`/`printf` dont la sortie va dans un fichier (`>`/`>>`)
    ou à l'écran tu : sans `|` dans le même segment, hors `$(…)` et accents graves — comme
    `sans_heredoc` pour `cat`/`tee` (chantier ENQ ; l'écran, dette VRB). Un `"…$(…)…"` reste lu :
    il s'exécute. Limite acceptée : `echo 'git add' > s.sh` puis `sh s.sh` passe — le
    gardien arrête une habitude, pas un attaquant."""
    def taire(m):
        avant = commande[:m.start()]
        dans_sous = re.search(r"(?:\$\(|`)[^;&|()\n`]*$", avant)
        if dans_sous:
            return m.group(0)
        args = re.sub(r"'[^']*'", "''", m.group("args"))
        args = re.sub(r'"[^"]*"', lambda q: q.group(0) if "$(" in q.group(0) else '""', args)
        return commande[m.start():m.start("args")] + args + commande[m.end("args"):m.end()]
    return ECHO_DONNEE.sub(taire, commande)


def ecrit_git(commande):
    """Vrai si un `APPEL_GIT` de la commande a un verbe hors `LECTURE_GIT` — une option inconnue
    en tient lieu, `git` seul n'écrit pas (chantier VRB). Lu sur la commande `sans_heredoc` puis
    `sans_echo` : un heredoc ou un `echo`/`printf` qui ne font qu'écrire les mots `git commit` dans
    un fichier n'écrivent pas dans Git (chantiers ECH, ENQ)."""
    return any(m.group("verbe") not in (None, *LECTURE_GIT)
               for m in APPEL_GIT.finditer(sans_echo(sans_heredoc(commande))))


def lire_contrat(chemin):
    """(premier mot du dernier message texte, appels qui écrivent dans Git, ceux que le gardien a
    bloqués (`REFUS_GIT` dans leur `tool_result`), interrompu) d'une transcription. Un appel qui
    écrit dans Git compte d'abord en écrit ; si son `tool_result` porte `REFUS_GIT`, il bascule en
    bloqué — sans `tool_result` (transcription coupée), il reste écrit. (None, 0, 0, False) si
    elle ne s'ouvre pas."""
    mot, git, bloque, interrompu = "", 0, 0, False
    en_attente = {}
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    d = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                m = d.get("message") if isinstance(d, dict) else None
                if not isinstance(m, dict):
                    continue
                contenu = m.get("content")
                if m.get("role") == "user":
                    for b in contenu if isinstance(contenu, list) else []:
                        if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                            continue
                        tid = b.get("tool_use_id")
                        if tid not in en_attente:
                            continue
                        texte_res = b.get("content")
                        if isinstance(texte_res, list):
                            texte_res = " ".join(x.get("text", "") for x in texte_res if isinstance(x, dict))
                        if isinstance(texte_res, str) and (REFUS_GIT in texte_res or REFUS_GIT_AVANT in texte_res):
                            git -= 1
                            bloque += 1
                        del en_attente[tid]
                    texte = contenu if isinstance(contenu, str) else None
                    if texte is None and isinstance(contenu, list):
                        textes = [x.get("text", "") for x in contenu if isinstance(x, dict) and x.get("type") == "text"]
                        texte = textes[0] if textes else None
                    if mot and isinstance(texte, str) and texte.startswith(INTERROMPU):
                        interrompu = True
                    continue
                if m.get("role") != "assistant" or not isinstance(contenu, list):
                    continue
                for b in contenu:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and b.get("text", "").strip():
                        mot, interrompu = b["text"].split()[0], False
                    elif b.get("type") == "tool_use" and b.get("name") in ("Bash", "PowerShell"):
                        commande = (b.get("input") or {}).get("command")
                        if isinstance(commande, str) and ecrit_git(commande):
                            git += 1
                            en_attente[b.get("id")] = True
    except (OSError, UnicodeDecodeError):
        return None, 0, 0, False
    return mot, git, bloque, interrompu


def type_agent(chemin):
    """L'`agentType` du `.meta.json` voisin ; `?` s'il manque ou ne se lit pas."""
    try:
        with mesure().ouvrir(chemin[:-len(".jsonl")] + ".meta.json") as f:
            return json.load(f).get("agentType") or "?"
    except (OSError, ValueError, AttributeError):
        return "?"


def ouverture(chemin):
    """(heure, None) : l'heure d'auteur du plus ancien commit qui ajoute le fichier de fiches —
    « Chantier X ouvert » pour 69 fichiers sur 80 ; le premier commit qui nomme le préfixe est
    souvent l'ajout à la TODO (chantier CHK). (None, raison) sans git ou sans ce commit."""
    import subprocess
    try:
        r = subprocess.run([GIT, "log", "--diff-filter=A", "--format=%at", "--", os.path.basename(chemin)],
                           cwd=os.path.dirname(os.path.abspath(chemin)), capture_output=True, encoding="utf-8",
                           errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "git ne se lance pas : %s" % e
    heures = r.stdout.split()
    if r.returncode or not heures or not heures[-1].isdigit():
        return None, "aucun commit n'ajoute ce fichier : l'ouverture n'est pas commitée"
    return int(heures[-1]), None


def cmd_contrat(a, sortie):
    """Une ligne par transcription de sous-agent : id, type, départ de la session parente, dernier
    mot (`(interrompu)` sinon), appels qui écrivent dans Git, ceux que le gardien a bloqués ; puis
    le bilan. Un interrompu ne compte pas en sans-statut (chantier ENQ). `--ouverture` :
    ceux partis — leur heure à eux, pas celle de la session parente — depuis l'ajout du fichier."""
    m = mesure()
    depuis = ouvert = None
    if a.depuis:
        depuis, err = m.borne(a.depuis)
        if err:
            sortie.write("GARDE: --depuis %s : %s\n" % (a.depuis, err))
            return 1
    if a.ouverture:
        ouvert, err = ouverture(a.ouverture)
        if err:
            sortie.write("GARDE: --ouverture %s : %s\n" % (a.ouverture, err))
            return 1
        sortie.write("DEPUIS %s · ouverture de %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ouvert)),
                                                        a.ouverture))
    chemins = a.transcriptions
    if not chemins:
        motif = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", "*", *m.SOUS_AGENTS)
        chemins = [c for c in sorted(glob.glob(motif)) if type_agent(c) == "vlp:fiche"]
    n = commitent = bloques = sans_statut = interrompus = 0
    for c in chemins:
        parent = os.path.dirname(os.path.dirname(c)) + ".jsonl"
        t, _ = m.depart(parent)     # absente ou illisible : t None
        if depuis is not None and (t is None or t < depuis):
            continue
        if ouvert is not None and (m.depart(c)[0] or 0) < ouvert:
            continue
        mot, git, bloque, interrompu = lire_contrat(c)
        if mot is None:
            sortie.write("ILLISIBLE %s\n" % c)
            continue
        heure_ = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t is not None else "?"
        id_ = os.path.basename(c)[len("agent-"):-len(".jsonl")]
        affiche = "(interrompu)" if interrompu else (mot or "(vide)")
        sortie.write("%s %s %s %s git %d bloqué %d\n" % (id_, type_agent(c), heure_, affiche, git, bloque))
        n += 1
        commitent += git > 0
        bloques += bloque > 0
        if interrompu:
            interrompus += 1
        elif mot not in STATUTS:
            sans_statut += 1
    sortie.write("CONTRAT %d sous-agents · %d écrivent dans Git · %d bloqués par le gardien · "
                 "%d sans statut en tête · %d interrompus\n" % (n, commitent, bloques, sans_statut, interrompus))
    return 0


VERDICTS = ("ACCEPTÉE", "REFUSÉE")     # les mots de tête de `vlp:relecture`
ESSAI_REFUSE = "FAITE refusée à la relecture."   # la ligne numérotée que `cocher --refuser` écrit ; boucle.py l'importe
JAUGE = ("Tout va bien", "Ça tient, mais", "Imprévu", "Pas bon", "Grosse erreur")
# La forme d'une jauge (chantier OUV) : un de ces émojis en tête, ou le mot suivi de `—`, `…`
# ou de la fin de ligne — `- Imprévu : j'ai dû…` est une puce, pas une jauge.
EMOJIS_JAUGE = ("✅", "🟢", "⚠", "❌", "🔥")
SUITE_JAUGE = re.compile(r"\*{0,2}\.?\*{0,2}[ \t]*(?:—|–|…|$)")


REGLES = ("tout", "tiret", "deux", "tete")     # la partie du texte que juge `forme_texte` (chantier JUG)
REGLE = "tete"     # retenue en JUG1 : le défaut du gardien et de `forme` ; `tout` rejoue l'ancienne mesure


def ouvre(ligne):
    """La ligne sans ses marques de tête — espaces, `#`, `*`, `-`, `>` et émojis ; `«` reste."""
    i = 0
    while i < len(ligne) and (ligne[i] in " \t#*->" or unicodedata.category(ligne[i]) in ("So", "Mn", "Cf")):
        i += 1
    return ligne[i:]


def forme_texte(texte, regle=REGLE):
    """(resume 0|1, jauge 0|1) de la partie du texte que juge `regle` ; (0, 0) si vide ou absent.
    `tete` (défaut, celle du gardien) : le mot doit ouvrir une ligne, marques retirées — une
    citation en milieu de phrase ne compte pas — et une jauge en avoir la forme, `EMOJIS_JAUGE`
    en tête ou `SUITE_JAUGE` derrière (chantier OUV) ; `tout` : le texte entier ; `tiret` : après la
    dernière ligne `---`, sinon tout ; `deux` : les deux dernières lignes non vides."""
    if not isinstance(texte, str):
        return 0, 0
    lignes = texte.splitlines()
    if regle == "tete":
        tetes = [(l[:len(l) - len(ouvre(l))], ouvre(l)) for l in lignes]
        return (int(any(t.startswith("En résumé") for _, t in tetes)),
                int(any(re.match(re.escape(j) + r'\b', t) and (any(e in marques for e in EMOJIS_JAUGE)
                                                               or SUITE_JAUGE.match(t[len(j):]))
                        for marques, t in tetes for j in JAUGE)))
    if regle == "tiret":
        tirets = [i for i, l in enumerate(lignes) if l.strip() == "---"]
        if tirets:
            texte = "\n".join(lignes[tirets[-1] + 1:])
    elif regle == "deux":
        texte = "\n".join([l for l in lignes if l.strip()][-2:])
    resume = int("En résumé" in texte)
    # Mots entiers, pas sous-chaîne : « Pas bon » ne matche pas « Pas bonne » ; `tete` borne de même
    jauge = int(any(re.search(r'\b' + re.escape(j) + r'\b', texte) for j in JAUGE))
    return resume, jauge


def lire_forme(chemin, regle=REGLE):
    """(caractères par type User/Project/AutoMem, resume 0|1, jauge 0|1, tete 0|1) d'une
    transcription, resume et jauge selon `regle` ; (None, 0, 0, 0) si elle ne s'ouvre pas. Les fichiers d'instructions sont
    ceux du premier attachment `instructions` — une entrée de premier niveau
    `{"attachment": {"type": "instructions", "files": […]}}`, pas un champ de `message`."""
    chars = {"User": 0, "Project": 0, "AutoMem": 0}
    vu, dernier = False, ""
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    d = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                if not isinstance(d, dict):
                    continue
                att = d.get("attachment")
                if not vu and isinstance(att, dict) and att.get("type") == "instructions":
                    vu = True
                    for fi in att.get("files") or []:
                        if isinstance(fi, dict) and fi.get("type") in chars and isinstance(fi.get("content"), str):
                            chars[fi["type"]] += len(fi["content"])
                m = d.get("message")
                if not isinstance(m, dict) or m.get("role") != "assistant" or not isinstance(m.get("content"), list):
                    continue
                for b in m["content"]:
                    if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                        dernier = b["text"].strip()
    except (OSError, UnicodeDecodeError):
        return None, 0, 0, 0
    resume, jauge = forme_texte(dernier, regle)
    tete = int(bool(dernier) and dernier.split()[0] in STATUTS + VERDICTS)
    return chars, resume, jauge, tete


def cmd_forme(a, sortie):
    """Une ligne par transcription de sous-agent : id, type, départ, et caractères
    d'instructions par type, plus resume, jauge, tete ; puis le bilan."""
    m = mesure()
    depuis = None
    if a.depuis:
        depuis, err = m.borne(a.depuis)
        if err:
            sortie.write("GARDE: --depuis %s : %s\n" % (a.depuis, err))
            return 1
    chemins = a.transcriptions
    if not chemins:
        motif = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", "*", *m.SOUS_AGENTS)
        chemins = [c for c in sorted(glob.glob(motif)) if type_agent(c) in ("vlp:fiche", "vlp:relecture")]
    n = resume_total = jauge_total = tete_total = user_total = 0
    for c in chemins:
        t, _ = m.depart(c)
        if depuis is not None and (t is None or t < depuis):
            continue
        chars, resume, jauge, tete = lire_forme(c, a.regle)
        if chars is None:
            sortie.write("ILLISIBLE %s\n" % c)
            continue
        heure_ = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t is not None else "?"
        id_ = os.path.basename(c)[len("agent-"):-len(".jsonl")]
        sortie.write("%s %s %s user %d projet %d memoire %d resume %d jauge %d tete %d\n" % (
            id_, type_agent(c), heure_, chars["User"], chars["Project"], chars["AutoMem"], resume, jauge, tete))
        n += 1
        user_total += chars["User"]
        resume_total += resume
        jauge_total += jauge
        tete_total += tete
    user_moyenne = user_total // n if n > 0 else 0
    sortie.write("FORME %d sous-agents · user %d car. · resume %d · jauge %d · tete %d\n"
                 % (n, user_moyenne, resume_total, jauge_total, tete_total))
    return 0


FICHE_A_JOUER = re.compile(r"Fiche à jouer :\s*(\S+)")


def fiche_jouee(chemin):
    """La fiche que `vlp:jouer` a donnée au sous-agent : `Fiche à jouer :` suivi de son id, dans
    le premier message utilisateur de sa transcription ; None si rien ne se lit."""
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    m = json.loads(ligne).get("message")
                except (ValueError, AttributeError):
                    continue
                if not isinstance(m, dict) or m.get("role") != "user":
                    continue
                c = m.get("content")
                texte = c if isinstance(c, str) else " ".join(
                    b.get("text", "") for b in c if isinstance(b, dict)) if isinstance(c, list) else ""
                t = FICHE_A_JOUER.search(texte)
                return t.group(1) if t else None
    except (OSError, UnicodeDecodeError):
        return None
    return None


def verdict_fin(d, deja_renvoye=False):
    """La raison de renvoyer au travail un sous-agent `vlp:fiche` qui s'arrête, ou None.
    `deja_renvoye` (`stop_hook_active`) : la tête n'est plus jugée — un troisième renvoi ne la
    corrigerait pas —, un `FAITE` l'est encore (chantier GAR)."""
    message = d.get("last_assistant_message")
    if not isinstance(message, str):
        return None
    mot = message.split()[0] if message.strip() else "(vide)"
    if mot not in STATUTS:
        return None if deja_renvoye else (
            "Ton dernier message commence par « %s » : son premier mot doit être FAITE, RETOUR ou "
            "BLOQUÉE (agents/fiche.md). Réécris-le, statut en tête." % mot)
    if mot != "FAITE" or not isinstance(d.get("agent_transcript_path"), str):
        return None
    fiche = fiche_jouee(d["agent_transcript_path"])
    racine = trouver(d.get("cwd") or os.getcwd())
    if fiche is None or racine is None:
        return None
    try:
        courant = courant_de(racine)
    except Absent:
        return None
    if courant is None:
        return None
    o = io.StringIO()
    cmd_cocher(argparse.Namespace(fichier=os.path.join(racine, courant), fiche=fiche, verifier=True), o)
    s = o.getvalue()
    if "TÊTE " in s:
        return ("Le dernier commit du dépôt nomme %s : tu as commité, contre agents/fiche.md. N'y touche "
                "pas ; rends RETOUR en le disant, le chef décidera." % fiche)
    if "CASE %s [ ]" % fiche in s:
        return ("FAITE, mais la case de %s est vide : coche-la par vlp.py cocher, puis rends FAITE." % fiche)
    return None


def cmd_gardien(entree, sortie):
    """Le contrat d'`agents/fiche.md` tenu à la sortie du sous-agent (chantier CON), le refus
    de l'écriture Git étendu à `vlp:relecture` (chantier RLG), et le filtrage de la forme (résumé
    et jauge) pour les deux agents — renvoi si une ligne du dernier message s'ouvre par « En
    résumé » ou un mot de JAUGE, selon `forme_texte` et sa règle par défaut (chantiers FOR, JUG). Muet hors de ces deux agents et sur une entrée illisible : il ne
    bloque jamais sur ce qu'il ne lit pas."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    if not isinstance(d, dict):
        return 0
    agent_type = d.get("agent_type")
    if not isinstance(agent_type, str):
        return 0
    relecteur = "relecture" in agent_type
    if "fiche" not in agent_type and not relecteur:
        return 0
    ev = d.get("hook_event_name")
    if ev == "PreToolUse" and d.get("tool_name") in ("Bash", "PowerShell"):
        outil = d.get("tool_input")
        commande = outil.get("command") if isinstance(outil, dict) else None
        if isinstance(commande, str) and ecrit_git(commande):
            agent, fin = ("relecture", "ton verdict") if relecteur else ("fiche", "ton statut")
            sortie.write(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason": ("Un sous-agent vlp:%s n'écrit pas dans Git (agents/%s.md) : %s %s."
                                            % (agent, agent, REFUS_GIT, fin))}},
                ensure_ascii=False) + "\n")
    elif ev == "SubagentStop":
        dernier_msg = d.get("last_assistant_message", "")
        resume, jauge = forme_texte(dernier_msg)
        stop_hook_active = bool(d.get("stop_hook_active"))

        # Pour vlp:fiche : d'abord verdict_fin (statut, case, commit), puis forme si aucune raison et pas déjà renvoyé
        if not relecteur:
            try:
                raison = verdict_fin(d, deja_renvoye=stop_hook_active)
            except (Absent, OSError, ValueError):
                raison = None
            if raison:
                sortie.write(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=False) + "\n")
            elif (resume or jauge) and not stop_hook_active:
                raison = "Ton dernier message porte un « En résumé » ou une jauge : ton lecteur est le chef (agents/fiche.md). Réécris-le sans eux, statut en tête."
                sortie.write(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=False) + "\n")
        # Pour vlp:relecture : seulement forme
        else:
            if (resume or jauge) and not stop_hook_active:
                raison = "Ton dernier message porte un « En résumé » ou une jauge : ton lecteur est le chef (agents/relecture.md). Réécris-le sans eux, statut en tête."
                sortie.write(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=False) + "\n")
    return 0


# --- page --------------------------------------------------------------------

# Le seuil vit dans le script (SEUIL_PAGE) : ici, il est défini et cité.
SEUIL_PAGE = 250
GABARIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "artefact-chantier.html")
JOINTS = ("vlp.css", "vlp.js")


def recopier_joints(dossier):
    """Copie les joints du kit (`JOINTS`, sources dans `templates/`) dans `dossier`, à chaque
    appel de `page` et `feuille` — la source ne bouge qu'au commit, la copie peut avoir été
    modifiée à la main entre deux appels (chantiers PLI, BTN). Rend `{nom publié: chemin de
    la copie}`, le paramètre `files` d'`Artifact` (`ligne_files`)."""
    copies = {}
    for nom in JOINTS:
        dest = os.path.join(dossier, nom)
        with open(os.path.join(os.path.dirname(GABARIT), nom), "rb") as f:
            contenu = f.read()
        with open(dest, "wb") as f:
            f.write(contenu)
        copies[nom] = dest
    return copies


PUBLIE = "publie"   # à côté des pages : page, nom publié, sha256 — ce que la dernière publication a joint


def empreinte(chemin):
    with open(chemin, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def notes_publie(lignes):
    """{(page, nom publié): sha256} des lignes d'un fichier `publie` ; une ligne qui n'a pas ses trois cellules est sautée."""
    notes = {}
    for l in lignes:
        c = l.split("\t")
        if len(c) == 3:
            notes[(c[0], c[1])] = c[2]
    return notes


def texte_publie(notes):
    """Le fichier `publie` de `notes` : une ligne par clé, triées — le texte que `noter_publie` écrit (chantier NUI)."""
    return "".join("%s\t%s\t%s\n" % (p, n, h) for (p, n), h in sorted(notes.items()))


def lire_publie(dossier):
    """{(page, nom publié): sha256} du fichier `publie` de `dossier` ; absent : {}."""
    chemin = os.path.join(dossier, PUBLIE)
    return notes_publie(lignes_de(chemin)) if os.path.isfile(chemin) else {}


def noter_publie(dossier, page, empreintes):
    """Remplace les empreintes de `page` pour les seuls noms donnés : un joint non repassé
    garde la sienne, il est toujours en ligne (chantier JNT). `.tmp` puis `os.replace`."""
    notes = lire_publie(dossier)
    notes.update({(page, nom): h for nom, h in empreintes.items()})
    chemin = os.path.join(dossier, PUBLIE)
    with open(chemin + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(texte_publie(notes))
    os.replace(chemin + ".tmp", chemin)


def ligne_files(copies, page=None):
    """`FILES {…}` : le JSON de `recopier_joints`, chemins en barres obliques — à passer
    tel quel au paramètre `files` d'`Artifact` (chantier BTN). Avec `page`, seuls les joints
    dont l'empreinte diffère de celle notée à sa dernière publication (`publie`, écrit par
    `attente hook`) ; page jamais notée : tous ; rien de changé : `FILES {}` (chantier JNT)."""
    if page:
        dossier, nom_page = os.path.split(os.path.abspath(page))
        notes = lire_publie(dossier)
        copies = {nom: c for nom, c in copies.items() if notes.get((nom_page, nom)) != empreinte(c)}
    return "FILES %s\n" % json.dumps({nom: chemin.replace("\\", "/") for nom, chemin in copies.items()},
                                     ensure_ascii=False)


def cmd_joints(dossier, sortie):
    """Pour `/vlp:init`, qui remplit sa feuille sans `feuille` : la ligne `FILES` seule."""
    if not os.path.isdir(dossier):
        sortie.write("GARDE: dossier introuvable : %s\n" % dossier)
        return 1
    sortie.write(ligne_files(recopier_joints(os.path.abspath(dossier))))
    return 0


# Une fiche de la page, dans ses deux formes : spans à plat (avant PLI), ou repliée dans un
# `<details>` (depuis PLI) — les pages des projets équipés gardent l'ancienne jusqu'à leur
# prochaine régénération.
LI_FICHE =re.compile(r'[ \t]*<li class="fiche"[^>]*>.*?</li>\n?', re.S)
UL_FICHES = re.compile(r'(<ul class="fiches">)(.*?)(\n[ \t]*</ul>)', re.S)
# Relit tout ce que `ligne_cout` écrit : le total entre parenthèses, ou nu sous
# 1 000 (`arrondi`), négatif compris ; le prix, négatif compris, ou `?` quand il
# manque. Un négatif, `couts` l'écrit sans Git quand l'ancienne page affiche plus
# que la session mesurée : il se relit avec son signe (chantier TAR).
COUT = re.compile(r"(?:\((\d[\d ]*)\)|(-?\d+)) · (\d+) tours · (-?[\d,]+|\?) \$")
_mesure = None


def mesure():
    """`mesure-tokens.py`, importé une fois (le tiret interdit `import`)."""
    global _mesure
    if _mesure is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mesure_tokens", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesure-tokens.py"))
        assert spec and spec.loader
        _mesure = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mesure)
    return _mesure


def esc(texte):
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def milliers(n):
    return "{:,}".format(n).replace(",", " ")


def arrondi(n):
    """La convention de coût en tête de templates/artefact-chantier.html."""
    if n < 1000:
        return str(n)
    # Dès 999 950, les milliers s'arrondiraient à « 1000,0k » : c'est déjà le million.
    valeur, unite = (n / 1_000_000, "M") if n >= 999_950 else (n / 1000, "k")
    return "≈%s%s (%s)" % (("%.1f" % valeur).replace(".", ","), unite, milliers(n))


def dollars(usd):
    """Un prix mesuré comme `47,08 $`, `? $` s'il est inconnu — celui des pages et de `clore` (chantier TAU)."""
    return "%s $" % ("?" if usd is None else ("%.2f" % usd).replace(".", ","))


def approx(usd):
    """Un prix approché comme `≈230 $` ou `≈9,00 $` — l'estimé d'`ouvrir`, au prix mesuré des clos
    (chantier TAU ; remplace l'ancienne louche à tant par million de tokens)."""
    v = float(usd)
    return "≈%s $" % (("%.2f" % v).replace(".", ",") if v < 10 else "%d" % round(v))


def ligne_cout(total, tours, usd):
    return "%s · %d tours · %s" % (arrondi(total), tours, dollars(usd))


def fiches_du_fichier(lignes):
    """[(id, titre, coché, sessions)] dans l'ordre du fichier."""
    titres = [(i, l) for i, l in enumerate(lignes) if TITRE.match(l)]
    rendu = []
    for n, (i, l) in enumerate(titres):
        suivant = titres[n + 1][0] if n + 1 < len(titres) else len(lignes)
        ident = l.split()[1]
        titre = l.split(" — ", 1)[1] if " — " in l else l
        rendu.append((ident, titre.replace("`", "").strip(), "[x]" in l, sessions_de(lignes[i:suivant])))
    return rendu


DEPEND = re.compile(r"\b[A-Z]{1,3}[0-9]+\b")
VISUEL = '<span class="badge visuel" title="Critère de fin visuel : il faudra regarder">visuel</span>'


def apercu_fiches(lignes):
    """{id: (dépendances, critère visuel, fichiers)} lus dans le bloc de chaque fiche : les
    identifiants de sa ligne `**Dépend de**` et de ses suites, vrai si son `**Critère de fin**`
    porte `(visuel)` — la colonne de gauche et celle de droite de sa carte sur la page (gabarit en
    colonnes) —, et le nom seul de chaque fichier de sa ligne `**Fichiers**` : `vlp.css` pour
    `templates/vlp.css`, pour qu'un même fichier nommé de deux façons compte comme commun."""
    titres = [i for i, l in enumerate(lignes) if TITRE.match(l)] + [len(lignes)]
    rendu = {}
    for i, suivant in zip(titres, titres[1:]):
        deps, visuel, dedans = [], False, False
        for l in lignes[i + 1:suivant]:
            if l.startswith("<!-- /FICHE"):
                break
            if l.startswith("**Dépend de**"):
                dedans = True
            elif dedans and (not l.strip() or l.startswith("**")):
                dedans = False
            if dedans:
                deps += [d for d in DEPEND.findall(l) if d not in deps]
            visuel = visuel or bool(CRITERE_VISUEL.match(l))
        # Un fichier : un chemin, ou un nom à extension — pas `compte_todo`, `:3124` ni « rien ».
        fichiers = {n.rstrip("/").rsplit("/", 1)[-1] for n in noms_fichiers(lignes[i + 1:suivant])
                    if "/" in n or re.fullmatch(r"[\w-]+(?:\.[\w-]+)+", n)}
        rendu[lignes[i].split()[1]] = (deps, visuel, fichiers)
    return rendu


def pretes(fiches_, etat, apercu):
    """({id: ce qu'elle attend}, [en même temps]) pour les fiches non faites. Une fiche attend ses
    dépendances de ce fichier pas encore faites ; sans rien à attendre, elle est prête. En même
    temps : les prêtes prises dans l'ordre, chacune seulement si elle n'a aucun fichier en commun
    avec celles déjà prises — une prête sans ligne `**Fichiers**` n'en est pas : on ne sait pas ce
    qu'elle touche. Moins de deux : aucune. Les fichiers sont ceux que la fiche annonce, pas ceux
    qu'elle touchera — le repère prévient, il ne garantit rien (chantier BTN)."""
    attend = {i: [d for d in apercu.get(i, ([],))[0] if etat.get(d, "faite") != "faite"]
              for i, _, _, _ in fiches_ if etat[i] != "faite"}
    ensemble, pris = [], set()
    for i, _, _, _ in fiches_:
        touche = apercu.get(i, ([], False, set()))[2]
        if i in attend and not attend[i] and touche and not touche & pris:
            ensemble.append(i)
            pris |= touche
    return attend, ensemble if len(ensemble) > 1 else []


def fleche(noms, unite):
    """Les dépendances d'une carte de la feuille, dans sa colonne de gauche : `← A, B` ; au-delà de
    deux, `← n <unite>` et la liste au survol (`title`) — la colonne est étroite ; rien sans dépendance."""
    if not noms:
        return ""
    if len(noms) <= 2:
        return '<span class="dep mono">← %s</span>' % esc(", ".join(noms))
    return '<span class="dep mono" title="%s">← %d %s</span>' % (esc(", ".join(noms)), len(noms), unite)


def libelle_calcule(texte):
    """Vrai si `regenerer` a écrit ce libellé d'état, qui se recalcule ; faux pour un libellé écrit à la
    main (« abandonnée »), que `--forme` garde. Toutes ses formes : « à faire » d'avant BTN, « à lancer »
    et « après A » en minuscules, puis la phrase « À lancer · en même temps que B »."""
    tete = texte.split(" · ")[0].strip().lower()
    return tete in ("faite", "en cours", "bloquée", "à faire", "à lancer") or tete.startswith("après ")


def lis_page(html):
    """{id: (data-etat ou None, note html ou None, cout html ou None)}."""
    vues = {}
    for li in LI_FICHE.findall(html):
        ident = re.search(r'<span class="id">(.*?)</span>', li)
        if not ident:
            continue
        etat = re.search(r'data-etat="(\w+)"', li)
        note = re.search(r'<span class="note">(.*?)</span>', li, re.S)
        cout = re.search(r'<span class="cout mono">(.*?)</span>', li, re.S)
        vues[ident.group(1)] = (etat and etat.group(1), note and note.group(1), cout and cout.group(1))
    return vues


def etats(fiches_, anciens):
    """{id: faite | encours | bloquee | None} — le fichier a raison ; seul
    `bloquee` vient de la page, et ne survit pas à la case cochée."""
    rendu, premiere = {}, True
    for ident, _, coche, _ in fiches_:
        if coche:
            rendu[ident] = "faite"
        elif premiere:
            rendu[ident] = "bloquee" if anciens.get(ident, (None,))[0] == "bloquee" else "encours"
            premiere = False
        else:
            rendu[ident] = None
    return rendu


def triplet(texte):
    """(total, tours, usd) lus sur une ligne de coût affichée, ou None ; usd
    vaut None sur `? $`."""
    c = texte and COUT.search(texte)
    if not c:
        return None
    from decimal import Decimal
    usd = None if c.group(4) == "?" else Decimal(c.group(4).replace(",", "."))
    return int((c.group(1) or c.group(2)).replace(" ", "")), int(c.group(3)), usd


def moins(a, b):
    """a − b, ou None si l'un manque : un prix inconnu le reste."""
    return None if a is None or b is None else a - b


GIT = "git"     # test-vlp.py le remplace pour simuler un poste sans Git
COMMIT_FICHE = re.compile(r"^([A-Z]{1,3}[0-9]+) :")
INFINI = float("inf")


def heures_commits(fichier, ids, pourquoi=None, clos=False, titres=None):
    """({id: heure}, [heures], [autres heures], [coupes]) en secondes UTC, lus par `git log` dans
    le dossier du fichier : l'heure d'auteur du commit `<id> :` de chaque fiche — s'il y en a deux,
    le plus ancien de ceux dont le sujet suit par le titre de la fiche (`titres`, {id: titre} ;
    le commit de 6 bis et de `boucle.py`), à défaut le plus ancien : un commit d'étape en cours de
    fiche ne la coupe plus avant sa fin, un correctif d'après ne l'étire pas (chantier PRP, `NUI20`) —,
    celles de tous les commits qui nomment le préfixe (`REP`, `REP2`…),
    celles des autres commits, puis, à part, celles des seuls commits `<PRÉFIXE> :` (`VIT :`,
    `Dette VIT :`, pas `Chantier VIT ouvert`), triées : elles bornent le chantier (`plages`).
    Sans commit de fiche, `{}` d'abord : un chantier en cours. None sans `git`, sans dépôt,
    sans commit qui nomme le préfixe, ou sans commit de fiche d'un chantier `clos` — sa
    dernière mention est sa clôture, rien ne tomberait après (chantier ZER) : le repli,
    jamais un traceback — et sa raison, ajoutée à la liste `pourquoi` si on en donne une."""
    import subprocess
    pourquoi = [] if pourquoi is None else pourquoi
    if not ids:
        pourquoi.append("aucune fiche au fichier")
        return None
    try:
        r = subprocess.run([GIT, "log", "--format=%at %s"], cwd=os.path.dirname(os.path.abspath(fichier)),
                           capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        pourquoi.append("git ne se lance pas : %s" % e)
        return None
    if r.returncode:
        pourquoi.append("git log en échec : %s" % ((r.stderr or "").strip().splitlines() or ["code %d" % r.returncode])[0])
        return None
    nomme = re.compile(r"(?<![A-Za-z0-9])(?:%s)[0-9]*(?![A-Za-z0-9])"
                       % "|".join(sorted({lettre_de(i) for i in ids})))
    coupe = re.compile(r"(?<![A-Za-z0-9])(?:%s) :" % "|".join(sorted({lettre_de(i) for i in ids})))
    commits, au_titre, prefixe, autres, coupes = {}, {}, [], [], []
    for ligne in r.stdout.splitlines():
        heure, _, sujet = ligne.partition(" ")
        if not heure.isdigit():
            continue
        (prefixe if nomme.search(sujet) else autres).append(int(heure))
        coupes.extend([int(heure)] if coupe.search(sujet) else [])
        c = COMMIT_FICHE.match(sujet)
        if c and c.group(1) in ids:
            titre = (titres or {}).get(c.group(1))
            vus = au_titre if titre and sujet[c.end():].replace("`", "").strip().startswith(titre) else commits
            vus[c.group(1)] = min(int(heure), vus.get(c.group(1), int(heure)))
    commits.update(au_titre)
    if not commits:
        if not prefixe:
            pourquoi.append("aucun commit qui nomme %s" % lettre_de(ids[0]))
            return None
        if clos:
            pourquoi.append("chantier clos sans commit « %s : » ni d'une autre fiche" % ids[0])
            return None
        return {}, sorted(prefixe), sorted(autres), sorted(coupes)
    return commits, sorted(prefixe), sorted(autres), sorted(coupes)


def plages(fiches_, heures, gardes, clos=False):
    """([(id, (début, fin])] dans l'ordre des commits, [plages hors fiches]). Une fiche va
    du commit de la précédente au sien ; la première part du dernier commit antérieur qui
    nomme le préfixe, à défaut de l'origine ; une fiche à session sans commit va jusqu'au
    bout du transcript — d'un chantier `clos`, jusqu'au premier commit suivant qui nomme le
    préfixe, comme la dernière plage hors fiches : la session a pu continuer après la clôture
    (LEC5, chantier ECA) —, et part de l'ouverture (le dernier commit qui nomme le préfixe)
    tant qu'aucune fiche n'a de commit — en cours : clos, `heures_commits` rend le repli. L'origine : le dernier commit qui ne nomme pas le
    préfixe, avant ce début — le chantier d'avant, quand une session en enchaîne plusieurs ;
    à défaut, le début de la session. Hors fiches : de l'origine à la première fiche, et de
    la dernière au premier commit suivant qui nomme le préfixe — la clôture ; sans lui,
    jusqu'au bout. Au-delà, rien ne compte : une mention plus tardive n'étire rien. Un commit
    `<PRÉFIXE> :` (4e liste de `heures`, absente : aucun) entre deux commits de fiche coupe la
    suivante : elle part du dernier de ces commits, le morceau d'avant va hors fiches, le total
    ne bouge pas (chantier PRP) ; une mention ailleurs dans le sujet (`Chantier VIT ouvert`) ne
    coupe rien. Ni commit de fiche ni fiche à session : ([], [])."""
    commits, prefixe, autres, *reste = heures
    coupes = reste[0] if reste else []
    ordre = sorted(commits, key=commits.get)
    premier = commits[ordre[0]] if ordre else INFINI    # sans commit de fiche : le dernier qui nomme
    debut = max((t for t in prefixe if t < premier), default=-INFINI)
    origine = max((t for t in autres if t < (premier if debut == -INFINI else debut)), default=-INFINI)
    debut = max(debut, origine)
    rendu, milieu = [], []
    for ident in ordre:
        coupe = max((t for t in coupes if debut < t < commits[ident]), default=None)
        if rendu and coupe is not None:
            milieu.append((debut, coupe))
            debut = coupe
        rendu.append((ident, (debut, commits[ident])))
        debut = commits[ident]
    sans = [f[0] for f in fiches_ if f[0] not in commits and f[3]]
    for ident in sans[:-1]:
        gardes.append("GARDE: %s porte une session sans commit « %s : » — ses tours comptent dans une autre plage"
                      % (ident, ident))
    if sans:
        rendu.append((sans[-1], (debut, min((t for t in prefixe if t > debut), default=INFINI) if clos else INFINI)))
    if not rendu:
        return [], []
    dernier = rendu[-1][1][1]
    fin = min((t for t in prefixe if t > dernier), default=INFINI)
    return rendu, [p for p in [(origine, rendu[0][1][0])] + milieu + [(dernier, fin)] if p[0] < p[1]]


def transcripts_du_fichier(fiches_, entete, gardes):
    """Rendre [(chemin, sorte)] des transcripts d'un fichier de fiches — sorte 0 : session, 1 : sous-agent, 2 : essai,
    3 : sous-agent d'un essai, rangé avec lui. Les sessions : celles des fiches, puis `entete` — le cadrage
    (`sessions_entete`) ; une session introuvable se dit en `GARDE:`."""
    m = mesure()
    sessions, fichiers = [], []
    for groupe in [f[3] for f in fiches_] + [list(entete)]:
        sessions += [s for s in groupe if s not in sessions]
    for s in sessions:
        chemin, erreur = m.resoudre(s)
        if erreur:
            gardes.append("GARDE: session non mesurée : %s — %s" % (s, erreur))
            continue
        fichiers += [(chemin, 0)] + [(a, 1) for a in m.sous_agents(chemin)]
        for e in essais_de(s):
            fichiers += [(e, 2)] + [(a, 3) for a in m.sous_agents(e)]
    return fichiers


def plages_du_cout(fiches_, heures, gardes, fin=None):
    """Rendre (plages des fiches, plages hors fiches) de `plages`, la dernière hors fiches arrêtée à `fin` s'il est
    donné : le chantier est alors clos (`parts_aux_commits`)."""
    par_fiche, trous = plages(fiches_, heures, gardes, clos=fin is not None)
    if fin is not None and trous:
        trous = trous[:-1] + [(trous[-1][0], min(trous[-1][1], fin))]
    return par_fiche, trous


def parts_aux_commits(fiches_, heures, gardes, entete=(), fin=None):
    """([(id, session, sous-agents, essais)], (session, sous-agents, essais) hors fiches), ou None
    sans transcript mesurable, ou sans fiche à découper. Les sessions : celles des fiches, puis
    `entete` — le cadrage (`sessions_entete`). Les essais : ceux de chaque session (`essais_de`),
    leurs sous-agents compris, qui ne comptent pas dans leur n (chantier ESS). Chaque fiche qui a
    une plage la prend dans chaque transcript (la plage de `mesurer`) ; le reste fait « hors fiches ». Une part vaut
    (total, tours, usd, n) — n : les transcripts qui y ont un tour —, usd arrondi au
    centime : tout s'additionne, dans `cout` comme sur la page. Aucun tour gardé, ni aux
    fiches ni hors fiches : une `GARDE:` le dit, les nombres restent (chantier ZER). `fin` : la
    dernière plage hors fiches s'y arrête — l'heure de l'appel `clore` (chantier APC). Donné, le
    chantier est clos : sa fiche sans commit s'arrête au commit suivant (`plages`, chantier ECA)."""
    from decimal import ROUND_HALF_UP, Decimal
    m = mesure()
    fichiers = transcripts_du_fichier(fiches_, entete, gardes)
    if not fichiers:
        return None
    par_fiche, trous = plages_du_cout(fiches_, heures, gardes, fin)
    if not par_fiche:
        return None

    def part(bornes):
        rendu = [[0, 0, Decimal(0), 0], [0, 0, Decimal(0), 0], [0, 0, Decimal(0), 0]]
        for chemin, sorte in fichiers:
            p, tours = rendu[min(sorte, 2)], 0
            for plage in bornes:
                r, erreur = m.mesurer(chemin, plage)
                if erreur:
                    g = "GARDE: transcript non mesuré : %s — %s" % (chemin, erreur)
                    gardes.extend([] if g in gardes else [g])
                    continue
                p[0], p[1], tours = p[0] + r["total"], p[1] + r["tours"], tours + r["tours"]
                p[2] = None if p[2] is None or r["usd_exact"] is None else p[2] + r["usd_exact"]
            p[3] += 1 if tours and sorte != 3 else 0
        return tuple((t, n, None if u is None else u.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), k)
                     for t, n, u, k in rendu)

    parts, hors = [(ident,) + part([p]) for ident, p in par_fiche], part(trous)
    if not plus(*[q for _, *r in parts for q in r], *hors)[1]:
        gardes.append("GARDE: découpe à zéro — aucun tour de %d transcript%s ne tombe dans une plage"
                      % (len(fichiers), "s" if len(fichiers) > 1 else ""))
    return parts, hors


def essais_entiers(sessions, gardes):
    """La part essais de sessions entières, sans plage : chaque essai (`essais_de`) mesuré en
    entier, ses sous-agents compris, comme `parts_aux_commits` le fait sur une plage. Une part
    (total, tours, usd, n) — n : les essais qui ont un tour —, usd arrondi au centime ; pour
    `cout` sans découpe (chantier ESD)."""
    from decimal import ROUND_HALF_UP, Decimal
    m = mesure()
    p = [0, 0, Decimal(0), 0]
    for s in sessions:
        for e in essais_de(s):
            tours = 0
            for chemin in [e] + m.sous_agents(e):
                r, erreur = m.mesurer(chemin)
                if erreur:
                    gardes.append("GARDE: transcript non mesuré : %s — %s" % (chemin, erreur))
                    continue
                p[0], p[1] = p[0] + r["total"], p[1] + r["tours"]
                tours += r["tours"] if chemin == e else 0
                p[2] = None if p[2] is None or r["usd_exact"] is None else p[2] + r["usd_exact"]
            p[3] += 1 if tours else 0
    return p[0], p[1], None if p[2] is None else p[2].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), p[3]


def plus(*parts):
    """La somme de parts (total, tours, usd, n) ; usd None dès qu'un prix manque."""
    usd = None if any(p[2] is None for p in parts) else sum(p[2] for p in parts)
    return sum(p[0] for p in parts), sum(p[1] for p in parts), usd, sum(p[3] for p in parts)


def ligne_parts(nom, session, agents, essais=(0, 0, 0, 0)):
    """`<nom> · <somme> = session <…> + <n> sous-agents <…>`, puis `+ <n> essais <…>` s'il y en a
    un tour : une ligne de `cout` qui nomme ce qu'elle compte. La somme d'abord : c'est le
    nombre de la page, et `triplet` la relit."""
    n, k = agents[3], essais[3]
    return "%s · %s = session %s + %s%s" % (
        nom, ligne_cout(*plus(session, agents, essais)[:3]), ligne_cout(*session[:3]),
        "%d sous-agent%s %s" % (n, "s" if n > 1 else "", ligne_cout(*agents[:3])) if n else "0 sous-agent",
        " + %d essai%s %s" % (k, "s" if k > 1 else "", ligne_cout(*essais[:3])) if essais[1] else "")


def couts_aux_commits(fiches_, heures, gardes, entete=(), fin=None):
    """`couts` coupé aux commits (`parts_aux_commits`) : une ligne par fiche, session et
    sous-agents sommés ; « hors fiches » à part, et total = fiches + hors fiches."""
    decoupe = parts_aux_commits(fiches_, heures, gardes, entete, fin)
    if decoupe is None:
        return {}, None, None
    parts, hors = decoupe
    sommes = {ident: plus(*r) for ident, *r in parts}
    hors = plus(*hors)
    return ({ident: ligne_cout(*v[:3]) for ident, v in sommes.items()},
            plus(*sommes.values(), hors)[:3], hors[:3])


def couts(fiches_, anciens, ancien_total, gardes, heures=None, entete=(), fin=None):
    """({id: ligne de coût}, total, hors fiches) — total et hors fiches en (total, tours,
    usd), ou None. Avec les heures des commits (`heures_commits`) : `couts_aux_commits`.
    Sans elles, tirés de l'ancienne page, sans hors fiches. Une session portée
    par plusieurs fiches : les premières gardent le coût déjà affiché (l'écart
    du compteur à leur clôture), la dernière prend le reste — moins la part que
    l'ancienne page n'attribuait à aucune fiche (le cadrage joué dans la même
    session), si une seule session est partagée."""
    if heures:
        return couts_aux_commits(fiches_, heures, gardes, entete, fin)
    m = mesure()
    mesures = {}
    for _, _, _, sessions in fiches_:
        for s in sessions:
            if s in mesures:
                continue
            chemin, erreur = m.resoudre(s)
            r = None
            if not erreur:
                r, erreur = m.mesurer(chemin)
            if erreur:
                gardes.append("GARDE: session non mesurée : %s — %s" % (s, erreur))
            mesures[s] = r
    # La part non attribuée de l'ancienne page : son total moins ses coûts affichés.
    base = triplet(ancien_total)
    for ident in anciens:
        c = triplet(anciens[ident][2])
        if base and c:
            base = (base[0] - c[0], base[1] - c[1], moins(base[2], c[2]))
    partagees = [s for s in mesures if mesures[s] and sum(1 for f in fiches_ if s in f[3]) > 1]
    if not base or len(partagees) != 1 or base[0] < 0 or base[1] < 0:
        base = (0, 0, 0)
    rendu = {}
    for s, r in mesures.items():
        if r is None:
            continue
        porteurs = [f[0] for f in fiches_ if s in f[3]]
        total, tours, usd = r["total"], r["tours"], r["usd_exact"]
        if len(porteurs) > 1:
            total, tours = total - base[0], tours - base[1]
            usd = moins(usd, base[2])
        for ident in porteurs[:-1]:
            ancien = anciens.get(ident, (None, None, None))[2]
            c = triplet(ancien)
            if not c:
                gardes.append("GARDE: %s partage la session %s sans coût affiché — tout le coût va sur %s"
                              % (ident, s, porteurs[-1]))
                continue
            rendu[ident] = ancien
            total, tours = total - c[0], tours - c[1]
            usd = moins(usd, c[2])
        rendu[porteurs[-1]] = ligne_cout(total, tours, usd)
    mesurees = [r for r in mesures.values() if r]
    if not mesurees:
        return rendu, None, None
    usd = None if any(r["usd_exact"] is None for r in mesurees) else sum(r["usd_exact"] for r in mesurees)
    return rendu, (sum(r["total"] for r in mesurees), sum(r["tours"] for r in mesurees), usd), None


def comptage(fiches_, etat):
    faites = sum(1 for e in etat.values() if e == "faite")
    texte = "%d fiches · %d %s" % (len(fiches_), faites, "faite" if faites <= 1 else "faites")
    courante = next((i for i, e in etat.items() if e in ("encours", "bloquee")), None)
    if courante:
        texte += " · %s : %s" % ("bloquée" if etat[courante] == "bloquee" else "en cours", courante)
    return texte


def nom_du_projet(projet):
    """`--projet` est un nom ; un dossier (`.`) donne l'alias de son `CHANTIER.md`, sinon son nom (dette CLI)."""
    if not os.path.isdir(projet):
        return projet
    chantier = os.path.join(projet, "CHANTIER.md")
    alias = [m.group(1) for m in map(ALIAS.match, lignes_de(chantier) if os.path.isfile(chantier) else []) if m]
    return alias[0] if alias else os.path.basename(os.path.abspath(projet))


def creer(fichier, projet, titre, resultat):
    projet = nom_du_projet(projet)
    html = lire(GABARIT)
    fiches_ = fiches_du_fichier(lignes_de(fichier))
    remplacements = [
        (r"<title>.*?</title>", "<title>%s — %s</title>" % (esc(projet), esc(titre))),
        (r'(<div class="eyebrow">).*?(</div>)', r"\g<1>%s · fiches \g<2>" % esc(projet)),
        (r"<h1>.*?</h1>", "<h1>%s</h1>" % esc(titre)),
        (r"(</h1>\s*<p>).*?(</p>)", r"\g<1>%s\g<2>" % esc(resultat).replace("\\", "\\\\")),
        (r'(<ul class="journal">).*?(\n[ \t]*</ul>)', r"\g<1>\g<2>"),
        (r'(<div class="blocage">\s*<p>).*?(</p>\s*<pre>).*?(</pre>)', r"\g<1>\g<2>\g<3>"),
        (r"(<h2>Chantier clos le ).*?(</h2>\s*<div class=\"bilan\">).*?(\n[ \t]*</div>)", r"\g<1>\g<2>\n      <p></p>\g<3>"),
        (r'(Fichier de fiches : <span class="mono">).*?(</span>)', r"\g<1>%s\g<2>" % esc(fichier.replace("\\", "/"))),
    ]
    for motif, rempl in remplacements:
        html, n = re.subn(motif, rempl, html, count=1, flags=re.S)
        if not n:
            raise ValueError("gabarit : motif introuvable : %s" % motif)
    return html


STYLE_INLINE = re.compile(r"<style>.*?</style>\n?", re.S)


def migrer_style(html):
    """Une page qui porte encore son `<style>` inline (d'avant `vlp.css`, chantier PLI) le
    remplace par le `<link>` — une fois, jamais deux. Rend le HTML, le même s'il n'y a rien
    à migrer (déjà lié, ou pas de `<style>` du tout)."""
    a_style = STYLE_INLINE.search(html)
    a_lien = 'href="vlp.css"' in html
    if a_style and not a_lien:
        return STYLE_INLINE.sub('<link rel="stylesheet" href="vlp.css">\n', html, count=1)
    if a_style and a_lien:
        return STYLE_INLINE.sub("", html, count=1)
    return html


META_CHARSET = '<meta charset="utf-8">'
SCRIPT_VLPJS = '<script src="vlp.js"></script>'


def migrer_joints(html):
    """Une page d'avant BTN1 reçoit `META_CHARSET` en première ligne et `SCRIPT_VLPJS` en
    dernière — une fois, jamais deux : cherchés hors commentaires, déjà là, rien ne bouge."""
    hors = COMMENTAIRE.sub("", html)
    if META_CHARSET not in hors:
        html = META_CHARSET + "\n" + html
    if SCRIPT_VLPJS not in hors:
        html = html.rstrip("\n") + "\n" + SCRIPT_VLPJS + "\n"
    return html


JOURNAL_VISIBLE = 3
JOURNAL_ANCIEN = re.compile(r'\n[ \t]*<details class="journal-ancien">.*?</details>', re.S)


def bilan_en_haut(html):
    """La section de `ZONE:bilan`, marqueur compris, déplacée juste sous l'en-tête — une page
    close se lit par son bilan (chantier PLI). Rend le HTML, le même si elle y est déjà."""
    i = html.find("<!-- ZONE:bilan")
    tete = html.find("  </header>\n")
    if i < 0 or tete < 0 or i < tete:
        return html
    debut = html.rfind("\n", 0, i) + 1
    fin = html.find("  </section>\n", i)
    if fin < 0:
        return html
    fin += len("  </section>\n")
    bloc = html[debut:fin]
    reste = html[:debut].rstrip("\n") + "\n\n" + html[fin:].lstrip("\n")
    apres = reste.find("  </header>\n") + len("  </header>\n")
    return reste[:apres] + "\n" + bloc + reste[apres:]


def regenerer(html, fichier, parts, date, gardes, forme=False):
    """`parts` (`lire_abri`/`abri_de_page`) fait foi pour résultat, notes et journal — recopiés
    en entier dans la page, plus jamais lus dans son ancienne version (chantier ABR). `forme` :
    rien ne se recompte — coûts des fiches, total et hors fiches recopiés de l'ancienne page (HAB)."""
    html = migrer_joints(migrer_style(html))
    lignes = lignes_de(fichier)
    fiches_ = fiches_du_fichier(lignes)
    if not fiches_:
        raise ValueError("aucun titre de fiche au format '## X1' dans %s" % fichier)
    anciens = lis_page(html)
    etat = etats(fiches_, anciens)
    ancien_total = re.search(r'<p class="mono cout-total">(.*?)</p>', html, re.S)
    vieux = {k: m.group(1) for k in ("hors", "total")
             for m in [re.search(r'<p class="mono cout-%s">(.*?)</p>' % k, html, re.S)] if m}
    # `forme` garde aussi ce que l'ancienne page disait de chaque fiche — titre, état et son
    # libellé écrits à la main (« abandonnée ») : mesuré sur le kit le 2026-09-27, 4 pages sur 64
    # perdaient sinon une ligne de texte (chantier HAB).
    libelles = {}
    if forme:
        for li in LI_FICHE.findall(html):
            ident = re.search(r'<span class="id">(.*?)</span>', li)
            titre_ = re.search(r'<span class="titre">(.*?)</span>', li, re.S)
            libelle = re.search(r'<span class="etat">(.*?)</span>', li, re.S)
            if ident and titre_ and libelle:
                libelles[ident.group(1)] = (titre_.group(1), libelle.group(1))
        etat = {i: anciens[i][0] if i in libelles else e for i, e in etat.items()}
    if forme:
        cout = {i: v[2] for i, v in anciens.items() if v[2] is not None}
        total = triplet(ancien_total.group(1)) if ancien_total else None
        hors = triplet(vieux.get("hors"))
    else:
        clos = any(l.startswith("**CLOS**") for l in lignes)
        heures = heures_commits(fichier, [f[0] for f in fiches_], clos=clos) if any(f[3] for f in fiches_) else None
        # Un clos s'arrête à son appel clore, comme cout : un chantier, un seul chiffre (dette PLI).
        fin = heure_clore(fichier, lignes) if clos and heures else None
        cout, total, hors = couts(fiches_, anciens, ancien_total and ancien_total.group(1), gardes, heures,
                                  sessions_entete(lignes), fin)
    html, n = re.subn(r'(</h1>\s*<p>).*?(</p>)', lambda m: m.group(1) + esc(parts["resultat"]) + m.group(2),
                      html, count=1, flags=re.S)
    if not n:
        raise ValueError("page : résultat introuvable")
    etiquette = {"faite": "Faite", "encours": "En cours", "bloquee": "Bloquée"}
    apercu = apercu_fiches(lignes)
    attend, ensemble = pretes(fiches_, etat, apercu)
    items = []
    for ident, titre, _, _ in fiches_:
        e = etat[ident]
        note = esc(parts["notes"][ident]) if ident in parts["notes"] else None
        visuel = apercu.get(ident, ([], False, set()))[1]
        # L'état en une phrase, sous le titre (commentaires de la page BTN, choix de l'utilisateur) :
        # « À lancer », ou « Après A, B » — ce qu'elle attend encore de ce fichier, `data-attend`,
        # pas de Copier (`vlp.js`) ; en cours ou bloquée, son état, puis « attend A » s'il en reste.
        # « en même temps que B » : prêtes sans fichier commun (`pretes`). Une dépendance faite ne
        # s'affiche plus : « À lancer » le dit déjà.
        reste = ", ".join(attend.get(ident, []))
        if e is None:
            libelle = "Après " + reste if reste else "À lancer"
        else:
            libelle = etiquette[e] + (" · attend " + reste if reste else "")
        autres = [i for i in ensemble if i != ident]
        if ident in ensemble:
            libelle += (" · en même temps que " + ", ".join(autres) if e is None else " · %s %s partir en même temps"
                        % (", ".join(autres), "peut" if len(autres) == 1 else "peuvent"))
        # `forme` garde un libellé écrit à la main (« abandonnée ») ; celui que ce script écrit se
        # recalcule — sinon « Après A » resterait une fois A faite.
        if ident in libelles and not libelle_calcule(libelles[ident][1]):
            libelle = libelles[ident][1]
        # Trois colonnes (gabarit en colonnes, 2026-09-27) : à gauche l'identifiant, où `vlp.js` pose
        # Copier ; au milieu le titre, qui seul replie la note — repliée sauf en cours ou bloquée
        # (PLI) —, et l'état dessous ; à droite le coût, ou « visuel » tant qu'une fiche à regarder
        # n'est pas faite. `data-etat` reste sur le `<li>`, que `LI_FICHE` et `lis_page` lisent dans
        # toutes les formes ; un `span` à gauche, pas un `div` : `comparer` coupe au `div`, la fiche
        # reste un seul bloc de texte.
        droite = ('<span class="cout mono">%s</span>' % cout[ident] if ident in cout
                  else VISUEL if visuel and e != "faite" else "")
        items.append('      <li class="fiche"%s><span class="gauche"><span class="id">%s</span></span>\n'
                     '        <details%s><summary><span class="titre">%s</span><span class="etat">%s</span></summary>'
                     '%s</details>%s</li>'
                     % ((' data-etat="%s"' % e if e else "") + (" data-attend" if attend.get(ident) else ""), ident,
                        " open" if e in ("encours", "bloquee") else "",
                        libelles[ident][0] if ident in libelles else esc(titre), libelle,
                        '\n        <span class="note">%s</span>' % note if note else "",
                        "\n        " + droite if droite else ""))
    prefixe = re.search(r'<p class="mono cout-total">(.*?) : ', html)
    prefixe = prefixe.group(1) if prefixe else "Coût du chantier"
    html = re.sub(r'\n[ \t]*<p class="mono cout-(?:total|hors)">.*?</p>', "", html, flags=re.S)
    bloc = "\n" + "\n".join(items)
    bloc_total = ""
    if forme:
        bloc_total = "".join('\n    <p class="mono cout-%s">%s</p>' % (k, vieux[k]) for k in ("hors", "total") if k in vieux)
    else:
        if hors:
            bloc_total += '\n    <p class="mono cout-hors">Hors fiches : %s</p>' % ligne_cout(*hors)
        if total:
            bloc_total += '\n    <p class="mono cout-total">%s : %s</p>' % (prefixe, ligne_cout(*total))
    html, n = UL_FICHES.subn(lambda m: m.group(1) + bloc + m.group(3) + bloc_total, html, count=1)
    if not n:
        raise ValueError("page : liste des fiches introuvable")
    spans = "".join('<span%s></span>' % (' data-etat="%s"' % etat[f[0]] if etat[f[0]] else "") for f in fiches_)
    html, n = re.subn(r'(<div class="avancement">\s*).*?(\s*</div>)', lambda m: m.group(1) + spans + m.group(2), html, count=1, flags=re.S)
    html, n2 = re.subn(r'(<p class="mono" style="margin-top:.5rem">).*?(</p>)',
                       lambda m: m.group(0) if forme else m.group(1) + comptage(fiches_, etat) + m.group(2),
                       html, count=1, flags=re.S)
    if not (n and n2):
        raise ValueError("page : avancement ou ligne de comptage introuvable")
    blocage = re.search(r'<section( hidden)?>(\s*<h2>Arrêt sur blocage</h2>\s*<div class="blocage">\s*<p>)(.*?)</p>', html, re.S)
    if blocage and not blocage.group(1):
        fiche_bloquee = re.match(r"\s*([A-Z]{1,3}[0-9]+)", blocage.group(3))
        if fiche_bloquee and etat.get(fiche_bloquee.group(1)) == "faite":
            html = html[:blocage.start()] + "<section hidden>" + html[blocage.start() + len("<section>"):]
    # Les `JOURNAL_VISIBLE` dernières entrées restent visibles ; les plus anciennes, repliées à la
    # suite (chantier PLI) — `abri_de_page` relit les deux, dans l'ordre.
    def lis_journal(entrees):
        return "".join('\n      <li><time datetime="%s">%s</time><span>%s</span></li>' % (d, d, esc(t))
                       for d, t in entrees)
    entrees = parts["journal"]
    anciennes, visibles = entrees[:-JOURNAL_VISIBLE], entrees[-JOURNAL_VISIBLE:]
    html = JOURNAL_ANCIEN.sub("", html)
    replie = ('\n    <details class="journal-ancien"><summary>%d entrée%s plus ancienne%s</summary>'
              '\n    <ul class="journal">%s\n    </ul>\n    </details>'
              % (len(anciennes), "s" if len(anciennes) > 1 else "", "s" if len(anciennes) > 1 else "",
                 lis_journal(anciennes))) if anciennes else ""
    html, n = re.subn(r'(<ul class="journal">).*?(\n[ \t]*</ul>)',
                      lambda m: m.group(1) + lis_journal(visibles) + m.group(2) + replie,
                      html, count=1, flags=re.S)
    if not n:
        raise ValueError("page : journal introuvable")
    # La plage de l'en-tête, vide à la création (`creer`), suit le fichier ; ce qui la suit
    # (« · clos », écrit à la main) reste (chantier PLA). Tout autre en-tête reste tel quel (REV6).
    html = re.sub(r'(<div class="eyebrow">[^<]*? · fiches )(?:[A-Z]{1,3}\d+(?:–[A-Z]{1,3}\d+)?)?(?=</div>| · )',
                  lambda m: m.group(1) + plage([f[0] for f in fiches_]), html, count=1)
    # Le lien vers la feuille de route, en fin d'en-tête : `**artefact feuille de route**` du
    # CHANTIER.md du projet, retrouvé en remontant depuis le fichier de fiches (chantier FEU).
    # Un seul lien : celui d'avant se retire toujours, avant qu'un nouveau (ou aucun) ne s'ajoute.
    racine = trouver(os.path.dirname(fichier))
    carte_racine = lignes_de(os.path.join(racine, "CHANTIER.md")) if racine else []
    url_route = champ(carte_racine, "artefact feuille de route", "aucun")
    def maj_eyebrow(m):
        reste = re.sub(r' · <a href="[^"]*">la feuille de route</a>$', "", m.group(1))
        if not url_route.lower().startswith("aucun"):
            reste += ' · <a href="%s">la feuille de route</a>' % esc(url_route)
        return '<div class="eyebrow">' + reste + '</div>'
    html = re.sub(r'<div class="eyebrow">(.*?)</div>', maj_eyebrow, html, count=1, flags=re.S)
    if not forme:
        html = re.sub(r'(Mis à jour le <span class="mono">).*?(</span>)', lambda m: m.group(1) + date + m.group(2),
                      html, count=1)
    return html, fiches_, etat, total, hors


def verifier_page(html, fichier, sortie):
    fiches_ = fiches_du_fichier(lignes_de(fichier))
    anciens = lis_page(html)
    etat = etats(fiches_, anciens)
    ecarts = []
    for ident, _, _, _ in fiches_:
        if ident not in anciens:
            ecarts.append("%s : absente de la page" % ident)
        elif anciens[ident][0] != etat[ident]:
            ecarts.append("%s : page %s, fichier %s" % (ident, anciens[ident][0] or "à faire", etat[ident] or "à faire"))
    for ident in anciens:
        if ident not in etat:
            ecarts.append("%s : sur la page, absente du fichier" % ident)
    avancement = re.search(r'<div class="avancement">(.*?)</div>', html, re.S)
    spans = re.findall(r'<span(?: data-etat="(\w+)")?></span>', avancement.group(1)) if avancement else []
    attendu = [etat[f[0]] or "" for f in fiches_]
    if spans != attendu:
        ecarts.append("avancement : page %s, fichier %s" % (spans, attendu))
    for e in ecarts:
        sortie.write("ÉCART: %s\n" % e)
    sortie.write("%s %d fiches · %d écarts (états et avancement seulement)\n"
                 % ("À JOUR" if not ecarts else "EN RETARD", len(fiches_), len(ecarts)))
    return 1 if ecarts else 0


# --- abri : le .md d'une page, source de ses notes et de son journal (chantier ABR) ---

ABRI_SECTIONS = ("Lien", "Résultat", "Notes", "Journal", "Bilan")


def chemin_abri(page):
    """Le `.md` d'une page : même dossier, même nom, extension `.md`."""
    return os.path.splitext(page)[0] + ".md"


def une_ligne(texte):
    return " ".join(texte.split())


def lire_abri(chemin):
    """{titre, lien, resultat, notes {id: texte}, journal [(date, texte)], bilan [texte]} ; `lien`,
    l'URL en ligne de la page (chantier HAB), vaut "" sans section `## Lien`."""
    parts = {"titre": "", "lien": "", "resultat": "", "notes": {}, "journal": [], "bilan": []}
    section = None
    for l in lignes_de(chemin):
        if l.startswith("# ") and not parts["titre"]:
            parts["titre"] = l[2:].rsplit(" — notes et journal", 1)[0].strip()
        elif l.startswith("## "):
            section = l[3:].strip()
        elif not l.strip():
            continue
        elif section == "Lien":
            parts["lien"] = parts["lien"] or l.strip()
        elif section == "Résultat":
            parts["resultat"] = une_ligne(parts["resultat"] + " " + l)
        elif section in ("Notes", "Journal") and l.startswith("- ") and " : " in l:
            cle, texte = l[2:].split(" : ", 1)
            if section == "Notes":
                parts["notes"][cle.strip()] = texte.strip()
            else:
                parts["journal"].append((cle.strip(), texte.strip()))
        elif section == "Bilan" and l.startswith("- "):
            parts["bilan"].append(l[2:].strip())
    return parts


def texte_abri(parts):
    """Le `.md`, au format du socle : quatre sections, une entrée par ligne, texte brut — plus
    `## Lien` en tête quand la page a une URL en ligne (chantier HAB)."""
    lignes = ["# %s — notes et journal" % une_ligne(parts["titre"])]
    if parts.get("lien"):
        lignes += ["## Lien", parts["lien"]]
    lignes.append("## Résultat")
    if parts["resultat"]:
        lignes.append(une_ligne(parts["resultat"]))
    lignes.append("## Notes")
    lignes += ["- %s : %s" % (i, une_ligne(t)) for i, t in parts["notes"].items()]
    lignes.append("## Journal")
    lignes += ["- %s : %s" % (d, une_ligne(t)) for d, t in parts["journal"]]
    lignes.append("## Bilan")
    lignes += ["- %s" % une_ligne(t) for t in parts["bilan"]]
    return "\n".join(lignes) + "\n"


def ecrire_abri(chemin, parts):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte_abri(parts))


def brut(fragment):
    """Le texte d'un fragment de page : balises retirées, puis désechappé, sur une ligne.
    Mesuré le 2026-09-26 : 0 note sur 221 et 4 lignes de journal sur 88 portent une balise
    (`<span class="mono">`, `<code>`) dans les 65 pages du kit ; leur texte seul est gardé."""
    return une_ligne(html.unescape(re.sub(r"<[^>]+>", "", fragment)))


def abri_de_page(page):
    """Les quatre parts du `.md`, tirées d'une page HTML existante (amorçage)."""
    titre = re.search(r"<h1>(.*?)</h1>", page, re.S)
    resultat = re.search(r"</h1>\s*<p>(.*?)</p>", page, re.S)
    notes = {i: brut(n) for i, (_, n, _) in lis_page(page).items() if n is not None and brut(n)}
    journal = []
    # Les entrées repliées (les plus anciennes, chantier PLI) d'abord, puis les visibles.
    ul = re.search(r'<ul class="journal">(.*?)\n[ \t]*</ul>', JOURNAL_ANCIEN.sub("", page), re.S)
    ancien = JOURNAL_ANCIEN.search(page)
    ul_ancien = ancien and re.search(r'<ul class="journal">(.*?)\n[ \t]*</ul>', ancien.group(0), re.S)
    for li in re.findall(r"<li>(.*?)</li>", (ul_ancien.group(1) if ul_ancien else "")
                         + (ul.group(1) if ul else ""), re.S):
        date = re.search(r"<time[^>]*>(.*?)</time>", li, re.S)
        texte = brut(li[date.end():] if date else li)
        if texte:
            journal.append((brut(date.group(1)) if date else "", texte))
    bilan = re.search(r'<section>\s*<h2>Chantier clos le [^<]*</h2>\s*<div class="bilan">(.*?)</div>', page, re.S)
    return {"titre": brut(titre.group(1)) if titre else "",
            "resultat": brut(resultat.group(1)) if resultat else "",
            "notes": notes, "journal": journal,
            "bilan": [t for t in (brut(p) for p in re.findall(r"<p>(.*?)</p>", bilan.group(1), re.S)) if t]
            if bilan else []}


def cmd_abri(pages, sortie):
    code = 0
    for chemin in pages:
        md = chemin_abri(chemin)
        if not os.path.isfile(chemin):
            sortie.write("GARDE: page introuvable : %s\n" % chemin)
            code = 1
        elif os.path.exists(md):
            sortie.write("DÉJÀ %s\n" % md)
        else:
            parts = abri_de_page(lire(chemin))
            ecrire_abri(md, parts)
            sortie.write("ABRI %s · résultat %d · notes %d · journal %d · bilan %d\n"
                         % (md, bool(parts["resultat"]), len(parts["notes"]), len(parts["journal"]),
                            bool(parts["bilan"])))
    return code


def page_du_fichier(fichier):
    """La page par défaut d'un fichier de fiches : `<dossier>/artefacts/<nom>.html`."""
    return os.path.join(os.path.dirname(fichier), "artefacts",
                        os.path.splitext(os.path.basename(fichier))[0] + ".html")


def cmd_page(a, sortie):
    date = a.date or __import__("datetime").date.today().isoformat()
    if a.forme and a.creer:
        sortie.write("GARDE: --forme ne va pas avec --creer — une page neuve n'a aucun chiffre à garder\n")
        return 1
    if a.creer:
        if os.path.exists(a.page):
            sortie.write("GARDE: la page existe déjà : %s — --creer n'écrase rien\n" % a.page)
            return 1
        if not (a.projet and a.titre and a.resultat):
            sortie.write("GARDE: --creer demande --projet, --titre et --resultat\n")
            return 1
        html = creer(a.fichier, a.projet, a.titre, a.resultat)
        os.makedirs(os.path.dirname(os.path.abspath(a.page)), exist_ok=True)
    elif not os.path.isfile(a.page):
        sortie.write("GARDE: page introuvable : %s — --creer pour la créer\n" % a.page)
        return 1
    else:
        html = lire(a.page)
    if a.verifier:
        return verifier_page(html, a.fichier, sortie)
    md = chemin_abri(a.page)
    if os.path.exists(md):
        parts = lire_abri(md)
    elif a.creer:
        parts = {"titre": a.titre, "resultat": a.resultat, "notes": {}, "journal": [], "bilan": []}
    else:
        parts = abri_de_page(html)
    for ident, texte in (a.note or []):
        parts["notes"][ident] = texte
    for texte in (a.journal or []):
        parts["journal"].append((date, texte))
    ecrire_abri(md, parts)
    gardes = []
    try:
        html, fiches_, etat, total, hors = regenerer(html, a.fichier, parts, date, gardes, forme=a.forme)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    # Un clos d'avant PLI6 a son bilan en bas : page le remonte aussi, pas seulement clore.
    i = html.find("<!-- ZONE:bilan")
    if i >= 0 and html.startswith("<section>", html.find("<section", i)):
        html = bilan_en_haut(html)
    with open(a.page, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    n = html.count("\n") + (0 if html.endswith("\n") else 1)
    for g in gardes:
        sortie.write(g + "\n")
    sortie.write("PAGE %s · %s · %d lignes · total %s%s\n"
                 % (a.page, comptage(fiches_, etat), n, ligne_cout(*total) if total else "gardé" if a.forme else "non mesuré",
                    ", dont hors fiches %s" % ligne_cout(*hors) if hors else ""))
    joints = recopier_joints(os.path.dirname(os.path.abspath(a.page)))
    sortie.write("CSS %s\n" % joints["vlp.css"])
    sortie.write(ligne_files(joints, a.page))
    if n > SEUIL_PAGE:
        sortie.write("GARDE: %d lignes, au-delà du seuil du script (%d) — la page est relue à chaque fiche\n"
                     % (n, SEUIL_PAGE))
    return 0


# --- etat --------------------------------------------------------------------

NUMERO = re.compile(r"^(\d\d)-")


def nom_etat(contexte):
    """Le `*-etat.md` présent, sinon le premier numéro libre après le plus grand."""
    try:
        noms = sorted(os.listdir(contexte))
    except OSError:
        noms = []
    for n in noms:
        if NUMERO.match(n) and n.endswith("-etat.md"):
            return n
    pris = [int(m.group(1)) for n in noms if (m := NUMERO.match(n))]
    return "%02d-etat.md" % (max(pris) + 1 if pris else 1)


# --- renvois -----------------------------------------------------------------

LIGNE_CHEMIN = re.compile(r"^\s*-\s*\*\*(contexte|index)\*\*\s*:\s*(.+?)\s*$")
CODE = re.compile(r"`([^`]+)`")


def cellules_de(ligne, ou):
    """Les cellules d'une ligne de table Markdown ; `\\|` reste un caractère de sa cellule (PIP, TAB2).
    Une ligne sans barre finale non échappée perdrait sa dernière cellule, en-tête compris, sans
    que le compte le voie : elle lève une `ValueError` préfixée de `ou` (« ligne 4 »…)."""
    morceaux = re.split(r"(?<!\\)\|", ligne.strip())
    if len(morceaux) < 2 or morceaux[-1] != "":
        raise ValueError("%s : pas de barre finale — une ligne de table se ferme par |" % ou)
    return [c.strip() for c in morceaux[1:-1]]


def noms_de_table(lignes, colonne, debut=None):
    """(numéro, nom) des noms entre accents graves dans la cellule `colonne`
    (0 ou -1) des lignes de table ; à partir du titre `debut` s'il est donné,
    jusqu'au titre `## ` suivant. Une ligne qui n'a pas le nombre de cellules
    de son en-tête lève une `ValueError` qui la nomme, au lieu d'être lue
    tronquée (TAB2)."""
    dedans, attendu = debut is None, None
    for i, l in enumerate(lignes, 1):
        if not l.startswith("|"):
            attendu = None
        if debut is not None and l.startswith("## "):
            dedans = l.startswith(debut)
            continue
        if not dedans or not l.startswith("|") or SEPARATEUR.match(l):
            continue
        cellules = cellules_de(l, "ligne %d" % i)
        if attendu is None:
            attendu = len(cellules)
        elif len(cellules) != attendu:
            raise ValueError("ligne %d : %d cellules au lieu de %d — une barre verticale dans une "
                             "cellule s'écrit \\|" % (i, len(cellules), attendu))
        if cellules[0].startswith("*("):
            continue
        for nom in CODE.findall(cellules[colonne]):
            if "<" in nom or "*" in nom or "." not in nom:
                continue
            yield i, nom


def noms_des_sources(projet, sources):
    """[(source, [(numéro, nom)] ou None si le fichier manque)] de chaque source de `renvois`,
    tout lu avant la moindre sortie ; une table coupée lève la `ValueError` de `noms_de_table`,
    préfixée de sa source (TAB2)."""
    lus = []
    for source, colonne, debut in sources:
        chemin = os.path.join(projet, source)
        if not os.path.isfile(chemin):
            lus.append((source, None))
            continue
        try:
            lus.append((source, list(noms_de_table(lignes_de(chemin), colonne, debut))))
        except ValueError as e:
            raise ValueError("%s, %s" % (source, e)) from e
    return lus


def chemins_de_carte(carte_):
    """{contexte, index} lus aux lignes `- **contexte** :` et `- **index** :` de `CHANTIER.md` ;
    le contexte vaut `context AI/` à défaut."""
    chemins = {"contexte": "context AI/"}
    for l in lignes_de(carte_):
        m = LIGNE_CHEMIN.match(l)
        if m:
            chemins[m.group(1)] = m.group(2)
    return chemins


def cmd_renvois(projet, sortie):
    """Vérifier que les fichiers nommés par l'index, son archive et le routage de `CLAUDE.md`
    existent, et peser ces fichiers de tête ; une table coupée : `GARDE:`, sort 1 (TAB2)."""
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    chemins = chemins_de_carte(os.path.join(projet, "CHANTIER.md"))
    contexte = chemins["contexte"]
    index = chemins.get("index", contexte.rstrip("/") + "/00-INDEX.md")
    sources = [(index, 0, None), (chemin_archive(index), 0, None), ("CLAUDE.md", -1, "## Routage")]
    try:
        lus = noms_des_sources(projet, sources)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    nommes, absents = 0, 0
    for source, noms in lus:
        if noms is None:
            if source == index:
                absents += 1
                sortie.write("ABSENT: CHANTIER.md: %s\n" % index)
            continue
        for i, nom in noms:
            nommes += 1
            if not any(os.path.exists(os.path.join(projet, base, nom)) for base in (contexte, "")):
                absents += 1
                sortie.write("ABSENT: %s:%d: %s\n" % (source, i, nom))
    poids = []
    for nom, source, seuil in (("CLAUDE.md", "CLAUDE.md", SEUIL_CLAUDE), ("CHANTIER.md", "CHANTIER.md", SEUIL_CHANTIER),
                               ("index", index, SEUIL_INDEX)):
        chemin = os.path.join(projet, source)
        n = len(lignes_de(chemin)) if os.path.isfile(chemin) else None
        if n is not None and n > seuil:
            sortie.write("AVERTISSEMENT: %s %d lignes > %d\n" % (source, n, seuil))
        poids.append("%s %s/%d" % (nom, "absent" if n is None else n, seuil))
    sortie.write("POIDS %s\n" % " · ".join(poids))
    sortie.write("RENVOIS %d nommés · %d absents\n" % (nommes, absents))
    return 1 if absents else 0


# --- feuille -----------------------------------------------------------------

AUCUN_ENCOURS = ('    <div class="encours">\n      <div class="titre">Aucun chantier ouvert</div>\n'
                 '      <div>Lancer <span class="mono">/vlp:chantier</span> pour en ouvrir un.</div>\n    </div>\n')
BADGE_COURS = ' <span class="badge" data-etat="cours">en cours</span>'


def retirer_chevrons_url(val):
    """Retirer les chevrons d'une URL si elle est entièrement entre chevrons."""
    if val and re.match(r"^<(https?://[^>]+)>$", val):
        return val[1:-1]
    return val


def champ(lignes, nom, defaut=None):
    """La valeur d'une ligne `- **nom** : valeur` de `CHANTIER.md`."""
    motif = re.compile(r"^\s*-\s*\*\*%s\*\*\s*:\s*(.+?)\s*$" % re.escape(nom))
    for l in lignes:
        m = motif.match(l)
        if m:
            return retirer_chevrons_url(m.group(1))
    return defaut


def lettre_de(id_fiche):
    """Le préfixe d'un id de fiche : `RNV` pour `RNV12`, `Z` pour `Z3`."""
    m = PREFIXE.match(id_fiche)
    return m.group(0) if m else id_fiche[:1]


LETTRES = "Lettres de fiche déjà prises"


def entrees_lettres(liste):
    """Les entrées de la liste des lettres, coupées aux virgules hors parenthèses : un titre à
    virgule n'en ajoute pas (chantier TAR). Partagé par `lettres_prises` et `matin` (NUI15)."""
    entrees, profondeur, debut = [], 0, 0
    for k, c in enumerate(liste):
        profondeur += {"(": 1, ")": -1}.get(c, 0)
        if c == "," and not profondeur:
            entrees.append(liste[debut:k])
            debut = k + 1
    entrees.append(liste[debut:])
    return entrees


def lettre_entree(entree):
    """La lettre d'une entrée, `X (titre)` ou `X` seule, entre backticks tolérée (chantier VOI) ;
    `None` si l'entrée n'en a pas."""
    m = re.match(r"\s*`?([A-Z]{1,3})`?(?: \(|\.?\s*$)", entree)
    return m.group(1) if m else None


def titre_entree(entree):
    """Le titre d'une entrée de la liste des lettres, entre ses parenthèses, espaces resserrés ; « » sans titre."""
    m = re.match(r"\s*`?[A-Z]{1,3}`? \((.*)\)\s*$", entree, re.S)
    return " ".join(m.group(1).split()) if m else ""


def doublon_lettres(liste_a, liste_b):
    """La `GARDE:` d'un code pris deux fois : une entrée de `liste_b` dont la lettre est dans `liste_a` sous un autre
    titre ; `None` sinon — même lettre et même titre, aux backticks et espaces près, c'est la même entrée. La fusion
    l'appelle avant toute écriture : deux chantiers ouverts en parallèle sous un même code se voient (NUI27)."""
    titres = {}
    for e in entrees_lettres(liste_a):
        lettre = lettre_entree(e)
        if lettre:
            titres.setdefault(lettre, titre_entree(e))
    for e in entrees_lettres(liste_b):
        lettre = lettre_entree(e)
        if lettre in titres and titre_entree(e) != titres[lettre]:
            return "GARDE: le code %s est pris deux fois : « %s » et « %s »" % (lettre, titres[lettre], titre_entree(e))
    return None


def fin_lettres(texte, j):
    """Où finit la liste des lettres qui commence en `j` : le point avant « Un nouveau chantier »,
    sinon la fin de sa ligne, sinon celle du texte. Partagé par `clore` et `matin` (NUI15)."""
    k = texte.find(". Un nouveau chantier", j)
    if k < 0:
        k = texte.find("\n", j)
    return k if k >= 0 else len(texte)


def lettres_prises(lignes):
    """Les lettres de la ligne « Lettres de fiche déjà prises » : une par entrée, `X (titre)`
    ou `X` seule, une lettre entre backticks tolérée (chantier VOI) ; les entrées se séparent
    aux virgules hors parenthèses, et un titre à virgule n'en ajoute pas (chantier TAR)."""
    texte = " ".join(l for l in lignes if l.strip())
    i = texte.find(LETTRES)
    if i < 0:
        return []
    fin = texte.find("Un nouveau chantier", i)
    liste = texte[i:fin if fin > 0 else None].split(":", 1)[-1]
    return [l for l in map(lettre_entree, entrees_lettres(liste)) if l]


def bornes(ids):
    """La fiche au plus petit et au plus grand numéro, pas l'ordre du fichier : REV rangé
    REV1…REV3, REV5…REV8, REV4 va de REV1 à REV8 (chantier PLG)."""
    rang = sorted(ids, key=lambda i: int(re.sub(r"\D", "", i) or 0))
    return rang[0], rang[-1]


def plage(ids):
    return "%s–%s" % bornes(ids) if len(ids) > 1 else ids[0]


# Le gras et les liens Markdown d'un texte déjà échappé. Un <span class="mono"> y est mis
# de côté sous un jeton `<n>` : hors des balises, un texte échappé n'a aucun `<`.
MONO = re.compile(r'<span class="mono">[^<]*</span>')
MORCEAU = re.compile(r"((?:%s|[^<])+)|<[^>]*>" % MONO.pattern)
JETON = re.compile(r"<(\d+)>")
GRAS = re.compile(r"\*\*(?!\s)(.+?)(?<!\s)\*\*")
LIEN = re.compile(r'\[([^\[\]]+)\]\((https?://(?:[^\s"()<]|\([^\s"()<]*\))+)\)')


def gras_et_liens(html):
    """`**x**` → `<strong>`, `[t](http…)` → `<a>` ; deux passes = une.

    Rien n'est converti dans un `<span class="mono">`, mais un gras peut l'englober.
    Toute autre balise borne un gras et reste telle quelle : une ligne entière se
    rejoue sans qu'un gras saute d'une cellule à l'autre. Un lien devient un jeton
    entier, son gras converti dedans : un gras du dehors l'englobe, sans le couper.
    """
    def morceau(m):
        if not m.group(1):
            return m.group(0)
        mis = []

        def jeton(bout):
            mis.append(bout)
            return "<%d>" % (len(mis) - 1)

        def rendu(t):
            return JETON.sub(lambda j: mis[int(j.group(1))], GRAS.sub(r"<strong>\1</strong>", t))

        t = MONO.sub(lambda j: jeton(j.group(0)), m.group(0))
        t = LIEN.sub(lambda j: jeton('<a href="%s">%s</a>' % (j.group(2), rendu(j.group(1)))), t)
        return rendu(t)
    return MORCEAU.sub(morceau, html)


def cellule_md(texte):
    texte = esc(texte.replace("\\|", "|"))
    return gras_et_liens(CODE.sub(lambda m: '<span class="mono">%s</span>' % m.group(1), texte))


SEPARATEUR = re.compile(r"^\|[\s|:-]+\|?$")     # `|---|---|`, sous l'en-tête d'une table


def todo_du_fichier(lignes):
    """[(numéro, chantier, apporte, coût, dépend)] de la table `| # | Chantier |`. Une ligne
    qui n'a pas ses 5 cellules — une barre verticale non échappée dans une cellule — lève une
    `ValueError` qui la nomme, au lieu d'être tronquée en silence (chantier PIP) ; `\\|` reste
    un caractère."""
    rangs, dedans = [], False
    for l in lignes:
        if l.startswith("| # | Chantier"):
            dedans = True
            continue
        if not dedans:
            continue
        if not l.startswith("|"):
            break
        if SEPARATEUR.match(l):
            continue
        cellules = cellules_de(l, "ligne %s de la TODO" % (l.split("|")[1].strip() or "?"))
        if len(cellules) != 5:
            raise ValueError("ligne %s de la TODO : %d cellules au lieu de 5 — une barre verticale "
                             "dans une cellule s'écrit \\|" % (cellules[0] if cellules else "?", len(cellules)))
        rangs.append(cellules)
    return rangs


def zone(html, nom, ouvre, ferme):
    """(début, fin) du contenu entre `ouvre` (après le marqueur `ZONE:nom`) et `ferme`."""
    i = html.find("<!-- ZONE:%s" % nom)
    if i < 0:
        raise ValueError("marqueur ZONE:%s absent de la page" % nom)
    debut = html.find(ouvre, html.find("-->", i))
    fin = html.find(ferme, debut)
    if debut < 0 or fin < 0:
        raise ValueError("ZONE:%s sans %s … %s" % (nom, ouvre.strip(), ferme.strip()))
    return debut + len(ouvre), fin


# Les deux formes de la TODO d'une feuille de route : cartes (chantier FEU), tableau d'avant.
FORMES_TODO = (("cartes", '<ol class="todo">\n', "        </ol>"),
               ("tableau", "<tbody>\n", "        </tbody>"))


def zone_todo(html):
    """(début, fin, forme) du contenu de `ZONE:todo`, forme `cartes` ou `tableau`. Bornée au
    prochain `<!-- ZONE:` : `zone` chercherait sans borne, et sur une feuille en cartes
    prendrait le `<tbody>` des clos pour la TODO (chantier FEU)."""
    i = html.find("<!-- ZONE:todo")
    if i < 0:
        raise ValueError("marqueur ZONE:todo absent de la page")
    depart = html.find("-->", i)
    borne = html.find("<!-- ZONE:", depart)
    if borne < 0:
        borne = len(html)
    for forme, ouvre, ferme in FORMES_TODO:
        debut = html.find(ouvre, depart, borne)
        fin = html.find(ferme, debut, borne) if debut >= 0 else -1
        if fin >= 0:
            return debut + len(ouvre), fin, forme
    raise ValueError("ZONE:todo sans tableau ni cartes avant la zone suivante")


def rang_en_cours(contenu, forme):
    """Le rang qui porte le badge « en cours » dans le contenu de `zone_todo` : 2e cellule d'une
    ligne de tableau ; sur une carte, avant la fin de son `summary` — colonne de gauche, ou titre
    dans la forme d'avant les colonnes. None sans badge."""
    rang = (r'<span class="rang mono">(\d+)</span>' if forme == "cartes"
            else r'<tr><td class="mono">(\d+)</td><td>')
    m = re.search(rang + r'(?:(?!</td>|</summary>).)*?' + re.escape(BADGE_COURS), contenu)
    return m.group(1) if m else None


def en_cartes(html):
    """La TODO d'une feuille en tableau passée en liste de cartes vide : le `<div class="tableau">`
    de la zone (à défaut, sa `<table>`) cède la place à `<ol class="todo">` ; ce qui le précède
    dans la zone reste — 4 feuilles sur 5 y ont du texte le 2026-09-27 (chantier FEU)."""
    d, f, forme = zone_todo(html)
    if forme == "cartes":
        return html
    depart = html.find("-->", html.find("<!-- ZONE:todo"))
    debut, ferme = html.rfind('<div class="tableau">', depart, d), "</div>"
    if debut < 0:
        debut, ferme = html.rfind("<table", depart, d), "</table>"
    fin = html.find(ferme, html.find("</table>", f))
    if debut < 0 or fin < 0:
        raise ValueError("ZONE:todo : tableau sans bloc à remplacer")
    return html[:debut] + '<ol class="todo">\n        </ol>' + html[fin + len(ferme):]


LECTURE = '<details class="lecture"><summary>Comment lire cette liste</summary>'


def replier_lecture(html):
    """Le texte de `ZONE:todo` d'avant les cartes (`zone_todo`) replié dans un `details.lecture`
    fermé, ni retouché ni retiré ; posé une fois — déjà replié, que du blanc ou pas de cartes : la
    page reste (chantier BTN, Cairn en a 177 mots le 2026-09-27)."""
    d, _, forme = zone_todo(html)
    if forme != "cartes":
        return html
    depart = html.find("-->", html.find("<!-- ZONE:todo")) + len("-->")
    avant = html[depart:html.rfind('<ol class="todo">', depart, d)]
    if not avant.strip() or 'class="lecture"' in avant:
        return html
    i, j = depart + len(avant) - len(avant.lstrip()), depart + len(avant.rstrip())
    ligne = html[html.rfind("\n", 0, i) + 1:i]
    marge = ligne[:len(ligne) - len(ligne.lstrip(" \t"))]
    return html[:i] + LECTURE + "\n" + marge + html[i:j] + "\n" + marge + "</details>" + html[j:]


SOMMAIRE = ('  <nav class="sommaire" aria-label="Sommaire"><a href="#encours">Chantier en cours</a>'
            '<a href="#todo">Chantiers possibles</a><a href="#clos">Chantiers clos</a></nav>\n')


def sommaire(html):
    """Le sommaire sous l'en-tête, et l'`id` des trois sections qu'il vise, posés **une seule
    fois** : déjà là, la page reste telle quelle. Sans `</header>`, ou sans une section propre à
    chacune des trois zones, rien n'est posé — un lien sans cible ne sert à rien (chantier FEU)."""
    if 'class="sommaire"' in html:
        return html
    tete = html.find("</header>")
    cibles = []
    for nom in ("encours", "todo", "clos"):
        z = html.find("<!-- ZONE:" + nom)
        if z < 0 and nom == "clos":
            z = html.find("<!-- ZONE:archive")   # les clos partis dans l'archive (chantier ARC)
        s = html.rfind("<section", 0, z) if z >= 0 else -1
        if s < 0:
            return html
        cibles.append((s + len("<section"), nom))
    if tete < 0 or len({i for i, _ in cibles}) < 3:
        return html
    for i, nom in sorted(cibles, reverse=True):
        html = html[:i] + ' id="%s"' % nom + html[i:]
    i = html.find("\n", tete) + 1
    return html[:i] + "\n" + SOMMAIRE + html[i:]


def depend_todo(de):
    """La cellule « Dépend de » d'un chantier possible, dans la colonne de gauche de sa carte : ses
    codes entre backticks par `fleche` ; un rang (`3`) tel quel ; rien pour `—`."""
    codes = re.findall(r"`([^`]+)`", de)
    if codes:
        return fleche(codes, "chantiers")
    return "" if de.strip() in ("", "—", "-", "rien") else '<span class="dep mono">← %s</span>' % cellule_md(de)


def feuille(projet, html, todo, date):
    """(page régénérée, bilan) : encours, todo et lettres depuis `CHANTIER.md` et le fichier d'état."""
    html = migrer_joints(migrer_style(html))
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    etat = champ(carte_, "fichier d'état")
    if not etat:
        raise ValueError("fichier d'état introuvable : aucun")
    lignes_etat = lignes_du_projet(projet, etat, "fichier d'état")
    courant = courant_de(projet)
    lettres = lettres_prises(carte_)
    # Sans la lettre du chantier en cours : `feuille` l'ajoute plus bas pour l'affichage, mais un
    # chantier possible qui en dépend n'est pas bloqué par ce seul ajout (chantier FEU).
    lettres_todo = list(lettres)
    if courant:
        lignes = lignes_du_projet(projet, courant, "fichier de fiches courant")
        ids = [l.split()[1] for l in lignes if TITRE.match(l)]
        titre = next((re.sub(r"^# Chantier \S+ — ", "", l) for l in lignes if l.startswith("# ")), courant)
        url = champ(carte_, "artefact du chantier", "aucun")
        lien = "" if url.lower().startswith("aucun") else ' — <a href="%s">la page du chantier</a>' % esc(url)
        encours = ('    <div class="encours">\n      <div class="titre">%s%s</div>\n'
                   '      <div>Fiches <span class="mono">%s</span>%s</div>\n    </div>\n'
                   % (cellule_md(titre), BADGE_COURS, plage(ids) if ids else "?", lien))
        if ids and lettre_de(ids[0]) not in lettres:
            lettres.append(lettre_de(ids[0]))
    else:
        encours = AUCUN_ENCOURS
    d, f, forme = zone_todo(html)
    if todo is None and courant:
        todo = rang_en_cours(html[d:f], forme)
    rangs = todo_du_fichier(lignes_etat)
    if todo is not None and todo not in [r[0] for r in rangs]:
        raise ValueError("--todo %s absent de la TODO de %s" % (todo, etat))
    # Une carte par rang, en colonnes comme les fiches : rang, badge et dépendances à gauche, le
    # titre qui replie « Ce qu'il apporte » (chantier FEU), le coût estimé à droite.
    corps = "".join('          <li class="carte-todo"><span class="gauche"><span class="rang mono">%s</span>%s%s</span>'
                    '<details><summary><span class="titre">%s</span></summary><div class="detail">%s</div></details>'
                    '<span class="meta mono">%s</span></li>\n'
                    % (esc(n), BADGE_COURS if n == todo else "", depend_todo(de), cellule_md(ch), cellule_md(ap),
                       cellule_md(co)) for n, ch, ap, co, de in rangs) \
        or '          <li class="rien">Rien en attente.</li>\n'
    cartes = replier_lecture(en_cartes(html))
    d, f, _ = zone_todo(cartes)
    neuf = compte_todo(cartes[:d] + corps + cartes[f:], rangs, lettres_todo)
    d, f = zone(neuf, "encours", "\n", "  </section>")
    neuf = neuf[:d] + encours + neuf[f:]
    neuf = re.sub(r'(Lettres de fiche prises : <span class="mono">).*?(</span>)',
                  lambda m: m.group(1) + ", ".join(lettres) + m.group(2), neuf, count=1)
    neuf = balise_couts(sommaire(neuf), couts_du_projet(projet, neuf))
    if neuf != html:
        neuf = re.sub(r'(Mis à jour le <span class="mono">).*?(</span>)',
                      lambda m: m.group(1) + date + m.group(2), neuf, count=1)
    bilan = "FEUILLE todo %d · encours %s · lettres %d" % (len(rangs), "oui" if courant else "non", len(lettres))
    return neuf, bilan


# Les deux formes : `<p class="resume-todo">` (chantier BTN) et celle d'avant, `mono` et `style=`.
RESUME_TODO = re.compile(r'    <p class="(?:mono )?resume-todo"[^>]*>.*?</p>\n')


# Au-delà de cette borne haute, en fiches, un chantier est « gros » : le décompte le compte tel,
# le tri du soir le découpe le soir même (`trier`, NUI10). Une seule valeur, lue par les deux.
GROS_FICHES = 4


NOMBRE_COUT = r"(?:\d+(?:,\d+)?½?|½)"
PLAGE_COUT = r"%s(?:\s*(?:à|-)\s*%s)?" % (NOMBRE_COUT, NOMBRE_COUT)


def borne_haute_cout(cout):
    """La borne haute d'un « Coût » de TODO, en fiches — `~4 à 6` → 6, `2-3` → 3, `~0,5` → 0,5,
    `~½` → 0,5 (`½` se lit 0,5 ; `1½`, 1,5) —, ou `None` sans plage suivie de « fiche(s) »
    (`à cadrer`, `🟡 pas estimé`, `—`, `sans fiche`) (FEU8, NUI10). La dernière estimation fait foi
    (NUI38) : le dernier segment ` · ` qui dit « fiche(s) » ; dans ce segment, la plage qui suit la
    dernière `→`, sinon la dernière plage suivie de « fiche(s) » — jamais une somme ni une durée."""
    segments = [s for s in cout.split(" · ") if re.search(r"\bfiches?\b", s)]
    if not segments:
        return None
    segment = segments[-1]
    apres = re.match(r"\s*[~≈+]?\s*(%s)" % PLAGE_COUT, segment.rsplit("→", 1)[1]) if "→" in segment else None
    plages = [apres.group(1)] if apres else re.findall(r"(%s)\s*fiches?\b" % PLAGE_COUT, segment)
    if not plages:
        return None
    nombres = re.findall(NOMBRE_COUT, plages[-1])
    return max(float(n.rstrip("½").replace(",", ".") or 0) + (0.5 if n.endswith("½") else 0) for n in nombres)


def dependances(depend):
    """(codes, rangs) d'une cellule « Dépend de » : les codes entre backticks, les numéros ou
    plages hors backticks développés en rangs (`1..3` → `{"1", "2", "3"}`) (FEU8, NUI10)."""
    codes = re.findall(r"`([A-Za-z]+)`", depend)
    rangs = set()
    for m in re.finditer(r"(\d+)(?:\.\.(\d+))?", re.sub(r"`[^`]*`", "", depend)):
        bas, haut = int(m.group(1)), int(m.group(2)) if m.group(2) else int(m.group(1))
        rangs.update(str(r) for r in range(bas, haut + 1))
    return codes, rangs


def est_bloque(depend, lettres_todo, rangs_presents):
    """Vrai si `depend` (cellule « Dépend de ») nomme un code entre backticks absent de
    `lettres_todo`, ou un numéro (`3`) ou une plage (`1..9`) qui touche un rang de
    `rangs_presents` — encore dans la TODO (FEU8)."""
    codes, rangs = dependances(depend)
    return any(lettre_de(c) not in lettres_todo for c in codes) or bool(rangs & set(rangs_presents))


def decompte_todo(rangs, lettres_todo):
    """(petits, moyens, gros, pas_estimés, bloqués, total en fiches) des rangs d'une TODO —
    petit ≤ 1, moyen ≤ `GROS_FICHES`, gros au-delà de la borne haute de leur « Coût » (FEU8)."""
    presents = {r[0] for r in rangs}
    petits = moyens = gros = pas_estimes = bloques = 0
    total = 0.0
    for _, _, _, cout, depend in rangs:
        borne = borne_haute_cout(cout)
        if borne is None:
            pas_estimes += 1
        else:
            total += borne
            if borne <= 1:
                petits += 1
            elif borne <= GROS_FICHES:
                moyens += 1
            else:
                gros += 1
        if est_bloque(depend, lettres_todo, presents):
            bloques += 1
    return petits, moyens, gros, pas_estimes, bloques, total


def resume_todo(n, petits=0, moyens=0, gros=0, pas_estimes=0, bloques=0, total=0.0):
    """Le décompte posé au-dessus de la TODO, comme `resume_clos` au-dessus des clos — parts à
    zéro omises, singulier sous 2 (FEU8)."""
    if not n:
        return "aucun chantier possible"
    base = "1 chantier possible" if n == 1 else "%d chantiers possibles" % n
    parts = ["%d %s" % (c, s if c < 2 else p) for c, s, p in
             ((petits, "petit", "petits"), (moyens, "moyen", "moyens"),
              (gros, "gros", "gros"), (pas_estimes, "pas estimé", "pas estimés")) if c]
    if parts:
        base += " · " + ", ".join(parts)
    if bloques:
        base += " · %d %s" % (bloques, "bloqué" if bloques < 2 else "bloqués")
    if total:
        base += " · ≈%s %s" % (decimal_fr(total), "fiche estimée" if total == 1 else "fiches estimées")
    return base


def compte_todo(html, rangs, lettres_todo):
    """La ligne du décompte, remplacée ; ou posée juste avant `ZONE:todo` sur une
    feuille d'avant qui ne l'a pas. Ce qui précède le premier ` · ` en `<strong>`, le style dans
    `vlp.css` (`.resume-todo`, chantier BTN)."""
    tete, sep, reste = resume_todo(len(rangs), *decompte_todo(rangs, lettres_todo)).partition(" · ")
    ligne = '    <p class="resume-todo"><strong>%s</strong>%s%s</p>\n' % (tete, sep, reste)
    if RESUME_TODO.search(html):
        return RESUME_TODO.sub(lambda _: ligne, html, count=1)
    i = html.rfind("\n", 0, html.index("<!-- ZONE:todo")) + 1
    return html[:i] + ligne + html[i:]


def page_feuille(projet):
    contexte = champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "contexte", "context AI/")
    return os.path.join(projet, contexte, "artefacts", "feuille-de-route.html")


# Les lignes des chantiers clos vivent dans `archive-clos.html` s'il existe, sinon dans la feuille
# (chantier ARC) : tout ce qui lit ou écrit une ligne close, son pied ou son prix passe par
# `page_clos` ; l'en-tête, la TODO, `encours` et le graphique restent sur la feuille.
ARCHIVE_CLOS = "archive-clos.html"


def page_clos(projet):
    archive = os.path.join(os.path.dirname(page_feuille(projet)), ARCHIVE_CLOS)
    return archive if os.path.isfile(archive) else page_feuille(projet)


def couts_du_projet(projet, html):
    """Les barres du graphique de la feuille `html` : lues dans l'archive si le projet en a une."""
    archive = page_clos(projet)
    return couts_clos(lire(archive) if archive != page_feuille(projet) else html)


def rafraichir_couts(projet, page, html):
    """Après l'écriture des lignes closes `html` dans `page` : `couts.svg` refait à côté de la feuille ;
    `page` est l'archive, le bloc `ZONE:archive` et la balise de la feuille aussi (chantier ARC)."""
    feuille_ = page_feuille(projet)
    if page == feuille_:
        return ecrire_couts(page, html)
    couts = couts_clos(html)
    avant = lire(feuille_)
    neuf = balise_couts(poser_bloc_archive(avant, html, champ(lignes_de(os.path.join(projet, "CHANTIER.md")),
                                                                "artefact archive")), couts)
    if neuf != avant:
        with open(feuille_, "w", encoding="utf-8", newline="") as fh:
            fh.write(neuf)
    return ecrire_couts(feuille_, neuf, couts)


GABARIT_ARCHIVE = "templates/artefact-archive-clos.html"
ICI_ARCHIVE = "    <!-- ARCHIVE:table -->\n"
BLOC_ARCHIVE = re.compile(r"    <!-- ZONE:archive[^\n]*\n.*?    <!-- /ZONE:archive -->\n", re.S)


def poser_bloc_archive(feuille_html, archive_html, url):
    """La feuille avec son bloc `ZONE:archive` refait sur les lignes closes de l'archive : le résumé
    replié (nombre, tokens, $) et le lien — `details.clos` y reste, où `balise_couts` pose le
    graphique. Sans bloc ni `ZONE:clos`, rien ne change (chantier ARC)."""
    d, f = zone(archive_html, "clos", "<tbody>\n", "        </tbody>")
    corps = archive_html[d:f]
    usd, n_usd = prix_clos(corps)
    lien = ('<a href="%s">dans l\'archive</a>' % esc(url) if url and not url.lower().startswith("aucun")
            else "dans l'archive, pas encore publiée")
    bloc = ('    <!-- ZONE:archive — les chantiers clos vivent dans l\'archive (chantier ARC) ; refait par clore -->\n'
            '    <details class="clos">\n      <summary><span class="resume-clos">%s</span></summary>\n'
            '      <p>Le détail de chacun, le plus récent en haut : %s.</p>\n    </details>\n'
            '    <!-- /ZONE:archive -->\n' % (resume_clos(len(lignes_clos(corps)), total_clos(corps), usd, n_usd), lien))

    def refait(m):
        # le graphique déjà posé reste : `clore` refait le bloc après `feuille`, qui l'a posé
        garde = BALISE_COUTS.search(m.group(0))
        return bloc.replace("    <details", (garde.group(0) if garde else "") + "    <details", 1)
    return BLOC_ARCHIVE.sub(refait, feuille_html, count=1)


def poser_champ(texte, nom, valeur, apres):
    """`texte` (un `CHANTIER.md`) avec sa ligne `- **nom** : valeur`, remplacée, sinon posée après la
    ligne du champ `apres`, sinon en fin de fichier."""
    ligne = "- **%s** : %s" % (nom, valeur)
    motif = re.compile(r"^\s*-\s*\*\*%s\*\*\s*:.*$" % re.escape(nom), re.M)
    if motif.search(texte):
        return motif.sub(lambda _: ligne, texte, count=1)
    m = re.search(r"^\s*-\s*\*\*%s\*\*\s*:.*$" % re.escape(apres), texte, re.M)
    fin = "\r\n" if "\r\n" in texte else "\n"
    if m:
        return texte[:m.end()] + fin + ligne + texte[m.end():]
    return texte.rstrip("\r\n") + fin + ligne + fin


def cmd_archive(projet, url, sortie):
    """Les chantiers clos de la feuille déplacés dans `archive-clos.html` (chantier ARC)."""
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    page = page_feuille(projet)
    if not os.path.isfile(page):
        sortie.write("GARDE: feuille de route introuvable : %s\n" % page)
        return 1
    chemin_carte = os.path.join(projet, "CHANTIER.md")
    carte_ = lignes_de(chemin_carte)
    archive = os.path.join(os.path.dirname(page), ARCHIVE_CLOS)
    html = lire(page)
    i = html.find("    <!-- ZONE:clos")
    deplacees = 0
    if i >= 0:
        j = html.find("    </details>\n", i)
        if os.path.isfile(archive) or j < 0:
            sortie.write("GARDE: %s — rien d'écrit\n" % ("archive déjà là, et la feuille a encore ses clos"
                                                         if j >= 0 else "fin des clos introuvable sur la feuille"))
            return 1
        j += len("    </details>\n")
        table = BALISE_COUTS.sub("", html[i:j]).replace('<details class="clos">', '<details class="clos" open>', 1)
        deplacees = len(lignes_clos(table))
        alias = champ(carte_, "alias", os.path.basename(os.path.abspath(projet)))
        gabarit = lire(os.path.join(KIT, GABARIT_ARCHIVE))
        archive_html = (gabarit.replace("&lt;md&gt;", esc(alias))
                        .replace("&lt;URL de la feuille&gt;", esc(champ(carte_, "artefact feuille de route", "")))
                        .replace(ICI_ARCHIVE, table))
        html = html[:i] + "    <!-- ZONE:archive -->\n    <!-- /ZONE:archive -->\n" + html[j:]
    elif not os.path.isfile(archive):
        sortie.write("GARDE: ni chantiers clos sur la feuille, ni archive — rien d'écrit\n")
        return 1
    else:
        archive_html = lire(archive)
    url = url or champ(carte_, "artefact archive")
    neuf = balise_couts(poser_bloc_archive(html, archive_html, url), couts_clos(archive_html))
    avant = lire(page)
    if i >= 0:
        with open(archive, "w", encoding="utf-8", newline="") as fh:
            fh.write(archive_html)
    if neuf != avant:
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(neuf)
    if url:
        texte = lire(chemin_carte)
        texte_neuf = poser_champ(texte, "artefact archive", url, "artefact feuille de route")
        if texte_neuf != texte:
            with open(chemin_carte, "w", encoding="utf-8", newline="") as fh:
                fh.write(texte_neuf)
    joints = recopier_joints(os.path.dirname(os.path.abspath(page)))
    joints.update(ecrire_couts(page, neuf, couts_clos(archive_html)))
    sortie.write(ligne_files(joints, page))
    sortie.write("ARCHIVE %d déplacées · %d dans l'archive · feuille %d → %d octets · %s — %s\n" % (
        deplacees, len(lignes_clos(archive_html)), len(avant.encode("utf-8")), len(neuf.encode("utf-8")),
        "url %s" % url if url else "sans url", archive))
    return 0


# --- le fichier des nuits : `<contexte>/NN-nuits.md` (chantier NUI) ------------

# Les seuls endroits de ces nombres : la leçon sous LECON_INDICE nuits n'est qu'un « indice », au-delà
# de LECONS_MAX vivantes la liste ne se lit plus d'un coup d'œil, et sous CARNET_MIN fiches acceptées
# la médiane des nuits n'est pas un chiffre (NUI11).
LECON_INDICE = 3
LECONS_MAX = 12
CARNET_MIN = 5
NUITS_TETE = ["# Les nuits — le plan du soir, la table des nuits, les leçons", "",
              "QUAND LIRE : on prépare une nuit (plan du soir) ou on relit les nuits passées (table, leçons) ;"
              " `vlp.py trier` imprime les leçons.", "",
              "| nuit | canal | chantier | jouées/acceptées/refusées | $ |", "|---|---|---|---|---|", "",
              "## Leçons", "",
              "Forme d'une leçon, écrite ici seul : `- <date> · N=<n> · <une cause, pas un constat> · <nombres nommés>"
              " · nuits <dates> · sessions <ids>`. N sous `LECON_INDICE` (`vlp.py`) : « indice ». Retirée, elle reste,"
              " suffixée `— retirée le <date> par <chantier ou nuit>`. Tenue deux nuits, proposée au matin, deux oui"
              " de l'utilisateur : elle monte. La colonne `$` est la somme des `usd_kit` du carnet."]
LIGNE_NUMERO = re.compile(r"^\|\s*`(\d+)")
LECON_FORME = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · N=(\d+) · (.+?) · (.+?) · nuits (.+?) · sessions (.+?)"
                         r"(?: — retirée le (\d{4}-\d{2}-\d{2}) par (.+))?$")


def fichier_nuits(projet, creer=False):
    """Le `*-nuits.md` du `contexte`, ou None s'il manque ; deux → `ValueError`. Absent et `creer` :
    le premier numéro libre (le plus grand du dossier + 1, deux chiffres au moins), écrit depuis
    `NUITS_TETE`, et sa ligne d'index sous le plus grand numéro lu en entier — sans `**clos**` ni
    `**ouvert**`, que `archiver` et `ouvrir` liraient. Relancé : rien. Tout est calculé avant d'écrire."""
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    dossier = os.path.normpath(os.path.join(projet, champ(carte_, "contexte", "context AI/")))
    trouves = sorted(os.path.join(dossier, f) for f in (os.listdir(dossier) if os.path.isdir(dossier) else [])
                     if f.endswith("-nuits.md"))
    if len(trouves) > 1:
        raise ValueError("deux fichiers des nuits : %s" % ", ".join(os.path.basename(t) for t in trouves))
    if trouves or not creer:
        return trouves[0] if trouves else None
    if not os.path.isdir(dossier):
        raise ValueError("dossier de contexte introuvable : %s" % dossier)
    index = champ(carte_, "index")
    chemin_index = os.path.join(projet, index) if index else None
    if not chemin_index or not os.path.isfile(chemin_index):
        raise ValueError("index introuvable : %s" % index)
    numeros = [int(m.group(1)) for m in (re.match(r"(\d+)-", f) for f in os.listdir(dossier)) if m]
    nom = "%02d-nuits.md" % (max(numeros, default=-1) + 1)
    idx = lignes_de(chemin_index)
    rangs = [(int(m.group(1)), k) for k, m in ((k, LIGNE_NUMERO.match(l)) for k, l in enumerate(idx)) if m]
    if not rangs:
        raise ValueError("aucune ligne de fichier dans %s" % index)
    idx.insert(max(rangs)[1] + 1, "| `%s` | on prépare ou on relit une nuit — plan du soir, table des nuits, leçons |" % nom)
    chemin = os.path.join(dossier, nom)
    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(NUITS_TETE) + "\n")
    with open(chemin_index, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(idx) + "\n")
    return chemin


def sections_nuits(lignes):
    """(table, leçons) : chacun `(début, fin)` en indices de `lignes`, fin exclue — la table depuis sa
    ligne d'en-tête `| nuit |` jusqu'à la première ligne qui n'en est pas une, les leçons depuis
    `## Leçons` jusqu'au titre suivant. `ValueError` si l'un manque."""
    d = next((k for k, l in enumerate(lignes) if l.startswith("| nuit |")), None)
    if d is None:
        raise ValueError("table des nuits absente : pas de ligne `| nuit | …`")
    f = d + 1
    while f < len(lignes) and lignes[f].startswith("|"):
        f += 1
    ld = next((k for k, l in enumerate(lignes) if l.strip() == "## Leçons"), None)
    if ld is None:
        raise ValueError("section `## Leçons` absente")
    lf = next((k for k in range(ld + 1, len(lignes)) if lignes[k].startswith("## ")), len(lignes))
    return (d, f), (ld, lf)


def nuits_du_fichier(lignes):
    """([cellules de chaque ligne de la table], [leçons]) d'un fichier des nuits ; une leçon est un
    dict `i` (indice de sa ligne), `n` (N), `retiree`. Une ligne de table qui n'a pas ses 5 cellules,
    ou une ligne `- ` de `## Leçons` hors de la forme, lève une `ValueError` qui la cite (NUI11)."""
    (td, tf), (ld, lf) = sections_nuits(lignes)
    rangees = []
    for k in range(td + 1, tf):
        if re.match(r"^\|[\s|:-]+\|?$", lignes[k]):
            continue
        cellules = cellules_de(lignes[k], "ligne %d de la table des nuits" % (k + 1))
        if len(cellules) != 5:
            raise ValueError("ligne %d de la table des nuits : %d cellules au lieu de 5 — une barre verticale "
                             "dans une cellule s'écrit \\|" % (k + 1, len(cellules)))
        rangees.append(cellules)
    lecons = []
    for k in range(ld + 1, lf):
        if lignes[k].startswith("- "):
            m = LECON_FORME.match(lignes[k])
            if not m:
                raise ValueError("leçon hors forme, ligne %d : %s" % (k + 1, lignes[k]))
            lecons.append({"i": k, "n": int(m.group(2)), "retiree": m.group(7) is not None})
    return rangees, lecons


def ecrire_lignes(chemin, lignes):
    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lignes) + "\n")


def nuits_ecrire(chemin, ligne):
    """Une ligne de table (`| …`) après la dernière de la table, ou une leçon (`- …`) après la dernière
    ligne de `## Leçons` ; le fichier d'après est relu par `nuits_du_fichier` avant l'écriture. Déjà là :
    rien (rend False). Ni l'un ni l'autre : `ValueError`."""
    lignes = lignes_de(chemin)
    nuits_du_fichier(lignes)
    if ligne in lignes:
        return False
    (td, tf), (ld, lf) = sections_nuits(lignes)
    if ligne.startswith("- "):
        fin = lf
        while fin - 1 > ld and not lignes[fin - 1].strip():
            fin -= 1
        # Un paragraphe, puis une liste : la première leçon prend une ligne vide devant elle.
        neuf_ligne = ["", ligne] if lignes[fin - 1].strip() and not lignes[fin - 1].startswith("- ") else [ligne]
    elif ligne.startswith("|"):
        fin, neuf_ligne = tf, [ligne]
    else:
        raise ValueError("ni ligne de table ni leçon : %s" % ligne)
    neuf = lignes[:fin] + neuf_ligne + lignes[fin:]
    nuits_du_fichier(neuf)
    ecrire_lignes(chemin, neuf)
    return True


def nuits_retirer(chemin, lecon, date, par):
    """La leçon `lecon` (sa ligne entière) suffixée `— retirée le <date> par <par>` : elle reste. Déjà
    retirée : rien (rend False). Introuvable : `ValueError`."""
    lignes = lignes_de(chemin)
    _, lecons = nuits_du_fichier(lignes)
    for l in lecons:
        if lignes[l["i"]] == lecon:
            lignes[l["i"]] += " — retirée le %s par %s" % (date, par)
            nuits_du_fichier(lignes)
            ecrire_lignes(chemin, lignes)
            return True
        if lignes[l["i"]].startswith(lecon + " — retirée le "):
            return False
    raise ValueError("leçon introuvable : %s" % lecon)


def usd_par_fiche(usd, fiches_usd):
    """Le prix d'une fiche au prix mesuré des clos : la division d'`ouvrir` pour l'estimé, aussi celle
    du `TAUX jour` de `trier` (NUI11)."""
    return float(usd) / fiches_usd


def taux_jour(projet):
    """La ligne `TAUX jour` : le prix par fiche des chantiers clos de la feuille, tel qu'`ouvrir` l'écrit
    dans son estimé ; sans clos au prix mesuré, `indice` et pourquoi."""
    page = page_clos(projet)
    if not os.path.isfile(page):
        return "TAUX jour indice — feuille de route introuvable"
    _, n_fiches, n_clos, usd, fiches_usd = moyenne_clos(lire(page))
    if not n_fiches or usd is None:
        return "TAUX jour indice — aucun chantier clos au prix mesuré"
    return "TAUX jour %s/fiche sur %d clos" % (approx(usd_par_fiche(usd, fiches_usd)), n_clos)


def taux_nuit(lignes):
    """(médiane, n, sans) des lignes de carnet : une fiche est (nuit, chantier, fiche), acceptée si une
    ligne `relire` n'a pas de `refus_n` ; son prix, la somme des `usd_kit` de ses lignes de session —
    jamais `usd_cli`. `n` : les fiches acceptées qui ont un prix, `sans` : leurs lignes sans `usd_kit`.
    Médiane `None` sans fiche."""
    fiches = {}
    for d in lignes:
        if carnet.est_session(d) and d.get("fiche"):
            fiches.setdefault((d.get("nuit"), d.get("chantier"), d["fiche"]), []).append(d)
    sommes, sans = [], 0
    for ds in fiches.values():
        if not any(d.get("role") == "relire" and not d.get("refus_n") for d in ds):
            continue
        prix = [u for d in ds for u in [d.get("usd_kit")] if u is not None]
        sans += len(ds) - len(prix)
        if prix:
            sommes.append(sum(prix))
    return (statistics.median(sommes) if sommes else None), len(sommes), sans


def lignes_taux_nuit(projet):
    """La ligne `TAUX nuit` sur tous les carnets du dépôt : la médiane des fiches acceptées, ou `indice`
    sous `CARNET_MIN` fiches — alors sans chiffre ; les lignes sans `usd_kit` à part."""
    jour = carnet.du_jour(projet)
    lignes = []
    for c in sorted(glob.glob(os.path.join(os.path.dirname(jour), "*.jsonl"))) if jour else []:
        lignes += carnet.lire(c)
    mediane, n, sans = taux_nuit(lignes)
    reste = " · sans usd_kit %d" % sans if sans else ""
    if mediane is None or n < CARNET_MIN:
        return "TAUX nuit indice — %d fiches acceptées%s" % (n, reste)
    return "TAUX nuit médiane %s $/fiche sur %d fiches acceptées%s" % (decimal_fr(round(mediane, 2)), n, reste)


def lecons_nuits(projet, sortie):
    """Les leçons du fichier des nuits imprimées par `imprimer_section`, `indice` accolé aux vivantes
    sous `LECON_INDICE` ; sort 1, par une `GARDE:` qui le nomme, si le fichier ne se lit pas ou si plus
    de `LECONS_MAX` leçons sont vivantes. Sans fichier : une ligne le dit, sort 0."""
    try:
        chemin = fichier_nuits(projet)
        if chemin is None:
            sortie.write("NUITS absent — pas de fichier *-nuits.md\n")
            return 0
        lignes = lignes_de(chemin)
        _, lecons = nuits_du_fichier(lignes)
        _, (ld, lf) = sections_nuits(lignes)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    vivantes = [l for l in lecons if not l["retiree"]]
    for l in vivantes:
        if l["n"] < LECON_INDICE:
            lignes[l["i"]] += " — indice"
    imprimer_section(sortie, "Leçons", os.path.relpath(chemin, projet).replace("\\", "/"), lignes, (ld + 1, lf))
    if len(vivantes) > LECONS_MAX:
        sortie.write("GARDE: %d leçons vivantes, plus de %d — en retirer avant la nuit\n" % (len(vivantes), LECONS_MAX))
        return 1
    return 0


# --- trier : le tri du soir, par script (chantier NUI) -------------------------

# La liste fermée des marques comptées en cellules 3-4 d'un rang : `MARQUES` les affiche, l'`ÉCARTÉE`
# relit les deux qui écartent (la visuelle et `push`). Rien ne cherche le sens d'une marque.
MARQUE_PUSH = "push"
MARQUES_TRI = ("🟡", "à trancher", "non mesuré", MARQUE_VISUELLE, MARQUE_PUSH)
EXTENSIONS_TRI = (".py", ".md", ".html", ".json", ".css", ".js")


def marques_tri(apporte, cout):
    """Les occurrences de chaque marque de `MARQUES_TRI` dans les cellules 3 et 4, casse ignorée."""
    texte = (apporte + "\n" + cout).lower()
    return [texte.count(m.lower()) for m in MARQUES_TRI]


def fichiers_tri(apporte, cout):
    """Les fichiers cités entre backticks dans les cellules 3 et 4 : les mots (`shlex.split`, guillemets
    retirés ; repli `split`) qui finissent en `EXTENSIONS_TRI` — `vlp.py archive` donne `vlp.py`."""
    vus = []
    for bout in CODE.findall(apporte + "\n" + cout):
        try:
            mots = shlex.split(bout)
        except ValueError:
            mots = [w.strip("\"'") for w in bout.split()]
        vus += [w for w in mots if w.lower().endswith(EXTENSIONS_TRI) and w not in vus]
    return vus


def groupes_tri(rangs, codes, prets, fichiers):
    """[([indices], [raisons])] des PRÊTES liées, dans l'ordre de la TODO : par dépendance d'une prête
    sur le code ou le rang d'une autre, puis par un fichier commun comparé sur son nom (`vlp.py` =
    `scripts/vlp.py`). Une prête sans lien reste seule, sans raison."""
    parent = {k: k for k in prets}

    def racine(k):
        while parent[k] != k:
            k = parent[k]
        return k

    liens = []
    for k in prets:
        deps, rangs_dep = dependances(rangs[k][4])
        lettres_dep = {lettre_de(c) for c in deps}
        for j in prets:
            if j != k and (lettre_de(codes[j]) in lettres_dep or rangs[j][0] in rangs_dep):
                liens.append(([k, j], "%s dépend de %s" % (codes[k], codes[j])))
    par_nom = {}
    for k in prets:
        for f in fichiers[k]:
            par_nom.setdefault(os.path.basename(f.replace("\\", "/")), []).append(k)
    for nom, ks in par_nom.items():
        if len(set(ks)) > 1:
            liens.append((sorted(set(ks)), "fichier %s : %s" % (nom, ", ".join(codes[k] for k in sorted(set(ks))))))
    for membres, _ in liens:
        for k in membres[1:]:
            parent[racine(k)] = racine(membres[0])
    groupes = {}
    for k in prets:
        groupes.setdefault(racine(k), []).append(k)
    rendu = []
    for membres in groupes.values():
        raisons = []
        for m, texte in liens:
            if m[0] in membres and texte not in raisons:
                raisons.append(texte)
        rendu.append((membres, raisons))
    return sorted(rendu, key=lambda g: g[0][0])


def codes_todo(rangs):
    """Le code de chaque rang de la TODO : le premier texte entre accents graves de sa cellule Chantier,
    sinon son numéro. `trier` et `plan` le lisent ici, d'un seul endroit (NUI10, NUI12)."""
    return [m.group(1) if m else r[0] for r in rangs for m in [CODE.search(r[1])]]


def trier(rangs, lettres):
    """Les lignes du tri du soir d'une TODO (`rangs` de `todo_du_fichier`, `lettres` closes) : par rang,
    `PRÊT <code>` ou `ÉCARTÉE <code> — <raison>`, `FICHIERS`, `MARQUES`, `SOIR` pour une prête à découper
    le soir ; puis un `CANAL` par groupe de prêtes liées. Une prête du même soir compte pour close — son
    code rejoint les clos, son rang quitte les présents — jusqu'à ce que plus rien ne bouge (NUI10)."""
    codes = codes_todo(rangs)
    marques = [marques_tri(r[2], r[3]) for r in rangs]
    fichiers = [fichiers_tri(r[2], r[3]) for r in rangs]
    ecartent = [MARQUES_TRI.index(MARQUE_VISUELLE), MARQUES_TRI.index(MARQUE_PUSH)]
    prets = []

    def bloque(k, ouvertes):
        presents = {r[0] for j, r in enumerate(rangs) if j not in ouvertes}
        return est_bloque(rangs[k][4], set(lettres) | {lettre_de(codes[j]) for j in ouvertes}, presents)

    while True:
        neuf = [k for k, r in enumerate(rangs) if k not in prets and not any(marques[k][i] for i in ecartent)
                and not bloque(k, prets)]
        if not neuf:
            break
        prets += neuf
    lignes = []
    for k, r in enumerate(rangs):
        if k in prets:
            lignes.append("PRÊT %s" % codes[k])
        else:
            raisons = ["marque %s" % MARQUES_TRI[i] for i in ecartent if marques[k][i]]
            if bloque(k, prets):
                raisons.append("dépendance non close : %s" % r[4])
            lignes.append("ÉCARTÉE %s — %s" % (codes[k], " · ".join(raisons)))
        if fichiers[k]:
            lignes.append("FICHIERS %s %s" % (codes[k], " · ".join(fichiers[k])))
        if sum(marques[k]):
            lignes.append("MARQUES %s %d : %s" % (codes[k], sum(marques[k]),
                                                  " · ".join("%s %d" % (m, n) for m, n in zip(MARQUES_TRI, marques[k]))))
        if k in prets:
            borne, raisons = borne_haute_cout(r[3]), []
            if borne is None:
                raisons.append("coût sans nombre de fiches")
            elif borne > GROS_FICHES:
                raisons.append("gros : jusqu'à %s fiches" % decimal_fr(borne))
            if "à cadrer" in (r[2] + "\n" + r[3]).lower():
                raisons.append("à cadrer")
            if raisons:
                lignes.append("SOIR %s — %s" % (codes[k], " · ".join(raisons)))
    for n, (membres, raisons) in enumerate(groupes_tri(rangs, codes, prets, fichiers), 1):
        lignes.append("CANAL %d : %s — %s" % (n, ", ".join(codes[k] for k in membres),
                                              " · ".join(raisons) or "inconnu → à la page"))
    lignes.append("TRI %d rangs · %d prêts · %d écartées" % (len(rangs), len(prets), len(rangs) - len(prets)))
    return lignes


def cmd_trier(a, sortie):
    """`trier <projet>` : le tri du soir ; dans Git, sur `main` seulement — ailleurs une `GARDE:`, rien trié (BRA1)."""
    if not equipe(a.projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % a.projet)
        return 1
    if git_texte(["rev-parse", "--is-inside-work-tree"], a.projet)[0] == 0:
        code, tete = git_texte(["symbolic-ref", "--short", "-q", "HEAD"], a.projet)
        branche = tete.strip() if code == 0 else "rien (détaché)"
        if branche != "main":
            sortie.write("GARDE: trier hors de main (branche %s) — le plan ne s'écrit que sur main : rien trié\n" % branche)
            return 1
    try:
        carte_ = lignes_de(os.path.join(a.projet, "CHANTIER.md"))
        etat = champ(carte_, "fichier d'état")
        if not etat:
            raise ValueError("fichier d'état introuvable : aucun")
        rangs = todo_du_fichier(lignes_du_projet(a.projet, etat, "fichier d'état"))
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("".join(l + "\n" for l in trier(rangs, lettres_prises(carte_))))
    code = lecons_nuits(a.projet, sortie)
    sortie.write("%s\n%s\n" % (taux_jour(a.projet), lignes_taux_nuit(a.projet)))
    return code


# --- plan : le plan du soir, écrit dans le fichier des nuits (chantier NUI) -----

CANAUX = ("A", "B")
PLAN_BORNE = re.compile(r"^Borne : (\S+) \$ · (\d+) chantiers$")
PLAN_CHANTIER = re.compile(r"^Canal (A|B) · rang (\d+) · code (.+) · préfixe ([A-Z]{1,3})$")


def plan_valider(plan, codes, prises):
    """`(usd, chantiers, [(canal, code, préfixe, réponses)])` du JSON d'un plan, canal A puis B, chacun dans
    son ordre ; `ValueError` au premier refus : rien ne s'écrit avant que tout soit vérifié (NUI12)."""
    if not isinstance(plan, dict):
        raise ValueError("le JSON du plan n'est pas un objet")
    inconnues = sorted(set(plan) - {"borne_usd", "borne_chantiers", *CANAUX})
    if inconnues:
        raise ValueError("clé inconnue du plan : %s — les canaux sont A et B" % ", ".join(inconnues))
    usd, borne_n = plan.get("borne_usd"), plan.get("borne_chantiers")
    if isinstance(usd, bool) or not isinstance(usd, (int, float)) or not 0 < usd < float("inf"):
        raise ValueError("borne_usd absente ou nulle : la borne double s'écrit avec le plan")
    if isinstance(borne_n, bool) or not isinstance(borne_n, int) or borne_n <= 0:
        raise ValueError("borne_chantiers absente ou nulle : la borne double s'écrit avec le plan")
    chantiers, canal_de, prefixes = [], {}, set()
    for canal in CANAUX:
        liste = plan.get(canal, [])
        if not isinstance(liste, list):
            raise ValueError("canal %s : une liste de chantiers était attendue" % canal)
        for ch in liste:
            code, prefixe = (ch.get("code"), ch.get("prefixe")) if isinstance(ch, dict) else (None, None)
            reponses = ch.get("reponses", []) if isinstance(ch, dict) else None
            if not isinstance(code, str) or not isinstance(prefixe, str) or not isinstance(reponses, list):
                raise ValueError("canal %s : un chantier est {code, prefixe, reponses}" % canal)
            if code not in codes:
                raise ValueError("code absent de la TODO : %s" % code)
            if code in canal_de:
                raise ValueError("chantier %s dans deux canaux (%s et %s)" % (code, canal_de[code], canal)
                                 if canal_de[code] != canal else "chantier %s donné deux fois" % code)
            if not PREFIXE.fullmatch(prefixe):
                raise ValueError("préfixe %s : une à trois majuscules, en entier" % prefixe)
            if prefixe in prises:
                raise ValueError("préfixe %s déjà pris" % prefixe)
            if prefixe in prefixes:
                raise ValueError("préfixe %s donné deux fois : deux canaux ouvrent chacun leur chantier sans se voir"
                                 % prefixe)
            for r in reponses:
                if not isinstance(r, str) or not r.strip() or "\n" in r or "\r" in r:
                    raise ValueError("chantier %s : une réponse tient sur une ligne, non vide" % code)
            canal_de[code] = canal
            prefixes.add(prefixe)
            chantiers.append((canal, code, prefixe, reponses))
    if not chantiers:
        raise ValueError("aucun chantier dans le plan")
    return usd, borne_n, chantiers


def plan_section(date, usd, borne_n, chantiers):
    """Les lignes de la section `## Nuit <date>` : la borne, une ligne par chantier (canal, rang, code,
    préfixe), puis un `### <code>` par chantier dont chaque réponse est une puce ; une ligne vide ferme."""
    rangs, bloc = {}, ["## Nuit %s" % date, "", "Borne : %s $ · %d chantiers" % (usd, borne_n)]
    for canal, code, prefixe, _ in chantiers:
        rangs[canal] = rangs.get(canal, 0) + 1
        bloc.append("Canal %s · rang %d · code %s · préfixe %s" % (canal, rangs[canal], code, prefixe))
    for _, code, _, reponses in chantiers:
        bloc += ["", "### %s" % code] + ["- %s" % r for r in reponses]
    return bloc + [""]


def fin_de_section(lignes, debut):
    """L'indice de fin (exclu) de la section qui s'ouvre à `lignes[debut]` : le prochain titre `## `."""
    return next((k for k in range(debut + 1, len(lignes)) if lignes[k].startswith("## ")), len(lignes))


def plan_poser(lignes, date, bloc):
    """`lignes` avec `bloc` : la section de la même date est remplacée, sinon il se pose juste avant
    `## Leçons` ; tout le reste est repris tel quel."""
    _, (ld, _) = sections_nuits(lignes)
    d = next((k for k, l in enumerate(lignes) if l == "## Nuit %s" % date), None)
    if d is None:
        return lignes[:ld] + bloc + lignes[ld:]
    return lignes[:d] + bloc + lignes[fin_de_section(lignes, d):]


def plan_ecrire(a, sortie):
    if os.environ.get("VLP_NUIT") == "1":
        raise ValueError("VLP_NUIT=1 : la nuit n'écrit aucun fichier suivi — le plan s'écrit le soir")
    if not a.json:
        raise ValueError("--json <fichier> est obligatoire pour ecrire")
    date = a.date or datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise ValueError("date %s : AAAA-MM-JJ attendu" % date) from None
    carte_ = lignes_de(os.path.join(a.projet, "CHANTIER.md"))
    etat = champ(carte_, "fichier d'état")
    if not etat:
        raise ValueError("fichier d'état introuvable : aucun")
    codes = codes_todo(todo_du_fichier(lignes_du_projet(a.projet, etat, "fichier d'état")))
    try:
        plan = json.loads(lire(a.json).lstrip("﻿"))
    except OSError as e:
        raise ValueError("--json illisible : %s" % e) from None
    usd, borne_n, chantiers = plan_valider(plan, codes, lettres_prises(carte_))
    chemin = fichier_nuits(a.projet)
    lignes = lignes_de(chemin) if chemin else list(NUITS_TETE)
    nuits_du_fichier(lignes)
    neuf = plan_poser(lignes, date, plan_section(date, usd, borne_n, chantiers))
    nuits_du_fichier(neuf)
    chemin = chemin or fichier_nuits(a.projet, creer=True)
    assert chemin
    ecrire_lignes(chemin, neuf)
    sortie.write("PLAN %s · %s · %d chantiers\n" % (os.path.relpath(chemin, a.projet).replace("\\", "/"), date,
                                                     len(chantiers)))
    return 0


def plan_lire(a, sortie):
    if not a.date:
        raise ValueError("--date est obligatoire pour lire : une nuit passe minuit")
    chemin = fichier_nuits(a.projet)
    if chemin is None:
        raise ValueError("pas de fichier des nuits — le plan s'écrit le soir (plan ecrire)")
    lignes = lignes_de(chemin)
    d = next((k for k, l in enumerate(lignes) if l == "## Nuit %s" % a.date), None)
    if d is None:
        raise ValueError("pas de plan à la date %s" % a.date)
    f = fin_de_section(lignes, d)
    borne = next((m for l in lignes[d:f] for m in [PLAN_BORNE.match(l)] if m), None)
    if borne is None:
        raise ValueError("plan du %s illisible : pas de ligne `Borne : …`" % a.date)
    liste = [m.groups() for l in lignes[d:f] for m in [PLAN_CHANTIER.match(l)] if m and a.canal in (None, m.group(1))]
    if a.chantier:
        k = next((k for k in range(d, f) if lignes[k] == "### %s" % a.chantier), None)
        if k is None or a.chantier not in [c[2] for c in liste]:
            raise ValueError("chantier %s absent du plan du %s%s" % (a.chantier, a.date,
                                                                 " (canal %s)" % a.canal if a.canal else ""))
        fin = next((j for j in range(k + 1, f) if lignes[j].startswith("#")), f)
        while fin - 1 > k and not lignes[fin - 1].strip():
            fin -= 1
        imprimer_section(sortie, "Plan %s" % a.chantier, os.path.relpath(chemin, a.projet).replace("\\", "/"),
                         lignes, (k + 1, fin))
        return 0
    sortie.write("BORNE %s $ · %s chantiers\n" % borne.groups())
    for canal, rang, code, prefixe in liste:
        sortie.write("CHANTIER %s · canal %s · rang %s · préfixe %s\n" % (code, canal, rang, prefixe))
    return 0


def cmd_plan(a, sortie):
    if not equipe(a.projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % a.projet)
        return 1
    try:
        return (plan_ecrire if a.verbe == "ecrire" else plan_lire)(a, sortie)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1


def cmd_feuille(a, sortie):
    if not equipe(a.projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % a.projet)
        return 1
    page = page_feuille(a.projet)
    if not os.path.isfile(page):
        sortie.write("GARDE: feuille de route introuvable : %s\n" % page)
        return 1
    html = lire(page)
    try:
        neuf, bilan = feuille(a.projet, html, a.todo, a.date or __import__("datetime").date.today().isoformat())
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    if a.verifier:
        sortie.write("%s · %s — %s\n" % (bilan, "identique" if neuf == html else "écart", page))
        return 0 if neuf == html else 1
    with open(page, "w", encoding="utf-8", newline="") as f:
        f.write(neuf)
    joints = recopier_joints(os.path.dirname(os.path.abspath(page)))
    sortie.write("CSS %s\n" % joints["vlp.css"])
    joints.update(ecrire_couts(page, neuf, couts_du_projet(a.projet, neuf)))
    sortie.write(ligne_files(joints, page))
    sortie.write("%s · %s — %s\n" % (bilan, "inchangée" if neuf == html else "réécrite", page))
    return 0


# --- la ZONE:clos d'une feuille de route -------------------------------------
# Lue par `clore`, qui y ajoute une ligne à chaque clôture, et par
# `niveau --ecrire`, qui pose sur une feuille d'avant le 2026-09-17 ce que le
# gabarit a depuis : le bloc repliable et l'estimation en dollars du pied — et
# convertit les lignes écrites avant `gras_et_liens`.

# Le coût brut d'une cellule : entre parenthèses (`≈1,5k (1 500)`), ou nu, fait de
# chiffres seuls, sous 1 000 (`arrondi`) — plage, date et pied n'en sont pas (chantier TAR).
BRUT = re.compile(r'<td class="mono">(?:[^<]*\((\d[\d ]*)\)|(\d+))</td>')
# `clore` écrit ses lignes à dix espaces, et les repère à dix espaces.
RANG_CLOS = re.compile(r"          <tr>\n.*?          </tr>\n", re.S)
PIED_CLOS = re.compile(r'(Total cumulé</td><td class="mono"><strong>.*?</strong></td>)<td[^>]*>([^<]*)</td>', re.S)
GABARIT_FEUILLE = "templates/artefact-feuille-de-route.html"
# Le prix mesuré en tête d'une cellule Tokens, posé par `clore` — `dollars` (chantier TAU).
PRIX_CLOS = re.compile(r'<td class="mono">(\d+,\d\d) \$ · ')


def prix_clos(corps):
    """(usd, n) : la somme des prix en tête de cellule Tokens des lignes de `corps`, et leur
    nombre ; `usd` vaut `None` si aucune n'en porte (chantier TAU)."""
    from decimal import Decimal
    prix = [Decimal(m.group(1).replace(",", ".")) for r in lignes_clos(corps) for m in [PRIX_CLOS.search(r)] if m]
    return (sum(prix) if prix else None), len(prix)


def texte_cout_clos(usd, n_usd, n):
    """`47,08 $` (toutes les lignes closes au prix mesuré), `47,08 $ sur 2 clos mesurés` (une
    partie), ou `""` (aucune) — partagé par `resommer` et `resume_clos` (chantier TAU)."""
    if usd is None:
        return ""
    return dollars(usd) if n_usd == n else "%s sur %d clos mesurés" % (dollars(usd), n_usd)


def lignes_clos(corps):
    """Les `<tr>` de chantiers clos d'un corps de table — les lignes d'exemple
    du gabarit, reconnaissables à leurs `<…>`, n'en sont pas."""
    return [r for r in RANG_CLOS.findall(corps) if '<td class="mono">&lt;' not in r]


def total_clos(corps):
    """La somme des coûts bruts — entre parenthèses, ou nus sous 1 000 — d'un corps de table."""
    return sum(int(re.sub(r"\D", "", entre or nu)) for entre, nu in BRUT.findall(corps))


# Le coût des chantiers clos en image (chantier BTN), joint à la feuille comme vlp.css. Une image
# ne lit pas les variables de la page : couleurs en dur, lisibles sur le fond crème comme sur le
# fond sombre de vlp.css ; chaque forme porte son `fill`.
COUTS_SVG = "couts.svg"
COUTS_TAILLE = (640, 160, 24)  # largeur, hauteur, bandeau du maximum en haut
COUTS_BARRE, COUTS_TEXTE = "#c47f1a", "#7d8796"
BALISE_COUTS = re.compile(r'[ \t]*<img src="couts\.svg"[^>]*>\n')
DETAILS_CLOS = re.compile(r'^([ \t]*)<details class="clos">', re.M)


def couts_clos(html):
    """[(chantier, tokens)] des lignes de `ZONE:clos` qui ont un coût brut (`BRUT`), du plus ancien
    au plus récent — la table met le plus récent en haut. Pas de zone, ou aucun coût au-dessus de 0 :
    [] — rien à dessiner, et `svg_couts` ne divise pas par un maximum nul (dette BTN)."""
    try:
        d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    except ValueError:
        return []
    couts = []
    for r in lignes_clos(html[d:f]):
        if BRUT.search(r):
            nom = re.search(r"<td>(.*?)</td>", r, re.S)
            nom = re.sub(r'<span class="badge".*?</span>', "", nom.group(1) if nom else "")
            couts.append((re.sub(r"<[^>]+>", "", nom).strip(), total_clos(r)))
    return couts[::-1] if any(t for _, t in couts) else []


def svg_couts(html, couts=None):
    """Le SVG du coût des chantiers clos (`couts_clos`, ou `couts` donnés), ou None sans aucun coût :
    une barre par chantier, du plus ancien à gauche au plus récent à droite, hauteur proportionnelle
    aux tokens, la plus haute pleine hauteur ; en haut à gauche, le maximum (`arrondi`) suivi de
    « tokens »."""
    couts = couts_clos(html) if couts is None else couts
    if not couts:
        return None
    largeur, hauteur, bandeau = COUTS_TAILLE
    haut = max(t for _, t in couts)
    pas = largeur / len(couts)
    barres = "".join('<rect class="barre" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                     % (i * pas + pas * .1, hauteur - h, pas * .8, h, COUTS_BARRE)
                     for i, h in enumerate((hauteur - bandeau) * t / haut for _, t in couts))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">'
            '<text x="0" y="16" font-family="system-ui,sans-serif" font-size="14" fill="%s">%s tokens</text>'
            '%s<rect x="0" y="%d" width="%d" height="1" fill="%s"/></svg>\n'
            % (largeur, hauteur, COUTS_TEXTE, arrondi(haut), barres, hauteur - 1, largeur, COUTS_TEXTE))


def donnees_couts(couts):
    """`data-couts` de la balise : le JSON `{"couleur", "barres": [[chantier, tokens, arrondi]]}`
    que `vlp.js` donne à Chart.js — la couleur et l'arrondi restent ici —, échappé pour un attribut."""
    brut = json.dumps({"couleur": COUTS_BARRE,
                       "barres": [[html.unescape(n), t, arrondi(t)] for n, t in couts]}, ensure_ascii=False)
    return brut.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def balise_couts(html, couts=None):
    """La balise `<img src="couts.svg">` de `#clos`, juste avant `details.clos` : posée une fois
    (une feuille d'avant la reçoit), son `alt` refait — nombre de barres, chantier le plus cher —
    et ses barres dans `data-couts` (`donnees_couts`) ; retirée sans aucun coût, ou sans
    `details.clos`. `couts` : les barres, lues ailleurs (`couts_du_projet`, chantier ARC)."""
    sans = BALISE_COUTS.sub("", html)
    couts, m = couts_clos(sans) if couts is None else couts, DETAILS_CLOS.search(sans)
    if not couts or not m:
        return sans
    nom = max(couts, key=lambda c: c[1])[0]
    alt = ("Coût des chantiers clos en tokens : %d barres, du plus ancien au plus récent ; le plus cher : %s"
           % (len(couts), nom)).replace('"', "&quot;")
    return sans[:m.start()] + '%s<img src="%s" alt="%s" data-couts="%s">\n' % (
        m.group(1), COUTS_SVG, alt, donnees_couts(couts)) + sans[m.start():]


def ecrire_couts(page, html, couts=None):
    """Écrit `couts.svg` à côté de la feuille `page` si `html` porte sa balise (`balise_couts`), le
    retire sinon. Rend `{"couts.svg": chemin}`, à joindre à la ligne `FILES`, ou {}."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(page)), COUTS_SVG)
    svg = svg_couts(html, couts) if BALISE_COUTS.search(html) else None
    if svg is None:
        if os.path.isfile(chemin):
            os.remove(chemin)
        return {}
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(svg)
    return {COUTS_SVG: chemin}


PLAGE_CLOS = re.compile(r'<td class="mono">([A-Z]{1,3})[0-9]+(?:–[A-Z]{1,3}[0-9]+)?</td>')
PLAGE_INDEX = re.compile(r"^\|\s*`([^`]+)`\s*\|.*`([A-Z]{1,3})[0-9]+\.\.[A-Z]{1,3}[0-9]+`")


def signe(n):
    return ("-" if n < 0 else "+") + milliers(abs(n))


def recompte(chemin):
    """(recompté ou None, méthode, essais, usd) d'un fichier de fiches clos : le nombre de la ligne `TOTAL` de
    `cout`, ou None et la raison de le garder — sans session, transcription absente, `DÉCOUPE
    aucune`, découpe à zéro (chantier REC). `essais` : les tokens de ses essais, ceux de la découpe
    ou, sans découpe, des sessions entières (`essais_entiers`) — pour `--essais` (chantier ESD).
    `usd` : le prix de la ligne `TOTAL`, None sans découpe — pour `--clos` (PRP3)."""
    lignes = lignes_de(chemin)
    ids = sessions_de(lignes)
    if not ids:
        return None, "gardé — sans session", 0, None
    for s in ids:
        if mesure().resoudre(s)[1]:
            return None, "gardé — transcription absente (%s)" % s, 0, None
    decoupe, pourquoi, gardes = decouper(chemin, lignes)
    if not decoupe:
        gardes = []
        essais = essais_entiers(ids, gardes)[0]
        manque = " · %d transcript(s) d'essai non mesuré(s)" % len(gardes) if gardes else ""
        return None, "gardé — DÉCOUPE aucune (%s)%s" % (pourquoi[0], manque), essais, None
    if any(g.startswith("GARDE: découpe à zéro") for g in gardes):
        return None, "gardé — découpe à zéro", 0, None
    total = plus(*totaux(decoupe))
    return total[0], "découpe", totaux(decoupe)[2][0], total[2]


# La cellule de coût d'une ligne close, seule sur sa ligne (`clore`), et les marques de
# `recompter --ecrire` : en tête, jamais après le brut, que `BRUT` ne lit qu'en fin de cellule.
CELLULE_CLOS = re.compile(r'(\n            <td class="mono">)([^<\n]*)(</td>\n)')
MARQUE_REC = "recompté (REC), était "
MARQUE_GARDE = "non recompté — "
MARQUE_ESSAIS = "essais (ESD) "


def marquer(cellule, brut, recompte_, methode):
    """La cellule de coût après `--ecrire` : le recompté au format de `clore` et l'ancien chiffre,
    ou le chiffre gardé et sa raison — la même cellule si rien n'est à marquer."""
    entre = lambda v: v if "(" in v or not v.isdigit() else "(%s)" % v   # un nu sous 1 000 reste lu
    if recompte_ is None:
        if MARQUE_GARDE in cellule:
            return cellule
        return "%s%s · %s" % (MARQUE_GARDE, esc(methode.replace("gardé — ", "", 1)), entre(cellule))
    if recompte_ == brut:
        return cellule
    esd = cellule.split(" · ")[0] + " · " if cellule.startswith(MARQUE_ESSAIS) else ""   # gardée en tête
    reste = cellule[len(esd):]
    marque = reste.split(" · ")[0] if reste.startswith(MARQUE_REC) else MARQUE_REC + milliers(brut)
    return "%s%s · %s" % (esd, marque, entre(arrondi(recompte_)))


def ajout_essais(cellule, brut, recompte_, methode, essais):
    """Ce que `recompter --essais` ajoute à une cellule close (chantier ESD) : rien si elle porte
    déjà la marque ; un gardé `DÉCOUPE aucune`, ses essais ; un découpé, ses essais sans passer
    le recompté ; tout autre gardé, rien. Seul endroit de la règle : l'affichage et l'écriture."""
    if MARQUE_ESSAIS in cellule:
        return 0
    if methode.startswith("gardé — DÉCOUPE aucune"):
        return essais
    if methode == "découpe":
        return max(0, min(essais, recompte_ - brut))
    return 0


def marquer_essais(cellule, brut, ajout):
    """La cellule après `recompter --essais --ecrire` : la marque et l'ajout en tête, la cellule
    d'avant sans son chiffre, puis le chiffre + l'ajout en fin, où `BRUT` le lit."""
    if not ajout:
        return cellule
    tete = cellule.rsplit(" · ", 1)[0] + " · " if " · " in cellule else ""
    n = arrondi(brut + ajout)
    return "%s%s · %s%s" % (MARQUE_ESSAIS, signe(ajout), tete, n if "(" in n else "(%s)" % n)


def clos_du_projet(projet, sortie):
    """Les chantiers clos d'un projet : `(feuille, début, fin de ZONE:clos, rangs)`, chaque rang
    `(ligne, préfixe, coût inscrit, fichier de fiches ou None)` — le fichier, que l'index (et son
    archive) nomme au même préfixe. None après une `GARDE:` (`recompter`, `repeindre`)."""
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return None
    page = page_clos(projet)
    if not os.path.isfile(page):
        sortie.write("GARDE: feuille de route introuvable : %s\n" % page)
        return None
    html = lire(page)
    try:
        d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return None
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    contexte = champ(carte_, "contexte", "context AI/")
    index = champ(carte_, "index", os.path.join(contexte, "00-INDEX.md"))
    fichiers = {}
    for l in lignes_index(projet, index):
        m = PLAGE_INDEX.match(l)
        if m:
            fichiers.setdefault(m.group(2), os.path.join(projet, contexte, m.group(1)))
    rangs = []
    for r in lignes_clos(html[d:f]):
        m = PLAGE_CLOS.search(r)
        if m:
            chemin = fichiers.get(m.group(1))
            rangs.append((r, m.group(1), total_clos(r), chemin if chemin and os.path.isfile(chemin) else None))
    return html, d, f, rangs


def cmd_repeindre(projet, sortie, a_blanc=False):
    """Chaque page de chantier clos qui ne lie pas encore `vlp.css` passe par `page --forme`
    puis par `vigile`, dans une copie : refusée, l'originale ne bouge pas (chantier HAB)."""
    import shutil
    import tempfile
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    vues, n = set(), {"repeintes": 0, "avec lien": 0, "sans lien": 0, "refusées": 0, "déjà": 0, "sans page": 0}
    for _, prefixe, _, chemin in parcours[3]:
        page = page_du_fichier(chemin) if chemin else None
        if page in vues:
            continue
        vues.add(page)
        if not chemin or not page or not os.path.isfile(page):
            n["sans page"] += 1
            sortie.write("SANS PAGE %s · %s\n" % (prefixe, page or "fichier de fiches introuvable"))
            continue
        if 'href="vlp.css"' in lire(page):
            n["déjà"] += 1
            continue
        with tempfile.TemporaryDirectory() as tmp:
            copie = os.path.join(tmp, os.path.basename(page))
            shutil.copyfile(page, copie)
            if os.path.isfile(chemin_abri(page)):
                shutil.copyfile(chemin_abri(page), chemin_abri(copie))
            rendu = io.StringIO()
            code = main(["page", chemin, copie, "--forme"], rendu)
            if code == 0:
                rendu = io.StringIO()
                code = main(["vigile", copie], rendu)
            if code != 0:
                n["refusées"] += 1
                gardes = [l for l in rendu.getvalue().splitlines() if l.startswith("GARDE:")]
                sortie.write("".join("%s · %s\n" % (g, page) for g in gardes) or "GARDE: refusée · %s\n" % page)
                continue
            if not a_blanc:
                shutil.copyfile(copie, page)
                shutil.copyfile(chemin_abri(copie), chemin_abri(page))
                recopier_joints(os.path.dirname(os.path.abspath(page)))
            lien = lire_abri(chemin_abri(copie)).get("lien")
        n["repeintes"] += 1
        n["avec lien" if lien else "sans lien"] += 1
        sortie.write("REPEINTE %s · %s\n" % (page, "lien %s" % lien if lien else "sans lien"))
    sortie.write("REPEINDRE %s%s\n" % (" · ".join("%d %s" % (v, k) for k, v in n.items()),
                                        " · à blanc, rien d'écrit" if a_blanc else ""))
    return 0


def poser_lien(page, url):
    """Écrit `url` dans la section `## Lien` du `.md` de `page` (créé depuis la page s'il manque) ;
    rend "écrit" ou "déjà" (chantier HAB)."""
    md = chemin_abri(page)
    parts = lire_abri(md) if os.path.exists(md) else abri_de_page(lire(page))
    if parts.get("lien") == url and os.path.exists(md):
        return "déjà"
    parts["lien"] = url
    ecrire_abri(md, parts)
    return "écrit"


def cmd_lien(page, url, sortie):
    if not os.path.isfile(page):
        sortie.write("GARDE: page introuvable : %s\n" % page)
        return 1
    if not re.match(r"https://claude\.ai/\S+$", url):
        sortie.write("GARDE: lien inattendu : %s — une URL https://claude.ai/…\n" % url)
        return 1
    sortie.write("LIEN %s · %s · %s\n" % (poser_lien(page, url), chemin_abri(page), url))
    return 0


def cmd_liens(projet, sortie):
    """Le lien de chaque ligne de `ZONE:clos` posé dans le `.md` de sa page (parcours de
    `recompter`). Deux lignes, deux liens pour une page : rien d'écrit, `DOUBLON`."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    par_page, n = {}, {"écrits": 0, "déjà": 0, "doublons": 0, "sans lien": 0, "sans page": 0}
    for r, prefixe, _, chemin in parcours[3]:
        page = page_du_fichier(chemin) if chemin else None
        if not page or not os.path.isfile(page):
            n["sans page"] += 1
            continue
        m = re.search(r'<a href="(https://claude\.ai/[^"]+)"', r)
        if not m:
            n["sans lien"] += 1
            sortie.write("SANS LIEN %s · %s\n" % (prefixe, page))
            continue
        par_page.setdefault(page, set()).add(m.group(1))
    for page, urls in par_page.items():
        if len(urls) > 1:
            n["doublons"] += 1
            sortie.write("DOUBLON %s · %s\n" % (page, " · ".join(sorted(urls))))
            continue
        fait = poser_lien(page, urls.pop())
        n["écrits" if fait == "écrit" else "déjà"] += 1
    sortie.write("LIENS %s\n" % " · ".join("%d %s" % (v, k) for k, v in n.items()))
    return 0


def cmd_recompter(projet, sortie, ecrire=False, essais=False, a_clore=False):
    """Chaque ligne de `ZONE:clos` recomptée par `cout` sur son fichier de fiches, que l'index
    nomme au même préfixe ; n'écrit rien sans `ecrire` (chantier REC). Avec `--essais`,
    n'ajoute que la part essais (chantier ESD). `a_clore` : chaque ligne recomptée finit par
    `à clore` et `après clore` (`totaux_a_clore`), ou `sans appel clore` (chantier APC)."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    rangs = parcours[3]
    porteurs = {}
    for _, prefixe, _, chemin in rangs:
        for s in sessions_de(lignes_de(chemin)) if chemin else []:
            porteurs.setdefault(s, set()).add(prefixe)
    n = inscrit = ecart = recoivent = ajoute = 0
    neufs = {}      # chaque ligne et sa réécriture, toutes calculées avant d'écrire
    for r, prefixe, brut, chemin in rangs:
        recompte_, methode, part, _ = recompte(chemin) if chemin else (None, "gardé — fichier introuvable", 0, None)
        autres = sorted({p for s in (sessions_de(lignes_de(chemin)) if chemin else [])
                         for p in porteurs[s]} - {prefixe})
        partage = " · partagée avec %s" % ", ".join(autres) if autres else ""
        if essais:
            c = CELLULE_CLOS.search(r)
            a = ajout_essais(c.group(2), brut, recompte_, methode, part) if c else 0
            inscrit, recoivent, ajoute = inscrit + brut, recoivent + (a > 0), ajoute + a
            sortie.write("%s inscrit %s · essais %s · ajout %s · %s%s%s\n" % (
                prefixe, milliers(brut), milliers(part), signe(a), methode, partage,
                " · déjà ajoutés (ESD)" if c and MARQUE_ESSAIS in c.group(2) else ""))
            neufs[r] = CELLULE_CLOS.sub(lambda c: c.group(1) + marquer_essais(c.group(2), brut, a)
                                        + c.group(3), r, count=1)
            continue
        e = 0 if recompte_ is None else recompte_ - brut
        n, inscrit, ecart = n + (recompte_ is not None), inscrit + brut, ecart + e
        clore_ = ""
        if a_clore and recompte_ is not None:
            avant = totaux_a_clore(chemin, lignes_de(chemin))
            clore_ = " · sans appel clore" if avant is None else " · à clore %s · après clore %s" % (
                milliers(plus(*avant)[0]), milliers(recompte_ - plus(*avant)[0]))
        sortie.write("%s inscrit %s · recompté %s · écart %s · %s%s%s\n" % (
            prefixe, milliers(brut), "gardé" if recompte_ is None else milliers(recompte_), signe(e), methode,
            partage, clore_))
        neufs[r] = CELLULE_CLOS.sub(lambda c: c.group(1) + marquer(c.group(2), brut, recompte_, methode)
                                    + c.group(3), r, count=1)
    if essais:
        sortie.write("ESSAIS %d clos · %d reçoivent · inscrit %s · avec essais %s · ajout %s\n" % (
            len(rangs), recoivent, milliers(inscrit), milliers(inscrit + ajoute), signe(ajoute)))
    else:
        sortie.write("RECOMPTE %d clos · %d recomptés · %d gardés · inscrit %s · recompté %s · écart %s\n" % (
            len(rangs), n, len(rangs) - n, milliers(inscrit), milliers(inscrit + ecart), signe(ecart)))
    if ecrire:
        ecrire_clos(projet, parcours, neufs, sortie)
    return 0


def ecrire_clos(projet, parcours, neufs, sortie):
    """`ZONE:clos` avec chaque ligne de `neufs` remplacée, pied et résumé resommés, `couts.svg`
    refait — la fin de `recompter --ecrire`, `--clos` compris (PRP3)."""
    html, d, f, rangs = parcours
    page = page_clos(projet)
    corps = html[d:f]
    neuf_corps = RANG_CLOS.sub(lambda m: neufs.get(m.group(0), m.group(0)), corps)
    avant, apres = total_clos(corps), total_clos(neuf_corps)
    usd, n_usd = prix_clos(neuf_corps)
    neuf = resommer(html[:d] + neuf_corps + html[f:], len(lignes_clos(neuf_corps)), apres, usd, n_usd)
    neuf = balise_couts(neuf) if page == page_feuille(projet) else neuf
    if neuf != html:
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(neuf)
    rafraichir_couts(projet, page, neuf)
    sortie.write("ÉCRIT %d cellules · total %s → %s\n" % (
        sum(neufs.get(r, r) != r for r, _, _, _ in rangs), milliers(avant), milliers(apres)))


def cmd_recompter_clos(projet, sortie, ecrire, clos):
    """`recompter --clos` : le seul clos `clos` recompté ; avec `ecrire`, ses quatre copies du coût —
    la cellule d'archive (`ecrire_clos`), puis `ecrire_copies` (PRP3)."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    rang = next((rg for rg in parcours[3] if rg[1] == clos), None)
    if rang is None:
        sortie.write("GARDE: clos %s absent de ZONE:clos — rien d'écrit\n" % clos)
        return 1
    r, _, brut, chemin = rang
    recompte_, methode, _, usd = recompte(chemin) if chemin else (None, "gardé — fichier introuvable", 0, None)
    sortie.write("%s inscrit %s · recompté %s · écart %s · %s\n" % (
        clos, milliers(brut), "gardé" if recompte_ is None else milliers(recompte_),
        signe(0 if recompte_ is None else recompte_ - brut), methode))
    if not ecrire:
        return 0
    neuf = CELLULE_CLOS.sub(lambda c: c.group(1) + marquer_prix(c.group(2), brut, recompte_, methode, usd)
                            + c.group(3), r, count=1)
    ecrire_clos(projet, parcours, {r: neuf}, sortie)
    ecrire_copies(chemin, usd, neuf != r, sortie)
    return 0


def marquer_prix(cellule, brut, recompte_, methode, usd):
    """`marquer` pour `--clos` : le prix d'en tête (`PRIX_CLOS`) mis à part, puis reposé — le
    recompté s'il est connu, sinon l'ancien (PRP3)."""
    m = re.match(r'(\d+,\d\d \$) · ', cellule)
    prix = dollars(usd) if usd is not None else (m.group(1) if m else None)
    marque = marquer(cellule[m.end():] if m else cellule, brut, recompte_, methode)
    return "%s · %s" % (prix, marque) if prix else marque


def copie_fait(chemin, usd):
    """La ligne `**Fait.**` de `chemin` recalée sur `usd` : écrite ou non ; ValueError sans ligne
    à joué (PRP3)."""
    lignes = lignes_de(chemin)
    k = next((k for k, l in enumerate(lignes) if l.startswith("**Fait.**") and JOUE_PRIX.search(l)), None)
    if k is None:
        raise ValueError("ligne **Fait.** avec un joué absente de %s" % chemin)
    vieille, lignes[k] = lignes[k], recaler_texte(lignes[k], usd, tout=True)[0]
    if lignes[k] != vieille:
        ecrire_par_tmp([(chemin, "\n".join(lignes) + "\n")])
    return lignes[k] != vieille


def copie_bilan(page, usd):
    """La `ZONE:bilan` de `page` recalée sur `usd` : écrite ou non ; ValueError sans page, sans zone
    ou sans joué dedans (PRP3)."""
    if not os.path.isfile(page):
        raise ValueError("page introuvable : %s" % page)
    pg = lire(page)
    d, f = zone(pg, "bilan", "\n", "  </section>")
    if not JOUE_PRIX.search(pg[d:f]):
        raise ValueError("ZONE:bilan sans joué : %s" % page)
    neuf = pg[:d] + recaler_texte(pg[d:f], usd, tout=True)[0] + pg[f:]
    if neuf != pg:
        ecrire_par_tmp([(page, neuf)])
    return neuf != pg


def copie_abri(md, usd):
    """Le bilan du `.md` d'abri `md` recalé sur `usd` (`ecrire_abri`) : écrit ou non ; ValueError sans
    `.md` ou sans joué au bilan (PRP3)."""
    parts = lire_abri(md) if os.path.isfile(md) else None
    if parts is None or not any(JOUE_PRIX.search(b) for b in parts["bilan"]):
        raise ValueError(".md d'abri sans joué au bilan : %s" % md)
    bilan = [recaler_texte(b, usd, tout=True)[0] for b in parts["bilan"]]
    if bilan != parts["bilan"]:
        ecrire_abri(md, dict(parts, bilan=bilan))
    return bilan != parts["bilan"]


def ecrire_copies(chemin, usd, archive, sortie):
    """Les trois autres copies du coût d'un clos recalées sur `usd` : `copie_fait`, `copie_bilan`,
    `copie_abri`. Une copie introuvable : `GARDE:`, les autres s'écrivent quand même. Puis
    `COPIES <n> écrites · <n> inchangées · <n> introuvables`, l'archive (`archive`, déjà écrite)
    comprise (PRP3)."""
    n = {"écrites": int(archive), "inchangées": int(not archive), "introuvables": 0}
    page = page_du_fichier(chemin) if chemin else ""
    for copie, cible in ((copie_fait, chemin), (copie_bilan, page), (copie_abri, chemin_abri(page) if page else "")):
        try:
            if usd is None or not cible:
                raise ValueError("prix non recompté")
            n["écrites" if copie(cible, usd) else "inchangées"] += 1
        except ValueError as e:
            n["introuvables"] += 1
            sortie.write("GARDE: %s — %s ; les autres copies s'écrivent\n" % (copie.__name__, e))
    sortie.write("COPIES %d écrites · %d inchangées · %d introuvables\n" % tuple(n.values()))


def poser_prix(cellule, prix):
    """La cellule de coût close avec le prix mesuré en tête — la même cellule s'il y est déjà
    (chantier TAU, `prix`)."""
    if re.match(r'\d+,\d\d \$ · ', cellule):
        return cellule
    return "%s · %s" % (dollars(prix), cellule)


# Le vieux joué à la louche (avec `≈`) et le vieil estimé non encore marqué — `prix` (chantier TAU).
JOUE_LOUCHE = re.compile(r'joué (\d+) fiches ≈[\d,]+ \$')
# Tout joué, mesuré, à la louche ou inconnu — `recompter --clos` (PRP3).
JOUE_PRIX = re.compile(r'joué (\d+) fiches (?:≈?[\d,]+|\?) \$')
ESTIME_NON_MARQUE = re.compile(r'(estimé \S+ fiches ≈[\d,]+ \$)(?! \(taux plat\))')


def recaler_texte(texte, prix, tout=False):
    """`texte` (`**Fait.**`, page ou `.md` d'abri) avec le joué à la louche recalé sur `prix` (le
    pondéré mesuré de sa page, `dollars`) et le vieil estimé marqué `(taux plat)` s'il ne l'est
    pas déjà — (nouveau texte, un joué a été recalé, un estimé a été marqué) ; inchangé et deux
    `False` si rien à faire (chantier TAU, `prix`). `tout` : tout joué recalé, mesuré compris
    (`JOUE_PRIX`, `recompter --clos`)."""
    neuf, n1 = (JOUE_PRIX if tout else JOUE_LOUCHE).subn(
        lambda m: "joué %s fiches %s" % (m.group(1), dollars(prix)), texte)
    neuf, n2 = ESTIME_NON_MARQUE.subn(lambda m: m.group(1) + " (taux plat)", neuf)
    return neuf, bool(n1), bool(n2)


def cmd_prix(projet, sortie, a_blanc=False):
    """Pose le prix mesuré — le `$` du `cout-total` de sa page — en tête de la cellule Tokens de
    chaque ligne de `ZONE:clos` qui ne l'a pas encore (parcours de `recompter`), recale son
    ancien `joué … ≈X $` sur ce prix et marque son vieil estimé `(taux plat)`, dans le fichier de
    fiches, la page et son `.md` d'abri. Une page sans `$` : rien d'écrit, comptée « sans prix ».
    Le résumé replié et le pied « Total cumulé » de la feuille (`resommer`) sont rafraîchis sur
    l'état final des cellules, posées ou déjà là — sinon ils restent à l'ancien total, à la louche
    (dette trouvée en clôture de TAU4). Relancé, plus rien à écrire (chantier TAU)."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    from decimal import Decimal
    html, d, f, rangs = parcours
    n = {"posés": 0, "déjà": 0, "sans prix": 0, "joués recalés": 0, "estimés marqués": 0}
    neufs, ecrits = {}, []
    for r, prefixe, brut, chemin in rangs:
        page = page_du_fichier(chemin) if chemin else None
        pg = lire(page) if page and os.path.isfile(page) else None
        m = re.search(r'<p class="mono cout-total">.*?(\d+,\d\d) \$</p>', pg) if pg else None
        if not m:
            n["sans prix"] += 1
            continue
        assert page is not None    # m ne matche que si `pg` (donc `page`) n'est pas None
        prix = Decimal(m.group(1).replace(",", "."))
        cellule = CELLULE_CLOS.search(r)
        if cellule and re.match(r'\d+,\d\d \$ · ', cellule.group(2)):
            n["déjà"] += 1
        elif cellule:
            neufs[r] = CELLULE_CLOS.sub(lambda c: c.group(1) + poser_prix(c.group(2), prix) + c.group(3), r, count=1)
            n["posés"] += 1
        texte = "\n".join(lignes_de(chemin))
        neuf_texte, joue_r, estime_m = recaler_texte(texte, prix)
        n["joués recalés"] += joue_r
        n["estimés marqués"] += estime_m
        if neuf_texte != texte:
            if not a_blanc:
                with open(chemin, "w", encoding="utf-8", newline="") as fh:
                    fh.write(neuf_texte + "\n")
            ecrits.append(chemin)
        pg_neuf = recaler_texte(pg, prix)[0]
        if pg_neuf != pg:
            if not a_blanc:
                with open(page, "w", encoding="utf-8", newline="") as fh:
                    fh.write(pg_neuf)
            ecrits.append(page)
        md_page = chemin_abri(page)
        if os.path.isfile(md_page):
            md_texte = lire(md_page)
            md_neuf = recaler_texte(md_texte, prix)[0]
            if md_neuf != md_texte:
                if not a_blanc:
                    with open(md_page, "w", encoding="utf-8", newline="") as fh:
                        fh.write(md_neuf)
                ecrits.append(md_page)
    corps = html[d:f]
    neuf_corps = RANG_CLOS.sub(lambda m: neufs.get(m.group(0), m.group(0)), corps)
    neuf_html = html[:d] + neuf_corps + html[f:]
    total = total_clos(neuf_corps)
    usd, n_usd = prix_clos(neuf_corps)
    neuf_html = resommer(neuf_html, len(lignes_clos(neuf_corps)), total, usd, n_usd)
    if neuf_html != html:
        page_route = page_clos(projet)
        if not a_blanc:
            with open(page_route, "w", encoding="utf-8", newline="") as fh:
                fh.write(neuf_html)
            if page_route != page_feuille(projet):
                rafraichir_couts(projet, page_route, neuf_html)   # le résumé du bloc d'archive (ARC)
        ecrits.append(page_route)
    if not a_blanc:
        for chemin_ecrit in ecrits:
            sortie.write("ÉCRIT %s\n" % chemin_ecrit)
    sortie.write("PRIX %d posés · %d déjà · %d sans prix · %d joués recalés · %d estimés marqués%s\n" % (
        n["posés"], n["déjà"], n["sans prix"], n["joués recalés"], n["estimés marqués"],
        " · à blanc, rien d'écrit" if a_blanc else ""))
    return 0


def resume_clos(n, total, usd=None, n_usd=0):
    """Ce que le bloc repliable montre sans être déplié — le prix mesuré des `n_usd` lignes qui
    en portent un, sur `n` (chantier TAU)."""
    if not n:
        return "aucun chantier clos"
    if not total:  # aucun des clos ne porte de coût mesuré : pas de 0 $ inventé.
        return "%d chantiers clos · coût non mesuré" % n
    return "%d chantiers clos · %s tokens · %s" % (n, arrondi(total), texte_cout_clos(usd, n_usd, n) or "coût non mesuré")


def resommer(html, n, total, usd=None, n_usd=0):
    """Le pied « Total cumulé » et le résumé du bloc repliable d'une feuille, pour `n` clos qui
    coûtent `total` tokens, dont `n_usd` au prix mesuré `usd` — écrits par `clore` et
    `recompter --ecrire` (chantier TAU ; plus la louche à tant par million)."""
    cout = texte_cout_clos(usd, n_usd, n)
    html = re.sub(r"(Total cumulé</td><td class=\"mono\"><strong>).*?(</strong></td><td[^>]*>).*?(</td>)",
                  lambda m: m.group(1) + arrondi(total) + m.group(2) + cout + m.group(3),
                  html, count=1)
    return re.sub(r"(<span class=\"resume-clos\">).*?(</span>)",
                  lambda m: m.group(1) + resume_clos(n, total, usd, n_usd) + m.group(2), html, count=1)


def migrer_feuille(html):
    """Une feuille de route d'avant le 2026-09-17 n'a ni bloc repliable ni
    cellule d'estimation au pied de la table des clos : poser le `<details class="clos">`
    manquant, sans toucher à l'indentation des lignes de `ZONE:clos`. Rend le HTML — le
    même s'il l'a déjà. Aucune règle CSS à poser ici (chantier PLI) : `migrer_style`,
    dans `regenerer`/`feuille`, remplace tout `<style>` par le `<link>` vers `vlp.css`,
    qui les porte déjà."""
    i = html.find("<!-- ZONE:clos")
    if i < 0:
        return html
    fin = html.find("  </section>", i)
    debut = html.find('    <div class="tableau">', i)
    if not 0 <= debut < fin:
        return html
    corps = html[debut:fin]
    total = total_clos(corps)
    usd, n_usd = prix_clos(corps)
    n_rows = len(lignes_clos(corps))
    # Une cellule qui porte déjà des dollars est celle que `clore` entretient.
    corps = PIED_CLOS.sub(lambda m: m.group(0) if "$" in m.group(2)
                          else m.group(1) + '<td class="mono">%s</td>' % texte_cout_clos(usd, n_usd, n_rows),
                          corps, count=1)
    if '<details class="clos">' not in html[i:fin]:
        corps = ('    <details class="clos">\n      <summary><span class="resume-clos">%s</span>'
                 '</summary>\n' % resume_clos(n_rows, total, usd, n_usd)) + corps + "    </details>\n"
    return html[:debut] + corps + html[fin:]


CHEVRONS_HREF = re.compile(r'href="&lt;([^"]*)&gt;"')


def migrer_clos(html):
    """(HTML, n) : les lignes de `ZONE:clos` écrites avant `gras_et_liens` y
    passent, et un `href="&lt;URL&gt;"` redevient `href="URL"` ; n lignes changées.
    Les dix espaces restent, la ligne d'exemple du gabarit aussi. Deux passes = une. Sans
    ZONE:clos (partie dans l'archive, chantier ARC) : rien à migrer."""
    if "<!-- ZONE:clos" not in html:
        return html, 0
    d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    n = 0

    def rang(m):
        nonlocal n
        avant = m.group(0)
        if not lignes_clos(avant):  # la ligne d'exemple du gabarit
            return avant
        apres = CHEVRONS_HREF.sub(r'href="\1"', gras_et_liens(avant))
        n += apres != avant
        return apres
    corps = RANG_CLOS.sub(rang, html[d:f])
    return html[:d] + corps + html[f:], n


# --- comparer -----------------------------------------------------------------

BLOC = {"tr", "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section"}


class Extracteur(html.parser.HTMLParser):
    """Le texte visible d'une page, par ligne de tableau (`tr`) ou par bloc
    (`p`, `div`, `li`, un titre, `section`) — coupé à chaque frontière de
    bloc, imbriqué ou non : une page enveloppée dans un `div` ne fait pas un
    seul bloc. `convert_charrefs` décode les entités."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hors_texte = 0
        self.pile = []
        self.tampon = []
        self.blocs = []

    def couper(self):
        texte = " ".join("".join(self.tampon).split())
        if texte:
            self.blocs.append(texte)
        self.tampon = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hors_texte += 1
        elif not self.hors_texte and tag in BLOC:
            self.couper()
            self.pile.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hors_texte = max(0, self.hors_texte - 1)
        elif not self.hors_texte and tag in BLOC and tag in self.pile:
            while self.pile[-1] != tag:
                self.pile.pop()
            self.pile.pop()
            self.couper()

    def handle_data(self, data):
        if not self.hors_texte and self.pile:
            self.tampon.append(data)


def textes_visibles(html_):
    """Les blocs de texte visible d'une page, dans leur ordre d'apparition."""
    ex = Extracteur()
    ex.feed(html_)
    return ex.blocs


COMMENTAIRE = re.compile(r"<!--.*?(?:-->|\Z)", re.S)
BALISE_STYLE = re.compile(r"<style\b", re.I)
LIEN_CSS = re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']?stylesheet\b", re.I)


def defauts_page(html_):
    """Les défauts qui interdisent de publier une page (chantier VID) : un commentaire
    ouvert sans `-->` après lui, aucun style hors commentaire (ni `style`, ni `link`
    `rel="stylesheet"`), aucun bloc de texte visible. Liste vide : la page est saine."""
    defauts = []
    i = html_.find("<!--")
    while i >= 0:
        j = html_.find("-->", i + 4)
        if j < 0:
            defauts.append("commentaire ouvert ligne %d (<!-- sans --> après lui)" % (html_.count("\n", 0, i) + 1))
            break
        i = html_.find("<!--", j + 3)
    hors_commentaires = COMMENTAIRE.sub("", html_)
    if not BALISE_STYLE.search(hors_commentaires) and not LIEN_CSS.search(hors_commentaires):
        defauts.append('aucun style (ni balise style, ni link rel="stylesheet")')
    if not textes_visibles(html_):
        defauts.append("aucun bloc de texte visible")
    return defauts


def cmd_vigile(chemin, sortie):
    """Le repli à la main : une ligne `GARDE:` par défaut (sort 1), ou `PAGE SAINE <n> blocs`."""
    if not os.path.isfile(chemin):
        sortie.write("GARDE: introuvable %s\n" % chemin)
        return 1
    html_ = lire(chemin)
    defauts = defauts_page(html_)
    for d in defauts:
        sortie.write("GARDE: %s — %s\n" % (chemin, d))
    if defauts:
        return 1
    sortie.write("PAGE SAINE %d blocs\n" % len(textes_visibles(html_)))
    return 0


def cmd_vigile_hook(entree, sortie):
    """Le hook `PreToolUse` sur `Artifact` : une page `.html` cassée est refusée (`deny`, la
    raison nomme le fichier et chaque défaut). Muet sur tout le reste, entrée illisible,
    `.md`, `asset` vrai ou fichier illisible compris : il ne bloque jamais ce qu'il ne lit pas."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    if not isinstance(d, dict) or d.get("hook_event_name") != "PreToolUse" or d.get("tool_name") != "Artifact":
        return 0
    outil = d.get("tool_input")
    if not isinstance(outil, dict) or outil.get("asset") is True:
        return 0
    chemin = outil.get("file_path")
    if not isinstance(chemin, str) or not chemin.lower().endswith(".html"):
        return 0
    cwd = d.get("cwd")
    if not os.path.isabs(chemin) and isinstance(cwd, str):
        chemin = os.path.join(cwd, chemin)
    try:
        defauts = defauts_page(lire(chemin))
    except OSError:
        return 0
    if defauts:
        sortie.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Page cassée, publication refusée (vlp.py vigile) — %s : %s. "
                                        "Corrige la page, puis republie." % (chemin, " ; ".join(defauts))}},
            ensure_ascii=False) + "\n")
    return 0


# --- chef page : la page à cartes, remplie par script (chantier NUI, fiche NUI17) ---------------

GABARIT_CHOIX = "templates/rapport-choix.html"
TETE_CHOIX = re.compile(r"<link\b[^>]*>|<style\b.*?</style>", re.S | re.I)
CLASSE_JAUGE = ("", "", " moyen", " ko", " ko")      # la classe du gabarit de chaque mot de `JAUGE`, dans son ordre
CHAMPS_DECISION = (("probleme", "Le problème"), ("choix", "Mon choix"), ("ecarte", "Écarté"),
                   ("prix", "Le prix"), ("defaire", "Défaire"))
EMOJI_MAL = {"erreur": "🔥", "alerte": "⚠️"}


def morceaux_choix(gabarit):
    """`(tête, réponses, script)` du gabarit : ses `<link>` et `<style>`, la section « Tes réponses » et le `<script>`,
    cherchés hors commentaires — le commentaire de tête peut citer une balise, et un remplacement la trouverait d'abord.
    Sans `<link>` ni `<style>` la tête est vide, et `defauts_page` le dit. `ValueError` : un des deux autres manque."""
    hors = COMMENTAIRE.sub("", gabarit)
    tete = "".join("%s\n" % m.group(0) for m in TETE_CHOIX.finditer(hors))
    i = hors.find("<h2>Tes réponses</h2>")
    debut, fin = hors.rfind("<section>", 0, i), hors.find("</section>", i)
    if i < 0 or debut < 0 or fin < 0:
        raise ValueError("gabarit : la section « Tes réponses » est introuvable")
    d = hors.find("<script>")
    f = hors.find("</script>", d)
    if d < 0 or f < 0:
        raise ValueError("gabarit : le <script> est introuvable")
    return tete, hors[debut:fin + len("</section>")], hors[d:f + len("</script>")]


def texte_json(d, cle, ou):
    """Le texte non vide de `d[cle]` ; sinon `ValueError`, qui dit où il manque."""
    v = d.get(cle)
    if not isinstance(v, str) or not v.strip():
        raise ValueError("%s : « %s » manque, ou n'est pas un texte non vide" % (ou, cle))
    return v


def liste_json(d, cle, ou, genre: type = dict):
    """La liste `d[cle]` (vide si la clé manque), dont chaque élément est un `genre` ; sinon `ValueError`."""
    v = d.get(cle, [])
    if not isinstance(v, list) or not all(isinstance(x, genre) for x in v):
        raise ValueError("%s : « %s » doit être une liste de %s" % (ou, cle, "textes" if genre is str else "objets"))
    return v


def objet_json(d, cle):
    """L'objet `d[cle]` (`{}` si la clé manque) ; sinon `ValueError`."""
    v = d.get(cle, {})
    if not isinstance(v, dict):
        raise ValueError("« %s » doit être un objet" % cle)
    return v


def attribut(texte):
    return esc(texte).replace('"', "&quot;")


def html_jauge(mot):
    if mot not in JAUGE:
        raise ValueError("jauge : « %s » n'est pas un de %s" % (mot, " · ".join(JAUGE)))
    k = JAUGE.index(mot)
    return '<span class="jauge%s">%s %s%s</span>' % (CLASSE_JAUGE[k], EMOJIS_JAUGE[k].replace("⚠", "⚠️"), mot,
                                                     "…" if k == 1 else "")


def html_decision(nom, k, c):
    ou = "decisions.cartes[%d]" % k
    niveau = c.get("niveau", "moyen")
    if niveau not in ("faible", "moyen"):
        raise ValueError("%s : « niveau » vaut faible ou moyen" % ou)
    lignes = "".join("        <dt>%s</dt><dd>%s</dd>\n" % (libelle, cellule_md(texte_json(c, cle, ou)))
                     for cle, libelle in CHAMPS_DECISION)
    return ('    <div class="decision">\n'
            '      <div class="tete"><h3>%s · %s</h3><span class="puce %s">%s</span></div>\n'
            '      <dl class="grille">\n%s      </dl>\n'
            '      <div class="choix"><label><input type="radio" name="%s" value="garder">Je garde</label>'
            '<label><input type="radio" name="%s" value="revoir">À revoir</label></div>\n'
            '    </div>\n' % (nom, cellule_md(texte_json(c, "titre", ou)), niveau,
                              cellule_md(texte_json(c, "portee", ou)), lignes, nom, nom))


def html_question(nom, k, q):
    ou = "choix[%d]" % k
    titre = texte_json(q, "titre", ou)
    options = liste_json(q, "options", ou)
    if len(options) < 2:
        raise ValueError("%s : %d option(s), il en faut au moins deux" % (ou, len(options)))
    valeurs, recommandees, labels = set(), 0, ""
    for j, o in enumerate(options):
        oou = "%s.options[%d]" % (ou, j)
        valeur, recommande = texte_json(o, "valeur", oou), o.get("recommande", False)
        if valeur in valeurs:
            raise ValueError("%s : la valeur « %s » est déjà prise" % (oou, valeur))
        if not isinstance(recommande, bool):
            raise ValueError("%s : « recommande » vaut true ou false" % oou)
        valeurs.add(valeur)
        recommandees += recommande
        if recommandees > 1:
            raise ValueError("%s : deux options recommandées" % ou)
        labels += ('        <label><input type="radio" name="%s" value="%s"><span><b>%s%s</b>%s</span></label>\n'
                   % (nom, attribut(valeur), cellule_md(texte_json(o, "libelle", oou)),
                      " (recommandé)" if recommande else "", cellule_md(texte_json(o, "effet", oou))))
    puces = "".join("        <li>%s</li>\n" % cellule_md(p) for p in liste_json(q, "puces", ou, str))
    return ('    <div class="question">\n      <h3>🟡 %s · %s</h3>\n%s      <div class="choix options">\n%s'
            '      </div>\n    </div>\n'
            % (nom, cellule_md(titre), "      <ul>\n%s      </ul>\n" % puces if puces else "", labels))


def sections_choix(d):
    """`([section html], [name des cartes])` : une section par clé de `d`, dans l'ordre du gabarit."""
    blocs, noms = [], []

    def section(titre, corps):
        blocs.append("  <section>\n    <h2>%s</h2>\n%s  </section>\n" % (titre, corps))

    chiffres = objet_json(d, "chiffres")
    cases = liste_json(chiffres, "cases", "chiffres")
    if cases:
        corps = "".join('      <div class="chiffre"><b>%s</b><span>%s</span></div>\n'
                        % (cellule_md(texte_json(x, "valeur", "chiffres.cases")),
                           cellule_md(texte_json(x, "legende", "chiffres.cases"))) for x in cases)
        sources = "".join("      <li>%s</li>\n" % cellule_md(s) for s in liste_json(chiffres, "sources", "chiffres", str))
        section("Les chiffres", '    <div class="chiffres">\n%s    </div>\n%s' % (
            corps, '    <ul class="sous" style="font-size:.95rem">\n%s    </ul>\n' % sources if sources else ""))
    fait = liste_json(d, "fait", "racine")
    if fait:
        lignes = "".join('          <tr><td class="n">%s</td><td><b>%s</b><br>%s</td><td>%s</td><td class="n">%s</td></tr>\n'
                         % tuple(cellule_md(texte_json(x, cle, "fait")) for cle in ("ref", "code", "titre", "livre", "cout"))
                         for x in fait)
        section("Ce qui a été fait", '    <div class="tableau">\n      <table>\n        <thead><tr><th>Réf.</th><th>Quoi</th>'
                "<th>Ce qu'il livre</th><th>Coût</th></tr></thead>\n        <tbody>\n%s        </tbody>\n      </table>\n"
                "    </div>\n" % lignes)
    dec = objet_json(d, "decisions")
    cartes = liste_json(dec, "cartes", "decisions")
    if cartes:
        noms += ["D%d" % (k + 1) for k in range(len(cartes))]
        intro = cellule_md(dec["intro"]) + " " if isinstance(dec.get("intro"), str) else ""
        section("Les décisions prises seul — à valider",
                '    <p class="sous">%sCoche ce que tu gardes, ajoute un commentaire si besoin ; en bas, un bouton copie tes '
                "réponses.</p>\n\n%s" % (intro, "\n".join(html_decision("D%d" % (k + 1), k, c) for k, c in enumerate(cartes))))
    questions = liste_json(d, "choix", "racine")
    if questions:
        noms += ["Q%d" % (k + 1) for k in range(len(questions))]
        section("Les choix à trancher", '    <p class="sous">Une carte par question. Chaque option dit ce qu\'elle change.</p>'
                "\n\n%s" % "\n".join(html_question("Q%d" % (k + 1), k, q) for k, q in enumerate(questions)))
    mal = liste_json(d, "mal", "racine")
    if mal:
        for k, m in enumerate(mal):
            if m.get("genre") not in EMOJI_MAL:
                raise ValueError("mal[%d] : « genre » vaut erreur ou alerte" % k)
        section("Ce qui a mal tourné", "".join(
            '    <div class="%s">\n      <h3>%s %s</h3>\n      <p>%s</p>\n    </div>\n'
            % (m["genre"], EMOJI_MAL[m["genre"]], cellule_md(texte_json(m, "titre", "mal")),
               cellule_md(texte_json(m, "texte", "mal"))) for m in mal))
    fil = liste_json(d, "fil", "racine")
    if fil:
        section("Le fil", '    <p class="sous" style="font-size:.95rem">Heures lues sur les commits.</p>\n'
                '    <ul class="fil">\n%s    </ul>\n' % "".join(
                    "      <li><time>%s</time><span><b>%s</b> · %s</span></li>\n"
                    % tuple(cellule_md(texte_json(x, cle, "fil")) for cle in ("heure", "code", "texte")) for x in fil))
    return blocs, noms


def explique_json(d):
    """`explique` à la racine du JSON de `chef page` : `True` pose l'Explique-moi sur la page (`data-explique`), absent
    vaut `False` ; d'un autre genre, `ValueError`."""
    v = d.get("explique", False)
    if not isinstance(v, bool):
        raise ValueError("racine : « explique » vaut true ou false")
    return v


def page_choix(gabarit, d):
    """`(html, name des cartes)` : la page de `d` (voir `chef page`, dans la docstring du module), bâtie sur les morceaux
    de `gabarit`. `ValueError` : ce qui manque ou n'est pas du bon genre, `GARDE:` à l'appelant."""
    tete, reponses, script = morceaux_choix(gabarit)
    explique = " data-explique" if explique_json(d) else ""
    projet, sujet, titre = (texte_json(d, k, "racine") for k in ("projet", "sujet", "titre"))
    date = d.get("date") or datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(date)
    except (TypeError, ValueError):
        raise ValueError("racine : « date » vaut AAAA-MM-JJ") from None
    plage = texte_json(d, "plage", "racine") if "plage" in d else None
    blocs, noms = sections_choix(d)
    if not noms:
        raise ValueError("aucune carte : ni « decisions », ni « choix »")
    entete = ('  <header style="display:flex;flex-direction:column;gap:.8rem">\n    <p class="mono sous">%s</p>\n'
              "    <h1>%s</h1>\n" % (" · ".join(esc(x) for x in (projet, date, plage) if x), cellule_md(titre)))
    if "jauge" in d:
        entete += "    %s\n" % html_jauge(d["jauge"])
    puces = "".join("      <li>%s</li>\n" % cellule_md(p) for p in liste_json(d, "puces", "racine", str))
    entete += "    <ul>\n%s    </ul>\n" % puces if puces else ""
    blocs = [entete + "  </header>\n"] + blocs + ["  " + reponses + "\n"]
    if "pied" in d:
        blocs.append('  <footer class="sous" style="font-size:.9375rem;border-top:1px solid var(--trait);padding-top:1rem">\n'
                     "    %s\n  </footer>\n" % cellule_md(texte_json(d, "pied", "racine")))
    return ("<title>%s — %s</title>\n%s\n" % (esc(projet), esc(titre), tete)
            + '<div class="page" data-cle="%s"%s>\n\n%s</div>\n\n%s\n' % (attribut("%s-%s-%s" % (projet, date, sujet)),
                                                                          explique, "\n".join(blocs), script)), noms


def cmd_chef_page(questions, chemin, sortie, gabarit):
    """`chef page` (forme du JSON et `GARDE:` : docstring du module) : `questions` est le JSON ou `@fichier`,
    `gabarit` le texte du modèle. Écrit `chemin` seulement si la page bâtie passe `defauts_page`."""
    try:
        d = json.loads(lire_arg(questions))
        if not isinstance(d, dict):
            raise ValueError("le JSON n'est pas un objet")
        page, noms = page_choix(gabarit, d)
    except OSError as e:
        sortie.write("GARDE: questions illisibles : %s\n" % e)
        return 1
    except json.JSONDecodeError as e:
        sortie.write("GARDE: JSON illisible : %s\n" % e)
        return 1
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    manques = defauts_page(page)
    for m in manques:
        sortie.write("GARDE: %s — %s\n" % (chemin, m))
    if manques:
        return 1
    try:
        os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
        with open(chemin, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page)
    except OSError as e:
        sortie.write("GARDE: %s — écriture impossible : %s\n" % (chemin, e))
        return 1
    sortie.write("PAGE SAINE %d blocs\nCARTES %s\n" % (len(textes_visibles(page)), " ".join(noms)))
    sortie.write("CAPACITES sample\n" if explique_json(d) else "")  # déjà validé par page_choix
    return 0


# --- attente : les pages que la limite du jour a refusées (chantier LOC) ------

TEXTE_LIMITE = "publish 429"                    # le début du texte du refus, relevé par LOC1
MARGE_TACHE = datetime.timedelta(minutes=10)    # la tâche planifiée part après la remise à zéro


def dossier_artefacts(racine):
    contexte = champ(lignes_de(os.path.join(racine, "CHANTIER.md")), "contexte", "context AI/")
    return os.path.join(racine, contexte, "artefacts")


def entrees_attente(lignes):
    """[(page, url, heure)] des lignes d'un fichier `en-attente`, dans leur ordre."""
    entrees = []
    for l in lignes:
        c = l.split("\t") + ["aucune", ""]
        if c[0]:
            entrees.append((c[0], c[1], c[2]))
    return entrees


def texte_attente(entrees):
    """Le fichier `en-attente` de `entrees` : une ligne par page — le texte que `ecrire_attente` écrit (chantier NUI)."""
    return "".join("\t".join(e) + "\n" for e in entrees)


def lire_attente(artefacts):
    """[(page, url, heure)] dans l'ordre du fichier `en-attente` ; absent : liste vide."""
    chemin = os.path.join(artefacts, "en-attente")
    return entrees_attente(lignes_de(chemin)) if os.path.isfile(chemin) else []


def ecrire_attente(artefacts, entrees):
    """Le fichier en entier dans un `.tmp` puis `os.replace` ; liste vide : le fichier disparaît."""
    chemin = os.path.join(artefacts, "en-attente")
    if not entrees:
        if os.path.exists(chemin):
            os.remove(chemin)
        return
    os.makedirs(artefacts, exist_ok=True)
    with open(chemin + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(texte_attente(entrees))
    os.replace(chemin + ".tmp", chemin)


def ajouter_attente(artefacts, page, url, heure):
    """La page prend la place de son ancienne entrée, en fin de liste : la dernière gagne."""
    ecrire_attente(artefacts, [e for e in lire_attente(artefacts) if e[0] != page] + [(page, url, heure)])


def retirer_attente(artefacts, page):
    """Le nombre d'entrées restantes ; rien n'est écrit si la page n'y était pas."""
    avant = lire_attente(artefacts)
    restant = [e for e in avant if e[0] != page]
    if len(restant) != len(avant):
        ecrire_attente(artefacts, restant)
    return len(restant)


def lignes_attente(artefacts):
    return ["ATTENTE=%s %s" % (p, u) for p, u, _ in lire_attente(artefacts)]


def attentes_de_nuit(projet, pages, sortie):
    """Sous `VLP_NUIT=1`, mettre en attente chaque `(chemin, url)` de `pages` — la session `claude -p` n'a pas l'outil
    Artifact : le chef du matin les publie (NPB1) —, et écrire `ATTENTE <page> — <url>`. Hors nuit : rien."""
    if os.environ.get("VLP_NUIT") == "1":
        noter_attentes(projet, pages, sortie)


def noter_attentes(projet, pages, sortie):
    """Mettre en attente chaque `(chemin, url)` de `pages` dans le dossier artefacts du projet, et écrire
    `ATTENTE <page> — <url>` ; une page hors de ce dossier est ignorée."""
    artefacts = dossier_artefacts(projet)
    heure = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    for chemin, url in pages:
        nom = page_relative(artefacts, os.path.abspath(chemin))
        if nom:
            ajouter_attente(artefacts, nom, url or "aucune", heure)
            sortie.write("ATTENTE %s — %s\n" % (nom, url or "aucune"))


def dire_attentes(projet, sortie):
    """Écrire les `ATTENTE=` du projet après les fusions du matin : les pages qu'une nuit n'a pas pu publier (NPB1)."""
    for ligne in lignes_attente(dossier_artefacts(projet)):
        sortie.write(ligne + "\n")


def page_relative(artefacts, page):
    """`page` relative au dossier artefacts, en barres obliques ; None si elle est ailleurs."""
    if os.path.isabs(page):
        try:
            page = os.path.relpath(page, artefacts)
        except ValueError:
            return None
    page = page.replace("\\", "/")
    return None if page == ".." or page.startswith("../") else page


def remise_a_zero(maintenant):
    """(remise à zéro, tâche planifiée) : le prochain minuit UTC après `maintenant`, puis
    `MARGE_TACHE` plus tard, dans le fuseau de `maintenant`."""
    utc = maintenant.astimezone(datetime.timezone.utc)
    zero = datetime.datetime.combine(utc.date() + datetime.timedelta(days=1), datetime.time(),
                                     tzinfo=datetime.timezone.utc)
    return zero.astimezone(maintenant.tzinfo), (zero + MARGE_TACHE).astimezone(maintenant.tzinfo)


def cmd_attente(a, sortie, maintenant=None):
    if a.op == "lister":
        # la racine d'un projet équipé vaut son dossier artefacts : sinon `.` rendait « ATTENTE 0 » en silence
        dossier = dossier_artefacts(a.dossier) if equipe(a.dossier) else a.dossier
        for l in lignes_attente(dossier):
            sortie.write(l + "\n")
        sortie.write("ATTENTE %d\n" % len(lire_attente(dossier)))
        return 0
    racine = trouver(a.projet or os.getcwd())
    if racine is None:
        sortie.write("GARDE: pas de projet équipé ici : %s\n" % (a.projet or os.getcwd()))
        return 1
    artefacts = dossier_artefacts(racine)
    page = page_relative(artefacts, a.page)
    url = getattr(a, "url", None) or "aucune"
    if page is None or any(c in page + url for c in "\t\r\n"):
        sortie.write("GARDE: page hors du dossier artefacts, ou tabulation dans la page ou l'url : %s\n" % a.page)
        return 1
    if a.op == "retirer":
        n = retirer_attente(artefacts, page)
    else:
        heure = (maintenant or datetime.datetime.now().astimezone()).isoformat(timespec="minutes")
        ajouter_attente(artefacts, page, url, heure)
        n = len(lire_attente(artefacts))
    sortie.write("ATTENTE %d\n" % n)
    return 0


def noter_joints(outil, cwd, page):
    """Après une publication réussie : l'empreinte de chaque fichier de `files` (forme dict,
    source en chemin ou `{from}` ; relative à `root`, puis au dossier courant) dans `publie`,
    à côté de `page` (chantier JNT). Un fichier copié d'un autre artefact ou absent : ignoré."""
    fichiers = outil.get("files")
    if not isinstance(fichiers, dict):
        return
    base = cwd if isinstance(cwd, str) else os.getcwd()
    if isinstance(outil.get("root"), str):
        base = os.path.join(base, outil["root"])
    empreintes = {}
    for nom, source in fichiers.items():
        if isinstance(source, dict):
            source = source.get("from")
        if isinstance(nom, str) and isinstance(source, str):
            source = os.path.join(base, source)
            if os.path.isfile(source):
                empreintes[nom] = empreinte(source)
    if empreintes:
        noter_publie(os.path.dirname(page), os.path.basename(page), empreintes)


def cmd_attente_hook(entree, sortie, maintenant=None):
    """Le hook `PostToolUse` et `PostToolUseFailure` sur `Artifact` (chantier LOC). Un échec dont
    `error` porte `TEXTE_LIMITE` ajoute la page à la liste et, la première fois du jour UTC pour
    ce projet, propose une tâche planifiée ; un succès retire la page et note l'empreinte des
    joints passés (`noter_joints`, chantier JNT). Muet sur tout le reste : un autre refus, une
    page hors des artefacts d'un projet équipé, une entrée illisible."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    if not isinstance(d, dict) or d.get("tool_name") != "Artifact":
        return 0
    evenement, outil = d.get("hook_event_name"), d.get("tool_input")
    if evenement not in ("PostToolUse", "PostToolUseFailure") or not isinstance(outil, dict) \
            or outil.get("asset") is True:
        return 0
    chemin = outil.get("file_path")
    if not isinstance(chemin, str) or not chemin:
        return 0
    cwd = d.get("cwd")
    if not os.path.isabs(chemin) and isinstance(cwd, str):
        chemin = os.path.join(cwd, chemin)
    chemin = os.path.abspath(chemin)
    racine = trouver(os.path.dirname(chemin))
    if racine is None:
        return 0
    artefacts = dossier_artefacts(racine)
    page = page_relative(artefacts, chemin)
    if page is None:
        return 0
    if evenement == "PostToolUse":
        retirer_attente(artefacts, page)
        noter_joints(outil, cwd, chemin)
        return 0
    erreur = d.get("error")
    if not isinstance(erreur, str) or TEXTE_LIMITE not in erreur:
        return 0
    maintenant = maintenant or datetime.datetime.now().astimezone()
    url = outil.get("url")
    ajouter_attente(artefacts, page, url if isinstance(url, str) and url else "aucune",
                    maintenant.isoformat(timespec="minutes"))
    jour = maintenant.astimezone(datetime.timezone.utc).date().isoformat()
    if not tampon_neuf("vlp-attente-%s-%s" % (hashlib.sha1(racine.encode("utf-8")).hexdigest()[:16], jour)):
        return 0
    zero, tache = remise_a_zero(maintenant)
    message = ("Limite de publication du jour atteinte : %s attend dans la liste (`attente lister`). "
               "Remise à zéro à %s locale ; propose à l'utilisateur une tâche planifiée à %s qui "
               "republie la liste." % (page, zero.strftime("%H:%M"), tache.strftime("%H:%M")))
    sortie.write(json.dumps({"hookSpecificOutput": {"hookEventName": evenement, "additionalContext": message}},
                            ensure_ascii=False) + "\n")
    return 0


# « Fiches » avec majuscule aussi : l'encart du chantier en cours l'écrit ainsi (dette BTN).
PLAGE_TEXTE = re.compile(r"[Ff]iches [A-Z]{1,3}[0-9]+(?:–[A-Z]{1,3}[0-9]+)?")


def cmd_comparer(a, sortie):
    """`PERDU:`/`AJOUTÉ:` entre le texte visible de deux pages, en multiset —
    une mesure, pas une garde : sort 0 même avec des pertes."""
    for chemin in (a.ancienne, a.neuve):
        if not os.path.isfile(chemin):
            sortie.write("GARDE: introuvable %s\n" % chemin)
            return 1
    anciens = textes_visibles(lire(a.ancienne))
    neufs = textes_visibles(lire(a.neuve))
    restant_neufs = collections.Counter(neufs)
    perdus = []
    for t in anciens:
        if restant_neufs[t] > 0:
            restant_neufs[t] -= 1
        else:
            perdus.append(t)
    restant_anciens = collections.Counter(anciens)
    ajoutes = []
    for t in neufs:
        if restant_anciens[t] > 0:
            restant_anciens[t] -= 1
        else:
            ajoutes.append(t)
    # Dette HAB : une plage d'en-tête refaite (« fiches X1–X7 » → « X1–X8 ») n'est
    # pas une perte — la paire sort en `PLAGE:`, ni perdue ni ajoutée.
    plages = []
    for t in list(perdus):
        forme = PLAGE_TEXTE.sub("fiches #", t)
        if forme == t:
            continue
        for n in ajoutes:
            if PLAGE_TEXTE.sub("fiches #", n) == forme:
                plages.append((t, n))
                perdus.remove(t)
                ajoutes.remove(n)
                break
    for t in perdus:
        sortie.write("PERDU: %s\n" % t)
    for t in ajoutes:
        sortie.write("AJOUTÉ: %s\n" % t)
    for t, n in plages:
        sortie.write("PLAGE: %s → %s\n" % (t, n))
    sortie.write("COMPARER %d perdus · %d ajoutés%s\n" % (
        len(perdus), len(ajoutes), " · %d plages refaites" % len(plages) if plages else ""))
    return 0


def markdown_brut(html):
    """(`**`, liens Markdown, liens cassés) restés dans les zones todo, encours et
    clos d'une feuille de route, en occurrences — hors code cité, hors ligne
    d'exemple du gabarit."""
    (a, b, _), (c, d) = zone_todo(html), zone(html, "encours", "\n", "  </section>")
    # une feuille dont les clos sont partis dans l'archive n'a plus de ZONE:clos (chantier ARC)
    e, f = zone(html, "clos", "<tbody>\n", "        </tbody>") if "<!-- ZONE:clos" in html else (0, 0)
    clos = RANG_CLOS.sub(lambda m: "".join(lignes_clos(m.group(0))), html[e:f])
    texte = MONO.sub("", html[a:b] + html[c:d] + clos)
    return texte.count("**"), texte.count("](http"), texte.count('href="&lt;')


# --- niveau ------------------------------------------------------------------

# Ce qu'on ne regarde pas : une copie locale de `methode-chantier.md`. La
# méthode dit qu'un projet équipé avant la règle garde la sienne — on a
# seulement cessé d'en fabriquer.
VARIABLE = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}")
# Une variable ne compte que là où une commande lit un chemin : le champ d'une
# ligne `- **nom** : …`, ou une cellule de table. Ailleurs c'est de la prose qui
# cite la règle, et le fichier d'état en cite beaucoup.
PORTEUSE = re.compile(r"^\s*(?:-\s*\*\*[^*]+\*\*\s*:|\|)")
TITRE_CLOS = re.compile(r"^#+\s.*\bclos\b", re.I)


def capte(fn, *args):
    """(code, lignes) d'une sous-commande rejouée pour son texte : `niveau`
    n'invente aucun contrôle que les autres savent déjà faire."""
    s = io.StringIO()
    code = fn(*(args + (s,)))
    return code, s.getvalue().splitlines()


def variables_citees(projet, sources):
    """(chemin, numéro, variable) de chaque `${…}` posée en chemin lisible."""
    for libelle, chemin in sources:
        for i, l in enumerate(lignes_du_projet(projet, chemin, libelle), 1):
            if PORTEUSE.match(l):
                for v in VARIABLE.findall(l):
                    yield chemin, i, v


def table_des_clos(lignes):
    """Le numéro du titre « Chantiers clos » suivi d'une table, ou None : le
    titre seul ne gêne pas, c'est la table qui double l'index."""
    debut = None
    for i, l in enumerate(lignes, 1):
        if l.startswith("#"):
            debut = i if TITRE_CLOS.match(l) else None
        elif debut and l.startswith("|"):
            return debut
    return None


FICHIER_MD = re.compile(r"[\w][\w./ -]*\.md")


def entete_clos():
    """Le titre et la phrase que le gabarit de `CHANTIER.md` pose à la place
    d'une table des chantiers clos."""
    g = lignes_de(os.path.join(KIT, "templates", "CHANTIER.md"))
    i = next(k for k, l in enumerate(g) if TITRE_CLOS.match(l))
    j = next(k for k in range(i, len(g)) if g[k].startswith("Lettres de fiche déjà prises"))
    return g[i:j]


def sans_table_des_clos(carte_, index):
    """`CHANTIER.md` sans sa table des chantiers clos, ou None si la retirer
    perdrait quelque chose : la ligne des lettres prises doit suivre la table,
    et l'index nommer chacun de ses fichiers."""
    i = table_des_clos(carte_)
    if i is None:
        return None
    i -= 1
    j = next((k for k in range(i, len(carte_)) if carte_[k].startswith("Lettres de fiche déjà prises")), None)
    if j is None:
        return None
    vus = "\n".join(index)
    for l in carte_[i:j]:
        if l.startswith("|") and any(os.path.basename(nom) not in vus for nom in FICHIER_MD.findall(l)):
            return None
    return carte_[:i] + entete_clos() + carte_[j:]


def cmd_niveau(a, sortie):
    """En quoi un projet équipé a dérivé du kit. Sans `--ecrire`, n'écrit rien
    nulle part ; avec, corrige les écarts dont la bonne valeur se déduit sans
    jugement, et laisse les autres en `ÉCART:`. Comme `clore`, tout se calcule
    avant la première écriture."""
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    date = a.date or __import__("datetime").date.today().isoformat()
    ecarts = avertissements = corriges = 0
    ecritures = []
    carte_ = lignes_du_projet(projet, "CHANTIER.md", "carte")

    _, lignes = capte(cmd_renvois, projet)
    poids = "POIDS non mesuré"
    for l in lignes:
        if l.startswith("ABSENT: "):
            ecarts += 1
            sortie.write("ÉCART: renvois: %s — nommé, introuvable\n" % l[8:])
        elif l.startswith("AVERTISSEMENT: "):
            avertissements += 1
            sortie.write("AVERTISSEMENT: poids: %s\n" % l[15:])
        elif l.startswith("POIDS "):
            poids = l
        elif l.startswith("GARDE: "):
            ecarts += 1
            sortie.write("ÉCART: renvois: %s\n" % l[7:])

    page = page_feuille(projet)
    absente = not os.path.isfile(page)
    html = lire(os.path.join(KIT, GABARIT_FEUILLE)) if absente else lire(page)
    migre = migrer_feuille(html)
    converti, n = html, 0
    try:
        neuf, _ = feuille(projet, migre, None, date)
        converti, n = migrer_clos(neuf)
        # sans --ecrire : la page que l'on voit ; absente, le gabarit régénéré, comme avant VOI1
        md = markdown_brut(converti if a.ecrire else neuf if absente else html)
    except ValueError as e:
        neuf = md = None
        ecarts += 1
        sortie.write("ÉCART: feuille: %s\n" % e)
    if neuf is None:
        pass
    elif absente:
        if a.ecrire:
            ecritures.append((page, converti))
            corriges += 1
            sortie.write("CORRIGÉ: feuille: posée depuis le gabarit puis régénérée — %s\n" % page)
        else:
            ecarts += 1
            sortie.write("ÉCART: feuille: feuille de route introuvable : %s — le gabarit la pose\n" % page)
    else:
        for present, manque, pose in (
                (migre != html, "le bloc repliable des chantiers clos manque, et son estimation en"
                                " dollars — le gabarit les a", "bloc repliable des chantiers clos posé"),
                (neuf != migre, "écart — « vlp.py feuille %s » la régénère" % projet, "régénérée")):
            if not present:
                continue
            if a.ecrire:
                corriges += 1
                sortie.write("CORRIGÉ: feuille: %s\n" % pose)
            else:
                ecarts += 1
                sortie.write("ÉCART: feuille: %s\n" % manque)
        if a.ecrire and n:
            corriges += 1
            sortie.write("CORRIGÉ: feuille: %d lignes closes converties\n" % n)
        if a.ecrire and converti != html:
            ecritures.append((page, converti))
    sortie.write("MARKDOWN non mesuré, la feuille ne se régénère pas — %s\n" % page if md is None
                 else "MARKDOWN %d ** · %d liens Markdown · %d liens cassés — %s\n" % (md + (page,)))
    if md and any(md):
        ecarts += 1
        sortie.write("ÉCART: feuille: Markdown brut ou lien cassé%s\n"
                     % (" — « vlp.py niveau --ecrire » convertit les lignes closes" if n and not a.ecrire else ""))

    courant = courant_a_compter(projet, sortie)
    if courant:
        fichier = chemin_garde(os.path.join(projet, courant), "fichier de fiches courant", courant)
        code, lignes = capte(cmd_page, argparse.Namespace(
            fichier=fichier, page=page_du_fichier(fichier), note=None, journal=None,
            creer=False, projet=None, titre=None, resultat=None, verifier=True, date=None, forme=False))
        for l in lignes:
            if l.startswith("ÉCART: ") or l.startswith("GARDE: "):
                ecarts += 1
                sortie.write("ÉCART: page: %s\n" % l[7:])

    contexte = champ(carte_, "contexte", "context AI/")
    index = champ(carte_, "index", contexte.rstrip("/") + "/00-INDEX.md")
    sources = [("carte", "CHANTIER.md"), ("index", index)]
    etat = champ(carte_, "fichier d'état")
    if etat:
        sources.append(("fichier d'état", etat))
    for chemin, i, v in variables_citees(projet, sources):
        ecarts += 1
        sortie.write("ÉCART: variable: %s:%d cite %s — une variable ne vaut que dans"
                     " le texte d'une commande, pas dans un fichier de données\n" % (chemin, i, v))

    for e, c, ecrites in etapes_niveau(projet, retirer_clos(projet, carte_, index, a.ecrire, sortie), date, a.ecrire,
                                       sortie):
        ecarts, corriges = ecarts + e, corriges + c
        ecritures += ecrites

    for chemin, contenu in ecritures:
        dossier = os.path.dirname(chemin)
        if dossier and not os.path.isdir(dossier):
            os.makedirs(dossier)
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write(contenu)
        if chemin == page:
            ecrire_couts(page, contenu, couts_du_projet(projet, contenu))
    sortie.write(poids + "\n")
    if a.ecrire:
        sortie.write("NIVEAU %d corrigés · %d à la main — %s\n" % (corriges, ecarts, projet))
    else:
        sortie.write("NIVEAU %d écarts · %d avertissements — %s\n" % (ecarts, avertissements, projet))
    return 1 if ecarts else 0


def etapes_niveau(projet, clos, date, ecrire, sortie):
    """Les quatre étapes de `niveau` de même forme, `[(écarts, corrigés, écritures)]`, dans l'ordre : `clos`, ce que
    `retirer_clos` a rendu, puis la marque, la ligne et Git. La ligne ne part
    qu'après la marque, que `poser_ouverture` pose en la lisant, et du CHANTIER.md que `retirer_clos` a peut-être
    réécrit (NUI31)."""
    etapes = [clos, poser_ouverture(projet, date, ecrire, sortie)]
    ecrites = [ec for _, _, ecs in etapes for ec in ecs]
    return etapes + [retirer_ligne_courant(projet, ecrites, etapes[1][0] == 0, ecrire, sortie),
                     ecarts_git(projet, sortie)]


# Un chemin de machine : un lecteur Windows, le dossier personnel, ou une racine Unix d'utilisateur.
CHEMIN_MACHINE = re.compile(r"(?<![\w/])(?:[A-Za-z]:[\\/]|~[\\/]|/(?:home|Users|mnt)/)")


def ecarts_git(projet, sortie):
    """L'étape « git » de `niveau` (NUI36) : ce que la règle veut suivi (`etat_git`) mais que Git ignore — avec la
    ligne de `.gitignore` qui le couvre — ou n'a pas ajouté, et une ligne **kit** qui porte un chemin de machine. Hors
    Git : rien. `--ecrire` ne corrige rien : retirer une ligne, ajouter, commiter sont des gestes de l'utilisateur.
    `(écarts, 0, [])`."""
    etat = etat_git(projet)
    if etat is None:
        return 0, 0, []
    ecarts = 0
    for nom, exemple in etat["ignoré"]:
        code, t = git_texte(["check-ignore", "-v", "--", exemple], projet)
        source = t.split("\t")[0].rpartition(":")[0] if code == 0 and "\t" in t else "?"
        sortie.write("ÉCART: git: %s — ignoré par %s — à retirer à la main, puis ajouter\n" % (nom, source))
        ecarts += 1
    for nom, _ in etat["non ajouté"]:
        sortie.write("ÉCART: git: %s — non ajouté — à ajouter et commiter à la main\n" % nom)
        ecarts += 1
    kit = champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "kit", "")
    if CHEMIN_MACHINE.search(kit):
        sortie.write("ÉCART: git: CHANTIER.md — la ligne « kit » porte un chemin de machine, et le fichier part"
                     " dans Git : « le plugin vlp », à la main\n")
        ecarts += 1
    return ecarts, 0, []


def retirer_clos(projet, carte_, index, ecrire, sortie):
    """L'étape « clos » de `niveau` : la table des chantiers clos restée dans CHANTIER.md, retirée avec `ecrire` si
    l'index nomme chacun de ses fichiers. `(écarts, corrigés, [(chemin, contenu)])`."""
    rang = table_des_clos(carte_)
    if rang is None:
        return 0, 0, []
    neuve = sans_table_des_clos(carte_, lignes_index(projet, index)) if ecrire else None
    if neuve is None:
        sortie.write("ÉCART: clos: CHANTIER.md:%d — la table des chantiers clos vit"
                     " dans l'index, pas dans la carte\n" % rang)
        return 1, 0, []
    sortie.write("CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:%d —"
                 " l'index nomme chacun de ses fichiers\n" % rang)
    return 0, 1, [(os.path.join(projet, "CHANTIER.md"), "\n".join(neuve) + "\n")]


def poser_ouverture(projet, date, ecrire, sortie):
    """L'étape « marque » de `niveau` (NUI30) : un projet sans aucune marque d'ouverture — `migre` faux — la reçoit
    sur le fichier que nomme l'ancienne ligne de CHANTIER.md, sous son titre, datée de son commit d'ouverture (`date`
    à défaut, et la ligne le dit) ; ligne à `aucun`, projet migré : rien. Sans `ecrire`, introuvable ou sans titre :
    `ÉCART: marque:`. `(écarts, corrigés, [(chemin, contenu)])`."""
    fichier = None if migre(projet) else fichier_courant(lire(os.path.join(projet, "CHANTIER.md")))
    if not fichier:
        return 0, 0, []
    chemin = os.path.join(projet, fichier)
    lignes = lignes_de(chemin) if os.path.isfile(chemin) else None
    ids = [l.split()[1] for l in lignes or () if TITRE.match(l)]
    code = lettre_de(ids[0]) if ids else "?"
    quand = date_ouverture(projet, code) if ids and ecrire else None
    if lignes is None:
        sortie.write("ÉCART: marque: %s introuvable — marque d'ouverture non posée\n" % fichier)
    elif not ecrire:
        sortie.write("ÉCART: marque: %s sans **Ouvert.** — « vlp.py niveau --ecrire » la pose\n" % fichier)
    elif not poser_marque(lignes, OUVERT_LIGNE % (quand or date)):
        sortie.write("ÉCART: marque: pas de titre « # Chantier » dans %s — marque non posée\n" % fichier)
    else:
        sortie.write("CORRIGÉ: marque: **Ouvert.** le %s sur %s — %s\n" % (quand or date, fichier, "son commit"
                     " d'ouverture" if quand else "date de l'appel, aucun commit « Chantier %s ouvert »" % code))
        return 0, 1, [(chemin, "\n".join(lignes) + "\n")]
    return 1, 0, []


def retirer_ligne_courant(projet, ecritures, marque_posee, ecrire, sortie):
    """L'étape « ligne » de `niveau` (NUI31) : la ligne « fichier de fiches courant » restée dans CHANTIER.md — plus
    aucun lecteur ne la suit, elle ne peut que mentir —, retirée avec `ecrire` si `marque_posee` (l'étape « marque »
    sans écart : sinon elle reste, seule trace du chantier ouvert). Part du dernier CHANTIER.md de `ecritures`, sinon
    du disque, fins de ligne gardées. `(écarts, corrigés, [(chemin, contenu)])`."""
    chemin = os.path.join(projet, "CHANTIER.md")
    texte = next((c for ch, c in reversed(ecritures) if ch == chemin), None)
    if texte is None:
        with open(chemin, encoding="utf-8", newline="") as fh:
            texte = fh.read()
    fin = "\r\n" if "\r\n" in texte else "\n"
    lignes = texte.replace("\r\n", "\n").split("\n")
    rangs = [k for k, l in enumerate(lignes) if COURANT.match(l)]
    if not rangs:
        return 0, 0, []
    if not (ecrire and marque_posee):
        sortie.write("ÉCART: ligne: CHANTIER.md:%d — « fichier de fiches courant » n'est plus lue (NUI31) — %s\n"
                     % (rangs[0] + 1, "« vlp.py niveau --ecrire » la retire" if marque_posee
                        else "gardée tant que la marque d'ouverture manque"))
        return 1, 0, []
    sortie.write("CORRIGÉ: ligne: « fichier de fiches courant » retirée de CHANTIER.md:%d — la marque d'ouverture"
                 " dit le chantier\n" % (rangs[0] + 1))
    return 0, 1, [(chemin, fin.join(l for k, l in enumerate(lignes) if k not in rangs))]


# --- clore -------------------------------------------------------------------

CLOS_LIGNE = "**CLOS** le %s. Ne se rejoue pas — ne sert plus qu'à relire son socle."
OUVERT_LIGNE = "**Ouvert.** le %s."
PAUSE_LIGNE = "**Pause.** le %s — %s"
# Les motifs de lecture des trois marques : le début de ligne, comme `**CLOS**` (chantier NUI21).
MARQUE_OUVERT, MARQUE_CLOS, MARQUE_PAUSE = "**Ouvert.**", "**CLOS**", "**Pause.**"
ENTREE_CLOS = re.compile(r"^- Clos le \S+ : .* \(chantier [A-Z]{1,3}\)\.$")
ROUTAGE_CLOS = "| relire un chantier clos |"
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
    code_git, texte = git_texte(["log", "--format=%as", "-i", "-E", "--grep=" + motif], racine)
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
    code, sortie_git = git_texte(["ls-tree", "--name-only", rev, "./%s/" % dossier], racine)
    noms = sorted(os.path.basename(l) for l in (sortie_git.splitlines() if code == 0 else []) if l.endswith(".md"))
    specs = ["%s:./%s/%s" % (rev, dossier, n) for n in noms]
    textes = []
    for n, spec, t in zip(noms, specs, blobs_git(specs, racine)):
        if t is None:       # pas un blob lisible d'un coup : `git show`, comme avant VIT3
            code, t = git_texte(["show", spec], racine)
            t = t if code == 0 else None
        textes.append((rel % n, t.split("\n") if t is not None else []))
    return textes


def blobs_git(specs, cwd):
    """Lire les objets `specs` (`<rev>:<chemin>`) en un seul `git cat-file --batch` (VIT3) ; rendre, pour chacun, son
    texte tel que `git_texte` le lit de `git show` — UTF-8, `\\r\\n` et `\\r` en `\\n` —, ou None : absent, pas un blob,
    ou Git en échec."""
    import subprocess
    try:
        r = subprocess.run([GIT, "-c", "core.quotepath=false", "cat-file", "--batch"], cwd=cwd, capture_output=True,
                           input="".join(s + "\n" for s in specs).encode("utf-8"), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return [None] * len(specs)
    if r.returncode:
        return [None] * len(specs)
    sortie, pos, textes = r.stdout, 0, []
    for _ in specs:
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
    code, s = git_texte(["worktree", "list", "--porcelain"], racine)
    blocs, dossier, branche = [], None, None
    for l in (s.split("\n") if code == 0 else []) + [""]:
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
    compte pas d'écart de page (NUI28)."""
    rendu = []
    for dossier in autres_worktrees(racine):
        try:
            f = courant_de(dossier)
        except Absent:
            continue
        ids = [l.split()[1] for l in lignes_de(os.path.join(dossier, f)) if TITRE.match(l)] if f else []
        if ids:
            rendu.append((lettre_de(ids[0]), dossier))
    return rendu


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
    code, p = git_texte(["rev-parse", "--git-path", "vlp-chantier"], racine)
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
    code, nom = git_texte(["rev-parse", "--abbrev-ref", tete], racine)
    if principale and code == 0 and nom.strip() != principale:
        code, base = git_texte(["merge-base", tete, principale], racine)
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
    if not equipe(a.projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % a.projet)
        return 1
    if a.rev is not None and git_texte(["rev-parse", "--verify", "-q", a.rev + "^{commit}"], a.projet)[0] != 0:
        sortie.write("GARDE: révision inconnue : %s\n" % a.rev)
        return 1
    liste = ouverts(a.projet, a.rev)
    sortie.write("".join("OUVERT %s\n" % f for f in liste) if liste else "OUVERTS=0\n")
    return 0


def rangee_todo(lignes, code):
    """(indice de l'en-tête `| # | Chantier`, indice de la rangée dont la 2e cellule commence par `` `code` ``,
    son numéro) ; sans en-tête ou sans rangée, None à leur place (TAB4)."""
    tete = next((k for k, l in enumerate(lignes) if l.startswith("| # | Chantier")), None)
    if tete is None:
        return None, None, None
    for k in range(tete + 1, len(lignes)):
        if not lignes[k].startswith("|"):
            break
        m = re.match(r"^\|\s*(\d+)\s*\|\s*`%s`" % re.escape(code), lignes[k])
        if m:
            return tete, k, m.group(1)
    return tete, None, None


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


def todo_de_clore(projet, carte_, code, date, ecritures):
    """La TODO à la clôture de `code` : sa rangée ôtée et ` <n>, `<code>`, clos le <date>.` à la provenance, sans
    entrée au journal — la ligne d'archive dit la clôture ; ajoutée à `ecritures`. Rend la ligne à imprimer ; un
    code absent de la TODO (chantier hors TODO) n'écrit rien et n'est pas une GARDE (RTO1)."""
    chemin = os.path.join(projet, champ(carte_, "fichier d'état") or "")
    lignes = lignes_de(chemin) if os.path.isfile(chemin) else []
    tete, k, numero = rangee_todo(lignes, code)
    if tete is None or k is None:
        return "TODO `%s` absente — rien ôté" % code
    oter_rangee(lignes, tete, k, " %s, `%s`, clos le %s." % (numero, code, date))
    ecritures.append((chemin, "\n".join(lignes) + "\n"))
    return "TODO `%s` ôtée · n° %s" % (code, numero)


def refus_d_oter(projet, carte_, code, lignes):
    """Le refus de `oter`, calculé avant toute écriture, ou None : TODO illisible, code absent de la TODO,
    chantier clos (« Lettres de fiche déjà prises ») ou ouvert (`courant_de`), journal absent (TAB4)."""
    try:
        todo_du_fichier(lignes)
    except ValueError as e:
        return "%s — rien écrit" % e
    if rangee_todo(lignes, code)[1] is None:
        return "`%s` absent de la TODO — rien écrit" % code
    if code in lettres_prises(carte_):
        return "`%s` est un chantier clos (« %s ») — rien écrit" % (code, LETTRES)
    courant = courant_de(projet)
    ids = [l.split()[1] for l in lignes_du_projet(projet, courant, "fichier de fiches") if TITRE.match(l)] \
        if courant else []
    if ids and lettre_de(ids[0]) == code:
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
    oter_rangee(lignes, tete, k, " %s, `%s`, retiré le %s : %s." % (numero, a.code, date, raison))
    while lignes and not lignes[-1].strip():
        lignes.pop()
    lignes += ["", "## %s — `%s` retiré de la TODO (n° %s)" % (date, a.code, numero), "", "- **Raison** : %s." % raison]
    ecrire_par_tmp([(chemin, "\n".join(lignes) + "\n")])
    sortie.write("OTÉ `%s` · n° %s · provenance marquée · journal %s — %s\n" % (a.code, numero, date, etat))
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
            if not any(l.startswith(ROUTAGE_CLOS) for l in cl):
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
        gardes.append("page du chantier introuvable : %s" % chemin_page)
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
                pg, _, _, total_mesure, _ = regenerer(pg, chemin_fiches, parts_page, date, couts_page)
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
    todo_dit = todo_de_clore(projet, carte_, lettre, date, ecritures)

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
    sortie.write(todo_dit + "\n")
    for g in gardes:
        sortie.write("GARDE: %s — le reste est écrit\n" % g)
    if html is None:
        sortie.write("GARDE: feuille de route introuvable : %s — CHANTIER.md et fiches écrits\n" % page)
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
        sortie.write(ligne_files(joints))
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
    code, ici = git_texte(["symbolic-ref", "--short", "-q", "HEAD"], projet)
    if os.environ.get("VLP_NUIT") != "1" and dossier_principal and principale and code == 0 \
            and ici.strip() != principale:
        sortie.write('FUSIONNER depuis %s : "%s" "%s" fusionner "%s" %s\n' % (
            dossier_principal, sys.executable, VLP_PY, dossier_principal, ici.strip()))
    return 0


# --- ouvrir ------------------------------------------------------------------

LIGNE_FICHIER = re.compile(r"^\| `\d\d")
# Une ligne close : sa plage `X1–Xn` (ou `X1` seule) et son total mesuré, le dernier nombre entre
# parenthèses de la cellule — `non mesurable` n'en a pas (chantier EST).
PLAGE_FICHES = re.compile(r'<td class="mono">[A-Z]{1,3}([0-9]+)(?:–[A-Z]{1,3}([0-9]+))?</td>')
TOTAL_MESURE = re.compile(r"\((\d[\d ]*)\)</td>")


def moyenne_clos(html):
    """(tokens, fiches, clos, usd, fiches_usd) des lignes de `ZONE:clos` au total mesuré ; fiches
    d'une ligne = `n − 1 + 1` de sa plage `X1–Xn`, une seule pour `X1` (chantier EST). `usd`
    (`None` sans aucune) et `fiches_usd` ne comptent que les lignes qui portent un prix en tête
    de cellule — la moyenne $/fiche de l'estimé se lit en les divisant (chantier TAU)."""
    from decimal import Decimal
    i = html.find("ZONE:clos")
    tokens = fiches = clos = fiches_usd = 0
    usd = None
    for r in lignes_clos(html[i:]) if i >= 0 else []:
        p, m = PLAGE_FICHES.search(r), TOTAL_MESURE.findall(r)
        if p and m:
            n = int(p.group(2) or p.group(1)) - int(p.group(1)) + 1
            tokens += int(m[-1].replace(" ", ""))
            fiches += n
            clos += 1
            d = PRIX_CLOS.search(r)
            if d:
                usd = Decimal(d.group(1).replace(",", ".")) if usd is None else usd + Decimal(d.group(1).replace(",", "."))
                fiches_usd += n
    return tokens, fiches, clos, usd, fiches_usd


def decimal_fr(v):
    return ("%g" % v).replace(".", ",")


def nombre_fiches(s):
    try:
        v = float(s.replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError("nombre de fiches attendu : %s" % s)
    if v <= 0:
        raise argparse.ArgumentTypeError("nombre de fiches positif attendu : %s" % s)
    return v


def lever_pause(lignes):
    """Retire de `lignes`, en place, chaque `**Pause.**` et la ligne vide posée avant elle ; vrai s'il y en avait une :
    `ouvrir` reprend un chantier en pause (NUI30)."""
    rangs = [k for k, l in enumerate(lignes) if l.startswith(MARQUE_PAUSE)]
    for k in reversed(rangs):
        del lignes[k - 1 if k and not lignes[k - 1].strip() else k:k + 1]
    return bool(rangs)


def cmd_ouvrir(a, sortie):
    """Ouvrir un chantier dans `a.projet` : les écritures mécaniques décrites à `ouvrir` dans la docstring de `vlp.py`."""
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    fichier = a.fiches.replace("\\", "/")
    chemin_fiches = os.path.join(projet, fichier)
    fiches_ = lignes_gardees(chemin_fiches, "fichier de fiches", fichier)
    ids = [l.split()[1] for l in fiches_ if TITRE.match(l)]
    if not ids:
        sortie.write("GARDE: aucune fiche dans %s\n" % fichier)
        return 1
    if any(l.startswith("**CLOS**") for l in fiches_):
        sortie.write("GARDE: %s porte **CLOS** — un chantier clos ne se rouvre pas\n" % fichier)
        return 1
    chemin_carte = os.path.join(projet, "CHANTIER.md")
    carte_ = lignes_de(chemin_carte)
    courant = courant_de(projet)
    if courant and courant != fichier:
        sortie.write("GARDE: un chantier est déjà ouvert : %s\n" % courant)
        return 1
    lettre, fait = lettre_de(ids[0]), "%s..%s" % bornes(ids)
    # Un même code ouvert dans un autre worktree : deux chantiers que la fusion confondrait. Le même fichier, hérité
    # d'une branche commune, n'en est pas un second (NUI27).
    for dossier, autre in ouverts_ailleurs(projet):
        ids_autre = [l.split()[1] for l in lignes_de(os.path.join(dossier, autre)) if TITRE.match(l)]
        if autre != fichier and ids_autre and lettre_de(ids_autre[0]) == lettre:
            sortie.write("GARDE: le code %s est déjà ouvert ailleurs : %s dans %s — rien d'écrit\n" % (lettre, autre, dossier))
            return 1
    # L'artefact ne se reprend que pour ce chantier-ci : un nouveau ne reçoit jamais la page d'un autre (NUI23).
    url = retirer_chevrons_url(a.artefact) or (champ(carte_, "artefact du chantier", "aucun")
                                                if courant == fichier else "aucun")
    gardes = []
    fiches_change = False

    # 0. une pause se lève — ouvrir un fichier en pause, c'est le reprendre (NUI30) —, puis la marque d'ouverture, une
    # fois, sous le titre `# Chantier ` : sans ce titre, `ouverts` ne la verrait pas.
    reprise = " · pause levée" if lever_pause(fiches_) else ""
    neuve = not any(l.startswith(MARQUE_OUVERT) for l in fiches_)
    fiches_change = neuve and poser_marque(fiches_, OUVERT_LIGNE % __import__("datetime").date.today().isoformat())
    if neuve and not fiches_change:
        gardes.append("pas de titre « # Chantier » dans %s — marque d'ouverture non posée" % fichier)
    fiches_change = fiches_change or bool(reprise)

    # 1. CHANTIER.md
    vu = False
    for k, l in enumerate(carte_):
        m = re.match(r"^(\s*-\s*\*\*artefact du chantier\*\*\s*:\s*)", l)
        if m:
            carte_[k], vu = m.group(1) + url, True
    if not vu:
        sortie.write("GARDE: ligne « artefact du chantier » absente de CHANTIER.md — rien d'écrit\n")
        return 1

    # 2. l'index
    ecritures = []
    nom = os.path.basename(fichier)
    index = champ(carte_, "index")
    chemin_index = os.path.join(projet, index) if index else None
    n_index = "+0"
    if not chemin_index or not os.path.isfile(chemin_index):
        gardes.append("index introuvable : %s" % index)
    else:
        idx = lignes_de(chemin_index)
        if not any(l.startswith("| `%s` |" % nom) for l in idx):
            rangs = [k for k, l in enumerate(idx) if LIGNE_FICHIER.match(l)]
            if not rangs:
                gardes.append("aucune ligne de fichier dans %s" % index)
            else:
                rang = max(rangs, key=lambda k: int(idx[k][3:5]))
                idx.insert(rang + 1,"| `%s` | on joue une fiche `%s*` — chantier **ouvert** « %s », `%s` |"
                           % (nom, lettre, a.titre, fait))
                ecritures.append((chemin_index, idx))
                n_index = "+1"
        else:
            # Relancé sur le fichier ouvert : seule la plage de sa ligne suit le fichier (chantier PLA).
            k = next(k for k, l in enumerate(idx) if l.startswith("| `%s` |" % nom))
            ligne = re.sub(r"`[^`]*` \|$", "`%s` |" % fait, idx[k])
            if "**ouvert**" in idx[k] and ligne != idx[k]:
                idx[k] = ligne
                ecritures.append((chemin_index, idx))
                n_index = "~1"

    # 3. le routage de CLAUDE.md
    chemin_claude = os.path.join(projet, "CLAUDE.md")
    n_routage = 0
    if not os.path.isfile(chemin_claude):
        gardes.append("CLAUDE.md introuvable")
    else:
        cl = lignes_de(chemin_claude)
        if not any("`%s`" % fichier in l for l in cl if l.startswith("|")):
            rang = next((k for k, l in enumerate(cl) if l.startswith(ROUTAGE_CLOS)),
                        next((k for k, l in enumerate(cl) if l.startswith("| relire le chantier")), None))
            if rang is None:
                gardes.append("aucune ligne « relire un chantier clos » ni « relire le chantier » dans CLAUDE.md")
            else:
                titre = a.titre[:1].lower() + a.titre[1:]
                cl.insert(rang, "| jouer une fiche du chantier %s (%s) | `%s` — chantier **ouvert**, par `/vlp:tache %s<n>` |"
                          % (lettre, titre, fichier, lettre))
                ecritures.append((chemin_claude, cl))
                n_routage = 1

    # 4. la session du cadrage, avant la première ligne `## ` : le socle dans un vrai fichier,
    # jamais entre le marqueur d'une fiche et son titre (chantier CAD). Un titre de fiche en
    # commence une : `next` la trouve toujours.
    n_session = 0
    s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if s and s not in sessions_de(fiches_):
        k = next(k for k, l in enumerate(fiches_) if l.startswith("## "))
        fiches_[k:k] = ["**Session** : %s" % s, ""]
        fiches_change = True
        n_session = 1

    # 5. l'estimé, juste avant `**Fait.**` : la moyenne $/fiche des clos au prix mesuré × N
    # (chantier EST ; TAU pour le prix, plus la louche).
    estime = ""
    if a.estime_fiches is not None:
        fait_ = next((k for k, l in enumerate(fiches_) if l.startswith(("**Fait.**", "**Où on en est.**"))), None)
        feuille_ = page_clos(projet)
        _, n_fiches, n_clos, usd_clos, fiches_usd = moyenne_clos(lire(feuille_)) if os.path.isfile(feuille_) else (0, 0, 0, None, 0)
        if any(l.startswith("**Estimé.**") for l in fiches_):
            estime = " · estimé gardé"
        elif not os.path.isfile(feuille_):
            gardes.append("feuille de route introuvable : %s — pas d'estimé" % feuille_)
        elif not n_fiches:
            gardes.append("aucun chantier clos mesuré sur la feuille de route — pas d'estimé")
        elif usd_clos is None:
            gardes.append("aucun chantier clos au prix mesuré sur la feuille de route — pas d'estimé")
        elif fait_ is None:
            gardes.append("pas de ligne **Fait.** dans %s — pas d'estimé" % fichier)
        else:
            par_fiche = usd_par_fiche(usd_clos, fiches_usd)
            usd = approx(a.estime_fiches * par_fiche)
            fiches_[fait_:fait_] = ["**Estimé.** %s fiches · %s — %s/fiche sur %d clos (le %s)."
                                    % (decimal_fr(a.estime_fiches), usd, approx(par_fiche), n_clos,
                                       __import__("datetime").date.today().isoformat()), ""]
            fiches_change = True
            estime = " · estimé %s fiches %s" % (decimal_fr(a.estime_fiches), usd)

    if fiches_change:
        ecritures.append((chemin_fiches, fiches_))
    ecritures.append((chemin_carte, carte_))
    for chemin, lignes in ecritures:
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lignes) + "\n")
    # Le post-it du dossier : son chantier, propre à ce worktree, jamais suivi par Git (NUI23).
    p = postit(projet)
    if p:
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(fichier + "\n")
    for g in gardes:
        sortie.write("GARDE: %s — le reste est écrit\n" % g)
    sortie.write("OUVERT %s %s · index %s · routage +%d · session +%d · artefact %s%s%s — %s\n"
                 % (lettre, fait, n_index, n_routage, n_session, url, estime, reprise, projet))
    return 0


def cmd_pause(a, sortie):
    """`pause <fichier> "<raison>"` : `**Pause.** le <date> — <raison>` sous le titre `# Chantier ` ; `ouvrir` la lève
    (NUI30). Introuvable, clos, déjà en pause, sans titre : `GARDE:`, rien d'écrit."""
    nom = a.fichier.replace("\\", "/")
    if not os.path.isfile(a.fichier):
        sortie.write("GARDE: fichier de fiches introuvable : %s\n" % nom)
        return 1
    lignes = lignes_de(a.fichier)
    deja = next((m for m in (MARQUE_CLOS, MARQUE_PAUSE) if any(l.startswith(m) for l in lignes)), None)
    date = a.date or __import__("datetime").date.today().isoformat()
    if deja:
        sortie.write("GARDE: %s porte déjà %s — rien d'écrit\n" % (nom, deja))
        return 1
    if not poser_marque(lignes, PAUSE_LIGNE % (date, a.raison.strip())):
        sortie.write("GARDE: pas de titre « # Chantier » dans %s — rien d'écrit\n" % nom)
        return 1
    with open(a.fichier, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lignes) + "\n")
    sortie.write("PAUSE %s le %s\n" % (nom, date))
    return 0


# --- entrée ------------------------------------------------------------------

# --- bac ---------------------------------------------------------------------

# Le bac d'essai de FIL3 (journal du 2026-09-24) : fixe, en constantes.
# Le fichier de fiches porte la marque d'ouverture, dans le dossier de contexte : `courant_de` le trouve (NUI31).
BAC_FICHES = "ctx/fiches.md"
BAC_CHANTIER = """# Chantier courant — bac d'essai

- **contexte** : ctx/
- **artefact du chantier** : aucun
- **livraison** : aucune
- **vérification** : aucune — lire le statut rendu

Lettres de fiche déjà prises : F (Deux fiches factices). Un nouveau chantier en choisit un autre.
"""
BAC_FICHIER = """# Chantier F — bac d'essai, deux fiches factices

**Ouvert.** le 2026-09-24.

## Le socle commun

Un bac d'essai : rien à écrire, rien à commiter.

## L'ordre des fiches

F1, puis F2.

---

<!-- FICHE:F1 -->
## F1 [ ] — Lire douze fichiers

**Prompt**
Lis `n01.txt`, `n02.txt`, … jusqu'à `n12.txt`, dans l'ordre, par l'outil `Read` :
un appel par message, d'affilée, dans cette même exécution.

**Critère de fin**
Les douze fichiers lus.
<!-- /FICHE -->

---

<!-- FICHE:F2 -->
## F2 [ ] — Lancer douze fois exit 3

**Prompt**
Lance douze fois `exit 3` par l'outil `Bash` : un appel par message, d'affilée,
dans cette même exécution.

**Critère de fin**
Douze appels lancés.
<!-- /FICHE -->
"""
BAC_COMMANDES = (
    'claude -p "Appelle l\'outil Skill avec skill \\"vlp:jouer\\" et args \\"F1\\", puis recopie son'
    ' resultat tel quel. Rien d\'autre." --model haiku --max-budget-usd 1 --permission-mode acceptEdits'
    ' --allowedTools "Skill" --output-format stream-json --verbose',
    'claude -p "Appelle l\'outil Skill avec skill \\"vlp:jouer\\" et args \\"F2\\", puis recopie son'
    ' resultat tel quel. Rien d\'autre." --model haiku --max-budget-usd 1 --permission-mode acceptEdits'
    ' --allowedTools "Skill" "Bash" --output-format stream-json --verbose < /dev/null',
)


CLAUDE_ABSENT = "GARDE: claude.exe introuvable — PATH, Packages et APPDATA vus\n"
# Le pre-commit refuse le commit sur ce début de ligne, et laisse passer sur celui de CLAUDE_ABSENT (VIT19).
CLAUDE_SANS_EXE = "GARDE: claude.exe absent de l'app Claude — cherché à */ et à */*/ sous %s\n"
# L'app Claude : Packages d'abord — l'app du Store, vue d'un terminal comme de l'app —, puis `%APPDATA%`, vue de
# l'app seule (REG3).
CLAUDE_APP = (("LOCALAPPDATA", ("Packages", "Claude_*", "LocalCache", "Roaming", "Claude")), ("APPDATA", ("Claude",)))


def dossiers_claude_code():
    """Rendre les dossiers `claude-code` de l'app Claude, une liste par racine de `CLAUDE_APP`, dans son ordre ; une
    variable absente ou une app absente rend une liste vide (VIT19)."""
    return [glob.glob(os.path.join(os.environ[v], *parties, "claude-code")) if os.environ.get(v) else []
            for v, parties in CLAUDE_APP]


def version_claude(dossier, chemin):
    """Rendre la version de `chemin`, lue au dossier juste sous `dossier` (`claude-code/<version>/…`), en nombres :
    2.1.99 passe avant 2.1.280 (CLI) ; l'empreinte que l'app range dessous (VIT19) n'y compte pas."""
    nom = os.path.relpath(chemin, dossier).split(os.sep)[0]
    return [int(x) if x.isdigit() else 0 for x in nom.split(".")]


def trouver_claude():
    """Rendre le `claude` du kit (chantier CLI) : `VLP_CLAUDE`, le PATH, puis la plus haute version de l'app, racine
    par racine (`CLAUDE_APP`) — à `claude-code/<version>/` comme à `claude-code/<version>/<empreinte>/` (VIT19) —,
    sinon None."""
    import shutil
    if os.environ.get("VLP_CLAUDE"):
        return os.environ["VLP_CLAUDE"]
    sur_path = shutil.which("claude")
    if sur_path:
        return sur_path
    for dossiers in dossiers_claude_code():
        trouves = [(d, p) for d in dossiers for motif in ("*", os.path.join("*", "*"))
                   for p in glob.glob(os.path.join(d, motif, "claude.exe"))]
        if trouves:
            return max(trouves, key=lambda t: version_claude(*t))[1]
    return None


def cmd_claude(sortie):
    """Imprimer `CLAUDE <chemin>` et rendre 0 ; sinon une `GARDE:` et rendre 1 — `CLAUDE_SANS_EXE` si l'app est là
    sans son `claude.exe`, que le pre-commit refuse, `CLAUDE_ABSENT` sinon, qu'il laisse passer (VIT19)."""
    chemin = trouver_claude()
    if chemin:
        sortie.write("CLAUDE %s\n" % chemin)
        return 0
    app = [d for dossiers in dossiers_claude_code() for d in dossiers]
    sortie.write(CLAUDE_SANS_EXE % " et ".join(app) if app else CLAUDE_ABSENT)
    return 1


def cmd_bac(dossier, sortie):
    """Pose le bac d'essai de FIL3 dans `dossier`, vide ou absent, et imprime ses commandes `claude -p`."""
    if os.path.exists(dossier) and (not os.path.isdir(dossier) or os.listdir(dossier)):
        sortie.write("GARDE: %s existe et n'est pas un dossier vide — rien d'écrit\n" % dossier)
        return 1
    os.makedirs(dossier, exist_ok=True)
    fichiers = {"CHANTIER.md": BAC_CHANTIER, BAC_FICHES: BAC_FICHIER}
    fichiers.update(("n%02d.txt" % k, "fichier %02d\n" % k) for k in range(1, 13))
    os.makedirs(os.path.join(dossier, os.path.dirname(BAC_FICHES)), exist_ok=True)
    for nom, texte in fichiers.items():
        with open(os.path.join(dossier, nom), "w", encoding="utf-8", newline="") as f:
            f.write(texte)
    sortie.write("BAC %s\n" % dossier)
    for c in BAC_COMMANDES:
        sortie.write(c + "\n")
    chemin = trouver_claude()
    if not chemin:
        sortie.write(CLAUDE_ABSENT)
    sortie.write('SESSION Set-Location "%s"; & "%s"\n' % (os.path.abspath(dossier), chemin or "claude"))
    return 0


KIT_EXCLUS = (".git", ".claude", "context AI", "__pycache__", "relais-python.err")
# La copie d'un mutant garde `context AI/` : la suite y lit la carte du kit (NIV1) et la pièce de JUG2 (VIT2).
MUTANT_EXCLUS = tuple(n for n in KIT_EXCLUS if n != "context AI")
# L'empreinte d'une suite verte (VIT11) laisse aussi ce que la clôture d'une fiche écrit après la suite (`sante --base`)
# et les sorties des evals, ignorées par Git ; elle vit dans le dossier Git du kit, hors suivi, une par worktree.
EMPREINTE_EXCLUS = KIT_EXCLUS + ("sante-base.json", "results")
SUITE_VERTE = "vlp-suite-verte"


def empreinte_kit(racine):
    """Rendre le sha256 des fichiers du kit `racine` tels qu'ils sont sur disque, commités ou non : chemins relatifs
    et contenus, dans l'ordre, sans `EMPREINTE_EXCLUS` (VIT11)."""
    h = hashlib.sha256()
    for dossier, sous, fichiers in os.walk(racine):
        sous[:] = sorted(s for s in sous if s not in EMPREINTE_EXCLUS)
        for nom in sorted(f for f in fichiers if f not in EMPREINTE_EXCLUS):
            chemin = os.path.join(dossier, nom)
            with open(chemin, "rb") as f:
                h.update(os.path.relpath(chemin, racine).replace(os.sep, "/").encode("utf-8") + b"\0" + f.read() + b"\0")
    return h.hexdigest()


def chemin_suite_verte(racine):
    """Rendre `<dossier Git de racine>/vlp-suite-verte`, ou `None` hors dépôt (la copie d'un mutant)."""
    code, dossier = git_texte(["rev-parse", "--absolute-git-dir"], racine)
    return os.path.join(dossier.strip(), SUITE_VERTE) if code == 0 and dossier.strip() else None


def noter_suite_verte(racine, empreinte):
    """Écrire `empreinte` comme celle de la dernière suite entière verte du kit `racine` ; hors dépôt, rien (VIT11)."""
    chemin = chemin_suite_verte(racine)
    if chemin:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(empreinte + "\n")


def est_kit(racine):
    """Vrai si `racine` est le kit vlp lui-même — son plugin et sa suite —, pas un projet équipé (VIT11)."""
    return all(os.path.isfile(os.path.join(racine, *p)) for p in ((".claude-plugin", "plugin.json"), ("scripts", "test-vlp.py")))


def suite_manquante(fichier):
    """Rendre le kit dont `fichier` fait partie si sa dernière suite verte n'a pas joué ses fichiers d'aujourd'hui,
    sinon `None` — et `None` hors du kit : un projet équipé a ses propres tests (VIT11)."""
    code, racine = git_texte(["rev-parse", "--show-toplevel"], os.path.dirname(os.path.abspath(fichier)))
    racine = racine.strip()
    if code != 0 or not racine or not est_kit(racine):
        return None
    chemin = chemin_suite_verte(racine)
    try:
        with open(chemin or "", encoding="utf-8") as f:
            notee = f.read().strip()
    except OSError:
        notee = ""
    return None if notee == empreinte_kit(racine) else racine


def cmd_kit_essai(dossier, max_turns, source, sortie):
    """Une copie jetable du kit à plafond bas (EVF2) : l'eval se lance sur elle, le vrai kit ne bouge pas."""
    import shutil
    source = os.path.abspath(source or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(dossier) and (not os.path.isdir(dossier) or os.listdir(dossier)):
        sortie.write("GARDE: %s existe et n'est pas un dossier vide — rien d'écrit\n" % dossier)
        return 1
    fiche = os.path.join(source, "agents", "fiche.md")
    avant = lire_max_turns(fiche)
    if avant is None:
        sortie.write("GARDE: pas de ligne maxTurns dans %s — rien d'écrit\n" % fiche)
        return 1

    def exclus(racine, noms):
        rel = os.path.relpath(racine, source).replace(os.sep, "/")
        return [n for n in noms if n in KIT_EXCLUS or (rel == "evals" and n == "results")]

    if os.path.isdir(dossier):
        os.rmdir(dossier)
    shutil.copytree(source, dossier, ignore=exclus)
    copie = os.path.join(dossier, "agents", "fiche.md")
    with open(copie, encoding="utf-8", newline="") as f:
        texte = f.read()
    texte = re.sub(r"(?m)^maxTurns:.*$", "maxTurns: %d" % max_turns, texte, count=1)
    with open(copie, "w", encoding="utf-8", newline="") as f:
        f.write(texte)
    sortie.write("KIT %s · maxTurns %d → %d\n" % (dossier, avant, max_turns))
    return 0


def cmd_transcription(chemin, sortie):
    """Compte la transcription d'un sous-agent (chantier BAC) : tours comme `comptoir_tours`,
    appels, avertissements du filet et l'appel qui les précède, erreurs de hook, dernier message."""
    tours, appels, erreurs_outil, avertis = [], {}, {}, []
    hook_erreurs, dernier_id, stop, textes = 0, None, None, {}
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    d = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                if not isinstance(d, dict):
                    continue
                att = d.get("attachment")
                if isinstance(att, dict):
                    if att.get("type") == "hook_additional_context":
                        avertis.append(att)
                    elif att.get("type") == "hook_non_blocking_error":
                        hook_erreurs += 1
                message = d.get("message")
                if not isinstance(message, dict):
                    continue
                contenu = message.get("content")
                blocs = contenu if isinstance(contenu, list) else []
                if d.get("type") == "user":
                    for b in blocs:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            erreurs_outil[b.get("tool_use_id")] = bool(b.get("is_error"))
                    continue
                mid = message.get("id")
                if d.get("type") != "assistant" or not mid or not isinstance(message.get("usage"), dict):
                    continue
                if mid not in tours:
                    tours.append(mid)
                if mid != dernier_id:
                    dernier_id, stop = mid, None
                stop = message.get("stop_reason") or stop
                for b in blocs:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        appels[b.get("id")] = (len(tours), b.get("name") or "?")
                    elif b.get("type") == "text":
                        textes.setdefault(mid, []).append(b.get("text") or "")
    except (OSError, UnicodeDecodeError) as e:
        sortie.write("GARDE: transcription illisible : %s — %s\n" % (chemin, e))
        return 1
    par_outil = {}
    for _, nom in appels.values():
        par_outil[nom] = par_outil.get(nom, 0) + 1
    sortie.write("TOURS=%d\n" % len(tours))
    sortie.write("APPELS=%d — %s\n" % (len(appels), ", ".join("%s %d" % o for o in par_outil.items()) or "aucun"))
    sortie.write("AVERTISSEMENTS=%d\n" % len(avertis))
    par_tour = {}
    for a in avertis:
        tour = appels.get(a.get("toolUseID"), ("?", "?"))[0]
        par_tour[tour] = par_tour.get(tour, 0) + 1
    sortie.write("AVERTIS_PAR_TOUR=%s\n" % (",".join("%s:%d" % t for t in par_tour.items()) or "aucun"))
    if avertis:
        a = avertis[0]
        uid = a.get("toolUseID")
        tour, outil = appels.get(uid, ("?", "?"))
        is_error = erreurs_outil.get(uid)
        sortie.write("PREMIER_AVERTISSEMENT tour=%s outil=%s is_error=%s hook=%s\n" % (
            tour, outil, "?" if is_error is None else ("oui" if is_error else "non"), a.get("hookName")))
        texte = a.get("content")
        if isinstance(texte, list):
            texte = " ".join(str(t) for t in texte)
        sortie.write("TEXTE=%s\n" % " ".join(str(texte or "").split()))
    else:
        sortie.write("PREMIER_AVERTISSEMENT aucun\n")
    sortie.write("HOOK_ERREURS=%d pour %d appels\n" % (hook_erreurs, len(appels)))
    texte = "\n".join(textes.get(dernier_id, [])) if dernier_id else ""
    mots = texte.split()
    sortie.write("DERNIER mot=%s stop_reason=%s\n" % (mots[0] if mots else "", stop))
    non_vides = [l.strip() for l in texte.splitlines() if l.strip()]
    sortie.write("DERNIERE_LIGNE=%s\n" % (non_vides[-1] if non_vides else ""))
    return 0


# --- aperçu local (chantier LOC) --------------------------------------------

TYPES_APERCU = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml; charset=utf-8"}
LARGEUR_TELEPHONE = 375
PORT_APERCU = 8790      # le premier port qu'`apercu` essaie ; +1 tant qu'une autre entrée le prend
PAGE_SERVIE = re.compile(r"[\w.\- ]+(/[\w.\- ]+)*$")    # relatif ; `..` se rejette à part


def faire_serveur(dossier, port):
    """Le serveur de `servir`, lié à 127.0.0.1 (port 0 : un port libre) ; `serve_forever` le lance."""
    import functools
    import html
    import http.server
    import urllib.parse

    class Apercu(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, **TYPES_APERCU}

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            if url.path != "/_telephone":
                return super().do_GET()
            page = urllib.parse.parse_qs(url.query).get("page", [""])[0]
            if not PAGE_SERVIE.match(page) or ".." in page.split("/"):
                return self.send_error(400, "page=<page> : un chemin relatif au dossier servi")
            cadre = ('<!doctype html><html lang="fr"><meta charset="utf-8"><title>Téléphone</title>'
                     '<body style="margin:0;background:#f4ede4"><iframe src="/%s" title="%s" '
                     'style="display:block;margin:0 auto;border:0;width:%dpx;height:100vh"></iframe>'
                     % (html.escape(urllib.parse.quote(page)), html.escape(page), LARGEUR_TELEPHONE))
            corps = cadre.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

    return http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Apercu, directory=dossier))


def cmd_servir(dossier, port, sortie):
    if not os.path.isdir(dossier):
        sortie.write("GARDE: dossier introuvable : %s\n" % dossier)
        return 1
    try:
        serveur = faire_serveur(dossier, port)
    except (OSError, OverflowError) as e:
        sortie.write("GARDE: port %s inutilisable : %s\n" % (port, e))
        return 1
    sortie.write("SERVIR http://127.0.0.1:%d/ · %s\n" % (serveur.server_port, dossier))
    sortie.flush()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        serveur.server_close()
    return 0


def lire_arg(x):
    """`@chemin` : le contenu du fichier, tel quel ; sinon le texte même."""
    if x.startswith("@"):
        with open(x[1:], encoding="utf-8", newline="") as f:
            return f.read()
    return x


def cmd_nuits_noter(texte, canal, arret, sortie, dossier=None, sorte=None):
    """Une ligne `note` (ou `stop`, avec `arret`) au carnet de nuit : `VLP_CARNET`, sinon celui du jour
    du dépôt de `dossier` (défaut : le dossier courant). Sans l'un ni l'autre : `GARDE:`, sort 1. `sorte` (une de
    `carnet.SORTES`) : ce que le matin fait de la note ; avec `arret`, `GARDE:` — un `stop` n'a pas de sorte."""
    if arret and sorte:
        print("GARDE: --sorte ne va pas avec --stop — un stop n'est pas une note du matin", file=sortie)
        return 1
    chemin = os.environ.get(carnet.ENV_CARNET) or carnet.du_jour(dossier or os.getcwd())
    if not chemin:
        print("GARDE: pas de dépôt Git ni de VLP_CARNET — pas de carnet de nuit où écrire", file=sortie)
        return 1
    canal = canal or os.environ.get(carnet.ENV_CANAL) or None
    if arret:
        carnet.stop(chemin, canal, texte)
    else:
        carnet.noter(chemin, canal, texte, sorte)
    print("NOTÉ %s" % chemin, file=sortie)
    return 0


# --- matin : fusionner la nuit dans main (chantier NUI, fiche NUI15) --------------------------
# Git fusionne sans conflit ce que `clore` remet à `aucun` dans `CHANTIER.md` : le chantier ouvert de `main`
# s'efface. `neutre` met à part le libellé de l'artefact et la liste des lettres, `restaurer` les rend ; la feuille,
# elle, se refait toujours, au rang « en cours » que `main` portait avant la fusion.

OUVERT_CARTE = re.compile(r"^([ \t]*-[ \t]*\*\*(artefact du chantier)\*\*[ \t]*:[ \t]*)(.*)$", re.M)
JETON_OUVERT, JETON_LETTRES = "§ouvert§", "§lettres§"


def neutre(texte):
    """`(texte, valeurs, liste)` : `texte` (un `CHANTIER.md`) dont la valeur du libellé et la liste des
    lettres sont remplacées par `JETON_OUVERT` et `JETON_LETTRES` ; `valeurs` : `{libellé: valeur}` ; `liste` :
    ce qui suit « Lettres de fiche déjà prises » jusqu'à `fin_lettres`, `None` sans cette ligne."""
    valeurs = {m.group(2): m.group(3) for m in OUVERT_CARTE.finditer(texte)}
    texte = OUVERT_CARTE.sub(lambda m: m.group(1) + JETON_OUVERT, texte)
    i = texte.find(LETTRES)
    if i < 0:
        return texte, valeurs, None
    i += len(LETTRES)
    k = fin_lettres(texte, i)
    return texte[:i] + JETON_LETTRES + texte[k:], valeurs, texte[i:k]


def restaurer(texte, valeurs, liste):
    """L'inverse de `neutre` : les libellés rendus à leur valeur dans `valeurs`, la liste des lettres à `liste`."""
    texte = OUVERT_CARTE.sub(lambda m: m.group(1) + valeurs.get(m.group(2), m.group(3)), texte)
    return texte if liste is None else texte.replace(JETON_LETTRES, liste)


def pointes_nuit(projet, date):
    """`([(branche, heure de la pointe)], None)` des `refs/heads/nuit/<date>-*`, ou `(None, erreur)`."""
    code, t = git_texte(["for-each-ref", "--format=%(refname) %(committerdate:unix)",
                         "refs/heads/nuit/%s-*" % date], projet)
    if code != 0:
        return None, t
    pointes = []
    for l in t.splitlines():
        champs = l.split()
        if len(champs) == 2 and champs[1].isdigit():
            pointes.append((champs[0][len("refs/heads/"):], int(champs[1])))
    return pointes, None


def ordre_nuit(pointes, date, projet):
    """Les branches de la nuit dans l'ordre du carnet : rang de la 1re ligne de chaque `canal` + `chantier` ; sans
    ligne au carnet, l'heure de la pointe, puis le nom. Rend `(branches, carnet_lu)` — `carnet_lu` faux : carnet
    absent ou sans ligne, tout est à l'heure de la pointe."""
    chemin = carnet.du_jour(projet, date)
    lignes = carnet.lire(chemin) if chemin else []
    place = {}
    for n, d in enumerate(lignes):
        place.setdefault((d.get("canal"), d.get("chantier")), n)

    def cle(p):
        canal, _, code = p[0][len("nuit/%s-" % date):].partition("-")
        return place.get((canal, code), len(lignes)), p[1], p[0]
    return [p[0] for p in sorted(pointes, key=cle)], bool(lignes)


# NUI16 : les fichiers que les deux canaux réécrivent ne se fusionnent pas ligne à ligne. Git y lève un conflit quand
# deux canaux ajoutent côte à côte (la TODO, le journal), et `merge=union` y ressuscite la ligne qu'un canal avait
# retirée (2cef70f). `fusionner_fichiers` les recalcule depuis la base, `main` et la branche, par clé ; ce qui reste
# d'un fichier va à `git merge-file`, un conflit y est un `GARDE:`.

JETON_TRANCHE = "§tranche§"
TITRE_JOURNAL = "## Journal des décisions"


def en_dict(lignes, cle):
    """`{clé: ligne}` dans l'ordre des lignes ; une clé en double lève `ValueError` — la fusion par clé n'y verrait plus clair."""
    d = {}
    for l in lignes:
        k = cle(l)
        if k in d:
            raise ValueError("clé en double : %s" % (k,))
        d[k] = l
    return d


def trois_voies(base, avant, leur, ordre="fin", resout=None):
    """La fusion à trois voies de `{clé: valeur}` : `([(clé, valeur)], désaccords)`. Une clé retirée d'un côté et intacte
    de l'autre est retirée ; changée d'un côté, elle prend ce changement ; ajoutée, elle est gardée. Changée des deux
    côtés, ou retirée d'un côté et changée de l'autre : un désaccord, rendu à l'appelant ; `resout(avant, leur)` le
    tranche (`None` : la clé s'en va), sans lui `avant` reste. Ordre : celui d'`avant`, puis les clés que seule la
    branche porte, à la suite (`fin`) ou en tête (`tete`)."""
    gardees, desaccords = {}, []
    for k in list(avant) + [k for k in leur if k not in avant]:
        b, a, l = base.get(k), avant.get(k), leur.get(k)
        if a == l or l == b:
            v = a
        elif a == b:
            v = l
        else:
            desaccords.append(k)
            v = resout(a, l) if resout else a
        if v is not None:
            gardees[k] = v
    cles = [k for k in avant if k in gardees]
    neuves = [k for k in leur if k in gardees and k not in avant]
    cles = neuves + cles if ordre == "tete" else cles + neuves
    return [(k, gardees[k]) for k in cles], desaccords


def fusion_lignes(b, a, l, cle, ordre="fin", resout=None):
    """`(lignes fusionnées, désaccords)` de trois listes de lignes, par `cle(ligne)`."""
    paires, desaccords = trois_voies(*(en_dict(t, cle) for t in (b, a, l)), ordre=ordre, resout=resout)
    return [v for _, v in paires], desaccords


def cle_todo(rangee):
    """Le n° d'une rangée de la TODO, lu par `todo_du_fichier` : `ValueError` si la rangée n'a pas ses 5 cellules."""
    lues = todo_du_fichier(["| # | Chantier", "|---|", rangee])
    if len(lues) != 1:
        raise ValueError("rangée de la TODO illisible : %s" % rangee)
    return lues[0][0]


def decouper_tables(lignes, quand):
    """`(neutre, tranches)` : sous chaque séparateur de table que `quand(lignes, i)` accepte, les rangées — les lignes
    `|` qui suivent — deviennent un `JETON_TRANCHE` dans `neutre`, et `tranches` les rend, table par table."""
    neutre, tranches, i = [], [], 0
    while i < len(lignes):
        neutre.append(lignes[i])
        i += 1
        if SEPARATEUR.match(lignes[i - 1]) and quand(lignes, i - 1):
            j = i
            while j < len(lignes) and lignes[j].startswith("|"):
                j += 1
            neutre.append(JETON_TRANCHE)
            tranches.append(lignes[i:j])
            i = j
    return neutre, tranches


def decouper_index(lignes):
    """`(neutre, genres, tranches)` de l'index ou de son archive : les rangées de chaque table."""
    neutre, tranches = decouper_tables(lignes, lambda ls, i: True)
    return neutre, ["rangées"] * len(tranches), tranches


def decouper_etat(lignes):
    """`(neutre, genres, tranches)` du fichier d'état : les rangées de la TODO, puis le journal, que `section` trouve
    à son titre et qui court jusqu'à la fin."""
    fin = lignes[-1:] == [""]
    corps = lignes[:-1] if fin else lignes
    trouve = section(corps, lambda l: l.startswith(TITRE_JOURNAL), lambda l: True)
    tete = corps if trouve is None else corps[:trouve[0]]
    neutre, tranches = decouper_tables(tete, lambda ls, i: i > 0 and ls[i - 1].startswith("| # | Chantier"))
    genres = ["TODO"] * len(tranches)
    if trouve is not None:
        neutre.append(JETON_TRANCHE)
        tranches.append(corps[trouve[0]:])
        genres.append("journal")
    return neutre + [""] * fin, genres, tranches


def decouper_claude(lignes):
    """`(neutre, genres, tranches)` de CLAUDE.md : les lignes « Clos le » de « Où on en est », en une tranche à la place
    de la première (ou à la suite de la dernière ligne de la section, s'il n'y en a pas)."""
    debut = next((k for k, l in enumerate(lignes) if l.startswith("## Où on en est")), None)
    if debut is None:
        return lignes, [], []
    fin = next((k for k in range(debut + 1, len(lignes)) if lignes[k].startswith("## ")), len(lignes))
    clos = [k for k in range(debut, fin) if ENTREE_CLOS.match(lignes[k])]
    place = clos[0] if clos else max((k for k in range(debut, fin) if lignes[k].strip()), default=debut) + 1
    neutre = [l for k, l in enumerate(lignes) if k not in clos]
    neutre.insert(place - sum(1 for k in clos if k < place), JETON_TRANCHE)
    return neutre, ["clos"], [[lignes[k] for k in clos]]


def fusion_texte(projet, textes, branche):
    """`(code, texte)` de `git merge-file` sur `textes` = (base, avant, leur) : 0, fusion propre ; > 0, le nombre de
    conflits, que le texte porte marqués ; `None`, Git muet ou en erreur, le texte est la raison."""
    with tempfile.TemporaryDirectory() as t:
        chemins = []
        for nom, contenu in (("avant", textes[1]), ("base", textes[0]), ("leur", textes[2])):
            chemins.append(os.path.join(t, nom))
            with open(chemins[-1], "w", encoding="utf-8", newline="") as fh:
                fh.write(contenu)
        code, msg = git_texte(["merge-file", "-L", "HEAD", "-L", "base", "-L", branche] + chemins, projet)
        if code is None or code > 127:
            return None, "git merge-file : %s" % msg
        return code, lire(chemins[0])


def fusion_a_jetons(projet, branche, textes, decouper, fusionner, gardes):
    """Le texte fusionné de `textes` = (base, avant, leur), ou `None` (à Git, ou `gardes` dit pourquoi). `decouper(lignes)`
    rend `(neutre, genres, tranches)` : le texte où chaque partie à fusionner par clé est un `JETON_TRANCHE`, et ces
    parties. Le reste passe par `git merge-file`, chaque tranche par `fusionner(genre, base, avant, leur, gardes)`."""
    if None in textes:
        return None
    try:
        morceaux = [decouper(t.split("\n")) for t in textes]
        if len({tuple(m[1]) for m in morceaux}) != 1:
            gardes.append("la structure n'est pas la même des trois côtés (tables, journal ou section)")
            return None
        code, fusion = fusion_texte(projet, ["\n".join(m[0]) for m in morceaux], branche)
        if code != 0:
            gardes.append("le reste du fichier est en conflit : %s" % ("à fusionner à la main" if code else fusion))
            return None
        rendu = [fusionner(g, b, a, l, gardes) for g, b, a, l in zip(morceaux[0][1], *(m[2] for m in morceaux))]
    except ValueError as e:
        gardes.append(str(e))
        return None
    if gardes:
        return None
    sortie, i = [], 0
    for ligne in fusion.split("\n"):
        if ligne == JETON_TRANCHE:
            sortie += rendu[i]
            i += 1
        else:
            sortie.append(ligne)
    return "\n".join(sortie)


def fusion_tranche_etat(genre, b, a, l, gardes):
    """La TODO par n° (`cle_todo`) ; le journal en union — la base, puis ce que `main` y a ajouté, puis la branche."""
    if genre == "TODO":
        rangees, desaccords = fusion_lignes(b, a, l, cle_todo)
        gardes.extend("TODO : la rangée n° %s est changée des deux côtés, ou retirée d'un côté et changée de l'autre" % k
                      for k in desaccords)
        return rangees
    if a == l:
        return a
    if a[:len(b)] != b or l[:len(b)] != b:
        gardes.append("journal : une ligne ancienne a changé, il ne se fusionne plus en union")
        return a
    return b + a[len(b):] + l[len(b):]


def fusion_tranche_claude(genre, b, a, l, gardes):
    """Les lignes « Clos le » des deux côtés, la branche à la suite, coupées aux `CLOS_GARDES` dernières."""
    entrees, _ = fusion_lignes(b, a, l, lambda x: x)
    entrees = entrees[len(clos_a_couper(entrees)):]
    return entrees


def fusion_tranche_index(trier):
    """La fusion des rangées d'un index, la ligne pour clé ; `trier` : l'archive, retriée par `numero_ligne`."""
    def fusionner(genre, b, a, l, gardes):
        rangees, _ = fusion_lignes(b, a, l, lambda x: x)
        return sorted(rangees, key=numero_ligne) if trier else rangees
    return fusionner


def fusion_etat(projet, branche, textes, gardes, infos):
    return fusion_a_jetons(projet, branche, textes, decouper_etat, fusion_tranche_etat, gardes)


def fusion_claude(projet, branche, textes, gardes, infos):
    return fusion_a_jetons(projet, branche, textes, decouper_claude, fusion_tranche_claude, gardes)


def fusion_index(projet, branche, textes, gardes, infos):
    return fusion_a_jetons(projet, branche, textes, decouper_index, fusion_tranche_index(False), gardes)


def fusion_archive_index(projet, branche, textes, gardes, infos):
    return fusion_a_jetons(projet, branche, textes, decouper_index, fusion_tranche_index(True), gardes)


def fusion_archive_clos(projet, branche, textes, gardes, infos):
    """`archive-clos.html` : les lignes closes par clé, celles de la branche en tête comme `clore` ; le pied et le résumé
    sont refaits par `resommer`, pas par `rafraichir_couts` (il réécrit la feuille)."""
    if None in textes:
        return None
    try:
        zones = [zone(t, "clos", "<tbody>\n", "        </tbody>") for t in textes]
        lignes, _ = fusion_lignes(*(lignes_clos(t[d:f]) for t, (d, f) in zip(textes, zones)), cle=lambda x: x, ordre="tete")
    except ValueError as e:
        gardes.append(str(e))
        return None
    corps, (d, f) = "".join(lignes), zones[1]
    usd, n_usd = prix_clos(corps)
    return resommer(textes[1][:d] + corps + textes[1][f:], len(lignes), total_clos(corps), usd, n_usd)


def heure_attente(entree):
    """L'heure d'une entrée de `en-attente`, en secondes ; 0 si elle ne se lit pas : sans heure, la plus ancienne."""
    try:
        return datetime.datetime.fromisoformat(entree[2]).timestamp()
    except ValueError:
        return 0.0


def fusion_attente(projet, branche, textes, gardes, infos):
    """`en-attente` : la page pour clé ; changée des deux côtés, l'heure la plus récente gagne, et elle passe en fin comme
    `ajouter_attente` ; retirée d'un côté et changée de l'autre, elle reste (mieux vaut republier deux fois que zéro) ;
    vide, le fichier est retiré par l'appelant. Absent d'un côté : sans entrée."""
    b, a, l = (en_dict(entrees_attente((t or "").split("\n")), lambda e: e[0]) for t in textes)

    def plus_recente(avant, leur):
        if avant is None or leur is None:
            return avant or leur
        return leur if heure_attente(leur) >= heure_attente(avant) else avant
    paires, _ = trois_voies(b, a, l, resout=plus_recente)
    entrees = [v for _, v in paires]
    return texte_attente([e for e in entrees if a.get(e[0]) == e]
                         + sorted((e for e in entrees if a.get(e[0]) != e), key=heure_attente))


def fusion_publie(projet, branche, textes, gardes, infos):
    """`publie` : la clé (page, nom) ; des empreintes différentes des deux côtés, la clé est retirée et dite — le joint
    sera republié. L'essai de `NUI16` : `merge=union` fait la même chose sauf là, où il garde les deux lignes."""
    b, a, l = (notes_publie((t or "").split("\n")) for t in textes)
    paires, desaccords = trois_voies(b, a, l, resout=lambda avant, leur: None)
    infos.extend("PUBLIE %s %s — empreintes différentes des deux côtés, clé retirée : le joint sera republié" % k
                 for k in desaccords)
    return texte_publie(dict(paires))


def lire_rev(projet, rev, chemin):
    """Le texte de `chemin` à `rev` — lu par `git show`, jamais dans l'arbre marqué — ou `None` s'il n'y est pas."""
    code, t = git_texte(["show", "%s:%s" % (rev, chemin)], projet)
    return t if code == 0 else None


def ecrire_comme(chemin, texte):
    """Écrit `texte` (fins de ligne `\\n`) dans `chemin`, en CRLF si le fichier qu'il remplace en avait."""
    crlf = False
    if os.path.isfile(chemin):
        with open(chemin, "rb") as fh:
            crlf = b"\r\n" in fh.read()
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        fh.write(texte.replace("\n", "\r\n") if crlf else texte)


def fusionner_fichiers(projet, branche, base, prevus, conflits, sortie):
    """Recalcule les fichiers de `prevus` = `[(chemin, fusion)]` que la fusion en cours a trouvés changés des deux côtés,
    depuis `base`, `HEAD` et `branche` : écrits et ajoutés (retirés, si la fusion les vide) ; un `GARDE:` laisse le
    chemin dans `conflits`. Un fichier absent des trois n'est ni écrit ni retiré. Rend la raison d'un échec de Git."""
    for chemin, fusion in prevus:
        textes = [lire_rev(projet, rev, chemin) for rev in (base, "HEAD", branche)]
        if textes[1] == textes[2] or textes[1] == textes[0] or textes[2] == textes[0]:
            continue
        gardes, infos = [], []
        texte = fusion(projet, branche, textes, gardes, infos)
        sortie.writelines("GARDE: %s : %s\n" % (chemin, g) for g in gardes)
        sortie.writelines(i + "\n" for i in infos)
        if gardes:
            conflits.add(chemin)
        if texte is None or gardes:
            continue
        complet = os.path.join(projet, chemin)
        if texte == "":
            if os.path.exists(complet):
                os.remove(complet)
            code, msg = git_texte(["rm", "-q", "--cached", "--ignore-unmatch", "--", chemin], projet)
        else:
            ecrire_comme(complet, texte)
            code, msg = git_texte(["add", "--", chemin], projet)
        if code != 0:
            return "%s : git %s" % (chemin, msg)
        conflits.discard(chemin)
    return None


def fusionner_branche(projet, branche, message, sortie):
    """Fusionne `branche` dans la branche du dossier — n'importe laquelle — et commite sous `message`, en réparant
    `CHANTIER.md` et la feuille. `True` à l'`ARRÊT` : la ligne est écrite, la fusion reste en cours ; `True` aussi
    sur la `GARDE:` d'un code pris deux fois, dite avant le merge, rien d'écrit (NUI27). `matin` et `fusionner`
    l'appellent (NUI26)."""
    chemin_carte, page = os.path.join(projet, "CHANTIER.md"), page_feuille(projet)
    archive = page_clos(projet)
    avec_archive = archive != page
    avant = lire(chemin_carte)
    carte_main, valeurs, liste_main = neutre(avant)
    courant_recu = courant_ou_rien(projet)     # avant le merge : le chantier de la branche qui reçoit (NUI31)
    liste_main = liste_main or ""     # `cmd_matin` a refusé un main sans sa ligne de lettres
    rang = None
    if os.path.isfile(page):
        try:
            html = lire(page)
            d, f, forme = zone_todo(html)
            rang = rang_en_cours(html[d:f], forme)
        except ValueError:
            pass

    def arret(raison):
        sortie.write("ARRÊT %s — %s\n" % (branche, raison))
        return True

    # un code pris des deux côtés sous deux titres : refusé avant le merge, rien d'écrit (NUI27)
    code_leur, texte_leur = git_texte(["show", "%s:CHANTIER.md" % branche], projet)
    carte_leur, _, liste_leur = neutre(texte_leur if code_leur == 0 else "")
    garde = doublon_lettres(liste_main.split(":", 1)[-1], (liste_leur or "").split(":", 1)[-1])
    if garde:
        sortie.write("%s — %s non fusionnée\n" % (garde, branche))
        return True

    code, msg = git_texte(["merge", "--no-ff", "--no-commit", branche], projet)
    if code not in (0, 1) or git_texte(["rev-parse", "-q", "--verify", "MERGE_HEAD"], projet)[0] != 0:
        return arret("fusion impossible : %s" % msg)
    code, t = git_texte(["diff", "--name-only", "--diff-filter=U"], projet)
    conflits = set(t.splitlines()) if code == 0 else set()

    # CHANTIER.md : les trois versions sans leurs libellés ni leurs lettres, fusionnées, puis les valeurs de `main`
    _, base = git_texte(["merge-base", "HEAD", branche], projet)
    code_base, texte_base = git_texte(["show", "%s:CHANTIER.md" % base.strip()], projet)
    carte_base = neutre(texte_base)[0] if code_base == 0 else ""
    pris = {lettre_entree(e) for e in entrees_lettres(liste_main.split(":", 1)[-1])}
    ajouts = []
    for e in entrees_lettres((liste_leur or "").split(":", 1)[-1]):
        lettre = lettre_entree(e)
        if lettre and lettre not in pris:
            pris.add(lettre)
            ajouts.append(e.strip())
    lettres = liste_main + "".join(", " + e for e in ajouts)
    code_fusion, fusion = fusion_texte(projet, [carte_base, carte_main, carte_leur], branche)
    if code_fusion is None:
        return arret("CHANTIER.md : %s" % fusion)
    # Le libellé reste celui de la branche qui reçoit, sauf si son chantier porte `**CLOS**` dans l'arbre fusionné :
    # clos dans un worktree, il ne bloque plus la principale — à `aucun`, comme `clore` (NUI26).
    chemin_recu = os.path.join(projet, courant_recu) if courant_recu else None
    if chemin_recu and os.path.isfile(chemin_recu) and any(l.startswith(MARQUE_CLOS) for l in lignes_de(chemin_recu)):
        # sa ligne a aussi quitté la TODO avec sa clôture : plus de badge « en cours » à remettre (dette NUI)
        valeurs, rang = {libelle: "aucun" for libelle in valeurs}, None
    ecrire_comme(chemin_carte, restaurer(fusion, valeurs, lettres))
    if code_fusion == 0:
        conflits.discard("CHANTIER.md")
        git_texte(["add", "CHANTIER.md"], projet)
    else:
        conflits.add("CHANTIER.md")

    # ce que `feuille` et `ecrire_couts` refont : jamais un conflit à résoudre à la main
    def rel(chemin):
        return os.path.relpath(chemin, projet).replace("\\", "/")
    dossier = os.path.dirname(os.path.abspath(page))
    derives = {rel(os.path.join(dossier, n)) for n in (COUTS_SVG,) + tuple(JOINTS)}
    if avec_archive:
        derives.add(rel(page))

    # les fichiers que les deux canaux réécrivent, par clé (NUI16) : avant la feuille, qui se lit dans la TODO fusionnée
    carte_lignes = avant.split("\n")
    index, etat = champ(carte_lignes, "index"), champ(carte_lignes, "fichier d'état")
    prevus = []
    if etat:
        prevus.append((etat, fusion_etat))
    prevus.append(("CLAUDE.md", fusion_claude))
    if index:
        prevus += [(index, fusion_index), (chemin_archive(index), fusion_archive_index)]
    if avec_archive:
        prevus.append((rel(archive), fusion_archive_clos))
    prevus += [(rel(os.path.join(dossier, nom)), f) for nom, f in (("en-attente", fusion_attente), (PUBLIE, fusion_publie))]
    raison = fusionner_fichiers(projet, branche, base.strip(), prevus, conflits, sortie)
    if raison:
        return arret(raison)
    for chemin in sorted(conflits & derives):
        code, msg = git_texte(["checkout", "--ours", "--", chemin], projet)
        if code != 0:
            return arret("conflit sur %s, celui de main non repris : %s" % (chemin, msg))
        conflits.discard(chemin)
    if conflits:
        suite = ' — après résolution : "%s" "%s" feuille "%s"%s' % (
            sys.executable, VLP_PY, projet, (" --todo %s" % rang) if rang else "")
        return arret("conflit : %s%s" % (", ".join(sorted(conflits)), suite))

    if os.path.isfile(page):
        try:
            neuf, _ = feuille(projet, lire(page), rang, datetime.date.today().isoformat())
            with open(page, "w", encoding="utf-8", newline="") as fh:
                fh.write(neuf)
            recopier_joints(dossier)
            if avec_archive:
                rafraichir_couts(projet, archive, lire(archive))
            else:
                ecrire_couts(page, neuf, couts_du_projet(projet, neuf))
        except ValueError as e:
            return arret("feuille : %s" % e)
    code, msg = git_texte(["add", "-A"], projet)
    if code != 0:
        return arret("git add : %s" % msg)
    code, msg = git_texte(["commit", "-q", "-m", message], projet)
    if code != 0:
        return arret("commit refusé : %s" % msg)
    sortie.write("FUSIONNÉE %s\n" % branche)
    return False


def projet_du_matin(a, sortie):
    """Le dossier absolu de `a.projet` si le matin peut y travailler — équipé, date lisible, racine d'un dépôt Git —,
    sinon None, après une `GARDE:`. Les trois gardes de `matin` et de `matin --rapport`."""
    projet = os.path.abspath(a.projet)
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return None
    try:
        if a.date is not None:    # sans date, `matin` la cherche (`nuit_a_ranger`) après ses gardes
            datetime.date.fromisoformat(a.date)
    except ValueError:
        sortie.write("GARDE: AAAA-MM-JJ attendu : %s\n" % a.date)
        return None
    return projet if racine_du_depot(projet, sortie) else None


def racine_du_depot(projet, sortie):
    """Vrai si `projet` est la racine de son dépôt Git, sinon une `GARDE:` (rien fusionné) : `matin` et `fusionner`."""
    code, haut = git_texte(["rev-parse", "--show-toplevel"], projet)
    try:
        racine = code == 0 and os.path.samefile(haut.strip(), projet)
    except OSError:
        racine = False
    if not racine:
        sortie.write("GARDE: %s n'est pas la racine d'un dépôt Git — rien fusionné\n" % projet)
    return racine


# Le sujet du commit d'un chantier mis de côté par la nuit (`mettre_de_cote`, boucle.py, qui l'importe) et son
# motif de lecture : `de_cote` le relit, une pointe WIP n'est jamais fusionnée (NUI24).
WIP_SUJET = "WIP %s mis de côté : %s"
WIP_MOTIF = re.compile(r"^WIP \S+ mis de côté : ")


def de_cote(projet, branche):
    """Ce qui met `branche` de côté — `matin` ne la fusionne jamais —, ou None : le chantier ouvert qu'elle ajoute
    (`courant_de`, lu dans son commit : un chantier hérité de la principale ne compte pas), sinon le sujet de sa
    pointe s'il suit `WIP_SUJET` — un découpage coupé avant `ouvrir` laisse un WIP sans chantier (NUI24). Plusieurs
    ouverts : leur liste. `matin` et `matin --rapport` l'appellent."""
    try:
        courant = courant_de(projet, rev=branche)
    except Absent as e:
        return str(e)
    if courant:
        return courant
    code, sujet = git_texte(["log", "-1", "--format=%s", branche], projet)
    return sujet.strip() if code == 0 and WIP_MOTIF.match(sujet.strip()) else None


def etat_branche_nuit(projet, branche):
    """Ce que `matin` fait de `branche` : `("deja", None)` si elle est ancêtre de `HEAD`, `("cote", <chantier ouvert>)`
    si son `CHANTIER.md` garde un chantier ouvert (`de_cote`), sinon `("fusion", None)`."""
    if git_texte(["merge-base", "--is-ancestor", branche, "HEAD"], projet)[0] == 0:
        return "deja", None
    courant = de_cote(projet, branche)
    return ("cote", courant) if courant else ("fusion", None)


NUIT_BRANCHE = re.compile(r"nuit/(\d{4}-\d{2}-\d{2})-")


def nuit_a_ranger(projet, sortie):
    """La date de la nuit que `matin` range quand on ne lui en donne pas : la seule qui a une branche à fusionner
    (`etat_branche_nuit`), dite par `NUIT <date> — la seule à ranger : <n> branche(s)`. Aucune, ou plusieurs (leurs
    dates, la plus ancienne d'abord) : None, après une `GARDE:`."""
    code, t = git_texte(["for-each-ref", "--format=%(refname)", "refs/heads/nuit/*"], projet)
    if code != 0:
        sortie.write("GARDE: %s — rien fusionné\n" % t.strip())
        return None
    a_ranger, vues = {}, 0
    for ref in sorted(t.splitlines()):
        branche = ref[len("refs/heads/"):]
        nuit = NUIT_BRANCHE.match(branche)
        if nuit:
            vues += 1
            if etat_branche_nuit(projet, branche)[0] == "fusion":
                a_ranger.setdefault(nuit.group(1), []).append(branche)
    if len(a_ranger) == 1:
        date, branches = next(iter(a_ranger.items()))
        sortie.write("NUIT %s — la seule à ranger : %d branche(s)\n" % (date, len(branches)))
        return date
    if a_ranger:
        sortie.write("GARDE: plusieurs nuits à ranger : %s — rien fusionné ; donne la date\n" % ", ".join(
            "%s (%d)" % (d, len(b)) for d, b in sorted(a_ranger.items())))
    else:
        sortie.write("GARDE: aucune nuit à ranger (%d branche(s) nuit/* déjà fusionnée(s) ou de côté) — rien fusionné\n" % vues)
    return None


def cmd_matin(a, sortie):
    """`matin <projet> [<date>]` : les gardes, la nuit (la date donnée, sinon `nuit_a_ranger`), l'ordre, puis chaque
    branche de la nuit — `DÉJÀ`, `DE CÔTÉ` ou fusionnée. `--rapport` veut la date : sans elle, `GARDE:`."""
    if a.rapport:
        if a.date is None:
            sortie.write("GARDE: --rapport veut la date de la nuit (celle que `matin` a dite : NUIT <date>)\n")
            return 1
        return cmd_matin_rapport(a, sortie)
    projet = projet_du_matin(a, sortie)
    if projet is None:
        return 1
    code, tete = git_texte(["symbolic-ref", "--short", "-q", "HEAD"], projet)
    if code != 0 or tete.strip() != "main":
        sortie.write("GARDE: HEAD est sur %s, pas sur main — rien fusionné\n" % (tete.strip() if code == 0 else "rien (détaché)"))
        return 1
    code, sale = git_texte(["status", "--porcelain"], projet)
    if code != 0 or sale.strip():
        sortie.write("GARDE: arbre pas propre (%s) — rien fusionné\n" % (
            "%d chemin(s)" % len(sale.splitlines()) if code == 0 else sale))
        return 1
    _, valeurs, liste = neutre(lire(os.path.join(projet, "CHANTIER.md")))
    if liste is None or not valeurs:
        sortie.write("GARDE: CHANTIER.md de main sans sa ligne « artefact du chantier » ou « %s » — rien fusionné\n"
                     % LETTRES)
        return 1
    date = a.date if a.date is not None else nuit_a_ranger(projet, sortie)
    if date is None:
        return 1
    pointes, erreur = pointes_nuit(projet, date)
    if not pointes:
        sortie.write("GARDE: %s — rien fusionné\n" % (erreur or "aucune branche nuit/%s-* (la date est-elle juste ?)" % date))
        return 1
    branches, lu = ordre_nuit(pointes, date, projet)
    if not lu:
        sortie.write("ORDRE pointes — carnet absent\n")
    _, avant = git_texte(["rev-parse", "HEAD"], projet)
    fusionnees = cote = 0
    for branche in branches:
        etat, courant = etat_branche_nuit(projet, branche)
        if etat == "deja":
            sortie.write("DÉJÀ %s\n" % branche)
            continue
        if etat == "cote":
            sortie.write("DE CÔTÉ %s — %s\n" % (branche, courant))
            cote += 1
            continue
        if fusionner_branche(projet, branche, "Matin %s : %s" % (date, branche), sortie):
            return 1
        fusionnees += 1
    retard_du_matin(projet, avant.strip(), sortie)
    dire_attentes(projet, sortie)
    sortie.write("MATIN %d fusionnée(s) · %d de côté\n" % (fusionnees, cote))
    return 0


def retard_du_matin(projet, avant, sortie):
    """Écrire `PLUGIN_RETARD=<n> …` : `n` commits fusionnés depuis `avant` qui touchent `CODE_PLUGIN`, quand `projet`
    est le kit chargé (`KIT`) — la session ouverte a lu ses commandes avant la fusion (RTD1). Rien pour un autre
    projet, aucun commit, ou Git muet."""
    if not avant or os.path.normcase(os.path.realpath(projet)) != os.path.normcase(os.path.realpath(KIT)):
        return
    code, n = git_texte(["rev-list", "--count", "%s..HEAD" % avant, "--"] + list(CODE_PLUGIN), projet)
    if code == 0 and n.strip().isdigit() and int(n) > 0:
        sortie.write("PLUGIN_RETARD=%d commit(s) de code du plugin fusionné(s) — la session ouverte ne les voit "
                     "qu'après /reload-plugins\n" % int(n))


def cmd_fusionner(a, sortie):
    """`fusionner <projet> <branche>` (NUI26) : la fusion du jour, `branche` dans celle du dossier, par
    `fusionner_branche` sous « Fusion : <branche> ». Gardes, rien fusionné : non équipé ou hors racine, `HEAD`
    détachée, `MERGE_HEAD` présent, arbre sale, branche absente, branche qui garde un chantier ouvert (`de_cote`)."""
    projet = os.path.abspath(a.projet)
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s — rien fusionné\n" % projet)
        return 1
    if not racine_du_depot(projet, sortie):
        return 1
    if git_texte(["symbolic-ref", "--short", "-q", "HEAD"], projet)[0] != 0:
        sortie.write("GARDE: HEAD détachée — rien fusionné\n")
        return 1
    if git_texte(["rev-parse", "-q", "--verify", "MERGE_HEAD"], projet)[0] == 0:
        sortie.write("GARDE: une fusion est déjà en cours (MERGE_HEAD) — rien fusionné\n")
        return 1
    code, sale = git_texte(["status", "--porcelain"], projet)
    if code != 0 or sale.strip():
        sortie.write("GARDE: arbre pas propre (%s) — rien fusionné\n" % (
            "%d chemin(s)" % len(sale.splitlines()) if code == 0 else sale))
        return 1
    if git_texte(["rev-parse", "-q", "--verify", "%s^{commit}" % a.branche], projet)[0] != 0:
        sortie.write("GARDE: branche absente : %s — rien fusionné\n" % a.branche)
        return 1
    if git_texte(["merge-base", "--is-ancestor", a.branche, "HEAD"], projet)[0] == 0:
        sortie.write("DÉJÀ %s\n" % a.branche)
        return 0
    ouvert = de_cote(projet, a.branche)
    if ouvert:
        sortie.write("GARDE: %s garde un chantier ouvert (%s) — clos-le dans son worktree d'abord, rien fusionné\n"
                     % (a.branche, ouvert))
        return 1
    return 1 if fusionner_branche(projet, a.branche, "Fusion : %s" % a.branche, sortie) else 0


# --- matin --rapport : le carnet complété, la table des nuits, la page du matin (chantier NUI, fiche NUI19) ------------
# Après la fusion : rien de commité, rien de fusionné, et rejoué, le carnet et le fichier des nuits ne changent plus.

def mesure_session_kit(session):
    """`(usd_kit, tours_kit, raison)` d'une session du carnet : `resoudre`, puis `mesurer` sur son transcript et sur chacun
    de ses `sous_agents`, `usd_exact` et `tours` sommés comme `parts_aux_commits` (un `usd_exact` None rend None), le
    prix arrondi une fois au centime. Transcript introuvable ou illisible, modèle hors `GRILLE` : `(None, None, raison)`
    — jamais 0."""
    from decimal import ROUND_HALF_UP, Decimal
    m = mesure()
    chemin, _ = m.resoudre(session)
    if chemin is None:
        return None, None, "transcription introuvable"
    usd, tours, inconnus = Decimal(0), 0, []
    for transcript in [chemin] + m.sous_agents(chemin):
        r, erreur = m.mesurer(transcript)
        if r is None:
            return None, None, "transcription illisible (%s)" % erreur
        tours += r["tours"]
        usd = None if usd is None or r["usd_exact"] is None else usd + r["usd_exact"]
        inconnus += r["inconnus"]
    if usd is None:
        return None, None, "modèle hors grille (%s)" % ", ".join(sorted(set(inconnus)))
    return float(usd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), tours, None


def completer_kit(chemin, sortie):
    """Donne `usd_kit` et `tours_kit` à chaque ligne de session du carnet `chemin` qui n'a pas `usd_kit`
    (`mesure_session_kit`) : mesurées d'abord, hors verrou, puis écrites d'un coup sous celui du carnet
    (`carnet.mettre_a_jour`). Une session non mesurée : `KIT ? <session> — <raison>` sur `sortie`, aucune clé `_kit`.
    Rend le nombre de lignes complétées."""
    mesures = {}
    for d in carnet.lire(chemin):
        s = d.get("session")
        if carnet.est_session(d) and d.get("usd_kit") is None and s not in mesures:
            mesures[s] = mesure_session_kit(s) if s else (None, None, "pas d'id de session au carnet")
            if mesures[s][0] is None:
                sortie.write("KIT ? %s — %s\n" % (s or "(sans id)", mesures[s][2]))

    def poser(d):
        m = mesures.get(d.get("session"))
        if carnet.est_session(d) and d.get("usd_kit") is None and m and m[0] is not None:
            return {"usd_kit": m[0], "tours_kit": m[1]}
        return None
    return carnet.mettre_a_jour(chemin, poser)


def bilan_chantiers(lignes):
    """Un dict par `(canal, chantier)` du carnet, dans l'ordre où ils y apparaissent : `jouees` (les fiches qu'une session
    `jouer` ou `relance` a prises), `acceptees` (celles qu'une session `relire` sans `refus_n` a prises, comme
    `taux_nuit`), `refusees` (celles qu'une `relire` à `refus_n` a prises : refusée puis acceptée compte aux deux),
    `issues` (`issue` : nombre de sessions), `relances`, `modeles` (`modeles_vus`, sans doublon), `retard`
    (`plugin_retard` de la dernière ligne qui en porte un), `usd` et `tours` (les sommes des `usd_kit` et `tours_kit`
    — jamais des `_cli`), `sans` (les sessions qui n'ont pas de `usd_kit`)."""
    bilans = {}
    for d in lignes:
        if not d.get("canal") or not d.get("chantier"):
            continue
        b = bilans.setdefault((d["canal"], d["chantier"]), {
            "canal": d["canal"], "chantier": d["chantier"], "jouees": set(), "acceptees": set(), "refusees": set(),
            "issues": collections.Counter(), "relances": 0, "modeles": [], "retard": None, "usd": 0.0, "tours": 0,
            "sans": 0})
        if d.get("plugin_retard") is not None:
            b["retard"] = d["plugin_retard"]
        if not carnet.est_session(d):
            continue
        role, fiche = d.get("role"), d.get("fiche")
        if role in ("jouer", "relance") and fiche:
            b["jouees"].add(fiche)
        if role == "relire" and fiche:
            b["refusees" if d.get("refus_n") else "acceptees"].add(fiche)
        b["relances"] += role == "relance"
        if d.get("issue"):
            b["issues"][d["issue"]] += 1
        b["modeles"] += [x for x in (d.get("modeles_vus") or []) if x not in b["modeles"]]
        if d.get("usd_kit") is None:
            b["sans"] += 1
        else:
            b["usd"] += d["usd_kit"]
            b["tours"] += d.get("tours_kit") or 0
    return list(bilans.values())


def cout_du_bilan(b, avec_unite=True):
    """La somme des `usd_kit` d'un bilan comme `4,50 $` ; `≥ 4,50 $` si des sessions n'en ont pas, `?` si aucune."""
    if b["sans"] and not b["usd"]:
        return "?"
    texte = ("%.2f" % b["usd"]).replace(".", ",")
    return ("≥ " if b["sans"] else "") + texte + (" $" if avec_unite else "")


def ecrire_table_nuits(projet, nuit, bilans):
    """Une ligne de table au fichier des nuits (`fichier_nuits(creer=True)`) par `(nuit, canal, chantier)` absente :
    `| <nuit> | <canal> | <chantier> | <jouées>/<acceptées>/<refusées> | <$> |`, le `$` étant `cout_du_bilan`. Une
    ligne déjà là n'est pas refaite. Rend `(chemin, nombre de lignes ajoutées)` ; `ValueError` : `fichier_nuits` ou
    `nuits_ecrire` refusent."""
    chemin = fichier_nuits(projet, creer=True)
    assert chemin
    rangees, _ = nuits_du_fichier(lignes_de(chemin))
    ajoutees = 0
    for b in bilans:
        deja = any(r[:3] == [nuit, b["canal"], b["chantier"]] for r in rangees)
        if deja:
            continue
        ligne = "| %s | %s | %s | %d/%d/%d | %s |" % (nuit, b["canal"], b["chantier"], len(b["jouees"]),
                                                      len(b["acceptees"]), len(b["refusees"]),
                                                      cout_du_bilan(b, avec_unite=False))
        ajoutees += nuits_ecrire(chemin, ligne)
    return chemin, ajoutees


def derniere_valeur(lignes, cle):
    """La dernière valeur non vide de `cle` parmi `lignes`, en texte, ou None."""
    return next((str(d[cle]) for d in reversed(lignes) if d.get(cle)), None)


def chantiers_de_cote(projet, date, lignes):
    """`([{canal, chantier, branche, raison, cause, reecriture, dependants, ecart}], [ÉCART])` : les chantiers mis de côté
    selon Git — la branche `nuit/<date>-<canal>-<code>` qui n'est pas dans `HEAD` et dont `de_cote` dit qu'elle garde un
    chantier ouvert — et selon le carnet — une garde `mis-de-cote:<raison>`, ses `cause` et `reecriture`, les chantiers
    dont une garde `saute:<code>` dit qu'ils en dépendaient (NUI7). Les deux se croisent : l'un le dit de côté, pas
    l'autre, c'est un `ÉCART` — dit, jamais tranché."""
    pointes, _ = pointes_nuit(projet, date)
    prefixe = "nuit/%s-" % date
    git_cote = {}
    for branche, _ in pointes or []:
        canal, _, code = branche[len(prefixe):].partition("-")
        if git_texte(["merge-base", "--is-ancestor", branche, "HEAD"], projet)[0] != 0 and de_cote(projet, branche):
            git_cote[(canal, code)] = branche
    raisons = {}
    for d in lignes:
        garde = str(d.get("garde") or "")
        if garde.startswith("mis-de-cote:") and d.get("chantier"):
            raisons[(d.get("canal"), d["chantier"])] = garde[len("mis-de-cote:"):]
    cotes, ecarts = [], []
    for cle in list(raisons) + [k for k in git_cote if k not in raisons]:
        canal, code = cle
        propres = [d for d in lignes if d.get("canal") == canal and d.get("chantier") == code]
        ecart = None
        if cle not in git_cote:
            ecart = "le carnet le met de côté, Git non (branche absente, déjà dans main, ou chantier fermé sur elle)"
        elif cle not in raisons:
            ecart = "Git le met de côté, le carnet n'a aucune ligne mis-de-cote"
        if ecart:
            ecarts.append("ÉCART %s-%s — %s" % (canal, code, ecart))
        cotes.append({"canal": canal, "chantier": code, "branche": "%s%s-%s" % (prefixe, canal, code),
                      "raison": raisons.get(cle), "cause": derniere_valeur(propres, "cause"),
                      "reecriture": derniere_valeur(propres, "reecriture"),
                      "dependants": [x for x in dict.fromkeys(
                          d["chantier"] for d in lignes
                          if d.get("chantier") and str(d.get("garde") or "") == "saute:%s" % code)],
                      "ecart": ecart})
    return cotes, ecarts


def option_matin(valeur, libelle, effet):
    return {"valeur": valeur, "libelle": libelle, "effet": effet, "recommande": False}


def question_de_cote(c):
    """La carte d'un chantier mis de côté : ce que le carnet et Git en disent, et les trois réponses du socle."""
    puces = ["Branche : `%s`" % c["branche"], "Raison au carnet : %s" % (c["raison"] or "aucune")]
    if c["cause"]:
        puces.append("Cause du dernier refus : %s" % c["cause"])
    if c["reecriture"]:
        puces.append("Réécriture demandée : %s" % c["reecriture"])
    puces.append("Chantiers sautés à cause de lui : %s" % (", ".join(c["dependants"]) or "aucun"))
    if c["ecart"]:
        puces.append("**ÉCART** : %s" % c["ecart"])
    return {"titre": "Mis de côté : %s (canal %s)" % (c["chantier"], c["canal"]), "puces": puces, "options": [
        option_matin("reprendre", "Reprendre à la main", "Tu reprends la branche `%s` toi-même ; je ne touche à rien "
                     "d'autre." % c["branche"]),
        option_matin("abandonner", "Abandonner", "Le travail de la branche est perdu : je te donne `git branch -D %s`, "
                     "je ne la lance jamais." % c["branche"]),
        option_matin("rejouer", "Rejouer une nuit", "Je te donne aussi `git branch -D %s` : la nuit suivante repart de "
                     "`main`. La ligne de la TODO reste, le tri du soir la reprend." % c["branche"])]}


def question_de_note(canal, texte, sorte):
    """La carte d'une note du carnet selon sa `sorte` : un reste (trois réponses, le premier oui de
    `methode-chantier.md`), ou une case du menu de fin de `cloture.md` (faire ou laisser)."""
    puces = ["Note du canal %s : %s" % (canal or "?", texte)]
    if sorte == "reste":
        return {"titre": "Reste à verser dans la TODO ?", "puces": puces + [
            "La TODO ne grossit pas sans deux oui : celui-ci est le premier, la ligne écrite sera le second."], "options": [
            option_matin("verser", "Verser", "Je t'écris la ligne et te la montre : elle ne part qu'après ton second oui."),
            option_matin("fondre", "Fondre dans une entrée existante", "Tu me nommes laquelle ; rien ne grossit."),
            option_matin("abandonner", "Abandonner", "Rien n'est écrit : abandonner est une réponse normale.")]}
    titre, faire = (("Case 3 du menu de fin : essaimer", "Je lance `niveau` sur les autres projets équipés, comme "
                     "`cloture.md` le dit.") if sorte == "case3" else
                    ("Case 4 du menu de fin : la dette repérée", "Petite : une tâche et un commit à elle. Plus grosse : "
                     "présentée comme un chantier (`cloture.md`)."))
    return {"titre": titre, "puces": puces, "options": [
        option_matin("faire", "Faire", faire),
        option_matin("laisser", "Laisser", "Rien n'est fait ; la note reste au carnet.")]}


def rapport_matin(projet, date, bilans, cotes, lignes, kit_sans):
    """Le JSON de `chef page --questions` du matin : une ligne `fait` par chantier du carnet (issues, relances, modèles
    vus, `plugin_retard`, coût `_kit` — jamais `_cli`), une carte par chantier mis de côté, une par note selon sa `sorte`,
    et `NOTE SANS SORTE` en alerte pour les autres. `kit_sans` : les lignes `KIT ?`, en puces."""
    notes = [d for d in lignes if carnet.est_note_matin(d)]
    fait, choix, mal = [], [question_de_cote(c) for c in cotes], []
    for b in bilans:
        issues = ", ".join("%s ×%d" % (k, n) for k, n in b["issues"].items()) or "aucune session"
        livre = " · ".join(x for x in (
            "issues : %s" % issues, "relances : %d" % b["relances"],
            "modèles vus : %s" % ", ".join(b["modeles"]) if b["modeles"] else None,
            "plugin en retard : %s commit(s)" % b["retard"] if b["retard"] else None) if x)
        fait.append({"ref": b["canal"], "code": b["chantier"], "livre": livre,
                     "titre": "%d jouée(s) · %d acceptée(s) · %d refusée(s)" % (len(b["jouees"]), len(b["acceptees"]),
                                                                              len(b["refusees"])),
                     "cout": "%s · %d tours" % (cout_du_bilan(b), b["tours"])})
    for d in notes:
        if d.get("sorte") in carnet.SORTES:
            choix.append(question_de_note(d.get("canal"), str(d["note"]), d["sorte"]))
        else:
            mal.append({"genre": "alerte", "titre": "NOTE SANS SORTE", "texte":
                        "%s (canal %s) — le matin ne sait pas quoi en faire : à classer à la main." % (
                            d["note"], d.get("canal") or "?")})
    rapport = {"projet": nom_du_projet(projet), "sujet": "matin", "titre": "Le matin du %s" % date, "date": date,
               "puces": ["%d chantier(s) au carnet · %d mis de côté · %d note(s) pour le matin"
                         % (len(bilans), len(cotes), len(notes))] + kit_sans}
    for cle, valeur in (("fait", fait), ("choix", choix), ("mal", mal)):
        if valeur:
            rapport[cle] = valeur
    return rapport


def cmd_matin_rapport(a, sortie):
    """`matin <projet> <date> --rapport <json>` : sans fusion ni commit, rejouable. Complète le carnet de la nuit
    (`completer_kit`), range une ligne par chantier au fichier des nuits (`ecrire_table_nuits`), puis écrit le JSON de
    `chef page --questions` (`rapport_matin`). Mêmes gardes que `matin` : équipé, date, racine du dépôt ; carnet absent
    ou vide, ou fichier des nuits illisible : `GARDE:`, sort 1."""
    projet = projet_du_matin(a, sortie)
    if projet is None:
        return 1
    chemin = carnet.du_jour(projet, a.date)
    if not chemin or not carnet.lire(chemin):
        sortie.write("GARDE: carnet de la nuit %s absent ou vide — pas de rapport\n" % a.date)
        return 1
    manques = io.StringIO()
    try:
        completer_kit(chemin, manques)
    except ValueError as e:
        sortie.write("GARDE: carnet %s — %s\n" % (chemin, e))
        return 1
    sortie.write(manques.getvalue())
    lignes = carnet.lire(chemin)
    bilans = bilan_chantiers(lignes)
    try:
        nuits, ajoutees = ecrire_table_nuits(projet, a.date, bilans)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("NUITS %s · %d ligne(s) ajoutée(s)\n" % (os.path.relpath(nuits, projet).replace("\\", "/"), ajoutees))
    cotes, ecarts = chantiers_de_cote(projet, a.date, lignes)
    for e in ecarts:
        sortie.write(e + "\n")
    rapport = rapport_matin(projet, a.date, bilans, cotes, lignes, manques.getvalue().splitlines())
    for d in lignes:
        if carnet.est_note_matin(d) and d.get("sorte") not in carnet.SORTES:
            sortie.write("NOTE SANS SORTE %s — %s\n" % (d.get("canal") or "?", d["note"]))
    try:
        with open(a.rapport, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rapport, f, ensure_ascii=False, indent=1)
            f.write("\n")
    except OSError as e:
        sortie.write("GARDE: %s — écriture impossible : %s\n" % (a.rapport, e))
        return 1
    sortie.write("RAPPORT %s · %d chantier(s) · %d mis de côté · %d carte(s)\n" % (
        a.rapport, len(bilans), len(cotes), len(rapport.get("choix", []))))
    return 0


def cmd_nuits_lecon(ligne, projet, sortie):
    """`nuits lecon "<ligne>"` : une leçon sous `## Leçons` du fichier des nuits (`fichier_nuits(creer=True)`). Hors de la
    forme de `LECON_FORME`, ou fichier illisible : `GARDE:`, sort 1, rien d'écrit. Déjà là : `LEÇON déjà là`."""
    try:
        if not LECON_FORME.match(ligne):
            raise ValueError("leçon hors forme : %s" % ligne)
        chemin = fichier_nuits(os.path.abspath(projet), creer=True)
        assert chemin
        ajoutee = nuits_ecrire(chemin, ligne)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("LEÇON %s · %s\n" % (os.path.relpath(chemin, projet).replace("\\", "/"), "ajoutée" if ajoutee else "déjà là"))
    return 0


DELAI_MUTANT = 1800     # secondes : passé ce délai, la suite d'un mutant est tuée et dite PLANTÉ


def texte_mute(fichier, avant, apres):
    """Lire `fichier` et rendre (ses octets, son texte où `avant` devient `apres`) ; les `\\n` des deux suivent
    la fin de ligne du fichier, et `avant` doit y être une fois exactement — sinon `ValueError`."""
    with open(fichier, "rb") as f:
        octets = f.read()
    texte = octets.decode("utf-8")
    nl = "\r\n" if "\r\n" in texte else "\n"
    avant, apres = (x.replace("\r\n", "\n").replace("\n", nl) for x in (avant, apres))
    n = texte.count(avant) if avant else 0
    if n != 1:
        raise ValueError("« avant » trouvé %d fois dans %s — il en faut exactement 1, rien écrit" % (n, fichier))
    return octets, texte.replace(avant, apres)


def kit_de(fichier):
    """Rendre la racine du premier kit (`est_kit`) en remontant depuis le dossier de `fichier`, `None` hors de tout
    kit : un worktree du kit est son propre kit, même rangé sous le dépôt principal (MUW1)."""
    d = os.path.dirname(os.path.abspath(fichier))
    while not est_kit(d):
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)
    return d


def copie_mutee(fichier, mute, dossier):
    """Copier sous `dossier` le kit qui contient `fichier` (`kit_de`) — ou, hors de tout kit, `KIT` s'il le contient,
    sinon le dossier de `fichier` —, sans `MUTANT_EXCLUS`, puis y écrire `mute` à la place de `fichier` ; rendre
    (la racine copiée, sa copie). Le vrai fichier n'est jamais écrit."""
    import shutil
    fichier = os.path.abspath(fichier)
    try:
        dans_kit = os.path.commonpath([os.path.normcase(KIT), os.path.normcase(fichier)]) == os.path.normcase(KIT)
    except ValueError:      # deux lecteurs différents
        dans_kit = False
    racine = kit_de(fichier) or (KIT if dans_kit else os.path.dirname(fichier))
    copie = os.path.join(dossier, "kit")

    def exclus(r, noms):
        """Rendre les noms de `r` que la copie laisse de côté."""
        rel = os.path.relpath(r, racine).replace(os.sep, "/")
        return [n for n in noms if n in MUTANT_EXCLUS or (rel == "evals" and n == "results")]

    shutil.copytree(racine, copie, ignore=exclus)
    with open(os.path.join(copie, os.path.relpath(fichier, racine)), "wb") as f:
        f.write(mute.encode("utf-8"))
    return racine, copie


def vers_copie(commande, racine, copie):
    """Rendre `commande` (chaîne ou liste) où chaque chemin sous `racine`, en barres obliques ou inverses, pointe
    sous `copie` : une commande déjà écrite pour le vrai kit joue la copie."""
    if not isinstance(commande, str):
        return [vers_copie(x, racine, copie) for x in commande]
    for r, c in {(racine, copie), (racine.replace("\\", "/"), copie.replace("\\", "/"))}:
        commande = re.sub(re.escape(r) + r"(?![^\\/\s\"'])", lambda _m, c=c: c, commande,
                          flags=re.I if os.name == "nt" else 0)
    return commande


def tuer_arbre(p):
    """Tuer le processus `p` et ses descendants : `taskkill /T` sous Windows, son groupe de session ailleurs."""
    import subprocess
    if p.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    else:
        import signal
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def jouer_suite(commande, dossier, attendu):
    """Jouer `commande` dans `dossier` avec `VLP_TOUS_ECARTS=1`, sa sortie lue ligne à ligne ; avec `attendu`, tuer
    l'arbre de processus dès l'`ÉCART:` dont le libellé commence par lui. Rendre (lignes, code de sortie, attrapé) ;
    passé `DELAI_MUTANT`, l'arbre est tué et une ligne `DÉLAI:` le dit."""
    import subprocess
    import threading
    env = dict(os.environ, VLP_TOUS_ECARTS="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONUNBUFFERED="1")
    p = subprocess.Popen(commande, shell=isinstance(commande, str), cwd=dossier, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, encoding="utf-8", errors="replace",
                         start_new_session=sys.platform != "win32")
    lignes, attrape = [], False

    def expirer():
        """Tuer la suite trop longue, et le noter."""
        lignes.append("DÉLAI: %d s dépassé, suite tuée" % DELAI_MUTANT)
        tuer_arbre(p)

    minuteur = threading.Timer(DELAI_MUTANT, expirer)
    minuteur.start()
    try:
        for ligne in p.stdout or ():
            lignes.append(ligne.rstrip("\n"))
            if attendu and ligne.startswith("ÉCART:") and ligne[len("ÉCART:"):].strip().startswith(attendu):
                attrape = True
                tuer_arbre(p)
                break
    finally:
        minuteur.cancel()
    return lignes, p.wait(), attrape


def effacer_copie(dossier):
    """Effacer `dossier`, en réessayant 2 s : un processus tué peut le tenir encore un instant ; rendre `True` s'il
    a disparu."""
    import shutil
    for _ in range(10):
        shutil.rmtree(dossier, ignore_errors=True)
        if not os.path.exists(dossier):
            return True
        time.sleep(0.2)
    return False


def verdict_mutant(lignes, code, attrape, attendu):
    """Rendre (texte, code de sortie) : les `ÉCART:` vus, puis `MUTANT ATTRAPÉ`, `VIVANT` ou `PLANTÉ`. Une suite
    finie sort 0 ou dit `OK` ou `FIN:` en dernière ligne ; arrêtée avant, elle est `PLANTÉ`, écarts vus ou non."""
    ecarts = [l for l in lignes if l.startswith("ÉCART:")]
    texte = "".join(l + "\n" for l in ecarts)
    fin = next((l.strip() for l in reversed(lignes) if l.strip()), "")
    if attrape:
        return texte + "MUTANT ATTRAPÉ %d écart(s) · arrêté sur « %s »\n" % (len(ecarts), attendu), 0
    if not (code == 0 or fin == "OK" or fin.startswith("FIN:")):
        dernieres = [l.strip() for l in lignes if l.strip()][-3:]
        return texte + "MUTANT PLANTÉ · tests sortis %d sans finir, après %d écart(s) — %s\n" % (
            code, len(ecarts), " / ".join(dernieres)), 1
    if attendu:
        return texte + "MUTANT VIVANT pour %s\n" % attendu, 1
    if ecarts:
        return texte + "MUTANT ATTRAPÉ %d écart(s)\n" % len(ecarts), 0
    return texte + "MUTANT VIVANT\n", 1


def jouer_mutant(commande, copie, attendu, vise):
    """Jouer les tests `commande` dans `copie` et rendre (texte, code de sortie) de leur verdict (`verdict_mutant`).
    Avec `vise` — pas de `--test` — et `attendu` (VIT21), d'abord les seuls groupes de `test-vlp.py` qui portent
    `attendu` (`--seul`) : l'écart attendu tombé là, une ligne `VISÉ` le dit ; sinon — aucun groupe, ou pas cet
    écart —, la suite entière tranche, et une ligne `SUITE ENTIÈRE` le dit. Un ATTRAPÉ ne vient que de l'écart
    attendu, un VIVANT que de la suite entière."""
    tete = ""
    if vise and attendu:
        lignes, code, attrape = jouer_suite(commande + ["--seul", attendu], copie, attendu)
        if attrape:
            texte, code = verdict_mutant(lignes, code, attrape, attendu)
            return "VISÉ --seul « %s »\n" % attendu + texte, code
        aucun = any(l.startswith("GARDE: aucun groupe") for l in lignes)
        tete = "SUITE ENTIÈRE · %s\n" % (("aucun groupe ne porte « %s »" if aucun
                                          else "« %s » n'est pas tombé dans ses groupes") % attendu)
    texte, code = verdict_mutant(*jouer_suite(commande, copie, attendu), attendu)
    return tete + texte, code


def cmd_mutant(a, sortie):
    """Casser `a.cible` exprès (`a.avant` → `a.apres`, une seule occurrence) dans une copie du kit, y jouer les
    tests, et dire si le mutant est attrapé — avec `a.attendu`, arrêtés dès cet écart (chantiers MUT, VIT2), et sans
    `a.test`, d'abord sur ses seuls groupes (`jouer_mutant`, VIT21). Le vrai fichier n'est jamais écrit : `RENDU`
    imprime son empreinte, la même qu'avant."""
    import subprocess
    try:
        octets, mute = texte_mute(a.cible, lire_arg(a.avant), lire_arg(a.apres))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    empreinte = hashlib.sha1(octets).hexdigest()[:12]
    dossier = tempfile.mkdtemp(prefix="vlp-mutant-")
    try:
        racine, copie = copie_mutee(a.cible, mute, dossier)
        suite = os.path.join(racine if est_kit(racine) else KIT, "scripts", "test-vlp.py")
        commande = vers_copie(a.test or [sys.executable, suite], racine, copie)
        texte, code = jouer_mutant(commande, copie, a.attendu, vise=not a.test)
        if not a.test:
            texte += "TESTS %s\n" % os.path.dirname(os.path.dirname(suite))
    except (OSError, subprocess.SubprocessError) as e:
        texte, code = "GARDE: les tests ne se lancent pas : %s\n" % e, 1
    finally:
        restee = not effacer_copie(dossier)
    sortie.write(texte + ("COPIE restée : %s\n" % dossier if restee else ""))
    with open(a.cible, "rb") as f:
        rendu = hashlib.sha1(f.read()).hexdigest()[:12]
    if rendu != empreinte:
        sortie.write("GARDE: %s a bougé pendant le mutant : %s avant, %s après\n" % (a.cible, empreinte, rendu))
        return 1
    sortie.write("RENDU %s\n" % rendu)
    return code


def entrees_launch(texte):
    """(index après le `[`, index du `]`, [(début, fin, entrée)]) du tableau `configurations` de
    `launch.json`, lu sur le texte : on y greffe une entrée sans réécrire les voisines. `None` :
    illisible, ou pas de tableau."""
    try:
        attendu = json.loads(texte)["configurations"]
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(attendu, list):
        return None
    lecteur = json.JSONDecoder()

    def apres_blancs(pos):
        while pos < len(texte) and texte[pos].isspace():
            pos += 1
        return pos

    for m in re.finditer(r'"configurations"\s*:\s*\[', texte):
        pos, spans = m.end(), []
        try:
            while True:
                pos = apres_blancs(pos)
                if texte[pos] == "]":
                    break
                entree, fin = lecteur.raw_decode(texte, pos)
                spans.append((pos, fin, entree))
                pos = apres_blancs(fin)
                if texte[pos] == ",":
                    pos += 1
        except (ValueError, IndexError):
            continue
        if [e for _, _, e in spans] == attendu:
            return m.end(), pos, spans
    return None


def cmd_apercu(projet, sortie, port=None):
    """Greffe `apercu-<dossier>` dans `<projet>/.claude/launch.json` (chantier LOC)."""
    racine = trouver(projet)
    if racine is None:
        sortie.write("GARDE: pas de projet équipé ici : %s\n" % projet)
        return 1
    nom = "apercu-" + os.path.basename(racine)
    chemin = os.path.join(racine, ".claude", "launch.json")
    texte = None
    if os.path.isfile(chemin):
        with open(chemin, encoding="utf-8", newline="") as f:
            texte = f.read()
    lu = entrees_launch(texte) if texte is not None else (0, 0, [])
    if lu is None:
        sortie.write("GARDE: %s illisible, ou sans tableau `configurations` : rien d'écrit\n" % chemin)
        return 1
    ouvre, ferme, spans = lu
    ici = [sp for sp in spans if isinstance(sp[2], dict) and sp[2].get("name") == nom]
    if len(ici) > 1:
        sortie.write("GARDE: %d entrées nommées %s dans %s : rien d'écrit\n" % (len(ici), nom, chemin))
        return 1
    prises = {sp[2].get("port") for sp in spans if isinstance(sp[2], dict) and sp not in ici}
    if port is None and ici and isinstance(ici[0][2].get("port"), int):
        port = ici[0][2]["port"]
    if port is None:
        port = next(n for n in range(PORT_APERCU, PORT_APERCU + 1000) if n not in prises)
    artefacts = dossier_artefacts(racine).replace("\\", "/")
    entree = {"name": nom, "runtimeExecutable": "py" if os.name == "nt" else "python3",
              "runtimeArgs": [VLP_PY.replace("\\", "/"), "servir", artefacts, str(port)],
              "port": port}
    eol = "\r\n" if texte and "\r\n" in texte else "\n"
    corps = json.dumps(entree, indent=2, ensure_ascii=False).replace("\n", eol + "    ")
    if texte is None:
        neuf = json.dumps({"version": "0.0.1", "configurations": [entree]}, indent=2, ensure_ascii=False) + "\n"
    elif ici:
        neuf = texte[:ici[0][0]] + corps + texte[ici[0][1]:]
    elif spans:
        neuf = texte[:spans[-1][1]] + "," + eol + "    " + corps + texte[spans[-1][1]:]
    else:
        neuf = texte[:ouvre] + eol + "    " + corps + eol + "  " + texte[ferme:]
    if neuf != texte:
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin + ".tmp", "w", encoding="utf-8", newline="") as f:
            f.write(neuf)
        os.replace(chemin + ".tmp", chemin)
    sortie.write("APERCU %s %s · port %d · %s\n"
                 % ("déjà" if neuf == texte else "remplacé" if ici else "écrit", nom, port, chemin))
    code, _ = git_texte(["check-ignore", "-q", ".claude/launch.json"], racine)
    if code == 1:
        sortie.write("GARDE: .claude/launch.json n'est pas couvert par .gitignore : il porte des chemins "
                     "de machine, et partirait dans le dépôt\n")
    return 0


def cmd_sante(a, sortie):
    """La santé du code (`sante.py`, VIT15) — chargé ici seulement : son `import ast` coûterait à chaque hook."""
    import sante
    return sante.principal(a, sortie, KIT)


def py_touches(racine):
    """Rendre les `.py` ajoutés, modifiés ou neufs du dépôt de `racine` depuis `HEAD` — index et arbre de travail, lus
    par `git status` —, en chemins absolus triés ; un fichier effacé n'y est pas. Git muet : `None`."""
    code, haut = git_texte(["rev-parse", "--show-toplevel"], racine)
    if code != 0:
        return None
    code, texte = git_texte(["status", "--porcelain=v1", "-z", "--untracked-files=all"], racine)
    if code != 0:
        return None
    champs, fichiers = iter(texte.split("\0")), set()
    for entree in champs:
        if entree[:1] in ("R", "C"):
            next(champs, None)  # le nom d'origine suit un renommage ou une copie
        chemin = os.path.join(haut.strip(), entree[3:])
        if entree.endswith(".py") and os.path.isfile(chemin):
            fichiers.add(os.path.normpath(chemin))
    return sorted(fichiers)


def controles_rapides(racine, motif, pyright):
    """Rendre les trois contrôles de `rapide` (VIT23), en (nom, commande, raison d'un saut) : les groupes de
    `test-vlp.py` qui portent `motif` (`--seul`), pyright sur les `.py` touchés — `pyright` : sa commande, `None`
    s'il manque —, et `sante --cliquet`. Un contrôle sauté a une commande `None` et dit sa raison."""
    scripts = os.path.join(racine, "scripts")
    fichiers = py_touches(racine)
    if fichiers is None:
        typage = ("pyright", None, "Git ne dit pas les fichiers touchés")
    elif not fichiers:
        typage = ("pyright", None, "aucun .py touché")
    elif not pyright:
        typage = ("pyright", None, "pyright introuvable")
    else:
        typage = ("pyright %d fichier(s)" % len(fichiers), list(pyright) + fichiers, None)
    return [("groupes « %s »" % motif, [sys.executable, os.path.join(scripts, "test-vlp.py"), "--seul", motif], None),
            typage,
            ("cliquet", [sys.executable, os.path.join(scripts, "vlp.py"), "sante", "--cliquet", "--racine", racine],
             None)]


def jouer_rapide(commande, racine):
    """Jouer `commande` dans `racine` ; rendre (code de sortie, lignes de sa sortie, durée en secondes) — `None` et la
    raison si elle ne se lance pas."""
    import subprocess
    debut = time.perf_counter()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    try:
        r = subprocess.run(commande, cwd=racine, env=env, capture_output=True, encoding="utf-8", errors="replace")
    except OSError as e:
        return None, ["ne se lance pas : %s" % e], time.perf_counter() - debut
    return r.returncode, (r.stdout + r.stderr).splitlines(), time.perf_counter() - debut


def ecrire_rapide(nom, saut, jeu, sortie):
    """Écrire la ligne `RAPIDE` d'un contrôle : sauté, avec sa raison ; vert, avec sa dernière ligne utile ; rouge,
    avec ses lignes, 30 au plus. Rendre `True` s'il est rouge."""
    if jeu is None:
        sortie.write("RAPIDE %s : sauté · %s\n" % (nom, saut))
        return False
    code, lignes, duree = jeu
    pleines = [l.rstrip() for l in lignes if l.strip()]
    if code == 1 and any(l.startswith("GARDE: aucun groupe ne porte") for l in pleines):
        sortie.write("RAPIDE %s : sauté · %.1f s · aucun groupe ne porte ce motif\n" % (nom, duree))
        return False
    if code == 0:
        utiles = [l.strip() for l in pleines if l.strip() != "OK"] or [l.strip() for l in pleines] or [""]
        sortie.write("RAPIDE %s : vert · %.1f s · %s\n" % (nom, duree, utiles[-1]))
        return False
    sortie.write("RAPIDE %s : rouge · %.1f s · code %s\n" % (nom, duree, code))
    sortie.write("".join("  %s\n" % l for l in pleines[:30]))
    if len(pleines) > 30:
        sortie.write("  … %d ligne(s) de plus\n" % (len(pleines) - 30))
    return True


def controle_rapide(racine, motif, pyright, sortie):
    """Jouer en parallèle les trois contrôles de `rapide` (`controles_rapides`), écrire leurs lignes `RAPIDE` dans
    l'ordre, puis le verdict et sa durée ; rendre 0 si aucun n'est rouge, sinon 1."""
    from concurrent.futures import ThreadPoolExecutor
    debut = time.perf_counter()
    controles = controles_rapides(racine, motif, pyright)
    with ThreadPoolExecutor(max_workers=len(controles)) as pool:
        jeux = [pool.submit(jouer_rapide, c, racine) if c else None for _, c, _ in controles]
        rouges = [ecrire_rapide(nom, saut, jeu.result() if jeu else None, sortie)
                  for (nom, _, saut), jeu in zip(controles, jeux)]
    rouge = any(rouges)
    sortie.write("RAPIDE %s · %.1f s — %s\n" % ("ROUGE" if rouge else "VERT", time.perf_counter() - debut,
                                                 "corrige avant de lancer la suite entière" if rouge
                                                 else "la suite entière reste à jouer : cocher l'exige"))
    return 1 if rouge else 0


def cmd_rapide(a, sortie):
    """Le contrôle rapide d'une fiche du kit, avant la suite entière (VIT23) : ses groupes de `test-vlp.py`, pyright
    sur les `.py` touchés et le cliquet, en parallèle (`controle_rapide`). Il ne remplace pas la suite entière, que
    `cocher` exige toujours (VIT11). Hors du kit — pas de `scripts/test-vlp.py` sous la racine — : `GARDE:`."""
    import shutil
    racine = os.path.abspath(a.racine or ".")
    if not os.path.isfile(os.path.join(racine, "scripts", "test-vlp.py")):
        sortie.write("GARDE: %s n'est pas le kit : pas de scripts/test-vlp.py\n" % racine)
        return 1
    pyright = shutil.which("pyright")
    return controle_rapide(racine, a.motif, [pyright] if pyright else None, sortie)


def cmd_symboles(a, sortie):
    """Imprimer `nom début-fin` pour chaque fonction ou classe de premier niveau de `a.fichier`, lu par `ast` sans
    l'importer — ou pour les seuls `a.noms`, `ABSENT <nom>` pour ceux qui n'y sont pas (sort 1) : une fiche cite un
    nom, ce script rend sa ligne du jour (VIT9). `ast` plutôt que `pyclbr`, bâti dessus : `pyclbr` garde un cache par
    nom de module, faux d'un fichier à l'autre dans un même processus. Fichier absent : `GARDE:`, sort 1."""
    import ast
    if not os.path.isfile(a.fichier):
        sortie.write("GARDE: %s n'est pas un fichier\n" % a.fichier)
        return 1
    with open(a.fichier, encoding="utf-8") as f:
        corps = ast.parse(f.read()).body
    trouves = {n.name: n for n in corps if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    for n in a.noms or list(trouves):
        o = trouves.get(n)
        sortie.write("%s %d-%d\n" % (n, o.lineno, o.end_lineno or o.lineno) if o else "ABSENT %s\n" % n)
    return 1 if any(n not in trouves for n in a.noms) else 0


def options_outils(sous):
    """Déclarer les lignes de commande des outils : `bac`, `claude`, `kit-essai`, `symboles`, `rapide`."""
    bc = sous.add_parser("bac")
    bc.add_argument("dossier")
    sous.add_parser("claude")
    ke = sous.add_parser("kit-essai")
    ke.add_argument("dossier")
    ke.add_argument("--max-turns", type=int, required=True)
    ke.add_argument("--kit")
    sy = sous.add_parser("symboles")
    sy.add_argument("fichier")
    sy.add_argument("noms", nargs="*")
    ra = sous.add_parser("rapide")
    ra.add_argument("motif")
    ra.add_argument("--racine")


def options_clore(sous):
    """Déclarer la ligne de commande de `clore` et d'`oter`, les deux qui ôtent un chantier de la TODO (TAB4)."""
    cl = sous.add_parser("clore")
    cl.add_argument("projet")
    cl.add_argument("--livre", required=True)
    cl.add_argument("--tokens", type=int)
    cl.add_argument("--abandon")
    cl.add_argument("--fait")
    cl.add_argument("--surpris")
    cl.add_argument("--resume")
    cl.add_argument("--date")
    ot = sous.add_parser("oter")
    ot.add_argument("projet")
    ot.add_argument("code")
    ot.add_argument("--raison", required=True)
    ot.add_argument("--date")


def options_marques(sous):
    """Déclarer la ligne de commande de `ouverts` et de `pause`, les lecteur et poseur des marques (NUI21, NUI30)."""
    ou = sous.add_parser("ouverts")
    ou.add_argument("projet")
    ou.add_argument("--rev")
    pa = sous.add_parser("pause")
    pa.add_argument("fichier")
    pa.add_argument("raison")
    pa.add_argument("--date")


def options_carte(sous):
    """Déclarer la ligne de commande de `carte`."""
    c = sous.add_parser("carte")
    c.add_argument("dossier", nargs="?", default=None)
    c.add_argument("--python")
    c.add_argument("--relais", action="store_true")
    c.add_argument("--relecteur", action="store_true")
    c.add_argument("--session-neuve", action="store_true")
    c.add_argument("--enchaine", action="store_true")


def options_mesure(sous):
    """Déclarer les lignes de commande de `cout`, de `compteur` et d'`essai`."""
    es = sous.add_parser("essai")
    es.add_argument("motif")
    es.add_argument("--session")
    co = sous.add_parser("cout")
    co.add_argument("fichier")
    co.add_argument("--session", action="store_true")
    co.add_argument("--a-clore", action="store_true")
    cm = sous.add_parser("compteur")
    cm.add_argument("fichier")
    cm.add_argument("fiches", nargs="*")
    cm.add_argument("--recoupe", action="store_true")


def options_mutant(sous):
    """Déclarer la ligne de commande de `mutant`."""
    mu = sous.add_parser("mutant")
    mu.add_argument("cible")
    mu.add_argument("avant")
    mu.add_argument("apres")
    mu.add_argument("--test")
    quoi = mu.add_mutually_exclusive_group()
    quoi.add_argument("--attendu")
    quoi.add_argument("--tous", action="store_true")


def options_sante(sous):
    """Déclarer la ligne de commande de `sante` : `--base` ou `--cliquet`, `--forcer` et `--si-base` avec `--base`
    seulement."""
    sa = sous.add_parser("sante")
    sa.add_argument("fichiers", nargs="*")
    quoi = sa.add_mutually_exclusive_group()
    quoi.add_argument("--base", action="store_true")
    quoi.add_argument("--cliquet", action="store_true")
    sa.add_argument("--forcer", metavar="RAISON")
    sa.add_argument("--si-base", action="store_true")
    sa.add_argument("--racine")
    sa.add_argument("--sans-ruff", action="store_true")


def main(argv, sortie=None, entree=None, erreur=None):
    """Lire la ligne de commande, puis lancer la sous-commande demandée."""
    sortie = sortie or sys.stdout
    p = argparse.ArgumentParser(prog="vlp.py", description="La mécanique du kit vlp.")
    sous = p.add_subparsers(dest="cmd", required=True)
    options_carte(sous)
    e = sous.add_parser("extraire")
    e.add_argument("fichier")
    e.add_argument("fiche")
    s = sous.add_parser("socle")
    s.add_argument("fichier")
    se = sous.add_parser("sessions")
    se.add_argument("fichier")
    options_mesure(sous)
    li = sous.add_parser("lignes")
    li.add_argument("chemins", nargs="+")
    eq = sous.add_parser("equiper")
    eq.add_argument("dossier")
    eq.add_argument("--contexte", default="context AI")
    v = sous.add_parser("valider")
    v.add_argument("fichiers", nargs="+")
    v.add_argument("--plan", action="store_true")
    pg = sous.add_parser("page")
    pg.add_argument("fichier")
    pg.add_argument("page", nargs="?")
    pg.add_argument("--note", nargs=2, action="append", metavar=("FICHE", "TEXTE"))
    pg.add_argument("--journal", action="append")
    pg.add_argument("--creer", action="store_true")
    pg.add_argument("--projet")
    pg.add_argument("--titre")
    pg.add_argument("--resultat")
    pg.add_argument("--verifier", action="store_true")
    pg.add_argument("--forme", action="store_true")
    pg.add_argument("--date")
    sous.add_parser("hook")
    sous.add_parser("filet")
    et = sous.add_parser("etat")
    et.add_argument("contexte")
    rv = sous.add_parser("renvois")
    rv.add_argument("projet")
    nv = sous.add_parser("niveau")
    nv.add_argument("projet")
    nv.add_argument("--ecrire", action="store_true")
    nv.add_argument("--date")
    cp = sous.add_parser("comparer")
    cp.add_argument("ancienne")
    cp.add_argument("neuve")
    sous.add_parser("trier").add_argument("projet")
    fe = sous.add_parser("feuille")
    fe.add_argument("projet")
    fe.add_argument("--todo")
    fe.add_argument("--verifier", action="store_true")
    fe.add_argument("--date")
    options_clore(sous)
    sous.add_parser("archiver").add_argument("projet")
    ar = sous.add_parser("archive")
    ar.add_argument("projet")
    ar.add_argument("--url")
    sous.add_parser("abri").add_argument("pages", nargs="+")
    ou =sous.add_parser("ouvrir")
    ou.add_argument("projet")
    ou.add_argument("--fiches", required=True)
    ou.add_argument("--titre", required=True)
    ou.add_argument("--artefact")
    ou.add_argument("--estime-fiches", type=nombre_fiches)
    lr = sous.add_parser("lire")
    lr.add_argument("chemins", nargs="+")
    co2 = sous.add_parser("cocher")
    co2.add_argument("fichier")
    co2.add_argument("fiche")
    co2.add_argument("--resolu")
    co2.add_argument("--date")
    cv = co2.add_mutually_exclusive_group()
    cv.add_argument("--verifier", action="store_true")
    cv.add_argument("--refuser")
    cv.add_argument("--session")
    co2.add_argument("--role")
    rl = sous.add_parser("relecture")
    rl.add_argument("fiche", nargs="?")
    rl.add_argument("--sha")
    rl.add_argument("--retirer", action="store_true")
    ct = sous.add_parser("contrat")
    ct.add_argument("transcriptions", nargs="*")
    ct.add_argument("--depuis")
    ct.add_argument("--ouverture")
    fm = sous.add_parser("forme")
    fm.add_argument("transcriptions", nargs="*")
    fm.add_argument("--depuis")
    fm.add_argument("--regle", choices=REGLES, default=REGLE)
    sous.add_parser("gardien")
    vg = sous.add_parser("vigile")
    vg.add_argument("fichier", nargs="?", default=None)
    options_marques(sous)
    at = sous.add_parser("attente")
    ats = at.add_subparsers(dest="op", required=True)
    at_aj = ats.add_parser("ajouter")
    at_aj.add_argument("page")
    at_aj.add_argument("--url")
    at_aj.add_argument("--projet")
    ats.add_parser("lister").add_argument("dossier")
    at_re = ats.add_parser("retirer")
    at_re.add_argument("page")
    at_re.add_argument("--projet")
    ats.add_parser("hook")
    rp = sous.add_parser("repeindre")
    rp.add_argument("projet")
    rp.add_argument("--a-blanc", action="store_true")
    ln = sous.add_parser("lien")
    ln.add_argument("page")
    ln.add_argument("url")
    lns = sous.add_parser("liens")
    lns.add_argument("projet")
    rc =sous.add_parser("recompter")
    rc.add_argument("projet")
    for o in ("--ecrire", "--essais", "--a-clore"):
        rc.add_argument(o, action="store_true")
    rc.add_argument("--clos")
    px = sous.add_parser("prix")
    px.add_argument("projet")
    px.add_argument("--a-blanc", action="store_true")
    options_outils(sous)
    sous.add_parser("joints").add_argument("dossier")
    sv = sous.add_parser("servir")
    sv.add_argument("dossier")
    sv.add_argument("port", type=int)
    ap = sous.add_parser("apercu")
    ap.add_argument("projet")
    ap.add_argument("--port", type=int)
    options_mutant(sous)
    nu = sous.add_parser("nuits")
    nu.add_argument("verbe", choices=["noter", "lecon"])
    nu.add_argument("texte")
    nu.add_argument("--canal")
    nu.add_argument("--stop", action="store_true")
    nu.add_argument("--sorte", choices=carnet.SORTES)
    nu.add_argument("--projet", default=".")
    pl = sous.add_parser("plan")
    pl.add_argument("verbe", choices=["ecrire", "lire"])
    pl.add_argument("projet")
    pl.add_argument("--json")
    pl.add_argument("--date")
    pl.add_argument("--canal", choices=CANAUX)
    pl.add_argument("--chantier")
    fu = sous.add_parser("fusionner")
    fu.add_argument("projet")
    fu.add_argument("branche")
    ma = sous.add_parser("matin")
    ma.add_argument("projet")
    ma.add_argument("date", nargs="?")
    ma.add_argument("--rapport")
    ch = sous.add_parser("chef")
    ch.add_argument("verbe", choices=["page"])
    ch.add_argument("--questions", required=True)
    ch.add_argument("--sortie", required=True)
    tr = sous.add_parser("transcription")
    tr.add_argument("jsonl")
    options_sante(sous)
    a = p.parse_args(argv)
    try:
        return repartir(a, sortie, entree, erreur)
    except Absent as e:
        sortie.write("GARDE: %s\n" % e)
        return 1


# Les sous-commandes qui ne demandent que leurs options et la sortie : `repartir` les lance d'une ligne.
PAR_ARGUMENTS = {
    "ouvrir": cmd_ouvrir, "clore": cmd_clore, "oter": cmd_oter, "archiver": cmd_archiver, "trier": cmd_trier, "feuille": cmd_feuille,
    "niveau": cmd_niveau, "comparer": cmd_comparer, "relecture": cmd_relecture, "contrat": cmd_contrat,
    "forme": cmd_forme, "ouverts": cmd_ouverts, "pause": cmd_pause, "plan": cmd_plan, "matin": cmd_matin, "fusionner": cmd_fusionner,
    "sante": cmd_sante, "symboles": cmd_symboles, "compteur": cmd_compteur, "carte": cmd_carte,
    "rapide": cmd_rapide, "essai": cmd_essai,
}


def repartir(a, sortie, entree, erreur):
    """Le dispatch. Une `Absent` levée ici est gardée par `main`, et nulle part
    ailleurs : un chemin de `CHANTIER.md` ne fait plus tomber le script."""
    if a.cmd in PAR_ARGUMENTS:
        return PAR_ARGUMENTS[a.cmd](a, sortie)
    if a.cmd == "lire":
        return cmd_lire(a.chemins, sortie)
    if a.cmd == "archive":
        return cmd_archive(a.projet, a.url, sortie)
    if a.cmd == "abri":
        return cmd_abri(a.pages, sortie)
    if a.cmd == "renvois":
        return cmd_renvois(a.projet, sortie)
    if a.cmd == "etat":
        sortie.write("ETAT=%s\n" % nom_etat(a.contexte))
        return 0
    if a.cmd == "hook":
        return une_fois(entree, cmd_hook, sortie, erreur or sys.stderr)
    if a.cmd == "filet":
        return une_fois(entree, cmd_filet, sortie, erreur or sys.stderr)
    if a.cmd == "page":
        chemin_garde(a.fichier)
        if a.page is None:
            a.page = page_du_fichier(a.fichier)
        return cmd_page(a, sortie)
    if a.cmd == "valider":
        return cmd_valider(a.fichiers, sortie, a.plan)
    if a.cmd == "equiper":
        return cmd_equiper(a.dossier, a.contexte, sortie)
    if a.cmd == "lignes":
        return cmd_lignes(a.chemins, sortie)
    if a.cmd == "gardien":
        return une_fois(entree, cmd_gardien, sortie)
    if a.cmd == "vigile":
        return cmd_vigile(a.fichier, sortie) if a.fichier else une_fois(entree, cmd_vigile_hook, sortie)
    if a.cmd == "attente":
        return une_fois(entree, cmd_attente_hook, sortie) if a.op == "hook" else cmd_attente(a, sortie)
    if a.cmd == "repeindre":
        return cmd_repeindre(a.projet, sortie, a.a_blanc)
    if a.cmd == "lien":
        return cmd_lien(a.page, a.url, sortie)
    if a.cmd == "liens":
        return cmd_liens(a.projet, sortie)
    if a.cmd == "recompter":
        return (cmd_recompter_clos(a.projet, sortie, a.ecrire, a.clos) if a.clos
                else cmd_recompter(a.projet, sortie, a.ecrire, a.essais, a.a_clore))
    if a.cmd == "prix":
        return cmd_prix(a.projet, sortie, a.a_blanc)
    if a.cmd == "bac":
        return cmd_bac(a.dossier, sortie)
    if a.cmd == "claude":
        return cmd_claude(sortie)
    if a.cmd == "kit-essai":
        return cmd_kit_essai(a.dossier, a.max_turns, a.kit, sortie)
    if a.cmd == "servir":
        return cmd_servir(a.dossier, a.port, sortie)
    if a.cmd == "apercu":
        return cmd_apercu(a.projet, sortie, a.port)
    if a.cmd == "mutant":
        return cmd_mutant(a, sortie)
    if a.cmd == "nuits":
        if a.verbe == "lecon":
            return cmd_nuits_lecon(a.texte, a.projet, sortie)
        return cmd_nuits_noter(a.texte, a.canal, a.stop, sortie, sorte=a.sorte)
    if a.cmd == "chef":
        return cmd_chef_page(a.questions, a.sortie, sortie, lire(os.path.join(KIT, GABARIT_CHOIX)))
    if a.cmd == "joints":
        return cmd_joints(a.dossier, sortie)
    if a.cmd == "transcription":
        return cmd_transcription(a.jsonl, sortie)
    chemin_garde(a.fichier)
    if a.cmd == "extraire":
        return cmd_extraire(a.fichier, a.fiche, sortie)
    if a.cmd == "cocher":
        return cmd_cocher(a, sortie)
    if a.cmd == "socle":
        return cmd_socle(a.fichier, sortie)
    if a.cmd == "cout":
        return cmd_cout(a.fichier, a.session, sortie, a.a_clore)
    return cmd_sessions(a.fichier, sortie)
