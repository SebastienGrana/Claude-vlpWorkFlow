"""La nuit : le fichier des nuits, le tri et le plan du soir, la page à cartes du chef (REF48 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import datetime
import glob
import json
import os
import re
import shlex
import statistics

import carnet

from noyau.facade import coeur
import noyau.relecture   # `noyau.relecture.<nom>` : un test remplace ce nom là
from noyau.commun import (PREFIXE, lignes_de, lignes_du_projet, lire)
from noyau.fiches import (MARQUE_VISUELLE)
from noyau.carte import (equipe, imprimer_section)
from noyau.page import (approx, esc, ligne_files, ligne_lire, recopier_joints)
from noyau.notes import (CODE, cellules_de)
from noyau.feuille import (
    GROS_FICHES,
    borne_haute_cout,
    cellule_md,
    champ,
    couts_du_projet,
    dependances,
    est_bloque,
    feuille,
    lettre_de,
    lettres_prises,
    page_clos,
    page_feuille,
    todo_du_fichier,
)
from noyau.clos import (COMMENTAIRE, defauts_page, ecrire_couts, textes_visibles)
from noyau.hooks import (EMOJIS_JAUGE, JAUGE)
from noyau.bac import (lire_arg)

__all__ = [
    "LECON_INDICE", "LECONS_MAX", "CARNET_MIN", "NUITS_TETE", "LIGNE_NUMERO", "LECON_FORME", "fichier_nuits",
    "sections_nuits", "nuits_du_fichier", "ecrire_lignes", "nuits_ecrire", "nuits_retirer", "usd_par_fiche",
    "taux_jour", "taux_nuit", "lignes_taux_nuit", "lecons_nuits", "MARQUE_PUSH", "MARQUES_TRI", "EXTENSIONS_TRI",
    "marques_tri", "fichiers_tri", "groupes_tri", "codes_todo", "trier", "cmd_trier", "CANAUX", "PLAN_BORNE",
    "PLAN_CHANTIER", "plan_valider", "plan_section", "fin_de_section", "plan_poser", "plan_ecrire", "plan_lire",
    "cmd_plan", "cmd_feuille", "GABARIT_CHOIX", "TETE_CHOIX", "CLASSE_JAUGE", "CHAMPS_DECISION", "EMOJI_MAL",
    "morceaux_choix", "texte_json", "liste_json", "objet_json", "attribut", "html_jauge", "html_decision",
    "html_question", "sections_choix", "explique_json", "page_choix", "cmd_chef_page",
]


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
    _, n_fiches, n_clos, usd, fiches_usd = coeur.moyenne_clos(lire(page))
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
    return "TAUX nuit médiane %s $/fiche sur %d fiches acceptées%s" % (coeur.decimal_fr(round(mediane, 2)), n, reste)


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
                raisons.append("gros : jusqu'à %s fiches" % coeur.decimal_fr(borne))
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
