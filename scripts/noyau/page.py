"""La page d'un chantier : régénérée depuis son fichier de fiches, états, coûts, date (REF46 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import hashlib
import json
import os
import re

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (ALIAS, TITRE, lignes_de, lire)
from noyau.fiches import (CRITERE_VISUEL, croisent)
from noyau.carte import (trouver)
from noyau.sessions import (essais_de, heure_clore, sessions_de, sessions_entete)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). La décision
# sortie de Git par REF46, `heures_du_log`, se lit ici seulement.
__all__ = [
    "SEUIL_PAGE", "GABARIT", "JOINTS", "recopier_joints", "PUBLIE", "empreinte", "notes_publie", "texte_publie",
    "lire_publie", "noter_publie", "joints_changes", "ligne_files", "ligne_lire", "cmd_joints", "LI_FICHE",
    "UL_FICHES", "COUT", "mesure", "esc", "milliers", "arrondi", "dollars", "approx", "ligne_cout",
    "fiches_du_fichier", "DEPEND", "PLAGE_DEPEND", "VISUEL", "deplier_plages", "apercu_fiches", "pretes",
    "apercu_lancables", "lancables", "indices", "cmd_lancables", "fleche", "libelle_calcule", "lis_page", "etats",
    "triplet", "moins", "COMMIT_FICHE", "COMMIT_FUSION", "INFINI", "heures_commits", "plages",
    "transcripts_du_fichier", "plages_du_cout", "sous_agents_nommes", "plages_du_transcript", "parts_aux_commits",
    "essais_entiers", "plus", "ligne_parts", "couts_aux_commits", "couts", "comptage", "nom_du_projet", "creer",
    "STYLE_INLINE", "migrer_style", "META_CHARSET", "SCRIPT_VLPJS", "migrer_joints", "JOURNAL_VISIBLE",
    "JOURNAL_ANCIEN", "bilan_en_haut", "couts_du_fichier", "total_sans_page", "regenerer", "verifier_page",
]


# --- page --------------------------------------------------------------------

# Le seuil vit dans le script (SEUIL_PAGE) : ici, il est défini et cité.
SEUIL_PAGE = 250
GABARIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "templates",   # scripts/noyau/ → scripts/
                       "artefact-chantier.html")
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


def joints_changes(copies, page=None):
    """Les joints de `copies` à republier : avec `page`, ceux dont l'empreinte diffère de celle notée
    à sa dernière publication (`publie`, écrit par `attente hook`) ; page jamais notée, ou sans
    `page` : tous (chantier JNT)."""
    if not page:
        return copies
    dossier, nom_page = os.path.split(os.path.abspath(page))
    notes = lire_publie(dossier)
    return {nom: c for nom, c in copies.items() if notes.get((nom_page, nom)) != empreinte(c)}


def ligne_files(copies, page=None):
    """`FILES {…}` : le JSON de `recopier_joints`, chemins en barres obliques — à passer
    tel quel au paramètre `files` d'`Artifact` (chantier BTN) ; `joints_changes` les filtre
    par `page` ; rien de changé : `FILES {}` (chantier JNT)."""
    return "FILES %s\n" % json.dumps({nom: chemin.replace("\\", "/") for nom, chemin in joints_changes(copies, page).items()},
                                     ensure_ascii=False)


def ligne_lire(copies, page=None):
    """`LIRE <nom>…` : les joints que la republication remplace — les noms de `FILES` —, à passer en
    `paths` au `read` d'`Artifact` avant de republier : un joint en ligne non lu la refuse (`APR`,
    10 refus sur 50, tous sur `couts.svg`) ; rien à remplacer : `LIRE aucun` (REF29)."""
    noms = list(joints_changes(copies, page))
    return "LIRE %s\n" % (" ".join(noms) if noms else "aucun")


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


def mesure():
    """`mesure-tokens.py`, importé une fois (le tiret interdit `import`)."""
    if etat._mesure is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mesure_tokens", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mesure-tokens.py"))
        assert spec and spec.loader
        etat._mesure = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(etat._mesure)
    return etat._mesure


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
PLAGE_DEPEND = re.compile(r"\b([A-Z]{1,3})([0-9]+)`?\s+à\s+`?\1([0-9]+)\b")
VISUEL = '<span class="badge visuel" title="Critère de fin visuel : il faudra regarder">visuel</span>'


def deplier_plages(ligne):
    """`ligne` où chaque plage « `X1` à `X4` » — même préfixe, bornes croissantes — devient `X1 X2 X3 X4`,
    que `DEPEND` lit ensuite nom à nom : lue telle quelle, elle ne donnait que X1 et X4 (cadrage d'ACA,
    2026-10-11). Des bornes à l'envers restent telles quelles."""
    def developper(m):
        """La plage de `m` en noms séparés par une espace, ou telle quelle si ses bornes sont à l'envers."""
        bas, haut = int(m.group(2)), int(m.group(3))
        return " ".join(m.group(1) + str(n) for n in range(bas, haut + 1)) if bas < haut else m.group(0)
    return PLAGE_DEPEND.sub(developper, ligne)


