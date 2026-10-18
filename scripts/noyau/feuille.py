"""La feuille de route : sa table, ses lignes, sa republication (REF46 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import os
import re

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (PREFIXE, TITRE, lignes_de, lignes_du_projet, lire)
from noyau.carte import (equipe)
from noyau.page import (esc, fleche, ligne_files, migrer_joints, migrer_style, recopier_joints)
from noyau.notes import (CODE, cellules_de)

__all__ = [
    "AUCUN_ENCOURS", "BADGE_COURS", "retirer_chevrons_url", "champ", "lettre_de", "LETTRES", "entrees_lettres",
    "lettre_entree", "titre_entree", "doublon_lettres", "fin_lettres", "lettres_prises", "bornes", "plage", "MONO",
    "MORCEAU", "JETON", "GRAS", "LIEN", "gras_et_liens", "cellule_md", "SEPARATEUR", "todo_du_fichier",
    "rangs_todo", "zone", "FORMES_TODO", "zone_todo", "rang_en_cours", "en_cartes", "LECTURE", "replier_lecture",
    "SOMMAIRE", "sommaire", "depend_todo", "PHASE_COUT", "phase_todo", "rang_phase", "taille_todo",
    "IMPORTANCE_PHASE", "FACILITE_FICHES", "aide_score", "carte_todo", "corps_todo", "PAGES_LIENS", "PAGES_NAV",
    "liens_pages", "feuille", "RESUME_TODO", "GROS_FICHES", "NOMBRE_COUT", "PLAGE_COUT", "borne_haute_cout",
    "bornes_cout", "dependances", "est_bloque", "decompte_todo", "resume_todo", "compte_todo", "page_feuille",
    "ARCHIVE_CLOS", "page_clos", "couts_du_projet", "rafraichir_couts", "GABARIT_ARCHIVE", "ICI_ARCHIVE",
    "BLOC_ARCHIVE", "poser_bloc_archive", "poser_champ", "cmd_archive",
]


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
    return [cellules for _, cellules in rangs_todo(lignes)]


def rangs_todo(lignes):
    """[(indice dans `lignes`, cellules)] des rangs de `todo_du_fichier` — l'indice pour la carte, qui
    numérote chaque ligne qu'elle condense (REF2)."""
    rangs, dedans = [], False
    for i, l in enumerate(lignes):
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
        rangs.append((i, cellules))
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


# La phase et le score en tête de la case « Coût » (`methode-chantier.md`, « Le score d'une ligne de
# TODO ») : `**V1 · score 25 (5 × 5)** · `, un score `?` tant que la facilité n'est pas chiffrée. La
# feuille les montre à gauche de la carte, et fait une sous-liste par phase écrite dans la TODO —
# celles du projet, `V3` compris s'il en a (AVL12, demandé le 2026-10-11).
PHASE_COUT = re.compile(r"\*\*(V\d+|après) · score (\d+|\?) \(([^)]*)\)\*\*(?: · )?")


def phase_todo(cout):
    """(phase, score, détail, reste) d'une case « Coût » : `**V1 · score 25 (5 × 5)** · 1 fiche` →
    `("V1", "25", "5 × 5", "1 fiche")` ; sans phase en tête, `(None, None, None, cout)`."""
    m = PHASE_COUT.match(cout.strip())
    if not m:
        return None, None, None, cout
    return m.group(1), m.group(2), m.group(3), cout.strip()[m.end():]


def rang_phase(phase):
    """La clé de tri des sous-listes : `V1`, `V2`, `V3`… dans l'ordre, puis `après`, puis sans phase."""
    if phase is None:
        return (2, 0)
    return (1, 0) if phase == "après" else (0, int(phase[1:]))


def taille_todo(cout):
    """`petit`, `moyen`, `gros` ou `pas-estime`, sur la borne haute du coût — les parts du décompte
    (`decompte_todo`), et le filtre « Taille » de la feuille (AVL12)."""
    borne = borne_haute_cout(cout)
    if borne is None:
        return "pas-estime"
    return "petit" if borne <= 1 else "moyen" if borne <= GROS_FICHES else "gros"


