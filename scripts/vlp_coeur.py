#!/usr/bin/env python3
"""Le code de `vlp.py` (VIT5) : `vlp.py` le lance, et son `.pyc` évite de recompiler ce module à chaque
lancement. La doc des sous-commandes vit dans la docstring de `vlp.py`, et nulle part ailleurs.
"""
import argparse
import collections
import datetime
import fnmatch
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

from noyau import etat   # l'état que les tests changent, lu `etat.NOM` (REF44)
from noyau import facade   # les noms pas encore sortis, lus à l'appel par les modules (REF45)

facade.coeur.noms = globals()

from noyau.commun import *     # noqa: E402,F403 — la façade ré-exporte (REF45)
from noyau.fiches import *     # noqa: E402,F403
from noyau.carte import *      # noqa: E402,F403
from noyau.sessions import *   # noqa: E402,F403
from noyau.page import *        # noqa: E402,F403
from noyau.notes import *       # noqa: E402,F403
from noyau.feuille import *     # noqa: E402,F403
from noyau.clos import *        # noqa: E402,F403
import noyau.page   # noqa: E402 — `noyau.page.regenerer` : un test la remplace là (REF46)
from noyau.relecture import *   # noqa: E402,F403
from noyau.hooks import *       # noqa: E402,F403
from noyau.niveau import *      # noqa: E402,F403
from noyau.bac import *         # noqa: E402,F403
import noyau.relecture   # noqa: E402 — `noyau.relecture.git_texte` : un test la remplace là (REF47)


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
    if noyau.relecture.git_texte(["rev-parse", "--is-inside-work-tree"], a.projet)[0] == 0:
        code, tete = noyau.relecture.git_texte(["symbolic-ref", "--short", "-q", "HEAD"], a.projet)
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
    """`feuille` : la feuille de route régénérée, ses joints recopiés, puis les lignes `FILES` et
    `LIRE` de sa republication ; `--verifier` compare sans écrire."""
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
    sortie.write(ligne_files(joints, page) + ligne_lire(joints, page))
    sortie.write("%s · %s — %s\n" % (bilan, "inchangée" if neuf == html else "réécrite", page))
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
    code, s = noyau.relecture.git_texte(["worktree", "list", "--porcelain"], racine)
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
    trouves = (COMMIT_FICHE.match(l) for l in (s.splitlines() if code == 0 else []))
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
    ordre_de_clore(todo_dit, sortie, carte_)
    dire_sans_page(carte_, [(chemin_page, "artefact du chantier", "la page du chantier"),
                            (page, "artefact feuille de route", "la feuille de route")], sortie, gardes)
    if html is None:
        sortie.write("".join("GARDE: %s\n" % g for g in garde_page(
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
        if noyau.relecture.git_texte(["merge-base", "--is-ancestor", branche, "HEAD"], projet)[0] != 0 and de_cote(projet, branche):
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
        dans_kit = os.path.commonpath([os.path.normcase(etat.KIT), os.path.normcase(fichier)]) == os.path.normcase(etat.KIT)
    except ValueError:      # deux lecteurs différents
        dans_kit = False
    racine = kit_de(fichier) or (etat.KIT if dans_kit else os.path.dirname(fichier))
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


def verdict_juge(lignes, code, attendu):
    """Rendre (texte, code de sortie) d'un juge hors kit (`--test`, chantier ISO) — il n'imprime ni `ÉCART:`, ni
    `OK` ou `FIN:` en dernière ligne : son code de sortie tranche. Un `DÉLAI:`, une erreur Python ou une commande
    introuvable (126, 127, 9009) → `PLANTÉ` ; 0 → `VIVANT` ; sinon `ATTRAPÉ`, et avec `attendu`, la première
    ligne qui le contient — aucune, `VIVANT pour`."""
    vues = [l.strip() for l in lignes if l.strip()]
    if code in (126, 127, 9009) or any(l.startswith(("DÉLAI:", "Traceback (most recent call last)"))
                                       or re.match(r"\w+(Error|Exception):", l) for l in vues):
        return "MUTANT PLANTÉ · juge hors kit sorti %d — %s\n" % (code, " / ".join(vues[-3:])), 1
    if code == 0:
        return "MUTANT VIVANT%s · juge hors kit sorti 0\n" % (" pour %s" % attendu if attendu else ""), 1
    ligne = next((l for l in vues if attendu in l), None) if attendu else (vues[-1] if vues else "")
    if ligne is None:
        return "MUTANT VIVANT pour %s · juge hors kit sorti %d sans le dire — %s\n" % (
            attendu, code, " / ".join(vues[-3:])), 1
    return "MUTANT ATTRAPÉ · juge hors kit sorti %d — « %s »\n" % (code, ligne), 0


def attendu_au_milieu(ecarts, attendu):
    """Rendre une ligne `ATTENDU AU MILIEU` par `ÉCART:` qui contient `attendu` ailleurs qu'en tête de son libellé
    (`jouer_suite` ne reconnaît que le début, défaut `E8` vu à la clôture d'ENA), avec le début à recopier."""
    texte = ""
    for e in ecarts:
        libelle = e[len("ÉCART:"):].strip()
        i = libelle.find(attendu)
        if i > 0:
            texte += "ATTENDU AU MILIEU · « %s » est dans « %s » : --attendu \"%s\"\n" % (
                attendu, libelle, libelle[:i + len(attendu)])
    return texte


def verdict_mutant(lignes, code, attrape, attendu, juge=False):
    """Rendre (texte, code de sortie) : les `ÉCART:` vus, puis `MUTANT ATTRAPÉ`, `VIVANT` ou `PLANTÉ`. Une suite
    finie sort 0 ou dit `OK` ou `FIN:` en dernière ligne ; arrêtée avant, elle est `PLANTÉ`, écarts vus ou non. Un
    `juge` hors kit (`--test`) qui ne parle pas ainsi — ni `ÉCART:`, ni cette dernière ligne — est jugé à son code
    (`verdict_juge`). Un `attendu` non attrapé mais lu au milieu d'un écart se signale (`attendu_au_milieu`)."""
    ecarts = [l for l in lignes if l.startswith("ÉCART:")]
    texte = "".join(l + "\n" for l in ecarts)
    fin = next((l.strip() for l in reversed(lignes) if l.strip()), "")
    if juge and not (attrape or ecarts or fin == "OK" or fin.startswith("FIN:")):
        return verdict_juge(lignes, code, attendu)
    if attrape:
        return texte + "MUTANT ATTRAPÉ %d écart(s) · arrêté sur « %s »\n" % (len(ecarts), attendu), 0
    milieu = attendu_au_milieu(ecarts, attendu) if attendu else ""
    if not (code == 0 or fin == "OK" or fin.startswith("FIN:")):
        dernieres = [l.strip() for l in lignes if l.strip()][-3:]
        return texte + "MUTANT PLANTÉ · tests sortis %d sans finir, après %d écart(s) — %s\n" % (
            code, len(ecarts), " / ".join(dernieres)) + milieu, 1
    if attendu:
        return texte + "MUTANT VIVANT pour %s\n" % attendu + milieu, 1
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
    texte, code = verdict_mutant(*jouer_suite(commande, copie, attendu), attendu, juge=not vise)
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
        suite = os.path.join(racine if est_kit(racine) else etat.KIT, "scripts", "test-vlp.py")
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
    code, _ = noyau.relecture.git_texte(["check-ignore", "-q", ".claude/launch.json"], racine)
    if code == 1:
        sortie.write("GARDE: .claude/launch.json n'est pas couvert par .gitignore : il porte des chemins "
                     "de machine, et partirait dans le dépôt\n")
    return 0


def cmd_sante(a, sortie):
    """La santé du code (`sante.py`, VIT15) — chargé ici seulement : son `import ast` coûterait à chaque hook."""
    import sante
    return sante.principal(a, sortie, etat.KIT)


def py_touches(racine):
    """Rendre les `.py` ajoutés, modifiés ou neufs du dépôt de `racine` depuis `HEAD` — index et arbre de travail, lus
    par `git status` —, en chemins absolus triés ; un fichier effacé n'y est pas. Git muet : `None`."""
    code, haut = noyau.relecture.git_texte(["rev-parse", "--show-toplevel"], racine)
    if code != 0:
        return None
    code, texte = noyau.relecture.git_texte(["status", "--porcelain=v1", "-z", "--untracked-files=all"], racine)
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
    nom de module, faux d'un fichier à l'autre dans un même processus. Fichier absent, ou qui ne se lit pas en
    Python (un `.as`, `AMD1`) : `GARDE:`, sort 1 — jamais un traceback (SYM)."""
    import ast
    if not os.path.isfile(a.fichier):
        sortie.write("GARDE: %s n'est pas un fichier\n" % a.fichier)
        return 1
    try:
        with open(a.fichier, encoding="utf-8") as f:
            corps = ast.parse(f.read()).body
    except (SyntaxError, UnicodeDecodeError, ValueError) as e:
        sortie.write("GARDE: %s ne se lit pas en Python (symboles ne lit que le Python ; grep -n ailleurs) : %s\n"
                     % (a.fichier, str(e).splitlines()[0] if str(e) else type(e).__name__))
        return 1
    trouves = {n.name: n for n in corps if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    for n in a.noms or list(trouves):
        o = trouves.get(n)
        sortie.write("%s %d-%d\n" % (n, o.lineno, o.end_lineno or o.lineno) if o else "ABSENT %s\n" % n)
    return 1 if any(n not in trouves for n in a.noms) else 0


def libelle_de(noeud):
    """Le libellé d'un `verifier(<libellé>, …)` ou d'un `assert …, <libellé>` (REF5) : la chaîne telle quelle, le
    gabarit d'un `"…" % x`, la gauche d'un `+` (`libellé + diagnostic`, REF43), un f-string ses morceaux fixes ; sinon None."""
    import ast
    if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
        return noeud.value
    if isinstance(noeud, ast.BinOp) and isinstance(noeud.op, (ast.Mod, ast.Add)):
        return libelle_de(noeud.left)
    if isinstance(noeud, ast.JoinedStr):
        return "".join(str(v.value) if isinstance(v, ast.Constant) else "{}" for v in noeud.values)
    return None


def verifs_des_groupes(arbre):
    """`[(groupe, [libellés])]` pour chaque `groupe(<fonction>)` de `test-vlp.py`, dans l'ordre : les `verifier` de
    la fonction, et ceux des fonctions du module qu'elle nomme, de proche en proche (une aide compte au groupe qui
    l'appelle ; un autre groupe qu'elle nomme, non : REF43)."""
    import ast
    fonctions = {n.name: n for n in arbre.body if isinstance(n, ast.FunctionDef)}

    def propres(f):
        """Les libellés des `verifier` écrits dans `f` même."""
        return [libelle_de(c.args[0]) or "" for c in ast.walk(f) if isinstance(c, ast.Call)
                and isinstance(c.func, ast.Name) and c.func.id == "verifier" and c.args]

    def libelles(nom, vus):
        """Ceux de `nom`, puis ceux des fonctions qu'il nomme et que `vus` n'a pas encore."""
        vus.add(nom)
        nommes = {n.id for n in ast.walk(fonctions[nom]) if isinstance(n, ast.Name) and n.id in fonctions} - set(groupes)
        return propres(fonctions[nom]) + [l for autre in sorted(nommes - vus) for l in libelles(autre, vus)]

    groupes = [c.value.args[0].id for c in arbre.body if isinstance(c, ast.Expr) and isinstance(c.value, ast.Call)
               and isinstance(c.value.func, ast.Name) and c.value.func.id == "groupe" and c.value.args
               and isinstance(c.value.args[0], ast.Name) and c.value.args[0].id in fonctions]
    return [(g, libelles(g, set())) for g in groupes]


def cmd_parite(a, sortie):
    """`parite [--racine <kit>]` (REF5) : la parité entre `scripts/test-vlp.py` et la suite pytest de `tests/`. La
    marque d'un test migré : le libellé d'origine du `verifier`, mot pour mot, en message de son `assert`
    (`assert cond, "<libellé>"` ; un libellé formaté, par son gabarit). Une ligne par groupe — `MIGRÉ <groupe> n/n`,
    `PARTIEL <groupe> k/n — manque : <libellés>`, `RESTE <groupe> 0/n` —, puis `PARITE …` et les comptes bruts.
    Un groupe ne sort de `test-vlp.py` que sur un `MIGRÉ`. Fichier absent ou illisible : `GARDE:`, sort 1."""
    import ast
    racine = os.path.abspath(a.racine or etat.KIT)
    try:
        with open(os.path.join(racine, "scripts", "test-vlp.py"), encoding="utf-8") as f:
            groupes = verifs_des_groupes(ast.parse(f.read()))
        migres = set()
        for chemin in sorted(glob.glob(os.path.join(racine, "tests", "**", "*.py"), recursive=True)):
            with open(chemin, encoding="utf-8") as f:
                migres.update(libelle_de(n.msg) for n in ast.walk(ast.parse(f.read()))
                              if isinstance(n, ast.Assert) and n.msg is not None)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as e:
        sortie.write("GARDE: parite ne lit pas %s : %s\n" % (racine, str(e).splitlines()[0] if str(e) else type(e).__name__))
        return 1
    etats = collections.Counter()
    trouvees = total = 0
    for nom, libelles in groupes:
        manque = [l for l in libelles if l not in migres]
        k, n = len(libelles) - len(manque), len(libelles)
        trouvees, total = trouvees + k, total + n
        if not manque:
            etats["migrés"] += 1
            sortie.write("MIGRÉ %s %d/%d\n" % (nom, k, n))
        elif k:
            etats["partiels"] += 1
            sortie.write("PARTIEL %s %d/%d — manque : %s\n" % (nom, k, n, " ; ".join(dict.fromkeys(manque))))
        else:
            etats["restent"] += 1
            sortie.write("RESTE %s 0/%d\n" % (nom, n))
    sortie.write("PARITE %d groupes · migrés %d · partiels %d · restent %d · vérifications %d/%d\n" % (
        len(groupes), etats["migrés"], etats["partiels"], etats["restent"], trouvees, total))
    return 0


# --- ordre : l'enchaînement entre projets (chantier ORD) ---------------------

def tables_ordre(lignes):
    """{titre de section `## `: [cellules de chaque ligne de table, en-tête et séparateur ôtés]} de la source."""
    tables, titre, entete = {}, None, False
    for l in lignes:
        if l.startswith("## "):
            titre, entete = l[3:].strip(), True
            tables[titre] = []
        elif titre and l.startswith("|"):
            if not entete and not SEPARATEUR.match(l):
                tables[titre].append(cellules_de(l, "%s, %s" % (titre, l.split("|")[1].strip())))
            entete = False
    return tables


def todo_projet(racine, sortie):
    """(lignes de TODO, chemins lus) d'un projet équipé, de chaque fichier de sa ligne **chantiers possibles**
    (comme `imprimer_todo`) ; un fichier introuvable ou une table cassée : une `GARDE:`, le fichier sauté."""
    possibles = CHANTIERS_POSSIBLES.search(lire(os.path.join(racine, "CHANTIER.md")))
    rangs, lus = [], []
    for chemin in chemins_md(possibles.group(1), racine) if possibles else []:
        try:
            rangs += todo_du_fichier(lignes_du_projet(racine, chemin, "fichier"))
            lus.append(chemin)
        except (Absent, ValueError) as e:
            sortie.write("GARDE: %s — %s\n" % (os.path.basename(racine), e))
    return rangs, lus


def prose_ordre(lignes):
    """{titre de section `## `: [texte de chaque puce]} de la source : une puce commence par `- `, ses lignes
    indentées la continuent. Le texte reste en markdown (accents graves, gras) : la page l'affiche en texte, jamais
    en HTML, car la base `db` qui peut le remplacer s'écrit hors du script (ORD4)."""
    prose, titre = {}, None
    for l in lignes:
        if l.startswith("## "):
            titre = l[3:].strip()
        elif titre and l.startswith("- "):
            prose.setdefault(titre, []).append(l[2:].strip())
        elif titre in prose and l.startswith("  ") and l.strip():
            prose[titre][-1] += " " + l.strip()
    return prose


def piste_ordre(todo):
    """Les lignes de la TODO du projet de la source, dans son ordre : code (le premier entre accents graves,
    sinon `n° <numéro>`), nom, phase, score et fiches (bas, haut) — le second graphique de la page."""
    piste = []
    for numero, chantier, _, cout, _ in todo:
        codes = CODE.findall(chantier)
        phase, score, _, _ = phase_todo(cout)
        bornes = bornes_cout(cout)
        piste.append({"code": codes[0] if codes else "n° %s" % numero,
                      "nom": nom_todo(chantier, codes[0]) if codes else chantier.strip(), "phase": phase,
                      "score": int(score) if score and score.isdigit() else None,
                      "bas": bornes and bornes[0], "haut": bornes and bornes[1], "fait": False, "note": ""})
    return piste


def taux_ordre(racine):
    """{usd, clos} : le prix d'une fiche au prix mesuré des chantiers clos du projet (celui de `taux_jour`),
    arrondi au cent ; `None` sans feuille de route ou sans clos au prix mesuré."""
    page = page_clos(racine)
    if not os.path.isfile(page):
        return None
    _, n_fiches, n_clos, usd, fiches_usd = moyenne_clos(lire(page))
    if not n_fiches or usd is None:
        return None
    return {"usd": round(usd_par_fiche(usd, fiches_usd), 2), "clos": n_clos}


def nom_todo(chantier, code):
    """Le nom d'un chantier de TODO sans son code : `🔴📅 \\`SCH\\` — Un numéro…` → `Un numéro…` ;
    `La course et la marge (\\`C2\\`)` → `La course et la marge`."""
    nom = re.sub(r"\s*\([^()]*`%s`[^()]*\)" % re.escape(code), "", chantier)
    return re.sub(r"^[^`\w]*`%s`\s*—\s*" % re.escape(code), "", nom).strip()


def pas_ordre(code, cle, todo, nom_src, cout_src):
    """Le pas `code` du projet `cle` : sa ligne de TODO (celle dont la cellule « Chantier » le porte entre accents
    graves), sinon le nom et le coût de la source (`✅ …` : fait). Rend (pas, origine, garde) — origine `todo`,
    `source` ou `None` ; garde : le texte d'une `GARDE:`, ou `None`."""
    lignes = [r for r in todo if code in CODE.findall(r[1])]
    if len(lignes) > 1:
        return None, None, "pas %s (%s) : %d lignes de TODO le portent (n° %s)" % (
            code, cle, len(lignes), ", ".join(r[0] for r in lignes))
    if lignes:
        numero, chantier, _, cout, depend = lignes[0]
        phase, score, _, _ = phase_todo(cout)
        bornes = bornes_cout(cout)
        return {"projet": cle, "code": code, "numero": numero, "nom": nom_todo(chantier, code), "phase": phase,
                "score": int(score) if score and score.isdigit() else None,
                "bas": bornes and bornes[0], "haut": bornes and bornes[1], "fait": False,
                "note": cout_src, "depend": depend}, "todo", None
    fait = cout_src.startswith("✅")
    bornes = None if fait else bornes_cout(cout_src)
    if not fait and bornes is None:
        return None, None, "pas %s (%s) : ni dans la TODO, ni un coût en fiches dans la source" % (code, cle)
    return {"projet": cle, "code": code, "numero": None, "nom": nom_src or None, "phase": None, "score": None,
            "bas": bornes and bornes[0], "haut": bornes and bornes[1], "fait": fait,
            "note": cout_src if fait else "", "depend": ""}, "source", None


def somme_ordre(liste):
    """Le nombre de pas, et la somme de leurs fiches (bas, haut) — les pas chiffrés seuls."""
    chiffres = [p for p in liste if p["haut"] is not None]
    return {"pas": len(liste), "bas": sum(p["bas"] for p in chiffres), "haut": sum(p["haut"] for p in chiffres)}


def totaux_ordre(pas):
    """Les totaux des pas : nombre, fiches (bas, haut) des pas chiffrés, codes faits et non chiffrés, et par projet."""
    return dict(somme_ordre(pas), faits=[p["code"] for p in pas if p["fait"]],
                non_chiffres=[p["code"] for p in pas if not p["fait"] and p["haut"] is None],
                par_projet={cle: somme_ordre([p for p in pas if p["projet"] == cle])
                            for cle in dict.fromkeys(p["projet"] for p in pas)},
                par_niveau={n: somme_ordre([p for p in pas if p.get("niveau") == n]) for n in NIVEAUX_ORDRE})


def numeros_todo(todos):
    """{projet: {numéros des lignes de sa TODO}} : un numéro dans « Dépend de » se lit contre eux."""
    return {cle: {r[0] for r in todo} for cle, todo in todos.items()}


NIVEAUX_ORDRE = ("obligatoire", "conseillé", "à la marge")


def cle_pas(p):
    """La clé d'un pas dans le graphe : (projet, code)."""
    return p["projet"], p["code"]


def pas_du_code(code, projet, pas):
    """Les pas du chemin qui portent `code` : celui du projet `projet` s'il y est, sinon ceux des autres projets —
    `[]` hors du chemin, plusieurs : ambigu."""
    memes = [p for p in pas if p["code"] == code]
    return [p for p in memes if p["projet"] == projet] or memes


def deps_todo(p, pas, numeros):
    """(pas dont `p` dépend, nombre hors du chemin, gardes, illisible) lus dans sa cellule « Dépend de » : les codes
    entre accents graves (un autre projet compris), et les numéros de ligne de la TODO de son projet."""
    brut = p["depend"].strip()
    codes = CODE.findall(brut)
    nombres = re.findall(r"(?<![\w-])\d+(?![\w-])", CODE.sub("", brut))
    deps, hors, gardes = [], 0, []
    for code in codes:
        trouves = pas_du_code(code, p["projet"], pas)
        if len(trouves) > 1:
            gardes.append("pas %s : dépend de %s, que %d projets portent" % (p["code"], code, len(trouves)))
        deps += trouves[:1]
        hors += not trouves
    for n in nombres:
        trouves = [q for q in pas if q["projet"] == p["projet"] and q["numero"] == n]
        if not trouves and n not in numeros.get(p["projet"], ()):
            gardes.append("pas %s : dépend de la ligne %s, absente de la TODO de %s" % (p["code"], n, p["projet"]))
        deps += trouves[:1]
        hors += not trouves and n in numeros.get(p["projet"], ())
    return [d for d in deps if d is not p], hors, gardes, brut not in ("", "—") and not codes and not nombres


def ajouts_ordre(lignes, pas, sautes):
    """({clé: [clés]} des dépendances que la source ajoute, gardes) : une ligne `| pas | dépend de | pourquoi |` ;
    un pas ou une dépendance introuvable, ou sans raison, une garde ; d'un projet absent, la ligne sautée."""
    ajouts, gardes = {}, []
    for cellules in lignes:
        code, depend, pourquoi = (cellules + ["", ""])[:3]
        code, depend = (CODE.findall(code) or [code])[0], CODE.findall(depend)
        if code in sautes or sautes.intersection(depend):
            continue
        porteurs = pas_du_code(code, None, pas)
        cibles = [pas_du_code(d, porteurs[0]["projet"], pas) for d in depend] if len(porteurs) == 1 else []
        if not pourquoi.strip() or not cibles or any(len(c) != 1 for c in cibles):
            gardes.append("dépendance ajoutée %s → %s : pas, dépendance ou raison introuvable" % (code, ", ".join(depend)))
            continue
        ajouts.setdefault(cle_pas(porteurs[0]), []).extend(cle_pas(c[0]) for c in cibles)
    return ajouts, gardes


def forces_ordre(lignes, pas, sautes):
    """({clé: niveau} que la source force, gardes) : une ligne `| pas | niveau | pourquoi |`, le niveau l'un de
    `NIVEAUX_ORDRE` ; un pas introuvable, un niveau inconnu ou sans raison, une garde."""
    forces, gardes = {}, []
    for cellules in lignes:
        code, niveau, pourquoi = (cellules + ["", ""])[:3]
        code = (CODE.findall(code) or [code])[0]
        if code in sautes:
            continue
        porteurs = pas_du_code(code, None, pas)
        if len(porteurs) != 1 or niveau.strip() not in NIVEAUX_ORDRE or not pourquoi.strip():
            gardes.append("niveau forcé de %s : pas, niveau (%s) ou raison introuvable" % (code, " | ".join(NIVEAUX_ORDRE)))
            continue
        forces[cle_pas(porteurs[0])] = niveau.strip()
    return forces, gardes


def graphe_ordre(pas, ajouts, numeros):
    """(graphe {clé: {clés dont il dépend}}, compte des dépendances lues en TODO, écrites par la source, hors du
    chemin, gardes) ; une cellule « Dépend de » illisible n'est une garde que si la source n'ajoute rien au pas."""
    graphe, compte, gardes = {}, {"todo": 0, "source": 0, "hors": 0}, []
    for p in pas:
        deps, hors, g, illisible = deps_todo(p, pas, numeros)
        lues = {cle_pas(d) for d in deps}
        ajoutees = set(ajouts.get(cle_pas(p), [])) - lues
        if illisible and not ajoutees:
            g.append("pas %s : dépendance illisible « %s »" % (p["code"], p["depend"].strip()))
        graphe[cle_pas(p)] = lues | ajoutees
        compte["todo"] += len(lues)
        compte["source"] += len(ajoutees)
        compte["hors"] += hors
        gardes += g
    return graphe, compte, gardes


def graines_ordre(cibles, pas, forces):
    """(clés obligatoires d'office : la cible, et les pas forcés obligatoires ; gardes pour un code de la cible
    absent du chemin)."""
    graines, gardes = {k for k, n in forces.items() if n == NIVEAUX_ORDRE[0]}, []
    for projet, codes in cibles.items():
        for code in codes:
            if (projet, code) in {cle_pas(p) for p in pas}:
                graines.add((projet, code))
            else:
                gardes.append("cible %s (%s) : absente du chemin" % (code, projet))
    return graines, gardes


def niveaux_ordre(pas, graphe, graines, forces):
    """({clé: niveau}, gardes) : obligatoire, les graines et ce dont elles dépendent, de proche en proche ; puis
    conseillé, une phase `V1` ; à la marge, `V2`, `V3`… ou `après`. Un niveau forcé l'emporte ; un pas sans phase,
    ni obligatoire ni forcé, une garde — jamais un niveau deviné."""
    obligatoires = set(graines)
    pile = list(obligatoires)
    while pile:
        for dep in graphe[pile.pop()]:
            if dep not in obligatoires:
                obligatoires.add(dep)
                pile.append(dep)
    niveaux, gardes = {}, []
    for p in pas:
        k = cle_pas(p)
        if k in forces or k in obligatoires:
            niveaux[k] = forces.get(k, NIVEAUX_ORDRE[0])
        elif p["phase"]:
            niveaux[k] = NIVEAUX_ORDRE[1] if p["phase"] == "V1" else NIVEAUX_ORDRE[2]
        else:
            gardes.append("pas %s : ni obligatoire, ni une phase dans la TODO — la source doit forcer son niveau"
                          % p["code"])
    return niveaux, gardes


def vagues_ordre(pas, graphe):
    """(vagues, garde) : une vague par niveau du tri topologique (`graphlib`), ses pas dans l'ordre du chemin ;
    un cycle, une garde qui le nomme."""
    import graphlib
    tri = graphlib.TopologicalSorter(graphe)
    try:
        tri.prepare()
    except graphlib.CycleError as e:
        return [], "cycle de dépendances : %s" % " → ".join(code for _, code in e.args[1])
    rang = {cle_pas(p): i for i, p in enumerate(pas)}
    vagues = []
    while tri.is_active():
        pretes = sorted(tri.get_ready(), key=lambda k: rang[k])
        vagues.append(pretes)
        tri.done(*pretes)
    return vagues, None


def classer_ordre(pas, tables, cibles, numeros, sautes):
    """Le niveau et la vague de chaque pas, écrits dans le pas ; rend (vagues en codes, compte des dépendances,
    gardes) — une garde, rien d'écrit."""
    ajouts, gardes = ajouts_ordre(tables.get("Les dépendances ajoutées", []), pas, sautes)
    forces, g_forces = forces_ordre(tables.get("Les niveaux forcés", []), pas, sautes)
    graphe, compte, g_graphe = graphe_ordre(pas, ajouts, numeros)
    graines, g_graines = graines_ordre(cibles, pas, forces)
    gardes += g_forces + g_graphe + g_graines
    niveaux, g_niveaux = niveaux_ordre(pas, graphe, graines, forces) if not gardes else ({}, [])
    vagues, cycle = vagues_ordre(pas, graphe) if not gardes else ([], None)
    gardes += g_niveaux + ([cycle] if cycle else [])
    if gardes:
        return [], compte, gardes
    for i, vague in enumerate(vagues):
        for k in vague:
            p = next(q for q in pas if cle_pas(q) == k)
            p["niveau"], p["vague"] = niveaux[k], i
    return [[code for _, code in v] for v in vagues], compte, []


def projets_ordre(lignes, racine, sortie):
    """({clé: lignes de TODO}, [clés absentes], [projets présents : clé, nom, TODO lues, racine ou non]) des
    projets de la source — `| clé | dossier | nom |`, le nom facultatif : un dossier cherché à côté de `racine`,
    `.` étant `racine` même ; absent ou non équipé, une `GARDE:` le dit, et ses pas seront sautés."""
    todos, absents, infos = {}, [], []
    for cellules in lignes:
        cle, dossier, nom = (cellules + ["", ""])[:3]
        dossier = (CODE.findall(dossier) or [dossier])[0]
        chemin = racine if dossier == "." else os.path.join(os.path.dirname(racine), dossier)
        if equipe(chemin):
            todos[cle], lus = todo_projet(chemin, sortie)
            infos.append({"cle": cle, "nom": nom.strip() or cle, "todo": lus, "racine": dossier == "."})
        else:
            absents.append(cle)
            sortie.write("GARDE: projet %s absent : %s n'est pas un dossier équipé à côté du kit ; ses pas sautés\n"
                         % (cle, dossier))
    return todos, absents, infos


def chemin_ordre(lignes, todos, absents):
    """(pas, origines, gardes) des lignes du chemin, dans l'ordre : le pas d'un projet absent est sauté, celui d'un
    projet inconnu ou introuvable donne le texte d'une `GARDE:`."""
    pas, origines, gardes = [], [], []
    for cellules in lignes:
        code, cle, nom_src, cout_src = (cellules + ["", "", ""])[:4]
        code = (CODE.findall(code) or [code])[0]
        if cle in absents:
            continue
        if cle not in todos:
            gardes.append("pas %s : projet %s inconnu de la table « Les projets »" % (code, cle))
            continue
        un, origine, garde = pas_ordre(code, cle, todos[cle], nom_src, cout_src)
        if garde:
            gardes.append(garde)
        else:
            pas.append(un)
            origines.append(origine)
    return pas, origines, gardes


BALISE_ORDRE = "<données>"   # la seule balise du gabarit : un seul bloc JSON, jamais citée ailleurs


def page_ordre(dossier, donnees, sortie):
    """Écrire `ordre.html` dans `dossier` : le gabarit `GABARIT_ORDRE`, sa balise remplacée par `donnees` en JSON
    (`<` échappé, rien ne ferme le script) ; puis ses joints, et la ligne `FILES` comme `vlp.py page`. Balise
    absente ou en double : une `GARDE:`, rien d'écrit, sort 1."""
    gabarit = lire(etat.GABARIT_ORDRE)
    if gabarit.count(BALISE_ORDRE) != 1:
        sortie.write("GARDE: %s : la balise %s y est %d fois, attendu 1\n"
                     % (etat.GABARIT_ORDRE, BALISE_ORDRE, gabarit.count(BALISE_ORDRE)))
        return 1
    page = os.path.join(dossier, "ordre.html")
    with open(page, "w", encoding="utf-8", newline="\n") as f:
        f.write(gabarit.replace(BALISE_ORDRE, json.dumps(donnees, ensure_ascii=False).replace("<", "\\u003c")))
    sortie.write("PAGE %s\n" % page)
    sortie.write(ligne_files(recopier_joints(dossier), page))
    return 0


def donnees_ordre(dossier, donnees, db, sortie):
    """Écrire `donnees.json` dans `dossier`, puis `ÉCRIT` ; avec `db`, compact — l'objet du document `donnees` de la
    collection `ordre`, tel qu'`ArtifactData` l'envoie par `file_path` — et la ligne `DB` : sa taille face à
    `LIMITE_DOC_DB` ; passé un dixième, un `AVERTISSEMENT:` (un seul document ne suffira plus longtemps) ; passé la
    limite, une `GARDE:`, rien d'écrit. Rend 1 sur une garde, sinon 0."""
    texte = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")) if db \
        else json.dumps(donnees, ensure_ascii=False, indent=1)
    taille = len(texte.encode("utf-8"))
    if db and taille > etat.LIMITE_DOC_DB:
        sortie.write("GARDE: ordre/donnees : %d octets, au-delà de la limite d'un document db (%d)\n"
                     % (taille, etat.LIMITE_DOC_DB))
        return 1
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "donnees.json")
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte + "\n")
    sortie.write("ÉCRIT %s\n" % chemin)
    if db:
        sortie.write("DB ordre/donnees %d octets · limite %d · %.1f %%\n"
                     % (taille, etat.LIMITE_DOC_DB, 100.0 * taille / etat.LIMITE_DOC_DB))
        if taille * 10 > etat.LIMITE_DOC_DB:
            sortie.write("AVERTISSEMENT: ordre/donnees passe le dixième de la limite d'un document db : "
                         "le découper avant qu'elle ne bloque\n")
    return 0


