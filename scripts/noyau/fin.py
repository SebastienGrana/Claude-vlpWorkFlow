"""La fin de fiche en un appel (ALG4, demandé par l'utilisateur le 2026-11-08 : « un seul geste de fin de fiche ») :
santé, palier (dans le kit), coche, note, coût, commit — les sous-commandes de `vlp.py`, appelées dans ce processus.

Avant ALG4, `/vlp:tache` prescrivait 5 appels pour finir une fiche (`skills/tache/SKILL.md`, étape 6 bis). L'ordre
est celui de cette étape ; le premier `GARDE:` arrête tout, et rien ne s'écrit après lui.
"""
import io
import os
import re

from noyau.bac import est_kit
from noyau.commun import ecrire_lignes, lignes_de
from noyau.fiches import chemins_changes, partage_commit
from noyau.palier import palier_manquant
from noyau.relecture import git_texte

__all__ = ["CONSTATE", "cmd_fin", "etape", "etrangers", "noter_constate"]

CONSTATE = "**Constaté** : "   # la note d'une fiche faite, que la page relit à la clôture (ALG5)


def etape(argv):
    """Lancer `vlp.py <argv>` dans ce processus ; rendre (code de sortie, sortie). Un test le remplace."""
    from noyau import cli   # importé ici : `cli` importe ce module
    s = io.StringIO()
    code = cli.main(argv, s)
    return code, s.getvalue()


def noter_constate(fichier, fiche, texte):
    """Écrire `**Constaté** : <texte>` dans le bloc de `fiche`, avant sa ligne `**Dépend de**` (sinon juste sous son
    titre) ; une note déjà là est remplacée, jamais doublée. Rend False si la fiche est introuvable."""
    lignes = lignes_de(fichier)
    debut = next((i for i, l in enumerate(lignes) if re.match(r"## %s \[" % re.escape(fiche), l)), None)
    if debut is None:
        return False
    fin = next((i for i in range(debut + 1, len(lignes)) if lignes[i].startswith(("## ", "<!-- /FICHE"))), len(lignes))
    ligne = CONSTATE + " ".join(texte.split())
    deja = next((i for i in range(debut, fin) if lignes[i].startswith(CONSTATE)), None)
    if deja is not None:
        lignes[deja] = ligne
    else:
        dep = next((i for i in range(debut, fin) if lignes[i].startswith("**Dépend de**")), debut + 2)
        lignes[dep:dep] = [ligne]
    ecrire_lignes([(fichier, lignes)])
    return True


def etrangers(fichier, fiche, racine):
    """Les chemins changés sous `racine` qui ne relèvent ni de la ligne **Fichiers** de `fiche` ni des communs (le
    fichier de fiches, `scripts/sante-base.json` dans le kit) — le travail d'une autre séance du même dossier, que
    `git add -A` emporterait (Emergence-Ants, ca8aed1, 2026-11-08) ; triés, `None` si Git est illisible. Le tri est
    celui de `commiter` (`partage_commit`, ENA4)."""
    changes = chemins_changes(racine)
    if changes is None:
        return None
    communs = {os.path.relpath(fichier, racine).replace(os.sep, "/")}
    if est_kit(racine):
        communs.add("scripts/sante-base.json")
    return sorted(partage_commit(lignes_de(fichier), fiche, communs, changes, changes)[1])


def cmd_fin(a, sortie):
    """`fin <fichier> <fiche> --note "<critère constaté>" [--resolu T]` : d'abord, un fichier changé hors de la ligne
    **Fichiers** arrête tout (`etrangers`) ; puis santé (`sante --base --si-base`), palier (dans le kit,
    `palier --lancer` s'il manque), coche, note `**Constaté**`, coût (`cout --session`), et le commit
    `<fiche> : <titre>` par chemins (`commiter`, jamais `git add -A`). Une ligne `FIN <étape> : …` par étape, puis
    `FIN <fiche> · COMMIT <sha>` ; au premier `GARDE:`, `FIN ARRÊT <étape>`, sort 1, rien d'écrit après."""
    fichier = os.path.abspath(a.fichier)
    code, racine = git_texte(["rev-parse", "--show-toplevel"], os.path.dirname(fichier))
    if code != 0:
        sortie.write("GARDE: fin — %s n'est pas dans un dépôt Git\nFIN ARRÊT dépôt\n" % a.fichier)
        return 1
    racine = racine.strip()

    def arret(nom, code_, texte):
        """Recopier la sortie de l'étape `nom` ; vrai si elle arrête la fin (code non nul ou `GARDE:`)."""
        sortie.write(texte)
        if code_ or "GARDE:" in texte:
            sortie.write("FIN ARRÊT %s\n" % nom)
            return True
        sortie.write("FIN %s : ok\n" % nom)
        return False

    hors = etrangers(fichier, a.fiche, racine)
    if hors is None or hors:
        raison = "git status illisible" if hors is None else "changés hors de sa ligne Fichiers : %s" % ", ".join(hors)
        sortie.write("GARDE: fin — %s ; ajoute-les à la ligne Fichiers de %s, ou laisse-les à leur séance\n"
                     "FIN ARRÊT fichiers\n" % (raison, a.fiche))
        return 1
    if arret("santé", *etape(["sante", "--base", "--si-base", "--racine", racine])):
        return 1
    if palier_manquant(fichier) and arret("palier", *etape(["palier", "--racine", racine, "--lancer"])):
        return 1
    cocher = ["cocher", fichier, a.fiche] + (["--resolu", a.resolu] if a.resolu else [])
    if arret("coche", *etape(cocher)):
        return 1
    noter_constate(fichier, a.fiche, a.note)
    sortie.write("FIN note : %s%s\n" % (CONSTATE, a.note))
    sortie.write(etape(["cout", fichier, "--session"])[1])
    code, texte = etape(["commiter", fichier, a.fiche])
    sortie.write(texte)
    sha = git_texte(["rev-parse", "--short", "HEAD"], racine)[1].strip()
    if code or "GARDE:" in texte or "HORS:" in texte:
        sortie.write("GARDE: fin — le commit n'est pas propre ; la fiche reste cochée : commite à la main après "
                     "correction\nFIN ARRÊT commit\n")
        return 1
    sortie.write("FIN %s · COMMIT %s\n" % (a.fiche, sha))
    return 0