# L'échelle du score, recopiée de `methode-chantier.md` (« Le score d'une ligne de TODO ») pour l'aide
# de la feuille : `test-vlp.py` la compare à la règle (AVL12, demandé le 2026-10-12).
IMPORTANCE_PHASE = (("V1", 5), ("V2", 3), ("V3", 2), ("après", 1))
FACILITE_FICHES = (("1", 5), ("2", 4), ("3 à 4", 3), ("5 à 7", 2), ("8 et plus", 1))


def aide_score():
    """L'aide repliée en tête des chantiers possibles, quand la TODO écrit des phases : ce que vaut
    le score et comment il se calcule, pour qui découvre le kit (AVL12)."""
    importance = ", ".join(("%d %s" if p == "après" else "%d en %s") % (n, p) for p, n in IMPORTANCE_PHASE)
    facilite = " · ".join("%s → %d" % (f, n) for f, n in FACILITE_FICHES)
    return ('          <li class="aide-score"><details class="aide"><summary>Comment se lit le score</summary>\n'
            "            <p><strong>Score = importance × facilité</strong>, de 1 à 25 : plus il est haut, plus le "
            "chantier rapporte pour peu d'effort.</p>\n            <ul>\n"
            "              <li><strong>La phase</strong> : V1, ce que la première version du projet demande, ou ce "
            "qui le garde juste ; V2, plus vite, moins cher ou plus lisible, sans que la V1 l'attende ; V3, si le "
            "projet l'écrit, la version suivante ; après, le confort.</li>\n"
            "              <li><strong>L'importance</strong> suit la phase : %s — sauf une note de 1 à 5 donnée à "
            "la ligne.</li>\n"
            "              <li><strong>La facilité</strong> suit le nombre de fiches estimé (une fiche : une tâche, "
            "une séance), le haut de la fourchette : %s ; « sans fiche » → 5.</li>\n"
            "              <li><strong>Un score « ? »</strong> : la facilité n'est pas encore chiffrée.</li>\n"
            "              <li><strong>L'ordre</strong> : les dépendances d'abord, puis le score.</li>\n"
            '            </ul>\n            <p>La règle entière : <span class="mono">methode-chantier.md</span>, '
            "« Le score d'une ligne de TODO ».</p></details></li>\n") % (importance, facilite)


def carte_todo(rang, todo, bloque):
    """La carte d'un chantier possible, en colonnes comme les fiches : rang, pastille de phase et de
    score, badge et dépendances à gauche ; le titre qui replie « Ce qu'il apporte » (chantier FEU) ; le
    coût sous le titre, sans sa phase, un segment ` · ` par ligne (AVL12). Ses `data-` (phase, score,
    taille, prêt) servent aux filtres de `vlp.js`."""
    n, ch, ap, co, de = rang
    phase, score, detail, reste = phase_todo(co)
    attributs = ' data-taille="%s" data-pret="%s"' % (taille_todo(co), "non" if bloque else "oui")
    pastille = ""
    if phase:
        attributs = ' data-phase="%s" data-score="%s"' % (phase, "" if score == "?" else score) + attributs
        pastille = ('<span class="phase mono" data-phase="%s" title="score %s = %s (importance × facilité)">%s · %s</span>'
                    % (phase, score, esc(detail), phase, score))
    return ('          <li class="carte-todo"%s><span class="gauche"><span class="rang mono">%s</span>%s%s%s</span>'
            '<details><summary><span class="titre">%s</span></summary><div class="detail">%s</div></details>'
            '<span class="meta">%s</span></li>\n'
            % (attributs, esc(n), pastille, BADGE_COURS if n == todo else "", depend_todo(de), cellule_md(ch),
               cellule_md(ap), "".join('<span class="seg">%s</span>' % s
                                       for s in cellule_md(reste).split(" · ") if s.strip())))


