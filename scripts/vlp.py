#!/usr/bin/env python3
"""La mécanique du kit vlp : ce que les commandes faisaient au `sed` et à l'`awk`.

Sous-commandes :

- `carte [dossier]` — la carte d'un projet, à injecter avant le 1er tour d'une
  commande. Remonte jusqu'au premier `CHANTIER.md`. Trouvé : `PROJET=<racine>`,
  le fichier en entier, puis — si un fichier de fiches est courant — ses titres
  de fiches numérotés, `PROCHAINE=<fiche>` (la première non cochée, dans l'ordre
  du fichier) ou `PROCHAINE=aucune`, et une `GARDE` si le fichier a des lignes
  mais aucun titre au format attendu. Pas trouvé : une ligne `VOISIN=` par
  sous-dossier équipé, avec son alias, ou `AUCUN_PROJET`. Sort toujours 0 : la
  commande lit la sortie, elle ne doit pas se faire refuser l'injection.
- `extraire <fichier> <fiche>` — la fiche entre ses marqueurs, marqueurs
  compris, puis `--- fiche, lignes : N`. Sans marqueurs, repli sur le titre
  jusqu'au premier `---`, annoncé par une `GARDE`. Absente : sort 1.
- `socle <fichier>` — de `## Le socle commun` (compris) à `## L'ordre des
  fiches` (exclu), puis `--- socle, lignes : N`. Vide : sort 1.
- `sessions <fichier>` — un id de ligne `**Session**` par ligne, dédoublonnés,
  dans l'ordre du fichier.
- `valider <fichier>…` — les écarts d'un fichier de fiches, un par ligne
  `fichier:ligne: message`, puis `VALIDE|INVALIDE <n> fiches · socle <n> lignes
  · <n> écarts · <n> avertissements — <fichier>`. Avertit si une fiche ou le
  socle dépasse son seuil. Un écart : sort 1.
- `page <fichier> <page.html>` — régénère la page du chantier depuis le fichier
  de fiches : états, avancement, comptage, coûts (`**Session**`), date. Garde
  de la page l'en-tête, les notes, le journal, le blocage et le bilan.
  `--note <fiche> <texte>`, `--journal <texte>` (répétables) ; `--creer
  --projet P --titre T --resultat R` part du gabarit ; `--verifier` n'écrit
  rien et sort 1 si états ou avancement diffèrent du fichier.
- `hook` — le hook `PostToolUse` (`Write|Edit`) du plugin : lit sur stdin le
  JSON du hook, prend `tool_input.file_path` (relatif : contre `cwd`). Sort 0
  muet si ce n'est pas un fichier de fiches — JSON illisible, chemin absent, pas
  `.md`, ou ni marqueur `<!-- FICHE:X1 -->` ni `## Le socle commun` hors bloc de
  code. Sinon `valider` : écart → écarts, bilan et consigne sur stderr, sort 2 ;
  valide → le JSON `hookSpecificOutput` dont `additionalContext` est le bilan,
  sort 0.

Python 3 sans dépendance, zéro appel modèle.
"""
import argparse
import glob
import io
import json
import os
import re
import sys

TITRE = re.compile(r"^## [A-Z][0-9]")
COURANT = re.compile(r"^\s*-\s*\*\*fichier de fiches courant\*\*\s*:\s*(.+?)\s*$")
ALIAS = re.compile(r"^\s*-\s*\*\*alias\*\*\s*:\s*(\S+)")
SESSION = re.compile(r"^\*\*Session\*\* : (.+?)\s*$")
FERMANT = "<!-- /FICHE -->"


