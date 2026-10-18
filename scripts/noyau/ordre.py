"""L'ordre : l'enchaînement entre projets, et les gardes de page de `clore` (REF49 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import argparse
import io
import json
import os
import re

from noyau import etat
from noyau.commun import (Absent, CHANTIERS_POSSIBLES, lignes_de, lignes_du_projet, lignes_gardees, lire)
from noyau.carte import (chemins_md, equipe, trouver)
from noyau.page import (ligne_files, recopier_joints)
from noyau.notes import (CODE, cellules_de)
from noyau.feuille import (SEPARATEUR, bornes_cout, champ, page_clos, phase_todo, todo_du_fichier)
from noyau.nuit import (usd_par_fiche)
from noyau.ouvrir import (moyenne_clos)

__all__ = [
    "tables_ordre", "todo_projet", "prose_ordre", "piste_ordre", "taux_ordre", "nom_todo", "pas_ordre",
    "somme_ordre", "totaux_ordre", "numeros_todo", "NIVEAUX_ORDRE", "cle_pas", "pas_du_code", "deps_todo",
    "ajouts_ordre", "forces_ordre", "graphe_ordre", "graines_ordre", "niveaux_ordre", "vagues_ordre",
    "classer_ordre", "projets_ordre", "chemin_ordre", "BALISE_ORDRE", "page_ordre", "donnees_ordre", "cmd_ordre",
    "dit_aucun", "garde_page", "dire_sans_page", "ordre_de_clore",
]


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
