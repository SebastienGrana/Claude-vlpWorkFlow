"""Les pages en attente de publication, et le niveau d'un projet équipé (REF47 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import argparse
import collections
import datetime
import hashlib
import io
import json
import os
import re
import noyau.relecture   # `noyau.relecture.<nom>` : un test remplace ce nom là (REF46)

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (
    COURANT,
    TITRE,
    chemin_garde,
    lignes_de,
    lignes_du_projet,
    lignes_index,
    lire,
    tampon_neuf,
)
from noyau.carte import (equipe, fichier_courant, trouver)
from noyau.page import (empreinte, noter_publie)
from noyau.notes import (cmd_page, cmd_renvois, page_du_fichier)
from noyau.feuille import (MONO, champ, couts_du_projet, feuille, lettre_de, page_feuille, zone, zone_todo)
from noyau.clos import (
    GABARIT_FEUILLE,
    RANG_CLOS,
    ecrire_couts,
    lignes_clos,
    migrer_clos,
    migrer_feuille,
    textes_visibles,
)
from noyau.relecture import (etat_git)

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF47 — `source_ignore` — se lisent ici seulement.
__all__ = [
    "TEXTE_LIMITE", "MARGE_TACHE", "dossier_artefacts", "entrees_attente", "texte_attente", "lire_attente",
    "ecrire_attente", "ajouter_attente", "retirer_attente", "lignes_attente", "attentes_de_nuit", "noter_attentes",
    "dire_attentes", "page_relative", "remise_a_zero", "cmd_attente", "noter_joints", "cmd_attente_hook",
    "PLAGE_TEXTE", "cmd_comparer", "markdown_brut", "VARIABLE", "PORTEUSE", "TITRE_CLOS", "capte",
    "variables_citees", "table_des_clos", "FICHIER_MD", "entete_clos", "sans_table_des_clos", "cmd_niveau",
    "etapes_niveau", "CHEMIN_MACHINE", "ecarts_git", "retirer_clos", "poser_ouverture", "retirer_ligne_courant",
]


# --- attente : les pages que la limite du jour a refusées (chantier LOC) ------

TEXTE_LIMITE = "publish 429"                    # le début du texte du refus, relevé par LOC1
MARGE_TACHE = datetime.timedelta(minutes=10)    # la tâche planifiée part après la remise à zéro


def dossier_artefacts(racine):
    contexte = champ(lignes_de(os.path.join(racine, "CHANTIER.md")), "contexte", "context AI/")
    return os.path.join(racine, contexte, "artefacts")


def entrees_attente(lignes):
    """[(page, url, heure)] des lignes d'un fichier `en-attente`, dans leur ordre."""
    entrees = []
    for l in lignes:
        c = l.split("\t") + ["aucune", ""]
        if c[0]:
            entrees.append((c[0], c[1], c[2]))
    return entrees


def texte_attente(entrees):
    """Le fichier `en-attente` de `entrees` : une ligne par page — le texte que `ecrire_attente` écrit (chantier NUI)."""
    return "".join("\t".join(e) + "\n" for e in entrees)


def lire_attente(artefacts):
    """[(page, url, heure)] dans l'ordre du fichier `en-attente` ; absent : liste vide."""
    chemin = os.path.join(artefacts, "en-attente")
    return entrees_attente(lignes_de(chemin)) if os.path.isfile(chemin) else []