def cmd_ordre(a, sortie):
    """`vlp.py ordre [--json | --db]` : lire la source (`context AI/ordre.md` du kit, ou `--source`), puis la TODO
    de chaque projet qu'elle nomme — cherché à côté du projet de la source, `.` étant ce projet même —, et écrire
    `ordre/donnees.json` à côté de la source : un pas par ligne du chemin, puis les totaux (`donnees_ordre`) ; sans
    option, aussi la page `ordre/ordre.html` et ses joints (`page_ordre`). Projet absent : une `GARDE:`, ses pas sautés. Un pas
    introuvable sans coût dans la source, ou porté par deux lignes : une `GARDE:` qui le nomme, rien d'écrit,
    sort 1."""
    # realpath : lancé par le plugin, KIT est la jonction `~/.claude/skills/vlp` ; les voisins sont à côté du vrai kit
    source = os.path.realpath(a.source or etat.SOURCE_ORDRE or os.path.join(etat.KIT, "context AI", "ordre.md"))
    lignes = lignes_gardees(source, "source de l'ordre")
    tables = tables_ordre(lignes)
    racine = trouver(os.path.dirname(source))
    if racine is None:
        sortie.write("GARDE: %s n'est dans aucun projet équipé (pas de CHANTIER.md au-dessus)\n" % source)
        return 1
    todos, absents, infos = projets_ordre(tables.get("Les projets", []), racine, sortie)
    chemin_pas = tables.get("Le chemin conseillé", [])
    pas, origines, gardes = chemin_ordre(chemin_pas, todos, absents)
    cibles = {cle: CODE.findall(codes) for cle, codes in tables.get("La cible", []) if cle not in absents}
    sautes = {(CODE.findall(c[0]) or [c[0]])[0] for c in chemin_pas if len(c) > 1 and c[1] in absents}
    vagues, compte, gardes_classement = classer_ordre(pas, tables, cibles, numeros_todo(todos), sautes) \
        if not gardes else ([], {}, [])
    for g in gardes + gardes_classement:
        sortie.write("GARDE: %s\n" % g)
    if gardes or gardes_classement:
        return 1
    donnees = {"source": os.path.relpath(source, racine).replace("\\", "/"),
               "date": __import__("datetime").date.today().isoformat(), "projets": infos, "cible": cibles,
               "projets_absents": absents, "pas": pas, "vagues": vagues, "dependances": compte,
               "totaux": totaux_ordre(pas), "prose": prose_ordre(lignes),
               "piste": piste_ordre(next((todos[p["cle"]] for p in infos if p["racine"]), [])),
               "taux": taux_ordre(racine)}
    dossier = os.path.join(os.path.dirname(source), "ordre")
    sortie.write("ORDRE %d pas · %d trouvés en TODO · %d pris de la source\n"
                 % (len(chemin_pas), origines.count("todo"), origines.count("source")))
    par_niveau = donnees["totaux"]["par_niveau"]
    sortie.write("CLASSEMENT %d obligatoires · %d conseillés · %d à la marge · %d vagues · dépendances : %d lues en "
                 "TODO, %d écrites par la source, %d hors du chemin\n"
                 % (tuple(par_niveau[n]["pas"] for n in NIVEAUX_ORDRE)
                    + (len(vagues), compte["todo"], compte["source"], compte["hors"])))
    if donnees_ordre(dossier, donnees, a.db, sortie):
        return 1
    return 0 if a.json or a.db else page_ordre(dossier, donnees, sortie)


