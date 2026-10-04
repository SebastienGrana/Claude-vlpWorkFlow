"""La santé du code, fonction par fonction : les cinq comptes du socle de VIT, la docstring, et le cliquet.

Lancé par `vlp.py sante` (fiche VIT15), qui en documente la ligne de commande ; Python 3 sans dépendance.
ruff, s'il est là, est appelé — jamais importé — et ses comptes font foi. Sinon, ce module compte par `ast`
en suivant les règles de ruff, relevées par sondes sur ruff 0.16.10 (`context AI/08-etat.md`, 2026-10-04) :
ses comptes sont dits « estimés », rien ne garantissant l'accord sur du code que les sondes n'ont pas couvert.

Le cliquet compare chaque fonction à la base (`scripts/sante-base.json`).
- Une fonction se suit par son fichier et son nom qualifié (`Classe.methode`, `externe.interne`, `nom#2`
  pour un doublon). Elle est touchée si son empreinte a changé — son texte, sans son nom, son retrait ni ses
  fins de ligne. Renommée ou déplacée, elle retrouve la fonction disparue de la base qui avait son empreinte.
- Une fonction neuve passe les cinq seuils. Un compte d'une vieille fonction empire quand il passe au-dessus
  du plus haut de son seuil et de sa base : sous les seuils, elle grandit jusqu'au seuil, comme une neuve.
- Toute fonction neuve ou touchée a sa docstring. Un `test-*.py` n'a ni instructions ni docstring à tenir.
"""
import ast
import collections
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

COMPTES = ("complexité", "branches", "arguments", "instructions", "imbrication")
SEUILS = (10, 12, 5, 50, 5)     # les défauts de ruff : `ruff rule C901`, `ruff config lint.pylint`…
REGLES = ("C901", "PLR0912", "PLR0913", "PLR0915", "PLR1702")
REGLAGES = ("lint.mccabe.max-complexity", "lint.pylint.max-branches", "lint.pylint.max-args",
            "lint.pylint.max-statements", "lint.pylint.max-nested-blocks")
EXEMPTS_TESTS = ("instructions",)     # un long scénario de test reste permis (socle de VIT, Q4)
BASE = "scripts/sante-base.json"
FORMAT = 1
MUET = re.compile(r"^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$")    # `lint.dummy-variable-rgx` de ruff, par défaut
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)
ESSAIS = tuple(t for t in (ast.Try, getattr(ast, "TryStar", None)) if t is not None)     # TryStar : 3.11
CHOIX = tuple(t for t in (getattr(ast, "Match", None),) if t is not None)                # Match : 3.10
BOUCLES = (ast.For, ast.AsyncFor, ast.While)
BLOCS = (ast.If, ast.With, ast.AsyncWith) + BOUCLES + ESSAIS     # `match` ne compte pas dans l'imbrication


def sous_corps(s):
    """Rendre les suites d'instructions qu'une instruction contient, dans l'ordre du texte."""
    if isinstance(s, ESSAIS):
        return [s.body] + [h.body for h in s.handlers] + [s.orelse, s.finalbody]
    if isinstance(s, CHOIX):
        return [c.body for c in s.cases]
    return [getattr(s, "body", []), getattr(s, "orelse", [])]


def est_elif(s):
    """Dire si le `else` d'un `if` n'est qu'un `elif` : un seul `if`, à la colonne du premier."""
    return len(s.orelse) == 1 and isinstance(s.orelse[0], ast.If) and s.orelse[0].col_offset == s.col_offset


def irrefutable(cas):
    """Dire si un `case` attrape tout : `case _:` ou `case nom:`, sans garde."""
    return cas.guard is None and isinstance(cas.pattern, ast.MatchAs) and cas.pattern.pattern is None