def ecrire_attente(artefacts, entrees):
    """Le fichier en entier dans un `.tmp` puis `os.replace` ; liste vide : le fichier disparaît."""
    chemin = os.path.join(artefacts, "en-attente")
    if not entrees:
        if os.path.exists(chemin):
            os.remove(chemin)
        return
    os.makedirs(artefacts, exist_ok=True)
    with open(chemin + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(texte_attente(entrees))
    os.replace(chemin + ".tmp", chemin)


def ajouter_attente(artefacts, page, url, heure):
    """La page prend la place de son ancienne entrée, en fin de liste : la dernière gagne."""
    ecrire_attente(artefacts, [e for e in lire_attente(artefacts) if e[0] != page] + [(page, url, heure)])


def retirer_attente(artefacts, page):
    """Le nombre d'entrées restantes ; rien n'est écrit si la page n'y était pas."""
    avant = lire_attente(artefacts)
    restant = [e for e in avant if e[0] != page]
    if len(restant) != len(avant):
        ecrire_attente(artefacts, restant)
    return len(restant)


def lignes_attente(artefacts):
    return ["ATTENTE=%s %s" % (p, u) for p, u, _ in lire_attente(artefacts)]


def attentes_de_nuit(projet, pages, sortie):
    """Sous `VLP_NUIT=1`, mettre en attente chaque `(chemin, url)` de `pages` — la session `claude -p` n'a pas l'outil
    Artifact : le chef du matin les publie (NPB1) —, et écrire `ATTENTE <page> — <url>`. Hors nuit : rien."""
    if os.environ.get("VLP_NUIT") == "1":
        noter_attentes(projet, pages, sortie)


def noter_attentes(projet, pages, sortie):
    """Mettre en attente chaque `(chemin, url)` de `pages` dans le dossier artefacts du projet, et écrire
    `ATTENTE <page> — <url>` ; une page hors de ce dossier est ignorée."""
    artefacts = dossier_artefacts(projet)
    heure = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    for chemin, url in pages:
        nom = page_relative(artefacts, os.path.abspath(chemin))
        if nom:
            ajouter_attente(artefacts, nom, url or "aucune", heure)
            sortie.write("ATTENTE %s — %s\n" % (nom, url or "aucune"))


def dire_attentes(projet, sortie):
    """Écrire les `ATTENTE=` du projet après les fusions du matin : les pages qu'une nuit n'a pas pu publier (NPB1)."""
    for ligne in lignes_attente(dossier_artefacts(projet)):
        sortie.write(ligne + "\n")


def page_relative(artefacts, page):
    """`page` relative au dossier artefacts, en barres obliques ; None si elle est ailleurs."""
    if os.path.isabs(page):
        try:
            page = os.path.relpath(page, artefacts)
        except ValueError:
            return None
    page = page.replace("\\", "/")
    return None if page == ".." or page.startswith("../") else page


def remise_a_zero(maintenant):
    """(remise à zéro, tâche planifiée) : le prochain minuit UTC après `maintenant`, puis
    `MARGE_TACHE` plus tard, dans le fuseau de `maintenant`."""
    utc = maintenant.astimezone(datetime.timezone.utc)
    zero = datetime.datetime.combine(utc.date() + datetime.timedelta(days=1), datetime.time(),
                                     tzinfo=datetime.timezone.utc)
    return zero.astimezone(maintenant.tzinfo), (zero + MARGE_TACHE).astimezone(maintenant.tzinfo)


def cmd_attente(a, sortie, maintenant=None):
    if a.op == "lister":
        # la racine d'un projet équipé vaut son dossier artefacts : sinon `.` rendait « ATTENTE 0 » en silence
        dossier = dossier_artefacts(a.dossier) if equipe(a.dossier) else a.dossier
        for l in lignes_attente(dossier):
            sortie.write(l + "\n")
        sortie.write("ATTENTE %d\n" % len(lire_attente(dossier)))
        return 0
    racine = trouver(a.projet or os.getcwd())
    if racine is None:
        sortie.write("GARDE: pas de projet équipé ici : %s\n" % (a.projet or os.getcwd()))
        return 1
    artefacts = dossier_artefacts(racine)
    page = page_relative(artefacts, a.page)
    url = getattr(a, "url", None) or "aucune"
    if page is None or any(c in page + url for c in "\t\r\n"):
        sortie.write("GARDE: page hors du dossier artefacts, ou tabulation dans la page ou l'url : %s\n" % a.page)
        return 1
    if a.op == "retirer":
        n = retirer_attente(artefacts, page)
    else:
        heure = (maintenant or datetime.datetime.now().astimezone()).isoformat(timespec="minutes")
        ajouter_attente(artefacts, page, url, heure)
        n = len(lire_attente(artefacts))
    sortie.write("ATTENTE %d\n" % n)
    return 0


def noter_joints(outil, cwd, page):
    """Après une publication réussie : l'empreinte de chaque fichier de `files` (forme dict,
    source en chemin ou `{from}` ; relative à `root`, puis au dossier courant) dans `publie`,
    à côté de `page` (chantier JNT). Un fichier copié d'un autre artefact ou absent : ignoré."""
    fichiers = outil.get("files")
    if not isinstance(fichiers, dict):
        return
    base = cwd if isinstance(cwd, str) else os.getcwd()
    if isinstance(outil.get("root"), str):
        base = os.path.join(base, outil["root"])
    empreintes = {}
    for nom, source in fichiers.items():
        if isinstance(source, dict):
            source = source.get("from")
        if isinstance(nom, str) and isinstance(source, str):
            source = os.path.join(base, source)
            if os.path.isfile(source):
                empreintes[nom] = empreinte(source)
    if empreintes:
        noter_publie(os.path.dirname(page), os.path.basename(page), empreintes)


def cmd_attente_hook(entree, sortie, maintenant=None):
    """Le hook `PostToolUse` et `PostToolUseFailure` sur `Artifact` (chantier LOC). Un échec dont
    `error` porte `TEXTE_LIMITE` ajoute la page à la liste et, la première fois du jour UTC pour
    ce projet, propose une tâche planifiée ; un succès retire la page et note l'empreinte des
    joints passés (`noter_joints`, chantier JNT). Muet sur tout le reste : un autre refus, une
    page hors des artefacts d'un projet équipé, une entrée illisible."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    if not isinstance(d, dict) or d.get("tool_name") != "Artifact":
        return 0
    evenement, outil = d.get("hook_event_name"), d.get("tool_input")
    if evenement not in ("PostToolUse", "PostToolUseFailure") or not isinstance(outil, dict) \
            or outil.get("asset") is True:
        return 0
    chemin = outil.get("file_path")
    if not isinstance(chemin, str) or not chemin:
        return 0
    cwd = d.get("cwd")
    if not os.path.isabs(chemin) and isinstance(cwd, str):
        chemin = os.path.join(cwd, chemin)
    chemin = os.path.abspath(chemin)
    racine = trouver(os.path.dirname(chemin))
    if racine is None:
        return 0
    artefacts = dossier_artefacts(racine)
    page = page_relative(artefacts, chemin)
    if page is None:
        return 0
    if evenement == "PostToolUse":
        retirer_attente(artefacts, page)
        noter_joints(outil, cwd, chemin)
        return 0
    erreur = d.get("error")
    if not isinstance(erreur, str) or TEXTE_LIMITE not in erreur:
        return 0
    maintenant = maintenant or datetime.datetime.now().astimezone()
    url = outil.get("url")
    ajouter_attente(artefacts, page, url if isinstance(url, str) and url else "aucune",
                    maintenant.isoformat(timespec="minutes"))
    jour = maintenant.astimezone(datetime.timezone.utc).date().isoformat()
    if not tampon_neuf("vlp-attente-%s-%s" % (hashlib.sha1(racine.encode("utf-8")).hexdigest()[:16], jour)):
        return 0
    zero, tache = remise_a_zero(maintenant)
    message = ("Limite de publication du jour atteinte : %s attend dans la liste (`attente lister`). "
               "Remise à zéro à %s locale ; propose à l'utilisateur une tâche planifiée à %s qui "
               "republie la liste." % (page, zero.strftime("%H:%M"), tache.strftime("%H:%M")))
    sortie.write(json.dumps({"hookSpecificOutput": {"hookEventName": evenement, "additionalContext": message}},
                            ensure_ascii=False) + "\n")
    return 0


# « Fiches » avec majuscule aussi : l'encart du chantier en cours l'écrit ainsi (dette BTN).
PLAGE_TEXTE = re.compile(r"[Ff]iches [A-Z]{1,3}[0-9]+(?:–[A-Z]{1,3}[0-9]+)?")


def cmd_comparer(a, sortie):
    """`PERDU:`/`AJOUTÉ:` entre le texte visible de deux pages, en multiset —
    une mesure, pas une garde : sort 0 même avec des pertes."""
    for chemin in (a.ancienne, a.neuve):
        if not os.path.isfile(chemin):
            sortie.write("GARDE: introuvable %s\n" % chemin)
            return 1
    anciens = textes_visibles(lire(a.ancienne))
    neufs = textes_visibles(lire(a.neuve))
    restant_neufs = collections.Counter(neufs)
    perdus = []
    for t in anciens:
        if restant_neufs[t] > 0:
            restant_neufs[t] -= 1
        else:
            perdus.append(t)
    restant_anciens = collections.Counter(anciens)
    ajoutes = []
    for t in neufs:
        if restant_anciens[t] > 0:
            restant_anciens[t] -= 1
        else:
            ajoutes.append(t)
    # Dette HAB : une plage d'en-tête refaite (« fiches X1–X7 » → « X1–X8 ») n'est
    # pas une perte — la paire sort en `PLAGE:`, ni perdue ni ajoutée.
    plages = []
    for t in list(perdus):
        forme = PLAGE_TEXTE.sub("fiches #", t)
        if forme == t:
            continue
        for n in ajoutes:
            if PLAGE_TEXTE.sub("fiches #", n) == forme:
                plages.append((t, n))
                perdus.remove(t)
                ajoutes.remove(n)
                break
    for t in perdus:
        sortie.write("PERDU: %s\n" % t)
    for t in ajoutes:
        sortie.write("AJOUTÉ: %s\n" % t)
    for t, n in plages:
        sortie.write("PLAGE: %s → %s\n" % (t, n))
    sortie.write("COMPARER %d perdus · %d ajoutés%s\n" % (
        len(perdus), len(ajoutes), " · %d plages refaites" % len(plages) if plages else ""))
    return 0


def markdown_brut(html):
    """(`**`, liens Markdown, liens cassés) restés dans les zones todo, encours et
    clos d'une feuille de route, en occurrences — hors code cité, hors ligne
    d'exemple du gabarit."""
    (a, b, _), (c, d) = zone_todo(html), zone(html, "encours", "\n", "  </section>")
    # une feuille dont les clos sont partis dans l'archive n'a plus de ZONE:clos (chantier ARC)
    e, f = zone(html, "clos", "<tbody>\n", "        </tbody>") if "<!-- ZONE:clos" in html else (0, 0)
    clos = RANG_CLOS.sub(lambda m: "".join(lignes_clos(m.group(0))), html[e:f])
    texte = MONO.sub("", html[a:b] + html[c:d] + clos)
    return texte.count("**"), texte.count("](http"), texte.count('href="&lt;')


# --- niveau ------------------------------------------------------------------

# Ce qu'on ne regarde pas : une copie locale de `methode-chantier.md`. La
# méthode dit qu'un projet équipé avant la règle garde la sienne — on a
# seulement cessé d'en fabriquer.
VARIABLE = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}")
# Une variable ne compte que là où une commande lit un chemin : le champ d'une
# ligne `- **nom** : …`, ou une cellule de table. Ailleurs c'est de la prose qui
# cite la règle, et le fichier d'état en cite beaucoup.
PORTEUSE = re.compile(r"^\s*(?:-\s*\*\*[^*]+\*\*\s*:|\|)")
TITRE_CLOS = re.compile(r"^#+\s.*\bclos\b", re.I)