def dit_aucun(carte_, nom):
    """Vrai si la ligne `nom` de `CHANTIER.md` (`carte_`) existe et vaut « aucun » ou « aucune » : le projet n'a pas
    cette page, et le veut ; une ligne absente n'en dit rien."""
    valeur = champ(carte_, nom)
    return valeur is not None and valeur.strip().lower() in ("aucun", "aucune")


def garde_page(carte_, nom, garde):
    """`[garde]` pour une page absente, `[]` si `CHANTIER.md` dit sa ligne `nom` « aucun » (`dit_aucun`) : voulu."""
    return [] if dit_aucun(carte_, nom) else [garde]


def dire_sans_page(carte_, pages, sortie, gardes):
    """Dire les `gardes` de `clore`, puis une ligne `SANS PAGE <pages> — CHANTIER.md dit « aucun »` pour les
    `pages` — (chemin, ligne de `CHANTIER.md`, nom) — absentes et dites « aucun » ; rien s'il n'y en a pas
    (chantier ISO)."""
    sortie.write("".join("GARDE: %s — le reste est écrit\n" % g for g in gardes))
    sans = [nom for chemin, ligne, nom in pages if not os.path.isfile(chemin) and dit_aucun(carte_, ligne)]
    if sans:
        sortie.write("SANS PAGE %s — CHANTIER.md dit « aucun »\n" % ", ".join(sans))