def corps_todo(rangs, todo, lettres_todo):
    """Les cartes de `ZONE:todo`. Sans aucune phase écrite, dans l'ordre de la TODO ; sinon une
    sous-liste par phase (`rang_phase`), titrée et comptée, l'ordre de la TODO gardé dans chacune ;
    une ligne sans phase va dans « Sans phase », en dernier — jamais perdue (AVL12)."""
    if not rangs:
        return '          <li class="rien">Rien en attente.</li>\n'
    presents = {r[0] for r in rangs}
    cartes = [(phase_todo(r[3])[0], carte_todo(r, todo, est_bloque(r[4], lettres_todo, presents))) for r in rangs]
    if not any(p for p, _ in cartes):
        return "".join(c for _, c in cartes)
    groupes = {}
    for phase, carte in cartes:
        groupes.setdefault(phase, []).append(carte)
    corps = aide_score()
    for phase in sorted(groupes, key=rang_phase):
        nom = "Sans phase" if phase is None else "Après" if phase == "après" else phase
        nombre = len(groupes[phase])
        corps += ('          <li class="phase-titre" data-phase="%s"><h3>%s · %d&nbsp;%s</h3></li>\n'
                  % (phase or "aucune", nom, nombre, "chantier" if nombre == 1 else "chantiers"))
        corps += "".join(groupes[phase])
    return corps


# Les autres pages du projet, sous le sommaire de la feuille, lues dans `CHANTIER.md` : la page
# du chantier ouvert, l'archive des clos, la page d'enchaînement entre projets (AVL10, demandé le
# 2026-10-12 : « retrouver toutes les pages du kit depuis la feuille de route »).
PAGES_LIENS = (("artefact du chantier", "la page du chantier"), ("artefact archive", "l'archive des clos"),
               ("artefact enchaînement", "la page d'enchaînement"))
PAGES_NAV = re.compile(r'  <nav class="pages"[^\n]*</nav>\n')


def liens_pages(html, carte_):
    """La ligne « Les autres pages » refaite sous le sommaire, à chaque appel ; ôtée quand aucun
    champ ne porte d'URL, jamais posée sans sommaire."""
    html = PAGES_NAV.sub("", html)
    liens = ['<a href="%s">%s</a>' % (esc(url), nom) for url, nom in
             ((champ(carte_, c, "aucun").strip("<> "), nom) for c, nom in PAGES_LIENS) if url.startswith("http")]
    i = html.find('<nav class="sommaire"')
    if not liens or i < 0:
        return html
    j = html.find("\n", i) + 1
    return (html[:j] + '  <nav class="pages" aria-label="Les autres pages">Les autres pages : %s</nav>\n'
            % " · ".join(liens) + html[j:])


def feuille(projet, html, todo, date):
    """(page régénérée, bilan) : encours, todo et lettres depuis `CHANTIER.md` et le fichier d'état."""
    html = migrer_joints(migrer_style(html))
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    etat = champ(carte_, "fichier d'état")
    if not etat:
        raise ValueError("fichier d'état introuvable : aucun")
    lignes_etat = lignes_du_projet(projet, etat, "fichier d'état")
    courant = coeur.courant_de(projet)
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
    corps = corps_todo(rangs, todo, lettres_todo)
    cartes = replier_lecture(en_cartes(html))
    d, f, _ = zone_todo(cartes)
    neuf = compte_todo(cartes[:d] + corps + cartes[f:], rangs, lettres_todo)
    d, f = zone(neuf, "encours", "\n", "  </section>")
    neuf = neuf[:d] + encours + neuf[f:]
    neuf = re.sub(r'(Lettres de fiche prises : <span class="mono">).*?(</span>)',
                  lambda m: m.group(1) + ", ".join(lettres) + m.group(2), neuf, count=1)
    neuf = coeur.balise_couts(liens_pages(sommaire(neuf), carte_), couts_du_projet(projet, neuf))
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
    """La borne haute d'un « Coût » de TODO, en fiches, ou `None` : le haut de `bornes_cout`."""
    bornes = bornes_cout(cout)
    return None if bornes is None else bornes[1]


