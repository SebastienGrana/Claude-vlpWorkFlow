"""Le rapport du matin : le carnet complété, la table des nuits, la page du matin (REF49 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import collections
import glob
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import time

import carnet

from noyau import etat
from noyau.commun import (lignes_de)
from noyau.fiches import (VLP_PY)
from noyau.carte import (trouver)
from noyau.page import (mesure, nom_du_projet)
from noyau.niveau import (dossier_artefacts)
from noyau.bac import (MUTANT_EXCLUS, PORT_APERCU, est_kit, lire_arg)
from noyau.nuit import (LECON_FORME, fichier_nuits, nuits_du_fichier, nuits_ecrire)
from noyau.matin import (de_cote, pointes_nuit, projet_du_matin)

import noyau.relecture   # `noyau.relecture.<nom>` : un test remplace ce nom là

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF49 — `py_du_statut` — se lisent ici seulement.
__all__ = [
    "mesure_session_kit", "completer_kit", "bilan_chantiers", "cout_du_bilan", "ecrire_table_nuits",
    "derniere_valeur", "chantiers_de_cote", "option_matin", "question_de_cote", "question_de_note", "rapport_matin",
    "cmd_matin_rapport", "cmd_nuits_lecon", "DELAI_MUTANT", "texte_mute", "kit_de", "copie_mutee", "vers_copie",
    "tuer_arbre", "jouer_suite", "effacer_copie", "verdict_juge", "attendu_au_milieu", "verdict_mutant",
    "jouer_mutant", "cmd_mutant", "entrees_launch", "cmd_apercu", "cmd_sante", "py_touches", "controles_rapides",
    "jouer_rapide", "ecrire_rapide", "controle_rapide", "cmd_rapide", "cmd_symboles", "libelle_de",
    "verifs_des_groupes", "cmd_parite",
]


# --- matin --rapport : le carnet complété, la table des nuits, la page du matin (chantier NUI, fiche NUI19) ------------
# Après la fusion : rien de commité, rien de fusionné, et rejoué, le carnet et le fichier des nuits ne changent plus.

def mesure_session_kit(session):
    """`(usd_kit, tours_kit, raison)` d'une session du carnet : `resoudre`, puis `mesurer` sur son transcript et sur chacun
    de ses `sous_agents`, `usd_exact` et `tours` sommés comme `parts_aux_commits` (un `usd_exact` None rend None), le
    prix arrondi une fois au centime. Transcript introuvable ou illisible, modèle hors `GRILLE` : `(None, None, raison)`
    — jamais 0."""
    from decimal import ROUND_HALF_UP, Decimal
    m = mesure()
    chemin, _ = m.resoudre(session)
    if chemin is None:
        return None, None, "transcription introuvable"
    usd, tours, inconnus = Decimal(0), 0, []
    for transcript in [chemin] + m.sous_agents(chemin):
        r, erreur = m.mesurer(transcript)
        if r is None:
            return None, None, "transcription illisible (%s)" % erreur
        tours += r["tours"]
        usd = None if usd is None or r["usd_exact"] is None else usd + r["usd_exact"]
        inconnus += r["inconnus"]
    if usd is None:
        return None, None, "modèle hors grille (%s)" % ", ".join(sorted(set(inconnus)))
    return float(usd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), tours, None


def completer_kit(chemin, sortie):
    """Donne `usd_kit` et `tours_kit` à chaque ligne de session du carnet `chemin` qui n'a pas `usd_kit`
    (`mesure_session_kit`) : mesurées d'abord, hors verrou, puis écrites d'un coup sous celui du carnet
    (`carnet.mettre_a_jour`). Une session non mesurée : `KIT ? <session> — <raison>` sur `sortie`, aucune clé `_kit`.
    Rend le nombre de lignes complétées."""
    mesures = {}
    for d in carnet.lire(chemin):
        s = d.get("session")
        if carnet.est_session(d) and d.get("usd_kit") is None and s not in mesures:
            mesures[s] = mesure_session_kit(s) if s else (None, None, "pas d'id de session au carnet")
            if mesures[s][0] is None:
                sortie.write("KIT ? %s — %s\n" % (s or "(sans id)", mesures[s][2]))

    def poser(d):
        m = mesures.get(d.get("session"))
        if carnet.est_session(d) and d.get("usd_kit") is None and m and m[0] is not None:
            return {"usd_kit": m[0], "tours_kit": m[1]}
        return None
    return carnet.mettre_a_jour(chemin, poser)


def bilan_chantiers(lignes):
    """Un dict par `(canal, chantier)` du carnet, dans l'ordre où ils y apparaissent : `jouees` (les fiches qu'une session
    `jouer` ou `relance` a prises), `acceptees` (celles qu'une session `relire` sans `refus_n` a prises, comme
    `taux_nuit`), `refusees` (celles qu'une `relire` à `refus_n` a prises : refusée puis acceptée compte aux deux),
    `issues` (`issue` : nombre de sessions), `relances`, `modeles` (`modeles_vus`, sans doublon), `retard`
    (`plugin_retard` de la dernière ligne qui en porte un), `usd` et `tours` (les sommes des `usd_kit` et `tours_kit`
    — jamais des `_cli`), `sans` (les sessions qui n'ont pas de `usd_kit`)."""
    bilans = {}
    for d in lignes:
        if not d.get("canal") or not d.get("chantier"):
            continue
        b = bilans.setdefault((d["canal"], d["chantier"]), {
            "canal": d["canal"], "chantier": d["chantier"], "jouees": set(), "acceptees": set(), "refusees": set(),
            "issues": collections.Counter(), "relances": 0, "modeles": [], "retard": None, "usd": 0.0, "tours": 0,
            "sans": 0})
        if d.get("plugin_retard") is not None:
            b["retard"] = d["plugin_retard"]
        if not carnet.est_session(d):
            continue
        role, fiche = d.get("role"), d.get("fiche")
        if role in ("jouer", "relance") and fiche:
            b["jouees"].add(fiche)
        if role == "relire" and fiche:
            b["refusees" if d.get("refus_n") else "acceptees"].add(fiche)
        b["relances"] += role == "relance"
        if d.get("issue"):
            b["issues"][d["issue"]] += 1
        b["modeles"] += [x for x in (d.get("modeles_vus") or []) if x not in b["modeles"]]
        if d.get("usd_kit") is None:
            b["sans"] += 1
        else:
            b["usd"] += d["usd_kit"]
            b["tours"] += d.get("tours_kit") or 0
    return list(bilans.values())


def cout_du_bilan(b, avec_unite=True):
    """La somme des `usd_kit` d'un bilan comme `4,50 $` ; `≥ 4,50 $` si des sessions n'en ont pas, `?` si aucune."""
    if b["sans"] and not b["usd"]:
        return "?"
    texte = ("%.2f" % b["usd"]).replace(".", ",")
    return ("≥ " if b["sans"] else "") + texte + (" $" if avec_unite else "")


def ecrire_table_nuits(projet, nuit, bilans):
    """Une ligne de table au fichier des nuits (`fichier_nuits(creer=True)`) par `(nuit, canal, chantier)` absente :
    `| <nuit> | <canal> | <chantier> | <jouées>/<acceptées>/<refusées> | <$> |`, le `$` étant `cout_du_bilan`. Une
    ligne déjà là n'est pas refaite. Rend `(chemin, nombre de lignes ajoutées)` ; `ValueError` : `fichier_nuits` ou
    `nuits_ecrire` refusent."""
    chemin = fichier_nuits(projet, creer=True)
    assert chemin
    rangees, _ = nuits_du_fichier(lignes_de(chemin))
    ajoutees = 0
    for b in bilans:
        deja = any(r[:3] == [nuit, b["canal"], b["chantier"]] for r in rangees)
        if deja:
            continue
        ligne = "| %s | %s | %s | %d/%d/%d | %s |" % (nuit, b["canal"], b["chantier"], len(b["jouees"]),
                                                      len(b["acceptees"]), len(b["refusees"]),
                                                      cout_du_bilan(b, avec_unite=False))
        ajoutees += nuits_ecrire(chemin, ligne)
    return chemin, ajoutees


def derniere_valeur(lignes, cle):
    """La dernière valeur non vide de `cle` parmi `lignes`, en texte, ou None."""
    return next((str(d[cle]) for d in reversed(lignes) if d.get(cle)), None)


def chantiers_de_cote(projet, date, lignes):
    """`([{canal, chantier, branche, raison, cause, reecriture, dependants, ecart}], [ÉCART])` : les chantiers mis de côté
    selon Git — la branche `nuit/<date>-<canal>-<code>` qui n'est pas dans `HEAD` et dont `de_cote` dit qu'elle garde un
    chantier ouvert — et selon le carnet — une garde `mis-de-cote:<raison>`, ses `cause` et `reecriture`, les chantiers
    dont une garde `saute:<code>` dit qu'ils en dépendaient (NUI7). Les deux se croisent : l'un le dit de côté, pas
    l'autre, c'est un `ÉCART` — dit, jamais tranché."""
    pointes, _ = pointes_nuit(projet, date)
    prefixe = "nuit/%s-" % date
    git_cote = {}
    for branche, _ in pointes or []:
        canal, _, code = branche[len(prefixe):].partition("-")
        if noyau.relecture.git_texte(["merge-base", "--is-ancestor", branche, "HEAD"], projet)[0] != 0 and de_cote(projet, branche):
            git_cote[(canal, code)] = branche
    raisons = {}
    for d in lignes:
        garde = str(d.get("garde") or "")
        if garde.startswith("mis-de-cote:") and d.get("chantier"):
            raisons[(d.get("canal"), d["chantier"])] = garde[len("mis-de-cote:"):]
    cotes, ecarts = [], []
    for cle in list(raisons) + [k for k in git_cote if k not in raisons]:
        canal, code = cle
        propres = [d for d in lignes if d.get("canal") == canal and d.get("chantier") == code]
        ecart = None
        if cle not in git_cote:
            ecart = "le carnet le met de côté, Git non (branche absente, déjà dans main, ou chantier fermé sur elle)"
        elif cle not in raisons:
            ecart = "Git le met de côté, le carnet n'a aucune ligne mis-de-cote"
        if ecart:
            ecarts.append("ÉCART %s-%s — %s" % (canal, code, ecart))
        cotes.append({"canal": canal, "chantier": code, "branche": "%s%s-%s" % (prefixe, canal, code),
                      "raison": raisons.get(cle), "cause": derniere_valeur(propres, "cause"),
                      "reecriture": derniere_valeur(propres, "reecriture"),
                      "dependants": [x for x in dict.fromkeys(
                          d["chantier"] for d in lignes
                          if d.get("chantier") and str(d.get("garde") or "") == "saute:%s" % code)],
                      "ecart": ecart})
    return cotes, ecarts


def option_matin(valeur, libelle, effet):
    return {"valeur": valeur, "libelle": libelle, "effet": effet, "recommande": False}


def question_de_cote(c):
    """La carte d'un chantier mis de côté : ce que le carnet et Git en disent, et les trois réponses du socle."""
    puces = ["Branche : `%s`" % c["branche"], "Raison au carnet : %s" % (c["raison"] or "aucune")]
    if c["cause"]:
        puces.append("Cause du dernier refus : %s" % c["cause"])
    if c["reecriture"]:
        puces.append("Réécriture demandée : %s" % c["reecriture"])
    puces.append("Chantiers sautés à cause de lui : %s" % (", ".join(c["dependants"]) or "aucun"))
    if c["ecart"]:
        puces.append("**ÉCART** : %s" % c["ecart"])
    return {"titre": "Mis de côté : %s (canal %s)" % (c["chantier"], c["canal"]), "puces": puces, "options": [
        option_matin("reprendre", "Reprendre à la main", "Tu reprends la branche `%s` toi-même ; je ne touche à rien "
                     "d'autre." % c["branche"]),
        option_matin("abandonner", "Abandonner", "Le travail de la branche est perdu : je te donne `git branch -D %s`, "
                     "je ne la lance jamais." % c["branche"]),
        option_matin("rejouer", "Rejouer une nuit", "Je te donne aussi `git branch -D %s` : la nuit suivante repart de "
                     "`main`. La ligne de la TODO reste, le tri du soir la reprend." % c["branche"])]}


def question_de_note(canal, texte, sorte):
    """La carte d'une note du carnet selon sa `sorte` : un reste (trois réponses, le premier oui de
    `methode-chantier.md`), ou une case du menu de fin de `cloture.md` (faire ou laisser)."""
    puces = ["Note du canal %s : %s" % (canal or "?", texte)]
    if sorte == "reste":
        return {"titre": "Reste à verser dans la TODO ?", "puces": puces + [
            "La TODO ne grossit pas sans deux oui : celui-ci est le premier, la ligne écrite sera le second."], "options": [
            option_matin("verser", "Verser", "Je t'écris la ligne et te la montre : elle ne part qu'après ton second oui."),
            option_matin("fondre", "Fondre dans une entrée existante", "Tu me nommes laquelle ; rien ne grossit."),
            option_matin("abandonner", "Abandonner", "Rien n'est écrit : abandonner est une réponse normale.")]}
    titre, faire = (("Case 3 du menu de fin : essaimer", "Je lance `niveau` sur les autres projets équipés, comme "
                     "`cloture.md` le dit.") if sorte == "case3" else
                    ("Case 4 du menu de fin : la dette repérée", "Petite : une tâche et un commit à elle. Plus grosse : "
                     "présentée comme un chantier (`cloture.md`)."))
    return {"titre": titre, "puces": puces, "options": [
        option_matin("faire", "Faire", faire),
        option_matin("laisser", "Laisser", "Rien n'est fait ; la note reste au carnet.")]}


def rapport_matin(projet, date, bilans, cotes, lignes, kit_sans):
    """Le JSON de `chef page --questions` du matin : une ligne `fait` par chantier du carnet (issues, relances, modèles
    vus, `plugin_retard`, coût `_kit` — jamais `_cli`), une carte par chantier mis de côté, une par note selon sa `sorte`,
    et `NOTE SANS SORTE` en alerte pour les autres. `kit_sans` : les lignes `KIT ?`, en puces."""
    notes = [d for d in lignes if carnet.est_note_matin(d)]
    fait, choix, mal = [], [question_de_cote(c) for c in cotes], []
    for b in bilans:
        issues = ", ".join("%s ×%d" % (k, n) for k, n in b["issues"].items()) or "aucune session"
        livre = " · ".join(x for x in (
            "issues : %s" % issues, "relances : %d" % b["relances"],
            "modèles vus : %s" % ", ".join(b["modeles"]) if b["modeles"] else None,
            "plugin en retard : %s commit(s)" % b["retard"] if b["retard"] else None) if x)
        fait.append({"ref": b["canal"], "code": b["chantier"], "livre": livre,
                     "titre": "%d jouée(s) · %d acceptée(s) · %d refusée(s)" % (len(b["jouees"]), len(b["acceptees"]),
                                                                              len(b["refusees"])),
                     "cout": "%s · %d tours" % (cout_du_bilan(b), b["tours"])})
    for d in notes:
        if d.get("sorte") in carnet.SORTES:
            choix.append(question_de_note(d.get("canal"), str(d["note"]), d["sorte"]))
        else:
            mal.append({"genre": "alerte", "titre": "NOTE SANS SORTE", "texte":
                        "%s (canal %s) — le matin ne sait pas quoi en faire : à classer à la main." % (
                            d["note"], d.get("canal") or "?")})
    rapport = {"projet": nom_du_projet(projet), "sujet": "matin", "titre": "Le matin du %s" % date, "date": date,
               "puces": ["%d chantier(s) au carnet · %d mis de côté · %d note(s) pour le matin"
                         % (len(bilans), len(cotes), len(notes))] + kit_sans}
    for cle, valeur in (("fait", fait), ("choix", choix), ("mal", mal)):
        if valeur:
            rapport[cle] = valeur
    return rapport


def cmd_matin_rapport(a, sortie):
    """`matin <projet> <date> --rapport <json>` : sans fusion ni commit, rejouable. Complète le carnet de la nuit
    (`completer_kit`), range une ligne par chantier au fichier des nuits (`ecrire_table_nuits`), puis écrit le JSON de
    `chef page --questions` (`rapport_matin`). Mêmes gardes que `matin` : équipé, date, racine du dépôt ; carnet absent
    ou vide, ou fichier des nuits illisible : `GARDE:`, sort 1."""
    projet = projet_du_matin(a, sortie)
    if projet is None:
        return 1
    chemin = carnet.du_jour(projet, a.date)
    if not chemin or not carnet.lire(chemin):
        sortie.write("GARDE: carnet de la nuit %s absent ou vide — pas de rapport\n" % a.date)
        return 1
    manques = io.StringIO()
    try:
        completer_kit(chemin, manques)
    except ValueError as e:
        sortie.write("GARDE: carnet %s — %s\n" % (chemin, e))
        return 1
    sortie.write(manques.getvalue())
    lignes = carnet.lire(chemin)
    bilans = bilan_chantiers(lignes)
    try:
        nuits, ajoutees = ecrire_table_nuits(projet, a.date, bilans)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("NUITS %s · %d ligne(s) ajoutée(s)\n" % (os.path.relpath(nuits, projet).replace("\\", "/"), ajoutees))
    cotes, ecarts = chantiers_de_cote(projet, a.date, lignes)
    for e in ecarts:
        sortie.write(e + "\n")
    rapport = rapport_matin(projet, a.date, bilans, cotes, lignes, manques.getvalue().splitlines())
    for d in lignes:
        if carnet.est_note_matin(d) and d.get("sorte") not in carnet.SORTES:
            sortie.write("NOTE SANS SORTE %s — %s\n" % (d.get("canal") or "?", d["note"]))
    try:
        with open(a.rapport, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rapport, f, ensure_ascii=False, indent=1)
            f.write("\n")
    except OSError as e:
        sortie.write("GARDE: %s — écriture impossible : %s\n" % (a.rapport, e))
        return 1
    sortie.write("RAPPORT %s · %d chantier(s) · %d mis de côté · %d carte(s)\n" % (
        a.rapport, len(bilans), len(cotes), len(rapport.get("choix", []))))
    return 0


def cmd_nuits_lecon(ligne, projet, sortie):
    """`nuits lecon "<ligne>"` : une leçon sous `## Leçons` du fichier des nuits (`fichier_nuits(creer=True)`). Hors de la
    forme de `LECON_FORME`, ou fichier illisible : `GARDE:`, sort 1, rien d'écrit. Déjà là : `LEÇON déjà là`."""
    try:
        if not LECON_FORME.match(ligne):
            raise ValueError("leçon hors forme : %s" % ligne)
        chemin = fichier_nuits(os.path.abspath(projet), creer=True)
        assert chemin
        ajoutee = nuits_ecrire(chemin, ligne)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("LEÇON %s · %s\n" % (os.path.relpath(chemin, projet).replace("\\", "/"), "ajoutée" if ajoutee else "déjà là"))
    return 0


DELAI_MUTANT = 1800     # secondes : passé ce délai, la suite d'un mutant est tuée et dite PLANTÉ


def texte_mute(fichier, avant, apres):
    """Lire `fichier` et rendre (ses octets, son texte où `avant` devient `apres`) ; les `\\n` des deux suivent
    la fin de ligne du fichier, et `avant` doit y être une fois exactement — sinon `ValueError`."""
    with open(fichier, "rb") as f:
        octets = f.read()
    texte = octets.decode("utf-8")
    nl = "\r\n" if "\r\n" in texte else "\n"
    avant, apres = (x.replace("\r\n", "\n").replace("\n", nl) for x in (avant, apres))
    n = texte.count(avant) if avant else 0
    if n != 1:
        raise ValueError("« avant » trouvé %d fois dans %s — il en faut exactement 1, rien écrit" % (n, fichier))
    return octets, texte.replace(avant, apres)


def kit_de(fichier):
    """Rendre la racine du premier kit (`est_kit`) en remontant depuis le dossier de `fichier`, `None` hors de tout
    kit : un worktree du kit est son propre kit, même rangé sous le dépôt principal (MUW1)."""
    d = os.path.dirname(os.path.abspath(fichier))
    while not est_kit(d):
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)
    return d


def copie_mutee(fichier, mute, dossier):
    """Copier sous `dossier` le kit qui contient `fichier` (`kit_de`) — ou, hors de tout kit, `KIT` s'il le contient,
    sinon le dossier de `fichier` —, sans `MUTANT_EXCLUS`, puis y écrire `mute` à la place de `fichier` ; rendre
    (la racine copiée, sa copie). Le vrai fichier n'est jamais écrit."""
    import shutil
    fichier = os.path.abspath(fichier)
    try:
        dans_kit = os.path.commonpath([os.path.normcase(etat.KIT), os.path.normcase(fichier)]) == os.path.normcase(etat.KIT)
    except ValueError:      # deux lecteurs différents
        dans_kit = False
    racine = kit_de(fichier) or (etat.KIT if dans_kit else os.path.dirname(fichier))
    copie = os.path.join(dossier, "kit")

    def exclus(r, noms):
        """Rendre les noms de `r` que la copie laisse de côté."""
        rel = os.path.relpath(r, racine).replace(os.sep, "/")
        return [n for n in noms if n in MUTANT_EXCLUS or (rel == "evals" and n == "results")]

    shutil.copytree(racine, copie, ignore=exclus)
    with open(os.path.join(copie, os.path.relpath(fichier, racine)), "wb") as f:
        f.write(mute.encode("utf-8"))
    return racine, copie


def vers_copie(commande, racine, copie):
    """Rendre `commande` (chaîne ou liste) où chaque chemin sous `racine`, en barres obliques ou inverses, pointe
    sous `copie` : une commande déjà écrite pour le vrai kit joue la copie."""
    if not isinstance(commande, str):
        return [vers_copie(x, racine, copie) for x in commande]
    for r, c in {(racine, copie), (racine.replace("\\", "/"), copie.replace("\\", "/"))}:
        commande = re.sub(re.escape(r) + r"(?![^\\/\s\"'])", lambda _m, c=c: c, commande,
                          flags=re.I if os.name == "nt" else 0)
    return commande


def tuer_arbre(p):
    """Tuer le processus `p` et ses descendants : `taskkill /T` sous Windows, son groupe de session ailleurs."""
    import subprocess
    if p.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    else:
        import signal
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def jouer_suite(commande, dossier, attendu):
    """Jouer `commande` dans `dossier` avec `VLP_TOUS_ECARTS=1`, sa sortie lue ligne à ligne ; avec `attendu`, tuer
    l'arbre de processus dès l'`ÉCART:` dont le libellé commence par lui. Rendre (lignes, code de sortie, attrapé) ;
    passé `DELAI_MUTANT`, l'arbre est tué et une ligne `DÉLAI:` le dit."""
    import subprocess
    import threading
    env = dict(os.environ, VLP_TOUS_ECARTS="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONUNBUFFERED="1")
    p = subprocess.Popen(commande, shell=isinstance(commande, str), cwd=dossier, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, encoding="utf-8", errors="replace",
                         start_new_session=sys.platform != "win32")
    lignes, attrape = [], False

    def expirer():
        """Tuer la suite trop longue, et le noter."""
        lignes.append("DÉLAI: %d s dépassé, suite tuée" % DELAI_MUTANT)
        tuer_arbre(p)

    minuteur = threading.Timer(DELAI_MUTANT, expirer)
    minuteur.start()
    try:
        for ligne in p.stdout or ():
            lignes.append(ligne.rstrip("\n"))
            if attendu and ligne.startswith("ÉCART:") and ligne[len("ÉCART:"):].strip().startswith(attendu):
                attrape = True
                tuer_arbre(p)
                break
    finally:
        minuteur.cancel()
    return lignes, p.wait(), attrape


def effacer_copie(dossier):
    """Effacer `dossier`, en réessayant 2 s : un processus tué peut le tenir encore un instant ; rendre `True` s'il
    a disparu."""
    import shutil
    for _ in range(10):
        shutil.rmtree(dossier, ignore_errors=True)
        if not os.path.exists(dossier):
            return True
        time.sleep(0.2)
    return False


def verdict_juge(lignes, code, attendu):
    """Rendre (texte, code de sortie) d'un juge hors kit (`--test`, chantier ISO) — il n'imprime ni `ÉCART:`, ni
    `OK` ou `FIN:` en dernière ligne : son code de sortie tranche. Un `DÉLAI:`, une erreur Python ou une commande
    introuvable (126, 127, 9009) → `PLANTÉ` ; 0 → `VIVANT` ; sinon `ATTRAPÉ`, et avec `attendu`, la première
    ligne qui le contient — aucune, `VIVANT pour`."""
    vues = [l.strip() for l in lignes if l.strip()]
    if code in (126, 127, 9009) or any(l.startswith(("DÉLAI:", "Traceback (most recent call last)"))
                                       or re.match(r"\w+(Error|Exception):", l) for l in vues):
        return "MUTANT PLANTÉ · juge hors kit sorti %d — %s\n" % (code, " / ".join(vues[-3:])), 1
    if code == 0:
        return "MUTANT VIVANT%s · juge hors kit sorti 0\n" % (" pour %s" % attendu if attendu else ""), 1
    ligne = next((l for l in vues if attendu in l), None) if attendu else (vues[-1] if vues else "")
    if ligne is None:
        return "MUTANT VIVANT pour %s · juge hors kit sorti %d sans le dire — %s\n" % (
            attendu, code, " / ".join(vues[-3:])), 1
    return "MUTANT ATTRAPÉ · juge hors kit sorti %d — « %s »\n" % (code, ligne), 0


def attendu_au_milieu(ecarts, attendu):
    """Rendre une ligne `ATTENDU AU MILIEU` par `ÉCART:` qui contient `attendu` ailleurs qu'en tête de son libellé
    (`jouer_suite` ne reconnaît que le début, défaut `E8` vu à la clôture d'ENA), avec le début à recopier."""
    texte = ""
    for e in ecarts:
        libelle = e[len("ÉCART:"):].strip()
        i = libelle.find(attendu)
        if i > 0:
            texte += "ATTENDU AU MILIEU · « %s » est dans « %s » : --attendu \"%s\"\n" % (
                attendu, libelle, libelle[:i + len(attendu)])
    return texte


def verdict_mutant(lignes, code, attrape, attendu, juge=False):
    """Rendre (texte, code de sortie) : les `ÉCART:` vus, puis `MUTANT ATTRAPÉ`, `VIVANT` ou `PLANTÉ`. Une suite
    finie sort 0 ou dit `OK` ou `FIN:` en dernière ligne ; arrêtée avant, elle est `PLANTÉ`, écarts vus ou non. Un
    `juge` hors kit (`--test`) qui ne parle pas ainsi — ni `ÉCART:`, ni cette dernière ligne — est jugé à son code
    (`verdict_juge`). Un `attendu` non attrapé mais lu au milieu d'un écart se signale (`attendu_au_milieu`)."""
    ecarts = [l for l in lignes if l.startswith("ÉCART:")]
    texte = "".join(l + "\n" for l in ecarts)
    fin = next((l.strip() for l in reversed(lignes) if l.strip()), "")
    if juge and not (attrape or ecarts or fin == "OK" or fin.startswith("FIN:")):
        return verdict_juge(lignes, code, attendu)
    if attrape:
        return texte + "MUTANT ATTRAPÉ %d écart(s) · arrêté sur « %s »\n" % (len(ecarts), attendu), 0
    milieu = attendu_au_milieu(ecarts, attendu) if attendu else ""
    if not (code == 0 or fin == "OK" or fin.startswith("FIN:")):
        dernieres = [l.strip() for l in lignes if l.strip()][-3:]
        return texte + "MUTANT PLANTÉ · tests sortis %d sans finir, après %d écart(s) — %s\n" % (
            code, len(ecarts), " / ".join(dernieres)) + milieu, 1
    if attendu:
        return texte + "MUTANT VIVANT pour %s\n" % attendu + milieu, 1
    if ecarts:
        return texte + "MUTANT ATTRAPÉ %d écart(s)\n" % len(ecarts), 0
    return texte + "MUTANT VIVANT\n", 1


def jouer_mutant(commande, copie, attendu, vise):
    """Jouer les tests `commande` dans `copie` et rendre (texte, code de sortie) de leur verdict (`verdict_mutant`).
    Avec `vise` — pas de `--test` — et `attendu` (VIT21), d'abord les seuls groupes de `test-vlp.py` qui portent
    `attendu` (`--seul`) : l'écart attendu tombé là, une ligne `VISÉ` le dit ; sinon — aucun groupe, ou pas cet
    écart —, la suite entière tranche, et une ligne `SUITE ENTIÈRE` le dit. Un ATTRAPÉ ne vient que de l'écart
    attendu, un VIVANT que de la suite entière."""
    tete = ""
    if vise and attendu:
        lignes, code, attrape = jouer_suite(commande + ["--seul", attendu], copie, attendu)
        if attrape:
            texte, code = verdict_mutant(lignes, code, attrape, attendu)
            return "VISÉ --seul « %s »\n" % attendu + texte, code
        aucun = any(l.startswith("GARDE: aucun groupe") for l in lignes)
        tete = "SUITE ENTIÈRE · %s\n" % (("aucun groupe ne porte « %s »" if aucun
                                          else "« %s » n'est pas tombé dans ses groupes") % attendu)
    texte, code = verdict_mutant(*jouer_suite(commande, copie, attendu), attendu, juge=not vise)
    return tete + texte, code


def cmd_mutant(a, sortie):
    """Casser `a.cible` exprès (`a.avant` → `a.apres`, une seule occurrence) dans une copie du kit, y jouer les
    tests, et dire si le mutant est attrapé — avec `a.attendu`, arrêtés dès cet écart (chantiers MUT, VIT2), et sans
    `a.test`, d'abord sur ses seuls groupes (`jouer_mutant`, VIT21). Le vrai fichier n'est jamais écrit : `RENDU`
    imprime son empreinte, la même qu'avant."""
    import subprocess
    try:
        octets, mute = texte_mute(a.cible, lire_arg(a.avant), lire_arg(a.apres))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    empreinte = hashlib.sha1(octets).hexdigest()[:12]
    dossier = tempfile.mkdtemp(prefix="vlp-mutant-")
    try:
        racine, copie = copie_mutee(a.cible, mute, dossier)
        suite = os.path.join(racine if est_kit(racine) else etat.KIT, "scripts", "test-vlp.py")
        commande = vers_copie(a.test or [sys.executable, suite], racine, copie)
        texte, code = jouer_mutant(commande, copie, a.attendu, vise=not a.test)
        if not a.test:
            texte += "TESTS %s\n" % os.path.dirname(os.path.dirname(suite))
    except (OSError, subprocess.SubprocessError) as e:
        texte, code = "GARDE: les tests ne se lancent pas : %s\n" % e, 1
    finally:
        restee = not effacer_copie(dossier)
    sortie.write(texte + ("COPIE restée : %s\n" % dossier if restee else ""))
    with open(a.cible, "rb") as f:
        rendu = hashlib.sha1(f.read()).hexdigest()[:12]
    if rendu != empreinte:
        sortie.write("GARDE: %s a bougé pendant le mutant : %s avant, %s après\n" % (a.cible, empreinte, rendu))
        return 1
    sortie.write("RENDU %s\n" % rendu)
    return code


def entrees_launch(texte):
    """(index après le `[`, index du `]`, [(début, fin, entrée)]) du tableau `configurations` de
    `launch.json`, lu sur le texte : on y greffe une entrée sans réécrire les voisines. `None` :
    illisible, ou pas de tableau."""
    try:
        attendu = json.loads(texte)["configurations"]
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(attendu, list):
        return None
    lecteur = json.JSONDecoder()

    def apres_blancs(pos):
        while pos < len(texte) and texte[pos].isspace():
            pos += 1
        return pos

    for m in re.finditer(r'"configurations"\s*:\s*\[', texte):
        pos, spans = m.end(), []
        try:
            while True:
                pos = apres_blancs(pos)
                if texte[pos] == "]":
                    break
                entree, fin = lecteur.raw_decode(texte, pos)
                spans.append((pos, fin, entree))
                pos = apres_blancs(fin)
                if texte[pos] == ",":
                    pos += 1
        except (ValueError, IndexError):
            continue
        if [e for _, _, e in spans] == attendu:
            return m.end(), pos, spans
    return None


def cmd_apercu(projet, sortie, port=None):
    """Greffe `apercu-<dossier>` dans `<projet>/.claude/launch.json` (chantier LOC)."""
    racine = trouver(projet)
    if racine is None:
        sortie.write("GARDE: pas de projet équipé ici : %s\n" % projet)
        return 1
    nom = "apercu-" + os.path.basename(racine)
    chemin = os.path.join(racine, ".claude", "launch.json")
    texte = None
    if os.path.isfile(chemin):
        with open(chemin, encoding="utf-8", newline="") as f:
            texte = f.read()
    lu = entrees_launch(texte) if texte is not None else (0, 0, [])
    if lu is None:
        sortie.write("GARDE: %s illisible, ou sans tableau `configurations` : rien d'écrit\n" % chemin)
        return 1
    ouvre, ferme, spans = lu
    ici = [sp for sp in spans if isinstance(sp[2], dict) and sp[2].get("name") == nom]
    if len(ici) > 1:
        sortie.write("GARDE: %d entrées nommées %s dans %s : rien d'écrit\n" % (len(ici), nom, chemin))
        return 1
    prises = {sp[2].get("port") for sp in spans if isinstance(sp[2], dict) and sp not in ici}
    if port is None and ici and isinstance(ici[0][2].get("port"), int):
        port = ici[0][2]["port"]
    if port is None:
        port = next(n for n in range(PORT_APERCU, PORT_APERCU + 1000) if n not in prises)
    artefacts = dossier_artefacts(racine).replace("\\", "/")
    entree = {"name": nom, "runtimeExecutable": "py" if os.name == "nt" else "python3",
              "runtimeArgs": [VLP_PY.replace("\\", "/"), "servir", artefacts, str(port)],
              "port": port}
    eol = "\r\n" if texte and "\r\n" in texte else "\n"
    corps = json.dumps(entree, indent=2, ensure_ascii=False).replace("\n", eol + "    ")
    if texte is None:
        neuf = json.dumps({"version": "0.0.1", "configurations": [entree]}, indent=2, ensure_ascii=False) + "\n"
    elif ici:
        neuf = texte[:ici[0][0]] + corps + texte[ici[0][1]:]
    elif spans:
        neuf = texte[:spans[-1][1]] + "," + eol + "    " + corps + texte[spans[-1][1]:]
    else:
        neuf = texte[:ouvre] + eol + "    " + corps + eol + "  " + texte[ferme:]
    if neuf != texte:
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin + ".tmp", "w", encoding="utf-8", newline="") as f:
            f.write(neuf)
        os.replace(chemin + ".tmp", chemin)
    sortie.write("APERCU %s %s · port %d · %s\n"
                 % ("déjà" if neuf == texte else "remplacé" if ici else "écrit", nom, port, chemin))
    code, _ = noyau.relecture.git_texte(["check-ignore", "-q", ".claude/launch.json"], racine)
    if code == 1:
        sortie.write("GARDE: .claude/launch.json n'est pas couvert par .gitignore : il porte des chemins "
                     "de machine, et partirait dans le dépôt\n")
    return 0


def cmd_sante(a, sortie):
    """La santé du code (`sante.py`, VIT15) — chargé ici seulement : son `import ast` coûterait à chaque hook."""
    import sante
    return sante.principal(a, sortie, etat.KIT)


def py_touches(racine):
    """Rendre les `.py` ajoutés, modifiés ou neufs du dépôt de `racine` depuis `HEAD` — index et arbre de travail, lus
    par `git status` —, en chemins absolus triés ; un fichier effacé n'y est pas. Git muet : `None`."""
    code, haut = noyau.relecture.git_texte(["rev-parse", "--show-toplevel"], racine)
    if code != 0:
        return None
    code, texte = noyau.relecture.git_texte(["status", "--porcelain=v1", "-z", "--untracked-files=all"], racine)
    if code != 0:
        return None
    chemins = (os.path.join(haut.strip(), r) for r in py_du_statut(texte))
    return sorted({os.path.normpath(c) for c in chemins if os.path.isfile(c)})


def py_du_statut(texte):
    """Les `.py` d'une sortie de `git status --porcelain=v1 -z`, relatifs à la racine du dépôt ; l'ancien nom d'un
    renommage ou d'une copie sauté. Ne lance rien (REF49)."""
    champs, rendus = iter(texte.split("\0")), []
    for entree in champs:
        if entree[:1] in ("R", "C"):
            next(champs, None)  # le nom d'origine suit un renommage ou une copie
        if entree.endswith(".py"):
            rendus.append(entree[3:])
    return rendus


def controles_rapides(racine, motif, pyright):
    """Rendre les trois contrôles de `rapide` (VIT23), en (nom, commande, raison d'un saut) : les groupes de
    `test-vlp.py` qui portent `motif` (`--seul`), pyright sur les `.py` touchés — `pyright` : sa commande, `None`
    s'il manque —, et `sante --cliquet`. Un contrôle sauté a une commande `None` et dit sa raison."""
    scripts = os.path.join(racine, "scripts")
    fichiers = py_touches(racine)
    if fichiers is None:
        typage = ("pyright", None, "Git ne dit pas les fichiers touchés")
    elif not fichiers:
        typage = ("pyright", None, "aucun .py touché")
    elif not pyright:
        typage = ("pyright", None, "pyright introuvable")
    else:
        typage = ("pyright %d fichier(s)" % len(fichiers), list(pyright) + fichiers, None)
    return [("groupes « %s »" % motif, [sys.executable, os.path.join(scripts, "test-vlp.py"), "--seul", motif], None),
            typage,
            ("cliquet", [sys.executable, os.path.join(scripts, "vlp.py"), "sante", "--cliquet", "--racine", racine],
             None)]


def jouer_rapide(commande, racine):
    """Jouer `commande` dans `racine` ; rendre (code de sortie, lignes de sa sortie, durée en secondes) — `None` et la
    raison si elle ne se lance pas."""
    import subprocess
    debut = time.perf_counter()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    try:
        r = subprocess.run(commande, cwd=racine, env=env, capture_output=True, encoding="utf-8", errors="replace")
    except OSError as e:
        return None, ["ne se lance pas : %s" % e], time.perf_counter() - debut
    return r.returncode, (r.stdout + r.stderr).splitlines(), time.perf_counter() - debut


def ecrire_rapide(nom, saut, jeu, sortie):
    """Écrire la ligne `RAPIDE` d'un contrôle : sauté, avec sa raison ; vert, avec sa dernière ligne utile ; rouge,
    avec ses lignes, 30 au plus. Rendre `True` s'il est rouge."""
    if jeu is None:
        sortie.write("RAPIDE %s : sauté · %s\n" % (nom, saut))
        return False
    code, lignes, duree = jeu
    pleines = [l.rstrip() for l in lignes if l.strip()]
    if code == 1 and any(l.startswith("GARDE: aucun groupe ne porte") for l in pleines):
        sortie.write("RAPIDE %s : sauté · %.1f s · aucun groupe ne porte ce motif\n" % (nom, duree))
        return False
    if code == 0:
        utiles = [l.strip() for l in pleines if l.strip() != "OK"] or [l.strip() for l in pleines] or [""]
        sortie.write("RAPIDE %s : vert · %.1f s · %s\n" % (nom, duree, utiles[-1]))
        return False
    sortie.write("RAPIDE %s : rouge · %.1f s · code %s\n" % (nom, duree, code))
    sortie.write("".join("  %s\n" % l for l in pleines[:30]))
    if len(pleines) > 30:
        sortie.write("  … %d ligne(s) de plus\n" % (len(pleines) - 30))
    return True


def controle_rapide(racine, motif, pyright, sortie):
    """Jouer en parallèle les trois contrôles de `rapide` (`controles_rapides`), écrire leurs lignes `RAPIDE` dans
    l'ordre, puis le verdict et sa durée ; rendre 0 si aucun n'est rouge, sinon 1."""
    from concurrent.futures import ThreadPoolExecutor
    debut = time.perf_counter()
    controles = controles_rapides(racine, motif, pyright)
    with ThreadPoolExecutor(max_workers=len(controles)) as pool:
        jeux = [pool.submit(jouer_rapide, c, racine) if c else None for _, c, _ in controles]
        rouges = [ecrire_rapide(nom, saut, jeu.result() if jeu else None, sortie)
                  for (nom, _, saut), jeu in zip(controles, jeux)]
    rouge = any(rouges)
    sortie.write("RAPIDE %s · %.1f s — %s\n" % ("ROUGE" if rouge else "VERT", time.perf_counter() - debut,
                                                 "corrige avant de lancer la suite entière" if rouge
                                                 else "la suite entière reste à jouer : cocher l'exige"))
    return 1 if rouge else 0


def cmd_rapide(a, sortie):
    """Le contrôle rapide d'une fiche du kit, avant la suite entière (VIT23) : ses groupes de `test-vlp.py`, pyright
    sur les `.py` touchés et le cliquet, en parallèle (`controle_rapide`). Il ne remplace pas la suite entière, que
    `cocher` exige toujours (VIT11). Hors du kit — pas de `scripts/test-vlp.py` sous la racine — : `GARDE:`."""
    import shutil
    racine = os.path.abspath(a.racine or ".")
    if not os.path.isfile(os.path.join(racine, "scripts", "test-vlp.py")):
        sortie.write("GARDE: %s n'est pas le kit : pas de scripts/test-vlp.py\n" % racine)
        return 1
    pyright = shutil.which("pyright")
    return controle_rapide(racine, a.motif, [pyright] if pyright else None, sortie)


def cmd_symboles(a, sortie):
    """Imprimer `nom début-fin` pour chaque fonction ou classe de premier niveau de `a.fichier`, lu par `ast` sans
    l'importer — ou pour les seuls `a.noms`, `ABSENT <nom>` pour ceux qui n'y sont pas (sort 1) : une fiche cite un
    nom, ce script rend sa ligne du jour (VIT9). `ast` plutôt que `pyclbr`, bâti dessus : `pyclbr` garde un cache par
    nom de module, faux d'un fichier à l'autre dans un même processus. Fichier absent, ou qui ne se lit pas en
    Python (un `.as`, `AMD1`) : `GARDE:`, sort 1 — jamais un traceback (SYM)."""
    import ast
    if not os.path.isfile(a.fichier):
        sortie.write("GARDE: %s n'est pas un fichier\n" % a.fichier)
        return 1
    try:
        with open(a.fichier, encoding="utf-8") as f:
            corps = ast.parse(f.read()).body
    except (SyntaxError, UnicodeDecodeError, ValueError) as e:
        sortie.write("GARDE: %s ne se lit pas en Python (symboles ne lit que le Python ; grep -n ailleurs) : %s\n"
                     % (a.fichier, str(e).splitlines()[0] if str(e) else type(e).__name__))
        return 1
    trouves = {n.name: n for n in corps if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    for n in a.noms or list(trouves):
        o = trouves.get(n)
        sortie.write("%s %d-%d\n" % (n, o.lineno, o.end_lineno or o.lineno) if o else "ABSENT %s\n" % n)
    return 1 if any(n not in trouves for n in a.noms) else 0


def libelle_de(noeud):
    """Le libellé d'un `verifier(<libellé>, …)` ou d'un `assert …, <libellé>` (REF5) : la chaîne telle quelle, le
    gabarit d'un `"…" % x`, la gauche d'un `+` (`libellé + diagnostic`, REF43), un f-string ses morceaux fixes ; sinon None."""
    import ast
    if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
        return noeud.value
    if isinstance(noeud, ast.BinOp) and isinstance(noeud.op, (ast.Mod, ast.Add)):
        return libelle_de(noeud.left)
    if isinstance(noeud, ast.JoinedStr):
        return "".join(str(v.value) if isinstance(v, ast.Constant) else "{}" for v in noeud.values)
    return None


def verifs_des_groupes(arbre):
    """`[(groupe, [libellés])]` pour chaque `groupe(<fonction>)` de `test-vlp.py`, dans l'ordre : les `verifier` de
    la fonction, et ceux des fonctions du module qu'elle nomme, de proche en proche (une aide compte au groupe qui
    l'appelle ; un autre groupe qu'elle nomme, non : REF43)."""
    import ast
    fonctions = {n.name: n for n in arbre.body if isinstance(n, ast.FunctionDef)}

    def propres(f):
        """Les libellés des `verifier` écrits dans `f` même."""
        return [libelle_de(c.args[0]) or "" for c in ast.walk(f) if isinstance(c, ast.Call)
                and isinstance(c.func, ast.Name) and c.func.id == "verifier" and c.args]

    def libelles(nom, vus):
        """Ceux de `nom`, puis ceux des fonctions qu'il nomme et que `vus` n'a pas encore."""
        vus.add(nom)
        nommes = {n.id for n in ast.walk(fonctions[nom]) if isinstance(n, ast.Name) and n.id in fonctions} - set(groupes)
        return propres(fonctions[nom]) + [l for autre in sorted(nommes - vus) for l in libelles(autre, vus)]

    groupes = [c.value.args[0].id for c in arbre.body if isinstance(c, ast.Expr) and isinstance(c.value, ast.Call)
               and isinstance(c.value.func, ast.Name) and c.value.func.id == "groupe" and c.value.args
               and isinstance(c.value.args[0], ast.Name) and c.value.args[0].id in fonctions]
    return [(g, libelles(g, set())) for g in groupes]


def cmd_parite(a, sortie):
    """`parite [--racine <kit>]` (REF5) : la parité entre `scripts/test-vlp.py` et la suite pytest de `tests/`. La
    marque d'un test migré : le libellé d'origine du `verifier`, mot pour mot, en message de son `assert`
    (`assert cond, "<libellé>"` ; un libellé formaté, par son gabarit). Une ligne par groupe — `MIGRÉ <groupe> n/n`,
    `PARTIEL <groupe> k/n — manque : <libellés>`, `RESTE <groupe> 0/n` —, puis `PARITE …` et les comptes bruts.
    Un groupe ne sort de `test-vlp.py` que sur un `MIGRÉ`. Fichier absent ou illisible : `GARDE:`, sort 1."""
    import ast
    racine = os.path.abspath(a.racine or etat.KIT)
    try:
        with open(os.path.join(racine, "scripts", "test-vlp.py"), encoding="utf-8") as f:
            groupes = verifs_des_groupes(ast.parse(f.read()))
        migres = set()
        for chemin in sorted(glob.glob(os.path.join(racine, "tests", "**", "*.py"), recursive=True)):
            with open(chemin, encoding="utf-8") as f:
                migres.update(libelle_de(n.msg) for n in ast.walk(ast.parse(f.read()))
                              if isinstance(n, ast.Assert) and n.msg is not None)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as e:
        sortie.write("GARDE: parite ne lit pas %s : %s\n" % (racine, str(e).splitlines()[0] if str(e) else type(e).__name__))
        return 1
    etats = collections.Counter()
    trouvees = total = 0
    for nom, libelles in groupes:
        manque = [l for l in libelles if l not in migres]
        k, n = len(libelles) - len(manque), len(libelles)
        trouvees, total = trouvees + k, total + n
        if not manque:
            etats["migrés"] += 1
            sortie.write("MIGRÉ %s %d/%d\n" % (nom, k, n))
        elif k:
            etats["partiels"] += 1
            sortie.write("PARTIEL %s %d/%d — manque : %s\n" % (nom, k, n, " ; ".join(dict.fromkeys(manque))))
        else:
            etats["restent"] += 1
            sortie.write("RESTE %s 0/%d\n" % (nom, n))
    sortie.write("PARITE %d groupes · migrés %d · partiels %d · restent %d · vérifications %d/%d\n" % (
        len(groupes), etats["migrés"], etats["partiels"], etats["restent"], trouvees, total))
    return 0