def capte(fn, *args):
    """(code, lignes) d'une sous-commande rejouée pour son texte : `niveau`
    n'invente aucun contrôle que les autres savent déjà faire."""
    s = io.StringIO()
    code = fn(*(args + (s,)))
    return code, s.getvalue().splitlines()


def variables_citees(projet, sources):
    """(chemin, numéro, variable) de chaque `${…}` posée en chemin lisible."""
    for libelle, chemin in sources:
        for i, l in enumerate(lignes_du_projet(projet, chemin, libelle), 1):
            if PORTEUSE.match(l):
                for v in VARIABLE.findall(l):
                    yield chemin, i, v


def table_des_clos(lignes):
    """Le numéro du titre « Chantiers clos » suivi d'une table, ou None : le
    titre seul ne gêne pas, c'est la table qui double l'index."""
    debut = None
    for i, l in enumerate(lignes, 1):
        if l.startswith("#"):
            debut = i if TITRE_CLOS.match(l) else None
        elif debut and l.startswith("|"):
            return debut
    return None


FICHIER_MD = re.compile(r"[\w][\w./ -]*\.md")


def entete_clos():
    """Le titre et la phrase que le gabarit de `CHANTIER.md` pose à la place
    d'une table des chantiers clos."""
    g = lignes_de(os.path.join(etat.KIT, "templates", "CHANTIER.md"))
    i = next(k for k, l in enumerate(g) if TITRE_CLOS.match(l))
    j = next(k for k in range(i, len(g)) if g[k].startswith("Lettres de fiche déjà prises"))
    return g[i:j]