def ordre_de_clore(todo_dit, sortie, carte_=()):
    """Dire `todo_dit`, la ligne de la TODO d'une clôture ; puis, quel que soit le projet clos, refaire les données
    de la page d'enchaînement du kit (`cmd_ordre --db` sur `SOURCE_ORDRE`) et la ligne `ORDRE envoyer
    <donnees.json> → <URL>` — l'URL lue à la ligne `artefact enchaînement` du `CHANTIER.md` du projet de la source.
    Sauf si le `CHANTIER.md` du projet clos (`carte_`) dit cette ligne « aucun » (`dit_aucun`, chantier ISO) : rien.
    Source absente, ou une garde d'`ordre` : une `GARDE:`, la clôture continue."""
    sortie.write(todo_dit + "\n")
    if etat.SOURCE_ORDRE is None or dit_aucun(carte_, "artefact enchaînement"):
        return
    source = os.path.realpath(etat.SOURCE_ORDRE)
    if not os.path.isfile(source):
        sortie.write("GARDE: ordre : source introuvable (%s) — page d'enchaînement non refaite\n" % source)
        return
    tampon = io.StringIO()
    try:
        code = cmd_ordre(argparse.Namespace(source=source, json=False, db=True), tampon)
    except ValueError as e:
        code = 1
        tampon.write("GARDE: %s\n" % e)
    for ligne in tampon.getvalue().splitlines():
        if ligne.startswith(("GARDE:", "AVERTISSEMENT:")):
            sortie.write("%s — page d'enchaînement non refaite\n" % ligne if code else ligne + "\n")
    if code:
        return
    url = champ(lignes_de(os.path.join(trouver(os.path.dirname(source)) or etat.KIT, "CHANTIER.md")),
                "artefact enchaînement", "aucune")
    sortie.write("ORDRE envoyer %s → %s\n" % (os.path.join(os.path.dirname(source), "ordre", "donnees.json"), url))


