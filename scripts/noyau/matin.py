"""Le matin : fusionner la nuit dans main, fusionner une fiche jouée en worktree (REF49 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import datetime
import io
import os
import re
import sys
import tempfile

import carnet

from noyau import etat
from noyau.facade import coeur
import noyau.relecture   # `noyau.relecture.<nom>` : un test remplace ce nom là
from noyau.commun import (Absent, chemin_archive, lignes_de, lire, numero_ligne, section)
from noyau.fiches import (VLP_PY)
from noyau.carte import (equipe)
from noyau.page import (COMMIT_FICHE, JOINTS, PUBLIE, notes_publie, recopier_joints, texte_publie)
from noyau.feuille import (
    LETTRES,
    SEPARATEUR,
    champ,
    couts_du_projet,
    doublon_lettres,
    entrees_lettres,
    feuille,
    fin_lettres,
    lettre_entree,
    page_clos,
    page_feuille,
    rafraichir_couts,
    rang_en_cours,
    todo_du_fichier,
    zone,
    zone_todo,
)
from noyau.clos import (COUTS_SVG, ecrire_couts, lignes_clos, prix_clos, resommer, total_clos)
from noyau.relecture import (CODE_PLUGIN)
from noyau.niveau import (dire_attentes, entrees_attente, texte_attente)
from noyau.clore import (ENTREE_CLOS, MARQUE_CLOS, clos_a_couper, courant_de, courant_ou_rien, worktrees)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF49 — `pointes_du_texte`, `choisir_nuit` — se lisent ici seulement.
__all__ = [
    "OUVERT_CARTE", "JETON_OUVERT", "JETON_LETTRES", "neutre", "restaurer", "pointes_nuit", "ordre_nuit",
    "JETON_TRANCHE", "TITRE_JOURNAL", "en_dict", "trois_voies", "fusion_lignes", "cle_todo", "decouper_tables",
    "decouper_index", "decouper_etat", "decouper_claude", "fusion_texte", "fusion_a_jetons", "fusion_tranche_etat",
    "fusion_tranche_claude", "fusion_tranche_index", "fusion_etat", "fusion_claude", "fusion_index",
    "fusion_archive_index", "fusion_archive_clos", "heure_attente", "fusion_attente", "fusion_publie", "lire_rev",
    "ecrire_comme", "fusionner_fichiers", "fusionner_branche", "projet_du_matin", "racine_du_depot", "WIP_SUJET",
    "WIP_MOTIF", "de_cote", "etat_branche_nuit", "NUIT_BRANCHE", "nuit_a_ranger", "cmd_matin", "retard_du_matin",
    "fusion_fiche_refusee", "garder_hors_commit", "retirer_worktree", "base_refaite", "fusionner_fiche",
    "cmd_fusionner",
]


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
    code, t = noyau.relecture.git_texte(["for-each-ref", "--format=%(refname) %(committerdate:unix)",
                         "refs/heads/nuit/%s-*" % date], projet)
    return (None, t) if code != 0 else (pointes_du_texte(t), None)


def pointes_du_texte(texte):
    """`[(branche, heure)]` d'une sortie de `git for-each-ref --format="%(refname) %(committerdate:unix)"`, `refs/heads/`
    ôté ; une ligne mal formée est sautée. Ne lance rien (REF49)."""
    pointes = []
    for l in texte.splitlines():
        champs = l.split()
        if len(champs) == 2 and champs[1].isdigit():
            pointes.append((champs[0][len("refs/heads/"):], int(champs[1])))
    return pointes


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
        code, msg = noyau.relecture.git_texte(["merge-file", "-L", "HEAD", "-L", "base", "-L", branche] + chemins, projet)
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
    code, t = noyau.relecture.git_texte(["show", "%s:%s" % (rev, chemin)], projet)
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
            code, msg = noyau.relecture.git_texte(["rm", "-q", "--cached", "--ignore-unmatch", "--", chemin], projet)
        else:
            ecrire_comme(complet, texte)
            code, msg = noyau.relecture.git_texte(["add", "--", chemin], projet)
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
    code_leur, texte_leur = noyau.relecture.git_texte(["show", "%s:CHANTIER.md" % branche], projet)
    carte_leur, _, liste_leur = neutre(texte_leur if code_leur == 0 else "")
    garde = doublon_lettres(liste_main.split(":", 1)[-1], (liste_leur or "").split(":", 1)[-1])
    if garde:
        sortie.write("%s — %s non fusionnée\n" % (garde, branche))
        return True

    code, msg = noyau.relecture.git_texte(["merge", "--no-ff", "--no-commit", branche], projet)
    if code not in (0, 1) or noyau.relecture.git_texte(["rev-parse", "-q", "--verify", "MERGE_HEAD"], projet)[0] != 0:
        return arret("fusion impossible : %s" % msg)
    code, t = noyau.relecture.git_texte(["diff", "--name-only", "--diff-filter=U"], projet)
    conflits = set(t.splitlines()) if code == 0 else set()

    # CHANTIER.md : les trois versions sans leurs libellés ni leurs lettres, fusionnées, puis les valeurs de `main`
    _, base = noyau.relecture.git_texte(["merge-base", "HEAD", branche], projet)
    code_base, texte_base = noyau.relecture.git_texte(["show", "%s:CHANTIER.md" % base.strip()], projet)
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
        noyau.relecture.git_texte(["add", "CHANTIER.md"], projet)
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
        code, msg = noyau.relecture.git_texte(["checkout", "--ours", "--", chemin], projet)
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
    code, msg = noyau.relecture.git_texte(["add", "-A"], projet)
    if code != 0:
        return arret("git add : %s" % msg)
    code, msg = noyau.relecture.git_texte(["commit", "-q", "-m", message], projet)
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
    code, haut = noyau.relecture.git_texte(["rev-parse", "--show-toplevel"], projet)
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
    code, sujet = noyau.relecture.git_texte(["log", "-1", "--format=%s", branche], projet)
    return sujet.strip() if code == 0 and WIP_MOTIF.match(sujet.strip()) else None


def etat_branche_nuit(projet, branche):
    """Ce que `matin` fait de `branche` : `("deja", None)` si elle est ancêtre de `HEAD`, `("cote", <chantier ouvert>)`
    si son `CHANTIER.md` garde un chantier ouvert (`de_cote`), sinon `("fusion", None)`."""
    if noyau.relecture.git_texte(["merge-base", "--is-ancestor", branche, "HEAD"], projet)[0] == 0:
        return "deja", None
    courant = de_cote(projet, branche)
    return ("cote", courant) if courant else ("fusion", None)


NUIT_BRANCHE = re.compile(r"nuit/(\d{4}-\d{2}-\d{2})-")


def nuit_a_ranger(projet, sortie):
    """La date de la nuit que `matin` range quand on ne lui en donne pas : la seule qui a une branche à fusionner
    (`etat_branche_nuit`), dite par `NUIT <date> — la seule à ranger : <n> branche(s)`. Aucune, ou plusieurs (leurs
    dates, la plus ancienne d'abord) : None, après une `GARDE:`."""
    code, t = noyau.relecture.git_texte(["for-each-ref", "--format=%(refname)", "refs/heads/nuit/*"], projet)
    if code != 0:
        sortie.write("GARDE: %s — rien fusionné\n" % t.strip())
        return None
    branches = [ref[len("refs/heads/"):] for ref in sorted(t.splitlines())]
    date, ligne = choisir_nuit([(b, etat_branche_nuit(projet, b)[0]) for b in branches if NUIT_BRANCHE.match(b)])
    sortie.write(ligne)
    return date


def choisir_nuit(etats):
    """`(date, ligne)` : la nuit à ranger d'après `etats`, `[(branche nuit/<date>-…, état)]` (`etat_branche_nuit`) — la
    seule date qui a une branche en `"fusion"`, et sa ligne `NUIT` ; aucune, ou plusieurs : `(None, "GARDE: …")`. Ne
    lance rien (REF49)."""
    a_ranger = {}
    for branche, etat_ in etats:
        nuit = NUIT_BRANCHE.match(branche)
        if nuit and etat_ == "fusion":
            a_ranger.setdefault(nuit.group(1), []).append(branche)
    if len(a_ranger) == 1:
        date, branches = next(iter(a_ranger.items()))
        return date, "NUIT %s — la seule à ranger : %d branche(s)\n" % (date, len(branches))
    if a_ranger:
        return None, "GARDE: plusieurs nuits à ranger : %s — rien fusionné ; donne la date\n" % ", ".join(
            "%s (%d)" % (d, len(b)) for d, b in sorted(a_ranger.items()))
    return None, ("GARDE: aucune nuit à ranger (%d branche(s) nuit/* déjà fusionnée(s) ou de côté) — rien fusionné\n"
                  % len(etats))


def cmd_matin(a, sortie):
    """`matin <projet> [<date>]` : les gardes, la nuit (la date donnée, sinon `nuit_a_ranger`), l'ordre, puis chaque
    branche de la nuit — `DÉJÀ`, `DE CÔTÉ` ou fusionnée. `--rapport` veut la date : sans elle, `GARDE:`."""
    if a.rapport:
        if a.date is None:
            sortie.write("GARDE: --rapport veut la date de la nuit (celle que `matin` a dite : NUIT <date>)\n")
            return 1
        return coeur.cmd_matin_rapport(a, sortie)
    projet = projet_du_matin(a, sortie)
    if projet is None:
        return 1
    code, tete = noyau.relecture.git_texte(["symbolic-ref", "--short", "-q", "HEAD"], projet)
    if code != 0 or tete.strip() != "main":
        sortie.write("GARDE: HEAD est sur %s, pas sur main — rien fusionné\n" % (tete.strip() if code == 0 else "rien (détaché)"))
        return 1
    code, sale = noyau.relecture.git_texte(["status", "--porcelain"], projet)
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
    _, avant = noyau.relecture.git_texte(["rev-parse", "HEAD"], projet)
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
    if not avant or os.path.normcase(os.path.realpath(projet)) != os.path.normcase(os.path.realpath(etat.KIT)):
        return
    code, n = noyau.relecture.git_texte(["rev-list", "--count", "%s..HEAD" % avant, "--"] + list(CODE_PLUGIN), projet)
    if code == 0 and n.strip().isdigit() and int(n) > 0:
        sortie.write("PLUGIN_RETARD=%d commit(s) de code du plugin fusionné(s) — la session ouverte ne les voit "
                     "qu'après /reload-plugins\n" % int(n))


def fusion_fiche_refusee(racine, fiche, dossier):
    """`(raison, sha, branche)` pour `fusionner_fiche` (ISO4) : la raison de ne rien toucher, sinon `(None, …)` avec
    la tête et la branche du worktree `dossier` (None si détachée). Refusé : `dossier` qui n'est pas un autre
    worktree du dépôt de `racine`, `MERGE_HEAD` présent ou fichier suivi changé dans `racine`, aucun commit
    `<fiche> :` (`COMMIT_FICHE`) du worktree que `racine` n'a pas."""
    blocs = {os.path.normcase(os.path.realpath(d)): b for d, b in worktrees(racine)}
    cle = os.path.normcase(os.path.realpath(dossier))
    if cle not in blocs or cle == os.path.normcase(os.path.realpath(racine)):
        return "%s n'est pas un autre worktree de ce dépôt" % dossier, None, None
    if noyau.relecture.git_texte(["rev-parse", "-q", "--verify", "MERGE_HEAD"], racine)[0] == 0:
        return "une fusion est déjà en cours (MERGE_HEAD)", None, None
    code, sale = noyau.relecture.git_texte(["status", "--porcelain", "--untracked-files=no"], racine)
    if code != 0 or sale.strip():
        return "fichier suivi changé dans %s" % racine, None, None
    code, sha = noyau.relecture.git_texte(["rev-parse", "HEAD"], dossier)
    sujets = noyau.relecture.git_texte(["log", "--format=%s", "HEAD.." + sha.strip()], racine)[1].splitlines() if code == 0 else []
    if not any(m and m.group(1) == fiche for m in map(COMMIT_FICHE.match, sujets)):
        return "aucun commit « %s : » du worktree que %s n'a pas" % (fiche, racine), None, None
    return None, sha.strip(), blocs[cle]


def garder_hors_commit(racine, dossier):
    """REF41 : le diff des chemins que le worktree `dossier` garde hors commit — non suivis compris, indexés là-bas
    juste avant son retrait — dans `vlp-gardes/<worktree>-<heure>.patch` du dossier Git commun de `racine`, écrit
    par Git en octets (REF56 : lu en texte, un CRLF ou un latin-1 s'y perdait) ; rend (chemin, `git apply --check`
    passé dans `racine`), ou (None, False) si Git échoue ou n'écrit rien."""
    code_dir, commun = noyau.relecture.git_texte(["rev-parse", "--path-format=absolute", "--git-common-dir"], racine)
    if code_dir != 0 or noyau.relecture.git_texte(["add", "-A"], dossier)[0] != 0:
        return None, False
    dossier_gardes = os.path.join(commun.strip(), "vlp-gardes")
    os.makedirs(dossier_gardes, exist_ok=True)
    chemin = os.path.normpath(os.path.join(dossier_gardes, "%s-%s.patch" % (
        os.path.basename(os.path.normpath(dossier)), datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))))
    if noyau.relecture.git_texte(["diff", "--cached", "--binary", "HEAD", "--output=" + chemin], dossier)[0] != 0 \
            or not os.path.getsize(chemin):
        return None, False
    return chemin, noyau.relecture.git_texte(["apply", "--check", chemin], racine)[0] == 0