def lire(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def lignes_de(chemin):
    lignes = lire(chemin).split("\n")
    if lignes and lignes[-1] == "":
        lignes.pop()
    return lignes


# --- carte -------------------------------------------------------------------

def equipe(d):
    """Vrai si `d` porte `CHANTIER.md` à la casse exacte : sous Windows et
    macOS, `isfile` prendrait `commands/chantier.md` pour la carte."""
    try:
        return "CHANTIER.md" in os.listdir(d) and os.path.isfile(os.path.join(d, "CHANTIER.md"))
    except OSError:
        return False


def trouver(depart):
    d = os.path.abspath(depart)
    while True:
        if equipe(d):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def fichier_courant(carte_texte):
    """Le chemin du fichier de fiches courant, ou None s'il vaut « aucun »."""
    for ligne in carte_texte.split("\n"):
        m = COURANT.match(ligne)
        if m:
            valeur = re.sub(r"\s+\([^)]*\)$", "", m.group(1)).strip()
            return None if valeur.lower().startswith("aucun") else valeur
    return None


def fiches(chemin):
    """(nombre de lignes, [(numéro, titre)], prochaine ou None)."""
    lignes = lignes_de(chemin)
    titres = [(i, l) for i, l in enumerate(lignes, 1) if TITRE.match(l)]
    prochaine = next((l.split()[1] for _, l in titres if "[x]" not in l), None)
    return len(lignes), titres, prochaine


def carte(depart, sortie):
    racine = trouver(depart)
    if racine is None:
        voisins = sorted(os.path.join(v, "CHANTIER.md") for v in glob.glob(os.path.join(os.path.abspath(depart), "*"))
                         if equipe(v))
        for v in voisins:
            m = next((ALIAS.match(l) for l in lire(v).split("\n") if ALIAS.match(l)), None)
            sortie.write("VOISIN=%s alias=%s\n" % (os.path.dirname(v), m.group(1) if m else "?"))
        if not voisins:
            sortie.write("AUCUN_PROJET\n")
        return 0
    texte = lire(os.path.join(racine, "CHANTIER.md"))
    sortie.write("PROJET=%s\n--- CHANTIER.md ---\n%s" % (racine, texte))
    if not texte.endswith("\n"):
        sortie.write("\n")
    courant = fichier_courant(texte)
    if courant is None:
        sortie.write("--- fichier de fiches courant : aucun ---\n")
        return 0
    chemin = os.path.join(racine, courant)
    if not os.path.isfile(chemin):
        sortie.write("GARDE: fichier de fiches introuvable : %s\n" % courant)
        return 0
    n, titres, prochaine = fiches(chemin)
    sortie.write("--- fiches : %s (%d lignes, %d titres) ---\n" % (courant, n, len(titres)))
    for i, l in titres:
        sortie.write("%d:%s\n" % (i, l))
    if n and not titres:
        sortie.write("GARDE: aucun titre de fiche au format '## X1' — ne rien conclure\n")
        return 0
    sortie.write("PROCHAINE=%s\n" % (prochaine or "aucune"))
    return 0


# --- extraire, socle, sessions -----------------------------------------------

def extraire_lignes(lignes, fiche):
    """(lignes de la fiche, garde ou None). Liste vide : fiche absente."""
    ouvrant = "<!-- FICHE:%s -->" % fiche
    debut = next((i for i, l in enumerate(lignes) if l.strip() == ouvrant), None)
    if debut is not None:
        # Un fermant oublié : `sed` avalait la fiche suivante sans rien dire.
        # On s'arrête au prochain marqueur ouvrant, et on le dit.
        fin = next((i for i in range(debut + 1, len(lignes))
                    if lignes[i].strip() == FERMANT or lignes[i].startswith("<!-- FICHE:")), len(lignes))
        if fin == len(lignes) or lignes[fin].strip() != FERMANT:
            return lignes[debut:fin], "GARDE: marqueur fermant absent après %s — fiche lue jusqu'au marqueur suivant ou la fin" % ouvrant
        return lignes[debut:fin + 1], None
    titre = "## %s " % fiche
    debut = next((i for i, l in enumerate(lignes) if l.startswith(titre)), None)
    if debut is None:
        return [], None
    fin = next((i for i in range(debut + 1, len(lignes)) if lignes[i].rstrip() == "---"), len(lignes) - 1)
    return lignes[debut:fin + 1], "GARDE: pas de marqueurs pour %s — repli du titre au premier '---', un '---' dans un bloc de code le coupe" % fiche


def socle_lignes(lignes):
    debut = next((i for i, l in enumerate(lignes) if l.startswith("## Le socle")), None)
    if debut is None:
        return []
    fin = next((i for i in range(debut + 1, len(lignes)) if re.match(r"^## L.*ordre des fiches", lignes[i])), len(lignes))
    return lignes[debut:fin]


def sessions_de(lignes):
    vues = []
    for l in lignes:
        m = SESSION.match(l)
        if m and m.group(1) not in vues:
            vues.append(m.group(1))
    return vues


def cmd_extraire(chemin, fiche, sortie):
    extrait, garde = extraire_lignes(lignes_de(chemin), fiche)
    if garde:
        sortie.write(garde + "\n")
    if not extrait:
        sortie.write("GARDE: fiche introuvable : %s\n--- fiche, lignes : 0\n" % fiche)
        return 1
    sortie.write("\n".join(extrait) + "\n--- fiche, lignes : %d\n" % len(extrait))
    return 0


def cmd_socle(chemin, sortie):
    extrait = socle_lignes(lignes_de(chemin))
    if extrait:
        sortie.write("\n".join(extrait) + "\n")
    sortie.write("--- socle, lignes : %d\n" % len(extrait))
    return 0 if extrait else 1


def cmd_sessions(chemin, sortie):
    for s in sessions_de(lignes_de(chemin)):
        sortie.write(s + "\n")
    return 0


# --- valider -----------------------------------------------------------------

OUVRANT = re.compile(r"^<!-- FICHE:(\S+) -->$")
CRITERE = "**Critère de fin**"
CRITERE_VISUEL = re.compile(r"^\*\*Critère de fin\*\* \(visuel\)")
CODE_EN_LIGNE = re.compile(r"`[^`]*`")
# Le seuil vit dans methode-chantier.md (« Si elle en fait 50, c'est deux
# fiches ») : ici, il n'est que cité.
SEUIL_FICHE = 50
# Le seuil vit dans methode-chantier.md (« Le socle fait au maximum 80 lignes ») :
# ici, il n'est que cité.
SEUIL_SOCLE = 80


def valider_lignes(lignes):
    """(écarts, avertissements, nombre de fiches, lignes du socle) ; un écart
    ou un avertissement est un couple (numéro de ligne, message)."""
    ecarts, avert = [], []
    blocs = []          # (id du marqueur, début, fin) — indices 0
    ouvert = None       # (id, début)
    for i, l in enumerate(lignes):
        s = l.strip()
        m = OUVRANT.match(s)
        if m:
            if ouvert:
                ecarts.append((i + 1, "marqueur imbriqué : <!-- FICHE:%s --> ouvert ligne %d sans fermant"
                               % (ouvert[0], ouvert[1] + 1)))
                blocs.append((ouvert[0], ouvert[1], i - 1))
            ouvert = (m.group(1), i)
        elif s == FERMANT:
            if ouvert:
                blocs.append((ouvert[0], ouvert[1], i))
                ouvert = None
            else:
                ecarts.append((i + 1, "marqueur fermant sans ouvrant"))
    if ouvert:
        ecarts.append((ouvert[1] + 1, "marqueur ouvrant sans fermant : <!-- FICHE:%s -->" % ouvert[0]))
        blocs.append((ouvert[0], ouvert[1], len(lignes) - 1))

    titres = [(i, l.split()[1]) for i, l in enumerate(lignes) if TITRE.match(l)]
    vus, fiches_ = {}, []
    for n, (i, ident) in enumerate(titres):
        if ident in vus:
            ecarts.append((i + 1, "identifiant en double : %s (déjà ligne %d)" % (ident, vus[ident] + 1)))
        vus.setdefault(ident, i)
        bloc = next((b for b in blocs if b[1] < i <= b[2]), None)
        if bloc is None:
            ecarts.append((i + 1, "titre sans marqueurs : %s" % ident))
            suivant = titres[n + 1][0] if n + 1 < len(titres) else len(lignes)
            fin = next((j for j in range(i + 1, suivant) if lignes[j].rstrip() == "---"), suivant) - 1
            fiches_.append((ident, i, fin))
        else:
            if bloc[0] != ident:
                ecarts.append((i + 1, "marqueur %s ≠ titre %s" % (bloc[0], ident)))
            fiches_.append((ident, bloc[1], bloc[2]))

    premiere = min([i for i, _ in titres] + [b[1] for b in blocs] + [len(lignes)])
    socle = socle_lignes(lignes)
    for nom, motif in (("## Le socle commun", r"^## Le socle"), ("## L'ordre des fiches", r"^## L.*ordre des fiches")):
        ou = [i for i, l in enumerate(lignes) if re.match(motif, l)]
        if not ou:
            ecarts.append((1, "section absente : %s" % nom))
        elif len(ou) > 1:
            ecarts.append((ou[1] + 1, "section en double : %s (déjà ligne %d)" % (nom, ou[0] + 1)))
        elif ou[0] > premiere:
            ecarts.append((ou[0] + 1, "section après la première fiche : %s" % nom))

    if socle and len(socle) > SEUIL_SOCLE:
        debut_socle = next((i for i, l in enumerate(lignes) if l.startswith("## Le socle")), 1)
        avert.append((debut_socle + 1, "socle : %d lignes, au-delà du seuil de methode-chantier.md (%d)"
                      % (len(socle), SEUIL_SOCLE)))

    for ident, debut, fin in fiches_:
        corps = lignes[debut:fin + 1]
        if not any(l.startswith(CRITERE) for l in corps):
            ecarts.append((debut + 1, "fiche %s sans ligne %s" % (ident, CRITERE)))
        ouvert_code = False   # un code en ligne peut commencer sur la ligne d'avant
        for j, l in enumerate(corps, debut + 1):
            if not l.strip() or l.lstrip().startswith("```"):
                ouvert_code = False
                continue
            # Une mention entre accents graves parle du marqueur, elle ne le pose pas.
            hors_code = CODE_EN_LIGNE.sub("", ("`" if ouvert_code else "") + l)
            if hors_code.count("`") % 2:
                ouvert_code, hors_code = True, hors_code[:hors_code.index("`")]
            else:
                ouvert_code = False
            if "(visuel)" in hors_code and not CRITERE_VISUEL.match(l):
                ecarts.append((j, "fiche %s : (visuel) hors de la ligne « %s (visuel) » — /vlp:enchainer ne s'y arrêtera pas"
                               % (ident, CRITERE)))
        if len(corps) > SEUIL_FICHE:
            avert.append((debut + 1, "fiche %s : %d lignes, au-delà du seuil de methode-chantier.md (%d)"
                          % (ident, len(corps), SEUIL_FICHE)))
    return sorted(ecarts), avert, len(vus), len(socle)


def cmd_valider(chemins, sortie):
    code = 0
    for chemin in chemins:
        if not os.path.isfile(chemin):
            sortie.write("%s:0: fichier introuvable\nINVALIDE 0 fiches · socle 0 lignes · 1 écarts · 0 avertissements — %s\n"
                         % (chemin, chemin))
            code = 1
            continue
        if rapport(chemin, lignes_de(chemin), sortie):
            code = 1
    return code


def rapport(chemin, lignes, sortie):
    """Écrit les écarts, les avertissements et le bilan ; rend le nombre d'écarts."""
    ecarts, avert, n, socle = valider_lignes(lignes)
    for ligne, message in ecarts:
        sortie.write("%s:%d: %s\n" % (chemin, ligne, message))
    for ligne, message in avert:
        sortie.write("%s:%d: avertissement : %s\n" % (chemin, ligne, message))
    sortie.write("%s %d fiches · socle %d lignes · %d écarts · %d avertissements — %s\n"
                 % ("INVALIDE" if ecarts else "VALIDE", n, socle, len(ecarts), len(avert), chemin))
    return len(ecarts)


# --- hook --------------------------------------------------------------------

MARQUE = re.compile(r"^<!-- FICHE:[A-Z][0-9]+ -->$")


def est_fichier_de_fiches(lignes):
    """Un marqueur de fiche ou le titre du socle, hors bloc de code : la méthode
    et les commandes en montrent dans des blocs, elles ne sont pas des fiches."""
    code = False
    for l in lignes:
        if l.lstrip().startswith("```"):
            code = not code
        elif not code and (MARQUE.match(l.strip()) or l.startswith("## Le socle commun")):
            return True
    return False


def cmd_hook(entree, sortie, erreur):
    try:
        d = json.loads(entree.read())
    except ValueError:
        return 0
    ti = d.get("tool_input") if isinstance(d, dict) else None
    chemin = ti.get("file_path") if isinstance(ti, dict) else None
    if not isinstance(chemin, str) or not chemin.lower().endswith(".md"):
        return 0
    if not os.path.isabs(chemin) and isinstance(d.get("cwd"), str):
        chemin = os.path.join(d["cwd"], chemin)
    if not os.path.isfile(chemin):
        return 0
    lignes = lignes_de(chemin)
    if not est_fichier_de_fiches(lignes):
        return 0
    texte = io.StringIO()
    if rapport(chemin, lignes, texte):
        erreur.write(texte.getvalue() + "Corrige ce fichier de fiches avant de continuer.\n")
        return 2
    bilan = texte.getvalue().strip().splitlines()[-1]
    sortie.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": bilan}},
                            ensure_ascii=False) + "\n")
    return 0