def complexite_propre(s):
    """Rendre ce qu'une instruction ajoute à la complexité de McCabe (C901), sans ce qu'elle contient : 1 par
    `if`, `elif`, boucle ou fonction imbriquée, 1 par `except` et pour le `else` d'un `try`, 1 par `case`
    — le dernier gratuit s'il attrape tout."""
    if isinstance(s, (ast.If,) + BOUCLES + DEFS):
        return 1
    if isinstance(s, ESSAIS):
        return len(s.handlers) + (1 if s.orelse else 0)
    if isinstance(s, CHOIX):
        return len(s.cases) - (1 if s.cases and irrefutable(s.cases[-1]) else 0)
    return 0


def complexite(corps) -> int:
    """Rendre ce qu'une suite d'instructions ajoute à la complexité, fonctions et classes imbriquées comprises."""
    return sum(complexite_propre(s) + sum(complexite(c) for c in sous_corps(s)) for s in corps)


def branches_propres(s):
    """Rendre les branches d'une instruction (PLR0912), sans ce qu'elle contient : 1 par `if` et par `elif`,
    1 par `else`, 1 par boucle et son `else`, 1 par `except`, `else` et `finally` d'un `try`, 1 par `case`."""
    if isinstance(s, ast.If):
        return 1 + (1 if s.orelse and not est_elif(s) else 0)
    if isinstance(s, BOUCLES):
        return 1 + (1 if s.orelse else 0)
    if isinstance(s, ESSAIS):
        return len(s.handlers) + (1 if s.orelse else 0) + (1 if s.finalbody else 0)
    if isinstance(s, CHOIX):
        return len(s.cases)
    return 0


def branches(corps) -> int:
    """Rendre les branches d'une suite d'instructions, sans entrer dans les fonctions ni les classes."""
    return sum(branches_propres(s) + sum(branches(c) for c in sous_corps(s))
               for s in corps if not isinstance(s, DEFS + (ast.ClassDef,)))


def instructions_propres(s):
    """Rendre ce qu'une instruction pèse dans le compte des instructions (PLR0915, à la Pylint), sans ce
    qu'elle contient : `return` et `for` 0, un `else` ou un `elif` 1, un `try` 1 et 1 par `except` (1 de plus
    s'il y en a plusieurs), son `else` 1, son `finally` 2, un `match` 1 et 1 par `case`, le reste 1."""
    if isinstance(s, (ast.Return, ast.For, ast.AsyncFor)):
        return 0
    if isinstance(s, ast.If):
        return 1 + (1 if s.orelse and not est_elif(s) else 0)
    if isinstance(s, ESSAIS):
        return (1 + len(s.handlers) + (1 if len(s.handlers) > 1 else 0) + (1 if s.orelse else 0)
                + (2 if s.finalbody else 0))
    if isinstance(s, CHOIX):
        return 1 + len(s.cases)
    return 1


def instructions(corps) -> int:
    """Rendre les instructions d'une suite, fonctions imbriquées comprises ; une classe compte sans son corps."""
    return sum(instructions_propres(s) + (0 if isinstance(s, ast.ClassDef) else
                                          sum(instructions(c) for c in sous_corps(s))) for s in corps)


def arguments(f, methode):
    """Compter les arguments comme ruff (PLR0913) : ni `*args` ni `**kwargs`, ni le premier d'une méthode
    (sauf sous `@staticmethod`), ni les noms muets (`_`, `_x`)."""
    a = f.args
    positionnels = list(a.posonlyargs) + list(a.args)
    if methode and not any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in f.decorator_list):
        positionnels = positionnels[1:]
    return sum(1 for x in positionnels + list(a.kwonlyargs) if not MUET.match(x.arg))


