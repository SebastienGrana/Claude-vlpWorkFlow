"""Le texte d'une page publiée existe-t-il ailleurs que dans la page ?
Pour chaque note de fiche, entrée de journal (pages de chantier) et cellule
« Ce qu'il apporte » (TODO de la feuille de route), cherche le texte dans tout
ce qu'un modèle peut relire sans la page : les .md du dossier de contexte,
CHANTIER.md, et les messages de commit du projet.

Comparaison tolérante : sans accents, sans casse, sans ponctuation, sans
balises ni `**`. Trois niveaux :
  - « entier » : le bloc entier est retrouvé ;
  - « début » : les 50 premiers caractères normalisés sont retrouvés ;
  - « morceau » : au moins un des trois morceaux de 40 caractères (début,
    tiers, deux tiers) est retrouvé.
Un bloc absent aux trois niveaux n'existe, en pratique, que dans la page.
La TODO de la feuille se compte par rang : un rang est « entier » si chacune
de ses cellules est retrouvée entière.

    python page_vs_source.py <racine du projet équipé> <nom du dossier de contexte>
"""
import glob, html, os, re, subprocess, sys, unicodedata

sys.stdout.reconfigure(encoding="utf-8")
racine, contexte = sys.argv[1], sys.argv[2]
ctx = os.path.join(racine, contexte)


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^0-9a-z]+", " ", s).strip()


def de_html(s):
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", s)))


def de_md(s):
    return norm(re.sub(r"[`*]", "", s))


morceaux_corpus = []
for p in glob.glob(os.path.join(ctx, "**", "*.md"), recursive=True):
    morceaux_corpus.append(de_md(open(p, encoding="utf-8", errors="replace").read()))
chantier = os.path.join(racine, "CHANTIER.md")
if os.path.isfile(chantier):
    morceaux_corpus.append(de_md(open(chantier, encoding="utf-8", errors="replace").read()))
try:
    log = subprocess.run(["git", "-C", racine, "log", "--all", "--format=%B"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
except OSError:
    log = ""
morceaux_corpus.append(de_md(log))
corpus = "\n".join(morceaux_corpus)


def trouve(bloc):
    """(entier, début, un morceau) retrouvés, pour un bloc normalisé."""
    entier = bloc in corpus
    debut = entier or bloc[:50] in corpus
    n = len(bloc)
    fenetres = [bloc[i:i + 40] for i in (0, n // 3, 2 * n // 3) if len(bloc[i:i + 40]) >= 30]
    return entier, debut, debut or any(f in corpus for f in fenetres)


tot = {"blocs": 0, "entier": 0, "debut": 0, "morceau": 0}


def compter(nom, blocs):
    blocs = [b for b in blocs if len(b) >= 30]
    e = d = m = 0
    absents = []
    for b in blocs:
        a0, a, b2 = trouve(b)
        e += a0
        d += a
        m += b2
        if not b2:
            absents.append(b[:70])
    tot["blocs"] += len(blocs); tot["entier"] += e; tot["debut"] += d; tot["morceau"] += m
    print("%-40s blocs %3d · entier %3d · début %3d · un morceau %3d" % (nom, len(blocs), e, d, m))
    for x in absents[:2]:
        print("      absent : %s…" % x)


for page in sorted(glob.glob(os.path.join(ctx, "artefacts", "[0-9]*.html"))):
    h = open(page, encoding="utf-8").read()
    base = os.path.basename(page)[:-5]
    notes = [de_html(x) for x in re.findall(r'<span class="note">(.*?)</span>\s*(?:<span class="cout|</li>)', h, re.S)]
    journal = [de_html(re.sub(r"<time[^>]*>.*?</time>", "", x, flags=re.S))
               for x in re.findall(r"<li>(\s*<time.*?)</li>", h, re.S)]
    compter(base + " · notes", notes)
    compter(base + " · journal", journal)

feuille = os.path.join(ctx, "artefacts", "feuille-de-route.html")
if os.path.isfile(feuille):
    f = open(feuille, encoding="utf-8").read()
    todo = re.search(r"ZONE:todo.*?<tbody>(.*?)</tbody>", f, re.S)
    rangs = entiers = 0
    for rang in re.findall(r"<tr>.*?</tr>", todo.group(1) if todo else "", re.S):
        cel = [de_html(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", rang, re.S)]
        if len(cel) >= 3:
            rangs += 1
            entiers += all(c in corpus for c in cel if c)
    print("TOTAL pages de chantier : blocs %(blocs)d · entier %(entier)d · début %(debut)d · un morceau %(morceau)d" % tot)
    print("feuille · TODO : rangs %d · toutes cellules entières ailleurs %d" % (rangs, entiers))
else:
    print("TOTAL pages de chantier : blocs %(blocs)d · entier %(entier)d · début %(debut)d · un morceau %(morceau)d" % tot)
