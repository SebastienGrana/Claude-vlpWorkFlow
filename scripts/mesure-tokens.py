#!/usr/bin/env python3
import collections
import glob
import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

# Colonnes affichées, dans l'ordre du socle (context AI/13-tours.md).
COLONNES = [
    "tours", "appels", "ctx_1er", "ctx_dernier",
    "input", "output", "cache_creation", "cache_1h", "cache_read", "total",
    "equiv", "usd", "invalides",
]
# Colonnes entières qui se somment sur la ligne TOTAL ; ctx_1er et ctx_dernier
# n'ont pas de somme qui ait un sens (un contexte n'est pas un cumul) ; equiv et
# usd se somment à part (ils peuvent valoir « ? »).
SOMMABLES = ["tours", "appels", "input", "output", "cache_creation", "cache_1h", "cache_read", "total", "invalides"]

# La grille — dollars par million de tokens, recopiés de la table des prix par
# modèle de la documentation officielle, lue le 2026-09-23 :
# https://platform.claude.com/docs/en/about-claude/pricing
#   - claude-opus-5-5 : ligne « Claude Opus 5.5 », ajoutée ce jour-là ;
#   - les sept autres, lues le 2026-09-17 dans la skill claude-api, y ont été
#     relues sans écart ;
#   - claude-haiku-4-5-20251001 : alias daté de claude-haiku-4-5, prix de la
#     ligne « Claude Haiku 4.5 » — la page ne nomme pas les ids, la skill
#     claude-api si (shared/models.md:70).
# Seuls les modèles que nomment les transcripts y figurent. Le mode « fast »
# n'y est pas : le 2026-09-17, la skill claude-api donnait son prix d'entrée et
# de sortie, pas celui de son cache — un tour fast compte comme un modèle inconnu.
GRILLE = {
    # modèle:                    (entrée,  sortie, cache lu, écrit 5 min, écrit 1 h)
    "claude-fable-5-1":          ("10",    "50",   "0.25",   "12.5",      "20"),
    "claude-opus-5-5":           ("4",     "20",   "0.20",   "5",         "8"),
    "claude-opus-5":             ("5",     "25",   "0.5",    "6.25",      "10"),
    "claude-opus-4-7":           ("5",     "25",   "0.5",    "6.25",      "10"),
    "claude-sonnet-5":           ("2",     "10",   "0.2",    "2.5",       "4"),
    "claude-sonnet-4-6":         ("3",     "15",   "0.3",    "3.75",      "6"),
    "claude-haiku-4-5":          ("1",     "5",    "0.1",    "1.25",      "2"),
    "claude-haiku-4-5-20251001": ("1",     "5",    "0.1",    "1.25",      "2"),
}
GRILLE = {m: tuple(Decimal(p) for p in prix) for m, prix in GRILLE.items()}


def ratios(prix):
    """Poids de chaque compte en tokens d'entrée : (sortie, cache lu, 5 min, 1 h)."""
    entree, sortie, lu, ecrit_5m, ecrit_1h = prix
    return (sortie / entree, lu / entree, ecrit_5m / entree, ecrit_1h / entree)


# Pour un modèle absent de la grille, `equiv` ne se calcule que si tous les
# modèles de la grille ont les mêmes ratios. Ce n'est pas le cas au 2026-09-17 :
# le cache lu de Fable 5.1 pèse 0,025 au lieu de 0,1. Donc « ? ».
_tous = {ratios(p) for p in GRILLE.values()}
RATIOS_COMMUNS = _tous.pop() if len(_tous) == 1 else None


def resoudre(argument):
    """Rend (chemin, None) ou (None, erreur), sans rien ouvrir.

    `~` → home ; un chemin (`C:\\…`, `C:/…`, `/…`) tel quel ; un id seul (ni
    séparateur ni `.jsonl`) → le premier `~/.claude/projects/*/<id>.jsonl`.
    """
    argument = argument.strip()
    if "/" in argument or "\\" in argument or argument.endswith(".jsonl"):
        return os.path.expanduser(argument), None
    motif = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", glob.escape(argument) + ".jsonl")
    trouves = sorted(glob.glob(motif))
    if not trouves:
        return None, f"id introuvable : aucun {motif}"
    return trouves[0], None