def options_outils(sous):
    """Déclarer les lignes de commande des outils : `bac`, `claude`, `kit-essai`, `symboles`, `rapide`, `lancables`,
    `commiter`, `ordre`."""
    la = sous.add_parser("lancables")
    la.add_argument("fichier")
    la.add_argument("--max", type=int, default=2)
    la.add_argument("--tourne", nargs="*", default=[])
    cm = sous.add_parser("commiter")
    cm.add_argument("fichier")
    cm.add_argument("fiche")
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
    sous.add_parser("parite").add_argument("--racine")
    od = sous.add_parser("ordre")
    od.add_argument("--json", action="store_true")
    od.add_argument("--db", action="store_true")
    od.add_argument("--source")
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
    ot.add_argument("--fait", action="store_true")


def options_marques(sous):
    """Déclarer la ligne de commande de `ouverts` et de `pause`, les lecteur et poseur des marques (NUI21, NUI30), et
    de `postit`, le poseur du post-it d'un worktree (ISO8)."""
    ou = sous.add_parser("ouverts")
    ou.add_argument("projet")
    ou.add_argument("--rev")
    po = sous.add_parser("postit")
    po.add_argument("dossier")
    po.add_argument("fichier")
    pa = sous.add_parser("pause")
    pa.add_argument("fichier")
    pa.add_argument("raison")
    pa.add_argument("--date")


