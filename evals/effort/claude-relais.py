#!/usr/bin/env python3
"""Relais de `claude` pour MET4, repris mot pour mot de VIT25 (série 2) : le vrai CLI (celui de `vlp.py claude`),
mêmes arguments, plus une consigne ajoutée au prompt système (`--append-system-prompt`, `claude --help` du 2026-10-06).

Pourquoi : en série 1 de VIT25, 8 sessions `claude -p` sur 11 ont lancé la suite entière en arrière-plan, rendu la
main pour « attendre sa notification » — et le CLI s'est arrêté là, avant `cocher` et le commit. Avec cette consigne,
série 2 : 12 sur 12 cochées. `boucle.py` lance un `--claude` en `.py` par son Python : c'est le relais de PAR7.
Le kit vient de `MET4_KIT`, posé par `met4-juge.py --kit` : aucun chemin de machine ici (EFF2).
"""
import os
import subprocess
import sys
CONSIGNE = ("Session sans humain (claude -p) : elle s'arrête dès que tu rends la main, et aucune notification ne "
            "viendra te réveiller. Ne lance donc aucune commande en arrière-plan (jamais run_in_background) et "
            "n'attends rien : lance chaque commande au premier plan, avec le timeout le plus long (600000 ms) quand "
            "elle est longue, comme la suite entière.")


def main():
    kit = os.environ.get("MET4_KIT")
    if not kit:
        print("GARDE: MET4_KIT absent — le relais se lance par met4-juge.py --kit", file=sys.stderr)
        return 2
    sortie = subprocess.run(["py", "-3", kit + "/scripts/vlp.py", "claude"], capture_output=True, text=True).stdout
    claude = sortie.strip().split(" ", 1)[1]
    return subprocess.call([claude] + sys.argv[1:] + ["--append-system-prompt", CONSIGNE])


if __name__ == "__main__":
    sys.exit(main())
