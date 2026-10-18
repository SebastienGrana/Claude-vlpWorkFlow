"""Ouvrir un chantier : sa marque, son fichier de fiches, sa page (REF48 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import argparse
import os
import re

from noyau.commun import (TITRE, lignes_de, lignes_gardees, lire)
from noyau.carte import (equipe)
from noyau.sessions import (sessions_de)
from noyau.page import (approx)
from noyau.feuille import (bornes, champ, lettre_de, page_clos, retirer_chevrons_url)
from noyau.clos import (PRIX_CLOS, lignes_clos)
from noyau.nuit import (usd_par_fiche)
from noyau.clore import (
    MARQUE_CLOS,
    MARQUE_OUVERT,
    MARQUE_PAUSE,
    OUVERT_LIGNE,
    PAUSE_LIGNE,
    courant_de,
    ouverts_ailleurs,
    poser_marque,
    postit,
    rang_routage_ouvrir,
)

__all__ = [
    "LIGNE_FICHIER", "PLAGE_FICHES", "TOTAL_MESURE", "moyenne_clos", "decimal_fr", "nombre_fiches", "lever_pause",
    "cmd_ouvrir", "cmd_pause",
]


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
            rang = rang_routage_ouvrir(cl)
            if rang is None:
                gardes.append("aucune ligne « relire un chantier clos », « relire le chantier » ni **clos** dans CLAUDE.md")
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
