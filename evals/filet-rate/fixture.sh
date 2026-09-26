#!/bin/bash
set -e

# Le bac de FIL3 (vlp.py bac), plus une fiche F3 : douze Read sur des fichiers
# absents — m01.txt … m12.txt n'existent pas (chantier RAT, TODO n° 43).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VLP="$SCRIPT_DIR/../../scripts/vlp.py"

if command -v python >/dev/null 2>&1; then
  python "$VLP" bac .
elif command -v python3 >/dev/null 2>&1; then
  python3 "$VLP" bac .
else
  py "$VLP" bac .
fi

cat >> fiches.md <<'FICHE'

---

<!-- FICHE:F3 -->
## F3 [ ] — Lire douze fichiers absents

**Prompt**
Lis `m01.txt`, `m02.txt`, … jusqu'à `m12.txt`, dans l'ordre, par l'outil `Read` :
un appel par message, d'affilée, dans cette même exécution. Un fichier absent ne
t'arrête pas : passe au suivant.

**Critère de fin**
Les douze lectures tentées.
<!-- /FICHE -->
FICHE
