#!/usr/bin/env python3
import json
import os
import sys

# Colonnes affichées, dans l'ordre du socle (context AI/13-tours.md).
COLONNES = [
    "tours", "ctx_1er", "ctx_dernier",
    "input", "output", "cache_creation", "cache_1h", "cache_read", "total",
    "invalides",
]
# Colonnes qui se somment sur la ligne TOTAL ; ctx_1er et ctx_dernier n'ont
# pas de somme qui ait un sens (un contexte n'est pas un cumul).
SOMMABLES = ["tours", "input", "output", "cache_creation", "cache_1h", "cache_read", "total", "invalides"]


def _comptes(usage):
    """Les cinq nombres qu'on somme, tirés d'un `usage`."""
    cc = usage.get("cache_creation")
    cache_1h = cc.get("ephemeral_1h_input_tokens", 0) if isinstance(cc, dict) else 0
    return (
        usage.get("input_tokens", 0),
        usage.get("output_tokens", 0),
        usage.get("cache_creation_input_tokens", 0),
        cache_1h,
        usage.get("cache_read_input_tokens", 0),
    )


def mesurer(chemin):
    # Un tour = un `message.id` ; un tour s'écrit sur 1 à 3 lignes `assistant`.
    # On garde les comptes de la DERNIÈRE ligne de chaque id, dans l'ordre
    # d'apparition, et on note les ids dont les comptes changent d'une ligne
    # à l'autre (le socle dit qu'ils sont identiques : on le vérifie).
    tours = {}          # id -> comptes de la dernière ligne (ordre d'insertion = ordre du fichier)
    divergents = set()
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
            usage = message.get("usage")
            if not isinstance(usage, dict):
                continue
            # Sans id (vieux transcript), la ligne compte pour un tour à elle seule.
            mid = message.get("id") or d.get("requestId") or f"_ligne{n_ligne}"
            comptes = _comptes(usage)
            if mid in tours and tours[mid] != comptes:
                divergents.add(mid)
            tours[mid] = comptes

    input_tokens = sum(c[0] for c in tours.values())
    output_tokens = sum(c[1] for c in tours.values())
    cache_creation = sum(c[2] for c in tours.values())
    cache_1h = sum(c[3] for c in tours.values())
    cache_read = sum(c[4] for c in tours.values())
    total = input_tokens + output_tokens + cache_creation + cache_read

    def ctx(c):
        return c[0] + c[2] + c[4]

    valeurs = list(tours.values())
    return {
        "tours": len(tours),
        "ctx_1er": ctx(valeurs[0]) if valeurs else 0,
        "ctx_dernier": ctx(valeurs[-1]) if valeurs else 0,
        "input": input_tokens,
        "output": output_tokens,
        "cache_creation": cache_creation,
        "cache_1h": cache_1h,
        "cache_read": cache_read,
        "total": total,
        "invalides": lignes_invalides,
        "divergents": len(divergents),
    }, None


def main(argv):
    if not argv:
        print("usage: mesure-tokens.py <fichier.jsonl> [...]", file=sys.stderr)
        return 1

    resultats = []
    au_moins_un_lu = False

    for chemin in argv:
        nom = os.path.basename(chemin)
        r, erreur = mesurer(chemin)
        if erreur:
            print(f"{nom}\t{erreur}", file=sys.stderr)
            continue
        au_moins_un_lu = True
        if r["divergents"] > 0:
            print(f"{nom}\tdivergents = {r['divergents']} (ids dont l'usage change d'une ligne à l'autre)",
                  file=sys.stderr)
        resultats.append((nom, r))

    if not au_moins_un_lu:
        print("aucun fichier n'a pu être lu", file=sys.stderr)
        return 1

    print("\t".join(["fichier"] + COLONNES))
    for nom, r in resultats:
        print("\t".join(str(x) for x in [nom] + [r[k] for k in COLONNES]))

    if len(resultats) > 1:
        cumul = {k: 0 for k in SOMMABLES}
        for _, r in resultats:
            for k in cumul:
                cumul[k] += r[k]
        print("\t".join(str(x) for x in ["TOTAL"] + [cumul.get(k, "-") for k in COLONNES]))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
