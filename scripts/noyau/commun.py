"""La tête de `vlp_coeur.py` : lire un fichier, ses gardes, l'archive de l'index (REF45 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import io
import os
import re
import sys

import vlp_hook

from noyau import etat
from noyau.facade import coeur

__all__ = [
    "TITRE",
    "TITRE_GENERIQUE",
    "PREFIXE",
    "COURANT",
    "ALIAS",
    "SESSION",
    "FERMANT",
    "CHANTIERS_POSSIBLES",
    "METHODE",
    "FORMAT_DEBUT",
    "FORMAT_FIN",
    "section",
    "premier_lancement",
    "tampon_neuf",
    "une_fois",
    "lire",
    "lignes_de",
    "Absent",
    "chemin_garde",
    "lignes_gardees",
    "lignes_du_projet",
    "chemin_archive",
    "lignes_index",
    "ARCHIVE_TETE",
    "NUMERO_LIGNE",
    "numero_ligne",
    "archiver",
    "cmd_archiver",
]


TITRE = re.compile(r"^## [A-Z]{1,3}[0-9]")
TITRE_GENERIQUE = re.compile(r"^##\s+\S")
PREFIXE = re.compile(r"^[A-Z]{1,3}")
COURANT = re.compile(r"^\s*-\s*\*\*fichier de fiches courant\*\*\s*:\s*(.+?)\s*$")
ALIAS = re.compile(r"^\s*-\s*\*\*alias\*\*\s*:\s*(\S+)")
SESSION = re.compile(r"^\*\*Session\*\* : (.+?)(?: \([^()]*\))?\s*$")    # l'id seul : le ` (<rôle>)` de la nuit n'en est pas
FERMANT = "<!-- /FICHE -->"
CHANTIERS_POSSIBLES = re.compile(r"^\s*-\s*\*\*chantiers possibles\*\*\s*:\s*(.+?)\s*$", re.MULTILINE)
METHODE = re.compile(r"^\s*-\s*\*\*méthode\*\*\s*:\s*(.+?)\s*$", re.MULTILINE)
FORMAT_DEBUT, FORMAT_FIN = "## Le fichier de fiches", "## Les deux formes de critère de fin"


def section(lignes, debut, fin):
    """(a, b), lignes 1-basées incluses, ou None : du premier titre `## ` qui
    vérifie `debut` jusqu'avant le premier titre qui suit celui qui vérifie
    `fin` — cherché à partir du titre de début —, ou jusqu'à la fin du fichier.
    None si aucun titre ne vérifie `debut`, ou aucun ensuite `fin`. Un `## `
    dans un bloc ``` n'est pas un titre."""
    titres, en_bloc = [], False
    for i, ligne in enumerate(lignes):
        if ligne.lstrip().startswith("```"):
            en_bloc = not en_bloc
        elif not en_bloc and TITRE_GENERIQUE.match(ligne):
            titres.append(i)
    d = next((k for k, i in enumerate(titres) if debut(lignes[i])), None)
    if d is None:
        return None
    f = next((k for k in range(d, len(titres)) if fin(lignes[titres[k]])), None)
    if f is None:
        return None
    return titres[d] + 1, titres[f + 1] if f + 1 < len(titres) else len(lignes)


def premier_lancement(texte, nom=""):
    """Vrai si ce lancement est le premier à traiter cette entrée de hook : le tampon de `vlp_hook`,
    nommé par `nom` + entrée — le nom, car `filet` et `hook` reçoivent la même entrée (PYT2) —, dans
    `TAMPON_HOOKS` ; ses replis (`None`, `VLP_SANS_TAMPON`, une autre `OSError`) y sont dits."""
    return tampon_neuf(vlp_hook.nom_tampon(texte, nom))


def tampon_neuf(nom):
    """Vrai si `<TAMPON_HOOKS>/<nom>` se crée en exclusif — `vlp_hook.tampon_neuf`, dans le dossier de ce module."""
    return vlp_hook.tampon_neuf(nom, etat.TAMPON_HOOKS)


def une_fois(entree, commande, *args):
    """Lire l'entrée d'un hook une fois : 0, muet, si un autre lanceur l'a déjà traitée ; une entrée
    déjà triée par le lanceur (`vlp_hook.Triee`, VIT8) passe sans re-tri."""
    if isinstance(entree, vlp_hook.Triee):
        return commande(entree, *args)
    texte = (entree or sys.stdin).read()
    return commande(io.StringIO(texte), *args) if premier_lancement(texte, commande.__name__) else 0