def apercu_fiches(lignes, racine=None):
    """{id: (dépendances, critère visuel, fichiers)} lus dans le bloc de chaque fiche : les
    identifiants de sa ligne `**Dépend de**` et de ses suites, une plage dépliée (`deplier_plages`), vrai
    si son `**Critère de fin**` porte `(visuel)` — la colonne de gauche et celle de droite de sa carte sur la page (gabarit en
    colonnes) —, et le nom seul de chaque fichier de sa ligne `**Fichiers**` : `vlp.css` pour
    `templates/vlp.css`, pour qu'un même fichier nommé de deux façons compte comme commun. `racine` (les entrées
    du projet, `entrees`) : sa liste d'invités (`invites`) à la place — `croisent` les compare (ENA5)."""
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
                deps += [d for d in DEPEND.findall(deplier_plages(l)) if d not in deps]
            visuel = visuel or bool(CRITERE_VISUEL.match(l))
        # Un fichier : un chemin, ou un nom à extension — pas `compte_todo`, `:3124` ni « rien ».
        fichiers = coeur.invites(lignes[i + 1:suivant], racine) if racine is not None else {
            n.rstrip("/").rsplit("/", 1)[-1] for n in coeur.noms_fichiers(lignes[i + 1:suivant])
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


def apercu_lancables(lignes, nom, racine=None):
    """`apercu_fiches` de `lignes`, le fichier de fiches `nom` ôté des fichiers de chacune — toutes le cochent, il
    n'est pas commun. Les fichiers : la liste d'invités (`invites`), `racine` les entrées du projet (`entrees`) —
    sans elle, un mot seul n'est jamais un dossier."""
    return {i: (d, v, {x for x in f if x.rstrip("/").rsplit("/", 1)[-1] != nom.lower()})
            for i, (d, v, f) in apercu_fiches(lignes, racine or {}).items()}


def lancables(lignes, nom, plafond, tournent=(), racine=None):
    """Les fiches que `/vlp:enchainer agents` lance ensemble, chacune dans son worktree (ENA3, ISO3) : les prêtes de
    `pretes`, dans l'ordre, jusqu'à `plafond` et avant la première `(visuel)`, qui ne part que seule. Deux fiches qui
    nomment un même fichier partent quand même : Git tranche à la fusion (Q7), `indices` le signale. `tournent`
    (ENA5) : les fiches déjà lancées — elles comptent dans `plafond`, rien ne part à côté d'une `(visuel)`, et une
    cochée en relecture ne libère pas encore ce qui dépend d'elle ; un id inconnu du fichier n'y compte pas
    (`cmd_lancables` le dit). `racine` : pour `apercu_lancables`."""
    fiches_ = fiches_du_fichier(lignes)
    apercu = apercu_lancables(lignes, nom, racine)
    attend, _ = pretes(fiches_, {i: "faite" if c and i not in tournent else "" for i, _, c, _ in fiches_}, apercu)
    lancees = [apercu[i] for i in tournent if i in apercu]
    if any(v for _, v, _ in lancees):
        return []
    rendu = []
    for i in [i for i, _, _, _ in fiches_ if i in attend and not attend[i] and i not in tournent]:
        visuel = apercu.get(i, ([], False, set()))[1]
        if len(rendu) + len(lancees) >= plafond or (visuel and (rendu or lancees)):
            break
        rendu.append(i)
        if visuel:
            break
    return rendu


def indices(apercu, ids):
    """Les `(a, b, fichier)` de deux fiches de `ids`, dans l'ordre, dont les lignes **Fichiers** se croisent
    (`croisent`, motifs compris) — `fichier`, le premier de `a`, trié, qui croise `b`. Elles partent ensemble quand
    même : le repère prévient, Git tranche à la fusion (ISO3, Q7)."""
    rendu = []
    for n, a in enumerate(ids):
        for b in ids[n + 1:]:
            uns, autres = (apercu.get(i, ([], False, set()))[2] for i in (a, b))
            f = next((x for x in sorted(uns) if croisent({x}, autres)), None)
            rendu += [(a, b, f)] if f else []
    return rendu


def cmd_lancables(a, sortie):
    """Imprimer `LANCABLES <id>…`, ou `LANCABLES aucune` : ce que `lancables` rend sur `a.fichier`, `a.max` au plus,
    puis une ligne `INDICE: <a> <b> <fichier>` par paire qui se croise, lancées comprises (`indices`). Un id de
    `--tourne` inconnu du fichier : une `GARDE:` avant, il est ignoré et le reste sort, sort 0 (ISO3). La racine :
    le projet qui porte le fichier (`trouver`)."""
    if not os.path.isfile(a.fichier) or a.max < 1:
        sortie.write("GARDE: lancables veut un fichier de fiches et --max ≥ 1 : %s, %d\n" % (a.fichier, a.max))
        return 1
    projet = trouver(os.path.dirname(os.path.abspath(a.fichier)))
    lignes, nom, racine = lignes_de(a.fichier), os.path.basename(a.fichier), coeur.entrees(projet) if projet else {}
    apercu = apercu_lancables(lignes, nom, racine)
    for i in [i for i in a.tourne if i not in apercu]:
        sortie.write("GARDE: --tourne %s : aucune fiche de ce nom dans %s, ignorée\n" % (i, a.fichier))
    ids = lancables(lignes, nom, a.max, a.tourne, racine)
    sortie.write("LANCABLES %s\n" % (" ".join(ids) or "aucune"))
    for x, y, f in indices(apercu, [i for i in a.tourne if i in apercu] + ids):
        sortie.write("INDICE: %s %s %s\n" % (x, y, f))
    return 0


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


COMMIT_FICHE = re.compile(r"^([A-Z]{1,3}[0-9]+) :")
COMMIT_FUSION = re.compile(r"^Fusion : ([A-Z]{1,3}[0-9]+)$")    # le sujet de `fusionner --worktree`
INFINI = float("inf")


def heures_commits(fichier, ids, pourquoi=None, clos=False, titres=None):
    """({id: heure}, [heures], [autres heures], [coupes]) en secondes UTC, lus par `git log` dans
    le dossier du fichier : l'heure d'auteur du commit `<id> :` de chaque fiche — s'il y en a deux,
    le plus ancien de ceux dont le sujet suit par le titre de la fiche (`titres`, {id: titre} ;
    le commit de 6 bis et de `boucle.py`), à défaut le plus ancien : un commit d'étape en cours de
    fiche ne la coupe plus avant sa fin, un correctif d'après ne l'étire pas (chantier PRP, `NUI20`) —,
    celles de tous les commits qui nomment le préfixe (`REP`, `REP2`…) — sauf un commit de fiche plus
    ancien que le premier retenu, une étape de celle-ci, qui ne borne pas son début (PRF) —,
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
        r = subprocess.run([etat.GIT, "log", "--format=%at %s"], cwd=os.path.dirname(os.path.abspath(fichier)),
                           capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        pourquoi.append("git ne se lance pas : %s" % e)
        return None
    if r.returncode:
        pourquoi.append("git log en échec : %s" % ((r.stderr or "").strip().splitlines() or ["code %d" % r.returncode])[0])
        return None
    return heures_du_log(r.stdout, ids, pourquoi, clos, titres)


def heures_du_log(texte, ids, pourquoi, clos=False, titres=None):
    """La décision de `heures_commits`, sur `texte`, la sortie de `git log --format="%at %s"` : mêmes rendus, même
    `pourquoi`. Ne lance rien (REF46)."""
    nomme = re.compile(r"(?<![A-Za-z0-9])(?:%s)[0-9]*(?![A-Za-z0-9])"
                       % "|".join(sorted({coeur.lettre_de(i) for i in ids})))
    coupe = re.compile(r"(?<![A-Za-z0-9])(?:%s) :" % "|".join(sorted({coeur.lettre_de(i) for i in ids})))
    commits, au_titre, prefixe, autres, coupes, etapes = {}, {}, [], [], [], set()
    for ligne in texte.splitlines():
        heure, _, sujet = ligne.partition(" ")
        if not heure.isdigit():
            continue
        # `Fusion : BLA4`, posé une seconde après `BLA4 :` en parallèle, fermait la clôture avant `clore` (dette GAI).
        fusion = COMMIT_FUSION.match(sujet)
        (prefixe if nomme.search(sujet) and not (fusion and fusion.group(1) in ids) else autres).append(int(heure))
        coupes.extend([int(heure)] if coupe.search(sujet) else [])
        c = COMMIT_FICHE.match(sujet)
        if c and c.group(1) in ids:
            etapes.add(int(heure))
            titre = (titres or {}).get(c.group(1))
            vus = au_titre if titre and sujet[c.end():].replace("`", "").strip().startswith(titre) else commits
            vus[c.group(1)] = min(int(heure), vus.get(c.group(1), int(heure)))
    commits.update(au_titre)
    if not commits:
        if not prefixe:
            pourquoi.append("aucun commit qui nomme %s" % coeur.lettre_de(ids[0]))
            return None
        if clos:
            pourquoi.append("chantier clos sans commit « %s : » ni d'une autre fiche" % ids[0])
            return None
        return {}, sorted(prefixe), sorted(autres), sorted(coupes)
    # Un commit `<id> :` plus ancien que le premier commit de fiche retenu est une étape de cette fiche
    # (`AVL1 : case cochée`, deux secondes avant `AVL1 : <titre>`) : il ne borne pas son début (PRF).
    premier = min(commits.values())
    prefixe = [t for t in prefixe if not (t < premier and t in etapes)]
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


def sous_agents_nommes(fichiers, idents):
    """{chemin: fiche} des sous-agents (sorte 1) dont le prompt nomme une fiche d'`idents` (`FICHE_NOMMEE`) :
    ils comptent en entier à elle, même partis pendant la plage d'une autre — en parallèle (chantier CPF)."""
    nommes = {c: coeur.fiche_jouee(c, coeur.FICHE_NOMMEE) for c, sorte in fichiers if sorte == 1}
    return {c: f for c, f in nommes.items() if f in idents}


def plages_du_transcript(chemin, bornes, ident, nommes):
    """Les plages où mesurer `chemin` pour la part `ident` (None : hors fiches) : un sous-agent de `nommes`
    en entier ([None]) à sa fiche, nulle part ailleurs ; tout autre transcript, sur `bornes`."""
    fiche = nommes.get(chemin)
    return bornes if fiche is None else [None] if fiche == ident else []


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
    chantier est clos : sa fiche sans commit s'arrête au commit suivant (`plages`, chantier ECA). Un sous-agent
    dont le prompt nomme une fiche qui a une plage lui compte en entier (`sous_agents_nommes`, chantier CPF)."""
    from decimal import ROUND_HALF_UP, Decimal
    m = mesure()
    fichiers = transcripts_du_fichier(fiches_, entete, gardes)
    if not fichiers:
        return None
    par_fiche, trous = plages_du_cout(fiches_, heures, gardes, fin)
    if not par_fiche:
        return None
    nommes = sous_agents_nommes(fichiers, {ident for ident, _ in par_fiche})

    def part(bornes, ident=None):
        """(session, sous-agents, essais) mesurés sur `bornes`, pour la fiche `ident` (None : hors fiches)."""
        rendu =[[0, 0, Decimal(0), 0], [0, 0, Decimal(0), 0], [0, 0, Decimal(0), 0]]
        for chemin, sorte in fichiers:
            p, tours = rendu[min(sorte, 2)], 0
            for plage in plages_du_transcript(chemin, bornes, ident, nommes):
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

    parts, hors = [(ident,) + part([p], ident) for ident, p in par_fiche], part(trous)
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
    hors = coeur.COMMENTAIRE.sub("", html)
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


def couts_du_fichier(fichier, anciens, ancien_total, gardes):
    """`couts` d'un fichier de fiches aux heures de ses commits, comme la page les écrit ; `anciens` et `ancien_total`
    viennent de l'ancienne page, `{}` et None sans elle — `clore` d'un projet sans page (dette GAI)."""
    lignes = lignes_de(fichier)
    fiches_ = fiches_du_fichier(lignes)
    clos = any(l.startswith("**CLOS**") for l in lignes)
    heures = heures_commits(fichier, [f[0] for f in fiches_], clos=clos) if any(f[3] for f in fiches_) else None
    # Un clos s'arrête à son appel clore, comme cout : un chantier, un seul chiffre (dette PLI).
    fin = heure_clore(fichier, lignes) if clos and heures else None
    return couts(fiches_, anciens, ancien_total, gardes, heures, sessions_entete(lignes), fin)


def total_sans_page(carte_, chemin_page, chemin_fiches, gardes):
    """`clore` sans page du chantier : sa garde dans `gardes`, sans « GARDE: », et le total (total, tours, usd) que la
    page écrirait — le bac de GAI2 closait en « non mesuré » (dette GAI) ; None sans fiche."""
    gardes.extend(coeur.garde_page(carte_, "artefact du chantier", "page du chantier introuvable : %s" % chemin_page))
    if not fiches_du_fichier(lignes_de(chemin_fiches)):
        return None
    couts_f = []    # celles de couts portent déjà « GARDE: »
    total = couts_du_fichier(chemin_fiches, {}, None, couts_f)[1]
    gardes.extend(re.sub(r"^GARDE: ", "", g) for g in couts_f)
    return total


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
        cout, total, hors = couts_du_fichier(fichier, anciens, ancien_total and ancien_total.group(1), gardes)
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
                  lambda m: m.group(1) + coeur.plage([f[0] for f in fiches_]), html, count=1)
    # Le lien vers la feuille de route, en fin d'en-tête : `**artefact feuille de route**` du
    # CHANTIER.md du projet, retrouvé en remontant depuis le fichier de fiches (chantier FEU).
    # Un seul lien : celui d'avant se retire toujours, avant qu'un nouveau (ou aucun) ne s'ajoute.
    racine = trouver(os.path.dirname(fichier))
    carte_racine = lignes_de(os.path.join(racine, "CHANTIER.md")) if racine else []
    url_route = coeur.champ(carte_racine, "artefact feuille de route", "aucun")
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