def _comptes(usage):
    """Les cinq nombres qu'on somme, tirés d'un `usage`."""
    cc = usage.get("cache_creation")
    # Sans sous-objet (vieux transcript), tout le cache écrit compte en 5 min,
    # la durée par défaut.
    cache_1h = cc.get("ephemeral_1h_input_tokens", 0) if isinstance(cc, dict) else 0
    return (
        usage.get("input_tokens", 0),
        usage.get("output_tokens", 0),
        usage.get("cache_creation_input_tokens", 0),
        cache_1h,
        usage.get("cache_read_input_tokens", 0),
    )


def _cout(comptes, modele):
    """(equiv, usd) d'un tour, en Decimal ; None à la place d'un terme inconnu."""
    entree, sortie, creation, ecrit_1h, lu = comptes
    if not any(comptes):
        return Decimal(0), Decimal(0)   # tour vide (ex. <synthetic>) : rien à payer
    ecrit_5m = creation - ecrit_1h
    prix = GRILLE.get(modele)
    r = ratios(prix) if prix else RATIOS_COMMUNS
    equiv = None
    if r:
        r_sortie, r_lu, r_5m, r_1h = r
        equiv = entree + sortie * r_sortie + lu * r_lu + ecrit_5m * r_5m + ecrit_1h * r_1h
    usd = None
    if prix:
        p_entree, p_sortie, p_lu, p_5m, p_1h = prix
        usd = (entree * p_entree + sortie * p_sortie + lu * p_lu + ecrit_5m * p_5m + ecrit_1h * p_1h) / Decimal(1_000_000)
    return equiv, usd