def retirer_worktree(racine, dossier, branche, sortie):
    """Retirer le worktree `dossier` et sa `branche` après `fusionner_fiche` (ISO4). Ce qu'il garde hors commit va
    d'abord dans un correctif (`garder_hors_commit`, REF41) : `GARDÉ <n> chemin(s) : <correctif>` — à appliquer,
    ou non, par `git apply` ; s'il manque ou échoue à `git apply --check`, `PERDU <n> chemin(s) …` (et son chemin).
    Un échec de Git au retrait, une `GARDE:`."""
    code, reste = noyau.relecture.git_texte(["status", "--porcelain"], dossier)
    if code == 0 and reste.strip():
        lignes = reste.splitlines()
        correctif, applicable = garder_hors_commit(racine, dossier)
        if applicable:
            sortie.write("GARDÉ %d chemin(s) : %s\n" % (len(lignes), correctif))
        else:
            sortie.write("PERDU %d chemin(s) non commités du worktree : %s%s\n" % (len(lignes), ", ".join(
                l[3:] for l in lignes), " — correctif rejeté par git apply --check : %s" % correctif if correctif else ""))
    for args in [["worktree", "remove", "--force", dossier]] + ([["branch", "-D", branche]] if branche else []):
        code, texte = noyau.relecture.git_texte(args, racine)
        if code != 0:
            sortie.write("GARDE: git %s : %s\n" % (" ".join(args[:2]), texte))


