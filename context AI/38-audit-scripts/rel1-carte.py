"""REL1 (jetable) : ce que chaque relecteur `vlp:relecture` tire de la carte injectée.
Comptes seulement, jamais un extrait. Python 3, sans dépendance.

    py "context AI/38-audit-scripts/rel1-carte.py" [--detail] [--sans-fichier]

`--detail` ajoute, après le total, une ligne par libellé cité : son compte.
`--sans-fichier` ignore `FICHIER=` et force la reconstitution du chemin (voir plus bas).

Le fichier de fiches relu : la ligne `FICHIER=` du premier résultat d'outil, si elle y est
(avant FFE1). Sinon, le dossier `APRÈS=` de ce même résultat joint au chemin de la ligne
« fichier de fiches courant » de la carte (premier message), étendue `(X1..X3)` retirée.

Par transcription, dans les messages de l'assistant (texte et entrées d'outil) :
  autres   identifiants de fiche de la carte (`n:## ID [`) cités, hors la fiche relue
  prochaine  `PROCHAINE` cité
  libelles  libellés en gras de `CHANTIER.md` cités comme libellés (`**x**`, « x », "x")
  entier / plage / grep  `Read` du fichier de fiches sans puis avec offset/limit, `Grep` dessus
"""
import glob, importlib.util, io, json, os, re, sys

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
kit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
spec = importlib.util.spec_from_file_location("vlp", os.path.join(kit, "scripts", "vlp.py"))
assert spec is not None and spec.loader is not None
vlp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vlp)

m = vlp.mesure()
motif = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", "*", *m.SOUS_AGENTS)
chemins = [c for c in sorted(glob.glob(motif)) if vlp.type_agent(c) == "vlp:relecture"]


def norme(p):
    return os.path.normcase(os.path.normpath(p.strip().strip('"'))) if p else ""


def blocs(d):
    c = (d.get("message") or {}).get("content")
    return [{"type": "text", "text": c}] if isinstance(c, str) else (c or [])


def texte_resultat(b):
    x = b.get("content")
    if isinstance(x, list):
        return "\n".join(y.get("text", "") for y in x if isinstance(y, dict))
    return x or ""


SANS_FICHIER = "--sans-fichier" in sys.argv
COLS = ("autres", "prochaine", "libelles", "entier", "plage", "grep")
total = dict.fromkeys(COLS, 0)
avec = dict.fromkeys(COLS, 0)
par_libelle = {}
print("%-18s %-7s %s" % ("id", "fiche", " ".join("%9s" % c for c in COLS)))
for c in chemins:
    lignes = [json.loads(l) for l in open(c, encoding="utf-8") if l.strip()]
    premier = next(d for d in lignes if d.get("type") == "user")
    carte = "\n".join(b.get("text", "") for b in blocs(premier) if b.get("type") == "text")
    relue = re.search(r"relire[^\n]*:\s*\n\s*\n?\s*(\S+)", carte)
    relue = relue.group(1) if relue else "?"
    ids = set(re.findall(r"^\d+:## (\S+) \[", carte, re.M)) - {relue}
    libelles = set(re.findall(r"^- \*\*([^*]+)\*\* :", carte, re.M))
    courant = re.search(r"^- \*\*fichier de fiches courant\*\* : (.+?)(?:\s*\([^)]*\))?\s*$", carte, re.M)
    fichier = ""
    vu = False   # premier résultat d'outil lu
    dit = []     # ce que l'assistant écrit : texte et entrées d'outil
    appels = []
    for d in lignes:
        for b in blocs(d):
            t = b.get("type")
            if d.get("type") == "assistant" and t == "text":
                dit.append(b["text"])
            elif d.get("type") == "assistant" and t == "tool_use":
                dit.append(json.dumps(b.get("input"), ensure_ascii=False))
                appels.append((b.get("name"), b.get("input") or {}))
            elif t == "tool_result" and not vu:
                vu = True
                r = texte_resultat(b)
                f = None if SANS_FICHIER else re.search(r"^FICHIER=(.+)$", r, re.M)
                a = re.search(r"^APRÈS=(.+)$", r, re.M)
                if f:
                    fichier = norme(f.group(1))
                elif a and courant:
                    fichier = norme(os.path.join(a.group(1).strip(), courant.group(1)))
    dit = "\n".join(dit)
    n = dict.fromkeys(COLS, 0)
    n["autres"] = sum(len(re.findall(r"(?<![A-Za-z0-9])%s(?![0-9])" % re.escape(i), dit)) for i in ids)
    n["prochaine"] = len(re.findall(r"PROCHAINE", dit))
    for lib in libelles:
        e = re.escape(lib)
        k = len(re.findall(r"\*\*%s\*\*|«\s*%s\s*»|\\?\"%s\\?\"" % (e, e, e), dit))
        n["libelles"] += k
        par_libelle[lib] = par_libelle.get(lib, 0) + k
    for nom, entree in appels:
        if not fichier:
            break
        if nom == "Read" and norme(entree.get("file_path")) == fichier:
            n["plage" if ("offset" in entree or "limit" in entree) else "entier"] += 1
        elif nom == "Grep" and norme(entree.get("path")) == fichier:
            n["grep"] += 1
    for k in COLS:
        total[k] += n[k]
        avec[k] += n[k] > 0
    ident = os.path.basename(c)[len("agent-"):-len(".jsonl")]
    print("%-18s %-7s %s%s" % (ident, relue, " ".join("%9d" % n[k] for k in COLS),
                               "" if fichier else "  (pas de chemin)"))
print("TOTAL %d transcriptions · %s" % (len(chemins), " · ".join(
    "%s %d (%d transcr.)" % (k, total[k], avec[k]) for k in COLS)))
if "--detail" in sys.argv:
    for lib, k in sorted(par_libelle.items(), key=lambda x: -x[1]):
        if k:
            print("LIBELLÉ %s %d" % (lib, k))