# --- page --------------------------------------------------------------------

# Le seuil vit dans le script (SEUIL_PAGE) : ici, il est défini et cité.
SEUIL_PAGE = 250
GABARIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "artefact-chantier.html")
LI_FICHE = re.compile(r'[ \t]*<li class="fiche"[^>]*>.*?</li>\n?', re.S)
UL_FICHES = re.compile(r'(<ul class="fiches">)(.*?)(\n[ \t]*</ul>)', re.S)
COUT = re.compile(r"\((\d[\d ]*)\) · (\d+) tours · ([\d,]+) \$")
_mesure = None


def mesure():
    """`mesure-tokens.py`, importé une fois (le tiret interdit `import`)."""
    global _mesure
    if _mesure is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mesure_tokens", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesure-tokens.py"))
        _mesure = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mesure)
    return _mesure


def esc(texte):
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def milliers(n):
    return "{:,}".format(n).replace(",", " ")


def arrondi(n):
    """La convention de coût en tête de templates/artefact-chantier.html."""
    if n < 1000:
        return str(n)
    valeur, unite = (n / 1_000_000, "M") if n >= 1_000_000 else (n / 1000, "k")
    return "≈%s%s (%s)" % (("%.1f" % valeur).replace(".", ","), unite, milliers(n))


def ligne_cout(total, tours, usd):
    return "%s · %d tours · %s $" % (arrondi(total), tours, "?" if usd is None else ("%.2f" % usd).replace(".", ","))


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
    """(total, tours, usd) lus sur une ligne de coût affichée, ou None."""
    c = texte and COUT.search(texte)
    if not c:
        return None
    from decimal import Decimal
    return int(c.group(1).replace(" ", "")), int(c.group(2)), Decimal(c.group(3).replace(",", "."))