def lire(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def lignes_de(chemin):
    lignes = lire(chemin).split("\n")
    if lignes and lignes[-1] == "":
        lignes.pop()
    return lignes


class Absent(ValueError):
    """Un chemin nommé par `CHANTIER.md` ne désigne pas de fichier. Sous-classe
    de `ValueError` : les `except ValueError` qui gardent déjà leur contexte la
    voient ; sinon `main` l'attrape — c'est le seul endroit où la règle vit."""


def chemin_garde(chemin, libelle="fichier", nom=None):
    """Le chemin, ou `Absent` : le point unique où un chemin venu de
    `CHANTIER.md` est vérifié. `nom` : ce qu'on montre quand le relatif parle
    mieux que l'absolu."""
    if not os.path.isfile(chemin):
        raise Absent("%s introuvable : %s" % (libelle, nom or chemin))
    return chemin


def lignes_gardees(chemin, libelle="fichier", nom=None):
    """Les lignes d'un chemin gardé : toute lecture d'un chemin de `CHANTIER.md`
    passe par ici."""
    return lignes_de(chemin_garde(chemin, libelle, nom))


def lignes_du_projet(projet, chemin_relatif, libelle):
    """Les lignes d'un chemin relatif au projet, gardées."""
    return lignes_gardees(os.path.join(projet, chemin_relatif), libelle, chemin_relatif)


def chemin_archive(index):
    """L'archive des lignes clos, dans le dossier de l'index : son chemin ne se
    retape jamais, il se dérive d'ici (chantier IDX)."""
    dossier = os.path.dirname(index)
    return (dossier.rstrip("/\\") + "/" if dossier else "") + "00-INDEX-archive.md"


def lignes_index(projet, index):
    """Les lignes de l'index, puis celles de son archive si elle existe : un
    lecteur de l'index voit aussi les chantiers clos qu'on y a déplacés."""
    archive = os.path.join(projet, chemin_archive(index))
    return lignes_du_projet(projet, index, "index") + (lignes_de(archive) if os.path.isfile(archive) else [])


ARCHIVE_TETE = ["# Archive de l'index — les chantiers clos", "",
                "QUAND LIRE : on relit un chantier clos ; l'index n'en garde qu'une ligne qui renvoie ici.", "",
                "| Fichier | Lire quand |", "|---|---|"]
NUMERO_LIGNE = re.compile(r"^\|\s*`(\d\d)")


def numero_ligne(ligne):
    """Le numéro de fichier d'une ligne de table (2 premiers chiffres) ; sans numéro : après tout."""
    m = NUMERO_LIGNE.match(ligne)
    return int(m.group(1)) if m else 100


def archiver(idx, arch, nom_archive):
    """Déplace chaque ligne de table `**clos**` de l'index `idx` vers l'archive `arch` (None :
    créée avec `ARCHIVE_TETE`), triée par numéro ; pose dans l'index une ligne qui renvoie à
    `nom_archive`, si elle manque. Une ligne se déplace telle quelle, jamais réécrite ; relancée,
    rien ne change. Rend (index, archive ou None, lignes déplacées) (chantier IDX)."""
    clos = [k for k, l in enumerate(idx) if l.startswith("|") and "**clos**" in l]
    renvoi = "| `%s` |" % nom_archive
    a_renvoi = any(l.startswith(renvoi) for l in idx)
    if not clos and (a_renvoi or arch is None):
        return idx, arch, 0
    arch = list(ARCHIVE_TETE) if arch is None else list(arch)
    sep = next((k for k, l in enumerate(arch) if l.startswith("|---")), None)
    if sep is None:
        arch += [""] + ARCHIVE_TETE[-2:]
        sep = len(arch) - 1
    fin = sep + 1
    while fin < len(arch) and arch[fin].startswith("|"):
        fin += 1
    rangees = arch[sep + 1:fin]
    rangees += [idx[k] for k in clos if idx[k] not in rangees]
    arch[sep + 1:fin] = sorted(rangees, key=numero_ligne)
    nouvel = [l for k, l in enumerate(idx) if k not in clos]
    if not a_renvoi:
        rang = clos[0] if clos else max((k + 1 for k, l in enumerate(nouvel) if coeur.LIGNE_FICHIER.match(l)), default=len(nouvel))
        nouvel.insert(rang, renvoi + " on relit un chantier clos — chacun y a sa ligne, triée par numéro |")
    return nouvel, arch, len(clos)


def cmd_archiver(a, sortie):
    projet = a.projet
    if not coeur.equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    index = coeur.champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "index")
    if not index:
        sortie.write("GARDE: champ **index** absent de CHANTIER.md\n")
        return 1
    idx = lignes_du_projet(projet, index, "index")
    chemin_arch = os.path.join(projet, chemin_archive(index))
    arch = lignes_de(chemin_arch) if os.path.isfile(chemin_arch) else None
    nidx, narch, n = archiver(idx, arch, os.path.basename(chemin_arch))
    for chemin, avant, apres in ((os.path.join(projet, index), idx, nidx), (chemin_arch, arch, narch)):
        if apres is not None and apres != avant:
            with open(chemin, "w", encoding="utf-8", newline="") as fh:
                fh.write("\n".join(apres) + "\n")
    sortie.write("ARCHIVÉ %d · index %d lignes · archive %d lignes\n" % (n, len(nidx), len(narch or [])))
    return 0