def arrondir_equiv(x):
    return "?" if x is None else int(x.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def arrondir_usd(x):
    return "?" if x is None else str(x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def mesurer(chemin):
    # Un tour = un `message.id` ; un tour s'écrit sur 1 à 3 lignes `assistant`.
    # On garde les comptes de la DERNIÈRE ligne de chaque id, dans l'ordre
    # d'apparition, et on note les ids dont les comptes changent d'une ligne
    # à l'autre (le socle dit qu'ils sont identiques : on le vérifie).
    # Les appels d'outils, eux, se comptent par ligne : un bloc `tool_use`
    # n'apparaît que sur une seule ligne (vérifié le 2026-09-17 sur deux
    # transcripts : 56 blocs, 56 ids distincts).
    tours = {}          # id -> (comptes, modèle) de la dernière ligne, ordre du fichier
    divergents = set()
    outils = collections.Counter()
    lignes_invalides = 0
    n_ligne = 0

    try:
        f = open(chemin, encoding="utf-8")
    except OSError as e:
        return None, f"illisible : {e}"

    with f:
        for ligne in f:
            n_ligne += 1
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                d = json.loads(ligne)
            except json.JSONDecodeError:
                lignes_invalides += 1
                continue
            message = d.get("message")
            if not isinstance(message, dict):
                continue
            contenu = message.get("content")
            if isinstance(contenu, list):
                for bloc in contenu:
                    if isinstance(bloc, dict) and bloc.get("type") == "tool_use":
                        outils[bloc.get("name") or "?"] += 1
            usage = message.get("usage")
            if not isinstance(usage, dict):
                continue
            # Sans id (vieux transcript), la ligne compte pour un tour à elle seule.
            mid = message.get("id") or d.get("requestId") or f"_ligne{n_ligne}"
            comptes = _comptes(usage)
            modele = str(message.get("model") or "?")
            if usage.get("speed") == "fast":
                modele += " (fast)"
            if mid in tours and tours[mid][0] != comptes:
                divergents.add(mid)
            tours[mid] = (comptes, modele)

    valeurs = [c for c, _ in tours.values()]
    input_tokens = sum(c[0] for c in valeurs)
    output_tokens = sum(c[1] for c in valeurs)
    cache_creation = sum(c[2] for c in valeurs)
    cache_1h = sum(c[3] for c in valeurs)
    cache_read = sum(c[4] for c in valeurs)
    total = input_tokens + output_tokens + cache_creation + cache_read

    equiv, usd = Decimal(0), Decimal(0)
    inconnus = set()
    for comptes, modele in tours.values():
        e, u = _cout(comptes, modele)
        if u is None:
            inconnus.add(modele)
        equiv = None if (equiv is None or e is None) else equiv + e
        usd = None if (usd is None or u is None) else usd + u

    def ctx(c):
        return c[0] + c[2] + c[4]

    return {
        "tours": len(tours),
        "appels": sum(outils.values()),
        "outils": dict(outils),
        "ctx_1er": ctx(valeurs[0]) if valeurs else 0,
        "ctx_dernier": ctx(valeurs[-1]) if valeurs else 0,
        "input": input_tokens,
        "output": output_tokens,
        "cache_creation": cache_creation,
        "cache_1h": cache_1h,
        "cache_read": cache_read,
        "total": total,
        "equiv": arrondir_equiv(equiv),
        "usd": arrondir_usd(usd),
        "equiv_exact": equiv,
        "usd_exact": usd,
        "inconnus": sorted(inconnus),
        "invalides": lignes_invalides,
        "divergents": len(divergents),
    }, None


def afficher_grille():
    print("\t".join(["modele", "entree", "sortie", "cache_lu", "cache_5m", "cache_1h",
                     "r_sortie", "r_lu", "r_5m", "r_1h"]))
    for modele, prix in GRILLE.items():
        print("\t".join([modele] + [str(p) for p in prix] + [str(r.normalize()) for r in ratios(prix)]))


def main(argv):
    if argv == ["--grille"]:
        afficher_grille()
        return 0
    if not argv:
        print("usage: mesure-tokens.py <fichier.jsonl | id de session> [...] | --grille", file=sys.stderr)
        return 1

    resultats = []
    vus = set()

    for argument in argv:
        chemin, erreur = resoudre(argument)
        if erreur:
            print(f"{argument}\t{erreur}", file=sys.stderr)
            continue
        nom = os.path.basename(chemin)
        # Le même fichier passé deux fois (un id et son chemin, ou deux fiches
        # jouées dans la même session) ne se compte qu'une fois.
        cle = os.path.normcase(os.path.abspath(chemin))
        if cle in vus:
            print(f"{nom}\tdéjà compté : passé plus d'une fois, compté une", file=sys.stderr)
            continue
        vus.add(cle)
        r, erreur = mesurer(chemin)
        if erreur:
            print(f"{nom}\t{erreur}", file=sys.stderr)
            continue
        if r["divergents"] > 0:
            print(f"{nom}\tdivergents = {r['divergents']} (ids dont l'usage change d'une ligne à l'autre)",
                  file=sys.stderr)
        if r["inconnus"]:
            print(f"{nom}\tmodèle absent de la grille : {', '.join(r['inconnus'])} — usd vaut ?",
                  file=sys.stderr)
        resultats.append((nom, r))

    if not resultats:
        print("aucun fichier n'a pu être lu", file=sys.stderr)
        return 1

    print("\t".join(["fichier"] + COLONNES))
    for nom, r in resultats:
        print("\t".join(str(x) for x in [nom] + [r[k] for k in COLONNES]))

    if len(resultats) > 1:
        cumul = {k: 0 for k in SOMMABLES}
        equiv, usd = Decimal(0), Decimal(0)
        for _, r in resultats:
            for k in cumul:
                cumul[k] += r[k]
            equiv = None if (equiv is None or r["equiv_exact"] is None) else equiv + r["equiv_exact"]
            usd = None if (usd is None or r["usd_exact"] is None) else usd + r["usd_exact"]
        cumul["equiv"] = arrondir_equiv(equiv)
        cumul["usd"] = arrondir_usd(usd)
        print("\t".join(str(x) for x in ["TOTAL"] + [cumul.get(k, "-") for k in COLONNES]))

    for nom, r in resultats:
        detail = " ".join(f"{n}={c}" for n, c in sorted(r["outils"].items(), key=lambda x: (-x[1], x[0])))
        print(f"{nom}\tappels\t{detail or '-'}")

    return 0


if __name__ == "__main__":
    # Sous Windows, la console n'est pas en UTF-8 : sans ceci, les accents des
    # messages sortent illisibles.
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