def couts(fiches_, anciens, ancien_total, gardes):
    """({id: ligne de coût}, (total, tours, usd) ou None). Une session portée
    par plusieurs fiches : les premières gardent le coût déjà affiché (l'écart
    du compteur à leur clôture), la dernière prend le reste — moins la part que
    l'ancienne page n'attribuait à aucune fiche (le cadrage joué dans la même
    session), si une seule session est partagée."""
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
            base = (base[0] - c[0], base[1] - c[1], base[2] - c[2])
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
            usd = None if usd is None else usd - base[2]
        for ident in porteurs[:-1]:
            ancien = anciens.get(ident, (None, None, None))[2]
            c = triplet(ancien)
            if not c:
                gardes.append("GARDE: %s partage la session %s sans coût affiché — tout le coût va sur %s"
                              % (ident, s, porteurs[-1]))
                continue
            rendu[ident] = ancien
            total, tours = total - c[0], tours - c[1]
            usd = None if usd is None else usd - c[2]
        rendu[porteurs[-1]] = ligne_cout(total, tours, usd)
    mesurees = [r for r in mesures.values() if r]
    if not mesurees:
        return rendu, None
    usd = None if any(r["usd_exact"] is None for r in mesurees) else sum(r["usd_exact"] for r in mesurees)
    return rendu, (sum(r["total"] for r in mesurees), sum(r["tours"] for r in mesurees), usd)


