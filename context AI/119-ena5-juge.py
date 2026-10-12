"""Le juge d'ENA5 : `lancables` contre l'historique Git du kit (critère de fin d'ENA5, 2026-10-12).

Pour chaque fichier de fiches de `context AI/`, chaque paire de fiches passe par `vlp_coeur.lancables` —
le chemin de la commande, pas une fonction seule —, sur leurs vraies lignes **Fichiers**, sans dépendance
ni `(visuel)`, la racine du kit donnée (`entrees`) : partent-elles ensemble ? Le juge : les fichiers des commits
`<ID> : …` de chaque fiche, communs ôtés (`communs_du_kit`). Un fichier commun aux deux est **prévisible** si
les deux lignes **Fichiers** le nomment (`nomme`, ou `releve` pour un motif) ; sinon une fiche a écrit hors de sa
ligne, ce qu'aucun texte ne peut prévoir.

Sortie : paires jugées, conflits prévisibles, lancées ensemble à tort (le critère veut 0), débordements
lancés ensemble, faux croisements (aucun fichier commun, et pourtant séparées). `--detail` liste les paires.

L'historique ne voit que les paires d'un même fichier de fiches qui ont vraiment joué : le 4e relecteur d'ENA5 a
trouvé un chemin partiel (`references/tache-page.md`) qu'aucune n'avait croisé. D'où le second juge, **l'arbre** :
chaque nom écrit des lignes **Fichiers** du kit (`noms_ecrits`) se résout en vrais fichiers (`git ls-files` et tout
chemin de l'historique) — ancré, depuis la racine ; partiel ou nom seul, toute fin de chemin. Deux noms qui
désignent un même fichier doivent se croiser par `croisent` après `ancre` : ratés, le critère veut 0. Un nom qui ne
désigne aucun fichier (à créer, ou mot parasite) n'est pas jugé ; leur nombre est imprimé.
Usage, depuis la racine du kit : py -3 "context AI/119-ena5-juge.py" [--detail]

Mesuré le 2026-10-12. Historique — noms tels qu'écrits : 0 raté, 406 lancées ensemble, 87 débordements, 289 faux
croisements ; 1re liste d'invités : 0, 361, 79, 326 ; partiels en nom seul : 0, 347, 73, 334. Arbre (156 noms
résolus sur 318) — noms tels qu'écrits : 13 ratés, 520 faux croisements ; partiels en nom seul : 0, 818.
"""
import collections
import fnmatch
import glob
import importlib.util
import itertools
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(KIT, "scripts"))
spec = importlib.util.spec_from_file_location("vlp_coeur", os.path.join(KIT, "scripts", "vlp_coeur.py"))
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
RACINE = mod.entrees(KIT)


def fichiers_des_commits():
    """{id de fiche: chemins changés par ses commits `<ID> : …`}, toutes tentatives comprises."""
    log = subprocess.run(["git", "-C", KIT, "-c", "core.quotepath=off", "log", "--no-merges", "--format=@@%s",
                          "--name-only"], capture_output=True, encoding="utf-8", check=True).stdout
    touche, ident = collections.defaultdict(set), None
    for ligne in log.splitlines():
        if ligne.startswith("@@"):
            m = re.match(r"@@([A-Z]{1,3}[0-9]+) :", ligne)
            ident = m.group(1) if m else None
        elif ligne.strip() and ident:
            touche[ident].add(ligne.strip())
    return touche


def ligne_fichiers(lignes, ident):
    """Les lignes du paragraphe **Fichiers** de la fiche `ident`, telles qu'écrites ; [] sans lui."""
    debut = next((i for i, l in enumerate(lignes) if l.startswith("## %s [" % ident)), None)
    if debut is None:
        return []
    fin = next((i for i in range(debut + 1, len(lignes)) if mod.TITRE.match(lignes[i])
                or lignes[i].startswith("<!-- /FICHE")), len(lignes))
    k = next((i for i in range(debut, fin) if lignes[i].startswith("**Fichiers**")), None)
    if k is None:
        return []
    para = [lignes[k]]
    for l in lignes[k + 1:fin]:
        if not l.strip() or l.startswith(("**", "<!--")):
            break
        para.append(l)
    return para


def ensemble(nom, a, pa, b, pb):
    """Vrai si `lancables` lance `a` et `b` ensemble, sur un fichier de deux fiches minimales."""
    def fiche(i, p):
        return ["<!-- FICHE:%s -->" % i, "## %s [ ] — x" % i, "", "**Dépend de** : rien."] + p + [
            "", "**Critère de fin**", "Rien.", "<!-- /FICHE -->"]
    lignes = ["# Juge", "", "## Le socle commun", "", "Rien.", "", "---"] + fiche(a, pa) + fiche(b, pb)
    return set(mod.lancables(lignes, nom, 2, racine=RACINE)) == {a, b}


def nomme_par(chemin, noms):
    """Vrai si `chemin` est nommé par la ligne **Fichiers** : la règle de `commiter` (`releve`) ou de la relecture."""
    return mod.nomme(chemin, noms) or any(mod.releve(chemin, n) for n in noms)