def sans_table_des_clos(carte_, index):
    """`CHANTIER.md` sans sa table des chantiers clos, ou None si la retirer
    perdrait quelque chose : la ligne des lettres prises doit suivre la table,
    et l'index nommer chacun de ses fichiers."""
    i = table_des_clos(carte_)
    if i is None:
        return None
    i -= 1
    j = next((k for k in range(i, len(carte_)) if carte_[k].startswith("Lettres de fiche déjà prises")), None)
    if j is None:
        return None
    vus = "\n".join(index)
    for l in carte_[i:j]:
        if l.startswith("|") and any(os.path.basename(nom) not in vus for nom in FICHIER_MD.findall(l)):
            return None
    return carte_[:i] + entete_clos() + carte_[j:]


def cmd_niveau(a, sortie):
    """En quoi un projet équipé a dérivé du kit. Sans `--ecrire`, n'écrit rien
    nulle part ; avec, corrige les écarts dont la bonne valeur se déduit sans
    jugement, et laisse les autres en `ÉCART:`. Comme `clore`, tout se calcule
    avant la première écriture."""
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    date = a.date or __import__("datetime").date.today().isoformat()
    ecarts = avertissements = corriges = 0
    ecritures = []
    carte_ = lignes_du_projet(projet, "CHANTIER.md", "carte")

    _, lignes = capte(cmd_renvois, projet)
    poids = "POIDS non mesuré"
    for l in lignes:
        if l.startswith("ABSENT: "):
            ecarts += 1
            sortie.write("ÉCART: renvois: %s — nommé, introuvable\n" % l[8:])
        elif l.startswith("AVERTISSEMENT: "):
            avertissements += 1
            sortie.write("AVERTISSEMENT: poids: %s\n" % l[15:])
        elif l.startswith("POIDS "):
            poids = l
        elif l.startswith("GARDE: "):
            ecarts += 1
            sortie.write("ÉCART: renvois: %s\n" % l[7:])

    page = page_feuille(projet)
    absente = not os.path.isfile(page)
    html = lire(os.path.join(etat.KIT, GABARIT_FEUILLE)) if absente else lire(page)
    migre = migrer_feuille(html)
    converti, n = html, 0
    try:
        neuf, _ = feuille(projet, migre, None, date)
        converti, n = migrer_clos(neuf)
        # sans --ecrire : la page que l'on voit ; absente, le gabarit régénéré, comme avant VOI1
        md = markdown_brut(converti if a.ecrire else neuf if absente else html)
    except ValueError as e:
        neuf = md = None
        ecarts += 1
        sortie.write("ÉCART: feuille: %s\n" % e)
    if neuf is None:
        pass
    elif absente:
        if a.ecrire:
            ecritures.append((page, converti))
            corriges += 1
            sortie.write("CORRIGÉ: feuille: posée depuis le gabarit puis régénérée — %s\n" % page)
        else:
            ecarts += 1
            sortie.write("ÉCART: feuille: feuille de route introuvable : %s — le gabarit la pose\n" % page)
    else:
        for present, manque, pose in (
                (migre != html, "le bloc repliable des chantiers clos manque, et son estimation en"
                                " dollars — le gabarit les a", "bloc repliable des chantiers clos posé"),
                (neuf != migre, "écart — « vlp.py feuille %s » la régénère" % projet, "régénérée")):
            if not present:
                continue
            if a.ecrire:
                corriges += 1
                sortie.write("CORRIGÉ: feuille: %s\n" % pose)
            else:
                ecarts += 1
                sortie.write("ÉCART: feuille: %s\n" % manque)
        if a.ecrire and n:
            corriges += 1
            sortie.write("CORRIGÉ: feuille: %d lignes closes converties\n" % n)
        if a.ecrire and converti != html:
            ecritures.append((page, converti))
    sortie.write("MARKDOWN non mesuré, la feuille ne se régénère pas — %s\n" % page if md is None
                 else "MARKDOWN %d ** · %d liens Markdown · %d liens cassés — %s\n" % (md + (page,)))
    if md and any(md):
        ecarts += 1
        sortie.write("ÉCART: feuille: Markdown brut ou lien cassé%s\n"
                     % (" — « vlp.py niveau --ecrire » convertit les lignes closes" if n and not a.ecrire else ""))

    courant = coeur.courant_a_compter(projet, sortie)
    if courant:
        fichier = chemin_garde(os.path.join(projet, courant), "fichier de fiches courant", courant)
        code, lignes = capte(cmd_page, argparse.Namespace(
            fichier=fichier, page=page_du_fichier(fichier), note=None, journal=None,
            creer=False, projet=None, titre=None, resultat=None, verifier=True, date=None, forme=False))
        for l in lignes:
            if l.startswith("ÉCART: ") or l.startswith("GARDE: "):
                ecarts += 1
                sortie.write("ÉCART: page: %s\n" % l[7:])

    contexte = champ(carte_, "contexte", "context AI/")
    index = champ(carte_, "index", contexte.rstrip("/") + "/00-INDEX.md")
    sources = [("carte", "CHANTIER.md"), ("index", index)]
    fichier_etat = champ(carte_, "fichier d'état")
    if fichier_etat:
        sources.append(("fichier d'état", fichier_etat))
    for chemin, i, v in variables_citees(projet, sources):
        ecarts += 1
        sortie.write("ÉCART: variable: %s:%d cite %s — une variable ne vaut que dans"
                     " le texte d'une commande, pas dans un fichier de données\n" % (chemin, i, v))

    for e, c, ecrites in etapes_niveau(projet, retirer_clos(projet, carte_, index, a.ecrire, sortie), date, a.ecrire,
                                       sortie):
        ecarts, corriges = ecarts + e, corriges + c
        ecritures += ecrites

    for chemin, contenu in ecritures:
        dossier = os.path.dirname(chemin)
        if dossier and not os.path.isdir(dossier):
            os.makedirs(dossier)
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write(contenu)
        if chemin == page:
            ecrire_couts(page, contenu, couts_du_projet(projet, contenu))
    sortie.write(poids + "\n")
    if a.ecrire:
        sortie.write("NIVEAU %d corrigés · %d à la main — %s\n" % (corriges, ecarts, projet))
    else:
        sortie.write("NIVEAU %d écarts · %d avertissements — %s\n" % (ecarts, avertissements, projet))
    return 1 if ecarts else 0


