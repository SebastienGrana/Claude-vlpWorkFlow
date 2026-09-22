"""Les chiffres d'une page publiée existent-ils ailleurs que dans la page ?
Pour chaque note et entrée de journal, relève les nombres d'au moins 3
chiffres (« 364 001 », « 1 566 », « 0,0653 ») et les cherche dans tous les .md
du dossier de contexte, et dans CHANTIER.md. Une note est « couverte » si au
moins la moitié de ses nombres s'y retrouvent.

    python chiffres_vs_source.py <racine du projet équipé> <nom du dossier de contexte>
"""
import glob, html, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

racine, contexte = sys.argv[1], sys.argv[2]
ctx = os.path.join(racine, contexte)
NB = re.compile(r"\d{1,3}(?:[  ]\d{3})+(?:,\d+)?|\d+,\d{2,}|\d{3,}")


def nombres(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return {re.sub(r"[  ]", "", n) for n in NB.findall(s)}


sources = [p for p in glob.glob(os.path.join(ctx, "**", "*.md"), recursive=True)]
sources.append(os.path.join(racine, "CHANTIER.md"))
connus = set()
for p in sources:
    if os.path.isfile(p):
        connus |= nombres(open(p, encoding="utf-8", errors="replace").read())

tot = [0, 0, 0]
for page in sorted(glob.glob(os.path.join(ctx, "artefacts", "[0-9]*.html"))):
    h = open(page, encoding="utf-8").read()
    blocs = re.findall(r'<span class="note">(.*?)</span>\s*(?:<span class="cout|</li>)', h, re.S)
    blocs += re.findall(r"<li>\s*<time.*?</time>(.*?)</li>", h, re.S)
    avec, couverts = 0, 0
    for b in blocs:
        n = nombres(b)
        if not n:
            continue
        avec += 1
        if len(n & connus) * 2 >= len(n):
            couverts += 1
    tot[0] += len(blocs); tot[1] += avec; tot[2] += couverts
    print("%-34s blocs %2d · avec chiffres %2d · couverts ailleurs %2d" % (os.path.basename(page)[:-5], len(blocs), avec, couverts))
print("TOTAL blocs %d · avec chiffres %d · couverts ailleurs %d" % tuple(tot))
