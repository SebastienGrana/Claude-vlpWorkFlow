"""Ce que la boucle lit pour décider : le verdict, les Tentatives, la garde, la TODO, la reprise (REF53).

Sorti de `boucle.py`, qui le ré-exporte. Chaque fonction reçoit des textes ou des chemins, et ne lance rien.
"""
import os
import re

import carnet

from boucle_noyau.session import COUPEES, REFUS_MAX, kit, ligne_carnet, mesure_kit

__all__ = ["CarteGardee", "verdict_de", "tentatives", "garde_de", "noter_arret", "verification_de", "lire_todo",
    "bloquant", "lire_reprise"
]


class CarteGardee(Exception):
    """La carte a trouvé le projet sans pouvoir dire son chantier — `PROJET=` puis `GARDE:`, sans ligne `COURANT=`
    (plusieurs ouverts, `courant_de`). Ni « aucun » ni un fichier : la boucle ne la prend jamais pour l'un d'eux
    (NUI25) ; le message est la ligne `GARDE:`."""


def verdict_de(texte):
    """(verdict, cause) lus dans le `result` de la relecture : le premier mot s'il est dans `VERDICTS`
    (sinon `None` : aucun verdict vaut `REFUSÉE`, `enchainement.md`), et le mot entre `<verdict> — ` et
    ` :` — `aucun-verdict` quand il n'y en a pas de lisible."""
    t = texte.lstrip()
    m = re.match(r"\w+", t)
    mot = m.group(0) if m and m.group(0) in kit().VERDICTS else None
    if mot is None:
        return None, "aucun-verdict"
    c = re.match(re.escape(mot) + r"\s*—\s*(\w+)\s*:", t)
    return mot, c.group(1) if c else "aucun-verdict"


def tentatives(extrait):
    """Le bloc **Tentatives** de la fiche dans `extrait` : `None` sans bloc, sinon `(refus_seuls, n, motif)` —
    `refus_seuls` si toutes ses lignes numérotées valent `ESSAI_REFUSE` (au moins une), `n` leur nombre,
    `motif` la ligne `Erreur :` du bloc (sans son préfixe) ou None."""
    lignes = extrait.splitlines()
    debut = next((i for i, l in enumerate(lignes) if l.startswith("**Tentatives**")), None)
    if debut is None:
        return None
    bloc = []
    for l in lignes[debut + 1:]:
        if not l.strip() or l.startswith("**"):
            break
        bloc.append(l)
    essais = [l.split(". ", 1)[1].strip() for l in bloc if re.match(r"[0-9]+\. ", l)]
    motif = next((l[len("Erreur :"):].strip() for l in bloc if l.startswith("Erreur :")), None)
    return bool(essais) and all(e == kit().ESSAI_REFUSE for e in essais), len(essais), motif


def garde_de(n, dernier, motif, cause):
    """La garde qui arrête la fiche au refus n° `n` (motif `motif`, cause `cause`, `dernier` : le motif
    d'avant), ou None : la cause est `copie`, la relance joue. Dans cet ordre : `meme-erreur`, `refus-max`,
    puis la cause — `copie` relance, `fiche` arrête (`cause-fiche`), toute autre arrête (`sans-cause`)."""
    if motif == dernier:
        return "meme-erreur"
    if n >= REFUS_MAX:
        return "refus-max"
    if cause == "copie":
        return None
    return "cause-fiche" if cause == "fiche" else "sans-cause"


def noter_arret(a, fiche, garde, n=None, cause=None, reecriture=None):
    """La ligne du carnet d'un arrêt de la nuit : la garde, et pour un refus son n, sa cause, sa réécriture.
    Sans `role` : le carnet ne la compte pas comme une session."""
    ligne_carnet(a, fiche=fiche, garde=garde, refus_n=n, cause=cause, reecriture=reecriture)


def verification_de(racine):
    """La commande du libellé `- **vérification de nuit** : <commande>` de CHANTIER.md, ou None."""
    try:
        return kit().champ(kit().lignes_de(os.path.join(racine, "CHANTIER.md")), "vérification de nuit")
    except OSError:
        return None


def lire_todo(racine):
    """`(todo, erreur)` : `todo` = `(rangs, codes, lettres closes)` — la TODO du fichier d'état (`todo_du_fichier`),
    le code de chaque rang (`codes_todo`) et les lettres de « Lettres de fiche déjà prises » —, lue une fois au départ
    du canal ; None sans fichier d'état lisible, et `valider` seul juge alors. `erreur` : le `ValueError` d'une ligne
    mal formée (une barre verticale dans une cellule, PIP) : tout chantier se met de côté."""
    k = kit()
    try:
        carte = k.lignes_de(os.path.join(racine, "CHANTIER.md"))
        etat = k.champ(carte, "fichier d'état")
        rangs = k.todo_du_fichier(k.lignes_du_projet(racine, etat, "fichier d'état")) if etat else None
    except (k.Absent, OSError):
        return None, None
    except ValueError as e:
        return None, str(e)
    if rangs is None:
        return None, None
    return (rangs, k.codes_todo(rangs), set(k.lettres_prises(carte))), None


