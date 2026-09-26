#!/bin/bash
set -e

# Pose le bac d'essai de FIL3 (fiches F1/F2, n01..n12.txt, CHANTIER.md) dans
# le workspace vide de l'eval, en appelant le vrai vlp.py du plugin par un
# chemin relatif à ce script — aucun chemin de machine (CLAUDE.md, règle 4).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VLP="$SCRIPT_DIR/../../scripts/vlp.py"

if command -v python >/dev/null 2>&1; then
  python "$VLP" bac .
elif command -v python3 >/dev/null 2>&1; then
  python3 "$VLP" bac .
else
  py "$VLP" bac .
fi