def options_fusionner(sous):
    """Déclarer la ligne de commande de `fusionner` : la fusion du jour (NUI26), ou, avec `--worktree`, la branche
    d'une fiche (ISO4)."""
    fu = sous.add_parser("fusionner")
    fu.add_argument("projet")
    fu.add_argument("branche")
    fu.add_argument("--worktree")


def options_etat(sous):
    """Déclarer la ligne de commande de `etat` : le nom du fichier d'état, ou, avec `--texte`, un texte ajouté à sa
    fin (ISO5)."""
    et = sous.add_parser("etat")
    et.add_argument("contexte")
    et.add_argument("--texte")


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
    options_etat(sous)
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
    options_fusionner(sous)
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
    "forme": cmd_forme, "ouverts": cmd_ouverts, "postit": cmd_postit, "pause": cmd_pause, "plan": cmd_plan, "matin": cmd_matin, "fusionner": cmd_fusionner,
    "sante": cmd_sante, "symboles": cmd_symboles, "parite": cmd_parite, "compteur": cmd_compteur, "carte": cmd_carte,
    "rapide": cmd_rapide, "essai": cmd_essai, "lancables": cmd_lancables,
    "commiter": cmd_commiter, "ordre": cmd_ordre, "etat": cmd_etat,
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
        return cmd_chef_page(a.questions, a.sortie, sortie, lire(os.path.join(etat.KIT, GABARIT_CHOIX)))
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