def imbriquer(corps, niveau, tete, fonction, profondeurs):
    """Parcourir `corps`, à `niveau` blocs sous la tête de sa chaîne, et noter la profondeur atteinte au compte
    de `tete`, la fonction qui contient le bloc de tête ; `fonction` est celle qui contient `corps`. Comme
    ruff (PLR1702) : la chaîne traverse les fonctions imbriquées, un `elif` reste au niveau de son `if`, et
    une chaîne née hors de toute fonction n'est comptée à aucune."""
    for s in corps:
        n, t = niveau, tete
        if isinstance(s, BLOCS):
            n, t = niveau + 1, (fonction if niveau == 0 else tete)
            if t is not None:
                profondeurs[t] = max(profondeurs.get(t, 0), n)
        f = s if isinstance(s, DEFS) else fonction
        if isinstance(s, ast.If) and est_elif(s):
            imbriquer(s.body, n, t, f, profondeurs)
            imbriquer(s.orelse, niveau, tete, f, profondeurs)
            continue
        for c in sous_corps(s):
            imbriquer(c, n, t, f, profondeurs)


def cueillir(corps, prefixe, en_classe, trouvees):
    """Ajouter à `trouvees` les fonctions de `corps` et de ce qu'il contient, dans l'ordre du texte, avec leur
    nom qualifié ; `en_classe` : la portée est une classe, une fonction y est une méthode."""
    for s in corps:
        if isinstance(s, DEFS):
            trouvees.append((prefixe + s.name, s, en_classe))
            cueillir(s.body, prefixe + s.name + ".", False, trouvees)
        elif isinstance(s, ast.ClassDef):
            cueillir(s.body, prefixe + s.name + ".", True, trouvees)
        else:
            for c in sous_corps(s):
                cueillir(c, prefixe, en_classe, trouvees)


def empreinte(f, lignes):
    """Rendre l'empreinte d'une fonction, 12 caractères : son texte sans son nom, son retrait ni ses espaces de
    fin — un déplacement ou un renommage la gardent, un changement du code la change."""
    texte = textwrap.dedent("\n".join(l.rstrip() for l in lignes[f.lineno - 1:f.end_lineno or f.lineno]))
    texte = re.sub(r"\bdef\s+%s\b" % re.escape(f.name), "def", texte, count=1)
    return hashlib.sha1(texte.encode("utf-8")).hexdigest()[:12]


def relatif(chemin, racine):
    """Rendre le chemin d'un fichier depuis la racine, en barres obliques ; sur un autre disque, tel quel."""
    try:
        return os.path.relpath(chemin, racine).replace("\\", "/")
    except ValueError:
        return chemin.replace("\\", "/")


def mesurer_fichier(racine, chemin):
    """Mesurer par `ast` les fonctions d'un fichier, dans l'ordre du texte ; rendre (fonctions, lignes)."""
    with open(chemin, encoding="utf-8") as fichier:
        texte = fichier.read().replace("\r\n", "\n")
    arbre = ast.parse(texte, filename=chemin)
    lignes = texte.split("\n")
    trouvees = []
    cueillir(arbre.body, "", False, trouvees)
    profondeurs = {}
    imbriquer(arbre.body, 0, None, None, profondeurs)
    vus = collections.Counter()
    fonctions = []
    for nom, f, methode in trouvees:
        vus[nom] += 1
        fonctions.append({
            "fichier": relatif(chemin, racine), "fonction": nom if vus[nom] == 1 else "%s#%d" % (nom, vus[nom]),
            "ligne": f.lineno, "fin": f.end_lineno or f.lineno, "empreinte": empreinte(f, lignes),
            "ast": [1 + complexite(f.body), branches(f.body), arguments(f, methode), instructions(f.body),
                    profondeurs.get(f, 0)],
            "ruff": None, "doc": ast.get_docstring(f, clean=False) is not None,
            "test": os.path.basename(chemin).startswith("test-")})
    return fonctions, len(lignes)


def carte_lignes(fonctions, nombre):
    """Rendre, pour chaque numéro de ligne, la fonction la plus intérieure qui le contient, ou None."""
    carte: list = [None] * (nombre + 2)
    for f in fonctions:     # dans l'ordre du texte : une fonction imbriquée passe après celle qui la contient
        for ligne in range(f["ligne"], f["fin"] + 1):
            carte[ligne] = f
    return carte


def cle(chemin):
    """Rendre la clé d'un chemin, liens résolus et casse comprise : ruff écrit les siens en absolu."""
    return os.path.normcase(os.path.realpath(chemin))