def etapes_niveau(projet, clos, date, ecrire, sortie):
    """Les quatre étapes de `niveau` de même forme, `[(écarts, corrigés, écritures)]`, dans l'ordre : `clos`, ce que
    `retirer_clos` a rendu, puis la marque, la ligne et Git. La ligne ne part
    qu'après la marque, que `poser_ouverture` pose en la lisant, et du CHANTIER.md que `retirer_clos` a peut-être
    réécrit (NUI31)."""
    etapes = [clos, poser_ouverture(projet, date, ecrire, sortie)]
    ecrites = [ec for _, _, ecs in etapes for ec in ecs]
    return etapes + [retirer_ligne_courant(projet, ecrites, etapes[1][0] == 0, ecrire, sortie),
                     ecarts_git(projet, sortie)]


# Un chemin de machine : un lecteur Windows, le dossier personnel, ou une racine Unix d'utilisateur.
CHEMIN_MACHINE = re.compile(r"(?<![\w/])(?:[A-Za-z]:[\\/]|~[\\/]|/(?:home|Users|mnt)/)")


def source_ignore(texte):
    """`<fichier>:<ligne>` du motif qui ignore un chemin, lu dans une sortie de `git check-ignore -v` (`<source>:<ligne>:<motif>`, une
    tabulation, le chemin), ou `?`. Ne lance rien (REF47)."""
    return texte.split("\t")[0].rpartition(":")[0] if "\t" in texte else "?"