def bloquant(code, todo, plan, de_cote):
    """Le code mis de côté ou sauté dont `code` dépend (cellule « Dépend de » de sa ligne TODO), ou None : le motif
    de `est_bloque` — les lettres closes, plus celles du plan, moins celles des chantiers de côté ; un numéro de
    rang d'un chantier de côté bloque aussi. Sans TODO, sans ligne pour `code`, ou rien de côté : None."""
    if not todo or not de_cote or code not in todo[1]:
        return None
    k = kit()
    rangs, codes, closes = todo
    depend = rangs[codes.index(code)][4]
    ok = (closes | {k.lettre_de(c) for c in plan}) - {k.lettre_de(c) for c in de_cote}
    if not k.est_bloque(depend, ok, {rangs[codes.index(c)][0] for c in de_cote if c in codes}):
        return None
    dep_codes, dep_rangs = k.dependances(depend)
    return (next((c for c in dep_codes if k.lettre_de(c) not in ok), None)
            or next((c for c in de_cote if c in codes and rangs[codes.index(c)][0] in dep_rangs), None) or "?")


def lire_reprise(a, racine, codes):
    """`(reprise, erreur)` de `--reprendre` (NUI8), lu dans le carnet du canal. D'abord, seule écriture : chaque `depart`
    sans ligne de session au même id reçoit sa ligne `coupure` (coût de `mesure_kit`). Puis, dans l'ordre du plan, le
    sort de chaque chantier qui a des lignes : `saute` et `de-cote` (garde `saute:…`, `mis-de-cote:…`), `clos` (une
    session `clore` jouée), sinon `en_cours` — le dernier seulement : un autre est de côté. `reprise` : `faits`
    (`{code: genre}`), `en_cours` (le code, ou None), `coupe` (il a une session coupée), `coupees` (le nombre de lignes
    écrites) et `base` — la pointe de la branche du dernier chantier clos, sinon la note `base <sha>` du départ du canal.
    `erreur` : la base ou la branche manque."""
    def du_canal():
        return [d for d in carnet.lire(a.carnet) if d.get("canal") == a.canal]

    lignes = du_canal()
    fins = {d.get("session") for d in lignes if carnet.est_session(d)}
    coupees = 0
    for d in lignes:
        m = re.match(r"depart (\S+)$", str(d.get("note") or ""))
        if not m or not d.get("session") or d["session"] in fins:
            continue
        usd, tours, garde = mesure_kit(d["session"])
        carnet.ajouter(a.carnet, nuit=carnet.nuit_de(a.carnet), canal=a.canal, chantier=d.get("chantier"),
                       role=m.group(1), fiche=d.get("fiche"), issue="coupure", usd_kit=usd, tours_kit=tours,
                       garde=" ; ".join(g for g in ("reprise : session sans fin", garde) if g), session=d["session"])
        coupees += 1
    lignes = du_canal()

    def garde_dit(d, debut):
        return str(d.get("garde") or "").startswith(debut)

    faits, en_cours, coupe = {}, None, False
    vus = [c for c in codes if any(d.get("chantier") == c for d in lignes)]
    for c in vus:
        ls = [d for d in lignes if d.get("chantier") == c]
        if any(garde_dit(d, "saute:") for d in ls):
            faits[c] = "saute"
        elif any(garde_dit(d, "mis-de-cote:") for d in ls):
            faits[c] = "de-cote"
        elif any(d.get("role") == "clore" and d.get("issue") == "jouée" and carnet.est_session(d) for d in ls):
            faits[c] = "clos"
        elif c == vus[-1]:
            en_cours = c
            coupe = any(carnet.est_session(d) and d.get("issue") in COUPEES for d in ls)
        else:
            faits[c] = "de-cote"
    clos = [c for c in codes if faits.get(c) == "clos"]
    if clos:
        branche = "nuit/%s-%s-%s" % (a.date, a.canal, clos[-1])
        code, sha = kit().git_texte(["rev-parse", "--verify", "--quiet", "refs/heads/%s" % branche], racine)
        if code != 0 or not sha.strip():
            return None, "branche %s absente — la base du chantier suivant est introuvable" % branche
        base = sha.strip()
    else:
        bases = [str(d["note"]).split(" ", 1)[1] for d in lignes if str(d.get("note") or "").startswith("base ")]
        if not bases:
            return None, "aucune note « base <sha> » au carnet pour le canal %s — la base du plan est introuvable" % a.canal
        base = bases[-1]
    return {"faits": faits, "en_cours": en_cours, "coupe": coupe, "coupees": coupees, "base": base}, None