def base_refaite(racine, sortie):
    """REF40 : une fusion en conflit sur la seule base du cliquet (`sante.BASE`, un relevé que `sante --base` refait)
    se règle sur le code fusionné — la base de `racine` reprise, le cliquet tenu contre elle, puis la base refaite et
    la fusion commitée. Rend True, `BASE REFAITE …` écrit ; cliquet rompu ou Git en échec : False, sa ligne écrite,
    la fusion laissée à `merge --abort`."""
    import sante
    if noyau.relecture.git_texte(["checkout", "--ours", "--", sante.BASE], racine)[0] != 0:
        sortie.write("BASE NON REFAITE : git checkout --ours %s a échoué\n" % sante.BASE)
        return False
    tampon = io.StringIO()
    try:
        fonctions, version = sante.mesurer(racine, sante.chemins_de(racine, None), sante.trouver_ruff(), tampon)
        tenu = (sante.tenir_cliquet(racine, fonctions, version, tampon) == 0
                and sante.poser_base(racine, fonctions, version, None, tampon) == 0)
    except (SyntaxError, OSError, ValueError) as e:
        tampon.write("GARDE: %s\n" % e)
        tenu = False
    if not tenu:
        sortie.write("".join(l + "\n" for l in tampon.getvalue().splitlines()
                             if l.startswith(("CLIQUET ROMPU", "GARDE:"))))
        return False
    for args in (["add", "--", sante.BASE], ["commit", "--no-edit"]):
        code, texte = noyau.relecture.git_texte(args, racine)
        if code != 0:
            sortie.write("BASE NON REFAITE : git %s : %s\n" % (args[0], texte.strip()))
            return False
    sortie.write("BASE REFAITE %s · seul conflit, cliquet tenu sur le code fusionné\n" % sante.BASE)
    return True