def ecarts_git(projet, sortie):
    """L'étape « git » de `niveau` (NUI36) : ce que la règle veut suivi (`etat_git`) mais que Git ignore — avec la
    ligne de `.gitignore` qui le couvre — ou n'a pas ajouté, et une ligne **kit** qui porte un chemin de machine. Hors
    Git : rien. `--ecrire` ne corrige rien : retirer une ligne, ajouter, commiter sont des gestes de l'utilisateur.
    `(écarts, 0, [])`."""
    etat = etat_git(projet)
    if etat is None:
        return 0, 0, []
    ecarts = 0
    # Ignoré exprès (NWT) : le projet le déclare, `- **contexte dans Git** : non — <pourquoi>` ; une ligne le dit.
    expres = champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "contexte dans Git", "")
    if etat["ignoré"] and re.match(r"non\b", expres, re.I):
        sortie.write("EXPRÈS: git: %d chemin(s) ignoré(s) exprès — CHANTIER.md, « contexte dans Git » : %s ; aucun "
                     "écart compté\n" % (len(etat["ignoré"]), expres))
    for nom, exemple in [] if re.match(r"non\b", expres, re.I) else etat["ignoré"]:
        code, t = noyau.relecture.git_texte(["check-ignore", "-v", "--", exemple], projet)
        source = source_ignore(t) if code == 0 else "?"
        sortie.write("ÉCART: git: %s — ignoré par %s — à retirer à la main, puis ajouter\n" % (nom, source))
        ecarts += 1
    for nom, _ in etat["non ajouté"]:
        sortie.write("ÉCART: git: %s — non ajouté — à ajouter et commiter à la main\n" % nom)
        ecarts += 1
    kit = champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "kit", "")
    if CHEMIN_MACHINE.search(kit):
        sortie.write("ÉCART: git: CHANTIER.md — la ligne « kit » porte un chemin de machine, et le fichier part"
                     " dans Git : « le plugin vlp », à la main\n")
        ecarts += 1
    return ecarts, 0, []