def bornes_cout(cout):
    """(bas, haut) d'un « Coût » de TODO, en fiches — `~4 à 6` → (4, 6), `2-3` → (2, 3), `~0,5` → (0,5, 0,5),
    `~½` → 0,5 (`½` se lit 0,5 ; `1½`, 1,5) —, ou `None` sans plage suivie de « fiche(s) »
    (`à cadrer`, `🟡 pas estimé`, `—`, `sans fiche`) (FEU8, NUI10). La dernière estimation fait foi
    (NUI38) : le dernier segment ` · ` qui porte une plage suivie de « fiche(s) » — un prix « (3,68 $ la
    fiche) » n'en est pas une ; dans ce segment, la plage qui suit la dernière `→`, sinon la dernière plage
    suivie de « fiche(s) ». Le texte entre parenthèses ne se lit pas (« (`AMD` : 7 fiches) » compare, il
    n'estime pas) ; une plage précédée de `+` (« ≈ +½ fiche ») s'ajoute à l'estimation d'avant au lieu de la
    remplacer (CLU). Jamais une durée."""
    borne = None
    for brut in cout.split(" · "):
        segment = brut
        while True:     # les parenthèses, imbriquées comprises, de l'intérieur vers l'extérieur
            neuf = re.sub(r"\([^()]*\)", "", segment)
            if neuf == segment:
                break
            segment = neuf
        if not re.search(r"\bfiches?\b", segment):
            continue
        apres = re.match(r"\s*[~≈]?\s*(\+?)\s*(%s)" % PLAGE_COUT, segment.rsplit("→", 1)[1]) if "→" in segment else None
        plages = [apres.groups()] if apres else re.findall(r"(\+?)\s*(%s)\s*fiches?\b" % PLAGE_COUT, segment)
        if not plages:
            borne = None if re.search(r"\bsans fiche\b", segment) else borne    # « re-cadré : sans fiche » fait foi
            continue
        ajout, plage = plages[-1]
        valeurs = [float(n.rstrip("½").replace(",", ".") or 0) + (0.5 if n.endswith("½") else 0)
                   for n in re.findall(NOMBRE_COUT, plage)]
        neuves = (min(valeurs), max(valeurs))
        borne = (borne[0] + neuves[0], borne[1] + neuves[1]) if ajout and borne is not None else neuves
    return borne


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
    `rangs_presents` — encore dans la TODO (FEU8). Un nom entre backticks qui n'est pas un code de
    lettres (`C1`, `V1-3`) est une fiche d'un autre projet, que le kit ne sait pas lire : il bloque
    (dette d'`AVL`, 2026-10-12 : `RMS` paraissait prête en attendant `C1` de MapDecorator)."""
    codes, rangs = dependances(depend)
    ailleurs = [n for n in re.findall(r"`([^`]+)`", depend) if not re.fullmatch(r"[A-Za-z]+", n)]
    return bool(ailleurs) or any(lettre_de(c) not in lettres_todo for c in codes) or bool(rangs & set(rangs_presents))


def decompte_todo(rangs, lettres_todo):
    """(petits, moyens, gros, pas_estimés, bloqués, total en fiches) des rangs d'une TODO —
    petit ≤ 1, moyen ≤ `GROS_FICHES`, gros au-delà de la borne haute de leur « Coût » (FEU8)."""
    presents = {r[0] for r in rangs}
    petits = moyens = gros = pas_estimes = bloques = 0
    total = 0.0
    for _, _, _, cout, depend in rangs:
        taille = taille_todo(cout)
        total += borne_haute_cout(cout) or 0.0
        petits += taille == "petit"
        moyens += taille == "moyen"
        gros += taille == "gros"
        pas_estimes += taille == "pas-estime"
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
        base += " · ≈%s %s" % (coeur.decimal_fr(total), "fiche estimée" if total == 1 else "fiches estimées")
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
    return coeur.couts_clos(lire(archive) if archive != page_feuille(projet) else html)


def rafraichir_couts(projet, page, html):
    """Après l'écriture des lignes closes `html` dans `page` : `couts.svg` refait à côté de la feuille ;
    `page` est l'archive, le bloc `ZONE:archive` et la balise de la feuille aussi (chantier ARC)."""
    feuille_ = page_feuille(projet)
    if page == feuille_:
        return coeur.ecrire_couts(page, html)
    couts = coeur.couts_clos(html)
    avant = lire(feuille_)
    neuf = coeur.balise_couts(poser_bloc_archive(avant, html, champ(lignes_de(os.path.join(projet, "CHANTIER.md")),
                                                                "artefact archive")), couts)
    if neuf != avant:
        with open(feuille_, "w", encoding="utf-8", newline="") as fh:
            fh.write(neuf)
    return coeur.ecrire_couts(feuille_, neuf, couts)


GABARIT_ARCHIVE = "templates/artefact-archive-clos.html"
ICI_ARCHIVE = "    <!-- ARCHIVE:table -->\n"
BLOC_ARCHIVE = re.compile(r"    <!-- ZONE:archive[^\n]*\n.*?    <!-- /ZONE:archive -->\n", re.S)


def poser_bloc_archive(feuille_html, archive_html, url):
    """La feuille avec son bloc `ZONE:archive` refait sur les lignes closes de l'archive : le résumé
    replié (nombre, tokens, $) et le lien — `details.clos` y reste, où `balise_couts` pose le
    graphique. Sans bloc ni `ZONE:clos`, rien ne change (chantier ARC)."""
    d, f = zone(archive_html, "clos", "<tbody>\n", "        </tbody>")
    corps = archive_html[d:f]
    usd, n_usd = coeur.prix_clos(corps)
    lien = ('<a href="%s">dans l\'archive</a>' % esc(url) if url and not url.lower().startswith("aucun")
            else "dans l'archive, pas encore publiée")
    bloc = ('    <!-- ZONE:archive — les chantiers clos vivent dans l\'archive (chantier ARC) ; refait par clore -->\n'
            '    <details class="clos">\n      <summary><span class="resume-clos">%s</span></summary>\n'
            '      <p>Le détail de chacun, le plus récent en haut : %s.</p>\n    </details>\n'
            '    <!-- /ZONE:archive -->\n' % (coeur.resume_clos(len(coeur.lignes_clos(corps)), coeur.total_clos(corps), usd, n_usd), lien))

    def refait(m):
        """Le bloc neuf, avec le graphique des coûts déjà posé dans l'ancien."""
        # le graphique déjà posé reste : `clore` refait le bloc après `feuille`, qui l'a posé
        garde = coeur.BALISE_COUTS.search(m.group(0))
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
        table = coeur.BALISE_COUTS.sub("", html[i:j]).replace('<details class="clos">', '<details class="clos" open>', 1)
        deplacees = len(coeur.lignes_clos(table))
        alias = champ(carte_, "alias", os.path.basename(os.path.abspath(projet)))
        gabarit = lire(os.path.join(etat.KIT, GABARIT_ARCHIVE))
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
    neuf = coeur.balise_couts(poser_bloc_archive(html, archive_html, url), coeur.couts_clos(archive_html))
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
    joints.update(coeur.ecrire_couts(page, neuf, coeur.couts_clos(archive_html)))
    sortie.write(ligne_files(joints, page))
    sortie.write("ARCHIVE %d déplacées · %d dans l'archive · feuille %d → %d octets · %s — %s\n" % (
        deplacees, len(coeur.lignes_clos(archive_html)), len(avant.encode("utf-8")), len(neuf.encode("utf-8")),
        "url %s" % url if url else "sans url", archive))
    return 0