def fusionner_fiche(fichier, fiche, dossier, sortie):
    """`fusionner <fichier de fiches> <fiche> --worktree <dossier>` (ISO4) : depuis la racine du dépôt du fichier,
    fusionne la tête du worktree — le commit de la fiche, fait là-bas par `commiter` — sous « Fusion : <fiche> »,
    `FUSIONNÉ <fiche> <sha>` (la tête d'après), puis retire le worktree et sa branche (`retirer_worktree`), sort 0.
    Conflit sur la seule base du cliquet : `base_refaite` (REF40), `FUSIONNÉ` s'il tient. Sinon, ou un autre
    fichier en conflit : `git merge --abort`, rien de gardé, le worktree retiré quand même, `CONFLIT <fiche> <fichiers>`,
    sort 1 — le chef rejoue la fiche (Q3). `GARDE:`, rien touché, sort 1 : `fusion_fiche_refusee`, ou un merge que
    Git refuse avant d'écrire ; un `--abort` raté laisse la fusion en cours, et le worktree."""
    code, racine = noyau.relecture.git_texte(["rev-parse", "--show-toplevel"], os.path.dirname(os.path.abspath(fichier)))
    raison, sha, branche = (fusion_fiche_refusee(racine.strip(), fiche, dossier) if code == 0
                            else ("%s hors Git" % fichier, None, None))
    if raison or not sha:
        sortie.write("GARDE: %s — rien touché\n" % raison)
        return 1
    racine = racine.strip()
    code, texte = noyau.relecture.git_texte(["merge", "--no-edit", "-m", "Fusion : %s" % fiche, sha], racine)
    if code != 0:
        conflits = noyau.relecture.git_texte(["diff", "--name-only", "--diff-filter=U"], racine)[1].splitlines()
        if not conflits:
            sortie.write("GARDE: git refuse la fusion : %s — rien touché\n" % texte)
            return 1
        import sante
        tampon = io.StringIO()
        if conflits == [sante.BASE] and base_refaite(racine, tampon):
            sortie.write("FUSIONNÉ %s %s\n" % (fiche, noyau.relecture.git_texte(["rev-parse", "--short", "HEAD"], racine)[1].strip()))
            sortie.write(tampon.getvalue())
            retirer_worktree(racine, dossier, branche, sortie)
            return 0
        sortie.write(tampon.getvalue())
        code, texte = noyau.relecture.git_texte(["merge", "--abort"], racine)
        if code != 0:
            sortie.write("GARDE: git merge --abort : %s — fusion laissée en cours, worktree gardé\n" % texte)
            return 1
        retirer_worktree(racine, dossier, branche, sortie)
        sortie.write("CONFLIT %s %s\n" % (fiche, ", ".join(conflits)))
        return 1
    sortie.write("FUSIONNÉ %s %s\n" % (fiche, noyau.relecture.git_texte(["rev-parse", "--short", "HEAD"], racine)[1].strip()))
    retirer_worktree(racine, dossier, branche, sortie)
    return 0