def retirer_clos(projet, carte_, index, ecrire, sortie):
    """L'étape « clos » de `niveau` : la table des chantiers clos restée dans CHANTIER.md, retirée avec `ecrire` si
    l'index nomme chacun de ses fichiers. `(écarts, corrigés, [(chemin, contenu)])`."""
    rang = table_des_clos(carte_)
    if rang is None:
        return 0, 0, []
    neuve = sans_table_des_clos(carte_, lignes_index(projet, index)) if ecrire else None
    if neuve is None:
        sortie.write("ÉCART: clos: CHANTIER.md:%d — la table des chantiers clos vit"
                     " dans l'index, pas dans la carte\n" % rang)
        return 1, 0, []
    sortie.write("CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:%d —"
                 " l'index nomme chacun de ses fichiers\n" % rang)
    return 0, 1, [(os.path.join(projet, "CHANTIER.md"), "\n".join(neuve) + "\n")]


def poser_ouverture(projet, date, ecrire, sortie):
    """L'étape « marque » de `niveau` (NUI30) : un projet sans aucune marque d'ouverture — `migre` faux — la reçoit
    sur le fichier que nomme l'ancienne ligne de CHANTIER.md, sous son titre, datée de son commit d'ouverture (`date`
    à défaut, et la ligne le dit) ; ligne à `aucun`, projet migré : rien. Sans `ecrire`, introuvable ou sans titre :
    `ÉCART: marque:`. `(écarts, corrigés, [(chemin, contenu)])`."""
    fichier = None if coeur.migre(projet) else fichier_courant(lire(os.path.join(projet, "CHANTIER.md")))
    if not fichier:
        return 0, 0, []
    chemin = os.path.join(projet, fichier)
    lignes = lignes_de(chemin) if os.path.isfile(chemin) else None
    ids = [l.split()[1] for l in lignes or () if TITRE.match(l)]
    code = lettre_de(ids[0]) if ids else "?"
    quand = coeur.date_ouverture(projet, code) if ids and ecrire else None
    if lignes is None:
        sortie.write("ÉCART: marque: %s introuvable — marque d'ouverture non posée\n" % fichier)
    elif not ecrire:
        sortie.write("ÉCART: marque: %s sans **Ouvert.** — « vlp.py niveau --ecrire » la pose\n" % fichier)
    elif not coeur.poser_marque(lignes, coeur.OUVERT_LIGNE % (quand or date)):
        sortie.write("ÉCART: marque: pas de titre « # Chantier » dans %s — marque non posée\n" % fichier)
    else:
        sortie.write("CORRIGÉ: marque: **Ouvert.** le %s sur %s — %s\n" % (quand or date, fichier, "son commit"
                     " d'ouverture" if quand else "date de l'appel, aucun commit « Chantier %s ouvert »" % code))
        return 0, 1, [(chemin, "\n".join(lignes) + "\n")]
    return 1, 0, []


