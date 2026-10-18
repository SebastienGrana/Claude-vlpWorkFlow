"""La carte d'un projet : ce que les commandes injectent avant leur premier tour (REF45 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import glob
import hashlib
import io
import os
import re
import sys
import tempfile
import time

import vlp_hook

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (
    ALIAS,
    Absent,
    CHANTIERS_POSSIBLES,
    COURANT,
    FORMAT_DEBUT,
    FORMAT_FIN,
    METHODE,
    SESSION,
    TITRE,
    chemin_garde,
    lignes_de,
    lignes_du_projet,
    lignes_gardees,
    lire,
    section,
)
from noyau.fiches import (socle_lignes)

__all__ = [
    "equipe",
    "trouver",
    "fichier_courant",
    "chemins_md",
    "imprimer_section",
    "todo_condensee",
    "sans_apporte",
    "imprimer_todo",
    "imprimer_methode",
    "fiches",
    "PLAFOND_CARTE",
    "carte_bornee",
    "EFFORT_SOCLE",
    "EFFORT_REGLE",
    "EFFORT_DEFAUT",
    "effort_defaut",
    "ligne_effort",
    "carte",
    "places_de_session",
    "SESSION_SURE",
    "marque_enchaine",
    "poser_marque_enchaine",
    "avertir_session",
    "RELAIS_SECONDES",
    "MARQUE_SECONDES",
    "carte_injectee",
    "cmd_carte",
]


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


def todo_condensee(lignes, plage):
    """Le texte de la section TODO `plage` que la carte imprime : son titre, puis chaque rang de la table
    `| # | Chantier |` sans « Ce qu'il apporte », précédé de son numéro de ligne (`382:| 96 | …`) — code,
    titre, coût et score, dépendance (REF2, piste `ALC`). La prose et cette colonne se lisent dans le
    fichier, à leur ligne. Sans table : None. Un rang cassé : la `ValueError` de `rangs_todo`."""
    corps = lignes[plage[0] - 1:plage[1]]
    rangs = coeur.rangs_todo(corps)
    entete = next((l for l in corps if l.startswith("| # | Chantier")), None)
    if entete is None:
        return None
    texte = [corps[0], "(condensée : ni la prose ni « Ce qu'il apporte » — une ligne entière se lit à son numéro)",
             sans_apporte(coeur.cellules_de(entete, "en-tête de la TODO"))]
    texte += ["%d:%s" % (plage[0] + i, sans_apporte(c)) for i, c in rangs]
    return "".join(l + "\n" for l in texte)


def sans_apporte(cellules):
    """La ligne de table des cinq `cellules` d'un rang de TODO, sans la 3e, « Ce qu'il apporte »."""
    return "| %s |" % " | ".join(cellules[:2] + cellules[3:])


def imprimer_todo(texte, racine, sortie):
    """La TODO de chaque fichier que nomme la ligne **chantiers possibles** : condensée (`todo_condensee`), sinon
    — pas de table — la section entière ; une table cassée : une `GARDE:`, puis la section entière."""
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
            continue
        try:
            court = todo_condensee(lignes, plage)
        except ValueError as e:
            sortie.write("GARDE: %s : %s — TODO entière\n" % (chemin, e))
            court = None
        if court is None:
            imprimer_section(sortie, "TODO", chemin, lignes, plage)
        else:
            sortie.write("--- TODO : %s (lignes %d–%d) ---\n%s" % (chemin, plage[0], plage[1], court))


def imprimer_methode(texte, racine, sortie):
    """Le format des fiches, dans le premier chemin de la ligne **méthode** :
    cherché dans le projet, sinon sous `KIT` (la ligne du kit est de la prose)."""
    methode = METHODE.search(texte)
    chemins = chemins_md(methode.group(1), racine) if methode else []
    if not chemins:
        sortie.write("METHODE=absente (pas de ligne « méthode »)\n")
        return
    chemin = chemins[0]
    lieu = racine if os.path.isfile(os.path.join(racine, chemin)) else etat.KIT
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


# Une injection `!` ne garde qu'un nombre borné de caractères, puis un aperçu (doc « tools-reference », chiffre dans
# le socle de `REF`) : la carte reste sous ce plafond, avec de la marge (REF2).
PLAFOND_CARTE = 25000


def carte_bornee(depart, sortie, tete="", relecteur=False, neuve=False):
    """Écrire `tete`, puis la `carte` du projet qui contient `depart` — ce que lance `vlp.py carte`. Au-delà de
    `PLAFOND_CARTE` caractères, `tete` comprise, une `GARDE:` en première ligne le dit, et la carte suit entière :
    jamais de coupe silencieuse (REF2)."""
    tampon = io.StringIO()
    code = carte(depart, tampon, relecteur, neuve)
    texte = tete + tampon.getvalue()
    if len(texte) > PLAFOND_CARTE:
        sortie.write("GARDE: carte de %d caractères, au-delà de PLAFOND_CARTE (%d) : une injection `!` la réduirait "
                     "à un aperçu — alléger CHANTIER.md ou la TODO\n" % (len(texte), PLAFOND_CARTE))
    sortie.write(texte)
    return code


EFFORT_SOCLE = re.compile(r"effort `([a-z]+)`")
EFFORT_REGLE = "- **L'effort se règle selon la tâche"
EFFORT_DEFAUT = re.compile(r"Une fiche[^`]*: `([a-z]+)`")


def effort_defaut(chemin=None):
    """L'effort d'une fiche que dit la règle « L'effort se règle selon la tâche » de `methode-chantier.md` (sous
    `KIT`, ou `chemin`) — le premier `Une fiche … : `<niveau>`` de sa puce ; None si la puce ou le niveau manque. Lu,
    jamais recopié (REF28, règle 3)."""
    try:
        lignes = lignes_de(chemin or os.path.join(etat.KIT, "methode-chantier.md"))
    except OSError:
        return None
    debut = next((i for i, l in enumerate(lignes) if l.startswith(EFFORT_REGLE)), None)
    if debut is None:
        return None
    puce = [lignes[debut]]
    for l in lignes[debut + 1:]:
        if not l.startswith("  "):
            break
        puce.append(l.strip())
    m = EFFORT_DEFAUT.search(" ".join(puce))
    return m.group(1) if m else None


def ligne_effort(lignes, methode=None):
    """La ligne `EFFORT=` de la carte (REF28) : le premier « effort `<niveau>` » du socle du fichier de fiches
    `lignes`, sinon le défaut d'`effort_defaut`, sinon `EFFORT=absent`."""
    m = next((EFFORT_SOCLE.search(l) for l in socle_lignes(lignes) if EFFORT_SOCLE.search(l)), None)
    if m:
        return "EFFORT=%s (socle du chantier)" % m.group(1)
    defaut = effort_defaut(methode)
    if defaut:
        return "EFFORT=%s (défaut de methode-chantier.md)" % defaut
    return "EFFORT=absent (ni le socle ni methode-chantier.md ne le disent)"


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
            sortie.write("".join(l + "\n" for l in coeur.ligne_git(os.path.dirname(v))))
        if not voisins:
            sortie.write("AUCUN_PROJET\n")
        return 0
    texte = lire(os.path.join(racine, "CHANTIER.md"))
    try:
        courant = coeur.courant_de(racine)
    except Absent as e:
        # `cmd_equiper` appelle `carte` en direct : elle garde, elle ne lève pas.
        sortie.write("PROJET=%s\nGARDE: %s\n" % (racine, e))
        return 1
    sortie.write("PROJET=%s\nCOURANT=%s\n--- CHANTIER.md ---\n%s" % (racine, courant or "aucun", texte))
    if not texte.endswith("\n"):
        sortie.write("\n")
    if not relecteur:
        for l in coeur.lignes_attente(coeur.dossier_artefacts(racine)):
            sortie.write(l + "\n")
        if os.environ.get("VLP_NUIT") == "1":
            sortie.write("NUIT=1\n")
        retard = coeur.retard_plugin(racine)
        if retard:
            sortie.write('PLUGIN_RETARD=%d commit(s) de code du plugin absents du plugin chargé — avant un '
                         '/reload-plugins : git -C "%s" merge --ff-only %s\n'
                         % (retard[0], retard[1].replace("\\", "/"), retard[2]))
        coeur.ecrire_ailleurs(racine, sortie)
        sortie.write("".join(l + "\n" for l in coeur.ligne_git(racine)))
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
    sortie.write(ligne_effort(lignes_de(os.path.join(racine, courant))) + "\n")
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
    return carte_bornee(depart, sortie, tete="\nPYTHON=%s\n" % python, **options)


def cmd_carte(a, sortie):
    """Lancer `vlp.py carte` : injectée avec `--python`, nue sinon. `--enchaine` pose la marque à chaque appel, relais
    compris : sous Ubuntu, le premier appel de l'injection échoue."""
    depart = a.dossier or os.getcwd()
    if a.enchaine:
        poser_marque_enchaine()
    if a.python:
        return carte_injectee(depart, a.python, a.relais, sortie, relecteur=a.relecteur, neuve=a.session_neuve)
    return carte_bornee(depart, sortie, relecteur=a.relecteur, neuve=a.session_neuve)