def version_de(commande):
    """Rendre la version de ruff que lance `commande`, ou None s'il ne répond pas."""
    try:
        r = subprocess.run(commande + ["--version"], capture_output=True, encoding="utf-8", errors="replace",
                           timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.match(r"ruff (\S+)", r.stdout or "")
    return m.group(1) if r.returncode == 0 and m else None


def trouver_ruff():
    """Trouver ruff — dans le PATH, sinon par `-m ruff` sous ce Python, puis sous `py -3` (Windows) — et
    rendre (commande, version), ou (None, None) s'il manque."""
    candidats = [[sys.executable, "-m", "ruff"]]
    chemin = shutil.which("ruff")
    if chemin:
        candidats.insert(0, [chemin])
    if os.name == "nt" and shutil.which("py"):
        candidats.append(["py", "-3", "-m", "ruff"])
    for commande in candidats:
        version = version_de(commande)
        if version:
            return commande, version
    return None, None


def lancer_ruff(commande, chemins):
    """Lancer ruff sur `chemins`, les cinq seuils à zéro pour que chaque fonction sorte ses comptes, sans
    fichier de réglages ni cache ; rendre sa sortie JSON, ou lever `ValueError`."""
    args = ["check", "--isolated", "--no-cache", "--preview", "--select", ",".join(REGLES),
            "--output-format", "json", "--exit-zero"]
    for reglage in REGLAGES:
        args += ["--config", "%s = 0" % reglage]
    try:
        r = subprocess.run(commande + args + list(chemins), capture_output=True, encoding="utf-8",
                           errors="replace", timeout=600)
    except (OSError, subprocess.SubprocessError) as e:
        raise ValueError("ruff ne se lance pas : %s" % e) from e
    if r.returncode != 0:
        dit = (r.stderr or "").strip()[:300]
        raise ValueError("ruff sort %d%s" % (r.returncode, " : " + dit if dit else ""))
    return r.stdout


def lire_ruff(texte, cartes):
    """Reporter sur les fonctions les comptes de la sortie JSON de ruff : un diagnostic va à la fonction la
    plus intérieure qui contient sa ligne, et le plus grand compte gagne (`PLR1702` en sort plusieurs)."""
    rang = {code: i for i, code in enumerate(REGLES)}
    for d in json.loads(texte):
        carte = cartes.get(cle(d.get("filename") or ""))
        m = re.search(r"\((\d+) > \d+\)", d.get("message") or "")
        ligne = (d.get("location") or {}).get("row")
        if carte is None or d.get("code") not in rang or not m or not isinstance(ligne, int) or ligne >= len(carte):
            continue
        f = carte[ligne]
        if f is not None:
            i = rang[d["code"]]
            f["ruff"][i] = max(f["ruff"][i], int(m.group(1)))


def mesurer(racine, chemins, ruff, sortie):
    """Mesurer les fonctions de `chemins` par `ast`, puis par ruff (`ruff` : commande et version, ou deux
    None) ; rendre (fonctions, version de ruff ou None). ruff en échec : une ligne le dit, `ast` reste seul."""
    fonctions, cartes = [], {}
    for chemin in chemins:
        trouvees, nombre = mesurer_fichier(racine, chemin)
        fonctions += trouvees
        cartes[cle(chemin)] = carte_lignes(trouvees, nombre)
    commande, version = ruff
    if commande is None:
        return fonctions, None
    for f in fonctions:
        f["ruff"] = [0] * len(REGLES)
    try:
        lire_ruff(lancer_ruff(commande, chemins), cartes)
    except ValueError as e:
        sortie.write("RUFF ÉCHEC %s — comptes estimés (ast)\n" % e)
        for f in fonctions:
            f["ruff"] = None
        return fonctions, None
    return fonctions, version


def seuils_de(f):
    """Rendre les seuils qui tiennent pour une fonction : ceux de ruff, sans les instructions d'un test."""
    return [None if f["test"] and nom in EXEMPTS_TESTS else s for nom, s in zip(COMPTES, SEUILS)]


def au_dessus(f, cote):
    """Rendre les comptes d'une fonction qui passent leur seuil."""
    return [nom for nom, n, s in zip(COMPTES, f[cote], seuils_de(f)) if s is not None and n > s]


def lieu(f):
    """Rendre où vit une fonction : fichier, ligne et nom qualifié."""
    return "%s:%d %s" % (f["fichier"], f["ligne"], f["fonction"])


def entete(mot, version):
    """Rendre la ligne de tête : d'où viennent les comptes, puis les seuils."""
    source = "ruff %s" % version if version else "sans ruff, comptes estimés (ast)"
    return "%s %s · seuils : %s\n" % (mot, source, " · ".join("%s %d" % c for c in zip(COMPTES, SEUILS)))


def bilan(fonctions, cote):
    """Rendre le bilan d'une liste de fonctions : combien, combien au-dessus d'un seuil, combien documentées."""
    hors = sum(1 for f in fonctions if au_dessus(f, cote))
    docs = sum(1 for f in fonctions if f["doc"])
    return "%d fonctions · %d au-dessus d'un seuil · %d avec docstring" % (len(fonctions), hors, docs)


def lister(fonctions, version, sortie):
    """Imprimer les comptes de chaque fonction, un `!` sur ceux qui passent leur seuil, un bilan par fichier et
    pour tout — puis, avec ruff, chaque compte `ast` qui s'en écarte."""
    cote = "ruff" if version else "ast"
    sortie.write(entete("SANTE", version))
    par_fichier = {}
    for f in fonctions:
        marques = ["%s %d%s" % (nom, n, "!" if s is not None and n > s else "")
                   for nom, n, s in zip(COMPTES, f[cote], seuils_de(f))]
        sortie.write("%s · %s · docstring %s\n" % (lieu(f), " · ".join(marques), "oui" if f["doc"] else "non"))
        par_fichier.setdefault(f["fichier"], []).append(f)
    for fichier, liste in par_fichier.items():
        sortie.write("FICHIER %s · %s\n" % (fichier, bilan(liste, cote)))
    sortie.write("TOTAL %d fichiers · %s\n" % (len(par_fichier), bilan(fonctions, cote)))
    if version:
        ecarts = [(f, nom, r, a) for f in fonctions for nom, r, a in zip(COMPTES, f["ruff"], f["ast"]) if r != a]
        accord = len(fonctions) - len({id(e[0]) for e in ecarts})
        sortie.write("AST=RUFF %d/%d fonctions\n" % (accord, len(fonctions)))
        for f, nom, r, a in ecarts:
            sortie.write("AST≠RUFF %s · %s ruff %d, ast %d\n" % (lieu(f), nom, r, a))
    return 0


def charger_base(chemin):
    """Lire la base du cliquet : None si elle n'existe pas ; illisible, `ValueError`."""
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8") as fichier:
        base = json.load(fichier)
    if not isinstance(base, dict) or base.get("format") != FORMAT or not isinstance(base.get("fonctions"), list):
        raise ValueError("%s : base illisible, format %d attendu" % (chemin, FORMAT))
    return base


def ecrire_base(chemin, fonctions, version, forcees):
    """Écrire la base, triée, une fonction par ligne : un diff Git s'y lit fonction par fonction. Les comptes
    ruff n'y sont que s'ils s'écartent des comptes `ast`."""
    lignes = []
    for f in sorted(fonctions, key=lambda f: (f["fichier"], f["fonction"])):
        entree = {"fichier": f["fichier"], "fonction": f["fonction"], "empreinte": f["empreinte"],
                  "ast": f["ast"], "doc": f["doc"]}
        if version and f["ruff"] != f["ast"]:
            entree["ruff"] = f["ruff"]
        lignes.append(json.dumps(entree, ensure_ascii=False))
    tete = json.dumps({"format": FORMAT, "ruff": version, "forcee": forcees}, ensure_ascii=False)[:-1]
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as fichier:
        fichier.write(tete + ', "fonctions": [\n' + ",\n".join(lignes) + "\n]}\n")


def apparier(fonctions, base):
    """Apparier chaque fonction à sa ligne de base : même fichier et même nom, sinon une fonction disparue de
    même empreinte (renommée ou déplacée) ; rendre [(fonction, ligne de base ou None)]."""
    par_nom = {(b["fichier"], b["fonction"]): b for b in base}
    presentes = {(f["fichier"], f["fonction"]) for f in fonctions}
    disparues = collections.defaultdict(list)
    for b in base:
        if (b["fichier"], b["fonction"]) not in presentes:
            disparues[b["empreinte"]].append(b)
    paires = []
    for f in fonctions:
        b = par_nom.get((f["fichier"], f["fonction"]))
        if b is None and disparues[f["empreinte"]]:
            b = disparues[f["empreinte"]].pop(0)
        paires.append((f, b))
    return paires


def cote_de(version, base):
    """Choisir les comptes à comparer — ceux de ruff si la même version a écrit la base, sinon ceux d'`ast` —
    et rendre (côté, ligne de tête)."""
    if version and base.get("ruff") == version:
        return "ruff", "CLIQUET sur ruff %s\n" % version
    raison = ("sans ruff" if not version else "base écrite sans ruff" if not base.get("ruff")
              else "ruff %s, base écrite par ruff %s" % (version, base["ruff"]))
    return "ast", "CLIQUET sur ast, comptes estimés (%s)\n" % raison


def ecarts_de(f, b, cote):
    """Rendre les écarts d'une fonction au cliquet : un compte au-dessus du plus haut de son seuil et de sa
    base, ou la docstring qui manque à une fonction neuve ou touchée, hors tests."""
    avant = None if b is None else b.get(cote, b["ast"])
    lignes = []
    for i, (nom, n, s) in enumerate(zip(COMPTES, f[cote], seuils_de(f))):
        if s is None or n <= (s if avant is None else max(s, avant[i])):
            continue
        if avant is None:
            lignes.append("SEUIL %s · %s %d, seuil %d (neuve)\n" % (lieu(f), nom, n, s))
        else:
            lignes.append("EMPIRE %s · %s %d → %d, seuil %d\n" % (lieu(f), nom, avant[i], n, s))
    if (b is None or b["empreinte"] != f["empreinte"]) and not f["doc"] and not f["test"]:
        lignes.append("DOCSTRING %s · sans docstring (%s)\n" % (lieu(f), "neuve" if b is None else "touchée"))
    return lignes


def ameliore(apres, avant):
    """Dire si des comptes ont baissé sans qu'aucun ne monte."""
    return any(a < b for a, b in zip(apres, avant)) and all(a <= b for a, b in zip(apres, avant))


def bilan_cliquet(paires, cote):
    """Rendre la ligne de bilan du cliquet : vieilles, dont touchées et renommées ou déplacées, neuves, et les
    améliorées que `--base` verrouillerait."""
    vieilles = [(f, b) for f, b in paires if b is not None]
    touchees = sum(1 for f, b in vieilles if b["empreinte"] != f["empreinte"])
    suivies = sum(1 for f, b in vieilles if (b["fichier"], b["fonction"]) != (f["fichier"], f["fonction"]))
    mieux = sum(1 for f, b in vieilles if ameliore(f[cote], b.get(cote, b["ast"])))
    texte = ("CLIQUET %d fonctions · vieilles %d, dont touchées %d, renommées ou déplacées %d · neuves %d"
             % (len(paires), len(vieilles), touchees, suivies, len(paires) - len(vieilles)))
    if mieux:
        texte += " · améliorées %d : `vlp.py sante --base` les verrouille" % mieux
    return texte + "\n"


def tenir_cliquet(racine, fonctions, version, sortie):
    """Comparer les fonctions à la base : imprimer chaque écart, le bilan, puis `CLIQUET TENU` (0) ou
    `CLIQUET ROMPU` (1) ; sans base, `GARDE:`."""
    base = charger_base(os.path.normpath(os.path.join(racine, BASE)))
    if base is None:
        sortie.write("GARDE: pas de base %s — `vlp.py sante --base` d'abord\n" % BASE)
        return 1
    cote, tete = cote_de(version, base)
    sortie.write(tete)
    paires = apparier(fonctions, base["fonctions"])
    ecarts = [l for f, b in paires for l in ecarts_de(f, b, cote)]
    sortie.write("".join(ecarts) + bilan_cliquet(paires, cote))
    if ecarts:
        sortie.write("CLIQUET ROMPU · %d écart(s)\n" % len(ecarts))
        return 1
    sortie.write("CLIQUET TENU\n")
    return 0


def poser_base(racine, fonctions, version, forcer, sortie):
    """Écrire la base. Si elle existe et que le cliquet tomberait, refuser de la relâcher — sauf `--forcer`,
    dont la raison reste écrite dans la base."""
    chemin = os.path.normpath(os.path.join(racine, BASE))
    ancienne = charger_base(chemin)
    forcees = list(ancienne.get("forcee") or []) if ancienne else []
    ecarts = []
    if ancienne is not None:
        cote = cote_de(version, ancienne)[0]
        ecarts = [l for f, b in apparier(fonctions, ancienne["fonctions"]) for l in ecarts_de(f, b, cote)]
    if ecarts and not forcer:
        sortie.write("".join(ecarts))
        sortie.write("GARDE: la base ne se relâche pas : %d écart(s) ci-dessus — corrige, ou "
                     "`--base --forcer \"<raison>\"`, rien écrit\n" % len(ecarts))
        return 1
    if ecarts:
        forcees.append({"date": datetime.date.today().isoformat(), "ecarts": len(ecarts), "raison": forcer})
    ecrire_base(chemin, fonctions, version, forcees)
    sortie.write("BASE %s · %d fonctions · %s%s\n" % (BASE, len(fonctions), "ruff %s" % version if version
                                                       else "sans ruff", " · relâchée : %s" % forcer if ecarts else ""))
    return 0


def chemins_de(racine, fichiers):
    """Rendre les fichiers à mesurer : ceux donnés, sinon les `.py` de `scripts/` sous la racine, triés."""
    if fichiers:
        return [os.path.abspath(f) for f in fichiers]
    chemins = sorted(glob.glob(os.path.join(racine, "scripts", "*.py")))
    if not chemins:
        raise ValueError("aucun fichier Python dans %s" % os.path.join(racine, "scripts"))
    return chemins


def principal(a, sortie, kit):
    """Lancer `vlp.py sante` : lister les comptes, poser la base (`--base`) ou tenir le cliquet (`--cliquet`).
    Avec `--si-base`, ne reprendre qu'une base qui existe : sans elle, `SANS BASE`, rien mesuré ni écrit — un
    projet sans cliquet n'en reçoit pas un, même sans `scripts/`."""
    racine = os.path.abspath(a.racine or kit)
    try:
        if (a.forcer or a.si_base) and not a.base:
            raise ValueError("%s ne va qu'avec --base" % ("--forcer" if a.forcer else "--si-base"))
        if a.si_base and not os.path.exists(os.path.join(racine, BASE)):
            sortie.write("SANS BASE %s · rien écrit\n" % BASE)
            return 0
        ruff = (None, None) if a.sans_ruff else trouver_ruff()
        fonctions, version = mesurer(racine, chemins_de(racine, a.fichiers), ruff, sortie)
        if a.base:
            return poser_base(racine, fonctions, version, a.forcer, sortie)
        if a.cliquet:
            return tenir_cliquet(racine, fonctions, version, sortie)
        return lister(fonctions, version, sortie)
    except SyntaxError as e:
        sortie.write("GARDE: %s:%s : %s\n" % (e.filename, e.lineno, e.msg))
    except (OSError, ValueError) as e:
        sortie.write("GARDE: %s\n" % e)
    return 1
