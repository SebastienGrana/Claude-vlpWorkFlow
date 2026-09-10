#!/usr/bin/env python3
import json
import os
import sys


def mesurer(chemin):
    input_tokens = 0
    output_tokens = 0
    cache_creation = 0
    cache_read = 0
    lignes_invalides = 0

    try:
        f = open(chemin, encoding="utf-8")
    except OSError as e:
        return None, f"illisible : {e}"

    with f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                d = json.loads(ligne)
            except json.JSONDecodeError:
                lignes_invalides += 1
                continue
            usage = d.get("message", {}).get("usage")
            if not isinstance(usage, dict):
                continue
            input_tokens += usage.get("input_tokens", 0)
            output_tokens += usage.get("output_tokens", 0)
            cache_creation += usage.get("cache_creation_input_tokens", 0)
            cache_read += usage.get("cache_read_input_tokens", 0)

    total = input_tokens + output_tokens + cache_creation + cache_read
    return {
        "input": input_tokens,
        "output": output_tokens,
        "cache_creation": cache_creation,
        "cache_read": cache_read,
        "total": total,
        "invalides": lignes_invalides,
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
        resultats.append((nom, r))

    if not au_moins_un_lu:
        print("aucun fichier n'a pu être lu", file=sys.stderr)
        return 1

    en_tete = ["fichier", "input", "output", "cache_creation", "cache_read", "total", "lignes_invalides"]
    print("\t".join(en_tete))
    for nom, r in resultats:
        print("\t".join(str(x) for x in [
            nom, r["input"], r["output"], r["cache_creation"], r["cache_read"], r["total"], r["invalides"],
        ]))

    if len(resultats) > 1:
        cumul = {k: 0 for k in ["input", "output", "cache_creation", "cache_read", "total", "invalides"]}
        for _, r in resultats:
            for k in cumul:
                cumul[k] += r[k]
        print("\t".join(str(x) for x in [
            "TOTAL", cumul["input"], cumul["output"], cumul["cache_creation"], cumul["cache_read"],
            cumul["total"], cumul["invalides"],
        ]))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
