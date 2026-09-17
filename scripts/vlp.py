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
  · <n> écarts · <n> avertissements — <fichier>`. Un écart : sort 1.

Python 3 sans dépendance, zéro appel modèle.
"""
import argparse
import glob
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
    for nom, motif in (("## Le socle commun", r"^## Le socle"), ("## L'ordre des fiches", r"^## L.*ordre des fiches")):
        ou = [i for i, l in enumerate(lignes) if re.match(motif, l)]
        if not ou:
            ecarts.append((1, "section absente : %s" % nom))
        elif len(ou) > 1:
            ecarts.append((ou[1] + 1, "section en double : %s (déjà ligne %d)" % (nom, ou[0] + 1)))
        elif ou[0] > premiere:
            ecarts.append((ou[0] + 1, "section après la première fiche : %s" % nom))

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
    return sorted(ecarts), avert, len(vus), len(socle_lignes(lignes))


def cmd_valider(chemins, sortie):
    code = 0
    for chemin in chemins:
        if not os.path.isfile(chemin):
            sortie.write("%s:0: fichier introuvable\nINVALIDE 0 fiches · socle 0 lignes · 1 écarts · 0 avertissements — %s\n"
                         % (chemin, chemin))
            code = 1
            continue
        ecarts, avert, n, socle = valider_lignes(lignes_de(chemin))
        for ligne, message in ecarts:
            sortie.write("%s:%d: %s\n" % (chemin, ligne, message))
        for ligne, message in avert:
            sortie.write("%s:%d: avertissement : %s\n" % (chemin, ligne, message))
        sortie.write("%s %d fiches · socle %d lignes · %d écarts · %d avertissements — %s\n"
                     % ("INVALIDE" if ecarts else "VALIDE", n, socle, len(ecarts), len(avert), chemin))
        if ecarts:
            code = 1
    return code


# --- entrée ------------------------------------------------------------------

def main(argv, sortie=None):
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
    a = p.parse_args(argv)
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
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