def cmd_fusionner(a, sortie):
    """`fusionner <projet> <branche>` (NUI26) : la fusion du jour, `branche` dans celle du dossier, par
    `fusionner_branche` sous « Fusion : <branche> ». Gardes, rien fusionné : non équipé ou hors racine, `HEAD`
    détachée, `MERGE_HEAD` présent, arbre sale, branche absente, branche qui garde un chantier ouvert (`de_cote`).
    Avec `--worktree`, les deux arguments sont `<fichier de fiches> <fiche>` : `fusionner_fiche` (ISO4)."""
    if a.worktree:
        return fusionner_fiche(a.projet, a.branche, a.worktree, sortie)
    projet = os.path.abspath(a.projet)
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s — rien fusionné\n" % projet)
        return 1
    if not racine_du_depot(projet, sortie):
        return 1
    if noyau.relecture.git_texte(["symbolic-ref", "--short", "-q", "HEAD"], projet)[0] != 0:
        sortie.write("GARDE: HEAD détachée — rien fusionné\n")
        return 1
    if noyau.relecture.git_texte(["rev-parse", "-q", "--verify", "MERGE_HEAD"], projet)[0] == 0:
        sortie.write("GARDE: une fusion est déjà en cours (MERGE_HEAD) — rien fusionné\n")
        return 1
    code, sale = noyau.relecture.git_texte(["status", "--porcelain"], projet)
    if code != 0 or sale.strip():
        sortie.write("GARDE: arbre pas propre (%s) — rien fusionné\n" % (
            "%d chemin(s)" % len(sale.splitlines()) if code == 0 else sale))
        return 1
    if noyau.relecture.git_texte(["rev-parse", "-q", "--verify", "%s^{commit}" % a.branche], projet)[0] != 0:
        sortie.write("GARDE: branche absente : %s — rien fusionné\n" % a.branche)
        return 1
    if noyau.relecture.git_texte(["merge-base", "--is-ancestor", a.branche, "HEAD"], projet)[0] == 0:
        sortie.write("DÉJÀ %s\n" % a.branche)
        return 0
    ouvert = de_cote(projet, a.branche)
    if ouvert:
        sortie.write("GARDE: %s garde un chantier ouvert (%s) — clos-le dans son worktree d'abord, rien fusionné\n"
                     % (a.branche, ouvert))
        return 1
    return 1 if fusionner_branche(projet, a.branche, "Fusion : %s" % a.branche, sortie) else 0
