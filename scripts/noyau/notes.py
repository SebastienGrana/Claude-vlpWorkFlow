"""Les notes d'une page : l'abri `.md`, le fichier d'état, les renvois (REF46 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import html.parser
import os
import re
import noyau.page   # `noyau.page.<nom>` : un test remplace ce nom là (REF46)

from noyau.facade import coeur
from noyau.commun import (chemin_archive, lignes_de, lire)
from noyau.fiches import (SEUIL_CHANTIER, SEUIL_CLAUDE, SEUIL_INDEX)
from noyau.carte import (equipe)
from noyau.page import (
    JOURNAL_ANCIEN,
    SEUIL_PAGE,
    bilan_en_haut,
    comptage,
    creer,
    ligne_cout,
    ligne_files,
    lis_page,
    recopier_joints,
    verifier_page,
)

__all__ = [
    "ABRI_SECTIONS", "chemin_abri", "une_ligne", "lire_abri", "texte_abri", "ecrire_abri", "brut", "abri_de_page",
    "cmd_abri", "page_du_fichier", "cmd_page", "NUMERO", "nom_etat", "ajouter_etat", "cmd_etat", "LIGNE_CHEMIN",
    "CODE", "cellules_de", "noms_de_table", "noms_des_sources", "chemins_de_carte", "cmd_renvois",
]


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
    """`vlp.py page` : régénérer la page d'un chantier depuis son fichier de fiches (`noyau.page.regenerer`), la
    créer (`--creer`) ou la vérifier ; une option en conflit ou une page introuvable : `GARDE:`, rien écrit."""
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
        html, fiches_, etat, total, hors = noyau.page.regenerer(html, a.fichier, parts, date, gardes, forme=a.forme)
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


def ajouter_etat(chemin, texte_de, sortie):
    """Le texte du fichier `texte_de` ajouté à la fin du fichier d'état `chemin`, une ligne vide avant : celui qu'une
    fiche jouée en worktree rend entre `ÉTAT:` et `/ÉTAT` au lieu de l'écrire (`enchainement.md`, ISO5). Un des deux
    fichiers absent, ou un texte vide : `GARDE:`, rien d'écrit, sort 1. Sinon `ÉTAT ajouté <n> ligne(s) à <chemin>`."""
    for nom, quoi in ((chemin, "fichier d'état"), (texte_de, "texte")):
        if not os.path.isfile(nom):
            sortie.write("GARDE: %s absent : %s — rien d'écrit\n" % (quoi, nom))
            return 1
    texte = lire(texte_de).strip("\n")
    if not texte.strip():
        sortie.write("GARDE: texte vide : %s — rien d'écrit\n" % texte_de)
        return 1
    avant = lire(chemin).rstrip("\n")
    coeur.ecrire_comme(chemin, (avant + "\n\n" if avant.strip() else "") + texte + "\n")
    sortie.write("ÉTAT ajouté %d ligne(s) à %s\n" % (texte.count("\n") + 1, chemin))
    return 0


def cmd_etat(a, sortie):
    """`etat <contexte>` : le nom du fichier d'état (`nom_etat`) ; `etat <fichier d'état> --texte <fichier>` : le
    texte d'une fiche ajouté à sa fin (`ajouter_etat`, ISO5)."""
    if a.texte is not None:
        return ajouter_etat(a.contexte, a.texte, sortie)
    sortie.write("ETAT=%s\n" % nom_etat(a.contexte))
    return 0


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
        if not dedans or not l.startswith("|") or coeur.SEPARATEUR.match(l):
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