def communs_du_kit(nom):
    """Les fichiers que toute fiche écrit sans être seule à les écrire : son fichier de fiches (coché ; `lancables`
    l'ôte exprès), sa page (le chef la régénère au bilan), la base du cliquet — `commiter` prend le 1er et le 3e."""
    base = nom[:-3]
    return {"context AI/" + nom, "context AI/artefacts/%s.html" % base, "context AI/artefacts/%s.md" % base,
            "scripts/sante-base.json"}


def juger(detail):
    """Imprimer les comptes du critère ; rendre le nombre de paires lancées ensemble à tort."""
    touche = fichiers_des_commits()
    comptes, debords, rates = collections.Counter(), collections.Counter(), []
    for chemin in sorted(glob.glob(os.path.join(ICI, "*.md"))):
        nom = os.path.basename(chemin)
        lignes = mod.lignes_de(chemin)
        ids = [f[0] for f in mod.fiches_du_fichier(lignes) if f[0] in touche]
        for a, b in itertools.combinations(ids, 2):
            pa, pb = ligne_fichiers(lignes, a), ligne_fichiers(lignes, b)
            if not pa or not pb:
                comptes["sans ligne Fichiers"] += 1
                continue
            comptes["paires jugées"] += 1
            na, nb = mod.noms_fichiers(pa), mod.noms_fichiers(pb)
            communs = (touche[a] & touche[b]) - communs_du_kit(nom)
            prevus = {c for c in communs if nomme_par(c, na) and nomme_par(c, nb)}
            ens = ensemble(nom, a, pa, b, pb)
            comptes["lancées ensemble"] += ens
            if prevus:
                comptes["conflits prévisibles"] += 1
                if ens:
                    rates.append((nom, a, b, sorted(prevus)))
            elif communs and ens:
                comptes["débordements lancés ensemble"] += 1
                debords.update(communs)
            elif not communs and not ens:
                comptes["faux croisements"] += 1
    for cle in ("paires jugées", "sans ligne Fichiers", "lancées ensemble", "conflits prévisibles",
                "débordements lancés ensemble", "faux croisements"):
        print("%s : %d" % (cle, comptes[cle]))
    print("lancées ensemble à tort : %d" % len(rates))
    for r in rates if detail else rates[:10]:
        print("  RATÉ %s %s + %s : %s" % (r[0], r[1], r[2], ", ".join(r[3])))
    print("débordements, fichiers les plus communs : %s" % ", ".join(
        "%s ×%d" % c for c in debords.most_common(8)))
    return len(rates)


def resout(nom, reels):
    """Les vrais chemins que `nom` (écrit, normalisé) peut désigner : ancré (premier nom à la racine), depuis la
    racine ; sinon, toute fin de chemin. Un dossier prend ce qu'il contient ; un motif, ce que `fnmatch` prend."""
    rendu = set()
    for m in mod.deplie(nom):
        ancre = "/" in m and m.split("/", 1)[0] in RACINE
        motif = bool(re.search(r"[*?[]", m))
        for p in reels:
            if m.endswith("/"):
                ok = p.startswith(m) if ancre else ("/" + m) in ("/" + p)
            elif motif:
                ok = fnmatch.fnmatchcase(p, m) or (not ancre and fnmatch.fnmatchcase(p, "*/" + m))
            else:
                ok = p == m or (not ancre and p.endswith("/" + m))
            if ok:
                rendu.add(p)
    return rendu


def arbre(detail):
    """Imprimer le juge de l'arbre ; rendre le nombre de paires de noms d'un même fichier que `croisent` sépare."""
    log = subprocess.run(["git", "-C", KIT, "-c", "core.quotepath=off", "log", "--all", "--format=", "--name-only"],
                         capture_output=True, encoding="utf-8", check=True).stdout
    actuels = subprocess.run(["git", "-C", KIT, "-c", "core.quotepath=off", "ls-files"], capture_output=True,
                             encoding="utf-8", check=True).stdout
    reels = {l.strip().lower() for l in (actuels + log).splitlines() if l.strip()}
    noms = set()
    for chemin in sorted(glob.glob(os.path.join(ICI, "*.md"))):
        lignes = mod.lignes_de(chemin)
        for f in mod.fiches_du_fichier(lignes):
            noms |= mod.noms_ecrits(ligne_fichiers(lignes, f[0]), RACINE)
    vise = {n: resout(n, reels) for n in noms}
    connus = sorted(n for n in noms if vise[n])
    rates, faux = [], 0
    for x, y in itertools.combinations(connus, 2):
        vrai = bool(vise[x] & vise[y])
        dit = mod.croisent({mod.ancre(x, RACINE)}, {mod.ancre(y, RACINE)})
        if vrai and not dit:
            rates.append((x, y, sorted(vise[x] & vise[y])[0]))
        faux += dit and not vrai
    print("arbre : %d chemins réels · %d noms écrits · %d résolus · %d paires" % (
        len(reels), len(noms), len(connus), len(connus) * (len(connus) - 1) // 2))
    print("arbre, faux croisements : %d" % faux)
    print("arbre, même fichier séparés à tort : %d" % len(rates))
    for r in rates if detail else rates[:10]:
        print("  RATÉ %s + %s : %s" % r)
    return len(rates)


if __name__ == "__main__":
    sys.exit(1 if juger("--detail" in sys.argv) + arbre("--detail" in sys.argv) else 0)
