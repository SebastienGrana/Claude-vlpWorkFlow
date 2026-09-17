#!/usr/bin/env python3
"""Rend la carte d'un projet vlp, pour l'injecter avant le 1er tour d'une commande.

Remonte depuis le dossier courant (ou celui passé en argument) jusqu'au
premier `CHANTIER.md`. Trouvé : imprime `PROJET=<racine>`, le fichier en
entier, puis — si un fichier de fiches est courant — ses titres de fiches
numérotés, `PROCHAINE=<fiche>` (la première non cochée, dans l'ordre du
fichier) ou `PROCHAINE=aucune`, et une `GARDE` si le fichier a des lignes mais
aucun titre au format attendu. Pas trouvé : imprime une ligne `VOISIN=` par
sous-dossier équipé, avec son alias, ou `AUCUN_PROJET`.

Python 3 sans dépendance, zéro appel modèle. Sort toujours 0 : la commande lit
la sortie, elle ne doit pas se faire refuser l'injection.
"""
import glob
import os
import re
import sys

TITRE = re.compile(r"^## [A-Z][0-9]")
COURANT = re.compile(r"^\s*-\s*\*\*fichier de fiches courant\*\*\s*:\s*(.+?)\s*$")
ALIAS = re.compile(r"^\s*-\s*\*\*alias\*\*\s*:\s*(\S+)")


def lire(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


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


def fichier_courant(carte):
    """Le chemin du fichier de fiches courant, ou None s'il vaut « aucun »."""
    for ligne in carte.split("\n"):
        m = COURANT.match(ligne)
        if m:
            valeur = re.sub(r"\s+\([^)]*\)$", "", m.group(1)).strip()
            return None if valeur.lower().startswith("aucun") else valeur
    return None


def fiches(chemin):
    """(nombre de lignes, [(numéro, titre)], prochaine ou None)."""
    lignes = lire(chemin).split("\n")
    if lignes and lignes[-1] == "":
        lignes.pop()
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
        return
    texte = lire(os.path.join(racine, "CHANTIER.md"))
    sortie.write("PROJET=%s\n--- CHANTIER.md ---\n%s" % (racine, texte))
    if not texte.endswith("\n"):
        sortie.write("\n")
    courant = fichier_courant(texte)
    if courant is None:
        sortie.write("--- fichier de fiches courant : aucun ---\n")
        return
    chemin = os.path.join(racine, courant)
    if not os.path.isfile(chemin):
        sortie.write("GARDE: fichier de fiches introuvable : %s\n" % courant)
        return
    n, titres, prochaine = fiches(chemin)
    sortie.write("--- fiches : %s (%d lignes, %d titres) ---\n" % (courant, n, len(titres)))
    for i, l in titres:
        sortie.write("%d:%s\n" % (i, l))
    if n and not titres:
        sortie.write("GARDE: aucun titre de fiche au format '## X1' — ne rien conclure\n")
        return
    sortie.write("PROCHAINE=%s\n" % (prochaine or "aucune"))


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    carte(argv[1] if len(argv) > 1 else os.getcwd(), sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