def retirer_ligne_courant(projet, ecritures, marque_posee, ecrire, sortie):
    """L'étape « ligne » de `niveau` (NUI31) : la ligne « fichier de fiches courant » restée dans CHANTIER.md — plus
    aucun lecteur ne la suit, elle ne peut que mentir —, retirée avec `ecrire` si `marque_posee` (l'étape « marque »
    sans écart : sinon elle reste, seule trace du chantier ouvert). Part du dernier CHANTIER.md de `ecritures`, sinon
    du disque, fins de ligne gardées. `(écarts, corrigés, [(chemin, contenu)])`."""
    chemin = os.path.join(projet, "CHANTIER.md")
    texte = next((c for ch, c in reversed(ecritures) if ch == chemin), None)
    if texte is None:
        with open(chemin, encoding="utf-8", newline="") as fh:
            texte = fh.read()
    fin = "\r\n" if "\r\n" in texte else "\n"
    lignes = texte.replace("\r\n", "\n").split("\n")
    rangs = [k for k, l in enumerate(lignes) if COURANT.match(l)]
    if not rangs:
        return 0, 0, []
    if not (ecrire and marque_posee):
        sortie.write("ÉCART: ligne: CHANTIER.md:%d — « fichier de fiches courant » n'est plus lue (NUI31) — %s\n"
                     % (rangs[0] + 1, "« vlp.py niveau --ecrire » la retire" if marque_posee
                        else "gardée tant que la marque d'ouverture manque"))
        return 1, 0, []
    sortie.write("CORRIGÉ: ligne: « fichier de fiches courant » retirée de CHANTIER.md:%d — la marque d'ouverture"
                 " dit le chantier\n" % (rangs[0] + 1))
    return 0, 1, [(chemin, fin.join(l for k, l in enumerate(lignes) if k not in rangs))]