def comptage(fiches_, etat):
    faites = sum(1 for e in etat.values() if e == "faite")
    texte = "%d fiches · %d %s" % (len(fiches_), faites, "faite" if faites <= 1 else "faites")
    courante = next((i for i, e in etat.items() if e in ("encours", "bloquee")), None)
    if courante:
        texte += " · %s : %s" % ("bloquée" if etat[courante] == "bloquee" else "en cours", courante)
    return texte


def creer(fichier, projet, titre, resultat):
    html = lire(GABARIT)
    fiches_ = fiches_du_fichier(lignes_de(fichier))
    plage = "%s–%s" % (fiches_[0][0], fiches_[-1][0]) if fiches_ else ""
    remplacements = [
        (r"<title>.*?</title>", "<title>%s — %s</title>" % (esc(projet), esc(titre))),
        (r'(<div class="eyebrow">).*?(</div>)', r"\g<1>%s · fiches %s\g<2>" % (esc(projet), plage)),
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


def regenerer(html, fichier, notes, journal, date, gardes):
    lignes = lignes_de(fichier)
    fiches_ = fiches_du_fichier(lignes)
    if not fiches_:
        raise ValueError("aucun titre de fiche au format '## X1' dans %s" % fichier)
    anciens = lis_page(html)
    etat = etats(fiches_, anciens)
    ancien_total = re.search(r'<p class="mono cout-total">(.*?)</p>', html, re.S)
    cout, total = couts(fiches_, anciens, ancien_total and ancien_total.group(1), gardes)
    etiquette = {"faite": "faite", "encours": "en cours", "bloquee": "bloquée", None: "à faire"}
    items = []
    for ident, titre, _, _ in fiches_:
        e = etat[ident]
        note = esc(notes[ident]) if ident in notes else anciens.get(ident, (None, None))[1]
        li = ['      <li class="fiche"%s>' % (' data-etat="%s"' % e if e else ""),
              '        <span class="id">%s</span><span class="titre">%s</span>' % (ident, esc(titre)),
              '        <span class="etat">%s</span>' % etiquette[e]]
        if note:
            li.append('        <span class="note">%s</span>' % note)
        if ident in cout:
            li.append('        <span class="cout mono">%s</span>' % cout[ident])
        items.append("\n".join(li + ["      </li>"]))
    prefixe = re.search(r'<p class="mono cout-total">(.*?) : ', html)
    prefixe = prefixe.group(1) if prefixe else "Coût du chantier"
    html = re.sub(r'\n[ \t]*<p class="mono cout-total">.*?</p>', "", html, flags=re.S)
    bloc = "\n" + "\n".join(items)
    if total:
        bloc_total = '\n    <p class="mono cout-total">%s : %s</p>' % (prefixe, ligne_cout(*total))
    else:
        bloc_total = ""
    html, n = UL_FICHES.subn(lambda m: m.group(1) + bloc + m.group(3) + bloc_total, html, count=1)
    if not n:
        raise ValueError("page : liste des fiches introuvable")
    spans = "".join('<span%s></span>' % (' data-etat="%s"' % etat[f[0]] if etat[f[0]] else "") for f in fiches_)
    html, n = re.subn(r'(<div class="avancement">\s*).*?(\s*</div>)', lambda m: m.group(1) + spans + m.group(2), html, count=1, flags=re.S)
    html, n2 = re.subn(r'(<p class="mono" style="margin-top:.5rem">).*?(</p>)',
                       lambda m: m.group(1) + comptage(fiches_, etat) + m.group(2), html, count=1, flags=re.S)
    if not (n and n2):
        raise ValueError("page : avancement ou ligne de comptage introuvable")
    blocage = re.search(r'<section( hidden)?>(\s*<h2>Arrêt sur blocage</h2>\s*<div class="blocage">\s*<p>)(.*?)</p>', html, re.S)
    if blocage and not blocage.group(1):
        fiche_bloquee = re.match(r"\s*([A-Z][0-9]+)", blocage.group(3))
        if fiche_bloquee and etat.get(fiche_bloquee.group(1)) == "faite":
            html = html[:blocage.start()] + "<section hidden>" + html[blocage.start() + len("<section>"):]
    for texte in journal:
        ligne = '      <li><time datetime="%s">%s</time><span>%s</span></li>' % (date, date, esc(texte))
        html, n = re.subn(r'(<ul class="journal">.*?)(\n[ \t]*</ul>)', lambda m: m.group(1) + "\n" + ligne + m.group(2),
                          html, count=1, flags=re.S)
        if not n:
            raise ValueError("page : journal introuvable")
    html = re.sub(r'(Mis à jour le <span class="mono">).*?(</span>)', lambda m: m.group(1) + date + m.group(2), html, count=1)
    return html, fiches_, etat, total


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


def cmd_page(a, sortie):
    date = a.date or __import__("datetime").date.today().isoformat()
    if a.creer:
        if os.path.exists(a.page):
            sortie.write("GARDE: la page existe déjà : %s — --creer n'écrase rien\n" % a.page)
            return 1
        if not (a.projet and a.titre and a.resultat):
            sortie.write("GARDE: --creer demande --projet, --titre et --resultat\n")
            return 1
        html = creer(a.fichier, a.projet, a.titre, a.resultat)
    elif not os.path.isfile(a.page):
        sortie.write("GARDE: page introuvable : %s — --creer pour la créer\n" % a.page)
        return 1
    else:
        html = lire(a.page)
    if a.verifier:
        return verifier_page(html, a.fichier, sortie)
    gardes = []
    try:
        html, fiches_, etat, total = regenerer(html, a.fichier, dict(a.note or []), a.journal or [], date, gardes)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    with open(a.page, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    n = html.count("\n") + (0 if html.endswith("\n") else 1)
    for g in gardes:
        sortie.write(g + "\n")
    sortie.write("PAGE %s · %s · %d lignes · total %s\n"
                 % (a.page, comptage(fiches_, etat), n, ligne_cout(*total) if total else "non mesuré"))
    if n > SEUIL_PAGE:
        sortie.write("GARDE: %d lignes, au-delà du seuil du script (%d) — la page est relue à chaque fiche\n"
                     % (n, SEUIL_PAGE))
    return 0


# --- entrée ------------------------------------------------------------------

def main(argv, sortie=None, entree=None, erreur=None):
    sortie = sortie or sys.stdout
    p = argparse.ArgumentParser(prog="vlp.py", description="La mécanique du kit vlp.")
    sous = p.add_subparsers(dest="cmd", required=True)
    c = sous.add_parser("carte")
    c.add_argument("dossier", nargs="?", default=None)
    e = sous.add_parser("extraire")
    e.add_argument("fichier")
    e.add_argument("fiche")
    s = sous.add_parser("socle")
    s.add_argument("fichier")
    se = sous.add_parser("sessions")
    se.add_argument("fichier")
    v = sous.add_parser("valider")
    v.add_argument("fichiers", nargs="+")
    pg = sous.add_parser("page")
    pg.add_argument("fichier")
    pg.add_argument("page")
    pg.add_argument("--note", nargs=2, action="append", metavar=("FICHE", "TEXTE"))
    pg.add_argument("--journal", action="append")
    pg.add_argument("--creer", action="store_true")
    pg.add_argument("--projet")
    pg.add_argument("--titre")
    pg.add_argument("--resultat")
    pg.add_argument("--verifier", action="store_true")
    pg.add_argument("--date")
    sous.add_parser("hook")
    a = p.parse_args(argv)
    if a.cmd == "hook":
        return cmd_hook(entree or sys.stdin, sortie, erreur or sys.stderr)
    if a.cmd == "page":
        if not os.path.isfile(a.fichier):
            sortie.write("GARDE: fichier introuvable : %s\n" % a.fichier)
            return 1
        return cmd_page(a, sortie)
    if a.cmd == "carte":
        return carte(a.dossier or os.getcwd(), sortie)
    if a.cmd == "valider":
        return cmd_valider(a.fichiers, sortie)
    if not os.path.isfile(a.fichier):
        sortie.write("GARDE: fichier introuvable : %s\n" % a.fichier)
        return 1
    if a.cmd == "extraire":
        return cmd_extraire(a.fichier, a.fiche, sortie)
    if a.cmd == "socle":
        return cmd_socle(a.fichier, sortie)
    return cmd_sessions(a.fichier, sortie)


if __name__ == "__main__":
    # Sous Windows, la console n'est pas en UTF-8 : sans ceci, les accents
    # sortent illisibles.
    for flux in (sys.stdin, sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
